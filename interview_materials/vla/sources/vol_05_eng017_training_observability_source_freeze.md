# VOL 05 ENG-017：训练可观测性（Loss / Grad / Data Wait / Comm / Overflow）来源冻结

> 审计日期：2026-07-17  
> 状态：`source_frozen / VLA-ENG-017_knowledge+card_drafted / WARN`  
> 对应问题：`VLA-ENG-017`——训练时如何把 loss、gradient、data_wait、communication、AMP overflow 记录成可定位的观测系统？  
> 当前边界：本文件冻结官方 API/配置语义和本地日志证据边界；ENG-017 知识正文与一张 `unseen` 题卡已生成，跨 run telemetry、性能因果与个人指标结论仍后置。

## 1. 问题与最小范围（Question / Scope）

本切片只回答五个问题：

1. loss 下降、gradient norm、AMP scale/overflow、skipped step 各自说明什么，不能说明什么？
2. 如何把 `data_wait`、forward/backward、optimizer、all-reduce/communication 和 checkpoint/eval callback 拆成同一条 step timeline？
3. PyTorch Profiler、autograd anomaly、DeepSpeed `steps_per_print`/`wall_clock_breakdown` 的官方语义边界是什么？
4. 如何区分“模型数值异常”“数据等待”“通信瓶颈”“日志/观测开销”？
5. 结合 UWM/OPD 本地材料，哪些日志字段已经存在，哪些仍缺时间序列或 rank-level trace？

本页不声称任何项目已经完成端到端 profiler、通信占比分析、AMP 稳定性证明或吞吐提升；单个 loss、单次 profile 或 config 字段都不能替代 matched run telemetry。

## 2. 证据类型与冻结输入

| 输入 | 类型 | 版本 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| PyTorch AMP | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | autocast/GradScaler 的模块关系、unscale-before-step、scale 与 NaN/overflow 边界 | 某模型在 FP16/BF16 下稳定、没有 skipped step 或性能收益 |
| PyTorch Profiler | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | CPU/CUDA activities、schedule 的 wait/warmup/active、trace 与 record function | 当前后端、CUPTI、分布式 trace 已完整可用 |
| PyTorch Autograd anomaly | primary / official-doc | PyTorch 2.13 `autograd.html`；访问 2026-07-17 | forward traceback、backward NaN 检测、debug-only 语义 | 长期打开 anomaly 不影响性能或能定位所有数据问题 |
| PyTorch DDP | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | gradient all-reduce、输入切分不自动发生、rank/collective 语义 | 某 workload 的通信占比、overlap 或 NCCL/RCCL/MCCL 性能 |
| PyTorch `clip_grad_norm_` | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | 返回 total norm、`error_if_nonfinite` 与 clipping 观测点 | 分片模型下该值自动等于全局 norm，或 clipping 已解决 overflow |
| PyTorch DataLoader | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | worker/prefetch/iterator 语义，data wait 作为工程测量层 | 当前 UWM stall 的根因、任何 storage 格式的性能结论 |
| DeepSpeed config JSON | official-doc | 官方 rolling page；访问 2026-07-17 | `steps_per_print` 中的 skipped updates/lr/momentum 报告，`wall_clock_breakdown` 的 forward/backward/update timing 开关 | 某项目已启用、各 rank trace 完整、吞吐提升或通信已重叠 |
| 本地训练/项目材料 | local-evidence | 本仓库 VOL 05 knowledge、ENG-004..006 gate、OPD inventory | UWM GradScaler/throughput/profile 配置，OPD grad norm/entropy/overlap/route loss 摘要 | 完整 overflow/scale/grad-norm 时间序列、rank-level data_wait/comm trace、matched A/B |

### 2.1 官方来源 normalized text 指纹

HTML 来源按仓库统一规则：移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256。DeepSpeed 配置页是官方 rolling page，保存访问日期与 normalized 指纹，不把它当 immutable commit。

