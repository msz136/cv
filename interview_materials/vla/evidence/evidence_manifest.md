# VLA 项目证据总索引

> 更新日期：2026-07-21  
> 状态：`researching / projects_inventoried_5_of_5 / WAM_1epoch_evidence_frozen / WARN`  
> 原则：项目页或简历里的数字不是 raw evidence；每个强 claim 必须绑定 run、protocol、artifact 和 ownership。

## 1. 五项目覆盖

| 项目 | 风险优先级 | Inventory | Raw artifact gate | 当前结论 | 入口 |
| --- | --- | --- | --- | --- | --- |
| Cosmos / WAM | P0 | drafted / ownership-ledger / P0-audited / 1epoch-evidence-frozen | 1 个 local-direct partial bundle（CoffeePressButton manifest/trace/video；checkpoint-unverified）+ 1 epoch gate contracts/logs（完整 checkpoint 未闭合） | optimized resume 已安全降级；trace-level diagnostic、8卡 9907-step gate、step-1900 OOM 与 step-1500 state_dict 保存失败已登记；checkpoint、metric denominator、完整 episode suite 与候选人 ownership 仍 pending | [WAM Inventory](projects/wam_claim_evidence_inventory.html) / [1epoch evidence freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html) / [Ownership ledger](projects/wam_ownership_ledger.html) / [P0 audit](projects/wm019_wam_p0_bundle_audit.html) / [review](projects/wam_claim_evidence_inventory.review.json) |
| OpenPiVLA | P0 | drafted / ownership-ledger / P0-audited | 6 个 local-direct bundle；2 个 remote-referenced；1 个 archive-summary-only | Qwen JSON/causal-CE、三类 recipe、formal trainer、smoke/report/diagnostic artifacts 与 [P0 audit](projects/openpivla_p0_bundle_audit.html) 可直接核验；13-row ownership ledger 已建立，但候选人角色确认、pre-snapshot diff、97.4 raw bundle、formal checkpoint/load smoke 与 lineage 未闭合 | [Inventory](projects/openpivla_claim_evidence_inventory.html) / [Ownership ledger](projects/openpivla_ownership_ledger.html) / [P0 audit](projects/openpivla_p0_bundle_audit.html) / [Batch 2 freeze](../sources/openpivla_batch2_evidence_freeze.html) |
| Robot Harness | P0 | drafted / ownership-ledger / aggregate-gate / raw-partial / P0-audited | local-direct runtime/data/reward/eval artifacts；13/13 aggregate均值；28/40 primary与6/10 exact support；12-slot metrics/run/remote locator与 [P0 audit](projects/robot_harness_p0_bundle_audit.html) 已冻结 | 定向搜索17个同名候选但0 eligible；另4 suite缺12个raw，scorer/checkpoint lineage、真实 effect-sink 与候选人确认仍缺 | [Inventory](projects/robot_harness_claim_evidence_inventory.html) / [Ownership ledger](projects/robot_harness_ownership_ledger.html) / [P0 audit](projects/robot_harness_p0_bundle_audit.html) / [10-suite gate](projects/robot_harness_10suite_aggregate_bundle_gate.html) / [Raw/recovery manifest](projects/robot_harness_common_support_raw_bundle_manifest.html) |
| UWM / LIBERO | P1 | drafted / ownership-ledger / P0-audited / transfer-evidence-frozen | local-direct project snapshot/scripts/report；5-task final 为 user-confirmed remote summary；actionheadfix/30/100epoch/h4/convert-action 证据已冻结；raw checkpoint/episodes 仍缺 | fixed-pruned-init、reset-style、UWM Table II OOD 三套口径已拆分；74.4% 不升级为 Table II 可比复现；RoboCasa h4 0/54 与 execution A/B 只作为诊断；工作树 recovery manifest 与未跟踪 final JSON 单独标记 | [Inventory](projects/uwm_libero_claim_evidence_inventory.html) / [Transfer freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html) / [Ownership ledger](projects/uwm_libero_ownership_ledger.html) / [P0 audit](projects/uwm_libero_p0_bundle_audit.html) / [review](projects/uwm_libero_claim_evidence_inventory.review.json) / [ENG-004..006 artifact gate](../sources/vol_05_local_artifact_gate_eng004_006.html) |
| OPD / VLM Grounding | P1 | drafted / ownership-ledger / P0-audited | local-direct scripts/manifests/report tables；OPD ownership ledger 与 [P0 audit](projects/opd_p0_bundle_audit.html) 已建立；weights/raw predictions/ablation 仍缺 | 五 expert route、coldstart、OPD5000 checkpoint 曲线与 raw-holdout leakage 可核；`point/` trainer 与根目录副本已分开；`msz136`/`mousongzhe` 身份和候选人逐文件角色仍待确认；组合因果保持 WARN | [Inventory](projects/opd_claim_evidence_inventory.html) / [Ownership ledger](projects/opd_ownership_ledger.html) / [P0 audit](projects/opd_p0_bundle_audit.html) / [review](projects/opd_claim_evidence_inventory.review.json) / [ENG-004..006 artifact gate](../sources/vol_05_local_artifact_gate_eng004_006.html) |

