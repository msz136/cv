# VOL 05 EVAL-017 Source Freeze：Simulator Success、Shadow Mode 与真机 Gate

> 状态：`source_frozen / VLA-EVAL-017 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结offline→simulator→live shadow/no-authority→guarded real canary→progressive promotion的证据阶梯、sim-real common support、counterfactual shadow边界、真机authority/risk envelope、abort/rollback/recovery与零事件上界；只生成一张`VLA-EVAL-017`原子题卡，EVAL-018后置。

## 问题（Question）

一个VLA在LIBERO/RoboCasa或自研simulator成功率很高，怎样安全推进到真机？答案不是“sim过线后直接上机器人”，也不是把shadow输出看起来合理当作闭环成功。可信release需要逐级扩大真实观测、执行权和风险暴露，每一级预注册promotion/abort条件，保存同一bundle与raw trace，并承认known-good rollback不会自动恢复已经改变的物理场景。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Li et al., *Evaluating Real-World Robot Manipulation Policies in Simulation*（SIMPLER） | primary paper；arXiv `2405.05941v1`，2024；论文许可未断言 | PDF `6a9481f3c0fc43fa6736e5f5fc8ddb72ebf05aad7dbd0ff31721e4d6bffec9e5` | 多policy上的sim-real matched evaluation、relative ranking与distribution-shift边界；simulation不完全替代real | 任意sim success可直接迁移；单一policy可建立相关性；默认gate阈值 |
| S2 | `simpler-env/SimplerEnv` | official-code；commit `06accaca93535902d408da4855f21cece12bceb7`；MIT | README `81aaa39d59e41c6b60d6ccdf09c17b1f0ca284ce7cb780b62b908afac6c0dc28`；metrics `ee8596be6997d41295bf5b25f90c9b5b3ba47ef2bd92296b8c45e7ffc5606dc6`；calc `c95963ec1452cb4f5f34db012eda79542c8afdd0465299ae30cf710c4b4a0521`；LICENSE `c28645822e5cdadf816144773ee153332449ae04aa6f0b6a6393e5611092f878` | REAL_PERF/SIMPLER_PERF policy-task mapping与Pearson/MMRV实现入口 | 用户项目已运行、真实硬件安全或canary机制 |
| S3 | Breck et al., *The ML Test Score* | primary paper；IEEE Big Data 2017；论文许可未断言 | Google Research page `e1588aa27c4a0aa74435327e92400443faf0b1ddf623068845571346484e1f6b`；PDF `8db5862dc7c7aaa2c55bb43bd42fc55531a0503782b7026b5811c00c98befd31` | offline testing不能保证live；重要slice release tests；old/new并行、小流量canary、rollback与监控 | 机器人shadow/authority定义、安全认证或本页阈值 |
| S4 | Argo Rollouts | official-code/docs；commit `9273b0ee05dbb629cc72fb9d343c08356c8379c8`；Apache-2.0 | LICENSE `c996fc213c94f4a4a838407d355b081226caa7b103a4f239bb87fb8f1d8e3a60`；canary `d50dadb21ed9ec2010be77ec0c7cde8af90a1b32e5af005102fad6a841b8c4ee`；analysis `2e4a68131130e307c396bd0cf431667152e599e056464e6eb22d2e18f348f8ae`；spec `0bcdbf333ffe7978f1530c3b79272a4098948154dde14bbf1807b212b6b8a665` | mirror/shadow route、traffic percentage、pause/analysis、abort与rollback window等progressive-delivery控制面 | pod traffic机制自动等于机器人动作安全；物理状态可软件rollback |
| S5 | Reality-gap / Sim2Real source audits | canonical local + frozen primary/doc snapshots | Sim2Real Audit `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200`；WM-031 `d25897218b4a276a0d9a981c826e8680ba21db7e64b298963eace10184877a97` | visual/sensor、dynamics/contact、control/timing、task/protocol与stochasticity gap；paired test与安全rollout边界 | 五项目已完成real-hardware transfer；randomization自动关闭gap |
| S6 | 本地前置节点 | canonical local prerequisites | EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd`；EVAL-014 `2027ea608960749f407099c56bac92528157e2125fd83525618507aa9f9f614a`；EVAL-016 `74a05d86958cfa3b620c363e34452597b453e3a3b8b0bc75b635bf5b987b6490` | golden/canary、sim-real panel、cancel/compensation、human/VLM proxy前置合同 | staged real-robot release已实施 |
| S7 | 五项目inventories + WAM manifest | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d`；WAM manifest `1ab8709201e2e75f580cb0aa0f8465defb546d63b2aab70a1752239a7da8f697` | 当前simulator/diagnostic/runtime artifacts与缺口 | live shadow、guarded real canary或个人真机认证 |

S1/S2支持sim-real相对评估，S3/S4提供通用parallel/mirror/canary控制机制，S5—S7约束机器人转换。下面的authority ladder、risk budget、shadow metrics、zero-event bound与artifact schema是source-consistent engineering synthesis，不冒充上游原协议。

## 2. 六级 Evidence / Authority Ladder

```text
L0 static/offline: dataset, parser, action validity, replay
L1 simulator: candidate controls simulated environment
L2 hardware-in-loop/dry-run: real stack, actuator disabled or isolated
L3 live shadow: real observations, candidate output logged, no actuator authority
L4 guarded real canary: bounded actuator authority under safety envelope
L5 progressive deployment: expand tasks/robots/time only after decision window
```

每一级同时增加三件事：realism、candidate authority和risk exposure。结论只能支持本级及其已观测support：simulator success不是real success；shadow不是closed-loop candidate success；一个小canary通过也不是全任务/长期安全认证。

L2和L3可合并实现，但语义要分开：hardware-in-loop验证真实serialization/controller/latency而不一定有live scene；shadow使用live真实观测，却让known-good policy/human继续控制或保持actuator disabled。

## 3. Simulator Gate

simulator success：

\[
\widehat p_{j,t}^{\mathrm{sim}}=
\frac{k_{j,t}^{\mathrm{sim}}}{n_{j,t}^{\mathrm{sim}}}.
\]

变量解释：`j`是policy/checkpoint，`t`是task/slice，`k/n`绑定init、seed、controller、predicate和valid/exclusion。直觉：一个95%数字只描述冻结sim protocol。实现映射：保存env/assets/physics/controller/camera/normalizer/horizon/action repeat/success code的revision和逐episode trace。

sim gate至少检查：

- common support上的baseline/candidate paired result与CI；
- clean、target perturbation、fault和critical safety slices；
- action/controller/time/normalizer roundtrip；
- collision/contact/forbidden effect和reset/termination；
- solver/physics/camera/domain randomization范围及其来源；
- reward/scorer hacking、unsolvable/invalid守恒；
- real calibration/incident数据是否落在target envelope。

高sim success可淘汰明显失败candidate、扩大failure coverage，不能单独授权真机。

## 4. Sim–Real Gap 与 Ranking

对同一policy-task common support：

\[
\Delta_{j,t}^{\mathrm{S2R}}=
\widehat p_{j,t}^{\mathrm{real}}-
\widehat p_{j,t}^{\mathrm{sim}}.
\]

变量解释：两侧必须对齐task语义、init family、controller/action、predicate和denominator；real trial较少时给二项/cluster uncertainty。直觉：absolute gap回答sim是否校准，rank回答是否能筛选policy。实现映射：多个真实policy/checkpoint`j`形成matched panel，报告Pearson/Spearman/MMRV、per-task gap、failure overlap和held-out prediction。[S1][S2]

单个policy只有一个sim/real pair，不能计算可靠相关性。即使rank保持，absolute success可能系统高估；可以说“所测support上适合前置筛选”，不能说“sim替代real”。

## 5. Shadow Mode：必须无 Candidate Actuator Authority

机器人shadow合同：

```text
live observation/state -> candidate inference -> safety projection/log
                                 X no dispatch to actuator
