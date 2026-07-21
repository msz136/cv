# VOL 05 EVAL-011：Offline Metric 与 Online Success 的相关性分析

> 状态：`drafted / VLA-EVAL-011 / knowledge_33_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-003 Success Uncertainty](vol_05_engineering_eval_eval003.html)、[EVAL-005 Aggregation](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)、[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)、[EVAL-010 Release Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)  
> 来源冻结：[EVAL-011 Source Freeze](../sources/vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)  
> 项目边界：五项目均没有多个matched policy/checkpoint的offline×online panel；本页不生成相关性数字。

## 问题（Question）

怎样验证action MSE、world/VLM proxy、sim success或tool score能否筛选online成功的VLA policy？先回答“一个点是谁”，再回答“要线性、排序、预测还是因果”。

## 1. 一句话框架

```text
many frozen policy/checkpoint variants
  × matched task/support/protocol
  -> offline score x_jt + uncertainty
  -> online k_jt / n_jt + uncertainty
  -> Pearson + rank/MMRV + cluster sensitivity
  -> held-out policy-family/task prediction
  -> prospective validation; never replace required online/safety gates
```

一个checkpoint的一对数字不是相关性；同一checkpoint多跑episode只提高它的success估计精度，不增加policy-level variation。

## 2. Panel Schema

```text
policy_id/family/checkpoint_sha/training_seed,
task_id/slice, offline_metric/direction/value/SE,
offline_split/scorer/protocol_sha,
online_success_k/n/env/controller/predicate/protocol_sha,
matched_support, exclusion_reason
```

每行是同一`policy j × task t`的matched pair。不同checkpoint、scorer、task support、init、controller或success predicate必须分层，不能放进同一相关性样本后假装同协议。[1][2]

## 3. 四类 Estimand

| 目标 | 指标/模型 | 回答 | 不回答 |
| --- | --- | --- | --- |
| 线性关联 | Pearson | 两轴是否近似线性共同变化 | 排序一定正确、因果 |
| 单调排序 | Spearman/Kendall | offline是否大体排对policy | 数值校准、margin重要性 |
| margin-aware ranking | MMRV、pairwise sign | 严重mis-rank有多大 | 概率预测、因果 |
| held-out prediction | hierarchical binomial + calibration | 新policy/task成功率能否预测 | 超出validation support的保证 |

## 4. Pearson：一个点是一条 Policy

令`x_j`是越大越好的offline score，`y_j`是matched online success estimate：

\[
r=\frac{\sum_{j=1}^{J}(x_j-\bar x)(y_j-\bar y)}
{\sqrt{\sum_j(x_j-\bar x)^2}\sqrt{\sum_j(y_j-\bar y)^2}}.
\]

变量解释：`J`是policy/checkpoint数；loss要取负或显式转换方向。直觉：Pearson只看线性一致性。实现映射：scatter每点标policy/task、两轴CI与protocol SHA；`J`很小、常数列、窄range或单个outlier时只报系数会误导。

SIMPLER指出Pearson会惩罚正确但非线性的排序，也会在real performance很接近时对小噪声敏感。[1]

## 5. Rank 与 MMRV

\[
\rho_s=\operatorname{Corr}(\operatorname{rank}(x_1,\ldots,x_J),
\operatorname{rank}(y_1,\ldots,y_J)).
\]

变量解释：Spearman回答单调排序；ties交给冻结实现。实现映射：同时输出pairwise ranking matrix和关键candidate的误排，不让一个overall系数隐藏critical reversal。

SIMPLER的MMRV按online margin惩罚误排：

\[
V(i,j)=|y_i-y_j|\,\mathbb{1}[(x_i<x_j)\ne(y_i<y_j)],
\qquad
\operatorname{MMRV}=\frac{1}{J}\sum_i\max_jV(i,j).
\]

变量解释：误排online差距大的两条policy惩罚更重，MMRV越低越好。实现映射：原论文是sim-real policy performance；用于action MSE/VLM proxy是工程推广，必须重新验证并报告online uncertainty。[1][2]

## 6. Online Axis 不是无噪声标签

\[
K_{jt}\sim\operatorname{Binomial}(n_{jt},p_{jt}),
\qquad \hat p_{jt}=K_{jt}/n_{jt}.
\]

变量解释：`K/n`来自冻结success predicate和有效episode分母。实现映射：EVAL-003给每个`p̂`区间，EVAL-009保存raw episode；不知道分母的百分比不能进入panel。offline metric也要保留rows/seeds、reduction和SE。

增加episode能缩小某个点的纵轴误差；要估计跨policy关系，仍需更多独立policy/checkpoint。把episode当policy会产生pseudo-replication。

## 7. Task Hierarchy 与 Simpson's Paradox

可选模型：

\[
K_{jt}\sim\operatorname{Binomial}(n_{jt},p_{jt}),
\qquad
\operatorname{logit}(p_{jt})=\alpha_t+\beta z(x_{jt})+u_j.
\]

变量解释：`α_t`控制task难度，`β`是conditional offline-online关系，`u_j`是policy层残差。实现映射：这是分析设计，不是五项目现有结果；只有policy/task数量足够并预注册时才拟合。

easy task可能同时有高offline和高success，hard task同时低；pooled correlation会很高，即使每个task内proxy无用。必须报告pooled、within-task、per-task与leave-one-task-out。

## 8. Cluster Bootstrap 与 Sensitivity

SciPy的paired bootstrap保持`x/y`配对，但不会自动知道cluster。建议：

1. resample policy/checkpoint或training run；
2. 需要跨task泛化时再重采样task cluster；
3. 同policy episode只用于重估`p_jt`；
4. 每次重算aggregation、Pearson/Spearman/MMRV；
5. 报leave-one-policy/task/family-out和所有原始points。

小`J`时bootstrap也不能制造新policy信息；CI很宽或not estimable是正确结论。

## 9. Held-out 才能证明 Proxy 可筛选

```text
discovery policies/tasks
  -> choose metric, direction, transform, threshold/model
  -> freeze contract
  -> held-out policy-family/task panel
  -> predict candidate before online result is opened
  -> online rollout + append immutable row
