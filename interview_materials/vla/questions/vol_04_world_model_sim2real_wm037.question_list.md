# VOL 04 VLA-WM-037 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-037 adaptation method selection；WM-038 保持 deferred。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-037 | L3 | P1 | residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择？ | SimOpt/UP-OSI/RMA/Residual RL/DAgger primary sources + Audit D + Evidence Manifest + OPD/UWM/OpenPiVLA inventories；无 local robot adaptation/safe-collection/rollback bundle |

## 覆盖合同

- update object：action、parameter/latent、sim distribution、dataset、weights；
- authority：real trajectory、expert/reward、privileged target 与 actuation limit；
- residual：reliable base、dimension/norm/rate limit、fallback；
- OSI/RMA：explicit physical parameter 与 task-relevant latent 分离；
- SimOpt：trajectory discrepancy、KL-bounded outer-loop distribution update；
- DAgger：learner-state collection、expert label、dataset lineage、retrain；
- evidence：replay→sim matched→real shadow→limited authority→real protocol；
- project：offline/token/sim rollout 与 robot real online adaptation 严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-037 Source Freeze](../sources/vol_04_wm037_adaptation_method_selection_source_freeze.html) 与 [WM-037 Knowledge](../knowledge/vol_04_world_model_sim2real_wm037_adaptation_method_selection.html)。
- 下一 bounded slice 是 `VLA-WM-038` uncertainty-aware planning/safety/fallback/recovery；不跨卷扩写。
