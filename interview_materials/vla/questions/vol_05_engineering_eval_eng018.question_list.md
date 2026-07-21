# VOL 05 Engineering / Evaluation：ENG-018 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Scheduler / Preemption / Retry](../knowledge/vol_05_engineering_eval_eng018.html)  
> 来源冻结：[ENG-018 Scheduler / Preemption / Retry Source Freeze](../sources/vol_05_eng018_scheduler_preemption_retry_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng018.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-018` | L2 | P1 | scheduler、preemption、retry、committed checkpoint 与幂等副作用 | card drafted / unseen |

## 边界

- 题卡只考 logical run/attempt/rank、SIGTERM/grace、安全边界 checkpoint、manifest-last/`COMMITTED`、duplicate execution 与 recovery drill。
- UWM/OPD/OpenPiVLA 只使用现有 metadata、final-only 或远端 path 证据，不把它们升级为 exact resume、exactly-once 或 world-size continuity 证明。
- 本切片不生成 `VLA-ENG-019`，不创建或更新 `coaching_state.md`。

