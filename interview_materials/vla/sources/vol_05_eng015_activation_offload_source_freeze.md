# VOL 05 ENG-015：Activation Checkpointing、CPU/NVMe Offload 与吞吐来源冻结

> 审计日期：2026-07-17  
> 状态：`source_frozen / VLA-ENG-015_knowledge+card_drafted / WARN`  
> 对应问题：`VLA-ENG-015`——显存不够时，activation checkpointing、CPU/NVMe offload 和吞吐之间如何取舍？  
> 当前边界：本文件冻结官方语义、版本/commit 和本地项目 hook；ENG-015 知识正文与一张 `unseen` 题卡已生成，matched A/B benchmark 与真实 resume 验证仍后置，不把配置文件写成已经获得的性能收益。

## 1. 问题与最小范围（Question / Scope）

本切片只回答五个面试准备问题：

1. activation checkpointing 为什么能降低 activation 峰值，它付出的重算和 RNG/determinism 成本是什么？
2. FSDP CPU offload、DeepSpeed ZeRO-Offload/ZeRO-Infinity 分别搬运哪些 state，为什么它们不是同一个机制？
3. CPU 与 NVMe offload 的带宽、延迟、CPU 内存和 I/O buffer 如何进入 step-time 账本？
4. 当显存下降但吞吐也下降时，怎样设计可复现、可回归的 A/B 协议？
5. 结合 UWM/OPD 本地证据，哪些只能说“配置或设计存在”，哪些才足以说“显存/吞吐/恢复得到验证”？

本页不声称某个项目已经从 activation checkpointing、CPU offload 或 NVMe offload 获得吞吐提升；不把能保存/加载 metadata 说成完整 resume，也不把 ZeRO 配置说成对应 run 已经执行。

## 2. 证据类型与冻结输入

HTML 页面使用仓库统一规范化：HTTP GET 后移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256。DeepSpeed GitHub 文件使用冻结 commit 上的 raw Markdown/RST bytes SHA-256。连续 GET 的官方 HTML 可能含动态资源，不把 raw HTML SHA 当版本号。

