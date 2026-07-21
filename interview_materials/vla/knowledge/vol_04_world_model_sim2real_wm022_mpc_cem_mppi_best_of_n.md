# VOL 04 World Model / Sim2Real：MPC、CEM/MPPI 与 Best-of-N（WM-022）

> 状态：`drafted / VLA-WM-022 / knowledge_24_of_44 / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：`VLA-WM-022`；本页比较候选规划范式，不声明本地 planner 结果。  
> 前置：[WM-021 Dreamer Imagination](vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.html)、[WM-022 Source Freeze](../sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html)。

## 问题（Question）

MPC、CEM/MPPI 与 best-of-N trajectory selection 的共同点和差异是什么？高分回答要拆开 proposal、scorer、更新/选择、执行 prefix、replan 和证据边界。

## 1. 共同抽象：候选—评分—执行

四者都可放进同一流程：

```text
current state/observation
        ↓
proposal: action sequences / trajectories
        ↓ world/value/reward/constraint scorer
selection or proposal update
        ↓ execute first step or prefix
        ↺ observe again and replan
```

共同点是候选搜索和闭环反馈，不是必须使用同一个 model 或 optimizer。实现上需要记录 candidate count (N)、planning horizon (H)、execution prefix (K)、scorer version、constraint/fallback 和 latency；不能只保存最终 top score。

## 2. MPC：闭环执行范式

Model Predictive Control（MPC）通常在每个时刻用 dynamics/world model 预测候选未来，优化有限 horizon 的目标，只执行第一步或短 prefix，再读取新 observation 重复规划：

\[
\mathbf a^*_{t:t+H-1}=\arg\max_{\mathbf a}J(\hat s_{t:t+H}),\qquad
\text{execute }a^*_t\text{ or }a^*_{t:t+K-1}.
\]

变量解释：(hat s) 是模型预测状态，(J) 是 reward/value/constraint 组合，(H) 是 planning horizon，(K) 是 execution prefix。MPC 的关键是反馈频率与 stale-action 控制，而不是某个特定采样器。模型偏差越大，通常越需要缩短 (K) 或加强 real observation 校正。[1]

## 3. CEM：用 elite 更新 proposal 分布

Cross-Entropy Method（CEM）从 action-sequence 分布 (q_eta(mathbf a)) 采样，使用 model/value scorer 评估，保留 top-(\rho) 的 elite，再用 elite 的均值/协方差更新 (q_eta)，重复若干轮：

\[
\eta_{j+1}=\operatorname{Fit}\left(\operatorname{Elite}_\rho\{\mathbf a_i,J_i\}\right).
\]

它的高分点是：CEM 是 proposal optimizer，可嵌入 MPC；多峰动作若用单一 Gaussian 可能早熟收缩；sample budget、elite ratio、协方差下界和随机 seed 都影响结果。CEM score 高不等于真实任务 success，必须保存 selected/unselected candidate 和 real outcome。

## 4. MPPI：带代价权重的采样控制

Model Predictive Path Integral（MPPI）通常围绕 nominal control 加噪声生成轨迹，按 cost/return 权重更新控制序列，并滚动执行。与 CEM 的直观区别是：CEM 以 elite 集合拟合 proposal；MPPI 更强调连续 cost-weighted update、噪声协方差、temperature 和控制平滑。具体公式、离散化、约束和温度必须以实现为准，不能把 source ledger 的方法名当作某个项目的 exact implementation。

面试中应追问：cost 单位是否归一化？noise covariance 是否与 action unit 匹配？temperature 变化是否改变探索/最优解？控制器是否能执行 clip、rate limit、collision/safety constraint？

## 5. Best-of-N：选择器而不是完整 planner

Best-of-N 一次生成 (N) 个候选 trajectory，用 value/reward/success/constraint scorer 选最高者：

\[
\hat\tau=\arg\max_{i\in\{1,\ldots,N\}}S(\tau_i).
\]

它可以和 MPC、CEM、MPPI 组合：例如 CEM 产生候选、best-of-N 做最终筛选，或每次 MPC replan 都选 N 条 trajectory。N 增大时，若 scorer 有偏，越容易选中 hallucination/过高 value 的候选（optimizer’s curse），同时 planning latency、通信和显存增加。因此要做 N sweep、rank calibration、random/median/top selector 和 selected-vs-unselected real trace。[2][3]

## 6. 方法对照

| 方法 | proposal | 更新/选择 | 典型执行 | 主要风险 |
| --- | --- | --- | --- | --- |
| MPC | 优化或采样 sequence | 每次重新求解 | first step/prefix + replan | model bias、latency、controller mismatch |
| CEM | 分布采样 | elite 拟合 mean/cov | 可作为 MPC 内层 | premature collapse、多峰丢失 |
| MPPI | nominal + noise trajectories | cost-weighted control update | 滚动控制 | temperature/noise/scale 错配 |
| best-of-N | N 个独立候选 | scorer 排序取 top | 一次执行或交给 MPC | scorer bias、N 放大 optimism |

## 7. 协议与失败诊断

| 失败模式 | 最小诊断 | 需要保存 |
| --- | --- | --- |
| model overoptimism | N/H sweep、OOD/disagreement、selected/unselected paired rollout | checkpoint、seed、candidate traces |
| scorer mismatch | rank correlation、calibration、task predicate 对齐 | scorer version、success predicate |
| proposal collapse | elite entropy、multi-seed、mixture/diversity | proposal stats、elite ratio |
| scale/temperature 错误 | action/cost unit A/B、noise/temperature sweep | normalizer、cost scale、dtype |
| stale action/latency | p50/p95 planning time、queue、action age、replan count | timestamped trace、controller log |
| infeasible command | clipping、rate limit、collision/fallback trace | feasibility mask、safety event |

## 8. 可审计伪代码

```python
def plan_with_candidates(model, state, protocol):
    # 1. Freeze checkpoint, normalizer, seed, horizon, prefix and scorer revision.
    proposals = propose_sequences(state, protocol)

    # 2. Roll every proposal through the same world/value model and constraints.
    scored = score_trajectories(model, proposals, protocol)

    # 3. Select top candidate or update CEM/MPPI proposal distribution.
    selected, update = select_or_update(scored, protocol.optimizer)

    # 4. Execute only the permitted prefix, record latency and replan metadata.
    action = execute_prefix(selected, protocol.execution_prefix)
    return action, scored, update
