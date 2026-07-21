# VOL 04 World Model / Sim2Real：Adaptation Method Selection（WM-037）

> 状态：drafted / VLA-WM-037 / knowledge_39_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择？  
> 前置：[WM-033 Dynamics DR / SysID](vol_04_world_model_sim2real_wm033_dynamics_randomization_system_identification.html)、[WM-034 Timing / Controller](vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)、[WM-037 Source Freeze](../sources/vol_04_wm037_adaptation_method_selection_source_freeze.html)。

## 1. 面试结论

选择方法前先回答四件事：

1. 更新对象：action、parameter/latent、sim distribution、dataset 还是 weights；
2. 更新节奏：control step、history window、episode、collection batch 还是 deployment；
3. data authority：有没有 real trajectory、expert label、reward、privileged target；
4. actuation authority：能否 shadow、限幅、fallback、rollback。

有可靠 base 且误差局部，选 bounded residual；参数有语义且可辨识，选 explicit OSI；参数难辨但 history 包含 task-relevant signal，选 RMA-style latent；少量安全 real trajectory 想调 simulator distribution，选 SimOpt；expert 可标 learner states，选 DAgger。直接在线改 weights 风险最高，应最后考虑。

## 2. “Online”有五种不同含义

| 说法 | 真正改变的对象 | rollout 内改 weights？ |
| --- | --- | --- |
| residual control | final action | 通常否 |
| test-time OSI/RMA | parameter/latent context | 否 |
| SimOpt | 下一轮 simulator distribution | 否 |
| DAgger | aggregated dataset 与下一版 policy | interaction 内通常否 |
| online fine-tune | policy/model weights | 是 |

把它们都叫“在线微调”会同时混淆算法、证据和安全责任。

## 3. Residual policy

\[
u_t=\operatorname{clip}_{\mathcal U}
\left(u_{base}(s_t)+M_r r_\phi(h_t)\right).
\]

变量解释：\(u_{base}\) 是可靠 base controller，\(r_\phi\) 是 learned correction，\(M_r\) 控制维度和幅度，\(\mathcal U\) 是可执行域。直觉是 base 管已知部分，residual 只补未建模的局部误差。实现映射：日志必须同时保存 base、raw/scaled residual、sum、clip/saturation、controller output 和 fallback；Residual RL 公开工作支持 superposition 与真实 contact-rich assembly，但不提供任意 residual 的稳定性保证。[1]

选择条件：base interface 已闭合；误差局部；residual 能被 dimension/norm/rate/energy limit 约束。若 action frame/unit/timing 错，先修合同，不让 residual 学 bug。

## 4. Explicit online system identification

\[
\hat\mu_t=f_\psi(h_t),
\qquad
u_t=\pi_\theta(s_t,\hat\mu_t),
\qquad
h_t=(s_{t-L:t},u_{t-L:t-1}).
\]

变量解释：\(\hat\mu_t\) 是有物理语义的 dynamics estimate，\(L\) 是 history window；deployment 时 \(\theta,\psi\) 可保持固定。UP-OSI 的直觉是 universal policy 先在多种 dynamics 上学会条件控制，OSI 再从近期 state/action history 推断当前参数。[2]

适合 mass/friction/payload 等参数定义稳定、sim 能给 label、history 有 excitation 的场景。风险是 identifiability：多组参数可能产生相近 trajectory，预测值可解释不等于是真值。

## 5. RMA-style latent adaptation

\[
z_t=\mu(e_t),
\qquad
\hat z_t=\phi(h_t),
\qquad
u_t=\pi_\theta(s_t,u_{t-1},\hat z_t).
\]

变量解释：\(e_t\) 是训练期 privileged environmental factors，\(z_t\) 是 task-relevant extrinsics，\(\phi\) 从 on-policy history 预测 \(\hat z_t\)。直觉是“不恢复完整物理真值，只恢复足以选动作的上下文”。实现映射：保存 privileged target、history schema、latent age、frequency、stale/OOD 与 policy frequency。[3]

RMA 的 A1 实例中 base 100 Hz、adaptation 10 Hz 且异步；这是平台事实，不是 manipulation/VLA 默认。图像 VLA 还要处理视觉 history、camera latency 和 action chunk，不能直接照搬 state-based legged recipe。

## 6. Test-time SysID 不是 test-time training

如果 rollout 时只更新 \(\hat\mu_t\) 或 \(\hat z_t\)，policy/estimator weights 不变，这叫 context inference。必须分别回答：

