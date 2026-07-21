# VOL 08 CODE-VLA-004 原子手撕题卡：Masked MSE / Huber Loss

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-004`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-004 Knowledge](../knowledge/vol_08_code004_masked_loss.html)；来源边界见 [CODE-004 Source Freeze](../sources/vol_08_code004_masked_loss_source_freeze.html)。

## 手写 masked MSE / Huber action loss

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-004</b> · 请手写带 mask 的 MSE/Huber loss，并说明 reduction、空 mask、低精度与测试。</summary>

**面试意图**：判断你能否处理 action padding、异构有效维、Huber delta、有效 denominator、分布式聚合和 VLA loss/mask 边界。

**30 秒回答**：先算 elementwise MSE/Huber，再乘 valid/action-dim mask，分母用有效权重和，不能 `mean(mask*loss)`。全零 mask 要 reject/skip；低精度用 fp32 累加。测试 padding 不变、delta/outlier、空 mask、分布式分母和梯度 parity。

**机制展开（约 2 分钟）**：误差 e=pred-target；MSE=e²，Huber 在 |e|≤δ 用 0.5e²，否则 δ(|e|-0.5δ)。把 mask/weight 广播到 [B,H,D]，loss=sum(wmℓ)/sum(wm)；分布式先 all-reduce numerator/denominator 再相除。全零 mask 不是正常零 loss，要 reject/skip；NaN/Inf 在乘 mask 前查。测试 mask=1 parity、不同 padding/有效维、delta 边界、outlier、fp16 和 autograd。attention mask、action valid mask、token CE 与 diffusion/flow target 要分开。

**诊断 / 证据**：记录 pred/target/mask/weight shape、normalized/physical space、delta、numerator、denominator、有效 timestep/dim 和 skip reason。验证 `mask=1` 与框架 parity、同有效元素不同 padding 的 loss 不变、全零 mask 触发显式分支、Huber 在 delta 处连续、outlier 梯度线性、fp16/bf16 finite。多 rank 必须聚合 numerator/denominator，而不是平均各 rank mean。

**项目挂钩**：OpenPiVLA 可连接 action chunk、valid dims、normalizer 与 causal-CE；UWM/WAM 可连接 action/video target mask、timestep weight 和多任务 reduction；OPD 可连接 metric-specific denominator。安全表达是“我能实现和审计 masked loss”，不声称更换 Huber 后项目成功率提升。

**追问树**：为什么 `mean(mask*loss)` 错？全零 mask 返回零可以吗？Huber 与 SmoothL1 的 scale 有何区别？delta 在 normalized 还是 physical space？不同 action dim 如何公平聚合？分布式为何先聚合 numerator/denominator？attention mask 是否能直接当 loss mask？

**易错点**：padding 进入分母；全零 mask 伪装成低 loss；`0*NaN` 仍传播 NaN；Huber delta/系数错；把 task weight 当二值 valid mask；先 rank mean 再平均；把 token CE、diffusion target 和 action MSE 混成同一 loss。

**危险答案**：说“乘 mask 后直接 mean 即可”“空 mask 返回 0 最稳定”“Huber 一定优于 MSE”“所有任务按有效元素 micro-average 就公平”或“loss 降低证明机器人成功率提升”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-004 Knowledge](../knowledge/vol_08_code004_masked_loss.html)：MSE/Huber、masked denominator、empty mask、weighting 与测试矩阵。
2. [CODE-004 Source Freeze](../sources/vol_08_code004_masked_loss_source_freeze.html)：PyTorch losses 与 VLA mask/reduction 边界。
3. PyTorch [`MSELoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)、[`HuberLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html) 与 [`SmoothL1Loss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.SmoothL1Loss.html)。
