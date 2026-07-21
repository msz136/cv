# VOL 05 EVAL-021 Source Freeze：Deployment Drift、Data Shift 与持续监控

> 状态：`source_frozen / VLA-EVAL-021 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结deployment reference/current windows、data/label/concept/protocol/system/scorer drift、schema/skew/drift comparator、two-sample与streaming detector、coverage/performance/safety/latency联合监控、告警治理、drift→impact→response边界及五项目真实性；只服务`VLA-EVAL-021`，EVAL-022后置。

## 问题（Question）

VLA部署后，摄像头、场景、任务、机器人、用户指令、controller、模型bundle或scorer都会变化。怎样及时发现分布变化，并判断它是否真的影响成功率、安全和实时性？可信持续监控不是“embedding距离超过阈值就自动重训”，而是冻结reference/current窗口和sampling unit，分层监控data quality、coverage、system、policy behavior与delayed outcome；drift alert只触发调查，只有same-protocol影响验证、root-cause定位和gated update完成后才允许rollback、recalibrate或retrain。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | NIST AI 100-1, *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* + AI RMF Playbook | official final framework；January 2023；Playbook页面2026-07-19抓取；页面/出版物许可未在本冻结中断言 | PDF `7576edb531d9848825814ee88e28b1795d3a84b435b4b797d3670eafdc4a89f1`；Playbook page `392d55aa40658cbd0eebedd3c928dc4f400066b1696f50ca6e59b2ae723be48a` | deployed AI ongoing testing/monitoring、risk tracking、反馈、recalibration/removal、disengage/deactivate、post-deployment monitoring/change management；data/model/concept drift可能触发更频繁维护 | 给出VLA drift统计量、窗口、阈值或自动重训标准；五项目已部署或符合NIST治理 |
| S2 | TensorFlow Data Validation guide + `tensorflow/metadata` schema | official docs；guide 2026-07-19抓取；official-code commit `f4f0753311ec2cfdedc84f09889f713b43f74d7a`（2026-06-09）；Apache-2.0 | guide `82ad2183c5cffad0e6cb57eec82fbf3be4ae90a7b4afcab08ba667d985006f4e`；API snapshot `8c70d02357b63ad507ef0909f683e877b521843f636de943b03cf2ecd774ef25`；`schema.proto` `c29fb7b8381489fd65373b6b11ae58e77796e42faa0e42d6c10eb039a85c8695`；LICENSE `9df6cd8aaf0768103846a8502186ed55a54a45c3f7cd9fce531b573cd400d8d9` | training-serving skew、consecutive-span drift、schema environments、L-infinity/Jensen–Shannon comparator与threshold字段 | 检测到feature drift等于模型质量下降；guide示例`0.01`是VLA通用阈值；TFDV直接覆盖图像、轨迹或闭环因果 |
| S3 | Gretton et al., *A Kernel Two-Sample Test* | primary paper；JMLR 13, 2012；论文许可未在本冻结中断言 | PDF `236e1e59ca080d36c59958777c523afdeb8b496871ed50bd21665312c8013f28` | two-sample hypothesis、Maximum Mean Discrepancy（MMD）、characteristic RKHS与quadratic/linear-time估计边界 | 任意embedding上的MMD告警自动代表semantic或performance drift；本页阈值、kernel或窗口已预注册 |
| S4 | `online-ml/river` ADWIN implementation | official-code；commit `5eed38dfd25183049de733b3016ff1edb84266e5`（2026-07-07）；BSD-3-Clause | API snapshot `3fb7a6e68654c7534ad7b8e1786e5ade849114b07834bf00df426a7945f82aa2`；`river/drift/adwin.py` `beb3f8aac9d1796a73974c4c0059e36315096a9f6c053eceee8ca414bccf17c1`；LICENSE `e87f2c8f1ba611702af10cba745e6ceb773d32310135ed55aa2722c55dd0d077` | adaptive window、两个子窗口均值比较、`delta/clock/min_window/grace_period`与检测延迟/误报trade-off | ADWIN在任意VLA telemetry上自动检测真正concept drift；检测点就是cause或release decision |
| S5 | 本地前置节点 | canonical local prerequisites | EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-007 `66800fd21d8d2ebb786b0f8d3234c2613b427a986f41432f93cba99c3596e278`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd`；EVAL-012 `7360b1ae5eadef08620f91c510df9b98a958f0992a153c59c49de0577f821478`；EVAL-013 `9b47d6cd3dbea63e16d80c2fd25c7d68d1aa8f642b11b75913eb58f7449470bb`；EVAL-017 `15f22c200c5b143a789a0152ba8be189533f70cf4ad89612d50717c7ae54c739`；EVAL-019 `01446407420dae1382eaccf503b66e1a06b2017e46a10b81bd13af81dc9568a0`；EVAL-020 `c85f5ca7ac79d3e942b0ba29916212435d7fe58ab6a28c254e1e25868a51397d` | protocol identity、coverage、raw telemetry、regression/canary、offline-online、robustness、latency、selection与incident闭环 | 五项目已有live monitor、alert backtest、drift-impact因果或自动响应系统 |
| S6 | 五项目claim–evidence inventories | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | static manifests、protocol conflicts、failure signals与future monitoring设计输入 | 任一项目已有timestamped deployment stream、online labels、SLO、drift alarm或update governance闭环 |

