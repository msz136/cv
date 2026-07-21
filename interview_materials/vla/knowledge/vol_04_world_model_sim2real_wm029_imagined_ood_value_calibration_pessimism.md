# VOL 04 World Model / Sim2Real：Imagined/OOD Value Calibration 与 Pessimism（WM-029）

> 状态：drafted / VLA-WM-029 / knowledge_31_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释 value OOD failure、calibration/uncertainty/ranking 与 pessimism 选择，不宣称本地 WAM 已实施。  
> 前置：[WM-024 Value Semantics](vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)、[WM-028 Routing / Mask / Weight](vol_04_world_model_sim2real_wm028_routing_slot_mask_loss_weight.html)、[WM-029 Source Freeze](../sources/vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html)。

## 问题（Question）

value 在 imagined/OOD state 上为何容易失准，如何做 calibration 或 pessimism？回答必须区分 support shift、world bias、ranking、uncertainty、calibration 与不同 pessimistic interventions。

## 1. 面试结论

value 通常在 replay/demo/rollout label 上训练，planning 却查询 policy proposal 经 learned world model 生成的 future；state、action、horizon 离开数据支持后，world error 与 value extrapolation 叠加。best-of-N 又最大化估计值，容易选中高估误差。

先明确 value 是 return、Q 还是 success probability，再分别看 calibration、ranking 与 uncertainty-error correlation。Pessimism 可以在 scorer 做 LCB、在 model rollout 做 MOPO reward penalty、在 offline Q training 做 CQL，或直接约束 support/缩短 horizon/fallback；它们不是同一种方法。

## 2. 失准的四条链

### 2.1 Support shift

\[
(s,a)\sim d_{\mathcal D}
\quad\neq\quad
(\hat s,a)\sim d_{\hat T}^{\pi}.
\]

变量解释：左侧是训练数据 occupancy，右侧是 policy 在 learned dynamics 中的 imagined occupancy。Value 在右侧属于 extrapolation，offline MAE 低也不保证可靠。[1][2]

### 2.2 World error + value error

\[
\hat V(\hat s')-V(s')=
[\hat V(\hat s')-V(\hat s')]
+[V(\hat s')-V(s')].
\]

变量解释：第一项是 value extrapolation，第二项是 world transition 把 future state 推错；需要 real-vs-imagined paired future 才能拆分。

### 2.3 Horizon / bootstrap

