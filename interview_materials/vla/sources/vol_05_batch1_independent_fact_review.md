# VOL 05 Batch 1：独立官方文档事实复核

> 状态：`reviewed_slice / WARN`  
> 复核日期：2026-07-17  
> 证据截止：2026-07-17  
> 复核范围：`VLA-ENG-003..006` 的知识页、对应题卡，以及 DDP、FSDP、ZeRO、AMP、Distributed Checkpoint、Reproducibility 官方文档。  
> 结论先行：分布式同步/分片、AMP unscale/clipping/accumulation、DCP load-time reshard 和“固定 seed 不保证跨版本/平台复现”均有官方文档支持；吞吐分解、checkpoint lineage、RNG/data cursor、项目数字与个人 ownership 仍是本仓库工程框架或本地证据边界。

## 问题（Question）

本记录回答：VOL 05 Batch 1 中哪些训练工程断言可以回到独立官方来源？哪些说法只是实现推断或面试设计框架？是否需要对题卡/知识页做最小修订？

本次复核只读取冻结版本的官方 HTML，不执行训练、分布式作业、checkpoint resume 或性能 benchmark；因此“官方机制已核对”不等于“本地 workload 已复现”。

## 复核方法与证据等级

| 等级 | 含义 | 允许的面试口径 |
| --- | --- | --- |
| `official-checked` | 直接读取版本化官方文档的 API/机制原文 | “PyTorch 2.13 文档说明……” |
| `official-tutorial-checked` | 直接读取第一方 tutorial 的阶段定义或示例 | “DeepSpeed 官方 tutorial 将……定义为……” |
| `framework` | 本仓库的工程分解、验收顺序或诊断建议 | “我会这样拆分/验收……” |
| `inference` | 从每进程/每 rank 的实现语义推导出的结果 | “通常意味着……但不是 API 保证” |
| `blocked` | 需要本地运行、checkpoint、性能 trace 或 ownership 才能证明 | 不升级为本地结果 |

所有 PyTorch 来源固定到 `docs/2.13/` 路径，读取日期为 2026-07-17；页面在读取时的 `Last-Modified` 为 2026-07-16 或 2026-07-17。DeepSpeed 页面没有版本化路径，使用读取日期与响应摘要作为边界。

## 1. DDP：官方保证的是 replica 上的 gradient synchronization

PyTorch 2.13 的 `DistributedDataParallel` 文档明确说：DDP 在每个 model replica 之间同步梯度；它不会替用户切分或 shard 输入，输入切分应由 `DistributedSampler` 等上层逻辑负责。文档还写明参数不会在进程间持续 broadcast，而是对梯度做 all-reduce，并假设各进程的 optimizer 以相同方式修改参数；buffers（例如 BatchNorm 统计量）则由 rank 0 在每次迭代 broadcast。[1]

这直接支持题卡 `VLA-ENG-004` 的“DDP 复制模型、反向同步梯度、输入切分由用户负责”。但“每卡复制 optimizer state”是每进程各自构造 optimizer 的常见实现推论，不是 DDP 通信 API 本身保证的对象。因此题卡短答应说“通常各 rank 独立持有 optimizer state”，不要把它写成 DDP 内部的同步协议。

## 2. FSDP：sharding strategy 决定 all-gather、reduce-scatter 与 reshard 时机

PyTorch 2.13 FSDP 文档把 `FULL_SHARD` 与 `SHARD_GRAD_OP` 的差异写得很具体：两者都在 backward 后对 gradient 做同步/分片，并由每个 rank 本地更新 sharded optimizer state；`FULL_SHARD` 在 forward/backward 周围更积极地 reshard 参数，而 `SHARD_GRAD_OP` 在 forward 后保留 unsharded parameters，到 backward 结束后才重新分片。[2]

文档还把 all-gather/reduce-scatter 作为 FSDP process group 的核心 collective，并提示 sharding strategy 会在显存节省与通信开销之间取舍。[2] 因此知识页中“按 wrap/shard policy 分片、靠 unit-level all-gather/reduce-scatter 执行”的说法是 source-consistent；但具体 peak memory、step time、wrap policy 和 tied-weight 行为仍需 workload 级测试。

## 3. ZeRO：Stage 1/2/3 的分片对象已由官方 tutorial 直接定义

