# VOL 04 WM-011 Source Freeze：World-model Objective Semantics

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-011 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-011  
> 本轮边界：只冻结 reconstruction、latent dynamics、reward、continuation 与 perceptual objective 的监督对象、实现合同、失效模式和 matched audit；不把 loss 下降写成控制收益，也不把公开 Dreamer/PlaNet 机制写成本地 WAM/UWM 成果。

## 1. 冻结结论

1. 一个 loss 的名字不能定义它；必须说明 prediction、target、时间索引、mask、reduction、scale 和 gradient path。
2. reconstruction 约束 decoder 从 latent 恢复 observation；latent dynamics 约束 action-conditioned prior 与 observation posterior 对齐，二者监督对象不同。
3. reward head 预测一步即时 reward；continuation head 预测 episode 是否继续或折扣因子。它们不等于 value、success classifier 或 task completion。
4. perceptual loss 比较冻结或明确更新的 feature-space representation；它可能更符合感知相似度，也可能忽略接触、位姿、深度等 action-critical 细节。
5. DreamerV3 frozen repo 将 dyn/rep KL、reward、continuation 和各 observation reconstruction 分开计算，再按 `loss_scales` 聚合；raw scalar 大小在不同 reduction 下不可直接比较。
6. `loss ↓` 只说明训练目标在当前样本/聚合下下降；要说“对 policy 有帮助”，必须做 matched objective ablation、gradient/representation diagnostics 与 closed-loop evaluation。

## 2. 一手来源与冻结快照

