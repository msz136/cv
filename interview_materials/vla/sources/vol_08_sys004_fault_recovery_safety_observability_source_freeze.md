# VOL 08 SYS-004 Source Freeze：Fault Recovery、Safety 与 Observability

> 状态：`source_frozen / SYS-VLA-004 / knowledge_pending / card_pending / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本页只冻结故障分层、first-divergence、健康探针、生命周期降级、取消/停止边界、rollback/replay 与可观测性合同；不把公开机制、上游 API 或五项目局部 hook 写成候选人已经实现了生产安全系统。
> 前置：[VOL 08 Coverage-Gap Audit](vol_08_coding_system_design_coverage_gap_audit.html)、[SYS-VLA-001 source](vol_08_sys001_vla_training_eval_platform_source_freeze.html)、[SYS-VLA-002 source](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html)、[VOL 05 EVAL-008](vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)。

## 问题（Question）

当 VLA policy 服务、数据管线、机器人 controller 或观测系统出现超时、schema mismatch、stale action、节点失活或指标异常时，如何先保护副作用，再定位 first verified divergence，最后执行可验证的降级、回滚与 replay？面试回答必须区分 liveness、readiness、startup、controller hold/stop、独立 e-stop、软件恢复和候选人项目证据。

## 1. Source gate 结论先行

1. ROS 2 managed node lifecycle 把 configure、activate、deactivate、cleanup、shutdown 与 supervisory state 分开；`ros2_control` controller manager 进一步提供 controller load/switch/deactivate/fallback 的运行时边界。它们支持状态机与资源释放语义，不等于机器人已经安全停机。
2. Kubernetes liveness/readiness/startup probes 与 Deployment revision/rollback 说明“进程活着”“可以接新流量”“启动尚未完成”和“恢复到旧 revision”是不同合同；它们不证明 action 已被 controller 执行、取消已到达物理侧或旧 action 已被 fencing。
3. ROS 2 QoS 的 deadline、liveliness、reliability、durability 是通信层信号；OpenTelemetry 的 traces/metrics/logs 是观测载体。它们需要被同一个 `request_id + robot_id + lease_epoch + model/schema revision` 连接，才可以从症状追到首个可验证分叉。
4. SYS‑002 已冻结 serving request/response、deadline/backpressure、chunk/replan 与 real-time/fail-safe 边界；SYS‑004 在此之上补 recovery state、e-stop/hold ownership、rollback/replay、incident evidence 与 failure injection 合同。
5. 当前五项目只有局部 timeout、controller、launcher、eval 或诊断 hook；没有统一 fault controller、physical-stop acknowledgement、rollback bundle、replay ledger、fault-injection matrix 或候选人逐项 ownership。因此 source gate 保持 `WARN`。

## 2. 冻结来源、revision、许可与 claim boundary

公开内容按 2026-07-20 访问；固定 raw 内容的 SHA-256 按 UTF-8 原文计算，网页内容的 SHA-256 按本次获取的 UTF-8 response 计算。`checked` 只证明来源可取得并通过窄 probe，不证明本仓库运行过对应系统。

| ID | 来源 | 类型 / revision / license | SHA-256 | 直接支持 | 不能支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | ROS 2 Design [`node_lifecycle.md`](https://raw.githubusercontent.com/ros2/design/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md) | official-design；`ros2/design@93a415b`；Apache-2.0 | `ead3a5a4bd2aa8be3bd029a84ab3afa8bba3c8a49b2dca5c72015bf3640d93c1` | managed node states、transition、resource acquire/release 与 supervisory lifecycle | lifecycle transition 自动等于物理安全停止或个人 ownership |
| S2 | `ros2_control` [`controller_manager/userdoc.rst`](https://raw.githubusercontent.com/ros-controls/ros2_control/e4ebcc352d9aeb69969308428b051bdd3105b88f/controller_manager/doc/userdoc.rst) | official-code/doc；`ros2_control@e4ebcc3`；Apache-2.0 | `cf3af601c715499e37408420a355f092176707912e542feb549ccac0a1f038a1` | update rate、controller deactivate/switch、fallback 与 manager error boundary | fallback 已在用户机器人上启用、controller ack 或 e-stop closure |
| S3 | ROS 2 QoS [`About-Quality-of-Service-Settings`](https://docs.ros.org/en/rolling/ROS-Framework/interfaces/topics/About-Quality-of-Service-Settings.html) | official-doc；Rolling page，访问 2026-07-20 | `47881f1c31063504a81bd85826257a47aae9b1181091485d4fd4380422ccd1f0` | deadline、liveliness、reliability、durability 与 incompatible QoS 的通信语义 | QoS event 自动证明 action freshness、controller stop 或 safety certification |
| S4 | Kubernetes [`liveness-readiness-startup-probes`](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) | official-doc；网页 response，访问 2026-07-20 | `0e9815b35ce497f91fa09b34c968b64b76aada4c2a2ffc30f23c70da107e9a6e` | liveness/readiness/startup、failureThreshold、探针失败后的 orchestration 行为 | readiness 等于 robot safe-to-apply、restart 等于 recovery 成功 |
| S5 | Kubernetes [`deployment.md`](https://raw.githubusercontent.com/kubernetes/website/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/workloads/controllers/deployment.md) | official-doc；`kubernetes/website@d19aace`；CC BY 4.0 | `b4896e5d45a7d97b0d36ca5fe9e2cac2188ab46ce9cfbc61b4c143220e550c98` | Deployment revision、progress deadline、rollout 与 rollback 语义 | 旧 revision 与当前 normalizer/controller/action schema 一定兼容 |
| S6 | OpenTelemetry [`signals`](https://opentelemetry.io/docs/concepts/signals/) | official-doc；网页 response，访问 2026-07-20 | `87fbe2046c8818626b64fac11465902043fa7f417ea02fd1a4b461433341e0c8` | traces、metrics、logs、baggage 的 signal 分工与关联思路 | telemetry 完整等于根因已确认、采样覆盖所有 side effect |
| S7 | 本仓库 [SYS‑002 source freeze](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html) | local canonical；source SHA `45d78013c69c5727017cea56c1c563333d92b173406104bc963a3ba31da2e694` | `45d78013c69c5727017cea56c1c563333d92b173406104bc963a3ba31da2e694` | request/response、deadline/backpressure、chunk/replan 与 serving safety boundary | SYS‑004 的 fault controller、physical stop、rollback 或 candidate ownership |
| S8 | 本仓库 [EVAL‑008 recovery taxonomy](vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html) | local canonical；source SHA `580ac70922472453c8806265b2fd4bae8dad7881bad3da2e8f211c870e1f37b0` | `580ac70922472453c8806265b2fd4bae8dad7881bad3da2e8f211c870e1f37b0` | symptom→first divergence→intervention→verification 的 evidence ladder | 五项目已经确认 root cause、recovery success 或 ownership |

SRE monitoring 页面本轮因网络 TLS 不稳定未纳入 checked source；不以未取得的二手摘要替代上述官方资料。

## 3. Claim registry：可写、需标 inference、必须拒绝

| Claim | 类型 | 证据 | Verdict / 边界 |
| --- | --- | --- | --- |
| liveness、readiness、startup 是不同 probe 语义 | official-doc direct | S4 | `checked`；不含 robot safety |
| Deployment revision 可 rollout/rollback | official-doc direct | S5 | `checked`；需另做 schema/checkpoint compatibility |
| managed lifecycle 可表达 configure/activate/deactivate/cleanup | official-design direct | S1 | `checked`；不含物理 stop |
| controller manager 可暴露 deactivate/fallback/update error 边界 | official-code/doc direct | S2 | `checked`；不证明用户项目启用 |
| deadline/liveliness/reliability 是通信层故障信号 | official-doc direct | S3 | `checked`；不是根因结论 |
| traces/metrics/logs 可以用共同 identity 关联 incident | design composition | S3/S6/S7 | `inference / design requirement`；需 trace artifact 验证 |
| `request_id + robot_id + lease_epoch + model/schema revision` 是 stale-action fencing 的最小关联键 | system-design inference | S1/S2/S3/S7 | `inference`；当前无统一 local implementation |
| Kubernetes/Rollback/ROS lifecycle 已构成个人 production safety system | unsupported personal claim | local evidence gate | `rejected`；五项目 inventories/ledgers 不支持 |
| cancel/timeout acknowledgement 自动等于物理 e-stop | unsupported safety claim | S2/S4/S7 | `rejected`；必须有独立 controller/e-stop evidence |

## 4. Fault identity、状态所有权与事件合同

### 4.1 最小 incident/event schema（设计推断）

每个 fault event 至少保留：

```text
(event_id, incident_id, request_id, session_id,
 robot_id, lease_epoch, model_revision, schema_revision,
 capture_ts, apply_deadline, observed_ts, stage,
 severity, symptom, first_verified_divergence,
 action_seq, controller_ack, recovery_attempt, evidence_refs)
