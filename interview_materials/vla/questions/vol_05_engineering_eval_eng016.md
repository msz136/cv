# VOL 05 Engineering / Evaluation：ENG-016 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-016`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-016 Student + Multiple Teachers](../knowledge/vol_05_engineering_eval_eng016.html)；没有 single-teacher A/B、teacher/student lineage 和 memory telemetry 前，不把五教师配置说成收益。

## Student + Multiple Teachers 的显存与调度

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ENG-016</b> · student 同时使用多个 teacher 做蒸馏时，如何安排显存、KL loss 和调度？</summary>

**面试意图**：判断你能否同时讲清 teacher freeze/no-grad、KL 的方向与 mask、多教师 schedule 的 memory/latency trade-off，以及 OPD 证据的因果边界。

**30 秒回答**：冻结 teacher，只训练 student，并用 no_grad 做 teacher forward；固定 KL 的方向、T、reduction 和 mask。比较常驻/顺序/CPU-NVMe schedule，固定 batch/world-size 测 peak、p95 和 replay。OPD 有五教师链路，但无单教师对照，不能归因收益。

**机制展开（约 2 分钟）**：teacher 不进 optimizer，forward 用 no_grad；detach 不能替代。KL 固定 student log-prob、teacher prob、T、reduction、valid mask；多教师按 route/weight 聚合。常驻 peak 高但少 reload，顺序 peak 低但 latency 累加，CPU/NVMe 还要计 copy/I/O。OPD 的 preloaded_zero3、coldstart KL、student-rollout→teacher-KL 是 local hook，不等于 learned router/uplift；需 single-teacher A/B 与 checkpoint/RNG/sampler replay。

**诊断 / 证据**：保存 teacher/student revision、`requires_grad`/`no_grad` 检查、route/weight distribution、temperature、KL reduction、valid-token mask、teacher forward ms、peak GPU/CPU/NVMe、copy/I/O wait、student grad norm、overflow/scaler 与下一批 sample IDs。若只看 aggregate loss，无法发现 route drift、padding 污染或 teacher 顺序造成的 latency。

**项目挂钩**：OPD inventory 支持五 expert mix、route metadata、coldstart 的五教师 `preloaded_zero3`/full-vocab KL，以及 student rollout 后的 route-based teacher forward/KL；当前实现不是独立验证的 learned router，也缺 single-teacher、SFT-only、no-synthetic、synthetic-ratio ablation 和完整 weights/optimizer bundle。我会把回答落在训练链路与 evidence gate，而不是“多教师带来全部 uplift”。

**追问树**：只 `detach` 为什么不够？KL 的 input/target/reduction 怎么定义？常驻与顺序 schedule 的峰值分别在哪？CPU/NVMe staging 要测什么？route metadata 为什么不是 learned router？怎样做 single-teacher/multi-teacher matched A/B？

**易错点**：把 `requires_grad=False` 当成不占显存；把 `no_grad` 当成自动 offload；混淆 KL 方向或 `mean`/`batchmean`；把五教师链路写成多教师因果 uplift。

**危险答案**：说“teacher 不反向就没有显存成本”“多教师一定比单教师好”“route 字段就是 learned router”，或把 OPD 的组合结果归因给 teacher 数量一个因素。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-016 知识页](../knowledge/vol_05_engineering_eval_eng016.html)：teacher graph、KL、schedule、memory/latency A/B 与 OPD 边界。
2. [ENG-016 Source Freeze](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)：Hinton、PyTorch 2.13、DeepSpeed ZeRO-3 官方语义。
3. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：五教师 route、coldstart、online KL 与缺失 ablation/lineage。
4. [ENG-015 Memory/Offload](../knowledge/vol_05_engineering_eval_eng015.html)：CPU/NVMe state ownership、matched A/B 与 replay 合同。

