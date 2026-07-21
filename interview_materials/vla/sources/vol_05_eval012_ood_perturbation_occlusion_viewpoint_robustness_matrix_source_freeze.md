# VOL 05 EVAL-012 Source Freeze：OOD、扰动、遮挡、视角与鲁棒性矩阵

> 状态：`source_frozen / VLA-EVAL-012 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结 perturbation taxonomy、target-envelope / stress-only 边界、clean–perturbed 配对、severity、visibility / solvability gate、分格指标与可复算 artifact；只生成一张 `VLA-EVAL-012` 原子题卡，VOL 05 同步为 knowledge/cards 34/44。

## 问题（Question）

怎样证明 VLA 在 OOD、视觉扰动、遮挡与视角变化下仍然鲁棒？出现 `OOD` suite、数据增强、多相机字段或两种 protocol 的成功率都不够。可信评估要先定义部署目标范围，把一个 checkpoint 在同 task/init/controller/predicate 下的 clean episode 与可核验 perturbation 成对，再按 family × severity × slice 展开，而不是用一个 overall success 掩盖局部崩溃。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Hendrycks & Dietterich, *Benchmarking Neural Network Robustness to Common Corruptions and Perturbations* | primary paper；arXiv `1903.12261v1`，2019-03-28；论文许可未断言 | arXiv API `b2eeb8443e7c9277655b7ec4d44c20afeeb7a0254298b93b2a18b28effb78b12`；ar5iv HTML `d3c445b259eb3af5381f0bba396d902bc28923fb8f743ce95107df734e33381f` | 15 类 corruption、noise/blur/weather/digital 四组、每类五个 severity、clean anchor、per-corruption 与 aggregate error 思想 | VLA action/closed-loop robustness；物理可解性；真实相机范围；机器人 OOD 结论 |
| S2 | `hendrycks/robustness` | official-code；commit `8190fe329f5f072a06e3a2aea02bb5dda69aed9f`（2022-08-24）；Apache-2.0 | README `718d37a53a84615961dcdf519602cfaf1467b192bb691f8e880fbadf9e92de0d`；ImageNet-C generator `3868a670617f6b931ad09d5613bf372962a47d17c2de4f15ccaec28feb9fa479`；LICENSE `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | corruption implementation入口与 severity-indexed generation | 用户项目已运行；VLA label 仍保持；target capture envelope |
| S3 | Li et al., SIMPLER | primary paper；arXiv `2405.05941v1`，2024-05-09；论文许可未断言 | arXiv API `a20cd969be3c4a310fbdc719d695873d0f541501eb8b023ee5bf6b9ea5baa79d`；ar5iv HTML `19db19183e0c55e2d41358fc8f290d2d6326ad86ef62ecae8c17ae5b8521e97d` | background、lighting、distractor、table texture、robot camera pose 五轴的 controlled distribution shifts；paired sim-real behavior | 任意 simulator 都能替代 real；用户项目已有同等矩阵 |
| S4 | `simpler-env/SimplerEnv` | official-code；commit `06accaca93535902d408da4855f21cece12bceb7`（2025-12-20）；MIT | README `81aaa39d59e41c6b60d6ccdf09c17b1f0ca284ce7cb780b62b908afac6c0dc28`；metrics `ee8596be6997d41295bf5b25f90c9b5b3ba47ef2bd92296b8c45e7ffc5606dc6`；LICENSE `c28645822e5cdadf816144773ee153332449ae04aa6f0b6a6393e5611092f878` | 可追溯机器人评估实现与指标入口 | 本页设计已经在五项目运行 |
| S5 | WM-032 / WM-035 / PER-003 | canonical local prerequisites | WM-032 `9086b6072047f3578cb731f48f08c48b509d7d38924b801728039b83d6245710`；WM-035 `50918b15cb279159a48e5526393164a866f3061a56ff202273f9a18aa505ad75`；PER-003 `a62fbea8507ff46c9636f0cb3280516546f4f01a3d02ebe777b55877f9338e19` | factor/range/label contract、camera/sensor/occlusion、multi-view/time identity 与 dropout | 新增项目证据；closed-loop 成功数字 |
| S6 | EVAL-003/005/006/007/009/010/011 | canonical local prerequisites | EVAL-003 `3d00ba8ac8345b1bf08e7530a0e681048fd01b64abfbadf9fab4ca60ab4d490f`；EVAL-005 `16b6a4c7c8e284ca8bd8a7cc831c3fc553405668ea87a071c23147f8f804ff46`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-007 `66800fd21d8d2ebb786b0f8d3234c2613b427a986f41432f93cba99c3596e278`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd` | k/n uncertainty、aggregation、protocol/coverage、recomputable bundle、release gate与proxy边界 | 五项目已有 robustness matrix |
| S7 | 五项目 inventories + WAM manifest | local-evidence | Robot Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d`；WAM manifest `1ab8709201e2e75f580cb0aa0f8465defb546d63b2aab70a1752239a7da8f697` | 当前 OOD / view / protocol 字段与缺口 | 真实 perturbation episode、severity curve 或系统鲁棒性结论 |

