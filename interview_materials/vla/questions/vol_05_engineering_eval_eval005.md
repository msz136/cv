# VOL 05 Engineering / Evaluation：EVAL-005 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-005`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-005 Aggregation](../knowledge/vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)；来源边界见 [Source Freeze](../sources/vol_05_eval005_aggregation_estimand_source_freeze.html)。本题不把 UWM summary 算术、OpenPiVLA equal-suite archive average 或 OPD 异构静态指标升级为新的综合成绩。

## Macro / Micro / Per-task / Weighted Aggregation

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-005</b> · 多 task VLA 评估中 macro、micro、per-task 和 weighted success 应怎样选择与报告？</summary>

**面试意图**：判断你能否先定义目标总体、task/suite/run 层级和共同权重，再处理不平衡分母、missingness、cluster uncertainty 与项目指标边界，而不是背四个术语。

**30 秒回答**：先报每 task 的 k/n/CI。macro 按 task 等权；micro 按 n_t 加权；weighted 用预注册部署/风险权重。A/B 必须用同一 task 集和权重，并报告 coverage、missing/exclusion 与 run/task/init-aware CI；不同 metric 或 protocol 不合成总分。

**机制展开（约 2 分钟）**：p_t=k_t/n_t，macro=mean_t p_t，micro=Σk_t/Σn_t=Σ(n_t/Σn)p_t，weighted=Σw_t p_t。等 n 时 macro=micro 仅是代数巧合；分母不平衡时 micro 可能被实验预算支配。多 suite 要区分 equal-suite 与 equal-task；training seed 是顶层 replicate，固定 task set 重采样 runs，推广到 task population 才考虑 task bootstrap。缺 task 不得各自重归一化，paired comparison 先算 A−B 再用共同 weights；IQM/profile 是补充，不替代 per-task 表。

**诊断 / 证据**：冻结 suite/task registry、revision、protocol/scorer hash、planned/attempted/valid n、k、exclusion、training seed、init cluster 和三套权重。检查 macro/micro 手算、权重和为 1、weight coverage、缺 task、不同 task 数、同名 task version drift、两模型 weights 是否一致；按 top-level run 与 task/init strata bootstrap，并保存 resampling seed。

**项目挂钩**：UWM 五 task 各 50 次，使 final summary 的 macro=micro=0.744，但缺 raw episodes且旧 report 的 book_caddy 42/50 与 final 44/50 不能混；OpenPiVLA 97.4 只是四 suite rows 的等权平均，缺 per-task denominator/lineage；OPD box/point/text metric 不同，不能按 10k rows 合成总准确率。

**追问树**：macro/micro 的隐含权重？为什么等 n 才相等？怎样出现 Simpson-style reversal？equal-suite 与 equal-task 差在哪？deployment weights 从哪来？training seed 怎样聚合？fixed tasks 与 task population 的 bootstrap 有何区别？缺 task 能否重归一化？IQM 是什么 estimand？safety task 能否被平均？三个项目当前各能报什么？

**易错点**：只报 average；把 rollout budget 当部署频率；A/B 使用不同 weights；各自删除 missing task；把 episode 展开替代 training runs；把 IQM 叫 macro；跨 suite version、scorer、box/point/text 或 simulator/real protocol 混分。

**危险答案**：说“macro 一定公平”“micro 样本多所以一定更准”“两模型各算 overall 再比较即可”“缺 task 删掉重算”“97.4 就代表所有 LIBERO tasks”“10k 行可以直接算总成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-005 知识页](../knowledge/vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)：estimand、公式、层级、missingness、uncertainty 与项目映射。
2. [EVAL-005 Source Freeze](../sources/vol_05_eval005_aggregation_estimand_source_freeze.html)：Agarwal/rliable、LIBERO/OpenPI frozen sources 与 arithmetic/evidence boundary。
3. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：五 task final summary、旧/新版本冲突与 raw episode 缺口。
4. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：四 suite archive table、97.4 equal-suite arithmetic 与 lineage/denominator 缺口。
5. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：box/point/text pool、by-format/by-pool 与 image-cluster 边界。
