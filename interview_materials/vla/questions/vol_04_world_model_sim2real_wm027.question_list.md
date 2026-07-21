# VOL 04 VLA-WM-027 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：negative transfer、layer/role gradient audit、PCGrad、GradNorm、matched closed-loop

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-027 | L3 | P1 | 什么时候 auxiliary world/value 会负迁移，如何识别 gradient conflict？ | PCGrad/GradNorm 一手论文 + official PCGrad code + WM-025/026 + WAM inventory；无本地 gradient trace、matched ablation 或修复结果 |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 明确 negative transfer 是 matched outcome，negative cosine 是局部诊断。
3. 给出 layer/role cosine、norm ratio、joint alignment、AMP/DDP 与 exact loss 边界。
4. 正确区分 PCGrad 的方向投影和 GradNorm 的尺度/训练速率平衡。
5. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-027 Source Freeze](../sources/vol_04_wm027_auxiliary_negative_transfer_gradient_conflict_source_freeze.html) 与 [WM-027 Knowledge](../knowledge/vol_04_world_model_sim2real_wm027_auxiliary_negative_transfer_gradient_conflict.html)。
- 依赖缺口：local exact config/checkpoint、per-role gradient、matched objective arms、multi-seed episodes 与 ownership。
- 下一 bounded slice 是 `VLA-WM-028` 的 routing/slot-mask/loss-weight contract；不批量生成 WM-028..038。

