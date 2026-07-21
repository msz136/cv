# VOL 05 Engineering / Evaluation：EVAL-009 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Raw Predictions / Trace / Video / Recomputable Summary](../knowledge/vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)  
> 来源冻结：[EVAL-009 Source Freeze](../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval009.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-009` | L2 | P0 | raw/parsed rows、episode trace、video sidecar、conservation、provenance与deterministic recompute | card drafted / unseen |

## 边界

- raw rows是source of truth，summary是derived artifact，video是diagnostic sidecar。
- planned/valid/excluded/missing守恒；crash、timeout、missing和retry显式记录。
- checkpoint/protocol/scorer/reducer/raw/summary形成可验证lineage并有payload hashes。
- clean command从raw重算numerator/denominator/slices/overall才称recomputable。
- 本切片不生成EVAL-010，不创建或更新`coaching_state.md`；下一内容节点固定为EVAL-010 regression/golden/canary。
