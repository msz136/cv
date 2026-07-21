# VOL 05 EVAL-003：Success Rate、置信区间与最小 Rollout 数

> 状态：`drafted / VLA-EVAL-003 / knowledge_25_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 来源入口：[EVAL-003 Source Freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。本节点的单张原子题卡已同步生成并保持 `unseen`；真实口述状态仍未开始。

## 问题（Question）

面试官问“成功率是多少？至少要跑多少个 rollout？”时，可信回答不能停在 `k/n`。需要先固定 episode-level success predicate 和 protocol，再说明 Bernoulli 点估计、Wilson/Clopper–Pearson 区间、误差 margin、task/seed/init 相关性以及停止规则。`n=50` 或 `n=250` 不是跨任务通用的最小样本数；样本量取决于置信水平、精度目标、决策阈值、比较设计和统计单元。

本节点对应知识地图的 VOL 05 Evaluation / Debugging，承接 `VLA-EVAL-001` 的 protocol tuple 与 `VLA-EVAL-002` 的 metric ladder，后续连接 `VLA-EVAL-004` paired significance 和 `VLA-EVAL-005` aggregation。

## 1. 30 秒直觉：先定义“一个样本”，再算区间

直觉上，success rate 是在同一评估合同下，成功 episode 占有效 episode 的比例；置信区间回答“如果重复抽取同类 episode，真实成功率可能落在哪个范围”。它不是模型能力的绝对证明，也不是把不同 task、seed、init 或 scorer 混在一起后自动得到的统计保证。

专业地说，必须先定义一个预注册的 episode 统计单元（statistical unit）：固定 task、环境、初始状态分布、seed、checkpoint、processor/normalizer、controller、horizon、warmup、replan 和 success predicate，然后记录每个 episode 的 `success ∈ {0,1}`、有效性、失败原因和 trace。

## 2. Bernoulli 合同与 episode manifest

令第 (i) 个有效 episode 的成功指示变量为 (X_i)：

\[
X_i\in\{0,1\},\qquad X_i\sim\operatorname{Bernoulli}(p),\qquad k=\sum_{i=1}^{n}X_i,\qquad \hat p=\frac{k}{n}.
\]

变量解释：(p) 是固定 protocol 下的真实成功概率，(k) 是成功 episode 数，(n) 是有效 episode 数，(hat p) 是点估计。实现上，(X_i) 应来自 episode manifest 的 success predicate，而不是把 episode 内每个 action step 当成独立样本；SciPy `binomtest` 只验证 `0 ≤ k ≤ n`，不会替你验证独立性或任务代表性。[1][2]

### 2.1 最小 manifest 字段

| 层级 | 字段 | 作用 |
| --- | --- | --- |
| run | `model_revision`、checkpoint、processor、normalizer、config、runtime | 确定评估对象和加载语义 |
| protocol | task、env、init distribution、seed、warmup、horizon、replan、controller、success predicate | 确定什么叫一次可比试验 |
| episode | `episode_id`、task/init/seed id、valid、success、termination、failure reason | 构造 (X_i) 并保留排除理由 |
| trace | observation/action timestamp、raw prediction、controller ack、video/log path | 支持 first-failure 和复算 |
| summary | (k)、(n)、per-task count、interval method、confidence、stopping rule | 防止只留一个百分比 |

若一个 episode 因环境崩溃被排除，必须记录 `valid=false` 和排除原因；静默从分母中删掉失败，会使 (hat p) 偏高。

## 3. 点估计与两种主区间

### 3.1 Wilson score interval

令 (z=z_{1-\alpha/2})，Wilson 双侧区间写成：

\[
\operatorname{CI}_{W}=\frac{\hat p+\frac{z^2}{2n}\;\pm\;z\sqrt{\frac{\hat p(1-\hat p)}{n}+\frac{z^2}{4n^2}}}{1+\frac{z^2}{n}}.
\]

变量解释：(alpha) 是双侧显著性水平，95% 区间取 (z\approx1.96)。Wilson 的中心和宽度同时考虑 (n) 与边界比例，比直接使用 Wald 的 (hat p\pm z\sqrt{\hat p(1-\hat p)/n}) 更适合小样本或接近 0/1 的 success rate。SciPy v1.16.3 的 `_binom_wilson_conf_int` 和 statsmodels v0.14.6 的 `method="wilson"` 提供可复查实现。[1][2]

### 3.2 Clopper–Pearson exact interval

Clopper–Pearson 通过二项分布尾概率反演，等价地可以表示为 Beta 分布分位数：

\[
L=\begin{cases}0,&k=0\\B^{-1}(\alpha/2;k,n-k+1),&k>0\end{cases},\qquad
U=\begin{cases}B^{-1}(1-\alpha/2;k+1,n-k),&k<n\\1,&k=n\end{cases}.
\]

其中 (B^{-1}(q;a,b)) 是 Beta((a,b)) 的 q 分位数。SciPy 的 `method="exact"` 通过 binomial CDF/SF 数值求根，statsmodels 的 `method="beta"` 使用 beta quantile；它的覆盖率至少达到目标但通常更保守，因此区间可能比 Wilson 更宽。[1][2][3]

### 3.3 zero/all-success 不是“证明概率为 0/1”

当 (k=0) 或 (k=n) 时，Wald 区间会退化到边界；Wilson 和 exact 仍然保留不确定性。以 (n=20) 为例：0 success 的 95% Wilson 区间约为 `[0, 0.161]`，exact 约为 `[0, 0.168]`；20/20 则约为 `[0.839, 1]` 和 `[0.832, 1]`。因此“20 次全成功”只能说明在这 20 个试验中没有观察到失败，不能说真实 (p=1)。

## 4. 最小 rollout 数：margin 规划不是万能常数

### 4.1 由置信度和绝对误差推导

如果目标是双侧置信度 (1-\alpha)，并希望区间半宽约不超过 (epsilon)，给定先验比例 (p_0) 时，正态近似样本量规划为：

\[
n\;\ge\;\frac{z_{1-\alpha/2}^{\,2}\,p_0(1-p_0)}{\epsilon^2}.
\]

变量解释：(p_0) 是规划比例，(epsilon) 是绝对 success-rate margin，不是相对百分比。statsmodels 的 `samplesize_confint_proportion` 目前只实现 normal approximation，因此结果是规划下界，最终要用 Wilson/exact 区间复核并向上取整。[2]

完全不知道 (p_0) 时，(p(1-p)) 在 0.5 最大：

\[
n_{\mathrm{worst}}\;\ge\;\frac{z_{1-\alpha/2}^{\,2}}{4\epsilon^2}.
\]

95% 置信度、(epsilon=0.05) 时约为 (384.16)，所以至少取 385 个**独立 Bernoulli 单元**。这不是 VLA 的固定规则：如果要证明 (p\ge p_\star)、比较两个 checkpoint、覆盖 5 个 task 或控制多重比较，还需要 power、paired design、task allocation 和 multiplicity 设计。

### 4.2 三种“够不够”的目标要区分

| 目标 | 需要的设计 | 不能用什么替代 |
| --- | --- | --- |
| 估计总体成功率到 margin (epsilon) | fixed-n + Wilson/exact CI | 只报点估计 |
| 证明成功率超过阈值 (p_\star) | 单侧区间或 power-based hypothesis test | 看到 (hat p>p_\star) 就宣称过线 |
| 比较两个 checkpoint | paired init/seed/task、差值区间或随机化检验 | 两个独立 aggregate CI 不重叠就下因果结论 |

最后一行留给 `VLA-EVAL-004`；macro/micro/per-task 权重留给 `VLA-EVAL-005`。

## 5. task/seed/init 相关性：250 次不一定是 250 个信息点

同一个 task、初始状态族或 seed 下的 episode 往往共享难度和随机性，(X_i) 可能相关。等大小 cluster、每簇 (m) 个 episode、组内相关系数（ICC）为 (ho) 时，常用 design effect 为：

\[
\operatorname{DE}=1+(m-1)\rho,\qquad n_{\mathrm{eff}}\approx\frac{n}{\operatorname{DE}}.
\]

变量解释：(operatorname{DE}>1) 表示相关性降低有效信息量；(ho=0) 才回到独立样本。实现映射不是机械地把 `n` 改小，而是保留 cluster id，按 task/seed/init 做分层汇总、cluster bootstrap、cluster-robust variance 或预先配对的设计。[6]

例如 5 个 task 各跑 50 次，原始 (n=250)，但若主要不确定性来自 task 难度，任务数量而非 episode 数才是总体泛化的瓶颈。此时应同时报告 per-task 区间和总体区间，并说明权重；不要用 250 个 episode 掩盖只有 5 个 task 的覆盖面。

## 6. 停止规则与重复查看

固定 (n) 后一次性计算 CI 是本节点默认 contract。如果每跑 10 个 episode 就查看一次普通 95% CI，看到区间下界超过阈值便停止，nominal coverage 不再自动保持；这是可选停止（optional stopping）和重复测试风险。若需要连续监测，应预先使用 always-valid confidence sequence 或正式 sequential design，而不是把 fixed-n CI 重复套用。[7]

一个可执行的预注册 stopping contract 至少写清：最大 (n)、最小 (n)、检查间隔、阈值、失败/超时是否计入分母、何时暂停、是否允许追加 seed，以及报告中如何披露中途检查。没有这些字段，“跑到稳定”为不可审计的停止规则。

## 7. 实现映射：从 episode manifest 到区间

下面是统计 contract 的最小实现示意，不代表本地已有统一 scorer：

```python
from scipy.stats import binomtest

