# VOL 04 VLA-WM-036 原子题卡：Contact、Friction、Compliance 与 Gripper Semantics

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-036  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-036 Knowledge](../knowledge/vol_04_world_model_sim2real_wm036_contact_friction_compliance_gripper.html)；来源边界见 [WM-036 Source Freeze](../sources/vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html)。

## friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-036</b> · friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点？</summary>

**面试意图**：判断你能否把“把 friction 调一下”升级为 hybrid contact、multi-dimensional friction、soft constraint/solver、collision geometry、gripper execution contract、micro-bench 与 matched real evidence。

**30 秒回答**：接触是模式切换：摩擦、间隙或刚度变化会让stick/slip切换。先核gripper符号、模式、range/limit与free-space；再按材料做press/slip/hold/lift，保存contact/force/current。固定模型比较friction、compliance、geometry、gripper与solver。

**机制展开（约 2 分钟）**：区分command、aperture、contact、force、hold/lift和task success。摩擦含sliding/torsional/rolling；compliance与solref/solimp、timestep/solver不是同一物理量。range按material/load/wear条件化，保存contact pair、normal/tangent force、slip、penetration、current和object pose。free-space失败回查action/controller。做factor/combined/overwide与sim/real micro-bench；当前缺真机trace，不声称transfer。

**诊断 / 证据**：冻结 simulator build、collision mesh、material、friction(3)、condim、solref/solimp、margin、timestep/integrator/solver 与 controller。保存 gripper scalar→controller→finger aperture/force/current round-trip；按 free-space、touch、press、slip、pinch/hold、lift、transport、task 记录 contact pair/point/normal、normal/tangent/torsional force、slip velocity、penetration、object pose、saturation 与 first divergence。固定 checkpoint 做 friction/compliance/geometry/gripper/solver/combined/overwide 对照。

**项目挂钩**：OpenPiVLA 支持 controller/rollout 的 partial provenance，UWM 只记录 grasp/contact failure hypothesis；当前缺 contact/gripper/solver manifest、material table、force/current/contact trace、micro-bench、matched arms、真机结果和 ownership。安全说“能设计 contact micro-bench”，不能把 LIBERO success、gripper scalar 或 simulator contact state 写成个人真机抓取成果。

**追问树**：contact 为什么 non-smooth？stick/slip 如何判断？sliding/torsional/rolling friction 分别是什么？elliptic/pyramidal cone 有何差别？solref/solimp 是真实刚度吗？timestep 为什么影响 bounce？visual mesh 与 collision mesh 差别？1 一定表示 close 吗？position/force gripper 有何不同？command/contact/hold/lift 怎样分层？为什么先 free-space？怎样测 friction/compliance？怎样做 matched solver/gripper sweep？

**易错点**：一个 global friction；忽略 torsional/rolling；把 solref 当材料刚度；只改 friction 不记 solver/timestep；visual mesh 当 collision mesh；所有 gripper 都 `1=close`；command 当 aperture；contact 当 grasp；没有 force/current；free-space 错仍调 contact；不同 object/surface 不条件化；同时换 controller/checkpoint 后归因 contact。

**危险答案**：说“friction=1 就够了”“抓取只看是否 close”“两指 contact 就等于成功”“调 solref 就拟合真实橡胶”“sim grasp success 证明真机抓取”“当前项目已通过 contact randomization 提升真机成功率”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-036 Source Freeze](../sources/vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html)：hybrid contact、friction/compliance/solver、gripper contract、micro-bench、matched gates 与项目边界。
2. MuJoCo, [Contact model](https://mujoco.readthedocs.io/en/stable/computation/index.html#soft-contact-model) 与 [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)。
3. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
4. robosuite, [Panda gripper @ v1.5.1](https://github.com/ARISE-Initiative/robosuite/blob/51cc01785bab80ffeed20da15e67d7dd4140e76a/robosuite/models/grippers/panda_gripper.py)；[Evidence Manifest](../evidence/evidence_manifest.html)。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-037`，不批量生成 WM-037..038，不创建 `coaching_state.md`。

