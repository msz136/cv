# VOL 05 EVAL-003 Source Freeze：Success Rate / Confidence Interval / Minimum Rollouts

> 状态：`source_frozen / VLA-EVAL-003 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-17  
> 证据截止：2026-07-17  
> 本切片冻结 success-rate 统计单元、Wilson / Clopper–Pearson 区间、近似样本量、cluster dependence 与停止规则的来源和项目证据边界；下游 knowledge 和一张原子题卡已在独立 bounded slice 生成，题卡保持 `unseen`，因此 VOL 05 为 knowledge 25/44、cards 25/44。

## 问题（Question）

面试中被问到“这个 VLA 成功率可信吗？至少要跑多少个 rollout？”时，不能只报 `k/n`。必须先定义 episode 是否是 Bernoulli 统计单元，再说明点估计、区间方法、置信水平、误差 margin、task/seed/init 的聚类关系，以及是否存在可选停止和重复测试。`n=50`、`n=250` 或“跑到看起来稳定”为经验数字，不是通用最小样本量。

本 source gate 固定以下边界：

```text
episode contract → X_i ∈ {0,1} → k=sum(X_i), n=count(X_i)
      → p_hat + Wilson/Clopper–Pearson interval
      → margin/decision threshold/sample-size plan
      → task/seed/init clustering and stopping rule
