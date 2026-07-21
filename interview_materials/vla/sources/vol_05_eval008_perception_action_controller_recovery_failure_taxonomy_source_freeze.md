# VOL 05 EVAL-008 Source Freeze：Perception / Action / Controller / Recovery Failure Taxonomy

> 状态：`source_frozen / VLA-EVAL-008 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 failure effect / mode / cause、first verified divergence、perception/action-interface/controller/recovery 分层、runtime detection 与 recovery outcome；下游只生成一张 `VLA-EVAL-008` 原子题卡，VOL 05 同步为 knowledge/cards 30/44。

## 问题（Question）

一个episode失败后，怎样判断是感知、policy/action、action interface、controller/execution还是recovery失败？强回答不是看视频后贴单标签，而是沿可观测链找到**最早被证据验证的偏差**，把failure effect、observable mode、root-cause hypothesis和recovery result分开。

```text
raw observation -> perception/state estimate -> policy proposal
 -> decode/denorm/frame transform -> controller command/executed state
 -> environment transition/success scorer -> detector/recovery -> resume/abort
```

## 1. 冻结来源、revision、许可与边界

| ID | 来源 | 类型 / revision | SHA-256 | 支持范围 |
| --- | --- | --- | --- | --- |
| S1 | NASA GSFC-HDBK-8004, *Guideline for FMEA and Risk Assessment* | official handbook / Baseline, change 0, 2024-08-20 | page `c661245f1ade662bb71c0d786bfd85a1eb41ebadf0d5b916d1fc71223167315c`; PDF `88e2f1a7a5ff96e264ff91bbac985a7711422c6608ceab58b36dfb24ac7dc8fb` | failure mode/effect/criticality作为随设计更新的living risk ledger；不提供VLA专用标签 |
| S2 | Agia et al., *Sentinel* | primary / CoRL 2024, arXiv `2410.04640`; official-code commit `6dc89ca4cb30f75ce834811c2d1b31f7ffadf7b5`, MIT | paper response `d226a4323f2990f2ef8cf3c4c478c92bb8d5f1bf9281f7d70d98e325e1836516`; README `85d63068108ce3d26ecf58ad65620dd8574a1a3d041934c0d18bae629213c6de`; LICENSE `92d4dfb71ad0b8827bcf0552b8064da4e7a8caacbc926c4d2a2f41a71dd58d16` | erratic/temporal-action-consistency与task-progression detector互补、failure detection需要成功/失败样本；detector类别不等于root cause |
| S3 | Duan et al., *AHA* | primary / ICLR 2025, arXiv `2410.00371`; official-code commit `0d39c0591566ddaf997be5822f3dead8e08501aa`, NVIDIA License | paper response `b8f9dde4991904f1bd147b7a6bfcacd6a4b2fb286cd7079629e24333d872b54d`; README `81a8fc37adb71d2293d996ccfd46cff5405d45ad2618696a94817998fea779c0`; LICENSE `f79d806b9a5512efced76b1df421a369ddf04ef48fbd7d98e61d4c6a4109b06f` | 从机器人失败轨迹做视觉语言检测/解释；natural-language explanation仍需trace/intervention核验 |
| S4 | Liu et al., *REFLECT* | primary / CoRL 2023, arXiv `2306.15724`; official-code commit `0ac7458735fba606151df851491124486dc8b489`, MIT | paper response `2403884d0142ce09ec68d569a95bc4be302d3663169cd3cde70bc7ababa897bc`; README `9849012a3165390d516586ae8b83e338afa101842cb889f32395766178572817`; LICENSE `076eb1a8b4e161bf953019c9f54c1e052d2f65f05c53a4fa0c5ef1489d1ffe11` | multisensory hierarchical summary、execution/planning failure explanation与correction plan；不保证perception或correction正确 |
| S5 | Thananjeyan et al., *Recovery RL* | primary / RA-L + ICRA 2021, arXiv `2010.15920v2`; official-code commit `084c968538850e82776564e07b9dcdffca369936`, MIT | paper response `68d42ec218715e5b08663d064e853d96b4428c83f9c650655969db506bf3eb8b`; README `47c35b98d3b4c12fb000c6fba9e79edecef32f1aa866f110ef93d6c62e9c3211`; `qrisk.py` `d85f65466609a0a76bee6c57ef462fe46b099f10c8c127a47a650747c67470e3`; LICENSE `cdbab599401d78c531d8662377974326f2ba9e347559eda288652f4761145e83` | task policy与recovery policy分离、risk trigger与recovery zone；不是任意VLA的默认recovery实现 |
| S6 | `ros-controls/ros2_control` Controller Manager / Hardware docs | official-code / commit `e4ebcc352d9aeb69969308428b051bdd3105b88f`, Apache-2.0 | userdoc `cf3af601c715499e37408420a355f092176707912e542feb549ccac0a1f038a1`; hardware doc `0349b40119198da85257daca285bf5baccd2fd81f2d5f60fc7cb0eead4014f0a`; LICENSE `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | hardware read/write与controller update error、deactivation/fallback、overrun/diagnostics；不证明本地项目使用ROS2或fallback成功 |
| S7 | 本地机制来源 | canonical source freezes | hashes见下 | action interface、WM failure probe、first-failure ladder与grounding边界 |
| S8 | 五项目inventories与WAM paired trace | local evidence | hashes见下 | 当前可见failure symptom、trace与缺口；不自动支持root cause |

