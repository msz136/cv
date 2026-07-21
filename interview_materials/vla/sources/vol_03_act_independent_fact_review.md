# VOL 03 Source Audit C：ACT CVAE / Action Chunk / Temporal Ensemble 独立事实复核

> 状态：`independent_fact_reviewed / audit_c / cvae_loss_mask_query_ensemble_checked / PASS WITH WARNING`
> 审查日期：2026-07-19
> 范围：ACT v1 论文与 frozen repo 的 CVAE 输入、latent train/infer、L1/KL、padding denominator、query embedding、temporal ensemble 与 H/K/R rollout。
> 结论先行：ACT 的论文与官方代码都支持“连续 action chunk + CVAE style latent + Transformer queries”的主机制，但实现层必须保留三类差异：Algorithm 1 写 reconstruction MSE，正文与 frozen code 使用 L1；论文图示的 fixed/sinusoidal query 与 frozen code 的 learned `nn.Embedding` 不同；`is_pad` 乘到逐元素 L1 numerator 后，代码直接对完整 `B×H×D` 张量取 mean，padding 会稀释 loss。temporal ensemble 融合的是不同 query 对同一 target time 的预测，oldest row 权重最大；含任意零分量的 prediction row 会被 sentinel 过滤。以上均为 public paper/code facts，不证明本地 OpenPiVLA 采用 ACT 或任何指标。

## 1. 直接复核来源与冻结对象

