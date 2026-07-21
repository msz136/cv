# VOL 04 VLA-WM-025 原子题卡：Cosmos/WAM Slot、Mask 与 Loss

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-025  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-025 Knowledge](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)；来源边界见 [WM-025 Source Freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。

## Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-025</b> · Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？</summary>

**面试意图**：判断你能否从概率角色讲到 latent layout、sample routing、condition/target mask、EDM reduction 和项目真实性，而不是只说“三个 head 联合训练”。

**30 秒回答**：Cosmos/WAM 在 latent sequence 放 action、future、value，不是三个 head。routing 定角色，condition mask 定 clean 条件，target mask 定反向目标；L1/MSE 只是日志，主项是 EDM MSE。审计 mask 方向、reduction、config；公开结构不是个人设计。

**机制展开（约 2 分钟）**：policy：state→action/future/value；world：state+action→future；value：prefix→return。LIBERO/RoboCasa action 为 16×7/32×7，future 在 t+K，value 扩展成 frame。condition mask 的 1 表示 clean，不能当 loss mask；可选 target mask 按角色保留目标 slot。审计 action/value round-trip、role×slot、non-zero gradient、terminal padding 与 action-only/+world/+value/all A/B；checkpoint 和 paired result 缺。

**诊断 / 证据**：对 demo、world rollout、value rollout、V/Q sample 分别打印 role flag、slot index、condition mask、target mask、sigma、loss denominator 和每类 gradient norm。验证 action normalize→inject→extract→denormalize、value scalar→frame→scalar；检查尾部 clamp/repeated action 与 valid-step mask A/B。component action/future/value L1/MSE 与主 noise-weighted latent loss、direct success、planning score必须分层。

**项目挂钩**：当前 WAM 可以安全说“按 frozen Cosmos contract 梳理/对齐统一 latent sequence、slot、mask、routing、normalizer 与 eval gate，并设计单测/ablation”。工作区缺 exact local config、可加载 checkpoint、gradient trace、paired closed-loop ablation 和 ownership；CoffeePressButton diagnostic 只支持部分 trace/proxy。不能说“我原创三个 head”或“已经证明 world/value auxiliary 提升成功率”。

**追问树**：为什么不是三个独立 head？LIBERO 与 RoboCasa slot/shape 有何不同？action 如何 inject/extract？future index 和 terminal padding 怎么处理？mask=1 是什么意思？condition mask 与 loss mask 差在哪？component L1 是主 loss 吗？target-mask flag 是否默认打开？value frame 如何还原 scalar？routing 错会怎样？如何证明某 slot 有梯度？怎么做 action-only/+world/+value/all 公平 ablation？

**易错点**：把 condition mask 当 attention/loss mask；把 clean slot 当反向目标；只看配置名不查调用点；把 component L1 当主 EDM loss；忽略 normalizer、padding、denominator、shared gradient；把上游 slot/mask 写成个人原创。

**危险答案**：说“Cosmos 就是三个 head 相加”“mask=1 表示这个 slot 参与 loss”“action/future/value L1 加起来就是训练目标”“value 高就证明规划成功”“官方结构是我设计的”“历史 MSE 或成功率已经证明 auxiliary 有增益”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-025 Source Freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)：slot、routing、condition/target mask、EDM loss 与单测。
2. [Cosmos Policy / WAM claim-to-code audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：frozen paper/repo layout 与代码合同。
3. [WM-016 Joint Objective](../knowledge/vol_04_world_model_sim2real_wm016.html)：condition/noise/target/metric mask 分层。
4. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：个人项目真实性和 artifact 缺口。
5. [WM-024 Reward / Value / Success / Termination](../knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)：value/return 与 success 边界。
