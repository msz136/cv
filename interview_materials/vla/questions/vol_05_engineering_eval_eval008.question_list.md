# VOL 05 Engineering / Evaluation：EVAL-008 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Perception / Action / Controller / Recovery Failure Taxonomy](../knowledge/vol_05_engineering_eval_eval008_failure_taxonomy_recovery.html)  
> 来源冻结：[EVAL-008 Source Freeze](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval008.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-008` | L2 | P0 | effect/mode/cause、first verified divergence、四层failure taxonomy、detector与recovery outcome | card drafted / unseen |

## 边界

- failure effect、observable mode、root-cause hypothesis、detector alarm和recovery outcome分开。
- primary layer是最早有verified evidence的偏差；上游缺日志时保持unknown。
- root cause需matched intervention、fix与同协议rerun；VLM explanation或单episode不够。
- detector与recovery分别报告precision/recall/delay/false alarm及eligible/triggered/recovered/unsafe denominator。
- 本切片不生成EVAL-009，不创建或更新`coaching_state.md`；下一内容节点固定为EVAL-009 raw trace与可复算summary。