def score_success_rate(episodes, confidence=0.95):
    # 1. Keep only pre-registered valid episode-level outcomes.
    valid = [ep for ep in episodes if ep["valid"]]
    successes = [int(ep["success"]) for ep in valid]
    k, n = sum(successes), len(successes)
    if n == 0:
        raise ValueError("no valid episodes")

    # 2. Compute point estimate and two complementary intervals.
    estimate = k / n
    result = binomtest(k=k, n=n)
    wilson = result.proportion_ci(confidence_level=confidence, method="wilson")
    exact = result.proportion_ci(confidence_level=confidence, method="exact")

    # 3. Preserve task/init/seed metadata for cluster-aware follow-up.
    clusters = [(ep["task_id"], ep["init_id"], ep["seed"]) for ep in valid]
    return {"k": k, "n": n, "estimate": estimate,
            "wilson": (wilson.low, wilson.high),
            "exact": (exact.low, exact.high), "clusters": clusters}
```

实现要点：`success` 是 episode-level predicate，`valid=false` 的原因必须写入 manifest；`wilson` 和 `exact` 不是“两个模型结果”，而是同一 (k/n) 的两种不确定性表达；`clusters` 为后续 task/seed/init 相关性分析保留索引。不要把这个函数扩展成自动删除失败 episode 或自动选择最佳 checkpoint。

## 8. 本地项目映射与统计边界

| 项目材料 | 可用于面试的知识 hook | 不能声称 |
| --- | --- | --- |
| UWM/LIBERO | fixed-pruned-init、5-step warmup、5 task × 50 rollout；`186/250=0.744` 可计算 naive Wilson `[0.686,0.794]` 和 exact `[0.685,0.797]` | 本地已有 250 条 raw episode、cluster-robust CI，或与 UWM Table II OOD protocol 直接可比 |
| OpenPiVLA | archive summary 的 `97.4%` 可用来说明“没有分母和 lineage 就不能算 CI” | 不知道 (n)、trial/seed/init、episode records 时计算统计显著性或绑定 current Qwen checkpoint |
| OPD/VLM grounding | 10,000-row raw-holdout 可按 box/point/text pool 单独定义 binary metric 的统计单元 | 将 Box IoU、Point Hit、Text exact 混成 robot rollout success；把 row count 自动当成独立 episode |

UWM 的 186/250 是用户确认的远端最终汇总；OpenPiVLA 的 97.4% 是 archive-summary-only；OPD 的 10k 是静态视觉评估。三者证据等级和统计单元不同，不能只看百分比排序。[4][5][8]

## 9. Trade-off、bad case 与面试追问

### 9.1 Trade-off

- Wilson 通常比 Wald 更稳健，Clopper–Pearson 更保守；面试时说明选择理由，不把某一种说成唯一正确。
- 提高置信度或缩小 margin 会增加 (n)；未知 (p_0) 取 0.5 更安全但可能过度采样。
- 增加每个 task 的 episode 数能减小条件估计误差，但不能替代更多 task、seed 或 init 覆盖。
- fixed-n CI 适合一次性评估；连续上线监控要切换到 sequential/always-valid 方案。

### 9.2 高概率 bad case

1. 把 action step、帧或多条标注当成独立 rollout。
2. 只报 `186/250`，不报 task/init/seed、失败排除和 success predicate。
3. 用 Wald 区间处理 0/20 或 20/20。
4. 把正态近似样本量 385 写成所有 VLA benchmark 的固定规则。
5. 看到 CI 过阈值就停止，却没有预注册 stopping rule。
6. 将 OPD 的 10k 静态样本、OpenPiVLA 的 97.4% archive summary 与 UWM episode success 混为一谈。

### 9.3 高压追问

1. 为什么 50 rollouts/task 不能自动说明结果稳定？
2. 186/250 的 95% Wilson 和 exact 区间分别是多少？哪些假设仍不成立？
3. 如果成功率预估为 0.8、margin 为 ±3%，如何重新规划 (n)？
4. 同一个 task 的 50 次 rollout 为什么可能不独立？如何保守处理？
5. 你会如何证明“超过 0.8”而不是只报 (hat p=0.82)？
6. 中途每 10 次查看一次 CI 后停止，为什么会有统计风险？
7. OpenPiVLA 的 97.4% 为什么不能直接算置信区间？
8. OPD 的 Point Hit@100 和机器人 success rate 在统计上哪里不同？

## 10. 结论与 review 边界

EVAL-003 的核心回答是：先把 episode、success predicate、protocol 和分母冻结，再用 (hat p=k/n) 报点估计；默认同时给 Wilson 与 Clopper–Pearson 区间，zero/all-success 不退化为“概率为 0/1”；样本量由 (alpha)、margin、先验 (p_0)、阈值/功效和 task/seed/init 结构共同决定；固定 (n) 与可选停止必须分开。对 VLA 而言，统计区间只能表达在既定协议下的结果不确定性，不能替代跨 task 泛化、checkpoint lineage、controller safety 或真实机器人证据。

当前 review 保持 `WARN`：官方实现和公式已经冻结，知识正文与一张原子题卡完成；UWM 的 raw episode/cluster-aware CI、OpenPiVLA 的 97.4% 分母与 lineage、OPD 的 metric-specific independence 仍未闭合。题卡保持 `unseen`；下一步是真实口述或补齐统计 artifacts，不创建或升级 coaching state。

## References

1. SciPy `scipy.stats._binomtest.py@v1.16.3`：[`binomtest` / `proportion_ci`](https://github.com/scipy/scipy/blob/56e567e70ccad213d04ab04e7cfe7365562a71f1/scipy/stats/_binomtest.py)。
2. statsmodels `statsmodels/stats/proportion.py@v0.14.6`：[`proportion_confint` / `samplesize_confint_proportion`](https://github.com/statsmodels/statsmodels/blob/40e6a84d26ac74623c6b94b718f0987ef0351c53/statsmodels/stats/proportion.py)。
3. Wilson (1927)、Clopper & Pearson (1934)、Brown, Cai & DasGupta (2001) 与 Newcombe (1998) 的方法比较，见 [EVAL-003 Source Freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。
4. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
5. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. Kerry & Bland, “The Intracluster Correlation Coefficient in Cluster Randomisation,” [DOI](https://doi.org/10.1136/bmj.316.7142.1455)。
7. Johari et al., “Always Valid Inference: Continuous Monitoring of A/B Tests,” [DOI](https://doi.org/10.1287/opre.2021.2135)。
8. [OPD / VLM Grounding Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
