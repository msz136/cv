# VOL 04 World Model / Sim2Real：World/Value Auxiliary 为什么可能帮助 Action Imitation（WM-026）

> 状态：drafted / VLA-WM-026 / knowledge_28_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释条件性机制与因果验证，不宣称 auxiliary 必然有效或已在本地 WAM 产生收益。  
> 前置：[WM-025 Cosmos/WAM Slot / Mask / Loss](vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)、[WM-026 Source Freeze](../sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html)。

## 问题（Question）

world/value auxiliary objective 为什么可能帮助 action imitation？回答必须同时说明表示机制、value 语义、数据覆盖、梯度相容性、负迁移和 matched ablation。

## 1. 面试结论

world auxiliary 可能迫使共享表示理解“动作之后什么会变”，从而保留可控物体、接触状态和任务阶段，而不是只拟合动作均值或 repeat baseline。value auxiliary 可能提供“当前状态/动作是否把任务推向成功”的 task-progress 信号。二者还可能通过更多 rollout 状态和额外监督起 regularization 作用。

但关键词是“可能”：如果 future 只学背景/像素细节、value label 噪声或 OOD、routing/mask 错、gradient 与 action 冲突、auxiliary 比例过大或 capacity 不足，就会无迁移甚至负迁移。只有 matched ablation 和闭环 evidence 才能升级结论。

## 2. 三种帮助机制

### 2.1 Action consequence representation

纯 imitation：

\[
\mathcal L_a=\ell_a(f_a(h_\theta(s_t)),a_t^\*).
\]

加入 world target：

