# VOL 05 Engineering / Evaluation：EVAL-014 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Forbidden Side Effect / Scope / Cancel / Compensation](../knowledge/vol_05_engineering_eval_eval014_forbidden_side_effect_scope_cancel_compensation.html)  
> 来源冻结：[EVAL-014 Source Freeze](../sources/vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval014.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-014` | L3 | P0 | authority/scope、intent→dispatch→sink、cancel/quiescence、compensation/residual、irreversible/manual与组合工具 | card drafted / unseen |

## 边界

- forbidden effect在authoritative sink判定；文本、tool-call validity和proxy score不能替代commit证据。
- scope绑定subject/resource/action/parameters/time/purpose/approval/state，resolved action在dispatch前重验。
- cancel request、accepted、no-new-dispatch、quiescence、compensation与manual reconcile分别记录。
- cancellation不是rollback；补偿是可能失败的领域化forward action，最终检查residual。
- Robot Harness只有局部工程入口和proxy evidence；五项目均无protocol-complete真实sink结论。
- 本切片不生成EVAL-015，不创建或更新`coaching_state.md`。
