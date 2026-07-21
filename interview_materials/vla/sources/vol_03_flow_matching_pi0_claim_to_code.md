# VOL 03 Source Audit E：Flow Matching 基础、π0 特化与 ODE Claim-to-Code

> 审计日期：2026-07-19  
> 状态：`independent_fact_reviewed / theorem_endpoint_time_sign_checked / local_runtime_pending / WARN`  
> 基础论文：*Flow Matching for Generative Modeling*，arXiv `2210.02747v2`  
> 后续官方包：`facebookresearch/flow_matching` frozen commit `11568d37f8d5a080e12aa7b5305d9c35ae07d136`，CC BY-NC 4.0  
> VLA 特化：*π0: A Vision-Language-Action Flow Model for General Robot Control*，arXiv `2410.24164v4`；`Physical-Intelligence/openpi` frozen commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`，Apache-2.0  
> 对应题目：`VLA-ACT-023..030`；补全 `VLA-ACT-026` 的 Diffusion / Flow 对照  
> 本页问题：Flow Matching 的 probability path、marginal / conditional vector field 与训练目标是什么？线性路径为什么只是特例？π0 如何把这套生成建模落到 `[B,H,D]` action chunk，openpi 为什么反向积分仍然等价？Flow 与 Diffusion 的 target、sampler、mask、guidance 和故障定位应如何严格区分？

## 1. 结论先行

1. **Flow Matching（FM）不是“直接回归最终 action”，而是回归给定 probability path 上的时间依赖速度场。**训练期随机取路径上的点 \(x_t\)，让 \(v_\theta(x_t,t)\) 拟合目标 vector field；推理期再解 ODE 把 source/noise 推到 target/data。[1]
2. **原始 FM objective 依赖通常不可直接计算的 marginal vector field。**Conditional Flow Matching（CFM）改为采样 data-conditioned path 和 conditional velocity；论文 Theorem 2 证明 FM 与 CFM 对参数 \(\theta\) 的梯度相同，而不是声称两项 loss 的逐样本数值相同。[1]
3. **线性插值 \(x_t=(1-t)x_0+tx_1\)、target \(x_1-x_0\) 是 conditional OT path 的零端点噪声特例，不是全部 Flow Matching。**原论文 Eq. 20–23 实际保留 \(\sigma_{\min}>0\)；当前官方包的 `CondOTProbPath` 才直接使用 \(\sigma_t=1-t,\alpha_t=t\)。[1][2]
4. **“simulation-free”只描述训练不需要先数值模拟 CNF trajectory。**采样仍要调用 ODE solver；solver method、步长、时间网格、NFE 和误差容限都会影响质量与 latency。[1][2]
5. **当前 `facebookresearch/flow_matching` 是后续维护的通用 PyTorch 包，不是 2022 论文发布时的历史实现快照。**它可补证现代 path / solver API，但不能倒推原论文当年的 exact code、default 或实验 recipe。[2]
6. **π0 把 data sample \(x_1\) 具体化为 normalized action chunk \(A\in\mathbb R^{B\times H\times D}\)，把 context 具体化为多视角图像、语言和 proprioception。**action expert 在每个 flow step 接收 noisy action 与 timestep，输出同形状 velocity。[3][4]
7. **π0 paper 与 openpi 的时间方向相反，但轨迹等价。**paper 从 \(\tau=0\) noise 到 \(\tau=1\) action，target 为 \(A-\epsilon\)；code 从 \(t=1\) noise 以负步长到 \(t=0\) action，target 为 \(\epsilon-A\)。令 \(\tau=1-t\)，时间和速度同时翻转，ODE 增量不变。[3][4]
8. **timestep sampling 也不能漏报。**基础 FM 论文写 \(t\sim\mathcal U[0,1]\)；π0 使用 shifted Beta recipe 强调 high-noise 区域。openpi 的 `0.001 + 0.999 * Beta(1.5,1)` 是在反向时间坐标下对论文 recipe 的直接实现，不是无缘由偏离。[3][4]
9. **Flow 与 Diffusion 可以共享 Gaussian path 语境，但不应混成同一训练接口。**本仓库冻结的 Diffusion Policy 默认预测 discrete scheduler timestep 的 epsilon；π0 预测 continuous flow time 的 velocity，并用显式 Euler ODE update。FM 论文还明确允许 diffusion probability paths，因此“Flow 与 Diffusion 完全无关”和“Flow 只是少步 Diffusion”都不准确。[1][5]
10. **上游 loss 正常不能证明本地 rollout 正确。**openpi flow loss 对 configured \(D\) 维直接 mean，没有 action-valid-dimension mask；padding、norm stats、axis/unit、\(H/K\)、solver sign 和 controller queue 都可能让 offline loss 看似正常但 closed-loop 失败。[4]

## 2. 证据层级、冻结对象与适用边界

| 层级 | 冻结对象 | 本页使用 | 不能支持 |
| --- | --- | --- | --- |
| 基础论文 | arXiv `2210.02747v2`，updated 2023-02-08 | CNF、FM/CFM、gradient equivalence、Gaussian / OT conditional path | 当前 package API、π0 action tensor、本地项目 |
| 后续官方包 | `facebookresearch/flow_matching` commit `11568d...` | `AffineProbPath`、`CondOTProbPath`、velocity target、ODE solver、supporting CFG example | 2022 paper 的历史 code/default；商业复用授权 |
| π0 论文 | arXiv `2410.24164v4` | action path、action expert、shifted Beta timestep、10-step flow sampling | frozen openpi 的逐行实现、本地 OpenPiVLA |
| openpi | commit `15a9616...` | `[B,H,D]` shape、loss、prefix/suffix、time reversal、Euler loop | 用户项目的 checkpoint、axis、H/K、97.4% |
| Diffusion Audit D | paper/repo/dependency 已冻结 | epsilon target、scheduler、\(T_o/T_p/T_a/K\) 对照 | 用 diffusion 实现替代 flow 实现 |
| 同源推断 | 上述公式与代码联合推导 | time/sign 等价、mask 污染、debug invariant | 未运行的本地 success、latency 和个人贡献 |

版本与许可边界：

- Flow Matching v2 的 title / revision 已按 arXiv 页面冻结；正文 Section 2–4 与 Appendix B continuity equation 已逐式核验。[1]
- 当前 `flow_matching` clone HEAD 为 `11568d37f8d5a080e12aa7b5305d9c35ae07d136`，commit date 2026-01-05；README 说明它属于后来的 *Flow Matching Guide and Codebase*，并同时覆盖 continuous / discrete flow matching。[2]
- 该 package 根 LICENSE 是 Attribution-NonCommercial 4.0；所以它适合作为学习与审计来源，不能默认当作无限制商用依赖。[2]
- π0 / openpi 的完整 architecture、FAST、normalization 与 rollout 边界已在 [Source Audit B](vol_03_pi0_fast_openpi_claim_to_code.html) 冻结；本页只重放与基础 FM 直接相关的最短证据链。[3][4]

## 3. CNF：路径、速度场与 continuity equation

### 3.1 从 ODE 定义 flow

Continuous Normalizing Flow（CNF）用时间依赖 vector field \(v_t:\mathbb R^d\rightarrow\mathbb R^d\) 定义 flow map \(\phi_t\)：

$$
\frac{d}{dt}\phi_t(x)=v_t(\phi_t(x)),
\qquad
\phi_0(x)=x.
$$

变量与直觉：\(x\sim p_0\) 是 source sample，\(\phi_t(x)\) 是沿速度场走到时间 \(t\) 的位置；实现中 \(v_t\) 就是神经网络或其 wrapper 的输出。公式来自基础论文 Eq. 1–2。[1]

flow map 将 source density push forward 成 probability path：

$$
p_t=[\phi_t]_*p_0,
\qquad
p_1\approx q.
$$

其中 \(q\) 是目标数据分布。直觉上，模型不是直接记住一个终点函数，而是学习一组随时间变化的“往哪里走”的指令。实现映射：ODE solver 从 source sample 和 time grid 出发，多次调用 velocity model。[1][2]

### 3.2 continuity equation 是一致性条件

若 \(v_t\) 真正生成 \(p_t\)，二者满足：

$$
\frac{\partial p_t(x)}{\partial t}
+\operatorname{div}\!\left(p_t(x)v_t(x)\right)=0.
$$

变量与直觉：第一项是某点概率质量随时间变化，divergence 项是流入/流出的净通量；它表达“概率质量没有凭空产生或消失”。这是理论一致性条件，不是 π0 训练代码额外计算的一项 divergence loss。基础论文正文引用 continuity equation，完整式见 Appendix B Eq. 26。[1]

### 3.3 probability path 不是单条 sample trajectory

- \(p_t\)：时间 \(t\) 上整个随机变量的 density。
- \(\phi_t(x_0)\)：给定一个 source sample 的 deterministic ODE trajectory。
- \(u_t(x)\)：能生成目标 path 的 target vector field。
- \(v_\theta(x,t)\)：神经网络对 target field 的近似。

把这四者混在一起会导致两类常见错误：把 `x_t` 当成 loss target，或把一次 Euler 更新当成完整 probability distribution。

## 4. 从 FM 到 CFM：为什么可以逐 data sample 训练

### 4.1 Flow Matching objective

给定预先选择的 marginal probability path \(p_t\) 及其 target field \(u_t\)，基础 FM objective 为：

$$
\mathcal L_{\mathrm{FM}}(\theta)
=
\mathbb E_{t\sim\mathcal U[0,1],\,x\sim p_t}
\left[
\left\|v_\theta(x,t)-u_t(x)\right\|_2^2
\right].
$$

变量与实现含义：\(t\) 是 continuous time，\(x\) 是 path sample，\(u_t\) 是监督 velocity。难点是 marginal \(p_t\) 与 \(u_t\) 通常包含对全部 data 的积分，不能为每个 minibatch point 直接算出。论文 Eq. 5 使用 uniform time。[1]

### 4.2 conditional path 如何组成 marginal path

令 \(x_1\sim q\) 为 data sample，为每个 \(x_1\) 设计 conditional probability path \(p_t(x\mid x_1)\)，则：

$$
p_t(x)
=
\int p_t(x\mid x_1)q(x_1)\,dx_1.
$$

变量与直觉：每个 data point 携带一条从 source/noise 到其邻域的 conditional path；把所有 data-conditioned paths 混合，就得到 marginal path。论文 Eq. 6–7 要求 \(p_0\) 是 source，\(p_1\) 逼近 target \(q\)。[1]

若 \(u_t(x\mid x_1)\) 生成每条 conditional path，则 marginal vector field 可写为：

$$
u_t(x)
=
\int
u_t(x\mid x_1)
\frac{p_t(x\mid x_1)q(x_1)}{p_t(x)}
\,dx_1.
$$

变量与直觉：权重是给定当前位置 \(x\) 时不同 data endpoint 的 posterior responsibility；所以多条 conditional velocity 在同一点会按概率混合。论文 Theorem 1 证明这个 field 生成前述 marginal path。[1]

### 4.3 Conditional Flow Matching objective

CFM 直接采样 \(x_1\)、conditional path point \(x\) 和可计算的 conditional velocity：

$$
\mathcal L_{\mathrm{CFM}}(\theta)
=
\mathbb E_{\substack{
t\sim\mathcal U[0,1],\,x_1\sim q,\\
x\sim p_t(\cdot\mid x_1)}}
\left[
\left\|v_\theta(x,t)-u_t(x\mid x_1)\right\|_2^2
\right].
$$

变量与实现：minibatch data 是 \(x_1\)，新采样 noise 构造 \(x_t\)，解析式或 path API 给出 \(u_t(x_t\mid x_1)\)。基础论文 Eq. 9 / Theorem 2 证明，在 objectives 有限的条件下，FM 与 CFM 对 \(\theta\) 的梯度相同。[1]

必须保留的限定：

- identical gradients 不等于每个 sample 的 target 相同；
- identical gradients 不等于两个 loss scalar 在日志中逐值相等；
- 结论依赖 conditional path / field 的构造确实生成所声明的 marginal path；
- π0 改用非 uniform timestep sampling，相当于选择了 task-specific time weighting，不能再无条件称为原始 uniform objective。

## 5. Gaussian conditional path 与 OT 特例

### 5.1 一般 affine Gaussian path

基础论文考虑：

$$
p_t(x\mid x_1)
=
\mathcal N\!\left(
x\mid\mu_t(x_1),\,\sigma_t(x_1)^2I
\right),
$$

并用 \(x_0\sim\mathcal N(0,I)\) 的 affine map 采样：

$$
\psi_t(x_0)
=
\sigma_t(x_1)x_0+\mu_t(x_1).
$$

变量与直觉：\(\mu_t\) 控制 conditional mean，\(\sigma_t\) 控制 noise scale；不同选择可得到 diffusion path 或 non-diffusion path。实现映射：现代 package 的 `AffineProbPath.sample` 正是 `x_t = sigma_t * x_0 + alpha_t * x_1`。[1][2]

沿这个 sample map 的 conditional target velocity 是：

$$
\dot x_t
=
\frac{d}{dt}\psi_t(x_0)
=
\dot\sigma_t(x_1)x_0+\dot\mu_t(x_1).
$$

变量与实现：`PathSample.dx_t` 保存这项 target；训练 example 用 `MSE(model(path_sample.x_t,t), path_sample.dx_t)`。这是 velocity prediction，不是 epsilon prediction 的同名替换。[2]

若只知道当前位置 \(x\)，论文还给出：

$$
u_t(x\mid x_1)
=
\frac{\dot\sigma_t}{\sigma_t}
\left(x-\mu_t\right)
+\dot\mu_t.
$$

这个表达把 conditional velocity 写成 \(x,x_1,t\) 的函数；\(\sigma_t=0\) 的端点需要按具体 path / solver 处理，不能机械在端点做除法。公式对应基础论文 Eq. 15。[1]

### 5.2 论文的 OT conditional path

基础论文的 OT path 取：

$$
\mu_t(x_1)=tx_1,
\qquad
\sigma_t=1-(1-\sigma_{\min})t,
$$

因此 sample path 与 target velocity 为：

$$
x_t=
\left[1-(1-\sigma_{\min})t\right]x_0+tx_1,
\qquad
\dot x_t=x_1-(1-\sigma_{\min})x_0.
$$

变量与边界：\(t=0\) 是 \(x_0\sim\mathcal N(0,I)\)；\(t=1\) 仍有 \(\sigma_{\min}x_0\)，所以 conditional endpoint 是以 \(x_1\) 为均值的小 Gaussian，而不是严格 delta。对应论文 Eq. 20–23。[1]

### 5.3 常背的线性公式是 \(\sigma_{\min}=0\) 特例

当 \(\sigma_{\min}=0\)：

$$
x_t=(1-t)x_0+tx_1,
\qquad
u_t=x_1-x_0.
$$

变量与直觉：每对 noise/data endpoint 沿直线匀速移动；target 不依赖 \(t\)，但网络输出仍依赖当前位置和 condition，因为不同 endpoint pairs 在空间中会重叠。不能从“conditional target 常量”推出“marginal field 是全局常量”。[1]

当前官方 package 的 `CondOTScheduler` 明确返回：

```python
# Modern package exact-endpoint convention.
alpha_t = t
sigma_t = 1 - t
d_alpha_t = 1
d_sigma_t = -1
```

代码块映射：`AffineProbPath.sample` 随后得到 `x_t=(1-t)x_0+tx_1`、`dx_t=x_1-x_0`。[2] 这可支持面试中的线性推导，但答题时要注明它是 package 的 exact-endpoint `CondOT` convention；不要反写成原论文所有公式都令 \(\sigma_{\min}=0\)。

## 6. 后续官方包：path、loss 与 solver 的真实接口

### 6.1 `AffineProbPath` 返回什么

frozen package 的 `PathSample` 包含：

| 字段 | 语义 | shape |
| --- | --- | --- |
| `x_0` | source/noise sample | `[B,...]` |
| `x_1` | target/data sample | `[B,...]` |
| `t` | sampled continuous time | `[B]` |
| `x_t` | conditional path point | `[B,...]` |
| `dx_t` | conditional velocity target | `[B,...]` |

`AffineProbPath.sample` 先从 scheduler 取 \(\alpha_t,\sigma_t,\dot\alpha_t,\dot\sigma_t\)，再计算：

$$
x_t=\sigma_tx_0+\alpha_tx_1,
\qquad
\dot x_t=\dot\sigma_tx_0+\dot\alpha_tx_1.
$$

实现证据为 [`affine.py#L57-L92`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/flow_matching/path/affine.py#L57-L92) 与 [`scheduler.py#L104-L114`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/flow_matching/path/scheduler/scheduler.py#L104-L114)。变量说明：package 用 \(\alpha_t\) 乘 target、\(\sigma_t\) 乘 source；这套命名必须跟具体 scheduler 一起读。

