# VOL 08 SYS-003：Robot Fleet 与 Multi-tenant GPU Scheduling

> 状态：`drafted / SYS-VLA-003 / knowledge_9_of_phase / card_1_of_1_unseen / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[SYS-003 Source Freeze](../sources/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling_source_freeze.html)。

## 问题（Question）

当机器人数量、模型 revision、租户和 GPU 类型同时增长时，怎样把“一个 policy server”扩展成可控的 robot fleet？本页把 Kubernetes/Volcano/Ray/Triton/NVIDIA/ROS 2 的公开机制转译成面试系统设计语言，同时明确哪些只是 design inference，哪些没有个人项目证据。

不要把 fleet 设计理解成“加一个 scheduler”。真正的合同需要同时覆盖 tenant/robot/model identity、资源向量、placement、queue/fairness、preemption、model replica/cache、robot lease、rollout/canary、成本和 action freshness。

## 1. 直觉与专业定义

### 1.1 Fleet scheduler

通俗地说，fleet scheduler 决定“哪个机器人请求、哪个模型副本、哪块 GPU、什么时候执行”。它必须同时考虑资源够不够、请求是否兼容、租户是否超额、机器人 lease 是否有效，以及动作返回时是否已经过期。

专业地说，scheduler 是从请求集合 (mathcal{Q})、节点/副本集合 (mathcal{N}) 和资源向量 (R) 到 placement 与 admission 决策的控制平面。Kubernetes 官方 scheduler 暴露 QueueSort、Filter、Score、Reserve/Permit、Bind 等阶段；这些阶段描述 Pod placement，不自动理解 VLA 的 camera schema、normalizer、action age 或 controller safety。

### 1.2 Multi-tenancy、capacity、fairness、priority、freshness

这四个词不能混用：

- **capacity**：一个 tenant/queue 最多能占多少 GPU、MIG 或其他资源；
- **fairness**：长期资源占用或 queue share 是否按权重平衡；
- **priority**：关键请求在冲突时谁先服务；
- **freshness**：机器人动作是否仍在 deadline 和 action-age 合同内。

Volcano 的 fair-share/capacity/queue-priority 设计分别提供 weight、guarantee/capability/deserved、priority/reclaim 机制；它们不能自动推出 VLA 的 deadline fairness。让高优先级离线训练抢占 serving GPU，可能改善训练等待，却恶化动作新鲜度。

### 1.3 Logical resource 与 physical resource

Kubernetes device plugin、Ray logical/custom resources 和 Triton named resources 都能表达“需要某类资源”。但逻辑 reservation 不等于显存/带宽隔离；NVIDIA time-slicing 或 MIG 还要配合 workload、driver、memory、tail latency 和 failure 观测，不能只看 GPU utilization。

## 2. Fleet identity 与状态所有权

### 2.1 最小 identity/schema 合同

| 类别 | 字段示例 | 面试时要回答的边界 |
| --- | --- | --- |
| tenant | `tenant_id`, `quota_class`, `priority`, `budget` | 配额、优先级、公平性、成本如何归属 |
| robot | `robot_id`, `robot_type`, `capability_set`, `lease_epoch`, `controller_endpoint` | 能力匹配、fencing、controller 路由 |
| policy | `model_revision`, `processor_revision`, `normalizer_revision`, `action_schema_version` | warm cache 与 action 语义兼容 |
| request | `request_id`, `session_id`, `capture_ts`, `deadline_abs`, `H`, `D`, `valid_until` | queue、batch、action age、幂等与 stale-response |
| placement | `gpu_type`, `mig_profile`, `memory_budget`, `network_zone`, `replica_id` | Filter/Score、locality、异构设备和成本 |

`robot_id` 不能仅凭 WebSocket 连接获得永久控制权。lease epoch、model/schema revision 和 controller acknowledgement 必须共同进入执行边界；这是 fleet 设计推断，不是当前 OpenPI 或五个项目已有字段。

### 2.2 State ownership 表

| 状态 | owner | 失效/恢复动作 | 证据边界 |
| --- | --- | --- | --- |
| tenant quota / queue | scheduler control plane | reject、requeue、reclaim、downgrade | Kubernetes/Volcano 机制；无 VLA local implementation |
| model replica / GPU reservation | orchestrator + inference runtime | warm/cold、drain、reschedule、load smoke | Ray/Triton/Kubernetes mechanism；不证明 checkpoint lineage |
| robot lease | fleet control plane + controller | renew、epoch bump、fence、hold/stop | Lease/ROS lifecycle 启发的设计合同 |
| action chunk | policy client/broker | expiry、stale drop、replan、fallback | SYS-002 OpenPI evidence；无 fleet-wide fencing proof |
| rollout/canary | release controller | promotion、per-tenant gate、rollback | design inference；项目只有局部 eval/rollout hooks |

## 3. Capacity 与 placement 数学

### 3.1 Resource vector admission

将一个请求抽象为资源向量 (R=(g,m,c,n,s))，分别表示 GPU/accelerator、显存、CPU、网络和模型/缓存空间；节点剩余容量为 (C)。必要的 admission 条件可写为：

\[
R_{\mathrm{req}}\preceq C_{\mathrm{node}},
\qquad
\mathrm{compatible}(M,S,N,\Gamma)=1.
\]

其中 (M) 是 model revision，(S) 是 action/schema，(N) 是 normalizer，(Gamma) 是 controller contract。逐维容量约束来自 Kubernetes/Ray/Triton 的资源机制；compatibility 是 VLA 系统设计推断，用来防止不同 shape、normalizer 或 controller mode 被错误合批。

### 3.2 多目标调度代价

单独最小化 GPU 空闲率是不够的。一个可用于面试澄清的设计目标是：

\[
J=\alpha W_q+\beta L_{tail}+\gamma A_{action}+\delta M_{deadline}+\eta F_{fair}+\lambda C_{run}.
\]

(W_q) 是 queue wait，(L_{tail}) 是 inference tail latency，(A_{action}) 是 action age，(M_{deadline}) 是 deadline miss rate，(F_{fair}) 是 tenant share 偏差，(C_{run}) 是运行成本。权重不是上游默认值，必须由 task criticality、tenant SLA 和安全边界决定；应在固定 workload matrix 上做 matched A/B，而不是凭单次 utilization 报公平或性能提升。

## 4. Queue、Fairness 与 Preemption

### 4.1 Queue 层级

Kubernetes ResourceQuota 限制 namespace 的 aggregate resource/object consumption；PriorityClass/Preemption 允许高优先级 Pod 驱逐低优先级 Pod；Volcano queue 机制可表达 weight、capacity、guarantee、deserved 和 reclaim。面试回答应说明四个层级的组合：

1. admission 先检查 tenant quota 与 robot/model compatibility；
2. queue order 再考虑 priority、fair-share deficit 和 deadline budget；
3. placement 通过 Filter/Score 选择 GPU 类型、MIG profile、network zone 和 warm replica；
4. preemption 前先判断被抢占的是 offline job、可重试 inference，还是带物理 side effect 的 controller path。

### 4.2 Freshness 不是 fairness

旧 observation 可以丢弃，已确认要执行的 action 不能无条件 latest-wins。一个 tenant 获得“公平 GPU share”并不保证它的机器人动作在 deadline 内返回；相反，一个安全 critical robot 可能需要保留 capacity，但仍要受到 lease、controller ack 和 independent stop 的约束。

### 4.3 抢占与降级

推荐的 fail-closed 顺序是：拒绝新请求 → 复用仍新鲜的 action chunk → 切换已验证 fallback → drain/terminate 无副作用的 offline replica → 最后才考虑抢占；任何涉及 controller side effect 的请求都要先丢弃 stale response、提升 lease epoch，并由 controller 完成 hold/stop。Kubernetes preemption 和 Volcano reclaim 只提供调度机制，不证明这个安全顺序已由上游或个人项目实现。

## 5. Heterogeneous GPU、Replica 与 Cache

### 5.1 GPU placement

NVIDIA device plugin 支持 GPU discovery/health、MIG 与 CUDA time-slicing 入口；Ray 可用 logical/custom resource 和 placement group 表达 accelerator、memory、PACK/SPREAD 或 gang scheduling；Triton model configuration 以 `max_batch_size`、batch dimension、instance group 等约束 batching shape。

应把以下字段纳入 placement key：GPU 型号/MIG profile、显存预算、模型 revision、processor/normalizer revision、camera/prompt/action shape、network locality 和 controller mode。GPU 可见不代表模型能加载；加载成功也不代表 capture→apply tail latency 达标。

### 5.2 Replica 与 named resource

Triton rate limiter 的 named resource/count 适合表达“某 model instance 执行时占用多少份资源”；Ray Serve 的 Controller/Proxy/Replica 结构适合表达请求队列、replica 数量和 per-replica GPU reservation。两者都不能自动提供 tenant fairness、robot lease 或 physical safety。

模型 cache 至少应绑定 `model_revision + processor_revision + normalizer_revision + action_schema_version`，并区分 warm hit、cold load、OOM、driver mismatch 和 stale bundle。cache hit 只能改善启动或吞吐的一个环节，不能替代 checkpoint hash、load smoke 或 closed-loop evaluation。

## 6. Robot Lease、Lifecycle 与 Fencing

Kubernetes Lease 文档支持 lock、heartbeat 和 single-instance coordination；ROS 2 managed-node lifecycle 支持资源 acquisition/release 与 supervisory state。将其组合为 robot fleet lease 时，应额外冻结：

- `lease_epoch` 单调递增，旧 epoch 的 action 回包必须拒绝；
- renew 失败进入 `EXPIRED`，不能继续发送新 action；
- model revision、normalizer 和 controller endpoint 与 lease 绑定；
- controller acknowledgement、hold/stop 和 independent e-stop 由机器人侧拥有；
- reconnect 必须重新握手，不能复用旧 session 或旧 action chunk。

这是一套 fail-closed 设计要求。当前五个项目的 inventory/ledger 没有统一 robot lease、epoch fencing、controller ack 或多机器人 replay artifact，不能说已经实现。

## 7. Rollout、Canary、Cost 与观测

### 7.1 正常路径

```text
# Design path; not an existing user fleet implementation.
request(identity + observation + deadline)
  → tenant quota / queue admission
  → compatible schema + model-revision grouping
  → Filter / Score / reserve GPU or placement group
  → warm replica + named rate-limiter resources
  → infer + parse + denormalize + safety boundary
  → robot lease/epoch + controller acknowledgement
  → per-tenant metrics, canary gate, replay and rollback record
