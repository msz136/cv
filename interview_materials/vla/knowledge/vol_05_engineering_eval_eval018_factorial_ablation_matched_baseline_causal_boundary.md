# VOL 05 Engineering / Evaluation：EVAL-018 Factorial Ablation、Matched Baseline 与因果边界

> 状态：`drafted / VLA-EVAL-018 / knowledge_40_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 难度：L3　优先级：P0  
> 来源冻结：[EVAL-018 Source Freeze](../sources/vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)  
> 本页把“组件打开后指标更高”拆成可执行factor、matched cells、主效应/交互、run-level uncertainty和protocol内因果effect；不把五项目现有组合结果升级成单组件贡献。

## 1. 问题与结论先行

面试中最危险的回答是：“我把world loss加进去，成功率从A涨到B，所以world model有效。”这句话同时跳过了baseline是否matched、data/compute/seed/scorer是否共变、best checkpoint如何选、失败run是否被删，以及效果是否能外推。

高分答案应先说：

1. 定义要干预的factor和要估计的estimand；
2. 用完整factorial cells分离main effect与interaction；
3. 对training randomness和eval pairs做block/randomization，而不是把episode当training replicates；
4. 冻结data、budget、selection和scorer，失败run也入账；
5. 只在实验support内说因果，不从一个bundle contrast外推组件普遍有效。

## 2. 直觉：不要比较两个“礼包”

```text
危险比较：
baseline = old data + old code + default lr + last checkpoint + scorer A
candidate = more data + new head + tuned lr + best checkpoint + scorer B

可解释比较：
same frozen base bundle
  × factor A on/off
  × factor B on/off
  × randomized/blocked training runs
  × same paired evaluation registry
