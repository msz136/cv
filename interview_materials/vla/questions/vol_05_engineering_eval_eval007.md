# VOL 05 Engineering / Evaluation：EVAL-007 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-007`  
> 难度：L3 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-007 Coverage / Difficulty](../knowledge/vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)；来源边界见[Source Freeze](../sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)。本题不把总count、suite summary或training data mix包装成task/init/seed coverage。

## Init / Seed / Task Coverage 与难度分层

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-EVAL-007</b> · 怎样设计init、seed、task coverage和difficulty stratification，避免“跑得多但覆盖窄”？</summary>

**面试意图**：判断你能否把count、unique support、coverage、representativeness分开，设计task×difficulty×init×training-seed cube，并处理allocation、oversampling、difficulty leakage与cluster uncertainty。

**30 秒回答**：先冻结task×difficulty×init×training-seed cells、weights和minimum，记录valid/unique init；区分training/env/rollout seed，用snapshot核验init。hard/rare可过采样，按weights重算；difficulty不得由candidate failure事后定义。

**机制展开（约 2 分钟）**：coverage不是success；报告Cw=ΣWh·1[nh≥mh]和per-cell k/n/CI。task按registry、family和deployment risk分层；init保留snapshot与pose/contact metadata；training seed走共同grid，rollout repeats不替代runs/inits。allocation可用proportional、equal/minimum，或基于独立pilot的Neyman；过采样后按target weights重算。difficulty用candidate-independent features或disjoint pilot的frozen baseline定bins；事后slice仅作exploratory。

**诊断 / 证据**：检查registry/protocol hash、cell weights和minimum、training/env/rollout/resampling seed、init snapshot/unique cluster、task family、difficulty schema/bin edges、planned/attempted/valid/exclusion与weight coverage。测试same-seed different-init、duplicate init、empty/critical cells、seed×task confound、oversampled hard cells、candidate-defined bins和train/final overlap。

**项目挂钩**：UWM 5×50缺raw unique-init/training-seed cube；WAM只有CoffeePressButton episode0 diagnostic；OpenPiVLA四suite summary缺per-task/init/seed；OPD 10k有8,251 unique images和format/pool quota但不代表deployment；Robot Harness browser是format-only，training task mix不等于execution coverage。

**追问树**：250次为何不等于250个init？四类seed覆盖什么？task count为何不够？difficulty如何防leakage？equal/proportional/Neyman怎么选？rare/hard过采样后怎样估总体？coverage score与success差别？缺critical cell怎么办？train/test generator seeds如何隔离？五项目当前coverage各到哪层？

**易错点**：总n代替coverage；seed整数代替actual state；重复rollout/image当unique support；单training run冒充seed coverage；按candidate失败定义hard；过采样后直接micro；各模型不同grid；空格静默删除；training mix当deployment/eval weights。

**危险答案**：说“每task 50次就够”“seed不重复就覆盖充分”“hard case就是模型失败的case”“多跑困难任务后直接算overall”“10k rows代表10k独立场景”或“一个training seed加很多rollout等于多seed”。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-007 知识页](../knowledge/vol_05_engineering_eval_eval007_coverage_difficulty_stratification.html)：coverage cube、difficulty、allocation、uncertainty与项目映射。
2. [EVAL-007 Source Freeze](../sources/vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)：Neyman、Procgen、rliable、LIBERO frozen sources与五项目边界。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