- weights 是否改变；
- history 多长、什么频率、是否含 controller state；
- episode reset/warmup 如何处理；
- latent/parameter 多久更新一次，过期怎么办；
- OOD/confidence 低时回退到哪一版 policy。

“用了 RMA，所以在线微调网络”是危险答案。

## 7. SimOpt

\[
\phi_{k+1}=\arg\min_\phi
\mathbb E_{\xi\sim p_\phi}
\left[D\!\left(\tau^{obs}_{sim}(\xi),\tau^{obs}_{real}\right)\right]
\quad
\text{s.t. }D_{KL}(p_\phi\Vert p_{\phi_k})\le\epsilon.
\]

变量解释：\(p_\phi(\xi)\) 是 simulator-parameter distribution，\(D\) 是 real/sim observable-trajectory discrepancy，\(\epsilon\) 限制更新幅度。直觉是让仿真行为分布靠近真实行为，不要求找到唯一真实参数。实现映射：每轮冻结 policy、real trajectory、observation projection、distance、sampled parameters、cost、old/new distribution 与 KL/rejection。[4]

SimOpt 适合能安全重复少量 real rollout、但 simulator 参数难以直接量测的场景。它是 batch outer loop；同时换 policy/controller/metric 会破坏归因。

## 8. DAgger / data aggregation

\[
\pi_i=\beta_i\pi^*+(1-\beta_i)\hat\pi_i,
\qquad
D\leftarrow D\cup\{(s,\pi^*(s)):s\sim d_{\pi_i}\},
\qquad
\hat\pi_{i+1}=\operatorname{Train}(D).
\]

变量解释：\(\pi^*\) 是 expert，\(d_{\pi_i}\) 是 learner/mixed policy 诱导的 state distribution，\(\beta_i\) 是 expert mixing。直觉是让 learner 暴露自己的 off-distribution 状态，再请 expert 标注。实现映射：记录 rollout policy、visited-state ID、expert label/intervention、dataset lineage、dedupe/weight、train/eval split 与下一 checkpoint。[5]

只有失败视频、没有 expert action/reward，不构成 DAgger label；盲目追加失败轨迹可能复制错误 action。

## 9. 什么时候才考虑在线改 weights

只有同时具备以下条件：

- reward/label 可信且可审计；
- immutable base checkpoint 和 optimizer/replay snapshot；
- replay anchor 与 holdout regression；
- shadow/canary、update norm/KL/action drift gate；
- real-step/update budget、rollback trigger 与 incident log。

否则先收集、离线训练、严格验收，再发布新版本。在线权重更新不是“适应能力更强”的免费升级。

## 10. 决策树

1. 无 real execution/data authority：只做 calibrated DR、sim/offline replay；
2. reliable base + 局部 residual：bounded residual；
3. 参数语义稳定且可辨识：explicit OSI；
4. hidden factors 快变且物理参数难辨：latent adaptation；
5. 少量 safe real trajectory、目标是更新 simulator support：SimOpt；
6. expert 能标 learner-visited states：DAgger；
7. 可靠 reward/label、回滚与 regression 都有：再评估 staged weight update。

方法组合要逐层 gate，先做单因素，再做 combined；不能四种方法同时上后只报 success。

## 11. 时间尺度与 stale context

| loop | 典型对象 | 必记字段 |
| --- | --- | --- |
| control | base/residual/final action | timestamp、norm、clip、controller output |
| context | \(\hat\mu/\hat z\) | window、age、confidence/OOD、reset |
| episode | warmup/calibration probe | init、probe、fallback |
| collection | real trajectory/expert label | budget、intervention、failure |
| training | dataset/distribution/weights | lineage、delta、checkpoint |
| deployment | promote/rollback | gate、incident、version |

context estimator 与 policy 异步时，必须保存 latent age；否则 estimate 对但来晚了，与 estimate 本身错误无法区分。

## 12. 证据阶梯

1. 公开机制理解；
2. offline history/context/action replay；
3. sim adaptation on/off matched test；
4. real shadow estimate，不接管；
5. limited-authority real；
6. protocol-complete real；
7. deployment/monitoring/rollback。

论文机制、sim score 或离线 finetune不能直接跳到第 6–7 级。

## 13. Matched evaluation

| family | arms | 不能漏的成本/风险指标 |
| --- | --- | --- |
| residual | base / bounded residual / authority sweep / stale-OOD | residual norm/rate、clip、fallback |
| OSI/RMA | no context / oracle / inferred / stale-corrupted history | estimate error、latent age、OOD |
| SimOpt | nominal / updated / over-update / held-out real | discrepancy、KL、real steps |
| DAgger | BC / equal-budget rounds / no-new-state control | expert queries、interventions、coverage |
| fine-tune | base / staged update / replay ablation / rollback test | regression、drift、incident |