S1—S4冻结持续治理、data validation、two-sample与stream change detection的公共边界；S5—S6将其映射到VLA。本页的drift taxonomy、monitoring planes、alert budget、response state machine和项目monitor schema是source-consistent engineering synthesis，不冒充NIST、TensorFlow、Gretton、River或项目原生实现。

## 2. Drift Taxonomy：先问什么分布变了

设时刻/窗口`t`的联合分布为：

\[
P_t(X,Y)=P_t(Y\mid X)P_t(X).
\]

变量解释：`X`可包含图像、语言、proprioception、robot/site/controller和task context；`Y`是成功、安全、人工标签或期望动作。直觉：输入变了与“同样输入下正确行为规则变了”不是同一种问题。实现映射：reference/current窗口分别保存feature、context和delayed outcome；缺`Y`时不能确认concept/performance drift。

| 类型 | 变化对象 | VLA例子 | 只能安全得出的结论 |
| --- | --- | --- | --- |
| schema / quality drift | shape、dtype、missing、range、timestamp | camera key缺失、7D/12D action、NaN、stale frame | 输入合同变化或数据损坏 |
| covariate / data drift | `P_t(X)` | 光照、视角、物体、task mix、语言、robot/site | current input与reference不同 |
| label / prior shift | `P_t(Y)` | success/failure比例或人工类别先验变 | outcome mix变化；原因未知 |
| concept drift | `P_t(Y|X)` | 同场景下安全动作/成功判定随controller或业务规则变 | 需标签或可信outcome验证 |
| protocol drift | eval/serve tuple变 | init、warmup、scorer、prompt/parser改变 | 指标不可直接纵向比较 |
| model / bundle drift | weights/processor/normalizer变 | silent checkpoint或stats切换 | lineage变化，不自动等于质量变化 |
| system drift | latency/resource/runtime变 | queue age、GPU/driver、network、tool failure | 执行条件变化 |
| behavior drift | policy output分布变 | action saturation、chunk/replan、tool depth、fallback | policy行为变化；好坏需outcome |
| scorer drift | success/reward/judge变 | threshold、VLM judge、parser revision | measurement system变化 |

deployment drift是上表多种变化的总称，不应只等同`P(X)`。

## 3. Reference Window 与 Current Window 合同

每个monitor先冻结：

- reference是training、validation、last-known-good production还是season-matched历史；
- current窗口按event、episode、robot-hour、site-day还是task-init pair聚合；
- window length、stride、minimum support、late-arrival与dedupe；
- model/processor/normalizer/controller/scorer bundle SHA；
- task/site/robot/camera/language/format等slice；
- seasonality、maintenance、rollout/canary与planned campaign标记；
- invalid/missing/abstain/timeout如何计数。

如果current窗口混入新模型、新site和新scorer，告警只能说“bundle/context一起变了”。必须先按lineage和context分层，再比较分布。

