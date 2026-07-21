# VOL 04 WM-034 Source Freeze：Control Frequency、Latency、Actuator 与 Controller Mismatch

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-034 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-034  
> 本轮边界：只冻结 physics/sensor/policy/controller/actuator 多时钟合同、端到端 action age、chunk/queue freshness、actuator dynamics、controller/action semantics、诊断顺序与 matched sweep；不提前展开 WM-035 camera calibration/noise、WM-036 contact/friction 机制课或 WM-038 safety/recovery 总课，也不声称个人项目已经完成真机 latency 优化或 Sim2Real。

## 1. 一页结论

1. **相同 step 数不等于相同物理时间。**必须同时记录 simulator physics step、sensor period、policy query period、low-level controller period、firmware/actuator update 与 action repeat；否则 dataset、sim 和 real 的 horizon/control semantics 不可比。[S1][S5]
2. **latency 不是一个平均数。**camera exposure/readout、transport、preprocess、batch wait、inference、serialization/network、controller queue、low-level control 与 actuator response 共同决定 observation-to-actuation age；异步流水线应看 critical path、p50/p95/p99、jitter 与 deadline miss，而不是把平均值简单相加。
3. **delay 会改变闭环稳定性。**Tan et al. 指出 simulator 的即时 command/measurement 会扩大反馈稳定域，真实 delay 可导致 oscillation/divergence；他们测量 latency，并在 simulation 中延迟 observation。[S1]
4. **理想 actuator 会制造虚假可执行性。**MuJoCo 官方模型把 control、actuator force、activation state、transmission、activation dynamics 与 force generation 分开；Hwangbo et al. 的消融中，理想或不足的 actuator model 无法支持真实运动，说明 command 不等于瞬时 torque/pose。[S3][S4]
5. **controller mismatch 首先是语义错误，不只是参数误差。**robosuite 的 OSC_POSE、JOINT_POSITION、JOINT_VELOCITY、JOINT_TORQUE 接收不同 high-level action，并经 composite controller 拆分到 body parts；同形状 vector 在 mode、frame、scale、gain、limit 或 gripper polarity 不同时不可互换。[S5]
6. **VLA action chunk 会产生 stale-prefix 风险。**第 \(j\) 个动作的 age 约等于 pipeline latency 加 \(j\) 个执行周期；若 response 过期、重复、乱序或 episode reset 后仍执行旧 queue，模型精度再好也会闭环失败。[S7][S8]
7. **诊断先 free-space，再 contact/task。**先闭合时间戳、action round-trip、step/sine tracking、saturation/rate limit、latency injection 和 controller parity；free-space 已失配时，不应先归因于 perception、world model 或 contact。[S6]
8. **本地证据不足以形成个人实时/真机成果。**OpenPiVLA inventory 有 H/K/controller 等审计入口，但缺 formal checkpoint 的 protocol-complete rollout、完整时间戳 trace、真机 actuator fit、controller parity sweep 与 ownership；只能讲设计和待补证据。[S9]

## 2. 冻结来源与可支持边界

