# VOL 08 SYS-002：Policy Serving 与 Real-time Control Loop

> 状态：`drafted / SYS-VLA-002 / knowledge_8_of_phase / card_1_of_1_unseen / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[SYS-VLA-002 Source Freeze](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html)。

## 问题（Question）

怎样把 VLA policy 接入实时控制环，同时准确区分“能返回动作的 WebSocket demo”和“可审计、可降级、可验证的 policy service”？面试回答至少要覆盖 request/response schema、状态所有权、action chunk/replan、端到端 deadline、admission/backpressure、batching、controller 与 fail-safe 边界。

本页只做 source freeze 的教学转译。OpenPI 的 frozen revision 是最小 serving baseline；下面的 request envelope、deadline propagation、bounded admission 和 controller watchdog 是系统设计合同或验证要求，不能倒写成 OpenPI 已有能力，也不能写成个人项目已经上线。

## 1. 直觉与专业定义

### 1.1 Policy serving

通俗地说，policy serving 是一个“把观测送给策略、把动作候选返回给控制器”的服务层。它负责模型、预处理和推理生命周期，但不自动拥有机器人控制权。

专业地说，serving contract 是一个带身份、版本、时间戳和动作语义的函数：
`observation + task condition → action chunk + timing/validity metadata`。必须同时定义输入输出 schema、模型 revision、normalizer、动作 frame/unit、可执行期限和异常处理。

### 1.2 Observation/action schema

观测（observation）不只是图片。最小合同通常包括 camera frame、proprioception/state、语言任务、action history、capture timestamp 和 schema/model revision。动作（action）也不只是一个向量：需要声明 horizon (H)、每步维度 (D)、frame、unit、normalizer、controller mode，以及是否允许执行到下一次 replan。

frozen OpenPI server 的直接路径是“连接后发送 metadata；每次收到消息后调用 `policy.infer`，附加 server timing，再发送结果”。frozen client 是同步 `send → recv`。当前这些文件没有正式的 request ID、absolute deadline、action expiry 或 controller acknowledgement；这些字段只能作为后续设计建议。

### 1.3 Action chunk 与 replan

一次推理可以返回未来 (H) 行动作。consumer 在本地缓存 chunk，用 cursor 逐行消费，并在执行 (K) 行后重新请求，形成 receding-horizon 控制。OpenPI 的 `ActionChunkBroker` 和 LIBERO/DROID examples 直接支持这种 client-side 语义；但 `H`、`K` 是 example/config 选择，不是所有 VLA 的通用标准。

### 1.4 Deadline、action age 与 backpressure

deadline 是“这次结果最晚什么时候仍可用”的绝对时间合同；action age 是动作从 observation capture 到 controller apply 已经过的时间。backpressure 是负载超过服务能力时限制 admission、丢弃或降级请求，而不是让无界队列把延迟悄悄变成 stale action。

### 1.5 Soft real-time、hard real-time 与 controller boundary

soft real-time 允许少量 deadline miss，但要可测量、可告警、可降级；hard real-time 要求在明确上界内完成，通常还要处理 scheduler、page fault、memory lock、优先级和最大延迟。Python WebSocket + GPU inference 仅凭平均 `infer_ms` 不能证明 hard real-time。

policy server 只返回动作候选；controller apply、hold/stop、独立 watchdog 和 physical e-stop 是另一层状态机。RPC timeout 或 task cancellation 不等于已经撤回发送中的控制命令，更不等于机器人已经停止。

## 2. 三层架构与接口合同

### 2.1 Server、client/broker、controller 的状态所有权

| 层 | 直接持有的状态 | 必须回答的追问 | frozen OpenPI 证据边界 |
| --- | --- | --- | --- |
| Policy server | checkpoint、policy object、输入/输出 transform、连接 metadata、server-local timing | revision 切换、warmup、readiness、模型错误如何传播 | `websocket_policy_server.py` 支持 metadata 与 `recv → infer → send`；没有显式 queue、batch、deadline、watchdog |
| Client / broker | WebSocket 连接、latest observation、action chunk cache、cursor、replan cadence | stale response 如何丢弃、重连如何恢复、chunk 何时失效 | `websocket_client_policy.py` 为同步 send/recv；`ActionChunkBroker` 支持 cursor/horizon reset；没有 request ID/expiry |
| Controller / robot | apply state、hold/stop、执行 ack、限位、e-stop、惯性与外部 side effect | timeout 后谁接管、命令是否 exactly-once、物理停止如何证明 | 这些状态在 OpenPI serving 文件之外；不能从 WebSocket response 推断 |

### 2.2 建议的 request envelope（设计推断）

下面是面试中应主动冻结的最小字段，而不是 frozen OpenPI 的现有 schema：

| 类别 | 字段示例 | 目的 |
| --- | --- | --- |
| identity | `request_id`, `session_id`, `robot_id`, `model_revision`, `schema_version` | 去重、路由、回包关联、审计 |
| observation | `capture_ts`, `clock_id`, `camera_ids`, `state`, `action_history`, `prompt` | 计算 age，保证相机/状态语义一致 |
| timing | `deadline_abs`, `enqueue_ts`, `infer_start`, `infer_end`, `send_ts` | 分段预算、deadline miss 与 first divergence 定位 |
| output | `action_chunk`, `H`, `D`, `frame`, `unit`, `normalizer_revision`, `valid_until` | parser、反归一化、切片与 freshness 检查 |
| control | `replan_after_K`, `controller_mode`, `fallback_policy` | 明确执行几步、失败后谁接管 |

回答时要把“字段建议”和“代码已存在字段”分开：OpenPI metadata 可以承载 identity，但 source freeze 没有证明上述字段已经齐全。

## 3. Timing 数学：从 server-local 到 controller apply

### 3.1 端到端 critical path

令 (t_c) 为 observation capture，(t_e) 为 enqueue，(t_i) 为 inference start，(t_r) 为 client response receive，(t_p) 为 postprocess 完成，(t_a) 为 controller apply。首个动作的端到端延迟可写成：

\[
T_{\mathrm{e2e}}
=(t_e-t_c)+(t_i-t_e)+(t_r-t_i)+(t_p-t_r)+(t_a-t_p).
\]

变量解释：五项分别对应 capture/serialize、queue 或 batch wait、网络与 infer、parse/denorm/safety、controller handoff。实现映射：OpenPI 直接给出的是 server-local `infer_ms` 与 `prev_total_ms`；完整分解需要在 envelope 和 controller trace 中增加 timestamp，因此这是基于 EVAL-013 与 source freeze 的 design instrumentation，而非现成 OpenPI 指标。

### 3.2 Action age

若一次请求在 (t_c) 捕获观测并返回 (H) 行 chunk，第 (k) 行在 (t_{\mathrm{apply},k}) 被执行，则：

\[
A_k=t_{\mathrm{apply},k}-t_c,\qquad k=0,\ldots,K-1.
\]

(H) 是模型输出 horizon，(K\le H) 是下一次 query 前执行的行数。它说明“首行延迟低”不代表后续行仍新鲜；实现上要记录 capture/apply timestamp，并在 `valid_until` 或 age threshold 超过时触发 replan/fallback。S5/S6/S7 只证明 client cursor 和 example cadence，不替你选择 freshness 阈值。

### 3.3 剩余 deadline budget

设调用方给出的绝对 deadline 为 (D)，任一层当前时刻为 (t)，则剩余预算为：

\[
B_{\mathrm{remain}}=D-t.
\]

每层都重新设置一段完整 timeout 会把 queue、网络、推理和 controller 的预算重复计算。应传播同一个 deadline、统一 clock 语义，并把 `DEADLINE_EXCEEDED`、in-flight compute、stale response、controller hold/stop 分开记录。gRPC 文档支持 deadline propagation；将该语义接入 WebSocket VLA service 是 design inference。

## 4. Pipeline 与有注释伪代码

### 4.1 推荐的控制路径

```text
# Each stage must emit trace fields; this is a design pipeline, not frozen OpenPI code.
observation capture
  → schema / timestamp validation
  → bounded admission
  → compatible queue or batch
  → policy inference
  → parse / denormalize / safety check
  → controller apply + acknowledgement
  → metrics, fallback and audit trace
