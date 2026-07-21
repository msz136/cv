# VOL 05 EVAL-018 Source Freeze：Factorial Ablation、Matched Baseline 与因果边界

> 状态：`source_frozen / VLA-EVAL-018 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结factor/arm/estimand、2×2 factorial主效应与交互、matched baseline、seed/eval block、fixed-recipe与equal-search-budget双estimand、失败run/selection/multiplicity、因果识别边界及五项目真实性；只服务`VLA-EVAL-018`，EVAL-019后置。

## 问题（Question）

一个VLA加入world objective、value head、数据路由、teacher、synthetic data或GRPO后指标提高，怎样证明“是这个因素带来的”，而不是data、seed、算力、调参、checkpoint selection、scorer或评估协议一起变化？可信消融不是删掉一行配置再比较两个最好数字，而是先定义estimand，再冻结可执行factor与matched baseline，在所有factorial cells中随机化/区组化 nuisance，保存planned→started→valid→failed/excluded账本，并把结论限制在实际实验protocol和support内。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | NIST/SEMATECH e-Handbook：Full factorial / Two-level full factorial | official technical handbook snapshot；2026-07-19抓取；页面许可未断言 | full factorial `318899d330e9b2de2be35797e821257d8147b65a87efd7edaf2c4119530c0723`；two-level detail `5d090fa4e993f36a30a703cce65d833d6b3fe38b863250ad9e7f9da296c6b60d` | 每个factor level组合、`2^k` run数、±1 design/analysis matrix、main/interaction列与orthogonality | VLA默认factor、训练seed数、online阈值或项目已做消融 |
| S2 | NIST/SEMATECH e-Handbook：Randomized block designs | official technical handbook snapshot；2026-07-19抓取；页面许可未断言 | page `d2a934337cfc56bb01af4afef684f265dc085b42270cf0886a583bd2a8a82646` | nuisance factor、homogeneous block、block内比较、`block what you can, randomize what you cannot` | 同seed自动消除全部训练随机性；任意post-hoc matching可识别因果 |
| S3 | Bouthillier et al., *Accounting for Variance in Machine Learning Benchmarks* | primary paper；arXiv `2103.03098v1`，2021-03-01；论文许可未断言 | PDF `1f458f7e606e4db86b207315c049a38b52cacde15ad34def2cc6c29124fc5d4c`；abs page `d7507d6b57958bb11dae7fe48b0884213dbf7de36775363ee64356260a4e476a` | data sampling、augmentation、initialization、hyperparameter optimization等方差来源；多次完整pipeline、配对训练与不确定性 | 单次run因果结论、固定一个seed即代表总体、本文的factorial公式或VLA外推 |
| S4 | Hernán & Robins, *Causal Inference: What If* | primary textbook；official author site，2025-11-21 edition；版权/许可未断言 | landing page `8f471a4bb735758c8417f060f1b4af4530e139f214549715241f0ab445766487`；PDF `49b2830c75d6e90c05689b85dd8a5923d9797c3ac4928678cfdf3fe27814193b` | counterfactual outcome、randomized experiment、consistency、exchangeability、positivity与识别边界 | ML消融自动满足假设；训练因素对新任务/新硬件的普遍因果效果 |
| S5 | `statsmodels/statsmodels` | official-code；commit `1bf73add5d92f64e48cf2ca143dfeef9811e4eac`；BSD-3-Clause | `anova.py` `77d3cac7bdba407ff42be44c91c231803504635f8f3df10bd92235d644fb823a`；formula API `8af09a0616d33f4f7874f1e8cf72b03cdf57ffebc484d237a41172485553cbda`；LICENSE `1ca78e1dec9dcebc55f3b96a862317f23e76422c5fc943568d955aad1f6b5fad` | formula/ANOVA计算入口与可复核实现版本 | ANOVA输出自动获得因果解释、binary/cluster数据默认模型正确或项目结果 |
| S6 | 本地前置节点 | canonical local prerequisites | WM-041所在知识卷 `89a3a5edadaae6b4e5b1b44b11c3fe1ecf8fef0889847d442e67a43c87b8effe`；VOL04独立复核 `115eed1c2c3d0d98adc46acde2e8effe12f0305b2f7ea2a81c7fa3ffac2503c1`；EVAL-004 `c89c052a630692a12a20235fa6d53278f43e4509c6e567110f81f7c2eb427313`；EVAL-005 `16b6a4c7c8e284ca8bd8a7cc831c3fc553405668ea87a071c23147f8f804ff46`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd` | action-only/+world/+value/all框架、paired unit、estimand、protocol identity、raw bundle与correlation/causal边界 | 四臂已经执行、项目component uplift或口述掌握 |
| S7 | 五项目claim–evidence inventories | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 当前run/protocol/scorer/lineage与缺失消融边界 | 任一项目已有matched factorial、单组件因果提升或完整ownership |

