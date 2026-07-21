# VOL 04 WM-036 Source Freeze：Contact、Friction、Compliance 与 Gripper Semantics

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-036 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-036  
> 本轮边界：只冻结 manipulation contact 的 hybrid/non-smooth 特性、friction dimensions、geometry/margin、soft constraint/compliance、solver/timestep、gripper action/controller/actuator semantics、micro-bench、matched evaluation 与项目真实性边界；不提前展开 WM-037 online adaptation/residual/data aggregation 或 WM-038 safety/recovery 总课，也不声称个人项目已完成真实接触标定、真机抓取优化或 contact Sim2Real。

## 1. 一页结论

1. **contact 是模式切换，不是平滑小误差。**separated→touch→stick/slip/roll 的切换由 gap、normal force、friction、velocity、geometry 与 controller 共同决定；微小参数变化可能跨过阈值，导致抓住/滑落、弹起/稳定的离散结果。
2. **friction 不是一个全局 scalar。**MuJoCo 明确区分 sliding、torsional、rolling friction，并支持 elliptic/pyramidal cones；contact pair 还受 `condim`、priority/`solmix`、margin/gap 等规则影响。[S1][S2]
3. **solver softness 不是直接物理材料常数。**MuJoCo soft constraints 使用 reference acceleration、stiffness/damping/impedance；`solref/solimp`、timestep、integrator/solver 配置共同影响 penetration、bounce、slip 与稳定性。不能把一个 `solref` 数字直接叫“真实橡胶刚度”。[S1][S2]
4. **collision geometry 与 visual mesh 都会影响接触。**finger pad、object collision mesh、contact margin、COM、scale、thin surface 和 self-collision 可改变 contact point/normal；视觉上相同不代表 collision geometry 相同。
5. **gripper scalar 必须解释。**open/close sign、position/velocity/force/binary mode、aperture unit/range、deadband、speed、force/current limit、finger coupling、saturation、reset state 都是合同。robosuite 的 Panda gripper 代码明确写 `-1=open, 1=closed` 并把一维 action 映射到两指状态；这只是该 simulator implementation，不是所有机器人约定。[S4]
6. **controller/actuator 与 contact 不可分。**相同 gripper target 在 position、force 或 impedance controller 下，受 gain、bandwidth、latency、backlash/compliance 影响；command 不等于 aperture/force/contact state。[S5][S8]
7. **range 必须 surface/object/gripper conditioned。**friction 随 finger pad、object material、surface、normal load、wear/contamination 变化；compliance 与 geometry/temperature/load 相关。独立 global uniform 会生成不可能组合或掩盖条件差异。
8. **先做 contact micro-bench，再跑长任务。**free-space closure→approach/touch→normal press→tangential slip→grasp hold/lift→disturbance→task；保存 contact pair/normal/tangent force、slip velocity、penetration、aperture/current/force、object pose 与 first divergence。
9. **本地项目没有 contact C2/C3 闭环。**OpenPiVLA/UWM inventories 有 controller/rollout 与 grasp/contact failure 假设，但缺 force/current/contact trace、material table、micro-bench、matched solver/gripper sweep、真机结果与 ownership。[S9]

## 2. 冻结来源与可支持边界

