# VOL 07：五项目 P0 Artifact Intake Contract

> 状态：`p0_intake_contract / five_projects / candidate_confirmation_pending / WARN`  
> 目的：把“项目有材料”收敛成可复核的 checkpoint、run、metric、raw output 与 ownership 入口；本页是 intake contract，不是任何项目结果的证明。  
> 证据边界：`public upstream mechanism → local evidence/interface → inference → unverified`。没有 immutable bundle 时，数字只能保持 protocol-limited 或 unverified。

## 1. 为什么需要一个统一的 P0 contract

五个项目已经有 claim–evidence inventory 和 ownership ledger，但各自的缺口字段不同。如果直接从项目 summary 生成面试答案，会把 archive、远端结果、上游机制和本地运行混成一条叙事。本 contract 只解决一个问题：**一份结果在进入强面试回答前，最低需要哪些可定位证据。**

P0 不代表“结果一定好”，而代表“结果可以被重新定位、解释和复核”。缺任一关键字段时，结果降级为 `PARTIAL` 或 `UNVERIFIED`，不会自动进入简历强 claim、题卡 mastery 或 `coaching_state.md`。

## 2. Promotion gate

| 状态 | 含义 | 面试可用范围 |
| --- | --- | --- |
| `MISSING` | 只有 summary、截图或口头记忆，没有可定位 artifact | 只能说问题定义或计划 |
| `PARTIAL` | 有代码/配置/报告/诊断，但 checkpoint、raw output、分母或 ownership 未闭合 | 可讲接口、机制、诊断和限制；数字必须带协议限定 |
| `ELIGIBLE` | 关键 hash、run lineage、protocol tuple、raw output、scorer、ownership 均可定位 | 可讲该 bundle 支持的结果，不外推到其它 run |
| `REJECTED` | hash、协议、结果或 provenance 冲突，或 artifact 无法解释 | 不得用于强回答，保留为失败审计记录 |

### 2.1 最小字段合同

一条可提升的 metric 必须绑定：

```text
metric = (checkpoint_sha, parent_checkpoint_sha, code_sha, config_sha,
          data_split, init_or_reset, seed, horizon, scorer_sha,
          denominator, invalid_policy, raw_output_locator, owner_verdict)
```

其中 `raw_output_locator` 至少能定位 episode/prediction 级别文件；只有 aggregate summary、视频截图或 Git author 不足以通过 P0。

## 3. 统一 intake schema

下面的 YAML 是提交新 bundle 时的最小模板。未知字段必须写 `unknown`，不能用推测值填空。

```yaml
bundle_id: "PROJECT-YYYYMMDD-run-name"
project: "openpivla | robot_harness | opd | wam | uwm_libero"
claim_ids: ["PROJECT-CL-..."]
provenance: "local-direct | user-confirmed-remote | remote-referenced | archive-summary-only"
status: "MISSING | PARTIAL | ELIGIBLE | REJECTED"
lineage:
  code_sha: ""
  config_sha: ""
  data_manifest_sha: ""
  scorer_sha: ""
  checkpoint_sha: ""
  parent_checkpoint_sha: ""
  run_id: ""
  hardware_or_runtime: ""
  created_at: ""
protocol:
  dataset_or_suite: ""
  split_or_pool: ""
  init_or_reset: ""
  seed: ""
  horizon: ""
  controller_or_decoder: ""
  success_predicate: ""
  denominator: ""
  invalid_policy: ""
artifacts:
  raw_episode_or_prediction_jsonl: ""
  per_sample_scores: ""
  aggregate_report: ""
  videos_or_traces: ""
  load_smoke_log: ""
ownership:
  design_decisions: "candidate-confirmation-pending"
  implementation_files: "candidate-confirmation-pending"
  collaboration_or_tool_assistance: "candidate-confirmation-pending"
  operator: "unknown"
  reviewer: "unknown"
review:
  checked_by: ""
  checked_at: ""
  first_divergence: ""
  contradictions: []
  allowed_claim: ""
  forbidden_claims: []
```

## 4. 五项目当前 intake 矩阵

