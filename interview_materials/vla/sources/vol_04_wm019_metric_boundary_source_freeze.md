# VOL 04 WM-019 Source Freeze：World-Model Metric Boundary

> 审计日期：2026-07-17  
> 状态：`source_frozen / metric-ladder / WARN`  
> 覆盖题目：`VLA-WM-019`  
> 本轮边界：本页只冻结 PSNR/SSIM/FVD、latent loss、action MSE、world/value proxy 与 downstream success 的统计语义和可比性边界；下游 knowledge page 与一张 `unseen` 题卡已在后续独立切片生成。

## 1. 问题与结论边界

题目：**PSNR/SSIM/FVD、latent loss、action MSE 与 downstream success 各能证明什么？**

冻结结论：

1. PSNR/SSIM 主要描述像素级重建/结构相似，FVD 类指标描述视频分布或感知质量（依实现而定）；它们不能单独证明 action consequence、物理接触或 policy success。[S1]
2. latent/video loss 说明某个 prediction target 的拟合程度；action MSE 说明标签拟合程度；两者都可能与 causal action validity、long-horizon rollout 和 controller execution 脱钩。[S1][S2]
3. world/value proxy、WorldGym VLM proxy、simulator success 与 real closed-loop success 是不同统计单元和环境合同，不能混成一个“成功率”。[S2][S3]
4. 可比较结果至少要固定 model/checkpoint、data split、schema/normalizer、horizon/replan、reset/init、camera/preprocess、seed、success predicate、episode denominator 和 metric script。[S2][S3]
5. metric ladder 的作用是定位证据层级：offline target fit → open-loop/latent rollout → world-model proxy → simulator closed loop → real closed loop；向上一级不能只靠下一级的平均分外推。[S1][S2]

## 2. 来源冻结

| ID | 来源 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- |
| S1 | [World Model Foundations Audit](vol_04_world_model_foundations_claim_to_code.html) | PSNR/SSIM/FVD/latent/action/reward/value/closed-loop 的 proxy boundary、one-step/open-loop compounding | 本地模型指标、任何指标普适优越性 | checked / WARN |
| S2 | [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html) | action/image MSE 的 conditional proxy、LIBERO rollout wrapper、metric protocol fields | MSE 等于 success、未运行 checkpoint 的 rollout 结果 | checked / WARN |
| S3 | [Benchmark / Evidence Audit E](vol_04_benchmark_evidence_claim_to_protocol.html) | strict tuple、reset/init、WorldGym proxy 与 simulator/real success 分层 | WorldGym VLM score 等于 simulator/real success | checked / WARN |
| S4 | [EVAL-003 statistical freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.html) | episode-level Bernoulli、denominator、cluster/aggregation 和 success CI 边界 | box/point/text pool 或 raw row 自动等于 episode success | supporting / WARN |
| S5 | project inventories | 用户 UWM/WAM/OpenPiVLA/OPD evidence 的 artifact/denominator 缺口 | 项目页数字已形成同一 metric contract | local / WARN |

## 3. Metric ladder

| 层级 | 典型指标 | 它能证明 | 它不能证明 |
| --- | --- | --- | --- |
| offline target fit | action MSE、latent MSE/L1、reward/value loss | 固定 split/target/reduction 下的拟合 | causal intervention、rollout stability、success |
| teacher-forced one-step | PSNR/SSIM、one-step latent/video error | 给定真实历史时的局部预测 | 自回归长期误差、控制可用性 |
| open-loop rollout | per-offset error、video FVD/proxy、latent drift | 模型使用自身预测时的稳定性线索 | simulator/real contact 与 task success |
| world-model proxy | WorldGym VLM score、generated-video task score | proxy environment/scorer 下的方向性筛选 | simulator predicate、real robot success |
| simulator closed loop | LIBERO/RoboCasa success | 固定 environment/controller/reset/success predicate 下的 episode outcome | real hardware transfer、单独归因某个 head |
| real closed loop | hardware episode success、failure trace | 指定 robot/controller/protocol 的最终任务结果 | 泛化到其他 embodiment 或解释所有内部机制 |

