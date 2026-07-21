# PROJ-OPENPIVLA-001 + Batch 2 证据约束下的示范回答

> 状态：`model_answer / evidence_bounded / not_candidate_transcript / unseen`  
> 更新日期：2026-07-21  
> 题目：从代码证据看，formal trainer 的模型、参数更新、稳定性选择、shape contract 与 checkpoint lineage 是什么？

## 1. 30 秒版本

> 这条 formal path 使用 Qwen3-VL 做条件生成模型，通过 PEFT LoRA 只更新 adapter 参数。训练循环把 batch 送进 `model(**batch)`，用 `outputs.loss` 做反向传播和梯度累积；collator 复制 `input_ids` 作为 labels，只把 padding 位置设为 `-100`。所以当前代码证明的是 full-chat causal CE trainer，包括 prompt、wrapper 和 assistant content 的非 padding token，不是 assistant-only CE，也不是原始 π0 的连续 flow-matching loss。代码和 report 能证明 trainer path，不能单独证明 checkpoint 效果或 benchmark 结果。

这段话只描述当前可读代码；“我实现/我修改”必须由候选人用 ownership ledger 逐文件确认。

## 2. 2 分钟版本

> 我先区分模型、可训练参数和监督目标。模型侧是 Qwen3-VL conditional-generation backbone，LoRA 通过 PEFT 注入指定 target modules，所以 optimizer 更新的是 LoRA adapter 以及配置中允许训练的参数，而不是默认意义上的全参数 Qwen。具体 trainable/total 参数量、target modules 和保存方式要以当前 config、启动脚本和 load smoke 为准。
>
> 数据侧，formal package 会把 DROID action window 或 MindCube QA 组织成 chat-style input。collator 先复制 `input_ids` 生成 labels，再依据 attention/padding mask 将 padding 位置改为 `-100`；没有看到 assistant-span-only 的 label mask。因此非 padding 的 user prompt、chat wrapper 和 assistant JSON/答案都会进入 causal cross-entropy。这个结论来自 collator 的实现，不应被描述成“只学习 action token”。
>
> 训练侧是标准 `model(**batch) → outputs.loss → backward → optimizer/gradient accumulation → checkpoint save` 路径。它不是连续 action expert 的 flow-matching objective：这里的 action 被序列化为文本/JSON 后进入语言模型 CE，表示、tokenization、parser 和执行端必须单独审计。尤其 recipe 里的 `fast_tokenizer` 字段不能证明实际调用了 FAST 的 DCT/BPE processor。
>
> 最后我会把证据分层：formal_train.py、recipes/config、smoke 和 committed report 可以证明 trainer/data contract；远端 log、checkpoint、load smoke、generation→strict parser→normalizer→controller round-trip 和 raw benchmark bundle 仍需要单独核验。因此我会说“formal trainer path 已实现/已审计”，不会直接说“模型效果已验证”或“已复现官方 97.4%”。

## 3. 证据映射

