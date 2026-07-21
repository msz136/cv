# VOL 05 EVAL-004 Source Freeze：Paired Init / Seed Evaluation 与显著性

> 状态：`source_frozen / VLA-EVAL-004 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 paired unit、binary discordant table、exact McNemar、pair 内 randomization、paired bootstrap、training-seed 层级、multiplicity 与项目真实性边界；下游只生成一张 `VLA-EVAL-004` 原子题卡，VOL 05 同步为 knowledge/cards 26/44。

## 问题（Question）

当面试官问“新 checkpoint 比 baseline 高 4 个点，显著吗？”时，正确入口不是把两个汇总成功率直接送入独立样本检验。先要证明 A/B 在同一个 task、同一个 initialization、同一个 environment/rollout protocol 上成对，再冻结 seed 类型、无效 pair 规则、checkpoint selection、task 权重和多重比较范围。

本 source gate 固定以下最小链路：

```text
same task + same init snapshot/hash + same protocol
        -> pair_id and A/B binary outcomes
        -> n11/n10/n01/n00 + paired effect
        -> exact McNemar / paired randomization + paired CI
        -> task/training-seed hierarchy + multiplicity + practical threshold
```

## 1. 冻结来源、revision 与许可

以下 hash 对 2026-07-18 取得的公开响应或 pinned UTF-8 原文计算。论文响应 hash 只证明本轮取得的来源对象，没有替代论文版本号、DOI 或实验复现；官方代码只支持实现语义，不证明任何本地 VLA 结果成立。

| ID | 来源 | 类型 / revision | 固定入口 | SHA-256 | 本节点支持范围 |
| --- | --- | --- | --- | --- | --- |
| S1 | McNemar (1947), correlated proportions | primary / DOI | [Psychometrika DOI](https://doi.org/10.1007/BF02295996) | DOI 指纹 | paired binary outcomes 只由 discordant pairs 提供差异证据 |
| S2 | Newcombe (1998), paired proportions CI | peer-reviewed / DOI | [Statistics in Medicine DOI](https://doi.org/10.1002/%28SICI%291097-0258%2819980501%2917%3A10%3C873%3A%3AAID-SIM779%3E3.0.CO%3B2-I) | DOI 指纹 | paired proportion difference 的区间不能假装两臂独立 |
| S3 | statsmodels `contingency_tables.py` | official-code / `v0.14.6`, commit `40e6a84d26ac74623c6b94b718f0987ef0351c53`, BSD-3 | [source](https://github.com/statsmodels/statsmodels/blob/40e6a84d26ac74623c6b94b718f0987ef0351c53/statsmodels/stats/contingency_tables.py) | `af2e5455df459abc9ced79186e16fecf38344cc630aeec1ade9e6e65b488090f` | `mcnemar(exact=True)` 使用 off-diagonal discordant counts 和 `p=0.5` binomial tail |
| S4 | SciPy `_resampling.py` | official-code / `v1.16.3`, commit `b9105ccc2237f57acb1060202cd77f6dd264fb34`, BSD-3 | [source](https://github.com/scipy/scipy/blob/b9105ccc2237f57acb1060202cd77f6dd264fb34/scipy/stats/_resampling.py) | `ad8335279281c69d4a3bbf4449100e3ac5e1f5bc7af360963133973ed2a64d7e` | `bootstrap(..., paired=True)` 共用 resampled indices；paired A/B assignment 用 `permutation_type="samples"` |
| S5 | SciPy `_binomtest.py` | official-code / `v1.16.3`, same commit, BSD-3 | [source](https://github.com/scipy/scipy/blob/b9105ccc2237f57acb1060202cd77f6dd264fb34/scipy/stats/_binomtest.py) | `696ea9faf464bf7a5207cff49d37d3de4340855f08a78e00dfd1043f297d5a57` | discordant-pair null 下的 exact binomial 计算语义 |
| S6 | Henderson et al., *Deep RL That Matters* | primary / arXiv `1709.06560` | [arXiv](https://arxiv.org/abs/1709.06560) | response `9180e8b28b30a7e013e3676786d8632190888dd82b667fce5d76216aa87cb585` | 随机种子、实现差异与统计报告会改变 RL 结论 |
| S7 | Colas et al., *How Many Random Seeds?* | primary / arXiv `1806.08295` | [arXiv](https://arxiv.org/abs/1806.08295) | response `dd230757a4eba88b99df2dbb05bfe7658ec2f8eefc7a1e282aa9f095055e6012` | training-run variability、seed 数与 power/效应大小要共同报告 |
| S8 | Agarwal et al., *Deep RL at the Edge of the Statistical Precipice* | primary / arXiv `2108.13264` | [arXiv](https://arxiv.org/abs/2108.13264) | response `74f11076d64de0f6beb9da4a9b185dd2a42465bfde6426fb2004fd6fd9e042ac` | 多 task / 多 run 的不确定性、robust aggregate 与 bootstrap 边界 |
| S9 | `google-research/rliable` | official-code / commit `3ccd9f4dea577a04d3d2b557f259aac08badbd81`, Apache-2.0 | [repository](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81) | README `c4d474f8a018c6faf8ab5d365bad135258a2af851e2a5672e07999438fcc6237`; library `0af084e4040fad3ae02a612b16fbcc59d9a141ac8259ad47dc1932bcc168ac14`; metrics `caf0c74e6238a12d2f59d6bcd47115e56167ea73c3b851c3f7981de17e5230cc`; LICENSE `43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1` | run uncertainty、task stratification 与 aggregate reporting 的实现参考；不是本地 VLA scorer |

SciPy `v1.16.3` 的 annotated tag object 是 `56e567...`，实际 commit 是 `b9105ccc...`；本表用实际 commit 固定 blob。任何“same seed 就完全相同”的说法都不是这些来源支持的结论。

## 2. Pairing unit：配的是实验条件，不是行号

一个 pair 至少共享：`task_id`、可验证的 `init_snapshot_hash`、环境/controller/scorer/protocol version、horizon、checkpoint role、success predicate。推荐主键：

```text
pair_id = hash(task_id, init_snapshot_hash, env_revision,
               controller_revision, scorer_revision, protocol_hash,
               rollout_repeat_id)
