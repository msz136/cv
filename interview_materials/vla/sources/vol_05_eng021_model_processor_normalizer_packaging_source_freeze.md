# VOL 05 ENG-021 Source Freeze：Model / Processor / Normalizer Packaging 与版本兼容

> 状态：`source_frozen / VLA-ENG-021 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-17  
> 证据截止：2026-07-17  
> 本切片冻结 VLA 模型、processor、normalizer、transform、checkpoint 与 runtime compatibility 的官方来源和本地证据边界；下游已生成一个知识节点和一张 `unseen` 题卡，未生成口述成绩。  
> 前置：[ENG-018 Scheduler / Preemption / Retry](../knowledge/vol_05_engineering_eval_eng018.html)、[ENG-019 Config Resolution / Run Identity](../knowledge/vol_05_engineering_eval_eng019.html)、[ENG-020 Secret / Permission / Logging](../knowledge/vol_05_engineering_eval_eng020.html) 与 [ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)。

## 问题（Question）

训练得到的 VLA 不能只交付一个权重文件。面试官会追问：模型 architecture/config、权重 shard、tokenizer/image processor、action schema、normalizer、data transforms、checkpoint lineage、runtime/backend 与 controller 如何作为一个可加载、可验证、可回滚的 bundle 发布？当训练、评估和部署使用不同版本时，怎样在加载前拒绝 shape、dtype、axis、unit、normalization 或 processor mismatch？

本切片的核心合同：

```text
model config + weight shards + processor/tokenizer/image config
        + action schema + normalizer + transform revision
        + checkpoint lineage + runtime/backend manifest
        + load smoke + fixed-batch / action round-trip evidence
