# VOL 05 ENG-012：HDF5 / Zarr / WebDataset / Parquet 来源冻结

> 状态：`source_frozen / VLA-ENG-012_knowledge+card_drafted / unseen / WARN`  
> 冻结日期：2026-07-17  
> 对应问题：`VLA-ENG-012`——HDF5、Zarr、WebDataset、Parquet 的访问模式和取舍是什么？  
> 当前边界：本文件只冻结来源与 claim contract；下游[知识正文](../knowledge/vol_05_engineering_eval_eng012.html)与[单张题卡](../questions/vol_05_engineering_eval_eng012.html)已生成，项目性能结论和掌握状态仍后置。  
> 前置切片：[VOL 05 Batch 2A 独立事实复核](vol_05_batch2a_independent_fact_review.html)。

## 1. 为什么不能做“格式排行榜”

这四个名字不完全处于同一抽象层：

- HDF5 / Zarr 主要提供 N 维数组、chunk、compression 和层级元数据。
- WebDataset 是以 tar shard 组织样本、面向顺序流式读取的 dataset representation / pipeline。
- Parquet 是 column-oriented table format，以 row group、column chunk、page 组织结构化/嵌套列。

因此 `VLA-ENG-012` 的安全问题不是“哪个格式最好”，而是：给定 VLA workload 的随机窗口、顺序 epoch、对象存储、列扫描、媒体 decode、worker 数与恢复边界，哪种布局减少了实际 I/O amplification，并且如何用 matched benchmark 验证。

## 2. 冻结来源与版本

HTML 页面使用与上一 source review 相同的规范化：HTTP GET 后移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256。GitHub raw Markdown 使用原始 bytes SHA-256。