```

## 1. 冻结指纹与许可

以下 SHA 对 2026-07-17 取得的 pinned UTF-8 原文计算；本文件只记录公开来源、版本、路径和 hash，不复制凭据值。论文 DOI 是方法来源，官方实现是可运行语义来源。

| 来源 | 类型 / revision | pinned URL | 原文 SHA-256 | 可支持的边界 |
| --- | --- | --- | --- | --- |
| SciPy `scipy.stats._binomtest.py` | official-code / tag `v1.16.3`, commit `56e567e70ccad213d04ab04e7cfe7365562a71f1`, BSD-3 | [source@v1.16.3](https://github.com/scipy/scipy/blob/56e567e70ccad213d04ab04e7cfe7365562a71f1/scipy/stats/_binomtest.py) | `696ea9faf464bf7a5207cff49d37d3de4340855f08a78e00dfd1043f297d5a57` | `binomtest` 的 `k/n` 校验、exact（Clopper–Pearson）、Wilson/WilsonCC、zero/all-success 边界 |
| statsmodels `statsmodels/stats/proportion.py` | official-code / tag `v0.14.6`, commit `40e6a84d26ac74623c6b94b718f0987ef0351c53`, BSD-3 | [source@v0.14.6](https://github.com/statsmodels/statsmodels/blob/40e6a84d26ac74623c6b94b718f0987ef0351c53/statsmodels/stats/proportion.py) | `b039f25cf95166fcc882a9fd47f72b7ab90013bfda9823aa7acf3c2950978ed9` | normal / Wilson / beta（Clopper–Pearson）方法、覆盖率 caveat、正态近似 half-length 样本量函数 |
| Wilson (1927) | primary paper / DOI | [JASA DOI](https://doi.org/10.1080/01621459.1927.10502953) | DOI 指纹；未复制全文 | Wilson score interval 的原始方法 |
| Clopper & Pearson (1934) | primary paper / DOI | [Biometrika DOI](https://doi.org/10.1093/biomet/26.4.404) | DOI 指纹；未复制全文 | exact binomial interval 的原始方法 |
| Brown, Cai & DasGupta (2001) | peer-reviewed review / DOI | [Statistical Science DOI](https://doi.org/10.1214/ss/1009213286) | DOI 指纹；未复制全文 | 不同 binomial interval 的覆盖率与 Wald 方法风险背景 |
| Newcombe (1998) | peer-reviewed comparison / DOI | [Statistics in Medicine DOI](https://doi.org/10.1002/%28sici%291097-0258%2819980430%2917%3A8%3C857%3A%3Aaid-sim777%3E3.0.co%3B2-e) | DOI 指纹；未复制全文 | Wilson 与其他区间方法的比较背景；SciPy 实现注释明确引用该方法 |
| Kerry & Bland (1998) | primary cluster-design note / DOI | [BMJ DOI](https://doi.org/10.1136/bmj.316.7142.1455) | DOI 指纹；未复制全文 | 同一 task/cluster 内 rollout 相关时，design effect / effective sample size 的统计边界 |
| Johari et al. (2022) | peer-reviewed sequential inference / DOI | [Operations Research DOI](https://doi.org/10.1287/opre.2021.2135) | DOI 指纹；未复制全文 | 连续监测、可选停止与 fixed-n CI 不可混用；需要 always-valid/sequential 方法才可保持保证 |

实现与论文都只证明统计方法；它们不证明任何本地 VLA 结果的 episode 独立性、任务代表性、controller 安全性或个人 ownership。

## 2. 统计单元：先定义 episode，再谈成功率

### 2.1 Bernoulli contract

设第 (i) 个**预先定义的 episode** 是否满足 success predicate 为 (X_iin\{0,1\})，并且在一个明确 protocol 内近似独立同分布：

\[
X_i\sim\operatorname{Bernoulli}(p),\qquad
k=\sum_{i=1}^{n}X_i,\qquad
\hat p=\frac{k}{n}.
\]

变量解释：(p) 是在固定 task/init/seed/controller 协议下的真实成功概率，(k) 是成功 episode 数，(n) 是有效 episode 数。实现映射是 episode manifest 的 `success` 字段和 `episode_id` 计数；如果一个 episode 内的每个 action step 被当成样本，会把时间相关的控制轨迹错误地放大成独立样本。该 iid 条件是统计模型假设，不是 SciPy 函数自动验证的事实。

一个可审计的 episode manifest 至少要冻结：`model_revision`、`processor/normalizer_revision`、task id、init id、seed、controller/success predicate、horizon、warmup、replan、异常退出原因，以及 episode 是否被排除。`k/n` 只能在这些字段已经固定或明确分层时解释。

### 2.2 不能把不同指标混为 rollout success

| 结果类型 | 是否直接属于本节点 Bernoulli rollout success | 原因 |
| --- | --- | --- |
| 机器人 episode 成功/失败 | 是，前提是 success predicate 和统计单元固定 | (X_i) 可以是 episode-level binary outcome |
| 每条静态样本的 Box Acc@0.5 / Point Hit | 仅在该指标单独定义样本单元时可做 binomial CI | 它不是 robot episode；同图、多标注、同 prompt 可能相关 |
| Box IoU、平均距离、Text exact 的混合 aggregate | 否，不能直接套一个 success-rate CI | 连续指标、不同 scorer 和不同 pool 的统计语义不同 |
| `97.4%` 但没有 (n)、trial/seed/init/episode | 否 | 没有分母和统计单元，不能重算区间 |

## 3. 点估计与置信区间

### 3.1 Wilson score interval

令 (z=z_{1-\alpha/2})，Wilson 两侧区间为：

\[
\operatorname{CI}_{W}=\frac{\hat p+\frac{z^2}{2n}\;\pm\;z\sqrt{\frac{\hat p(1-\hat p)}{n}+\frac{z^2}{4n^2}}}{1+\frac{z^2}{n}}.
\]

变量解释：(alpha) 是双侧显著性水平，95% 区间取 (z\approx1.96)。分母的 (z^2/n) 使区间在 (k=0) 或 (k=n) 时仍有合理宽度；SciPy frozen implementation 的 `_binom_wilson_conf_int` 直接实现该表达式。Wilson 是近似区间，面试中不能称为“exact”。

### 3.2 Clopper–Pearson exact interval

SciPy 的 `method='exact'` 通过二项分布尾概率反演；等价地可写成 beta quantile 的边界：

\[
L=\begin{cases}0,&k=0\\B^{-1}(\alpha/2;k,n-k+1),&k>0\end{cases},\qquad
U=\begin{cases}B^{-1}(1-\alpha/2;k+1,n-k),&k<n\\1,&k=n\end{cases}.
\]

这里 (B^{-1}(q;a,b)) 表示 Beta((a,b)) 分布的 q 分位数。实现映射是 SciPy `_binom_exact_conf_int` 的 `binom.sf/cdf` 数值求根，statsmodels 的 `method='beta'` 走 Beta quantile；该区间覆盖率至少达到目标但可能偏保守，不能把“更宽”误解成模型更差。

### 3.3 zero/all-success 边界

当 (k=0) 或 (k=n) 时，Wald 区间会退化到点估计边界；SciPy exact/Wilson 实现显式返回 `[0, high]` 或 `[low, 1]`。例如 (n=20) 且 0 success 的 95% 区间约为 Wilson `[0, 0.161]`、exact `[0, 0.168]`；20/20 则为对称的 `[0.839, 1]` 与 `[0.832, 1]`。这些数字只说明不确定性仍然存在，不能说“20 次全成功就证明 (p=1)”。

## 4. 最小 rollout 数：先定 margin，再做计划

### 4.1 正态近似的规划公式

如果目标是双侧置信度 (1-\alpha) 和半宽（margin）不超过 (epsilon)，在预估成功率 (p_0) 下，Wald 近似给出：

\[
n\;\ge\;\frac{z_{1-\alpha/2}^{\,2}\,p_0(1-p_0)}{\epsilon^2}.
\]

变量解释：(p_0) 是规划时的先验比例，(epsilon) 是绝对成功率误差而非相对百分比，(z) 由置信水平决定。statsmodels `samplesize_confint_proportion` 只实现 normal approximation，因此这是**规划下界**；最终应使用 Wilson/exact 复核并向上取整。

若完全不知道 (p_0)，因为 (p(1-p)) 在 (p=0.5) 处最大，可用最坏情况：

\[
n_{\mathrm{worst}}\;\ge\;\frac{z_{1-\alpha/2}^{\,2}}{4\epsilon^2}.
\]

95% 置信度、(epsilon=0.05) 时，最坏情况约为 (384.16)，至少向上取 **385 个独立 Bernoulli 单元**。这不是 VLA 的固定规则：若目标是区分阈值 (p\ge p_\star)、比较两个 checkpoint、覆盖多个 task，通常还需要 power、paired design 或 multiplicity 规划。

### 4.2 本地数字的示例计算（不是新实验）

以下只是把现有材料中的分子/分母代入 frozen implementation；由于 task/init/seed 的相关性和远端 raw artifact 缺失，区间仅作**episode-level naive diagnostic**，不升级证据等级。

| 材料 | (k/n) | (hat p) | Wilson 95% | Clopper–Pearson 95% | 解释 |
| --- | ---: | ---: | ---: | ---: | --- |
| UWM fixed-pruned-init 五任务汇总 | 186/250 | 0.744 | [0.686, 0.794] | [0.685, 0.797] | 由项目材料用户确认；缺本地 250 条 episode raw bundle，且 task clustering 未建模 |
| UWM `book_caddy` | 44/50 | 0.880 | [0.762, 0.944] | [0.757, 0.955] | 单任务诊断；不能代表五任务平均或论文 protocol |
| OpenPiVLA archive `97.4%` | 未知 | 不可算 | 不可算 | 不可算 | `n`、trial/seed/init、episode records 和 checkpoint lineage 未闭合 |
| OPD raw-holdout | 10,000 行，但为 box/point/text pool | 不适用为 rollout success | 不适用 | 不适用 | 需按指标/格式单独定义统计单元；不能把 10k 行当 robot episodes |

UWM 的 186/250 来自 fixed-pruned-init、5-step warmup、每任务 50 次的项目口径；它不等于 UWM Table II 的 OOD initialization / 多 seed protocol。OpenPiVLA 的 97.4% 只有 committed summary；OPD 的 10k 是静态评估池。上述边界来自本仓库项目 inventories，而不是从比例数值反推出来的。

## 5. task/seed/init clustering 与 effective sample size

如果同一 task、同一初始状态族或同一 seed 下的 episode 共享难度、模型随机性或环境状态，则 (X_i) 不是独立样本。等大小 cluster、每簇 (m) 个观测、组内相关系数（ICC）为 (ho) 时，常用设计效应是：

\[
\operatorname{DE}=1+(m-1)\rho,\qquad n_{\mathrm{eff}}\approx\frac{n}{\operatorname{DE}}.
\]

变量解释：(operatorname{DE}>1) 表示相关性让有效信息量小于 episode 数；当 (ho=0) 才退化为独立样本。实现映射不是把原始 `n` 直接替换掉，而是要在 protocol manifest 中记录 cluster id，并选择 cluster-robust CI、task-level bootstrap 或预先配对设计。仅有 5 个 task × 50 rollouts 时，250 不能自动等于 250 个独立证据点。

面试安全说法：如果目标是总体平均 success，应预先规定 task 权重、每 task 的 rollout 与 seed，并按 cluster/stratified protocol 汇总；如果目标是单一 task 的条件 success，则只对该 task 的 episode 做区间。跨 task 的 macro/micro/weighted aggregation 属于 `VLA-EVAL-005`，paired checkpoint significance 属于 `VLA-EVAL-004`，本节点不提前解决。

## 6. 停止规则、阈值与可选停止

### 6.1 固定设计与决策阈值

“最小 rollout 数”还取决于面试/发布决策：是希望区间半宽 (epsilon)，还是要以给定置信度证明 (p\ge p_\star)，或检测两个 checkpoint 的差异。后两者需要明确 null/alternative、power、效应大小和 paired/cluster structure；只套 margin 公式会把“估计得准”和“判定过线”混为一谈。

固定 (n) 后一次计算 Wilson 或 exact 区间，属于本切片的默认 contract。若每 10 个 episode 看一次 CI，看到上界/下界合意就停止，最终的 nominal 95% 覆盖率未必仍然成立；连续监测应使用 always-valid confidence sequence 或正式 sequential design，而不是把普通 fixed-n CI 反复使用。

### 6.2 实现伪代码（统计 contract，不是本地现有脚本）

```python
def plan_and_score_rollouts(episodes, confidence=0.95, margin=0.05):
    # 1. Filter only pre-registered, valid episode-level success records.
    x = [int(ep["success"]) for ep in episodes if ep["valid"]]
    k, n = sum(x), len(x)

    # 2. Compute point estimate and both intervals; do not hide zero/all cases.
    p_hat = k / n
    wilson = scipy.stats.binomtest(k, n).proportion_ci(confidence, method="wilson")
    exact = scipy.stats.binomtest(k, n).proportion_ci(confidence, method="exact")

    # 3. Check the pre-registered margin/threshold and report protocol clusters.
    return {"k": k, "n": n, "p_hat": p_hat,
            "wilson": wilson, "exact": exact,
            "task_ids": sorted({ep["task_id"] for ep in episodes}),
            "init_seed_ids": sorted({(ep["init_id"], ep["seed"]) for ep in episodes})}
