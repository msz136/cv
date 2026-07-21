# VOL 05 Engineering / Evaluation：ENG-015 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Activation Checkpointing、CPU/NVMe Offload 与吞吐](../knowledge/vol_05_engineering_eval_eng015.html)  
> 来源冻结：[ENG-015 Source Freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng015.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-015` | L2 | P1 | activation checkpointing、FSDP CPU offload、ZeRO CPU/NVMe offload 与 matched A/B/resume | card drafted / unseen |

## 边界

- 题卡只考 activation 与 model-state offload 的机制差异、显存/吞吐 trade-off、matched A/B 和 fixed-next-batch resume。
- UWM/OPD 只使用 ENG-004..006 artifact gate 的配置、summary、load report 和 final-only manifest；不升级为 NVMe benchmark、吞吐提升或完整 resume。
- 本切片不生成 `VLA-ENG-016`，不创建或更新 `coaching_state.md`。

