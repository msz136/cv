# VOL 06 PER-017 Source Freeze：Belief、Memory、Frontier 与 Active Exploration

> 状态：`source_frozen / VLA-PER-017 / primary_official_checked / belief_memory_exploration_contract / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本 source slice 只冻结 POMDP belief、recurrent latent / explicit spatial map / episodic history memory、frontier、active exploration、coverage / visitation / revisit protocol 与五项目真实性边界；下游 knowledge 与单张 card 已在各自 bounded slice 同步；card保持 `unseen`，不修改 mastery，不进入 PER-018 的 BC/DAgger/RL 训练，也不重写 PER-005 的 navigation policy architecture、PER-016 的 localization/SLAM 或 PER-019 的完整导航评估。

## 问题（Question）

面试官问“partial observation 下的导航为什么需要 belief 和 memory、frontier 怎样从 occupancy map 中产生、information gain 如何与目标概率/路程/风险权衡、revisit 和 stuck 怎样处理”时，怎样给出可实现、可评估、会 fail closed 的合同；以及五个本地项目到底有多少直接证据。

## 1. 结论先行

1. POMDP 的 hidden state、observation、action 与 belief 必须分开。belief 是在已冻结 transition / observation model 下对 hidden state 的条件分布，不是“把历史塞进 LSTM”或“保存一张地图”的同义词。
2. memory 至少分三类：recurrent latent 压缩序列、explicit spatial map 保存 world-frame occupancy/semantic/visited state、episodic history 保存带时间与来源的 observation/action/event。它们可组合，但更新、reset、校准、可解释性和失效条件不同。
3. occupancy frontier 是 **known-free 与 unknown 的边界**，不是任意高不确定区域、目标物体得分峰值或地图边缘。frontier 进入候选集前还要经过 obstacle inflation、连通性、可达性、map revision 和 stale-age gate。
4. active exploration 不是“随机走得更远”。information gain、coverage gain、novelty、goal probability、travel cost 与 risk 必须显式分项；权重和预算改变结论，单一 coverage 数字不能证明 goal-directed navigation 更好。
5. revisit 本身不是错误：绕障、回到高价值观测位、loop recovery 都可能需要 revisit。应区分有信息收益的 deliberate revisit、无进展振荡与因 map 错误导致的重复规划。
6. map revision、episode reset 或 localization jump 会使旧 frontier ID、坐标锚点、distance cache 与 recurrent hidden state失效。继续消费 stale memory 会把“长期记忆”变成系统性错误。
7. 当前五项目没有可核验的 navigation belief/frontier/active-exploration runtime 或 episode trace。Robot Harness 只有消息 history 管理、导航工具合同和 occupancy/map bridge；`history.py` 的定向测试当前为 `2 passed / 2 failed`，更不能把它升级成 learned navigation memory。整体保持 `WARN`。

## 2. Primary Paper 冻结矩阵

| 来源 | 固定版本 / 完整性 | PDF SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| Kaelbling, Littman & Cassandra, [Planning and Acting in Partially Observable Stochastic Domains](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf) | Artificial Intelligence 101, 1998；作者 PDF；36页；全文解析；belief/state-estimator/policy 视觉检查 p8 | `71A6D1AEE278E93C5FAE8DD7D0C452C8B7B035AF55D9DCE2BC367D473BFC9645` | POMDP tuple、belief state、Bayes update、belief-MDP 与 policy 边界 | 任意 neural hidden state 已校准成 belief、本地导航部署 |
| Yamauchi, [A Frontier-Based Approach for Autonomous Exploration](https://www.robotfrontier.com/papers/cira97.pdf) | CIRA 1997；作者站 PDF；6页；全文解析；open/unknown/occupied 与 frontier 视觉检查 p2 | `34AEF437313894AB1EFA114E2C86D6D645688CE449235B7B965735AA7EF98D59` | frontier 是 open/known-free 与 unexplored/unknown 的边界、去 frontier 的经典探索循环 | learned utility、semantic goal probability、任意地图均可达 |
| Chaplot et al., [Learning to Explore using Active Neural SLAM v1](https://arxiv.org/pdf/2004.05155v1) | arXiv `2004.05155v1` / ICLR 2020；18页；全文解析；map/visited/global-local policy 视觉检查 p5 | `683DD9DBB8D9E168C00572C1F1C99EAA601FBE4A2D7A0918BA1F9CAC575E365C` | learned mapper、explicit map/visited state、global goal、local planner、coverage reward | 完整 Bayesian belief、真实机器人泛化、所有 unexplored cell 可达 |
| Ramakrishnan et al., [Occupancy Anticipation for Efficient Exploration and Navigation v2](https://arxiv.org/pdf/2008.09285v2) | arXiv `2008.09285v2` / ECCV 2020；38页；全文解析；anticipative mapper/global-local pipeline 视觉检查 p7 | `ACDC453E2DEB142E3BBC7C44D7C8F4ECAE8247DC91137E022DB1C1D7D59F8C63` | 可见范围外 occupancy anticipation、spatial memory、area seen 与 map-quality边界 | predicted-free 自动等于 safe known-free、任意 domain 下校准 |
| Chaplot et al., [Object Goal Navigation using Goal-Oriented Semantic Exploration v2](https://arxiv.org/pdf/2007.00643v2) | arXiv `2007.00643v2` / NeurIPS 2020；11页；全文解析；semantic map 与 long-term goal 视觉检查 p3 | `ABE66C10E6D8115852EDF797CC02BD09B15E587E1690573C4582CF7D714621F2` | episodic semantic map、goal-conditioned exploration、global goal/local planning | POMDP posterior、任意语义预测可直接控制、用户项目结果 |
| Ramakrishnan et al., [PONI: Potential Functions for ObjectGoal Navigation with Interaction-free Learning v2](https://arxiv.org/pdf/2201.10029v2) | arXiv `2201.10029v2` / CVPR 2022；19页；全文解析；area/object potential 与 frontier 视觉检查 p4 | `D9603E23F3936E0F767C93BB49A6206CA571D5B65D4973374EB37AA7317D57B5` | semantic-map-conditioned area/object potentials、frontier/goal scoring、distance masking | 本页综合 utility 是 PONI 原公式、无需环境/地图误差 gate |
| Ramakrishnan, Jayaraman & Grauman, [An Exploration of Embodied Visual Exploration v2](https://arxiv.org/pdf/2001.02192v2) | arXiv `2001.02192v2`；51页；全文解析；curiosity/novelty/coverage/reconstruction 视觉检查 p10 | `4AFD4BB8653F883EC49FDA5EB5D077187FE9D5A7F400D792D84F656E071A0046` | exploration objective taxonomy、coverage/visitation/downstream-task evaluation 与 frontier baseline | 一个 intrinsic reward 在所有任务都最好、指标跨协议直接可比 |
| Das et al., [Embodied Question Answering v2](https://arxiv.org/pdf/1711.11543v2) | arXiv `1711.11543v2` / CVPR 2018；20页；全文解析；LSTM history、planner/controller 视觉检查 p7 | `66FD93EF8F14FB1B9CBD6B281D84CCF2D154A0F2947E35E59CA567CD51F938DE` | recurrent action/visual history、hierarchical planner/controller、history-dependent embodied policy | hidden state 是显式 belief、frontier/coverage policy、本地 EQA 结果 |

八份 PDF 均检查 `%PDF`、尾部 `%%EOF` 并用 `pypdf` 读取全部页面：总文本字符分别为 98,559、22,223、67,795、87,706、40,634、69,679、120,354、66,913；只有 Exploring Exploration 有1个无提取文本页面，其余页面均有文本。上述代表页已由 Poppler 150 DPI 渲染并视觉确认正文、公式与系统图清晰。旧 PDF 的字体解析 warning 不改变代表页可读性。论文版权条件与代码 license 分开，PDF 可读不代表可任意再分发。

## 3. Official Repository 冻结矩阵

| 官方仓库 | 固定 revision / date / license | 直接读取文件与 SHA-256 | 支持边界 |
| --- | --- | --- | --- |
| [devendrachaplot/Neural-SLAM@8876e1e](https://github.com/devendrachaplot/Neural-SLAM/tree/8876e1eafff5414e92d72347d89488d970a4f6b2) | `8876e1eafff5414e92d72347d89488d970a4f6b2`；2021-07-19；MIT | `README C8EE08DBDF05E77B777648F7EE3A54D0E02531B70EFDAB5F70DF1B74203B44C6`；`LICENSE 220C08BA52B19297199382B6741396A4DD7953CA6EBACA7FC7FE734083B91F97`；`model.py 48D90E3073645CF703930F7D6E36641567A4DE972C4232EEC3454D3765D703B4`；`main.py 85A2E5183296DFAF7C0437D6BF6ABDF7E5D8550770592808E7B734FEC6F82E37`；`exploration_env.py 6D434BD731AE35D20862BB2B9FFC02D1FE96624C48BD82B3A41E3B3B07D77C6C`；`map_builder.py 09D97AA14ED6E2C931159D7FFD43B1C08EB1C2C032E2048C79DA5C92D85893A2` | map/explored/visited state、explored-area reward、global goal 与 FMM reachability；不支持本地复现或 calibrated belief |
| [facebookresearch/OccupancyAnticipation@aea6a2c](https://github.com/facebookresearch/OccupancyAnticipation/tree/aea6a2c0d9701336c01c9c85f5c3b8565d7c52ba) | `aea6a2c0d9701336c01c9c85f5c3b8565d7c52ba`；2021-07-01；MIT | `README 4FDCE677448FBAA44DA4591612F327A1D201D69ECCA9CF8AFAA15E0EADCD03D6`；`LICENSE F08A94BFB0BDC1D7F1CB59BADAF0F8C551B10DB871185622DBF1FD036AFFA9CB`；`occant.py 51B59EFF718BE9D0E36DA01CEEB7D8895AB1650843A3EC8BA518A98B2F93F55C`；`ans.py 8F6077A3C4472880B8AA493F3D0E05C8F64ABFF6AD37254DCCD1D9A5942458F1`；`measures.py B78EF28B2CC1B7C5433F96197E13C403B158D289355B3B145F3FB7DAA73B2C42`；`metrics.py 5D8F3D7C1FE8AC749FCF7DBBC169DE1A5244396F7C72CCD84410B423E369A5A9` | anticipation map、entropy filter、area seen/free/occupied 与 map quality；不支持 predicted-free 无风险执行 |
| [devendrachaplot/Object-Goal-Navigation@5d76902](https://github.com/devendrachaplot/Object-Goal-Navigation/tree/5d76902fe9be821926a1de32557ca9a8dc21d0f5) | `5d76902fe9be821926a1de32557ca9a8dc21d0f5`；2021-04-02；MIT | `README 8EE0E23B3B6433456DE28EB1468D6543934583B85FA6745BDD98BE3C614D4A95`；`LICENSE 220C08BA52B19297199382B6741396A4DD7953CA6EBACA7FC7FE734083B91F97`；`model.py E551DD5FFEC7A88A29DB5FF33EB22A9BB664499ACF88A3EC94AF3980CA9B5D93`；`sem_exp.py 7F395F3A23116337B73456B365EB641AFC3F633AC5FE3FF8EFDF0ED8DC0C2E22`；`objectgoal_env.py 80ABB5FFF6A2CD1FF0D438F677DFA59F7F4FDA625E00AE224FFBD18008F648B7`；`map_builder.py A5B7EDF83827E3A038C08D741670DA8B0C23E4591DAFCABA88D41B7D33D93612` | semantic episodic map、goal found/global goal/planner loop；不支持 posterior calibration 或 local benchmark |
| [srama2512/PONI@30682c2](https://github.com/srama2512/PONI/tree/30682c2bdcd820eec8f72043b2579eb045d547bf) | `30682c2bdcd820eec8f72043b2579eb045d547bf`；2022-12-29；MIT | `README 4E4A939791EAB41D122312BA28FF260ADD031A3B3404479766C78C9D362A4E0A`；`LICENSE FF14374A819121D78E59F43B846AA2E305282AF7393764CE8E439BA3C9884F1C`；`poni/model.py DD25A467C62C5C156BACD451294E9369C80D084661F9DFC1B5281D998E511E6A`；`pf_exp.py C65CFB99F213BE2417B22F13E65D40583E9313E94C97CB3088AE1EE409980CDD`；`global_agent.py 95E4E83768AA425CEE2AC959173CB129C3CB08E3926AE83F2DACE17E878D0CA2`；`create_poni_dataset.py 0643FAE3C3F346080608CA5E877C6F73CC3CB0BAF7AA2D94E2E7FA7531BC24BC` | area/object potential、unexplored masking、agent-distance maps 与 global goal；`needs_frontier_maps=False` 说明该 policy 不等于经典 frontier 实现 |
| [facebookresearch/exploring_exploration@09d3f9b](https://github.com/facebookresearch/exploring_exploration/tree/09d3f9b8703162fcc0974989e60f8cd5b47d4d39) | `09d3f9b8703162fcc0974989e60f8cd5b47d4d39`；2021-03-16；CC BY-NC 4.0 | `README 485D4816EDBC1439ACB9BFC23B22570026A9C0364F90879228A027EFBB1E4C3F`；`LICENSE 864DF6B58BF3660C2944072253E854A0F51F47E26E251E1CAB6E911E1E8B057E`；`frontier_agent.py E2E4C0C72D83930B8E3355AAD0385C9E4A9225A675EFC2A9F7B0D51E82A56BD7`；`exploration.py 2F97C6C2F1763C5CCDA7EFD2B6B794B216873D514402BFE5460AEEAAD41EA2C3`；`evaluate_visitation.py BC70A6051B3B5C61EE3B6BFF1EAE62DEC7223CD25F05BD9FC259442B9D97716A`；`metrics.py 765109195C2F59076DE783DAC1E03B9A9AD1314BD5B13E0D6254DFB4E479FFC5` | frontier baseline、recurrent exploration policy、visitation evaluation entrypoint 与 downstream metrics；license 不是商业部署许可 |
| [facebookresearch/EmbodiedQA@306fd6e](https://github.com/facebookresearch/EmbodiedQA/tree/306fd6ef3064b5b9a3bd2d3f06ac96a09c481d9d) | `306fd6ef3064b5b9a3bd2d3f06ac96a09c481d9d`；2018-12-22；BSD-3-Clause-like project license | `README E2490D906E798CD6E5D7498DFCB0A2B2BE422B75847C676C7F77A85DFE9DD4C1`；`LICENSE 8BA40A26092D2C9EF8B45E705B04F0D79855811AEBBC3683B2F08E9AC41F84FB`；`models.py B1DD28AB8176A2105D881862332203805FD22D6340DDBAADCF0A3B6BB61D1646`；`train_nav.py D3BDECA19FFBB75E4A2A36339E534EC863390FF2E194C5345C94FA42E434928C`；`data.py E15B8C7FA63DF6CBDF9E981B4B88F628587695F805AA91F537646BF9A7C1864C`；`metrics.py BEA27FF3F0CDAAD0347B341D00269B867E2439B1611BC2CDF98CC39953CEE171` | LSTM action history、planner/controller hidden state、episode/stop metrics；不支持 explicit frontier 或 Bayesian belief |

36个文件均从 fixed checkout 按原始字节计算 SHA-256。repo license 不自动覆盖论文、dataset、Habitat/Matterport assets、model weights、third-party planner、ROS package 或商业部署；官方代码存在也不证明用户项目运行了相同 revision/config/checkpoint。

## 4. 节点边界与依赖

| 相邻节点 | 已负责 | PER-017只新增 |
| --- | --- | --- |
| PER-004 | VLN/ObjectNav task、episode、action、stop、SR/SPL 等合同 | partial observation 下的 information state 与探索状态 |
| PER-005 | map-free/map-based/waypoint、global/local policy、planner/controller、latency | belief/memory/frontier/active-exploration 语义与失效门 |
| PER-013/014 | occupancy/BEV/semantic scene 表示与 3D query | known-free/unknown/frontier、visited/episodic layer 与 exploration utility |
| PER-015 | reachability、collision、uncertainty 与 action failure gate | exploration candidate 的 risk/reachability/revisit gate |
| PER-016 | localization/odometry/SLAM、map revision、drift、ATE/RPE | belief 如何消费 state/map revision，旧 memory 如何 invalidation |
| PER-018 | BC/DAgger/RL、reward/optimization 与 policy learning | 不在本页声称怎样训练最优 exploration policy |
| PER-019 | 完整导航 benchmark、failure statistics 与 sim-to-real | 本页只冻结 coverage/visitation/revisit 子协议，不宣称整套导航评估完成 |

## 5. POMDP 与 Belief Contract

POMDP 可写为：

\[
\mathcal M=\langle \mathcal S,\mathcal A,T,\mathcal O,Z,R,\gamma\rangle,
\qquad
b_t(s)=P(s_t=s\mid o_{1:t},a_{1:t-1}).
\]

变量解释：`S` 是不可完全观测的环境状态，`A` 是动作，`T` 是转移，`O` 是观测空间，`Z(o|s,a)` 是 observation likelihood，`R` 是 reward，`γ` 是折扣；`b_t` 是在完整 action-observation history 条件下的 posterior。直觉是策略不直接看到真实 state，只能维护足以决策的信息状态。实现映射：belief 记录必须绑定 model revision、observation schema、timestamp、episode 与 normalization；一个 RNN tensor 只有在训练/校准合同支持时才可称为 approximate belief。

离散 Bayes update 为：

\[
\tilde b_t(s')=Z(o_t\mid s',a_{t-1})
\sum_s T(s'\mid s,a_{t-1})b_{t-1}(s),
\qquad
b_t(s')=\frac{\tilde b_t(s')}{\sum_x\tilde b_t(x)}.
\]

变量解释：先用 transition 得到 prior，再用当前 observation likelihood 校正并归一化。probe 使用 `b=[0.6,0.4]`、likelihood `[0.2,0.8]`，posterior 为 `[0.272727,0.727273]`。若归一化常数为0，表示 observation/model 不一致或数值崩溃；目标合同必须返回 `invalid_belief`、保留 last-safe state 或触发 stop/relocalize，不能静默均匀化后继续控制。

## 6. 四类状态不能混写

| 状态 | 例子 | 优点 | 主要缺口 / 失效门 |
| --- | --- | --- | --- |
| true simulator state | GT pose、完整 occupancy、object state | 可训练/评估 | 部署不可直接读取；不能冒充 estimator output |
| probabilistic belief | pose/object/map posterior 或 particles | 能表达多模态与 uncertainty | 依赖显式 transition/likelihood、归一化和校准 |
| recurrent latent | GRU/LSTM/Transformer cache hidden state | 紧凑、端到端可学 | 语义不透明、可能泄漏 episode、未必校准或 Markov-sufficient |
| explicit map / history | occupancy/semantic/visited map 与 timestamped events | 可解释、可查询、可 revision | frame/time/data association 错误会累积并污染下游 |

“有 memory”至少要回答：写入什么、坐标/时间是什么、谁更新、容量/压缩、何时 reset、map/episode revision 如何绑定、冲突如何合并、consumer 怎样检测 stale。只说“用了 LSTM”或“传入历史帧”不够。

## 7. Memory Taxonomy 与生命周期

### 7.1 Recurrent latent

典型更新为 `h_t=f_θ(h_{t-1},o_t,a_{t-1})`。它可以编码历史，但不能从接口形状推出其中保存了地图、目标概率或 uncertainty。评估要有 hidden reset、sequence length、truncation、teacher-forcing/rollout mismatch 与 ablation；跨 episode 不清零会造成 leakage。

### 7.2 Explicit spatial map

至少分 `occupancy`、`explored/known`、`semantic`、`visited`、`uncertainty` 与 `timestamp` 层。`unknown` 不能由 occupancy 概率0.5、padding、传感器不可见或 map outside-range 混成一个值；anticipation 的 predicted occupancy 还要与 directly observed known-free 分层。

### 7.3 Episodic / history memory

记录应包含 `episode_id/event_id/time/pose_or_frame/map_revision/observation_ref/action/result/confidence`。文本对话压缩是 interaction history 管理；除非它绑定真实 navigation observation、pose/map revision 和 rollout 结果，否则不构成 embodied episodic memory。

### 7.4 Invalidation

以下事件至少触发局部或全量失效：episode reset、map UUID/revision 变化、global localization jump、sensor/calibration revision 变化、semantic model/checkpoint 变化、clock discontinuity。失效对象包括 frontier component ID、distance field、goal score、visited cell index、episodic coordinate anchor 与 recurrent hidden state。

## 8. Frontier：定义、聚类与可达性

对栅格地图 `M` 与4/8邻域 `N(c)`，经典 occupancy frontier 可写成：

\[
\mathcal F(M)=\{c\mid M(c)=\text{known-free},\ 
\exists c'\in\mathcal N(c):M(c')=\text{unknown}\}.
\]

变量解释：frontier cell 本身是当前认为可站立的 known-free cell，它邻接尚未观测的 unknown；先对 free-space 做 obstacle inflation，再抽取连通 frontier component，最后选择 component centroid 或可达 view pose。直觉是机器人站在已知安全一侧观察未知，而不是把 unknown cell 当安全目标。probe 的4邻域网格得到 frontier `[(1,2),(2,2)]`。

候选还必须满足：

- 与当前 pose 在 inflated known-free graph 连通；
- component 面积、sensor view range 与预期可见 unknown 足够；
- goal/centroid 能投影到实际可达 free cell；
- map revision、frontier age 与 distance field revision 一致；
- predicted-free 与 observed-free 有不同 risk budget；
- blacklisted/unreachable/stuck candidate 在 cooldown 前不重复入队。

PONI 的 potential policy 可消费 unexplored mask 和 distance map，但 fixed `pf_exp.py` 明确 `needs_frontier_maps=False`；所以“使用 unexplored potential”不能被改写为“代码实现了经典 frontier extractor”。

## 9. Information Gain 与综合 Exploration Utility

belief entropy 与 expected information gain 可写为：

\[
H(b_t)=-\sum_s b_t(s)\log b_t(s),
\qquad
\operatorname{IG}(a)=H(b_t)-
\mathbb E_{o\sim P(o\mid b_t,a)}[H(b_{t+1})].
\]

变量解释：entropy 衡量当前 uncertainty，IG 衡量执行 action 后预期减少多少 uncertainty。probe 使用均匀二状态 prior 与准确率0.9的对称 observation model，得到 `1-H_2(0.9)=0.531004 bits`。实现中可对 pose belief、occupancy cells、semantic goal location 或 downstream prediction 定义 entropy，但这些不是同一量，必须冻结粒度、相关性近似和 observation model。

工程候选排序可综合为：

\[
U(f)=w_I\,\operatorname{IG}(f)+w_g\,p_{\mathrm{goal}}(f)
+w_c\,\Delta C(f)+w_n\,N(f)
-w_d\,d(f)-w_r\,\operatorname{Risk}(f).
\]

变量解释：`f` 是候选 frontier/viewpoint，`ΔC` 是预期 coverage gain，`N` 是 novelty，`d` 是规划距离/时间，`Risk` 汇总 collision、localization、predicted-free 与 uncertainty。此式是本页对多篇来源的 **工程综合合同**，不是某篇论文或 PONI 的逐字公式。权重必须绑定训练/部署场景；risk 超硬阈值时应直接 reject，而不是用高 IG 抵消安全风险。

## 10. Goal-directed 与 Task-agnostic Exploration

| 类型 | 主要价值 | 典型记忆/score | 失败方式 |
| --- | --- | --- | --- |
| task-agnostic coverage | 尽快看见更多区域/视角 | occupancy、visited、coverage/novelty | 覆盖多但与任务无关 |
| information seeking | 降低 pose/map/object uncertainty | belief/map entropy、expected IG | model 错误导致伪信息增益 |
| ObjectGoal/VLN directed | 提升找到目标/路线的概率 | semantic map、goal potential、instruction progress | semantic bias、目标先验过强 |
| downstream perception | 为 reconstruction/recognition/pose 等收集证据 | feature/episodic memory、task proxy | proxy 提升不等于 navigation success |

SemExp/PONI 提供 goal-conditioned semantic exploration；Exploring Exploration 强调不同 exploration objective 对下游任务的优劣不一致。回答时应先说最终任务，再选 coverage/IG/goal score，不能从“active”二字推出统一最优目标。

## 11. Revisit、Stuck 与 Unreachable Frontier

| 现象 | 可观测证据 | 正确处理 | 错误处理 |
| --- | --- | --- | --- |
| deliberate revisit | 新 view angle、loop recovery、目标概率/IG上升 | 允许并记录收益 | 所有 revisit 一律禁止 |
| oscillation | action n-gram重复、pose progress近0、同两 frontier 交替 | cooldown、局部重规划、切换 candidate | 继续累计相同 reward |
| collision/stuck | collision count、odom/map progress、controller timeout | stop/rotate/recover，必要时 blacklist | 只换 random seed |
| unreachable frontier | planner disconnected、inflation后无路径 | reject component、记录 map revision/reason | 把 unknown/obstacle 改成 free |
| stale frontier | map revision/age不匹配 | invalidate、重抽取、重算 distance/score | 静默复用旧坐标 |

revisit novelty 可采用显式单调衰减示例 `N(n)=1/sqrt(1+n)`；probe 在访问次数 `0,1,4` 时得到 `1,0.707107,0.447214`。这只是可测试的 policy contract，不是声称论文都使用该公式。

## 12. Coverage、Visitation 与 Revisit 评估合同

唯一覆盖率可写为：

\[
C_t=\frac{|\mathcal V_t\cap\mathcal E|}{|\mathcal E|},
\qquad
\mathcal V_t=\bigcup_{\tau\le t}\operatorname{VisibleCells}(o_\tau),
\]

变量解释：`E` 是协议冻结的 explorable ground-truth cells，`V_t` 是截至预算 `t` 真正被 sensor visibility 看到的 cell union。若只用预测 map 的 explored channel，指标会与 mapper 自己的错误耦合；应同时报告 noise-free GT visibility 与 agent-estimated coverage。OccupancyAnticipation fixed code 的 `measure_area_seen_performance` 把 explored/free/occupied cell 数乘 `map_scale²` 得到面积，这是 area seen，不自动等于归一化 coverage ratio。

| 指标 | 必须冻结 | 不能混淆 |
| --- | --- | --- |
| coverage / area seen | GT explorable mask、visibility ray/depth、cell size、step/time/path budget、unique union、noise setting | predicted explored probability、走过的 path area |
| visitation | reference pose/object/view set、distance/angle threshold、去重规则、stop requirement、episode denominator | 单纯 coverage 或 object detector recall |
| revisit ratio | cell/view quantization、最小时间间隔、repeat 定义、必要 revisit 标签 | trajectory 自交或 raw step count |
| frontier reach rate | accepted candidates、reached tolerance、unreachable/stale/timeout denominator | 只统计成功选择的 frontier |
| exploration efficiency | `C_t` 曲线、AUC、path/time/energy/collision budget | 单一最终 coverage |
| downstream utility | frozen reconstruction/recognition/pose/navigation task 与 checkpoint | intrinsic reward 本身 |

至少按 episode 输出 seed/scene/start、budget、map/sensor/model revision、coverage curve、unique visit、revisit、frontier accept/reject/reach、collision/stuck/reset 与 failure reason。均值还需 bootstrap CI 或 seed dispersion；timeout、zero-likelihood、lost-localization 和 no-frontier episode必须进入 denominator。

## 13. First-divergence Failure Diagnosis

诊断顺序为：`episode/sensor/time → localization/map revision → observation/occupancy semantics → belief update/normalizer → memory write/reset → frontier extraction → reachability/inflation → utility components → planner/controller → metric denominator`。

| 症状 | first divergence 候选 | 首查 artifact | 不应先做 |
| --- | --- | --- | --- |
| coverage 高但找不到目标 | goal probability/semantic memory | goal-score map、semantic FP/FN、view coverage | 直接增大 rollout horizon |
| frontier 反复落在墙后 | unknown/free semantics 或 reachability | occupancy legend、inflation、component/path log | 把 obstacle threshold 调低 |
| 同一区域振荡 | revisit/stuck state 未持久化 | frontier IDs、cooldown、pose/action trace | 只加随机噪声 |
| belief 变 NaN/均匀 | zero likelihood/underflow | log-likelihood、normalizer、dtype | 静默填均匀 posterior |
| reset 后异常好 | hidden/map 泄漏 | episode ID、reset event、cache lifecycle | 报成 memory 能力 |
| map 更新后走向旧目标 | stale frontier/distance cache | map UUID/revision、goal anchor | 归因 planner 不够强 |

## 14. Fail-closed Exploration Pipeline 伪代码

```python
def exploration_step(packet, state, manifest, models, planner):
    # 1. Reject wrong episode, stale sensor packets, or changed model/schema identities.
    assert packet.episode_id == state.episode_id
    if not manifest.sensor_time_valid(packet):
        return stop("invalid_sensor_time")

    # 2. Consume localization/map state only at a declared revision.
    map_state = state.map_store.read(packet.map_uuid, packet.map_revision)
    if map_state is None or not packet.localization_valid:
        state.invalidate_spatial_anchors()
        return stop("map_or_localization_invalid")

    # 3. Update belief; a zero/NaN normalizer fails closed.
    belief = models.belief_update(state.belief, packet.observation, packet.last_action)
    if not belief.finite or belief.normalizer <= manifest.min_normalizer:
        return stop("invalid_belief")

    # 4. Write typed recurrent, spatial, and episodic memory under this revision.
    state.update_memory(packet, belief, map_state)

    # 5. Extract known-free/unknown boundaries, then enforce reachability and risk.
    frontiers = extract_frontiers(map_state.observed_free, map_state.unknown)
    candidates = []
    for frontier in cluster(frontiers):
        view = project_to_reachable_free(frontier, map_state)
        if view is None or state.in_cooldown(view) or state.is_stale(view):
            continue
        score = component_utility(view, belief, state, map_state)
        if score.risk <= manifest.hard_risk_limit:
            candidates.append((score.total, view))

    # 6. No valid frontier is an explicit terminal/recovery state, not a random action.
    if not candidates:
        return recover_or_stop("no_valid_frontier")

    goal = max(candidates)[1]
    plan = planner.plan(packet.pose, goal, map_state.inflated_known_free)
    if not plan.reachable:
        state.blacklist(goal, reason="unreachable", map_revision=packet.map_revision)
        return recover_or_stop("unreachable_frontier")

    # 7. Execute a bounded prefix; replan after progress, collision, or map revision change.
    return execute_bounded(plan, progress_watchdog=True, revision_guard=True)
