# VOL 04 VLA-WM-020 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：posterior collapse、action ignoring、future leakage、background shortcut 与诊断矩阵

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-020 | L3 | P1 | 怎样发现 posterior collapse、action ignoring、future leakage 与 background shortcut？ | DreamerV3/World Model/ACT/causal-temporal audits；无本地 latent/action/future/background probe，不做项目 failure claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 分开 representation、intervention、time visibility、domain invariance 四层 failure。
3. 包含 posterior/prior、latent ablation、action swap/sweep、future removal/mask、background holdout 与 counterfactual。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[WM-020 Source Freeze](../sources/vol_04_wm020_failure_diagnostics_source_freeze.html) 与 [WM-020 Knowledge](../knowledge/vol_04_world_model_sim2real_wm020_failure_diagnostics.html)。
- 依赖缺口：latent-usage log、action-swap trace、future-removal replay、background-domain holdout 与项目 ownership artifact。
- 下一步只进行一次 `VLA-WM-020` 真实口述或补一个诊断 artifact；不批量生成 WM-021..038。
