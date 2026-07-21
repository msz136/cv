# VOL 04 Source Audit D：Sim2Real Claim-to-Mechanism

> 审计日期：2026-07-16  
> 独立复核：2026-07-20  
> 状态：drafted / primary_papers_and_official_docs_reviewed / design_test_matrix_drafted / independent_fact_reviewed / PASS WITH WARNING  
> 覆盖题目：VLA-WM-031..038、VLA-WM-040..044  
> 目标：把 Sim2Real 从“加随机化”拆成 visual/sensor、dynamics、control、contact、task/protocol 与 safety 六层可测合同。

## 1. 结论先行

1. **Sim2Real 不是单一 distribution shift。**至少要拆成视觉/传感器、刚体动力学、控制/时序、接触/柔顺、任务/初始分布与安全恢复六层；每层的可观测症状、可调参数和验证实验不同。[1][2][4][10]
2. **Domain randomization 的目标不是越宽越好。**它优化的是 simulator parameter distribution 上的期望性能；SimOpt 与 Minitaur 工作都明确指出过宽范围可能包含不可解场景、压低峰值性能或产生过度保守策略。[3][4]
3. **System identification 与 dynamics randomization 互补。**可测参数先围绕实测中心建范围；不可准确辨识、会漂移或强耦合的参数用分布覆盖；少量 real rollouts 可进一步更新分布，而不是盲目扩大所有区间。[3][4]
4. **控制时序是独立高风险层。**policy frequency、physics timestep、zero-order hold、sensor/compute/network/actuator delay 与 low-level controller 都会改变闭环；Tan et al. 展示了遗漏 actuator model 与 latency 会导致 sim policy 到硬件振荡和失败。[4]
5. **视觉随机化必须围绕真实成像链。**texture/light/background 只是 appearance；camera extrinsics、intrinsics、distortion、exposure/blur、occlusion、resize/crop/flip 与 timestamp 都可能破坏 pose/action mapping。[1][11]
6. **contact gap 不能只用一个 friction scalar 概括。**滑动/扭转/滚动摩擦、contact softness、stiffness/damping、solver/integrator/timestep、compliance、backlash、gripper aperture/force 和 object deformability 均可能改变 manipulation outcome。[10][13]
7. **适配方法按 real-data authority 与风险选择。**无 real data 时只能做 calibrated randomization；少量 safe rollouts 可做 SimOpt/latent search；需要快速变化时使用 history-conditioned OSI/RMA；已有可靠 controller 时 residual policy 更合适。[3][5][6][7]
8. **安全不能等价于训练时 action clipping。**最小闭环需要 state/action constraints、uncertainty/risk gate、fallback/recovery controller、timeout/E-stop、事件日志和逐级 rollout gate。[8][9]
9. **Sim2Real claim 必须做 paired test。**同 checkpoint、同 real initial conditions、同 controller，只改变一个 simulator-side intervention，报告 seed/trial、failure family 和置信区间；sim score 上升本身不能证明 transfer。[1][2][3]
10. **本卷不证明任何个人项目已完成真实硬件迁移。**若没有 robot logs、calibration、controller config、real rollouts 与 safety record，只能写“Sim2Real 设计/诊断方案”，不能写“完成 Sim2Real 部署”。

## 2. 来源与证据边界

