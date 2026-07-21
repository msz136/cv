# VOL 04 World Model / Sim2Real：Control Frequency、Latency、Actuator 与 Controller Mismatch（WM-034）

> 状态：drafted / VLA-WM-034 / knowledge_36_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real？  
> 前置：[WM-023 Open-loop / Receding-horizon](vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)、[WM-033 Dynamics DR / SysID](vol_04_world_model_sim2real_wm033_dynamics_randomization_system_identification.html)、[WM-034 Source Freeze](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)。

## 1. 面试结论

强回答不是“把 sim 的 control_freq 调成 real 一样”，而是：

1. 冻结 physics/sensor/policy/network/controller/actuator 多时钟；
2. 测 observation capture→controller apply 的 action age 与 p50/p95/p99；
3. 把 action type/frame/unit/normalizer/controller/gain/limit 作为执行合同；
4. 用 fitted actuator model 代替 zero-latency/infinite-bandwidth 假设；
5. 给 chunk/queue 加 episode/version/deadline/freshness guard；
6. 先做 round-trip/free-space tracking，再做 contact/task；
7. 固定 checkpoint 做 frequency/latency/actuator/controller/K matched sweep；
8. 没有真机 trace 就不声称实时性或 transfer uplift。

## 2. 直觉：模型看到的是过去，机器人执行的是更晚的未来

policy 输入的图像在到达模型时已经变旧；模型推理、传输和排队后，动作又更晚才被 controller/actuator 执行。若一次还预测 H 步并执行前 K 步，后面的动作基于更旧的 observation。与此同时，simulator 可能让 command 瞬时生效、sensor 瞬时返回，并使用与真实 firmware 不同的 controller。

结果是：离线 action loss 很低，sim 中也稳定，真实执行却表现为 overshoot、oscillation、stale chunk、gripper 反向或完全不可达。[1][2]

## 3. 六条时钟

| clock | 关键字段 | 不记录会怎样 |
| --- | --- | --- |
| physics | `sim_dt/substeps` | 把 env step 当积分步 |
| sensor | capture/readout/sample timestamp | frame index 代替观测年龄 |
| policy | preprocess/infer start/end、query period | 只知道 GPU 时间 |
| transport/queue | send/receive/enqueue/dequeue、depth | 看不到 burst、乱序、stale |
| controller | mode/config、apply timestamp、Hz | policy Hz 冒充低层 Hz |
| actuator/firmware | command/response timestamp、bandwidth | command 冒充真实 torque/pose |

robosuite 的 `control_freq` 表示环境 applied action 的频率示例，不自动等于 physics、camera 或 real firmware frequency。[3]

## 4. Action age 才是核心量

对第 \(k\) 次 observation 与 chunk 第 \(j\) 个动作：

\[
A_{k,j}=t_{k,j}^{apply}-t_k^{capture}.
\]

变量解释：\(t_k^{capture}\) 是 sensor capture time，\(t_{k,j}^{apply}\) 是 controller 真正接受第 \(j\) 个 target 的时间。实现映射：camera、server、client 和 controller 必须使用同一时钟或保存 clock-offset calibration；只测 `model.forward()` 不能得到 action age。

同步近似下：

\[
A_{k,j}\approx\tau_{pipe}+j\Delta t_c.
\]

其中 \(\tau_{pipe}\) 是 capture→first apply latency，\(\Delta t_c\) 是 controller period。实现映射：画 per-offset age/error 曲线；若 K 增大后后半段失败，不能只说“模型 long horizon 不行”。

## 5. Latency 不能只报平均值

阶段包括 sensor、input transport、preprocess、batch wait、inference、serialization/network、controller queue、controller 和 actuator。异步系统有 overlap，因此端到端是 critical path，不是阶段平均值之和。

至少报告：

- inference latency；
- request→response latency；
- capture→first apply action age；
- capture→apply→next sensor loop；
- p50/p95/p99 与 jitter；
- deadline miss、drop、duplicate、out-of-order、stale rate；
- queue depth 与 fallback count。

Tan et al. 指出 instantaneous feedback 会扩大 simulated stability region；真实 delay 可能导致 oscillation/divergence。[1]

## 6. Delay 的闭环形式

离散线性化：

\[
x_{k+1}=A_dx_k+B_du_{k-d}.
\]