| ID | 一手来源 / 本地证据 | 冻结版本与快照 | 本节点可支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | MuJoCo official *Computation / Contact model* docs | `stable` 页面，2026-07-18 response SHA-256 `94228bfd24a70ce8d7c522269235bc17357183f7b7f2d17ffcd23703785ce3ac` | point contacts、normal/tangent frame、contact distance、soft constraints、tangential/torsional/rolling friction、elliptic/pyramidal cones | mutable stable docs 等于固定 local build；sim contact 是真实物理真值 |
| S2 | MuJoCo official XML reference | `stable` 页面，2026-07-18 response SHA-256 `c816a678f9af103744ef51a2d7312dac84030f1362d29d977c404d4c7492229b` | `friction(3)`、`condim`、priority/solmix、`solref/solimp`、margin/gap、solver/timestep semantics | 任一默认参数是 target robot/object 的正确值 |
| S3 | OpenAI et al., *Learning Dexterous In-Hand Manipulation* | arXiv:1808.00177v5；ar5iv response SHA-256 `826fb63d545518661a10b9cac05110bf7c813e88f99698d3b9e98cb313f81e93` | contact-rich real manipulation、friction randomization、tendon-vs-torque、rigid-vs-deformable contact gap、relative-position low-level control | Shadow Hand recipe/结果可直接推广到 parallel-jaw gripper 或用户项目 |
| S4 | robosuite gripper code | tag `v1.5.1` commit `51cc01785bab80ffeed20da15e67d7dd4140e76a`；`gripper_model.py` SHA-256 `b4582d448add9f4726a343a257fa32932465360b2bbc0362665846828a1356cb`；`panda_gripper.py` SHA-256 `df0449a9b003e9a019fad4ef59b435ae2b9accd2705026da041165dd99faab8d` | abstract gripper action、dof/speed、force/torque sensor names、Panda `-1=open,1=closed` mapping | code mapping 等于 real Panda/其他 gripper firmware；scalar sign 普适 |
| S5 | robosuite official Controllers docs | robosuite 1.5 docs；response SHA-256 `fdee90590d9ab45a2865531928c7ec4e0f46065a441777c53ed6921a83f65c99` | composite/body-part action split、OSC/joint controller families、input/output/gain semantics | simulator controller config 等于用户 real controller |
| S6 | [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html) | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | contact/friction/compliance/gripper 六层合同与 diagnostic order | 审计设计等于本地 contact implementation/result |
| S7 | [WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html) | canonical SHA-256 `d25897218b4a276a0d9a981c826e8680ba21db7e64b298963eace10184877a97` | free-space→contact→task first-failure gate | taxonomy 已完成 contact calibration |
| S8 | [WM-033 Dynamics SysID](vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)、[WM-034 Timing / Controller](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)、[VOL 03 Execution Audit](vol_03_architecture_execution_claim_to_code.html) | canonical SHA-256 `033a7485cd9ba9099aafaea2c4b34c42b7ef7ed0fbb1dec3d4bd629e24d967b2` / `106fe97d60e78505ae71e7a8667499a615d71b2e1f0099c1da474713ecf940f8` / `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809` | conditioned ranges、controller/action/actuator/timing semantics | 这些合同已证明 contact/gripper parity |
| S9 | [Evidence Manifest](../evidence/evidence_manifest.html)、OpenPiVLA/UWM inventories | manifest SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 本地 controller/rollout/grasp-contact failure hypothesis 边界 | failure hypothesis 等于 confirmed root cause、real contact measurement 或个人 uplift |

## 3. Hybrid contact：小误差为何变成大结果

将 contact mode 写为：

\[
m_t\in\{\text{separated},\text{touching},\text{sticking},\text{sliding},\text{rolling}\},
\qquad
x_{t+1}=f_{m_t}(x_t,u_t;\xi_c).
\]

变量解释：\(m_t\) 是离散 contact mode，\(\xi_c\) 包含 geometry、friction、compliance、solver、gripper/controller。实现映射：trace 不能只记 object final pose；需保存 contact onset/offset、pair ID、normal/tangent frame、force、relative velocity、penetration/gap 与 mode proxy。

当 gap、normal force 或 tangential demand 穿过阈值时，mode 会切换；因此 contact loss/trajectory 对参数可能非光滑，平均小 MSE 不保证抓取成功。

## 4. Friction cone 与 margin

最简 Coulomb sliding condition：

\[
\lVert f_t\rVert_2\le\mu f_n,
\qquad f_n\ge0.
\]

变量解释：\(f_n\) 是 normal force，\(f_t\) 是 tangential force，\(\mu\) 是简化 sliding friction。若 tangential demand 超出 cone，stick 转为 slip。实现映射：报告 friction margin

\[
m_f=\mu f_n-\lVert f_t\rVert_2,
\]

并与 slip velocity、object motion、finger pad/contact pair 同步；\(m_f<0\) 只是简化诊断，不代表所有 solver 的精确判据。

MuJoCo 还区分 torsional/rolling friction 与 elliptic/pyramidal cone；XML `friction(3)` 分别表示 sliding、torsional、rolling，并通过 contact-pair mixing/priority 组合。[S1][S2]

## 5. Compliance 与 soft constraint

物理材料的简化 normal force–displacement 可写：

\[
F_n\approx k_p\delta+c_p\dot\delta,
\]