| 编号 | Primary / official source | 冻结版本 | 本页用途 | 不能外推 |
| --- | --- | --- | --- | --- |
| [1] | Tobin et al., Domain Randomization | arXiv 1703.06907v1 | texture/light/camera/object/distractor randomization 与 visual transfer | object localization 结果不证明任意 VLA policy transfer |
| [2] | Peng et al., Dynamics Randomization | arXiv 1710.06537v3 | parameter distribution、latency/noise、memory-based adaptation、real pushing | 95-parameter recipe不是通用默认配置 |
| [3] | Chebotar et al., SimOpt | arXiv 1810.05687v4 | 用少量 real rollouts 更新 simulator parameter distribution | 需要安全 real execution；不等于精确 system ID |
| [4] | Tan et al., Minitaur Sim2Real | arXiv 1804.10332v2 | measured parameter + margin、actuator model、latency、robustness/optimality trade-off | locomotion 数值不直接迁移到 manipulation |
| [5] | Yu et al., UP-OSI | arXiv 1702.02453v3 | history→dynamics parameter→universal policy 的显式 online SysID | 论文主要 simulation；不能写成真实机器人验证 |
| [6] | Kumar et al., RMA | arXiv 2107.04034v1 | privileged extrinsics、history-based latent adaptation、异步部署 | legged policy 结构不自动适配 VLA 图像输入 |
| [7] | Johannink et al., Residual RL | arXiv 1812.03201v2 | base controller + learned residual、contact-rich real manipulation | residual 不自动保留 base controller 的稳定性保证 |
| [8] | Thananjeyan et al., Recovery RL | arXiv 2010.15920v2 | risk critic、task/recovery policy 分工、offline unsafe data | chance-safety 不等于 formal zero-violation guarantee |
| [9] | Hewing et al., Cautious MPC | arXiv 1705.10702v4 | GP residual uncertainty、chance-constrained MPC | GP/hardware racing设置不是 VLA 默认实现 |
| [10] | MuJoCo official docs | stable docs accessed 2026-07-16；repo HEAD 0ce5e98916d8128ddb0eeb2f17304d2d9d29eecf | contact friction、solref/solimp、timestep、actuator/contact semantics | stable docs URL 与观察到的 HEAD 不视为同一 build proof |
| [11] | OpenCV calib3d official docs | 4.x docs accessed 2026-07-16 | pinhole intrinsics/extrinsics 与 lens distortion contract | calibration API 不证明某个项目标定正确 |
| [12] | robosuite controller docs | 1.5 docs；repo HEAD 5ce6643f3092639d08f7b0f90ed1c6a84f50552c | OSC/joint controller、composite action split、controller config | docs defaults 不等于 LIBERO/RoboCasa local config |
| [13] | OpenAI et al., Dexterous In-Hand Manipulation | arXiv 1808.00177v5 | calibration + extensive randomization、contact/sensor model limits、memory | Shadow Hand recipe 不直接推广到 Panda/gripper |

arXiv papers [1]–[9][13] 的 abs metadata 与 ar5iv full text或官方 abstract 已核对；它们使用 arXiv non-exclusive distribution license。这里只做事实引用，不复用图表或代码。官方 docs [10]–[12] 用于参数语义，不承担任何用户项目运行证明。

## 3. Reality gap 六层合同

将 real execution 写成：

\[
o_t^{real}=h_{\psi_r}(x_{t-\tau_s}^{real})+\epsilon_t,
\qquad
x_{t+1}^{real}=f_{\xi_r}\!\left(x_t^{real},
\mathcal C_{\kappa_r}(a_{t-\tau_a})\right),
\]

其中 \(h_{\psi_r}\) 是真实传感器/渲染链，\(\psi_r\) 包含 camera/exposure/noise；\(f_{\xi_r}\) 是真实 dynamics，\(\xi_r\) 包含 mass/friction/contact；\(\mathcal C_{\kappa_r}\) 是 low-level controller/actuator，\(\tau_s,\tau_a\) 是 sensor/action delay。simulation 使用另一组 \((\psi_s,\xi_s,\kappa_s,\tau_s^s,\tau_a^s)\)。Sim2Real 的目标不是让每个参数完全相等，而是让 policy 在目标分布上保持可接受的 closed-loop behavior。[2][4][10]

| Gap 层 | 典型 mismatch | 首要观测 | 可调 intervention | 必须冻结 |
| --- | --- | --- | --- | --- |
| Visual / sensor | texture、light、camera、distortion、blur、noise、timestamp | feature/pose drift、camera-specific failure | calibration、photometric/geometric DR、real fine-tune | camera serial/intrinsics/extrinsics、preprocess |
| Dynamics | mass、inertia、damping、motor strength、payload | free-space trajectory error | SysID、dynamics DR、latent adaptation | URDF/MJCF、parameter distribution |
| Control / timing | controller type/gain、frequency、latency、ZOH、queue | oscillation、overshoot、stale action | latency model、actuator model、replan | policy/controller/physics Hz、delay histogram |
| Contact / compliance | friction、softness、solver、deformation、gripper | slip、bounce、penetration、failed grasp | contact calibration/randomization、force/compliance | geom/contact/controller/gripper config |
| Task / protocol | init/object/layout/language/success/horizon | sim success only on narrow reset | task distribution alignment、strict eval | task list、reset/init、success predicate |
| Safety / recovery | OOD state、uncertain action、collision | risk score、constraint event | shield/fallback/recovery/E-stop | thresholds、limits、event logs |

