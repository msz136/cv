# VOL 04 WM-038 Source Freeze：Uncertainty-aware Planning、Safety Constraint、Fallback 与 Recovery

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-038 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-038  
> 本轮边界：只冻结 VLA rollout 的 uncertainty/risk/hard-constraint/fallback/recovery 最小闭环、状态机、trace 与 matched evaluation；不把 learned risk、action clipping、simulation success 或高层 tool cancellation 写成形式化低层安全保证，也不声称个人项目已完成真机安全部署。

## 1. 冻结结论

1. 安全不能只靠训练 reward、action clipping 或一个 uncertainty threshold；至少要有 input health、hard constraints、risk/uncertainty gate、短前缀执行、re-observe、recovery/fallback/E-stop 和事件日志。
2. chance constraint 只有在预测分布与 calibration 有证据时才是概率声明；未校准 ensemble variance 只能叫 risk heuristic。
3. CBF/QP 可在已知 dynamics、安全函数和可行性假设下做 minimally invasive action filter；它不能凭空补齐错误模型、感知缺失或高 relative-degree 约束。
4. Recovery RL 用 risk critic 判断未来 violation 并在高风险时切 recovery policy；这是 learned shield，不是 zero-risk theorem。
5. fallback、recovery 与 E-stop 职责不同：recovery 尝试回到 recoverable safe set，fallback 可放弃任务交给已验证控制器，E-stop 是锁存式最后手段。
6. chunked VLA 一旦发生风险事件必须 flush queued actions；只拒绝下一次 policy query 不够。

## 2. 一手来源与冻结快照

| ID | Primary source | 冻结版本与快照 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Hewing et al., *Cautious Model Predictive Control using Gaussian Process Regression* | arXiv `1705.10702v4`；ar5iv 2026-07-18 response SHA-256 `2d96ea745b3e465c4181778d8ea31a71f68d3f14d8e000b61f8824ddbf2f8847` | nominal+GP residual、uncertainty propagation、chance constraint/tightening | racing/GP assumptions不等于任意 VLA uncertainty 已校准 |
| S2 | Thananjeyan et al., *Recovery RL: Safe Reinforcement Learning with Learned Recovery Zones* | arXiv `2010.15920v2`；ar5iv response SHA-256 `0e95072e0c1d883e3e9c808307498dc162d58d010ef202285809a2ef0369df12` | offline unsafe data、risk critic、task/recovery policy 分工 | empirical safer learning不等于 formal zero-violation guarantee |
| S3 | Ames et al., *Control Barrier Functions: Theory and Applications* | arXiv `1903.11199v1`；ar5iv response SHA-256 `d9a799bdb3ea6358b5cb9af51c98afe1509ef43bb52f1dca2261c4bbb487f651` | safe-set forward invariance、CBF condition、minimally invasive QP | 需要 dynamics/state/h/feasibility assumptions；不是黑盒 VLA 即插即用 |
| S4 | Achiam et al., *Constrained Policy Optimization* | arXiv `1705.10528v1`；ar5iv response SHA-256 `30d6930c736dda6679c9c05d440a8b6297d6455e93721916a3e6e7cef5077654` | reward/constraint 分离、训练期 near-constraint satisfaction | expected/training guarantee不等于每步 runtime hard safety |
| S5 | [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html) | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | chance/risk/recovery 初始框架与真实性边界 | 不是本地安全 rollout 证据 |
| S6 | [Evidence Manifest](../evidence/evidence_manifest.html) | canonical SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6` | 五项目证据分级与缺失项 | 不支持未归档真机 safety claim |
| S7 | [Robot Harness Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) | canonical SHA-256 `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e` | scope/lock/cancel/timeout/best-effort compensation 与 safety-suite weakness | 不支持低层 collision/force/CBF/recovery 或真实机器人安全率 |
| S8 | [OpenPiVLA Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | canonical SHA-256 `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293` | action/controller/rollout partial provenance | 不支持 real safety gate、incident 或 E-stop |
| S9 | [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | canonical SHA-256 `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | simulator rollout protocol 与 failure instrumentation | 不支持 physical safety/recovery completion |

