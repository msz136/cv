# VOL 04 VLA-WM-024 原子题卡：Reward、Value、Success 与 Termination

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-024  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-024 Knowledge](../knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)；来源边界见 [WM-024 Source Freeze](../sources/vol_04_wm024_reward_value_success_termination_source_freeze.html)。

## reward model、value function、success classifier 与 termination predictor 如何区分？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-024</b> · reward model、value function、success classifier 与 termination predictor 如何区分？</summary>

**面试意图**：判断你能否按时间粒度、label、return、bootstrap、任务 predicate 和控制流拆开四种语义，而不是把它们统称“奖励分数”。

**30 秒回答**：Reward 是一步信号；value/Q 是给定策略与终止规则的未来回报；success 是任务级结果；termination 只表示回合结束，可能因成功、失败或超时。reward 和 continue 构成 return，value 可排序但不等于成功率。审计时分开记录成功判定、结束原因、截断和分母；公开 value 或 benchmark 不是本地结果。

**机制展开（约 2 分钟）**：reward head 预测一步分数；V/Q 汇总折扣未来 reward，依赖策略和 continuation mask。success 是终局 predicate 或 classifier probability；termination 是控制流，timeout 不必等于失败。Cosmos/WAM 的 value 可排序候选但可能 OOD；LIBERO/Cosmos 的 done/check_success 依赖 wrapper。审计时分开保存 reward、continue、value、success、termination_reason 和 denominator，并做 calibration 与 selected-vs-random 对照。

**诊断 / 证据**：检查 reward/return 的时间索引和单位、value/Q 的 policy/discount/horizon、continuation/terminal/truncation mask、success predicate revision、首次成功步、termination_reason、invalid/retry denominator。value 要做 calibration、rank correlation 和 selected/unselected outcome；success classifier 要做 OOD、阈值和 false-positive；reward loss 下降不能替代 closed-loop success。

**项目挂钩**：Cosmos/WAM 可连接 Monte-Carlo return、state-value/Q variants、value frame 与 candidate ranking；UWM/LIBERO 可连接 check_success、fixed init、timeout、horizon 和 denominator；OpenPiVLA/Robot Harness 可连接 scorer、controller 和 termination trace。当前没有统一 reward/value/success/termination artifact、校准曲线或 paired candidate bundle，安全表达是“我能审计标签与协议”，不声称公开 value 或 benchmark success 是个人收益。

**追问树**：reward model 是 transition head 还是偏好 judge？V 与 Q 有何差异？value 何时可解释为 success probability？为什么 done 不等于 success？timeout 是否 bootstrap？success classifier 需要哪些正负样本？如何校准 value ranking？WorldGym VLM reward 能否并入 LIBERO success？reward loss 降低但 success 不变怎么查？

**易错点**：把即时 reward 当终局 success；把 value 当校准成功率；把 done、termination、truncation 混为成功；忽略 policy、discount、horizon 和 continuation mask；跨任务直接比较 value；把公开 scorer 或 benchmark 写成本地结果。

**危险答案**：说“value 就是成功率”“done=True 一定成功”“termination head 预测任务是否完成”“reward 越高 episode 一定成功”“timeout 就是真实 terminal”“离线 value MSE 下降证明闭环成功率提升”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-024 Source Freeze](../sources/vol_04_wm024_reward_value_success_termination_source_freeze.html)：四类语义、公式、protocol 与失败矩阵。
2. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)：Dreamer reward/continue/value 与 lambda-return。
3. [Cosmos Policy / WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：Monte-Carlo return、V/Q variants、value ranking。
4. [Benchmark / Evidence audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)：success predicate、done、timeout 和 denominator。
5. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)：offline reward/value proxy 与 closed-loop success 分层。
