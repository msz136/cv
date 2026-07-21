# VOL 08 SYS-004 原子题卡：Fault Recovery、Safety 与 Observability

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-21  
> 覆盖范围：`SYS-VLA-004`  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[SYS-004 Knowledge](../knowledge/vol_08_sys004_fault_recovery_safety_observability.html)；来源边界见 [SYS-004 Source Freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html)。

## 如何设计 VLA 系统的故障恢复、安全边界与可观测性？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>SYS-VLA-004</b> · policy、controller、robot 或数据链路异常时，如何定位 first divergence、降级恢复并防止 stale action 造成物理风险？</summary>

**面试意图**：判断你能否把状态机、证据链、safe-apply、lease fencing、rollback/replay 和独立 e-stop 边界连成闭环，而不是把“加日志、重试、stop”当作完整安全设计。

**30 秒回答**：用 trace/metric/log 找 first divergence，按 DEGRADED→HOLD/STOPPED 分级。action 校验 schema、时间、lease epoch、deadline；失败即丢弃并 hold/stop。恢复隔离后回滚兼容 bundle，用 replay/canary 验证；e-stop 属于独立安全链。

**机制展开（约 2 分钟）**：让 observation→infer→apply→ack 共用 robot/session identity，关联 trace、metric、log。按 symptom→first divergence→root cause→outcome 诊断；liveness/readiness/startup 与 QoS 分开。`safe_apply` 检查 schema、normalizer/controller compatibility、freshness、deadline、lease epoch；失败则 quiesce、清旧 chunk，进入 hold/stop。rollback 用兼容矩阵和 bundle；replay 固定输入与版本，再做 canary。硬件 e-stop 独立断能。

**诊断 / 证据**：先找第一条可验证的时间戳分叉：capture→queue→infer→validate→apply→ack；记录 `A_age=t_apply-t_capture`、deadline miss、QoS drop、queue、lease epoch、controller ack 和状态迁移。做 stale response、model/schema mismatch、normalizer drift、timeout、partial sensor、controller restart、rollback 与 replay fault injection。没有本地 supervisor、controller acknowledgement、fault-injection matrix、immutable replay bundle 或 rollback compatibility artifact 时，只能讲设计合同，不能声称完成生产安全闭环。

**项目挂钩**：OpenPiVLA 可连接 WebSocket connect/infer timeout、parser/normalizer/action-shape 风险；Robot Harness 可连接 tool timeout、lock、cancel/compensation；OPD 可连接多教师/配置 lineage；WAM 可连接 simulator/chunk/controller diagnostics；UWM/LIBERO 可连接 loader、launcher、protocol 与 fixed-init 结果。五个项目都没有被证据证明拥有统一 fault supervisor、controller e-stop acknowledgement 或 production incident replay，不能把局部脚本写成个人安全平台 ownership。

**追问树**：liveness/readiness/startup 为什么不能互换？first divergence 如何区别 symptom 和 root cause？cancel、hold、stop、e-stop 的 owner 分别是谁？为什么 lease epoch 能挡 stale action？action age 与 inference latency 有什么区别？rollback 只换 checkpoint 够不够？如何保证 replay 不被 wall-clock、随机数或在线状态污染？QoS reliable 是否等于动作必达？controller 没 ack 时策略服务该做什么？

**易错点**：把重试当恢复；把服务进程存活当 readiness；只记录 error log 不记录 identity/timestamp；把 cancel 说成物理 stop；没有 fencing 仍执行旧 action；把上游 ROS/Kubernetes/OpenTelemetry 机制当个人 production evidence；把 simulator replay 当真实机器人安全结果。

**危险答案**：说“超时就重试直到成功”；说“服务返回 200 就代表机器人执行成功”；说“kill policy pod 就是 e-stop”；说“有 trace 就能证明 RCA”；或说“五个项目已经完成 fault supervisor、rollback 和物理安全闭环”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [SYS-004 Knowledge](../knowledge/vol_08_sys004_fault_recovery_safety_observability.html)：fault state、first-divergence、safe-apply、lease fencing、rollback/replay 与项目边界。
2. [SYS-004 Source Freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html)：ROS 2、Kubernetes、OpenTelemetry、12 个 deterministic probes 与五项目证据边界。
3. ROS 2 [managed node lifecycle](https://design.ros2.org/articles/node_lifecycle.html) 与 `ros2_control` [controller manager](https://control.ros.org/master/doc/ros2_control/controller_manager/doc/userdoc.html)。
4. Kubernetes [probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) 与 [rollout/rollback](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)。
5. OpenTelemetry [signals and context](https://opentelemetry.io/docs/concepts/signals/)；物理 e-stop 仍属于独立安全控制链，不由软件 tracing 或 policy response 取代。
