# VOL 04 VLA-WM-030 原子题卡：Test-time Planning Latency、Communication 与 Risk Contract

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-030  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-030 Knowledge](../knowledge/vol_04_world_model_sim2real_wm030_test_time_planning_latency_risk.html)；来源边界见 [WM-030 Source Freeze](../sources/vol_04_wm030_test_time_planning_latency_risk_source_freeze.html)。

## test-time planning 增加的 N、world rollout、value scoring 与通信开销怎样计时和限险？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-030</b> · test-time planning 增加的 N、world rollout、value scoring 与通信开销怎样计时和限险？</summary>

**面试意图**：判断你能否把算法搜索量、硬件并行、CUDA timing、网络/队列、action freshness 与安全 fallback 放进同一部署合同，而不是只报 forward time 或平均 FPS。

**30 秒回答**：按 obs→上传/排队→action/world/value→selector→controller apply 计 e2e；GPU 用 CUDA Event，报 p50/p95/p99。同步限 pause，异步要求 p99+余量≤K/fctrl。超时/不全/stale 按 TTL/version 丢弃并 fallback；同候选做 N–P–成功率曲线。

**机制展开（约 2 分钟）**：depth=1 的 work 约为 N(Ca+EwCw+EwEvCv)；串行累加，P≥N 并行由最慢 branch 加 dispatch/IPC/collect 决定，总算力并未免费。trace 要含 sensor、queue、CUDA stage、selector、response、enqueue/apply 时间戳与 bytes。CUDA 默认异步，未同步 CPU timing 不可靠。分 cold/steady，报 tail、timeout/cancel/fallback。sync 检查最大 pause；async 检查 p99+margin≤K/fctrl，并用 action age、TTL、version、watchdog 拒绝晚到计划。

**诊断 / 证据**：固定 checkpoint、processor/normalizer、图像形状、N/P/Ew/Ev/depth、action/world/value denoise、K/Hz、task/init/controller/success predicate。先用同一 Nmax candidate pool 的 seed prefix 比 N=1/2/4/8，再固定 N 扫 P/serial/parallel/payload；保存 returned/missing candidate IDs、per-branch/stage latency、queue depth、request/response bytes、action age、deadline miss、first-failure 与 success CI。

**项目挂钩**：Cosmos 论文的 4.9 s 是 N=8、8×H100、10-step action、3×5-step world、每 future 5×5-step value 的指定 recipe；代码默认 depth=1、`parallel_timeout=15s`，但没有统一 controller-apply trace。WAM 本地无 candidate/runtime/network/fallback bundle，安全说“能设计审计合同”，不能说“已做到实时或复现 4.9 s”。

**追问树**：N 和 P 有什么区别？为什么并行由最慢 branch 决定？Ew/Ev/depth 怎样放大 work？`time.time()` 为什么可能错？CUDA Event 与 e2e clock 各测什么？RTT 如何和 server queue 分离？sync/async deadline 分别是什么？partial candidates 能否选？stale action 如何发现？timeout 后怎样 cancel？为何 success–N 要固定 candidate prefix？4.9 s 能否外推到本机？

**易错点**：把 N GPU wall-clock 当单 GPU；只报 mean/FPS；每次线上请求全局 synchronize；把 server return 当 controller apply；忽略 payload/IPC/queue；timeout 后仍接受旧结果；partial result 不记 missing IDs；同步 pause 与异步 deadline 混用；调 N 时同时改变 seeds/denoise/episode；把指定 H100 数字写成个人指标。

**危险答案**：说“N 越大只增显存不增延迟”“多 GPU 完全消除 planning 开销”“`time.time()` 足够测 CUDA”“15 秒 timeout 就安全”“返回 action 就代表执行”“重复上一动作永远是安全 fallback”“Cosmos 4.9 秒等于 WAM/本机实时部署结果”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-030 Source Freeze](../sources/vol_04_wm030_test_time_planning_latency_risk_source_freeze.html)：critical path、N/P/ensemble/depth、CUDA timing、deadline/freshness/fallback 与项目边界。
2. NVlabs, [Cosmos Policy](https://arxiv.org/html/2601.16163v1) 与 [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)。
3. PyTorch 2.13, [CUDA asynchronous execution](https://docs.pytorch.org/docs/2.13/notes/cuda.html#asynchronous-execution)。
4. NVIDIA Triton, [Perf Analyzer Measurements](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/perf_analyzer/docs/measurements_metrics.html)。
5. [ENG-022 Policy Server Resilience](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html) 与 [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
