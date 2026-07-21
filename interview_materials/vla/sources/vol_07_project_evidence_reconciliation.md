# VOL 07：五项目证据、Ownership 与面试叙事 Reconciliation

> 状态：`project_evidence_reconciliation / VOL-07 / inventories_5_of_5 / ownership_ledgers_5_of_5 / p0_audits_5_of_5 / cards_37_unseen / WARN`  
> 审查日期：2026-07-21  
> 范围：只汇总五个项目现有的 claim–evidence inventory、ownership ledger、诊断 artifact 与项目题卡；本轮补入 UWM RoboCasa ActionHeadFix 30-epoch P0 audit（此前已纳入 Cosmos full10k trained 24×5 P0 audit），但不改变 280 张题卡的 `unseen` 状态、不创建 `coaching_state.md`，也不把 summary、Git 作者或上游机制升级为个人贡献。

## 问题（Question）

五个项目目前分别有不同强度的代码、配置、报告、远端引用和诊断 artifact。怎样把它们统一成一套可面试复述的证据合同：每个 claim 的来源是什么、候选人能说到哪一层、还缺什么 P0 artifact、如何回答高压追问？

## 1. 结论先行

1. **五个项目的 claim inventory 与 ownership ledger 均已存在**，但它们解决的是“登记与边界”，不是“所有项目结果已证实”。
2. **项目题卡共 37 张**：OPD 9、OpenPiVLA 12、Robot Harness 8、WAM 4、UWM/LIBERO 4；全部保持 `unseen`。
3. **证据强度不对称**：OpenPiVLA 的 local-direct 代码/recipe 最完整；Robot Harness 有较多工程与 raw partial bundle；OPD 有静态数据/评估链；UWM 有 user-confirmed remote final 但无 raw checkpoint/episode bundle；WAM 只有有限诊断 artifact，历史强结果已安全降级。
4. **所有项目都必须使用四层叙事**：`public upstream mechanism → local evidence/interface → inference → unverified`。其中 inference 不能被口述成 measured result，unverified 不能被包装成 ownership。
5. **五项目 P0 audit coverage 已完成 5/5，但 P0 closure 尚未完成**：WAM、OpenPiVLA、Robot Harness、OPD、UWM/LIBERO 均有独立 P0 审计页；这些页面确认了现有证据和缺口，不等于 checkpoint/raw/scorer/ownership 已闭合。VOL 07 仍缺候选人逐文件 ownership 确认、P0 immutable bundle、真实口述和项目级 matched evaluation，因此 verdict 继续为 `WARN`。

## 2. 统一证据合同

### 2.1 Claim 的四层标签

| 层级 | 可以说什么 | 不可以说什么 | 最小证据 |
| --- | --- | --- | --- |
| `public_upstream` | 论文、官方 repo 或官方配置定义的机制 | 把机制说成自己设计或自己的结果 | 固定版本 URL/commit + 可定位文件 |
| `local_evidence` | 本地代码、配置、日志、manifest、trace 实际显示的内容 | 从文件名、Git author 或 summary 推断完整 ownership | 文件路径、SHA、字段、运行/生成关系 |
| `inference` | 基于局部证据提出的诊断或设计解释 | 把假设写成 root cause、uplift 或 benchmark | 明确假设、反例、待验证实验 |
| `unverified` | 当前缺失或冲突的 checkpoint、raw bundle、角色确认 | 在面试中用“应该/大概/项目里有”填空 | 明确缺口、下一步 artifact |

### 2.2 叙事最小单元

每个项目的 2 分钟回答都按以下顺序组织：

1. **问题与约束**：任务、输入输出、时间/算力/安全约束；
2. **个人边界**：我直接改动/验证/决策的文件或接口；
3. **机制**：数据、模型、loss、评估或部署环节的因果链；
4. **证据**：可复核 artifact、协议、分母和失败样本；
5. **反例与下一步**：当前不能证明什么，以及若继续工作要补的最小实验。

没有第 4 步的 raw evidence 时，应主动降级为“设计/接口/诊断经验”，不要补造数字。

## 3. 五项目 Reconciliation Matrix

