# VOL 08 CODE-VLA-002 原子手撕题卡：Scaled Dot-Product Attention

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-002`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-002 Knowledge](../knowledge/vol_08_code002_attention.html)；来源边界见 [CODE-002 Source Freeze](../sources/vol_08_code002_attention_source_freeze.html)。

## 手写 scaled dot-product attention 并处理 mask/shape

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-002</b> · 请手写 scaled dot-product attention，并说明多头 shape、causal/padding mask、dropout 和测试。</summary>

**面试意图**：判断你能否把 Q/K/V shape、\(1/\sqrt{d_k}\)、mask 方向、不同 query/key 长度、dtype、dropout 和 VLA loss 边界落到可运行实现。

**30 秒回答**：先统一 Q/K/V 为 [B,H,L,D]，算 scores=QKᵀ/√D，沿 Lk 做 softmax；mask 在 softmax 前应用，causal 只屏蔽未来，训练才 dropout。测试 Lq≠Lk、padding、fp16 和梯度 parity。

**机制展开（约 2 分钟）**：实现时只在最后两维做 matmul，score 为 [B,H,Lq,Lk]，softmax 沿 key 维；bool/additive mask 的 True 语义先定，Lq≠Lk 不能写死方阵。fp16/bf16 可在 fp32 算 score/softmax 后 cast；全 masked 行要 reject/invalid，避免 NaN；dropout 只在 train。用手算、多头、causal future、padding、不同长度、极值、autograd/SDPA parity 验证。attention mask 决定可见性，loss mask 决定监督，continuous action 不需 softmax。

**诊断 / 证据**：白板先标注每个 tensor 的 `[B,H,L,D]`，再验证 `Q @ K.transpose(-2,-1)`、scale、mask broadcast、softmax axis 和 `A @ V`。测试 square 与 `Lq≠Lk`、单头手算、多头 merge、future blocking、padding、train/eval dropout、fp16/bf16 finite、all-masked row、autograd 与 PyTorch SDPA tolerance。记录 device、dtype、dropout seed 和 backend；forward 通过不等于 fused kernel 性能通过。

**项目挂钩**：OpenPiVLA 可连接 causal-CE、eager attention 与 action packaging；OPD 可连接 token/format scorer；WAM/UWM 可连接 condition/mask/routing。安全表达是“我能实现并测试 attention 合同”，不把上游 SDPA/FlashAttention 或局部项目代码写成个人原创或性能 uplift。

**追问树**：为什么除以 √D？softmax 沿哪个维度？`Lq≠Lk` 怎么做 causal mask？bool mask 的 True 是 allow 还是 deny？全 masked 行如何处理？dropout 在 eval 是否关闭？attention mask 与 loss mask 有何区别？continuous action 为什么不用 softmax？

**易错点**：Q/K/V 轴顺序错；沿 query 而非 key 维 softmax；把不同长度写成方阵；causal 方向反；mask 广播到错 head/batch；eval 仍 dropout；把 forward parity 当作 latency 或真机收益。

**危险答案**：说“attention 天然是 O(L)”“mask 加 0/1 就够”“True 的语义所有框架都一样”“FlashAttention 一定等价且更快”或“attention mask 正确就说明 action loss/项目闭环正确”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-002 Knowledge](../knowledge/vol_08_code002_attention.html)：shape、scale、mask、dropout、dtype、复杂度与测试矩阵。
2. [CODE-002 Source Freeze](../sources/vol_08_code002_attention_source_freeze.html)：PyTorch SDPA/MHA、Transformer paper 与 VLA boundary。
3. PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) 与 [`MultiheadAttention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html)。
4. Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762)。
