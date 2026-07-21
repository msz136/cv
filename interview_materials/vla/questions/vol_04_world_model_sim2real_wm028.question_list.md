# VOL 04 VLA-WM-028 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：sample routing、condition/target/valid/metric mask、effective weight、reduction

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-028 | L3 | P0 | sample routing、slot mask 与 loss weight 怎样避免 action/world/value 互相污染？ | Cosmos paper + official commit exact code + WM-025/027 + WAM inventory；valid mask/per-role normalization 为推荐设计，无本地执行/收益 |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 区分 admission、routing、condition、target、valid、metric、weight/reduction。
3. 说明 effective weight 受 sampling、active slot、noise weight、multiplier 和 denominator 共同影响。
4. 准确说明 frozen defaults、full-tensor mean 与 value-mask flag WARN。
5. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-028 Source Freeze](../sources/vol_04_wm028_routing_slot_mask_loss_weight_source_freeze.html) 与 [WM-028 Knowledge](../knowledge/vol_04_world_model_sim2real_wm028_routing_slot_mask_loss_weight.html)。
- 依赖缺口：local resolved config、role/mask dump、numerator/denominator、gradient share、matched episodes 与 ownership。
- 下一 bounded slice 是 `VLA-WM-029` imagined/OOD value calibration 与 pessimism；不批量生成 WM-029..038。

