# VOL 04 VLA-WM-033 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-033 dynamics randomization 与 system identification；WM-034..038 保持 deferred。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-033 | L3 | P0 | dynamics randomization 与 system identification 如何互补，参数范围怎样确定？ | Peng/Tan/UP-OSI/SimOpt primary papers + Audit D/WM-031/WM-032/Evidence Manifest；无 local dynamics SysID/DR/real-transfer bundle |

## 覆盖合同

- SysID：measurement/excitation、nominal fit、held-out residual、uncertainty 与 identifiability；
- DR：residual/population/drift/structural coverage；
- Range：unit/source/distribution/correlation/cadence/validity；
- 方法：offline SysID、fixed calibrated DR、explicit OSI、implicit recurrent、SimOpt 边界；
- 评估：baseline / SysID-only / DR-only / combined / overwide matched arms；
- 项目：设计理解与本地 C2/C3 证据严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-033 Source Freeze](../sources/vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html) 与 [WM-033 Knowledge](../knowledge/vol_04_world_model_sim2real_wm033_dynamics_randomization_system_identification.html)。
- 下一 bounded slice 是 `VLA-WM-034` control frequency / latency / actuator / controller mismatch；不批量生成 WM-034..038。