固定 base checkpoint、task/init/seed、camera/action/controller、horizon、success predicate 与 trial denominator。跨 family 还要匹配或报告 real-step、expert-label 与 compute budget。

## 14. 选择伪代码

```python
def adaptation_gate(contract, evidence, method):
    # 1. Freeze base/controller/schema/protocol and method-specific data budget.
    run = freeze_manifest(contract, evidence)

    # 2. Reject when required labels, trajectories, history or action limits are absent.
    if not has_required_authority(method, run):
        return reject("missing_authority", run)

    # 3. Validate offline/shadow before granting action or weight-update authority.
    shadow = replay_or_shadow(method, run, log_context_residual=True)
    if not shadow.passes:
        return reject("shadow_failed", shadow)

    # 4. Run fixed-budget matched arms, then promote only with rollback ready.
    matched = limited_authority_matched_test(method, run, shadow)
    return promote_or_rollback(matched, run.gates)
```

核心顺序是 authority → replay/shadow → limited authority → matched gate → promote/rollback。

## 15. 高频诊断

| 症状 | 首查 |
| --- | --- |
| residual 经常 clip | base/interface 错、authority 过小/过大、distribution shift |
| \(\hat\mu\) 漂但 action 不变 | policy 忽略 context、参数不可辨、scale/mask 错 |
| latent 突然失效 | history schema/timestamp/reset/OOD/stale |
| SimOpt discrepancy 下降但 task 变差 | metric shortcut、observation projection、support collapse |
| DAgger 数据增多但回归 | label quality、state coverage、weight/dedupe、old-task forgetting |
| online update 短期涨、长期崩 | replay不足、optimizer drift、reward shortcut、无 rollback |

## 16. 项目挂钩与真实性边界

当前项目可支持的只到：

- UWM/LIBERO：offline finetune、sim rollout、protocol/failure instrumentation；
- OpenPiVLA：action/controller/rollout partial provenance；
- OPD：student token rollout + teacher forward 的训练机制。

它们不支持 residual、UP-OSI/RMA、SimOpt、robot-state DAgger 或真机 online weight update。特别是 OPD 的“online”发生在 VLM token rollout，不是 robot learner-state collection；UWM finetune 发生在训练阶段，不是 test-time adaptation。[6][7][8]

安全回答：

> 我会先明确更新对象和 authority。有可靠 base 且误差局部才用 bounded residual；history 能辨识物理参数用 OSI，不能辨识但有 task-relevant signal 用 latent adaptation；少量安全 real trajectory 调 simulator distribution 用 SimOpt；有 expert action 才谈 DAgger。当前项目只有离线 finetune、仿真 rollout 与 token rollout 证据，所以不声称做过真机 online adaptation。

## 17. 实战审计清单

- [ ] 更新对象、频率、weights 是否变化明确；
- [ ] base/controller/action schema 与 safety limit 固定；
- [ ] history window/timestamp/reset/stale/OOD 完整；
- [ ] residual/context/distribution/dataset/weight delta 可追溯；
- [ ] real trajectory/expert/reward provenance 与预算完整；
- [ ] shadow→limited authority→matched→promote/rollback；
- [ ] adaptation on/off/oracle/stale/over-update 对照；
- [ ] real steps、expert queries、interventions、incident 一起报告；
- [ ] offline/token/sim rollout 不写成真机 adaptation；
- [ ] ownership 与 C0–C3 evidence 对齐。

## 18. 参考来源

1. Johannink et al., [*Residual Reinforcement Learning for Robot Control*](https://arxiv.org/abs/1812.03201v2)。
2. Yu et al., [*Preparing for the Unknown: Learning a Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3)。
3. Kumar et al., [*RMA: Rapid Motor Adaptation for Legged Robots*](https://arxiv.org/abs/2107.04034v1)。
4. Chebotar et al., [*Closing the Sim-to-Real Loop*](https://arxiv.org/abs/1810.05687v4)。
5. Ross et al., [*A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning*](https://proceedings.mlr.press/v15/ross11a.html)。
6. [WM-037 Source Freeze](../sources/vol_04_wm037_adaptation_method_selection_source_freeze.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)。
8. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) evidence inventories。

## 19. 下一节点

下一节点是 `VLA-WM-038`：uncertainty-aware planning、安全约束、fallback 与 recovery policy 如何形成最小闭环。本节点保持 WARN，题卡在真实口述前保持 unseen。
