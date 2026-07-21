# VOL 05 ENG-004..006：本地 Artifact Gate 复核

> 状态：`artifact_audit_slice / WARN`  
> 盘点日期：2026-07-17  
> 证据截止：2026-07-17  
> 盘点范围：UWM / RoboCasa transfer snapshot、OPD / point remote-sync snapshot，以及它们对 `VLA-ENG-004..006`（分布式配置、数值/梯度合同、checkpoint lineage）的本地 metadata、config、load report 和 binary gate。  
> 结论先行：本页原始 2026-07-17 snapshot 范围内存在可核验的训练 summary、world-size/DeepSpeed 配置、action normalizer、checkpoint load report 和 OPD ZeRO-2/3 manifest，但没有实际 `.pt/.pth/.ckpt/.safetensors/.bin` 文件。2026-07-21 对用户提供的 `C:\Users\mousongzhe\project` 根目录补做扫描后，在 `wm/uwm_robocasa_transfer/_downloads/libero_90.pt` 发现并冻结了 UWM base binary；该发现已由独立 [UWM base checkpoint immutable manifest gate](uwm_libero90_checkpoint_immutable_manifest_gate.html) 记录。它只关闭 base binary existence/hash，不关闭 RoboCasa fine-tune `models.pt`、normalizer、完整 resume 或 closed-loop scorer。

## 问题（Question）

本记录回答：在已经完成官方机制复核后，当前工作区是否存在足以关闭 `ENG-004..006` 的本地 artifact？哪些字段可以进入面试项目 hook，哪些仍需补件？

本次是只读盘点，不执行远端同步、训练、加载权重或修改项目目录。路径、大小和 SHA 只证明当前本地 snapshot 的内容，不证明远端路径仍可访问或二进制与 report 同源。

## 盘点边界与证据等级

| 等级 | 本次含义 | 可使用的口径 |
| --- | --- | --- |
| `local-direct` | 当前机器可直接读取的 JSON、config、log 或 report | “本地 snapshot 记录了……” |
| `report-supported` | 本地 report 记录了远端命令/路径/结果，但对应 binary 不在 snapshot | “report 记录 load/save 过程……” |
| `config-only` | 只有配置或 manifest，没有执行结果 | “配置计划/声明为……” |
| `missing-binary` | 搜索范围内没有 checkpoint binary | 不能称 checkpoint-verified |
| `blocked` | 缺少 optimizer/scheduler/RNG/sampler cursor、固定 batch diff 或独立 resume step | 不能称完整 resume |

扫描根目录：

```text
C:\Users\mousongzhe\Project\remote_sync\muxi_20260629
C:\Users\mousongzhe\agent\remote_training_pipeline_v2
```

两处原始根目录在 2026-07-17 扫描中均找到 `0` 个 `.pt/.pth/.ckpt/.safetensors/.bin` 文件；因此当时后文所有 checkpoint 结论都显式区分 metadata/report 与 binary。该扫描不覆盖后续用户明确提供的 `C:\Users\mousongzhe\project` 根目录；新根目录下的 base binary 结果不回填成旧 snapshot 当日已知事实。

## 0.1 2026-07-21 范围补充（不改写原始 snapshot）

新 gate 对 `C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer\_downloads\libero_90.pt` 逐文件重算 SHA-256：`4,044,929,076` bytes，hash `E43C562E1D5145662006877AAC0FB30C3C5D57302AEFC16524DA2D862D694602`。它支持“UWM LIBERO base binary 当前在 project copy 中可读”，但旧报告中的 `checkpoint_load_report.json` 仍只记录远端路径，尚未证明该 report 对应的 loader 进程实际使用了这一个 hash。target fine-tune `models.pt`、target normalizer 与 fresh-load parity 仍缺。

## 1. UWM：训练与 checkpoint metadata 是 local-direct

### 1.1 `true_save_smoke`：保存合同和 partial-load 报告

本地文件：

```text
C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\true_save_smoke_20260625_155910\train_summary.json
C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\true_save_smoke_20260625_155910\artifacts\target_atomic_seen_action_normalizer.json
```

`train_summary.json` 直接记录：`save_checkpoint=true`、每 step 保存、请求 2 steps、`world_size=8`、backend `nccl`、DeepSpeed 开启、`checkpoint_report.matched_count=433`、`skipped_count=21`。normalizer 文件记录 12 维 action 的 count、min/max、scale/offset，SHA-256 为 `28cc40b778dfc087fefd0cbdd5ba9918ae2902f3372b75dfb3612c5bb289807f`。

