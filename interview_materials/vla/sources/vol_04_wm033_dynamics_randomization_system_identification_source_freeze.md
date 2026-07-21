# VOL 04 WM-033 Source Freeze：Dynamics Randomization 与 System Identification

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-033 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-033  
> 本轮边界：只冻结 dynamics randomization 与 system identification 的互补关系、参数分类、range provenance、相关性/可辨识性、采样合同、matched evaluation 和项目真实性边界；不提前展开 WM-034 latency/controller mismatch、WM-036 contact 机制课或 WM-037 online adaptation 方法课，也不声称任何个人项目已经完成真机 Sim2Real。

## 1. 一页结论

1. **System identification（SysID）和 dynamics randomization（DR）解决的问题不同。**SysID 用真实或台架轨迹缩小 nominal model 的系统性偏差，并给出拟合残差/置信区域；DR 在这一中心附近覆盖 measurement error、未建模项、设备差异、环境差异和时变漂移。[S1][S3]
2. **准确 nominal model 不能替代分布训练。**Tan et al. 同时使用 system identification、learned actuator model、latency simulation 与 randomization；其消融显示，model discrepancy 过大时，仅靠随机扰动不足以弥合 gap。[S3]
3. **宽分布也不能替代辨识。**SimOpt 明确指出 overly wide distribution 会包含不可行场景、阻碍训练或产生过度保守策略；range 必须有 target-support 依据和 rollback gate。[S4]
4. **range 不是统一的 ±x%。**每个参数要记录 name、unit、site、nominal、lower/upper、distribution、source、confidence、correlation、sampling cadence、validity rule 和 stress/nominal role。
5. **不可辨识不等于随便放宽。**若不同参数组合产生近似轨迹，只能报告 task-relevant equivalence set；可改用 history-conditioned explicit OSI、implicit recurrent adaptation 或 behavior-matching distribution update，但不能把 latent/behavior match 说成恢复了真实物理参数。[S1][S2][S4]
6. **正参数、相关参数和时变参数要区别采样。**mass/friction/gain 通常不应由无界 Gaussian 产生负值；mass–inertia、battery–motor strength、control step–latency 等关系不能默认独立；episode-level 常量与 step-level jitter 也不能混为一谈。[S1][S3]
7. **最终证据必须是 matched transfer ladder。**固定 checkpoint lineage、训练预算、task set、controller 和 rollout protocol，比较 nominal、SysID-only、DR-only、SysID+DR、overwide；分 nominal sim、parameter sweep、real replay/free-space、contact/task closed-loop 报告 first failure。
8. **本地项目证据不足以形成个人 DR/SysID 成果。**当前仓库没有同时存在 parameter manifest、real excitation trace、fit report、sampler audit、matched arms、真机闭环结果与 ownership；只能回答设计方案与证据需求。[S5][S8]

## 2. 冻结来源与可支持边界

