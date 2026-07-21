# VOL 04 WM-028 Source Freeze：Routing、Slot Mask 与 Loss Weight 防污染合同

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-028 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-028  
> 本轮边界：冻结 sample routing、condition/target/valid/metric mask、reduction 与 effective weight 的分层合同，并独立回查 frozen Cosmos commit；不声称推荐的 valid mask/per-role normalization 已存在于上游或用户 WAM，也不声称某种比例/权重已提升闭环。

## 1. 结论先行

1. **Routing 决定样本承担什么角色。**demo、world rollout、value rollout 的来源、比例和 label 语义必须先确定；loss weight 不能把错误 role 变正确。[S1][S2]
2. **Condition mask 与 target mask 控制不同信息流。**condition mask 决定哪些 slot 作为 clean input，target mask 决定哪些预测误差进入反向；valid/padding mask 决定 target 是否真实有效，metric mask 只决定日志统计。四者不能复用一个字段。[S2][S3]
3. **Effective weight 不等于配置里的 \(\lambda\)。**采样概率、每个 role 的 active slot 数、每 slot 元素数、noise weight、reduction denominator 和显式 multiplier 共同决定实际 loss/gradient share。
4. **Frozen Cosmos base recipe 并未默认做 role-isolated target masking。**配置类中 `mask_loss_for_action_future_state_prediction=False`、`mask_value_prediction_loss_for_policy_prediction=False`、`action_loss_multiplier=1`，基础 LIBERO/RoboCasa experiment config 没有覆写；因此 optional branch 不能写成所有官方 checkpoint 的既定行为。[S2]
5. **Frozen target mask 后仍做 full-tensor mean。**代码先将 `final_mask_B_T` 乘到 EDM loss，再对整个 \(B\times C\times T\times H\times W\) 求 mean；active slot 少的 role 会被隐式降权。若要比较 per-role normalized objective，必须明确这是新的设计/消融，不是 frozen exact loss。[S2]
6. **WAM 本地 resolved config 仍缺。**没有 local config、checkpoint、mask dump、role histogram、loss denominator、gradient/paired episodes 和 ownership，不能说“本人已通过 routing/mask/weight 消除污染”。[S5]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Kim et al., *Cosmos Policy* + claim-to-code audit | arXiv:2601.16163v1；paper CC BY 4.0 | policy/world/value 概率角色、约 50/25/25 base routing、joint latent contract | 所有 run 使用同一比例；用户本地结果 | primary / WARN |
| S2 | `NVlabs/cosmos-policy` official code | commit `18a2accadf4e7a3531e56754102af5a24d2316da`，Apache-2.0 | dataset role flags、condition mask、target-mask branches、defaults、global mean reduction、action multiplier | 用户 resolved override、checkpoint 兼容性、local execution | official-code / checked |
| S3 | WM-025 Slot / Mask / Loss Source Freeze | 本地 canonical + review | slot layout、四类 mask、EDM/component metric 边界与基础单测 | WM-025 审计化归一式是 frozen exact reduction | supporting / WARN |
| S4 | WM-027 Negative Transfer / Gradient Conflict | 本地 canonical + review | contract-first 顺序、norm/gradient share 与 matched outcome | gradient surgery 可以修 routing/mask bug | supporting / WARN |
| S5 | WAM Claim–Evidence Inventory | 2026-07-18 | local diagnostic 边界和 config/checkpoint/mask/gradient/ownership 缺口 | historical metrics 或污染根因已确认 | local-evidence / WARN |

### 2.1 Frozen 文件与 SHA

