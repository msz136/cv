# VOL 04 WM-013 Source Freeze：Latent Overshooting 与 Multi-step Consistency

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-013 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-013  
> 本轮边界：只冻结 PlaNet latent overshooting 的问题定义、multi-step variational objective、posterior-target/prior-rollout 实现、distance/weight/mask/gradient 合同与潜在偏差；不把 PlaNet overshooting 写成 DreamerV3 frozen repo 机制，不把泛称 multi-step consistency 等同 PlaNet exact objective，也不把公开机制写成本地 WAM/UWM 结果。

## 1. 冻结结论

1. 标准 sequential ELBO 的 transition KL 主要在 posterior state 附近训练一步 prior；梯度不必穿过连续多次 transition，因此有限容量模型的一步最优不一定是多步最优。
2. latent overshooting 从较早的 posterior state 出发，关闭中间 observation，沿真实 action sequence 滚动 \(d\) 步 prior，再用未来 posterior 作为 latent target，从而直接训练不同距离的 open-loop consistency。
3. 它不同于 observation overshooting：后者对每个 multi-step prediction 解码 observation/reconstruction，图像域成本高；latent overshooting 只计算 latent divergence。
4. PlaNet 论文把它作为 generalized variational objective，但同时明确最终 RSSM agent 并不需要该项；官方 frozen repo 默认 `overshooting_scale=0.0`、`overshooting_distance=0`。
5. 更强 multi-step consistency 不自动更好：错误 posterior、future leakage、action/reset错位、受限分布、过强 regularization、距离权重/denominator 与额外计算都可能制造偏差。
6. latent KL 改善不能替代 action intervention、reward/termination horizon curve、planning/closed-loop success 与项目 evidence。

## 2. 一手来源与冻结快照

| ID | 来源 | 冻结版本与响应 SHA-256 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Hafner et al., *Learning Latent Dynamics for Planning from Pixels*（PlaNet） | arXiv `1811.04551`；ar5iv response `6a9bed11e5963626016235227ab85594ae5d42773e675860788c51a071929a97` | standard bound 的一步限制、observation/latent overshooting、Eq. 7、\(1\le d\le D\)、posterior stop-gradient、final-agent caveat | DreamerV3 exact implementation、本地 VLA uplift |
| S2 | `google-research/planet` official project code | commit `c04226b6db136f5269625378cd6a0aa875a92842`；README `61d0d9215eae2cc8ee4d035913f745fa426db3a6342c5008ee5bae158aa3bd48`；Apache-2.0 LICENSE `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | README 将 repo 标为 PlaNet open-source implementation；paper experiment默认入口 | 当前依赖可运行、论文所有 checkpoint/result 已复现 |
| S3 | PlaNet overshooting implementation | `planet/tools/overshooting.py` `c87beb84bc4304a26af833f4e39b692c1b37e632bce63f1ec6405dfa2a5b1358`；`training/utility.py` `885d3d29ccc3b15cc71a7a32da5ff952313b37d76e6804cd96e7bc969f467f15`；`test_overshooting.py` `6f524056e087c80c398b26408a092bf0e701d12d1e1fe3953804e6cede6e4d11` | posterior starts、shifted actions、use_obs=false、padding mask、optional stop-gradient、divergence/free-nats/reduction | 默认已启用或个人项目使用 |
| S4 | PlaNet config/model | `configs.py` `a98af57c64c9f6f1d8d3b3a29caec922938e6daf552cbf944f6007465e985807`；`models/rssm.py` `7462f36a40a504ec912435bd6c5a78fd6878308826888341a20c602291b12712` | default overshooting scale/distance=0、stop posterior grad=true、free_nats=3、state divergence | 所有实验变体或 Dreamer defaults |
| S5 | [Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html) | canonical SHA `bb48af7605688132ddd589109c8417dd0ebfe65f504a98cf5ab660f01e34ba7b` / `da16c172179cae926d329259e76955a55555fe53a15233f265d1f74a3d421ae4` | WM-013 可逐节点生成；PlaNet→DreamerV3 强归因被禁止 | local overshooting run |
| S6 | [WM-012 RSSM/Dreamer](vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)、[WM-018 Horizon](vol_04_wm018_prediction_horizon_source_freeze.html)、[WM-020 Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html) | canonical SHA `c5f8a2dd056736a8b7338cd76116631a8bf42a3d10c05e86d6bb4cfbf64ae6e0` / `6927970508d01f328aef6ca629a72589d986a48b9ac811eb8eb6327907b00254` / `4053bb051296bcc785a3e1b7f7ddf0a0c75339dcb4f8c84aed755b49888c06dd` | posterior/prior、horizon 与 failure-probe 去重边界 | 本节点完成项目实验 |
| S7 | [WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories | canonical SHA `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d` / `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 项目 architecture/protocol 与缺失 artifact | local latent-overshooting/multi-step-consistency causal result |