| 结论 | 证据 | 当前强度 |
| --- | --- | --- |
| Qwen3-VL + PEFT LoRA | [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 formal trainer 记录 | `local-direct / ownership-open` |
| `model(**batch)` 与 `outputs.loss` | formal trainer / committed report | `local-direct / trainer-path` |
| labels 只屏蔽 padding | `Qwen3VLCollator` 代码审计与题卡 | `local-direct / full-sequence-CE` |
| JSON/causal-CE 与 FAST 分离 | [OpenPiVLA JSON/CE Shape Gate](../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.html) | `PASS WITH WARNING / representation boundary` |
| checkpoint/benchmark 尚未闭环 | inventory 的 remote-referenced、archive-summary-only 与 ownership ledger | `WARN` |

## 4. 高频追问答法

### “为什么不是 assistant-only CE？”

因为当前 collator 的 mask 规则只把 padding 位置变成 `-100`，没有根据 assistant span 或 response token 区间生成额外 mask；所以 prompt、wrapper 和 assistant content 的非 padding token 都参与 CE。若要改成 assistant-only，需要明确 span parser、token offset、empty-response 和 batch reduction 的测试。

### “LoRA checkpoint 如何证明可加载？”

需要 base model revision、adapter/config SHA、保存目录或 immutable artifact、load command 和 stdout smoke；仅有 `save` 调用、report 行或远端路径不能证明当前环境可加载。

### “为什么这不等于 flow matching？”

flow matching 直接在连续 action/noise path 上学习向量场或速度目标；当前 formal route 把 action window 序列化为 assistant JSON/text，再用语言模型 causal CE。两者的 target、mask、decode 和执行接口不同，loss 数值不能直接比较。

### “recipe 里有 `fast_tokenizer`，是不是已经使用 FAST？”

不能这样推断。要沿 call graph 找到 FAST processor、DCT/量化/BPE、decode/IDCT 和 round-trip；当前审计显示 local JSON/CE route 与 upstream FAST 机制分开。

### “代码里有 trainer，能否说 97.4% 已复现？”

不能。97.4% 是 archive-summary-only，official 96.85 是另一条 frozen upstream baseline；缺 checkpoint lineage、trial/seed/init、harness、raw episodes 和 metric recomputation，不能做 uplift 或同源结论。

## 5. Batch 2：稳定性、证据阶梯与动作合同

### 5.1 30 秒项目版本

> 我把 OpenPiVLA formal path 拆成三层：代码直接证明 Qwen3-VL+LoRA、`eager` attention 和 `outputs.loss` 的 full-chat causal CE；public smoke 只证明公开数据的 batch/schema 与 tiny step；formal report 记录三条 `complete @ 100000`，但 raw log、checkpoint hash 和 load smoke 尚未闭合。更关键的是 recipe 的 `H=15,D=72` 与 formatter 每步 `limit=16` 冲突，action parser/normalizer/controller round-trip 不存在，所以不能说 formal Qwen 已闭环。

### 5.2 2 分钟版本

> 我会先讲稳定性决策。历史 co-train 记录出现过 Qwen3-VL flash-attention/position-id 失败，当前 `formal_train.py` 的 CLI 默认 `--attn-implementation eager`，并把它传给 `Qwen3VLForConditionalGeneration.from_pretrained`。这能证明当前路径选择了一个可诊断的兼容实现，不能证明 eager 比 flash 更快、更准或带来 benchmark uplift；要证明性能差异，必须做同硬件、同 seed、同数据和同 batch 的 profiler A/B。
>
> 然后分证据等级。三份 public smoke summary 标记 `private_data_deployed=false`，只能证明公开 roots、`(B,H,D)` shape、padding 和 tiny optimizer step；formal report 是本地报告对三条 `complete @ 100000` 和远端路径的记录，属于 report-supported/remote-referenced；当前缺 immutable raw log、checkpoint/processor SHA、load stdout、generation/parser 和 raw eval bundle。因此“报告记录完成”不等于“当前环境拥有可加载最终模型”。
>
> 最后讲动作合同。recipe/smoke 的目标是 `H=15,D=72`，但 formal JSON formatter 每步最多保留 16 个数，sentinel probe 证明 `15×72` 中有 840/1080 个位置被丢弃，tail-repeat、empty/ragged/NaN 也没有严格校验。Python `json.dumps→loads` 只能还原 `15×16` 前缀；formal package 没有 Qwen generation、strict parser、normalizer 或 controller adapter。故我的可信项目贡献是建立训练/证据审计并定位 representation/lineage 风险，而不是宣称完成 72D action deployment。

### 5.3 Batch 2 Evidence Contract

| Claim | 当前证据 | 强度 | 安全口径 |
| --- | --- | --- | --- |
| formal 默认 `eager` | `formal_train.py` CLI 与 Qwen loader call | `local-direct / C1` | 可讲兼容性选择；不能讲性能 uplift |
| public smoke 通过 | 三份 `*_smoke_summary.json`，`private_data_deployed=false` | `local-direct / C1` | 可讲 schema、shape、tiny step；不能替代私有 full run |
| 三条 `complete @ 100000` | formal reproduction report | `report-supported / C1` | 可讲报告记录；不能称本地 verified checkpoint |
| raw formal checkpoint/load | 当前缺 binary、SHA、stdout smoke | `unverified / C3` | 禁止宣称可加载、可 rollout |
| `H=15,D=72` | recipe + public smoke shape | `config/smoke / C1` | 只能说目标 shape，不等于语义闭环 |
| `limit=16` lossy formatter | local source + deterministic probe | `local-direct / C2` | 可讲 72→16 schema loss 与 bad case |
| formal parser/controller | 冻结 package 未找到 generation/parser/normalizer/controller call | `negative evidence / C2` | 可讲缺口定位，不说已修复 |
| archived `flow_matching_loss` | recipe historical metadata | `archive-summary-only` | 不与 current `outputs.loss` 合并 |
| 97.4% / official 96.85 | archive/upstream references | `non-comparable` | 不写成 current formal uplift |

当前可以讲 C1/C2：eager call graph、smoke/formal/raw 证据阶梯、shape conflict、deterministic probe、lineage manifest 设计。当前 C3 禁止讲：正式 checkpoint 已验证、72D controller-ready action、formal Qwen closed-loop success、eager 带来的性能收益或 97.4% uplift。

### 5.4 四个 Batch 2 高压追问

#### “eager 是不是比 flash 更好？”

**危险回答**：是，eager 更稳定也更快，所以最终效果更好。

**可过回答**：eager 是为了绕过 flash 的兼容问题，但我没有做性能对比。

**强回答**：

> 我只把 eager 认定为兼容性路径：代码确实把它传入 Qwen loader，历史记录也有 flash/position-id 失败，但没有同硬件、同 seed、同数据的 profiler、显存、step-time 或成功率 A/B。因此我不会说 eager 更快或更准；要验证，只能固定其他变量跑 eager/flash smoke 和 matched training comparison。

#### “smoke 和 report 都说完成，为什么还不能说有最终模型？”

**危险回答**：report 已经写了 complete，所以 checkpoint 肯定存在。

**可过回答**：smoke 和 report 的证据等级不同，raw checkpoint 还要补。

**强回答**：

> smoke 的 `private_data_deployed=false`，只验证公开数据的 schema、batch、padding 和 tiny step；report 是本地对历史/远端运行的转述，路径仍是 remote-referenced。要升级为 checkpoint lineage verified，必须拿到 raw log、checkpoint/adapter/processor SHA、新进程 load stdout 和最小 eval manifest。`complete @ 100000` 只是 steps_reached，不是可加载权重证明。

#### “`H=15,D=72` 不是已经写在 recipe 里了吗？”

**危险回答**：是，所以模型已经输出 15×72 的真实控制量。

**可过回答**：recipe 是目标 shape，但 formatter 只保留 16 维，语义还没闭合。

**强回答**：

> recipe/smoke 证明的是目标或 tensor shape，不证明 formatter、parser、normalizer、axis/unit 和 controller 共用同一合同。当前 formatter 每步最多写 16 个数，probe 证明相对 `15×72` 丢掉 840 个标量，还存在 tail-repeat、ragged 和 NaN 风险。JSON codec 只能还原保留前缀；在严格 parser、逐维 round-trip 和 controller trace 出现前，不能称 72D action 已验证。

#### “历史日志有 flow matching loss，能否说 current trainer 做了 flow matching？”

**危险回答**：能，loss 名字已经说明模型在做 flow matching。

**可过回答**：那是历史 metadata，current code 目前看到的是 `outputs.loss`。

**强回答**：

> 我会把两条证据分开：`recipes.py` 中的 `flow_matching_loss` 是 archived historical metadata；current formal trainer 明确执行的是 chat-template token labels 进入 Hugging Face `outputs.loss` 的 causal CE。没有同一代码、checkpoint、action head 和 parser lineage，就不能把它们称为同一个 loss 或连续修复。要重建 flow-matching 结论，需要直接看到连续 action/noise target、训练 call graph 和可加载权重。

### 5.5 Batch 2 追问树与 lineage 最小合同

```text
“三条 formal run 已完成”
  -> 追问 raw log、checkpoint/processor SHA、load stdout、eval manifest
  -> 缺任一项：降级为 report-supported

“模型预测 15×72 action”
  -> 追问 formatter 输出、strict parser、axis/unit、normalizer、controller trace
  -> 出现 limit=16：定位 840/1080 dropped positions

“eager 带来收益”
  -> 追问同硬件/seed/data/batch 的 flash A/B profiler
  -> 没有对照：只保留 compatibility claim

“我负责这次修复”
  -> 追问具体文件、函数、diff、operator、reviewer 和验收命令
  -> 只有 report/author：ownership 保持 pending
```

最小 lineage manifest 必须绑定：`run_id`、trainer/config/recipe SHA、base model revision、LoRA adapter、checkpoint/processor SHA、data manifest、raw log、load smoke、eval harness 与 episode manifest。只记录 `steps_reached=100000` 不足以证明权重存在或结果可复算。

## 6. 练习边界

- 这是示范回答，不是候选人 transcript；不要把第一人称事实自动认领为个人贡献。
- 真实回答应至少指出一个具体函数/文件、label mask 规则、`H/D` contract 缺口和一个证据缺口。
- 真实口述前，`PROJ-OPENPIVLA-001` 保持 `unseen`，不创建 `coaching_state.md`。

## References

1. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
2. [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
3. [OpenPiVLA JSON/CE + H/D Shape Gate](../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.html)。
4. [OpenPiVLA Action JSON Parser / Round-trip Gate](../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html)。
5. [PROJ-OPENPIVLA-001..008 Atomic Cards](../questions/proj_openpivla.html)。
6. [OpenPiVLA Batch 2 Evidence Freeze](../sources/openpivla_batch2_evidence_freeze.html)。
7. [PROJ-OPENPIVLA-009..012 Atomic Cards](../questions/proj_openpivla_batch2.html)。
