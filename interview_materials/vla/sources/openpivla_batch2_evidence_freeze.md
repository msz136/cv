# OpenPiVLA Batch 2：eager/MACA、smoke/formal/raw log 与 shape/lineage 证据冻结

> 审计日期：2026-07-17  
> 状态：`drafted / local-source-frozen / WARN`  
> 作用：为 `PROJ-OPENPIVLA-009..012` 题卡冻结最小证据，不把配置字段、报告摘要或远端路径升级成已验证结果。  
> 当前主结论：本地 formal trainer 的 attention 与 loss 路径可直接读；`H=15/D=72` 只在 recipe/smoke tensor contract 中直接出现，formal JSON action text 的每步向量实际被截到最多 16 个数；formal raw log、checkpoint hash、parser roundtrip 与 axis/unit 语义仍未闭合。

## 1. 问题与范围（Question / Scope）

本页只回答四个面试准备问题：

1. 为什么 local formal trainer 默认使用 eager attention？它证明了什么，不能证明什么？
2. smoke summary、formal report、raw log/checkpoint 的证据等级如何分层？
3. `H=15, D=72` 是真实 action contract，还是仅 config/smoke shape？formal formatter 是否保持该宽度？
4. 怎样设计一个可审计的 checkpoint lineage manifest，才能把 run、代码、数据、权重和 eval 连接起来？

本页不复核官方 π0/FAST 的算法定义，也不重新判定 97.4% 与 official 96.85 的可比性；这些仍由既有 OpenPiVLA inventory 和 Batch 1 题卡管理。

## 2. 冻结输入与证据类型

| 输入 | 类型 | SHA-256 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| `repro_train/.../formal_train.py` | local-direct | `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94` | Qwen load、eager 参数、LoRA、JSON formatter、causal-CE batch、checkpoint 写出 | checkpoint binary 存在、parser/controller roundtrip、benchmark success |
| `repro_train/.../data.py` | local-direct | `32c6aa76929d941c4832d2eb4c2550527d3e607e31c2a9f5507cc76eeedbc2ec` | public smoke 的 `(H,D)` padding、占位 action、数据 manifest | 历史 DROID 私有数据的真实轴序、单位和语义 |
| `repro_train/.../recipes.py` | local-direct + historical-log metadata | `397d1b384a2bd93d9dc81b7003e6ab7bfac3fc458ea04008197c3f503f9d780e` | `action_dim=72`、`action_horizon=15`、三类 run、历史 `flow_matching_loss` 文字记录 | 这些字段已被 current formal runtime 等价执行 |
| 三份 YAML recipe | local-direct | `20260305/10/11` 三份文件已冻结 | run id、mode、public smoke 与 full data 缺口 | 远端 full run 的 raw config/log |
| 三份 `*_smoke_summary.json` | local-direct | `b6211977...`、`cd7d1eae...`、`5c09d0ee...` | public roots、batch shape、tiny train step、`private_data_deployed=false` | 私有数据训练、正式 checkpoint、online rollout |
| `vla_train_repro_report.html` | local report | `50b0da3bb6bd7e880b14b42101aef76e099f87a6ba841ce31e60a4cc726f2ec6` | smoke/prepare/shape 解释与历史路径边界 | raw log 或 checkpoint binary 本身 |
| `vla_formal_reproduction_report_20260617.html` | report-supported | `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074` | 报告记录的 eager、三条 `complete @ 100000`、远端输出路径 | 本地可重放的 raw formal logs、checkpoint hash、load smoke |
| `DEPLOYMENT.md` | local-direct deployment ledger | `c0a3dd0c0da8c1c0d36023046d5337900a71680b413657bc9b1062eef2eea14e` | MACA runtime、official checkpoint 与远端 formal 路径边界 | formal Qwen checkpoint binary 或 archive→formal lineage |
| `Project` Git snapshot | authorship signal | `6c524d9c6c6226075f100cdac395fef2fdc37671` | snapshot revision 和粗粒度 author 信号 | per-file ownership、协作/工具边界 |

证据命名采用四层：`local-direct`（当前文件可直接读取）、`report-supported`（本地报告转述的运行事实）、`remote-referenced`（只有远端路径或历史引用）、`unverified`（缺关键 artifact）。

## 3. Eager attention 与 MACA 稳定性边界

### 3.1 直觉

原历史 co-train run 的记录指向 Qwen3-VL flash-attention / position-id 失败；当前 formal CLI 默认把 attention 实现切到 eager，目标是先获得可诊断、可保存的 Qwen causal-LM 训练路径。它是稳定性与兼容性选择，不是模型质量提升证明。

### 3.2 代码映射

`formal_train.py` 的模型构造把 `args.attn_implementation` 传给 `Qwen3VLForConditionalGeneration.from_pretrained`；CLI 默认值为 `eager`。同一文件的训练循环调用 `outputs = model(**batch)`，再对 `outputs.loss` 反传。最小调用链可写成：

