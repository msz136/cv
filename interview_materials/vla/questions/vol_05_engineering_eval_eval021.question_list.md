# VOL 05 Engineering / Evaluation：EVAL-021 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Deployment Drift / Data Shift / Continuous Monitoring](../knowledge/vol_05_engineering_eval_eval021_deployment_drift_data_shift_continuous_monitoring.html)  
> 来源冻结：[EVAL-021 Source Freeze](../sources/vol_05_eval021_deployment_drift_data_shift_continuous_monitoring_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval021.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-021` | L3 | P1 | data/concept/protocol/system/scorer drift、reference/window/slice、MMD/JS/ADWIN、delayed outcome、alert budget与gated response | card drafted / unseen |

## 边界

- distribution drift只说明已定义signal变化，不自动证明performance或safety下降。
- reference/current必须绑定lineage、context、sampling unit、support、seasonality与scorer。
- outcome延迟时保持`impact_pending`并监控label coverage/delay，不能让proxy替代真实结果。
- rollback、recalibrate或retrain必须经过cause、regression、fresh audit与shadow/canary gate。
- 五项目只有离线reference/schema输入，没有timestamped deployment monitoring或自动重训证据。
- 本切片不生成EVAL-022或`coaching_state.md`。