```

### 7.2 Canary gate

模型 promotion 至少要绑定 model/processor/normalizer/action-schema revision、tenant/robot cohort、fixed task/seed、episode artifact、capture→apply tail latency、deadline miss、fallback、lease conflict 和 success predicate。不能只用 offline loss、GPU utilization 或一条 summary JSON 作为 fleet canary。

### 7.3 Cost 与 SLO

成本账本应分 GPU reservation、cold-start、network、storage/cache、preemption/retry 和机器人空闲时间；SLO 应分 queue wait、inference tail、action age、deadline miss、lease availability、fallback 和 task success。Ray Serve 的 replica queue、Triton rate limiter、Volcano queue 和 Kubernetes quota 是机制入口，不是本地 SLO 结果。

## 8. 面试级伪代码

```python
def schedule_fleet_request(req, cluster, registry, clock):
    # 1. Reject stale or malformed identity before touching GPU or robot state.
    validate_identity(req.tenant_id, req.robot_id, req.model_revision)
    validate_schema_and_normalizer(req)

    # 2. Check quota, lease epoch, deadline budget, and side-effect class.
    if not quota_allows(req) or not lease_is_current(req):
        return reject_or_fallback(req, reason="admission")

    # 3. Keep only resources and replicas compatible with the VLA contract.
    candidates = filter_nodes(cluster, req.gpu_type, req.mig_profile, req.shape)
    candidates = score_for_locality_fairness_freshness(candidates, req)
    placement = reserve_or_queue(candidates, req.resource_vector)
    if placement is None:
        return reject_or_fallback(req, reason="capacity")

    # 4. Route to a warm model replica; the limiter controls instance occupancy.
    replica = acquire_replica(registry, req.model_revision, req.normalizer_revision)
    result = replica.infer(req, deadline_abs=req.deadline_abs)

    # 5. Fence old results and require controller acknowledgement at the edge.
    if result.lease_epoch != current_lease_epoch(req.robot_id):
        return discard_stale_result(req, result)
    action = denormalize_and_limit(result.action_chunk, req.normalizer_revision)
    return controller_apply_with_ack(req.robot_id, action, req.valid_until)
