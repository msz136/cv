# VOL 06 Perception / Grounding / Navigation：VLN 与 ObjectNav（PER-004）

> 状态：`drafted / VLA-PER-004 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[PER-004 VLN / ObjectNav Source Freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html)。  
> 前置知识：[PER-001 Grounding](vol_06_per001_grounding_coordinate.html)、[PER-002 3D Lift](vol_06_per002_3d_lift_frame.html)、[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)。

## 问题（Question）

VLN、ObjectNav 和 REVERIE 都把视觉、语言和移动动作放在同一条链上，但它们不是同一个任务。面试回答不能从“输入一张图和一句话，输出动作”直接跳到模型结构；应先冻结 episode 与 goal contract，再解释 observation/action/stop，最后说明 success、SPL 和 simulator-to-real 证据。

本页回答：

1. VLN、ObjectNav、REVERIE 的目标与监督有什么不同？
2. 一个可复现的 episode、observation、action、goal schema 应包含哪些字段？
3. Habitat-Lab 的 `stop`、距离度量、ObjectGoal/view-point 如何进入 success？
4. SR、SPL、TL、NE、OS 分别测什么，为什么不能脱离 protocol 比较？
5. 如何把任务协议接到 VLA grounding、planner、controller 和项目真实性边界？

## 知识地图位置与前置依赖

```text
PER-001 point/box/text grounding
          ↓
PER-002 depth / calibration / frame
          ↓
PER-003 multi-view / temporal schema
          ↓
PER-004 VLN / ObjectNav task + evaluation contract
          ↓
planner / action chunk / controller / closed-loop evidence
```

Habitat-Lab 是任务与评估框架，Habitat-Sim 负责场景、传感器和导航/物理模拟；VLN-CE 将 R2R/RxR 指令迁移到连续环境。R2R、REVERIE 和 ObjectNav Revisited 是任务/评估语境的原始论文。它们提供公开协议参照，不等于用户项目已经运行过这些 benchmark。

## 1. 30 秒直觉：先定义“到哪里”，再讨论“怎么走”

导航回答的最小闭环是：

```text
episode(scene + start pose + goal/instruction + split)
  → observation(rgb/depth/semantic + pose + language + valid)
  → action(discrete/continuous + stop)
  → simulator transition(navmesh + collision + controller)
  → success predicate + path metrics
  → protocol-scoped report
```

同一个 `stop` 动作，在 PointNav、ObjectNav、R2R 和 REVERIE 中可能依赖不同目标字段、距离定义或 object-grounding 条件。没有 episode denominator、split、scene revision、action space、success threshold 和实际轨迹，单独的“成功率”不具备可复核性。

## 2. 任务 taxonomy：输入相似，目标合同不同

| 任务 | goal / instruction | 典型 observation | action / termination | success 的核心问题 |
| --- | --- | --- | --- | --- |
| ObjectNav | 目标类别或 object ID；`ObjectGoal` 可带 room 与 `view_points` | RGB/Depth/Semantic、object-goal、pose/GPS/Compass | 移动/转向或连续速度 + `stop` | 停止时是否在 protocol 指定的目标点或 view-point 距离内 |
| R2R/RxR VLN | 自然语言 route instruction、scene、start pose、split、参考路径 | RGB/RGB-D、pose、语言 token；连续环境还记录轨迹 | nav-graph action 或连续前进/转角/俯仰 + `stop` | 是否到达目标附近，以及走过的路径是否高效 |
| REVERIE | instruction + referring expression 指向具体物体 | 视觉、语言、pose、候选 object/region | 导航动作 + object selection/grounding | 是否到达目标区域与是否选中正确物体，通常应分层报告 |

三个常见混淆：

- ObjectNav 的“椅子”是类别 goal，不等同于 REVERIE 的某个 referring expression 实例。
- R2R 的参考路线用于 instruction-following 与路径评估，不等同于 agent 必须逐点复现的 controller trace。
- grounding hit、进入物体附近和 task success 是不同证据层；point/box/text scorer 不能自动变成移动成功。

## 3. Episode contract：把 reset 和评估分母冻结

### 3.1 最小字段

```text
episode_id
scene_id / scene_dataset_config
start_position: [x, y, z]
start_rotation: [qx, qy, qz, qw]
goals: position/radius 或 ObjectGoal + view_points
instruction / reference_expression（VLN/REVERIE）
shortest_paths（若数据协议提供）
split / seed / dataset_revision
```

Habitat-Lab 的 `NavigationEpisode` 以 episode/scene ID、起点位姿和 goals 组织导航任务；ObjectNav 数据集进一步保存 category mappings、`ObjectGoal`、`ObjectViewLocation` 和可选 shortest paths。字段存在只说明 schema 可解析，不说明该 episode 已经被完整执行。

### 3.2 Reset 与数据泄漏

reset 时至少要记录：

- scene asset 与 scene-dataset revision；
- start pose、agent embodiment、navmesh 和 collision/controller 配置；
- language/object goal parser 的版本；
- split（seen/unseen 等）、seed 和 episode ID；
- 是否加载 reference path、teacher action 或 oracle 信息。

如果把 shortest path、未来轨迹或 terminal observation 误放进 policy observation，就会产生 future leakage。teacher-forced action accuracy 也不能当作 closed-loop success。

### 3.3 Goal 与 view-point

`ObjectGoal` 的字段可能包括 `object_id`、`object_category`、room 信息和 `view_points`。因此至少要区分：

```text
target point        → 到几何点的距离
target view-point   → 到可见目标的候选位置集合的距离
category goal       → 目标类别是否满足
instance/object ID  → 是否找到指定实例
```

若 config 在 `POINT` 和 `VIEW_POINTS` 之间切换，或将 semantic category 与 instance ID 混用，SR/SPL 就不再是同一任务的数字。

## 4. Observation contract：合法 tensor 不等于语义正确

### 4.1 视觉、语言与状态

建议将每个 observation 记录为带 provenance 的结构，而不是裸字典：

```text
rgb/depth/semantic
  + sensor_uuid / resolution / intrinsics / noise policy
