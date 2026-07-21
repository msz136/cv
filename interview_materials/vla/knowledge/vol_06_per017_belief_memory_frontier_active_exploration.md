# VOL 06 PER-017：Belief、Memory、Frontier 与 Active Exploration

> 状态：`knowledge_drafted / VLA-PER-017 / source_frozen / card_synced / project_truth_bounded / WARN`  
> 更新日期：2026-07-20  
> 权威来源：[PER-017 Source Freeze](../sources/vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html)  
> 学习边界：本页把已冻结的 POMDP、memory、frontier、active exploration 与 evaluation contract 转化为可学习讲义；下游单张题卡已在独立 bounded slice 同步且保持 `unseen`，不改变 mastery，不进入 PER-018 的 BC/DAgger/RL 训练，也不把公开方法写成本地项目成果。

## 问题（Question）

在 partial observation 的导航中，机器人如何用 belief 和不同形态的 memory 汇总历史，怎样从 occupancy map 提取可达 frontier，怎样权衡 information gain、目标概率、coverage、路程和风险，以及怎样诊断 revisit、stuck、unreachable frontier 和 stale map memory？

## 1. 学习出口

学完本页，面试中应能完成六件事：

1. 用 POMDP 语言严格区分 hidden state、observation、action、history、belief 与 policy。
2. 解释 recurrent latent、explicit spatial map、episodic history 三种 memory 的信息、优缺点和 reset/invalidation 条件。
3. 写出 Bayes belief update，并说明 zero-likelihood、underflow、model mismatch 时为什么必须 fail closed。
4. 从 `known-free / unknown / occupied / predicted-free` 地图语义出发，讲清 frontier extraction、聚类、可达性和 risk gate。
5. 把 information gain、goal probability、coverage/novelty、travel cost 与 risk 拆成可审计的 utility，而不是只说“探索未知区域”。
6. 给出 coverage/visitation/revisit/frontier-reach 的评估合同，并守住五项目“只有接口、没有 exploration runtime”的真实性边界。

## 2. 一分钟心智模型

```text
hidden environment state s_t
        ↓ 只产生局部 observation o_t
Bayes / learned belief update + typed memory write
        ↓
belief + recurrent latent + spatial map + episodic events
        ↓
known-free / unknown boundary → frontier components
        ↓
reachability + freshness + risk hard gates
        ↓
IG + goal probability + coverage + novelty - distance - risk
        ↓
choose frontier/viewpoint → bounded plan prefix → observe again
        ↓
progress/revisit/stuck/map-revision watchdog → replan or stop
```

最重要的顺序是：**先确认信息状态可信，再产生探索候选；先做 hard gate，再做 soft ranking；执行有限前缀后重新观测，而不是一次规划到底。**

## 3. POMDP：为什么不能只看当前帧

部分可观测马尔可夫决策过程（Partially Observable Markov Decision Process, POMDP）可写为：

\[
\mathcal M=
\langle \mathcal S,\mathcal A,T,\mathcal O,Z,R,\gamma\rangle,
\qquad
b_t(s)=P(s_t=s\mid o_{1:t},a_{1:t-1}).
\]

变量解释：`S` 是真实但不可完全读取的环境状态；`A` 是动作；`T` 是状态转移；`O` 是观测空间；`Z` 是 observation likelihood；`R` 是 reward；`γ` 是折扣；`b_t` 是给定历史后的 state posterior。直觉上，当前图像可能看不到门后、被遮挡目标或累计定位误差，因此策略需要一个 information state。实现映射：belief record 必须绑定 `episode_id`、observation/action schema、transition/observation model revision、timestamp 与 normalization；只有一个 RNN hidden tensor 不能自动满足这些语义。

| 量 | 回答的问题 | 导航例子 | 常见误写 |
| --- | --- | --- | --- |
| hidden state `s_t` | 世界真实是什么 | 真实 pose、完整障碍、目标位置 | 把 simulator GT 当部署输入 |
| observation `o_t` | 此刻传感器看到了什么 | RGB-D、IMU、局部 collision | 把一帧图像当完整 state |
| history `h_t` | 过去发生过什么 | observation/action/result 序列 | 不记录 episode/time/revision |
| belief `b_t` | 基于模型和历史，现在相信什么 | pose/object/map posterior | 把任意 feature 称为概率 belief |
| policy `π` | 根据 information state 做什么 | 选 frontier、waypoint 或 stop | belief update 与 action head 混为一层 |

