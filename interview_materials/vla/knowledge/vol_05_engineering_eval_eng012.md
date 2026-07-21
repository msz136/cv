# VOL 05 Engineering / Evaluation：Storage Layout 与 VLA 访问模式（ENG-012）

> 状态：`drafted / knowledge_14_of_44 / cards_14_of_44_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-012`；[单张题卡](../questions/vol_05_engineering_eval_eng012.html)已在独立切片生成并保持 unseen。  
> 来源入口：[ENG-012 Source Freeze](../sources/vol_05_eng012_storage_formats_source_freeze.html)。  
> 核心边界：HDF5/Zarr 是数组存储，WebDataset 是 tar-shard dataset representation，Parquet 是列式表格式；不把它们做成脱离 workload 的“格式排行榜”。

## 问题（Question）

`VLA-ENG-012`：HDF5、Zarr、WebDataset、Parquet 的访问模式和取舍是什么？如果训练既有 episode 内随机窗口，又有对象存储上的顺序 epoch 和 metadata audit，怎样设计存储布局并证明它真的更合适？

## 知识地图位置与前置依赖

```text
schema / split / transform / normalizer manifest
                 ↓
        storage layout + access pattern
                 ↓
     decode / collate / worker / GPU pipeline
                 ↓
       throughput + reproducibility + eval trace
```

前置：

- `VLA-ENG-001` 的 observation/action/schema/normalizer 合同。
- `VLA-ENG-003` 的 data wait、decode、host→device 和 GPU pipeline 分解。
- `VLA-ENG-009..011` 的 manifest、cache key、variable-length 与 padding/mask 合同。

本节点只解决“数据如何布局和取”，不解决 decoder 算子、模型结构、数据质量或 controller 语义。

## 1. 先区分抽象层

| 系统 | 主要抽象 | 典型读取单位 | 适合先问的问题 |
| --- | --- | --- | --- |
| HDF5 / h5py | 层级文件 + N 维 Dataset | chunk / selection | 一个 episode window 会触碰多少 chunk？ |
| Zarr v3 | N 维 array + 可替换 store | chunk；sharding 时 shard 是写入单元 | 对象存储 request、chunk shape、shard shape 如何协同？ |
| WebDataset | tar 文件 + sample/shard 命名约定 | tar member / shard stream | 样本是否已预切，能否顺序流式消费？ |
| Parquet | column-oriented table | row group / column chunk / page | 只读少数 metadata 列时能跳过多少数据？ |

“读取单位”不是“有效样本单位”。VLA 的一个样本可能包含多帧图像、语言、proprio、action window 和 provenance；必须在 adapter 层把物理读取单位转换成 schema row，并记录 logical bytes 与 physical bytes。

## 2. HDF5：chunk shape 决定随机窗口的代价

### 2.1 机制

h5py 3.15 文档区分 contiguous layout 与 chunked layout。chunked Dataset 把数组切成固定大小块，用索引结构定位；chunking 支持 resize 与 compression。一次 selection 即使只需要 chunk 中一个元素，也可能需要处理整个 chunk，因此 chunk shape 直接影响读取放大。[1]

假设一个窗口真实消费的字节数为 (B_{used})，底层实际读取或解压的 chunk 字节数为 (B_{fetched})，定义：

\[
A_{read}=\frac{B_{fetched}}{B_{used}}.
\]

这里 (A_{read}) 是本仓库的 profiling 指标，不是 HDF5 API 字段。若 episode 内连续取时间窗，时间维和常用 camera/action 维度应尽量与 chunk selection 对齐；chunk 太大可能带来 over-read 和解压浪费，太小可能增加索引、seek、metadata 和文件系统调用。

### 2.2 VLA 映射

```text
episode[t0:t0+H, cameras, state, action]
       ↓
触碰若干 HDF5 chunks
       ↓
decode / normalize / collate
       ↓
model batch
```

如果训练 sampler 以随机 episode/window 为主，应报告每个 window 触碰的 chunk 数、(A_{read})、p95 latency 和 worker idle；不能只看文件总吞吐。若训练是整段顺序扫描，随机窗口最优的 chunk 形状未必最优。

### 2.3 边界与 bad case

- h5py 页面支持 chunk/compression/resize 语义，不支持“这个 chunk shape 对所有 VLA workload 最优”。
- 本节点不从 Dataset 页面推出 SWMR、MPI、文件锁或多进程写入结论；这些需要单独来源与 smoke。
- “一个 `.h5` 文件”不等于 checkpoint、manifest、normalizer 和 controller contract 自动绑定。

## 3. Zarr：chunk、store 与 v3 sharding 的组合

### 3.1 机制

Zarr v3 数组按 chunk 切分，可使用 compressor；storage guide 支持 local、Zip、Fsspec remote、memory 与 object store。[2] v3 sharding 允许多个 chunks 放入一个 storage object：chunk 是独立读取单位，shard 是写入单位；完整 shard 写入有利于性能并减少并发写入问题。

因此 Zarr 的访问成本至少有两层：

