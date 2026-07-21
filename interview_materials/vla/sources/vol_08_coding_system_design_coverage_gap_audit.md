# VOL 08 Coding / System Design：Coverage-Gap Audit

> 审计日期：2026-07-20  
> 状态：`coverage_contract_frozen / planned_12 / sources_12 / knowledge_12 / cards_12 / missing_sources_0 / missing_knowledge_0 / missing_cards_0 / WARN`  
> 审计对象：VOL 08 已有 source/knowledge/card、早期手撕题 registry、全局 Knowledge Map、Repository Completion Audit、GitHub skeleton guidance、VOL 05 工程/评估卷与五项目 evidence inventory。  
> 核心边界：本报告冻结整卷范围、去重边界和退出条件；`SYS-VLA-002..003` 三联件已同步但未练习，不把 VOL 05 组件知识重复包装成系统设计答案，不把公开系统方案写成个人项目成果。  

## 问题（Question）

现有 `SYS-VLA-001` 与 `CODE-VLA-001..006` 是否足以支持“VOL 08 Coding / System Design 已完成”？如果不足，整卷应冻结为哪些不可合并的系统设计与手撕实现节点，如何与 VOL 01、VOL 05 和个人项目证据分工？

## 1. 结论先行

1. VOL 08 冻结为 **12 个原子节点**：`SYS-VLA-001..004` 四个系统设计题，`CODE-VLA-001..008` 八个手撕实现题；其中 10 个 P0、2 个 P1。
2. 当前 source coverage 为`12/12=100%`，knowledge coverage 为`12/12=100%`，card coverage 为`12/12=100%`：`SYS-VLA-004` source+knowledge+card 已完成；`CODE-VLA-008` 已完成 source+knowledge+card，`CODE-VLA-007` 与 `SYS-VLA-001..003/CODE-VLA-001..006` 均已有三联件。十二张题卡全部保持`unseen/WARN`。
3. 页面三联件已完整闭合；不能把页面覆盖计为题卡掌握，四题 SYS 口述与八题 CODE 练习仍是独立退出门。
4. WinstonJQ 骨架支持“先题目清单、再分卷、Markdown canonical、折叠题卡、review、L1/L2/L3”的工作流，但不支持具体 VLA 系统事实、题目频次或个人项目 claim。
5. VOL 05 负责可复用组件机制；VOL 08 的系统设计题必须把这些组件整合成 requirements/capacity、API/schema、state ownership、SLO/deadline/backpressure、failure/degradation/rollback、scaling/cost/safety 和项目证据边界，不能只背组件名。
6. Coverage、review、drill 与 project truth 分开验收。即使未来达到 12/12 页面覆盖，没有四题真实系统设计口述与八题白板/runtime 练习，也不能标记为 `drilled/done`。

## 2. 本次审计依据

| 依据 | 实际支持 | 不能支持 |
| --- | --- | --- |
| [GitHub Source Scout](00_github_guidance_and_sources.html) | WinstonJQ 骨架：主索引、分卷、canonical Markdown、折叠题卡、review、L1/L2/L3 与题目前置清单 | VLA 系统设计的技术事实、面试频次或个人贡献 |
| [VLA Knowledge Map](../knowledge/00_vla_knowledge_map.html) | VOL 08 应覆盖 attention/loss/norm、geometry/FK、train pipeline、policy service、robot fleet、fault recovery | 当前十一节点已有 source/knowledge，十张题卡已生成 |
| [Repository Completion Audit](repository_completion_audit.html) | 全局 274 张卡均 unseen；VOL 08 当前有十二个完整节点，SYS-004 三联件已同步 | registry-only ID 或页面生成等于掌握 |
| [VOL 01 Phase 0 Question List](../questions/vol_01_foundations.question_list.md) | `CODE-VLA-001..008` 的早期手撕候选边界，含 PID 与 TD(0) | 007 source 已冻结但 knowledge/card 未生成；008 仍 planned |
| [SYS-VLA-001 Source Freeze](vol_08_sys001_vla_training_eval_platform_source_freeze.html) | dataset/run/bundle/eval/rollout lineage 与可复现训练—评估平台合同 | policy service、fleet 和 fault-recovery 三题已经覆盖 |
| [SYS-VLA-002 Source Freeze](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.html) | OpenPI request/response、client-side chunk/replan、deadline/backpressure、real-time boundary、14/14 probes与五项目truth boundary | knowledge 与题卡已转译；production SLO、hard real-time或个人端到端ownership仍未完成 |
| [CODE-VLA-001..006 Source Freezes](vol_08_code001_softmax_source_freeze.html) | softmax、attention、norm、masked loss、transform、planar FK 六个实现节点各自的来源与测试边界 | PID、TD(0) 或本地白板/runtime 已完成 |
| [VOL 05 Completion Audit](vol_05_completion_independent_fact_review.html) | 工程与评估组件知识的计划内覆盖和证据边界 | 四个端到端 system-design oral answer |
| 五项目 inventories / ownership ledgers | 项目接口、artifact、指标与个人贡献边界 | 已建设统一平台、robot fleet、生产 policy service 或物理安全系统 |