| ID | 一手来源 / 本地证据 | 冻结版本与快照 | 本节点可支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | Tan et al., *Sim-to-Real: Learning Agile Locomotion for Quadruped Robots* | arXiv:1804.10332v2；ar5iv response SHA-256 `c34db6210074989010a635a11705e17da4a38d4b105e471159a9cc832a120a49` | measured latency、delayed observation interpolation、actuator model、zero-delay stability-gap、real quadruped case | 论文 latency 数值是所有平台默认；其 real result 是用户项目结果 |
| S2 | Peng et al., *Sim-to-Real Transfer of Robotic Control with Dynamics Randomization* | arXiv:1710.06537v3；ar5iv response SHA-256 `29d5e90f2a01e918bacb9d2a3e31622fc68018063be2bece6d86d2e0fca8a1b3` | action timestep 作为 latency proxy、episode/step cadence、history-conditioned policy、real pushing case | exponential timestep recipe 是 VLA runtime 默认；random delay 能替代完整 pipeline trace |
| S3 | Hwangbo et al., *Learning Agile and Dynamic Motor Skills for Legged Robots* | arXiv:1901.08652v1；ar5iv response SHA-256 `53c0966cd6f700324a67c4a62dd35a708dbf5738547ba869bc307d4afdb197e9` | learned actuator network、ideal/analytical actuator ablation、bandwidth/latency/history 与 real robot transfer case | ANYmal actuator network 可直接复制给 manipulation；论文消融是用户项目证据 |
| S4 | MuJoCo official *Computation / Actuation model* docs | `stable` 页面，2026-07-18 response SHA-256 `94228bfd24a70ce8d7c522269235bc17357183f7b7f2d17ffcd23703785ce3ac` | control→force、transmission、activation dynamics、force generation、activation state | mutable `stable` 页面等于固定软件版本；MuJoCo actuator 配置等于真实 actuator |
| S5 | robosuite official Controllers / Environments docs | robosuite 1.5 docs；controllers SHA-256 `fdee90590d9ab45a2865531928c7ec4e0f46065a441777c53ed6921a83f65c99`；environments SHA-256 `521289c934304606d4c4fa3d03ce9b006cc20dc293748c88ef9f78022f80c1e5` | OSC/joint controller families、composite action split、input/output scaling、`control_freq` example | 20 Hz example或某 controller config 是用户 runtime；sim controller 等于 real firmware |
| S6 | [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html) | canonical SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200` | 多时钟、latency decomposition、controller 与 first-failure 设计 | 审计设计等于本地测量/优化结果 |
| S7 | [WM-023 Open-loop / Receding-horizon Source Freeze](vol_04_wm023_open_loop_receding_horizon_source_freeze.html) | canonical SHA-256 `7f37930bf857614a3275228887fcf35382bd1823f3ca87c78e0555875519aa3c` | H/K、observation age、queue、sync/async 与 stale response | planning source freeze 已证明 control stack parity |
| S8 | [VOL 03 Architecture / Execution Audit](vol_03_architecture_execution_claim_to_code.html) | canonical SHA-256 `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809` | action type/frame/unit/normalizer/controller round-trip 与 deployment evidence boundary | 上游 action contract 等于用户真机执行证据 |
| S9 | [Evidence Manifest](../evidence/evidence_manifest.html) 与 OpenPiVLA inventory | manifest SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6`；inventory SHA-256 `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293` | 本地 H/K/controller/checkpoint/rollout 证据缺口 | partial diagnostics 可升级为 formal checkpoint 真机 latency/C3 结果 |

## 3. 多时钟系统合同

至少区分：

| clock | 周期/时间戳 | 负责对象 | 常见错配 |
| --- | --- | --- | --- |
| physics | \(\Delta t_{sim}\) | simulator integration/substeps | 用 env step 当 physics step |
| sensor | \(\Delta t_s,t_{capture}\) | exposure/readout/sample | frame index 代替 capture time |
| policy | \(\Delta t_p,t_{infer}\) | observation→action chunk | 推理完成时间当 observation 时间 |
| network/queue | send/receive/enqueue/dequeue | server/client transport | 只记 RTT，不记排队/乱序 |
| controller | \(\Delta t_c,t_{apply}\) | high-level target→low-level command | policy Hz 当 controller Hz |
| actuator/firmware | \(\Delta t_a\) / response trace | command→force/position response | 假定 infinite bandwidth/zero delay |

robosuite 的 `control_freq` 是 applied action 的环境频率示例；它不自动等于 simulator physics、real firmware 或 camera frequency。[S5]

设观测 capture 时间为 \(t_k^o\)，动作真正 apply 的时间为 \(t_{k,j}^a\)，则 chunk 第 \(j\) 个动作的 observation-to-actuation age 为：

\[
A_{k,j}=t_{k,j}^a-t_k^o.
\]

变量解释：\(k\) 是 policy query，\(j\) 是 chunk 内 offset。实现映射：必须在 camera、preprocess、server、client、queue、controller apply 写同一时钟域或可校准的 clock offset；仅用 Python wall-clock 计 inference 不能得到 \(A_{k,j}\)。

同步执行近似下：

\[
A_{k,j}\approx \tau_{pipe}+j\Delta t_c,
\]

其中 \(\tau_{pipe}\) 是 capture→first apply 的 critical-path latency。该式忽略异步 overlap、queue wait 与 clock skew，只能作为初始审计模型，不能替代真实 timestamp trace。

## 4. Latency decomposition 与 critical path

概念上可列出：

\[
\tau_{parts}=	au_{sensor}+\tau_{transport}^{in}+\tau_{pre}+
\tau_{batch}+\tau_{infer}+\tau_{serialize}+\tau_{network}+
\tau_{queue}+\tau_{controller}+\tau_{actuator}.
\]

变量解释：每一项是一个可打点阶段。异步 pipeline 中阶段会 overlap，所以 end-to-end latency 是关键路径，不一定等于各阶段平均数之和。实现映射：保存 start/end timestamp、request/episode/version ID、queue depth、deadline、drop reason，并同时报告 end-to-end p50/p95/p99。

