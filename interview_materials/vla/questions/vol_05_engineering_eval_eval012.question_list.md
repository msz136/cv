# VOL 05 Engineering / Evaluation：EVAL-012 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[OOD / Perturbation / Occlusion / Viewpoint Robustness Matrix](../knowledge/vol_05_engineering_eval_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix.html)  
> 来源冻结：[EVAL-012 Source Freeze](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval012.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-012` | L2 | P1 | target/stress envelope、factor×severity、clean pairing、visibility/solvability、per-cell/worst-cell robustness gate | card drafted / unseen |

## 边界

- OOD 是相对训练/目标分布的关系，不是 suite 名称；target、diagnostic 与 stress-only 分开。
- 同 checkpoint/task/init/controller/predicate 建 clean–perturbed pair；协议变化不解释为 robustness。
- severity 有 unit/range source/cadence/correlation；扰动须通过 render、label、visibility 与 solvability gate。
- per-cell k/n/CI、drop、retention、curve、worst target cell 和 fallback 同时报告，overall 只作辅助。
- 五项目当前均无闭合矩阵；本切片不生成 EVAL-013，不创建或更新 `coaching_state.md`。
