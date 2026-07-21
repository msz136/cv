# OpenPiVLA P0 Bundle Audit：Formal Trainer / Action Route / Eval Lineage

> 状态：`p0_audited / partial / checkpoint-pending / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计现有 OpenPiVLA local-direct code/config/report/smoke/diagnostic evidence；不把 report summary、official checkpoint rollout 或 Git author 升级为个人 benchmark 结果。

## 1. 结论

OpenPiVLA 已具备较强的工程接口证据：Qwen3-VL + PEFT LoRA formal trainer、三类 recipe、JSON action dataset/collator、smoke summaries、部署记录、official-checkpoint rollout diagnostics 和 committed formal report 均可定位。但 P0 结果链仍是 `PARTIAL`：formal checkpoint binary/hash、三条 formal run raw logs、97.4 archive 的 trial/seed/protocol/episodes、action parser/controller round-trip、pre-snapshot diff 和候选人 ownership 未闭合。

```text
P0 status = PARTIAL
eligible benchmark claims = 0
eligible ownership claims = 0
allowed = trainer/data/loss/recipe/interface evidence
forbidden = “97.4 verified”, “higher than official 96.85”, “FAST-equivalent”, “personally trained end-to-end”
```

## 2. P0 gate matrix

| P0 字段 | 当前证据 | 状态 | 面试边界 |
| --- | --- | --- | --- |
| model/trainer identity | `formal_train.py` 加载 `Qwen3VLForConditionalGeneration`、LoRA、`outputs.loss`、adapter save | `PRESENT` | 可解释 trainer path；不等于最终 checkpoint 已加载 |
| code/config lineage | trainer、data、recipes、YAML、launch scripts、smoke/report SHA 已登记 | `PARTIAL` | 可讲接口与 recipe；pre-snapshot diff 仍缺 |
| action representation | assistant JSON content、`H=15,D=72` recipe/smoke、formatter `limit=16` | `PARTIAL / CONFLICT` | 必须说明 72D→15×16 lossy serialization；不能称 FAST DCT/BPE |
| labels/loss mask | collator 只屏蔽 padding，full-chat causal CE 可复核 | `PRESENT WITH WARNING` | 不得说 assistant-only CE 或 continuous action loss |
| parser/controller round-trip | formal package 无 action-output parser；official 7D/4-step WebSocket 是平行 lineage | `MISSING` | 不能说 formal Qwen 已完成闭环控制 |
| formal checkpoint | report/path 有 remote references，无本地 binary/hash/load smoke | `MISSING` | 97.4 保持 archive-summary-only |
| formal run ledger | 三条 launch scripts、report run table、smoke summaries | `PARTIAL` | completion 记录不能替代 raw logs/checkpoint |
| rollout/eval protocol | official LIBERO/ALOHA diagnostics 与 scripts 可读 | `PARTIAL` | 不可绑定 formal Qwen 或 97.4 |
| raw benchmark bundle | `224_h10_40000` summary 有，raw episodes/trials/seed/init/denominator 缺 | `MISSING` | 不写 verified benchmark 或高于 official |
| ownership | 13-row ledger、root snapshot author 线索 | `PENDING` | Git author 不等于逐文件个人实现 |

## 3. Deterministic technical checks

- `H=15,D=72` recipe/smoke shape 与 formatter `limit=16` 同时存在；
- 72D sentinel 经过 JSON formatter 只保留 `15×16=240` 个标量，相对 `15×72=1080` 少 840；
- collator 的 mask 只排除 padding，full-chat 非 padding token 进入 CE；
- formal package 中没有 generation/decode/action-output `json.loads` parser；唯一 `json.loads` 是 MindCube 输入；
- official `pi0_aloha_sim` rollout 为 7D/4-step，不能补 formal Qwen 的 parser/controller lineage。

这些检查支持“当前工程路径的形状、mask 和缺口”，不支持模型效果或个人 ownership。

## 4. 安全口径

可以说：

> “我能从本地 formal trainer、recipe、collator 和 smoke/report 解释 Qwen3-VL + LoRA 的数据到 loss 路径，也能指出 action JSON 的 `H=15,D=72` 与 `limit=16` 冲突，以及 formal package 缺少 parser/controller round-trip。报告里的 97.4 仍是 archive summary，checkpoint、raw episodes、protocol 和 ownership 没有闭合，所以我不把它说成高于官方 96.85 的已验证结果。”

不能说：

1. 本地已经加载并验证三条 100k formal checkpoint；
2. 97.4 是本人可复算、协议完整的 LIBERO 结果；
3. local JSON action route 等价于 FAST DCT/BPE；
4. official-checkpoint ALOHA/LIBERO rollout 就是 formal Qwen 的效果；
5. root commit author 自动证明所有文件由本人独立完成。

## 5. 关闭 P0 的最小动作

1. 导出 formal checkpoint/processor/normalizer/config 的 immutable hash 与 load smoke；
2. 为 `224_h10_40000` 提供 trial/seed/init/task/version、raw episodes、success predicate 和 reducer；
3. 实现并测试 strict JSON parser、axis/unit/normalizer/controller round-trip；
4. 提供 pre-snapshot diff、运行命令、review/协作记录，回答 `OWN-OPV-001`。

在这些字段闭合前，OpenPiVLA 保持 `PARTIAL/WARN`，不改变 `PROJ-OPENPIVLA-*` 或通用题卡 mastery。

## References

1. [OpenPiVLA Claim–Evidence Inventory](openpivla_claim_evidence_inventory.md)
2. [OpenPiVLA Ownership Ledger](openpivla_ownership_ledger.md)
3. [OpenPiVLA JSON/CE + H/D Shape Contract Gate](../../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.md)
4. [OpenPiVLA Action JSON Parser / Round-trip Gate](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.md)
5. [五项目 P0 Artifact Intake Contract](../p0_artifact_intake_contract.md)
