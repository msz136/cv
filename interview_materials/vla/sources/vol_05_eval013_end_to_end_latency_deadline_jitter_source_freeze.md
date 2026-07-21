# VOL 05 EVAL-013 Source Freeze：端到端 Latency、Deadline Miss 与 Jitter

> 状态：`source_frozen / VLA-EVAL-013 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结 timestamp boundary、clock contract、critical path、p50/p95/p99、deadline miss、control jitter、action age、warm/cold/load stratification、coordinated omission 与可复算 trace；只生成一张 `VLA-EVAL-013` 原子题卡，VOL 05 同步为 knowledge/cards 35/44。

## 问题（Question）

怎样证明一个 VLA policy loop 满足实时性要求？“模型推理 20 ms”“平均 latency 很低”“控制频率设成 20 Hz”都不够。可信评估要从 observation capture 到 controller apply 建统一时间轴，拆出 queue/infer/transport/decode 等阶段，报告 tail、deadline miss、jitter、stale/drop 与负载条件，并把 action chunk 的后续动作年龄纳入闭环协议。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Dean & Barroso, *The Tail at Scale* | primary paper page；CACM 2013；论文许可未断言 | Google Research page `08b0ee41b61e513ba6b9514028a50e88bdc53116f60828762bbd4a557a096376` | 系统规模/利用率上升时 temporary high latency 会主导整体响应；tail-tolerant 设计动机 | VLA p99 阈值、机器人 deadline 或用户项目性能 |
| S2 | ROS 2 `demos/pendulum_control` | official-code；commit `54d49d22e898d796ea476c42268757ad422bf878`；Apache-2.0 | README `55cf38fb84378228c3f031f88985a2bc016b7524b2bf79c6fb0978a43d29c3ff`；LICENSE `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | periodic real-time demo 的 deadline-latency min/max/mean/std、page faults、priority/memory lock 与 latency spike 边界 | observation→action E2E latency；其示例数值是用户硬件 SLO |
| S3 | ROS 2 QoS design | official design；commit `93a415bf928751d37fce6f83215c521658e20c93`；Apache-2.0 | `qos.md` `e4c8f7a73abbc2b367017c3a2e5637a9ccd3a2914f68d9f8bc92ee46dfe11e41`；LICENSE `0e18850f8b379c340346bf727ac58d4d280cdfa6d0e91569e6640be996cdb76a` | queue depth、reliability、sensor data 更重及时最新样本而非必达的设计边界 | DDS 配置自动保证 VLA action freshness 或控制稳定 |
| S4 | HdrHistogram | official-code；commit `de84b0a7de2378abfc405da503bf4898e84ea98e`；CC0 / BSD-2-Clause 双许可 | README `d44cf3ffd7b4ca28e2fd4c619e5ac638a0935bbe2b38aba20b039eab7aac9d18`；LICENSE `ba550515c77c9e6f8b6a400381eacd3c47569297f8f27884801a95dff5309483` | 高动态范围 histogram、percentile 与 expected-interval correction；长响应导致少采样的 coordinated omission | 自动选择 VLA load model、SLO 或统计置信度 |
| S5 | RFC 3393, *IP Packet Delay Variation Metric for IP Performance Metrics* | standard；RFC 3393，2002-11；IETF copyright | text `bd9170bd9d9fe7fa6deda27198d90a067d300e4d755b0c2ab5c880016ec72f2c` | IP packet delay variation 的网络测量语义 | controller scheduling jitter、GPU jitter 或完整 action-age jitter |
| S6 | CPython `time` docs | official-code/doc；commit `2931f2067a6ecdc52cb44f694ce14ab8b50b9a32`；PSF-2.0 | `time.rst` `56404007fc70cdcd8441628bdd0d68eb6a29f721919600f4ad2658726ed95229` | `monotonic`、`perf_counter` / `_ns` 的 duration clock 入口与 resolution metadata | 跨主机 clock 已同步；GPU 异步工作已完成 |
| S7 | Physical Intelligence OpenPI serving | official-code；commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`；Apache-2.0 | server `1370d345e6c3c5b8f15573050e485e60a5b423d1df33e24b237805e6b442b026`；serve entry `eccc0448b4873fd30a1fff3355c5de7a7c227138e6db04b7dcaa5bb38a6a5809`；policy `a2ac5236e23b11d0f5a840d4a8fef148d89dba921d5452ec5dfcd5a6ffa46f20`；LICENSE `43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1` | `infer_ms` / policy timing、WebSocket request-response 与 transform boundary | capture→controller apply、p99 SLO、deadline/jitter 或用户项目实时性 |
| S8 | ENG-007 / ENG-022 / WM-034 / VOL 03 / EVAL-009/010 | canonical local prerequisites | ENG-007 volume `19965c8d0620255e794b6ffa2b6fb791a80bf36f61e9c7cb699972b8a9ebc547`；ENG-022 `9945c2a6d415a36105847c1c1cddf99b197dd670ea169b2d21cdfc5cdeeda656`；WM-034 `106fe97d60e78505ae71e7a8667499a615d71b2e1f0099c1da474713ecf940f8`；VOL 03 `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911` | loop budget、queue/deadline、multi-clock/action-age、GPU timing、raw bundle 与 release gate | 五项目已有 protocol-complete latency benchmark |
| S9 | 五项目 inventories + WAM manifest | local-evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d`；WAM manifest `1ab8709201e2e75f580cb0aa0f8465defb546d63b2aab70a1752239a7da8f697` | 当前 timing hook、timeout、DataLoader A/B 与缺口 | VLA action-age p99、deadline SLO 或真机实时闭环 |

