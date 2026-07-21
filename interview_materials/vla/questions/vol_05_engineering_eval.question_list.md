# VOL 05 Engineering / Evaluation Phase 0 题目清单

> 规划日期：2026-07-17  
> 状态：`44 planned / knowledge 44 drafted / cards 44 drafted/unseen / ENG-001..022 + EVAL-001..022 drafted/unseen / EVAL-003..022 source-frozen / WARN`
> 知识正文：[VOL 05 Batch 1](../knowledge/vol_05_engineering_eval.html)  
> Batch 1 题卡：[10 张折叠题卡](vol_05_engineering_eval.html)  
> Batch 2A 知识页：[ENG-009..011](../knowledge/vol_05_engineering_eval_batch2a.html)；题卡：[3 张折叠题卡](vol_05_engineering_eval_batch2a.html)  
> Batch 2A 官方文档复核：[DVC / PyTorch / Hugging Face](../sources/vol_05_batch2a_independent_fact_review.html)  
> ENG-012 Source Gate：[HDF5 / Zarr / WebDataset / Parquet](../sources/vol_05_eng012_storage_formats_source_freeze.html)  
> ENG-012 知识页：[单节点知识正文](../knowledge/vol_05_engineering_eval_eng012.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng012.html)  
> ENG-013 Source Freeze：[seed / determinism / sampler cursor](../sources/vol_05_eng013_reproducibility_source_freeze.html)；知识页：[单节点正文](../knowledge/vol_05_engineering_eval_eng013.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng013.html)  
> ENG-014 Source Freeze：[CUDA / MACA / ROCm / operator compatibility](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html)；知识页：[单节点知识正文](../knowledge/vol_05_engineering_eval_eng014.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng014.html)。  
> ENG-015 Source Freeze：[activation checkpointing / CPU-NVMe offload / throughput](../sources/vol_05_eng015_activation_offload_source_freeze.html)；知识页：[单节点正文](../knowledge/vol_05_engineering_eval_eng015.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng015.html)。  
> ENG-016 Source Freeze：[student + multiple teachers / distillation / memory scheduling](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)；知识页：[单节点正文](../knowledge/vol_05_engineering_eval_eng016.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng016.html)。  
> ENG-017 Source Freeze：[loss / grad / data_wait / comm / AMP overflow observability](../sources/vol_05_eng017_training_observability_source_freeze.html)；知识页：[单节点正文](../knowledge/vol_05_engineering_eval_eng017.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng017.html)。  
> ENG-018 Source Freeze：[scheduler / preemption / retry / idempotent jobs](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)；知识页与一张题卡已生成，题卡保持 unseen。  
> ENG-019 Source Freeze：[config / CLI / env resolution / run identity](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)；知识页：[单节点正文](../knowledge/vol_05_engineering_eval_eng019.html)；题卡：[单张折叠题卡](vol_05_engineering_eval_eng019.html)。  
> ENG-020 Source Freeze：[secret / token / data permission / logging redaction](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)；知识页与一张 `unseen` 题卡已生成，未产生口述成绩。  
> 规则：先按来源批次完成知识页，再生成对应折叠题卡；题卡生成后默认 `unseen`，没有真实口述不得升级。

## 1. Engineering / Deployment（22）

