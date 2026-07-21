# VOL 05 ENG-022 Source Freeze：Policy Server Batching / Backpressure / Timeout / Fallback

> 状态：`source_frozen / VLA-ENG-022 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-17  
> 证据截止：2026-07-17  
> 本切片冻结 policy server 的 batching、queue/backpressure、deadline、cancellation、fallback 与 closed-loop safety 来源和项目边界；下游已生成一个知识节点和一张 `unseen` 题卡，未生成口述成绩。  
> 前置：[ENG-017 Observability](../knowledge/vol_05_engineering_eval_eng017.html)、[ENG-018 Retry](../knowledge/vol_05_engineering_eval_eng018.html)、[ENG-021 Packaging](../knowledge/vol_05_engineering_eval_eng021.html) 与 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。

## 问题（Question）

VLA policy server 面对多机器人或多客户端请求时，怎样在吞吐、p99 latency、action freshness 和安全 fallback 之间做取舍？当请求进入队列、batch 尚未凑齐、模型推理超时、连接断开、GPU 不可用或 controller 不接受输出时，系统如何拒绝、取消、降级、恢复和记录？

核心链路：

```text
request → admission/deadline → bounded queue → batch formation
        → model inference → per-request demux → action validation
        → controller/robot → result or safe fallback
                 ↘ timeout/cancel/overload/incident metrics
```

“用了 WebSocket”“支持 batch”“有 timeout 参数”都不能单独证明 p99、队列上限、取消传播、safe fallback 或 closed-loop safety 已闭合。

## 1. 冻结指纹与许可

SHA 对 2026-07-17 取得的 pinned UTF-8 原文计算；本文件只记录公开来源、路径和 hash，不复制凭据值。

| 来源 | pinned URL | SHA-256 | 可支持的边界 |
| --- | --- | --- | --- |
| CPython asyncio Queue | [asyncio-queue.rst@2931f2](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-queue.rst) | `c7312064e8c18f1e45656bbabb59949cdd0adf258f32595d073b2e66593244d2` | bounded `maxsize`、`put` 阻塞、`QueueFull`、`task_done/join`、shutdown 语义 |
| CPython asyncio tasks/timeouts | [asyncio-task.rst@2931f2](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-task.rst) | `1d833356e1a5977399a0668ef7a07223db793cc1a1bcad4dae4934d8d8434cd2` | `asyncio.timeout`/`wait_for` 的 deadline、cancel 与 `TimeoutError` 边界 |
| Triton model configuration | [model_configuration.md@0ae38c](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/model_configuration.md) | `01e50042a66024ad5c9143e7aa3f43b0338f29f8ef6cc42979909589774b8151` | `max_batch_size`、batch dimension、ragged input 与 dynamic/sequence batcher 前置条件 |
| Triton dynamic batcher | [batcher.md@0ae38c](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/batcher.md) | `577e45c86b65a73e42aca1bb406d48a5edf25540e9312de904388ae69c1f9505` | preferred batch、max queue delay、priority/queue size、timeout action 与 sequence batching |
| OpenPI policy server | [websocket_policy_server.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/serving/websocket_policy_server.py) | `1370d345e6c3c5b8f15573050e485e60a5b423d1df33e24b237805e6b442b026` | WebSocket handler、逐请求 `policy.infer`、server timing、connection close/error |
| OpenPI serve entry | [scripts/serve_policy.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/scripts/serve_policy.py) | `eccc0448b4873fd30a1fff3355c5de7a7c227138e6db04b7dcaa5bb38a6a5809` | checkpoint/default policy 加载、metadata、server 启动、可选 recorder |
| OpenPI policy interface | [policy.py@15a9616](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py) | `a2ac5236e23b11d0f5a840d4a8fef148d89dba921d5452ec5dfcd5a6ffa46f20` | input/output transforms、policy timing、action result boundary |
| 本地 OpenPiVLA action server | 项目 `scripts/eval_lerobot_action_server.py` | `B1B7FB9B7A86355B9C1843CDE971B38FD26A2DAB1F18550128671F79F1AB4F39` | connect/infer timeout、server unavailable、per-sample action eval 的本地入口 |
| 本地 OpenPiVLA rollout | 项目 `scripts/run_aloha_sim_real_rollout.py` | `E583E4770E4F867FA7B4BEABB3C88964EAB5B3E1AECBD1B59B870B20EF191DE3` | policy rollout、episode/action metrics 与 failure output 入口 |
| 本地 deployment record | 项目 `DEPLOYMENT.md` | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14` | official server/client/checkpoint/path 与 rollout protocol 记录 |
| Robot Harness registry | `server/tools/registry.py` | `EF1AFE36697D16F4C2A1392F618444712A87F2F88EE3BDABE409BD2948D24CF1` | tool polling timeout、cancel、best-effort compensation；不是 VLA inference batcher |
| Robot Harness runtime | `server/agent/runtime.py` | `CEE9148C2987DA7FF6839534EBCFED75B953A8678742AD9442523F96A6A77280` | request cancel context、robot scope、lock cleanup |

