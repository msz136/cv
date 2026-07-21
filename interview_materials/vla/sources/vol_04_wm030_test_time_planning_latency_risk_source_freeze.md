# VOL 04 WM-030 Source Freeze：Test-time Planning Latency、Communication 与 Risk Contract

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-030 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-030  
> 本轮边界：冻结 test-time planning 的 action proposal、world rollout、value scoring、selector、N/ensemble/search-depth 开销，端到端计时方法和 deadline/freshness/fallback 合同；不把上游指定硬件 wall-clock 外推到本机或用户 WAM，也不声称当前项目已完成 planning latency 优化。

## 1. 结论先行

1. **先拆 stage，再谈“planning latency”。**最小 critical path 是 observation capture/serialize/upload → admission/queue/preprocess → action proposal → world rollout → value scoring → selector → response/download → action queue/controller apply；只计 GPU forward 会漏掉通信、排队、序列化和 stale action。[S2][S5]
2. **N 增大既不是纯线性成本，也不是免费并行。**串行时近似累加 N 个 branch；N 个 GPU 并行时 wall-clock 更接近最慢 branch 加 IPC/queue/collect，但 compute、显存、payload 和 tail latency 仍增长。必须同时报告 N、并行度 P、world/value ensemble、denoising steps、search depth 和 batch policy。[S1][S2]
3. **CUDA 计时必须处理异步执行。**PyTorch 官方说明 GPU operation 默认异步，未同步的 CPU wall-clock 不准确；kernel 段用 CUDA Event 或显式 synchronize，端到端段用 monotonic wall-clock，并分别报告 warmup/cold-start 与 p50/p95/p99。[S3]
4. **deadline 取决于执行架构。**同步 stop-and-plan 检查最大允许 pause；异步 overlap 检查 \(L_{plan}+M\le K/f_{ctrl}\)；两者都要检查 observation/action age、TTL、queue underrun、late-result cancellation 和 watchdog，不能只用平均 latency。[S6]
5. **Frozen Cosmos 给出的是特定 recipe。**论文报告 direct joint generation 在单 H100 上 5-step 为 0.61 s、1-step 为 0.16 s，ALOHA 10-step 为 0.95 s；真实机器人 best-of-N 使用 N=8、8 张 H100、action 10-step、3 个 world samples×5-step、每个 future 5 个 value samples×5-step，总计 4.9 s。它们是指定硬件/实现的 action-chunk wall-clock，不是通用 VLA SLA。[S1]
6. **Frozen code 的 telemetry 仍不完整。**代码用 `time.time()` 分段打印 action/future/value 和 parallel total，`parallel_timeout=15`，默认 `search_depth=1`；但没有统一 request id 下的 upload/queue/IPC/selector/download/controller-apply 时间戳，也没有 CUDA Event、warmup 或 percentile ledger。[S2]
7. **WAM 本地没有 planning runtime 证据。**当前缺 candidate/future/value ledger、N/P/depth sweep、network trace、action freshness、controller apply、fallback 和 matched success-latency curve，不能说已经实现或优化 Cosmos planning。[S7]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | *Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning* | arXiv:2601.16163v1；HTML 访问 2026-07-18；UTF-8 SHA-256 `02ca817937f4b62a96873dc2702574d6e1c4a66715f8cedec24fd5cf42f4fc70` | direct/action-chunk wall-clock、1/5/10 denoise、真实机器人 N=8/3 world/5 value/4.9 s、指定 H100 语境与动态任务限制 | 本机 latency、网络/队列分解、任意任务 SLA、WAM 本地复现 | primary / checked |
| S2 | NVlabs/cosmos-policy | commit `18a2accadf4e7a3531e56754102af5a24d2316da` | serial/parallel best-of-N、worker queue、timeout、stage prints、FastAPI `/act`、selector、默认 N/depth/ensemble/open-loop fields | 打印即完整 trace；timeout 后一定安全 fallback；上游代码等于个人实现 | official-code / WARN |
| S3 | PyTorch CUDA semantics | PyTorch 2.13 docs；访问 2026-07-18 | CUDA 默认异步；未同步 CPU timing 不准确；`torch.cuda.synchronize()` 与 CUDA Event/`elapsed_time` 方法 | 某模型真实 kernel latency 或端到端 SLA | official-doc / checked |
| S4 | NVIDIA Triton Perf Analyzer measurements | rolling docs；访问 2026-07-18；UTF-8 SHA-256 `0c24a82a70b5993bfd6be59ac899c4d285c2b57c60a62d8c666a528fed0b734e` | client latency、send/receive/response wait、server queue/compute/overhead、p50/p90/p95/p99 与 throughput-latency 分解范式 | 当前服务使用 Triton；其字段已被 WAM/Cosmos 采集 | official-doc / checked |
| S5 | VOL 05 ENG-022 Policy Server Resilience | 本地 canonical + review；2026-07-18 | bounded queue、backpressure、deadline/cancel、action freshness、watchdog/fallback 的 serving 合同 | 当前项目已实现 resilience 或达到 p99 | supporting / WARN |
| S6 | WM-023 Open-loop / Receding Horizon 与 WM-029 OOD Value | 本地 canonical + review；2026-07-18 | H/K/action-age 时间轴、同步/异步合同、best-of-N selector risk | 某 K/N/β 对 WAM 已最优 | supporting / WARN |
| S7 | WAM Claim–Evidence Inventory | 2026-07-18 | local checkpoint/protocol/ownership 与 planning artifact 缺口 | local planning latency、success uplift 或线上部署 | local-evidence / WARN |

