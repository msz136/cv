# VOL 05 Engineering / Evaluation：EVAL-011 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-011`  
> 难度：L3 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-011 Offline–Online Correlation](../knowledge/vol_05_engineering_eval_eval011_offline_online_correlation.html)；来源边界见[Source Freeze](../sources/vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)。本题不从单checkpoint、不同protocol summary或episode伪重复生成相关性。

## Offline Metric 与 Online Success 的相关性分析

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-EVAL-011</b> · 怎样验证offline metric能否预测online success？</summary>

**面试意图**：判断你能否正确选择policy-level统计单元，区分Pearson、rank/MMRV、held-out prediction与causal effect，并处理online二项噪声、task hierarchy、selection bias和项目证据边界。

**30 秒回答**：以多个matched policy/checkpoint为相关性点，不把episode当点。固定task/protocol后配对offline score与online k/n，报告Pearson、Spearman/MMRV和cluster CI，再做held-out验证。单点、混协议或同panel挑metric都不能证明proxy，更不是因果。

**机制展开（约 2 分钟）**：先建policy×task panel，绑定checkpoint、scorer、controller、predicate与raw bundle；episode只估计每格success和CI。Pearson看线性，Spearman/Kendall看rank，MMRV按online margin惩罚误排。按policy/task cluster bootstrap并做leave-one-family/task-out；discovery选metric后冻结，在held-out panel先预测再开online结果。pooled结果要防task难度的Simpson混淆。proxy只作screen，online/safety gate保留；因果需matched ablation。

**诊断 / 证据**：检查常数列、小J、窄range、outlier、ties、未知分母、policy/task伪重复、协议漂移、pooled-vs-within-task反转、selection-set复用、leave-one-point崩溃和scorer更新后关系漂移；保存panel manifest、raw两轴、scatter facets、rank violation、CI、held-out prediction与SHA。

**项目挂钩**：Robot Harness无真实robot online且n/scorer不齐；OPD只有offline checkpoint曲线；OpenPiVLA各材料lineage不匹配；WAM缺offline target且只有单episode；UWM只有单policy summary，reset差异是protocol confound。五者均不能报项目相关系数。

**追问树**：为什么episode不是相关性点？Pearson与Spearman差别？MMRV解决什么？小J怎么办？online measurement error如何处理？为什么pooled task会Simpson反转？paired bootstrap为何还不够？怎样做held-out？proxy何时失效？相关如何升级为因果？

**易错点**：单checkpoint谈相关；把episode当独立policy；不同scorer/protocol混合；只报r不画点；p值替代effect/CI；pooled task掩盖within-task；试很多metric后挑最高；offline选择和验证复用；相关称因果；proxy替代safety/online gate。

**危险答案**：说“loss与success都下降所以强相关”“1000个offline样本足够算相关”“Pearson高说明排序和校准都好”“Spearman高就可替代真机”“UWM strict/reset是两个policy点”或为五项目编造`r/ρ`。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-011 知识页](../knowledge/vol_05_engineering_eval_eval011_offline_online_correlation.html)。
2. [EVAL-011 Source Freeze](../sources/vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与[Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [VOL 04 WM-040/041](../knowledge/vol_04_world_model_sim2real.html)。