其中 \(\delta\) 是压缩/penetration proxy，\(k_p,c_p\) 是有效 stiffness/damping。真实 finger pad/object 可能非线性、rate/load/temperature dependent；这只是 micro-bench 拟合入口。

MuJoCo soft constraint 使用 reference acceleration 和 impedance，可抽象为：

\[
a_r=-bv-kr,
\qquad
a_c=(1-d)a_u+da_r,
\]

其中 \(r,v\) 是 constraint residual/velocity，\(k,b\) 是 virtual stiffness/damping，\(d\) 是 impedance，\(a_u/a_c\) 是 unconstrained/constrained acceleration。`solref/solimp`、timestep/integrator/solver 一起决定数值行为；不能把它们直接等同于 \(k_p,c_p\)。[S1][S2]

## 6. Geometry、margin 与 collision model

contact point/normal 依赖 collision geometry，而不只视觉 mesh：

- finger pad/collision mesh、convex decomposition、scale；
- object collision vs visual geometry、thin wall/edge/corner；
- geom margin/gap、contact generation、pair/filter；
- object mass/COM/inertia 与 pose initialization；
- self-collision、joint limit、finger alignment；
- deformable/rigid assumption与 surface roughness。

OpenAI Dexterous 明确指出 simulation 直接 joint torque、真实 tendon actuation，以及 rigid-body vs deformable contact 的差异，支持“高保真 contact 很难”，不支持放弃 calibration/trace。[S3]

## 7. Gripper semantics contract

policy gripper output到执行：

\[
u_g=\mathcal C_{\kappa_g}
\left(T_g(a_g),q_g,\dot q_g,i_g,f_g\right).
\]

变量解释：\(T_g\) 包括 sign、range、binary/continuous、position/velocity/force mapping 与 clipping；\(\mathcal C_{\kappa_g}\) 包括 speed/gain/force/current limit、deadband、coupling、reset；\(q_g,i_g,f_g\) 是 aperture/joint、current 与 force feedback。实现映射：manifest 保存 model scalar→controller command→finger targets→measured aperture/force 的 round-trip。

| 语义 | 同一 scalar 的不同含义 |
| --- | --- |
| binary open/close | sign/threshold 决定状态 |
| position/aperture | meter/mm/rad、absolute/delta、joint vs jaw width |
| velocity | closing rate 与 control period |
| force/current | desired force/current、inner-loop limit |
| hybrid | position target + force limit / grasp state machine |

robosuite Panda implementation 写 `-1=open, 1=closed`，并用 `speed` 累积到两指 action；这是 simulator-specific mapping，不能假设其他 dataset/robot 相同。[S4]

## 8. Command、contact state 与 grasp success 不同

至少区分：

- `gripper_command`：policy/controller target；
- `aperture/joint_actual`：实际 finger position；
- `contact_detected`：一侧/两侧接触 pair；
- `normal/tangent force`：接触载荷；
- `object_constrained/held`：物体是否被稳定约束；
- `lift/transport success`：任务谓词。

command=close 不代表接触；两侧 contact 不代表 force 足够；短时 lift 不代表稳定 transport。指标必须沿这条 ladder 分层。

## 9. Conditioned range 与 correlation

| factor | range source | 条件/相关性 |
| --- | --- | --- |
| sliding/torsional/rolling friction | push/slip/twist/roll tests | pad×object/surface、load、wear/contamination |
| compliance/damping | force–displacement/rate tests | pad/object、temperature、speed/load |
| collision geometry/margin | CAD/scan/contact-point residual | object/finger revision、scale |
| gripper speed/force/deadband | closure/hold/current trace | controller/firmware、battery/temperature |
| solver/timestep | sim sensitivity/trace fit | simulator build、integrator/iterations/cone |

不要独立采 `friction×compliance×object material×gripper force` 到不可能组合。至少按 material pair 绑定参数，保存 population/drift 与 stress 分布。[S8]

## 10. Contact micro-bench ladder

1. **free-space closure**：无物体，测 command→aperture/speed/limit；
2. **approach/touch**：单轴慢速接近，测 contact onset/normal/gap；
3. **normal press**：不同 displacement/rate/load，拟合 force–displacement；
4. **tangential push/slip**：不同 normal load、surface、speed，测 slip threshold；
5. **pinch/hold**：两指 contact、force balance、object pose drift；
6. **lift**：重力/COM/acceleration 下的 slip/drop；
7. **disturbance/transport**：外扰、方向变化、持续时间；
8. **task**：只在前面闭合后运行 long-horizon success。

