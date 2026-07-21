# VOL 04 VLA-WM-021 原子题卡：Dreamer Imagination Actor/Critic 与 Model Bias

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-WM-021`  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[WM-021 Knowledge](../knowledge/vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.html)；来源边界见 [WM-021 Source Freeze](../sources/vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)。

## Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-021</b> · Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？</summary>

**面试意图**：判断你能否把 posterior 起点、prior rollout、return、actor/critic、梯度边界和 dream/real 证据分开。

**30 秒回答**：从 posterior 起点，用 actor+prior 想象 latent，按 lambda-return 更新 actor/critic。model bias 使 actor 利用 OOD，dream reward 高而真实失败。做 horizon、uncertainty 和 imagined/real 对照，不只看 dream return。

**机制展开（约 2 分钟）**：posterior 只校准 replay 起点，prior 不读未来；actor 选动作，critic 估计回报，lambda-return 混合 reward、continuation、discount 与 bootstrap。stop-gradient、horizon 和 loss routing 依赖实现。模型误差随 horizon 累积，actor 可能 exploit OOD；比较 imagined return、open-loop、action sensitivity 和 sim/real trace，并用 replan、uncertainty 或 pessimistic value 限险。

**诊断 / 证据**：固定 checkpoint、init、task、controller、seed，记录起点、horizon、prefix、reward/continue、value target、gradient routing、normalizer 和分母；做 horizon sweep、imagined/real paired rollout、value calibration 与 action perturbation。dream reward 上升而 real success 不变时，先查 model bias、protocol 和 controller。

**项目挂钩**：UWM/LIBERO 可连接 action/image conditional loss、fixed/reset protocol、normalizer 和 horizon；WAM/Cosmos 可连接 world/value/action slots 与 offline proxy；OpenPiVLA/OPD/Harness 可连接 action schema、mask、scorer 和 episode trace。安全表达是“我能解释并审计 Dreamer-style pipeline”，不把公开 reimplementation、离线 MSE、proxy 或历史 0-success 写成个人 actor/critic 结果。

**追问树**：为什么不能每步喂真实 observation？critic target 是否是真实 value？lambda-return 的 (c_t) 是什么？actor loss 会不会更新 world model？imagined reward 高但 real success 低先查什么？horizon 和 execution prefix 如何拆？为什么 uncertainty/disagreement 不是成功保证？DreamerV3 repo 能否称官方代码？

**易错点**：把 posterior 与 prior 混为一谈；把 critic 当 reward/success classifier；把 imagined trajectory 当真实数据；忽略 continuation、terminal mask、bootstrap；说 actor loss 总是更新 RSSM；只看 dream return；把 reimplementation 写成作者官方实现。

**危险答案**：说“Dreamer 不需要真实数据”“critic 预测的就是成功率”“imagined reward 高证明策略有效”“长 horizon 一定更好”“actor 端到端修正了 world model”“DreamerV3 GitHub 就是官方实现”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-021 Source Freeze](../sources/vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)：Dreamer dataflow、return、gradient 与 model-bias 边界。
2. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)：RSSM、imagination actor-critic、model exploitation。
3. [DreamerV3 independent fact review](../sources/vol_04_world_model_foundations_independent_fact_review.html)：frozen reimplementation、`Agent.loss`、`RSSM.imagine` 与梯度边界。
4. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)：imagined/open-loop/simulator/real metric ladder。
