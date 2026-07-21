# VOL 04 VLA-WM-026 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：world/value auxiliary、shared representation、gradient alignment、matched ablation、negative transfer

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-026 | L2 | P0 | world/value auxiliary objective 为什么可能帮助 action imitation？ | Cosmos/WAM、WM-025/016、UWM、WAM inventory；无本地 paired experiment/gradient/episode，不做已验证增益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 说明 action consequence、task progress、data coverage 与 gradient alignment。
3. 给出 action-only/+world/+value/all、shuffled-label、stop-gradient 和 matched data/compute protocol。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-026 Source Freeze](../sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html) 与 [WM-026 Knowledge](../knowledge/vol_04_world_model_sim2real_wm026_world_value_auxiliary_action_imitation.html)。
- 依赖缺口：local config/checkpoint、gradient alignment、matched objective metric、episode trace 与 ownership。
- 下一步只进行一次 VLA-WM-026 真实口述或补一个 auxiliary ablation artifact；不批量生成 WM-027..038。
