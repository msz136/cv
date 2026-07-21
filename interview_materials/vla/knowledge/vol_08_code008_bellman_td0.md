# VOL 08 CODE-008：Bellman TD(0) Update

> 状态：`drafted / CODE-VLA-008 / knowledge_11_of_phase / card_pending / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[CODE-008 Source Freeze](../sources/vol_08_code008_bellman_td0_source_freeze.html)。

## 问题（Question）

Bellman TD(0) 手撕题的高危点不是公式本身，而是把真实终止、time-limit 截断、success、timeout、bootstrap 和 batch mask 混成一个 `done`。高分答案必须能说明 transition schema、target detach、discount、shape/reduction、异常样本以及它们如何映射到 VLA/robot rollout。

## 1. 直觉与专业定义

TD(0) 不等整条 episode 结束才算 return，而是用当前 transition 的 reward 加一步 bootstrap value 修正估计：

- **真实终止**：环境进入吸收状态，未来价值通常为 0；
- **truncated**：外部时间限制、预算或采样窗口结束，MDP 可能没有终止，通常仍应使用 `obs_{t+1}` bootstrap；
- **success**：业务/评估谓词，不自动等价于 termination；
- **valid**：这条 transition 是否允许进入 learner reduction。

Gymnasium 将 `terminated` 与 `truncated` 分开，VOL 01/VOL 02 fact review 也将 timeout bootstrap 作为必须保留的边界。它们是语义合同，不是候选人的项目实现证据。

## 2. Transition schema

```text
(obs_t, action_t, reward_t, obs_tp1,
 terminated_t, truncated_t, success_t,
 discount_t, valid_t, episode_id, step_id)
```

`episode_id/step_id` 用于防止跨 episode 拼接；`obs_tp1` 缺失时不能假设 truncation 可以安全 bootstrap。进入 learner 前不要写成无来源的 `done = terminated or truncated`，除非你明确说明这是 rollout 停止标记，而不是 Bellman terminal mask。

## 3. State-value TD(0) target

令 `V_next=V_target(obs_tp1)`，真实终止 mask 为 `m_term`：

\[
y_t=r_t+\gamma_t\left(1-m_t^{\mathrm{term}}\right)\operatorname{stopgrad}\!\left[V_{next}\right],
\qquad
\delta_t=y_t-V(obs_t).
\]

变量解释：`r_t` 是即时 reward，`γ_t` 是折扣，`m_term=1` 只代表真实终止，`V_next` 是下一状态 value，`δ_t` 是 TD residual。实现映射是 `target` 分支 detached，只让 `V(obs_t)` 产生梯度；`valid_t` 再决定这条样本是否进入 loss。

当 `terminated=False,truncated=True` 时，通常 `m_term=0`，保留 timeout transition 的 bootstrap；当 `terminated=True` 时，`m_term=1`，不 bootstrap。若环境定义有特殊 absorbing-state 语义，必须把该协议写进 source/benchmark manifest，而不是用一个全局规则猜测。

## 4. Q-learning 变体

若 learner 是 Q function，next value 不是任意地“取最大”：

\[
y_t^Q=r_t+\gamma_t(1-m_t^{\mathrm{term}})\operatorname{stopgrad}\!\left[\max_{a'}Q_{target}(obs_{t+1},a')\right].
\]

Double Q、actor-critic、distributional value 或 action-conditioned VLA value head 会替换 `V_next` 的构造，但仍需保留 terminal mask、timeout 语义、target detach 与 reduction 合同。TD target 不是完整算法名，也不自动保证稳定、保守或安全。

## 5. Batch、dtype 与 reduction

| 维度/字段 | 合同 | 高危错误 |
| --- | --- | --- |
| `reward`, `gamma` | 与 value 同 device/dtype；`gamma=0` 完全关掉 bootstrap | Python float 隐式转 device、负 gamma 未拒绝 |
| `terminated`, `truncated` | bool 或明确 0/1，分别保留来源 | 合并成 `done`，timeout 被当 terminal |
| `valid` | 控制 loss denominator；全零是数据事件 | all-invalid 返回漂亮的零 loss |
| `[B]` / `[B,T]` | 明确 broadcast/flatten、episode boundary | `[B,T]` mask 错位到 next state |
| target | `stopgrad`，必要时 target network | target 和 prediction 一起反传 |
| NaN/Inf | 在 reduction 前 reject/mark invalid | mask 后才检查，异常被隐藏 |

masked TD loss 可写为：

\[
L=\frac{\sum_i v_i\,\rho(\delta_i)}{\sum_i v_i},
\qquad v_i\in\{0,1\},
\]

其中 `ρ` 可是平方、Huber 或其他明确 loss；分母要和报告口径一致。分布式训练应先聚合 numerator/denominator，再相除，不能对各 rank mean 做无权平均。

## 6. 参考实现（带边界注释）

```python
def td0_target(reward, value_next, gamma, terminated, truncated, valid):
    # Keep flags separate; truncation is not automatically terminal.
    if (terminated & truncated).any():
        raise ValueError("ambiguous transition: both flags are true")
    if not torch.isfinite(reward).all() or not torch.isfinite(gamma).all():
        raise ValueError("non-finite reward/discount")
    if not valid.any():
        raise ValueError("all transitions are invalid")

    terminal_mask = terminated.to(value_next.dtype)
    target = reward + gamma * (1.0 - terminal_mask) * value_next.detach()
    return target, valid

