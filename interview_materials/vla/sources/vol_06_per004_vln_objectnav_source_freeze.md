# VOL 06 PER-004 Source Freeze：VLN / ObjectNav 任务、观测与成功协议

> 状态：`source_frozen / VLA-PER-004 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 Vision-and-Language Navigation（VLN）与 ObjectNav 的任务合同、episode/observation/action/goal schema、停止与成功谓词、SPL 等指标以及 simulator-to-real 边界；不把模拟器成功、论文指标或项目中的 grounding 字段写成个人导航成果。

## 问题（Question）

VLN、ObjectNav 和“带语言的物体导航”都涉及视觉、语言与移动动作，但它们的 goal contract、监督信号和 success predicate 并不相同。面试中应先说明任务与 episode schema，再说明 action/stop 如何进入 simulator，最后说明 SR/SPL 等指标到底以什么分母、路径和阈值计算。

最小链路：

```text
episode(scene + start pose + goal/instruction + split)
  → observations(rgb/depth/semantic + pose + text + valid)
  → action(discrete/continuous + stop)
  → simulator transition(navmesh/collision/controller)
  → success predicate + path/length metrics
  → protocol-scoped report (not real-robot success)
```

## 1. 冻结来源与指纹

| 来源 | 类型 / revision | SHA-256（原始文件） | 可支持的事实 | 不能支持的 claim |
| --- | --- | --- | --- | --- |
| [Habitat-Lab README](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/README.md) | official repo；commit `0fb6f43ffe806a8088a171b036336c093bcf604e`；访问 2026-07-18 | `49ffbba6a3e459e382aebcc1724a9682ebb3c4eec85df7f6e2aa92ee0eefa8a7` | Habitat-Lab 是高层 embodied-AI task/train/eval 框架，使用 Habitat-Sim，MIT 代码许可；README 明确提示 v0.3.4 之后不再由 Meta 内部团队主动维护 | 当前本地环境、数据资产或任何项目已经复现官方结果 |
| [ObjectNav task implementation](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/object_nav_task.py) | official source；同一 commit | `a22a9369012bc22b2202ada66cbf2f533527f9579f14037e7a1e84d0724ce0b6` | `ObjectNav-v1`、`ObjectGoalNavEpisode`、`ObjectGoal`、`ObjectViewLocation`、object category/ID sensor 与 view-point 字段 | 所有 ObjectNav benchmark 都使用相同 category map、success radius 或 view-point 生成协议 |
| [Navigation task and measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) | official source；同一 commit | `3ce31b1bb75cc733c09d777e1ff0f18fb99c1882206a9496da648c1bd6ee549d` | `NavigationEpisode` 的 start pose/scene/goals、`StopAction`、`Success` 依赖停止与距离阈值、`SPL` 依赖 success 与路径长度、PointGoal/GPS/Compass 观测 | 只看到类定义就能证明某个实验使用了特定 config、阈值、seed 或 denominator |
| [ObjectNav dataset loader](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/datasets/object_nav/object_nav_dataset.py) | official source；同一 commit | `a04c0e9822085999697a9ea1f19523b74d7a5e06fed674e2f76d3220b95a8408` | `ObjectNav-v1` episode JSON 的 category mappings、scene/episode IDs、goals-by-category、view points 和 shortest paths 读取方式 | 数据文件中的 scene split、goal generation 或评测分母已自动等同于另一版本 |
| [Habitat-Sim README](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/README.md) | official simulator repo；commit `57ee4941dc4765240f0f91f70b2c97a919bf9038`；访问 2026-07-18 | `2422fd0b1c58dc9939fc3e74d6b39415e202df651dd93b87204d3871bfc803b8` | RGB-D/egomotion sensors、navmesh/physics、scene assets 与 headless/sim setup；同样注明 v0.3.4 之后的维护提示 | simulator 中的导航成功等价于真实机器人闭环成功，或场景/传感器/控制频率与本地项目相同 |
| [Habitat-Sim PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h) | official source；同一 commit | `9baeef24a29963e11e34df4446c0809f8106e7c23b065cf25be4f4d2a0a4a1e2` | navmesh 的可行走区域、geodesic shortest path、isNavigable、tryStep/无滑移和 agent-height/radius/slope 约束 | navmesh shortest path 是执行 controller 的真实轨迹，或不同 agent radius/碰撞模型结果可直接比较 |
| [VLN-CE README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md) | official benchmark repo；commit `729d141b2ee10628061ada74dd3a5b9f70faeba5`；访问 2026-07-18 | `33c547d6d6fa8a7deca433c5e441894aad72d676dfca152fea0cd4ef80b9a41c` | 连续环境中的 R2R/RxR instruction-following、Habitat 依赖、R2R/RxR split、trajectory JSONL；README 给出 challenge action/observation contract 示例及 TL/NE/OS/SR/SPL 字段 | README 中的 baseline 数字是可迁移的当前 SOTA，或与其他 Habitat 版本、硬件、数据预处理天然可复现 |
| [R2R paper](https://arxiv.org/abs/1711.07280) | primary paper；CVPR 2018；arXiv version | — | 语言指令驱动的 indoor route following、路径/指令配对与导航评估语境 | R2R 的离散/图导航协议自动等同于 VLN-CE 的连续控制协议 |
| [REVERIE paper](https://arxiv.org/abs/1904.10151) | primary paper；CVPR 2020；arXiv version | — | remote referring expression、导航到物体附近并进行 object grounding；导航成功与目标物体 grounding 是不同层级 | REVERIE 的 object grounding 结果等于 ObjectNav category-goal 成功，或只凭语言 grounding 就证明了移动控制 |
| [ObjectNav Revisited](https://arxiv.org/abs/2006.13171) | primary evaluation paper；arXiv 2020 | — | ObjectNav 指标与评测协议的再审视、不同 success/efficiency 结果的解释风险 | 论文中的诊断自动覆盖用户项目的场景、seed、controller 或真实硬件 |
| [SPL paper](https://arxiv.org/abs/1807.06757) | primary metric paper；2018 | — | Success weighted by Path Length 的定义与导航效率语境 | 只报 SPL 就能恢复 success radius、路径记录、episode filtering 或统计置信区间 |

## 2. 任务 taxonomy：相似输入，不同 goal contract

| 任务 | goal / instruction | 常见 observation | action / stop | 核心 success 语义 |
| --- | --- | --- | --- | --- |
| ObjectNav | 目标物体类别或 object ID；ObjectGoal 还可含 room、view points | RGB/Depth/Semantic、object-goal sensor、pose/GPS/Compass | 离散移动/转向或连续速度；显式 `stop` | 先停止，再检查当前位置到目标点或目标 view-point 的距离是否低于 config 阈值；阈值与 `distance_to` 配置必须随实验冻结 |
| R2R/RxR VLN | 自然语言 route instruction；R2R/RxR 数据还定义 scene、start pose、split 与参考轨迹 | RGB/RGB-D、pose/GPS/Compass、语言 token；连续 VLN 还记录真实轨迹 | 图/离散动作或连续前进/转角/俯仰；终止通常是 `stop` | 目标附近成功与路径效率联合报告；instruction following 不等于 object grounding |
| REVERIE | instruction + referring expression 指向具体物体 | 视觉、语言、pose、候选 object/region | 导航动作 + object selection/grounding | 至少拆成“是否到达目标区域”和“是否选中正确物体”，不能合并为单一导航分数 |

面试回答应先问清楚：目标是类别、实例、房间、坐标还是引用表达式；动作是 nav-graph edge、固定步长、速度控制还是 waypoint；success 是 stop 后距离阈值、视野/IoU、object ID 还是 task-specific predicate。

## 3. Episode / observation / action / goal contract

### 3.1 Episode 最小字段

```text
episode_id
scene_id / scene_dataset_config
start_position (x, y, z)
start_rotation (quaternion)
goals (position/radius 或 ObjectGoal + view_points)
instruction / reference expression（VLN/REVERIE）
shortest_paths（若 protocol 提供）
split / seed / dataset revision
```

`scene_id` 和 `start pose` 决定 reset；`goals` 决定 success 的目标对象；`shortest_paths` 只能作为数据或评估辅助，不能默认代表 agent 实际走过的路径。没有 split、seed、dataset revision 和 episode denominator，单个成功数不能复核。

### 3.2 Observation 合同

至少记录：

- RGB/Depth/Semantic 的 sensor UUID、分辨率、内参/噪声与有效值约定；
- agent pose、GPS/Compass 或其他 frame 定义；
- instruction token、语言、reference expression 与 padding/mask；
- capture/step timestamp、history/stack 规则和缺失传感器 mask；
- simulator 版本、场景资产、navmesh 版本以及 action repeat/control-hz。

一个合法 tensor 不代表语义合同正确：RGB 与 depth 交换、语言 padding 未 mask、pose 在错误 frame 或 terminal observation 重复，均可能保持 shape 正确而让导航结果失真。

### 3.3 Action 与 stop

Habitat-Lab 的 `StopAction` 将 task 的 `is_stop_called` 置为真；`Success` 再结合距离度量与 success distance 判定。VLN-CE README 的 challenge 示例还固定了 30° turn、0.25 m step 和 480×640 RGB-D，这些是特定 challenge contract，不是所有 VLN benchmark 的 universal defaults。连续速度 action 还要冻结速度范围、time step、碰撞/滑移策略和 controller。

### 3.4 Goal 与 viewpoint

ObjectNav 的 `ObjectGoal` 可有 `object_id`、category、room 和 `view_points`。因此“到达物体位置”“进入可见 view-point”“停在阈值半径内”可能是不同协议。若实验把 `distance_to=VIEW_POINTS`、`distance_to=POINT` 或 semantic category 互换，SR/SPL 不可直接横比。

## 4. 成功与效率指标

### 4.1 Success、SR 与停止条件

对每个 episode (i)，先固定 success predicate (S_iin{0,1})：例如 `stop_called == true` 且 geodesic distance 小于 `success_distance`。Success Rate 为

\[
SR = \frac{1}{N}\sum_{i=1}^{N} S_i.
\]

如果任务要求 object ID、view-point 可见性、region IoU 或语言引用匹配，predicate 需要显式写出来；“最终位置看起来接近”不能替代 protocol。

### 4.2 SPL

对成功定义和最短参考路径均已冻结时，常用 Success weighted by Path Length 为

\[
SPL = \frac{1}{N}\sum_{i=1}^{N} S_i\frac{L_i}{\max(P_i,L_i)},
\]

其中 (L_i) 是 protocol 规定的 shortest/geodesic path length，(P_i) 是 agent 实际记录的 path length。失败 episode 的 (S_i=0)，绕路会降低比值。实现中还要明确：是否含 stop 前最后一步、是否按 geodesic 还是 Euclidean、是否按 view-point 集合取最小距离。

### 4.3 VLN 常见配套指标

| 指标 | 含义 | 不能单独证明 |
| --- | --- | --- |
| TL | Trajectory Length | 走得短不代表到达正确目标 |
| NE | final navigation error | 没有 stop 或 success predicate 时不能当 SR |
| OS | oracle success；轨迹中任一步曾到达 | agent 是否知道何时 stop |
| SR | episode-level success ratio | 路径是否高效、是否跨 split 泛化 |
| SPL | success 与路径效率的联合值 | 真实机器人稳定性或任务操作成功 |

指标必须绑定 episode 数、split、scene/goal protocol、action space、controller、seed、dataset revision 和失败 trace。VLN-CE README 的历史 baseline 表只能作为该仓库的参考记录，不能跨版本当作当前比较基线。

## 5. Simulator protocol 与真实机器人边界

| 证据层级 | 最小 artifact | 仍不能支持 |
| --- | --- | --- |
| task schema | dataset JSON、episode 字段、instruction/goal parser、split manifest | agent 学到了有效导航 |
| simulator execution | reset/step log、action space、sensor config、navmesh/scene revision | 真实相机、底盘和控制器成功 |
| offline/teacher-forced | 参考轨迹、action imitation loss、per-step error | closed-loop success |
| simulated closed-loop | 全 episode denominator、SR/SPL/TL/NE/OS、seed 与 failure traces | 跨 simulator、跨 scene asset 或 real-world 泛化 |
| real closed-loop | 真机传感器/控制日志、时间同步、碰撞与安全记录、同 protocol 对照 | 没有 matched sim-real protocol 时的因果归因 |

主要 sim-to-real 差异包括：navmesh 与真实可通行区域、碰撞/滑移模型、相机内外参和噪声、控制周期与延迟、reset/终止条件、场景资产与光照、语言/目标标注以及安全停止机制。即使 simulator SR=1，也只能说明该 simulator protocol 下的 episode 成功。

## 6. 与现有项目的真实挂钩

| 项目 | 当前可连接的节点 | 明确不能升级为 |
| --- | --- | --- |
| OPD / VLM grounding | point/box/text route、坐标与 scorer，可作为导航前的目标 grounding 输入 | VLN/ObjectNav episode、navmesh trajectory、SPL 或真实移动成功 |
| Robot Harness | tool schema、timeout/cancel/compensation，可讨论如何把导航工具接入系统 | Habitat task success、R2R/RxR 指令跟随或移动控制结果 |
| OpenPiVLA | observation/action packaging、policy latency、action chunk contract | 导航 benchmark 的 SR/SPL，除非有独立 episode 与轨迹 artifact |
| WAM / Cosmos | simulator rollout provenance 与 metric boundary | ObjectNav/VLN 结果、3D navigation 或真机闭环 |
| UWM / LIBERO | simulator reset、任务协议、closed-loop evaluation 的证据分层 | 语言导航或 ObjectNav 的目标/指标 |

## 7. Source gate 结论与下游范围

已冻结：

1. VLN、ObjectNav、REVERIE 的 goal、instruction、action 与 success predicate 不能混写；先冻结 episode contract，再解释指标。
2. Habitat-Lab 的 ObjectNav success 依赖 stop、距离度量和 config；ObjectGoal 的 category/ID/view-point 字段不等同于统一的“到物体位置”。
3. SPL 必须绑定最短路径、实际轨迹、success predicate、episode denominator 与版本化 protocol；跨 benchmark/版本比较前要核对 action space、scene、split、controller 和数据预处理。
4. simulator success、offline proxy 与 real robot closed-loop 是不同证据层；现有 OPD/Harness/WAM/UWM 证据不支持个人 VLN/ObjectNav 成果。

知识页与 `VLA-PER-004` 原子题卡已将 episode JSON、instruction/action mask、stop-success-SPL 计算、REVERIE 的双层 success、navmesh 与连续控制 failure tree 展开；本地 benchmark run artifact 仍缺。

当前 verdict：`WARN`。来源足以冻结任务与评估合同，但没有用户本地 VLN/ObjectNav 运行 artifact、真实机器人导航日志或可复现 benchmark bundle。

## References

1. [Habitat-Lab frozen README](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/README.md)、[ObjectNav task](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/object_nav_task.py)、[navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)。
2. [Habitat-Sim frozen README](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/README.md) 与 [PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h)。
3. [VLN-CE frozen README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
4. [R2R](https://arxiv.org/abs/1711.07280)、[REVERIE](https://arxiv.org/abs/1904.10151)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)、[SPL](https://arxiv.org/abs/1807.06757)。
5. 本仓库前置切片：[PER-001 Grounding](vol_06_per001_grounding_coordinate_source_freeze.html)、[PER-002 3D Lift](vol_06_per002_3d_lift_frame_source_freeze.html)、[PER-003 Multi-view/Temporal](vol_06_per003_multiview_temporal_source_freeze.html)。