```

伪代码把 episode validity、统计计算和 protocol metadata 分开；它不是 UWM、OpenPiVLA 或 OPD 已有的统一 scorer。若采样采用中途可选停止，必须在函数外记录 stopping rule 或改用 sequential inference。

## 7. 本地项目证据边界

| 项目材料 | 当前可支持 | 当前不能支持 |
| --- | --- | --- |
| [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `186/250=0.744` 的 user-confirmed remote final、fixed-pruned-init / 5-step warmup / 50-task 口径；旧 reset-style 仅为 protocol diagnostic | 本地 250 episode raw JSON、checkpoint/normalizer hash、cluster-robust CI、与 Table II 直接可比 |
| [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | archive `224_h10_40000` summary 的 97.4%，以及缺少 raw trial/seed/init/episode 的明确边界 | 可信 `n`、CI、formal Qwen checkpoint 的归属或高于 official baseline 的显著性 |
| [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.html) | 10,000-row raw-holdout、box/point/text pool、by-format/by-pool 统计协议 | 把 IoU/text/point 混成 episode success；把 row count 当独立 rollout；真实机器人闭环成功率 |
| [UWM project page](../../05_uwm_libero_eval_protocol.html) / [OpenPiVLA project page](../../03_openpivla_action_modeling.html) | 面试叙事和来源等级的现有安全措辞 | 新的统计实验、独立复算或额外 seed/init 证据 |

本节点不把本地报告中的百分比写成“统计显著”，也不把 `97.4%` 或 OPD 指标硬套到 success-rate CI。后续若补齐 episode-level manifests，必须在同一 protocol 下重新计算，并说明 cluster/aggregation 处理。

## 8. 验证矩阵与 Source Gate 结论

| Case | 最小验证 | 当前状态 |
| --- | --- | --- |
| ordinary success rate | 固定 success predicate，记录 (k,n)，Wilson + exact | PASS（官方实现已冻结） |
| zero/all success | (k=0) 与 (k=n) 的 non-degenerate interval | PASS（SciPy/statsmodels 代码可复查） |
| margin planning | 固定 (alpha,epsilon,p_0)，normal approximation 向上取整 | PASS WITH WARNING（只是规划下界） |
| task/seed/init clustering | cluster id、ICC/design effect 或 cluster bootstrap | PENDING（本地 186/250 尚无 raw episode/ICC） |
| threshold decision | (p\ge p_\star) 的 one-sided/power 设计 | PENDING（留给 EVAL-004/005 相关设计） |
| optional stopping | fixed-n 或 always-valid sequential method，禁止反复看普通 CI | PASS WITH WARNING（论文边界已冻结，项目未实现） |
| OpenPiVLA 97.4 | 必须有 (n)、trial/seed/init、episode/raw summary、lineage | FAIL CLOSED（当前仅 archive-summary-only） |
| OPD 10k | 按 metric/pool 单独定义 observation unit，不叫 rollout success | PASS WITH WARNING |
| canonical/source integrity | Markdown SHA→HTML meta→review JSON 一致 | PASS（已完成静态哈希链核验） |
| browser visual QA | in-app Browser 打开 local `file://` | BLOCKED（静态检查不替代视觉 QA） |
| oral drill | 一次只问 `VLA-EVAL-003`，真实口述后再更新 mastery | PENDING |