| ID | 难度 | 优先级 | 主题 | 当前状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-001` | L2 | P0 | VLA 数据 schema：observation/action/time/normalizer/provenance | card drafted / unseen |
| `VLA-ENG-002` | L2 | P0 | grouped split、dedupe 与 leakage audit | card drafted / unseen |
| `VLA-ENG-003` | L2 | P0 | DataLoader/preprocess/GPU/sync 吞吐分解 | card drafted / unseen |
| `VLA-ENG-004` | L2 | P0 | DDP、FSDP、ZeRO 的分片与选择 | card drafted / unseen |
| `VLA-ENG-005` | L2 | P0 | AMP、gradient accumulation、clipping、effective batch | card drafted / unseen |
| `VLA-ENG-006` | L3 | P0 | checkpoint lineage、resume 与 load smoke | card drafted / unseen |
| `VLA-ENG-007` | L2 | P0 | policy server latency、chunk 与 replan | card drafted / unseen |
| `VLA-ENG-008` | L3 | P0 | action parser/denorm/frame/controller deployment contract | card drafted / unseen |
| `VLA-ENG-009` | L2 | P0 | dataset/version/transform manifest 与可追溯性 | card drafted / unseen |
| `VLA-ENG-010` | L2 | P1 | multimodal decode、augmentation、cache 与确定性 | card drafted / unseen |
| `VLA-ENG-011` | L3 | P1 | variable-length sample、dynamic batching 与 padding waste | card drafted / unseen |
| `VLA-ENG-012` | L2 | P1 | HDF5/Zarr/WebDataset/Parquet 的访问模式与取舍 | card drafted / unseen |
| `VLA-ENG-013` | L2 | P0 | seed、determinism、sampler cursor 与复现实验 | card drafted / unseen |
| `VLA-ENG-014` | L3 | P1 | CUDA/MACA/ROCm 等硬件迁移与算子兼容 | card drafted / unseen |
| `VLA-ENG-015` | L2 | P1 | activation checkpointing、CPU/NVMe offload 与吞吐 | knowledge+card drafted / unseen |
| `VLA-ENG-016` | L3 | P1 | student + multiple teachers 的显存/调度设计 | knowledge+card drafted / unseen |
| `VLA-ENG-017` | L2 | P0 | train observability：loss/grad/data_wait/comm/overflow | knowledge+card drafted / unseen |
| `VLA-ENG-018` | L2 | P1 | scheduler、preemption、retry 与幂等 checkpoint | knowledge+card drafted / unseen |
| `VLA-ENG-019` | L2 | P1 | config/CLI/env 合并与 run identity | knowledge+card drafted / unseen |
| `VLA-ENG-020` | L2 | P1 | secret、token、数据权限与日志脱敏 | knowledge+card drafted / unseen |
| `VLA-ENG-021` | L2 | P0 | model/processor/normalizer 打包与版本兼容 | knowledge+card drafted / unseen |
| `VLA-ENG-022` | L3 | P0 | policy server batching、backpressure、timeout、fallback | knowledge+card drafted / unseen |

## 2. Evaluation / Debugging（22）

| ID | 难度 | 优先级 | 主题 | 当前状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-001` | L2 | P0 | closed-loop protocol tuple 与 run/episode manifest | card drafted / unseen |
| `VLA-EVAL-002` | L2 | P0 | metric ladder 与 first-failure debugging | card drafted / unseen |
| `VLA-EVAL-003` | L2 | P0 | success rate、置信区间与最小 rollout 数 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-004` | L3 | P0 | paired init/seed evaluation 与显著性 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-005` | L2 | P0 | macro/micro/per-task/weighted aggregation | source+knowledge+card drafted / unseen |
| `VLA-EVAL-006` | L2 | P0 | benchmark/env/controller/scorer versioning | source+knowledge+card drafted / unseen |
| `VLA-EVAL-007` | L3 | P1 | init/seed/task coverage 与难度分层 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-008` | L2 | P0 | perception/action/controller/recovery failure taxonomy | source+knowledge+card drafted / unseen |
| `VLA-EVAL-009` | L2 | P0 | raw predictions、episode trace、video 与可复算 summary | source+knowledge+card drafted / unseen |
| `VLA-EVAL-010` | L2 | P0 | regression gate、golden set 与 canary rollout | source+knowledge+card drafted / unseen |
| `VLA-EVAL-011` | L3 | P1 | offline metric 与 online success 的相关性分析 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-012` | L2 | P1 | OOD、扰动、遮挡、视角与鲁棒性矩阵 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-013` | L2 | P1 | p50/p95/p99 latency、deadline miss 与 jitter | source+knowledge+card drafted / unseen |
| `VLA-EVAL-014` | L3 | P0 | forbidden side effect、scope 与取消补偿评估 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-015` | L3 | P0 | reward/scorer hacking 与 adversarial evaluation | source+knowledge+card drafted / unseen |
| `VLA-EVAL-016` | L2 | P1 | VLM/human proxy 评分的一致性与偏差 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-017` | L3 | P1 | simulator success、shadow mode 与真机 gate | source+knowledge+card drafted / unseen |
| `VLA-EVAL-018` | L3 | P0 | factorial ablation、matched baseline 与因果边界 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-019` | L2 | P0 | checkpoint selection、Pareto frontier 与 holdout overfit | source+knowledge+card drafted / unseen |
| `VLA-EVAL-020` | L2 | P1 | incident timeline、root cause 与 bug-fix verification | source+knowledge+card drafted / unseen |
| `VLA-EVAL-021` | L3 | P1 | deployment drift、data shift 与持续监控 | source+knowledge+card drafted / unseen |
| `VLA-EVAL-022` | L3 | P0 | paper→repo→checkpoint→runtime→ownership evidence audit | source+knowledge+card drafted / unseen |

