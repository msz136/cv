# VOL 08 SYS-001：可复现的 VLA 训练—评估平台

> 状态：`drafted / SYS-VLA-001 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[SYS-001 Source Freeze](../sources/vol_08_sys001_vla_training_eval_platform_source_freeze.html)。

## 问题（Question）

面试中的“设计一个 VLA 训练/评估平台”不是画几个服务框，而是要保证：数据、模型、processor/normalizer、checkpoint、评估协议、rollout artifact 和结果解释能被同一个 lineage graph 串起来。否则训练 loss、offline proxy、simulator success 和真机结果会互相污染。

本页回答：

1. 怎样定义 dataset、run、bundle、evaluation 和 rollout contract？
2. 如何把 determinism、checkpoint lineage、processor/normalizer 与 protocol 固定在同一 run？
3. 怎样隔离 offline、simulator、real rollout 和不同 success predicate？
4. 哪些证据只能支持接口，哪些证据才支持结果或个人贡献？

## 知识地图位置与前置依赖

```text
VOL 05 ENG-013 reproducibility + ENG-017 observability + ENG-021 packaging
                                  ↓
dataset/schema → train run → immutable bundle → offline eval
                                  ↓
                         simulator / real rollout
                                  ↓
                       episode trace + metric manifest
```

前置：[ENG-013 Reproducibility](vol_05_engineering_eval_eng013.html)、[ENG-017 Observability](vol_05_engineering_eval_eng017.html)、[ENG-021 Packaging](vol_05_engineering_eval_eng021.html)。

## 1. 30 秒直觉：让每个结果都能回到输入

可信平台至少有五层：

```text
数据快照 → 训练 run → 可加载 bundle → 固定协议评估 → episode/安全 artifact
```

每层都产出 manifest 和 hash。只保存 checkpoint 路径、平均 loss 或成功率截图，无法回答“使用了哪个数据、normalizer、init、scorer 和代码版本”。

## 2. Dataset contract：目录不是版本

每个样本至少绑定：

```text
episode_id / step_id / embodiment / task
camera_set / image_size / calibration_revision
state_schema / action_schema / frame / unit
timestamp / action_age / valid_mask
dataset_revision / source_hash / split
```

RLDS/Open X 的 episode/step 组织是 schema 参照，但不证明本地数据已经无泄漏。对 VLA，`action_dim`、chunk horizon、absolute/velocity frame、gripper convention、camera order 和 padding mask 必须显式记录。

`train/val/raw_holdout/rollout` 不应只靠文件夹名区分。manifest 要记录 episode、scene、object、operator 或 image hash 的分组规则；相邻 window 不能跨 train/holdout。holdout scorer 也要冻结版本。

## 3. Run contract：一次训练到底是什么

可用下式表达 run identity：

\[
run\_id = H(code\_rev, config\_hash, dataset\_manifest, seed, rank/world\_size, hardware, model\_rev, processor\_rev, normalizer\_rev, resume\_source).
\]

变量是代码、配置、数据、随机源、分布式拓扑、硬件、模型和恢复来源；`H` 是身份索引，不是 bitwise identical 的保证。PyTorch reproducibility 文档明确：版本、平台和非确定性算子仍会改变结果。

训练 step 至少拆成：

```text
data_wait → transfer → forward → backward → communication
→ optimizer → checkpoint → logging
```

VLA 还要记录 `valid/action mask count、grad norm、AMP scale/overflow、effective batch、checkpoint save latency`。单卡 smoke 不能推出多 rank parity 或完整吞吐。

## 4. Bundle contract：checkpoint path 不等于模型

| 组件 | 作用 | 缺失风险 |
| --- | --- | --- |
| model weights/config | 参数与结构 | load 错模型 |
| processor/tokenizer | 图像、文本、特殊 token | 输入分布改变 |
| normalizer | action/state scale | action 幅值/轴错误 |
| observation/action schema | camera、frame、unit、H/D、mask | silent reshape |
| code/dependency revision | decode/denorm 逻辑 | lineage 断裂 |
| metadata/integrity hash | step、source、binary identity | 远端路径冒充权重 |

最小 load gate：固定 sample 完成 processor→model→decode→denorm→schema validation roundtrip，并保存 shape、dtype、finite、range 和 parser 结果。缺 normalizer 或 action schema 时，只能做静态审计，不能进入 rollout。

## 5. Evaluation / rollout contract：同名任务不等于同一指标

每次评估冻结：

```text
task / scene-or-init / seed / horizon / control-hz / action-repeat
checkpoint+bundle revision / success predicate / scorer revision
denominator / terminal reason / metric namespace
```

| namespace | 例子 | 能说明什么 |
| --- | --- | --- |
| `train.*` | loss、grad、throughput | 优化与工程观测 |
| `offline.*` | MSE、NLL、raw holdout | 代理或输入/标签指标 |
| `sim.*` | episode success、SPL、collision | 固定 simulator protocol 的闭环结果 |
| `real.*` | safety stop、intervention、success | 有安全日志的真实 rollout |
| `proxy.*` | PSNR/SSIM、视觉 embedding | 离线代理，不等于动作成功 |

每个 rollout episode 保存 `episode_id、task、init、seed、bundle_revision、observation/action trace、action_age、latency、controller status、terminal reason、success predicate inputs、scorer revision`。只有远端 summary JSON 时，应标为 `user-confirmed` 或 `report-supported`。

## 6. 可审计 pipeline 伪代码

```python
def run_vla_pipeline(dataset_manifest, config, bundle, protocol):
    # Freeze identity and split before reading training samples.
    verify_manifest(dataset_manifest, protocol.split_contract)
    run_id = make_run_id(config, dataset_manifest, bundle, protocol)
    for batch in deterministic_loader(dataset_manifest, config.seed):
        # Validate action/frame/unit/mask before the model sees the batch.
        batch = validate_schema_and_masks(batch, bundle.action_schema)
        loss, telemetry = train_step(batch, bundle.model, config)
        record_train_event(run_id, loss, telemetry)
    # Save an immutable bundle before any online rollout.
    save_immutable_bundle(bundle, run_id)
    offline = eval_holdout(bundle, protocol.offline)
    sim = rollout_sim(bundle, protocol.sim) if protocol.sim else None
    real = rollout_real(bundle, protocol.real) if protocol.real else None
    write_metric_manifest(run_id, offline=offline, sim=sim, real=real)
    return run_id
