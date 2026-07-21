# VOL 04 WM-016 Source Freeze：Action / Video Joint Objective 审计

> 审计日期：2026-07-17  
> 状态：`source_frozen / UWM-and-Cosmos-boundary / WARN`  
> 覆盖题目：`VLA-WM-016`  
> 本轮边界：只冻结来源、claim、代码映射和待验证实验；不生成 knowledge page，不生成题卡，不把 UWM 与 Cosmos/WAM 拼成一个实现。

## 1. 题目与结论边界

`VLA-WM-016` 要回答：**action/video joint objective 的共享表示、condition、noise schedule 和 mask 应怎样审计？**面试中最容易混淆的是“共享 backbone”“联合生成”“condition mask”“loss mask”这四个词。它们分别属于表示/网络、采样分布、输入条件语义和目标聚合语义，不能互换。

本轮冻结的最小结论：

1. UWM 用共享 diffusion transformer 交互 action 与 future-video token，两个 modality 有独立 timestep；frozen code 的 action/video MSE 聚合与 `action_mask` 语义必须分开审计。
2. Cosmos/WAM 将 action、future observation、value/proprio 等写入统一 latent-video slot，并通过 sample routing、condition mask 和可选 target mask 控制不同任务；其 EDM/`x_0` 预测、slot mask 和 UWM 的 epsilon-prediction 不能直接等式替换。
3. “mask=1”没有跨项目统一含义：Cosmos 的 condition mask 中 `1` 表示 clean condition；UWM 的 `action_mask` 是 sample-level 标记，当前实现只影响 action timestep，不自动证明 action loss 被排除。
4. 联合目标是否真正帮助 policy，必须用固定 checkpoint、数据 split、normalizer、scheduler、seed 与 closed-loop protocol 做 action-only / action+video / action+value 的 paired ablation；单看 component loss 不足以归因。

## 2. 冻结来源清单

