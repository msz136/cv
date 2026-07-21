# PROJ-OPENPIVLA 题卡清单（Direct-Evidence Batch 1）

> 规划日期：2026-07-17  
> 状态：`local_direct_audit / batch_1_drafted / WARN`；题卡 review：[`proj_openpivla.review.json`](proj_openpivla.review.json)  
> 题数：8  
> 项目：OpenPI / OpenPiVLA / Qwen3-VL / MACA-C500  
> 规则：只把已读取的源码、配置、报告和诊断 artifact 写成事实；97.4%、formal checkpoint lineage、official comparison 与 ownership 继续作为显式待核项。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| PROJ-OPENPIVLA-001 | L2 | P0 | 从代码证据看，formal trainer 的模型、参数更新和 loss 是什么？ | local-direct；不证明 checkpoint 效果 |
| PROJ-OPENPIVLA-002 | L2 | P0 | local action route 如何把连续 action window 变成 Qwen supervision？ | local-direct JSON/CE；不等价 FAST |
| PROJ-OPENPIVLA-003 | L3 | P0 | 为什么不能把 `fast_tokenizer` 字段说成 local FAST DCT/BPE 实现？ | representation boundary |
| PROJ-OPENPIVLA-004 | L2 | P0 | VLA-only、VLM-only、co-train 三类 recipe 的数据流区别是什么？ | recipe/config/smoke direct；不证明结果优劣 |
| PROJ-OPENPIVLA-005 | L3 | P1 | 三条 100k formal run 应该如何分层陈述？ | report-supported + remote-referenced |
| PROJ-OPENPIVLA-006 | L3 | P0 | `224_h10_40000` 的 97.4% 能否与 official 96.85 比较？ | archive-summary-only / comparison open |
| PROJ-OPENPIVLA-007 | L2 | P0 | local ALOHA/LIBERO/replay artifacts 分别证明什么？ | diagnostics vs task success |
| PROJ-OPENPIVLA-008 | L3 | P1 | 如何回答 OpenPiVLA 的个人 ownership？ | Git-supported coarse signal；ledger missing |

## 2. 题卡退出条件

1. 8 个 ID 全局唯一，均保持 `unseen`。
2. 每题包含短答案、机制展开、诊断/证据、项目挂钩、追问树、危险答案和来源。
3. 每题显式区分 `local-direct`、`report-supported`、`remote-referenced`、`archive-summary-only` 或 `unverified`。
4. 不把 97.4% 写成 current Qwen formal 结果，不把 local JSON/CE 写成 FAST 等价实现，不把 Git author 写成完整 ownership 证明。

## 3. 下一批候选

- `PROJ-OPENPIVLA-009`：eager attention 与 MACA 稳定性边界。
- `PROJ-OPENPIVLA-010`：smoke summary、formal report 与 raw log 的证据层级。
- `PROJ-OPENPIVLA-011`：checkpoint lineage manifest 如何设计。
- `PROJ-OPENPIVLA-012`：DROID `H=15/D=72` 的 shape 与 axis/unit 缺口如何追问。