但 summary 中的 `checkpoint_path` 是 `/data/msz/.../checkpoints/models.pt`，对应本地 run 目录没有 `checkpoints/models.pt`；因此这是 `local-direct metadata + report-supported path`，不是本地权重 load smoke。

### 1.2 `human300_native_pretrain`：更长 run 仍缺二进制

本地 bundle 包含：

```text
train_summary.json                         SHA 359dd24da82bdb2cf350cb049a09299cfb0f4ba295105e6722e565c0afc03f6d
artifacts/checkpoint_load_report.json      SHA 03feab5c36a4883eb2a203450dc628cfe3d28740e8a7cffbe6247b4612d3397a
artifacts/human300_action_normalizer.json  SHA 385cde0e5375aebadb4ccbad8860bfbf343aa30d4fb2b8cd3538248748fde6f6
ds_config_effective.json                   SHA 2bf8216f04391ce4323fc79ae74aae9728e8b13f8d4057f281734a0a4da54642
```

summary 记录 `steps=1757`、`world_size=8`、DeepSpeed 开启、每 1757 steps 保存；effective config 是 micro batch 128、global train batch 1024、gradient accumulation 1、gradient clipping 1.0，`zero_optimization.stage=0`。这说明该 run 的本地记录不是 ZeRO-2/3 运行证据。

`checkpoint_load_report.json` 记录远端 `/data/msz/uwm_robocasa_transfer_muxi/checkpoints/libero_90.pt`、`checkpoint_step=100000`、匹配 446 个 keys、跳过 8 个 keys；在该 report 的原始 snapshot 中没有随 bundle 提供 `.pt` 文件，不能独立验证权重 hash、processor、optimizer 或可复现输出。2026-07-21 新发现的 C01 base binary 只为后续 hash gate 提供了候选文件，不自动把旧 report 与 C01 绑定。

### 1.3 UWM fine-tune：存在 report-supported parent checkpoint

`human300_to_target_atomic_seen_native.../artifacts/checkpoint_load_report.json` 记录 parent `/data/msz/.../human300_native_pretrain.../checkpoints/models.pt`、`checkpoint_step=1756`。同一目录有 target normalizer 和 DeepSpeed effective config，但没有 parent 或 child binary。该证据支持“训练命令引用了某个 parent checkpoint”，不支持“本地可加载并续训”。

## 2. OPD / point：ZeRO 配置存在，lineage manifest 明确保留缺口

本地配置：

```text
C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\point\configs\zero2.json
C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\point\configs\zero3_opd_maca_gradclip5.json
```

`zero2.json` 是 `stage=2`、BF16 开启、FP16 关闭、gradient clipping 1.0；`zero3_opd_maca_gradclip5.json` 是 `stage=3`、BF16 开启、FP16 关闭、gradient clipping 5.0，并设置了 Stage-3 bucket/persistence 参数。两份文件是 `config-only`：它们证明配置存在，不证明对应 run 已完成、性能更好或 checkpoint 可恢复。

两个 run manifest 的关键字段：

| manifest | batch/accumulation | checkpoint policy | lineage 边界 |
| --- | --- | --- | --- |
| `seed0_100k_mb4_v1_manifest.json` | per-device 4、accum 4、effective 128、预计每 expert 782 steps | `final_model_only_no_intermediate_checkpoints` | 没有中间 checkpoint；仅声明 final weights 输出 |
| `seed0_continue100k_from100k_mb1_filtered_stdtrainer_maxnorm5_v1_manifest.json` | per-device 1、accum 4、effective 32、max grad norm 5.0、预计 3125 steps | `final_model_only_no_intermediate_checkpoints` | `continue_from_each_seed0_100k_final_weights_no_optimizer_state`，明确没有 optimizer state |

这组 local-direct manifest 对 `ENG-005` 的 effective batch/clip 合同和 `ENG-006` 的 lineage 风险很有价值，但不能被写成“OPD 已完成 ZeRO-3 resume”。

## 3. 节点级 Gate 结论

