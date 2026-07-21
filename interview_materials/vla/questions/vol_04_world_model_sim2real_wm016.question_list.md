# VOL 04 World Model / Sim2Real：WM-016 题目清单

> 状态：`source_reviewed / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[WM-016 Joint Objective](../knowledge/vol_04_world_model_sim2real_wm016.html)  
> 来源审计：[WM-016 Source Freeze](../sources/vol_04_wm016_joint_objective_source_freeze.html) / [UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html) / [Cosmos/WAM Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)  
> 题卡：[单张折叠题卡](vol_04_world_model_sim2real_wm016.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-WM-016` | L3 | P1 | shared representation、condition mask、sample routing、prediction target、noise schedule、target loss mask、reduction 与 paired ablation | card drafted / unseen |

## 边界

- 题卡只考 frozen UWM/Cosmos/WAM source contract 与审计方法，不把两个上游实现拼成一个模型。
- `condition mask`、`sample routing`、`prediction target` 和 `target loss mask` 必须分别解释；不能凭变量名推断 loss 已排除。
- paired ablation、runtime gradient、checkpoint lineage 和 closed-loop success 尚未完成，回答中保持 WARN。
- 本切片不生成 `VLA-WM-017..038`，不创建或更新 `coaching_state.md`。
