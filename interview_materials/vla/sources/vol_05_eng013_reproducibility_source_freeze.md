# VOL 05 ENG-013：Seed、Determinism、Sampler Cursor 与 Resume 来源冻结

> 状态：`source_frozen / VLA-ENG-013_knowledge+card_drafted / unseen / WARN`  
> 冻结日期：2026-07-17  
> 对应问题：`VLA-ENG-013`——seed、determinism、sampler cursor 与复现实验如何设计？  
> 当前边界：本文件只冻结官方语义和工程合同；下游[知识正文](../knowledge/vol_05_engineering_eval_eng013.html)与[单张题卡](../questions/vol_05_engineering_eval_eng013.html)已生成，本地复现实验结论和掌握状态仍后置。  
> 相关来源：[VOL 05 Batch 1 官方复核](vol_05_batch1_independent_fact_review.html) 已核对 PyTorch 2.13 Reproducibility；本文件补齐 DistributedSampler 与 RNG state API。

## 1. 三个强度不要混为一谈

| 强度 | 要回答的问题 | 典型证据 | 本轮结论 |
| --- | --- | --- | --- |
| 固定 seed | 同一次启动是否使用可解释的随机源？ | Python/NumPy/torch CPU/CUDA seed、worker seed | API 可控制，但 seed 不是完整复现证明 |
| 可复现实验 | 同一 code/data/env/protocol 能否重现样本顺序、指标和 artifact？ | manifest、RNG state、sampler epoch/seed、run bundle、matched rerun | 需要工程合同和 replay smoke |
| 精确中途续训 | 从 step (k) 恢复后，下一批 sample、梯度、optimizer/scaler 和结果是否一致？ | sampler cursor、worker/prefetch policy、所有 RNG state、fixed-request diff | PyTorch 页面不自动提供；必须自行设计/验证 |

“我设置了 `seed=42`”只覆盖第一层的一部分，不能直接回答后两层。

## 2. 冻结来源与版本

HTML 页面使用规范化正文指纹：移除 `script/style/nav/header/footer/svg`，合并正文空白后计算 normalized main-text SHA-256；连续 GET 的 raw HTML 可能包含动态资源，不作为稳定指纹。

