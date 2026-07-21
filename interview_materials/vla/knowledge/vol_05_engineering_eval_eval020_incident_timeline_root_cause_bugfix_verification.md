# VOL 05 Engineering / Evaluation：EVAL-020 Incident Timeline、Root Cause 与 Bug-fix Verification

> 状态：`drafted / VLA-EVAL-020 / knowledge_42_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 难度：L2　优先级：P1  
> 来源冻结：[EVAL-020 Source Freeze](../sources/vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)  
> 本页建立incident→impact→timeline→first divergence→hypothesis→cause→fix→verification→prevention链路；不把时间先后、rollback、first bad commit或一次绿色rerun直接升级为confirmed root cause。

## 1. 问题与30秒框架

事故复盘要回答三个不同问题：发生了什么、为什么发生、怎样证明不会以相同机制复发。先冻结现场和impact，建立带时钟/provenance的timeline；再对齐known-good/bad找到first verified divergence，用可证伪hypothesis和最小干预定位原因；最后做same-protocol red→green、unaffected controls、fresh neighbors和多次/多seed复验。

```text
freeze incident bundle + bound impact
 -> clock-aware timeline + first verified divergence
 -> falsifiable hypothesis ledger
 -> targeted intervention / bisect when valid
 -> same-protocol RED -> GREEN
 -> unaffected controls + fresh neighbor regression
 -> prevention gate + follow-up owner
```

## 2. 十一个概念不要混

| 概念 | 核心语义 | 常见误写 |
| --- | --- | --- |
| incident | 触发响应的异常事件 | 所有bad case都叫事故 |
| impact | 受影响support、程度、时长与风险 | “指标掉了”无denominator |
| symptom | 被观察到的表象 | 直接写成根因 |
| first divergence | good/bad最早可验证差异 | 最早告警或最后日志 |
| hypothesis | 可被实验反驳的机制猜想 | 只有支持证据的故事 |
| contributing condition | 放大概率/blast radius的条件 | 唯一原因 |
| proximate cause | 直接触发异常的事件 | 系统性root cause终点 |
| root cause | 目标support上经干预确认的系统因素组合 | last change / human error |
| mitigation/rollback | 暂时控制影响或回旧版本 | 永久修复 |
| recovery | 服务/机器人回安全状态 | 根因消失 |
| fix/prevention | 改机制 / 防复发与早发现 | 一次rerun或一句action item |

最重要的面试边界：`RECOVERED != FIXED != PREVENTED`。

## 3. 先保存现场，再修

incident manifest至少绑定：

- incident ID、trigger、severity、owner；
- task/site/robot/checkpoint/model/processor/normalizer/controller/scorer；
- start/detect/ack/mitigate/recover/end与clock domain；
- expected/observed、support、denominator、unknown impact；
- raw alert/log/trace/video/metric与完整SHA；
- responder操作、restart/rollback/manual override及副作用。

没有不可变bundle，复盘很容易把修复后的配置当作事故配置，把curated video当作全部影响，把summary当作可重算raw evidence。[1][2]

## 4. Timeline 要区分四种时间

一条事件至少区分：发生时间、被观测时间、写日志时间、复盘推断时间。跨robot、policy server、simulator、GPU和scorer时，还要记录clock source、offset/error与happens-before。

日志行号不是全局时间。若时钟不同步，只能说：

```text
observation captured
 -> request admitted
 -> model returned
 -> action queued
 -> controller executed
 -> scorer observed effect
```

并给每段证据来源和允许的时间误差，不能伪造毫秒级全序。[4]

## 5. First Verified Divergence

沿数据到物理效果逐层对齐：

```text
input/data
 -> preprocessing/normalizer
 -> logits/action prediction
 -> decode/chunk
 -> queue/network
 -> controller command
 -> robot/sim state
 -> success/safety scorer
