# VOL 08 CODE-001 Source Freeze：数值稳定的 softmax / log-softmax

> 状态：`source_frozen / CODE-VLA-001 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 softmax、log-softmax、mask、dtype 与测试边界；不把一个手写函数升级为完整 VLA 训练实现。

## 问题（Question）

手撕 softmax 时，怎样避免 overflow/underflow，正确处理 batch、axis、mask、全 masked 行和低精度，并说明它如何映射到 attention、CE loss 或 action-token 分布？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [PyTorch `torch.softmax`](https://docs.pytorch.org/docs/stable/generated/torch.softmax.html) | official API docs；2026-07-18 | `dim` 语义、输出形状与概率归一化接口 | 用户项目具体实现或性能结果 |
| [PyTorch `torch.log_softmax`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) | official API docs；2026-07-18 | fused log-softmax 的数值稳定接口与 `dim` | 手写版本在所有 dtype/device 上等价 |
| [PyTorch CrossEntropyLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html) | official API docs；2026-07-18 | CE 内部应组合 log-softmax/NLL、target/mask 语义 | VLA action loss 已使用同一实现 |
| [PyTorch scaled dot-product attention](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) | official API docs；2026-07-18 | attention logits、scale、bool/float mask 的机制参照 | 项目已采用同一 kernel 或 flash backend |
| 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) | local canonical knowledge | softmax、attention、mask 的基础解释 | CODE-VLA-001 的 dtype/test 通过 |

## 2. 冻结的数学与边界

对向量 (z)，

\[
\operatorname{softmax}(z_i)=\frac{e^{z_i}}{\sum_j e^{z_j}},\qquad
\operatorname{logsoftmax}(z_i)=z_i-\operatorname{logsumexp}(z).
\]

平移不变性允许先减去 (m=\max_i z_i)：

\[
\operatorname{softmax}(z)=\operatorname{softmax}(z-m).
\]

实现必须冻结：沿哪个 `dim` 归一化、mask 是加 `-inf` 还是 bool 屏蔽、全 masked 行返回什么、累加 dtype、NaN/Inf 策略、空张量行为和梯度预期。

## 3. 测试门

最小测试矩阵：

1. 小数值与已知概率；
2. 大正/大负 logits，检查无 `inf/nan`；
3. batch 与任意 `dim`，检查输出 shape 和沿 dim 求和；
4. bool/float mask，检查 masked 位置概率/梯度；
5. 全 masked 行，显式规定 `-inf`、zero 或 reject，不能静默传播 NaN；
6. float16/bfloat16 输入，检查是否在 float32 中归一化后再 cast；
7. 与框架 `softmax/log_softmax` forward/backward 对照；
8. extreme logits 与 finite-difference/autograd 梯度 smoke。

## 4. VLA 边界

softmax 可出现在 attention 权重、分类/action token 分布或 routing probability；continuous action MSE、diffusion/flow vector loss 不需要把动作强行 softmax。`attention_mask`、`valid_mask` 和 `loss_mask` 语义不同：前者限制信息流，后者限制监督；不要只因实现了 softmax 就声称 VLA mask 正确。

## 5. Source gate 结论

官方文档足以支持稳定实现、dim/mask/CE/attention 机制；本地基础页提供 VLA 语境。当前没有一个用户项目的手写 softmax、dtype benchmark 或梯度 parity artifact，因此下游保持 `WARN`。

下一步：保持已同步的 CODE-VLA-001 题卡为 `unseen`，进行白板练习或补充 parity artifact。

## References

1. PyTorch [`torch.softmax`](https://docs.pytorch.org/docs/stable/generated/torch.softmax.html)、[`log_softmax`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) 与 [`CrossEntropyLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)。
2. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)。
3. 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html)。