def td0_loss(value, target, valid):
    residual = target.detach() - value
    weight = valid.to(residual.dtype)
    denom = weight.sum()
    if denom.item() == 0:
        raise ValueError("empty TD batch")
    return (weight * residual.square()).sum() / denom
```

这段实现刻意不把 `truncated` 丢掉：它可以进入日志、replay 与评估，但不直接进入 terminal mask。真实代码还需要检查 `obs_tp1` provenance、episode/step order、target network revision、reward scale、AMP/fp32 accumulation 与 distributed counts。

## 7. Deterministic probes 与诊断顺序

| Probe | 预期 | 首个分叉 |
| --- | --- | --- |
| P1 terminal | 不 bootstrap | terminal mask/flag 错 |
| P2 truncation | 有 next state 时仍 bootstrap | timeout 被错误当 terminal |
| P3 both flags | reject 或显式 precedence | schema/collector 合同不清 |
| P4 `gamma=0` | target=reward | discount broadcast/dtype 错 |
| P5 `[B]` vs `[B,T]` | 逐元素一致 | flatten/next-state 对齐错 |
| P6 all-invalid | reject/skip | 伪造零 loss、分母错 |
| P7 detach | target 无梯度 | autograd graph 错 |
| P8 NaN/Inf | reduction 前暴露 | 异常被 mask 掩盖 |

诊断顺序固定为：`transition lineage → flag semantics → obs_tp1 availability → terminal mask → gamma/dtype → target detach → shape/broadcast → valid denominator → optimizer/target revision`。不要只看 loss 下降就断言 TD 实现正确。

## 8. VLA 与项目真实性边界

在 VLA/robot rollout 中，`success`、controller stop、time-limit、policy timeout 和 environment termination 可能来自不同层。action chunk 被截断不等于任务失败；网络 timeout 不等于 MDP terminal；success scorer 也不一定写入 value target。必须保留 `episode_id/step_id`, `capture/apply` 时间和 model/schema revision，才能复查 transition 是否错位。

VOL 02 的本地 Harness 只能作为 offline grouped reward-weighted update、GAE/timeout 讨论的 hook；WAM/UWM/OPD/OpenPiVLA 的 reward、rollout 或 summary 不能替代 transition-level artifact。当前没有 CODE-008 local implementation、gradient parity、replay bundle、target revision 或 candidate ownership，因此安全表达是“我能实现并审计 TD(0) 合同”，不能声称 value 收敛或真机成功。

## 9. 30 秒回答与高压追问

**30 秒回答**：先把 transition 里的 `terminated` 和 `truncated` 分开。TD(0) target 是 `r+γ(1−terminated)V_next`，真实 terminal 不 bootstrap，time-limit truncation 通常仍 bootstrap。target 要 detach，`valid` 控制 denominator；检查 gamma=0、batch shape、all-invalid、NaN 和 flags 同时为 true。success/timeout/controller stop 不能自动当 terminal。没有 transition/replay/gradient artifact 时，我只讲实现合同，不报 value 或机器人收益。

**高压追问**：为什么 truncation 通常仍 bootstrap？如果 `obs_tp1` 缺失怎么办？`success=True` 是否一定 terminal？为什么 target detach？Q-learning 的 max 放在哪里？两 flags 同时 true 怎么办？VLA action chunk timeout 如何进入 schema？分布式 loss 为什么要聚合 numerator/denominator？

## 10. 结论与下一步

TD(0) 的高分实现是：显式 transition schema，terminal mask 只来自真实 termination，timeout bootstrap 保留 provenance，target detach，valid denominator 和 batch shape 可审计。当前 CODE‑VLA‑008 source contract 已冻结；下一步只生成 atomic card，仍需独立 bounded slice，题卡保持 `unseen`。

## References

1. [CODE-008 Source Freeze](../sources/vol_08_code008_bellman_td0_source_freeze.html)。
2. Sutton & Barto, [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html)。
3. Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。
4. 本仓库 [VOL 01 Batch 2 review](../sources/vol_01_batch2_mdp_td_control_independent_fact_review.html) 与 [VOL 02 review](../sources/vol_02_il_rl_posttraining_independent_fact_review.html)。
