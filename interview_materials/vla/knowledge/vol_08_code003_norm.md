# VOL 08 CODE-003：LayerNorm / RMSNorm 手写与调试

> 状态：`drafted / CODE-VLA-003 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-003 Source Freeze](../sources/vol_08_code003_norm_source_freeze.html)。

## 问题（Question）

手撕 LayerNorm/RMSNorm 的高频坑是：沿错维度、误用 BatchNorm 的 running statistics、忽略低精度累加、epsilon 位置错、affine shape 错，以及把 RMSNorm 简化成“LayerNorm 去掉 bias”。

## 1. 公式与区别

LayerNorm：

\[
\mu=\frac1D\sum_i x_i,\quad
\sigma^2=\frac1D\sum_i(x_i-\mu)^2,\quad
y_i=\gamma_i\frac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta_i.
\]

RMSNorm：

\[
r=\sqrt{\frac1D\sum_i x_i^2+\epsilon},\quad
y_i=\gamma_i\frac{x_i}{r}.
\]

LayerNorm 同时 re-center 和 re-scale；RMSNorm 不减均值，只按 root mean square 缩放。RMSNorm 通常只有 scale，但具体 API 是否允许 bias 要看实现，不能从名称猜测。

## 2. 归一化轴

对 `[B,L,D]`，Transformer 常沿最后 `D` 归一化：每个 batch、每个 token 独立计算统计量。`normalized_shape=(H,W,C)` 时，则沿末尾三维计算。实现应把 axis 写成 `tuple(range(x.ndim-len(shape), x.ndim))`，而不是写死 `dim=-1` 后假装支持多维。

## 3. 手写实现

```python
def layer_norm(x, weight=None, bias=None, eps=1e-5, normalized_ndim=1):
    # Accumulate statistics in fp32 for fp16/bf16 inputs.
    work = x.float() if x.dtype in (torch.float16, torch.bfloat16) else x
    dims = tuple(range(work.ndim - normalized_ndim, work.ndim))
    mean = work.mean(dim=dims, keepdim=True)
    var = (work - mean).pow(2).mean(dim=dims, keepdim=True)
    y = (work - mean) * torch.rsqrt(var + eps)
    if weight is not None:
        y = y * weight
    if bias is not None:
        y = y + bias
    return y.to(dtype=x.dtype)

def rms_norm(x, weight=None, eps=1e-6, normalized_ndim=1):
    # RMSNorm keeps the mean; it normalizes by mean-square only.
    work = x.float() if x.dtype in (torch.float16, torch.bfloat16) else x
    dims = tuple(range(work.ndim - normalized_ndim, work.ndim))
    inv_rms = torch.rsqrt(work.pow(2).mean(dim=dims, keepdim=True) + eps)
    y = work * inv_rms
    if weight is not None:
        y = y * weight
    return y.to(dtype=x.dtype)
```

`weight/bias` 的 shape 必须与 normalized shape 可广播；生产实现优先使用框架 kernel，手写版本用于解释合同和测试。

## 4. Epsilon 与 dtype

(epsilon) 应加在方差/均方的平方根之前，避免零方差除零。不同 API 默认 epsilon 可能不同，迁移 checkpoint 时必须随 config 冻结。fp16/bf16 直接算均值平方可能精度不足或溢出，常在 fp32 中累加；输出是否 cast 回原 dtype 取决于 kernel/API contract。

## 5. 训练与推理

LayerNorm/RMSNorm 使用当前样本/位置的末尾维统计，不维护 BatchNorm 式 running mean/variance，因此相同输入、相同参数、dropout 关闭时，train/eval 输出应一致。若输出不同，应先查外层 dropout、autocast、fused kernel、量化或模型状态，而不是为 norm 人为添加 running stats。

## 6. 测试矩阵

| 测试 | 断言 | 典型 bug |
| --- | --- | --- |
| `[B,L,D]` | 每个 token 独立归一化 | 沿 batch/sequence 统计 |
| multi-dim shape | 末尾多维统计与 affine 广播正确 | 写死 `dim=-1` |
| constant input | LayerNorm finite、中心化；RMSNorm finite | eps 位置错 |
| non-zero mean | LayerNorm 输出均值近零；RMSNorm 不保证 | 把两者写成同一公式 |
| fp16/bf16 | finite、与 fp32 对照受控 | 低精度统计不稳定 |
| affine on/off | weight/bias shape 与梯度正确 | broadcast 错 |
| train/eval | norm 自身一致 | 误加 running stats |
| autograd parity | 与 PyTorch forward/backward 接近 | variance/ddof/cast 错 |

LayerNorm 的 variance 通常使用 population variance（unbiased=False）；若手写成 sample variance，短维度时会明显偏差。

## 7. Transformer / VLA 映射

- pre-norm 将 norm 放在 attention/MLP 前，残差路径更直接；post-norm 放在残差相加后。不能脱离深度、初始化和学习率说绝对优劣。
- VLM/VLA backbone 常用 LayerNorm 或 RMSNorm；action expert、vision adapter 和 language backbone 可能 epsilon/dtype 不同。
- norm 解决特征尺度稳定性，不负责 action denormalization；训练用 feature norm 与机器人 action normalizer 是不同概念。
- 上游模型选择 RMSNorm 不等于用户项目完成了 norm ablation 或获得推理加速。

## 8. 项目挂钩与真实性边界

OpenPiVLA 的 Qwen backbone、LoRA/attention 兼容讨论可连接 RMSNorm/LayerNorm；UWM/WAM 的 DiT/transformer blocks 可连接 pre/post-norm 和 dtype；但当前没有本地 CODE-VLA-003 parity、profile 或 matched norm ablation。安全表达是“我能解释并实现 norm 合同”，不声称项目因更换 norm 获得 uplift。

## 9. 结论与下一步

LayerNorm 手写要减均值、按末尾 normalized shape 算 population variance、加 epsilon、affine；RMSNorm 不减均值，只按 mean-square 缩放。两者都不使用 running statistics。高分答案还应覆盖 fp32 累加、affine broadcast、train/eval parity、constant/non-zero-mean 测试和 VLA action normalizer 边界。

下一步：保持 `CODE-VLA-003` 题卡为 `unseen`，进行一次白板/实现练习，或补充 forward/backward parity artifact。

## References

1. [CODE-003 Source Freeze](../sources/vol_08_code003_norm_source_freeze.html)。
2. PyTorch [`LayerNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html) 与 [`RMSNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html)。
3. Zhang & Sennrich, [Root Mean Square Layer Normalization](https://arxiv.org/abs/1910.07467)。
4. 本仓库 [VOL 01 Foundations](vol_01_foundations.html)。