```

前者只能说“两个礼包数字不同”；后者才有机会回答某个factor的作用。factor不是标签，而是可执行、版本化的intervention：其code/config/data semantic diff必须可审计。

## 3. 五个基本对象

| 对象 | 面试中怎么定义 | 机器人/VLA例子 |
| --- | --- | --- |
| factor | 一个预注册、可执行的变化 | world loss on/off；route metadata on/off |
| arm/cell | factor levels的完整组合 | action-only、+world、+value、all |
| experimental unit | 独立接受factor并产生outcome的单位 | 一次完整training pipeline run |
| outcome | protocol-bound metric/cost/failure | paired sim success、latency、OOM rate |
| estimand | 对什么随机性、预算和support取平均 | frozen task/seed分布上的平均risk difference |

episode是trained policy的评估样本，不是独立training run。1000个episode不能补偿每个arm只有一个training seed。

## 4. 最小2×2 Factorial

以action主任务恒开、world/value为两个factor：

| Cell | World | Value | 能回答什么 |
| --- | --- | --- | --- |
| A00 | off | off | action-only baseline |
| A10 | on | off | value关闭时world的simple effect |
| A01 | off | on | world关闭时value的simple effect |
| A11 | on | on | 联合表现与interaction |

只跑A00和A11无法区分：A有效、B有效、两者都有效、只有interaction有效，或一个有益但被另一个抵消。NIST的full factorial要求每个factor setting与其他factor setting完整组合；`k`个二水平factor需要`2^k` cells。[1]

## 5. 主效应与交互效应

令`μ_ab`为冻结protocol内cell `(A=a,B=b)`的平均outcome。0/1编码下：

\[
\tau_A=\frac{(\mu_{10}-\mu_{00})+(\mu_{11}-\mu_{01})}{2},
\qquad
\tau_B=\frac{(\mu_{01}-\mu_{00})+(\mu_{11}-\mu_{10})}{2}.
\]

变量解释：`τ_A`把A在B=0和B=1时的两个simple effects平均；`τ_B`同理。直觉：主效应不是只看A10−A00。实现映射：从每个cell的seed×task raw rows计算contrast，并保留层次不确定性。[1][2]

加性interaction为：

\[
\tau_{AB}=\mu_{11}-\mu_{10}-\mu_{01}+\mu_{00}.
\]

变量解释：若A、B作用完全加和，`τ_AB=0`；正值可能是协同，负值可能是冲突。实现映射：A11最好不够，必须同时有另外三个cells。对于success probability，这是risk-difference尺度interaction；换成logit/odds尺度结论可能不同，必须声明scale。

## 6. 回归模型只是计算器，不是因果许可证

可用±1编码拟合解释性模型：

\[
g\!\left(E[Y_{r,e}]\right)=
\beta_0+\beta_Ax_A+\beta_Bx_B+\beta_{AB}x_Ax_B+b_r+c_e.
\]

变量解释：`r`是training run，`e`是task/init/eval block，`g`可为identity或logit；`b_r/c_e`表示层次/区组结构。直觉：模型把cell差异、interaction和nuisance block组织起来。实现映射：statsmodels可提供formula/ANOVA入口，但模型输出是否有因果意义仍取决于factor assignment、完整cells、missingness和protocol。[3]

报告时优先给cell table、effect estimate、CI与practical margin；`p<0.05`不能替代effect大小、方向稳定性和工程成本。

## 7. Matched Baseline 八项合同

| 维度 | 必须冻结 | 不匹配时最多能说 |
| --- | --- | --- |
| initialization | base checkpoint bytes、processor/normalizer、freeze policy | 不同lineage的bundle比较 |
| data | source pool、split、sampling、mix、dedupe | data+method联合变化 |
| optimization | optimizer、effective batch、schedule、precision | recipe联合变化 |
| budget | steps/tokens/FLOPs/wall-clock定义 | 不同资源下的系统比较 |
| tuning | search space、trials、compute、selection | candidate被额外调优 |
| evaluation | task/init/controller/scorer/pair IDs | protocol-confounded数字 |
| failure policy | OOM/NaN/timeout/invalid处理 | survivor-only观察 |
| semantic diff | 只含factor及必要mechanical adaptation | 多因素bundle contrast |

“同名数据集”“同epoch”“同seed”都不自动matched。打开auxiliary objective若同时增加视频样本、head容量和训练步数，应拆factor，或诚实称为system-bundle intervention。

## 8. Seed 与 Eval Pair：Block What You Can

NIST建议用blocking控制重要nuisance；Bouthillier等进一步指出ML benchmark需覆盖data sampling、augmentation、initialization和hyperparameter optimization等随机性，并推荐可行时做paired trainings。[1][2]

对同一block的factor contrast：

\[
d_{s,e}=Y_{1,s,e}-Y_{0,s,e},
\qquad
\widehat\tau=\frac{1}{|S||E|}
\sum_{s\in S}\sum_{e\in E}d_{s,e}.
\]

变量解释：`s`是training/data randomness block，`e`是相同task/init episode pair。直觉：先做block内差值，减少无关波动。实现映射：training/data/env/rollout/bootstrap seeds必须分字段；CI按training run与task/episode hierarchy cluster/bootstrap，不能把episode伪装成training replicate。[2][4]

相同整数seed不保证新增module后RNG call sequence相同。能保持coupling时pair；不能时仍要随机化和重复，并明确哪些randomness未配对。

## 9. Fixed Recipe 与 Equal Search Budget

### 9.1 机制诊断

\[
\Delta_{\mathrm{fixed}}=
E\!\left[Y(\mathrm{on},\lambda_0,B)-Y(\mathrm{off},\lambda_0,B)\right].
\]

`λ0`是共同recipe，`B`是固定预算。它回答“其他recipe不变时打开组件怎样”，便于定位机制；但新组件可能需要不同loss weight/lr，负结果不代表最佳可达能力一定无效。

### 9.2 系统能力

\[
\Delta_{\mathrm{tuned}}=
E\!\left[Y(\mathrm{on},\widehat\lambda_{on},B,H)-
Y(\mathrm{off},\widehat\lambda_{off},B,H)\right].
\]

`H`是两arm相同的search space、trial/compute budget、validation selection与fresh holdout协议。它回答“给同等调参资源后哪个pipeline更好”。candidate调50次、baseline用默认值，既不是公平系统比较，也不能支持component因果。[2]

两种estimand都值得报告，但不能混成一个结论。

## 10. 四本资源账

1. **Data**：unique samples、tokens/frames/actions、mix、repeat与augmentation；
2. **Optimization**：updates、effective batch、schedule position与gradient accumulation；
3. **Compute**：FLOPs近似、GPU-hours、peak memory、retry/failure；
4. **Capacity/runtime**：trainable params、latency、throughput、planning calls。

同epoch在数据量不同的arms上不等token；同steps在模型FLOPs不同的arms上不等compute。可以并列fixed-token、equal-FLOP与equal-wall-clock结果，但必须先定义每个estimand。

## 11. 失败 Run、Selection 与 Test Leakage

```text
planned = not_started + started
started = completed_valid + failed_runtime + excluded_protocol
```

OOM、NaN、timeout、load failure和invalid output必须保留。若factor导致更高failure rate，它就是重要engineering outcome；只比较survivors会产生post-treatment selection bias。

checkpoint selection也要matched：

- 预注册metric、cadence、patience、tie-break与eligible set；
- 所有cells用同validation support和selection budget；
- test/real-canary不参与调weight/threshold/checkpoint；
- last、pre-registered selected与oracle-best分开；
- repaired rerun使用新run ID，不能覆盖失败run。

## 12. Binary Success、层次与 Multiplicity

closed-loop success至少按cell报告`k/n/CI`、per-task结果、macro/micro、training-seed分布和paired difference。训练run是factor assignment unit；episode只估计该policy的conditional success。

多个factors×tasks×metrics×checkpoints会制造大量比较。primary outcome、primary contrast、practical margin和confirmatory family应事前冻结；其余标exploratory。Holm/FDR可处理multiplicity，但修复不了不匹配protocol、post-hoc factor或失败run丢失。[4]

## 13. 什么时候可以说“因果”

potential outcome记为`Y_u(1),Y_u(0)`。随机化/区组化factorial要识别冻结protocol内effect，至少需要：[5]

| 假设 | 对应工程检查 |
| --- | --- |
| consistency | 每个factor level只有一个版本化实现；无隐藏data/head/weight变体 |
| exchangeability | arm assignment不按好seed、好hardware或预览结果决定 |
| positivity | 目标task/seed/hardware block内所有必要cells都有机会运行 |
| no interference | run间不共享会被candidate改变的数据、cache、label或adaptive scorer |
| outcome accounting | failed/excluded/missing按预注册规则守恒 |

即使全部满足，最强结论也是：“在冻结model/data/budget/task/eval support上，factor A使outcome平均变化多少。”它不自动意味着新机器人、真机、长期部署或所有VLA都受益。

### Claim ladder

```text
mechanism hypothesis
 -> two bundle numbers differ
 -> matched contrast with uncertainty
 -> randomized factorial effect in frozen protocol
 -> replicated effect across new support
 -> deployment utility / safety evidence
