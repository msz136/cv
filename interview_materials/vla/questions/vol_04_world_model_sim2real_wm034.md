# VOL 04 VLA-WM-034 原子题卡：Control Frequency、Latency、Actuator 与 Controller Mismatch

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-034  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-034 Knowledge](../knowledge/vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)；来源边界见 [WM-034 Source Freeze](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)。

## control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-034</b> · control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real？</summary>

**面试意图**：判断你能否把“模型推理速度”和一个 `control_freq` 配置升级为多时钟、action age、controller/action semantics、actuator response、freshness guard 与 matched closed-loop evidence。

**30 秒回答**：先冻结六条时钟，测capture→apply的action age与p95/p99；核对动作类型、坐标/单位、normalizer、controller、gain和limit。用free-space round-trip、fitted actuator、delay/频率/K/queue对照找首个偏差；超时或旧响应须丢弃或safe hold。

**机制展开（约 2 分钟）**：同样H步在不同Hz代表不同秒数，delta/velocity/absolute/torque语义也不同。delay拆sensor、preprocess、infer、network、queue、controller、actuator，按critical path计时。action经denorm、frame/axis、controller和有限带宽actuator才成为execution；用episode/version/deadline拦截stale chunk。固定checkpoint/task/controller做frequency、latency、actuator、K/queue sweep，先free-space再contact。当前缺真机trace，不声称实时或transfer。

**诊断 / 证据**：保存 physics/sensor/policy/network/controller/firmware clocks；每个 request 记录 episode/obs/chunk/version、capture/preprocess/send/response/enqueue/apply/next-sensor timestamp、queue depth、deadline/drop reason。做 dataset→denorm→frame/axis→controller target round-trip，记录 target/actual/current/torque/saturation；固定 checkpoint 比较 zero/measured/tail delay、ideal/fitted actuator、matched/wrong/restored controller、Hz/action-repeat 与 K/queue policy。

**项目挂钩**：OpenPiVLA evidence 支持 H/K、action packaging、controller/eval audit，但缺 formal checkpoint 完整 rollout、统一 timestamp trace、action-age tails、真机 actuator fit、controller parity、matched latency sweep 和 ownership。安全说“能设计多时钟与 first-divergence audit”，不能把 websocket、policy server、`control_freq` 字段或 sim rollout 写成个人实时真机成果。

**追问树**：policy Hz、controller Hz、physics Hz 有何区别？为什么 forward 20 ms 不等于 50 Hz？action age 怎么定义？异步 pipeline 为什么不能加平均数？delta action 换 Hz 会怎样？absolute/velocity/torque 呢？ideal actuator 错在哪里？OSC_POSE 与 joint position 能共用 7D 吗？如何防 stale/out-of-order chunk？先测 free-space 还是 task success？怎样做 latency injection 与 K sweep？没有真机 trace 怎么回答？

**易错点**：只报平均 inference；把 env `control_freq` 当 firmware Hz；不记 capture/apply；同 shape 当同语义；delta 不换算物理时间；只加 constant delay；忽略 tail/jitter/queue；reset 不 flush；command 当 actual；sim ideal actuator；同时换 checkpoint/controller/task 后归因 latency；free-space 未闭合就调视觉或 contact。

**危险答案**：说“sim/real 都是 20 Hz 就对齐了”“模型 20 ms 所以闭环 50 Hz”“7D action 一样 controller 就一样”“actuator 瞬时跟随 target”“平均 latency 低就没有 stale 风险”“当前项目已完成真机 latency 优化并提升成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-034 Source Freeze](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)：多时钟、action age、actuator/controller、freshness、matched sweep 与项目边界。
2. Tan et al., [*Sim-to-Real Agile Locomotion*](https://arxiv.org/abs/1804.10332v2)；Peng et al., [*Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3)。
3. Hwangbo et al., [*Learning Agile and Dynamic Motor Skills for Legged Robots*](https://arxiv.org/abs/1901.08652v1)。
4. MuJoCo, [*Actuation model*](https://mujoco.readthedocs.io/en/stable/computation/index.html#actuation-model)；robosuite [Controllers](https://robosuite.ai/docs/modules/controllers.html)。
5. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-035`，不批量生成 WM-035..038，不创建 `coaching_state.md`。

