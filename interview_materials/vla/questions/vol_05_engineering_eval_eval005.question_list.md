# VOL 05 Engineering / Evaluation：EVAL-005 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Macro / Micro / Per-task / Weighted Aggregation](../knowledge/vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)  
> 来源冻结：[EVAL-005 Source Freeze](../sources/vol_05_eval005_aggregation_estimand_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval005.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-005` | L2 | P0 | aggregation estimand、macro/micro/weighted、task/run hierarchy、missingness 与 stratified uncertainty | card drafted / unseen |

## 边界

- per-task `k/n/CI` 是主表；macro、micro、weighted 必须写出 task registry 和权重。
- A/B 使用共同 task set、共同 weights；paired raw data 先算差值再聚合。
- training seed 是顶层 replicate；task/init/episode cluster 不能展开成 iid。
- UWM 0.744 与 OpenPiVLA 97.4 只做现有 summary arithmetic audit；OPD 异构 metric 不合成总分。
- 本切片不生成 EVAL-006，不创建或更新 `coaching_state.md`；下一内容节点固定为 EVAL-006 versioning。