| Cross-project PER-004 navigation gate | P0 | drafted | 0 个 local-direct VLN/ObjectNav bundle；五项目只有接口或非导航 provenance | 没有 episode/scene/navmesh/action trace/stop predicate/denominator，因此不支持个人 SR/SPL 或真机导航 | [Navigation Artifact Gate](projects/per004_navigation_artifact_gate.html) / [Markdown](projects/per004_navigation_artifact_gate.md) / [review](projects/per004_navigation_artifact_gate.review.json) |

## 2. 状态词

| 状态 | 含义 |
| --- | --- |
| `upstream-verified` | paper/official repo 支持公有机制 |
| `local-direct` | 当前工作区可直接读取 code/config/log/checkpoint/eval/episode artifact |
| `local-claim-only` | 只有简历/项目页自述，不能升级为结果证明 |
| `conflict` | run、protocol、checkpoint 或结果来源未统一 |
| `release-blocked` | 当前投递稿含未关闭的高风险 C3 表述 |

## 3. 当前切片结论

WAM inventory 已冻结 optimized/research/engineering 三版简历、项目页、resume plan、Cosmos source audit 与 benchmark audit。2026-07-18 在外部 Project outputs 发现一组 CoffeePressButton base/trained manifest、action trace、失败视频和共同 rollout log，已由 WM-019 manifest 与 paired diagnostic 登记；checkpoint binary、metric denominator、完整 episode suite、local diff 与候选人 ownership 仍未闭合。`0.90–0.95 / 0.75`、MSE 45%、official-HF 71.19% reproduction、local 0-success 与 full10k/C500 run 继续留在 evidence queue。

2026-07-17 已完成 optimized resume 安全降级：WAM bullet 不再报上述数字，也不声称 root cause 或 local closed-loop uplift；对应投递 PDF 已重建并通过 A4 单页视觉与文本检查。该动作关闭了投递 release blocker，但没有把任一本地 claim 升级为 verified。

2026-07-21 WM-019 P0 bundle audit 进一步核对了两侧 manifest、300×7 action trace、失败视频、paired MAE/RMSE 与 future-image proxy。结论保持 `PARTIAL/WARN`：checkpoint binary/hash、完整 scorer/denominator、run lineage、operator/reviewer 和候选人 ownership 仍缺；该审计只证明 diagnostic/interface evidence，不证明 uplift 或 benchmark success。同期完成 [Cosmos 1 epoch evidence freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)：冻结 8 卡/9907-step 合同、数据运行统计、step-1900 cgroup OOM 中断和 no-cycle 后 step-1500 `state_dict` 保存失败；没有把中间 loss 或官方 baseline 拼成 1 epoch 结果。

