# VOL 05 Engineering / Evaluation：EVAL-021 Deployment Drift、Data Shift 与持续监控

> 状态：`drafted / VLA-EVAL-021 / knowledge_43_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 难度：L3　优先级：P1  
> 来源冻结：[EVAL-021 Source Freeze](../sources/vol_05_eval021_deployment_drift_data_shift_continuous_monitoring_source_freeze.html)  
> 本页建立reference/current→quality/coverage/system/behavior/outcome→drift signal→impact validation→gated response链路；不把分布检验、协议差异或单次离线结果直接称为线上退化、concept drift或自动重训依据。

## 1. 问题与30秒框架

持续监控要同时回答：输入/环境是否变了，系统执行是否变了，policy行为是否变了，最终成功/安全是否变差。先锁reference/current窗口、sampling unit、lineage和slice；再监控schema/coverage、latency/resource、action/tool behavior与delayed outcome。MMD、JS或ADWIN只产生drift signal，必须定位affected slice并验证same-protocol outcome impact，之后才进入rollback、recalibrate或retrain gate。

```text
freeze reference/current + lineage/context
 -> data quality + coverage
 -> system + behavior signals
 -> registered drift detectors
 -> delayed outcome impact
 -> alert budget + triage
 -> rollback/recalibrate/retrain candidate
 -> regression + shadow/canary + approved reference
```

## 2. 八类 Drift

联合分布分解为：

\[
P_t(X,Y)=P_t(Y\mid X)P_t(X).
\]

变量解释：`X`是image/text/state/robot/site/controller等context，`Y`是success/safety/label。直觉：输入变了和正确映射变了不是一回事。实现映射：无`Y`时只能确认data/behavior signal，不能确认concept或performance drift。[1]

| 类型 | 变化 | 例子 |
| --- | --- | --- |
| schema/quality | shape/type/missing/range/time | camera缺失、action维错、stale frame |
| data/covariate | `P(X)` | 光照、视角、物体、task/language mix |
| label/prior | `P(Y)` | failure类别或success比例变化 |
| concept | `P(Y|X)` | 同context的正确动作/成功规则改变 |
| protocol | init/warmup/prompt/parser/scorer | fixed vs reset、strict vs lenient |
| bundle | model/processor/normalizer/controller | silent version切换 |
| system | latency/resource/runtime | queue age、timeout、driver/tool失败 |
| behavior/scorer | action/tool/fallback或measurement | saturation、tool depth、judge threshold |

deployment drift是多类变化的总称；必须给namespace，不能只写“模型漂移”。

## 3. Reference / Current Window

每个monitor登记：reference来源、current window长度/stride、episode或robot-hour单位、minimum support、slice、lineage、late data、dedupe、invalid/missing、seasonality和planned campaign。

建议同时保留：

- frozen training/validation anchor；
- last-known-good production；
- season-matched历史；
- concurrent canary/control。

rolling recent window适合适应正常变化，但若单独使用，会把慢性退化不断吸收进baseline。

## 4. 五层 Monitoring Plane

| Plane | 监控内容 | 典型问题 |
| --- | --- | --- |
| identity | code/model/data/processor/normalizer/controller/scorer SHA | 是drift还是换版？ |
| quality/coverage | schema、missing、range、timestamp、task/site support | 数据坏了还是分布变了？ |
| system | capture→apply、queue、timeout、OOM、fallback | 执行条件是否退化？ |
| behavior | action norm/saturation、chunk、tool route、abstain | policy是否表现不同？ |
| outcome | success、forbidden effect、recovery、override、incident | 是否真的有业务/安全影响？ |

只有outcome往往太迟，只有proxy又不够；五层要通过episode/request ID join。

## 5. TFDV 式 Schema / Skew / Drift

TFDV把training-serving差异称skew，把相邻data spans差异称drift，并在schema中提供L-infinity和Jensen–Shannon comparator。[2]

对类别比例：

\[
D_{\infty}(p,q)=\max_j|p_j-q_j|.
\]

变量解释：`j`可为task、format、camera-present或tool类别。直觉：找占比变化最大的类别。实现映射：必须同时输出reference/current count、unknown类别、max category和slice；官方guide中的`0.01`只是示例，不能照搬。[2]

对同support分布：

\[
JS(p,q)=\frac12 KL(p\|m)+\frac12 KL(q\|m),\quad m=\frac{p+q}{2}.
\]

变量解释：`m`是两侧混合分布。直觉：对称比较reference/current离共同中间分布的距离。实现映射：bin、smoothing、unknown和threshold必须冻结；JS高不等于success下降。

## 6. MMD 监控高维分布

MMD可比较image/text/state embedding：

\[
\operatorname{MMD}[\mathcal F,p,q]
=\sup_{f\in\mathcal F}\left(E_p[f(X)]-E_q[f(Y)]\right).
\]

变量解释：`F`是RKHS unit ball，kernel与embedding决定检测方向。直觉：寻找最能区分两个窗口的函数。实现映射：冻结encoder SHA/layer/pooling、normalization、kernel/bandwidth、sample unit和permutation/bootstrap方法。[3]

embedding drift有三类混杂：encoder换版、task/site mix变化、统计显著但实际风险不变。因此要同时看raw signals、coverage与outcomes。

## 7. ADWIN 与 Streaming Signal

ADWIN维护可变窗口，将其切成两个子窗口比较均值；`delta`、`clock`、`min_window_length`和`grace_period`影响误报、检测延迟和冷启动。[4]

适合输入：failure/override indicator、timeout、fallback、latency、action saturation或calibration residual。它检测的是该标量流的变化，不自动识别cause，也不保证那是concept drift。

机器人episode/task/site有自相关；不能把每个control step当独立sample。按episode/robot/site block解释并保留发布、维护和campaign事件。

## 8. Drift Signal 到 Impact

同一预注册slice`s`的风险差：

\[
\widehat{\Delta R}_s
=\widehat R_{current,s}-\widehat R_{reference,s}.
\]

变量解释：`R`可为failure、forbidden effect、deadline miss或human override。直觉：先问变化是否落到真实风险上。实现映射：same scorer/lineage、support、cluster-aware interval和delayed-label coverage必须一起报告；无label时状态是`impact_pending`。[5]

正确链路：

```text
drift alert
 -> validate identity/support/statistic
 -> localize feature/slice/time
 -> join delayed outcome
 -> compare same-protocol control
 -> investigate cause
 -> choose response
