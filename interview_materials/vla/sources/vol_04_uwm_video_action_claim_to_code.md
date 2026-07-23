# VOL 04 Source Audit B：UWM Video / Action Diffusion Claim-to-Code

> 审计日期：2026-07-16  
> 状态：drafted / paper_abstract_and_official_site_reviewed / repo_frozen_and_line_audited / independent_review_complete / WARN  
> 覆盖题目：VLA-WM-015..020、VLA-WM-039..044  
> frozen repo：WEIRDLabUW/unified-world-model @ b7d4067c8859775e5b08f681e76d538015cdd445（commit date 2025-10-08）

## 1. 结论先行

1. **UWM 不是在视频模型旁边外挂 action head。**它在一个共享 diffusion transformer 中同时建模 action chunk 和 next-observation latent video；action 与 video 使用独立 diffusion timestep，官方摘要/项目页将其描述为 policy、forward dynamics、inverse dynamics 和 video prediction 的统一框架。[1][2]
2. **训练 schema 有 robot tuple 与 action-free video tuple。**robot 数据提供 \((o,a,o')\)，视频数据只提供 \((o,o')\)。官网方法页把缺失 action 描述为 fully noised，并将 action diffusion timestep 手动设到 \(T\)。[2]
3. **独立 timestep 定义了 inference mode，而不是一句“多任务学习”。**一个分支固定在高噪声、另一分支迭代得到 marginal；给定 clean action 预测未来是 forward dynamics；给定 clean future 反推 action 是 inverse dynamics；两个分支一起迭代是 joint sample。[1][2][3]
4. **frozen default 不是 language-conditioned VLA。**configs/model/uwm.yaml 设置 use_low_dim=False 和 use_language=False；默认 LIBERO 输入是两路 RGB，DROID 是否使用 low-dim 也由模型配置控制。[3]
5. **工程默认合同是 num_frames=19、obs_num_frames=2、action_len=16、100 training steps、10 DDIM inference steps。**这些值只属于 frozen config，不是方法常数。[3]
6. **当前代码里的 action_mask 不是 action loss mask。**它只把 video 样本的 `action_t` 设为最大噪声 timestep；随后 action loss 仍是全量 `F.mse_loss(action_noise_pred, action_noise)`。因此不能说 video 样本 action loss 已排除。[3]
7. **离线 MSE 不能替代闭环 success。**仓库 validation 同时记录 marginal/inverse/joint action MSE 与 marginal/forward/joint image MSE；每项只对应一个 conditional proxy。[3]
8. **README 的 LIBERO 命令与 Google Drive 链接不等于本地 checkpoint 或 strict 结果。**train_robomimic.py 对 libero_90 预训练直接跳过 rollout；checkpoint 没有 hash/revision。[3][4]
9. **frozen tree 没有 LICENSE/COPYING/NOTICE。**代码可见性不等于明确复用许可，需向上游确认。[3]

## 2. 来源与证据边界

| 编号 | 来源 | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [1] | arXiv 2504.02792v3 abstract，提交 2025-04-03、修订 2025-05-23；快照：%TEMP%/vol04-papers/uwm.html | 统一 action/video diffusion、独立 timestep、四种 mode、DROID/LIBERO 方向 | 本轮未稳定获得 full-text equation/PDF/source tar；不写摘要外 exact 数字 |
| [2] | 官方 weirdlabuw.github.io/uwm 项目页；快照：%TEMP%/vol04-papers/uwm_site.html | tuple schema、fully-noised action、独立 timestep、DROID 实验方向 | 官网视频/文字不是本地运行证据 |
| [3] | frozen repo WEIRDLabUW/unified-world-model @ b7d4067c8859775e5b08f681e76d538015cdd445 | 模型、config、dataset、normalizer、train/eval/wrapper 的逐行行为 | commit 是论文 v3 之后的实现；无许可证/ checkpoint revision |
| [4] | frozen repo README | 安装、LIBERO-90 pretrain/finetune、DROID pretrain/cotrain/finetune、checkpoint 链接 | 命令未在本机执行，不证明本地结果 |
| 同源推断 | [1]–[4] 联合分析 | timestep mode table、shape/horizon、metric comparability、mask 风险 | 未运行模型、未下载 checkpoint、未做 rollout |

