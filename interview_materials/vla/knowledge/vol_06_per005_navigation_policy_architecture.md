# VOL 06 Perception / Grounding / Navigation：Navigation Policy Architecture（PER-005）

> 状态：`drafted / VLA-PER-005 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[PER-005 Navigation Policy Architecture Source Freeze](../sources/vol_06_per005_navigation_policy_architecture_source_freeze.html)。  
> 前置知识：[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)、[PER-004 VLN / ObjectNav](vol_06_per004_vln_objectnav.html)。

## 问题（Question）

一个导航 policy 可以直接从视觉/语言历史回归动作，也可以维护 semantic map、预测 waypoint，再交给 planner/controller。两者的差别不只是“端到端 vs 模块化”，还涉及记忆、partial observability、长时域探索、frame、action age、stop/replan 和延迟预算。

本页回答：

1. map-free、semantic map-based、waypoint 和 hybrid policy 的接口与 trade-off 是什么？
2. semantic exploration 如何把观测、地图、目标类别先验和 frontier/subgoal 连成闭环？
3. waypoint / subgoal 传给 planner/controller 时必须携带哪些 frame、unit、uncertainty 和 freshness 字段？
4. 如何拆分 capture、perception、map/planner、policy、controller 和 actuation latency？
5. 怎样通过 ablation、episode trace 和项目证据，避免把公开机制写成个人导航结果？

## 知识地图位置与前置依赖

```text
PER-001 point/box/text grounding
          ↓
PER-002 depth / calibration / frame
          ↓
PER-003 multi-view / temporal schema
          ↓
PER-004 task / episode / success / SPL contract
          ↓
PER-005 policy architecture / exploration / waypoint / controller
          ↓
closed-loop evaluation / sim2real / VOL 07 project claims
```

GOSE、VLN-CE waypoint、Habitat-Lab/Sims 的公开实现和论文是机制参照。当前五项目的 PER-004 navigation artifact gate 为 `0_local_direct_navigation_bundles`，因此本页讲架构与审计方法，不宣称个人已实现或提升导航。

## 1. 30 秒直觉：记忆在哪里，动作在哪里落地

所有架构都要回答三件事：

```text
我记住什么？（history / map / semantic prior）
我输出什么？（low-level action / waypoint / subgoal）
谁负责最后执行？（learned policy / planner / controller）
```

map-free policy 把记忆压进 recurrent/transformer state，直接输出动作或局部 waypoint；map-based policy 显式维护空间/语义记忆，再挑选探索目标；waypoint policy 把长 horizon 拆成中间目标；hybrid policy 将学习模块与几何 planner/controller 分开。没有明确的 frame、stop、replan 和 latency，架构图无法说明真实闭环行为。

## 2. 架构 taxonomy

| 架构 | 典型数据流 | 优点 | 主要风险 |
| --- | --- | --- | --- |
| map-free / reactive | image + language + pose/history → action 或 local waypoint | 端到端、运行时简单、部署组件少 | partial observability、长时域探索、hidden-state drift、stale observation；要记录 history、action age 与 replan |
| semantic map-based | perception + pose → occupancy/semantic map → goal/frontier score → planner → action | 可积累历史、支持长时域探索、子目标较可解释 | mapping/calibration/pose error、map stale、显存和延迟；要保存 map revision、更新轨迹、planner config、ablation |
| waypoint policy | language/visual state → next waypoint/subgoal → local controller | 将长序列动作压缩为中间接口，适合连续环境 | waypoint frame/scale、tracking error、stop/replan 与 controller latency；要有 waypoint-to-action trace |
| hybrid learned + classical | learned semantic proposal → classical planner/controller | 可将语义理解和几何/安全约束分层调试 | 接口 mismatch、planner latency、目标抖动、model/planner 归因混淆；需要 matched component ablation |

这些是可组合的设计家族，不是互斥模型名称。例如 map-free encoder 可以输出 waypoint，再交给 controller；map-based explorer 也可以使用 learned goal scoring。面试中先画清接口，再讨论模型优劣。

## 3. Map-free policy：简单不等于没有记忆

### 3.1 状态与 partial observability

真实导航通常只能看到局部 RGB-D/语义和有限历史，因此 policy 近似：

\[
 a_t = \pi_\theta(o_{t-k:t},\; l,\; s_t),
\]

其中 \(o\) 是视觉/传感器 observation，\(l\) 是 instruction/goal，\(s_t\) 可以是 pose/proprio/history state。即使没有显式 map，Transformer cache、RNN hidden state 或 stacked frames 仍是记忆；需要冻结 history length、stride、mask、timestamp 和 reset 行为。

### 3.2 常见 failure

- 目标暂时不可见时，policy 没有探索先验，容易原地抖动或重复路径；
- long horizon 中 hidden state 与实际 pose 漂移，局部动作仍合法但全局方向错误；
- inference latency 或 action repeat 变化，使训练时的 action age 与部署时不一致；
- 只看 imitation/action loss，未记录 stop、replan、collision 和 episode success。

map-free 并不自动意味着低延迟：视觉 encoder、语言 cross-attention、policy server queue 和 controller 仍要计入 latency ledger。

## 4. Semantic map-based exploration

### 4.1 最小闭环

GOSE 的公开机制可抽象为：

```text
RGB-D + pose
  → local geometry / semantic observation
  → episodic semantic map
  → target-category prior + frontier/object scoring
  → exploration subgoal
  → planner/controller
  → execute, update map, repeat
