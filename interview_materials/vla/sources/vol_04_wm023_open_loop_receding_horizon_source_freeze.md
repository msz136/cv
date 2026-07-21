# VOL 04 WM-023 Source Freeze：Open-loop Plan 与 Receding-horizon Replanning

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-023 / downstream_pending / WARN  
> 覆盖题目：VLA-WM-023  
> 本轮边界：冻结 open-loop execution、receding-horizon replanning、prediction horizon \(H\)、execution horizon \(K\)、推理 latency 与 action freshness 的权衡；不把公开 benchmark 或指定硬件 wall-clock 写成个人项目结果。

## 1. 问题与结论边界

题目：**open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？**

冻结结论：

1. **open-loop 是执行合同，不等于模型没有闭环能力。**策略在一次观测后生成一段动作，并在 \(K\) 个控制步内不重新查询高层策略；低层 controller 仍可能执行 rate limit、clip 和安全检查。\(K\) 越大，推理成本可以摊薄，动作序列也更连续，但新观测不能及时纠偏。
2. **receding horizon 是滚动闭环。**模型可预测 \(H\) 步，但只执行前 \(K\) 步，随后获取新 observation、丢弃或重用旧计划并重新规划；PlaNet 的算法返回当前时刻的 first-action mean，并在下一 observation 后重新初始化 action-sequence belief。[S1]
3. **\(H\) 与 \(K\) 不是同一个旋钮。**\(H\) 决定看多远、训练/采样要覆盖多长未来；\(K\) 决定多久暴露在 stale plan 下。通常要求 \(1\le K\le H\)，但不能从论文默认值推导出普适最优值。
4. **latency 约束先于“更频繁重规划”。**若一次端到端推理、通信和排队延迟为 \(L\)，控制周期为 \(\Delta t\)，同步执行至少要检查 \(L\lesssim K\Delta t\) 与 queue underflow；异步执行还要记录 action timestamp、版本、取消/拼接规则，不能只看平均 FPS。
5. **证据必须做 matched sweep。**固定 checkpoint、normalizer、denoise steps、reset、controller、任务和 success predicate，分别扫 \(H\)、\(K\)、人为注入 latency 与扰动，报告 success、阶段恢复、p50/p95 latency、action age、queue underrun、jitter 和每步失败位置。当前工作区没有 WM-023 的本地 planning runtime、paired sweep 或 ownership artifact，因此只冻结可审计机制，不宣称个人结果。

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Hafner et al., Learning Latent Dynamics for Planning from Pixels / PlaNet | arXiv:1811.04551v5，2019-06-04 | latent CEM、每时刻规划、返回 first action、belief 在新 observation 后重置、过长 planning horizon 扩大搜索空间并可能变差 | 用户项目已采用 PlaNet 或某个 \(H/K\) 已最优 | primary / checked |
| S2 | Chi et al., Diffusion Policy: Visuomotor Policy Learning via Action Diffusion | arXiv:2303.04137v5，2024-03-14 | \(T_o/T_p/T_a\) 三种 horizon；\(T_a\) 步 action 在不 re-plan 下执行；action horizon 的 temporal-consistency / responsiveness trade-off；latency 定义 | 任意 diffusion policy 的默认 \(T_a\)、真实部署 latency 或本地成功率 | primary / checked |
| S3 | real-stanford/diffusion_policy | commit 5ba07ac6661db573af695b419a7947ecb704690f，Apache-2.0 | n_obs_steps、n_action_steps、horizon、policy 输出切片与 n_action_steps 相关的 execution contract；n_latency_steps 数据 padding 入口 | 本机运行速度、checkpoint 兼容性或用户项目采用该 commit | official-code / checked |
| S4 | Zhao et al., Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware / ACT | arXiv:2304.13705v1；官方 repo commit 742c753c0d4a5d87076c8f69e5628c79a8cc5488 | action chunking 减少有效 horizon；temporal ensembling 以更高 query frequency 融合重叠 chunk；代码中的 query_frequency=1 与 overlap aggregation | chunking 必然提升所有任务、ACT 的结果可外推到其他 VLA | primary + official-code / checked |
| S5 | Cosmos Policy / WAM claim-to-code audit | 本地 frozen audit，Cosmos repo commit 18a2accadf4e7a3531e56754102af5a24d2316da | LIBERO 16×7 默认全 16 步 open-loop；RoboCasa 32×7、默认执行前 16 步再 requery；论文/代码指定硬件的 5-step/1-step chunk wall-clock 语境；必须固定 action queue 与 protocol | 公开 98.5%/67.1% 是本地结果、用户 planner 已复现、指定硬件数字等于本机 latency | local audit / WARN |
| S6 | WM-019 Metric Boundary 与 WM-022 MPC/CEM/MPPI | 本地 canonical + review | teacher-forced/open-loop/proxy/simulator/real 的 metric 分层；\(N/H/K\)、scorer、controller、latency、selected/unselected trace 的 protocol 要求 | open-loop proxy 等于 closed-loop success；单次 best score 等于因果提升 | local audit / WARN |

