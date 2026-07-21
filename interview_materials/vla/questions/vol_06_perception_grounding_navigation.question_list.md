# VOL 06 Perception / Grounding / Navigation：整卷题目清单

> 冻结日期：2026-07-19  
> 状态：`phase_0_frozen / planned_20 / sources_18 / knowledge_18 / cards_18 / per018_independent_fact_reviewed / missing_sources_2 / missing_knowledge_2 / missing_cards_2 / WARN`  
> 计数边界：本清单中的 `planned` ID 不计入已生成题卡；只有出现 canonical question Markdown 中的 `<details class="qa">` 后才计入全局题库。  
> 来源审计：[VOL 06 Coverage-Gap Audit](../sources/vol_06_perception_grounding_navigation_coverage_gap_audit.html)。

## 1. 范围与优先级

VOL 06 固定为 20 个原子节点：12 个 P0、8 个 P1。现有 `VLA-PER-001..005` 保留，不重编号、不重复生成；`006..020` 先进入 source queue，再按 source → knowledge → card 顺序逐个闭环。

| ID | 主题 | 难度 / 优先级 | 前置 | 当前状态 |
| --- | --- | --- | --- | --- |
| `VLA-PER-001` | Point / Box / Text Grounding 与坐标协议 | L2 / P0 | VOL 01 坐标、VOL 03 action contract | source + knowledge + card / unseen |
| `VLA-PER-002` | 2D→3D Lift、Calibration、Depth、Frame 与 TF | L3 / P0 | PER-001 | source + knowledge + card / unseen |
| `VLA-PER-003` | Multi-view / Temporal Schema、Fusion 与 Observation Age | L3 / P0 | PER-001/002 | source + knowledge + card / unseen |
| `VLA-PER-004` | VLN / ObjectNav / REVERIE Task 与 Metric Contract | L2 / P0 | PER-001..003 | source + knowledge + card / unseen |
| `VLA-PER-005` | Navigation Policy、Semantic Map、Waypoint 与 Controller | L3 / P0 | PER-003/004 | source + knowledge + card / unseen |
| `VLA-PER-006` | Image Preprocess、Resize/Crop/Letterbox、Patch Token 与 Camera Identity | L2 / P0 | VOL 01 Transformer | source + knowledge + card / unseen |
| `VLA-PER-007` | Open-vocabulary Detection / Grounding Pipeline 与 Text–Region Matching | L2 / P0 | PER-006 | source + knowledge + card / unseen |
| `VLA-PER-008` | Point / Box / Mask / Keypoint / Affordance 表示选择 | L2 / P0 | PER-001/007 | source + knowledge + card / unseen |
| `VLA-PER-009` | Grounding Training Objective、Matching、Negative 与 Loss Reduction | L3 / P1 | PER-007/008、VOL 01 loss | source + knowledge + card / unseen |
| `VLA-PER-010` | Grounding Metric、Strict Parser、IoU/PCK/Recall 与 Protocol Comparability | L2 / P0 | PER-001/008 | source + knowledge + card / unseen |
| `VLA-PER-011` | Pseudo-label / Teacher Noise、Confidence Calibration、Leakage 与 Curriculum | L3 / P0 | PER-009/010、VOL 02 IL | source + knowledge + card / unseen |
| `VLA-PER-012` | Segmentation、Depth、Keypoint 与 Manipulation Affordance | L3 / P1 | PER-002/008 | source + knowledge + card / unseen |
| `VLA-PER-013` | Point Cloud、Voxel / BEV / Occupancy 表示与 Sampling | L3 / P1 | PER-002/003 | source + knowledge + card / unseen |
| `VLA-PER-014` | 3D Grounding、Spatial Relation 与 Open-vocabulary 3D Scene | L3 / P1 | PER-007/013 | source + knowledge + card / unseen |
| `VLA-PER-015` | Perception→Action Interface、Reachability、Uncertainty 与 Failure Gate | L3 / P0 | PER-002/008/014、VOL 03 action | source + knowledge + card / unseen |
| `VLA-PER-016` | Localization / Odometry / SLAM、Map Frame 与 Drift | L3 / P1 | PER-002/003 | source + knowledge + card / unseen |
| `VLA-PER-017` | POMDP Memory、Belief、Frontier 与 Active Exploration | L3 / P1 | PER-005/016 | source + knowledge + card / unseen |
| `VLA-PER-018` | VLN/ObjectNav Training：BC/DAgger/RL、Teacher Forcing 与 Exposure Bias | L3 / P1 | PER-004/005、VOL 02 | source + knowledge + card + independent fact review / unseen |
| `VLA-PER-019` | Navigation Evaluation、Collision/Stop、Confidence Interval 与 Failure Taxonomy | L2 / P0 | PER-004/005、VOL 05 eval | source + knowledge + card / unseen |
| `VLA-PER-020` | Occlusion、Sensor Noise、Domain Shift、Sim2Real 与 Safety Fallback | L3 / P1 | PER-003/015/019、VOL 04 | source + knowledge + card / unseen |

## 2. 四个学习簇

| 学习簇 | Stable IDs | 面试出口 |
| --- | --- | --- |
| 输入与 2D grounding | `001,006..012` | 能从 image transform/token 讲到 region/point/mask 输出、训练 loss、parser 与 metric，不把静态 grounding 升级为 action success |
| 3D、多视角与动作接口 | `002,003,013..015` | 能说明 calibration/frame/time/uncertainty 如何进入 3D representation 和 reachable action target |
| 导航任务、地图与训练 | `004,005,016..018` | 能冻结 task/episode/action/stop，比较 map-free/map-based/waypoint，并解释 memory、SLAM 与 IL/RL 训练边界 |
| 评估、鲁棒性与安全 | `019,020` | 能给出 protocol、denominator、置信区间、failure trace、domain gap 与 fallback，不虚构本地导航结果 |

## 3. 出卷纪律

1. 每次只推进一个 planned ID 的 source-freeze，完成审查后再写 knowledge 和单张 card。
2. 全局题库现为276；`PER-001..020` source/knowledge/card已同步且unseen。
3. VOL 06 页面覆盖已达20/20/20；下一bounded slice只做真实口述或独立fact review，不预先修改mastery。
4. 新卡沿用 stable ID、短答、机制展开、来源、项目挂钩、易错点、追问和练习状态字段。
5. OPD、Robot Harness、OpenPiVLA、WAM、UWM 只能作为有证据的 interface hook；当前没有 personal VLN/ObjectNav result。
6. 真实口述发生前，二十张卡保持 `unseen`，不得创建 `coaching_state.md`。
