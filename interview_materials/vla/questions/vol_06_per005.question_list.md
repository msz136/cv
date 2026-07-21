# VOL 06 PER-005 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Navigation policy architecture、semantic exploration、waypoint 与 planner/controller latency contract

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-005 | L3 | P0 | map-free、map-based、waypoint policy 如何比较？planner/controller 接口和 latency 要冻结哪些字段？ | GOSE、VLN-CE waypoint、Habitat-Lab/SIM 的公开机制；当前无本地 map/subgoal/action/episode bundle，不做个人导航 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 policy/memory、waypoint/subgoal、planner/controller、stop/replan、latency 与 evidence boundary。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[PER-005 Source Freeze](../sources/vol_06_per005_navigation_policy_architecture_source_freeze.html) 与 [PER-005 Knowledge](../knowledge/vol_06_per005_navigation_policy_architecture.html)。
- 依赖缺口：本地 map snapshot、subgoal/action trace、planner/controller log、episode denominator 与 real-navigation safety artifact。
- 下一步只进行一次 `VLA-PER-005` 真实口述，或补一个本地 navigation artifact；不并行扩展 VOL 06 其他题卡。
