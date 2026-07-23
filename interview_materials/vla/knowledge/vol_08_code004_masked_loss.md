# VOL 08 CODE-004：Masked MSE / Huber Action Loss

> 状态：`drafted / CODE-VLA-004 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-004 Source Freeze](../sources/vol_08_code004_masked_loss_source_freeze.html)。

## 问题（Question）

VLA action batch 常含不同 horizon、action dimension、padding 与缺失维度。手写 masked loss 的核心不是乘一个 mask，而是冻结 elementwise target、mask 语义、分母、sample/task weighting、空 mask 和梯度行为。

## 1. MSE 与 Huber

令误差 \(e_i=\hat a_i-a_i\)。MSE：

\[
\ell_i=e_i^2.
\]

Huber：

\[
\ell_i=\begin{cases}
\frac12 e_i^2,& |e_i|\le\delta,\\
\delta(|e_i|-\frac12\delta),& |e_i|>\delta.
\end{cases}
\]

Huber 在小误差区保持平滑二次惩罚，在大误差区改为线性，降低 outlier 的梯度支配；它不是“自动更鲁棒”，delta、单位、normalizer 和任务分布必须冻结。

## 2. Masked reduction

正确的有效元素均值通常是：

\[
L=\frac{\sum_i w_i m_i\ell_i}{\sum_i w_i m_i}.
\]

`m` 是 valid/loss mask，`w` 可是 sample/task/dimension weight。危险实现 `mean(mask * loss)` 的分母是总 slot 数，会使 padding 更多的 batch 获得更小 loss，从而改变不同 horizon/embodiment 的权重。

## 3. 手写实现

```python
def masked_huber(pred, target, mask, delta=1.0, weight=None):
    # pred/target: [B, H, D]; mask must be broadcastable to the same shape.
    work_pred = pred.float() if pred.dtype in (torch.float16, torch.bfloat16) else pred
    work_target = target.float() if target.dtype in (torch.float16, torch.bfloat16) else target
    error = work_pred - work_target
    abs_error = error.abs()
    element = torch.where(
        abs_error <= delta,
        0.5 * error.square(),
        delta * (abs_error - 0.5 * delta),
    )

    valid = mask.to(dtype=element.dtype)
    if weight is not None:
        valid = valid * weight
    denom = valid.sum()
    # Empty supervision is a data/protocol event, not an ordinary zero-loss batch.
    if denom.item() == 0:
        raise ValueError("empty masked action target")
    return (element * valid).sum() / denom
```

若分布式训练，各 rank 的 numerator/denominator 应先聚合，再相除；先在每 rank 求 mean 再平均会在有效元素数不同的情况下产生偏差。

## 4. Mask taxonomy

| mask | 控制什么 | 常见错误 |
| --- | --- | --- |
| attention mask | token 信息流 | 当作 action supervision mask |
| sequence/padding mask | 无效 timestep/slot | 只乘 loss 不改分母 |
| action-dim mask | 异构 embodiment 有效轴 | silent truncate/zero padding 当真实标签 |
| label/loss mask | 哪些 target 产生梯度 | 与 causal mask 混淆 |
| task/sample weight | 样本/任务贡献 | 与二值 valid mask 混成同一语义 |

mask 应先扩展到 elementwise loss shape，再检查 dtype、0/1 或非负权重、广播维和有效计数。

## 5. 空 mask 与异常值

全零 mask 可能来自数据 bug、空 action chunk、过滤后无有效维或路由错误。安全处理是 reject/skip 并记录 `episode/sample/reason`；若必须返回零梯度，应显式标记 `skipped_step`，不能把它记成正常低 loss。

NaN/Inf target、weight 或 prediction 应在乘 mask 前检测，因为 `0 * NaN` 仍可能产生 NaN。异常 outlier 是否用 Huber 处理，要先确认它是合法长尾还是单位/normalizer/axis 错误。

## 6. Weighting 与可比性

不同任务可以按 episode、sample、timestep、action dimension 或 task weight 聚合。每种 denominator 表达不同问题：

- per-element mean：每个有效 action 维等权；
- per-step mean：先对维度平均，再对有效 timestep；
- per-episode mean：每个 episode 等权；
- per-task macro：每个 task 等权；
- global micro：所有有效元素共同计数。

报告 loss 时必须写清 reduction；否则不同 horizon、D 或数据比例之间不能比较。

## 7. 测试矩阵

| 测试 | 断言 | 典型 bug |
| --- | --- | --- |
| mask=1 | 与框架 elementwise+mean 相同 | 公式/reduction 错 |
| 部分 timestep/dim | 只有效元素有梯度 | broadcast/分母错 |
| 不同 padding 比例 | 相同有效元素得到相同 loss | `mean(mask*loss)` |
| all-zero mask | reject/skip contract 生效 | 伪零 loss |
| Huber delta 边界 | 分段连续、梯度方向正确 | delta/系数错 |
| outlier | Huber 梯度线性增长 | 仍被平方项支配 |
| fp16/bf16 | finite、与 fp32 对照受控 | 低精度 square 溢出 |
| distributed counts | global numerator/denominator 一致 | rank mean 平均偏差 |
| autograd parity | 与 PyTorch elementwise loss 接近 | where/cast/weight 错 |

## 8. VLA 映射

- ACT/continuous regression 可对 action chunk 使用 L1/MSE/Huber，并用 timestep/dim mask。
- Diffusion/Flow Matching 常对 noise/vector field 做 MSE，但要冻结 timestep weight、condition mask、target 与 reduction。
- action token 模型使用 CE/token mask，不应把 token ID 当 continuous value 做 MSE。
- action normalizer 改变误差单位；Huber delta 必须在同一 normalized/physical space 下解释。

## 9. 项目挂钩与真实性边界

OpenPiVLA 可连接 action chunk、valid dims、normalizer 和 causal-CE；UWM/WAM 可连接 action/video target mask 与多任务 reduction；OPD 可连接 metric-specific denominator。当前没有本地 CODE-VLA-004 parity、empty-mask log 或 matched MSE/Huber ablation，因此只能讲实现与审计方法。

## 10. 结论与下一步

masked loss 的高分答案是：先算 elementwise MSE/Huber，再用 valid mask/weight 得到 numerator 和有效 denominator；空 mask 作为数据事件处理；低精度用 fp32 累加；分布式聚合 numerator/denominator；最后说明 reduction 与 VLA action schema。不能把 `mean(mask*loss)`、伪零 loss 或不同 denominator 的数字直接比较。

下一步：保持 `CODE-VLA-004` 题卡为 `unseen`，进行一次白板/实现练习，或补充 empty-mask/parity artifact。

## References

1. [CODE-004 Source Freeze](../sources/vol_08_code004_masked_loss_source_freeze.html)。
2. PyTorch [`MSELoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)、[`HuberLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html) 与 [`SmoothL1Loss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.SmoothL1Loss.html)。
3. 本仓库 [VOL 03 action audit](../sources/vol_03_architecture_execution_claim_to_code.html) 与 [VOL 05 heterogeneous batch](vol_05_engineering_eval_batch2a.html)。
