# VOL 03 Source Audit D：Diffusion Policy 独立事实复核

> 状态：`independent_fact_review / horizon_loss_padding_queue_checked / WARN`
> 审查日期：2026-07-19
> 范围：Diffusion Policy v5 与 `real-stanford/diffusion_policy` frozen commit 的训练 target、condition mask、normalization/padding、\(T_o/T_p/T_a\)、采样步数、warm-start、sim/real rollout 与 synthetic probes。
> 结论先行：论文与 frozen code 支持“条件 action-sequence diffusion + receding-horizon execution”的主机制，但必须保留四类边界：代码的 loss 通过 `loss_mask` 置零后仍对完整元素取 mean；episode 边界 sampler 重复首/尾 frame/action，而不是 valid-length mask；论文提出 warm-start 设计意图，frozen policy 入口拒绝 `past_action` 且从 Gaussian 重启；DDIM inference steps、返回 action 数和 real queue/requery interval 是不同合同。以下均为 public paper/code facts，不证明本地 OpenPiVLA 的 scheduler、horizon、latency 或 success。

## 1. 直接复核来源与冻结对象

| ID | 来源 | 本次核对 | SHA / Verdict |
| --- | --- | --- | --- |
| P01 | [Diffusion Policy v5 PDF](https://arxiv.org/pdf/2303.04137v5) | Section 2–4、Table 7/8、Appendix B；\(T_o/T_p/T_a\)、warm-start、DDIM 10/16、action horizon trade-off | `B65C474B696A4802D8F1457D86B637CE2C5521412570D3AA928CD54563BABC8F` / `primary-verified` |
| C01 | [`diffusion_unet_hybrid_image_policy.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_hybrid_image_policy.py) | Gaussian init、global/inpainting condition、slice、loss target/mask、`past_action` assert | `D8EAD767ED3B1501C358AA3DD97AB479EBDF77A62EC9AB7081D6A2211C2D2E76` / `official-code` |
| C02 | [`diffusion_transformer_hybrid_image_policy.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_transformer_hybrid_image_policy.py) | Transformer path、`pred_action_steps_only`、同一 loss contract | `E4166882BF0FC2E36E97BEB27CDF701286230ABCECA1EFAEA9AAE9A114A008E7` / `official-code` |
| C03 | [`sampler.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/common/sampler.py) | `pad_before/pad_after` 与 episode 边界填充 | `3DC7AFB686A418ABF4CEEE4648DAFB7E1BE901BB70B1539530F9F9964CAD1688` / `official-code` |
| C04 | [`pusht_image_runner.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/env_runner/pusht_image_runner.py) | sim `policy.predict_action` → `env.step(action)`、每次执行 batch 后重新观测 | `84FAA24E803635FE1F07B1907EF04FCB74D07C6ECFCE5F2FF598601019232F03` / `official-code` |
| C05 | [`multistep_wrapper.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/gym_util/multistep_wrapper.py) | `n_action_steps` 的 wrapper action batch 与 observation deque | `2923E73C13FF9F782451AB61BED43A802670BBF29419471F82878C690F26A342` / `official-code` |
| C06 | [`eval_real_robot.py`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/eval_real_robot.py) | `num_inference_steps=16`、timestamped action queue、over-budget fallback、clip | `CD7C0F1F46DCE8606EBB9B2B2618811870C4D41205CE4AD6369AC5D7AC0A1B7C` / `official-code` |
| C07 | [`conda_environment.yaml`](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/conda_environment.yaml) | frozen dependency declaration | `C945BCAC09284CF897D3E1837139EA83F991E4B2298DBD3A8C4A0718A34994EA` / `official-code` |
| D01 | [DDPM scheduler v0.11.1](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddpm.py) | `prediction_type` branches and scheduler step API | `238D19CBE8F105106121F67ABFCA507BB208A72B14C6595DABA4829BB2001CA5` / `dependency` |
| D02 | [DDIM scheduler v0.11.1](https://github.com/huggingface/diffusers/blob/v0.11.1/src/diffusers/schedulers/scheduling_ddim.py) | inference timestep decimation/step semantics | `073AF47F32CA3DA9F5BB9285A774643C66978DE7987805A69283B5F65F163F79` / `dependency` |
| O01 | 本次 synthetic probes | action slice、mask dilution、boundary repeat、unsupported v-pred | `local-evidence / PASS` |

冻结 repo commit：`5ba07ac6661db573af695b419a7947ecb704690f`，MIT；依赖声明包含 `diffusers=0.11.1`。本页不把其它 fork、用户本地 checkpoint 或论文结果升级为个人项目事实。

## 2. Action-sequence diffusion 与三条 horizon

论文定义最近 \(T_o\) 步 observation，预测 \(T_p\) 步 action，仅执行 \(T_a\) 步后重新观察：

\[
O_t=(o_{t-T_o+1},\ldots,o_t),\qquad
A_t=(a_t,\ldots,a_{t+T_p-1}),
\]

变量与直觉：\(T_o\) 是 observation history 长度，\(T_p\) 是一次 diffusion trajectory 的时间长度，\(T_a\) 是送入执行器的 action prefix。它们不是 diffusion solver 的步数，也不能自动推出 real requery interval \(R\)。代码将它们映射到 `n_obs_steps`、`horizon` 与 `n_action_steps`；UNet 与 Transformer hybrid 都保留这个输出合同。

在标准 hybrid image path，输入 observation 经 encoder 压成 `global_cond`，trajectory 只有 action channels：

```python
# Encode the latest To frames and flatten them as global condition.
features = obs_encoder(obs[:, :To].reshape(B * To, ...))
global_cond = features.reshape(B, -1)

# Diffuse a B x Tp x Da action trajectory, then return an execution prefix.
cond_data = torch.zeros(B, Tp, Da)
cond_mask = torch.zeros_like(cond_data, dtype=torch.bool)
sample = conditional_sample(cond_data, cond_mask, global_cond=global_cond)
action_pred = action_normalizer.unnormalize(sample[..., :Da])
action = action_pred[:, To - 1: To - 1 + Ta]
```

代码证据是 `diffusion_unet_hybrid_image_policy.py` 的 `start = To - 1` 与 `end = start + n_action_steps`。若走 `obs_as_global_cond=False`，observation feature 会拼到 trajectory 作为 inpainting condition；这不是“所有 Diffusion Policy 都只有 global condition”的通用定义。

## 3. 训练 target、condition mask 与 denominator

标准化 clean trajectory \(X_0\) 在随机 timestep \(k\) 加噪：

\[
X_k=\sqrt{\bar\alpha_k}X_0+\sqrt{1-\bar\alpha_k}\,\epsilon,
\qquad \epsilon\sim\mathcal N(0,I).
\]

变量与直觉：\(X_k\) 是网络输入，\(\epsilon\) 或 clean \(X_0\) 是由 scheduler `prediction_type` 选择的 target。frozen policy 只接受 `epsilon` 与 `sample`；遇到其它字符串（例如 `v_prediction`）直接 `ValueError`。依赖 scheduler 的能力不能替代 policy 的 `compute_loss` 分支。

代码先构造 `condition_mask`，将被条件化的位置重新写回 `cond_data`，然后：

\[
\mathcal L_{\mathrm{code}}
=\operatorname{mean}_{b,\tau,d}
\left[(1-m_{b,\tau,d})
\left(\hat y_{b,\tau,d}-y_{b,\tau,d}\right)^2\right].
\]

变量与实现：`F.mse_loss(..., reduction='none')` 后乘 `loss_mask = ~condition_mask`，再先对每个 batch 展平取 mean、最后 batch mean。被条件化元素的 numerator 为零，但 denominator 仍包含完整 tensor；因此这是 masked numerator + full-element denominator，不是 valid-count normalization。当前 commit 还明确 `assert 'valid_mask' not in batch`，不能把它说成支持 episode valid mask。

## 4. Boundary padding：重复边界值而非 valid-length mask

`SequenceSampler.sample_sequence` 在 sample 越过 episode 边界时分配完整 `sequence_length`，将左侧位置填成 `sample[0]`，右侧位置填成 `sample[-1]`，再把真实片段写回中间。以 episode 长度 2、`sequence_length=4`、右侧越界 2 为例，action 序列是：

```text
真实:      [a0, a1]
采样结果:  [a0, a1, a1, a1]
valid mask: 没有随 sampler 一起返回
```

因此“边界位置已 padding，所以 loss 自动忽略”是错误答案；这个实现选择的是 boundary-repeat 数据合同。是否把重复值视作真实监督，必须结合训练 pipeline 另外证明，不能仅凭 `pad_after` 推断 valid-only loss。

## 5. Sampling、solver steps 与 action execution

推理 `conditional_sample` 每次先用与 \(T_p\times D_a\) 同形状的 Gaussian 初始化，再调用 `scheduler.set_timesteps(num_inference_steps)`，对每个 scheduler timestep 运行一次网络和 `scheduler.step`。因此：

| 量 | frozen field | 语义 |
| --- | --- | --- |
| \(T_o\) | `n_obs_steps` | 输入 observation 数 |
| \(T_p\) | `horizon` | 生成 trajectory 长度 |
| \(T_a\) | `n_action_steps` | 返回 action prefix 长度 |
| \(K_d\) | `num_inference_steps` | 一次 query 的 denoising/network forwards |
| \(R\) | runner/real timestamp loop | 多久重新获取 observation 并 query |

论文正文给出 DDIM 100 training iterations / 10 inference iterations 的 0.1s 例子；Table 7/8 的 real rows 使用 16 eval iterations；frozen `eval_real_robot.py` 在 diffusion 分支把 `policy.num_inference_steps = 16`。这些对象属于不同版本/配置，不能压成“Diffusion Policy 默认 10 步”或“16 步机器人控制”。

## 6. Warm-start：paper design ≠ frozen implementation

论文在 closed-loop action-sequence prediction 段落提出，receding horizon 可以用上一段 action sequence prediction warm-start 下一轮 inference。frozen UNet/Transformer hybrid 的 `conditional_sample` 始终 `torch.randn(...)`，`predict_action` 入口还执行 `assert 'past_action' not in obs_dict`。因此安全口径是：

1. warm-start 是论文提出的可选设计意图；
2. 该 frozen commit 的默认 inference 从 fresh Gaussian 开始；
3. 若本地实现 warm-start，仍需处理已执行 prefix、时间平移、noise level、新 observation 冲突与可复现性。

不要把“论文提到 warm-start”升级成“官方 frozen repo 默认启用 warm-start”。

## 7. Simulation 与 real execution 的边界

PushT runner 调用 `policy.predict_action`，把返回的 action batch 传给 `MultiStepWrapper.step`；wrapper 逐步执行 batch 并收集新 observation。这个路径把 \(T_a\) 作为一次环境 wrapper 的执行窗口。

real script 则把 policy 输出转成 timestamped target poses：用 observation timestamp 与控制周期 \(\Delta t\) 构造未来时间戳，删除已经过期的 action；若 inference 超过时间预算，只保留最后一个 target 并安排到下一个可用时刻。`steps_per_inference` 参与 cycle timing，不能仅凭提交的 action 数量断言“恰好执行 \(T_a\) 步后才 replan”。真实的 executed prefix 取决于 timestamp filtering、latency 与 queue。

## 8. Synthetic probes

| Probe | 结果 | 结论 |
| --- | --- | --- |
| \(T_o=2,T_p=16,T_a=8\) | `start=1,end=9`，返回 indices `[1..8]` | observation 对齐与 action prefix 分离 |
| loss mask：总元素 8、仅 1 个元素误差 1 | full mean `1/8=0.125`；valid-only mean `1` | mask 不等于 valid-count denominator |
| episode `[a0,a1]`，右 padding 2 | `[a0,a1,a1,a1]` | sampler 重复边界值，不生成 valid mask |
| `prediction_type='v_prediction'` | policy branch raises `ValueError` | frozen policy 未实现 v-target |
| \(T_p=16,T_a=8,K_d=16\) | 每次 query 最多 16 次 scheduler/model step，返回 8 行 action | solver steps 与 execution rows 分离 |
| real action timestamps 中一半已过期 | 只保留未来 entries；全过期时保留最后一行 | queue/replan 受 latency 与 wall-clock 影响 |

这些 probes 验证的是 shape、reduction、padding 与 branch semantics，不证明任何 learned checkpoint success、真实 latency 或个人项目 bug。

## 9. 对 `VLA-ACT-018..022` 与 `VLA-ACT-017` 的回写结论

| Question ID | 独立复核结论 | 必须保留的边界 |
| --- | --- | --- |
| `VLA-ACT-017` | ACT/token/Diffusion/Flow 的 target 与 sampler 对照可用 | 跨协议 success 不可直接排名 |
| `VLA-ACT-018` | sequence-level conditional diffusion 与多模态直觉通过 | 不推断本地 diversity/success |
| `VLA-ACT-019` | epsilon/sample target、condition mask、full-mean reduction 通过 | 本地 valid mask 待取证 |
| `VLA-ACT-020` | schedule、prediction type、\(T_p\)、\(K_d\) 分离通过 | frozen policy 不支持 v-pred |
| `VLA-ACT-021` | \(T_o/T_p/T_a\)、sim wrapper 与 real timestamp queue 通过 | 本地 H/K/R 未证 |
| `VLA-ACT-022` | DDPM/DDIM、10/16 step 版本差异与 warm-start gap 通过 | 不把论文 latency 迁移到本地硬件 |

## 10. 项目真实性边界与面试安全口径

上游 Diffusion Policy 可以作为 action diffusion、horizon 拆分与 0-success interface debugging 的对照；它不能证明 OpenPiVLA 使用同一 scheduler、`prediction_type`、\(T_o/T_p/T_a\)、warm-start、action axis、normalizer 或 real queue。要把这些写入个人项目回答，仍需本地 config、checkpoint、transform、controller trace、timestamped rollout 和 eval summary。

### 30 秒安全回答

“Diffusion Policy 把未来 \(T_p\) 步连续动作作为一个 trajectory，用 observation 条件化的 diffusion process 学 noisy action 的噪声或 clean sample。推理从同形状 Gaussian trajectory 开始，运行 \(K_d\) 次 scheduler step，再从 \(T_o-1\) 起切出 \(T_a\) 步执行；\((T_o,T_p,T_a,K_d,R)\) 是不同时间轴。论文提出可用上一段预测 warm-start，但这个 frozen commit 的 policy 每次从 Gaussian 重启，并且 real script 还要经过 timestamp queue，所以我不会把 action batch 长度直接等同于 replan interval。”

## 11. 风险、未决项与下一步

1. **核心 public facts 已独立复核**：training target/mask、boundary repeat、horizon/slice、solver steps、warm-start gap 与 sim/real queue 已核对。
2. **视觉 QA**：当前环境的 `file://` 浏览器导航受策略限制，静态检查可以通过但不宣称浏览器视觉验收。
3. **本地 runtime**：OpenPiVLA scheduler、checkpoint、normalizer、action schema、H/K/R、controller 与 success protocol 仍待 artifact。
4. **下一 bounded slice**：进行一题真实 ACT/Diffusion 口述，或补一个本地 OpenPiVLA runtime artifact；不批量新增 VOL 03 题卡。

## 参考文献（References）

1. Chi et al., [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/html/2303.04137v5)，arXiv `2303.04137v5`。
2. [real-stanford/diffusion_policy](https://github.com/real-stanford/diffusion_policy/tree/5ba07ac6661db573af695b419a7947ecb704690f)，frozen commit `5ba07ac6661db573af695b419a7947ecb704690f`，MIT。
3. [Hugging Face diffusers v0.11.1](https://github.com/huggingface/diffusers/tree/v0.11.1)，DDPM/DDIM scheduler source。
4. [VOL 03 Diffusion Policy Claim-to-Code](vol_03_diffusion_policy_claim_to_code.html)，本仓库先前 source freeze；本页为独立复核，不替代本地项目证据。
