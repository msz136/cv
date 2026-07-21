# VOL 04 World Model / Sim2Real：WM-016 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-WM-016`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[WM-016 Joint Objective 知识页](../knowledge/vol_04_world_model_sim2real_wm016.html)；来源边界见 [WM-016 Source Freeze](../sources/vol_04_wm016_joint_objective_source_freeze.html)、[UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html) 与 [Cosmos/WAM Source Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。本题只讲 frozen upstream 方法/代码，不绑定用户项目成绩或个人原创。

## 如何审计 action/video joint objective 的 mask 与 loss

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-016</b> · action/video joint objective 的共享表示、condition、noise schedule 和 mask 应怎样审计？</summary>

**面试意图**：判断你能否把 shared representation、sample routing、condition mask、prediction target、target loss mask 和 reduction 分开，而不是看到一个 `mask` 就断言某项 loss 被排除。

**30 秒回答**：冻结 config，核对 target、mask 和 reduction。UWM 是双 timestep shared DiT，`action_mask` 只改 timestep；Cosmos/WAM 是 latent-slot EDM，condition mask 不等于 loss mask。用 paired ablation 判断收益。

**机制展开（约 2 分钟）**：检查 route、clean condition、timestep/sigma、prediction target 和 reduction。UWM 的 action/video MSE 全张量相加；action-free 的 `action_mask` 只把 timestep 推到最大步，不等于 action loss 为零。Cosmos/WAM 的 action/future/value 是 latent slots，target-mask 与 multiplier 要查调用点。做 mask A/B、gradient、paired fine-tune，同时看 component loss 与 success。

**诊断 / 证据**：保存 route、mask 原值、shape、dtype、normalizer、timestep/sigma、prediction target、reduction denominator、checkpoint SHA 和 seed；比较 frozen 与显式 target-mask 的 loss/gradient/参数更新，并同时报告 action sensitivity、future error、success 和 failure trace。

**项目挂钩**：UWM/LIBERO 可讲 action-free tuple、normalizer、checkpoint、reset/init 和 rollout protocol 的核对；WAM 可讲 latent routing、value/world/policy 角色和 0-success 诊断。不能把 UWM shared DiT 或 Cosmos/WAM routing 说成个人原创，也不能用离线 MSE 或项目页数字证明 joint objective 的因果收益。

**追问树**：condition mask 和 target loss mask 有何不同？为什么 UWM action-free 不等于 action loss 为零？epsilon-MSE 与 EDM (x_0) loss 能直接比较吗？如何证明 video/value auxiliary 真正提升 policy？若 component loss 降但 success 不变先查什么？如何做 gradient cosine 或 action perturbation？

**易错点**：把 `mask=1` 统一解释成“屏蔽”；把 route 当 loss mask；忽略 prediction target 与 reduction；把 UWM 与 WAM 拼成一个三头模型；用 action/future/value 日志列替代主 loss；用 proxy MSE 代替 paired closed-loop success。

**危险答案**：说“所有 mask 都是 loss mask”“UWM 视频样本 action loss 自动为零”“EDM 的 L1 和 UWM 的 MSE 可以直接排序”“joint loss 降低就证明机器人成功率提升”或“上游 routing 是我的设计”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-016 知识页](../knowledge/vol_04_world_model_sim2real_wm016.html)：joint objective、mask、prediction target、reduction 与 paired ablation。
2. [WM-016 Source Freeze](../sources/vol_04_wm016_joint_objective_source_freeze.html)：UWM/Cosmos/WAM claim-to-code 对照与待验证队列。
3. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)：shared DiT、dual timestep、action-free semantics 与当前 loss 边界。
4. [Cosmos/WAM Source Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：latent slot、EDM、condition/target mask、routing 与 value/world/policy 角色。
5. [UWM/WAM evidence inventories](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：个人项目的 checkpoint、protocol、ownership 与指标证据边界。
