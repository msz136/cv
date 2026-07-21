# VOL 04 VLA-WM-012 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-012 RSSM / Dreamer posterior、prior、KL balancing 与 imagined rollout；不提前展开 WM-013 latent overshooting / multi-step consistency。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-012 | L3 | P0 | RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导？ | PlaNet/DreamerV1/V2/V3 primary sources + frozen DreamerV3 reimplementation + WAM/UWM inventories；无 local Dreamer checkpoint/RSSM implementation/paired rollout evidence |

## 覆盖合同

- state：deterministic \(h_t\)、stochastic \(z_t\)、previous action 与 current observation；
- factorization：action-conditioned generative model 与 filtering posterior；
- ELBO：prediction likelihood − prior/posterior KL；
- balancing：KL 双重职责、V2 α、V3 dyn/rep/free bits/scale；
- code：reset→core→posterior、starts→policy→core→prior→sample；
- leakage：future observation removal、action off-by-one、reset/padding；
- diagnostics：raw/clipped KL、entropy/usage、gradient、action sensitivity、horizon curve；
- project：Dreamer/RSSM 与 WAM/UWM diffusion contract 严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-012 Source Freeze](../sources/vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html) 与 [WM-012 Knowledge](../knowledge/vol_04_world_model_sim2real_wm012_rssm_dreamer_posterior_prior_kl_imagination.html)。
- 下一 bounded slice 只做 `VLA-WM-013`：latent overshooting 或 multi-step consistency loss 解决什么、可能带来什么偏差。