## 3. 批次计划

| 批次 | 节点 | 目标 |
| --- | --- | --- |
| Batch 1 | ENG-001..008 + EVAL-001..002 | 数据→训练→checkpoint→serving→protocol→first failure 基础闭环 |
| Batch 2 | ENG-009..016 | data/version/storage/determinism/hardware/memory 深化 |
| Batch 3 | ENG-017..022 | observability、调度、配置、安全、打包与 serving resilience |
| Batch 4 | EVAL-003..011 | 统计、paired eval、aggregation、versioning、trace 与 offline-online correlation |
| Batch 5 | EVAL-012..022 | robustness、safety、proxy、sim-to-real、ablation、selection、incident/drift/evidence audit |

### Batch 2A 已完成的知识切片

- `VLA-ENG-009..011` 已完成 canonical knowledge Markdown/HTML/review（3 个节点）。
- Batch 2A 的 3 张题卡已在独立 bounded slice 生成，默认状态为 `unseen`；没有真实口述不得升级。
- 证据状态保持 `WARN`：DVC/DataLoader/padding/HF cache-collator 官方语义已独立复核，但 manifest/cache/dynamic-batching 的项目 A/B 证据仍未闭合。

### ENG-012 Source Gate

- HDF5/h5py 3.15.0、Zarr v3.2.1、WebDataset frozen commit、Apache Parquet format commit 与 PyArrow 22.0 来源已冻结。
- source freeze、单节点知识正文与一张原子题卡均已完成；题卡保持 `unseen`。
- ENG-012..020 的 source freeze、知识与题卡现已逐节点完成；所有题卡仍可逐题口述，但没有真实回答前保持 `unseen`。
- ENG-021 的 source freeze、知识与一张题卡已完成；严格 bundle/hash/load/round-trip/backend gate 仍保持 WARN。
- ENG-022 Source Freeze、knowledge slice 与一张题卡已完成；官方 queue/timeout/dynamic batching 与 OpenPI server 边界已冻结，题卡保持 unseen。
- ENG-022 的 knowledge slice 与一张题卡已完成；bounded queue、batch/freshness、deadline/cancel、fallback 和项目边界保持 WARN。

### EVAL-003 Source Gate + Knowledge + Card（已完成，WARN）

- 已冻结 SciPy `v1.16.3` `binomtest().proportion_ci()`、statsmodels `v0.14.6` `proportion_confint()` / normal sample-size approximation，以及 Wilson、Clopper–Pearson、cluster design effect、sequential inference 的论文边界。
- 已明确 episode-level Bernoulli contract、Wilson/exact 区间、zero/all-success、`n >= z²p(1-p)/epsilon²` 的规划语义；UWM 186/250 只作 naive diagnostic，OpenPiVLA 97.4 缺分母，OPD 10k 是 metric-specific holdout，不能混成 rollout success。
- 已生成 `knowledge/vol_05_engineering_eval_eval003.md/.html/.review.json` 与 `questions/vol_05_engineering_eval_eval003.md/.html/.question_list.md/.review.json`，覆盖 Bernoulli episode contract、Wilson/exact、zero/all-success、margin planning、cluster dependence 与 optional stopping；VOL 05 knowledge 25/44、cards 25/44，题卡保持 unseen。

### EVAL-004 Source Gate + Knowledge + Card（已完成，WARN）

