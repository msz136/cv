# VOL 05 Engineering / Evaluation：ENG-013 原子题卡

> 状态：`drafted / cards_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-013`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-013 Reproducibility](../knowledge/vol_05_engineering_eval_eng013.html)；没有 replay artifact 前，不能把 checkpoint load 说成精确续训。

## Seed、Sampler Cursor 与 Resume

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-013</b> · 为什么 `seed=42` 仍不能证明 VLA 训练可精确续训？</summary>

**面试意图**：判断你能否区分随机源控制、实验复现和 mid-epoch sampler cursor 恢复，并识别 distributed data order 的高危缺口。

**30 秒回答**：seed 只初始化部分 RNG。实验复现还需冻结代码、数据、环境、worker/sampler policy、共同 seed 与 `set_epoch`，并保存 CPU/CUDA/Python/NumPy 状态；中途续训还需 cursor、next IDs 和 replay smoke。checkpoint 能加载不等于精确 resume。

**机制展开（约 2 分钟）**：我先分三层：固定 seed、实验 replay、精确中途续训。PyTorch DistributedSampler 要求 dataset size/order 稳定，各 rank 共享 seed，并在每个 epoch 创建 iterator 前调用 `set_epoch`；否则可能重复相同 ordering。CPU/CUDA/Python/NumPy/worker RNG 要分层保存。中途恢复受 `drop_last`、dynamic batch、过滤样本、worker prefetch 和 retry 影响，不能用 `step_in_epoch` 代替 cursor；应保存/重放 next sample IDs，并做一小步 loss/optimizer/scaler smoke。

**诊断 / 证据**：先做 epoch-boundary save/load，再做固定 request trace 的 mid-epoch save/load；比较 next sample IDs、augmentation/RNG、loss、optimizer step 和 scaler state。仅 `load_state_dict` 成功、最终 loss 接近或报告写着 resume，不足以关闭证据门。

**项目挂钩**：ENG-004..006 artifact gate 只有训练 summary、load report、normalizer、ZeRO 配置和 final-only manifest，没有 per-rank RNG、sampler cursor 或 next-sample replay。因此我会说“恢复合同已定义、精确续训证据缺失”，不会声称个人项目已经 exact resume。

**追问树**：`set_epoch` 忘了会怎样？为什么保存 CPU RNG 不够？dynamic batching 如何影响 cursor？epoch-boundary resume 与 mid-epoch 有何取舍？怎样设计 fixed request trace？

**危险答案**：说“固定 seed 就完全复现”，或把 DistributedSampler 当成自动保存 cursor、把 checkpoint 可加载当成精确续训。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-013 知识页](../knowledge/vol_05_engineering_eval_eng013.html)：seed ownership、DistributedSampler、RNG state、resume contract 与 replay smoke。
2. [ENG-013 Source Freeze](../sources/vol_05_eng013_reproducibility_source_freeze.html)：PyTorch 2.13 / NumPy 1.26 官方语义与 normalized text fingerprints。
3. [VOL 05 ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：当前本地 checkpoint/load/normalizer/ZeRO 证据及 sampler/RNG/replay 缺口。
