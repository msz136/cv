# VOL 04 WM-029 Source Freeze：Imagined/OOD Value Calibration 与 Pessimism

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-029 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-029  
> 本轮边界：冻结 imagined/OOD value 失准机制、calibration 诊断、PETS/MOPO/CQL/LCB 的适用边界和 frozen Cosmos scorer 行为；不声称任一理论保证直接适用于 Cosmos value frame，也不声称用户 WAM 已实现 calibration/pessimism 或 planning。

## 1. 结论先行

1. **Value 在 imagined state 上失准的首因是 support shift。**训练 label 来自 replay/demo/rollout 分布，planning 却查询 learned world model 与候选 action 产生的 \(d_{\hat T}^{\pi}\)；state、action、horizon 任一离开支持集，value 都会外推。[S3][S4]
2. **World-model error 与 value error 会串联。**future state 先被模型偏差推离真实动力学，再由 value 对 OOD latent 打分；best-of-N 还会主动挑中估计误差最大的候选，形成 optimizer's curse。[S3][S5]
3. **Calibration、uncertainty、ranking 不是一回事。**calibration 问“0.8 是否在同条件下约 80% 成功”，uncertainty 问“我们有多不确定”，ranking 问“候选顺序是否正确”。低 MAE、低 ECE 或高 rank 任一个都不能替代另两个。[S1]
4. **Pessimism 有不同层级。**score-level LCB 用 \(\mu-\beta\sigma\)，MOPO 对 imagined reward 加 model-uncertainty penalty，CQL 在 offline Q objective 中压低数据外 action 的 Q；三者不能互换，更不能无改造套到生成式 value frame。[S3][S4]
5. **Frozen Cosmos LCB 是 heuristic。**同一模型以不同 seed/denoising steps 采多次 value，先映射并 clip 到 \([0,1]\)，再用 fixed \(\beta=1\) 的 mean-minus-std；它不是独立模型 ensemble，也没有覆盖/下界保证。LIBERO/RoboCasa 默认关闭 ensemble 且 aggregation 为 average。[S5]
6. **WAM 本地仍没有 calibration 证据。**缺 exact checkpoint、value label/return manifest、pre/post-clip predictions、candidate/episode ledger、N/β/horizon sweep 和 ownership，不能说 value 已校准或 pessimism 已改善 planning。[S7]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Guo et al., *On Calibration of Modern Neural Networks* | arXiv:1706.04599v2；PDF SHA-256 `cb654a65acb785ed4387d6c2db1301d065075dddc2d363676836a2f2a14bc50d` | reliability diagram、ECE、temperature scaling、calibration 与 accuracy 区分 | arbitrary return scalar 可直接 temperature-scale；OOD calibration 自动成立 | primary / checked |
| S2 | Chua et al., PETS | arXiv:1805.12114v2；PDF SHA-256 `7dbf3c65ece763384258a60f5f4b26d7b849ad80765ed77435c4861f9583219c` | probabilistic ensemble、aleatoric/epistemic 区分、trajectory sampling uncertainty propagation | arbitrary ensemble std 是 calibrated confidence bound | primary / checked |
| S3 | Yu et al., MOPO | arXiv:2005.13239v6；PDF SHA-256 `c9566a8e3d2e5b576cb65cc2ae1684761f5dc0c88017cd646bf74e5b51c0f4f4` | model-based offline distribution shift、uncertainty-penalized reward、lower-bound theorem assumptions、heuristic estimator limitation | MOPO guarantee 直接适用于 Cosmos/WAM；heuristic variance 有保证 | primary / checked |
| S4 | Kumar et al., CQL | arXiv:2006.04779v3；PDF SHA-256 `2bae51a0b45635ab714df39446cd656a9f4f1c503f512d6d0ce1eec3198d1716` | offline Q overestimation、conservative regularizer、policy-value lower-bound conditions | 生成式 value frame 已使用 CQL；pointwise universal lower bound | primary / checked |
| S5 | Cosmos Policy paper + official code | paper arXiv:2601.16163v1；repo commit `18a2accadf4e7a3531e56754102af5a24d2316da` | value frame extraction/clip、best-of-N、same-model sampling ensemble、average/LCB/vote/majority aggregation、defaults | LCB 是 calibrated epistemic bound；用户本地 planning result | primary + official-code / WARN |
| S6 | WM-021/024/028 | 本地 canonical + review | imagination model bias、value/return/success 语义、value role/mask/valid contract | 上述机制是本地失败根因 | supporting / WARN |
| S7 | WAM Claim–Evidence Inventory | 2026-07-18 | local diagnostic 边界和 checkpoint/value/candidate/episode/ownership 缺口 | local value calibration、planning uplift 或 pessimism 已验证 | local-evidence / WARN |

