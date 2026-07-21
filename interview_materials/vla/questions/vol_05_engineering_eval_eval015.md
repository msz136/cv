# VOL 05 Engineering / Evaluation：EVAL-015 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-015`  
> 难度：L3 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-015 Reward / Scorer Hacking 与 Adversarial Evaluation](../knowledge/vol_05_engineering_eval_eval015_reward_scorer_hacking_adversarial_evaluation.html)；来源边界见[Source Freeze](../sources/vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)。本题不从训练reward、公开holdout、单一judge或一次scorer单测生成“没有hacking”结论。

## Reward / Scorer Hacking 与 Adversarial Evaluation

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-EVAL-015</b> · 怎样发现reward/scorer hacking，并设计adversarial evaluation？</summary>

**面试意图**：判断你能否区分reward hacking、scorer hacking、reward tampering与普通失败，把优化proxy与独立audit分开，并用预算曲线、mutation、decoy和真实state/effect构造可复算release gate。

**30 秒回答**：先把训练reward/选模scorer与locked audit分开，audit不复用数据、parser/judge。用高proxy低audit、decoy、mutation、tamper组，扫RL step或best-of-N并留全候选；报gap k/n/CI和audit曲线。critical失败hard veto，正常任务设utility floor。

**机制展开（约 2 分钟）**：我会登记每个metric是否参与gradient、选模或调参，locked audit读取独立raw state/effect并限制访问。用parser畸形、keyword stuffing、judge injection、遮挡failure、循环刷reward、提前terminal、近重复和scorer换版做paired cases；同一raw输出跑proxy、多audit和blind human裁决。若proxy随steps/N升而audit反转，先标proxy gap，再排查bug/shift与hacking机制。修复样例进regression，fresh hidden family继续验收；不以多个同源judge或单测全绿代替真实canary。

**诊断 / 证据**：检查reward/component/penalty、train/dev/audit lineage、scorer code/prompt/backend/threshold、parser/fallback、audit访问日志、candidate selection budget、全部候选而非winner、paired mutation oracle、raw simulator/robot state、human rubric/agreement、gap分母、failure triage、bridge rescore与checksums。

**项目挂钩**：Robot Harness有schema-aware reward、hard penalties和128-row restraint边界测试，但`no_forbidden_side_effect`只是forbidden-tool proxy，cancel component只查`cancel/stop`字符串，semantic scorer有backend/fallback漂移；95.6% holdout也未闭合safety。OPD等四项目没有locked budget curve，不能声称已无hacking或已观察到主动作弊。

**追问树**：reward hacking与tampering区别？高reward低success是否足以证明？hidden oracle为何仍会失效？换另一个VLM judge够吗？best-of-N怎样测overoptimization？mutation如何保证语义不变？deny-all为何不是安全解？如何防反复看holdout？scorer单测怎样做mutation testing？发现失败后为何还要fresh hidden set？

**易错点**：reward等同utility；同一parser换阈值当独立；同一judge换prompt当审计；只存winner；只看最终checkpoint；audit反复调参不降级；timeout从分母删除；scorer字段名冒充effect；hard penalty当未知漏洞证明；多个同源proxy平均；utility抵消critical事故；单测全绿外推真机。

**危险答案**：说“reward上升就学对了”“再加一个judge即可”“holdout没下降所以没有hacking”“hard penalty能彻底防hack”“sandbox 100%证明真实任务正确”“Harness已解决reward hacking”，或为任一项目编造locked audit、tampering事件与真实robot adversarial结果。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-015 知识页](../knowledge/vol_05_engineering_eval_eval015_reward_scorer_hacking_adversarial_evaluation.html)。
2. [EVAL-015 Source Freeze](../sources/vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [VOL02 / EVAL-006 / EVAL-009..011 / EVAL-014 prerequisites](../sources/vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)。
