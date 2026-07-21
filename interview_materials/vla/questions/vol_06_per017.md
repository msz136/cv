# VOL 06 Perception / Grounding / Navigation：PER-017 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-017`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-017 Belief / Memory / Frontier / Active Exploration Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html)；来源边界见 [PER-017 Source Freeze](../sources/vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html)。

## Belief、Memory、Frontier 与 Active Exploration

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-017</b> · Partial observation下怎样维护belief和memory，并用frontier、information gain、coverage、revisit与stuck完成active exploration？</summary>

**面试意图**：判断你能否把“记住历史、探索未知”拆成有身份和失效条件的 belief/memory 状态、known-free/unknown frontier、硬门与软效用、短执行与重规划、可复算指标，再在项目追问中坚持“history/map/interface 不等于 active-exploration runtime”。

**30 秒回答**：用transition/likelihood更新belief，分母0就停或重定位；memory分hidden、map、event。frontier是free邻接unknown，先过revision、可达、风险门，再按IG、目标概率、coverage减路程与风险排序；执行短前缀，用revisit、stuck、map revision触发重规划。

**机制展开（约 2 分钟）**：先冻结episode、传感器/时钟、模型和地图版本。belief按预测→校正→归一化更新，分母0/NaN就停，不伪造后验。memory分hidden、版本绑定map、时间戳event；reset、重定位或schema变化时清空/失效。frontier只取膨胀后free邻接unknown，经新鲜度、可达、风险硬门，再以IG、目标概率、coverage/novelty减路程/风险排序。执行短plan；进展停滞、碰撞、振荡、revisit或map revision触发重规划。评估冻结visibility/cell/budget/denominator；五项目只有接口/资产，无exploration runtime/result。

**诊断 / 证据**：按first divergence检查episode/sensor/clock/model/map身份→predict/correct/normalizer与数值有限性→hidden reset、spatial anchor revision、event timestamp→occupancy legend、inflation、free/unknown边界→frontier component、viewpoint、path reachability、risk/freshness gate→IG/goal/coverage/novelty/cost分项→plan prefix、progress、collision、oscillation、revisit/cooldown与map revision→visibility/cell/budget/denominator。固定probe至少保留Bayes `[.6,.4]×[.2,.8]→[.272727,.727273]`、全零likelihood拒绝、binary `.5`/accuracy `.9`得IG `.531004 bits`、frontier为`[(1,2),(2,2)]`、隔墙候选不可达、utility选A、visit `0/1/4`的novelty为`1/.707107/.447214`、revision 7/8只留e1、hidden `[3,-2]` reset为0、`runtimeReady=false`或缺trace均不通过；10/10只证明合同，不是benchmark或项目结果。

**项目挂钩**：Robot Harness有semantic duplicate turn compaction、导航tool contract、occupancy/PCD/reloc map路径与pixel/world bridge，但定向history test仍为`2 failed, 2 passed, 2 warnings`，且fallback明确`runtimeReady=false`；没有typed belief/frontier/visited trace、planner/controller log或matched episode。OPD的`target_coverage/pred_coverage`是2D region overlap；OpenPiVLA的action history/chunk只是policy temporal context；WAM的video/world prediction不是calibrated belief；UWM的simulator ground-truth state和DataLoader memory也不是部署memory。五项目都不能升级为已实现frontier exploration、coverage提升或真实机器人结果；Git身份、字段名和map资产也不能替代机制、运行证据与候选人ownership。

**追问树**：POMDP的state、observation、history、belief和policy怎样区分？Bayes predict与correct各依赖什么模型？normalizer为0、underflow或NaN为何不能填均匀分布？belief、recurrent hidden、spatial map、episodic event各保存什么？episode reset、relocalization、map revision、model/schema变化分别失效什么？为什么frontier位于known-free一侧而不是unknown一侧？predicted-free为何不能直接当observed-free？inflation、viewpoint与path reachability怎样进入硬门？frontier cluster大小能否等同information gain？IG的expectation对什么 observation 求？goal probability、coverage、novelty、distance和risk怎样避免量纲支配？何时必须hard-risk gate而不是负权重？为什么只执行plan prefix？怎样区分暂时stuck、系统振荡与真正unreachable？revisit是失败还是必要行为？coverage、area seen、visitation、revisit rate与frontier reach rate的分母怎样冻结？reset泄漏为何会虚高？Robot Harness的history、map和tool字段最多支持什么claim？

