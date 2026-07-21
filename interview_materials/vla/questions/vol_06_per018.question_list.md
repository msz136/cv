# VOL 06 PER-018 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / independent_fact_reviewed / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：BC、teacher/student forcing、scheduled sampling、exposure bias、DAgger visited-state oracle/aggregate/β、GAE/PPO/DD-PPO、termination/truncation、typed training manifest、train/eval protocol、diagnosis与五项目真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-018 | L3 | P1 | VLN/ObjectNav 中 BC、Teacher/Student Forcing、Scheduled Sampling、DAgger 与 PPO 如何区分？怎样判断项目是否真的实现了 DAgger/PPO？ | 七份固定版本primary PDF、四个official repositories/27文件、10个deterministic probes、五份inventory与八个local-direct files；无候选人local navigation expert/oracle、immutable DAgger rounds、fresh PPO rollout、behavior log-prob/value/return、matched checkpoint/episode/result或ownership闭环 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. BC、teacher forcing、student forcing、scheduled sampling、DAgger与PPO按state distribution、target/feedback和update object分开。
4. DAgger保留current/mixture-policy rollout、visited-state oracle label、immutable aggregate与β lineage四道门。
5. PPO保留fresh rollout、reward、old log-prob、value/return、GAE、ratio/clip、terminated/truncated与checkpoint lineage。
6. train/eval绑定task/split、observation/action/STOP、oracle/reward、collector policy、horizon、seed与episode denominator。
7. diagnosis按task/schema→oracle/reward→policy/checkpoint→collector→label/log-prob/value/return→mask/denominator→ratio/grad→eval protocol的first divergence展开。
8. 10个probe只证明数值与identity合同，不升级成论文benchmark或本地项目结果。
9. OpenPiVLA、Robot Harness、OPD、UWM、WAM只映射到有证据的offline/interface/upstream/failed-trace hook，不升级为个人navigation DAgger/PPO ownership。
10. 30秒答案≤180字符，机制展开≤350字符；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-018 Source Freeze](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html) 与 [PER-018 Knowledge](../knowledge/vol_06_per018_navigation_bc_dagger_rl_exposure_bias.html)。
- 依赖缺口：typed task/oracle/reward/collector/update/checkpoint/eval manifest、immutable DAgger round、fresh PPO rollout、behavior log-prob/value/return、matched navigation episode/result和逐文件候选人ownership确认。
- `VLA-PER-018` source/knowledge/card与独立事实复核已同步，题卡保持`unseen`；下一bounded slice优先进行一题真实口述，不启动PER-019。
