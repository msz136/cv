# VOL 08 CODE-004 Source Freeze：Masked MSE / Huber Action Loss

> 状态：`source_frozen / CODE-VLA-004 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 elementwise loss、mask、reduction denominator、Huber delta 与空 mask 边界；不把通用 loss 实现写成项目收益。

## 问题（Question）

手写带 mask 的 MSE / Huber loss 时，怎样处理 action padding、valid dimensions、broadcast、sample/task weighting、空 mask、低精度和 reduction，使不同 horizon/embodiment 的 loss 可比？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [PyTorch MSELoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html) | official API docs；2026-07-18 | elementwise squared error 与 reduction 语义 | 用户项目 mask/reduction 已正确 |
| [PyTorch HuberLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html) | official API docs；2026-07-18 | quadratic/linear 分段、delta 与 reduction | Huber 必然提升机器人成功率 |
| [PyTorch SmoothL1Loss](https://docs.pytorch.org/docs/stable/generated/torch.nn.SmoothL1Loss.html) | official API docs；2026-07-18 | 与 Huber 的 beta/delta scale 关系参照 | 两个 API 在任意参数下数值完全相同 |
| 本仓库 [VOL 03 action audit](../sources/vol_03_architecture_execution_claim_to_code.html) | local source audit | action padding mask、有效维、continuous loss 边界 | 所有 VLA 都使用相同 reduction |
| 本仓库 [VOL 05 heterogeneous batch](../knowledge/vol_05_engineering_eval_batch2a.html) | local knowledge | padding/valid/loss mask、heterogeneous schema 与 denominator 风险 | 项目已有 matched loss ablation |

## 2. 冻结数学合同

MSE elementwise：

\[
\ell_i=(\hat a_i-a_i)^2.
\]

Huber：

\[
\ell_i=\begin{cases}
\frac12 e_i^2,& |e_i|\le\delta,\\
\delta(|e_i|-\frac12\delta),& |e_i|>\delta.
\end{cases}
\]

masked mean 应除以有效权重和：

\[
L=\frac{\sum_i m_i\ell_i}{\max(\sum_i m_i,\epsilon_{count})}.
\]

空 mask 时不能悄悄返回伪零并参加优化；应 reject/skip 并记录原因，或按明确 contract 返回零梯度。

## 3. 测试门

最小矩阵：无 mask 与框架 parity、部分 action-step/dim mask、broadcast、全零 mask、不同 horizon/有效维、sample/task weight、delta 边界、极端 outlier、fp16/bf16 finite、gradient parity。`mean(mask*loss)` 会把 padding 数量带进分母，通常是高危错误。

## 4. VLA 边界

action padding mask、valid-dimension mask、attention mask 和 label/loss mask 不同。MSE/Huber 适合 continuous regression；diffusion/flow loss 可能对 noise/vector field 做 MSE，但 target、timestep weight 和 reduction 必须单独冻结；action token CE 不是 masked MSE。

## 5. Source gate 结论

官方 API 与本仓库 action/schema 审计足以冻结公式、mask 和 reduction 边界；当前没有本地 CODE-VLA-004 parity、empty-mask incident 或 matched Huber/MSE ablation，因此保持 `WARN`。

下一步：保持已同步的 CODE-VLA-004 题卡为 `unseen`，进行白板练习或补充 masked-loss parity artifact。

## References

1. PyTorch [`MSELoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)、[`HuberLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html) 与 [`SmoothL1Loss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.SmoothL1Loss.html)。
2. 本仓库 [VOL 03 architecture/action audit](../sources/vol_03_architecture_execution_claim_to_code.html) 与 [VOL 05 heterogeneous batch knowledge](../knowledge/vol_05_engineering_eval_batch2a.html)。
