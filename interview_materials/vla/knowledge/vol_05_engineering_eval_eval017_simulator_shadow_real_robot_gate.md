# VLA Engineering / Evaluation：Simulator Success、Shadow Mode 与真机 Gate

> 节点：`VLA-EVAL-017`  
> 状态：`drafted / knowledge_39_of_44 / card_1_of_1_unseen / WARN`  
> 更新日期：2026-07-19  
> 学习目标：能把simulator success、live shadow和guarded real canary放在不同authority/evidence层，设计sim-real common support、无执行权证明、风险暴露、promotion/abort/rollback与零事件不确定性，并准确陈述五项目现状。

## 1. 一页结论

```text
offline/replay
  -> simulator gate
  -> hardware dry-run
  -> live shadow (candidate authority = none)
  -> guarded real canary (bounded authority + safety envelope)
  -> progressive expansion / abort + recovery
```

面试先说：

1. simulator success只属于冻结sim protocol，必须做多policy的matched sim-real validation；
2. shadow使用live observation但candidate action不进入actuator，所以不能报candidate closed-loop success；
3. canary按robot/task/workspace/speed/force/time逐级扩大authority，并有独立safety controller与human stop；
4. promotion是hard gates的合取，abort后的software rollback只影响未来动作，物理场景另做recovery/reconcile。

## 2. Evidence / Authority Ladder

| 层 | Candidate authority | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| offline | 无 | parser/action/data/replay有效 | closed-loop |
| simulator | 控制sim | sim protocol内success/failure | real transfer |
| HIL/dry-run | actuator disabled/isolated | real serialization/controller/latency | candidate effect |
| live shadow | live sensor，无candidate dispatch | real input下action/latency/constraint | candidate闭环success |
| real canary | 受限真实执行 | measured envelope内真实outcome | 全任务/长期安全 |
| progressive | 分阶段扩大 | 已暴露support内gate | 未见support或认证 |

每升一级同时增加realism、candidate authority和risk exposure。层级不能跳：有sim summary不等于shadow，有shadow log不等于real canary。

## 3. Simulator Gate

\[
\widehat p_{j,t}^{\mathrm{sim}}=
\frac{k_{j,t}^{\mathrm{sim}}}{n_{j,t}^{\mathrm{sim}}}.
\]

变量解释：`j`是policy/checkpoint，`t`是task/slice；`k/n`必须绑定init/seed/controller/predicate和valid/exclusion。直觉：95%只表示该simulator及该protocol。实现映射：保存env/assets/physics/camera/controller/normalizer/action repeat/horizon/success code与逐episode trace。[1]

sim gate至少覆盖：

- baseline/candidate同case paired CI；
- clean、target perturbation、fault、OOD和critical safety slices；
- action/frame/unit/frequency/normalizer/controller roundtrip；
- contact/collision/forbidden effect/reset/termination；
- reality-gap参数和target envelope来源；
- reward/scorer exploit、invalid/unsolvable守恒；
- raw trace/video与可复算summary。

domain randomization增加覆盖，不自动证明real transfer；过宽范围还可能引入不可解场景或过度保守。[2]

## 4. Sim–Real Validation

\[
\Delta_{j,t}^{\mathrm{S2R}}=
\widehat p_{j,t}^{\mathrm{real}}-
\widehat p_{j,t}^{\mathrm{sim}}.
\]

变量解释：sim/real两侧对齐task、init family、controller/action、predicate和denominator。直觉：absolute gap看校准，rank看筛选能力。实现映射：多个policy/checkpoint形成matched panel，报告per-task gap、Pearson/Spearman/MMRV、failure overlap、CI和held-out prediction。[1][3]

SIMPLER在多个policy上研究simulation与real的relative performance和distribution shift边界。[1] 它支持“用sim筛选候选需matched validation”，不支持任意sim替代real。单个policy只有一对数字，无法证明rank correlation。

## 5. Shadow Mode：候选无执行权

```text
real observation/state -> candidate -> log + safety projection
                                  X actuator dispatch
known-good/human/disabled path -> actual execution
```

shadow必须在三层证明无authority：

- server/tool/router不接受candidate dispatch；
- controller command source只允许known-good/human；
- actuator/hardware interlock或credential隔离阻断candidate。

