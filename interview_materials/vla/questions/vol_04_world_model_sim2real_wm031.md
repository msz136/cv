# VOL 04 VLA-WM-031 原子题卡：Sim2Real Reality-gap Taxonomy

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-031  
> 难度：L1 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-031 Knowledge](../knowledge/vol_04_world_model_sim2real_wm031_reality_gap_taxonomy.html)；来源边界见 [WM-031 Source Freeze](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。

## Sim2Real reality gap 主要来自视觉、动力学、控制、任务与随机性哪些层？

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-WM-031</b> · Sim2Real reality gap 主要来自视觉、动力学、控制、任务与随机性哪些层？</summary>

**面试意图**：判断你能否把 reality gap 从“画面不真实/加随机化”升级为完整闭环 taxonomy，并按 first divergence 选择诊断，而不是把所有 real failure 都归因于 physics 或 backbone。

**30 秒回答**：五层：视觉/传感器看相机、预处理、时间戳；动力学/接触看质量、摩擦、柔顺；控制/时序看 action、controller、频率、延迟；任务/协议看 init、horizon、success；随机性看漂移、wear、jitter。按 replay→action round-trip→free-space→contact→task→repeat 找首个偏离。

**机制展开（约 2 分钟）**：真实闭环由 observation hψ、controller Cκ、dynamics fξ 与 protocol P 组成。视觉分 appearance、geometry、time；动力学与控制先用无接触轨迹隔离，free-space 通过后再测 contact/gripper；任务冻结 language/init/reset/horizon/success/denominator；随机性区分 episode、step、drift、rare event。Safety 是响应层。每个 gate 保存 paired timestamp trace，不能从 success=0 直接判层。

**诊断 / 证据**：先核对 sim/real protocol tuple；冻结 real frames 走 processor→policy→decode；对 normalized action 做 unit/frame/gripper/controller round-trip；用安全限幅 command 比较 free-space trajectory/latency；再做 push/slip/grasp micro-bench；最后按 init/task/time/event 分层重复 trial。记录 camera calibration、controller/Hz、action apply、model/contact params、success predicate、episode denominator 和 first divergence。

**项目挂钩**：当前五项目没有 protocol-complete real-hardware Sim2Real bundle。LIBERO/RoboCasa 是 simulator evidence；WAM CoffeePressButton trace 是接口/失败诊断；deployment entry 或高层 robot tool 也不是 real transfer。安全说“我能设计五层 paired audit”，不能说“我在 simulator 做过所以完成 Sim2Real”。

**追问树**：为什么 visual gap 不只是 texture？camera extrinsics 错会怎样？dynamics 与 control 怎样隔离？为什么先测 free-space？contact 为何要单列？task name 相同为何仍不可比？randomness 有哪些时间尺度？safety 是 gap 还是 response？仿真高、真机 0 时第一步查什么？什么证据才能写“完成 Sim2Real”？

**易错点**：把 reality gap 等于 appearance；把 actuator/controller 混入 physics 后无法归因；用抓取直接测全部层；把 i.i.d. noise 当 drift；忽略 init/horizon/success；sim score 高就说 transfer；看到 0-success 就扩大 randomization；把 safety gate 当作已经解决模型 mismatch。

**危险答案**：说“Sim2Real 主要靠纹理随机化”“把所有参数范围加宽即可”“LIBERO/RoboCasa 成功就是 Sim2Real”“相同 action vector 在 sim/real 含义相同”“最终 success=0 已证明是摩擦问题”“当前项目已经有真实硬件迁移结果”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-031 Source Freeze](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html)：五层合同、first-failure ladder、paired matrix 与项目边界。
2. Tobin et al., [Domain Randomization](https://arxiv.org/abs/1703.06907v1)。
3. Peng et al., [Dynamics Randomization](https://arxiv.org/abs/1710.06537v3)。
4. Tan et al., [Sim-to-Real Agile Locomotion](https://arxiv.org/abs/1804.10332v2) 与 OpenAI et al., [Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5)。
5. [Sim2Real Audit D](../sources/vol_04_sim2real_claim_to_mechanism.html)、[Benchmark Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html) 与 [Evidence Manifest](../evidence/evidence_manifest.html)。
