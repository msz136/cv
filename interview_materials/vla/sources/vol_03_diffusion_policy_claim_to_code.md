# VOL 03 Source Audit D：Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Claim-to-Code

> 审计日期：2026-07-16  
> 状态：`drafted / upstream_paper_and_code_reviewed / independent_review_pending`  
> 论文版本：*Diffusion Policy: Visuomotor Policy Learning via Action Diffusion*，arXiv `2303.04137v5`  
> 官方仓库：`real-stanford/diffusion_policy` frozen commit `5ba07ac6661db573af695b419a7947ecb704690f`  
> License：MIT；关键依赖：Hugging Face `diffusers=0.11.1`  
> 对应题目：`VLA-ACT-018..022`；`VLA-ACT-017` 的 diffusion 对照  
> 本页问题：Diffusion Policy 为什么能表示多模态连续动作？训练时 noisy action、noise target、condition 与 mask 如何组织？observation / prediction / execution horizon 如何进入代码？receding-horizon、DDIM、去噪步数和 warm-start 在论文与 frozen repo 中是否一致？

## 1. 结论先行

1. **Diffusion Policy 把 visuomotor policy 写成条件 action-sequence diffusion，而不是逐维 token 分类。**时刻 \(t\) 接收最近 \(T_o\) 步 observation，建模未来 action sequence 的条件分布 \(p_\theta(A_t\mid O_t)\)；论文记作 \(T_p\)，官方代码叫 `horizon`。[1][2]
2. **训练目标是随机 timestep 的 noise/sample MSE。**代码对标准化 trajectory 加 scheduler noise；`prediction_type=epsilon` 时 target 是同形状 Gaussian noise，`sample` 时 target 是 clean trajectory。该 policy 代码只显式支持 epsilon/sample，不自动处理 `v_prediction`。[2][3]
3. **默认 image hybrid 路径是 global conditioning。**前 \(T_o\) 帧经视觉 encoder 成为扁平 `global_cond`，diffusion trajectory 只保留 action channels，初始采样为 \([B,T_p,D_a]\) 的 Gaussian noise；默认 global path 的 action condition mask 全 False。[2]
4. **模型 horizon、返回 action 数和真正 replanning interval 必须分开。**`horizon=T_p`；`n_action_steps=T_a` 决定 `predict_action` 返回多少步；simulation 的 `MultiStepWrapper` 一次执行 \(T_a\) 步后再 query，real eval 可提交更长 action slice、每 `steps_per_inference` 步重算。[2]
5. **官方 action slice 从最后一帧 observation 对齐。**`start=n_obs_steps-1`，`end=start+n_action_steps`；例如 \(T_p=16,T_o=2,T_a=8\) 时，完整 trajectory 有 16 步，返回 index 1 到 8 的 8 步。[2]
6. **paper 说 receding-horizon 可以 warm-start 下一次 inference；该 frozen commit 没实现。**主要 policy 都从 `torch.randn` 重新开始，并在入口拒绝 `past_action`。所以“论文支持 warm-start”不能讲成“这个 commit 默认用上一段 action 初始化”。[1][2]
7. **论文正文、论文表格和 code 的 inference step 数不是统一常数。**论文正文给 DDIM 100 train / 10 eval 的 real-world 例子；v5 表格的 real rows 为 16 eval；frozen real configs 为 8，`eval_real_robot.py` 又运行时设为 16。[1][2]
8. **多模态来自 sequence-level stochastic generation，而非每个时间点独立采样。**随机 Gaussian 初值和 DDPM/DDIM transition 提供多样性；一次对整段 \(T_p\times D_a\) trajectory 去噪，使相邻动作共享同一生成过程。[1]

## 2. 证据层级、冻结对象与适用边界

