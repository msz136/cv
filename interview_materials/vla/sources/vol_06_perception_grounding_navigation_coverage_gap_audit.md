# VOL 06 Perception / Grounding / Navigation：Coverage-Gap Audit

> 审计日期：2026-07-20  
> 状态：`coverage_contract_frozen / planned_20 / sources_19 / knowledge_19 / cards_19 / per018_independent_fact_reviewed / per019_triplet_synced / missing_sources_1 / missing_knowledge_1 / missing_cards_1 / WARN`  
> 审计对象：VOL 06 已有 source/knowledge/card、全局 Knowledge Map、Repository Completion Audit、GitHub skeleton guidance、五项目 evidence inventory 与导航 artifact gate。  
> 核心边界：本报告冻结整卷范围与退出条件；不把 planned/source/knowledge-only ID 计入题库，不生成占位卡，不把公开 perception/navigation 机制写成个人项目成果。

## 问题（Question）

现有 `VLA-PER-001..005` 是否足以支持“VOL 06 Perception / Grounding / Navigation 已完成”？如果不足，缺失的是哪些不可合并的知识节点、来源门、项目证据门和真实训练门？

## 1. 结论先行

1. 二十个节点覆盖 image/token contract 与 grounding representation → 3D lift → multi-view/time → VLN/ObjectNav protocol → navigation architecture → open-vocabulary grounding → matching/loss → metric/parser → pseudo-label/noise/calibration/leakage → segmentation/depth/keypoint/affordance → point/voxel/BEV/occupancy → 3D grounding/spatial relation/open-vocabulary 3D scene → perception/action feasibility → localization/odometry/SLAM/map-frame/drift → belief/memory/frontier/active-exploration → navigation BC/DAgger/RL/exposure bias → navigation evaluation/failure → robustness/safety主链；`PER-001..020`已有source/knowledge/card，二十张卡均为 `unseen/WARN`。
2. image preprocessing/token contract由PER-006独立承载；open-vocabulary inference由PER-007承载；PER-008..018均已按独立source→knowledge→card切片同步。PER-018独立事实复核重新命中7/7 PDF、10/10 official files、10/10 probes、8/8 local files，并确认R2R student-forcing的限定语境与pinned Habitat done-mask版本差异；完整评估与robustness/safety仍没有独立节点。
3. VOL 06 整卷冻结为 **20 个原子节点**：当前source为`20/20=100%`，knowledge为`20/20=100%`，card为`20/20=100%`；PER-001..020三联件同步，二十张题卡保持`unseen`。
4. 五项目中有 interface/provenance hook，但 [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html) 重算为 `0` 个 local-direct VLN/ObjectNav episode bundle；因此不得产生个人导航成功率、SPL 或真实机器人 claim。
5. 覆盖完成、事实审查、项目证据、HTML 生命周期和口述 mastery 分开计数。即使未来达到 20/20 页面覆盖，没有真实回答、visual QA 或项目 artifact 时也不能写成 `drilled/done`。

## 2. 本次审计依据

