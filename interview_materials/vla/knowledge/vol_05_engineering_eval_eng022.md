# VOL 05 Engineering / Evaluation：Policy Server Batching、Backpressure、Timeout 与 Fallback（ENG-022）

> 状态：`drafted / knowledge_24_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-022`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-022 Policy Server Resilience Source Freeze](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)。  
> 核心边界：CPython/Triton/OpenPI 给出 queue、batch、deadline 与 server baseline；OpenPiVLA 只有 offline timeout reports，Robot Harness 只有 tool-side timeout/cancel/compensation，不能声称 VLA policy server 已具备 batching、SLO、safe fallback 或多机器人 fairness 闭环。

## 问题（Question）

当多个机器人或客户端同时请求 VLA 推理，怎样在吞吐、p99 latency、action freshness 和安全性之间设计 policy server？请求排队、batch 未凑齐、模型超时、连接断开、GPU 故障或 action 非法时，如何拒绝、取消、降级、恢复和留下可审计证据？

回答应拆成：

1. admission 与 bounded queue；
2. compatible batching 与 shape/freshness；
3. deadline budget 与 cancellation propagation；
4. action validation、controller watchdog 与 fallback；
5. metrics、load/chaos drill、retry storm 和 recovery。

## 知识地图位置与前置依赖

```text
ENG-017 observability + ENG-018 retry + ENG-021 immutable bundle
                         ↓
admission → bounded queue → compatible batch → deadline-aware infer
                         ↓
validate/demux → controller/watchdog → result or safe fallback
                         ↓
queue/infer/action-age SLO → overload/timeout/rollback drill
```

前置：[ENG-017 Training Observability](vol_05_engineering_eval_eng017.html)、[ENG-018 Retry](vol_05_engineering_eval_eng018.html)、[ENG-021 Packaging](vol_05_engineering_eval_eng021.html)。

## 1. 30 秒直觉：先限制过载，再谈 batch 加速

一个可信的 policy server 不是“收到请求就调用 `infer`”：先用 bounded admission queue 限制内存和 stale work，再只把 shape、modality、deadline、robot affinity 兼容的请求组成 batch；deadline 从 caller 传播到 queue、batch wait、infer、postprocess、transport 和 controller。超时或非法 action 必须取消后续副作用，并依据 TTL、action age 和已验证 bundle 触发安全 fallback。吞吐、p99、queue depth、batch size 和 fallback rate 都要可测。

## 2. Admission 与 bounded queue

### 2.1 Queue contract

设 `Q_max` 为最大未完成请求数：

\[
admit(r)=\mathbf{1}[q<Q_{max}\land deadline(r)-now>B_{min}]
\]

队列满或剩余预算不足时，系统必须选择明确策略：拒绝/限流、等待到 caller deadline、低优先级淘汰或进入受控 fallback。无界队列会把突发流量转成内存增长、p99 爆炸和过期 action。

CPython `asyncio.Queue(maxsize)` 中，`put()` 在满时等待，`put_nowait()` 抛 `QueueFull`；队列操作本身没有 timeout 参数，要外包 `asyncio.wait_for` 或 `asyncio.timeout`。因此 admission wait、queue wait、batch wait、infer timeout 必须分开计时。

### 2.2 Admission fields

```text
request_id / idempotency_key / client / robot_id / priority
enqueue_ts / absolute_deadline / max_action_age
model_revision / processor_revision / action_schema
observation_shape / camera_set / prompt_length
```

不要把 raw image、prompt 或 token 放进普通 queue metrics；只保留 request/correlation/reference。

## 3. Batching：吞吐和 freshness 的约束优化

Triton dynamic batcher 要求模型声明 `max_batch_size` 和 batch dimension；可以用 preferred batch size、`max_queue_delay`、priority queue 和 queue size 调节吞吐/等待。对 VLA 还要加入 action freshness：

\[
age_{action}=t_{send}-t_{observation},\quad
T_{total}=T_{queue}+T_{batch}+T_{infer}+T_{post}+T_{transport}+T_{margin}
\]

如果 `age_action > freshness_budget`，即使模型最终返回，也应丢弃或进入安全 stop，而不是执行 stale chunk。

### 3.1 Compatible batch key

可用 `(model_revision, processor_revision, camera_set, resolution, prompt_bucket, action_horizon, action_dim, dtype, robot_affinity)` 作为 batch compatibility key；不能仅按到达时间合并。不同 camera 数量、H/D、padding/mask、frame/unit 或 deadline 的请求，需要显式 pad/ragged/sequence contract，否则拒绝混 batch。

### 3.2 VLA-specific trade-off

