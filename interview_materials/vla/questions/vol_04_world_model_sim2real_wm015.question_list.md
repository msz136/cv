# VOL 04 World Model / Sim2Real：WM-015 题目清单

> 状态：`source_reviewed / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[UWM Video–Action Coupling](../knowledge/vol_04_world_model_sim2real_wm015.html)  
> 来源审计：[UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html) / [独立事实复核](../sources/vol_04_uwm_independent_fact_review.html)  
> 题卡：[单张折叠题卡](vol_04_world_model_sim2real_wm015.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-WM-015` | L3 | P0 | robot/action-free tuple、共享 DiT、双 timestep、sampling mode、action-mask/loss 边界 | card drafted / unseen |

## 边界

- 题卡只考 frozen upstream UWM 的 method/code contract，不绑定用户 UWM 74.4%/92.8%、checkpoint provenance 或个人原创。
- `action_mask` 只改变 action timestep；当前 action MSE 未显式 sample mask，不能说 action-free video 没有 action gradient。
- action/image MSE 是 conditional proxy，不能替代 strict closed-loop success。
- 本切片不生成 `VLA-WM-016..038`，不创建或更新 `coaching_state.md`。

