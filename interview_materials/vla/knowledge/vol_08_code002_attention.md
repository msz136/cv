# VOL 08 CODE-002：Scaled Dot-Product Attention 手写与调试

> 状态：`drafted / CODE-VLA-002 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-002 Source Freeze](../sources/vol_08_code002_attention_source_freeze.html)。

## 问题（Question）

手写 attention 需要同时处理 Q/K/V shape、head 拆分、(1/\sqrt{d_k}) scale、mask 方向、不同 query/key 长度、dropout 和低精度。VLA 还要区分 attention mask 与 action loss mask。

## 1. 数学与 shape

\[
S=\frac{QK^\top}{\sqrt{d_k}}+M,\qquad
A=\operatorname{softmax}(S),\qquad
Y=AV.
\]

典型 shape：`Q:[B,H,Lq,D]`、`K/V:[B,H,Lk,D]`；`Q @ K.transpose(-2,-1)` 得 `[B,H,Lq,Lk]`；`A @ V` 回到 `[B,H,Lq,D]`。最后合并 head 为 `[B,Lq,H*D]`。`Lq` 与 `Lk` 可以不同，不能只用一个 `L` 写死。

## 2. 手写实现

```python
def attention(q, k, v, mask=None, dropout_p=0.0, training=True):
    # q/k/v: [B, H, L, D]; only the last two axes are contracted.
    d = q.size(-1)
    work_q = q.float() if q.dtype in (torch.float16, torch.bfloat16) else q
    work_k = k.float() if k.dtype in (torch.float16, torch.bfloat16) else k
    scores = work_q @ work_k.transpose(-2, -1) / math.sqrt(d)

    # Apply a bool allow-mask or an additive float bias before softmax.
    if mask is not None:
        scores = apply_attention_mask(scores, mask)
    weights = torch.softmax(scores, dim=-1)
    if training and dropout_p > 0:
        weights = torch.dropout(weights, dropout_p, train=True)
    out = weights @ (v.float() if v.dtype in (torch.float16, torch.bfloat16) else v)
    return out.to(dtype=q.dtype)
```

关键是只在最后两个维度做矩阵乘法，softmax 沿 key 维 `Lk`，mask 在 softmax 前应用，低精度可在更宽 dtype 中计算。生产环境优先使用 fused SDPA；手写版本用于解释 shape、契约和测试。

## 3. (1/\sqrt{d_k}) 为什么必要

若 query/key 各维近似独立、方差相近，点积方差随 (d_k) 增长。未缩放的 score 进入 softmax 后容易过尖，非主位置梯度变小；除以 (sqrt{d_k}) 把 logit 尺度拉回稳定范围。它是尺度控制，不是让 softmax “变成概率”的原因。

## 4. Mask 语义与 causal 方向

### 4.1 Bool 与 additive mask

bool mask 必须规定 `True` 是 allow 还是 deny；float mask 通常把禁止位置加上极小值或 (-\infty)。实现中必须统一语义，不能把 `key_padding_mask` 的 convention 直接套到自定义 `attn_mask`。

### 4.2 Causal mask

自回归 query 位置 (i) 只能读取 key 位置 (j\le i)。若 `Lq != Lk` 或使用 prefix/suffix layout，不能凭矩阵左上角猜方向；应写出 query/key 的物理位置映射，并用 future-blocking 单测验证。

### 4.3 全 masked 行

整行都被禁止时，`softmax(-inf,...,-inf)` 可能返回 NaN。系统必须规定 reject、返回 invalid/zero，或保证每行至少一个 valid key；不能静默把 NaN 送入 action head。

## 5. Dropout、dtype 与复杂度

dropout 只在训练时打开，评估/推理必须为 0；不要在手写函数中忽略 `training`。score/value 的主要计算量近似为 (O(BHL_qL_kD))，显存还包含 `[B,H,Lq,Lk]` 的 score/weight；softmax 本身是沿 `Lk` 的归一化，不等于 attention 整体变成线性复杂度。fp16/bf16 可用 fp32 累加，但输出 cast 与误差阈值要由接口冻结。

## 6. 测试矩阵

| 测试 | 断言 | 典型 bug |
| --- | --- | --- |
| 单头小矩阵 | 与手算 score/weight/output 一致 | transpose/scale 错 |
| 多头 batch | 输出 `[B,H,Lq,D]`，合并 head 正确 | head/hidden reshape 错 |
| `Lq != Lk` | score `[B,H,Lq,Lk]`、softmax 沿 `Lk` | 写死 square attention |
| causal | future key 权重为 0 | mask 方向反 |
| padding | padded key 不被读取 | mask broadcast 错 |
| train/eval dropout | eval deterministic，train 可随机 | 忘记 training flag |
| fp16/bf16 | finite，误差与 fp32 对照受控 | 低精度 score 溢出 |
| all masked row | 按 contract invalid/zero/reject | `-inf-(-inf)` NaN |
| autograd parity | 与 PyTorch SDPA 梯度差异在 tolerance 内 | 手写路径不等价 |

## 7. VLA 映射

- image/text/proprio/action token 的排列决定 Q/K/V 能看到什么；prefix/suffix 与 causal mask 必须画成信息流图。
- `attention_mask` 控制可见性；`loss_mask` 控制哪些 token 产生 CE/ action loss，二者不能混称。
- continuous action 的 MSE、diffusion 或 flow vector field loss 不需要对动作维度做 softmax。
- fused SDPA、FlashAttention 或特定 backend 的速度需要独立 benchmark；forward parity 不自动证明 latency、显存或真机收益。

## 8. 项目挂钩与真实性边界

OpenPiVLA 可连接 causal-CE、eager attention 与 action packaging；OPD 可连接 token/format scorer；WAM/UWM 可连接 condition/mask/routing，但这些都只是机制或局部代码证据。当前没有本地 CODE-VLA-002 多 backend parity、profile 或项目 uplift artifact。

## 9. 结论与下一步

手写 attention 的高分答案是：先固定 `[B,H,L,D]` 合同，再做 (QK^\top/\sqrt{d_k})、沿 key 维 softmax、mask/causal/dropout、`AV` 和 head merge；随后用不同长度、mask、低精度、梯度与 fused SDPA parity 测试。它能证明实现理解，不能直接证明 VLA 项目性能。

下一步：保持 `CODE-VLA-002` 题卡为 `unseen`，进行一次白板/实现练习，或补充多 backend attention parity/profile artifact。

## References

1. [CODE-002 Source Freeze](../sources/vol_08_code002_attention_source_freeze.html)。
2. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) 与 [`MultiheadAttention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)。
3. Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762)。
4. 本仓库 [VOL 01 Foundations](vol_01_foundations.html) 与 [VOL 03 architecture audit](../sources/vol_03_architecture_execution_claim_to_code.html)。
