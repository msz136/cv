# VOL 05 Engineering / Evaluation：Reproducibility、Sampler Cursor 与 Resume（ENG-013）

> 状态：`drafted / knowledge_15_of_44 / cards_15_of_44_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-013`；[单张题卡](../questions/vol_05_engineering_eval_eng013.html)已在独立切片生成并保持 unseen。  
> 来源入口：[ENG-013 Reproducibility Source Freeze](../sources/vol_05_eng013_reproducibility_source_freeze.html)。  
> 核心边界：固定 seed、可复现实验、epoch-boundary resume、mid-epoch exact resume 是不同强度；没有 replay artifact 时不把“能 load checkpoint”说成“可精确续训”。

## 问题（Question）

`VLA-ENG-013`：VLA 训练怎样设计 seed、determinism、DistributedSampler 和 sampler cursor，才能让实验可复现、故障可诊断、训练可恢复？

## 知识地图位置与前置依赖

```text
manifest / schema / transform
          ↓
dataset order + sampler + worker RNG
          ↓
batch IDs + augmentation + model RNG
          ↓
optimizer/scaler + checkpoint
          ↓
epoch-boundary or mid-epoch replay
```

前置：

- `VLA-ENG-006` 的 checkpoint lineage、optimizer/scaler 与 load smoke。
- `VLA-ENG-009..011` 的 manifest、cache、dynamic batch、padding/mask 合同。
- ENG-013 source freeze 中的 PyTorch 2.13 Reproducibility、DistributedSampler 和 RNG API。

## 1. 三种“复现”强度

| 强度 | 目标 | 必须冻结/保存 | 不能用什么替代 |
| --- | --- | --- | --- |
| 固定 seed | 启动时随机源可解释 | Python、NumPy、torch CPU/CUDA、worker seed policy | 一个整数 seed |
| 实验复现 | 相同输入和协议得到可比 run | code/data/transform/env、sampler epoch/seed、RNG、metric protocol | 只比较最终 loss |
| 精确中途续训 | 从 step (k) 后得到相同 next sample/step | cursor、next IDs、所有 RNG、optimizer/scaler、worker/prefetch policy | checkpoint 能 load |

PyTorch 2.13 明确不保证跨 release、commit、platform、CPU/GPU 完全复现；deterministic algorithms 也可能更慢。[1] 因此面试回答应先说明复现强度和容忍度，再谈 seed。

## 2. Seed ownership：随机源不是一个变量

### 2.1 随机源分层

| 随机源 | 典型 owner | 保存/初始化动作 | 常见漏项 |
| --- | --- | --- | --- |
| Python `random` | 数据增强/采样辅助代码 | `random.getstate()` / `setstate()` | 只保存 torch seed |
| NumPy legacy / `Generator` | decode、几何、增强库 | singleton state 或每个 Generator state | `random.seed()` 不覆盖新 Generator |
| torch CPU | model/data augmentation | `torch.get_rng_state()` / `set_rng_state()` | 误以为包含 CUDA |
| CUDA per device | dropout、kernel、采样 | `torch.cuda.get_rng_state_all()` / set | 只保存 rank-0 device |
| DataLoader worker | worker transform | `worker_init_fn` + DataLoader `generator` | worker 重启/持久化后的状态漂移 |
| sampler | shuffle/index order | epoch、seed、rank/world、cursor 或 replay trace | 只保存 epoch |

`torch.get_rng_state()` 官方 API只覆盖 CPU default generator；CUDA 要使用 all-device API。NumPy 1.26 还提醒 legacy `random.seed` 只是 singleton RandomState 的便利接口，新的 `Generator` 必须单独管理。[3][4]

### 2.2 一个可审计的 run identity

```text
run_id
  = code SHA + environment lock + dataset/transform manifest
  + world_size/rank + sampler policy + seed policy
  + model/optimizer/scaler/processor versions
```

这不是某个框架的默认字段，而是把随机源、数据顺序和模型状态放在同一条 lineage 上的工程合同。

## 3. DistributedSampler：官方前提与 `set_epoch`

### 3.1 官方语义

PyTorch 2.13 的 `DistributedSampler` 把 dataset 子集分给不同 process，并假设 dataset 大小恒定、每次以相同顺序返回相同元素。`seed` 在 distributed group 中应一致；`drop_last=True` 丢尾部，`False` 会补 index 使 replica 可整除。[2]

