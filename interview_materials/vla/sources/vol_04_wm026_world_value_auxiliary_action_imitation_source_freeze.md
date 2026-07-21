# VOL 04 WM-026 Source Freeze：World/Value Auxiliary 为什么可能帮助 Action Imitation

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-026 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-026  
> 本轮边界：冻结 shared representation、额外监督、task-progress signal、gradient alignment 与 matched ablation 的机制；不声称 world/value auxiliary 必然改善 action imitation，或已在用户 WAM 项目产生收益。

## 1. 结论先行

1. **World auxiliary 可能让共享表示保留动作后果。**仅做 action imitation 容易拟合局部动作均值、重复前一动作或背景相关性；预测 action-conditioned future 会额外约束可控物体、接触状态和任务阶段，但前提是 future target 与控制相关而非只奖励视觉细节。[S1][S2]
2. **Value auxiliary 可能提供 task-progress 与 failure signal。**return/value 让共享表示区分“看起来相似但离成功可达性不同”的状态；若 label 噪声、reward scale、OOD calibration 或 success semantics 错，它也会把 action 表示带偏。[S1][S3]
3. **多任务监督可能充当 regularizer 和数据扩展。**demo/rollout 的不同角色增加共享 backbone 看到的状态分布，可能减轻过拟合；若 auxiliary 数据分布与 policy 不匹配、比例过高或 capacity 不足，则会负迁移。
4. **机制成立不等于因果收益已证明。**需要 action-only、+world、+value、all 的 matched ablation，固定初始化、数据、总 updates/compute、normalizer 和 eval protocol，并同时报告 action proxy、future/value quality 与 closed-loop success。
5. **梯度相容性只是诊断，不是充分条件。**共享参数上 action gradient 与 auxiliary gradient 的 cosine、norm 和更新占比可发现冲突；正 cosine 不保证闭环提升，负 cosine 也不自动要求删掉目标，必须结合表示 probe 和 paired rollout。

## 2. 来源冻结

| ID | 来源 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- |
| S1 | Cosmos Policy / WAM claim-to-code audit | unified action/future/value latent contract、demo/rollout routing、shared backbone、component metric 与 direct/planning boundary | auxiliary 对 action 的独立因果收益、用户本地 uplift | primary + official-code audit / WARN |
| S2 | WM-025 Slot/Mask/Loss Source Freeze 与 WM-016 Joint Objective | slot、routing、condition/target mask、EDM loss、gradient/reduction 和 action-only/+world/+value/all 审计模板 | generic additive loss 是 Cosmos exact implementation | supporting / WARN |
| S3 | WM-024 Reward/Value/Success/Termination | value/return、success、termination 和 calibration 语义 | value label 一定可靠或等于成功概率 | supporting / WARN |
| S4 | UWM Video/Action audit 与 WM-015 Coupling | action-video conditional coupling、shared diffusion representation、action-free/robot tuple 边界 | Cosmos 与 UWM 使用相同 loss/slot，用户 UWM/WAM 已验证 transfer | primary + official-code audit / WARN |
| S5 | WAM Claim–Evidence Inventory | action-only/+world/+value/all 仅为待补 ablation；local config/checkpoint/metric/ownership 缺口 | 历史 MSE、成功率或 root cause 已核验 | local evidence / WARN |
| S6 | WM-019 Metric Boundary | offline action/future/value proxy 与 closed-loop success 的证据阶梯 | component loss 下降即可证明 action 或 success 改善 | supporting / WARN |

## 3. 三条“可能帮助”的机制

### 3.1 控制相关表示

设共享 encoder/backbone 产生 \(h_\theta(s_t)\)。action-only 目标只约束：

\[
\mathcal L_a=\ell_a\left(f_a(h_\theta(s_t)),a_t^\*\right).
\]

加入 action-conditioned future：

\[
\mathcal L_w=\ell_w\left(
f_w(h_\theta(s_t),a_{t:t+K-1}),s'_{t+K}
\right).
\]

