# VOL 08 CODE-VLA-003 原子手撕题卡：LayerNorm / RMSNorm

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-003`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-003 Knowledge](../knowledge/vol_08_code003_norm.html)；来源边界见 [CODE-003 Source Freeze](../sources/vol_08_code003_norm_source_freeze.html)。

## 手写 LayerNorm / RMSNorm 并解释差异

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-003</b> · 请手写 LayerNorm 和 RMSNorm，并说明归一化轴、epsilon、低精度与训练/推理差异。</summary>

**面试意图**：判断你能否区分 re-centering/re-scaling、normalized shape、population variance、affine、epsilon、dtype 与 BatchNorm running statistics。

**30 秒回答**：LayerNorm 沿 normalized_shape 算均值/方差，减均值后乘 rsqrt(var+eps)，再做 γ/β；RMSNorm 不减均值，只除以 sqrt(mean(x²)+eps)，通常只有 γ。低精度用 fp32 统计；两者无 running stats，测试任意轴、constant 和 autograd parity。

**机制展开（约 2 分钟）**：对 [B,L,D] 逐 token 沿 D：LN 算 μ、population var，`(x-μ)*rsqrt(var+eps)*γ+β`；RMSNorm 为 `x*rsqrt(mean(x²)+eps)*γ`。多维 normalized_shape 沿末尾多轴，affine 可广播；低精度用 fp32 统计后 cast。两者无 running stats，train/eval 自身一致。用 constant、non-zero-mean、multi-dim、affine on/off、低精度和 PyTorch forward/backward parity 测试；feature norm 不等于 action normalizer。

**诊断 / 证据**：先写输入与 normalized shape，再列出归一化 dims、统计 dtype、epsilon、affine shape 和输出 dtype。测试 `[B,L,D]`、末尾多维、constant/zero/non-zero-mean、fp16/bf16、γ/β on/off、train/eval 和 autograd parity；LayerNorm 用 population variance。若项目换 norm，要固定 checkpoint/config/eps/dtype/residual layout 并做 matched ablation，不能只看单次 loss。

**项目挂钩**：OpenPiVLA 的 Qwen backbone 可连接 RMSNorm/LayerNorm、LoRA 与 attention 兼容；UWM/WAM 的 transformer/DiT block 可连接 pre/post-norm 和 dtype。安全表达是“我能实现并审计 norm 合同”，不把上游 norm 选择写成个人原创，也不把 feature norm 与 action normalizer 混为一谈。

**追问树**：为什么 RMSNorm 不减均值？LayerNorm variance 是否 unbiased？`normalized_shape=(H,W,C)` 沿哪些轴？epsilon 加在哪里？为什么不用 running mean？train/eval 为什么应一致？fp16 怎样处理？feature norm 与 action denormalization 有何区别？

**易错点**：沿 batch/sequence 维统计；把 sample variance 当 population variance；epsilon 放在 sqrt 外；把 RMSNorm 写成 LayerNorm 去 bias 但仍减均值；给 norm 加 running stats；affine 广播错；把上游 RMSNorm 说成个人优化。

**危险答案**：说“RMSNorm 就是没有 β 的 LayerNorm”“LayerNorm 训练和推理用不同 running mean”“normalized_shape 永远只有最后一维”“换 RMSNorm 一定更快更好”或“action normalizer 与 RMSNorm 是同一件事”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-003 Knowledge](../knowledge/vol_08_code003_norm.html)：公式、normalized shape、低精度、训练/推理与测试矩阵。
2. [CODE-003 Source Freeze](../sources/vol_08_code003_norm_source_freeze.html)：PyTorch LayerNorm/RMSNorm、RMSNorm paper 与项目边界。
3. PyTorch [`LayerNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)、[`RMSNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html) 与 [RMSNorm paper](https://arxiv.org/abs/1910.07467)。