S1—S5冻结通用DOE、ML benchmark方差、因果识别与计算入口；S6—S7把它们映射到VLA。下面的双estimand、run ledger、artifact schema和项目实验臂是source-consistent engineering synthesis，不冒充NIST、论文或项目已有protocol。

## 2. 先冻结五个对象：Factor、Arm、Unit、Outcome、Estimand

| 对象 | 必须写清 | VLA例子 | 常见偷换 |
| --- | --- | --- | --- |
| factor | 可执行、版本化的单一干预 | `world_loss_enabled={0,1}`且target/mask/weight冻结 | “用了world model”但data/head/loss都变 |
| arm/cell | factor levels的完整组合 | A00/A10/A01/A11 | 只跑baseline与all，却声称两个组件各自有效 |
| experimental unit | 被独立分配factor的单位 | 一次完整training pipeline run | 把同一run的episode当独立training replicates |
| outcome | protocol-bound结果与方向 | paired task success risk difference、latency、cost | 先看结果再挑最好metric |
| estimand | 要平均到哪个随机性/预算/support | frozen tasks与seed分布上的平均component effect | 用一个最好seed回答“平均是否有效” |

factor必须绑定`code/data/config/bundle SHA + semantic diff`。如果打开world objective同时增加视频数据、训练steps和head参数，则“objective on/off”不是单一factor；要拆成多factor设计，或把结论降级为“system bundle contrast”。

## 3. Matched Baseline 不是“名字相同”

一个baseline/candidate pair至少匹配：

- 相同base checkpoint bytes、processor/normalizer与可比的parameter-freeze policy；
- 相同train/validation/test source pool、split rule、sampling distribution与dedupe/leakage gate；
- 相同optimizer family、schedule语义、effective batch、precision与gradient budget，除非它们就是factor；
- 预先选择的fixed steps/tokens/FLOPs/wall-clock预算estimand；
- 相同task/init/controller/scorer/horizon/replan与raw eval pair IDs；
- 相同hyperparameter search空间、trial budget、selection rule与fresh holdout；
- 相同failure/exclusion policy，并保留crash/OOM/NaN/timeout；
- code/config diff只含预注册factor及其必要mechanical adaptation。

“相同epoch”在数据量不同的arm间不等于相同tokens；“相同steps”在FLOPs不同的arm间也不等于相同compute。必须先说要估计fixed-recipe机制差异，还是equal-resource系统能力差异。

## 4. 最小2×2 Factorial

令`A`为world objective，`B`为value objective，action主任务始终开启：

| Cell | A world | B value | 回答的问题 |
| --- | --- | --- | --- |
| A00 | off | off | action-only baseline |
| A10 | on | off | world在value关闭时的simple effect |
| A01 | off | on | value在world关闭时的simple effect |
| A11 | on | on | 联合、协同或冲突 |

每个cell都要跨多个training seeds完整训练，并在相同episode/task pair IDs上评估。只比较A00与A11只能估计“整个bundle变化”，无法分离A、B和interaction。

## 5. Cell Mean、主效应与交互效应

令`μ_ab=E[Y|do(A=a,B=b)]`为冻结protocol内cell outcome均值。0/1编码下的平均主效应和加性交互可写为：

\[
\tau_A=\frac{(\mu_{10}-\mu_{00})+(\mu_{11}-\mu_{01})}{2},
\qquad
\tau_B=\frac{(\mu_{01}-\mu_{00})+(\mu_{11}-\mu_{10})}{2},
\]

\[
\tau_{AB}=\mu_{11}-\mu_{10}-\mu_{01}+\mu_{00}.
\]

变量解释：`τ_A/τ_B`平均了另一factor的两个level；`τ_AB`回答联合变化是否偏离加和。直觉：A11最好不等于A和B分别都有效；可能只有A有效、B无效，或两者单独有效但联合冲突。实现映射：从每个seed×eval block的raw结果重算cell means和contrasts，不能从四个截图手算后丢失不确定性。[S1][S2]

