# VOL 05 Engineering / Evaluation：EVAL-020 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-020`  
> 难度：L2 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-020 Incident Timeline / Root Cause / Bug-fix Verification](../knowledge/vol_05_engineering_eval_eval020_incident_timeline_root_cause_bugfix_verification.html)；来源边界见[Source Freeze](../sources/vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)。本题不把时间先后、rollback、first bad commit或单次rerun升级为confirmed root cause。

## Incident Timeline、Root Cause 与 Bug-fix Verification

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-EVAL-020</b> · VLA事故怎样定位root cause并证明bug fix有效？</summary>

**面试意图**：判断你能否从impact和不可变现场推进到clock-aware timeline、first divergence、可证伪RCA与same-protocol verification，并区分mitigation、recovery、fix和prevention。

**30 秒回答**：先冻结incident bundle、影响范围和时钟来源，对齐known-good/bad找到first verified divergence；用可证伪hypothesis和最小干预定位机制。修复后在同输入同协议上做red→green，同时跑未受影响controls、fresh邻近case和多次/多seed复验；rollback或一次通过只算弱证据。

**机制展开（约 2 分钟）**：timeline绑定事件/观测时间、clock误差、bundle SHA与raw evidence，日志顺序不是因果。first divergence只是最早可见分叉；root cause还需复现、targeted intervention和替代解释控制。`git bisect`仅在稳定oracle、可构建且近似单调时定位first bad。verification锁data/seed与runtime/scorer bundle，只改target patch；incident replay红转绿、unaffected仍绿、fresh neighbors也绿，并报告paired effect和flakiness。RECOVERED≠FIXED≠PREVENTED。

**诊断 / 证据**：incident/impact manifest、raw log/trace/video、clock sync与timeline、good/bad bundle diff、first-divergence record、failure predicate、minimal reproducer、hypothesis/bisect ledger、fix patch manifest、exact before/after pairs、unaffected controls、fresh/stress cases、multi-seed/cluster CI、rollback/recovery log、action-item owner/deadline/test与checksums。

**项目挂钩**：OPD裸point格式与strict parser不一致，protocol-fixed后format/Hit@100恢复，是狭窄协议层red→green，不能外推模型整体能力。UWM的DataLoader p95 wait约`13.86s→0.19s`是子系统A/B，不是完整训练吞吐RCA。WAM/OpenPiVLA/Harness均缺matched fix闭环。

**追问树**：impact怎样界定？最早告警与first divergence区别？rollback为何不等于root cause？human error为何不是终点？bisect何时失效？一次通过为何不够？same protocol锁什么？controls/fresh cases各防什么？flaky怎么验？无法复现怎么办？OPD能说修复模型能力吗？

**易错点**：last-change bias；日志行号当时间；症状当原因；rollback当fix；first bad commit当机制；一次green；before/after换scorer或support；只测事故样本；删invalid；重跑到通过；human error终止；action item无owner/test；recovered=fixed；把子系统smoke外推端到端。

**危险答案**：说“最后commit就是根因”“rollback恢复说明bug已修好”“bisect能自动证明因果”“跑一次过了就可以关事故”“OPD证明point能力整体提升”“UWM已解决完整GPU吞吐”，或编造五项目完整incident timeline、multi-seed fix与预防gate。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-020 知识页](../knowledge/vol_05_engineering_eval_eval020_incident_timeline_root_cause_bugfix_verification.html)。
2. [EVAL-020 Source Freeze](../sources/vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)。
3. [Google SRE Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)。
4. [NIST SP 800-61r3](https://doi.org/10.6028/NIST.SP.800-61r3)。
5. [`git bisect` official docs](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-bisect.adoc)。
6. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [Robot Harness / OpenPiVLA / WAM inventories](../evidence/evidence_manifest.html)。
