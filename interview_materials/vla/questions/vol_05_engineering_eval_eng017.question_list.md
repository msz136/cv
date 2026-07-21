# VOL 05 Engineering / Evaluation：ENG-017 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[训练可观测性](../knowledge/vol_05_engineering_eval_eng017.html)  
> 来源冻结：[ENG-017 Training Observability Source Freeze](../sources/vol_05_eng017_training_observability_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng017.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-017` | L2 | P0 | loss/grad、AMP overflow、data_wait、communication、Profiler 与 lineage schema | card drafted / unseen |

## 边界

- 题卡只考 numerical/data/compute/comm/lineage 五层、AMP skipped step、短窗口 Profiler、first-failure replay 和告警归因。
- UWM/OPD 只使用现有 summary/profile hook 证据，不把配置、摘要或单卡 profile 升级为完整 rank telemetry、吞吐或稳定性证明。
- 本切片不生成 `VLA-ENG-018`，不创建或更新 `coaching_state.md`。

