# 五项目 Ownership Confirmation Queue

> 状态：`ownership_drill / five_projects / 40_slots / unseen / WARN`  
> 目的：把五份 ownership ledger 中的候选人确认项变成可逐题执行的训练队列。该页只定义问题、所需证据和安全状态，不代表候选人已经回答，也不创建 `coaching_state.md`。  
> 执行规则：一次只问一题；没有真实回答前，所有条目保持 `unseen`，不能把 Git author、文件存在、示范回答或 Codex 生成内容当作 ownership。

## 1. 角色词汇

每个问题回答时，只能从以下角色中选择并解释：

| 角色 | 含义 | 可用第一人称 |
| --- | --- | --- |
| `self-designed` | 本人做了关键设计或取舍 | “我决定……” |
| `self-implemented` | 本人亲手修改/编写并能定位函数 | “我改了……” |
| `collaborative` | 与他人共同完成，边界需说明 | “我和……协作……” |
| `tool-assisted` | 工具/Codex 生成或落地，本人负责审查/验收 | “工具实现，我审查/验收……” |
| `reviewed-only` | 只读、复核或提出问题，没有实现 ownership | “我审计了……” |
| `ran-only` | 只运行或操作远端流程 | “我运行了……” |
| `unknown` | 当前证据不足，不猜 | “我无法确认……” |

强 ownership 需要同时具备：文件/函数 locator、具体动作、过程或决策证据、运行/验收证据和协作边界。缺任一项，答案降级为 `role-confirmation-pending`。

## 2. 统一回答格式

每题只提交下面这一段，不要一次回答整张表：

```text
queue_id: OWN-WAM-001
role: self-designed | self-implemented | collaborative | tool-assisted | reviewed-only | ran-only | unknown
answer: <自然语言回答，30–120 秒>
file_or_function_locator: <路径、函数、commit 或 artifact；没有就写 unknown>
evidence: <diff / log / manifest / review / raw output；没有就写 unknown>
boundary: <协作者、工具、上游、远端 operator/reviewer>
confidence: High | Medium | Low
```

## 3. 队列总览

