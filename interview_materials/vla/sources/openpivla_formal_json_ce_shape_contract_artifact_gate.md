# OpenPiVLA 本地 Artifact Gate：JSON/CE 动作表示与 H/D shape contract

> 状态：`local_direct_audit / formatter_probe_passed / semantics_open / WARN`
> 审查日期：2026-07-19
> 范围：`C:\Users\mousongzhe\Project\openpivla_deployment` 中 Qwen3-VL formal trainer、recipe、public smoke summary 与 action formatter；只关闭一个本地证据切片，不宣称 checkpoint、benchmark 或个人 ownership 已闭合。
> 结论先行：本地 formal trainer 的可核验实现是 **assistant JSON content + full-chat Qwen causal LM CE**，不是 assistant-token-only loss，也不是 frozen FAST DCT/BPE processor或连续 flow/action-expert loss。recipe/smoke 的模型合同是 `H=15,D=72`，但 JSON formatter 对每个 action/state row 使用 `limit=16`；实际 probe 得到 `15×16`。后续 [parser/round-trip gate](openpivla_action_json_parser_roundtrip_artifact_gate.html) 进一步确认 840/1080 个 schema positions 未序列化、formal package 中没有 action-output parser，axis/unit/decoder/controller 继续 `semantics-open`。

## 1. Evidence freeze

| ID | 本地对象 | 直接核对 | SHA-256 / 状态 |
| --- | --- | --- | --- |
| L01 | `...\vla_qwen3_repro\formal_train.py` | `_format_action_sequence`、`DroidActionTextDataset`、Qwen chat template、padding labels、`Qwen3VLForConditionalGeneration`、LoRA、`outputs.loss` | `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94` / `local-direct` |
| L02 | `...\vla_qwen3_repro\recipes.py` | `action_dim=72`、`proprio_dim=72`、`action_horizon=15`、`fast_tokenizer` 字段、三种 run recipe | `397D1B384A2BD93D9DC81B7003E6AB7BFAC3FC458EA04008197C3F503F9D780E` / `local-direct` |
| L03 | `...\vla_qwen3_repro\data.py` | public smoke dataset/batch adapter 与 action padding helper | `32C6AA76929D941C4832D2EB4C2550527D3E607E31C2A9F5507CC76EEEDBC2EC` / `local-direct` |
| S01 | `artifacts\vla_train_repro\20260305_122516-akpdp2to_smoke_summary.json` | VLA-only public smoke、`[2,15,72]`、tiny loss/grad、private data false | `local-direct` |
| S02 | `artifacts\vla_train_repro\20260310_125200-c6665s5x_smoke_summary.json` | co-train public smoke、robot/VLM batch shape、tiny loss/grad、private data false | `local-direct` |
| S03 | `artifacts\vla_train_repro\20260311_114400-nodm49pk_smoke_summary.json` | VLM-only public smoke、private data false | `local-direct` |
| R01 | `C:\Users\mousongzhe\Project\openpivla_deployment\artifacts\vla_formal_reproduction_report_20260617.html` | 报告中 100k/97.4 等汇总与历史路线描述 | `report-supported`；不作为本页 formatter 事实唯一来源 |

本页的 `Project` 路径是用户工作区外的本地项目目录；它没有被复制进本仓库，也没有改写其代码。smoke JSON 的 `private_data_deployed=false` 明确限制了“公源接口 smoke”与“私有 formal run”之间的推断。

## 2. 实际数据流：DROID row → JSON assistant → causal CE

`formal_train.py` 的 DROID path 逐步做：

1. 从 parquet 读取 `action`、`observation.state`、episode 与 language instruction；
2. 连续 action window 按 `action_horizon` 截取；
3. 每一行通过 `_to_flat_float_list(..., limit=16)`，然后 `_format_action_sequence` 在不足 horizon 时重复最后一行；
4. 生成紧凑 `{"actions": ...}` assistant 文本；
5. 通过 Qwen chat template/tokenizer；
6. collator 只把 `attention_mask==0` 的 token label 置为 `-100`；user prompt、chat wrapper 与 assistant JSON 的全部非 padding token 进入 HF causal LM `outputs.loss`。

抽象为：