```

地图不是把过去图片简单拼起来，而是带有坐标、时间、语义和有效性合同的状态：

```text
map_revision
cell/frame/metric resolution
pose source + timestamp + uncertainty
occupancy / obstacle / semantic evidence
last_update / confidence / decay policy
candidate object / frontier / subgoal
```

### 4.2 Category prior 与探索边界

目标类别先验可以改变候选 frontier 或 subgoal 的排序，但不能伪装成已观测到目标：

```text
score(frontier) = geometry + semantic_prior + uncertainty/value
```

若 prior 只来自公开论文或训练数据，它支持的是探索机制解释；只有在项目中保存了 map snapshot、候选分数、执行轨迹和 matched ablation，才可讨论个人实现或 uplift。

### 4.3 Map-based failure

| 失败层 | 例子 | 需要的诊断 |
| --- | --- | --- |
| geometry | depth/pose/calibration 错、地图坐标漂移 | roundtrip、pose error、map revision |
| semantic | object label 错、类别先验 shortcut、遮挡 | per-class confusion、candidate evidence、view trace |
| exploration | frontier 重复、目标排序错误、无 fallback | subgoal score、visited/replan trace |
| planner | navmesh island 无路径、路径过长 | planner status、geodesic/actual path |
| controller | waypoint tracking、collision、latency | action trace、tracking error、controller log |

## 5. Waypoint / subgoal interface

### 5.1 中间目标 schema

waypoint 不能只是 `(x, y)` 或一个未注明单位的 pose；至少保留：

```text
subgoal_id / source_views / instruction_span
frame_id / position-or-heading / unit
created_at / observation_timestamp / observation_age
uncertainty / valid / stop_allowed
replan_policy / horizon / controller_budget
```

同一 `(x, y)` 在 agent、camera、map、world frame 中含义不同；resize、map origin、heading convention 和 unit 变化会让 shape 正确的 waypoint 语义错误。`valid=false`、age 超预算或 uncertainty 超阈值时，应重新 grounding、replan、safe hold 或 reject，不能静默执行。

### 5.2 Waypoint 与 controller 的边界

waypoint policy 优化的是中间目标预测，不等于 controller 已经完成跟踪。至少要分别记录：

```text
predicted waypoint
→ planner/local path
→ controller command
→ pose_after / tracking error / collision
→ stop or replan reason
```

如果只报告 waypoint prediction accuracy，而没有实际 action trace、controller frequency、tracking tolerance 和 stop predicate，不能称为 closed-loop success。

## 6. Planner、controller 与 stop/replan

### 6.1 重新规划触发

常见 trigger 包括：

- 固定时间或执行步数；
- tracking error、collision 或 controller timeout；
- map revision、目标重新出现或 semantic confidence 变化；
- observation age、uncertainty 或 action deadline 超阈值；
- stop predicate 满足或发现无可行路径。

每次 replan 应有 `reason` 和 `source_timestamp`，否则无法判断动作抖动来自模型、地图还是调度策略。

### 6.2 Stop 是独立协议

PER-004 已冻结：Habitat-Lab 的 `StopAction` 设置 `is_stop_called`，success 还依赖 task-specific distance/predicate。PER-005 进一步要求 policy、planner 和 controller 共享 stop contract：

```text
stop_allowed = valid_goal
                and distance/view/object predicate satisfied
                and observation_age <= budget