\[
\mathcal L_w=\ell_w(
f_w(h_\theta(s_t),a_{t:t+K-1}),s'_{t+K}).
\]

变量解释：\(h_\theta\) 是共享表示，\(a_t^\*\) 是专家动作，\(s'_{t+K}\) 是 future observation proxy。若 \(\mathcal L_w\) 真正依赖 action consequence，shared feature 可能保留对象、接触与阶段；若 action swap 后 future 不变，world loss 再低也不能证明帮助 action。

### 2.2 Task-progress/value signal

\[
\mathcal L_v=\ell_v(
f_v(h_\theta(s_t),a_t,s'_{t+K}),G_{t+K}).
\]

变量解释：\(G_{t+K}\) 是指定 reward/termination contract 的 return。它可能区分视觉相近但成功可达性不同的状态；若 return scale、failure label、timeout 或 calibration 错，也会形成 shortcut。

### 2.3 Data coverage 与 regularization

demo 主要覆盖 expert-like states；success/failure rollout 能增加偏离、恢复和失败状态。共享 backbone 若从这些辅助角色学习有效因果/进展特征，可能提升 action robustness；若 rollout domain 与 demo policy 不匹配，则会污染 representation。

## 3. 梯度相容性

对 shared parameters：

\[
g_a=\nabla_\theta\mathcal L_a,\qquad
g_{\mathrm{aux}}=\lambda_w\nabla_\theta\mathcal L_w+
\lambda_v\nabla_\theta\mathcal L_v,
\]

\[
\cos(g_a,g_{\mathrm{aux}})=
\frac{g_a^\top g_{\mathrm{aux}}}
\lVert g_a\rVert_2\lVert g_{\mathrm{aux}}\rVert_2+\epsilon}.
\]

变量解释：cosine 为正说明当前 batch 的局部方向更相容，为负提示冲突；还要记录 layer-wise norm、role frequency、loss scale、mask denominator 和 distributed reduction。它是 debug signal，不是闭环收益证明。

## 4. Cosmos/WAM 的实现边界

Cosmos/WAM 使用统一 latent sequence、sample routing、condition mask 和可选 target mask，而不是简单三个 scalar loss head。[1][2] 因此上面的 \(\mathcal L_a+\lambda_w\mathcal L_w+\lambda_v\mathcal L_v\) 是机制审计抽象；exact frozen main loss 仍是 noise-weighted latent EDM MSE，component action/future/value L1/MSE 只是诊断 metric。

要证明 auxiliary 真正更新 action-relevant shared feature，必须保存：

- demo/world/value role 的 effective sample/update 数；
- action/future/value target slot 与 non-zero gradient；
- shared trunk 和 slot-specific layer 的 gradient norm/cosine；
- normalizer、padding、mask、denominator 和 checkpoint revision。

## 5. Matched ablation

| Arm | 目标 | 核心问题 |
| --- | --- | --- |
| A | action-only | action baseline |
| B | action + world | world target 是否带来 transfer |
| C | action + value | value signal 是否带来 transfer |
| D | action + world + value | 组合是否超过单目标 |
| E | shuffled auxiliary label | 排除额外 compute/regularization |
| F | auxiliary stop-gradient / frozen trunk | 区分 head fitting 与 shared representation 更新 |

需要固定：

1. base checkpoint、dataset split、demo/rollout identity；
2. total updates、token/sample 数、optimizer、LR schedule、batch 和 compute；
3. slot、mask、normalizer、action schema、seed；
4. eval task/init/controller/chunk/horizon/success predicate 和 denominator；
5. checkpoint selection rule。

如果 B/C/D 使用更多数据或 compute，应增加同资源 action-only control。

## 6. 指标阶梯

| 层 | 指标 | 结论边界 |
| --- | --- | --- |
| optimization | main loss、gradient norm/cosine | 只证明目标进入反向/冲突 |
| action proxy | action MAE/MSE、repeat baseline、per-dim/per-step | 只证明 frozen split imitation |
| actionability | action swap/sensitivity、counterfactual future | 检查 world 是否用 action |
| auxiliary | per-offset future error、value calibration/rank | 检查 auxiliary 自身质量 |
| closed loop | task success、first failure、recovery、episode trace | 固定 protocol 下系统结果 |

典型判读：

- auxiliary proxy 好、action/closed-loop 不变：只学会 auxiliary task。
- action MSE 好、closed-loop 不变：检查 contact、normalizer、recovery 和 metric mismatch。
- D 优于 B/C：还不能直接说 synergy，需 interaction/gradient evidence。
- future 不好但 B 优于 A：可能是 regularization/资源差异，不足以说 dynamics 表示成功。

## 7. 可审计伪代码

```python
def matched_auxiliary_ablation(base_state, data, protocol):
    # 1. Keep initialization, samples, updates, compute and evaluation fixed.
    arms = {
        "action": {"world": 0.0, "value": 0.0},
        "action_world": {"world": 1.0, "value": 0.0},
        "action_value": {"world": 0.0, "value": 1.0},
        "all": {"world": 1.0, "value": 1.0},
    }
    results = {}
    for name, weights in arms.items():
        model = restore_exact(base_state)
        # 2. Log role counts, masks, shared gradients and all metric layers.
        train(model, data, weights, protocol)
        results[name] = evaluate_same_protocol(model, protocol)
    # 3. Attribute gain only after paired proxy and closed-loop comparison.
    return paired_compare(results)
```

实际运行还要加入 shuffled-label 和 stop-gradient controls，并保存每个 arm 的 manifest、checkpoint、metric、episode 和 ownership。

## 8. 负迁移与诊断

| 风险 | 症状 | 检查 |
| --- | --- | --- |
| visual shortcut | future 清晰但 action sensitivity 低 | action swap、foreground/contact probe |
| value noise/OOD | value loss 低但 rank/calibration 差 | reliability、failure rollout audit |
| gradient conflict | auxiliary 降、action 梯度/指标差 | layer-wise cosine/norm、weight sweep |
| role imbalance | action update 被稀释 | effective role/token/update count |
| capacity competition | world pixel detail占满 trunk | width/freeze/head-only control |
| terminal padding | 尾部 loss 异常 | valid-step mask A/B |
| domain mismatch | rollout auxiliary 伤害 demo | per-source holdout |

## 9. WAM 项目真实性

WAM inventory 只证明上游机制已核和项目提出过 ablation 计划；exact local config、可加载 checkpoint、raw metric、gradient trace、paired episode 和 ownership 仍缺。历史 45% MSE、任务成功率、0-success 与 root cause 不能作为 WM-026 的已验证结论。

安全说法是：“我能解释辅助目标的表示假设，并设计 matched objective、gradient alignment、action sensitivity、value calibration 与 closed-loop 验证。”不能说“world/value 已经提升了我的策略”。

## 10. 结论

world/value auxiliary 可能通过 action consequence、task progress 和更广状态覆盖帮助 imitation；是否真的帮助取决于 label、routing/mask、gradient、capacity 和 protocol。最终证据必须来自 matched ablation，而不是 component loss 或上游论文结论。

本节点保持 WARN，题卡保持 unseen；真实口述前不创建 coaching state。

参考：[WM-026 Source Freeze](../sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html)、[Cosmos/WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)、[WM-025](vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)、[WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[WM-019](vol_04_world_model_sim2real_wm019.html)。
