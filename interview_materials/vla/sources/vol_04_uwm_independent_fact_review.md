# VOL 04 Audit B：UWM 独立事实复核

> 状态：`independent_review / UWM / WARN`  
> 复核日期：2026-07-17  
> 冻结 revision：`WEIRDLabUW/unified-world-model@b7d4067c8859775e5b08f681e76d538015cdd445`  
> 目的：独立重新获取官方 raw 文件与项目页，复核 Audit B 对 `VLA-WM-015..020` 的关键实现断言；不复核用户项目数字，不下载 checkpoint，不生成题卡。

## 复核问题与结论

本轮只问：UWM 是否真的在共享网络中同时处理 action/video，是否使用独立 timestep，action-free video 的 mask 到底改变了什么，以及默认 shape、训练/评估和 checkpoint 边界是否被 source audit 正确描述？

结论：核心架构断言可以由官方项目页与冻结 commit 的 raw 文件独立支持；`action_mask` 的边界也被代码直接证实，但它不是 action loss mask。checkpoint、runtime、完整论文公式、许可证与本地项目结果仍未闭合，因此 verdict 保持 `WARN`。本复核足以解锁下一 bounded slice：单独生成 `VLA-WM-015` 知识与题卡；不能把 UWM 方法审计升级为个人项目结果。

## 来源与可重复指纹

访问方式是只读 HTTP GET；raw 文件按返回字节计算 SHA-256。网页内容是访问时快照，不等同 Git commit 文件。

| Source | 类型 | 访问/冻结 | SHA-256 | 直接支持 |
| --- | --- | --- | --- | --- |
| `configs/model/uwm.yaml` | official-code | frozen commit | `9C2EB19F65ED823C06F3D9C6A1520FF62393BA6DC4B1820E50AEA0F4BA62D152` | `action_len=16`、`use_low_dim=False`、`use_language=False`、train/inference steps |
| `models/uwm/uwm.py` | official-code | frozen commit | `ADD93268D82B784CC733C84F8A09E98115C0ACC370FC9894BC9373976EF39E26` | Dual timestep、共享 token sequence、action mask timestep、loss、sampling modes |
| `experiments/uwm/train.py` | official-code | frozen commit | `7971ECEAB5495C4BD534F48AF5BE075751465CCB3E0E0F6549CAA9C5483E8707` | validation metric ladder、`action_mask` 传递、pretrain load |
| `experiments/uwm/train_robomimic.py` | official-code | frozen commit | `71F8CBD2FAC379A69221B4224699E3777443F042D37279BC5BA5666284D07678` | rollout hook、pretraining skip、checkpoint load |
| `environments/robomimic/wrappers.py` | official-code | frozen commit | `981088E44B22E1B7E68EB2679DFBE931D6839E33B43F2B45DA24913A9D2374AD` | LIBERO wrapper、`reset_to_state`、`check_success` |
| `README.md` | official-code | frozen commit | `84FDD2F1E3E3E90E33B65148F196EBE9DD7024514D0F911BD7D173F5D9406B16` | LIBERO-90 pretrain/finetune 命令、Google Drive checkpoint 链接 |
| UWM official project page | primary web | fetched 2026-07-17 | `6C6155C17F807F55CCA22D40AF877CFFBB166D0116A3F3C04D72C2577EE623C6` | action/video coupling、independent timestep、action-free video、four inference modes |
| arXiv abstract page `2504.02792v3` | primary web | fetched 2026-07-17 | `1B71E15DE9AE075D10810403ACB1D69C1D9B8C3A72FA288531932CDD841BA5CD` | 论文版本与摘要级方法定位；本轮未使用 full-text equation |

许可证探测：冻结 commit 的 `LICENSE`、`COPYING`、`NOTICE` raw 路径均返回 404；不能假定该树有可复用许可证。

## Claim-by-claim 复核

| Claim | 复核证据 | 结果 | 边界 |
| --- | --- | --- | --- |
| 共享 diffusion transformer 同时处理 action 与 next-observation video | `DualNoisePredictionNet` 定义 action encoder、3D video patchifier、registers、共享 AdaLN blocks；输出再切成 action/video 两段 | `PASS` | 这是上游实现事实，不是个人创新 |
| 两路 timestep 独立进入条件 | `DualTimestepEncoder.forward(t1,t2)` 分别做 sinusoidal embedding 后拼接；`UnifiedWorldModel.forward` 独立采样 action/next_obs timestep | `PASS` | 只能说明代码合同，未做 runtime numerical smoke |
| action-free video 把 action 置为 fully noised | official page 明确 missing actions as noise；代码 `action_t[~action_mask] = num_train_steps - 1` | `PASS WITH WARNING` | 代码还用 zero action 作为输入张量；“fully noised”指 timestep，不等于移除 action loss |
| `action_mask` 会屏蔽 action loss | 代码随后直接执行 `F.mse_loss(action_noise_pred, action_noise)`，没有 sample mask 或 valid-axis denominator | `FAIL CLOSED / claim rejected` | source audit 的“不是 action loss mask”断言被独立确认 |
| inference modes 由 modality timestep slice 控制 | `sample_forward_dynamics` 固定 `action_t=timesteps[-1]`；`sample_inverse_dynamics` 固定 `next_obs_t=timesteps[-1]`；marginal/joint 方法分别迭代对应分支 | `PASS` | scheduler endpoint 的数值含义仍依赖 pinned diffusers runtime |
| frozen defaults 是 action_len 16、train steps 100、inference steps 10 | `configs/model/uwm.yaml` 与 `uwm.py` defaults 同时出现 | `PASS` | 不是方法常数；dataset config 可覆盖 |
| 默认配置不是 language-conditioned VLA | config 明确 `use_low_dim=False`、`use_language=False` | `PASS WITH WARNING` | 其他实验 config 若 override，必须单独记录；不能泛化所有 UWM run |
| validation metrics 只形成 proxy ladder | `train.py` 记录 action MSE（marginal/inverse/joint）与 image MSE（marginal/forward/joint），并对每项单独 `F.mse_loss` | `PASS` | 不等于 closed-loop success 或 causal validity |
| pretraining checkpoint 可由 README 复现 | README 给出命令与 Google Drive folder；train code load `ckpt["model"]` 及 normalizers | `PASS WITH WARNING` | 没有 checkpoint hash/revision，命令未在本机执行 |
| LIBERO wrapper 证明 strict fixed-init benchmark | wrapper 有 `reset_to_state` 与 `check_success`，训练脚本有 rollout hook | `FAIL CLOSED / claim rejected` | wrapper/API 不等于某次 strict init、seed、horizon 或本地成功率 |

