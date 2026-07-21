# VOL 03 Source Audit B：π0 / π0.5 / FAST / openpi Claim-to-Code

> 审计日期：2026-07-19  
> 状态：independent_fact_reviewed / pi05_fast_norm_rollout_checked / local_runtime_pending / WARN  
> 论文版本：π0 arXiv 2410.24164v4；π0.5 arXiv 2504.16054v1；FAST arXiv 2501.09747v1  
> 官方仓库：Physical-Intelligence/openpi frozen commit 15a9616a00943ada6c20a0f158e3adb39df2ccac  
> FAST Hub：physical-intelligence/fast frozen revision ec4d7aa71691cac0b8bed6942be45684db2110f4  
> 对应题目：VLA-ARCH-002..004、006、008、010..012；VLA-ACT-001..002、005..008、010..011、023..025、027..028、031..032  
> 本页问题：π0 的连续 flow action expert、π0.5 的混合训练、π0-FAST 的自回归 token 路线以及 openpi 的 normalization / rollout 到底如何连接？哪些公开事实仍不能证明本地 OpenPiVLA？

## 1. 结论先行

1. **π0 的公开主路径是多图 + 语言 + proprioception → 连续 action chunk**。论文使用 2–3 张 RGB、语言命令与关节状态，预测长度 50 的动作块；冻结 openpi 默认配置则给出 3 个图像槽、32 维 model action space 和 H=50 的张量合同。[P1][R1]
2. **π0 的 action expert 学的是 flow velocity，不是 action token CE**。论文从 noise time 0 积分到 data time 1；openpi 采用相反但等价的时间参数，从 t=1 的 noise 以负步长积分到 t=0 的 data，默认 10 步。[P1][R1]
3. **π0.5 论文不是简单的“π0 改了 state token”**。论文预训练时用 FAST action token 做 autoregressive next-token prediction，post-training 再加入连续 action expert，并联合优化 token CE 与 flow loss；推理用文本自回归输出后接 10 步 flow sampling。[P2]
4. **冻结 openpi 的 Pi0(pi05=True) 只直接实现 flow loss**。它确实把 state 放进离散 prompt token，并用 adaRMSNorm 注入 flow timestep，但 compute_loss 没有 π0.5 论文的 FAST action-token CE 分支。不能说该 commit 完整复现了论文的 hybrid pre-training objective。[R1]
5. **openpi 的 Pi0FAST 是另一条独立自回归路线**。它把 prompt、离散 state 和 FAST actions 排成 prefix/postfix token sequence，只对 postfix 做 next-token CE，推理逐 token 生成后再通过 FAST decoder 恢复 H×D 连续动作。[R1]
6. **FAST 的算法顺序是 quantile normalization → per-dimension temporal DCT → scale-and-round → frequency-first flatten → BPE**。BPE 是唯一 learned component；DCT 和反 DCT 是解析变换。官方 Hub processor 本身不做 normalization，调用者必须先把动作处理到合适尺度。[P3][H1]
7. **论文默认值、Hub tokenizer 与 model config 不是同一个“默认”**。FAST 单数据集实验使用 scale=10、BPE vocab=1024；冻结 FAST+ Hub processor 是 scale=10、vocab=2048；openpi 的 Pi0FASTConfig 默认 H=32、D=32，而 LIBERO 示例配置显式改为 H=10、D=7。[P3][H1][R1]
8. **model horizon、executed prefix 与 replan interval 必须分开**。openpi LIBERO client 默认每次取 chunk 的前 K=5 步执行后重新推理；ActionChunkBroker 则可把整个 action horizon 逐步消费完才请求新 chunk。H 和 K 不是同一参数。[R1]
9. **normalization stats 是 checkpoint contract，不是可选装饰**。policy 构造时从 checkpoint assets 取训练期 stats；推理 pipeline 在 sample 前 normalize、sample 后 unnormalize，再做 dataset-specific output slicing。[R1]
10. **以上仍不能证明本地 OpenPiVLA 的 97.4%、Qwen JSON/token、horizon 10 或个人贡献**。这些必须由本地 checkpoint、config、diff、norm stats、rollout client 与 eval summary 建立独立 artifact manifest。

## 2. 证据层级与冻结边界

| 层级 | 冻结对象 | 本页能支持 | 本页不能支持 |
| --- | --- | --- | --- |
| 论文 | π0 v4、π0.5 v1、FAST v1 | 方法定义、论文约定、公开训练/推理路线 | 某个未来 commit 或本地 fork 的逐行行为 |
| official repo | openpi commit 15a9616...，Apache-2.0 | JAX model、transform、policy、LIBERO client 的当前实现 | 论文未发布的训练数据；本地项目实际采用情况 |
| official model artifact | FAST Hub revision ec4d7aa...，Apache-2.0 | processor 源码、scale、vocab、DCT/BPE encode/decode | openpi checkpoint 是否固定加载了该 revision |
| 同源推断 | paper ↔ frozen code 对照 | 时间约定等价、shape 流、mask 语义 | local run 的 checkpoint、指标、axis/order |
| 本地项目材料 | 03_openpivla_action_modeling.html | 待核对 claim 与项目口述入口 | 缺 raw config/log/diff 时的强归因 |

