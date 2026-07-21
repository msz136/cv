# VOL 05 ENG-018：Scheduler、Preemption、Retry 与幂等训练任务来源冻结

> 审计日期：2026-07-17  
> 状态：`source_frozen / VLA-ENG-018_planned / WARN`  
> 对应问题：`VLA-ENG-018`——训练任务被抢占、worker 失败或调度器重试时，如何保证可恢复、幂等且不重复污染 artifact？  
> 当前边界：本文件只冻结 TorchElastic、Distributed Checkpoint、Kubernetes Job/Pod 和 DeepSpeed checkpoint 语义，以及本地 checkpoint/retry 证据边界；知识正文、题卡、真实 preemption drill、exact resume 与 retry 性能结论后置。

## 1. 问题与最小范围（Question / Scope）

本切片回答六个问题：

1. scheduler 的 logical job、attempt、worker group、rank/world-size 与 run identity 如何区分？
2. preemption signal 到达后，怎样在有限 grace period 内保存一致 checkpoint，而不是留下半写 artifact？
3. retry 为什么可能重复启动同一程序，训练脚本如何做到 side-effect 幂等或可去重？
4. TorchElastic restart 和 Kubernetes Job retry 分别保证什么，不保证什么？
5. DCP/DeepSpeed checkpoint 如何影响多 rank、不同 world-size 与恢复合同？
6. UWM、OPD、OpenPiVLA 当前有哪些保存/load metadata，为什么仍不足以声称弹性训练或无损续训？

本页不声称本地项目已使用 Kubernetes/TorchElastic，不声称 preemption 后可 exact resume，不把 checkpoint path、summary 或 final-only weights 写成幂等重试证明。

## 2. 证据类型与冻结输入

| 输入 | 类型 | 版本 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| PyTorch `torchrun` / TorchElastic | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | `--max-restarts`、rendezvous/run ID、restart count、worker group、rank/world-size 可变化、推荐 load→initialize→train→checkpoint 结构 | 用户脚本自动保存 sampler/RNG/optimizer、exact resume 或副作用幂等 |
| TorchElastic Quickstart | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | fault-tolerant/elastic launch、failure 作为 membership change | 某集群 scheduler 的 SLA、checkpoint 成功率 |
| PyTorch Distributed Checkpoint | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | 多 rank parallel save/load、多文件 checkpoint、load-time resharding、in-place load | partial-write 原子提交、完整业务 manifest、sampler cursor 自动包含 |
| Kubernetes Job | primary / official-doc | rolling official page；访问 2026-07-17 | `backoffLimit`、replacement Pod、同一程序可能启动两次、并发容忍要求 | exactly-once execution、训练 checkpoint/resume |
| Kubernetes Pod lifecycle | primary / official-doc | rolling official page；访问 2026-07-17 | `preStop`、TERM/SIGTERM、termination grace period、超时后 KILL | 信号到达后一定有足够时间保存大 checkpoint |
| DeepSpeed model checkpointing | official-code / official-doc source | `microsoft/DeepSpeed@de1846cf6fbdd6f1c2adf046f319791ca78cc547` | save/load routines、ZeRO fp32 recovery、Universal Checkpoints 仍 under development | 当前项目已完成 cross-world-size resume、atomic save 或 retry |
| 本地 ENG-004..006 / ENG-013 audits | local-evidence | 本仓库 source freezes | UWM save/load metadata、OPD final-only/no-optimizer-state、RNG/sampler/cursor 缺口 | checkpoint binary、exact resume、preemption/retry trace |
| OpenPiVLA / OPD project inventories | local-evidence | 本仓库 evidence layer | report/manifest/path、checkpoint selection 与 lineage 风险 | scheduler attempt ledger、immutable checkpoint/load smoke、exact continuation |

### 2.1 官方来源 normalized / raw 指纹

HTML 来源按仓库统一规则：移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256；DeepSpeed RST 使用 frozen commit 的 raw bytes SHA-256。Kubernetes 页面是 rolling docs，版本锚点为访问日期和指纹。