**Source Gate 结论：**SciPy 与 statsmodels 官方实现足以冻结 `k/n`、Wilson、Clopper–Pearson、zero/all-success 和正态近似样本量的技术语义；Wilson / Clopper–Pearson / interval-comparison 论文、cluster design-effect 文献和 sequential-inference 论文提供方法边界。当前本地项目证据只支持“先定义 protocol 和统计单元，再讨论区间”，不支持把 186/250、97.4% 或 OPD 10k 直接当作同一种独立 Bernoulli rollout 结果。Verdict 保持 `WARN`；`VLA-EVAL-003` knowledge、原子题卡和 review 已生成，题卡保持 `unseen`，下一步只做真实口述或补 episode-level artifacts。

## References

1. SciPy `scipy.stats._binomtest.py@v1.16.3`：[`binomtest` / `proportion_ci`](https://github.com/scipy/scipy/blob/56e567e70ccad213d04ab04e7cfe7365562a71f1/scipy/stats/_binomtest.py)。
2. statsmodels `statsmodels/stats/proportion.py@v0.14.6`：[`proportion_confint` / `samplesize_confint_proportion`](https://github.com/statsmodels/statsmodels/blob/40e6a84d26ac74623c6b94b718f0987ef0351c53/statsmodels/stats/proportion.py)。
3. E. B. Wilson, “Probable Inference, the Law of Succession, and Statistical Inference,” 1927，[DOI](https://doi.org/10.1080/01621459.1927.10502953)。
4. C. J. Clopper and E. S. Pearson, “The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial,” 1934，[DOI](https://doi.org/10.1093/biomet/26.4.404)。
5. L. D. Brown, T. T. Cai, and A. DasGupta, “Interval Estimation for a Binomial Proportion,” 2001，[DOI](https://doi.org/10.1214/ss/1009213286)。
6. R. G. Newcombe, “Two-sided Confidence Intervals for the Single Proportion: Comparison of Seven Methods,” 1998，[DOI](https://doi.org/10.1002/%28sici%291097-0258%2819980430%2917%3A8%3C857%3A%3Aaid-sim777%3E3.0.co%3B2-e)。
7. S. M. Kerry and J. M. Bland, “The Intracluster Correlation Coefficient in Cluster Randomisation,” 1998，[DOI](https://doi.org/10.1136/bmj.316.7142.1455)。
8. R. Johari et al., “Always Valid Inference: Continuous Monitoring of A/B Tests,” 2022，[DOI](https://doi.org/10.1287/opre.2021.2135)。
9. 本仓库 [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.md)、[OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.md)、[OPD inventory](../evidence/projects/opd_claim_evidence_inventory.md) 与项目页面。