## 4. 指标语义与失败模式

### PSNR / SSIM / FVD

PSNR 对像素误差敏感，SSIM 关注局部结构；FVD 等视频感知/分布指标依赖 feature extractor、clip length、sample count 和实现。背景、光照或纹理改善可能让视觉指标上升，但 action-sensitive contact、物体状态和任务 predicate 不变。

### Latent / action MSE

latent loss 受 VAE/feature scale、normalizer 和 target mask 影响；action MSE 受 action semantics、axis、gripper、horizon、padding 与 reduction 影响。UWM validation 的 marginal/forward/inverse/joint action/image MSE 是各自 conditional proxy，不等于 LIBERO strict success。[S2]

### Success / proxy success

success 必须绑定 episode/task/init/controller/success predicate 和有效分母。WorldGym 由生成视频和 VLM scorer 得到的 proxy 与 simulator `check_success`、real hardware predicate 不同，不能在同一表格直接平均。[S3]

## 5. 可比性合同

两个结果 (hat m_a,hat m_b) 只有在以下字段一致或已分层时才可解释为模型差异：

- checkpoint/model revision、processor/normalizer revision；
- data split、target schema、metric script、reduction/valid mask；
- camera/preprocess、task/suite、initial state、warmup、horizon、chunk/replan；
- controller、seed/determinism、episode/trial denominator、success predicate；
- proxy scorer/version（若为 WorldGym/VLM）或 simulator/environment version。

如果 protocol 不同，差值同时包含 model effect 与 protocol effect；“相同任务名”不足以建立可比性。

## 6. 最小评估矩阵

| 诊断 | 需要记录 | 目的 |
| --- | --- | --- |
| one-step vs open-loop | per-offset error、teacher/open-loop、horizon | 发现 compounding gap |
| action sensitivity | fixed observation、action perturbation、future delta | 发现 action ignoring/visual shortcut |
| proxy vs simulator | same checkpoint、same init/task、scorer/predicate | 判断 proxy rank 是否可迁移 |
| simulator vs real | controller/camera/normalizer/latency、episode trace | 定位 sim2real gap |
| metric implementation | target mask、reduction、valid count、dtype | 防止 loss/metric 计算错误 |
| statistics | episode id、k/n、cluster、seed/task aggregation | 防止把 row/step 当独立 rollout |

## 7. 项目证据边界

- UWM 的 action/image MSE、LIBERO success、fixed-pruned-init 和 reset-style 必须按各自 protocol 命名；不能用一个 proxy 替代另一个。
- WAM 的 held-out MSE、planning uplift、0-success 和官方 baseline 需要 checkpoint、prediction/label artifact、episode trace、scorer 与 denominator；没有这些只能保持 WARN。
- OpenPiVLA 的 97.4%、OPD 的 10k raw-holdout 和其他项目数字不能自动套用 episode-level success CI；统计单位要按 task/format/pool 重新定义。[S4]

## 8. Review 结论与下一步

本 source freeze 为 `WARN`：metric ladder、proxy/closed-loop boundary、protocol tuple 与统计单位已冻结；本地 per-offset/open-loop、proxy-vs-simulator paired test、checkpoint/denominator artifact 和真实 episode traces 仍 pending。

下游 `knowledge/vol_04_world_model_sim2real_wm019.*` 与 `questions/vol_04_world_model_sim2real_wm019.*` 已在后续独立 bounded slices 完成，题卡保持 `unseen`。下一步进行 WM-015..019 真实口述或补 paired/evidence artifacts；WM-020..038 继续后置。

## 参考来源

1. [World Model Foundations Audit](vol_04_world_model_foundations_claim_to_code.html)。
2. [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html)。
3. [Benchmark / Evidence Audit E](vol_04_benchmark_evidence_claim_to_protocol.html)。
4. [EVAL-003 statistical source freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。
5. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [WAM evidence inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