```

关键点是先冻结身份，再校验 batch/schema，训练后保存 immutable bundle，最后把 offline/sim/real 分开记录。伪代码是系统设计合同，不是任何现有项目的完整实现。

## 7. Failure tree 与恢复策略

| 失败层 | 第一证据 | 常见误判 |
| --- | --- | --- |
| data/schema | sample manifest、roundtrip、hash | 归因模型结构 |
| transform/normalizer | processor/normalizer revision、finite/range | 归因 checkpoint |
| train/runtime | telemetry、rank log、DCP marker | 只看最终 loss |
| bundle/load | immutable hash、compatibility smoke | 只比较路径 |
| protocol | eval tuple、scorer/init/seed | 说成模型 uplift |
| controller/safety | action trace、latency、watchdog | 归因 policy loss |

恢复顺序是：保留失败 run 和 marker，定位第一失败层；不要覆盖 latest checkpoint，不要自动把旧 bundle 送入新 protocol，也不要在没有 paired run 时恢复强因果叙事。

## 8. 项目映射与真实性边界

- **OpenPiVLA**：可连接 formal trainer、recipe、action packaging、timeout hook；不能把 archive-only 结果或远端路径写成完整平台。
- **UWM/LIBERO**：可连接 task mapping、fixed/reset protocol、normalizer/action shape、DataLoader stall；186/250 仍缺本地 raw episode bundle，RoboCasa success 未验证。
- **WAM**：可连接 rollout manifest、controller/horizon/camera provenance；checkpoint、target metric、ownership 仍缺。
- **Robot Harness**：可连接 schema、timeout/cancel/compensation；不等于 VLA lineage 或 inference batching。
- **OPD**：可连接 split、raw holdout、strict scorer、point/box/text schema；不等于 robot rollout。

## 9. 结论与下一步

VLA 平台设计的核心不是堆服务，而是用 manifest、immutable bundle、固定 protocol 和逐 episode artifact 把“输入—训练—模型—评估—执行—结果”连成可追溯图。公开来源和本仓库 ENG-013/021 足以冻结机制，但当前五个项目仍缺统一 registry、checkpoint/normalizer hash、raw rollout 与 ownership ledger，因此保持 `WARN`。

下一步：保持 `SYS-VLA-001` 题卡为 `unseen`，进行一次系统设计口述，或补充一个平台 artifact；之后再做 VOL 08 hand-coding 或第二个 system-design slice。

## References

1. [SYS-001 Source Freeze](../sources/vol_08_sys001_vla_training_eval_platform_source_freeze.html)。
2. PyTorch [Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html) 与 [Reproducibility](https://pytorch.org/docs/stable/notes/randomness.html)。
3. [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment/tree/9eeb68b989efbcf474e8fb9019e01d02b962a604)、[LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO/tree/8f1084e3132a39270c3a13ebe37270a43ece2a01)、[OpenPI policy interface](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py)。
4. 本仓库 [ENG-013](vol_05_engineering_eval_eng013.html)、[ENG-017](vol_05_engineering_eval_eng017.html)、[ENG-021](vol_05_engineering_eval_eng021.html) 与五项目 evidence inventory。