可以用一个面试级抽象表示每个 epoch 的 index 流：

\[
I_{e,r}=\operatorname{partition}_r\left(\operatorname{permute}(N;\;s+e)\right),
\]

其中 (N) 是 dataset index 集合，(s) 是共同 sampler seed，(e) 是 epoch，(r) 是 rank；`partition` 还受 `world_size`、`drop_last` 和 padding policy 影响。这个式子是机制抽象，不是承诺 PyTorch 内部恰好使用 `s+e` 的源码公式。

### 3.2 `set_epoch` 的位置

官方文档明确：distributed training 中，每个 epoch 在创建 DataLoader iterator 前调用 `sampler.set_epoch(epoch)`，否则多 epoch 可能一直使用相同 ordering。[2]

```python
for epoch in range(start_epoch, num_epochs):
    # Change the epoch-dependent sampler order before creating the iterator.
    if distributed:
        sampler.set_epoch(epoch)
    for batch in loader:
        train_step(batch)
```

忘记 `set_epoch` 不只是性能问题：它改变数据顺序合同，可能让多 epoch shuffle 冻结；如果把它放在 resume 后错误的位置，还可能跳过或重复一段 index。

## 4. Epoch-boundary 与 mid-epoch resume

### 4.1 Epoch-boundary resume

如果只允许在 epoch 完成后保存，resume 合同相对清晰：

```text
checkpoint
  + completed_epoch
  + next_epoch sampler seed/set_epoch policy
  + model/optimizer/scaler/RNG states
  + manifest + world-size policy
```

验证重点是：恢复后第一个 epoch 的 sample IDs、loss、optimizer step 和 metric protocol 与从头运行一致或在声明的 tolerance 内一致。即使这样，跨硬件/版本也不能宣称 bitwise identical。

### 4.2 Mid-epoch exact resume

仅保存 `step_in_epoch` 不够，因为以下因素会让 optimizer step 与实际消费位置不等价：

- `drop_last`、DistributedSampler padding 或过滤样本；
- dynamic batching 改变每步样本数；
- DataLoader worker prefetch 已经取出但尚未完成 optimizer step 的 batch；
- transform counter、随机增强和异步 decode 状态；
- rank 间不同的 error/retry 或 skipped sample。

因此需要保存或重放：

```text
epoch + sampler seed + rank/world_size + dataset order
accepted sample IDs / next expected IDs
batch policy + drop/filter decisions
worker/prefetch policy + all RNG states
model/optimizer/scaler state
```

如果真实 cursor 无法保存，安全降级为“epoch-boundary resume”或“固定 request trace replay”，不要把 step number 当作 sampler cursor。

## 5. Determinism 不是无条件的 bitwise equality

### 5.1 可复现目标分层

| 目标 | 比较对象 | 适用场景 |
| --- | --- | --- |
| sample replay | next sample IDs / request keys | 数据和 sampler 调试 |
| transform replay | decode、augment、mask、dtype hash | 数据管线回归 |
| step replay | loss、grad norm、optimizer/scaler step | checkpoint/resume smoke |
| metric replay | eval manifest、seed、episode result | 论文/项目结果复核 |
| bitwise replay | 每个 tensor 完全相等 | 仅在固定平台/版本/算子且成本可接受时尝试 |

“deterministic=True”或单个 seed 不能替代协议、环境和 artifact manifest。确定性算法可能降低性能，应该把速度 trade-off 记录下来。[1]

### 5.2 Worker seed 与 generator

PyTorch Reproducibility 文档给出用 `worker_init_fn` 和 DataLoader `generator` 控制 worker reseed 的示例。工程上还要固定：worker 数、persistent worker policy、prefetch、in_order、collate、error/fallback、augmentation counter。否则同一 seed 也可能消费不同的随机调用次数。

## 6. 最小 checkpoint / replay smoke

```python
def resume_smoke(bundle, fixed_requests):
    # Restore model/optimizer/scaler before drawing the next random number.
    restore_model_optimizer_scaler(bundle)
    restore_python_numpy_cpu_cuda_rng(bundle)
    restore_sampler_or_replay_cursor(bundle)
    # Compare IDs and one step, not only whether load_state_dict succeeds.
    result = next_batch_and_step(fixed_requests)
    assert result.sample_ids == bundle.expected_next_sample_ids
    assert close(result.loss, bundle.expected_loss, atol=bundle.loss_tolerance)
    return result
```