```

如果 policy 预测“停”，controller 仍在执行旧 chunk，或 evaluator 没记录 terminal reason，模型与指标就不是同一个系统。

## 7. Latency ledger：平均 FPS 不够

一个闭环周期至少拆分：

```text
T_capture + T_transfer + T_encode/ground + T_map/planner
  + T_policy + T_controller + T_actuation
```

若 observation 在 \(t_o\) 捕获、action 在 \(t_a\) 生成，则：

\[
age_{action}=t_a-t_o+T_{queue}+T_{communication}+T_{execution\ delay}.
\]

对窄空间、动态目标或短 stop threshold，平均 latency 不能替代 p50/p95、queue wait、replan count、stale-action rate 和 per-episode trace。action chunk 长度 (H) 还需结合 control-hz、repeat 和 replan cadence 换算成物理执行时间。

## 8. 可审计的 policy loop 伪代码

```python
def navigation_step(obs, memory, protocol, planner, controller):
    # 1. Validate identity, timestamp, frame, unit and freshness.
    rec = validate_observation(obs, protocol.schema)
    if not rec.valid or rec.age > protocol.max_observation_age:
        return safe_hold(reason="stale_or_invalid_observation")

    # 2. Update explicit map only when this architecture declares one.
    if protocol.architecture in {"semantic_map", "hybrid"}:
        memory = update_semantic_map(memory, rec, protocol.map_contract)
        candidate = score_frontiers_or_objects(
            memory, rec.goal, protocol.exploration_contract
        )
    else:
        candidate = None

    # 3. Predict low-level action or a typed waypoint/subgoal.
    proposal = policy_or_waypoint_model(rec, memory, candidate)
    proposal = validate_subgoal(proposal, protocol.subgoal_contract)

    if protocol.stop_predicate(proposal, rec, memory):
        return stop(reason="predicate_satisfied", source=rec.timestamp)
    if not proposal.valid or proposal.uncertainty > protocol.max_uncertainty:
        return safe_hold(reason="invalid_subgoal")

    # 4. Planner/controller remain explicit evidence boundaries.
    local_path = planner.plan(proposal, protocol.planner_contract)
    command = controller.track(local_path, protocol.controller_contract)
    return command, memory, {
        "observation_age": rec.age,
        "replan_reason": proposal.replan_reason,
        "latency_breakdown": collect_latency_trace(),
    }
```

伪代码的关键不是某个模型名称，而是把架构选择、map 更新、waypoint validation、stop、safe hold、planner、controller 和 latency trace 分开。没有这些边界，端到端模型的一个输出无法解释失败归因。

## 9. 实验与 evidence ladder

### 9.1 必须固定的比较因素

| 因素 | 例子 | 不固定时的风险 |
| --- | --- | --- |
| policy family | map-free / map-based / waypoint / hybrid | 把组件变化当作 backbone uplift |
| memory | history length、map size、semantic prior | 长时域优势无法归因 |
| planner/controller | same planner、controller、control-hz | policy 与执行器混淆 |
| timing | queue、latency、repeat、replan | stale action 伪装成模型失败 |
| task protocol | scene、split、goal、stop、denominator | SR/SPL 不可比 |

### 9.2 最小 ablation

map-based claim 至少应比较：去 map、去 semantic prior、固定 planner/controller；waypoint claim 至少应比较：direct action、waypoint + same controller、matched horizon/replan。每个分支保存 episode-level result、failure type、latency 和 raw trace，而不是只保留最终均值。

### 9.3 证据阶梯

```text
schema/interface
  → map/subgoal mechanism
  → planner/controller trace
  → simulated closed-loop SR/SPL + denominator
  → matched sim-real / real navigation safety log