S1解释为什么 tail 不能被平均值掩盖；S2测的是 periodic loop deadline lateness，不是 VLA E2E；S5只定义网络 packet delay variation，不等于 control jitter；S7只提供 serving stage timing。下面的统一 trace、统计和 gate 是 source-consistent engineering synthesis，不冒充任一来源的原始 schema。

## 2. 先冻结“Latency 从哪里到哪里”

同一次 policy query `i` 至少保存：

```text
episode_id, request_id, obs_version, chunk_id, checkpoint_sha,
t_sensor_capture, t_pre_start/end, t_enqueue/dequeue,
t_infer_start/end, t_serialize_end, t_response_receive,
t_decode_end, t_controller_accept, t_apply[j], t_next_sensor,
clock_id/host/resolution/offset_uncertainty,
queue_depth, batch_size, payload_bytes, H, K, f_control,
camera_count/resolution, token_or_NFE, dtype/backend/device,
deadline, timeout_stage, drop_reason, fallback, outcome
```

端到端 observation-to-actuation latency：

\[
L_i^{\mathrm{e2e}}=t_{i,0}^{\mathrm{apply}}-t_i^{\mathrm{capture}}.
\]

变量解释：`t_capture` 是生成该 request 的传感器采集时刻，`t_apply,0` 是第一条动作真正被 controller 接受/应用的时刻。直觉：它回答“机器人依据多旧的观测开始行动”。实现映射：不能用 request send、response receive 或 Python 函数 return 代替两端硬事件；保存 request/obs/chunk 关联和 clock uncertainty。

必须区分：

| metric | 起点→终点 | 回答 | 常见误用 |
| --- | --- | --- | --- |
| model compute | synchronized infer start→end | 模型/solver计算 | 说成控制频率 |
| server response | request send→response receive | queue+infer+transport | 忽略采集、decode、controller |
| first-action age | capture→first apply | 第一条动作新鲜度 | 忽略 chunk 后续动作 |
| per-offset action age | capture→apply[j] | chunk 第 j 条动作年龄 | 只报一次 infer latency |
| loop response | capture→apply→next effective sensor | 闭环状态何时可观测 | 说成网络 RTT |
| scheduler lateness | planned wakeup/deadline→actual wakeup | real-time loop调度 | 说成 VLA E2E |

