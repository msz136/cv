# VOL 04 World Model / Sim2Real：WM-018 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-WM-018`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[WM-018 Prediction Horizon](../knowledge/vol_04_world_model_sim2real_wm018.html)；来源边界见 [WM-018 Horizon Source Freeze](../sources/vol_04_wm018_prediction_horizon_source_freeze.html)、[Diffusion Policy Audit](../sources/vol_03_diffusion_policy_claim_to_code.html)、[ACT Audit](../sources/vol_03_act_claim_to_code.html) 与 [UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。本题只讲 horizon/replan contract，不绑定用户项目强 claim。

## Prediction horizon 过短或过长有什么影响

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-WM-018</b> · prediction horizon 过短或过长如何影响可控性、细节与训练稳定性？</summary>

**面试意图**：判断你能否拆开 observation、prediction、execution、replan 和 imagination horizon，并把 step 数换成物理时间和闭环证据。

**30 秒回答**：拆开历史、预测、执行、重规划和想象五条时间轴。短 horizon 易训但缺长期结构；长 horizon 增强 coherence 却放大 rollout error、stale action 和延迟。用 matched sweep 看 per-offset error、latency 和 success。

**机制展开（约 2 分钟）**：Diffusion Policy 分 (T_o,T_p,T_a)，ACT 的 chunk (H) 也不必等于 replan；Cosmos 可预测 32 步但执行前 16 步，UWM `action_len=16` 是 config。短 horizon target 近、计算小，却可能缺接触和长时序；长 horizon 结构更强，却增加 compounding/OOD、显存和 stale action。固定 checkpoint、data、Hz、normalizer、reset、protocol，扫 prediction/execution/replan，并看 per-offset error、action age、step-time、success 和 failure offset。

**诊断 / 证据**：记录 timestamp、control frequency、action repeat、valid target count、chunk/replan、inference p50/p95、open-loop traces、recovery time 和 success predicate；不能只看平均 MSE。

**项目挂钩**：UWM/LIBERO 可讲 `action_len`、history/future、normalizer、reset 和 rollout protocol；WAM 可讲 LIBERO/RoboCasa chunk/execution 差异。OpenPiVLA 的 horizon/replan 必须回到 config、checkpoint、inference loop 和 eval summary；公开 ACT/Diffusion Policy 配置不能替代个人事实。

**追问树**：prediction horizon 和 execution prefix 有何区别？为什么 16 steps 不是通用常数？replan=1 是否总是更好？想象 horizon 过长怎样放大 value bias？如何设计 horizon sweep？chunk 后半段漂移先查什么？

**易错点**：把 horizon 当执行步数；忽略 control Hz；把 chunk 内 open-loop 当整条 episode open-loop；把 one-step MSE 当 long-rollout 证据；把论文 warm-start 写成 frozen repo 默认；只比较平均 success 不看 latency 和 failure offset。

**危险答案**：说“horizon 越长越强”“16 就是所有 VLA 的执行长度”“每步 replan 一定最好”“one-step loss 下降证明长 horizon 可控”或“公开 recipe 就是我的项目配置”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-018 知识页](../knowledge/vol_04_world_model_sim2real_wm018.html)：五条时间轴、trade-off、物理时间与 matched sweep。
2. [WM-018 Horizon Source Freeze](../sources/vol_04_wm018_prediction_horizon_source_freeze.html)：Diffusion Policy/ACT/Cosmos/UWM horizon contract。
3. [Diffusion Policy Audit](../sources/vol_03_diffusion_policy_claim_to_code.html)：(T_o/T_p/T_a)、replan 和 warm-start 边界。
4. [ACT Audit](../sources/vol_03_act_claim_to_code.html)：chunk horizon、query frequency 与 temporal aggregation。
5. [Cosmos/WAM 与 UWM Audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：chunk/execution 与 UWM action/history 配置边界。