这张表是基于 [1]–[13] 的工程综合，不是某篇论文原表。诊断时一次只缩小一层：若 real observation replay 到 simulator policy 已经异常，先修 sensor contract；若 observation replay 正常但 actuation trace 不同，转向 control/dynamics，而不是继续加 texture noise。

## 4. Visual domain randomization 与 camera contract

### 4.1 视觉随机化目标

令 \(\psi\sim p_\phi(\psi)\) 表示 renderer/camera 参数，visual policy/detector 的训练可写成：

\[
\theta^*=\arg\min_\theta
\mathbb E_{\psi\sim p_\phi,\,(x,y)\sim\mathcal D_{sim}}
\left[\ell\left(g_\theta(R_\psi(x)),y\right)\right].
\]

变量解释：\(R_\psi\) 是按 \(\psi\) 渲染/增强的 observation；\(p_\phi\) 应覆盖与任务相关的真实变化。Tobin et al. 随机化 camera position/orientation/FOV、lighting、object pose、textures 与 distractors，并用 ablation 检查哪些项影响 real test；这支持“按假设逐项验证”，不支持“任意强增强都有效”。[1]

### 4.2 Camera geometry 不能被 appearance augmentation 替代

标准 pinhole contract 为：

\[
\tilde u \propto K [R\mid t]\tilde X_w,
\qquad
K=\begin{bmatrix}
f_x&0&c_x\\
0&f_y&c_y\\
0&0&1
\end{bmatrix}.
\]

变量解释：\([R|t]\) 是 world→camera extrinsics，\(K\) 是 focal/principal-point intrinsics；真实 lens 还含 radial/tangential distortion。实现映射：OpenCV calib3d 明确定义该变换与 distortion coefficients；MuJoCo camera 可配置 focal/sensor size/FOV。若 wrist-camera extrinsics 偏移，color jitter 无法修复 action-space geometry。[10][11]

### 4.3 可审计的 camera randomization

1. 先标定/测量 \(K,R,t\)，保存 reprojection error 与 calibration timestamp。
2. 从 mounting tolerance、标定残差、robot vibration 建 \(\Delta R,\Delta t,\Delta f,\Delta c\) 分布，而不是拍脑袋给 ±20%。
3. appearance 分开建模：exposure、white balance、gamma、lighting direction/intensity、texture、background、JPEG、motion blur、occluder。
4. preprocessing 作为 contract：RGB/BGR、vertical flip、resize、crop、aspect ratio、frame stacking、timestamp。
5. paired test：每次只 ablate geometry、photometric、occlusion 或 compression 一组，比较 sim validation、real replay 与 closed-loop。

Tobin 的 camera range是其桌面 object-localization setup 的实例，不应复制为其他 robot 的默认 range。[1]

## 5. Dynamics randomization、System ID 与 SimOpt

### 5.1 分布式 dynamics objective

令 simulator 参数为 \(\xi\sim p_\phi(\xi)\)，policy objective 为：

\[
\theta^*(\phi)=\arg\max_\theta
\mathbb E_{\xi\sim p_\phi}
\left[J\left(\pi_\theta;f_\xi\right)\right].
\]

变量解释：\(\xi\) 可含 mass、inertia、damping、friction、controller gain、latency、observation noise、payload；\(J\) 是 simulator rollout return。Peng et al. 在 episode 起点采样大部分 dynamics 参数，并让 action timestep/noise 在 step 级变化；recurrent/history policy 用于从轨迹隐式辨识 dynamics。[2]

关键边界：该目标只优化 \(p_\phi\) 内平均性能。它不证明真实 \(\xi_r\) 在 support 内，也不保证极端尾部；分布越宽会增加 robust coverage，同时可能牺牲 nominal optimality。[3][4]

### 5.2 量测优先的 range 设计

| 参数族 | 建议中心 | range 来源 | 不宜做法 |
| --- | --- | --- | --- |
| mass/COM/inertia | CAD、称重、摆动/trajectory fit | measurement residual + safety margin | 所有 link 同比例无依据放大 |
| motor/actuator | current/torque/step response | fit error、battery/temp/wear | 把理想 torque source 当真实 actuator |
| latency/frequency | timestamp trace | p50/p95/p99 与 jitter | 只随机常数 delay，不测 queue/compute |
| friction/contact | slip/push/grasp experiments | surface/object-conditioned interval | 单一 global friction 覆盖所有 contact |
| sensor noise/bias | static/dynamic capture | bias、variance、dropout、drift | 只加 i.i.d. Gaussian 忽略 bias/time correlation |

