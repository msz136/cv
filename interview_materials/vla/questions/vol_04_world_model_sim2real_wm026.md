# VOL 04 VLA-WM-026 原子题卡：World/Value Auxiliary 与 Action Imitation

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-026  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-026 Knowledge](../knowledge/vol_04_world_model_sim2real_wm026_world_value_auxiliary_action_imitation.html)；来源边界见 [WM-026 Source Freeze](../sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html)。

## world/value auxiliary objective 为什么可能帮助 action imitation？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-026</b> · world/value auxiliary objective 为什么可能帮助 action imitation？</summary>

**面试意图**：判断你能否提出可证伪的表示、value、数据覆盖与梯度机制，并用 matched ablation 证明，而不是说“多任务监督天然更强”。

**30 秒回答**：world 辅助可能让表示保留动作后果与接触，value 辅助编码任务进展，rollout 扩展状态。但标签、mask、梯度或容量错会负迁移。用 action-only、+world、+value、all 的同数据/算力消融，同时看动作、future/value 与闭环；不能从 component loss 或论文推断本地收益。

**机制展开（约 2 分钟）**：共享梯度可写成 g=ga+λw gw+λv gv。world 若对 action swap 敏感，可学习动作后果；value 若校准，可编码任务进展。记录逐层 gradient cosine/norm、role count、mask denominator、normalizer 和 padding。四个 arm 固定 checkpoint、split、updates、compute、controller、horizon、denominator，再加 shuffled-label 与 stop-gradient control。若辅助 proxy 好但动作/闭环不变，只说明学会辅助任务；WAM 本地 checkpoint、gradient、paired episode 仍缺。

**诊断 / 证据**：保存各 role 的 effective sample/update count、main loss、action/future/value component metric、shared trunk 和 slot-specific gradient。做 repeat baseline、per-dim/per-step action error、action swap/sensitivity、future per-offset error、value calibration/rank、first-failure stage 与 per-task success。若 auxiliary arm 多用 rollout 或 compute，要加同数据/同算力 action-only control。

**项目挂钩**：Cosmos/WAM 可连接 unified slot/routing、world/value rollout 和 direct/planning boundary；UWM 可连接 action-video coupling。WAM inventory 只证明上游机制与 ablation 计划，exact local config、checkpoint、raw metric、gradient、paired episode 和 ownership 缺失。安全说“我能设计验证矩阵”，不能说 world/value 已提升个人策略。

**追问树**：world 目标具体保留哪些信息？怎么证明不是背景 shortcut？value 为什么能提供进展？value label 噪声如何查？gradient cosine 正就一定有益吗？如何匹配 data/compute？为什么加 shuffled-label control？stop-gradient 能区分什么？action MSE 好但 success 不变怎么解释？D 优于 B/C 能否叫 synergy？

**易错点**：把多任务当必然 regularizer；把 Cosmos exact EDM loss 简化成三个 head 相加；只看 component loss；不匹配数据/算力；忽略 role ratio、padding、normalizer、checkpoint selection；把 ablation 计划说成已完成结果。

**危险答案**：说“world/value 一定提升 imitation”“gradient cosine 为正就证明成功率提升”“future 图像清晰说明动作更好”“value loss 低等于闭环成功”“历史 MSE 下降已经证明 auxiliary 有效”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-026 Source Freeze](../sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html)：表示机制、梯度诊断、matched ablation 与负迁移。
2. [Cosmos Policy / WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：shared action/future/value contract 与 metric boundary。
3. [WM-025 Slot / Mask / Loss](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)：exact routing、mask 与 EDM 边界。
4. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：ablation pending 与真实性边界。
5. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)：proxy 与 closed-loop success 分层。
