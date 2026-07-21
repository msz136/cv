# VOL 03 Source Audit C：ACT CVAE、Action Chunk 与 Temporal Ensemble Claim-to-Code

> 审计日期：2026-07-19  
> 状态：`independent_fact_reviewed / cvae_loss_mask_query_ensemble_checked / local_runtime_pending / WARN`  
> 论文版本：*Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware*，arXiv `2304.13705v1`  
> 官方仓库：`tonyzhaozh/act` frozen commit `742c753c0d4a5d87076c8f69e5628c79a8cc5488`  
> License：MIT  
> 对应题目：`VLA-ACT-011..017`  
> 本页问题：ACT 到底如何用 CVAE-Transformer 一次预测 action chunk？训练期 latent、padding 和 loss 如何实现？不使用 / 使用 temporal ensemble 时，prediction horizon、执行窗口、查询频率和闭环性分别是什么？

## 1. 结论先行

1. **ACT 是连续 action-chunk policy，不是 action tokenizer，也不是带语言输入的 VLA。**论文与 frozen code 的主合同是多视角 RGB + 当前双臂关节位置 → 未来 $H$ 步绝对目标关节位置；该 commit 把 state/action dimension 都硬编码为 14。[1][2]
2. **`chunk_size`、`num_queries` 和模型 prediction horizon 在这份实现里是同一个配置 $H$，但它不自动等于执行窗口。**不开 temporal aggregation 时，代码每 $H$ 步查询一次并顺序执行整段，等价于 $K=H$；开启后每一步查询并融合覆盖当前时刻的多个 chunk，等价于 $K=1$。[2]
3. **训练期 CVAE encoder 只看当前 qpos 与目标 action chunk，不看图像。**输入顺序是 `[CLS] + qpos + H actions`，长度 $H+2$；`[CLS]` 输出产生 posterior 的 `mu/logvar`，再用 reparameterization 得到 32D style latent。[1][2]
4. **推理期不是“从 prior 随机采样风格”。**CVAE encoder 被丢弃，frozen code 把 $z$ 固定为全零，即单位高斯 prior 的均值，因此同一 observation 的输出是确定的。[1][2]
5. **decoder 用一个共享 ResNet18 逐相机提特征，将各相机 feature map 沿宽度拼接，再把 $z$ 与 qpos 作为额外 encoder tokens。**$H$ 个 query slot 经 Transformer decoder 和线性 action head 并行输出 $[B,H,14]$，不是逐步自回归生成。[2]
6. **实际优化目标是 masked elementwise L1 + `kl_weight × KL`。**但源码用 mask 乘零后对完整 $B\times H\times D$ 张量 `.mean()`，分母仍包含 padded slots；它不是按有效元素数重新归一化。`is_pad_head` 虽被定义并前向计算，却没有进入该 commit 的 loss。[2]
7. **论文内部存在 reconstruction loss 表述差异。**Algorithm 1 写 `MSE`，方法正文明确写使用 L1，frozen code 也是 `F.l1_loss`；面试中应以“正文 + 官方实现为 L1，并说明算法框误写/版本差异”为安全口径。[1][2]
8. **temporal ensemble 只融合“不同查询对同一物理时刻的预测”，不是对相邻时刻动作做低通滤波。**论文与代码都把 oldest prediction 排在权重序列首位，并用 $\exp(-mi)$ 使较老预测权重更大；它换来更平滑的动作，但需要每个控制步都做一次 policy inference。[1][2]
9. **ACT 不能替代本地 OpenPiVLA 证据。**ACT 的 14D 绝对 joint target、$H=100$ 示例、50 Hz、CVAE、temporal aggregation 和公开成功率都不能迁移成个人项目的 action schema、horizon、replan 或指标。[1][2]

## 2. 证据层级、冻结对象与适用边界

| 层级 | 本页使用方式 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| arXiv v1 | 方法 Section 4、Algorithms 1/2、Appendix architecture 与 ablation | ACT 的公开动机、CVAE/action-chunk/temporal-ensemble 定义、论文实验 | frozen commit 的精确 tensor/mask 行为；个人项目事实 |
| frozen official repo | commit `742c753...` 的 `detr_vae.py`、`policy.py`、`imitate_episodes.py`、`utils.py` | 张量布局、loss、normalization、query/execute 分支 | 论文未归档的真实机器人外部 `aloha_scripts` 全路径 |
| 同源推断 | 从上述论文与代码联合推导 $H/K$、有效 loss 分母和 row ordering | implementation contract 与安全面试口径 | 未运行的性能、未给出的 controller 语义 |
| 本地项目 | 本页不读取个人项目 raw artifact | 只能提出取证清单 | OpenPiVLA checkpoint、axis order、97.4%、个人贡献 |

