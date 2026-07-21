# VOL 04 WM-018 Source Freeze：Prediction / Execution / Replan Horizon

> 审计日期：2026-07-17  
> 状态：`source_frozen / horizon-contract / WARN`  
> 覆盖题目：`VLA-WM-018`  
> 本轮边界：只冻结 observation、prediction、execution、replan 与 imagination horizon 的定义、实现入口和实验矩阵；不生成 knowledge page，不生成题卡。

## 1. 问题与结论边界

题目：**prediction horizon 过短或过长如何影响可控性、细节与训练稳定性？**

回答前必须拆开至少五条时间轴：observation/history horizon、model prediction horizon、action execution prefix、policy replan interval、world-model imagination/planning horizon。它们可能数值相同，但语义不相同；仅说“horizon=16”无法判断模型预测、执行还是多久吸收一次新 observation。

冻结结论：

1. horizon 太短会削弱动作/未来序列的长期一致性，难以覆盖延迟 reward、接触过程和 demonstration 的 temporal structure；但 target 更近、误差更小、训练通常更容易稳定。[S1][S2]
2. horizon 太长增加 sequence coherence 与规划视野，同时扩大 compounding error、OOD rollout、stale action、显存/计算和 padding 比例；若 execution/replan 也变长，反馈纠错会变慢。[S1][S2][S3]
3. model prediction horizon 与 execution horizon 可解耦：Diffusion Policy 区分 (T_o,T_p,T_a)，ACT 在 temporal aggregation 下可保持长 prediction horizon 但每步 replan，Cosmos RoboCasa 可预测 32 步只执行前 16 步。[S2][S3][S4]
4. UWM 的 `action_len=16`、`num_frames=19`、`obs_num_frames=2` 是 frozen config；未来 observation 帧数与 action horizon 不应被当作所有任务的通用最优值。[S5]
5. horizon 优劣必须用 per-step error、open-loop rollout、action sensitivity、latency、closed-loop success 与 failure traces 联合判断；one-step MSE 不能外推长 horizon 可用性。[S1][S5]

## 2. 冻结来源

| ID | 来源 | frozen boundary | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | [World Model Foundations Audit](vol_04_world_model_foundations_claim_to_code.html) | World Models/PlaNet/DreamerV3 papers + DreamerV3 `e3f0224` audit | teacher-forced vs open-loop、compounding error、imagination/planning horizon、receding horizon | 本地 UWM/WAM 的最优 horizon | checked / WARN |
| S2 | [Diffusion Policy Audit](vol_03_diffusion_policy_claim_to_code.html) | repo `5ba07ac6661db573af695b419a7947ecb704690f` + paper | (T_o,T_p,T_a)、`horizon`/`n_action_steps`、sim/real replan、warm-start 边界 | 本地 OpenPiVLA 或 world-model 具体配置 | checked / WARN |
| S3 | [ACT Audit](vol_03_act_claim_to_code.html) | repo `742c753c0d4a5d87076c8f69e5628c79a8cc5488` + paper | (H)、query frequency、temporal aggregation、chunk 内 open-loop/边界闭环 | 所有 action chunk 模型都用 ACT 的 14D/100-step recipe | checked / WARN |
| S4 | [Cosmos/WAM Audit C](vol_04_cosmos_policy_wam_claim_to_code.html) | repo `18a2accadf4e7a3531e56754102af5a24d2316da` + paper/docs | LIBERO 16-step、RoboCasa 32-step prediction/16-step execution、planning compute | 用户 WAM runtime/horizon 已复现 | checked / WARN |
| S5 | [UWM Audit B](vol_04_uwm_video_action_claim_to_code.html) | repo `b7d4067c8859775e5b08f681e76d538015cdd445` | action_len/history/future shape、forward/inverse/joint proxy 与 metric boundary | `16` 是方法常数；proxy MSE 等于 success | checked / WARN |
| S6 | [WM-017 Schema Freeze](vol_04_wm017_heterogeneous_schema_source_freeze.html) | Open X/UWM schema boundary | timestamp、control Hz、valid-step/terminal mask、per-embodiment horizon | 本地 adapter/horizon A/B 已完成 | checked / WARN |

## 3. 五条时间轴

| 时间轴 | 符号 | 回答的问题 | 常见错误 |
| --- | --- | --- | --- |
| observation/history horizon | (T_o) | 模型读取多少历史 observation | 当成全部 episode history |
| prediction horizon | (T_p) / (H) | 模型一次预测多少未来 action/state slots | 当成真实执行步数 |
| execution prefix | (T_a) / (K) | 一次 query 后实际执行多少步 | 默认等于 prediction horizon |
| replan interval | (R) | 多久再次读取 observation 并推理 | 只从 model config 猜 |
| imagination/planning horizon | (H_{imag}) | latent/world model 向前 rollout 多远以算 value/return | 与视频 future frame 数混同 |

物理时间还要乘 control period：

\[
\Delta t_{pred}=T_p/f_{ctrl},\qquad
\Delta t_{exec}=T_a/f_{ctrl},\qquad
\Delta t_{replan}=R/f_{ctrl}.
\]

