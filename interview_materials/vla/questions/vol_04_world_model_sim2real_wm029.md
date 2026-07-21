# VOL 04 VLA-WM-029 原子题卡：Imagined/OOD Value Calibration 与 Pessimism

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-029  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-029 Knowledge](../knowledge/vol_04_world_model_sim2real_wm029_imagined_ood_value_calibration_pessimism.html)；来源边界见 [WM-029 Source Freeze](../sources/vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html)。

## value 在 imagined/OOD state 上为何容易失准，如何做 calibration 或 pessimism？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-029</b> · value 在 imagined/OOD state 上为何容易失准，如何做 calibration 或 pessimism？</summary>

**面试意图**：判断你能否区分 support shift、world/value error、best-of-N selection bias、calibration、uncertainty 与不同保守方法，而不是把 “mean-std” 当万能置信下界。

**30 秒回答**：value 在数据分布训练，却给 imagined OOD 打分；world bias、外推与 best-of-N 高估叠加。先区分 return/Q/成功概率，测校准、排序和 uncertainty-error。LCB 改 scorer，MOPO 惩罚 rollout，CQL 压低 OOD Q；用同候选做 β/N/depth 与闭环对照，std 不是保证。

**机制展开（约 2 分钟）**：dD≠imagined dTπ，value error 可拆成外推与 transition shift；best-of-N 的 argmax(V+error) 会偏向正误差。成功概率测 reliability/ECE/Brier，return 测 bias/rank/coverage/selected regret，并按 support、depth、task 分层。LCB=μ-βσ 只改 scorer，MOPO 惩罚 model rollout，CQL 正则 OOD action Q。Cosmos LCB 是同模型不同 seed/steps、先 clip 后 mean-std、β=1，默认 ensemble off，不是 epistemic bound。

**诊断 / 证据**：审计 return/gamma/horizon/terminal；保存 real-vs-imagined paired future、pre/post-clip value samples、disagreement-error 与 risk-coverage。固定 proposal/world/value checkpoints 和 candidates，对 random/mean/LCB、β、N、depth、oracle replay 做对照，并报告 per-task success、selected regret、latency 和 first-failure。低 global MAE/ECE、低 Bellman residual 或高 rank 都不能单独证明 OOD planning 安全。

**项目挂钩**：Cosmos/WAM value frame 在 [0,1] 不等于成功概率；frozen LCB 是 repeated sampling heuristic，LIBERO/RoboCasa 默认 average/ensemble off。WAM inventory 没有 value labels/predictions、candidate ledger、selector sweep、planning episodes 或 ownership。安全说“我能设计 calibration/pessimism audit”，不能说“已用 CQL/MOPO/LCB 提升 WAM planning”。

**追问树**：为什么 offline value 对 imagined state 不可靠？world error 和 value error 怎么拆？best-of-N 为什么放大高估？ECE 能证明 ranking 吗？return 可否直接做 temperature scaling？ensemble std 何时代表 epistemic？LCB 为什么不是保证？MOPO 与 CQL 分别惩罚什么？Cosmos ensemble 是独立模型吗？clip 后算 std 有什么风险？如何做 fixed-candidate selector A/B？

**易错点**：把 bounded value 当成功概率；把全局 ECE 当 OOD calibration；只看 mean error 不看 top-tail regret；把同模型多 seed 叫 epistemic ensemble；把 CQL/MOPO 公式直接写成 Cosmos exact objective；调 β/N 同时改变 candidates 导致不可比；把支持的 LCB option 说成默认启用。

**危险答案**：说“value 在 [0,1] 就是 calibrated success probability”“ensemble std 天然是置信区间”“LCB 一定下界真实 value”“CQL/MOPO 已用于 Cosmos/WAM”“N 越大 planning 越好”“本地历史 MSE 已证明 value 校准”。

**来源**：[1][2][3][4][5][6]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-029 Source Freeze](../sources/vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html)：失准分解、calibration、PETS/MOPO/CQL/LCB 与项目边界。
2. Guo et al., [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599v2)。
3. Chua et al., [PETS](https://arxiv.org/abs/1805.12114v2)。
4. Yu et al., [MOPO](https://arxiv.org/abs/2005.13239v6)。
5. Kumar et al., [CQL](https://arxiv.org/abs/2006.04779v3)。
6. [Cosmos Policy / WAM Audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html) 与 [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