| 节点 | 当前 verdict | 已有证据 | 尚缺最小补件 |
| --- | --- | --- | --- |
| `VLA-ENG-004` | `PASS WITH WARNING` | UWM world-size/DeepSpeed summary；OPD ZeRO-2/3 configs；UWM effective config 明确 stage 0 | 对应 run 的 effective config、rank/world-size、save/load log 与 binary hash 需一一绑定；不能用 config 替代执行结果 |
| `VLA-ENG-005` | `PASS WITH WARNING` | OPD BF16/FP16/clip/accum config；UWM log 中出现 GradScaler、gradient accumulation、throughput/profile 配置 | overflow/scale/grad-norm/clip-ratio 时间序列；固定 effective batch 的 matched A/B；不能只凭 BF16 或 GradScaler warning 说稳定 |
| `VLA-ENG-006` | `PASS WITH WARNING` | UWM save summary、checkpoint load reports、现已独立冻结的 base binary hash、normalizer SHA、OPD final-only/无 optimizer state manifest | base hash 与旧 load report 的 shared run identity、target fine-tune binary、optimizer/scheduler/scaler/RNG/sampler cursor、processor/normalizer/config hash、固定 batch pre/post-load diff、续训一步日志 |

## 4. 最小验收脚本合同

下面是拿到与 run manifest 绑定的 binary 后应执行的只读验收顺序；C01 base binary 的 hash 已有，但 target fine-tune binary 与 shared run identity 仍缺，因此本次不把整个合同标成已执行：

```python
def checkpoint_gate(run_dir, fixed_batch):
    # 1) Resolve every path and reject a report-only remote path.
    bundle = load_manifest(run_dir)
    assert exists_local(bundle.model_binary)  # C01 base 可满足；target models.pt 仍待补

    # 2) Bind model/processor/normalizer/config hashes before loading.
    verify_hashes(bundle.model, bundle.processor, bundle.normalizer, bundle.config)

    # 3) Compare a fixed batch before save and after an independent load.
    before = model_forward(bundle.model, fixed_batch)
    save_full_bundle(bundle)
    loaded = independent_load(bundle)
    after = model_forward(loaded, fixed_batch)
    assert close_enough(before, after)

    # 4) Continue one optimizer step and record finite loss/grad and step + 1.
    resume_one_step(loaded, fixed_batch)
    assert finite_metrics() and step_incremented()
```

该脚本是验收合同，不是本地执行结果；不得把 report 中的 `save_checkpoint=true` 代替第 1–4 步。

## 5. 证据摘要与真实性边界

本次最强可用口径是：

> “原始 remote-sync snapshot 里我能复核到 8 卡 DeepSpeed 训练摘要、action normalizer、checkpoint load report、OPD 的 ZeRO-2/3 配置和 final-only/no-optimizer-state manifest；随后在项目 copy 中又冻结了 UWM `libero_90.pt` base binary 的 SHA。这个 hash 只关闭 base 文件身份，不等于 target fine-tune `models.pt`、normalizer、完整 resume 或 benchmark 已闭合。”

不能使用的口径包括：

1. “本地已经完成 RoboCasa checkpoint reload”——C01 只证明 base binary 存在；原始 report 仍是远端路径引用，target reload 需要独立 fresh-process artifact。
2. “OPD 已用 ZeRO-3 并验证性能提升”——配置文件不等于完整 run/performance comparison。
3. “保存成功所以可以无缝 resume”——缺 optimizer/scheduler/RNG/sampler cursor 与固定 batch diff。
4. “有 normalizer JSON 所以 action contract 已闭合”——仍需与 checkpoint/processor/controller roundtrip 对齐。

总体 verdict 保持 `WARN`：base binary identity 已提升到 `local-direct`，但 target binary、optimizer lineage、独立 load/resume 和 matched performance 仍是 release gate。

## 参考来源（References）

1. UWM local snapshot：`C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\true_save_smoke_20260625_155910`，selected file SHA 见正文。
2. UWM local snapshot：`C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\human300_native_pretrain_20260629_104957_human300_native`，selected file SHA 见正文。
3. UWM local snapshot：`C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\human300_to_target_atomic_seen_native_20260629_104957_human300_native`。
4. OPD local snapshot：`C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\point\configs` 与 `point\outputs`，selected config/manifest SHA 见正文。
5. 本仓库 [VOL 05 Batch 1 官方机制复核](vol_05_batch1_independent_fact_review.html)。
6. 本仓库 [VOL 05 Engineering / Evaluation 知识页](../knowledge/vol_05_engineering_eval.html) 与 [Batch 1 题卡](../questions/vol_05_engineering_eval.html)。
7. 本仓库 [UWM `libero_90.pt` 本地 immutable checkpoint manifest gate](uwm_libero90_checkpoint_immutable_manifest_gate.html)。
