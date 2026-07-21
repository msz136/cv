# VOL 04 VLA-WM-023 原子题卡：Open-loop Plan 与 Receding-horizon Replanning

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-023  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-023 Knowledge](../knowledge/vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)；来源边界见 [WM-023 Source Freeze](../sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.html)。

## open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-023</b> · open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？</summary>

**面试意图**：判断你是否区分 prediction horizon \(H\)、execution horizon \(K\)、observation age、query frequency、queue 和闭环证据，而不是只背 action chunk 默认值。

**30 秒回答**：先区分 H 与 K：H 是预测多远，K 是连续执行多久。open-loop 摊薄推理，但 K 越大 action age 和扰动风险越高；receding horizon 执行前缀后重规划，鲁棒但队列与 latency 压力大。固定 checkpoint、reset、controller，做 H/K、延迟和扰动 sweep；公开默认值不是本地结果。

**机制展开（约 2 分钟）**：K 越大，action age≈L+jΔt，能摊薄 inference，却更容易 stale；若 L>KΔt 会 queue underflow。K 越小反馈快，但 chunk switch、通信和 jitter 增加。H 决定候选未来，不等于反馈；长 H 可能扩大 model error、搜索或 denoising 成本。同步、异步和 event-trigger 都要记 timestamp、版本、fallback。固定 checkpoint、normalizer、reset、controller，扫 K、再扫 H，报告 p95 latency、action age、恢复延迟、first failure 和 per-step success。

**诊断 / 证据**：至少保存 observation/policy/controller timestamps、chunk id、model revision、queue depth、replan reason、fallback、termination reason；做 \(K\in\{1,4,8,16\}\) 或任务适配 sweep，固定 \(H\) 后再反向扫 \(H\)，并注入 0/1/2/4 个 control-step delay。Diffusion Policy 支持 \(T_o/T_p/T_a\) 的概念区分，PlaNet 支持每次返回 first action 的滚动规划，ACT 支持 chunk overlap/temporal ensemble；这些公开机制不等于本地 closed-loop 曲线。

**项目挂钩**：Cosmos/WAM audit 中 LIBERO 是 16×7、默认执行 16 步，RoboCasa 是 32×7、默认执行前 16 步再 requery；UWM/LIBERO 可挂 fixed init、horizon、normalizer 和 episode protocol，Robot Harness/OpenPiVLA 可挂 action queue、controller、timeout 和 trace。当前没有 WM-023 的本地 planning runtime、paired \(H/K\) 曲线、扰动 bundle 或 ownership artifact，安全表达是“我能设计并审计 horizon/latency contract”，不声称已经证明缩短 chunk 提升鲁棒性。

**追问树**：\(H\) 和 \(K\) 为什么不能合并？\(K=1\) 是否一定最好？如何把 steps 换算成秒？同步和异步 replan 的 race condition 是什么？如何定义 action age？queue underflow 怎么 fallback？为何 \(H\) 越长可能越差？如何做 latency injection？chunk switch jitter 如何量化？什么时候用 event-trigger？公开 16-step open-loop 能否写成本地结果？

**易错点**：把 open-loop 说成完全没有低层反馈；把 \(H\) 当执行长度；只看平均 FPS 不记 p95 action age；把 \(K\) 越小等同于一定更鲁棒；忽略 queue、controller、normalizer、reset、denominator；把 Diffusion Policy/ACT/Cosmos 默认值当成自己的实验结论。

**危险答案**：说“每步重规划总是最好”“chunk 越长吞吐和成功率都更高”“只要 GPU FPS 高就没有 latency 问题”“公开 16 步 open-loop 就证明我项目鲁棒”“\(H\) 越大一定更有远见”“action age 不需要记录”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-023 Source Freeze](../sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.html)：时间轴、\(H/K\)、latency 与 matched sweep。
2. [PlaNet / World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)：latent planning、first action、receding horizon 与长 horizon 风险。
3. [Diffusion Policy](https://arxiv.org/abs/2303.04137)：\(T_o/T_p/T_a\)、action execution horizon 与 responsiveness。
4. [ACT](https://arxiv.org/abs/2304.13705)：action chunking 与 temporal ensembling。
5. [Cosmos Policy / WAM claim-to-code audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：公开 chunk/open-loop/requery 协议和本地证据边界。