若使用±1编码回归：

\[
g\!\left(E[Y_{r,e}]\right)=
\beta_0+\beta_A x_A+\beta_B x_B+\beta_{AB}x_Ax_B+b_r+c_e,
\]

其中`g`可为identity或logit，`b_r/c_e`表示training-run与eval block结构。系数缩放取决于编码和link；报告必须回到可解释的cell means、risk difference/odds scale与CI，不能只报`p<0.05`。[S5]

## 6. Seed、Dataset Split 与 Eval Pair 是 Block，不是装饰

对factor A的matched contrast，可在seed/block层先计算：

\[
d_{s,e}=Y_{A=1,s,e}-Y_{A=0,s,e},
\qquad
\widehat\tau_A=\frac{1}{|S||E|}\sum_{s\in S}\sum_{e\in E}d_{s,e}.
\]

变量解释：`s`可包含data split、initialization、augmentation/sampler seeds，`e`是task/init/eval pair。直觉：block内共享nuisance可提高比较功效，但episode不能替代training-run重复。实现映射：manifest分别记录training/data/env/rollout/bootstrap seed；CI按training run和task/episode hierarchy cluster/bootstrap。[S2][S3][S6]

相同整数seed不保证两arm消费完全相同随机数：新增module可能改变RNG调用顺序。seed pairing的含义是预注册共同randomness source与block ID；若无法保持coupling，仍要随机化并把run当独立replicate，不能伪造逐step一致。

## 7. 两个必须分开的 Estimand

### 7.1 Fixed-recipe effect

\[
\Delta_{\mathrm{fixed}}=
E\!\left[Y(\text{factor on},\lambda_0,B)-Y(\text{factor off},\lambda_0,B)\right].
\]

`λ0`是共同超参数recipe，`B`是固定steps/tokens/FLOPs等预算。它回答“在同recipe下打开组件发生什么”，适合机制诊断；若新组件需要不同weight/lr，负结果不等于其最佳能力无效。

### 7.2 Equal-search-budget system effect

\[
\Delta_{\mathrm{tuned}}=
E\!\left[Y(\text{on},\widehat\lambda_{\mathrm{on}},B,H)-
Y(\text{off},\widehat\lambda_{\mathrm{off}},B,H)\right].
\]

`H`是相同search space/trial/compute/selection protocol；两arm各自只在validation上调参，再在fresh holdout评估。它回答“给相同调参资源后哪个完整pipeline更好”。不能让candidate调50次、baseline只用默认值后称component effect。[S3]

## 8. Training Budget、Data Amount 与 Model Capacity

factorial表必须同时给四本账：

1. **data账**：unique samples、tokens/frames/actions、mix、repeats、augmentation；
2. **optimization账**：steps、effective batch、optimizer updates、schedule position；
3. **compute账**：FLOPs近似、GPU-hours、peak memory、failure/retry；
4. **capacity/runtime账**：trainable/total params、latency、throughput、planning calls。

如果auxiliary factor天然增加data或compute，可同时报告fixed-token与equal-wall-clock两个estimand，或承认它是bundle intervention。不要用一个“公平”标签掩盖不同资源定义。

## 9. Planned→Started→Valid→Failed/Excluded 守恒

每个cell预先登记`planned runs`。OOM、NaN、timeout、load failure和invalid eval不是可以静默删除的“坏seed”：

```text
planned = not_started + started
started = completed_valid + failed_runtime + excluded_protocol
```

先报告completion/failure rate，再按预注册policy做primary estimand。若factor导致更多OOM或invalid output，这本身是engineering outcome；只比较survivors会产生post-treatment selection bias。exploratory repaired rerun必须新run ID，不能覆盖失败记录。

## 10. Checkpoint Selection 与 Test Reuse

- selection metric、cadence、patience、tie-break和eligible checkpoints在训练前冻结；
- 所有arms共享validation support和selection budget；
- test/real-canary不参与weight、threshold或checkpoint选择；
- 报last、pre-registered selected与oracle-best的身份，oracle只作诊断；
- 多次查看test再选factor属于adaptive overfit，需fresh holdout或nested protocol。

比较“baseline last”与“candidate best”不是ablation；不同checkpoint lineage、processor、normalizer或scorer也不是matched cells。

## 11. Binary Success 的 Scale 与层次结构

