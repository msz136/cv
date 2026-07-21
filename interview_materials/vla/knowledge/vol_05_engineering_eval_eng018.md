# VOL 05 Engineering / Evaluation：Scheduler、Preemption、Retry 与幂等训练任务（ENG-018）

> 状态：`drafted / knowledge_20_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-018`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-018 Scheduler / Preemption / Retry Source Freeze](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)。  
> 核心边界：scheduler retry 只负责再次启动，不能自动保证 checkpoint 完整、optimizer/RNG/sampler 恢复、exact resume 或副作用 exactly-once。

## 问题（Question）

`VLA-ENG-018`：训练被抢占、worker 失败或 scheduler 重试时，如何设计 run identity、checkpoint generation、信号处理和幂等副作用，避免重复训练、半写 checkpoint 或错误续训？

面试回答应先区分：

1. **谁在重试**：logical run、attempt、worker group、rank；
2. **恢复什么**：restart-from-scratch、weights-only、epoch-boundary 还是 exact mid-epoch；
3. **如何提交 artifact**：临时目录、manifest、校验、`COMMITTED`、latest/final promotion；
4. **如何证明**：注入 SIGTERM、worker crash、duplicate attempt、storage failure 和 world-size change。

## 知识地图位置与前置依赖

```text
ENG-006 checkpoint lineage + ENG-013 RNG/sampler replay
                 ↓
logical run / attempt / worker group / rank identity
                 ↓
preemption signal → safe-boundary checkpoint → committed generation
                 ↓
retry/dedupe/idempotent side effects → recovery drill → closed-loop eval
```

前置：