S1/S2 是分类 benchmark：它证明了多 corruption × 多 severity 的标准化测试思想，但它的 severity 不是用户相机的物理单位，top-1 error 也不是 VLA success。S3/S4 是机器人主锚点：SIMPLER 在 background、lighting、distractor、table texture、camera pose 五轴比较 policy behavior，并强调 simulation 仍是 real evaluation 的补充。以下统一矩阵是 source-consistent engineering synthesis，不冒充论文原始 schema。

## 2. 先定义 Robustness Estimand

鲁棒性不是“在 OOD 集上还有一个分数”，而是固定 policy 与任务协议后，对受控环境变化的条件性能：

\[
p_{f,s,g}=\Pr(Y=1\mid \pi,\mathcal{T}_g,\mathcal{P},F=f,S=s),
\]

其中 `π` 是 checkpoint，`T_g` 是 task/slice，`P` 绑定 env/controller/success predicate，`f` 是 perturbation family，`s` 是 severity。变量解释：只允许扰动轴变化；实现映射：每一格都要回到 manifest、paired episode rows 与 `k/n`。若同时换 checkpoint、reset、controller 或 scorer，差值不再识别 robustness。

### 2.1 三种边界必须分开

| 区域 | 来源 | 用途 | 可以说 | 不能说 |
| --- | --- | --- | --- | --- |
| target envelope | 部署 capture / calibration / incident / site survey 的分位数或物理上限 | 发布主结论 | 目标范围内 retention / worst-cell | 超出已采样任务与硬件的保证 |
| diagnostic OOD | one-factor、可解、故意超出训练分布但仍接近任务 | 找 failure mode | 在该冻结测试格上的性能变化 | 等于真实世界频率 |
| stress-only | blackout、极端遮挡、组合最坏情况或未知频率 | fallback / safety gate | 系统是否拒绝、停机或恢复 | 作为 nominal success 平均的一部分 |

训练分布之外不自动等于部署 OOD；部署中常见但训练没覆盖的值可能在 target envelope 内。反过来，ImageNet-C severity-5 可以是 stress reference，却不能替代 target capture survey。[S1][S5]

## 3. Perturbation Taxonomy

| family | 典型 factor | severity / unit | 标签与有效性关键点 |
| --- | --- | --- | --- |
| photometric / appearance | brightness、contrast、exposure、WB、gamma、noise、blur、compression、texture | lux / exposure / SNR / blur px，或冻结 stress index | color/material instruction 可能 semantic-changing |
| geometry / viewpoint | camera translation/rotation、height、FOV、intrinsics/extrinsics、crop | mm、degree、pixel、FOV degree | 同一 task geometry；检查 target 仍在 frame 与 reachability |
| occlusion / visibility | hand/object/self-occlusion、container、人、镜头污渍、blackout | target visible fraction、duration、camera count | 区分 task-natural、environmental、sensor obstruction 与 failure |
| sensor / missing-view | dropout、stale frame、timestamp jitter、packet loss、compression | missing mask、ms、Hz、loss rate | 保留 camera identity；多视角相关性与共同缺失单列 |
| scene / object / layout | object instance、background、table texture、layout、distractor、clutter | instance/split ID、distance、count、density | 任务目标与 success predicate 不变；不可解 layout 拒收 |
| semantic / language | paraphrase、referent ambiguity、distractor instruction、color/relational cue | template/family/ambiguity level | 语义等价与任务改变分开；不能只改 prompt 不改 target |
| dynamics / timing | mass/friction/compliance、latency、control rate | SI units、ms、Hz | 本页仅登记矩阵槽位；详细 latency 归 EVAL-013，动力学前置见 WM-033/034/036 |