建议最少两条 smoke：

1. epoch-boundary：保存 epoch 完成后的 bundle，比较下一 epoch 的 sample IDs 和一小步结果。
2. mid-epoch：在固定 request trace 的 step (k) 保存，恢复后比较 next IDs、augmentation/RNG、loss、optimizer step、scaler state。

只看 checkpoint 是否能 load、最终 loss 是否接近，不能证明 sampler cursor 和随机状态已恢复。

## 7. 项目证据边界

ENG-004..006 本地 artifact gate 盘点到训练 summary、load report、normalizer、ZeRO 配置和 final-only manifest，但没有 fixed-batch continuation、per-rank RNG、sampler cursor 或 next-sample replay artifact。因而当前个人项目只能说“恢复合同需要这些字段”，不能说已经完成精确续训。

UWM 的 DataLoader-only stall smoke 说明数据等待会影响实验节奏，但不提供 deterministic replay；OpenPiVLA/OPD inventory 也没有完整 RNG/cursor bundle。项目回答保持 `evidence missing / do not claim`。

## 8. 面试抓手、trade-off 与 bad case

### 30 秒抓手

“我先区分 seed、实验 replay 和精确 mid-epoch resume。PyTorch 的 DistributedSampler 要求 dataset size/order 稳定、各 rank 共享 seed，并在每个 epoch 调 `set_epoch`；CPU/CUDA/Python/NumPy/worker RNG 要分层保存。中途恢复不能只记 step，还要有 sampler cursor 或固定 request trace、next sample IDs 和 prefetch policy。没有 replay smoke，我只会说 checkpoint 可加载，不会说精确续训。”

### Trade-off

- 更强 determinism 通常增加状态保存、同步和调试成本，可能牺牲吞吐。
- epoch-boundary resume 更简单但丢失中途计算；mid-epoch resume 更精确却要处理 prefetch、filter、dynamic batch 和 worker 状态。
- 固定 request trace 便于回归，却不一定代表真实随机 sampler 的分布。

### Bad case

1. 所有 rank 使用不同 sampler seed，结果“可运行”但数据覆盖和指标不可比。
2. 忘记 `set_epoch`，多 epoch 一直复用相同顺序，却只把问题归因于模型过拟合。
3. 保存 CPU RNG 而遗漏 CUDA/NumPy/worker state，resume 后 loss 仍下降就误判为精确恢复。
4. dynamic batching 或 skipped sample 后用 `step_in_epoch` 直接跳过数据，导致重复/遗漏窗口。

## 9. 结论与下一步

官方来源支持 seed、worker reseed、DistributedSampler、`set_epoch`、CPU/CUDA RNG state API 和 NumPy legacy seed 的语义；sampler cursor、prefetch replay、dynamic-batch resume、完整 checkpoint bundle 是工程合同。`VLA-ENG-013` 单张题卡已生成但没有真实口述，仍为 `unseen`；不升级个人项目证据，ENG-014..016 重新走 source-first gate。

## References

1. PyTorch 2.13 [Reproducibility](https://docs.pytorch.org/docs/2.13/notes/randomness.html)。
2. PyTorch 2.13 [DataLoader / DistributedSampler](https://docs.pytorch.org/docs/2.13/data.html#torch.utils.data.distributed.DistributedSampler)。
3. PyTorch 2.13 [CPU RNG state](https://docs.pytorch.org/docs/2.13/generated/torch.get_rng_state.html) / [set state](https://docs.pytorch.org/docs/2.13/generated/torch.set_rng_state.html)。
4. PyTorch 2.13 [CUDA RNG states](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.get_rng_state_all.html) / [set all](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.set_rng_state_all.html)。
5. NumPy 1.26 [`random.seed`](https://numpy.org/doc/1.26/reference/random/generated/numpy.random.seed.html)。
6. 本仓库 [ENG-013 Source Freeze](../sources/vol_05_eng013_reproducibility_source_freeze.html)、[VOL 05 Batch 1 official review](../sources/vol_05_batch1_independent_fact_review.html) 与 [ENG-004..006 artifact gate](../sources/vol_05_local_artifact_gate_eng004_006.html)。