每一步保存 sim/real paired initial condition、controller config、object/material revision 与 first divergence。

## 11. Trace fields 与诊断

最小 per-step trace：

- timestamp、policy/gripper command、controller target；
- finger joint/aperture/velocity/current/estimated force；
- contact pair IDs、point、normal、distance/penetration；
- normal/tangential/torsional force与 relative/slip velocity；
- object pose/twist、COM、grasp/lift predicate；
- solver/timestep/integrator/iterations/cone/contact config；
- saturation、limit、collision/event/failure code。

诊断模式：

| 现象 | 优先检查 |
| --- | --- |
| command close、finger 不动 | sign/range/controller/limit/actuator |
| finger 合拢但未接触 | geometry/scale/pose/margin |
| 接触后弹开/振荡 | stiffness/damping/timestep/latency/gain |
| normal force 足够仍滑 | friction cone/tangent demand/COM/acceleration |
| sim 抓稳、real 掉落 | pad/material/friction/compliance/force/current model |
| free-space 也错 | 不进入 contact 归因；先查 WM-034 |

## 12. Validity、rejection 与 rollback

拒绝或分流：

- negative/invalid friction、nonphysical material combination；
- collision mesh 穿插、contact explosion、solver non-convergence；
- stiffness/timestep 组合导致 numerical instability；
- gripper sign/range/unit与 dataset/controller 不一致；
- object 初始化已 penetration/不可达；
- task 不可解却混入 nominal；
- combined randomization nominal 下降而 target micro-bench/real gate无收益；
- simulator-specific trace 被误当 real force/current truth。

保存 nominal/low/high/boundary/rejected cases、seed、contact overlay/trace 与 reason。

## 13. Matched contact matrix

固定 checkpoint、data/compute/init、camera/action/timing、controller family、object/task set、trial count、success predicate：

| arm | 变化 | 目的 |
| --- | --- | --- |
| A | nominal contact | baseline |
| B | friction only | stick/slip/twist/roll sensitivity |
| C | compliance only | penetration/bounce/force response |
| D | geometry/margin only | contact point/normal/pair sensitivity |
| E | gripper semantics/controller only | sign/range/mode/force/speed parity |
| F | solver/timestep/cone only | numerical/model sensitivity |
| G | calibrated combined | complementarity |
| H | overwide/invalid stress | contamination/conservative cost |

分 free-space、push/slip、press、hold/lift、transport、task closed-loop 报告；只有 G 在 matched target/real gate 上稳定更好，才能支持本地 contact calibration/DR 主张。

## 14. 最小 artifact bundle

| Artifact | 必须字段 | 能证明 | 不能单独证明 |
| --- | --- | --- | --- |
| `contact_model_manifest` | geom/material/friction(3)/condim/solref/solimp/margin/solver/timestep/build | sim contact 可追溯 | 参数真实 |
| `gripper_contract` | sign/type/unit/range/speed/force/current/deadband/controller/reset | gripper semantics 清楚 | contact/hold 成功 |
| `material_object_manifest` | pad/object/surface revision、mass/COM/geometry、conditioned range | 条件化参数存在 | range 正确 |
| `microbench_bundle` | free-space/press/slip/hold/lift traces、initial conditions | first-divergence 可定位 | long task success |
| `contact_trace` | command/actual/current/force/contact/slip/object/solver timestamps | contact behavior 可审计 | 因果提升 |
| `matched_contact_ablation` | A–H、固定项、sim/real protocol/result | 方法因果对照 | 未执行的 real result |
| `ownership_ledger` | 谁建模、测量、改 controller、运行验证 | 个人贡献 | 效果本身 |

## 15. 注释伪代码：contact micro-bench harness

