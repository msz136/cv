# VOL 05 Engineering / Evaluation：训练可观测性（ENG-017）

> 状态：`drafted / knowledge_19_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-017`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-017 Training Observability Source Freeze](../sources/vol_05_eng017_training_observability_source_freeze.html)。  
> 核心边界：loss、grad、AMP overflow、data wait、communication 和 lineage 是不同事件层；summary/config 不能替代 per-step/per-rank trace、matched A/B 或 first-failure replay。

## 问题（Question）

`VLA-ENG-017`：训练 loss 看起来正常但吞吐下降、梯度爆炸或多卡变慢时，如何设计可观测性系统定位第一处故障？

回答不能只说“加 TensorBoard”。要明确：

1. 记录哪些数值、时间和 lineage 字段；
2. 每个字段由哪个 rank/step/event owner 产生；
3. 如何用同步计时、Profiler、AMP 状态和 request trace 复现；
4. 哪些本地项目材料只是 summary/config，不能升级成稳定性或性能结论。

## 知识地图位置与前置依赖

```text
ENG-003 data/compute timing + ENG-005 AMP/grad
                 ↓
numerical / data / compute / distributed / lifecycle events
                 ↓
Profiler + first-failure replay + alert policy
                 ↓
checkpoint lineage、closed-loop eval 与 incident review
```

前置：

- `VLA-ENG-003`：DataLoader、host→device、GPU 和同步时间。
- `VLA-ENG-005`：AMP、effective batch、gradient clipping 和 overflow。
- `VLA-ENG-006/013`：checkpoint、RNG、sampler cursor 与 replay。
- `VLA-ENG-015/016`：offload、多教师 schedule 与 memory/latency 账本。

## 1. 短答：五层事件合同

**30 秒回答**：我把观测拆成 numerical、data、compute、distributed、lifecycle 五层：记录 loss component/mask、grad norm/clip、AMP scale/overflow/skipped step，再同步拆 data_wait、forward/backward、all-reduce、optimizer、checkpoint 和 logging。每条事件带 run/step/rank/config/data hash。当前 UWM/OPD 有部分 summary 和 profile hook，但没有完整 rank trace、overflow 时间序列或 matched A/B，不能声称吞吐或稳定性结论。

## 2. 直觉：给训练装五个仪表盘

- **numerical 仪表盘**：模型有没有产生 finite loss/gradient，是否一直被 clipping 或跳过 optimizer step？
- **data 仪表盘**：GPU 是在计算，还是在等 decode、collate、host→device 或 queue？
- **compute 仪表盘**：forward/backward/optimizer 各自耗时多少，peak memory 是否变化？
- **distributed 仪表盘**：哪一个 rank、bucket 或 collective 在等，通信是否和计算 overlap？
- **lifecycle 仪表盘**：这条曲线来自哪个 code/data/config/checkpoint，能否用固定 request trace 重放？

一条曲线如果没有 `run_id`、`step`、`rank`、单位和 config/data hash，就无法证明两个 run 可比。

## 3. 五层观测字段

| 层 | 最小字段 | 第一处故障问题 | 不能替代 |
| --- | --- | --- | --- |
| numerical | loss component、有效 token/sample、finite、grad norm、clip ratio、AMP scale、overflow/skipped step、lr | 优化是否真的更新，哪一项先异常？ | online success |
| data | sample/request ID、decode/collate、`data_wait_ms`、host→device、queue depth | GPU 是否在等输入？ | 仅看 CPU 利用率 |
| compute | forward/backward/optimizer、peak memory、Profiler range | 模型计算/内存哪里变慢？ | 未同步 wall-clock |
| distributed | rank/world-size、collective name、bytes、wait/overlap、错误码 | 哪个 rank/collective 拖慢？ | 单卡 profile |
| lifecycle | code/config/data/normalizer hash、checkpoint、scaler/RNG/sampler、event timestamp | 结果能否复现、归属和回滚？ | 无 lineage 的截图 |