## 3. 当前资产盘点

| 层 | 已有 | 目标 | 覆盖 | 仍开放的门 |
| --- | ---: | ---: | ---: | --- |
| planned stable IDs | 12 | 12 | 100% contract | 本报告只冻结边界，不代表内容完成 |
| source freeze | 12 | 12 | 100% | source gate 已冻结；三联件已同步 |
| knowledge nodes | 12 | 12 | 100% | knowledge gate 已冻结；三联件已同步 |
| generated question cards | 12 | 12 | 100% | 页面覆盖完成；仍需真实系统设计/白板训练 |
| system-design oral drill | 0 | 4 | 0% | 四张 SYS 卡均已生成并保持 unseen，尚未完成限时口述 |
| coding whiteboard/runtime drill | 0 | 8 | 0% | 六张已有卡仍 unseen，007/008 未生成 |
| project truth gate | 5 inventories + 5 ledgers | 每个 system answer 都有 bounded hook | partial | 不得把 interface/evidence 升级成 platform/fleet ownership |

## 4. 整卷 Stable-ID 合同

| ID | 优先级 / 难度 | 冻结题目 | 当前状态 | 不得合并掉的核心边界 |
| --- | --- | --- | --- | --- |
| `SYS-VLA-001` | P0 / L3 | 可复现的 VLA 训练—评估平台 | source + knowledge + card / unseen | data/run/checkpoint/bundle/eval/rollout lineage 与 protocol identity |
| `SYS-VLA-002` | P0 / L3 | Policy serving 与 real-time control loop | source + knowledge + card / unseen | API/schema、session/state ownership、latency budget、deadline、backpressure、chunk/replan、fallback |
| `SYS-VLA-003` | P1 / L3 | Robot fleet 与 multi-tenant GPU scheduling | source + knowledge + card / unseen | capacity、tenant/robot/model identity、placement、fairness、cache、rollout、cost 与异构设备 |
| `SYS-VLA-004` | P0 / L3 | Fault recovery、safety 与 observability | source + knowledge + card / unseen | first-divergence、SLO、degradation、cancel/e-stop 边界、rollback、replay 与 incident evidence |
| `CODE-VLA-001` | P0 / L1 | Numerically stable softmax / log-softmax | source + knowledge + card / unseen | max-shift、mask、dtype、all-masked row 与 parity |
| `CODE-VLA-002` | P0 / L2 | Scaled dot-product attention | source + knowledge + card / unseen | shape、scale、mask、dropout、complexity 与 backend parity |
| `CODE-VLA-003` | P0 / L1 | LayerNorm / RMSNorm | source + knowledge + card / unseen | axis、centering、variance/RMS、epsilon、dtype 与 train/eval |
| `CODE-VLA-004` | P0 / L1 | Masked MSE / Huber loss | source + knowledge + card / unseen | valid denominator、empty mask、weighting 与 distributed reduction |
| `CODE-VLA-005` | P0 / L2 | Homogeneous transform composition | source + knowledge + card / unseen | `T^A_B` 方向、frame、单位、时间戳、point/vector/pose 与 inverse |
| `CODE-VLA-006` | P1 / L2 | 2-link planar forward kinematics | source + knowledge + card / unseen | relative joint angle、analytic/matrix parity、Jacobian 与 FK/IK 边界 |
| `CODE-VLA-007` | P0 / L2 | PID update with anti-windup | source + knowledge + card / unseen | `dt`、derivative state、saturation、conditional integration/back-calculation 与 reset |
| `CODE-VLA-008` | P0 / L2 | Bellman TD(0) update | source + knowledge + card / unseen | reward、discount、bootstrap、terminated/truncated 与 batch mask |

`registered / planned` 只表示 stable ID 已进入范围，不进入 272 张 generated-card 计数，也不产生 mastery。

## 5. 依赖主链与学习簇

```text
# Planned nodes are scope contracts, not generated answers.
CODE-001 softmax -> CODE-002 attention
CODE-003 norm + CODE-004 masked loss -> train-time numerical correctness

CODE-005 transform -> CODE-006 FK -> CODE-007 PID -> policy/controller boundary
VOL 01 MDP/Bellman -> CODE-008 TD(0) -> value/update implementation

VOL 05 reproducibility/packaging/eval -> SYS-001 train-eval platform
VOL 05 policy server/latency -> SYS-002 serving-control loop
VOL 05 scheduling/retry/observability -> SYS-003 fleet -> SYS-004 recovery/safety
```

