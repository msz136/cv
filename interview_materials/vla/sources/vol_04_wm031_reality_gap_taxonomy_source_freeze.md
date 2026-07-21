# VOL 04 WM-031 Source Freeze：Sim2Real Reality-gap Taxonomy

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-031 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-031  
> 本轮边界：只冻结 visual/sensor、dynamics/contact、control/timing、task/protocol、stochasticity 五层 reality gap，以及 first-failure 诊断顺序；不提前展开 WM-032..038 的 randomization、SysID、camera、contact、adaptation 或 safety 方法课，也不声称任何个人项目已完成 real-hardware transfer。

## 1. 结论先行

1. **Reality gap 不是“仿真图片不够真”。**它是从 observation、物理转移、动作执行、任务分布到随机扰动的复合 mismatch；任何一层都可能让 simulator success 无法迁移。[S1][S2][S3]
2. **面试可先答五层，工程上把 contact 单列。**五层是 visual/sensor、dynamics/contact、control/timing、task/protocol、stochasticity；manipulation 中 contact/gripper 同时受物理参数和 controller 影响，后续 WM-036 再独立深挖。[S3][S4][S5]
3. **Safety/recovery 是响应层，不是第六种物理根因。**碰撞、OOD 或约束事件可由前五层触发；limits、fallback、recovery、E-stop 用来控制后果，不能替代 gap 诊断。
4. **先找 first divergence，再选 intervention。**顺序是 real observation replay → action decode/round-trip → free-space tracking → contact bench → task/reset/success → repeated-trial drift；不要看到 real failure 就直接扩大 domain randomization。[S3][S5]
5. **视觉层同时包含 appearance、geometry 与 time。**texture/light/background 只是 appearance；intrinsics/extrinsics、distortion、crop/flip、exposure/blur、frame timestamp 与 dropout 都能改变几何和闭环反馈。[S1][S4][S5]
6. **动力学层不止质量与摩擦。**mass/inertia/COM、joint damping/backlash、actuator response、gravity/payload、solver/timestep、contact/compliance 共同决定下一状态；相同动作向量也可能因 actuator/controller 不同产生完全不同轨迹。[S2][S3][S5]
7. **任务层不是“模型不懂指令”这么简单。**对象/layout/initial state、语言语义、episode horizon、reset/warmup、success predicate 和 invalid-episode 处理都属于 target task/protocol；相同 task name 但 protocol tuple 不同，success 不能直接比较。[S7]
8. **随机性包括时间相关变化。**sensor bias/drift、battery/temperature/wear、payload、网络 jitter、外力和动态物体并非都可用 i.i.d. Gaussian noise 代表；要区分 episode-constant、step-wise、correlated 与 rare-event variation。[S2][S4]
9. **当前项目证据只支持方法论。**Evidence Manifest 没有一套 protocol-complete real-hardware Sim2Real bundle；LIBERO/RoboCasa simulator 结果、接口设计或单个 action trace 不能升级为真实迁移 claim。[S7]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Tobin et al., *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World* | arXiv:1703.06907v1；ar5iv snapshot 访问 2026-07-18，UTF-8 SHA-256 `faba518e98357c65a59d41f340bb723d4bb84c50eb359813597daab113dcd33a` | reality gap 包含 unmodeled physics 与 sensor/render mismatch；camera、lighting、object pose、texture、distractor 的 visual randomization | object-localization recipe 是通用 VLA transfer taxonomy 或个人结果 | primary / checked |
| S2 | Peng et al., *Sim-to-Real Transfer of Robotic Control with Dynamics Randomization* | arXiv:1710.06537v3；ar5iv snapshot SHA-256 `29d5e90f2a01e918bacb9d2a3e31622fc68018063be2bece6d86d2e0fca8a1b3` | mass/friction/damping/controller gain/action timestep/observation noise 等 dynamics variation；history-based adaptation | 95 个参数或其范围是任意 manipulation 默认配置 | primary / checked |
| S3 | Tan et al., *Sim-to-Real: Learning Agile Locomotion for Quadruped Robots* | arXiv:1804.10332v2；ar5iv snapshot SHA-256 `c34db6210074989010a635a11705e17da4a38d4b105e471159a9cc832a120a49` | unmodeled dynamics、wrong parameters、numerical error、contact amplification；SysID、actuator model、latency 与 robustness/optimality | locomotion 数值、actuator model 或随机范围可直接迁移到 VLA manipulation | primary / checked |
| S4 | OpenAI et al., *Learning Dexterous In-Hand Manipulation* | arXiv:1808.00177v5；ar5iv snapshot SHA-256 `826fb63d545518661a10b9cac05110bf7c813e88f99698d3b9e98cb313f81e93` | camera position/intrinsics/lighting/texture、correlated/uncorrelated observation noise、physics/contact/actuation randomization 与 memory | Shadow Hand recipe 普适；大量 randomization 自动证明安全/成功 | primary / checked |
| S5 | MuJoCo / OpenCV / robosuite official docs | MuJoCo stable、OpenCV 4.13.0 page、robosuite 1.5；访问 2026-07-18 | camera frame/intrinsics、pinhole/extrinsics/distortion、contact/constraint/actuator/controller parameter semantics | 某项目配置正确，或 docs 默认等于项目 runtime | official-doc / checked |
| S6 | VOL 04 Source Audit D：Sim2Real | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | 六层工程综合、source-to-mechanism 边界、paired test 与项目 truth boundary | 已完成独立复核或本地真实机器人迁移 | local-audit / WARN |
| S7 | Benchmark Audit E + Evidence Manifest | Audit E SHA-256 `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a`；manifest SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6` | task/protocol tuple、LIBERO/RoboCasa simulation 边界、五项目 artifact gate | protocol 名称相同即结果可比；存在 real-hardware Sim2Real bundle | local-audit / WARN |

### 2.1 Official-doc snapshots

| 文档 | 访问日 UTF-8 SHA-256 | 本节点用途 |
| --- | --- | --- |
| MuJoCo `modeling.html` | `505230785371f9e6e54575b5178950ffbce4b5b2fa9db7a0a393f91adc1315da` | camera attachment/intrinsics、constraint/contact、sensor metadata、actuator semantics |
| OpenCV `calib3d` | `e0a638f53a7f09287b8c502a364cfed8afa2fea3531a7dbe81bd30f4583825ce` | pinhole model、world→camera extrinsics、distortion |
| robosuite controller docs | `fdee90590d9ab45a2865531928c7ec4e0f46065a441777c53ed6921a83f65c99` | controller family/action semantics；不等于 local config |

网页 snapshot hash 只固定本轮读取内容；rolling docs URL 仍不是永久 build pin。

## 3. 五层系统合同

把真实闭环写成：

\[
o_t^r=h_{\psi_r}(x_{t-\tau_s}^r)+\epsilon_t^r,
\qquad
u_t^r=\mathcal C_{\kappa_r}(a_{t-\tau_a}),
\qquad
x_{t+1}^r=f_{\xi_r}(x_t^r,u_t^r,w_t^r).
\]

变量解释：\(h_{\psi_r}\) 是真实相机/传感器与 preprocessing，\(\psi_r\) 包含 geometry/appearance；\(\mathcal C_{\kappa_r}\) 是 controller/actuator，\(\tau_s,\tau_a\) 是 sensor/action delay；\(f_{\xi_r}\) 是真实 dynamics/contact，\(w_t^r\) 是未建模扰动。Simulator 使用对应的 \(\psi_s,\kappa_s,\xi_s,\tau_s^s,\tau_a^s,w_t^s\)。[S2][S3][S5]

任务结果还依赖 protocol：

\[
Y^r=Y(\tau^r;\mathcal P_r),
\qquad
\mathcal P=(T,I,L,H,R,S),
\]

其中 \(T\) 是 task/object/layout，\(I\) 是 initial/reset distribution，\(L\) 是 language/goal contract，\(H\) 是 horizon/termination，\(R\) 是 randomness/seed，\(S\) 是 success predicate。变量解释：即使低层物理完全匹配，\(\mathcal P_s\neq\mathcal P_r\) 仍会产生 task/protocol gap；Audit E 的完整 tuple 更细，本页只保留 taxonomy 所需字段。[S7]

| 主层 | 典型 mismatch | 主要症状 | 先冻结的证据 |
| --- | --- | --- | --- |
| visual / sensor | light/texture/background、K/R/t、distortion、exposure/blur、crop/flip、noise/dropout/timestamp | real replay feature/pose drift、camera-specific failure、目标位置系统偏差 | raw frame、camera ID/serial、intrinsics/extrinsics、preprocess hash、timestamp |
| dynamics / contact | mass/inertia/COM、damping/backlash、friction、compliance、solver/timestep、payload/deformation | free-space trajectory drift、slip/bounce/penetration、grasp failure | model parameters/units、measured trajectory、contact/gripper/controller config |
| control / timing | action dim/order/unit/frame、controller type/gain、frequency/ZOH、latency/queue、saturation/deadband | oscillation、overshoot、stale action、sim/real command response不同 | action round-trip、controller revision、Hz、timestamp trace、limits |
| task / protocol | instruction/goal、object/layout/init、reset/warmup、horizon、success/invalid rule | 同名 task 只在某 init 成功、sim score 不可复算、终止语义冲突 | task/init manifest、language、horizon、success code、trial denominator |
| stochasticity / operating condition | correlated noise、drift、battery/temp/wear、payload变化、外力、network jitter、dynamic object/human | 重复 trial 方差、随时间退化、rare-event failure | time/episode bucket、environment telemetry、seed/disturbance/event log |

这张表是来源综合，不是某篇论文原表。Contact 在五层回答里归入 dynamics，但 manipulation 诊断时应独立成一层，因为 gripper/controller/compliance 会跨越 dynamics 与 control。[S3][S4][S5]

## 4. Visual/sensor gap 的三个子类

1. **Appearance**：光照、颜色、材质、背景、阴影、反光、遮挡、motion blur、compression。Tobin 与 OpenAI dexterous work 支持 camera/lighting/texture/occlusion 等为可随机化变量。[S1][S4]
2. **Geometry**：intrinsics、extrinsics、distortion、mounting tolerance、depth scale、camera frame。OpenCV 的 pinhole/extrinsics 合同说明 world point 到 pixel 的映射依赖 \(K[R|t]\)；color jitter 无法修复 wrist-camera extrinsics 偏差。[S5]
3. **Time/data contract**：exposure/readout timestamp、transport、frame drop、RGB/BGR、resize/crop/flip、history alignment。真实图像“看起来像”仍可能因时间或预处理错位导致 action geometry 失败。

视觉层的 first check 不是闭环 success，而是把 frozen real observation 送入同一 processor/policy，比较 shape/range/feature/pose/action 输出；若 replay 已失败，先修 observation contract。

## 5. Dynamics/contact 与 control/timing 必须分开

真实转移误差可粗分为：

\[
e_{next}=
\underbrace{f_{\xi_r}(x,\mathcal C_{\kappa_r}(a))-f_{\xi_r}(x,\mathcal C_{\kappa_s}(a))}_{\text{controller / actuator mismatch}}
+
\underbrace{f_{\xi_r}(x,\mathcal C_{\kappa_s}(a))-f_{\xi_s}(x,\mathcal C_{\kappa_s}(a))}_{\text{dynamics / contact mismatch}}.
\]

变量解释：第一项保持真实 dynamics，只替换 controller/actuator；第二项保持 command execution，比较真实与 simulated transition。这是诊断分解，不是可直接观测的严格因果等式；实现需要 action round-trip、free-space tracking 和 contact bench 逐层近似隔离。

### 5.1 Free-space first

在无接触条件下发送安全、限幅的相同 command，比较 joint/end-effector trajectory、delay、overshoot 和 steady-state error。若此时已失配，优先查 action units/frame、controller、gain、actuator、mass/inertia、latency，不要先归因于 friction/contact或 VLA backbone。[S3][S5]

### 5.2 Contact second

Free-space 对齐后再做 push/slip/grasp micro-bench，记录 gripper aperture/force、object mass/COM、friction、compliance、solver/timestep 与接触事件。Contact 失败可能来自 dynamics，也可能是 gripper action semantics 或 impedance controller，因此 WM-036 需单独处理。[S4][S5]

## 6. Task/protocol gap 不等于 physics gap

Audit E 已表明 LIBERO default fixed `pruned_init`、UWM OOD shifted initialization、Cosmos runner 的 warmup/horizon/chunk 是不同协议。[S7] 因而以下变化即使都发生在 simulator 内，也足以改变 success：

- task/object/layout subset 与 language prompt；
- reset/initial-state distribution、warmup/stabilization；
- camera/preprocess/action/controller；
- episode horizon、timeout、early stop；
- success predicate、invalid episode、denominator；
- seed/determinism 与 trials per task。

“sim success 高、real success 低”只有在 simulator 与 real 的 task/protocol 对齐后才能进一步归因到 physics；否则首先是 evaluation distribution mismatch。

## 7. Stochasticity 不是只加 Gaussian noise

按时间尺度区分：

| 类型 | 示例 | 采样/记录方式 |
| --- | --- | --- |
| episode-constant | payload、object mass/friction、camera mount、battery start state | episode manifest + fixed parameter draw |
| step-wise | sensor noise、packet jitter、external perturbation | timestamped per-step trace |
| temporally correlated | bias drift、temperature、wear、lighting change | stateful process/sequence bucket，不用独立噪声代替 |
| rare event | occlusion、packet loss、unexpected contact、human intrusion | event injection + incident/fallback log |

Peng et al. 区分 episode-level dynamics 与 step-level action timestep/noise；OpenAI dexterous work 同时加入 episode-correlated与 timestep observation noise。[S2][S4] 这支持按时间尺度建模，不支持把其分布或数值照搬到用户任务。

## 8. First-failure 诊断梯子

```text
G0 protocol identity
  → G1 real observation replay / preprocess
  → G2 action decode + controller round-trip
  → G3 free-space trajectory tracking
  → G4 contact / gripper micro-bench
  → G5 task init / language / horizon / success
  → G6 repeated trials / drift / perturbation / safety response