每条 event 至少包含：

```text
run_id, code_sha, config_sha, data_sha, step, epoch, rank, world_size,
event, value, unit, sample_count, token_count, finite, route_or_task,
timestamp_wall, timestamp_mono, checkpoint_id, scaler_state, error_code
```

`timestamp_mono` 用来做同一进程内的 elapsed time；`timestamp_wall` 方便跨机器关联。两者都要保留，不能只依赖 wall clock。

## 4. Loss、gradient 与 clipping

### 4.1 Loss component 和 mask

VLA 的 aggregate loss 可能混合 action、文本、format、aux 或 route loss。每个 component 都要写：mask 定义、有效元素数量、reduction、dtype 和 data split。可用一个通用形式表示：

\[
L=\frac{\sum_i m_i\,\ell_i}{\max(\sum_i m_i,1)}
\]

其中 (m_i) 是有效 token/step/dimension mask，(ell_i) 是逐元素 loss。这个公式不是某个框架的默认实现；它提醒面试时先问“分母和 mask 是什么”，否则不同 padding/route 的 loss 不可比。

### 4.2 Grad norm 不只记录一个数字

PyTorch `clip_grad_norm_` 返回 total gradient norm，并支持 `error_if_nonfinite`；但 DDP/FSDP/ZeRO 中要明确它是 local shard、框架 global norm，还是 clipping 前/后的值。建议记录：

- `grad_norm_pre_clip`、`grad_norm_post_clip`；
- clip threshold 和 `clip_ratio`；
- finite flag、模块/bucket owner；
- AMP unscale 是否已完成；
- optimizer step 是否实际执行。

如果每步都被裁剪，loss 下降也可能只是“更新被限制”；如果 norm 突然变为 NaN，要回到第一处非有限 input/operation，而不是直接增大 clip threshold。

## 5. AMP scale、overflow 与 skipped step

PyTorch AMP 文档说明 gradient scaling 先放大 loss/backward 的梯度，optimizer 更新前要 unscale；FP16 可能 overflow，GradScaler 的 scale 也不保证始终大于 1。DeepSpeed `steps_per_print` 文档把 skipped optimizer updates（可能由 mixed-precision overflow 触发）纳入进度报告。

所以应把以下事件分开记录：

| 事件 | 需要回答的问题 |
| --- | --- |
| `micro_step_finished` | backward 是否完成？ |
| `optimizer_step_executed` | 参数是否真的更新？ |
| `amp/overflow` | 哪个 rank/loss component 触发非有限？ |
| `amp/scale_before/after` | scale 如何 backoff/grow，连续 skipped 几次？ |
| `scheduler_step` | scheduler 按 micro step 还是 optimizer step 前进？ |

“loss 没有 NaN”不能证明没有 overflow；“scale 变化”也不能证明根因已找到。

## 6. Step timeline：data、compute、comm、logging 分开

一个 optimizer step 可先拆成：

\[
T_{\mathrm{step}}=T_{\mathrm{data}}+T_{\mathrm{fwd}}+T_{\mathrm{bwd}}+T_{\mathrm{optim}}+T_{\mathrm{comm}}+T_{\mathrm{ckpt}}+T_{\mathrm{log}}+T_{\mathrm{sync}}
\]

其中 (T_{\mathrm{data}}) 可继续拆 decode/collate/host→device，(T_{\mathrm{comm}}) 要带 collective 名称和 bytes；(T_{\mathrm{log}}) 是观测开销，必须计入而不能假设为零。每段需要明确开始/结束事件和同步方式；未同步 GPU wall-clock 只能算 enqueue 时间。

### 6.1 Data wait

DataLoader 的 worker/prefetch 语义只告诉你数据如何被取出，不自动告诉你 stall 根因。建议同时记录 `next(loader)` wait、decode、collate、host→device、queue depth、worker restart/error 和 sample ID。UWM 的 DataLoader-only stall smoke 可以作为 local clue，但不能直接归因某个 storage 格式或完整训练吞吐。

