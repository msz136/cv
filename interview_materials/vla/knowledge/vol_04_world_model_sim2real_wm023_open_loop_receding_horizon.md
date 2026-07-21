# VOL 04 World Model / Sim2Real：Open-loop Plan 与 Receding-horizon Replanning（WM-023）

> 状态：drafted / VLA-WM-023 / knowledge_25_of_44 / card_pending / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：回答“多久重新看一次环境”，不把公开 horizon/chunk 或硬件 latency 写成个人部署结果。  
> 前置：[WM-022 MPC/CEM/MPPI](vol_04_world_model_sim2real_wm022_mpc_cem_mppi_best_of_n.html)、[WM-023 Source Freeze](../sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.html)。

## 问题（Question）

open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？高分回答必须区分 \(H\)（看多远）与 \(K\)（执行多久），并把 observation age、queue、controller 和 success protocol 说清楚。

## 1. 先给面试结论

直觉上，open-loop chunk 像“先写一小段动作再执行”：推理只做一次，动作连续，能摊薄 inference latency；代价是执行到 chunk 后半段时 observation 已变旧，遇到扰动、接触或目标移动不能及时纠偏。receding-horizon 则是“预测较长、只执行前缀、重新观察再规划”，用反馈换鲁棒性，但需要更高 query rate、稳定队列和可接受的 p95 latency。

严格说，\(H\) 是 prediction/planning horizon，\(K\) 是 execution horizon，通常 \(1\le K\le H\)。Diffusion Policy 明确把 observation horizon、action prediction horizon 和 action execution horizon 分开，并定义 \(T_a\) 个 action 在不 re-planning 下执行；其消融把 \(T_a\) 解释成 temporal consistency 与 responsiveness 的 trade-off。[1] PlaNet 则在每个决策时刻用 latent CEM 搜索 action sequence，返回当前时刻的 first-action mean，新 observation 到来后重新初始化 belief。[2]

所以不能回答“\(K=1\) 一定最好”或“chunk 越长吞吐越高”。真正的选择是：在给定控制周期、端到端延迟、扰动时间尺度和安全约束下，哪一个 \(K\) 让 action age、queue underrun、切换抖动和恢复延迟都可接受。

## 2. 五条时间轴

| 轴 | 符号 | 面试中要说什么 |
| --- | --- | --- |
| observation history | \(T_o\) | 当前策略看多少帧/状态；过短可能看不到速度和接触趋势 |
| prediction/planning | \(H\) 或 \(T_p\) | 模型向未来展开多远；越长不只“信息更多”，也会放大 model error、搜索或 denoising 成本 |
| execution prefix | \(K\) 或 \(T_a\) | 生成 chunk 后连续执行多少控制步；决定 feedback frequency |
| control period | \(\Delta t=1/f_{\mathrm{ctrl}}\) | 把步数换成物理时间；不能只比较“16 steps”而不说明 Hz |
| end-to-end delay | \(L_{\mathrm{e2e}}\) | 从 observation timestamp 到 controller apply；包括推理、通信、排队和同步，不只是 GPU forward |

对一个长度为 \(K\) 的 chunk，第 \(j\) 个动作看到的 observation 已经老了：

\[
A_j\approx L_{\mathrm{e2e}}+j\Delta t,\qquad j=0,\ldots,K-1.
\]

变量解释：\(A_j\) 是 action age；\(L_{\mathrm{e2e}}\) 是第一步 action 可执行前的总延迟；\(j\Delta t\) 是 chunk 内没有新高层 observation 的等待。实现要从带时间戳的 observation、policy 输出、queue 入队/出队和 controller apply 事件计算 \(A_j\)，不能用平均 FPS 替代。

## 3. \(H\) 与 \(K\) 的取舍

### 3.1 增大 \(H\)：更有远见，但预测更脆弱

较大的 \(H\) 允许 planner 提前考虑抓取前的对齐、障碍绕行或长任务子目标；但每一步模型误差都会进入后续状态，搜索空间、采样数或扩散 denoising 计算也可能上升。PlaNet 的 planning-parameter 讨论明确指出，过短 horizon 不够，过长 horizon 会因搜索空间增大而伤害表现。[2]

面试中要补一句：增加 \(H\) 不等于增加真实反馈；若 \(K\) 不变，实际仍只执行前缀，后半段只是候选未来的条件。应固定 \(K\)，做 \(H\) matched sweep，并报告 per-offset error、first-failure stage 和 p95 latency。

### 3.2 减小 \(K\)：更快纠偏，但更难跑稳

小 \(K\) 减少 stale action age，使策略更快响应视觉偏移和接触事件；代价是高层 query 变频繁，推理/通信负载提高，chunk 拼接处可能出现速度或方向不连续。若 \(L_{\mathrm{e2e}}>K\Delta t\)，同步系统会 queue underflow，只能停顿、重复旧动作或触发 fallback。

### 3.3 增大 \(K\)：吞吐和连贯性更好，但开环风险更大

大 \(K\) 可以 amortize inference，动作 chunk 内更平滑，也减少高层接口调用。但遇到目标移动、抓取接触或终止条件时，策略要等到 chunk 边界才重规划；后半段 action 的 observation age 也更高。ACT 通过 action chunking 减少有效 horizon，并用 temporal ensembling 融合重叠 chunk；这说明“chunk 长度”和“query frequency”可以是两个不同旋钮，而不是把每个 chunk 全部 open-loop 执行。[3]

## 4. 执行架构：同步、异步与事件触发

