# OpenPiVLA Action JSON Parser / Round-trip Artifact Gate

> 状态：`local_direct_negative_evidence / retained_prefix_roundtrip_pass / controller_roundtrip_missing / WARN`  
> 审查日期：2026-07-19  
> 本地范围：`C:\Users\mousongzhe\Project\openpivla_deployment` 中 `vla_qwen3_repro` formal package、official OpenPI WebSocket eval script 与冻结 summary。  
> 结论先行：当前 Qwen formal route 只实现 **action window → assistant JSON training text**，没有找到 Qwen generation、action JSON output parser、shape/finiteness validator、normalizer 或 controller adapter。Python `json.dumps→json.loads` 能无损恢复被保留的 `15×16` 前缀，但相对 recipe 的 `15×72` 已丢失 840/1080 个标量（77.78%），因此这不是 controller round-trip。另一个 7D/4-step WebSocket artifact 使用 official OpenPI checkpoint，是平行 lineage，不能替 Qwen JSON route 补证据。

## 问题（Question）

`H=15,D=72` 的 action window 经 `limit=16` JSON formatter 后，是否存在可验证的 tokenizer/generation/parser/normalizer/controller round-trip？如果没有，当前代码到底证明了什么，哪些项目表述必须降级？

## 1. 项目分型与 Role Fit

| 字段 | 当前判断 |
| --- | --- |
| 项目类型 | VLA training/evaluation recovery + multimodal causal-LM action representation |
| 目标岗位 | VLA / Robot Policy / Multimodal Training / Embodied Evaluation |
| 当前最像 | 有 formal training source 与多条 official-checkpoint eval diagnostics，但 Qwen text-action execution contract 未闭合的研究工程项目 |
| 安全包装 | “实现并审计 JSON action-supervision training path，定位 shape/loss-mask/parser lineage 风险” |
| 禁止包装 | “完成了 72D Qwen action decoder、FAST 等价实现或 formal Qwen closed-loop deployment” |

本切片只关闭 parser/round-trip 证据门，不替候选人确认 ownership，也不把 local negative evidence 伪装成已修复功能。

## 2. Evidence freeze

| ID | 本地对象 | 直接支持 | SHA-256 |
| --- | --- | --- | --- |
| L01 | `...\vla_qwen3_repro\formal_train.py` | formatter、JSON target、collator labels、Qwen/LoRA train loop；formal package 内没有 generation/parser call | `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94` |
| L02 | `...\vla_qwen3_repro\recipes.py` | `H=15,D=72` recipe intent | `397D1B384A2BD93D9DC81B7003E6AB7BFAC3FC458EA04008197C3F503F9D780E` |
| L03 | `...\vla_qwen3_repro\runner.py` | public smoke runner；没有 formal Qwen action generation/parser | `F0908B9F824A0AAFD99F170F0FEB7F72E931F88EBC60594D9F5636E2539C13C5` |
| L04 | `scripts\eval_lerobot_action_server.py` | official `WebsocketClientPolicy` 返回 numeric `response["actions"]`；按交集裁剪后算 L1 | `B1B7FB9B7A86355B9C1843CDE971B38FD26A2DAB1F18550128671F79F1AB4F39` |
| L05 | `scripts\export_bridge_fractal_rollout_actions.py` | official OpenPI numeric action chunk、`:7` slice、replan steps | `B8222F99F0ED08939E3B8D52DE30B9386729D3C43B3B3E6D1223AE4357EC3BC8` |
| A01 | `bridge_fractal_eval_real_v2/.../widowx_spoon_on_towel/summary.json` | checkpoint=`pi0_aloha_sim`、numeric action `D=7,H=4`、4 samples | `7238B0238315852730A559AF0E01678448E4507E76F7BBCCCE608C8D426CD4E1` |

这些文件位于项目外本地目录，本轮只读，没有修改项目源码或生成新的项目 artifact。项目目录本身没有可用 `.git` metadata；ownership 继续依赖现有粗粒度 snapshot ledger 与候选人确认。

## 3. 四层合同不能混写

| 层 | 当前实现 | 当前 verdict |
| --- | --- | --- |
| training target | DROID rows 经 `limit=16`、round(5)、tail-repeat 后写成 assistant JSON content | `local-direct / lossy` |
| training objective | `labels=input_ids.clone()`，只把 attention padding 设为 `-100` | `full-sequence causal CE`，不是 assistant-token-only CE |
| formal Qwen inference | 未找到 `model.generate`、`decode/batch_decode` 或 action-output `json.loads` | `missing` |
| robot execution | 未找到 Qwen JSON schema validator、72D reconstruction、axis/unit、normalizer、controller adapter | `missing` |