### 6.2 Communication

DDP 官方语义是 replica 间 gradient all-reduce，输入切分由用户负责。通信观测要按 rank/collective/bucket 记录 duration、bytes、wait、overlap 和 error；单卡 profile 或全局平均 step time 不能告诉你哪个 rank 拖慢了训练。

## 7. Profiler 与 anomaly detection 的正确使用

PyTorch Profiler 的 schedule 把窗口分成 wait、warmup、active，可选择 CPU/CUDA activities；CUPTI 不可用时 CUDA trace 内容会受限。生产训练建议短窗口采样：固定 rank、warmup 后 active、明确同步，并把 profiler overhead 单独记录。

`torch.autograd.detect_anomaly(check_nan=True)` 会保存 forward traceback，使 backward 出错时能定位创建该 function 的 forward，并在 backward NaN 时抛错。它适合 tiny batch/固定 request trace 的 first-failure replay，不适合长期全量开启。

建议路径：

1. 常规训练只保留轻量 scalar、rank summary、sample/lineage 字段。
2. 发现第一处非有限或 rank skew 后，冻结 request trace、seed、config、input 和 checkpoint。
3. 开启 anomaly/短 profiler window，重放少量 steps，保留 raw trace。
4. 修复后关闭高开销 debug，重新跑 matched smoke 和独立 eval。

## 8. 告警与归因矩阵

| 现象 | 第一检查 | 不要直接做 |
| --- | --- | --- |
| 连续 NaN/Inf loss 或 grad | input ID、loss component、AMP scale、rank、anomaly replay | 只调大 clip 或自动重启丢失首个样本 |
| skipped optimizer step 连续增加 | scale/overflow/finite、dtype、loss component | 把 skipped 当作普通 step 计入吞吐 |
| `data_wait/step` 突增 | worker、decode、queue、storage、host→device | 先归因模型变慢 |
| 单 rank comm p95 偏高 | collective、bytes、bucket、rank skew、overlap | 看平均值后说通信已优化 |
| profile 后吞吐下降 | profiler/logging overhead、active window | 把 profile run 与 baseline 直接比较 |
| loss 正常、闭环失败 | parser/denorm/controller/eval protocol | 继续只调学习率 |

## 9. 本地项目映射与真实性边界

本仓库既有证据支持：

- UWM/OPD 的配置和 summary 中出现 GradScaler、gradient accumulation、throughput/profile 配置；ENG-004..006 artifact gate 明确尚缺 overflow/scale/grad-norm/clip-ratio 时间序列、fixed-effective-batch A/B 和 rank-level trace。
- OPD inventory/report 有 `train_loss`、`last_opd_loss`、`last_opd_topk_overlap` 以及 grad norm、entropy、overlap、route loss 等 hook/summary；这能支持“有观测入口或摘要”，不能证明优化稳定性或任务成功。
- OpenPiVLA 有 formal trainer、smoke、diagnostic/report 和 eager/MACA call graph，但没有完整 per-step telemetry、formal checkpoint bundle 或 matched cross-backend profiler。

安全回答：

> “我会把训练监控拆成 numerical、data、compute、distributed 和 lineage 五层。loss 之外，我会记录 mask count、grad norm/clip、AMP scale/overflow/skipped step，再用同步计时和短 profiler 窗口拆 data_wait、forward/backward、all-reduce、optimizer、checkpoint 和 logging。当前项目有 summary 和部分 profile/loss hook，但没有完整 rank trace、overflow 时间序列或 matched A/B，所以我把它称为可观测性合同，而不是已经证明了吞吐或稳定性。”