```

## 9. Coverage 与 Selective Labels

需要守恒：

```text
planned = valid + invalid + timeout + cancelled + missing
labeled <= valid, with label-delay distribution
```

监控per-task/site/robot/camera/language/format support、label arrival、human override、fallback后outcome、unknown category和retention drop。只看有label或成功完成的case会产生selection bias；monitor pipeline自身也要有coverage SLO。[6]

## 10. Alert 治理

| 机制 | 解决什么 |
| --- | --- |
| effect threshold | 防止微小但显著变化page |
| minimum support | 防止小样本抖动 |
| consecutive windows | 防止单窗口噪声 |
| hysteresis/cooldown | 防止告警反复开关 |
| FDR/confirmatory check | 控制feature×slice×window多重检验 |
| page budget/owner | 控制alert fatigue |
| incident/synthetic backtest | 衡量false alert与detection delay |

primary安全/实时信号与diagnostic embedding信号要分级。critical forbidden effect可立即限权；单个MMD p-value不能自动rollback。

## 11. Severity 与响应

| 状态 | 证据 | 默认响应 |
| --- | --- | --- |
| INFO | 轻微变化、impact稳定 | 记录 |
| WARN | effect/support/persistence成立 | 增加slice采样/label，调查 |
| CRITICAL | safety/deadline或大范围unknown | fallback、限权、rollback/canary stop |
| INCONCLUSIVE | label/scorer/support不足 | 不自动放行或重训 |

NIST AI RMF强调ongoing monitoring、risk tracking、response/recovery以及必要时supersede/disengage/deactivate；它不给本项目具体阈值。[1]

## 12. Retrain 不是默认答案

| 现象 | 优先处理 |
| --- | --- |
| schema/processor错误 | block/load gate、修接口 |
| normalizer/action scale | 校验stats、recalibration candidate |
| input shift且outcome稳定 | 扩充audit/stress，继续观察 |
| outcome degradation | 定位slice/cause，再决定data/model/controller |
| latency/resource drift | queue/capacity/runtime修复 |
| scorer drift | 旧/新scorer双跑与历史重算 |
| safety critical | 限权、fallback、rollback |

retrain candidate仍需fresh development/audit、regression、shadow/canary和selection控制，不能用同一报警窗口既训练又证明修复。[7]

## 13. Response State Machine

```text
OBSERVING
 -> ALERT_CANDIDATE
 -> VALIDATED_SIGNAL
 -> IMPACT_PENDING / IMPACT_CONFIRMED
 -> TRIAGED_CAUSE
 -> RESPONSE_CANDIDATE
 -> OFFLINE_REGRESSION
 -> SHADOW / CANARY
 -> RELEASED / REJECTED
 -> REFERENCE_PROMOTION_APPROVAL
```

reference promotion必须保留审批与rollback anchor；current不能自动成为new normal。

## 14. Artifact Bundle

```text
monitor registry + immutable reference/current manifests
 -> lineage/context + schema/coverage/system/behavior tables
 -> delayed outcome join
 -> registered drift statistics
 -> alert threshold/budget + backtest
 -> alert/incident join + response decisions
 -> update release ledger
 -> approved reference promotion + checksums