冻结 openpi commit 的提交时间为 2026-06-16T00:14:00Z。本页所有 GitHub 代码链接都固定到该 commit；FAST Hub 链接固定到 revision ec4d7aa...。访问日期均为 2026-07-16。

## 3. π0 的 observation、action chunk 与 action expert

### 3.1 论文 I/O 合同

令批大小为 B，图像数为 n，动作维数为 D，预测长度为 H。π0 论文把观测和动作块写成：

\[
o_t=[I_t^1,\ldots,I_t^n,\ell_t,q_t],\qquad
A_t=[a_t,a_{t+1},\ldots,a_{t+H-1}].
\]

变量与直觉：每个 \(I_t^i\) 是当前时刻的一路 RGB，\(\ell_t\) 是语言 token，\(q_t\in\mathbb{R}^{D_q}\) 是 proprioceptive joint state，\(A_t\in\mathbb{R}^{H\times D}\) 是未来动作块。论文实验使用 n=2 或 3、H=50。[P1]

实现映射：冻结 openpi 的 Pi0Config 默认 D=32、H=50，输入规格有 base_0_rgb、left_wrist_0_rgb、right_wrist_0_rgb 三个 image slot，state shape 为 [B,32]，action shape 为 [B,50,32]。[R1]

这不是“每个机器人天然都有 32 个执行轴”。32 是 model-side unified dimension；真实机器人可使用较少维度，再通过 padding 和 output transform 恢复 dataset contract。

### 3.2 prefix / suffix 信息流

冻结代码把 π0 分成两个 token group：

```text
# Information-flow sketch: prefix is cached; suffix changes with flow time.
prefix: image tokens from each valid view + language tokens
    │
    ├── cached once during sampling
    │
suffix: one continuous state token + H noisy-action tokens
    │
    └── recomputed at every flow integration step
             ↓
      action_out_proj → velocity [B,H,D]
```

该代码块的注释含义：prefix 提供视觉语言条件；suffix 承载随 flow time 改变的动作状态。采样时 prefix 的 KV cache 只计算一次，每个 Euler step 只重算 suffix。[R1]

π0 的 image/language prefix 内部是 full attention；suffix 的 H 个 action tokens 在同一 action block 内可互相注意。论文明确称 action expert 对 action tokens 使用 full bidirectional attention，因此一次建模整个 chunk，而不是按时间步自回归生成。[P1]

### 3.3 backbone 与 action expert

论文和冻结配置都把 PaliGemma 视觉语言模块与较小 action expert 配对：PaliGemma 侧使用 2B Gemma 变体，action expert 约 300M。冻结代码以 action_in_proj 将 D 维 noisy action 映射到 expert width，再以 action_out_proj 返回 D 维 velocity。[P1][R1]

面试安全说法：

- VLM backbone 负责把图像与语言变成条件 context。
- action expert 负责在这个 context 下建模连续 H×D noisy action 的 velocity field。
- controller 不在 action expert 内；output transform、axis/unit conversion、replan queue 与 env.step 属于 policy/eval interface。

## 4. Flow Matching：论文约定与代码约定为什么等价

### 4.1 π0 论文约定

令真实动作块为 \(A\in\mathbb{R}^{B\times H\times D}\)，高斯噪声为 \(\epsilon\sim\mathcal{N}(0,I)\)，论文时间为 \(\tau\in[0,1]\)。线性 probability path 为：

\[
A^\tau=\tau A+(1-\tau)\epsilon,\qquad
u_{\mathrm{paper}}=A-\epsilon.
\]

变量与直觉：\(\tau=0\) 是 noise，\(\tau=1\) 是 data；沿直线路径的目标 velocity 不随 \(\tau\) 改变。π0 用网络 \(v_\theta(A^\tau,o)\) 预测该速度。[P1]

训练目标为：

\[
\mathcal{L}_{\mathrm{flow}}
=
\mathbb{E}_{A,o,\epsilon,\tau}
\left[
\frac{1}{HD}
\left\|
v_\theta(A^\tau,o)-(A-\epsilon)
\right\|_2^2
\right].
\]

变量与实现含义：平方误差先作用于每个 action dimension；论文公式写总体范数，冻结 model 的 compute_loss 先在 D 维取 mean，训练脚本再对 batch 与 H 取 mean，最终等价于对有效 [B,H,D] 元素求平均。该公式只描述公开 π0 路径；若真实项目对 padding 维做 mask，则必须额外写出 mask 来源。[P1][R1]