formal package 中唯一的 `json.loads` 位于 `MindCubeDataset._load_rows`，读取 VLM QA 的输入 JSONL；它不是 action prediction parser。这个负面检索只证明冻结 package 中未出现相应 call，不证明其他未归档机器或分支绝对不存在 parser。

## 4. 数学合同：保留前缀不等于 72D round-trip

对非空、每行至少 16 维的典型输入，令 action window 为：

\[
A\in\mathbb R^{H\times D},\qquad H=15,\quad D=72.
\]

变量解释：\(H\) 是未来 action 行数，\(D\) 是 recipe/smoke 中的每行宽度。实现映射：`recipes.py` 给出 `action_horizon=15, action_dim=72`；该式是 schema intent，不是 serializer 输出事实。

当前 formatter 对每行做：

\[
S(A)_{h,:}=\operatorname{round}\!\left(A_{h,0:\min(D,16)},5\right).
\]

变量解释：\(S\) 是 `_format_action_sequence`，只保留前 16 个标量并四舍五入到 5 位；短 window 还会重复最后一行。实现含义：即使 JSON parser 完全正确，也只能恢复 \(S(A)\)，不能逆推出被删除的 \(A_{:,16:72}\)。

若用 Python 自带 JSON codec 记为 \(J^{-1}(J(\cdot))\)，本轮 probe 只得到：

\[
J^{-1}(J(S(A)))=S(A)\neq A.
\]

变量解释：等号左侧表示保留前缀的 Python object round-trip；右侧不等式来自 shape 和信息丢失，而不是数值误差。实现边界：这没有经过 Qwen tokenizer、model generation、schema validator、denormalizer 或 controller。

## 5. Deterministic probes

本轮从真实 AST 提取 `_to_flat_float_list`、`_format_action_sequence` 与 `Qwen3VLCollator`，不导入完整训练栈；所有 probes 只在内存中运行。

| Probe | 结果 | 判定 |
| --- | --- | --- |
| 两行 72D sentinel，`H=15` | JSON parse 后 shape=`15×16` | horizon 保留，72D 未保留 |
| serialized scalars | 240；相对 `15×72=1080` 少 840 | 77.78% schema positions 未序列化 |
| retained prefix equality | `True` | 只证明 Python JSON codec 对已保留数值可逆 |
| tail repeat | 第 3–15 行共 13 行重复第 2 行 | 没有 valid length/mask，真实重复与 padding 不可区分 |
| empty window | `15×1` 的 `[0.0]` | output width 不固定为 16/72 |
| one empty row | `15×0` | 可产生 ragged/zero-width action rows |
| NaN row | 输出 `{"actions":[[NaN],[NaN]]}` | Python 可读回非有限值，但这是非标准 JSON，且没有 finite check |
| collator labels | `[11,12,13,14,-100]` | 仅 padding 被屏蔽；四个非 padding token 全部监督 |
| formal package AST calls | `generate/decode/batch_decode=0`；`loads=1` at MindCube input | 没有 Qwen action output parser 证据 |

因此当前问题不是“parser 精度还没测”，而是 **parser contract 尚未出现在冻结 formal path 中**。

## 6. Loss-mask 事实纠正

旧材料把该 route 简写成“assistant token CE”。冻结代码实际是：

```python
# Chat template contains user prompt, wrappers and assistant JSON content.
batch = processor(text=full_chat_text, padding=True, ...)

# Only attention padding is ignored; prompt/wrapper tokens remain labels.
labels = batch["input_ids"].clone()
labels[batch["attention_mask"] == 0] = -100
loss = model(**batch).loss
```

其 token-level objective 更准确地写为：

\[
\mathcal L_{\mathrm{full\mbox{-}seq}}
=\frac{1}{N}\sum_{t:m_t=1}
-\log p_\theta(x_t\mid x_{<t}),
\]

变量解释：\(x_t\) 覆盖 chat template 的全部非 padding token，\(m_t\) 只是 attention mask，\(N=\sum_t m_t\)。实现映射：代码没有 assistant-span mask，HF causal LM 在内部做 next-token shift。它仍包含 action JSON 学习信号，但 loss 也包含可预测 prompt/wrapper；因此 loss 下降不能单独证明 action token 或 controller 行为改善。