本地来源SHA：architecture/execution `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809`；WM-020 `4053bb051296bcc785a3e1b7f7ddf0a0c75339dcb4f8c84aed755b49888c06dd`；VOL 05基础页 `19965c8d0620255e794b6ffa2b6fb791a80bf36f61e9c7cb699972b8a9ebc547`；PER-001 `345b7601602d0800e669f85ce1d8b8d77760c3022beab48e44e7ce7b11cc803b`；WAM paired trace `913d68cb1e7be44fd108d2a06509d33ea04462b255a153af030b2f3c0a603fb5`；五inventory分别为 `66acc52c...aa291e`、`078c86b1...772d`、`728b8326...3674d`、`a3c644f9...ce293`、`0a68251d...12bb`（完整值见各review）。

## 2. Effect、Mode、Cause、Detection 与 Recovery 分开

| 层 | 回答什么 | 例子 |
| --- | --- | --- |
| failure effect | 最终发生了什么 | timeout、success=false、碰撞、未抓起 |
| failure symptom/mode | trace中哪里偏离 | mask缺失、action跳变、tracking error、detector未触发 |
| root cause | 为什么偏离 | 相机错帧、训练分布缺口、轴序错误、控制饱和 |
| detection | 何时、依据什么报警 | action inconsistency、VLM progress monitor、joint limit |
| recovery outcome | 报警后是否安全恢复 | stop、regrasp、replan、human takeover、abort |

视频里“夹爪没抓住”是effect；它可能来自目标pose错、gripper action错、axis/unit转换错、controller未跟踪或接触物理变化。没有matched probe时root cause保持`unknown`。

## 3. First Verified Divergence

为每层定义偏差证据 `D_l`，最早已验证层为：

\[
l^*=\min\{l:D_l=1\ \land\ evidence_l=\text{verified}\}.
\]

变量解释：`l`按observe→perceive→policy→transform→control→transition→score→recovery排序；`D_l=1`表示该层违反冻结合同。`l*`是**最早验证偏差**，不是必然root cause；上游缺日志时不得把下游首个可见症状冒充上游正常。

事件记录：

```text
episode_id, protocol_sha, t_first_symptom, t_detected,
raw_obs_ref, estimate_ref, policy_input/output_ref,
decoded_action, controller_command, executed_state,
effect, mode_labels, primary_layer, cause_hypotheses,
evidence_grade, detector, recovery_action, recovery_outcome
```

## 4. 四层主taxonomy与交叉层

### 4.1 Perception / State Estimation