### 4.2 openpi 代码约定

冻结代码直接写：

\[
x_t=t\epsilon+(1-t)A,\qquad
u_{\mathrm{code}}=\epsilon-A,
\quad t\in[0,1].
\]

代码从 t=1 的 noise 出发，以 \(dt=-1/N\) 迭代到 t=0 的 data：

\[
x_{t+dt}=x_t+dt\,v_{\theta}^{\mathrm{code}}(x_t,o),
\qquad N=10\ \text{by default}.
\]

变量与实现映射：noise shape 为 [B,H,D]；num_steps 默认 10；prefix KV 先缓存，suffix 在每一步重算；最终返回 x_0。对应 Pi0.compute_loss 与 Pi0.sample_actions。[R1]

### 4.3 等价变量替换

令论文时间 \(s=1-t\)，则：

\[
x_{\mathrm{code}}(t)
=t\epsilon+(1-t)A
=sA+(1-s)\epsilon
=x_{\mathrm{paper}}(s),
\]

\[
u_{\mathrm{code}}=\epsilon-A=-u_{\mathrm{paper}},
\qquad ds=-dt.
\]

因此 \(v_{\mathrm{code}}=-v_{\mathrm{paper}}\)，而 \(v_{\mathrm{code}}dt=v_{\mathrm{paper}}ds\)。直觉上，代码把时间轴和速度方向同时翻转，轨迹上的点与最终 data endpoint 不变。冻结源码还直接注释其 convention 与 π0 paper 相反。[R1]

面试中不要只说“一个从 0 到 1，一个从 1 到 0”；必须补上 target velocity 也取反，否则会被追问为什么 ODE 仍然等价。

## 5. π0 与 π0.5：论文差异、代码差异和未覆盖项

### 5.1 π0.5 论文的 hybrid objective

π0.5 论文将同一 action supervision 同时表示为：

- FAST 离散 action tokens，由大 VLM 自回归预测；
- 连续 noisy action chunk，由小 action expert 做 flow matching。

论文联合目标可概括为：

\[
\mathcal{L}_{\pi_{0.5}}
=
\mathcal{H}\!\left(x_{1:M},f_\theta^\ell(o,\ell)\right)
+
\alpha
\left\|
\omega-A-f_\theta^a(A^{\tau,\omega},o,\ell)
\right\|_2^2.
\]

变量与直觉：\(\mathcal{H}\) 是 text、semantic output 与 FAST action token 的 next-token cross-entropy；\(f_\theta^a\) 是 action expert velocity；\(\alpha\) 是两项目标的权衡。论文先以 \(\alpha=0\) 做 autoregressive pre-training，再在 post-training 加入随机初始化的 action expert，并报告 \(\alpha=10\) 的联合训练。[P2]

推理不需要自回归生成 FAST actions：论文描述为先生成所需 text/subtask token，再用条件 flow action expert 做 10 步采样。这正是“token route 帮助训练、flow route 保证较快连续动作推理”的设计意图。[P2]

### 5.2 论文中的 state 与 timestep 注入

与 π0 相比，π0.5：

1. 将 proprioceptive state 离散化后放入 text/prefix token，而不是单独连续 state suffix token；
2. 不再把 flow timestep 与每个 noisy action embedding 拼接，而是经单独 MLP 后用 adaptive RMSNorm 注入 action expert 各层。[P2]

冻结 openpi 对这两点有直接代码：

- PaligemmaTokenizer 在 pi05 格式中将 normalized state 用 256 bins 离散，组成 Task: ..., State: ...; Action: prompt。
- Pi0Config(pi05=True) 默认 discrete_state_input=True，max_token_len 从 48 变为 200。
- Pi0.embed_suffix 在 pi05 路径不添加 continuous state token，timestep MLP 的结果作为 adarms_cond；π0 路径则把 time embedding 与每个 action token 拼接。[R1]

### 5.3 必须保留的 paper / repo 缺口

| Claim | π0.5 paper | openpi Pi0(pi05=True) | 判定 |
| --- | --- | --- | --- |
| state 作为离散 prompt token | direct | direct，且可由 config 关闭 | implemented with config nuance |
| adaRMSNorm 注入 flow timestep | direct | direct | implemented |
| action expert 预测连续 chunk | direct | direct | implemented |
| FAST action tokens 同时参加 CE | direct | Pi0.compute_loss 未实现该分支 | **paper-only in this audit** |
| 联合 CE + α flow loss | direct | Pi0.compute_loss 只返回 flow MSE | **not reproduced by this path** |
| 论文完整 pretrain/post-train data recipe | direct overview | repo code不足以重建私有数据 | unverified |

