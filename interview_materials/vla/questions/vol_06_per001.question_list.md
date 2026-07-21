# VOL 06 PER-001 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Point / Box / Text Grounding 与坐标协议  
> 规则：固定 representation、coordinate space、parser、transform、scorer 和 downstream boundary；不把 static grounding metric 写成 action/robot success。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-001 | L3 | P0 | 为什么 grounding 面试必须先讲 coordinate contract，而不能只报 IoU 或 point hit？ | Grounding DINO/RoboPoint 机制 + OPD local evidence；3D lift、controller roundtrip 与真实闭环仍缺 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问树、易错点、危险答案和来源。
3. 明确区分 normalized `cxcywh`、pixel `xyxy`、point/text parser，以及 original strict、protocol-fixed strict、lenient geometry。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一批

- 前置：[PER-001 Source Freeze](../sources/vol_06_per001_grounding_coordinate_source_freeze.html) 与 [PER-001 Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html)。
- 依赖缺口：真实 parser/normalizer/controller roundtrip、3D depth/extrinsic、multi-view fusion、逐文件 ownership。
- 下一批只在完成一次口述或补齐一个 perception artifact 后，再进入 PER-002 3D lift；不批量生成 VOL 06。
