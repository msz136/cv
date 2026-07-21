# VOL 05 Engineering / Evaluation：EVAL-017 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-017`  
> 难度：L3 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-017 Simulator / Shadow / Real-Robot Gate](../knowledge/vol_05_engineering_eval_eval017_simulator_shadow_real_robot_gate.html)；来源边界见[Source Freeze](../sources/vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)。本题不从simulator summary、shadow action合理性或小样本0事故生成真机成功/安全结论。

## Simulator Success、Shadow Mode 与真机 Gate

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-EVAL-017</b> · simulator成功后，怎样通过shadow mode安全推进到真机？</summary>

**面试意图**：判断你能否区分sim、live no-authority shadow与bounded real canary，建立sim-real common support、candidate authority proof、risk exposure、hard promotion gate及abort/rollback/recovery闭环。

**30 秒回答**：按offline→sim→shadow→真机canary逐级授权。sim冻结协议做paired/fault gate；shadow接真观测但candidate零执行权，只测动作、延迟和约束。真机从低速短程白名单开始，有独立safety/E-stop与人工监管；hard trigger即撤权、停机、切known-good并恢复场景。

**机制展开（约 2 分钟）**：用多policy/task做matched sim-real gap/rank。shadow存live观测、candidate/reference/actual action、latency、OOD与约束投影；未来state由known-good产生，不能报candidate闭环。canary冻结robot/task/workspace/speed/time预算、最低暴露和intervention/E-stop/forbidden gate，同窗对照baseline，每次只扩一个authority。0/n报上界；abort后阻断新动作、等quiescence、切known-good，已发生effect另补偿/人工reconcile。

**诊断 / 证据**：检查candidate/known-good bundle SHA、sim/real common support、env/assets/controller/predicate、shadow credentials/routes/actuator source/interlock、action frame/time、projected constraint、canary allowlist与速度/力/horizon、robot-hours/contact count、intervention分母、0/n上界、E-stop/rollback drill、last effect/quiescence、scene reset及promotion decision ledger。

**项目挂钩**：UWM的186/250是user-confirmed LIBERO sim summary且raw缺；WAM只有公开sim机制和单episode diagnostic；OpenPiVLA有official-checkpoint rollout diagnostics但formal Qwen无real shadow/canary；Harness是tool/sandbox/runtime入口，OPD是static holdout。五项目均无same-bundle sim→shadow→real canary连续证据。

**追问树**：sim 95%为何不够？怎样验证sim能排序policy？shadow与dry-run/canary区别？如何证明无actuator authority？reference action不同是否算错？shadow为何不能报success？risk budget怎么定义？0事故为何仍不安全？intervention分母是什么？rollback为何不恢复物理场景？每阶段扩大什么？

**易错点**：sim当real；单policy算相关；shadow输出dispatch；配置字段当authority proof；shadow trajectory当candidate闭环；reference action当唯一gold；只报overall sim；0/n写零风险；提前接管episode删分母；同时扩大所有变量；software rollback当物理undo；canary通过外推全任务认证。

**危险答案**：说“LIBERO 95%即可上真机”“shadow就是低流量真实执行”“candidate动作看起来合理所以shadow成功”“0次事故证明100%安全”“切回旧checkpoint会恢复场景”“UWM/WAM/OpenPiVLA已完成真机canary”，或编造五项目real robot证据。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-017 知识页](../knowledge/vol_05_engineering_eval_eval017_simulator_shadow_real_robot_gate.html)。
2. [EVAL-017 Source Freeze](../sources/vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)。
3. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与[Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
8. [SIMPLER / EVAL-010 / EVAL-011 / EVAL-014 / WM-031 prerequisites](../sources/vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)。