## 4. 五层 Monitoring Plane

```text
Plane 0 identity/provenance
 -> Plane 1 data quality + coverage
 -> Plane 2 system/latency/resource
 -> Plane 3 policy behavior + safety proxies
 -> Plane 4 delayed outcome + human/incident feedback
```

| Plane | 代表信号 | 为什么不能省 |
| --- | --- | --- |
| identity | code/model/data/processor/normalizer/controller/scorer SHA | 先区分drift与silent version change |
| data quality | schema、missing、range、timestamp、camera、language、task mix | 最快发现接口/采集问题 |
| system | capture→apply latency、queue age、timeout、OOM、fallback | 模型没变也会闭环退化 |
| behavior | action norm/saturation、chunk/replan、tool route、abstain、unsafe proxy | outcome到达前的早期信号 |
| outcome | per-task success、forbidden effect、recovery、human override、incident | 验证drift是否产生真实影响 |

单一overall dashboard会把critical slice、invalid和新support稀释掉。

## 5. Schema、Skew 与 Consecutive-span Drift

TFDV明确区分training-serving `skew`与不同training day/span之间的`drift`，在schema中提供`skew_comparator`和`drift_comparator`；官方schema定义`infinity_norm`、`jensen_shannon_divergence`及threshold字段。[S2]

对离散类别比例`p_j,q_j`，L-infinity距离为：

\[
D_{\infty}(p,q)=\max_j|p_j-q_j|.
\]

变量解释：`j`是task、format、language、camera-present或tool类别。直觉：找出占比变化最大的类别。实现映射：输出max-difference category、reference/current count和support；TFDV guide中的`0.01`只是示例阈值，不能复制为VLA默认阈值。[S2]

Jensen–Shannon divergence可写为：

\[
JS(p,q)=\frac12 KL(p\|m)+\frac12 KL(q\|m),\qquad m=\frac{p+q}{2}.
\]

变量解释：`m`是两分布混合，`KL`是Kullback–Leibler divergence。直觉：以共同中间分布对称比较两侧。实现映射：binning、unknown category、smoothing与单位必须冻结；高JS仍只表示分布不同，不证明性能下降。

## 6. High-dimensional / Embedding Drift 与 MMD

对reference samples`X={x_i}_{i=1}^m`、current samples`Y={y_j}_{j=1}^n`，RKHS中的population MMD为：

\[
\operatorname{MMD}[\mathcal F,p,q]
=\sup_{f\in\mathcal F}\left(E_p[f(X)]-E_q[f(Y)]\right).
\]

变量解释：`F`取characteristic RKHS unit ball时可区分分布；kernel、bandwidth和embedding extractor决定敏感方向。直觉：寻找最能区分两个窗口的函数。实现映射：冻结encoder SHA、layer/pooling、normalization、kernel/bandwidth、sample unit与permutation/bootstrap方法，并保存witness/top slices。[S3]

MMD适合多维image/text/state embedding，但有三重风险：encoder自身换版、support/seasonality混杂、统计显著但业务效应极小。必须与raw feature、coverage和outcome panel共同解释。

## 7. Streaming Change Detector：ADWIN 的位置

River的ADWIN维护可变长度窗口，将其分成两个子窗口比较均值；`delta`控制显著性，`clock`控制检查频率，`min_window_length/grace_period`控制最小证据与冷启动。[S4]

可输入的标量包括：

- success/failure或human override；
- timeout/fallback/invalid indicator；
- action saturation、queue age、latency；
- per-episode error或calibration residual。

不能把任意高维embedding先压成一个无语义分数再称concept drift。ADWIN检测的是输入序列统计变化；autocorrelation、campaign切换、模型发布和site maintenance仍需进入解释。

## 8. Fixed Window、Rolling Window 与 Seasonality

| 设计 | 优点 | 风险 |
| --- | --- | --- |
| frozen training reference | 语义稳定 | 可能把合法业务演化持续报警 |
| last-known-good production | 接近真实流量 | reference可能已经慢性漂移 |
| rolling recent window | 适应季节变化 | 渐进退化被reference吞掉 |
| season-matched reference | 减少昼夜/班次/任务campaign混杂 | 需更多历史support |
| canary-control concurrent | 最接近因果比较 | 需路由、pairing和安全权限 |