| ID | 来源 | 本次直接读取内容 | SHA / Verdict |
| --- | --- | --- | --- |
| P01 | [ACT v1 PDF](https://arxiv.org/pdf/2304.13705v1) | Section IV、Algorithms 1/2、Fig. 4/5、loss/query/ensemble ablation | `2E2FE25860F5F9CEE9E655A2714E9F2264A7A5078BCD267C16D3F39AF461345A` / `primary-verified` |
| C01 | [`detr_vae.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py) | posterior input、reparameterization、zero latent、query embedding、pad head | `499D968A3704156E5E29425A29691C3FA93421481D3609ED6B600B21801270F1` / `official-code` |
| C02 | [`policy.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py) | masked L1、KL、loss denominator、test path | `352EFCA415EE0E31073A27CA91560195702D1E9B545E573A3A668A53F06DD127` / `official-code` |
| C03 | [`utils.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/utils.py) | episode tail padding、is_pad、mean/std、all-episode stats | `71315DE9E613024E781F089C2F46BAA6A94BE79DAA97A45C8601829FC1BADCEC` / `official-code` |
| C04 | [`imitate_episodes.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py) | query frequency、temporal table、sentinel、postprocess、50 rollouts | `F2B057CD497F3FEF20BDC4197879D1C02E1C751F83154CCE0183FCC10F7E2540` / `official-code` |
| C05 | [`constants.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/constants.py) | simulation camera/task defaults | `2E27D4412E2B7E1F2E4148105FDF514D8C52EC6C8F1C86EF0549C475E8B91D86` / `official-code` |
| C06 | [`transformer.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/transformer.py) | latent/proprio prefix、camera concat、query decoder | `C6D2A1E7138E6CA62DB7CC61BFC99857FB2A3A9375BA7B304310CA264F357EE2` / `official-code` |
| O01 | 本次 synthetic probes | masked mean dilution、temporal weights、zero sentinel、H/K query steps | `local-evidence / PASS` |

冻结 commit：`742c753c0d4a5d87076c8f69e5628c79a8cc5488`，MIT。本文不把 repo 外部 `aloha_scripts`、第三方 ACT++ 或用户本地 fork 混入实现结论。

## 2. ACT 的 public I/O 与 chunk contract

论文 real-robot setup 使用多视角 RGB、当前 follower qpos 与 14D absolute joint target；frozen repo 的 simulation config 可只有 top camera，因此“ACT repo 默认总是四相机”不成立。一次 policy forward 输出 `[B,H,14]` 连续 action chunk：

\[
\pi_\theta(a_{t:t+H-1}\mid o_t,z),
\qquad
o_t=(I_t^{1:C},q_t),
\qquad
a_t\in\mathbb R^{14}.
\]

变量与直觉：`H` 是 prediction/chunk horizon，`C` 是实际 camera count；`q_t` 与 `a_t` 是当前 joint state 与未来 joint target。代码中的 `num_queries` 同时决定 query slot 数与输出时间长度，但不能单独证明执行窗口 `K` 或 replan interval `R`。

## 3. CVAE：posterior 看什么，推理时如何消失

训练期 posterior encoder 的输入是：

```text
[CLS] learned token      [B,1,D]
current qpos projection  [B,1,D]
target action projection [B,H,D]
                         → encoder sequence [B,H+2,D]
```

代码由 `encoder_action_proj`、`encoder_joint_proj`、`cls_embed` 与 `latent_proj` 产生 $\mu,\log\sigma^2$，再用：

\[
z=\mu_\phi+\exp\!\left(\frac12\log\sigma^2_\phi\right)\odot\epsilon,
\qquad
\epsilon\sim\mathcal N(0,I).
\]

变量与实现：`z\in\mathbb R^{32}` 是 style latent；posterior 不读取 image，image 只进入 decoder policy path。推理时不传 action，因此代码跳过 posterior，直接构造全零 `z=0`，即单位高斯 prior mean；这使 frozen path 在相同输入下 deterministic。不能说 ACT inference 默认随机采样多个 style。

decoder 通过 ResNet 特征、qpos、latent 与 `H` 个 query embedding 经过 Transformer decoder，最后由 `action_head` 映射到 `[B,H,14]`。论文图示/文字使用 fixed/sinusoidal position embedding 的表述，而该 frozen commit 的 `query_embed=nn.Embedding(num_queries, hidden_dim)` 是 learned query；这是必须保留的 paper/code mismatch。

## 4. L1/KL、padding 与 loss denominator

论文 Algorithm 1 写 reconstruction MSE，但正文 Section IV-C 说明使用 L1，frozen `policy.py` 实际执行：

\[
\mathcal L_{\mathrm{L1,code}}
=
\operatorname{mean}_{b,h,d}
\left[
m_{b,h}\,
\left|\hat a_{b,h,d}-a_{b,h,d}\right|
\right],
\]

\[
\mathcal L_{\mathrm{total}}
=
\mathcal L_{\mathrm{L1,code}}
+
\lambda_{\mathrm{KL}}\,
D_{\mathrm{KL}}\!\left(q_\phi(z\mid q,a)\,\|\,\mathcal N(0,I)\right).
\]

变量与实现：`m_{b,h}=1` 表示 non-padding timestep；代码把 `is_pad.unsqueeze(-1)` 取反后乘到逐元素 L1，但随后直接调用 tensor `.mean()`，分母仍是完整 `B\times H\times D`。`is_pad_head` 由 decoder 返回，却没有进入该 commit 的 loss。

理想的 valid-element reduction 应为：

\[
\mathcal L_{\mathrm{valid}}
=
\frac{\sum_{b,h,d}m_{b,h}
\left|\hat a_{b,h,d}-a_{b,h,d}\right|}
{\sum_{b,h,d}m_{b,h}+\varepsilon}.
\]

这两个公式的区别不是“mask 是否存在”，而是 denominator 是否按有效 action elements 归一化。被 mask 的 padding 不参与 numerator，但仍会稀释 gradient scale；不能把 frozen code 的行为称为严格 valid-only mean。

## 5. 数据 padding 与 normalization 边界

`EpisodicDataset` 随机选 episode 内 `start_ts`，读取当前 qpos/图像和从该时刻开始的 action；episode 尾部不足 `episode_len` 的位置以零填充并置 `is_pad=True`。`get_norm_stats` 在 train/val split 之前对传入的全部 `num_episodes` 计算 qpos/action mean/std，并将 std clip 到至少 `1e-2`：

\[
\tilde q=\frac{q-\mu_q}{\max(\sigma_q,10^{-2})},
\qquad
\tilde a=\frac{a-\mu_a}{\max(\sigma_a,10^{-2})}.
\]

变量与实现：这说明当前 commit 的 normalization stats 不是严格只由 train split 计算；它是实现事实，不应推广成推荐的 holdout protocol。推理时 `imitate_episodes.py` 用 dataset_stats 反归一化并把结果命名为 `target_qpos` 传给 `env.step`，证明该实现的 controller target 是 joint-position path。

## 6. Temporal ensemble：同一 target time，oldest 权重最大

不开 temporal aggregation 时，代码：

- `query_frequency=num_queries=H`；
- 在 `t=0,H,2H,...` query；
- 对当前 chunk 读取 `all_actions[:,t % H]`；
- chunk 内 open-loop，chunk 边界重新观察。

开启 temporal aggregation 时：

- `query_frequency=1`，每个 control step query；
- 第 `q` 次 query 的 `H` 个预测写入 `all_time_actions[q,q:q+H]`；
- 当前物理时刻 `t` 读取的是 column `t`，融合不同 query 对同一 `a_t` 的预测；
- `exp_weights=np.exp(-0.01*np.arange(n))`，row 顺序 oldest→newest，因此 oldest 权重最大。

若有效预测数为 `n`，权重是：

\[
w_i=\frac{\exp(-m i)}{\sum_{j=0}^{n-1}\exp(-m j)},
\qquad i=0\ \text{表示 oldest row}.
\]

变量与实现：这不是把 `a_{t-1},a_t,a_{t+1}` 做普通时域平滑，而是对同一目标时刻的多次估计加权。论文称没有额外 training cost，但 inference 从每 `H` 步一次变为每步一次；不能把“无额外训练成本”说成“无额外部署成本”。

## 7. Synthetic probes

本次用独立 NumPy probe 检查边界，不安装或修改 ACT 运行环境：

| Probe | 结果 | 含义 |
| --- | --- | --- |
| `B=1,H=4,D=14`，仅 1 个 valid element error=1 | code-style full mean = `1/56=0.0178571429`，valid-only mean = 1 | padding/维度会产生 56 倍 dilution |
| 两样本 valid lengths=4 与 1 | full mean=0.625，valid-only mean=1 | batch 内不同 episode 长度也改变 effective scale |
| temporal weights `n=3,m=0.01` | [0.336672, 0.333322, 0.330006] | oldest row 最大 |
| prediction row 含一个零分量 | `torch.all(row != 0)` 为 false，整行被过滤 | sentinel 不是 per-dimension mask |
| `H=3`、10 control steps | no-ensemble query steps [0,3,6,9]；ensemble [0..9] | H、K、R 的查询语义分离 |

probe 验证的是 reduction、权重和分支语义，不证明任何 learned policy success、controller safety 或个人项目 bug。

## 8. 对 VLA-ACT-011..017 的回写结论

| Question ID | 独立复核结论 | 必须保留的边界 |
| --- | --- | --- |
| `VLA-ACT-011` | `H/K/R/\Delta t` 与两种 rollout 分支通过 | local OpenPiVLA H/K 未证 |
| `VLA-ACT-012` | CVAE posterior/decoder/query/shape 通过 | ACT 不是 language VLA |
| `VLA-ACT-013` | posterior train、reparameterization、test `z=0` 通过 | 不推断本地随机 rollout |
| `VLA-ACT-014` | same-target-time ensemble 与 oldest-first weight 通过 | sentinel edge-case 仍是实现风险 |
| `VLA-ACT-015` | chunk boundary 与 per-step ensemble 通过 | local queue/controller 未证 |
| `VLA-ACT-016` | H trade-off、calls、staleness 与 paper ablation 通过 | 论文 H=100 不是通用最优 |
| `VLA-ACT-017` | ACT/FAST/π0/Diffusion 表示对照可用 | 不横比跨 protocol success |

本次不改变 44 张 VOL 03 卡或全局题卡的 `unseen` 状态，也不创建 `coaching_state.md`。

## 9. 不能推出的本地项目事实

- 不推出 OpenPiVLA 使用 ACT 的 CVAE、14D absolute joint target 或 temporal ensemble。
- 不推出本地 `H=100`、`K=1`、`R=1`、50 Hz、4 cameras、mean/std stats 或 97.4%。
- 不把论文 Algorithm 1 的 MSE/L1 表述差异、learned query、mask denominator 或 sentinel edge-case 写成本人发现/修复。
- 不把 ACT public success、paper ablation 或 official code author 映射为候选人 ownership。

## 10. 下一步

Audit C 的 ACT CVAE、L1/KL、padding denominator、query embedding、temporal ensemble 与 H/K/R public facts 已完成独立复核，公共事实层 verdict 为 `PASS WITH WARNING`。这只表示 paper/frozen-code/synthetic-probe 证据链已闭合；local project artifacts、controller、ownership 与 oral drill 仍保持 `WARN/PENDING`。下一 bounded slice 优先进行一题 ACT 真实口述，或收集本地 OpenPiVLA runtime artifact。

## 参考入口

- [VOL 03 ACT Claim-to-Code](vol_03_act_claim_to_code.html)
- [VOL 03 π0 / FAST / OpenPI Independent Review](vol_03_pi0_fast_openpi_independent_fact_review.html)
- [VOL 03 Diffusion Policy Claim-to-Code](vol_03_diffusion_policy_claim_to_code.html)
- [VOL 03 Completion Reconciliation](vol_03_completion_fact_reconciliation.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)
