# VLA 面试仓库 Completion Audit：覆盖、审查与训练状态分离

> 审计日期：2026-07-21  
> 状态：`repository_reconciled / coverage_not_mastery / WARN`  
> 审计对象：`knowledge/`、`questions/`、`sources/`、`evidence/` 中的 canonical Markdown、生成 HTML、review JSON，以及总路线图和索引。  
> 核心边界：本报告只证明仓库中“有什么、是否同步、处于什么审查状态”；不把页面覆盖、事实复核候选或静态校验升级为候选人的口述掌握。

## 问题（Question）

当前仓库到底完成了多少？八卷的“内容覆盖”“事实审查”“项目证据”“生成完整性”和“真实训练”是否被混成了一个完成度数字？

## 1. 结论先行

1. 全局题库有 **280 个唯一 stable ID**，没有重复 ID；状态分布为 `unseen=280`、其余为 0。
2. VOL 01–05 已达到各自当前计划内的知识/题卡覆盖；VOL 06 已冻结20节点合同，source/knowledge/card为20/20/20，PER-001..020三联件同步且unseen；VOL 07完成五项目inventory/ownership、37张项目卡与Robot Harness aggregate + partial-raw gate；VOL 08已冻结12节点合同，sources/knowledge/card为12/12/12，`SYS-VLA-004` 三联件已同步但尚未口述。因此“八卷都有产物”不等于“八卷达到退出条件”。
3. 五项目 Claim–Evidence Inventory 为 5/5，Ownership Ledger 为 5/5；候选人角色确认、checkpoint/benchmark lineage 和若干 raw bundle 仍是 `PENDING/WARN`。
4. 创建本报告前的审计快照共有286份非README、非question-list的Markdown，其中283份有三联件；后续registry/source/knowledge/card/review切片持续闭合生命周期，VOL 07 五项目 evidence reconciliation、口述队列、五项目 model answers、readiness audit、P0 artifact intake contract、ownership confirmation queue、五项目 P0 bundle audit、Cosmos 1 epoch evidence freeze、WAM full10k run reconciliation、official-HF RoboCasa baseline P0 audit、Cosmos full10k trained 24×5 P0 audit、TurnOffMicrowave trained-failure P0 audit、Checkpoint save-load gate P0 audit、UWM/LIBERO/RoboCasa transfer evidence freeze、UWM RoboCasa ActionHeadFix 30-epoch P0 audit、OpenPiVLA Runtime Rollout Artifact Gate、LIBERO Checkpoint Load–Serve–Client Lineage Gate、ALOHA Action-Level Eval Load Gate、Official Checkpoint Immutable Manifest Gate、LIBERO Matched Failure Probe Readiness Gate 与 UWM `libero_90.pt` 本地 Immutable Checkpoint Manifest Gate 加入后，当前为 **387份canonical、387份三联件**。所有当前canonical均有HTML与review。
5. 当前387份review JSON均可解析；verdict分布为`WARN=377`、`PASS WITH WARNING=10`、`PASS=0`。十份`PASS WITH WARNING`只表示相应独立事实复核切片通过且仍有warning，不代表整卷完成。
6. `coaching_state.md` 不存在。没有候选人真实回答前，本仓库不得改变 mastery，也不得从 `unseen` 推导出 `pass/strong`。

## 2. 审计口径

### 2.1 题卡与卷归属

- 只统计 `<details class="qa">` 的 `<summary>` 中 `<b>stable-id</b>`；正文引用、路线图历史数字和 question list 不计题卡。
- 卷映射使用前缀：`VLA-FND`、`VLA-RL`、`VLA-ARCH/VLA-ACT`、`VLA-WM`、`VLA-ENG/VLA-EVAL`、`VLA-PER`、`PROJ-*`、`SYS-VLA/CODE-VLA`。
- 每张卡的练习状态从卡内最后一个 `练习状态` 字段读取。

### 2.2 知识覆盖

- VOL 03–06、VOL 08 可用 stable ID 对 knowledge canonical 与题卡集合做一一对账。
- VOL 01/02 的早期 consolidated knowledge 页面没有逐节点 stable ID 标记，因此依据对应 completion/fact review、题卡 review 与 consolidated knowledge review 交叉确认，不伪造 ID-level knowledge mapping。
- VOL 07 的知识载体是五项目 inventory、ownership ledger、项目页与原子题卡，不把它硬算成通用 knowledge node。

### 2.3 生成与审查

```text
canonical Markdown
  -> HTML source SHA
  -> review JSON source SHA
  -> structure / ID / link checks
  -> oral drill（只有候选人真实回答后才发生）
```