```

`seed` 只能帮助重放，不能代替 init 证据。同一个整数 seed 在不同 simulator version、wrapper、进程顺序、随机调用次数或 reset path 下可能得到不同初始状态；至少保存 reset 后 state/proprio、首帧或 init snapshot/hash，并在 A/B 开始前核对。

### 2.1 四类 seed 必须分开

| seed | 控制对象 | 在 paired 设计中的位置 | 常见误用 |
| --- | --- | --- | --- |
| environment / init seed | task 初态、物体位置、场景随机化 | pairing key 的候选字段，仍需 snapshot/hash 验证 | 只看整数相同就宣称 same init |
| rollout stochastic seed | policy sampling、noise、planner sampling | 可作为 common-random-number 条件或重复层 | 把同 seed 当作独立 episode |
| model training seed | 初始化、shuffle、dropout、优化轨迹 | 更高层 replicate；每个 checkpoint run 是统计单位 | 用单个训练 run 的几百个 episode 替代多个 training runs |
| sampler / bootstrap seed | permutation 或 bootstrap 的 Monte Carlo 随机性 | 只保证分析可复算 | 把 resampling seed 当成实验复现 seed |

若 A/B 架构或执行路径不同，共用 rollout seed 未必产生同一噪声语义；此时 pairing 依赖 same init/protocol，不能把“随机数消费顺序相同”作为隐含前提。

## 3. Paired binary 四格表与效应

对每个有效 pair 记录二元结果 `(A_i,B_i)`，汇总：

| cell | 含义 | 对差异的作用 |
| --- | --- | --- |
| `n11` | A 成功、B 成功 | concordant；不支持方向差异 |
| `n10` | A 成功、B 失败 | discordant；支持 A 优于 B |
| `n01` | A 失败、B 成功 | discordant；支持 B 优于 A |
| `n00` | A 失败、B 失败 | concordant；不支持方向差异 |

令 `n=n11+n10+n01+n00`，paired risk difference 为：

\[
\hat\Delta=\frac{1}{n}\sum_{i=1}^{n}(A_i-B_i)=\frac{n_{10}-n_{01}}{n}.
\]

变量解释：`A_i-B_i` 只可能是 `1/0/-1`；因此相同 pair 上双方都成功或都失败时贡献为 0。实现映射是先 join pair manifest，再逐 pair 计算 `delta_i`，绝不能由两个不带 join key 的 aggregate success rate 反推四格表。

报告至少包含 `n11/n10/n01/n00`、`Delta`、paired CI、p-value、alpha 与预注册 practical threshold。p-value 不是 effect size，统计显著也不自动等于工程收益。

## 4. Exact McNemar：只看 discordant pairs

在“discordant pair 中两个方向等概率”的 null 下，令 `d=n10+n01`：

\[
n_{10}\mid d\sim\operatorname{Binomial}(d,0.5).
\]

变量解释：`d` 是真正对 A/B 方向差异提供信息的 pair 数。statsmodels `mcnemar(exact=True)` 取 off-diagonal 较小计数作为 statistic，并用 `Binomial(d,0.5)` 尾概率计算双侧 exact p-value。`n11+n00` 再大，也不能制造更多 discordant direction evidence。

当 `d=0` 时，样本中没有观察到方向差异，不能说“两模型等价”；只能说该 protocol/样本没有提供差异证据。若目标是 non-inferiority/equivalence，需另行预注册 margin 和相应设计。

## 5. Paired randomization 与 paired bootstrap

### 5.1 Randomization / permutation

对统计量 `mean(A-B)`，null 下在每个 pair 内交换 A/B 标签，而不是打乱 observation-pair 对应关系：

```python
from scipy.stats import permutation_test

