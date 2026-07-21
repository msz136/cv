# VOL 06 PER-010 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：strict/lenient parser、typed validity、IoU/Acc/RefExp/COCO、PCK/mask-hit/fixed-distance Hit、invalid denominator、protocol comparability与本地OPD证据边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-010 | L2 | P0 | Grounding评估时，strict parser、IoU/PCK/Recall和protocol comparability该怎么讲？为什么本地OPD的Hit@50/100不能直接叫PCK？ | MDETR/COCO API/RoboPoint/MMPose固定版本与本地OPD evaluator/inventory；无raw predictions、exact checkpoint hashes、parser-v2 paired rerun、robot result或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 分开tag、syntax、coordinate与geometry，并保持strict主口径、lenient diagnostic双轨。
4. 区分IoU/Acc、RefExp R@k、COCO AP/AR、PCK、mask-hit与fixed-coordinate any-pair Hit。
5. 冻结matching、invalid/empty/duplicate、字段分母、micro/macro与protocol identity。
6. 保留MDETR paper/code的IoU/GIoU discrepancy，不凭指标名或打印名推断protocol。
7. 本地OPD只讲scorer代码、10k inventory与三口径reconciliation，不升级为标准PCK、robot success、单因素因果或个人ownership。
8. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-010 Source Freeze](../sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.html) 与 [PER-010 Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.html)。
- 依赖缺口：raw predictions、sample/image/gold hashes、exact checkpoint/generation config、strict parser v2 golden tests与paired rerun、representation-stratified denominator、controller/episode bundle及候选人ownership confirmation。
- `VLA-PER-010` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只做`VLA-PER-011` pseudo-label/teacher-noise source freeze，不生成knowledge/card。