三联件完整只说明文件生命周期闭合；`WARN`、缺本地 artifact 或没有口述时，模块不能进入 `drilled/done`。

## 3. 八卷权威矩阵

| 卷 | 当前内容覆盖 | 题卡 | 事实/证据门 | 训练状态 | 对退出条件的判断 |
| --- | --- | ---: | --- | --- | --- |
| VOL 01 Foundations | consolidated knowledge + 39-card completion reconciliation | 39 | fact-reviewed candidate；local runtime 仍 WARN | 39 unseen | 覆盖完成；未 drilled |
| VOL 02 IL / RL / Post-training | consolidated knowledge + 40-card fact review | 40 | public facts 与 local GRPO boundary 已核对；project/run gate 仍 WARN | 40 unseen | 覆盖完成；未 drilled |
| VOL 03 VLA / Action | knowledge/cards 44/44；Audit A–F public facts 已独立复核 | 44 | local checkpoint、normalizer、controller、latency、ownership 仍 WARN | 44 unseen | 覆盖与 public-fact review 完成；未 drilled |
| VOL 04 World Model / Sim2Real | aggregate knowledge/cards 44/44；Audit A–E independently reviewed | 44 | Audit D重新获取10份fixed PDF（124页/0空白页）、官方源码/文档并完成12/12 probes；五项目真实硬件、checkpoint/result/ownership gate 仍 WARN | 44 unseen | 覆盖与public-fact review完成；未 drilled |
| VOL 05 Engineering / Evaluation | knowledge/cards 44/44；completion audit 已有 | 44 | source/doc review 完成到当前范围；五项目强指标 artifact gate 仍 WARN | 44 unseen | 覆盖完成；未 drilled |
| VOL 06 Perception / Grounding / Nav | planned `VLA-PER-001..020`；source/knowledge/card 20/20/20 | 20 | PER-001..020三联件已同步；PER-019冻结Habitat/VLN-CE指标、split、denominator、failure taxonomy与10 probes；PER-020冻结robustness/safety、risk gate、fallback/recovery/E-stop与10 probes，并完成独立事实复核；本地无navigation episode bundle/ownership或shifted-input safety bundle | 20 unseen | source 100%，knowledge 100%，card 100%；仍缺至少8次真实drill |
| VOL 07 Project Deep Dives | inventories 5/5 + ownership ledgers 5/5 + cross-project evidence reconciliation + Robot Harness aggregate/raw/recovery gates + project cards | 37 | 28/40 primary、6/10 exact support；12-slot metrics/run/remote locator已冻结；17个本地/tar候选0 eligible，统一scorer/checkpoint/candidate role仍PENDING | 37 unseen | evidence skeleton与P0 recovery contract完成；2分钟叙事/口述未闭环 |
| VOL 08 Coding / System Design | planned `SYS-VLA-001..004` + `CODE-VLA-001..008`；source/knowledge/card 12/12/12 | 12 | SYS-004 三联件已同步；真实口述仍未做 | 12 unseen | source/knowledge/card 100%，4次SYS口述与8次CODE练习均未做 |

全局题卡算式：`39 + 40 + 44 + 44 + 44 + 20 + 37 + 12 = 280`。

## 4. 项目证据与真实性边界

| 项目 | Inventory | Ownership Ledger | 项目题卡 | 当前能安全证明 | 仍不能升级的主张 |
| --- | --- | --- | ---: | --- | --- |
| OpenPiVLA | 有 | 有 | 12 | local JSON/causal-CE route、`H=15,D=72` 与 formatter `limit=16` contract 风险；官方 `pi05_libero` load/connect 与 `pi0_aloha_sim` load + 4×50×14 offline action L1 已冻结 | private formal checkpoint、immutable binary manifest、97.4 lineage、FAST 实际调用、matched controller/scorer 与个人 ownership |
| Robot Harness | 有 | 有 | 8 | local trainer/eval/config；13/13 mean、60/60 metrics；28/40 primary、6/10 exact support；12-slot remote locator与17-candidate rejection audit | 剩余12 raw、统一scorer/backend、122B/35B输入、checkpoint binary、真实物理成功或未经确认的全面主导 |
| OPD | 有 | 有 | 9 | point/box/text、coldstart、已有 report/run 边界 | 缺 weights/raw predictions/严格 ablation 时的强效果 claim |
| WAM | 有 | 有 | 4 | 已登记 artifact 与 paired diagnostics；full10k trained 24×5 raw/trusted eval、official-HF 24×5 raw/trusted eval、TurnOffMicrowave local 1k first-divergence 和 DeepSpeed save/load gate 均已独立冻结 | 本地 checkpoint binary/hash、fresh-process reload、matched 5-frame fix→rerun、multi-episode scorer/version、完整 episode JSONL、因果 uplift、候选人角色确认 |
| UWM / LIBERO | 有 | 有 | 4 | LIBERO protocol/fixed-pruned-init与user-confirmed final限定叙述；UWM base `libero_90.pt` 已有独立本地 hash gate；RoboCasa actionheadfix一条3930-step run及8×54 raw rollout已冻结 | base hash 与旧 load report 的 shared run identity、LIBERO target/fine-tune checkpoint/250 episodes；RoboCasa produced checkpoint、env/scorer/videos、matched repeat与未经确认ownership |

