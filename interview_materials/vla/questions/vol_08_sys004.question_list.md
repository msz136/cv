# VOL 08 SYS-004 题卡清单

> 规划日期：2026-07-21  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：fault recovery、safety、observability、first divergence、rollback/replay

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| SYS-VLA-004 | L3 | P0 | policy、controller、robot 或数据链路异常时，如何定位 first divergence、降级恢复并防止 stale action 造成物理风险？ | ROS 2/Kubernetes/OpenTelemetry mechanisms、五项目局部 inventory/ledger；缺 supervisor、controller ack、fault-injection、immutable replay 与 rollback compatibility 时不称生产安全闭环或个人 ownership |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 first divergence、root cause、recovery outcome，以及 hold/stop/e-stop 的 owner 边界。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[SYS-004 Source Freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html) 与 [SYS-004 Knowledge](../knowledge/vol_08_sys004_fault_recovery_safety_observability.html)。
- 训练前缺口：first-divergence trace、fault-injection matrix、controller acknowledgement、lease fencing、rollback compatibility、immutable replay 与 candidate role confirmation。
- 下一步只进行一次 `SYS-VLA-004` 系统设计真实口述；未取得回答前不改变 `unseen`，不创建 `coaching_state.md`，不启动其它 VOL 08 节点。
