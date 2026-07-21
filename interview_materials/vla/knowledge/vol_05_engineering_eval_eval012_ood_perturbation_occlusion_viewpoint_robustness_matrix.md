# VOL 05 EVAL-012：OOD、扰动、遮挡、视角与鲁棒性矩阵

> 状态：`drafted / VLA-EVAL-012 / knowledge_34_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 前置：[EVAL-003 Success Uncertainty](vol_05_engineering_eval_eval003.html)、[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-007 Coverage](vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)、[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)、[EVAL-010 Release Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)、[WM-035 Camera/Sensor](vol_04_world_model_sim2real_wm035_camera_sensor_modeling.html)  
> 来源冻结：[EVAL-012 Source Freeze](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)  
> 项目边界：五项目均没有 checkpoint-bound、clean–perturbed paired、按 severity 展开的 closed-loop robustness matrix；本页只给出评估合同。

## 问题（Question）

怎样设计 VLA 的 OOD、扰动、遮挡与视角鲁棒性测试，既能定位 failure mode，又不把不可解场景、协议变化或任意图像增强误当系统能力？

## 1. 一句话框架

```text
deployment survey -> target envelope + stress-only boundary
  -> freeze checkpoint/task/init/controller/predicate
  -> factor × severity matrix + clean paired anchor
  -> render/label/visibility/solvability gate
  -> raw closed-loop episodes
  -> per-cell k/n, drop, retention, curve, worst target cell
  -> robustness + safety/fallback release gate
