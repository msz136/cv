# VOL 05 EVAL-007：Init / Seed / Task Coverage 与难度分层

> 状态：`drafted / VLA-EVAL-007 / knowledge_29_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-004 Paired](vol_05_engineering_eval_eval004_paired_init_seed_significance.html)、[EVAL-005 Aggregation](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)、[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)  
> 来源冻结：[EVAL-007 Source Freeze](../sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)  
> 项目边界：五项目均未闭合完整task×init×difficulty×training-seed raw cube，本页不升级coverage或robustness claim。

## 问题（Question）

如何设计VLA的init/seed/task coverage和难度分层？核心是先定义目标总体与风险strata，再设计blocked/stratified sampling、unique support、minimum per-cell、oversampling reweighting和difficulty leakage防线。

## 1. 直觉：250次不等于250种情况

如果250次都来自相似初态、单一training seed和五个方便task，count很大但support很窄。coverage回答“目标空间哪些区域被测到足够多”，representativeness回答“这些区域的权重是否像部署”。二者都不能由总n推断。

```text
count -> unique support -> cell coverage -> target representativeness
```

## 2. Coverage Cube

\[
h=(task, difficulty, init\_stratum, training\_seed).
\]

变量解释：每个cell固定task/family、候选模型无关的difficulty/risk标签、init/scene/object stratum和training run。cell内可有rollout repeats，但repeat不增加training-seed或unique-init coverage。

建议ledger：

```text
cell_id, task/revision, difficulty_schema/bin,
init_snapshot_hash/family, training/env/rollout_seed,
protocol_sha, planned/attempted/valid/unique_init_n,
success_k, exclusions, target_weight
```

A/B比较使用同一cube、同一weights与同一missing rule。

## 3. Coverage Score 只测覆盖，不测成功

设cell权重 `W_h`、最低有效样本 `m_h`、实际 `n_h`：

\[
C_w=\sum_h W_h\mathbf 1[n_h\ge m_h].
\]

变量解释：`C_w`是target-weight coverage。它不包含success outcome，不能说coverage高就模型好。还要报告unweighted covered cells、`n_h/m_h`、unique-init ratio、weight coverage和per-cell `k/n/CI`。

critical cell可设hard minimum或gate，不能让easy cells的大n平均掉未覆盖的safety/contact区域。

## 4. 四类Seed Coverage

| seed | 统计层级 | coverage要求 |
| --- | --- | --- |
| training seed | model run | 每个run尽量覆盖共同task/init grid |
| env/init seed | state generator | 用snapshot/hash确认actual init |
| rollout stochastic seed | fixed model+init noise | 作为repeat，不冒充unique init |
| bootstrap seed | analysis | 只保证重采样可复算 |

若seed1只跑easy tasks、seed2只跑hard tasks，training variance与task difficulty confounded。episode再多也无法拆开。

## 5. Task Coverage 三层

1. **registry**：planned/attempted/valid task IDs；
2. **capability family**：grasp、place、contact、navigation、tool safety、recovery；
3. **deployment/risk**：真实流量权重和high-severity cases。

task taxonomy会影响cell数和macro权重；保存ordered registry hash、family schema、inclusion/exclusion和版本。新增task后，旧新模型先在common registry重算，再报告新coverage。

## 6. Init Coverage

必须保存actual state evidence：snapshot/hash、reset state/proprio、first frame checksum，以及pose/rotation、scene/layout/style、distractor/background、camera/occlusion、contact/gripper/robot pose、ID/OOD生成规则。

错误说法：

- seed整数不同，所以init一定不同；
- range覆盖min/max，所以内部和corners都覆盖；
- 50次reset，所以有50个independent states；
- 同一图片多标注就是50个视觉场景。

可按metadata或state/image distance聚类近重复init，报告unique cluster support。

## 7. Difficulty Schema

### 7.1 候选模型无关特征

| 维度 | 特征例子 |
| --- | --- |
| horizon | stages、expert/demo length、subgoals |
| geometry | pose shift、rotation、tolerance、clearance |
| contact | contact transitions、friction、grasp mode |
| perception | occlusion、distractors、view shift、object size |
| language | length、relations、ambiguity、composition |
| recovery | perturbation、off-nominal start、replan需求 |
| safety | severity、forbidden effect、intervention |

### 7.2 Baseline/Pilot difficulty

可用frozen baseline或disjoint pilot success估计difficulty，但baseline revision、sample、bin edges和merge rule必须在candidate final前冻结。candidate失败后才把case定义为hard，只能做exploratory slice。

难度可保留多维vector，不必强压成easy/medium/hard。每bin设minimum、unknown bucket和predefined merge rule。

## 8. Sampling Allocation

### 8.1 Proportional

`n_h≈nW_h`适合目标mixture估计，但rare/risk strata可能不足。

### 8.2 Equal / Minimum

每格等量或minimum适合诊断。因为sample mix改变，总体结果要按target `W_h`重加权，不能报oversampled micro。

### 8.3 Neyman

\[
n_h\propto\frac{W_h\sigma_h}{\sqrt{c_h}},
\qquad \sigma_h\approx\sqrt{p_h(1-p_h)}.
\]

变量解释：`sigma_h`是stratum variance、`c_h`是成本。用独立pilot估计；不能用final candidate outcomes调整allocation后仍称预注册。

### 8.4 Hybrid

先满足critical/rare minimum，再按target weight、variance或cost分配剩余budget；同时报告raw allocation、target weights与reweighted estimate。

## 9. Train / Pilot / Validation / Final

- exact train init/level不进入final；
- pilot估计variance/difficulty，不参与final significance；
- validation冻结checkpoint、bins和weights；
- final锁定registry/protocol/exclusion；
- procedural generator保存version/config/train-test seed lists和overlap audit。

Procgen说明train/test levels分离与generalization gap的重要性，但“新seed”不自动等于语义新task或真实机器人泛化。

## 10. Uncertainty 与 Slice Audit

training run顶层resample，保持task/init strata；同init重复episode不展开为iid。每格给k/n/CI，primary aggregate按EVAL-005 weights重算。

难度切片多时预注册primary slices，其余标exploratory并公开完整family。空格和小格显示insufficient coverage，不静默合并、不只展示最亮眼/最差格。

## 11. 五项目映射

### UWM

5 tasks×50 summary只证明planned count；缺250raw rows、unique init、training-seed grid和difficulty schema。Table II的50 OOD init×3 seeds是另一protocol。moka/mug低分只可触发exploratory failure audit。

### WAM

local diagnostic只有CoffeePressButton episode0和一组seed/env_seed的base/trained traces，不能代表task/init coverage。24×5与86/120/84/118无raw bundle，coverage不可算。

### OpenPiVLA

四suite summary缺per-task trials/seeds/inits；不能恢复coverage matrix。formal Qwen runs与archive eval lineage未闭合。

### OPD

10k有box/point/text quotas、8,251 unique images与重复image paths，是强coverage metadata，但quota不等于deployment mixture。按image cluster、pool/domain、format、seen/unseen/hard与metric分层。

### Robot Harness

project/safety/browser/cross n不同，browser为format-only，execution coverage为0。training task-family counts不是eval coverage；需tool family×scope×severity×trajectory length×runner availability矩阵。

## 12. Coverage Planner

```python
def coverage_report(registry, weights, minimums, rows):
    # Build cells from schemas frozen before candidate evaluation.
    cells = build_cells(registry)
    ledger = summarize(rows, unique_key="init_snapshot_hash")

    # Coverage ignores success; it checks minimum valid support.
    c_weighted = sum(weights[h] * int(ledger[h].valid_n >= minimums[h])
                     for h in cells)

    # Outcome estimates remain separate and use target weights/clusters.
    estimate = stratified_estimate(
        rows, weights=weights,
        clusters=["training_seed", "init_family"]
    )
    return {"cells": ledger, "coverage": c_weighted,
            "estimate": estimate}