```

first divergence是最早“能由同输入、同bundle和aligned trace复现”的差异。例如parser首次拒绝point输出，只能证明协议层首先出现可见分叉；仍需检查上游prompt是否发出了错误格式、parser合同是否正确、scorer是否漂移。

## 6. Hypothesis Ledger

每个hypothesis写四件事：预测什么、什么能反驳、只改哪个因素、哪些controls应不变。

| 状态 | 含义 |
| --- | --- |
| proposed | 只有合理性，尚无干预 |
| supported | 预测与至少一个targeted experiment一致 |
| weakened | 关键预测不成立，但未完全排除 |
| rejected | 反证与稳定oracle足以排除 |
| partially confirmed | 某support/机制成立，外推仍缺 |
| confirmed | reproducer、干预、red→green、controls、fresh cases闭合 |
| unknown | 无法复现或confounding未解 |

被拒绝的hypothesis也要保留，否则复盘会出现hindsight bias。[1][2]

## 7. Root Cause 的最低证据门槛

以下只是线索：故障跟在某commit后、rollback有效、`git bisect`找到first bad、某个signal异常、patch后一次通过。confirmed root cause至少要求：

1. failure predicate、incident bundle和impact冻结；
2. failure可复现或概率被量化；
3. first divergence有same-input对齐；
4. targeted intervention只改候选机制；
5. affected exact replay由RED变GREEN；
6. unaffected controls保持GREEN；
7. fresh neighboring cases通过；
8. seed/task/site/flakiness不确定性有界；
9. 替代解释被反驳或明确保留。

如果一次同时改checkpoint、prompt、parser、data和scorer，结论最多是bundle-level mitigation/fix，不能归因单一component。[5]

## 8. `git bisect` 能做什么

`git bisect`从known-good/known-bad端点二分，使用稳定的good/bad oracle缩小区间，最终返回first bad commit；`run`可自动判定，`skip`表示revision不可测。[3]

它适合：commit历史上failure近似单调、每版可构建、外部依赖锁定、oracle稳定。它不适合直接处理：flaky、多因素交互、data/checkpoint/scorer漂移、non-monotonic failure或事后改阈值。

所以first bad commit回答“哪次revision首次被该测试判bad”，而root cause还要回答“哪个机制通过何种路径导致failure”。

## 9. Verification 的四格矩阵

| 样本 | before | after | 解释 |
| --- | --- | --- | --- |
| incident exact replay | RED | GREEN | 原failure是否消失 |
| unaffected exact controls | GREEN | GREEN | 正常路径是否被破坏 |
| fresh affected-neighbor | RED/unknown | GREEN | 是否只针对事故样本过拟合 |
| stress/boundary/rollback | 预注册预期 | 预注册预期 | 边界与恢复是否仍有效 |

只允许target patch变化；checkpoint、data、seed/init、processor、normalizer、controller、scorer和hardware差异都要锁定或登记。否则“修复前后”其实是两个protocol。

## 10. Paired Effect

在相同episode/task-init pair上，修复前后成功indicator为`Y_i^-`与`Y_i^+`：

\[
\widehat{\Delta}_{fix}=\frac{1}{n}\sum_{i=1}^{n}(Y_i^+-Y_i^-).
\]

变量解释：`n`是完整matched pairs，invalid/missing也需守恒。直觉：让每个困难case和自己比较。实现映射：保存pair ID、两个bundle SHA、raw output；二元结果用McNemar或cluster bootstrap，连续误差报告paired difference与CI。[5]

若failure是间歇性的，`k`次预注册reproduction中失败`r`次：

\[
\widehat p_{repro}=\frac{r}{k}.
\]

变量解释：`failure predicate`和`k`必须事先冻结。直觉：一次通过不代表复发率为零。实现映射：报告全部attempt、置信区间与停止规则，不重跑到出现想要的绿色结果。

## 11. Mitigation 到 Prevention

| 阶段 | 例子 | 关闭条件 |
| --- | --- | --- |
| mitigation | 禁用task、限流、切fallback | impact下降且副作用受控 |
| rollback | 切known-good bundle | 当前窗口恢复且bundle身份确认 |
| recovery | service/robot回SLO/safe state | recovery predicate满足 |
| corrective fix | parser/schema/guardrail patch | four-cell verification通过 |
| prevention | CI gate、monitor、runbook、permission | owner/deadline/test/closure evidence完整 |

Google SRE的blameless边界是理解当时信息与contributing system conditions，而不是把“操作员犯错”写成终点。仍需明确owner、审批边界和行动项验收。[1][2]

## 12. Flaky / 无法复现时怎么办

- 先验证scorer/oracle，再验证系统；
- 固定seed、data order、driver/dependency、resource和warmup；
- 把timeout/build/load failure和true negative分开；
- 预注册尝试次数与停止规则；
- 多因素漂移时构造minimal reproducer和2×2 cells；
- 仍无法复现就写`unknown/partially_confirmed`，补observability，不编造RCA。

NIST强调Detect、Respond、Recover和持续改进，但它是cybersecurity框架；本页只借用生命周期思维，不把它包装成VLA标准。[6]

## 13. Artifact Bundle

```text
incident manifest + impact scope
 -> raw evidence + clock-aware timeline
 -> first divergence + hypothesis ledger
 -> minimal reproducer + bisect/experiment ledger
 -> fix patch manifest
 -> exact replay before/after
 -> unaffected controls + fresh neighbors
 -> rollback/recovery log
 -> action items + checksums + reproduce command