| 学习簇 | IDs | 当前 / 目标 | 主要验收方式 |
| --- | --- | ---: | --- |
| 数值与 Transformer 实现 | `CODE-001..004` | 4 / 4 | 白板实现、shape/mask/dtype probes、reference parity |
| 几何、控制与 RL 更新 | `CODE-005..008` | 2 / 4 | 单位/frame/edge-case 测试、finite difference、termination semantics |
| 训练、服务、fleet 与恢复 | `SYS-001..004` | 1 / 4 | 需求澄清、容量估算、API/schema、SLO/failure/rollback 口述 |

## 6. 与 VOL 01 / VOL 05 的去重边界

### 6.1 VOL 01 Foundations 与 CODE 题

VOL 01 负责解释公式、概念与使用条件；VOL 08 CODE 负责在明确函数签名、shape、dtype、mask、edge case、复杂度和测试 oracle 下实现。能口述 softmax 或 PID 原理不等于能写出稳定、可测的实现。

### 6.2 VOL 05 Engineering / Evaluation 与 SYS 题

VOL 05 的 ENG/EVAL 节点是组件知识。VOL 08 每个系统设计回答必须显式走完以下主线：

1. 需求与非目标：任务类型、机器人/请求规模、控制频率、安全边界、可接受降级。
2. 容量与延迟预算：吞吐、并发、GPU/CPU/网络、端到端 deadline 与 jitter。
3. API 与 schema：observation/action/model/session/run identity、版本、幂等与兼容性。
4. 状态所有权：谁持有 session、action chunk、normalizer、checkpoint、robot lease 与 replay cursor。
5. 正常数据流：从 observation capture 到 infer、validate、denormalize、execute、replan、record。
6. 压力与失败：queue/backpressure、timeout、partial failure、stale observation、model/server/controller mismatch。
7. 降级与恢复：fallback、cancel、rollback、canary、checkpoint recovery、incident replay；物理 e-stop 只能作为系统边界，不能由无证据软件 claim 替代。
8. 扩展、成本与证据：多 tenant/robot/model 的 placement 与公平性，以及哪些设计在个人项目中真实存在。

## 7. 后续 Source Queue

下表只冻结检索队列；跨卷引用可以减少重复，但不能替代每个新节点自己的 claim-level source gate。

| ID | 待冻结的来源类型 | 可复用入口 | 当前状态 |
| --- | --- | --- | --- |
| `SYS-VLA-002` | OpenPI 8 fixed files、CPython/Triton/gRPC/ROS 2 fixed docs、3个local OpenPiVLA files、14 probes | SYS-001、VOL 03 action execution、VOL 05 ENG-022/EVAL-013 | `source + knowledge + card / unseen` |
| `SYS-VLA-003` | Kubernetes scheduler/quota/lease、NVIDIA device plugin、Volcano fair-share/capacity/priority、Triton rate/model config、Ray resources/placement/Serve、ROS lifecycle 与五项目 manifests | VOL 05 ENG-016/018/019/022、五项目 inventories/ledgers | `source + knowledge + card / unseen` |
| `SYS-VLA-004` | ROS 2 lifecycle/controller/QoS、Kubernetes probes/rollback、OpenTelemetry signals、SYS-002/EVAL-008 | VOL 05 ENG-017/018/022、EVAL-008/014/020/021、VOL 04 safety/fallback | `source + knowledge + card synced / unseen` |
| `CODE-VLA-007` | ROS 2 control PID、WPILib PIDController、Feedback Systems 与 VOL 01 advanced-control review | VOL 01 `VLA-FND-036`、advanced-control fact review | `source + knowledge + card / unseen` |
| `CODE-VLA-008` | Sutton–Barto TD(0)、Gymnasium terminated/truncated semantics 与 VOL 01/VOL 02 fact reviews | VOL 01 `VLA-FND-023/027`、VOL 02 fact review | `source + knowledge + card synced / unseen` |

## 8. 项目挂钩与真实性边界

| 项目 | 可用 hook | 当前不能说 |
| --- | --- | --- |
| Robot Harness | local trainer/eval/config、metrics/raw-support/recovery manifest，可用于 offline evaluation、lineage 和 failure-evidence 讨论 | 已部署 robot fleet、online policy service、统一生产平台或真实物理安全闭环 |
| OpenPiVLA | local JSON/causal-CE、shape/formatter 风险与 official parallel serving/action contract，可用于 schema/round-trip 诊断 | formal checkpoint、controller round-trip、稳定 online rollout 或个人拥有完整 serving platform |
| OPD | point/box/text route、scorer、data/eval boundary，可用于 typed request/result 与 evaluation contract | robot policy serving、fleet scheduling 或 closed-loop physical execution |
| WAM | simulator/policy artifact 与 paired diagnostic，可用于 checkpoint/eval/rollout 失败边界 | 已完成真实机器人部署、生产 recovery 或安全系统 |
| UWM / LIBERO | simulator protocol、fixed-init 与 user-confirmed limited result，可用于 protocol identity 与 rollout schema | 跨协议生产泛化、robot fleet、可复算 checkpoint/episode bundle 或未经确认 ownership |

