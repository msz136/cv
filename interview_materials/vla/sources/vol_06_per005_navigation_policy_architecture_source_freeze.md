# VOL 06 PER-005 Source Freeze：Navigation Policy Architecture、语义探索与 Waypoint 接口

> 状态：`source_frozen / VLA-PER-005 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片只冻结 map-free / map-based、semantic exploration、waypoint policy、planner/controller interface 与 latency 的公开机制；不把公开 baseline、论文结果或 Robot Harness 的高层工具接口写成个人导航实现。

## 问题（Question）

ObjectNav/VLN policy 可以直接从 observation 回归 action，也可以维护局部/全局 semantic map、预测 waypoint，再交给 planner/controller。面试中应说明这些架构如何处理 partial observability、长时域探索、stop/replan、action age 和 controller latency，而不是只说“端到端更简单”或“地图一定更可靠”。

最小链路：

```text
RGB-D / language / pose / memory
  → map-free policy OR semantic map / waypoint proposal
  → planner / subgoal selector
  → local controller / simulator action
  → stop / replan / latency contract
  → protocol-scoped navigation metrics
```

## 1. 冻结来源与指纹

| 来源 | 类型 / revision | 可支持的事实 | 不能支持的 claim |
| --- | --- | --- | --- |
| [Habitat-Lab README](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/README.md) | official repo；commit `0fb6f43ffe806a8088a171b036336c093bcf604e`；2026-07-18 | Habitat-Lab 提供 embodied task、训练/评估和 Habitat-Sim 接口；支持 imitation、RL、导航与 instruction-following | 用户项目已使用同一 baseline、config、scene 或训练结果 |
| [Habitat-Lab navigation task/measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) | official source；同一 commit | `NavigationTask`、移动 action、`StopAction`、distance/success/SPL measure 的任务层接口 | planner/controller 延迟、地图质量或真实机器人行为已由类定义证明 |
| [Habitat-Sim PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h) | official source；commit `57ee4941dc4765240f0f91f70b2c97a919bf9038` | navmesh、geodesic shortest path、isNavigable、tryStep 与 agent geometry constraints | shortest path 是实际 controller trace，或 map-free policy 已使用同一规划器 |
| [VLN-CE README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md) | official benchmark repo；commit `729d141b2ee10628061ada74dd3a5b9f70faeba5` | 连续 VLN 的 R2R/RxR 数据、Habitat 依赖、waypoint baseline 入口、action/observation 与 latency-sensitive evaluation context | README baseline 数字是当前通用 SOTA，或用户项目已复现该结果 |
| [Object Goal Navigation using Goal-Oriented Semantic Exploration](https://arxiv.org/abs/2007.00643) | primary paper；arXiv v2；2020 | GOSE 将 episodic semantic map、目标类别语义先验和探索/规划模块组合用于 ObjectNav；论文讨论 map-based modular 与 end-to-end baseline 的差异 | 论文的模拟器/真机结果属于用户项目，或 semantic map 一定优于 map-free policy |
| [ObjectNav Revisited](https://arxiv.org/abs/2006.13171) | primary evaluation paper；2020 | ObjectNav 中探索、指标和评估解释的风险；提醒比较 map-based/end-to-end 方法时要固定 protocol | 论文诊断自动覆盖用户的 scene、seed、controller 或 episode denominator |
| [Beyond the Nav-Graph: VLN in Continuous Environments](https://arxiv.org/abs/2004.02857) | primary paper；ECCV 2020 | VLN 从离散 nav-graph 迁移到连续环境的动作、轨迹和评估语境 | 连续环境下的 waypoint/controller 已被用户项目实现或获得相同结果 |
| [Waypoint Models for Instruction-guided Navigation in Continuous Environments](https://arxiv.org/abs/2110.02207) | primary paper；2021 | waypoint prediction 作为语言/视觉到连续导航之间的中间接口；需要与低层执行和评估合同配合 | waypoint prediction 本身等于闭环成功，或不需要 controller/latency/stop contract |
| [R2R](https://arxiv.org/abs/1711.07280) / [REVERIE](https://arxiv.org/abs/1904.10151) | primary task papers | 指令路线、referential object grounding 与导航/目标选择的任务差异 | 任务数据或论文 baseline 可以当作个人训练或导航 artifact |

## 2. 架构 taxonomy：policy 的记忆和动作接口不同

| 架构 | 典型链路 | 优点 | 主要 failure / 证据要求 |
| --- | --- | --- | --- |
| map-free / reactive | image/language/pose/history → action or local waypoint | 端到端、运行时简单、无需显式地图维护 | partial observability、长时域探索、drift、stale observation；要有 action-age、replan 与 closed-loop trace |
| semantic map-based | perception/pose → occupancy/semantic map → goal scoring/exploration → planner → action | 能积累历史、做全局/长时域探索、解释子目标 | mapping/calibration/pose error、显存与延迟、map stale；要有 map revision、pose/observation sync、exploration trace 与 ablation |
| waypoint policy | language/visual state → next waypoint/subgoal → local controller | 把长序列动作压缩为中间目标，适配连续环境 | waypoint frame/scale、controller tracking、stop/replan 与 action age；需 waypoint-to-action trace |
| hybrid learned + classical | learned semantic proposal → classical planner/controller | 可将学习和安全/几何约束分开调试 | 接口 mismatch、planner latency、目标抖动和 reward/metric 归因；需 matched component ablation |

这些是设计家族，不是互斥的模型名称；一个系统可以用 map-free encoder 预测 waypoint，再由 classical controller 执行，也可以在 map-based explorer 中使用 learned goal scoring。

## 3. Planner / controller interface

### 3.1 中间目标必须带 frame 和 freshness

waypoint 或 semantic subgoal 不应只是两个浮点数，应至少包含：

```text
subgoal_id / source_views / instruction_span
frame_id / position-or-heading / unit
created_at / observation_timestamp / observation_age
uncertainty / valid / stop_allowed
replan_policy / horizon / controller_budget
```

同一 `(x, y)` 在 agent、camera、map 或 world frame 中含义不同；旧 waypoint 继续执行可能因 agent 已转向、map 更新或目标被遮挡而失效。`valid=false`、age 超预算或 uncertainty 超阈值时，应 re-ground、replan、safe hold 或 reject，而不是静默执行。

### 3.2 延迟账本

对每个闭环周期，至少拆分：

```text
T_capture + T_transfer + T_encode/ground + T_map/planner
  + T_policy + T_controller + T_actuation
