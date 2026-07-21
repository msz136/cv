# VOL 04 World Model / Sim2Real：Objective Semantics（WM-011）

> 状态：drafted / VLA-WM-011 / knowledge_41_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么？  
> 前置：[World-model Foundations](vol_04_world_model_sim2real.html)、[WM-011 Source Freeze](../sources/vol_04_wm011_objective_semantics_source_freeze.html)。

## 1. 面试结论

回答这题不要背 loss 名称，而要逐项说清：`prediction、target、时间索引、mask、reduction、scale、gradient path`。

| objective | 监督对象 | 主要用途 | 不能证明 |
| --- | --- | --- | --- |
| reconstruction | latent → observation | 保留可解码视觉/proprio 信息 | prior rollout、actionability |
| latent dynamics | action/history prior ↔ observation posterior | 学会无未来观测的 latent prediction | 长 horizon 稳定、closed-loop success |
| reward | latent → 一步即时 reward | imagined outcome 的局部任务信号 | value 或 task success |
| continuation | latent → continue/discount | return bootstrap 与终止建模 | success predicate |
| perceptual | predicted/target observation 的 feature distance | 强调感知结构而非逐像素一致 | 接触/几何/控制正确 |

## 2. 总目标

\[
\mathcal L_{\mathrm{wm}}
=\lambda_{\mathrm{rec}}\mathcal L_{\mathrm{rec}}
+\lambda_{\mathrm{dyn}}\mathcal L_{\mathrm{dyn}}
+\lambda_{\mathrm{rep}}\mathcal L_{\mathrm{rep}}
+\lambda_r\mathcal L_r
+\lambda_c\mathcal L_c
+\lambda_p\mathcal L_{\mathrm{perc}}.
\]

变量解释：\(\mathcal L_k\) 是不同监督，\(\lambda_k\) 是聚合权重。直觉是分别约束“看得见、推得动、知道即时回报、知道是否继续、符合感知结构”。实现映射：每项记录 numerator、valid denominator、reduced/scaled loss 和梯度范数；总 loss 单值不足以诊断。

## 3. Reconstruction：重建 observation

\[
\mathcal L_{\mathrm{rec}}^{(k)}
=-\frac{1}{N_k}\sum_{t,i}m_{t,i}^{(k)}
\log p_\theta(o_{t,i}^{(k)}\mid h_t,z_t).
\]

变量解释：\(k\) 是 camera/proprio key，\(m\) 是有效 mask，\(N_k\) 是有效元素数。直觉是让 latent 能恢复 observation。实现映射：必须固定 camera key、resize/crop、dtype/range、MSE/NLL、padding/missing mask 与 per-key reduction。[1][2]

DreamerV3 frozen reimplementation 对 image target `/255`，每个 decoder key 单独计算 reconstruction loss，再把 `rec` scale 映射到各 key。[1]

**边界：**posterior 可以读取当前 observation，因而重建很好却不代表 prior 能 rollout；pixel loss 也可能被背景/低频纹理主导。

## 4. Latent dynamics：让 prior 学会预测 posterior

\[
q_\phi(z_t\mid h_t,o_t),\qquad
p_\theta(z_t\mid h_t),\qquad
h_t=f_\theta(h_{t-1},z_{t-1},a_{t-1}).
\]

变量解释：posterior \(q\) 读取当前 observation，prior \(p\) 只读历史/action；\(h_t\) 是 deterministic memory。直觉是 posterior 校正 belief，prior 才能在 imagination 阶段预测未来。实现映射：分别对应 `RSSM.observe` 与 `RSSM.imagine`。[1][2]

## 5. Dynamics / representation KL

\[
\mathcal L_{\mathrm{dyn}}
=D_{\mathrm{KL}}[\operatorname{sg}(q_\phi)\|p_\theta],
\qquad
\mathcal L_{\mathrm{rep}}
=D_{\mathrm{KL}}[q_\phi\|\operatorname{sg}(p_\theta)].
\]

