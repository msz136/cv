# VOL 05 Engineering / Evaluation：EVAL-003 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Success Rate / Confidence Interval / Minimum Rollouts](../knowledge/vol_05_engineering_eval_eval003.html)  
> 来源冻结：[EVAL-003 Source Freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval003.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-003` | L2 | P0 | episode-level success、Wilson/exact CI、minimum rollout planning、cluster dependence 与 stopping rule | card drafted / unseen |

## 边界

- 题卡只考 Bernoulli statistical unit、Wilson/Clopper–Pearson、zero/all-success、margin-based sample size、task/seed/init clustering 和 optional stopping。
- UWM 186/250 只作 naive interval；OpenPiVLA 97.4% 因缺分母不可算；OPD 10k 只按 metric-specific observation unit 解释。
- paired significance 留给 `VLA-EVAL-004`，macro/micro/per-task aggregation 留给 `VLA-EVAL-005`。
- 本切片不生成 EVAL-004，不创建或更新 `coaching_state.md`。