```

在同一checkpoint curve尝试很多metric后挑最高相关者，会产生selection optimism。Breck等建议用small-scale online实验验证offline proxy；SIMPLER强调simulation是real eval的补充。[1][3]

用于release时，proxy只作screen；EVAL-010的critical/safety veto与必要canary仍保留。scorer、policy family、task distribution变化后要监控relationship drift并重新validate。

## 10. Correlation ≠ Causation

training step、model size、data scale或family可能同时驱动offline/online。要说“降低loss导致success提升”，需只改变该objective/weight的matched ablation、同data/compute/protocol、多seed与held-out online eval。相关性只能说明association；selection后的best checkpoint还存在winner's curse。

## 11. 五项目边界

### Robot Harness

base/SFT/GRPO有多个suite数字，但n/scorer不同，且没有真实robot/browser online success；高tool与低safety是proxy冲突线索，不是相关性估计。

### OPD

ckpt1000–5000有box/point/text/by-pool曲线，但全是static offline；不同pool最佳点只说明多目标rank风险，没有online axis。

### OpenPiVLA

formal loss/smoke、97.4 archive summary与official-checkpoint diagnostics没有统一lineage/per-checkpoint rows；不能拼成panel。

### WAM

offline target fit在manifest中明确missing；base/trained只有一个CoffeePressButton失败episode且checkpoint未核。`J<=2`且两轴不完整，不能说相关或不相关。

### UWM

一个user-confirmed `186/250`没有多个matched policy offline score；reset `232/250`改变了protocol，不是第二条policy观测。

## 12. Artifact 与伪代码

```text
offline_online_panel/
  panel_manifest.json
  offline/raw_and_summary/
  online/episode_bundle/
  analysis/paired_panel.parquet
  analysis/correlation.json
  analysis/heldout_predictions.jsonl
  figures/scatter_facets.svg
  checksums/manifest-sha256.txt
```

```python
def validate_proxy(panel, spec):
    # Validate identity, direction, common support and protocol before statistics.
    rows = validate_matched_policy_task_rows(panel, spec)

    # Aggregate episodes within policy-task; do not turn them into new policies.
    points = aggregate_offline_and_online(rows, by=["policy_id", "task_id"])

    # Compute complementary linear, rank and margin-aware summaries.
    stats = compute_pearson_spearman_kendall_mmrv(points)

    # Resample policy/task clusters and inspect leave-one-cluster sensitivity.
    stats["intervals"] = cluster_bootstrap(points, spec)
    stats["sensitivity"] = leave_one_cluster_out(points)

    # Fit on discovery and evaluate frozen predictions on held-out families/tasks.
    model = fit_hierarchical_binomial(points.discovery, spec)
    stats["heldout"] = score_heldout(model, points.validation)
    return write_immutable_bundle(stats, spec)
```

伪代码是analysis contract，不是本地已有工具。

## 13. 面试防线与下一入口

- 单个checkpoint不能谈相关性；
- episode数不等于policy数；
- Pearson高不等于rank、calibration或causation都好；
- pooled task correlation可能是难度confounding；
- proxy在被优化、scorer或distribution变化后要重新验证；
- 五项目当前只能讲补证据设计，不能报告`r/ρ/MMRV/β`。

EVAL-011知识与一张题卡保持`WARN/unseen`。下一节点是`VLA-EVAL-012`：OOD、扰动、遮挡、视角与鲁棒性矩阵。没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. Li et al., [*Evaluating Real-World Robot Manipulation Policies in Simulation*](https://arxiv.org/abs/2405.05941v1), 2024。
2. `simpler-env/SimplerEnv` [frozen metrics implementation](https://github.com/simpler-env/SimplerEnv/blob/06accaca93535902d408da4855f21cece12bceb7/simpler_env/utils/metrics.py)，MIT。
3. Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/), 2017。
4. SciPy `v1.16.3`, [`pearsonr/spearmanr/kendalltau`](https://github.com/scipy/scipy/blob/v1.16.3/scipy/stats/_stats_py.py)与[`bootstrap`](https://github.com/scipy/scipy/blob/v1.16.3/scipy/stats/_resampling.py)。
5. [EVAL-011 Source Freeze](../sources/vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)。
6. [WM-019 Metric Boundary](../sources/vol_04_wm019_metric_boundary_source_freeze.html)与[VOL 04 WM-040/041](vol_04_world_model_sim2real.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
