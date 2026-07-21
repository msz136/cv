# VOL 08 CODE-VLA-005 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：SE(3) composition、frame 方向、point/vector/pose、inverse 与 roundtrip

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-005 | L2 | P0 | 请解释并手写 4×4 homogeneous transform composition，说明 frame 方向、逆变换和测试。 | ROS REP-103/105、SciPy Rotation 与 PER-002；无本地 TF/calibration parity，不做项目 3D/闭环 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 `T^A_B` 方向、右到左 composition、rigid inverse、w=1/0、frame/单位/时间戳与 roundtrip。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-005 Source Freeze](../sources/vol_08_code005_transform_source_freeze.html) 与 [CODE-005 Knowledge](../knowledge/vol_08_code005_transform.html)。
- 依赖缺口：真实手写实现、TF/calibration roundtrip、unit/frame mismatch 和 controller 连接 artifact。
- 下一步只进行一次 `CODE-VLA-005` 白板/口述练习，或补一个 roundtrip artifact；不批量扩展手撕题。
