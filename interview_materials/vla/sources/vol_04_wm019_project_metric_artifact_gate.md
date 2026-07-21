# VOL 04 WM-019：Project Metric Artifact Gate

> 状态：`artifact_gate / VLA-WM-019 / WARN`  
> 审查日期：2026-07-18  
> 证据截止：2026-07-18  
> 范围：只审查 UWM/LIBERO 与 Cosmos/WAM 项目材料如何支撑 WM-019 的 metric ladder、统计单位和 paired validation；不新增项目结果、不运行远端任务、不创建题卡或 coaching state。

## 问题（Question）

对于项目中出现的 MSE、proxy、simulator success 或 real success，当前工作区到底有什么 artifact 可以复核？缺什么字段才能比较两个 checkpoint 或判断 proxy 是否与 downstream success 同向？

## 证据边界与来源

本 gate 只使用以下已存在的本地材料：

1. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：记录 fixed-pruned-init、reset-style、5-task summary、协议字段和缺失的 checkpoint/episode bundle。
2. [Cosmos/WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：记录 `cv` 工作区的历史缺口、WAM claim 状态，以及 2026-07-18 外部 diagnostic artifact addendum。
3. [WM-019 Metric Source Freeze](vol_04_wm019_metric_boundary_source_freeze.html)：冻结 metric ladder、统计单位、protocol tuple 和不可外推边界。
4. [Benchmark / Evidence Audit E](vol_04_benchmark_evidence_claim_to_protocol.html)：冻结 paper/repo/checkpoint/runtime/ownership 的证据层次。
5. [WAM CoffeePressButton Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)：登记一组 base/trained action-rollout diagnostic bundle 的本地文件与缺口。
6. [WAM Action-Trace Paired Diagnostic](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html)：对同一 episode 的 base/trained JSONL 做结构和逐步差异诊断。
7. [WAM Future-Metric Paired Diagnostic](../evidence/projects/wm019_wam_future_metric_paired_diagnostic.html)：对同一离线 episode 的两个 checkpoint label 做 PSNR/SSIM 对照。
8. [WAM Matched-Checkpoint Protocol Bridge](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.html)：验证 `iter_000010000` 离线 metrics 与 trained rollout 的 checkpoint path exact equality，同时拆开两种 protocol。

本页的 `MISSING` 表示当前工作区没有足够 artifact；不代表用户远端绝对不存在文件。

## 1. Metric ladder 与项目证据层

| 层级 | 可接受的最小 artifact | 当前 UWM/LIBERO | 当前 WAM | 能否升级为个人结果 |
| --- | --- | --- | --- | --- |
| offline target fit | split、target schema、prediction/label、metric script、mask/reduction、valid count | 有部分代码/report 线索；缺完整可复算 bundle | 无本地 metric bundle | 否，保持 `WARN` |
| teacher-forced one-step | checkpoint、真实历史输入、per-offset target、预处理/normalizer hash | source/adapter 合同有；run artifact 缺失 | 无本地 run artifact | 否 |
| open-loop rollout | 自回归 trace、per-offset error、horizon、action sensitivity | inventory 明确缺 target-based per-offset metric | CoffeePressButton 已有 base/trained action trace 与 MAE/RMSE paired diagnostic，但缺 target scorer/action-sensitivity probe | `PARTIAL / WARN` |
| world/proxy score | scorer/version、generated samples、task/init、paired checkpoint | WorldGym/项目 proxy 只能作为协议框架 | WAM 历史分数为 claim-only | 否 |
| simulator closed loop | checkpoint、environment version、reset/init、controller、predicate、episode ledger | `186/250` 为 user-confirmed remote final；raw episode/checkpoint 缺失 | CoffeePressButton episode 0 manifest 有 `success=false`，但不是完整 denominator 或 checkpoint-verified run | `DIAGNOSTIC ONLY` |
| real closed loop | robot/controller/camera/latency、安全记录、episode trace | 没有 real-hardware artifact | 没有 real-hardware artifact | 否 |

## 2. 项目级 gate 结论

### 2.1 UWM / LIBERO

| Claim | 当前证据 | 状态 | 面试安全说法 | 最小补件 |
| --- | --- | --- | --- | --- |
| fixed-pruned-init `186/250=0.744` | user-confirmed final JSON、UWM inventory、项目 recovery report | `user-confirmed / protocol-limited / WARN` | “用户确认的固定项目协议结果；不能称本地 raw verified 或 Table II strict reproduction” | checkpoint/normalizer hash、exact config、init index、250 episode JSONL、success script/scorer |
| reset-style `232/250=0.928` | user-confirmed summary、source audit | `protocol diagnostic` | “reset/init 分布变化会显著改变结果；不能称模型 uplift” | 同 checkpoint paired run、逐 episode seed/init、相同 predicate |
| Book-Caddy `42/50=0.84` | committed report、远端路径记录 | `report-supported / single-task-only` | “报告记录的单任务结果” | checkpoint binary、raw episodes、run manifest |
| action/image MSE | UWM source audit、validation 语义、inventory | `metric-specific proxy` | “特定 conditional slice 的 proxy，不等于 LIBERO success” | target/prediction files、mask/reduction、per-offset report、checkpoint lineage |
| soup/mug failure hypothesis | per-task summary与 project report | `local-inference` | “接触、放置和 recovery 是待验证假设” | failure video、action trace、first-divergence label、paired rerun |

UWM 当前可达到的最高证据层是 C1/C2：能指向脚本、协议和诊断，但没有 C3 immutable bundle。UWM Table II 的 OOD initialization、object shift、背景处理和多 seed 口径不能由 `186/250` 直接替代。

### 2.2 Cosmos / WAM

| Claim | 当前证据 | 状态 | 面试安全说法 | 最小补件 |
| --- | --- | --- | --- | --- |
| action/future/value slot、routing、loss mask | Cosmos paper/repo frozen audit | `upstream-verified` | “我按 upstream contract 审计/对齐” | local diff、设计记录、ownership ledger |
| CoffeePressButton base/trained diagnostic bundle | 外部 Project 目录中的两个 manifest、两个 action trace、两条 raw video、rollout log；checkpoint 字段为远端路径 | `local-direct artifact / checkpoint-unverified / WARN` | “我复核过一个 action-rollout diagnostic bundle；它支持接口、controller、失败 trace 讨论，不支持 benchmark/uplift” | checkpoint binary/hash、output-root reconciliation、完整 episode denominator、target metric |
| held-out MSE `0.09718→0.05349` | 只出现在旧简历/项目材料 | `C3-BLOCKED / REMOVED` | 当前不主动报数 | split、metric script、prediction/label、checkpoint、复算命令 |
| task success `0.90–0.95 / 0.75` | 旧材料且与 local 0-success provenance 未闭合 | `CONFLICT / REMOVED` | 当前不报数 | run ID、checkpoint、task/init/trial、episode ledger、predicate |
| official-HF `84/118` 或 `86/120` | 项目页/旧材料，实际 bundle 缺失 | `local-claim-only` | 只能讲应如何验证官方 checkpoint harness | model revision、config/stats hash、episode/video/summary |
| local 0-success 与 root cause | 项目页中的诊断链 | `inference / WARN` | “候选原因与排查方向”，不说 root cause confirmed | checkpoint load log、action/gripper trace、修复前后 paired rerun |

WAM 当前有 `local-direct artifact / checkpoint-unverified` 的 CoffeePressButton action bundle、一组单 sample future-image PSNR/SSIM JSON，以及 `iter_000010000` 的 exact checkpoint-path bridge；但没有本地 checkpoint binary、完整 denominator、target-based action metric 或 simulator/real paired success，因此不把 WAM 历史数字放进 WM-019 的统一 success 表。

## 3. 可比性合同（Protocol Tuple）

两个结果 (m_a,m_b) 只有在下列字段一致或被显式分层时，差异才可以主要归因于模型：

```text
(run_id, checkpoint_sha, processor/normalizer_sha,
 split/target_schema, metric_script_sha, mask/reduction,
 task/suite, init_index, seed, horizon, chunk/replan,
 camera/preprocess, controller, scorer/environment_version,
 success_predicate, valid_denominator)
```

缺少任何高影响字段时，面试回答应把结论降级为 `protocol-limited` 或 `WARN`。相同任务名、相同平均分或同一个 success 词不能替代这个 tuple。

## 4. Paired validation 最小矩阵

| 对照 | 固定字段 | 输出 artifact | 当前状态 |
| --- | --- | --- | --- |
| teacher-forced vs open-loop | checkpoint、输入历史、horizon、normalizer | per-offset error、drift、valid count | `PENDING` |
| action sensitivity | observation、action perturbation、seed | future delta、contact/task probe | `PENDING` |
| proxy vs simulator | checkpoint、task/init、scorer、predicate | paired rank/correlation、failure table | `PENDING` |
| reset-style vs fixed-pruned-init | checkpoint、controller、episode budget | 每 episode init/seed、success、CI | `PENDING` |
| simulator vs real | controller、camera、latency、安全停止 | episode trace、failure taxonomy、recovery | `PENDING` |

最小的 episode ledger 至少包含：`episode_id/task/init/seed/checkpoint_sha/protocol_sha/predicate/success/failure_code/trace_path`。只有均值或截图，没有 ledger，不能完成 denominator audit。

## 5. 个人项目真实性边界

- UWM：可以讲协议固定、LIBERO adapter、strict/reset 对照、DataLoader stall 诊断和失败分析；`186/250` 必须称为 user-confirmed/protocol-limited，不能称本地复算或论文复现。
- WAM：可以讲 Cosmos Policy 的 upstream 机制、评估合同和失败诊断框架；当前不能讲本地 MSE、success、uplift 或 root cause 已被 artifact 证明。
- 两个项目都不能把 paper/repo 机制、Git author、协作实现或工具辅助生成写成个人原创 architecture。

## 6. 当前 gate 与下一步

当前 verdict 为 `WARN`：UWM 有可用的协议与 summary 证据，但缺 C3 bundle；WAM 有一组诊断 artifact，但仍缺 checkpoint、metric、denominator 与 ownership 闭环。该 gate 不改变 197 张题卡的 `unseen` 状态，也不创建 coaching state。

下一 bounded slice 只能二选一：

1. 继续补齐 WAM diagnostic bundle 的 checkpoint、output-root reconciliation、denominator 和 target metric fields，或在 UWM raw artifact 出现后按本页 tuple 建立其 manifest；或
2. 进行一题 `VLA-WM-015..019` 真实口述，并把回答记录到训练状态。

在 artifact 或真实回答出现前，不生成 WM-020..038，不升级任何项目数字或题卡 mastery。

## 参考来源（References）

1. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
2. [Cosmos/WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
3. [WM-019 Metric Source Freeze](vol_04_wm019_metric_boundary_source_freeze.html)。
4. [Benchmark / Evidence Audit E](vol_04_benchmark_evidence_claim_to_protocol.html)。
5. [EVAL-003 statistical source freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。
