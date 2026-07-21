# VOL 06 Perception / Grounding / Navigation：PER-005 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-PER-005`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-005 Navigation Policy Architecture Knowledge](../knowledge/vol_06_per005_navigation_policy_architecture.html)；来源边界见 [PER-005 Source Freeze](../sources/vol_06_per005_navigation_policy_architecture_source_freeze.html)。

## 导航 policy 的记忆、子目标与执行边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-005</b> · map-free、map-based、waypoint policy 如何比较？planner/controller 接口和 latency 要冻结哪些字段？</summary>

**面试意图**：判断你能否把 policy family、显式记忆、中间目标、planner/controller、stop/replan 和时延放进同一可审计闭环，而不是只说端到端或模块化。

**30 秒回答**：先按接口比较：map-free 直接出 action；map-based 维护语义地图并选 subgoal；waypoint 预测中间目标交给 controller。取舍在探索、partial observability、延迟和可解释性；都要冻结 frame/unit、uncertainty、age、stop/replan。公开结果不能写成个人导航。

**机制展开（约 2 分钟）**：接口分三层：map-free(history→action)、map-based(map→subgoal)、waypoint(subgoal→controller)。subgoal 冻结 frame/unit、timestamp/age、uncertainty、valid、stop/replan。延迟记各阶段及 p95/stale-action。比较固定 planner/controller、hz、scene/split、stop/分母，做去 map、去 semantic prior、direct-action ablation；无 map/action trace 和 episode bundle，只讲机制，不称导航结果。

**诊断 / 证据**：为每个 episode 保存 observation/action schema、map revision、pose/semantic update、subgoal frame/unit/age/uncertainty、planner status、controller command、stop/replan reason 和 latency breakdown。做 map-free↔map-based、direct-action↔waypoint、去 semantic prior 的 matched ablation，并固定 scene、split、seed、controller、control-hz、action repeat 和 denominator。用 stale-action、tracking error、collision、replan 次数和 terminal reason 分开归因；若只有论文表格、接口草图或单次 rollout，证据停在机制层。

**项目挂钩**：OPD 可连接 point/box/text grounding 作为目标候选前端；Robot Harness 可连接 semantic-navigation 高层接口、timeout/cancel/compensation；OpenPiVLA 可连接 observation/action packaging、chunk 与 latency；WAM/UWM 可连接 rollout provenance 和 simulator/evaluation ladder。安全口径是“我能设计并审计这些接口”，不声称五个项目已有 map-based、waypoint、VLN/ObjectNav 或真机导航结果。

**追问树**：map-free 没有显式地图时记忆在哪里？semantic prior 如何避免伪装成已观测目标？waypoint 的 frame/unit 错了会怎样？为什么 action age 比平均 FPS 更关键？controller 固定后如何归因 policy uplift？stop 与 replan 谁负责？没有 episode bundle 时你能声称什么？

**易错点**：把 waypoint prediction 当 closed-loop success；把 map revision、pose、unit 或 timestamp 丢掉；只报平均 latency；改变 planner/controller 却归因 policy；把论文 baseline、远端路径或高层工具接口写成个人导航结果。

**危险答案**：说“map-based 一定优于端到端”“waypoint 就等于 controller 已执行”“平均 FPS 足够说明实时”“只要 final distance 小就成功”或“OpenPiVLA/WAM/UWM 已证明我的导航闭环”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-005 Navigation Policy Architecture Knowledge](../knowledge/vol_06_per005_navigation_policy_architecture.html)：policy taxonomy、semantic exploration、waypoint contract、planner/controller、latency 与 evidence ladder。
2. [PER-005 Navigation Policy Architecture Source Freeze](../sources/vol_06_per005_navigation_policy_architecture_source_freeze.html)：GOSE、VLN-CE waypoint、Habitat-Lab/SIM 与项目边界。
3. [GOSE](https://arxiv.org/abs/2007.00643)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)。
4. [VLN-CE](https://arxiv.org/abs/2004.02857)、[Waypoint Models](https://arxiv.org/abs/2110.02207)。
5. [Habitat-Lab navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) 与 [Habitat-Sim PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h)。