必须区分：

- `compute latency`：GPU/CPU inference 本身；
- `response latency`：request send→response receive；
- `action age`：observation capture→controller apply；
- `sensor-to-sensor loop`：capture→apply→下一有效 observation；
- `jitter/deadline miss`：尾部延迟与超时率；
- `staleness`：response 到达时 episode/state/version 已变化。

“模型 20 ms”不等于“控制 50 Hz”，因为还缺 sensor、queue、network、controller、actuator 与调度预算。

## 5. Delay 为什么破坏反馈

离散线性化可写为：

\[
x_{k+1}=A_dx_k+B_du_{k-d},
\]

其中 \(d\) 是按 controller period 离散的有效 delay。delay 增加 phase lag；对依赖快速反馈的 policy/controller，zero-delay simulation 中稳定的 gain 或 action correction 在 real 中可能 oscillate、overshoot 或 divergence。

Tan et al. 明确指出 instantaneous actuation/observation 会扩大 simulated feedback stability region；他们用 hardware measurement 设 latency，并从 observation history 插值 delayed observation。[S1]

诊断不能只加一个 constant delay：还要测 fixed delay、jitter、bursty queue、drop、out-of-order、duplicate、clock skew 和 sensor age。Peng et al. 用随机 action timestep 作为简化 proxy，但这不覆盖完整 VLA server/client pipeline。[S2]

## 6. Control frequency 改变 action 语义

令数据/训练频率为 \(f_D\)，runtime policy frequency 为 \(f_P\)，controller frequency 为 \(f_C\)。同一数值动作在不同语义下影响不同：

| action type | frequency mismatch 后果 |
| --- | --- |
| delta pose/joint | 每步相同 delta 在更高 Hz 下产生更大单位时间位移；低 Hz 下单步跳变更大 |
| velocity | 若 controller 正确按秒解释，理想幅值不随 Hz，但 ZOH、滤波、限幅与 integration 会变化 |
| absolute target | target 可重复，但 dwell time、interpolation、gain 与 settle time 变化 |
| torque/current | ZOH duration、bandwidth、saturation 与 inner loop 直接影响状态 |
| action chunk | 同样 H steps 对应 \(H/f_C\) 秒；执行 prefix \(K/f_C\) 秒 |

所以 manifest 必须写 action type、unit、frame、normalization、per-step/per-second、action repeat、interpolation 与 timestamp；只对齐 shape 不够。[S8]

## 7. Actuator dynamics：command 不等于 execution

MuJoCo 将 actuator 表达为 scalar control \(c_i\) 经 transmission、activation dynamics 与 force generation 产生 actuator force，并可有 activation state \(z_i\)。一个最小近似是：

\[
\tau_m\dot z(t)=-z(t)+g(c(t)),
\qquad
u(t)=\operatorname{clip}\big(h(z(t)),u_{min},u_{max}\big).
\]

变量解释：\(\tau_m\) 是响应时间常数，\(g\) 含 deadband/command mapping，\(h\) 含 gain、backlash、rate/current/force limit。实现映射：用 step/sine/chirp 或安全 excitation 收集 command、encoder、velocity、current/torque 与 timestamp，fit 后在 held-out frequency/amplitude/load 上验证。

Hwangbo et al. 使用 actuator network 学习复杂 SEA response，并比较理想/分析 actuator model；论文说明 ideal infinite-bandwidth/zero-latency 假设会造成真实执行失败。[S3] 这支持“actuator model 是 transfer contract”，不支持把论文网络直接复制成其他机器人模型。

## 8. Controller mismatch：同 vector 不同物理动作

把 policy action 到执行写为：

\[
u_k=\mathcal C_{\kappa}
\left(T_{a\rightarrow c}(a_k),x_k\right),
\]

其中 \(T_{a\rightarrow c}\) 是 denormalization、axis reorder、unit/frame transform、absolute/delta integration 与 clipping；\(\mathcal C_\kappa\) 是 mode、gain、damping、limit、interpolation、nullspace、gripper semantics 等 controller config。

robosuite 官方文档说明 composite controller 会把 action vector 拆到不同 body-part controller，并区分 OSC_POSE、JOINT_POSITION、JOINT_VELOCITY、JOINT_TORQUE；其配置还含 input/output range 与 impedance 参数。[S5]

最小 controller contract：

- action dimension、axis order、unit、frame、absolute/delta/velocity/torque；
- denormalizer SHA、clip/saturation、rate limit；
- controller family/version/config SHA；
- gain/damping/nullspace/interpolation；
- gripper polarity/deadband/force/position semantics；
- policy/controller/firmware Hz 与 action repeat；
- reset behavior、queue flush、safe hold 与 E-stop。

