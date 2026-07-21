# VOL 05 Engineering / Evaluation：EVAL-007 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Init / Seed / Task Coverage 与难度分层](../knowledge/vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)  
> 来源冻结：[EVAL-007 Source Freeze](../sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval007.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-007` | L3 | P1 | coverage cube、seed层级、difficulty schema、stratified allocation与oversampling reweighting | card drafted / unseen |

## 边界

- count、unique support、coverage、representativeness和success必须分开。
- difficulty schema在candidate final前冻结；post-hoc failure slice只作exploratory。
- rare/hard oversampling后按target weights重算；training seed/task/init不展开成iid。
- 五项目均缺完整raw coverage cube，不升级coverage或robustness claim。
- 本切片不生成EVAL-008，不创建或更新`coaching_state.md`；下一内容节点固定为EVAL-008 failure taxonomy。