```text
# 仅描述当前 local formal path，不代表历史 upstream trainer
parse --attn-implementation (default=eager)
    -> Qwen3VLForConditionalGeneration.from_pretrained(..., attn_implementation=...)
    -> processor/chat_template + labels(mask padding=-100)
    -> outputs = model(**batch)
    -> loss = outputs.loss
    -> backward / optimizer.step / save_pretrained
```

### 3.3 能说与不能说

| 口径 | 证据等级 | 安全表述 |
| --- | --- | --- |
| eager 参数和调用位置 | local-direct | “我在 Qwen formal path 中默认使用 eager，避开已记录的 flash-attention 兼容失败点。” |
| 100k 被报告记录 | report-supported + remote-referenced | “报告记录了完成状态和输出路径。” |
| MACA 性能/吞吐优于 flash | unverified | 没有 profiler、吞吐对照或完整 raw log，不能这样说。 |
| eager 导致 benchmark 提升 | unverified | attention 稳定性与任务成功率之间没有闭合因果证据。 |

## 4. Smoke、formal report 与 raw log 的证据阶梯

### 4.1 三类 artifact 的合同

| 层级 | 当前实际内容 | 可以证明 | 不能证明 |
| --- | --- | --- | --- |
| public smoke summary | 三份 JSON；public roots；`(images,input_ids,states,actions)` shapes；tiny train step；私有数据标记为 false | schema、padding、batch、反传通路和基础 runtime 可用 | 历史私有 DROID/MindCube、100k full run、checkpoint 可加载 |
| formal report | 本地 HTML 记录三条 run 的 mode、loss、`complete @ 100000`、远端日志/输出路径 | 报告作者在该 revision 记录了这些事实 | 当前工作区拥有 raw log、checkpoint SHA 或可复现 eval |
| raw log / checkpoint / load smoke | 当前工作区未发现对应 formal binary、immutable log bundle 或 load stdout | 若补齐，可闭合 run→weight→eval lineage | 目前不能把 report summary 写成 local-verified checkpoint |

### 4.2 历史 `flow_matching_loss` 与 current `outputs.loss` 必须拆开

`recipes.py` 中 `20260305` 的 `EvidenceRecipe.important_log_facts` 保留了历史日志文字：step 0 记录过 `flow_matching_loss`。这是一条 archived historical metadata；它不等于 current `formal_train.py` 正在计算同一个 loss。当前代码唯一显式反传的是 Hugging Face `outputs.loss`，其输入是 chat-template 生成的 token labels。

因此面试中要说：

- 历史 run metadata 可以支持“归档路径曾记录过 flow-matching loss 名称”；
- current local formal trainer 可以支持“Qwen causal-LM CE 路径可读”；
- 两者之间没有已冻结的同一 checkpoint、同一代码、同一 parser 和同一 action head lineage，不能称为等价实现或同一 loss 的连续修复。

## 5. `H=15, D=72`：配置/Smoke shape 与 formal JSON 的不一致

### 5.1 先定义 shape

用 (mathbf{A}inmathbb{R}^{H	imes D}) 表示一个动作窗口，其中 (H) 是未来动作步数（horizon），(D) 是每步动作向量宽度（action dimension）。当前 recipe 声明 (H=15,D=72)，对应“15 步、每步 72 个数”的目标 shape；这只是变量定义，不能单独证明每个数的轴序、单位或控制语义。

### 5.2 三条证据路径

| 路径 | 代码事实 | 结论 |
| --- | --- | --- |
| recipe/model metadata | `ModelRecipe.action_dim=72`、`proprio_dim=72`、`action_horizon=15` | 配置层目标 shape 是 `(15,72)` |
| public smoke adapter | `PublicRobotFrameDataset` 将单行 action 宽度补齐到 `D`，再沿 horizon 重复；collator pad 到 `(H,D)`；三份 smoke JSON 报告 `(B,15,72)` | smoke tensor contract 可运行，但包含占位/重复动作逻辑，不是正式 DROID 语义 |
| current formal JSON formatter | `_to_flat_float_list(v, limit=16)` 被 `_format_action_sequence` 用于每步 action；state 也以 `limit=16` 截断；JSON 只保证最多 15 个列表、每列表最多 16 个数 | current formal text path 没有直接证明每步保留 72 维；`D=72` 与实际 formatter 宽度存在未闭合缺口 |

关键风险不是“shape 写错”这么简单，而是：`H` 影响未来窗口长度，`D` 影响动作序列的语义宽度；若 formatter、tokenizer、parser、normalizer 和 controller 没有同一份 contract，训练 loss 能下降也不能推出可执行动作正确。

### 5.3 必须补的 schema/roundtrip 证据