配置里一个`shadow=true`或prompt声明不够。Argo mirror route提供软件类比：请求可被镜像给canary，但primary response不被替换。[4] 机器人还需验证动作通路和硬件interlock。

## 6. Shadow 能测什么

\[
D_i=\mathbb{1}
\left[d(a_i^{\mathrm{candidate}},a_i^{\mathrm{reference}})>\tau_d\right].
\]

变量解释：`d/τ`绑定action semantics、frame、time和state。reference action不是唯一gold，多解任务需sim/human/state复核。实现映射：保存live observation、candidate/reference/actual action、safety projection、latency、OOD、abstain与reference source。

可测：

- real schema/missingness/visual shift；
- action finite/range/frame/controller acceptance；
- p50/p95/p99 latency、deadline/stale；
- projected collision/constraint/forbidden action；
- disagreement、OOD、fallback/abstain和logging completeness。

不可测：candidate action后的next state、contact、closed-loop recovery和真实task success。整条shadow trajectory来自known-good/human policy的state distribution，是off-policy counterfactual evidence；candidate自己可能把系统带入完全不同状态。

## 7. Guarded Real Canary 合同

promotion前冻结：

- candidate/known-good完整bundle与rollback health；
- allowlisted robot、task/init、workspace、object和time window；
- max speed/force/displacement/horizon/contact/irreversibility；
- safety controller、workspace/velocity/force limit和hardware E-stop；
- human supervisor、stop/takeover权限与演练；
- minimum exposure、decision window和hard/soft metrics；
- abort、safe-stop、quiescence、scene recovery/manual reconcile；
- 同时间窗baseline与raw observation/action/effect/video证据。

canary-0从free-space/低速/短horizon/软物体开始，每次只扩大一个authority维度；同时换model、controller、speed、workspace和task后无法归因。

## 8. Risk / Exposure Budget

\[
B_s=\sum_{i\in s}w_i\Delta t_i.
\]

变量解释：`w_i`是预注册severity/risk weight，`Δt_i`是stage内真实authority时长或操作数。这是operational exposure账本，不是形式化风险概率。实现映射：记录robot-hours、episode/contact count、速度/力、human distance、damage tier和不可逆操作。[5]

达到budget上限、decision window或hard trigger即pause/abort；不能为了凑成功样本继续危险暴露。

## 9. Canary Metrics

| 维度 | 指标 |
| --- | --- |
| task | success k/n/CI、partial、time/steps/retry |
| safety | collision/near-miss/forbidden effect、limit/E-stop |
| human | intervention per opportunity、takeover、operator burden |
| systems | latency tail、deadline miss、timeout/restart |
| control | tracking、clip/reject、oscillation、stale action |
| recovery | stop/quiescence、compensation/manual、scene reset |
| coverage | task/init/state/OOD、robot/site/time/payload/thermal |

intervention分母可以是decision opportunity、episode或robot-hour，必须命名。human提前接管的episode保留terminal reason，不能从success/safety分母删除；其未干预counterfactual结果通常不可识别。

## 10. 0/N 事件仍有不确定性

在独立同分布Bernoulli假设下，0次事件的`1-α`单侧上界：

\[
p_{\mathrm{event}}^{\mathrm{upper}}=1-\alpha^{1/n}.
\]

变量解释：`n`是有效暴露。直觉：0/10绝不等于零风险。实现映射：报告0/n、上界、task/robot/day support、检测灵敏度、near-miss和intervention；实际episode相关，应按robot/day/task cluster并承认模型假设。[5]

critical forbidden effect仍可一票否决；统计上界表达剩余不确定性，不替代engineering limits和risk analysis。

## 11. Promotion Gate

\[
G_{mathrm{promote}}=
G_{mathrm{artifact}}\land G_{mathrm{offline}}\land
G_{mathrm{sim}}\land G_{mathrm{shadow}}\land
G_{mathrm{canary}}\land G_{mathrm{safety}}.
\]

变量解释：每个gate有PASS/FAIL/INCONCLUSIVE和missing policy。直觉：overall success不能抵消collision、forbidden effect或deadline miss。实现映射：promotion record保存输入SHA、decision、owner、时间、override理由；inconclusive默认不promote。[4][5]

soft metrics可以排序candidate，hard artifact/safety/scope/minimum-exposure不能加权平均。一次promotion只bless当前support和authority范围。

## 12. Abort、Rollback、Recovery

