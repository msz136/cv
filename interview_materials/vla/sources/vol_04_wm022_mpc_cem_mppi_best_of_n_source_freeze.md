# VOL 04 WM-022 Source Freeze：MPC、CEM/MPPI 与 Best-of-N Trajectory Selection

> 审计日期：2026-07-18  
> 状态：`source_frozen / VLA-WM-022 / knowledge_synced / card_synced / WARN`  
> 覆盖题目：`VLA-WM-022`  
> 本轮边界：冻结 model-based planning、CEM/MPPI、best-of-N 的共同抽象、差异、计算合同与失败边界；不把公开 benchmark 或用户项目数字写成个人 planning 结果。

## 1. 问题与结论边界

题目：**MPC、CEM/MPPI 与 best-of-N trajectory selection 的共同点和差异是什么？**

冻结结论：

1. 三者都可被看作“生成候选 action/trajectory → 用 model/value/reward scorer 评价 → 选择或更新 proposal → 执行”的候选规划框架；共同目标不是某个固定网络结构。[S1][S2][S3]
2. MPC 是闭环执行范式：通常只执行第一步或短 prefix，重新观测后再规划；CEM 是对 action-sequence 分布反复采样、精英筛选和参数更新；MPPI 用带代价/奖励权重的采样轨迹更新控制序列，常强调平滑、噪声和实时性。[S1][S2]
3. best-of-N 通常一次生成 N 个候选，再按 value/reward/成功概率/约束 scorer 选 top；它可与 MPC、CEM、MPPI 组合，但 N 增大也会放大 value overestimate、模型漏洞与 latency。[S3][S4]
4. 规划质量必须绑定 proposal、world/value checkpoint、horizon、execution prefix、controller、reset/init、seed、scorer 和 episode denominator；只报 best score 不能证明闭环提升。[S4]

## 2. 来源冻结

| ID | 来源 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- |
| S1 | PlaNet / World Model Foundations Audit A | latent-space planning、CEM、receding horizon、model bias 与 candidate rollout | 所有 MPC 都使用 CEM、用户项目已经完成 planning | primary / WARN |
| S2 | [MPPI / Cautious MPC source ledger](vol_04_world_model_sim2real_sources.md) | MPPI/cautious sampling、trajectory cost、实时与风险门设计方向 | 任意实现的 exact hyperparameter 或 formal safety certificate | supporting / WARN |
| S3 | [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html) | action/future/value outputs、best-of-N、proposal/value/ranking、LIBERO/RoboCasa protocol | 官方分数是用户本地收益、checkpoint/dataset revision 已复现 | official-code-checked / WARN |
| S4 | [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html) | imagined/open-loop/proxy/simulator/real 分层、paired protocol、latency/denominator 边界 | best-of-N 分数等于真实 success 或独立因果提升 | supporting / WARN |
| S5 | [WM-021 Dreamer Imagination](vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html) | model bias、OOD imagined state、uncertainty/replan/pessimism 防护 | planning selector 已在用户项目验证 | supporting / WARN |

## 3. 共同抽象与差异

| 方法 | proposal 如何产生 | scorer/更新 | 执行方式 | 主要风险 |
| --- | --- | --- | --- | --- |
| MPC | 优化/采样未来 action sequence | 每次重算，通常只执行 prefix/第一步 | receding horizon | latency、model bias、controller mismatch |
| CEM | 从参数分布采样，保留 elite，更新 mean/cov | elite statistics 迭代更新 | 可作为 MPC 内层 optimizer | sample budget、早熟/多峰丢失 |
| MPPI | 在 nominal control 周围加噪声轨迹 | cost-weighted exponential update，常带平滑/动力学约束 | 适合滚动实时控制 | temperature、噪声、cost scale、风险过度乐观 |
| best-of-N | 独立生成 N 个候选 | 只按 scorer 排序选择 top | 可一次执行或交给 MPC | optimizer's curse、scorer bias、N/latency 放大 |

## 4. 协议合同

比较方法前固定：model/world/value checkpoint、candidate N、planning horizon、execution prefix、control frequency、action normalization、proposal seed、scorer version、constraint/fallback、reset/init、controller、latency budget 与 episode denominator。候选选择还要保存 selected/unselected trajectories，才能判断 scorer 是否真的排序正确。

`WARN` 边界：本仓库当前没有统一 planning runtime、same-checkpoint N sweep、selected-vs-unselected real episodes 或用户 ownership artifact；以下只是 interview-ready design。

## 5. 失败模式与最小诊断

| 失败 | 症状 | 诊断 |
| --- | --- | --- |
| model overoptimism | N/H 增大 imagined score 上升，real success 下降 | N/H sweep、OOD/disagreement、selected-vs-unselected paired rollout |
| scorer mismatch | value 排名与 task success 相关性低 | rank correlation、calibration、failure predicate 分层 |
| CEM premature collapse | elite 过早集中，错过多峰方案 | elite entropy、multi-seed、mixture/proposal diversity |
| MPPI scale error | cost/temperature/normalizer 变化导致控制失稳 | cost unit、noise covariance、temperature A/B |
| latency/stale action | proposal compute 超预算，执行时 observation 过期 | p50/p95 planning latency、queue、action age、replan count |
| controller mismatch | planned action 在执行器上不可达 | action clipping、feasibility、controller trace、fallback |

## 6. Source gate 结论与下一步

本 source freeze 为 `WARN`：共同抽象、CEM/MPPI/MPC 差异、best-of-N 组合方式和 protocol/failure 边界已冻结；本地 planner runtime、checkpoint、N/H sweep、selected-vs-unselected episodes 与 ownership 仍缺。下游 knowledge 与题卡已同步，题卡保持 `unseen`；下一步进行真实口述或补一个 planning artifact。

## 参考来源

1. [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html)。
2. [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html)。
3. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
4. [WM-021 Dreamer Imagination](vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)。
5. [World Model source ledger](vol_04_world_model_sim2real_sources.md)。
