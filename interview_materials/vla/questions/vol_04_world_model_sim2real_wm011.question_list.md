# VOL 04 VLA-WM-011 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-011 objective semantics；不提前展开 WM-012 RSSM / Dreamer posterior、prior、KL balancing 与 imagined rollout。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-011 | L2 | P0 | reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么？ | World Models/PlaNet/DreamerV3/Perceptual/LPIPS primary sources + frozen DreamerV3 reimplementation + WAM/UWM inventories；无 local objective ablation/uplift evidence |

## 覆盖合同

- objective：prediction、target、time index、mask、denominator、scale、gradient recipient；
- reconstruction：observation key/range/likelihood 与 posterior-shortcut 边界；
- dynamics：prior/posterior、dyn/rep stop-gradient、free nats 与 rollout；
- reward/continue：immediate reward、learned discount、terminal/timeout/off-by-one；
- perceptual：backbone/layer/normalization/frozen/domain 与 geometry/contact boundary；
- aggregation：raw/reduced/scaled loss、valid count、gradient diagnostics；
- evaluation：single-objective/combined/overwide matched arms 与 closed-loop evidence；
- project：WAM/UWM 机制理解和个人 objective uplift 严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-011 Source Freeze](../sources/vol_04_wm011_objective_semantics_source_freeze.html) 与 [WM-011 Knowledge](../knowledge/vol_04_world_model_sim2real_wm011_objective_semantics.html)。
- 下一 bounded slice 只做 `VLA-WM-012`：RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导。
