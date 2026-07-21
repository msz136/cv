# VOL 05 Engineering / Evaluation：ENG-020 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Secret Lifecycle / Permission / Logging](../knowledge/vol_05_engineering_eval_eng020.html)  
> 来源冻结：[ENG-020 Secret / Permission / Logging Source Freeze](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng020.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-020` | L2 | P1 | secret lifecycle、data-purpose authorization、allowlist/redaction logging 与 audit negative tests | card drafted / unseen |

## 边界

- 题卡只考短期 scoped lease、deny-by-default/every-request authorization、data permission manifest、allowlist-first logging、audit protection 和 canary/deny-case/incident drill。
- Robot Harness 只作为 `__access_token` 定点 masking、dedup exclusion 与 robot/tool scope 的局部直接证据；UWM/OpenPiVLA/OPD 只作为 args/path/summary exposure 证据。
- 本切片不声称统一 secret manager、rotation/revoke、IAM、data governance、generic redaction 或 audit protection 已实现。
- 本切片不生成 `VLA-ENG-021`，不创建或更新 `coaching_state.md`。

