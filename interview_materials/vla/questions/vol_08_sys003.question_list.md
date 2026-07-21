# VOL 08 SYS-003 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Robot fleet、multi-tenant GPU scheduling、fairness、lease 与 rollout/cost

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| SYS-VLA-003 | L3 | P1 | 当机器人、租户、模型 revision 和异构 GPU 同时增长时，如何设计 fleet scheduler，并保证公平、freshness 与安全边界？ | Kubernetes/Volcano/NVIDIA/Triton/Ray/ROS 2 mechanisms、五项目局部 inventory/ledger；缺统一 fleet control plane、multi-tenant load/fairness A/B、lease fencing、controller ack、cache/checkpoint lineage 时不称 production fleet 或个人 ownership |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 capacity、fairness、priority、freshness，以及上游机制与本地项目证据。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[SYS-003 Source Freeze](../sources/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling_source_freeze.html) 与 [SYS-003 Knowledge](../knowledge/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling.html)。
- 训练前缺口：tenant/robot/model/request/placement trace、GPU placement/fairness A/B、lease epoch fencing、controller acknowledgement、cache/checkpoint lineage 与 candidate role confirmation。
- 下一步只进行一次 `SYS-VLA-003` 真实口述；未取得回答前不改变 `unseen`，不创建 `coaching_state.md`，不启动 `SYS-VLA-004`。