变量解释：`sg` 是 stop-gradient。dyn 主要更新 prior，rep 主要约束 posterior。直觉是相同分布对齐因梯度接收者不同而承担不同职责。实现映射：DreamerV3 frozen repo 分别记录 `dyn/rep`，默认 `free_nats=1.0` 后截断小 KL。[1]

要检查 posterior collapse、action ignoring 和 one-step/open-loop gap。PlaNet latent overshooting 不能被说成该 DreamerV3 repo 的实现机制。[2]

## 6. Reward：一步即时信号

\[
\mathcal L_r
=-\frac{1}{N_r}\sum_t m_t^r
\log p_\theta(r_t\mid h_t,z_t).
\]

变量解释：\(r_t\) 是数据合同中的一步 reward，\(m_t^r\) 是有效 mask。直觉是 imagined latent 需要局部任务信号。实现映射：固定 reward shaping、scale/symlog、sparse/dense 和 terminal transition 的索引。[1]

**严格区分：**reward 是一步信号；value 是特定 policy/discount 下的累计未来回报；success classifier 是任务判定。三者不能混成“好坏分数”。

## 7. Continuation：是否继续 / learned discount

\[
\mathcal L_c
=-\frac{1}{N_c}\sum_t m_t^c
\left[c_t\log\hat c_t+(1-c_t)\log(1-\hat c_t)\right].
\]

变量解释：\(c_t\) 是 continuation target，\(\hat c_t\) 是预测概率。直觉是决定 imagined return 是否继续 bootstrap。实现映射：frozen repo 使用 `~is_terminal`；启用 `contdisc` 时再乘 `(1-1/horizon)`，语义更接近 learned discount。[1]

首查四类 bug：off-by-one、timeout 被误当 terminal、reset/padding 未 mask、`is_last` 与 `is_terminal` 混用。

## 8. Perceptual：feature-space similarity

\[
\mathcal L_{\mathrm{perc}}
=\sum_{l\in\mathcal S}\alpha_l\frac{1}{N_l}
\left\|\operatorname{norm}(\phi_l(\hat o_t))
-\operatorname{norm}(\phi_l(o_t))\right\|_2^2.
\]

变量解释：\(\phi_l\) 是预训练 feature extractor 的第 \(l\) 层，\(\alpha_l\) 是 layer weight。直觉是比较语义/结构 feature 而非逐像素相等。实现映射：记录 backbone/revision、frozen/trainable、输入 normalize、layer、resize、mask、weight 与 reduction。[3][4]

perceptual loss 可能对纹理/小位移更稳健，也可能忽略毫米位姿、深度、gripper aperture 和接触状态。LPIPS 是感知距离家族，不是 actionability 保证。

## 9. Mask、reduction 与有效权重

\[
\bar{\mathcal L}_k
=\frac{\sum_i m_{k,i}\ell_{k,i}}
{\max(1,\sum_i m_{k,i})},
\qquad
\mathcal L=\sum_k\lambda_k\bar{\mathcal L}_k.
\]

变量解释：\(m_{k,i}\) 决定有效元素，denominator 决定 loss 标度。直觉是 nominal weight 只有结合 reduction 和 route frequency 才有意义。实现映射：同时保存 raw sum、valid count、reduced/scaled loss、route count 和 per-module gradient norm。

不同 likelihood、pixel/token/sequence denominator、free nats、symlog 与 class imbalance 下，raw loss 不能直接比大小。

## 10. 最小 objective audit 伪代码

```python
def audit_objectives(batch, model, scales):
    # Posterior reads observations; prior must not read future observations.
    post, prior, feat = model.observe(batch.obs, batch.prev_action)

    # Keep stop-gradient directions separate so gradient ownership is auditable.
    dyn = kl(stop_gradient(post), prior).clamp_min(model.free_nats)
    rep = kl(post, stop_gradient(prior)).clamp_min(model.free_nats)

    # Build each target with its own time index, mask and denominator.
    rec = masked_loss(model.decoder(feat), batch.obs, batch.obs_mask)
    rew = masked_loss(model.reward(feat), batch.reward, batch.reward_mask)
    con_target = build_continuation(batch.is_terminal, batch.is_timeout)
    con = masked_loss(model.continue_head(feat), con_target, batch.valid_mask)
    perc = perceptual_loss(model.decoder(feat), batch.obs, frozen_features=True)

    terms = dict(rec=rec, dyn=dyn, rep=rep, rew=rew, con=con, perc=perc)
    return weighted_sum(terms, scales), log_denominators_and_gradients(terms)
```

