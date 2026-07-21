# VOL 05 Engineering / Evaluation：Batch 2A 原子题卡

> 状态：`drafted / cards_3_of_44 / WARN`  
> 更新日期：2026-07-17  
> 当前题数：3 / 44（本批新增 3 张）  
> 覆盖范围：`VLA-ENG-009..011`  
> 难度：L2 2 题 / L3 1 题  
> 优先级：P0 1 题 / P1 2 题  
> 练习状态：全部 `unseen`  
> 前置知识：[VOL 05 Batch 2A](../knowledge/vol_05_engineering_eval_batch2a.html)；manifest/cache/dynamic batching 的工程 A/B 证据尚未闭合，不能把设计合同讲成个人已验证结果。

## A. Dataset / Version / Transform Provenance

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-009</b> · 为什么 VLA run 只记录 Git SHA 和 dataset path 还不够？manifest 至少要冻结什么？</summary>

**面试意图**：判断你是否理解训练输入是数据、切分、变换和统计量组成的可追溯合同，而不是一个目录字符串。

**30 秒回答**：manifest 要绑定 content/schema/split/transform/normalizer、分母和 lineage，并在 train/eval 校验。Git SHA 加路径仍会漏掉原地替换或统计量漂移；DVC pointer 有 hash 也不等于对象本地可读。

**机制展开（约 2 分钟）**：最小链路是 `raw → revision/content hash → schema adapter → split/dedupe → transform graph → normalizer → run`。manifest 至少包含 `content_hash`、`schema_version`、`split_manifest_sha`、`transform_graph_sha`、`normalizer_sha`、分母统计和 file/episode/camera lineage。启动时写入 run bundle，eval 时重新计算；关键字段不一致就阻断。DVC 的 `.dvc` 文件能记录输出路径、hash 和依赖元数据，但不能证明远端对象已经下载、可解码或与 checkpoint 配套。

**诊断 / 证据**：对同一 run 做 JSON canonicalization 后的 manifest diff；抽 sentinel 样本比较 decode shape、dtype、颜色空间、action order 和 normalized range；保存 split、transform、normalizer 的 SHA。当前仓库有设计合同和 bad case，但没有完整项目 manifest diff A/B。

**项目挂钩**：OpenPiVLA 的 `H=15,D=72` 与 formal `limit=16` 冲突、UWM 的 normalizer/data-root 分离，都能说明 representation 和统计量必须进入 manifest；不要说这些冲突已经被项目闭环修复。

**追问树**：为什么只 hash 目录不够？normalizer 算数据还是模型的一部分？DVC pointer 文件存在能否直接启动训练？manifest 不一致时为什么要 fail closed？

**危险答案**：说“代码 commit 和路径固定就可复现”，或把 DVC 元数据存在等同于本地数据对象、checkpoint 和 controller 已验证。

**来源**：[1][7][8]　**练习状态**：unseen

</details>

## B. Multimodal Decode / Cache / Determinism

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-010</b> · multimodal decode、cache 和 determinism 怎样一起设计？</summary>

**面试意图**：检查你能否区分“加载更快”和“样本可重放”，并识别 worker、缓存和随机增强之间的边界。

**30 秒回答**：cache key 绑定媒体内容、decoder、transform、dtype/shape 和 seed policy；worker seed、epoch、sample key 要有明确 owner。记录命中率、decode error、fallback 和 wait；prefetch 只能隐藏等待，不能保证确定性。

**机制展开（约 2 分钟）**：数据流是 bytes→decode→canonical layout→resize/augment→cache→collate/mask→H2D。`num_workers` 会把 dataset、collate 和 worker init 放入 worker；`prefetch_factor`、`persistent_workers`、`pin_memory` 改变生命周期和拷贝行为。cache key 可写成 `H(content, decoder, transform, dtype, shape, seed-policy)`，并在 sidecar 校验颜色空间、shape、dtype 和 transform SHA。每个 worker 的 Python/NumPy/torch RNG、epoch 和 sample key 必须可解释；否则同一 run 可能因 worker 重启或 persistent state 得到不同增强。

**诊断 / 证据**：固定 sample key 和 seed，分别做 cold decode、cache hit、worker 数变化和重跑；比较输出 hash、mask、错误/回退计数与 p95 wait。当前证据只支持 UWM DataLoader-only stall smoke 作为读取瓶颈线索，不能外推 full training 加速或所有 cache 路径确定。

