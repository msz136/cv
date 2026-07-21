# VOL 05 Engineering / Evaluation：Model / Processor / Normalizer Packaging 与版本兼容（ENG-021）

> 状态：`drafted / knowledge_23_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-021`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-021 Model / Processor / Normalizer Packaging Source Freeze](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)。  
> 核心边界：官方文档支持加载/保存与 revision 语义；OpenPI 展示 params/assets/transforms/shape 的分离；本地 OpenPiVLA/UWM/OPD 仍缺统一 immutable bundle、processor/normalizer hash binding、formal binary、round-trip 和 backend A/B。

## 问题（Question）

训练完成后，怎样把 VLA 的 model、processor、normalizer、action schema、transform、checkpoint lineage 和 runtime 打成一个可独立加载、可回滚、可验证的 bundle？如果“模型能加载”，为什么仍可能在图像 resize、chat template、action axis/unit、归一化统计或 controller 上失败？

回答时要分开：

1. model config/architecture 与权重 shard；
2. tokenizer、image/video processor、special token 和 preprocessing；
3. action shape、horizon/dim、axis/unit/frame、parser/controller；
4. normalizer stats 与 valid dimensions；
5. ordered transforms、dataset/model revision、runtime/backend；
6. strict load、fixed-batch diff、action round-trip 和 rollback evidence。

## 知识地图位置与前置依赖

```text
ENG-006 checkpoint lineage + ENG-019 config/revision identity
                         ↓
model/config/weights ── processor/tokenizer/image ── action schema
                         ↓
normalizer stats ── ordered transforms ── runtime/backend manifest
                         ↓
strict load → fixed batch → denorm/parser/controller round-trip
                         ↓
immutable release / rollback / compatibility matrix
```

前置：[ENG-006 Checkpoint Lineage](vol_05_engineering_eval.html)、[ENG-018 Retry/Checkpoint](vol_05_engineering_eval_eng018.html)、[ENG-019 Run Identity](vol_05_engineering_eval_eng019.html)。

## 1. 30 秒直觉：交付的是 bundle，不是权重文件

面试中可以先说：一个 VLA release 至少包含 model config/权重、processor、action schema、normalizer、transform revision、lineage 和 runtime manifest；所有文件有 SHA，revision 固定到 commit。加载时严格检查 key/shape/dtype 与 processor/action/normalizer 兼容，加载后做 fixed-batch 输出 diff 和 action/controller round-trip。`safetensors` 只解决 tensor serialization，不自动保存 tokenizer、normalizer 或 controller 语义。

## 2. Immutable bundle schema

| 层 | 最低字段 | 典型检查 |
| --- | --- | --- |
| model | `model_type`、architecture、config JSON、weight shard/index、dtype、key schema | config 与 key/shape/dtype 对齐；无 missing/unexpected key 被静默忽略 |
| processor | tokenizer、image/video processor、chat template、special tokens、resize/pixel range、revision | 相同 modality 输入产生相同 token/image tensor |
| action | `horizon`、`dim`、axis/unit/frame、absolute/delta、padding/mask、parser/controller | `(B,H,D)` 与 denorm、parser、controller round-trip |
| normalizer | method、stats SHA、mean/std 或 q01/q99、valid dims、clip/quantile policy | train/serve 使用同一 stats 和有效维掩码 |
| transforms | ordered input/output transforms、参数、code/schema revision | 顺序与参数 hash 稳定；没有隐式 default |
| lineage | base/parent revision、dataset manifest、run/attempt/checkpoint id、file SHA | 结果可追溯到唯一 artifact |
| runtime | framework/backend/dtype/operator/compiler/controller/protocol | 同步 numerical parity、latency 与 rollback gate |

可将加载定义为：

\[
\text{usable} = \text{schema}\land\text{config}\land\text{weights}\land\text{processor}\land\text{norm}\land\text{transform}\land\text{runtime}\land\text{smoke}
\]

`usable` 不是 Python 函数不抛异常，而是所有 compatibility gate 通过。

## 3. Model config 与权重：严格加载不等于忽略错误

### 3.1 Transformers 语义

冻结的 Transformers `PreTrainedModel` 文档和 `modeling_utils.py` 表明：`save_pretrained` 把 config 与权重写入目录；`from_pretrained` 可从本地目录或 Hub revision 解析 config、safetensors/分片 index、dtype 和 checkpoint。目录、revision、权重 shard 与 config 必须作为同一 bundle 记录。