`build_continuation` 必须服从具体 dataset/environment 合同；这段是审计骨架，不是某个个人项目的已运行代码。

## 11. Matched ablation

固定 data split/sampler、seed、steps/tokens、optimizer、batch、architecture、init、augmentation、eval 和 compute：

| arm | 诊断目标 |
| --- | --- |
| base | 最小 baseline |
| +rec | observation reconstruction 增量 |
| +dyn/rep | prior/posterior consistency 增量 |
| +reward | immediate reward 增量 |
| +continue | termination/discount 增量 |
| +perceptual | feature-space objective 增量 |
| combined | 交互作用 |
| overwide/overweight | 容量/辅助目标主导反例 |

同时报告 one-step、open-loop horizon curve、action sensitivity、reward/continue calibration、closed-loop success、compute/latency 与 seed CI。`base vs combined` 不能归因单项。

## 12. 高频失败诊断

| 症状 | 首查 |
| --- | --- |
| rec 下降但 rollout 漂 | posterior shortcut、prior rollout、action sensitivity |
| KL 很低且 decoder 模糊 | collapse、posterior usage、capacity |
| dyn/rep 卡在 1 nat | clipping proportion、entropy、scale、gradient |
| reward 好但 success 差 | reward/value/success 边界、policy OOD、continue |
| continue 总为 1 | class imbalance、timeout/terminal、off-by-one |
| perceptual 好但 contact 差 | backbone domain、geometry/depth/contact sensitivity |
| combined 退化 | gradient conflict、effective weight、mask/route、capacity |

## 13. 项目挂钩与真实性边界

WAM 当前支持解释 upstream action/future/value slot、condition/loss mask 与 objective audit，但没有 local objective config、gradient trace、action-only/+world/+value/all matched result；历史 MSE/成功率已经安全降级。

UWM/LIBERO 支持 shared diffusion 的 action/video 输出和协议绑定的训练/评估材料，但没有 reconstruction/dynamics/reward/continue/perceptual 单项消融；不能把 user-confirmed 74.4% 归因到某个 objective。[5][6]

面试安全表达：

> 我能逐项闭合 prediction、target、mask、reduction、scale 和 gradient path，并设计 matched ablation；当前个人证据没有 objective-level 因果实验，所以只讲机制与审计，不声称某项 loss 已提升成功率。

## 14. 实战检查清单

- [ ] 每项 loss 的 prediction/target/time index 明确；
- [ ] missing/padding/terminal/route mask 与 denominator 可追溯；
- [ ] dyn/rep stop-gradient 与 free-nats 比例可观测；
- [ ] reward、value、success、continuation 不混用；
- [ ] perceptual backbone/layer/frozen/domain 明确；
- [ ] raw/reduced/scaled loss、valid count、gradient norm 同报；
- [ ] teacher-forced、open-loop、closed-loop 指标分层；
- [ ] matched single-objective/combined/overwide arms；
- [ ] public mechanism 与 personal evidence 分开。

## 15. 参考来源

1. [WM-011 Source Freeze](../sources/vol_04_wm011_objective_semantics_source_freeze.html)：primary/source-code SHA、公式和项目边界。
2. Hafner et al., [DreamerV3](https://arxiv.org/abs/2301.04104)；Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)。
3. Johnson et al., [Perceptual Losses](https://arxiv.org/abs/1603.08155)。
4. Zhang et al., [LPIPS / Deep Features as a Perceptual Metric](https://arxiv.org/abs/1801.03924)。
5. [WAM Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。

## 16. 下一节点

本节点保持 WARN、题卡保持 unseen。下一 bounded slice 只做 `VLA-WM-012`：RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导。