- raw sensor missing/stale/corrupt、camera/time/view错配；
- object/point/box/pose/state误检、漏检、identity swap、coordinate transform错误；
- language grounding或subgoal state estimate错误。

需要raw frame/timestamp/calibration、ground-truth或第二传感器/人工标注对照。VLM解释文本不是ground truth。

### 4.2 Policy / Action 与 Action Interface

- 在正确输入下，subgoal、motion mode、action chunk或停止决策不合任务；
- action token/parser失败，shape/H/D、valid mask、axis/unit/frame、normalization/denormalization、clipping、H/K切片错误；
- temporally erratic actions或consistent-but-no-progress。

policy failure与interface failure必须分开：先做sentinel action、encode/decode/denorm roundtrip，再讨论模型策略。

### 4.3 Controller / Execution

- command未被执行、tracking error、IK infeasible、joint/velocity/torque saturation；
- latency/queue/overrun、controller state错误、hardware read/write error；
- collision/contact/gripper/slip与安全限制触发。

保存policy action、transformed command、joint/state反馈和controller lifecycle。`ros2_control`的fallback只有在接口可用、配置正确时才可能激活，必须在仿真测试。

### 4.4 Recovery / Supervision

- detector miss、false alarm、检测太晚；
- recovery eligibility或trigger错误；
- safe stop/rollback/regrasp/replan/human intervention失败；
- recovery oscillation、恢复后未验证、resume造成二次失败。

Recovery RL支持一种risk-based task/recovery切换：

\[
a_t=\begin{cases}
\pi_{rec}(s_t), & Q_{risk}(s_t,\pi_{task}(s_t))>\tau,\\
\pi_{task}(s_t), & \text{otherwise}.
\end{cases}
\]

变量解释：`Q_risk`是constraint-risk critic、`tau`是冻结threshold。该式说明detector/trigger与recovery action分开；本仓库五项目均没有证据表明实现了此机制。

### 4.5 Cross-cutting Protocol / Environment / Scorer

invalid reset、asset/version漂移、timeout/termination语义、success predicate/scorer bug会制造“模型失败”。先通过EVAL-006 protocol identity和EVAL-007 coverage gate，才进入模型归因。

## 5. 最小归因实验

| 假设 | matched intervention | 支持该层的证据 | 仍不能推出 |
| --- | --- | --- | --- |
| perception | 用verified state/人工pose替换estimate，其他不变 | policy/rollout恢复且raw→estimate已有偏差 | detector为何错的最终原因 |
| policy | verified observation下与expert/paired policy比较proposal | 错误在transform前已出现 | training data是唯一原因 |
| interface | sentinel逐维roundtrip、identity normalizer、固定H/K | parser/axis/unit/frame前后不一致 | learned policy本身差 |
| controller | 同command replay，比较commanded/executed state | tracking/limit/error在controller层出现 | 上游完全正确 |
| recovery | matched failed states上比较trigger/action | detection delay、false alarm、conditional recovery outcome | recovery提升总体成功的因果结论 |

单episode可以生成hypothesis，不能confirm root cause。确认至少需要matched replay/intervention、复现、修复与同协议rerun。

## 6. Detector 与 Recovery 指标

\[
\mathrm{Recall}_{fail}=\frac{TP}{TP+FN},\quad
\mathrm{Precision}_{alarm}=\frac{TP}{TP+FP},\quad
\Delta t=t_{detect}-t_{first\_observable}.
\]

还要报告false alarms/episode或hour、failure-family confusion、eligible recovery count、triggered count、conditional recovery success、post-recovery task success、unsafe violations与human interventions。只收失败episode无法估precision/false-positive；只报“恢复成功率”而不报eligible/triggered denominator会选择性偏高。

Sentinel把temporally inconsistent erratic failure与temporally consistent no-progress分给互补detector，说明单一monitor会漏掉另一类；其detector输出仍不是perception/controller root-cause label。

## 7. 五项目边界

