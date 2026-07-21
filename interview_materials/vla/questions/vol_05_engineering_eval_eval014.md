# VOL 05 Engineering / Evaluation：EVAL-014 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-014`  
> 难度：L3 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-014 Forbidden Side Effect / Scope / Cancel / Compensation](../knowledge/vol_05_engineering_eval_eval014_forbidden_side_effect_scope_cancel_compensation.html)；来源边界见[Source Freeze](../sources/vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)。本题不从文本安全、tool-call格式、timeout或cancel acknowledgement生成真实side-effect安全结论。

## Forbidden Side Effect、Scope 与取消补偿

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-EVAL-014</b> · 怎样评估 forbidden side effect、scope、取消与补偿？</summary>

**面试意图**：判断你能否把intent、authorization、dispatch、sink commit分层，定义完整scope与cancel/quiescence状态机，并识别compensation、不可逆点、重试和组合工具风险。

**30 秒回答**：我会在真实effect sink判forbidden commit，逐层记录intent、授权、dispatch与状态差；scope绑定人、机器人/资源、工具、参数、时效、审批和版本。取消要测accepted、停止新派发、静止时间及残留；已提交effect另做幂等补偿或人工处置，不能把cancel当rollback。

**机制展开（约 2 分钟）**：先预注册allowed/forbidden case、初始状态与sink oracle，dispatch前对resolved tool/resource/parameters逐请求重验，缺字段默认deny。按cancel before dispatch、during execution、after commit注入，量post-cancel effect和quiescence；以operation key/state version补偿，记录残留、失败与不可逆审批。报告false allow/deny、forbidden commit k/n/CI、重复effect、补偿结果和正常任务utility；critical commit是hard veto，proxy/sim不替代真实sink。

**诊断 / 证据**：检查requested与granted scope、policy/version、resource binding、parameter normalization、approval expiry、auth→dispatch是否可连接、alias/nested/background executor、late/duplicate/out-of-order请求、cancel接受与最后effect时间、before/committed/post-compensation snapshot、补偿幂等key、manual owner和checksum复算。

**项目挂钩**：Robot Harness有scope/robot绑定、allowlist、cancel检查、timeout、lock cleanup和best-effort stop/cancel，但safety suite仍是tool/scope proxy，`RH-CL-009`为FAIL；不能声称全量越权阻断、零残留或真机认证。OPD、OpenPiVLA、WAM、UWM均无完整真实sink/cancel/compensation证据。

**追问树**：scope字符串为何不够？OAuth scope能证明逐请求授权吗？cancel accepted与CANCELED/quiescent差别？timeout等于cancel吗？stop和rollback区别？补偿为何不是逆序undo？point of no return怎么处理？allowed tools为何组合后仍危险？retry怎样避免重复effect？deny-all为何不合格？proxy到真机怎样升级？

**易错点**：模型文本当sink；tool call合法当授权正确；只查tool name不查resource/parameter；token有效当请求获准；cancel 200当静止；timeout后不查后台work；stop当状态恢复；补偿成功不验residual；从分母删除timeout；用utility抵消critical事故；sandbox 100%外推真机。

**危险答案**：说“没有危险回复所以安全”“allowlist足够”“cancel接口成功就不会继续执行”“补偿就是把动作反着做”“安全reward高能抵消少量事故”“Harness sandbox 100%证明真机不会越权”，或为五项目编造forbidden commit率与补偿成功率。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-014 知识页](../knowledge/vol_05_engineering_eval_eval014_forbidden_side_effect_scope_cancel_compensation.html)。
2. [EVAL-014 Source Freeze](../sources/vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [ENG-018 / ENG-020 / ENG-022 / WM-038 / EVAL-009 / EVAL-010 prerequisites](../sources/vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)。
