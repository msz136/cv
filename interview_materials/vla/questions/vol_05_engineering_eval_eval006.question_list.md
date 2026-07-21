# VOL 05 Engineering / Evaluation：EVAL-006 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Versioned Evaluation Manifest](../knowledge/vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)  
> 来源冻结：[EVAL-006 Source Freeze](../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval006.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-006` | L2 | P0 | label/revision/digest、versioned eval manifest、protocol SHA、semantic diff与migration bridge | card drafted / unseen |

## 边界

- SemVer/API compatibility、environment name、controller/scorer label都不能替代resolved semantic identity。
- episode、summary、video和lineage必须绑定单一protocol SHA；比较前先做manifest diff。
- 五项目当前都缺至少一段run-specific benchmark→env→controller→scorer→raw-result lineage，不升级成绩。
- 本切片不生成EVAL-007，不创建或更新`coaching_state.md`；下一内容节点固定为EVAL-007 coverage。