建议同时保留长期anchor、season-matched和concurrent control三类reference；rolling window不能成为唯一真相。

## 9. Drift Detection 不等于 Performance Impact

需要三步证据：

```text
drift signal
 -> localized affected slice / first divergence
 -> matched or controlled outcome degradation
```

对同一slice的reference/current风险估计，可报告：

\[
\widehat{\Delta R}_s=\widehat R_{current,s}-\widehat R_{reference,s}.
\]

变量解释：`R`可为failure、forbidden effect、deadline miss或human override rate，`s`是预注册slice。直觉：先问变化有没有落到真实风险上。实现映射：给support、cluster-aware interval、same scorer和lineage；没有标签时只标`impact_pending`，不能由MMD/JS替代。

若outcome延迟，应保存prediction/episode ID与后续label join ledger，监控label coverage和delay分布，防止“只有容易回传的case有标签”。

## 10. Coverage、Missingness 与 Selective Labels

必须监控：

- planned/observed/valid/labeled/invalid/timeout守恒；
- per-task/site/robot/camera/language/format support；
- label arrival rate、delay、human escalation与override；
- fallback/abstain后是否仍有outcome；
- 新category/unknown token/empty mask；
- sampling、retention与privacy删减是否改变可见分布。

只看已成功完成或已有label的episode会产生survivorship/selection bias。monitor本身也要有coverage SLO。

## 11. 多重检验、重复窗口与 Alert Fatigue

若有`d`个feature、`s`个slice、`w`个窗口与多个statistics，每分钟独立用`p<0.05`会产生大量false alarms。工程合同至少包含：

- primary monitors与diagnostic monitors分级；
- family-wise/FDR或confirmatory rerun策略；
- minimum effect size与minimum support；
- consecutive-window、cooldown、hysteresis与dedupe；
- expected alerts/day、page budget与owner；
- known campaign/maintenance suppression但保留audit log；
- false-positive/false-negative backtest与detection delay。

p-value回答“在null下多极端”，不等于effect重要，也不等于cause；阈值应在历史incident、synthetic shift与normal variation上backtest。

## 12. Threshold 与 Severity Contract

| 状态 | 例子 | 默认动作 |
| --- | --- | --- |
| INFO | identity一致、轻微distribution movement | 记录，不page |
| WARN | effect threshold超过且连续窗口成立 | slice诊断、加采样/label |
| CRITICAL | safety/deadline/forbidden effect或大范围unknown | 限权、fallback、rollback/canary stop |
| INCONCLUSIVE | support/labels/scorer不足 | 不自动PASS/FAIL，补证据 |

critical安全信号不能等待overall success显著下降；反之，单个embedding p-value也不能触发全量rollback。

## 13. Drift → Response State Machine

```text
OBSERVING
 -> ALERT_CANDIDATE
 -> VALIDATED_SIGNAL (identity/support/statistic checked)
 -> IMPACT_PENDING / IMPACT_CONFIRMED
 -> TRIAGED_CAUSE
 -> MITIGATE / ROLLBACK / RECALIBRATE / RETRAIN_CANDIDATE
 -> OFFLINE_REGRESSION
 -> SHADOW / CANARY
 -> RELEASED or REJECTED
 -> NEW_REFERENCE_APPROVAL
```

自动响应最多应停在安全限权/已预注册fallback；自动重训、自动替换reference或自动全量发布会把反馈、selection和holdout污染隐藏起来。[S1][S5]

## 14. Retrain / Recalibrate / Rollback 如何选