官方文档说明机制和配置语义；项目文件只支持“存在某个入口/局部 hook”，不支持统一 policy server SLO、batching、fallback 或 robot safety 已完成。

## 2. Admission、queue 与 backpressure 合同

### 2.1 Bounded queue

用 `maxsize` 限制未完成请求数，队列满时必须明确：拒绝（429/overload）、等待到 caller deadline、低优先级淘汰，或进入受控 fallback。无界队列会把过载转化为 stale action、内存增长和 p99 爆炸。

```text
queue_depth ≤ Q_max
admit if queue_depth < Q_max and deadline - now > min_service_budget
else reject/defer with reason=overload_or_deadline
```

CPython `asyncio.Queue` 的 `put()` 在达到 `maxsize` 时阻塞，队列操作本身没有 timeout 参数，要用 `asyncio.wait_for`/`timeout` 包装；因此 admission timeout、queue wait 和 model inference timeout 必须拆开计时。

### 2.2 Batching 与 freshness

Triton dynamic batcher 要求模型声明 `max_batch_size` 和 batch dimension；可以用 preferred batch size 和 `max_queue_delay_microseconds` 在吞吐与等待之间取舍。VLA 还要加 action freshness：较大的 batch 或 queue delay 可能让 observation 到 action 的 age 超过 controller deadline。

每个 request 至少记录：`enqueue_ts/dequeue_ts/batch_id/infer_start/infer_end/deadline/action_age`。不能只报平均 throughput。

### 2.3 Shape 与 sequence

VLA 请求可能包含不同 image resolution、camera 数量、prompt token length、action horizon 或 robot state shape。若不能 ragged/pad 到同一 contract，不能把“请求同时到达”强行 batch；sequence/robot-affinity 请求还可能需要 sticky routing，而不是任意混 batch。

## 3. Deadline、cancellation 与 timeout budget

端到端 deadline 应拆为：

```text
T_total = T_admission + T_queue + T_batch_wait + T_infer
        + T_postprocess + T_transport + T_controller_margin
```

deadline 传播规则：

1. caller 给绝对 deadline 或剩余 budget，不在每层重新加完整 timeout；
2. queue wait、batch wait、model infer、postprocess、send 和 controller 各自扣减预算；
3. timeout 时取消 awaitable，并等待 cancellation 完成；不能只返回错误而让 GPU/robot action 继续执行；
4. response 标记 `timeout_stage`、`request_id`、`model_revision`、`batch_id` 和是否触发 fallback；不记录敏感 observation 原文。

CPython `wait_for` 在 timeout 时取消任务并抛 `TimeoutError`，取消清理本身可能延长总等待；因此必须做 cancellation latency 与 leaked-task 监控。

## 4. Fallback：先定义安全，再定义可用

VLA fallback 不是简单“换小模型”：

| 触发 | 允许动作 | 禁止动作 | 证据 |
| --- | --- | --- | --- |
| queue overload | reject/defer、保持安全 hold、已验证低风险 controller | 执行 stale action、无界排队 | overload negative test、queue depth/p99 |
| model timeout | stop/hold/last-safe action（有 TTL）、安全 controller | 无限沿用旧 chunk、静默重试造成重复动作 | timeout injection、action age、side-effect audit |
| worker/GPU unavailable | known-good local policy 或 safe stop | 未验证 checkpoint/processor fallback | health/readiness、bundle compatibility |
| malformed action | reject、clip 仅在 contract 允许时、safe stop | 盲目 reshape/denorm/axis swap | schema/property/controller test |
| connection loss | cancel pending request、robot-side watchdog | 服务端继续向断开的 robot 推 action | disconnect drill、watchdog trace |

fallback 必须有 TTL、owner、reason、恢复条件和审计事件；“last action”只有在 action age、速度/力矩和安全边界允许时才可能是 safe。

## 5. OpenPI 与本地项目边界

### 5.1 OpenPI official server

OpenPI frozen `WebsocketPolicyServer` 建立 WebSocket server，handler 收到消息后调用 `self._policy.infer(obs)`，记录 `infer_ms` 后发送 action；它有 connection close 和内部错误路径。源码没有因此证明 dynamic batching、bounded admission queue、deadline propagation、safe fallback、multi-robot fairness 或 closed-loop watchdog。

`scripts/serve_policy.py` 加载 checkpoint/default policy、metadata 和可选 recorder，再创建 server；它说明启动路径，不说明生产 SLO。

### 5.2 OpenPiVLA local evidence

