# VOL 05 Engineering / Evaluation：Activation Checkpointing、CPU/NVMe Offload 与吞吐（ENG-015）

> 状态：`drafted / knowledge_17_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-015`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-015 Activation Checkpointing / Offload Source Freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html)。  
> 核心边界：activation checkpointing 是重算换显存；CPU/NVMe offload 是 state 归属变化；显存下降、吞吐提升和完整 resume 都必须用 workload 级 artifact 分别证明。

## 问题（Question）

`VLA-ENG-015`：当 VLA 训练显存不够时，activation checkpointing、CPU/NVMe offload 应该怎样选择？如何证明没有用显存收益换来不可接受的吞吐、数值或恢复风险？

面试中先回答两个分类问题：**哪类 tensor 被省略或搬走？什么时候需要它？** 然后再回答测量问题：**峰值显存、step time、数值 parity 和 resume 是否在同一协议下验证？**

## 知识地图位置与前置依赖

```text
数据等待/有效 batch（ENG-003/005）
        ↓
显存账本 → activation checkpoint / FSDP CPU / ZeRO CPU-NVMe
        ↓
step-time 分解 → checkpoint lineage / replay（ENG-006/013）
        ↓
VLA action shape、normalizer、controller 和 closed-loop eval（ENG-008/EVAL-001）
```

前置：

- `VLA-ENG-003`：DataLoader、GPU、同步与吞吐分解。
- `VLA-ENG-004..006`：DDP/FSDP/ZeRO、effective batch、checkpoint lineage。
- `VLA-ENG-013`：RNG、sampler cursor 与 resume smoke。
- [ENG-015 Source Freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html)：PyTorch 2.13、DeepSpeed frozen commit 与本地 artifact gate。

## 1. 短答：先分清机制，再谈收益

**30 秒回答**：activation checkpointing 不保存一部分 forward activation，在 backward 时重算，主要换取 GPU activation 显存；FSDP CPU offload 把参数、梯度等 state 移到 CPU，ZeRO-Offload/Infinity 还可把分片 state 放到 CPU/NVMe。它们的代价分别是重算、传输、CPU/I/O 等待和恢复复杂度。我要在固定 code/data/effective batch/world-size 下同时测 peak memory、p50/p95 step time、数值 parity 和 fixed-next-batch resume；当前 UWM/OPD 只有配置与 report，不能声称吞吐或恢复收益。

## 2. 直觉：训练显存像一间有不同货架的仓库

参数、梯度、optimizer state、activation、teacher 和临时 buffer 不是同一种货物：

- activation checkpointing 是“只保留检查点，其他中间货物需要时重新生产”；
- CPU offload 是“把不在当前计算路径的货物放到旁边的仓库”；
- NVMe offload 是“把更多货物放到容量更大的但更慢的仓库”；
- ZeRO/FSDP sharding 是“不同工位只保留自己负责的份额”。

因此，“GPU 变空了”不等于“工厂每分钟产量变高”：重新生产、搬运、排队和同步可能把节省的空间换成时间。

## 3. 四种机制的对象与生命周期

| 机制 | 主要对象 | 何时发生 | 主要收益 | 主要代价/边界 |
| --- | --- | --- | --- | --- |
| activation checkpointing | forward 中间 activation | backward 需要梯度时重算 | 降低 (M_{\mathrm{act}}) | 额外 FLOPs；随机函数需处理 RNG；非纯函数可能导致错误梯度 |
| FSDP CPU offload | FSDP 参数；`offload_params=True` 时梯度也到 CPU | 参数不参与计算时、梯度归约后 | 降低 GPU 参数/梯度驻留 | CPU↔GPU copy；optimizer step 在 CPU；CPU-offload 下 accumulation 有限制 |
| ZeRO-Offload | ZeRO-2 的 optimizer/gradient state | state update 与归约路径 | 降低 GPU optimizer/gradient state | CPU 内存与 host compute；不能当作 activation checkpoint |
| ZeRO-Infinity | ZeRO-3 的分片参数/梯度/optimizer state，可到 CPU/NVMe | gather、partition、offload 生命周期 | 扩大可容纳的 model-state 容量 | NVMe latency/bandwidth、buffer/prefetch、I/O overlap 与调度复杂度 |

PyTorch 2.13 的 checkpoint 文档把 activation checkpointing 定义为 compute-for-memory trade-off，并说明 `use_reentrant=False` 是推荐实现；FSDP 文档说明 `CPUOffload(offload_params=True)` 会让参数和梯度进入 CPU，optimizer step 在 CPU。DeepSpeed 冻结文档则把 activation checkpointing 与 ZeRO state offload 作为不同 API/配置族，不能用一个机制替代另一个机制。[1–4]

## 4. Activation checkpointing：重算区域和 RNG 合同

### 4.1 机制与公式

普通训练可近似写成：

