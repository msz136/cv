# VOL 04 VLA-WM-024 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：reward、value/Q、success predicate/classifier、termination/continuation、timeout/truncation

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-024 | L2 | P0 | reward model、value function、success classifier 与 termination predictor 如何区分？ | Dreamer/World Model、Cosmos/WAM、LIBERO/Cosmos protocol；无本地校准曲线或 paired candidate bundle，不做个人 value/success claim |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 区分 step reward、policy-conditioned V/Q、task success 与 episode termination。
3. 说明 continuation/terminal/truncation mask、success predicate revision、denominator 与 calibration。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-024 Source Freeze](../sources/vol_04_wm024_reward_value_success_termination_source_freeze.html) 与 [WM-024 Knowledge](../knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)。
- 依赖缺口：本地 reward/value/success/termination artifact、calibration、paired candidate outcome 与 ownership。
- 下一步只进行一次 VLA-WM-024 真实口述或补一个 value/success artifact；不批量生成 WM-025..038。