```

registry逐monitor保存signal、unit、window、reference、slice、statistic、effect、support、persistence、owner与action。没有这些字段，dashboard无法复算或审计。

## 15. 五项目真实性映射

### OPD

static manifests、raw-holdout pool/format quotas和strict/protocol-fixed/lenient口径可作为离线reference候选。future monitor应看pool/format/language/image mix、strict reject、parse/OOB、box/point/text outcome并锁prompt/parser/scorer SHA。当前无timestamped serving stream、online label或alert backtest，不能称deployment monitoring。[8]

### Robot Harness

应监控task/tool/version mix、tool depth、argument/schema reject、auth/timeout/cancel/side effects、fallback与human override。现有约`38–44%` safety tool accuracy是静态failure summary，不是live SLO；共同n/scorer和request trace仍缺。

### OpenPiVLA

应先做checkpoint/processor/normalizer/controller identity，再看camera/state/action schema、action saturation、chunk/replan、load reject、capture→apply latency与task success。multiple lineage和eager路径是version/compatibility线索，不是已监控的drift。

### WAM

单episode、三camera字段和单sample future proxy只能指导camera age、conditioning/sigma、action/gripper、world/value proxy与closed-loop outcome的monitor设计，不能建立distribution threshold或concept drift。

### UWM / LIBERO

fixed-pruned-init `186/250`与reset-style `232/250`改变protocol和distribution，不能写成时间drift或模型退化。future monitor可登记task/init/scene/camera、normalizer/action saturation、chunk、per-task outcome、data wait与step time；当前缺raw 250 episodes、timestamps和alerts。

五项目最多提供C0/C1输入，没有线上持续监控、自动漂移检测、SLO或自动重训证据。

## 16. 面试追问防线

- **MMD显著是否模型退化？** 不一定；只证明已定义representation上的分布差异，还要outcome impact。
- **data drift与concept drift区别？** `P(X)`变与`P(Y|X)`变；后者通常需要标签/可信结果。
- **reference用最近一周行吗？** 可以辅助，但不能唯一使用，否则慢性退化被吞掉。
- **为什么不自动重训？** 可能是schema、latency、scorer或合法seasonality；还会污染评估窗口。
- **标签晚到怎么办？** ID join、coverage/delay监控和`impact_pending`状态。
- **多feature为何会误报？** feature×slice×window重复检验，需要effect/support/persistence与alert budget。
- **项目做到哪？** 只有离线reference/schema输入，没有timestamped deployment monitor闭环。

## 17. 监控伪代码

```python
def monitor_window(reference, current, registry):
    # Bind the current rows to one deployment/scorer lineage.
    assert_lineage_and_context(current, registry.bundle)

    # Validate schema and observation/label coverage before drift statistics.
    quality = validate_quality(current, registry.schema)
    coverage = compute_coverage_and_label_delay(current)

    # Run only registered feature, embedding and stream detectors.
    drift = detect_registered_changes(reference, current, registry.detectors)

    # Drift is not impact: join delayed outcomes on identical semantic units.
    impact = estimate_slice_risk_delta(reference, current, registry.outcomes)

    # Apply effect, support, persistence and page-budget gates.
    return persist_alerts_and_decisions(quality, coverage, drift, impact, registry)
```

这是未来monitoring system验收合同，不代表五项目已有实现。[8]

## 18. 本节点状态

EVAL-021知识节点与一张题卡已起草并保持`WARN/unseen`。本页没有把distribution test、fixed/reset差异、offline curve或单次diagnostic升级为deployment degradation/concept drift；没有真实口述前不创建`coaching_state.md`。下一节点是`VLA-EVAL-022`：paper→repo→checkpoint→runtime→ownership evidence audit。

## 参考文献（References）

1. NIST, [*AI RMF 1.0*](https://doi.org/10.6028/NIST.AI.100-1), January 2023。
2. TensorFlow, [TFDV guide](https://www.tensorflow.org/tfx/data_validation/get_started)与[`schema.proto`@`f4f0753`](https://github.com/tensorflow/metadata/blob/f4f0753311ec2cfdedc84f09889f713b43f74d7a/tensorflow_metadata/proto/v0/schema.proto)。
3. Gretton et al., [*A Kernel Two-Sample Test*](https://www.jmlr.org/papers/v13/gretton12a.html), 2012。
4. River, [`ADWIN`@`5eed38d`](https://github.com/online-ml/river/blob/5eed38dfd25183049de733b3016ff1edb84266e5/river/drift/adwin.py)。
5. [EVAL-011 Offline–Online](vol_05_engineering_eval_eval011_offline_online_correlation.html)与[EVAL-020 Incident / Fix](vol_05_engineering_eval_eval020_incident_timeline_root_cause_bugfix_verification.html)。
6. [EVAL-007 Coverage](vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)与[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)。
7. [EVAL-010 Regression](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)、[EVAL-017 Release Gate](vol_05_engineering_eval_eval017_simulator_shadow_real_robot_gate.html)与[EVAL-019 Selection](vol_05_engineering_eval_eval019_checkpoint_selection_pareto_holdout_overfit.html)。
8. [EVAL-021 Source Freeze](../sources/vol_05_eval021_deployment_drift_data_shift_continuous_monitoring_source_freeze.html)及[五项目inventories](../evidence/evidence_manifest.html)。