## 3. 四层安全职责

| layer | 负责什么 | 不能替代什么 |
| --- | --- | --- |
| hard constraints / shield | joint/workspace/collision/force 等已知边界，逐 action 审批 | 未知 hazard、错误 sensing/model |
| uncertainty/risk gate | 对 model/OOD/trajectory risk 做拒绝、缩 horizon 或降速 | 硬限位与 E-stop |
| recovery | 从 recoverable zone 回到 safer set，可继续或重试 | 不可逆/高危状态的立即停止 |
| fallback / E-stop | 放弃 task、交给验证控制器或锁存停机 | learned task performance |

训练期 constrained RL 是第五层“降低 proposal 风险”，不能取代以上 runtime layers。

## 4. Constraint contract 先于算法

每条 constraint 必须写成：

`name + state/source + frame/unit + threshold/margin + sample clock + severity + response + reset/approval`。

至少覆盖 joint position/velocity/acceleration、Cartesian workspace/orientation、self/environment collision、force/torque/current/contact、gripper/object state、human zone、thermal/battery、sensor/communication staleness。只写“做 action clip”缺少 hazard、单位和响应语义。

## 5. Chance constraint

对预测状态/动作分布，逐 constraint 可要求：[S1]

\[
\Pr\!\left(g_j(x_{t+k},u_{t+k})\le 0\right)\ge 1-\delta_j,
\qquad k=1,\ldots,H.
\]

变量解释：\(g_j\le0\) 表示第 \(j\) 个安全约束，\(\delta_j\) 是允许的 violation probability，\(H\) 是规划 horizon。直觉是 planner 不只看期望轨迹，还给不确定性留 margin。实现映射：保存 predicted mean/covariance/quantile、\(\delta_j\)、constraint margin、candidate rejection 与 chosen horizon。

若 scalar constraint 在局部近似为 Gaussian，可写成：

\[
\mu_{g_j}+\Phi^{-1}(1-\delta_j)\sigma_{g_j}\le0.
\]

变量解释：\(\mu_{g_j},\sigma_{g_j}\) 是约束变量的预测均值/标准差，\(\Phi^{-1}\) 是标准正态分位点。实现映射：需要明确 distribution/linearization 和 calibration；该式是常见 Gaussian deterministic equivalent，S1 的具体实现还使用 state distribution propagation 与 probabilistic reachable-set tightening。

## 6. Uncertainty 必须校准

ensemble disagreement、GP variance、quantile spread、world-model sample variance 都可能作为 score，但只有在 held-out/shifted trajectories 上验证 coverage 才能叫 calibrated risk。

至少报告：

- risk bin → observed violation reliability；
- false-safe / false-alarm；
- risk–coverage curve；
- OOD/corruption 分层；
- threshold、horizon 和 latency sensitivity。

“variance 大就停”是 heuristic；“违反概率低于 1%”需要 denominator、calibration 和 assumptions。

## 7. CBF safe set

对 control-affine dynamics \(\dot x=f(x)+g(x)u\)，定义安全集：[S3]

\[
\mathcal C=\{x:h(x)\ge0\}.
\]

变量解释：\(h(x)\) 是 barrier function；\(\mathcal C\) forward invariant 意味着从安全集出发的状态保持在安全集。实现映射：\(h\) 可编码 collision distance、workspace margin 或 joint limit，但必须记录 state source、model revision 与 sampling delay。

CBF 条件可写为：

\[
L_fh(x)+L_gh(x)u\ge-\alpha(h(x)).
\]

变量解释：\(L_fh,L_gh\) 是 Lie derivatives，\(\alpha\) 是 extended class-\(\mathcal K\) function。直觉是边界附近动作必须把系统推回/保持在安全侧。实现映射：若 sensing/dynamics/relative degree 不满足假设，不能直接宣称 forward invariance。

## 8. CBF-QP action shield

给 policy proposal \(u_{nom}\)，minimally invasive filter 为：[S3]

\[
u^*=\arg\min_u\frac12\lVert u-u_{nom}\rVert_2^2
\quad\text{s.t.}\quad
L_fh(x)+L_gh(x)u\ge-\alpha(h(x)),\;u\in\mathcal U.
\]