对closed-loop binary success，cell mean是risk/probability。`τ_AB`在risk-difference加性尺度上的0，不代表log-odds尺度也无interaction。必须声明scale，并给每cell`k/n/CI`、task macro/micro、training-seed分布与paired episode contrast。

episode只估计某个trained policy的conditional success；training seeds、tasks、robots/sites/day等高层变异不能被几千episode伪装成几千独立训练重复。small number of runs时，重点报告cell/seed raw table、effect CI与方向稳定性，不靠渐近`p`值制造确定性。

## 12. Multiplicity 与 Confirmatory / Exploratory 分层

一个`2^k`设计会产生多项main/interaction effects，再乘tasks、metrics、checkpoints和slices。primary outcome、primary contrast、family与practical margin应预注册；其余标exploratory。多重检验可沿用EVAL-004的Holm/FDR合同，但校正不能修复protocol不匹配、post-hoc factor定义或缺失runs。[S6]

## 13. 因果识别边界

对实验unit `u`，factor A的potential outcomes记为`Y_u(1)`与`Y_u(0)`；同一unit不能同时观测两者。factorial随机分配/完整执行要把observed contrast识别为protocol内因果effect，至少需要：

| 条件 | ML/VLA解释 | 典型破坏 |
| --- | --- | --- |
| consistency | factor level有唯一、版本化实现 | “world on”在不同arm使用不同data/weight/head |
| exchangeability | factor assignment不被结果相关nuisance决定 | 只给candidate挑好seed/好hardware |
| positivity | 每个目标block都有所有必要arms | hard task只跑candidate、easy task只跑baseline |
| no interference | 一个run不污染另一个run的data/cache/label/serving | candidate生成数据泄漏进baseline；shared adaptive scorer |
| complete outcome accounting | 失败/缺失按预注册policy处理 | OOM seed静默删除 |

即使内部识别成立，结论仍只到冻结data/task/model/budget/hardware/eval support。它不自动外推到新机器人、真实世界、长期deployment或“该思想普遍有效”。[S4]

## 14. Full、Fractional 与 Sequential Design

`k`个二水平factor的full factorial需要`2^k` cells；NIST明确指出factor增加时run数快速膨胀。[S1] 工程上可以：

1. 先用mechanism/evidence选择2—4个高价值factor；
2. 低成本offline/sim做screening；
3. 若用fractional factorial，明确resolution与alias structure，不把confounded effects分开解释；
4. 对入选factor补完整factorial和更多training seeds；
5. 最后才进入昂贵closed-loop/real stage，并保留confirmatory holdout。

one-factor-at-a-time容易漏interaction；fractional design节省cells但引入alias。二者都不能在不声明限制时替代full factorial。

## 15. 最小 Artifact Bundle

```text
factorial_ablation/
  preregistration/{factors,levels,estimands,outcomes,margins}.json
  baseline_candidate_bundle_manifest.json
  design_matrix.parquet
  run_registry.jsonl
  config_semantic_diffs/
  train/{logs,checkpoints,failure_records}/
  selection_decisions.jsonl
  eval_pair_registry.parquet
  raw_episode_results.parquet
  cell_seed_task_summary.parquet
  main_interaction_effects.json
  compute_data_capacity_ledger.json
  multiplicity_and_deviation_log.json
  checksums/manifest-sha256.txt
  reproduce.ps1
```

`design_matrix`一行对应planned training run，记录factor levels、block IDs、randomization order、initial bundle、data/config/code SHA与预算；`run_registry`即使失败也不能缺行。

## 16. 评估伪代码

```python
def run_factorial_ablation(spec, factor_grid, train_blocks, eval_pairs):
    # 1. Freeze estimands, budgets, outcomes and all planned cells before training.
    design = randomize_within_blocks(factor_grid, train_blocks, spec)
    registry = create_planned_run_registry(design)

    for row in design:
        # 2. Build one versioned intervention and reject unregistered semantic deltas.
        bundle = materialize_arm(row, spec.base_bundle)
        assert_only_declared_factor_diffs(bundle, row.factor_levels)
        try:
            # 3. Train under the frozen budget and preserve every attempt/checkpoint.
            result = train_complete_pipeline(bundle, budget=spec.budget)
            registry.record_completion(row, result)
        except Exception as failure:
            # 4. A failed run remains an outcome; never replace or silently drop it.
            registry.record_failure(row, failure)

    # 5. Apply the same pre-registered selection rule and paired eval IDs to all cells.
    selected = select_without_test_leakage(registry, spec.selection_rule)
    raw = evaluate_same_pairs(selected, eval_pairs, scorer=spec.scorer_bundle)

    # 6. Estimate cell means, main/interaction effects and hierarchical uncertainty.
    return summarize_factorial(raw, registry, scales=spec.effect_scales)
```