```

`first_verified_divergence` 是最早已被观测/复现的协议偏离，不是事后猜的 root cause。`controller_ack` 必须区分“收到 cancel”“进入 hold”“停止执行”；没有物理侧证据时只能写到 software boundary。

### 4.2 状态机与 owner

| 状态 | 进入条件 | owner | 允许动作 | 退出证据 |
| --- | --- | --- | --- | --- |
| `HEALTHY` | schema、deadline、controller ack 与 telemetry 正常 | serving + controller | 正常 infer/apply | 同一 identity 的连续健康窗口 |
| `DEGRADED` | deadline miss、QoS fault、指标异常但副作用仍受控 | fault supervisor | 降低 horizon、限流、切备用 revision、停止新请求 | 明确 health gate 与 freshness 恢复 |
| `QUIESCING` | 需要 drain、rollback 或 lease epoch 变更 | release/fleet controller | 拒绝新请求、等待/取消旧请求 | in-flight 清零或逐项 ack |
| `HOLD` | stale action、controller fault 或未知状态 | controller/safety layer | 保持安全姿态、丢弃 action、等待人工/策略恢复 | controller hold ack 与 release reason |
| `STOPPED` | 明确 stop/e-stop 或不可恢复故障 | independent safety/controller | 不再 apply action | 独立 reset/inspection 记录 |
| `RECOVERY` | 已执行一次恢复动作 | fault supervisor | replay、restart、fallback、rollback 或重新 acquire | fault injection / rerun / audit bundle |
| `QUARANTINED` | revision、schema、lease 或证据不兼容 | release/evidence controller | 禁止继续 rollout，保留 artifact | compatibility review 与人工批准 |

上述状态是 SYS‑004 的设计合同，不是 ROS/Kubernetes 自动提供的完整状态机。

### 4.3 Safety boundary

[
\mathrm{safe\_apply}(a_t)=1
\Longleftrightarrow
\mathrm{fresh}(a_t)\land\mathrm{compatible}(r,m,s)\land\mathrm{lease\_valid}\land\mathrm{controller\_ready}.
]

这里 `fresh` 由 capture/apply deadline 与 action sequence 判定，`compatible` 绑定 robot、model、schema、normalizer，`lease_valid` 由 epoch/fencing 判断，`controller_ready` 只代表 controller 明确允许接收。公式是系统设计推断，不是任一上游 API 的默认保证。

## 5. Failure、degradation、rollback 与 replay 合同

| 故障 | 首个检查 | 可逆动作 | 不可自动推断 |
| --- | --- | --- | --- |
| readiness 失败 | probe revision、dependency、model load | 拒绝新请求、drain、重启/回滚 | 已安全 apply 或恢复成功 |
| deadline / action-age 超限 | capture→infer→parse→apply 时间线 | 丢弃 stale action、hold、降低 horizon | timeout 等于 MDP terminal |
| schema/normalizer mismatch | revision 与 shape/normalizer hash | quarantine revision、回滚兼容包 | 旧 checkpoint 一定可用 |
| controller update/fallback error | controller manager error、ack、hardware state | deactivate、fallback、hold/stop | fallback 已停止物理副作用 |
| telemetry gap | trace/log/metric correlation 与采样窗口 | 标记 unknown、停止 rollout、补采样 | 没日志就没有故障 |
| rollout regression | fixed protocol、fresh holdout、canary delta | quiesce、rollback、replay | rollback 本身修复 root cause |

rollback 必须同时记录 `from_revision → to_revision`、schema/normalizer compatibility、in-flight drain、controller acknowledgement、health gate、fresh canary 与 rollback reason。replay 必须使用不可变的 observation/action/event bundle；“重跑一次变绿”不能替代同输入、同 revision、同 protocol 的对照。

## 6. 正常与恢复数据流（设计合同）

```text
# Design path; not a claim that the user's projects already implement it.
observe + identity + deadline
  → schema/lease compatibility gate
  → infer / parse / freshness check
  → controller-ready + action apply
  → trace + metric + log correlation
  → first-divergence detector
  → DEGRADED / QUIESCING / HOLD / STOPPED
  → fallback / rollback / replay
  → recovery verification + incident closure
