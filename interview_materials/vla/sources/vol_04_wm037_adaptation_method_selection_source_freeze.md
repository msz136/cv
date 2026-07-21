# VOL 04 WM-037 Source Freeze：Residual Policy、Online Adaptation、Test-time SysID 与 Data Aggregation

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-037 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-037  
> 本轮边界：只冻结 adaptation 方法的“更新对象 × 时间尺度 × 数据/执行 authority × safety gate”选择合同；不提前展开 WM-038 uncertainty/safety/recovery 总课，不把 offline fine-tune、token rollout、simulator rollout 或公开论文机制写成个人真机 online adaptation 成果。

## 1. 冻结结论

1. “online adaptation”不是一个算法名；必须先说明更新的是 **action、context/latent、simulator distribution、dataset，还是 model weights**。
2. residual policy 适合“已有可靠 base controller、误差局部且 action interface 可闭合”的场景；它扩大的是 action authority，不自动继承 base 的稳定性保证。
3. UP-OSI 从 history 显式估计 dynamics parameter；RMA 从 history 估计 task-relevant latent。二者都可在部署时保持 policy weights 不变。
4. SimOpt 用少量 real trajectory 的 behavior discrepancy 更新 simulator-parameter distribution；它不是逐步控制器适配，也不等于精确物理参数辨识。
5. DAgger 执行当前/混合 policy、让 expert 标注访问状态、聚合数据并训练下一版 policy；它不是 rollout 内无门槛地改权重。
6. 若没有可靠 base、可观测 history、expert/reward、safe real rollout、回滚和 matched evaluation，就没有足够 authority 声称 real online adaptation。

## 2. 一手来源与冻结快照