- 已冻结 paired unit、`n11/n10/n01/n00`、`Delta=(n10-n01)/n`、exact McNemar、SciPy `permutation_type="samples"` / `bootstrap(..., paired=True)`、四类 seed、training-run 层级、invalid-pair、selection/holdout、Holm 与 practical threshold 边界。
- 已明确 UWM 186/250 与 232/250 协议不同且缺 matched raw pairs，OpenPiVLA 97.4% 缺 denominator/lineage，OPD 10k 是静态 cluster；三者均不产生本地 paired significance claim。
- 已生成 `sources/vol_05_eval004_paired_init_seed_significance_source_freeze.*`、`knowledge/vol_05_engineering_eval_eval004_paired_init_seed_significance.*` 与 `questions/vol_05_engineering_eval_eval004.*`；VOL 05 knowledge 26/44、cards 26/44，题卡保持 unseen，下一内容节点为 EVAL-005。

### EVAL-005 Source Gate + Knowledge + Card（已完成，WARN）

- 已冻结 aggregation estimand、per-task `k/n`、macro/micro/weighted 公式、equal-suite/task/episode hierarchy、common-support weights、missingness/coverage 与 rliable fixed-task/task-population uncertainty。
- UWM final 五 task 等分母使 macro=micro=0.744 只作 arithmetic audit；OpenPiVLA 97.4 只到 equal-suite archive table；OPD box/point/text 异构 metric 不合成总分。
- 已生成 `sources/vol_05_eval005_aggregation_estimand_source_freeze.*`、`knowledge/vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.*` 与 `questions/vol_05_engineering_eval_eval005.*`；VOL 05 knowledge 27/44、cards 27/44，题卡保持 unseen，下一内容节点为 EVAL-006。

### EVAL-006 Source Gate + Knowledge + Card（已完成，WARN）

- 已冻结 label/SemVer/tag、immutable revision、file/OCI digest、Gymnasium resolved EnvSpec、RFC 8785 canonical manifest、protocol SHA与semantic diff gate。
- 已明确benchmark/env/controller/scorer/policy/runtime六部分identity，并映射UWM、WAM、OpenPiVLA、OPD与Robot Harness的具体version/scorer/lineage断点；不产生新的可比成绩。
- 已生成 `sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.*`、`knowledge/vol_05_engineering_eval_eval006_versioned_evaluation_manifest.*` 与 `questions/vol_05_engineering_eval_eval006.*`；VOL 05 knowledge 28/44、cards 28/44，题卡保持unseen，下一内容节点为EVAL-007。

### EVAL-007 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结Neyman、Procgen、rliable、LIBERO task registry与EVAL-004..006；count、unique support、coverage、representativeness和success严格分开。
- coverage cube固定为task×difficulty×init×training-seed；training/env/rollout/bootstrap seed分层，difficulty不得由candidate final failure事后定义。
- 五项目均缺完整raw task/init/training-seed cell ledger与target weights，不升级coverage或robustness claim。
- 已生成 `sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.*`、`knowledge/vol_05_engineering_eval_eval007_coverage_difficulty_stratification.*` 与 `questions/vol_05_engineering_eval_eval007.*`；VOL 05 knowledge 29/44、cards 29/44，题卡保持unseen，下一内容节点为EVAL-008。

### EVAL-008 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结FMECA、Sentinel、AHA、REFLECT、Recovery RL与ros2_control；effect/mode/cause/detection/recovery outcome严格分开。
- primary layer取first verified divergence；root cause需matched intervention、fix与同协议rerun，缺证据标unknown。
- 五项目均缺完整layer-aligned trace + intervention + rerun，不升级root-cause或recovery claim。
- 已生成 `sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.*`、`knowledge/vol_05_engineering_eval_eval008_failure_taxonomy_recovery.*` 与 `questions/vol_05_engineering_eval_eval008.*`；VOL 05 knowledge 30/44、cards 30/44，题卡保持unseen，下一内容节点为EVAL-009。