OpenPiVLA inventory 已冻结 optimized/research/engineering 简历、项目页、resume plan、VOL 03 source audits 与 frozen OpenPI official README，并审计 `C:\Users\mousongzhe\Project\openpivla_deployment` 的真实 snapshot（Project commit `c4469eb`）。official 96.85 已直接核实；Qwen3-VL + PEFT LoRA formal trainer、JSON/causal-CE action route、DROID/MindCube 三类 recipe、smoke summaries、formal report、official LIBERO launcher 与 ALOHA/LIBERO/diagnostic artifacts 均为 local-direct。ownership ledger 进一步确认 360 个 OpenPiVLA paths 一次进入 root snapshot、frozen upstream 没有 custom trainer path，并把 13 个文件/决策分层；它不证明个人逐文件原创，候选人确认和 pre-snapshot diff 仍缺。三条 100k completion 是 committed report + remote-referenced，97.4 是 archive-summary-only；checkpoint/load smoke、raw eval bundle 与 archive→formal lineage仍未闭合，因此项目保持 WARN。

Robot Harness inventory 已冻结 runtime、SFT/GRPO 数据路由、schema-aware reward、8B/32B eval 与失败域。ownership ledger 进一步明确候选人 self-attested owner/reviewer 与 Codex-primary implementation，并用 Git diff、13 个文件/决策和 8 项确认问题记录贡献边界；targeted tests 当前为 11 pass/1 config-drift fail。[五/八模型×十套件聚合证据门](projects/robot_harness_10suite_aggregate_bundle_gate.html)固定两份 overview、builder 与旧输入 SHA，13/13 mean probes、5/5 overlap 和12/12 archived run/60/60 metrics通过。后续 [raw/recovery manifest](projects/robot_harness_common_support_raw_bundle_manifest.html) 用 Windows extended path 校验28/40个primary JSONL、17,828行，并确认6/10 suite的四模型ID set/order exact；又冻结12条metrics/run/remote locator，扫描agent、Project与718-member原tar的17个同名候选，0个匹配缺失模型/rows。另4 suite缺12个primary，五种metric、不同n、新模型远端输入、统一scorer/backend与0/6本地checkpoint仍使结果保持descriptive/partial。真实 browser/robot effect-sink 与候选人确认仍未闭合，因此保持 WARN。

2026-07-21 Robot Harness P0 bundle audit 将 runtime/data/reward、aggregate arithmetic、partial raw、scorer、checkpoint、effect-sink 和 ownership 分成独立 gates。当前允许讲约束建模和协议层评估，不允许讲真实机器人成功率、严格 37.8→95.6 uplift 或全部代码的个人独立 ownership。

OPD / VLM Grounding inventory 已冻结五 expert mix、OPD student route metadata、coldstart500、student-rollout OPD5000、10k raw-holdout leakage gate、按 format/pool 的 checkpoint 曲线以及 point protocol 修正。旧版 OPD final 与新版 OPD5000 ckpt5000 已显式分开；original strict、protocol-fixed strict 和 lenient geometry 不能混报。OPD ownership ledger 已按 13 个文件/决策区分 `msz136` 初始 scaffold、`mousongzhe` 后续提交、`point/` 实际 run 版本、远端 summary 与结果资产；权重/raw predictions、统一 ablation 和候选人角色确认仍缺，因此保持 WARN。

2026-07-21 OPD P0 bundle audit 将 data route、distillation、holdout leakage、checkpoint curve、scorer/protocol、lineage、raw predictions、ablation 和 ownership 分成独立 gates。当前可讲组合路线与 protocol-bounded table，不可讲 OPD 单因果 uplift、checkpoint ownership 或静态 holdout 的机器人成功率。

UWM / LIBERO inventory 已冻结 LIBERO official route、fixed-pruned-init/reset/Table II protocol、DataLoader stall、RoboCasa contract 和 user-confirmed final。UWM ownership ledger 进一步区分 `0341c50` official repro snapshot、RoboCasa 多次提交、当前工作树 recovery 文件、未跟踪 user-confirmed JSON 与上游 UWM/LIBERO；checkpoint/normalizer/episodes、GPU A/B 和候选人角色仍缺，因此保持 WARN。

