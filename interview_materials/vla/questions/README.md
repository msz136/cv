# Questions

本目录存放可折叠自测的短答案题库，与 `knowledge/` 分离。

总索引：[`00_master_question_index.html`](00_master_question_index.html)。

Phase 0 题目清单：

- [VOL 01 Foundations](vol_01_foundations.question_list.md)：39/39 已进入题卡。
- [VOL 02 IL / RL / Post-training](vol_02_il_rl_posttraining.question_list.md)：40/40 已进入题卡。
- [VOL 03 VLA / Action](vol_03_vla_action.question_list.md)：44 道已规划并全部进入题卡；全部保持 unseen。
- [VOL 04 World Model / Sim2Real](vol_04_world_model_sim2real.question_list.md)：44/44 已进入知识/题卡，全部保持 unseen。
- [VOL 05 Engineering / Evaluation](vol_05_engineering_eval.question_list.md)：44/44 已进入知识/题卡，全部保持 unseen。
- [VOL 06 Perception / Grounding / Navigation](vol_06_perception_grounding_navigation.question_list.md)：20 道已规划，`VLA-PER-001..020`三联件已同步且全部unseen；下一步进行一题真实口述或独立fact review。
- [VOL 06 PER-020](vol_06_per020.html)：1 道 L3/P1 题卡，覆盖 corruption/severity、shifted calibration、risk–coverage、risk gate、queue flush、fallback/recovery/E-stop 与五项目truth boundary；保持 `unseen/WARN`。
- [VOL 05 EVAL-003 题卡](vol_05_engineering_eval_eval003.question_list.md)：`VLA-EVAL-003` 单张题卡已生成，短答/机制展开通过长度门，保持 `unseen`；review 见 [`vol_05_engineering_eval_eval003.review.json`](vol_05_engineering_eval_eval003.review.json)。
- [VOL 05 Engineering / Evaluation Batch 2A](vol_05_engineering_eval_batch2a.question_list.md)：`VLA-ENG-009..011` 三张题卡，全部 unseen；review 见 [`vol_05_engineering_eval_batch2a.review.json`](vol_05_engineering_eval_batch2a.review.json)，官方文档复核见 [`source review`](../sources/vol_05_batch2a_independent_fact_review.html)。
- [VOL 05 ENG-012 Source Gate](../sources/vol_05_eng012_storage_formats_source_freeze.html)：HDF5/Zarr/WebDataset/Parquet 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng012.html)与单张题卡已生成，题卡保持 unseen。
- [VOL 05 ENG-012 题卡](vol_05_engineering_eval_eng012.question_list.md)：单张 workload-to-layout 题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng012.review.json`](vol_05_engineering_eval_eng012.review.json)。
- [VOL 05 ENG-013 Source Gate](../sources/vol_05_eng013_reproducibility_source_freeze.html)：seed/determinism/DistributedSampler/RNG state/cursor 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng013.html)与单张题卡已生成。
- [VOL 05 ENG-013 题卡](vol_05_engineering_eval_eng013.question_list.md)：单张 seed/sampler-cursor/resume 题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng013.review.json`](vol_05_engineering_eval_eng013.review.json)。
- [VOL 05 ENG-014 Source Gate](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html)：CUDA/HIP/ROCm/MACA 六层兼容合同与 operator matrix 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng014.html)与单张题卡已生成。
- [VOL 05 ENG-014 题卡](vol_05_engineering_eval_eng014.question_list.md)：单张硬件/算子兼容题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng014.review.json`](vol_05_engineering_eval_eng014.review.json)。
- [VOL 05 ENG-015 Source Gate](../sources/vol_05_eng015_activation_offload_source_freeze.html)：activation checkpointing、FSDP CPU offload、ZeRO CPU/NVMe offload 与吞吐/resume 合同来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng015.html)与单张题卡已生成。
- [VOL 05 ENG-015 题卡](vol_05_engineering_eval_eng015.question_list.md)：单张 memory/offload A/B 题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng015.review.json`](vol_05_engineering_eval_eng015.review.json)。
- [VOL 05 ENG-016 Source Gate](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)：student + multiple teachers、distillation/KL、teacher no-grad 与 memory scheduling 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng016.html)与单张题卡已生成。
- [VOL 05 ENG-016 题卡](vol_05_engineering_eval_eng016.question_list.md)：单张多教师蒸馏/显存调度题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng016.review.json`](vol_05_engineering_eval_eng016.review.json)。
- [VOL 05 ENG-017 Source Gate](../sources/vol_05_eng017_training_observability_source_freeze.html)：loss/grad/data_wait/comm/AMP overflow observability 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng017.html)与单张题卡已生成。
- [VOL 05 ENG-017 题卡](vol_05_engineering_eval_eng017.question_list.md)：单张训练可观测性题卡，全部 unseen；review 见 [`vol_05_engineering_eval_eng017.review.json`](vol_05_engineering_eval_eng017.review.json)。
- [VOL 05 ENG-018 Source Gate](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)：scheduler/preemption/retry/idempotency 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng018.html)与单张题卡已生成。
- [VOL 05 ENG-018 题卡](vol_05_engineering_eval_eng018.question_list.md)：单张 scheduler/preemption/retry 题卡，保持 unseen；review 见 [`vol_05_engineering_eval_eng018.review.json`](vol_05_engineering_eval_eng018.review.json)。
- [VOL 05 ENG-019 Source Gate](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)：config/CLI/env resolution、field provenance、secret-safe canonicalization 与 run identity 来源已冻结，[知识页](../knowledge/vol_05_engineering_eval_eng019.html)与单张题卡已生成。
- [VOL 05 ENG-019 题卡](vol_05_engineering_eval_eng019.question_list.md)：单张 config resolution/run identity 题卡，保持 unseen；review 见 [`vol_05_engineering_eval_eng019.review.json`](vol_05_engineering_eval_eng019.review.json)。
- [VOL 05 ENG-020 Source Gate](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)：secret/token lifecycle、least privilege/data permission、logging redaction 与 Robot Harness token-mask hook 来源已冻结；[知识页](../knowledge/vol_05_engineering_eval_eng020.html)与[单张题卡](vol_05_engineering_eval_eng020.html)已生成，题卡保持 unseen。
- [VOL 05 ENG-020 题卡](vol_05_engineering_eval_eng020.question_list.md)：单张 secret/permission/logging 题卡，保持 unseen；review 见 [`vol_05_engineering_eval_eng020.review.json`](vol_05_engineering_eval_eng020.review.json)。
- [VOL 05 ENG-021 Source Gate](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)：model/processor/normalizer/checkpoint/transform/shape compatibility 来源已冻结；[知识页](../knowledge/vol_05_engineering_eval_eng021.html)与单张题卡已生成，题卡保持 unseen。
- [VOL 05 ENG-021 题卡](vol_05_engineering_eval_eng021.question_list.md)：单张 model/processor/normalizer packaging 题卡，保持 unseen；知识页与 review 已同步。
- [VOL 05 ENG-022 Source Gate](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)：policy server batching/backpressure/timeout/fallback 来源已冻结；[知识页](../knowledge/vol_05_engineering_eval_eng022.html)与单张题卡已生成，题卡保持 unseen。
- [VOL 05 ENG-022 题卡](vol_05_engineering_eval_eng022.question_list.md)：单张 policy-server resilience 题卡，保持 unseen；知识页与 review 已同步。
- [VOL 07 OpenPiVLA 项目题卡](proj_openpivla.question_list.md)：Batch 1 已进入 8 道 direct-evidence-bounded 题卡；后续批次按新增证据推进。
- [VOL 07 OpenPiVLA Batch 2](proj_openpivla_batch2.question_list.md)：证据冻结后新增 4 道题卡，覆盖 eager/evidence ladder/lineage/shape conflict。
- [VOL 07 Robot Harness Batch 1](proj_robot_harness.question_list.md)：8 道题卡，覆盖 runtime、数据/reward、run/scorer 与 proxy/ownership 边界。
- [VOL 07 OPD Batch 1](proj_opd.question_list.md)：8 道题卡，覆盖五 expert route、online OPD、checkpoint、holdout 与 point protocol。
- [VOL 07 WAM Batch 1](proj_wam.question_list.md)：4 道题卡，覆盖 CoffeePressButton diagnostic bundle、save/load gate、full10k/official-HF eval provenance、trace/offline proxy/checkpoint 分层与项目真实性边界。
- [VOL 06 PER-001](vol_06_per001.question_list.md)：1 道题卡，覆盖 point/box/text 表示、坐标变换、strict/lenient scorer 与 OPD grounding 边界。
- [VOL 06 PER-002](vol_06_per002.question_list.md)：1 道题卡，覆盖 depth、camera calibration、反投影、timestamped TF、uncertainty 与 3D evidence ladder。
- [VOL 06 PER-003](vol_06_per003.question_list.md)：1 道题卡，覆盖 camera/frame identity、timestamp、presence mask、common-frame fusion 与 observation age。
- [VOL 06 PER-004](vol_06_per004.question_list.md)：1 道题卡，覆盖 VLN/ObjectNav/REVERIE task contract、stop/success、SR/SPL 与 simulator-to-real 证据边界。
- [VOL 06 PER-005](vol_06_per005.question_list.md)：1 道题卡，覆盖 map-free/map-based/waypoint policy、planner/controller、stop/replan、latency 与 matched ablation。
- [VOL 06 PER-006](vol_06_per006.question_list.md)：1 道题卡，覆盖image preprocess、patch/token、camera identity、inverse mapping与本地double-resize边界。
- [VOL 06 PER-007](vol_06_per007.question_list.md)：1 道题卡，覆盖open-vocabulary grounding pipeline、phrase/box/NMS边界与本地生成式坐标路径。
- [VOL 06 PER-008](vol_06_per008.question_list.md)：1 道题卡，覆盖point/box/mask/keypoint/affordance表示选择、信息损失与OPD point-only边界。
- [VOL 06 PER-009](vol_06_per009.question_list.md)：1 道题卡，覆盖matching/final loss、negative/reduction、本地CE/KL与metrics真实性边界。
- [VOL 06 PER-010](vol_06_per010.question_list.md)：1 道题卡，覆盖strict parser、IoU/PCK/fixed Hit、denominator与protocol comparability。
- [VOL 06 PER-011](vol_06_per011.question_list.md)：1 道题卡，覆盖pseudo-label、calibration、risk–coverage、curriculum、leakage与OPD teacher边界。
- [VOL 06 PER-012](vol_06_per012.question_list.md)：1 道题卡，覆盖segmentation、relative/metric depth、semantic keypoint、affordance、action gate与OPD point-only边界。
- [VOL 06 PER-013](vol_06_per013.question_list.md)：1 道题卡，覆盖point cloud、sampling、voxel/sparse/pillar/BEV/occupancy与Robot Harness map/PCD边界。
- [VOL 06 PER-014](vol_06_per014.question_list.md)：1 道题卡，覆盖六类3D grounding输出、candidate hard bound、relation frame、score/metric与五项目边界。
- [VOL 06 PER-015](vol_06_per015.question_list.md)：1 道题卡，覆盖typed perception→action、workspace/IK/collision/trajectory/controller、uncertainty与failure gate。
- [VOL 06 PER-016](vol_06_per016.question_list.md)：1 道题卡，覆盖localization/odometry/SLAM、map/odom、loop/relocal/map merge、drift、ATE/RPE与五项目边界。
- [VOL 06 PER-019](vol_06_per019.html)：1 道题卡，覆盖Success/STOP、SPL/SoftSPL、denominator、failure taxonomy与五项目边界。

当前题库：

- [VOL 01 Foundations](vol_01_foundations.html)：39 题，review 见 [`vol_01_foundations.review.json`](vol_01_foundations.review.json)。
- [VOL 02 IL / RL / Post-training](vol_02_il_rl_posttraining.html)：40 题，review 见 [`vol_02_il_rl_posttraining.review.json`](vol_02_il_rl_posttraining.review.json)。
- [VOL 03 VLA / Action 完整卷](vol_03_vla_action.html)：44 题，全部 unseen；review 见 [`vol_03_vla_action.review.json`](vol_03_vla_action.review.json)。
- [VOL 04 World Model / Sim2Real](vol_04_world_model_sim2real.html)：aggregate 44/44，基础页 16 题、WM-011..038 为原子题卡，全部 unseen；review 见 [`vol_04_world_model_sim2real.review.json`](vol_04_world_model_sim2real.review.json) 与对应原子题卡 review。
- [VOL 04 WM-015 UWM coupling](vol_04_world_model_sim2real_wm015.html)：1 题，全部 unseen；review 见 [`vol_04_world_model_sim2real_wm015.review.json`](vol_04_world_model_sim2real_wm015.review.json)。
- [VOL 04 WM-016 Joint Objective](vol_04_world_model_sim2real_wm016.html)：1 题，全部 unseen；review 见 [`vol_04_world_model_sim2real_wm016.review.json`](vol_04_world_model_sim2real_wm016.review.json)。
- [VOL 04 WM-017 Heterogeneous Embodiment Schema](vol_04_world_model_sim2real_wm017.html)：1 题，全部 unseen；review 见 [`vol_04_world_model_sim2real_wm017.review.json`](vol_04_world_model_sim2real_wm017.review.json)。
- [VOL 04 WM-018 Prediction Horizon](vol_04_world_model_sim2real_wm018.html)：1 题，全部 unseen；review 见 [`vol_04_world_model_sim2real_wm018.review.json`](vol_04_world_model_sim2real_wm018.review.json)。
- [VOL 04 WM-020 Failure Diagnostics](vol_04_world_model_sim2real_wm020.html)：1 题，覆盖 posterior collapse、action ignoring、future leakage、background shortcut 与诊断矩阵；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm020.review.json`](vol_04_world_model_sim2real_wm020.review.json)。
- [VOL 04 WM-021 Dreamer Imagination Actor/Critic](vol_04_world_model_sim2real_wm021.html)：1 题，覆盖 replay posterior、prior imagination、lambda-return、gradient routing 与 model bias；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm021.review.json`](vol_04_world_model_sim2real_wm021.review.json)。
- [VOL 04 WM-022 MPC / CEM / MPPI / Best-of-N](vol_04_world_model_sim2real_wm022.html)：1 题，覆盖 proposal、scorer、N/H/K、latency、model/scorer bias 与 planning evidence；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm022.review.json`](vol_04_world_model_sim2real_wm022.review.json)。
- [VOL 04 WM-023 Open-loop / Receding-horizon](vol_04_world_model_sim2real_wm023.html)：1 题，覆盖 H/K、observation age、latency、queue、同步/异步 replan 与扰动恢复；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm023.review.json`](vol_04_world_model_sim2real_wm023.review.json)。
- [VOL 04 WM-024 Reward / Value / Success / Termination](vol_04_world_model_sim2real_wm024.html)：1 题，覆盖 reward、V/Q、success predicate/classifier、termination/continuation、timeout、calibration 与 denominator；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm024.review.json`](vol_04_world_model_sim2real_wm024.review.json)。
- [VOL 04 WM-025 Cosmos/WAM Slot / Mask / Loss](vol_04_world_model_sim2real_wm025.html)：1 题，覆盖 unified latent sequence、action/future/value slot、routing、condition/target mask、EDM loss 与项目边界；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm025.review.json`](vol_04_world_model_sim2real_wm025.review.json)。
- [VOL 04 WM-026 World/Value Auxiliary](vol_04_world_model_sim2real_wm026.html)：1 题，覆盖 action consequence、task progress、gradient alignment、matched ablation、negative transfer 与 WAM 真实性；保持 unseen；review 见 [`vol_04_world_model_sim2real_wm026.review.json`](vol_04_world_model_sim2real_wm026.review.json)。
- [VOL 05 Engineering / Evaluation Batch 1](vol_05_engineering_eval.html)：10 题，全部 unseen；review 见 [`vol_05_engineering_eval.review.json`](vol_05_engineering_eval.review.json)。
- [VOL 05 Engineering / Evaluation Batch 2A](vol_05_engineering_eval_batch2a.html)：3 题，全部 unseen；review 见 [`vol_05_engineering_eval_batch2a.review.json`](vol_05_engineering_eval_batch2a.review.json)。
- [VOL 05 EVAL-003 Success Rate / Confidence Interval](vol_05_engineering_eval_eval003.html)：1 题，保持 unseen；review 见 [`vol_05_engineering_eval_eval003.review.json`](vol_05_engineering_eval_eval003.review.json)。
- [VOL 07 OpenPiVLA Batch 1](proj_openpivla.html)：8 题，全部 unseen；PROJ-OPENPIVLA-007 已同步 official `pi05_libero` restore/norm-stats/client-connect 证据；review 见 [`proj_openpivla.review.json`](proj_openpivla.review.json)。
- [VOL 07 OpenPiVLA Batch 2](proj_openpivla_batch2.html)：4 题，全部 unseen；review 见 [`proj_openpivla_batch2.review.json`](proj_openpivla_batch2.review.json)。
- [VOL 07 Robot Harness Batch 1](proj_robot_harness.html)：8 题，全部 unseen；review 见 [`proj_robot_harness.review.json`](proj_robot_harness.review.json)。
- [VOL 07 OPD Batch 1](proj_opd.html)：8 题，全部 unseen；review 见 [`proj_opd.review.json`](proj_opd.review.json)。
- [VOL 07 WAM Batch 1](proj_wam.html)：4 题，保持 unseen；review 见 [`proj_wam.review.json`](proj_wam.review.json)。
- [VOL 07 UWM / LIBERO Batch 1](proj_uwm.html)：4 题，覆盖 fixed-pruned-init、reset-style、论文 OOD protocol、DataLoader/zarr stall、RoboCasa actionheadfix/open-loop/closed-loop 断层、结果 reconciliation 与 ownership 边界；保持 unseen；review 见 [`proj_uwm.review.json`](proj_uwm.review.json)。
- [VOL 08 SYS-VLA-001](vol_08_sys001.question_list.md)：1 道系统设计题，覆盖 dataset/run/bundle/evaluation/rollout lineage、metric namespace 与项目证据边界。
- [VOL 08 SYS-VLA-002](vol_08_sys002.question_list.md)：1 道系统设计题，覆盖 policy serving schema、chunk/replan、deadline/backpressure、real-time 与 controller/e-stop 边界。
- [VOL 08 SYS-VLA-003](vol_08_sys003.question_list.md)：1 道系统设计题，覆盖 fleet identity、capacity/placement、fairness/preemption、GPU/cache、robot lease 与 rollout/cost。
- [VOL 08 SYS-VLA-004](vol_08_sys004.question_list.md)：1 道系统设计题，覆盖 first divergence、fault state、safe-apply、lease fencing、rollback/replay、observability 与 e-stop 边界；保持 unseen/WARN。
- [VOL 08 CODE-VLA-001](vol_08_code001.question_list.md)：1 道手撕题，覆盖稳定 softmax/log-softmax、mask、低精度、梯度与 VLA 映射。
- [VOL 08 CODE-VLA-002](vol_08_code002.question_list.md)：1 道手撕题，覆盖 scaled dot-product attention、多头 shape、causal/padding mask、dropout 与 parity。
- [VOL 08 CODE-VLA-003](vol_08_code003.question_list.md)：1 道手撕题，覆盖 LayerNorm/RMSNorm、normalized shape、epsilon、dtype 与 parity。
- [VOL 08 CODE-VLA-004](vol_08_code004.question_list.md)：1 道手撕题，覆盖 masked MSE/Huber、valid denominator、empty mask、distributed reduction 与 VLA action schema。
- [VOL 08 CODE-VLA-005](vol_08_code005.question_list.md)：1 道手撕题，覆盖 SE(3) composition、frame 方向、point/vector/pose、inverse 与 roundtrip。
- [VOL 08 CODE-VLA-006](vol_08_code006.question_list.md)：1 道手撕题，覆盖二连杆 planar FK、relative joint angle、frame/单位、矩阵 parity 与 Jacobian 测试。
- [VOL 08 CODE-VLA-007](vol_08_code007.question_list.md)：1 道手撕题，覆盖离散 PID、output/i clamp、conditional integration、back-calculation、reset 与 VLA controller 边界。
- [VOL 08 CODE-VLA-008](vol_08_code008.question_list.md)：1 道手撕题，覆盖 Bellman TD(0)、terminated/truncated、timeout bootstrap、target detach、valid reduction 与 batch 对齐，保持 unseen。
- [VOL 06 PER-001](vol_06_per001.html)：1 题，保持 unseen；review 见 [`vol_06_per001.review.json`](vol_06_per001.review.json)。
- [VOL 06 PER-002](vol_06_per002.html)：1 题，保持 unseen；review 见 [`vol_06_per002.review.json`](vol_06_per002.review.json)。
- [VOL 06 PER-003](vol_06_per003.html)：1 题，保持 unseen；review 见 [`vol_06_per003.review.json`](vol_06_per003.review.json)。
- [VOL 06 PER-004](vol_06_per004.html)：1 题，保持 unseen；review 见 [`vol_06_per004.review.json`](vol_06_per004.review.json)。
- [VOL 06 PER-005](vol_06_per005.html)：1 题，保持 unseen；review 见 [`vol_06_per005.review.json`](vol_06_per005.review.json)。
- [VOL 06 PER-006](vol_06_per006.html)：1题，保持unseen；review见[`vol_06_per006.review.json`](vol_06_per006.review.json)。
- [VOL 06 PER-007](vol_06_per007.html)：1题，保持unseen；review见[`vol_06_per007.review.json`](vol_06_per007.review.json)。
- [VOL 06 PER-008](vol_06_per008.html)：1题，保持unseen；review见[`vol_06_per008.review.json`](vol_06_per008.review.json)。
- [VOL 06 PER-009](vol_06_per009.html)：1张L3/P1 atomic card，保持unseen；review见[`vol_06_per009.review.json`](vol_06_per009.review.json)。
- [VOL 06 PER-010](vol_06_per010.html)：1张L2/P0 atomic card，短答180字、机制338字，保持unseen；review见[`vol_06_per010.review.json`](vol_06_per010.review.json)。
- [VOL 06 PER-011](vol_06_per011.html)：1张L3/P0 atomic card，短答179字、机制338字，保持unseen；review见[`vol_06_per011.review.json`](vol_06_per011.review.json)。
- [VOL 06 PER-012](vol_06_per012.html)：1张L3/P1 atomic card，短答180字、机制350字，保持unseen；review见[`vol_06_per012.review.json`](vol_06_per012.review.json)。
- 总计280张已生成题卡，全部保持`unseen`；VOL 06的`VLA-PER-001..020`已全部计入；VOL 08 `SYS-VLA-001..004`与`CODE-VLA-001..008`题卡均已生成；WAM `PROJ-WAM-003..004` 已加入 save/load 与 eval provenance 题，UWM `PROJ-UWM-003..004` 已加入 DataLoader stall 与 actionheadfix 闭环断层题，但仍保持unseen。后续按source→knowledge→card与真实训练门推进。

题卡最低字段：

- 稳定 Question ID。
- L1 / L2 / L3 难度。
- 题源频次或“补充/项目追问”标识。
- 30 秒回答目标 ≤180 字；机制展开目标 ≤350 字。
- “易错”一句。
- 追问树与项目 hook。
- 论文/官方来源或本地 evidence。
- `unseen / weak / pass / strong / stale` 练习状态。

题目 ID 采用 `VLA-<DOMAIN>-NNN` 或 `PROJ-<PROJECT>-NNN`。同义题先合并，不按题量凑卷。
