# VOL 08 CODE-008 Source Freeze：Bellman TD(0) Update

> 状态：`source_frozen / CODE-VLA-008 / knowledge_synced / card_pending / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结 TD(0) 的 batch 输入、bootstrap、discount、terminated/truncated、success 与 shape/reduction 合同；不把 VOL 01/VOL 02 的公开机制或本地 offline RL hook 写成候选人已经实现了可靠 value learner。

## 问题（Question）

如何实现一个正确的 Bellman TD(0) update，并避免把 `terminated`、time-limit `truncated`、success 和一个无语义 `done` 混在一起？手撕题还要说明 reward/discount 的 dtype、bootstrap mask、batch shape、target detach、empty/invalid transition 与测试 oracle。

## 1. 来源、revision 与 claim boundary

| 来源 | 类型 / 固定信息 | 直接支持 | 不能支持 |
| --- | --- | --- | --- |
| Sutton & Barto, [Reinforcement Learning: An Introduction, 2nd ed.](http://incompleteideas.net/book/the-book-2nd.html) | primary textbook；访问日期 2026-07-20 | MDP、return、value/Q、Bellman relation、TD target 与 on/off-policy 区分 | 用户项目采用某个 TD 变体、稳定性或指标收益 |
| Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | official docs；访问日期 2026-07-20；time-limit 语义按 VOL 02 review 固定 | `terminated` 是 MDP 真终止，`truncated` 是外部时间限制；timeout 通常仍允许 bootstrap | 所有环境的 success predicate、episode 语义或候选人代码 |
| 本仓库 [VOL 01 Batch 2 MDP / TD / Control review](vol_01_batch2_mdp_td_control_independent_fact_review.html) | local canonical fact review | TD terminal mask 的修正、terminated/truncated 分离、项目边界 | CODE-008 本地实现、白板通过或个人 ownership |
| 本仓库 [VOL 02 IL / RL fact review](vol_02_il_rl_posttraining_independent_fact_review.html) | local canonical fact review | GAE/timeout bootstrap 与本地 offline RL 表述边界 | 本地 Harness 是 online GRPO 或完整 value learner |

`checked` 只支持窄机制 claim；source freeze 不声明 reward scale、target network、optimizer、loss reduction 或项目算法已经闭合。

## 2. Frozen transition schema

建议每条 transition 至少包含：

```text
(obs_t, action_t, reward_t, obs_tp1, terminated_t, truncated_t,
 success_t, discount_t, valid_t, episode_id, step_id)
```

`terminated` 表示环境内真实吸收终止，`truncated` 表示时间限制或外部截断；二者不能在进入 learner 前压成一个没有来源的 `done`。`success` 是任务评估/业务谓词，不能自动等价于 `terminated`；timeout 也不能自动等于 failure。

## 3. TD(0) target

对 state-value learner，固定 `V_next = V_target(obs_tp1)`：

\[
y_t=r_t+\gamma_t\left(1-m_t^{\mathrm{term}}\right)\,\operatorname{stopgrad}\!\left[V_{next}\right],
\qquad
\delta_t=y_t-V(obs_t).
\]

这里 `m_term=1` 只表示真实终止；time-limit truncation 通常令 `m_term=0`，因此仍从 `obs_tp1` bootstrap。对 Q-learning，`V_next` 替换为 `max_a Q_target(obs_tp1,a)` 或明确的 next-action value；这不是“把所有 next value 都取 max”的通用答案。

实现映射：`reward/discount/mask` 先广播到 `[B]` 或 `[B,T]`，target 分支 detached，loss 只在 `valid_t=1` 的 transition 上 reduction。若数据集没有可靠 `obs_tp1`，不能声称 timeout bootstrap 已实现，应 reject/mark invalid。

## 4. Batch、discount 与 reduction

- `gamma` 可以是标量或 per-transition discount，但 dtype/device 与 reward/value 必须一致；`gamma=0` 应完全关闭 bootstrap。
- `terminated`、`truncated`、`valid` 必须是 bool 或明确的 0/1 mask，不能用浮点 reward 的符号推断。
- `target` 使用 `stopgrad`；只对 prediction 反传，避免 target network/value 被错误地一起更新。
- masked loss 的 numerator/denominator 要明确：全零 `valid` 是数据事件，不应静默返回“漂亮的零 loss”。
- batch shape、单步 `[B]`、序列 `[B,T]` 与 extra action/value head 必须有显式 broadcast/flatten 合同。

## 5. Deterministic probe matrix

| Probe | 输入/条件 | 预期 |
| --- | --- | --- |
| P1 | `terminated=True`, `truncated=False` | target 不 bootstrap |
| P2 | `terminated=False`, `truncated=True`, 有 `obs_tp1` | target 仍 bootstrap，并保留 truncation provenance |
| P3 | 两 flags 同时为 true | reject 或显式 precedence；不得静默混合 |
| P4 | `gamma=0` | target 仅为 reward |
| P5 | `[B]` 与 `[B,T]` broadcast | shape/flatten 后逐元素一致 |
| P6 | `valid=0` / all-invalid batch | reject/skip 并记录 reason，不伪造零 loss |
| P7 | target detach | value prediction 有梯度，target 分支无梯度 |
| P8 | reward/value dtype、NaN/Inf | finite/ dtype policy 明确，异常在 reduction 前暴露 |

## 6. 项目真实性边界

VOL 02 review 中的 local Harness 只能绑定 offline grouped reward-weighted policy update 与 timeout/GAE 讨论；它不证明候选人实现了 CODE-008 TD learner。WAM/UWM/OPD/OpenPiVLA/Robot Harness 的 rollout、reward、success 或 eval summary 也不能替代 transition-level `obs_tp1 + terminated/truncated + target/reduction` artifact。安全表达是“我能写出并审计 TD(0) update”，不能声称 value 收敛、offline RL 稳定或真机成功。

## 7. Source gate 结论与下一步

Sutton–Barto 与 Gymnasium 加上 VOL 01/VOL 02 fact review 足以冻结 TD(0)、timeout bootstrap 与 batch edge cases；下游 knowledge 已独立生成并保持与本 source contract 一致。当前仍没有 CODE-008 local implementation、transition bundle、gradient parity 或 candidate ownership。source gate 保持 `WARN`，下一步只生成 CODE‑VLA‑008 atomic card，继续保持 `unseen`，不启动 `SYS-VLA-004`。

## References

1. [Sutton & Barto, Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html)。
2. [Gymnasium Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。
3. 本仓库 [VOL 01 Batch 2 MDP/TD/Control review](vol_01_batch2_mdp_td_control_independent_fact_review.html)。
4. 本仓库 [VOL 02 IL/RL/Post-training review](vol_02_il_rl_posttraining_independent_fact_review.html)。