### EVAL-009 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结BagIt、PROV-DM与MCAP；summary、raw rows、trace/video、immutable bundle和independent recompute分层。
- planned/valid/excluded/missing守恒，video只作timestamp-aligned sidecar，summary必须由冻结reducer从raw重算。
- 五项目均缺完整immutable raw-to-summary bundle，不升级metric claim。
- 已生成EVAL-009 source/knowledge/question artifacts；VOL 05 knowledge/cards 31/44，下一节点为EVAL-010。

### EVAL-010 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结Breck et al. ML Test Score与Argo Rollouts；SRE官方章节在当前环境抓取受阻，未承担唯一强主张。
- golden case/expected/slice/margin在candidate前冻结；同protocol/scorer/common support做paired non-inferiority，critical/safety/latency不被overall抵消。
- shadow保持无actuator authority；canary固定exposure/window/guardrail，失败abort并回滚known-good完整bundle。
- 五项目均没有闭合common-support raw bundle、预注册decision与live canary，不升级release-system claim。
- 已生成EVAL-010 source/knowledge/question artifacts；VOL 05 knowledge/cards 32/44，下一节点为EVAL-011。

### EVAL-011 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结SIMPLER v1/official metrics、ML Test Score与SciPy Pearson/Spearman/Kendall/bootstrap实现入口。
- policy/checkpoint是相关性变异单位；episode只估计每个online success点，不能pseudo-replicate。
- Pearson、rank/MMRV、held-out prediction与causal effect分开；task hierarchy、cluster uncertainty与selection bias显式处理。
- 五项目均缺matched policy-task offline×online panel，不生成或升级任何项目相关系数。
- 已生成EVAL-011 source/knowledge/question artifacts；VOL 05 knowledge/cards 33/44，下一节点为EVAL-012。

### EVAL-012 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结 ImageNet-C `1903.12261v1` / official commit `8190fe3` 与 SIMPLER `2405.05941v1` / official commit `06accaca`；分类 corruption benchmark 与机器人 closed-loop robustness 边界分开。
- target envelope、diagnostic OOD、stress-only 分层；clean–perturbed pair 固定 checkpoint/task/init/controller/predicate，severity 绑定 unit/range source/cadence/correlation。
- visibility、label、reachability、physics、predicate 与 solvability gate 显式；每格报告 k/n/CI、drop、retention、curve 与 preregistered worst target cell。
- 五项目均缺 checkpoint-bound paired closed-loop robustness matrix，不新增任何项目性能结论。
- 已生成 EVAL-012 source/knowledge/question artifacts；VOL 05 knowledge/cards 34/44，下一节点为 EVAL-013。

### EVAL-013 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结 Tail at Scale、ROS 2 pendulum/QoS、HdrHistogram、RFC 3393、CPython clock 与 OpenPI serving 的revision/hash；tail、scheduler lateness、network PDV和action age严格分开。
- capture→apply事件边界、clock uncertainty、GPU synchronization、critical path、p50/p95/p99/max、deadline miss、phase/interval jitter与per-offset chunk age已闭合。
- cold/warm/load/fault、intended arrival与coordinated omission、matched H/K/Hz/backend/queue实验和raw trace artifact进入评估合同。
- 五项目均缺protocol-complete capture→controller-apply trace；UWM DataLoader p95只保留为训练input-stall证据。
- 已生成EVAL-013 source/knowledge/question artifacts；VOL 05 knowledge/cards 35/44，下一节点为EVAL-014。

### EVAL-014 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结ROS 2 Actions cancel状态机、RFC 6749 scope、OWASP逐请求授权、Microsoft compensating transaction与CPython cancellation的revision/hash；公开机制不冒充本地结果。
- intent→authorization→dispatch→authoritative sink分层；scope绑定subject/resource/action/parameters/time/purpose/approval/state并在dispatch前对resolved action重验。
- cancel request/accepted/no-new-dispatch/quiescence/compensation/manual reconcile分开；补偿作为可失败、可恢复、幂等、可审计的领域化forward action。
- resource/parameter/expiry/indirection/retry/duplicate/cancel timing/irreversibility/toxic composition进入测试矩阵；critical forbidden commit hard veto与allowed-case utility floor分离。
- Robot Harness仅有scope/cancel/cleanup入口与proxy safety evidence，`RH-CL-009`仍FAIL；五项目均无protocol-complete真实effect-sink结论。
- 已生成EVAL-014 source/knowledge/question artifacts；VOL 05 knowledge/cards 36/44，下一节点为EVAL-015。