```

`OOD` 是相对于训练或目标分布的关系，不是 suite 名字；鲁棒性结论是某 checkpoint、某任务支持、某协议和某扰动范围内的条件结论。

## 2. 三层 Envelope

| 层 | 范围来源 | 主要输出 |
| --- | --- | --- |
| target envelope | 真实相机 capture、标定、部署站点、incident 与 object/layout survey | 目标范围 success、drop、retention、worst cell |
| diagnostic OOD | 受控 one-factor，超出 train support 但任务仍可解 | failure localization 与 sensitivity curve |
| stress-only | blackout、极端遮挡、组合异常、未知频率 | detection、fallback、safe stop、recovery |

ImageNet-C 的五档 severity 是外部 stress 参考，不是目标相机的物理范围；训练没见过也不自动等于部署罕见。target 与 stress 必须分别进入报告和 gate。[1][2]

## 3. Taxonomy

| family | factor 示例 | 必存量 |
| --- | --- | --- |
| photometric | exposure、WB、brightness、contrast、noise、blur、compression、texture | unit/range/source/cadence；语言颜色 cue |
| viewpoint / geometry | translation、rotation、height、FOV、intrinsics/extrinsics、crop | mm/degree/FOV；target-in-frame/reachability |
| occlusion / visibility | self/object/environmental occlusion、lens obstruction、blackout | per-view visible fraction、duration、occluder/depth |
| sensor / missing-view | dropout、stale frame、timestamp jitter、packet loss | camera ID、presence mask、ms/Hz、cross-view correlation |
| scene / object / layout | unseen instance、background、table、layout、distractor、clutter | split/asset/layout ID、count/density、task validity |
| semantic / language | paraphrase、ambiguity、referent/color/relation shift | semantic equivalence、target transform、scorer contract |
| dynamics / timing | friction、mass、compliance、latency、control rate | SI unit；本页登记，EVAL-013 展开实时性 |

camera pose 不是普通 pixel augmentation：它会同时改变投影、可见率、背景和 workspace geometry。组合效应需要单列，不要混成“视觉 OOD”。

## 4. Robustness Cell Schema

```text
matrix/revision, policy_checkpoint_sha,
task/slice/init/seed, env/controller/predicate_sha,
family/factor/unit/severity/value/range_source,
cadence/temporal_and_cross_view_correlation,
clean_anchor_id/pair_id/perturbation_seed,
label_mode/target_transform,
target_or_stress, validity/solvability/rejection,
code_sha/asset_sha/render_proof,
episode/trace/video/outcome/critical_failure/fallback
```

`range_source` 防止 severity 任意化，`pair_id` 保证 clean 对照，`label/solvability` 防止任务被改掉，`code/asset/render proof` 防止“配置写了但扰动没生效”。

## 5. Paired Estimand

固定 checkpoint 与协议，对同一 task/init：

\[
\Delta_{i,f,s}=Y^{\mathrm{pert}}_{i,f,s}-Y^{\mathrm{clean}}_i.
\]

变量解释：`Y∈{0,1}`来自同一 success predicate，`f/s` 是唯一受控扰动。直觉：`Δ=-1` 是 perturbation 引入的配对失败。实现映射：serialize initial state 或绑定 init/seed；若随机性不能完全复现，则在相同 strata 做 matched allocation，并保存 pair validity。

换了 reset、controller、success predicate、checkpoint 或 task mix 后的两个百分比，不是 robustness drop。[3]

## 6. Severity Contract

每个 factor 保存：

1. unit、实际值与 lower/upper；
2. range 来自 target quantile、calibration、diagnostic 还是 stress reference；
3. per-episode、per-step 或连续相关 cadence；
4. 多 camera 独立/共同/条件相关；
5. transform revision、随机 seed 和实际生效 proof；
6. validity rejection 与 monotonicity sanity check。

ImageNet-C 用 15 corruption × 5 severity 覆盖 noise、blur、weather、digital。[1] 可借鉴的是 per-factor curve；不同 factor 的 severity-3 没有共同物理含义，不能粗暴平均。

## 7. Occlusion、Label 与 Solvability

\[
r_{\mathrm{vis}}=\frac{|M_t\cap M_v|}{|M_t|+\epsilon}.
\]

变量解释：`M_t` 是无遮挡 target mask，`M_v` 是实际可见区域。实现映射：保存每相机 visible fraction、occluder、depth order、duration、mask overlay；区分 task-natural、environmental、sensor obstruction 与 full blackout。[2]

执行前逐格检查：referent/语义仍一致，目标至少有允许的感知路径，目标与 grasp/placement 仍可达，collision/physics 合法，predicate 不受 perturbation code 影响。不可解样本进 rejected ledger；故意 blackout 进入 safety/fallback cell，不与 nominal completion 混算。

## 8. 指标矩阵

每格先报 `k/n + CI`，再报 absolute paired drop。相对保持率：

\[
\operatorname{Retention}_{f,s}=\frac{p_{f,s}}{\max(p_0,\epsilon)}.
\]

变量解释：`p0` 是同支持 clean success，`p_f,s` 是扰动成功率。实现映射：clean 很低时 retention 不稳定，必须同时看 absolute success/drop；`p0=0` 时标 `not interpretable`。

目标范围的最差格：

\[
R_{\mathrm{worst}}=\min_{(f,s,g)\in\Omega_{\mathrm{target}}}p_{f,s,g}.
\]

变量解释：`g` 是 critical task/slice。实现映射：critical cells 事前冻结并逐格带 CI；后验找最差格要说明探索性。还应给 severity curve/AUC、paired discordant counts、critical failure、fallback activation 与 recovery。overall 平均只是辅助，不能掩盖某个 viewpoint 或 occlusion 崩溃。

## 9. One-factor 先于 Composed Stress

one-factor matrix 用来定位 causal sensitivity；composed stress 用来测真实共现和系统安全。组合时冻结 joint distribution、correlation 与 interaction 对照。低照度与高 sensor noise 可以相关，多相机共同 blackout 与独立 dropout 也是不同事件。

任意 factor 笛卡尔积会制造不可解、低概率样本和统计稀释。先覆盖 critical single factors，再加入部署 incident 支持的组合。

## 10. 统计与 Gate

- clean/perturbed 同 pair：报告 discordant pairs 与 paired uncertainty；
- task、scene、object instance、robot-day 重复：按 cluster 聚合/重采样；
- 每格 `k/n/CI` 优先于一个 macro score；
- target floor/worst-cell 与 stress fallback gate 分开；
- clean regression、critical safety veto、robustness threshold 一同进入 EVAL-010；
- simulator 或 offline corruption 结果只能作证据层，不能替代必要 real closed-loop canary；
- policy/scorer/camera/perturbation revision 变化后重新建 matrix。

## 11. 两个外部锚点

### ImageNet-C

提供 15 类 corruption、四组 taxonomy、五个 severity 与 corruption-wise aggregation。[1] 对 VLA 的价值是提醒“分 factor、分强度、带 clean anchor”；其 top-1 error/mCE、severity 参数和 pixel transform 不自动对应 action、任务可解性或真实相机分布。

### SIMPLER

在机器人 manipulation 中沿 background、lighting、distractors、table texture、robot camera pose 做 controlled shifts，并比较 sim-real policy behavior。[4] 可借鉴的是保持任务并分轴验证；SIMPLER 结果不能迁移成用户项目结论，simulation 也不完全替代 real evaluation。

## 12. 五项目边界

### Robot Harness

`OOD/D` 只是 suite 标签；tool/safety/browser 的 scorer 与分母并不统一，且无视觉/相机/控制 perturbation episode。browser 还是 format-only，不能称 closed-loop robustness。

### OPD

`seen/unseen/hard`、`boundary/format_conflict` 与 by-pool curve 是静态 point/box/text 分层；没有物理 severity、paired clean/perturbed robot episode。

### OpenPiVLA

parser/roundtrip/format robustness 仍待补，97.4 缺 raw eval bundle；没有 checkpoint-bound occlusion/viewpoint/OOD matrix。

### WAM

单个 CoffeePressButton manifest 有三路 `224×224` camera、`obj_instance_split=B`、一个 layout/style，base/trained 都失败。camera 字段不是 viewpoint ablation，两个 episode 也不是 curve。

### UWM

`186/250` fixed-pruned-init 与 `232/250` reset-style 改了 protocol，不能解释为同 checkpoint 的扰动保持率；还缺 raw episode 与论文 Table II 对齐。

## 13. Artifact 与伪代码

```text
robustness_eval/
  matrix_spec.yaml
  protocol_manifest.json
  paired_episode_index.parquet
  accepted_rejected.jsonl
  perturbation_proofs/
  raw/{traces,videos,outcomes}/
  summaries/{per_cell.parquet,severity_curves.json,critical_gate.json}
  checksums/manifest-sha256.txt
  reproduce.ps1
