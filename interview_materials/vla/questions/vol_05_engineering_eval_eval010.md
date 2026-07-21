# VOL 05 Engineering / Evaluation：EVAL-010 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-010`  
> 难度：L2 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-010 Regression / Golden / Canary](../knowledge/vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)；来源边界见[Source Freeze](../sources/vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)。本题不把checkpoint曲线、smoke或summary包装成已落地release system。

## Regression Gate、Golden Set 与 Canary Rollout

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-010</b> · 怎样用golden set、regression gate和canary发布VLA新checkpoint？</summary>

**面试意图**：判断你能否区分固定判题集合、预注册离线否决规则与有限live exposure，并把critical slice、safety、latency、missing、abort和rollback写成release合同。

**30 秒回答**：先冻结golden case、expected/invariant、slice和协议，让模型逐case配对；schema/safety先hard veto，再对critical指标做预注册non-inferiority。通过后先shadow无执行权，再小范围canary；到最小暴露和决策窗才扩量，越界立即abort并回滚known-good bundle。

**机制展开（约 2 分钟）**：golden与train/dev分开，失败后不能删case或改margin。两侧绑定同checkpoint/processor/normalizer/protocol/scorer与raw bundle，算paired delta；overall、per-task、critical、safety、latency分别判，missing/invalid/协议漂移fail closed。shadow只比较live输出不执行；canary冻结task/init/robot或traffic、authority、window、guardrail。decision记录证据与SHA，rollback恢复known-good整套artifact。通过只覆盖已暴露support，不是安全认证。

**诊断 / 证据**：注入wrong shape/unit、NaN、forbidden action、missing/crash、scorer漂移、critical regression、latency deadline miss、shadow drift、canary timeout和rollback failure；保存golden/gate/protocol manifest、paired rows、decision、analysis、incident与rollback drill。

**项目挂钩**：Robot Harness的n/scorer不一致且safety弱；OPD不同pool最佳checkpoint不同且缺raw predictions；OpenPiVLA 97.4与diagnostics不同lineage；WAM只有单episode；UWM只有186/250 summary。它们可用于设计补强，不能说已有统一gate/canary。

**追问树**：golden为何会overfit？为何要paired？p>0.05为何不够？safety能否加权平均？missing怎么判？shadow与canary差别？minimum exposure为何必要？abort与rollback差别？机器人canary还需什么独立保护？五项目谁最接近哪一层？

**易错点**：事后改gold；不同n/scorer相减；overall掩盖critical；静默删crash；没有decision window；baseline不同时段；shadow有执行权；只有abort命令没有known-good bundle；canary通过就称全量安全；把Argo机制写成项目已使用。

**危险答案**：说“每个checkpoint跑benchmark就是regression gate”“overall涨了就发”“p值不显著说明无退化”“小流量没事故说明安全”“有一键回滚就够”或把当前五项目讲成已上线canary。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-010 知识页](../knowledge/vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)。
2. [EVAL-010 Source Freeze](../sources/vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
8. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