变量解释：\(u^*\) 是批准动作，\(\mathcal U\) 是 actuator/action constraints。实现映射：保存 nominal/approved action、active constraint、QP status/slack、solve latency、infeasible reason；QP infeasible 不能继续执行 nominal action，应转 fallback/E-stop。

## 9. Training constraint 不等于 runtime shield

CPO 将 reward 与 constraint cost 分开，并在其假设下提供训练迭代中的 near-constraint satisfaction。[S4] 但 expected discounted cost 小并不等于：

- 每个 trajectory 都无 violation；
- rare catastrophic event 被覆盖；
- 真机 perception/model 正确；
- runtime action 一定满足 hard limit。

因此 constrained training 可减少危险 proposals，仍需 runtime hard filter、monitor 和 fallback。

## 10. Recovery RL risk critic

Recovery RL 定义未来 constraint cost 的 discounted risk：[S2]

\[
Q_{risk}^{\pi}(s_i,a_i)=
\mathbb E_{\pi,\mu,P}
\left[\sum_{t\ge0}\gamma_{risk}^t C(s_{t+i})\right].
\]

变量解释：\(C(s)=1\) 表示 constraint violation，\(\gamma_{risk}\) 是 risk discount。直觉是当前 action 的危险不只看一步 collision，还看后续进入 unsafe zone 的概率质量。实现映射：保存 risk target/source、offline unsafe-data lineage、critic score、threshold、calibration 与 actual violation。

## 11. Task/recovery policy 切换

\[
a_t=
\begin{cases}
\pi_{task}(s_t), & \hat Q_{risk}(s_t,a_t^{task})\le\epsilon_{risk},\\
\pi_{rec}(s_t), & \text{otherwise}.
\end{cases}
\]

变量解释：\(\epsilon_{risk}\) 是 risk gate，\(\pi_{rec}\) 负责导向安全，而不是最大化 task reward。实现映射：保存 task proposal、risk score、switch reason、recovery action/attempt、是否回到 safe set。S2 支持这一 learned recovery zone 思路，但不支持任意项目的 zero-risk 声明。

## 12. Recovery、fallback、E-stop 分离

| mechanism | 目标 | authority | 退出条件 |
| --- | --- | --- | --- |
| recovery policy | 回到 recoverable safe set，可能继续 task | learned/scripted limited | safe-set dwell + health pass |
| fallback controller | 放弃/暂停 task，hold/retreat/home 等 | verified conservative | operator/reset protocol |
| E-stop | 立即锁存停机/切断危险执行 | independent highest priority | 人工检查与显式复位 |

具体 fallback 必须来自 hazard analysis。“总是 open gripper”在高处持物时可能制造掉落；“总是 retreat”在未知障碍后方也可能更危险。

## 13. 最小安全状态机

建议状态：

`NORMAL → CAUTION → SHIELD/REPLAN → RECOVERY → FALLBACK → E_STOP`。

转换必须有 threshold、hysteresis、dwell time、attempt budget、timeout 和 queue-flush rule。成功 recovery 不能一帧后立刻回 NORMAL；需要 safe-set dwell、sensor health 与 controller ack。

## 14. Chunked VLA 的队列风险

VLA 常一次输出 \(H\) 个动作，只执行前 \(K\) 步。安全层必须逐步或逐短前缀审批：

\[
K_{safe}=\min(K,K_{risk},K_{health}),
\qquad 1\le K_{safe}\le K.
\]

变量解释：\(K_{risk}\) 由预测风险限制，\(K_{health}\) 由 observation/controller freshness 限制。实现映射：记录 query time、chunk ID、approved prefix、每步 gate 与 event-triggered queue flush。risk/timeout/collision event 后继续执行旧 chunk 是严重 contract violation。

## 15. Guarded rollout 顺序

1. observation schema/range/timestamp/health gate；
2. policy/world-model 生成候选 chunk/trajectory；
3. denormalize、frame/unit/order 转换；
4. hard joint/workspace/collision/force limits；
5. CBF/shield 或 deterministic action projection；
6. uncertainty/chance/risk gate 与 horizon/prefix reduction；
7. 执行批准的短前缀并逐步 monitor；
8. event 时 flush queue → recovery/fallback/E-stop；
9. 保存完整 trace、reset/approval 和 incident。