变量解释：\(d\) 是以 controller period 计的 effective delay。delay 引入 phase lag；高 gain 或快速 correction 在 zero-delay sim 中稳定，到了 real 可能 overshoot/oscillate。实现映射：latency injection 不能只有 constant delay，还应覆盖 jitter、burst、drop、stale 和 out-of-order。

Peng et al. 随机 action timestep 是简化的 latency proxy，但不等于完整 VLA pipeline trace。[4]

## 7. Frequency 如何改变动作

| action type | Hz 改变后的影响 |
| --- | --- |
| delta pose/joint | 相同 per-step delta 在更高 Hz 下变成更高单位时间速度 |
| velocity | 数值按秒解释，但 ZOH/filter/integration/limit 改变 |
| absolute target | dwell、interpolation、gain 和 settle time 改变 |
| torque/current | hold duration、bandwidth、saturation 与 inner loop 改变 |
| chunk | H/K steps 对应的秒数随 controller Hz 改变 |

必须写清 dataset Hz、runtime policy Hz、controller/firmware Hz、action repeat、per-step/per-second、interpolation 与 timestamp。shape 相同不代表物理时间相同。

## 8. Actuator dynamics

MuJoCo 官方模型把 control、transmission、activation dynamics 和 force generation 分开，并允许 activation state。[5] 一个最小近似：

\[
\tau_m\dot z=-z+g(c),\qquad
u=\operatorname{clip}(h(z),u_{min},u_{max}).
\]

变量解释：\(c\) 是 command，\(z\) 是 actuator internal state，\(\tau_m\) 是响应时间，\(g/h\) 含 gain、deadband、backlash、rate/current/force limit。实现映射：收集 command、encoder、velocity、current/torque、timestamp，用 step/sine/chirp 在 held-out frequency/amplitude/load 上验证。

Hwangbo et al. 用 actuator network 表达复杂 SEA response；其 ideal actuator 消融说明 infinite bandwidth/zero latency 是危险假设。[2]

## 9. Controller mismatch

policy action 到真实控制：

\[
u_k=\mathcal C_{\kappa}
\left(T_{a\rightarrow c}(a_k),x_k\right).
\]

变量解释：\(T\) 包括 denormalization、axis reorder、unit/frame、absolute/delta integration、clip；\(\mathcal C_\kappa\) 包括 OSC/joint mode、gain/damping、limit、interpolation、nullspace 和 gripper semantics。实现映射：保存 controller config SHA，并对 dataset→model→controller target 做 round-trip。

robosuite 区分 OSC_POSE、OSC_POSITION、JOINT_POSITION、JOINT_VELOCITY 和 JOINT_TORQUE，composite controller 还会拆分 body-part action。[3] 所以“都是 7D”不能证明可执行语义一致。

## 10. Freshness 与 queue

每个 response 至少带：

`episode_id / request_id / obs_version / chunk_id / offset / t_capture / t_response / t_apply`。

执行前检查：

- reset/episode/version 是否仍一致；
- response 是否超过 deadline；
- 是否 duplicate/out-of-order；
- 新 plan 是否已经覆盖旧 prefix；
- timeout 后 safe hold/requery/fallback/terminate 的规则；
- replan 时 FIFO、latest-only 或 flush-on-replan。

平均 latency 很低也可能被一次 reset 后继续执行旧 chunk 的事件击穿。

## 11. First-divergence ladder

1. protocol/checkpoint/normalizer/controller 同源；
2. clock sync 与 capture→apply trace；
3. action round-trip；
4. free-space step/sine/chirp tracking；
5. ideal vs fitted actuator；
6. constant/jitter/burst/drop/stale injection；
7. frequency、action repeat、H/K、queue policy sweep；
8. free-space 闭合后才进入 contact/task。

判断：target 前错，查 parser/normalizer/queue；target 对、actual 错，查 controller/actuator/limit；free-space 对、contact 错，转 WM-036。

## 12. Matched sweep

固定 checkpoint、normalizer、task/init、camera/preprocess、controller family、success predicate、trial count 和 seed：

