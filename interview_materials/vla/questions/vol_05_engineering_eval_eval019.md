# VOL 05 Engineering / Evaluation：EVAL-019 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-019`  
> 难度：L2 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-019 Checkpoint Selection / Pareto / Holdout Overfit](../knowledge/vol_05_engineering_eval_eval019_checkpoint_selection_pareto_holdout_overfit.html)；来源边界见[Source Freeze](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)。本题不把per-metric best、反复查询holdout或不同lineage结果拼成唯一最佳checkpoint。

## Checkpoint Selection、Pareto Frontier 与 Holdout Overfit

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-019</b> · 多个checkpoint怎样用Pareto frontier选择并避免holdout overfit？</summary>

**面试意图**：判断你能否区分development selection与final audit，解释winner's curse、hard-feasible set、Pareto dominance、uncertainty和真实bundle决策，并审计test访问历史。

**30 秒回答**：先冻结candidate、metric角色、hard gate和selection rule；只在dev上筛选，先去掉安全/延迟不合格，再按多目标Pareto保留不支配点，并按预注册lexicographic或权重选一个真实bundle。锁定SHA后只在fresh audit评一次；若按audit回改，它就不再是test。

**机制展开（约 2 分钟）**：validation best是在含噪估计上取max，候选/查询越多越易winner's curse。每个checkpoint绑定完整bundle与同scorer metric vector；critical safety先形成feasible set。Pareto只保留不可支配trade-off，不给唯一winner，仍需冻结constraint、margin、normalization和tie-break；paired/cluster CI不足就标UNRESOLVED。early-stop、best seed、改threshold、看失败视频都算selection。dev选完锁bundle，final audit只测该bundle；回改就开新cycle和fresh holdout。

**诊断 / 证据**：检查candidate/parent/bundle SHA、step/tokens/cadence、metric-role registry、scorer/prompt/parser SHA、dev pair IDs、hard-gate matrix、per-task/macro/worst/safety/latency/cost向量、paired CI与margins、dominance graph、Pareto set、decision weights/tie-break、selected bundle lock、holdout access/submission log、fresh audit pair lock、raw audit和selection-vs-audit gap。

**项目挂钩**：OPD的ckpt2000/3000/4000/5000各在不同pool/metric占优，只说明trade-off，不能认证ckpt5000全局最优；Harness的ckpt100/200主分近似但safety均值不同，缺raw CI与预注册rule。OpenPiVLA多lineage，WAM/UWM缺candidate/selection/audit链。

**追问树**：validation best为何偏高？候选数和cadence影响什么？test看失败视频算访问吗？hard gate与objective区别？Pareto上哪个最好？能否每列拿不同checkpoint？权重何时定？CI overlap怎么处理？best seed能否代表方法？nested eval是什么？audit失败后怎么办？OPD ckpt5000能否叫best？

**易错点**：test选epoch；best seed；per-column cherry-pick；不同scorer进同frontier；overall洗安全；只看mean无CI；frontier当winner；看结果后改权重；candidate creep；删OOM/invalid；重复leaderboard；audit回改仍称final；把不同lineage拼成曲线；offline frontier直接授权真机。

**危险答案**：说“test上最高就是最终模型”“Pareto会自动选唯一最好”“每个指标拿各自最佳checkpoint即可”“只要不看label就能无限看分数”“ckpt5000所有能力都最佳”“Harness ckpt100已显著支配ckpt200”，或编造五项目fresh holdout与selection ledger。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-019 知识页](../knowledge/vol_05_engineering_eval_eval019_checkpoint_selection_pareto_holdout_overfit.html)。
2. [EVAL-019 Source Freeze](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)。
3. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [EVAL-010 / EVAL-011 / EVAL-015 / EVAL-018 prerequisites](../sources/vol_05_eval019_checkpoint_selection_pareto_holdout_overfit_source_freeze.html)。