## 3. Clock Contract

同主机 duration 使用 monotonic/performance counter；wall-clock 只用于日志对齐，不用于可能回拨的 duration。[S6] 每个 clock 保存 source、resolution、host/process、是否包含 suspend。跨主机需要 PTP/NTP/硬件 trigger 或离线 offset estimation，并保存 offset/skew uncertainty。

若起终点 clock offset uncertainty 为 `u_clock`，一个测得的 latency `L_obs` 只能解释为：

\[
L_i^{\mathrm{true}}\in
[L_i^{\mathrm{obs}}-u_{\mathrm{clock}},\;L_i^{\mathrm{obs}}+u_{\mathrm{clock}}].
\]

变量解释：`u_clock` 是同步误差上界或区间，不是运行 jitter。直觉：当要区分 2 ms 优化而 clock uncertainty 已有 5 ms 时，结论不可识别。实现映射：trace manifest 保存 sync method、offset sample、drift fit、同步前后 residual。

GPU kernel 默认异步；CPU wall-clock 包围 launch 可能只测到 enqueue。使用 device event 或显式 synchronization，并把 synchronization boundary、warm-up、compile/cache 状态写入 protocol。[S8]

## 4. Stage Decomposition 与 Critical Path

概念账本可写：

\[
L_{\mathrm{parts}}=
L_{\mathrm{sensor}}+L_{\mathrm{pre}}+L_{\mathrm{queue}}+
L_{\mathrm{infer}}+L_{\mathrm{serialize}}+L_{\mathrm{transport}}+
L_{\mathrm{decode}}+L_{\mathrm{controller}}.
\]

变量解释：每项必须有同一 request 的 start/end span。直觉：先定位 tail 出在哪一段。实现映射：异步 pipeline 会 overlap，真实 `L_e2e` 是 span DAG 的 critical path，不是各阶段平均数相加；同时输出 exclusive span、overlap 与 end-to-end trace。

每个阶段既要报自身 p50/p95/p99，也要报告其对 E2E tail case 的条件贡献：例如 `E[L_queue | L_e2e ≥ q99]`。否则“infer p99低”仍可能被 queue、camera 或 controller tail 主导。

## 5. Percentile 不是三个装饰数字

对 `n` 个同协议 latency，经验 CDF：

\[
\widehat F_n(x)=\frac{1}{n}\sum_{i=1}^{n}\mathbb{1}[L_i\le x],
\qquad
\widehat q_p=\inf\{x:\widehat F_n(x)\ge p\}.
\]

变量解释：`q50/q95/q99`分别是经验分位点；实现映射：冻结 quantile definition/interpolation、有效样本 `n`、bin precision、warm/cold/load slice，并保存 raw span。`n=100` 的 p99 基本由一个极端 order statistic 决定，不能伪装为稳定 SLO；报告 bootstrap/重复 run/cluster uncertainty 与 max。

S1说明临时高延迟在大规模/高利用率下会主导整体体验；对机器人，少量 tail 还可能跨过 contact、reset 或 safety deadline。平均值、单次 best-case、吞吐和 p99回答不同问题。

## 6. Deadline Miss 是独立 Estimand

每个 request/loop 先冻结 absolute deadline `D_i`。miss indicator 与 miss rate：

\[
M_i=\mathbb{1}[t_i^{\mathrm{apply}}>D_i],
\qquad
\widehat r_{\mathrm{miss}}=\frac{1}{n}\sum_{i=1}^{n}M_i.
\]

变量解释：deadline 可以来自 controller period、max action age 或 safety envelope；实现映射：保存 miss stage、lateness `t_apply-D`、连续 miss burst、drop/fallback/outcome，并给二项区间。timeout response 不等于 work 已取消；还要记录 late completion 与 leaked action。[S2][S8]