1. **严格同步**：观察 → 推理 → 执行 \(K\) 步 → 再观察。可解释、易复现；必须检查 \(L_{\mathrm{e2e}}\) 是否小于 \(K\Delta t\)，并记录断流/等待。
2. **异步 overlap**：当前 chunk 执行时后台准备下一个 chunk。吞吐更好，但每个输出必须带 observation version、model revision 和 deadline；晚到的旧计划不能覆盖新计划。
3. **事件触发**：默认执行较长前缀，若 action age、视觉偏移、接触异常、value disagreement 或安全事件超过阈值，立即 replan。要把阈值、false positive、fallback 和最坏延迟纳入评估。

Cosmos/WAM audit 是很好的协议例子：LIBERO 的公开执行合同是 16×7 chunk、默认全 16 步 open-loop；RoboCasa 是 32×7 chunk、默认先执行 16 步再 requery。[4] 这些是指定代码/协议的事实，不是“16 步对所有 VLA 最优”；本地仍需固定 controller、action queue、reset、denormalization 和 episode denominator。

## 5. 用一个工程目标组织 sweep

可以把设计直觉写成一个待验证的成本，而不是伪装成理论最优：

\[
K^\*=\arg\min_K
\left[
\lambda_{\mathrm{compute}}\frac{L_{\mathrm{e2e}}}{K\Delta t}
\lambda_{\mathrm{stale}}E_{\mathrm{drift}}(K)
\lambda_{\mathrm{switch}}E_{\mathrm{switch}}(K)
\lambda_{\mathrm{safety}}E_{\mathrm{safety}}(K)
\right],
\qquad 1\le K\le H.
\]

第一项表示每个动作承担的平均推理负担；第二项表示开环漂移与扰动；第三项表示 chunk 切换不连续；第四项表示碰撞、终止响应或 fallback 成本。四个 \(E\) 和 \(\lambda\) 必须由任务定义和实验测量，不能从公式直接推导成功率。

最小实验矩阵：

| 实验 | 固定 | 扫描/注入 | 必须记录 |
| --- | --- | --- | --- |
| \(K\) sweep | checkpoint、\(H\)、denoise、reset、controller | \(K\in\{1,4,8,16\}\) 或任务适配值 | success、stage recovery、action age、jitter、queue underrun |
| \(H\) sweep | checkpoint、\(K\)、执行器 | short/medium/long \(H\) | per-offset error、first failure、compute、p95 latency |
| latency injection | 所有模型和协议 | 0/1/2/4 control-step delay | action age、stale failure、fallback、success |
| perturbation | 相同 episode/init | 接触、目标移动、视觉偏移 | recovery latency、replan reason、后续动作 |
| overlap check | 相同 observation/seed policy | 重叠 chunk 或 temporal ensemble | action disagreement、融合权重、边界行为 |

## 6. 可审计伪代码

```python
def execute_receding_horizon(policy, env, protocol):
    # 1. Freeze H, K, checkpoint, normalizer, controller and timestamps.
    while not terminal:
        obs = env.observe()
        plan = policy.predict(obs, horizon=protocol.H)
        # 2. Execute only K actions, or stop early on an event trigger.
        for action in plan[:protocol.K]:
            if stale_or_unsafe(obs, action, protocol):
                break
            env.apply(action)
        # 3. Persist action age, queue state, replan reason and outcome.
        log_step(obs, plan, protocol)
```

这段伪代码的关键不是循环本身，而是 \(H/K\) 的独立字段、event-trigger 的提前中断、timestamped action age 和可回放日志。它不能产生个人 latency 或 success 结果。

## 7. 失败诊断与项目边界

| 症状 | 优先怀疑 | 最小检查 |
| --- | --- | --- |
| chunk 前半段正常，后半段漂移 | \(K\) 太长或 observation age 增长 | per-step success、action-age 曲线、\(K\) sweep |
| \(K\) 很小反而掉点 | queue underflow、chunk switch jitter 或策略不一致 | p95 latency、queue depth、overlap disagreement |
| \(H\) 越长 imagined score 越高、真实成功下降 | model/value optimism 或 OOD future | matched \(H\) sweep、selected-vs-random、future error |
| 延迟注入后只在某类任务失败 | 接触/终止时间尺度与 \(K\) 不匹配 | failure stage、扰动恢复、controller trace |
| async 结果偶发倒退 | stale output 覆盖、版本/取消逻辑错误 | observation version、deadline、replan reason |

项目口述可以把 Cosmos/WAM、UWM/LIBERO、OpenPiVLA 和 Robot Harness 接到这些字段上：action chunk、future/value scorer、fixed init、normalizer、controller、timeout、episode trace。但当前工作区没有统一 WM-023 planning runtime、\(H/K\) paired curve、扰动 bundle 或 ownership artifact，安全表达应是“我能设计并审计 horizon/latency contract”，不能说“我已经证明缩短 chunk 提升鲁棒性”。

## 8. 参考与结论

WM-023 的一句话回答是：**\(H\) 决定计划看多远，\(K\) 决定多久接受旧观测；较长 \(K\) 摊薄 latency 并保持动作连续，较短 \(K\) 提高反馈频率和扰动恢复，但会增加 query、队列和切换风险。最终要在相同 checkpoint、reset、controller、denormalizer、success predicate 和 episode denominator 下做 \(H/K\)、latency injection 与 perturbation paired sweep。**

本节点保持 WARN，题卡保持 unseen；真实口述前不创建 coaching state。

参考：[WM-023 Source Freeze](../sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.html)、[PlaNet](https://arxiv.org/abs/1811.04551)、[Diffusion Policy](https://arxiv.org/abs/2303.04137)、[ACT](https://arxiv.org/abs/2304.13705)、[Cosmos/WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)、[WM-019 Metric Boundary](vol_04_world_model_sim2real_wm019.html)。

