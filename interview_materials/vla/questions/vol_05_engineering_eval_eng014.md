# VOL 05 Engineering / Evaluation：ENG-014 原子题卡

> 状态：`drafted / cards_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-014`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-014 Hardware / Operator Compatibility](../knowledge/vol_05_engineering_eval_eng014.html)；没有 backend/operator parity artifact 前，不把“能启动”说成“已兼容”。

## CUDA / MACA / ROCm 兼容性与算子验证

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ENG-014</b> · 为什么 `torch.cuda.is_available()` 或 `device='cuda'` 仍不能证明 VLA 已完成 MACA/ROCm 算子迁移？</summary>

**面试意图**：判断你能否把硬件迁移拆成 runtime、build、operator、communication、numerical/runtime 和 VLA workload/eval 六层，并把 eager/MACA 个人经历放在证据边界内。

**30 秒回答**：兼容性分六层：runtime、build、operator、通信、数值/同步、VLA 闭环。`torch.cuda` 复用或 MACA eager 能启动只证明一层；还要做 forward/backward、parity 和 2-rank smoke。无 custom-op、profiler、checkpoint→eval 证据，不说算子等价或性能提升。

**机制展开（约 2 分钟）**：先冻结 wheel/driver/SDK 与 device visibility，做 op 的 forward/backward、dtype/shape/layout 和 fallback 检查；再跑 process-group/all-reduce，最后在同步完成后比较 reference 输出、梯度与 p50/p95。HIP 复用 `torch.cuda` 降低 Python 改动，不等于 `.cu`、Triton、FlashAttention 自动可用；mcPytorch/mcTriton 仍需专用 compiler/SDK。OpenPiVLA 的 eager/MACA 目前只支持稳定性 call graph，不是性能 uplift。

**诊断 / 证据**：先保存 backend/framework/driver/SDK manifest 和固定输入，再记录 op matrix、compile log、forward/backward smoke、missing-kernel/fallback warning、同步方式、reference relative error、p50/p95、2-rank collective 与 checkpoint→parser→controller roundtrip。当前本地只有 eager call graph 和 public smoke，没有 custom-op matrix、profiler、formal checkpoint 或 roundtrip，因此项目口径降级为“迁移路径可诊断，兼容性尚未闭合”。

**项目挂钩**：OpenPiVLA Batch 2 证据冻结支持 local formal trainer 的 eager 参数、Qwen `outputs.loss` 和 `(B,15,72)` public smoke；不支持 MACA 性能优于 CUDA/flash、所有第三方 op 已适配或三后端闭环成功率等价。我会把贡献说成跨算力栈训练/诊断 contract 迁移，而不是硬件带来的算法提升。

**追问树**：为什么 HIP 复用 `torch.cuda` 仍要重编译 extension？为什么未同步 wall-clock 不可信？2-rank smoke 要验证什么？BF16/非 contiguous layout 为什么要单列？eager 能启动后下一条最小证据是什么？

**危险答案**：说“把 `cuda` 换成 `maca` 就完成迁移”“driver compatibility 就是算子 parity”“eager 比 flash 快”，或把单卡 forward smoke 当成训练、通信和闭环 eval 全部通过。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-014 知识页](../knowledge/vol_05_engineering_eval_eng014.html)：六层兼容合同、operator matrix、同步 parity 与 OpenPiVLA 证据边界。
2. [ENG-014 Source Freeze](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html)：PyTorch 2.13、ROCm 7.14.0、NVIDIA Compatibility、MetaX mcPytorch/mcTriton 的冻结来源。
3. [OpenPiVLA Batch 2 证据冻结](../sources/openpivla_batch2_evidence_freeze.html)：eager/MACA local call graph、smoke/formal/raw 证据阶梯与未闭合的 custom-op/profiler/roundtrip 缺口。