| 维度 | 对照 | 读数 |
| --- | --- | --- |
| frequency | matched、half/double、repeat compensated | physical horizon、tracking、success |
| latency | zero、measured、tail jitter、burst/drop | action age、overshoot、recovery |
| actuator | ideal、fitted、misfit stress | target–actual、saturation、success |
| controller | expected、wrong mode/scale/frame、restored | round-trip、free-space、closed loop |
| chunk/queue | K sweep、FIFO/latest/flush、sync/async | stale/drop、queue、success/CI |

同时换 checkpoint、controller 和 task set，不能归因于 latency。

## 13. 实现伪代码

```python
def timestamped_policy_step(env, client, queue, contract):
    # 1. Capture observation, sensor time and episode/version together.
    obs = env.read_observation()
    req = make_request(obs, env.episode_id, env.obs_version)
    trace = begin_trace(req, obs.capture_time)

    # 2. Keep preprocess/send/response timestamps instead of only model.forward time.
    response = client.infer(req)
    trace.record_response(response)

    # 3. Drop wrong-episode, expired, duplicate or out-of-order responses.
    if not freshness_gate(response, env.state_version, contract.deadline):
        trace.record_drop("stale_or_version_mismatch")
        return env.apply_safe_hold()

    # 4. Map model output through the frozen action/controller contract.
    targets = action_to_controller_targets(response.actions, contract)
    queue.update(targets, policy=contract.queue_policy)

    # 5. Execute only the approved prefix and log apply time, actual state and limits.
    for target in queue.take(contract.execute_prefix):
        t_apply = env.controller.apply(target)
        trace.record_apply(t_apply, target, env.actuator_state())
        if env.done_or_success():
            break
    return trace
```

## 14. 项目挂钩与真实性边界

当前 [Evidence Manifest](../evidence/evidence_manifest.html) 和 OpenPiVLA inventory 支持 action packaging、H/K、controller 与 eval engineering 的讨论，但缺：formal checkpoint 完整 rollout lineage、多阶段统一 timestamp、action-age tails、真实 actuator fit、controller parity、matched frequency/latency/K sweep 和真机 ownership。

面试安全回答：

> 我会先冻结 physics、sensor、policy、queue、controller 和 actuator 六条时钟，测 capture 到 controller apply 的 action age 与尾延迟；再核对 action type/frame/unit/normalizer/controller/gain/limit，做 dataset→controller round-trip 和 free-space tracking。随后比较 ideal/fitted actuator、latency injection、frequency 与 K/queue policy。当前项目没有完整真机 trace，所以我只说具备这套审计设计，不声称已经降低真机 latency 或提升成功率。

不能说：

- “forward 20 ms，所以闭环 50 Hz”；
- “sim/real 都写 20 Hz 就对齐了”；
- “7D action 一样，所以 controller 一样”；
- “有 websocket/policy server 就是实时系统”；
- “改 control_freq 后 success 上升就是 latency 因果”；
- “当前项目已经完成 actuator/latency Sim2Real”。

## 15. 实战审计清单

- [ ] physics/sensor/policy/network/controller/firmware clocks 完整；
- [ ] clock offset 与 capture/response/apply timestamp 可追溯；
- [ ] action age p50/p95/p99、jitter、deadline/stale/drop 可查；
- [ ] action type/frame/unit/normalizer/controller config SHA 完整；
- [ ] reset、queue flush、version/freshness/fallback 有测试；
- [ ] actuator command/actual/current/torque held-out fit 有报告；
- [ ] dataset→model→controller→actual round-trip 可复现；
- [ ] frequency/latency/actuator/controller/K matched sweep；
- [ ] free-space 先于 contact/task；
- [ ] C0–C3 claim 与 ownership 对齐。

## 16. 参考来源

1. Tan et al., [*Sim-to-Real Agile Locomotion*](https://arxiv.org/abs/1804.10332v2)。
2. Hwangbo et al., [*Learning Agile and Dynamic Motor Skills for Legged Robots*](https://arxiv.org/abs/1901.08652v1)。
3. robosuite, [*Controllers*](https://robosuite.ai/docs/modules/controllers.html) 与 [*Environments*](https://robosuite.ai/docs/modules/environments.html)。
4. Peng et al., [*Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3)。
5. MuJoCo, [*Actuation model*](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model)。
6. [WM-034 Source Freeze](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 17. 下一节点

下一节点是 `VLA-WM-035`：camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模。本节点保持 WARN，题卡在真实口述前保持 unseen。
