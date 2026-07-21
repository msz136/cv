# VOL 05 EVAL-011 Source Freeze：Offline Metric 与 Online Success 的相关性分析

> 状态：`source_frozen / VLA-EVAL-011 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结matched policy-task panel、Pearson/Spearman/MMRV、层次二项映射、cluster uncertainty、held-out validation、proxy selection与因果边界；只生成一张`VLA-EVAL-011`原子题卡，VOL 05同步为knowledge/cards 33/44。

## 问题（Question）

action MSE、VLM/world-model proxy、simulator success或tool-call score能否预测真实closed-loop success？可信回答不能从一对数字或几千个episode计算“相关性”，而要把多个policy/checkpoint作为独立变异来源，在同task/protocol上得到matched offline-online panel，再区分线性关联、排序能力、预测校准与因果作用。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Li et al., *Evaluating Real-World Robot Manipulation Policies in Simulation*（SIMPLER） | primary paper；arXiv `2405.05941v1`，2024-05-09；论文许可未断言 | arXiv API `a20cd969be3c4a310fbdc719d695873d0f541501eb8b023ee5bf6b9ea5baa79d`；ar5iv HTML `19db19183e0c55e2d41358fc8f290d2d6326ad86ef62ecae8c17ae5b8521e97d` | multiple policies上的paired sim-and-real performance；Pearson局限；MMRV定义；relative ranking与distribution-shift behavior；simulation不完全替代real eval | 任意offline metric都与online success相关；论文结果自动迁移到用户项目 |
| S2 | `simpler-env/SimplerEnv` | official-code；commit `06accaca93535902d408da4855f21cece12bceb7`（2025-12-20）；MIT | README `81aaa39d59e41c6b60d6ccdf09c17b1f0ca284ce7cb780b62b908afac6c0dc28`；metrics `ee8596be6997d41295bf5b25f90c9b5b3ba47ef2bd92296b8c45e7ffc5606dc6`；calc `c95963ec1452cb4f5f34db012eda79542c8afdd0465299ae30cf710c4b4a0521`；LICENSE `c28645822e5cdadf816144773ee153332449ae04aa6f0b6a6393e5611092f878` | `REAL_PERF/SIMPLER_PERF`的policy-task对齐、Pearson与MMRV实现 | 统计CI、cluster bootstrap、用户项目运行或real-robot evidence |
| S3 | Breck et al., *The ML Test Score* | primary paper；IEEE Big Data 2017；Google Research页面/PDF；论文许可未断言 | page `e1588aa27c4a0aa74435327e92400443faf0b1ddf623068845571346484e1f6b`；PDF `8db5862dc7c7aaa2c55bb43bd42fc55531a0503782b7026b5811c00c98befd31` | offline proxy与online impact需要建立关系；可用small-scale A/B与故意降级模型测量；重要slice单独看 | correlation阈值、VLA metric choice或因果保证 |
| S4 | SciPy `stats` | official-code；tag `v1.16.3`（tag object `56e567e70ccad213d04ab04e7cfe7365562a71f1`）；BSD-3 | `_stats_py.py` `c1f98867bce4a0bdb336b6c33bd930bcf50f8b9aae6a654e1f9a6d2064bda3b4`；`_resampling.py` `ad8335279281c69d4a3bbf4449100e3ac5e1f5bc7af360963133973ed2a64d7e`；LICENSE `221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94` | `pearsonr`、`spearmanr`、`kendalltau`、paired bootstrap的实现入口 | 自动选择统计单元、解决task/policy clustering或证明proxy有效 |
| S5 | EVAL-003/005/006/007/009/010、WM-019与VOL 04 WM-040/041 | canonical local prerequisites | EVAL-003 `3d00ba8a...4d490f`；EVAL-005 `16b6a4c7...804ff46`；EVAL-006 `8a2ccfbc...ccd054`；EVAL-007 `66800fd2...6e278`；EVAL-009 `be6945d...13dea`；EVAL-010 `512d9e16...b2911`；WM-019 `2cff5c30...b08a5`；VOL 04 `89a3a5ed...8effe` | success uncertainty、aggregation/protocol/coverage、raw bundle、release gate与metric ladder | 五项目已有matched correlation study |
| S6 | 五项目inventories + WAM manifest | local-evidence | Robot Harness `66acc52c...aa291e`；OPD `0a68251d...db12bb`；OpenPiVLA `a3c644f9...ce293`；WAM `078c86b1...772d`；UWM `728b8326...3674d`；WAM manifest `1ab87092...8f697` | 当前offline/online artifact和缺口 | 项目相关性、因果或real-robot claim |

S1把policy作为圆点/比较对象，目标是simulation与real对relative policy performance的排序一致，而非逐episode相关。S4只提供统计实现；本页的层次模型、cluster resampling与held-out design是source-consistent engineering synthesis，不冒充SIMPLER或SciPy的原结论。

## 2. 先定义“相关性的一个点”

### 2.1 正确 panel

```text
policy_variant_id, policy_family, checkpoint_sha, training_seed,
task_id, task_slice, offline_metric_name/value/uncertainty,
offline_split/scorer/protocol_sha,
online_success_k/n, online_env/controller/predicate/protocol_sha,
matched_support, exclusion_reason
```

设policy/checkpoint为`j=1..J`、task/slice为`t=1..T`。一个panel row是同一`(j,t)`在冻结offline与online协议上的一对结果。必须有多个真实不同的`j`；episode只是估计某个`p_{jt}`的重复观测，不会把`J=1`变成有相关性样本。

### 2.2 三种错误“扩样本”

1. 把同一个policy的1000个offline rows与50个online episodes逐行拼接；两侧没有一一对应单位。
2. 把task×checkpoint所有格子当独立点；同policy和同task重复出现，标准误会过小。
3. 把不同scorer、init、controller或success predicate的summary放到同一散点图；protocol effect被误当metric关系。

## 3. 四个问题不是一个“相关系数”

| 目标 | 问题 | 合适输出 | 不足 |
| --- | --- | --- | --- |
| linear association | offline每变化一单位，online是否近似线性变化 | Pearson + scatter/residual + CI | 对非线性、窄range、outlier敏感 |
| ranking | proxy能否把候选排对 | Spearman/Kendall、pairwise sign、MMRV | 不代表数值校准或绝对success |
| prediction | 能否预测新policy/task的online success | held-out hierarchical model、log loss/Brier/calibration | 需要足够policy/task support |
| causal effect | 优化offline metric是否导致online提升 | matched intervention/ablation | correlation本身不回答 |

“相关性高”“排序可用”“概率校准”“改metric能提升success”必须使用不同措辞。

## 4. Pearson：线性一致性与范围限制

令`x_j`为方向统一成越大越好的offline score，`y_j`为同policy的online success estimate：

\[
r=\frac{\sum_{j=1}^{J}(x_j-\bar x)(y_j-\bar y)}
{\sqrt{\sum_j(x_j-\bar x)^2}\sqrt{\sum_j(y_j-\bar y)^2}}.
\]

变量解释：一个`j`是一条policy/checkpoint，不是episode；loss需取负号或明确方向。直觉：`r`只衡量线性共同变化。实现映射：保存scatter、每点policy/task身份、protocol SHA与两轴CI；常数输入、很小`J`、极端点或窄performance range时不报告孤立`r`。

SIMPLER明确指出Pearson可能惩罚正确但非线性的排序，也会在real policy性能很接近时被小噪声大幅影响。[S1]

## 5. Spearman / Kendall 与 MMRV

Spearman可写为rank后的Pearson：

\[
\rho_s=\operatorname{Corr}(\operatorname{rank}(x_1,\ldots,x_J),
\operatorname{rank}(y_1,\ldots,y_J)).
\]

变量解释：`ρ_s`回答单调排序，不要求数值线性；ties由冻结实现处理。实现映射：同时报告pairwise排序表，避免一个系数隐藏哪个关键candidate被排反。

SIMPLER提出Mean Maximum Rank Violation（MMRV），让排错的重要性由real performance margin加权：

\[
V(i,j)=|y_i-y_j|\,\mathbb{1}[(x_i<x_j)\ne(y_i<y_j)],
\qquad
\operatorname{MMRV}=\frac{1}{J}\sum_{i=1}^{J}\max_j V(i,j).
\]

变量解释：若proxy把`i/j`顺序排反，`V`等于两者online差距；MMRV越低越好。实现映射：SIMPLER原式用于sim/real policy performance；推广到任意offline proxy是本文设计，前提是两轴同policy、同task support且`y`方向一致。MMRV仍受online estimate噪声影响，必须带uncertainty或敏感性分析。

## 6. Online Success 有测量误差

对policy `j`、task `t`，online success不是无噪声实数：

\[
K_{jt}\sim\operatorname{Binomial}(n_{jt},p_{jt}),
\qquad \hat p_{jt}=K_{jt}/n_{jt}.
\]

变量解释：`K/n`来自冻结success predicate和有效episode denominator；`p`是该协议下潜在成功概率。实现映射：EVAL-003的Wilson/exact interval与EVAL-009 raw episode bundle给每个online点提供uncertainty；未知`n`的97.4不能进入定量panel。

若offline metric本身来自有限rows/seeds，也要保存其SE/CI。忽略两轴measurement error通常会让关系不稳定或产生attenuation；增加每policy episode能缩小`p_j`误差，却不能替代更多policy variants。

## 7. Task / Policy Hierarchy 与 Simpson 风险

一个可选的解释/预测模型是：

\[
K_{jt}\sim\operatorname{Binomial}(n_{jt},p_{jt}),
\qquad
\operatorname{logit}(p_{jt})=\alpha_t+\beta z(x_{jt})+u_j.
\]

变量解释：`α_t`控制task难度，`β`描述标准化offline score与online log-odds的条件关系，`u_j`表示policy层残差。实现映射：只有在`J/T`足够、设计预注册时才拟合；按policy family/task做held-out验证。该式是engineering synthesis，不是五项目已运行模型。

把easy task的高offline/high success与hard task的低offline/low success混在一起，可能得到很高pooled correlation，即使每个task内proxy完全无用；因此至少同时报告pooled、within-task、per-task与leave-one-task-out结果。

## 8. Uncertainty：在正确层级重采样

SciPy `bootstrap(..., paired=True)`可保持两轴配对，但`paired=True`不会自动识别policy/task cluster。VLA panel建议：

1. primary resampling unit取policy/checkpoint或training run；
2. 若目标是跨task泛化，再按task cluster分层/双层重采样；
3. 同一policy内部episode用于重新估计`p_{jt}`，不能冒充独立policy；
4. 每次bootstrap同时重算aggregation、rank、Pearson/Spearman/MMRV；
5. 小`J`时展示所有points与leave-one-policy-out sensitivity，不用窄CI制造精确感。

没有跨policy variation或存在常数列时，相关系数不可识别；输出`not estimable`比填0更正确。

## 9. Discovery、Validation 与 Prospective Gate

```text
discovery panel
  -> choose metric/direction/transform/model
  -> freeze proxy contract and decision rule
  -> held-out policy-family/task validation panel
  -> prospective candidate prediction
  -> online rollout reveals outcome
  -> append immutable row; monitor relationship drift
