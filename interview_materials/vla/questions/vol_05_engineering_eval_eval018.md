# VOL 05 Engineering / Evaluation：EVAL-018 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-018`  
> 难度：L3 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-018 Factorial Ablation / Matched Baseline / Causal Boundary](../knowledge/vol_05_engineering_eval_eval018_factorial_ablation_matched_baseline_causal_boundary.html)；来源边界见[Source Freeze](../sources/vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)。本题不从两个best数字、单seed、不同scorer或组合路线生成单组件因果提升。

## Factorial Ablation、Matched Baseline 与因果边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-EVAL-018</b> · VLA加入多个模块后，怎样设计可归因的factorial ablation？</summary>

**面试意图**：判断你能否把bundle差异拆成factor/estimand/cells，区分main effect与interaction，控制seed/data/compute/tuning/selection/scorer，并把因果结论限制在冻结protocol内。

**30 秒回答**：先定义factor、outcome与estimand，再跑baseline、A、B、A+B完整cells。各cell匹配base、data、预算、调参、selection与scorer；跨training seeds区组并复用同eval pairs。报告cell均值、主效应、interaction与CI，失败run不删；因果只到冻结support。

**机制展开（约 2 分钟）**：两因素用四cell估计`τA`、`τB`及`τAB=μ11-μ10-μ01+μ00`，A+B最好不代表A、B各自有效。先分fixed-recipe机制effect与equal-search-budget系统effect；training/data随机性做block/randomization，episode只做层次内评估。planned→valid/failed守恒，checkpoint只由共同validation规则选。只有factor实现一致、assignment可交换、各block有完整arms、run间无污染且missingness闭合，才在该model/data/budget/task/scorer support内说因果。

**诊断 / 证据**：检查preregistration、factor semantic diff、base/checkpoint/processor/normalizer SHA、design matrix、data mix/tokens、steps/FLOPs/GPU-hours、search trials、training/data/env/rollout seeds、planned/failed registry、selection rule、eval pair IDs、scorer SHA、cell×seed×task raw table、main/simple/interaction effects、CI、multiplicity、deviation与fresh holdout。

**项目挂钩**：UWM的0.744/0.928是不同init protocol；WAM四臂未执行；OpenPiVLA archived flow与formal causal-CE非同lineage；Harness base/SFT/GRPO的n/scorer不同；OPD缺SFT-only、single-teacher、no-synthetic/route ablation。五项目都不能升级单组件因果。

**追问树**：为何A00/A11不够？main与simple effect区别？interaction在哪个scale？同seed为何不够？episode多能否替代training seeds？same steps是否公平？baseline要不要调参？OOM seed怎么办？best checkpoint怎样选？fractional factorial何时可用？满足什么条件才说因果？能否外推真机？

**易错点**：factor名不绑定实现；一次改data/head/loss；只比两个best；单seed；episode伪重复；candidate多调参；同epoch冒充同tokens；忽略compute/capacity；删OOM/NaN；baseline last对candidate best；test选checkpoint；A11最好即各组件有效；只报p值；fractional alias不声明；protocol内effect外推所有VLA。

**危险答案**：说“删掉模块掉点就证明模块有效”“固定seed即可排除随机性”“1000 episodes等于1000次独立实验”“A+B最高所以A和B都有贡献”“只保留成功训练的seed”“candidate调参而baseline默认也公平”，或把UWM/WAM/OpenPiVLA/Harness/OPD现有组合数字编造成matched ablation。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-018 知识页](../knowledge/vol_05_engineering_eval_eval018_factorial_ablation_matched_baseline_causal_boundary.html)。
2. [EVAL-018 Source Freeze](../sources/vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)。
3. [VOL 04 WM-041 Factorial Ablation](../knowledge/vol_04_world_model_sim2real.html)。
4. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
5. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
8. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