| 来源 | 版本 / URL | normalized text 长度 / SHA-256 | 支持内容 | 不支持内容 |
| --- | --- | --- | --- | --- |
| PyTorch Reproducibility | [2.13 randomness](https://docs.pytorch.org/docs/2.13/notes/randomness.html) | `11230` / `5a19f15c86d56dbd0f9ea0572b86e960475328c99c36408cfb82d4fce90a03c5` | 跨 release/platform 不保证完全复现、deterministic trade-off、torch/Python/NumPy RNG、DataLoader worker reseed | 固定 seed 后任意环境 bitwise identical |
| PyTorch DataLoader / DistributedSampler | [2.13 data](https://docs.pytorch.org/docs/2.13/data.html#torch.utils.data.distributed.DistributedSampler) | `47667` / `9032517582f5a20a811008e4f71a81e356d058380cfc985b552ef338b1cecf5f` | worker generator、Iterable/Map semantics、DistributedSampler 的 constant-size/order、seed、drop_last、`set_epoch` | mid-epoch cursor checkpoint、全局 replay contract |
| `torch.get_rng_state` | [PyTorch 2.13](https://docs.pytorch.org/docs/2.13/generated/torch.get_rng_state.html) | `1100` / `68f3efc879a6a9c84a3fbf7ff72c8981c788b021b88698b5fbc58b1bcdc72050` | CPU default generator state 是 ByteTensor | CUDA、NumPy、Python 或 sampler 状态自动包含其中 |
| `torch.set_rng_state` | [PyTorch 2.13](https://docs.pytorch.org/docs/2.13/generated/torch.set_rng_state.html) | `1142` / `d5c6b11ba57b56686c4b5d88bf2f55dcea7cbc923e0a7399584d4245dcddd7b4` | 恢复 CPU RNG state；CUDA 需其他 API | 完整训练 resume 自动恢复 |
| `torch.cuda.get_rng_state_all` / `set_rng_state_all` | [get](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.get_rng_state_all.html) / [set](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.set_rng_state_all.html) | `1050` / `25cd8d0b28fcd18c4d3a02d8ed537d512abc6a62b2eb1c57af3efe1a8c09fe0b`; `1097` / `2eb06b6c1058f8595e5b28f69fece528b725527c1fe9fd6ec3f81dba3284e237` | 所有 CUDA device 的 ByteTensor state 读写 | Python/NumPy/worker/sampler cursor 自动恢复 |
| NumPy `random.seed` | [NumPy 1.26](https://numpy.org/doc/1.26/reference/random/generated/numpy.random.seed.html) | `437` / `312e83995a2006d130efb04f802be1cbad551da045a54e7af2462ae99d3b9ef3` | legacy singleton RandomState reseed；文档建议 dedicated Generator | 新 Generator 实例、PyTorch worker 或完整 run replay |

## 3. 官方语义核对

### 3.1 PyTorch reproducibility 的否定边界

PyTorch 2.13 明确声明：跨 release、individual commits、平台，以及 CPU/GPU 之间，完全可复现结果不被保证；deterministic operations 往往更慢。文档建议分别控制 torch、Python、NumPy 等随机源，并用 DataLoader 的 `worker_init_fn` 和 `generator` 处理 worker reseed。[1]

因此安全表达是“在固定 release/platform/device 与明确随机源后，限制不确定性并做 replay”，不是“seed 后完全复现”。

### 3.2 DistributedSampler 的前提与 `set_epoch`

官方文档把 `DistributedSampler` 定义为把 dataset 子集分配给各 process，并假设 dataset 大小恒定、每次以相同顺序返回相同元素。`seed` 在 distributed group 中应一致；`drop_last=False` 时 sampler 会补 index 以使各 replica 可整除，`drop_last=True` 时丢掉尾部。文档还明确：每个 epoch 创建 DataLoader iterator 前调用 `set_epoch(epoch)`，否则多 epoch 会一直使用相同顺序。[2]

这支持：

- `dataset length/order`、`world_size/rank`、`seed`、`shuffle`、`drop_last` 必须进入 run manifest。
- resume 时不能只恢复 `epoch`；若从 epoch 中途恢复，还要知道已消费的 index/cursor 和 DataLoader/worker 行为。
- 把 `set_epoch` 放错位置会改变或冻结 shuffle 顺序，属于可诊断的 first-failure。

这不支持“DistributedSampler 自动保存 cursor”或“任意 dataset 动态增删仍可精确恢复”。

### 3.3 RNG state API 的范围

`torch.get_rng_state()` / `set_rng_state()` 针对 CPU default generator；CUDA 的 `get_rng_state_all()` / `set_rng_state_all()` 针对所有 CUDA device。它们是可组合的 state API，不是训练 checkpoint bundle：Python random、NumPy Generator、worker seed、sampler generator、prefetch queue 和 dataset transform counter 仍要单独处理。

NumPy 1.26 的 `random.seed` 是 legacy singleton RandomState 的便利接口，文档建议 dedicated `Generator`。因此项目若同时使用 legacy API 和 Generator，必须记录每个 owner，不能只保存一个整数 seed。

## 4. Resume / Sampler Cursor 工程合同

下面是本仓库建议的 resume bundle，不是 PyTorch 默认 schema：

```text
model / optimizer / scaler
code + environment + dataset/transform manifest
python RNG + numpy RNG/Generator states
torch CPU RNG + per-CUDA-device RNG states
world_size + rank + sampler seed/shuffle/drop_last
dataset length/order + epoch + step_in_epoch + sampler cursor
worker_init policy + DataLoader generator + prefetch/persistent policy
next expected sample IDs / request trace
```

`step_in_epoch` 不能自动等于 sampler cursor：batch size、drop_last、dynamic batching、worker prefetch、filtered sample 和 distributed padding 都可能让“已完成 optimizer step 数”与“已消费样本位置”不一致。若无法保存真实 cursor，应使用固定 request trace 或 deterministic skip/replay，并把结论降级为“epoch-boundary resume”。

## 5. 最小 replay smoke

```python
def resume_smoke(bundle, fixed_requests):
    # Restore model/optimizer/scaler before consuming the next request.
    restore_training_state(bundle)
    restore_python_numpy_torch_cuda_rng(bundle)
    restore_sampler_or_replay_cursor(bundle)
    # Compare exact next sample IDs and one-step outputs, not only loss text.
    got = next_batch_and_step(fixed_requests)
    assert got.sample_ids == bundle.expected_next_sample_ids
    assert close(got.loss, bundle.expected_loss, atol=bundle.tolerance)
    return got
```

至少做两种测试：

1. epoch-boundary resume：保存 epoch 完成后的 bundle，比较下一 epoch 的 sample IDs 和 loss。
2. mid-epoch resume：在固定 request trace 的 step (k) 保存，恢复后比较下一批 IDs、RNG-dependent augmentation、loss、optimizer step 和 scaler state。

只比较最终 loss 或只确认 checkpoint 能 load，不能证明 sampler cursor、RNG、transform 和数据顺序被恢复。

## 6. 不能支持的强 claim

| 强 claim | 结论 | 安全替代 |
| --- | --- | --- |
| `seed=42` 后完全复现 | REJECT | 固定主要 RNG，并在固定环境做 replay |
| `DistributedSampler` 自动恢复中途位置 | REJECT | 记录/重放 sampler cursor，或明确只支持 epoch-boundary |
| 保存 `torch.get_rng_state()` 就够了 | REJECT | CPU/CUDA/Python/NumPy/worker/sampler 分层保存 |
| 每 epoch 忘记 `set_epoch` 只影响性能 | REJECT | 会使多 epoch shuffle 顺序保持相同 |
| checkpoint 能 load 就证明 resume 正确 | REJECT | 做 fixed-batch/request next-step smoke |
| 动态 batch 与 prefetch 不影响 cursor | REJECT | 把 batch policy、drop/filter/prefetch 作为 resume 合同 |

## 7. 本地项目证据边界

上一轮 ENG-004..006 artifact gate 只盘点了训练 summary、load report、normalizer、ZeRO 配置和 final-only manifest；没有 fixed-batch continuation、per-rank RNG、sampler cursor 或 next-sample replay artifact。因此本节点不能把任何个人项目写成“已完成精确 resume”。

UWM DataLoader-only stall smoke 说明数据等待可以影响实验节奏，但不提供 sampler cursor 或 deterministic replay 证据。OpenPiVLA/OPD 的现有 inventory 也没有为本节点提供完整 RNG/cursor bundle；项目 hook 保持 `evidence missing / do not claim`。

## 8. Source Freeze 结论与下一步

`VLA-ENG-013` 已达到 `source_frozen / knowledge+card_drafted / unseen / WARN`：

- seed、不确定性、DistributedSampler、RNG API 的官方语义已冻结。
- sampler cursor、dynamic batching resume、worker prefetch replay、完整 checkpoint bundle 是工程合同。
- 没有本地 fixed-batch/mid-epoch resume artifact，不升级项目真实性或 ownership。

下一步优先做 `VLA-ENG-013` 真实口述或独立 wording review；ENG-014..016 继续 source-first 后置。

## References

1. PyTorch 2.13 [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)。
2. PyTorch 2.13 [torch.utils.data / DistributedSampler](https://docs.pytorch.org/docs/2.13/data.html#torch.utils.data.distributed.DistributedSampler)。
3. PyTorch 2.13 [get/set RNG state](https://docs.pytorch.org/docs/2.13/generated/torch.get_rng_state.html)、[CUDA all-device states](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.get_rng_state_all.html)。
4. NumPy 1.26 [`random.seed`](https://numpy.org/doc/1.26/reference/random/generated/numpy.random.seed.html)。
5. 本仓库 [VOL 05 Batch 1 official fact review](vol_05_batch1_independent_fact_review.html) 与 [ENG-004..006 artifact gate](vol_05_local_artifact_gate_eng004_006.html)。
