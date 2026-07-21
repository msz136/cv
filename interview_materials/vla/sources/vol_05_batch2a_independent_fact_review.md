# VOL 05 Batch 2A：独立官方文档事实复核

> 状态：`source_reviewed / ENG-009..011 / WARN`  
> 复核日期：2026-07-17  
> 复核对象：[Batch 2A 知识页](../knowledge/vol_05_engineering_eval_batch2a.html)与[三张原子题卡](../questions/vol_05_engineering_eval_batch2a.html)  
> 复核范围：DVC `.dvc` 元数据、PyTorch DataLoader / `pad_sequence` / Reproducibility、Hugging Face Datasets cache 与 Transformers collator。  
> 结论边界：本报告核对官方 API/文档语义；不证明个人项目已完成 manifest diff、cache replay、dynamic-batch A/B 或 closed-loop 验收。

## 1. 复核问题与方法

本轮只回答三个问题：

1. `VLA-ENG-009` 中哪些 provenance 字段由 DVC 官方文档直接支持，哪些是本仓库额外设计？
2. `VLA-ENG-010` 中 DataLoader worker/cache/reproducibility 的表述是否准确？
3. `VLA-ENG-011` 中 `pad_sequence`、padding waste、mask 分离与 dynamic batching 的来源边界是什么？

复核方法：对官方页面直接 HTTP GET；移除 `script/style/nav/header/footer/svg`，合并正文空白后，记录 normalized main-text 长度和 SHA-256；再按“官方原文支持 / 工程推导 / 项目证据 / 未核实”逐条审查。完整 HTML 会包含请求时动态生成的资源标识，raw response SHA 在连续 GET 间可能变化，因此本报告不把它当稳定来源版本号。

## 2. 冻结来源账本

