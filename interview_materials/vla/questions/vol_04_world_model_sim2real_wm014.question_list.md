# VOL 04 VLA-WM-014 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖WM-014 action-conditioned observational correlation与interventional dynamics；本题完成后VOL 04 knowledge/card为44/44。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-014 | L3 | P0 | action-conditioned prediction怎样区分相关性预测与可干预dynamics？ | Action-conditional/Causal Confusion/WCS/CausalWorld/CDL primary sources + frozen author/official code + WAM/UWM inventories；无local cloned-state effect/real intervention evidence |

## 覆盖合同

- query：\(p(y|x,a)\) vs \(p(y|x,do(a))\)；
- identification：state/history sufficiency、overlap、consistency、temporal order；
- execution：raw→denorm→shield/controller→measured action；
- ladder：syntax、sensitivity、observational、sim intervention、cross-policy、real、closed-loop；
- metric：conditional effect与predicted-vs-environment effect delta；
- test：snapshot/seed/action pair、shuffle/zero/axis/scale/nuisance；
- safety：real matched repeats、small perturbation、gate/fallback/CI；
- project：WAM/UWM coupling与personal causal evidence严格分开。

## 状态与下一入口

- 本题保持`unseen`；没有候选人口述，不创建`coaching_state.md`。
- 前置：[WM-014 Source Freeze](../sources/vol_04_wm014_action_conditioned_correlation_intervention_source_freeze.html) 与 [WM-014 Knowledge](../knowledge/vol_04_world_model_sim2real_wm014_action_conditioned_correlation_intervention.html)。
- VOL 04 knowledge/card达到44/44；下一步由全局缺口审计选择其他卷的首个source-ready节点。
