# VOL 08 CODE-001：数值稳定的 softmax / log-softmax 实现

> 状态：`drafted / CODE-VLA-001 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-001 Source Freeze](../sources/vol_08_code001_softmax_source_freeze.html)。

## 问题（Question）

手撕 softmax 不只是写出指数公式。面试官通常会继续追问数值稳定性、`dim`、mask、低精度、全 masked 行、梯度和它在 attention/CE/action-token 中的边界。

## 1. 直觉：先把最大值搬到零

直接计算 (e^{1000}) 会溢出，直接计算 (e^{-1000}) 可能下溢。因为 softmax 对整体平移不敏感，可以令 (m=\max(z))，先计算 (z-m)：最大项变成 0，指数最多为 1。

## 2. 数学与实现映射

\[
 p_i=\frac{\exp(z_i)}{\sum_j\exp(z_j)},\qquad
 \log p_i=z_i-\operatorname{logsumexp}(z).
\]

`z` 是沿 `dim` 归一化的 logits；`p` 的和为 1；`logsumexp` 通过稳定的 max-shift 计算。实现时不要先 `softmax` 再 `log`，而应直接使用 `log_softmax` 或 `logsumexp`，避免概率下溢。

### 2.1 手写 forward

```python
def stable_softmax(x, dim=-1):
    # Accumulate in a wider dtype when the input is low precision.
    work = x.float() if x.dtype in (torch.float16, torch.bfloat16) else x
    shifted = work - work.amax(dim=dim, keepdim=True)
    exp = shifted.exp()
    probs = exp / exp.sum(dim=dim, keepdim=True)
    return probs.to(dtype=x.dtype)
```

代码中的 `keepdim=True` 保证广播维度正确；`amax` 与 `sum` 都沿同一个 `dim`。低精度输入是否 cast 回原 dtype，要由调用方的误差和 kernel contract 决定。

### 2.2 手写 log-softmax

```python
def stable_log_softmax(x, dim=-1):
    # Compute logsumexp without materializing an unstable exp(x).
    work = x.float() if x.dtype in (torch.float16, torch.bfloat16) else x
    m = work.amax(dim=dim, keepdim=True)
    lse = m + (work - m).exp().sum(dim=dim, keepdim=True).log()
    return (work - lse).to(dtype=x.dtype)
```

生产代码优先使用框架 fused `log_softmax`；手写版本的价值在于解释 shape、dtype、mask 和测试，而不是替代高度优化 kernel。

## 3. Mask 语义

### 3.1 Attention mask

对不允许读取的位置，常见做法是将 logits 加上 (-\infty) 或使用 bool mask。它改变信息流：被 mask 的位置不应获得 attention probability。

### 3.2 Loss mask

`loss_mask` 决定哪些 label 参与梯度；它不等于 attention mask。VLA 中 image/prompt token 可能可见但不计 CE loss，action token 可能需要 loss；必须分别记录。

### 3.3 全 masked 行

如果一整行都被加上 `-inf`，`max` 和 `logsumexp` 可能产生 `-inf - (-inf)=NaN`。系统必须提前规定：reject、返回全零并标记 invalid，或由上游保证每行至少一个 valid key。不能让 NaN 静默进入 attention 或 action head。

## 4. 梯度与复杂度

对 softmax Jacobian：

\[
\frac{\partial p_i}{\partial z_j}=p_i(\delta_{ij}-p_j).
\]

这说明概率越尖，非主类梯度越小；过大的 logits 会使 softmax 饱和。沿长度 (L) 的 dense softmax 通常是 (O(L)) 的归一化，但 attention 的 (QK^\top) 仍可能是 (O(L^2))；不要把 softmax 稳定性误说成 attention 复杂度优化。

## 5. 测试矩阵

| 测试 | 断言 | 发现的 bug |
| --- | --- | --- |
| known small logits | 沿 dim 和为 1，值接近手算 | dim/keepdim 错 |
| extreme ±1000 | 无 NaN/Inf，结果与框架接近 | 未 max-shift |
| batch/transpose | shape 与任意 dim 正确 | 广播轴错 |
| bool/float mask | masked probability/gradient 符合 contract | mask 加法方向错 |
| all masked row | 按约定返回 invalid/zero/reject | `-inf-(-inf)` NaN |
| fp16/bf16 | forward/backward finite，误差在阈值内 | 低精度累加溢出 |
| autograd parity | 与框架 forward/backward 差异受控 | 手写 backward 或 cast 错 |

最小属性测试：随机生成不同 batch、长度、dim、dtype 和 mask，比较 `stable_log_softmax(x).exp()` 与 `stable_softmax(x)`，并与框架结果做 toleranced parity。对于全 masked 行，属性测试必须跳过或验证显式 invalid 分支。

## 6. VLA 映射与边界

- **Attention**：对 (QK^\top/\sqrt{d_k}) 做 mask+softmax，决定 token 信息流；scale、mask 和 softmax 是不同合同。
- **Action token CE**：使用 `log_softmax`/交叉熵，prompt/image label 可能由 `loss_mask` 排除。
- **Continuous action**：MSE、Huber、diffusion/flow vector field 不需要 softmax；动作维度不能因为“概率和为 1”而被错误归一化。
- **Routing**：softmax 权重可表示 mixture/router probability，但还需说明 temperature、capacity、load balance 和 auxiliary loss。

## 7. 项目挂钩与真实性边界

OpenPiVLA 的 causal-CE、OPD 的 scorer、WAM/UWM 的 mask/routing 可用于讨论“概率/监督/条件 mask 的区别”；但当前项目没有本地 CODE-VLA-001 手写实现、dtype benchmark 或梯度 parity artifact。面试时可以解释实现和测试设计，不能声称某项目因自写 softmax 获得性能提升。

## 8. 结论与下一步

稳定 softmax 的核心是 max-shift、正确 dim、明确 mask/全 masked 行和合适的累加 dtype；log-softmax 应避免先算概率再取 log。手撕题的高分点是同时给出代码、边界测试、梯度/复杂度解释和 VLA mask 映射，而不是只背公式。

下一步：保持 `CODE-VLA-001` 题卡为 `unseen`，进行一次白板/实现练习，或补充 dtype/device parity artifact。

## References

1. [CODE-001 Source Freeze](../sources/vol_08_code001_softmax_source_freeze.html)。
2. PyTorch [`torch.softmax`](https://docs.pytorch.org/docs/stable/generated/torch.softmax.html)、[`log_softmax`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) 与 [`CrossEntropyLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)。
3. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)。
4. 本仓库 [VOL 01 Foundations](vol_01_foundations.html) 与 [VOL 03 architecture/mask audit](../sources/vol_03_architecture_execution_claim_to_code.html)。
