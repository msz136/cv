# VOL 04 VLA-WM-013 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-013 latent overshooting / multi-step consistency；不提前展开 WM-014 causal/action intervention。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-013 | L3 | P1 | latent overshooting 或 multi-step consistency loss 解决什么，可能带来什么偏差？ | PlaNet primary paper + `google-research/planet@c04226b` official implementation/config + WAM/UWM inventories；无 local overshooting config/per-distance trace/matched uplift |

## 覆盖合同

- problem：一步gradient distance与有限容量多步最优；
- objective：posterior start、d-step prior、future posterior target、KL；
- implementation：shifted previous action、use_obs=false、mask、stop-gradient、free-nats；
- weighting：D、β_d、per-distance valid count与denominator；
- bias：target shortcut、多模态family、collapse、compute、reset/terminal；
- provenance：PlaNet提出/可选实现与final/default未启用并列；
- boundary：PlaNet与DreamerV3、WAM、UWM严格分开；
- evaluation：D/β/gradient/capacity matched arms与closed-loop证据。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-013 Source Freeze](../sources/vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html) 与 [WM-013 Knowledge](../knowledge/vol_04_world_model_sim2real_wm013_latent_overshooting_multistep_consistency.html)。
- 下一 bounded slice 只做 `VLA-WM-014`：action-conditioned prediction 怎样区分相关性预测与可干预 dynamics。
