# VOL 04 World Model / Sim2Real：Routing、Slot Mask 与 Loss Weight 防污染（WM-028）

> 状态：drafted / VLA-WM-028 / knowledge_30_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释多目标数据/反向控制面与 effective weight，不宣称推荐改造已在本地 WAM 执行。  
> 前置：[WM-025 Slot / Mask / Loss](vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)、[WM-027 Negative Transfer](vol_04_world_model_sim2real_wm027_auxiliary_negative_transfer_gradient_conflict.html)、[WM-028 Source Freeze](../sources/vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html)。

## 问题（Question）

sample routing、slot mask 与 loss weight 怎样避免 action/world/value 互相污染？回答必须区分 role、condition、target、valid、metric、reduction 和 effective gradient share。

## 1. 面试结论

防污染不是“把三个 loss weight 调小一点”，而是五道门：先决定样本能否进入，再把它路由到唯一 role；condition mask 决定模型看见什么，target/valid mask 决定哪些真实误差反向，最后才用采样比例、slot 数、noise weight、multiplier 和 denominator 控制影响大小。metric mask 只管日志。

任何上游错误都不能靠下游权重补救：错 role 会训练错目标，condition 错会 target leakage，target/valid 错会把其他 slot 或 padding 反向，reduction 错会让 slot 数变成隐式权重。最终要看 observed role/active-slot/gradient share 和 matched closed-loop，不只看 config。

## 2. 五层控制面

| 控制面 | 核心对象 | 必答问题 | 常见污染 |
| --- | --- | --- | --- |
| admission | source/split/success/embodiment | 样本该不该进入？ | label/domain 错 |
| routing | policy/world/value role | 样本训练哪个条件分布？ | 同时进多个 role 或错 role |
| conditioning | clean input mask | 模型允许看哪些 slot？ | target leakage、缺 action condition |
| target validity | target + valid mask | 哪些预测误差真实有效？ | 串线、empty target、terminal repeat |
| weighting | ratio/slot/noise/multiplier/reduction | 各 role 影响有多大？ | 主任务被淹没、比例与 config 不符 |

metric mask 独立：它用于日志切片，不能替代 training target mask。

## 3. Role 与 mask 真值表

