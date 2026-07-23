# VOL 01 Foundations Batch 3：Impedance / MPC / Learned Policy 独立事实复核

> 状态：`independent_fact_review / batch3 / WARN`
> 审查日期：2026-07-19
> 范围：VOL 01 knowledge 的 advanced-control 入口与 `VLA-FND-039`；目标是建立控制方法选择边界，不把通用方法反向写成个人项目实现。
> 结论先行：impedance control、MPC 与 learned policy 解决的层级不同，常见系统是组合而不是互斥选择。只有在 action/controller contract、动力学模型、replan 频率、约束与本地 runtime artifact 齐全时，才能声称项目实际实现了某种组合。

## 1. 冻结来源

| ID | 来源 | 类型 | 支持 | 不支持 |
| --- | --- | --- | --- | --- |
| S01 | Hogan, [Impedance Control: An Approach to Manipulation, Part I](https://doi.org/10.1115/1.3140702), 1985 | primary paper | 通过期望动态关系连接运动误差与交互力 | 不支持 impedance 天然安全或任意接触稳定 |
| S02 | Rawlings, Mayne, Diehl, [Model Predictive Control: Theory, Computation, and Design](https://sites.engineering.ucsb.edu/~jbraw/mpc/MPC-book-2nd-edition-5th-printing.pdf) | primary textbook | finite-horizon optimization、模型/约束、receding horizon | 不支持模型失配下性能必然优于 policy |
| S03 | Chi et al., [Diffusion Policy](https://arxiv.org/abs/2303.04137), 2023 | primary paper | 视觉条件 action sequence policy、receding-horizon execution | 不支持其替代底层 controller 或安全约束 |
| S04 | Kim et al., [OpenVLA](https://arxiv.org/abs/2406.09246), 2024 | primary paper | vision-language-conditioned robot action policy | 不支持本地 OpenPiVLA action schema/ownership |
| S05 | Lynch & Park, [Modern Robotics](https://modernrobotics.northwestern.edu/) | primary textbook/site | kinematics、Jacobian、force/velocity 与 controller 接口 | 不支持项目实际控制频率或 torque loop |
| S06 | [VOL 03 Action Knowledge](../knowledge/vol_03_vla_action.html) | local knowledge audit | action chunk、replan、normalization 的跨卷入口 | 不支持本地 runtime 已闭合 |
| S07 | [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | local evidence audit | 项目 action/controller 与 artifact 缺口 | 不支持从项目页推断 impedance/MPC 已实现 |

## 2. 方法边界

### 2.1 Impedance control

令 \(e=x-x_d\)，一种目标阻抗关系可写为：

\[
M_d\ddot e+D_d\dot e+K_de=F_{ext}.
\]

\(M_d,D_d,K_d\) 是期望惯性、阻尼和刚度，\(F_{ext}\) 是外部交互力。直觉是系统不只追踪位置，还规定“受力后应该有多硬、多软、多阻尼”。这不等于天然安全：离散时间、延迟、力传感噪声、饱和、接触模型与底层 torque/position loop 都会影响稳定性。

### 2.2 Model Predictive Control

标准 finite-horizon MPC 可抽象为：

\[
\min_{u_{0:H-1}}\sum_{k=0}^{H-1}\ell(x_k,u_k)+\ell_f(x_H),
\quad
x_{k+1}=f(x_k,u_k),
\quad x_k\in\mathcal X,\ u_k\in\mathcal U.
\]

每次根据当前观测/状态解长度 (H) 的受约束优化，只执行第一步或短前缀，再重新估计和求解。优势是约束显式、代价可解释；风险是模型失配、状态估计误差、求解延迟与 horizon/terminal design。

### 2.3 Learned policy / VLA

learned policy 直接学习 \(\pi_\theta(a_t\mid o_{\le t},c)\) 或 action chunk，擅长把高维视觉和语言条件压到动作分布。它仍需要 action normalization、frame/unit、controller rate、safety limit、replan 和 success predicate。模型输出可作为末端目标、subgoal、MPC reference、residual 或直接 action；这些接口不是同一语义。

## 3. 选择与组合

| 场景 | 首要方法 | 组合建议 | 主要 gate |
| --- | --- | --- | --- |
| 接触、插入、表面跟随 | impedance/admittance | learned policy 给目标，低层控制力—位移关系 | force sensing、stiffness/damping、delay |
| 约束明确、动力学可用 | MPC | policy/world model 提 reference/model，MPC 做 constrained replan | model error、solver deadline、state estimate |
| 高维视觉语言、任务变化大 | learned policy/VLA | controller/MPC/impedance 承担执行和约束 | data coverage、OOD、action contract |
| 长时序且模型不准 | hybrid | policy 产 subgoal/chunk，短 horizon 重规划与 recovery | observation age、failure detector、fallback |

回答“什么时候用哪个”时先声明输出接口和闭环层级，再比较模型可信度、接触强度、约束、延迟、数据覆盖和安全预算。不能只以“方法更先进”作选择依据。

## 4. 项目与真实性边界

- OpenPiVLA/UWM 页面支持讨论 learned policy 与 controller 的接口，但当前 inventory 不证明候选人实现了 impedance 或 MPC。
- WAM/world model 可以为 planning/MPC 提预测或评分，但必须有 local planner runtime、objective、constraint、latency 与 selected-action trace 才能声称实际接入。
- `VLA-FND-039` 只能作为通用系统设计题；个人回答须使用“如果系统采用……”或绑定已核验 artifact。
- 39 张 VOL 01 题卡继续 `unseen`；本页不改变 mastery，也不创建 coaching state。

## 5. 下一步

将 impedance/MPC 公式、变量、pipeline 与 evidence boundary 回写 VOL 01 knowledge，并把 `VLA-FND-039` 的来源从仅 Modern Robotics 扩展到 primary control/policy sources。完成静态校验后，VOL 01 可进入“knowledge fact-review candidate”，但仍不能进入 `reviewed/drilled`。

## 参考文献

本页冻结 S01–S07；项目实现与个人 ownership 仍以 VOL 07 inventories/ledgers 为唯一入口。