## 3. 与相邻节点的边界

| 节点 | 已回答 | WM-013 只补什么 |
| --- | --- | --- |
| WM-005/006 | one-step、teacher-forcing、open-loop gap | 为什么 objective 的梯度距离也重要 |
| WM-012 | RSSM posterior/prior、KL balancing、prior-only imagination | 从多个 posterior start 直接监督多步 prior |
| WM-018 | horizon 长短的控制/训练取舍 | multi-step loss 的 distance/weight/mask 实现 |
| WM-020 | collapse/leakage/action ignoring 诊断 | overshooting 特有的 target、梯度与偏差 |

## 4. 标准一步 KL 的限制

令当前 posterior 为 \(q_\phi(s_t\mid o_{\le t},a_{<t})\)，一步 prior 为 \(p_\theta(s_{t+1}\mid s_t,a_t)\)。标准项：

\[
\mathcal L_{1}
=\sum_t D_{\mathrm{KL}}\!\left[
q_\phi(s_{t+1}\mid o_{\le t+1},a_{\le t})
\,\|\,
p_\theta(s_{t+1}\mid s_t,a_t)
\right].
\]

变量解释：\(s_t\) 通常来自 observation-informed posterior；transition 只被直接要求预测下一步。直觉是老师每步纠正后考一步，未必能学会连续闭卷滚动。实现映射：一步 KL 好仍需 prior-only horizon curve；不能从单步 scalar 推出 \(H\)-step planning 可用。

## 5. 有限容量为什么使一步与多步最优不同

若模型能完美拟合真实 transition，一步正确会推出多步正确。但实际 latent dimension、distribution family、网络容量、优化和数据有限；一步 loss 可能偏好局部平均或 posterior shortcut，而 planning 需要 reward-relevant long-horizon consequence。[S1]

这不是说 multi-step loss 能消除 compounding error，而是把训练权重从“只在一步邻域正确”重新分配到“多个 rollout distance 也尽量一致”。

## 6. d-step prior

从 time \(t-d\) 的 posterior state 出发，沿动作序列递推：

\[
\hat s_{t-d\mid t-d}\sim q_\phi(s_{t-d}\mid o_{\le t-d},a_{<t-d}),
\]

\[
\hat s_{j+1\mid t-d}\sim
p_\theta(s_{j+1}\mid \hat s_{j\mid t-d},a_j),
\quad j=t-d,\ldots,t-1.
\]

变量解释：\(\hat s_{t\mid t-d}\) 是只看见 observation 到 \(t-d\) 的 \(d\)-step prediction。直觉是把中间 observation 拿走，模拟真实 open-loop consequence。实现映射：每个 start、action slice、distance 与 random sample/seed 必须可追溯。

## 7. Latent overshooting 的简化 estimator

\[
\mathcal L_{\mathrm{OS}}
=\frac{1}{Z}
\sum_{t}\sum_{d=1}^{D}
m_{t,d}\,\beta_d\,
D_{\mathrm{KL}}\!\left[
\operatorname{sg}\!\left(q_\phi(s_t\mid o_{\le t},a_{<t})\right)
\,\|\,
p_\theta^{(d)}(s_t\mid s_{t-d},a_{t-d:t-1})
\right],
\]

\[
Z=\sum_{t,d}m_{t,d}.
\]

变量解释：\(D\) 是最大 overshooting distance，\(\beta_d\) 是距离权重，\(m_{t,d}\) 过滤 padding/episode boundary，\(p^{(d)}\) 表示多次 transition 后的分布。直觉是未来 posterior 当教师，训练较早 start 的 open-loop prior。实现映射：这是 PlaNet Eq. 7/代码的审计化简写；正式下界还对中间 stochastic states 取期望，不能把单样本 KL 说成完整解析式。[S1][S3]

