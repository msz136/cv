# VOL 05 Engineering / Evaluation：ENG-014 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[CUDA / MACA / ROCm 兼容性与算子验证](../knowledge/vol_05_engineering_eval_eng014.html)  
> 来源冻结：[ENG-014 Hardware / Operator Compatibility Source Freeze](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eng014.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-ENG-014` | L3 | P1 | CUDA/MACA/ROCm 六层兼容合同、算子矩阵与项目证据边界 | card drafted / unseen |

## 边界

- 题卡只考“能启动 ≠ 已兼容”：六层合同、operator matrix、同步 parity、2-rank 与 VLA parser/controller roundtrip。
- OpenPiVLA 只使用当前 local-direct eager/MACA 与 public smoke 证据，不升级性能、custom-op parity 或 benchmark claim。
- 本切片不生成 `VLA-ENG-015..016`，不创建 `coaching_state.md`。
