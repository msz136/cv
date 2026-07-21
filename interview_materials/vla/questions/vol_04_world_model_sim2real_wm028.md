# VOL 04 VLA-WM-028 原子题卡：Routing、Slot Mask 与 Loss Weight

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-028  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-028 Knowledge](../knowledge/vol_04_world_model_sim2real_wm028_routing_slot_mask_loss_weight.html)；来源边界见 [WM-028 Source Freeze](../sources/vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html)。

## sample routing、slot mask 与 loss weight 怎样避免 action/world/value 互相污染？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-028</b> · sample routing、slot mask 与 loss weight 怎样避免 action/world/value 互相污染？</summary>

**面试意图**：判断你能否把数据角色、模型可见信息、反向目标、padding 有效性和优化权重分层，而不是把所有问题都归结成“调 loss coefficient”。

**30 秒回答**：routing 定角色，condition 定可见信息，target/valid 定反向，weight 只缩放梯度。用 one-hot、slot 真值表、padding 单测防串线，看 gradient share。Cosmos 隔离 mask 默认关闭，张量 mean 使 slot 数成为隐式权重；核对 config/denominator 后做闭环对照。

**机制展开（约 2 分钟）**：审计 role、condition、target/valid、weight/reduction；metric 只管日志。有效影响由 role 概率、active slot、noise weight、multiplier、denominator 决定。隔离模式要求 target 属于该 role 且不作 clean input，valid 排除末端重复。Cosmos 隔离 flag 默认 false、action multiplier=1，mask 后仍对完整 BCTHW mean；value-mask flag 存在“构造但未进入 apply 条件”的 WARN。最后对照 joint、isolated、valid、per-role normalization 和 ratio/weight。

**诊断 / 证据**：保存 resolved config、role histogram、source/token/active-slot count、四张 mask、loss numerator/denominator、noise-weight exposure、per-role pre-clip gradient。单测包括 role one-hot、mask truth table、no-target-leak、empty-target fail-fast、padding invariance、multiplier monotonicity 和单卡/多卡 parity。component L1/MSE 只做 metric，不能证明 target mask 生效。

**项目挂钩**：Cosmos/WAM 可映射 demo/world/value role、clean condition、optional target mask 与 action multiplier。WAM inventory 没有 local resolved flags、mask dump、role/denominator/gradient trace、paired episodes 和 ownership；CoffeePressButton 单 episode 不能证明训练污染。安全说“我能设计合同与验证矩阵”，不能说“已调好 50/25/25 或已消除污染”。

**追问树**：condition mask 和 target mask 有何区别？valid mask 为什么独立？metric mask 能证明什么？50/25/25 是 batch 事实吗？为什么 slot 数是隐式权重？full-tensor mean 与 active-count mean 差什么？target 能否同时 clean-conditioned？empty mask 为什么危险？如何测 observed gradient share？为何 weight 修不了 label/mask bug？怎样做 distributed parity？

**易错点**：复用一张 mask；把 mask=1 一律解释为 target；只读 sampling config 不看 observed share；忽略 full-tensor denominator；把 component metric 当训练 objective；看到 flag 名就断言生效；把推荐 valid mask/per-role normalization 写成上游或个人已实现。

**危险答案**：说“把三个 loss weight 调成 1:1:1 就不会污染”“Cosmos 默认严格隔离三种目标”“50/25/25 每个 batch 都成立”“target mask 乘上后天然按有效元素归一化”“我已经用 mask/weight 提升了 WAM 成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-028 Source Freeze](../sources/vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html)：五层合同、frozen defaults/reduction、测试矩阵与 WAM 边界。
2. [Cosmos Policy / WAM Claim-to-Code](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：routing、condition、target-mask branch 与 exact training path。
3. [WM-025 Slot / Mask / Loss](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)：slot layout 与主 loss/component metric 边界。
4. [WM-027 Negative Transfer](../knowledge/vol_04_world_model_sim2real_wm027_auxiliary_negative_transfer_gradient_conflict.html)：contract-first 与 gradient share。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：local config/mask/gradient/ownership 缺口。