\[
M_{\mathrm{peak}} \approx M_{\mathrm{param}}+M_{\mathrm{grad}}+M_{\mathrm{optim}}+M_{\mathrm{act}}+M_{\mathrm{temp}}+M_{\mathrm{fragment}}
\]

activation checkpointing 主要减少需要长期保存的 (M_{\mathrm{act}})，但不会自动消除参数、optimizer、临时 buffer、通信峰值或 allocator fragmentation。实现上，checkpoint segment 的 forward 输出不保存全部内部 intermediates；backward 再次调用同一函数得到梯度所需的值。

若一次 step 的原始时间为 (T_0)，checkpoint 后可写成工程上的近似：

\[
T_{\mathrm{ckpt}} \approx T_0 + T_{\mathrm{recompute}} + T_{\mathrm{rng}} + T_{\mathrm{sync}}
\]

其中 (T_{\mathrm{recompute}}) 是重算时间，(T_{\mathrm{rng}}) 是保存/恢复随机状态的开销，(T_{\mathrm{sync}}) 是必须等待的同步。这个式子是 workload 分解，不是 PyTorch 官方性能公式；是否能被通信/数据加载 overlap，必须实测。

### 4.2 为什么随机操作是风险点

PyTorch 文档说明默认 checkpoint 逻辑会保存 CPU 与一个设备类型的 RNG state；关闭 `preserve_rng_state` 可以省开销，但若 segment 含 dropout 或随机 augmentation，前后执行可能不再等价。多设备时只保存一个设备类型也有明确边界。

所以验证时至少固定：随机输入、dropout policy、CPU/CUDA RNG state、checkpoint segment、`use_reentrant`、dtype 和 world-size。不能因为 loss 曲线还能下降，就说 checkpoint 版本与 baseline 完全等价。

### 4.3 reentrant / non-reentrant 面试口径

安全回答不是背 API 差异，而是说明选择理由：使用官方推荐的 non-reentrant 路径时，仍要检查函数是否纯、输入输出是否满足 autograd 约束、随机状态是否可复现；如果沿用 reentrant 旧路径，就必须说明其限制和版本合同。任何“只包一层 `checkpoint()` 就没有副作用”的回答都不完整。

## 5. CPU/NVMe offload：state 归属与传输路径

### 5.1 FSDP CPU offload

FSDP 的 `CPUOffload` 不是普通的 `tensor.to("cpu")`。官方语义是：当参数不参与计算时可放在 CPU；`offload_params=True` 时梯度也 offload 到 CPU，optimizer step 在 CPU。FSDP 文档还警告 CPU offloading 下不能把 `no_sync()` 之外的 gradient accumulation 当成无条件支持，因为归约梯度处理可能得到错误结果。

因此一个 FSDP A/B 至少要记录：`sharding_strategy`、wrap policy、offload 参数、optimizer device、gradient accumulation、CPU pinned memory、copy/compute overlap 和 peak GPU/CPU memory。只改 config 不等于对应 run 已按该语义执行。

### 5.2 ZeRO-Offload 与 ZeRO-Infinity

DeepSpeed 的 ZeRO 文档把 model states 分为 optimizer states、gradients、parameters：Stage 1/2/3 逐步增加分片对象；ZeRO-Offload 在 ZeRO-2 路径中把 optimizer/gradient states 放到 CPU；ZeRO-Infinity 在 ZeRO-3 上扩展到 CPU 与 NVMe memory，并提供 `offload_optimizer`、`offload_param` 与 `nvme_path` 配置示例。

这说明 offload 的对象和时机与 activation checkpointing 不同：checkpointing 让某些 activation 不常驻；ZeRO offload 让 state 在不同设备层级间流动。DeepSpeed 文档提到 bandwidth utilization、overlap 和 memory-centric tiling，但这些是系统设计能力或目标，不是当前机器上“吞吐提升”的证据。

### 5.3 CPU 与 NVMe 的工程账本

对每个 step，可把时间拆成：

\[
T_{\mathrm{step}} = T_{\mathrm{data}}+T_{\mathrm{fwd}}+T_{\mathrm{recompute}}+T_{\mathrm{bwd}}+T_{\mathrm{copy}}+T_{\mathrm{comm}}+T_{\mathrm{io}}+T_{\mathrm{sync}}
\]

(T_{\mathrm{copy}}) 覆盖 CPU↔GPU，(T_{\mathrm{io}}) 覆盖 NVMe 读写和 queue wait；(T_{\mathrm{comm}}) 覆盖 sharding/gather/partition。有效吞吐 (S=\mathrm{effective\ samples}/T_{\mathrm{step}}) 只有在 effective batch、数据、warm-up、precision、world-size 和测量窗口相同的情况下才可比较。

## 6. 选择策略：先定位账本中的最大项