known-good policy / human / disabled actuator -> actual execution
```

Argo的`setMirrorRoute`把匹配流量镜像给canary而不替换primary response，提供软件shadow类比。[S4] 机器人实现必须额外在server/controller/hardware三层证明candidate output无dispatch path；仅在prompt写“shadow=true”不够。

shadow能验证：real sensor schema、latency/queue、missingness、action range、policy disagreement、projected constraint、OOD/abstain与logging。不能验证：candidate action执行后的下一观察、contact、closed-loop recovery、真实success或candidate-induced incident。

## 6. Shadow Metrics 与 Counterfactual Boundary

相对known-good/human action的disagreement：

\[
D_i=\mathbb{1}
\left[d(a_i^{\mathrm{candidate}},a_i^{\mathrm{reference}})>\tau_d\right].
\]

变量解释：`d/τ_d`绑定action semantics、frame、time和state；reference action不等于唯一正确答案。实现映射：记录observation/state version、candidate/reference action、safety projection、latency、OOD、reference source与实际执行action。

还要报：valid/finite/range、controller reject、projected collision/constraint、forbidden action、action-age、fallback/abstain、per-state/task disagreement与counterfactual evaluator uncertainty。对多解任务，action disagreement高不等于candidate错误；需要sim replay、human/state review或safe cloned-state experiment。

shadow日志是off-policy/counterfactual证据：candidate未改变未来state，因此把整条observed trajectory喂给candidate，只测“在known-good状态分布下会输出什么”，不测它自身诱导的state distribution。

## 7. 从 Shadow 到 Guarded Real Canary

promotion前冻结：

- candidate完整bundle/checkpoint/processor/normalizer/controller与rollback bundle；
- allowlisted robot、workspace、object、task/init、速度/力/位移/时长上限；
- independent safety controller、workspace/velocity/force limits与hardware E-stop；
- human supervisor、操作权限、通信与stop rehearsal；
- minimum exposure、decision window、success/safety/latency gates；
- abort trigger、safe-stop、scene recovery/manual reconcile与incident owner；
- baseline对照和同时间窗/环境support；
- raw observation/action/controller/effect/event/video bundle。

canary-0可先做free-space或软物体、低速、短horizon；随后逐步增加contact、task、robot和时窗。不能同时扩大model、controller、workspace、speed和task后把结果归因policy。

## 8. Authority 与 Risk Budget

每个canary stage登记最大暴露：

\[
B_s=\sum_{i\in s}w_i\,\Delta t_i,
\]

其中`w_i`是事前定义的risk/severity weight，`Δt`是candidate拥有真实执行权的时间或操作次数。变量解释：它是operational exposure账本，不是正式安全概率。实现映射：stage manifest保存robot-hours、episodes、contact count、max speed/force、human distance、object damage tier和不可逆操作数。

budget达到上限、观察窗结束或任一hard trigger出现即pause decision；不能因“还没收够成功样本”擅自继续危险暴露。

## 9. Canary Metrics 与 Denominator

至少同时报告：

| 维度 | 指标 |
| --- | --- |
| task | success `k/n/CI`、partial、time/steps、retry |
| safety | collision/near-miss/forbidden effect、limit trigger、E-stop |
| human | intervention/opportunity、takeover、false alarm、operator burden |
| systems | p50/p95/p99 latency、deadline miss、timeout、restart |
| control | tracking error、action clipping/reject、oscillation、stale action |
| recovery | safe-stop、quiescence、compensation/manual reconcile、scene reset |
| coverage | task/init/state/OOD、robot/site/time/thermal/payload exposure |

intervention rate的分母可以是eligible decision、episode或robot-hour，必须命名；只报“2次干预”不可比较。被human提前接管的episode不能从success/safety分母静默删除，应标记terminal reason和counterfactual不可识别。

## 10. 零事故不等于零风险

若`n`个独立Bernoulli exposure中观察到0次事件，在置信水平`1-α`下的exact单侧上界：

\[
p_{\mathrm{event}}^{\mathrm{upper}}=1-\alpha^{1/n}.
\]

变量解释：独立同分布假设在robot episode中往往过强；实际应按robot/day/task cluster并报告coverage。直觉：`0/10`仍允许很高未知风险，不能写“100%安全”。实现映射：给`0/n`、上界、exposure support、cluster、observation window和检测灵敏度；near-miss与intervention另报。

critical forbidden effect通常仍是hard veto，而不是等待统计显著。统计上界用于表达剩余不确定性，不是替代风险分析/工程limit。

## 11. Promotion 是 Conjunction，不是总分

\[
G_{mathrm{promote}}=
G_{mathrm{artifact}}\land G_{mathrm{offline}}\land
G_{mathrm{sim}}\land G_{mathrm{shadow}}\land
G_{mathrm{canary}}\land G_{mathrm{safety}}.
\]

变量解释：每个gate有预注册PASS/FAIL/INCONCLUSIVE与missing policy。直觉：overall success不能抵消forbidden effect、deadline或E-stop。实现映射：promotion decision记录每个gate输入SHA、decision maker、时间、override及理由；inconclusive默认不自动promote。

soft metrics可用于排序/调优，hard safety、artifact identity、scope和minimum exposure不能用weighted average洗掉。candidate只在当前stage范围被bless，扩大support需新stage。

## 12. Abort、Rollback 与 Physical Recovery

abort触发后链路：

```text
revoke candidate authority
 -> no new dispatch
 -> safe stop / quiescence
 -> switch future decisions to known-good bundle
 -> assess committed physical/business effects
 -> compensate or manual reconcile
 -> preserve incident bundle and block promotion