冻结信息：

- arXiv API 返回唯一版本 `2304.13705v1`，published/updated 为 `2023-04-23T19:10:53Z`。[1]
- 官方 repo `HEAD` 已核对为 `742c753c0d4a5d87076c8f69e5628c79a8cc5488`，commit date `2024-01-28`；根目录 `LICENSE` 为 MIT。[2]
- 本页审计的是上述历史 commit，不把 2026 年可能存在的 fork、后续 ACT++/ALOHA 2 或第三方重实现混入同一实现结论。

## 3. 任务 I/O 与数据构造

### 3.1 论文中的 real-robot contract

论文 Section 4 将 observation 写成当前 follower joint positions 加 4 路 RGB，相机为 top、front、left wrist、right wrist；action 是下一时刻两个 leader arms 的绝对目标关节位置，共 14D。policy 在当前观测下预测未来 action sequence：[1]

$$
\pi_\theta(a_{t:t+H-1}\mid o_t,z),
\qquad
o_t=(I_t^{1:C},q_t),
\qquad
a_t\in\mathbb{R}^{14}.
$$

变量与直觉：$C$ 是相机数，$q_t\in\mathbb{R}^{14}$ 是当前双臂 joint positions，$H$ 是 chunk/prediction horizon，$z$ 是 CVAE style latent。模型不是只猜 $a_t$，而是一次输出 $H\times14$ 的连续目标关节序列。实现映射：`state_dim=14` 和 `num_queries=chunk_size` 在 [`imitate_episodes.py#L49-L68`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L49-L68)，输出 head 在 [`detr_vae.py#L47-L54`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L47-L54) 与 [`#L131-L139`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L131-L139)。