**易错点**：把history当belief、action chunk当长期memory、world-model latent当calibrated posterior；漏掉transition predict或用全零likelihood生成均匀后验；让hidden/map跨episode泄漏；把unknown或predicted-free直接当安全可走区域；只按frontier大小排序，不做revision、可达和风险门；把PONI potential说成经典frontier或通用IG；用随机动作掩盖no-valid-frontier；只报coverage，不冻结visibility/cell/budget/denominator；把revisit一律判错；用字段名、map文件、fallback test、公开repo或Git身份证明本地exploration runtime与个人贡献。

**危险答案**：说“belief就是把历史喂给LSTM”“frontier就是未知格子”“信息增益就是frontier越大越好”“coverage高说明导航好”“卡住就随机走”“有occupancy map和history所以项目做了active exploration”，却不交代episode/sensor/model/map身份、predict/correct/normalize与zero-likelihood、memory reset/invalidation、known-free/unknown语义、reachability/risk硬门、utility分项、短执行/重规划、metric denominator、matched runtime artifact和候选人ownership。

**来源**：[1][2][3][4][5][6][7][8][9][10]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-017 Belief / Memory / Frontier / Active Exploration Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html)：POMDP/Bayes、三类memory、typed manifest、frontier/IG/utility、coverage/revisit、10 probes、诊断、两档回答与五项目truth boundary。
2. [PER-017 Source Freeze](../sources/vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html)：八份primary paper、六个fixed official repositories/36文件、10个deterministic probes、五份inventory与Robot Harness local-direct audit。
3. Kaelbling, Littman & Cassandra, [Planning and Acting in Partially Observable Stochastic Domains](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), Artificial Intelligence, 1998。
4. Yamauchi, [A Frontier-Based Approach for Autonomous Exploration](https://www.robotfrontier.com/papers/cira97.pdf), CIRA, 1997。
5. Chaplot et al., [Learning to Explore using Active Neural SLAM](https://arxiv.org/abs/2004.05155), ICLR, 2020；[official code@8876e1e](https://github.com/devendrachaplot/Neural-SLAM/tree/8876e1eafff5414e92d72347d89488d970a4f6b2)。
6. Ramakrishnan et al., [Occupancy Anticipation for Efficient Exploration and Navigation](https://arxiv.org/abs/2008.09285), ECCV, 2020；[official code@aea6a2c](https://github.com/facebookresearch/OccupancyAnticipation/tree/aea6a2c0d9701336c01c9c85f5c3b8565d7c52ba)。
7. Chaplot et al., [Object Goal Navigation using Goal-Oriented Semantic Exploration](https://arxiv.org/abs/2007.00643), NeurIPS, 2020；[official code@5d76902](https://github.com/devendrachaplot/Object-Goal-Navigation/tree/5d76902fe9be821926a1de32557ca9a8dc21d0f5)。
8. Ramakrishnan et al., [PONI](https://arxiv.org/abs/2201.10029), CVPR, 2022；[official code@30682c2](https://github.com/srama2512/PONI/tree/30682c2bdcd820eec8f72043b2579eb045d547bf)。
9. Ramakrishnan, Jayaraman & Grauman, [An Exploration of Embodied Visual Exploration](https://arxiv.org/abs/2001.02192)；[official code@09d3f9b](https://github.com/facebookresearch/exploring_exploration/tree/09d3f9b8703162fcc0974989e60f8cd5b47d4d39)；Das et al., [Embodied Question Answering](https://arxiv.org/abs/1711.11543)；[official code@306fd6e](https://github.com/facebookresearch/EmbodiedQA/tree/306fd6ef3064b5b9a3bd2d3f06ac96a09c481d9d)。
10. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