### EVAL-015 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结Concrete Problems、AI Safety Gridworlds、Reward Tampering与Reward Model Overoptimization的版本/hash；observed reward、hidden performance、tampering和proxy过度优化严格分层。
- training/selection proxy、locked audit与deployment utility分离；audit独立性按data、signal、implementation、reviewer和access逐项声明。
- high-proxy/low-audit gap、optimizer-budget曲线、positive/negative/invariance/directional controls与parser/judge/tamper/trajectory/selection adversarial matrix进入评估合同。
- critical hard veto与allowed utility floor并行；发现failure进入regression后仍保留fresh hidden family。
- Robot Harness有reward/scorer源码和128-row窄边界测试，但真实effect、cancel语义、semantic backend与locked audit仍缺；其他四项目也无budget curve。
- 已生成EVAL-015 source/knowledge/question artifacts；VOL 05 knowledge/cards 37/44，下一节点为EVAL-016。

### EVAL-016 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结WorldGym、MT-Bench judge、Prometheus-Vision、MJ-Bench与scikit-learn/SciPy agreement/rank实现的版本/hash；机器人proxy、judge bias与统计入口分层。
- binary/ordinal/pairwise/ranking/probability/failure taxonomy分别选择confusion、kappa、rank、calibration与per-class指标，correlation不冒充absolute agreement。
- human blind double-label、raw disagreement、adjudication与evidence visibility进入protocol；同模型五票不当独立专家。
- position/style/identity/rubric/visual/temporal/viewpoint/task/injection/language paired probes与abstention进入bias contract。
- WorldGym代码literal `gpt-4o`、n=5、0/0.5/1与乐观平票边界已核对；五项目均无VLM×human×objective predicate成对bundle。
- 已生成EVAL-016 source/knowledge/question artifacts；VOL 05 knowledge/cards 38/44，下一节点为EVAL-017。

### EVAL-017 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结 SIMPLER、ML Test Score、Argo Rollouts mirror route、Sim2Real Audit 与 WM-031 的版本/hash；simulator、HIL/dry-run、live shadow、guarded real canary 与 progressive deployment 分层。
- simulator success 仅属于冻结 sim protocol；sim–real 相关或排序必须有多个 policy/checkpoint 与 matched support，不能由单一候选模型外推。
- shadow 接入 live observation，但 candidate 在 server/controller/hardware 三层均无 actuator dispatch 权限；shadow trajectory 由 known-good/human 产生，不能报告 candidate closed-loop success。
- canary 在执行前冻结 robot/task/workspace/speed/force/time 风险预算、minimum exposure、decision window 与 hard abort；`0/n` 只给单侧风险上界，不等于零风险。
- promotion 是 hard gate 合取；回滚 known-good 只影响未来动作，已发生物理 effect 仍需 stop、quiescence、compensation 或 manual reconcile。
- 五项目均无 same-bundle sim→shadow→real canary 连续证据；已生成 EVAL-017 source/knowledge/question artifacts，VOL 05 knowledge/cards 39/44，题卡保持 unseen，下一节点为 EVAL-018。

### EVAL-018 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结NIST full-factorial/randomized-block页面、Bouthillier等ML benchmark variance论文、Hernán–Robins因果识别框架与statsmodels实现入口的版本/hash；通用DOE与VLA映射边界分开。
- factor、arm、experimental unit、outcome与estimand分层；两因素至少跑A00/A10/A01/A11，分别估计main/simple effect与`μ11-μ10-μ01+μ00` interaction。
- matched baseline冻结initial bundle、data、optimization/budget、tuning、selection、eval/scorer和failure policy；fixed-recipe机制effect与equal-search-budget系统effect分开。
- training/data随机性与eval pair做block/randomization；episode不替代training seeds；planned→started→valid/failed/excluded守恒，OOM/NaN/timeout不得静默删除。
- 因果表述要求factor consistency、exchangeability、positivity、no interference与outcome accounting闭合，且只到冻结model/data/budget/task/scorer support。
- 五项目均无完整matched factorial；已生成EVAL-018 source/knowledge/question artifacts，VOL 05 knowledge/cards 40/44，题卡保持unseen，下一节点为EVAL-019。

