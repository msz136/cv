# VOL 05 Engineering / Evaluation：ENG-017 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-017`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-017 Training Observability](../knowledge/vol_05_engineering_eval_eng017.html)；没有 per-step/per-rank trace、AMP event 和 first-failure replay 前，不把 summary/config 说成吞吐或稳定性证明。

## Loss、Grad、Data Wait、Comm 与 AMP Overflow 的训练可观测性

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-017</b> · 训练 loss 正常但吞吐下降、梯度异常或多卡变慢时，你如何设计可观测性？</summary>

**面试意图**：判断你能否把数值、数据、计算、通信和 lineage 事件拆开，并把 AMP skipped step、Profiler 开销和项目证据边界讲清楚。

**30 秒回答**：拆 numerical/data/compute/comm/lineage 五层；记录 loss/mask、grad norm、AMP scale/overflow/skipped step、data_wait、all-reduce 和 logging。事件带 step/rank/hash。当前缺 rank trace 与 A/B，不能声称吞吐或稳定性。

**机制展开（约 2 分钟）**：loss 记录 component/mask/reduction；grad 记录 pre/post clip、local/global norm；AMP 区分 unscale、scale、overflow、skipped step。timeline 拆 data_wait、forward/backward、all-reduce、optimizer、logging，用 Profiler 的 wait/warmup/active 短窗口。anomaly 只用于固定 trace 的 first failure。UWM/OPD 有 summary/profile hooks，但缺 per-rank trace、overflow 序列和 A/B，不能声称吞吐或稳定性。

**诊断 / 证据**：每条 event 保存 run/code/config/data hash、step、rank/world-size、monotonic timestamp、unit、sample/token count、finite、checkpoint/scaler/RNG/sampler 信息。连续 NaN 要保留第一条 request ID；连续 skipped step 要对齐 scale/rank/loss component；data_wait 突增要拆 worker/decode/collate/host→device；comm p95 要带 collective、bytes、bucket、wait/overlap。Profiler 与 anomaly 只做短窗口，并单独记录观测开销。

**项目挂钩**：ENG-004..006 gate 只支持 UWM/OPD 的 GradScaler、gradient accumulation、throughput/profile 配置；OPD inventory/report 有 train/OPD loss、overlap、route loss 等摘要。当前没有完整 overflow/grad-norm 时间序列、rank-level data_wait/comm trace、matched A/B 或 first-failure replay。我会把项目回答落在 observability schema 和诊断合同，而不是“已经优化吞吐”。

**追问树**：loss 为什么要带 mask/reduction？local norm 和 global norm 怎么区分？skipped optimizer step 是否计入吞吐？Profiler 的 wait/warmup/active 怎么选？data_wait 突增如何排查？DDP all-reduce 慢如何定位 rank/bucket？anomaly 为什么不能长期打开？

**易错点**：只记录 aggregate loss；把 scale 变化当成 overflow 根因；把单卡 wall-clock 当成 kernel/comm 时间；把 DeepSpeed config 或项目 summary 写成完整 telemetry。

**危险答案**：说“loss 下降说明训练稳定”“GPU 利用率低就是 DataLoader 慢”“多卡慢就是通信问题”，或把 profile run 的吞吐与未 profile baseline 直接比较。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-017 知识页](../knowledge/vol_05_engineering_eval_eng017.html)：五层 observability、AMP/grad、timeline、Profiler 与项目边界。
2. [ENG-017 Source Freeze](../sources/vol_05_eng017_training_observability_source_freeze.html)：PyTorch 2.13、DeepSpeed logging/profile 官方语义。
3. [ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：UWM/OPD 的 summary/config 与 telemetry 缺口。
4. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：loss/overlap/route summary 与 evidence boundary。

