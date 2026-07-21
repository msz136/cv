# VOL 05 Engineering / Evaluation：ENG-015 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-015`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-015 Activation Checkpointing / Offload](../knowledge/vol_05_engineering_eval_eng015.html)；没有 matched A/B 和 resume artifact 前，不把显存配置说成吞吐或恢复收益。

## Activation checkpointing、CPU/NVMe offload 与吞吐取舍

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-015</b> · 显存不够时，activation checkpointing、CPU/NVMe offload 怎么选？如何证明没有把显存收益换成不可接受的吞吐或恢复风险？</summary>

**面试意图**：判断你能否区分 activation 与 model state，理解重算/搬运代价，并设计 matched A/B 与 resume gate，而不是只背一个配置开关。

**30 秒回答**：先按账本区分 activation、state 和临时 buffer。checkpoint 用重算换显存；CPU/NVMe offload 搬 state，代价是 copy/I/O。固定 batch、world-size 和测量窗口，同测 peak、p95、parity、next-batch；当前项目只有 config/report，不能说收益。

**机制展开（约 2 分钟）**：checkpoint 不保存部分 activation，backward 重算；固定 RNG。FSDP CPU offload 搬参数/梯度，optimizer 在 CPU；ZeRO-Offload/Infinity 搬分片 state 到 CPU/NVMe。A/B 固定 batch、dtype、world-size、warm-up，测 peak、recompute/copy/I/O、p95、gradient parity 与 next-batch replay。UWM/OPD 只有 config/report，不能说吞吐或完整 resume。

**诊断 / 证据**：先输出显存时间线和 state ownership，再做 baseline/candidate 的 matched run；保存 profiler wait buckets、overflow/scaler、binary hash、optimizer/scheduler/RNG/sampler bundle 和固定下一批样本 ID。若只看到 peak GPU 下降，不能说明吞吐提升；若只 `load()` 成功，不能说明中途恢复正确。

**项目挂钩**：ENG-004..006 artifact gate 支持 UWM 的 DeepSpeed/effective config、normalizer、load report，以及 OPD 的 ZeRO-2/3 config 和 final-only/no-optimizer-state manifest；当前 snapshot 没有 checkpoint binary、matched throughput A/B 或 fixed-batch continuation。我会把项目回答落在显存/恢复合同设计与证据边界，而不是宣称 offload 已经优化。

**追问树**：为什么 activation checkpoint 不等于 CPU offload？FSDP CPU offload 的 optimizer 在哪里？NVMe offload 要测哪些 I/O 字段？如何固定 effective batch？为什么 `load()` 成功仍不代表 resume？如果显存降 30% 但 p95 step time 上升，是否接受？

**易错点**：把 activation、optimizer state、parameter state 混为一类；用不同 batch/world-size 做 A/B；把 DeepSpeed 文档的“支持 NVMe”写成当前项目已有 NVMe benchmark。

**危险答案**：说“checkpoint/offload 一定提速”“显存下降就代表吞吐提升”“保存成功就能无损续训”，或把 UWM/OPD 的配置文件写成已验证的性能结果。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-015 知识页](../knowledge/vol_05_engineering_eval_eng015.html)：显存账本、state/lifecycle 分类、matched A/B 与 resume gate。
2. [ENG-015 Source Freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html)：PyTorch 2.13 checkpoint/FSDP 与 DeepSpeed frozen commit。
3. [ENG-004..006 Local Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：UWM/OPD 配置、report、binary/resume/throughput 缺口。
4. [ENG-013 Reproducibility](../knowledge/vol_05_engineering_eval_eng013.html)：RNG、sampler cursor 与 fixed-next-batch replay 合同。
