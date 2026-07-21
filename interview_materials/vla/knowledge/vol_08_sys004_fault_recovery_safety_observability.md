# VOL 08 SYS-004：Fault Recovery、Safety 与 Observability

> 状态：`drafted / SYS-VLA-004 / knowledge_12_of_phase / card_pending / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[SYS-004 Source Freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html)。

## 问题（Question）

VLA policy、数据管线、机器人 controller 或 telemetry 出现 timeout、schema mismatch、stale action、节点失活或 rollout regression 时，如何先保护 side effect，再找出 first verified divergence，最后完成可验证的 degradation、rollback 与 replay？本页把 source freeze 转译成面试可讲的状态、事件、恢复和项目边界；它不是个人项目已经上线安全系统的证明。

## 1. 直觉与专业定义

### 1.1 先保护副作用，再解释原因

直觉上，故障处理不是“看到 error 就 restart”。机器人动作可能已经进入 controller，任何 retry、rollback 或 latest-wins 都可能产生新的 side effect。因此顺序应是：

```text
发现异常 → 关闭新请求/丢弃 stale action → 记录事件
  → 找 first verified divergence → 选择 hold/fallback/rollback/replay
  → 用同一 identity 的证据验证恢复 → 才能释放降级状态
```

专业上，fault supervisor 需要把 serving、controller、lease、release 和 evidence 状态分离。ROS 2 lifecycle/`ros2_control` 提供状态与资源管理机制；Kubernetes probes/rollback 提供编排层信号；QoS 与 OpenTelemetry 提供通信和观测信号。把它们组合成 VLA 安全闭环是系统设计推断。

### 1.2 First verified divergence 不等于 root cause

- **symptom**：例如 deadline miss、action-age 超限、readiness 失败或 success 降低；它是现象。
- **first verified divergence**：最早能由日志、trace、schema diff、replay 或 ack 复现的协议偏离，例如 `capture_ts` 到 `infer_ts` 已超预算，或 action 的 `schema_revision` 与 controller 不一致。
- **root cause**：导致偏离的因果解释，例如 queue starvation、normalizer mismatch 或硬件错误；必须有干预/替换/重跑证据。
- **recovery outcome**：降级动作是否真的消除了故障，并且没有引入新的 side effect；不能由“进程重启成功”替代。

回答时把四层分开，避免把一个 warning 讲成 root cause 或 recovery success。

## 2. Fault state machine 与 owner

### 2.1 状态定义

| 状态 | 进入条件 | 主要 owner | 允许动作 | 退出证据 |
| --- | --- | --- | --- | --- |
| `HEALTHY` | schema、deadline、lease、controller ack 和 telemetry 正常 | serving + controller | 正常 infer/apply | 同一 identity 的连续健康窗口 |
| `DEGRADED` | deadline/QoS/metric 异常但 side effect 仍受控 | fault supervisor | 限流、降低 horizon、切 verified fallback、拒绝新请求 | freshness 与 health gate 恢复 |
| `QUIESCING` | drain、rollback 或 lease epoch 变更 | release/fleet controller | 拒绝新请求、等待或取消 in-flight | in-flight 清零或逐项 ack |
| `HOLD` | stale action、controller fault 或未知状态 | controller/safety layer | 保持安全姿态、丢弃 action、等待恢复 | controller hold ack 与 release reason |
| `STOPPED` | 明确 stop/e-stop 或不可恢复故障 | independent safety/controller | 不再 apply action | 独立 reset/inspection 记录 |
| `RECOVERY` | 已执行 restart/fallback/rollback/replay | fault supervisor | 执行恢复并收集证据 | fault-injection/rerun/audit bundle |
| `QUARANTINED` | revision、schema、lease 或证据不兼容 | release/evidence controller | 禁止继续 rollout，保留 artifact | compatibility review 与人工批准 |

这些状态是面试设计合同，不是 ROS 或 Kubernetes 自动提供的完整 robot-safety 状态机。尤其 `readiness=1` 只说明服务可以接流量，不说明 controller 可以安全 apply。

### 2.2 状态转换的负面边界

1. `HEALTHY → DEGRADED` 可以由一个确定的 health gate 触发，但不能仅凭 GPU utilization。
2. `DEGRADED → RECOVERY` 需要记录触发原因和当前 in-flight side effect；不能跳过 hold/fence。
3. `RECOVERY → HEALTHY` 必须有同 revision、同 schema、同 protocol 的验证窗口。
4. 任何 unknown lease/schema/controller 状态都应 fail-closed 到 `HOLD`、`STOPPED` 或 `QUARANTINED`，而不是继续 latest-wins。

## 3. Liveness、Readiness、Startup 与通信信号

### 3.1 三类 probe 不可混用

| 信号 | 回答的问题 | 失败时可做 | 不能推出 |
| --- | --- | --- | --- |
| startup | 进程/模型是否还在启动 | 暂缓 liveness/readiness、延长启动窗口 | 模型已 warm、controller 可用 |
| liveness | 进程是否仍应被重启 | restart 或标记实例异常 | restart 等于 recovery success |
| readiness | 当前实例是否接收新流量 | 从 service/queue 摘除、drain | 已安全 apply action |
| QoS deadline | 传输/消费是否在 deadline 内 | 记录 miss、降级或丢弃 stale 数据 | miss 的 root cause |
| liveliness | publisher/subscriber 是否仍被认为活跃 | 触发 reconnect/hold 策略 | controller 已停止物理动作 |

Kubernetes probes 是 orchestration 机制，ROS 2 QoS 是通信语义；两者都要通过 `request_id`、时间戳和 revision 进入 incident event，才能和 VLA 的 capture→infer→parse→apply 链接起来。

### 3.2 Deadline 与 action age

对一条 action chunk，至少记录：

[
A_{mathrm{age}}=t_{mathrm{apply}}-t_{mathrm{capture}},qquad
mathrm{fresh}(a)=mathbf{1}!left[A_{mathrm{age}}leq D_{mathrm{valid}}ight].
]

`A_age` 是观测捕获到动作 apply 的年龄，`D_valid` 是动作协议允许的有效窗口。它映射到 capture/apply timestamp、chunk cursor 和 controller apply log；缺任一时间点时只能标记 unknown，不能把 timeout 直接解释为 MDP terminal 或任务失败。

## 4. Incident identity 与可观测性

### 4.1 最小事件 schema

```text
(event_id, incident_id, request_id, session_id,
 robot_id, lease_epoch, model_revision, schema_revision,
 capture_ts, infer_ts, parse_ts, apply_deadline, apply_ts,
 stage, severity, symptom, first_verified_divergence,
 action_seq, controller_ack, recovery_attempt, evidence_refs)