Tan et al. 的做法是实测 mass/motor friction/latency，以测量加小 margin 建 range；对不确定的 inertia、wear、battery、control step 和 contact 进行更强 randomization。这是“SysID 给中心、DR 给覆盖”的直接例子。[4]

### 5.3 SimOpt：用 real trajectory 更新 distribution

SimOpt 可抽象为：先在 \(p_{\phi_k}(\xi)\) 上训练 policy，再用同一 policy 收集少量 real trajectory \(\tau^r\)，寻找能让 simulated behavior 接近 real behavior 的下一分布：

\[
\phi_{k+1}=\arg\min_\phi
\mathbb E_{\xi\sim p_\phi}
\left[D\left(\tau^r,\tau^{sim}(\xi)\right)\right]
+\lambda\,\Omega(\phi,\phi_k).
\]

变量解释：\(D\) 是可观测 trajectory discrepancy，\(\Omega\) 限制分布更新不要跳得过远；公式是对 SimOpt 迭代的审计抽象。它优化 transfer-relevant behavior match，而不是要求每个真实物理参数精确可辨识。[3]

安全要求：real rollout 必须先通过 conservative controller/limit/E-stop gate；若当前 policy 会撞击或掉落，不能为了 SimOpt 直接扩大 real-data collection authority。

## 6. Control frequency、latency 与 actuator

### 6.1 多时钟合同

设 physics step 为 \(\Delta t_{sim}\)，low-level controller 周期为 \(\Delta t_c\)，policy query 周期为 \(\Delta t_p\)，action chunk 前 \(K_e\) 步以 zero-order hold/queue 执行。真实动作可写为：

\[
u(t)=\mathcal C_{\kappa_r}
\left(a_{\lfloor(t-\tau_a)/\Delta t_p\rfloor}\right),
\qquad
o_t=h(x_{t-\tau_s}).
\]

变量解释：\(\tau_a\) 包含 policy compute、serialization/network、queue 与 actuator delay；\(\tau_s\) 包含 exposure/readout/transport/preprocess。相同 action vector 在 OSC_POSE、joint position、velocity 或 torque controller 下语义不同；robosuite docs 也说明 composite controller 会把统一 action vector 拆给不同 body-part controllers。[4][12]

### 6.2 为什么 latency 会放大

Tan et al. 指出 simulator 的即时 actuation/observation 会人为放大 feedback stability region；真实 delay 会引起 oscillation/divergence。他们测量硬件 latency、在 simulator 用 observation history 插值 delayed observation，并加入更准确 actuator model。[4]

VLA rollout 还要加上 action chunk stale risk：若一次预测 \(K\) 步而执行 \(K_e\) 步，环境变化与 model error 在 open-loop prefix 内累积。审计必须记录：

- camera timestamp → policy start/end → packet send/receive → controller apply → next camera timestamp；
- latency 的分布而非平均值；
- chunk \(K\)、execute horizon \(K_e\)、replan trigger、queue flush/version；
- simulator physics substeps、controller Hz、policy Hz 和 robot firmware Hz；
- stale response、timeout、duplicate packet、out-of-order packet 的处理。

### 6.3 最小 paired sweep

固定 checkpoint 与 real trials，比较 \(K_e\in\{1,4,8,16\}\)、人工 delay bucket、nominal vs fitted actuator model。若 free-space tracking 已失配，不要先把失败归因于 world model 或视觉表征。

## 7. Contact、friction、compliance 与 gripper semantics

### 7.1 Soft-contact 参数不是装饰配置

MuJoCo 把 soft constraint 的 reference acceleration 写成 spring-damper 形式，并把 constraint-space dynamics 近似写为由 impedance 插值约束作用：[10]

\[
a_r=-b v-k r,
\qquad
a_c=(1-d)a_u+d a_r,
\]

其中 \(r\) 是 constraint residual/penetration，\(v\) 是 constraint velocity，\(k,b\) 是 stiffness/damping，\(d\in(0,1)\) 是 impedance；<code>solref</code> 控制 time constant/damping ratio，<code>solimp</code> 控制 position-dependent impedance。官方 docs 还指出 time constant 相对 timestep 过小会让系统对 integrator 过硬并可能不稳定。[10]

