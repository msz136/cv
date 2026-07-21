# VOL 04 VLA-WM-032 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：geometry、appearance、sensor/time、scene/task、label contract、range、contamination、ADR/SimOpt 与 matched ablation

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-032 | L2 | P0 | visual/domain randomization 该随机化什么，怎样避免随机化到无关分布？ | Tobin/OpenAI/Tan/SimOpt/ADR primary papers + OpenCV + Audit D/WM-031/Evidence Manifest；无 local visual-DR/real-transfer bundle |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 能列出 geometry、appearance、sensor/time、scene/task 四组因子。
3. 区分 invariant/equivariant/semantic-changing，明确 point/pose/action/prompt 同步。
4. 用 target inventory、range evidence、validity、sample render、label round-trip、matched ablation 和 rollback 防止 irrelevant domain。
5. 正确说明 overwide、ADR 与 SimOpt 的能力边界，不把 sim/replay 写成 closed-loop transfer。
6. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-032 Source Freeze](../sources/vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html) 与 [WM-032 Knowledge](../knowledge/vol_04_world_model_sim2real_wm032_visual_domain_randomization_relevance.html)。
- 依赖缺口：local randomization manifest、factor/range source、sample/rejection ledger、label tests、matched arms、real calibration/replay/closed-loop 与 ownership。
- 下一 bounded slice 是 `VLA-WM-033` dynamics randomization 与 system identification；不批量生成 WM-033..038。
