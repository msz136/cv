# VOL 08 SYS-002 原子题卡：Policy Serving 与 Real-time Control Loop

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`SYS-VLA-002`  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[SYS-002 Knowledge](../knowledge/vol_08_sys002_policy_serving_realtime_control_loop.html)；来源边界见 [SYS-002 Source Freeze](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html)。

## 如何设计 VLA Policy Serving 与实时控制环？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>SYS-VLA-002</b> · 如何把 VLA policy 接入实时控制环，并区分 WebSocket demo、soft-real-time service 与物理安全边界？</summary>

**面试意图**：判断你能否把 API/schema、状态所有权、chunk/replan、端到端 latency、deadline/backpressure、fallback 和 controller/e-stop 串成一条可验证的系统设计，而不是只说“加一个 policy server”。

**30 秒回答**：拆三层：server 返回动作，client 管 chunk，controller 管 ack/stop。冻结 deadline、H/D、frame、expiry；batch 需兼容，denorm/限幅后交 controller。看 capture→apply、age、miss、fallback；infer_ms/timeout 不等于 E2E/stop。

**机制展开（约 2 分钟）**：server 管模型，client 管连接和 chunk，controller 管执行与停止。request 记录 id、capture_ts、revision、deadline、H/D、frame、normalizer、expiry，并传播 deadline。队列满则 reject、复用新鲜 chunk 或 fallback；batch 前校验 shape/normalizer。推理后 parse、denorm、限幅、stale 检查，再交 controller。用 capture→apply、action age、deadline miss、fallback 验证 soft real-time；cancel、旧回包、stop、e-stop 分开。

**诊断 / 证据**：先用 request_id 串起 capture、enqueue、infer、receive、postprocess、apply 时间戳，定位 queue/network/GPU/controller 的 first divergence；再做 queue-full、deadline-too-small、stale-response、parse/denorm、controller-ack 缺失和 reconnect fault injection。检查 H/K、action axis/frame/unit、normalizer revision、control frequency 与 success predicate 是否一致。没有 load/fault trace、E2E timestamp、controller ack 或 watchdog/e-stop 证据时，只能说设计了验证门，不能报 p99 SLO、hard real-time 或“timeout 后机器人必停”。

**项目挂钩**：OpenPiVLA 可安全连接 offline WebSocket eval、connect/infer alarm、in-process `ActionChunkBroker` rollout 和 parser/normalizer 风险；Robot Harness 可连接 timeout/cancel/compensation；OPD 可连接 data/eval route；WAM、UWM/LIBERO 可连接 simulator/chunk/controller protocol。五者都只能作为局部接口或证据 hook，不能升级为我已上线 production policy service、multi-robot fleet、hard real-time watchdog 或完整物理安全系统。

**追问树**：为什么 `infer_ms` 不是 E2E latency？H 与 K 如何共同影响 action age？什么请求可以 dynamic batch，什么请求必须拒绝？deadline 与逐层 timeout 有何区别？queue 满时丢 observation 和丢 action 的语义为何不同？RPC cancellation 为什么不等于 e-stop？controller ack、hold/stop 和 watchdog 谁拥有最终状态？如何证明旧 chunk 不会在重连后执行？

**易错点**：把 WebSocket 叫作“天然实时”；把 example 的 H/K 当通用标准；把 `asyncio.Queue`、Triton batcher 或 ROS QoS 文档写成 OpenPI 已实现；只报平均 infer time；把 timeout/exception 当成物理停止；把上游代码路径当个人 ownership；把 offline action metric 当 closed-loop success。

**危险答案**：说“OpenPI 已经有 production queue、dynamic batching、deadline propagation、fairness 和 watchdog”；说“server 返回 200 就代表机器人执行成功”；说“取消 RPC 会撤回 GPU 和已发控制命令”；或说“OpenPiVLA 的 WebSocket/ALOHA 脚本证明我完成了端到端生产部署”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [SYS-002 Knowledge](../knowledge/vol_08_sys002_policy_serving_realtime_control_loop.html)：schema、状态所有权、timing、backpressure、实时边界与五项目 hook。
2. [SYS-002 Source Freeze](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html)：OpenPI frozen revision、CPython/Triton/gRPC/ROS 2 机制与 14/14 probes。
3. Physical Intelligence [OpenPI `openpi@15a9616a`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：server/client、broker、LIBERO/DROID examples。
4. CPython [`asyncio` queue/tasks](https://github.com/python/cpython/tree/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library)、NVIDIA Triton [batcher/model configuration](https://github.com/triton-inference-server/server/tree/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide)。
5. gRPC [Deadlines](https://github.com/grpc/grpc.io/blob/78db5a6f78ee0d3426cf53cee07739196d962ea2/content/en/docs/guides/deadlines.md) 与 ROS 2 [QoS / pendulum real-time](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/qos.md)。
