# VOL 05 Engineering / Evaluation：Batch 2A 数据可追溯与批处理

> 状态：`drafted / knowledge_13_of_44 / cards_13_of_44_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前覆盖：`VLA-ENG-009..011`，3/44 个知识节点；对应 3 张题卡已生成并保持 unseen。  
> 本批目标：把 dataset/version/transform provenance、multimodal decode/cache/determinism、variable-length batching/padding 连接成可追溯的数据输入合同。

## 问题（Question）

1. `VLA-ENG-009`：怎样用 dataset/version/transform manifest 让一次训练可以追溯？
2. `VLA-ENG-010`：multimodal decode、augmentation、cache 与 determinism 如何共同影响训练？
3. `VLA-ENG-011`：variable-length sample、dynamic batching 与 padding waste 怎样设计和评估？

本批不展开 `VLA-ENG-012..016` 的存储格式、硬件迁移、offload、multi-teacher 显存等问题；也不生成对应题卡。

## 知识地图位置与边界

### 前置知识

- Batch 1 的 schema、split、DataLoader、checkpoint 和 reproducibility 合同。
- VOL 01 的 tensor shape、mask、数值稳定与统计估计。
- VOL 03 的 multimodal action window、padding、normalization 和 controller boundary。

### 证据边界

- DVC `.dvc` 文件规范支持数据输出路径、hash 和依赖字段，但不保证远端数据在本机可访问。[1]
- PyTorch DataLoader / `pad_sequence` 文档支持 API 语义；动态 batching 的 bucket、token budget、cache key 和 manifest schema 是本仓库工程设计。
- OpenPiVLA 的 `H=15,D=72`/`limit=16`、UWM 的 normalizer/data-root 只作为真实 bad case，不升级为通用 benchmark 事实。

## VLA-ENG-009：Dataset / Version / Transform Manifest

### 为什么“数据路径 + Git SHA”仍然不够

一次 VLA run 的输入不是单个目录，而是一个图：

```text
raw source
  -> dataset revision / content hash
  -> schema adapter
  -> split + group manifest
  -> decode / augment transform graph
  -> normalizer / sampler
  -> train run
```

如果只记录代码 commit，原始文件可以被原地替换；只记录数据目录，transform、split 或 normalizer 可能漂移。DVC 官方 `.dvc` 规范把 tracked output 的路径与 hash 写入 YAML，并允许记录依赖与 working directory；这支持“元数据可版本化”，但不等于远端对象已下载或内容一定可 load。[1]

### 最小 manifest

| 字段 | 作用 | 典型错误 |
| --- | --- | --- |
| `dataset_id/version` | 业务版本和来源 revision | 同名目录被覆盖 |
| `content_hash` | raw file/shard/metadata 内容指纹 | 只 hash 目录名，不 hash内容 |
| `schema_version` | observation/action 字段合同 | adapter 改了但版本不变 |
| `split_manifest_sha` | group split、holdout、dedupe 规则 | 重新生成 split 后无迹可循 |
| `transform_graph_sha` | decode/resize/augment 参数与代码 | `train.py` commit 相同但 YAML 漂移 |
| `normalizer_id/sha` | action/state 统计与维度顺序 | checkpoint 复用错误 normalizer |
| `sample_counts` | episode/row/frame/token 分母 | 只报样本总数，隐藏过滤 |
| `source_lineage` | file、line、episode、robot、camera | 异常样本无法回溯 |

### 实现映射

```python
def build_data_manifest(raw, schema, split, transforms, normalizer):
    # Hash content and metadata, never just the directory name.
    return {
        "dataset_id": raw.dataset_id,
        "dataset_version": raw.revision,
        "content_hash": hash_files(raw.files, raw.metadata),
        "schema_version": schema.version,
        "split_manifest_sha": sha256_json(split.manifest),
        "transform_graph_sha": sha256_json(transforms.resolved_config),
        "normalizer_sha": sha256_json(normalizer.stats),
        "sample_counts": split.counts,
        "source_lineage": raw.provenance,
    }
```

manifest 必须在训练启动时写入 run bundle，并在 eval 时重新校验。若 `content_hash`、`schema_version` 或 `normalizer_sha` 不匹配，应阻断，而不是静默继续。

### 诊断与项目挂钩

1. 对同一个 run 复算 manifest，比较 JSON canonicalization 后的 SHA。
2. 抽取少量 sentinel 样本，比较 decode 后 shape、dtype、颜色空间、action order 和 normalized range。
3. 用 manifest diff 区分“模型变了”和“数据/transform 变了”。

OpenPiVLA 的 `H=15,D=72` 与 formal formatter `limit=16` 冲突，说明 representation contract 必须进入 manifest；UWM 本地 snapshot 的 action normalizer JSON 与远端 data-root 说明“normalizer 文件存在”仍不等于 checkpoint/controller 已闭合。[7][8]

**危险做法**：把 `git commit + dataset path` 当成完整可复现 ID，或把 DVC pointer 文件存在写成数据对象已经本地可读。

## VLA-ENG-010：Multimodal Decode、Augmentation、Cache 与 Determinism

### Pipeline 分层

```text
bytes / remote object
  -> decode (image/video/json/audio)
  -> canonical dtype / color / layout
  -> resize / crop / augmentation
  -> cache lookup or write
  -> collate + mask
  -> host-to-device copy