```

若 action 在 (t_a) 生成，而 observation 在 (t_o) 捕获，action age 为 (t_a-t_o) 加上排队、通信和执行延迟。对移动目标或窄空间，平均 latency 不足以解释失败；需要 p50/p95、queue wait、replan count、stale-action rate 和 per-episode traces。

### 3.3 Stop / replan / action repeat

必须同时冻结：

- stop predicate：距离、view-point、object grounding 或 language goal；
- replan trigger：固定步数、时间、tracking error、map change、confidence/age；
- action repeat / control-hz / controller timeout；
- collision、safe hold、cancel、compensation 和 terminal reason。

只报告“每步预测 waypoint”而不报告何时重规划、何时停止和何时拒绝动作，无法复现闭环行为。

## 4. Semantic exploration 的最小机制

GOSE 论文的公开机制可以抽象为：

```text
RGB-D + pose
  → local geometry / semantic observations
  → episodic semantic map
  → target-category prior / frontier or goal scoring
  → exploration subgoal
  → planner/controller
  → update map and repeat
```

关键不只是“有一张地图”，而是：

1. map 的坐标、更新频率、pose 来源和历史窗口一致；
2. target category prior 只影响候选探索排序，不能伪装成已看到目标；
3. frontier、object candidate、stop 和 fallback 的 predicate 明确；
4. map error、pose drift、遮挡和 stale memory 要进入失败分析；
5. map-based uplift 必须通过去 map、去 semantic prior、固定 planner/controller 的 matched ablation 归因。

## 5. 证据矩阵与项目边界

| Claim 层级 | 最小 artifact | 当前五项目状态 |
| --- | --- | --- |
| policy interface | observation/action/waypoint schema、frame/unit、latency fields | OpenPiVLA/Harness 可讨论接口；不等于导航实现 |
| map/planner mechanism | map snapshot、pose/semantic update、subgoal trace、planner config | 未发现 VLN/ObjectNav map bundle |
| closed-loop simulator | episode manifest、scene/navmesh revision、SR/SPL、failure trace | PER-004 navigation gate：0 local-direct bundle |
| real navigation | sensor/controller/collision/safety log、matched sim protocol | 未发现 |

OPD 的 point/box/text 可以作为目标 grounding 前端，Robot Harness 的 semantic-navigation 可以作为高层工具接口；WAM/UWM/OpenPiVLA 的现有材料不能证明 map-based、waypoint 或真实导航闭环已经由个人完成。

## 6. Source gate 结论与下游范围

已冻结：

1. map-free、semantic map-based、waypoint 和 hybrid policy 是不同的 memory/action interface 家族，不能只用“端到端/模块化”二分。
2. planner/controller 接口必须绑定 frame、unit、uncertainty、observation age、replan、stop、repeat、latency 和 failure reason。
3. GOSE、VLN-CE waypoint、Habitat-Sim navmesh 和 ObjectNav/VLN 论文提供机制与 protocol 参照，不支持个人项目已经实现或提升了导航结果。
4. map-based 或 waypoint claim 至少需要 map/subgoal/action trace、matched ablation 和 episode-level denominator；当前五项目不满足。

知识页已补充 map-free vs map-based 伪代码、semantic map 更新与 frontier scoring、waypoint frame/latency contract、planner/controller A/B 与 failure tree；仍待 `VLA-PER-005` 题卡。

当前 verdict：`WARN`。来源足以冻结架构 taxonomy 与接口审计框架，但没有用户本地 navigation implementation/run artifact。

## References

1. [Habitat-Lab frozen README](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/README.md)、[navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)。
2. [Habitat-Sim PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h)。
3. [VLN-CE frozen README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
4. [GOSE](https://arxiv.org/abs/2007.00643)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)、[VLN-CE paper](https://arxiv.org/abs/2004.02857)、[Waypoint Models](https://arxiv.org/abs/2110.02207)。
5. [R2R](https://arxiv.org/abs/1711.07280) 与 [REVERIE](https://arxiv.org/abs/1904.10151)。