本地 `eval_lerobot_action_server.py` 有 `connect_timeout_seconds`、`infer_timeout_seconds`，连接失败会写 `server_unavailable`，推理异常会写 `infer_failed`；这是 offline evaluation 的 failure reporting hook。它不等于 online policy server 的 queue/backpressure/batch/fallback 闭环。

本地 rollout 脚本和 deployment 记录 official OpenPI WebSocket client/server、checkpoint path、episode/action metrics；当前没有 formal Qwen checkpoint 的 immutable server bundle、batch load test、p99 SLO 或 safe fallback drill。

### 5.3 Robot Harness

Robot Harness registry/runtime 能证明 tool polling timeout、cancel context、robot lock cleanup、best-effort compensation 和 scope filtering；这些是 tool/robot side-effect control，不是 VLA model inference scheduler。不能把 tool timeout 直接称为 policy server timeout 或 batching。

## 6. 验证伪代码（工程合同）

```python
async def serve_request(req, queue, policy, controller, fallback, clock):
    deadline = req.deadline
    if deadline - clock.now() < MIN_BUDGET or queue.full():
        return fallback.overload(req, reason="admission")

    item = await asyncio.wait_for(queue.put(req), timeout=remaining(deadline, clock))
    try:
        batch = await collect_compatible_batch(queue, req, deadline)
        outputs = await asyncio.wait_for(policy.infer(batch), timeout=remaining(deadline, clock))
        action = validate_and_demux(outputs, req.schema)
        return await asyncio.wait_for(controller.send(action), timeout=remaining(deadline, clock))
    except TimeoutError:
        await cancel_inflight(req.request_id)
        return fallback.timeout(req, reason=timeout_stage(clock))
    except (Overload, InvalidAction) as exc:
        return fallback.reject(req, reason=type(exc).__name__)
    finally:
        record_queue_wait_batch_deadline_and_action_age(req)
        queue.task_done()
```

伪代码表达 admission→bounded queue→compatible batch→deadline-aware inference→action validation→controller/fallback；它不是 OpenPI 或本地项目现有实现。

## 7. 验证矩阵

| Case | 注入 | 通过条件 |
| --- | --- | --- |
| burst overload | 并发请求超过 `Q_max` | bounded memory；明确 reject/defer；无 stale action |
| batch wait | 请求稀疏/高峰交替 | queue delay、batch size、p50/p95/p99 和 action age 可解释 |
| shape incompatibility | resolution/camera/H/D/prompt 不同 | 不混 batch或显式 pad/ragged contract；无 silent reshape |
| queue timeout | deadline 在排队阶段到期 | request cancelled、reason=queue、无后续 infer/send |
| infer timeout | model worker 超时 | cancellation/leaked task 受控；fallback TTL 与 audit 完整 |
| transport disconnect | client/robot 断开 | pending work cancel；robot watchdog/hold 生效 |
| malformed action | NaN、越界、错误 axis/unit | reject/safe stop；不盲目 denorm 或执行 |
| worker failure | GPU/process kill | readiness fail；known-good fallback 或 safe stop，不加载未验证 bundle |
| retry storm | caller/server 同时 retry | idempotency/request key 或限流，副作用不重复 |
| recovery | worker 恢复/队列 drain | old request 不复活；新 revision/health/queue metrics 可追溯 |

## 8. Source Gate 结论

官方来源支持：bounded queue 是 backpressure 的基础；dynamic batching 需要明确 max batch/shape/queue delay；deadline 应传播并在 timeout 时取消任务；fallback 必须绑定 freshness、side-effect safety、TTL 和审计。OpenPI server 只提供逐请求 WebSocket infer 与 timing/error 基线，OpenPiVLA local script 提供 connect/infer timeout failure reports，Robot Harness 提供局部 tool timeout/cancel/compensation。

当前缺：统一 admission queue、dynamic batching policy、p99/action-age SLO、deadline propagation、cancel/leaked-task proof、known-good bundle fallback、robot watchdog、burst/retry storm/load test 和 multi-client fairness。Verdict 保持 `WARN`；知识页 `knowledge_24_of_44` 与一张 `unseen` 题卡已生成，后续综合 resilience 节点后置。

## References

1. CPython [`asyncio-queue.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-queue.rst) 与 [`asyncio-task.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-task.rst)。
2. NVIDIA Triton [`model_configuration.md@0ae38c`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/model_configuration.md) 与 [`batcher.md@0ae38c`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/batcher.md)。
3. Physical Intelligence [`openpi@15a9616`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：`websocket_policy_server.py`、`scripts/serve_policy.py`、`policies/policy.py`。
4. 本仓库 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[ENG-017 Observability](../knowledge/vol_05_engineering_eval_eng017.html)、[ENG-018 Retry](../knowledge/vol_05_engineering_eval_eng018.html) 与 [ENG-021 Packaging](../knowledge/vol_05_engineering_eval_eng021.html)。