### 2.1 Frozen Cosmos files

| 文件 | 关键作用 | SHA-256 |
| --- | --- | --- |
| `cosmos_policy/experiments/robot/cosmos_utils.py` | action/world/value generation、same-model ensembles、worker pool、IPC queue、timeout | `ebe56d63d88f9a4d4ad6706d9a9ecd1376a1dff1b5cbb010c8fcd8f0c2ee0b1d` |
| `cosmos_policy/experiments/robot/libero/run_libero_eval.py` | LIBERO N/open-loop/serial-parallel path、stage logging、selector 与 env step | `2c00207579749d935102276081858a790ad413a7a64c5b838cb8f4d5d508c9a7` |
| `cosmos_policy/experiments/robot/robocasa/run_robocasa_eval.py` | RoboCasa defaults 与 planning loop | `8e92cddfc72a23b95abe8c2b99fce93a1c382cf46ea0e97d87a8805c06360f4b` |
| `cosmos_policy/experiments/robot/aloha/deploy.py` | FastAPI `/act`、serial/parallel N、selector、optional all-results response | `e4592f5ac26a41d5d550190ea7cd9531029ac329955be8409d2f60d54824914e` |

## 3. Planning critical path

```text
camera/state capture (t_obs)
  → encode / serialize / upload
  → admission / server queue / preprocess
  → N action proposals
  → per proposal: E_w world samples
  → per future: E_v value samples
  → depth aggregation + best-of-N selector
  → serialize / download
  → action queue / controller apply (t_apply)
```

端到端 observation-to-actuation latency 定义为：

\[
L_{e2e}=t_{apply}-t_{obs}.
\]

变量解释：\(t_{obs}\) 是传感器样本时间而非 client 发包时间，\(t_{apply}\) 是 controller 真正接收/应用动作而非 server 返回时间。实现必须使用 `request_id + observation_version + monotonic timestamp` 串起各 stage；跨主机单向分解需要时钟同步或用 RTT/服务端时间间接估计。

可审计分解为：

\[
L_{e2e}=L_{capture}+L_{encode}+L_{up}+L_{queue}+L_{pre}
+L_{plan}+L_{select}+L_{down}+L_{ctrl}.
\]

变量解释：`plan` 是模型搜索，`select` 是 depth/value 聚合与候选选择，`ctrl` 含 action queue 到 apply；这些项可能 overlap，所以逐项和只在同一 critical path、相同 timestamp 语义下成立。Triton 的 queue/compute/send-receive 分解只作为 instrumentation 范式，不表示 Cosmos 使用 Triton。[S4]