```text
revoke candidate authority
 -> stop new dispatch
 -> safe stop / quiescence
 -> known-good handles future decisions
 -> inspect committed effects
 -> compensate/manual reconcile + scene reset
 -> preserve incident bundle and block promotion
```

software rollback不会自动把物体放回、修复碰撞或撤销外部副作用；EVAL-014的cancel/quiescence/compensation合同继续适用。[6] known-good bundle要预加载/health-check，rollback/E-stop至少演练一次。

## 13. Artifact Bundle

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

```python
def staged_release(candidate, known_good, stages, safety):
    spec = freeze_bundle_gates_authority_risk_abort(stages)
    require(run_offline_and_sim_gates(candidate, known_good, spec))

    shadow = run_live_shadow(candidate, actuator_authority="none")
    require(verify_no_dispatch_and_shadow_metrics(shadow, spec, safety))

    for stage in spec.real_canaries:
        safety.verify_limits_estop_and_human_stop(stage)
        result = run_bounded_real_canary(candidate, known_good, stage)
        persist_raw_events(result)
        if result.hard_abort or not gate_passes(result, stage):
            revoke_stop_rollback_and_reconcile(result, known_good, safety)
            return "ABORT"
        expand_one_authority_dimension(stage)
    return "PROMOTE_WITHIN_MEASURED_SUPPORT"
```

这是release合同，不代表五项目已有实现。

## 14. 五项目面试边界

### UWM / LIBERO

`186/250`是user-confirmed simulator summary且raw episodes/checkpoint/normalizer仍缺；可讲protocol和未来stage设计，不能讲real shadow、canary或Sim2Real完成。[7]

### WAM / Cosmos

公开RoboCasa/LIBERO机制与本地单episode diagnostic最多是sim/diagnostic入口；没有完整sim gate、real validation或canary。

### OpenPiVLA

official checkpoint的ALOHA/LIBERO rollout diagnostics与archive summary支持eval/deployment接口讨论；formal Qwen checkpoint没有真实shadow/real canary，97.4不能写成真机。

### Robot Harness / OPD

Harness的sandbox、scope/cancel runtime可复用authority/audit设计，但不是VLA sim/real chain；OPD是static perception holdout，仅能做L0 gate。

## 15. 追问防线

- **sim 95%为何不能上真机？** 只属于冻结sim protocol，reality gap和真实风险未观测。
- **shadow和canary区别？** shadow无candidate actuator authority；canary有受限真实authority。
- **shadow能报成功率吗？** 不能报candidate closed-loop success，因未来state由reference policy产生。
- **reference action不同就candidate错吗？** 多解任务不一定；需state/sim/human复核。
- **0事故意味着安全吗？** 报0/n、上界、coverage和检测灵敏度。
- **rollback能恢复场景吗？** 只切未来bundle；物理状态需stop、补偿和人工reconcile。
- **怎样扩大canary？** 每次只扩大robot/task/workspace/speed/time中的一个authority维度。
- **项目做到哪里？** 当前L0/L1/diagnostic，没有连续shadow→real canary证据。

## 16. 本节点状态

EVAL-017知识与一张题卡保持`WARN/unseen`。五项目缺`same candidate bundle → matched sim → live no-authority shadow → bounded real canary → promotion/abort`连续证据链。本节点不新增sim/real结果。下一节点是`VLA-EVAL-018`：factorial ablation、matched baseline与因果边界；没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. Li et al., [SIMPLER, arXiv:2405.05941v1](https://arxiv.org/abs/2405.05941v1)与[SimplerEnv](https://github.com/simpler-env/SimplerEnv/tree/06accaca93535902d408da4855f21cece12bceb7)。
2. [VOL 04 Sim2Real Audit](../sources/vol_04_sim2real_claim_to_mechanism.html)与[WM-031 Reality Gap](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。
3. [EVAL-011 Sim/Real Correlation](vol_05_engineering_eval_eval011_offline_online_correlation.html)。
4. Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/)；Argo Rollouts [mirror/canary specification](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/specification.md)。
5. [EVAL-017 Source Freeze](../sources/vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)与[EVAL-010 Regression Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)。
6. [EVAL-014 Cancel / Compensation](vol_05_engineering_eval_eval014_forbidden_side_effect_scope_cancel_compensation.html)。
7. [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)与[OPD](../evidence/projects/opd_claim_evidence_inventory.html) inventories。
