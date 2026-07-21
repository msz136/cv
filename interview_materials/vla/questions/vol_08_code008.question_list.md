# VOL 08 CODE-VLA-008 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_synced / card_drafted / WARN`  
> 题数：1  
> 节点：Bellman TD(0)、terminated/truncated、timeout bootstrap、target detach、valid reduction 与 batch 对齐

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-008 | L2 | P0 | 请实现 Bellman TD(0) update，区分 terminated/truncated，并处理 target、mask 与 batch edge cases。 | Sutton–Barto、Gymnasium、VOL 01/VOL 02 fact review；无本地 TD learner、replay/gradient artifact 或 candidate ownership，不做 value/机器人收益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 `terminated`、`truncated`、`success`、`valid`、`obs_tp1`、target detach、batch shape 与 distributed denominator 边界。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-008 Source Freeze](../sources/vol_08_code008_bellman_td0_source_freeze.html) 与 [CODE-008 Knowledge](../knowledge/vol_08_code008_bellman_td0.html)。
- 依赖缺口：本地 TD implementation、transition/replay bundle、gradient parity、target revision、8-probe runtime/whiteboard artifact 与 ownership。
- 下一步只进行一次 `CODE-VLA-008` 白板/runtime 练习；不启动 `SYS-VLA-004`，不创建 `coaching_state.md`。

