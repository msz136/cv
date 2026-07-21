# VOL 04 World Model / Sim2Real：Test-time Planning Latency、Communication 与 Risk Contract（WM-030）

> 状态：drafted / VLA-WM-030 / knowledge_32_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释 N、world/value ensemble、search depth、通信和 controller 的统一计时与限险，不宣称本地 WAM 已实施。  
> 前置：[WM-023 Open-loop / Receding Horizon](vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)、[WM-029 OOD Value / Pessimism](vol_04_world_model_sim2real_wm029_imagined_ood_value_calibration_pessimism.html)、[WM-030 Source Freeze](../sources/vol_04_wm030_test_time_planning_latency_risk_source_freeze.html)。

## 问题（Question）

test-time planning 增加的 N、world rollout、value scoring 与通信开销怎样计时和限险？高分回答必须能画出 critical path，区分 algorithmic work 与 wall-clock，解释 CUDA timing、N/P/ensemble/depth、同步/异步 deadline、action freshness 和 fallback。

## 1. 30 秒结论

我不会只报 model forward 或平均 FPS。先把 observation capture/upload、server queue/preprocess、N 个 action proposal、每个 proposal 的 world/value sampling、selector、download、action queue 和 controller apply 串成同一 request trace。串行 N 近似累加；多 GPU 并行由最慢 branch 加 IPC/queue/collect 决定，仍要报告 N、并行度 P、world/value ensemble、depth 和 denoise。

GPU stage 用 CUDA Event 或同步后的 timing，端到端用 monotonic clock，分 cold-start/steady-state 并报 p50/p95/p99。异步 overlap 要满足 \(L_{plan}^{p99}+M\le K/f_{ctrl}\)，同步模式则约束最大 pause；超时、结果不全或 action stale 时按版本/TTL 丢弃并走 direct policy、hold 或 safe stop。最后用相同 candidate prefix 与 episode 做 N–latency–success matched curve。

## 2. 先画完整 critical path

```text
sensor timestamp
  → client encode / upload
  → admission / queue / preprocess
  → N × [action → E_w world → E_v value]
  → depth/value aggregation → selector
  → response serialize / download
  → action queue → controller apply
```

端到端量不是 server return time，而是：

\[
L_{e2e}=t_{apply}-t_{obs}.
\]

变量解释：\(t_{obs}\) 是传感器捕获时间，\(t_{apply}\) 是 controller 实际应用动作的时间。实现映射：每个 request 保存 `request_id、observation_version、t_obs、t_encode、t_server_recv、t_queue_in/out、t_gpu_start/end、t_select、t_client_recv、t_enqueue、t_apply`；跨主机要说明 clock sync 或只用 RTT。

展开后：

\[
L_{e2e}=L_{capture}+L_{encode}+L_{up}+L_{queue}+L_{pre}
+L_{plan}+L_{select}+L_{down}+L_{ctrl}.
\]

变量解释：这些 stage 可能并发，只有沿同一 critical path 的 timestamp 才能相加；不能把各模块独立 profile 的最优数字拼成一个虚假的端到端值。Triton 的 client/send-receive/server queue/compute 分解可作为 telemetry 设计参照，但不意味着当前服务使用 Triton。[4]

## 3. N、ensemble、depth 到底增加多少工作

设：

- \(N\)：action proposal 数；
- \(E_w\)：每个 action 的 world/future samples；
- \(E_v\)：每个 future 的 value samples；
- \(D\)：search depth；
- \(P\)：并行 worker/GPU 数；
- \(s_a,s_w,s_v\)：action/world/value denoising steps。

depth=1 时，调用量级可以写成：

\[
W_{plan}\approx N(C_a+E_wC_w+E_wE_vC_v).
\]

变量解释：\(C_a,C_w,C_v\) 分别是一次 action/world/value generation work，并随 denoise、图像/序列长度、dtype/backend、batch 改变。这是调用数模型，不保证 latency 对 denoise 或 N 严格线性。[1][2]