- **WAM**：CoffeePressButton episode0有base/trained 300-step action trace与`success=false`，range差异只能启动interface/controller排查；缺checkpoint binary、target、multi-episode与修复rerun，不能确认gripper/high-sigma/root cause或“0-success benchmark”。
- **OpenPiVLA**：recipe/smoke的`D=72`与formal formatter `limit=16`是action-interface risk；缺formal Qwen checkpoint→controller rollout，official checkpoint diagnostics不能归为formal policy failure。
- **OPD**：point strict=0可能是parser/format/scorer failure，也可能是geometry/grounding failure；先拆parse-valid、protocol-fixed strict与lenient geometry，不能直接说“不会point”。
- **Robot Harness**：源码支持timeout/cancel/best-effort compensation和structured error，是orchestration recovery contract；没有视觉、低层controller、物理执行与runner trace，不能报robot recovery success。
- **UWM**：task-level summary与moka/mug低分只能定位effect slice；没有raw video/state/action/controller/first-divergence trace，perception/contact/planning原因均为hypothesis。

## 8. Failure Ledger 伪代码

```python
def attribute_and_recover(trace, frozen_contracts, detectors, recovery):
    # Validate protocol and raw trace before blaming the learned policy.
    validate_protocol_and_reset(trace, frozen_contracts)

    # Compare each adjacent interface and keep unknown when evidence is absent.
    divergences = compare_layers(
        trace, layers=["observation", "perception", "policy", "transform",
                       "controller", "environment", "scorer"])
    primary = earliest_verified(divergences)

    # Detection is a separate prediction task with latency and false alarms.
    alarm = detectors.evaluate(trace)
    action = recovery.choose(trace) if alarm.triggered else "continue"

    # Verify safe state and task outcome before resuming execution.
    outcome = execute_verify_or_abort(action, trace)
    return write_failure_ledger(trace, primary, alarm, action, outcome)
```

这是artifact contract，不是五项目已实现系统。

## 9. Source Gate 结论与下一入口

EVAL-008保持`WARN`：failure mode/effect/cause、first verified divergence、四层taxonomy、detector与recovery指标已冻结；五项目均没有完整layer-aligned trace + matched intervention + fix/rerun闭环，因此不产生root-cause或recovery强claim。

下一内容节点固定为`VLA-EVAL-009`：raw predictions、episode trace、video与可复算summary。真实口述前不创建`coaching_state.md`。

## References

1. NASA [GSFC-HDBK-8004](https://standards.nasa.gov/standard/GSFC/GSFC-HDBK-8004)。
2. Agia et al., [Sentinel](https://arxiv.org/abs/2410.04640) / [official repo](https://github.com/agiachris/sentinel/tree/6dc89ca4cb30f75ce834811c2d1b31f7ffadf7b5)。
3. Duan et al., [AHA](https://arxiv.org/abs/2410.00371) / [official repo](https://github.com/NVlabs/AHA/tree/0d39c0591566ddaf997be5822f3dead8e08501aa)。
4. Liu et al., [REFLECT](https://arxiv.org/abs/2306.15724) / [official repo](https://github.com/real-stanford/reflect/tree/0ac7458735fba606151df851491124486dc8b489)。
5. Thananjeyan et al., [Recovery RL](https://arxiv.org/abs/2010.15920) / [official repo](https://github.com/abalakrishna123/recovery-rl/tree/084c968538850e82776564e07b9dcdffca369936)。
6. `ros2_control` [Controller Manager](https://github.com/ros-controls/ros2_control/blob/e4ebcc352d9aeb69969308428b051bdd3105b88f/controller_manager/doc/userdoc.rst)与[Hardware Components](https://github.com/ros-controls/ros2_control/blob/e4ebcc352d9aeb69969308428b051bdd3105b88f/hardware_interface/doc/hardware_components_userdoc.rst)。
7. [Architecture / Execution Audit](vol_03_architecture_execution_claim_to_code.html)、[WM-020](vol_04_wm020_failure_diagnostics_source_freeze.html)、[PER-001](vol_06_per001_grounding_coordinate_source_freeze.html)。
8. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
