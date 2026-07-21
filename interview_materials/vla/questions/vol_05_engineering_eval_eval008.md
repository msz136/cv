# VOL 05 Engineering / Evaluation：EVAL-008 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-008`  
> 难度：L2 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-008 Failure Taxonomy](../knowledge/vol_05_engineering_eval_eval008_failure_taxonomy_recovery.html)；来源边界见[Source Freeze](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)。本题不把失败截图、VLM解释、单episode或低task score包装成root cause。

## Perception / Action / Controller / Recovery Failure Taxonomy

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-008</b> · rollout失败后，怎样区分perception、action、controller与recovery failure？</summary>

**面试意图**：判断你能否区分failure effect/mode/cause，沿系统链找first verified divergence，用matched intervention定位perception/action-interface/controller，并正确评估detector与recovery。

**30 秒回答**：先验协议，沿obs→estimate→policy→transform→controller→state→recovery找最早证实偏差。effect/mode/cause分开：感知查raw→estimate，action做roundtrip，控制查command→state，恢复查miss/false alarm、延迟与outcome；不足标unknown。

**机制展开（约 2 分钟）**：success=false不是cause。verified state替换estimate定位perception；verified input查proposal定位policy；decode/denorm/frame roundtrip隔离interface；command replay配tracking/error trace定位controller。detector报precision/recall/delay/false alarm；recovery分eligible、triggered、recovered、post-task success与unsafe outcome。primary取最早verified偏差；确认cause需复现、matched intervention、fix和协议rerun。

**诊断 / 证据**：最小ledger含episode/protocol SHA、first symptom/detection time、raw obs/timestamp、estimate、policy I/O、decoded action、controller command/executed state、predicate、effect/mode/cause confidence、alarm、recovery action与outcome。测试verified-state替换、sentinel action roundtrip、identical-command replay、miss/false-alarm、late trigger、recovery oscillation和invalid reset/scorer。

**项目挂钩**：WAM只有一条双侧失败trace，不能确认gripper根因；OpenPiVLA `D=72` vs `limit=16`只是interface risk；OPD point strict=0先拆parser与geometry；Robot Harness只有orchestration compensation contract；UWM task summary缺first-divergence trace。

**追问树**：effect/mode/cause区别？first symptom为何不等于root cause？感知替换实验怎么做？policy与denorm错误怎么分？controller trace存什么？erratic/no-progress为何需不同detector？VLM解释能否当cause？recovery denominator是什么？fallback为何失效？五项目各能讲到哪层？

**易错点**：失败都归模型；抓取失败都归gripper；VLM explanation当ground truth；first visible symptom当first divergence；parser failure当perception差；smooth action当正常；只测失败样本；只报triggered recoveries；配置fallback就说恢复成功；缺日志仍强制单标签。

**危险答案**：说“看视频就能判断根因”“success=false说明action model错”“point strict=0说明看不懂点”“controller收到命令就代表执行正确”“恢复成功率只算触发的case”或“一个episode修好就确认root cause”。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-008 知识页](../knowledge/vol_05_engineering_eval_eval008_failure_taxonomy_recovery.html)。
2. [EVAL-008 Source Freeze](../sources/vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