### EVAL-019 Source Gate + Knowledge + Card（已完成，WARN）

- 冻结Cawley–Talbot model-selection bias、Dwork等adaptive holdout、Deb/NSGA-II+pymoo Pareto/NDS与scikit-learn nested evaluation的版本/hash；公共机制与VLA决策规则分层。
- candidate、feasible、Pareto与selected bundle四个集合分开；metric角色冻结为train/development/hard-gate/audit-only/monitoring。
- validation best是在含噪估计上取max；checkpoint cadence、early stopping、best seed、失败视频和leaderboard访问均进入selection/exposure history。
- artifact/safety/deadline等hard gates先形成feasible set；Pareto只保留不支配trade-off，最终仍按预注册constraint/lexicographic/weight/tie-break选一个真实bundle。
- paired/cluster uncertainty与practical margin进入robust dominance；dev选完锁定bundle，fresh audit若驱动回改则开启新cycle并更换audit family。
- OPD/Harness只有局部trade-off输入，其他项目candidate/lineage更不完整；已生成EVAL-019 source/knowledge/question artifacts，VOL 05 knowledge/cards 41/44，题卡保持unseen，下一节点为EVAL-020。

### ENG-013 Source Gate

- PyTorch 2.13 Reproducibility、DataLoader/DistributedSampler、CPU/CUDA RNG state API 与 NumPy 1.26 seed 已冻结。
- ENG-013 知识正文和单张题卡均已完成；本地 fixed-batch/mid-epoch replay 仍未生成/验证。
- ENG-014 的 source freeze、单节点知识与题卡已完成；真实跨后端 benchmark 仍后置。

### ENG-014 Source Gate

- PyTorch 2.13 CUDA/HIP/C++ extension、ROCm 7.14.0 compatibility matrix、NVIDIA CUDA Compatibility、`mcPytorch@b3db5e` 与 `mcTriton@7dd407` 已冻结。
- 当前只支持 L0 device/runtime → L5 workload/eval 的分层合同、operator matrix 和项目真实性边界；不支持“CUDA API 能调用 = 算子/性能等价”。
- 独立措辞复核已完成；ENG-014..020 题卡均保持 unseen，真实兼容 benchmark 仍未补齐。

### ENG-015 Source Gate

- 已冻结 PyTorch 2.13 activation checkpoint/FSDP CPU offload，以及 DeepSpeed frozen commit `de1846cf6fbdd6f1c2adf046f319791ca78cc547` 的 activation-checkpointing/ZeRO-3 文档。
- Source freeze 明确区分 activation recompute、FSDP CPU offload、ZeRO-Offload 与 ZeRO-Infinity；显存账本、step-time 分解、matched effective batch、A/B profiler 和 fixed-next-batch resume 均保留为工程验收合同。
- 当前没有本地 checkpoint binary、optimizer/RNG/sampler lineage、matched throughput A/B 或 fixed-batch resume artifact；ENG-015 题卡保持 `unseen`。

### ENG-016 Source Gate

- 已冻结 Hinton distillation、PyTorch 2.13 `kl_div`/`no_grad`/FSDP 与 DeepSpeed ZeRO-3；明确 `input=log-probability`、`target` shape、`batchmean`、temperature/mask 和 teacher no-grad 边界。
- 多教师调度只作为 resident/sequential/staged engineering design；OPD 的五教师 `preloaded_zero3`、route metadata、coldstart full-vocab KL 和 student-rollout KL 是 local hook，不是多教师收益或 learned-router 证明。
- 当前缺 single-teacher/SFT-only/no-synthetic/synthetic-ratio ablation、teacher/student binary bundle 和 matched memory/latency A/B；ENG-016 题卡保持 `unseen`。

### ENG-017 Source Gate

