# VOL 04 World Model / Sim2Real：Contact、Friction、Compliance 与 Gripper Semantics（WM-036）

> 状态：drafted / VLA-WM-036 / knowledge_38_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点？  
> 前置：[WM-031 Reality-gap Taxonomy](vol_04_world_model_sim2real_wm031_reality_gap_taxonomy.html)、[WM-034 Timing / Controller](vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)、[WM-036 Source Freeze](../sources/vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html)。

## 1. 面试结论

contact 高风险，因为它是 hybrid/non-smooth 交叉层：

1. separated/stick/slip/roll 的模式切换会把小误差放大成抓住/滑落；
2. friction 有 sliding/torsional/rolling，不是全局一个 \(\mu\)；
3. compliance、solver、timestep、geometry/margin 一起影响 penetration/bounce/slip；
4. gripper scalar 需要 sign/type/unit/range/speed/force/controller/firmware 合同；
5. command、aperture、contact、hold、lift、task success 是不同指标；
6. 先 free-space，再 press/slip/hold/lift micro-bench，最后 long task；
7. 没有 force/current/contact trace 与 matched real protocol，不声称 contact Sim2Real。

## 2. Contact 是 mode switch

\[
m_t\in\{\text{separated},\text{touching},\text{sticking},\text{sliding},\text{rolling}\},
\qquad x_{t+1}=f_{m_t}(x_t,u_t;\xi_c).
\]

变量解释：\(m_t\) 是 contact mode，\(\xi_c\) 是 geometry、friction、compliance、solver、gripper/controller。实现映射：保存 contact onset/offset、pair、point/normal、force、relative/slip velocity、penetration/gap；只看 final success 无法定位 mode switch。

## 3. Friction cone

\[
\lVert f_t\rVert_2\le\mu f_n,
\qquad f_n\ge0.
\]

变量解释：\(f_n\) 是 normal force，\(f_t\) 是 tangential demand，\(\mu\) 是简化 sliding friction。超过 cone 后 stick 变 slip。诊断 margin：

\[
m_f=\mu f_n-\lVert f_t\rVert_2.
\]

实现映射：与 slip velocity、contact pair、object pose、normal load同步。MuJoCo 还支持 torsional/rolling friction 与 elliptic/pyramidal cone，所以 \(m_f\) 只是简化解释。[1]

## 4. Compliance 与 solver

物理 pad/object 简化：

\[
F_n\approx k_p\delta+c_p\dot\delta.
\]

变量解释：\(\delta\) 是压缩/penetration proxy，\(k_p,c_p\) 是有效 stiffness/damping。真实材料可能 nonlinear/load/rate/temperature dependent。

MuJoCo soft constraint 可抽象为：

\[
a_r=-bv-kr,
\qquad a_c=(1-d)a_u+da_r.
\]

`solref/solimp`、timestep、integrator/solver 共同决定数值 behavior；不能直接把配置值叫材料刚度。[1][2]

## 5. Friction 不止一个数字

| 维度 | 对 manipulation 的影响 |
| --- | --- |
| sliding | finger/object 或 object/table 平面滑动 |
| torsional | 绕 contact normal 扭转 |
| rolling | 球/圆柱或局部曲面滚动 |
| cone type | elliptic/pyramidal approximation 改变可行 force set |
| condim/mixing | contact DOF 与 pair friction/priority/solmix |

range 要按 pad×object/surface、normal load、wear/contamination 条件化，不能单一 global uniform。[1][2]

## 6. Geometry/margin 同样关键

- collision mesh 与 visual mesh 是否一致；
- finger pad geometry、scale、alignment；
- object thin edge/corner、COM/inertia；
- margin/gap/contact pair/filter；
- initial penetration、self-collision、joint limit；
- rigid/deformable assumption。

视觉看起来接触，并不代表 collision geometry 已接触；反之也可能有 invisible margin 提前接触。

## 7. Gripper scalar 到底是什么

\[
u_g=\mathcal C_{\kappa_g}
\left(T_g(a_g),q_g,\dot q_g,i_g,f_g\right).
\]

变量解释：\(T_g\) 是 sign/range/binary-position-velocity-force mapping，\(\mathcal C\) 是 controller speed/gain/force/current/deadband/coupling/reset，\(q_g,i_g,f_g\) 是 aperture/joint、current、force feedback。实现映射：保存 scalar→controller target→finger command→actual aperture/force round-trip。

robosuite Panda gripper 约定 `-1=open,1=closed`，并把一维 action 累积映射为两指控制；其他 simulator/dataset/firmware 可能相反或使用 aperture/force。[3]

## 8. 六级抓取指标

1. `command_close`：policy 发出闭合；
2. `aperture_reached`：finger 到达目标；
3. `contact_detected`：一侧/双侧 contact；
4. `force_sufficient`：normal/tangent margin 合理；
5. `object_held/lifted`：短时约束/离桌；
6. `transport/task_success`：完整任务谓词。

低级指标不能替代高级指标；“gripper close=1”不等于抓取成功。

## 9. Conditioned range

| factor | evidence | correlation |
| --- | --- | --- |
| friction(3) | push/slip/twist/roll | pad×object/surface/load/wear |
| compliance | force–displacement/rate | material/temperature/speed/load |
| geometry/margin | CAD/scan/contact-point residual | object/finger revision/scale |
| gripper dynamics | closure/current/hold trace | controller/firmware/battery/temp |
| solver/timestep | sensitivity/trace fit | sim build/integrator/iterations/cone |