| 观察 | 优先动作 | 不能直接做 |
| --- | --- | --- |
| schema/processor错配 | block/load gate或修接口 | 用更多数据掩盖 |
| normalizer/action scale漂移 | 校验stats与recalibrate候选 | 未验证就全量替换 |
| input shift但outcome稳定 | 扩充stress/audit，观察 | 自动重训 |
| confirmed outcome degradation | 定位slice/cause，再定data/model/controller修复 | 只按overall微调 |
| system latency drift | capacity/queue/runtime修复 | 把问题归因模型权重 |
| scorer drift | 双跑旧/新scorer并重建comparability | 把历史曲线直接拼接 |
| safety critical | 限权/fallback/rollback | 等待统计平均显著 |

任何candidate update都要回到EVAL-010/017/019/020：regression、shadow/canary、selection/fresh audit和incident verification。

## 15. 最小 Artifact Bundle

```text
monitoring/
  monitor_registry.json
  reference_window_manifest.json
  current_window_manifests.jsonl
  lineage_and_context_registry.jsonl
  schema_quality_stats.parquet
  coverage_label_delay.parquet
  system_latency_resource.parquet
  behavior_safety_proxies.parquet
  delayed_outcomes.parquet
  slice_drift_statistics.parquet
  mmd_kernel_encoder_spec.json
  streaming_detector_state.json
  alert_thresholds_and_budget.json
  alert_incident_join.jsonl
  response_decisions.jsonl
  update_release_ledger.jsonl
  reference_promotion_approvals.jsonl
  checksums/manifest-sha256.txt
  reproduce_monitoring.ps1
```

`monitor_registry`逐项登记signal、unit、window、reference、slice、statistic、effect threshold、owner、retention与action；`reference_promotion`必须审批，不能让rolling current自动成为新的good baseline。

## 16. 持续监控伪代码

```python
def monitor_vla_window(reference, current, registry):
    # 1. Bind every row to one immutable deployment and scorer lineage.
    assert_identity_and_context(current, registry.bundle_contract)

    # 2. Check support and raw contracts before running statistical detectors.
    quality = validate_schema_missing_range_time(current, registry.schema)
    coverage = compute_planned_valid_labeled_conservation(current)

    # 3. Detect feature, embedding and streaming changes per registered slice.
    drift = run_registered_two_sample_and_stream_tests(
        reference, current, registry.detectors
    )

    # 4. Join delayed outcomes; a drift signal alone does not prove impact.
    impact = estimate_same_protocol_slice_risk_differences(
        reference, current, registry.outcome_contract
    )

    # 5. Apply alert budgets and route only evidence-complete decisions.
    alerts = validate_effect_support_persistence(drift, impact, registry.alerts)
    return persist_alert_and_response_ledger(quality, coverage, drift, impact, alerts)
```

伪代码是未来验收合同，不代表五项目已有deployment telemetry或monitoring service。

## 17. 五项目 Evidence Mapping

| 项目 | 当前可作为reference/diagnostic的证据 | Future monitors | 不能说 / 缺口 |
| --- | --- | --- | --- |
| OPD | static train/eval manifests；raw-holdout format/pool quotas；original strict/protocol-fixed/lenient协议差异；checkpoint by-pool表 | pool/format/language/image support，strict reject、parse/OOB、box/point/text metric，embedding与delayed human quality；全部绑定prompt/parser/scorer SHA | 没有timestamped serving stream、online label、alert/backtest；不能称已检测deployment drift或自动更新 |
| Robot Harness | task/tool schema、SFT/GRPO route/reward与静态eval summaries；safety multi-step failure | task/tool/version mix、tool-call depth、argument/schema reject、auth/timeout/cancel/side effect、fallback、human override和safety outcome | 约`38–44%` safety tool accuracy是静态failure evidence，不是live SLO；缺共同scorer/n、request trace与deployment stream |
| OpenPiVLA | multiple lineage、processor/normalizer/action-shape资料、formal Qwen eager路径与diagnostics | checkpoint/processor/normalizer identity、camera/state/action schema、action norm/saturation、chunk/replan、load reject、capture→apply latency、task success | 无formal checkpoint binary、统一online scorer、timestamped telemetry或real deployment；eager不等于drift fix |
| WAM | base/trained单episode、三camera字段、5k/10k单sample future proxy与若干failure hypotheses | camera presence/age、conditioning/sigma、action/gripper、world/value proxy、closed-loop success/recovery、resource/latency；均需同lineage | 单episode/单sample不能建立reference distribution、threshold或concept drift；无deployment labels与monitor service |
| UWM / LIBERO | fixed-pruned-init `186/250`与reset-style `232/250`是不同protocol；task map、normalizer/action contract与DataLoader wait smoke | task/init/scene/camera、normalizer/action saturation、chunk/replan、per-task success/recovery、data wait/step time、checkpoint/scorer identity | `0.928→0.744`是protocol distribution sensitivity，不是时间drift或model degradation；缺raw 250 episodes、timestamped stream、paired labels与alerts |

