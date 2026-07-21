# VOL 05 Engineering / Evaluation：EVAL-018 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Factorial Ablation / Matched Baseline / Causal Boundary](../knowledge/vol_05_engineering_eval_eval018_factorial_ablation_matched_baseline_causal_boundary.html)  
> 来源冻结：[EVAL-018 Source Freeze](../sources/vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval018.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-018` | L3 | P0 | factor/estimand、2×2 cells、matched baseline、main/interaction、seed/eval blocks、failure/selection与protocol内因果边界 | card drafted / unseen |

## 边界

- A00与A11只能比较bundle；分离A、B和interaction至少需要完整2×2 cells。
- matched baseline同时冻结initial bundle、data、budget、tuning、selection、eval/scorer和failure policy。
- training run是factor assignment unit；episode不能替代多个training seeds。
- fixed-recipe effect与equal-search-budget system effect回答不同问题。
- failed/OOM/NaN/invalid runs进入planned账本；不能只比较survivors。
- 五项目均无完整matched factorial；本切片不生成EVAL-019或`coaching_state.md`。