一个 transform 可能跨层：camera pose 同时改变投影、可见率和 reachable workspace；它不能简单记作“图像增强”。

## 4. 每个 Matrix Cell 的最小 Schema

```text
matrix_id, revision, policy_checkpoint_sha,
task_id, task_slice, init_id, seed, controller_sha, predicate_sha,
family, factor, unit, severity_id, value_or_range,
range_source, cadence, temporal_correlation, cross_view_correlation,
clean_anchor_id, pair_id, perturbation_seed,
label_mode, target_transform, target_envelope_or_stress,
validity_status, solvability_status, rejection_reason,
perturbation_code_sha, asset_sha, render_proof_uri,
episode_uri, trace_uri, video_uri, outcome, critical_failure, fallback
```

字段直觉：`family/factor/severity`回答改了什么，`range_source`回答为什么取这个范围，`pair_id`回答和哪个 clean episode 对比，`label/solvability`防止任务被偷偷改掉，`code/asset/render proof`证明扰动真的生效。

## 5. Clean–Perturbed 配对

对 task/init pair `i`、family `f`、severity `s`：

\[
\Delta_{i,f,s}=Y^{\mathrm{pert}}_{i,f,s}-Y^{\mathrm{clean}}_i.
\]

变量解释：`Y∈{0,1}`使用同一 success predicate；`Δ=-1`表示 clean 成功而 perturbed 失败，`+1`表示相反。实现映射：同 checkpoint、task、init、controller、predicate、episode budget；随机性无法完全相同时绑定 seed/initial-state serialization，并保存配对失败原因。

不应把一批容易 clean init 与一批更难 perturbed init 比较。若 simulator determinism 不足，至少按 task/init strata 做 matched allocation，并在 task 或 scene cluster 层统计不确定性。[S6]

## 6. Severity 不是随便编号 1–5

ImageNet-C 用每类五个 severity，覆盖 noise、blur、weather、digital 共 15 类 corruption。[S1][S2] VLA 可借用“同类多强度、画曲线”的思想，但机器人矩阵还要记录：

1. 物理单位或目标 capture quantile；
2. `target-derived`、`diagnostic` 或 `stress reference` 来源；
3. 每 episode 固定、每 step 采样或连续相关过程的 cadence；
4. 多 camera 独立、共同或条件相关；
5. 实际生效值与 rejection；
6. severity monotonicity sanity check。

不同 family 的 `severity=3` 没有共同物理尺度，不能直接平均后称“平均三档 OOD”。若 range 后续扩展，增加 revision，不静默覆盖旧曲线。

## 7. Occlusion 与 Solvability Gate

目标可见率：

\[
r_{\mathrm{vis}}=\frac{|M_t\cap M_v|}{|M_t|+\epsilon}.
\]

变量解释：`M_t` 是未遮挡 target mask，`M_v` 是实际可见区域；实现映射：保存 occluder ID、depth order、每相机 `r_vis`、持续时间和 overlay。单个矩形贴片不是所有遮挡的充分代理。[S5]

每个 perturbed episode 必须经过：

1. target/referent 是否仍存在且语义一致；
2. 至少一条允许的感知路径是否可见；
3. 目标/容器/抓取位姿是否仍可达；
4. collision 与物理初始化是否合法；
5. success predicate 是否未被扰动代码影响。

不可解样本进入 rejected ledger；若故意测 blackout/failure，进入 stress/safety cell，并把安全停机、fallback 或 recovery 作为目标，不能把“无法完成原任务”与普通 robustness 混成一个 success drop。