| 来源 | URL | 指纹类型 | 长度 | SHA-256 |
| --- | --- | --- | ---: | --- |
| PyTorch `torchrun` | [2.13/elastic/run.html](https://docs.pytorch.org/docs/2.13/elastic/run.html) | normalized main text | 13889 | `77d82a42359b5f76a07260cdd9c44abd3a5002a8fff4fd54b59f64a43342560e` |
| TorchElastic Quickstart | [2.13/elastic/quickstart.html](https://docs.pytorch.org/docs/2.13/elastic/quickstart.html) | normalized main text | 2788 | `55a15d33aabcabb70aa529730c4dee30d979e77a9620015beb3f4b379bb5daf2` |
| PyTorch DCP | [2.13/distributed.checkpoint.html](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html) | normalized main text | 62096 | `937dfc304fe1162f9a0276e651eb8a0afac039c485946447b3b5d73a35240468` |
| Kubernetes Job | [Job controller](https://kubernetes.io/docs/concepts/workloads/controllers/job/) | normalized main text | 56328 | `ec66af818bd901c6b68e2da133ffcaf3933d295daa53d37cbc2ada3e60e792ff` |
| Kubernetes Pod lifecycle | [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | normalized main text | 49902 | `d9d1d6cdd3573d7329eba94aeb99adeed750a1dbab6d7bafdb07bc00634d3e92` |
| DeepSpeed model checkpointing | [model-checkpointing.rst](https://raw.githubusercontent.com/microsoft/DeepSpeed/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/model-checkpointing.rst) | raw RST bytes | 2856 | `1687250240dca70a3e3a448c47604277b5818dc1af93dca5e54a1a7baa205c11` |

## 3. 先分清四个 identity

| Identity | 含义 | 是否跨 retry 稳定 | 用途 |
| --- | --- | --- | --- |
| `logical_run_id` | 同一个训练目标/实验 | 应稳定 | lineage、最终 artifact、去重主键 |
| `attempt_id` | 调度器的一次执行尝试 | 每次 retry 变化 | 日志、临时目录、失败归因 |
| `worker_group_id` / rendezvous | 一组同时运行的 workers | restart 后可能重建 | 组成员和通信 |
| `rank/world_size` | 当前 worker 的分布式身份 | TorchElastic restart/elasticity 下可能变化 | collective、shard、rank-level trace |

TorchElastic 文档明确写明 `RANK is NOT stable`，elastic job 的 `WORLD_SIZE` 也可能变化；还提供 `TORCHELASTIC_RESTART_COUNT`、`TORCHELASTIC_MAX_RESTARTS` 和 `TORCHELASTIC_RUN_ID`。因此不能用 rank 作为永久 artifact owner，也不能把 `rank0/checkpoint.pt` 当跨 attempt 的唯一身份。

推荐目录合同：

```text
runs/<logical_run_id>/
  attempts/<attempt_id>/logs|tmp|failure.json
  checkpoints/<generation>/shards|manifest|COMMITTED
  latest -> only a committed generation
  final/ -> promoted immutable output
```

## 4. Retry 不是 exactly-once：幂等与去重

Kubernetes Job 文档明确说明，即使 `parallelism=1`、`completions=1`、`restartPolicy=Never`，同一程序有时也可能启动两次；replacement Pod 还可能在旧 Pod 终止前创建。因此训练任务必须容忍 duplicate/concurrent attempt。

若 side effect 写成函数 (F(s,x))，幂等要求可抽象为：

\[
F(F(s,x),x)=F(s,x)
\]

这里 (x) 不是“第几次启动”，而是稳定的 logical operation key，例如 `(logical_run_id, checkpoint_generation)` 或 `(run_id, eval_request_id)`。训练 step 本身通常不是天然幂等：重复消费同一 batch 会再次更新 optimizer。因此 retry 必须从 **committed checkpoint + data cursor** 恢复，而不是重新执行一段不受控的 side effect。

### 4.1 常见重复副作用

| Side effect | 重试风险 | 幂等/去重设计 |
| --- | --- | --- |
| checkpoint write | 两个 attempt 覆盖同一路径、半写 shard 被 `latest` 指向 | attempt temp dir → 校验 shards/manifest → 原子 promote/COMMITTED |
| metric/log upload | 重复 step、曲线回退或跨 attempt 混合 | key=`run+attempt+step+event`，查询时按 logical step/attempt 展开 |
| eval launch | 同 checkpoint 重复评估、结果相互覆盖 | key=`checkpoint_hash+protocol_hash`，结果 immutable |
| data generation/cache | 同样本重复写、partial cache 被复用 | content hash、write temp、atomic rename、reader 验证 manifest |
| final model publish | 失败 attempt 覆盖已验证产物 | 只从 committed checkpoint 经 gate promote；目标版本不可变 |

## 5. Preemption signal 与 checkpoint state machine

Kubernetes Pod lifecycle 文档说明，容器终止时通常先收到 TERM/SIGTERM 并有 termination grace period，超时后会收到 KILL；`preStop` 也消耗 grace period。它支持“捕获信号并尽快进入安全保存”的设计，但不保证保存一定完成。

建议状态机：

```text
PENDING → RUNNING → CHECKPOINT_REQUESTED → WRITING → COMMITTED → EXIT
                      └──────────────→ FAILED_PARTIAL
RUNNING → FAILURE → RETRY_WAIT → new ATTEMPT
```

signal handler 不直接执行复杂 distributed save；它只设置 `preempt_requested`、记录 deadline。训练循环在 micro/optimizer step 的安全边界协调所有 rank 保存，若剩余时间不足就写 failure marker，而不是把半写目录冒充 latest。

## 6. Checkpoint generation：多文件也要有提交协议

PyTorch DCP 文档说明 checkpoint 可由多 rank 并行保存、产生多个文件，并支持 load-time resharding；这意味着“目录存在”不能证明 generation 完整。每一代至少需要：

```text
model / optimizer / scheduler / scaler
RNG states / sampler epoch+cursor / data+transform manifest
world_size / rank topology / sharding strategy
code+config+environment / processor+normalizer
expected next sample IDs / logical step / attempt lineage
per-file size+SHA / global manifest / COMMITTED marker
```

写入顺序应是：创建 attempt-scoped temp generation → 所有 rank 写 shard → barrier/collect errors → 写 manifest 与哈希 → load/read smoke → 最后发布 COMMITTED/latest。这个原子 promote 协议是本仓库工程合同，不是 DCP 自动保证的业务 schema。

DeepSpeed frozen source提供 save/load、ZeRO fp32 recovery，并把 Universal Checkpoints 标为 under development；因此跨 world-size 或 3D parallelism 恢复不能只凭“DeepSpeed 支持 checkpoint”就宣称完成。

## 7. TorchElastic restart 的边界

TorchElastic `torchrun` 提供 `--max-restarts`、rendezvous ID 和 restart-count 环境变量；worker failure 时，worker group 可以被重新启动。官方文档推荐的脚本结构包含 `load_checkpoint → initialize → train → periodic checkpoint`。

但 restart 只重新拉起进程，不自动保证：

- 最新 checkpoint 是完整 generation；
- optimizer/scaler/RNG/sampler cursor 被保存；
- 新 world-size 下 data partition 和 effective batch 语义不变；
- 外部日志、eval、cache 或 model registry 没有重复副作用；
- checkpoint 后到 failure 前的样本不会重复或漏掉。

因此恢复语义要明确是：`restart-from-scratch`、`weights-only warm start`、`epoch-boundary resume`，还是 `mid-epoch exact replay`。没有 artifact 时不要统称为 resume。

## 8. 最小 retry/preemption 验证矩阵

| Case | 注入点 | 必须验证 |
| --- | --- | --- |
| clean restart | checkpoint 后正常退出 | load、next sample IDs、optimizer step、scaler、loss |
| SIGTERM preemption | micro step、optimizer step 后、checkpoint 中 | deadline、rank coordination、partial generation 不可见、fallback generation |
| worker crash | 单 rank forward/backward/collective | group restart、attempt/restart count、no deadlock、rank remap |
| duplicate attempt | 两个同 logical run 同时启动 | temp isolation、checkpoint/eval dedupe、single final promotion |
| world-size change | N→M ranks load | DCP/框架 reshard、effective batch、sampler partition、metric continuity |
| storage failure | shard/manifest/upload 中断 | partial marker、hash failure、retry 不覆盖 last committed |

结果同时报告 recovery time、lost/replayed steps、duplicate side effects、checkpoint bytes/write time、success/failure reason 和 resumed numerical diff；只报告“job 最终成功”无法证明恢复正确。

## 9. 最小伪代码（工程合同，不是 upstream 实现）

```python
def run_training(logical_run_id, attempt_id, cfg):
    # 1. Resolve only a committed checkpoint; never load a partial generation.
    checkpoint = resolve_latest_committed(logical_run_id)
    state = load_full_training_state(checkpoint, cfg)

    # 2. Signal handlers only request preemption; distributed save runs at a safe boundary.
    preempt = install_preemption_flag_and_deadline()
    for batch in restore_sampler_and_iter(state):
        train_one_step(batch, state)

        if should_checkpoint(state) or preempt.requested:
            tmp = create_attempt_scoped_generation(logical_run_id, attempt_id, state.step)
            save_all_rank_shards_and_manifest(tmp, state)
            verify_load_smoke_and_next_sample(tmp, state)
            atomically_mark_committed_and_promote_latest(tmp)

        if preempt.requested:
            return exit_with_retryable_code()

    # 3. Final publication is keyed by immutable checkpoint+protocol hashes.
    promote_final_once(checkpoint_hash=state.checkpoint_hash,
                       protocol_hash=cfg.protocol_hash)
```

伪代码表达 logical run/attempt 隔离、safe-boundary save、manifest-last commit、retryable exit 和 immutable promotion；具体 signal、barrier、DCP/DeepSpeed API、object store rename 和 scheduler exit code 必须由部署环境实现。

## 10. 本地项目证据与真实性边界

本仓库当前证据：

- UWM 有 save summary、checkpoint load report、normalizer 和 effective config，但本地 snapshot 没有 checkpoint binary；不能验证 generation 完整、load smoke、sampler cursor 或 preemption continuation。
- OPD 有 ZeRO-2/3 config、checkpoint selection table 和 `final_model_only_no_intermediate_checkpoints` / `final_weights_no_optimizer_state` manifest；这明确是 weights-only/final-only 边界，不是 exact resume。
- OpenPiVLA 有 formal trainer、report、远端 log/checkpoint 路径引用与 smoke/diagnostic artifact，但缺 checkpoint hash/load smoke、attempt ledger 和 retry/preemption trace。

安全回答：

> “我会把 logical run、attempt、worker group 和 rank 分开。重试可能重复启动程序，所以 checkpoint、eval 和最终发布都用稳定 key 去重；checkpoint 采用 attempt 临时目录、全 rank shard/manifest 校验、load smoke 后再 COMMITTED/latest。当前项目有保存/load metadata 和 final-only manifest，但没有 binary、sampler/RNG/optimizer bundle 或 preemption drill，因此我不会说已经实现无损弹性续训。”

| 口径 | 证据等级 | 面试安全表达 |
| --- | --- | --- |
| UWM save/load metadata | local-direct/report-supported | 有保存/load 路径与摘要，binary 缺失 |
| OPD final-only/no-optimizer-state | local-direct manifest | weights-only continuation，不是 exact resume |
| OpenPiVLA remote checkpoint paths | remote-referenced/report-supported | 路径存在于报告，未做 immutable load smoke |
| preemption/retry/idempotency | unverified | 当前没有 scheduler/attempt/signal/duplicate trace |

## 11. Gate、风险与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| TorchElastic restart identity | `PASS WITH WARNING` | run/attempt/restart/rank 分层；不假设 rank/world-size 稳定 |
| Kubernetes retry/idempotency | `PASS WITH WARNING` | 稳定 operation key、attempt temp、dedupe 与 immutable promotion |
| signal/graceful termination | `PASS WITH WARNING` | safe-boundary coordinated save；测 checkpoint time 与 grace budget |
| DCP/DeepSpeed checkpoint | `PASS WITH WARNING` | multi-file manifest-last commit、load smoke、lineage 和 world-size test |
| local project recovery | `WARN` | 补 binary、full state、attempt ledger、SIGTERM/crash/duplicate drills |
| knowledge/card | `DRAFTED / UNSEEN` | ENG-018 知识节点和一张题卡已生成；保持 `unseen`，后续补 binary/full-state/preemption/retry artifacts；ENG-019 后置 |

## 参考来源（References）

1. PyTorch 2.13，[Elastic Run / torchrun](https://docs.pytorch.org/docs/2.13/elastic/run.html)：worker group、restart、run/restart count、rank/world-size instability。
2. PyTorch 2.13，[TorchElastic Quickstart](https://docs.pytorch.org/docs/2.13/elastic/quickstart.html)：fault-tolerant/elastic launch 与 `--max-restarts`。
3. PyTorch 2.13，[Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html)：multi-rank save/load、多文件与 load-time resharding。
4. Kubernetes，[Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)：backoff、replacement、duplicate/concurrent execution 边界。
5. Kubernetes，[Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)：preStop、TERM/SIGTERM、grace period 与 KILL。
6. Microsoft DeepSpeed，[Model Checkpointing](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/model-checkpointing.rst)：save/load、ZeRO recovery 与 Universal Checkpoints under development。
7. 本仓库，[ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)、[ENG-013 Reproducibility](vol_05_eng013_reproducibility_source_freeze.html)、[OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