```

伪代码中的关键边界是：先保护 side effect，再记录 event，再做 recovery；不能因为 telemetry 或服务进程恢复就直接释放 HOLD。

## 7. 五项目真实性边界

| 项目 | 可安全绑定 | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | offline WebSocket timing、parser/normalizer/schema mismatch 风险 | production watchdog、controller e-stop、rollback closure |
| Robot Harness | timeout/cancel、robot lock、compensation 与 trace hook | VLA fault supervisor、physical stop、fleet incident response |
| OPD | teacher/route/holdout 与 scorer diagnostics | production observability、perception-to-action recovery |
| WAM | simulator/chunk/controller diagnostic trace | real-robot safety recovery、rollback canary、root cause closure |
| UWM/LIBERO | launcher/task mapping、protocol mismatch、DataLoader diagnosis | physical safety state、lease fencing、cross-robot recovery |

五个项目的 inventory/ownership ledger 只允许作为 bounded hook。Git author、上游 lifecycle、示例 YAML、路径或 smoke report 都不能自动变成候选人 ownership。

## 8. Deterministic source probes

本轮对 8 个固定 source rows 执行 12 项窄 probe；probe 只验证来源锚点和负面边界，不验证 runtime 性能、安全或个人贡献。

| Probe | 结果 | 检查内容 |
| --- | --- | --- |
| P01 | PASS | S1 包含 Unconfigured、Inactive、Active、Finalized 与 lifecycle transition |
| P02 | PASS | S2 包含 controller manager、deactivate、fallback 与 update rate |
| P03 | PASS | S3 包含 deadline、liveliness、reliability、durability |
| P04 | PASS | S4 同时出现 liveness、readiness、startup 与 failureThreshold |
| P05 | PASS | S5 包含 revision、progressDeadlineSeconds、maxUnavailable 与 rollback |
| P06 | PASS | S6 同时出现 traces、metrics、logs 与 baggage |
| P07 | PASS | S7 保留 request/response、deadline/backpressure、chunk/replan 与 fail-safe 边界 |
| P08 | PASS | S8 保留 first-divergence、intervention、verification 与 recovery evidence ladder |
| P09 | PASS | 负面检查：S1–S6 不把 lifecycle/probe/telemetry 写成 physical e-stop 证明 |
| P10 | PASS | 负面检查：S5 rollback 不被写成 checkpoint/normalizer/controller compatibility 证明 |
| P11 | PASS | 负面检查：S3 QoS signal 不被写成 root-cause 或 action-success 结论 |
| P12 | PASS | 负面检查：五项目 inventory/ledger 不包含统一 fleet safety ownership 结论 |

汇总：`12/12 PASS`。负面 probe 只证明本页没有越界表述，不能证明未来实现一定安全。

## 9. Source gate 结论与下一切片

本节点达到 `source_frozen`：8 个 source rows、固定 revision/response SHA、12 个 deterministic probes、fault identity/state/recovery/safety/observability 合同及五项目真实性边界均已登记。它仍为 `WARN`，因为没有统一 fault supervisor、controller/e-stop acknowledgement、fault-injection matrix、immutable replay bundle、rollback compatibility gate 或候选人逐项 ownership。

下一 bounded slice：只把本 source contract 转译为 `SYS-VLA-004` knowledge；题卡继续后置，不在同一轮生成 atomic card，也不创建 `coaching_state.md`。

## 参考文献（References）

1. ROS 2 Design，[Managed nodes lifecycle](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md)。
2. ros2_control，[controller_manager userdoc](https://github.com/ros-controls/ros2_control/blob/e4ebcc352d9aeb69969308428b051bdd3105b88f/controller_manager/doc/userdoc.rst)。
3. ROS 2，[Quality of Service settings](https://docs.ros.org/en/rolling/ROS-Framework/interfaces/topics/About-Quality-of-Service-Settings.html)。
4. Kubernetes，[Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)。
5. Kubernetes，[Deployments and rollback](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/workloads/controllers/deployment.md)。
6. OpenTelemetry，[Signals](https://opentelemetry.io/docs/concepts/signals/)。
7. 本仓库 [SYS‑002 Source Freeze](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.md) 与 [EVAL‑008 Recovery Taxonomy](vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.md)。