| ID | 来源 | 冻结版本与响应 SHA-256 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Ha & Schmidhuber, *World Models* | arXiv `1803.10122`；ar5iv response `94b1cfb329e803b6b305f574755a83478f051f268c693e445ea3a959680683aa` | VAE reconstruction、MDN-RNN latent prediction、controller 分工 | 现代 RSSM exact loss、机器人 objective uplift |
| S2 | Hafner et al., *PlaNet* | arXiv `1811.04551`；ar5iv response `6a9bed11e5963626016235227ab85594ae5d42773e675860788c51a071929a97` | latent dynamics、observation/reward likelihood、multi-step latent consistency | PlaNet overshooting 是 DreamerV3 实现机制 |
| S3 | Hafner et al., *DreamerV3* | arXiv `2301.04104`；arXiv HTML response `7ce561853df3b35ccf0316476b3f7538b60117feb358bd562dc279f0d5067a26` | prediction/dynamics/representation loss、reward/continue/decoder heads、free bits | frozen reimplementation 的所有默认值或本地项目结果 |
| S4 | Johnson et al., *Perceptual Losses for Real-Time Style Transfer and Super-Resolution* | arXiv `1603.08155`；ar5iv response `5c4923e8ce75ded7f37b317541c0297e4d7acd1df685fcd9a21012260ffddc38` | frozen loss network 的 feature reconstruction 目标 | 任意视觉 backbone 都适合机器人接触/几何 |
| S5 | Zhang et al., *The Unreasonable Effectiveness of Deep Features as a Perceptual Metric* | arXiv `1801.03924`；ar5iv response `fb10022b5757b81d033dfe21a676b2acf5c6d4e7c46dab3b10a801905f1d7ac2` | deep-feature perceptual distance、layer normalization/calibration | LPIPS 分数等于 dynamics/actionability |
| S6 | `danijar/dreamerv3` frozen code | commit `e3f02248693a79dc8b0ebd62c93683888ddaccfe`；`rssm.py` `d6d50166914e94fb8bd17a5d5dbda9d42cdd37b85819bb1e9fff3a64d4ad2eb6`；`agent.py` `adce8e4274bc098c218bf9a20fd3327545f0ad7d850b5fe328597382e91b5269`；`configs.yaml` `9dff9c7062e3e33951cb54c6dd4b598aaf7e56e18e2cff39c812eaa797bcfcfc`；README `a4d8e77c07a876a7f528aa204fbc910812c5ca96bcfb67709b366f8ff0d3ed6b` | `observe/imagine/loss`、target/mask/reduction/scale 的具体实现映射 | 论文作者官方代码、checkpoint reproduction、个人贡献 |
| S7 | [Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html) | canonical SHA `bb48af7605688132ddd589109c8417dd0ebfe65f504a98cf5ab660f01e34ba7b` / `da16c172179cae926d329259e76955a55555fe53a15233f265d1f74a3d421ae4` | 允许 WM-011..014 逐节点生成；repo provenance 与 overshooting 边界 | 本地 objective ablation |
| S8 | [WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories | canonical SHA `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d` / `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 项目可讲的训练/协议边界与缺失 artifact | reconstruction/perceptual/dynamics 对 success 的个人因果收益 |

**Provenance warning：**S6 的 README 明确称其为 DreamerV3 reimplementation，并与 Google/DeepMind 无关。本页只能说“该 frozen reimplementation 的代码路径”，不能说“论文作者官方实现”。

## 3. 先写 objective contract

每一项至少写成：

`prediction + target + time index + valid mask + reduction denominator + scale + gradient recipients`。

例如“用了 reconstruction loss”仍缺少：重建哪路 camera/proprio、像素是 `[0,255]` 还是 `[0,1]`、是 MSE 还是 likelihood、padding/缺帧如何 mask、对时间/像素怎样平均、decoder loss 是否回传 encoder/dynamics。没有这些字段，loss 名称不能复现实验。

## 4. 总目标只是容器

一个最小 world-model objective 可抽象为：

\[
\mathcal L_{\mathrm{wm}}
=\lambda_{\mathrm{rec}}\mathcal L_{\mathrm{rec}}
+\lambda_{\mathrm{dyn}}\mathcal L_{\mathrm{dyn}}
+\lambda_{\mathrm{rep}}\mathcal L_{\mathrm{rep}}
+\lambda_r\mathcal L_r
+\lambda_c\mathcal L_c
+\lambda_p\mathcal L_{\mathrm{perc}}.
\]

变量解释：每个 \(\mathcal L\) 是一类监督信号，\(\lambda\) 是有效权重；具体系统可以没有某一项，也可把 observation 分成多个 key。直觉是把“看得见、推得动、知道回报、知道何时结束”拆成不同约束。实现映射：必须保存各项 unreduced/valid-count/reduced/scaled loss、梯度范数和总 loss；不能只保存一个总标量。

## 5. Reconstruction 监督什么

对 observation key \(k\)，可写负对数似然：

\[
\mathcal L_{\mathrm{rec}}^{(k)}
=-\frac{1}{N_k}\sum_{t,i}m_{t,i}^{(k)}
\log p_\theta\!\left(o_{t,i}^{(k)}\mid h_t,z_t\right),
\qquad
N_k=\sum_{t,i}m_{t,i}^{(k)}.
\]

变量解释：\(o^{(k)}\) 是某个 camera/proprio observation，\((h_t,z_t)\) 是 latent feature，\(m\) 是有效元素 mask，\(N_k\) 是有效 denominator。直觉是让 latent 保留 decoder 能恢复的 observation 信息。实现映射：固定 camera key、resize/crop、dtype/range、likelihood/MSE、mask 与 per-key reduction。

S6 的 `Agent.loss` 对 image target 做 `/255`，对每个 decoder output key 调用 `recon.loss(stop_gradient(target))`；`rec` scale 会复制到各 decoder space。这里 stop-gradient 作用于 target，不表示 decoder/representation 都停止更新。

## 6. Reconstruction 的典型误读

- pixel MSE/NLL 低，可能只说明背景、光照和低频纹理重建好；小物体位姿、接触点和遮挡状态仍可能错。
- posterior decoder 可借助当前 observation 编码后的 latent 重建，却不证明 action-conditioned prior 能 open-loop rollout。
- 多 camera 直接求和会让高分辨率/高 valid-count 的 key 主导；先按 key 平均或全局按元素平均是不同 objective。
- padding、missing camera、episode boundary 若未 mask，会把无效帧当成监督。

## 7. Latent dynamics 监督什么

Dreamer 风格 RSSM 区分 observation posterior 与 action-conditioned prior：

\[
q_\phi(z_t\mid h_t,o_t),
\qquad
p_\theta(z_t\mid h_t),
\qquad
h_t=f_\theta(h_{t-1},z_{t-1},a_{t-1}).
\]

变量解释：posterior \(q\) 读取当前 observation，prior \(p\) 只能依赖历史 latent/action；\(h_t\) 是 deterministic memory。直觉是 posterior 用真实观测校正 belief，prior 学会在没有未来 observation 时预测。实现映射：S6 中分别对应 `RSSM.observe` 与 `RSSM.imagine`。

## 8. Dynamics / representation KL 的梯度边界

S6 的 frozen `RSSM.loss` 计算：

\[
\mathcal L_{\mathrm{dyn}}
=D_{\mathrm{KL}}\!\left[\operatorname{sg}(q_\phi)\,\|\,p_\theta\right],
\qquad
\mathcal L_{\mathrm{rep}}
=D_{\mathrm{KL}}\!\left[q_\phi\,\|\,\operatorname{sg}(p_\theta)\right].
\]

变量解释：`sg` 是 stop-gradient。dyn 主要训练 prior 追 posterior；rep 主要约束 posterior 靠近 prior，防止 encoder 任意编码当前 observation。直觉是双向“对齐目标”相同但梯度接受者不同。实现映射：分别保存 dyn/rep loss、prior/posterior entropy、KL histogram 和 encoder/dynamics gradient norm。

该实现用 `free_nats=1.0` 对两项逐元素下限截断。free nats 给小 KL 一个不继续压缩的区间，不是把 KL 从总目标删除，也不保证避免 collapse。

## 9. Latent dynamics 的失效模式

- **posterior collapse**：posterior 几乎不使用 observation，latent 无信息；看 KL、entropy、decoder quality、latent intervention。
- **action ignoring**：prior 主要靠惯性/背景预测，换 action 结果不变；做 action-swap、zero/random action、finite-difference sensitivity。
- **one-step only**：单步 prior 对齐但 rollout 漂移；分 teacher-forced 与 open-loop horizon curve。
- **跨方法误归因**：PlaNet latent overshooting 是 S2 的机制，当前证据不能把它写成 S6 DreamerV3 repo 的实现事实。

## 10. Reward 监督什么

\[
\mathcal L_r
=-\frac{1}{N_r}\sum_t m_t^r
\log p_\theta(r_t\mid h_t,z_t).
\]

变量解释：\(r_t\) 是数据合同中的一步即时 reward，\(m_t^r\) 是有效 mask。直觉是让 imagined state 能给 planner/actor 提供一步任务信号。实现映射：S6 `Agent.loss` 用 `self.rew(...).loss(obs['reward'])`；要固定 reward shaping、scale/symlog、sparse/dense、时间索引和 terminal transition。

reward 不是 value：value 依赖 policy、discount 与未来 return；reward 也不是 success classifier，后者可能只在 episode 末按任务 predicate 标记。一个 reward head 拟合好不能证明 cumulative return 或 binary success 正确。

## 11. Continuation 监督什么

令 continuation target \(c_t\in\{0,1\}\) 表示 episode 是否在该 transition 后继续：

\[
\mathcal L_c
=-\frac{1}{N_c}\sum_t m_t^c
\left[c_t\log \hat c_t+(1-c_t)\log(1-\hat c_t)\right].
\]

变量解释：\(\hat c_t\) 是 predicted continuation probability，\(m_t^c\) 是有效 mask。直觉是控制 imagined return 何时停止 bootstrap。实现映射：S6 用 `con = ~obs['is_terminal']`；启用 `contdisc` 时还乘 `(1 - 1/horizon)`，因此其 target 更接近 learned discount，而不是纯 done classifier。

## 12. Continuation 的时间索引与 timeout 陷阱

- 必须说明 `is_terminal[t]` 指 transition \(t-1\to t\) 还是 \(t\to t+1\)；错一位会让终止前后都学错。
- time-limit truncation 与 true terminal 不应自动等价：前者常允许 value bootstrap，后者通常不允许。
- padding、reset frame、absorbing state 和 dataset `is_last/is_terminal` 字段必须分别处理。
- continuation 与 success 可同时为 0/1 的组合取决于任务：失败终止、成功终止、超时截断语义不同。

## 13. Perceptual loss 监督什么

给定预训练 feature extractor \(\phi_l\)，一个 feature reconstruction objective 可写为：[S4][S5]

\[
\mathcal L_{\mathrm{perc}}
=\sum_{l\in\mathcal S}\alpha_l
\frac{1}{N_l}\left\|
\operatorname{norm}(\phi_l(\hat o_t))
-\operatorname{norm}(\phi_l(o_t))
\right\|_2^2.
\]

变量解释：\(\mathcal S\) 是选定 layer 集合，\(\alpha_l\) 是 layer weight，`norm` 表示约定的 channel/spatial normalization。直觉是比较深层 feature，而非要求每个像素精确相等。实现映射：记录 backbone/revision、是否冻结、输入归一化、layer、spatial resize、mask、weight 和 reduction。

S4 直接使用预训练并固定的 loss network 做 feature reconstruction；S5 说明深层 feature distance 与人类感知相似度有较强对应，并讨论 feature normalization 与线性校准。它们不支持“LPIPS/perceptual loss 自动提升机器人 actionability”。

## 14. Perceptual loss 的机器人边界

- ImageNet/感知相似度 feature 可能对纹理稳健，却不敏感于毫米级位姿、深度、gripper aperture 和接触状态。
- feature extractor 若与 generator 联合更新，target space 会漂移；必须明确 frozen/trainable 和梯度路径。
- LPIPS 本质是度量定义/校准方案之一；将其作为 training loss 仍需说明输入 domain、layer 与权重。
- perceptual loss 可与 pixel loss 互补，但两者都不能替代 action-swap、rollout、reward/termination 和 closed-loop success。

## 15. Mask、reduction 与 effective weight

同一个 nominal \(\lambda_k\) 不代表相同训练影响。若第 \(k\) 项先对 valid elements 平均：

\[
\bar{\mathcal L}_k
=\frac{\sum_i m_{k,i}\ell_{k,i}}
{\max(1,\sum_i m_{k,i})},
\qquad
\mathcal L=\sum_k\lambda_k\bar{\mathcal L}_k.
\]

变量解释：\(m_{k,i}\) 是 mask，denominator 是有效样本数。直觉是避免 padding/route 比例改变 raw sum；但 per-sample、per-token、per-pixel、per-key 平均仍有不同含义。实现映射：日志同时记录 numerator、valid count、reduced loss、scaled loss 与 route count。

## 16. Loss 大小不能直接比较

`reconstruction=0.1` 与 `reward=1.0` 不能推出 reconstruction 更不重要，原因包括：

- 单位/likelihood family 不同；
- pixel、token、sequence、batch denominator 不同；
- free-nats/clipping/symlog 改变标度；
- scale 相同但梯度范数、共享参数投影不同；
- sparse reward/terminal 的有效样本与 class imbalance 不同。

最低限度要画 raw/reduced/scaled loss、valid count、per-module gradient norm、cosine/conflict、head calibration 和 downstream metric。

## 17. 最小实现伪代码

```python
def world_model_objective(batch, model, scales):
    # 1. Posterior reads observations; prior only uses past latent and actions.
    post, prior, feat = model.rssm.observe(batch.obs, batch.prev_action)

    # 2. Keep the two KL directions separate because stop-gradient recipients differ.
    dyn = kl(stop_gradient(post), prior).clamp_min(model.free_nats)
    rep = kl(post, stop_gradient(prior)).clamp_min(model.free_nats)

    # 3. Build each target from its own schema and time-index contract.
    rec = masked_loss(model.decoder(feat), batch.obs, batch.obs_mask)
    rew = masked_loss(model.reward(feat), batch.reward, batch.reward_mask)
    con_target = build_continuation(batch.is_terminal, batch.is_timeout)
    con = masked_loss(model.continue_head(feat), con_target, batch.valid_mask)
    perc = perceptual_loss(model.decoder(feat), batch.obs, frozen_features=True)

    # 4. Log denominators and gradients; a total scalar alone cannot diagnose influence.
    terms = dict(rec=rec, dyn=dyn, rep=rep, rew=rew, con=con, perc=perc)
    return sum(scales[k] * terms[k].mean() for k in terms), audit(terms)
```

伪代码是 S1–S8 的工程综合，不是 S6 的逐行复制；`build_continuation` 必须按具体 environment/dataset 定义。

## 18. Matched objective audit

固定 data split/sampler、seed、steps/tokens、optimizer/schedule、batch、architecture、checkpoint init、augmentation、eval protocol 和 compute budget：

| arm | 目的 |
| --- | --- |
| base | action/policy 或最小 world-model baseline |
| +rec | observation reconstruction 的增量 |
| +dyn/rep | latent prior/posterior consistency 的增量 |
| +reward | immediate reward prediction 的增量 |
| +continue | termination/discount modeling 的增量 |
| +perceptual | feature-space reconstruction 的增量 |
| combined | 交互作用 |
| overwide/overweight | 容量与 auxiliary domination 反例 |

报告 one-step、open-loop horizon curve、action sensitivity、reward/continue calibration、closed-loop success、latency/compute 和 seed CI。若只比较 `base` 与 `combined`，无法归因某一 objective。

## 19. Failure-first 诊断

| 症状 | 首查 |
| --- | --- |
| rec 下降、rollout 仍漂 | posterior shortcut、prior/open-loop、action sensitivity、horizon |
| dyn/rep 卡在 free nats | clipping proportion、entropy、scale、梯度路径 |
| KL 很低、decoder 模糊 | collapse、decoder capacity、posterior usage |
| reward 好、success 差 | shaping/时间索引、value/continue、policy OOD、success predicate |
| continuation 全预测继续 | class imbalance、timeout/terminal、off-by-one、padding |
| perceptual 好、接触失败 | feature domain、geometry/contact sensitivity、camera/depth key |
| combined 比单项差 | gradient conflict、effective weight、route/mask、capacity competition |

## 20. 项目真实性边界

WAM inventory 支持讲 upstream action/future/value slot、condition/loss mask 与 objective audit 设计，但 local code/config/gradient trace 和 action-only/+world/+value/all matched result 缺失；历史 MSE/成功率已降级，不能借 WM-011 恢复。

UWM/LIBERO inventory 支持 shared diffusion 的 action/video 输出、finetune/eval protocol 与 user-confirmed protocol-bound result；它不提供 reconstruction/dynamics/reward/continuation/perceptual 单项消融，也不能证明某一 objective 带来 74.4% 或任何 uplift。

安全口径：

> 我能把每个 objective 落到 prediction、target、mask、reduction、scale 和 gradient path，并设计 matched ablation；当前个人材料没有完整 objective-level 因果实验，所以我只讲机制和审计方案，不声称某项 loss 已提升项目成功率。

## 21. Claim ledger

| Claim | 来源 | 等级 | 状态 |
| --- | --- | --- | --- |
| reconstruction 约束 latent 保留可解码 observation 信息 | S1–S3/S6 | primary + frozen code | checked |
| dyn/rep KL 以不同 stop-gradient 方向对齐 prior/posterior | S3/S6 | paper + frozen code | checked |
| reward、continue、value、success 语义不同 | S3/S6/S7 | primary + code | checked |
| perceptual objective 比较深层 feature，不保证 action-critical geometry | S4/S5 + analysis | primary + bounded synthesis | checked with warning |
| matched arms 可识别 objective 的局部贡献 | S1–S8 | engineering design | WARN / needs execution |
| WAM/UWM 已证明某项 auxiliary objective 提升 success | S8 | missing local ablation | rejected |

## 22. 仍待独立复核与补证据

1. 本节点的 primary/source-code 映射已复核，独立事实复核仍标 `PENDING`。
2. 需要 local objective config、dataset schema、mask/reduction trace、checkpoint、gradient log 和 matched ablation。
3. 需要 reward/continuation 的 exact time-index test，尤其 timeout、reset、padding 与 terminal transition。
4. 需要 perceptual backbone/layer/domain sensitivity test，包含 contact/geometry probes。
5. 浏览器 `file://` visual QA 受策略阻断，只能做 renderer/static/link validation。
6. 没有真实口述，不创建 `coaching_state.md`，题卡保持 `unseen`。

## 23. 参考来源

1. Ha and Schmidhuber, [*World Models*](https://arxiv.org/abs/1803.10122), 2018.
2. Hafner et al., [*Learning Latent Dynamics for Planning from Pixels*](https://arxiv.org/abs/1811.04551), 2019.
3. Hafner et al., [*Mastering Diverse Domains through World Models*](https://arxiv.org/abs/2301.04104), 2023/2025.
4. Johnson et al., [*Perceptual Losses for Real-Time Style Transfer and Super-Resolution*](https://arxiv.org/abs/1603.08155), 2016.
5. Zhang et al., [*The Unreasonable Effectiveness of Deep Features as a Perceptual Metric*](https://arxiv.org/abs/1801.03924), 2018.
6. `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`: [README](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/README.md), [`rssm.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/rssm.py), [`agent.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/agent.py), [`configs.yaml`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/configs.yaml).
7. [VOL 04 Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html)。
8. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) evidence inventories。

## 24. 下一节点

完成本节点后，VOL 04 进入 41/44；下一 bounded slice 只做 `VLA-WM-012`（RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导），不跨到 WM-013/014。
