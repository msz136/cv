# VOL 04 World Model / Sim2Real：Reward、Value、Success Classifier 与 Termination Predictor（WM-024）

> 状态：drafted / VLA-WM-024 / knowledge_26_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：区分四种“好坏/结束”信号，不把 value score、success predicate 和 termination 混为一谈。  
> 前置：[WM-023 Open-loop / Receding-horizon](vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)、[WM-024 Source Freeze](../sources/vol_04_wm024_reward_value_success_termination_source_freeze.html)。

## 问题（Question）

reward model、value function、success classifier 与 termination predictor 如何区分？回答必须同时覆盖时间粒度、标签来源、训练目标、规划用途、bootstrap mask 和评估 protocol。

## 1. 一句话区分

- **Reward \(r_t\)**：这一步转移即时得到多少任务信号。
- **Value \(V^\pi(s_t)\)**：在指定 policy、reward、discount 和终止规则下，从当前状态往后预计累计多少回报。
- **Success classifier/predicate**：这条 episode 或某个阶段是否满足任务成功规则，或分类器对成功的概率。
- **Termination predictor**：episode 是否结束，或下一步是否仍 continuation；结束原因可能是成功、失败、碰撞、死亡、timeout 或异常。

最容易穿帮的说法是“value 就是成功率”或“done 就是 success”。只有在明确的稀疏奖励、固定 horizon、固定 policy 和校准条件下，value 才可能与成功概率有特定关系；一般不能直接替换。

## 2. 标签合同与时间粒度

| 量 | 标签粒度 | 典型输入 | 输出/用途 | 不能推出 |
| --- | --- | --- | --- | --- |
| reward head | 每步 transition | state、action、next state 或 latent | reward prediction、RL target、dense shaping | 终局成功、长期价值 |
| value / Q head | state 或 state-action | 当前 belief、policy、action | critic、bootstrap、candidate ranking | 成功概率、动作可执行性 |
| success predicate/classifier | episode/阶段 | trajectory、终局 state、task 条件 | eval、稀疏监督、终局筛选 | dense credit、是否 timeout |
| termination/continuation head | 每步边界 | state、next state、environment flag | reset、return mask、rollout 截断 | 成功或失败原因 |

“reward model” 还可能指人类偏好模型或语言模型 judge；此时 label 不是环境 transition reward，校准和部署对象也不同。面试中先确认命名，再讨论公式。

## 3. 数学关系

带 continuation 的 return 可以写成：

\[
G_t=r_t+\gamma c_tG_{t+1},\qquad
V^\pi(s_t)=\mathbb E_{\pi,p}\left[
\sum_{k\ge0}\gamma^k
\left(\prod_{i=0}^{k-1}c_{t+i}\right)r_{t+k}
\mid s_t\right].
\]

变量解释：\(r_t\) 是即时 reward，\(c_t\) 表示 episode 是否继续，\(\gamma\) 是 discount；\(V^\pi\) 还依赖 policy \(\pi\) 和 transition distribution \(p\)。代码里 continuation/terminal mask 决定是否 bootstrap，timeout 是否截断也必须显式记录。

Q function 还条件于动作：

\[
Q^\pi(s_t,a_t)=
\mathbb E\left[r_t+\gamma c_tV^\pi(s_{t+1})\mid s_t,a_t\right].
\]

因此 value scorer 可以比较候选 action，但它是模型/策略条件的预期回报；success predicate 是终局规则，两者的误差模式不同。

## 4. World model、Dreamer 与 WAM/Cosmos 映射

Dreamer 风格的 world model 通常有 observation/reconstruction、reward 和 continuation heads；actor 在 imagined state 上选动作，critic 对 continuation-weighted multi-step return 提供 baseline/target。reward head 的当前输出不是 critic value，continuation 也不是 success classifier。[1]

Cosmos/WAM audit 中，rollout 的 future index 与 Monte-Carlo return 构成 value target；state-value 与 Q variants 通过不同 condition/mask 读取状态或 action。value frame aggregation 产生的高分可用于 candidate ranking，但 direct policy 同时输出 value 不代表 direct eval 一定用 value 选动作。[2]

