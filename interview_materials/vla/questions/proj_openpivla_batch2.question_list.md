# PROJ-OPENPIVLA 题卡清单（Direct-Evidence Batch 2）

> 规划日期：2026-07-17  
> 状态：`source_frozen / batch_2_drafted / WARN`；证据审计：[`openpivla_batch2_evidence_freeze.review.json`](../sources/openpivla_batch2_evidence_freeze.review.json)  
> 题数：4  
> 项目：OpenPI / OpenPiVLA / Qwen3-VL / MACA-C500  
> 规则：`eager` 只作为兼容性证据；smoke、formal report、raw log/checkpoint 分层；`H=15,D=72` 与 formal `limit=16` 的冲突必须显式保留。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| PROJ-OPENPIVLA-009 | L2 | P0 | 为什么 local formal trainer 默认使用 eager attention？ | local-direct call graph；无 profiler/uplift |
| PROJ-OPENPIVLA-010 | L2 | P0 | smoke summary、formal report 和 raw log/checkpoint 的证据等级有什么区别？ | smoke local-direct；formal report-supported；raw lineage missing |
| PROJ-OPENPIVLA-011 | L3 | P1 | 如何设计一份可审计的 OpenPiVLA checkpoint lineage manifest？ | manifest 设计稿；实际 hash/load evidence missing |
| PROJ-OPENPIVLA-012 | L3 | P0 | `H=15,D=72` 与 formal formatter 的 `limit=16` 冲突时，应该怎样解释？ | recipe/smoke vs formal representation conflict |

## 2. 题卡退出条件

1. 4 个 ID 全局唯一，均保持 `unseen`。
2. 每题包含短答案、机制展开、诊断/证据、项目挂钩、追问树、危险答案和来源。
3. 每题明确区分 local-direct、report-supported、remote-referenced、archive-summary-only 或 unverified。
4. 不把 eager 写成性能 uplift，不把 smoke shape 写成 controller 语义，不把历史 `flow_matching_loss` 与 current `outputs.loss` 合并。
5. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠且 review verdict 保持 `WARN`。

## 3. 依赖与下一批

- 前置证据：[Batch 2 evidence freeze](../sources/openpivla_batch2_evidence_freeze.html)。
- 依赖缺口：immutable formal logs、checkpoint/processor SHA、load smoke、DROID sentinel、parser、normalizer、axis/unit/controller roundtrip。
- 本批完成后再转 Robot Harness；不在同一增量生成其他项目题卡。