```

此伪代码是目标合同，不是五项目已有实现。生产系统还需并发 map write、queue/backpressure、log-domain belief、particle degeneracy、multi-robot map merge、dynamic obstacle、semantic conflict、watchdog 与 emergency stop。

## 15. 十个 Deterministic Probes

| Probe | 固定输入 | 结果 | 教学结论 |
| --- | --- | --- | --- |
| Bayes update | prior `[.6,.4]`，likelihood `[.2,.8]` | `[.272727,.727273]` | predict/correct/normalize不可少 |
| zero likelihood | likelihood全0 | gate=`false` | 不伪造 posterior |
| information gain | binary prior `.5`，symmetric accuracy `.9` | `.531004 bits` | entropy下降需 expectation |
| frontier classification | known-free邻接unknown的4-neighbor grid | `[(1,2),(2,2)]` | frontier 在 free 一侧 |
| unreachable reject | obstacle隔断两块free region | `false` | frontier语义不等于可达 |
| utility argmax | IG/goal/novelty/cost/risk 两候选 | candidate `A` | 分项权衡可复算 |
| revisit decay | visits `0/1/4` | `1/.707107/.447214` | novelty随重复下降 |
| map revision invalidation | record revision `7/8`，current `8` | 只保留 `e1` | spatial anchor必须绑定 revision |
| episode reset | hidden `[3,-2]` | reset为`[0,0]` | 禁止跨 episode 泄漏 |
| local runtime gate | `runtimeReady=false` 或 trace缺失 | 两者均 false | map/interface不等于 exploration runtime |

实际执行得到 `10/10 expected decisions matched`。这些 probe 只验证合同与反例，不是论文 benchmark 复现，也不证明任何本地系统已实现对应模块。

## 16. Public Method → Code Mapping

| 机制 | Fixed source/code | 本页读取到 | 仍需单独验证 |
| --- | --- | --- | --- |
| exact POMDP belief | Kaelbling et al. | belief update与belief-MDP边界 | large-scale neural approximation/calibration |
| classic frontier | Yamauchi；Exploring Exploration frontier agent | known-free/unknown boundary与baseline | map/noise/reachability robustness |
| map + visited + coverage reward | Neural-SLAM `exploration_env.py/main.py` | explored area delta、visited map、global goal、FMM reachable | local checkpoint/run/generalization |
| occupancy anticipation | OccupancyAnticipation `occant.py/metrics.py` | predicted occupancy、entropy filter、area/map quality | predicted-free risk calibration |
| goal-oriented semantic memory | SemExp repo | episodic semantic map、found-goal/global goal | detector bias与本地 ObjectNav result |
| area/object potential | PONI `model.py/pf_exp.py` | semantic-map potential、distance/unexplored masks | 与 classic frontier 不能等同 |
| recurrent history | EmbodiedQA `models.py/train_nav.py` | LSTM hidden、action history、planner/controller | explicit belief/map semantics |
| objective/task comparison | Exploring Exploration paper/repo | frontier/recurrent baseline与 visitation entrypoint | 所有 metrics 的跨协议可比性 |

## 17. 本地五项目 Inventory 与 Direct Audit

### 17.1 Canonical Inventory

| Inventory | Canonical SHA-256 | 当前安全结论 |
| --- | --- | --- |
| [OPD](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | 2D point/box/relation 与 region target coverage；不是 navigation coverage/frontier runtime |
| [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | image/language/action training与sim diagnostics；无 navigation belief/map/frontier trace |
| [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | 消息 history、navigation tool contract、occupancy/map bridge；无 active-exploration policy |
| [WAM](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | video/action/world-model diagnostic；prediction memory不等于 navigation belief |
| [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | simulator state/action 与 DataLoader optimization；不证明 partial-observation navigation memory |

### 17.2 Robot Harness Local-direct Exceptions

| fixed file | SHA-256 | 直接发现 | 不能升级 |
| --- | --- | --- | --- |
| `server/agent/history.py` | `CAD470FC6B00470C37636285A3F84732EBFCDEB824612D0439AA65B70B5FC805` | semantic duplicate turn compaction、tool success/error preference、action-tool history stripping、消息格式转换 | learned memory、Bayesian belief、spatial/episodic navigation memory |
| `server/tools/registry.py` | `EF1AFE36697D16F4C2A1392F618444712A87F2F88EE3BDABE409BD2948D24CF1` | semantic-navigation tool scope、timeout/cancel/compensation入口 | 底层 frontier/exploration algorithm 或真实导航成功率 |
| `server/agent/runtime.py` | `CEE9148C2987DA7FF6839534EBCFED75B953A8678742AD9442523F96A6A77280` | agent/tool runtime orchestration | model内部长期记忆已学会 |
| `server/sim/ros2_bridge.py` | `8291D64DE01AAC2EFDF52409008EFD7AE18C5FEC0BA7B9D4677F6636F8287A48` | occupancy/PCD/reloc map 路径与 pixel/world bridge | visited/frontier/IG/coverage trace |
| `server/sim/acerobotics_sim.py` | `E373090035AADBCBECD7016698175345804194CC727969ECC972AC97CCCE9EBE` | simulator fixture与 localization/map fields | field 来自真实 estimator 或 exploration policy |
| `server/tests/test_acerobotics_ros2_backend.py` | `A0FE082007E68BBFA8CA7A535E67ECBF5935B55DB28C52A449694B3C0773B1FB` | fallback 明确 `runtimeReady=false` | local runtime exploration pass |

定向执行 `python -m pytest -q server/tests/test_history_semantic_compaction.py` 得到 `2 failed, 2 passed, 2 warnings`；失败用例是 semantic duplicate navigation turns 未按预期去重/保留成功 turn。该结果不在本切片修复，因为任务是 source freeze；它证明当前 message-history test 仍有 open failure，也再次说明不能用该文件声称稳定的 embodied memory。

对 `C:\Users\mousongzhe\agent`、`C:\Users\mousongzhe\muxi`、`C:\Users\mousongzhe\Project` 的选定实现路径做 `frontier/information gain/active exploration/belief update/episodic memory/revisit/visited map/coverage` 定向检索：Robot Harness 实现目录无 exact navigation-mechanism 命中；OPD 的 `target_coverage/pred_coverage` 是2D region overlap；Project 的 episodic-memory命中位于独立 `llm_vlm_memory_research` 文稿，不是五项目 navigation runtime。inventory和定向检索不能证明所有远端、历史分支或未同步 artifact 绝对不存在。

## 18. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 最小补强 artifact |
| --- | --- | --- | --- |
| OPD | grounding score可作为 semantic observation 的上游候选 | 已实现 active ObjectNav、navigation coverage提升 | observation→pose/map binding、semantic map/frontier trace、matched episode |
| Robot Harness | runtime message history、导航工具安全合同、map bridge | 模型学会长期 memory、POMDP belief 或 frontier exploration | episode/map manifest、belief/frontier/visited trace、planner/controller log、通过的runtime tests |
| OpenPiVLA | action history/chunk 可讨论 policy temporal context | action model就是 navigation belief/exploration policy | navigation task/sensor/map schema、memory reset、exploration rollout |
| WAM | latent/video prediction可讨论 observation model 候选 | world model等于 calibrated belief 或带来 exploration gain | posterior calibration、active data collection A/B、navigation metric |
| UWM | simulator state/action protocol可用于构造 partial-observation实验 | simulator GT state就是部署 belief、DataLoader memory就是 agent memory | observation masking、belief estimator、map/frontier trace、episode bundle |

安全回答顺序：`public definition → fixed paper/repo → engineering synthesis label → local inventory → local-direct exception → missing runtime/episode → candidate ownership`。源码中出现 `history/map/coverage` 单词、Git author 或 map asset 都不能替代机制、结果和个人贡献证据。

## 19. Source Gate 与下一切片

本轮已关闭：

- 八份 primary paper 的固定版本、SHA、全文完整性与代表页视觉检查；
- 六个 official repo 的 fixed commit/date/license 与36个核心文件逐字节 SHA；
- POMDP belief、zero-likelihood fail-closed、四类 state 与三类 memory 的边界；
- known-free/unknown frontier、reachability、map revision、revisit/stuck/unreachable contract；
- IG/goal/coverage/novelty/cost/risk 的综合 utility，并明确它是工程综合而非单篇原公式；
- coverage/visitation/revisit/frontier reach 的 metric identity 与 denominator；
- 10个 deterministic probes，全部命中预期；
- 五份 canonical inventory、Robot Harness 六个 local-direct exceptions、一个 `2 failed / 2 passed` history test 与定向负证据。

仍为 `WARN`：本地没有 transition/observation model revision、calibrated belief、recurrent reset/ablation、typed spatial/episodic memory、frontier extractor、visited/coverage trace、map-revision invalidation、unreachable/stuck log、完整 episode denominator、matched exploration A/B、checkpoint 或逐文件候选人 ownership 闭环。primary paper 与 official code不能替代这些 artifact。

下游 [VLA-PER-017 Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html) 与 [Atomic Card](../questions/vol_06_per017.html) 已在各自 bounded slice 同步，card保持 `unseen/WARN`。下一 bounded slice 只冻结 `VLA-PER-018` navigation BC/DAgger/RL/exposure-bias source；不生成其 knowledge/card，不修改 mastery。

## References

1. Kaelbling, Littman & Cassandra, [Planning and Acting in Partially Observable Stochastic Domains](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), Artificial Intelligence, 1998.
2. Yamauchi, [A Frontier-Based Approach for Autonomous Exploration](https://www.robotfrontier.com/papers/cira97.pdf), CIRA, 1997.
3. Chaplot et al., [Learning to Explore using Active Neural SLAM](https://arxiv.org/abs/2004.05155), ICLR, 2020；[official code](https://github.com/devendrachaplot/Neural-SLAM/tree/8876e1eafff5414e92d72347d89488d970a4f6b2).
4. Ramakrishnan et al., [Occupancy Anticipation for Efficient Exploration and Navigation](https://arxiv.org/abs/2008.09285), ECCV, 2020；[official code](https://github.com/facebookresearch/OccupancyAnticipation/tree/aea6a2c0d9701336c01c9c85f5c3b8565d7c52ba).
5. Chaplot et al., [Object Goal Navigation using Goal-Oriented Semantic Exploration](https://arxiv.org/abs/2007.00643), NeurIPS, 2020；[official code](https://github.com/devendrachaplot/Object-Goal-Navigation/tree/5d76902fe9be821926a1de32557ca9a8dc21d0f5).
6. Ramakrishnan et al., [PONI](https://arxiv.org/abs/2201.10029), CVPR, 2022；[official code](https://github.com/srama2512/PONI/tree/30682c2bdcd820eec8f72043b2579eb045d547bf).
7. Ramakrishnan, Jayaraman & Grauman, [An Exploration of Embodied Visual Exploration](https://arxiv.org/abs/2001.02192)；[official code](https://github.com/facebookresearch/exploring_exploration/tree/09d3f9b8703162fcc0974989e60f8cd5b47d4d39).
8. Das et al., [Embodied Question Answering](https://arxiv.org/abs/1711.11543), CVPR, 2018；[official code](https://github.com/facebookresearch/EmbodiedQA/tree/306fd6ef3064b5b9a3bd2d3f06ac96a09c481d9d).
9. [PER-005 Navigation Policy Architecture](vol_06_per005_navigation_policy_architecture_source_freeze.html)、[PER-016 Localization / SLAM](vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html) 与 [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html).
10. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories.
11. [VLA-PER-017 Belief / Memory / Frontier / Active Exploration Knowledge](../knowledge/vol_06_per017_belief_memory_frontier_active_exploration.html).
