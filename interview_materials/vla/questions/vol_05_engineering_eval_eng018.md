# VOL 05 Engineering / Evaluation：ENG-018 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-018`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-018 Scheduler / Preemption / Retry](../knowledge/vol_05_engineering_eval_eng018.html)；来源边界见 [Source Freeze](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)。当前项目没有 binary、attempt ledger 或 preemption drill，不把 metadata 说成 exact resume。

## Scheduler 重试、抢占与幂等 checkpoint

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-018</b> · 训练被抢占或 worker 失败后，如何保证 retry 不读半写 checkpoint？</summary>

**面试意图**：判断你能否区分 logical run/attempt/rank，解释 SIGTERM 安全边界、`COMMITTED` generation、重复副作用与恢复证据。

**30 秒回答**：logical run 稳定，attempt 新建，rank 可变。checkpoint 写临时 generation，完整性与 load smoke 通过才 `COMMITTED`、更新 latest；SIGTERM 只置位，安全边界保存。retry 重复启动，用稳定 key 去重。当前无 binary/drill，不说 exact resume。

**机制展开（约 2 分钟）**：retry 是新 attempt；从同一 logical run 的 committed generation 恢复 optimizer、RNG、sampler。SIGTERM 记录 deadline，在 step 边界协调保存；超时标记 partial，不能更新 latest。多 rank shard 写临时目录，manifest-last、hash、load smoke 通过后原子 promote。eval/metrics/cache 用 step+checkpoint/protocol hash 去重；world-size 变化验证 reshard、batch、sample IDs。项目只有 metadata/final-only/path，不能证明 exact resume。

**诊断 / 证据**：记录 logical_run_id、attempt_id、worker_group、rank/world-size、restart count、signal/deadline、generation、manifest/hash、lost/replayed steps 和副作用 key。演练 SIGTERM 位于 micro step、optimizer step、checkpoint write 中间，以及 worker crash、duplicate attempt、storage failure、N→M world-size；通过条件是 last committed 不变、无 deadlock、next sample IDs 和 final promotion 可复核。

**项目挂钩**：UWM 有 save/load summary、normalizer 和 effective config；OPD 有 ZeRO 配置及 final-only/no-optimizer-state manifest；OpenPiVLA 有远端 checkpoint path 与 smoke/diagnostic。它们只能支持 metadata、weights-only 或路径引用边界，当前缺 checkpoint binary、attempt ledger、signal/retry trace、immutable load smoke 和 recovery matrix。我会把回答落在恢复合同与待补证据。

**追问树**：logical run 与 attempt 为什么分开？`COMMITTED` 何时写？SIGTERM 正好发生在 shard 写入中怎么办？retry 如何避免重复 eval？world-size 改变后如何证明 sample IDs？grace 不够写完 checkpoint 时如何降级？

**易错点**：把 `rank0/checkpoint.pt` 当永久 owner；直接覆盖 latest；只存 weights 却说 exact resume；把 Job 最终成功说成 exactly-once；忽略重复日志、cache 或 eval。

**危险答案**：说“scheduler 会自动恢复 optimizer/RNG”“目录存在就代表 checkpoint 完整”“TorchElastic 保证 rank 不变”或“重试次数多就一定能恢复”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-018 知识页](../knowledge/vol_05_engineering_eval_eng018.html)：identity、retry、preemption、checkpoint commit 与 recovery drills。
2. [ENG-018 Source Freeze](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)：PyTorch 2.13、Kubernetes 与 DeepSpeed 官方边界。
3. [ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：UWM/OPD 保存/load metadata 与 binary 缺口。
4. [OPD / OpenPiVLA evidence inventory](../evidence/projects/opd_claim_evidence_inventory.html)：项目证据边界与未核实项。
