# VOL 04 World Model / Sim2Real：UWM 的 Video–Action 统一扩散（WM-015）

> 状态：`drafted / knowledge_17_of_44 / card_1_of_1_unseen / WARN`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-WM-015`；来源已完成 Audit B canonical audit 与独立事实复核，单张题卡同步生成并保持 `unseen`。  
> 前置：[VOL 04 World Model Foundations](vol_04_world_model_sim2real.html)、[UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)、[UWM 独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)。

## 问题（Question）

UWM 如何把 video diffusion 与 action diffusion 放进统一预训练框架？面试回答不能停留在“多任务学习”：需要说明 robot tuple 与 action-free video tuple、两路 timestep、共享 token/transformer、输出 head、inference mode，以及 `action_mask` 为什么不等于 action loss mask。

## 知识地图位置与证据边界

```text
# 节点依赖图：本页只展开 WM-015，后续节点保持 source-first。
WM-001..010 world-model contract / RSSM / rollout
                         ↓
WM-015 UWM video–action coupling
                         ↓
WM-016 joint objective / mask audit
                         ↓
WM-017..020 heterogeneous data / horizon / metric / bad case
```

本节点只支持冻结 UWM commit 的方法与代码合同：`WEIRDLabUW/unified-world-model@b7d4067c8859775e5b08f681e76d538015cdd445`。它不支持用户本地 UWM 74.4%/92.8% 的 checkpoint provenance、严格 benchmark 复现或个人原创声明；这些仍属于 VOL 07 evidence 层。

## 1. 先讲直觉：一个 backbone，两个可控生成分支

普通 imitation policy 只从 observation 预测 action；视频预训练则从当前观测预测未来视觉。UWM 的关键是把 action chunk 和 next-observation latent video 都变成 noisy tokens，送入同一个 diffusion transformer，再用两个 timestep 告诉模型“当前要去噪哪一支、另一支应被视作条件还是 nuisance”。因此，同一个网络可以切换 policy、forward dynamics、inverse dynamics、marginal video 和 joint sampling。

这不是“视频模型旁边外挂 action head”：代码中的 action encoder、3D video patchifier、register tokens 与 AdaLN blocks 共享序列，只有 action decoder 和 video unpatchifier 在输出端分开。共享表示能让视频数据参与表征学习，但也会引入 modality shortcut、loss 竞争和 action-free 样本梯度风险。

## 2. 两种数据合同：

### 2.1 Robot tuple

机器人轨迹提供当前 observation、action chunk 与下一段 observation：

\[
\mathcal D_{robot}=\{(o_{t:t+T_o-1},\ a_{t:t+H-1},\ o_{t+T_o:t+T_o+T_y-1})\}.
\]

其中 (T_o) 是历史观测帧数，(H) 是 action horizon，(T_y) 是未来观测帧数。冻结 UWM config 的 `action_len=16`，但 action dimension (D_a) 由 dataset shape metadata 决定；不能把 16 或 7 维泛化为所有 embodiment 的常数。

### 2.2 Action-free video tuple

无动作视频只提供 ((o,o'))。官方项目页把缺失动作描述为 fully noised；冻结代码的具体行为是：保留 action tensor 形状，将 `action_t` 设为 `num_train_steps - 1`。这意味着视频样本的 action 分支主要承担“高噪声条件”的角色，而不是自动从 loss 中删除 action 项。

## 3. 共享网络与双 timestep

令 (a_{t_a}) 是加噪 action，(y_{t_y}) 是加噪的未来视觉 latent，(c(o)) 是当前观测条件，(t_a,t_y) 是两路 timestep。共享预测器可以抽象为：

\[
(\hat\epsilon_a,\hat\epsilon_y)=F_\theta\big(E_a(a_{t_a}),E_y(y_{t_y}),c(o),e(t_a,t_y),R\big).
\]

这里 (E_a) 是 action MLP，(E_y) 是多视角 3D patchifier，(R) 是 register tokens，(e(t_a,t_y)) 是两个 sinusoidal embedding 的拼接；输出分别与 action/video noise 同形状。独立 timestep 不是装饰字段，而是控制 inference condition 的接口。

训练时两路 noise prediction 可写成：

\[
\mathcal L_{UWM}=\operatorname{MSE}(\hat\epsilon_a,\epsilon_a)+\operatorname{MSE}(\hat\epsilon_y,\epsilon_y).
\]

当前 frozen code 对两项分别调用全张量 `F.mse_loss` 后相加，没有显式 modality weight、sample denominator 或 valid-axis mask。因此面试中要区分“共享目标的代码形状”和“未来可能设计的 masked/weighted objective”；后者不能冒充当前实现。

## 4. Inference mode：固定一侧、迭代另一侧

| Mode | action branch | next-observation branch | 代码映射 | 能说明什么 |
| --- | --- | --- | --- | --- |
| policy / marginal action | 从 noise 迭代 | 固定在高噪声端作为 nuisance | `sample_marginal_action` | 从 observation 采样 action |
| forward dynamics | clean/低噪声 action 条件 | 从 noise 迭代 | `sample_forward_dynamics` | 给定 action 预测未来视觉 latent |
| inverse dynamics | 从 noise 迭代 | clean/低噪声 future 条件 | `sample_inverse_dynamics` | 从当前/未来观测反推 action |
| marginal video | 固定高噪声 action | 从 noise 迭代 | `sample_marginal_next_obs` | 不输出可执行 action 的未来预测 |
| joint | 两支都迭代 | 两支都迭代 | `sample_joint` | 联合采样 action 与未来 latent |

独立复核直接观察到 forward/inverse 方法把另一分支设为 `timesteps[-1]`，marginal 方法把 nuisance 分支设为 `timesteps[0]`。`[0]/[-1]` 的数值噪声语义仍依赖 pinned diffusers scheduler 的 runtime smoke，因此回答应说“代码使用 endpoint slice，数值方向需与 scheduler 版本一起核验”。

## 5. 为什么这不是普通 multi-task head

### 5.1 信息流变化

action 与 video tokens 在共享 blocks 中互相注意；因此 action 分支可以利用未来视觉条件，video 分支也能利用 noisy action。切换 timestep 就能改变条件分布，而不是仅在最后一层选择不同 head。

### 5.2 代价与风险

- action-free video 如果 action loss 未 mask，zero-action/noisy-action 的训练梯度可能污染 policy branch；
- 视频细节 loss 下降不等于 action conditional 更可控；
- 长 horizon 的 latent video 预测可能有视觉合理但动力学不可执行的 shortcut；
- 不同机器人 action dimension、camera view、normalizer 和 horizon 若未经 schema 对齐，会把共享 backbone 变成错误的混合分布。

## 6. 实现映射与审计表

| 机制 | Frozen source | 直接事实 | 不支持的升级 |
| --- | --- | --- | --- |
| action/video token coupling | `models/uwm/uwm.py` | action encoder + video patchifier + shared AdaLN blocks | “上游结构是个人原创” |
| independent timestep | `DualTimestepEncoder`、`UnifiedWorldModel.forward` | action/next_obs 各采样 timestep 并拼接 embedding | “两个任务完全独立训练” |
| action-free semantics | `action_t[~action_mask] = num_train_steps-1`、官方项目页 | 缺失 action 进入最大 timestep | “video sample action loss 已排除” |
| objective | `F.mse_loss` 两次相加 | action/video noise prediction 的无权和 | “存在已验证的 modality weighting/ablation” |
| metric ladder | `experiments/uwm/train.py` | action/image 的 marginal/forward/inverse/joint proxy | “MSE 等于 LIBERO success” |
| checkpoint | `train.py`、README | save/load model、optimizer、scheduler、scaler、normalizer、step；README 提供 Drive folder | “公开链接就是 immutable 可复算 checkpoint” |

## 7. 最小训练/采样伪代码

```python
def uwm_step(batch, model, scheduler):
    # 1. Read current observation, future observation and action chunk.
    obs, next_obs, action = build_uwm_tuple(batch)

    # 2. Sample independent diffusion times for action and future video.
    action_t = random_timestep(batch_size=action.shape[0])
    video_t = random_timestep(batch_size=next_obs.shape[0])

    # 3. For action-free video, only change the action timestep; do not assume loss masking.
    action_t = apply_action_free_timestep(action_t, batch.get("action_mask"))
    noisy_action, eps_a = scheduler.add_noise(action, action_t)
    noisy_video, eps_y = scheduler.add_noise(encode_video(next_obs), video_t)

    # 4. Shared transformer predicts both noise tensors.
    pred_a, pred_y = model(obs, noisy_action, action_t, noisy_video, video_t)

    # 5. Frozen implementation uses full-tensor MSE; any masked objective is a new design.
    loss = mse(pred_a, eps_a) + mse(pred_y, eps_y)
    return loss