```

字段职责：

- `request_id/session_id` 连接一次服务调用及其重试；
- `robot_id/lease_epoch` 防止旧连接或旧动作越过 fencing；
- `model/schema_revision` 绑定 checkpoint、processor、normalizer、action parser 和 controller contract；
- `capture_ts/infer_ts/parse_ts/apply_ts` 支持阶段级 latency 与 first divergence；
- `controller_ack` 必须区分收到 cancel、进入 hold 和停止执行；
- `evidence_refs` 指向不可变 trace、log、metric snapshot、replay bundle 或人工批准。

### 4.2 Traces、metrics、logs 的分工

| 信号 | 适合回答 | 常见误区 |
| --- | --- | --- |
| trace | 一次 request 从 capture 到 apply 的跨服务路径 | trace 存在不代表每个 side effect 都被采样 |
| metric | p95/p99 latency、deadline miss、queue depth、fallback rate、lease conflict | 平均值掩盖 tail 或分母不一致 |
| log | schema diff、异常栈、controller ack、rollback reason、人工批准 | 有日志不等于 root cause 已确认 |
| baggage/identity | 把 tenant/robot/model/session 信息跨边界传递 | identity 未校验会污染 incident correlation |

OpenTelemetry 的 signals 规定载体和关联方式；将其组合为 robot-safety evidence 是设计工作，不是 telemetry SDK 自动完成的功能。

## 5. Safety boundary 与 stale-action fencing

### 5.1 Safe apply 条件

[
\mathrm{safe\_apply}(a_t)=1
\Longleftrightarrow
\mathrm{fresh}(a_t)land
\mathrm{compatible}(r,m,s,n)land
\mathrm{lease\_valid}\land
\mathrm{controller\_ready}.
]

其中 `r` 是 robot identity，`m` 是 model revision，`s` 是 action schema，`n` 是 normalizer revision。`fresh` 检查 action age/sequence，`compatible` 检查 shape、unit、parser 和 controller contract，`lease_valid` 检查 epoch/fencing，`controller_ready` 只代表 controller 明确允许接收。它是 SYS‑004 的系统设计推断，不是任一上游 API 的默认保证。

### 5.2 Cancel、hold、stop、e-stop

| 层 | 能安全声称 | 还需要什么才能升级 |
| --- | --- | --- |
| software cancel | 请求被取消或不再排队 | in-flight infer、parse、send 是否已被收敛 |
| controller hold | controller 返回 hold acknowledgement | hardware state、动作是否真正停止 |
| software stop | policy/client 不再发送 action | controller/actuator 是否仍有 buffered command |
| independent e-stop | 安全链路触发停止 | 复位、检查、incident record 与物理验证 |

“cancel acknowledged”不能写成“机器人已经停下”；“readiness=false”不能写成“任务安全失败”。若 controller ack 缺失，保持 `HOLD/STOPPED/UNKNOWN`，不释放 side effect gate。

## 6. Degradation、rollback 与 replay

### 6.1 Fail-closed 顺序

推荐顺序是：

1. 拒绝新请求并记录 incident identity；
2. 丢弃过期 action，提升 lease epoch，阻断旧 response；
3. 进入 `HOLD` 或 `STOPPED`，要求 controller acknowledgement；
4. 对无物理 side effect 的请求执行 fallback、restart 或 drain；
5. 对 revision regression 执行 quiesce→compatibility check→rollback；
6. 用固定输入、固定 revision、固定 protocol replay，并记录 recovery outcome；
7. 通过 health gate 和人工/策略批准后才回到 `HEALTHY`。

### 6.2 Rollback compatibility matrix

rollback 不能只记录 `from_revision → to_revision`，至少要比较：

| 项 | 必须一致或显式迁移 |
| --- | --- |
| model/processor | checkpoint、tokenizer/processor 版本与 load smoke |
| normalizer | mean/std、action unit、valid-dimension slice |
| schema | camera/text/proprio/action shape、parser、chunk horizon |
| controller | endpoint、ack/hold semantics、limit 与 lease epoch |
| protocol | task/seed/init/episode、scorer 与 denominator |
| rollout | cohort、canary window、in-flight drain 与 fallback |

Kubernetes Deployment 的 rollback 只描述 workload revision；上表是 VLA 兼容性设计推断。

### 6.3 Replay evidence

replay bundle 应是不可变的 observation/action/event/metric/trace manifest，并包含 SHA、revision、timestamps、protocol tuple 与原始输出位置。“重跑一次变绿”不能替代同输入、同版本、同协议的对照；没有 bundle 时只能写“恢复路径已设计”，不能写“恢复成功”。

## 7. 参考伪代码（带关键边界注释）

```python
def handle_result(req, result, clock, controller, ledger):
    # 1. Fence stale identity before any physical side effect.
    if result.model_revision != req.model_revision:
        return quarantine(req, result, "model_revision_mismatch")
    if result.lease_epoch != ledger.current_epoch(req.robot_id):
        return discard(req, result, "stale_lease_epoch")
    if clock.now() > result.valid_until:
        return hold(req.robot_id, controller, "stale_action")

    # 2. Require explicit controller acknowledgement; cancel is not e-stop.
    ack = controller.apply(result.action_chunk, req.action_schema)
    if ack.kind not in {"APPLIED", "HOLD", "STOPPED"}:
        return hold(req.robot_id, controller, "unknown_controller_ack")

    # 3. Write one correlated event before selecting recovery.
    ledger.append_event(req.identity, result, ack)
    if ack.kind in {"HOLD", "STOPPED"}:
        return enter_recovery(req, ack.kind)
    return mark_healthy_if_gate_passes(req)