```

若在同一checkpoint曲线上试很多metric，最后挑相关性最高者并仍在同数据报告，结果存在selection optimism。Breck等建议用small-scale online experiment验证offline proxy；SIMPLER也强调simulation是real evaluation的补充而非完全替代。[S1][S3]

用于EVAL-010 release gate时，offline proxy只能作screen：先在独立历史panel上证明对目标候选分布有排序/预测价值，再冻结阈值；critical/safety hard gate和必要online canary仍保留。

## 10. Correlation 不等于 Causation

多个checkpoint的loss与success共同改善，可能由training step、model size、data amount或policy family共同驱动。要说“降低action MSE导致success提升”，至少需要：

- 预注册只改变该目标/权重的matched ablation；
- 同data/compute/protocol与多个training seeds；
- offline和online都在held-out common support评估；
- 检查mediator、side effect和critical slice；
- 报effect/uncertainty，不只报跨arm correlation。

对已用offline metric选择的best checkpoint再估计相关性还会产生winner's curse；selection set与validation set必须分开。

## 11. 五项目 Evidence Mapping

| 项目 | offline候选 | online候选 | 当前panel判定 | 安全表述 |
| --- | --- | --- | --- | --- |
| Robot Harness | tool/coverage/argument/safety/browser suite | 无真实robot/browser closed-loop success | `MISSING`；base/SFT/GRPO的n/scorer也不同 | 可讲proxy冲突与未来panel设计；不能报tool→robot相关性 |
| OPD | ckpt1000–5000 box/point/text/by-pool | 无matched robot/simulator closed-loop | `OFFLINE ONLY` | 不同pool最佳点说明多目标rank风险，不是offline-online correlation |
| OpenPiVLA | formal loss/smoke/diagnostic线索 | 97.4 archive simulator summary与official-checkpoint diagnostics不同lineage | `UNMATCHED` | 先闭合per-checkpoint offline+LIBERO raw rows；当前不能拟合关系 |
| WAM | manifest明确offline target fit缺失 | base/trained各一个CoffeePressButton失败episode，checkpoint未核 | `J<=2 / MISSING` | 两条失败trace只作diagnostic；不能说MSE/proxy与success脱钩或相关 |
| UWM | training loss/DataLoader等材料，不是统一policy-quality metric | 一个user-confirmed 186/250；reset 232/250是protocol变化 | `SINGLE POLICY / CONFOUNDED` | strict/reset说明protocol sensitivity，不是policy correlation |

五项目目前都不能计算可信`r/ρ/MMRV/β`。本页提供的是补证据合同，不是新增项目结果。

## 12. 最小 Artifact Bundle

```text
offline_online_panel/
  panel_manifest.json        # policies, tasks, metrics, directions, exclusions
  offline/raw_and_summary/   # metric rows + scorer/protocol SHA
  online/episode_bundle/     # EVAL-009 raw episodes + k/n/CI
  analysis/paired_panel.parquet
  analysis/correlation.json  # r/rho/MMRV + interval/sensitivity
  analysis/heldout_predictions.jsonl
  figures/scatter_facets.svg
  checksums/manifest-sha256.txt