| 层级 | 本页使用方式 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| arXiv v5 | formulation、horizons、network/noise schedule、DDIM 与 ablation | 方法定义、论文符号、公开实验和 warm-start 设计意图 | frozen repo 的实际 default 与个人项目事实 |
| frozen official repo | policy、dataset、sampler、runner、real eval、YAML | tensor shape、mask、normalization、action slice、执行/重规划路径 | 个人 OpenPiVLA 是否采用该实现 |
| frozen dependency | diffusers 0.11.1 DDPMScheduler/DDIMScheduler | `add_noise`、prediction type、`set_timesteps`、`step` 语义 | 不能替代 policy 自己的 loss/mask |
| 同源推断 | paper/code 联合推导 \(T_o/T_p/T_a\)、latency 与 stochasticity | 面试解释的 interface contract | 未运行的 latency/success |

冻结信息：

- arXiv API 的唯一 latest entry 是 `2303.04137v5`，更新时间 2024-03-14；v5 是 extended journal version。[1]
- 官方 repo HEAD 为 `5ba07ac6661db573af695b419a7947ecb704690f`，commit message 为 `Done adapting mujoco image dataset`；根目录 LICENSE 为 MIT。[2]
- repo `conda_environment.yaml` 固定 `diffusers=0.11.1`、PyTorch 1.12.1、Hydra 1.2.0。[2]
- 代表实现为 `DiffusionUnetHybridImagePolicy` 与 `DiffusionTransformerHybridImagePolicy`；lowdim policy 共享 scheduler、loss、horizon 和 inference contract。

## 3. 论文符号与三个 horizon

论文定义：

$$
O_t=(o_{t-T_o+1},\ldots,o_t),\qquad
A_t=(a_t,\ldots,a_{t+T_p-1}),
$$

其中 \(T_o\) 是 observation horizon，\(T_p\) 是 action prediction horizon，\(T_a\) 是 action execution horizon。policy 用 \(O_t\) 预测 \(T_p\) 步，只执行 \(T_a\) 步，随后重新观察并规划。[1]