因此，冻结 repo 可以支持“released π0.5-style flow architecture 的 state/timestep 改造”，不能单独支持“完整复现论文 π0.5 hybrid pre-training”。独立的 Pi0FAST class 也不能自动当作 Pi0(pi05=True) 内部的 CE branch；它们是不同 ModelType、不同 loss 和不同 inference path。[R1]

## 6. FAST：从连续 action chunk 到频域 token

### 6.1 normalization 不在 Hub processor 内

令第 i 个 action dimension 的训练集 1%/99% quantile 为 \(q_i^{01},q_i^{99}\)。论文和 openpi 的 quantile normalization 形式为：

\[
\tilde a_i
=
2\frac{a_i-q_i^{01}}{q_i^{99}-q_i^{01}+\varepsilon}-1.
\]

变量与边界：\(\tilde a_i\) 是输入 tokenizer/model 的归一化值；openpi 的 Normalize._normalize_quantile 没有显式 clip，所以超出训练分位范围的值可能落在 [-1,1] 外。FAST paper/README 推荐预归一化到约 [-1,1]，但冻结 Hub processor 的 __call__ 从 DCT 开始，不读取 norm stats。[P3][R1][H1]

这意味着正确 pipeline 是“dataset/checkpoint normalizer → FAST processor”，不是“FAST processor 自己完成所有尺度处理”。

### 6.2 DCT、量化与 frequency-first flatten

对 \(\tilde A\in\mathbb{R}^{H\times D}\) 的每个 action dimension i，FAST 在时间轴做 DCT：

\[
C_j^i=\operatorname{DCT}(\tilde a_{1:H}^i),\qquad
\bar C_j^i=\operatorname{round}(\gamma C_j^i).
\]

变量与直觉：j 是频率 index，低 j 表示慢变化趋势；\(\gamma\) 越大，保留的小系数越多、重建更精细但压缩更弱。论文单数据集实验使用 \(\gamma=10\)。Hub processor 对 shape [B,H,D] 在 axis=1 做 orthonormal DCT，再乘 scale 并 round。[P3][H1]

随后按频率优先展开：

\[
z=
[\bar C_0^1,\ldots,\bar C_0^D,
\bar C_1^1,\ldots,\bar C_1^D,\ldots],
\qquad
y_{1:L}=\operatorname{BPE}_{\Phi}(z).
\]

变量与实现映射：z 先排列所有维度的低频 coefficient，再进入高频；BPE 字典 \(\Phi\) 合并常见整数片段和大量重复 zero。Hub 源码的 DCT 输出是 [H,D]，C-order elem.flatten() 正好实现 frequency-major flatten。[P3][H1]

解码为：

\[
\hat A=
\operatorname{IDCT}
\left(
\operatorname{unflatten}_{H,D}
\left(\operatorname{BPE}^{-1}_{\Phi}(y_{1:L})\right)/\gamma
\right).
\]

变量与边界：FAST 解码恢复的是 normalized H×D chunk，之后仍需 checkpoint-matched unnormalize 和 dataset output transform。Hub decoder 若 token 序列无法 reshape 成 [H,D]，冻结实现会退化为全零 coefficient；这类错误不应在 rollout 中静默忽略。[H1]

### 6.3 BPE 是 learned component，但 compression 不等于控制质量

FAST 的 DCT、round 与 IDCT 不需要训练；BPE vocabulary 是唯一 learned component。论文消融显示去掉 BPE 会留下大量重复 zero token、显著增加 autoregressive steps，并在其评测任务上降低 policy performance。[P3]

但以下推论不成立：

- token 更少 ⇒ 物理重建误差必然更小；
- reconstruction MSE 更低 ⇒ closed-loop success 必然更高；
- FAST+ 在一个 embodiment 上可用 ⇒ 不需要核对 axis、unit、frequency 与 norm stats。

compression、reconstruction、next-token learning signal、autoregressive latency 和 online control 是五个不同指标层。

### 6.4 三组容易混淆的默认值

| 对象 | scale | BPE vocab | H / D | 解释 |
| --- | ---: | ---: | --- | --- |
| FAST paper 单数据集实验 | 10 | 1024 | 1-second chunks，依 robot frequency | 实验 recipe |
| frozen FAST+ Hub processor | 10 | 2048 | decode 时显式传或缓存 | 发布 artifact 的 processor_config |
| openpi Pi0FASTConfig 默认 | 由 external tokenizer | 由 external tokenizer | H=32，D=32 | model class default |
| openpi pi0_fast_libero 示例 | external tokenizer | external tokenizer | H=10，D=7 | dataset-specific example config |

这些数值必须连同对象名称一起回答。尤其不能用 LIBERO example 的 H=10 证明本地 OpenPiVLA 也使用 horizon 10。

