# VOL 04 VLA-WM-038 原子题卡：Uncertainty、Safety、Fallback 与 Recovery

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-038  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-038 Knowledge](../knowledge/vol_04_world_model_sim2real_wm038_uncertainty_safety_fallback_recovery.html)；来源边界见 [WM-038 Source Freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。

## uncertainty-aware planning、安全约束、fallback 和 recovery policy 如何形成最小闭环？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-038</b> · uncertainty-aware planning、安全约束、fallback 和 recovery policy 如何形成最小闭环？</summary>

**面试意图**：判断你能否把“uncertainty 大就停”升级为 constraint registry、calibration/chance gate、CBF/shield、short-prefix execution、recovery/fallback/E-stop 状态机、queue flush 与可审计 safety metrics。

**30 秒回答**：最小闭环四层：硬约束/CBF逐动作审批；校准不确定性做risk gate；可恢复状态交recovery；不可恢复或超时转fallback/E-stop。VLA只执行短前缀，事件立即flush队列并重观测。评估同报success、coverage、violation severity、false-safe、time-to-safe和gate latency。

**机制展开（约 2 分钟）**：先校验obs schema/timestamp/health，再生成chunk并闭合denorm/frame/unit。硬joint/workspace/collision/force限制和CBF-QP过滤action；world/ensemble风险校准后才作chance约束。risk超阈值切recovery，QP infeasible或attempt/timeout超限转fallback，紧急锁存E-stop。event立即flush旧chunk；用hysteresis/dwell防抖。固定hazard exposure比较task-only、hard、risk、recovery、fallback与fault-injection。

**诊断 / 证据**：保存 policy/world/risk/recovery/controller/shield version，obs/action frame/unit/timestamp，candidate mean/variance/OOD，constraint value/margin/\(\delta\)/severity，nominal/filtered/executed action、QP slack/status/latency，state transition、recovery attempt、fallback/E-stop、chunk flush/ack、near miss/incident/reset approval。重点看 false-safe、severity-weighted violation、autonomous coverage、recovery success、time-to-safe 与 p95/p99 gate latency。

**项目挂钩**：Robot Harness 支持高层 scope、lock、cancel、timeout 和 best-effort stop/cancel compensation，但 safety suite 多步能力仍弱；OpenPiVLA/UWM 只有 simulator rollout 与 controller/protocol partial provenance。当前没有低层 CBF、calibrated risk、recovery matched arms、真机 E-stop/incident bundle。安全说“做过高层执行安全协议并能设计物理 gate”，不能说“已保证真机零事故”。

**追问树**：chance constraint 的\(\delta\)从哪来？ensemble variance为何不等于概率？CBF safe set/forward invariance假设是什么？QP infeasible怎么办？CPO为何不能替代runtime shield？recovery与fallback区别？什么时候必须E-stop？为什么不能总是open gripper？chunk发生collision event如何清队列？怎样测false-safe和coverage？0 collision为何可能是假安全？

**易错点**：只做action clip；未校准variance却报概率；把CPO expected constraint当逐步保证；忽略CBF dynamics/state/feasibility假设；recovery和fallback混用；所有hazard用同一动作；无hysteresis/dwell；event后旧chunk继续执行；只报success或0 collision；不同hazard exposure直接比较；把高层cancel外推成物理安全认证。

**危险答案**：说“uncertainty大就一定安全”“CBF能修所有VLA动作”“CPO保证每步零违规”“Recovery RL保证零事故”“fallback就是永远open gripper”“仿真没碰撞说明真机安全”“Robot Harness有cancel所以项目已完成真机安全闭环”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-038 Source Freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)：chance/CBF/risk/recovery/state-machine/trace 与项目边界。
2. Hewing et al., [Cautious MPC](https://arxiv.org/abs/1705.10702v4)；Ames et al., [CBF](https://arxiv.org/abs/1903.11199v1)。
3. Thananjeyan et al., [Recovery RL](https://arxiv.org/abs/2010.15920v2)；Achiam et al., [CPO](https://arxiv.org/abs/1705.10528v1)。
4. [Evidence Manifest](../evidence/evidence_manifest.html) 与 [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
5. [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 下一步

保持 `unseen`，直到候选人完成真实口述。WM-031..038 子链已闭合；下一 bounded slice 回到尚缺的 `VLA-WM-011`，不重复生成已完成的 WM-039..044，不创建 `coaching_state.md`。
