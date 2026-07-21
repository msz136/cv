# VOL 04 World Model / Sim2Real：WM-018 题目清单

> 状态：`source_reviewed / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[WM-018 Prediction Horizon](../knowledge/vol_04_world_model_sim2real_wm018.html)  
> 来源审计：[WM-018 Horizon Source Freeze](../sources/vol_04_wm018_prediction_horizon_source_freeze.html) / [Diffusion Policy Audit](../sources/vol_03_diffusion_policy_claim_to_code.html) / [ACT Audit](../sources/vol_03_act_claim_to_code.html)  
> 题卡：[单张折叠题卡](vol_04_world_model_sim2real_wm018.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-WM-018` | L2 | P1 | observation/prediction/execution/replan/imagination horizon、物理时间、chunk/replan trade-off 与 matched sweep | card drafted / unseen |

## 边界

- 题卡必须区分 prediction horizon、execution prefix、replan interval 和 imagination horizon。
- Diffusion Policy、ACT、Cosmos/WAM、UWM 的公开配置只支持方法/代码合同，不替代用户项目 config、checkpoint 或 eval artifact。
- horizon A/B、per-offset error、latency、closed-loop traces 尚未完成，回答中保持 WARN。
- 本切片不生成 `VLA-WM-019..038`，不创建或更新 `coaching_state.md`。
