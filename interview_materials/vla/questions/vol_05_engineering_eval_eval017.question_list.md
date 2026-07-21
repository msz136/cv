# VOL 05 Engineering / Evaluation：EVAL-017 题目清单

> 状态：`source_frozen / knowledge_drafted / card_1_of_1 / WARN`  
> 知识页：[Simulator / Shadow / Real-Robot Gate](../knowledge/vol_05_engineering_eval_eval017_simulator_shadow_real_robot_gate.html)  
> 来源冻结：[EVAL-017 Source Freeze](../sources/vol_05_eval017_simulator_shadow_real_robot_gate_source_freeze.html)  
> 题卡：[单张折叠题卡](vol_05_engineering_eval_eval017.html)  
> 练习状态：`unseen`；没有真实口述前不得升级。

| ID | 难度 | 优先级 | 主题 | 状态 |
| --- | --- | --- | --- | --- |
| `VLA-EVAL-017` | L3 | P1 | sim-real common support、no-authority shadow、bounded real canary、risk exposure、promotion/abort/rollback/recovery | card drafted / unseen |

## 边界

- simulator、dry-run/HIL、live shadow、guarded real canary与progressive deployment分层。
- shadow使用live observation但candidate无actuator authority，不能报candidate closed-loop success。
- sim-real相关/排序需要多个policy/checkpoint和matched task/protocol；单点不成立。
- canary冻结authority/risk envelope、minimum exposure、hard trigger、human stop及scene recovery。
- 0/n不等于零风险；rollback known-good只改变未来动作，不自动恢复物理状态。
- 五项目无same-bundle sim→shadow→real canary连续证据；本切片不生成EVAL-018或`coaching_state.md`。