变量与直觉：\(T_o\) 决定历史长度，\(T_p\) 决定一次 diffusion 生成多长 trajectory，\(T_a\) 决定多久才吸收新 observation。实现映射：`n_obs_steps`、`horizon`、`n_action_steps` 在 [`train_diffusion_unet_hybrid_workspace.yaml#L12-L20`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/config/train_diffusion_unet_hybrid_workspace.yaml#L12-L20) 与 policy constructor [`diffusion_unet_hybrid_image_policy.py#L22-L40`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L22-L40) 对应。

| 概念 | frozen field | 作用 | 不能混同 |
| --- | --- | --- | --- |
| observation horizon \(T_o\) | `n_obs_steps` | encoder 使用 `obs[:,:To]` | 不等于全部 episode history |
| prediction horizon \(T_p\) | `horizon` | diffusion trajectory 时间维 | 不等于返回 action 数 |
| execution window \(T_a\) | `n_action_steps` | action slice 长度 | 不自动等于 real query interval |
| replan interval \(R\) | simulation 的 action batch；real CLI `steps_per_inference` | 多少控制步后再次 inference | 不由 `horizon` 单独决定 |
| diffusion steps \(K\) | `num_inference_steps` | 一次 query 内的 denoising iterations | 不是机器人控制步数 |

## 4. Conditional DDPM：训练目标与前向加噪

### 4.1 论文 objective

论文以 clean action sequence \(A_t^0\) 为样本，随机选 diffusion timestep \(k\)，采样 \(\epsilon\)，让网络根据 observation、noisy action 和 \(k\) 预测噪声：

$$
A_t^k
=\sqrt{\bar\alpha_k}\,A_t^0
 +\sqrt{1-\bar\alpha_k}\,\epsilon,
\qquad
\epsilon\sim\mathcal N(0,I),
$$

$$
\mathcal L_\epsilon
=\mathbb E_{A_t^0,O_t,k,\epsilon}
\left[
\left\|\epsilon-\epsilon_\theta(O_t,A_t^k,k)\right\|_2^2
\right].
$$

变量与直觉：\(\bar\alpha_k\) 由 beta/noise schedule 决定；较小 \(k\) 保留更多 action signal，较大 \(k\) 更接近 Gaussian。网络学习去噪方向而不是直接回归 clean action。论文 Section DDPM/DDPM Training 见 [HTML](https://arxiv.org/html/2303.04137v5#S2)；repo 的 `add_noise` 映射到 diffusers v0.11.1 [`scheduling_ddpm.py#L329-L350`](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddpm.py#L329-L350)。

论文把反向 transition 写成：

$$
A_t^{k-1}
=\alpha_k\left(
A_t^k-\gamma_k\epsilon_\theta(O_t,A_t^k,k)
+\mathcal N(0,\sigma_k^2I)
\right).
$$

这表示网络输出与 scheduler 共同定义 reverse update；不能把 \(\epsilon_\theta\) 单独当最终 action。系数、variance 和 clipping 由 DDPM/DDIM scheduler 完成。[1][2]

### 4.2 Frozen training path

```python
def training_step(batch, policy):
    # Normalize observations and the action trajectory.
    nobs = policy.normalizer.normalize(batch["obs"])
    nactions = policy.normalizer["action"].normalize(batch["action"])

    # Encode the first To observations and build the trajectory contract.
    cond_data, trajectory, global_cond = build_condition(nobs, nactions)

    # Sample one diffusion timestep and Gaussian noise per batch item.
    noise = torch.randn_like(trajectory)
    timesteps = torch.randint(
        0, policy.noise_scheduler.config.num_train_timesteps,
        (trajectory.shape[0],), device=trajectory.device
    )
    noisy = policy.noise_scheduler.add_noise(trajectory, noise, timesteps)

    # Re-impose hard conditions after adding noise.
    condition_mask = policy.mask_generator(trajectory.shape)
    noisy[condition_mask] = cond_data[condition_mask]

    # Predict epsilon or the clean sample and apply the masked MSE.
    pred = policy.model(noisy, timesteps, global_cond=global_cond)
    target = noise if policy.noise_scheduler.config.prediction_type == "epsilon" \
        else trajectory
    loss = ((pred - target) ** 2 * (~condition_mask)).mean()
    return loss
```

直接代码证据：normalization/trajectory 在 [`diffusion_unet_hybrid_image_policy.py#L284-L314`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L284-L314)，noise/timestep/add_noise 在 [`#L316-L337`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L316-L337)，target 与 MSE 在 [`#L339-L351`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L339-L351)。

### 4.3 `prediction_type` 与 mask

$$
y_\theta=
\begin{cases}
\epsilon,&\texttt{prediction\_type}=\texttt{epsilon},\\
A_t^0,&\texttt{prediction\_type}=\texttt{sample}.
\end{cases}
$$

变量与实现：policy 只处理 epsilon/sample，其他字符串直接 `ValueError`。diffusers scheduler 虽有 `v_prediction` 分支，policy 的 `compute_loss` 没实现对应 velocity target；依赖库能力不等于当前 policy 能力。证据为 [`diffusion_unet_hybrid_image_policy.py#L339-L345`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L339-L345) 与 [`scheduling_ddpm.py#L278-L289`](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddpm.py#L278-L289)。

`loss_mask = ~condition_mask` 后用完整 tensor mean；conditioned dimensions 的 numerator 被置零，但 denominator 仍是 trajectory 总元素数。policy 还 assert batch 不带 `valid_mask`。默认 `obs_as_global_cond=True` 时 `obs_dim=0`、`action_visible=False`，action channels 全部参与 MSE；non-global/inpainting path 才把前 \(T_o\) observation-feature dimensions 固定并排除。[2]

### 4.4 为什么 sequence diffusion 能表达多模态

$$
p_\theta(A_t\mid O_t)
\neq
\prod_{h=0}^{T_p-1}p_\theta(a_{t+h}\mid O_t).
$$

一次去噪对象是整段联合 trajectory，不是每个时间点独立的 categorical/Gaussian head。同一噪声初值和 temporal network 让“向左绕/向右绕”等 mode 形成连贯 sequence；这是论文设计解释，不是 repo 显式计算的概率分解。[1]

## 5. Observation conditioning 与网络实现

### 5.1 CNN / UNet hybrid

论文 CNN policy 用视觉 encoder 生成 \(O_t\) latent，通过 FiLM 将 observation feature 和 diffusion timestep 注入 1D temporal U-Net。repo 的 `ConditionalUnet1D` 将 timestep embedding 与 global visual condition 拼接，并在 residual blocks 生成 per-channel scale/bias：

```text
image sequence [B, To, C, H, W] + lowdim obs
             |
             v
ResNet18 observation encoder (GroupNorm / fixed crop)
             |
             v
global_cond [B, To * Do]
             |
random noisy action trajectory [B, Tp, Da]
             |
             v
ConditionalUnet1D + timestep FiLM
             |
             v
predicted epsilon/sample [B, Tp, Da]
```

`obs_as_global_cond=True` 时 `input_dim=action_dim`、`global_cond_dim=obs_feature_dim*n_obs_steps`，见 [`diffusion_unet_hybrid_image_policy.py#L129-L146`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L129-L146)。FiLM scale/bias 在 [`conditional_unet1d.py#L14-L66`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/model/diffusion/conditional_unet1d.py#L14-L66)，global feature concat 在 [`#L173-L201`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/model/diffusion/conditional_unet1d.py#L173-L201)。

论文 visual encoder 为每个 camera 使用 separate ResNet-18、空间 softmax 和 GroupNorm；代码由 robomimic config 建立 encoder，并可用 `obs_encoder_group_norm=True`、`eval_fixed_crop=True` 替换 BN/随机 crop。camera 数、action dimensions、absolute/velocity semantics 由 task `shape_meta` 决定。

### 5.2 Time-series diffusion transformer

Transformer variant 将 noisy action sequence 作为 \(T_p\) 个 token，扩散 timestep embedding 作为 condition；视觉 observation sequence 变为 condition embedding，decoder cross-attend 到 condition memory，输出每个 action token 的 residual。`TransformerForDiffusion.forward` 的 contract 是 input `[B,T,input_dim]`、cond `[B,T_o,cond_dim]`、output `[B,T,input_dim]`，见 [`transformer_for_diffusion.py#L270-L344`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/model/diffusion/transformer_for_diffusion.py#L270-L344)。

默认 transformer hybrid config 是 \(T_p=10,T_o=2,T_a=8\)、causal attention、8 layers、256 embedding、DDPM 100 train / 100 inference；real hybrid 改为 \(T_p=16,T_o=2,T_a=8\)、DDIM 8 inference。[2] 论文建议先用 CNN；action sequence 变化快时再试 transformer，但 transformer 对超参更敏感。[1]

## 6. Inference：随机初始化、denoising loop 与 action slice

### 6.1 Global-conditioned inference

`predict_action` 的顺序：

1. normalize observation；
2. 只取 `obs[:, :To]` 过 vision encoder；
3. 建立全零 `cond_data`，形状 `[B,Tp,Da]`，`cond_mask` 全 False；
4. 以同形状 Gaussian noise 初始化 trajectory；
5. `scheduler.set_timesteps(num_inference_steps)`，依次执行 `scheduler.step(...).prev_sample`；
6. 从 `nsample[...,:Da]` unnormalize，再从 `start=To-1` 切出 `Ta` 步。

$$
X^{(K)}\sim\mathcal N(0,I),\qquad
X^{(k-1)}=\operatorname{SchedulerStep}
\left(X^{(k)},f_\theta(X^{(k)},k,O_t)\right),
$$

$$
\hat A_t=
\operatorname{Unnormalize}\!\left(
X^{(0)}_{:,\;To-1:To-1+T_a,\;:D_a}
\right).
$$

变量与实现：\(K\) 是 diffusion steps，\(T_p\) 是 trajectory time，\(T_a\) 是返回 action 数。UNet hybrid random init/scheduler loop 在 [`#L175-L212`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L175-L212)，condition/action slice 在 [`#L215-L278`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py#L215-L278)。Transformer hybrid 同构路径见 [`#L183-L219`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_transformer_hybrid_image_policy.py#L183-L219) 与 [`#L222-L290`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_transformer_hybrid_image_policy.py#L222-L290)。

### 6.2 Paper warm-start 与 code random restart

论文称 receding-horizon formulation 可以用上一段 action prediction warm-start 下一轮 inference。[1] frozen repo 的主要 policy paths 都是：

```python
def conditional_sample(condition_data, condition_mask):
    # Every query in this commit starts from fresh Gaussian noise.
    trajectory = torch.randn(condition_data.shape, device=condition_data.device)

    # The scheduler determines descending diffusion timesteps.
    scheduler.set_timesteps(num_inference_steps)
    for t in scheduler.timesteps:
        # Re-impose hard conditions before each denoising step.
        trajectory[condition_mask] = condition_data[condition_mask]
        model_output = model(trajectory, t, global_cond=global_cond)
        trajectory = scheduler.step(model_output, t, trajectory).prev_sample
    return trajectory
```

`predict_action` 还 assert `past_action` 不在 observation dict，因此没有 previous `action_pred` 初值或 warm-start buffer。[2]

| 说法 | 判定 |
| --- | --- |
| 论文提出 warm-start 作为 receding-horizon 可用选项 | direct paper claim |
| frozen repo 默认 eval 使用 warm-start | rejected |
| code stochasticity 只来自 scheduler step | rejected；还有 initial `torch.randn` |
| 固定 generator/seed 可复现同一输入 | 同源推断，需目标设备/版本实测 |

### 6.3 DDPM、DDIM、去噪步数

| 路径 | scheduler | train timesteps | config inference steps | 备注 |
| --- | --- | ---: | ---: | --- |
| UNet hybrid | DDPMScheduler | 100 | 100 | squared-cosine、epsilon、fixed_small |
| UNet DDIM hybrid | DDIMScheduler | 100 | 8 | inference grid 抽稀 |
| real UNet hybrid | DDIMScheduler | 100 | 8 | frozen real config |
| `eval_real_robot.py` diffusion branch | loaded scheduler | checkpoint-dependent | 强制 16 | runtime override |
| paper main text example | DDIM | 100 | 10 | 3080 / 0.1s 叙述 |
| paper v5 real table rows | task rows | 100 | 16 | 与 main text 不完全一致 |

DDIM 将 train grid 与 inference steps 解耦；减少 \(K\) 降低 query compute，但改变 reverse approximation。`DDIMScheduler.set_timesteps`/`step` 见 [`scheduling_ddim.py#L196-L214`](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddim.py#L196-L214) 与 [`#L249-L334`](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddim.py#L249-L334)。

## 7. Normalization、padding 与数据切片

### 7.1 默认 \([-1,1]\) normalizer

PushT image dataset 对 action 与 agent position 统计 min/max，`LinearNormalizer.fit(..., mode='limits')` 将每维映射到 \([-1,1]\)；图像先除以 255，再做 \(x\mapsto2x-1\)。[2]

$$
\tilde x_i
=\frac{2(x_i-x_i^{\min})}{x_i^{\max}-x_i^{\min}}-1,
\qquad
x_i=
\frac{\tilde x_i+1}{2}(x_i^{\max}-x_i^{\min})+x_i^{\min}.
$$

变量与直觉：每个 axis 独立 scale；near-constant dimension 特殊处理避免除零。实现见 [`pusht_image_dataset.py#L60-L68`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/dataset/pusht_image_dataset.py#L60-L68)、[`normalize_util.py#L6-L35`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/common/normalize_util.py#L6-L35) 与 [`normalizer.py#L182-L261`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/model/common/normalizer.py#L182-L261)。`clip_sample=True` 又会在 scheduler 侧限制 clean prediction，因此 stats 与 clipping 是联合 contract。

### 7.2 Boundary padding 不是 valid loss mask

PushT dataset 以 `sequence_length=horizon` 建 SequenceSampler，用 `pad_before=To-1`、`pad_after=Ta-1` 让 episode 边界也能采样。[2] sampler 在边界重复第一/最后一个真实 frame/action，见 [`sampler.py#L121-L153`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/common/sampler.py#L121-L153)。

因此 default boundary padding 是 repeated values，不是 NaN 或显式 valid mask；policy 又要求 batch 不带 `valid_mask`，这些 repeated targets 会按普通 actions 进入 MSE。不能见到 `pad_after` 就说 padded positions 不监督。

### 7.3 Normalizer 数据范围

`PushTImageDataset.get_normalizer` 从完整 replay buffer 的 action/state 拟合；sampler 的 train/validation episode mask 不会自动限制 stats。[2] 这是该 dataset implementation 的复现边界，不等于所有 dataset 都有 validation leakage；要先报具体 dataset class。

## 8. Receding-horizon rollout：simulation 与 real robot

### 8.1 Simulation

`PushTImageRunner` 每次 query 得到 `[B,T_a,D_a]`，再把整段 action 传给 `MultiStepWrapper.step`；wrapper 内部逐 action 调 env，执行 \(T_a\) 步后返回最近 \(T_o\) 个 observation。[2]

```python
def simulation_rollout(env_wrapper, policy):
    # Reset and receive the latest To observations.
    obs = env_wrapper.reset()
    policy.reset()
    while not done:
        # K denoising steps produce Tp, then policy returns Ta actions.
        action_chunk = policy.predict_action(obs)["action"]
        # Wrapper executes Ta actions before returning a new observation stack.
        obs, reward, done, info = env_wrapper.step(action_chunk)
```

证据：query/step 在 [`pusht_image_runner.py#L176-L214`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/env_runner/pusht_image_runner.py#L176-L214)，wrapper action loop 在 [`multistep_wrapper.py#L101-L124`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/gym_util/multistep_wrapper.py#L101-L124)。

### 8.2 Real robot

`eval_real_robot.py` diffusion branch 将 `num_inference_steps` 设为 16，并把 `n_action_steps` 改成 `horizon-n_obs_steps+1`，尽量返回从最后 observation 对齐后的整段 action。[2] 外层 `steps_per_inference` 是 CLI 参数，默认 6；它决定多久再读 real observation。action 带 timestamp 提交给 controller，超时则只提交最后一项。[2]

所以有三个长度：

1. diffusion trajectory \(T_p\)，例如 16；
2. `predict_action` slice，可能是 \(T_p-T_o+1=15\)；
3. 外层 query interval，默认 6，还受 observation/inference/controller latency 影响。

“每次执行 15 步后才重规划”是错误的；script 可能提交 15 个未来 targets，但下一次 query 由 6-step schedule 和实时预算决定。证据：[`eval_real_robot.py#L90-L118`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/eval_real_robot.py#L90-L118) 与 [`#L294-L345`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/eval_real_robot.py#L294-L345)。

## 9. Horizon、去噪步数与 latency trade-off

### 9.1 \(T_p/T_a\) 太短

sequence-level consistency 变弱；若 \(T_a\) 同步变短，query 次数增加、inference overhead 上升；但 observation 刷新更快，对扰动更 responsive。

### 9.2 \(T_p/T_a\) 太长

long trajectory 提供更强 sequence modeling buffer；若 \(T_a\) 也变长，replan 变稀疏，stale action 和 latency 风险上升。U-Net/Transformer 时间维与每次 denoising 计算共同影响显存和吞吐。

论文把 action horizon 说成 temporal consistency 与 responsiveness 的 trade-off，并把 latency 定义为“最后一帧 observation 到第一条可执行 action 之间的 step 数”。[1] 该延迟不只由 `num_inference_steps` 决定。

### 9.3 \(K\) 太少或太多

\(K\) 小会降低 query latency，但 reverse approximation 误差可能变大；\(K\) 大给更多 denoising compute，却延长闭环周期。\(K\) 与 \(T_p/T_a\) 正交；scheduler、prediction type、clip_sample 和 beta schedule 必须一起报。

### 9.4 warm-start 取舍

若实现 warm-start，可把上一轮 trajectory 时间平移后作为下一轮初值，理论上减少随机重采样；但要处理已执行 prefix、时间对齐与新 observation 冲突。本页不把它写成 frozen repo 行为。

## 10. 与 ACT、token、flow 路线的归纳偏置

| 方法 | 训练 target | 一次生成 | stochasticity | closed-loop 接口 |
| --- | --- | --- | --- | --- |
| ACT | continuous chunk masked L1 + CVAE KL | 一次 forward，test \(z=0\) | 默认 deterministic | chunk boundary / temporal ensemble |
| OpenVLA | scalar token CE | autoregressive token | token decoding | 原始单步 action |
| FAST | frequency-space token CE | autoregressive FAST tokens | token decoding | window/replan 由 config |
| Diffusion Policy | epsilon/sample MSE | \(K\) 次 scheduler step | Gaussian init + scheduler | \(T_o,T_p,T_a\) + controller |
| π0 flow | velocity MSE | ODE/flow solver | noise init / solver | openpi H/K contract |

“能表示多模态”不等于部署必须随机；是否固定 generator、如何 smoothing、如何选择 \(T_a\)，仍是 evaluation/controller contract。

## 11. Claim-to-code 总表

| Claim | paper | frozen code | 判定 | 安全口径 |
| --- | --- | --- | --- | --- |
| 默认直接回归 clean action | noise MSE | target 按 prediction type | rejected | 默认 epsilon；sample 可选 |
| 每时刻独立 diffusion | action trajectory | `[B,Tp,Da]` | rejected | 联合 sequence |
| horizon 就是执行步数 | 区分 \(T_p,T_a\) | slice/runner 分开 | rejected | 四条时间轴分开 |
| global cond 拼进 action channel | visual condition | flattened global cond | rejected | trajectory action-only |
| 所有路径都 inpainting | 有 global/non-global | default global | rejected | 先报 cond path |
| policy 已支持 v_prediction | dependency 有 | policy 无 target | rejected | 依赖能力不等于 policy |
| padding 自动不进 loss | 无统一 claim | repeat + no valid_mask | rejected | dataset-specific |
| random noise 只在训练 | inference 也 random | `conditional_sample` | rejected | 两端都有 |
| warm-start 是默认 | paper says can | code rejects past_action | rejected | design option only |
| DDIM 固定 10 steps | paper example | config 8/runtime 16 | rejected | 报版本/config |
| \(T_a=1\) 才闭环 | fixed horizon allowed | batch execute | rejected | consistency/responsiveness trade-off |
| 46.9% 可迁移本地 | specific benchmarks | no local artifact | rejected | 不证明个人指标 |

## 12. 对 `VLA-ACT-018..022` 的支持状态

| ID | 覆盖 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ACT-018 | conditional diffusion、多模态、temporal consistency | source-ready | independent review |
| VLA-ACT-019 | noisy action、target、condition/mask、MSE | source-ready | 手算 scheduler |
| VLA-ACT-020 | schedule、prediction type、\(T_p\)、\(K\) | source-ready with warning | v-pred extension |
| VLA-ACT-021 | \(T_o/T_p/T_a\)、sim/real replan | source-ready | 本地 controller |
| VLA-ACT-022 | DDPM/DDIM、latency、warm-start gap | source-ready with warning | hardware telemetry |

source-ready 不等于 candidate-ready；题卡不在本页生成，练习状态不改变。

## 13. 与个人项目的真实性边界

| 上游事实 | 可用于提醒 | 不可迁移 |
| --- | --- | --- |
| \(T_o,T_p,T_a\) | 拆本地 H/K/replan | 不证明本地数值 |
| normalizer + clipping | stats/scheduler/controller 一致 | 不替代本地 asset |
| global condition | encoder/denoise loop 对照 | 不证明本地 Qwen path |
| random restart | paper/code 差异案例 | 不证明本地行为 |
| public latency | recipe 语境 | 不证明本地 GPU |
| timestamp scheduling | action slice/queue 分开 | 不替代本地 client |

进入 OpenPiVLA 强回答前仍需：policy class、checkpoint、scheduler/prediction type、normalizer、action axes、model horizon、executed prefix、replan trigger、controller frequency、latency、task/trial/seed/protocol 和 success summary。

## 14. 面试安全口径与危险答案

### 14.1 30 秒安全骨架

“Diffusion Policy 把未来 action chunk 当作联合连续变量，用 conditional DDPM 学 noisy action 的噪声残差。训练时随机选 diffusion timestep，把标准化 trajectory 加 Gaussian noise，condition 是最近 \(T_o\) 步 image/state；默认 epsilon prediction 用 noise MSE。推理从 Gaussian trajectory 开始，运行 \(K\) 次 scheduler step 得到 \(T_p\) 步，再只返回/执行 \(T_a\) 步并重观测。horizon、action slice、replan interval 和 diffusion iterations 是不同时间轴；论文提 warm-start，但 frozen repo 每次从 random noise 重启。”

### 14.2 高危说法

- “MSE 直接回归 clean action。”——默认 target 是 epsilon。
- “每步只生成一个 action。”——生成整个 \(T_p\times D_a\) sequence。
- “horizon=16 就执行 16 步。”——config 可能返回 8，real eval 还异步重规划。
- “100 inference steps 是机器人控制步。”——是 denoising iterations。
- “代码 warm-start 上一段 action。”——当前 commit random init。
- “mask 去掉所有 padding。”——sampler 可能重复边界值。
- “DDIM 把训练也改成 8 steps。”——通常只抽稀 inference。
- “46.9% 说明本地一定更好。”——protocol 不可偷换。

## 15. 风险、未决项与下一步

1. **独立审查未完成**：本页由同一 agent 完成 freeze，review 保持 WARN。
2. **版本差异必须保留**：warm-start vs random restart；10/16/8 steps；paper symbols vs real scheduling。
3. **padding 需合成 test**：确认各 dataset repeated targets 是否进 loss。
4. **scheduler 要锁版本**：记录 diffusers、scheduler、prediction type、clip_sample、runtime steps。
5. **尚未进入题卡**：`VLA-ACT-018..022` 先 source-ready。
6. **下一主交付物**：基础 Flow Matching → π0，核对 probability path、velocity target、ODE solver 与 openpi 时间方向。
7. **本地仍待取证**：upstream 只作方法对照，不进入个人指标/贡献。

## 参考文献（References）

1. Chi et al., [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/html/2303.04137v5), arXiv `2303.04137v5`, 2024；[arXiv abs/API](https://arxiv.org/abs/2303.04137v5)。
2. [real-stanford/diffusion_policy](https://github.com/real-stanford/diffusion_policy/tree/5ba07ac6661db573af695b419a7947ecb704690f), frozen commit `5ba07ac6661db573af695b419a7947ecb704690f`, MIT；核心路径为 policy、dataset、sampler、runner 与 `eval_real_robot.py`。
3. [Hugging Face diffusers v0.11.1 schedulers](https://github.com/huggingface/diffusers/tree/v0.11.1/src/diffusers/schedulers)，supporting dependency。
4. [ACT Claim-to-Code](vol_03_act_claim_to_code.html)，本仓库 Source Audit C。
5. [OpenVLA Claim-to-Code](vol_03_openvla_claim_to_code.html)，本仓库 Source Audit A。
6. [π0 / FAST / openpi Claim-to-Code](vol_03_pi0_fast_openpi_claim_to_code.html)，本仓库 Source Audit B。