| 观察到的瓶颈 | 先试什么 | 必须测什么 | 不能直接说什么 |
| --- | --- | --- | --- |
| activation 峰值高，参数/optimizer 尚可 | activation checkpointing | peak memory、recompute ms、RNG/determinism、step p50/p95 | “一定更快” |
| 参数/梯度/optimizer 占满 GPU，CPU 余量足 | FSDP CPU 或 ZeRO CPU offload | GPU/CPU memory、copy、CPU optimizer、accumulation 语义 | “activation 也被 offload” |
| model states 超过 CPU 容量，NVMe 较快 | ZeRO-Infinity / NVMe | NVMe bandwidth、queue wait、buffer hit、I/O overlap | “NVMe 保持原吞吐” |
| 多 teacher/action expert 造成临时峰值 | 先做 live-state/temporary-buffer ledger | teacher residency、peak timeline、通信/同步 | “只调 batch size 就解决” |

先用 profiling 证明峰值来源，再选择机制；否则很容易把 activation 问题误诊成 optimizer state 问题，或把 PCIe/I/O 等待误诊成 DataLoader stall。

## 7. 最小 matched A/B 协议

### 7.1 固定合同

每个 baseline/candidate run 固定：

- code commit、framework/backend、driver/SDK 与 world-size；
- model、optimizer、teacher 数量、dtype、sequence/action horizon；
- dataset/transform manifest、split、effective batch、gradient accumulation；
- checkpoint segment、offload device、CPU pinned memory、NVMe path/buffer；
- warm-up 数、测量窗口、同步方式、失败重试和 telemetry schema。

### 7.2 指标和 parity

相对误差可作为统一的工程检查：

\[
e_{\mathrm{rel}}=\frac{\lVert y_{\mathrm{candidate}}-y_{\mathrm{baseline}}\rVert_2}{\max(\lVert y_{\mathrm{baseline}}\rVert_2,\epsilon)}
\]

这里 (y) 可以是 forward 输出、gradient、归一化 action 或 denormalized controller input；(epsilon) 防止零范数。容差按 dtype、算子和 action contract 声明，不能把不同硬件要求成字节级相同。

吞吐同时报告 peak GPU/CPU/NVMe memory、step p50/p95、samples/s、recompute/copy/comm/io/data_wait buckets、overflow/scaler state 和 closed-loop protocol。只报一个 final samples/s，无法说明收益来自哪里。

### 7.3 resume gate

offload 版本的 checkpoint bundle 至少包含：model/optimizer/scheduler/scaler、offload 配置、code/data manifest、CPU/CUDA/Python/NumPy RNG、sampler/cursor、normalizer/processor、expected next sample IDs。保存能 load 只证明序列化入口可读；必须做 fixed-next-batch 或 one-step replay，才能讨论中途恢复。

## 8. 验证伪代码（工程合同，不是 upstream 实现）

```python
def compare_memory_policy(baseline_cfg, candidate_cfg, fixed_requests):
    # 1. Freeze code/data/effective-batch/world-size before changing memory policy.
    baseline = launch_run(baseline_cfg, fixed_requests, warmup=10)
    candidate = launch_run(candidate_cfg, fixed_requests, warmup=10)

    # 2. Collect peak memory and wait buckets, not only one final throughput number.
    fields = ["peak_gpu", "peak_cpu", "nvme_io", "recompute_ms", "copy_ms", "step_ms"]
    base_metrics = collect_metrics(baseline, fields=fields)
    cand_metrics = collect_metrics(candidate, fields=fields)

    # 3. Compare fixed-batch outputs, gradients and scaler/overflow state.
    parity = compare_fixed_batch(baseline, candidate, tolerance=candidate_cfg.tolerance)

    # 4. Resume from candidate and compare the next sample IDs and one-step result.
    resume = fixed_next_batch_resume_smoke(candidate, fixed_requests)

    # 5. Keep the verdict WARN when memory drops but parity/throughput/resume is missing.
    return summarize(base_metrics, cand_metrics, parity, resume)
```

伪代码表达的是验证顺序：固定 workload → 记录峰值/等待 → parity → resume。`launch_run`、`collect_metrics` 和 `fixed_next_batch_resume_smoke` 需要在具体 PyTorch/FSDP/DeepSpeed 环境实现；代码本身不是性能或恢复证明。

## 9. 项目映射：UWM / OPD 能说到哪里

本仓库 [ENG-004..006 Local Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html) 盘点到：

- UWM 有 8 卡训练 summary、DeepSpeed/effective config、action normalizer 和 checkpoint load report；某条 effective config 明确 `zero_optimization.stage=0`。
- OPD 有 ZeRO-2/3 配置和 final-only/no-optimizer-state manifest；这是 config/manifest evidence，不是性能或完整 resume evidence。
- 当前快照没有 `.pt/.pth/.ckpt/.safetensors/.bin` checkpoint binary，也没有 optimizer/scheduler/scaler/RNG/sampler lineage、matched throughput A/B 或 fixed-batch continuation。

