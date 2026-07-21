# VOL 06 PER-015 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：typed perception→action manifest、workspace/IK/bounds/singularity、state/motion collision、robust clearance、trajectory/controller、uncertainty/abstention、failure recovery与五项目真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-015 | L3 | P0 | VLA从semantic target到controller-ready action要过哪些gate？可达性、不确定性和失败怎样处理？ | 六份完整primary PDF、六个fixed official repositories/35文件、10个deterministic probes、五份inventory及11个local-direct exceptions；无本地统一typed gate、robot/tool/scene immutable bundle、IK/collision/TOTG raw report、calibrated risk–coverage、controller execution trace、matched robot episode或候选人ownership闭环 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. semantic target先转成带frame/unit/time/tool/robot/scene/controller revision的typed action target，不直接送IK/controller。
4. workspace只做cheap reject；IK return之后独立验证FK residual、joint bounds、branch与Jacobian最小奇异值。
5. 区分state、motion与path validity；冻结scene、ACM、attached object、padding与motion-validation resolution。
6. nominal clearance加入model/sensor/pose uncertainty inflation；unknown/not_checked在fail-closed模式下不能执行。
7. 几何path通过time parameterization与q/qdot/qddot、start-state、controller shape/semantics/order/unit/time/status检查。
8. semantic/geometric/execution uncertainty分开；KnowNo式prediction set只保留校准与marginal coverage边界，非singleton触发ask。
9. OPD、Robot Harness、OpenPiVLA、WAM、UWM只映射到有证据的perception/action/interface或diagnostic hook，不升级为通用gate、robot success或个人ownership。
10. 30秒答案≤180字符，机制展开≤350字符；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-015 Source Freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html) 与 [PER-015 Knowledge](../knowledge/vol_06_per015_perception_action_reachability_uncertainty_failure_gate.html)。
- 依赖缺口：typed target/robot/tool/scene/controller manifest、raw IK residual/bounds/singularity/collision/clearance/TOTG/execution logs、calibration/risk–coverage、matched episodes与逐文件候选人ownership确认。
- `VLA-PER-015` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只冻结`VLA-PER-016` localization/odometry/SLAM/map-frame/drift source，不生成knowledge/card。
