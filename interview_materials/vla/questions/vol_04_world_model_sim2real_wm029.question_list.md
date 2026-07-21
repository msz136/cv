# VOL 04 VLA-WM-029 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：imagined/OOD value、calibration、ranking、uncertainty、LCB/MOPO/CQL

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-029 | L3 | P1 | value 在 imagined/OOD state 上为何容易失准，如何做 calibration 或 pessimism？ | Calibration/PETS/MOPO/CQL primary papers + Cosmos exact scorer + WM-024/028 + WAM inventory；无本地 value/planning artifacts |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 分开 support shift、world bias、value extrapolation、horizon 与 best-of-N selection bias。
3. 区分 calibration、ranking、uncertainty 与 accuracy。
4. 正确说明 LCB、MOPO、CQL 的干预层级和 frozen Cosmos heuristic/default 边界。
5. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-029 Source Freeze](../sources/vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html) 与 [WM-029 Knowledge](../knowledge/vol_04_world_model_sim2real_wm029_imagined_ood_value_calibration_pessimism.html)。
- 依赖缺口：local value labels/predictions、pre/post-clip samples、candidate ledger、selector sweep、planning episodes 与 ownership。
- 下一 bounded slice 是 `VLA-WM-030` planning N/world/value/communication/latency budget；不批量生成 WM-030..038。