| 来源 | URL | normalized text 长度 | SHA-256 |
| --- | --- | ---: | --- |
| PyTorch AMP | [2.13/amp.html](https://docs.pytorch.org/docs/2.13/amp.html) | 23456 | `e423f9ca8f768cdc0494e1b3652a4757bb9a1a3b0600f8bdfd3780a3eeb94f5e` |
| PyTorch Profiler | [2.13/profiler.html](https://docs.pytorch.org/docs/2.13/profiler.html) | 15300 | `f02305bb5e26cd24d06567680950308cea7baeeadd33d22a6a07d64ea11aa67a` |
| PyTorch Autograd | [2.13/autograd.html](https://docs.pytorch.org/docs/2.13/autograd.html) | 40582 | `b4e2275427dc0a9d8d5cbb20742dbccbc7d2ba0e5b6788129490446c7f471b79` |
| PyTorch DDP | [2.13/DistributedDataParallel.html](https://docs.pytorch.org/docs/2.13/generated/torch.nn.parallel.DistributedDataParallel.html) | 25763 | `5b3910138fdec51f70a297d612318938cb73c601856057d27e6d24acd6b57d53` |
| PyTorch `clip_grad_norm_` | [2.13/clip_grad_norm_.html](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.clip_grad_norm_.html) | 2228 | `c8645bb903b85b055290893f27e0863469fdc9133479f6af0f3e8894dee265af` |
| PyTorch DataLoader | [2.13/data.html](https://docs.pytorch.org/docs/2.13/data.html) | 47667 | `9032517582f5a20a811008e4f71a81e356d058380cfc985b552ef338b1cecf5f` |
| DeepSpeed config JSON | [config-json](https://www.deepspeed.ai/docs/config-json/) | 76125 | `9ecae0433d4ca3168cee7d3939c9ef5492f05df358566a17cc32ec8fad07eab3` |

## 3. 可观测性不是“多打几个 print”：五层事件合同

| 层 | 每 step/每窗口记录 | 主要问题 | 不能替代 |
| --- | --- | --- | --- |
| numerical | loss finite、per-task loss、grad norm、clip ratio、AMP scale、overflow/skipped step、lr | 数值是否在更新、哪一项先异常？ | online task success |
| input/data | request/sample IDs、decode/collate、`data_wait_ms`、host→device、queue depth | GPU 是否在等数据？ | 仅凭 CPU 利用率判根因 |
| compute | forward/backward/optimizer、peak memory、kernel/record_function | 模型计算花了多久？ | 未同步 wall-clock |
| distributed | rank/world-size、all-reduce/all-gather/reduce-scatter、comm wait/overlap、collective error | 哪个 rank/collective 拖慢？ | 单卡 profile |
| lifecycle/record | code/config/data/normalizer hash、step、epoch、checkpoint、scaler/RNG/sampler | 这条指标能否重放和归属？ | 无 lineage 的曲线截图 |

观测系统的第一原则是**事件有 owner 和时间基准**：每行至少包含 `run_id`、`step`、`rank`、`wall_time`、`monotonic_elapsed`、`event`、`value`、`unit`、`config_hash`。否则把不同 run、不同 rank 或不同 effective batch 的曲线拼在一起会制造假因果。

## 4. Loss、grad、AMP overflow：三种不同的异常

### 4.1 Loss 不是策略成功率

训练 loss 是优化目标在当前 batch/mask/reduction 上的数值；必须同时报告 loss component、有效 token/sample 数、数据 split 和 reduction。VLA 中 action/format/aux loss 可能有不同 mask，不能只报 aggregate loss。loss 下降也不能证明 parser、controller 或 closed-loop success。

### 4.2 Gradient norm 与 clipping

PyTorch `clip_grad_norm_` 文档把返回值定义为所有参数梯度的 total norm，并提供 `error_if_nonfinite` 检查。对 FSDP/ZeRO，记录字段必须写清楚是 local shard norm、框架 global norm 还是 clipping 前后的哪一个时刻；不能默认单卡 API 返回的数就是全局值。

建议最小记录：`grad_norm_pre_clip`、`clip_threshold`、`clip_ratio`、`grad_norm_post_clip`、参数/模块名或 bucket、finite flag。若只记录“clip=1.0”，无法判断是否每步都在裁剪。

### 4.3 AMP scale / overflow / skipped step

PyTorch AMP 文档说明 gradient scaling 先放大 loss/backward 的梯度，optimizer 更新前要 unscale；FP16 可能 overflow，`GradScaler` 的 scale 也不保证始终大于 1。DeepSpeed config 文档还说明 `steps_per_print` 报告可能包含因 mixed-precision overflow 而 skipped 的 optimizer updates。

因此要把以下事件分开：

- `micro_step` 是否完成 backward；
- `optimizer_step` 是否真正执行；
- `overflow/finite` 是哪个 rank/哪个 loss component 触发；
- `scale_before/scale_after`、backoff/growth 和连续 skipped 次数；
- scheduler 是按 optimizer step 还是 micro step 前进。

“loss 没有 NaN”不等于没有 overflow；“scale 变化”也不等于已经找到根因。

## 5. Data wait、compute、communication 与同步

### 5.1 Step timeline

可把一个 optimizer step 拆为：

\[
T_{\mathrm{step}}=T_{\mathrm{data}}+T_{\mathrm{fwd}}+T_{\mathrm{bwd}}+T_{\mathrm{optim}}+T_{\mathrm{comm}}+T_{\mathrm{ckpt}}+T_{\mathrm{log}}+T_{\mathrm{sync}}
\]

其中 (T_{\mathrm{data}}) 包含 decode/collate/host→device，(T_{\mathrm{comm}}) 包含 all-reduce/all-gather/reduce-scatter 等 collective，(T_{\mathrm{log}}) 包含 telemetry 本身。它是工程分解，不是某个框架的自动报告；每段必须明确开始/结束事件和同步方式。

### 5.2 Profiler 的 wait/warmup/active

PyTorch Profiler 的 schedule 将记录周期拆为 wait、warmup、active，并可选择 CPU/CUDA activities；CUPTI 不可用时，CUDA trace 的粒度和 JSON 内容会受限。生产训练不应永久开启 full trace，而应使用短窗口、固定 rank、warmup 后采样，并把 profiler overhead 单独记录。

### 5.3 DDP communication

PyTorch DDP 官方语义是各 replica 间同步梯度，输入不会自动 shard；all-reduce 是梯度同步合同。它不告诉你某次训练中通信是否与 backward overlap、哪个 bucket/collective 最慢或网络是否饱和。需要 rank-level trace、collective name、duration、bytes、wait/overlap 和 error，不能从单卡 step time 推断。

## 6. Anomaly debug 与生产观测的边界

`torch.autograd.detect_anomaly(check_nan=True)` 会在 forward 开启记录，让 backward 出错时打印创建该 backward function 的 forward traceback，并在 backward 产生 NaN 时抛错。它是 debug 工具，应该在 tiny batch/短窗口复现，不应把长期启用 anomaly 当成免费 observability。

建议分两条路径：

1. **常规 telemetry**：轻量 scalar、rank summary、step timeline、sample IDs 和 checkpoint lineage。
2. **异常复现**：固定 request trace、开启 anomaly、保留 input/seed/config、限制 steps，并在复现后关闭高开销诊断。

这样可以区分“系统长期趋势”和“某个 batch 的第一处非有限值”，避免把所有训练都变成 debug mode。

## 7. 最小日志 schema 与告警规则

### 7.1 Scalar event schema

```text
run_id, code_sha, config_sha, data_sha, step, epoch, rank, world_size,
event, value, unit, sample_count, token_count, finite, route_or_task,
timestamp_wall, timestamp_mono, checkpoint_id, scaler_state, error_code
```

至少保留以下 event：

| event | unit | 触发频率 | 备注 |
| --- | --- | --- | --- |
| `loss/<component>` | scalar | step/window | 带 mask/effective count |
| `grad_norm_pre_clip` | L2 norm | optimizer step | 标注 local/global、clip 前后 |
| `amp/scale` | scalar | optimizer step | 与 overflow/skipped 配对 |
| `amp/overflow` | bool/count | optimizer step | rank、loss component、连续次数 |
| `time/data_wait` | ms | step/window | DataLoader/host→device 分开更好 |
| `time/comm` | ms | step/window/rank | collective/bytes/wait/overlap |
| `time/compute` | ms | step/window | forward/backward/optimizer 分开 |
| `memory/peak_gpu` | bytes | sampled window | allocator、rank、teacher/state owner |

### 7.2 告警不是结论

- 连续非有限 loss/grad：停止或降级到 anomaly replay；不要只自动重启并丢失第一条样本。
- 连续 skipped optimizer steps：记录 scale、rank、loss component 和 input IDs，再决定降低 scale/dtype 或回滚。
- `data_wait / step` 突增：先对齐 worker、storage、queue 和 host→device，再谈模型变慢。
- 单 rank comm p95 显著偏高：检查 rank skew、bucket、collective bytes 和网络，而不是平均全局吞吐。
- logging/profiler 时间占比上升：降低采样频率或缩短 active window；观测开销本身必须进入账本。

## 8. 本地项目证据与真实性边界

本仓库既有材料支持：

- UWM/OPD 的配置和 summary 中有 GradScaler、gradient accumulation、throughput/profile 配置；ENG-004..006 artifact gate 明确指出尚缺 overflow/scale/grad-norm/clip-ratio 时间序列、fixed-effective-batch A/B 和 rank-level trace。
- OPD inventory/report 直接包含 `train_loss`、`last_opd_loss`、`last_opd_topk_overlap`，以及项目页所述的 grad norm、entropy、overlap、route loss 观测 hook；这些是 summary/route 证据，不自动等于优化稳定性或任务成功。
- OpenPiVLA 当前最强证据仍是 formal trainer、smoke、diagnostic/report 和 eager/MACA call graph；没有完整 per-step telemetry、formal checkpoint bundle 或跨 backend matched profiler。

安全回答：

> “我会把观测拆成 numerical、data、compute、distributed 和 lineage 五层。先记录 loss component、mask count、grad norm、AMP scale/overflow/skipped step，再用 profiler/同步计时拆 data_wait、forward/backward、all-reduce、optimizer 和 logging。当前项目有 summary 和部分 loss/overlap/profile hook，但没有完整 rank-level trace、overflow 时间序列或 matched A/B，所以我把它称为可观测性合同，而不是已经证明了吞吐或稳定性。”

| 口径 | 证据等级 | 面试安全表达 |
| --- | --- | --- |
| DeepSpeed `steps_per_print` / `wall_clock_breakdown` 语义 | official-doc | 配置/报告字段的含义 |
| UWM GradScaler/throughput/profile 配置 | local-direct metadata | 存在观测入口，缺时间序列 |
| OPD loss/overlap/route summary | local-direct/report-supported | 有 summary 指标，不等于稳定性因果 |
| communication 占比、overflow 根因、吞吐提升 | unverified | 需要 rank trace、AMP event 和 matched A/B |

## 9. Gate、风险与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| loss/grad/clipping | `PASS WITH WARNING` | 固定 component、mask、pre/post-clip 和 local/global norm |
| AMP overflow/scale | `PASS WITH WARNING` | 记录 scaler、finite、skipped optimizer step 和 rank/error code |
| profiler/timeline | `PASS WITH WARNING` | 使用 wait/warmup/active 短窗口，并记录 profiler overhead |
| data_wait/comm | `PASS WITH WARNING` | 设计 rank-level event schema；不从单卡或平均值推断 |
| local project observability | `WARN` | 补 per-step/rank trace、overflow series、matched A/B 和 first-failure replay |
| knowledge/card | `DRAFTED / UNSEEN` | 保持题卡 `unseen`；后续补 rank trace、AMP event、matched A/B 与 first-failure replay；ENG-018 后置 |

## 参考来源（References）

1. PyTorch 2.13，[Automatic Mixed Precision](https://docs.pytorch.org/docs/2.13/amp.html)：autocast、GradScaler、unscale 与 overflow/scale 边界。
2. PyTorch 2.13，[Profiler](https://docs.pytorch.org/docs/2.13/profiler.html)：activities、schedule、wait/warmup/active、CUPTI 边界。
3. PyTorch 2.13，[Autograd anomaly detection](https://docs.pytorch.org/docs/2.13/autograd.html)：forward traceback 与 backward NaN 检查。
4. PyTorch 2.13，[DistributedDataParallel](https://docs.pytorch.org/docs/2.13/generated/torch.nn.parallel.DistributedDataParallel.html)：gradient all-reduce 与 input-sharding 边界。
5. PyTorch 2.13，[`clip_grad_norm_`](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.clip_grad_norm_.html)：total norm 与 non-finite 检查。
6. PyTorch 2.13，[DataLoader](https://docs.pytorch.org/docs/2.13/data.html)：worker/prefetch/iterator 语义。
7. DeepSpeed，[Config JSON](https://www.deepspeed.ai/docs/config-json/)：`steps_per_print`、skipped updates 与 `wall_clock_breakdown`。
8. 本仓库，[VOL 05 Batch 1 knowledge](../knowledge/vol_05_engineering_eval.html)、[ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html) 与 [OPD evidence inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