| 依据 | 实际支持 | 不能支持 |
| --- | --- | --- |
| [GitHub Source Scout](00_github_guidance_and_sources.html) | WinstonJQ 骨架规则：主索引、分卷、Markdown canonical、折叠题卡、review、L1/L2/L3、题目前置清单 | 具体 VLA/perception 技术事实或题目频次 |
| [VLA Knowledge Map](../knowledge/00_vla_knowledge_map.html) | VOL 06 范围为 image/token、point/box/text、3D geometry、multi-view、VLN/ObjectNav、grounding quality | 现有五页已经覆盖所有原子问题 |
| [Repository Completion Audit](repository_completion_audit.html) | 当前全局276 cards；VOL 06有20个完整节点，整卷退出条件仍未满足 | planned ID、source或knowledge自动成为已生成题卡 |
| [PER-001 Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html) | point/box/text、parser、坐标逆变换、OPD truth boundary | 3D、action success 或个人导航结果 |
| [PER-002 Source Freeze](vol_06_per002_3d_lift_frame_source_freeze.html) | calibration/depth/back-projection/frame/TF 合同 | 本地 3D round-trip 或 controller success |
| [PER-003 Source Freeze](vol_06_per003_multiview_temporal_source_freeze.html) | camera/frame/time/presence 与 fusion schema | 本地 multi-camera calibration、sync 或 ablation |
| [PER-004 Source Freeze](vol_06_per004_vln_objectnav_source_freeze.html) | VLN/ObjectNav/REVERIE task、episode、stop、SR/SPL 协议 | 用户复现 benchmark 或真实导航 |
| [PER-005 Source Freeze](vol_06_per005_navigation_policy_architecture_source_freeze.html) | map-free/map-based/waypoint/planner/controller taxonomy | 用户实现、matched ablation 或 ownership |
| [PER-008 Source Freeze](vol_06_per008_representation_choice_source_freeze.html) / [Knowledge](../knowledge/vol_06_per008_representation_choice.html) / [Card](../questions/vol_06_per008.html) | point/box/mask/semantic-keypoint/affordance语义、选择、转换损失与OPD边界 | local dense affordance、matched ablation或robot result |
| [PER-009 Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.html) / [Knowledge](../knowledge/vol_06_per009_grounding_matching_negative_loss.html) / [Card](../questions/vol_06_per009.html) | Hungarian/token negatives/focal/L1/GIoU/reduction、本地CE/top1/KL、typed manifest、面试诊断与2500行metrics边界 | first-party criterion、checkpoint/holdout/robot绑定 |
| [PER-010 Source Freeze](vol_06_per010_grounding_metric_parser_protocol_source_freeze.html) / [Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.html) / [Card](../questions/vol_06_per010.html) | strict/lenient parser、IoU/Acc、RefExp/COCO、PCK/mask-hit/fixed-distance Hit、denominator、protocol identity、面试诊断与项目边界 | raw prediction reconciliation、parser v2 rerun与robot结果 |
| [PER-012 Source Freeze](vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html) / [Knowledge](../knowledge/vol_06_per012_segmentation_depth_keypoint_affordance.html) / [Card](../questions/vol_06_per012.html) | segmentation task、relative/metric depth、3D surface、semantic keypoint、primitive-conditioned affordance、typed composition、atomic answer与OPD point-only边界 | local dense checkpoint、metric-depth/camera bundle、planner/controller episode或robot success |
| [PER-013 Source Freeze](vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html) / [Knowledge](../knowledge/vol_06_per013_pointcloud_voxel_bev_occupancy.html) / [Card](../questions/vol_06_per013.html) | PointNet++/VoxelNet/PointPillars/Minkowski/BEVFusion/occupancy contracts、九个probe、教学诊断、atomic answer与Harness 2D-map/PCD boundary | local learned 3D encoder、matched benefit、robot result或ownership |
| [PER-014 Source Freeze](vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html) / [Knowledge](../knowledge/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.html) / [Card](../questions/vol_06_per014.html) | ScanRefer/ReferIt3D/OpenScene/OpenMask3D/LERF/ConceptFusion、六类output、typed manifest、relation、score/metric、diagnostic、155/335字符atomic answer与五项目真实性边界 | local 3D semantic head/map/checkpoint/raw query/robot result或ownership |
| [PER-015 Source Freeze](vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html) / [Knowledge](../knowledge/vol_06_per015_perception_action_reachability_uncertainty_failure_gate.html) / [Card](../questions/vol_06_per015.html) | Modern Robotics/MoveIt/OMPL/TRAC-IK/CLIPort/KnowNo、typed action manifest、九层gate、10个probe、first-divergence diagnosis、141/257字符atomic answer与五项目direct audit | 本地完整gate/runtime、robot success或ownership |
| [PER-016 Source Freeze](vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html) / [Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.html) / [Card](../questions/vol_06_per016.html) | ORB-SLAM3/VINS-Mono/Cartographer/DROID-SLAM/OpenVINS/Kimera、REP-105、typed manifest、state/covariance、pose graph、drift、ATE/RPE、10个probe、179/350字符回答与Harness map/PCD真实性边界 | 本地SLAM estimator/runtime、trajectory bundle、robot localization结果或ownership |
| [PER-017 Source Freeze](vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html) / [Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html) / [Card](../questions/vol_06_per017.html) | POMDP/Bayes/zero-likelihood、三类memory、typed manifest、known-free/unknown frontier、IG/utility、revisit/stuck、metric contract、10 probes、172/315字符回答、诊断与五项目direct audit | local exploration runtime/episode、checkpoint/result或ownership |
| [PER-018 Source Freeze](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html) / [Knowledge](../knowledge/vol_06_per018_navigation_bc_dagger_rl_exposure_bias.html) / [Card](../questions/vol_06_per018.html) / [Independent Review](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html) | BC/forcing/DAgger/GAE/PPO-DDPPO、7 PDFs/96页、10 official files rehash、10 probes、8 local files、两档回答、诊断与单张unseen题卡 | local navigation DAgger/PPO runtime、matched episode/result、ownership与真实口述 |
| [PER-019 Source Freeze](vol_06_per019_navigation_evaluation_failure_source_freeze.html) | stop-gated success、POINT/VIEW_POINTS geodesic、SPL/SoftSPL、split/denominator、failure taxonomy、10 source probes与五项目truth boundary | local navigation bundle、统一scorer、per-episode trace、个人导航结果或ownership |
| [PER-020 Source Freeze](vol_06_per020_robustness_safety_fallback_source_freeze.html) | corruption family/severity、clean-shift protocol、dataset-shift uncertainty、risk-coverage、queue flush、fallback/recovery/E-stop、10 source probes与五项目truth boundary | local shifted-input bundle、逐step risk log、hardware E-stop audit、个人OOD或安全结果 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | local point/box/text route、scorer 与 leakage 边界 | 3D grounding、closed-loop manipulation 或 navigation success |