```

这段伪代码只表达检查顺序；`controller.apply`、`current_epoch`、`append_event` 与 recovery supervisor 必须有真实实现、trace 和 ownership 才能成为 local-direct evidence。

## 8. First-divergence 诊断矩阵

| 观察到的症状 | 首个分叉检查 | 不应直接下的结论 |
| --- | --- | --- |
| readiness 失败 | probe dependency、model load、revision | “重启后已经恢复” |
| deadline/action-age 超限 | capture→infer→parse→apply 时间线 | “timeout 就是任务失败” |
| stale response | request/lease epoch/action sequence | “模型能力下降” |
| controller update/fallback error | controller ack、hardware state、buffer | “fallback 已停止物理动作” |
| telemetry gap | trace sampling、event identity、metric denominator | “没有日志就没有故障” |
| rollout regression | fixed holdout、canary cohort、protocol tuple | “rollback 自动修复 root cause” |
| replay mismatch | model/schema/normalizer/scorer hash | “同一个 checkpoint 就可比” |

诊断顺序固定为：`identity → stage timestamps → schema/normalizer → lease/action sequence → controller ack → health gate → recovery intervention → replay outcome`。不要跳到最后一层猜 root cause。

## 9. 五项目真实性边界

| 项目 | 可安全绑定的 hook | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | offline WebSocket timing、parser/normalizer/schema mismatch | production watchdog、controller e-stop、rollback closure |
| Robot Harness | timeout/cancel、robot lock、compensation、trace hook | VLA fault supervisor、physical stop、fleet incident response |
| OPD | teacher/route/holdout、scorer diagnostics | production observability、perception-action recovery |
| WAM | simulator/chunk/controller diagnostic trace | real-robot safety recovery、rollback canary、root-cause closure |
| UWM/LIBERO | launcher/task mapping、protocol mismatch、loader diagnosis | physical safety state、lease fencing、cross-robot recovery |

五个项目的 inventory/ownership ledger 只允许作为 bounded hook。Git author、上游 lifecycle、示例 YAML、路径、smoke report 或局部 timeout 字段都不能自动变成候选人 ownership。

## 10. 面试回答模板与高压追问

### 10.1 60 秒回答

“我会先把故障拆成 symptom、first verified divergence、root cause 和 recovery outcome。事件必须带 request、robot、lease epoch、model/schema/normalizer revision，以及 capture→infer→parse→apply 时间线。readiness、liveness、QoS deadline 和 telemetry 只代表不同层信号，不能直接写成安全成功。出现 stale action 或未知 controller 状态时先丢弃旧结果、提升 epoch、进入 HOLD/STOPPED 并要求 controller ack，再做 fallback、rollback 或固定协议 replay。Kubernetes/ROS/OpenTelemetry 是机制来源；我当前项目只有局部 timeout、eval、launcher 或 diagnostic hook，不能声称已经实现 production fault supervisor 或物理 e-stop。”

### 10.2 高压追问

- readiness=false 与 controller hold 有什么区别？
- cancel acknowledged 为什么不等于 e-stop？
- rollback 如何证明 normalizer、schema、controller 兼容？
- 如何定义 first verified divergence，而不是凭经验猜 root cause？
- stale action 如何用 lease epoch 和 sequence fencing？
- telemetry 缺失时为什么应进入 unknown/hold，而不是继续执行？
- replay bundle 最小字段是什么？如何避免“重跑一次变绿”？
- 你的五个项目中哪一个有真实 fault-injection 或 recovery artifact？没有时怎样回答？

## 11. 结论与下一步

SYS‑004 的高分答案不是背某个 probe 或 restart 命令，而是把 identity、first-divergence、side-effect safety、controller acknowledgement、degradation、rollback、replay 和证据闭环连接起来。当前 source gate 已冻结，knowledge 已完成教学转译；仍没有 fault supervisor、physical-stop acknowledgement、fault-injection matrix、immutable replay bundle 或个人 ownership 证据。

下一步：单独生成一张 `SYS-VLA-004` atomic card；在此之前不创建 `coaching_state.md`，不升级任何 mastery。

## 参考文献（References）

1. [SYS-004 Source Freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html)。
2. ROS 2 [managed node lifecycle](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md) 与 [QoS](https://docs.ros.org/en/rolling/ROS-Framework/interfaces/topics/About-Quality-of-Service-Settings.html)。
3. `ros2_control` [controller manager](https://github.com/ros-controls/ros2_control/blob/e4ebcc352d9aeb69969308428b051bdd3105b88f/controller_manager/doc/userdoc.rst)。
4. Kubernetes [probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) 与 [Deployment rollback](https://github.com/kubernetes/website/blob/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts/workloads/controllers/deployment.md)。
5. OpenTelemetry [signals](https://opentelemetry.io/docs/concepts/signals/)。
6. 本仓库 [SYS‑002](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html) 与 [EVAL‑008](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)。