## 7. Pi0FAST：自回归训练与 decode path

### 7.1 token layout 与 masks

冻结 openpi 的 FASTTokenizer 构造：

```text
# Token-layout sketch: prefix is condition; postfix is the autoregressive target.
prefix  = BOS + "Task: ..., State: <256-bin state>;\\n"
postfix = "Action: " + <FAST action tokens mapped into PaliGemma tail vocab> + "|" + EOS
```

代码块说明：prefix token 使用 bidirectional prefix attention；postfix 使用 causal attention；loss_mask 只在 postfix 为 true。FAST action token 通过 PaliGemma vocabulary 末尾区域映射，另跳过 128 个 special-token slots。[R1]

这与 OpenVLA 的逐标量 tail-vocab token 不同：

- OpenVLA：每个当前动作维度对应一个 scalar token；
- FAST：整个时间窗口先做 DCT/round/BPE，token 数 L 可变；
- π0 flow：不生成离散 action token，网络每步输出 H×D velocity。

### 7.2 masked next-token CE

令序列 token 为 \(y_{1:T}\)，postfix loss mask 为 \(m_k\in\{0,1\}\)。Pi0FAST 的训练目标是：

\[
\mathcal{L}_{\mathrm{FAST\text{-}CE}}
=
-\frac{\sum_{k=1}^{T-1}
m_{k+1}\log p_\theta(y_{k+1}\mid y_{\le k},I)}
{\max(1,\sum_{k=1}^{T-1}m_{k+1})}.
\]

变量与实现：I 是图像 token 条件；target 和 loss mask 都右移一位以匹配 next-token prediction；prefix 与 padding 不参加 loss。Pi0FAST.compute_loss 返回每个 batch example 的平均 masked CE，训练脚本再取 batch mean。[R1]

### 7.3 推理先生成 token，output transform 再恢复 action

Pi0FAST.sample_actions 的直接返回值其实是最多 256 个 autoregressive output token，不是最终 controller action。Policy.infer 把它暂存为 actions 字段，随后 ModelTransformFactory 注册的 ExtractFASTActions 才执行：

1. 从生成文本中抽取 Action: ... | 区间；
2. 映回 FAST token IDs；
3. 以指定 action_horizon 与 action_dim 做 FAST decode；
4. 进入 Unnormalize；
5. 进入 dataset-specific output transform 和 slicing。[R1]

因此只阅读 sample_actions 函数会误判它的返回合同。必须继续追到 policy output transform。

### 7.4 latency 的来源

FAST 论文在 NVIDIA 4090 的报告值是：π0 flow 约 100 ms/chunk，而 π0-FAST 约 750 ms/chunk；其解释是 FAST 通常需要 autoregressively decode 30–60 个 action tokens，并使用完整 2B backbone，而 flow π0 使用 10 次较小 300M action expert integration。[P3]

这些是论文硬件与实现下的公开测量，不是所有 deployment 的固定延迟。真实面试回答应拆成 vision encode、prefix prefill、per-token/per-step decode、network transport 与 controller queue，并用本地 timing log 证明本地数值。

## 8. Normalization、padding、slicing 与执行合同

### 8.1 checkpoint-matched normalization

冻结 policy_config 明确从 checkpoint_dir/assets 加载训练时 norm stats。输入顺序是：

```text
# Policy transform order: arrows denote the exact inference data flow.
repack → dataset input transform → normalize → model input transform
      → sample_actions
      → model output transform → unnormalize
      → dataset output transform → repack output
```

代码块说明：norm stats 不是仅在数据预处理脚本里用一次，而是 train/infer 必须共享的 policy artifact；错用 asset_id、漏 unnormalize 或先 slice 再错误匹配 stats 都可能产生 offline loss 正常但 online 0-success。[R1]

### 8.2 zero-padding 与 selection matrix

真实机器人 action \(a\in\mathbb{R}^{d}\) 可嵌入 model action \(a^{model}\in\mathbb{R}^{D}\)，其中 \(d\le D\)：

\[
a^{model}=Pa=
\begin{bmatrix}
I_d\\
0
\end{bmatrix}a,
\qquad
a^{env}=Sa^{model},
\quad
S=\begin{bmatrix}I_d&0\end{bmatrix}.
\]

变量与代码映射：P 对应 PadStatesAndActions 的尾部 zero-pad，S 对应 dataset output transform 的前 d 维 slicing；理论上 \(SP=I_d\)。LIBERO output transform 返回前 7 维，Pi0Config 默认 model D=32；Pi0FAST 的 LIBERO 示例则直接把 model D 配成 7。[R1]