```

| Gate | 通过标准 | 失败主要指向 | 不能证明 |
| --- | --- | --- | --- |
| G0 | sim/real task与metric合同可比 | task/protocol | physics 已匹配 |
| G1 | real replay shape/range/feature/action sane | visual/sensor/preprocess/time | real actuation 正确 |
| G2 | normalized action→controller command 单位/顺序/frame 一致 | control schema/normalizer/controller | dynamics/contact匹配 |
| G3 | safe free-space trajectory within tolerance | latency/actuator/control/dynamics | contact可靠 |
| G4 | push/slip/grasp micro-bench可复现 | friction/compliance/gripper/contact | long-horizon task成功 |
| G5 | init/language/horizon/success一致 | task/protocol | stochastic robustness |
| G6 | matched repeated trials与扰动下可接受 | stochasticity、risk/recovery | formal safety guarantee |

这个顺序减少“用更多 randomization 掩盖接口 bug”的风险。每个 gate 都要保存 paired timestamped artifact；最终 success=0 本身不足以定位层级。

## 9. 最小 paired matrix

| 假设 | 固定 | 只改变 | 输出 |
| --- | --- | --- | --- |
| observation gap | checkpoint/action/controller/task | sim render vs captured real replay | processor/feature/action discrepancy |
| control gap | same command/robot state | sim vs real controller path 或 delay injection | trajectory/latency/overshoot |
| dynamics gap | controller/action/init | nominal vs measured model parameter | free-space next-state error |
| contact gap | free-space-aligned stack | surface/object/gripper/contact setting | slip/grasp/contact trace |
| task gap | model/controller/physics | init/layout/language/horizon/success | per-stratum success + first failure |
| stochastic gap | nominal stack | seed/drift/jitter/perturbation/event | variance/tail/risk/fallback |

“只改变”是实验目标；真实系统很难完全隔离，因而必须记录剩余 confounder 并把因果结论降级为 `partially confirmed` 或 `open`。

## 10. 项目真实性边界

当前 Evidence Manifest 可支持：五个项目的 simulation protocol、部分代码/config/log/report 与接口诊断。它不提供一套完整的 real-hardware Sim2Real bundle：real camera calibration、robot/controller revision、paired sim/real initial conditions、per-step sensor→action→apply trace、contact/safety event、episode denominator 和 ownership 没有同时闭合。[S7]

安全表达：**“我能按五层 taxonomy 设计 first-failure 与 paired test，当前项目证据主要是 simulation/接口诊断，尚不能声称完成 real-hardware Sim2Real。”**

不能说：**“LIBERO/RoboCasa 成功率或 ALOHA/LIBERO 接口说明我已经完成 Sim2Real。”**Simulator benchmark、部署入口和真实硬件 rollout 是不同 evidence level。

按 ProjectProof evidence contract，公开论文与本地审计最多支持 C0“理解/能设计诊断”；只有存在个人 diff/measurement/run ledger 才能升级 C1/C2，real transfer 数字需要 C3 protocol/episode evidence。

## 11. 下一入口

下一 bounded slice 是 `VLA-WM-032`：visual/domain randomization 该随机化什么，怎样避免随机化到无关分布。本页只提供 taxonomy，不提前给 randomization range 或 ablation 结论。

## 参考文献（References）

1. Tobin et al., [Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World](https://arxiv.org/abs/1703.06907v1), 2017。
2. Peng et al., [Sim-to-Real Transfer of Robotic Control with Dynamics Randomization](https://arxiv.org/abs/1710.06537v3), 2018。
3. Tan et al., [Sim-to-Real: Learning Agile Locomotion for Quadruped Robots](https://arxiv.org/abs/1804.10332v2), 2018。
4. OpenAI et al., [Learning Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5), 2019。
5. [MuJoCo Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html)、[OpenCV calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)、[robosuite Controllers](https://robosuite.ai/docs/modules/controllers.html)。
6. [VOL 04 Source Audit D：Sim2Real](vol_04_sim2real_claim_to_mechanism.html)。
7. [VOL 04 Benchmark / Evidence Audit E](vol_04_benchmark_evidence_claim_to_protocol.html)。
8. [VLA Project Evidence Manifest](../evidence/evidence_manifest.html)。
