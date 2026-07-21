# VOL 05 Engineering / Evaluation：EVAL-016 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[VLM / Human Proxy 一致性与偏差](../knowledge/vol_05_engineering_eval_eval016_vlm_human_proxy_agreement_bias.html)  
> 来源冻结：[EVAL-016 Source Freeze](../sources/vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval016.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-016` | L2 | P1 | human protocol、confusion/kappa、ordinal/rank/calibration、position/visual/temporal bias、abstention与WorldGym边界 | card drafted / unseen |

## 边界

- binary、ordinal、pairwise、ranking、probability与failure taxonomy分别选择metric。
- human需blind double-label、保留raw disagreement并独立adjudicate；majority不是无噪声gold。
- 同一VLM多票只测sampling variation；冻结snapshot/prompt/frame/parser并保存全部raw responses。
- correlation不等于absolute agreement；overall不能掩盖contact/safety/partial minority slice。
- WorldGym是公开generated-video VLM proxy；五项目无VLM×human×objective predicate成对bundle。
- 本切片不生成EVAL-017，不创建或更新`coaching_state.md`。