### 6.2 continuous FM MSE 不在 `flow_matching.loss` 中自动替你做

当前 package 的 continuous example 直接写：

```python
def continuous_fm_step(model, path, x_1):
    # Sample source noise and one continuous time per data item.
    x_0 = torch.randn_like(x_1)
    t = torch.rand(x_1.shape[0], device=x_1.device)

    # The path object provides both the interpolated point and velocity target.
    sample = path.sample(x_0=x_0, x_1=x_1, t=t)

    # Continuous FM uses ordinary velocity MSE in this example.
    pred = model(sample.x_t, t)
    return ((pred - sample.dx_t) ** 2).mean()
```

代码块映射：`examples/image/training/train_loop.py` 用 `CondOTProbPath`、`path_sample.dx_t` 与 tensor MSE。[2] package 的 `flow_matching.loss` 目录此 commit 主要提供 discrete mixture path 的 generalized KL；所以“import 一个 FlowMatchingLoss 就自动处理连续 CFM”不是这个 frozen API 的事实。

### 6.3 ODE solver

frozen `ODESolver.sample` 接收 initial state、time grid、method、step size 与 tolerances，然后调用 `torchdiffeq.odeint`。Euler 情况为：

$$
\hat x_{k+1}
=
\hat x_k+\Delta t\,
v_\theta(\hat x_k,t_k).
$$