风险边界：zero padding 不自动保证 padded dimensions 不参与 loss。公开 π0 compute_loss 对 D 维直接 mean；如果 model D 大于真实 d，是否需要 loss mask、是否训练 padding 为零，必须按具体 data/config 路径核对。不能把 output slicing 当作训练期 loss masking 的证据。

### 8.3 quantile unnormalize

对有统计的前 d 维，openpi 反归一化为：

\[
\hat a_i=
\frac{\hat{\tilde a}_i+1}{2}
\left(q_i^{99}-q_i^{01}+\varepsilon\right)+q_i^{01}.
\]

变量与实现：\(\hat{\tilde a}\) 是 flow sample 或 FAST decode 后的 normalized action。若 model 输出还有 stats 未覆盖的 padding dimensions，Unnormalize 保留这些额外维原值，随后 dataset output transform 再切片。[R1]

公式中的乘法应理解为 \((\hat{\tilde a}_i+1)/2\) 乘以 quantile range；这是 normalized unit 到 dataset action unit 的恢复，仍不等于 controller-specific axis conversion 或安全裁剪。

### 8.4 action axis 与 unit 不能靠维数猜

openpi norm_stats 文档的默认 π action layout 是：

- dim 0–5：left arm joint angles；
- dim 6：left gripper；
- dim 7–12：right arm joint angles；
- dim 13：right gripper；
- dim 14–15：mobile base x-y velocity。

Franka 路径使用前 7 维 joint + 第 8 维 gripper；DROID 又是前 7 维 joint velocity + 第 8 维 gripper，15 Hz。[R1]

这说明同样的 8D shape 可以有 position 或 velocity 等不同语义。shape 对齐只是必要条件，不是 controller contract 完成的充分条件。

## 9. Action horizon、execution window 与 replan

令 model 预测：

\[
\hat A_t=[\hat a_t,\ldots,\hat a_{t+H-1}]
\in\mathbb{R}^{H\times d},
\]

每次只执行前 K 步：

\[
\text{execute}\left(\hat A_t[0:K]\right),
\qquad 1\le K\le H,
\]

然后以新观测重新 query policy。变量含义：H 是 model output horizon；K 是 execution/replan interval。K 小时闭环更强但 query 更频繁；K 大时吞吐更好但更容易沿旧计划累积误差。[R1]

冻结 LIBERO example 的默认 K=5、50 trials/task、seed=7，并在每次 queue 为空时取新 chunk 的前 K 步。它还将 base/wrist 图像旋转 180°以匹配训练 preprocessing，构造 8D state，output transform 只返回前 7 action dims。[R1]

另一个 ActionChunkBroker 会逐步消费整个 configured action_horizon，耗尽后才重新 infer。两种 queue policy 都是公开示例；本地项目到底采用哪一种，必须读本地 client。

```python
def rollout_step(env, client, task, replan_steps):
    # 1. Read fresh RGB observations and proprioceptive state.
    obs = build_libero_observation(env, task)

    # 2. Policy transforms normalize state and build model-specific tokens.
    #    Flow returns HxD normalized actions; FAST first returns tokens then decodes HxD.
    action_chunk = client.infer(obs)["actions"]

    # 3. Output transforms have already unnormalized and sliced dataset dimensions.
    assert len(action_chunk) >= replan_steps

    # 4. Execute only K steps, then use a new observation for the next query.
    for action in action_chunk[:replan_steps]:
        _, _, done, info = env.step(action.tolist())
        if done:
            return info
    return info
```

伪代码映射冻结 examples/libero/main.py 与 policy transform 顺序；真实项目若在 client 外另做 denormalize、clip 或 axis reorder，必须改写并附本地源码证据。

## 10. 三条 action 路线对照

| 维度 | OpenVLA scalar tokens | FAST / Pi0FAST | π0 flow action expert |
| --- | --- | --- | --- |
| 基本单位 | 当前动作的每个 scalar dimension | H×D chunk 的频域/BPE token sequence | H×D continuous noisy action |
| 时间结构 | 原始旗舰单步 | 先压缩整个 1-second chunk | 整个 chunk 联合建模 |
| 训练目标 | masked token CE | masked autoregressive token CE | velocity MSE |
| 推理 | 生成 d 个 token | 生成可变 L 个 token，再 FAST decode | N 次 ODE/Euler update |
| 多模态连续 action | 量化 token 分布 | token sequence 分布 | continuous generative field |
| 主要延迟 | LM decoding | 完整 VLM 的多 token AR decoding | 多次较小 action expert |
| normalization | dataset q01/q99 + scalar bins | external norm stats + FAST processor | external norm stats |
| 必查风险 | token offset、bin endpoint | H/D reshape、BPE revision、truncation | time convention、solver、valid dims |
| 本地 OpenPiVLA 关系 | 只作 scalar-token 对照 | 可能是上游机制候选 | 可能是上游 action expert 候选 |