```

PyTorch DataLoader 文档说明：`num_workers>0` 会启用多进程加载；dataset、collate 和 worker init 在 worker 中运行；`prefetch_factor`、`persistent_workers`、`pin_memory` 等参数会改变加载生命周期和 host→device 行为。[2] IterableDataset 在多 worker 下会复制 dataset replica，必须自行避免重复数据。[2]

### Cache key 不能只用 image path

一个安全的 decode cache key 至少是：

\[
k = H(\text{media_content},\text{decoder_version},\text{transform_graph},\text{dtype},\text{shape},\text{seed-policy}).
\]

变量解释：`media_content` 防止原文件被覆盖；`decoder_version` 防止库升级改变结果；`transform_graph` 绑定 resize/crop/augmentation；`dtype/shape` 防止 cache 被另一模型复用；`seed-policy` 区分 deterministic preprocess 与每 epoch 随机增强。实现上可将 `k` 写入 cache sidecar，并在读取时校验。

### Determinism 与速度 trade-off

- worker seed、Python/NumPy/torch RNG、epoch、sample key 和 augmentation counter 必须有明确 owner。
- `persistent_workers` 减少 worker 重启成本，并让 worker/Dataset instance 跨一次数据集消费继续存活；“RNG 未重置会改变重跑顺序”是需要用 seed/replay 验证的风险，不是文档保证的必然结果。
- `prefetch`/cache 能隐藏等待，不会修复坏数据、随机读争用或错误的 transform 版本。
- cache 命中率、decode error、fallback count、worker wait、CPU memory 和 pinned-memory 使用量应进入 observability。

### 最小检查

```python
def validate_decode_cache(sample, cache_entry, policy):
    # Recompute key from bytes, decoder, transform, output contract and seed policy.
    assert cache_entry.key == make_cache_key(sample, policy)
    assert cache_entry.shape == policy.output_shape
    assert cache_entry.dtype == policy.output_dtype
    assert cache_entry.color_space == policy.color_space
    assert cache_entry.transform_sha == policy.transform_sha
    assert cache_entry.error is None or policy.explicit_fallback
```

**项目挂钩**：UWM 的 DataLoader-only stall smoke 可支持“读取模式是瓶颈”的诊断，但不能单独证明 full training 加速；OpenPiVLA 的 eager/MACA 差异可作为 decoder/kernel compatibility 追问，不等于所有 AMP/cache 路径稳定。[7][8]

**危险做法**：cache 只按路径命名、decode error 静默返回最后一帧、把 `num_workers` 加大直接当作 determinism 或吞吐保证。

## VLA-ENG-011：Variable-Length Sample、Dynamic Batching 与 Padding Waste

### Padding 的数学账本

对 batch 中长度为 (L_1,\ldots,L_B) 的样本，统一 padding 到 (L_{max}=\max_i L_i) 时，粗略 padding waste 为：

\[
w_{pad}=1-\frac{\sum_{i=1}^{B}L_i}{B\,L_{max}}.
\]

其中 (L) 可以是 token、frame、action step 或 multimodal patch 数；它不是所有 workload 的同一成本单位。PyTorch `pad_sequence` 直接定义了将不同长度 Tensor 堆叠并填充到最长长度的输出形状，`batch_first=True` 时为 (B\times T\times *)，并显式接受 `padding_value` 与 `padding_side`。[3]

### 三种 mask 不要混用

| mask | 作用 | 典型错误 |
| --- | --- | --- |
| `attention_mask` | backbone 是否读取该位置 | padding token 参与 attention |
| `valid_mask` | observation/action/frame 是否真实存在 | padding 被当成真动作 |
| `loss_mask` | 该位置是否计入目标 | aux/padding loss 污染主任务 |

dynamic batching 通常按 token/frame/action budget 组 batch，而不是只按样本数；可先按长度分桶，再在桶内填充。它能降低 (w_{pad})，但改变 sampler 顺序、GPU 峰值、梯度噪声和分布式同步语义，必须记录 bucket policy、budget、drop_last、per-rank batch 与 effective workload。

### Bucket 与动态 budget

```python
def make_dynamic_batch(samples, token_budget):
    # Sort/bucket only with a deterministic key recorded in the manifest.
    ordered = sorted(samples, key=lambda x: (x.length, x.sample_id))
    batch, used = [], 0
    for sample in ordered:
        # A sample may be oversized and require an explicit singleton path.
        if batch and used + sample.length > token_budget:
            yield pad_and_mask(batch)
            batch, used = [], 0
        batch.append(sample)
        used += sample.length
    if batch:
        yield pad_and_mask(batch)