| ID | 来源 | 类型 / revision | 可支持的断言 | 不能支持的断言 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html) | 本仓库 canonical audit；依据 UWM repo `b7d4067c8859775e5b08f681e76d538015cdd445` | shared DiT、dual timestep、robot/video tuple、当前 action MSE 与 `action_mask` 边界 | 本地 checkpoint、mask ablation、个人 UWM 结果 | checked / WARN |
| S2 | [UWM 独立事实复核](vol_04_uwm_independent_fact_review.html) | frozen raw-source review；同一 UWM commit | raw config/model/train/wrapper 的复核结果、license/checkpoint/runtime 风险 | scheduler endpoint 的本地数值 smoke、gradient 实验 | checked / WARN |
| S3 | [Cosmos/WAM Source Audit C](vol_04_cosmos_policy_wam_claim_to_code.html) | 本仓库 canonical audit；Cosmos Policy repo `18a2accadf4e7a3531e56754102af5a24d2316da` | latent slot、condition/sample routing、EDM `x_0` prediction、可选 target mask、action multiplier、value/world 分支 | 某个 model card 结果等于本地 WAM run；所有 config 都打开 target mask | checked / WARN |
| S4 | [Cosmos Policy 论文](https://arxiv.org/html/2601.16163v1) | primary paper `2601.16163v1` | action/future/value 的统一 latent-video 设计、policy/planning 角色边界 | 用户项目贡献、未冻结 checkpoint 的复现 | checked / WARN |
| S5 | [UWM 论文](https://arxiv.org/abs/2504.02792v3) 与 [官方项目页](https://weirdlabuw.github.io/uwm/) | primary / first-party | action-free tuple、统一 policy/forward/inverse/video 语义 | full-text equation 的所有实现细节、个人结果 | checked / WARN |
| S6 | [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [WAM inventory](../evidence/projects/wam_claim_evidence_inventory.html) | local evidence boundary | checkpoint、normalizer、score、ownership 的缺口 | 用项目页数字证明 joint objective 有效 | checked / WARN |

## 3. Claim → code 对照

| 审计维度 | UWM frozen behavior | Cosmos/WAM frozen behavior | 面试安全表述 |
| --- | --- | --- | --- |
| 共享表示 | action MLP、video patchifier、registers 与 observation condition 进入共享 AdaLN/DiT blocks，输出 action decoder 与 video unpatchifier | action/proprio/future/value 写入统一 latent-video frame/slot，角色由 routing 与 condition 决定 | 都有 cross-modality interaction，但 token/latent contract 不同 |
| condition | observation 是 global condition；clean action 或 clean future 可作为另一 branch 的 condition | clean frame/slot 通过 condition mask 固定，sample mask 决定需 denoise 的 slot | condition mask 是输入/采样语义，不等于 loss mask |
| noise / target | 两路独立 timestep，frozen UWM 主要按 epsilon noise prediction 组织 MSE | Hybrid EDM 产生 noisy latent，denoiser 输出 `x_0`；日志 component L1/MSE 不等于主 noise-weighted loss | 先确认 prediction target，再比较 loss |
| sample routing | robot tuple 与 action-free video tuple；video 样本 action timestep 置高噪声 | policy/world/value/V/Q 变体由 sample routing 和 slot mask 选择 | routing 决定任务分布，不能只看 batch 名称 |
| loss mask | 当前 frozen code 的 action MSE 未显式按 `action_mask` 乘零；需 gradient/A-B 实验确认影响 | 可选 `mask_loss_for_action_future_state_prediction`、`action_loss_multiplier` 等分支，主 config 是否开启要逐项核对 | 看到 mask 名称后必须查调用点、reduction 与 config |
| 结果指标 | action/image MSE 是 conditional proxy；不替代 rollout success | component L1/MSE、direct policy success、planning uplift 语义不同 | metric ladder 先分层，再做因果归因 |

## 4. 统一审计框架（不是统一实现）

可以用一个抽象合同描述审计对象：

\[
\mathcal{L}=\sum_{m\in\mathcal{M}}\frac{\sum_{b,t,d}M^{(m)}_{btd}\,\ell^{(m)}(\hat y^{(m)}_{btd},y^{(m)}_{btd})}{\max(1,\sum_{b,t,d}M^{(m)}_{btd})}.
\]

变量解释：(m) 是 modality/task（action、video、future、value 等），(M^{(m)}) 是真正参与 reduction 的 target mask，(ell^{(m)}) 是与 prediction target 匹配的逐元素损失。这个式子是审计模板，不声称 UWM 与 Cosmos 都采用同一 denominator；代码中必须核对 reduction、weight、mask 以及是否只改输入 timestep。

对 UWM，当前源码支持的具体检查是：分别记录 `action_mask`、`action_t`、`video_t`、`action_noise_pred`、`video_noise_pred`，确认 `F.mse_loss` 的输入和 reduction，再做显式 target-mask A/B。对 Cosmos/WAM，则要分别记录 slot condition mask、sample routing、EDM sigma、`mask_loss_for_action_future_state_prediction`、`action_loss_multiplier` 与 value/policy flags；不能把 `mask=1` 直接代入上式当作同一 (M)。

## 5. 最小证据与实验队列

| 优先级 | 检查 | 目的 | 当前状态 |
| --- | --- | --- | --- |
| P0 | 打印 UWM 一个 robot batch 与一个 action-free batch 的 `action_mask/action_t/video_t`、各项 loss 和 gradient norm | 证明 timestep 改动与 loss mask 是否分离 | pending；无本地 runtime/checkpoint |
| P0 | UWM 显式 action target mask A/B：原实现 vs `where(action_mask, loss, 0)`，固定 seed/normalizer | 识别 action-free video 对 action branch 的真实梯度影响 | pending |
| P0 | Cosmos/WAM 逐 config 记录 condition mask、target mask、sample routing、sigma 与 reduction | 识别 clean condition、denoise target、loss mask 的语义 | pending；主实验 config/weights 未完整冻结 |
| P1 | action-only / action+video / action+value paired fine-tune，固定 data split、checkpoint、scheduler、steps | 判断 auxiliary objective 是否有因果收益 | pending |
| P1 | component loss、action sensitivity、future error、closed-loop success 四层同时报告 | 防止 proxy metric 代替 policy success | pending |
| P1 | modality/slot permutation、zero-action、future perturbation、gradient cosine | 发现 action ignoring、shortcut 与 gradient conflict | pending |
| P2 | scheduler endpoint / sigma schedule numerical smoke 与 backend parity | 排除采样端点、dtype、runtime 差异 | pending |

## 6. 个人项目边界

- UWM/LIBERO inventory 只能支持 fixed-pruned-init、reset style、normalizer、checkpoint/runtime 缺口和已有报告的证据等级；不能把上游 shared DiT 或 WM-016 的 joint objective 写成本人原创。
- WAM inventory 允许讨论 source-level latent routing、value/world/policy 角色和 0-success 的诊断队列；在缺少 immutable checkpoint、prediction artifact、episode trace 和 ownership artifact 前，不升级为已复现个人结果。
- “action loss 下降”“future 画面更好”“value MAE 下降”只能作为局部信号；面试回答必须继续追问 paired closed-loop success、failure taxonomy 和 protocol parity。

## 7. Review 结论与下一步

本 source freeze 结论为 `WARN`：UWM 与 Cosmos/WAM 的主要代码边界已冻结，`mask`、prediction target、routing、reduction 和 metric ladder 的审计问题已列出；但 runtime gradient、checkpoint lineage、paired ablation、scheduler smoke 与 browser visual QA 尚未完成。

本轮不生成 `knowledge/vol_04_world_model_sim2real_wm016.*` 或 `questions/vol_04_world_model_sim2real_wm016.*`。下一步只能二选一：

1. 候选人先口述 `VLA-WM-015`，再按真实回答更新训练状态；或
2. 在本 source freeze 基础上生成一个 `WM-016` knowledge node，再单独生成一张保持 `unseen` 的题卡。

## 8. 参考来源

1. [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html)。
2. [UWM 独立事实复核](vol_04_uwm_independent_fact_review.html)。
3. [Cosmos/WAM Source Audit C](vol_04_cosmos_policy_wam_claim_to_code.html)。
4. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
5. [WAM evidence inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM official project page](https://weirdlabuw.github.io/uwm/)。
7. [Cosmos Policy paper](https://arxiv.org/html/2601.16163v1)。