```

“有 checkpoint path”“能实例化 model”“config 文件存在”都不能单独证明 bundle 可复现或可部署。

## 1. 冻结指纹与许可

所有 SHA 对 2026-07-17 取得的 pinned UTF-8 原文计算；这里只记录来源指纹和可支持的机制，不复制任何凭据值。

| 来源 | pinned URL | 原文 SHA-256 | 可支持的边界 |
| --- | --- | --- | --- |
| Transformers model docs | [model.md@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/model.md) | `e8c0b2fe13997464b39ad89b24138cdff4979cdf074d04d70b48131eae85e3bf` | `PreTrainedModel` 是模型保存/加载基类；local path 与 Hub model 均属于加载入口 |
| Transformers processor docs | [processors.md@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/processors.md) | `cd830dd43eb219ba6a07cb816ab61c6872711ab8c0301c9f406a16ef0aba5014` | 多模态 processor 组合 tokenizer/image/audio 子处理器并提供保存/加载 |
| Transformers configuration docs | [configuration.md@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/configuration.md) | `902911a9c7684ffe45f9a804bc44b77136fc908c23d113d377479f118d71f63e` | `PreTrainedConfig` 的保存/加载和 model-specific attributes |
| Transformers modeling utils | [modeling_utils.py@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/modeling_utils.py) | `d8bf1879d6f582888b6cf47b4d63070260285a3bd1dc94ce7e1373304f74168a` | `save_pretrained` 保存 config/权重；`from_pretrained` 解析 revision、sharded weights、dtype/shape 与 safetensors 路径 |
| Transformers processing utils | [processing_utils.py@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/processing_utils.py) | `d49b92aba8a755e6d93928a5fec94950004a5bc53a48746f9b83dd04cb7edacd` | `ProcessorMixin` 的 attributes、`save_pretrained`、`from_pretrained(revision=...)` 与子处理器配置 |
| Transformers configuration utils | [configuration_utils.py@150eb7c](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/configuration_utils.py) | `c00dcc84295a7867156aae2e0952c4e7d2ae1cafef1a1d965fb4d3f741ae2bf0` | config JSON、model type、版本化配置字段的加载边界 |
| Hugging Face Hub snapshot | [_snapshot_download.py@b2ae5b6](https://github.com/huggingface/huggingface_hub/blob/b2ae5b6a898d5303e55c256aa714f9f9a1f4bd70/src/huggingface_hub/_snapshot_download.py) | `8dd5f2108fded3418b79322ceabefcdcc6cee7e01d4b69c2a30d9aaa5833cb54` | `revision` 可为 branch/tag/commit；snapshot 以 commit hash 建缓存并可 allow/ignore pattern |
| Hugging Face Hub file download | [file_download.py@b2ae5b6](https://github.com/huggingface/huggingface_hub/blob/b2ae5b6a898d5303e55c256aa714f9f9a1f4bd70/src/huggingface_hub/file_download.py) | `8d2c2be997bd093d2149c020119851c772c5dc146065264ba29b58c28b50c62b` | 文件 revision/etag/cache 与 local-only 读取边界 |
| Safetensors README | [README.md@6eb4dc9](https://github.com/huggingface/safetensors/blob/6eb4dc9a28ebce297606e0f4836bbf28839cacef/README.md) | `0a932f120de5c2477b286cae5517b6fec5e1d3ed64a19b99ccfc0a8504db7b13` | tensor-only header、shape/dtype/offset metadata、safe/lazy/zero-copy trade-off；不保存 arbitrary code |
| OpenPI README | [README.md@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/README.md) | `567fc57766bd736664f50126cab8145af4071ca16cc5e238f2b11e369169c3b5` | OpenPI checkpoint/config、模型和 policy 使用入口；不等于本地项目结果 |
| OpenPI model base | [model.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/model.py) | `0d74bc1d8f4623ac3d8e543710b8bf75f9b95e588a3ebf6127c659e001385cff` | `BaseModelConfig` 的 `action_dim/action_horizon/max_token_len`、shape spec 与 params restore |
| OpenPI checkpoint | [checkpoints.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/checkpoints.py) | `3cc32682ec3609e9075dabd991488edb9d7f6c045443f58963d733f99c468dbd` | Orbax checkpoint 分离 `assets/train_state/params`；save/restore 与 norm-stats asset 边界 |
| OpenPI Pi0 config | [pi0_config.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_config.py) | `d321858c30b398126035ea2b6da09e1c422eeeebb5ebf8df631daf9dc77647fa` | `action_dim=32`、`action_horizon=50`、input/output shape spec 与 model config |
| OpenPI normalize | [normalize.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/shared/normalize.py) | `6c2cea4946fb07e51801530400d2b2fd94730e195cd290d6b6960114eca9739d` | `NormStats` JSON serialization/save/load；stats 不是可由 checkpoint name 推断的常量 |
| OpenPI transforms | [transforms.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py) | `a1b94e9e72849a18834778f229c6bb389a495eb7fbe0aa800edea728b9424ff4` | transform composition、Normalize/Unnormalize、FAST、padding、action dimension 语义 |
| OpenPI data loader | [data_loader.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/data_loader.py) | `4d0b055ac28527c1ab1f0ba7496057722c7c748c88564a8de2ff4fac650e97c9` | 数据 transform 顺序、norm stats lookup、skip-normalization boundary |
| OpenPI policy | [policy.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py) | `a2ac5236e23b11d0f5a840d4a8fef148d89dba921d5452ec5dfcd5a6ffa46f20` | inference 前后 input/output transforms 和 action output boundary |

这些来源说明“如何打包/加载”以及“哪些字段会影响 shape/semantics”；不证明任何本地项目已经通过完整 load smoke、round-trip 或发布门禁。

## 2. Packaging contract：模型不是单一权重文件

建议把一个 VLA release 定义为 immutable bundle：

| 层 | 最低字段 | 失败时的风险 |
| --- | --- | --- |
| model | architecture/model type、config JSON、weight shard/index、dtype、parameter key schema | 能读文件但实例化为错误 architecture；missing/unexpected key 被忽略 |
| processor | tokenizer、chat template、image/video processor、special tokens、resize/normalization config、processor revision | 文本/图像 token 对齐改变，推理输入与训练分布不一致 |
| action | action horizon/dim、axis/unit/frame、chunk/replan、padding/mask、parser/serializer schema | 输出 shape 看似正确但 controller 语义错误 |
| normalizer | method、stats revision、mean/std 或 q01/q99、valid dims、clip/quantile policy | 同一 checkpoint 在不同 stats 下输出完全不同；越界维被错误归一化 |
| transforms | ordered input/output transforms、code revision、parameters、data schema | transform 顺序改变，offline loss 与 online action 不可比 |
| lineage | parent/base model revision、dataset/manifest revision、run/attempt/checkpoint id、file SHA | 无法回答“哪个权重、哪个数据、哪个 processor 产生该结果” |
| runtime | framework/library/backend/dtype、CUDA/MACA/ROCm、controller/protocol、hardware | 能加载但数值、延迟、算子或 action interface 不兼容 |

模型加载合同可抽象为：

\[
\text{loadable}=\text{schema}\land\text{config}\land\text{weights}\land\text{processor}\land\text{normalizer}\land\text{transform}\land\text{runtime}\land\text{smoke}
\]

其中 `loadable` 不是“函数没有抛异常”，而是 fixed batch 输出、action round-trip 和兼容性 gate 均通过。

## 3. 官方机制：revision、config、processor 与权重必须绑定

### 3.1 Transformers 目录语义

`PreTrainedModel.save_pretrained` 会在目录中保存 config 与权重；`from_pretrained` 可从本地目录或 Hub revision 解析权重文件，并处理 safetensors、分片 index、dtype 与部分 size mismatch 选项。面试时要说明：`ignore_mismatched_sizes=True` 会放宽加载检查，不能被当作兼容性证明。

`ProcessorMixin` 把 tokenizer、image processor 等子处理器作为 attributes 保存；`from_pretrained(..., revision=...)` 读取同一 revision 的 processor config。processor 与 model revision 不一致时，即使 tensor shape 相同，也可能造成 special-token、resize、chat-template 或 pixel normalization 漂移。

### 3.2 Hub snapshot 不是任意远端路径

Hub 的 `snapshot_download` 支持 branch/tag/commit，但稳定 artifact 应把 commit hash 写入 manifest；branch 名称只是可移动引用。下载缓存、allow/ignore pattern、local-only 与 incomplete snapshot 都要写进 evidence。只记录 `repo_id` 或当前 `main` 不能复现“当时的模型”。

### 3.3 Safetensors 只解决一部分问题

Safetensors header 记录 tensor name、dtype、shape、offset，支持安全读取、lazy loading 和部分 tensor 访问；它不保存 tokenizer、processor、normalizer、controller 或 arbitrary Python code。使用 `.safetensors` 不等于 architecture、config、shape、revision 和 action contract 已绑定。

## 4. OpenPI 机制：params、assets、transforms 和 shape 是分离对象

OpenPI frozen source 提供了一个特别适合 VLA 面试的对照：

1. `BaseModelConfig` 显式给出 `action_dim`、`action_horizon`、`max_token_len` 与 `inputs_spec`；`Pi0Config` 默认 `action_dim=32`、`action_horizon=50`，这是某个 config 的字段，不是所有 VLA 的通用事实。
2. `checkpoints.py` 保存 `assets`、`train_state`、`params` 三类对象；assets 回调保存 norm stats，params 与训练状态不是同一语义。
3. `normalize.py` 将 `NormStats` 序列化到独立目录；stats 需要和数据 revision、valid dimensions、quantile/z-score policy 一起绑定。
4. `data_loader.py` 把 repack/data/model transforms 和 Normalize 按序组合；`skip_norm_stats` 是显式边界，不应悄悄 fallback。
5. `policy.py` 在推理前后应用 input/output transform；因此训练期和 serving 期 transform sequence 必须可比较。

OpenPI 的分离结构不能直接外推到项目实现，但它证明“权重、训练状态、资产、shape 与 transform 是不同的验收对象”。

## 5. 本地 direct evidence：OpenPiVLA、UWM、OPD

### 5.1 OpenPiVLA

| 文件 | SHA-256 | 直接可见 | 不能由此证明 |
| --- | --- | --- | --- |
| `formal_train.py` | `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94` | `Qwen3VLCollator` 持有 processor，调用 chat template；formal trainer/LoRA/causal-CE 路径可读 | local checkpoint、processor revision、normalizer/controller round-trip |
| `data.py` | `32C6AA76929D941C4832D2EB4C2550527D3E607E31C2A9F5507CC76EEEDBC2EC` | DROID/MindCube 数据和 action formatter 的代码入口 | DROID `H=15,D=72` 的 axis/unit 与 formal `limit=16` 已被同一 bundle 证明 |
| `recipes.py` | `397D1B384A2BD93D9DC81B7003E6AB7BFAC3FC458EA04008197C3F503F9D780E` | 三类 recipe、model/data 参数入口 | 三条 formal run 的 immutable checkpoint lineage |
| `DEPLOYMENT.md` | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14` | 远端 official checkpoint/config/path 和 rollout 命令记录 | 本地 bundle、权重 SHA、processor/norm stats 与 formal Qwen load smoke |

