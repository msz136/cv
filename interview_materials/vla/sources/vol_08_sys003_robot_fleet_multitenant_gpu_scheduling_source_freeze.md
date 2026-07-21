# VOL 08 SYS-003 Source Freeze：Robot Fleet 与 Multi-tenant GPU Scheduling

> 状态：`source_frozen / SYS-VLA-003 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本页冻结 fleet identity、GPU/accelerator placement、queue/fairness、capacity/preemption、model replica/cache、robot lease、rollout/canary 与五项目真实性边界；下游 knowledge/card 已在独立 bounded slice 生成，仍不把 Kubernetes、Volcano、Ray 或 Triton 的公开机制写成个人项目已上线的 fleet。
> 前置：[VOL 08 Coverage-Gap Audit](vol_08_coding_system_design_coverage_gap_audit.html)、[SYS-VLA-001 source](vol_08_sys001_vla_training_eval_platform_source_freeze.html)、[SYS-VLA-002 source](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html) 与 VOL 05 的 [ENG-016](vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)、[ENG-018](vol_05_eng018_scheduler_preemption_retry_source_freeze.html)、[ENG-019](vol_05_eng019_config_resolution_run_identity_source_freeze.html)、[ENG-022](vol_05_eng022_policy_server_resilience_source_freeze.html)。

## 问题（Question）

当机器人数量、模型 revision、租户和 GPU 类型同时增长时，怎样把“一个 policy server”扩展成可控的 robot fleet？需要冻结哪些 tenant/robot/model identity、resource vector、placement、queue/fairness、preemption、model cache、robot lease、rollout/canary 与 cost/SLO 合同，才能回答系统设计追问？

## 1. 结论先行

1. Kubernetes scheduler 的官方合同是 `QueueSort → Filter → Score → Reserve/Permit → Bind` 等可配置阶段；它支持把 Pod 资源请求与节点能力分离，但不理解 VLA 的 action age、camera schema、normalizer 或 robot safety。
2. Kubernetes ResourceQuota、PriorityClass/Preemption 和 Lease 分别提供租户资源上限、优先级/抢占与共享资源租约机制。把 `tenant_id/robot_id/model_revision` 放进 fleet API、把 Lease 用作 robot ownership/fencing，是系统设计推断，不是 Kubernetes 自动拥有的机器人语义。
3. NVIDIA device plugin 暴露 GPU、健康状态、MIG 与 CUDA time-slicing 入口；Volcano 的 fair-share/capacity/priority 设计提供 queue weight、guarantee/capability/deserved 与 reclaim 机制；这些机制仍需和 VLA 的 deadline、action freshness 与 side-effect controller 组合。
4. Triton rate limiter 用命名 resource/count 控制 model instance 的并发占用，model configuration 的 `max_batch_size` 约束 dynamic/sequence batching 的 shape 合同。Ray resources、placement groups、Serve controller/proxy/replica 则提供 logical resource、gang placement、replica queue 与 per-replica GPU reservation 的另一种实现路径。
5. fleet scheduler 的公平性不能只看 GPU utilization：应同时记录 queue wait、inference tail、action age、deadline miss、tenant share、robot lease conflicts、model cold-start、fallback 和 cost。当前五个项目只有局部训练/eval/timeout/rollout hooks；没有统一 fleet control plane、multi-tenant load trace、robot lease、fairness A/B 或 candidate ownership 证据，因此 verdict 保持 `WARN`。

## 2. 冻结来源、Revision、许可与 Claim Boundary

所有公开 raw 内容于 2026-07-20 以指定 commit 获取，SHA-256 按 UTF-8 原文计算。`checked` 只证明来源可取得且 hash 匹配，不证明本仓库运行了对应系统。

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Kubernetes [`kube-scheduler.md`](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/scheduling-eviction/kube-scheduler.md) | official-doc；`website@d19aace`；CC BY 4.0 | `A3289AD80B90623B2AA9C37AEEFB683699CCA0CBE09BA694CEB47D4F13A560C3` | scheduling stages、Filter/Score/Bind 与 placement factors | VLA action age、robot safety 或 fleet API 已实现 |
| S2 | Kubernetes [`pod-priority-preemption.md`](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/scheduling-eviction/pod-priority-preemption.md) | official-doc；同 revision/license | `9814E53FCC34460C5659B02C35F54959F3E87E669EE34C064225684D6930F812` | PriorityClass、higher-priority Pod 与 preemption 语义 | 抢占一个推理 Pod 就等于安全取消或物理停止 |
| S3 | Kubernetes [`resource-quotas.md`](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/policy/resource-quotas.md) | official-doc；同 revision/license | `FF097EAEBC0B5155CC48C627563F297CA624348115D0612A32942E5502203069` | namespace aggregate quota 与 object/resource limits | quota 自动提供 weighted fairness 或 robot isolation |
| S4 | Kubernetes [`leases.md`](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/architecture/leases.md) | official-doc；同 revision/license | `A23F1A9920505C3916071C7CBE5325F504C0381A97D527D4DEC4EC962C3F2F46` | Lease lock、heartbeat 与 single-instance coordination | Lease 自动完成 robot command fencing 或 controller ack |
| S5 | NVIDIA [`k8s-device-plugin/README.md`](https://github.com/NVIDIA/k8s-device-plugin/blob/248164727d5d8bac7024a8e12a13e69246cf0969/README.md) | official-code/doc；`2481647`；Apache-2.0 | `275441486E964DFC59D23AE766CC93B9A1CD2F06033AE1E92590CF436823374A` | GPU discovery/health、MIG 与 CUDA time-slicing configuration | GPU share 必然公平、显存隔离或适合实时 control |
| S6 | Volcano [`fairshare.md`](https://github.com/volcano-sh/volcano/blob/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0/docs/design/fairshare.md) | official-design；`329f91d`；Apache-2.0 | `906024CE070563037AE417659B20D156CF93E9E5A0907097C13ED3A9D1A5F031` | queue/namespace、weight、quota 与 fair-share direction | 已为 VLA tenant 实测公平或满足 deadline |
| S7 | Volcano [`capacity-scheduling.md`](https://github.com/volcano-sh/volcano/blob/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0/docs/design/capacity-scheduling.md) | official-design；同 revision/license | `FD19288F51142F84AC46411206B2966C6531BF8FB929AC067794303B165A0AAE` | guarantee、capability、deserved、reclaim 与异构资源 capacity | capacity policy 自动解决 model cold-start、action freshness 或 robot lease |
| S8 | Volcano [`queue-priority.md`](https://github.com/volcano-sh/volcano/blob/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0/docs/design/queue-priority.md) | official-design；同 revision/license | `500437A3CA409C51343290A257119065D75EDFC753689D65FD67539E8D6CB1E8` | queue priority ordering 与 reclaim interaction | priority 顺序等于 product/user fairness 或安全 criticality |
| S9 | Triton [`model_configuration.md`](https://github.com/triton-inference-server/server/blob/d1e6320698eda052ea2c3deaba4069958171caa5/docs/user_guide/model_configuration.md) | official-doc；`server@d1e6320`；BSD-3-Clause | `01E50042A66024AD5C9143E7AA3F43B0338F29F8EF6CC42979909589774B8151` | `max_batch_size`、batch dimension 与 dynamic/sequence batching shape contract | VLA camera/prompt/normalizer 请求天然可 batch |
| S10 | Triton [`rate_limiter.md`](https://github.com/triton-inference-server/server/blob/d1e6320698eda052ea2c3deaba4069958171caa5/docs/user_guide/rate_limiter.md) | official-doc；同 revision/license | `3857CBEEC5227EE0B50EA9F47A88568843ABCDE2D95E592045A6EFA07512627A` | named resource/count allocation 与 model instance concurrency | rate limiter 自动提供 multi-tenant fairness 或 E2E deadline |
| S11 | Ray [`resources.rst`](https://github.com/ray-project/ray/blob/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3/doc/source/ray-core/scheduling/resources.rst) | official-doc；`ray@6623e6b`；Apache-2.0 | `C48B0DD8887F4A1ED3CF39B3540A01C9E73D99355E5A542E947FAE1CB48CAD5A` | logical/physical resources、GPU、memory 与 custom resources | logical resource reservation 等于真实 GPU isolation |
| S12 | Ray [`placement-group.rst`](https://github.com/ray-project/ray/blob/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3/doc/source/ray-core/scheduling/placement-group.rst) | official-doc；同 revision/license | `1CF393A22A200F2005FEDB764A0095F84A78766F4883A2E63020D14BFEFCE267` | atomic bundles、gang scheduling、PACK/SPREAD 与 fault-tolerance rationale | placement group 自动处理 robot rollout protocol 或 controller recovery |
| S13 | Ray Serve [`architecture.md`](https://github.com/ray-project/ray/blob/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3/doc/source/serve/architecture.md) | official-doc；同 revision/license | `47E9A424F1B0AC4BCA8BDBEED323A8819C031725BE978D7E66E942BB8D449710` | controller/proxy/replica、request queue、per-replica processing/batching | VLA action schema、robot lease 或 physical safety |
| S14 | Ray Serve [`resource-allocation.md`](https://github.com/ray-project/ray/blob/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3/doc/source/serve/resource-allocation.md) | official-doc；同 revision/license | `17DCFF6FE21FFB6FF5150BAC2E9B29B716E77B8E142DF796B0B301E205F3B155` | replica count、`ray_actor_options`、GPU reservation | reservation 证明了模型已在用户项目 fleet 上运行 |
| S15 | ROS 2 [`node_lifecycle.md`](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md) | official-design；`93a415b`；Apache-2.0 | `EAD3A5A4BD2AA8BE3BD029A84AB3AFA8BBA3C8A49B2DCA5C72015BF3640D93C1` | managed node lifecycle、resource acquisition/release、supervisory state | lifecycle state 自动成为 robot fleet lease/fencing |

本地项目入口按 2026-07-20 当前文件字节冻结：OpenPiVLA、Robot Harness、OPD、WAM、UWM/LIBERO 各自的 claim inventory 与 ownership ledger 均已存在；它们支持“项目 hook 与缺口”盘点，不支持统一 fleet ownership。对应入口：[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。

### 2.1 Local evidence SHA ledger

| 项目 | claim inventory SHA-256 | ownership ledger SHA-256 | 直接支持 | 明确不支持 |
| --- | --- | --- | --- | --- |
| OpenPiVLA | `13023578d1b7343083beb588c7f8ce7b1bdc267e2bc834204d309106e8ea132a` | `564cf577b1dd41d98fcd8ae568a3bf68ef9a47af4ca37cacf150cd37866a4851` | local policy/eval/parser/normalizer hooks 与 role gap | fleet scheduler、GPU fairness、lease fencing |
| Robot Harness | `71c3b62f52204574c1b854b554258dabc1856f5d9044eb9628280a32500a797f` | `66e6a93dc1c512e0f5603355cbe910d6d7db3ad0ca64ad41b0c494339bba7bd7` | tool scope/lock/timeout/compensation、训练/eval route | VLA inference scheduler、GPU placement、fleet SLO |
| OPD | `c002b2275eb1f747e1e6f383cb271539f081ae8ccee0c8d11afc92ebabe99afa` | `43280ccda28125f284679d5612fac2ae1621cc9a97285970f35cf4ebe703b7ad` | multi-expert route、teacher schedule、ZeRO/config、holdout | multi-tenant serving、robot fleet rollout |
| WAM | `2362311b8d90a5b82d9d2d6333f5d376625cf2311dd7a3921f42b339bb55afb4` | `62d85f35d6c30c5c7fed652fea34c70f492b75a5bc83d4a5d5993b17d11ec4a4` | simulator/chunk/controller diagnostic hook | heterogeneous GPU scheduler、fleet canary |
| UWM/LIBERO | `c35c41d6248e3b072e9181f4ad3aafa423631d74604207cb5ab65352105dd8a9` | `528e6f4af7e43f0891b8298e3005b459684632b4820b7481903f1eba79c84ec2` | launcher、task mapping、fixed protocol、loader diagnosis | production fleet、lease/watchdog、cross-robot serving |

这些 hash 是本地 evidence 文件内容的身份，不是远端 checkpoint、runtime binary、GPU load test 或 candidate ownership 的证明。

## 3. Claim Registry：可写、需标 inference、必须拒绝

| Claim | 类型 | 证据 | Verdict / 边界 |
| --- | --- | --- | --- |
| scheduler 可按 Filter/Score/Bind 等阶段决定 Pod placement | official-doc direct | S1 | `checked`；不含 VLA semantics |
| namespace quota、PriorityClass/preemption 与 queue weight/capacity 可表达租户资源边界 | official-doc/design direct | S2/S3/S6/S7/S8 | `checked`；公平性仍需 workload 定义和测量 |
| GPU device plugin 可暴露健康、MIG、time-slicing 入口 | official-code/doc direct | S5 | `checked`；不证明 isolation/fairness |
| model instance 可用 rate-limiter resource/count 做并发占用 | official-doc direct | S10 | `checked`；不等于 tenant SLO |
| placement group / logical resource 可表达 multi-node/gang/accelerator placement | official-doc direct | S11/S12/S14 | `checked`；需单独做 VLA schema 和 controller contract |
| robot lease 应绑定 `robot_id + lease_epoch + model_revision`，并在失联时 fencing | cross-source system design | S4/S15 + SYS-002 | `inference / design requirement`；当前没有统一 robot lease 实现 |
| scheduler objective 应同时约束 capacity、fair share、queue wait、action age、deadline miss、cost | system design inference | S1–S14 + SYS-002 | `inference`；需 workload trace/A-B 才可调权重 |
| Kubernetes/Volcano/Ray/Triton 已构成用户个人 production fleet | unsupported personal claim | local evidence gate | `rejected`；五项目 inventories/ledgers 没有统一 fleet runtime/load/fairness artifact |
| GPU time-slicing 或 preemption 后旧 action 一定不会到 controller | unsupported safety claim | S2/S5 + SYS-002 | `rejected`；必须有 stale-response fencing、controller ack 与 independent stop |

## 4. Fleet Identity 与 State Ownership

### 4.1 最小 request / lease identity（设计推断）

| 类别 | 最小字段 | 作用 |
| --- | --- | --- |
| tenant | `tenant_id`, `quota_class`, `priority`, `budget` | 配额、优先级、公平性和成本归属 |
| robot | `robot_id`, `robot_type`, `capability_set`, `lease_epoch`, `controller_endpoint` | 能力匹配、fencing、controller 路由 |
| policy | `model_revision`, `processor_revision`, `normalizer_revision`, `action_schema_version` | warm cache、compatibility 与结果审计 |
| request | `request_id`, `session_id`, `capture_ts`, `deadline_abs`, `H`, `D`, `valid_until` | queue、batch、action-age、幂等与 stale-response |
| placement | `gpu_type`, `mig_profile`, `memory_budget`, `network_zone`, `replica_id` | Filter/Score、locality、异构设备与成本账本 |

同一个 `robot_id` 不应仅凭网络连接获得永久控制权；lease epoch、model/schema revision 和 controller acknowledgement 必须共同进入执行边界。上述是设计合同，不是当前 OpenPI 或五项目已有字段。

### 4.2 Scheduler state ownership

| 状态 | owner | 失效/恢复动作 | 当前来源边界 |
| --- | --- | --- | --- |
| tenant quota / queue | scheduler control plane | reject、requeue、reclaim 或 downgrade | K8s/Volcano 机制；无 VLA local implementation |
| model replica / GPU reservation | orchestrator + inference runtime | warm/cold、drain、reschedule、load smoke | Ray/Triton/K8s mechanisms；不证明 checkpoint lineage |
| robot lease | fleet control plane + controller | renew、epoch bump、fence、hold/stop | Lease/lifecycle 启发的 design contract |
| action chunk | policy client/broker | expiry、stale drop、replan、fallback | SYS-002 OpenPI evidence；无 fleet-wide stale-response proof |
| rollout/canary | release controller | model revision promotion/rollback、per-tenant gate | design inference；项目只有局部 eval/rollout hooks |

## 5. Capacity、Placement 与 Fairness Contract

### 5.1 Resource vector

将一个请求抽象为资源向量 (R=(g,m,c,n,s))，分别表示 GPU/accelerator、显存、CPU、网络和模型/缓存空间；节点剩余容量为 (C)。基本 admission 条件是：

\[
R_{\mathrm{req}}\preceq C_{\mathrm{node}},
\qquad
\mathrm{compatible}(\text{model},\text{schema},\text{normalizer},\text{controller})=1.
\]

变量解释：逐维不超过容量只是必要条件，compatibility 才能阻止把不同 action shape 或 normalizer 混进同一 replica。Kubernetes/Ray/Triton 来源支持资源与 shape 机制；后半项是 VLA system-design inference，不是上游默认检查。

### 5.2 Queue / fairness / priority

Volcano fair-share、capacity 和 priority 文档提供不同层面的 queue ordering、weight、guarantee/capability/deserved 与 reclaim 语义。面试时要区分：

- **capacity**：限制一个 tenant/queue 能占多少 GPU、MIG 或其他资源；
- **fairness**：长期资源占用或 queue share 的平衡；
- **priority**：关键任务的先后顺序；
- **freshness**：robot action 是否仍在 deadline 内。

四者不等价。让高优先级 offline training 抢占 serving GPU，可能改善训练等待，却恶化 action age；让所有 tenant 严格 equal share，也可能不符合机器人安全或 SLA。需要在同一 workload matrix 中报告 queue wait、GPU utilization、p95/p99 capture→apply、deadline miss、tenant share、preemption/retry 和 cost。

### 5.3 Heterogeneous GPU 与 model cache

NVIDIA device plugin 的 MIG/time-slicing 入口、Ray 的 custom/logical resources、Triton 的 model instance/rate limiter 可以组成 placement options：例如将某 model revision 绑定到 A100/MIG profile，并用 named resource 限制同一 GPU 上的 instance concurrency。但“可声明资源”不自动意味着显存/带宽隔离，也不保证 warm cache 命中；cache key 至少要绑定 model/processor/normalizer/action schema revision，冷启动必须进入 tail-latency 与 cost ledger。

## 6. 正常数据流、Rollout 与 Canary 边界

```text
# Design path; these steps are not claimed as an existing user fleet.
request(identity + observation + deadline)
  → tenant quota / queue admission
  → compatible shape + model revision grouping
  → Filter / Score / reserve GPU or placement group
  → warm model replica / named rate-limiter resources
  → infer + parse + denormalize + safety boundary
  → robot lease/epoch + controller acknowledgement
  → per-tenant metrics, canary gate, replay and rollback record