变量解释：(f_{ctrl}) 是控制频率。同样的 16 步，在 5 Hz 与 50 Hz 下分别是 3.2 秒和 0.32 秒；因此跨项目比较必须记录 control rate、action repeat、latency 和 timestamp，而不能只报 step 数。

## 4. 过短与过长的机制

| Horizon | 收益 | 风险 | 重点指标 |
| --- | --- | --- | --- |
| 较短 prediction | target 更近、padding 少、计算/显存低、误差较易控制 | 缺 sequence coherence、接触/延迟 reward 覆盖不足、频繁 query | one-step/per-step error、query latency、success |
| 较长 prediction | 捕获连续动作、接触阶段与长期结构；可供 planner/ensemble 选择 | compounding error、OOD latent、末端模糊/多模态平均、padding 与训练难度 | error-vs-offset、action sensitivity、open-loop rollout |
| 较短 execution/replan | 快速吸收新 observation，扰动恢复快 | inference/通信频繁、可能抖动 | latency/action age、controller smoothness |
| 较长 execution/replan | 推理摊销、chunk coherence | stale action、接触后继续执行错误计划 | failure offset、recovery、closed-loop success |
| 较长 imagination | value 看得更远 | model bias/optimizer exploitation 放大 | imagined-vs-real return、uncertainty/calibration |

## 5. 实现对照

### Diffusion Policy

frozen repo 将 prediction horizon 写为 `horizon=T_p`，返回步数由 `n_action_steps=T_a` 控制；simulation wrapper 一次执行 action batch，real eval 的 `steps_per_inference` 决定多久重算。论文提到 receding-horizon warm-start，但 frozen主要路径从 random noise 重启，不能写成默认实现。[S2]

### ACT

`chunk_size=num_queries=H` 决定一次输出多少 action slots。不做 temporal aggregation 时每 (H) 步 query 并顺序执行；开启 aggregation 时每步 query，把覆盖同一时刻的多个 chunk 预测加权，model horizon 长但 replan interval 可为 1。[S3]

### Cosmos/WAM 与 UWM

Cosmos LIBERO 默认 16×7 action chunk 并执行 16 步；RoboCasa 默认预测 32×7、执行前 16 步。UWM 默认 `action_len=16`，history/future frame 又由 `num_frames`/`obs_num_frames` 定义。三者都说明 prediction、future observation、execution 与 replan 必须分别记录。[S4][S5]

## 6. 最小实验矩阵

| 变量 | 建议 sweep | 必须固定 | 输出 |
| --- | --- | --- | --- |
| prediction horizon (T_p) | 4/8/16/32 或任务合理网格 | model size、data split、steps、normalizer | per-offset action/video error、memory、step time |
| execution prefix (T_a) | 1/4/8/16 | 同一 checkpoint 或 matched training | success、action age、recovery、latency |
| replan (R) | 1/4/8/16 | controller Hz、queue policy | stale-action failures、p50/p95 inference |
| imagination (H_{imag}) | short/medium/long | world/value checkpoint、planner budget | imagined-vs-real return、calibration |
| terminal padding | mask on/off | same batches/seed | loss、gradient、per-offset error |

不能只做单变量 loss sweep：horizon 改变有效 target 数、padding 比例和 compute budget，必须报告有效元素分母、训练 token/step、wall-clock 和 closed-loop protocol。

## 7. 项目与证据边界

- UWM/LIBERO 可讲 action_len/history/future、normalizer、reset、rollout protocol 和 DataLoader 证据；不能把 16 写成跨任务最优，也不能用 action/image MSE 证明长 horizon 可执行。
- WAM 可讲 LIBERO/RoboCasa 的 chunk/execution 差异与 0-success 诊断；没有 matched horizon sweep、checkpoint 与 episode trace，不能归因于 horizon。
- OpenPiVLA 的本地 horizon/replan/controller 需从 config、checkpoint、inference loop 和 eval summary 取证；ACT/Diffusion Policy 的公开设置不能替代个人项目事实。

## 8. Review 结论与下一步

本 source freeze 为 `WARN`：五条 horizon、物理时间换算、Diffusion Policy/ACT/Cosmos/UWM 代码边界和最小 sweep 已冻结；本地 matched horizon A/B、per-offset error、action-age/latency、closed-loop traces 与个人项目 lineage 仍 pending。

本轮已完成 `knowledge/vol_04_world_model_sim2real_wm018.*` 与 `questions/vol_04_world_model_sim2real_wm018.*`；下一步进行 WM-015..018 真实口述，WM-019..038 继续后置。

## 参考来源

1. [World Model Foundations Audit](vol_04_world_model_foundations_claim_to_code.html)。
2. [Diffusion Policy Audit](vol_03_diffusion_policy_claim_to_code.html)。
3. [ACT Audit](vol_03_act_claim_to_code.html)。
4. [Cosmos/WAM Audit C](vol_04_cosmos_policy_wam_claim_to_code.html)。
5. [UWM Audit B](vol_04_uwm_video_action_claim_to_code.html)。
6. [WM-017 Schema Freeze](vol_04_wm017_heterogeneous_schema_source_freeze.html)。
