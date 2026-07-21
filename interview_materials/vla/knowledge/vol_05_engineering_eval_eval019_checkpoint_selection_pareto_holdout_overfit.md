# VOL 05 Engineering / Evaluation：EVAL-019 Checkpoint Selection、Pareto Frontier 与 Holdout Overfit

> 状态：`drafted / VLA-EVAL-019 / knowledge_41_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 难度：L2　优先级：P0  
> 来源冻结：[EVAL-019 Source Freeze](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)  
> 本页建立candidate→feasible→Pareto→selected→fresh audit链路；不把每列最佳数字、反复访问的holdout或不同lineage结果拼成“最佳checkpoint”。

## 1. 问题与30秒框架

checkpoint多、metric多时，真正的问题不是“哪个数字最高”，而是：哪些checkpoint有资格参与、哪些metric只是development信号、哪些是hard gate、trade-off怎样表达、最终谁有权做selection、以及选完后用什么独立证据估计泛化。

```text
freeze candidates + metric roles
 -> development evaluation
 -> hard feasible set
 -> uncertainty-aware Pareto set
 -> frozen decision rule selects one real bundle
 -> lock SHA/threshold
 -> one-shot fresh audit
```

Pareto frontier负责保留不可互相支配的trade-offs，不负责自动产生唯一winner；final test负责估计已选流程，不负责继续挑checkpoint。

## 2. 四个集合：C、F、P、c*

| 集合 | 含义 | 典型错误 |
| --- | --- | --- |
| candidate `C` | 事前登记、完整可加载的checkpoint bundles | 看完test后临时补一个更好checkpoint |
| feasible `F` | 通过artifact/safety/latency/coverage hard gates | overall高分抵消critical failure |
| Pareto `P` | `F`中不被其他candidate支配的集合 | 把frontier叫成一个“最佳点” |
| selected `c*` | 按冻结业务规则从`P`选出的一个bundle | 每个metric各拿不同checkpoint |

所有点必须是真实bundle：checkpoint、processor、normalizer、controller和scorer共同锁定。把ckpt3000的Box IoU与ckpt5000的Point Hit拼在一行，是不存在的Frankenstein模型。

## 3. Metric-role Registry

每个metric先登记角色：

| role | 用途 | 是否可反复看 |
| --- | --- | --- |
| train | gradient/reward/online optimization | 按训练协议 |
| development | hyperparameter、early stop、checkpoint、threshold选择 | 可以，但要记access |
| hard gate | artifact/safety/deadline/critical coverage | 按预注册判定 |
| audit-only | 最终锁定bundle的独立泛化估计 | 原则上一轮一次 |
| monitoring | deployment后漂移/incident | 不能回写旧test claim |

同一个metric可以有不同数据实例，但同一rows被用于selection后就不是untouched audit。scorer model、prompt、parser、threshold、aggregation和direction都要有SHA/版本。[1][2]

## 4. Candidate Registry 与 Early Stopping

candidate registry至少保存：run/attempt/checkpoint/parent、step/tokens、code/data/config、processor/normalizer/controller、completion/load smoke、eligible状态和已查看metric。

early stopping本身就是model selection，必须冻结：

- metric与maximize/minimize；
- cadence、patience、`min_delta`；
- warmup和eligible step range；
- tie-break：earlier、later或lower-cost；
- NaN/missing/failure处理；
- last、EMA、averaged和best的身份。

保存更密的checkpoint会扩大candidate set；在噪声validation上从更多点取max，winner's curse通常更严重。

## 5. 为什么 Validation Best 会乐观

令真实utility为`U(c)`，validation估计为：

\[
\widehat U_v(c)=U(c)+\epsilon_c,
\qquad
c^*=\arg\max_{c\in\mathcal C}\widehat U_v(c).
\]

变量解释：`ε_c`来自有限样本、training seed、task mix和scorer噪声。直觉：winner既可能真实好，也更可能撞上正向噪声。实现映射：candidate count、每个candidate完整validation vector和最终audit差值必须保留，不能只保存winner。[1][3]

selection optimism记为：

\[
B_{sel}=E\!\left[\widehat U_v(c^*)-U(c^*)\right].
\]

它通常随搜索空间和估计噪声增大，但不是每个有限样本都必然为正的常数。Cawley–Talbot的核心边界是：selection criterion也会被过拟合，评估必须包含完整selection procedure，而不是把选中checkpoint当预先指定。[1]

## 6. Holdout 为什么会“用旧”

以下都算holdout exposure：看overall/per-task、看失败视频、改parser/scorer、按结果补数据、换threshold、选下一checkpoint、让agent继续搜索。即使labels不可见，重复暴露细粒度score也会让开发过程适应该holdout。[2]

```text
holdout_access_log:
query_id, candidate_sha, shown_fields, actor, time,
decision, downstream_code_data_config_diff, cycle_id
```

如果audit已被用于改模型，应诚实重命名为development set并冻结新audit family。改文件名、清空日志或只隐藏raw rows不能恢复独立性。

## 7. Hard Gates 先过滤

令`g_k(c)≤0`为artifact identity、forbidden effect、safety、deadline、memory和minimum coverage约束：

\[
\mathcal F=\{c\in\mathcal C:g_k(c)\le0,\ \forall k\}.
\]

变量解释：`g_k`带unit、threshold、uncertainty与missing policy。直觉：critical failure意味着“不具备参选资格”，不是一个可以被overall平均掉的低分项。实现映射：hard-gate matrix保留PASS/FAIL/INCONCLUSIVE和输入artifact SHA；inconclusive默认不自动通过。[4]

## 8. Pareto Dominance

统一objective方向为“越大越好”，例如：

```text
z(c) = [macro_success, worst_slice_success,
        -forbidden_rate, -p99_latency, -GPU_hours]
