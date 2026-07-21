# VOL 08 SYS-001 Source Freeze：可复现的 VLA 训练—评估平台

> 状态：`source_frozen / SYS-VLA-001 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片只冻结数据、训练、checkpoint、评估与 rollout 的系统合同；不把公开框架或个人项目脚本写成已完成的平台。

## 问题（Question）

如何设计一个能复现、能诊断、能安全回滚的 VLA 训练—评估平台，使数据版本、模型/processor/normalizer、checkpoint、评估协议和 rollout artifact 不互相污染？

最小链路：

```text
dataset snapshot + schema
  → deterministic transform / split manifest
  → training run + config + code revision
  → immutable checkpoint bundle
  → offline eval (fixed protocol)
  → online rollout (separate environment)
  → episode/metric manifest + lineage graph
```

## 1. 冻结来源与支持边界

| 来源 | 类型 / revision | 可支持的机制 | 不能支持的 claim |
| --- | --- | --- | --- |
| [PyTorch Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html) | official docs；2.13；2026-07-18 | 多 rank checkpoint、state-dict 组织、保存/加载与 resharding 语义 | 用户项目已经完成可恢复 mid-epoch 或跨硬件 parity |
| [PyTorch reproducibility notes](https://pytorch.org/docs/stable/notes/randomness.html) | official docs；2026-07-18 | RNG、determinism、版本/平台差异与复现限制 | 固定 seed 就能保证完整机器人 rollout 相同 |
| [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment/tree/9eeb68b989efbcf474e8fb9019e01d02b962a604) | official repo；pinned commit | RLDS episode/step 组织、跨 embodiment 数据字段参照 | 所有本地数据已符合同一 schema 或无 leakage |
| [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO/tree/8f1084e3132a39270c3a13ebe37270a43ece2a01) | official repo；pinned commit | task/init/reset、benchmark protocol、success/eval 入口 | 项目远端结果已复算或与论文协议对齐 |
| [OpenPI policy interface](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py) | official-code；pinned commit | observation→action transform、policy metadata 与 inference 边界 | 项目已有生产级 serving、SLO 或安全 fallback |
| 本仓库 [VOL 05 ENG-013 Reproducibility](../sources/vol_05_eng013_reproducibility_source_freeze.html) | local source audit | seed、sampler、resume、rank/order 与 replay 缺口 | 单卡 smoke 已证明多 rank/mid-epoch 复现 |
| 本仓库 [VOL 05 ENG-021 Packaging](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html) | local source audit | model/processor/normalizer/action schema 的 bundle 合同 | 远端 checkpoint lineage 或 ownership 已闭合 |
| 本仓库 [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | local evidence | fixed-init/reset、normalizer、task mapping、user-confirmed result 的边界 | 0.744 已是本地 raw benchmark 或 RoboCasa 已完成 |
| 本仓库 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | local evidence | smoke/formal/report/archive 的证据分层与 action packaging | 远端 97.4 或 checkpoint 已具备 immutable lineage |

## 2. 关键合同（Contract）

### 2.1 Dataset contract

每个样本至少绑定：`dataset_revision、episode_id、step_id、embodiment、camera_set、state/action schema、unit/frame、timestamp、split、source_hash、valid_mask`。训练集、验证集、raw holdout 和 rollout environment 必须有不可变 manifest；不能只记录目录路径。

### 2.2 Run contract

`run_id` 必须指向：代码 revision、config hash、dataset manifest、seed/rank/world-size、hardware/runtime、model/processor/normalizer revision、optimizer/scheduler、resume source 和 artifact root。日志中把 `data_wait、forward/backward、communication、checkpoint、eval` 分开，避免把单次 loss 或单卡速度当系统结论。

### 2.3 Bundle contract

可部署 bundle 至少包含：model weights、model config、processor/tokenizer、normalizer、action schema、observation schema、code revision、dependency lock、checkpoint metadata、integrity hash 和 compatibility test。缺任一项时只能做诊断或离线解析，不应进入 robot rollout。

### 2.4 Evaluation / rollout separation

offline proxy、simulator success、real rollout 和 human/visual proxy 使用不同 metric namespace。评估 manifest 固定 `task、scene/init、seed、horizon、control-hz、action-repeat、success predicate、denominator、scorer revision`；rollout 另存逐 episode action/observation trace、terminal reason、latency、safety event。训练脚本不应静默修改评估分布。

## 3. 证据阶梯

```text
schema / manifest
  → deterministic data transform
  → checkpoint load + processor/normalizer roundtrip
  → offline metric on frozen holdout
  → simulator closed-loop with denominator
  → real rollout with safety log
```

每一层只能支持该层及其上游接口，不可从 `loss` 跳到 `success`，从 checkpoint path 跳到 binary identity，或从 simulator summary 跳到 real-robot claim。

## 4. 当前项目边界

| 项目 | 可复用的系统设计证据 | 当前不能声称 |
| --- | --- | --- |
| OpenPiVLA | formal trainer、recipe、action packaging、timeout hook、report/evidence ladder | 97.4 的本地 raw denominator、formal checkpoint lineage、生产 serving SLO |
| UWM/LIBERO | task mapping、fixed/reset protocol、normalizer/action shape、DataLoader stall smoke | 186/250 的本地 episode bundle、Table II 严格复现、RoboCasa benchmark |
| WAM | rollout manifest、controller/camera/horizon provenance、paired diagnostic | checkpoint binary、target metric、closed-loop uplift |
| Robot Harness | tool schema、timeout/cancel/compensation、scope/lock cleanup | VLA training lineage、policy-server batching、端到端机器人成功 |
| OPD | split/raw holdout、strict scorer、point/box/text schema | robot rollout、3D/navigation 或单因果 uplift |

## 5. Source gate 结论

公开来源足以冻结：数据/运行/模型 bundle 的字段，PyTorch DCP 与 reproducibility 的限制，RLDS/LIBERO 的 episode/protocol 参照，以及 policy interface 与 rollout 的证据边界。当前仓库仍缺一个全项目统一的 immutable artifact registry、checkpoint binary/normalizer hash、逐 episode rollout bundle 和 ownership ledger，因此本节点保持 `WARN`。

下一步：保持已同步的 `SYS-VLA-001` 题卡为 `unseen`，进行一次系统设计口述，或补充一个平台 artifact；不把现有项目局部脚本升级成已完成的平台。

## References

1. PyTorch [Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html) 与 [Reproducibility](https://pytorch.org/docs/stable/notes/randomness.html)。
2. Google DeepMind [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment/tree/9eeb68b989efbcf474e8fb9019e01d02b962a604)。
3. LIBERO [official repository](https://github.com/Lifelong-Robot-Learning/LIBERO/tree/8f1084e3132a39270c3a13ebe37270a43ece2a01)。
4. Physical Intelligence [openpi policy interface](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py)。
5. 本仓库 ENG-013、ENG-021、UWM/LIBERO 与 OpenPiVLA evidence inventory。
