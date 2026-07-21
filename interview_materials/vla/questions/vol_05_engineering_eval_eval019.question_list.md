# VOL 05 Engineering / Evaluation：EVAL-019 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Checkpoint Selection / Pareto / Holdout Overfit](../knowledge/vol_05_engineering_eval_eval019_checkpoint_selection_pareto_holdout_overfit.html)  
> 来源冻结：[EVAL-019 Source Freeze](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval019.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-019` | L2 | P0 | candidate/metric roles、selection optimism、adaptive holdout、hard gates、Pareto/uncertainty、decision rule与fresh audit | card drafted / unseen |

## 边界

- validation上从多个checkpoint取max会产生selection optimism；candidate/query history必须入账。
- hard artifact/safety/deadline gate先形成feasible set，不能被overall分数抵消。
- Pareto frontier保留不支配trade-off，不自动给唯一winner；必须选择一个真实bundle。
- early stopping、best seed、threshold修改、失败视频和leaderboard查询都可能参与selection。
- dev选完锁定bundle；final audit若驱动回改，就进入development history并开启新cycle。
- 五项目均无完整selection→fresh audit链；本切片不生成EVAL-020或`coaching_state.md`。