pose / gps / compass
  + frame_id / timestamp / calibration revision
instruction / reference expression
  + language / token_ids / attention_mask
valid / presence / observation_age
  + missing-sensor and terminal-observation policy
```

PER-003 的 camera identity、timestamp、presence mask 在这里成为导航输入合同；如果 RGB 与 depth 对调、语言 padding 未 mask、pose frame 错位或重复 terminal frame，shape 检查仍可能通过，但 policy 学到的是错误关联。

### 4.2 连续环境中的时间合同

对每个动作 (a_t)，应保留：

```text
observation_timestamp
action_timestamp
control_hz / action_repeat
controller_delay
observation_age
replan_or_stop_policy
```

动作 chunk 的长度 (H) 不能只看数组维度；若控制频率为 (f)，近似执行时长是 (H/f)，还要加 action repeat、通信和 controller delay。旧 observation 上计算的目标可能在机器人移动后已经 stale，应触发 re-grounding、缩短 horizon、safe hold 或 action reject。

## 5. Action 与 stop：从任务动作到 controller

### 5.1 离散与连续 action

常见 action 层级如下：

| 层级 | 示例 | 必须冻结的字段 |
| --- | --- | --- |
| nav-graph edge | next viewpoint / shortest-path edge | graph、edge semantics、oracle 是否可见 |
| fixed-step simulator | `move_forward`、`turn_left/right`、look up/down | 步长、转角、碰撞和 action repeat |
| velocity control | linear/angular velocity | velocity range、time step、滑移/碰撞策略 |
| waypoint/controller | target pose 或 local waypoint | frame、controller、latency、tracking tolerance |

VLN-CE README 的 challenge 示例使用固定 turn angle、step size 和 RGB-D resolution；这是一个特定 benchmark contract，不是所有 VLN 或真实机器人系统的默认值。

### 5.2 `stop` 不是“模型结束了”

Habitat-Lab 的 `StopAction` 会设置 task 的 `is_stop_called`。随后 `Success` 还要依赖距离度量与 success distance；只在目标附近经过但没有调用 stop，按该实现可能仍是失败。相反，某些 benchmark 的成功谓词还包括 object ID、region/IoU、视野或引用表达式匹配，不能用一个通用的“距离小于阈值”替代全部任务。

### 5.3 最小动作执行日志

```text
episode_id, step_id
observation_timestamp, action_timestamp
action_type, action_parameters, repeat
pose_before, pose_after, collision, controller_status
stop_called, terminal, failure_reason
```

没有 action trace，就无法判断失败来自 grounding、规划、controller、碰撞、延迟还是终止条件。

## 6. Success、SR、SPL 与配套指标

### 6.1 Success predicate 与 SR

先为每个 episode 定义 (S_i\in\{0,1\})。一个 Habitat 风格的导航例子是：

```text
S_i = 1{stop_called_i == true
        and distance_to_goal_i < success_distance}
