# VOL 05 Engineering / Evaluation：ENG-022 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Policy Server Resilience](../knowledge/vol_05_engineering_eval_eng022.html)  
> 来源冻结：[ENG-022 Policy Server Resilience Source Freeze](../sources/vol_05_eng022_policy_server_resilience_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng022.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-022` | L3 | P0 | bounded queue、compatible batching、deadline/cancel、action freshness、safe fallback 与 resilience drills | card drafted / unseen |

## 边界

- 题卡只考 admission/backpressure、batch key/max delay、deadline budget、cancellation、action validation、fallback TTL/watchdog 和 p99/action-age evidence。
- OpenPI 只作为逐请求 WebSocket infer/timing/error baseline；OpenPiVLA 只作为 offline timeout report；Robot Harness 只作为 tool-side timeout/cancel/compensation 局部证据。
- 不把 WebSocket、`max_batch_size`、timeout 参数或重试逻辑升级为多机器人 VLA policy-server SLO/fairness/safety 已实现。
- 本切片不生成后续 resilience 节点，不创建或更新 `coaching_state.md`。

