# VOL 07 UWM / LIBERO 题卡清单

> 规划日期：2026-07-18；actionheadfix evidence refresh：2026-07-21  
> 状态：`evidence_frozen / card_drafted / WARN`  
> 题数：4  
> 节点：UWM/LIBERO 评估协议、结果 reconciliation、ownership 与真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| PROJ-UWM-001 | L3 | P0 | UWM/LIBERO 中 0.744、0.928 和论文约 0.79 三个结果如何解释，为什么不能直接比较？ | local-direct 协议/诊断 + user-confirmed remote final；RoboCasa actionheadfix/open-loop 与 h4 `0/54` 分层；缺 checkpoint、250 episode/raw trace 与 ownership，不称严格复现或性能修复 |
| PROJ-UWM-002 | L3 | P0 | UWM/LIBERO 哪些部分能说是你做的？如何区分上游、Git 快照、远端结果和个人 ownership？ | 13-row ownership ledger；`mousongzhe` commits、工作树 recovery、user-confirmed JSON 与上游机制分开；候选人确认仍 pending |
| PROJ-UWM-003 | L3 | P0 | zarr DataLoader 的周期性长停是怎么定位的？为什么 preload+infinite smoke 不能直接写成训练吞吐提升？ | local report/code 的 DataLoader-only A/B；p95 wait `13.862s→0.194s`，但缺 matched GPU throughput/memory/loss parity，保持 smoke-bounded |
| PROJ-UWM-004 | L3 | P0 | actionheadfix 的 loss 和 teacher-forced x0 都改善了，为什么 RoboCasa h4 仍是 0/54？如何定位 first divergence？ | Human300/actionheadfix train → teacher-forced group x0 → h4 target-contact 三层；`convert_action` invalid 与有效 rollout 分母分开，不称性能修复 |

## 2. 题卡退出条件

1. 4 个 ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 fixed-pruned-init、reset-style、论文 OOD protocol、report-supported 与 user-confirmed evidence。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。
5. PROJ-UWM-002 不把 Git author、用户确认 summary 或 report path 自动升级为个人 ownership。

## 3. 依赖与下一步

- 前置：[UWM / LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
- 依赖缺口：checkpoint/normalizer immutable bundle、250 条 episode JSONL、exact init/seed manifest、同 checkpoint paired protocol 与候选人 ownership 确认。
- RoboCasa 依赖缺口：h4 54 条 raw episode/contact/action trace、before/after checkpoint、wrapper-convert paired eval 与逐文件 actionheadfix ownership。
- 下一步只进行一次 `PROJ-UWM-001..004` protocol/ownership/data-pipeline/closed-loop 真实口述，或补一个 UWM raw artifact；不继续批量生成 UWM 题卡。