| 顺序 | Queue ID | 项目 | 主题 | 主要证据入口 | 状态 |
| ---: | --- | --- | --- | --- | --- |
| 1 | `OWN-WAM-001` | Cosmos/WAM | 你具体修改或决定了哪一个训练/诊断接口？ | [WAM ledger](../evidence/projects/wam_ownership_ledger.md) | `unseen` |
| 2 | `OWN-WAM-002` | Cosmos/WAM | CoffeePressButton bundle 是谁生成、运行、审查的？ | [WAM artifact manifest](../evidence/projects/wm019_wam_artifact_manifest.md) | `unseen` |
| 3 | `OWN-WAM-003` | Cosmos/WAM | 你如何区分上游机制、项目适配和个人原创？ | [WAM ledger](../evidence/projects/wam_ownership_ledger.md) | `unseen` |
| 4 | `OWN-WAM-004` | Cosmos/WAM | action/future/value 与 slot/mask 的具体证据是什么？ | [WAM claim inventory](../evidence/projects/wam_claim_evidence_inventory.md) | `unseen` |
| 5 | `OWN-WAM-005` | Cosmos/WAM | 0-success 诊断中你做了什么，哪些仍是假设？ | [WAM ledger](../evidence/projects/wam_ownership_ledger.md) | `unseen` |
| 6 | `OWN-WAM-006` | Cosmos/WAM | offline future metric 与 rollout path 如何绑定？ | [WAM paired diagnostic](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.md) | `unseen` |
| 7 | `OWN-WAM-007` | Cosmos/WAM | 哪个指标可以被你安全地称为本地结果？ | [WAM inventory](../evidence/projects/wam_claim_evidence_inventory.md) | `unseen` |
| 8 | `OWN-WAM-008` | Cosmos/WAM | 如果重做，第一件 P0 artifact 是什么？ | [P0 intake](../evidence/p0_artifact_intake_contract.md) | `unseen` |
| 9 | `OWN-OPV-001` | OpenPiVLA | `formal_train.py` 中哪些函数是你的 ownership？ | [OpenPiVLA ledger](../evidence/projects/openpivla_ownership_ledger.md) | `unseen` |
| 10 | `OWN-OPV-002` | OpenPiVLA | JSON action formatter、label mask 和 CE 路由是谁决定的？ | [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.md) | `unseen` |
| 11 | `OWN-OPV-003` | OpenPiVLA | `H=15,D=72` 与 `limit=16` 冲突是谁发现、谁修复？ | [JSON/CE gate](../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.md) | `unseen` |
| 12 | `OWN-OPV-004` | OpenPiVLA | 三类 recipe 的设计、实现、运行分别归谁？ | [OpenPiVLA ledger](../evidence/projects/openpivla_ownership_ledger.md) | `unseen` |
| 13 | `OWN-OPV-005` | OpenPiVLA | MACA/eager fallback 是技术事实还是个人决策？ | [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.md) | `unseen` |
| 14 | `OWN-OPV-006` | OpenPiVLA | 你亲自运行过哪些 smoke、load 或 rollout？ | [OpenPiVLA ledger](../evidence/projects/openpivla_ownership_ledger.md) | `unseen` |
| 15 | `OWN-OPV-007` | OpenPiVLA | 97.4 与 official 96.85 的 provenance 如何拆开？ | [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.md) | `unseen` |
| 16 | `OWN-OPV-008` | OpenPiVLA | 如果重做，第一件 P0 artifact 是什么？ | [P0 intake](../evidence/p0_artifact_intake_contract.md) | `unseen` |
| 17 | `OWN-RH-001` | Robot Harness | 你定义了哪些 robot scope/cancel/compensation 约束？ | [Harness ledger](../evidence/projects/robot_harness_ownership_ledger.md) | `unseen` |
| 18 | `OWN-RH-002` | Robot Harness | registry/runtime 代码哪些由 Codex 实现、你如何验收？ | [Harness inventory](../evidence/projects/robot_harness_claim_evidence_inventory.md) | `unseen` |
| 19 | `OWN-RH-003` | Robot Harness | SFT/GRPO 数据路由与 reward 是谁设计和实现？ | [Harness ledger](../evidence/projects/robot_harness_ownership_ledger.md) | `unseen` |
| 20 | `OWN-RH-004` | Robot Harness | 32B base/SFT/GRPO 数字的 run/operator/scorer 归属是什么？ | [Harness inventory](../evidence/projects/robot_harness_claim_evidence_inventory.md) | `unseen` |
| 21 | `OWN-RH-005` | Robot Harness | 为什么不能把 sandbox 100% 说成物理成功率？ | [Harness aggregate gate](../evidence/projects/robot_harness_10suite_aggregate_bundle_gate.md) | `unseen` |
| 22 | `OWN-RH-006` | Robot Harness | 你审查过哪一个 bad case 或 rejected alternative？ | [Harness ledger](../evidence/projects/robot_harness_ownership_ledger.md) | `unseen` |
| 23 | `OWN-RH-007` | Robot Harness | common-support raw bundle 的 operator/reviewer 是谁？ | [Common-support manifest](../evidence/projects/robot_harness_common_support_raw_bundle_manifest.md) | `unseen` |
| 24 | `OWN-RH-008` | Robot Harness | 如果重做，第一件 P0 artifact 是什么？ | [P0 intake](../evidence/p0_artifact_intake_contract.md) | `unseen` |
| 25 | `OWN-OPD-001` | OPD | 五 expert 数据配比与 image-hash split 谁决定？ | [OPD ledger](../evidence/projects/opd_ownership_ledger.md) | `unseen` |
| 26 | `OWN-OPD-002` | OPD | metadata route 与 learned router 的边界是什么？ | [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.md) | `unseen` |
| 27 | `OWN-OPD-003` | OPD | coldstart、student rollout 和 full-vocabulary KL 谁实现/审查？ | [OPD ledger](../evidence/projects/opd_ownership_ledger.md) | `unseen` |
| 28 | `OWN-OPD-004` | OPD | raw-holdout 去重和 point protocol 谁运行、谁验收？ | [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.md) | `unseen` |
| 29 | `OWN-OPD-005` | OPD | OPD final 与 OPD5000 是否同一条 lineage？ | [OPD ledger](../evidence/projects/opd_ownership_ledger.md) | `unseen` |
| 30 | `OWN-OPD-006` | OPD | 现有数字为什么不能归因于 OPD 单一因素？ | [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.md) | `unseen` |
| 31 | `OWN-OPD-007` | OPD | 你能现场解释哪一个 scorer/parser 函数？ | [OPD ledger](../evidence/projects/opd_ownership_ledger.md) | `unseen` |
| 32 | `OWN-OPD-008` | OPD | 如果重做，第一件 P0 artifact 是什么？ | [P0 intake](../evidence/p0_artifact_intake_contract.md) | `unseen` |
| 33 | `OWN-UWM-001` | UWM/LIBERO | task map、pruned-init、normalizer 和 horizon 谁决定？ | [UWM ledger](../evidence/projects/uwm_libero_ownership_ledger.md) | `unseen` |
| 34 | `OWN-UWM-002` | UWM/LIBERO | official repro 与 RoboCasa patch 的个人边界是什么？ | [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.md) | `unseen` |
| 35 | `OWN-UWM-003` | UWM/LIBERO | DataLoader stall 是谁发现、谁设计 A/B、谁运行？ | [UWM ledger](../evidence/projects/uwm_libero_ownership_ledger.md) | `unseen` |
| 36 | `OWN-UWM-004` | UWM/LIBERO | `186/250` 的结果 provenance 和 operator/reviewer 是什么？ | [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.md) | `unseen` |
| 37 | `OWN-UWM-005` | UWM/LIBERO | strict/reset/paper 三套协议为何不能混比？ | [UWM ledger](../evidence/projects/uwm_libero_ownership_ledger.md) | `unseen` |
| 38 | `OWN-UWM-006` | UWM/LIBERO | 你亲自改过哪一个 launcher、patch 或 scorer？ | [UWM ledger](../evidence/projects/uwm_libero_ownership_ledger.md) | `unseen` |
| 39 | `OWN-UWM-007` | UWM/LIBERO | 哪个 claim 必须保持 user-confirmed-remote-final？ | [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.md) | `unseen` |
| 40 | `OWN-UWM-008` | UWM/LIBERO | 如果重做，第一件 P0 artifact 是什么？ | [P0 intake](../evidence/p0_artifact_intake_contract.md) | `unseen` |

## 4. 状态与评分边界

- `unseen`：题目已准备，但候选人没有提交真实回答。
- `captured`：已收到原始回答，尚未完成教练分析。
- `reviewed`：已完成五维 rubric、证据越界和 ownership 边界检查。
- `confirmed`：候选人回答与 artifact/ledger 相互印证；只对该条目生效。
- `blocked`：证据冲突或缺失，保持保守措辞；不等于候选人能力为零。

该队列不自动改变 280 张通用题卡的 mastery。只有真实回答进入 interview-coach 流程后，才可以创建或更新 `coaching_state.md`。

## 5. 当前入口

队首仍是 `OWN-WAM-001`。准备时先阅读 [WAM implementation-derived model answer](wam_oral_model_answer.html) 的 `PROJ-WAM-002` ownership section，再实际回答这一题；model answer 不迁移状态。若候选人先练项目主叙事，也只提交 `PROJ-WAM-001`，不能同时提交两题。

## References

1. [VOL 07 五项目证据 Reconciliation](../sources/vol_07_project_evidence_reconciliation.md)
2. [五项目 P0 Artifact Intake Contract](../evidence/p0_artifact_intake_contract.md)
3. [首轮口述 Drill Queue](oral_drill_queue.md)