1. store/object 层：GET、range request、metadata、retry 和 small-object 数量。
2. array/chunk 层：selection 触碰多少 chunk、解压多少数据、是否跨 camera/time/action 维。

shard 可以减少对象数量，但不会消除 chunk 的逻辑读取；同时可能扩大写入单元和更新冲突范围。

### 3.2 VLA 映射

```python
def read_window(zarr_array, request, contract):
    # Use a frozen selection; record chunk and store-level trace separately.
    selection = contract.window_to_selection(request)
    sample = zarr_array[selection]
    # Schema checks prevent a fast but semantically wrong window.
    validate_shape_dtype_frame(sample, contract)
    return sample
```

对对象存储训练，应把 `requests/sample`、metadata GET、logical/physical bytes、cache hit、retry 和 p95 latency 与模型 step timing 关联。小 chunk 可能降低 (A_{read})，却造成 request storm；sharding 可能减少 request 数，却让写入和更新更粗粒度。这些是 workload trade-off，不是 Zarr 的性能保证。

### 3.3 边界与 bad case

- Zarr 支持 remote store 不等于网络、权限、缓存和一致性已经解决。
- `chunks`/`shards` 参数不自动知道 VLA 的 episode、camera、action horizon 或 worker pattern。
- 不把“云端友好”写成“任何云端任务都更快”。

## 4. WebDataset：tar shard 与顺序流式 pipeline

### 4.1 机制

冻结的 WebDataset README 将格式定义为 tar files：同一样本的文件共享 basename，shard 使用编号命名；可以从 local disk 或 pipe 读取，并面向 object/cloud store。示例 pipeline 产生 PyTorch `IterableDataset`，通过 shard/sample shuffle buffer 改变消费顺序。[3]

### 4.2 VLA 映射

WebDataset 的优势是把样本预先打包成适合顺序流的单元：

```text
episode/window sample
  -> image/video/json/action members
  -> tar shard
  -> iterable stream
  -> decode + collate
  -> GPU
```

它适合：

- 远端 shard 上的大规模顺序 epoch；
- 样本已经按 episode/window 预切；
- 需要把多个模态文件一起流式送入 worker。

它不自动解决：

- 从超长 episode 任意跨 frame 取 window；
- 全局均匀随机访问；
- shard 之间的 class/task/robot balance；
- worker/rank 对 IterableDataset 的分片和重复问题。

README 中“相对 random access 的 3x–10x local-drive I/O”是项目文档中的概括，缺少本仓库 workload、硬件和 protocol，不得写成 VLA 通用 benchmark。也不能反过来说 WebDataset 完全没有 random-access 路径，那会混淆基础 streaming interface 与其他 indexed reader。

## 5. Parquet：列式 metadata 与 row-group 读取

### 5.1 机制

Apache Parquet format 将文件组织为 row groups；每个 row group 对每个 column 有一个 column chunk，column chunk 再由 pages 构成。file metadata 保存 chunk 位置，reader 可先读取 metadata，再选择感兴趣的 column chunks。[4] PyArrow 22.0 展示了 `read_row_group`、多个 row groups 和 partitioned datasets。[5]

### 5.2 VLA 映射

Parquet 很适合把以下字段作为可过滤、可审计的表：

```text
episode_id / robot / site / task / timestamp
length / camera_keys / quality_flag / split
action_statistics / normalizer_id / source_line
```

当 split、leakage、quality audit 只需要少数列时，column projection 和 row-group/partition 组织可以减少无关 payload 读取。Parquet 也支持 nested 和 binary，但这不等于把压缩视频、高维 frame tensor 或高频随机单窗口 payload 直接放进去就一定高效。

常见候选架构是：

```text
Parquet metadata/index
        +
HDF5 / Zarr / WebDataset media or tensor payload
        ↓
shared sample_id + manifest hash + roundtrip check
```

这是组合设计，不是 Parquet 规范要求；双写会新增 index/payload drift、repair 和 lineage 风险。

## 6. Workload → candidate layout

| Workload | 候选 shortlist | 先测什么 | 不能直接宣称 |
| --- | --- | --- | --- |
| local SSD、episode 内随机连续 window | chunk-aligned HDF5 / Zarr | (A_{read})、触碰 chunk 数、p50/p95、worker idle | HDF5/Zarr 必然更快 |
| object store、大规模顺序 epoch | WebDataset shard / sharded Zarr | request/sample、MB/s、shuffle、retry、shard imbalance | WebDataset 的 README 倍率适用于本项目 |
| split/leakage/quality metadata scan | Parquet | selected columns、bytes scanned、row-group pruning、planning time | Parquet 适合所有 media payload |
| training + debug + audit 混合 | Parquet index + payload store | sample_id、manifest hash、roundtrip、repair path | 双格式天然一致 |

候选 shortlist 不是结论。benchmark 必须固定 storage medium、episode/window 长度分布、camera/modalities、compression、chunk/shard/row-group 参数、worker/rank 数、cold/warm cache 和 sampler。

## 7. 最小 benchmark 与实现映射