面试选择路线时不要只谈“谁更先进”。至少同时回答：action 多模态性、控制频率、H/K、允许延迟、训练数据量、reconstruction tolerance、checkpoint assets 与 controller contract。

## 11. Claim-to-code 总表

| Claim | paper / artifact | frozen code | 判定 | 面试口径 |
| --- | --- | --- | --- | --- |
| π0 输入多图、语言、proprio | π0 v4 direct | Pi0Config 三图 + state | direct | 论文 2–3 图；repo 默认三槽 |
| π0 输出 H=50 action chunk | π0 v4 direct | Pi0Config default H=50 | direct default | config 可覆盖，不是所有 checkpoint 固定 50 |
| π0 flow paper/code 时间相反 | π0 v4 0→1 | code 1→0 | equivalent with sign change | 同时报 time 和 target velocity 取反 |
| π0 默认 10 Euler steps | π0 v4 direct | sample_actions num_steps=10 | direct default | deployment 可覆盖 |
| π0.5 state token + adaRMSNorm | π0.5 v1 direct | Pi0 pi05 branch | direct with config nuance | released architecture difference |
| π0.5 联合 FAST CE + flow loss | π0.5 v1 direct | Pi0 compute_loss 无 CE branch | paper-only here | 不得称 frozen path 完整复现 |
| Pi0FAST 用 FAST token CE | FAST/openpi direct | Pi0FAST.compute_loss | direct | 独立 ModelType，不等于 Pi0 pi05 |
| FAST 是 per-scalar bins | FAST v1 rejects | Hub processor DCT/BPE | rejected | 它是 window frequency tokenization |
| FAST processor 自带 q01/q99 stats | README 要求预归一化 | processor 从 DCT 开始 | rejected | normalizer 在 processor 外 |
| FAST 默认 vocab 永远 1024 | paper 单数据集 1024 | Hub artifact 2048 | rejected as universal | 回答时注明对象/version |
| openpi quantile normalize 会 clip | 未声明 | transform 无 clip | rejected | 超界值可落在 [-1,1] 外 |
| D=32 代表 32 个真实控制轴 | 无 | Pad/Slice path | rejected | D 是 model capacity，d 是 dataset action |
| output slicing 等于 loss mask | 无 | loss 与 output transform 分离 | rejected | 训练有效维必须另核对 |
| H 等于 replan interval | 无 | LIBERO H 与 K 分离 | rejected | H model output；K executed prefix |
| LIBERO example 证明本地 H=10 | 无 | 只是 official example config | rejected | 需本地 config/checkpoint |
| upstream code 证明本地 97.4% | 无 | 无 | rejected | 需 eval summary + protocol + checkpoint |

## 12. 对 Phase 0 题目的支持状态

| Question ID | 本页支持 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ARCH-002 | multi-view/text/state → H×D contract | source-ready | generic history/time alignment 对照 |
| VLA-ARCH-003 | VLM context、action expert、output transform、controller 边界 | source-ready | Octo / RT-2 comparison |
| VLA-ARCH-004 | 三图槽、mask、离散/连续 state | partial | 更广 multi-view alignment |
| VLA-ARCH-006 | π0 action expert + flow train/infer | source-ready | independent formula review |
| VLA-ARCH-008 | Pi0FAST prefix/postfix/AR/loss masks | source-ready | other VLA layouts |
| VLA-ARCH-010 | D/d、padding、slicing、loss risk | source-ready | explicit masked-loss positive example |
| VLA-ARCH-011 | FAST vs flow latency component | partial | local timing instrumentation |
| VLA-ARCH-012 | paper/repo/artifact/checkpoint audit method | source-ready | local manifest |
| VLA-ACT-002 | checkpoint norm stats、normalize/unnormalize | source-ready | local norm asset |
| VLA-ACT-005..007 | FAST motivation、algorithm、trade-off | source-ready | independent fact review |
| VLA-ACT-008 | H×D、P/S、valid dimension boundary | source-ready | local action_dim/mask |
| VLA-ACT-011 | H、K、chunk queue | source-ready | ACT temporal ensemble later |
| VLA-ACT-023..025 | probability path、velocity、ODE solver | source-ready for π0 | foundational Flow Matching paper |
| VLA-ACT-027 | context/state/noisy action expert input | source-ready | PyTorch parity if needed |
| VLA-ACT-028 | padding pollution risk | partial / negative evidence | positive mask implementation |
| VLA-ACT-031..032 | decode→unnorm→slice→queue | partial | controller axis/safety tests |

source-ready 只表示来源足够起草知识页，不代表候选人已掌握。后续题卡创建后仍必须标为 unseen，直到真实口述训练。

## 13. 本地 OpenPiVLA 证据缺口