UWM / LIBERO inventory 已冻结项目 snapshot、UWM/LIBERO source audits、LIBERO-90→LIBERO-10 route、fixed-pruned-init/5-step warmup/50-task rollout、reset-style 对照、DataLoader stall smoke 和 RoboCasa 转向边界。5-task `186/250=0.744` 仅为 user-confirmed remote final；论文 Table II 的 OOD initialization/3-seed protocol 与项目 fixed-pruned-init 不同，不能直接比较；完整 checkpoint、normalizer、episode、视频、paired protocol 和 ownership 仍缺，因此保持 WARN。

2026-07-21 UWM/LIBERO P0 bundle audit 将 protocol、remote summary、paper comparability、episode bundle、DataLoader-only smoke、RoboCasa success 和 ownership 分成独立 gates。同期 [UWM/LIBERO/RoboCasa transfer evidence freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html) 固定了 actionheadfix partial load、Human300/target/teacher-forced 指标、30/100 epoch、h4 `0/54` 与 convert_action A/B，并把 committed、working-tree、user-confirmed 和 raw-local provenance 分开。当前允许讲协议工程、训练诊断和数据等待，不允许讲 local 0.744 reproduction、Table II 严格复现或 RoboCasa benchmark success。

2026-07-17 ENG-004..006 本地 Artifact Gate：当前 snapshot 可直接读取 UWM train summary、checkpoint-load report、action normalizer、DeepSpeed effective config，以及 OPD ZeRO-2/3 configs 与 final-only manifests；两个扫描根目录均没有 checkpoint binary。该 audit 提升了 metadata/config/report 证据等级，但不关闭 checkpoint、optimizer lineage、fixed-batch resume、throughput A/B 或 ownership gate。

OpenPiVLA Batch 2 source freeze 已发现并显式记录一个新的 representation conflict：recipe/public smoke 声明 `H=15,D=72`，而 current formal JSON formatter 对 action/state 使用 `limit=16`；历史 `flow_matching_loss` metadata 与 current Qwen `outputs.loss` 也属于不同证据路径。该发现不改变安全简历口径，但会约束下一批题卡和后续 parser/normalizer/controller roundtrip 补证据。

2026-07-21 OpenPiVLA P0 bundle audit 将 trainer、representation、loss mask、official-lineage、checkpoint、raw metric、parser/controller 与 ownership 分成独立 gates。当前允许讲工程接口和 shape/loss 诊断，不允许讲 97.4 verified、高于 official 96.85、FAST-equivalent 或个人 end-to-end ownership。

PER-004 Navigation Artifact Gate（2026-07-18）对五个项目和现有 evidence/inventory 做了导航字段盘点：没有 local-direct VLN/ObjectNav episode、navmesh、continuous action trace、SR/SPL denominator 或 real-navigation safety log。Robot Harness 的 semantic-navigation 只支持高层工具接口与取消/补偿设计；OPD/OpenPiVLA/WAM/UWM 分别提供 grounding、action packaging、simulator provenance 或 LIBERO protocol hook，不能升级为导航结果。

## 4. 下一步

1. 继续补 WAM run/checkpoint/metric/episode/ownership manifest；当前 CoffeePressButton bundle 只关闭“完全没有任何 diagnostic artifact”的疑问，不关闭 checkpoint/uplift gate。
2. OpenPiVLA Batch 1+2（12 张）、Robot Harness Batch 1（8 张）、OPD Batch 1 + ownership（9 张）、WAM Batch 1（2 张）与 UWM Batch 1 + ownership（2 张）已完成并保持 `unseen`；五项目 ownership ledger 均不改变 mastery state。
3. 五项目均已有 inventory；OpenPiVLA、Robot Harness、OPD、UWM 与 WAM ownership ledgers 已完成 5/5。Robot Harness 已证明aggregate arithmetic可复算，并为6/10 suite闭合四模型raw ID support；本地17个同名候选均不合格。下一步只能按12条remote locator受控恢复，或冻结统一scorer/checkpoint后做paired rescoring，不得把partial bundle升级为十套件强结论。
4. PER-004 导航 gate 保持 `WARN`；只有出现 protocol-complete episode/trajectory bundle 后，才重新计算任何 VLN/ObjectNav metric 或 ownership claim。