```

伪代码只表达 frozen implementation 的数据流；`apply_action_free_timestep` 不等于 `where(action_mask, ...)` 的 loss mask，必须通过代码和 gradient test 分别验证。

## 8. 与项目面试的安全挂钩

### UWM / LIBERO

可以把 UWM 项目挂钩到“我如何核对 action length、observation history、normalizer、checkpoint 和 rollout protocol”，也可以讨论 DataLoader stall、fixed-pruned-init 与 reset-style 的评估边界。不能把 UWM 上游 shared diffusion architecture 说成本人设计，不能把 74.4%/92.8% 直接写成该方法的通用结果，也不能在没有 checkpoint bundle 时声称复现了官方 Table II。

### WAM / Cosmos

本节点只用于对照：UWM 的 frozen code 没有 Cosmos/WAM 的 action/future/value 三头。若面试官追问 WAM，必须切回 Cosmos source audit，不把两个项目的 world/action 术语拼成同一实现。

## 9. Bad Case、追问与回答边界

### Bad Case

1. 视频样本的 action tensor 虽为零，但 action loss 仍全量计算。
2. 把 `timesteps[0]`/`[-1]` 的代码 endpoint 当成无需 scheduler 版本验证的物理噪声结论。
3. action MSE 降低，却没有 forward intervention 或 closed-loop success。
4. 不同 embodiment 的 action dimension、camera key 或 normalizer 混用。
5. 把 action-free video 的视觉收益直接归因为 policy uplift。

### 追问

- 为什么 action-free video 不能直接 `action_loss=0`？
- 两路 timestep 怎样把 policy、forward、inverse mode 统一起来？
- 如果 image MSE 变好而 action success 不变，你先查什么？
- 为什么 action length 16 不是 UWM 的方法常数？
- 如何做 action-free sample 的 gradient ablation？
- UWM 和 Cosmos/WAM 的输出 head、loss mask 有何关键不同？

### 危险回答

“UWM 就是视频模型加 action head”“视频没有 action 所以 action loss 自动为零”“两路 timestep 只是两个任务标签”“MSE 下降就代表机器人成功率提升”“action_len=16 是论文固定设置”。

## 10. 结论与后续

UWM 的可复述机制是：robot/video 两种 tuple 共用一个 diffusion transformer；action 与 future video 各自加噪、各自 timestep，却在共享 token blocks 中交互；固定一侧 timestep 可以得到 policy、forward、inverse、marginal video 与 joint sampling。当前实现最重要的审计点是：action-free 的最大 timestep 已确认，但 action loss 没有显式 sample mask；离线 proxy、checkpoint 链和用户项目结果必须保持独立证据层。

下一节点：`VLA-WM-016` joint objective / mask audit；本页题卡保持 `unseen`，不创建 coaching state。

## 参考文献（References）

1. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)：paper abstract、official project page、frozen code 的 claim-to-code 审计。
2. [UWM 独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)：frozen raw file SHA、实现断言与 fail-closed 边界。
3. [UWM official project page](https://weirdlabuw.github.io/uwm/)：共享 video/action diffusion、action-free video 与 inference modes 的官方方法说明。
4. [UWM frozen repository](https://github.com/WEIRDLabUW/unified-world-model/tree/b7d4067c8859775e5b08f681e76d538015cdd445)：`models/uwm/uwm.py`、`configs/model/uwm.yaml`、`experiments/uwm/train.py`、README。
5. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：项目 checkpoint、strict/reset 与个人 evidence 边界。
