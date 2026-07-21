# VOL 04 World Model / Sim2Real：Dynamics Randomization 与 System Identification（WM-033）

> 状态：drafted / VLA-WM-033 / knowledge_35_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：dynamics randomization 与 system identification 如何互补，参数范围怎样确定？  
> 前置：[WM-031 Reality-gap Taxonomy](vol_04_world_model_sim2real_wm031_reality_gap_taxonomy.html)、[WM-032 Visual DR](vol_04_world_model_sim2real_wm032_visual_domain_randomization_relevance.html)、[WM-033 Source Freeze](../sources/vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)。

## 1. 面试结论

一句话：**SysID 把 simulator 拉到真实系统附近，DR 覆盖仍然存在的误差、变化与漂移；range 从 measurement/fit uncertainty/population/drift/structural residual 来，不从论文百分比或“越宽越好”来。**

一个强回答应同时包含：

1. 参数合同：name/unit/site/nominal/range/distribution/source/correlation/cadence/validity；
2. SysID：real excitation、fit、held-out residual、uncertainty 与 identifiability；
3. DR：围绕 calibrated center 覆盖 residual，而不是替代建模；
4. range：测量、拟合、跨设备/物体、漂移和结构误差；
5. evaluation：baseline / SysID-only / DR-only / combined / overwide 的 matched arms；
6. truth boundary：没有本地 artifact 就只讲设计，不讲个人 transfer 结果。

## 2. 直觉：准星与散布

可以把 SysID 看成“把准星校到靶心附近”，DR 看成“训练时覆盖仍可能出现的散布”。只有 SysID，policy 可能对 fit dataset 很准，但换 payload、surface、battery、temperature 或 queue delay 就失败；只有 DR，中心偏差很大时会浪费训练容量，甚至把不物理/不可解场景混进训练。

Tan et al. 的 quadruped 案例同时使用 system identification、actuator model、latency simulation 与 randomization；SimOpt 则明确提醒 overly wide distribution 可能 infeasible 或 conservative。[1][2]

## 3. 数学合同

真实/模拟 dynamics 可写为：

\[
x_{t+1}=f(x_t,u_t;\xi)+\varepsilon_t.
\]

变量解释：\(x_t\) 是状态，\(u_t\) 是 controller 实际接收的动作，\(\xi\) 是 mass、inertia、friction、actuator、latency 等参数，\(\varepsilon_t\) 是未建模扰动与噪声。实现映射：必须先确认 controller/action/timestamp contract，否则 fit 到的“参数”可能只是在吸收接口错误。

SysID 用真实数据 \(D_r\) 得到 nominal 或 posterior：

\[
q(\xi\mid D_r)\propto p(D_r\mid\xi)p_0(\xi).
\]

变量解释：\(p_0\) 来自 CAD、datasheet、称重/标定或历史平台，likelihood/fit loss 衡量 simulator 与真实轨迹差异。实现映射：保存 train/held-out trajectory、multi-start、bootstrap 和 parameter correlation；只有点估计时也要报告残差。

DR 训练目标为：

\[
\xi_e\sim p_\phi(\xi),\qquad
\theta^*=\arg\max_\theta
\mathbb E_{\xi_e\sim p_\phi}[J(\pi_\theta;f_{\xi_e})].
\]

变量解释：\(p_\phi\) 是训练参数分布，\(e\) 是 episode。实现映射：sampler 必须把 source、seed、draw、accept/reject、cadence 和 revision 写入 ledger。这个式子只保证训练分布期望，不保证真实参数在 support 内。

## 4. 二者怎样互补

| 只做什么 | 得到什么 | 典型失败 |
| --- | --- | --- |
| nominal simulator | 一个方便训练的模型 | 系统性偏差未校准 |
| SysID only | 更接近 real trace 的中心/模型 | residual、跨设备差异与漂移未覆盖 |
| DR only | 对指定分布更鲁棒 | 中心错、分布过宽、无关/不可行样本 |
| SysID + calibrated DR | bias reduction + residual coverage | 仍需验证 support、相关性与真实闭环 |

Peng et al. 在模拟中随机化多类 dynamics，并用 recurrent history 隐式适应；UP-OSI 则显式用 recent state/action history 估计 dynamics parameter，再条件化 universal policy。两者都不意味着任意宽 DR 可以替代真实测量。[3][4]

## 5. 参数先分型

| 类型 | 例子 | 怎么处理 |
| --- | --- | --- |
| 可测且近似固定 | mass、geometry、gear ratio | 测量/CAD 设中心，小范围覆盖误差 |
| 可通过激励拟合 | damping、motor response、latency | offline SysID + held-out residual |
| population variation | object mass/COM、surface friction、不同 robot unit | 条件化或分层 distribution |
| time-varying | battery、temperature、wear、queue jitter | time/context-conditioned range；必要时 adaptation |
| 难辨识/强耦合 | contact、compliance、backlash | equivalence set、task-relevant latent、bounded DR |
| 结构/离散 | controller mode、gripper semantics、solver model | 分支/protocol gate，不用连续噪声掩盖 |

