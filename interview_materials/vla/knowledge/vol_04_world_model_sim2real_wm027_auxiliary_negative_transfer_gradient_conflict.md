# VOL 04 World Model / Sim2Real：Auxiliary Negative Transfer 与 Gradient Conflict（WM-027）

> 状态：drafted / VLA-WM-027 / knowledge_29_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：区分负迁移结果、局部 gradient conflict 与处置手段；不把诊断方法写成本地已执行结论。  
> 前置：[WM-026 为什么 auxiliary 可能帮助](vol_04_world_model_sim2real_wm026_world_value_auxiliary_action_imitation.html)、[WM-027 Source Freeze](../sources/vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html)。

## 问题（Question）

什么时候 auxiliary world/value 会负迁移，如何识别 gradient conflict？回答必须给出可证伪定义、逐层/逐角色统计、PCGrad/GradNorm 的区别、contract-first 排查和 matched closed-loop 验证。

## 1. 面试结论

auxiliary 会在目标语义错、routing/mask/padding 错、role/domain 失衡、gradient 尺度压制、方向冲突或 shared capacity 不足时伤害 action。负迁移的定义不是“看见负 cosine”，而是同数据、同算力、同协议下，auxiliary arm 相对 action-only 的 action/闭环主指标稳定变差。

gradient cosine 是某个模型状态、batch、layer 和参数子集的一阶信号。先修数据合同；仍有稳定方向冲突可试 PCGrad，尺度与训练速率失衡可试 GradNorm。最终必须回到跨 seed 的 paired closed-loop evidence。

## 2. 三层证据不要混淆

| 层 | 问题 | 证据 | 不能推出 |
| --- | --- | --- | --- |
| optimization geometry | 当前 step 的 task gradients 是否冲突/失衡？ | cosine、dot、norm ratio、conflict rate | 泛化或 success 必然下降 |
| training outcome | auxiliary 是否让 action 学习更差？ | matched action metric、learning curve、checkpoint | controller 闭环一定更差 |
| system outcome | 固定 protocol 下是否负迁移？ | per-task success、paired episode、seed/CI、first-failure | 根因一定是 gradient |

## 3. Gradient conflict 的数学诊断

对 shared parameters \(\theta_s\)：

\[
g_a=\nabla_{\theta_s}\mathcal L_a,
\qquad
g_u=\nabla_{\theta_s}\mathcal L_u,
\]

\[
c_{a,u}=
\frac{g_a^\top g_u}
{\lVert g_a\rVert_2\lVert g_u\rVert_2+\epsilon}.
\]

变量解释：\(g_a\) 是 action gradient，\(g_u\) 是 world/value gradient；\(c<0\) 表示 PCGrad 定义的局部 conflict。[1] 实现映射到 exact training loss 的 `autograd.grad`，不能拿日志 component L1/MSE 冒充主反向梯度；zero/empty target 的 cosine 记 `NA`。

联合更新为：

\[
g_{\mathrm{joint}}=g_a+\lambda_w g_w+\lambda_v g_v,
\qquad
\Delta\mathcal L_a\approx-\eta g_a^\top g_{\mathrm{joint}}.
\]

变量解释：若 \(g_a^\top g_{\mathrm{joint}}<0\)，该步在一阶近似下会增加 action loss；但 stochastic gradient、曲率和后续训练使它仍只是诊断，不是负迁移证明。

必须逐层记录：

\[
c_{ij}^{(\ell)},
\qquad
\rho_{u/a}^{(\ell)}=
\frac{\lVert\lambda_u g_u^{(\ell)}\rVert}
{\lVert g_a^{(\ell)}\rVert+\epsilon}.
\]

变量解释：\(c\) 看方向，\(\rho\) 看 auxiliary 是否在尺度上淹没 action。至少分 shared trunk、slot/modality projection 和 task head；全模型平均可能掩盖某几层长期反向。

## 4. 如何采集可信 gradient trace

1. 同一 model state 分别计算 action/world/value 的 exact loss；记录 role、target mask、valid count 和 denominator。
2. AMP 下先 unscale 再求 norm/cosine；同时保存 pre-clip 与 post-clip，避免把 scale/clip 伪影当冲突。
3. DDP 下先得到全局一致的 per-role gradient；FSDP/sharded 情况聚合 exact dot/norm sufficient statistics，不平均各 rank cosine。
4. 同时报 pairwise cosine、joint-update alignment、norm ratio、conflict rate、分位数和连续冲突时长。
5. 既做 matched-state probe，也看真实 routed schedule；否则不同 role 的 domain shift 会被误叫成 objective conflict。

## 5. 负迁移根因树

| 根因 | 典型表现 | 最小实验 |
| --- | --- | --- |
| world target shortcut | future 好看、action swap 不敏感 | action swap + foreground/contact probe |
| value label/OOD | loss 低，rank/calibration 差 | reliability/rank + failure-label audit |
| routing/mask/empty target | 某 role zero/huge gradient | role matrix + non-zero grad + fail-fast |
| terminal padding/normalizer | 尾部或某 action dim 异常 | valid-step mask、round-trip、per-offset/per-dim |
| role/domain imbalance | rollout 目标压过 demo | same-count/same-compute + per-source holdout |
| scale domination | \(\rho_{u/a}\gg1\) | weight sweep / GradNorm A/B |
| direction conflict | conflict rate 高且 joint update 伤 action | PCGrad / asymmetric projection A/B |
| capacity competition | auxiliary 好，action representation 差 | stop-gradient、head-only、freeze/width control |

## 6. PCGrad 与 GradNorm 不解决同一问题

### 6.1 PCGrad：去掉负方向分量

若 \(g_i^{\mathrm{PC}\top}g_j<0\)：