```python
def benchmark_storage(adapter, requests, run_config):
    # Freeze request order and cold/warm cache state before comparing formats.
    adapter.open(run_config)
    for request in requests:
        # Separate logical bytes used from physical bytes fetched/decoded.
        sample, trace = adapter.read(request)
        validate_schema_and_hash(sample, request.expected)
        emit_latency_bytes_requests_cpu_gpu_wait(trace)
```

至少记录：

1. cold/warm cache 的 p50/p95/p99 sample latency。
2. samples/s、logical MB/s、physical MB/s 与 (A_{read})。
3. file open、object request、range read、seek、decode、decompress 次数。
4. CPU/RAM、worker idle、GPU data wait、per-rank token/workload imbalance。
5. corrupt file/shard/object 的 failure blast radius、retry 与可恢复性。

如果只报告“DataLoader 更快”或单次峰值 MB/s，无法支持格式选择；必须把 request trace 与逻辑样本结果绑定。

## 8. 项目证据挂钩

UWM/LIBERO inventory 和 ENG-004..006 artifact gate 中的 DataLoader-only stall smoke，可作为存储布局诊断入口：先查看 window selection、chunk 触碰、preload、worker wait 和 cache state。它只能支持“读取路径存在瓶颈线索”，不能证明 Zarr 是根因、不能证明转换为 HDF5/WebDataset 会更快，也不能外推 full-training throughput。

当前没有四格式 matched benchmark、同一 request trace、转换后 schema roundtrip 或 payload/index consistency artifact。因此本节点的项目 hook 标签为 `local clue / A-B pending`。

## 9. Trade-off、bad case 与面试抓手

### Trade-off

- chunk 越大：更少的索引/request，但可能更高 over-read 和解压峰值。
- chunk 越小：随机窗口更细，但可能产生 small-object、metadata 和 seek 压力。
- shard 越大：顺序吞吐和对象数量可能更好，但更新、重试和坏 shard 影响范围更大。
- row group 越大：顺序列扫描更连续，但单次过滤可能读更多数据；越小则 metadata/规划开销增加。
- hybrid layout：metadata scan 与 media payload 可分别优化，但 lineage、双写一致性和修复成本上升。

### Bad case

1. 用随机小 window 读取被按整段视频/episode 打成大 chunk，GPU 等待但只消费很少字节。
2. 把每帧/每小对象单独放入 object store，压缩率很好却被 request/metadata latency 主导。
3. WebDataset shard 内样本已配对，但 sampler 没有按 worker/rank 正确分片，导致重复或 task imbalance。
4. Parquet metadata 与 Zarr/HDF5 payload 的 sample_id 或 manifest hash 漂移，audit 读到的列与训练 tensor 不一致。

### 30 秒面试抓手

“我不会先选格式，而是先区分随机 window、顺序 stream 和 column scan。HDF5/Zarr 的核心变量是 chunk 和 over-read，WebDataset 的核心变量是 tar shard、预切 sample 和顺序流，Parquet 的核心变量是 row group/column chunk 和 metadata projection。然后用固定 request trace 比较 logical/physical bytes、p95 latency、request 数、worker/GPU wait 和坏数据恢复；没有 matched A/B 就只称为候选布局。”

## 10. 证据边界与下一步

官方来源支持四类系统的组织和读取语义；`A_read`、workload shortlist、hybrid layout、benchmark contract 和三项目 hook 属于本仓库工程框架或 local clue。当前仍不能支持：

- 任意格式的普遍性能排名；
- WebDataset README 倍率在本项目复现；
- UWM stall 的单一格式根因；
- 多进程/多机并发、远端一致性和 corruption recovery 的强结论。

`VLA-ENG-012` 单张题卡已在独立切片生成，但没有真实口述，仍为 `unseen`。下一步优先独立 review 或一题一练；ENG-013 seed/sampler/reproducibility 必须重新走 source-first gate。

## References

1. h5py 3.15.0 [Datasets](https://docs.h5py.org/en/3.15.0/high/dataset.html)，tag commit `4e8866a3d1af352add72014149d0810ee5543c48`。
2. zarr-python v3.2.1 [Arrays](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/arrays.md) 与 [Storage](https://raw.githubusercontent.com/zarr-developers/zarr-python/v3.2.1/docs/user-guide/storage.md)，commit `85890b3bb404fd1d401267c508a2694f5734559e`。
3. WebDataset [README](https://raw.githubusercontent.com/webdataset/webdataset/e0953f9bba17b416d5792d5a263b171c266e78be/README.md)，commit `e0953f9bba17b416d5792d5a263b171c266e78be`。
4. Apache Parquet format [README](https://raw.githubusercontent.com/apache/parquet-format/21ecc2b0f5786070561ae0d34152230853c83e2b/README.md)，commit `21ecc2b0f5786070561ae0d34152230853c83e2b`。
5. Apache Arrow 22.0 [PyArrow Parquet](https://arrow.apache.org/docs/22.0/python/parquet.html)。
6. 本仓库 [ENG-012 Source Freeze](../sources/vol_05_eng012_storage_formats_source_freeze.html) 与 [UWM/LIBERO inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