```

若`c,d∈F`满足：

\[
c\succ d
\iff
(\forall j,\ z_j(c)\ge z_j(d))
\land(\exists j,\ z_j(c)>z_j(d)),
\]

则`c`支配`d`。Pareto set为：

\[
\mathcal P=\{c\in\mathcal F:\nexists d\in\mathcal F\text{ s.t. }d\succ c\}.
\]

变量解释：frontier保留所有不可支配checkpoint。直觉：一个点success更高但latency更慢时，两者可能都留在frontier。实现映射：pymoo提供non-dominated sorting入口；仓库仍需自行绑定metric语义、hard gates、uncertainty和真实checkpoint bundles。[5]

## 9. Frontier 不等于唯一 Winner

从`P`选一个bundle还需决策规则：

1. constrained：满足safety/worst-slice/latency floor后最大化primary utility；
2. lexicographic：safety→critical task→overall→cost；
3. reference/knee：按预注册业务目标选折中点；
4. scalarized：固定权重、方向和normalization；
5. 多profile：只有确实发布多个独立bundle时才保留多个winner。

\[
S_w(c)=\sum_{j=1}^{m}w_j\widetilde z_j(c),
\qquad w_j\ge0,\quad\sum_jw_j=1.
\]

变量解释：`\widetilde z_j`是冻结scale后的metric。直觉：权重/归一化一变，winner可能变。实现映射：decision record保存weights、reference range、tie-break和sensitivity analysis；看结果后调权重属于新一轮selection。

## 10. 不确定性下不要强行排序

raw mean差0.1pp可能只是episode/task/seed噪声。对paired difference`Δ_j(c,d)`，可用本仓库工程规则：

\[
c\succ_{robust}d
\iff
(\forall j,\mathrm{LCB}_{1-\alpha}[\Delta_j(c,d)]\ge-\epsilon_j)
\land
(\exists j,\mathrm{LCB}_{1-\alpha}[\Delta_j(c,d)]>\delta_j).
\]

变量解释：`ε_j`是non-inferiority margin，`δ_j`是practical superiority margin。直觉：所有目标都至少不劣、且某个目标实质更优才稳健删除对手。实现映射：CI按training seed、task/init pair、robot/site cluster；证据不足标`UNRESOLVED`，不把CI overlap机械写成相等。[3][4]

该规则是source-consistent synthesis，不是NSGA-II原始显著性算法。多candidate/metric还要控制multiplicity或做confirmatory rerun。

## 11. Nested Selection / Fresh Audit

nested protocol在inner data选择，在outer data估计完整选择流程：

\[
\widehat U_{nested}=\frac1K\sum_{k=1}^{K}
U\!\left(\operatorname{Select}(D_{inner}^{(k)}),D_{outer}^{(k)}\right).
\]

变量解释：每个outer fold都重新执行selection。直觉：要评估的是“选模型的方法”，不是事后幸运winner。实现映射：scikit-learn冻结example演示nested/non-nested入口；VLA训练昂贵、episode有task/scene/time cluster时，不能直接假设IID folds。[1][6]

昂贵VLA最低可信流程：只在development选→锁定bundle/threshold SHA→fresh audit仅评估该bundle→不根据audit回改。若回改，开启新cycle并换fresh audit family，原audit进入development history。

## 12. Method Claim 与 Deployment Selection

| 目标 | 正确统计单位 | 不能做 |
| --- | --- | --- |
| 方法平均是否更好 | 全training seeds/recipes的分布 | 只报best seed |
| 选择部署bundle | 合法candidate中的一个具体bundle | 把全seed均值当可部署checkpoint |
| benchmark性能 | 锁定selection procedure后的audit | 无限leaderboard提交再报最好 |
| real release | audit后通过EVAL-017 canary gate | offline frontier直接上真机 |

部署可以选一个实际checkpoint，但论文/简历里的method uplift仍要覆盖training randomness。二者不能互相替代。

## 13. Multi-task / Multi-metric 细节

每个objective登记unit、direction、aggregation、support、scorer SHA、CI和missing policy。建议同时看：

- per-task与macro/micro；
- target-weighted与worst critical slice；
- task success、forbidden/near-miss、latency/deadline；
- train/serve cost、memory与coverage；
- invalid/abstain/failure rate。

per-pool最佳点说明trade-off，但只有在weights、metric roles、candidate identity和selection history冻结后才有“global decision”。不同protocol/scorer的数字不能进入同一个Pareto向量。

## 14. 常见 Selection Leakage

| 失败模式 | 识别问题 | 修复 |
| --- | --- | --- |
| per-column best | 每列来自不同checkpoint | 一行一个bundle |
| test-selected epoch | test曲线决定best | dev选、fresh audit估计 |
| best-seed claim | 只留最高seed | 报全seed分布 |
| candidate creep | 看完结果再加点 | 新cycle+fresh audit |
| scorer drift | prompt/parser改变 | versioned scorer gate |
| overall洗安全 | critical fail被平均 | hard feasible set |
| missing deletion | OOM/invalid消失 | planned/failed守恒 |
| leaderboard loop | 多次提交后报最好 | exposure/submission ledger |

## 15. Artifact 与 Pipeline

```text
candidate + metric-role registries
 -> same development pairs
 -> hard gate matrix
 -> paired uncertainty + dominance graph
 -> Pareto set
 -> frozen decision record
 -> selected bundle lock
 -> one-shot fresh audit
 -> selection-vs-audit report
