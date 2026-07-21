# VOL 04 VLA-WM-036 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-036 contact/friction/compliance/gripper semantics；WM-037..038 保持 deferred。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-036 | L3 | P0 | friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点？ | MuJoCo official docs + OpenAI Dexterous primary paper + robosuite pinned gripper/controller code/docs + Audit D/WM-031/WM-033/WM-034/Evidence Manifest；无 local complete contact/gripper/microbench/real-transfer bundle |

## 覆盖合同

- hybrid：separate/touch/stick/slip/roll 与 first divergence；
- friction：sliding/torsional/rolling、cone、condim/mixing；
- compliance：force–displacement、solref/solimp、solver/timestep；
- geometry：collision mesh、margin/gap、object/pad/material；
- gripper：sign/type/unit/range/speed/force/current/deadband/controller/reset；
- evidence：command/aperture/contact/force/hold/lift/task ladder；
- 评估：free-space→press/slip→hold/lift→transport→task 与 matched arms；
- 项目：sim/controller/failure hypothesis 与 C2/C3 real contact 证据严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-036 Source Freeze](../sources/vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html) 与 [WM-036 Knowledge](../knowledge/vol_04_world_model_sim2real_wm036_contact_friction_compliance_gripper.html)。
- 下一 bounded slice 是 `VLA-WM-037` residual/online adaptation/test-time SysID/data aggregation；不批量生成 WM-037..038。