面试中按 `public upstream design → local evidence → local inference → unverified` 四层作答。路径、官方 example、Git author、配置字段或局部脚本都不能自动升级为个人端到端 system ownership。

## 9. VOL 08 退出条件

### 9.1 Coverage complete

1. `SYS-VLA-001..004` 与 `CODE-VLA-001..008` 全部有唯一 source/knowledge/card 三联件，卷级 registry 与索引同步。
2. 每张卡包含 stable ID、优先级/难度、短答、机制展开、来源、项目挂钩、易错点、追问和练习状态。
3. 新节点有 primary/official revision 与 claim boundary；跨卷链接不能单独支撑强事实。

### 9.2 Reviewed

1. 12 个节点的 canonical/HTML/review SHA、单 H1、层级、锚点、公式、代码、表格和本地链接通过。
2. 四个 SYS 节点逐一完成独立事实/设计边界复核；两个 CODE 学习簇各至少有一次 reference-parity review。
3. 项目 hook 只引用 evidence inventory/ownership ledger；缺 runtime、checkpoint、raw bundle 或候选人确认时保留 WARN。

### 9.3 Drilled

1. `SYS-VLA-001..004` 各完成一次限时系统设计口述，记录需求澄清、容量、API、状态、failure 与 trade-off 反馈。
2. `CODE-VLA-001..008` 各完成一次白板或 runtime 练习，记录代码、测试、复杂度、错误与复盘。
3. 只有真实回答/实现后才创建或更新 coaching state；页面覆盖与静态校验不改变 `unseen/weak/pass/strong/stale`。

### 9.4 Project truth

1. 每个 SYS 回答至少包含一个真实项目 hook，同时明确“已做 / 参与 / 可补做 / 未验证 / 不能说”。
2. 不要求虚构 fleet 或生产部署；没有直接证据时，允许把答案限定为设计方案和项目差距分析。
3. 系统设计能力与个人已落地系统是两个不同 claim，必须分别表述。

## 10. 缺口优先级与下一切片

| 优先级 | 缺口 | 原因 | 下一动作 |
| --- | --- | --- | --- |
| P0-1 | `SYS-VLA-002` knowledge | request/schema、state、timing、backpressure、real-time与truth boundary已完成教学转译 | 已完成，保持WARN |
| P0-2 | `SYS-VLA-002` card | 建立在已审knowledge上，包含短答、机制、诊断、项目 hook 与危险答案 | 已完成一张unseen卡，保持WARN |
| P0-3 | `SYS-VLA-004` oral drill | knowledge/card 已完成；需记录 incident/recovery 口述与项目边界 | 下一步进行一次真实系统设计口述 |
| P1 | `SYS-VLA-003` fleet scheduling | 价值高但依赖 serving identity、state 与 SLO 合同 | source+knowledge+card已同步，等待口述 |

下一 bounded slice：**只进行一次 `SYS-VLA-004` 系统设计真实口述**；保持 `unseen`、不修改 mastery、不创建`coaching_state.md`，不启动其他 VOL 08 节点。

## 参考入口（References）

1. [GitHub 骨架与来源入口](00_github_guidance_and_sources.md)
2. [VLA Knowledge Map](../knowledge/00_vla_knowledge_map.md)
3. [Repository Completion Audit](repository_completion_audit.md)
4. [VOL 01 Phase 0 Question List](../questions/vol_01_foundations.question_list.md)
5. [SYS-VLA-001 Source Freeze](vol_08_sys001_vla_training_eval_platform_source_freeze.md)
6. [CODE-VLA-001 Softmax Source Freeze](vol_08_code001_softmax_source_freeze.md)
7. [CODE-VLA-002 Attention Source Freeze](vol_08_code002_attention_source_freeze.md)
8. [CODE-VLA-003 Norm Source Freeze](vol_08_code003_norm_source_freeze.md)
9. [CODE-VLA-004 Masked Loss Source Freeze](vol_08_code004_masked_loss_source_freeze.md)
10. [CODE-VLA-005 Transform Source Freeze](vol_08_code005_transform_source_freeze.md)
11. [CODE-VLA-006 Planar FK Source Freeze](vol_08_code006_planar_fk_source_freeze.md)
12. [VOL 05 Completion Independent Fact Review](vol_05_completion_independent_fact_review.md)
13. [Evidence Manifest](../evidence/evidence_manifest.md)
14. [SYS-VLA-002 Policy Serving / Real-time Control Loop Source Freeze](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.md)
