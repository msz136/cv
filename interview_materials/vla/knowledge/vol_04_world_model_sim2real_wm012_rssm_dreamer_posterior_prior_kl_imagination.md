# VOL 04 World Model / Sim2Real：RSSM / Dreamer Posterior、Prior、KL Balancing 与 Imagination（WM-012）

> 状态：drafted / VLA-WM-012 / knowledge_42_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导？  
> 前置：[WM-004 RSSM Data Flow](vol_04_world_model_sim2real.html)、[WM-011 Objective Semantics](vol_04_world_model_sim2real_wm011_objective_semantics.html)、[WM-012 Source Freeze](../sources/vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)；actor/critic 见 [WM-021](vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.html)。

## 1. 面试结论

RSSM 的关键不是“RNN + VAE”标签，而是两条信息路径：

```text
history latent + previous action → deterministic memory h_t
                                  ├→ prior p(z_t|h_t)
current observation o_t ──────────┴→ posterior q(z_t|h_t,o_t)
```

训练时 posterior 用 observation 修正 belief，KL 让 prior 学会预测 posterior并限制 representation；imagination 从 replay posterior state 起步，之后只用 policy action + prior 循环，不能读取未来 observation。

## 2. RSSM state

\[
s_t=(h_t,z_t),
\qquad
h_t=f_\phi(h_{t-1},z_{t-1},a_{t-1}).
\]

变量解释：\(h_t\) 是 deterministic recurrent memory，\(z_t\) 是 stochastic representation。直觉是 \(h_t\) 汇总历史/action，\(z_t\) 容纳当前 observation 带来的新信息和多可能状态。实现映射：frozen reimplementation 先用 previous action 调 `_core` 更新 deter，再结合当前 token 得 posterior。[1]

## 3. Prior 与 posterior

\[
\hat z_t\sim p_\phi(z_t\mid h_t),
\qquad
z_t\sim q_\phi(z_t\mid h_t,o_t).
\]

变量解释：prior 不读当前 observation；posterior 读当前 observation。直觉是 prior 是预测，posterior 是看见现实后的校正。实现映射：`_prior(deter)` 输出 prior logits；`_observe` 用 deter+encoder token 输出 posterior logits并采样。[1][2]

## 4. Action-conditioned sequential model

\[
p(o,r,c,z\mid a)
=\prod_t p(z_t\mid h_t)
p(o_t\mid h_t,z_t)
p(r_t\mid h_t,z_t)
p(c_t\mid h_t,z_t).
\]

变量解释：\(h_t\) 已包含过去 latent/action；\(c_t\) 是 continuation/discount。直觉是 prior 先生成 latent，再由 heads 解释 observation 与任务信号。实现映射：具体 observation key、reward/continue 时间索引和 likelihood 仍按 WM-011 的 objective contract 冻结。[1][3]

## 5. Approximate posterior

\[
q(z_{1:T}\mid o_{1:T},a_{0:T-1})
=\prod_t q(z_t\mid h_t,o_t).
\]

变量解释：这是逐时刻 filtering approximation；每一步只能使用允许的当前/历史 observation。直觉是“看到 \(o_t\) 后更新当前 belief”，不是读取未来整段。实现映射：需要 causal encoder test；bidirectional future token 会造成 leakage。

## 6. Sequential ELBO

\[
\log p(o,r,c\mid a)
\ge
\mathbb E_q\sum_t
\left[
\log p(o_t,r_t,c_t\mid h_t,z_t)
-D_{\mathrm{KL}}(q(z_t\mid h_t,o_t)\|p(z_t\mid h_t))
\right].
\]

变量解释：prediction likelihood 让 latent 解释 target；KL 让 posterior 与 action-conditioned prior 对齐。直觉是 sequential VAE 同时解决“编码现实”和“预测未来”。实现映射：DreamerV3 会把 prediction、dyn、rep 拆开并加 scale/free bits，抽象 ELBO 不是 exact config。[2][3]

## 7. KL 的两项工作

\(D_{\mathrm{KL}}(q\|p)\) 同时：

1. 更新 prior 追 posterior；
2. 更新 posterior 靠近 prior，使 representation 可预测。

坏 prior 过早强压 posterior，会丢 observation 信息；完全不约束 posterior，又可能让它编码 prior 无法预测的任意细节。因此要拆 gradient recipient，而不只调一个总 KL 标量。