material、friction、compliance、gripper force必须联合或条件采样，避免不可能组合。

## 10. Contact micro-bench

按顺序：

1. free-space closure；
2. approach/touch；
3. normal press；
4. tangential push/slip；
5. pinch/hold；
6. lift；
7. disturbance/transport；
8. task。

free-space 未通过时，先查 WM-034 的 sign/range/controller/actuator；不要调 friction 掩盖接口错误。

## 11. 必须保存的 trace

- policy/gripper command、controller target；
- finger aperture/joint/velocity/current/force；
- contact pair/point/normal/distance/penetration；
- normal/tangent/torsional force、relative/slip velocity；
- object pose/twist、COM、hold/lift predicate；
- solver/timestep/integrator/iterations/cone/contact config；
- saturation/limit/event/failure code与 timestamp。

## 12. First-divergence 诊断

| 症状 | 首查 |
| --- | --- |
| close command 后 finger 不动 | sign/range/controller/limit/actuator |
| finger 合拢但无接触 | geometry/scale/pose/margin |
| 接触后弹开/振荡 | stiffness/damping/timestep/latency/gain |
| normal force 足仍滑 | friction cone/tangent demand/COM/acceleration |
| sim 抓稳、real 掉落 | pad/material/friction/compliance/force/current |
| free-space 已错 | 不进入 contact；回到 action/controller gate |

OpenAI Dexterous 明确指出 tendon-vs-torque 与 rigid-vs-deformable contact gap，说明 contact failure 常是 model/controller 跨层问题。[4]

## 13. Matched contact ablation

固定 checkpoint、data/compute/init、camera/action/timing、controller family、object/task、trials、success predicate：

| arm | 变化 |
| --- | --- |
| nominal | baseline contact |
| friction | sliding/torsional/rolling |
| compliance | stiffness/damping/softness |
| geometry | collision/margin/contact pair |
| gripper | sign/range/mode/speed/force/controller |
| solver | timestep/integrator/iterations/cone |
| combined | calibrated factors |
| overwide | invalid/irrelevant stress |

分 free-space、press/slip、hold/lift、transport、task 报告，不能只看最终平均 success。

## 14. 实现伪代码

```python
def contact_microbench(env, gripper, object_spec, contract, mode):
    # 1. Freeze simulator, controller, gripper, object and material revisions.
    episode = reset_with_manifest(env, gripper, object_spec, contract)

    # 2. Verify command-to-aperture in free space before contact attribution.
    free_trace = run_free_space_closure(episode, contract.gripper)
    if not free_trace.within_tolerance:
        return classify_failure("gripper_or_controller", free_trace)

    # 3. Execute one isolated press/slip/hold/lift/transport mode with safety limits.
    trace = execute_contact_mode(
        episode, mode, contract.safety_limits, log_force_current=True
    )

    # 4. Analyze contact onset, force/displacement, friction margin and object drift.
    metrics = analyze_contact_trace(trace, contract.contact_semantics)

    # 5. Retain first divergence, full revisions and invalid/rejected reasons.
    return validate_record(metrics, trace, episode.manifest, contract)
```

## 15. 项目挂钩与真实性边界

当前 [Evidence Manifest](../evidence/evidence_manifest.html)、OpenPiVLA/UWM inventories 支持 controller/rollout/grasp-contact failure hypothesis，但缺 contact/gripper/solver manifest、scalar→aperture/force round-trip、material table、micro-bench、force/current/contact trace、matched contact arms、真机结果和 ownership。

面试安全回答：

> Contact 是 mode-switch 问题。我会先闭合 gripper sign/type/unit/range/controller 和 free-space closure，再按 pad×object/surface 条件做 press、slip、hold、lift micro-bench，保存 force/current/contact/slip/object trace；最后比较 friction、compliance、geometry、gripper、solver、combined、overwide。当前项目没有真实 contact bundle，所以不声称已提升真机抓取成功率。

不能说：

- “friction=1 就够了”；
- “1 总是 close”；
- “两指接触就等于 grasp success”；
- “调 solref 就拟合了真实橡胶”；
- “sim grasp 成功说明真机也会成功”；
- “当前项目已完成 contact randomization/real transfer”。

## 16. 实战审计清单

- [ ] contact/friction(3)/condim/solref/solimp/margin/solver/timestep/build 完整；
- [ ] gripper sign/type/unit/range/speed/force/current/deadband/reset 完整；
- [ ] collision visual/mesh/object/pad/material revision 可追溯；
- [ ] scalar→controller→aperture/force round-trip；
- [ ] free-space→press→slip→hold→lift→transport→task；
- [ ] contact pair/force/slip/penetration/current/object trace；
- [ ] conditioned range/correlation 与 invalid rejection；
- [ ] factor/combined/overwide matched arms；
- [ ] sim/real initial condition/protocol/denominator；
- [ ] ownership 与 C0–C3 claim 对齐。

## 17. 参考来源

1. MuJoCo, [Contact model](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model)。
2. MuJoCo, [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)。
3. robosuite, [Panda gripper @ v1.5.1](https://github.com/ARISE-Initiative/robosuite/blob/51cc01785bab80ffeed20da15e67d7dd4140e76a/robosuite/models/grippers/panda_gripper.py)。
4. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
5. [WM-036 Source Freeze](../sources/vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html)。
6. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 18. 下一节点

下一节点是 `VLA-WM-037`：residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择。本节点保持 WARN，题卡在真实口述前保持 unseen。
