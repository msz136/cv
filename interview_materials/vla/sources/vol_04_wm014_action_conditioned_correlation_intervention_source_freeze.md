# VOL 04 WM-014 Source Freeze：Action-conditioned Prediction、相关性与可干预 Dynamics

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-014 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-014  
> 本轮边界：只冻结“action进入模型”到“action effect与环境干预一致”的证据阶梯、观测条件分布与do-intervention差异、隐藏混杂/状态充分性/overlap/执行动作合同、cloned-state action-swap与matched evaluation；不声称仅凭action-conditioned loss即可识别因果dynamics，也不把公开方法写成本地WAM/UWM因果验证。

## 1. 冻结结论

1. action-conditioned只说明模型形式包含action：\(\hat y=f_\theta(x,a)\)。模型仍可能忽略action、利用behavior-policy shortcut，或在数据支持外随意外推。
2. 观测条件分布 \(p(y\mid x,a)\) 与干预分布 \(p(y\mid x,\operatorname{do}(a))\) 只有在state/history充分阻断混杂、action有overlap、标签与执行一致等假设下才可等同。
3. 若隐藏变量 \(u\) 同时影响policy选择action与未来outcome，观测数据会用 \(p(u\mid x,a)\) 混合结果；真正干预应保持 \(p(u\mid x)\)，两者不同。
4. action sensitivity或非零Jacobian只能证明模型对输入action有反应，不能证明反应方向、幅度、时序和物理后果正确。
5. 最强可重复验证是在相同simulator state/exogenous seed下执行多个action，比较模型与环境的counterfactual effect；真实机器人无法完美clone时，需要matched initial conditions、多次安全随机干预与置信区间。
6. VLA系统必须以**实际执行action**作为干预：policy output、denormalized command、controller setpoint与measured actuator motion必须分开，否则模型可能学的是command correlation而非physical consequence。
7. WAM/UWM公开结构支持action/future或action/video coupling，但当前本地证据没有same-state action intervention、effect-alignment或real counterfactual bundle，不能称causal/actionable dynamics已验证。

## 2. 一手来源与冻结快照

