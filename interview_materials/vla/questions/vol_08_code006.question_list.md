# VOL 08 CODE-VLA-006 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：二连杆 planar FK、frame/单位、矩阵链与 Jacobian 测试

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-006 | L2 | P0 | 请推导并实现 2-link planar forward kinematics，说明角度/坐标约定和测试。 | Modern Robotics、ROS REP-103、VOL 01/CODE-005；无本地 URDF/calibration/controller artifact，不做项目成功 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确相对 joint angle、解析式、齐次链、rad/deg、长度单位、tool offset、Jacobian 与 FK/IK 边界。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-006 Source Freeze](../sources/vol_08_code006_planar_fk_source_freeze.html) 与 [CODE-006 Knowledge](../knowledge/vol_08_code006_planar_fk.html)。
- 依赖缺口：真实 URDF/joint calibration、FK roundtrip、finite-difference Jacobian 和 controller 连接 artifact。
- 下一步只进行一次 `CODE-VLA-006` 白板/口述练习，或补一个 FK artifact；不批量扩展手撕题。