伪代码是验收合同，不代表五项目已经运行该pipeline。

## 17. 五项目 Evidence Mapping

| 项目 | 当前能观察到什么 | 为什么不是matched causal ablation | 最小下一实验 |
| --- | --- | --- | --- |
| UWM / LIBERO | fixed-pruned-init `186/250`为user-confirmed；reset-style `232/250`是另一protocol | init/warmup/distribution变了，不能归因模型；缺checkpoint/raw pairs与training factor cells | 同checkpoint在相同episode IDs上做protocol sensitivity；若测objective需独立action-only/+video arms、同data/budget/selection |
| WAM / Cosmos | 上游action/future/value机制与本地单episode diagnostic | action-only/+world/+value/all只是设计建议，未执行；checkpoint、metric、denominator缺 | 四cells×training seeds×paired sim tasks，先闭合bundle和component/closed-loop/cost表 |
| OpenPiVLA | official-checkpoint diagnostics、formal Qwen causal-CE路径、archive recipes | archived flow-matching metadata与formal causal-CE不是同lineage单factor；97.4 raw/protocol缺 | 冻结同base/data/scorer后逐一测试formatter/objective/recipe，保留formal checkpoint和raw eval |
| Robot Harness | 32B base/SFT/GRPO ladder与project/safety suites | base与ladder的`n`、hidden-embedding/token-overlap scorer及lineage不同 | 同suite/n/scorer的base/SFT/GRPO；再做scope/no-arg/restraint reward factorial |
| OPD | 五expert、coldstart、route KL、synthetic mix与10k raw-holdout summary | 无SFT-only、single-teacher、no-synthetic、ratio/route matched cells；旧final与OPD5000不同run | 先跑base/SFT-only/coldstart-only/full，再对teacher/route/synthetic做预注册factorial |

五项目目前都只能支持机制、组合路线或protocol-bound结果，不能把某个组件写成单因果uplift。本节点不新增项目实验结果或ownership结论。

## 18. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 设计factorial/matched消融协议 | source freeze、design matrix与estimand |
| C1 | 观察到bundle差异 | 可比raw结果，但factor仍可能共变 |
| C2 | frozen protocol内matched factor contrast | 完整cells、multiple runs、paired eval、failure/selection账本 |
| C3 | frozen support内随机化因果effect | consistency/exchangeability/positivity/no-interference与uncertainty闭合 |
| C4 | 跨task/robot/预算可迁移结论 | 新support confirmatory studies、异质性与deployment evidence |

当前五项目未达到C2/C3。本节点保持`WARN`；下一内容节点固定为`VLA-EVAL-019`：checkpoint selection、Pareto frontier与holdout overfit。本切片不生成EVAL-019，也不创建`coaching_state.md`。

## 参考文献（References）

1. NIST/SEMATECH, [Full factorial designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri333.htm)、[Two-level full factorial designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3331.htm)与[Randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。
2. Bouthillier et al., [*Accounting for Variance in Machine Learning Benchmarks*, arXiv:2103.03098v1](https://arxiv.org/abs/2103.03098v1)。
3. Hernán & Robins, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook)，2025-11-21 edition。
4. statsmodels, [`anova.py`@`1bf73ad`](https://github.com/statsmodels/statsmodels/blob/1bf73add5d92f64e48cf2ca143dfeef9811e4eac/statsmodels/stats/anova.py)与[formula API](https://github.com/statsmodels/statsmodels/blob/1bf73add5d92f64e48cf2ca143dfeef9811e4eac/statsmodels/formula/api.py)。
5. [VOL 04 WM-041 Factorial Ablation](../knowledge/vol_04_world_model_sim2real.html)与[独立事实复核](vol_04_batch1_independent_fact_review.html)。
6. [EVAL-004 Paired Evaluation](vol_05_eval004_paired_init_seed_significance_source_freeze.html)、[EVAL-005 Estimand](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006 Versioned Protocol](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-009 Recomputable Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)与[EVAL-011 Causal Boundary](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)。
7. [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
