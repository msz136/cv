# VOL 04 VLA-WM-022 原子题卡：MPC、CEM/MPPI 与 Best-of-N

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-WM-022`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[WM-022 Knowledge](../knowledge/vol_04_world_model_sim2real_wm022_mpc_cem_mppi_best_of_n.html)；来源边界见 [WM-022 Source Freeze](../sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html)。

## MPC、CEM/MPPI 与 best-of-N 的共同点和差异是什么？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-022</b> · MPC、CEM/MPPI 与 best-of-N trajectory selection 的共同点和差异是什么？</summary>

**面试意图**：判断你能否区分闭环执行范式、proposal optimizer 和 scorer selector，并说明 N/H/K、latency、model/scorer bias 与证据边界。

**30 秒回答**：共同流程是候选生成、评分、选择/更新、执行 prefix。MPC 是 receding-horizon 闭环；CEM 用 elite 更新分布；MPPI 用带噪轨迹和 cost 权重更新；best-of-N 只按 scorer 取 top，可组合前三者。N/H 增大会放大 optimism 和 latency，要做 paired eval。

**机制展开（约 2 分钟）**：MPC 优化有限 horizon，只执行 (K) 步再观测；CEM 采样、保留 elite、更新分布；MPPI 围绕 nominal control 加噪声并按 cost 权重更新；best-of-N 只排序 N 条候选，不是完整 planner。冻结 checkpoint、seed、N/H/K、controller、scorer、reset、latency 和分母。N 增大可能选中 value/model hallucination，要做 N/H sweep、rank calibration 与 selected/unselected trace。

**诊断 / 证据**：记录 proposal、selected/unselected、checkpoint/scorer revision、normalizer、control Hz、p50/p95 latency、action age、replan、fallback 和 episode success；检查 CEM elite entropy、MPPI cost/temperature、best-of-N rank correlation，以及同 checkpoint 的 imagined/open-loop/sim/real 对照。公开分数不能替代本地 planner artifact。

**项目挂钩**：Cosmos/WAM 可连接 action/future/value slots、best-of-N 与 LIBERO/RoboCasa protocol；UWM 可连接 horizon、normalizer、fixed/reset；OpenPiVLA/OPD/Harness 可连接 action schema、scorer、timeout 与 episode trace。安全表达是“我能解释并审计 planning contract”，不把公开代码、离线 proxy 或未核验 checkpoint 写成个人 MPC/CEM/MPPI 成果。

**追问树**：MPC 和 CEM 是同一层概念吗？MPPI 与 CEM 的 proposal/update 差异？best-of-N 是否需要 world model？为什么 N 越大可能越差？H 与 execution prefix K 如何拆？scorer 不校准怎么办？CEM 早熟如何发现？MPPI temperature/noise 错配如何定位？如何把 planning latency 计入 success？

**易错点**：把 MPC 当 optimizer；把 CEM 当闭环执行；把 MPPI 公式当所有实现的默认；把 best-of-N top score 当真实 success；忽略 selected/unselected、N/H sweep、controller、latency、reset 和 denominator；把公开 Cosmos 分数写成个人 planning uplift。

**危险答案**：说“best-of-N 一定提高成功率”“N 越大越好”“CEM/MPPI 不需要 scorer”“只要 world model 预测好就能控制”“MPC 执行完整 horizon 不用 replan”“benchmark best-of-N 就证明项目闭环”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-022 Source Freeze](../sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html)：方法差异、协议和失败边界。
2. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)：CEM、latent planning、receding horizon 与 model bias。
3. [Cosmos Policy / WAM claim-to-code audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：best-of-N、action/future/value routing 与评估边界。
4. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)：imagined/open-loop/simulator/real metric ladder。
