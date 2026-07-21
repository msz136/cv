# VOL 05 Engineering / Evaluation：ENG-021 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Model / Processor / Normalizer Packaging](../knowledge/vol_05_engineering_eval_eng021.html)  
> 来源冻结：[ENG-021 Model / Processor / Normalizer Packaging Source Freeze](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng021.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-021` | L2 | P0 | model/processor/normalizer/checkpoint immutable bundle、revision、shape/action round-trip 与 runtime compatibility | card drafted / unseen |

## 边界

- 题卡只考 model config/weights、processor、action schema、normalizer、ordered transforms、lineage、strict load、fixed-batch/action round-trip 和 rollback。
- OpenPiVLA 只使用 processor/collator、recipe、远端 path 的 direct/report evidence；UWM/OPD 只使用 normalizer/load metadata 与 final-only manifest 边界。
- 不把 `from_pretrained` 成功、safetensors、OpenPI 默认 `action_dim/horizon` 或远端 checkpoint path 升级为完整兼容性证明。
- 本切片不生成 `VLA-ENG-022`，不创建或更新 `coaching_state.md`。