| 项目 | Inventory / ownership | 当前可核验的 local evidence | 当前安全叙事 | P0 缺口 | 题卡覆盖 |
| --- | --- | --- | --- | --- | --- |
| **OpenPiVLA / OpenPI / LIBERO / MACA** | [claim inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/openpivla_ownership_ledger.html)；[P0 audit](../evidence/projects/openpivla_p0_bundle_audit.html) | formal trainer、Qwen3-VL + PEFT LoRA、JSON/causal-CE、DROID/MindCube recipe、smoke/report/diagnostic artifacts；部分 bundle 为 remote-referenced 或 archive-summary-only | 可以讲数据/格式/训练器/解析器的实现边界，以及如何做 formal-vs-smoke 分层 | immutable checkpoint、raw benchmark denominator、archive→formal lineage、processor/normalizer/controller round-trip、逐文件 ownership | `PROJ-OPENPIVLA-001..012`，12 unseen |
| **Robot Harness** | [claim inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/robot_harness_ownership_ledger.html)；[P0 audit](../evidence/projects/robot_harness_p0_bundle_audit.html)；[raw manifest](../evidence/projects/robot_harness_common_support_raw_bundle_manifest.html) | tool schema、PydanticAI/runtime、mutex/cancel/compensation、SFT/GRPO-style 路由、reward/constraint 设计；raw recovery 28/40，common support 6/10 | 可以讲问题定义、约束取舍、数据/reward/eval 设计与 Codex 协作边界；不能把 proxy 100% 当物理成功 | 余下 raw files、checkpoint identity、matched scorer/holdout、cancel/fallback trace、角色与实现分工确认 | `PROJ-HARNESS-001..008`，8 unseen |
| **OPD / VLM Grounding** | [claim inventory](../evidence/projects/opd_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/opd_ownership_ledger.html)；[P0 audit](../evidence/projects/opd_p0_bundle_audit.html) | tagged point/box/text SFT→generation→parser/scorer、teacher/route、raw-holdout 10k 与 checkpoint-5000 邻接证据；静态 processor/geometry 风险 | 可以讲数据路由、teacher/student、parser/scorer 和 protocol 选择；组合收益不能归因于单一 OPD 因素 | weights/optimizer/RNG、统一 ablation、raw prediction bundle、point protocol fixed scorer、账号身份与逐文件 ownership | `PROJ-OPD-001..009`，9 unseen |
| **Cosmos Policy / WAM / RoboCasa** | [claim inventory](../evidence/projects/wam_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/wam_ownership_ledger.html)；[P0 audit](../evidence/projects/wm019_wam_p0_bundle_audit.html)；[artifact manifest](../evidence/projects/wm019_wam_artifact_manifest.html)；[full10k trained eval](../evidence/projects/cosmos_policy_full10k_trained_eval_p0_audit.html)；[official-HF baseline](../evidence/projects/cosmos_policy_robocasa_baseline_p0_audit.html)；[save-load gate](../evidence/projects/cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html) | CoffeePressButton episode-0 base/trained manifest、action trace、未来帧诊断、DeepSpeed save gate、full10k trained 24×5 raw/trusted summary、official-HF baseline audit；不同 run family 分层 | 可以讲 slot/mask/loss、失败 trace、保存门、eval harness 与 raw/trusted denominator；不能把 official `84/118` 归为本地训练，或恢复历史 uplift/root-cause 强 claim | binary checkpoint、fresh reload、完整 episode/metric denominator、matched scorer、训练/rollout lineage、candidate ownership | `PROJ-WAM-001..004`，4 unseen |
| **UWM / LIBERO** | [claim inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/uwm_libero_ownership_ledger.html)；[P0 audit](../evidence/projects/uwm_libero_p0_bundle_audit.html)；[ActionHeadFix 30-epoch audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) | LIBERO route、fixed-pruned-init/reset-style 协议、DataLoader stall smoke；RoboCasa一条8卡3930-step run与8×54 raw rollout已冻结，full-h4 `0/54`/contact `45/54`；`186/250`仍为user-confirmed remote final | 可以讲 protocol 对齐、数据/normalizer/评估口径、train→closed-loop 断层和 failure diagnosis；strict/reset/official与相邻RoboCasa run不能混比 | produced checkpoint binary/fresh reload、LIBERO 250 episodes、RoboCasa env/scorer revision/videos、matched repeat、角色确认 | `PROJ-UWM-001..004`，4 unseen |

## 4. 项目间共性风险

### 4.1 结果分母与 protocol

任何成功率、准确率、SPL、point hit 或 proxy 分数都必须绑定：

`metric = (checkpoint, dataset/scene split, init/reset, seed, horizon, scorer, denominator, invalid policy)`。

只要其中一项来自另一条实验链，回答就应改成“不可直接比较”。尤其是：

- UWM `186/250` 不等于官方 Table II 或真机成功；
- OpenPiVLA `97.4%` 缺 raw denominator 时不计算 CI；
- OPD 10k 是 metric-specific holdout unit，不是 robot rollout success；
- Robot Harness proxy 100% 不是 physical safety 或 browser-complete；
- WAM trace geometry 不是训练 uplift。

