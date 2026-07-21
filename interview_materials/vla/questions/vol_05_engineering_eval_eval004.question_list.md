# VOL 05 Engineering / Evaluation：EVAL-004 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Paired Init / Seed Evaluation 与显著性](../knowledge/vol_05_engineering_eval_eval004_paired_init_seed_significance.html)  
> 来源冻结：[EVAL-004 Source Freeze](../sources/vol_05_eval004_paired_init_seed_significance_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval004.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-004` | L3 | P0 | pairing key、discordant table、exact McNemar、paired resampling、seed hierarchy、power 与 multiplicity | card drafted / unseen |

## 边界

- pair 必须共享 task、init snapshot/hash 和 protocol；same seed 本身不构成 same init 证据。
- exact McNemar 只看 `n10+n01`；同时报告四格表、effect、paired CI、p-value 与 practical threshold。
- SciPy paired assignment 用 `permutation_type="samples"`；bootstrap 用 `paired=True` 和同一组 resampled indices。
- training seed 是更高层 replicate；frame、同 episode step、重复 rollout 或 row 不能展开成 iid。
- UWM 两个不同协议 aggregate、OpenPiVLA 97.4% 与 OPD 10k 不构成本地 paired rollout result。
- 本切片不生成 EVAL-005，不创建或更新 `coaching_state.md`；下一内容节点固定为 EVAL-005 aggregation。