```

这是设计合同，不是项目已实现系统。coverage score不替代per-cell table、representativeness或success。

## 13. 高频追问

1. 250episodes为什么不等于250种init？
2. training/env/rollout/bootstrap seed分别覆盖什么？
3. task coverage为何不仅是task count？
4. difficulty怎样避免candidate outcome leakage？
5. equal/proportional/Neyman allocation各适合什么？
6. hard strata oversample后怎样汇总？
7. same seed为何还要snapshot hash？
8. coverage score与success有什么区别？
9. fixed benchmark task与task population怎样做CI？
10. 五项目当前各自coverage证据到哪一层？

## 14. Review Checklist 与下一入口

- [ ] task/init/difficulty/training-seed cube与schema已冻结；
- [ ] planned/attempted/valid/unique counts和exclusions完整；
- [ ] difficulty不由candidate final outcome事后定义；
- [ ] rare/critical minimum与target weights都明确；
- [ ] oversampling后按target weights重算，不报raw micro；
- [ ] A/B使用共同grid，training seed/task不confound；
- [ ] per-cell table、coverage、success/CI分开；
- [ ] 项目缺raw cube时保持WARN。

本节点保持`WARN/unseen`。下一内容节点固定为`VLA-EVAL-008`：perception / action / controller / recovery failure taxonomy；真实口述前不创建coaching state。

## References

1. [EVAL-007 Source Freeze](../sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)。
2. Neyman (1934)、Procgen、Agarwal/rliable与LIBERO registry，revision/hash见source freeze。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

