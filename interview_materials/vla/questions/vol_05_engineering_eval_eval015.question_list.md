# VOL 05 Engineering / Evaluation：EVAL-015 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Reward / Scorer Hacking 与 Adversarial Evaluation](../knowledge/vol_05_engineering_eval_eval015_reward_scorer_hacking_adversarial_evaluation.html)  
> 来源冻结：[EVAL-015 Source Freeze](../sources/vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval015.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-015` | L3 | P0 | reward/scorer/tampering边界、independent audit、proxy gap、optimizer-budget curve、mutation/decoy与release gate | card drafted / unseen |

## 边界

- reward、公开scorer与learned judge均是proxy；audit必须在data/signal/implementation/access上声明独立性。
- 高proxy低audit先标proxy gap；排除label、logging、environment和protocol bug后再归因hacking机制。
- sweep RL steps、best-of-N、checkpoint/prompt search，并保存全部候选和locked audit曲线。
- parser、semantic judge、reward input、trajectory、selection、contamination与version mutation进入adversarial matrix。
- Robot Harness有reward/scorer源码与窄边界测试，但无真实effect/locked audit结论；其他四项目也无budget curve。
- 本切片不生成EVAL-016，不创建或更新`coaching_state.md`。
