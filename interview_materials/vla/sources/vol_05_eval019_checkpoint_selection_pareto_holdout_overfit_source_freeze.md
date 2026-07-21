# VOL 05 EVAL-019 Source Freeze：Checkpoint Selection、Pareto Frontier 与 Holdout Overfit

> 状态：`source_frozen / VLA-EVAL-019 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结checkpoint候选集、metric-role registry、model-selection optimism、adaptive holdout、hard-feasible set、Pareto dominance/frontier、uncertainty-aware decision、nested/fresh evaluation、selection exposure ledger与五项目边界；只服务`VLA-EVAL-019`，EVAL-020后置。

## 问题（Question）

训练产生几十个checkpoint，每个在success、safety、latency、不同task/pool和cost上各有优劣，怎样选最终模型？答案不是拿test上最高overall的checkpoint，也不是把每个metric的最佳数字拼成一个不存在的“best model”。可信流程要先冻结candidate set、metric角色、hard constraints和决策规则，只用development evidence选择一个真实bundle，再用未参与选择的audit/test做一次最终估计；反复查看并据此训练后，所谓holdout已经成为development set。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Cawley & Talbot, *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation* | primary paper；JMLR 11，2010；JMLR页面许可未断言 | PDF `db01ac8fabef3064a0297bfcf64fb9791bf35c4d03be7a51f5862260adfca206`；paper page `c3118f2b3a84d3826d6e45565a8e7f5a308b356635a30776844ded55b7db4509` | noisy model-selection criterion会被二级优化过拟合；performance evaluation需更严格的nested/double protocol | 本页VLA阈值、Pareto规则或用户项目已发生selection bias |
| S2 | Dwork et al., *Generalization in Adaptive Data Analysis and Holdout Reuse* | primary paper；arXiv `1506.02629v2`，2015；论文许可未断言 | PDF `dcfbb9aa401c62949123be2d74787c4f9cca48597f18860760ef1580ddb4bc71`；abs page `f0dfe6255c0fb4c9077aa079362bbbcb0c868835ce0dd853df6de32ae1ec0d3e` | 交互、adaptive分析中的generalization/holdout reuse风险与可控复用研究框架 | 普通test可无限查询；本文机制已在仓库实现；隐藏holdout天然无偏 |
| S3 | Deb et al., *A Fast Elitist Non-Dominated Sorting Genetic Algorithm for Multi-Objective Optimization: NSGA-II* + `anyoptimization/pymoo` | primary paper institutional copy；PPSN VI/2000；paper许可未断言；official-code commit `23110c155aa8f31b5f1b86928227fb3931ba7f00`；Apache-2.0 | paper `ec4f251a0e53905a79889ffa2953c5947032267f207b81b68c3cdd9cc343b5b6`；NDS code `b4b9b1d2971d91c57e16eb444513a64844a61d8972868e34d6955082020a1402`；docs `ed4120313bc6918d36b426e1f1bcfc7d9b596a07082048bbc46a689a116e8f84`；LICENSE `2d81ea060825006fc8f3fe28aa5dc0ffeb80faf325b612c955229157b8c10dc0` | 多目标non-dominated/Pareto集合与官方实现入口 | frontier自动给唯一checkpoint、VLA hard gate或统计显著性 |
| S4 | `scikit-learn/scikit-learn` nested vs non-nested CV example | official-code；commit `6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6`；BSD-3-Clause | example `322ec4d26e1f8b3f2e7567c42671541531a88de81e5c9f8f3d3aa373f6868e52`；COPYING `50d6a9d340f19ab355609917993114daf5f47e3161067bcf34955bbd05cd9cb0` | nested/non-nested selection与evaluation代码入口；例子引用S1并展示non-nested optimism | 机器人episode可直接IID分fold；用户项目已执行nested protocol |
| S5 | Bouthillier et al., *Accounting for Variance in Machine Learning Benchmarks* | primary paper；arXiv `2103.03098v1`，2021；论文许可未断言 | PDF `1f458f7e606e4db86b207315c049a38b52cacde15ad34def2cc6c29124fc5d4c` | data/init/augmentation/hyperparameter optimization方差、完整pipeline重复与paired comparison | best seed代表方法、单checkpoint test结果可忽略selection过程 |
| S6 | 本地前置节点 | canonical local prerequisites | EVAL-004 `c89c052a630692a12a20235fa6d53278f43e4509c6e567110f81f7c2eb427313`；EVAL-005 `16b6a4c7c8e284ca8bd8a7cc831c3fc553405668ea87a071c23147f8f804ff46`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd`；EVAL-015 `9136d4de46b2c754ba4ed23c6ac0515f2239d2031e246c7479876fb6baf5d872`；EVAL-018 `3798164600cdaacf43473d55e7f8d964cbbcc781e01ef1efa37ca88e82634bfd` | paired unit、estimand、protocol/scorer identity、raw bundle、golden gate、winner's curse、audit proxy与factorial selection边界 | 五项目已有clean final holdout、Pareto release或口述掌握 |
| S7 | 五项目claim–evidence inventories | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | checkpoint/pool/suite/scorer差异和缺口 | 任何项目已有预注册selection、未触碰audit holdout或统计稳健Pareto frontier |