\[
g_i^{\mathrm{PC}}
\leftarrow g_i^{\mathrm{PC}}
-\frac{g_i^{\mathrm{PC}\top}g_j}{\lVert g_j\rVert_2^2}g_j.
\]

变量解释：投影后当前 pair 的内积归零，非冲突梯度不变；多任务按随机顺序处理并汇总。[1][2] 它适合“方向冲突稳定、contract 已正确”的情况，但需要 per-task gradients，增加显存/通信，且不修错误标签、域差异或容量竞争。

### 6.2 GradNorm：动态平衡 gradient magnitude

\[
G_W^{(i)}(t)=\lVert\nabla_W w_i(t)L_i(t)\rVert_2,
\quad
r_i(t)=
\frac{L_i(t)/L_i(0)}{E_j[L_j(t)/L_j(0)]},
\]

\[
G_i^*(t)=\overline G_W(t)[r_i(t)]^\alpha,
\quad
\mathcal L_{\mathrm{grad}}=
\sum_i|G_W^{(i)}-G_i^*|_1.
\]

变量解释：\(r_i>1\) 表示 task 相对学得慢，\(\alpha\) 控制 rate balancing；更新 loss weight 后归一化 \(\sum_iw_i=T\)。[3] 它处理尺度/速率，不看 gradient sign；噪声大或不可学的 auxiliary 也可能被上调，所以先做 label/learnability audit。

### 6.3 选择表

| 现象 | 首选动作 | 理由 |
| --- | --- | --- |
| label/mask/domain 错 | 修数据与 routing | 优化器不能修目标语义 |
| norm 差异大、方向多为正 | weight schedule / GradNorm | 主要是尺度与速率 |
| 负 cosine 持续、joint update 伤 action | PCGrad A/B | 直接处理方向分量 |
| action 是唯一主 KPI | stop-gradient / 分层共享 / 非对称保护 | 避免对称方法牺牲主任务，需单独验证 |
| auxiliary proxy 好、闭环差 | matched closed-loop + failure trace | 先确认是否 metric mismatch |

## 7. 可审计伪代码

```python
def diagnose_auxiliary_step(model, role_batches, scaler, distributed):
    # 1. Use exact role-conditioned training losses, masks and denominators.
    shared_groups = select_shared_parameter_groups(model)
    role_grads = {}
    for role, batch in role_batches.items():
        loss, valid_count = exact_training_loss(model, batch, role)
        if valid_count == 0:
            role_grads[role] = None  # Empty target is NA, not zero cosine.
            continue
        grads = autograd_grad(loss, shared_groups)
        role_grads[role] = scaler.unscale_copy(grads)

    # 2. Synchronize per-role gradients or exact sharded dot/norm statistics.
    role_grads = distributed.sync_role_grads(role_grads)

    # 3. Log layer-wise direction, magnitude and joint-update interference.
    stats = pairwise_cosine_norm_ratio(role_grads)
    stats.update(joint_alignment(role_grads, loss_weights=model.loss_weights))
    return stats
```

这段是 instrumentation 设计，不是 WAM 已存在代码。真实训练还要把采样 cadence、gradient accumulation、clip、optimizer step 和 checkpoint outcome 绑定到同一 `run_id/step_id`。

## 8. Matched 确认协议

至少比较 action-only、+world、+value、all，并按根因增加 PCGrad、GradNorm、stop-gradient 或 routing/weight arm。固定：

- base checkpoint、data identity/split、effective sample/token、updates 与 compute；
- optimizer/LR/AMP/DDP、normalizer、slot/mask/padding 和 seed 计划；
- checkpoint selection；task/init/controller/chunk/horizon/success predicate；
- 每个 task 的 trials、paired episode key、失败分层和统计不确定性。

判断顺序：先确认 auxiliary arm 是否相对 action-only 负迁移，再看 gradient 指标能否解释退化，最后看 mitigation 是否同时修复 gradient 与主任务。只修好 cosine 而 action/closed-loop 不变，不能叫问题解决。

## 9. Cosmos/WAM 与个人项目边界

Cosmos/WAM 的 exact main loss 是 unified noise-weighted latent EDM objective，component action/future/value L1/MSE 主要是诊断 metric。[4] 要测 per-role gradient，需从 exact role/mask loss 重算，不能对日志 metric 反向后冒充官方目标。

当前 WAM inventory 仍没有可加载 local checkpoint、per-role gradient trace、matched objective arms、跨 seed episode 和 ownership。CoffeePressButton 的单 episode action trace 与单样本 future proxy 不能确认 negative transfer。安全说“我能设计并解释诊断协议”，不能说“已经用 PCGrad/GradNorm 修复 WAM”。[5]

## 10. 结论与下一入口

负迁移由 matched 主任务结果定义；gradient conflict 只是局部原因候选。排查顺序应是 contract → routing/weight/shared capacity → PCGrad/GradNorm → paired closed-loop。PCGrad 管方向，GradNorm 管尺度/训练速率，两者都不能替代正确目标与证据。

下一节点 `VLA-WM-028` 将进入更靠前的数据合同层：sample routing、slot mask 与 loss weight 如何避免三类目标互相污染。题卡保持 unseen；真实口述前不创建 coaching state。

## 参考文献（References）

1. Yu et al., [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782v4), ICLR 2020。
2. Yu et al., [`PCGrad@c5fbd7c`](https://github.com/tianheyu927/PCGrad/tree/c5fbd7c856526373828074f06875230f7f3ee79e)。
3. Chen et al., [GradNorm](https://arxiv.org/abs/1711.02257v4), ICML 2018。
4. [WM-025 Cosmos/WAM Slot / Mask / Loss](vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [WM-027 Source Freeze](../sources/vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html)。