安全回答：

> 我会先用显存账本判断瓶颈来自 activation、state 还是 temporary buffer，再决定 checkpoint 或 offload。当前项目能支持我讨论 UWM/OPD 的配置和 checkpoint 风险，但还不能说 activation checkpointing/NVMe offload 已经带来吞吐提升或无损 resume。下一步要补固定 effective batch 的 A/B、profiler wait buckets、binary/optimizer bundle 和 next-batch replay。

| 口径 | 证据等级 | 面试安全表达 |
| --- | --- | --- |
| UWM/OPD 的 ZeRO/offload 配置 | local-direct | 存在配置或设计 hook |
| checkpoint save/load report | local-direct + report-supported path | 有 metadata/report；binary 不在当前 snapshot |
| activation checkpoint 机制能降低 activation 驻留 | primary mechanism | 机制上可行；本地幅度待 profile |
| CPU/NVMe offload 提高吞吐 | unverified | 没有 matched A/B，不能说 |
| offload 后可无损中途恢复 | unverified | 没有 optimizer/RNG/sampler/fixed-batch smoke，不能说 |

## 10. Trade-off、bad case 与追问

### 10.1 常见 trade-off

- activation checkpoint 减少显存，但重算可能让 step time 上升；随机状态保存还会增加开销。
- CPU offload 释放 GPU，但 CPU optimizer、PCIe/NVLink copy 和 pinned-memory 管理可能成为新瓶颈。
- NVMe offload 扩大容量，但 queue、带宽、buffer/prefetch 和 I/O overlap 决定实际结果。
- ZeRO 分片/offload 降低单卡 state，但 gather/partition 与 external parameter 访问增加系统复杂度。

### 10.2 高概率 bad case

1. 只看到 peak GPU memory 下降，就宣称吞吐提升。
2. 把 activation checkpointing 和 optimizer/parameter offload 混为同一个开关。
3. 用不同 effective batch、warm-up 或 world-size 做 A/B。
4. `checkpoint.load()` 成功就宣称 optimizer、RNG、sampler 和下一批样本都恢复。
5. 只比较 final loss，不检查 overflow、gradient、action denorm 和 controller roundtrip。
6. 把 DeepSpeed 文档中“支持 CPU/NVMe”写成当前项目已经完成 NVMe benchmark。

### 10.3 面试追问顺序

1. 你的峰值显存具体由哪一项占主导？
2. 为什么不用 checkpoint，而是 offload？
3. CPU/NVMe 的 copy/I/O 是否与计算 overlap？怎么测？
4. A/B 如何固定 effective batch 和测量窗口？
5. offload checkpoint 如何证明下一批数据、optimizer 和 RNG 都一致？
6. 如果显存下降 30% 但 p95 step time 上升，是否接受？取决于什么 deployment/training constraint？

## 11. 结论与下一步

面试中的完整回答应形成一条证据链：先做显存账本，区分 activation 与 model state；再选 checkpoint、CPU offload 或 NVMe hierarchy；最后用 matched A/B 同时报 memory、step-time、parity、resume 和 VLA closed-loop contract。PyTorch/DeepSpeed 官方文档支持这些机制的语义，不替代本地 workload benchmark。

当前节点已完成知识页和一张 `unseen` 题卡；仍保持 `WARN`，因为本地没有 checkpoint binary、matched throughput A/B 或 fixed-next-batch replay。下一步可以进行 ENG-015 一题口述或补本地 artifact；ENG-016 student + multiple teachers 继续后置。

## References

1. PyTorch 2.13，[torch.utils.checkpoint](https://docs.pytorch.org/docs/2.13/checkpoint.html)：activation recompute、`use_reentrant`、RNG preservation 与 determinism 边界。
2. PyTorch 2.13，[Fully Sharded Data Parallel](https://docs.pytorch.org/docs/2.13/fsdp.html)：`CPUOffload`、参数/梯度归属、CPU optimizer 与限制。
3. Microsoft DeepSpeed，[`activation-checkpointing.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/activation-checkpointing.rst)：activation partitioning、CPU checkpointing、contiguous memory optimizations 与 RNG tracker。
4. Microsoft DeepSpeed，[`zero3.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst)：ZeRO stages、CPU/NVMe offload、memory-centric tiling 与 assumptions。
5. ZeRO-Offload，[arXiv:2101.06840](https://arxiv.org/abs/2101.06840)：CPU offload 论文背景。
6. ZeRO-Infinity，[arXiv:2104.07857](https://arxiv.org/abs/2104.07857)：CPU/NVMe hierarchy 论文背景。
7. 本仓库，[ENG-015 Source Freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html) 与 [ENG-004..006 Local Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)。
