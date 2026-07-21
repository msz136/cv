# VOL 06 PER-011 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：typed pseudo-label、teacher noise、hard/soft与teacher-forced/free-generation、confidence/calibration、risk–coverage、selection bias、Noisy Student、curriculum、leakage与本地OPD证据边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-011 | L3 | P0 | 用teacher做pseudo-label时，confidence threshold、calibration、selection bias、curriculum和leakage怎么讲？本地OPD现在到底证明了什么？ | FixMatch/Noisy Student/calibration/curriculum/leakage固定来源与本地OPD mix/cache/train/holdout；无独立calibration/gold audit、teacher lineage、semantic/near-dup、sealed selection、exact raw/checkpoint、robot result或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 区分hard/soft target与teacher-forced/free-generation，不把token cache叫自由生成pseudo dataset。
4. 区分raw confidence、correctness、validation-fitted calibration、generation temperature和entropy logging。
5. 同时报告threshold后的coverage、accepted error、strict validity和class/route/source/domain drift。
6. Noisy Student迭代冻结teacher/candidate/filter/student/eval identity；curriculum包含ordering、schedule、intervention和counterfactual。
7. leakage分row/source/path/content/perceptual/semantic/teacher-training/preprocessing/model-selection/pseudo-feedback，不用单一boolean吞并。
8. 本地OPD只讲mix/cache/train/10k visible gate，不升级为已校准、完全无污染、因果提升、robot success或个人ownership。
9. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-011 Source Freeze](../sources/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html) 与 [PER-011 Knowledge](../knowledge/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage.html)。
- 依赖缺口：typed pseudo manifest、独立calibration labels与拟合温度T*、accepted-set gold audit、confidence-aware cache、perceptual/semantic dedup、teacher training lineage、sealed model-selection log、exact raw predictions/checkpoint hashes、matched ablation与robot trials。
- `VLA-PER-011` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只做`VLA-PER-012` segmentation/depth/keypoint/affordance source freeze，不生成knowledge/card。