```

实际任务还可能要求 object category/ID、view-point 可见性、region IoU 或 language reference match。Success Rate 为：

\[
SR=\frac{1}{N}\sum_{i=1}^{N}S_i.
\]

这里的 (N) 必须是明确的 evaluated episodes；过滤掉失败、重复 episode 或不同 split 后再报 SR，会改变指标含义。

### 6.2 SPL

在 shortest path (L_i)、实际轨迹长度 (P_i) 和 success predicate 都冻结时：

\[
SPL=\frac{1}{N}\sum_{i=1}^{N}S_i\frac{L_i}{\max(P_i,L_i)}.
\]

解释：成功但绕路，(L_i/P_i) 变小；失败 episode 的 (S_i=0)。实现仍需注明：

- (L_i) 是 navmesh geodesic、graph path、view-point 集合最小值还是其他参考；
- (P_i) 是否包含 stop 前最后一步、controller 微步和重复 action；
- 是否按 episode、任务、seed 或 scene 聚合；
- success threshold、episode filtering、终止/超时规则。

### 6.3 TL、NE、OS 与“高分陷阱”

| 指标 | 解释 | 不能单独证明 |
| --- | --- | --- |
| TL | Trajectory Length | 到达正确目标 |
| NE | final navigation error | agent 是否正确 stop、是否高效 |
| OS | Oracle Success：轨迹中曾到达 | agent 的 stopping policy 正确 |
| SR | episode-level success ratio | 路径效率或跨 split 泛化 |
| SPL | success × path efficiency | 真机稳定性、碰撞安全或操作成功 |

例如 OS 高而 SR 低，可能表示 agent 经过目标但不会停止；SR 高而 SPL 低，可能表示到达但路径绕行；NE 低但 SR 低，可能是 stop predicate 或阈值问题。面试时先拆 failure taxonomy，再谈模型 uplift。

## 7. 一个可审计的 evaluator 伪代码

```python
def evaluate_episode(episode, trace, protocol):
    # 1. Verify denominator and identity before computing a metric.
    assert trace.episode_id == episode.episode_id
    assert trace.scene_revision == protocol.scene_revision
    assert trace.split == protocol.split

    # 2. Reconstruct the executed path, not the reference shortest path.
    path = reconstruct_path(trace.poses, trace.controller_steps)
    path_len = geodesic_or_declared_length(path, protocol.path_metric)

    # 3. Compute task-specific goal distance/predicate.
    goal_distance = distance_to_goal(
        trace.final_pose, episode.goals,
        mode=protocol.distance_to,  # POINT or VIEW_POINTS, for example
    )
    stop_ok = trace.stop_called and trace.terminal_reason == "stop"
    success = protocol.success_predicate(
        episode=episode,
        final_pose=trace.final_pose,
        goal_distance=goal_distance,
        stop_ok=stop_ok,
        object_selection=trace.object_selection,
    )

    # 4. Only then compute SR/SPL and retain all provenance.
    shortest_len = shortest_reference_length(episode, protocol)
    spl = float(success) * shortest_len / max(path_len, shortest_len)
    return {
        "success": int(success),
        "spl": spl,
        "tl": path_len,
        "ne": goal_distance,
        "protocol": protocol.id,
        "failure_reason": classify_failure(trace, success),
    }
```

关键设计不是公式本身，而是 `protocol.success_predicate`、`distance_to`、`path_metric`、`scene_revision` 和 episode identity 不能被 evaluator 隐式猜测。所有失败样本和 denominator 都应保留，便于 paired comparison 与置信区间分析。

## 8. Habitat-Sim / Habitat-Lab 的 simulator 边界

Habitat-Sim 的 `PathFinder` 以 navmesh 近似可通行区域，可查询 geodesic path、`isNavigable`、island 和 try-step；navmesh 由 agent height、radius、最大爬升、坡度等约束影响。Habitat-Lab 则在上层组织 task、dataset、sensor、action 和 measures。

这意味着：

1. shortest geodesic path 是 simulator/navmesh 参考，不是 controller 实际轨迹；
2. 改变 agent radius、navmesh 参数、scene asset 或碰撞/滑移策略，可能改变 success 与 SPL；
3. simulator RGB-D、reset 和同步条件不自动等于真机相机、底盘和时间系统；
4. VLN-CE README 中的 baseline 数字只能在相同 repo、数据、预处理、硬件与 evaluator 语境下解释。

## 9. Grounding → navigation → control 的失败树

```text
任务失败
├─ goal/语言解析
│  ├─ 类别、实例、room、reference expression 混淆
│  └─ instruction token / language mask / split 错误
├─ perception / grounding
│  ├─ point/box 坐标或 frame 错误
│  ├─ 多视角未做 common-frame association
│  └─ stale observation / invalid sensor 未被 mask
├─ planning
│  ├─ navmesh island 无路径
│  ├─ stop/replan/horizon policy 不合适
│  └─ shortest path 与 actual path 混淆
├─ controller / simulator
│  ├─ action repeat、速度、转角或 latency 不匹配
│  ├─ collision/sliding 与 protocol 不同
│  └─ terminal / timeout / stop 记录错误
└─ evaluation / evidence
   ├─ denominator、split、scene revision 不一致
   ├─ SR/SPL 聚合或 shortest path 定义改变
   └─ simulator proxy 被写成真机成功