| ID | 一手来源 / 本地证据 | 冻结版本与快照 | 本节点可支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Peng et al., *Sim-to-Real Transfer of Robotic Control with Dynamics Randomization* | arXiv:1710.06537v3；ar5iv response SHA-256 `29d5e90f2a01e918bacb9d2a3e31622fc68018063be2bece6d86d2e0fca8a1b3` | episode-level parameter sampling、step-level timing/noise、95-parameter case、history-conditioned implicit SysID、real pushing demonstration | 95 个参数和论文 range 是所有机器人默认配置；其 real result 是用户项目结果 |
| S2 | Yu et al., *Preparing for the Unknown: Learning a Universal Policy with Online System Identification* | arXiv:1702.02453v3；ar5iv response SHA-256 `929c344cfa0c5c39f6010b79867c5d827bcd17634a004b87a543ee6c5f66aa5d` | universal policy conditioned on dynamics parameter；recent state/action history→explicit OSI；训练域外与突变测试 | 论文的 simulation 结果等于真实机器人验证；估计参数必然是物理真值 |
| S3 | Tan et al., *Sim-to-Real: Learning Agile Locomotion for Quadruped Robots* | arXiv:1804.10332v2；ar5iv response SHA-256 `c34db6210074989010a635a11705e17da4a38d4b105e471159a9cc832a120a49` | measurement/SysID、actuator model、latency、actual measurement plus small margin、robustness–optimality trade-off | Minitaur 的数值范围可直接复制到 manipulation/VLA；locomotion transfer 证明用户项目 transfer |
| S4 | Chebotar et al., *SimOpt* | arXiv:1810.05687v4；ar5iv response SHA-256 `d655425962c13511caf54a1c669144793e0747366db9f9b48d0f0d5d58ca2391` | real/sim observation-trajectory discrepancy、KL-constrained distribution update、overwide/infeasible/conservative 风险、无需 exact replication | 少量 real rollout 没有安全/成本；behavior matching 等于 exact SysID |
| S5 | [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html) | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | 六层 gap、SysID+DR、range、adaptation 与 truth boundary 的已有审计 | 审计设计等于本地实现或真机结果 |
| S6 | [WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html) | canonical SHA-256 `d25897218b4a276a0d9a981c826e8680ba21db7e64b298963eace10184877a97` | dynamics/contact/control 层与 first-failure ladder | taxonomy 已完成参数辨识 |
| S7 | [WM-032 Visual DR Source Freeze](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html) | canonical SHA-256 `9086b6072047f3578cb731f48f08c48b509d7d38924b801728039b83d6245710` | relevant support、range provenance、validity/rejection、overwide/SimOpt 边界 | visual factor 合同自动证明 dynamics factor 合同 |
| S8 | [Evidence Manifest](../evidence/evidence_manifest.html) 与项目 inventories | manifest SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6` | 当前项目证据缺口与可安全表述 | 缺失 artifact 可由报告文本替代 |

## 3. 核心定义：点估计、残余不确定性与训练分布

设 simulator dynamics 为

\[
x_{t+1}=f(x_t,u_t;\xi)+\varepsilon_t,
\]

其中 \(x_t\) 是状态，\(u_t\) 是 controller 接收的动作，\(\xi\) 是 mass、inertia、damping、actuator、friction、latency 等参数，\(\varepsilon_t\) 包含未建模扰动与观测/过程噪声。

SysID 用真实数据 \(D_r=\{x_t,u_t,x_{t+1}\}\) 找到点估计或后验：

\[
q(\xi\mid D_r)\propto p(D_r\mid\xi)p_0(\xi).
\]

变量解释：\(p_0\) 是 CAD、datasheet 或历史平台给出的 prior；\(p(D_r\mid\xi)\) 衡量 simulator/模型在参数 \(\xi\) 下复现实测轨迹的能力。工程实现可以是 least squares、trajectory matching、Bayesian fit 或 learned actuator model；若只有点估计，也必须保留 fit residual 和 data coverage。

DR 在训练时从一个可审计分布采样：

\[
\xi_e\sim p_\phi(\xi),\qquad
\theta^*=\arg\max_\theta\mathbb E_{\xi_e\sim p_\phi}\left[J(\pi_\theta;f_{\xi_e})\right].
\]

变量解释：\(e\) 表示 episode；\(p_\phi\) 不应是无依据的大盒子，而应由 \(q(\xi\mid D_r)\)、跨设备/物体差异、时变漂移、结构误差和安全 stress policy 组成。该目标只证明在训练分布上的平均性能，不证明真实系统一定在 support 内。[S1][S4]

因此互补关系是：

\[
\text{SysID: reduce bias / locate support}
\quad + \quad
\text{DR: cover residual uncertainty / variation}.
\]

这是一条工程综合结论，而不是“先拟合一次就知道真实参数”的承诺。

## 4. 参数必须先分型，再决定是否辨识或随机化

| 参数类型 | 例子 | 首选处理 | 原因与风险 |
| --- | --- | --- | --- |
| 可直接测量、近似固定 | link mass、几何尺寸、gear ratio | measurement/CAD 设中心，小 residual range | 大范围随机会浪费容量或生成不物理样本 |
| 可通过激励轨迹拟合 | damping、motor response、latency、joint friction | offline SysID + fit confidence | 激励不足会出现参数共线与假精确 |
| 跨设备/物体变化 | payload、object mass/COM、surface friction | population/conditioned distribution | 不能把不同 object/surface 混成一个无条件 global range |
| 运行中漂移 | battery、temperature、wear、queue delay | time/context-conditioned range；必要时 online adaptation | 只在 episode 起点采样无法覆盖 step-level drift |
| 难辨识或强耦合 | contact、compliance、backlash、unmodeled actuator | task-relevant latent/behavior set + bounded DR | 单个“真值”可能不存在或不可观测 |
| 结构/离散不确定性 | controller mode、solver/contact model、gripper semantics | 分支模型或 protocol gate | 不能用连续微扰掩盖接口语义错误 |

WM-033 只规定选择逻辑；latency 的多时钟细节留给 WM-034，contact 参数与 gripper semantics 留给 WM-036，online adaptation 比较留给 WM-037。

## 5. Range provenance：不是抄论文百分比

### 5.1 中心和残差

对连续参数 \(\xi_j\)，先保存 nominal \(\hat\xi_j\)，再分解不确定性来源：

\[
\delta_j=
\delta_j^{measure}+
\delta_j^{fit}+
\delta_j^{population}+
\delta_j^{drift}+
\delta_j^{model}.
\]

变量解释：measurement 是仪器/标定误差，fit 是 trajectory residual，population 是不同机器人/物体/表面差异，drift 是温度/电量/磨损/时延变化，model 是 simulator 结构误差。实现时不要机械相加成“统计置信区间”；应分别记录来源、估计方法、样本数和保守 margin，再由 safety owner 审批最终 support。

一种可审计的初始化是：

\[
[l_j,u_j]=Q_{\alpha/2,1-\alpha/2}\big(q(\xi_j\mid D_r)\big)
\oplus \Delta_j^{population}
\oplus \Delta_j^{drift}
\oplus m_j^{safety},
\]

其中 \(Q\) 是 posterior/bootstrapped fit 的分位数，\(\oplus\) 表示工程上的有界扩张而非概率卷积，\(m_j^{safety}\) 是有来源的 margin。若没有 posterior，至少以 bootstrap、held-out trajectory residual 或 repeated measurement 给出区间。

### 5.2 正值与尺度

mass、friction magnitude、gain 等正参数可在 log space 采样或使用 truncated distribution：

\[
\log \xi_j\sim\mathcal U(\log l_j,\log u_j),\qquad 0<l_j<u_j.
\]

Peng et al. 对部分参数使用 logarithmic sampling，但其 range 是特定 Fetch pushing setup 的 case study，不能成为通用默认值。[S1]

### 5.3 相关性与条件化

独立 box sampling \(p(\xi)=\prod_j p(\xi_j)\) 容易生成不可能组合。应至少冻结：

- mass、COM 与 inertia 来自同一个 body-property sample；
- battery/temperature 与 motor strength、response、current limit 相关；
- control period、compute/network queue 与 effective latency 相关；
- object identity 与 mass/COM/friction/compliance 条件化；
- surface identity 与 friction/contact 参数条件化；
- controller mode 与 gain/action semantics 作为离散分支，而不是连续噪声。

### 5.4 采样频率

| cadence | 适合参数 | 典型错误 |
| --- | --- | --- |
| build/robot-level | link geometry、gear ratio、sensor mount | 每 step 改 mass，生成非物理动力学 |
| episode-level | payload、object mass、constant friction regime、motor scale | episode 内偷偷换参数但 policy 无可观测线索 |
| segment/event-level | grasp 后 payload、surface transition、mode switch | 不记录 transition time，无法复现 |
| step-level | sensor noise、small jitter、queue delay fluctuation、disturbance | 把所有参数都当 i.i.d. noise，破坏时间相关性 |

Peng et al. 明确区分 episode-level mass/damping 等参数与 step-level action timestep/noise，说明 cadence 是 dynamics contract 的一部分。[S1]

## 6. 可辨识性：fit 好不等于参数真

令模型输出轨迹特征为 \(y(\xi)\)，局部 sensitivity matrix 为

\[
S_{ij}=\frac{\partial y_i}{\partial \xi_j}\Big|_{\hat\xi}.
\]

若某列接近零，当前 excitation 对该参数不敏感；若多列高度共线，不同参数组合可能产生近似轨迹。此时即使 training trajectory error 很小，也不能声称每个 \(\hat\xi_j\) 是物理真值。

最小审计：

1. excitation 覆盖 free-space、不同速度/负载和必要的安全 contact regime；
2. train/held-out trajectory 分开，报告 state/action/torque/time strata；
3. 检查 sensitivity、bootstrap spread、parameter correlation 和 multi-start fit；
4. 做 parameter intervention：单独改变候选参数，看预测/真实 response 是否按假设变化；
5. 对不可辨识组保存 equivalence set 或 task-relevant latent，不制造虚假的单点真值。

UP-OSI 显式预测 dynamics parameters；Peng et al. 则指出复杂系统中手工指定 runtime 参数集合可能困难，并用 recurrent memory 隐式汇总 history。两者说明“解释性参数”和“task-relevant adaptation state”是不同合同。[S1][S2]

## 7. 四种组合方式与边界

| 方法 | 训练/运行合同 | 适用条件 | 主要风险 |
| --- | --- | --- | --- |
| offline SysID only | fit \(\hat\xi\)，只在 nominal sim 训练 | 设备稳定、模型充分、任务窄 | 对 residual/漂移脆弱，fit dataset leakage |
| fixed calibrated DR | 从 measured/fit range 采样 | real rollout authority 低，但有测量/台架数据 | support miss、独立采样污染、过度保守 |
| explicit OSI + universal policy | history→\(\hat\xi_t\)，policy 条件化参数 | 参数语义可定义且可从 history 识别 | estimate OOD、参数共线、simulation-only validation |
| behavior-matching distribution update | real trajectory discrepancy→更新 \(p_\phi\) | 有少量安全 real rollout 与可比较 observation | discrepancy shortcut、unsafe collection、不是 exact SysID |

SimOpt 的重点是更新 simulation parameter distribution，使 policy-induced observation trajectories 更接近真实轨迹，并用 KL trust region 限制更新；它不要求 exact replication，也不能取消 real rollout 的安全 gate。[S4]

## 8. Range expansion、rejection 与 rollback

每次 revision 只能在有证据时扩大：

1. **support miss**：真实 trace 落在当前 posterior/range 外；
2. **boundary failure**：held-out parameter sweep 在边界显著退化；
3. **population/drift evidence**：新设备、负载、表面、温度或电量出现；
4. **model residual**：结构误差可用 bounded nuisance parameter 近似，且不污染任务语义。

以下情况应拒绝或回滚：

- mass/inertia/contact 组合违反物理约束；
- simulator unstable、penetration/explosion 或 controller 饱和；
- task 在采样参数下不可解，但被混入 nominal training；
- nominal performance 明显下降而 target/held-out 没有收益；
- real discrepancy 下降仅来自观测缩放、时间对齐或 metric shortcut；
- distribution 更新超出 policy trust region 或安全 authority。

可将 nominal 与 stress 分开：

\[
p_{train}(\xi)=(1-\rho)p_{cal}(\xi)+\rho p_{stress}(\xi),
\]

其中 \(p_{cal}\) 是有 target-support 依据的 calibrated distribution，\(p_{stress}\) 是边界测试分布，\(\rho\) 必须记录。stress score 不得与 nominal transfer score 混报。

## 9. Matched 实验矩阵

固定 dataset states、train steps、optimizer、network、init/checkpoint、seed set、controller、task set、rollout count、success predicate 和 logging，至少比较：

| arm | nominal model | fitted model | residual DR | 目的 |
| --- | --- | --- | --- | --- |
| A | baseline | no | no | 记录未校准基线 |
| B | fitted center | yes | no | SysID-only 的 bias reduction |
| C | baseline center | no | yes | DR-only 是否只是用宽分布硬扛 |
| D | fitted center | yes | yes | 检验互补收益 |
| E | fitted center | yes | overwide | 观察 conservative/optimization cost |

每个 arm 分层报告：

- nominal sim return/tracking error；
- one-factor sensitivity sweep 与 correlated holdout；
- held-out robot/object/surface/latency strata；
- real replay/free-space tracking；
- 若有 authority，再做 protocol-complete closed-loop success/CI、first failure 与 safety events。

只有 D 相对 B/C 在 matched target gate 上稳定更好，且 E 没有伪造优势，才能支持“SysID 与 DR 互补”的本地因果主张。

## 10. 最小 artifact bundle

| Artifact | 必须字段 | 能证明 | 不能单独证明 |
| --- | --- | --- | --- |
| `dynamics_parameter_manifest` | name/unit/site/nominal/range/distribution/source/correlation/cadence/validity/revision | 参数合同存在 | range 正确、transfer 成功 |
| `sysid_dataset_manifest` | robot/object/surface、excitation、timestamp、sensor/action/controller、split、安全限制 | 辨识数据可追溯 | 参数可辨识 |
| `fit_report` | objective、optimizer、multi-start、train/heldout residual、bootstrap/correlation | fit 过程与不确定性 | 物理真值 |
| `sampler_audit` | seed、draw、accept/reject reason、boundary cases、correlation tests | 实际采样符合合同 | policy 已鲁棒 |
| `matched_ablation` | A–E arms、固定项、seed、checkpoint lineage、sim/real protocol | 方法因果比较 | 未执行的真机结果 |
| `real_gate` | authority、limits、E-stop、trial protocol、trace、success/failure | 真机验证可审计 | 跨平台泛化 |
| `ownership_ledger` | 谁测量、谁拟合、谁改 sampler、谁训练/评估 | 个人贡献边界 | 技术效果本身 |

## 11. 注释伪代码：calibrated DR pipeline

```python
def build_calibrated_dynamics_distribution(real_dataset, parameter_contract):
    # 1. Validate units, controller semantics, timestamps and excitation coverage.
    checked = validate_sysid_dataset(real_dataset, parameter_contract)

    # 2. Fit a nominal parameter vector with multiple starts; keep held-out residuals.
    fit = fit_nominal_dynamics(checked.train, multistart=True)
    residual = evaluate_trajectory_fit(fit, checked.holdout)

    # 3. Estimate uncertainty by bootstrap/repeated measurements; do not invent precision.
    uncertainty = estimate_uncertainty(fit, checked, residual)

    # 4. Combine fit uncertainty, population variation and drift with sourced margins.
    distribution = construct_bounded_distribution(
        nominal=fit.parameters,
        uncertainty=uncertainty,
        correlations=parameter_contract.correlations,
        cadence=parameter_contract.sampling_cadence,
    )

    # 5. Reject negative, inconsistent, unstable or task-unsolvable samples and log why.
    accepted, rejected = audit_sampler(distribution, parameter_contract.validity_rules)
    return distribution, fit, residual, accepted, rejected


