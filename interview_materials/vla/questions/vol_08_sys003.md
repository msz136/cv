# VOL 08 SYS-003 原子题卡：Robot Fleet 与 Multi-tenant GPU Scheduling

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`SYS-VLA-003`  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：`unseen`  
> 前置知识：[SYS-003 Knowledge](../knowledge/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling.html)；来源边界见 [SYS-003 Source Freeze](../sources/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling_source_freeze.html)。

## 如何设计 Robot Fleet 与 Multi-tenant GPU Scheduling？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>SYS-VLA-003</b> · 当机器人、租户、模型 revision 和异构 GPU 同时增长时，如何设计 fleet scheduler，并保证公平、freshness 与安全边界？</summary>

**面试意图**：判断你能否把 tenant/robot/model identity、quota、placement、fairness、preemption、replica/cache、robot lease、canary 和 cost/SLO 串起来，而不是只罗列 Kubernetes 或 GPU 名词。

**30 秒回答**：拆 queue、placement、lease、rollout。请求带 tenant/robot/model、deadline、epoch；查 quota/兼容性，按 GPU/MIG/显存选节点。capacity/fairness/priority/freshness 分开；lease 失效丢 action，controller stop。

**机制展开（约 2 分钟）**：校验 tenant/robot/model/schema、deadline、lease 后查 quota，按 GPU/MIG、显存、locality、warm replica placement。capacity/fairness/priority/freshness 分开；Triton/Ray 只提供资源机制。cache 绑定 model/processor/normalizer/schema；preemption 先处理无副作用任务。lease 失效提升 epoch、丢旧回包、controller stop。用 queue wait、tail、age、miss、share、fallback、cost 验证；局部项目 hook 不能称 fleet。

**诊断 / 证据**：先做 identity/schema/normalizer roundtrip，再记录 admission、queue wait、Filter/Score、GPU reservation、model load、infer、lease renew、controller ack 和 rollback 时间戳。做 tenant burst、GPU 异构、cold/warm cache、preemption、lease expiry、stale-response、replica crash 和 reconnect fault injection；固定 task/seed/cohort，按 tenant 报 queue wait、p95/p99 capture→apply、action age、deadline miss、share、fallback、cost 与 success。没有 multi-tenant load trace、placement/fairness A/B、lease fencing、controller ack 或 checkpoint/cache lineage 时，只能讲设计门，不能报 fleet SLO 或 production fairness。

**项目挂钩**：OpenPiVLA 可连接 offline WebSocket、in-process broker、normalizer/action-shape/parser 风险；Robot Harness 可连接 tool scope/lock/timeout/compensation；OPD 可连接 multi-expert route、teacher schedule、ZeRO/config；WAM 可连接 simulator/chunk/controller diagnostic；UWM/LIBERO 可连接 launcher、task mapping、fixed protocol 和 loader diagnosis。五个项目都没有统一 fleet control plane、GPU placement、robot lease 或 multi-tenant fairness artifact，不能把局部 hook 说成我上线了 production fleet。

**追问树**：capacity、fairness、priority、freshness 有什么区别？为什么 GPU utilization 高不代表 action deadline 满足？Kubernetes preemption 能否安全抢占 serving？MIG/time-slicing 是否提供显存和实时隔离？model cache key 为什么必须带 normalizer/schema revision？Ray placement group 与 Triton rate limiter 各解决什么？Lease epoch 如何防止旧 action 回包？controller ack、hold/stop 和 independent e-stop 谁最终负责？如何设计 canary 与 rollback 的 cohort/metric tuple？

**易错点**：把 quota 当 fairness；把 priority 当 safety；把 logical resource 当 physical isolation；把 preemption 当 cancellation；把 warm cache 当 checkpoint lineage；只报 GPU utilization 或平均 latency；把上游 scheduler 文档和 Git author 当个人 fleet ownership；把 simulator rollout 当 multi-robot production result。

**危险答案**：说“Kubernetes/Volcano/Ray/Triton 已经构成我的 VLA fleet”；说“GPU time-slicing/MIG 天然安全”；说“Lease renew 就代表机器人执行成功”；说“抢占 Pod 会自动撤回旧 action”；或说“五个项目的脚本证明我完成了 tenant fairness、fleet SLO 和物理安全”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [SYS-003 Knowledge](../knowledge/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling.html)：identity、capacity/placement、fairness/preemption、GPU/cache、lease、canary/cost 与项目边界。
2. [SYS-003 Source Freeze](../sources/vol_08_sys003_robot_fleet_multitenant_gpu_scheduling_source_freeze.html)：15 个 pinned public sources、5 项目 inventory/ledger SHA 与 15/15 probes。
3. Kubernetes [scheduler/quota/priority/Lease](https://github.com/kubernetes/website/tree/d19aacebe8061a6ef5dcc1e68904aaefe35c5445/content/en/docs/concepts)。
4. NVIDIA [device plugin](https://github.com/NVIDIA/k8s-device-plugin/tree/248164727d5d8bac7024a8e12a13e69246cf0969)、Volcano [fair-share/capacity/priority](https://github.com/volcano-sh/volcano/tree/329f91d73dc75e4b7f29a55e8c29fa6ea67cd6b0)、Triton [model/rate limiter](https://github.com/triton-inference-server/server/tree/d1e6320698eda052ea2c3deaba4069958171caa5)。
5. Ray [resources/placement/Serve](https://github.com/ray-project/ray/tree/6623e6b1e71fcdb7161d6ec0b190e345665d5ba3) 与 ROS 2 [node lifecycle](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/node_lifecycle.md)。
