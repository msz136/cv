# VOL 04 VLA-WM-027 原子题卡：Auxiliary Negative Transfer 与 Gradient Conflict

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-027  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-027 Knowledge](../knowledge/vol_04_world_model_sim2real_wm027_auxiliary_negative_transfer_gradient_conflict.html)；来源边界见 [WM-027 Source Freeze](../sources/vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html)。

## 什么时候 auxiliary world/value 会负迁移，如何识别 gradient conflict？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-027</b> · 什么时候 auxiliary world/value 会负迁移，如何识别 gradient conflict？</summary>

**面试意图**：判断你能否区分“局部梯度冲突”和“已确认负迁移”，并按数据合同、梯度诊断、优化器干预、闭环证据的顺序定位问题。

**30 秒回答**：负迁移指同数据、算力、协议下，加入辅助目标后 action/闭环比 action-only 稳定变差；负 cosine 只是局部信号。用 exact loss 记录逐层 cosine、norm ratio，先查标签、mask、padding、role 比例。方向冲突试 PCGrad，尺度失衡试 GradNorm，最终靠多 seed 闭环对照证实。

**机制展开（约 2 分钟）**：令 ga 为 action 梯度、gu 为辅助梯度；cos<0 是 PCGrad conflict，ga·gjoint<0 只表示该步一阶上伤害 action，不证明最终负迁移。逐层/角色记录 cosine、weighted norm、valid target；AMP 先 unscale，DDP 用全局梯度。PCGrad投影负方向，GradNorm按相对训练速率调权重；label、mask、domain、capacity 错则先修 contract。最后 matched 比较 action-only/+world/+value/all 的 action、auxiliary、per-task success、paired episode 与 seed/CI。

**诊断 / 证据**：先做 role matrix、exact target-mask loss、empty-mask fail-fast、action/value label audit、terminal-padding A/B 和 normalizer round-trip；再画 layer×role gradient matrix、norm ratio、conflict duration 与 joint-update alignment。AMP 先 unscale，DDP/FSDP 统计全局 gradient 或 exact sharded dot/norm，不平均 rank cosine。gradient 变好但 action/闭环不变，只能说优化几何改变。

**项目挂钩**：Cosmos/WAM 的主项是 unified latent EDM loss，日志 action/future/value L1/MSE 不天然等于三条训练梯度。WAM inventory 仍缺 exact local config/checkpoint、gradient trace、matched objective arms、跨 seed episodes 与 ownership；单 episode trace、单样本 future proxy 不能证明 negative transfer。安全说“我能设计 audit”，不能说“已用 PCGrad/GradNorm 修好项目”。

**追问树**：负 cosine 为什么不等于负迁移？为什么要看 ga·gjoint？逐层统计为何优于全模型平均？不同 routed batch 的 cosine 怎样解释？AMP/DDP 下怎么测？PCGrad 的投影公式是什么？随机 task order 有何影响？GradNorm 的 relative inverse training rate 怎么算？GradNorm 能消除方向冲突吗？如果 value 是噪声任务，GradNorm 会怎样？如何做 matched closed-loop？

**易错点**：从一次负 cosine 宣布根因；用 component metric 代替 exact training gradient；平均各 rank cosine；AMP 未 unscale；只改 loss weight 不查 valid target；把 PCGrad 与 GradNorm 当同一种方法；gradient 图改善就宣称 success 提升。

**危险答案**：说“cosine<0 就证明负迁移”“PCGrad 保证多任务更好”“GradNorm 会自动删除坏任务”“action/future/value 日志 loss 可直接当三条 official gradient”“我已经在 WAM 用 gradient surgery 提升成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-027 Source Freeze](../sources/vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html)：定义、诊断合同、PCGrad/GradNorm 与项目边界。
2. Yu et al., [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782v4)。
3. Chen et al., [GradNorm](https://arxiv.org/abs/1711.02257v4)。
4. [WM-025 Cosmos/WAM Slot / Mask / Loss](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)：exact loss、routing 与 metric 边界。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：本地 gradient/ablation/ownership 缺口。