## 8. 指标：曲线、Retention 与 Worst Cell

每格先报告 `k/n` 与区间，再与 clean anchor 比较。定义：

\[
\operatorname{Retention}_{f,s}
=\frac{p_{f,s}}{\max(p_0,\epsilon)}.
\]

变量解释：`p_0` 是同支持 clean success，`p_f,s` 是扰动成功率；实现映射：同时展示 absolute drop，因为 clean 很低时 retention 会失真。若 `p0=0`，retention 标 `not interpretable`。

对目标范围 `Ω_target`：

\[
R_{\mathrm{worst}}=\min_{(f,s,g)\in\Omega_{\mathrm{target}}}p_{f,s,g}.
\]

变量解释：最差 family × severity × critical slice；实现映射：预注册 critical cells，给每格 `k/n/CI`，避免后验搜索最差点后只报裸值。还应报告 per-severity curve / AUC、paired discordant counts、critical failure、fallback activation 与 recovery。overall average 只能作辅助，不能掩盖 camera-pose 或 occlusion 崩溃。

## 9. One-factor 与 Composed Stress

先做 one-factor 诊断，定位 brightness、viewpoint、visibility、instance 或 distractor 的独立敏感性；再做符合部署共现结构的 composed cells。任意笛卡尔积会产生大量不真实或不可解场景，也无法解释 failure 来源。

组合扰动需额外冻结 joint distribution / correlation 与 interaction 对照。例如低照度和高 sensor noise 可以相关；多相机同时 blackout 与单相机 dropout 是不同系统事件。composed stress 不能反向冒充单因素因果结论。

## 10. 统计与 Release Gate

- 使用相同 episode pair 时，报告 paired success drop / discordant pairs；
- task、scene、object instance 或 robot-day 重复时按 cluster 聚合/重采样；
- 多 cell 探索与预注册 critical gate 分开；
- 同时看 absolute success、drop、retention、worst target cell 与 uncertainty；
- target-envelope gate 与 stress-only fallback gate 分开；
- clean regression、critical safety veto、robustness floor 共同进入 EVAL-010 release gate；
- offline corruption 或 simulator robustness 不替代必要的真实 closed-loop canary。[S3][S6]

## 11. SIMPLER 与 ImageNet-C 如何正确使用

SIMPLER 直接展示了 background、lighting、distractors、table texture、robot camera pose 五个 distribution-shift 轴，并在多 policy 的 sim-real evaluation 中比较行为；论文观察到 camera pose 与 table texture 等轴会产生不同敏感性。[S3] 可借鉴的是“控制轴、保持任务、分轴比较、真实对应验证”，不是复制其结果到另一机器人。

ImageNet-C 给出 15 corruption × 5 severity 和 corruption-wise aggregation。[S1][S2] 可借鉴的是 factorized severity curve 与 clean anchor；不能把 top-1 mCE 当 VLA success，也不能假定其 pixel transform 符合真实相机噪声、遮挡或任务语义。

## 12. 五项目 Evidence Mapping

| 项目 | 已有线索 | 缺失 | 当前结论 / 安全表述 |
| --- | --- | --- | --- |
| Robot Harness | `OOD/D` suite 名称；tool/safety/browser 指标 | 视觉/相机/控制 perturbation、severity、paired episode；base/SFT/GRPO 的 n/scorer 不同；browser 为 format-only | 只能讲 suite 分层；不能称系统 robustness matrix |
| OPD | `seen/unseen/hard`、`boundary/format_conflict`、raw-holdout、by-pool/checkpoint curve | 物理 severity、matched clean/perturbed pair、closed-loop outcome | 是静态 grounding slice，不是 VLA closed-loop robustness |
| OpenPiVLA | parser/roundtrip/format robustness 待补；97.4 summary | raw eval bundle、checkpoint-bound occlusion/view/OOD matrix | 只能列补证据合同；不能报 robustness |
| WAM | CoffeePressButton episode 0 manifest 有三路 `224×224` camera、`obj_instance_split=B`、单个 `layout/style=[1,1]`；base/trained 均失败 | 多场景、多 episode、受控 view/layout/style cells、checkpoint 核验 | 多 camera 字段不等于 viewpoint robustness；两个失败不能形成曲线 |
| UWM | fixed-pruned-init `186/250`；reset-style `232/250` | 与论文 Table II 一致的 OOD protocol、raw episode、checkpoint-bound paired matrix | strict/reset 改变 protocol，是 confound，不是校准扰动 |