## 3. 当前资产盘点

| 层 | 已有 | 目标 | 覆盖 | 仍开放的门 |
| --- | ---: | ---: | ---: | --- |
| generated question cards | 20 | 20 | 100% | `PER-001..020`已生成且unseen |
| source freeze | 20 | 20 | 100% | PER-001..019与PER-020 source已冻结；PER-020 knowledge/card仍后置 |
| knowledge nodes | 20 | 20 | 100% | PER-001..020已生成；全部对应题卡保持unseen |
| question card | 20 | 20 | 100% | PER-001..020均有单张原子卡；仍未进行真实口述 |
| oral drill | 0 | 最少 8 | 0% | 二十张已有卡仍全部 `unseen` |
| local-direct navigation bundle | 0 | 不强制有正结果，但必须保持 truth boundary | — | episode/scene/start/goal/action/denominator/failure trace 缺失 |
| browser desktop/narrow QA | 0 | 当前卷页面均需验收 | 0% | `file://` 策略阻断；静态检查不能替代视觉 QA |

## 4. 整卷 Stable-ID 合同

权威题目清单为 [VOL 06 Phase 0 Question List](../questions/vol_06_perception_grounding_navigation.question_list.md)。规划 20 个节点，按 12 个 P0、8 个 P1 分层；以下只给出聚类，不重复清单全文。

| 学习簇 | IDs | 现有 / 规划 | 核心缺口 |
| --- | --- | ---: | --- |
| 输入与 2D grounding | `001,006..012` | 8 complete / 8 | 独立fact review、local dense artifact与真实drill仍开放 |
| 3D、多视角与动作接口 | `002,003,013..015` | 5 complete / 5 | 独立fact review、本地physical-gate runtime与真实drill仍开放 |
| 导航任务、地图与训练 | `004,005,016..018` | 5 triplets / 5 | 学习簇覆盖完成；独立fact review与真实drill仍开放 |
| 评估、鲁棒性与安全 | `019,020` | 2 source + 2 knowledge + 2 cards / 2 nodes | PER-019/020 source+knowledge+card均同步；真实口述仍缺 |

依赖主链：

```text
# Planned IDs are registry entries, not generated mastery.
PER-006 image/token
  -> PER-007 open-vocab grounding
  -> PER-008 representation choice
  -> PER-009 loss/matching -> PER-010 metric/parser -> PER-011 pseudo-label/noise
  -> PER-012 segmentation/depth/keypoint/affordance

PER-002 3D lift + PER-003 multi-view
  -> PER-013 3D representation -> PER-014 3D grounding
  -> PER-015 perception-to-action gate

PER-004 task contract + PER-005 policy architecture + PER-016 SLAM
  -> PER-017 memory/exploration -> PER-018 IL/RL training
  -> PER-019 evaluation/failure -> PER-020 robustness/safety
```

## 5. Source Queue 与冻结边界

下表是后续逐节点 source freeze 的检索队列，不表示已经核验完成。只有读取 primary paper、official code/docs 或本地 artifact 并记录 revision 后，才能进入知识页。