def matched_transfer_study(base_config, distribution, safe_real_authority=None):
    # 1. Keep data, compute, initialization, controller and eval protocol identical.
    arms = make_arms(["baseline", "sysid_only", "dr_only", "sysid_plus_dr", "overwide"])

    # 2. Train and evaluate nominal, one-factor and correlated held-out simulations.
    results = train_and_evaluate_matched(arms, base_config, distribution)

    # 3. Real trials are optional and require explicit limits, E-stop and trace authority.
    if safe_real_authority is not None:
        results.real = run_guarded_real_trials(results.checkpoints, safe_real_authority)

    # 4. Expand or roll back ranges only from documented support/failure evidence.
    return decide_distribution_revision(results)
```

## 12. 项目真实性边界

对 `interview_materials/vla/evidence/`、OpenPiVLA inventory、WAM artifact manifest 与已有 Sim2Real audit 的检索，没有发现可闭合 WM-033 的本地 bundle：

- 没有 real robot/object/surface 的 parameter inventory 与单位；
- 没有 excitation trajectory、controller/timestamp contract 和 train/held-out split；
- 没有 fit residual、bootstrap/correlation 或 identifiability report；
- 没有实际 randomization sampler draw/rejection ledger；
- 没有 SysID-only / DR-only / combined / overwide matched arms；
- 没有 protocol-complete real closed-loop result 与 ownership ledger。[S5][S8]

安全表达：

- 可以说：“我会先做 parameter contract 与可辨识性审计，用 measurement/fit residual 建 calibrated distribution，再做 matched transfer ladder。”
- 可以说：“现有项目证据支持 simulator/action/eval contract 的讨论，但没有完成 dynamics SysID/DR 的本地结果闭环。”
- 不能说：“我通过 dynamics randomization 提升了真机成功率”“我辨识了真实机器人动力学”“SimOpt 已在项目中收敛”，除非补齐上述 artifact。

这遵循 C0–C3 evidence contract：设计理解不自动升级为 C2 本地优化，更不能升级为 C3 transfer 结果。

## 13. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| SysID 与 DR 互补而非替代 | S1、S3、S4 | primary synthesis | checked |
| measured center + residual/variation range 比盲目宽分布更可审计 | S3、S4 | primary + engineering synthesis | checked with scope |
| explicit OSI 使用 recent state/action history 估计 dynamics parameter | S2 | primary | checked |
| recurrent memory 可隐式汇总 dynamics history | S1 | primary | checked |
| overwide distribution 可能 infeasible/conservative | S4 | primary | checked |
| parameter correlations、cadence、validity 必须入 manifest | S1、S3 + engineering synthesis | synthesis | WARN / needs local execution |
| 用户项目已完成 dynamics SysID/DR transfer | S8 | missing local evidence | rejected |

## 14. 仍待独立复核与补证据

1. 一手论文机制已复核；source freeze 仍保持 `independent_fact_review=PENDING`，避免自写自证。
2. 需要真实 parameter manifest、measurement/excitation data、fit report、sampler audit 与 matched arms。
3. 需要真实口述后才更新练习状态；本节点不得创建 `coaching_state.md`。
4. 浏览器本地 `file://` 导航若继续被策略阻断，只能记录静态验证，不能写 visual PASS。

## 15. 参考来源

1. Peng et al., [*Sim-to-Real Transfer of Robotic Control with Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3), 2018。
2. Yu et al., [*Preparing for the Unknown: Learning a Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3), 2017。
3. Tan et al., [*Sim-to-Real: Learning Agile Locomotion for Quadruped Robots*](https://arxiv.org/abs/1804.10332v2), 2018。
4. Chebotar et al., [*Closing the Sim-to-Real Loop: Adapting Simulation Randomization with Real World Experience*](https://arxiv.org/abs/1810.05687v4), 2019。
5. [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html)。
6. [WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。
7. [WM-032 Visual DR / Relevant Support](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)。
8. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 16. 下一边界

下一 bounded slice 是 `VLA-WM-034`：control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real。本页不提前展开多时钟公式、queue/stale action 或 controller mode 细节。