# "samples" swaps A/B assignment within each paired observation.
result = permutation_test(
    (a, b),
    statistic=lambda x, y, axis: (x - y).mean(axis=axis),
    permutation_type="samples",
    alternative="two-sided",
)
```

SciPy 的 `permutation_type="pairings"` 是重排样本内部的配对关系，适合 association/correlation 类 null，不是本节点 A/B paired assignment test。两者写反会检验不同假设。

### 5.2 Paired bootstrap

paired bootstrap 必须抽 pair index，并把同一组 index 同时用于 A/B：

```python
from scipy.stats import bootstrap

# paired=True reuses one resampled index vector for both arms.
ci = bootstrap(
    (a, b),
    statistic=lambda x, y, axis: (x - y).mean(axis=axis),
    paired=True,
    confidence_level=0.95,
)
```

若 task 是目标总体的一部分，应按预注册目标做 task-stratified 或 cluster bootstrap；不能把 frame、同 episode 的 step、重复图像路径或同 training run 下的大量 rollout 展开成 iid。`rliable` 的 stratified bootstrap 是跨 task/run 报告的实现参考，但不是“任意二维数组都自动代表正确层级”。

## 6. Training seed、cluster 与 power

### 6.1 episode 不能替代 training runs

若结论是“训练方法 A 优于 B”，推断单位首先是 model training run。每个 training seed 生成一对 A/B checkpoint，再在共享 task/init grid 上评估；episode 层只估计该 checkpoint pair 的 rollout noise。只有一个 A checkpoint 和一个 B checkpoint 时，即使各跑 10,000 episodes，也不能估计训练过程的 seed-to-seed variability。

推荐结构：

```text
training_seed
  -> checkpoint_A / checkpoint_B
      -> task
          -> init_snapshot
              -> rollout repeat -> A/B success