| IDs | 待冻结的来源类型 | 本仓库可复用入口 | 当前状态 |
| --- | --- | --- | --- |
| `006` | VLM/ViT 官方 image processor、resize/crop/patch/position contract | GitHub Source Scout 中的 Qwen3-VL frozen repo；VOL 01/03 vision-token pages | `source + knowledge + card synchronized / unseen` |
| `007` | Grounding/open-vocabulary detection primary paper与 official code；matching、two-threshold、phrase与NMS boundary | PER-001 Grounding DINO；PER-006 image contract；OPD inventory | `source + knowledge + card synchronized / unseen` |
| `008` | point/box/mask/keypoint/affordance primary papers与official output contracts | PER-001/007；RoboPoint/SAM/kPAM/Where2Act；OPD local point evidence | `source + knowledge + card / unseen` |
| `009` | grounding loss/matching primary/official sources | PER-007/008 source gates；GroundingDINO/DETR/HF；OPD train artifacts | `source + knowledge + card synchronized / unseen` |
| `010` | grounding metric/parser primary/official sources | PER-001；PER-007/008 source gates；OPD scorer inventory | `source + knowledge + card synchronized / unseen` |
| `011` | noisy/pseudo-label、confidence calibration、curriculum与data leakage primary/official sources | FixMatch/Noisy Student/calibration/leakage来源、OPD mix/cache/online/holdout | `source+knowledge+card synced / unseen` |
| `012` | segmentation/depth/keypoint/affordance concrete methods | Mask2Former/SAM/Depth Anything V2/kPAM/Where2Act、OPD point-only audit | `source+knowledge+card synced / unseen` |
| `013` | point-cloud/voxel/BEV/occupancy representation与sampling | PointNet++/VoxelNet/PointPillars/Minkowski/BEVFusion/Occupancy Networks/OctoMap、Harness map/PCD | `source+knowledge+card / unseen` |
| `014` | 3D grounding、spatial relation、open-vocabulary 3D scene primary/official sources | ScanRefer/ReferIt3D/OpenScene/OpenMask3D/LERF/ConceptFusion；PER-007/013；五项目inventories与direct exceptions | `source + knowledge + card synchronized / unseen` |
| `015` | reachability/uncertainty primary sources | PER-002/003/013/014、Modern Robotics/MoveIt/OMPL/TRAC-IK/CLIPort/KnowNo、VOL 03 action contract | `source+knowledge+card synced / unseen` |
| `016` | SLAM/odometry/map-frame/drift primary paper、official code与REP-105 frame contract | ORB-SLAM3/VINS-Mono/Cartographer/DROID-SLAM/OpenVINS/Kimera；Harness map/PCD/reloc assets | `source + knowledge + card synced / unseen` |
| `017` | POMDP belief、active exploration/memory、frontier、coverage/revisit primary + official code | Kaelbling/Yamauchi/Neural-SLAM/OccupancyAnticipation/SemExp/PONI/Exploring Exploration/EmbodiedQA；PER-004/005/016 | `source + knowledge + card synced / unseen` |
| `018` | VLN IL/RL、teacher forcing与exposure bias primary + official benchmark code | DAgger/Scheduled Sampling/R2R/VLN-CE/DD-PPO/PPO/GAE；VLN-CE/Habitat/R2R official code；PER-004/005与VOL 02 | `source + knowledge + card synchronized / unseen` |
| `019` | official navigation measures、SPL/benchmark protocol、statistical reporting | PER-004、VOL 05 evaluation、PER-004 artifact gate | `source + knowledge + card synchronized / unseen` |
| `020` | sensor/domain randomization、uncertainty/safety/fallback primary + simulator docs | VOL 04 Sim2Real Audit D、VOL 05 failure taxonomy、Hendrycks/Ovadia/Safety Gym | `source + knowledge synchronized / card pending` |

## 6. 项目挂钩与真实性边界

| 项目 | 可用 hook | 当前不能说 |
| --- | --- | --- |
| OPD | point/box/text route、affordance-labelled point supervision、Visual Genome 2D image spatial-relation数据与strict/protocol-fixed/lenient scorer | 3D relation frame、3D semantic grounding、closed-loop grasp/navigation、单因素 uplift 或未确认 ownership |
| Robot Harness | semantic-navigation tool schema、2D tri-state occupancy、non-semantic PCD与tool-call/eval interface | language-queryable 3D map、personal VLN/ObjectNav policy、physical navigation episode 或 success/SPL |
| OpenPiVLA | image/language/action schema、normalization/controller contract 风险 | 使用 grounding/SLAM/navigation module，或 formal rollout 已闭环 |
| WAM | camera/controller/provenance 与有限 paired diagnostic | multi-view fusion、3D target、navigation success 或真机 Sim2Real |
| UWM / LIBERO | simulated manipulation protocol与 camera/action schema | VLN/ObjectNav、mobile navigation、跨协议真实泛化 |

面试回答必须按 `public upstream mechanism → local interface/evidence → inference → unverified` 分层。Git author、official example、字段名或工具描述不能自动成为个人贡献。

## 7. VOL 06 退出条件

### 7.1 Coverage complete

1. `VLA-PER-001..020` 全部有唯一 source/knowledge/card 三联件，卷级 question list 与索引同步。
2. 每张卡包含 stable ID、难度/优先级、短答、机制展开、来源、项目挂钩、易错点、追问与练习状态。
3. P0/P1 节点均有 primary/official source revision；discovery list 或跨卷引用不能单独支撑强技术答案。

