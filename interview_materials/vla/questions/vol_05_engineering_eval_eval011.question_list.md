# VOL 05 Engineering / Evaluation：EVAL-011 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Offline Metric / Online Success Correlation](../knowledge/vol_05_engineering_eval_eval011_offline_online_correlation.html)  
> 来源冻结：[EVAL-011 Source Freeze](../sources/vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval011.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-011` | L3 | P1 | matched policy-task panel、Pearson/Spearman/MMRV、cluster uncertainty、held-out prediction与causal boundary | card drafted / unseen |

## 边界

- correlation unit是policy/checkpoint或training run；episode只估计每个online点。
- 同task/support/protocol/scorer配对offline与online；不同协议结果不进入一个panel。
- 线性、rank、margin-aware ranking、held-out prediction与causal effect分别回答。
- cluster bootstrap、leave-one-out、pooled/within-task与selection/validation分离同时报告。
- 五项目当前均无可估计panel；本切片不生成EVAL-012，不创建或更新`coaching_state.md`。