## 4. Bayes Belief Update 与 Zero-likelihood Gate

离散 belief update 分为 prediction、correction 与 normalization：

\[
\bar b_t(s')=
\sum_s T(s'\mid s,a_{t-1})b_{t-1}(s),
\qquad
\tilde b_t(s')=Z(o_t\mid s',a_{t-1})\bar b_t(s'),
\qquad
b_t(s')=\frac{\tilde b_t(s')}{\sum_x\tilde b_t(x)}.
\]

变量解释：`\bar b_t` 是动作后的 prior，`\tilde b_t` 是乘 observation likelihood 后的未归一化 posterior，分母是 evidence/normalizer。直觉上，动作模型先把可能状态向前传播，传感器再排除与观测不一致的状态。实现映射：source probe 使用 prior `[0.6,0.4]`、likelihood `[0.2,0.8]`，得到 posterior `[0.272727,0.727273]`；代码必须检查 finite、sum>阈值和 model/schema revision。

### 4.1 为什么不能把全零 likelihood 变成均匀分布

若 `\sum_x\tilde b_t(x)=0`，可能原因包括：observation model 覆盖不全、单位/坐标错误、数值下溢、错误 episode、传感器异常或真实状态不在 hypothesis set。静默改成均匀分布会把模型错误伪装成“高不确定性”，随后策略仍可能输出危险动作。

正确路径是：

- 返回 `invalid_belief`，保留 last-safe belief 但标记 stale；
- 切到 log-domain 或扩大 hypothesis set，仅在数学原因明确时恢复；
- 请求新 observation、relocalization 或 safe-stop；
- 记录 normalizer、model revision、packet identity 与 rejected reason。

### 4.2 Log-domain 实现

对小概率连乘，可用 log-sum-exp：

\[
\log b_t(s')=
\log Z(o_t\mid s',a_{t-1})+
\operatorname{LSE}_{s}
\left(\log T(s'\mid s,a_{t-1})+log b_{t-1}(s)\right)
-\log \eta_t.
\]

变量解释：`LSE` 是 log-sum-exp，`η_t` 是归一化常数。直觉是把概率乘法变成 log 空间加法，避免浮点下溢。实现映射：需要对 impossible transition 使用 `-inf`、对 all-`-inf` row 单独 gate，并在 normalize 后验证 `logsumexp(log_b)=0`；本地五项目没有该实现证据，因此这里只是标准工程合同。

## 5. Memory 不是一个模块名

### 5.1 Recurrent latent memory

\[
h_t=f_\theta(h_{t-1},e(o_t),e(a_{t-1})).
\]

变量解释：`h_t` 是 GRU/LSTM/Transformer cache 等 recurrent state，`e(·)` 是 observation/action encoder。直觉是把长历史压成固定维向量。实现映射：EmbodiedQA official code 使用 action/visual history 与 LSTM hidden state；但若没有 hidden reset、sequence truncation、rollout ablation 和 calibration，不能说 `h_t` 等价于显式 belief 或地图。

优点：紧凑、端到端可学习、可表达难以手工设计的历史特征。缺点：语义不透明、容量有限、容易 episode leakage、难以做 map revision invalidation，也未必表达多模态 uncertainty。

### 5.2 Explicit spatial memory

空间地图至少应拆成：

| Layer | 语义 | 必要身份 | 典型 consumer |
| --- | --- | --- | --- |
| observed occupancy | 直接观测的 free/occupied | sensor/model/time/map revision | collision gate、planner |
| predicted occupancy | anticipation 的 free/occupied probability | checkpoint/calibration/domain | soft utility、risk estimate |
| known/explored | 是否真正进入 sensor visibility | visibility model/cell size | frontier、coverage metric |
| semantic | category/object/affordance score | class vocabulary/checkpoint | ObjectGoal utility |
| visited | agent真正到达或观测过的位置 | pose/frame/time quantization | novelty、revisit/stuck |
| uncertainty | pose/map/semantic confidence | estimator/calibration revision | IG、hard risk gate |

最危险的混淆是：`unknown`、padding、outside-map、传感器不可见、概率0.5 与 anticipation 的 predicted-free 被编码成同一个数。经典 frontier 只能从 **observed known-free** 一侧产生；predicted-free 最多在额外 risk budget 下辅助排序或扩展规划。

### 5.3 Episodic / history memory

episodic memory 记录“何时、何地、看到了什么、做了什么、结果怎样”，最小字段为：

```json
{
  "episode_id": "...",
  "event_id": "...",
  "timestamp_ns": 0,
  "pose_frame_revision": ["map", "map_revision"],
  "observation_ref": "content-addressed artifact",
  "action_and_result": {},
  "belief_or_map_delta_ref": "...",
  "confidence_and_failure_reason": {},
  "producer_model_revision": "..."
}
```

文本对话压缩也属于 history management，但只有当记录绑定 navigation observation、pose/map revision、action/result 与 episode lifecycle 时，才可升级为 embodied episodic memory。

## 6. Typed Exploration State Manifest

```json
{
  "episode_contract": {
    "episode_id_seed_scene_start_goal": [],
    "reset_timestamp_ns": 0,
    "step_time_path_energy_budget": [],
    "termination_and_stop_contract": "..."
  },
  "belief_contract": {
    "state_hypothesis_schema": "...",
    "transition_observation_model_revision": [],
    "normalizer_log_evidence_calibration": [],
    "validity": "valid | stale | zero_likelihood | divergent"
  },
  "memory_contract": {
    "recurrent_hidden_revision_and_reset": [],
    "spatial_map_uuid_revision_layers": [],
    "episodic_event_store_revision": [],
    "capacity_compaction_and_invalidation": "..."
  },
  "frontier_contract": {
    "observed_free_unknown_occupied_predicted_free_legend": {},
    "connectivity_inflation_component_min_size": [],
    "frontier_id_map_revision_age": [],
    "reachable_viewpoint_and_distance_field_revision": []
  },
  "utility_contract": {
    "information_gain_goal_coverage_novelty": [],
    "travel_time_energy_collision_localization_risk": [],
    "hard_reject_thresholds_before_soft_weights": []
  },
  "evaluation_contract": {
    "gt_visibility_explorable_mask_cell_size": [],
    "coverage_visitation_revisit_frontier_reach": [],
    "failure_denominator_confidence_interval": []
  }
}
```

这个 manifest 的价值不是“字段多”，而是阻止跨 episode、跨 map revision、跨 checkpoint 和跨 metric protocol 的静默拼接。任何 frontier score 若缺 `map_revision + distance_field_revision + observation age`，都不能安全复用。

## 7. Memory 生命周期与 Invalidation

| 事件 | recurrent latent | spatial map | episodic history | frontier / cache |
| --- | --- | --- | --- | --- |
| episode reset | 强制清零或新 sequence token | 新 map/session 或显式复用门 | 新 episode namespace | 全量失效 |
| map revision update | 通常重编码相关 context | 按 delta 更新并保留 revision | 旧 event 保留但坐标锚点标 stale | 重抽取 frontier、重算 distance |
| global localization jump | 清除 pose-sensitive hidden 或重对齐 | 更新 frame transform | 记录 correction event | 旧 goal/viewpoint失效 |
| sensor/calibration change | hidden revision不兼容 | 重投影或新 layer | 新 producer revision | visibility/IG cache失效 |
| semantic checkpoint change | semantic hidden不兼容 | semantic layer新 revision | 保留旧预测但不可直接融合 | goal probability重算 |
| clock discontinuity | sequence断开 | observation age不可用 | 新 time segment | stale-age gate失败 |

不要删除历史来伪装一致性：旧 episodic event 可以保留作为审计证据，但 consumer 必须看到它的 revision 已 stale。空间 memory 的“可变当前状态”和 episodic memory 的“不可变事件记录”应分开。

## 8. Frontier 的严格定义

对 occupancy map `M` 与邻域 `N(c)`：

\[
\mathcal F(M)=
\{c\mid M(c)=\mathrm{known\mbox{-}free},\ 
\exists c'\in\mathcal N(c):M(c')=\mathrm{unknown}\}.
\]

变量解释：frontier cell `c` 本身位于已观测安全一侧，至少有一个邻居仍是 unknown。直觉是机器人站在“已知地板边缘”向未知看，而不是把未知格直接设成 goal。实现映射：source 的4-neighbor probe 在固定网格上得到 `[(1,2),(2,2)]`；代码必须冻结4/8 connectivity、unknown legend、map bounds 与 obstacle inflation。

### 8.1 Frontier extraction pipeline

```python
def extract_reachable_frontiers(map_state, pose, contract):
    # 1. Keep observed-free separate from anticipated/predicted-free.
    observed_free = map_state.observed_free
    unknown = map_state.unknown

    # 2. Inflate occupied cells by the robot footprint and safety margin.
    traversible = inflate_and_subtract_obstacles(
        observed_free,
        map_state.observed_occupied,
        contract.robot_radius_and_margin,
    )

    # 3. A frontier lies on the traversible side adjacent to unknown cells.
    frontier_mask = traversible & dilate(unknown, connectivity=contract.connectivity)

    # 4. Cluster components; reject tiny/noisy/stale components.
    components = connected_components(frontier_mask)
    components = [c for c in components if c.area >= contract.min_component_area]

    # 5. Project each component to a reachable free viewpoint, not an unknown centroid.
    reachable = []
    for component in components:
        view = select_reachable_viewpoint(component, traversible, pose)
        if view is not None and view.map_revision == map_state.revision:
            reachable.append(view)
    return reachable
```

代码注释对应五道 gate：map semantics、footprint inflation、boundary extraction、component denoise、reachable view projection。Yamauchi 支持 classic frontier 定义；PONI 的 potential policy可以使用 unexplored/distance maps，但 fixed code 的 `needs_frontier_maps=False`，不能把二者说成同一实现。

## 9. Information Gain：探索什么不确定性

\[
H(b_t)=-\sum_s b_t(s)\log b_t(s),
\qquad
\operatorname{IG}(a)=
H(b_t)-\mathbb E_{o\sim P(o\mid b_t,a)}[H(b_{t+1})].
\]

变量解释：`H` 是 entropy，`IG(a)` 是执行 action 后预期减少的 uncertainty。直觉是一个 viewpoint 的价值来自“预计能排除多少假设”，不是它离未知区域有多近。实现映射：source probe 的均匀二状态 prior、准确率0.9对称 observation model 得到 `0.531004 bits`；实际系统还要说明 entropy 属于 pose、occupancy、object location 还是 task feature，它们不能直接相加。

常见近似：

- 对 occupancy cells 求独立 Bernoulli entropy，但要承认忽略 cell correlation；
- 用 ensemble/dropout disagreement 近似 epistemic uncertainty，但不等于 calibrated posterior；
- 用预期新增可见 cell 数近似 coverage gain，它不是严格 IG；
- 用 downstream reconstruction/recognition improvement 作为 task utility，不能改名成 navigation success。

## 10. 综合 Exploration Utility：先 Gate，后 Rank

通过 hard gate 后，可用综合 utility：

\[
U(f)=
w_I\operatorname{IG}(f)+w_g p_{\mathrm{goal}}(f)
+w_c\Delta C(f)+w_nN(f)
-w_dd(f)-w_eE(f)-w_r\operatorname{Risk}(f).
\]

变量解释：`f` 是 frontier/viewpoint；`ΔC` 是预期 coverage gain；`N` 是 novelty；`d` 是 path/time cost；`E` 是 energy；`Risk` 汇总 collision、localization、predicted-free 与 uncertainty。直觉是“信息多、接近任务、覆盖新区域、代价低且风险可控”的候选更好。实现映射：这是本页对多篇来源的 **工程综合**，不是 PONI、Active Neural SLAM 或任何单篇论文的逐字公式；配置必须记录每项单位、归一化、weight 与 hard threshold。

### 10.1 为什么 risk 不能只做负权重

如果一个候选超过 collision/localization/safety hard limit，它应被 reject；否则极高的 IG 或 goal probability 可能在加权和里“买掉”安全约束。正确结构是：

```text
schema/revision valid
  AND localization/map valid
  AND reachable in inflated observed-free
  AND risk <= hard_limit
  AND not stale/blacklisted
      → only then compute soft utility and argmax
```

### 10.2 目标导向与任务无关探索

| 目标 | 主要 score | 适合 | 典型偏差 |
| --- | --- | --- | --- |
| coverage | 新增可见区域 | 建图、无任务巡检 | 看得多但不解决任务 |
| information gain | uncertainty reduction | localization/map/object消歧 | observation model错会产生伪 IG |
| semantic goal | object/room potential | ObjectGoal | detector/commonsense prior bias |
| downstream task | reconstruction/recognition/pose proxy | active perception | proxy好不等于导航成功 |

Exploring Exploration 的核心启示是：不同 exploration objective 对 downstream task 的排序可能不同；应先冻结最终任务，再选择 intrinsic objective。

## 11. 公开方法如何放进同一张图

| 方法 | memory / information state | 高层探索决策 | 本页应记住的边界 |
| --- | --- | --- | --- |
| classic frontier | occupancy known/unknown map | 去 free/unknown 边界 | 定义清晰，但依赖地图与可达性 |
| Active Neural SLAM | learned map + explored/visited + pose | global goal，local planner执行 | learned mapper不等于 calibrated belief |
| Occupancy Anticipation | observed + anticipated occupancy memory | 加快 area seen / navigation | predicted-free不能自动进入安全层 |
| SemExp | episodic semantic map | goal-conditioned long-term goal | detector bias会污染 memory/utility |
| PONI | semantic map + area/object potential + distance | potential peak/global goal | potential policy不等于 classic frontier extractor |
| EmbodiedQA navigator | recurrent visual/action history | LSTM planner/controller | recurrent hidden不等于 explicit map/belief |

方法选择不是“learned 比 classic 高级”：如果 map semantics、revision 和 reachability可审计，classic frontier很强；如果目标语义重要，需要 semantic map/potential；如果 observation model与分布可靠，可加入 anticipation/IG；如果真实部署缺少可靠不确定性，宁可保守 fail closed。

## 12. Revisit、Stuck 与 Unreachable Frontier

revisit 不应一刀切。loop recovery、换视角确认目标、从死路返回都可能是合理 revisit；问题是“重复是否带来新信息或任务进展”。

一种可测试的 novelty 衰减为：

\[
N(c;n_c)=\frac{1}{\sqrt{1+n_c}},
\qquad
\operatorname{progress}_t=
d_{\mathrm{plan}}(x_{t-k},g)-d_{\mathrm{plan}}(x_t,g).
\]

变量解释：`n_c` 是 cell/view 的有效访问次数，`progress_t` 是过去 `k` 步规划距离减少量。直觉是访问越多 novelty 越低；若动作持续执行但 goal distance 不下降，则可能 stuck。实现映射：source probe 在 `n=0,1,4` 时得到 `1,0.707107,0.447214`；部署还需 cell/view quantization、最小 revisit 间隔、collision 与 odometry confidence。

| 状态 | 判据组合 | 动作 |
| --- | --- | --- |
| useful revisit | 新 view、IG/goal score上升、progress恢复 | 允许，记录收益原因 |
| oscillation | action n-gram重复、两 frontier交替、progress≈0 | cooldown、切 candidate、局部恢复 |
| physical stuck | collision/actuation timeout、pose近似不变 | safe recovery或stop |
| unreachable | inflated graph disconnected、planner fail | blacklist component+revision |
| stale target | frontier/map/distance revision不一致 | invalidate并重抽取 |
| no valid frontier | 全部被 gate、地图封闭或传感器失败 | explicit terminal/relocalize，不随机撞 |

## 13. Coverage、Visitation、Revisit 与效率

唯一 coverage ratio 为：

\[
C_t=
\frac{|\mathcal V_t\cap\mathcal E|}{|\mathcal E|},
\qquad
\mathcal V_t=
\bigcup_{\tau\le t}\operatorname{VisibleCells}(o_\tau).
\]

变量解释：`E` 是 ground-truth explorable cells，`V_t` 是截至预算 `t` 真正进入 sensor visibility 的 cell union。直觉是只计算“看见过的唯一可探索区域”，不是走过的 path footprint。实现映射：OccupancyAnticipation official metrics 将 explored/free/occupied cell count 乘 `map_scale²` 得到 area seen；若要 coverage ratio，还必须冻结 GT denominator、visibility model、cell size 和 noise setting。

revisit ratio 可写为：

\[
R_{\mathrm{visit}}=
\frac{\sum_{t=1}^{T}\mathbb 1[n(q(x_t))>0]}{T},
\]

变量解释：`q(x_t)` 把 pose/view quantize 到协议单元，分子统计访问已出现单元的 step。直觉是衡量轨迹有多少重复，但它不能区分必要返回和无效振荡。实现映射：必须冻结 quantization resolution、时间间隔、view orientation、teleport/reset 和 denominator；最好再报告 `useful_revisit` 标签或 revisit 后的 IG/progress。

| 指标 | 最小协议身份 | 回答什么 |
| --- | --- | --- |
| area seen / coverage | GT mask、visibility、cell size、budget | 看了多少唯一空间 |
| visitation | reference pose/object/view、阈值、stop | 覆盖了哪些任务相关观察位 |
| revisit ratio | quantization、间隔、必要性标签 | 重复程度及是否有效 |
| frontier accept/reach | accepted/rejected/reached denominator | 候选生成与执行是否一致 |
| coverage AUC | step/time/path/energy axis | 同预算下探索效率 |
| collision/stuck/no-frontier | failure definition和episode denominator | 安全与恢复性 |

平均值不能隐藏失败：应保留每 episode curve、seed/scene/start、timeout、zero-likelihood、lost-localization、no-frontier 与 stuck reason，并报告 seed dispersion 或 confidence interval。

## 14. 十个可手算 / 可编码 Probe

| # | Probe | Expected | 面试意义 |
| ---: | --- | --- | --- |
| 1 | 两状态 Bayes update | `[.272727,.727273]` | 会算 predict/correct/normalize |
| 2 | likelihood全0 | fail closed | 不伪造 posterior |
| 3 | binary IG | `.531004 bits` | 会算 expected entropy reduction |
| 4 | frontier grid | `[(1,2),(2,2)]` | frontier 在 known-free 一侧 |
| 5 | 障碍隔断 frontier | unreachable | 语义候选还需 graph gate |
| 6 | 综合 utility 两候选 | candidate A | 分项和单位可复算 |
| 7 | revisit count `0/1/4` | `1/.707107/.447214` | novelty单调下降 |
| 8 | map revision `7/8` | 只保留 current `8` | stale anchor失效 |
| 9 | episode reset hidden `[3,-2]` | `[0,0]` | 防止 leakage |
| 10 | `runtimeReady=false` 或 trace缺失 | local gate false | interface/map不等于 runtime |

source freeze 已实际执行并得到 `10/10 expected decisions matched`。这些 probe 用于验证概念合同，不是论文复现，不允许被写成本地项目 benchmark。

## 15. First-divergence 诊断

固定顺序：

```text
episode/sensor/time
  → localization/map revision
  → observed/predicted/unknown semantics
  → belief update/normalizer
  → memory write/reset/invalidation
  → frontier extraction/component
  → inflation/reachability/freshness/risk
  → utility components and weights
  → planner/controller/progress watchdog
  → metric visibility/denominator
```

| 症状 | first divergence | 首查证据 | 常见误诊 |
| --- | --- | --- | --- |
| belief NaN或突然均匀 | likelihood/normalizer/model mismatch | log evidence、schema、dtype、packet | “模型不确定所以正常” |
| frontier在墙后 | map legend/inflation/reachability | observed-free mask、footprint、path graph | planner不够强 |
| 反复去同一区域 | visited/revisit/cooldown未持久化 | frontier ID、visit count、action/pose trace | 加随机噪声即可 |
| reset后成绩异常好 | hidden/map跨episode泄漏 | reset log、episode namespace | memory能力强 |
| coverage高但目标失败 | semantic goal score/visibility mismatch | semantic FP/FN、goal map、view coverage | 继续增加coverage reward |
| map更新后走旧目标 | stale revision/distance cache | map/frontier/goal revisions | controller延迟 |
| 无 frontier | 真正探索完成或全候选被gate | rejection reasons、map bounds、sensor state | 随机走一步试试 |

## 16. Fail-closed Active Exploration Pipeline

```python
def active_exploration_step(packet, state, models, planner, contract):
    # 1. Validate episode, clock, sensor schema, localization and map revision.
    if not contract.packet_valid(packet, state):
        return safe_stop("invalid_packet_or_revision")

    # 2. Update belief; zero/NaN evidence is an explicit invalid state.
    belief = models.update_belief(state.belief, packet)
    if not belief.finite or belief.normalizer <= contract.min_evidence:
        return relocalize_or_stop("invalid_belief")

    # 3. Write recurrent, spatial and episodic memory with immutable identities.
    state.memory.write(packet, belief)

    # 4. Build frontiers only from observed known-free adjacent to unknown.
    frontier_views = extract_reachable_frontiers(
        state.spatial_map,
        packet.pose,
        contract.frontier,
    )

    # 5. Apply hard freshness/reachability/risk gates before any weighted score.
    valid = [
        f for f in frontier_views
        if state.fresh(f)
        and not state.cooldown_or_blacklisted(f)
        and contract.risk(f, state) <= contract.hard_risk_limit
    ]
    if not valid:
        return recover_or_stop("no_valid_frontier")

    # 6. Rank valid candidates using auditable utility components.
    goal = max(valid, key=lambda f: component_utility(f, belief, state, contract))
    plan = planner.plan(packet.pose, goal, state.spatial_map.inflated_observed_free)
    if not plan.reachable:
        state.blacklist(goal, packet.map_revision, reason="unreachable")
        return recover_or_stop("unreachable_frontier")

    # 7. Execute a bounded prefix, then re-observe and replan on any revision/progress event.
    return execute_prefix(plan, watchdogs=["progress", "collision", "revision"])
```

这段伪代码体现面试回答的主线：belief valid → typed memory → frontier → hard gate → utility → bounded execution → watchdog。它是目标架构，不是五项目现有代码。

## 17. 本地五项目真实性边界

| 项目 | 能安全挂钩 | 不能升级 | 面试中的安全说法 |
| --- | --- | --- | --- |
| OPD | 2D grounding/region score可作为 semantic observation 候选 | active ObjectNav、frontier runtime、navigation coverage uplift | “我能解释 grounding 如何进入 semantic map，但项目没有该闭环证据” |
| Robot Harness | message history、navigation tool安全合同、occupancy/map bridge | learned belief、spatial/episodic navigation memory、active exploration | “当前证据是 runtime接口，不是模型记忆或探索算法” |
| OpenPiVLA | image/state/action history与chunk contract | navigation belief/frontier policy | “temporal context 不等于 POMDP belief” |
| WAM | future/video prediction可讨论 observation model 候选 | calibrated posterior 或 exploration gain | “world prediction 要经 calibration和active A/B 才能支持该claim” |
| UWM | simulator state/action可构造 partial-observation实验 | GT state等于部署belief、DataLoader memory等于agent memory | “当前只支持协议设计，不支持在线探索结果” |

Robot Harness `history.py` 的 source-freeze 定向测试为 `2 failed, 2 passed, 2 warnings`，因此连 message compaction 都要带当前失败边界。项目回答顺序固定为：`公开定义 → fixed paper/code → 本地直接证据 → inference → missing artifact → 个人ownership`。

## 18. 两档面试回答

### 18.1 约30秒回答

partial observation 下我不会把当前帧当 state，而是维护 belief 和 typed memory。belief 用 transition 与 observation likelihood 做 Bayes update；normalizer 为0就停止或重定位。空间图要区分 observed free、unknown、occupied 和 predicted free，frontier 是 free 邻接 unknown 的边界。候选先过 revision、可达性和风险硬门，再按信息增益、目标概率、coverage/novelty减去路程和风险排序；执行有限前缀后根据 revisit、stuck 和 map revision 重规划。

### 18.2 约2分钟机制回答

我会先把系统写成 POMDP：真实 state 不可直接读取，策略消费的是由 observation/action history 得到的 belief。memory 分三层：RNN hidden 压缩历史，explicit map 保存 occupancy/semantic/visited/uncertainty，episodic store 保存带 episode、时间、pose/map revision 的 observation-action-result。Bayes update 必须检查 evidence；zero-likelihood、NaN 或 model revision 不匹配要 fail closed。frontier 只从 inflated observed-free 与 unknown 的边界抽取，component centroid还要投影到真实可达 viewpoint。通过 freshness、reachability、collision/localization risk 等硬门后，才用 IG、goal probability、预期coverage、novelty、path/time/energy cost 做 soft ranking。执行时只跑 plan prefix，并监控 progress、collision、两点振荡、revisit收益与 map revision；旧 frontier、distance field 和坐标锚点必须失效。评估至少冻结 GT visibility、cell size、预算和 denominator，分开报 coverage、visitation、revisit、frontier reach、collision/stuck。当前五项目只有接口或上游观测证据，没有本地 active-exploration runtime，所以我不会声称个人导航指标。

## 19. 高频追问与答题抓手

| 追问 | 回答抓手 |
| --- | --- |
| RNN hidden 为什么不一定是 belief？ | 没有概率语义、model identity、normalization、calibration与多模态保证 |
| explicit map 与 belief 谁更好？ | 不是二选一；map可解释，belief表达不确定性，recurrent latent压缩非结构信息 |
| frontier 为什么在 free 一侧？ | robot goal必须是当前已知可站立位置，unknown只是预期可观测区域 |
| predicted-free 能否直接规划？ | 只能在独立 risk/calibration门下使用，不能冒充 observed-free |
| coverage 与 IG 有什么区别？ | coverage计新增可见空间，IG计 posterior entropy预期下降 |
| revisit 一定不好吗？ | 不；关键看是否带来新信息、恢复进展或必要返回 |
| no frontier 怎么办？ | 区分探索完成、map/sensor错误、全部候选被gate，显式stop/relocalize |
| map revision 后哪些状态失效？ | frontier ID、goal/viewpoint、distance cache、visited坐标锚点、pose-sensitive hidden |
| 如何证明 exploration 好？ | frozen budget 下 coverage/AUC、task utility、failure denominator、matched A/B 与 episode trace |
| 你的项目实现了吗？ | 当前没有 direct runtime/episode证据，只能讲接口与设计迁移条件 |

## 20. 常见错误

1. 把 simulator GT state 写成部署 belief。
2. 把 action/image history tensor 直接称为长期记忆。
3. 把 unknown、unseen、概率0.5、padding和 predicted-free 混成一个 map value。
4. 把 frontier target 放在 unknown 或 obstacle cell 中。
5. 用高 information gain 抵消 collision risk hard limit。
6. 把所有 revisit 都惩罚，导致无法绕障或回到关键观察位。
7. map revision 后继续用旧 frontier/distance cache。
8. 用预测 map 的 explored channel同时做策略输入和唯一评估真值。
9. 只报最终 coverage，不报 budget curve、failure denominator和scene/seed分布。
10. 把 official repo、字段名、map asset 或本地 history 管理说成个人 active-exploration成果。

## 21. 本页证据边界与下一步

本页已把 source freeze 转成可学习知识：POMDP/belief、zero-likelihood、三类memory、typed manifest、frontier extraction、IG/utility、revisit/stuck/unreachable、metric contract、10 probes、诊断树、伪代码、两档回答和五项目truth boundary均已覆盖。

仍为 `WARN`：没有独立 fact-review、真实口述、PER-017 atomic card、本地 calibrated belief、typed exploration trace、matched A/B、checkpoint/episode bundle 或候选人 ownership闭环。页面生成不改变 mastery。

下游 [VLA-PER-017 Atomic Card](../questions/vol_06_per017.html) 已在独立 bounded slice 同步，短答、机制答、诊断、追问与五项目边界保持 `unseen/WARN`。下一 bounded slice 只冻结 `VLA-PER-018` navigation BC/DAgger/RL/exposure-bias source；不生成其 knowledge/card，不创建 coaching state。

## References

1. [PER-017 Source Freeze](../sources/vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html)：八份论文、六个 fixed official repo/36文件、10 probes 与五项目证据边界。
2. Kaelbling, Littman & Cassandra, [Planning and Acting in Partially Observable Stochastic Domains](https://people.csail.mit.edu/lpk/papers/aij98-pomdp.pdf), Artificial Intelligence, 1998.
3. Yamauchi, [A Frontier-Based Approach for Autonomous Exploration](https://www.robotfrontier.com/papers/cira97.pdf), CIRA, 1997.
4. Chaplot et al., [Learning to Explore using Active Neural SLAM](https://arxiv.org/abs/2004.05155)；[official code](https://github.com/devendrachaplot/Neural-SLAM/tree/8876e1eafff5414e92d72347d89488d970a4f6b2).
5. Ramakrishnan et al., [Occupancy Anticipation for Efficient Exploration and Navigation](https://arxiv.org/abs/2008.09285)；[official code](https://github.com/facebookresearch/OccupancyAnticipation/tree/aea6a2c0d9701336c01c9c85f5c3b8565d7c52ba).
6. Chaplot et al., [Object Goal Navigation using Goal-Oriented Semantic Exploration](https://arxiv.org/abs/2007.00643)；[official code](https://github.com/devendrachaplot/Object-Goal-Navigation/tree/5d76902fe9be821926a1de32557ca9a8dc21d0f5).
7. Ramakrishnan et al., [PONI](https://arxiv.org/abs/2201.10029)；[official code](https://github.com/srama2512/PONI/tree/30682c2bdcd820eec8f72043b2579eb045d547bf).
8. Ramakrishnan, Jayaraman & Grauman, [An Exploration of Embodied Visual Exploration](https://arxiv.org/abs/2001.02192)；[official code](https://github.com/facebookresearch/exploring_exploration/tree/09d3f9b8703162fcc0974989e60f8cd5b47d4d39).
9. Das et al., [Embodied Question Answering](https://arxiv.org/abs/1711.11543)；[official code](https://github.com/facebookresearch/EmbodiedQA/tree/306fd6ef3064b5b9a3bd2d3f06ac96a09c481d9d).
10. [PER-005 Navigation Policy Architecture](vol_06_per005_navigation_policy_architecture.html)、[PER-016 Localization / SLAM](vol_06_per016_localization_odometry_slam_map_frame_drift.html) 与 [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html).
11. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories.