串行 wall-clock：

\[
L_{serial}\approx\sum_{i=1}^{N}L_i+L_{select}.
\]

并行 wall-clock（\(P\ge N\)）：

\[
L_{parallel}\approx L_{dispatch}+\max_i L_i+L_{collect}+L_{select}.
\]

变量解释：并行由 straggler 决定，还会付 observation copy、process queue、serialization、CPU/GPU copy 与 result collection 成本；\(P<N\) 时需要多 wave。并行 wall-clock 下降不等于总 compute/GPU-hours 下降。

depth >1 还会把 predicted future 变成下一层 current state，再生成 action/world/value。若每层保留多个 future，work 可能随 branch factor 扩张；必须同时冻结 pruning/aggregation，而不是只写“depth=2”。Frozen Cosmos 默认 depth=1。[2]

## 4. Cosmos 公开 recipe 应该怎么读

| 路径 | 公开条件 | Wall-clock | 正确解释 |
| --- | --- | ---: | --- |
| direct joint generation | 1×H100，LIBERO/RoboCasa，5 denoise | 0.61 s/chunk | action/future/value 同次生成；指定硬件/实现 |
| direct joint generation | 1×H100，1 denoise | 0.16 s/chunk | quality-latency trade-off；不是通用加速比 |
| ALOHA direct | 1×H100，10 denoise | 0.95 s/chunk | 论文说明机器人暂停 0.95 s，再执行 2 s chunk |
| real-robot planning | N=8，8×H100；10-step action，3×5-step world，future 各 5×5-step value | 4.9 s/search | 多 GPU best-of-N 的指定 recipe；论文也承认动态任务适用性受限 |

Cosmos 代码还显示：LIBERO/RoboCasa 默认 N=1、parallel off、depth=1、world/value ensemble off、`parallel_timeout=15s`。上游支持 best-of-N/ensemble 与默认启用是两回事。[1][2]

ALOHA server 的 `/act` 默认返回 selected action/future/value；若请求 `return_all_query_results`，会把全部 actions/futures/values/depth results 序列化回 client。此时 payload 和传输时间可能远大于只返回 action，必须记录 request/response bytes，而不是把通信统称为“网络有点慢”。[2]

## 5. 为什么 `time.time()` 还不够

CUDA 默认异步：CPU 发出 kernel 后可以继续执行。PyTorch 官方明确说，未同步的 CPU timing 不准确；可以在 benchmark 中显式 `torch.cuda.synchronize()`，或用启用 timing 的 CUDA Event，并在读取 `elapsed_time` 前等待 event 完成。[3]

```python
def timed_gpu_stage(fn, *args):
    # Warmup is performed outside this function; events measure GPU stream work.
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    out = fn(*args)
    end.record()
    torch.cuda.synchronize()  # Benchmark only: wait until recorded work completes.
    return out, start.elapsed_time(end)
```

实现注意：

1. CUDA Event 测 GPU stream 段，不能包含 client upload、server queue 或 controller apply。
2. CPU→GPU/GPU→CPU copy 是否计入，要显式规定；`.cpu()`/`.numpy()` 可能引入隐式同步。
3. 不要为每个线上请求无条件全局 synchronize；可在 benchmark run 同步，线上 sampled tracing。
4. model load、CUDA context、compile/cache、worker/T5 init 属于 cold-start，必须与 steady-state 分开。
5. 单次打印没有 percentile；至少报 p50/p95/p99/max 和 timeout/error/cancel/fallback rate。

## 6. 同步与异步的 deadline 不一样

### 6.1 同步 stop-and-plan

若机器人规划时暂停或保持安全动作：

\[
L_{plan}^{p99}+M\le L_{pause,max}.
\]

