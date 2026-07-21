# VOL 04 World Model / Sim2Real：Latent Overshooting 与 Multi-step Consistency（WM-013）

> 状态：drafted / VLA-WM-013 / knowledge_43_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：latent overshooting 或 multi-step consistency loss 解决什么，可能带来什么偏差？  
> 前置：[WM-012 RSSM / Dreamer](vol_04_world_model_sim2real_wm012_rssm_dreamer_posterior_prior_kl_imagination.html)、[WM-013 Source Freeze](../sources/vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html)；horizon与failure见 [WM-018](vol_04_world_model_sim2real_wm018.html)、[WM-020](vol_04_world_model_sim2real_wm020_failure_diagnostics.html)。

## 1. 面试结论

标准一步 KL 像“每步都看答案后考下一步”；latent overshooting 则从较早 posterior state 出发，关闭中间 observation，沿动作滚动多步 prior，再对齐未来 posterior。它把多步 rollout mismatch直接放进训练，但 target仍是 learned posterior，不是真实物理 state，因此可能放大shortcut、错位、受限分布和过强regularization。

## 2. 一步 objective 的限制

\[
\mathcal L_1
=\sum_t D_{\mathrm{KL}}\!\left[
q(s_{t+1}\mid o_{\le t+1},a_{\le t})
\,\|\,
p(s_{t+1}\mid s_t,a_t)
\right].
\]

变量解释：\(s_t\) 通常是 observation-informed posterior state；transition只被直接监督一步。直觉是有限容量模型的一步最优不一定是多步最优。实现映射：必须将teacher-forced/posterior rollout与prior-only horizon curve分开。[1]

## 3. d-step prior

\[
\hat s_{t-d\mid t-d}\sim q(s_{t-d}\mid o_{\le t-d},a_{<t-d}),
\]

\[
\hat s_{j+1\mid t-d}\sim p(s_{j+1}\mid\hat s_{j\mid t-d},a_j),
\quad j=t-d,\ldots,t-1.
\]

变量解释：\(\hat s_{t\mid t-d}\) 只看见 observation到 \(t-d\)，中间完全用 prior。直觉是模拟真实 open-loop consequence。实现映射：冻结 start、action slice、distance、seed、terminal/mask。[1][2]

## 4. Latent overshooting loss

\[
\mathcal L_{\mathrm{OS}}
=\frac{1}{Z}\sum_{t,d=1}^{D}
m_{t,d}\beta_d
D_{\mathrm{KL}}\!\left[
\operatorname{sg}(q(s_t\mid o_{\le t},a_{<t}))
\,\|\,
p^{(d)}(s_t\mid s_{t-d},a_{t-d:t-1})
\right],
\]

\[
Z=\sum_{t,d}m_{t,d}.
\]

变量解释：\(D\) 是最大distance，\(\beta_d\) 是距离权重，\(m_{t,d}\) 是padding/terminal mask。直觉是未来 posterior做教师，直接训练各距离prior。实现映射：这是PlaNet Eq.7/代码的审计化简写；正式目标还对中间stochastic state取期望。[1][2]

## 5. Target 不是 ground truth state

future posterior能看 \(o_t\)，所以比long-horizon prior更informed；但它仍是encoder产生的learned target。若posterior含future leakage、背景shortcut、错误contact representation，overshooting会更强地复制错误。

因此安全说“对齐future posterior”，不能说“对齐真实latent/物理state”。

## 6. Stop-gradient

PlaNet实践中对 \(d>1\) posterior target stop-gradient，使multi-step prior追posterior，而不是让posterior被较差的long-horizon prior拖动。[1]

不stop可能通过移动target降低loss、丢信息；永远stop又可能锁住posterior错误。要联看prediction heads、entropy/usage、reward/contact probe与closed-loop。

## 7. Observation vs latent overshooting

| 方法 | multi-step监督 | 优点 | 风险 |
| --- | --- | --- | --- |
| observation overshooting | 每个d-step state解码并算observation likelihood | target直观 | 图像成本高、像素主导 |
| latent overshooting | d-step prior与future posterior做latent divergence | 快、无需额外图像生成 | target依赖encoder语义/尺度 |

两者都不自动证明action consequence正确。

## 8. Official PlaNet code path

`google-research/planet@c04226b` 的 `overshooting.py`：先closed-loop得到posterior starts；按distance shift target/action/mask；将`use_obs=false`且embedding置零；从每个start open-loop unroll；恢复batch维并返回prior/posterior/mask。[2]

`training/utility.py`可选stop posterior gradient，计算`KL(posteriors||priors)`，应用free nats并reduce mean。previous-action示例`obs=[A B C]`对应`action=[0 A B]`，action索引错一位会被多步放大。

## 9. Final/default PlaNet 没启用

论文说明若干dynamics model受益，但最终RSSM agent不需要overshooting；official README的PlaNet paper experiment不加额外参数，frozen config默认：[1][2]

```text
overshooting_scale = 0.0
overshooting_distance = 0
os_stop_posterior_grad = True
```

所以它是PlaNet提出并保留的可选机制，不是“PlaNet成功必需项”。

## 10. DreamerV3 边界

当前 frozen DreamerV3 reimplementation只有one-step dyn/rep KL、free nats与imagination证据；没有PlaNet式从每个posterior start对多个distance prior施加overshooting loss。两者都用RSSM不等于训练objective相同。[3]

## 11. 偏差：posterior与shortcut