Git author、上游论文/仓库、官方 example、路径或 smoke report 都不自动等于候选人个人贡献；当前所有 ownership ledger 仍需候选人确认。

## 5. 文件生命周期审计

| 目录 | Canonical Markdown | HTML | Review JSON | 完整三联件 |
| --- | ---: | ---: | ---: | ---: |
| `knowledge/` | 98 | 98 | 98 | 98 |
| `questions/` | 104 | 104 | 104 | 104 |
| `sources/` | 141 | 141 | 141 | 141 |
| `evidence/` | 30 | 30 | 30 | 30 |
| `practice/` | 9 | 9 | 9 | 9 |
| 合计 | 387 | 387 | 387 | 387 |

VOL 02/03/04 的早期 source-plan registry 均已 reconciliation 并生成 HTML/review；当前不存在 registry-only 或缺三联件例外。生命周期闭合只说明 canonical、render 和 review 同步，不代表事实门、local evidence、visual QA 或口述门完成。

本轮确认 renderer 的 source SHA 按 UTF-8 文本规范化换行计算，不能用原始 CRLF 文件字节 hash 制造“stale SHA”假阳性；历史同步修复包括三份旧式 12 位 review SHA、一份 63 位 review SHA、两处遗留 U+0008、WAM一处U+000C `\frac`与七个inline MathJax span，以及VOL 01/02重复手写目录。本次340页全量校验继续要求零控制字符、公式delimiter平衡与`.formula em=0`；修复不改变技术结论、verdict或mastery。

## 6. Review 与训练状态

| 状态 | 数量 | 含义 |
| --- | ---: | --- |
| `WARN` | 377 | 页面可用，但仍有事实、runtime、ownership、visual QA 或口述门未闭合 |
| `PASS WITH WARNING` | 10 | 十份独立事实复核切片通过；warning 仍保留 |
| `PASS` | 0 | 没有任何 artifact 可被解释为全门完成 |
| `unseen` 题卡 | 280 | 候选人尚未提供真实口述回答 |
| `weak/pass/strong/stale` | 0 | 没有训练证据，不做推断 |

当前环境已可通过 localhost 对代表页面做桌面/窄屏视觉 QA；未逐页打开的 artifact 仍只能主张静态校验，不能用代表抽样冒充全仓逐页视觉验收。

## 7. 当前优先级与停止条件

完成度最高但价值最低的动作是无边界堆页面；当前 VOL 06 的 PER-001..020 source/knowledge/card gate 已冻结，五项目 P0 artifact intake contract 和 ownership confirmation queue 也已建立，UWM base binary 亦已单独冻结，但二十张卡均未口述、五项目 P0 仍未闭合，下一步只做一题真实口述或一份 target P0 bundle，避免把页面覆盖当成掌握或个人安全结果。

本轮之后只选择一个 bounded next slice：

1. **推荐：只做一题真实口述或独立 fact review**。PER-001..020 三联件已完成；本轮不修改 mastery、不创建 coaching state，先把页面覆盖与真实训练分开。
2. Robot Harness已恢复28/40 primary、闭合6/10 exact support，并证明本地17个同名候选均不能填12个缺口；若远端文件可达，只按12条locator恢复，不用同名候选凑数。
3. 真实口述仍是独立优先队列；得到候选人回答后，才创建/更新 coaching state。
4. OpenPiVLA 的 LIBERO load/connect、ALOHA action-level load/L1、本地文件 manifest 与 LIBERO matched-probe preflight 已由 [LIBERO Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.md)、[ALOHA Action Eval Gate](openpivla_aloha_action_eval_load_gate.md)、[Official Checkpoint Immutable Manifest Gate](openpivla_official_checkpoint_immutable_manifest_gate.md) 和 [Matched Failure Probe Readiness Gate](openpivla_libero_matched_failure_probe_readiness_gate.md) 冻结，并已映射到 `PROJ-OPENPIVLA-007`；远端 checkpoint/norm-stats 逐文件 SHA、effective argv、raw trace、独立 scorer 与 shared run identity 仍缺，下一步可做远端只读 manifest 或 fresh matched probe。
5. UWM `libero_90.pt` base binary 已由 [本地 Immutable Checkpoint Gate](uwm_libero90_checkpoint_immutable_manifest_gate.md) 冻结；这不关闭 target fine-tune binary、normalizer、fresh reload、scorer 或 ownership。
6. 五项目 P0 intake contract：[`../evidence/p0_artifact_intake_contract.md`](../evidence/p0_artifact_intake_contract.md)，用于 checkpoint、protocol、raw output、scorer 与 ownership 的统一收口。