```

这段伪代码不能产生项目指标；必须额外记录 selected/unselected trajectories、real/sim episode outcome 和 latency budget。

## 9. 项目挂钩与真实性边界

- Cosmos/WAM：可连接 action/future/value slots、best-of-N、LIBERO/RoboCasa protocol 与 offline proxy；不能把公开分数或未核验 checkpoint 写成个人 planning uplift。
- UWM/LIBERO：可连接 horizon、normalizer、fixed/reset protocol 与 rollout wrapper；不能把 protocol-limited result 当作通用 MPC/CEM 结论。
- OpenPiVLA、OPD、Robot Harness：可挂接 action schema、scorer、timeout、episode trace 和接口审计，但不支持个人已经实现 CEM/MPPI 的 claim。

## 10. 结论与下一步

MPC 是闭环执行范式，CEM/MPPI 是候选 proposal/optimizer，best-of-N 是 scorer-based selector；它们可以组合但不能互相替代。比较时必须冻结 N/H/K、proposal、scorer、controller、latency、reset 和分母，并用 selected-vs-unselected、sim/real paired trace 防止 model/scorer optimism。当前节点保持 `WARN`，题卡已同步并保持 `unseen`；下一步进行真实口述或补一个 planning artifact。

## 参考文献（References）

1. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)。
2. [Cosmos Policy / WAM claim-to-code audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
3. [WM-022 Source Freeze](../sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html)。
4. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)。