```

## 13. 分析伪代码

```python
def validate_offline_online_proxy(panel, spec):
    # 1. Validate one matched row per policy-task and freeze metric direction.
    rows = validate_ids_protocols_common_support(panel, spec)

    # 2. Keep policies as the primary variation unit; episodes estimate p_jt only.
    points = aggregate_raw_rows_and_episodes(rows, by=["policy_id", "task_id"])

    # 3. Report linear, rank and margin-weighted ranking views together.
    stats = compute_pearson_spearman_kendall_mmrv(points)

    # 4. Resample policy/task clusters, then run leave-one-policy/task sensitivity.
    stats["intervals"] = hierarchical_cluster_bootstrap(points, spec)
    stats["sensitivity"] = leave_one_cluster_out(points)

    # 5. Fit only on discovery rows and score frozen predictions on held-out families/tasks.
    predictor = fit_hierarchical_binomial(points.discovery, spec)
    stats["heldout"] = evaluate_predictions(predictor, points.validation)
    return write_immutable_analysis_bundle(stats, spec)
```

这是analysis contract，不是五项目已有脚本。

## 14. Source Gate 结论与下一入口

EVAL-011保持`WARN`：SIMPLER提供了多policy paired sim-real、Pearson/MMRV及“proxy不替代real”的一手案例；SciPy冻结了实现入口；ML Test Score支持offline-online关系需要实证验证。本页进一步冻结统计单元、层次结构、uncertainty、held-out与因果边界。五项目均没有可估计相关性的matched panel。

下一节点固定为`VLA-EVAL-012`：OOD、扰动、遮挡、视角与鲁棒性矩阵。真实口述前不创建`coaching_state.md`。

## References

1. Li et al., [*Evaluating Real-World Robot Manipulation Policies in Simulation*](https://arxiv.org/abs/2405.05941v1), 2024；[ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2405.05941)。
2. `simpler-env/SimplerEnv` commit [`06accaca`](https://github.com/simpler-env/SimplerEnv/tree/06accaca93535902d408da4855f21cece12bceb7)，[metrics.py](https://github.com/simpler-env/SimplerEnv/blob/06accaca93535902d408da4855f21cece12bceb7/simpler_env/utils/metrics.py)，MIT。
3. Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/), IEEE Big Data 2017。
4. SciPy `v1.16.3`, [`_stats_py.py`](https://github.com/scipy/scipy/blob/v1.16.3/scipy/stats/_stats_py.py)与[`_resampling.py`](https://github.com/scipy/scipy/blob/v1.16.3/scipy/stats/_resampling.py)，BSD-3。
5. [EVAL-003](vol_05_eval003_success_rate_confidence_interval_source_freeze.html)、[EVAL-005](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-007](vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)、[EVAL-009](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)。
6. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)与[VOL 04 WM-040/041](../knowledge/vol_04_world_model_sim2real.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