```

分析可在 training-run 顶层做 paired seed comparison，并在 run 内对 task/init cluster 建模或 bootstrap。若 nominal same training seed 对两方法不构成可信 common random numbers，应改用独立或层级设计并如实说明。

### 6.2 power 由 discordance 与目标效应共同决定

McNemar exact 的有效 trial 数是 `d=n10+n01`，不是总 `n`。规划 MDE / power 时要预估 discordant rate `q=(n10+n01)/n` 以及 discordant direction imbalance，而不是只写“跑 250 对”。若两个模型几乎总是一起成功/失败，`n` 很大但 `d` 很小，差异检验仍可能没有 power。

最低报告：预期 baseline、practical effect threshold、预计 discordant rate、alpha、power、task/training-seed 层级、计划 pair 数与允许的 invalid-pair 比例。pilot 用来估计这些量时，要和 final holdout 分开。

## 7. Invalid pairs、选择偏差与多重比较

### 7.1 invalid-pair rule 预注册

先定义 environment crash、timeout、安全终止、缺帧、scorer error、单臂服务异常分别记 failure、invalid 还是 infrastructure exclusion。观察 A/B 结果后再删 pair 会引入选择偏差；特别是单臂异常不能静默删除。必须同时报告 attempted pairs、valid pairs、每类 exclusion count、单臂/双臂异常及 sensitivity analysis。

### 7.2 selection 与 final holdout 分离

用同一批 init 挑 checkpoint/horizon/replan K，再在同一批 init 上报最终 p-value，会低估选择带来的乐观偏差。checkpoint selection 使用 validation grid；最终结论使用预先锁定、未参与选择的 holdout grid和冻结 scorer。

### 7.3 multiplicity

如果同时比较多个 task、checkpoint、horizon、seed slice 或指标，单个 `p<0.05` 不再代表整个搜索过程的 5% 错误率。三种安全策略：

1. 预注册一个 primary endpoint 和一个 primary comparison，其余为 exploratory；
2. 对有限 family 使用 Holm step-down 控制 family-wise error；
3. 对多 task / 多 run 用层级模型或预注册 aggregate，同时报告 per-task effect，不从最亮眼 task 反推总体结论。

Holm 只处理 multiplicity，不修复错误 pairing、protocol drift 或 selection leakage。

## 8. 本地项目真实性边界

| 项目材料 | 当前可支持 | 当前不能支持 |
| --- | --- | --- |
| [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | fixed-pruned-init `186/250=0.744` 与 reset-style `232/250=0.928` 属于不同 protocol；差异可作为 protocol sensitivity 风险 | 没有同 checkpoint、同 normalizer/scorer、同 task/init/seed 的 250 对 raw outcomes；不能构造 `n10/n01`，不能做 McNemar，不能称 paired uplift |
| [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | archive summary 记录 `97.4%`，并明确 denominator/trial/seed/init/lineage 缺失 | 不能进入 paired comparison、不能计算 paired CI/p-value、不能声称显著高于 official |
| [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.html) | 10,000-row box/point/text 静态 holdout 可按 metric/pool 设计 cluster-aware 分析 | row 不是 robot episode；重复 image/path 是 cluster，不能和 rollout paired test 混用 |
| [EVAL-003 source](vol_05_eval003_success_rate_confidence_interval_source_freeze.html) / [artifact gate](vol_05_eval003_local_statistical_artifact_gate.html) | episode-level CI、分母、cluster 与 raw artifact 最低字段 | 不能从两个 aggregate CI 推导 pair table；既存 EVAL-003 hash 漂移不在本切片顺手修复 |

UWM 若要补证据，最小 pair row 为：`pair_id, task_id, init_snapshot_hash, env_seed, rollout_seed, training_seed, A_checkpoint, B_checkpoint, protocol_hash, A_success, B_success, A_valid, B_valid, exclusion_reason`。本节点只给 artifact contract，不声称项目已经采集。

## 9. 最小验证矩阵

| case | 必须验证 | 当前状态 |
| --- | --- | --- |
| same seed / different init | 对比 snapshot/hash、首帧或 reset-state | PENDING（项目未提供） |
| four-cell table | `n11+n10+n01+n00=n`，逐 pair 可回查 | PENDING（项目无 raw pairs） |
| exact McNemar | 只使用 `n10+n01`，zero-discordance 明示 | PASS（official-code frozen） |
| paired permutation | pair 内交换 A/B，SciPy `samples` | PASS（official-code frozen） |
| paired bootstrap | A/B 共用 resampled indices，SciPy `paired=True` | PASS（official-code frozen） |
| hierarchy | training run 与 task/init/episode 不展开为 iid | PASS WITH WARNING（合同完成，本地运行缺失） |
| invalid pairs | 预注册并报告单臂/双臂异常 | PENDING（项目规则未冻结） |
| multiplicity | primary endpoint 或 Holm/层级处理 | PASS WITH WARNING（方法边界完成，项目未执行） |
| practical significance | effect/CI/MDE 与 p-value 分开 | PASS WITH WARNING |
| canonical integrity | Markdown SHA→HTML meta→review JSON | PASS（本轮渲染后核验） |
| browser visual QA | in-app Browser 打开 local `file://` | BLOCKED（策略限制；静态检查不替代视觉 QA） |
| oral drill | 真实口述后才更新 mastery | PENDING |

## 10. Source Gate 结论与下一入口

EVAL-004 的 source gate 为 `WARN`：paired binary 的方法、official implementation、seed 层级和最小 artifact contract 已冻结；本地 UWM/OpenPiVLA/OPD 均没有可执行的 paired raw bundle，因此不产生新的显著性结论。知识页与一张题卡保持 `unseen`，不创建 `coaching_state.md`。

下一内容节点固定为 `VLA-EVAL-005`：macro / micro / per-task / weighted aggregation；只有在用户真实口述时才可另开 drill slice。

## References

1. McNemar, “Note on the Sampling Error of the Difference between Correlated Proportions or Percentages,” [DOI](https://doi.org/10.1007/BF02295996)。
2. Newcombe, “Improved confidence intervals for the difference between binomial proportions based on paired data,” [DOI](https://doi.org/10.1002/%28SICI%291097-0258%2819980501%2917%3A10%3C873%3A%3AAID-SIM779%3E3.0.CO%3B2-I)。
3. statsmodels `mcnemar` frozen [source](https://github.com/statsmodels/statsmodels/blob/40e6a84d26ac74623c6b94b718f0987ef0351c53/statsmodels/stats/contingency_tables.py)。
4. SciPy `bootstrap` / `permutation_test` frozen [source](https://github.com/scipy/scipy/blob/b9105ccc2237f57acb1060202cd77f6dd264fb34/scipy/stats/_resampling.py)。
5. Henderson et al., [*Deep RL That Matters*](https://arxiv.org/abs/1709.06560)；Colas et al., [*How Many Random Seeds?*](https://arxiv.org/abs/1806.08295)。
6. Agarwal et al., [*Deep RL at the Edge of the Statistical Precipice*](https://arxiv.org/abs/2108.13264)；[`rliable`](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81)。
7. [EVAL-003 Success Rate / CI Source Freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.html) 与 [Local Statistical Artifact Gate](vol_05_eval003_local_statistical_artifact_gate.html)。