安全术语应从“assistant-token-only CE”改为：**“assistant JSON content embedded in a full-chat causal-LM objective”**。

## 7. 为什么 official WebSocket eval 不能补 Qwen parser

`eval_lerobot_action_server.py` 的实际链路是：

```text
LeRobot obs
  -> official OpenPI WebsocketClientPolicy
  -> response["actions"] numeric array
  -> min(gt_h, pred_h, requested_h) × min(gt_d, pred_d)
  -> offline L1 diagnostic
```

A01 明确记录 checkpoint `/.../pi0_aloha_sim`、`action_dim=7`、`action_horizon=4`。这证明 official checkpoint/server 的 numeric I/O 路径可以返回动作并形成离线 L1 artifact；它不经过 Qwen JSON generation，也不使用 `H=15,D=72` formal recipe。

此外，eval script 用 `min` 裁剪 horizon/dim 后比较，没有 assert 预测 shape 等于目标 shape；因此即使该 official diagnostic 状态为 `ok`，也不能反向证明另一路 Qwen contract 严格匹配。

## 8. 缺失 parser 的最小生产合同

以下是 **建议补做**，不是当前项目已有实现：

```python
def parse_action_json(text, *, expected_h=15, expected_d=72):
    # 1. Use a strict JSON decoder; reject NaN/Infinity and extra prose.
    obj = strict_json_loads(text)

    # 2. Require exactly one actions field and a dense numeric matrix.
    actions = require_dense_finite_matrix(obj, key="actions")

    # 3. Reject shape mismatch instead of silently slicing/padding.
    assert actions.shape == (expected_h, expected_d)

    # 4. Apply the frozen normalizer/axis/unit contract.
    env_actions = denormalize_and_map_axes(actions)

    # 5. Enforce controller limits and record a round-trip trace.
    return controller_safety_check(env_actions)
```

最低测试矩阵：valid sentinel、missing key、extra prose、ragged rows、empty rows、NaN/Infinity、wrong H、wrong D、axis permutation、unit mismatch、normalizer mismatch、gripper bounds、tail validity mask、JSON→array→controller→logged-command 逐维对账。

## 9. Evidence Contract 与 claim 更新

| Claim | 证据结论 | 当前安全表达 | 禁止升级 |
| --- | --- | --- | --- |
| `OPV-CL-002` JSON/CE route | formatter/target/labels direct；parser missing | “action window 被写入 assistant JSON content，并在 full-chat causal CE 中训练” | assistant-token-only loss、controller-ready decoder |
| `OPV-CL-003` FAST reuse | formal package 无 FAST processor call | “FAST 仅作 upstream 对照；local route 是 JSON text” | FAST 等价、DCT/BPE round-trip |
| `OPV-CL-004` H/D contract | `15×72` intent → `15×16` serialized prefix；840 scalars missing | “定位到 lossy shape contract，尚未修复/闭环” | 72D action semantics 已保留 |
| `OPV-CL-010` rollout | official numeric WebSocket eval direct；Qwen lineage absent | “做过 official-checkpoint eval diagnostics” | formal Qwen closed-loop rollout |
| Ownership | 技术 finding 可复核；decision/fixer role 未确认 | “仓库/项目中发现并记录风险” | “我独立定位并修复” |

## 10. Production Gap、Question Tree 与局部评分

### Production Gap

| 当前做法 | 生产追问 | 缺口 | 可补证据 |
| --- | --- | --- | --- |
| `json.dumps` training target | 模型输出由谁解析？ | generation/parser missing | immutable checkpoint + generation samples + parser source |
| `limit=16` | 72D 中被删的是哪些轴？ | schema/axis ownership missing | field registry + sentinel axis test |
| repeat-last padding | 哪些行有效？ | valid mask/length missing | explicit `valid_horizon` + loss/execution mask |
| padding-only label mask | action signal占 loss 多少？ | assistant-span mask/metric missing | token-span audit + masked-vs-full CE ablation |
| official WebSocket L1 | 是否验证 formal Qwen？ | checkpoint lineage mismatch | same formal checkpoint/server/parser/controller bundle |

### Question Tree

```text
为什么说 round-trip 没闭合？
  -> 如果只说 json.loads 成功：追问 72→16 的 840 个标量去哪了？
  -> 如果拿 official WebSocket eval 作证：追问 checkpoint/config 是否属于 Qwen formal lineage？
  -> 如果说 loss 能下降：追问 prompt/wrapper token 是否也进入 CE？
  -> 如果声称已修复：要求 parser source、strict schema、sentinel trace 与 controller log。
```