## 6. Range 怎样确定

### 6.1 五类来源

对每个参数分开记录：

\[
\delta_j=delta_j^{measure}+delta_j^{fit}+delta_j^{population}+delta_j^{drift}+delta_j^{model}.
\]

- `measure`：仪器、称重、标定、datasheet tolerance；
- `fit`：trajectory fit residual、bootstrap spread；
- `population`：不同 robot、payload、object、surface；
- `drift`：temperature、battery、wear、latency jitter；
- `model`：未建模 actuator/contact/solver effect 的 bounded proxy。

这里的“+”是来源分解，不是无条件把最大误差相加。每一项要保留样本、方法和置信度。

### 6.2 初始 support

\[
[l_j,u_j]=Q_{\alpha/2,1-\alpha/2}(q(\xi_j\mid D_r))
\oplus\Delta_j^{population}
\oplus\Delta_j^{drift}
\oplus m_j^{safety}.
\]

变量解释：\(Q\) 是 posterior/bootstrap 分位数，\(\oplus\) 是有依据的 bounded expansion，\(m_j^{safety}\) 是审批过的 margin。实现映射：manifest 要保存各边界的 source，不只保存最终数字。

### 6.3 正值与分布形状

正参数不能被无界 Gaussian 采成负值。可用 truncated distribution，或在 log space 采样：

\[
\log\xi_j\sim\mathcal U(\log l_j,\log u_j),\quad 0<l_j<u_j.
\]

Peng et al. 的部分参数采用 logarithmic sampling，但其 95-parameter 和具体 range 只属于 Fetch pushing case，不是模板。[3]

## 7. 不要默认独立采样

错误写法是 \(p(\xi)=\prod_j p(\xi_j)\) 然后对所有参数独立 uniform。常见相关性包括：

- mass、COM、inertia 来自同一个 body-property sample；
- battery/temperature 与 motor strength、response、current limit 相关；
- control period、network/queue 与 effective latency 相关；
- object identity 与 mass/COM/friction/compliance 相关；
- surface identity 与 friction/contact 相关。

若数据不足以拟合 joint distribution，至少使用条件规则、correlation matrix、copula/low-rank latent 或 rejection constraints，不能装作独立盒子就是现实分布。

## 8. 采样 cadence 是 dynamics 的一部分

| cadence | 例子 | 审计点 |
| --- | --- | --- |
| robot/build-level | link geometry、gear ratio | 一个 robot unit 内保持一致 |
| episode-level | payload、object、constant friction regime | reset 时采样并写 episode manifest |
| segment/event-level | grasp 后 payload、surface transition | 记录切换事件和可观测线索 |
| step-level | sensor noise、small timing jitter、disturbance | 保留时间相关性，避免全 i.i.d. |

Peng et al. 区分 episode-level physical parameters 与 step-level timestep/noise；把 mass 每 step 随机改变会生成非物理系统。[3]

## 9. Fit 好为什么仍可能错

定义 sensitivity matrix：

\[
S_{ij}=\frac{\partial y_i}{\partial \xi_j}\Big|_{\hat\xi},
\]

其中 \(y\) 是可观测 trajectory feature。某列近零说明当前 excitation 看不到该参数；多列共线说明多个参数组合效果相似。实现映射：做 multi-start fit、bootstrap、parameter correlation、held-out trajectory 和单参数 intervention。

因此必须区分：

- `prediction fit`：轨迹预测误差小；
- `parameter identification`：参数在当前实验下可辨识；
- `task-relevant equivalence`：参数不唯一，但对 policy 行为足够；
- `transfer`：在 matched real protocol 下闭环成功。

四者不能互相替代。

## 10. Explicit OSI、implicit adaptation 与 SimOpt

| 方式 | 输入→输出 | 结论边界 |
| --- | --- | --- |
| UP-OSI | recent state/action history→\(\hat\xi_t\)→universal policy | 参数必须有定义且可从 history 识别；论文主要 simulation |
| recurrent implicit SysID | history→memory/latent→action | latent 可 task-relevant，但不一定对应物理真值 |
| SimOpt | real/sim observation trajectory discrepancy→更新 \(p_\phi\) | 学 distribution，不要求 exact replication；需要 safe real rollout |

WM-033 只说明它们与参数分布的关系；online adaptation 的系统选择留给 WM-037。

## 11. Range 扩展与回滚

扩展 range 需要至少一种证据：真实 trace 超出 support、held-out boundary failure、新设备/负载/表面/温度数据，或可验证的结构残差。以下情况要 reject/rollback：