S1—S5冻结model selection、adaptive holdout、多目标优化与nested evaluation的公共边界；S6—S7把它们映射到VLA。下面的metric-role registry、robust dominance、exposure ledger、release schema和项目selection建议是source-consistent engineering synthesis，不冒充论文或项目原protocol。

## 2. 先分清四个集合与四种数据职责

| 对象 | 作用 | 不能混成 |
| --- | --- | --- |
| candidate set `C` | 预注册可被选择的真实checkpoint bundles | 任意看过test后临时加入的checkpoint |
| feasible set `F` | 通过artifact/safety/latency等hard gates的candidates | 用overall高分抵消critical failure |
| Pareto set `P` | `F`中不被其他candidate支配的多目标集合 | 自动唯一winner |
| selected bundle `c*` | 按预注册规则从`P`选出的一个可部署bundle | 每个metric拼不同checkpoint的Frankenstein结果 |

数据职责也必须分开：

```text
train: gradient / fitting
development-validation: hyperparameter, early-stop, checkpoint, threshold selection
audit-test: one-shot estimate after all selection decisions freeze
canary/real: staged deployment evidence, not an extra offline tuning set
```

一旦audit/test结果被用来改loss、data、threshold、checkpoint或metric权重，它就加入development history；不能继续称为untouched final holdout。[S1][S2]

## 3. Candidate Registry 必须先冻结

每个candidate至少绑定：

- run/attempt/checkpoint ID、parent checkpoint和完整bundle SHA；
- train code/data/config/processor/normalizer/controller/scorer revisions；
- step/tokens/FLOPs/wall-clock、selection eligibility与completion state；
- checkpoint cadence、EMA/averaged/last语义；
- 是否因OOM/NaN/timeout/invalid/load failure被排除及预注册理由；
- 哪些metrics/slices已经被人或程序查看。

checkpoint保存越频繁，candidate count越大，选择噪声峰值的机会也越多。改变cadence、patience、`min_delta`或eligible window就是改变selection procedure，不是无关实现细节。

## 4. Model-selection Optimism / Winner's Curse

令`U(c)`是checkpoint `c`的真实目标utility，validation估计为`\widehat U_v(c)=U(c)+\epsilon_c`。选择：

\[
c^*=\arg\max_{c\in\mathcal C}\widehat U_v(c).
\]

即使每个`\widehat U_v(c)`单独近似无偏，`c*`也倾向同时拥有较好的真实utility和正向噪声。定义selection optimism：

\[
B_{\mathrm{sel}}=
E\!\left[\widehat U_v(c^*)-U(c^*)\right].
\]