1. 一个真实 DROID parquet sentinel row：记录原始 action 长度、字段名、episode 边界和单位。
2. formatter 输出 JSON：记录每步长度、是否截断、padding/重复策略和数值精度。
3. parser：JSON → 数组的代码、异常处理、期望 shape `(15,72)` 或其他实际 shape。
4. normalizer/denormalizer：统计量来源、轴序、单位和夹爪维度。
5. controller adapter：数组如何切片、重排、转单位并进入仿真/机器人。
6. roundtrip test：sentinel action → JSON → parser → controller input，逐维比较误差和语义映射。

## 6. Checkpoint lineage manifest（设计稿，不是已存在 artifact）

下面的 manifest 是下一步补证据的最小合同；当前只完成字段设计，不能当作 checkpoint 已经存在的证明。

```yaml
# 每一个 run 必须能从代码、数据、权重一路追到 eval
run_id: 20260310_125200-c6665s5x
trainer_sha256: 51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94
recipe_sha256: 397d1b384a2bd93d9dc81b7003e6ab7bfac3fc458ea04008197c3f503f9d780e
config_sha256: <frozen-yaml-sha256>
base_model_id: Qwen/Qwen3-VL-2B-Instruct
base_model_revision: <local-model-manifest-or-hash>
adapter_type: PEFT-LoRA
checkpoint_path: <immutable-path>
checkpoint_sha256: <missing>
processor_sha256: <missing>
data_manifest_sha256: <private-or-public-manifest>
steps_reached: 100000
raw_log_sha256: <missing>
load_smoke_command: <command-and-stdout-sha>
eval_harness_sha256: <script/config-sha>
episode_manifest_sha256: <missing>
status: report-supported / lineage-open
```

字段的设计依据是：只记录 `complete` 不足以证明权重存在；只有把脚本、config、base model、adapter、checkpoint、processor、数据 manifest、raw log、load smoke 和 eval harness 绑定，才有可重放的 lineage。

## 7. 项目口述安全边界

**30 秒版本**：我把 Batch 2 拆成三层证据：eager 和 Qwen `outputs.loss` 能从 local formal code 直接读；smoke 只证明公开数据的 `(B,15,72)` tensor 和 tiny step；formal report 记录了三条 100k，但 raw log、checkpoint hash、load smoke 尚未在本地闭合。更关键的是 recipe 的 `D=72` 与 formal JSON formatter 的每步 `limit=16` 还需要 parser/axis/unit roundtrip，不能直接说 action contract 已验证。

**高压追问应主动承认**：历史 recipe 中出现过 `flow_matching_loss` 字段，但那是 archived metadata；current formal path 反传的是 Qwen causal CE。没有同一代码和 checkpoint lineage，就不把两者说成等价修复。

## 8. 当前结论与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| eager call graph | `PASS / local-direct` | 保留 `eager` 兼容性表述，不写性能 uplift |
| smoke vs formal evidence ladder | `PASS WITH WARNING` | 为每条 run 收集 raw log、checkpoint SHA 与 load smoke |
| `H=15,D=72` semantic contract | `WARN / representation-conflict` | 补 sentinel、parser、normalizer、axis/unit 与 controller roundtrip |
| checkpoint lineage manifest | `DRAFT / unverified` | 用 immutable manifest 连接 run→weight→eval |
| oral drill | `PENDING` | 题卡生成后保持 `unseen`，逐题口述才更新状态 |

## 参考来源（References）

1. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py`，SHA `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94`。
2. 本地 `...\data.py`，SHA `32c6aa76929d941c4832d2eb4c2550527d3e607e31c2a9f5507cc76eeedbc2ec`。
3. 本地 `...\recipes.py`，SHA `397d1b384a2bd93d9dc81b7003e6ab7bfac3fc458ea04008197c3f503f9d780e`。
4. 三份 YAML：`repro_train/configs/20260305_122516-akpdp2to.yaml`、`20260310_125200-c6665s5x.yaml`、`20260311_114400-nodm49pk.yaml`。
5. 三份本地 smoke summary：`artifacts/vla_train_repro/*_smoke_summary.json`；其 `private_data_deployed=false` 与 batch shape 已核验。
6. 本地 `artifacts/vla_train_repro_report.html`，SHA `50b0da3bb6bd7e880b14b42101aef76e099f87a6ba841ce31e60a4cc726f2ec6`。
7. 本地 `artifacts/vla_formal_reproduction_report_20260617.html`，SHA `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074`。
8. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\DEPLOYMENT.md`，SHA `c0a3dd0c0da8c1c0d36023046d5337900a71680b413657bc9b1062eef2eea14e`。
9. 本地 [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)，记录 local-direct / report-supported / remote-referenced / archive-summary-only 边界。
10. 本地 [OpenPiVLA Batch 1 题卡](../questions/proj_openpivla.html)，`PROJ-OPENPIVLA-001..008`；本页对应后续 `009..012` 的证据冻结。