五项目都只提供monitor schema输入或离线reference候选，没有C3 deployment monitoring证据。本节点不新增“线上监控”“自动漂移检测”“自动重训”“production SLO”或ownership结论。

## 18. 常见失败模式

| 失败模式 | 症状 | 修复 |
| --- | --- | --- |
| drift=degradation | MMD/JS高就宣称性能差 | join outcome与same-protocol impact |
| one overall monitor | rare safety/task被稀释 | coverage cube与critical slices |
| rolling baseline only | 慢性退化被reference吞掉 | frozen anchor + seasonal + concurrent control |
| silent lineage mix | 新旧model/scorer混窗 | immutable lineage/context split |
| p-value paging | 高频窗口大量误报 | effect/support/persistence/alert budget |
| auto-retrain loop | 告警即抓当前数据重训 | evidence gate、fresh audit、shadow/canary |
| missing-label blindness | 只监控有label成功case | label coverage/delay与selective outcome |
| proxy-only safety | action norm正常就称安全 | forbidden/human/incident outcome |
| protocol shift called drift | reset/fixed或scorer变更拼曲线 | protocol namespace与comparability gate |
| reference promotion leak | current自动变baseline | approval、audit与rollback reference |

## 19. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 设计VLA drift/monitoring schema | 本页、registry与source freeze |
| C1 | 生成离线reference/current统计 | immutable windows、lineage、coverage与recompute |
| C2 | alert在历史/synthetic shift上有效 | threshold backtest、false alert、delay和slice evidence |
| C3 | drift与部署impact被验证 | timestamped telemetry、delayed labels、same-protocol control与incident join |
| C4 | response/update长期有效 | rollback/recalibrate/retrain gate、shadow/canary、reference governance与复发统计 |

当前五项目最多提供C0/C1输入，不到C2 alert backtest或C3 deployment impact。本节点保持`WARN`；下一内容节点固定为`VLA-EVAL-022`：paper→repo→checkpoint→runtime→ownership evidence audit。本切片不生成EVAL-022，也不创建`coaching_state.md`。

## 参考文献（References）

1. NIST, [*Artificial Intelligence Risk Management Framework (AI RMF 1.0)*](https://doi.org/10.6028/NIST.AI.100-1), January 2023；[AI RMF Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook)。
2. TensorFlow, [*Get started with TensorFlow Data Validation*](https://www.tensorflow.org/tfx/data_validation/get_started)；`tensorflow/metadata` [`schema.proto`@`f4f0753`](https://github.com/tensorflow/metadata/blob/f4f0753311ec2cfdedc84f09889f713b43f74d7a/tensorflow_metadata/proto/v0/schema.proto)。
3. Gretton et al., [*A Kernel Two-Sample Test*](https://www.jmlr.org/papers/v13/gretton12a.html), JMLR 13, 2012。
4. River, [`ADWIN`@`5eed38d`](https://github.com/online-ml/river/blob/5eed38dfd25183049de733b3016ff1edb84266e5/river/drift/adwin.py)；Bifet & Gavaldà, *Learning from Time-Changing Data with Adaptive Windowing*, 2007。
5. [EVAL-006 Protocol Versioning](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-007 Coverage](vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)、[EVAL-009 Recomputable Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010 Regression](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-011 Offline–Online](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)、[EVAL-012 Robustness](vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)、[EVAL-013 Latency](vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)、[EVAL-017 Release Gate](vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)、[EVAL-019 Selection](vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)与[EVAL-020 Incident](vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)。
6. [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
