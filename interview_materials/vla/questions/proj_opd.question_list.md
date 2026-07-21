# PROJ-OPD Batch 1 + Ownership Question List

> 状态：`drafted / 9 cards / all unseen / WARN`  
> 前置证据：[OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)  
> 正文：[OPD 题卡](proj_opd.html)

| ID | 难度 | 优先级 | 主题 | 主要 claim | 状态 |
| --- | --- | --- | --- | --- | --- |
| `PROJ-OPD-001` | L2 | P0 | OPD 问题定义与五 expert student | OPD-CL-001 / 012 | unseen |
| `PROJ-OPD-002` | L2 | P0 | expert quota、image split、relation bucket | OPD-CL-001 / 002 | unseen |
| `PROJ-OPD-003` | L3 | P0 | seen/unseen、boundary、format-conflict | OPD-CL-003 / 004 | unseen |
| `PROJ-OPD-004` | L2 | P0 | coldstart500 vs online OPD5000 | OPD-CL-005 / 006 | unseen |
| `PROJ-OPD-005` | L3 | P0 | route teacher selection vs learned router | OPD-CL-006 / 012 | unseen |
| `PROJ-OPD-006` | L3 | P0 | checkpoint selection与多目标 trade-off | OPD-CL-007 / 008 | unseen |
| `PROJ-OPD-007` | L2 | P0 | raw-holdout leakage与重复图片 | OPD-CL-009 | unseen |
| `PROJ-OPD-008` | L3 | P1 | point protocol、因果与 ownership 边界 | OPD-CL-010..012 | unseen |
| `PROJ-OPD-009` | L3 | P0 | 逐文件 ownership、Git identity、run/result 边界 | OPD-CL-012 + ownership ledger | unseen |

## 题卡退出条件

1. 9 个 ID 全局唯一，全部保持 `unseen`。
2. 每题包含面试意图、30 秒回答、机制展开、诊断/证据、项目挂钩、追问树、危险答案、来源和练习状态。
3. 每题显式绑定 OPD inventory claim，不把 report-supported 或 protocol-limited 数字写成无条件事实。
4. 不把 route metadata 写成 learned router，不把 OPD5000 写成所有 checkpoint/pool 的全局最佳，不把 static raw-holdout 写成真实机器人成功率。
5. PROJ-OPD-009 不把 Git author、report summary 或候选账号提交自动升级为个人 ownership；真实口述前保持 pending。

## 下一批候选

- `PROJ-OPD-010`：旧版 OPD final 与新版 OPD5000 checkpoint lineage 如何统一。
- `PROJ-OPD-010`：aggregate summary 为什么不能替代 by-format/by-pool 表。
- `PROJ-OPD-011`：single-teacher、SFT-only、synthetic-ratio ablation 如何设计。
- `PROJ-OPD-012`：如何建立 OPD 逐文件 ownership ledger 与现场复现清单。