已有项目 evidence 明确：formal report 与 launch script 指向远端路径；本地 snapshot 没有三条 formal checkpoint binary。不能把 path、report 或 `save_checkpoint=true` 写成 checkpoint-verified。

### 5.2 UWM / OPD

- UWM local artifact gate 有 action normalizer JSON、checkpoint load report 和 effective config；扫描根目录未发现 `.pt/.pth/.ckpt/.safetensors/.bin` binary。normalizer SHA 只能证明该 JSON 文件，不证明它与权重/processor/controller 绑定。
- OPD manifest 记录 `final_model_only_no_intermediate_checkpoints`、`final_weights_no_optimizer_state` 和 ZeRO config；这是 lineage 缺口的 direct evidence，不是完整 package 或 resume 证明。
- WAM inventory 没有 local runtime/config/log/checkpoint bundle；ENG-021 对 WAM 保持 `UNVERIFIED`。

## 6. Compatibility matrix：从文件可读到闭环可用

| 层级 | gate | 最小检查 | 失败含义 |
| --- | --- | --- | --- |
| C0 artifact | file/schema | manifest、文件 SHA、required files、no unexpected executable payload | bundle 不完整或引用漂移 |
| C1 model | config/weights | model type、key set、shape、dtype、shard index、missing/unexpected keys | 权重和 architecture 不匹配 |
| C2 processor | tokenizer/image/video | processor revision、special tokens、chat template、resize、pixel range、modality names | 输入分布/序列语义漂移 |
| C3 action | shape/semantics | `(B,H,D)`、axis/unit/frame、mask/padding、decode/denorm/controller round-trip | action 可运行但物理意义错误 |
| C4 normalizer | stats | stats SHA、method、valid dims、clip/quantile、train/serve equality | 输出尺度和边界错误 |
| C5 runtime | backend | framework/backend/dtype/operator/compile/runtime manifest | 数值、性能或算子不等价 |
| C6 closed loop | protocol | fixed observation、inference、controller、episode predicate、latency budget | offline load 成功但 robot/eval 失败 |