\[
\text{action window}
\xrightarrow{\text{flatten/limit=16 + repeat}}
Y\in\mathbb R^{H\times16}
\xrightarrow{\text{JSON + tokenizer}}
y_{1:L}
\xrightarrow{\text{causal LM}}
\mathcal L_{\mathrm{CE}}(y).
\]

变量与边界：\(H=15\) 是 recipe 的窗口长度；`16` 是当前 formatter 的每行上限；\(L\) 是 JSON/token 文本长度，不等于 \(H\times D\)。`action_dim=72` 出现在 recipe/smoke batch contract，但当前 `formal_train.py` 的 assistant serializer 没有把 72 维 row 原样写入 JSON。除非存在 decoder/parser/axis mapping 证据，不能把 `(15,72)` 直接当作 controller-ready action。

## 3. 直接代码证据与 formatter probe

关键片段（来源为 L01）：

```python
def _format_action_sequence(values, horizon):
    # Each serialized row is flattened and truncated to at most 16 numbers.
    seq = [_to_flat_float_list(v, limit=16) for v in values]
    if not seq:
        seq = [[0.0]]
    # Tail padding repeats the last available row, not a valid-length mask.
    while len(seq) < horizon:
        seq.append(seq[-1])
    return seq[:horizon]

# The dataset writes the result as assistant-side compact JSON.
answer = json.dumps({"actions": action_seq}, separators=(",", ":"))
```

本轮用 AST 提取上述两个真实函数（没有导入完整训练栈），输入两行 72D synthetic rows、`horizon=15`：

| Probe | 结果 | 含义 |
| --- | --- | --- |
| formatter output length | `15` rows | recipe horizon 被使用 |
| every serialized row width | `16` | `limit=16` 截断真实生效 |
| short window tail | 第 3–15 行重复第 2 行 | padding 是 repeat，不是 mask |
| first row `[0..71]` | 输出前 16 个值 `[0..15]` | 72D row 未原样序列化 |

probe 输出摘要：`horizon=15`, `row_widths=[16]`, `tail_repeat=True`。这验证的是 formatter 语义，不证明 tokenizer round-trip、robot axis/unit 或 learned checkpoint。

## 4. H/D/serialized-width 冲突的正确解释

| 层 | 当前事实 | 能说什么 | 不能说什么 |
| --- | --- | --- | --- |
| recipe/model | `action_horizon=15`, `action_dim=72`, `proprio_dim=72` | formal batch/schema 目标是 `H=15,D=72` | 不能证明 JSON 每行包含 72 个可执行量 |
| smoke batch | robot `actions=[2,15,72]`，state `[2,72]` | public smoke tensor contract 通过 | 不能证明 private DROID/formal checkpoint 同源 |
| formal serializer | 每行 `limit=16`，assistant JSON | 当前 local representation 是 15 行 × 最多 16 数值 | 不能称为 15×72 的完整 action decode |
| controller boundary | 本切片未发现 parser/axis/unit/normalizer round-trip | semantics-open、需补 artifact | 不能声称 controller-ready 或 rollout success |

因此 `H=15,D=72` 与 `limit=16` 不是简单“超参数不同”：前者是 batch/model contract，后者改变了 serialized action semantics。面试中应主动指出冲突，并把“谁发现、是否修复、如何验证”作为 ownership 追问，而不是用 `shape=(15,72)` 掩盖它。

## 5. FAST 边界：字段名不是 processor 调用

`ModelRecipe` 保留 `fast_tokenizer="physical-intelligence/fast"`、`slowfast=1` 与 `fast_only=True` 等字段；但本次直接读取的 `formal_train.py` action path 使用 `json.dumps`、Qwen chat template 与 causal LM CE，没有调用 frozen FAST processor 的 DCT/quantization/BPE/inverse pipeline。

安全分类：

- **upstream-verified**：FAST 的 DCT/quantization/BPE 方法与 OpenPI/FAST frozen source；
- **local-direct**：本地 formal JSON/CE formatter；
- **representation-conflict**：仅凭 recipe 字段把 local JSON 宣称为 FAST；
- **待补**：formatter→tokenizer→decode→72D/action-controller round-trip。

## 6. Smoke evidence 与 结果边界