overshooting优化的是future posterior target。posterior若偏向背景/相机/奖励shortcut，多步一致性会放大而非纠正。检查：causal encoder、future-frame removal、background/camera counterfactual、latent/head/contact probes。

## 12. 偏差：多模态与受限分布

真实未来多模态但latent family受限时，多距离KL可能让prior过宽、丢难预测细节或在sample path间梯度不稳。平均latent KL改善仍可能掩盖rare contact mode恶化。要报entropy、calibration、mode/failure-family指标。

## 13. 偏差：过强regularization

大 \(D\)、大 \(\beta_d\) 或重复计数会让“可预测”压过“信息充分”。症状：OS loss下降、prior/posterior更近，但observation/reward/contact/action probe变差，latent entropy/usage下降。

## 14. 偏差：weight与denominator

长distance near episode end的valid样本更少。global mean可能让short distance因条目多而主导；per-distance等权又可能放大long distance高方差。记录每个distance的numerator、valid count、mean、scale、gradient与task/episode分层。

## 15. 偏差：计算预算

从每个time start展开最多 \(D\) 步，计算/activation近似随 \(T\times D\) 增长。matched比较要同时说明data samples/tokens、optimizer steps、wall-clock、throughput、peak memory；否则objective effect与compute/data exposure混在一起。

## 16. 偏差：action、reset、terminal

multi-step loss会把一个错位传播多次。必须测试previous-action对齐、padding/terminal stop、reset/carry、timeout/continuation与heterogeneous action normalizer；不能让rollout跨episode。

## 17. “Multi-step consistency”不是一个固定loss

它还可能指 \(k\)-step latent regression/cosine、multi-step reward/observation likelihood、cycle consistency或rollout distillation。先报prediction、target、distance、divergence、stop-gradient、stochastic expectation、mask与reduction，再比较方法。

## 18. 可审计伪代码

```python
def latent_overshooting(sequence, model, max_distance, beta):
    # Filter once; learned posteriors are starts and future targets.
    posterior = model.observe(sequence.obs, sequence.previous_action,
                              sequence.is_first)
    terms = []
    for distance in range(1, max_distance + 1):
        # Roll only the prior along aligned recorded actions.
        prior_d = model.roll_prior(
            posterior.start(distance), sequence.action_slice(distance),
            use_observation=False)

        # Do not cross padding/reset/terminal; freeze d>1 targets.
        target = stop_gradient(posterior.target(distance))
        mask = sequence.valid_pair_mask(distance, stop_at_terminal=True)
        terms.append(masked_kl(target, prior_d, mask) * beta[distance])

    # Keep per-distance numerator/count; a single mean hides weighting.
    return declared_reduction(terms), audit_per_distance(terms)
```

这是审计骨架；PlaNet exact code还包含stochastic intermediate rollouts、reshape/crop与free-nats语义。

## 19. Matched ablation

固定data、capacity、optimizer、steps/tokens、seed、one-step loss与eval：

- one-step only；
- +OS `D=3/5/10`；
- equal/decayed \(\beta_d\)；
- stop-target on/off diagnostic；
- observation overshooting；
- multi-step reward；
- zero/shuffled action；
- capacity-matched wider baseline。

报告per-distance KL/count、entropy/usage、one-step/open-loop state/reward/continue、action sensitivity、planning/closed-loop success、compute与seed CI。

## 20. 高频诊断

| 症状 | 首查 |
| --- | --- |
| OS降、open-loop不变 | short-distance主导、posterior shortcut、metric尺度 |
| latent好、reward/contact差 | 信息被压、restricted family、head mismatch |
| long-distance震荡 | D/β、sample variance、action/reset错位 |
| valid count骤减 | episode长度、terminal/padding、denominator |
| posterior退化 | stop-gradient、effective scale、free-nats |
| action swap不变 | action未进transition、coverage、shortcut |
| train慢、score不变 | compute/data exposure未matched |

## 21. 项目挂钩与真实性边界

WAM/Cosmos与UWM是diffusion-based action/future/video contracts，不是PlaNet overshooting。当前无per-distance latent KL、overshooting config、D/β sweep、posterior/prior trace或matched success evidence。[4][5]

面试安全表达：

> 我能解释从posterior start做prior-only多步对齐，也会先说明PlaNet final/default并未启用；WAM/UWM不是该实现，所以我只把它作为可选诊断/消融设计，不声称项目使用或受益。

## 22. 实战检查清单

- [ ] exact multi-step prediction/target/divergence明确；
- [ ] distance、\(\beta_d\)、mask、denominator可追溯；
- [ ] posterior target不是ground truth；
- [ ] d>1 stop-gradient与free-nats明确；
- [ ] previous-action/reset/terminal unit test；
- [ ] per-distance raw loss/count/gradient/compute同报；
- [ ] latent、reward/contact、action sensitivity联合评估；
- [ ] final/default PlaNet与可选实现分开；
- [ ] PlaNet与DreamerV3实现不混写；
- [ ] public mechanism与personal evidence分开。

## 23. 参考来源

1. Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)。
2. `google-research/planet@c04226b`: [`overshooting.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/tools/overshooting.py), [`utility.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/training/utility.py), [`configs.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/scripts/configs.py)。
3. [WM-013 Source Freeze](../sources/vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html) 与 [Foundations Independent Review](../sources/vol_04_world_model_foundations_independent_fact_review.html)。
4. [WAM Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
5. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。

## 24. 下一节点

本节点保持 WARN、题卡保持 unseen。下一 bounded slice 只做 `VLA-WM-014`：action-conditioned prediction 怎样区分相关性预测与可干预 dynamics。