```

```python
def select_and_audit(spec, registry, dev_pairs, fresh_audit):
    # Freeze real candidate bundles, metric roles and all decision rules.
    candidates = lock_eligible_bundles(registry, spec)
    assert_zero_prior_exposure(fresh_audit)

    # Evaluate every bundle on the same development pairs and scorer revision.
    dev_raw = evaluate_same_pairs(candidates, dev_pairs, spec.dev_scorer)
    feasible = apply_hard_gates(dev_raw, spec.constraints)

    # Preserve uncertain trade-offs rather than choosing the noisiest mean.
    uncertainty = paired_hierarchical_intervals(feasible, spec)
    pareto = robust_non_dominated_set(feasible, uncertainty, spec.margins)

    # Choose one existing bundle using the pre-registered business rule.
    selected = apply_frozen_rule(pareto, spec.decision_rule)
    lock_bundle_and_thresholds(selected)

    # Audit only the locked bundle; any later change starts a new cycle.
    audit_raw = evaluate_once(selected, fresh_audit, spec.audit_scorer)
    return persist_full_selection_history(dev_raw, pareto, selected, audit_raw)
```

这是应补做的selection system，不是五项目已有实现。[7]

## 16. 五项目真实性映射

### OPD

ckpt1000–5000在同一10k raw-holdout有by-format/by-pool表，且semantic-nav、VG region/relation、keepalive、point的最佳点分散。它可靠地说明多目标trade-off；但当前没有selection/access ledger、raw predictions/CI、hard gates或冻结weights，所以不能认证ckpt5000是统计稳健global best，也不能证明10k仍是untouched final test。[7]

### Robot Harness

同ladder summary里，ckpt100/200主holdout近似相同，ckpt100在列出的argument与safety均值上不低于ckpt200；这是“critical safety不能被overall洗掉”的局部观察。缺raw paired rows/CI和预注册rule，不能升级robust dominance；base→SFT还存在n/scorer差异。

### OpenPiVLA

official-checkpoint diagnostics、archive 97.4与formal Qwen路径lineage不同。先闭合candidate bundle/metric/scorer registry；当前不能把97.4称为formal best checkpoint或把多个lineage放进同一frontier。

### WAM

base/trained各一个episode以及5k/10k单sample future proxy只够diagnostic；缺checkpoint binary、完整metric/denominator和candidate trajectory，不能做best-step或Pareto选择。

### UWM / LIBERO

Book-Caddy、fixed-pruned-init `186/250`和reset-style `232/250`属于不同scope/protocol，且最终checkpoint/raw episodes缺。没有checkpoint trajectory、selection rule或holdout access记录，不能称“从多个checkpoints选出的最佳模型”。

五项目没有C3 fresh-audit selection证据。本页不新增best checkpoint、Pareto membership、holdout independence或ownership结论。

## 17. 面试追问防线

- **为什么validation best会偏高？** 因为在含噪估计上取max，selection也会拟合噪声。
- **test只看几次可以吗？** 关键不只是次数，而是是否根据结果做了后续decision；每次都要入access log。
- **Pareto frontier哪个最好？** frontier没有唯一最好；还需冻结constraints、risk preference和tie-break。
- **overall最高为何不能选？** 可能违反safety/deadline/worst-slice hard gate。
- **不同metric各拿best行吗？** 不行，必须选择一个真实可加载bundle。
- **CI overlap是否无差异？** 不能机械判断；给paired effect、margin和UNRESOLVED状态。
- **best seed能部署为何不能写方法提升？** 部署选择与方法平均效果是不同estimand。
- **项目做到哪里？** OPD/Harness有trade-off输入证据，但没有完整selection→fresh audit系统。

## 18. 本节点状态

EVAL-019知识节点与一张题卡已起草并保持`WARN/unseen`。本页不把开发集最优、Pareto候选或项目summary升级为final泛化结论；没有真实口述前不创建`coaching_state.md`。下一节点是`VLA-EVAL-020`：incident timeline、root cause与bug-fix verification。

## 参考文献（References）

1. Cawley & Talbot, [*On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*](https://www.jmlr.org/papers/v11/cawley10a.html), JMLR 11, 2010。
2. Dwork et al., [*Generalization in Adaptive Data Analysis and Holdout Reuse*, arXiv:1506.02629v2](https://arxiv.org/abs/1506.02629v2)。
3. Bouthillier et al., [*Accounting for Variance in Machine Learning Benchmarks*, arXiv:2103.03098v1](https://arxiv.org/abs/2103.03098v1)。
4. [EVAL-010 Regression Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)与[EVAL-018 Factorial Boundary](vol_05_engineering_eval_eval018_factorial_ablation_matched_baseline_causal_boundary.html)。
5. Deb et al., [NSGA-II institutional copy](https://repository.ias.ac.in/83498/)；pymoo [non-dominated sorting](https://github.com/anyoptimization/pymoo/blob/23110c155aa8f31b5f1b86928227fb3931ba7f00/pymoo/util/nds/non_dominated_sorting.py)。
6. scikit-learn, [Nested versus non-nested cross-validation](https://github.com/scikit-learn/scikit-learn/blob/6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6/examples/model_selection/plot_nested_cross_validation_iris.py)。
7. [EVAL-019 Source Freeze](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)及[五项目inventories](../evidence/evidence_manifest.html)。