应显式记录：

- `model_type`、architecture class、library/commit、config JSON SHA；
- weight file/index SHA、dtype、shard count 和 expected key set；
- `revision` 是 commit hash 还是可移动 branch/tag；
- `missing_keys`、`unexpected_keys`、`mismatched_keys` 以及是否允许 adapter-only load。

`ignore_mismatched_sizes=True` 或宽松 partial load 可以帮助迁移实验，但不能作为生产 release gate；否则一个“能加载”的模型可能随机初始化关键层或丢失 action head。

### 3.2 Safetensors 边界

Safetensors header 保存 tensor name、dtype、shape、offset，支持安全读取和 lazy/部分加载；它不保存 model class、tokenizer、processor、normalizer、action axis/unit、controller 或运行时代码。因此正确说法是“权重文件格式可安全读取”，不是“VLA bundle 已兼容”。

## 4. Processor：多模态 preprocessing 也是模型的一部分

Transformers `ProcessorMixin` 将 tokenizer、image processor、audio/video feature extractor 等子处理器作为 attributes 保存和加载。VLA 需把以下字段纳入 processor manifest：

```text
processor_revision / tokenizer files / vocabulary size
chat_template / special_tokens / padding-truncation
image resize/crop/pixel range/channel order
modality names / camera key mapping / frame sampling
```

model revision 为 A、processor revision 为 `main` 时，即使 embedding shape 相同，也可能出现 chat template、special token、resize、pixel normalization 或 camera key 漂移。processor 的 `from_pretrained` 成功只能证明子组件可解析，不能证明 action/controller 语义正确。

## 5. Normalizer 与 transform：统计和顺序必须可追溯

### 5.1 Normalizer

OpenPI frozen code 将 `NormStats` 单独序列化为 asset，并区分 z-score 与 quantile 归一化。VLA manifest 至少记录：

```text
stats_sha / data_revision / method / mean / std / q01 / q99
valid_dims / clip_policy / action_schema / producer_code_revision
```

以 z-score 为例：

\[
z_d = \frac{x_d-\mu_d}{\max(\sigma_d,\epsilon)},\qquad
\hat{x}_d=z_d\cdot\sigma_d+\mu_d
\]

`d` 只对 valid action dimension 生效；padding、未观测维、gripper 或 delta/absolute 切换不能隐式共享统计。`normalizer.json` 的存在不证明它绑定到某个 checkpoint。

### 5.2 Ordered transforms

OpenPI 的 data loader 把 repack、data、Normalize、model transforms 组合成有序 pipeline，policy 再组合 input/output transforms。训练和 serving 必须保存相同的 transform sequence、参数和 code/schema revision；调整 resize→normalize→tokenize 的顺序就可能改变输入分布，即使每个函数单独都“正确”。

## 6. Action schema：shape 相同也可能语义不同

需要同时冻结：

```text
B: batch      H: action horizon/chunk length      D: action dimension
axis order / unit / coordinate frame / absolute-vs-delta
padding mask / gripper convention / parser grammar
controller rate / queue / replan / denormalization
```

`(B,15,72)` 与 `(B,16,72)`、`(B,50,32)` 都是合法 tensor shape，但不代表同一 action contract。OpenPI `Pi0Config` 的 `action_dim=32`、`action_horizon=50` 是该 frozen config 的默认值，不能外推为所有 VLA 的标准。

最小 round-trip 是：

```text
raw action → normalize → model input/target → model output
          → denormalize → serialize/parse → controller frame
```

每一段都要记录 axis、unit、frame、clip 和 tolerance；仅比较 tensor shape 不够。

## 7. Revision 与 lineage：branch 不是 immutable identity

Hub `snapshot_download` 的 `revision` 可以是 branch、tag 或 commit；branch/tag 会移动，稳定 bundle 应保存 resolved commit hash、每个文件 SHA 和 allow/ignore pattern。lineage 最小字段为：

```text
bundle_id / parent_model_revision / model_config_sha / weight_shards_sha
processor_revision / norm_stats_sha / transform_code_sha
dataset_manifest_sha / run_id / attempt_id / checkpoint_id
runtime_manifest_sha / eval_protocol_sha / release_pointer
```