- 物理约束或相关性被破坏；
- simulator/controller unstable 或 task 不可解；
- nominal performance 下降但 target gate 无收益；
- discrepancy 下降来自 time alignment/scaling shortcut；
- update 超出 policy trust region 或 real safety authority。

nominal 与 stress 可用 mixture 分开：

\[
p_{train}=(1-\rho)p_{cal}+\rho p_{stress}.
\]

变量解释：\(p_{cal}\) 是 target-supported calibrated distribution，\(p_{stress}\) 是边界测试，\(\rho\) 是明确记录的比例。实现映射：nominal score 和 stress score 分栏报告，不能混成一个成功率。

## 12. 最小 matched ablation

固定 data、compute、network、init、seed、controller、task、rollout count、success predicate 和 checkpoint lineage：

| Arm | 目的 |
| --- | --- |
| baseline | 未校准中心、无 DR |
| SysID-only | 测 bias reduction |
| DR-only | 测宽分布是否硬扛中心误差 |
| SysID+DR | 测互补收益 |
| fitted+overwide | 测 conservative/optimization cost |

分层报告 nominal sim、one-factor sweep、correlated holdout、real replay/free-space；只有具备安全 authority 才进入 contact/task closed-loop，并报告 success/CI、first failure 和 safety events。

## 13. 实现伪代码

```python
def calibrated_dr_pipeline(real_data, contract, base_config):
    # 1. Check units, controller semantics, timestamps and excitation coverage.
    dataset = validate_sysid_data(real_data, contract)

    # 2. Fit nominal dynamics with multi-start and evaluate held-out trajectories.
    fit = fit_dynamics(dataset.train, multistart=True)
    residual = evaluate_fit(fit, dataset.holdout)

    # 3. Estimate uncertainty and preserve correlations/cadence from the contract.
    uncertainty = bootstrap_uncertainty(fit, dataset, residual)
    distribution = build_bounded_distribution(
        fit.parameters,
        uncertainty,
        contract.population_and_drift,
        contract.correlations,
        contract.sampling_cadence,
    )

    # 4. Reject negative, inconsistent, unstable or task-unsolvable samples.
    sampler_audit = audit_samples(distribution, contract.validity_rules)

    # 5. Run matched baseline/SysID/DR/combined/overwide arms before any claim.
    return run_matched_arms(base_config, distribution, sampler_audit)
```

## 14. 项目挂钩与真实性边界

当前 [Evidence Manifest](../evidence/evidence_manifest.html)、OpenPiVLA inventory 与 WAM artifact manifest 没有组成 WM-033 所需 bundle：缺 parameter manifest、real excitation、fit/identifiability report、sampler audit、matched arms、真机闭环和 ownership。

面试时可以说：

> 我会先确认 action/controller/timestamp contract，再用测量和 excitation trajectory 做 SysID，报告 held-out residual 与 parameter correlation。随机化围绕 fitted center 覆盖 measurement、population、drift 和 structural residual，并保留 correlation/cadence/validity。最后做 baseline、SysID-only、DR-only、combined、overwide 的 matched ablation。当前项目没有这套真机 artifact，所以我只把它作为可执行设计，不声称已提升真机成功率。

不能说：

- “把 mass/friction 随机 ±50% 就完成了 dynamics randomization”；
- “simulation loss/return 更好就证明 Sim2Real”；
- “trajectory match 说明每个参数都辨识正确”；
- “有 randomization config 就是我的 C2 优化”；
- “我已经通过 SysID+DR 提升真机成功率”。

## 15. 实战审计清单

- [ ] 参数 name/unit/site/nominal/range/distribution/source 完整；
- [ ] controller/action/timestamp contract 先闭合；
- [ ] excitation、train/held-out split、fit residual 可追溯；
- [ ] bootstrap/sensitivity/correlation/identifiability 有报告；
- [ ] positive support、correlation、cadence、validity 有测试；
- [ ] sampler draw/reject/boundary cases 有 ledger；
- [ ] baseline/SysID/DR/combined/overwide matched；
- [ ] nominal、stress、real replay、closed-loop 分层；
- [ ] real trial 有 limits/E-stop/trace authority；
- [ ] ownership 与 C0–C3 claim 对齐。

## 16. 参考来源

1. Tan et al., [*Sim-to-Real: Learning Agile Locomotion for Quadruped Robots*](https://arxiv.org/abs/1804.10332v2)。
2. Chebotar et al., [*SimOpt*](https://arxiv.org/abs/1810.05687v4)。
3. Peng et al., [*Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3)。
4. Yu et al., [*Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3)。
5. [WM-033 Source Freeze](../sources/vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)。
6. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 17. 下一节点

下一节点是 `VLA-WM-034`：control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real。本节点保持 WARN，题卡在真实口述前保持 unseen。