| 文件 | 作用 | SHA-256 |
| --- | --- | --- |
| `cosmos_policy/datasets/libero_dataset.py` | demo/rollout routing、world/value role、slot index、return | `0114300e72ab52acc0946cc4563aef8af924cc5c2413a4c2329c1f0eade9fe02` |
| `cosmos_policy/datasets/robocasa_dataset.py` | 同上；显式 `p_world_model` | `2c4e5f0d2e05647a9ed573b671e7966fbd55683697c7bb105418ba33ed661004` |
| `cosmos_policy/models/policy_video2world_model.py` | role-conditioned clean input mask | `13312470552a9fe9b6a8915f214331902b455a279fd985b9121683c484622eb2` |
| `cosmos_policy/models/policy_text2world_model.py` | target mask、multiplier、EDM loss 与 reduction | `cd7cc70b831fedd56be4fb474916250c372c6fcea1c44730600ee1a7d73987c4` |
| `cosmos_policy/config/experiment/cosmos_policy_experiment_configs.py` | base LIBERO/RoboCasa dataset routing | `bc75c73d04f6f57c7e3e07f6fb5fc8dac8b6b8c40ffb326354e64c4693e4d807` |

## 3. 五层控制面

| 层 | 字段/对象 | 回答的问题 | 失败后果 |
| --- | --- | --- | --- |
| sample admission | dataset source、split、success/failure、embodiment | 样本能否进入训练？ | label/domain 污染 |
| role routing | `rollout_data_mask`、world/value role flag | 这条样本承担 policy/world/value 哪个角色？ | 错 objective、错 condition |
| condition mask | clean input mask | 模型在该角色下可以看见哪些 slot？ | target leakage 或缺条件 |
| target + valid mask | role target、padding validity | 哪些误差真实有效并进入反向？ | 目标串线、terminal repeat 污染、empty loss |
| weight + reduction | sampling ratio、slot count、noise weight、multiplier、denominator | 每个 role 最终有多大优化影响？ | 某目标被淹没或主任务被压制 |

metric mask 独立于上述训练面：它只选择 action/future/value 的日志切片，不能反向证明 training mask 生效。

## 4. Frozen Cosmos routing 与 condition contract

LIBERO/RoboCasa index space 先按 demo、success rollout、failure rollout 组织。demo 的 `rollout_data_mask=0`；rollout 为 1。rollout 再分 world/value role；LIBERO 固定 \(p_{world}=0.5\)，RoboCasa 暴露 `p_world_model`，默认 0.5。基础 experiment config 的 `demonstration_sampling_prob=0.5`、`success_rollout_sampling_prob=0.5`，于是得到约 policy/world/value = 50/25/25，但这是指定 frozen recipe 的期望比例，不是每个 finite batch 或所有 checkpoint 的事实。[S1][S2]

role 到 condition 的 frozen 语义：