| Role | Clean condition | Role-isolated target | 高危错误 |
| --- | --- | --- | --- |
| policy demo | current state \(s\) | action | action 同时作为 clean input；future/value 意外反向 |
| world rollout | current state + action \((s,a)\) | future proprio/images | action 没有 condition；value/当前帧混入 target |
| value rollout | prefix \((s,a,s')\) | value | value target 被 condition；return/timeout 语义错 |
| \(V(s')\) variant | future state | value | current/action 泄漏 |
| \(Q(s,a)\) variant | current state + action | value | future state 泄漏 |

对 role-isolated regime：

\[
m^{target}_{b,t}=1\Rightarrow
\operatorname{slot}(t)\in\mathcal T(r_b),
\qquad
m^{target}_{b,t}m^{condition}_{b,t}=0.
\]

变量解释：\(r_b\) 是样本角色，\(\mathcal T(r_b)\) 是该 role 的合法 target slot；第二项阻止 target 同时作为 clean condition。Frozen Cosmos base joint regime 默认不打开 role-isolated target mask，因此这条 invariant 用于 isolated arm/审计，不能拿来否定 joint objective。

## 4. Valid mask 解决 terminal/padding 污染

令 \(q_{b,t}=1\) 表示 target 对应真实 episode step，0 表示 clamp/repeat padding：

\[
m^{effective}_{b,t}=m^{target}_{b,t}q_{b,t}.
\]

变量解释：只有 role 合法且真实有效的 slot 才进入反向。Frozen LIBERO/RoboCasa 会把 future index clamp 到末帧、action 不足时重复最后动作，没有独立 valid-step mask；所以 \(q\) 是推荐补强，不是上游现状。[1]

一个强单测是 padding invariance：只改变 \(q=0\) 区域的值，loss 与 gradient 应保持不变；否则 target mask、valid mask 或 denominator 至少有一个错误。

## 5. Effective weight 的构成

每个 frame 的 noise-weighted error：

\[
e_{b,t}=\frac{1}{CHW}
\sum_{c,h,w}w(\sigma_{b,t})
\left(x_{0,bcthw}-\hat x_{0,bcthw}\right)^2.
\]

变量解释：\(w(\sigma)\) 是 EDM noise weight；实现映射到 `pred_mse * weights_per_sigma`，还未应用 role/target mask。

若按 active target 做 per-role normalization：

\[
\mathcal L_r=
\frac{\sum_{b,t}\mathbf1[r_b=r]m^{effective}_{b,t}e_{b,t}}
{\sum_{b,t}\mathbf1[r_b=r]m^{effective}_{b,t}+\epsilon},
\qquad
\mathcal L=\sum_r\lambda_r\mathcal L_r.
\]

变量解释：\(\lambda_r\) 是显式 role weight。该式便于控制比较，但不是 frozen Cosmos exact loss。

实际影响还包括：

\[
\operatorname{exposure}_r
\propto p_r\,E[N_r^{active}]\,\lambda_r\,E[w(\sigma)],
\qquad
\operatorname{gradshare}_r=
\frac{\lVert\lambda_r g_r\rVert}
{\sum_j\lVert\lambda_j g_j\rVert+\epsilon}.
\]

变量解释：\(p_r\) 是采样概率，\(N_r^{active}\) 是 active target 数。exposure 是数据/目标质量，gradshare 才更接近优化影响；两者都比“配置写了 0.25/1.0”更可信。

## 6. Frozen Cosmos 的关键实现边界

### 6.1 Routing

基础 LIBERO/RoboCasa config 以 0.5 概率采 demo，rollout 再以 0.5 分 world/value，得到约 50/25/25 的期望 role mix。有限 batch 会波动，其他 recipe 也可能不同；必须记录 observed counts。[1]

### 6.2 Condition mask

world sample 把 action frame 设为 clean condition；value sample 把除 value frame外的 prefix 设为 clean。这里 mask=1 是 condition，不是 target。[1]

### 6.3 Target mask、multiplier 与 denominator

Frozen config class defaults：

- `mask_loss_for_action_future_state_prediction=False`；
- `mask_value_prediction_loss_for_policy_prediction=False`；
- `action_loss_multiplier=1`，且实现 cast 为 integer。

base experiment config 没有覆写。target mask 若开启，会乘到 EDM tensor；训练入口随后对完整 \(BCTHW\) mean，所以 active slot 少的 role 被隐式降权，而不是按 active count 重新归一化。[1]

另有 WARN：`mask_value_prediction_loss_for_policy_prediction` 构造了 mask，但 apply-mask 条件没有包含该 flag。base config 未启用它；个人配置若启用，必须验证 non-zero loss/gradient，不能相信变量名。[1]

## 7. 为什么 loss weight 不能修上游错误

| 错误 | 只调 weight 会怎样 | 正确动作 |
| --- | --- | --- |
| role 错 | 更小地训练错误目标 | 修 source/role label |
| condition 泄漏 | 更小地学习 shortcut | 修 condition truth table |
| target 串线 | 仍会更新错误 slot | 修 target mask |
| padding 有效性错 | 仍会拟合 terminal repeat | 加 valid mask/重构 target |
| denominator 错 | weight 与 active count耦合 | 固定 reduction contract |
| domain imbalance | weight 无法改变状态覆盖 | 改 sampling/source balance |

只有 role、condition、target、valid 全正确后，loss weight 才有“平衡合法梯度”的语义；否则它只是掩盖 bug。

## 8. 最小测试矩阵

1. role one-hot：每条样本恰有一个 semantic role。
2. role×slot truth table：打印 condition/target/valid/metric 四张 mask。
3. no-target-leak：故意把 target 设 clean，测试必须失败。
4. empty-target fail-fast：active role 的 valid target count 不能为 0。
5. padding invariance：无效 padding 改值不改变 loss/gradient。
6. mixture calibration：observed role/token/active-slot share 对齐 expectation。
7. multiplier monotonicity：只改变 action weight，只改变预期 slot 的 pre-clip gradient。
8. distributed parity：单卡/多卡 numerator、denominator、role count 对齐。
9. matched ablation：joint、isolated mask、valid mask、per-role normalization、ratio/weight sweep 都固定数据/算力/协议。

## 9. 可审计伪代码

```python
def audited_multirole_step(batch, model, contract):
    # 1. Route each sample to exactly one semantic role.
    role = assert_one_hot_role(batch.role_flags)

    # 2. Keep information-access and gradient-selection masks independent.
    cond = build_condition_mask(role, batch.slot_index)
    target = build_target_mask(role, batch.slot_index)
    valid = build_valid_mask(batch.episode_length, batch.target_step)
    assert_no_target_leak(cond, target, role)

    # 3. Compute the exact training tensor, then select only valid targets.
    edm = model.exact_edm_error(batch, condition_mask=cond)
    active = target * valid
    assert_nonempty_by_role(active, role)

    # 4. Apply a versioned reduction/weight contract and log observed shares.
    losses = reduce_by_role(edm, active, role, contract.denominator)
    total = sum(contract.weight[r] * losses[r] for r in role.types)
    log_exposure_gradient_and_denominator(total, losses, role, active)
    return total
```

它是推荐 instrumentation，不是本地 WAM 已存在实现。若复现 frozen Cosmos，先保持 full-tensor mean/default flags，再用独立 arm 做因果比较。

## 10. Matched 评估与判读

| Arm | 改动 | 回答的问题 |
| --- | --- | --- |
| A | frozen joint/default | 基线合同 |
| B | role-isolated target mask | 是否存在 target 串线/共享收益 trade-off |
| C | B + valid mask | terminal repeat 是否污染 |
| D | C + per-role normalization | active slot 数隐式权重是否关键 |
| E | D + ratio/weight sweep | 合法梯度的平衡点 |

固定 base checkpoint、data identity、updates/compute、noise schedule、normalizer、seed、checkpoint rule 和 closed-loop protocol。若只改善 component loss 或 gradient share，不能说闭环污染已解决；必须报告 action proxy、future/value、per-task success、paired episode 和 first-failure。

## 11. WAM 项目真实性

当前 WAM 没有 resolved training config、role histogram、mask dump、loss numerator/denominator、gradient share、paired checkpoint/episode 和 ownership。本页只能支持方法回答与补证据设计。

安全说法：“我把 routing、condition、target、valid、metric 与 reduction 分层，并会用 observed share 和 matched arms 验证。”不能说“我已调好 50/25/25 或证明 mask/weight 提升成功率”。

## 12. 结论与下一入口

防污染顺序是 admission→routing→condition→target/valid→weight/reduction→gradient/outcome。权重是最后一道控制，不是修 bug 的万能旋钮。Frozen Cosmos 的默认 joint regime、optional mask branch 和 full-tensor mean 必须分开描述。

下一节点 `VLA-WM-029` 将处理 imagined/OOD value 的 calibration 与 pessimism。题卡保持 unseen；真实口述前不创建 coaching state。

## 参考文献（References）

1. [WM-028 Source Freeze](../sources/vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html)。
2. [WM-025 Slot / Mask / Loss](vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)。
3. [WM-027 Negative Transfer / Gradient Conflict](vol_04_world_model_sim2real_wm027_auxiliary_negative_transfer_gradient_conflict.html)。
4. [Cosmos Policy / WAM Claim-to-Code](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。