| 输入 | 类型 | 版本 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| PyTorch activation checkpoint | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | 不保存全部 forward intermediates，backward 时按需 recompute；计算换显存；`use_reentrant` 两种实现、RNG preservation 与函数前后不一致风险 | 任何模型都无损、无额外延迟，或跨后端 bitwise identical |
| PyTorch FSDP | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | `CPUOffload(offload_params=True)` 的参数/梯度 CPU offload 语义；optimizer step 在 CPU；CPU-offload 下 gradient accumulation 限制 | NVMe offload、任意 PCIe/NVLink 带宽或项目吞吐 |
| DeepSpeed activation checkpointing | official-code / official-doc source | `microsoft/DeepSpeed@de1846cf6fbdd6f1c2adf046f319791ca78cc547` | activation partitioning、CPU checkpointing、contiguous memory optimizations 的 API 入口；checkpoint function 与 CUDA RNG tracker | 某个 VLA 模型已经启用这些选项，或已经提升 tokens/s |
| DeepSpeed ZeRO-3 / Infinity | official-code / official-doc source | 同上 frozen commit | ZeRO 分片 optimizer/gradient/parameter；ZeRO-Offload 的 CPU state；ZeRO-Infinity 的 CPU/NVMe state、overlap/带宽目标和配置入口 | NVMe 实测带宽、I/O 无阻塞、端到端吞吐提升或恢复正确 |
| ZeRO-Offload paper | primary / paper | [arXiv:2101.06840](https://arxiv.org/abs/2101.06840) | CPU offload 作为系统设计问题和内存扩展方向的论文背景 | 当前项目的实现、硬件和指标 |
| ZeRO-Infinity paper | primary / paper | [arXiv:2104.07857](https://arxiv.org/abs/2104.07857) | CPU/NVMe hierarchy、memory capacity 与 bandwidth utilization 的研究背景 | 当前机器的 NVMe 设备、buffer/prefetch 参数或 VLA 结果 |
| 本地 ENG-004..006 artifact gate | local-evidence | 本仓库 `sources/vol_05_local_artifact_gate_eng004_006.md` | UWM/OPD 的 DeepSpeed/ZeRO 配置、训练 summary、load report、final-only/no-optimizer-state 边界 | checkpoint binary、optimizer/RNG/sampler lineage、fixed-batch resume、matched throughput A/B |

### 2.1 官方来源 normalized / raw 指纹

| 来源 | URL | 指纹类型 | 长度 | SHA-256 |
| --- | --- | --- | ---: | --- |
| PyTorch checkpoint | [2.13/checkpoint.html](https://docs.pytorch.org/docs/2.13/checkpoint.html) | normalized main text | 16775 | `ac47e4a48f1e17f17cf485083059c6b0b7b30fd4d883dff0aca1f6d429a9e681` |
| PyTorch FSDP | [2.13/fsdp.html](https://docs.pytorch.org/docs/2.13/fsdp.html) | normalized main text | 61919 | `9f14bed9d2267151f21bd7c0a61007e25f7443e877ab16a047fd29a28aa87810` |
| DeepSpeed activation checkpointing | [activation-checkpointing.rst](https://raw.githubusercontent.com/microsoft/DeepSpeed/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/activation-checkpointing.rst) | raw RST bytes | 1307 | `9ce53eea54425e30376159448d045f5748c898f9a2d5ad45f80ab2f738e1a590` |
| DeepSpeed ZeRO-3 / offload | [zero3.rst](https://raw.githubusercontent.com/microsoft/DeepSpeed/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst) | raw RST bytes | 22955 | `e8eeb0ccfd067c371e522b494d70e0a233e7aeda4d5ccf6dd1a200d01a4b6847` |

## 3. 先分清四种“搬运/省显存”

| 机制 | 主要对象 | 发生时机 | 省下的是什么 | 典型代价/风险 |
| --- | --- | --- | --- | --- |
| activation checkpointing | forward 中间激活 | backward 前后按需重算 | 不长期保存的 activation | 额外 FLOPs、重算延迟、随机函数/RNG 状态处理、非纯函数可能错梯度 |
| FSDP CPU offload | FSDP 参数；`offload_params=True` 时梯度也到 CPU | 参数不参与计算时、梯度归约后 | GPU 参数/梯度驻留 | CPU↔GPU copy、CPU optimizer step；CPU-offload 下 gradient accumulation 约束 |
| ZeRO-Offload | ZeRO-2 的 optimizer/gradient state | 训练 step 的 state update 路径 | GPU optimizer/gradient state | CPU 内存、host compute 和传输；不是 activation recompute |
| ZeRO-Infinity | ZeRO-3 的参数/optimizer/gradient，可到 CPU/NVMe | gather/partition/offload 生命周期 | GPU + CPU 容量扩展 | NVMe latency/bandwidth、buffer/prefetch、I/O overlap 和调度复杂度 |

面试中的安全句式是：**“我先标记是哪一类 tensor 被搬走或不保存，再单独测显存峰值、step time 和数值/恢复；省 GPU memory 不等于吞吐提升。”**

## 4. 官方语义核对

### 4.1 PyTorch activation checkpointing：以重算换激活存储

PyTorch 2.13 把 activation checkpointing 定义为一种 **compute-for-memory trade-off**：正常 forward 的 tensors 会保留到 backward 使用；checkpoint 区域不保留未指定的 tensors，而是在 backward 中重新调用函数得到所需值。官方页面还说明 `use_reentrant=False` 是推荐实现，并警告 checkpointed function 若 forward/backward 行为不一致，可能报错或产生静默错误梯度。

RNG 不是免费细节。默认逻辑会保存并恢复 CPU 与一个设备类型的 RNG state；`preserve_rng_state=False` 可以省掉这部分开销，但如果 checkpoint 区域包含随机操作，就不应把结果自动当成与未 checkpoint 版本等价。多设备场景只保存一个设备类型的 state 也构成边界，因此随机增强、dropout 和后端差异要进入验证矩阵。

### 4.2 FSDP CPU offload：参数/梯度的 CPU 归属

PyTorch 2.13 的 `CPUOffload(offload_params=False)` 语义是：`offload_params=True` 时，未参与计算的参数移到 CPU，梯度也 offload 到 CPU，因此 optimizer step 在 CPU 执行。FSDP 页面同时列出 CPU-offload 的限制：不能把普通 gradient accumulation（`no_sync()` 之外）当作无条件支持的行为，因为归约后的梯度处理方式可能导致错误结果。

这说明 CPU offload 不是简单的 `tensor.to("cpu")`：参数生命周期、梯度归约、optimizer device 和同步点必须一起设计。FSDP 的 sharding strategy、wrap policy 和通信/计算 overlap 也会改变性能；所以只能在固定 world-size、wrap、dtype 和 batch 下做 A/B。

### 4.3 DeepSpeed activation checkpointing：额外的激活级选项

冻结的 DeepSpeed `activation-checkpointing.rst` 明确列出 activation partitioning（在 model parallel GPU 间分区）、CPU checkpointing、contiguous memory optimizations 等 API 能力，并提供 `configure`、`checkpoint`、`reset` 与 CUDA RNG tracker。它支持我们把“激活级省显存”作为单独实验因素，但不支持把配置存在写成某个本地 run 已启用，更不支持性能结论。

### 4.4 ZeRO-Offload 与 ZeRO-Infinity：state hierarchy，不是 activation checkpoint

冻结的 DeepSpeed `zero3.rst` 将 ZeRO 定义为在 data-parallel processes 间分区 optimizer states、gradients、parameters：Stage 1/2/3 依次增加分区对象。该页进一步说明：ZeRO-Offload 在 ZeRO-2 中把 optimizer 与 gradient states offload 到 CPU；ZeRO-Infinity 在 ZeRO-3 上扩展到更多 model states，并可使用 CPU 与 NVMe memory。配置示例含 `offload_optimizer.device=cpu|nvme`、`offload_param.device=cpu|nvme` 及 `nvme_path`。

同一页还强调了代价边界：ZeRO-Infinity 的目标包含更有效的带宽利用和计算/通信 overlap，但这不是对任意硬件、模型或 batch 的吞吐承诺；ZeRO-3 的 forward/backward 仍要求子模块单独 fit device memory，参数 gather/partition/offload 的粒度和 external parameter 访问规则也会影响工程实现。

## 5. 显存账本与吞吐账本

### 5.1 显存账本

对一个训练 step，可把峰值显存拆成可审计的近似账本：

\[
M_{\mathrm{peak}} \approx M_{\mathrm{param}}+M_{\mathrm{grad}}+M_{\mathrm{optim}}+M_{\mathrm{act}}+M_{\mathrm{temp}}+M_{\mathrm{teacher}}+M_{\mathrm{fragment}}
\]

变量分别是参数、梯度、optimizer state、activation、temporary buffer、teacher/model ensemble 和 allocator fragmentation。activation checkpointing 主要作用于 (M_{\mathrm{act}})；CPU/NVMe offload 主要改变某些参数/梯度/optimizer state 在 GPU、CPU、NVMe 之间的归属，不会自动消除 temporary buffer、通信峰值或 fragmentation。这个账本是工程分解，不是官方单一公式。

### 5.2 吞吐账本

对固定有效 batch 的每 step 时间，可先写成：

\[
T_{\mathrm{step}} = T_{\mathrm{data}} + T_{\mathrm{fwd}} + T_{\mathrm{recompute}} + T_{\mathrm{bwd}} + T_{\mathrm{copy}} + T_{\mathrm{comm}} + T_{\mathrm{io}} + T_{\mathrm{sync}}
\]

其中 (T_{\mathrm{recompute}}) 是 checkpoint 新增的计算，(T_{\mathrm{copy}}) 是 CPU↔GPU 传输，(T_{\mathrm{io}}) 是 NVMe 读写和 queue 等待，(T_{\mathrm{comm}}) 是 sharding/offload 相关通信，(T_{\mathrm{sync}}) 是必须等待的同步。吞吐 (S=\text{effective samples}/T_{\mathrm{step}}) 只有在 effective batch、数据、world-size、warm-up、precision 和评估协议相同的 A/B 中才可比较。

### 5.3 何时选择哪种机制

| 症状 | 优先实验 | 需要监控 | 不应直接推出 |
| --- | --- | --- | --- |
| activation 峰值高、参数/optimizer 尚可 | activation checkpointing | peak allocated/reserved、recompute time、RNG/determinism、step time | “一定更快” |
| 参数/梯度/optimizer 占满 GPU，但 CPU 内存充足 | FSDP CPU offload 或 ZeRO-Offload | GPU/CPU memory、copy time、optimizer step、gradient accumulation 语义 | “activation 也被 offload” |
| 模型 state 总量超过 CPU 可承受范围、NVMe 较快 | ZeRO-Infinity / NVMe offload | NVMe bandwidth、queue depth、buffer hit、I/O wait、overlap ratio | “NVMe 能把吞吐保持不变” |
| 多 teacher 或 action expert 造成临时峰值 | 先做 live-state/temporary-buffer ledger，再考虑分阶段 offload | teacher residency、peak timeline、通信和同步 | “只调 batch size 就解决” |

## 6. 最小 A/B 验证矩阵

每一行至少固定：`run_id`、code/commit、framework、world-size、backend、model/optimizer state、dataset/transform manifest、effective batch、dtype、sequence/action horizon、checkpoint policy、offload device、activation checkpoint segments、warm-up、measurement window。

| 维度 | baseline | candidate | 验收字段 |
| --- | --- | --- | --- |
| activation | off | non-reentrant checkpoint，固定 segment | peak GPU、recompute ms、loss/grad parity |
| state offload | off | FSDP CPU / ZeRO CPU / ZeRO NVMe | GPU/CPU/NVMe memory、copy/I/O wait、optimizer step |
| numeric | same seed/input | same seed/input | forward/gradient relative error、overflow、scaler state |
| throughput | same effective batch | same effective batch | warm-up 后 p50/p95 step ms、samples/s、data_wait/comm/io breakdown |
| checkpoint | full bundle | full bundle + offload metadata | binary hash、optimizer/scheduler/scaler/RNG/sampler、fixed next-batch smoke |
| workload | same VLA protocol | same VLA protocol | action shape/normalizer/parser/controller roundtrip、closed-loop metric |

相对误差可用下面的工程指标先做汇总：

\[
e_{\mathrm{rel}}=\frac{\lVert y_{\mathrm{candidate}}-y_{\mathrm{baseline}}\rVert_2}{\max(\lVert y_{\mathrm{baseline}}\rVert_2,\epsilon)}
\]

这里 (y) 可以是 forward 输出、gradient 或归一化后的 action；(epsilon) 防止零范数。容差要按 dtype、算子和任务协议声明，不能把不同 backend 的浮点结果要求成字节级相同。

## 7. 最小验证伪代码（工程合同，不是 upstream 实现）

```python
def compare_memory_throughput(baseline_cfg, candidate_cfg, fixed_requests):
    # 1. Freeze the code/data/env/effective-batch contract before changing memory policy.
    base = launch_run(baseline_cfg, fixed_requests, warmup=10)
    cand = launch_run(candidate_cfg, fixed_requests, warmup=10)

    # 2. Record peak memory and every wait bucket, not only a final samples/s number.
    base_metrics = collect_metrics(base, fields=["peak_gpu", "cpu_mem", "nvme_io", "recompute", "step_ms"])
    cand_metrics = collect_metrics(cand, fields=["peak_gpu", "cpu_mem", "nvme_io", "recompute", "step_ms"])

    # 3. Compare fixed-request outputs, gradients and overflow/scaler state with declared tolerances.
    parity = compare_fixed_batch(base, cand, tolerance=candidate_cfg.tolerance)

    # 4. A memory reduction without matched throughput/parity/resume evidence stays WARN.
    resume = fixed_next_batch_resume_smoke(cand, fixed_requests)
    return summarize(base_metrics, cand_metrics, parity, resume)
```

伪代码表达验证顺序：先固定 workload，再记录峰值/等待分解，再做数值和恢复 smoke。它不实现 PyTorch、FSDP 或 DeepSpeed 的具体 API，也不替代真实 profiler、NVMe telemetry 或 closed-loop eval。

## 8. 本地项目证据与口径边界

本仓库 [ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html) 盘点到：

- UWM 有训练 summary、world-size/DeepSpeed 配置、action normalizer 和 checkpoint load report；effective config 中有 `zero_optimization.stage=0` 的记录。
- OPD 有 ZeRO-2/3 配置和 final-only/no-optimizer-state manifest；配置证明存在，不证明对应 run 已完成或性能更好。
- 当前扫描没有 `.pt/.pth/.ckpt/.safetensors/.bin` checkpoint binary，也没有 optimizer/scheduler/scaler/RNG/sampler lineage、fixed-batch continuation 或 matched throughput A/B。

因此在面试中可以说：

> “我会先把显存账本拆成 activation、参数、梯度、optimizer、teacher 和临时 buffer，再决定 checkpoint 或 state offload。当前项目证据能支持我讨论 UWM/OPD 的配置和恢复风险，但还不足以声称 activation checkpointing/NVMe offload 已带来吞吐提升或完整 resume；下一步要补固定 effective batch 的 A/B、同步 profiler、binary/optimizer bundle 和 next-batch replay。”

| 口径 | 证据等级 | 安全表达 |
| --- | --- | --- |
| UWM/OPD 的 offload/ZeRO 配置 | local-direct | “存在配置或设计 hook” |
| checkpoint/load report | local-direct + report-supported path | “有 metadata/report；binary 不在当前 snapshot” |
| activation checkpointing 降低 activation 峰值 | primary mechanism | “机制上可降低保存的 activation；需要本地 profile 验证幅度” |
| CPU/NVMe offload 提高吞吐 | unverified | 没有 matched A/B，不能说 |
| offload 后可无损中途恢复 | unverified | 没有 optimizer/RNG/sampler/fixed-batch smoke，不能说 |

## 9. Gate、风险与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| PyTorch activation checkpoint 语义 | `PASS WITH WARNING` | 后续知识页保留 recompute、RNG、reentrant/non-reentrant 边界 |
| FSDP CPU offload 语义 | `PASS WITH WARNING` | 明确参数/梯度 CPU 归属、CPU optimizer 与 accumulation 限制 |
| DeepSpeed activation checkpointing | `PASS WITH WARNING` | 以 frozen commit 为准；不把旧 404 tutorial 当来源 |
| ZeRO-Offload / Infinity | `PASS WITH WARNING` | 区分 CPU/NVMe state offload 与 activation checkpoint；记录 I/O/overlap 待实测 |
| memory/throughput protocol | `PASS` | 后续知识页使用固定 effective batch、warm-up、p50/p95 与 wait buckets |
| local project evidence | `WARN` | 补 binary、optimizer lineage、fixed-batch resume 和 matched A/B 后再升级 claim |
| knowledge/card | `DRAFTED / UNSEEN` | 保持题卡 `unseen`；后续补 matched A/B、binary/lineage 和 fixed-next-batch replay；ENG-016 保持后置 |

## 参考来源（References）

1. PyTorch 2.13，[torch.utils.checkpoint](https://docs.pytorch.org/docs/2.13/checkpoint.html)：activation recompute、`use_reentrant`、RNG preservation 与 determinism 边界。
2. PyTorch 2.13，[Fully Sharded Data Parallel](https://docs.pytorch.org/docs/2.13/fsdp.html)：`CPUOffload`、参数/梯度归属、CPU optimizer 与限制。
3. Microsoft DeepSpeed，[`activation-checkpointing.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/activation-checkpointing.rst)，冻结 commit `de1846cf6fbdd6f1c2adf046f319791ca78cc547`。
4. Microsoft DeepSpeed，[`zero3.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst)，ZeRO stages、CPU/NVMe offload 与 memory-centric tiling。
5. Rajbhandler et al.，[ZeRO-Offload](https://arxiv.org/abs/2101.06840)，CPU offload 论文背景。
6. Rajbhandler et al.，[ZeRO-Infinity](https://arxiv.org/abs/2104.07857)，CPU/NVMe hierarchy 论文背景。
7. 本仓库，[VOL 05 ENG-004..006 Local Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)，UWM/OPD 配置、report 与 binary/resume/throughput 缺口。
