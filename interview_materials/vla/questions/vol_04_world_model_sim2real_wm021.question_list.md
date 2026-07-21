# VOL 04 VLA-WM-021 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Dreamer latent imagination、actor/critic、lambda-return、gradient routing 与 model bias

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-021 | L3 | P0 | Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？ | DreamerV3 paper/reimplementation、World Model audit、WM-019 metric boundary；无本地 Dreamer checkpoint/paired rollout，不做项目收益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 说明 replay posterior 起点、prior imagination、reward/continue、actor/critic 与 lambda-return。
3. 说明 stop-gradient/gradient routing、model bias、OOD exploitation 与 imagined/sim/real 分层。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[WM-021 Source Freeze](../sources/vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html) 与 [WM-021 Knowledge](../knowledge/vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.html)。
- 依赖缺口：checkpoint、imagined/real paired trace、horizon sweep、value calibration 与 ownership artifact。
- 下一步只进行一次 `VLA-WM-021` 真实口述或补一个 paired artifact；不批量生成 WM-022..038。
