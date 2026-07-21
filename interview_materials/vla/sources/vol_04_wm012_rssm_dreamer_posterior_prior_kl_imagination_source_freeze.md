# VOL 04 WM-012 Source Freeze：RSSM / Dreamer Posterior、Prior、KL Balancing 与 Imagined Rollout

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-012 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-012  
> 本轮边界：只冻结 RSSM 的 action-conditioned sequential latent model、posterior/prior 因子分解、KL 双重职责、DreamerV2 KL balancing、DreamerV3 dyn/rep + free bits，以及从 replay posterior state 到 pure-prior imagination 的推导与实现映射；不重复 WM-011 的五类 objective 语义，不展开 WM-021 的 actor/critic return 优化，也不把公开 Dreamer 机制写成本地 WAM/UWM 实现。

## 1. 冻结结论

1. RSSM 把 model state 拆为 deterministic recurrent state \(h_t\) 与 stochastic state \(z_t\)：\(h_t\) 汇总历史/action，\(z_t\) 表达当前一步的不确定表示。
2. posterior \(q(z_t\mid h_t,o_t)\) 在 filtering/training 时读取当前 observation；prior \(p(z_t\mid h_t)\) 不读当前 observation，因而才能在未来 observation 不存在时 rollout。
3. 单个 \(D_{\mathrm{KL}}(q\|p)\) 同时承担“训练 prior 追 posterior”和“约束 posterior 不要偏离 prior”两种职责；KL balancing 用 stop-gradient 与权重拆开两条梯度路径。
4. DreamerV2 的 balancing 是 \(\alpha D_{\mathrm{KL}}(\operatorname{sg}(q)\|p)+(1-\alpha)D_{\mathrm{KL}}(q\|\operatorname{sg}(p))\)，论文取 \(\alpha=0.8\)；DreamerV3 改为独立 dyn/rep loss、不同 scale 与 1 nat free bits。二者相关但不能混成同一 exact objective。
5. imagined rollout 必须从 replay 中过滤得到的 posterior state 起步；起点之后只由 policy action、deterministic transition 与 prior sampling推进，不能读取未来 encoder token/observation。
6. posterior fit、one-step KL 或 imagined return 都不证明 long-horizon/closed-loop 有效；需要 reset/time-index test、prior-only trace、action intervention、horizon curve 与项目证据。

## 2. 一手来源与冻结快照