## 16. Guarded rollout 伪代码

```python
def guarded_vla_step(obs, policy, safety, recovery, controller):
    # 1. Reject malformed, stale or unhealthy observations before inference.
    health = safety.validate_observation(obs)
    if not health.ok:
        return controller.fallback(health.reason, flush_queue=True)

    # 2. Generate a candidate action chunk, then close the execution contract.
    raw_chunk = policy.infer(obs)
    env_chunk = controller.denormalize_and_transform(raw_chunk)

    # 3. Apply hard limits / CBF projection and evaluate uncertainty plus learned risk.
    approved = safety.filter_and_score(obs, env_chunk)
    if approved.emergency:
        return controller.estop(approved.reason, latch=True)
    if approved.requires_recovery:
        return recovery.act(obs, flush_queue=True)
    if not approved.feasible:
        return controller.fallback(approved.reason, flush_queue=True)

    # 4. Execute only the approved prefix; re-observe after every step/event.
    return controller.execute_prefix(approved.actions, monitor_every_step=True)
```

伪代码是 S1–S9 的工程综合。真实 `fallback/recovery/estop` 动作必须按 robot/task hazard analysis 实现。

## 17. 必须保存的 trace / manifest

- policy/world/risk/recovery/controller/shield version 与 config hash；
- observation/action schema、frame/unit/order、timestamp、health；
- candidate trajectory/chunk、predicted mean/variance/quantile/OOD；
- constraint name/value/margin/threshold/\(\delta\)/severity；
- nominal/filtered/executed action、active constraint、QP status/slack/latency；
- task/recovery/fallback/E-stop state、transition reason、dwell/attempt/timeout；
- queue ID、approved prefix、flush/ack；
- violation severity、near miss、intervention、incident、reset/approval；
- task success、time-to-safe、coverage、false-safe/false-alarm。

## 18. Evaluation metric ladder

| level | metric | 不能替代 |
| --- | --- | --- |
| proposal | predicted risk/uncertainty、candidate rejection | observed violation |
| filter | intervention/QP feasibility/slack/latency | recovery success |
| safety event | violations/near misses、severity、false-safe | task utility |
| recovery | attempts、success、time-to-safe、repeat violation | deployment safety |
| fallback | fallback/E-stop rate、queue flush/ack | low false alarm |
| task | success、coverage、latency/throughput | safety guarantee |

只报“0 collision”但 trial 很少、coverage 很低或一直 fallback，不证明可用安全系统。

## 19. Matched safety evaluation

固定 checkpoint、task/init/seed/hazard suite、camera/action/controller、horizon/replan、threshold source 与 trial denominator：

| arm | 内容 |
| --- | --- |
| task-only | 无新增 safety gate 的诊断 baseline |
| hard-only | deterministic limits / shield |
| uncertainty-only | calibrated/heuristic risk gate，明确等级 |
| hard+risk | 双层 gate |
| hard+risk+recovery | learned/scripted recovery |
| fallback-only | 无 learned recovery 的 conservative control |
| combined | 全状态机 |
| stale/OOD/fault | delay/dropout/model-error/contact/hazard stress |

报告 task success、autonomous coverage、severity-weighted violation、intervention、recovery/time-to-safe、fallback/E-stop、false-safe/false-alarm 和 p95/p99 gate latency。没有等 hazard 暴露就不能比较 violation rate。

## 20. Failure-first 诊断

| 症状 | 首查 |
| --- | --- |
| planner“低风险”仍碰撞 | calibration/OOD、collision geometry、prediction horizon、timestamp |
| CBF/QP 经常 infeasible | safe set/model/action limit 不一致、已进入不可恢复区、latency |
| recovery oscillation | hysteresis/dwell、policy conflict、stale risk、attempt budget |
| false alarm 太多 | threshold/calibration、risk support、constraint margin、sensor noise |
| event 后仍动作 | queue flush/ack、controller buffer、race/timeout |
| success 高但 violation 也高 | task reward 未约束、gate bypass、severity 被平均掩盖 |