```

不要跨级。

## 14. Factor 多时怎么办

`k`个二水平factor需要`2^k`cells。factor多时可先在offline/sim做screening，再对少数高价值factor跑完整factorial；若使用fractional factorial，必须声明resolution和alias structure。fractional design节省计算但会让某些effects混叠；one-factor-at-a-time则容易漏interaction。[1]

推荐顺序：

1. 机制/风险筛选2—4个factor；
2. 低成本screening；
3. 完整factorial+多个training seeds；
4. paired closed-loop confirmatory；
5. 新support replication；
6. 真实部署另走EVAL-017 gate。

## 15. Artifact 与执行 Pipeline

```text
preregistration + base bundle
 -> design matrix + randomized blocks
 -> immutable planned run registry
 -> all attempts/checkpoints/failures
 -> common selection rule
 -> paired raw evaluation rows
 -> cell/main/interaction/cost summaries
 -> deviation + multiplicity + claim decision
```

```python
def evaluate_factorial(spec, factor_grid, train_blocks, eval_pairs):
    # Freeze every planned cell, estimand and outcome before seeing results.
    design = randomize_within_blocks(factor_grid, train_blocks, spec)
    registry = create_planned_registry(design)

    for row in design:
        # Materialize only declared factor changes and record semantic diffs.
        arm = build_versioned_arm(spec.base_bundle, row.factor_levels)
        assert_declared_diffs_only(arm, row)
        try:
            result = train_under_budget(arm, spec.budget)
            registry.complete(row, result)
        except Exception as failure:
            # Failure is an outcome, not a seed that may be silently removed.
            registry.fail(row, failure)

    # Use one selection rule and the same task/init IDs for every valid arm.
    selected = select_on_validation(registry, spec.selection)
    raw = evaluate_same_pairs(selected, eval_pairs, spec.scorer)
    return estimate_cells_effects_interactions_and_cost(raw, registry, spec)
