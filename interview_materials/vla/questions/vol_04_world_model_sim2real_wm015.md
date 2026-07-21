# VOL 04 World Model / Sim2Real：WM-015 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-WM-015`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[WM-015 UWM Video–Action Coupling](../knowledge/vol_04_world_model_sim2real_wm015.html)；来源边界见 [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html) 与 [独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)。本题只讲 frozen upstream 方法/代码，不绑定用户 UWM 成绩或个人原创。

## UWM 如何统一 Video 与 Action Diffusion

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-015</b> · UWM 如何把 video diffusion 与 action diffusion 放进统一预训练框架？</summary>

**面试意图**：判断你能否解释 robot/action-free tuple、共享 token transformer、独立 timestep、sampling mode 与 loss/mask 边界，而不是只说“视频和动作一起训练”。

**30 秒回答**：UWM 把加噪 action 与未来视频 latent 放进共享 DiT，用独立 timestep 预测两路 noise。机器人样本监督两路；无动作视频只把 action timestep 置高噪声，frozen action MSE 未 mask。固定一侧可切 policy、forward、inverse 或 joint。

**机制展开（约 2 分钟）**：当前观测先编码为 condition；action 经 MLP、未来视频经 3D patchifier，与 registers 进入共享 AdaLN blocks，模型预测两路 noise，loss 是 action/video 全张量 MSE 之和。两路 timestep 独立：给 clean action、迭代 video 是 forward；给 clean future、迭代 action 是 inverse；将另一支固定高噪声可取 marginal；两支同时迭代是 joint。`action_mask` 只改 action_t，不证明视频样本没有 action gradient。

**诊断 / 证据**：核对 frozen commit、`action_len/action_dim`、camera/history/future shape、scheduler endpoint、action/video timestep、token slice、loss reduction、normalizer、checkpoint manifest 与 validation metric。做 action-free sample gradient、显式 masked-loss A/B、action perturbation、forward/inverse/joint shape、denorm/controller roundtrip 和 closed-loop paired test；image/action MSE 只能作 conditional proxy。

**项目挂钩**：UWM/LIBERO 项目可讲 action/history/normalizer/checkpoint/rollout protocol 的核对，以及 fixed-pruned-init、reset-style 与 DataLoader stall 的证据边界；不能把上游 shared diffusion 说成个人原创，也不能用 74.4%/92.8% 证明本题机制。Cosmos/WAM 另有 action/future/value 语义，不能与 UWM 两分支混写。

**追问树**：为什么独立 timestep 能切换 inference mode？action-free video 为什么不等于 action loss 为零？共享 blocks 与两个独立 head 有何区别？`timesteps[0]/[-1]` 为什么要绑定 scheduler 版本？action_len=16 是方法常数吗？image MSE 好但 success 不变先查什么？怎样证明 video data 帮助 policy？UWM 与 Cosmos/WAM 的 head/loss 有何差异？

**易错点**：说成视频 backbone 外挂 action head；把 action mask 当 loss mask；忽略 action-free gradient；把 endpoint 当固定物理语义；把 16/7D 当方法常数；用 proxy MSE 替代 closed-loop success；把 UWM 和 Cosmos 三头拼成同一实现。

**危险答案**：说“视频没有 action，所以 action loss 自动为零”“两个 timestep 只是任务标签”“MSE 降低就证明机器人成功率提升”“UWM 的 action 长度永远是 16”或“本地成绩证明了上游架构有效”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-015 知识页](../knowledge/vol_04_world_model_sim2real_wm015.html)：数据合同、双 timestep、共享网络、sampling mode、mask 与项目边界。
2. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)：官方项目页与 frozen repo 的 claim-to-code。
3. [UWM 独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)：raw source SHA 与关键断言复核。
4. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：项目成绩、protocol、checkpoint 与 ownership 边界。