| Role | Clean condition | 主要生成/预测对象 |
| --- | --- | --- |
| policy demo | current state \(s\) | action，joint regime 还可含 future/value |
| world rollout | current state + action \((s,a)\) | future state；value 可作为 joint output |
| value rollout | 除 value frame 外的 prefix \((s,a,s')\) | value frame |
| state-value variant | future state \(s'\) | \(V(s')\) |
| Q variant | current state + action \((s,a)\) | \(Q(s,a)\) |

`condition_video_input_mask=1` 表示 clean condition，0 表示 denoise/predict。这个方向必须随字段名、shape、dtype、slot index 一起冻结；不能凭“1 通常表示有效 target”的习惯解释。[S2]

## 5. Target、valid 与 metric mask

### 5.1 Target mask

若 role-isolated target masking 打开，目标真值表应是：demo 只计 action slot，world sample 只计 future proprio/images，value sample 只计 value frame。Frozen code 的 `mask_loss_for_action_future_state_prediction` 实现了这一 optional branch，但默认 `False`，base experiment config 未覆写。[S2]

核心 invariant：

\[
m^{target}_{b,t}=1\Longrightarrow
\text{slot}(t)\in\mathcal T(r_b),
\]

\[
m^{target}_{b,t}=1\Longrightarrow
m^{condition}_{b,t}=0
\quad\text{for a role-isolated predicted target}.
\]

变量解释：\(r_b\) 是 sample role，\(\mathcal T(r_b)\) 是该 role 允许的 target slot 集；第二式阻止同一真正 target 同时作为 clean condition。它是 role-isolated 设计 invariant；frozen joint objective 在 target-mask branch 关闭时不是该 isolated regime，不能用这条式子反向否定它。

### 5.2 Valid/padding mask

推荐再有独立 \(q_{b,t}\) 表示该 target 是否来自真实时刻，而非 terminal clamp/repeated action：

\[
m^{effective}_{b,t}=m^{target}_{b,t}q_{b,t}.
\]

变量解释：\(q=0\) 应排除越过 episode 末端的 action/future target。Frozen LIBERO/RoboCasa dataset 会 clamp future index、重复最后 action，未提供独立 valid-step mask；因此 \(q\) 是推荐补强，不是上游已存在事实。[S2][S3]

### 5.3 Metric mask

component action/future/value L1/MSE 可按 role/slot 切片监控，但它们不等于 `kendall_loss` 的 exact target mask。必须分别记录 `training_target_mask_sha` 与 `metric_slice_version`，避免日志看似分开、反向仍联合。

## 6. Effective weight：不只是一个 lambda

先把每个 latent frame 的 EDM error 写成：

\[
e_{b,t}=\frac{1}{CHW}
\sum_{c,h,w}w(\sigma_{b,t})
\left(x_{0,bcthw}-\hat x_{0,bcthw}\right)^2.
\]

变量解释：\(w(\sigma)\) 是 noise-level weight，\(e_{b,t}\) 已对 channel/spatial 元素取平均；实现对应 `pred_mse * weights_per_sigma`。

一种 per-role normalized 设计可写为：

\[
\mathcal L_r=
\frac{\sum_{b,t}\mathbf 1[r_b=r]
m^{target}_{b,t}q_{b,t}e_{b,t}}
{\sum_{b,t}\mathbf 1[r_b=r]m^{target}_{b,t}q_{b,t}+\epsilon},
\qquad
\mathcal L=\sum_r\lambda_r\mathcal L_r.
\]

变量解释：该式让 \(\lambda_r\) 更接近显式 role weight，并对 active target 数归一化；它是审计/消融设计，不是 frozen Cosmos exact reduction。

Frozen code 的 exact 路径是：先把 frame mask/multiplier 乘到 EDM tensor，再对整个 tensor `mean()`。因此其优化影响近似同时依赖：

\[
\text{exposure}_r
\propto
p_r\times E[N_r^{active}]\times
\lambda_r\times E[w(\sigma)],
\]

变量解释：\(p_r\) 是 role 采样概率，\(N_r^{active}\) 是 active frame/element 数，\(\lambda_r\) 包括 action multiplier 等显式缩放。残差与参数 Jacobian 还会进一步决定 gradient share，所以最终要测 \(\lVert\lambda_r g_r\rVert\)，不能只看 exposure。

## 7. Frozen code 的三项关键边界

1. `mask_loss_for_action_future_state_prediction=False`：默认不启用 role-isolated action/future/value target mask。
2. `action_loss_multiplier=1` 且类型为 integer：默认不额外 upweight action；若改为非整数，代码会 cast 为 integer，resolved config 必须显式记录。
3. `mask_value_prediction_loss_for_policy_prediction` 会构造 `final_mask_B_T`，但 frozen apply-mask 条件没有包含该 flag。主 base config 未打开它，不能据此否定官方 checkpoint；个人配置若打开，必须用 non-zero loss/gradient test 验证，而不是信配置名。[S2]

## 8. 最小防污染断言与测试

1. **Role one-hot**：demo 不得同时是 rollout；rollout 的 world/value role 必须恰有一个为 1。
2. **Role×slot truth table**：打印每种 role 的 condition、target、valid、metric mask；核对 0/1 方向、shape、dtype 和 slot index。
3. **No-target-leak**：role-isolated regime 中，真正 target 不得同时 clean-conditioned；故意翻转一位应触发测试。
4. **Empty-target fail-fast**：每个 active role 的 valid target count > 0；不能把全零 mask 当作 loss=0 的好结果。
5. **Padding invariance**：改变 padded value 但保持 valid target 不变，loss/gradient 应不变；若变化说明 q/denominator 错。
6. **Mixture calibration**：采样至少一个统计 window，observed role/token/active-slot share 接近 resolved expectation，而非只读 config。
7. **Weight monotonicity**：单独改变 multiplier 时，目标 slot 的 pre-clip gradient/exposure 按预期变化，其他 slot 不应意外改变。
8. **Distributed parity**：单卡与 DDP/FSDP 在同 logical batch 上的 role count、loss numerator/denominator 和 gradient share 对齐。
9. **Matched outcome**：action-only、joint、isolated-mask、per-role-normalized、weight/ratio sweep 固定数据/算力/协议，最后比较闭环。

## 9. 可审计伪代码

```python
def build_multirole_loss(batch, model, resolved_contract):
    # 1. Route every sample to exactly one semantic training role.
    role = validate_one_hot_role(batch.role_flags)

    # 2. Build independent masks; never reuse condition as target/metric validity.
    condition_mask = build_condition_mask(role, batch.slot_indices)
    target_mask = build_target_mask(role, batch.slot_indices)
    valid_mask = build_valid_mask(batch.episode_length, batch.target_timestep)
    assert_no_target_leak(role, condition_mask, target_mask)

    # 3. Compute the exact noise-weighted tensor before any diagnostic slicing.
    edm_tensor = model.exact_edm_error(batch, condition_mask)
    effective_mask = target_mask * valid_mask
    assert_valid_target_count(effective_mask, role)

    # 4. Normalize and weight according to the resolved experiment contract.
    per_role_loss = reduce_per_role(edm_tensor, effective_mask, role)
    total_loss = sum(resolved_contract.loss_weight[r] * per_role_loss[r] for r in role.types)

    # 5. Log observed role/slot/denominator and gradient share, not config alone.
    audit_role_exposure_and_gradient(total_loss, per_role_loss, role, effective_mask)
    return total_loss
```

这段伪代码是推荐的防污染合同，不是 frozen Cosmos 或用户 WAM 已存在实现。复现 exact frozen behavior 时，应保留其 full-tensor mean 与 optional flags，再以独立 arm 比较改造。

## 10. WAM 真实性边界

当前 inventory 只能支持“上游 routing/slot/mask/loss contract 已核，并设计了审计清单”。CoffeePressButton 单 episode trace 不包含训练 role histogram、resolved flags、mask tensor、denominator 或 gradient；它不能证明训练污染、修复或收益。[S5]

安全说法：**“我会把 sample role、condition、target、valid、metric mask 和 reduction 分开审计，并用 observed exposure/gradient share 与 matched closed-loop 验证。”**

不能说：**“我已调好 50/25/25 和 loss weight，消除了 WAM 多目标污染。”**

## 11. 下一入口

下一 bounded slice 是 `VLA-WM-029`：value 在 imagined/OOD state 上为何失准，以及 calibration/pessimism 如何限制 planning 风险。WM-029 应复用本页的 value role/label/valid contract，不再重复 mask 实现。

## 参考文献（References）

1. Kim et al., [Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning](https://arxiv.org/abs/2601.16163v1), 2026。
2. NVlabs, [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)。重点：[dataset routing](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/datasets/libero_dataset.py)、[condition mask](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/models/policy_video2world_model.py)、[target mask / reduction](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/models/policy_text2world_model.py)。
3. [WM-025 Slot / Mask / Loss Source Freeze](vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。
4. [WM-027 Negative Transfer / Gradient Conflict](vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html)。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。