| 来源 | 冻结 URL / 版本 | normalized text 长度 / SHA-256 | 可支持内容 | 不能支持内容 |
| --- | --- | --- | --- | --- |
| DVC `.dvc Files` | [rolling official page](https://dvc.org/doc/user-guide/project-structure/dvc-files) | `8393` / `27cd7fc76b1f6fe720c835ad4c3b34bfd89549c464fddb032ebb1fee4e268b5a` | YAML 中的 `outs`、path、hash、`deps`、`wdir` 等元数据字段 | 远端对象已下载、本地可解码、与某 checkpoint 配套 |
| PyTorch DataLoader | [PyTorch 2.13](https://docs.pytorch.org/docs/2.13/data.html) | `47667` / `9032517582f5a20a811008e4f71a81e356d058380cfc985b552ef338b1cecf5f` | worker 生命周期、dataset/collate/worker init、IterableDataset replica、prefetch、persistent workers、pin memory | cache key schema、项目吞吐提升、端到端 determinism |
| PyTorch `pad_sequence` | [PyTorch 2.13](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.rnn.pad_sequence.html) | `2405` / `b8fb4f7c4d334a2d65f957c5aa1387bc43f995dea64fe2999ced80db15ce928e` | pad 到最长长度、`T×B×*` / `B×T×*`、padding value/side | 有效长度自动保存、mask 自动正确、dynamic batching 性能 |
| PyTorch Reproducibility | [PyTorch 2.13](https://docs.pytorch.org/docs/2.13/notes/randomness.html) | `11230` / `5a19f15c86d56dbd0f9ea0572b86e960475328c99c36408cfb82d4fce90a03c5` | 跨版本/平台不保证完全复现、Python/NumPy/torch seed、DataLoader worker reseed、deterministic trade-off | 任意硬件/版本 bitwise identical、仅设一个 seed 即完全复现 |
| HF Datasets cache management | [Datasets v4.8.4](https://huggingface.co/docs/datasets/v4.8.4/en/cache) | `5751` / `afaabe583e52ab68350addcd56f2fe90f746b52ae153b263143c63aa993cd61e` | Hub/Datasets 两类本地 cache、Arrow cache、`load_from_cache_file=False` 重算 | 自定义 VLA decode cache key 的全部字段 |
| HF Datasets cache fingerprint | [Datasets v4.8.4](https://huggingface.co/docs/datasets/v4.8.4/en/about_cache) | `4695` / `bcedb14fe09d45e1cb43f58db96b00753e0a076992754d1f887ea6f42767cdfa` | 初始 Arrow/file hash、前一 fingerprint 与最新 transform hash 的组合 | decoder/version/dtype/shape/seed-policy 必然进入默认 fingerprint |
| HF Transformers Data Collator | [Transformers v5.14.0](https://huggingface.co/docs/transformers/v5.14.0/en/main_classes/data_collator) | `17879` / `6250a91993214a7dee35eb553e110ddef230848a6d5561cff18c7fa65d44e945` | collator 形成 batch、padding、random masking、longest/max length/pad-to-multiple | VLA 的 `attention/valid/loss` 三 mask 自动分离 |

知识页初次冻结的 PyTorch DataLoader 与 `pad_sequence` 完整 HTML SHA 分别为 `b0d12f...`、`11c15d...`；复核发现 raw HTML 在连续 GET 间也会漂移，而 normalized main-text SHA 稳定。因此本轮把来源指纹统一改为规范化正文 SHA，并重新核对相关语义。Hugging Face 原先使用 `main`/无版本 URL，本轮改为可复查的稳定版本页。

## 3. `VLA-ENG-009`：Dataset / Version / Transform Manifest

### 3.1 直接支持的事实

DVC `.dvc` 文件是 YAML 元数据文件。官方示例的 `outs` 项包含内容 hash 与 `path`；schema 也列出 `deps`、`wdir`、`cmd`、`outs` 等字段。因此题卡说“pointer 可记录 path/hash/dependency/working-directory metadata”成立。

### 3.2 需要保留的边界

- “`.dvc` 文件存在不等于数据对象已经本地可读”是正确的可用性边界，但不是 DVC 页面逐字给出的保证；应表述为 metadata 与 object availability 的工程区分。
- `schema_version`、`split_manifest_sha`、`transform_graph_sha`、`normalizer_sha`、`sample_counts`、camera/episode lineage 是本仓库建议的 VLA manifest，不是 DVC 默认 schema。
- “关键字段不一致就阻断”是 fail-closed 工程策略；官方文档没有替项目决定哪些字段属于 fatal mismatch。

### 3.3 节点结论

`VLA-ENG-009 = PASS WITH WARNING`：DVC 元数据语义准确；完整 VLA manifest 仍需明确标记为 engineering contract，不能写成 DVC 的默认保证，也不能升级为项目已运行 manifest diff。

## 4. `VLA-ENG-010`：Decode / Cache / Determinism

### 4.1 DataLoader 语义核对

PyTorch 2.13 文档直接支持：

- 创建 DataLoader iterator 时，`num_workers>0` 会创建 worker process；dataset、`collate_fn`、`worker_init_fn` 被传给 worker，I/O、transform 与 collate 在 worker 中运行。
- IterableDataset 在多进程下每个 worker 持有 replica；若不分片，naive loading 可能重复数据。
- `prefetch_factor` 是每个 worker 提前加载的 batch 数；`persistent_workers=True` 会在一次数据集消费后保留 worker process 和 Dataset instance；`pin_memory=True` 会将可识别的 Tensor 放入 pinned memory。

因此知识页对 worker/prefetch/persistent/pin 的 API 描述成立。但“persistent worker 如果不重置随机状态会改变重跑顺序”是由生命周期语义推导出的风险，不是官方页保证必然发生。

### 4.2 Cache 与 reproducibility 边界

HF Datasets 官方 fingerprint 把初始 Arrow table/file hash 与后续 transform hash 结合；cache management 页面也允许通过 `load_from_cache_file=False` 重新执行 transform。这支持“cache 必须与数据状态和 transform 绑定”的方向。

本仓库的 VLA cache key：

\[
k=H(\text{media content},\text{decoder version},\text{transform graph},\text{dtype},\text{shape},\text{seed policy})
\]

变量与实现边界：`media content` 与 `transform graph` 有 HF fingerprint 的相邻官方语义；decoder version、dtype、shape、seed policy 是面向 multimodal/VLA 的额外工程字段。公式不是 HF 默认实现，代码中必须自行构造 sidecar 和 invalidation policy。

PyTorch Reproducibility 页面明确说跨 release、commit、platform，甚至 CPU/GPU 之间都不保证完全复现；它建议控制 torch/Python/NumPy RNG，并用 DataLoader `worker_init_fn` 和 `generator` 处理 worker reseed。由此，题卡“prefetch/cache 不等于 determinism”成立。

### 4.3 节点结论

`VLA-ENG-010 = PASS WITH WARNING`：DataLoader 与 seed 边界有官方依据；VLA cache key、decode fallback 和 observability 字段是工程合同。UWM stall smoke 仍只能支持读取瓶颈线索，不能证明 full-training 加速或确定性。

## 5. `VLA-ENG-011`：Variable-Length / Dynamic Batching

### 5.1 Padding 语义与公式

PyTorch `pad_sequence` 明确把不同长度 Tensor pad 到 batch 最长长度；`batch_first=True` 时输出为 `B×T×*`，否则为 `T×B×*`。它只返回 padded Tensor，不附带每个样本的原始有效长度，因此题卡“不能把 padded 输出当有效长度信息”成立。

对长度为 `L_1,...,L_B`、统一 pad 到 `L_max` 的 batch：

\[
w_{pad}=1-\frac{\sum_i L_i}{B L_{max}}.
\]

变量解释：`B L_max` 是总 slot 数，`sum_i L_i` 是有效 slot 数，两者之差除以总 slot 即 padding fraction。该推导正确，但 `L` 可能代表 token、frame、action step 或 patch；实际 attention/decoder 计算成本不一定与 `L` 线性，因此不能把 `w_pad` 直接当 GPU FLOP 节省比例。

### 5.2 Dynamic batch 与 mask 边界

PyTorch DataLoader 文档说明 IterableDataset 的用户定义顺序允许 dynamic batch size；HF collator 文档支持 longest/max-length padding 和 padding/masking 类处理。这些来源不规定：

- 按 `(length, sample_id)` 排序；
- token/frame/action budget；
- oversize singleton 策略；
- `attention_mask`、`valid_mask`、`loss_mask` 的 VLA 三层合同；
- per-rank workload、梯度噪声或同步诊断。

这些是合理的工程设计，必须通过 matched fixed-batch vs dynamic-batch A/B 验证。不同 rank 的有效 token 数、loss denominator 和 step timing 应被记录，不能仅用 samples/s 宣称更快。

### 5.3 节点结论

`VLA-ENG-011 = PASS WITH WARNING`：`pad_sequence` shape/padding 与 `w_pad` 推导成立；bucket/budget/mask/per-rank 合同仍是 framework，不是 PyTorch/HF 默认保证。

## 6. Claim–Source 结论表

| Claim | 类型 | 结论 | 安全表达 |
| --- | --- | --- | --- |
| `.dvc` 可保存 path/hash/deps/wdir 元数据 | official | PASS | DVC 支持元数据追踪，不代表 object/runtime 可用 |
| VLA manifest 必须含 schema/split/transform/normalizer/lineage | engineering contract | PASS WITH WARNING | 这是可复现性设计，不是 DVC 默认字段 |
| DataLoader 多 worker 会运行 dataset I/O/transform/collate | official | PASS | 用 worker 语义解释并行边界 |
| IterableDataset replica 未分片可能重复数据 | official | PASS | 使用 worker info/init 做 replica 配置 |
| persistent workers 必然导致随机顺序变化 | inference | REJECT AS ABSOLUTE | 只说生命周期跨 epoch，RNG reset policy 必须显式验证 |
| HF 默认 cache key 已包含 decoder/dtype/shape/seed | unsupported | REJECT | HF fingerprint 是相邻机制；VLA key 需自行实现 |
| `pad_sequence` 返回有效长度和正确 mask | unsupported | REJECT | 它只 pad/stack；length 与 mask 由上层维护 |
| dynamic batching 必然提升吞吐或训练效果 | unsupported | REJECT | 用 matched A/B、token/frame throughput 与 per-rank workload 验证 |
| 三种 mask 应分离 | engineering contract | PASS WITH WARNING | 是 VLA loss/执行语义设计，不冒充框架默认行为 |

## 7. 对知识页与题卡的修订

本轮做以下最小修订：

1. 将官方页面指纹更新为可重复计算的 normalized main-text SHA，并记录规范化规则。
2. 将 Hugging Face source 从 rolling `main` 改为 Datasets v4.8.4 / Transformers v5.14.0；增加 `about_cache` fingerprint 来源。
3. 明确 `persistent_workers` 的 RNG 影响是需要验证的风险，不写成必然结果。
4. 明确 custom cache key、manifest schema、dynamic budget、三种 mask 是 engineering contract。
5. 不修改任何项目指标、checkpoint 结论、个人 ownership 或练习状态。

## 8. 总结与下一步

三个节点均达到 `PASS WITH WARNING`：官方 API 语义已复核，核心工程推导没有发现公式或 API 错误；WARN 来自四个未闭环项：rolling DVC 页面、custom cache/manifest/batching contract、缺项目 A/B artifact、缺真实口述与浏览器视觉 QA。

下一步不应直接扩展 `ENG-012..016`。优先级是：

1. 对 `VLA-ENG-009..011` 做一次一题一练；或
2. 若出现真实项目 artifact，补 manifest diff、cache replay、fixed-vs-dynamic batch A/B；或
3. 在来源准备充分后再进入 `ENG-012` 存储格式切片。

## References

1. DVC, [.dvc Files](https://dvc.org/doc/user-guide/project-structure/dvc-files)，读取日期 2026-07-17。
2. PyTorch 2.13, [torch.utils.data](https://docs.pytorch.org/docs/2.13/data.html)，读取日期 2026-07-17。
3. PyTorch 2.13, [pad_sequence](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.rnn.pad_sequence.html)，读取日期 2026-07-17。
4. PyTorch 2.13, [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)，读取日期 2026-07-17。
5. Hugging Face Datasets v4.8.4, [Cache management](https://huggingface.co/docs/datasets/v4.8.4/en/cache)与[Cache fingerprint](https://huggingface.co/docs/datasets/v4.8.4/en/about_cache)，读取日期 2026-07-17。
6. Hugging Face Transformers v5.14.0, [Data Collator](https://huggingface.co/docs/transformers/v5.14.0/en/main_classes/data_collator)，读取日期 2026-07-17。
7. 本仓库 [Batch 2A canonical knowledge](../knowledge/vol_05_engineering_eval_batch2a.md)与[Batch 2A atomic cards](../questions/vol_05_engineering_eval_batch2a.md)。