## 8. 为什么 target 用未来 posterior

未来 posterior 能读取 \(o_t\)，通常比 \(d\)-step prior 更 informed，因此可作为 latent target；但它是 learned target，不是真实 state。若 encoder 有 future leakage、背景 shortcut、错误 contact representation 或 task-irrelevant detail，overshooting 会更努力拟合这些错误。

高分回答必须说“对齐未来 posterior”，不能说“对齐 ground-truth latent state”。

## 9. 为什么 d>1 通常 stop posterior gradient

PlaNet 论文说明实践中对 \(d>1\) 的 posterior target stop-gradient，使 multi-step prediction 追 informed posterior，而不是让 posterior 被较差的 long-horizon prior 拉走。[S1]

若允许双向梯度，loss 可通过“移动 target”降低，representation 可能变得容易预测但丢信息。若永远 stop target，又会把 posterior 错误固定为教师。因此需要与 prediction heads、entropy/usage 和 downstream probe 联合观察。

## 10. Observation overshooting 与 latent overshooting

| 类型 | 多步预测后监督 | 优点 | 代价/风险 |
| --- | --- | --- | --- |
| observation overshooting | 解码每个 \(d\)-step state，计算 observation likelihood | target 直观，可看预测 | image decoder/likelihood 成本高，像素主导 |
| latent overshooting | 对齐 \(d\)-step prior 与 future posterior | 快、无需生成额外图像 | target 是 learned latent，语义/尺度依赖 encoder |

二者都不能自动证明 action consequence 正确；latent loss 甚至可能改善而 pixel/reward/contact 越差。

## 11. PlaNet official code 的 rollout contract

S3 `overshooting.py`：

1. 先 closed-loop unroll 得每个 time 的 posterior；
2. 将每个 posterior time 组织成 open-loop start；
3. action 使用“leading to current time step”的 previous-action 对齐，例如 observation `[A B C]` 对应 action `[0 A B]`；
4. `use_obs=false`、observation embedding置零，禁止中间 observation；
5. 从每个 start 并行 rollout `amount` 个 distance；
6. shift/merge/restore batch-time，并返回 prior/posterior/target/mask。

这个实现直接暴露三个高危点：previous-action off-by-one、padding/episode boundary、distance 维度的 reshape/reduction。

## 12. Official objective mapping

S3 `training/utility.py` 的 overshooting branch：

- 调 `tools.overshooting(..., overshooting_distance, posterior)`；
- 截取 `[:, :, 1:-1]`；
- 若 `os_stop_posterior_grad`，对 posterior stop-gradient；
- 计算 `divergence_from_states(posteriors, priors)`；
- free nats 为 `max(0, KL-free_nats)`；
- 最后 reduce mean，再由 `loss_scales` 加权。

这里 PlaNet 的 free-nats 写法与 DreamerV3 `max(KL, threshold)` 相差常数但梯度阈值类似；不能把日志 scalar 直接跨 repo 比较。

## 13. “PlaNet 默认使用 overshooting”是错误说法

S1 明确写：若干 dynamics model 受益，但最终使用 RSSM 的 agent 不需要 latent overshooting；appendix 又说明 previous version 使用过，后来发现不必要。[S1]

S2 README 说 paper PlaNet experiment 不加额外 params；S4 默认：

```text
overshooting_scale = 0.0
overshooting_distance = 0
os_stop_posterior_grad = True
```

因此安全说法是“PlaNet 论文提出并评估 latent overshooting，official repo保留可选实现，final/default RSSM path未启用”，不是“PlaNet成功依赖overshooting”。

## 14. 与 DreamerV3 的实现边界

当前 frozen DreamerV3 reimplementation 证据只有 one-step `dyn/rep` KL、free nats 与 imagination；未见 PlaNet式从每个 posterior start 对多 distance prior施加 overshooting loss。Source Audit A 独立复核已把“PlaNet overshooting → DreamerV3 implementation”列为 `BLOCKED FOR STRONG CLAIM`。[S5]

不能因为两者都用 RSSM、prior/posterior 或 multi-step imagination，就说 DreamerV3 训练采用 latent overshooting。

## 15. 偏差一：posterior target 不等于真值

overshooting 让 multi-step prior 更接近 future posterior。如果 posterior 使用背景、相机、future leakage 或 reward shortcut，对齐更紧会放大 shortcut，而不是纠正物理 dynamics。