```

这是应补做的实验合同，不是个人项目已有实现。[6]

## 16. 五项目真实性映射

### UWM / LIBERO

`186/250` fixed-pruned-init与`232/250` reset-style改变了init/warmup/distribution，是protocol sensitivity，不是模型factor effect；raw pairs/checkpoint也缺。先做同checkpoint、同episode IDs的protocol对照，再谈action-only/+video objective arms。[6]

### WAM / Cosmos

action/future/value上游机制已核；action-only/+world/+value/all目前只是设计建议。本地只有单episode diagnostic，缺四cells、training seeds、checkpoint和完整closed-loop denominator。

### OpenPiVLA

formal Qwen causal-CE与archived flow-matching metadata不在同一闭合lineage，不能把差异叫objective ablation。official-checkpoint diagnostics与97.4 summary也不能替代formal matched cells。

### Robot Harness

32B base与SFT/GRPO的holdout `n`和hidden-embedding/token-overlap scorer不同；当前ladder不能支持严格uplift。下一步先统一suite/n/scorer/raw prediction，再做scope/no-arg/restraint reward factorial。

### OPD

五teacher、coldstart、route KL、synthetic mix一起构成组合路线；缺SFT-only、single-teacher、no-synthetic、ratio/route ablation。可讲机制与10k static holdout结果，不能说某组件单独带来提升。

五项目都未达到“matched factorial + full run ledger + paired raw eval + causal assumptions”的C2/C3门槛。

## 17. 面试追问防线

- **为什么不是只删模块？** 因为要定义factor、estimand、预算和interaction；删模块可能同时改data/compute/capacity。
- **为什么同seed还不够？** 一个seed不代表随机性分布，且不同graph可能消费不同RNG序列。
- **A11最好能说A、B都有效吗？** 不能，必须看四cells的main/simple/interaction effects。
- **baseline需要重新调参吗？** fixed-recipe与equal-search-budget回答不同问题，应分开报告。
- **OOM seed怎么处理？** 进入planned/failed账本；不能静默删除或用新seed覆盖。
- **episode很多为什么仍不显著？** factor分配单位是training run，episode是层次内样本。
- **什么时候能说因果？** factor assignment、完整cells、consistency/exchangeability/positivity/no-interference和outcome accounting闭合时，只在冻结support内说。
- **你的项目做过吗？** 当前五项目没有完整matched factorial；我能讲设计与缺口，不能编造effect。

## 18. 本节点状态

EVAL-018知识节点与一张题卡已起草并保持`WARN/unseen`。本页没有新增任何项目uplift、单组件因果或ownership结论；没有真实口述前不创建`coaching_state.md`。下一节点是`VLA-EVAL-019`：checkpoint selection、Pareto frontier与holdout overfit。

## 参考文献（References）

1. NIST/SEMATECH, [Full factorial](https://www.itl.nist.gov/div898/handbook/pri/section3/pri333.htm)、[Two-level full factorial](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3331.htm)与[Randomized block designs](https://www.itl.nist.gov/div898/handbook/pri/section3/pri332.htm)。
2. Bouthillier et al., [*Accounting for Variance in Machine Learning Benchmarks*, arXiv:2103.03098v1](https://arxiv.org/abs/2103.03098v1)。
3. statsmodels, [`anova.py`@`1bf73ad`](https://github.com/statsmodels/statsmodels/blob/1bf73add5d92f64e48cf2ca143dfeef9811e4eac/statsmodels/stats/anova.py)。
4. [EVAL-004 Paired Evaluation](vol_05_engineering_eval_eval004_paired_init_seed_significance.html)、[EVAL-005 Estimand](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)与[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)。
5. Hernán & Robins, [*Causal Inference: What If*](https://miguelhernan.org/whatifbook)，2025-11-21 edition。
6. [EVAL-018 Source Freeze](../sources/vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)及[五项目inventories](../evidence/evidence_manifest.html)。