| ID | 来源 | 冻结版本与响应 SHA-256 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Hafner et al., *PlaNet* | arXiv `1811.04551`；ar5iv response `6a9bed11e5963626016235227ab85594ae5d42773e675860788c51a071929a97` | RSSM deterministic/stochastic state、latent planning 与 posterior/prior 基础 | DreamerV2/V3 exact KL 配置 |
| S2 | Hafner et al., *Dream to Control*（DreamerV1） | arXiv `1912.01603`；ar5iv response `a9e11616b9bc421ac9886ad78fd2bfd1ac0bc1a44e9f6333a9c068da5eb52fec` | latent imagination、analytic-gradient behavior learning 与 replay belief 起点 | DreamerV2 categorical state/KL balancing、V3 exact loss |
| S3 | Hafner et al., *Mastering Atari with Discrete World Models*（DreamerV2） | arXiv `2010.02193`；ar5iv response `4679cffcc4cd621d2adb7aca04cc3cfc60bf8f7f994c2678a9174ee2043039b1` | categorical RSSM、sequential VAE、KL 双重职责、\(\alpha=0.8\) balancing、imagination MDP | DreamerV3 free-bits/scale 或个人项目结果 |
| S4 | Hafner et al., *DreamerV3* | arXiv `2301.04104`；arXiv HTML response `7ce561853df3b35ccf0316476b3f7538b60117feb358bd562dc279f0d5067a26` | RSSM factorization、prediction/dynamics/representation loss、1 nat free bits、imagined representations | frozen reimplementation 的全部 defaults 或本地复现 |
| S5 | `danijar/dreamerv3` frozen code | commit `e3f02248693a79dc8b0ebd62c93683888ddaccfe`；`rssm.py` `d6d50166914e94fb8bd17a5d5dbda9d42cdd37b85819bb1e9fff3a64d4ad2eb6`；`agent.py` `adce8e4274bc098c218bf9a20fd3327545f0ad7d850b5fe328597382e91b5269`；`configs.yaml` `9dff9c7062e3e33951cb54c6dd4b598aaf7e56e18e2cff39c812eaa797bcfcfc`；README `a4d8e77c07a876a7f528aa204fbc910812c5ca96bcfb67709b366f8ff0d3ed6b` | reset/observe/imagine/starts/loss、categorical shape、dyn/rep/free_nats、Agent imagination 路径 | 论文作者官方代码、checkpoint reproduction、个人 ownership |
| S6 | [Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html) | canonical SHA `bb48af7605688132ddd589109c8417dd0ebfe65f504a98cf5ab660f01e34ba7b` / `da16c172179cae926d329259e76955a55555fe53a15233f265d1f74a3d421ae4` | WM-012 允许逐节点生成；repo provenance 与 PlaNet overshooting 边界 | local Dreamer run |
| S7 | [WM-011 Objective Semantics](vol_04_wm011_objective_semantics_source_freeze.html) 与 [WM-021 Actor/Critic](vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html) | canonical SHA `7632d05497acd5170a5955a1c7eda2e68f40df39257f2d343229a61eba9d7b35` / `de2bd8a1652e28c0ba5c4ec389574040e2bc06bfe63ce057764dbe9c3e11f4ca` | 相邻节点去重边界 | 本节点已做 actor/critic 或 objective ablation |
| S8 | [WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories | canonical SHA `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d` / `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 项目机制与真实性边界 | 个人 RSSM/Dreamer implementation 或收益 |

**Provenance warning：**S5 README 明确称该仓库为 DreamerV3 reimplementation，并与 Google/DeepMind 无关。本页只能说“该 frozen reimplementation 的代码路径”。

## 3. 与相邻节点的边界

| 节点 | 已回答 | WM-012 只补什么 |
| --- | --- | --- |
| WM-004 | encoder、RSSM、decoder/reward/continue 的数据流 | sequential latent factorization 与推导 |
| WM-011 | reconstruction、dyn/rep、reward、continue、perceptual 各监督什么 | KL 为什么有两条梯度职责 |
| WM-021 | imagined actor/critic、lambda-return 与 model bias | imagination 轨迹本身如何从 posterior 起点生成 |

WM-012 不重新解释每个 head 的完整 loss，也不推导 actor/critic loss；它负责把“训练 belief”与“预测未来”之间的数学和代码桥梁闭合。

## 4. POMDP 与 belief state 直觉

机器人 observation \(o_t\) 只看到环境的一部分；单帧无法唯一确定速度、遮挡物、接触模式或任务阶段。RSSM 用：

- \(h_t\)：deterministic memory，汇总历史 latent 和 action；
- \(z_t\)：stochastic representation，容纳当前 observation 带来的新信息与多可能状态。

组合 state \(s_t=(h_t,z_t)\) 是 learned belief，不是真实物理 state 的保证。若 observation/history 不充分或 objective 允许 shortcut，belief 仍会丢失 action-critical 信息。

## 5. RSSM 的时间递推

\[
h_t=f_\phi(h_{t-1},z_{t-1},a_{t-1}).
\]

变量解释：\(f_\phi\) 是 deterministic recurrent transition，输入前一步 memory、stochastic state 与已执行 action。直觉是先用“过去 + 动作”推到当前预测上下文。实现映射：S5 `_observe` 在读取当前 token 前先调用 `_core(deter, stoch, action)`；reset 时旧 carry/action 被 mask。

## 6. Prior 与 posterior

\[
\hat z_t\sim p_\phi(z_t\mid h_t),
\qquad
z_t\sim q_\phi(z_t\mid h_t,o_t).
\]

变量解释：prior \(p_\phi\) 只依赖历史汇总 \(h_t\)，posterior \(q_\phi\) 额外读取当前 observation。直觉是 prior 回答“没看当前帧时我预测会在哪”，posterior 回答“看到当前帧后我相信在哪”。实现映射：S5 `_prior(deter)` 输出 prior logits；`_observe` 将 encoder token 与 deter 拼接后输出 posterior logits并采样 stochastic state。

## 7. Action-conditioned generative model

给定动作序列，最小因子分解可写为：

\[
p_\phi(o_{1:T},r_{1:T},c_{1:T},z_{1:T}\mid a_{0:T-1})
=\prod_{t=1}^{T}
p_\phi(z_t\mid h_t)
p_\phi(o_t\mid h_t,z_t)
p_\phi(r_t\mid h_t,z_t)
p_\phi(c_t\mid h_t,z_t).
\]

变量解释：\(c_t\) 是 continuation/discount target；\(h_t\) 由前式确定。直觉是 prior 生成 latent，heads 再生成可观测/任务信号。实现映射：具体 observation key、reward/continue 的时间索引和 likelihood 必须按 dataset/config 冻结；该式是跨版本抽象，不是 S5 的 tensor dump。

## 8. Approximate posterior

真实 posterior \(p(z_{1:T}\mid o,r,c,a)\) 难以直接计算，RSSM 用 observation-conditioned approximation：

\[
q_\phi(z_{1:T}\mid o_{1:T},a_{0:T-1})
=\prod_{t=1}^{T}q_\phi(z_t\mid h_t,o_t).
\]

变量解释：每一步 posterior 使用当前 encoder token 和 action/history memory。直觉是按时间进行 filtering，而不是一次读取整段未来。实现映射：训练时必须检查 encoder/attention 是否意外看到 \(o_{t+1:T}\)；否则表面是 posterior，实际发生 future leakage。

## 9. Sequential ELBO 从哪里来

由变分下界：

\[
\log p_\phi(o,r,c\mid a)
\ge
\mathbb E_{q_\phi}\left[
\sum_{t=1}^{T}
\left(
\log p_\phi(o_t,r_t,c_t\mid h_t,z_t)
-D_{\mathrm{KL}}\!\left(q_\phi(z_t\mid h_t,o_t)\|p_\phi(z_t\mid h_t)\right)
\right)
\right].
\]

变量解释：第一项奖励 latent 解释 observation/reward/continue；KL 让 posterior 与可预测 prior 对齐。直觉是 sequential VAE：既要“看到当前帧能编码”，又要“只靠历史动作能预测”。实现映射：Dreamer 实际会拆 prediction/dynamics/representation loss、加权、free bits、symlog 或不同 likelihood；不能把抽象 ELBO 当 exact config。

## 10. KL 的双重职责

同一个 \(D_{\mathrm{KL}}(q\|p)\) 对两组参数有不同作用：

1. 固定 posterior，更新 prior：让 transition predictor 追上 observation-derived representation；
2. 固定 prior，更新 posterior：限制 encoder 不要把每帧编码成难以预测的任意信息。

若 prior 尚差却强力把 posterior 拉向 prior，representation 可能变得容易预测但信息不足；若只训练 prior 不约束 posterior，posterior 可能塞入大量当前帧细节，prior 永远追不上。

## 11. DreamerV2 的 KL balancing

DreamerV2 将两条梯度路径显式写成：[S3]

\[
\mathcal L_{\mathrm{KL-bal}}
=\alpha D_{\mathrm{KL}}\!\left(\operatorname{sg}(q)\|p\right)
+(1-\alpha)D_{\mathrm{KL}}\!\left(q\|\operatorname{sg}(p)\right),
\qquad \alpha=0.8.
\]

变量解释：第一项只更新 prior，第二项只更新 posterior；\(\alpha=0.8\) 是 DreamerV2 论文 setting，不是所有 Dreamer 默认。直觉是先让困难的 transition prior 更快追 posterior，避免坏 prior 过早压扁 representation。实现映射：审计时分别记录两项、梯度范数和 entropy，不能只看合并 KL。

## 12. DreamerV3 的 dyn / rep 分离

DreamerV3 写为：[S4]

\[
\mathcal L_{\mathrm{dyn}}
=\max\!\left(1,
D_{\mathrm{KL}}[\operatorname{sg}(q_\phi)\|p_\phi]
\right),
\]

\[
\mathcal L_{\mathrm{rep}}
=\max\!\left(1,
D_{\mathrm{KL}}[q_\phi\|\operatorname{sg}(p_\phi)]
\right).
\]

变量解释：dyn 更新 sequence prior，rep 约束 representation；`max(1,·)` 是 1 nat free bits。直觉是低于阈值时不继续为压小 KL 牺牲 prediction 信息。实现映射：S5 `RSSM.loss` 逐行对应两条 KL 与 `jnp.maximum`；frozen config 的 `loss_scales` 为 `dyn:1.0, rep:0.1`。

## 13. V2 balancing 与 V3 dyn/rep 不能混写

共同点：都用 stop-gradient 拆 prior-learning 与 posterior-regularization。

差异：

- DreamerV2 用一个 α-balanced 表达，论文给 \(\alpha=0.8\)；
- DreamerV3 用两个命名 loss、各自 scale，并加 1 nat free bits；
- S5 frozen config 是 V3 reimplementation 的 `dyn=1.0, rep=0.1`，不能写成“使用 α=0.8”。

面试中可说“同属 KL gradient balancing 思路”，但必须按版本报 exact formula/config。

## 14. Free bits 的诊断边界

free bits 不是“免 KL”或“保证不 collapse”。当 raw KL 低于 1 nat 时，clipped loss 对继续压低 KL 不再提供梯度；但 prediction loss、representation capacity、decoder shortcut 与数据仍决定 latent 是否有用。

至少记录：raw KL、clipped KL、低于阈值比例、prior/posterior entropy、categorical usage、decoder/reward/continue fit、action sensitivity 与 rollout horizon error。只记录 clipped `loss/dyn=1` 会隐藏 raw KL 已经接近 0 还是刚低于 1。

## 15. Reset 与时间索引

S5 `_observe` 的顺序是：

1. 用 `reset` mask 掉旧 \((h,z)\) 与 previous action；
2. 用 \((h_{t-1},z_{t-1},a_{t-1})\) 更新 \(h_t\)；
3. 将 \(h_t\) 与当前 token \(e(o_t)\) 生成 posterior \(z_t\)。

因此 batch 中传给 RSSM 的 action 必须是与当前 observation 对齐的 previous action。若错用 \(a_t\)、reset 前动作或跨 episode carry，会产生一位偏移或 episode leakage；模型仍可能靠 observation 重建而掩盖错误。

## 16. Frozen code 的 categorical state

S5 `initial` 创建：

```text
deter: [B, deter]
stoch: [B, stoch, classes]
```

`_logit` 输出 `[... , stoch, classes]`，`_dist` 构造 categorical/one-hot distribution 并跨 stochastic variables 聚合 KL。shape 与 `unimix` 来自 config；它证明 frozen implementation 的表示形式，不代表所有 RSSM 都必须使用 categorical latent。

## 17. Replay posterior 起点

S5 `RSSM.loss/observe` 先对 replay sequence 生成 posterior entries；`starts(entries, carry, nlast)` 从最后 \(K\) 个 posterior entries reshape 出 imagination starts。`Agent.loss` 中 \(K=\min(\texttt{imag_last},T)\)（未设置时受代码/config语义控制），再调用 `dyn.imagine(..., H)`。

起点是“由真实 replay 过滤得到的 belief state”，不是纯 prior 随机状态，也不是每个 imagined step 都重新读取真实 observation。

## 18. Imagined rollout 的递推

给定 \(s_0=(h_0,z_0)\sim q_{\mathrm{replay}}\)，每一步：

\[
\hat a_t\sim\pi(\cdot\mid \hat h_t,\hat z_t),
\]

\[
\hat h_{t+1}=f_\phi(\hat h_t,\hat z_t,\hat a_t),
\qquad
\hat z_{t+1}\sim p_\phi(\cdot\mid\hat h_{t+1}).
\]

变量解释：帽号表示 imagined variable；从第一个 transition 起 stochastic state 只来自 prior。直觉是 actor 提 action，world model 预测 consequence，再循环。实现映射：S5 `imagine(single=True)` 先在 carry 上采 action，再 `_core`、`_prior`、sample；sequence mode 用 scan 重复 \(H\) 步。

## 19. Imagination trajectory 的联合分布

\[
p(\hat z_{1:H},\hat a_{0:H-1}\mid s_0)
=\prod_{t=0}^{H-1}
\pi(\hat a_t\mid\hat s_t)
p_\phi(\hat z_{t+1}\mid\hat h_{t+1}).
\]

变量解释：\(s_0\) 来自 replay posterior，后续 transition 由 policy 与 prior 决定。reward/continue/value heads 可在 \(\hat s_t\) 上查询，但不改变“未来 observation 不可见”的条件。实现映射：保存 start episode/time index、start state、action、prior logits/sample、horizon、random seed 与 reset/continue handling。

## 20. 为什么不必在 imagination 中解码像素

actor/critic 只需 latent feature、predicted reward/continue/value；每步解码 RGB 会增加计算，而且视觉细节不一定是 behavior learning 所需。DreamerV2 明确在 behavior learning 时不预测 image，以并行模拟大量 latent trajectory。[S3]

但“不解码”也会失去直观诊断。实践中可离线解码少量 trace 检查 hallucination，同时以 latent/action/reward/continue 与真实 cloned-state rollout 为主证据；漂亮视频不能替代因果验证。

## 21. Future leakage 与伪 imagination

以下任一情况都会破坏 pure-prior rollout：

- imagined step 继续喂 \(o_{t+1}\) 或其 encoder token；
- bidirectional encoder/attention 在 posterior 时读到未来帧；
- action 与 observation 索引错位，使“未来 action”进入当前 transition；
- reset/padding mask 让上一 episode state 泄漏；
- evaluation 用 posterior trajectory，却称 open-loop prior trajectory。

最小单元测试：在 rollout 起点后替换/清空未来 observation，prior trajectory 应不变；posterior filtering trajectory应随 observation intervention 改变。

## 22. 最小可审计伪代码

```python
def rssm_filter_then_imagine(batch, rssm, policy, horizon):
    # 1. Encode only the replay observations allowed at each filtering step.
    tokens = encode_causally(batch.observation)

    # 2. Previous actions and reset masks must align with the current observation.
    entries, posterior = rssm.observe(tokens, batch.previous_action, batch.is_first)

    # 3. Keep prior-learning and posterior-regularization gradients separate.
    prior = rssm.prior(posterior.deter)
    dyn = kl(stop_gradient(posterior.dist), prior).clamp_min(1.0)
    rep = kl(posterior.dist, stop_gradient(prior)).clamp_min(1.0)

    # 4. Choose replay posterior states as starts, then remove future observations.
    starts = select_posterior_starts(entries, batch.valid_mask)
    imagined = rssm.imagine(starts, policy, horizon=horizon)

    # 5. Audit actions, prior logits/samples and horizon-wise drift independently.
    return imagined, audit_kl_and_rollout(dyn, rep, posterior, prior, imagined)
```

伪代码是 S1–S8 的工程综合；`clamp_min(1.0)` 和 categorical latent 映射 S4/S5，不能泛化成所有 RSSM 默认。

## 23. 最小诊断矩阵

| Probe | 证明什么 | 不能证明 |
| --- | --- | --- |
| posterior reconstruction/head fit | filtering state 含 target 信息 | prior 可预测 |
| one-step prior↔posterior KL | 局部分布对齐 | long-horizon稳定 |
| raw/clipped KL + entropy/usage | free-bits、collapse/underuse 迹象 | downstream success |
| future-observation removal | imagination 未显式读未来 | 无间接 leakage/shortcut |
| action swap/zero/random | prior 对 action 是否敏感 | consequence 与环境一致 |
| horizon-wise prior rollout | compounding 与 drift | closed-loop可执行 |
| cloned-state alignment | 同 start/action 的模型/环境 consequence | real-robot transfer |
| actor/critic success | behavior 层结果 | RSSM 每个机制都正确 |

## 24. Matched ablation / trace

固定 data、steps、architecture、optimizer、seed、posterior encoder、heads 与 eval：

| arm | 目的 |
| --- | --- |
| no-KL / tiny-KL diagnostic | 检查 posterior 任意编码与 prior 追不上 |
| unbalanced KL | 基准 ELBO 梯度耦合 |
| V2-style α sweep | prior/posterior gradient权重敏感性 |
| V3 dyn/rep scale sweep | 独立 scale 与 free-bits敏感性 |
| posterior rollout | teacher-forced/filtering 上界诊断 |
| prior-only rollout | 真正 imagination/open-loop |
| shuffled/zero action | action dependence 反例 |

报告 prediction loss、raw/clipped KL、entropy/usage、gradient norm、one-step/open-loop error、action sensitivity、reward/continue calibration、closed-loop success、compute 与 seed CI。不同 latent type/capacity 不能只改 KL 系数后直接比较。

## 25. 高频失败诊断

| 症状 | 首查 |
| --- | --- |
| posterior 好、prior 差 | action/time index、prior capacity、KL gradient、future shortcut |
| raw KL≈0、表示无信息 | posterior collapse、decoder/reward shortcut、free-bits日志 |
| raw KL 很大不降 | prior capacity、action missing、reset leakage、posterior塞细节 |
| dyn=rep=1 长期不动 | raw KL 与 clipping ratio；不要只看 clipped scalar |
| prior 不随 action 变 | action mask/order/scale、data coverage、core input |
| horizon 增长即崩 | one-step-only fit、model bias、latent sampling、terminal handling |
| episode 开头异常 | previous-action/reset/carry off-by-one |
| imagined return 好、real 差 | 转 WM-021 的 model exploitation、value calibration 与 paired rollout |

## 26. 项目真实性边界

WAM/Cosmos 当前材料是 diffusion latent slot、condition/loss mask、action/future/value 与 planning/eval contract，不是 RSSM。UWM 是 shared diffusion 的 action/video modeling，也不是 Dreamer posterior/prior implementation。两者可用于回答“为什么需要可预测 latent/action-conditioned future”，但不能说“项目使用了 RSSM、KL balancing 或 Dreamer imagination”。

安全口径：

> 我能从 sequential ELBO 推导 posterior/prior 与 KL 的双重职责，并按 frozen Dreamer code 解释 filtering→posterior starts→prior-only imagination；我的 WAM/UWM 项目不是 RSSM 实现，当前也没有本地 Dreamer checkpoint/trace，所以只讲机制和可执行审计，不声称个人复现或收益。

## 27. Claim ledger

| Claim | 来源 | 等级 | 状态 |
| --- | --- | --- | --- |
| RSSM 组合 deterministic memory 与 stochastic latent | S1–S4 | primary | checked |
| posterior 读 observation、prior 用于不读未来的 imagination | S1–S5 | primary + frozen code | checked |
| DreamerV2 KL balancing 使用 α=0.8 的两条 stop-gradient 路径 | S3 | primary | checked / version-specific |
| DreamerV3 分 dyn/rep、1 nat free bits，S5 scale 1.0/0.1 | S4/S5 | primary + frozen code | checked / config-specific |
| S5 imagination 从 replay posterior entries 起步后只用 prior | S5 | frozen code | checked |
| WAM/UWM 使用 RSSM/Dreamer 或已证明其收益 | S8 | missing / contradicted by architecture boundary | rejected |

## 28. 仍待独立复核与补证据

1. primary/frozen-code 事实已复核，本节点独立事实复核仍标 `PENDING`。
2. 需要 local causal encoder test、previous-action/reset alignment test、raw/clipped KL trace 与 categorical usage。
3. 需要 posterior-vs-prior horizon curve、action intervention、cloned-state consequence 与 checkpoint/config SHA。
4. 若未来项目采用 RSSM，需补 module path、local diff、run ledger、ownership 与 actor/critic gradient boundary。
5. 浏览器 `file://` visual QA 受策略阻断，只能做 renderer/static/link validation。
6. 没有真实口述，不创建 `coaching_state.md`，题卡保持 `unseen`。

## 29. 参考来源

1. Hafner et al., [*Learning Latent Dynamics for Planning from Pixels*](https://arxiv.org/abs/1811.04551), 2019.
2. Hafner et al., [*Dream to Control: Learning Behaviors by Latent Imagination*](https://arxiv.org/abs/1912.01603), 2020.
3. Hafner et al., [*Mastering Atari with Discrete World Models*](https://arxiv.org/abs/2010.02193), 2021.
4. Hafner et al., [*Mastering Diverse Domains through World Models*](https://arxiv.org/abs/2301.04104), 2023/2025.
5. `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`: [README](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/README.md), [`rssm.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/rssm.py), [`agent.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/agent.py), [`configs.yaml`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/configs.yaml).
6. [VOL 04 Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html)。
7. [WM-011 Objective Semantics](vol_04_wm011_objective_semantics_source_freeze.html) 与 [WM-021 Dreamer Actor/Critic](vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)。
8. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) evidence inventories。

## 30. 下一节点

完成本节点后，VOL 04 进入 42/44；下一 bounded slice 只做 `VLA-WM-013`（latent overshooting 或 multi-step consistency loss 解决什么、可能带来什么偏差），不跨到 WM-014。