规划时至少要保存：

1. candidate action / future state；
2. value 或 Q score、scorer revision；
3. success predicate 与 learned classifier probability；
4. termination reason、timeout/truncated；
5. selected 和 unselected 的真实 outcome。

只保存 top value 会隐藏 value optimism、future OOD 和 scorer mismatch。

## 5. Success、done、timeout 的区别

success 是任务语义，通常由环境的 check_success、终局阈值或学习分类器给出；termination 是 episode 控制流。一个 episode 可以：

- 成功后 termination；
- 失败/碰撞后 termination；
- 到达最大 horizon 的 timeout/truncation；
- 发生异常或手动停止。

某些 LIBERO/Cosmos wrapper 把 env.done 或 env._check_success 写进 success record，但等价性依赖代码版本和 wrapper。严谨日志至少包含 success predicate revision、success step、termination_reason、truncated、exception 与 denominator rule。[3]

WorldGym 的 VLM reward/proxy 仍应与 simulator predicate、real-robot success 分开；proxy 可以作为排序或诊断，不应直接并入闭环成功率。[3][4]

## 6. 反例与失败诊断

| 现象 | 误判 | 正确检查 |
| --- | --- | --- |
| reward loss 下降、success 不变 | reward head 已证明控制变好 | action intervention、per-step reward、closed-loop predicate |
| value 高、候选失败 | value 等于 success probability | calibration、rank correlation、selected-vs-random |
| classifier probability 高、环境失败 | classifier 是真值 | OOD holdout、阈值、视频与 predicate 对照 |
| done 高、success 异常高 | done 一定表示成功 | termination_reason、timeout/truncated、wrapper revision |
| critic 不稳定 | 只是 value 网络容量不足 | terminal/truncation mask、discount、return denominator |
| 跨任务 value 不可比 | 一个全局阈值即可 | reward scale、horizon、task-wise calibration |

## 7. 可审计伪代码

```python
def audit_episode(step_records, task_contract):
    # 1. Keep step-level reward/continuation separate from terminal success.
    rewards = [row.reward for row in step_records]
    continuation = [row.continue_flag for row in step_records]
    returns = discounted_return(rewards, continuation, task_contract.gamma)

    # 2. Evaluate the task predicate and preserve the actual termination reason.
    success = task_contract.check_success(step_records)
    reason = infer_termination_reason(step_records)

    # 3. Do not overwrite value, classifier probability or success with done.
    return {
        "return": returns,
        "success": success,
        "termination_reason": reason,
        "truncated": reason == "timeout",
    }
```

实现重点是字段隔离：reward 用于 return，continuation 用于 bootstrap，success 用于任务评价，termination 用于控制流；任何合并都必须在 protocol 中显式说明。

## 8. 项目挂钩与证据边界

Cosmos/WAM 可以挂 action/future/value slots、Monte-Carlo return、value ranking；UWM/LIBERO 可以挂 fixed init、success predicate、horizon、normalizer 和 denominator；OpenPiVLA/Robot Harness 可以挂 scorer、timeout、controller trace。但当前工作区没有统一 reward/value/success/termination artifact、校准曲线或 paired candidate bundle。安全表达是“我能审计四类标签及其协议”，不能声称公开 value 或 benchmark success 已证明个人闭环收益。

## 9. 结论

高分回答的边界是：**reward 是一步信号，value/Q 是 policy-conditioned 的未来回报，success 是任务级结果，termination 是 episode 控制流；reward 与 continuation 进入 return，value 可用于排序但不自动等于成功概率，done 也不自动等于 success。**

本节点保持 WARN，题卡保持 unseen；真实口述前不创建 coaching state。

参考：[WM-024 Source Freeze](../sources/vol_04_wm024_reward_value_success_termination_source_freeze.html)、[Dreamer/World Model audit](../sources/vol_04_world_model_foundations_claim_to_code.html)、[Cosmos/WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)、[Benchmark protocol audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)、[WM-023](vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)。