- batch 越大，GPU utilization 可能更好，但 queue delay 和 action age 增加；
- preferred batch size 适合稳定流量，不适合极低延迟单机器人请求；
- sequence/robot-affinity 可避免跨机器人状态污染，却降低可合批率；
- micro-batch 和 dynamic batch 需要 matched load test，不能用离线单样本 latency 推断 online p99。

## 4. Deadline 与 cancellation propagation

端到端预算可拆为：

```text
T_total = T_admission + T_queue + T_batch_wait + T_infer
        + T_postprocess + T_transport + T_controller_margin
```

工程规则：

1. 使用绝对 deadline 或剩余 budget，下游不重复加完整 timeout；
2. 每阶段扣减 budget，并记录 `timeout_stage`；
3. timeout 取消 awaitable、GPU task、pending send 和 controller side effect；
4. cancellation cleanup 结束后才释放 queue/robot lock，并记录 leaked-task；
5. response 只带 request/model/batch/status/reason/timing reference，不复刻敏感 observation。

`asyncio.wait_for` 在超时时取消 awaitable 并抛 `TimeoutError`，取消清理可能使实际等待超过 timeout；因此需要测 cancellation latency，而不是只看异常出现时间。

## 5. Action validation 与 fallback

### 5.1 Fallback matrix

| 触发 | 可选动作 | 禁止动作 | 必要证据 |
| --- | --- | --- | --- |
| overload | reject/defer、safe hold、已验证低风险 controller | 无界排队、执行 stale chunk | queue depth/p99/overload drill |
| infer timeout | TTL 内 last-safe/hold、safe stop | 无限复用旧 action、静默重复 retry | timeout injection、action age、side-effect trace |
| worker/GPU down | known-good bundle、safe stop | 未验证 checkpoint/processor fallback | readiness、bundle compatibility、rollback |
| malformed/NaN action | reject、contract-approved clip、safe stop | 盲目 reshape、axis/unit swap | schema/property/controller tests |
| disconnect | cancel pending work、robot watchdog | 断连后继续发送 action | disconnect drill/watchdog trace |

“last action”只有在 TTL、速度/力矩边界和 controller contract 允许时才可能安全。fallback 必须有 `reason/owner/ttl/recovery_condition`，并能区分 model timeout、queue overload、invalid action 和 transport failure。

## 6. OpenPI、OpenPiVLA 与 Robot Harness 证据边界

### 6.1 OpenPI official baseline

OpenPI frozen `WebsocketPolicyServer` 接收消息后调用 `policy.infer(obs)`，记录 `infer_ms` 后回传 action，并处理连接关闭和内部错误。`scripts/serve_policy.py` 加载 policy/checkpoint、metadata 和可选 recorder，再启动 server。这是逐请求 server baseline，不证明 dynamic batching、bounded admission、deadline propagation、fallback 或 multi-client fairness。

### 6.2 OpenPiVLA

本地 `eval_lerobot_action_server.py` 有 `connect_timeout_seconds`、`infer_timeout_seconds`，连接失败写 `server_unavailable`，推理异常写 `infer_failed`；这是 offline action evaluation 的 failure-reporting hook。部署记录使用 official OpenPI WebSocket client/server 和 checkpoint path；当前没有 formal Qwen checkpoint 的 batch load test、p99/action-age SLO、fallback watchdog 或 safe rollback artifact。

### 6.3 Robot Harness

Robot Harness 的 registry/runtime 可证明 tool polling timeout、cancel context、robot lock cleanup、best-effort compensation 与 scope filtering；这些约束 tool/robot side effects，不是 VLA inference scheduler。不能把 tool timeout 写成 policy server batching 或端到端 fallback 证明。

## 7. 验证伪代码（工程合同）

```python
async def serve_request(req, queue, policy, controller, fallback, clock):
    if queue.full() or remaining(req.deadline, clock) < MIN_BUDGET:
        return fallback.overload(req, reason="admission")

    await asyncio.wait_for(queue.put(req), timeout=remaining(req.deadline, clock))
    try:
        batch = await collect_compatible_batch(queue, req, req.deadline)
        outputs = await asyncio.wait_for(policy.infer(batch), timeout=remaining(req.deadline, clock))
        action = validate_and_demux(outputs, req.action_schema)
        return await asyncio.wait_for(controller.send(action), timeout=remaining(req.deadline, clock))
    except TimeoutError:
        await cancel_inflight(req.request_id)
        return fallback.timeout(req, reason=timeout_stage(clock))
    except InvalidAction:
        return fallback.reject(req, reason="invalid_action")
    finally:
        record_queue_wait_batch_deadline_and_action_age(req)
        queue.task_done()
```

伪代码表达 admission→bounded queue→compatible batch→deadline-aware infer→validate→controller/fallback；不是任何本地项目已有实现。

