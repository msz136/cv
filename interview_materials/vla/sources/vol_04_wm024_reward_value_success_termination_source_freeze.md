# VOL 04 WM-024 Source Freeze：Reward、Value、Success Classifier 与 Termination Predictor

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-024 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-024  
> 本轮边界：区分即时 reward、policy-conditioned value/Q、任务 success predicate/classifier、episode termination/continuation；不把任何公开 value score 或 benchmark success 写成个人项目结果。

## 1. 结论先行

1. **Reward 是时间步级的即时信号。**在状态/动作转移后产生 \(r_t\)，可以由环境规则、人工偏好模型或 world-model reward head 给出；它回答“这一步/这一转移有多好”，不直接回答整条 episode 是否成功。
2. **Value/Q 是未来累计回报的条件期望。**\(V^\pi(s_t)\) 依赖 policy、discount、reward convention 和 termination mask；\(Q^\pi(s_t,a_t)\) 还条件于当前 action。Cosmos/WAM 的 value target 是 rollout return/value score，用于排序候选或学习价值，不应默认解释成 success probability。[S1][S2]
3. **Success classifier/predicate 是任务级结果标签。**它通常是环境的 check_success、终局规则或学习得到的 \(P(\mathrm{success}\mid\tau)\)，依赖 task、阈值、episode 终点、debounce 和 protocol；它不是 dense reward，也不是任意状态上的 value。
4. **Termination predictor 预测 episode 是否结束，或 continuation \(c_t\) 是否为真。**它控制 return bootstrap、rollout 截断和 reset；终止原因可能是成功、失败、碰撞、死亡或时间上限，故 termination 不等于 success。
5. **四者可组合但不能互换。**reward/termination 进入 return，value 汇总未来 reward，success 用于任务评价或稀疏训练标签；若把它们都叫“分数”，规划、loss mask、分母和失败归因都会错位。

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | World Model / PlaNet / DreamerV3 Foundations Audit A + DreamerV3 paper | arXiv:2301.04104；本地 audit 已核对 paper HTML 与 frozen reimplementation contract | reward head、continuation head、critic value、lambda-return、world-model/actor/critic 分工；reward/continue/value 不是同一变量 | 用户项目使用 DreamerV3、任何本地 value calibration 或成功率 | primary + local audit / WARN |
| S2 | Cosmos Policy / WAM claim-to-code audit | arXiv:2601.16163v1；Cosmos repo commit 18a2accadf4e7a3531e56754102af5a24d2316da | Monte-Carlo return \(G_{t+K}\)、state-value/Q variants、value frame aggregation、value ranking 与 action/future/world slots | value score 是真实 success probability、公开分数是本地结果、planning checkpoint 已在本机复现 | primary + official-code audit / WARN |
| S3 | Benchmark / Evidence claim-to-protocol audit | LIBERO commit 8f1084e3132a39270c3a13ebe37270a43ece2a01；Cosmos eval commit 18a2accadf4e7a3531e56754102af5a24d2316da | task success predicate、env check_success、done wrapper、timeout/invalid episode、WorldGym VLM proxy 与 simulator/real success 分层 | 所有 benchmark 的 done 都等价 success、proxy 分数等于真实任务成功 | official-code audit / WARN |
| S4 | WM-019 Metric Boundary 与 WM-023 Horizon Source Freeze | 本地 canonical + review | reward/value/open-loop/proxy/simulator/real metric ladder、termination/horizon/denominator 与 action-age protocol | 任一离线 reward/value loss 证明 controller closed-loop success | supporting / WARN |

## 3. 四种量的标签合同

| 量 | 时间粒度 | 典型标签/单位 | 主要用途 | 不能直接推出 |
| --- | --- | --- | --- | --- |
| reward \(r_t\) | 每步或每次 transition | 标量、symlog/normalized return、偏好分数 | world-model reward prediction、RL target、dense shaping | episode success、未来价值、物理终止 |
| value \(V^\pi(s_t)\) | 状态/时刻 | discounted return 的期望 | critic baseline、candidate ranking、bootstrap | success probability、独立于 policy 的“真实好坏” |
| Q \(Q^\pi(s_t,a_t)\) | 状态-动作对 | action-conditioned return | action selection、planning scorer | action 一定可执行、成功 predicate |
| success \(y_{\mathrm{succ}}\) | episode/阶段 | bool、task predicate、classifier probability | 评估、稀疏目标、终局筛选 | dense credit assignment、episode 是否因 timeout 结束 |
| termination \(d_t\) / continuation \(c_t\) | 每步边界 | Bernoulli、done、timeout/truncation flag | reset、rollout 截断、return mask | 成功、失败原因、任务质量 |

面试里先问清楚 “reward model” 的含义：若它是 world model 的 transition reward head，输入通常是 state/action 后果；若它是人工偏好或语言模型打分器，label 来源、校准和部署对象不同。本节点默认讨论前者，同时保留这层歧义。

## 4. 数学关系与反例

对一个带 continuation 的 return：

