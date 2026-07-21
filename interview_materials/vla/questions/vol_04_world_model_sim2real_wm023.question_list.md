# VOL 04 VLA-WM-023 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：open-loop、receding horizon、\(H/K\)、observation age、latency、queue 与扰动恢复

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-023 | L2 | P0 | open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？ | PlaNet、Diffusion Policy、ACT、Cosmos/WAM audit；无本地 planning runtime、\(H/K\) paired sweep 或扰动 bundle，不做个人 latency/robustness claim |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 区分 prediction/planning horizon \(H\) 与 execution horizon \(K\)，解释 observation age。
3. 覆盖同步、异步、event-trigger replan、queue underflow、controller、reset、normalizer 与 denominator。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-023 Source Freeze](../sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.html) 与 [WM-023 Knowledge](../knowledge/vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)。
- 依赖缺口：本地 planning runtime、同 checkpoint 的 \(H/K\) 曲线、latency trace、扰动 episode 与 ownership artifact。
- 下一步只进行一次 VLA-WM-023 真实口述或补一个 horizon/latency artifact；不批量生成 WM-024..038。

