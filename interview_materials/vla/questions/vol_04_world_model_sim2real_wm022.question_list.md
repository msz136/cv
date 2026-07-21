# VOL 04 VLA-WM-022 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：MPC、CEM、MPPI、best-of-N、N/H/K、scorer、latency 与 evidence boundary

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-022 | L2 | P0 | MPC、CEM/MPPI 与 best-of-N trajectory selection 的共同点和差异是什么？ | PlaNet/World Model、Cosmos/WAM、WM-019/021；无本地 planner runtime、N/H sweep 或 selected-vs-unselected episodes，不做个人 planning claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 区分 MPC 闭环范式、CEM/MPPI proposal optimizer 与 best-of-N selector。
3. 说明 N/H/K、scorer、controller、latency、reset、denominator 与 model/scorer optimism。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[WM-022 Source Freeze](../sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.html) 与 [WM-022 Knowledge](../knowledge/vol_04_world_model_sim2real_wm022_mpc_cem_mppi_best_of_n.html)。
- 依赖缺口：planner runtime、checkpoint、N/H sweep、selected/unselected trajectory、latency trace 与 ownership artifact。
- 下一步只进行一次 `VLA-WM-022` 真实口述或补一个 planning artifact；不批量生成 WM-023..038。
