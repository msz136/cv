# VOL 04 World Model / Sim2Real：Uncertainty、Safety、Fallback 与 Recovery（WM-038）

> 状态：drafted / VLA-WM-038 / knowledge_40_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：uncertainty-aware planning、安全约束、fallback 和 recovery policy 如何形成最小闭环？  
> 前置：[WM-029 Value Calibration / Pessimism](vol_04_world_model_sim2real_wm029_imagined_ood_value_calibration_pessimism.html)、[WM-030 Planning Latency](vol_04_world_model_sim2real_wm030_test_time_planning_latency_risk.html)、[WM-038 Source Freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。

## 1. 面试结论

最小安全闭环不是“action clip + uncertainty 大就停”，而是：

1. observation health/schema/timestamp gate；
2. policy/world model 只生成 candidate chunk；
3. denormalize 与 frame/unit/order 闭合；
4. hard joint/workspace/collision/force constraints 与 shield；
5. calibrated uncertainty/chance/risk gate；
6. 只执行批准的短前缀并逐步 monitor；
7. event 立即 flush queue，进入 recovery/fallback/E-stop 状态机；
8. 保存 violation、false-safe、recovery、time-to-safe、incident 和 reset/approval。

## 2. 四层职责

| layer | 职责 | 失败时 |
| --- | --- | --- |
| hard limit / shield | 审批已知安全边界 | infeasible → fallback/E-stop |
| uncertainty/risk | 拒绝/缩短未知或高风险轨迹 | caution/replan/recovery |
| recovery | 回到 recoverable safe set | attempt/timeout 超限 → fallback |
| fallback/E-stop | 放弃 task、保守控制或锁存停机 | 人工检查/显式 reset |

constrained training 只能降低 dangerous proposal，不能替代 runtime 层。

## 3. Constraint registry

每条约束都要包含：`name、state source、frame/unit、threshold/margin、clock、severity、response、reset/approval`。

至少覆盖：joint position/velocity/acceleration、Cartesian workspace、self/environment collision、force/torque/current/contact、gripper/object、human zone、thermal/battery、sensor/network staleness。没有单位、采样源和 response 的“安全阈值”不可执行。

## 4. Chance constraint

\[
\Pr\!\left(g_j(x_{t+k},u_{t+k})\le0\right)\ge1-\delta_j,
\qquad k=1,\ldots,H.
\]

变量解释：\(g_j\le0\) 是第 \(j\) 个约束，\(\delta_j\) 是允许的 violation probability，\(H\) 是规划 horizon。直觉是 planner 给预测误差留 margin，而不是只看 mean trajectory。实现映射：保存 mean/covariance/quantile、\(\delta_j\)、constraint margin、candidate rejection、chosen horizon 与 source model。[1]

若 scalar constraint 近似 Gaussian：

\[
\mu_{g_j}+\Phi^{-1}(1-\delta_j)\sigma_{g_j}\le0.
\]

变量解释：\(\mu_{g_j},\sigma_{g_j}\) 是预测均值/标准差，\(\Phi^{-1}\) 是 normal quantile。实现映射：必须记录 Gaussian/linearization assumption 与 held-out calibration；没有 calibration 时只叫 conservative heuristic。

## 5. Uncertainty calibration

ensemble/GP/world-model spread 本身不是 violation probability。至少要看：

- risk bin 对 observed violation 的 reliability；
- false-safe（最危险）与 false-alarm；
- risk–coverage curve；
- OOD/corruption/hazard family；
- threshold/horizon/latency sensitivity。

“variance 大就停”可以是 gate；“风险低于 1%”需要 denominator、coverage 与 assumptions。

## 6. CBF safe set

对 \(\dot x=f(x)+g(x)u\)，定义：[2]

\[
\mathcal C=\{x:h(x)\ge0\},
\qquad
L_fh(x)+L_gh(x)u\ge-\alpha(h(x)).
\]

变量解释：\(h(x)\) 是 barrier function，\(\mathcal C\) 是 safe set，\(L_fh,L_gh\) 是 Lie derivatives。直觉是边界附近必须选择把系统留在安全侧的动作。实现映射：可映射 collision/workspace/joint margin，但要记录 state/model/h revision、sampling delay、relative degree 与 feasibility assumptions。

## 7. CBF-QP shield

\[
u^*=\arg\min_u\frac12\lVert u-u_{nom}\rVert_2^2
\quad\text{s.t.}\quad
L_fh(x)+L_gh(x)u\ge-\alpha(h(x)),\;u\in\mathcal U.
\]

变量解释：\(u_{nom}\) 是 VLA/controller proposal，\(u^*\) 是 minimally modified approved action，\(\mathcal U\) 是 actuator limits。实现映射：记录 nominal/approved action、active constraint、QP status/slack/latency/infeasible reason。QP infeasible 不能执行 nominal proposal，应转 fallback/E-stop。[2]

## 8. CPO 为什么仍不够

CPO 把 reward 与 constraint cost 分开，并在其假设下追求训练迭代的 near-constraint satisfaction。[3] 但 expected discounted cost 较小不等于每一步、每条轨迹、每个 rare hazard 都安全；也不保证真机感知/模型正确。因此：

- training constraint：减少危险 proposal；
- runtime shield：逐 action 审批；
- monitor/fallback：处理模型外事件。

三者不能互相替代。

## 9. Recovery risk critic

\[
Q_{risk}^{\pi}(s_i,a_i)=
\mathbb E\left[\sum_{t\ge0}\gamma_{risk}^{t}C(s_{t+i})\right].
\]

变量解释：\(C(s)=1\) 表示 violation，\(\gamma_{risk}\) 是 risk discount。直觉是当前 action 的风险包括未来进入 unsafe zone。实现映射：保存 offline unsafe data lineage、risk target/score/threshold、calibration 与 observed violation。[4]

## 10. Task / recovery 切换

\[
a_t=
\begin{cases}
\pi_{task}(s_t), & \hat Q_{risk}(s_t,a_t^{task})\le\epsilon_{risk},\\
\pi_{rec}(s_t), & \text{otherwise}.
\end{cases}
\]

变量解释：\(\pi_{rec}\) 追求回到 safer zone，\(\epsilon_{risk}\) 是切换阈值。实现映射：保存 task proposal、risk score、switch reason、recovery attempt/action、safe-set return。Recovery RL 支持这一 learned recovery zone 机制，但不提供任意 VLA zero-risk 保证。[4]

## 11. Recovery、fallback、E-stop

- **recovery**：learned/scripted，有限 authority，尝试回 safe set；
- **fallback**：verified conservative controller，可 hold/retreat/home/abort；
- **E-stop**：independent、latched、最高优先级，需要人工检查与显式 reset。

fallback 动作必须 hazard-specific。高处持物时 open gripper 可能更危险；未知后方障碍时 blind retreat 也可能更危险。

## 12. 最小状态机

`NORMAL → CAUTION → SHIELD/REPLAN → RECOVERY → FALLBACK → E_STOP`

每条 transition 必须有：threshold、hysteresis、dwell time、attempt budget、timeout、queue flush/ack 与 reset authority。recovery 一帧成功不能立即回 NORMAL；需要 safe-set dwell 和 sensor/controller health pass。

## 13. Chunk queue 与 approved prefix

\[
K_{safe}=\min(K,K_{risk},K_{health}),
\qquad 1\le K_{safe}\le K.
\]

变量解释：\(K\) 是计划执行的 chunk prefix，\(K_{risk}\) 由风险限制，\(K_{health}\) 由 observation/controller freshness 限制。实现映射：保存 chunk/query ID、每步 gate、approved prefix 与 event-triggered flush/ack。碰撞、timeout、sensor fault 后继续旧 chunk 是安全合同错误。

## 14. Guarded rollout 伪代码

```python
def guarded_vla_step(obs, policy, safety, recovery, controller):
    # 1. Reject stale/malformed observations before policy inference.
    health = safety.validate_observation(obs)
    if not health.ok:
        return controller.fallback(health.reason, flush_queue=True)

    # 2. Generate a candidate chunk and close normalization/frame/controller semantics.
    raw_chunk = policy.infer(obs)
    env_chunk = controller.denormalize_and_transform(raw_chunk)

    # 3. Apply hard limits / shield and score uncertainty plus learned risk.
    approved = safety.filter_and_score(obs, env_chunk)
    if approved.emergency:
        return controller.estop(approved.reason, latch=True)
    if approved.requires_recovery:
        return recovery.act(obs, flush_queue=True)
    if not approved.feasible:
        return controller.fallback(approved.reason, flush_queue=True)

    # 4. Execute only the approved prefix and monitor each step.
    return controller.execute_prefix(approved.actions, monitor_every_step=True)
```

顺序是 health → proposal → execution contract → hard shield → risk gate → short prefix → re-observe/event state machine。

## 15. 必须保存的 trace

- policy/world/risk/recovery/controller/shield version；
- obs/action schema、frame/unit/order、timestamp/health；
- candidate chunk/trajectory、mean/variance/quantile/OOD；
- constraint name/value/margin/threshold/\(\delta\)/severity；
- nominal/filtered/executed action、QP/slack/latency；
- state transition、dwell/attempt/timeout、fallback/E-stop；
- queue/prefix/flush/ack；
- violation/near-miss/intervention/incident/reset/approval；
- success/coverage/false-safe/time-to-safe。

## 16. Matched safety evaluation

| arm | 目的 |
| --- | --- |
| task-only | 无 gate 诊断 baseline |
| hard-only | 硬限制/shield 贡献 |
| uncertainty-only | 风险 gate 贡献与 calibration 边界 |
| hard+risk | 双层作用 |
| hard+risk+recovery | learned/scripted recovery 增量 |
| fallback-only | 无 learned recovery 的保守对照 |
| combined | 全状态机 |
| stale/OOD/fault | delay/dropout/model/contact/hazard stress |

固定 checkpoint、task/init/seed/hazard exposure、camera/action/controller、horizon、threshold source 与 denominator。报告 success、coverage、severity-weighted violations、false-safe/false-alarm、intervention、recovery/time-to-safe、fallback/E-stop 与 p95/p99 gate latency。

## 17. 高频诊断

| 症状 | 首查 |
| --- | --- |
| predicted low-risk 仍碰撞 | calibration/OOD、geometry、horizon、timestamp |
| CBF/QP infeasible | safe set/model/limit 不一致、已进不可恢复区、latency |
| recovery oscillates | hysteresis/dwell、task/recovery conflict、stale risk |
| false alarm 高 | threshold/calibration、margin、sensor noise/support |
| event 后仍动作 | queue flush/ack、controller buffer、race condition |
| success 与 violation 同时高 | gate bypass、reward/constraint 错、severity 被平均 |

## 18. 项目挂钩与真实性边界

Robot Harness 在高层 tool/runtime 层有 scope、mutual exclusion、cancel event、timeout 和 best-effort stop/cancel compensation；同时 safety suite 的多步 tool accuracy 仍弱。这支持“高层执行协议与失败边界”，不支持低层 CBF/collision/force/recovery 或真机安全率。

OpenPiVLA/UWM 只提供 simulator rollout、action/controller/protocol partial provenance；当前没有 calibrated risk、shield/recovery matched arms、真实 fallback/E-stop、near-miss/incident 或 approval bundle。[5][6][7][8]

面试安全回答：

> 我在 Robot Harness 做过高层 scope、取消、timeout 和补偿协议；物理 VLA safety 需要另建 observation health、hard constraints/CBF、calibrated risk、短前缀、queue flush、recovery/fallback/E-stop 状态机。当前没有真机 bundle，所以只讲设计与高层软件证据，不讲零事故或安全认证。

## 19. 实战审计清单

- [ ] constraint registry 含 source/frame/unit/margin/clock/severity/response；
- [ ] uncertainty 有 calibration、false-safe 与 risk–coverage；
- [ ] nominal/filtered/executed action 与 QP status/slack 可追溯；
- [ ] task/recovery/fallback/E-stop 职责和 authority 分离；
- [ ] hysteresis/dwell/attempt/timeout/reset approval 明确；
- [ ] chunk event 后 flush/ack；
- [ ] hard/risk/recovery/fallback/fault matched arms；
- [ ] hazard exposure、success、coverage、violation severity 同报；
- [ ] high-level cancel 不外推 physical safety；
- [ ] ownership 与 C0–C3 evidence 对齐。

## 20. 参考来源

1. Hewing et al., [*Cautious Model Predictive Control using Gaussian Process Regression*](https://arxiv.org/abs/1705.10702v4)。
2. Ames et al., [*Control Barrier Functions: Theory and Applications*](https://arxiv.org/abs/1903.11199v1)。
3. Achiam et al., [*Constrained Policy Optimization*](https://arxiv.org/abs/1705.10528v1)。
4. Thananjeyan et al., [*Recovery RL*](https://arxiv.org/abs/2010.15920v2)。
5. [WM-038 Source Freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。
6. [Evidence Manifest](../evidence/evidence_manifest.html)。
7. [Robot Harness Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
8. [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 21. 下一节点

WM-031..038 Sim2Real 安全子链已闭合。下一尚缺节点回到 `VLA-WM-011`：reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么；本节点保持 WARN，题卡在真实口述前保持 unseen。