变量解释：`C`是实际搜索过的checkpoint/hyperparameter/seed/metric combinations，`ε_c`包含有限样本与scorer噪声。直觉：搜索越宽、估计越噪，winner's curse风险通常越大。实现映射：报告candidate/query count、完整validation向量与最终fresh-test差值，不能只留winner。[S1][S5]

`B_sel`是分析对象，不是保证对每个有限实验严格为正的常数；关键是选择过程本身必须进入performance estimate，而不能假装checkpoint预先指定。

## 5. Adaptive Holdout：访问次数不是只有API调用

一次holdout exposure包括：

- 查看overall、per-task、failure sample、video或confusion matrix；
- 根据结果修改checkpoint、loss/data mix、prompt、parser、threshold或metric；
- 人工比较多次report后决定下一run；
- 让自动agent/optimizer查询并继续训练；
- 改scorer后在同一rows上重新选winner。

`holdout_access_log`应记录query ID、candidate SHA、展示字段、操作者、时间、下游decision和代码/data diff。只隐藏raw labels但反复暴露精细score，仍然可能适应其噪声。[S2]

若final holdout已被反复使用，诚实处理是将其重命名为development set，冻结新的fresh audit set，或使用有明确假设的adaptive-analysis机制；不能靠改文件名恢复独立性。

## 6. Early Stopping 与 Best Checkpoint 都是 Selection

early stopping合同至少包含：

| 字段 | 示例语义 |
| --- | --- |
| selection metric | validation macro success / loss / safety-composite |
| direction | maximize/minimize |
| cadence | every N updates/tokens，而非模糊“每epoch” |
| patience/min_delta | 连续多少次、最小改进多少 |
| warmup/eligible window | 哪些checkpoint可竞争 |
| tie-break | earlier/later/lower-cost checkpoint |
| missing/NaN policy | fail、worst、inconclusive或重试 |

“best checkpoint”只在该metric、validation support和selection rule内best。若用test选epoch，再用同test报告成绩，就是同一数据同时做selection与evaluation。

## 7. Hard Constraints 先于 Pareto

令`g_k(c)≤0`表示artifact identity、forbidden effect、safety、deadline、memory或minimum coverage等hard gate，feasible set为：

\[
\mathcal F=
\left\{c\in\mathcal C:\ g_k(c)\le 0,\ \forall k\right\}.
\]

变量解释：每个`g_k`必须有unit、threshold、uncertainty和missing policy。直觉：critical safety fail不是“一个较差objective”，而是candidate不可进入release frontier。实现映射：gate matrix保留PASS/FAIL/INCONCLUSIVE与raw evidence SHA；inconclusive默认不自动变PASS。[S6]

## 8. Pareto Dominance 与 Frontier

把所有objective统一成“越大越好”的向量`z(c)`，例如：

```text
z(c) = [macro_success, worst_slice_success,
        -forbidden_rate, -p99_latency, -GPU_hours]
```

对`c,d∈F`，若：

\[
c\succ d
\iff
\left(\forall j,\ z_j(c)\ge z_j(d)\right)
\land
\left(\exists j,\ z_j(c)>z_j(d)\right),
\]

则`c`支配`d`。Pareto set为：

\[
\mathcal P=
\left\{c\in\mathcal F:\nexists d\in\mathcal F\ \text{s.t.}\ d\succ c\right\}.
\]

变量解释：frontier只删除“所有目标都不更好且至少一个更差”的candidate。直觉：它揭示trade-off，不替团队选择风险偏好。实现映射：保存每个实际checkpoint的完整metric vector、direction、normalization、coverage和dominance graph；不能把不同checkpoint的列拼成一个点。[S3]

## 9. Pareto Set 不是最终决策

从`P`选一个bundle仍需预注册decision rule：

1. **constrained optimization**：先满足hard/worst-slice/latency floor，再最大化primary success；
2. **lexicographic**：safety→critical task→overall→cost逐层比较；
3. **reference point / knee**：选择离业务目标最近或边际收益骤降点，但算法/阈值先冻结；
4. **scalarization**：固定权重与normalization后求分数；
5. **multiple deployment profiles**：只有业务确有不同profile且每个bundle独立发布时才保留多个winner。