变量解释：\(a_t^\*\) 是示范动作，\(s'_{t+K}\) 是 future observation proxy；\(\mathcal L_w\) 可能迫使 \(h_\theta\) 保留动作会改变的对象、接触与阶段。但若 \(\ell_w\) 主要优化背景/像素细节，或者模型忽略 action，表示收益并不成立。

### 3.2 Task-progress 与失败可达性

value objective 可写成：

\[
\mathcal L_v=\ell_v\left(f_v(h_\theta(s_t),a_t,s'_{t+K}),G_{t+K}\right).
\]

变量解释：\(G_{t+K}\) 是指定 reward/termination contract 下的 return。它可能为 action imitation 提供“当前行为是否把任务推向成功”的语义；但 return scale、failure rollout、horizon、timeout、classifier/value calibration 任一错误都会产生 shortcut。

### 3.3 数据覆盖与正则化

Cosmos recipe 将 demos、success rollout、failure rollout 分配给 policy/world/value roles，共享 backbone 获得比纯 demo imitation 更广的状态分布。[S1] 这可能提升 recovery/OOD representation；同时也可能因 rollout distribution、标签质量和 role ratio 与 policy 不匹配而污染 action。

## 4. 梯度相容性诊断

对共享参数 \(\theta_s\)：

\[
g_a=\nabla_{\theta_s}\mathcal L_a,\qquad
g_{\mathrm{aux}}=\lambda_w\nabla_{\theta_s}\mathcal L_w+
\lambda_v\nabla_{\theta_s}\mathcal L_v,
\]

\[
\operatorname{align}=
\frac{g_a^\top g_{\mathrm{aux}}}
\lVert g_a\rVert_2\lVert g_{\mathrm{aux}}\rVert_2+\epsilon}.
\]

变量解释：align 接近正值表示当前 batch 上更新方向相容，负值表示局部冲突；还要记录各 layer/head 的 norm、shared parameter update ratio、role frequency 和 AMP/DDP reduction。该指标只用于定位，不是 performance theorem。

需要分别检查：

- shared trunk 与 modality/slot-specific projection 的 gradient；
- demo/world/value role 的 per-batch 与 moving-average alignment；
- loss scale 改变后 action gradient 是否被 auxiliary 淹没；
- zero/empty target mask、padding 和 distributed denominator 是否制造假冲突。

## 5. Matched ablation 合同

| Arm | 训练目标 | 目的 |
| --- | --- | --- |
| A | action-only | 控制基线 |
| B | action + world | 检验 action consequence 表示 |
| C | action + value | 检验 task-progress/value signal |
| D | action + world + value | 检验组合与交互 |
| E | action + shuffled world/value label | 排除仅因额外 compute/regularization |
| F | frozen shared trunk / stop-gradient auxiliary | 区分表示更新与 head-only 拟合 |

必须固定或显式匹配：

1. base checkpoint、data split、demo/rollout identity、总 token/sample count；
2. optimizer、LR schedule、total updates、batch、AMP/DDP、wall-clock/compute budget；
3. action schema、normalizer、slot layout、mask/reduction、seed；
4. task/init/controller/chunk/horizon/success predicate、episode denominator；
5. checkpoint selection 规则，避免每个 arm 取不同“最好”点。

如果 auxiliary arm 使用更多 rollout 数据或计算，应提供同数据量/同 compute 的 action-only control，而不是把资源增量误归因为 objective。

## 6. 指标阶梯

| 层 | 指标 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| optimization | main loss、gradient norm/alignment | 目标进入反向、是否冲突 | action 更准确 |
| action proxy | action MAE/MSE、repeat baseline、per-dim/per-step | frozen split 上 imitation quality | closed-loop recovery |
| actionability | action swap/sensitivity、counterfactual future | future 对 action 有响应 | 真实动力学正确 |
| world/value | per-offset future error、value MAE/calibration/rank | auxiliary target quality | policy 因果增益 |
| closed loop | per-task success、first-failure stage、recovery | 固定 protocol 下系统效果 | 单独归因 world 或 value |

结论要求：

- B 优于 A 但 future proxy 不改善：可能是 regularization/compute，不足以说“学会 dynamics”。
- future/value proxy 改善但 action/closed-loop 不变：auxiliary 学会自身任务，没有 transfer。
- action proxy 改善但 closed-loop 不变：可能是 denominator、contact、normalizer、recovery 或 metric mismatch。
- D 优于 B/C：仍需 interaction/gradient 证据，不能直接说 synergy。

## 7. 何时可能负迁移

| 风险 | 症状 | 最小检查 |
| --- | --- | --- |
| world 学视觉 shortcut | future 清晰但 action sensitivity 低 | action swap、foreground/contact probe |
| value label 噪声 | value loss 降、rank/calibration 差 | reliability、failure rollout audit |
| gradient conflict | auxiliary loss 降、action loss/grad 变差 | layer-wise cosine/norm、loss-scale sweep |
| role imbalance | action batch/update 被稀释 | effective role count、token/update budget |
| capacity competition | shared trunk 被 world pixel detail 占满 | width/freeze/head-only control |
| terminal padding | 尾部 repeated action/future 虚低 loss | valid-step mask A/B |
| domain mismatch | rollout auxiliary 伤害 demo policy | per-source holdout、domain-conditioned stats |

## 8. 项目真实性边界

WAM inventory 已明确：action-only/+world/+value/all 是待补实验，当前没有 exact local config、可加载 checkpoint、metric bundle、paired closed-loop episode 和 ownership ledger。历史 45% MSE、任务成功率、0-success 与 root-cause 均不能用作 WM-026 已验证证据。

安全表达：

> “world/value auxiliary 的机制假设是让共享表示保留 action consequence 与 task progress；我会用 matched objective ablation、gradient alignment、action sensitivity、value calibration 和 closed-loop trace验证，而不是从 component loss 推断收益。”

## 9. Source gate 结论

本 source freeze 为 WARN：表示、value signal、数据覆盖、gradient alignment、matched ablation、metric ladder 和负迁移矩阵已冻结；用户 WAM 的本地 paired experiment、checkpoint、raw metric、episode 与 ownership 仍缺。下游知识页与题卡只能回答“为什么可能”和“如何证明”，不能回答“已经提升多少”。

## 参考来源

1. [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html)。
2. [WM-025 Slot / Mask / Loss Source Freeze](vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。
3. [WM-016 Joint Objective Source Freeze](vol_04_wm016_joint_objective_source_freeze.html)。
4. [UWM Video / Action audit](vol_04_uwm_video_action_claim_to_code.html)。
5. [WM-024 Reward / Value / Success / Termination](../knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)。
6. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