摩擦至少区分 sliding、torsional 与 rolling；contact pair 还涉及 mixing/priority、friction cone、solver 与 no-slip settings。因而“把 friction 从 0.5 随机到 1.5”没有固定完整 contact contract。[10]

### 7.2 Manipulation 高风险点

1. gripper action 是 position、velocity、force 还是 binary open/close；正负号、deadband、saturation 是否一致。
2. gripper finger geometry、pad compliance、joint backlash、closing speed/force 与 real wear。
3. object rigid/deformable、mass/COM、surface-conditioned friction、mesh/collision margin。
4. OSC/joint impedance gain、force limit、collision contact threshold。
5. simulator solver/timestep 的 slip、bounce、penetration artifact。

OpenAI dexterous manipulation工作明确承认 rigid-body contact、tendon actuation与传感器难以匹配，并依赖 calibration、randomization 与 memory；Residual RL 则用 conventional controller 处理可建模部分，让 learned residual 针对 friction/contact 未建模部分。[7][13]

## 8. Adaptation 方法选择

| 方法 | 输入/authority | 适用场景 | 主要风险 |
| --- | --- | --- | --- |
| Fixed domain randomization | simulator only | 无 real data、先建立 coverage | support 选错、过度保守 |
| SimOpt / distribution adaptation | 少量 real trajectories | 可安全重复 rollout、需调整 simulator distribution | real cost、trajectory metric shortcut |
| Explicit UP-OSI | history→physical parameter \(\hat\mu\) | 参数语义明确、可在 sim 监督 | identifiability、模型假设错误；[5]未做 real robot |
| Latent RMA | history→task-relevant latent \(\hat z\) | 参数不可辨、环境快速变化 | latent OOD、history/timing mismatch |
| Recurrent implicit SysID | state/action history→policy memory | 希望 end-to-end adaptation | memory shortcut、难解释/校准 |
| Residual policy | base control + learned correction | 有可靠 controller、contact residual 局部 | residual 破坏稳定性或饱和 |
| Real fine-tune / data aggregation | real labels/rewards | 有足够安全数据与回滚机制 | hardware damage、catastrophic forgetting |

UP-OSI 直接预测 dynamics parameters；RMA 则预测 task-relevant low-dimensional extrinsics latent，强调不必恢复“物理真值”，只需支持正确 action。RMA 的 base policy 与 adaptation module 可异步运行，提醒部署必须记录各模块频率与 stale latent 策略。[5][6]

Residual policy 的核心为：

\[
u_t=\operatorname{sat}\left(u_{base}(s_t)+\alpha\,u_{res,\theta}(s_t,o_t)\right).
\]

变量解释：\(u_{base}\) 是 conventional feedback/impedance controller，\(u_{res}\) 学习未建模 contact/friction correction，\(\alpha\) 与 saturation 限制 residual authority。Johannink et al. 证明该结构可用于真实 contact-rich assembly，但其经验结果不等于对任意 neural residual 的稳定性证明；上线仍需 residual norm/rate/energy limits 与 fallback。[7]

## 9. Uncertainty-aware planning、安全与 recovery

### 9.1 Chance constraint

对 predicted state distribution \(x_{t+k}\sim p_\theta\)，安全规划可要求：

\[
\Pr\left(g_j(x_{t+k},a_{t+k})\le 0,
\ \forall j,k\right)\ge 1-\delta.
\]

变量解释：\(g_j\) 可表示 joint/velocity/force/collision/workspace constraints，\(\delta\) 是允许风险。Hewing et al. 用 GP residual dynamics 的不确定性传播构造 chance-constrained MPC；VLA 中可以用 ensemble/disagreement/quantile 近似，但若 uncertainty 没有 calibration，就不能声称满足概率约束。[9]

### 9.2 Risk gate 与 recovery

Recovery RL 的执行逻辑可抽象为：

\[
a_t=
\begin{cases}
\pi_{task}(s_t), & \hat Q_{risk}(s_t,a_t^{task})\le\epsilon_{risk},\\
\pi_{rec}(s_t), & \text{otherwise}.
\end{cases}
\]