加权分数：

\[
S_w(c)=\sum_{j=1}^{m}w_j\,\widetilde z_j(c),
\qquad w_j\ge 0,\ \sum_j w_j=1.
\]

变量解释：`\widetilde z_j`是冻结scale/normalization后的metric，`w_j`是事前权重。直觉：权重或归一化一变，winner可能改变。实现映射：decision record保存权重、单位、reference范围与sensitivity analysis；看到结果后调权重属于额外selection。

## 10. Uncertainty-aware Frontier

raw mean frontier在小样本下会随噪声抖动。对paired difference`\Delta_j(c,d)=z_j(c)-z_j(d)`，可定义工程化robust dominance：

\[
c\succ_{\mathrm{robust}}d
\iff
\left(\forall j,\ \mathrm{LCB}_{1-\alpha}[\Delta_j(c,d)]\ge-\epsilon_j\right)
\land
\left(\exists j,\ \mathrm{LCB}_{1-\alpha}[\Delta_j(c,d)]>\delta_j\right).
\]

变量解释：`ε_j`是可接受non-inferiority margin，`δ_j`是practical superiority margin；CI按training seed、task/init pair和robot/site层次构造。直觉：不因0.1pp噪声就删除checkpoint。实现映射：pair registry、cluster bootstrap与margin preregistration进入artifact；不确定时标`UNRESOLVED`而非强行排序。[S5][S6]

这是本仓库的selection合同，不是Deb/NSGA-II原始统计检验。multiple candidates/objectives还需multiplicity或confirmatory rerun；CI overlap也不能机械等同“无差异”。

## 11. Nested / Fresh Evaluation

标准nested逻辑是：outer split只估计完整selection procedure；inner split负责选择hyperparameter/checkpoint。对outer folds：

\[
\widehat U_{\mathrm{nested}}=
\frac{1}{K}\sum_{k=1}^{K}
U\!\left(\operatorname{Select}(D_{\mathrm{inner}}^{(k)}),
D_{\mathrm{outer}}^{(k)}\right).
\]

变量解释：每个outer fold都要重跑完整selection，不能先在全数据选checkpoint再做outer evaluation。直觉：评估的是“选择流程”，不是幸运winner。实现映射：scikit-learn官方example提供nested/non-nested入口；机器人任务若因训练成本、时间/scene cluster不能IID nested，应使用冻结dev + one-shot fresh audit，并明确外推限制。[S1][S4]

对昂贵VLA训练，不能伪称做过nested retraining。最低可信替代是：固定candidate/selection policy→只在dev选一次→锁定bundle SHA→final audit只跑该bundle→不根据audit回改；若回改，开启新cycle并换fresh audit family。

## 12. Method Evaluation 与 Deployment Selection 分开

- **研究方法claim**：不能挑best seed；应对完整training-seed/recipe distribution报告均值、CI和failure rate。
- **部署checkpoint选择**：可以从多个合法trained bundles选一个，但selection procedure必须冻结并在fresh audit上评估。
- **benchmark submission**：若允许有限提交次数，submission history仍是selection exposure；leaderboard不可当无限validation。

“我们部署了最好seed”不证明方法平均更好；“所有seed平均好”也不自动给出哪个具体bundle满足部署hard gates。

## 13. Multi-task / Multi-metric Registry

每个metric登记：

| 字段 | 作用 |
| --- | --- |
| role | train / selection / hard gate / audit-only / monitoring |
| unit/direction | success probability、ms、J、collision per robot-hour等 |
| aggregation | per-task、macro、micro、target weight、worst slice |
| support | task/init/robot/site/time/payload |
| scorer revision | code/model/prompt/parser/threshold SHA |
| uncertainty | pair/block/cluster与CI方法 |
| missing policy | fail/worst/inconclusive/exclude-with-reason |