ROS 2 pendulum demo报告“deadline missed 后的 latency”、min/max/mean/std 和 page faults，并警告即使 mean 尚可仍可能出现不可接受的 maximum/spike。[S2] 该例支持 tail/scheduling gate，不提供 VLA action deadline 默认值。

## 7. Jitter、Network PDV 与 Action Age 分开

若 controller 目标周期为 `T_c=1/f_c`，apply-time phase error 与 interval jitter 可定义：

\[
e_i=t_i^{\mathrm{apply}}-(t_0+iT_c),
\qquad
J_i=(t_i^{\mathrm{apply}}-t_{i-1}^{\mathrm{apply}})-T_c.
\]

变量解释：`e_i`看相对理想时间轴的漂移，`J_i`看相邻执行间隔偏差；实现映射：分别报告 signed/absolute p50/p95/p99、early/late、miss burst 和频谱/周期性 spike。只报 standard deviation 会掩盖偏置与非对称 tail。

RFC 3393 的 IP packet delay variation 是网络层 metric。[S5] VLA 总 jitter 还包含 sensor cadence、OS scheduling、queue/batch、GPU、decode、controller 与 actuator；不能把 ping jitter 叫 control jitter。

对 chunk 第 `j` 条动作：

\[
A_{i,j}=t_{i,j}^{\mathrm{apply}}-t_i^{\mathrm{capture}}
\approx L_i^{\mathrm{e2e}}+jT_c.
\]

变量解释：近似式假设固定 controller period且无 queue disturbance；实现映射：实际逐条保存 `t_apply[j]`。即使 first-action latency 很低，执行较长 prefix 的后半段仍可能 stale。[S8]

## 8. Control Frequency、H/K 与 Deadline Budget

`f_c` 是 low-level apply frequency，policy query frequency 不一定相同。若一次预测 `H` 步、执行 `K≤H` 步再 replan：

\[
T_c=\frac{1}{f_c},
\qquad
T_{\mathrm{chunk}}=\frac{H}{f_c},
\qquad
T_{\mathrm{replan}}=\frac{K}{f_c}.
\]

变量解释：同样 `H/K` 在不同 `f_c` 下对应不同物理时长。实现映射：manifest冻结 action type、per-step/per-second语义、action repeat、interpolation、H/K、policy/controller Hz；改变频率可能改变 delta action 的物理语义，不能只看 shape。[S8]

可把 query budget 设为 `min(T_replan, A_max)` 再扣除 controller/safety margin，但 `A_max` 必须来自任务动力学与风险分析，不是经验拍一个 50 ms。低频 chunk 可提高吞吐，却增加 stale exposure；高频 query 可提高响应，却可能造成 queue、GPU contention 和 deadline miss。

## 9. 测量矩阵：Cold、Steady、Load 与 Fault

| 维度 | 至少的 strata | 原因 |
| --- | --- | --- |
| lifecycle | process start、first request、compile/cache warm-up、steady state、checkpoint reload | cold start不能被 warm percentile抹掉 |
| load | idle single-client、target concurrency、burst、overload、multi-robot | tail常随利用率/排队非线性上升 [S1] |
| request | camera count/resolution、prompt/token、H/D、NFE、batch、payload | 请求异构决定 compute/transport |
| runtime | checkpoint/processor/backend/dtype/device/power/thermal | 性能数字必须绑定 bundle与硬件 |
| task | free-space、contact、recovery、reset transition | 相同 latency在不同状态风险不同 |
| fault | delayed sensor、queue burst、network loss、worker restart、controller reject | 验证 miss/drop/cancel/fallback，而非只测 happy path |

每个 slice 保存 `n`、arrival model、offered load、accepted/completed/dropped/timeout 数量。只在低负载循环“发一个、等一个、再发一个”会让长响应期间没有新 request，低估真实 backlog。

## 10. Coordinated Omission

HdrHistogram README说明：当大响应时间导致预期采样被“跳过”时，原始 histogram 会漏掉本应发生的慢样本；`recordValueWithExpectedInterval` 用 expected interval 做 correction。[S4]