## 3. 统一 diffusion 合同

令 \(o\) 是当前 observation feature，\(a\in\mathbb R^{H\times D_a}\) 是 action chunk，\(y\) 是 next-observation latent，\(t_a,t_y\) 是两路 timestep。共享预测器可抽象为：

\[
\big(\hat\epsilon_a,\hat\epsilon_y\big)
=F_\theta\left(
\operatorname{concat}(E_a(a_{t_a}),E_y(y_{t_y}),R),
E_o(o),e_t(t_a,t_y)\right).
\]

变量解释：\(E_a\) 是 action MLP，\(E_y\) 是 3D video patchifier，\(R\) 是 register tokens，\(E_o\) 是 observation encoder，\(e_t\) 是两个 sinusoidal timestep embedding；输出分别与 action/video noise 同形状。代码映射是 DualNoisePredictionNet、DualTimestepEncoder、AdaLN attention blocks。[3]

DDPM-style noise prediction 的通用表达为：

\[
x_t=\sqrt{\bar\alpha_t}x_0+
\sqrt{1-\bar\alpha_t}\epsilon,\qquad
\mathcal L_{noise}=\operatorname{MSE}(\hat\epsilon_\theta(x_t,t,c),\epsilon).
\]

其中 \(x_0\) 可以是 action 或 VAE latent video，\(c\) 是 observation 与另一 modality 的 noisy token，\(\bar\alpha_t\) 来自 scheduler。frozen code 用 diffusers DDIMScheduler 的 add_noise/step；公式是通用 diffusion 记号，不是 UWM 的独有新公式。[2][3]

robot tuple 的代码目标可整理为：

\[
\mathcal L=\operatorname{MSE}(\hat\epsilon_a,\epsilon_a)
+\operatorname{MSE}(\hat\epsilon_y,\epsilon_y).
\]

当前 UnifiedWorldModel.forward 对两项各调用一次 F.mse_loss 后相加，没有显式 modality weight、valid-axis mask 或 per-sample denominator。[3]

## 4. 架构、数据与 shape

### 4.1 视觉与可选条件

UWMObservationEncoder 做 image transform、ViT/ResNet feature、可选 low-dim/text 拼接，并用 VAEDownsample 将 future images 转成 latent video。MultiViewVideoPatchifier 用 3D Conv patchify latent video，输出经 linear decoder/unpatchifier 回到 latent shape。[3]

默认模型配置为 ResNet、use_low_dim=False、use_language=False，所以没有证据时不能称其为 language VLA；若本地 config 覆盖了这些字段，需把覆盖文件和 checkpoint 一起记录。

### 4.2 sequence / action contract

process_batch 使用 action_start=obs_horizon-1、action_end=action_start+action_horizon：在默认 num_frames=19、obs_num_frames=2、action_len=16 下，当前 history 是前 2 帧，action 是索引 1–16 的 16 步，future observation 是剩余 2 帧。

LIBERO template action shape [7]（position/quaternion/gripper 注释）；DROID config shape [10]（3 position + 6 rotation + gripper 注释）。因此 action tensor 可能是 [B,16,7] 或 [B,16,10]，不能把 7D 当成 UWM 固定维度。[3]

### 4.3 shared transformer flow

共享数据流是：current RGB history → UWMObservationEncoder → global condition；noisy action → action MLP；noisy next latent video → 3D patchifier；两者与 registers、position embedding 拼接后进入 AdaLN DiT；最后分为 action decoder 和 video unpatchifier。共享 blocks 使 modality 交互，但输出 decoder 分离；没有 value/reward head，不能把它写成 Cosmos/WAM 的 action/world/value 三头。[3]

