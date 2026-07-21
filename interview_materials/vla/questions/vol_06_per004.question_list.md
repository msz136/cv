# VOL 06 PER-004 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：VLN / ObjectNav 任务、观测与成功协议  
> 规则：先拆 VLN、ObjectNav、REVERIE 的 goal contract，再冻结 episode、stop、success、SPL 和 simulator-to-real 证据边界。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-004 | L3 | P0 | VLN、ObjectNav 和 REVERIE 的 success/SPL 协议怎样拆，为什么不能只报一个成功率？ | Habitat-Lab/Habitat-Sim/VLN-CE、R2R/REVERIE/ObjectNav/SPL 机制；无本地 VLN/ObjectNav run bundle，不做个人导航 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问树、易错点、危险答案和来源。
3. 明确区分 task contract、episode/observation/action、success/SPL、simulator 与 real closed-loop evidence。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[PER-004 Source Freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html) 与 [PER-004 Knowledge](../knowledge/vol_06_per004_vln_objectnav.html)。
- 依赖缺口：本地 benchmark episode manifest、scene/navmesh revision、action trace、success predicate、denominator、failure traces 与 real-navigation log。
- 下一步只进行一次 `VLA-PER-004` 真实口述，或补一个本地导航 artifact；不并行扩展 VOL 06 其他题卡。