## 3. 统一时间轴与术语

设控制周期为 \(\Delta t=1/f_{\mathrm{ctrl}}\)，一次高层推理与通信总延迟为 \(L_{\mathrm{e2e}}\)：

| 量 | 含义 | 典型问题 |
| --- | --- | --- |
| \(T_o\) / \(O\) | 输入 observation history | 过短看不到速度/接触趋势；过长增加编码与缓存成本 |
| \(H\) / \(T_p\) | prediction / planning horizon | 太短没有提前量；太长扩大 model error、搜索空间或 denoising compute |
| \(K\) / \(T_a\) | execution horizon / chunk prefix | 太短 replan 频繁、latency 和 jitter；太长 action stale、扰动恢复慢 |
| \(L_{\mathrm{e2e}}\) | observation→inference→queue→controller 延迟 | 不能用平均 FPS 代替 p95 action age |
| \(A_j\) | 第 \(j\) 个执行动作的 observation age | open-loop 中 \(A_j\) 随 \(j\) 增长 |

在一次 chunk 内，第 \(j\) 个动作（\(j=0,\ldots,K-1\)）的近似 observation age 为：

\[
A_j \approx L_{\mathrm{e2e}}+j\Delta t .
\]

变量解释：\(L_{\mathrm{e2e}}\) 是拿到 observation 到第一条可执行 action 的延迟，\(j\Delta t\) 是 chunk 内等待时间；实现中应从 timestamped observation、policy output、queue enqueue/dequeue 和 controller apply 事件计算，而不是只记录模型 forward time。

## 4. 三种执行架构

### 4.1 严格同步 receding horizon

每次 observation 后完成推理，执行 \(K\) 步，等待下一次 observation。它最容易审计，但当 \(L_{\mathrm{e2e}}>K\Delta t\) 时会出现动作断流或不得不降低控制频率。\(K=1\) 的“每步重规划”只有在系统真的能按周期完成推理时才成立。

### 4.2 异步 overlap

当前 chunk 执行时，后台线程准备下一 chunk；到达 splice point 时切换。它可以摊薄 latency，但必须处理 stale output、observation version、取消旧 future、队列深度和 fallback。后台结果晚到时不能静默覆盖更新的计划。

### 4.3 事件触发 replan

默认执行较长 prefix，若检测到视觉偏移、接触异常、value disagreement、action-age 超阈值或安全事件则提前 replan。事件触发降低平均 compute，但阈值、false positive、fallback 和最坏延迟必须进入协议；不能只报平均成功率。

## 5. \(H\) 与 \(K\) 的机制权衡

