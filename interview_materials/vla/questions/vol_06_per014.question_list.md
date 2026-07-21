# VOL 06 PER-014 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：六类3D grounding输出、candidate hard upper bound、spatial relation frame/arity、open-vocabulary score/metric、first-divergence diagnosis与五项目真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-014 | L3 | P1 | 3D grounding有哪些输出？candidate、spatial relation、open-vocabulary score和metric该怎样冻结？ | 六篇完整primary PDF、六个fixed official repositories/36文件、九个deterministic probes、五份inventory及OPD/Robot Harness direct exceptions；无本地3D semantic head/map/checkpoint、raw query/proposal oracle、same-protocol metric、robot episode或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 区分3D box、candidate ID、point semantics、instance mask、continuous field与semantic map，不用“CLIP投点云”合并六类输出。
4. 区分ScanRefer raw-scene proposal/box链与ReferIt3D segmented-object listener，保留target-present/proposal oracle硬上界。
5. point semantic不升级为instance identity；OpenMask3D保留mask proposal、view、SAM crop、CLIP与aggregation边界。
6. spatial relation冻结target/anchors、arity、observer/world/object frame、axis和tolerance；between为三元关系。
7. dot、cosine、positive-vs-negative relative probability分开；冻结encoder/prompt/negative/normalization/temperature/threshold/unknown。
8. proposal recall、Acc@IoU、top-1、semantic mIoU、instance AP、field/map localization不可互换，更不等于robot success。
9. 本地OPD只讲2D image relation/point-box supervision，Robot Harness只讲2D occupancy/non-semantic PCD/bridge；其余三项目不升级为local 3D grounding。
10. 30秒答案≤180字符，机制展开≤350字符；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-014 Source Freeze](../sources/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html) 与 [PER-014 Knowledge](../knowledge/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.html)。
- 依赖缺口：typed 3D candidate/scene manifest、frame/pose/depth lineage、semantic/instance fields、query service、model/config/checkpoint、raw scores、proposal oracle、same-protocol metric、controller episode与候选人ownership确认。
- `VLA-PER-014` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只冻结`VLA-PER-015` perception→action/reachability/uncertainty/failure-gate source，不生成knowledge/card。