## 4. N、world/value ensemble、depth 的计算模型

令 \(N\) 为 action proposals，\(E_w\) 为每个 proposal 的 world samples，\(E_v\) 为每个 future 的 value samples，\(D\) 为 search depth，\(P\) 为并行 worker/GPU 数。depth=1、autoregressive stage 的粗略 work 为：

\[
W_{plan}\approx N\left(C_a+E_w C_w+E_wE_v C_v\right).
\]

变量解释：\(C_a,C_w,C_v\) 分别是一次 action、world、value generation 的成本；denoising steps、输入长度、图像数、dtype/backend 和 batch 决定每项实际值。公式只表示调用数级别，不假设 kernel cost 严格线性。[S1][S2]

串行 wall-clock 近似：

\[
L_{plan}^{serial}\approx
\sum_{i=1}^{N}L_i+L_{select}.
\]

并行 wall-clock 近似：

\[
L_{plan}^{parallel}\approx
L_{dispatch}+\max_{i\le N}L_i+L_{collect}+L_{select},
\qquad P\ge N.
\]

变量解释：并行由最慢 branch 决定，并额外支付 process start/warmup、observation 复制、IPC serialization、queue wait、result copy 和 straggler 成本；若 \(P<N\)，还要分 wave，不能把 N GPU 结果外推到单 GPU。search depth >1 时，后续 action→world→value 会递归增加 work，且 branch factor 取决于 world samples；frozen defaults 为 depth=1。[S2]

## 5. Frozen Cosmos exact behavior

### 5.1 论文 recipe

- direct policy 同一次生成 action/future/value：单 H100，5 denoise 为 0.61 s，1 denoise 为 0.16 s；ALOHA 10 denoise 为 0.95 s。论文明确这些是生成一个 action chunk 的 wall-clock，并举例 ALOHA 会暂停 0.95 s 后执行 2 s chunk。[S1]
- model-based planning 真实机器人 recipe：N=8，8 张并行 H100；每个 action proposal 10 denoise；每个 proposal 3 个 future，每个 5 denoise；每个 future 5 个 value，每个 5 denoise；总 search 4.9 s。[S1]
- 论文同时把约 5 s planning latency 视为 dynamic manipulation/locomotion 的限制；不能把“任务能跑”解释成满足实时性或安全 SLA。

### 5.2 代码路径

- `WorkerPoolManager` 为每个 GPU 建 `multiprocessing.Queue`，把 observation/task 分发给 query，等待 `num_queries_best_of_n` 个结果直到 `parallel_timeout`；默认 timeout 15 s，worker 初始化 timeout 600 s。[S2]
- worker 内分别用 `time.time()` 围住 action、future、value 调用；parallel caller 只记录整批完成时间。代码没有显式 CUDA Event/synchronize，因此这些日志受异步 kernel、隐式 CPU copy/sync 和 Python/IPC 边界共同影响，不能当 kernel-only profile。[S2][S3]
- LIBERO/RoboCasa 默认 N=1、parallel off、depth=1、world ensemble off、value ensemble off；公开支持不等于默认启用。
- ALOHA deploy 暴露 FastAPI `/act`；request 可携带多路图像、proprio 与 task，response 默认返回 selected actions/future/value。若 `return_all_query_results=True`，还会返回所有 action、future/value/depth 结果，通信与 JSON serialization 可能显著放大，必须单独测 payload bytes 和 latency。[S2]
- selector 在已有结果中取最大 value。timeout/worker error 的 returned-result count、missing candidate IDs、fallback reason 与 stale request 需要显式落盘；不能只记录 selected seed。

## 6. 正确计时合同

### 6.1 两种 clock，两类问题

| 区间 | 推荐时钟 | 必须处理 | 输出 |
| --- | --- | --- | --- |
| GPU kernel / stage | CUDA Event；必要时 `torch.cuda.synchronize()` | async stream、warmup、host-device copy 边界 | 每 stage ms、p50/p95/p99 |
| process/client/server/controller wall-clock | monotonic `perf_counter_ns` 类时钟 | request id、clock domain、serialization、queue、RTT | e2e/action age/queue/RTT |