DeepSpeed 官方 ZeRO tutorial 将训练状态分为 weights、gradients、optimizer states，并定义：Stage 1 分片 optimizer states；Stage 2 在此基础上分片 reduced gradients；Stage 3 进一步分片 model parameters，并在 forward/backward 中自动收集和重新分区。[3]

这直接支持 `VLA-ENG-004` 的阶段表。它不支持“Stage 3 对所有 VLA workload 最优”，也不替代通信、offload、checkpoint 保存/加载和多 teacher 共存的实测。OPD 的 `preloaded_zero3` 只能作为显存压力的项目 hook，不能升级为通用性能结论。

## 4. AMP：unscale、clipping 与 accumulation 的顺序有直接官方依据

PyTorch AMP examples 将 `autocast` 与 `GradScaler` 作为常见 mixed-precision 组合，并明确指出：如果要做 gradient clipping，应先对 optimizer 调用 `scaler.unscale_(optimizer)`，否则 norm 或 maximum magnitude 仍处于 scale 后的数值，clip threshold 语义会错误。[4]

同一页对 gradient accumulation 给出更强的约束：effective batch 是 `batch_per_iter × iters_to_accumulate`（分布式时再乘进程数）；在一个 effective batch 内，梯度应保持 scaled，scale factor 保持不变；inf/NaN 检查、step skip 和 scale update 应在 effective-batch 粒度发生。[4]

因此 `VLA-ENG-005` 的核心顺序是 `backward → accumulate → unscale → global norm/clipping → optimizer.step/update`。scheduler 按 micro step 还是 optimizer step、variable-length 样本按 sample/token/frame/action 计，则是训练合同，需要由项目配置与日志明确，不能伪装成 AMP API 的默认答案。

