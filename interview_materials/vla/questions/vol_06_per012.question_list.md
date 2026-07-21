# VOL 06 PER-012 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：task-typed segmentation、relative/metric depth、registered 3D surface、semantic keypoint、primitive-conditioned affordance、planner/controller gate与本地OPD point-only真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-012 | L3 | P1 | 如何把segmentation、depth、keypoint与affordance串成机器人可用的操作目标？为什么单模块高分不等于robot success？ | Mask2Former/SAM/Depth Anything V2/kPAM/Where2Act固定来源与本地OPD五文件audit；无本地dense checkpoint、metric-depth/camera bundle、3D keypoint/affordance raw output、planner/controller episode、robot result或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 区分semantic、instance、panoptic与promptable segmentation，不把任意mask默认成category+instance。
4. 区分relative、metric、sensor与aligned-relative depth；只有unit/range/validity/camera/time齐全的metric path可进入3D lift。
5. 说明Mask2Former task-specific postprocess/metric、SAM multimask/quality边界与Depth Anything V2 relative/metric独立代码和checkpoint。
6. semantic keypoint保留ID、visibility、covariance与frame；affordance保留point、orientation、primitive、state与score semantics。
7. proposal必须经过reachability、IK、collision、controller和episode gate；单模块metric不等于robot success。
8. 本地OPD只讲affordance-labelled point supervision，不升级为dense perception stack、3D/robot结果或个人ownership。
9. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-012 Source Freeze](../sources/vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html) 与 [PER-012 Knowledge](../knowledge/vol_06_per012_segmentation_depth_keypoint_affordance.html)。
- 依赖缺口：本地model/checkpoint/license、preprocess/raw dense output、metric-depth/intrinsics/registration/TF/time bundle、semantic keypoint covariance、primitive/state/orientation score、planner rejection、episode trace与候选人ownership确认。
- `VLA-PER-012` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只做`VLA-PER-013` point-cloud/voxel/BEV/occupancy representation source freeze，不生成knowledge/card。