### 2.1 Frozen Cosmos scorer 文件

| 文件 | 作用 | SHA-256 |
| --- | --- | --- |
| `cosmos_policy/experiments/robot/cosmos_utils.py` | value sampling、clip、ensemble aggregation、LCB | `ebe56d63d88f9a4d4ad6706d9a9ecd1376a1dff1b5cbb010c8fcd8f0c2ee0b1d` |
| `cosmos_policy/experiments/robot/libero/run_libero_eval.py` | LIBERO planning defaults | `2c00207579749d935102276081858a790ad413a7a64c5b838cb8f4d5d508c9a7` |
| `cosmos_policy/experiments/robot/robocasa/run_robocasa_eval.py` | RoboCasa planning defaults | `8e92cddfc72a23b95abe8c2b99fce93a1c382cf46ea0e97d87a8805c06360f4b` |

## 3. 为什么 imagined/OOD value 容易失准

### 3.1 Occupancy / support shift

训练与规划查询分布通常不同：

\[
(s,a)\sim d_{\mathcal D}(s,a)
\quad\text{vs.}\quad
(\hat s,a)\sim d_{\hat T}^{\pi}(s,a).
\]

变量解释：\(d_{\mathcal D}\) 是数据集 occupancy，\(d_{\hat T}^{\pi}\) 是 policy 在 learned dynamics \(\hat T\) 中产生的 imagined occupancy。CQL/MOPO 分别从 OOD action value 与 learned-model state/action shift 处理这一问题；两者都依赖自己的算法合同。[S3][S4]

### 3.2 World-model error 传给 value