## 9. Chunk、queue 与 freshness

对每个 response 保存 `(episode_id, request_id, obs_version, chunk_id, j, t_capture, t_response, t_apply)`。执行前至少检查：

1. episode/reset version 是否一致；
2. response 是否晚于 deadline；
3. obs/state version 是否过旧；
4. chunk offset 是否已被新计划覆盖；
5. queue 是否含 duplicate/out-of-order action；
6. timeout 时是 safe hold、requery、fallback 还是 terminate。

队列策略必须显式：FIFO、latest-only、flush-on-replan、execute-prefix、event-triggered replan。低平均 latency 不能抵消偶发旧 chunk 在 reset/contact 后继续执行的安全风险。[S7]

## 10. First-divergence 诊断梯子

1. **protocol gate**：checkpoint/normalizer/action/controller/task/reset 是否同源；
2. **clock gate**：统一时钟或估计 offset，画 capture→apply→next-sensor trace；
3. **action round-trip**：dataset action→model representation→denormalize→controller target；
4. **free-space target test**：固定 pose、step/sine/chirp，测 target/actual/error/saturation；
5. **actuator test**：ideal vs fitted model、amplitude/frequency/load held-out；
6. **latency injection**：constant、jitter、burst、drop、stale/out-of-order；
7. **frequency/H/K sweep**：固定 checkpoint，改 policy/controller Hz、action repeat、execute prefix；
8. **contact/task gate**：只有 free-space 闭合后才进入 contact 和 task success。

若第一处 divergence 在 controller target 之前，查 parser/normalizer/queue；若 target 对但 actual 错，查 controller/actuator/limit；若 free-space 对而 contact 错，留给 WM-036。

## 11. Matched sweep

固定 dataset/checkpoint、normalizer、task/init、camera/preprocess、controller family、success predicate、trial count 与 seed：

| sweep | arms | 主要读数 |
| --- | --- | --- |
| frequency | matched train/runtime、runtime half/double、action-repeat compensated | physical horizon、tracking、success、deadline miss |
| latency | zero、measured center、p95/p99 jitter、burst/drop | action age、overshoot、recovery、first failure |
| actuator | ideal、analytical/fitted、learned/fitted、misfit stress | target–actual error、saturation、task success |
| controller | expected config、wrong mode、gain/scale/frame mismatch、restored | round-trip、free-space error、closed-loop success |
| chunk/queue | \(K\) sweep、FIFO/latest-only/flush、sync/async | stale rate、queue depth、success/CI、safety event |

不要同时改变 model checkpoint、controller、frequency 和 task set后把差异归因于 latency。

## 12. 最小 artifact bundle

| Artifact | 必须字段 | 能证明 | 不能单独证明 |
| --- | --- | --- | --- |
| `clock_contract` | clock source/offset、physics/sensor/policy/controller/firmware Hz | 时间轴可解释 | latency 已优化 |
| `latency_trace` | stage start/end、request/version、queue、t_capture/t_apply、p50/p95/p99 | action age 与 tail 可测 | task transfer 成功 |
| `controller_contract` | mode/config SHA、frame/unit/type/scale/gain/limit/gripper/reset | action semantics 对齐 | actuator 跟踪正确 |
| `actuator_fit_report` | excitation、command/state/current/torque、fit/heldout error、load/frequency | actuator model 有数据支撑 | 全任务 dynamics 正确 |
| `roundtrip_tracking` | dataset/model/controller target/actual trace、saturation | interface/free-space parity | contact/task success |
| `matched_sweep` | frequency/latency/actuator/controller/K arms、固定项、seed/trials | 方法因果对照 | 未执行的真机结果 |
| `ownership_ledger` | 谁打点、fit、改 queue/controller、运行验证 | 个人贡献边界 | 效果本身 |

## 13. 注释伪代码：timestamped rollout 与 stale guard

