# VOL 04 World Model / Sim2Real：Action-conditioned、相关性与可干预 Dynamics（WM-014）

> 状态：drafted / VLA-WM-014 / knowledge_44_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：action-conditioned prediction怎样区分相关性预测与可干预dynamics？  
> 前置：[World-model Foundations](vol_04_world_model_sim2real.html)、[WM-014 Source Freeze](../sources/vol_04_wm014_action_conditioned_correlation_intervention_source_freeze.html)；多步与诊断见[WM-013](vol_04_world_model_sim2real_wm013_latent_overshooting_multistep_consistency.html)、[WM-020](vol_04_world_model_sim2real_wm020_failure_diagnostics.html)。

## 1. 面试结论

`action-conditioned`只证明函数接受action，不证明action effect正确。高分回答要区分：

```text
action tensor接入
  → model对action敏感
  → held-out p(y|x,a)拟合
  → same-state p(y|x,do(a)) effect对齐
  → cross-policy / OOD / real / closed-loop可用
```

## 2. Observational vs interventional

\[
p(y\mid x,a)
\quad\text{vs}\quad
p(y\mid x,\operatorname{do}(a)).
\]

变量解释：conditioning是在日志中筛出policy选择a的样本；`do(a)`是外部设action并切断原policy assignment。直觉是“看到采取a的状态”不等于“让同一状态采取a”。实现映射：offline prediction多是前者；cloned simulator或安全随机trial近似后者。[1][2]

## 3. Hidden confounder

\[
p(y\mid x,a)=\int p(y\mid x,a,u)p(u\mid x,a)du,
\]

\[
p(y\mid x,\operatorname{do}(a))
=\int p(y\mid x,a,u)p(u\mid x)du.
\]

变量解释：\(u\) 同时影响action assignment和future outcome。观测action会改变hidden-state mixture，干预不应改变pre-action \(u\)。机器人例子：expert只在快碰撞时刹车，日志可能显示“刹车与碰撞相关”，并非刹车导致碰撞。[2][3]

## 4. 识别假设

让两者相等至少需要：

- state/history充分阻断混杂；
- action在该state附近有overlap/positivity；
- command/treatment定义一致；
- pre-action变量没有future leakage；
- environment/controller机制在比较间稳定。

低prediction loss不会自动满足这些假设。

## 5. Partial observability

单帧RGB常缺速度、遮挡、contact、gripper load、controller integrator。behavior policy若用history/proprio/privileged state选action，而model只看image，action会携带hidden-state信息，成为“状态提示”而非纯物理干预。

检查image-matched/full-state-different pairs、增加history/proprio后的effect变化与same-full-state action swap。

## 6. Action support

expert在某state只选一个action时，未见action的do-effect不能从日志直接识别。连续action数据只覆盖窄manifold。记录state-conditioned density、nearest-neighbor distance、OOD/ensemble score与safe support mask；support外只称extrapolation。

## 7. Executed action contract

```text
raw policy action
  → denormalize/frame transform
  → clip/shield/controller setpoint
  → actuator command
  → measured joint/EE/contact outcome
```

真正treatment必须明确是哪一层。若模型condition raw command，实际被clip或delay，学到的只是command correlation。保存nominal/approved/executed action、controller state与timestamps。

## 8. Ignoring vs shortcut

- action ignoring：swap action输出几乎不变；
- action shortcut：输出会变，但action只标识policy/task phase，同state真实effect错误。

shuffle/zero/Jacobian可发现前者；same-state environment intervention才检查后者。

## 9. Sensitivity Jacobian

\[
J_a(x,a)=\frac{\partial\mathbb E_\theta[Y\mid x,a]}{\partial a}.
\]

变量解释：\(J_a\)是模型局部action敏感度。非零只说明使用action，不说明方向/幅度正确；clip、contact和discrete action处还可能不可微。实现映射：做finite-difference sweep并与environment effect curve比较。

## 10. Conditional action effect

