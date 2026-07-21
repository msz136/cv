# VOL 06 PER-016 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：tracking/odometry/localization/mapping/SLAM、typed sensor/state/map manifest、REP-105 map/odom、VIO state/covariance、preintegration、front/back end、loop/relocal/map merge、drift、ATE/RPE、diagnosis与五项目真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-016 | L3 | P1 | 机器人怎样定位自己？Odometry、Localization和SLAM如何区分，map/odom、loop closure、drift与ATE/RPE怎样讲？ | 六份完整primary PDF、六个fixed official repositories/36文件、REP-105、10个deterministic probes、五份inventory及Robot Harness六个local-direct exceptions；无本地sensor bag、estimator config/checkpoint、live TF/pose/covariance、pose graph/loop logs、ATE/RPE bundle、matched robot episode或候选人ownership闭环 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. tracking、odometry、localization、mapping与SLAM按输入、state、map假设与failure分开，不用“都有pose”合并。
4. `map→odom→base`区分global consistency与local continuity；global correction不直接伪造local motion。
5. state/covariance propagation、measurement update、preintegration与front/local/backend/global责任边界保留。
6. loop candidate经过geometric verification、relative transform、robust pose-graph residual与map revision gate；relocalization、loop closure和map merge分开。
7. drift按translation/yaw/scale/vertical/time/map corruption/lost/jump分类，并按first-divergence诊断。
8. ATE/RPE冻结timestamp association、SE3/Sim3 alignment、delta、unit与failure denominator；Sim3不证明metric scale。
9. OPD、Robot Harness、OpenPiVLA、WAM、UWM只映射到有证据的upstream、map asset或interface hook，不升级为本地SLAM、robot result或个人ownership。
10. 30秒答案≤180字符，机制展开≤350字符；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-016 Source Freeze](../sources/vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html) 与 [PER-016 Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.html)。
- 依赖缺口：sensor/map/estimator typed manifest、raw packet/TF/state/covariance/graph/loop logs、SE3/Sim3 trajectory evaluation、matched planner/controller episodes与逐文件候选人ownership确认。
- `VLA-PER-016` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只冻结`VLA-PER-017` belief/memory/frontier/active-exploration source，不生成knowledge/card。