per-pool最佳点可以说明trade-off；若pool weights、metric roles或business target未冻结，就不能称global best。critical slice应为constraint或lexicographic层，而不是被大量easy samples稀释。

## 14. Selection / Audit Cycle 状态机

```text
freeze candidate set + metric roles + decision rule
 -> evaluate all candidates on development pairs
 -> apply hard gates
 -> estimate uncertainty-aware Pareto set
 -> choose one real bundle with a frozen tie-break
 -> lock candidate SHA and all thresholds
 -> evaluate once on fresh audit/test
 -> release / reject / inconclusive
```

若audit失败：保存结果，回到新的development cycle；原audit family不再对新candidate保持“未见”。不能删除失败candidate、重置访问次数或把同一test换名继续使用。

## 15. Selection Leakage / Failure Matrix

| 失败模式 | 症状 | 修复 |
| --- | --- | --- |
| per-metric cherry-pick | 表格每列来自不同checkpoint | 一行一个bundle；单一decision record |
| test-selected epoch | test曲线决定checkpoint | dev选择，fresh audit一次 |
| best-seed reporting | 只保留最高seed | 方法层报告全seed distribution |
| scorer drift | checkpoint间prompt/parser不同 | scorer SHA与semantic diff gate |
| candidate-set creep | 看完结果再加checkpoint | 新selection cycle与fresh audit |
| safety averaged away | overall高但critical fail | hard feasible set先过滤 |
| missing run deletion | OOM/invalid不入表 | planned/valid/failed守恒 |
| repeated leaderboard | 多次提交再报最好 | access budget与submission ledger |

## 16. 最小 Artifact Bundle

```text
checkpoint_selection/
  candidate_bundle_registry.jsonl
  metric_role_registry.json
  development_pair_registry.parquet
  candidate_metric_vectors.parquet
  hard_gate_matrix.json
  paired_uncertainty.json
  dominance_graph.json
  pareto_set.json
  decision_rule.json
  selected_bundle.lock.json
  holdout_access_log.jsonl
  audit_pair_registry.lock.json
  final_audit_raw.parquet
  selection_vs_audit_report.json
  deviations_and_new_cycle.jsonl
  checksums/manifest-sha256.txt
  reproduce.ps1
```

`selected_bundle.lock.json`必须引用唯一checkpoint/processor/normalizer/controller/scorer SHA；`final_audit_raw`只含该bundle，除非protocol事前允许多个finalists并对其selection multiplicity负责。

## 17. 选择伪代码

```python
def select_checkpoint(spec, candidate_registry, dev_pairs, fresh_audit):
    # 1. Freeze candidates, metric roles, hard gates and the decision rule.
    candidates = lock_eligible_bundles(candidate_registry, spec)
    assert_fresh_audit_has_zero_prior_exposure(fresh_audit)

    # 2. Evaluate every real bundle on identical development pairs and one scorer bundle.
    dev_raw = evaluate_same_pairs(candidates, dev_pairs, spec.dev_scorer)
    feasible = apply_hard_gates(dev_raw, spec.constraints)

    # 3. Keep uncertain trade-offs; do not force a winner from noisy means.
    effects = estimate_paired_hierarchical_uncertainty(feasible, spec)
    pareto = robust_non_dominated_set(feasible, effects, spec.margins)

    # 4. Pick one existing bundle with a pre-registered lexicographic/scalar rule.
    selected = apply_frozen_decision_rule(pareto, spec.decision_rule)
    lock_bundle_and_thresholds(selected)

    # 5. Audit exactly the locked bundle; any later change starts a new cycle.
    audit_raw = evaluate_once(selected, fresh_audit, spec.audit_scorer)
    return persist_selection_and_audit(dev_raw, effects, pareto, selected, audit_raw)
```

伪代码是未来验收合同，不代表五项目已有该系统。

## 18. 五项目 Evidence Mapping