VLA load test建议同时记录：

- intended arrival time 与 actual send time；
- open-loop / scheduled arrivals 与 closed-loop client；
- expected interval、offered/accepted/completed QPS；
- queue depth、backpressure/drop 与 raw uncorrected/corrected view；
- robot端因安全 gate 跳过的 action cycle。

correction 不是凭空补真实 episode；它是对 load generator sampling bias 的诊断。主证据仍需原始 arrival/queue/span ledger。

## 11. 统计与 Release Gate

1. 预注册 primary endpoint：如 `capture→first apply p99` 与 `deadline miss rate`，不是看完数据再挑最好数字；
2. 同 checkpoint/request mix/load/hardware 比 candidate vs baseline，最好 paired 或按 run/robot-day cluster；
3. 同报 q50/q95/q99/max、miss k/n/CI、jitter、stale/drop/fallback、throughput 与 success/safety；
4. latency 改善不能抵消 invalid action 或 success 下降；success 提升也不能越过 hard deadline/safety veto；
5. 多次 run 报 run-to-run variability，保留 thermal、power、background load 与 compiler/cache 状态；
6. 用 EVAL-009 raw bundle重算 summary，用 EVAL-010 hard gate和 canary验证 target load；
7. simulator/server microbenchmark不替代 robot-side capture/apply trace。

## 12. Matched 实验矩阵

| sweep | 固定项 | arms | 主要读数 |
| --- | --- | --- | --- |
| model/backend | request/load/controller | checkpoint/backend/dtype/NFE | infer 与 E2E tail、parity、success |
| H/K/frequency | checkpoint/task/init/controller family | H/K、policy/controller Hz、repeat compensation | action-age curve、miss、stale、success |
| batching/queue | model/request mix/hardware | batch delay/size、queue policy、concurrency | throughput、queue p99、E2E p99、drop |
| transport | same payload/server/controller | local/in-process/LAN、serialization/compression | response/E2E tail、packet PDV、CPU |
| fault | same baseline/load | delay/burst/drop/restart/thermal | miss burst、cancel、fallback、recovery |

不要同时换 checkpoint、分辨率、NFE、batch、H/K、controller、task mix 后把差异归因于“推理优化”。

## 13. 五项目 Evidence Mapping

| 项目 | 已有证据 | 能安全说 | 不能说 / 缺口 |
| --- | --- | --- | --- |
| Robot Harness | tool polling timeout、cancel context、robot lock cleanup、best-effort compensation | 有 tool-side deadline/cancel/side-effect 控制入口 | 不是 VLA capture→apply；缺 infer/action-age p99、controller cycle、load test |
| OPD | static point/box/text eval 与 checkpoint/by-pool summaries | 可讨论 offline metric pipeline | 无 policy server、controller、clock trace、deadline/jitter；不能报 closed-loop latency |
| OpenPiVLA | local connect/infer timeout failure hooks；official OpenPI server有 `infer_ms` | 有局部 serving/timing入口，能设计 stage trace | 缺 formal checkpoint绑定的 capture/apply、warm/load p99、miss/jitter、GPU sync与 robot canary |
| WAM | 单 episode三 camera、300-step trace/video与远端 checkpoint path | 能检查 action/video步数与manifest | 没有 per-step timestamp、controller apply、latency、clock或真机闭环；视频长度不是 control frequency证据 |
| UWM | DataLoader-only A/B：p95 wait约 `13.86s→0.19s`，local-direct/smoke-bounded | 可讲训练 input stall定位 | 不是 rollout latency；缺 action-age/deadline/jitter raw episode，不能把训练 p95写成实时控制优化 |

五项目均没有 protocol-complete VLA real-time benchmark。本页只生成补证据合同，不新增 latency 或 success 结果。

## 14. 最小 Artifact Bundle

