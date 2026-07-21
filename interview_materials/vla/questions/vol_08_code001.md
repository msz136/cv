# VOL 08 CODE-VLA-001 原子手撕题卡：数值稳定的 softmax

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-001`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-001 Knowledge](../knowledge/vol_08_code001_softmax.html)；来源边界见 [CODE-001 Source Freeze](../sources/vol_08_code001_softmax_source_freeze.html)。

## 手写稳定 softmax / log-softmax 并说明 VLA 边界

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-001</b> · 请手写数值稳定的 softmax 或 log-softmax，并说明 mask、低精度和测试怎么处理。</summary>

**面试意图**：判断你能否同时处理公式、axis/shape、数值稳定性、mask、dtype、梯度和 VLA 中 attention/loss/action 的边界，而不是只写一行 `exp(x)/sum(exp(x))`。

**30 秒回答**：先沿 dim 做 max-shift，再 exp/sum；低精度用更宽累加。log-softmax 直接算 logsumexp，不能先 softmax 再 log。mask、全 masked 行和 dtype 要定合同，并用极值、梯度、任意 dim 与框架 parity 测试。

**机制展开（约 2 分钟）**：实现 `m=x.amax(dim,keepdim=True)`，`p=exp(x-m)/sum(exp(x-m))`；fp16/bf16 在 fp32 累加后按 contract cast。log-softmax 用 `x-logsumexp(x)`；mask 区分 bool/加性，全 masked 行约定 reject/zero/invalid，避免 `-inf-(-inf)` NaN。测试 batch/transpose、±1000、mask、低精度、finite、autograd 与 PyTorch parity。attention 的 mask/scale 和 VLA loss mask 不同，continuous action MSE/diffusion 不需要 softmax。

**诊断 / 证据**：白板先写 shape/`dim`/`keepdim`，再写 max-shift 和累加 dtype；代码题至少覆盖已知小 logits、±1000、任意 batch/dim、bool/float mask、全 masked 行、fp16/bf16、NaN/Inf、forward/backward parity。若与 fused `torch.log_softmax` 对照，记录 tolerance、device、dtype 和是否 cast；不要把一次 forward 通过当作所有 kernel/device 都正确。

**项目挂钩**：OpenPiVLA 的 causal-CE、OPD 的 scorer、WAM/UWM 的 mask/routing 可用于解释监督 mask 与条件 mask 的区别；但当前没有本地 CODE-VLA-001 实现或 parity artifact。安全表达是“我能写出并测试稳定实现”，不声称某项目因手写 softmax 获得收益。

**追问树**：为什么 max-shift 不改变结果？`dim=-1` 与 `keepdim` 如何影响广播？全 masked 行为什么会 NaN？为什么 CE 不应先 softmax 再 log？fp16 为什么要更宽累加？attention mask 和 loss mask 是否相同？continuous action 为什么通常不用 softmax？

**易错点**：忘记减最大值；沿错轴归一化；`keepdim=False` 导致广播错；全 masked 行传播 NaN；先 softmax 再 log；把 bool mask 当 loss mask；把 softmax 的 (O(L)) 归一化说成 attention 变成线性复杂度。

**危险答案**：说“softmax 天然不会溢出”“所有 mask 都加一个 0/1 就行”“概率和为 1 所以 action 必须 softmax”“一次单测通过就兼容 fp16/所有设备”或“PyTorch fused kernel 就是我的原创实现”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-001 Knowledge](../knowledge/vol_08_code001_softmax.html)：max-shift、logsumexp、mask、dtype、梯度和测试矩阵。
2. [CODE-001 Source Freeze](../sources/vol_08_code001_softmax_source_freeze.html)：PyTorch softmax/log-softmax/CE/SDPA 官方 API 与项目边界。
3. PyTorch [`torch.softmax`](https://docs.pytorch.org/docs/stable/generated/torch.softmax.html)、[`log_softmax`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html) 与 [`CrossEntropyLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)。
4. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)。