变量解释：\(M\) 是 scheduling/network/controller margin，\(L_{pause,max}\) 由任务稳定性与安全分析给出。此时不必假装规划已与执行 overlap；pause 时长本身要进入 episode trace 和失败归因。

### 6.2 异步 overlap

当前长度 K 的 action prefix 执行时生成下一 chunk：

\[
L_{plan}^{p99}+M\le\frac{K}{f_{ctrl}}.
\]

变量解释：\(K/f_{ctrl}\) 是 action buffer 可覆盖的物理时间。若不满足，会 queue underrun、停顿、重复旧动作或触发 fallback。公式是 deadline gate，不保证策略质量。

### 6.3 Action freshness

\[
A_j=t_{apply,j}-t_{obs},
\qquad
execute(a_j)\iff A_j\le TTL\land version(a_j)=version_{active}.
\]

变量解释：\(A_j\) 是 action age；TTL 按任务/阶段冻结；version 防止旧 request 晚到覆盖新计划。需要记录 late-result drop、cancel latency、queue underrun 与 watchdog reason。[5][6]

## 7. Timeout 不等于安全处理

timeout 只是“等多久”，还必须定义：

| 事件 | 必须冻结的行为 | 必须记录 |
| --- | --- | --- |
| admission overload | bounded queue / reject / degrade | queue depth、reject reason |
| candidate partial | 最低 candidate 数、是否允许 degraded selection | expected/returned IDs、missing reason |
| deadline miss | cancel late work，禁止覆盖新 version | deadline、cancel ack、late drop |
| GPU OOM/crash | direct policy / hot standby / hold / safe stop | backend error、fallback revision |
| disconnect | stop work或完成但丢弃，controller 独立 watchdog | disconnect/cancel/leaked task |
| stale action | TTL/version gate 拒绝 | action age、obs/action IDs |
| controller reject | 不把 server success 当执行成功 | schema/range/safety reject reason |

“继续执行上一动作”不能作为通用 fallback：在抓取接触、末端高速运动或动态目标场景中可能扩大风险。fallback 必须按任务安全语义选择并演练。[5]

## 8. N–latency–success 怎样做 matched comparison

需要两个不同 sweep：

### 8.1 Algorithmic N sweep

先为每个 frozen observation/episode 生成最大 candidate pool，例如 Nmax=8，然后比较相同 seed 顺序的 prefix N=1/2/4/8。固定 proposal/world/value checkpoint、selector、denoise、task/init 与 controller，记录 selected regret、success、failure stage。这样减少“不同 N 恰好抽了不同候选”的混淆。

### 8.2 System P sweep

固定 N，再扫 serial/parallel、P、batch 与 response payload，记录 stage/e2e p50/p95/p99、GPU-hours、peak memory、queue、timeout/fallback。N 是算法搜索量，P 是资源并行度，不能只报告其中一个。

### 8.3 最小结果表

| N | P | Ew/Ev/D | steps a/w/v | K/Hz | p50/p95/p99 e2e | timeout/fallback | success + CI | first failure |
| ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | frozen | frozen | frozen | measured | measured | matched episodes | labeled |
| 4 | 1/4 | frozen | frozen | frozen | measured | measured | matched episodes | labeled |
| 8 | 1/8 | frozen | frozen | frozen | measured | measured | matched episodes | labeled |

还应扫 action/world/value denoise、Ew/Ev/depth，并画 quality–latency–resource Pareto frontier。不能只挑最高 success 或最快 latency 的一个点。

## 9. 可审计 planning loop