```text
latency_eval/
  clock_contract.json          # source/resolution/host/offset/skew uncertainty
  protocol_manifest.json       # model/processor/request/load/H/K/Hz/controller/hardware
  raw_spans.parquet            # per request/stage start-end + IDs
  action_apply.parquet         # capture/chunk offset/controller apply/next sensor
  arrivals_queue.parquet       # intended/actual arrival, depth, batch, drop
  outcomes.jsonl               # deadline/stale/fallback/success/safety
  summaries/by_slice.json      # n, q50/q95/q99/max, miss k/n/CI, jitter
  figures/{timeline,cdf,tail,load_curve}.svg
  checksums/manifest-sha256.txt
  reproduce.ps1
```

## 15. 评估伪代码

```python
def latency_eval(policy_client, controller, schedule, protocol, clock):
    # 1. Freeze bundle, request/load mix, H/K/Hz and every event boundary.
    spec = validate_clock_protocol_and_deadlines(protocol, clock)

    # 2. Schedule arrivals independently of prior response completion.
    for req in schedule.intended_arrivals:
        trace = start_trace(req, intended_ts=req.ts)
        obs = capture_with_timestamp(req, clock)

        # 3. Record queue/infer/transport/decode spans; synchronize GPU timing.
        chunk = policy_client.infer_with_spans(obs, trace, sync_device=True)

        # 4. Reject late/stale responses and timestamp every applied chunk offset.
        for j, action in enumerate(freshness_gate(chunk, req.deadline)):
            t_apply = controller.apply(action)
            trace.mark_apply(j, t_apply)

        # 5. Persist raw spans/outcomes before percentile aggregation.
        write_immutable_trace(trace)

    # 6. Stratify cold/warm/load/fault and compute tail, miss, jitter and age.
    return recompute_latency_release_report(protocol)
```

这是 evaluation contract，不是五项目已有实现。

## 16. Source Gate 结论与下一入口

EVAL-013 保持 `WARN`：Tail at Scale支持 tail 的系统重要性；ROS 2 demo支持 deadline lateness、max/spike 与 page-fault real-time边界；HdrHistogram支持 coordinated-omission警告；RFC 3393和ROS QoS帮助分开网络 PDV、latest sample 与完整控制 jitter；CPython/OpenPI冻结 clock/serving打点入口。本页完成 event boundary、clock、tail、deadline、jitter、H/K/Hz、load与artifact合同；五项目均缺 capture→apply 的 protocol-complete实时证据。

下一节点固定为 `VLA-EVAL-014`：forbidden side effect、scope、取消与补偿评估。真实口述前不创建 `coaching_state.md`。

## References

1. Dean & Barroso, [*The Tail at Scale*](https://research.google/pubs/the-tail-at-scale/), CACM 2013。
2. ROS 2 `demos` commit [`54d49d2`](https://github.com/ros2/demos/tree/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control)，[pendulum control README](https://github.com/ros2/demos/blob/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control/README.md)，Apache-2.0。
3. ROS 2 Design commit [`93a415b`](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/qos.md)，*Quality of Service policies*，Apache-2.0。
4. HdrHistogram commit [`de84b0a`](https://github.com/HdrHistogram/HdrHistogram/tree/de84b0a7de2378abfc405da503bf4898e84ea98e)，CC0 / BSD-2-Clause。
5. IETF, [RFC 3393](https://www.rfc-editor.org/rfc/rfc3393), *IP Packet Delay Variation Metric for IP Performance Metrics*, 2002。
6. CPython [`time.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/time.rst)，PSF-2.0。
7. Physical Intelligence [`openpi@15a9616`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)：`websocket_policy_server.py`、`serve_policy.py`、`policy.py`，Apache-2.0。
8. [ENG-022 Policy Server](vol_05_eng022_policy_server_resilience_source_freeze.html)、[WM-034 Control Latency](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)、[VOL 03 Architecture / Execution](vol_03_architecture_execution_claim_to_code.html)、[EVAL-009 Recomputable Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010 Release Gate](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)。
9. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目 inventories。