### 局部 SP/SSP 评分（只评 action-contract 证据）

| 维度 | 当前分数 / 5 | 原因 |
| --- | ---: | --- |
| 技术洞察 | 4 | 能定位 loss mask、shape loss 与 parallel lineage |
| 可复现证据 | 3 | source hash + deterministic probe 齐全，但没有 formal checkpoint/generation |
| 生产闭环 | 1 | parser/normalizer/controller contract 缺失 |
| Ownership | 1 | candidate role/fixer 未确认 |
| 面试防线 | 4 | 可明确说清“做了什么、没做什么、如何补” |

局部结论：这是一个可信的高价值 bad-case/审计故事，但还不是“Qwen VLA 部署成功”的项目结果。

## 11. Upgrade Plan 与 Output Pack

| 时间 | 动作 | 证据升级 | 状态 |
| --- | --- | --- | --- |
| 半天 | 冻结 JSON schema、assistant span、axis/unit registry；补 strict parser 单测 | CL-002/004 从 negative evidence 到 parser contract | `可补做` |
| 1 天 | 用 immutable Qwen checkpoint 生成 valid/invalid samples，跑 tokenizer→generate→parser | inference contract 可复现 | `可补做` |
| 3 天 | 接 normalizer/controller dry-run，记录 sentinel 与 safety rejection trace | controller round-trip 可审计 | `可补做` |
| 1 周 | matched full-seq vs assistant-mask、16D vs intended schema ablation + closed-loop eval | 训练目标与效果可比较 | `可补做` |

### 30 秒回答

“我复核后不会把这条路线说成已经完成 action round-trip。formal code 只把每步 action 截到 16 个数并写成 assistant JSON；Python JSON codec 能还原这个 `15×16` 前缀，但相对 recipe 的 `15×72` 少了 840 个标量，而且 package 里没有 Qwen generate、action parser、normalizer 或 controller adapter。collator 也只屏蔽 padding，所以是 full-chat causal CE，不是 assistant-token-only CE。项目里的 7D/4-step WebSocket eval 用的是 official OpenPI checkpoint，是另一条 lineage。当前可信贡献是实现/审计训练路径并定位 contract 风险，不能说 formal Qwen 已闭环部署。”

### 简历安全表达

- 当前可写：`审计 Qwen3-VL JSON action-supervision path，定位 72→16 lossy serialization、full-sequence CE mask 与 official/Qwen rollout lineage 分叉，并建立 parser/controller 补证矩阵。`
- 补做后可写：`实现 strict action JSON parser 与 tokenizer→generation→denormalizer→controller sentinel round-trip。`
- 当前不建议写：`完成 72D Qwen action decoder并在机器人闭环验证。`

## 12. 风险与下一步

1. 本报告没有 immutable formal Qwen checkpoint，因此没有运行真实 generation；parser absence 是 frozen source/package 结论。
2. Python 对 `NaN` 的默认行为不是严格 JSON 合规；真正接口必须显式拒绝非有限值。
3. official OpenPI offline L1 使用 shape 交集，不能作为严格 I/O parity 或 closed-loop success。
4. candidate 尚未确认谁设计 `limit=16`、谁发现问题、是否曾在别处修复；ownership 保持 PENDING。
5. 下一 bounded slice 优先做 OpenPiVLA ownership confirmation drill，或冻结一个 formal checkpoint/generation bundle；不新增项目题卡，不改变 12 张卡的 `unseen` 状态。

## 参考文献（References）

1. Local `formal_train.py`、`recipes.py`、`runner.py`，路径与 SHA 见 Evidence freeze。
2. Local `eval_lerobot_action_server.py`、`export_bridge_fractal_rollout_actions.py` 与 A01 summary，路径与 SHA 见 Evidence freeze。
3. [前一阶段 JSON/CE + H/D Shape Contract Gate](openpivla_formal_json_ce_shape_contract_artifact_gate.html)。
4. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
5. [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
6. [OpenPiVLA Batch 1 Cards](../questions/proj_openpivla.html) 与 [Batch 2 Cards](../questions/proj_openpivla_batch2.html)。
7. [FAST / OpenPI upstream independent review](vol_03_pi0_fast_openpi_independent_fact_review.html)，只用于 upstream 方法与 local route 边界。