`checkpoint-5000`、`main`、远端 path 或实验名都不能单独充当 lineage。

## 8. OpenPI 对照：params、assets、shape、transforms 分离

OpenPI frozen source 提供清晰的 engineering reference：

1. `BaseModelConfig` 显式提供 `action_dim`、`action_horizon`、`max_token_len` 和 `inputs_spec`；
2. checkpoint manager 分开保存 `assets`、`train_state`、`params`；
3. norm stats 作为 asset 单独保存/加载；
4. data loader 组合 Normalize 与其他 transforms；
5. policy 在推理前后应用 input/output transforms。

这不是“本仓库项目已采用 OpenPI checkpoint contract”的证明，而是说明为什么 model weights、optimizer/train state、normalizer、shape 和 transform 应作为不同 gate 管理。

## 9. 本地项目证据与真实性边界

| 项目 | local-direct 可说 | 不能升级为 |
| --- | --- | --- |
| OpenPiVLA | `formal_train.py` 有 processor/collator/chat-template、LoRA/causal-CE；`data.py`/`recipes.py` 有 action formatter、三类 recipe；DEPLOYMENT 记录远端 official checkpoint/path | formal Qwen checkpoint 本地可加载、processor/norm hash binding、DROID `H=15,D=72` 与 formal `limit=16` 已统一、round-trip 或 formal rollout 已验证 |
| UWM | artifact gate 有 action normalizer JSON、checkpoint load report、effective config；normalizer SHA 可复核 | normalizer 与 checkpoint/processor/controller immutable binding；snapshot 没有 binary |
| OPD | ZeRO-2/3 config 和 final-only/no-optimizer-state manifest | 完整 model/processor/normalizer bundle、可恢复 optimizer lineage 或 load smoke |
| WAM | 当前 inventory 没有 local runtime/config/log/checkpoint bundle | 任何 packaging/compatibility claim，保持 `UNVERIFIED` |

当前 strongest statement：项目源码和 metadata 暴露了 loader/formatter/path；但 release gate 需要实际 bundle、hash、strict load、fixed-batch diff 与 action round-trip。

## 10. 验证伪代码（工程合同）

```python
def verify_vla_bundle(manifest, runtime):
    # 1. Resolve immutable revisions and verify every file before import.
    verify_manifest_files(manifest.files, manifest.sha256)
    assert manifest.model_revision and manifest.processor_revision

    # 2. Strict model/processor load; do not hide key or shape mismatches.
    config = load_config(manifest.model_config, revision=manifest.model_revision)
    model, report = load_model(manifest.weights, config=config, strict=True)
    processor = load_processor(manifest.processor, revision=manifest.processor_revision)
    assert not report.missing_keys and not report.unexpected_keys

    # 3. Bind normalizer/action schema/transforms to the same bundle.
    stats = load_norm_stats(manifest.normalizer.path)
    assert sha256(stats) == manifest.normalizer.sha256
    assert schema_compatible(model, processor, stats, manifest.action_schema)

    # 4. Fixed-batch equality plus denorm/parser/controller round-trip.
    before = forward(model, processor, manifest.fixed_batch)
    after = reload_and_forward(manifest, manifest.fixed_batch, runtime)
    assert close_enough(before, after, manifest.tolerance)
    assert action_round_trip(after, stats, manifest.action_schema, manifest.controller)

    # 5. Runtime/backend is part of the release verdict; no silent fallback.
    assert runtime_compatible(manifest.runtime, runtime)
    return "verified"
```

伪代码是验收合同，不是 OpenPiVLA、UWM 或 OPD 已有实现。

## 11. Compatibility matrix

| Case | 检查 | 通过条件 |
| --- | --- | --- |
| missing processor | 删除 tokenizer/image config | manifest/loader fail closed，不从环境默认值补齐 |
| revision drift | model commit A + processor `main` | 拒绝或显式兼容矩阵；不能静默混用 |
| key/shape mismatch | action head/config/shard 不一致 | strict load fail；不以 `ignore_mismatched_sizes` 过 gate |
| normalizer drift | train 与 serving stats SHA/method/valid dims 不同 | gate fail，fixed action round-trip 不通过 |
| transform reorder | resize/normalize/tokenize/denorm 顺序变化 | transform revision/property test fail |
| shard omission | 缺 safetensors shard/index | file manifest/load smoke fail，禁止 partial release |
| dtype/backend | BF16/FP16/CUDA/MACA/ROCm 改变 | finite/numerical parity、operator matrix、同步 latency gate |
| controller semantics | radians/degrees、absolute/delta、world/robot frame 混用 | parser/controller round-trip fail |
| remote path only | report 有 path，snapshot 无 binary | 只标 `report-supported/remote-referenced` |
| rollback | 新 processor/norm 与旧 checkpoint 不兼容 | immutable previous-good pointer 可恢复 |

