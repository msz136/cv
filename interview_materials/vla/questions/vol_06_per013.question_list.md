# VOL 06 PER-013 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：typed 3D manifest、PointNet++ sampling/grouping、voxel/VFE、sparse convolution、pillar/BEV、explicit/octree/implicit occupancy、diagnostic与Robot Harness map/PCD真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-013 | L3 | P1 | 点云、voxel、BEV和occupancy怎样选？sampling、量化与unknown语义如何影响下游？ | 六篇完整primary PDF、六个fixed official repositories、九个deterministic probes与Robot Harness map/PCD/bridge direct evidence；无本地3D encoder/config/checkpoint、online ingest、matched representation benefit、planner/controller episode、robot result或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. PointNet++保留FPS start/seed、ball/kNN radius/K、density与input-order边界，不把permutation invariance扩大到完整pipeline。
4. voxel量化绑定frame/origin/range/axis/resolution/floor，并解释boundary、collision、cap/drop与aggregation alias。
5. 区分MeanVFE与learned VFE，区分SubM/Sparse/Inverse convolution，不声称sparse总是更快或更省。
6. 区分pillar z spatial bin、per-point z feature与HeightCompression的D→channel。
7. BEV fusion绑定intrinsics/extrinsics、pose、augmentation、grid与time；同shape不等于同物理平面。
8. 区分explicit grid、OctoMap log-odds和implicit occupancy；unknown不等于observed free，threshold不等于collision safety。
9. 本地Robot Harness只讲2D tri-state map、PCD schema与path/URL bridge，不升级为个人3D perception或robot result。
10. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-013 Source Freeze](../sources/vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html) 与 [PER-013 Knowledge](../knowledge/vol_06_per013_pointcloud_voxel_bev_occupancy.html)。
- 依赖缺口：本地point-cloud ingest、frame/time manifest、voxel/pillar/BEV/occupancy config与checkpoint、raw tensor、matched ablation、planner/controller episode、robot result及候选人ownership确认。
- `VLA-PER-013` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只冻结`VLA-PER-014` 3D semantic/open-vocabulary grounding source，不生成knowledge/card。
