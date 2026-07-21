# VOL 05 EVAL-007 Source Freeze：Init / Seed / Task Coverage 与难度分层

> 状态：`source_frozen / VLA-EVAL-007 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 coverage cube、training/env/rollout seed 层级、task/init support、难度标签来源、stratified allocation、oversampling reweighting 与五项目 coverage 边界；下游只生成一张 `VLA-EVAL-007` 原子题卡，VOL 05 同步为 knowledge/cards 29/44。

## 问题（Question）

“每个 task 跑 50 次”并不能证明覆盖充分：50 次可能重复同一 init family、只用一个 training seed、漏掉 rare contact/occlusion/recovery strata，或只覆盖五个方便 task。强回答要把 task、init/difficulty、training seed 和 rollout repeat 组成预注册 coverage cube，报告 planned/attempted/valid/unique counts、target weights 与每格不确定性。

本 source gate 固定以下链路：

```text
target population + risk constraints
  -> task / init / difficulty / training-seed strata
  -> planned minimum + allocation + unique support
  -> attempted / valid / excluded cell ledger
  -> per-cell result + target-weighted aggregate
  -> uncovered regions + exploratory slices
```

## 1. 冻结来源、revision 与许可

公开 hash 对 2026-07-18 取得的 UTF-8 原文计算。分层采样和 procedural-level generalization 只支持方法边界；它们不证明本地 VLA task/init 分布代表真实部署。

| ID | 来源 | 类型 / revision | 固定入口 | SHA-256 | 支持范围 |
| --- | --- | --- | --- | --- | --- |
| S1 | Neyman (1934), stratified sampling | primary / DOI | [DOI](https://doi.org/10.2307/2342192) | DOI 指纹 | stratified sampling、allocation 与 purposive selection 的统计边界 |
| S2 | Cobbe et al., *Leveraging Procedural Generation to Benchmark Reinforcement Learning* | primary / arXiv `1912.01588` | [arXiv](https://arxiv.org/abs/1912.01588) | response `3c3062b173aaae5dea5cabd8a82908b0fb66390803fe3c620dad990994801541` | train/test level 分离、有限环境覆盖与generalization gap；不自动迁移为机器人真实部署保证 |
| S3 | Agarwal et al. / `rliable` | primary + official-code / arXiv `2108.13264`, commit `3ccd9f4dea577a04d3d2b557f259aac08badbd81`, Apache-2.0 | [paper](https://arxiv.org/abs/2108.13264) / [repo](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81) | paper response `74f11076d64de0f6beb9da4a9b185dd2a42465bfde6426fb2004fd6fd9e042ac`; library `0af084e4040fad3ae02a612b16fbcc59d9a141ac8259ad47dc1932bcc168ac14`; metrics `caf0c74e6238a12d2f59d6bcd47115e56167ea73c3b851c3f7981de17e5230cc` | run×task matrix、fixed-task/task-population bootstrap 与完整分布报告 |
| S4 | LIBERO task registry / metric | official-code / commit `8f1084e3132a39270c3a13ebe37270a43ece2a01`, MIT | [registry](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/benchmark/__init__.py) | registry `4ce6edbb00b3280692f2e2b2e8a14bf6e2d5878965b0484a386c0355a867ecc5`; metric `4fe37407f23cd9c1ceb4c93670f308d2fed6d34b2c2139d86123702c849cabcb`; eval config `e9775e56a15317666ee8248f7e9d59072b9469c0f7346dc3ed496484657c6bcd`; LICENSE `e2885fd30a08381b799c4a33385522b23d637b4051b8f9a7f9f2519944b68ff6` | ordered suites/tasks、per-task success与default eval count；不证明项目实际覆盖这些init/task |
| S5 | EVAL-004 / EVAL-005 / EVAL-006 | canonical local source freezes | [paired](vol_05_eval004_paired_init_seed_significance_source_freeze.html) / [aggregation](vol_05_eval005_aggregation_estimand_source_freeze.html) / [versioning](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html) | `c89c052a630692a12a20235fa6d53278f43e4509c6e567110f81f7c2eb427313`; `16b6a4c7c8e284ca8bd8a7cc831c3fc553405668ea87a071c23147f8f804ff46`; `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054` | seed taxonomy、common support/weights、protocol identity与missingness前置合同 |
| S6 | Benchmark / Evidence Audit | canonical local source | [audit](vol_04_benchmark_evidence_claim_to_protocol.html) | `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a` | LIBERO default、UWM 50 OOD init×3 seeds、Cosmos/RoboCasa task/init protocol |
| S7 | 五项目 inventories | local evidence boundary | [manifest](../evidence/evidence_manifest.html) | individual hashes in review | 当前 task/init/seed/format/suite coverage 与raw artifact缺口 |

## 2. Count、support、coverage、representativeness 分开

| 概念 | 问题 | 例子 |
| --- | --- | --- |
| count | 跑了多少条？ | 250 episodes、10k rows |
| unique support | 覆盖多少不同条件？ | unique init snapshot、unique image、task family |
| coverage | 预注册 strata 中哪些达到最低样本？ | contact×OOD-pose×training-seed cell |
| representativeness | sample weights 是否对应目标总体？ | deployment task mixture |

大 count 可以由重复同一简单条件得到；coverage高也可能使用人为均匀分布而不代表部署。报告必须同时给 count、unique support、coverage matrix和 target weights。

## 3. Coverage Cube

定义 cell：

\[
h=(t,d,i,s_{train}),
\]

其中 `t` 是 task/family，`d` 是预注册difficulty/risk stratum，`i` 是init/scene/object stratum，`s_train` 是model training seed。每格内可有多个rollout stochastic repeats，但repeat不能替代新的training seed或unique init。

最低ledger字段：

```text
cell_id, task_id, task_revision, difficulty_schema,
difficulty_bin, init_snapshot_hash, init_family,
training_seed, env_seed, rollout_seed, protocol_sha,
planned_n, attempted_n, valid_n, unique_init_n,
success_k, exclusions, target_weight
```

若模型A/B比较，coverage cube和weights必须共同；缺格沿用EVAL-004/005的fail-closed或预注册missing rule。

## 4. Coverage 指标

设cells为 `h=1..H`，目标权重 `W_h≥0` 且和为1，最低有效样本 `m_h`，实际valid count `n_h`：

\[
C_w=\sum_{h=1}^{H}W_h\,\mathbf 1[n_h\ge m_h].
\]

变量解释：`C_w` 是本节点定义的target-weight coverage；它只说明哪些目标区域达到minimum，不是模型success。实现还应报告unweighted cell coverage、`n_h/m_h`、unique init ratio、weight coverage和每格success/CI。

风险关键格可以设更高 `m_h` 或hard gate；不能用大量easy-cell episodes把未覆盖的safety/contact cell平均掉。

## 5. Seed Coverage：四类seed再次分层

| seed | coverage含义 | 常见错误 |
| --- | --- | --- |
| training seed | 训练方法的run-to-run variability | 一个checkpoint的episode数替代多runs |
| environment/init seed | reset distribution候选索引 | same integer直接当same init |
| rollout stochastic seed | 固定checkpoint/init内sampling noise | 重复rollout当unique init |
| resampling seed | bootstrap/permutation可复算 | 当成实验coverage |

理想blocked design让每个training seed覆盖同一task/init grid；若不同training seeds只跑不同task，training variation与task difficulty完全confounded。same seed还要用init snapshot/hash和protocol SHA验证。

## 6. Task Coverage

task coverage至少分三层：

1. **registry coverage**：planned task IDs中attempted/valid多少；
2. **family/skill coverage**：grasp、place、contact、long-horizon、navigation、tool safety等族；
3. **deployment/risk coverage**：目标流量和高severity场景是否覆盖。

task taxonomy本身是设计：把一个skill拆成十个近似task会抬高macro票数和cell count。保存ordered registry hash、family labels、inclusion/exclusion和版本；新增task时在common registry上重算旧模型。

## 7. Init Coverage

init不是一个seed整数，而是状态分布。建议保存：

- exact snapshot/hash、reset后state/proprio和首帧checksum；
- object pose/rotation、relative geometry、scene/layout/style；
- distractor、background、lighting、camera/view、occlusion；
- contact/friction/gripper state、initial robot pose；
- in-distribution / interpolation / OOD shift标签及生成规则。

只报min/max range不能证明内部density或corner coverage；unique seed也不证明unique state。近重复init可按state/image distance或生成metadata聚类，报告cluster-level support。

## 8. Difficulty 分层：先定义，再看candidate outcome

难度最好来自**候选模型无关**的metadata：

| 维度 | 可冻结特征 |
| --- | --- |
| horizon/composition | required stages、expert/demo length、subgoal count |
| geometry/precision | target tolerance、pose distance/rotation、clearance |
| contact/dynamics | contact transitions、friction/compliance、grasp mode |
| perception | occlusion、distractor count、camera shift、object size |
| language | instruction length、relations、ambiguity/compositionality |
| recovery | perturbation、off-nominal start、required replan |
| safety | severity、forbidden side effect、intervention requirement |

可以用frozen baseline或独立pilot success定义empirical difficulty，但baseline/checkpoint、sample和bin edges必须在候选模型评估前冻结，最好与final holdout分开。根据候选模型失败后再定义“hard bin”会产生post-hoc选择；可以做exploratory failure slice，但不用于primary robustness claim。

难度常是多维vector，不必强压成easy/medium/hard单轴。每个bin要有minimum count、merge rule和unknown bucket，避免只展示有利切片。

## 9. Allocation：估计、诊断与风险目标不同

### 9.1 Proportional allocation

若目标是部署mixture总体估计，常以 `n_h≈nW_h` 分配；micro自然接近target weights。但rare/hard格可能样本太少。

### 9.2 Equal / minimum-per-cell

equal allocation或每格最低 `m_h` 适合诊断与发现tail failure，但它不是部署分布。总体估计必须按target `W_h`重加权，不能直接报oversampled micro。

### 9.3 Neyman allocation

在近似独立strata、已知/可pilot估计方差和cost时，经典allocation可写：

\[
n_h\propto\frac{W_h\sigma_h}{\sqrt{c_h}},
\qquad \sigma_h\approx\sqrt{p_h(1-p_h)}.
\]

变量解释：`W_h`是目标权重，`sigma_h`是stratum outcome标准差，`c_h`是单样本成本。对binary success，pilot估计 `p_h`；未知时不能从候选final outcomes反向优化并继续当预注册设计。

### 9.4 Hybrid risk allocation

工程上可先给每个critical/rare格minimum，再把剩余budget按target weight、variance或cost分配。无论怎样oversample，最终同时报告raw sample mix、target weights和reweighted estimate。

## 10. Train / Validation / Final Coverage 分离

- training levels/init不可泄漏到final exact snapshots；
- pilot可估difficulty/variance，但不和final p-value混用；
- validation用于checkpoint/hyperparameter和difficulty schema冻结；
- final holdout保持版本、registry、weights和exclusion rule锁定；
- procedural generation需要保存generator version/config/seed list，train/test level集合不重叠。

Procgen的train/test levels说明有限level训练可能产生generalization gap，但不能把“不同seed”自动当成语义充分的新场景。

## 11. Uncertainty 与多重切片

按目标推断层级resample：training runs顶层、task/init strata保留，重复episode不展开为iid。每格报告 `k/n + CI`；primary aggregate按EVAL-005固定weights重算。

大量difficulty slices会产生multiple-comparison问题。预注册primary slices；其余标exploratory并报告完整slice family，不从最差/最好bin单独做总体结论。空格/小格显示`insufficient coverage`，不静默合并。

## 12. 五项目真实性边界

### 12.1 UWM

user-confirmed summary写5 tasks×50，但缺250 row-level episode、exact unique init IDs、training-seed grid和difficulty metadata。task count平衡不等于init/seed coverage。论文Table II的50 OOD initializations×3 finetune seeds属于另一protocol，不能补齐local coverage。moka/mug低分可作为exploratory hard-task signal，不能事后宣称接触/长时序根因。

### 12.2 WAM

当前local-direct diagnostic只覆盖CoffeePressButton、episode0、一个seed/env_seed、base/trained两条trace且都failure；它是matched diagnostic，不是task/init coverage。项目页24 tasks×5、86/120/84/118缺raw episode和versioned manifest，不能计算coverage cube。

### 12.3 OpenPiVLA

archive只有spatial/object/goal/LIBERO-10 suite summaries；缺per-task trial、seed、init和raw episodes。四suite表不证明task或difficulty coverage，formal Qwen runs也没有和archive eval lineage闭合。

### 12.4 OPD

10k raw-holdout有box6100/point1400/text2500、8,251 unique images、1,168重复paths/2,917 rows位于重复images，并有by-format/by-pool表。这是当前最强coverage evidence，但quota是评估设计，不自动代表deployment。应按image cluster、pool/domain、format、seen/unseen/hard和metric-specific strata报告。

### 12.5 Robot Harness

project/safety/browser/cross suite n差异大，browser是deferred format-only，不能算execution coverage；project sandbox高分也不覆盖vision/controller/physics。SFT task-family counts是training data mix，不是eval/deployment coverage。应建立tool family×scope×side-effect severity×trajectory length×runner availability matrix，并用target weights重算。

## 13. Coverage Planner 伪代码

```python
def plan_and_score_coverage(registry, target_weights, min_counts, rows):
    # 1. Build cells from frozen task/init/difficulty/training-seed schemas.
    cells = build_cells(registry)
    validate_weights(target_weights, cells)

    # 2. Count attempted/valid/unique support without treating repeats as new init.
    ledger = summarize_cells(rows, unique_key="init_snapshot_hash")

    # 3. Fail closed on missing critical cells; compute coverage, not success.
    weighted_coverage = sum(
        target_weights[h] * int(ledger[h].valid_n >= min_counts[h])
        for h in cells
    )

    # 4. Estimate outcomes separately with target weights and cluster-aware CI.
    estimate = stratified_estimate(rows, target_weights,
                                   clusters=["training_seed", "init_family"])
    return {"ledger": ledger, "coverage": weighted_coverage,
            "estimate": estimate}
```

伪代码是artifact contract，不是五项目已存在平台。coverage score不能替代per-cell ledger、representativeness审查或模型success。

## 14. Source Gate 结论与下一入口

EVAL-007保持`WARN`：stratified allocation、coverage cube、seed/task/init层级、difficulty leakage防线与五项目coverage边界已冻结；没有一个项目同时具备完整target registry、raw rows、unique init、multi-training-seed和difficulty schema，因此不产生新的coverage或robustness强claim。

下一内容节点固定为`VLA-EVAL-008`：perception / action / controller / recovery failure taxonomy。题卡保持`unseen`，真实口述前不创建`coaching_state.md`。

## References

1. Neyman, “On the Two Different Aspects of the Representative Method,” [DOI](https://doi.org/10.2307/2342192)。
2. Cobbe et al., [*Leveraging Procedural Generation to Benchmark Reinforcement Learning*](https://arxiv.org/abs/1912.01588)。
3. Agarwal et al. / [`rliable`](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81)。
4. LIBERO frozen [task registry](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/benchmark/__init__.py)。
5. [EVAL-004](vol_05_eval004_paired_init_seed_significance_source_freeze.html)、[EVAL-005](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)。
6. [Benchmark / Evidence Audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html) 与五项目inventories。

