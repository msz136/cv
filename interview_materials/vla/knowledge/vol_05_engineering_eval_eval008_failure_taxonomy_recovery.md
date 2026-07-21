# VOL 05 EVAL-008：Perception / Action / Controller / Recovery Failure Taxonomy

> 状态：`drafted / VLA-EVAL-008 / knowledge_30_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-007 Coverage](vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)、[WM-020 Diagnostics](vol_04_world_model_sim2real_wm020_failure_diagnostics.html)  
> 来源冻结：[EVAL-008 Source Freeze](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)  
> 项目边界：五项目均未闭合layer-aligned trace、matched intervention与fix/rerun，本页不升级root-cause或recovery claim。

## 问题（Question）

VLA rollout失败后，怎样区分perception、policy/action、action interface、controller/execution与recovery failure？核心是先验证protocol，再沿接口找first verified divergence；未知就保留unknown。

## 1. 一条失败链，不是一张失败截图

```text
raw obs -> estimate -> policy -> transform -> controller -> executed state
       -> environment/predicate -> detector -> recovery -> verify/resume/abort
```

success=false是effect；“抓取失败”是symptom；“pose错”“gripper维错”“控制饱和”是不同cause hypothesis。failure explanation、detector alarm和root cause也不是一回事。

## 2. 四个名词必须分开

| 名词 | 定义 | 输出例子 |
| --- | --- | --- |
| effect | episode最终影响 | timeout、碰撞、任务未完成 |
| mode/symptom | 可观测偏差 | box漂移、action跳变、tracking error |
| cause | 导致偏差的机制 | 错帧、OOD、axis/unit错、饱和 |
| recovery outcome | 失败后动作及结果 | regrasp成功、safe abort、二次失败 |

NASA FMECA强调failure mode/effect/criticality是随设计更新的living risk assessment；用于VLA时应加trace、evidence grade与unknown，而不是把taxonomy当静态词表。[1]

## 3. First Verified Divergence

\[
l^*=\min\{l:D_l=1\land evidence_l=\mathrm{verified}\}.
\]

变量解释：`l`按observation、perception、policy、transform、controller、environment、scorer、recovery排序；`D_l`表示该层合同已被证据证明违反。`l*`只是最早验证偏差；更上游缺日志时仍不能声称它们正常。

primary label给`l*`，下游连锁后果标secondary；多个独立偏差可以multi-label。无matched evidence则primary=`unknown`。

## 4. Perception / State Estimation Failure

### 4.1 Failure modes

- raw frame缺失、stale、错view/时间戳、颜色/resize/flip错误；
- object/point/box/pose/state误检、漏检、identity swap；
- calibration、depth、coordinate transform、grounding/subgoal state错误。

### 4.2 证据

保存raw frame/timestamp/view、preprocess后张量、estimate与坐标、ground truth/人工标注或第二传感器。最强matched probe是用verified state替换estimate而保持policy/controller不变；若结果恢复，才支持perception层归因。

AHA与REFLECT说明视觉语言/多传感summary可以检测、解释失败，但generated explanation不是传感器ground truth，也不能单独确认cause。[3][4]

## 5. Policy / Action 与 Action Interface Failure

### 5.1 Policy/action

在verified observation与task下，错误subgoal、错误停止、错误action mode/chunk、temporally erratic action或consistent-but-no-progress属于policy proposal层。

Sentinel把erratic temporal inconsistency与task progression failure交给互补detector：action很平滑仍可能不推进任务；action抖动也不自动说明perception错。[2]

### 5.2 Action interface

token/parser、shape/H/D、valid mask、axis order、unit/frame、normalization/denormalization、clip、H/K slice与queue都可能把正确proposal变成错误command。

最小单测：

```text
sentinel action -> encode -> model-format -> decode -> denorm
 -> valid-dim slice/frame transform -> controller command
```

逐维对比值、axis、unit与timestamp。roundtrip失败时先修interface，不把它包装成policy能力差。

## 6. Controller / Execution Failure

- command tracking error、IK infeasible、joint/velocity/torque saturation；
- latency、queue、missed update、overrun、stale command；
- controller lifecycle/hardware read-write error；
- collision、contact、slip、gripper与安全限制。

保存policy output、transformed command、command timestamp、joint/state反馈、controller state、limit/error/stop。相同command的paired replay若在controller后才分叉，才支持执行层归因。

`ros2_control`会在hardware read/write或controller update返回ERROR时停用相关controller，并可尝试fallback；fallback接口可用性和仿真测试是前置，不能把“配置了fallback”说成“恢复成功”。[6]

## 7. Recovery / Supervision Failure

完整恢复状态机：

```text
detect -> classify/estimate risk -> choose recovery
 -> safe stop/rollback/regrasp/replan/human -> verify state
 -> resume or abort