```python
def amp_accumulation_step(micro_batches, model, optimizer, scaler, clip_norm):
    # Keep gradients scaled and accumulate across the whole effective batch.
    for batch in micro_batches:
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            loss = model.loss(batch) / len(micro_batches)
        scaler.scale(loss).backward()

    # Only now unscale, inspect/clip unscaled gradients, and update once.
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), clip_norm)
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

代码是面试用的最小顺序示意，不代表每个 VLA trainer 的完整实现；分片 optimizer、多个 optimizer、梯度检查和 scheduler 仍需按框架合同补充。

## 5. Distributed Checkpoint：load-time reshard 是官方能力，lineage bundle 不是

PyTorch 2.13 Distributed Checkpoint 文档明确写明：DCP 支持从多个 rank 并行保存/加载，并支持 load-time reshard，因此 checkpoint 可以在一种 cluster topology 保存、另一种 topology 加载；其 checkpoint 通常由多个文件组成，而不是单一 `torch.save` 文件。[5]

这支持知识页 `VLA-ENG-006` 中“分布式 checkpoint 要明确 full/sharded state dict、world-size reshard、rank ownership”的机制提醒。但 `run_id + git SHA + config/env + processor + normalizer + optimizer/scheduler/scaler + RNG + sampler/data cursor + eval manifest` 是本仓库建议的 lineage bundle，不是 DCP 自动保存或验证的完整字段集合。必须把“DCP 能重分片加载”和“训练实验可审计、可无缝 resume”分开回答。

## 6. Reproducibility：固定 seed 不是充分条件

PyTorch 2.13 Reproducibility 文档直接警告：跨 PyTorch release、不同 commit、不同平台，以及 CPU/GPU 之间，即使使用相同 seed，也不保证完全复现；文档建议控制随机源、配置 deterministic 算法，但 deterministic 操作往往更慢。[6]

因此知识页中的“kernel、数据顺序、环境和 simulator 同样属于合同”是合理的工程扩展；“只固定随机种子即可复现”应继续列为危险答案。这个来源只证明 PyTorch 侧的可复现性边界，不证明任何 UWM/OpenPiVLA/Harness run 已复现。

## 7. 逐节点复核矩阵

| 节点 | 独立结果 | 可直接支持的内容 | 不可由该来源支持的内容 |
| --- | --- | --- | --- |
| `VLA-ENG-003` | `FRAMEWORK / SOURCE-CONSISTENT` | data/compute/sync/misc 的 timing 分解与 A/B 诊断顺序 | 某个项目的实际吞吐提升比例 |
| `VLA-ENG-004` DDP | `PASS WITH WARNING` | replica、gradient all-reduce、输入不自动 shard；optimizer state 需标 inference | 当前 workload 的显存/通信最优 |
| `VLA-ENG-004` FSDP | `PASS` | sharding strategy、all-gather/reduce-scatter、reshard 时机 | 当前 wrap policy 的峰值显存与速度 |
| `VLA-ENG-004` ZeRO | `PASS` | Stage 1/2/3 的分片对象 | 多 teacher、offload 与恢复的项目收益 |
| `VLA-ENG-005` | `PASS WITH WARNING` | autocast/GradScaler、unscale 后 clipping、effective-batch accumulation | scheduler 选择、variable-length workload 与 BF16 项目稳定性 |
| `VLA-ENG-006` | `PASS WITH WARNING` | DCP 并行保存/加载与 load-time reshard | lineage 完整、sampler cursor 恢复、固定 batch 输出相等 |
| `VLA-ENG-013` 预览 | `PASS WITH WARNING` | seed 不是跨 release/platform 的充分复现条件 | 本地训练已经 deterministic |

## 8. 最小回写与真实性边界

本次发现一处需要最小回写的措辞风险：`VLA-ENG-004` 题卡短答把“DDP 每卡复制完整训练状态”说得像 DDP API 的直接保证。应改为“DDP 每卡复制模型参数，梯度 all-reduce；optimizer state 通常由各 rank 独立持有”，并在知识页补充“optimizer state 是每进程 optimizer 的实现推论”。其余 9 张 Batch 1 题卡不需要因本次官方复核改写核心机制。

项目 hook 继续沿用 evidence inventory：OpenPiVLA remote path、UWM raw checkpoint、OPD `preloaded_zero3`、Harness scorer 等只能作为追问入口；本次官方文档复核不升级任何个人贡献、项目数字、部署延迟或真机闭环结论。

## 复核结论

本批分布式训练/AMP/checkpoint 的核心机制已达到 `official-checked` 或 `official-tutorial-checked`；吞吐、lineage、resume 验收和项目结果继续保持 `framework`/`blocked`。总体 verdict 仍为 `WARN`，因为本地 runtime artifacts、跨 world-size resume smoke、性能 A/B、浏览器视觉 QA 和候选人口述尚未完成。

## 参考文献（References）

1. PyTorch 2.13, [DistributedDataParallel](https://docs.pytorch.org/docs/2.13/generated/torch.nn.parallel.DistributedDataParallel.html)，读取日期 2026-07-17；响应 SHA-256 `6895c721fe7e483fa473d30afba5e0666723c7a5e144078c329eb91ee383bdd4`。
2. PyTorch 2.13, [FullyShardedDataParallel](https://docs.pytorch.org/docs/2.13/fsdp.html)，读取日期 2026-07-17；响应 SHA-256 `d188ded37aec986272a6cefadb0d8eb1316030303c2069ab7b5abc71397e00b9`。
3. DeepSpeed official, [ZeRO tutorial](https://www.deepspeed.ai/tutorials/zero/)，读取日期 2026-07-17；响应 SHA-256 `32e2b242be5088e4e64d9cc2d03e553b4fdea7d0116c4e84eeee5eca282d653f`。
4. PyTorch 2.13, [Automatic Mixed Precision examples](https://docs.pytorch.org/docs/2.13/notes/amp_examples.html)，读取日期 2026-07-17；响应 SHA-256 `41b26df690e71e7a83d6ec1a62e47c776051978e319c6da31c355fa5adaa6a59`。
5. PyTorch 2.13, [Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html)，读取日期 2026-07-17；响应 SHA-256 `c55275fd489a912f657fd528ea066bd1cfaf843a14889db04fb442b088d34b12`。
6. PyTorch 2.13, [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)，读取日期 2026-07-17；响应 SHA-256 `cebd51bee8f3286d36db9a3ee2dba3ef7e1a46fd351269d59fc127ea8dac0966`。
7. 本仓库 [VOL 05 Batch 1 知识页](../knowledge/vol_05_engineering_eval.html) 与 [10 张题卡](../questions/vol_05_engineering_eval.html)。
8. 本仓库 [项目 Evidence Manifest](../evidence/evidence_manifest.html) 与五项目 claim–evidence inventories。