| ID | 来源 | 冻结版本与响应 SHA-256 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Oh et al., *Action-Conditional Video Prediction using Deep Networks in Atari Games* | arXiv `1507.08750`；ar5iv response `484d2f12defb0d3297b31bc5a83b99fec539a5db68843b10225f80fd5daafea1` | action-conditioned future prediction的建模范式 | 输入action即因果识别、机器人可干预性 |
| S2 | de Haan et al., *Causal Confusion in Imitation Learning* | arXiv `1905.11979`；ar5iv response `98767a4890019076caab95dd23ea7e7e6c0bc2b0d0d9468800c946ca72dc19ba` | demonstration中的nuisance/confounder、低held-out误差仍部署失败、intervention/expert解混杂思路 | world-model exact effect、任意offline data可识别 |
| S3 | Buesing et al., *Woulda, Coulda, Shoulda: Counterfactually-Guided Policy Search* | arXiv `1811.06272`；ar5iv response `74a19c6fa5cf253550576e2b05524e712e770cbd9a1a7a8e9f5b39be6183bc75` | structural causal model、abduction/action/prediction式counterfactual与hidden-confounder/inference假设 | 通用真实机器人counterfactual已可靠 |
| S4 | Ahmed et al., *CausalWorld* | arXiv `2010.04296`；ar5iv response `263b079fe7a2fdd6eaf2e3d8f5d2452d7386c19e915ec93759197f03a479b5ef` | robotic manipulation causal variables、do-interventions与transfer benchmark | simulator intervention等于real-world effect |
| S5 | Wang et al., *Causal Dynamics Learning for Task-Independent State Abstraction* | arXiv `2206.13452`；ar5iv response `bf64fbb272cf172253b4d58eeb2c14fb18e42d565f5aa7130d27837d0a4da858` | dense dynamics的spurious dependency、causal dependency/state abstraction与unseen-state generalization | 所有视觉world model都能恢复真实causal graph |
| S6 | action-conditioned official/author code | `junhyukoh/nips2015-action-conditional-video-prediction@a8f6545e9df65803227f83c65f926ddc54bff848`；README `885a5057b4d1f03043eddd7558edf11dfdb21d22f2395f78bfe780fdf720d467` | repo明确对应S1、action log与action-count输入 | current dependencies、causal effect |
| S7 | causal intervention code | `pimdh/causal-confusion@3c0d31601cdee160f12eaae0de4747ff5703d857`；README `b448d14c85f04466a08a0628e0273c5afe1b44fcbc89e3572915263e2c70f76d`；policy-execution intervention `f6f5aa1c76efcc452aad8abf3ce5e2a3427507ad788618f179d616c3e3a2f6e8` | repo对应S2并实现MountainCar graph-conditioned/intervention-by-policy-execution slice | 全论文环境、world dynamics或license完整性 |
| S8 | CausalWorld official code | `rr-learning/CausalWorld@1045277101a92c506db42704da28f6e7227d401b`；README `3a6394d32638306a7cd741e36c11f757ada78a717187708991381ce815f99e4c`；MIT LICENSE `446e7f9eef1cb8133ffbb5ce20e8bc7c0a99ce3b5bb38611789484c5f2435e5a` | exposed variables、`do_intervention`接口与counterfactual environment | real-hardware intervention |
| S9 | DreamerV3 frozen reimplementation | `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`；`rssm.py` SHA `d6d50166914e94fb8bd17a5d5dbda9d42cdd37b85819bb1e9fff3a64d4ad2eb6` | action确实进入RSSM `_core`，作为“syntactic conditioning”代码例 | action effect与环境一致、论文作者官方code |
| S10 | [Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html) | canonical SHA `bb48af7605688132ddd589109c8417dd0ebfe65f504a98cf5ab660f01e34ba7b` / `da16c172179cae926d329259e76955a55555fe53a15233f265d1f74a3d421ae4` | actionability、action-swap与local-evidence边界；WM-014可生成 | local causal validation |
| S11 | [WM-013 Multi-step](vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html) 与 [WM-020 Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html) | canonical SHA `9f2d68af1cec4c012f60f2c4e1e288e67b07953d9177c6c3171b0bf0d304a4e7` / `4053bb051296bcc785a3e1b7f7ddf0a0c75339dcb4f8c84aed755b49888c06dd` | multi-step与failure-probe去重边界 | causal claim已完成 |
| S12 | [WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories | canonical SHA `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d` / `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | project mechanism/protocol与缺失artifact | personal causal/action-intervention result |

## 3. “Action进入网络”只是什么证据

若模型写成：

\[
\hat y_{t+1}=f_\theta(x_t,a_t),
\]

只能证明函数签名接受action。还需逐级验证：

1. action path没有被mask/scale/shape bug破坏；
2. 输出对action有统计敏感性；
3. 预测的action effect与environment intervention方向/幅度一致；
4. 多步、OOD和closed-loop仍可用。

S1/S6是action-conditioned prediction的典型建模证据，但不提供第三、四层的通用保证。

## 4. Observational 与 interventional query

观测条件：

\[
p(y_{t+1}\mid x_t,a_t=a).
\]

干预条件：

\[
p(y_{t+1}\mid x_t,\operatorname{do}(a_t=a)).
\]

变量解释：conditioning是在日志中筛出“policy碰巧/决定采取a”的样本；`do(a)`是外部把action设为a并切断其原有policy生成机制。直觉是“看到做过a的人”不等于“让同一个状态执行a”。实现映射：日志训练通常给前者；cloned-state simulator或安全随机实验才能近似后者。

## 5. 隐藏混杂的积分差异

设隐藏变量 \(u_t\) 同时影响behavior policy的action与future outcome：

\[
p(y\mid x,a)
=\int p(y\mid x,a,u)\,p(u\mid x,a)\,du,
\]

\[
p(y\mid x,\operatorname{do}(a))
=\int p(y\mid x,a,u)\,p(u\mid x)\,du.
\]

变量解释：观测条件会因“谁/何时选择a”改变hidden-state mixture；干预固定action但不应改变pre-action \(u\) 分布。直觉是专家只在快碰撞时刹车，日志可能学到“刹车与碰撞相关”，并非刹车导致碰撞。实现映射：机器人中的 \(u\) 可是未观测接触、速度、operator意图、controller状态、遮挡或task phase。[S2][S3]

## 6. 什么时候两者可以相等

需要至少说明以下识别假设：

- **state/history sufficiency / conditional exchangeability**：给定 \(x_t\) 或belief/history后，潜在结果与action assignment无剩余混杂；
- **positivity/overlap**：每个关心的state附近，不同action都有非零支持；
- **consistency**：日志中标记的action与定义的intervention版本一致；
- **no interference / stable mechanism**：一个trial的action不改变另一个trial结果，环境机制在比较间稳定；
- **correct temporal order**：pre-action covariates不包含post-action变量或future leakage。

深度模型预测准确不会自动使这些假设成立。

## 7. Partial observability 是首要混杂来源

当前RGB \(o_t\) 往往缺速度、遮挡后对象、contact force、gripper load与controller integrator。behavior policy可能使用proprio/history/privileged state选action，但world model只看image；于是action携带hidden state信息，模型把action当“状态提示”，而不是物理干预。

检查：增加history/belief/proprio后，observational effect是否变化；在相同full simulator state下action swap；比较image-matched但hidden-state不同的pair。

## 8. Positivity / action support

若expert在某state只选一个action，则 \(p(y\mid x,\operatorname{do}(a'))\) 对未见 \(a'\) 不可从该日志直接识别。连续action更严重：有限trajectory只覆盖state-action manifold的窄邻域。

实现上记录state-conditioned action density、nearest-neighbor distance、ensemble/OOD score与safe support mask；support外prediction只能称外推，必须限险或补intervention data。

## 9. Commanded action不等于executed action

至少区分：

```text
policy raw action
  → denormalized / frame-converted command
  → clipped / shielded controller setpoint
  → actuator command
  → measured joint/EE motion and contact
```

若world target由measured motion产生，但condition只用raw command，delay、clip、shield与controller会成为hidden mediator/confounder。可干预dynamics应记录并选择清楚的treatment：nominal command、approved action还是executed physical motion。

## 10. Action ignoring 与 action shortcut不同

- **action ignoring**：改变action，模型输出几乎不变；常因narrow action distribution、history足以预测或action path bug。
- **action shortcut**：模型对action敏感，但action只是behavior-policy/task phase标签；在同state反事实action上effect错误。

前者可由shuffle/zero/Jacobian发现；后者必须通过同state environment intervention发现。

## 11. Sensitivity不等于causal alignment

模型局部敏感度：

\[
J_a(x,a)=\frac{\partial\,\mathbb E_\theta[Y\mid x,a]}{\partial a}.
\]

变量解释：\(J_a\) 量化模型输出对action的局部导数。非零只说明模型“使用action”；符号/尺度可能错误，且离散action、clip与contact处不可微。实现映射：用finite difference/action sweep，并与environment effect curve对齐，而不是单独报告gradient norm。

## 12. Conditional effect

对两个action：

\[
\tau(x;a,a')
=\mathbb E[Y\mid x,\operatorname{do}(a)]
-\mathbb E[Y\mid x,\operatorname{do}(a')].
\]

变量解释：\(Y\) 可是next pose、latent、reward、contact event或success。直觉是同一个pre-action context下只改变action的后果差。实现映射：连续action要明确delta、unit/frame、horizon与随机seed；不能用不同initial state的raw outcome差替代effect。

## 13. Effect-alignment error

对cloned simulator state \(s\)：

\[
\mathcal E_{\mathrm{effect}}
=\mathbb E_{s,a,a'}\left[
\left\|
(\hat Y_s(a)-\hat Y_s(a'))
-(Y_s^{\mathrm{env}}(a)-Y_s^{\mathrm{env}}(a'))
\right\|_W
\right].
\]

变量解释：\(W\) 可按position/orientation/contact/reward单位加权。直觉是比较“action改变了多少”，消除共同baseline bias。实现映射：保存snapshot/hash、exogenous seed、两action、predicted/actual outcomes、effect residual与validity；随机环境需多seed比较distribution而非一条sample。

## 14. Distributional intervention metric

随机/多模态环境应比较：

\[
\mathcal D\left(
p_\theta(Y\mid s,\operatorname{do}(a)),
p_{\mathrm{env}}(Y\mid s,\operatorname{do}(a))
\right),
\]

其中 \(\mathcal D\) 可是proper scoring rule、Wasserstein/MMD或任务定义距离。必须用matched random seeds或足够repeats估计aleatoric spread；单sample MSE不能区分随机未来与model error。

## 15. Cloned-state action-swap

最小simulator实验：

1. freeze full state、object/contact/controller state与random seed；
2. 给model相同可用observation/history；
3. 生成action pair：expert vs perturbed、positive vs negative、zero vs nonzero；
4. 从同snapshot分别执行；
5. 比较one-step与multi-steppose/contact/reward/termination effect；
6. 按action support、state family与horizon分层。

cloned simulator提供强干预证据，但只证明该simulator/controller contract，不证明real physics。

## 16. 真实机器人不能完美clone怎么办

使用matched初始条件与安全设计：

- fixture/jig/automatic reset减少state差；
- randomized small perturbation而非危险大action；
- 多次trial估计initial-state与outcome不确定性；
- pre-action sensor/contact/controller trace做matching/adjustment；
- hard safety gate、short prefix、fallback与operator approval；
- 报effect CI、invalid/reset failure与coverage。

不能把两个不同起点各跑一次的差叫counterfactual truth。

## 17. Negative controls

| Probe | 预期 | 暴露问题 |
| --- | --- | --- |
| zero action | 静态/惯性基线 | 模型凭时间预测 |
| action shuffle | prediction应显著变差 | action ignoring/数据泄漏 |
| sign/axis swap | effect方向应相应改变 | action order/frame shortcut |
| scale sweep | 与actuator/clip曲线一致 | 非物理线性外推 |
| impossible/out-of-support action | 高uncertainty/拒绝 | 过度自信 |
| nuisance intervention | physical effect尽量不变 | background/task-ID shortcut |

negative control失败不能直接定位root cause，但能否定“可干预dynamics已验证”的强claim。

## 18. Cross-policy invariance

用不同behavior policy收集相同environment dynamics：expert、random、安全扰动、recovery policy。真正transition mechanism在给定充分state/action后应较稳定；若 \(p_\theta(y\mid x,a)\) 随policy ID/数据配比大变，说明action携带policy/context shortcut或state不充分。

必须固定environment/controller revision，并显式记录policy mixture；不同policy访问不同state support时不能无调整比较。

## 19. Causal Confusion 提醒了什么

S2展示behavior cloning可能依赖与expert action相关但非causal的nuisance变量，即使training/held-out imitation error低，部署distribution shift仍失败；paper与S7讨论expert/intervention或policy execution帮助识别正确图结构。

映射到world model：低next-frame loss也可能来自policy/task/background correlation。该论文不直接证明某个world model错误，只支持“观测拟合不能替代干预验证”的方法边界。

## 20. Causal Dynamics Learning 提醒了什么

S5指出dense dynamics model容易使用state/action间不必要依赖并在unseen state泛化差，提出学习稀疏causal dependency/state abstraction。对WM-014的启示是：prediction graph越密不代表机制越真；需要dependency intervention、跨context稳定性与downstream effect。

不能把S5在特定simulated环境的理论/实验结果泛化成视觉VLA已恢复真实causal graph。

## 21. Counterfactual model 的假设

S3的counterfactually-guided policy search使用structural causal model，通过已观察trajectory反推noise，再修改action并预测结果；paper也明确讨论noise inference、model accuracy与hidden-confounder假设的限制。

因此“同一噪声下换action”的counterfactual比独立sampling更强，但前提是SCM/noise posterior可信。普通conditional generator随机换action不自动成为structural counterfactual model。

## 22. CausalWorld 的证据角色

S4/S8提供robotic manipulation simulator、exposed causal variables与`do_intervention`接口，可构造controlled environment/goal/robot/property changes和counterfactual-style evaluation。

它证明“如何建立可干预benchmark”，不证明在CausalWorld上通过的model能迁移real robot，也不证明user项目已经运行该benchmark。

## 23. 最小证据阶梯

| Level | Evidence | 允许说 | 不允许说 |
| --- | --- | --- | --- |
| C0 syntax | action tensor连入transition | action-conditioned architecture | 使用了action effect |
| C1 sensitivity | swap/Jacobian/shuffle | model output depends on action | effect正确 |
| C2 observational | held-out \(p(y\mid x,a)\) | data-distribution prediction好 | do-effect已识别 |
| C3 simulator intervention | cloned-state action pairs | simulator contract内effect aligned | real effect |
| C4 cross-policy/shift | 多policy/context稳定 | mechanism更稳健 | 任意OOD保证 |
| C5 real matched intervention | safe repeated real trials | 指定hardware/protocol effect证据 | 普遍因果模型 |
| C6 closed-loop | planning/control success + safety | 指定任务可用 | 所有内部变量都因果正确 |

## 24. 最小可审计伪代码

```python
def audit_action_effect(model, env, snapshots, action_pairs, protocol):
    records = []
    for snapshot in snapshots:
        # 1. Restore identical full simulator/controller state and exogenous seed.
        base = env.restore(snapshot, seed=protocol.seed)
        obs = protocol.policy_observation(base)

        for action_a, action_b in action_pairs(base):
            # 2. Verify support, units and the exact executed-action transform.
            pair = protocol.validate_and_transform(action_a, action_b, base)

            # 3. Query model outcomes while changing only the action.
            pred_a = model.rollout(obs, pair.model_a, horizon=protocol.horizon)
            pred_b = model.rollout(obs, pair.model_b, horizon=protocol.horizon)

            # 4. Execute both actions from the same restored state/seed.
            real_a = env.restore(snapshot, seed=protocol.seed).rollout(pair.env_a)
            real_b = env.restore(snapshot, seed=protocol.seed).rollout(pair.env_b)

            # 5. Compare effect deltas, not unmatched raw outcomes.
            records.append(compare_effect(pred_a - pred_b, real_a - real_b,
                                          support=pair.support))
    return summarize_by_state_action_horizon(records)
```

真实机器人版本不能直接restore，需改为matched reset/repeated safe trials并报告initial-state差异。

## 25. Matched evaluation

固定model/checkpoint、dataset、state snapshots、action transform/controller、horizon、random seed/repeats与metric：

| Arm | 目的 |
| --- | --- |
| no-action model | action信息增量 |
| conditioned observational | 标准held-out prediction |
| action shuffle/zero | ignoring/shortcut negative control |
| same-state action pairs | interventional effect alignment |
| cross-policy data | behavior-policy invariance |
| nuisance intervention | spurious context dependency |
| support/OOD sweep | positivity与uncertainty |
| closed-loop planner | effect是否带来控制收益 |

同报observation/latent/reward/contact/termination effect、distributional calibration、support coverage、latency/compute与closed-loop success/safety。

## 26. Failure-first 诊断

| 症状 | 首查 |
| --- | --- |
| action shuffle几乎不影响 | action path/mask、history shortcut、narrow data |
| model effect非零但env为零 | command clip/deadband、controller、shortcut |
| effect符号相反 | axis/frame/unit/time index、confounding |
| observational好、cloned差 | hidden state、policy shortcut、support不足 |
| simulator好、real差 | dynamics/contact/controller/camera gap |
| small action好、large action崩 | support、saturation、nonlinearity、uncertainty |
| cross-policy效果漂移 | state不充分、policy ID leakage、mixture shift |
| planning选极端action | OOD exploitation、uncalibrated effect/value |

## 27. 项目真实性边界

WAM/Cosmos可以讲action/future/value slot、action-conditioned future与planning contract；UWM可以讲action/video shared diffusion、action-free/action-present routes与LIBERO protocol。它们当前没有：

- cloned-state action-pair dataset；
- predicted-vs-environment effect delta；
- cross-policy/action-support audit；
- measured executed-action/controller trace；
- real matched intervention。

安全口径：

> 我会把action-conditioned分成syntax、sensitivity、observational fit、sim intervention与real/closed-loop五层。WAM/UWM目前支持前两层的上游机制和部分sim protocol，但没有effect-alignment artifact，所以我不会称其为causal dynamics已验证。

## 28. Claim ledger

| Claim | 来源 | 等级 | 状态 |
| --- | --- | --- | --- |
| action可作为future predictor输入 | S1/S6/S9 | primary + code | checked / syntax only |
| observational imitation/dynamics可利用spurious correlate | S2/S5 | primary | checked with scope |
| counterfactual prediction依赖SCM/noise inference/hidden-confounder假设 | S3 | primary | checked |
| CausalWorld提供robotic do-intervention接口 | S4/S8 | primary + official code | checked / sim only |
| cloned-state effect alignment是本节点验证设计 | S1–S12 synthesis | engineering design | WARN / needs execution |
| WAM/UWM已验证causal/action-interventional dynamics | S12 | missing local evidence | rejected |

## 29. 仍待独立复核与补证据

1. primary/code事实已复核，本节点独立事实复核仍标`PENDING`。
2. 需要local action path/mask/normalizer/controller trace与action shuffle/sweep。
3. 需要simulator snapshot+seed+action-pair+predicted/actual effect bundle。
4. 需要cross-policy/support/OOD、distributional repeats与same-protocol closed-loop结果。
5. real claim需要safe randomized/matched trials、measured action、initial-state trace、CI与safety approval。
6. 浏览器`file://` visual QA受策略阻断，只能做renderer/static/link validation。
7. 没有真实口述，不创建`coaching_state.md`，题卡保持`unseen`。

## 30. 参考来源

1. Oh et al., [*Action-Conditional Video Prediction using Deep Networks in Atari Games*](https://arxiv.org/abs/1507.08750), 2015。
2. de Haan et al., [*Causal Confusion in Imitation Learning*](https://arxiv.org/abs/1905.11979), NeurIPS 2019。
3. Buesing et al., [*Woulda, Coulda, Shoulda: Counterfactually-Guided Policy Search*](https://arxiv.org/abs/1811.06272), ICLR 2019。
4. Ahmed et al., [*CausalWorld*](https://arxiv.org/abs/2010.04296), 2020。
5. Wang et al., [*Causal Dynamics Learning for Task-Independent State Abstraction*](https://arxiv.org/abs/2206.13452), ICML 2022。
6. [Action-conditional code](https://github.com/junhyukoh/nips2015-action-conditional-video-prediction/tree/a8f6545e9df65803227f83c65f926ddc54bff848)、[Causal Confusion code](https://github.com/pimdh/causal-confusion/tree/3c0d31601cdee160f12eaae0de4747ff5703d857)、[CausalWorld code](https://github.com/rr-learning/CausalWorld/tree/1045277101a92c506db42704da28f6e7227d401b)。
7. [VOL 04 Source Audit A](vol_04_world_model_foundations_claim_to_code.html) 与 [独立事实复核](vol_04_world_model_foundations_independent_fact_review.html)。
8. [WM-013 Multi-step Consistency](vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html) 与 [WM-020 Failure Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html)。
9. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) evidence inventories。

## 31. VOL 04 收口

完成本节点后，VOL 04 `VLA-WM-001..044` 的44个knowledge/card节点全部覆盖；这只表示页面`drafted/WARN`，不表示独立事实复核、项目artifact或真实口述已完成。下一步转入全局剩余卷的首个source-ready缺口，不创建coaching state。