```

`fix_patch_manifest`声明唯一允许变化；`action_items`包含owner、priority、due date、test和closure SHA。这个bundle才允许把“调好了”升级为可复核的fix claim。

## 14. 五项目真实性映射

### OPD

早期point示例输出裸`[(x,y)]`，strict parser要求`<point>[[...]]</point>`；原strict下base等为0。protocol-fixed后，Qwen-122B format `0.9986`、Hit@100 `0.8200`，Qwen3-35B-VL format `0.9857`、Hit@100 `0.7871`。这是最强的局部协议层red→green，但缺完整same-row before/after、unaffected box/text control、fresh templates和incident timeline；只能说`partially_confirmed / protocol-bounded`，不能说模型point能力整体提升。[7]

### UWM / LIBERO

zarr小chunk随机读的DataLoader-only smoke中，preload+infinite使p95 wait约`13.86s→0.19s`。它支持输入等待的局部定位/mitigation；没有matched end-to-end GPU step trace和长跑复验，不能称完整训练吞吐root cause。`186/250`仍是user-confirmed summary，raw缺。[7]

### WAM

gripper/high-sigma/conditioning/DeepSpeed/OOM/state_dict主要是hypotheses。单episode rollout diagnostic和单sample 5k/10k proxy不具备paired rerun，不能确认root cause或fix。

### OpenPiVLA

formal Qwen路径使用eager attention，源码/report可读；可称兼容/稳定性选择，不能称模型质量root-cause fix。还缺checkpoint binary/load smoke、same-checkpoint A/B与正式benchmark。

### Robot Harness

safety telecom repair gold需5个tool steps而模型只选1个，safety tool accuracy约`38–44%`。这是明确failure case，不是修复闭环；需per-sample trace区分planner/router/runtime/scorer，再做exact replay和fresh multi-step workflows。

## 15. 面试追问防线

- **rollback有效是否证明最后commit是根因？** 不证明；可能同时回退多个因素，只支持旧bundle在当前窗口可恢复。
- **first divergence就是root cause吗？** 不一定；它是最早可见分叉，上游机制仍可能导致它。
- **bisect找到first bad够吗？** 不够；还需稳定oracle、环境锁定和机制干预。
- **一次rerun过了能关事故吗？** 只能是弱证据；还要controls、fresh cases和复发不确定性。
- **human error为什么不够？** 要追到默认值、权限、review、guardrail和observability。
- **不能复现怎么办？** 保持unknown/partial，保存原bundle并补观测，不写确定RCA。
- **项目最可信案例？** OPD是狭窄协议层red→green；UWM是DataLoader子系统A/B；都不能外推端到端。

## 16. 调查伪代码

```python
def close_incident(incident, known_good, fix, spec):
    bundle = freeze_raw_evidence_and_identity(incident)
    impact = compute_bounded_impact(bundle, spec.impact)
    timeline = normalize_clocks_without_faking_total_order(bundle)
    reproducer = build_minimal_reproducer(bundle, spec.failure_predicate)
    divergence = align_good_bad_and_find_first_verified(reproducer, known_good)
    causes = test_competing_hypotheses(divergence, spec.interventions)

    exact = same_protocol_before_after(reproducer, fix)
    controls = run_unaffected_controls(fix, spec.controls)
    fresh = run_fresh_neighbor_regression(fix, spec.fresh_cases)
    return require_closure_evidence(impact, causes, exact, controls, fresh)
```

这是未来incident-response验收合同，不代表五项目已部署该系统。[7]

## 17. 本节点状态

EVAL-020知识节点与一张题卡已起草并保持`WARN/unseen`。本页没有把last change、rollback、bisect、单episode或一次绿色rerun升级为confirmed root cause；没有真实口述前不创建`coaching_state.md`。下一节点是`VLA-EVAL-021`：deployment drift、data shift与持续监控。

## 参考文献（References）

1. Google SRE, [*Postmortem Culture: Learning from Failure*](https://sre.google/sre-book/postmortem-culture/)。
2. Google SRE Workbook, [*Postmortem Culture: Learning from Failure*](https://sre.google/workbook/postmortem-culture/)。
3. `git/git`, [`git-bisect`@`41365c2`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-bisect.adoc)。
4. [EVAL-013 Clock / Latency](vol_05_engineering_eval_eval013_end_to_end_latency_deadline_jitter.html)。
5. [EVAL-018 Factorial / Causal Boundary](vol_05_engineering_eval_eval018_factorial_ablation_matched_baseline_causal_boundary.html)。
6. Nelson et al., [NIST SP 800-61r3](https://doi.org/10.6028/NIST.SP.800-61r3), April 2025。
7. [EVAL-020 Source Freeze](../sources/vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)及[五项目inventories](../evidence/evidence_manifest.html)。
