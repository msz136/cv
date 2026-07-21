# VOL 05 Engineering / Evaluation：ENG-016 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Student + Multiple Teachers 的显存与调度](../knowledge/vol_05_engineering_eval_eng016.html)  
> 来源冻结：[ENG-016 Student + Multiple Teachers Source Freeze](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng016.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-016` | L3 | P1 | teacher freeze/no-grad、KL/mask、多教师 memory schedule 与 OPD 因果边界 | card drafted / unseen |

## 边界

- 题卡只考 student-only backward、KL input/target/reduction、resident/sequential/staged schedule、matched A/B 和 lineage/replay。
- OPD 只使用 inventory 已冻结的五教师、route metadata、coldstart/online KL 事实；不把多教师写成 learned router 或单因果 uplift。
- 本切片不生成 `VLA-ENG-017`，不创建或更新 `coaching_state.md`。