| 调整 | 可能收益 | 代价/风险 | 最小证据 |
| --- | --- | --- | --- |
| 增大 \(H\)，固定 \(K\) | 看到更远目标、允许长程动作规划 | world/value error、搜索/denoise 成本和 OOD 未来增大 | matched \(H\) sweep、per-offset error、p95 latency |
| 减小 \(H\)，固定 \(K\) | 计算快、预测分布较近 | 可能只会局部贪心，接触前没有提前量 | 同一 \(K\) 的 long-task success 与 first-failure stage |
| 减小 \(K\) | 更快使用新 observation，抗扰动、动作 age 小 | replan 次数和通信/推理负担增大；多模态策略可能出现 chunk switch 抖动 | \(K\) sweep、jitter、queue underrun、recovery latency |
| 增大 \(K\) | amortize inference、动作连续、减少 query | open-loop drift、终止/碰撞响应晚、执行器不再按当前状态匹配 | action-age 曲线、扰动恢复、每步成功率 |

可把选型写成工程决策而非“固定公式最优”：

\[
K^\*=\arg\min_K
\left[
\lambda_{\mathrm{compute}}\frac{L_{\mathrm{e2e}}}{K\Delta t}
\lambda_{\mathrm{stale}}E_{\mathrm{drift}}(K)
\lambda_{\mathrm{switch}}E_{\mathrm{chunk\_switch}}(K)
\lambda_{\mathrm{risk}}E_{\mathrm{safety}}(K)
\right],
\qquad 1\le K\le H .
\]

变量解释：第一项表示每个动作摊到的推理负担，第二项表示 stale plan/扰动造成的偏差，第三项表示频繁换 chunk 的不连续，第四项表示安全事件成本；\(\lambda\) 是业务权重。这是用于设计 sweep 的抽象目标，不是论文报告的统一定理，也不能由它生成个人指标。

## 6. 最小可复现实验合同

固定 checkpoint、dataset statistics、\(T_o\)、denoising steps、controller、reset/init、camera preprocessing、success predicate、episode denominator 和随机种子，然后执行：

1. **matched \(K\) sweep**：例如 \(K\in\{1,4,8,16\}\)，固定 \(H\)，记录 success、stage recovery、\(A_j\)、p50/p95 latency、queue underrun、action jerk/jitter。
2. **matched \(H\) sweep**：固定 \(K\)，对比 short/medium/long horizon，记录 per-offset action/state error、first failure stage 与 compute。
3. **latency injection**：在相同 checkpoint 下人为注入 0、1、2、4 个 control-step delay，区分 pure compute delay、queue delay 和 controller delay。
4. **perturbation test**：在抓取、接触或目标移动阶段加入可复现扰动，对比 open-loop prefix 与提前 replan 的 recovery latency。
5. **overlap consistency**：对同一 observation 重复采样 chunk，统计重叠 action 的 disagreement；若使用 temporal ensemble，记录权重、有效 query frequency 和 edge handling。

每条 episode 至少保存 obs_timestamp、policy_start/end、chunk_id、model_revision、action_age、queue_depth、replan_reason、fallback、termination_reason 和 per-step success/constraint 字段。

## 7. Source gate 结论与下一步

本 source freeze 为 WARN：open-loop/receding-horizon 的时间轴、\(H/K\) 语义、同步/异步执行和最小 matched sweep 已冻结；WM-023 本地 planning runtime、同 checkpoint 的 \(H/K\) 曲线、扰动 episode、latency trace 与 ownership 仍缺。下游知识页和题卡可以写机制与审计合同，但不能写个人“降低 latency”或“提升鲁棒性”。

## 参考来源

1. Hafner et al., [Learning Latent Dynamics for Planning from Pixels](https://arxiv.org/abs/1811.04551)，arXiv v5；PlaNet paper 与 Algorithm 2。
2. Chi et al., [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/abs/2303.04137)，arXiv v5；[official repository](https://github.com/real-stanford/diffusion_policy/tree/5ba07ac6661db573af695b419a7947ecb704690f)。
3. Zhao et al., [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/abs/2304.13705)，arXiv v1；[official ACT repository](https://github.com/tonyzhaozh/act/tree/742c753c0d4a5d87076c8f69e5628c79a8cc5488)。
4. [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html)。
5. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)。
6. [WM-022 MPC/CEM/MPPI/Best-of-N Source Freeze](vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html)。
