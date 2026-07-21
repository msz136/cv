# VOL 04 World Model / Sim2Real：Action–Video Joint Objective 审计（WM-016）

> 状态：`drafted / knowledge_18_of_44 / card_deferred / WARN`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-WM-016`；本轮只生成 knowledge node，不生成题卡，不创建 coaching state。  
> 前置：[UWM Video–Action Coupling](vol_04_world_model_sim2real_wm015.html)、[WM-016 Source Freeze](../sources/vol_04_wm016_joint_objective_source_freeze.html)、[Cosmos/WAM Source Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。

## 问题（Question）

action/video joint objective 的共享表示、condition、noise schedule 和 mask 应怎样审计？面试中不能把“共享 backbone”“联合采样”“condition mask”和“loss mask”混成一个概念；必须先确认 prediction target、slot/token contract、sample routing、reduction 和实际 gradient。

## 证据边界与学习位置

```text
WM-015 UWM video/action coupling
                 ↓
WM-016 joint objective / mask / reduction audit
                 ↓
WM-017 heterogeneous embodiment and data schema
                 ↓
WM-025..028 Cosmos/WAM multi-objective routing
```

本页统一的是“审计框架”，不是把 UWM 与 Cosmos/WAM 写成同一实现：

- UWM 的 frozen contract：shared diffusion transformer、dual timestep、epsilon-noise prediction、robot/action-free tuple，以及当前 action MSE 与 `action_mask` 的边界。[1][2]
- Cosmos/WAM 的 frozen contract：action/proprio/future/value latent slots、EDM-style noisy latent、condition/sample routing、可选 target mask 和 action loss multiplier。[3][4]
- 本页不支持 checkpoint 已复现、paired ablation 已完成或用户项目 joint objective 有个人原创；这些仍在 evidence 层。[5][6]

## 1. 先分清四种“共享”

### 1.1 共享表示（representation sharing）

UWM 把 noisy action token、future-video patch token、register 和 observation condition 送入共享 AdaLN/DiT blocks，输出端再分 action decoder 与 video unpatchifier。Cosmos/WAM 则把 action、proprio、future observation、value 等写入统一 latent-video frame/slot，并由 routing 决定当前 sample 需要预测哪些 slot。

二者都允许 modality interaction，但 token 的排列、latent 的物理含义、decoder/denoiser target 和 checkpoint contract 不同。面试回答应该说“共享交互路径”，而不是“同一个三头实现”。

### 1.2 共享条件（conditioning）

condition 是输入侧语义：某个分支可以被 clean action、clean future、current observation 或 clean latent slot 条件化。它决定采样分布，不自动决定 loss 是否计算。

### 1.3 共享噪声调度（noise schedule）

UWM 为 action 与 video 使用独立 timestep；Cosmos/WAM 以 EDM/HybridEDMSDE 的 sigma 产生 noisy latent。即使两个系统都叫 diffusion，也要先核对是 epsilon、(x_0)、velocity 还是 score target，再谈 loss 数值。

### 1.4 共享目标（joint objective）

joint objective 是多项 loss 如何聚合的问题：哪些样本、哪些 slot、哪些 axis 参与 reduction，是否有 modality weight，分母按 batch、token 还是有效元素计算。它与共享 backbone、condition mask 均不是同义词。

## 2. 抽象目标与变量解释

为了审计不同实现，可以先写一个不绑定具体框架的合同：

\[
\mathcal{L}=\sum_{m\in\mathcal{M}}\lambda_m\cdot
\frac{\sum_{b,t,d}M^{(m)}_{btd}\,\ell_m(\hat y^{(m)}_{btd},y^{(m)}_{btd})}
{\max\left(1,\sum_{b,t,d}M^{(m)}_{btd}\right)}.
\]

变量解释：(m) 是 action、video、future 或 value 等任务；(lambda_m) 是显式 loss weight；(M^{(m)}) 是真正作用于 target reduction 的 mask；(ell_m) 必须与 prediction target 匹配。直觉是“先确定谁在学习，再比较学得多好”。实现映射是查找 loss 调用点、`reduction`、`where`/乘法、denominator、config flag 和日志字段；这个式子不是断言 UWM/Cosmos 都采用同一公式。

### 2.1 UWM 的具体边界

UWM frozen code 的已核实形态可以简化为：

\[
\mathcal{L}_{UWM}=\operatorname{MSE}(\hat\epsilon_a,\epsilon_a)+
\operatorname{MSE}(\hat\epsilon_y,\epsilon_y).
\]

其中 (hat\epsilon_a,hat\epsilon_y) 分别是 action/video noise prediction。当前审计记录显示，两项调用全张量 `F.mse_loss` 后相加；`action_mask` 只将 action-free video 的 action timestep 推到最大训练步，并不等价于 (M^{(a)}=0)。是否存在非零 action gradient，仍需 pinned runtime 的实验确认。

### 2.2 Cosmos/WAM 的具体边界

Cosmos/WAM 先将 clean action、future state/image 与 value 写入统一 latent sequence，再用 EDM/HybridEDMSDE 得到 noisy latent，denoiser 输出 (\hat x_0)。condition mask 表示哪些 frame/slot 是 clean condition；可选 target mask 与 `action_loss_multiplier` 才涉及哪些 target 进入 loss。不同 policy/world/value/V/Q sample routing 可能使用不同 mask 组合，不能只依据配置名推断主实验实际打开了哪些分支。[3]

## 3. Condition mask、sample routing 与 target mask

| 层级 | 它回答什么 | UWM | Cosmos/WAM |
| --- | --- | --- | --- |
| sample routing | 这个样本属于哪种任务分布？ | robot tuple / action-free video | policy / world / value / V / Q variants |
| condition mask | 哪些输入保持 clean、哪些需要 denoise？ | clean action/future 或 nuisance high-noise branch | latent frame/slot 的 clean condition mask |
| noise schedule | 以什么噪声强度构造输入？ | action/video independent timestep | EDM sigma / HybridEDMSDE |
| target loss mask | 哪些输出元素进入 loss reduction？ | 当前 action MSE 未显式 sample mask | 可选 action/future/value target mask，需查 flag 与调用点 |
| metric mask | 日志里统计哪些元素？ | marginal/forward/inverse/joint proxy | action/future/value component metrics 与 success/planning metrics |

一个常见错误是看到 `mask=1` 就断言“该项被 mask 掉”。Cosmos condition mask 的 `1` 可表示 clean condition；UWM 的 `action_mask=False` 表示 action-free sample，随后代码只改变 timestep。面试中必须说清 mask 的层级和正负语义。

## 4. Prediction target 与 schedule 审计

### 4.1 UWM：双 timestep，不是双标签

令 (a_{t_a}) 为 noisy action，(y_{t_y}) 为 noisy future-video latent，(c(o)) 为当前 observation condition，则共享预测器可抽象为：

\[
(\hat\epsilon_a,\hat\epsilon_y)=F_\theta\left(
E_a(a_{t_a}),E_y(y_{t_y}),c(o),e(t_a,t_y),R\right).
\]

(E_a) 是 action MLP，(E_y) 是 video patchifier，(e) 是两路 timestep embedding，(R) 是 register tokens。独立 timestep 让同一网络表达 policy、forward、inverse、marginal video 与 joint sampling 的不同 conditional slice；它不是简单的 task ID。

### 4.2 Cosmos/WAM：EDM noisy latent 与 (x_0) target

Cosmos/WAM 审计中的抽象形式是：

\[
x_\sigma=\operatorname{EDMNoise}(x_0,\sigma),\qquad
\hat x_0=D_\theta(x_\sigma,\sigma,c,m),
\]

其中 (x_0) 是 action/future/value latent sequence，(sigma) 是 noise level，(c) 是 clean condition，(m) 是 condition/routing mask。实现中主反向项是 noise-weighted latent objective；日志里的 action/future/value L1/MSE 主要用于诊断，不能直接当作主 loss。

### 4.3 跨实现比较规则

只有在以下条件都冻结后，才可以比较两个 loss：prediction target、normalizer/latent scale、noise schedule、slot/token mask、reduction denominator、data mixture、checkpoint revision 和 metric script。否则“UWM MSE 更低”与“WAM L1 更低”没有直接排序意义。

## 5. 从源码到实验的审计顺序

```text
1. Freeze source / commit / config / checkpoint manifest.
2. Print sample routing and raw mask values before any transform.
3. Print noisy input, timestep/sigma, prediction target and output shape.
4. Locate the exact loss call, reduction, denominator and optional weights.
5. Run one-batch gradient and mask A/B tests.
6. Run paired action-only vs action+video/value training.
7. Report component loss, intervention sensitivity and closed-loop success together.
```

每一步都需要保存 shape、dtype、seed、normalizer 和 revision。只截取训练日志中的一列 loss，无法证明 joint objective 的因果收益。

## 6. 最小伪代码：不把输入 mask 当 loss mask

```python
def audit_joint_objective(batch, model, scheduler, cfg):
    # 1. Preserve task routing before any padding or tensor conversion.
    route = batch["route"]
    action_mask = batch.get("action_mask")

    # 2. Build noisy inputs using the implementation's actual target convention.
    noisy_a, eps_a, t_a = make_action_noise(batch["action"], scheduler)
    noisy_y, eps_y, t_y = make_video_noise(batch["future"], scheduler)

    # 3. Action-free semantics may change t_a; do not call this a loss mask.
    if action_mask is not None:
        t_a = set_action_free_endpoint(t_a, action_mask, cfg.num_train_steps)

    # 4. Shared model returns modality-specific predictions.
    pred_a, pred_y = model(batch["obs"], noisy_a, t_a, noisy_y, t_y, route)

    # 5. Reproduce the frozen loss first, then compare an explicit target-mask A/B.
    frozen = mse(pred_a, eps_a) + mse(pred_y, eps_y)
    masked = masked_mse(pred_a, eps_a, action_mask) + mse(pred_y, eps_y)
    return frozen, masked
