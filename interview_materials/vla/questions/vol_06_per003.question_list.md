# VOL 06 PER-003 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：多视角 / 时序 Grounding 与输入 Schema  
> 规则：固定 camera/frame identity、timestamp、K/T revision、presence mask、common-frame association 和 observation age；不把多路 camera 字段写成 fusion 或闭环收益。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-003 | L3 | P0 | 多相机、多帧输入为什么不能只是把图片 concat 后喂给模型？ | Open X/Octo/WM-017 机制 + OPD/WAM 项目边界；per-view calibration、sync、ablation、replay artifact 缺失 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问树、易错点、危险答案和来源。
3. 明确区分 schema、geometry、fusion、temporal replay 与 closed-loop evidence。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一批

- 前置：[PER-003 Source Freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html) 与 [PER-003 Knowledge](../knowledge/vol_06_per003_multiview_temporal.html)。
- 依赖缺口：per-view calibration/sync、common-frame roundtrip、view ablation、frame-drop/jitter replay、causal-mask audit 与 ownership ledger。
- 下一批先进行 PER-001..003 真实口述或补一个 multi-view artifact，再决定是否进入 PER-004 VLN/ObjectNav。