最小检查：latent intervention、decoder/reward/contact probe、camera/background counterfactual、causal encoder test 与 future-frame removal。

## 16. 偏差二：受限分布与多模态未来

当真实未来多模态、但 prior/posterior family 受限时，多距离 KL 可能：

- 使 prior 过宽以覆盖互相冲突的 posterior；
- 使 representation 丢弃难预测但任务重要的细节；
- 在不同随机 sample/path 上给不稳定梯度；
- 改善平均 latent KL，却恶化 rare contact mode。

必须报告 calibration、entropy/mode coverage 与分 failure family 指标，不能只报 aggregate KL。

## 17. 偏差三：过强 consistency 与 representation collapse

大 \(D\)、大 \(\beta_d\) 或多距离重复计数会让“可预测”压过“信息充分”。症状是 overshooting loss下降、posterior/prior更接近，但 observation/reward/contact/action probe 变差，latent entropy/usage降低。

这与 WM-012 的 KL balancing 相连：multi-step prior 学习和 posterior regularization 的 gradient recipient、scale 与 free-nats 必须分别记录。

## 18. 偏差四：distance weighting 与 denominator

长距离在 episode 尾部可用样本更少。若直接对所有 valid element mean：

- 短 distance 可能因条目更多而主导；
- 或每 distance 等权后长 distance 的高方差被放大；
- variable-length episode/task 会改变 effective \(\beta_d\)；
- padding mask 错误会让零状态成为 target。

日志至少包含 per-distance numerator、valid count、mean、scale、gradient norm 与 task/episode分层。

## 19. 偏差五：计算和优化预算

从每个 time start 展开最多 \(D\) 步，朴素计算/内存近似随 \(T\times D\) 增长；实现可并行化，但仍增加 state rollout、KL 与 activation。若 matched arm 固定 wall-clock而不是 optimizer steps/tokens，overshooting arm可能看到更少数据；反之固定 steps又使用更多算力。

报告 wall-clock、samples/tokens、optimizer steps、peak memory 与 throughput，才能区分 objective effect 和 compute effect。

## 20. 偏差六：action、reset 与跨 episode 泄漏

multi-step loss会把一个 off-by-one 重复传播 \(d\) 次。必须验证：

- observation \(o_t\) 对应 previous action \(a_{t-1}\)；
- start 不在 padding/terminal 后；
- rollout 不跨 true terminal/reset；
- timeout/continuation 的语义与 mask 一致；
- heterogeneous task/action normalizer 没有跨 route 混用。

## 21. 泛称 multi-step consistency 的边界

“multi-step consistency”可能指：

- PlaNet latent overshooting 的 distribution KL；
- \(k\)-step latent regression/cosine loss；
- multi-step reward/observation likelihood；
- cycle consistency 或 teacher-student target；
- rollout distillation。

它们的 target、divergence direction、stop-gradient、stochastic expectation、mask 和 evidence不同。面试中先报 exact prediction/target/gradient，不能用一个术语代替实现。

## 22. 最小可审计伪代码

```python
def latent_overshooting(sequence, model, max_distance, beta):
    # 1. Filter the real sequence once; these learned posteriors are targets/starts.
    posterior = model.observe(sequence.obs, sequence.previous_action,
                              sequence.is_first)

    losses, counts = [], []
    for distance in range(1, max_distance + 1):
        # 2. Start earlier and roll only the prior along aligned recorded actions.
        prior_d = model.roll_prior(
            posterior.start(distance),
            sequence.action_slice(distance),
            use_observation=False)

        # 3. Never cross padding/reset/terminal; stop target gradients for d > 1.
        target = stop_gradient(posterior.target(distance))
        mask = sequence.valid_pair_mask(distance, stop_at_terminal=True)
        losses.append(beta[distance] * masked_kl(target, prior_d, mask))
        counts.append(mask.sum())

    # 4. Return per-distance traces; one reduced scalar hides effective weighting.
    return reduce_with_declared_denominator(losses, counts), audit(losses, counts)
```

这是 S1–S7 的审计骨架；PlaNet code还对 stochastic intermediate state取样/期望并有具体 reshape/crop/free-nats语义。

## 23. Matched ablation

固定 data/split、architecture/capacity、optimizer、steps/tokens、seed、one-step objective、action/reset contract 与 eval：

