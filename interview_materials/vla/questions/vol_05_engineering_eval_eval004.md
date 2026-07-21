# VOL 05 Engineering / Evaluation：EVAL-004 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-004`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-004 Paired Init / Seed Evaluation](../knowledge/vol_05_engineering_eval_eval004_paired_init_seed_significance.html)；来源边界见 [Source Freeze](../sources/vol_05_eval004_paired_init_seed_significance_source_freeze.html)。本题不把 UWM 不同协议 aggregate、OpenPiVLA 无分母 97.4% 或 OPD 10k 静态 rows 包装成 paired rollout evidence。

## Paired Init / Seed Evaluation 与显著性

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-EVAL-004</b> · 怎样用 paired init/seed evaluation 判断两个 VLA checkpoint 的差异是否显著？</summary>

**面试意图**：判断你能否从合法 pairing、discordant table 和 paired inference，一路讲到 seed 层级、invalid pairs、power、selection/multiplicity 与实际收益，而不是拿两个成功率直接做独立检验。

**30 秒回答**：先按同 task、init snapshot、protocol 配 A/B，统计四格表，效应 Δ=(n10−n01)/n；exact McNemar 只看 n10+n01。CI/bootstrap 保持配对，training seed 是顶层 replicate；另预注册 invalid pair、MDE、holdout 和 multiplicity。

**机制展开（约 2 分钟）**：same seed≠same init，需核对 init hash/首帧与 protocol。null 下 n10 | d~Binomial(d,0.5)，d=n10+n01；SciPy pair 内交换用 `samples`，bootstrap 用同一 indices 和 `paired=True`。episode 不替代 training runs，power 取决于 discordant rate。报告四格表、effect/paired CI/p、exclusions 和 practical threshold；validation 选 checkpoint，holdout 检验，多 task/horizon 用 primary endpoint 或 Holm/层级。

**诊断 / 证据**：冻结 `pair_id/task/init_snapshot_hash/env_seed/rollout_seed/training_seed/A-B checkpoint/protocol hash/A-B success/valid/exclusion_reason`。先查 key 唯一、双臂 init/protocol 一致和缺臂，再构四格表；测试 `d=0`、极少 discordance、单臂 crash、重复 init、同 seed 异 init及 task cluster。输出 attempted/valid/excluded、四格表、Δ/CI/p、alpha/MDE/multiplicity family、analysis seed 和 holdout id。

**项目挂钩**：UWM `186/250` fixed-pruned-init 与 `232/250` reset-style 协议不同，且无 250 条 matched raw pairs，不能做 McNemar或称显著 uplift；OpenPiVLA `97.4%` 缺 denominator/trial/seed/init/lineage，不能入 paired test；OPD 10k 是静态 row pool，重复 image/path 要按 cluster 处理，不能叫 robot rollout。

**追问树**：为什么 same seed 不等于 same init？n11/n00 为什么不进入 McNemar？`d=0` 能否证明等价？`samples` 与 `pairings` 有何区别？paired bootstrap 怎样写？为什么 10k episodes 不能替代多个 training seeds？power 为什么依赖 discordant rate？单臂 crash 怎么处理？选 checkpoint 后为何要新 holdout？多 task/horizon 如何控制 multiplicity？p<0.05 是否足够上线？

**易错点**：由两个 aggregate 反推 pairing；独立 bootstrap 两臂；SciPy permutation type 写成 `pairings`；把 frame/重复 episode 展开成 iid；混淆四类 seed；事后删除单臂异常；只报 p-value；用同一 grid 选择并检验；从最亮眼 task 下总体结论。

**危险答案**：说“同 seed 就天然配对”“A 74.4%、B 92.8%，所以显著”“总 n 很大就有 power”“p<0.05 就证明提升有用”“崩溃 episode 删掉即可”或“每个 episode 都算一个 training seed”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-004 知识页](../knowledge/vol_05_engineering_eval_eval004_paired_init_seed_significance.html)：pairing、四格表、McNemar、paired resampling、seed 层级、power 与 multiplicity。
2. [EVAL-004 Source Freeze](../sources/vol_05_eval004_paired_init_seed_significance_source_freeze.html)：McNemar/Newcombe、statsmodels/SciPy、RL seeds 与 `rliable` frozen sources。
3. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：186/250 与 232/250 的 protocol 不可比及 raw pair 缺口。
4. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：97.4% denominator、trial/seed/init 与 lineage 缺口。
5. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：10k 静态 metric pool 与 repeated image/path cluster 边界。