- `VLA-ENG-006/013`：checkpoint bundle、RNG、sampler cursor、next-batch replay。
- `VLA-ENG-015`：offload、checkpoint write time、固定 A/B。
- `VLA-ENG-017`：事件、rank trace、first-failure 与 lineage schema。
- [ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：本地 binary/resume 缺口。

## 1. 短答：retry 只重新启动，不能替你恢复状态

**30 秒回答**：我把 logical run、attempt、worker group 和 rank 分开；retry 每次用新 attempt ID，checkpoint 写到临时 generation，所有 rank 完成 shard/manifest/hash/load smoke 后才标记 `COMMITTED` 并更新 latest。SIGTERM 只设置 preempt flag，训练在安全边界保存；Kubernetes/TorchElastic 可能重复启动或改变 rank/world-size，所以用稳定 operation key 去重。当前项目没有 binary、full-state bundle 或 preemption drill，不能说 exact resume。

## 2. 直觉：把训练当成可恢复事务

一个训练任务像长事务：

- logical run 是业务目标；attempt 是一次执行尝试；
- checkpoint generation 是事务快照；`COMMITTED` 是提交标记；
- retry 是重新执行尝试，不是把上一次进程的内存直接复活；
- latest/final 只能指向已经校验和可读的 committed generation。

如果进程在写 shard 的中途被杀死，目录存在不代表状态可读；如果两个 attempt 同时写 `latest`，最后完成的 attempt 也不一定是正确或最新的。因此保存和发布要采用“临时写入 → 校验 → 原子 promote”的事务思路。

## 3. 四层 identity：不要把 rank 当永久 owner

| Identity | 作用 | retry/restart 后是否稳定 | 典型字段 |
| --- | --- | --- | --- |
| `logical_run_id` | 同一个实验/训练目标 | 稳定 | dataset/config/base model/预算 hash |
| `attempt_id` | scheduler 的一次执行 | 变化 | start time、failure reason、retry index |
| `worker_group_id` | 同时工作的进程集合 | 可重建 | rendezvous/run ID、membership |
| `rank/world_size` | 当前通信身份 | 可能变化 | rank、local rank、world-size、node |

TorchElastic 文档明确 `RANK` 不稳定，elastic job 中 `WORLD_SIZE` 也可能变化；`TORCHELASTIC_RESTART_COUNT` 和 `TORCHELASTIC_RUN_ID` 可用于记录重启上下文。故 artifact owner 应使用 `logical_run_id + generation`，而不是 `rank0` 路径或某次 attempt 的本地目录。

## 4. Retry 与幂等副作用

Kubernetes Job 文档说明，同一程序可能启动两次，甚至出现并发 Pod；`backoffLimit` 控制失败尝试边界，但不提供 exactly-once 训练语义。

可用稳定 operation key 表示副作用：

\[
k=\operatorname{hash}(logical\_run\_id, operation\_type, generation\_or\_request\_id)
\]

如果相同 (k) 的操作被重复执行，系统应返回同一已提交结果或安全地发现冲突，而不是覆盖未知状态。训练 optimizer step 本身不是天然幂等；因此 retry 只能从明确 committed state 和 sampler/RNG cursor 恢复，不能盲目重跑已消费 batch。

| 副作用 | 可靠模式 | 不能做 |
| --- | --- | --- |
| checkpoint | `attempt/tmp/generation` → hash/manifest/load smoke → `COMMITTED` → latest | 直接覆盖 `latest` |
| metrics/logs | attempt-scoped event key，按 logical step 聚合 | 把两次 attempt 的 step 直接拼接 |
| eval | `checkpoint_hash + protocol_hash` 去重，结果 immutable | 同路径覆盖不同 scorer/协议 |
| cache/data generation | content hash、临时写、原子 rename | 读取未完成 cache |
| final publish | 只从 committed generation 经过 gate promote | 任意 retry 直接覆盖 final |

## 5. Preemption：信号到安全 checkpoint

Kubernetes Pod lifecycle 文档描述了 TERM/SIGTERM、termination grace period 和超时后的 KILL；`preStop` 也占用 grace budget。训练进程不能假设收到信号后一定有足够时间写完整 checkpoint。

推荐状态机：

```text
PENDING → RUNNING → CHECKPOINT_REQUESTED → WRITING → COMMITTED → EXIT
                      └──────────────→ FAILED_PARTIAL
RUNNING → FAILURE → RETRY_WAIT → new ATTEMPT
```

信号 handler 只做三件事：记录 signal/deadline、设置 `preempt_requested`、让主循环在安全边界协调保存。保存应优先在 micro/optimizer step 边界执行，避免一个 rank 已退出而其他 rank 卡在 barrier；如果剩余 grace 不够，要留下 `FAILED_PARTIAL`/retryable marker，而不是把半写目录公开为 latest。

## 6. Checkpoint generation 与 DCP/DeepSpeed

PyTorch DCP 支持多 rank 并行保存/加载，checkpoint 由多文件组成，并支持 load-time resharding；这适合大模型，但也意味着完整性不能由单个路径存在判断。一个 generation 至少包含：

```text
model / optimizer / scheduler / scaler
CPU/CUDA/Python/NumPy RNG / sampler epoch+cursor
data/transform/normalizer/processor manifest
world-size / sharding strategy / code+config+environment
expected next sample IDs / logical step / attempt lineage
per-file size+SHA / global manifest / COMMITTED
```

写入顺序：

1. 创建 attempt-scoped temp generation；
2. 所有 rank 写 shard，收集错误；
3. barrier 后生成 manifest、文件 hash 和 metadata；
4. 用独立 load/read smoke 检查 shape、optimizer、scaler、normalizer 和 next-batch；
5. 最后写 `COMMITTED` 并原子更新 latest。

DeepSpeed frozen checkpointing source 提供 save/load、ZeRO fp32 recovery，并说明 Universal Checkpoints 仍 under development；因此跨 world-size/3D parallelism 的恢复仍需显式验证。

## 7. TorchElastic restart 的边界

`torchrun --max-restarts` 和 rendezvous 可以重新拉起 worker group；官方建议训练脚本采用 `load_checkpoint → initialize → train → save_checkpoint` 结构。但 restart 不自动保存/恢复：

- optimizer、scheduler、scaler、RNG、sampler cursor；
- latest generation 是否完整、是否来自同一 logical run；
- world-size 改变后的 effective batch 和 data partition；
- 外部 metric/eval/cache 的重复副作用；
- checkpoint 后到 failure 前的样本是否重复或丢失。

因此恢复结论必须标注强度：

| 结论 | 最小证据 |
| --- | --- |
| restart-from-scratch | 新 attempt 能启动 |
| weights-only warm start | model weights hash + load smoke |
| epoch-boundary resume | optimizer/scheduler/scaler/RNG + 下一 epoch sample IDs |
| mid-epoch exact replay | sampler cursor、所有 RNG、worker/prefetch、fixed next-batch diff |

## 8. Recovery drill 矩阵

| Case | 注入点 | 通过条件 |
| --- | --- | --- |
| clean restart | committed checkpoint 后退出 | load、next IDs、loss、optimizer/scaler 一致 |
| SIGTERM preemption | micro step、optimizer step、checkpoint write 中 | grace 内 safe save；partial 不可见；retryable exit |
| worker crash | forward/backward/collective | group restart、无 deadlock、rank remap 可记录 |
| duplicate attempt | 两个相同 logical run 同时启动 | temp 隔离、side effect 去重、single final promotion |
| world-size change | N→M ranks load | DCP/框架 reshard、effective batch/sampler 语义明确 |
| storage failure | shard/manifest/upload 中断 | last committed 不变；retry 不读 partial、不覆盖已验证结果 |

结果至少报告 recovery time、lost/replayed steps、duplicate side effects、checkpoint bytes/write time、failure reason 和 resumed numerical diff；“Job 最终成功”不等于恢复正确。

## 9. 本地项目映射与真实性边界

本仓库证据支持：

- UWM 有 save summary、checkpoint load report、normalizer 和 effective config，但 snapshot 没有 checkpoint binary，不能验证 generation 完整、optimizer/RNG/sampler cursor 或 preemption continuation。
- OPD 有 ZeRO-2/3 配置、checkpoint selection table 和 `final_model_only_no_intermediate_checkpoints` / `final_weights_no_optimizer_state` manifest；这是 final/weights-only 边界，不是 exact resume。
- OpenPiVLA 有 formal trainer、report、远端 log/checkpoint path 引用和 smoke/diagnostic artifact，但缺 immutable checkpoint hash/load smoke、attempt ledger、SIGTERM/retry trace。

安全回答：

> “我会把 logical run、attempt、worker group、rank 分开。retry 可能重复启动，因此 checkpoint、eval 和 final publish 都用稳定 key 去重；checkpoint 写到 attempt 临时 generation，所有 rank 完成 shard/manifest/hash/load smoke 后才 COMMITTED/latest。当前项目能证明保存/load metadata 和 final-only 配置，但没有 binary、optimizer/RNG/sampler bundle 或 preemption drill，所以我不会说已实现无损弹性续训。”

| 口径 | 证据等级 | 面试安全表达 |
| --- | --- | --- |
| UWM save/load metadata | local-direct/report-supported | 有保存/load 摘要，binary 缺失 |
| OPD final-only/no-optimizer-state | local-direct manifest | weights-only continuation，不是 exact resume |
| OpenPiVLA remote checkpoint path | remote-referenced | 报告中有路径引用，未做 immutable load smoke |
| scheduler/retry/preemption/idempotency | unverified | 当前没有 attempt/signal/duplicate/world-size drill |

## 10. 验证伪代码（工程合同，不是 upstream 实现）

```python
def run_attempt(logical_run_id, attempt_id, cfg):
    # 1. Resolve only a committed generation and restore the full training state.
    state = load_full_state(resolve_latest_committed(logical_run_id), cfg)
    preempt = install_signal_flag_and_deadline()

    for batch in restore_sampler_and_iter(state):
        train_one_step(batch, state)

        # 2. Save only at a safe boundary, using an attempt-scoped temp directory.
        if should_checkpoint(state) or preempt.requested:
            tmp = create_temp_generation(logical_run_id, attempt_id, state.step)
            save_all_rank_shards(tmp, state)
            write_manifest_and_hashes(tmp, state)
            verify_load_and_next_batch(tmp, state)
            atomically_commit_and_promote_latest(tmp)

        # 3. Exit retryably after a committed generation, never from a partial path.
        if preempt.requested:
            return retryable_exit("preempted_after_commit")

    # 4. Final publication is keyed by immutable checkpoint/protocol hashes.
    promote_final_once(state.checkpoint_hash, cfg.protocol_hash)
```

伪代码表达 committed-only load、safe-boundary save、manifest-last、atomic promotion 和 retryable exit；signal/barrier/DCP/DeepSpeed/object-store API 必须由部署环境实现，代码本身不是 exact resume 证明。

## 11. Trade-off、bad case 与追问

### 11.1 Trade-off

- checkpoint 越频繁，lost work 越少，但写入/同步开销越高。
- grace budget 越短，越需要轻量增量/异步保存或提前 checkpoint；不能把大 checkpoint 写入时间假设为零。
- retry 上限越高，短暂故障更能恢复，但重复副作用和总成本也会上升。
- world-size elastic 提高资源弹性，却要求重新验证 sampler、effective batch、optimizer state 和 metrics continuity。

### 11.2 高概率 bad case

1. 把 `rank0/checkpoint.pt` 当成跨 retry 永久路径。
2. retry attempt 直接覆盖 `latest`，导致旧 checkpoint 被半写目录污染。
3. 捕获 SIGTERM 后每个 rank 独自保存，最终 barrier deadlock 或 shard 不一致。
4. 只保存 model weights，却把结果说成 optimizer/RNG/sampler exact resume。
5. Job 最终成功就忽略 duplicate eval、重复数据生成或不同 attempt 的日志混合。
6. world-size 变化后仍复用旧 rank、batch 和 sampler 假设。

### 11.3 面试追问

1. logical run 和 attempt 为什么不能用同一个 ID？
2. `COMMITTED` 应在什么时候写？
3. 如果 SIGTERM 发生在 checkpoint write 中间怎么办？
4. Kubernetes retry 和 TorchElastic restart 各自保证什么？
5. 如何证明下一批 sample IDs 没有重复或丢失？
6. 如果 checkpoint 写入时间超过 grace period，系统如何降级？

## 12. 结论与下一步

可靠训练任务必须把 scheduler、signal、checkpoint 和 side effect 设计成一条恢复合同：logical run 保持稳定，attempt 可重试，rank 可变化；checkpoint 先写临时 generation，完成全 rank 校验和 load smoke 后再 `COMMITTED`；final/eval/cache 用稳定 key 去重。TorchElastic/Kubernetes/DCP/DeepSpeed 官方语义支持这些机制的边界，但不自动证明本地 exact resume 或 exactly-once。

当前节点已完成知识页和一张 `unseen` 题卡；仍保持 `WARN`。下一步可进行 ENG-018 一题口述，或补 binary、attempt、signal、duplicate 和 world-size recovery artifacts；ENG-019 继续后置。

## References

1. PyTorch 2.13，[Elastic Run / torchrun](https://docs.pytorch.org/docs/2.13/elastic/run.html)：worker group、restart、run/restart count、rank/world-size instability。
2. PyTorch 2.13，[TorchElastic Quickstart](https://docs.pytorch.org/docs/2.13/elastic/quickstart.html)：fault-tolerant/elastic launch 与 `--max-restarts`。
3. PyTorch 2.13，[Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html)：multi-rank save/load、多文件与 load-time resharding。
4. Kubernetes，[Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)：backoff、replacement、duplicate/concurrent execution 边界。
5. Kubernetes，[Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)：preStop、TERM/SIGTERM、grace period 与 KILL。
6. Microsoft DeepSpeed，[Model Checkpointing](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/model-checkpointing.rst)：save/load、ZeRO recovery 与 Universal Checkpoints under development。
7. 本仓库，[ENG-018 Source Freeze](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)、[ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)、[ENG-013 Reproducibility](../sources/vol_05_eng013_reproducibility_source_freeze.html) 与项目 inventory。