```

报告至少同时给出 sample/s、token(or frame)/s、平均 padding waste、p95 batch length、GPU peak memory、drop/oversize count 和 per-rank imbalance。只报 samples/s 会掩盖一个 batch 内长度差异。

### 项目挂钩与失败诊断

- VLA action horizon 固定时，`H` 仍可能因多图、语言长度、历史窗口或 patch 数而产生 variable token cost。
- OpenPiVLA 的 formatter `limit` 冲突、UWM 的 action window/normalizer 和 OPD 的 mixed-format 输出都需要把 padding/valid/loss mask 写入 schema，而不是隐含在 collator 中。
- 若 loss 下降但吞吐/显存异常，先比较 bucket histogram、padding waste、mask coverage 和 per-rank token count，再判断模型或 DataLoader。

**危险做法**：把 `pad_sequence` 的输出当成有效长度信息、只用一个 `attention_mask` 覆盖 action/loss mask，或声称 dynamic batching 必然提高训练效果。

## Batch 2A 复习表

| ID | 30 秒抓手 | 必须追问的证据 |
| --- | --- | --- |
| `VLA-ENG-009` | manifest 绑定 content/schema/split/transform/normalizer，路径本身不够 | manifest SHA、sentinel diff、source lineage |
| `VLA-ENG-010` | cache key 必须包含内容、decoder、transform、输出合同和 seed policy | hit/error/fallback/worker timing、cache sidecar |
| `VLA-ENG-011` | 先算 padding waste，再按 token/frame/action budget 做可重放 bucket | length histogram、mask coverage、per-rank workload |

## 证据与真实性边界

| 类型 | 本批使用方式 |
| --- | --- |
| 官方文档 | 支持 DVC pointer/schema、PyTorch DataLoader worker/prefetch/IterableDataset、`pad_sequence` shape/padding |
| 工程框架 | cache key、manifest 字段、dynamic budget、padding waste、mask audit |
| 项目 inventory | 提供 OpenPiVLA/UWM/OPD 的真实 schema/normalizer/shape bad cases |
| 未核实 | 当前项目是否已执行完整 manifest diff、cache replay、dynamic-batch A/B |

当前 review 保持 `WARN`：3 个知识节点已形成来源和实现映射，3 张题卡已生成但尚未独立逐条事实复核或进行候选人口述。

## References

1. DVC official docs, [.dvc Files](https://dvc.org/doc/user-guide/project-structure/dvc-files)，读取日期 2026-07-17；normalized main-text SHA-256 `27cd7fc76b1f6fe720c835ad4c3b34bfd89549c464fddb032ebb1fee4e268b5a`。
2. PyTorch 2.13, [torch.utils.data](https://docs.pytorch.org/docs/2.13/data.html)，读取日期 2026-07-17；normalized main-text SHA-256 `9032517582f5a20a811008e4f71a81e356d058380cfc985b552ef338b1cecf5f`。
3. PyTorch 2.13, [torch.nn.utils.rnn.pad_sequence](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.rnn.pad_sequence.html)，读取日期 2026-07-17；normalized main-text SHA-256 `b8fb4f7c4d334a2d65f957c5aa1387bc43f995dea64fe2999ced80db15ce928e`。
4. Hugging Face Datasets v4.8.4, [Cache management](https://huggingface.co/docs/datasets/v4.8.4/en/cache) 与 [Cache fingerprint](https://huggingface.co/docs/datasets/v4.8.4/en/about_cache)，读取日期 2026-07-17；normalized main-text SHA-256 分别为 `afaabe583e52ab68350addcd56f2fe90f746b52ae153b263143c63aa993cd61e`、`bcedb14fe09d45e1cb43f58db96b00753e0a076992754d1f887ea6f42767cdfa`。
5. Hugging Face Transformers v5.14.0, [Data Collator](https://huggingface.co/docs/transformers/v5.14.0/en/main_classes/data_collator)，读取日期 2026-07-17；normalized main-text SHA-256 `6250a91993214a7dee35eb553e110ddef230848a6d5561cff18c7fa65d44e945`。
6. PyTorch 2.13, [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)，读取日期 2026-07-17；normalized main-text SHA-256 `5a19f15c86d56dbd0f9ea0572b86e960475328c99c36408cfb82d4fce90a03c5`，用于 seed/determinism 边界。
7. 本仓库 [OpenPiVLA Batch 2 evidence freeze](../sources/openpivla_batch2_evidence_freeze.html)、[UWM/LIBERO inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
8. 本仓库 [VOL 05 ENG-004..006 local artifact gate](../sources/vol_05_local_artifact_gate_eng004_006.html)。
