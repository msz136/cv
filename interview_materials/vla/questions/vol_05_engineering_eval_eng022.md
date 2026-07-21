# VOL 05 Engineering / Evaluation：ENG-022 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-022`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-022 Policy Server Resilience](../knowledge/vol_05_engineering_eval_eng022.html)；来源边界见 [Source Freeze](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)。当前 OpenPI 只有逐请求 WebSocket infer/timing/error baseline，OpenPiVLA 有 offline timeout reports，Robot Harness 有 tool-side timeout/cancel/compensation；不能声称 policy-server batching、SLO、safe fallback 或多机器人 fairness 已闭环。

## Policy Server Batching、Backpressure、Timeout 与 Fallback

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ENG-022</b> · 多机器人 VLA policy server 如何设计 batching、backpressure、timeout 和安全 fallback？</summary>

**面试意图**：判断你能否把吞吐、队列、deadline、action freshness、取消传播、controller side effect 和 fallback 组织成可测的服务合同，而不是只说“加 batch/重试”。

**30 秒回答**：bounded queue 后按 shape/deadline 合批；deadline 传播到 queue/infer/controller，超时取消副作用。校验 action age/schema，fallback 绑定 TTL、已验证 bundle 和 watchdog；OpenPI 只有逐请求 infer baseline。

**机制展开（约 2 分钟）**：按 Qmax、batch key、max queue delay、deadline 和 action-age admission；队列满拒绝或安全 hold，不执行 stale chunk。T_total 拆 queue/batch/infer/post/controller，timeout 取消 task、send、lock；输出先做 H/D/axis/unit/NaN gate，再选 TTL 内 known-good fallback。OpenPiVLA 只有 connect/infer timeout reports，Harness 只有 tool timeout/cancel，不能称 policy-server SLO。

**诊断 / 证据**：记录 request/robot/priority/idempotency、enqueue/dequeue、batch id/size、queue/infer/total p50/p95/p99、deadline miss、action age、cancel latency、leaked task、fallback reason/TTL/recovery、controller/watchdog result。做 burst overload、稀疏/高峰 batch、shape conflict、queue/infer timeout、disconnect、malformed action、GPU kill、retry storm 和 recovery drill；验证 bounded memory、无 stale action、无重复 side effect、fallback bundle compatibility 与旧请求不复活。

**项目挂钩**：OpenPiVLA `eval_lerobot_action_server.py` 有 connect/infer timeout，并输出 `server_unavailable`/`infer_failed`；deployment 使用 official WebSocket client/server 和 checkpoint path。Robot Harness registry/runtime 有 polling timeout、cancel context、robot lock cleanup、best-effort compensation 和 scope filtering。它们分别是 offline eval failure hook 与 tool-side effect control，不是统一 VLA inference scheduler。

**追问树**：为什么无界 queue 会让 p99 和 action age 爆炸？`max_batch_size` 为什么不等于请求可合批？deadline 如何跨 queue/infer/controller 传播？`wait_for` timeout 后怎样证明没有 leaked task？last-safe action 何时危险？fallback 如何绑定 ENG-021 bundle？如何测 retry storm/disconnect/worker failure？OpenPI server 当前证据支持什么、不支持什么？

**易错点**：只看 GPU throughput；不同 H/D/camera/frame 请求 silent reshape；timeout 返回但 GPU/send 仍继续；无限复用旧 action；用未验证 checkpoint 做 fallback；断连后继续发 action；caller/server 双重 retry；把逐请求 WebSocket 写成生产级 dynamic batching。

**危险答案**：说“队列越长吞吐越高”“timeout 就重试”“last action 永远安全”“fallback 小模型就行”“有 WebSocket 就支持多机器人 batching”或“Robot Harness 的 tool timeout 证明 policy server SLO”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-022 知识页](../knowledge/vol_05_engineering_eval_eng022.html)：bounded queue、batch/freshness、deadline/cancel、fallback、验证矩阵与项目边界。
2. [ENG-022 Source Freeze](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)：CPython/Triton/OpenPI pinned source 与本地 timeout/cancel evidence。
3. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：official WebSocket client/server、timeout reports、checkpoint/path 与 offline eval 边界。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：tool polling/cancel/compensation/lock/scope 的局部证据。

