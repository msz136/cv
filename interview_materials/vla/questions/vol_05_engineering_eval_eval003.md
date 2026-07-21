# VOL 05 Engineering / Evaluation：EVAL-003 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-EVAL-003`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-003 Success Rate / Confidence Interval](../knowledge/vol_05_engineering_eval_eval003.html)；来源边界见 [Source Freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。UWM 186/250 只到 user-confirmed/protocol-limited，OpenPiVLA 97.4% 缺分母和 raw episodes，OPD 10k 是 metric-specific raw-holdout；三者不能混成同一种独立 rollout success。

## Success Rate、置信区间与最小 Rollout 数

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-003</b> · VLA 成功率怎样报置信区间，最少要跑多少个 rollout？</summary>

**面试意图**：判断你能否把 episode-level 统计单元、Wilson/exact 区间、sample-size planning、task/seed/init 相关性和 stopping rule 组织成可审计评估，而不是背一个固定 rollout 数。

**30 秒回答**：先冻结 episode、task/init/seed、success predicate 和停止规则，再报 p̂=k/n 与 Wilson/Clopper–Pearson 区间。样本量由置信度、margin、p0 和阈值决定；95%/±5% 最坏 p0=0.5 约需 385 个独立单元。task 聚类会降低有效 n，未知分母的 97.4% 不能算 CI。

**机制展开（约 2 分钟）**：令 Xi∈{0,1}、p̂=k/n；Wilson 适合常规报告，Clopper–Pearson exact 更保守，0/n 或 n/n 也不能说真实 p=0/1。规划精度时 n≥z²p0(1-p0)/ε²，未知 p0 取 0.5；若 task/seed/init 相关，用 DE=1+(m-1)ρ 理解 n_eff≈n/DE，并按 cluster/per-task 复算。普通 fixed-n CI 不能反复查看后可选停止。UWM 186/250 只有 naive interval，OpenPiVLA 97.4 缺 n，OPD 10k 不是 robot episode。

**诊断 / 证据**：冻结 run/episode manifest：checkpoint、processor/normalizer、task/env/init/seed、warmup/horizon/replan/controller/success predicate、episode valid/success/termination、失败排除、stopping rule 和 raw trace。用 SciPy 对同一 k/n 同时报 Wilson/exact，测试 0 success、all success 和阈值边界；检查 per-task count、cluster id、ICC/design effect 或 cluster bootstrap。若持续监测，改用预注册 sequential/always-valid 方法，不重复套普通 95% CI。

**项目挂钩**：UWM fixed-pruned-init 为 5 task×50、186/250；naive Wilson 约 [0.686,0.794]、exact 约 [0.685,0.797]，但缺本地 250 episode 和 cluster-aware evidence，且不能与 Table II OOD protocol 直比。OpenPiVLA archive 97.4% 缺 n/trial/seed/init/lineage，不能算 CI。OPD 10k 是 box/point/text 静态评估池，不能叫机器人 rollout success。

**追问树**：为什么 50 rollouts/task 不自动稳定？Wilson 与 exact 怎么选？0/20、20/20 怎么报？95%/±5% 为什么最坏要 385？如果目标是证明 p≥0.8 怎么设计？同 task rollout 为什么相关？如何做 cluster-aware CI？每 10 次看一次 CI 后停止有什么风险？UWM/OpenPiVLA/OPD 三个数字为什么不能排序？

**易错点**：把 action step 当独立样本；静默删除 env crash；只报百分比；对 0/all success 用 Wald；把 385 当通用常数；忽略 task clustering；反复看 fixed-n CI；把静态 grounding 指标或未知分母汇总当 robot success。

**危险答案**：说“每任务 50 次足够”“97.4% 一定显著”“全成功说明 p=1”“CI 越窄模型越强”“10k raw-holdout 就是 10k rollouts”或“跑到结果稳定再停即可”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-003 知识页](../knowledge/vol_05_engineering_eval_eval003.html)：Bernoulli contract、Wilson/exact、sample-size、cluster dependence、stopping rule 与项目映射。
2. [EVAL-003 Source Freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)：SciPy/statsmodels frozen implementation、方法论文与本地证据边界。
3. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：186/250 的 protocol、user-confirmed 等级与 raw episode 缺口。
4. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：archive 97.4%、formal lineage 和 denominator 缺口。
5. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：10k raw-holdout 的 box/point/text metric-specific 边界。