```python
def run_contact_microbench(env, gripper, object_spec, contract, mode):
    # 1. Freeze simulator/controller/object/material revisions and reset without penetration.
    episode = reset_with_manifest(env, gripper, object_spec, contract)

    # 2. Verify command -> controller target -> free-space aperture before contact tests.
    free_trace = run_free_space_closure(episode, contract.gripper)
    if not free_trace.within_tolerance:
        return classify_failure("gripper_or_controller", free_trace)

    # 3. Run one isolated contact mode: press, slip, hold/lift or transport.
    trace = execute_mode(
        episode,
        mode=mode,
        limits=contract.safety_limits,
        log_contact_pair=True,
        log_force_current=True,
    )

    # 4. Compute contact onset, force/displacement, friction margin, slip and object drift.
    metrics = analyze_contact_trace(trace, contract.contact_semantics)

    # 5. Reject invalid/unstable runs and retain first divergence plus full revisions.
    return validate_and_record(metrics, trace, episode.manifest, contract)
```

## 16. 项目真实性边界

对 Evidence Manifest、OpenPiVLA/UWM inventories、architecture/execution audit 与现有 Sim2Real pages 的检索，没有形成 WM-036 本地 bundle：

- 缺 simulator contact/gripper/solver/timestep/build 完整 manifest；
- 缺 gripper scalar→controller→finger aperture/force/current round-trip；
- 缺 finger pad/object/surface material table、mass/COM/collision geometry revision；
- 缺 force–displacement、push/slip/twist、hold/lift/transport micro-bench；
- 缺 per-step contact pair/force/slip/penetration/current/object trace；
- 缺 friction/compliance/geometry/gripper/solver/combined/overwide matched arms；
- 缺 protocol-complete real contact result 与 ownership。[S8][S9]

安全表达：

- 可以说：“我会先闭合 gripper semantics 和 free-space tracking，再按 material/object 条件做 press/slip/hold/lift micro-bench，最后做 matched contact sweep。”
- 可以说：“UWM 的 grasp/contact 只是 failure hypothesis，OpenPiVLA 的 controller/rollout 是 partial provenance；当前没有真实 contact root-cause closure。”
- 不能说：“把 friction 调到 1 就解决 contact”“1 永远表示闭合”“sim grasp success 证明真机抓取”“项目已通过 contact randomization 提升真机成功率”。

按照 evidence contract，读懂 simulator/gripper config 最多 C0/C1；本地 micro-bench/ablation 才可能支持 C2；真实抓取 uplift 需要 C3 raw protocol、traces 与 ownership。

## 17. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| contact 支持 normal/tangent、torsional/rolling friction 与多种 cone/soft constraints | S1、S2 | official docs | checked |
| `friction(3)`、`solref/solimp`、margin/priority/solver/timestep 都进入 contact contract | S2 | official docs | checked |
| rigid/tendon/deformable contact gap 是 real dexterous transfer 风险 | S3 | primary | checked with platform scope |
| Panda gripper `-1=open,1=closed` 是 simulator-specific code mapping | S4 | official-code pinned | checked |
| hybrid/contact micro-bench、conditioned range 与 matched matrix | S1–S8 + engineering synthesis | synthesis | WARN / needs local execution |
| 用户项目已完成 contact calibration/real transfer | S9 | missing local evidence | rejected |

## 18. 仍待独立复核与补证据

1. 一手论文/官方 docs/code 已复核；source freeze 保持 `independent_fact_review=PENDING`。
2. 需要真实 contact/gripper/material/micro-bench/trace/matched/real bundle。
3. 需要真实口述后才更新练习状态；不得创建 `coaching_state.md`。
4. 浏览器本地 `file://` 若受策略阻断，只记录静态验证，不能写 visual PASS。

## 19. 参考来源

1. MuJoCo, [*Computation: Contact model*](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model) 与 [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)。
2. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
3. robosuite, [gripper model @ v1.5.1](https://github.com/ARISE-Initiative/robosuite/blob/51cc01785bab80ffeed20da15e67d7dd4140e76a/robosuite/models/grippers/gripper_model.py)、[Panda gripper](https://github.com/ARISE-Initiative/robosuite/blob/51cc01785bab80ffeed20da15e67d7dd4140e76a/robosuite/models/grippers/panda_gripper.py) 与 [Controllers](https://robosuite.ai/docs/modules/controllers.html)。
4. [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html)。
5. [WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。
6. [WM-033 Dynamics SysID](vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)。
7. [WM-034 Timing / Controller](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)。
8. [VOL 03 Architecture / Execution Audit](vol_03_architecture_execution_claim_to_code.html)。
9. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 20. 下一边界

下一 bounded slice 是 `VLA-WM-037`：residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择。本页不提前展开 adaptation authority、update stability、real-data collection 或 fallback/recovery。