| 系统 | Primary source | 版本 / commit | 指纹 | License | 本轮使用范围 |
| --- | --- | --- | --- | --- | --- |
| HDF5 / h5py | [Datasets](https://docs.h5py.org/en/3.15.0/high/dataset.html) | h5py `3.15.0`；tag commit `4e8866a3d1af352add72014149d0810ee5543c48` | normalized text `a083daf7148d6aff3842bced69230c361c9507a71fc5b44ddfc7af3d7860ad3e`（22807 chars） | BSD-3-Clause style | contiguous/chunked layout、chunk read amplification、resize/compression |
| Zarr arrays | [arrays.md](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/arrays.md) | zarr-python `v3.2.1`；commit `85890b3bb404fd1d401267c508a2694f5734559e` | raw `a68767daf086a2305e0a5fcfeb7e813e768a5e352d265d422a7de6ec700a9cd7` | MIT | chunks、compressors、v3 sharding、read/write unit |
| Zarr storage | [storage.md](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/storage.md) | 同上 | raw `67d2b5e4b23172815ca3f3b0b0039d9ab8e06a9e11f5f415794b97b6d87f84fe` | MIT | Local/Fsspec/Zip/Memory/Object store 边界 |
| WebDataset | [README.md](https://raw.githubusercontent.com/webdataset/webdataset/e0953f9bba17b416d5792d5a263b171c266e78be/README.md) | commit `e0953f9bba17b416d5792d5a263b171c266e78be` | raw `99d918fb992a68b4bae908ab7e4ffcdad6f3e4e7de3bfd817077b9b7020c689e` | BSD-3-Clause | tar shard convention、sequential pipeline、pipe/object-store access、IterableDataset |
| Apache Parquet format | [parquet-format README](https://raw.githubusercontent.com/apache/parquet-format/21ecc2b0f5786070561ae0d34152230853c83e2b/README.md) | commit `21ecc2b0f5786070561ae0d34152230853c83e2b` | raw `692afb37e07e752376006765729794cf358b4aae0582aef6a42deff1f19ca7de` | Apache-2.0 | column-oriented format、row group/column chunk/page、metadata |
| Parquet Python access | [PyArrow Parquet](https://arrow.apache.org/docs/22.0/python/parquet.html) | Apache Arrow `22.0` docs | normalized text `0211e40bb1cd05e142e839b44daa957dbc0714c072ea5dd0f74432bf9b48fa7b`（28931 chars） | Apache-2.0 | read row group、multiple row groups、partitioned datasets |
| Parquet file layout | [official file-format page](https://parquet.apache.org/docs/file-format/) | rolling official page；核心语义由 frozen repo 交叉核对 | normalized text `1d35808adb95b1781761d2b431707b084cafb076b38f8e685edb0862c43a6bda`（1570 chars） | Apache-2.0 | metadata 与 column chunk 位置、列读取顺序 |

## 3. HDF5 / h5py：local array 与 chunk alignment

### 3.1 官方事实

h5py 3.15 文档说明：默认 Dataset 是 contiguous C-order layout；也可使用 chunked layout，把数据分为固定大小块并通过 B-tree 索引。chunking 支持 resize 与 compression。文档同时明确，即使只需要一个 chunk element，也会涉及整个 chunk；chunk shape 决定一次 selection 需要多少 chunk。

### 3.2 可推导的 VLA 含义

若样本读取是 episode 内连续时间窗，chunk shape 应与 `time × camera/state/action` 的常用 selection 对齐。可定义粗略 over-read amplification：

\[
A_{read}=\frac{\text{bytes fetched or decompressed}}{\text{bytes consumed by the sample}}.
\]

变量解释：分子是底层实际读取/解压量，分母是 batch 真正使用的数据量。公式是本仓库 profiling 指标，不是 HDF5 API 指标。chunk 太大可能扩大 over-read/decompression，太小可能增加索引、seek 和 metadata 开销；最终需本地 benchmark。

### 3.3 不能从当前来源推出

- HDF5 必然比 Zarr 快或慢。
- 单文件天然适合任意多进程/多机访问。
- `chunks=(...)` 写入后就自动适配 action window、camera 数与 worker pattern。

并发写、SWMR、MPI、文件锁和远端访问不是本切片审查范围；知识页不得用本来源做强并发结论。

## 4. Zarr：chunk、store 与 v3 sharding

### 4.1 官方事实

Zarr v3.2.1 文档展示 N 维数组按 chunk 切分，并支持 compressor。storage guide 明确支持 local、Zip、Fsspec remote、memory 与 object store。v3 sharding 用一个 storage object 容纳多个 chunk，解决超多小 chunk 对文件系统/对象存储的压力；文档明确：chunk 是独立读取单位，shard 是写入单位，写入时完整 shard 对性能和并发更重要。

### 4.2 可推导的 VLA 含义

- object store 上不能只看压缩率，还要记录每 sample request count、range/read size、metadata GET 和 retry。
- 小 chunk 能降低随机窗口 over-read，但可能制造 small-object / metadata storm；sharding 可减少对象数，却扩大写入单元。
- camera、time、height、width、action 维度的 chunk order 必须匹配常用 slice，不能只沿用默认值。

### 4.3 不能从当前来源推出

- Zarr 天生适合云端，因此任意 workload 都更快。
- sharding 必然减少端到端延迟。
- 同一个 chunk shape 可同时最优支持 sequential training、随机 debug 与在线 append。

这些结论都需要结合 store、cache、worker 和 selection 做 matched A/B。

## 5. WebDataset：tar shard 与顺序流

### 5.1 官方事实

冻结 README 将 WebDataset format 定义为 tar files：同一样本的成员共享 basename，tar shards 使用编号/brace notation。它可从 local disk 或 pipe 读取，并面向 object/cloud store；README 明确把核心 representation 定位为纯顺序 I/O pipeline，生成的 pipeline 是 PyTorch `IterableDataset`，并提供 shard/sample shuffle buffer。

### 5.2 可推导的 VLA 含义

- 适合已经预先打包成 sample 或 episode unit 的大规模顺序 epoch、远端 shard streaming。
- 若训练需要从一个超长 episode 任意抽取跨 frame/action 的随机窗口，必须在写 shard 时预切 sample、增加索引/旁路系统，或接受额外读放大；基本顺序 pipeline 不自动解决这个问题。
- shuffle quality 取决于 shard order、resampling 与 buffer，而不是 tar 格式自动提供全局均匀随机。

### 5.3 不能从当前来源推出

README 提到相对 random access 的 `3x–10x` local-drive I/O 提升，但这是项目 README 的概括，缺本轮 workload、硬件和 protocol；不得写成 VLA 通用 benchmark。也不能说 WebDataset 完全不支持随机访问——那会混淆基础 streaming API 与其他 indexed/WIDS 路径。

## 6. Parquet：列式表、row group 与元数据扫描

### 6.1 官方事实

Parquet format 是 column-oriented。一个 file 由 row groups 组成；每个 row group 对每列有一个 contiguous column chunk，column chunk 再分 pages。file metadata 保存 column chunk 位置，reader 先读 metadata，再读取感兴趣的 column chunks。PyArrow 22.0 文档展示单独读取 row group、写入多个 row groups，以及由多个文件组成 partitioned dataset。

### 6.2 可推导的 VLA 含义

- 适合只扫描 episode id、task、robot、timestamp、length、quality flag、action statistics 等少数列，用于 split、filter、audit 和 manifest。
- 可存 nested/byte-array 数据，不代表将压缩视频或高维 frame tensor 直接塞入 Parquet 一定高效；row group、column projection、decode 与单样本 lookup 仍需测试。
- 常见组合设计是 `Parquet metadata/index + HDF5/Zarr/WebDataset media/tensor payload`，但这只是候选架构，不是格式规范要求。

### 6.3 不能从当前来源推出

- Parquet 只能存标量，不能存 nested 或 binary。
- columnar 格式会让任意单 episode/window lookup 变快。
- row group 越大或越小始终更优。

## 7. Workload → Candidate Layout 合同

| VLA workload | 首选候选，不是最终答案 | 关键可测风险 | 最小证据 |
| --- | --- | --- | --- |
| local SSD 上 episode 内随机连续窗口 | chunk-aligned HDF5 或 Zarr | over-read、decompression、seek/metadata、worker contention | matched window trace、`A_read`、p50/p95 latency |
| object store 上大规模顺序 epoch | WebDataset shard 或 sharded Zarr | request count、shard imbalance、shuffle buffer、retry blast radius | request/sample、MB/s、sample/s、worker idle、retry log |
| split/leakage/quality audit 的列扫描 | Parquet metadata/index | row-group pruning、列投影、small-file overhead | selected columns、bytes scanned、filter hit、planning time |
| 训练 + debug + audit 混合需求 | hybrid layout | 双写一致性、lineage、payload/index drift | shared sample id、manifest hash、roundtrip/repair tool |

这里的“首选候选”只是进入 benchmark 的 shortlist。正式选择必须固定：数据量、episode/window 分布、camera/modalities、storage medium、worker/rank 数、cache state、compression、chunk/shard/row-group 参数和 sampler。

## 8. Benchmark 合同

```python
def benchmark_storage(adapter, requests, run_config):
    # Freeze the exact sample/window requests and cold/warm cache state.
    adapter.open(run_config)
    for req in requests:
        # Record logical bytes used separately from physical bytes fetched/decoded.
        sample, trace = adapter.read(req)
        validate_schema_and_hash(sample, req.expected)
        emit_latency_bytes_requests_cpu(trace)
```

最少同时报告：

1. cold / warm cache 的 p50、p95、p99 sample latency。
2. samples/s、logical MB/s、physical MB/s 与 `A_read`。
3. object request / file open / seek / decode / decompress 次数。
4. CPU、RAM、worker idle、GPU data wait 与 per-rank imbalance。
5. chunk/shard/row-group 参数、compression、storage medium、worker/rank 数。
6. corrupt object/shard/file 的 failure blast radius、retry 和可恢复性。

只报“DataLoader 更快”或单次峰值 MB/s，不能支持格式选择结论。

## 9. 个人项目证据挂钩

UWM/LIBERO inventory 与 ENG-004..006 artifact gate 记录了 Zarr small-chunk 随机读取的 DataLoader-only stall smoke。它可以作为 `ENG-012` 的真实 bad case：先检查 window selection、chunk layout、preload 与 worker trace。它不能证明 Zarr 是根因、不能证明换成 HDF5/WebDataset 会更快，也不能外推 full training throughput。

当前没有四格式 matched benchmark、相同样本 request trace 或转换后一致性 artifact；因此所有项目 hook 保持 `local clue / A-B pending`。

## 10. Source Freeze 结论

`VLA-ENG-012` 已具备进入知识页/题卡的来源条件，下游知识正文和单张题卡已生成；当前为 `source_frozen / knowledge+card_drafted / unseen / WARN`：

- 四类系统的核心组织与访问语义有官方依据。
- workload mapping、`A_read`、benchmark contract 与 hybrid layout 是工程框架。
- concurrency、remote consistency、corruption recovery 和实际性能没有统一保证。
- 下一切片优先做 `ENG-012` 独立 review 或真实口述；ENG-013..016 继续 source-first 后置。

## References

1. h5py 3.15.0, [Datasets](https://docs.h5py.org/en/3.15.0/high/dataset.html)，tag commit `4e8866a3d1af352add72014149d0810ee5543c48`。
2. zarr-python v3.2.1, [Arrays](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/arrays.md) 与 [Storage](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/storage.md)，commit `85890b3bb404fd1d401267c508a2694f5734559e`。
3. WebDataset, [README](https://raw.githubusercontent.com/webdataset/webdataset/e0953f9bba17b416d5792d5a263b171c266e78be/README.md)，commit `e0953f9bba17b416d5792d5a263b171c266e78be`。
4. Apache Parquet format, [README](https://raw.githubusercontent.com/apache/parquet-format/21ecc2b0f5786070561ae0d34152230853c83e2b/README.md)，commit `21ecc2b0f5786070561ae0d34152230853c83e2b`。
5. Apache Arrow 22.0, [PyArrow Parquet](https://arrow.apache.org/docs/22.0/python/parquet.html)。
6. 本仓库 [UWM/LIBERO inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)与[ENG-004..006 artifact gate](vol_05_local_artifact_gate_eng004_006.html)。