## 8. 验证矩阵

| Case | 注入 | 通过条件 |
| --- | --- | --- |
| burst overload | 并发超过 `Q_max` | bounded memory、明确 reject/defer、无 stale action |
| batch wait | 稀疏/高峰流量 | batch size、queue delay、p50/p95/p99、action age 可解释 |
| shape conflict | camera/resolution/prompt/H/D 不同 | 不混 batch或显式 pad/ragged；无 silent reshape |
| queue timeout | deadline 在排队时到期 | request cancel、reason=queue、无后续 infer/send |
| infer timeout | worker 超时 | cancellation/leaked-task 受控、fallback TTL/audit 完整 |
| disconnect | client/robot 断开 | pending work cancel，watchdog/hold 生效 |
| malformed action | NaN、越界、axis/unit 错 | reject/safe stop，不执行盲目 denorm |
| worker failure | kill GPU/process | readiness fail，known-good fallback 或 safe stop |
| retry storm | caller/server 同时重试 | idempotency/rate limit，副作用不重复 |
| recovery | worker 恢复/queue drain | old request 不复活，新 revision/health 可追溯 |

## 9. Trade-off、bad case 与追问

### 9.1 Trade-off

- dynamic batching 提高吞吐但增加 queue/action age；必须用 freshness budget 限制；
- bounded queue 保护系统但会降低接受率；拒绝原因比无界等待更可解释；
- fallback 提升可用性却可能执行旧策略；必须有 TTL、bundle compatibility 和 controller safety gate；
- cancellation 降低重复副作用，但清理与锁释放可能延长真实 latency；
- priority/fairness 避免关键机器人饥饿，但会改变 batch efficiency，需要独立 SLO。

### 9.2 高概率 bad case

1. 无界 queue 让请求排队到 action 已过期。
2. 只看 GPU throughput，不记录 queue wait、action age 和 p99。
3. 不同 camera/H/D/frame 请求被 silent reshape 后混 batch。
4. infer timeout 返回了，但 GPU task 或 controller send 仍在继续。
5. 用任意旧 checkpoint/processor 作为 fallback，没有 bundle gate。
6. 断连后 server 仍发送 action，robot 侧没有 watchdog。
7. caller 和 server 同时 retry，导致重复动作或 queue storm。
8. 把 OpenPI 逐请求 WebSocket baseline 写成生产级 batching/SLO 方案。

### 9.3 面试追问

1. queue delay 和 action freshness 如何共同设 budget？
2. 为什么 `max_batch_size` 不代表 VLA 请求一定可合批？
3. `wait_for` timeout 后如何证明没有 leaked task？
4. 什么情况下 last-safe action 是危险的？
5. fallback 模型如何与 ENG-021 bundle manifest 绑定？
6. 如何测 burst、retry storm、disconnect 和 worker failure？
7. OpenPI server 当前直接证据支持什么、不支持什么？
8. Robot Harness tool timeout 和 policy inference timeout 的边界是什么？

## 10. 结论与下一步

可信的 VLA policy server 先做 bounded admission/backpressure，再按 shape/modality/deadline/robot affinity 合批；deadline 贯穿 queue、batch、infer、postprocess、transport 和 controller；timeout 必须传播 cancellation；action 要做 schema/age/finite 检查；fallback 绑定 TTL、已验证 bundle、watchdog 和审计。吞吐不能代替 p99、freshness 和 side-effect safety。

OpenPI 只证明逐请求 WebSocket infer/timing/error baseline；OpenPiVLA 只证明 offline timeout reports；Robot Harness 只证明 tool-side timeout/cancel/compensation。统一 queue、batch、SLO、fallback、watchdog 和 chaos/load evidence 仍缺。因此本节点保持 `WARN`，题卡保持 `unseen`；下一步可口述 `VLA-ENG-022` 或补 queue/SLO/fallback artifact，后续 resilience 节点继续后置。

## References

1. [ENG-022 Source Freeze](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)：CPython/Triton/OpenPI pinned source、本地 timeout hooks 与验证边界。
2. CPython [`asyncio-queue.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-queue.rst) 与 [`asyncio-task.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-task.rst)。
3. NVIDIA Triton [`model_configuration.md@0ae38c`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/model_configuration.md) 与 [`batcher.md@0ae38c`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/batcher.md)。
4. Physical Intelligence [`openpi@15a9616`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：WebSocket policy server、serve entry、policy timing。
5. 本仓库 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[ENG-017 Observability](vol_05_engineering_eval_eng017.html)、[ENG-018 Retry](vol_05_engineering_eval_eng018.html) 与 [ENG-021 Packaging](vol_05_engineering_eval_eng021.html)。