PyTorch 官方明确指出 GPU operation 默认异步，未同步的 CPU timing 不准确；`Event.elapsed_time` 返回 event 间毫秒。不要在每个生产 request 中无条件全局 synchronize 破坏并发，benchmark/profile run 可同步，线上可用 event/trace sampled instrumentation。[S3]

### 6.2 统计协议

1. 固定 model/checkpoint、processor、normalizer、dtype/backend、image shape/count、N/P/\(E_w\)/\(E_v\)/D、denoise、batch、K/frequency。
2. cold-start 单独报告 model load、CUDA context、compile/cache/T5 init；steady-state 先 warmup，再采足够 request。
3. 记录 p50/p95/p99/max、timeout/cancel/error/fallback rate、queue depth、payload bytes、GPU utilization/memory，而非只报 mean/FPS。
4. client RTT、server queue、preprocess、GPU service、selector、serialization、controller apply 分开；server compute 不能从 client RTT 直接相减，除非 timestamp/clock contract成立。
5. 每条 episode 绑定 request/observation/action IDs，保留 selected/unselected candidate latency 与 outcome，防止只看成功候选。

## 7. Deadline、freshness 与 failure policy

### 7.1 同步 stop-and-plan

机器人在规划时停止或保持安全动作，约束是：

\[
L_{plan}^{p99}+M\le L_{pause,max}.
\]

变量解释：\(M\) 是 scheduling/network/controller margin，\(L_{pause,max}\) 由任务稳定性、负载/接触保持与安全分析给出。它不要求必然小于 chunk execution time，但 pause 本身必须进入成功和安全评估。

### 7.2 异步 overlap

当前 chunk 执行时准备下一 chunk，避免 queue underflow 的必要工程 gate 为：

\[
L_{plan}^{p99}+M\le \frac{K}{f_{ctrl}}.
\]

变量解释：\(K/f_{ctrl}\) 是当前可用 action prefix 的物理时长；若 deadline miss，不能静默等待或执行任意 stale chunk，必须执行已冻结的 fallback。

### 7.3 Freshness gate

对第 j 个动作：

\[
A_j=t_{apply,j}-t_{obs},
\qquad
execute(a_j)\iff A_j\le TTL\land version(a_j)=version_{active}.
\]

变量解释：`TTL` 是按任务/阶段冻结的最大 action age，version 防止旧 request 晚到覆盖新 plan。还要记录 cancel acknowledged time、late-result drop、queue underrun、watchdog trip 与 terminal/safety reason。[S5][S6]

### 7.4 限险状态机

```text
admit request only if queue/deadline budget permits
  → plan with candidate-completeness contract
  → if complete and fresh: select + enqueue
  → if partial: accept only when min_candidates and policy allow; mark degraded
  → if timeout/error/stale: cancel late work
  → fallback: direct policy / last safe short prefix / hold / safe stop
  → watchdog logs reason and recovery
```

具体 fallback 必须由机器人/任务安全评审决定；“重复上一动作”在接触和移动目标任务中可能危险，不能作为通用默认值。

## 8. Matched N–latency–success evaluation

最小实验分两层：

| 层 | 固定 | 扫描 | 记录 |
| --- | --- | --- | --- |
| algorithmic N | 同一最大 candidate pool、proposal seeds、world/value checkpoint、selector、episode/init | prefix N=1/2/4/8；必要时 oracle/random | rank/selected regret、success、failure stage；避免不同 N 采到不同候选造成混淆 |
| system scaling | checkpoint/data/protocol/N | P、serial/parallel/batch、payload mode | p50/p95/p99 stage/e2e、GPU-hours、memory、queue、timeout/fallback |
| denoise/ensemble/depth | candidate identity 与 episode | action/world/value steps，\(E_w/E_v/D\) | quality-latency frontier、OOD/error、deadline miss |
| control | task/init/controller/success predicate | K/frequency、sync/async、latency injection | action age、pause、underrun、recovery、safety event |