停止条件：本轮不新增其他知识节点或题卡，不修改任何 mastery，不提交或推送；真实口述、项目证据与 SYS-VLA-004 仍保留为独立队列。

## 参考入口（References）

1. [VLA 总路线图](../../vla_interview_roadmap.md)
2. [VLA 子仓库 README](../README.md)
3. [八卷知识地图](../knowledge/00_vla_knowledge_map.md)
4. [全局题库目录](../questions/README.md)
5. [项目 Evidence Manifest](../evidence/evidence_manifest.md)
6. [GitHub 骨架与来源入口](00_github_guidance_and_sources.md)
7. [VOL 06 Coverage-Gap Audit](vol_06_perception_grounding_navigation_coverage_gap_audit.md)
8. [Robot Harness Common-Support Raw Bundle Manifest](../evidence/projects/robot_harness_common_support_raw_bundle_manifest.md)
8. [PER-006 Image Preprocess / Token / Camera Source Freeze](vol_06_per006_image_preprocess_token_camera_contract_source_freeze.md)
9. [PER-006 Image Preprocess / Token / Camera Knowledge](../knowledge/vol_06_per006_image_preprocess_token_camera_contract.md)
10. [PER-006 Atomic Card](../questions/vol_06_per006.md)
11. [PER-007 Open-vocabulary Grounding Pipeline Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.md)
12. [PER-007 Open-vocabulary Grounding Pipeline Knowledge](../knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.md)
13. [VOL 04 Audit D Sim2Real Independent Fact Review](vol_04_sim2real_independent_fact_review.md)
14. [PER-007 Open-vocabulary Grounding Atomic Card](../questions/vol_06_per007.md)
15. [PER-008 Representation Choice Source Freeze](vol_06_per008_representation_choice_source_freeze.md)
16. [PER-008 Representation Choice Knowledge](../knowledge/vol_06_per008_representation_choice.md)
17. [PER-008 Representation Choice Atomic Card](../questions/vol_06_per008.md)
18. [PER-009 Grounding Matching / Negative / Loss Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.md)
19. [PER-009 Grounding Matching / Negative / Loss Knowledge](../knowledge/vol_06_per009_grounding_matching_negative_loss.md)
20. [PER-009 Grounding Matching / Negative / Loss Atomic Card](../questions/vol_06_per009.md)
21. [PER-010 Grounding Metric / Parser / Protocol Source Freeze](vol_06_per010_grounding_metric_parser_protocol_source_freeze.md)
22. [PER-010 Grounding Metric / Parser / Protocol Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.md)
23. [PER-010 Grounding Metric / Parser / Protocol Atomic Card](../questions/vol_06_per010.md)
24. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Source Freeze](vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.md)
25. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.md)
26. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Atomic Card](../questions/vol_06_per016.md)
27. [PER-017 Belief / Memory / Frontier / Active Exploration Source Freeze](vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.md)
28. [PER-017 Belief / Memory / Frontier / Active Exploration Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.md)
29. [PER-017 Belief / Memory / Frontier / Active Exploration Atomic Card](../questions/vol_06_per017.md)
30. [PER-018 Navigation BC / DAgger / RL / Exposure Bias Source Freeze](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.md)
31. [VOL 04 Audit C Cosmos Policy / WAM Independent Fact Review](vol_04_cosmos_policy_wam_independent_fact_review.md)
32. [Robot Harness Five/Eight-Model Ten-Suite Aggregate Bundle Gate](../evidence/projects/robot_harness_10suite_aggregate_bundle_gate.md)
33. [VOL 08 Coding / System Design Coverage-Gap Audit](vol_08_coding_system_design_coverage_gap_audit.md)
34. [SYS-VLA-002 Policy Serving / Real-time Control Loop Source Freeze](vol_08_sys002_policy_serving_realtime_control_loop_source_freeze.md)