## 21. 项目真实性边界

本地证据支持：

- Robot Harness 在高层 tool/runtime 层有 robot scope、互斥 lock、cancel event、timeout 与 best-effort stop/cancel compensation；
- Robot Harness safety suite 同时暴露多步 safety tool accuracy 仍弱，不能隐藏；
- OpenPiVLA/UWM 提供 simulator rollout、action/controller/protocol partial provenance。

本地证据不支持：

- 低层 joint/workspace/collision/force/CBF filter；
- calibrated uncertainty/risk critic、recovery policy matched test；
- 真机 fallback/E-stop、queue-flush ack、near-miss/incident/approval log；
- physical safety rate、formal guarantee 或 safety certification。

安全表达：可以说“我在 Robot Harness 实现/审计了高层 scope、取消、timeout 和补偿协议，并能设计 VLA 的 layered safety gate”；不能说“项目已实现真机安全闭环”或“通过 CBF/Recovery RL 保证零事故”。[S6–S9]

## 22. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| GP residual uncertainty 可进入 chance-constrained MPC | S1 | primary | checked with model/calibration assumptions |
| Recovery RL 分 task/recovery policy 并用 future-risk threshold 切换 | S2 | primary | checked; zero-risk rejected |
| CBF-QP 可在假设下最小修正 nominal action 以维持 safe set | S3 | primary | checked with dynamics/h/feasibility assumptions |
| CPO 提供训练期 near-constraint satisfaction 而非 runtime hard shield | S4 | primary | checked |
| layered state machine、queue flush、trace/matched matrix | S1–S9 + engineering synthesis | synthesis | WARN / needs execution |
| 用户项目已完成真机 safety deployment | S6–S9 | missing local evidence | rejected |

## 23. 面试答题骨架

安全回答要覆盖：

1. hard constraint、calibrated uncertainty/risk、recovery、fallback/E-stop 四层；
2. policy 只 proposal，action 必须经过 transform、shield 和短前缀审批；
3. event 立刻 flush chunk，按状态机和 hysteresis/timeout 处理；
4. 评估同时报 success、coverage、violation severity、false-safe、recovery/time-to-safe、fallback 和 gate latency；
5. 当前项目只支持高层 cancel/compensation 与 simulator protocol，不声称真机安全部署。

## 24. 仍待独立复核与补证据

1. 四篇一手来源已复核，source freeze 保持 `independent_fact_review=PENDING`。
2. 需要 local constraint registry、CBF/shield/risk/recovery/fallback state-machine implementation 与 fault-injection matched arms。
3. real claim 需要真机 limits、E-stop、queue flush/ack、near-miss/incident、reset/approval 和 protocol-complete trials。
4. 需要真实口述后才更新题卡状态；不得创建 `coaching_state.md`。
5. 浏览器本地 `file://` 若受策略阻断，只记录静态验证，不能写 visual PASS。

## 25. 参考来源

1. Hewing, Kabzan and Zeilinger, [*Cautious Model Predictive Control using Gaussian Process Regression*](https://arxiv.org/abs/1705.10702v4), 2019.
2. Thananjeyan et al., [*Recovery RL: Safe Reinforcement Learning with Learned Recovery Zones*](https://arxiv.org/abs/2010.15920v2), 2021.
3. Ames et al., [*Control Barrier Functions: Theory and Applications*](https://arxiv.org/abs/1903.11199v1), 2019.
4. Achiam et al., [*Constrained Policy Optimization*](https://arxiv.org/abs/1705.10528v1), ICML 2017.
5. [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html).
6. [Evidence Manifest](../evidence/evidence_manifest.html).
7. [Robot Harness Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html).
8. [OpenPiVLA Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html).
9. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html).

## 26. 下一边界

完成 WM-038 后，VOL 04 的 Sim2Real 安全子链 `WM-031..038` 闭合。下一 bounded slice 回到尚缺的 `VLA-WM-011`：reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么；不重复生成已完成的 WM-039..044。