```

代码中的 `masked` 只是审计对照，不是当前 UWM 的既定实现；必须比较 loss、gradient norm、参数更新方向和 downstream rollout，不能只比较一个标量。

## 7. 失败模式与诊断

| 症状 | 优先检查 | 不能直接下的结论 |
| --- | --- | --- |
| video loss 降、action success 不变 | action-free gradient、action coverage、loss scale、normalizer、action sensitivity | 视频预训练一定没有用 |
| action loss 降、future prediction 变差 | shared-block gradient cosine、modality weight、camera/latent scale | 两任务天然冲突 |
| value loss 降、best-of-N 更差 | value calibration、OOD rank correlation、N sweep、selected-vs-random success | value head 学坏了 |
| mask 改了但结果不变 | mask 是否进入 target reduction、route 是否真的覆盖样本、denominator 是否变化 | mask 设计无效 |
| 不同实现 loss 无法比较 | target type、sigma/timestep、latent scale、reduction、checkpoint | 某个模型更强 |

最小的 causal check 是：固定 observation，做 action perturbation 或 action permutation，测 future prediction 的变化；再把 action-only 与 action+video/value 在同一 seed/split/protocol 下 paired 比较。

## 8. 项目与面试边界

### UWM / LIBERO

可以讲如何核对 action-free tuple、normalizer、checkpoint、reset/init 和 rollout protocol；不能把上游 shared DiT、WM-016 的 joint objective 或 UWM 的报告数字说成本人原创或方法定论。没有 immutable checkpoint、gradient log 和 paired ablation 时，个人项目 hook 保持 `claim-only/WARN`。

### Cosmos / WAM

可以讲 latent slot、policy/world/value routing、condition/target mask 和 best-of-N 的源码审计；但必须注明这是上游 Cosmos/WAM 设计。个人 WAM 的 MSE、0-success 或 baseline 数字仍需 checkpoint、prediction artifact、episode trace 和 ownership evidence 才能升级。

## 9. 结论与后续

WM-016 的核心不是背一个“联合损失公式”，而是建立可复核的证据链：先分 sample routing、condition mask、noise schedule 和 target loss mask，再核对 prediction target、reduction 和 gradient，最后用 paired closed-loop ablation 判断 joint objective 是否真正帮助 policy。

本节点目前为 `WARN`：source boundary 已冻结，runtime gradient、mask A/B、paired ablation、checkpoint lineage、scheduler smoke 和浏览器视觉 QA 尚未完成。本轮不生成 WM-016 题卡；下一步可在真实口述 WM-015 后，再生成一张保持 `unseen` 的 WM-016 原子题卡。

## 参考文献（References）

1. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。
2. [UWM 独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)。
3. [Cosmos/WAM Source Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
4. [Cosmos Policy 论文](https://arxiv.org/html/2601.16163v1)。
5. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [WAM evidence inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