## 8. DreamerV2 KL balancing

\[
\mathcal L_{\mathrm{KL-bal}}
=\alpha D_{\mathrm{KL}}(\operatorname{sg}(q)\|p)
+(1-\alpha)D_{\mathrm{KL}}(q\|\operatorname{sg}(p)),
\qquad \alpha=0.8.
\]

变量解释：第一项只训 prior，第二项只约束 posterior；\(\alpha=0.8\) 是 DreamerV2 paper setting。直觉是让困难的 transition predictor 更快追 representation，避免坏 prior 过早压平 posterior。[2]

## 9. DreamerV3 dyn / rep

\[
\mathcal L_{\mathrm{dyn}}
=\max(1,D_{\mathrm{KL}}[\operatorname{sg}(q)\|p]),
\qquad
\mathcal L_{\mathrm{rep}}
=\max(1,D_{\mathrm{KL}}[q\|\operatorname{sg}(p)]).
\]

变量解释：dyn 训 sequence prior，rep 约束 representation；1 nat 是 free-bits threshold。直觉是 KL 已足够小时把优化重点还给 prediction。实现映射：frozen `RSSM.loss` 对应两条 KL 和 `jnp.maximum`；config scale 是 `dyn=1.0, rep=0.1`。[1][3]

不要说“DreamerV3 使用 α=0.8”：V2 与 V3 共享 stop-gradient balancing 思路，但 exact objective/config 不同。

## 10. Free bits 怎么看

free bits 不是免 KL，也不保证不 collapse。只看 clipped `dyn=rep=1` 无法知道 raw KL 是 0.01 还是 0.99 nat。应同报：

- raw/clipped KL 与 clipping ratio；
- prior/posterior entropy、categorical usage；
- reconstruction/reward/continue fit；
- action sensitivity 与 open-loop horizon error。

## 11. Reset 与 previous-action 索引

frozen `_observe` 顺序：mask reset → 用旧 \((h,z)\)+previous action 更新 \(h_t\) → 用当前 token 得 \(z_t\)。因此传入 action 必须对应 \(a_{t-1}\)。错用当前 \(a_t\)、reset 前动作或跨 episode carry 会造成 off-by-one/leakage；posterior 仍可能靠当前帧重建好，掩盖 transition 错误。[1]

## 12. Categorical latent 的代码边界

frozen code 的 state shape 是：

```text
deter: [B, deter]
stoch/logit: [B, stoch, classes]
```

`_dist` 构造 one-hot categorical distribution，KL 跨 stochastic variables 聚合。它是当前 frozen V3 reimplementation 的实现事实，不代表所有 RSSM 都必须离散化。[1]

## 13. Posterior start 到 prior-only imagination

训练 replay sequence 先经 `observe` 得 posterior entries；`starts` 选最后 \(K\) 个有效 state 作为 \(s_0\)。之后每一步：

\[
\hat a_t\sim\pi(\cdot\mid\hat s_t),
\]

\[
\hat h_{t+1}=f(\hat h_t,\hat z_t,\hat a_t),
\qquad
\hat z_{t+1}\sim p(\cdot\mid\hat h_{t+1}).
\]

变量解释：帽号表示 imagined variable。直觉是 replay posterior 只提供现实锚点；从第一步未来开始只靠 policy action 与 prior。实现映射：frozen `imagine(single=True)` 是 policy→core→prior→sample，scan 重复 \(H\) 步。[1]

## 14. Imagined joint distribution

\[
p(\hat z_{1:H},\hat a_{0:H-1}\mid s_0)
=\prod_{t=0}^{H-1}
\pi(\hat a_t\mid\hat s_t)
p(\hat z_{t+1}\mid\hat h_{t+1}).
\]

变量解释：\(s_0\) 来自 replay posterior；后续没有 observation factor。reward/continue/value 可在 imagined state 上查询，但不能偷偷把未来 encoder token送回 transition。actor/critic 如何用这些 trajectory 见 WM-021。[4]

## 15. Future leakage test

以下都不是真正 pure-prior imagination：

- rollout 后续继续读取真实 frame/token；
- posterior encoder 能看未来帧；
- action/observation 错位，未来 action 进入当前 step；
- reset/padding 未切断 episode；
- 用 posterior trajectory 报 open-loop metric。

