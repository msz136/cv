# VOL 08 CODE-VLA-007 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：PID update、output/i clamp、conditional integration、back-calculation、reset 与 VLA controller 边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-007 | L2 | P0 | 请实现离散 PID update，处理输出饱和、积分 anti-windup、reset 与测试。 | ROS 2 control、WPILib、Feedback Systems、VOL 01；无本地 PID/feedback/tuning artifact，不做项目闭环 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 `dt`、error sign、state、`u_unsat/u_sat`、output/i clamp、conditional integration、back-calculation、`Tt`、reset 与 action schema 边界。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-007 Source Freeze](../sources/vol_08_code007_pid_anti_windup_source_freeze.html) 与 [CODE-007 Knowledge](../knowledge/vol_08_code007_pid_anti_windup.html)。
- 依赖缺口：本地 PID 实现、8-probe runtime/whiteboard artifact、joint feedback、tuning log、matched controller comparison 与 ownership。
- 下一步只进行一次 `CODE-VLA-007` 白板/runtime 练习；不批量扩展 `CODE-VLA-008`，不创建 `coaching_state.md`。