```python
def deadline_aware_planning(obs, cfg, planner, controller, trace):
    # 1. Create a versioned request from the sensor timestamp.
    req = trace.new_request(obs.timestamp, obs.version, cfg.deadline_ms)
    if not bounded_admission(req, cfg.max_queue):
        return fallback("queue_reject")

    # 2. Preserve candidate IDs through proposal, world rollout and value scoring.
    actions = planner.propose(obs, n=cfg.N, trace_cuda=True)
    futures = planner.rollout(actions, ensemble=cfg.Ew, trace_cuda=True)
    values = planner.score(futures, ensemble=cfg.Ev, trace_cuda=True)

    # 3. Check completeness and freshness before selecting anything.
    if req.expired() or obs.version != controller.active_observation_version:
        planner.cancel(req)
        return fallback("stale_or_timeout")
    if len(values) < cfg.min_candidates:
        return fallback("partial_candidates")

    # 4. Selector output is not execution evidence until controller apply is logged.
    selected = select(values)
    action_id = controller.enqueue(selected.actions, request_id=req.id)
    trace.wait_or_sample_controller_apply(req.id, action_id)
    return selected
```

关键不是代码形状，而是：candidate completeness、freshness gate、cancel/fallback 与 controller apply 都有统一 ID 和时间戳。它是待补 instrumentation 设计，不是 WAM 已运行实现。

## 10. 常见症状与 first-failure

| 症状 | 先查 | 对照 |
| --- | --- | --- |
| N 增大平均 latency 不多，p99 暴涨 | straggler、queue wave、IPC、partial timeout | N/P matrix、per-branch timeline |
| GPU stage 快，client 仍慢 | image JSON/payload、upload/response、serialization | bytes、RTT、server recv/send timestamps |
| planning 返回及时但机器人停顿 | action queue/controller apply、sync execution | server return→enqueue→apply |
| async 偶发倒退 | stale result 覆盖、版本/取消失效 | obs/action version、late-drop log |
| success 随 N 下降 | OOD value/optimizer's curse | fixed candidate random/mean/LCB/oracle audit |
| timeout 后仍有 GPU 负载 | cancellation 未传播、leaked task | cancel ack、active task registry |

## 11. 项目与真实性边界

当前 WAM evidence 没有 candidate/world/value request bundle、N/P/Ew/Ev/D sweep、network/IPC trace、action-age/controller apply、fallback drill 或 matched success-latency curve。因此安全口述是：

**“我能基于 frozen Cosmos path 设计端到端 planning telemetry 与 deadline/freshness/fallback 合同；真正升级为项目结果前，还需要本地 request trace、candidate ledger、matched episodes 和 ownership 证据。”**

不能说：**“我已经把 WAM best-of-N 做到 4.9 s 或实时，并提升成功率。”**4.9 s 是 Cosmos 论文在 8×H100、指定 N/world/value recipe 下的公开结果。[1][7]

`bigtech-interview-project-upgrader` 的证据契约在这里要求降级：公开代码机制最多支持 C0“理解/能审计”；没有个人 code diff、run trace、指标口径与 ownership，不能升级到 C1/C2/C3。

## 12. 一句话收束与下一入口

**Planning latency 是 observation-to-controller 的 critical path，不是一次 forward；N、world/value ensemble、depth 决定 work，P/queue/IPC 决定 wall-clock，CUDA timing 保证测得准，deadline/TTL/version/fallback 保证晚到结果不伤害系统，matched N–P–success sweep 才能回答是否值得部署。**

下一节点是 `VLA-WM-031`：Sim2Real reality gap 的视觉、动力学、控制、任务与随机性分层。本节点保持 WARN，题卡在真实口述前保持 unseen。

## 参考文献（References）

1. NVlabs, [Cosmos Policy](https://arxiv.org/html/2601.16163v1), 2026。
2. NVlabs, [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)。
3. PyTorch 2.13, [CUDA semantics: Asynchronous execution](https://docs.pytorch.org/docs/2.13/notes/cuda.html#asynchronous-execution) 与 [`torch.cuda.Event`](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.Event.html)。
4. NVIDIA Triton, [Perf Analyzer: Measurements and Metrics](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/measurements_metrics.html)。
5. [ENG-022 Policy Server Resilience](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)。
6. [WM-023 Open-loop / Receding Horizon](vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.html)。
7. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