```

当前 PER-004 navigation artifact gate 只达到“公开机制 + 项目接口边界”；OPD/Harness/OpenPiVLA/WAM/UWM 没有 map/subgoal/action bundle，不能跨越到个人 navigation result。

## 10. 项目映射与真实性边界

| 项目 | 可以连接的机制 | 当前不能声称 |
| --- | --- | --- |
| OPD | point/box/text grounding 可作为目标候选或 semantic observation 前端 | 没有 semantic map、frontier、waypoint、planner 或 ObjectNav success |
| Robot Harness | semantic-navigation tool schema、scope、timeout/cancel/compensation 可作为高层服务接口 | 没有低层 controller、navmesh trajectory、VLN/ObjectNav episode 或真机导航 |
| OpenPiVLA | action packaging、normalizer、chunk、latency 可迁移到 waypoint/policy server | 没有导航 scene/split/stop/SR/SPL artifact |
| WAM / Cosmos | rollout provenance、controller/horizon、metric ladder 可用于 simulator evidence 讨论 | 没有 map-based exploration、waypoint 或 navigation result |
| UWM / LIBERO | reset、closed-loop protocol、failure/evidence ladder 可迁移到评估设计 | 没有语言导航或 ObjectGoal 结果 |

安全口径是：可以解释如何设计导航 policy 和审计 planner/controller 接口，但当前项目材料不支持“我实现了 GOSE/waypoint/VLN/ObjectNav 并取得某个结果”。

## 11. 面试回答检查表

回答 PER-005 至少覆盖：

1. 先画出 observation/memory → policy/map/waypoint → planner/controller → stop/replan 的接口；
2. 比较 map-free、map-based、waypoint、hybrid 的记忆、长时域和 failure trade-off；
3. 说明 semantic map 的坐标、pose、revision、semantic evidence、frontier/subgoal 和 stale policy；
4. 给出 waypoint 的 frame/unit/uncertainty/age/valid/replan schema；
5. 拆 capture、perception、map/planner、policy、controller、actuation latency；
6. 用 matched ablation 和 episode trace 区分 model、map、planner、controller、protocol effect；
7. 把 OPD/Harness/OpenPiVLA/WAM/UWM 的连接限定在现有 evidence gate 内。

## 12. 结论与下一步

导航 policy architecture 的核心不是选择一个“更先进”的家族，而是把记忆、空间、动作接口、controller、stop、replan 和 timing 变成可审计合同。GOSE、VLN-CE waypoint 与 Habitat-Sim 提供公开机制参照；当前本地项目仍没有 map/subgoal/action/episode bundle，因此本页保持 `WARN`。

对应的 `VLA-PER-005` 原子题卡已同步并保持 `unseen`；下一 bounded slice 进行 PER-001..005 的真实口述训练，或补本地导航 artifact。

## References

1. [PER-005 Navigation Policy Architecture Source Freeze](../sources/vol_06_per005_navigation_policy_architecture_source_freeze.html)。
2. [GOSE](https://arxiv.org/abs/2007.00643)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)。
3. [VLN-CE paper](https://arxiv.org/abs/2004.02857)、[Waypoint Models](https://arxiv.org/abs/2110.02207)、[VLN-CE frozen README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
4. [Habitat-Lab navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) 与 [Habitat-Sim PathFinder](https://github.com/facebookresearch/habitat-sim/blob/57ee4941dc4765240f0f91f70b2c97a919bf9038/src/esp/nav/PathFinder.h)。
5. [R2R](https://arxiv.org/abs/1711.07280) 与 [REVERIE](https://arxiv.org/abs/1904.10151)。
6. [PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html) 与 [PER-004 VLN / ObjectNav](vol_06_per004_vln_objectnav.html)。
