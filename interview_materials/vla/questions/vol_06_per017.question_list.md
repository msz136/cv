# VOL 06 PER-017 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：POMDP belief、predict/correct/normalize、zero-likelihood、recurrent/spatial/episodic memory、frontier extraction、map revision、reachability/risk gate、IG/goal/coverage/novelty/cost utility、revisit/stuck/unreachable、metric contract、diagnosis与五项目真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-017 | L3 | P1 | Partial observation下怎样维护belief和memory，并用frontier、information gain、coverage、revisit与stuck完成active exploration？ | 八份完整primary PDF、六个fixed official repositories/36文件、10个deterministic probes、五份inventory与Robot Harness六个local-direct exceptions；无本地transition/observation model、calibrated belief、typed memory/frontier/visited trace、matched exploration episode、checkpoint/result或候选人ownership闭环 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. true state、belief、recurrent hidden、explicit spatial map与episodic event分开；episode reset与map/model/schema revision失效条件明确。
4. belief遵循predict→correct→normalize；zero likelihood、underflow或NaN必须fail closed，不静默伪造posterior。
5. frontier定义为observed/known-free邻接unknown；predicted-free、inflation、viewpoint、freshness、reachability与risk gate边界保留。
6. IG、goal probability、coverage/novelty、travel cost与risk分项可审计；工程综合utility不冒充任一论文原公式。
7. 只执行bounded plan prefix；progress、collision、oscillation、revisit、stuck、unreachable与map revision进入恢复/重规划合同。
8. coverage、area seen、visitation、revisit与frontier reach冻结visibility、cell、budget和failure denominator，不用单一coverage替代导航能力。
9. OPD、Robot Harness、OpenPiVLA、WAM、UWM只映射到有证据的upstream、history、map asset或interface hook，不升级为本地active exploration、robot result或个人ownership。
10. 30秒答案≤180字符，机制展开≤350字符；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-017 Source Freeze](../sources/vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html) 与 [PER-017 Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html)。
- 依赖缺口：typed episode/sensor/model/map manifest、belief calibration、memory reset/invalidation trace、frontier/visited/coverage log、planner/controller progress与failure trace、matched exploration A/B、checkpoint/result和逐文件候选人ownership确认。
- `VLA-PER-017` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只冻结`VLA-PER-018` navigation BC/DAgger/RL/exposure-bias source，不生成knowledge/card。
