# VOL 08 CODE-003 Source Freeze：LayerNorm / RMSNorm 实现

> 状态：`source_frozen / CODE-VLA-003 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结归一化轴、公式、epsilon、affine 参数、dtype 与测试边界；不把通用 norm 实现写成项目性能优化。

## 问题（Question）

手写 LayerNorm 与 RMSNorm 时，如何确定归一化维度、解释两者是否减均值、处理 epsilon/低精度/affine，并验证训练与推理一致性？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [PyTorch LayerNorm](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html) | official API docs；2026-07-18 | normalized shape、均值/方差、elementwise affine、epsilon | 用户项目具体 norm 路径或 uplift |
| [PyTorch RMSNorm](https://docs.pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html) | official API docs；2026-07-18 | RMS 归一化、normalized shape、affine 与 eps | 所有模型都用同一 epsilon/dtype |
| [Root Mean Square Layer Normalization](https://arxiv.org/abs/1910.07467) | primary paper；2019 | RMSNorm 不做 re-centering、只按 RMS 缩放的动机 | 用户项目已复现效率或质量收益 |
| 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) | local canonical knowledge | pre-norm/post-norm、Transformer 基础 | CODE-VLA-003 的本地实现/parity |

## 2. 冻结数学与 shape 合同

LayerNorm：

\[
y=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta.
\]

RMSNorm：

\[
y=\gamma\odot\frac{x}{\sqrt{\operatorname{mean}(x^2)+\epsilon}}.
\]

对 Transformer 常见输入 `[B,L,D]`，默认沿最后 `D` 归一化，每个 token 独立；若 `normalized_shape` 包含多维，则沿末尾多维归一化。LayerNorm 通常有 \((\gamma,\beta)\)，RMSNorm 通常只有缩放 \(\gamma\)。

## 3. 测试门

最小矩阵：已知小张量、任意 batch/sequence、不同 normalized shape、constant input、零输入、极大/极小值、fp16/bf16 与 fp32 累加、affine on/off、forward/backward parity、train/eval 相同输入。LayerNorm/RMSNorm 不依赖 running statistics，不能照搬 BatchNorm 的训练/推理逻辑。

## 4. VLA 边界

VLA/VLM backbone 中 norm 可出现在 attention/MLP 前后或 action expert 内；pre-norm/post-norm、epsilon、dtype 和 residual path 共同影响稳定性。看到 `RMSNorm` 不能自动得出“更快/更好”，更不能把上游模型的 norm 选择写成个人创新。

## 5. Source gate 结论

官方 API 与 RMSNorm 论文足以冻结公式、axis、affine、epsilon 和测试合同；当前没有本地 CODE-VLA-003 forward/backward parity 或项目 ablation，因此保持 `WARN`。

下一步：保持已同步的 CODE-VLA-003 题卡为 `unseen`，进行白板练习或补充 norm parity artifact。

## References

1. PyTorch [`LayerNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html) 与 [`RMSNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html)。
2. Zhang & Sennrich, [Root Mean Square Layer Normalization](https://arxiv.org/abs/1910.07467)。
3. 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html)。