比较时至少报告 \((N,P,E_w,E_v,D,s_a,s_w,s_v,K,f_{ctrl})\) 与 hardware/software revision。只画 success–N 而不画 latency/resource，或只画 latency 而不固定 candidate/episode，都不能支持部署取舍。

## 9. 可审计伪代码

```python
def plan_with_deadline(obs, cfg, planner, controller, trace):
    # 1. Bind sensor time, request identity and freshness deadline.
    req = new_request(obs.timestamp, obs.version, deadline=cfg.deadline)
    trace.mark(req, "client_encode_start")

    # 2. Record admission/queue/preprocess separately from GPU stages.
    admitted = bounded_admission(req, max_queue=cfg.max_queue)
    if not admitted:
        return safe_fallback("queue_reject")

    # 3. Use CUDA events for GPU stages; keep candidate IDs through N/world/value.
    candidates = planner.propose(req, n=cfg.N, trace_cuda=True)
    futures = planner.rollout(candidates, ensemble=cfg.Ew, trace_cuda=True)
    scores = planner.score(futures, ensemble=cfg.Ev, trace_cuda=True)

    # 4. Drop late/stale results before selection; partial results require policy.
    if expired(req) or obs.version != controller.active_observation_version:
        cancel_late_work(req)
        return safe_fallback("stale_or_timeout")
    if len(scores) < cfg.min_candidates:
        return safe_fallback("insufficient_candidates")

    selected = select(scores)
    action = controller.enqueue(selected.actions, request=req)
    trace.mark(req, "controller_apply", action_id=action.id)
    return action
```

这是 instrumentation/failure-policy 设计，不是 WAM 已执行代码。真实实现还需处理 clock sync、process crash、GPU OOM、client disconnect、controller reject 与 safety supervisor。

## 10. WAM 真实性边界

当前 WAM inventory 可支持训练/评估材料的局部诊断，但没有 request-level planning trace、candidate/world/value bundle、N/P/ensemble/depth sweep、network payload/RTT、controller apply、action-age、deadline/fallback 或 matched closed-loop episodes。[S7]

安全说法：**“我会先把 action/world/value/selector 与通信/队列/controller apply 放到同一 request trace，再分别做 algorithmic N 和 system P sweep，用 p99 deadline、action freshness 和 fallback rate 约束 success–latency frontier。”**

不能说：**“我已经把 WAM best-of-N 并行化到 4.9 秒/实时，并证明 planning 提升成功率。”**4.9 s 是 Cosmos 论文的指定 8×H100 recipe，不是个人结果。

## 11. 下一入口

下一 bounded slice 是 `VLA-WM-031`：Sim2Real reality gap 的视觉、动力学、控制、任务与随机性分层。本页不提前扩写 domain randomization 或 system identification。

## 参考文献（References）

1. NVlabs, [Cosmos Policy](https://arxiv.org/html/2601.16163v1), 2026。
2. NVlabs, [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)，重点 [`cosmos_utils.py`](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/cosmos_utils.py) 与 [`aloha/deploy.py`](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/aloha/deploy.py)。
3. PyTorch 2.13, [CUDA semantics: Asynchronous execution](https://docs.pytorch.org/docs/2.13/notes/cuda.html#asynchronous-execution)、[`torch.cuda.Event`](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.Event.html)、[`torch.cuda.synchronize`](https://docs.pytorch.org/docs/2.13/generated/torch.cuda.synchronize.html)。
4. NVIDIA Triton, [Perf Analyzer: Measurements and Metrics](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/measurements_metrics.html)。
5. [ENG-022 Policy Server Resilience](vol_05_eng022_policy_server_resilience_source_freeze.html)。
6. [WM-023 Open-loop / Receding Horizon](vol_04_wm023_open_loop_receding_horizon_source_freeze.html)。
7. [WM-029 Imagined/OOD Value Calibration](vol_04_wm029_imagined_ood_value_calibration_pessimism_source_freeze.html)。
8. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
