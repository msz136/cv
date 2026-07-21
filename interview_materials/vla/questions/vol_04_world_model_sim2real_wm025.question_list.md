# VOL 04 VLA-WM-025 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：Cosmos/WAM action/future/value slot、routing、condition mask、target mask、EDM loss

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-025 | L3 | P0 | Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？ | Cosmos paper/repo audit、WM-016、WAM inventory；无 exact local config/checkpoint/gradient/paired result，不做个人设计或增益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 能从 probability role 讲到 slot layout 和 action/future/value 注入。
3. 区分 sample routing、condition mask、target loss mask、metric 与 main EDM loss。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-025 Source Freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html) 与 [WM-025 Knowledge](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)。
- 依赖缺口：exact local config、checkpoint、role×slot trace、gradient、paired ablation 与 ownership。
- 下一步只进行一次 VLA-WM-025 真实口述或补一个 slot/mask artifact；不批量生成 WM-026..038。
