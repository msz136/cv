# VOL 08 SYS-002 Source Freeze：Policy Serving 与 Real-time Control Loop

> 状态：`source_frozen / SYS-VLA-002 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本页冻结 policy client/server、request/response、action chunk/replan、deadline/backpressure 与 real-time boundary 的来源和项目真实性边界；下游 knowledge/card 已在独立 bounded slice 生成，仍不改变 mastery，不把设计建议写成 OpenPI 或个人项目既有实现。  
> 前置：[VOL 08 Coverage-Gap Audit](vol_08_coding_system_design_coverage_gap_audit.html)、[SYS-VLA-001](vol_08_sys001_vla_training_eval_platform_source_freeze.html)、[ENG-022](vol_05_eng022_policy_server_resilience_source_freeze.html)、[EVAL-013](vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html) 与 [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。

## 问题（Question）

怎样把 VLA 模型接入实时控制环，而不把“有一个 WebSocket demo”误称为生产 policy service？需要冻结哪些 request/response schema、状态所有权、action chunk/replan、deadline、backpressure、batching、controller 与 fail-safe 边界，才能回答端到端系统设计追问？

## 1. 结论先行

1. frozen OpenPI 提供了一个可核的最小 serving baseline：服务端连接后先发 metadata，再按 `recv observation → policy.infer → attach timing → send action result` 处理；同步客户端执行 `send → recv`。它没有显式 request ID、deadline、admission queue、dynamic batching、cancellation propagation 或 robot watchdog。
2. action-chunk 状态位于 client/consumer 侧：`ActionChunkBroker` 缓存上次结果与当前 cursor；LIBERO example 默认每 5 步重新请求并只执行 chunk 前 5 步，DROID example 以可配置 open-loop horizon 决定何时重新请求。以上是固定 example 合同，不是所有 VLA 的通用 H/K。
3. OpenPI 的 `server_timing.infer_ms` 与 `prev_total_ms` 只能支持 server-local timing；它不包含 observation capture、排队、网络、client postprocess、controller apply 或后续 chunk action age，不能证明 control-loop deadline。
4. CPython、Triton、gRPC 与 ROS 2 来源分别支持 bounded queue、batch queue policy、deadline/propagation、fresh sensor queue 与 real-time profiling机制；把这些机制组合成 VLA service 是本仓库的系统设计综合，不是 OpenPI 现状。
5. 本地 OpenPiVLA 有 official WebSocket client 的 offline action-eval入口与 connect/infer timeout wrapper；另一个 ALOHA rollout 是 in-process policy + `ActionChunkBroker`，不是网络 policy server。它们支持 eval-interface engineering，不支持 production p99、batching、multi-robot fairness、cancel propagation、hard real-time 或 physical safety claim。
6. 本轮14/14 deterministic source probes通过；但缺少可执行统一服务、schema version/request ID、端到端 timestamp trace、load/fault injection、controller watchdog/e-stop、formal checkpoint bundle 与候选人逐项 ownership，因此 verdict 保持 `WARN`。

## 2. 冻结来源、Revision、许可与 Claim Boundary

所有公开 SHA 对2026-07-20重新取得的 pinned UTF-8 原文按 LF 计算；本地 SHA 对当前文件字节计算。`checked` 只证明指定来源仍可取得且内容 hash 匹配，不证明用户运行了该系统。

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | OpenPI [`websocket_policy_server.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/serving/websocket_policy_server.py) | official-code；`openpi@15a9616a...`；Apache-2.0 | `1370D345E6C3C5B8F15573050E485E60A5B423D1DF33E24B237805E6B442B026` | metadata、msgpack、recv→infer→send、server timing 与 connection/error path | queue/batch/deadline/request ID/watchdog 已实现 |
| S2 | OpenPI [`scripts/serve_policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/scripts/serve_policy.py) | official-code；同 commit/license | `ECCC0448B4873FD30A1FFF3355C5DE7A7C227138E6DB04B7DCAA5BB38A6A5809` | default/checkpoint policy、metadata、recorder 与 server 启动入口 | production deployment、SLO、autoscaling |
| S3 | OpenPI [`policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py) | official-code；同 commit/license | `A2AC5236E23B11D0F5A840D4A8FEF148D89DBA921D5452EC5DFCD5A6FFA46F20` | input/output transform、normalization、sampling 与 timing boundary | controller schema、network deadline、robot safety |
| S4 | OpenPI [`websocket_client_policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/websocket_client_policy.py) | official-code；同 commit/license | `36557CB0B91CCF31CD4FB4B508306850D76ED0FEB4028DAC5182D0F5A5D88005` | connect/retry、metadata、同步 send/recv 与 error-string boundary | timeout/deadline/request ID/cancel 已实现 |
| S5 | OpenPI [`action_chunk_broker.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/action_chunk_broker.py) | official-code；同 commit/license | `019B9D69CB26CC681331A2F95DBE60A2CC7B02D6D309C5D15B6457AB39798234` | cached result、cursor、逐步 slice 与 horizon reset | stale-response ID、deadline 或安全检查 |
| S6 | OpenPI [`examples/libero/main.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/main.py) | official-code；同 commit/license | `D53748C95804ADA559E3CA867305B8F755D8651C4C7F4E2723EF80AEA55A3943` | `replan_steps=5`、chunk length assertion、执行前K步与 success logging | 通用机器人K值、real-time SLO、真机安全 |
| S7 | OpenPI [`examples/droid/main.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/droid/main.py) | official-code；同 commit/license | `4BDBDBDDE068EBB30BA90D62BF8C51DF156B4BAAE5C5AC5870C08F7B03D4AFC2` | client query cadence、`[10,8]` example、env step 与 control-frequency sleep | 通用action shape、deadline guarantee、用户项目实现 |
| S8 | OpenPI [`LICENSE`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/LICENSE) | official-license；Apache-2.0 | `43070E2D4E532684DE521B885F385D0841030EFA2B1A20BAFB76133A5E1379C1` | 上述code许可边界 | checkpoint/model-card许可自动相同 |
| S9 | CPython [`asyncio-queue.rst`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-queue.rst) | official-doc；`cpython@2931f2...`；PSF-2.0 | `C7312064E8C18F1E45656BBABB59949CDD0ADF258F32595D073B2E66593244D2` | `maxsize`、blocking put、`QueueFull`、queue op无timeout参数 | OpenPI 已使用此queue |
| S10 | CPython [`asyncio-task.rst`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-task.rst) | official-doc；同 commit/license | `1D833356E1A5977399A0668EF7A07223DB793CC1A1BCAD4DAE4934D8D8434CD2` | `timeout`/`wait_for`、cancellation 与 TimeoutError 语义 | GPU kernel 或 robot side-effect 已被取消 |
| S11 | Triton [`model_configuration.md`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/model_configuration.md) / [`batcher.md`](https://github.com/triton-inference-server/server/blob/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide/batcher.md) | official-doc；`server@0ae38c...`；BSD-3-Clause | config `01E50042A66024AD5C9143E7AA3F43B0338F29F8EF6CC42979909589774B8151`；batcher `577E45C86B65A73E42ACA1BB406D48A5EDF25540E9312DE904388AE69C1F9505` | batch dimension、preferred batch、queue delay/size、timeout action | VLA schema天然可batch或OpenPI使用Triton |
| S12 | gRPC [Deadlines](https://github.com/grpc/grpc.io/blob/78db5a6f78ee0d3426cf53cee07739196d962ea2/content/en/docs/guides/deadlines.md) | official-doc；`grpc.io@78db5a6...`；content CC BY 4.0 / samples Apache-2.0 | `E310A0E5A4BDC8F353EF04A641336D9A51176FFAA0BA0EE8B8B1AAD98263A900` | deadline vs timeout、`DEADLINE_EXCEEDED`、server cancellation与propagation | OpenPI WebSocket 自动具有gRPC语义 |
| S13 | ROS 2 [QoS design](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/qos.md) | official-design；`ros2/design@93a415...`；Apache-2.0 | `E4C8F7A73ABBC2B367017C3A2E5637A9CCD3A2914F68D9F8BC92EE46DFE11E41` | keep-last/depth、sensor timely-over-reliable设计边界 | latest-wins必然适合action或保证稳定 |
| S14 | ROS 2 [`pendulum_control/README.md`](https://github.com/ros2/demos/blob/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control/README.md) | official-code/doc；`ros2/demos@54d49d...`；Apache-2.0 | `55CF38FB84378228C3F031F88985A2BC016B7524B2BF79C6FB0978A43D29C3FF` | deadline latency、page fault、memory lock、priority 与 latency spike boundary | WebSocket/JAX/Python loop是hard real-time |

许可复核：CPython `LICENSE` SHA `B0E25A78...10231`；Triton `LICENSE` SHA `179F3734...0036`；ROS design/demo `LICENSE` SHA 分别为 `0E18850F...B76A` / `CFC7749B...D30`；gRPC repo `LICENSE` SHA `9E3D1E4B...0201`。

## 3. Claim Registry：可写、需标 inference、必须拒绝

| Claim | 类型 | 证据 | Verdict / 边界 |
| --- | --- | --- | --- |
| frozen OpenPI server按连接先发metadata，再循环recv→infer→send | official-code direct | S1 | `checked`；仅该commit |
| frozen OpenPI client是同步send→recv并读取metadata | official-code direct | S4 | `checked`；没有因此获得deadline/cancel |
| OpenPI返回server-local infer/previous-total timing | official-code direct | S1/S3 | `checked`；不等于E2E/action age |
| action chunk cursor/client-side replan可由broker/examples实现 | official-code direct | S5/S6/S7 | `checked`；H/K是example/config，不是标准 |
| bounded admission、dynamic batching、deadline propagation是生产设计所需机制 | cross-source synthesis | S9–S13 + ENG-022/EVAL-013 | `inference / design requirement`；不得称OpenPI已实现 |
| observation queue可采用latest-wins/keep-last以限制staleness | same-source inference | S13 | 仅适合允许丢旧观测的协议；不能套到action或side effect |
| Python WebSocket policy server满足hard real-time | unsupported | S1/S4/S14 | `rejected`；缺scheduler/memory/page-fault/deadline证据 |
| 用户完成production policy service或multi-robot serving | unsupported personal claim | local evidence gate | `rejected`；当前只有局部eval/rollout入口 |
| server timeout后物理robot一定停止 | unsupported safety claim | S10 + missing controller evidence | `rejected`；software cancel与physical stop分层 |

## 4. Source-direct Serving Path 与 Schema Boundary

### 4.1 frozen OpenPI 最小路径

```text
# Official-code direct at openpi@15a9616a; not a production topology.
client connect
  <- server metadata (one message)
client pack(observation) -> WebSocket bytes
server unpack -> policy.infer(observation)
server attach server_timing -> pack(action result)
client recv -> unpack(result)
consumer selects/executes action rows
```

S1/S4直接支持消息顺序与msgpack边界。当前文件中没有正式 schema version、request ID、observation timestamp、absolute deadline、model revision echo、action expiry、controller acknowledgement 或 retry/idempotency key。metadata可以承载部分identity，但“可以承载”是设计可能性，不是当前字段已齐全。

### 4.2 建议冻结的 request envelope（design inference）

后续knowledge只能把下列字段写成“面试设计合同”，不能写成OpenPI现有字段：

| 类别 | 最小字段 | 作用 |
| --- | --- | --- |
| identity | `request_id/session_id/robot_id/model_revision/schema_version` | 去重、路由、回包关联与审计 |
| observation | `capture_ts/clock_id/camera_ids/state/action_history/prompt` | 计算age、保证camera/state语义 |
| timing | `deadline_abs/enqueue_ts/infer_start/infer_end/send_ts` | 分段预算、deadline miss与first divergence |
| output | `action_chunk/H/D/frame/unit/normalizer_revision/valid_until` | parser、denorm、slice与freshness |
| control | `replan_after_K/controller_mode/fallback_policy` | 明确谁执行几步、失败后谁接管 |

## 5. 状态所有权（State Ownership）

| 状态 | frozen OpenPI 中的直接位置 | 系统设计追问 | 当前缺口 |
| --- | --- | --- | --- |
| model/checkpoint/transforms | server policy object / serve entry | revision切换、warmup、load/readiness | no immutable runtime manifest in this node |
| server metadata | server connection init → client cache | schema/model/norm identity是否完整 | exact metadata fields depend on launcher/policy |
| WebSocket connection | client object | reconnect、auth、timeout、half-open | no explicit per-call deadline in S4 |
| latest observation/env state | example consumer/client loop | capture clock、stale/drop、camera/state consistency | no shared envelope or timestamp trace |
| action chunk cache/cursor | `ActionChunkBroker._last_results/_cur_step` or example queue | H、K、replan trigger、old chunk disposal | no request ID/expiry/stale-response guard |
| controller state/side effect | environment/robot wrapper outside policy server | apply ack、stop/hold/e-stop、exactly-once boundary | not proven by WebSocket response |

关键结论：模型服务完成“返回动作候选”不等于controller完成“安全执行”。server、client/broker、controller三层各自持有不同状态；没有显式ownership与ack时，timeout后无法仅凭server日志证明robot状态。

## 6. Timing、Deadline 与 Action Freshness

### 6.1 端到端 critical path

令 \(t_c\) 为 observation capture，\(t_e\) 为 enqueue，\(t_i\) 为 inference start，\(t_r\) 为 response receive，\(t_p\) 为 postprocess完成，\(t_a\) 为 controller apply；则首动作端到端延迟为：

\[
T_{\mathrm{e2e}}
=(t_e-t_c)+(t_i-t_e)+(t_r-t_i)+(t_p-t_r)+(t_a-t_p).
\]

变量解释：五项依次对应capture/serialize、queue/batch wait、infer+transport、parse/denorm/safety与controller handoff。S1只直接给出server infer和previous total的局部计时；完整分解来自EVAL-013的评估合同与本页系统综合，必须标为design instrumentation。

### 6.2 chunk后续动作也会变旧

若一次请求在 \(t_c\) 捕获观测并返回 \(H\) 步chunk，consumer实际执行前 \(K\le H\) 步，第 \(k\) 行动作的年龄为：

\[
A_k=t_{\mathrm{apply},k}-t_c,
\qquad k=0,\ldots,K-1.
\]

变量解释：\(H\) 是模型输出horizon，\(K\) 是下一次query前执行行数。即使首行低延迟，后续 \(A_k\) 仍随控制周期增加；S5/S6/S7支持cursor与example replan行为，但没有替用户选择freshness阈值。

### 6.3 deadline传播

设caller绝对deadline为 \(D\)，任一层当前时刻为 \(t\)，剩余预算为：

\[
B_{\mathrm{remain}}=D-t.
\]

变量解释：S12区分deadline与timeout并描述propagation/cancellation；把该合同应用到WebSocket VLA服务是design inference。每层重新给一个完整timeout会放大总延迟，正确实现还需统一clock/跨主机同步策略、cancel acknowledgement和GPU/controller side-effect测试。

## 7. Admission、Backpressure 与 Batching Boundary

1. **bounded admission**：S9说明`asyncio.Queue(maxsize)`达到上限后`put`阻塞，queue API自身无timeout参数；它提供机制，不说明OpenPI使用了该queue。
2. **batch formation**：S11说明dynamic batching依赖batch dimension、preferred batch、queue delay、queue size和timeout action。VLA不同camera数、resolution、prompt、state/action shape、normalizer或controller contract不能只因同时到达就混batch。
3. **fresh observation**：S13的sensor profile强调及时性与较小keep-last queue；这可以启发丢弃旧observation，但action/command通常具有side effect，不能无条件latest-wins。
4. **frozen OpenPI baseline**：S1在每条收到的消息上直接调用`policy.infer`；S1/S4没有显式admission queue或batcher。因此“OpenPI支持多连接”与“服务已经有多机器人公平batch scheduler”是不同主张。

系统面试中必须同时回答吞吐和freshness：吞吐更高但action age越过deadline不是成功优化；无界queue把overload转成stale action与tail latency。

## 8. Real-time 与 Safety 的 Fail-closed Boundary

### 8.1 soft real-time、hard real-time 与普通RPC

S14把real-time profiling落到deadline miss latency、min/max/mean/std、page fault、memory lock和priority；即使平均值较好，最大latency spike仍可能不可接受。Python WebSocket + model inference只凭`infer_ms`不能升级为hard real-time。

本节点允许的安全措辞：

- “为控制环设计deadline/freshness/fallback接口”；
- “使用ROS 2 real-time来源定义验证门”；
- “当前服务路径是soft-real-time candidate / best-effort RPC”。

本节点拒绝的措辞：

- “WebSocket天然实时”；
- “timeout就保证robot停止”；
- “server exception等同physical e-stop”；
- “平均20ms证明20Hz闭环稳定”。

### 8.2 cancellation不是physical stop

S10/S12支持task/RPC cancellation语义；但GPU kernel、已发送controller command、robot inertia和外部side effect可能继续存在。后续knowledge必须把 `cancel compute`、`discard stale response`、`controller hold/stop`、`independent e-stop` 分成不同层，并把最后两层标为需要controller/robot direct evidence。

## 9. 本地项目证据与真实性边界

### 9.1 本轮重新哈希的 OpenPiVLA local-direct 文件

| 文件 | SHA-256 / bytes | 直接支持 | 不能支持 |
| --- | --- | --- | --- |
| `scripts/eval_lerobot_action_server.py` | `B1B7FB9...AB4F39` / 19,702 | official `WebsocketClientPolicy`、connect/infer alarm、`server_unavailable`/`infer_failed`、offline action metric入口 | online controller、queue/batch、p99、cancel propagation |
| `scripts/run_aloha_sim_real_rollout.py` | `E583E477...91DE3` / 11,583 | in-process `create_trained_policy` + `ActionChunkBroker`、env apply、episode trace入口 | 网络policy server或formal Qwen checkpoint闭环 |
| `DEPLOYMENT.md` | `C0A3DD0C...A14E` / 28,695 | official server/client/checkpoint path与报告边界 | remote state、binary identity、无failure summary等于production SLO |

`eval_lerobot_action_server.py`的alarm wrapper是process-local eval failure reporting；它没有证明server取消inference或robot停止。`run_aloha_sim_real_rollout.py`第172行创建in-process policy，第178行创建broker，第187–188行broker infer后直接apply action，因此不能称为WebSocket deployment。

### 9.2 五项目边界

| 项目 | 可用hook | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | offline WebSocket action eval、in-process broker rollout、timeout/failure summary、H/D/parser风险 | production service、formal checkpoint serving、p99/fairness、cancel→physical stop、个人完整ownership |
| Robot Harness | tool polling timeout、cancel context、scope/lock cleanup与best-effort compensation | VLA inference batcher、action freshness、controller deadline或robot success |
| OPD | training/eval data route与strict scorer | policy serving、closed-loop controller或fleet |
| WAM | simulator rollout launcher、chunk/controller schema与diagnostic | network serving、hard real-time、真机watchdog或已验证checkpoint uplift |
| UWM / LIBERO | simulator protocol、action/state/normalizer与rollout evidence | production policy service、multi-robot serving或跨协议真机泛化 |

回答顺序保持 `public upstream → local-direct → inference/design → unverified`。系统设计能力可以口述，但“我建设并上线了该系统”必须另有local runtime、load/fault test与ownership证据。

## 10. Deterministic Source Probes

本轮从固定raw URL重新取源并执行14项字符串/顺序probe；这些probe验证本页引用的代码/文档锚点，不验证runtime性能。

| Probe | 结果 | 检查内容 |
| --- | --- | --- |
| P01 | PASS | server metadata send位于message loop之前 |
| P02 | PASS | server `recv < policy.infer < send` 顺序 |
| P03 | PASS | server含`infer_ms`与`prev_total_ms` |
| P04 | PASS | server文件无deadline/request ID/asyncio queue/batcher显式实现 |
| P05 | PASS | client infer为同步send→recv |
| P06 | PASS | client文件无timeout/deadline/request ID |
| P07 | PASS | broker含last-result、cursor、action-horizon reset |
| P08 | PASS | LIBERO为`replan_steps=5`且slice前K步 |
| P09 | PASS | DROID含open-loop horizon、env step与control-frequency sleep |
| P10 | PASS | CPython bounded queue与external timeout contract |
| P11 | PASS | Triton queue delay/size/timeout policy入口 |
| P12 | PASS | gRPC deadline propagation/timeout conversion入口 |
| P13 | PASS | ROS 2 QoS keep-last/timely sensor/small depth入口 |
| P14 | PASS | ROS 2 real-time page-fault/max-latency/memory-lock入口 |

汇总：`14/14 PASS`。Negative probe只说明指定文件中未出现对应机制，不能证明整个upstream仓库或未来版本永远没有该能力。

## 11. Knowledge 下游允许与禁止的命题

### 11.1 可以进入 SYS-VLA-002 knowledge

1. frozen OpenPI request/response、metadata、timing与client-side chunk cursor的直接事实。
2. E2E latency、action age、deadline remaining budget三条公式及其source/inference标签。
3. server/client/controller三层state ownership与ack边界。
4. bounded admission、compatible batching、fresh-observation与side-effect action的差异。
5. soft/hard real-time、cancel compute与physical stop的分层。
6. 五项目只能作为有证据的interface/gap hook。

### 11.2 不能进入强回答

1. OpenPI或个人项目已有生产级queue/batching/deadline/fairness/watchdog。
2. `infer_ms`等于capture→apply E2E latency。
3. example的`H=10`、`K=5`、`[10,8]`是用户模型或所有机器人标准。
4. connection/timeout错误能够证明inflight compute取消、old action清空或robot停止。
5. official code、路径、root Git author或文档记录等于候选人个人端到端ownership。

## 12. Source Gate 结论与下一切片

本节点已达到`source_frozen`：14个公开source rows、8个OpenPI文件hash、CPython/Triton/gRPC/ROS机制边界、3个local-direct OpenPiVLA文件与14/14 probes均可复核。它仍是`WARN`，因为没有本地统一服务、immutable formal checkpoint bundle、versioned request/response trace、E2E timestamp、load/fault injection、controller acknowledgement、watchdog/e-stop与candidate role confirmation。

下一 bounded slice：**只生成 `SYS-VLA-002` knowledge page**，把本source contract教学转译为requirements→API/schema→state→timing→backpressure→failure→project truth；不生成题卡，不启动`SYS-VLA-003`或`PER-019`，不创建`coaching_state.md`，不修改mastery。

## 参考文献（References）

1. Physical Intelligence, [OpenPI `openpi@15a9616a`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), Apache-2.0：S1–S8。
2. CPython, [`asyncio` queue/tasks docs at `2931f2`](https://github.com/python/cpython/tree/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library), PSF-2.0：S9–S10。
3. NVIDIA Triton Inference Server, [docs at `0ae38c`](https://github.com/triton-inference-server/server/tree/0ae38c793358f8db77a9cbc1d1bde984619d5c1b/docs/user_guide), BSD-3-Clause：S11。
4. gRPC, [Deadlines at `grpc.io@78db5a6`](https://github.com/grpc/grpc.io/blob/78db5a6f78ee0d3426cf53cee07739196d962ea2/content/en/docs/guides/deadlines.md)：S12。
5. ROS 2, [QoS design at `93a415`](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/qos.md) and [pendulum control at `54d49d`](https://github.com/ros2/demos/blob/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control/README.md), Apache-2.0：S13–S14。
6. 本仓库 [ENG-022 Policy Server Resilience](vol_05_eng022_policy_server_resilience_source_freeze.md)、[EVAL-013 Latency/Deadline/Jitter](vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.md)、[VOL 03 Architecture/Execution Audit](vol_03_architecture_execution_independent_fact_review.md)。
7. 本仓库 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.md) / [Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.md) 与其余四项目 inventories/ledgers。