| arm | 目的 |
| --- | --- |
| one-step only | 基准 sequential ELBO |
| +OS D=3/5/10 | distance sensitivity |
| β distance decay/equal | effective weighting |
| stop-target on/off diagnostic | target movement风险 |
| observation overshooting | latent vs decoded multi-step supervision |
| multi-step reward | task signal而非纯latent consistency |
| shuffled/zero action | action dependence反例 |
| capacity-matched wider model | objective收益 vs capacity |

同时报告 per-distance raw/clipped KL、entropy/usage、one-step与open-loop state/reward/continue error、action sensitivity、planning/closed-loop success、compute 与 seed CI。

## 24. Failure-first 诊断

| 症状 | 首查 |
| --- | --- |
| OS loss降、open-loop不变 | target/metric尺度、short-distance主导、posterior shortcut |
| latent KL好、reward/contact差 | task信息被压掉、restricted family、head mismatch |
| long distance震荡 | sample variance、gradient horizon、D/β过大、action/reset错位 |
| d越大valid count骤减 | episode长度、terminal/padding mask、denominator |
| posterior也一起退化 | stop-gradient配置、effective scale、free-nats |
| action swap结果相同 | action未进入transition、数据action覆盖、shortcut |
| train更慢但score不变 | compute/data exposure未matched |
| closed-loop差 | 转WM-018/020/021检查horizon、model bias、controller/value |

## 25. 项目真实性边界

WAM/Cosmos 与 UWM 当前都是 diffusion-based action/future/video contracts，不是 PlaNet latent overshooting implementation。项目材料没有 per-distance latent KL、overshooting config、posterior/prior trace、D/β sweep 或 matched closed-loop result。

安全口径：

> 我能解释 latent overshooting 如何从每个 posterior start 做 prior-only多步对齐，也会先核对PlaNet final/default并未启用；当前WAM/UWM不是该实现，我只会把它作为可选诊断/消融设计，不声称项目使用或受益。

## 26. Claim ledger

| Claim | 来源 | 等级 | 状态 |
| --- | --- | --- | --- |
| 标准 objective 只直接训练一步 stochastic transition | S1 | primary | checked |
| latent overshooting 对齐多距离 prior 与未来 posterior | S1/S3 | primary + official code | checked |
| d>1 实践中 stop posterior gradient | S1/S3/S4 | primary + config | checked |
| official default PlaNet RSSM未启用overshooting | S1/S2/S4 | paper + official code | checked |
| DreamerV3 frozen repo使用PlaNet overshooting | S5/S6 | missing / blocked strong claim | rejected |
| WAM/UWM使用或受益于latent overshooting | S7 | missing local evidence | rejected |

## 27. 仍待独立复核与补证据

1. primary/official-code事实已复核，本节点独立事实复核仍标 `PENDING`。
2. 需要 local per-distance target/prior/mask trace、raw/clipped KL、valid counts、gradient和compute账本。
3. 需要 D/β/stop-gradient/observation-vs-latent matched arms与多seed结果。
4. 需要 action intervention、reward/contact/continue horizon curve和same-protocol closed-loop验证。
5. 浏览器 `file://` visual QA受策略阻断，只能做renderer/static/link validation。
6. 没有真实口述，不创建 `coaching_state.md`，题卡保持 `unseen`。

## 28. 参考来源

1. Hafner et al., [*Learning Latent Dynamics for Planning from Pixels*](https://arxiv.org/abs/1811.04551), ICML 2019。
2. `google-research/planet@c04226b6db136f5269625378cd6a0aa875a92842`: [README](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/README.md), [`overshooting.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/tools/overshooting.py), [`utility.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/training/utility.py), [`configs.py`](https://github.com/google-research/planet/blob/c04226b6db136f5269625378cd6a0aa875a92842/planet/scripts/configs.py), Apache-2.0。
3. [VOL 04 Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html)。
4. [WM-012 RSSM/Dreamer](vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)、[WM-018 Prediction Horizon](vol_04_wm018_prediction_horizon_source_freeze.html)、[WM-020 Failure Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html)。
5. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) evidence inventories。

## 29. 下一节点

完成本节点后，VOL 04 进入 43/44；下一 bounded slice 只做 `VLA-WM-014`（action-conditioned prediction 怎样区分相关性预测与可干预 dynamics）。