每个 compatibility verdict 都要绑定 `bundle_id`，而不是写在项目标题或 checkpoint step 上。

## 7. 验证伪代码（工程合同）

```python
def load_vla_bundle(manifest, runtime):
    # 1. Resolve immutable revisions and verify every file hash before import.
    verify_manifest_files(manifest.files, manifest.sha256)
    assert manifest.model_revision and manifest.processor_revision

    # 2. Load config/model/processor without silently ignoring mismatches.
    config = load_config(manifest.model_config, revision=manifest.model_revision)
    model = load_model(manifest.weights, config=config, strict=True)
    processor = load_processor(manifest.processor, revision=manifest.processor_revision)

    # 3. Bind action schema and normalizer to the same bundle and data revision.
    stats = load_norm_stats(manifest.normalizer.path)
    assert sha256(stats) == manifest.normalizer.sha256
    assert schema_compatible(model, processor, manifest.action_schema, stats)

    # 4. Run deterministic fixed-batch and action round-trip tests.
    before = model_forward(model, processor, manifest.fixed_batch)
    after = reload_and_forward(manifest, manifest.fixed_batch, runtime)
    assert close_enough(before, after, manifest.tolerance)
    assert action_round_trip(after, manifest.action_schema, stats, manifest.controller)

    # 5. Record backend/runtime and refuse unverified fallback artifacts.
    assert runtime_compatible(manifest.runtime, runtime)
    return Bundle(model, processor, stats, manifest)
```

伪代码强调 strict load、revision/hash、normalizer/action contract 和 round-trip；它不是任何本地项目已有实现。

## 8. 验证矩阵与 bad cases