```

伪代码中的 `filter_nodes`、`reserve_or_queue`、`acquire_replica` 和 `controller_apply_with_ack` 需要具体系统实现后才能成为 local-direct。它展示的是面试设计顺序，不是 Kubernetes、Ray 或任何一个个人项目的现成函数。

## 9. 实现映射与项目真实性边界

| 证据层 | 可用映射 | 不可升级的 claim |
| --- | --- | --- |
| official upstream | Kubernetes scheduler/quota/Lease、NVIDIA device plugin、Volcano queue、Triton limiter、Ray placement/Serve、ROS lifecycle | 用户已部署 VLA fleet、SLO、公平性或 physical safety |
| local evidence | 五项目 inventory/ownership ledger 的 trainer/eval/timeout/rollout hooks | 统一 control plane、multi-tenant load test、GPU placement、lease fencing |
| design inference | identity/schema、multi-objective scheduler、cache key、canary、fencing | 已有 runtime、checkpoint lineage、candidate end-to-end ownership |
| unverified | p99/p999、tenant fairness、cold-start uplift、robot fleet success | 任何 production/hard-real-time/多机器人安全强结论 |

五项目具体 hook：

- OpenPiVLA：offline WebSocket、in-process broker、normalizer/action shape/parser 风险；没有 fleet scheduler 或 lease。
- Robot Harness：tool scope、lock、timeout、compensation、训练/eval route；不是 VLA inference scheduler。
- OPD：multi-expert route、teacher schedule、ZeRO/config、holdout；不是 multi-tenant serving。
- WAM：simulator launcher、chunk/controller schema、diagnostic trace；不是 heterogeneous GPU fleet。
- UWM/LIBERO：launcher、task mapping、fixed protocol、loader diagnosis；不是 production fleet 或 cross-robot serving。

## 10. 60 秒回答与禁说清单

### 10.1 60 秒回答模板

“我会把 fleet 拆成 identity、admission/queue、placement、replica、robot lease 和 rollout 六层。请求必须带 tenant、robot、model/processor/normalizer、schema、deadline 和 lease epoch；先检查 quota、兼容性和 freshness，再按 GPU/MIG、显存、network locality 与 warm replica 做 Filter/Score。fair-share、priority、capacity 和 freshness 分开衡量，不能只看 GPU utilization。模型 promotion 要绑定 cohort、episode、tail latency、deadline miss、fallback 和 success predicate。Lease 失效时提升 epoch、丢弃旧 action，controller 自己负责 ack/hold/stop/e-stop。Kubernetes、Volcano、Ray、Triton 只能作为机制来源；我当前项目只有局部 eval/timeout/rollout hooks，不能称作已经上线的 production fleet。”

### 10.2 不能说的强 claim

- “Kubernetes/Volcano/Ray/Triton 已经构成我的 production VLA fleet。”
- “GPU utilization 高就说明租户公平、动作 deadline 满足。”
- “GPU time-slicing、MIG 或 Pod preemption 天然提供显存隔离和物理安全。”
- “Lease renew 成功就等于 controller 已安全执行 action。”
- “Ray placement group、Triton rate limiter 或 Volcano fair-share 证明我的项目有 multi-robot load test。”
- “五个项目的局部脚本、配置或 Git author 等于我完成了 fleet control plane。”

## 11. 结论与下一步

fleet 系统设计的高分点是把资源调度和机器人语义连接起来：capacity 约束 GPU，fairness 约束长期 share，priority 决定冲突顺序，freshness 约束动作可执行性，lease/fencing 保护 robot ownership，canary/replay 保护 revision promotion。当前 source freeze 已核对 15 个公开机制和五项目证据缺口；尚未证明统一 fleet service、tenant/robot/model trace、GPU fairness A/B、model cache lineage、lease fencing、controller ack 或个人 ownership。

下一步：保持 `SYS-VLA-003` 题卡未生成；先用本页 60 秒模板做一次口述，或补一个 tenant/robot/model/request/placement trace artifact。未取得真实回答前不创建 `coaching_state.md`，不启动 `SYS-VLA-004`。

## 参考文献（References）

1. [SYS-003 Source Freeze](../sources/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling_source_freeze.html)：15 个 pinned sources、local evidence SHA 与 15/15 probes。
2. Kubernetes [scheduler](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/scheduling-eviction/kube-scheduler.md)、[Priority/Preemption](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/scheduling-eviction/pod-priority-preemption.md)、[ResourceQuota](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/policy/resource-quotas.md)、[Lease](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/architecture/leases.md)。
3. NVIDIA [Kubernetes device plugin](https://github.com/NVIDIA/k8s-device-plugin/tree/248164727d5d8bac7024a8e12a13e69246cf0969) 与 Volcano [fair-share/capacity/priority](https://github.com/volcano-sh/volcano/tree/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0)。
4. NVIDIA Triton [model configuration/rate limiter](https://github.com/triton-inference-server/server/tree/d1e6320698eda052ea2c3deaba4069958171caa5)。
5. Ray [resources/placement groups/Serve](https://github.com/ray-project/ray/tree/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3) 与 ROS 2 [node lifecycle](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md)。
6. 本仓库 [ENG-016](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)、[ENG-018](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)、[ENG-019](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)、[ENG-022](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html) 与 [五项目 evidence inventories](../evidence/projects/openpivla_claim_evidence_inventory.html)。