变量与实现：Euler 只是 `method="euler"` 时的一阶近似；package 还可调用 `dopri5`、`midpoint`、`heun3` 等 torchdiffeq methods。`time_grid` 可升序或降序，方向必须与 velocity convention 配套。[2]

关键边界：

- fixed-step solver 要记录 step size / grid；adaptive solver 要记录 `atol`、`rtol` 与实际 NFE；
- training path sample 不需要先跑 ODE，但 inference 需要；
- solver 更高阶不自动修复错误 velocity target、time sign 或 normalization；
- package 默认 API 不等于 π0 的 deployment default，π0/openpi 手写固定 10-step Euler。

### 6.4 当前 package 的 CFG 只是 supporting example

image example 在训练时以 `class_drop_prob` 丢弃 label condition，推理时组合 conditional / unconditional velocities：

$$
v_{\mathrm{cfg}}
=
(1+s)v_{\mathrm{cond}}-s\,v_{\mathrm{uncond}}.
$$

变量与实现：\(s\) 是 `cfg_scale`；当 \(s\neq0\) 时，每次 ODE function evaluation 实际做两次 model forward。证据见 [`train_loop.py#L68-L73`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/examples/image/training/train_loop.py#L68-L73) 与 [`eval_loop.py#L36-L66`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/examples/image/training/eval_loop.py#L36-L66)。[2]

这不是 action-policy 直接证据：frozen openpi Pi0 path 未实现 condition dropout / CFG。若迁移到 VLA，必须定义究竟 drop language、images、state 还是全部 condition，并评估 double forward latency、velocity magnitude、action safety 与 task compliance；不能只复制一个 scale。

## 7. π0：把 CFM 特化为 action chunk generation

### 7.1 data、noise、condition 与 output shape

对 π0：

- data endpoint：normalized action chunk \(A\in\mathbb R^{B\times H\times D}\)；
- source：\(\epsilon\sim\mathcal N(0,I)\)，shape 同 \(A\)；
- condition：多视角图像、语言 prompt、proprioceptive state；
- model output：action expert velocity，shape `[B,H,D]`；
- inference endpoint：仍是 normalized action chunk，之后才 unnormalize、slice 并进入 controller。

论文路径为：

$$
A^\tau=\tau A+(1-\tau)\epsilon,
\qquad
u_{\mathrm{paper}}=A-\epsilon.
$$

变量与直觉：\(\tau=0\) 是 noise，\(\tau=1\) 是 action；这是上一节 exact linear path 令 \(x_0=\epsilon,x_1=A\) 的直接实例。π0 用 observation \(o\) 对 velocity model 条件化。[3]

训练目标可写为：

$$
\mathcal L_{\pi_0}
=
\mathbb E
\left[
\frac{1}{HD}
\left\|
v_\theta(A^\tau,\tau,o)-(A-\epsilon)
\right\|_2^2
\right].
$$

变量与代码映射：论文写 action flow objective；openpi `compute_loss` 对最后 action dimension \(D\) 先 mean，`scripts/train.py` 再对 batch 与 horizon mean，最终覆盖 configured `[B,H,D]` 元素。若 \(D\) 含 zero-padding，这个公式也会监督 padded elements，除非另有 mask；frozen Pi0 path 未见该 mask。[3][4]

### 7.2 VLM prefix 与 action suffix

frozen openpi 的信息流：

```text
# Prefix is condition and is cached during sampling.
images + language
        |
        v
PaliGemma/VLM prefix tokens ------------------+
                                              |
state token + noisy actions [B,H,D] + time ---+--> action expert
                                                    |
                                                    v
                                           velocity [B,H,D]
```

代码块说明：`action_in_proj` 把每步 D 维 noisy action 投到 expert width，time embedding 与 action token 融合；`action_out_proj` 投回 D 维 velocity。采样时 prefix KV cache 只建一次，每个 Euler step 重算 suffix。[4]

注意 π0 与 π0.5 分支差异已在 Source Audit B 详述；本页的基础公式不证明 frozen `Pi0(pi05=True)` 完整实现 π0.5 hybrid CE objective。

### 7.3 shifted Beta timestep 与 openpi 的反向坐标

基础 FM 论文使用 uniform time。π0 Appendix 改为强调 high-noise 区域的 shifted Beta：

$$
y\sim\operatorname{Beta}(1.5,1),
\qquad
\tau=s(1-y),
\qquad
s=0.999.
$$

变量与直觉：较大的 \(y\) 映射到较小 \(\tau\)，也就是更接近 noise 的 action path point；这改变了不同 flow times 在训练 loss 中的权重。π0 还截掉 \(\tau>s\) 的极低噪声末端。[3]

令 openpi code time \(t=1-\tau\)，则：

$$
t
=
1-s(1-y)
=
0.001+0.999y.
$$

这正对应 `time = Beta(1.5,1) * 0.999 + 0.001`。所以 code 的 Beta sample 不是和 π0 paper 冲突；它是在反向时间坐标中的等价写法。[3][4]

## 8. openpi 时间反转、loss 与 Euler sampling

### 8.1 code training convention

frozen `Pi0.compute_loss` 构造：

$$
x_t=t\epsilon+(1-t)A,
\qquad
u_{\mathrm{code}}=\epsilon-A.
$$

变量与实现：\(t=1\) 是 noise，\(t=0\) 是 action；`noise`、`x_t`、`u_t` 均为 `[B,H,D]`。action expert 的直接输出 \(v_t\) 与 \(u_{\mathrm{code}}\) 做 MSE。[4]

### 8.2 与 paper 的严格等价

令 \(\tau=1-t\)：

$$
x_{\mathrm{code}}(t)
=
t\epsilon+(1-t)A
=
(1-\tau)\epsilon+\tau A
=
x_{\mathrm{paper}}(\tau),
$$

$$
u_{\mathrm{code}}
=
\epsilon-A
=
-u_{\mathrm{paper}},
\qquad
d\tau=-dt.
$$

变量与直觉：同一路径上的 point 没变；velocity 和 time differential 都取反，因此：

$$
u_{\mathrm{code}}\,dt
=
u_{\mathrm{paper}}\,d\tau.
$$

这才是“反向时间仍等价”的完整理由。只说 `t=1` 到 `0` 而不说 velocity sign，会留下方向错误。[3][4]

### 8.3 explicit Euler

`sample_actions` 默认 \(N=10\)，令 \(\Delta t=-1/N\)：

$$
x_{k+1}
=
x_k+\Delta t\,v_\theta(x_k,t_k,o),
\qquad
t_{k+1}=t_k+\Delta t.
$$

变量与实现：初值在代码中名为 `noise`，time 从 1 开始；循环结束返回 time 0 的 action estimate。`num_steps` 是一次 policy query 内的 flow integration steps，不是 action horizon \(H\)、执行 prefix \(K\) 或机器人 control steps。[4]

```python
def openpi_flow_sample(observation, model, num_steps=10):
    # Cache image/language prefix once for this policy query.
    prefix_cache = model.encode_prefix(observation)

    # Initialize the whole normalized action chunk from Gaussian noise.
    x = randn(shape=[batch, action_horizon, action_dim])
    t = 1.0
    dt = -1.0 / num_steps

    while t >= -dt / 2:
        # Recompute state/noisy-action/time suffix at each flow step.
        velocity = model.action_expert(
            prefix_cache, observation.state, noisy_actions=x, time=t
        )

        # Explicit Euler follows code-time velocity toward data time 0.
        x = x + dt * velocity
        t = t + dt

    # Still normalized model-space [H,D]; policy transforms run afterward.
    return x
```

伪代码映射 `src/openpi/models/pi0.py` 的 `embed_suffix`、`compute_loss` 与 `sample_actions`；unnormalize、dataset output transform 和 execution queue 不在 model method 内完成。[4]

## 9. Diffusion noise prediction 与 Flow velocity prediction

### 9.1 不能只用“都是加噪再还原”回答

| 维度 | Frozen Diffusion Policy | π0 / openpi Flow |
| --- | --- | --- |
| training time | discrete scheduler index \(k\) | continuous flow time \(t/\tau\) |
| path construction | scheduler `add_noise` with \(\bar\alpha_k\) | explicit linear interpolation |
| default target | Gaussian epsilon | endpoint displacement / velocity |
| model output | scheduler interprets epsilon/sample | ODE vector field |
| inference init | Gaussian trajectory | Gaussian action chunk |
| update | DDPM/DDIM `scheduler.step` | explicit Euler \(x+\Delta t v\) |
| time count | diffusion iterations \(K_d\) | flow NFE / steps \(N_f\) |
| horizon | \(T_p\) plus action slice \(T_a\) | \(H\) plus execution prefix/replan \(K\) |
| conditioning | visual/state global or inpainting path | VLM prefix + state/action suffix |
| frozen warm-start | paper option，code random restart | random init unless noise supplied |

Diffusion Audit D 的默认 objective：

$$
\mathcal L_\epsilon
=
\mathbb E
\left[
\|\epsilon-\epsilon_\theta(O,A^k,k)\|_2^2
\right].
$$

π0 flow objective：

$$
\mathcal L_v
=
\mathbb E
\left[
\|u_t-v_\theta(o,x_t,t)\|_2^2
\right].
$$

变量与区别：两者都可用 MSE，也都可从 Gaussian 初始化，但 target 的定义、time parameterization 和 sampler update contract 不同。FM 基础论文允许用 diffusion probability paths，所以“path family”与“prediction parameterization / sampler”应分别比较。[1][4][5]

### 9.2 采样步数不是本质定义

- Flow 可以用很多 ODE steps；Diffusion 也可以用少步 DDIM。
- π0 默认 10 steps、Diffusion Policy frozen config 的 8/16/100 都是具体 recipe，不是方法定义。
- latency 要拆 vision/prefix encode、每次 model NFE、solver/scheduler overhead、transport 与 controller queue。
- 质量要同时看 offline velocity/noise error、action reconstruction、closed-loop success 与 safety，不可只比较 step 数。

## 10. Action valid dimensions、padding 与 guidance

### 10.1 frozen Pi0 loss 没有 action-valid-dimension mask

若 environment action \(a\in\mathbb R^d\) 被 padding 到 model dimension \(D\ge d\)，理想 masked flow loss 可写为：

$$
\mathcal L_{\mathrm{masked}}
=
\frac{
\sum_{b,h,j}
m_{b,h,j}
\left(v_{b,h,j}-u_{b,h,j}\right)^2
}{
\sum_{b,h,j}m_{b,h,j}+\varepsilon_0
}.
$$

变量与实现要求：\(m_{b,h,j}=1\) 才是有效 timestep / action axis；\(\varepsilon_0\) 防止空 mask 除零。mask 必须来自 dataset schema、sequence validity 或 action-dimension metadata，不能由 output slicing 反推。[4]

frozen openpi Pi0 实际先：

$$
\ell_{b,h}
=
\frac{1}{D}
\sum_{j=1}^{D}
\left(v_{b,h,j}-u_{b,h,j}\right)^2,
$$

训练脚本再对 \(b,h\) mean。变量与风险：configured \(D\) 中的 padded zero targets 也进入 denominator 和 gradient；`PadStatesAndActions` 与推理 output slice 不能替代 loss mask。它未必造成训练错误——模型可以学输出零——但会改变有效维 loss 权重，并可能让平均 loss 被大量容易 padding 维稀释。[4]

### 10.2 mask 的四个层次

| mask / slice | 作用阶段 | 能解决 | 不能解决 |
| --- | --- | --- | --- |
| image/prompt attention mask | model input | 缺失 modality / token padding | action loss validity |
| action timestep mask | training loss | episode/chunk padding | action axis 语义 |
| action dimension mask | training loss | \(d<D\) 的无效轴 | controller reorder |
| output slicing / transform | inference | model D 到 env d | 训练期 padding gradient |

### 10.3 conditional dropout / guidance 的 action 风险

Flow package image example足以支持 CFG 机制公式，但不足以证明 openpi action policy 已用 CFG。若要为 action generation 补做：

1. 明确 dropout unit：只 drop language，还是同时 drop images/state；
2. 训练 conditional 与 unconditional branches 使用同一 action/noise/time；
3. 记录实际 model forwards，而不是只报 solver NFE；
4. 检查 guidance 后 normalized action magnitude、axis safety 和 temporal smoothness；
5. 比较 task compliance、diversity、success 与 latency，而不是只看 velocity MSE。

因此 `VLA-ACT-029` 当前是 source-ready with warning：有通用 flow CFG supporting code，没有 frozen action-policy positive evidence。

## 11. Loss 正常但 rollout 失败：四层 invariant debugging

### 11.1 Layer A：target / path algebra

先用固定 \(A,\epsilon,t\) 做 hand-check：

$$
x_t=t\epsilon+(1-t)A,
\qquad
u_t=\epsilon-A.
$$

检查 endpoint、shape、dtype、time distribution 和 target sign；用 oracle field \(v=u_t\) 做一次完整 Euler integration，确认能从同一 noise 回到 \(A\)。这一步失败，问题在 target/path/solver，不应先调 controller。[4]

### 11.2 Layer B：solver / scheduler

| Flow 必查 | Diffusion 必查 |
| --- | --- |
| time grid 升降序 | train/inference scheduler 是否匹配 |
| velocity sign 与 \(dt\) | prediction type epsilon/sample/v |
| Euler steps / adaptive NFE | beta schedule / DDIM steps |
| endpoint 与 off-by-one | `set_timesteps` / step order |
| fixed noise reproducibility | generator / stochastic variance |

先 overfit tiny batch，再用相同 observation 和固定 noise 对比：一步误差、十步 endpoint、不同 NFE 收敛趋势。若增加 flow steps 反而稳定发散，优先怀疑 sign、scale 或 time conditioning。

### 11.3 Layer C：normalization、mask 与 action schema

执行：

- normalize → unnormalize round-trip；
- q01/q99 或 min/max 的 checkpoint / dataset ID 对齐；
- 每轴 sentinel：只激活一个 action dimension，追到 controller；
- \(d/D\)、padding、loss denominator 与 output slice 对齐；
- horizon padding / episode boundary 是否进入 loss；
- action unit、position/velocity、delta/absolute 与 gripper convention。

offline loss 对 normalized tensor 正常，只能证明模型拟合了这个 tensor contract；它不证明 tensor 与真实 controller contract 一致。

### 11.4 Layer D：online controller / queue

固定一段已知安全 action，不经过模型直接走 output transform 和 controller，检查：

- \(H\) 是 model output horizon，\(K\) 是执行/replan prefix；
- control frequency、timestamp、queue drop 和 network latency；
- axis reorder、clip、安全限幅与 termination；
- camera resize/flip、state timestamp 与 action observation alignment；
- rollout summary 绑定 exact checkpoint、task、seed、trial count。

```python
def debug_flow_rollout(batch, policy, controller):
    # A. Verify path algebra with fixed data/noise/time and an oracle velocity.
    assert_oracle_integration_recovers_action(batch.actions)

    # B. Freeze observation and noise; compare solver endpoints across step counts.
    endpoints = sweep_flow_steps(policy, batch.observation, fixed_noise=True)
    check_convergence_and_time_sign(endpoints)

    # C. Round-trip every valid action axis through normalization and transforms.
    assert_action_transform_roundtrip(batch.action_schema)
    run_per_axis_sentinel_tests(policy.output_transform)

    # D. Bypass the model and execute a known-safe controller sequence.
    assert_controller_contract(controller, batch.safe_action_fixture)
```

伪代码说明：四层按因果距离从模型 objective 到真实控制排列；每层产生可保存的 test artifact。它是面试中的 debug framework，不代表这些 tests 已在本地 OpenPiVLA 跑过。

## 12. Claim-to-code 总表

| Claim | 基础论文 | frozen package / openpi | 判定 | 安全面试口径 |
| --- | --- | --- | --- | --- |
| FM 直接回归 clean data/action | velocity field | `dx_t` / `u_t` MSE | rejected | 回归 path velocity |
| FM training 要先解 ODE | simulation-free training | path sample 解析构造 | rejected | inference 才解 ODE |
| FM 完全不需要 solver | CNF sampling | `odeint` / Euler loop | rejected | sampling 需要 |
| CFM loss 与 FM 每项数值相等 | identical gradients | conditional sample MSE | rejected | 对 \(\theta\) 梯度相同 |
| 所有 FM 都是线性插值 | general Gaussian paths | 多 scheduler | rejected | linear CondOT 是特例 |
| 原论文 OT endpoint 必为 exact data | 保留 \(\sigma_{\min}\) | package exact endpoint | rejected | 报 paper/package 差异 |
| current package 是 2022 paper 历史代码 | 无 | 2026 maintained package | rejected | 只作现代 API 补证 |
| `flow_matching.loss` 自动提供 continuous MSE | objective in paper | continuous example手写 MSE | rejected | path 给 target，用户算 MSE |
| π0 flow target 是 epsilon | \(A-\epsilon\) velocity | code \(\epsilon-A\) | rejected | 是 time-reversed velocity |
| paper/code 反向所以不等价 | paper 0→1 | code 1→0 | rejected | time 与 velocity 同时翻转 |
| openpi Beta time 偏离 π0 | shifted Beta | reverse-coordinate exact mapping | rejected | 公式换元后对齐 |
| 10 steps 是 action horizon | 10 integrations | `num_steps` | rejected | flow NFE 与 H/K 分开 |
| padded D 不影响 loss | 无该保证 | Pi0 all-D mean | rejected as universal | 需 explicit mask/evidence |
| output slice 等于 loss mask | 无 | transform 与 loss 分离 | rejected | train/infer 分层 |
| package CFG 证明 π0 已用 guidance | generic image example | openpi 无对应 branch | rejected | 仅 supporting mechanism |
| Flow 比 Diffusion 快是定义事实 | 无 | recipe-dependent | rejected | 报 model/NFE/hardware |
| upstream 可证明本地 97.4% | 无 | 无 local eval | rejected | 必须绑定本地 artifact |

## 13. 对 `VLA-ACT-023..030` 的支持状态

| ID | 覆盖 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ACT-023 | probability path、CNF、velocity field、continuity intuition | source-ready | independent review |
| VLA-ACT-024 | CFM、linear/OT path、target velocity 与 MSE 推导 | source-ready with paper/package boundary | 手算题与口述 |
| VLA-ACT-025 | ODE solver、Euler、time grid、π0 10-step loop | source-ready | target hardware telemetry |
| VLA-ACT-026 | epsilon prediction vs velocity prediction、scheduler vs ODE | source-ready | 同 checkpoint controlled comparison |
| VLA-ACT-027 | VLM prefix、state/noisy action/time suffix、`[B,H,D]` output | source-ready | local OpenPiVLA model class |
| VLA-ACT-028 | all-D mean、理想 mask、padding/slice 分层 | source-ready with warning | positive local mask implementation |
| VLA-ACT-029 | generic flow CFG training/inference mechanism | source-ready with warning | action-policy implementation与安全实验 |
| VLA-ACT-030 | target/solver/norm/controller 四层 debug | source-ready as framework | 本地 tests、logs 与 failure traces |

`source-ready` 只表示可进入后续知识页与题卡起草；本页不创建题卡，也不改变 `unseen` 练习状态。

## 14. 与个人 OpenPiVLA 项目的真实性边界

| 上游可确认 | 可用于本地核验问题 | 不能直接迁移 |
| --- | --- | --- |
| π0 linear flow path | 本地 `x_t` / target / time convention | 不证明本地 model 是 Pi0 |
| openpi `[B,H,D]` action expert | 查本地 forward / loss / config | 不证明 H、D 数值 |
| shifted Beta timestep | 查本地 sampler / seed | 不证明本地采用同分布 |
| default 10 Euler steps | 查 runtime override | 不证明本地 latency |
| prefix cache / suffix recompute | 查本地 architecture | 不证明 Qwen action head |
| all-D mean risk | 查 mask / padding test | 不证明已发生污染 |
| package CFG example | 设计 advanced ablation | 不证明本地 guidance |
| public solver behavior | 设计 oracle integration test | 不证明本地 97.4% |

进入项目强回答前仍需本地 artifact：

1. exact model class、base checkpoint 与 startup manifest；
2. data action shape、axis/order/unit、normalization stats 与 output transform；
3. `compute_loss` / target builder / timestep sampler / valid mask；
4. model \(H,D\)、真实 \(d\)、execution prefix \(K\) 与 control frequency；
5. solver type、runtime steps、fixed-noise test 与 latency breakdown；
6. exact eval checkpoint、task/split、trials、seed、success summary；
7. upstream/local diff 与本人设计、实现、实验贡献边界。

在这些证据缺失时，安全说法是：“我能用 Flow Matching / π0 的公开机制解释候选 action head，并已把需要核验的 target、time、mask、normalization 与 controller contract 列成检查项”；不能说“我主导设计了 π0 action expert”或“上游默认证明本地达到 97.4%”。

## 15. 面试安全口径与危险答案

### 15.1 30 秒安全骨架

“Flow Matching 先选一条从 noise distribution 到 data distribution 的 probability path，再训练网络预测这条路径上的 velocity field。直接的 marginal field 难算，所以 CFM 对每个 data sample 构造 conditional path；论文证明 CFM 与 FM 对参数的梯度相同。最常用的 CondOT 特例是 \(x_t=(1-t)x_0+tx_1\)，target 是 \(x_1-x_0\)，但它不是全部 FM。π0 把 \(x_1\) 换成整个 action chunk，用图像、语言和 state 作 condition；openpi 反向时间积分，因此 target 和步长一起取反，默认 10 次 Euler。与 Diffusion Policy 相比，它预测 continuous velocity 并解 ODE，而 frozen Diffusion Policy 默认预测 epsilon 并走 scheduler；两者的 horizon、sampling steps 和 controller replan 都必须分开。”

### 15.2 2 分钟展开锚点

1. CNF ODE 与 \(p_t\)；
2. FM marginal target 难算；
3. CFM conditional sample 与 gradient equivalence；
4. Gaussian affine path → CondOT linear special case；
5. π0 `[B,H,D]`、shifted Beta time、VLM/action expert；
6. openpi time/sign/Euler 等价；
7. Diffusion epsilon/scheduler 对照；
8. mask/norm/controller 的 closed-loop 防线。

### 15.3 高危说法

- “Flow Matching 直接预测 clean action。”——它预测 velocity。
- “CFM 和 FM loss 数值完全一样。”——论文证明 gradient equivalence。
- “所有 Flow Matching 都是线性插值。”——一般 Gaussian / diffusion paths 都可用。
- “原论文 CondOT 就严格到 data endpoint。”——Eq. 20 保留 \(\sigma_{\min}\)。
- “simulation-free 表示推理也不用迭代。”——sampling 仍解 ODE。
- “openpi 和 π0 paper 方向相反，所以代码错了。”——time 和 velocity 同时翻转。
- “Beta timestep 是 openpi 自己改坏的。”——反向换元后与 π0 recipe 对齐。
- “10 是 action horizon。”——是 flow integration steps。
- “Flow 本质上一定比 Diffusion 少步/更快。”——取决于 model、solver、NFE 和硬件。
- “padding 最后 slice 掉就不影响训练。”——loss 已可能监督 padding。
- “官方 flow package 有 CFG，所以 π0 默认有 guidance。”——没有对应 frozen action path 证据。
- “loss 降了说明 controller 没问题。”——norm、axis、H/K 和 queue 仍可错。

## 16. 风险、未决项与下一步

1. **核心高风险事实已独立复核**：Theorem 2、paper `sigma_min` endpoint、π0/OpenPI time-sign-dt、shifted Beta 与 deterministic oracle 已在 [独立复核页](vol_03_flow_pi0_time_sign_independent_fact_review.html) 闭合，公共事实层为 `PASS WITH WARNING`；local runtime、mask、controller、ownership 与 oral drill 仍使本页整体保持 `WARN/PENDING`。
2. **arXiv source tar 不可靠**：下载对象达到服务器 Content-Length，但本地 tar 读取报告 truncated；公式最终以完整 ar5iv/arXiv HTML v2 的 equation anchors 核验，不能声称 TeX source 已成功解包。
3. **current package 不是 historical implementation**：只把它用于 modern path/solver/CFG API evidence。
4. **\(\sigma_{\min}\) 边界要保留**：题卡中同时给 paper form 与 exact-linear special case。
5. **CFG 只到 supporting evidence**：进入 action strong answer 前需本地实现与 safety/latency ablation。
6. **mask 仍缺 positive local evidence**：Source Audit B/E 只能证明 frozen Pi0 all-D mean 与风险，不能虚构已实现 valid-dim mask。
7. **题卡已分批生成**：累计 Batch 2B 已完成本页对应的 `VLA-ACT-023..030`，8 张新卡均保持 `unseen`；后续只做 independent review 与真实口述，不倒填 mastery。
8. **个人项目继续等待 artifact**：checkpoint、action schema、solver、H/K、97.4% 与个人贡献不得由 upstream 代证。
9. **视觉 QA 已完成**：通过 localhost 静态服务检查桌面 `1440×1000` 与窄屏 `800×1000`；确认一处 H1、academic palette/serif、desktop sticky TOC、narrow static TOC、公式无 `<em>` 污染且无页面级横向溢出。`arXiv source tar` 的 truncated 仍保留为独立证据风险。

## 参考文献（References）

1. Lipman et al., [Flow Matching for Generative Modeling](https://arxiv.org/html/2210.02747v2), arXiv `2210.02747v2`, 2023；重点为 [Section 2 CNF](https://arxiv.org/html/2210.02747v2#S2)、[Section 3 FM / CFM](https://arxiv.org/html/2210.02747v2#S3)、[Section 4 conditional paths](https://arxiv.org/html/2210.02747v2#S4) 与 [Appendix B continuity equation](https://arxiv.org/html/2210.02747v2#A2)。
2. [facebookresearch/flow_matching](https://github.com/facebookresearch/flow_matching/tree/11568d37f8d5a080e12aa7b5305d9c35ae07d136), frozen commit `11568d37f8d5a080e12aa7b5305d9c35ae07d136`, CC BY-NC 4.0；核心路径：[`affine.py`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/flow_matching/path/affine.py)、[`scheduler.py`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/flow_matching/path/scheduler/scheduler.py)、[`ode_solver.py`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/flow_matching/solver/ode_solver.py)、[`continuous train example`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/examples/image/training/train_loop.py)、[`CFG eval wrapper`](https://github.com/facebookresearch/flow_matching/blob/11568d37f8d5a080e12aa7b5305d9c35ae07d136/examples/image/training/eval_loop.py)。
3. Black et al., [π0: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/html/2410.24164v4), arXiv `2410.24164v4`, 2024；重点为 [model/action flow](https://arxiv.org/html/2410.24164v4#S4) 与 [timestep sampling appendix](https://arxiv.org/html/2410.24164v4#A1.SS2)。
4. [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), frozen commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`, Apache-2.0；核心路径：[`pi0.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0.py)、[`pi0_config.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_config.py)、[`train.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/scripts/train.py)。
5. [Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Claim-to-Code](vol_03_diffusion_policy_claim_to_code.html)，本仓库 Source Audit D，2026-07-16。
6. [π0 / π0.5 / FAST / openpi Claim-to-Code](vol_03_pi0_fast_openpi_claim_to_code.html)，本仓库 Source Audit B，2026-07-16。
7. [ACT CVAE、Action Chunking 与 Temporal Aggregation Claim-to-Code](vol_03_act_claim_to_code.html)，本仓库 Source Audit C，2026-07-16。
8. [Flow Matching / π0 Time–Sign 独立事实复核](vol_03_flow_pi0_time_sign_independent_fact_review.html)，本仓库二次 primary/frozen-source 复核与 deterministic oracle，2026-07-19。
