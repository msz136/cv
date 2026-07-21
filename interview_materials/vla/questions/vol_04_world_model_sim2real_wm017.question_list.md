# VOL 04 World Model / Sim2Real：WM-017 题目清单

> 状态：`source_reviewed / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[WM-017 Heterogeneous Embodiment Schema](../knowledge/vol_04_world_model_sim2real_wm017.html)  
> 来源审计：[WM-017 Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html) / [Open X frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md) / [UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)  
> 题卡：[单张折叠题卡](vol_04_world_model_sim2real_wm017.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-WM-017` | L3 | P1 | RLDS/container、camera/state/action semantics、timestamp、horizon、presence/valid mask、normalizer 与 per-embodiment loss | card drafted / unseen |

## 边界

- 题卡只考跨 embodiment schema 与 world-loss audit，不把不同项目的 action/camera 语义强行合并。
- 公开 Open X README 支持容器和 RT-1-X 示例边界，不证明用户本地已完成统一转换或跨机器人结果。
- adapter manifest、round-trip、terminal-mask A/B 和 per-embodiment eval 尚未完成，回答中保持 WARN。
- 本切片不生成 `VLA-WM-018..038`，不创建或更新 `coaching_state.md`。