```

software rollback只恢复未来serving/controller bundle，不会把已移动物体、碰撞、订单或场景状态自动还原。[S6] 必须单独验证cancel accepted、last effect、quiescence、scene recovery和operator handoff。known-good也要做load/health smoke，避免rollback target失效。

## 13. Matched Staged Experiment

1. 冻结candidate/baseline完整bundle和stage contract；
2. simulator在target common support做paired clean/fault/safety matrix；
3. shadow接live observations但candidate output在多层被阻断，保存全部counterfactual动作；
4. 用shadow failure/coverage决定canary allowlist，不用同一数据反复调threshold后称holdout；
5. real canary按robot/task/time block与known-good交错，控制day/site/operator/thermal；
6. stage内达到minimum exposure且所有hard gate PASS才扩大一个authority维度；
7. abort/rollback/E-stop至少演练一次，真实trigger自动执行；
8. 每次decision由immutable raw bundle重算，incident进入regression但另留fresh holdout。

## 14. 最小 Artifact Bundle

```text
staged_robot_release/
  candidate_known_good_bundle_manifest.json
  gate_contract.json
  simulator/{protocol,episodes,summaries}/
  sim_real_panel.parquet
  shadow/{authority_proof,observations,candidate_actions,reference_actions}.parquet
  canary/{stage_manifest,episodes,exposure_ledger}.jsonl
  safety_events.jsonl
  interventions_abort_rollback.jsonl
  scene_recovery_manual_review.jsonl
  promotion_decisions.jsonl
  checksums/manifest-sha256.txt
  reproduce.ps1