| ID | Primary / official source | 冻结版本与快照 | 本节点支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Chebotar et al., *Closing the Sim-to-Real Loop: Adapting Simulation Randomization with Real World Experience* | arXiv `1810.05687v4`；ar5iv 2026-07-18 response SHA-256 `d655425962c13511caf54a1c669144793e0747366db9f9b48d0f0d5d58ca2391` | real/sim trajectory discrepancy、black-box simulator、KL-bounded distribution update | 不支持“识别出真实唯一参数”或无风险 real rollout |
| S2 | Yu et al., *Preparing for the Unknown: Learning a Universal Policy with Online System Identification* | arXiv `1702.02453v3`；ar5iv response SHA-256 `929c344cfa0c5c39f6010b79867c5d827bcd17634a004b87a543ee6c5f66aa5d` | universal policy + history-to-parameter OSI | 论文任务主要在 simulation；不支持个人真机验证 |
| S3 | Kumar et al., *RMA: Rapid Motor Adaptation for Legged Robots* | arXiv `2107.04034v1`；ar5iv response SHA-256 `4f09d9e44cb1726f4c2cae8cd90b35eed6d659199e53875c2420bccef42533b4` | privileged extrinsics encoder、history adaptation module、asynchronous deployment | legged state/action recipe 不自动适配 image-based VLA/manipulation |
| S4 | Johannink et al., *Residual Reinforcement Learning for Robot Control* | arXiv `1812.03201v2`；ar5iv response SHA-256 `5b0bc192221a41824801d96b76644ee61cd41b9a46482f933de5938ba9fe42df` | conventional controller + learned residual、真实 contact-rich assembly | 不提供任意 residual 的通用 stability/safety guarantee |
| S5 | Ross et al., *A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning* | PMLR 15 official page response SHA-256 `e515cc08883fb65a967c7cc1cd4905107d7dc31aeed4a71c254ea250a670ad75`；official PDF SHA-256 `17bdd6e049e64f09010b322f9e2d4fb5c744c33ff7ac99b4c4561e39bd9082a7` | DAgger learner-state collection、expert labels、dataset aggregation、retraining | sequence/IL theorem不自动提供真机安全或低标注成本 |
| S6 | [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html) | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | 方法初始对比、SimOpt/residual 公式和真实性边界 | 不是本地 adaptation 运行证据 |
| S7 | [Evidence Manifest](../evidence/evidence_manifest.html) | canonical SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6` | 五项目证据分级与缺口 | 不支持未归档的真机/在线更新成果 |
| S8 | [OPD Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | canonical SHA-256 `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb` | student token rollout + teacher forward 的本地机制边界 | 不是 robot-state DAgger 或 Sim2Real adaptation |
| S9 | [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | canonical SHA-256 `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | offline finetune、sim rollout、protocol/failure instrumentation | 不是 test-time SysID、residual 或 real hardware update |
| S10 | [OpenPiVLA Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | canonical SHA-256 `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293` | action/controller/rollout partial provenance | 不支持 local real adaptation 或 matched uplift |

## 3. 先问：究竟更新什么

| 方法族 | rollout/test-time 改变量 | policy weights 当场改变？ | 典型时间尺度 | 必要监督/authority |
| --- | --- | --- | --- | --- |
| bounded residual | executed action correction (r_t) | 通常否 | control step | reliable base + action/safety limits |
| explicit OSI | physical parameter estimate \(\hat\mu_t\) | 否 | step/window/episode | parameter labels in sim + informative history |
| latent adaptation / RMA | task-relevant latent \(\hat z_t\) | 否 | fast window | privileged latent teacher + on-policy history |
| SimOpt | simulator distribution \(p_\phi(\xi)\) | rollout 内否 | real batch / outer loop | safe real trajectories + sim/real discrepancy |
| DAgger | aggregated dataset \(D\)，随后训练 \(\pi_{i+1}\) | interaction 内通常否 | collection/training iteration | expert labels on learner-visited states |
| online weight fine-tune | model parameters \(\theta\) | 是 | batch/episode/stream | trusted reward/label + replay + rollback |

同一句“模型在线适配了”可能对应完全不同的风险面。面试回答必须先给更新对象、频率、数据来源和回滚点。

## 4. 两条选择轴：data authority 与 actuation authority

定义：

- **data authority**：能否获取 real trajectory、expert label、reward、privileged parameter、intervention/failure；
- **actuation authority**：方法能把多大的修正写入真实 controller/action，是否有 dimension mask、norm/rate/energy limit 与 fallback。

没有 data authority 时不能做 real-data adaptation；没有 actuation safety 时不能让 residual/新 policy 任意接管。方法“模型能力强”不能替代这两条合同。

## 5. Residual policy：局部补偿，不是重做全部控制

Residual RL 的公开结构是 conventional controller 与 learned residual 的 superposition：[S4]

\[
u_t=\operatorname{clip}_{\mathcal U}
\left(u_{base}(s_t)+M_r\,r_\phi(h_t)\right).
\]

变量解释：\(u_{base}\) 是已验证 base controller，\(r_\phi\) 是 residual，\(M_r\) 是允许 residual 作用的 dimension/scale mask，\(\mathcal U\) 是动作可行域。直觉是 base 负责已建模部分，residual 只补局部误差。实现映射：记录 base action、raw/scaled residual、sum 前后 action、clip/saturation、controller output 与 fallback event。\(M_r\) 和 safety limits 是本节点的工程 gate，不是 S4 的通用稳定性定理。

适用前提：base 已有可接受成功率/安全边界；action 的 frame/unit/order/frequency 闭合；误差可由有限 residual authority 修正。若 base interface 本身错误，residual 只会学习补偿 bug。

## 6. Explicit OSI：估计有语义的 dynamics parameter

UP-OSI 使用近期 state/action history 预测 dynamics parameter，再把估计与 state 一起输入 universal policy：[S2]

\[
\hat\mu_t=f_\psi(h_t),
\qquad
u_t=\pi_\theta(s_t,\hat\mu_t),
\qquad
h_t=(s_{t-L:t},u_{t-L:t-1}).
\]

变量解释：\(\mu\) 是 mass/friction/inertia 等有语义参数，\(L\) 是 history window；\(\theta,\psi\) 可在 deployment 固定。直觉是先判断“当前系统像哪个 dynamics”，再由 universal policy 条件化控制。实现映射：保存 history schema/timestamps、\(\hat\mu_t\)、sim label、parameter range、prediction residual、policy input 和 stale-window 标志。

高风险点是 identifiability：若 excitation 不足，不同 \(\mu\) 可能生成相近 trajectory；显式参数可解释，不代表估计必然是真值。

## 7. Latent adaptation / RMA：估计任务相关 extrinsics

RMA 两阶段训练先用 privileged environmental factors \(e_t\) 生成 latent extrinsics，再用 on-policy state/action history 预测该 latent：[S3]

\[
z_t=\mu(e_t),
\qquad
\hat z_t=\phi(h_t),
\qquad
u_t=\pi_\theta(s_t,u_{t-1},\hat z_t).
\]

变量解释：\(z_t\) 不要求逐维对应真实物理参数，只需保留 action-relevant information；\(\phi\) 是 adaptation module。直觉是“不必恢复世界真值，只要估计足够控制的上下文”。实现映射：训练时保存 privileged latent target 与 on-policy history，部署时保存 latent age、update frequency、staleness、OOD score 和 base-policy frequency。

RMA 公布的 A1 部署中 base policy 100 Hz、adaptation module 10 Hz 且异步运行；这些是该平台实例，不是 VLA/manipulation 默认值。[S3]

## 8. Test-time SysID 不等于 test-time training

若 deployment 时只更新 \(\hat\mu_t\) 或 \(\hat z_t\)，而 \(\theta,\psi\) 固定，这是 **inference-time context estimation**，不是 gradient-based weight update。必须分别记录：

1. context estimator weights/version；
2. history window、sampling clock 与 missing/stale rule；
3. inferred parameter/latent 与 confidence/OOD；
4. policy weights 是否改变；
5. reset/episode boundary 是否清空 context。

把 RMA/OSI 说成“在线微调模型”是概念错误。

## 9. SimOpt：outer-loop simulator distribution adaptation

SimOpt 用 fixed policy 的 real/sim observable trajectories 建 discrepancy，并通过 black-box sampling 更新 simulator parameter distribution；论文使用 KL-bounded relative-entropy update。[S1]

\[
\phi_{k+1}=\arg\min_\phi
\mathbb E_{\xi\sim p_\phi}
\left[D\!\left(\tau^{obs}_{sim}(\xi),\tau^{obs}_{real}\right)\right]
\quad
\text{s.t. }D_{KL}(p_\phi\Vert p_{\phi_k})\le\epsilon.
\]

变量解释：\(\xi\) 是 simulator parameter，\(D\) 是 observable trajectory discrepancy，\(\epsilon\) 限制一次 distribution shift。直觉是让“仿真行为分布”逐轮接近 real，而非强求唯一真实参数。实现映射：每轮冻结 policy/checkpoint、real trajectory、observation projection、distance metric、sampled \(\xi\)、cost、old/new distribution 和 reject reason。

SimOpt 的 update 在 real-collection 外循环发生；若每次同时换 policy、controller、distance 与 task，就无法归因 distribution update。

## 10. DAgger：修正 learner-induced state distribution

DAgger 处理 imitation learning 中 expert-demonstration distribution 与 learner-induced distribution 的偏移。原论文算法为：[S5]

\[
\pi_i=\beta_i\pi^*+(1-\beta_i)\hat\pi_i,
\qquad
D\leftarrow D\cup\{(s,\pi^*(s)):s\sim d_{\pi_i}\},
\qquad
\hat\pi_{i+1}=\operatorname{Train}(D).
\]

变量解释：\(\pi^*\) 是 expert，\(\beta_i\) 是 expert mixing，\(d_{\pi_i}\) 是当前混合 policy 诱导的 state distribution。直觉是“让 learner 去到自己会去的状态，再请 expert 标答案”。实现映射：保存 rollout policy/mixing、visited state ID、expert label/intervention、dataset lineage、sampling weight、train checkpoint 和 validation selection。

这不等于把失败 episode 无条件追加后继续训：必须有可靠 label、去重/权重、train/eval separation、版本化 lineage 与安全 collection gate。

## 11. Online weight fine-tune：最高风险 authority

直接在 deployment stream 更新 \(\theta\) 会同时改变 representation、policy output 与历史数据依赖。本节点只给工程边界，不把它绑定到某一篇论文的保证：

- trusted reward/label 和 corruption/replay guard；
- immutable base checkpoint、optimizer/replay snapshot；
- shadow/canary → limited authority → rollout gate；
- update norm、KL/action drift、holdout regression；
- rollback trigger、max update/real-step budget、incident log。

若这些条件不满足，优先收集数据后离线更新，而不是在真机 rollout 内自由改权重。

## 12. 方法选择矩阵

| 当前条件 | 首选方向 | 为什么 | 必须先排除 |
| --- | --- | --- | --- |
| reliable base；局部 contact/actuator residual | bounded residual | 保留 base 分工，修正局部误差 | frame/unit/timing bug、base 已不安全 |
| 参数有语义、sim 可标、history 可辨识 | explicit OSI | 可解释 \(\hat\mu\)，policy 条件化 | excitation 不足、parameter aliases |
| hidden factors 快变、物理参数难辨、latent teacher 可建 | RMA-style latent | task-relevant context，不追求物理真值 | history/timing/OOD、跨域结构照搬 |
| 少量 safe real trajectories；想改 simulator distribution | SimOpt | outer-loop behavior matching | 不可比 observation、unsafe collection |
| expert 能标 learner-visited states | DAgger | 直击 compounding error/state shift | 无 expert、无 intervention gate、label latency |
| reward/labels 稳定且可 rollback；需广泛改 policy | staged fine-tune | 改变能力范围最大 | live uncontrolled update、forgetting |

方法可以组合，但应按单因素 gate 逐步叠加；不要一开始同时 residual + latent + DAgger + weight update。

## 13. 时间尺度合同

必须分开记录：

- control loop：base/residual action；
- context loop：OSI/RMA estimate；
- episode loop：reset、context warmup、calibration probe；
- collection loop：real trajectory/expert label；
- training loop：dataset aggregation、policy update；
- deployment loop：shadow/canary/promote/rollback。

异步模块要记录 estimate age；没有 timestamp 时，“适配慢”与“controller 错”不可区分。

## 14. Adaptation evidence ladder

1. `mechanism_read`：能解释公开方法；
2. `interface_replay`：离线 history/context/action replay；
3. `sim_matched`：同 checkpoint adaptation on/off；
4. `shadow_real`：真机只估计/预测，不接管；
5. `limited_authority_real`：小 residual/latent gate；
6. `protocol_complete_real`：多任务/seed、数据预算、安全与回滚；
7. `deployment_claim`：持续监控、incident/rollback 与 ownership 完整。

低层证据不能替代高层。公开 RMA/Residual RL 结果只支持公源机制，不提升个人 evidence ladder。

## 15. 必须保存的 trace / manifest

- base/adaptation/residual/policy checkpoint 与 optimizer/replay version；
- observation/action/controller schema、unit/frame/order/frequency；
- history window、timestamp、missing/stale/reset/warmup；
- \(\hat\mu_t/\hat z_t\)、confidence/OOD、oracle target（若有）；
- base/raw residual/final action、mask/scale/clip/saturation；
- real trajectory ID、expert label/intervention、reward/success predicate；
- SimOpt old/new distribution、sample/cost/KL/rejection；
- DAgger dataset lineage、dedupe、sample weight、train/eval split；
- safety gate、fallback、E-stop、rollback、incident/failure family；
- real steps、expert queries、interventions、wall time 与 compute/data budget。

## 16. Matched evaluation 合同

固定 task/init/seed、base checkpoint、camera/action/controller、horizon/replan、hardware/simulator build、success predicate 与 trial denominator：

| family | minimum matched arms | 关键指标 |
| --- | --- | --- |
| residual | base / base+bounded residual / authority sweep / stale-OOD stress | success、residual norm/rate、clip、fallback |
| OSI/RMA | no context / oracle context / inferred context / stale-corrupted history | success、estimate error、latent age、OOD |
| SimOpt | nominal distribution / updated distribution / over-update / held-out real trajectory | discrepancy、KL、real steps、transfer metric |
| DAgger | BC base / equal-budget DAgger rounds / no-new-state control | success、expert queries、interventions、coverage |
| fine-tune | immutable base / staged update / replay-anchor ablation / rollback test | uplift、regression、drift、incident |

跨 family 比较还要报告 real-step、expert-label、compute 与 safety cost；不等预算的最高 success 不能直接归因“方法更好”。

## 17. 选择与执行伪代码

```python
def choose_and_gate_adaptation(contract, evidence, method):
    # 1. Freeze base policy, controller, action schema, task protocol and data budget.
    run = freeze_run_manifest(contract, evidence)

    # 2. Reject methods whose required authority or supervision is absent.
    if not required_inputs_available(method, run):
        return reject("missing_data_or_actuation_authority", run)

    # 3. Start with shadow/offline replay; do not grant real action authority immediately.
    shadow = evaluate_shadow_or_replay(method, run, log_context_and_residual=True)
    if not shadow.within_contract:
        return reject("shadow_contract_failed", shadow)

    # 4. Run method-specific matched arms under a fixed real/expert/data budget.
    matched = run_limited_authority_matched_arms(method, run, shadow)

    # 5. Promote only if task gains, safety, drift and rollback gates all pass.
    return promote_or_rollback(matched, run.promotion_gates)
```

伪代码重点是先判 authority、再 shadow、再有限接管、最后 promotion/rollback；它是 S1–S10 的工程综合，不是某篇论文的原始算法。

## 18. 项目真实性边界

当前本地证据支持：

- UWM/LIBERO 有 offline finetune、simulator closed-loop rollout、protocol 和 failure instrumentation；
- OpenPiVLA 有 action/controller/rollout partial provenance；
- OPD 有 student token rollout、同一 response 的 teacher forward 与数据/训练 lineage。

当前不支持：

- 任何项目实现 residual controller、UP-OSI/RMA、SimOpt 或 robot-state DAgger；
- 真机 test-time parameter/latent estimation、在线权重更新或 safety promotion；
- real adaptation uplift、expert intervention budget、rollback/incident 或 ownership 完整记录。

尤其要说清：OPD 的“online student-rollout”是 VLM token-space 蒸馏机制，不是机器人在线 system ID 或 DAgger；UWM 的 task finetune 是训练阶段离线更新，不是 rollout 中 adaptation。[S7–S10]

## 19. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| residual = base controller + learned correction | S4 | primary | checked |
| UP-OSI = history→physical parameter→universal policy | S2 | primary | checked with simulation scope |
| RMA = privileged latent teacher + history adaptation module | S3 | primary | checked with legged-platform scope |
| SimOpt 用 real/sim trajectory discrepancy 更新 simulator distribution | S1 | primary | checked |
| DAgger 聚合 learner-visited state 的 expert labels 后重训 | S5 | peer-reviewed primary | checked |
| authority/timescale/trace/matched matrix | S1–S10 + engineering synthesis | synthesis | WARN / needs execution |
| 用户项目已完成真机 online adaptation | S7–S10 | missing local evidence | rejected |

## 20. 面试答题骨架

安全答案应包含四句：

1. 先说更新对象和时间尺度；
2. 有可靠 base、局部误差选 bounded residual；参数可解释选 OSI，参数不可辨但 history 有信息选 latent adaptation；
3. 少量安全 real trajectory 调 simulator distribution 选 SimOpt；有 expert label 修 learner-state shift 选 DAgger；
4. 所有方法先 shadow/limited authority，报告 real steps、expert queries、drift、fallback、rollback；当前项目没有真机 bundle，不声称完成 adaptation。

## 21. 仍待独立复核与补证据

1. 五篇一手来源已复核，source freeze 保持 `independent_fact_review=PENDING`。
2. 需要 local adaptation implementation、history/context/residual trace 与 matched sim arms。
3. 若要升级到 real claim，需要 safe collection、expert/reward provenance、intervention/incident、rollback 和 protocol-complete trials。
4. 需要真实口述后才更新题卡状态；不得创建 `coaching_state.md`。
5. 浏览器本地 `file://` 若受策略阻断，只记录静态验证，不能写 visual PASS。

## 22. 参考来源

1. Chebotar et al., [*Closing the Sim-to-Real Loop: Adapting Simulation Randomization with Real World Experience*](https://arxiv.org/abs/1810.05687v4), 2019.
2. Yu et al., [*Preparing for the Unknown: Learning a Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3), 2017.
3. Kumar et al., [*RMA: Rapid Motor Adaptation for Legged Robots*](https://arxiv.org/abs/2107.04034v1), 2021.
4. Johannink et al., [*Residual Reinforcement Learning for Robot Control*](https://arxiv.org/abs/1812.03201v2), 2018.
5. Ross, Gordon and Bagnell, [*A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning*](https://proceedings.mlr.press/v15/ross11a.html), PMLR 15, 2011.
6. [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html).
7. [Evidence Manifest](../evidence/evidence_manifest.html).
8. [OPD Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html).
9. [UWM/LIBERO Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html).
10. [OpenPiVLA Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html).

## 23. 下一边界

下一 bounded slice 是 `VLA-WM-038`：uncertainty-aware planning、安全约束、fallback 与 recovery policy 如何形成最小闭环。本页不提前展开 chance constraint、risk critic、E-stop 或 recovery-state-machine 总课。