```python
def rollout_step(env, policy_client, clock_sync, queue, contract):
    # 1. Capture observations with sensor timestamps and the current episode/version.
    obs = env.read_observation()
    request = build_request(obs, episode_id=env.episode_id, obs_version=env.obs_version)

    # 2. Record preprocessing, send, inference/response and queue timestamps separately.
    trace = start_trace(request, t_capture=obs.capture_time)
    response = policy_client.infer(request)
    trace.mark_response(response)

    # 3. Reject stale, wrong-episode, duplicate or out-of-order responses before execution.
    if not freshness_gate(response, env.state_version, contract.deadline):
        trace.mark_drop(reason="stale_or_version_mismatch")
        return apply_safe_hold(env, contract.fallback)

    # 4. Denormalize and map the action through the expected controller contract.
    targets = transform_action_chunk(response.actions, contract.action, contract.controller)
    queue.replace_or_append(targets, policy=contract.queue_policy)

    # 5. Apply only the approved prefix and log target, actual state and saturation.
    for target in queue.take(contract.execute_prefix):
        t_apply = env.controller.apply(target)
        trace.mark_apply(t_apply, target, env.read_actuator_state())
        if env.done_or_success():
            break
    return trace
```

## 14. 项目真实性边界

对 Evidence Manifest、OpenPiVLA inventory、architecture/execution audit 与现有 rollout source 的检索，只能确认 H/K/controller/action-contract 的审计入口，不能闭合 WM-034 本地成果：

- 缺 formal checkpoint 的完整 rollout lineage；
- 缺 camera capture→policy→network→queue→controller apply→next camera 的统一 timestamp trace；
- 缺 p50/p95/p99 action age、deadline miss、drop/stale/out-of-order 统计；
- 缺真实 actuator excitation/fit/held-out report；
- 缺 expected controller config 与 wrong/restored parity sweep；
- 缺固定 checkpoint 的 frequency/latency/actuator/K matched arms；
- 缺真机 closed-loop result 与 ownership ledger。[S8][S9]

安全表达：

- 可以说：“我能把 rollout 拆成多时钟与 action-age contract，并设计 latency injection、controller round-trip 和 actuator tracking sweep。”
- 可以说：“当前本地证据支持 action packaging/eval engineering 的讨论，但没有 protocol-complete 真机 latency/actuator 结果。”
- 不能说：“我把推理降到 X ms 因而提升真机成功率”“policy server 已满足实时闭环”“调整 control_freq 完成了 Sim2Real”，除非有对应 trace、matched trial 与 ownership。

按照 evidence contract，config/字段理解最多是 C0/C1；设计 matched harness 需要本地 C2 artifact；具体 latency/success uplift 需要 C3 protocol 和结果。

## 15. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| zero-delay/instant observation 会改变反馈稳定域 | S1 | primary | checked |
| action timestep randomization 可作为简化 latency proxy | S2 | primary | checked with scope |
| complex actuator 可由 learned model 表达，ideal actuator 会误导 transfer | S3、S4 | primary + official docs | checked with platform scope |
| robosuite controller families/action split 与 `control_freq` 是显式 runtime contract | S5 | official docs | checked |
| action age、critical path、freshness/queue guard 必须单独审计 | S6–S8 + engineering synthesis | synthesis | WARN / needs local execution |
| 用户项目已完成实时真机闭环或 latency uplift | S9 | missing local evidence | rejected |

## 16. 仍待独立复核与补证据

1. 一手论文和官方 docs 已复核；source freeze 仍保持 `independent_fact_review=PENDING`。
2. 需要真实 clock/controller contract、latency trace、actuator fit、round-trip tracking 与 matched sweep。
3. 需要真实口述后才更新练习状态；本节点不得创建 `coaching_state.md`。
4. 浏览器本地 `file://` 若受策略阻断，只能记录静态验证，不能写 visual PASS。

## 17. 参考来源

1. Tan et al., [*Sim-to-Real: Learning Agile Locomotion for Quadruped Robots*](https://arxiv.org/abs/1804.10332v2)。
2. Peng et al., [*Sim-to-Real Transfer of Robotic Control with Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3)。
3. Hwangbo et al., [*Learning Agile and Dynamic Motor Skills for Legged Robots*](https://arxiv.org/abs/1901.08652v1)。
4. MuJoCo, [*Computation: Actuation model*](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model)。
5. robosuite, [*Controllers*](https://robosuite.ai/docs/modules/controllers.html) 与 [*Environments*](https://robosuite.ai/docs/modules/environments.html)。
6. [VOL 04 Sim2Real Audit D](vol_04_sim2real_claim_to_mechanism.html)。
7. [WM-023 Open-loop / Receding-horizon](vol_04_wm023_open_loop_receding_horizon_source_freeze.html)。
8. [VOL 03 Architecture / Execution Audit](vol_03_architecture_execution_claim_to_code.html)。
9. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 18. 下一边界

下一 bounded slice 是 `VLA-WM-035`：camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模。本页不提前展开 camera projection/calibration、rolling shutter 或 sensor corruption 的完整方法课。