```

```python
def robustness_matrix(policy, spec, protocol):
    # Freeze target/stress ranges and every non-perturbation protocol component.
    spec = validate_range_provenance_and_protocol(spec, protocol)

    # Match every perturbed episode to a clean task/init anchor.
    pairs = materialize_paired_cells(spec, protocol)

    # Verify effective values, labels, visibility, physics and solvability.
    pairs = render_and_validity_gate(pairs, spec)

    # Run closed loop and retain raw traces, videos, masks and outcomes.
    bundle = execute_immutable_episodes(policy, pairs, protocol)

    # Preserve cells and pair/cluster structure before any macro aggregation.
    stats = summarize_k_n_ci_drop_retention_curves(bundle, spec)
    stats["worst_target"] = preregistered_worst_cell(stats, spec)
    return write_recomputable_bundle(bundle, stats, spec)
```

伪代码是评估合同，不是本地已有实现。

## 14. 面试防线与下一入口

- `OOD` suite 名字不等于真实分布外能力；
- train augmentation 不等于 test-time robustness evidence；
- 多 camera 字段不等于 viewpoint robustness；
- 不同 reset/protocol 的成功率不能作 paired drop；
- 不可解 occlusion 要拒收或转入 stress/fallback；
- overall 平均不能隐藏 critical worst cell；
- 五项目当前只能讲补证据设计，不能报已完成矩阵。

EVAL-012 知识与一张题卡保持 `WARN/unseen`。下一节点是 `VLA-EVAL-013`：端到端 latency、control frequency 与实时性评估。没有真实口述前不创建 `coaching_state.md`。

## 参考文献（References）

1. Hendrycks & Dietterich, [*Benchmarking Neural Network Robustness to Common Corruptions and Perturbations*](https://arxiv.org/abs/1903.12261v1), ICLR 2019；[官方代码](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f)。
2. [WM-032 Visual DR](../sources/vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)、[WM-035 Camera/Sensor](vol_04_world_model_sim2real_wm035_camera_sensor_modeling.html)、[PER-003 Multi-view/Temporal](vol_06_per003_multiview_temporal.html)。
3. [EVAL-003/005/006/007/009/010/011 canonical prerequisites](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)。
4. Li et al., [*Evaluating Real-World Robot Manipulation Policies in Simulation*](https://arxiv.org/abs/2405.05941v1), 2024；[`SimplerEnv`](https://github.com/simpler-env/SimplerEnv/tree/06accaca93535902d408da4855f21cece12bceb7)。
5. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目 inventories。