```

authority proof需包含candidate credentials/tool/controller routes、server dispatch denial、actuator command source和hardware interlock测试；不能只靠配置字段。每个事件用episode/operation/robot/state/action IDs贯穿sim、shadow、canary与incident。

## 15. 评估伪代码

```python
def staged_robot_release(candidate, known_good, stages, safety):
    spec = freeze_bundle_gates_authority_risk_and_abort(stages)
    require(run_offline_and_simulator_gates(candidate, known_good, spec))

    # Candidate consumes live observations but cannot reach an actuator route.
    shadow = run_live_shadow(candidate, authority="none", proof=safety.dispatch_proof)
    require(evaluate_shadow_latency_disagreement_constraints(shadow, spec))

    for stage in spec.real_canary_stages:
        safety.assert_limits_and_estop(stage)
        result = run_guarded_real_canary(candidate, known_good, stage)
        persist_raw_events_before_summary(result)
        if result.hard_abort or not stage_gate_passes(result, stage):
            revoke_stop_rollback_and_reconcile(result, known_good, safety)
            return "ABORT"
        promote_one_authority_dimension(stage)
    return "PROMOTE_WITHIN_MEASURED_SUPPORT"
```

伪代码是release合同，不是五项目已有系统。

## 16. 五项目 Evidence Mapping

| 项目 | 当前最接近层级 | 能安全说 | 不能说 / 缺口 |
| --- | --- | --- | --- |
| UWM / LIBERO | L1 simulator summary/protocol；final `186/250`为user-confirmed且raw bundle缺 | 讲sim protocol控制、分母与下一步shadow设计 | real robot、live shadow、canary或Sim2Real完成 |
| WAM / Cosmos | 公开RoboCasa/LIBERO机制；本地单episodediagnostic | 可把episode作为一个regression/diagnostic case | 完整sim gate、human/VLM/real validation或canary |
| OpenPiVLA | official-checkpoint ALOHA/LIBERO rollout diagnostics + archive summary | 讲eval/deployment工程入口与lineage缺口 | formal Qwen checkpoint真实shadow/real canary；97.4对应真机 |
| Robot Harness | project sandbox/tool proxy与runtime scope/cancel入口 | 可复用authority proof、cancel和audit思想 | VLA simulator success、candidate shadow、real robot canary |
| OPD | L0 static point/box/text holdout | 可作为perception gate之一 | policy/controller/simulator/shadow/real execution |

五项目均没有`same candidate bundle → matched sim → live no-authority shadow → bounded real canary → promotion/abort`连续证据链。本节点不新增sim/real或canary结果。

## 17. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 设计staged release合同 | 本页、gate schema |
| C1 | simulator协议内成功/回归 | checkpoint-bound raw sim episodes与CI |
| C2 | live shadow通过 | no-authority proof、live input/action/latency/constraint traces |
| C3 | bounded real canary通过 | authority/risk envelope、raw episodes、intervention/safety、abort drill |
| C4 | measured support内progressive deployment | 多stage decision、longitudinal monitoring与incident response |

当前项目分别停在L0/L1/diagnostic，不能升级C2—C4。

本节点保持`WARN/unseen`。下一内容节点固定为`VLA-EVAL-018`：factorial ablation、matched baseline与因果边界；本切片不生成该节点，也不创建`coaching_state.md`。

## 参考文献（References）

1. Li et al., [*Evaluating Real-World Robot Manipulation Policies in Simulation*, arXiv:2405.05941v1](https://arxiv.org/abs/2405.05941v1)；[SimplerEnv@06accac](https://github.com/simpler-env/SimplerEnv/tree/06accaca93535902d408da4855f21cece12bceb7)。
2. Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/), 2017。
3. Argo Rollouts, [Canary](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/canary/index.md)、[Analysis](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/analysis.md)与[mirror/specification](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/specification.md)。
4. [VOL 04 Sim2Real Audit](vol_04_sim2real_claim_to_mechanism.html)与[WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。
5. [EVAL-010 Regression/Canary](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-011 Sim/Real Correlation](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)、[EVAL-014 Cancel/Compensation](vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)与[EVAL-016 VLM/Human Proxy](vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)。
6. [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)与[OPD](../evidence/projects/opd_claim_evidence_inventory.html) inventories。
