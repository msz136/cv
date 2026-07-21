# VOL 05 EVAL-005 Source Freeze：Macro / Micro / Per-task / Weighted Aggregation

> 状态：`source_frozen / VLA-EVAL-005 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片只冻结 aggregation estimand、task/run hierarchy、macro/micro/weighted 公式、stratified uncertainty、missing-task 与项目指标边界；下游只生成一张 `VLA-EVAL-005` 原子题卡，VOL 05 同步为 knowledge/cards 27/44。

## 问题（Question）

VLA 在多个 task、suite、initialization 和 training seed 上评估时，“平均成功率”不是唯一对象。必须先回答：目标总体是什么、每个 task/suite 的权重是什么、task 是固定清单还是从更大总体抽样、多个 training run 如何进入统计、缺失 task 和无效 episode 怎样处理。macro、micro、weighted 只是不同 estimand 的实现，不能在看完结果后挑最亮眼的一种。

本 source gate 固定以下链路：

```text
target population / decision
  -> task-suite hierarchy + fixed weight vector
  -> per-task k_t / n_t and coverage
  -> macro / micro / weighted aggregate
  -> run/task/init-aware uncertainty
  -> per-task table + aggregate label + exclusions
```

## 1. 冻结来源、revision 与许可

公开 blob hash 对 2026-07-18 重新取得的 UTF-8 原文计算。公式是本节点对 estimand 的显式定义；官方代码和论文支持实现与报告边界，但不证明任何本地项目数据完整或可比。

| ID | 来源 | 类型 / revision | 固定入口 | SHA-256 | 支持范围 |
| --- | --- | --- | --- | --- | --- |
| S1 | Agarwal et al., *Deep RL at the Edge of the Statistical Precipice* | primary / arXiv `2108.13264` | [arXiv](https://arxiv.org/abs/2108.13264) | response `74f11076d64de0f6beb9da4a9b185dd2a42465bfde6426fb2004fd6fd9e042ac` | 多 task / 多 run 下点估计、区间、robust aggregate 与 performance profile 的报告边界 |
| S2 | `google-research/rliable` | official-code / commit `3ccd9f4dea577a04d3d2b557f259aac08badbd81`, Apache-2.0 | [repository](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81) | README `c4d474f8a018c6faf8ab5d365bad135258a2af851e2a5672e07999438fcc6237`; library `0af084e4040fad3ae02a612b16fbcc59d9a141ac8259ad47dc1932bcc168ac14`; metrics `caf0c74e6238a12d2f59d6bcd47115e56167ea73c3b851c3f7981de17e5230cc`; LICENSE `43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1` | `num_runs × num_tasks` score matrix、equal-task aggregate mean、IQM/median、run/task stratified bootstrap 语义 |
| S3 | LIBERO `metric.py` | official-code / `Lifelong-Robot-Learning/LIBERO@8f1084e3132a39270c3a13ebe37270a43ece2a01`, MIT | [metric.py](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/lifelong/metric.py) | `4fe37407f23cd9c1ceb4c93670f308d2fed6d34b2c2139d86123702c849cabcb` | 单 task 成功率 `num_success/n_eval` 与跨 task success vector；不替下游决定唯一 aggregate |
| S4 | LIBERO eval config / LICENSE | official-code / same commit | [eval config](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/configs/eval/default.yaml) | config `e9775e56a15317666ee8248f7e9d59072b9469c0f7346dc3ed496484657c6bcd`; LICENSE `e2885fd30a08381b799c4a33385522b23d637b4051b8f9a7f9f2519944b68ff6` | frozen default `n_eval` 与代码许可；不证明其他论文/项目使用同一分母 |
| S5 | OpenPI LIBERO README | official-code/doc / `Physical-Intelligence/openpi@15a9616a00943ada6c20a0f158e3adb39df2ccac`, Apache-2.0 | [README](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/README.md) | `a2caaf5459c4b01837b73aa93a6f69e8cdf10385b39c34eba36afa85f83fafe9` | official π0.5 四 suite rows 98.8/98.2/98.0/92.4 与 equal-suite average 96.85 |
| S6 | UWM paper / benchmark source audit | primary + canonical local audit / arXiv `2504.02792v3` | [Table II](https://arxiv.org/html/2504.02792v3#S4.T2) / [local audit](vol_04_benchmark_evidence_claim_to_protocol.html) | local canonical `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a` | 五 task、50 OOD init、3 finetune seeds 与 protocol non-comparability；不证明本地 74.4 可复算 |
| S7 | Simpson (1951), interaction in contingency tables | primary / DOI | [DOI](https://doi.org/10.1111/j.2517-6161.1951.tb00088.x) | DOI 指纹 | 不同分层权重可能造成 aggregate association/ranking reversal |
| S8 | EVAL-003 / EVAL-004 | canonical local source freezes | [CI/artifact gate](vol_05_eval003_local_statistical_artifact_gate.html) / [paired significance](vol_05_eval004_paired_init_seed_significance_source_freeze.html) | artifact gate `4f28ebe5c2e2acdb47963bb71189123bcbcd6de7f7bb3ccb87e7a6843d3d63f4`; EVAL-004 `c89c052a630692a12a20235fa6d53278f43e4509c6e567110f81f7c2eb427313` | episode denominator、cluster、paired difference、training-seed 与 invalid-pair 前置合同 |

`rliable.aggregate_mean` 对完整 `runs × tasks` 矩阵先对 run 求每 task mean，再对 task 等权求 mean；`aggregate_iqm` 则对 run-task entries 做 25% trimmed mean。二者是不同 estimand，不能把 IQM 改名为 macro average。`StratifiedBootstrap(task_bootstrap=False)` 对固定 task set 的 run uncertainty；`task_bootstrap=True` 还对 task 重采样，面向更大未知 task population 的敏感性。

## 2. 先冻结 estimand：平均的是谁

设共有 `T` 个 task，第 `t` 个 task 有 `n_t` 个有效 episode，成功数 `k_t`，条件成功率：

\[
\hat p_t=\frac{k_t}{n_t},\qquad t=1,\ldots,T.
\]

变量解释：`p_t` 只属于同一 checkpoint、protocol、task definition 和 episode-validity rule。实现映射是 per-task summary 的 `task_id/k/n/rate`；不同 scorer、metric type、suite version 或 controller 的结果不能只因都落在 `[0,1]` 就合并。

聚合前写出一句 estimand，例如：

```text
在固定的五个 task 上，每个 task 等权、先对 training seeds 求均值的成功率。
```

或：

```text
按部署流量预注册权重，对 task-conditional success 做期望。
```

这两句对应不同总体和不同决策，数值不可互换。

## 3. Per-task、macro、micro 与 weighted 的精确定义

### 3.1 Per-task vector

\[
\hat{\mathbf p}=(\hat p_1,\ldots,\hat p_T).
\]

per-task 不是“还没聚合完的中间结果”，而是定位失败、检查 coverage 和发现 tail task 的必报主结果。任何 scalar aggregate 都应能回链到这张表。

### 3.2 Macro：task 等权

\[
\hat p_{\mathrm{macro}}=\frac{1}{T}\sum_{t=1}^{T}\hat p_t.
\]

变量解释：每个 task 权重都是 `1/T`，不管该 task 跑 10 还是 100 episode。它回答“从这 T 个 task 均匀抽一个 task，再按其条件分布执行”的平均表现。task taxonomy 粒度会改变 macro：把一个 task 拆成五个近似 task 会让它获得五倍权重。

### 3.3 Micro：episode count 加权

\[
\hat p_{\mathrm{micro}}=\frac{\sum_t k_t}{\sum_t n_t}
=\sum_{t=1}^{T}\frac{n_t}{\sum_j n_j}\hat p_t.
\]

变量解释：micro 的隐含权重是观测分母占比。只有当 episode allocation 就代表目标部署 mixture，或明确只描述这批 pooled episodes 时，才可把它解释为目标总体表现。如果某个难 task 为了提高精度而多跑了 episode，micro 会把“实验预算”误当“业务权重”。

### 3.4 Weighted：外部固定权重

\[
\hat p_w=\sum_{t=1}^{T}w_t\hat p_t,
\qquad w_t\ge 0,\quad \sum_t w_t=1.
\]

变量解释：`w_t` 应来自预注册的部署频率、风险/业务优先级或 benchmark contract，而不是从模型表现反推。若 safety-critical task 是 hard gate，通常不应靠小权重把其失败平均掉；需同时报告 constraint/gate。

macro 是 `w_t=1/T` 的 weighted 特例，micro 是 `w_t=n_t/sum n` 的 weighted 特例。名字不是重点，权重向量才是可审计对象。

## 4. 何时 macro = micro，何时会反转

若所有 task 的 `n_t=n_0`，则：

\[
\hat p_{\mathrm{micro}}
=\frac{n_0\sum_t\hat p_t}{Tn_0}
=\hat p_{\mathrm{macro}}.
\]

变量解释：两者数值相等只因为权重相等，不代表 estimand 语义相同。下一版若某 task 缺 10 个 episode，micro 权重就改变，而 macro 仍等 task。

### 4.1 不同权重可制造 ranking reversal

示例中 A 在 easy/hard 两个 task 都更高，但两模型的 episode allocation 不同：

| model | easy | hard | macro | micro |
| --- | --- | --- | ---: | ---: |
| A | 9/10 = 0.90 | 60/100 = 0.60 | 0.75 | 69/110 = 0.627 |
| B | 80/100 = 0.80 | 5/10 = 0.50 | 0.65 | 85/110 = 0.773 |

如果直接比各自 micro，B 看起来更高，尽管 A 在两个 task 都占优。原因不是模型行为悖论，而是比较时用了两套不同 task weights。A/B comparison 必须在共同 task set 和同一权重向量上重算；paired 数据还要沿用 EVAL-004 的 pair 内差值。

## 5. Suite → task → init → run 的层级

多 suite 时，`average of suite averages` 隐含 suite 等权；`average of all tasks` 隐含 task 等权；`pool all episodes` 隐含 episode 等权。三者只有在 suite task 数和 episode 数都平衡时才相等。

推荐显式写：

\[
w_{s,t}=w_s\,w_{t\mid s},\qquad
\sum_s w_s=1,\quad \sum_{t\in s}w_{t\mid s}=1.
\]

变量解释：`w_s` 是 suite 权重，`w_{t|s}` 是 suite 内 task 权重。实现必须保存 suite/task registry，不能只存最后一个 `average` 字段。

training seed 是更高层 replicate。若结论指向训练方法，先对每个 `(training_seed, task)` 得到 score matrix，再定义“先 seed 后 task”或联合 robust aggregate。把同一 checkpoint 的数百 episodes 平铺，会夸大 training-run 证据。

## 6. 固定 task set 与 task population 的区间

### 6.1 固定 benchmark tasks

问题是“在这 T 个固定 task 上，换一组 training/rollout runs 会怎样”。应保持 task strata，重采样 run/seed 或 task 内 cluster，然后用同一权重向量重算 aggregate。`rliable` 的 `task_bootstrap=False` 对应固定 task set 下的 run uncertainty。

### 6.2 更大未知 task population

问题是“这些 task 若来自更大 task population，换 task 会怎样”。可在假设 task 可交换且抽样机制可解释时重采样 task；`rliable task_bootstrap=True` 同时对 task 重采样。但 benchmark 的 hand-picked tasks 往往不是随机样本，task-bootstrap interval 不能自动升级成真实部署泛化保证。

### 6.3 权重与 cluster

- task 内 episode/init 相关：按 init/scene cluster 重采样；
- 多 training seed：先在顶层 resample seed/run；
- deployment weights 来自有限流量：说明把权重视为 fixed 还是一并估计不确定性；
- per-task 与 aggregate CI 同时报；naive pooled binomial CI 不能表达 task heterogeneity。

## 7. Missing task、invalid episode 与 coverage

聚合规则必须在结果前冻结：

| 情况 | 错误做法 | 安全合同 |
| --- | --- | --- |
| 一个模型缺整个 task | 各自平均 available tasks | 对共同预注册 task set fail closed，或按预注册 failure/missing 规则并报告 coverage |
| task 内单臂 crash | 从该模型分母删除 | 沿用 EVAL-004 invalid-pair rule；报告 attempted/valid/excluded |
| 不同 task 跑不同 n | 默认叫 overall success | 同时报 n_t，明确 micro 权重是否符合 target mixture |
| task version/scorer 不同 | 只按名字 join | 使用 versioned task/scorer/protocol hash |
| suite 新增 task | 直接和旧 aggregate 比 | 在旧共同 registry 重算，再单独报告新增 coverage |

不能把 missing task 的权重重新归一化后静默比较，因为这会让弱模型避开难 task。至少报告 planned/attempted/valid task count、episode count、missingness reason 和 weight coverage `sum_{observed} w_t`。

## 8. 比较模型时先固定共同支持集

对 A/B 的 task-level paired effect：

\[
\hat\Delta_w=\sum_{t=1}^{T}w_t(\hat p_{A,t}-\hat p_{B,t}).
\]

变量解释：A/B 使用同一 `w_t` 和同一 task registry。更强的 paired init/seed 设计应先在每个 pair 上算 `A-B`，再按 task/seed hierarchy 聚合；不能让 A 的 micro weights 和 B 的 micro weights不同。显著性、multiplicity 与 holdout 沿用 EVAL-004。

## 9. Robust aggregates 是补充，不是改名

`rliable` 还提供 median、IQM、optimality gap 和 performance profile。它们有助于展示少量 run/task、outlier 和跨 task 分布，但不能替代：

- per-task `k/n` 与 failure table；
- 明确 macro/micro/deployment weights；
- safety-critical task gate；
- protocol 和 metric compatibility。

特别是 `aggregate_iqm` 在 frozen code 中对 run-task entries 做 25% trimmed mean，和“每 task 等权的 mean success”不是同一个量。报告中应写全名、输入矩阵 shape、normalization 和 CI method，不只写 `average`。

## 10. 项目真实性边界

### 10.1 UWM

user-confirmed final table 为 `0.88/0.80/0.76/0.66/0.62`，每 task 50 次，因此：

\[
\hat p_{macro}=\frac{0.88+0.80+0.76+0.66+0.62}{5}=0.744,
\qquad
\hat p_{micro}=\frac{186}{250}=0.744.
\]

这是现有 summary 的算术一致性检查，不是 raw verification。inventory 还保留较早 `book_caddy=42/50` report，而 final summary 是 `44/50`；不能跨版本拼表。`232/250` reset-style 属于不同 protocol，也不能和 fixed-pruned-init 放在同一个 aggregate comparison。

### 10.2 OpenPiVLA

archive table 的四 suite rows `0.98/0.995/0.99/0.93` 做 equal-suite macro 得 `0.97375`，按一位百分数显示为 `97.4%`；official OpenPI `98.8/98.2/98.0/92.4` 的 equal-suite macro 是 `96.85%`。这只验证表内 arithmetic。archive 仍缺 suite/task/trial/seed/init 分母、raw episodes 和 checkpoint lineage，因此不能恢复 per-task/micro/CI，也不能称 0.55pp uplift。

### 10.3 OPD

10k raw-holdout 是 `box 6100 / point 1400 / text 2500`，对应 IoU/Acc、Hit@50/100、text exact 等不同 metric。不能用 row-count micro 把它们压成“总准确率”；应先 by-format/by-pool 报告，并在同一 metric 内按预注册 pool weights 聚合。8,251 unique images、重复 image/path cluster 还要求 cluster-aware uncertainty。

## 11. 最小 summary schema 与伪代码

最低 task row：

```text
run_id, training_seed, suite_id, task_id, task_revision,
protocol_hash, scorer_hash, planned_n, attempted_n, valid_n,
success_k, rate, exclusion_counts, weight_macro,
weight_micro, weight_deployment
```

聚合伪代码：

```python
def aggregate_task_success(rows, target_weights):
    # 1. Fail closed on version/protocol mismatch and missing planned tasks.
    validate_common_registry(rows)
    per_task = summarize_k_n_by_task(rows)

    # 2. Keep all named estimands; never return an unlabeled "average".
    macro = mean([x.k / x.n for x in per_task])
    micro = sum(x.k for x in per_task) / sum(x.n for x in per_task)
    weighted = sum(target_weights[x.task_id] * (x.k / x.n)
                   for x in per_task)

    # 3. Resample the declared top-level unit and recompute fixed weights.
    intervals = stratified_cluster_bootstrap(
        rows, statistics=["macro", "micro", "weighted"],
        fixed_weights=target_weights,
    )
    return {"per_task": per_task, "macro": macro, "micro": micro,
            "weighted": weighted, "intervals": intervals}