| 项目 | 当前checkpoint/metric证据 | 可安全解释 | 不能说 / 缺口 |
| --- | --- | --- | --- |
| OPD | ckpt1000–5000同10k raw-holdout的by-format/by-pool表；pool最佳分散在2000/3000/4000/5000 | 多目标trade-off真实存在；ckpt5000是report中的综合默认候选 | 未冻结selection rule、holdout exposure、raw predictions/CI与hard gates；不能称统计稳健global best或untouched final test |
| Robot Harness | GRPO ckpt100/200在同ladder holdout/safety summary；ckpt100报告均值在列出的主/安全指标上不低于ckpt200 | 可用作“overall近似相同但safety不可忽略”的selection案例 | raw paired rows/CI、预注册decision和统一base→SFT scorer缺；不能宣称robust dominance或release winner |
| OpenPiVLA | official-checkpoint diagnostics、archive 97.4 summary、formal Qwen路径分属不同lineage | 先做candidate/lineage registry再谈选择 | 无统一候选集、同scorer metric vector、access log或fresh audit；不能把97.4当formal best checkpoint |
| WAM | base/trained单episode diagnostic；5k/10k单sample future proxy | 只能展示两个diagnostic artifact不同 | checkpoint binary、完整metric/denominator/candidate trajectory缺；不能做frontier或best-step选择 |
| UWM | Book-Caddy summary、user-confirmed fixed-protocol `186/250`与reset diagnostic `232/250` | 结果绑定各自protocol，先闭合bundle | 缺checkpoint trajectory、selection rule、raw episodes和holdout access；不能称从多个checkpoints选出的最佳模型 |

OPD/Harness提供了很好的面试trade-off案例，但都没有证据证明本页selection system已实施。OpenPiVLA/WAM/UWM连统一candidate registry也未闭合。本节点不新增任何best-checkpoint、Pareto membership、holdout independence或ownership结论。

## 19. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 设计checkpoint selection / Pareto协议 | 本页、metric roles与decision schema |
| C1 | 描述某checkpoint在某protocol上的metric vector | checkpoint/scorer/support绑定summary |
| C2 | development上得到可复算Pareto/decision | 完整candidate vectors、hard gates、raw pairs、uncertainty与预注册rule |
| C3 | selected bundle通过fresh audit | zero-prior-exposure ledger、locked bundle与one-shot raw audit |
| C4 | deployment profile持续有效 | canary、drift/incident与新support复验 |

当前项目最多到C1/局部C2输入，不到C2完整selection或C3 fresh audit。本节点保持`WARN`；下一内容节点固定为`VLA-EVAL-020`：incident timeline、root cause与bug-fix verification。本切片不生成EVAL-020，也不创建`coaching_state.md`。

## 参考文献（References）

1. Cawley & Talbot, [*On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation*](https://www.jmlr.org/papers/v11/cawley10a.html), JMLR 11, 2010。
2. Dwork et al., [*Generalization in Adaptive Data Analysis and Holdout Reuse*, arXiv:1506.02629v2](https://arxiv.org/abs/1506.02629v2)。
3. Deb et al., [*A Fast Elitist Non-Dominated Sorting Genetic Algorithm for Multi-Objective Optimization: NSGA-II*](https://repository.ias.ac.in/83498/)；pymoo [non-dominated sorting@`23110c1`](https://github.com/anyoptimization/pymoo/blob/23110c155aa8f31b5f1b86928227fb3931ba7f00/pymoo/util/nds/non_dominated_sorting.py)。
4. scikit-learn, [Nested versus non-nested cross-validation@`6d7f1f1`](https://github.com/scikit-learn/scikit-learn/blob/6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6/examples/model_selection/plot_nested_cross_validation_iris.py)。
5. Bouthillier et al., [*Accounting for Variance in Machine Learning Benchmarks*, arXiv:2103.03098v1](https://arxiv.org/abs/2103.03098v1)。
6. [EVAL-010 Regression Gate](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-011 Offline–Online / Winner's Curse](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)、[EVAL-015 Proxy Overoptimization](vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)与[EVAL-018 Factorial Selection Boundary](vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)。
7. [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