```

Ray Serve 的 controller/proxy/replica 和 request queue 可作为一种 serving topology；Ray placement group 的 atomic bundles 可作为 multi-node training/gang placement；Triton rate limiter 可作为 model-instance concurrency gate；Kubernetes/Volcano 可作为 cluster-level queue/placement。把它们拼成 VLA fleet 是架构综合，不能写成其中任一项目已部署。

## 7. 五项目证据与真实性边界

| 项目 | 可安全连接的 hook | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | offline WebSocket eval、in-process broker、model/action shape 与 normalizer/parser 风险 | multi-robot fleet、GPU scheduler、tenant fairness、lease fencing、production canary |
| Robot Harness | tool scope、timeout/cancel、robot lock、best-effort compensation 与训练/eval data routes | VLA inference scheduler、GPU placement、fleet SLO 或 controller lease |
| OPD | multi-expert route、teacher scheduling、ZeRO/config 与 holdout scorer | multi-tenant serving、GPU fairness、robot fleet rollout |
| WAM | simulator launcher、chunk/controller schema、diagnostic trace | fleet service、heterogeneous GPU scheduler、real-hardware canary |
| UWM/LIBERO | training/rollout launcher、task mapping、fixed protocol、DataLoader diagnosis | production fleet、lease/watchdog、cross-robot serving |

五个 inventory/ownership ledger 的共同结论是：有项目局部代码、配置、报告或诊断 artifact，但缺统一 scheduler control plane、fleet request trace、multi-tenant load/fairness A/B、lease epoch/controller ack、模型 cache lineage 和候选人逐项 ownership。因此只能说“我能设计并审计这些边界”，不能说“我已经建设并上线多机器人 GPU fleet”。

## 8. Deterministic Source Probes

本轮从固定 raw URL 重新获取并执行 15 项字符串/顺序 probe；probe 只验证引用锚点，不验证 runtime 性能或 fairness。

| Probe | 结果 | 检查内容 |
| --- | --- | --- |
| P01 | PASS | Kubernetes scheduler 含 QueueSort、Filter、Score、Bind stages |
| P02 | PASS | Priority/Preemption 文档包含 higher-priority Pod 抢占 lower-priority Pod 语义 |
| P03 | PASS | ResourceQuota 包含 namespace aggregate resource/object limits |
| P04 | PASS | Lease 文档包含 lock shared resources、heartbeat 与 Lease API |
| P05 | PASS | NVIDIA device plugin README 包含 GPU health、MIG 与 CUDA time-slicing |
| P06 | PASS | Volcano fair-share 包含 namespace、weight、quota |
| P07 | PASS | Volcano capacity 包含 Guarantee、Capability、Deserved |
| P08 | PASS | Volcano queue priority 包含 priority ordering 与 reclaim |
| P09 | PASS | Triton model configuration 包含 max_batch_size 与 dynamic batcher |
| P10 | PASS | Triton rate limiter 包含 resource allocation/release |
| P11 | PASS | Ray resources 包含 logical/custom resources |
| P12 | PASS | Ray placement group 包含 atomic reserve、gang scheduling、SPREAD |
| P13 | PASS | Ray Serve architecture 包含 Controller、Replicas 与 request queue |
| P14 | PASS | Ray Serve resource allocation 包含 num_gpus 与 replica resources |
| P15 | PASS | ROS 2 lifecycle 包含 managed node、resource acquisition/release、lifecycle_state |

汇总：`15/15 PASS`。Negative probe 只说明指定文件未证明 VLA fleet semantics；不能推断整个仓库或未来版本永远没有相关能力。

## 9. Source Gate 结论与下一切片

本节点达到 `source_frozen`：15 个公开 source rows、固定 revision/SHA、Kubernetes/Volcano/Ray/Triton/NVIDIA/ROS 2 的 capacity/placement/fairness/lease/lifecycle 机制，以及五项目 inventory/ownership hooks 均已登记。它仍为 `WARN`，因为没有统一 fleet service、tenant/robot/model request trace、GPU placement/fairness load test、cache lineage、lease fencing、controller ack、canary/rollback artifact 或候选人逐项 ownership confirmation。

下一 bounded slice：保持已同步的 `SYS-VLA-003` 题卡为 `unseen`，进行一次真实口述或收集 tenant/robot/model/request/placement trace；`CODE-VLA-007` 另有独立 source→knowledge 队列，不启动 `SYS-VLA-004`。

## 参考文献（References）

1. Kubernetes official docs：scheduler、Pod Priority/Preemption、ResourceQuota、Lease，均固定在 `kubernetes/website@d19aacebe8061a6ef5dcc1e68904aaefe35c5445`。
2. NVIDIA，[Kubernetes device plugin `248164727d5d8bac7024a8e12a13e69246cf0969`](https://github.com/NVIDIA/k8s-device-plugin/tree/248164727d5d8bac7024a8e12a13e69246cf0969)。
3. Volcano，[fair-share/capacity/queue-priority `329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0`](https://github.com/volcano-sh/volcano/tree/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0)。
4. NVIDIA Triton，[model configuration/rate limiter `d1e6320698eda052ea2c3deaba4069958171caa5`](https://github.com/triton-inference-server/server/tree/d1e6320698eda052ea2c3deaba4069958171caa5)。
5. Ray，[resources/placement groups/Serve `6623e6b1e71fcdb7161d6ec0b190e345665d5ba3`](https://github.com/ray-project/ray/tree/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3)。
6. ROS 2，[managed node lifecycle `93a415bf928751d37fce6f83215c521658e20c93`](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md)。
7. 本仓库 [ENG-016](vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)、[ENG-018](vol_05_eng018_scheduler_preemption_retry_source_freeze.html)、[ENG-019](vol_05_eng019_config_resolution_run_identity_source_freeze.html)、[ENG-022](vol_05_eng022_policy_server_resilience_source_freeze.html) 与五项目 [claim inventories](../evidence/projects/openpivla_claim_evidence_inventory.html)。