| Case | 注入 | 通过条件 |
| --- | --- | --- |
| missing processor | 删除 tokenizer/image config | load gate fail closed，不能从环境默认值静默补齐 |
| revision drift | model 用 commit A，processor 用 main | manifest/loader 拒绝，或显式记录兼容矩阵 |
| shape mismatch | `action_dim/horizon` 与权重或 controller 不同 | strict schema gate 拒绝；不使用 `ignore_mismatched_sizes` 掩盖 |
| normalizer drift | train stats 与 serving stats 不同 | stats SHA/method/valid dims mismatch，fixed action round-trip fail |
| transform order | 调换 resize/normalize/tokenize/denorm 顺序 | transform revision/property test fail |
| shard omission | 缺一个 safetensors shard/index | file manifest 或 load smoke fail，禁止 partial load 变成 release |
| dtype/backend | BF16/FP16/MACA/CUDA 变更 | finite/numerical parity + operator matrix + synchronized latency gate |
| controller semantics | radians/degrees、absolute/delta、world/robot frame 混用 | action round-trip 和 controller contract fail |
| remote path only | report 有 path，snapshot 无 binary | 只能标 `report-supported/remote-referenced`，不能标 `checkpoint-verified` |
| rollback | 新 processor/normalizer 与旧 checkpoint 发布 | immutable bundle + previous known-good pointer 可恢复 |

## 9. 不能使用的面试口径

1. “有 `config.json` 就能复现”——还缺权重、processor、normalizer、transform、runtime 和数据 lineage。
2. “用了 safetensors 就安全且兼容”——它只描述 tensor 文件，不保存 action/controller 语义。
3. “`from_pretrained` 能加载就说明部署可用”——必须补 shape、normalizer、round-trip、backend 和 closed-loop smoke。
4. “normalizer JSON 和 checkpoint step 同名，所以一定匹配”——要有 stats SHA、data revision 和 manifest binding。
5. “Hub `main` 是同一模型”——branch 可移动，应冻结 commit hash。
6. “`ignore_mismatched_sizes=True` 解决了版本兼容”——它可能掩盖错误 key/shape，不能作为 release gate。
7. “OpenPI 的 `action_dim=32` / `horizon=50` 是 VLA 通用规格”——只是 frozen `Pi0Config` 默认值。
8. “本地 report 有远端 checkpoint path，所以我验证过 load”——当前项目证据明确缺 binary/immutable hash/load smoke。

## 10. Source Gate 结论

官方来源支持以下工程合同：把 model config/weights、processor 子组件、action schema、normalizer stats、ordered transforms、checkpoint lineage 和 runtime manifest 绑定为 immutable bundle；revision 优先使用 commit hash；safetensors 只作为 tensor serialization 层；加载前做 strict schema/shape/dtype checks，加载后做 fixed-batch 与 action/controller round-trip。

本地证据只能证明：OpenPiVLA formal trainer 有 processor/collator、recipe 和远端 checkpoint/path 入口；UWM 有 normalizer/load metadata；OPD 有 final-only/no-optimizer-state manifest；OpenPI 官方代码把 params、assets、norm stats、transforms 和 shape 明确分开。当前缺统一 bundle manifest、model/processor/normalizer SHA binding、formal checkpoint binary、processor revision、parser/controller round-trip 与跨 backend compatibility A/B。Verdict 保持 `WARN`；知识页 `knowledge_23_of_44` 与一张 `unseen` 题卡已生成，ENG-022 继续后置。

## References

1. Hugging Face Transformers [`model.md@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/model.md)、[`processors.md@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/processors.md)、[`configuration.md@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/docs/source/en/main_classes/configuration.md)。
2. Hugging Face Transformers [`modeling_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/modeling_utils.py)、[`processing_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/processing_utils.py) 与 [`configuration_utils.py@150eb7c`](https://github.com/huggingface/transformers/blob/150eb7c9ed4091294c829fa0e9466b090cb0f87f/src/transformers/configuration_utils.py)。
3. Hugging Face Hub [`snapshot_download@b2ae5b6`](https://github.com/huggingface/huggingface_hub/blob/b2ae5b6a898d5303e55c256aa714f9f9a1f4bd70/src/huggingface_hub/_snapshot_download.py) 与 [`file_download@b2ae5b6`](https://github.com/huggingface/huggingface_hub/blob/b2ae5b6a898d5303e55c256aa714f9f9a1f4bd70/src/huggingface_hub/file_download.py)。
4. Hugging Face [`safetensors@6eb4dc9`](https://github.com/huggingface/safetensors/blob/6eb4dc9a28ebce297606e0f4836bbf28839cacef/README.md)。
5. Physical Intelligence [`openpi@15a9616`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：model/checkpoint/config/normalize/transforms/data_loader/policy frozen files listed above。
6. 本仓库，[ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)、[OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
