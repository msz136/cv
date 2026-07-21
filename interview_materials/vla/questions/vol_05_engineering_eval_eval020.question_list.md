# VOL 05 Engineering / Evaluation：EVAL-020 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Incident Timeline / Root Cause / Bug-fix Verification](../knowledge/vol_05_engineering_eval_eval020_incident_timeline_root_cause_bugfix_verification.html)  
> 来源冻结：[EVAL-020 Source Freeze](../sources/vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval020.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-020` | L2 | P1 | impact/timeline、first divergence、hypothesis/cause ladder、bisect边界、same-protocol red→green、controls/fresh cases与prevention | card drafted / unseen |

## 边界

- timeline必须绑定clock/provenance；时间先后、last change与first bad commit不自动证明root cause。
- mitigation、rollback、recovery、corrective fix与prevention严格分开。
- confirmed cause至少需要reproducer、targeted intervention、same-protocol red→green、unaffected controls与fresh cases。
- flaky或无法复现时保持`unknown/partially_confirmed`，不重跑到出现期望结果。
- OPD只到狭窄协议层局部验证；UWM只到DataLoader子系统A/B；其余项目无matched fix闭环。
- 本切片不生成EVAL-021或`coaching_state.md`。