变量解释：risk critic 估计未来 constraint violation，超过阈值就把 control authority 交给 recovery policy。论文用 offline constraint-violation data 预训练 risk/recovery，并在线更新；这是 learned shield 的实例，不是 formal zero-risk guarantee。[8]

### 9.3 VLA 最小安全闭环

```python
def guarded_replan(obs, policy, safety, recovery):
    # 1. Reject stale, malformed or out-of-range observations before policy inference.
    assert observation_contract_ok(obs)

    # 2. Generate a short action chunk and attach timestamp / checkpoint / schema metadata.
    chunk = policy.infer(obs)

    # 3. Parse, denormalize and run hard kinematic/controller limits before any execution.
    env_actions = transform_and_clip(chunk)

    # 4. Evaluate collision, force, workspace, uncertainty and learned risk gates.
    if safety.reject(obs, env_actions):
        return recovery.safe_action(obs)  # Hold, retreat, open gripper or E-stop by policy.

    # 5. Execute only the approved prefix, re-observe, and flush stale queued actions on any event.
    return env_actions[:approved_open_loop_steps]
```

这个伪代码是设计框架。具体 recovery action 必须由 robot/task hazard analysis 决定；“open gripper”在高处搬运时可能比 hold 更危险，不能写成通用默认。

## 10. Paired test matrix 与失败归因

| Test | 只改变 | 观测指标 | 能回答 | 不能回答 |
| --- | --- | --- | --- | --- |
| Camera replay | sim/real camera transform | feature/pose/action delta | visual contract 是否先失配 | real actuation |
| Open-loop actuator ID | commanded trajectory | position/velocity/current delay | actuator/latency model | contact policy success |
| Push/slip/grasp ID | surface/object/contact settings | slip/bounce/grasp force | contact parameter family | long-horizon task |
| DR width sweep | \(p_\phi(\xi)\) width | nominal/robust sim + fixed real trials | coverage/optimality trade-off | 未测 target support |
| SimOpt iteration | \(\phi_k\to\phi_{k+1}\) | real/sim trajectory discrepancy + success | distribution adaptation | exact real parameters |
| Chunk/replan sweep | \(K_e\) | latency、success、correction rate | stale/open-loop sensitivity | backbone quality独立贡献 |
| Safety gate ablation | risk/fallback gate | constraint events、recoveries、success | safety-performance trade-off | formal safety unless assumptions proven |

失败轨迹按如下顺序归因：observation contract → action transform → controller/timing → free-space dynamics → contact/gripper → task/success → uncertainty/recovery。每层要保存原始 timestamped trace；只看最终 success=0 无法区分根因。

## 11. 项目证据与真实性边界

| 可写 claim | 最低 artifact | 没有 artifact 时的安全表达 |
| --- | --- | --- |
| “做了视觉随机化” | randomization config/distribution、ablation、sample renders | “设计了待验证的 visual DR matrix” |
| “完成 dynamics randomization” | parameter names/ranges/units/source、training config、paired result | “识别了需随机化的 dynamics 参数” |
| “做了 system ID” | excitation trajectory、measurement、fit objective/residual、versioned model | “制定了 system ID 方案” |
| “处理 latency” | timestamp trace、p50/p95/p99、sim delay injection、paired eval | “将 latency 列为控制合同风险” |
| “实现 Sim2Real” | hardware、controller、safety、real rollout summary/videos/failures | “在 simulation benchmark 验证，尚未 real deployment” |
| “安全部署” | limits、risk gate、E-stop、incident log、approval protocol | “提出安全 gate，未完成安全认证” |

当前五个项目页中的 LIBERO/RoboCasa simulation 不等于 Sim2Real。没有真实硬件 artifact 时，本页只能支持面试中的方法论与诊断题，不能提升个人 Truth Boundary。

## 12. 面试答题骨架与当前边界

### 12.1 30 秒回答

“我会把 Sim2Real 拆成六层：visual/sensor、dynamics、control/timing、contact、task protocol 和 safety。先做 camera/action/controller 的接口 round-trip，再用 real measurement 给 mass、actuator、latency 和 friction 建中心与区间；可测参数做 system ID，不确定或会漂移的参数做 domain randomization。range 不是越宽越好，要通过同 checkpoint 的 paired real trials 看 robustness–optimality trade-off。快速变化可用 history-conditioned OSI/RMA，有可靠 controller 时可加 bounded residual。部署端还要有 uncertainty/risk gate、hard limits、fallback/recovery、E-stop 和完整 timestamp trace。没有真实硬件 rollout，我只会说这是迁移设计，不会说已完成 Sim2Real。”