若真实 future 为 \(s'\)，world model 给出 \(\hat s'=s'+\delta_T\)，value query 误差可分解为：

\[
\hat V(\hat s')-V(s')=
\underbrace{\hat V(\hat s')-V(\hat s')}_{\text{value extrapolation}}
+\underbrace{V(\hat s')-V(s')}_{\text{transition/model shift}}.
\]

变量解释：第一项是 value 在 queried latent 上的估计误差，第二项是 world model 把状态推错后造成的真实 value 变化。即使 value 对真实 replay state 准，第二项仍可让 imagined ranking 失败。

### 3.3 Bootstrapping / horizon amplification

对 Bellman-style value：

\[
\hat Q(s,a)=\hat r(s,a)+\gamma
E_{\hat T}[\hat V(s')].
\]

变量解释：reward、transition、next-value 误差会沿 horizon 递推；\(\gamma\) 接近 1、rollout 深、terminal/timeout label 错时更危险。Cosmos 的 Monte-Carlo return value frame 不等于经典 bootstrapped Q，但 imagined future shift 与 long-horizon label/calibration 问题仍存在，不能混成同一公式。

### 3.4 Best-of-N optimizer's curse

令候选估计为

\[
\hat V_i=V_i+\epsilon_i,
\qquad i^*=\arg\max_{i\le N}\hat V_i.
\]

变量解释：selector 同时最大化真实 value 与估计噪声；当 error 与 OOD/模型幻觉相关时，\(N\) 越大越可能选到过估计候选。低 global value MSE 不能保证 top-tail ranking 或 selected-candidate regret。

## 4. Calibration 该校准什么

### 4.1 Success probability

只有当 scorer 明确定义为成功概率 \(p_i=P(Y_i=1\mid x_i)\) 时，reliability/ECE 才有直接语义：

\[
\operatorname{ECE}=
\sum_{m=1}^{M}\frac{|B_m|}{n}
\left|\operatorname{acc}(B_m)-\operatorname{conf}(B_m)\right|.
\]

变量解释：\(B_m\) 是 confidence bin。Guo et al. 同时强调 reliability diagram 与 ECE 是有限样本近似，scalar summary 不全面；应报告 bin count、task/support/horizon 分层。Temperature scaling 适用于 classification logits 的 post-hoc calibration，不应直接套到任意 clipped return scalar。[S1]

还应报告 Brier/NLL、阈值下 precision/recall 和 selected-candidate success。Calibration 好不代表 discrimination/ranking 好。

### 4.2 Return/value regression

若 target 是 discounted return 而非成功概率，重点是：

- MAE/RMSE 与 bias，按 task、return bucket、support、rollout depth 分层；
- Spearman/Kendall 或 pairwise ranking accuracy；
- prediction interval coverage/width，明确 interval 如何构造；
- top-N selected regret：selected candidate 的真实 return 与 oracle best 的差；
- pre-clip 与 post-clip saturation，检查 0/1 mass 是否掩盖误差。

不能把“value 在 \([0,1]\)”自动解释为 calibrated success probability；WM-024 已冻结 value/return/success 的语义边界。[S6]

### 4.3 OOD-specific calibration

全局 holdout 可被 in-support 样本主导。至少按以下 bucket 报告：

1. behavior/replay vs policy proposal；
2. real next state vs imagined state；
3. rollout depth / model disagreement；
4. action distance / task / embodiment；
5. selected top tail vs random/median candidate。

真正的 imagined OOD label 需要 real/simulator execution 或 trusted counterfactual；只有 self-consistency/Bellman residual 不足以证明 calibration。

## 5. Uncertainty 与 calibration 的边界

PETS 使用 bootstrapped probabilistic dynamics ensemble 区分 epistemic 与 aleatoric uncertainty，并通过 trajectory sampling 传播。[S2] 但一般情况下：

- ensemble disagreement 是 uncertainty proxy，不自动是 error probability；
- 同一模型不同 seed/dropout/denoising path 的 dispersion 不等于独立 model epistemic uncertainty；
- low disagreement 可能是 ensemble 共错；high disagreement 也可能来自 benign multimodality；
- \(\sigma\) 必须在 held-out/OOD strata 上验证 error correlation、coverage 或 selective risk。

## 6. 四类 pessimism

### 6.1 Score-level LCB

\[
V_{LCB}(x)=\mu(x)-\beta\sigma(x).
\]

变量解释：\(\mu,\sigma\) 来自重复预测/ensemble，\(\beta\) 控制保守程度。没有 calibrated coverage 与独立误差模型时，它只是 risk score，不是数学置信下界。应 sweep \(\beta\)、N、rollout depth，并报告 coverage-risk/return trade-off。

### 6.2 MOPO：model uncertainty reward penalty

\[
\tilde r(s,a)=\hat r(s,a)-\lambda u(s,a).
\]

变量解释：MOPO 理论要求 \(u\) 是 admissible dynamics-error estimator；实践用 ensemble predicted variance 的 heuristic penalty，并明确该 estimator 本身缺少理论保证。[S3] 它惩罚 learned-model rollouts，不是简单把 value frame 减一个 std。

### 6.3 CQL：offline Q conservatism

简化的 CQL(H) 目标：

\[
\min_Q\;\alpha E_{s\sim\mathcal D}
\left[\log\sum_a e^{Q(s,a)}
-E_{a\sim\hat\pi_\beta}[Q(s,a)]\right]
+\frac12 E_{(s,a,s')\sim\mathcal D}
\left[(Q-\hat{\mathcal B}^{\pi}Q)^2\right].
\]

变量解释：第一项压低广泛 action 的 Q、相对抬高数据 action；第二项是 Bellman error。CQL 的 lower-bound 结论有 policy update、sampling 等条件，并非对每个 point 的任意 Q 保证。[S4] Cosmos 生成式 value frame没有这套 Q objective，除非重构训练合同。

### 6.4 Support constraint / fallback

不一定修改 value：可限制 proposal 接近 behavior support、缩短 imagined horizon、降低 N、拒绝高-uncertainty 候选、退回 direct policy 或 replanning/recovery。对真实机器人，这些常比声称“校准好了”更可审计。

## 7. Frozen Cosmos exact boundary

1. value latent 均值先映射 \((z+1)/2\) 并 clip 到 \([0,1]\)。clip 会造成 saturation；**由代码推断**，post-clip std 可能低估越界预测差异，应保存 pre-clip 与 post-clip 值配对验证。[S5]
2. optional “ensemble” 在同一模型、同一 future latent 上改变 seed 与 denoising steps，默认 5 次；不是 bootstrap model ensemble。
3. `lcb` 计算 post-clip predictions 的 mean - 1.0×std；\(\beta\) hard-coded 为 1.0。
4. LIBERO/RoboCasa 默认 `use_ensemble_value_predictions=False`，aggregation config 是 `average`；因此 LCB 支持不等于默认启用。
5. `success_vote`/`majority_mean` 使用 0.05 threshold；该阈值不是经本轮核验的 calibrated success probability threshold。
6. ALOHA deploy recipe 使用 majority-mean 与 N=8；不能外推到 LIBERO/RoboCasa 或用户 WAM。

## 8. 诊断与 matched 评估

| 层 | 指标/实验 | 能回答 | 不能回答 |
| --- | --- | --- | --- |
| label | return/success/timeout manifest | target 是否正确 | OOD 是否准 |
| in-support | MAE、bias、reliability、rank | replay holdout 拟合 | imagined top-tail |
| model shift | real-vs-imagined paired future | world bias 贡献 | closed-loop selection |
| uncertainty | disagreement-error correlation、coverage-risk | proxy 是否有用 | 下界保证 |
| selector | random/mean/LCB/oracle、N/β/depth sweep | optimizer's curse/pessimism trade-off | 项目因果收益，除非 protocol matched |
| closed loop | per-task success、paired episode、first-failure | 固定协议系统结果 | value 独立贡献，除非消融 |

最小 arms：direct/no planning、random selector、mean value、LCB、多种 β、oracle recorded-return selector（仅离线诊断），并固定 proposals、world samples、checkpoint、N、seed 与 latency budget。

## 9. 可审计伪代码

```python
def audit_value_selector(candidates, value_sampler, execute_or_replay, beta):
    # 1. Keep candidate actions and imagined futures fixed across selectors.
    records = []
    for candidate in candidates:
        # 2. Save pre-clip and post-clip samples; dispersion is only a proxy.
        raw_samples = value_sampler(candidate, save_preclip=True)
        clipped = clip01(raw_samples)
        mean, std = clipped.mean(), clipped.std()
        score = mean - beta * std

        # 3. Obtain trusted outcome from simulator/real execution or replay label.
        outcome = execute_or_replay(candidate)
        records.append((candidate, raw_samples, mean, std, score, outcome))

    # 4. Report calibration/ranking/selected regret by support and rollout depth.
    return stratified_selector_report(records)
```

这是补证据 instrumentation，不是 WAM 已执行代码。真实 best-of-N 还要绑定 proposal/world/value checkpoint、future sample、N、latency、controller 和 episode key。

## 10. WAM 真实性边界

当前 WAM evidence 没有 value labels/predictions、pre/post-clip samples、candidate ledger、planning episodes 或 selector sweep。历史 action MSE、single future proxy 和 0-success 叙述不能证明 value miscalibration，也不能证明 LCB/CQL/MOPO 会修复。[S7]

安全说法：**“我会分开评估 in-support calibration、imagined shift、ranking 与 uncertainty-error correlation，再用 fixed candidates 做 mean/LCB/β/N/depth 和闭环对照。”**

不能说：**“我已经用 CQL/MOPO/LCB 校准了 WAM value 并提升 planning。”**

## 11. 下一入口

下一 bounded slice 是 `VLA-WM-030`：test-time planning 的 N、world rollout、value scoring、通信与 latency 如何计时和限险。它应复用本页 selector-risk 结论，不重复 calibration 公式。

## 参考文献（References）

1. Guo et al., [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599v2), ICML 2017。
2. Chua et al., [Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models](https://arxiv.org/abs/1805.12114v2), NeurIPS 2018。
3. Yu et al., [MOPO: Model-based Offline Policy Optimization](https://arxiv.org/abs/2005.13239v6), NeurIPS 2020。
4. Kumar et al., [Conservative Q-Learning for Offline Reinforcement Learning](https://arxiv.org/abs/2006.04779v3), NeurIPS 2020。
5. NVlabs, [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)，重点 [`aggregate_value_predictions`](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/cosmos_utils.py)。
6. [WM-024 Reward / Value / Success / Termination](vol_04_wm024_reward_value_success_termination_source_freeze.html)。
7. [WM-028 Routing / Mask / Weight](vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html)。
8. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。