\[
G_t=r_t+\gamma c_t G_{t+1},\qquad
V^\pi(s_t)=\mathbb E_{\pi,p}\left[\sum_{k\ge0}\gamma^k
\left(\prod_{i=0}^{k-1}c_{t+i}\right)r_{t+k}\mid s_t\right].
\]

变量解释：\(r_t\) 是即时 reward，\(c_t\in\{0,1\}\) 表示 episode 是否继续，\(\gamma\) 是 discount；\(V^\pi\) 还依赖 policy \(\pi\) 和 transition distribution \(p\)。实现中 continuation/terminal mask 决定是否 bootstrap，不能把 done 直接当 success。

同一状态可以有不同 value 与 success：

- 一个接近成功的状态可能 \(P(\mathrm{success})\) 高，但若当前 policy 会绕开目标，\(V^\pi\) 仍低。
- 一个碰撞前的状态可能短期 reward 很高、value 仍高估，但终局 success 为 0。
- 时间上限导致 \(d_t=1\) 时，episode 结束却不一定是任务失败；若把 timeout 当真实 terminal，会错误截断 bootstrap。

因此，success classifier 不是 value 的无监督替代；它需要明确正负 episode、时间点、阈值、校准集和跨任务迁移边界。

## 5. World model 与 WAM/Cosmos 中的映射

Dreamer 风格 world model 通常同时有 observation/reconstruction、reward 和 continuation heads；actor/critic 在 imagined states 上工作。critic 的 target 是 continuation-weighted multi-step return，而不是 reward head 的当前输出。[S1]

Cosmos/WAM audit 中，rollout 的 future index 与 Monte-Carlo return 形成 value target；state-value variant 与 Q variant 通过不同 condition/mask 选择输入。value frame 的 latent aggregation 输出可用于候选 ranking，但 direct policy 生成 value 不等于 direct eval 使用 value selection。[S2]

这里要区分三种“成功”：

1. **value scorer 高**：模型认为候选未来回报高，可能受 OOD/value optimism 影响。
2. **success predicate 为真**：环境在指定终点通过 task-specific check_success。
3. **learned success classifier 概率高**：分类器相信成功，需额外做 calibration、OOD 与 false-positive 检查。

最小 paired 诊断应同时保存 candidate value、success predicate、classifier probability、termination reason 和 selected/unselected outcome；只保存 top value 不能证明 scorer 排序正确。

## 6. Success、done、timeout 的 protocol 边界

LIBERO/Cosmos audit 显示，runner 可能把 env.done、wrapper.check_success 或 env._check_success 作为 success record，但它们的等价性依赖具体 commit 和 wrapper。[S3] 所以每个 episode 需要至少记录：

| 字段 | 解释 |
| --- | --- |
| success_predicate_revision | 成功函数/阈值/任务版本 |
| success_step | 首次满足 predicate 的时间步，或 null |
| termination_reason | success、failure、collision、death、timeout、exception、manual stop |
| truncated | 是否因最大 horizon/时间上限截断 |
| denominator_rule | invalid episode、重试、早停和剔除规则 |

WorldGym 的 VLM reward/proxy 也必须与 simulator check_success 和 real-robot success 分层；代理评分可以帮助排序或诊断，但不能直接并入 closed-loop success rate。[S3][S4]

## 7. 失败模式与最小检查

| 症状 | 可能混淆 | 最小诊断 |
| --- | --- | --- |
| reward loss 下降、success 不变 | reward head 拟合但动作后果/终局不对 | action intervention、per-step reward、closed-loop predicate |
| value 高、selected candidate 失败 | value optimism、future OOD 或 policy mismatch | value calibration、rank correlation、selected-vs-random |
| success classifier 高、env success 低 | classifier shortcut、domain shift、阈值偏移 | calibration curve、OOD holdout、video/predicate audit |
| done 高、success 高得不合理 | wrapper 把 timeout/exception 当 success | termination_reason、truncated、predicate revision |
| critic target 不稳定 | continuation/discount/time-limit mask 错 | terminal vs truncation A/B、bootstrap mask、return denominator |
| 不同任务 value 不可比 | reward scale、horizon、success semantics 不同 | task-wise normalization、per-task calibration、protocol tuple |

## 8. Source gate 结论与项目边界

本 source freeze 为 WARN：四类量的时间粒度、公式、head/label、success/done/timeout protocol 和 value-ranking 风险已冻结；本地 reward/value/success/termination artifact、校准曲线、paired candidate trace 与 ownership 仍缺。可以用 Cosmos/WAM、UWM/LIBERO、OpenPiVLA 和 Robot Harness 作为字段挂钩，但不能把公开 value score、离线 reward loss 或 benchmark success 写成个人闭环收益。

## 参考来源

1. [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html)。
2. [WM-021 Dreamer Imagination Source Freeze](vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)。
3. [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html)。
4. [Benchmark / Evidence claim-to-protocol audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
5. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
6. [WM-023 Open-loop / Receding-horizon Source Freeze](vol_04_wm023_open_loop_receding_horizon_source_freeze.html)。