### 12.2 高频追问防线

- “为什么不全随机化？”——过宽 distribution 会包含不可解/不相关场景并让 policy 过度保守；先测量再分层扩宽。[3][4]
- “SysID 与 DR 二选一吗？”——不是；SysID 给 nominal center，DR 覆盖 residual uncertainty，SimOpt 可用 real behavior 迭代 distribution。[3][4]
- “world model uncertainty 大怎么办？”——校准 ensemble/GP-style uncertainty，用 chance/risk gate 拒绝候选并缩短 horizon；uncalibrated variance 只算 heuristic。[8][9]
- “接触失败先查什么？”——gripper semantics/force、controller impedance、friction/contact solver/timestep、object mass/COM 与 camera-action geometry；不先怪 backbone。[10][12]
- “仿真 95%、真机 0%？”——按 observation→action transform→controller/timing→dynamics→contact 的 trace 顺序做 paired replay，不用更多随机化掩盖接口 bug。

### 12.3 独立复核后的开放项

- 已核实：10 份固定 PDF 共 124 页/0 空白页，MuJoCo/OpenCV/robosuite 固定源码与文档快照，六层 test matrix、12 个 deterministic probes，以及 WM-031..038 / WM-040..044 的 source→knowledge→card reconciliation；详见 [Audit D 独立事实复核](vol_04_sim2real_independent_fact_review.html)。
- 仍未核实：任何用户项目的协议完整 real hardware、calibration、latency/contact measurements、安全记录、real rollout 与候选人逐文件 ownership。
- 当前边界：Audit A–E public facts 已完成独立 review；VOL 04 仍因 local runtime、ownership 与 oral gate 保持 `WARN`，题卡真实口述前保持 `unseen`。

## 13. 参考文献（References）

1. Tobin et al., “Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World”, arXiv 1703.06907v1, 2017. [arXiv](https://arxiv.org/abs/1703.06907v1)。
2. Peng et al., “Sim-to-Real Transfer of Robotic Control with Dynamics Randomization”, arXiv 1710.06537v3, 2018. [arXiv](https://arxiv.org/abs/1710.06537v3)。
3. Chebotar et al., “Closing the Sim-to-Real Loop: Adapting Simulation Randomization with Real World Experience”, arXiv 1810.05687v4, 2019. [arXiv](https://arxiv.org/abs/1810.05687v4)。
4. Tan et al., “Sim-to-Real: Learning Agile Locomotion for Quadruped Robots”, arXiv 1804.10332v2, 2018. [arXiv](https://arxiv.org/abs/1804.10332v2)。
5. Yu et al., “Preparing for the Unknown: Learning a Universal Policy with Online System Identification”, arXiv 1702.02453v3, 2017. [arXiv](https://arxiv.org/abs/1702.02453v3)。
6. Kumar et al., “RMA: Rapid Motor Adaptation for Legged Robots”, arXiv 2107.04034v1, 2021. [arXiv](https://arxiv.org/abs/2107.04034v1)。
7. Johannink et al., “Residual Reinforcement Learning for Robot Control”, arXiv 1812.03201v2, 2018. [arXiv](https://arxiv.org/abs/1812.03201v2)。
8. Thananjeyan et al., “Recovery RL: Safe Reinforcement Learning with Learned Recovery Zones”, arXiv 2010.15920v2, 2021. [arXiv](https://arxiv.org/abs/2010.15920v2)。
9. Hewing et al., “Cautious Model Predictive Control Using Gaussian Process Regression”, arXiv 1705.10702v4 / IEEE TCST, 2019. [arXiv](https://arxiv.org/abs/1705.10702v4)。
10. MuJoCo official documentation, “Modeling” and “XML Reference”, accessed 2026-07-16. [Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html) / [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)。
11. OpenCV 4.x official documentation, “Camera Calibration and 3D Reconstruction”, accessed 2026-07-16. [calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)。
12. robosuite 1.5 official documentation, “Controllers”, accessed 2026-07-16. [Docs](https://robosuite.ai/docs/modules/controllers.html)。
13. OpenAI et al., “Learning Dexterous In-Hand Manipulation”, arXiv 1808.00177v5, 2019. [arXiv](https://arxiv.org/abs/1808.00177v5)。