## 5. action-free video 与 mask 风险

官方语义是把视频样本缺失 action 当作 fully noised。[2] frozen code 路径是：webvideo dataset 返回 zero action 与 action_mask=False；mixture dataset 给 robot/video 样本写 true/false；train.py 把 sample-level mask 传给 model.forward；uwm.py 执行 action_t[~action_mask] = num_train_steps - 1，但未对 action_loss 做 sample mask。

这支持的强 claim 是“action-free video 走最大 action noise timestep”，不支持“video action loss 被完全排除”。最小审计应固定 seed，检查 video 样本 action loss 是否有非零梯度，并比较当前实现与显式 `where(action_mask, ...)` 的 loss、gradient、rollout 消融；该测试尚未运行，review 保持 WARN。

## 6. 独立 timestep 与 inference modes

| mode | action branch | next-observation branch | frozen method |
| --- | --- | --- | --- |
| policy / marginal action | action 从 noise 迭代；future branch 固定高噪声 | nuisance sample，不输出 | sample_marginal_action |
| forward dynamics | action 作为 clean/low-noise condition | future 从 noise 迭代 | sample_forward_dynamics |
| inverse dynamics | action 从 noise 迭代 | next observation 作为 clean/low-noise condition | sample_inverse_dynamics |
| marginal video | action branch 固定高噪声；不输出 action | future 从 noise 迭代 | sample_marginal_next_obs |
| joint | 两个 branch 同时迭代 | 两个 branch 同时更新 | sample_joint |

这张表需要结合 DDIMScheduler.timesteps[0]（通常 descending schedule 的高噪声端）和 [-1]（低噪声端）解释；scheduler 版本、endpoint、clip 和 sample order 必须在本地运行时确认。mode 是 distribution slice，不代表所有 slice 都已校准。[1][2][3]

## 7. normalizer、checkpoint 与训练/评估

| 项目 | DROID config | LIBERO config |
| --- | --- | --- |
| RGB | exterior 2 + wrist 1 | agentview + eye-in-hand 2 |
| low-dim | cartesian 6 + gripper 1；可 normalize | template 默认无 low-dim |
| action | [10] | [7] |
| action normalize | normalize_action=True，min/max 线性到约 \([-1,1]\) | Robomimic template 没有 DROID normalizer 字段 |
| image transform | dataset-specific | flip_rgb=True，wrapper 另做垂直 flip，需实测方向 |

DROID normalizer 使用 scale=(max-min)/2、offset=(max+min)/2；checkpoint 保存 action/lowdim normalizer；finetune 读取后替换 dataset normalizer，并将 image encoder LR 设为 base LR 的 0.05 倍。这些是 repo 行为，不是个人创新。[3]

checkpoint 保存 model、optimizer、scheduler、scaler、normalizers、step；README 只给 Google Drive folder，没有 hash/revision/file manifest。[3][4]

validation 记录 action/dynamics loss、marginal/inverse/joint action MSE、marginal/forward/joint image MSE；train_robomimic.py 的 maybe_collect_rollout 在 libero_90 上直接 return。故这些 proxy 与 LIBERO strict success 不可互换。[3]

## 8. LIBERO wrapper 与 strict-eval 边界

LIBEROEnvWrapper 在 reset 时用同一初始 observation 填满 history buffer，step 接收 action sequence 并在 success/done/truncation 时提前结束，success 调 env.check_success()，并把 agentview_rgb/eye_in_hand_rgb 映射到环境 key 后垂直翻转。reset_to_state 虽存在，当前 rollout 入口使用 env.reset()，不证明 demo-state 初始化。num_rollouts=50 与 rollout_length=1000 只是 template defaults，不是官方 strict protocol。[3]

