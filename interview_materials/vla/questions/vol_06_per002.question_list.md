# VOL 06 PER-002 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：2D Grounding → 3D Lift、相机标定与 Frame Contract  
> 规则：必须绑定 depth、`K/distortion/image_size`、frame ID、timestamp、单位和 uncertainty；不把 3D geometry 直接写成 controller success。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-002 | L3 | P0 | 一个 grounding point 怎样才能安全地进入 planner 或 controller？ | OpenCV/ROS 机制 + OPD/WAM 项目缺口；3D roundtrip、TF、planner/controller artifact 未闭合 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问树、易错点、危险答案和来源。
3. 明确区分 projection math、calibration、frame transform、planner interface 与 closed-loop episode。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一批

- 前置：[PER-002 Source Freeze](../sources/vol_06_per002_3d_lift_frame_source_freeze.html) 与 [PER-002 Knowledge](../knowledge/vol_06_per002_3d_lift_frame.html)。
- 依赖缺口：真实 calibration/depth/TF bundle、pixel↔camera↔target roundtrip、uncertainty/invalid trace、planner/controller trace 和 ownership ledger。
- 下一批先进行 PER-001/PER-002 口述或补一个 3D artifact，再决定是否进入 PER-003 多视角/时序融合。
