# VOL 08 SYS-002 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Policy serving、实时控制环、chunk/replan、deadline/backpressure 与 safety boundary

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| SYS-VLA-002 | L3 | P0 | 如何把 VLA policy 接入实时控制环，并区分 WebSocket demo、soft-real-time service 与物理安全边界？ | OpenPI frozen server/client/broker/examples、CPython/Triton/gRPC/ROS 2 机制与五项目局部 evidence；缺统一服务、E2E trace、load/fault test、controller ack、watchdog/e-stop 时不称 production/hard-real-time/个人端到端 ownership |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 OpenPI direct facts、系统设计 inference、local evidence 与 unsupported personal claims。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[SYS-002 Source Freeze](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html) 与 [SYS-002 Knowledge](../knowledge/vol_08_sys002_policy_serving_realtime_control_loop.html)。
- 训练前缺口：request-ID + capture→apply trace、queue/fault injection、controller acknowledgement、watchdog/e-stop 与候选人真实 ownership confirmation。
- 下一步只进行一次 `SYS-VLA-002` 真实口述；未取得回答前不改变 `unseen`，不创建 `coaching_state.md`，不启动 `SYS-VLA-003`。
