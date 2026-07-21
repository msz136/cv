# VOL 04 VLA-WM-031 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：visual/sensor、dynamics/contact、control/timing、task/protocol、stochasticity 与 first-failure ladder

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-031 | L1 | P0 | Sim2Real reality gap 主要来自视觉、动力学、控制、任务与随机性哪些层？ | Tobin/Peng/Tan/OpenAI primary papers + MuJoCo/OpenCV/robosuite docs + Audit D/E + Evidence Manifest；无 protocol-complete local real-hardware bundle |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 能在 30 秒内列出五层及每层一个典型 mismatch。
3. 明确 contact 是 dynamics/control 的高风险交叉层，safety 是响应层。
4. 给出 protocol→real replay→action round-trip→free-space→contact→task→repeat 的 first-failure 顺序。
5. 不把 simulator、deployment entry 或公开论文结果写成个人 real-hardware transfer。
6. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-031 Source Freeze](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html) 与 [WM-031 Knowledge](../knowledge/vol_04_world_model_sim2real_wm031_reality_gap_taxonomy.html)。
- 依赖缺口：real camera calibration、robot/controller revision、paired sim/real init/trace、contact/safety events、episode denominator 与 ownership ledger。
- 下一 bounded slice 是 `VLA-WM-032` visual/domain randomization；不批量生成 WM-032..038。