最小测试：起点后替换未来 observation，prior trajectory必须不变；posterior filtering trajectory应随 observation intervention 改变。

## 16. 可审计伪代码

```python
def filter_then_imagine(batch, rssm, policy, horizon):
    # Encode replay observations causally and align previous actions with o_t.
    tokens = encode_causally(batch.observation)
    entries, post = rssm.observe(tokens, batch.previous_action, batch.is_first)

    # Separate gradients that train the prior from those regularizing the posterior.
    prior = rssm.prior(post.deter)
    dyn = kl(stop_gradient(post.dist), prior).clamp_min(1.0)
    rep = kl(post.dist, stop_gradient(prior)).clamp_min(1.0)

    # Anchor in replay posterior states; no future observations enter after this point.
    starts = select_valid_posterior_starts(entries, batch.valid_mask)
    imagined = rssm.imagine(starts, policy, horizon)

    # Keep raw KL, clipping, entropy, actions and horizon-wise rollout traces.
    return imagined, audit(dyn, rep, post, prior, imagined)
```

这是机制审计骨架，不是用户项目已运行代码；categorical latent、1 nat 与 scale 要按具体 version/config确认。

## 17. 诊断与 matched probes

| 症状 | 首查 |
| --- | --- |
| posterior 好、prior 差 | action/time index、prior capacity、KL gradient、future shortcut |
| raw KL≈0 且表示无信息 | collapse、decoder/reward shortcut、free-bits日志 |
| raw KL 很大 | action missing、reset leakage、posterior塞细节、prior欠拟合 |
| dyn/rep总是1 | raw KL 与 clipping ratio |
| prior 对 action 不敏感 | action mask/order/scale、data coverage、core input |
| episode 开头异常 | previous action、reset/carry off-by-one |
| horizon增长即崩 | one-step-only fit、sampling、terminal、model bias |
| imagined好、real差 | 转 WM-021 做 exploitation/value/paired rollout |

固定 data/steps/architecture/optimizer/seed，比较 unbalanced KL、V2-style α sweep、V3 dyn/rep scale/free-bits、posterior rollout、prior-only rollout、zero/shuffled action。报告 raw/clipped KL、entropy/usage、gradient、one-step/open-loop/action sensitivity 与 closed-loop success。

## 18. 项目挂钩与真实性边界

WAM/Cosmos 是 diffusion latent slot + action/future/value + mask/planning contract；UWM 是 shared action/video diffusion。它们都不是当前材料里的 RSSM/Dreamer implementation，不能说项目用了 posterior/prior、KL balancing 或 Dreamer imagination。[5][6]

面试安全表达：

> 我能从 sequential ELBO 推导 posterior/prior 与 KL 双重职责，并按 frozen code 解释 replay filtering、posterior starts 和 prior-only imagination；WAM/UWM 不是 RSSM 项目，且我没有本地 Dreamer checkpoint/trace，所以不声称个人复现或收益。

## 19. 实战检查清单

- [ ] \(h_t,z_t,a_{t-1},o_t\) 时间索引明确；
- [ ] posterior 可读字段与 future leakage test 明确；
- [ ] prior 不读取当前/未来 observation；
- [ ] KL 两条 stop-gradient 与版本/config 分开；
- [ ] raw/clipped KL、entropy、usage、gradient同报；
- [ ] reset、padding、previous action unit test；
- [ ] imagination start 的 episode/time/validity可追溯；
- [ ] posterior与prior-only horizon curve分开；
- [ ] action intervention与closed-loop证据分层；
- [ ] Dreamer机制不外推为WAM/UWM个人实现。

## 20. 参考来源

1. [WM-012 Source Freeze](../sources/vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)：primary/frozen-code SHA、推导与项目边界。
2. Hafner et al., [DreamerV2](https://arxiv.org/abs/2010.02193)。
3. Hafner et al., [DreamerV3](https://arxiv.org/abs/2301.04104)；Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)。
4. [WM-021 Dreamer Imagination Actor/Critic](vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.html)。
5. [WAM Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。

## 21. 下一节点

本节点保持 WARN、题卡保持 unseen。下一 bounded slice 只做 `VLA-WM-013`：latent overshooting 或 multi-step consistency loss 解决什么、可能带来什么偏差。
