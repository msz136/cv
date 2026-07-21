# VOL 08 CODE-VLA-008 原子手撕题卡：Bellman TD(0) Update

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`CODE-VLA-008`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-008 Knowledge](../knowledge/vol_08_code008_bellman_td0.html)；来源边界见 [CODE-008 Source Freeze](../sources/vol_08_code008_bellman_td0_source_freeze.html)。

## 实现正确的 Bellman TD(0) update

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-008</b> · 请实现 Bellman TD(0) update，区分 terminated/truncated，并处理 target、mask 与 batch edge cases。</summary>

**面试意图**：判断你能否把 MDP 语义落实到 transition schema、target detach、valid reduction 和可诊断的代码，而不是只背 Bellman 公式。

**30 秒回答**：分开 `terminated/truncated`，带上 `obs_tp1`。target=`r+γ(1−terminated)V_next.detach()`；terminal 不 bootstrap，timeout 通常 bootstrap。检查 flags、all-invalid、`γ=0`、shape；无 replay artifact 不声称收敛。

**机制展开（约 2 分钟）**：冻结 transition schema 与 episode/step lineage；拒绝双 flag、缺 `obs_tp1`、非 finite reward/discount。terminal mask 只来自 `terminated`，truncation 有 next state 仍 bootstrap。target detach；`valid` 明确分子/分母，`[B]`/`[B,T]` 对齐，分布式先聚合计数再相除。Q-learning 只替换 next value，不是所有 TD 都取 max；success、controller stop、network timeout 保留来源，不自动变成 terminal。

**诊断 / 证据**：按 `schema/lineage → terminated/truncated → obs_tp1 → terminal mask → gamma/dtype → detach → shape/broadcast → valid denominator → target revision` 定位。至少跑 8 个 probe：真实 terminal 不 bootstrap；time-limit truncation bootstrap；两 flag 冲突 reject/precedence；`gamma=0` 只剩 reward；`[B]` 与 `[B,T]` 等价；all-invalid reject/skip；target 无梯度；NaN/Inf 在 reduction 前暴露。runtime 还要有 transition/replay bundle、target-network revision 和 numerator/denominator 记录。

**项目挂钩**：VOL 02 的 Harness 只能连接 offline grouped reward-weighted update、GAE/timeout 讨论；OpenPiVLA、WAM、UWM/LIBERO、OPD 的 rollout/reward/summary 不能替代 transition-level artifact。当前没有 CODE-008 本地 learner、replay bundle、gradient parity、target revision 或候选人 ownership；安全说法是“我能实现并审计 TD(0) 合同”，不能说已证明 value 收敛、offline RL 稳定或真机成功。

**追问树**：为什么 truncation 通常仍 bootstrap？`obs_tp1` 缺失怎么办？`success=True` 是否一定 terminal？为什么 target 要 detach？两 flag 同时 true 怎么处理？Q-learning 的 max 在哪一侧？action chunk timeout 如何进入 schema？分布式 masked loss 为什么不能平均各 rank 的 mean？

**易错点**：把 `done=terminated or truncated` 直接用于 Bellman mask；把 success 当 terminal；忽略 `obs_tp1` provenance；target 和 prediction 一起反传；all-invalid 静默返回 0；把 `[B,T]` mask 错位到 next state；用 loss 下降冒充 value 正确；把公开 TD 机制写成个人项目实现。

**危险答案**：说“timeout 就是失败所以不 bootstrap”“Gymnasium API 证明我实现了 learner”“所有 Q/V target 都取 max”“target 不 detach 也一样”“一次 rollout 成功就证明 TD 稳定”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-008 Knowledge](../knowledge/vol_08_code008_bellman_td0.html)：transition schema、terminal/timeout bootstrap、target detach、reduction、probe 与项目边界。
2. [CODE-008 Source Freeze](../sources/vol_08_code008_bellman_td0_source_freeze.html)：Sutton–Barto、Gymnasium time-limit 语义与 8 个 deterministic probes。
3. Sutton & Barto, [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html)。
4. Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。
