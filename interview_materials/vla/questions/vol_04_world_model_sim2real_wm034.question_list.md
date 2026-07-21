# VOL 04 VLA-WM-034 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-034 control frequency、latency、actuator 与 controller mismatch；WM-035..038 保持 deferred。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-034 | L3 | P0 | control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real？ | Tan/Peng/Hwangbo primary papers + MuJoCo/robosuite official docs + Audit D/WM-023/Architecture Audit/Evidence Manifest；无 local complete clock/actuator/controller/real-transfer bundle |

## 覆盖合同

- 时钟：physics/sensor/policy/network/controller/actuator；
- 延迟：critical path、action age、p50/p95/p99、jitter/deadline/stale；
- 动作：type/frame/unit/normalizer/Hz/action repeat/H/K；
- 执行：controller mode/config/gain/limit、actuator bandwidth/state/saturation；
- 运行：episode/version/deadline、queue flush、safe hold/fallback；
- 评估：round-trip/free-space、latency/frequency/actuator/controller/K matched sweep；
- 项目：设计理解与本地 C2/C3 latency/transfer 证据严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-034 Source Freeze](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html) 与 [WM-034 Knowledge](../knowledge/vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)。
- 下一 bounded slice 是 `VLA-WM-035` camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise；不批量生成 WM-035..038。