```

failure modes包括miss、false alarm、late trigger、错误eligibility、recovery action不可执行、oscillation、verification缺失和unsafe resume。

Recovery RL的一类切换合同是：

\[
a_t=\begin{cases}
\pi_{rec}(s_t),&Q_{risk}(s_t,\pi_{task}(s_t))>\tau,\\
\pi_{task}(s_t),&\text{otherwise}.
\end{cases}
\]

变量解释：risk critic只负责trigger evidence，recovery policy负责动作；threshold、false alarm和constraint violation都需验证。它是公开机制，不是本地项目实现事实。[5]

REFLECT还展示了execution/planning explanation进入correction planner的路线；correction plan存在不等于机器人已安全执行。[4]

## 8. Cross-cutting：Protocol / Reset / Scorer

以下问题先归protocol/environment/scorer，不归policy：invalid reset、asset/version漂移、termination/truncation混淆、success predicate变化、episode遗漏、controller版本不一致。先过EVAL-006 identity和EVAL-007 coverage gate。

## 9. 归因矩阵

| 层 | 必需对照 | 决定性trace | 常见误判 |
| --- | --- | --- | --- |
| perception | verified estimate替换 | raw→estimate | VLM说“看错了”就确认 |
| policy | verified input下paired proposal | input→raw action | rollout失败都归模型 |
| interface | sentinel roundtrip | raw→decoded command | loss正常就接口正确 |
| controller | identical command replay | command→executed state | 夹爪没抓住必是gripper head |
| recovery | matched failed-state trigger/action | alarm→recovery→verify | 一次恢复成功就报rate |

确认root cause的最低链：`reproduce → matched intervention → predicted change → fix → same-protocol rerun`。

## 10. Detection / Recovery Metrics

\[
Recall_{fail}=\frac{TP}{TP+FN},\qquad
Precision_{alarm}=\frac{TP}{TP+FP},\qquad
\Delta t=t_{detect}-t_{first\_observable}.
\]

同时报告failure-family confusion、false alarms/hour、eligible/triggered/recovered denominators、post-recovery task success、unsafe violations与human intervention。只有失败样本无法估precision；只在被触发且容易恢复的case上报rate会有selection bias。

## 11. Failure Ledger

```python
def failure_ledger(trace, contracts, detector, recovery):
    # Reject invalid protocol/reset/scorer records before model attribution.
    validate_protocol(trace, contracts)

    # Compare adjacent interfaces and preserve unknown for missing evidence.
    deltas = compare_adjacent_layers(trace)
    primary = earliest_verified(deltas)

    # Detection and recovery are evaluated separately from root-cause labels.
    alarm = detector(trace)
    decision = recovery(trace) if alarm.triggered else "continue"
    result = execute_then_verify_or_abort(decision)
    return record(trace, primary, deltas, alarm, decision, result)
```

最小字段包括episode/protocol、first symptom/detection time、raw obs、estimate、policy I/O、decoded action、controller command/executed state、effect/mode/cause confidence、alarm、recovery与最终outcome。

## 12. 五项目映射

### WAM

一条CoffeePressButton episode0双侧300-step trace均`success=false`；range差异只是interface/controller probe入口。没有checkpoint binary、target、multi-episode和修复rerun，不确认gripper/high-sigma或0-success root cause。

### OpenPiVLA

`D=72`与formal `limit=16`是action-interface冲突；缺formal Qwen checkpoint到controller的rollout。official OpenPI checkpoint diagnostics不能绑定到formal policy。

### OPD

point strict=0先拆parse-valid、protocol-fixed strict与lenient geometry：parser/scorer failure不等于perception/grounding能力不存在。

### Robot Harness

timeout/cancel/best-effort compensation与structured result是orchestration recovery contract；没有低层controller、物理执行与runner outcome，不能报robot recovery success。

### UWM

moka/mug或其他task summary只能形成failure slice；缺raw video/state/action/controller与first-divergence trace，perception/contact/planning均保持hypothesis。

## 13. 高频追问

1. failure effect、mode和cause有什么区别？
2. 为什么first visible symptom不一定是first divergence？
3. 怎样用verified state替换定位perception？
4. policy action错与parser/denorm错怎样分？
5. controller tracking failure要存什么？
6. erratic与no-progress为何需要不同detector？
7. detector explanation能否当root cause？
8. recovery rate的denominator怎么定义？
9. fallback controller为何可能无法激活？
10. 五项目当前能安全讲到哪一层？

## 14. Review Checklist 与下一入口

- [ ] effect/mode/cause/detection/recovery outcome分开；
- [ ] primary是最早verified divergence，缺证据标unknown；
- [ ] observation→estimate→proposal→transform→command→state trace齐全；
- [ ] matched intervention与fix/rerun支持root cause；
- [ ] detector报告precision/recall/delay/false alarms；
- [ ] recovery报告eligible/triggered/recovered与unsafe outcome；
- [ ] protocol/reset/scorer failure不归罪模型；
- [ ] 项目无闭环证据时保持WARN。

本节点保持`WARN/unseen`。下一节点固定为`VLA-EVAL-009`：raw predictions、episode trace、video与可复算summary；真实口述前不创建coaching state。

## References

1. [EVAL-008 Source Freeze](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)。
2. Sentinel、AHA、REFLECT、Recovery RL、NASA FMECA与`ros2_control` frozen revisions见source freeze。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与[paired trace](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html)。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