```

每个箭头都应能在 trace 中定位；只记录 `infer_ms` 无法回答“延迟究竟发生在 queue、网络还是 controller”。

### 4.2 面试级伪代码

```python
def online_rollout(env, policy_client, task, replan_steps):
    # Reset the environment and capture a timestamped observation.
    obs = env.reset(task)
    chunk = None
    cursor = 0

    while not obs.done:
        # Build the versioned request: images, state, prompt, and capture_ts.
        request = build_policy_observation(obs, task, capture_ts=clock.now())
        validate_schema(request)

        # Query only when no valid chunk remains or the replan cadence fires.
        if chunk is None or cursor >= replan_steps or chunk.is_expired(clock.now()):
            chunk = policy_client.infer(request, deadline_abs=request.deadline_abs)
            cursor = 0

        # Parse, denormalize, slice to controller dimensions, and enforce limits.
        action = output_transform(chunk.rows[cursor])
        safe_action = safety_check_or_fallback(action, obs)

        # Apply at the controller boundary; RPC success alone is not physical ack.
        obs = env.step(safe_action)
        record_trace(request, chunk, safe_action, obs, action_age=clock.now() - request.capture_ts)
        cursor += 1

    # Return the success predicate and failure trace, not just the last RPC status.
    return obs.info
```

伪代码中的 `build_policy_observation`、`output_transform` 和 `env.step` 必须替换为具体项目函数后才能声称 local-direct。OpenPI LIBERO example 直接证明了“执行 chunk 前 K 步并记录 success”的一种实现；本页的 deadline、expiry、safety 和 ack 是应补齐的系统设计层。

## 5. Admission、Backpressure 与 Batching

### 5.1 Bounded admission

CPython `asyncio.Queue(maxsize)` 在达到上限后会阻塞 `put`，而 queue API 本身没有 timeout 参数，因此必须在外层包裹 deadline-aware admission。面试中应明确选择：拒绝新请求、丢弃旧 observation、复用仍有效的 action chunk，还是切换到 fallback policy；不同选择会改变 freshness 与安全语义。

### 5.2 Dynamic batching 的兼容条件

Triton 文档中的 preferred batch、queue delay、queue size 和 timeout 只提供通用 batcher 机制。VLA 请求只有在 camera 数量/分辨率、prompt、state/action shape、normalizer、model revision 和 controller contract 兼容时才可 batch。把不同机器人请求“同时到达”直接拼成 batch，可能造成 padding、条件串线或错误反归一化。

### 5.3 Fresh observation 与 side-effect action

ROS 2 QoS 的 sensor profile 强调及时性、较小 keep-last depth 和可接受丢包；这可启发 observation queue 使用 latest-wins。但 action/command 有 side effect，不能无条件 latest-wins。旧 observation 可以丢，已确认要执行的 action 必须有 request ID、expiry、顺序和 controller ownership。

系统优化目标不是单独提高吞吐，而是同时约束 throughput、tail latency、action age、deadline miss rate 和 fallback rate。无界 queue 往往把 overload 变成“看似成功、实际过期”的动作。

## 6. Failure、降级与实时边界

| 故障 | 可能发生的层 | 正确处理 | 不能直接声称 |
| --- | --- | --- | --- |
| connect/recv 失败 | client/server/network | retry 或 fallback，并记录 request/session | “机器人已停止” |
| queue 满或 deadline 不足 | admission/queue | reject、复用仍新鲜 chunk 或切 fallback | “吞吐变高” |
| inference exception / timeout | server/GPU | 标记 request failed，丢弃 stale response，通知 controller | “in-flight kernel 已取消” |
| parse/denorm/limit 失败 | client/controller boundary | fail-closed、hold/stop、独立 watchdog | “模型输出天然安全” |
| controller ack 缺失 | controller/robot | 超时进入 hold/stop，保留 e-stop 路径 | “RPC 200 等于物理执行成功” |

### 6.1 Cancel compute 不等于 physical stop

asyncio task cancellation 与 gRPC deadline propagation 只描述软件任务/RPC 的取消语义。GPU kernel、已发出的 controller command、机器人惯性和外部副作用可能继续存在。因此回答必须拆成四件事：`cancel compute`、`discard stale response`、`controller hold/stop`、`independent e-stop`；后两项需要 controller/robot 直接证据。

### 6.2 Soft real-time 的验证门

若目标是 soft real-time，应至少收集 capture→apply 的 p50/p95/p99、最大 action age、deadline miss、queue depth、fallback rate 和 success predicate，并在固定 task/trial/seed 下对比。若声称 hard real-time，还要提供 scheduler、page-fault、memory-lock、priority 和最大延迟证据；ROS 2 pendulum real-time 文档可作为验证门参考，不能替代真实系统测量。

## 7. 实现证据与代码映射

| 证据层 | 文件/来源 | 可以回答 | 不可以回答 |
| --- | --- | --- | --- |
| official-code | OpenPI `websocket_policy_server.py`、`websocket_client_policy.py`、`action_chunk_broker.py` | metadata、同步 send/recv、server-local timing、client cursor | production queue/batch/deadline/watchdog |
| official-code | OpenPI LIBERO/DROID examples | `replan_steps=5`、open-loop horizon、env step 与 success logging | 通用 H/K、hard real-time、真机安全 |
| local-evidence | `scripts/eval_lerobot_action_server.py` | WebSocket client、connect/infer timeout wrapper、offline action metric 入口 | p99、cancel propagation、online controller |
| local-evidence | `scripts/run_aloha_sim_real_rollout.py` | in-process policy + `ActionChunkBroker` + env apply 的 rollout 入口 | network policy server、production serving |
| local-evidence | `DEPLOYMENT.md` | official server/client/checkpoint 路径与部署说明 | binary identity、SLO、watchdog、个人端到端 ownership |
| inference / design | CPython、Triton、gRPC、ROS 2 机制拼接 | bounded admission、compatible batching、deadline、QoS 与 real-time profiling 的设计要求 | 这些机制已存在于 OpenPI 或个人项目 |

阅读项目时保持四层顺序：`public upstream → local-direct → inference/design → unverified`。上游代码被仓库引用，不等于候选人写过、维护过或上线过同样的系统。

## 8. 五个项目的真实性边界

| 项目 | 面试可用 hook | 不能说的强 claim |
| --- | --- | --- |
| OpenPiVLA | offline WebSocket action eval、in-process broker rollout、timeout/failure summary、H/D/parser 风险 | production policy service、formal checkpoint serving、p99/fairness、cancel→physical stop、完整端到端 ownership |
| Robot Harness | tool polling timeout、cancel context、scope/lock cleanup、best-effort compensation | VLA inference batcher、action freshness、controller deadline、robot success |
| OPD | training/eval data route、strict scorer、多目标 checkpoint 选择 | policy serving、closed-loop controller、fleet 调度 |
| WAM | simulator rollout launcher、chunk/controller schema、diagnostic artifacts | network serving、hard real-time、真机 watchdog、已验证 checkpoint uplift |
| UWM / LIBERO | simulator protocol、action/state/normalizer、rollout evidence | production policy service、multi-robot serving、跨协议真机泛化 |

## 9. 面试回答模板与禁说清单

### 9.1 60 秒回答模板

“我先把系统拆成 server、client/broker、controller 三层。OpenPI 的 frozen baseline 是连接后 metadata，再按 observation→infer→action 返回；chunk cursor 和 replan 在 client/example 侧。若要做可审计的实时服务，我会在 request 中加入 request/session/robot/model/schema identity、capture timestamp、absolute deadline，在 admission 层做 bounded queue 和兼容 batch，在输出侧做 denormalize、limit、expiry 与 controller ack。指标不能只看 `infer_ms`，还要看 capture→apply、action age、deadline miss 和 fallback。最后，RPC timeout 只代表软件请求失败，physical stop 仍由 controller watchdog/e-stop 负责。对我的项目，我会把 OpenPiVLA 的 offline WebSocket 与 in-process broker 作为局部 evidence，不把它们升级成 production serving。”

### 9.2 不能说的强 claim

- “OpenPI 已经有 production-grade queue、dynamic batching、deadline propagation、multi-robot fairness 或 watchdog。”
- “`server_timing.infer_ms` 就是端到端 capture→controller apply latency。”
- “LIBERO 的 (H/K) 示例值是所有机器人和所有 VLA 的标准。”
- “timeout 或 exception 自动取消 GPU、清空旧动作并让机器人物理停止。”
- “引用 official code、目录路径或文档，就等于我个人拥有端到端实现和上线责任。”

## 10. 结论与下一步

高质量的 policy-serving 回答不是背 WebSocket API，而是能把 schema、状态所有权、chunk freshness、deadline budget、bounded overload、controller ack 和独立 e-stop 串成同一条证据链。当前 source gate 已证明 OpenPI 最小 serving path、client-side chunk 语义和跨来源系统设计机制；尚未证明统一服务、load/fault test、E2E timestamp trace、formal checkpoint bundle 或候选人完整 ownership。

下一步：保持 `SYS-VLA-002` 题卡未生成；先用本页 60 秒模板做一次口述，或补充一个带 request ID/capture→apply timestamp 的最小 trace artifact。未完成真实口述前不创建 `coaching_state.md`，不启动 `SYS-VLA-003`。

## 参考文献（References）

1. [SYS-VLA-002 Source Freeze](../sources/vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html)：OpenPI、CPython、Triton、gRPC、ROS 2 的 frozen revisions 与 14/14 probes。
2. Physical Intelligence，[OpenPI `openpi@15a9616a`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：server/client、broker 与 LIBERO/DROID examples。
3. CPython，[asyncio queue/tasks](https://github.com/python/cpython/tree/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library)：bounded queue 与 cancellation 语义。
4. NVIDIA Triton，[batcher/model configuration](https://github.com/triton-inference-server/server/tree/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide)：preferred batch、queue delay/size 与 timeout policy。
5. gRPC，[Deadlines](https://github.com/grpc/grpc.io/blob/78db5a6f78ee0d3426cf53cee07739196d962ea2/content/en/docs/guides/deadlines.md)；ROS 2，[QoS design](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/qos.md) 与 [pendulum real-time](https://github.com/ros2/demos/blob/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control/README.md)。
6. 本仓库 [ENG-022 Policy Server Resilience](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)、[EVAL-013 Latency/Deadline/Jitter](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html) 与 [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