**项目挂钩**：UWM 的随机读 stall 可用于说明要先定位 I/O；OpenPiVLA 的 eager/MACA 差异可作为 kernel/兼容性追问，但不能说 eager 证明 AMP、cache 或训练吞吐都稳定。

**追问树**：cache 为什么不能只用 image path？persistent workers 如何影响随机状态？decode error 应如何处理？如何证明 cache 命中没有改变 label/mask？

**危险答案**：把 `num_workers` 调大当成 determinism 保证，或让 decode 失败静默返回上一帧并继续训练。

**来源**：[2][4][6][7][8]　**练习状态**：unseen

</details>

## C. Variable-Length / Dynamic Batching

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ENG-011</b> · variable-length VLA batch 如何减少 padding waste，同时不污染 mask 和分布式训练？</summary>

**面试意图**：判断你是否能把动态 batch 从“调参技巧”讲成有成本账本、mask 合同和可重放 sampler 的工程设计。

**30 秒回答**：先用 `w_pad = 1 - ΣL_i/(B·L_max)` 量化浪费，再按 token/frame/action budget 分桶；同时分开 `attention_mask`、`valid_mask`、`loss_mask`，记录 bucket、drop、oversize、per-rank token 和显存。动态 batch 可能改变 sampler 顺序、梯度噪声和同步语义，不能默认提升效果。

**机制展开（约 2 分钟）**：`pad_sequence` 只是把不同长度 Tensor 填到最长，`batch_first=True` 时输出为 `B×T×*`，不等于真实有效长度。先用确定性 `(length, sample_id)` 排序，在 token/frame/action budget 内组 batch；超长样本走显式 singleton 或拒绝路径。attention mask 控制 backbone 读取，valid mask 表示真实 observation/action/frame，loss mask 决定哪些位置计入目标，三者不能混用。报告同时给 samples/s、token(or frame)/s、平均 waste、p95 长度、GPU peak、drop/oversize 和 per-rank imbalance。

**诊断 / 证据**：对 fixed-sample 与 dynamic-bucket 做 matched A/B；保存 length histogram、mask coverage、每 rank workload、OOM 和 step time。若 loss 下降但显存或吞吐异常，先查 padding、mask 和 rank imbalance。当前仓库只有工程设计和 OpenPiVLA/UWM/OPD 的 shape bad cases，没有 dynamic-batch A/B。

**项目挂钩**：OpenPiVLA formatter 的 `limit` 冲突、UWM action window/normalizer、OPD mixed-format 输出都说明 padding/valid/loss mask 应进入 schema，而不是隐含在 collator；不能把 `H=15` 或一次 smoke shape 当成完整 controller 语义。

**追问树**：为什么只报 samples/s 会误导？`attention_mask` 能否代替 `loss_mask`？分布式下每 rank 长度不同怎么办？oversized sample 如何保证可复现？

**危险答案**：说 `pad_sequence` 会自动告诉你有效长度，或声称 dynamic batching 必然提高训练效果、不会改变梯度和同步。

**来源**：[3][5][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [VOL 05 Batch 2A 知识页](../knowledge/vol_05_engineering_eval_batch2a.html)：manifest、cache key、padding/mask 与项目边界。
2. PyTorch 2.13 [`torch.utils.data`](https://docs.pytorch.org/docs/2.13/data.html)：worker、prefetch、persistent worker、pin memory 与 IterableDataset 语义。
3. PyTorch 2.13 [`pad_sequence`](https://docs.pytorch.org/docs/2.13/generated/torch.nn.utils.rnn.pad_sequence.html)：padding 输出和 `batch_first`/`padding_value`。
4. Hugging Face Datasets v4.8.4 [Cache management](https://huggingface.co/docs/datasets/v4.8.4/en/cache) 与 [Cache fingerprint](https://huggingface.co/docs/datasets/v4.8.4/en/about_cache)：cache reload 与 transform fingerprint 的 supporting 语义。
5. Hugging Face Transformers v5.14.0 [Data Collator](https://huggingface.co/docs/transformers/v5.14.0/en/main_classes/data_collator)：padding/collation supporting 语义。
6. PyTorch 2.13 [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)：随机状态与确定性边界。
7. 本仓库 [OpenPiVLA Batch 2 evidence freeze](../sources/openpivla_batch2_evidence_freeze.html)、[UWM/LIBERO inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
8. 本仓库 [VOL 05 ENG-004..006 local artifact gate](../sources/vol_05_local_artifact_gate_eng004_006.html)。