出现 `OOD` 标签、不同协议数字、train augmentation 或 camera list 都不能替代可复算 perturbation evidence。本节点不新增任何项目结果。

## 13. 最小 Artifact Bundle

```text
robustness_eval/
  matrix_spec.yaml             # families, factors, units, ranges, source, cadence
  protocol_manifest.json       # policy/task/init/controller/predicate revisions
  paired_episode_index.parquet # clean_id, perturbed_id, pair validity
  accepted_rejected.jsonl      # validity, solvability, actual values, reasons
  perturbation_proofs/         # sample render, mask/overlay, calibration checks
  raw/{traces,videos,outcomes}/
  summaries/per_cell.parquet
  summaries/severity_curves.json
  summaries/critical_gate.json
  checksums/manifest-sha256.txt
  reproduce.ps1
```

## 14. 评估伪代码

```python
def evaluate_robustness(policy, matrix_spec, protocol):
    # Freeze policy, task/init/controller/predicate and derive ranges from named sources.
    spec = validate_target_and_stress_envelopes(matrix_spec, protocol)

    # Generate a clean anchor and perturbation with identical task/init allocation.
    pairs = materialize_clean_perturbed_pairs(spec, protocol)

    # Prove the perturbation took effect and reject invalid or unsolvable episodes.
    pairs = render_label_visibility_solvability_gate(pairs, spec)

    # Run immutable episodes and retain raw traces, videos, masks and outcomes.
    bundle = execute_and_store(policy, pairs, protocol)

    # Summarize every cell before macro views; preserve paired and cluster structure.
    stats = per_cell_k_n_ci_drop_retention_curve(bundle, spec)
    stats["worst_target"] = preregistered_worst_cell(stats, spec.target)
    stats["stress_fallback"] = score_stress_safety_behavior(bundle, spec.stress)
    return write_recomputable_bundle(bundle, stats, spec)
```

这是 evaluation contract，不是五项目已有实现。

## 15. Source Gate 结论与下一入口

EVAL-012 保持 `WARN`：ImageNet-C 冻结了 corruption × severity 的外部方法参考，SIMPLER 冻结了机器人 distribution-shift 的一手案例，WM-032/035 与 PER-003 提供 label/camera/visibility/view 前置。本页完成 target vs stress、paired cell、severity provenance、solvability、指标和 artifacts 的工程闭环；五项目均缺可核验的 closed-loop robustness matrix。

下一节点固定为 `VLA-EVAL-013`：端到端 latency、control frequency 与实时性评估。真实口述前不创建 `coaching_state.md`。

## References

1. Hendrycks & Dietterich, [*Benchmarking Neural Network Robustness to Common Corruptions and Perturbations*](https://arxiv.org/abs/1903.12261v1), ICLR 2019；[ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1903.12261)。
2. `hendrycks/robustness` commit [`8190fe3`](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f)，[ImageNet-C generator](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/create_c/make_imagenet_c.py)，Apache-2.0。
3. Li et al., [*Evaluating Real-World Robot Manipulation Policies in Simulation*](https://arxiv.org/abs/2405.05941v1), 2024；`simpler-env/SimplerEnv` commit [`06accaca`](https://github.com/simpler-env/SimplerEnv/tree/06accaca93535902d408da4855f21cece12bceb7)，MIT。
4. [WM-032 Visual DR](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)、[WM-035 Camera/Sensor](vol_04_wm035_camera_sensor_modeling_source_freeze.html)、[PER-003 Multi-view/Temporal](vol_06_per003_multiview_temporal_source_freeze.html)。
5. [EVAL-003](vol_05_eval003_success_rate_confidence_interval_source_freeze.html)、[EVAL-005](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-007](vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)、[EVAL-009](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-011](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)。
6. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目 inventories。