| 口径 | 证据等级 | 面试安全表达 |
| --- | --- | --- |
| DeepSpeed `steps_per_print`/`wall_clock_breakdown` | official-doc | 字段的官方语义 |
| UWM GradScaler/throughput/profile 配置 | local-direct metadata | 存在观测入口，缺时间序列 |
| OPD loss/overlap/route summary | local-direct/report-supported | 有摘要指标，不等于稳定性因果 |
| communication 占比、overflow 根因、吞吐提升 | unverified | 需要 rank trace、AMP event、matched A/B |

## 10. 验证伪代码（工程合同，不是 upstream 实现）

```python
def train_step_with_observability(batch, model, optimizer, scaler, profiler):
    # 1. Start a monotonic step span and record request/config lineage.
    step = start_event("step", batch.request_ids, rank=dist.get_rank())

    # 2. Measure data wait separately from model compute and keep masks/counts.
    with span("forward", sync_before=False):
        with autocast_context():
            outputs = model(batch.inputs)
            loss_parts, valid_count = compute_masked_losses(outputs, batch)
            loss = reduce_loss(loss_parts, valid_count)

    # 3. Scale/backward, unscale before clipping, then record finite/overflow state.
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    grad_norm = clip_and_measure_grad_norm(model, max_norm=cfg.max_norm)
    scaler.step(optimizer)       # may be skipped when gradients are non-finite
    scaler.update()

    # 4. Persist compute/comm/wait/AMP/lifecycle events before closing the step span.
    record_scalars(loss_parts, valid_count, grad_norm, scaler.get_scale())
    profiler.step()
    return finish_event(step, collect_rank_comm_and_wait_buckets())
```

伪代码表达观测顺序：lineage → masked loss → scaled backward → unscale/clip → possible skipped step → profiler/event flush。实际 AMP、FSDP/ZeRO、异步通信和同步 API 必须按目标环境实现；代码本身不是性能或稳定性证明。

## 11. 结论与下一步

训练可观测性不是把日志数量堆多，而是让每个数值、时间和状态都能回到一个可复现的 step/rank/request。Loss、grad、AMP overflow、data wait、communication 和 logging overhead 必须分层；Profiler/anomaly 只在短窗口和 first-failure replay 中使用。当前本地材料足以建立 schema 和诊断路线，但不足以声称 UWM/OPD/OpenPiVLA 已完成 per-rank telemetry、AMP 稳定性或吞吐优化。

当前节点已完成知识页和一张 `unseen` 题卡；仍保持 `WARN`。下一步可进行 ENG-017 一题口述，或补 overflow/rank trace/first-failure artifacts；ENG-018 继续后置。

## References

1. PyTorch 2.13，[Automatic Mixed Precision](https://docs.pytorch.org/docs/2.13/amp.html)：autocast、GradScaler、unscale 与 overflow/scale 边界。
2. PyTorch 2.13，[Profiler](https://docs.pytorch.org/docs/2.13/profiler.html)：activities、schedule、wait/warmup/active 与 CUPTI 边界。
3. PyTorch 2.13，[Autograd anomaly detection](https://docs.pytorch.org/docs/2.13/autograd.html)：forward traceback 与 backward NaN 检查。
4. PyTorch 2.13，[DistributedDataParallel](https://docs.pytorch.org/docs/2.13/generated/torch.nn.parallel.DistributedDataParallel.html)：gradient all-reduce 与 input-sharding 边界。
5. PyTorch 2.13，[`clip_grad_norm_`](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.clip_grad_norm_.html)：total norm 与 non-finite 检查。
6. PyTorch 2.13，[DataLoader](https://docs.pytorch.org/docs/2.13/data.html)：worker/prefetch/iterator 语义。
7. DeepSpeed，[Config JSON](https://www.deepspeed.ai/docs/config-json/)：`steps_per_print`、skipped updates 与 `wall_clock_breakdown`。
8. 本仓库，[ENG-017 Source Freeze](../sources/vol_05_eng017_training_observability_source_freeze.html)、[VOL 05 Batch 1 knowledge](../knowledge/vol_05_engineering_eval.html)、[ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html) 与 [OPD evidence inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