```

这棵树适合把“模型没到目标”拆成可验证的故障，而不是把所有失败归因于 backbone 或语言理解。

## 10. 与个人项目的真实连接

| 项目 | 可回答的连接点 | 当前不能声称 |
| --- | --- | --- |
| OPD / VLM grounding | point/box/text route、坐标变换、strict/lenient scorer 可作为导航前的目标 grounding 讨论 | 没有 VLN/ObjectNav episode、navmesh trajectory、SPL 或真实移动成功证据 |
| Robot Harness | tool schema、timeout/cancel/compensation 可用于讨论导航服务的接口和失败恢复 | 没有 Habitat task success、R2R/RxR 指令跟随或底盘控制 benchmark |
| OpenPiVLA | observation/action packaging、latency、chunk/replan contract 可迁移到导航 policy server | 没有导航 split、episode denominator 或 SR/SPL artifact |
| WAM / Cosmos | simulator rollout provenance、controller/horizon 和 metric boundary 可用于比较 simulator evidence 层 | 没有 ObjectNav/VLN 结果、3D navigation 或真机闭环 |
| UWM / LIBERO | reset、任务协议、closed-loop eval 与 evidence ladder 可迁移到 benchmark 设计 | 没有语言导航目标或 ObjectNav success |

当前项目证据只支持这些“接口与审计方法”的连接，不支持把现有项目包装成 VLN/ObjectNav 经验。

## 11. 面试回答检查表

回答 PER-004 至少覆盖：

1. 先区分 VLN、ObjectNav、REVERIE 的 goal/instruction/success contract；
2. 说清 episode 的 scene、start pose、goal、split、seed、revision 和 denominator；
3. 说明 RGB-D、pose、language、timestamp、mask 与 observation age；
4. 区分 nav-graph、fixed-step、velocity、waypoint/controller action 和 `stop`；
5. 给出 success predicate、SR、SPL，并说明 shortest path 与 actual path 的区别；
6. 用 failure tree 分离 grounding、planning、controller、simulator 和 evaluator 问题；
7. 明确 simulator、offline proxy、simulated closed-loop、real closed-loop 的证据阶梯；
8. 把 OPD/Harness/WAM/UWM 的项目挂钩限定在真实 artifact 支持的范围内。

## 12. 结论与下一步

VLN/ObjectNav 的难点不是把语言接到 policy，而是让 goal、observation、action、stop、simulator 和 evaluator 在同一个 protocol 中闭合。Habitat-Lab/Habitat-Sim/VLN-CE 提供可审计的公开实现参照；R2R、REVERIE、ObjectNav Revisited 与 SPL 论文提供任务和指标语境。当前本地项目没有 VLN/ObjectNav run bundle，因此本页保持 `WARN`，不生成个人导航结果。

对应的 `VLA-PER-004` 原子题卡已生成并保持 `unseen`；下一 bounded slice 进行 PER-001..004 的真实口述训练，或补本地导航 artifact，不把公开 baseline 写成个人结果。

## References

1. [PER-004 VLN / ObjectNav Source Freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html)。
2. [Habitat-Lab frozen README](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/README.md)、[ObjectNav task](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/object_nav_task.py)、[navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)。
3. [Habitat-Sim frozen README](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/README.md) 与 [PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h)。
4. [VLN-CE frozen README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
5. [R2R](https://arxiv.org/abs/1711.07280)、[REVERIE](https://arxiv.org/abs/1904.10151)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)、[SPL](https://arxiv.org/abs/1807.06757)。
6. [PER-001 Grounding](vol_06_per001_grounding_coordinate.html)、[PER-002 3D Lift](vol_06_per002_3d_lift_frame.html)、[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)。