## 关键实现核对

### 1. Sequence 与 shape

冻结 config 给出 `action_len=16`，`action_dim` 来自 dataset shape metadata；模型的 positional sequence 是 action tokens + video tokens + registers。因而 `[B,16,D_a]` 是该 config 的 action contract，而不是 UWM 的普适 action dimension。DROID/LIBERO 的 `D_a` 必须回到各自 dataset config，不能从 `action_len` 推出。

### 2. 训练 loss 与 mask

`forward` 为 action 和 next observation 各采样一个 timestep、各自加噪并预测 noise；最后是两个全张量 MSE 的和。对 action-free video，`action_mask` 只改变 action branch 的 timestep。要声称“视频样本不产生 action gradient”，必须补一个 gradient test 或显式 masked-loss A/B；当前没有这项 runtime artifact。

### 3. Sampling mode

官方项目页将 UWM 描述为 policy、forward dynamics、inverse dynamics 和 video prediction 的统一框架；raw code 进一步显示这些 mode 通过固定另一分支的 timestep、只迭代目标分支实现。这个结论是“方法/代码映射”，不是说每种 mode 都在用户本地 checkpoint 上校准过。

### 4. 训练、评估与 checkpoint

`train.py` 的 validation 会对 action/image proxy 做分项 MSE；`train_robomimic.py` 的 rollout 逻辑在 pretraining 阶段跳过，finetune 才可能调用环境。checkpoint 保存 model、optimizer、scheduler、scaler、normalizer 和 step，但 README 只提供 Google Drive folder。故 paper → repo 已核对，repo → checkpoint/runtime 仍为 open。

## 独立复核中未完成的项目

| 未完成项 | 原因 | 处理 |
| --- | --- | --- |
| full-paper equations | 本轮只取 arXiv abstract 页面 | 公式只保留 code/project-page 可支持的抽象，不写摘要外数字 |
| diffusers endpoint numerical smoke | 当前环境未固定官方训练 runtime/checkpoint | 题卡中把 `timesteps[0]/[-1]` 写成需核验的 implementation detail |
| action-free gradient ablation | 没有 upstream dataset/checkpoint/runtime | 保持“timestep mask ≠ loss mask”边界 |
| checkpoint hash/contents | README 只有 Google Drive folder | 不把公开链接当本地 artifact |
| strict LIBERO result | wrapper 与 benchmark protocol 不是同一证据 | UWM 74.4/92.8 仍留在 VOL 07 evidence |
| license | frozen tree 未找到 LICENSE/COPYING/NOTICE | 复用前向上游确认 |
| browser visual QA | 当前 app 的 `file://` 策略限制 | review 标记 BLOCKED/PENDING，不用静态检查冒充 |

## 允许进入下一节点的口径

`VLA-WM-015` 可以以如下范围进入知识页：

> UWM 的 frozen implementation 在共享 diffusion transformer 中拼接 action 与 next-observation video token，使用独立 timestep，并通过固定一侧 timestep 实现 policy/forward/inverse/video/joint sampling；action-free video 的代码行为是把 action timestep 设到最大训练步，但当前 action MSE 没有显式 sample mask。所有 checkpoint、runtime、许可证和用户项目结果另行标注。

不允许升级为：

- “UWM 已证明本地 74.4% checkpoint”；
- “视频样本完全不产生 action loss”；
- “README 的 checkpoint 链接就是可复算权重”；
- “wrapper API 等价于官方 strict benchmark”；
- “共享 architecture 属于个人原创”。

## 参考资料

1. [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html)：原始 claim-to-code 审计与未决项。
2. [UWM 官方项目页](https://weirdlabuw.github.io/uwm/)：方法与 action-free video 语义。
3. [UWM frozen repository](https://github.com/WEIRDLabUW/unified-world-model/tree/b7d4067c8859775e5b08f681e76d538015cdd445)：本轮 raw 文件来源。
4. [arXiv 2504.02792v3](https://arxiv.org/abs/2504.02792v3)：论文版本与摘要定位。
5. [VOL 04 knowledge map](../knowledge/vol_04_world_model_sim2real.html)：当前 18/44 knowledge 边界与后续节点。
