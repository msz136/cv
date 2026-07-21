# VOL 06 PER-007 题卡清单

> 规划日期：2026-07-19  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Open-vocabulary detector/grounder、query–token matching、双阈值、phrase、geometry/NMS 与显式/生成式边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-007 | L2 | P0 | Grounding DINO 式 open-vocabulary grounding 如何从文本得到带 phrase 的框？box/text threshold 与 NMS 分别做什么？ | Grounding DINO v5、pinned official code、Transformers 4.57.1 与本地 OPD 生成式路径；无本地 detector checkpoint/raw logits、threshold calibration、NMS trace、closed-loop 或个人 ownership 证据 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 `Q×L` score、`L_max=256` token-axis、严格 `>` 双阈值、phrase reconstruction、coordinate inverse、optional NMS 与 Transformers API drift。
4. 区分 Grounding DINO 式显式 detector 与 OPD 生成式 tagged-coordinate pipeline，不把静态 grounding 升级为机器人结果或个人实现。
5. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[PER-007 Source Freeze](../sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html) 与 [PER-007 Knowledge](../knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.html)。
- 依赖缺口：本地 detector checkpoint/config、raw query–token logits、input IDs、threshold calibration、pre/post NMS trace、closed-loop 与候选人 ownership confirmation。
- `VLA-PER-007..008` source/knowledge/card已同步且保持`unseen`；PER-009 source已冻结，下一 bounded slice 只生成其knowledge，不生成card。
