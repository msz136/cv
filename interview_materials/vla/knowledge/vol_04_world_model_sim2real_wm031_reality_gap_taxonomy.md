# VOL 04 World Model / Sim2Real：Reality-gap Taxonomy（WM-031）

> 状态：drafted / VLA-WM-031 / knowledge_33_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：建立 visual/sensor、dynamics/contact、control/timing、task/protocol、stochasticity 五层 taxonomy 与 first-failure 顺序；不宣称本地项目已完成真实硬件迁移。  
> 前置：[WM-030 Planning Runtime Contract](vol_04_world_model_sim2real_wm030_test_time_planning_latency_risk.html)、[WM-031 Source Freeze](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。

## 问题（Question）

Sim2Real reality gap 主要来自视觉、动力学、控制、任务与随机性哪些层？面试回答要能列全层级、给出典型症状，并说明怎样找到 first divergence，而不是一句“做 domain randomization”。

## 1. 先给直觉

Sim2Real 像把在“数字孪生排练场”学会的策略搬到真实机器人：相机看到的可能不同，物体与机器人运动规律可能不同，动作接口和时钟可能不同，考试题与判分规则可能不同，真实环境还会漂移和突然受扰动。

所以我用五层回答：

1. **视觉/传感器（visual/sensor）**：看见的内容、几何与时间是否一致；
2. **动力学/接触（dynamics/contact）**：同一真实力和动作是否产生相同下一状态；
3. **控制/时序（control/timing）**：模型动作怎样被 controller/actuator 执行，频率与延迟是否一致；
4. **任务/协议（task/protocol）**：对象、初始态、语言、horizon、success 是否真是同一任务；
5. **随机性/工况（stochasticity/operating condition）**：噪声、漂移、wear、jitter、外力和动态变化是否覆盖。

Manipulation 面试中最好补一句：contact/gripper 虽可归入 dynamics，但它同时受 friction、compliance、solver、gripper semantics 和 impedance controller 影响，工程上要单独测。Safety/recovery 是这些 gap 触发失败后的响应层，不是另一种物理根因。[1][2]

## 2. 严格系统表示

真实闭环可以写成：

\[
o_t^r=h_{\psi_r}(x_{t-\tau_s}^r)+\epsilon_t^r,
\qquad
u_t^r=\mathcal C_{\kappa_r}(a_{t-\tau_a}),
\qquad
x_{t+1}^r=f_{\xi_r}(x_t^r,u_t^r,w_t^r).
\]

变量解释：\(x_t^r\) 是真实状态，\(h_{\psi_r}\) 是相机/传感器与 preprocessing，\(\mathcal C_{\kappa_r}\) 是 controller/actuator，\(a_t\) 是 policy 输出，\(f_{\xi_r}\) 是 dynamics/contact，\(\tau_s,\tau_a\) 是 delay，\(\epsilon_t^r,w_t^r\) 是 sensor/process disturbance。Simulator 使用对应的下标 \(s\) 参数；Sim2Real 不是要求每个参数完全相等，而是要求闭环行为在目标任务分布上可接受。[2][3][4]

任务判定还依赖：

\[
Y=Y(\tau;\mathcal P),
\qquad
\mathcal P=(T,I,L,H,R,S).
\]

变量解释：\(T\) 是 task/object/layout，\(I\) 是 init/reset，\(L\) 是 language/goal，\(H\) 是 horizon/termination，\(R\) 是 randomness，\(S\) 是 success predicate。实现映射：评估 manifest 至少记录这些字段；否则“同一个 LIBERO task”也可能是不同 protocol。[5]

## 3. 五层 taxonomy 总表

| 层 | 典型 mismatch | 典型症状 | 第一检查 | 后续节点 |
| --- | --- | --- | --- | --- |
| visual / sensor | light/texture/background、intrinsics/extrinsics/distortion、exposure/blur、crop/flip、noise/dropout/timestamp | real replay 输入后 feature/action 偏移，某相机/视角专门失败 | raw frame + camera/preprocess/timestamp contract | WM-032、WM-035 |
| dynamics / contact | mass/inertia/COM、damping/backlash、actuator、friction/compliance、solver/timestep、payload/deformation | free-space drift、slip/bounce、grasp不稳 | safe free-space tracking，再做 contact micro-bench | WM-033、WM-036 |
| control / timing | action dim/order/unit/frame、controller type/gain、Hz/ZOH、latency/queue、clip/saturation/deadband | oscillation、overshoot、stale action、sim/real command response 不同 | action decode/denorm/controller round-trip + apply timestamp | WM-034 |
| task / protocol | language/goal、object/layout/init、reset/warmup、horizon、success/invalid rule | 相同模型只在特定 init 或判分方式成功 | protocol tuple 与 per-stratum denominator | Audit E / WM-039 |
| stochasticity / operating condition | correlated noise、bias drift、battery/temp/wear、payload变化、network jitter、外力、动态对象 | trial variance 大、随时间退化、rare-event failure | repeated matched trials + time/event bucket | WM-037、WM-038 |

这不是“选一个最像的层”就结束。一个现象可以跨层：wrist camera 延迟既是 sensor time gap，也会通过 controller feedback 变成 control gap；gripper slip 既可能是 friction，也可能是力/位置控制语义错误。

## 4. Visual/sensor：不只是图片风格

### 4.1 Appearance

光照、材质、纹理、背景、阴影、反射、遮挡、blur、compression 会改变视觉特征。Tobin et al. 对 camera、light、object pose、texture、distractor 做 randomization；OpenAI dexterous work还覆盖 camera intrinsics、materials 与多相机 appearance。[1][4]

### 4.2 Geometry

Camera geometry 决定 pixel 与机器人空间的对应：

\[
s\tilde p=K[R\mid t]\tilde P_w.
\]

变量解释：\(\tilde P_w\) 是 world point，\([R|t]\) 是 world→camera extrinsics，\(K\) 是 intrinsics，\(\tilde p\) 是 pixel；真实镜头还含 distortion。实现映射：保存 camera serial、calibration revision、intrinsics/extrinsics、distortion 和 reprojection error；color jitter 不能修复 extrinsics 偏移。[6]

### 4.3 Time and preprocessing

RGB/BGR、resize、crop、flip、aspect ratio、frame stacking、exposure/readout、transport 与 timestamp 都属于 observation contract。真实帧视觉上正常，但若 wrist frame 与 proprio 相差 100 ms，动作仍可能指向旧位置。

第一诊断：冻结一批 real observation，不驱动机器人，走与部署完全相同的 processor→policy→decode，检查 shape/range/feature/action；如果 replay 已异常，先修视觉/数据合同。

## 5. Dynamics/contact：同一命令为何走出不同轨迹

Dynamics gap 包括：

- robot：link mass/inertia/COM、joint damping/friction/backlash、motor strength/response、gravity；
- object/environment：mass/COM、friction、rigid/deformable、surface、payload；
- numerical/contact：timestep、integrator/solver、collision geometry、softness/compliance；
- disturbance：外力、线缆、wear、温度、电池状态。

Peng et al. 把 mass、friction、damping、controller gains、action timestep 与 observation noise 纳入 dynamics variation；Tan et al. 强调 unmodeled dynamics、wrong parameters、numerical errors、actuator model 与 latency，且 frequent contact 会放大小 mismatch。[2][3]

不要一上来测抓取。先做无接触（free-space）安全轨迹：同一 command 下比较 joint/end-effector position、velocity、delay、overshoot 和 steady-state error。Free-space 已错时，优先查 controller/actuator/latency/mass，而不是摩擦或视觉 backbone。

Free-space 通过后再做 contact micro-bench：push、slip、grasp、release。记录 gripper aperture/force、friction、object mass/COM、contact event、compliance 与 controller。这个顺序把 WM-033 与 WM-036 的问题边界分开。

## 6. Control/timing：相同 action vector 不一定是相同动作

Policy 可能输出 normalized delta pose，但真实 stack 需要 meter/radian、base frame 的 OSC pose；也可能存在 gripper sign、axis order、clip 和 action-repeat 差异。必须冻结：

- action dimension/order、unit、frame、absolute/relative；
- normalizer/denormalizer、clip、deadband、saturation；
- controller type、gain、impedance/force limit；
- policy/controller/physics/firmware Hz 与 ZOH/action repeat；
- sensor→policy→network→queue→controller apply latency。

第 j 个动作的 observation age 为：

\[
A_j=t_{apply,j}-t_{obs}.
\]

变量解释：\(t_{obs}\) 是传感器时间，\(t_{apply,j}\) 是 controller apply；server return 不是 apply。实现映射与 WM-030 相同：request/observation/action ID 串起 encode、queue、inference、enqueue/apply。若 sim instantaneous、real 有 delay/queue，策略可能振荡或执行 stale chunk。[3][7]

## 7. Task/protocol：任务名称相同仍可能不是同一测试

需要逐项对齐：

1. task/object/layout subset；
2. initial-state/reset distribution 与 warmup；
3. language prompt/goal definition；
4. observation/action/controller/chunk；
5. horizon、timeout、termination；
6. success predicate、invalid episode 与 denominator；
7. seeds、trial count 与 aggregation。

本仓库 Audit E 已冻结三个不同例子：LIBERO default fixed `pruned_init`、UWM Table II 的 OOD shifted initialization、Cosmos runner 的另一组 init/warmup/horizon/chunk。它们都在 simulator 中，但 protocol 不同，不能把 success 差异直接归因于模型或 Sim2Real。[5]

因此“仿真 95%、真机 0%”的第一问是：sim 与 real 是否真在做相同 \(\mathcal P\)？如果 real 对象、初始位姿、语言、horizon 或 success 不同，先标为 task/protocol gap。

## 8. Stochasticity：真实环境会漂移，也会发生稀有事件

| 时间尺度 | 示例 | 错误建模 |
| --- | --- | --- |
| episode-constant | payload、object friction、camera mount、battery 起始状态 | 每 step 独立重采样 |
| step-wise | sensor noise、packet jitter、外力 | 只保存 episode seed，不存 trace |
| correlated/drift | bias、temperature、wear、lighting 变化 | 用零均值 i.i.d. Gaussian 代替 |
| rare event | occlusion、packet loss、意外接触、动态人/物 | 只看平均 success，忽略 event/fallback |

Peng et al. 区分 episode-level dynamics 与 step-level timestep/noise；OpenAI dexterous work同时使用 episode-correlated和 timestep observation noise。[2][4] 工程结论是：按真实时间尺度采样和记录，而不是复制论文数值。

Safety/recovery 在这里是响应合同：当 rare event 或 OOD 发生时，系统如何限幅、拒绝、replan、fallback 或 E-stop。它不能让上游 gap 消失，详细方法留到 WM-038。

## 9. First-failure 诊断梯子

```text
G0 protocol identity
  → G1 real observation replay
  → G2 action/controller round-trip
  → G3 free-space tracking
  → G4 contact/gripper micro-bench
  → G5 task init/language/horizon/success
  → G6 repeated trials/drift/perturbation + safety response
```

```python
def localize_reality_gap(bundle):
    # 0. Do not compare success until task/protocol identities match.
    require_protocol_manifest(bundle.sim, bundle.real)

    # 1. Replay real observations without actuation to test sensor/preprocess.
    if not real_observation_replay_passes(bundle):
        return "visual_sensor"

    # 2. Verify normalized action, units, frame and controller apply.
    if not action_roundtrip_passes(bundle):
        return "control_schema_timing"

    # 3. Separate free-space dynamics from contact-rich execution.
    if not free_space_tracking_passes(bundle):
        return "control_actuator_or_dynamics"
    if not contact_microbench_passes(bundle):
        return "contact_gripper"

    # 4. Only then inspect task distribution and repeated-trial drift.
    if not task_protocol_passes(bundle):
        return "task_protocol"
    return analyze_stochasticity_and_recovery(bundle)
```

这段伪代码是诊断顺序，不是自动因果分类器。每个 gate 需要 paired timestamped artifact；若无法隔离 confounder，结论写 `open/partially confirmed`，不能写“已定位根因”。

## 10. 症状到层级的快速映射

| 症状 | 第一怀疑 | 关键反例 |
| --- | --- | --- |
| real replay 已输出异常动作 | visual/preprocess/task prompt | 也可能是 checkpoint/normalizer 错 |
| 末端持续固定方向偏移 | extrinsics/frame/action unit | 不一定是光照 |
| 无接触时振荡/overshoot | controller/gain/latency/actuator | 不先怪 friction |
| free-space 正常，一接触就 slip/bounce | contact/gripper/compliance | 也要查 gripper command/force |
| 只在某类 init/layout 失败 | task/protocol/perception support | 不等于 dynamics 一定正确 |
| 同 init 重复结果方差很大 | stochasticity/jitter/drift | 也要排除 nondeterministic evaluator |
| simulator score 高，真实硬件停止/timeout | control deadline/safety/task horizon | server forward 快不等于 apply 快 |

## 11. 项目证据与面试防线

当前五项目 Evidence Manifest 没有一套同时包含以下字段的 real-hardware Sim2Real bundle：

- real camera calibration 与 raw frames；
- robot/controller/firmware revision 和 action round-trip；
- paired sim/real init、task、checkpoint 与 per-step trace；
- contact/safety/fallback event；
- episode denominator、metric code 与 ownership ledger。

LIBERO/RoboCasa success 是 simulator evidence；WAM 的 CoffeePressButton action trace 是 simulator/接口诊断；deployment entry、接口或高层 robot tool 也不等于 real transfer result。[5][8]

安全口述：**“当前项目材料主要支持 simulation protocol 和接口诊断；我能按五层 taxonomy 设计 paired tests，但没有完整 real-hardware bundle，所以不把它包装成已完成 Sim2Real。”**

危险口述：**“我在 LIBERO/RoboCasa 做过，所以有 Sim2Real 经验”“我用了 domain randomization，所以已经解决 reality gap。”**

按 evidence contract，当前该节点对个人项目只支持 C0“机制理解/诊断设计”。C1 需要个人代码或 measurement artifact；C2 需要 matched ablation；C3 real transfer 需要完整 real rollout protocol 与结果。

## 12. 一句话收束与下一入口

**Reality gap 要按“看见什么、怎么运动、动作怎样执行、到底考什么、环境怎样变化”五层拆分；先做 protocol、real replay、action round-trip、free-space、contact、task、repeat 的 first-failure ladder，再选择 WM-032..038 的具体方法。**

下一节点是 `VLA-WM-032`：visual/domain randomization 该随机化什么，怎样避免随机化到无关分布。本节点保持 WARN，题卡在真实口述前保持 unseen。

## 参考文献（References）

1. Tobin et al., [Domain Randomization](https://arxiv.org/abs/1703.06907v1), 2017。
2. Peng et al., [Dynamics Randomization](https://arxiv.org/abs/1710.06537v3), 2018。
3. Tan et al., [Sim-to-Real Agile Locomotion](https://arxiv.org/abs/1804.10332v2), 2018。
4. OpenAI et al., [Learning Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5), 2019。
5. [VOL 04 Benchmark / Evidence Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
6. [OpenCV Camera Calibration and 3D Reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)。
7. [WM-030 Planning Runtime Contract](vol_04_world_model_sim2real_wm030_test_time_planning_latency_risk.html)。
8. [VLA Project Evidence Manifest](../evidence/evidence_manifest.html)。
