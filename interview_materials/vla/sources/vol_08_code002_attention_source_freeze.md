# VOL 08 CODE-002 Source Freeze：Scaled Dot-Product Attention 实现

> 状态：`source_frozen / CODE-VLA-002 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 Q/K/V shape、scale、causal/padding mask、dropout 与复杂度测试边界；不把通用实现写成项目原创。

## 问题（Question）

手写 scaled dot-product attention 时，怎样处理多头 shape、(1/\sqrt{d_k}) 缩放、bool/float mask、causal 方向、dropout、低精度和复杂度？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [PyTorch `scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) | official API docs；2026-07-18 | Q/K/V shape、scale、attn mask、causal 与 dropout 参数语义 | 用户项目采用同一 kernel/backend |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | primary paper；2017 | scaled dot-product、multi-head、复杂度与 mask 机制 | 项目已复现论文性能 |
| [PyTorch MultiheadAttention](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html) | official API docs；2026-07-18 | batch/sequence/head 维度与 `key_padding_mask`/`attn_mask` 参照 | 自写实现已通过所有 backend parity |
| 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) | local canonical knowledge | attention scale、mask、RoPE 基础 | CODE-VLA-002 的 shape/device 测试 |
| 本仓库 [VOL 03 architecture audit](../sources/vol_03_architecture_execution_claim_to_code.html) | local source audit | VLA sequence layout、attention/loss mask 分离、OpenVLA/Octo/π 的实现边界 | 用户项目使用同一 attention mask |

## 2. 冻结数学与 shape 合同

\[
\operatorname{Attn}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.
\]

典型多头 shape 为 `Q:[B,H,Lq,D]`、`K/V:[B,H,Lk,D]`，score 为 `[B,H,Lq,Lk]`，输出为 `[B,H,Lq,D]`。`M` 可以是广播到 score 的 float bias，也可以是 bool allow/deny mask；两种语义必须明确。

## 3. 测试与风险边界

最小测试矩阵：shape/transpose、单头手算、causal future blocking、padding mask、不同 `Lq/Lk`、`D` 缩放、dropout train/eval、fp16/bf16 finite、全 masked row、autograd parity、(O(BHL_qL_kD)) score/value 复杂度 smoke。不要把 `attn_mask` 与 `loss_mask` 混淆，也不要把 SDPA 的 fused backend 当作手写实现自动获得的性能。

## 4. VLA 边界

image/text/proprio/action token 的 sequence layout、prefix/suffix/causal 方向和 action loss mask 决定信息流与监督；continuous action head 的 MSE/diffusion/flow loss 不等于 attention probability。一个 attention forward 通过只支持 mechanism，不支持闭环成功或项目 uplift。

## 5. Source gate 结论

官方 API 与论文足以冻结 shape、scale、mask、dropout 和复杂度合同；当前没有本地 CODE-VLA-002 实现或多后端 parity artifact，因此下游保持 `WARN`。

下一步：保持已同步的 CODE-VLA-002 题卡为 `unseen`，进行白板练习或补充 attention parity/profile artifact。

## References

1. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) 与 [`MultiheadAttention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)。
2. Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762)。
3. 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) 与 [VOL 03 architecture audit](../sources/vol_03_architecture_execution_claim_to_code.html)。