**边界**：paper 的 real setup 是 4 cameras；frozen repo 自带的 simulation task configs 只有 `camera_names=['top']`，见 [`constants.py#L5-L32`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/constants.py#L5-L32)。真实机器人 task config 来自仓库外部 `aloha_scripts`，因此不能把“此 repo 所有运行默认 4 相机”写成源码事实。

### 3.2 一条训练样本怎样产生

`EpisodicDataset.__getitem__` 随机选择 `start_ts`，只读取该时刻各相机图像和 qpos，并读取从该时刻起的所有 action；尾部不足 episode length 的位置补零并生成 `is_pad`。[2]

| Tensor | frozen code 语义 | 进入 policy 前的 shape |
| --- | --- | --- |
| `image_data` | 当前时刻、按 `camera_names` 堆叠、像素除以 255 | `[C,3,H_img,W_img]` |
| `qpos_data` | 当前关节位置，dataset mean/std 标准化 | `[14]` |
| `action_data` | 从 `start_ts` 起的绝对目标 joint positions，补到 episode length 后标准化 | `[T_episode,14]` |
| `is_pad` | 真实 target 为 `False`，尾部补零为 `True` | `[T_episode]` |

随后 `ACTPolicy` 只截前 `num_queries=H` 个 action 与 mask，所以监督 target 是 `[B,H,14]`，见 [`policy.py#L18-L35`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L18-L35)。完整数据读取、padding 与 normalization 在 [`utils.py#L23-L76`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/utils.py#L23-L76)。

### 3.3 normalization 与执行前反归一化

令训练集每维均值和标准差为 $\mu_q,\sigma_q,\mu_a,\sigma_a$，代码使用：

$$
\tilde q_t=\frac{q_t-\mu_q}{\max(\sigma_q,10^{-2})},
\qquad
\tilde a_{t:t+H-1}=\frac{a_{t:t+H-1}-\mu_a}{\max(\sigma_a,10^{-2})}.
$$

变量与实现：所有量均按 14 个 action/state dimensions 独立统计；标准差下界防止近常数维除零。统计在 [`utils.py#L79-L108`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/utils.py#L79-L108)。该函数在 train/val split 后仍对全部 `num_episodes` 计算统计，见 [`utils.py#L111-L128`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/utils.py#L111-L128)；这是此 commit 的数据边界，不应泛化为严格 holdout normalization recipe。

推理时再做：

$$
\hat a_t=\hat{\tilde a}_t\odot\sigma_a+\mu_a.
$$

代码将反归一化结果直接命名为 `target_qpos` 并传入 `env.step`，见 [`imitate_episodes.py#L267-L273`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L267-L273)。这证明当前实现目标是 joint-position control，不证明任何本地 VLA 的坐标轴、单位或 gripper 语义。

## 4. CVAE encoder：style latent 如何训练、如何消失

### 4.1 posterior 输入不是完整 observation

训练时 encoder 输入序列为：

```text
[CLS] learned token       [B, 1, D]
current qpos projection   [B, 1, D]
target action projection  [B, H, D]
             concatenate → [B, H+2, D]
                              │
                              v
                 Transformer encoder
                              │ take CLS output
                              v
                mu, logvar ∈ R^[B,32]
```

论文明确说明为加速训练，CVAE encoder 不输入图像，只条件于 proprioception 和 target action sequence；Appendix 又给出 `[CLS] + joints + actions` 的 $H+2$ 布局。[1] 代码逐行对应 [`detr_vae.py#L66-L110`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L66-L110)。源码的局部 shape comment 写过 `seq+1`，但实际 `cat` 和 position table 都是 `H+2`；面试应以操作和论文附录为准。

posterior 写为：

$$
q_\phi(z\mid q_t,a_{t:t+H-1})
=\mathcal N\!\left(\mu_\phi,\operatorname{diag}(\exp(\ell_\phi))\right),
\qquad z=\mu_\phi+\exp(\!\tfrac12\ell_\phi)\odot\epsilon,
\quad\epsilon\sim\mathcal N(0,I).
$$

变量与直觉：$\ell_\phi$ 是 `logvar`，$z\in\mathbb{R}^{32}$。target action chunk 帮助 encoder 把人类 demonstration 的风格/多模态因素压进 latent；reparameterization 让梯度通过采样。代码映射：[`reparametrize#L17-L20`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L17-L20) 与 [`DETRVAE.forward#L85-L110`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L85-L110)。

`is_pad` 在 posterior encoder 中作为 `src_key_padding_mask`，并在前面补两个恒为 `False` 的 CLS/qpos mask，因此 padded future actions 不参与 self-attention，见 [`detr_vae.py#L97-L105`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L97-L105)。

### 4.2 推理为什么固定 $z=0$

当 `actions is None` 时，代码不运行 posterior encoder，而是：

$$
z_{test}=0=\mathbb E_{p(z)}[z],
\qquad p(z)=\mathcal N(0,I).
$$

变量与直觉：$z_{test}$ 是 prior mean，不是一次随机 sample。这样部署输出可重复，但训练期 CVAE 的“能表达多种 demonstration style”不等于测试时会主动探索多模态轨迹。论文 Appendix 明确称该选择使 evaluation deterministic；代码在 [`detr_vae.py#L111-L115`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L111-L115) 和 [`policy.py#L36-L38`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L36-L38) 对齐。

**面试防线**：不要说“ACT 推理时从 CVAE 随机采样多个 action chunk 再选一个”；此 frozen path 只用一个零 latent、一次 deterministic forward。

## 5. CVAE decoder：相机、qpos、latent 和 action queries 怎样汇合

### 5.1 observation encoder

每个相机图像先经过同一个 `backbones[0]`；得到的 feature maps 和 2D position embeddings 沿 width 维拼接。然后将 projected latent 与 projected qpos 作为两个额外 token 放在图像 tokens 前面：

```python
def act_decode(images, qpos, z, action_queries):
    # All cameras reuse the same ResNet18 weights in this frozen commit.
    camera_features = [shared_resnet(img) for img in images]

    # Concatenate camera feature maps along the spatial-width axis.
    visual_memory = concat_width(camera_features)

    # Prepend projected style and proprioception as two encoder tokens.
    memory_input = prepend(project(z), project(qpos), visual_memory)

    # Decode H learned query slots in parallel; no autoregressive token loop.
    hidden = transformer(memory_input, queries=action_queries)
    return linear_action_head(hidden)  # [B, H, 14]
```

实现链：相机共享 backbone 与 width concat 在 [`detr_vae.py#L116-L131`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L116-L131)；latent/qpos prepend 与图像 flatten 在 [`transformer.py#L49-L77`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/transformer.py#L49-L77)。图像在 dataset 先除 255，进入 policy 后再做 ImageNet mean/std normalize，见 [`policy.py#L18-L23`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L18-L23)。

### 5.2 $H$ 个 query slot 是并行输出槽

模型定义 `query_embed = nn.Embedding(num_queries, hidden_dim)`；decoder 的零初始 target 叠加这些 learned query positions，并对 encoder memory 做 cross-attention。最终 `action_head` 对每个 query 输出一个 14D action，因此：

$$
\operatorname{ACT}_\theta(o_t,z)
=\left(\hat a_t^{(t)},\hat a_{t+1}^{(t)},\ldots,
\hat a_{t+H-1}^{(t)}\right)
\in\mathbb R^{H\times14}.
$$

变量与记号：上标 $(t)$ 表示“在 query time $t$ 做出的预测”，下标表示它要执行的物理时刻。实现映射：query/action heads 在 [`detr_vae.py#L47-L54`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py#L47-L54)，Transformer decoder 的 self-/cross-attention 在 [`transformer.py#L204-L250`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/transformer.py#L204-L250)。

**paper/code boundary**：论文正文/Appendix 把 query 描述为 fixed position / sinusoidal embeddings；此 commit 明确使用可学习 `nn.Embedding`。二者不能在实现面试中混成“代码使用固定正弦 action queries”。

### 5.3 `is_pad_head` 不能被讲成已训练终止头

模型同时定义 `is_pad_head = nn.Linear(hidden_dim,1)` 并返回 `is_pad_hat`，但 `ACTPolicy` 不计算它的 BCE/CE，也不在推理使用它。因而本 commit 的 chunk 长度由固定 `H=num_queries` 决定；有效尾部依赖 dataset `is_pad` mask 训练，而不是由模型预测动态停止。[2]

## 6. 训练目标、padding mask 与 paper/code 差异

### 6.1 frozen code 的 reconstruction loss

令 $p_{b,h}\in\{0,1\}$ 表示 target slot 是否为 padding，$D_a=14$。源码的精确 L1 为：

$$
\mathcal L_{L1}^{code}
=\frac{1}{BHD_a}
\sum_{b=1}^{B}\sum_{h=1}^{H}\sum_{d=1}^{D_a}
(1-p_{b,h})\left|a_{b,h,d}-\hat a_{b,h,d}\right|.
$$

变量与直觉：mask 确实让 padded target 的 numerator 为零；但随后 `.mean()` 仍除以完整 $BHD_a$，而不是 $D_a\sum_{b,h}(1-p_{b,h})$。所以靠近 episode 尾部、valid slots 较少的样本，其 reconstruction contribution 会被额外缩小。直接证据是 [`policy.py#L23-L34`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L23-L34)。

这与常见的 valid-count normalization 不同：

$$
\mathcal L_{L1}^{valid}
=\frac{
\sum_{b,h,d}(1-p_{b,h})|a_{b,h,d}-\hat a_{b,h,d}|
}{D_a\sum_{b,h}(1-p_{b,h})+\epsilon}.
$$

此式只作为对照，并不是 frozen code。它说明“有 loss mask”与“按有效 token/action 数无偏归一化”是两个独立问题；面试中不能看到 `~is_pad` 就默认后者成立。

### 6.2 KL 与总 loss

posterior 对单位高斯 prior 的 KL 实现为：

$$
\mathcal L_{KL}
=\frac{1}{B}\sum_{b=1}^{B}\frac12
\sum_{j=1}^{32}
\left(\mu_{b,j}^2+\exp(\ell_{b,j})-1-\ell_{b,j}\right),
$$

$$
\mathcal L_{ACT}
=\mathcal L_{L1}^{code}+\beta\mathcal L_{KL}.
$$

变量与实现：$j$ 遍历 32D latent，$\ell$ 是 `logvar`，$\beta$ 对应 CLI/config 的 `kl_weight`。KL 在 [`policy.py#L71-L84`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L71-L84)，总 loss 在 [`policy.py#L27-L35`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py#L27-L35)。README 示例和论文 hyperparameter table 都使用 `kl_weight/beta=10`、`chunk_size=100`，但它们是公开 recipe，不是跨任务最优常数。[1][2]

### 6.3 论文 Algorithm 1 的 MSE 不等于实际代码

| 位置 | reconstruction 表述 | 判定 |
| --- | --- | --- |
| Paper Algorithm 1 | `MSE(a_hat, a)` | 论文算法框原文 |
| Paper Section 4.3 / line after architecture | “We use L1 loss ... instead of L2” | 论文方法正文 |
| Frozen `policy.py` | `F.l1_loss(..., reduction='none')` | 实际审计实现 |

因此安全表述是：“ACT v1 论文算法框存在 MSE/L1 不一致；方法正文和 commit `742c753...` 的训练路径使用 masked L1，再加 beta-weighted KL。”不要只背算法框，也不要删掉版本差异。

## 7. Horizon、执行窗口、replan 与 temporal ensemble

### 7.1 四个容易混淆的量

| 量 | 本页记号 | ACT frozen code | 含义 |
| --- | --- | --- | --- |
| Prediction horizon / chunk size | $H$ | `policy_config['num_queries']` | 一次 forward 输出多少个未来 action slots |
| Execution window | $K$ | 无独立 CLI 参数 | 一次 query 后实际连续执行多少步才使用新观测重新规划 |
| Query/replan interval | $R$ | `query_frequency` | 两次 policy inference 相隔多少 control steps |
| Control period | $\Delta t$ | sim `DT=0.02` | 环境/机器人执行一步的物理周期；不是模型 horizon |

此 commit 中 $K$ 与 $R$ 被 rollout 分支绑在一起，但概念上仍应分开：不开 ensemble 时 $K=R=H$；开 ensemble 时 $K=R=1$。模型 $H$ 在两种模式中不变。

### 7.2 模式 A：整段执行

默认 `temporal_agg=False` 时：

```python
# Query once at t = 0, H, 2H, ...
if t % H == 0:
    chunk = policy(qpos_t, image_t)  # [1, H, 14]

# Execute every predicted action in order before the next policy query.
raw_action = chunk[:, t % H]
```

这对应 [`imitate_episodes.py#L191-L194`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L191-L194) 与 [`#L246-L261`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L246-L261)。它不是“一次输出 H 步，因此整个 episode 永远 open-loop”；更准确地说，**每个 chunk 内不吸收新 observation，chunk 边界重新闭环**。只有 $H=T_{episode}$ 时才退化为整条 episode open-loop。

### 7.3 模式 B：每步查询 + overlapping-chunk ensemble

开启 `temporal_agg=True` 后，`query_frequency` 被改为 1。query time $q$ 产生对未来时刻 $t$ 的预测 $\hat a_t^{(q)}$；对当前时刻 $t$，有效 query 集为：

$$
\mathcal Q_t
=\{q\mid \max(0,t-H+1)\le q\le t\}.
$$

变量与直觉：最多有 $H$ 个历史 chunk 覆盖当前时刻，且它们都在预测**同一个 $a_t$**。代码将每次输出写入 `all_time_actions[q, q:q+H]`，再读取 column `t`，见 [`imitate_episodes.py#L217-L254`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L217-L254)。

按 oldest-to-newest 排序 $q_0<q_1<\cdots<q_{n-1}$ 后：

$$
w_i=\exp(-mi),
\qquad
a_t^{exec}
=\frac{\sum_{i=0}^{n-1}w_i\hat a_t^{(q_i)}}
{\sum_{i=0}^{n-1}w_i}.
$$

变量与实现：$m$ 是 decay rate；论文明确 $w_0$ 对应 oldest action，代码 row 过滤后仍保持 query-time 升序，并固定 `m/k=0.01`，见 [`imitate_episodes.py#L251-L259`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py#L251-L259)。因此较旧预测权重最大；$m$ 越小权重越平，新的 observation 相对占比越高。

**不是相邻时刻平滑**：它没有把 $a_{t-1},a_t,a_{t+1}$ 混在一起，而是把多个 `query time` 对同一 target time $t$ 的估计做 ensemble，避免普通时域 smoothing 引入时间偏移。

### 7.4 rollout 伪代码

```python
def act_rollout(env, policy, stats, horizon, temporal_agg):
    # Reset environment; qpos and images are the current observation only.
    ts = env.reset()
    prediction_table = {}  # target_time -> predictions ordered oldest to newest

    for t in range(env.max_steps):
        # Normalize qpos/images exactly as in training.
        qpos_t, images_t = preprocess(ts.observation, stats)

        if temporal_agg:
            # Replan every control step while keeping model horizon H unchanged.
            chunk = policy(qpos_t, images_t)  # deterministic z=0, [H, 14]
            for offset, pred in enumerate(chunk):
                prediction_table.setdefault(t + offset, []).append(pred)

            # Fuse predictions for the same physical target time, oldest first.
            normalized_action = exponential_ensemble(prediction_table[t], m=0.01)
        else:
            # Query every H steps, then execute the entire cached chunk.
            if t % horizon == 0:
                chunk = policy(qpos_t, images_t)
            normalized_action = chunk[t % horizon]

        # Recover absolute target joint positions and execute one control step.
        target_qpos = denormalize_action(normalized_action, stats)
        ts = env.step(target_qpos)
```

这段伪代码表达 frozen rollout 的信息流，不声称是逐行可运行复制。真实代码还以全零 tensor 作为“尚未填充”的 sentinel，并通过 `torch.all(action != 0)` 判断有效行；若模型恰好输出含精确零分量的 normalized action，该行可能被误判为空。它是此 commit 的实现风险，不等于论文方法必须如此设计。[2]

## 8. Chunk 长短、闭环性、延迟与吞吐的 trade-off

### 8.1 $H$ 太短

- $H=1$ 是单步 policy：每个控制步都要查询，反馈最及时，但长任务的有效决策 horizon 最大，行为更容易受局部预测噪声和 compounding error 影响。[1]
- inference 次数约为 $T/H$；无 temporal ensemble 时 $H$ 越小，单位 episode 的 policy calls 越多，吞吐压力越高。
- 单步输出缺少 chunk-level sequence coherence，难以利用一个 demonstration 片段中持续动作/暂停等 temporal structure。

### 8.2 $H$ 太长

- 不 replanning 时，新的 observation 最多要等 $H$ 个 control steps 才被吸收；环境扰动或早期 action error 会让 chunk 后半段 stale。
- 长序列更难建模，decoder query 数增加；可推断地，query self-attention 与 cross-attention 的计算/显存负担也会随 $H$ 增加，但本页没有做 runtime benchmark。
- 论文在四个 simulation/data settings、关闭 temporal ensemble 的 ablation 中报告：平均 success 从 $H=1$ 的 1% 升到 $H=100$ 的 44%，更长的 200/400 又轻微下降；作者归因于反应性不足与长序列建模困难。[1] **这不是“100 对所有机器人最优”的证据。**

### 8.3 temporal ensemble 的额外取舍

| 收益 | 代价 / 风险 |
| --- | --- |
| 每步吸收新 observation，避免只在 chunk 边界突变 | policy inference 从每 $H$ 步一次变为每步一次 |
| 融合相同 target time 的多次估计，减少模型噪声 | oldest prediction 权重最大，快速变化场景可能保留 stale plan |
| 不增加训练成本 | 需要维护 overlapping prediction buffer；实现 sentinel/mask 要可靠 |
| 动作更平滑且无相邻时刻平均的 phase bias | 平滑不等于安全，仍可能把多个一致但错误的预测融合 |

论文报告 temporal ensemble 对 ACT 的平均增益约 3.3%，但相应实验 separately tuned；因此它是该论文协议内的 ablation，不应直接迁移为本地成功率预期。[1]

## 9. ACT 与 token、Diffusion / Flow 路线的归纳偏置

| 路线 | Action 表示 / 目标 | 生成方式 | 主要归纳偏置 | 本页边界 |
| --- | --- | --- | --- | --- |
| ACT | 标准化连续 $H\times D_a$；masked L1 + CVAE KL | $H$ 个 learned queries 一次并行回归；test $z=0$ | chunk coherence、低 inference step 数、训练期 latent regularization | 本页 paper/code verified |
| OpenVLA scalar token | 每个 action scalar 离散为 token；next-token CE | 自回归生成一个当前动作的各维 token | 复用 LM vocabulary/objective，量化连续值 | 见 [OpenVLA audit](vol_03_openvla_claim_to_code.html) |
| FAST token | action window 频域变换、量化、BPE；masked token CE | 自回归生成压缩后的 action tokens | 利用机器人轨迹的时频结构和重复模式 | 见 [π0/FAST/openpi audit](vol_03_pi0_fast_openpi_claim_to_code.html) |
| π0 flow action | noisy continuous action chunk 上的 velocity MSE | 多步 ODE/Euler integration | 连续多模态生成、VLM context + action expert | 见 [π0/FAST/openpi audit](vol_03_pi0_fast_openpi_claim_to_code.html) |
| Diffusion Policy | noisy continuous action trajectory 的 epsilon/sample MSE | scheduler 多步去噪；$T_o/T_p/T_a$ 分离 | 见 [Diffusion Policy audit](vol_03_diffusion_policy_claim_to_code.html) | source-ready / WARN |

选择时不能只问“谁更先进”，而应问：

1. action 是否需要离散 token 与语言模型统一接口；
2. 是否需要显式多模态生成，还是允许 deterministic prior-mean deployment；
3. 一次 forward 的低延迟是否比 iterative generation 更重要；
4. $H$、$K$、controller frequency 和 observation latency 如何共同决定闭环；
5. 数据量、动作平滑性、action axes 与 normalization 是否和该表示匹配。

## 10. Claim-to-code 总表

| Claim | 论文证据 | frozen code 证据 | 判定 | 面试口径 |
| --- | --- | --- | --- | --- |
| ACT 输入 language instruction | 无 | 无 text encoder/input | rejected | ACT 本身是 visuomotor imitation policy，不是 VLA |
| 一次输出未来 $H$ 步连续 joint targets | Section 4.3 | `num_queries` + `action_head` | direct | `[B,H,14]`，并行 query slots |
| $H$ 自动等于执行窗口 | 论文区分 naive chunk 与 per-step ensemble | rollout 有两分支 | rejected | 模型 horizon 与执行/重规划分开报 |
| posterior encoder 输入 RGB | Section 4.2 明确省略 image | 只 project qpos/actions | rejected | encoder 看 `[CLS]+qpos+target chunk` |
| 推理从 prior 随机采样 $z$ | Appendix 明确设零 | zero tensor | rejected | test $z=0$，deterministic |
| 代码用固定正弦 action queries | paper 如此描述 | `nn.Embedding` | paper/code mismatch | 此 commit 是 learned queries |
| 实际 reconstruction 是 MSE | Algorithm 1 写 MSE；正文写 L1 | `F.l1_loss` | mismatch, code=L1 | 报版本差异，训练路径按 L1 |
| padded targets 完全按有效数归一化 | 未给实现分母 | mask 后完整 `.mean()` | rejected | numerator masked，denominator 含 padded slots |
| `is_pad_head` 是训练好的 stop head | 无此 claim | head 返回但不进 loss | rejected | 固定长度 chunk；不要称动态 stop |
| temporal ensemble 平均相邻时刻动作 | 明确否定 | 读取 prediction table 同一 column | rejected | 融合不同 query 对同一 target time 的预测 |
| 新预测权重最大 | paper $w_0$ oldest | row 旧→新，exp 衰减 | rejected | oldest prediction 权重最大 |
| 不开 ensemble 就完全不是闭环 | chunk boundary 接收新 observation | 每 $H$ 步 query | rejected | chunk 内 open-loop、边界闭环 |
| 开 ensemble 不增加成本 | 仅称无额外 training cost | inference 每步一次 | rejected | training 不变，inference 更贵 |
| 论文 4 cameras 是 sim repo 默认 | real paper 4 view | sim config top-only | rejected as universal | 报具体 task/config |
| ACT 公开结果证明本地 OpenPiVLA | 无 | 无 | rejected | 另做本地 artifact contract |

## 11. 对 `VLA-ACT-011..017` 的支持状态

| Question ID | 本页覆盖 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ACT-011 | $H/K/R/\Delta t$ 定义与两个 rollout 分支 | source-ready | 本地 OpenPiVLA 的实际 H/K/config |
| VLA-ACT-012 | CVAE encoder、decoder、queries、shape 与 loss | source-ready | 独立事实审查 |
| VLA-ACT-013 | posterior/reparameterization、test $z=0$ | source-ready | 真实口述训练 |
| VLA-ACT-014 | same-target-time exponential ensemble、weight ordering | source-ready with warning | sentinel edge-case test |
| VLA-ACT-015 | chunk 内/边界闭环、per-step replan 与 ensemble | source-ready | 更一般 rollout abstraction 的项目映射 |
| VLA-ACT-016 | $H$ 长短、calls、staleness、论文 ablation | source-ready | 本地 latency/profile 与控制频率 |
| VLA-ACT-017 | ACT 对 OpenVLA/FAST/π0 的归纳偏置 | partial/source-ready | Diffusion Policy 独立 source batch |

`source-ready` 只表示可据来源写后续题卡，不表示候选人已掌握；题卡生成后仍必须保持 `unseen`，直到真实口述。

## 12. 与个人项目的真实性边界

| ACT 上游事实 | 可以怎样帮助 OpenPiVLA 面试 | 不能怎样迁移 |
| --- | --- | --- |
| $H=num_queries$ 输出 chunk | 用作区分 model horizon / execution prefix / replan 的反例 | 不能证明本地 `horizon=10` 或执行几步 |
| mean/std action normalization | 提醒 checkpoint、stats 与 controller 必须匹配 | 不能替代本地 q01/q99 / norm asset |
| 14D absolute joint targets | 作为 action schema 需要显式报告的例子 | 不能推断本地 axis/order/unit |
| temporal aggregation $K=1$ | 帮助解释“chunk policy 仍可逐步闭环” | 不能声称本地使用 ACT ensemble |
| masked L1 + KL | 训练 objective 的对照 | 不能证明本地 token CE / flow loss |
| paper ablation / public success | 说明方法在特定协议的观察 | 不能支撑本地 97.4% 或个人贡献 |

进入项目强回答前仍需本地取证：model class/checkpoint、action dimension 与 axis order、normalization stats、model horizon $H$、执行前缀 $K$、policy query 条件、controller frequency、rollout task/trial/split/seed、success predicate 与 eval summary。

## 13. 面试安全口径与危险答案

### 13.1 30 秒安全骨架

“ACT 把单步行为克隆改成连续 action chunk 预测。训练时，一个 CVAE encoder 用当前 qpos 和未来动作段推断 style latent，decoder 再结合多视角图像、qpos 和 latent，用 $H$ 个 Transformer queries 并行回归 $H\times14$ 的绝对 joint targets；loss 在官方实现里是 masked L1 加 beta-KL。推理时 encoder 丢弃并固定 $z=0$。不开 temporal ensemble 时每 $H$ 步重规划；开启后每步查询，并对不同 chunk 预测的同一时刻动作做指数加权，所以 prediction horizon 与 execution/replan interval 不能混为一谈。”

### 13.2 高危说法

- “ACT 就是把 action token 一次生成 100 个。”——它输出连续向量，不是 token。
- “CVAE 推理时随机采样，所以每次轨迹不同。”——此官方路径固定 $z=0$。
- “chunk size 100 就代表机器人 100 步都不看图。”——只适用于不开 temporal ensemble 的整段执行分支。
- “temporal ensemble 对最近预测权重最大。”——论文与代码的序列约定恰好是 oldest 最大。
- “mask 后 loss 就严格只除 valid slots。”——源码 denominator 仍含 padded slots。
- “论文说 MSE，所以代码也是 MSE。”——正文和 frozen code 是 L1。
- “ACT 的 80M、50Hz、4 相机、14D 都是所有 action-chunk policy 的定义。”——这些是特定论文/实现配置。
- “ACT 证明我的 OpenPiVLA 采用了 action chunking 并得到 97.4%。”——缺本地 artifact。

## 14. 风险、未决项与下一步

1. **核心高风险事实已独立复核**：ACT CVAE、L1/KL、padding denominator、learned query、temporal ensemble ordering、sentinel 与 H/K/R 已在 [独立复核页](vol_03_act_independent_fact_review.html) 直接核对，公共事实层为 `PASS WITH WARNING`；local project artifacts、controller、ownership 与 oral drill 仍使本页整体保持 `WARN/PENDING`。
2. **视觉 QA 已完成**：通过 localhost 静态服务检查桌面 `1440×1000` 与窄屏 `800×1000`；确认一处 H1、academic palette/serif、desktop sticky TOC、narrow static TOC、公式无 `<em>` 污染且无页面级横向溢出。
3. **paper/code mismatch 必须保留**：MSE/L1、fixed/sinusoidal query vs learned embedding 都不应被“统一润色”掉。
4. **mask 需要测试**：可用不同 valid lengths 的合成 batch 验证 `.mean()` 缩放；本页当前是逐行确定的代码结论，尚未执行单元测试。
5. **temporal table sentinel 需要测试**：精确零 action component 的有效行可能被 `torch.all(... != 0)` 过滤；不把它夸大为公开论文失败原因。
6. **VLA-ACT-017 仍有缺口**：Diffusion Policy 已完成 source freeze；仍需基础 Flow Matching 独立审计，才能完成 ACT / token / diffusion / flow 的严格对比。
7. **本地项目仍待取证**：ACT upstream 只进入知识与面试对照，不进入个人贡献或指标证明。

## 参考文献（References）

1. Zhao et al., [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/html/2304.13705v1), arXiv `2304.13705v1`, 2023；[arXiv abs/API version entry](https://arxiv.org/abs/2304.13705v1)。
2. Tony Z. Zhao et al., [tonyzhaozh/act](https://github.com/tonyzhaozh/act/tree/742c753c0d4a5d87076c8f69e5628c79a8cc5488), frozen commit `742c753c0d4a5d87076c8f69e5628c79a8cc5488`, MIT License；核心路径：[`detr/models/detr_vae.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/detr_vae.py)、[`detr/models/transformer.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/detr/models/transformer.py)、[`policy.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/policy.py)、[`imitate_episodes.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/imitate_episodes.py)、[`utils.py`](https://github.com/tonyzhaozh/act/blob/742c753c0d4a5d87076c8f69e5628c79a8cc5488/utils.py)。
3. [VOL 03 OpenVLA Action Token 与 I/O Claim-to-Code](vol_03_openvla_claim_to_code.html)，本仓库 Source Audit A，2026-07-16。
4. [VOL 03 π0 / π0.5 / FAST / openpi Claim-to-Code](vol_03_pi0_fast_openpi_claim_to_code.html)，本仓库 Source Audit B，2026-07-16。
5. [VOL 03 Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Claim-to-Code](vol_03_diffusion_policy_claim_to_code.html)，本仓库 Source Audit D，2026-07-16。
6. [VOL 03 ACT CVAE / Action Chunk / Temporal Ensemble 独立事实复核](vol_03_act_independent_fact_review.html)，本仓库二次 paper/frozen-code 复核与 synthetic probes，2026-07-19。