### 4.2 Ownership 证据

以下材料不能单独证明个人贡献：Git author、文件名、目录位置、远端 summary、上游 repo、自动生成报告、协作工具默认提交者。安全回答应拆成：

```text
我能直接指向的改动/决策
→ 我实际验证过的输入输出或 trace
→ 我根据证据做出的推断
→ 仍需本人/团队确认的 ownership 或结果
```

### 4.3 失败诊断顺序

五个项目统一采用 `symptom → first verified divergence → root-cause hypothesis → recovery/next experiment`。如果没有 raw trace，只能停在 `unknown / not recomputable`，不能用时间先后、日志摘要或“训练完成”替代 first divergence。

## 5. 面试高压追问入口

| 追问 | 安全回答骨架 |
| --- | --- |
| “你具体改了哪几个文件？” | 先给可定位的 local-direct 文件与接口，再说明协作/上游/远端部分；不能用 Git author 代替 ownership |
| “这个数字是你跑的吗？” | 说清 local-direct、user-confirmed、remote-referenced、archive-summary-only 四类 provenance；缺 raw bundle 就不称为可复现本地结果 |
| “为什么不是数据配比导致的？” | 给 matched ablation 设计、固定 checkpoint/seed/denominator；当前没有就承认 inference |
| “失败根因是什么？” | 指出 first verified divergence；没有 trace 就保留 unknown，并给最小补证实验 |
| “你如何证明上线安全？” | 说 schema/constraint/logging/fallback 设计与实际 safety audit 的差别；不把 simulator/proxy/上游机制当真机安全 |
| “如果重做一次会先做什么？” | 选择一个 P0 immutable artifact：checkpoint hash、raw episode JSONL、matched scorer、seed/init manifest 或 ownership confirmation |

## 6. 面试回答模板（不含虚构数字）

### 6.1 30 秒总述

> 我把项目回答拆成问题约束、我直接负责的接口或决策、机制链和可复核证据四层。现在五个项目都有 claim inventory 和 ownership ledger，但证据强度不同：OpenPiVLA 偏代码/recipe，Harness 偏工程与 partial raw bundle，OPD 偏静态数据和 scorer，UWM 有 protocol-limited remote result，WAM 主要是 diagnostic artifact。没有 checkpoint、raw episode、matched denominator 或逐文件确认的地方，我会明确说是 inference 或 unverified，不把上游机制和 summary 写成个人结果。

### 6.2 2 分钟展开

> 先固定任务输入输出、split/init/seed/horizon/scorer，再定位我实际改动或验证的文件。然后沿 data→model/loss→parser/controller→evaluation trace 解释机制；结果只引用带 checkpoint、分母和 raw artifact 的记录。遇到失败，我先找 first divergence，再区分数据、表示、几何/时间、模型、控制和协议问题。当前缺少 immutable bundle 的项目，我会把答案收敛到接口设计、诊断方法和下一步补证，而不是声称 uplift、sim-to-real 或安全闭环已经完成。

## 7. 退出条件与下一步

本切片完成了五项目的统一 reconciliation，但 G09 仍未完成。退出条件还包括：

1. 候选人逐文件 ownership 确认；
2. 每个高风险项目至少一个 P0 immutable bundle；
3. 一题真实项目口述与追问记录；
4. 对关键数字建立 checkpoint/protocol/denominator 对齐；
5. 不把本页 coverage 当作 mastery。

下一 bounded slice：优先进行一题项目口述（建议 WAM 或 OpenPiVLA），或在用户提供新 artifact 后只审计一个 P0 bundle；不批量新增项目题卡。

## References

1. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
2. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html) 与 [Raw Bundle Manifest](../evidence/projects/robot_harness_common_support_raw_bundle_manifest.html)。
3. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 与 [Ownership Ledger](../evidence/projects/opd_ownership_ledger.html)。
4. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[Ownership Ledger](../evidence/projects/wam_ownership_ledger.html) 与 [WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
5. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html) 与 [P0 Audit](../evidence/projects/uwm_libero_p0_bundle_audit.html)。
6. [五项目 P0 Artifact Intake Contract](../evidence/p0_artifact_intake_contract.html)。
6. [VOL 04 Audit C Cosmos/WAM](vol_04_cosmos_policy_wam_independent_fact_review.html) 与 [Audit D Sim2Real](vol_04_sim2real_independent_fact_review.html)。