```

该伪代码是 artifact contract，不是当前项目已实现的统一 scorer。真实实现还需明确 task fixed/random、training-seed 层级、paired comparison、missingness 和 resampling seed。

## 12. Source Gate 结论与下一入口

EVAL-005 保持 `WARN`：aggregation estimand、公式、官方 benchmark vector、rliable run/task uncertainty 与三个项目的 arithmetic/evidence boundary 已冻结；本地仍没有统一 raw episode bundle、跨项目共同 metric 或 deployment weight manifest，因此不产生新的综合成绩。

下一内容节点固定为 `VLA-EVAL-006`：benchmark / environment / controller / scorer versioning。题卡保持 `unseen`，真实口述前不创建 `coaching_state.md`。

## References

1. Agarwal et al., [*Deep RL at the Edge of the Statistical Precipice*](https://arxiv.org/abs/2108.13264)。
2. Google Research, [`rliable@3ccd9f4`](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81)。
3. LIBERO frozen [`metric.py`](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/lifelong/metric.py)。
4. OpenPI frozen [LIBERO README](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/README.md)。
5. Simpson, “The Interpretation of Interaction in Contingency Tables,” [DOI](https://doi.org/10.1111/j.2517-6161.1951.tb00088.x)。
6. [Benchmark / Evidence Source Audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
7. [EVAL-003 Local Statistical Artifact Gate](vol_05_eval003_local_statistical_artifact_gate.html) 与 [EVAL-004 Paired Significance](vol_05_eval004_paired_init_seed_significance_source_freeze.html)。

