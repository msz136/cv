# VOL 05 Engineering / Evaluation：EVAL-013 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[End-to-End Latency / Deadline Miss / Jitter](../knowledge/vol_05_engineering_eval_eval013_end_to_end_latency_deadline_jitter.html)  
> 来源冻结：[EVAL-013 Source Freeze](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval013.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-013` | L2 | P1 | capture→apply、clock/critical path、p50/p95/p99、deadline miss、jitter、per-offset age、load/coordinated omission | card drafted / unseen |

## 边界

- `infer_ms`、response latency、first/per-offset action age、loop response与scheduler lateness分别定义。
- clock source/offset uncertainty、GPU synchronization、cold/warm/load/fault与request shape进入protocol。
- p50/p95/p99/max、miss k/n/CI、jitter、stale/drop/fallback、throughput和success/safety同时报告。
- intended arrival与actual send分开，避免closed-loop load generator低估tail。
- 五项目当前均无protocol-complete实时闭环；本切片不生成EVAL-014，不创建或更新`coaching_state.md`。