三个 smoke summary 都记录 Qwen3-VL recipe、public roots、batch shape 与 tiny train step；其中 VLA-only 和 co-train 的 robot batch 是 `[2,15,72]`，co-train 另有 VLM batch，且三份 summary 都写 `private_data_deployed=false`。这些文件支持：

1. 代码路径能够在 public smoke 设置下构造 batch；
2. tiny train step 能返回 loss/grad norm；
3. 三种 recipe 的 mode/config 具有可读的分层合同。

它们不支持：

- 远端 formal checkpoint 已在本地存在或可加载；
- archived `97.4%` 与这些 smoke/formal run 同一 lineage；
- private DROID/MindCube 数据已进入 smoke；
- JSON representation 已通过 robot controller 或 closed-loop success。

## 7. 对项目 claim 的回写

| Claim | 当前 verdict | 面试安全口径 | 升级所需 artifact |
| --- | --- | --- | --- |
| `OPV-CL-002` assistant JSON + causal CE | `local-direct / PASS WITH WARNING` | “formal trainer 把 action window 序列化为 assistant JSON content，但当前 objective 覆盖 full chat 非 padding token；不是 assistant-only 或连续 flow loss” | parser、token/JSON round-trip、assistant-span mask test |
| `OPV-CL-003` 复用 FAST DCT/BPE | `REPRESENTATION-CONFLICT` | “recipe 有 FAST 字段，但当前直接审计到的是 JSON/CE；不能把两者混写” | frozen processor call、revision、round-trip |
| `OPV-CL-004` H=15/D=72 action contract | `local-direct / SEMANTICS-OPEN` | “smoke tensor 是 `[B,15,72]`，但 formatter 每行 limit=16；语义闭环仍待修” | decoder、axis/unit、normalizer、controller trace |
| `OPV-CL-005` 三种 recipe | `local-direct` | “三类 recipe 与 public smoke 可读；不能据此证明三条 private formal completion” | immutable logs/checkpoints/load smoke |
| `OPV-CL-007` archived 97.4 | `archive-summary-only` | “报告有归档汇总；不是本页 local formatter/smoke 的结果证明” | checkpoint/protocol/raw episodes |

### 30 秒项目回答

“我会把这条 local route 讲成 Qwen3-VL 的 JSON action training path：代码把 action window 截成 \(H=15\)，序列化为 assistant JSON content，但 collator 只屏蔽 padding，所以实际是 full-chat causal CE。它与 FAST 的 DCT/BPE 不是同一个实现。recipe/smoke 写 \(D=72\)，formatter 每行只取 16 个数；后续 probe 又确认没有 formal Qwen parser/controller round-trip，所以不能说已经形成 72 维 controller contract。”

## 8. 风险与下一步

1. **已关闭**：local formal source 的 JSON/CE 表示、`H=15,D=72` recipe/smoke、`limit=16` serializer 与 tail-repeat probe。
2. **仍开放**：72D action 的 decode、axis order、unit/frame、normalizer、controller 与 safety contract。
3. **仍开放**：FAST 字段是否只是 recipe metadata，还是另有未读取的 processor path；需要 call-site/revision/round-trip 证据。
4. **仍开放**：checkpoint/load/eval lineage 与个人 ownership；smoke summary 不升级 C3。
5. **下一 bounded slice**：parser/round-trip negative-evidence gate 已完成；后续优先做 ownership confirmation，或补 immutable formal checkpoint/generation bundle；不新增题卡。

## 参考文献（References）

1. Local `formal_train.py`、`data.py`、`recipes.py`，路径与 SHA 见本页 Evidence freeze。
2. Local smoke summaries `vla_train_repro/*_smoke_summary.json`，本页 S01–S03。
3. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)，用于 claim tier 与真实性边界。
4. [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)，用于个人贡献边界。
5. [FAST upstream audit](vol_03_pi0_fast_openpi_independent_fact_review.html)，用于 DCT/BPE 与 local JSON/CE 的对照边界。
6. [OpenPiVLA Action JSON Parser / Round-trip Artifact Gate](openpivla_action_json_parser_roundtrip_artifact_gate.html)，用于 72→16 loss、full-sequence CE、parser absence 与 official-eval lineage 边界。