\[
\hat Q(s,a)=\hat r(s,a)+\gamma E_{\hat T}[\hat V(s')].
\]

变量解释：Bellman-style Q 会递推 reward、transition 与 next-value error。Cosmos value frame 使用 rollout return，不等于经典 Q；但长 horizon、return/timeout label 与 imagined shift 仍需审计。

### 2.4 Optimizer's curse

\[
\hat V_i=V_i+\epsilon_i,
\qquad i^*=\arg\max_{i\le N}\hat V_i.
\]

变量解释：best-of-N 同时选择真实 value 与正向估计噪声；N 增大可能提升 proposal coverage，也可能放大 top-tail overestimate。必须做 N sweep 和 oracle/random/mean selector 对照。

## 3. Calibration、ranking、uncertainty 分开测

| 属性 | 核心问题 | 指标 | 常见误用 |
| --- | --- | --- | --- |
| calibration | 预测数值与经验频率/return 是否匹配？ | reliability、ECE、bias、coverage | 把低 MAE 当 calibrated |
| ranking | 候选顺序是否正确？ | pairwise/rank correlation、selected regret | calibrated 就一定会选对 |
| uncertainty | 高不确定是否对应高 error？ | disagreement-error、risk-coverage | std 就是置信区间 |
| accuracy | 平均预测误差多大？ | MAE/RMSE/NLL/Brier | 平均好就代表 top tail 好 |

## 4. Success probability calibration

若 value 明确定义为 success probability：

\[
\operatorname{ECE}=
\sum_{m=1}^{M}\frac{|B_m|}{n}
|\operatorname{acc}(B_m)-\operatorname{conf}(B_m)|.
\]

变量解释：\(B_m\) 是 confidence bin。应同时给 reliability diagram、bin count、Brier/NLL，并按 task/support/depth 分层。ECE 是 binning 近似与不全面的 scalar summary；temperature scaling 面向 classification logits，不能直接校准任意 clipped return。[3]

## 5. Return/value regression calibration

若 target 是 discounted return：

- 报 MAE/RMSE/bias，但另报 rank 与 selected regret；
- 按 in-support/imagined、rollout depth、task、return bucket 分层；
- 若输出 interval，报告 coverage 与 width，并冻结构造方法；
- 保存 pre-clip/post-clip，检查 0/1 saturation；
- 用 fixed candidate 的 trusted simulator/real outcome 做 top-tail calibration。

Value 处于 \([0,1]\) 不代表它是 calibrated success probability；先回到 WM-024 的 label contract。

## 6. Uncertainty proxy 怎样验

PETS 的 bootstrapped probabilistic dynamics ensemble可以分开 epistemic/aleatoric，并用 particles 传播 uncertainty。[4] 实际项目里应检查：

1. disagreement 与 absolute error 是否单调相关；
2. risk-coverage：拒绝最高 uncertainty 后错误/成功如何变；
3. in-support 与 OOD bucket 的 coverage；
4. ensemble 成员是否真正独立，还是同模型 seed/dropout/sample；
5. 低 disagreement 是否出现共错。

没有这些验证，\(\sigma\) 只是 heuristic score。

## 7. Pessimism 方法对比

### 7.1 LCB scorer

\[
V_{LCB}=\mu-\beta\sigma.
\]

变量解释：适合不改训练、只改 candidate selector；\(\beta\) 需在 held-out/paired episodes 上 sweep。若 \(\sigma\) 未校准，LCB 不是置信下界。

### 7.2 MOPO reward penalty

\[
\tilde r(s,a)=\hat r(s,a)-\lambda u(s,a).
\]

变量解释：在 learned-model MDP 内惩罚 uncertain transition；理论下界要求 admissible error estimator。MOPO 实践 variance estimator 自身被论文标为 heuristic。[1]

### 7.3 CQL Q regularization

\[
\mathcal L_{CQL}=\alpha E_s
\left[\log\sum_a e^{Q(s,a)}-E_{a\sim\mathcal D}Q(s,a)\right]
+\mathcal L_{Bellman}.
\]

变量解释：压低广泛/OOD action Q、相对数据 action 更保守；lower-bound 有算法条件，不是任意 pointwise 保证。生成式 value frame 没有这套 Q objective。[2]

### 7.4 Support/fallback

限制 action 距 behavior、缩短 model horizon、降低 N、拒绝 high-risk candidate、退回 direct policy、replan/recovery。它们往往比“假设 score 已校准”更安全。

## 8. Frozen Cosmos exact boundary

| 行为 | Frozen code | 面试边界 |
| --- | --- | --- |
| value transform | latent mean → \((z+1)/2\) → clip [0,1] | bounded 不等于 calibrated probability |
| ensemble | 同一模型，不同 seed 与 denoising steps | sample dispersion，不是 independent-model epistemic |
| LCB | post-clip mean - 1×std | fixed heuristic，非覆盖保证 |
| defaults | ensemble off，aggregation average | 支持 LCB 不等于默认使用 |
| vote threshold | 0.05 | 未核验为 calibrated threshold |
| ALOHA recipe | majority-mean、N=8 | 不外推 LIBERO/RoboCasa/WAM |

由代码推断：先 clip 再算 std 可能在 0/1 saturation 降低 observed dispersion。应配对保存 pre/post-clip predictions 验证，不能直接宣称该推断已造成失败。[5]

## 9. 评估矩阵

1. label audit：return、gamma、horizon、terminal/timeout、success predicate。
2. in-support：MAE/bias/reliability/rank。
3. imagined shift：real-vs-imagined future/value paired error，按 depth。
4. uncertainty：disagreement-error、coverage-risk、共错率。
5. selector：same candidates 下 random/mean/LCB/β sweep/oracle replay。
6. planning：N、world samples、depth、latency 与 closed-loop success。
7. failure：selected candidate 的 perception/world/value/controller first divergence。

## 10. 可审计伪代码

```python
def compare_value_selectors(fixed_candidates, sampler, trusted_outcome, betas):
    # 1. Reuse identical action/future candidates for every selector.
    ledger = []
    for candidate in fixed_candidates:
        # 2. Preserve raw and clipped samples; std is only a proxy.
        raw = sampler(candidate, save_preclip=True)
        clipped = clip01(raw)
        outcome = trusted_outcome(candidate)
        ledger.append({"candidate": candidate, "raw": raw, "clipped": clipped, "outcome": outcome})

    # 3. Sweep beta and report stratified calibration, ranking and regret.
    return evaluate_mean_lcb_oracle(ledger, betas, by=["task", "support", "depth"])
```

这不是 WAM 已执行代码；真实运行必须绑定 proposal/world/value checkpoint、candidate、future、seed、N、latency 和 episode key。

## 11. WAM 项目真实性

WAM inventory 没有 value prediction/label bundle、candidate ledger、pre/post-clip samples、selector sweep 或 planning episodes。单 episode action trace、future proxy 和历史 MSE 不能证明 value calibration/pessimism。

安全说法：“我会先分层校准与 ranking，再验证 uncertainty-error correlation，最后对 fixed candidates 做 mean/LCB/β/N/depth 的闭环对照。”不能说“已用 CQL/MOPO/LCB 提升 WAM planning”。

## 12. 结论与下一入口

imagined value 失准来自 support shift、world bias、value extrapolation、horizon 与 selector bias。Calibration、ranking、uncertainty 和 pessimism 必须分层；任何 LCB 只有在 uncertainty proxy 被验证后才有工程意义。

下一节点 `VLA-WM-030` 进入 test-time planning 的 N、world rollout、value scoring、通信和 latency budget。题卡保持 unseen；真实口述前不创建 coaching state。

## 参考文献（References）

1. [WM-029 Source Freeze](../sources/vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html)。
2. [WM-024 Value Semantics](vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)。
3. Guo et al., [Calibration](https://arxiv.org/abs/1706.04599v2)。
4. Chua et al., [PETS](https://arxiv.org/abs/1805.12114v2)。
5. [Cosmos Policy / WAM Audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
6. Yu et al., [MOPO](https://arxiv.org/abs/2005.13239v6)。
7. Kumar et al., [CQL](https://arxiv.org/abs/2006.04779v3)。
8. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。