| 指标 | 证明 | 不能替代 |
| --- | --- | --- |
| marginal/inverse action MSE | 某个 action conditional 的 sample proxy | policy execution |
| forward image MSE | 给定 action 的 future latent proxy | contact/physics/closed loop |
| joint image/action MSE | joint sample 的近似质量 | causal action validity |
| rollout success | 固定 wrapper/task/seed 下结果 | 解释哪一分支有效 |

跨版本比较必须冻结 task set、episode、reset/init、camera、normalizer、horizon、replan、checkpoint SHA、environment 和 success predicate。

## 9. 失败诊断与证据链

| 症状 | 优先检查 | 不应直接结论 |
| --- | --- | --- |
| action MSE 降、0 success | normalization、axis、chunk、camera、reset | world model 没学到 |
| video loss 好、action policy 差 | action-free branch gradient、action coverage、loss balance | 视频预训练必然帮助 |
| forward MSE 好、contact fail | latent metric、friction、control frequency | dynamics 正确 |
| inverse MSE 好、policy fail | 多解、future state、time shift | inverse 等于 policy |
| joint 漂移 | timestep endpoint、scheduler、shared-token shortcut | shared transformer 保证一致 |
| finetune 不复现 | checkpoint/normalizer/config manifest | 论文结果不可复现 |

证据链必须分为 paper → repo → checkpoint → runtime → personal contribution：论文不能证明 repo default，README 不能证明 checkpoint，checkpoint link 不能证明 runtime success，上游 UWM 结构不能写成本人原创。

## 10. 面试答题骨架与当前边界

### 10.1 30 秒回答

“UWM 用共享 diffusion transformer 同时建模 action chunk 与 next-observation latent video，两个 modality 的 timestep 独立，因此可切换 policy、forward、inverse、marginal video 和 joint sampling。robot 数据是 \((o,a,o')\)，action-free video 是 \((o,o')\)，官网语义是把缺失 action 置 fully noised。代码上我会核对 action length、obs history、VAE latent、DDIM steps、normalizer、timestep endpoint 和 rollout wrapper；特别是 frozen action_mask 只改 timestep，当前 action MSE 未显式 mask。离线 MSE 只能证明 conditional proxy，不能替代 strict closed-loop success。”

### 10.2 尚未核实

- 已核实：arXiv v3 metadata、官方 website method、frozen repo commit/date、无 license tree entry、UWM model/config/dataset/normalizer/train/eval/wrapper。
- 尚未核实：full-text equations、Google Drive checkpoint hash/contents、用户本地 UWM run/log/rollout、strict LIBERO protocol、mask ablation、browser visual QA、oral drill。
- 不写入本页：UWM 74.4%、92.8%、WAM 45%/71.19% 等项目数字与任何个人贡献。
- 下一步：已完成 UWM Audit B 独立复核；下一 bounded slice 进入 `VLA-WM-015` knowledge + atomic card，Source Audit C（Cosmos Policy/WAM）继续后置。

## 11. 参考文献（References）

1. Zhu et al., “Unified World Models: Coupling Video and Action Diffusion for Pretraining on Large Robotic Datasets”, arXiv 2504.02792v3, 2025. [arXiv abstract](https://arxiv.org/abs/2504.02792v3)；本地：%TEMP%/vol04-papers/uwm.html。
2. Unified World Models official project page. [Website](https://weirdlabuw.github.io/uwm/)；本地：%TEMP%/vol04-papers/uwm_site.html。
3. WEIRDLabUW/unified-world-model, frozen commit b7d4067c8859775e5b08f681e76d538015cdd445. [GitHub](https://github.com/WEIRDLabUW/unified-world-model/tree/b7d4067c8859775e5b08f681e76d538015cdd445)；重点文件：models/uwm/uwm.py、experiments/uwm/train.py、configs/model/uwm.yaml、environments/robomimic/wrappers.py。
4. UWM repository README at the same frozen commit. [README](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/README.md)。
