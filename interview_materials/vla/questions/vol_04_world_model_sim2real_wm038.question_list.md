# VOL 04 VLA-WM-038 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-038 uncertainty/safety/fallback/recovery；不重复展开已完成的 WM-039..044。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-038 | L3 | P0 | uncertainty-aware planning、安全约束、fallback 和 recovery policy 如何形成最小闭环？ | Cautious MPC/Recovery RL/CBF/CPO primary sources + Audit D + Evidence Manifest + Robot Harness/OpenPiVLA/UWM inventories；无 local low-level shield/recovery/real-safety bundle |

## 覆盖合同

- constraint：source/frame/unit/margin/clock/severity/response/reset；
- uncertainty：calibration、chance gate、false-safe、risk–coverage；
- hard safety：CBF safe set、QP filter、feasibility/latency/fallback；
- learned safety：future-risk critic、task/recovery switch、zero-risk boundary；
- state machine：NORMAL/CAUTION/SHIELD/RECOVERY/FALLBACK/E_STOP；
- chunk：short-prefix approval、event queue flush/ack、re-observe；
- evaluation：hazard exposure、success/coverage/violation/recovery/latency；
- project：high-level cancel/compensation 与 physical safety 严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-038 Source Freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html) 与 [WM-038 Knowledge](../knowledge/vol_04_world_model_sim2real_wm038_uncertainty_safety_fallback_recovery.html)。
- WM-031..038 Sim2Real 子链闭合；下一 bounded slice 回到尚缺的 `VLA-WM-011` objective semantics。