### 7.2 Reviewed

1. 20 个节点的 canonical/HTML/review SHA、单 H1、ID、锚点、公式、表格和本地链接通过。
2. 四个学习簇各完成至少一个独立 fact-review slice；高风险 metric、3D frame、navigation stop/success 与 project truth boundary 必须覆盖。
3. Project hook 只引用 evidence inventory/ownership ledger；缺本地 bundle 时明确说“没有直接证据”。

### 7.3 Drilled

1. 至少完成 8 个真实口述 drill，四个学习簇各至少 1 题，其中至少 2 题带项目追问。
2. 只有真实回答后才创建/更新 coaching state；状态变化必须有回答、反馈、日期和 next review。
3. 覆盖完成或 HTML 生成不改变 `unseen/weak/pass/strong/stale`。

### 7.4 Visual / evidence boundary

1. 支持的本地页面表面恢复后，对卷级入口与代表性原子页做 desktop/narrow QA；当前 `BLOCKED` 不能写成 PASS。
2. 不强制虚构正向导航结果；如果没有 local-direct bundle，退出时应保留“无个人导航结果”的真实边界。

## 8. 缺口优先级与下一切片

| 优先级 | 缺口 | 原因 | 下一动作 |
| --- | --- | --- | --- |
| P0-1 | 真实口述与 navigation artifact | 二十张卡均 unseen，local-direct bundle 仍为0 | 先做一题真实口述或收集 immutable episode bundle |

下一 bounded slice：只做一题真实口述或独立 fact review；不修改任何mastery。local-direct navigation/robustness bundle继续保留为证据队列。

## 参考入口（References）

1. [VOL 06 Phase 0 Question List](../questions/vol_06_perception_grounding_navigation.question_list.md)
2. [GitHub Source Scout](00_github_guidance_and_sources.md)
3. [VLA Knowledge Map](../knowledge/00_vla_knowledge_map.md)
4. [Repository Completion Audit](repository_completion_audit.md)
5. [PER-001 Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.md)
6. [PER-002 Source Freeze](vol_06_per002_3d_lift_frame_source_freeze.md)
7. [PER-003 Source Freeze](vol_06_per003_multiview_temporal_source_freeze.md)
8. [PER-004 Source Freeze](vol_06_per004_vln_objectnav_source_freeze.md)
9. [PER-005 Source Freeze](vol_06_per005_navigation_policy_architecture_source_freeze.md)
10. [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.md)
11. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.md)
12. [PER-007 Open-vocabulary Grounding Pipeline Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.md)
13. [PER-007 Open-vocabulary Grounding Pipeline Knowledge](../knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.md)
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
24. [PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Source Freeze](vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.md)
25. [PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Knowledge](../knowledge/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage.md)
26. [PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Atomic Card](../questions/vol_06_per011.md)
27. [PER-012 Segmentation / Depth / Keypoint / Affordance Source Freeze](vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.md)
28. [PER-012 Segmentation / Depth / Keypoint / Affordance Knowledge](../knowledge/vol_06_per012_segmentation_depth_keypoint_affordance.md)
29. [PER-012 Segmentation / Depth / Keypoint / Affordance Atomic Card](../questions/vol_06_per012.md)
30. [PER-013 Point Cloud / Voxel / BEV / Occupancy Source Freeze](vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.md)
31. [PER-013 Point Cloud / Voxel / BEV / Occupancy Knowledge](../knowledge/vol_06_per013_pointcloud_voxel_bev_occupancy.md)
32. [PER-013 Point Cloud / Voxel / BEV / Occupancy Atomic Card](../questions/vol_06_per013.md)
33. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary 3D Scene Source Freeze](vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.md)
34. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary 3D Scene Knowledge](../knowledge/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.md)
35. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary 3D Scene Atomic Card](../questions/vol_06_per014.md)
36. [PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Source Freeze](vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.md)
37. [PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Knowledge](../knowledge/vol_06_per015_perception_action_reachability_uncertainty_failure_gate.md)
38. [PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Atomic Card](../questions/vol_06_per015.md)
39. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Source Freeze](vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.md)
40. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.md)
41. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Atomic Card](../questions/vol_06_per016.md)
42. [PER-017 Belief / Memory / Frontier / Active Exploration Source Freeze](vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.md)
43. [PER-017 Belief / Memory / Frontier / Active Exploration Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.md)
44. [PER-017 Belief / Memory / Frontier / Active Exploration Atomic Card](../questions/vol_06_per017.md)
45. [PER-018 Navigation BC / DAgger / RL / Exposure Bias Source Freeze](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.md)