公开 π0/FAST/openpi 可以给出上游机制，但以下 claim 必须补本地 artifact：

| 本地 claim | 需要的最小证据 | 当前状态 |
| --- | --- | --- |
| base checkpoint / backbone | load config、checkpoint manifest、startup log | pending |
| 是 Pi0、Pi05、Pi0FAST 还是自定义 Qwen path | model class、forward/compute_loss、local diff | pending |
| action H=10 | dataset target shape、model config、inference output shape | pending |
| action dimension / axis / unit | dataset schema、norm stats、output transform、controller wrapper | pending |
| FAST revision / scale / vocab | tokenizer config、cached revision、training log | pending |
| JSON/action token supervision | formatter、labels/loss mask、decode/parser tests | pending |
| replan / queue policy | local rollout client、K、control frequency | pending |
| 97.4% | exact checkpoint、suite/tasks、trials、seed/split、summary JSON | pending |
| personal contribution | upstream/local diff、设计记录、run ledger | pending |

在这些证据收集完成前，最安全的项目表述是“基于 π/FAST/openpi 公开机制建立 action modeling 与 eval pipeline 的候选解释；本地具体实现和指标归因仍按 artifact 核实”，不能把 upstream design 自动写成本人创新。

## 14. 风险与下一步

1. **核心高风险事实已独立复核**：π0.5 hybrid、FAST normalization/DCT/BPE、OpenPI model split、padding/slicing、norm stats 与 LIBERO replan 已在 [独立复核页](vol_03_pi0_fast_openpi_independent_fact_review.html) 直接核对，公共事实层为 `PASS WITH WARNING`；local checkpoint、tokenizer revision、axis/unit、H/K、controller、eval bundle 与 ownership 仍使本页整体保持 `WARN/PENDING`。
2. **π0.5 hybrid gap 是高优先级复核项**：需独立确认 frozen openpi 的 released Pi05 training path 是否在其他文件另有 combined CE；当前已读主 compute_loss 和 transform factory，未见该分支。
3. **FAST artifact revision 必须固定**：openpi 默认字符串没有 pin Hub revision；复现时需要 cache/lockfile 或显式 revision。
4. **normalization 无 clip 的边界需单测**：测试 q01/q99 外动作、constant dimension、padding dimension 和 inverse consistency。
5. **decode failure 不应静默全零**：本地部署应让 malformed FAST sequence 触发 error/telemetry，而不是无声执行零动作。
6. **视觉 QA 已完成**：通过 localhost 静态服务检查桌面 `1440×1000` 与窄屏 `800×1000`；确认一处 H1、academic palette/serif、desktop sticky TOC、narrow static TOC、公式无 `<em>` 污染且无页面级横向溢出。
7. **下一步**：优先进行一题 π0/FAST/Flow 真实口述，或收集本地 OpenPiVLA checkpoint/tokenizer/stats/controller artifact；题卡继续保持 `unseen`。

## 参考文献（References）

1. [P1] Black et al., [π0: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/html/2410.24164v4), arXiv v4, 2024.
2. [P2] Black et al., [π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/html/2504.16054v1), arXiv v1, 2025.
3. [P3] Pertsch et al., [FAST: Efficient Action Tokenization for Vision-Language-Action Models](https://arxiv.org/html/2501.09747v1), arXiv v1, 2025.
4. [R1] [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), frozen commit 15a9616a00943ada6c20a0f158e3adb39df2ccac, accessed 2026-07-16. 核心路径：
   - [pi0_config.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_config.py)
   - [pi0.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0.py)
   - [pi0_fast.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_fast.py)
   - [tokenizer.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/tokenizer.py)
   - [transforms.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py)
   - [training/config.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/config.py)
   - [policy_config.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_config.py)
   - [libero_policy.py](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/libero_policy.py)
   - [LIBERO client](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/main.py)
   - [normalization notes](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/docs/norm_stats.md)
5. [H1] [physical-intelligence/fast](https://huggingface.co/physical-intelligence/fast/tree/ec4d7aa71691cac0b8bed6942be45684db2110f4), frozen revision ec4d7aa71691cac0b8bed6942be45684db2110f4, Apache-2.0, accessed 2026-07-16. [processor source](https://huggingface.co/physical-intelligence/fast/blob/ec4d7aa71691cac0b8bed6942be45684db2110f4/processing_action_tokenizer.py) / [processor config](https://huggingface.co/physical-intelligence/fast/blob/ec4d7aa71691cac0b8bed6942be45684db2110f4/processor_config.json).
6. 本地项目页：[OpenPiVLA：FAST 动作表示、Metax 迁移与策略评估复现](../../03_openpivla_action_modeling.html)。当前仅作为 claim 入口，不作为缺失 raw artifact 的替代证据。