## 12. Trade-off、bad case 与追问

### 12.1 Trade-off

- 把所有组件打进单 bundle，回滚和复现更稳，但更新 tokenizer/processor 的成本更高；用 manifest 版本化和兼容矩阵缓解。
- strict load 会拒绝部分迁移实验；生产发布应 strict，研究迁移另存 `partial-load` evidence，不能共用 verdict。
- safetensors 降低任意代码执行和部分加载风险，但仍需外部 config/processor/action manifest。
- 保存每步 transform/config/hash 增加存储和审核成本，却能定位“模型变了还是 preprocessing 变了”。

### 12.2 高概率 bad case

1. 只上传 `model.safetensors`，遗漏 config/tokenizer/image processor。
2. processor 跟随 Hub `main`，checkpoint 固定在旧 commit。
3. normalizer JSON 从另一个 dataset/run 复制，未记录 stats SHA。
4. `ignore_mismatched_sizes=True` 掩盖 action head shape mismatch。
5. `H/D` shape 对了，但 frame、unit、absolute/delta 或 gripper convention 错。
6. 训练和 serving 的 transform 顺序、pixel range 或 camera key 不同。
7. 把 OpenPI 默认 `32×50` 当成所有 VLA 的通用 action contract。
8. report 中远端 checkpoint path 被写成“本地验证过的模型”。

### 12.3 面试追问

1. model config、processor config 和 normalizer stats 为什么要分开 hash？
2. `from_pretrained` 能加载但 action 仍然错，最先查哪三层？
3. safetensors 解决了什么，没解决什么？
4. branch/tag/revision/commit hash 在发布时如何取舍？
5. 如何证明 train/serve normalization 与 transform sequence 一致？
6. `(B,15,72)` 与 `(B,16,72)` 怎样定位是 horizon、padding 还是 semantics conflict？
7. strict load 与研究迁移的 partial load 如何分开记录？
8. OpenPiVLA 当前哪些证据是 path/report，哪些才算 bundle-verified？

## 13. 结论与下一步

可靠的 VLA 发布合同把 model config/weights、processor、action schema、normalizer、ordered transforms、lineage 和 runtime manifest 绑定为 immutable bundle；revision 固定到 commit；加载严格检查 key/shape/dtype；safetensors 只作为 tensor 层；最后用 fixed-batch、action/controller round-trip、backend parity 和 rollback smoke 关闭兼容性。

OpenPiVLA 当前有 processor/collator、recipe、远端 checkpoint/path；UWM 有 normalizer/load metadata；OPD 有 final-only/no-optimizer-state manifest。它们不能证明统一 bundle、formal binary、processor/norm hash binding 或 round-trip 已闭合。因此本节点保持 `WARN`，题卡保持 `unseen`；下一步可口述 `VLA-ENG-021` 或补 bundle/hash/round-trip artifact，`VLA-ENG-022` 继续后置。

## References

1. [ENG-021 Source Freeze](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)：官方 revision/SHA、本地 evidence 与 compatibility gate。
2. Hugging Face Transformers [`modeling_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/modeling_utils.py)、[`processing_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/processing_utils.py) 与 [`configuration_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/configuration_utils.py)。
3. Hugging Face Hub [`snapshot_download@b2ae5b6`](https://github.com/huggingface/huggingface_hub/blob/b2ae5b6a898d5303e55c256aa714f9f9a1f4bd70/src/huggingface_hub/_snapshot_download.py) 与 [`safetensors@6eb4dc9`](https://github.com/huggingface/safetensors/blob/6eb4dc9a28ebce297606e0f4836bbf28839cacef/README.md)。
4. Physical Intelligence [`openpi@15a9616`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：model/checkpoint/config/normalize/transforms/data loader/policy frozen files。
5. 本仓库 [ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)、[OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

