# VOL 05 Engineering / Evaluation：ENG-012 原子题卡

> 状态：`drafted / cards_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-012`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-012 Storage Layout](../knowledge/vol_05_engineering_eval_eng012.html)；没有 matched request-trace benchmark 前，格式选择只能称为候选方案。

## Storage Layout 与 Workload

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-012</b> · HDF5、Zarr、WebDataset、Parquet 应怎样按 VLA workload 选择？</summary>

**面试意图**：判断你能否区分数组存储、tar-shard streaming 与列式表，并用访问 trace 证明选择，而不是背格式优缺点排行榜。

**30 秒回答**：先区分随机窗口、顺序流和列扫描：HDF5/Zarr 看 chunk 与读放大，WebDataset 看 shard 和预切样本，Parquet 看 row group 与列投影。再用固定请求 trace 比 p95、物理/逻辑字节、请求数和 GPU 等待；没有 matched A/B 只称候选布局。

**机制展开（约 2 分钟）**：四者不是同一层。HDF5/Zarr 是 N 维数组，随机窗口看 chunk 对齐和 `A_read=physical/logical bytes`；Zarr 另看 object request 与 shard 写入。WebDataset 将预切样本放入 tar shards，适合顺序远端流，但 shuffle、worker/rank 分片和任意窗口需另行设计。Parquet 按 row group/column chunk 组织，适合 split、quality、lineage 等少数列扫描。混合布局可用 Parquet index + payload store，但要用 shared sample_id、manifest hash 和 roundtrip 防漂移。

**诊断 / 证据**：冻结相同 sample/window request、schema、compression、storage medium、worker/rank 与 cold/warm cache；报告 p50/p95/p99、samples/s、logical/physical MB、`A_read`、object/file request、decode/decompress、worker idle、GPU data wait、rank imbalance、retry 和 corrupt-unit blast radius。只报峰值 MB/s 或 DataLoader-only 加速不能支持最终选择。

**项目挂钩**：UWM/LIBERO 的 Zarr DataLoader-only stall 只能作为读取瓶颈线索；可先查 window selection、chunk 触碰、preload、worker wait 和 cache state。不能据此说 Zarr 是根因、换 HDF5/WebDataset 必然更快，或 full-training throughput 已提升。

**追问树**：为什么 HDF5/Zarr 不能直接排名？chunk 越小越好吗？WebDataset 如何保证 shuffle 与 worker 分片？Parquet 能不能存视频？hybrid layout 如何防 index/payload 漂移？怎样设计 fixed request trace？

**危险答案**：说“Zarr 最适合云、WebDataset 一定快 3–10 倍、Parquet 不能存 binary”，或拿不同 sampler/cache/压缩参数的结果直接比较。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-012 知识页](../knowledge/vol_05_engineering_eval_eng012.html)：四类系统机制、workload mapping、`A_read`、benchmark contract 与项目边界。
2. [ENG-012 Source Freeze](../sources/vol_05_eng012_storage_formats_source_freeze.html)：h5py 3.15.0、Zarr v3.2.1、WebDataset commit、Parquet format commit 与 PyArrow 22.0 的 frozen evidence。
3. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：Zarr DataLoader-only stall、preload 方向与 full-training evidence boundary。