- 已冻结 PyTorch 2.13 AMP、Profiler、Autograd anomaly、DDP、`clip_grad_norm_`、DataLoader，以及 DeepSpeed `steps_per_print`/`wall_clock_breakdown` 配置语义。
- Source freeze 定义 numerical、data、compute、distributed、lifecycle 五层事件合同；UWM/OPD 现有 summary/hook 不能升级为完整 per-step/per-rank telemetry 或吞吐因果。
- 当前缺 overflow/scale/grad-norm 时间序列、rank-level data_wait/comm trace、matched A/B 和 first-failure replay；ENG-017 题卡保持 `unseen`。

### ENG-018 Source Gate

- 已冻结 PyTorch 2.13 TorchElastic/torchrun/DCP、Kubernetes Job/Pod Lifecycle 与 DeepSpeed model checkpointing；明确 rank/world-size 可变、duplicate execution、SIGTERM/grace 和 multi-file checkpoint 边界。
- Source freeze 定义 logical run/attempt/worker group/rank 四层 identity、attempt-scoped temp generation、manifest-last COMMITTED、stable operation key 去重和 immutable final promotion。
- UWM/OPD/OpenPiVLA 当前只有 save/load metadata、final-only/no-optimizer-state manifest 或远端 path；没有 binary、attempt ledger、signal/retry/duplicate/world-size drill；ENG-018 知识与一张题卡已生成并保持 unseen。

### ENG-019 Source Gate

- 已冻结 Hydra 1.3.2 Defaults/override、pydantic-settings 2.14.1 priority、CPython 3.14 argparse、PyTorch 2.13 torchrun runtime env 与 RFC 8785 canonical JSON。
- Source freeze 定义 resolve→typed validate→field provenance→secret redaction→canonical semantic hash，并区分 semantic run key、logical run、attempt 与 rank/restart identity。
- UWM 有 env defaults/Hydra CLI/effective DeepSpeed subset，OpenPiVLA 有 argparse/formal plan/args snapshot，OPD 有 argparse/DeepSpeed `auto` runtime mutation/partial summary；三者都缺统一 source map、secret-safe canonical hash 和 checkpoint/eval lineage；ENG-019 知识与一张题卡已生成并保持 unseen。

### ENG-020 Source Gate

- 已冻结 OWASP Secrets/Logging/Authorization、Kubernetes Secret/Good Practices、NIST SP 800-53 Rev.5 AC-3/AC-6/AU-9/IA-5 与 pydantic-settings debug secret warning。
- Source freeze 定义 secret lease/rotate/revoke、deny-by-default/least privilege/every-request authorization、data purpose/retention/export manifest、allowlist-first redaction 与 canary/negative/incident drill。
- Robot Harness 有特定 `__access_token` mask/dedup exclusion 和 robot/tool scope filtering；UWM/OpenPiVLA/OPD 只有 args/path/summary 暴露面，统一 secret manager/IAM/data purpose/generic redaction/audit protection 仍缺；ENG-020 知识与一张题卡已生成并保持 unseen。

### ENG-021 Source Gate

- 已冻结 Transformers `save_pretrained/from_pretrained`、`ProcessorMixin`、Hub commit-revision snapshot、safetensors header/安全边界，以及 OpenPI params/assets/train_state/norm-stats/transforms/shape 语义。
- Source gate 要求 model config/weight shards、processor、action schema、normalizer、ordered transforms、lineage、runtime manifest、strict load、fixed-batch 与 action/controller round-trip 绑定为 immutable bundle。
- OpenPiVLA 当前有 processor/collator、recipe、远端 checkpoint/path；UWM 有 normalizer/load metadata；OPD 有 final-only/no-optimizer-state manifest；formal checkpoint binary、processor/norm hash binding、round-trip 与 backend A/B 仍缺。知识页与题卡后置，ENG-022 不展开。

## 4. Batch 1 退出条件

1. 10 个知识节点有公式/实现/shape 或协议字段、trade-off、bad case 和项目 hook。
2. 对应 10 张题卡已在独立切片生成，ID 全局唯一，全部保持 `unseen`。
3. 不把项目 inventory 的数字升级为通用事实；每个 project hook 保留证据等级。
4. DDP/FSDP/ZeRO/AMP/checkpoint 需要后续独立官方文档复核，当前 review 保持 `WARN`。
