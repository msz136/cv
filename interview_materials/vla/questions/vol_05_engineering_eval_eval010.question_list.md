# VOL 05 Engineering / Evaluation：EVAL-010 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Regression Gate / Golden Set / Canary Rollout](../knowledge/vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)  
> 来源冻结：[EVAL-010 Source Freeze](../sources/vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval010.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-010` | L2 | P0 | versioned golden、paired non-inferiority、critical hard gate、shadow/canary与abort/rollback | card drafted / unseen |

## 边界

- checkpoint curve、smoke、holdout summary、golden set、regression gate与canary是不同证据层。
- golden case/expected/slice/margin在candidate评估前冻结；训练污染与事后改gold显式拒绝。
- 新旧模型在同protocol/scorer/common support上逐case配对；critical/safety/latency不被overall抵消。
- shadow无actuator authority；canary冻结exposure/window/guardrail，失败abort并回滚known-good完整bundle。
- 本切片不生成EVAL-011，不创建或更新`coaching_state.md`；下一内容节点固定为offline-online correlation。