| 项目 | 当前状态 | 已有可核验入口 | 最小下一件 P0 artifact | 当前可说 | 当前不可说 |
| --- | --- | --- | --- | --- | --- |
| [OpenPiVLA](projects/openpivla_claim_evidence_inventory.md) | `PARTIAL` | trainer、recipe、JSON/CE、shape/diagnostic、部分 report | formal checkpoint + parent lineage + generation/parser round-trip +逐文件 ownership | 数据格式、trainer/loss、recipe 和诊断接口 | local 97.4、优于 official、formal rollout 已验证 |
| [Robot Harness](projects/robot_harness_claim_evidence_inventory.md) | `PARTIAL` | tool schema、runtime、SFT/GRPO 路由、partial raw bundle | 同 protocol base/SFT/GRPO lineage + raw prediction/per-sample scorer + cancel/fallback trace | 约束设计、工具协议、reward/eval 设计 | 真实机器人闭环成功率、同 scorer 的因果 uplift |
| [OPD / VLM Grounding](projects/opd_claim_evidence_inventory.md) | `PARTIAL` | 数据构建、五 expert、route metadata、raw-holdout aggregate | base/coldstart/OPD5000 immutable lineage +统一 10k raw predictions + ablation | 数据路由、teacher/student、parser/scorer、协议选择 | 单独归因 OPD 带来的全部提升、real-robot success |
| [Cosmos Policy / WAM](projects/wam_claim_evidence_inventory.md) | `PARTIAL` | CoffeePressButton manifest、action trace、未来帧诊断、path bridge | checkpoint/hash + metric script + denominator + paired rerun + ownership | slot/mask/loss 公开机制、失败 trace 与诊断过程 | 0.90–0.95、MSE uplift、71.19% 或 root-cause 定论 |
| [UWM / LIBERO](projects/uwm_libero_claim_evidence_inventory.md) | `PARTIAL` | route、fixed-pruned-init/reset-style protocol、normalizer/load metadata、smoke | checkpoint + exact config/normalizer + 250 episode JSONL + init/seed manifest | protocol 对齐、DataLoader stall 诊断、失败分类 | 复现论文 0.79、官方/strict/reset 三种结果混比 |

“当前状态”是审计状态，不是候选人能力评分；五行都保持 `WARN`，直到用户提供 artifact 或逐文件 ownership 确认。

## 5. Intake 顺序：一次只收一个 bundle

每次只处理一个项目的一份 P0 bundle，顺序固定为：

1. 先冻结 bundle locator 和所有 SHA；
2. 再冻结 protocol tuple 与 denominator；
3. 再验证 raw output / scorer 能否重算 aggregate；
4. 再记录 first divergence、失败分类和限制；
5. 最后由候选人确认逐文件 ownership、operator、reviewer 和工具协作边界；
6. 只有上述字段闭合，才允许把对应 claim 从 `PARTIAL` 提升到 `ELIGIBLE`。

不允许用“文件名看起来像 checkpoint”“Git commit author”“远端 summary”“单 episode 视频”替代上述步骤。

## 6. 与面试训练的连接

P0 bundle 通过前，题卡保持 `unseen`。通过后也不会自动变成 `strong`；它只为以下回答提供证据入口：

- `What did you personally implement?`：读取 `ownership.implementation_files` 和 local diff；
- `Which number can you defend?`：读取 `protocol`、`denominator`、`scorer_sha` 和 raw output；
- `How did you debug the failure?`：读取 `first_divergence`、trace 和 paired rerun；
- `What would you do next?`：读取 `forbidden_claims` 与仍缺失的 P0 字段。

真实口述仍需单独收集；示范回答不能替代候选人 transcript，也不能创建 coaching state。

## 7. 当前边界与下一入口

- 本页没有新增任何个人结果、ownership 或 mastery 状态。
- 本页只建立五项目共用的 intake contract；现有 inventory、ledger 和题卡仍是各项目事实的来源。
- 当前最小下一步是：提交一份 WAM CoffeePressButton bundle，或直接完成 `PROJ-WAM-001` 的真实口述；两者只选其一，不能用 summary 代替。

## References

1. [VOL 07 五项目证据 Reconciliation](../sources/vol_07_project_evidence_reconciliation.md)
2. [WAM claim–evidence inventory](projects/wam_claim_evidence_inventory.md)
3. [OpenPiVLA claim–evidence inventory](projects/openpivla_claim_evidence_inventory.md)
4. [Robot Harness claim–evidence inventory](projects/robot_harness_claim_evidence_inventory.md)
5. [OPD claim–evidence inventory](projects/opd_claim_evidence_inventory.md)
6. [UWM/LIBERO claim–evidence inventory](projects/uwm_libero_claim_evidence_inventory.md)
