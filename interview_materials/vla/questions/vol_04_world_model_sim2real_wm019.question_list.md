# VOL 04 World Model / Sim2Real：WM-019 题目清单

> 状态：`source_reviewed / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)  
> 来源审计：[WM-019 Metric Source Freeze](../sources/vol_04_wm019_metric_boundary_source_freeze.html) / [World Model Foundations Audit](../sources/vol_04_world_model_foundations_claim_to_code.html) / [UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html) / [Benchmark Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)  
> 题卡：[单张折叠题卡](vol_04_world_model_sim2real_wm019.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-WM-019` | L2 | P0 | PSNR/SSIM/FVD、latent/action MSE、teacher-forced/open-loop、proxy/simulator/real success 的 metric ladder、统计单位与 protocol contract | card drafted / unseen |

## 边界

- 题卡必须区分视觉/latent/action proxy、open-loop 稳定性线索、world-model proxy、simulator episode success 与 real closed-loop success。
- 所有比较必须说明 target、mask、normalizer、reduction、checkpoint、schema、horizon/replan、reset/init、controller、seed、scorer/predicate 和 denominator。
- frame、step、raw row、box/point/text pool 不能自动当作 episode-level Bernoulli；项目数字没有 checkpoint、脚本、trace 和分母时保持 WARN。
- 本切片只生成一张 WM-019 题卡；WM-020..038 继续后置，不创建或更新 `coaching_state.md`。