\[
\tau(x;a,a')
=\mathbb E[Y\mid x,\operatorname{do}(a)]
-\mathbb E[Y\mid x,\operatorname{do}(a')].
\]

变量解释：\(Y\)可为pose、latent、reward、contact或success。直觉是在同一pre-action context只改变action。实现映射：固定frame/unit/horizon/seed；不同initial state的outcome差不能替代effect。

## 11. Effect-alignment error

\[
\mathcal E_{\mathrm{effect}}
=\mathbb E\left[
\left\|
(\hat Y_s(a)-\hat Y_s(a'))
-(Y_s^{env}(a)-Y_s^{env}(a'))
\right\|_W
\right].
\]

变量解释：\(s\)是cloned full state，\(W\)对齐position/orientation/contact/reward单位。直觉是比较model与environment的action-induced delta，而不是共同baseline error。随机环境要多seed比较distribution。[3][4]

## 12. Cloned-state action-swap

1. freeze full state、object/contact/controller state与seed；
2. 给model同一可用observation/history；
3. 生成expert/perturbed、sign/axis、zero/nonzero action pair；
4. 从同snapshot执行两次；
5. 比较one/multi-step pose/contact/reward/termination effect；
6. 按support/state family/horizon分层。

这证明simulator contract内effect，不是real-world transfer。

## 13. 真实机器人matched intervention

真实系统不能完美clone：使用fixture/reset、small safe randomized perturbation、多trial、pre-action sensor/contact/controller matching、hard gate/short prefix/fallback；报告initial-state差、effect CI、invalid/reset failures与coverage。两个不同起点各跑一次不是真counterfactual。

## 14. Negative controls

| Probe | 应看到 | 暴露风险 |
| --- | --- | --- |
| zero action | inertia/static baseline | 纯时间预测 |
| action shuffle | prediction显著变差 | action ignoring/leakage |
| sign/axis swap | effect方向对应变化 | order/frame shortcut |
| scale sweep | deadband/clip/saturation一致 | 非物理外推 |
| OOD action | 高uncertainty/拒绝 | 过度自信 |
| nuisance intervention | physical effect稳定 | background/task-ID shortcut |

## 15. Cross-policy invariance

在同environment/controller下，用expert、random、安全扰动、recovery policy采数据。给定充分state/action后transition mechanism应较稳定；effect随policy ID/mixture大变，提示state不充分或policy shortcut。不同policy覆盖state不同，必须先做support matching。

## 16. Causal Confusion与Causal Dynamics

`Causal Confusion`说明demonstration中的nuisance correlate可让imitation held-out error低但部署失败；`Causal Dynamics Learning`说明dense dynamics可能用不必要依赖并在unseen state泛化差。[2][5]

它们支持“观测拟合不足以证明机制”，不直接证明某个VLA world model的root cause。

## 17. Structural counterfactual边界

`Woulda, Coulda, Shoulda`用SCM先从trajectory反推noise，再换action并保持同noise预测counterfactual；这依赖model、noise posterior与hidden-confounder假设。[3] 普通conditional generator换action后独立采样，不自动成为structural counterfactual model。

## 18. CausalWorld角色

CausalWorld暴露robot/environment/goal等causal variables与`do_intervention`接口，可构造controlled manipulation evaluation。[4] 它提供sim benchmark，不证明real effect或用户项目已运行。

## 19. 证据阶梯

| 层 | 证据 | 允许说 |
| --- | --- | --- |
| C0 | action tensor接入 | architecture conditioned |
| C1 | shuffle/sweep/Jacobian | model uses action |
| C2 | held-out \(p(y\mid x,a)\) | observational fit |
| C3 | cloned-state pairs | simulator do-effect aligned |
| C4 | cross-policy/context | effect更稳定 |
| C5 | real matched repeats | 指定hardware effect证据 |
| C6 | closed-loop+safety | 指定任务可用 |

## 20. 可审计伪代码

```python
def audit_action_effect(model, env, snapshots, action_pairs, protocol):
    records = []
    for snapshot in snapshots:
        # Restore the identical simulator/controller state and exogenous seed.
        base = env.restore(snapshot, seed=protocol.seed)
        obs = protocol.policy_observation(base)

        for action_a, action_b in action_pairs(base):
            # Close support, units, frame, clipping and executed-action semantics.
            pair = protocol.validate_and_transform(action_a, action_b, base)
            pred_a = model.rollout(obs, pair.model_a, protocol.horizon)
            pred_b = model.rollout(obs, pair.model_b, protocol.horizon)

            # Execute each action from the same restored state and seed.
            real_a = env.restore(snapshot, seed=protocol.seed).rollout(pair.env_a)
            real_b = env.restore(snapshot, seed=protocol.seed).rollout(pair.env_b)
            records.append(compare_effect(pred_a - pred_b, real_a - real_b,
                                          support=pair.support))
    return summarize_by_state_action_horizon(records)
```

真实机器人版本需matched reset/repeated safe trials，不能直接调用restore。

## 21. Matched evaluation

固定checkpoint、snapshots、action/controller transform、horizon、seed/repeats与metric，比较：no-action、observational conditioned、shuffle/zero、same-state pairs、cross-policy、nuisance intervention、support/OOD sweep和closed-loop planner。

同报observation/latent/reward/contact/termination effect、distribution calibration、support coverage、latency/compute与success/safety。

## 22. 高频诊断

| 症状 | 首查 |
| --- | --- |
| shuffle几乎无影响 | path/mask、history shortcut、narrow data |
| model有effect、env为零 | clip/deadband/controller、shortcut |
| effect符号相反 | axis/frame/unit/time、confounding |
| observational好、cloned差 | hidden state、policy shortcut、support |
| sim好、real差 | dynamics/contact/controller/camera gap |
| cross-policy漂移 | state不充分、policy ID leakage |
| planner选极端action | OOD exploitation、uncalibrated effect/value |

## 23. 项目挂钩与真实性边界

WAM/Cosmos支持action/future/value slot、action-conditioned future与planning contract；UWM支持action/video shared diffusion及action-free/action-present routes。当前没有cloned-state pairs、effect delta、cross-policy/support、measured executed action或real matched intervention。[6][7]

面试安全表达：

> 我把action-conditioned分成syntax、sensitivity、observational fit、sim intervention和real/closed-loop。WAM/UWM目前支持上游机制和部分sim protocol，但没有effect-alignment artifact，所以不称causal dynamics已验证。

## 24. 实战检查清单

- [ ] treatment是raw、approved还是executed action明确；
- [ ] state/history sufficiency与hidden confounder列出；
- [ ] action support/positivity与OOD gate明确；
- [ ] action shuffle/Jacobian只标sensitivity；
- [ ] snapshot/seed/action pair严格matched；
- [ ] predicted/env effect delta按unit/horizon对齐；
- [ ] stochastic outcome用distribution/repeats；
- [ ] cross-policy/nuisance intervention；
- [ ] simulator/real/closed-loop证据分层；
- [ ] public mechanism与personal evidence分开。

## 25. 参考来源

1. Oh et al., [Action-Conditional Video Prediction](https://arxiv.org/abs/1507.08750)。
2. de Haan et al., [Causal Confusion in Imitation Learning](https://arxiv.org/abs/1905.11979)。
3. Buesing et al., [Woulda, Coulda, Shoulda](https://arxiv.org/abs/1811.06272)。
4. Ahmed et al., [CausalWorld](https://arxiv.org/abs/2010.04296)。
5. Wang et al., [Causal Dynamics Learning](https://arxiv.org/abs/2206.13452)。
6. [WAM Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。

## 26. VOL 04 收口

`VLA-WM-001..044` knowledge/card已全部覆盖，但保持`WARN/unseen`；页面生成不是掌握或项目证据。下一步进入其他卷的首个source-ready缺口，不创建coaching state。
