# VOL 06 PER-019：Navigation Evaluation、Failure Taxonomy 与 Fail-Closed Protocol

> 状态：`knowledge_drafted / VLA-PER-019 / source_frozen / project_truth_bounded / card_pending / WARN`  
> 更新日期：2026-07-21  
> 权威来源：[PER-019 Navigation Evaluation / Failure Source Freeze](../sources/vol_06_per019_navigation_evaluation_failure_source_freeze.html)  
> 学习边界：本页把 `Success`、`DistanceToGoal`、SPL、SoftSPL、NE、OS、TL、split、episode denominator、统计报告与 failure taxonomy 转成可面试、可审计的知识；不生成题卡，不修改 274 张题卡的 mastery，不创建 `coaching_state.md`。

## 问题（Question）

在 VLN、ObjectNav 与 PointGoal 评估中，怎样保证 `success`、`SPL`、`SoftSPL`、`NE`、`OS`、`TL` 与 failure taxonomy 共享同一 episode、split、stop 和 denominator？当本地没有完整 navigation bundle 时，如何 fail closed，而不是从一张 summary、训练 loss 或项目文件名推断导航能力？

## 1. 学习出口

完成本页后，面试中应能做到：

1. 解释为什么 success 不是“曾经到过附近”，而是 stop、距离模式和阈值共同定义的协议谓词。
2. 从 `POINT` / `VIEW_POINTS`、Euclidean step length、geodesic distance 三层区分距离语义。
3. 写出 SPL，并说明参考最短距离、实际路径、success 必须来自同一 episode 与同一 scorer。
4. 区分 binary success、SoftSPL 的连续软成功项、NE、OS、TL 与 summary 平均值；不把不同 metric namespace 混报。
5. 设计包含 task、split、simulator、trajectory、metric、statistics、failure 和 ownership 的 typed evaluation manifest。
6. 说明 `EVAL.EPISODE_COUNT == -1`、invalid/duplicate row、missing episode、early stop 与 CI 样本单位如何改变 estimand。
7. 按 `symptom → first verified divergence → root cause → recovery/terminal outcome` 诊断导航失败；没有 raw trace 时保留 `unknown`。
8. 对 OpenPiVLA、Robot Harness、OPD、WAM、UWM/LIBERO 给出不越界的项目回答。

## 2. 一分钟心智模型

```text
task / dataset / split / episode manifest
              ↓
simulator + navmesh + distance mode + success threshold
              ↓
ordered poses + action + STOP + termination/truncation trace
              ↓
per-episode scorer: Success / Distance / SPL / SoftSPL / NE / OS / TL
              ↓
denominator manifest + CI/statistics + failure taxonomy
              ↓
aggregate report + checkpoint/scorer/ownership lineage
```

核心句子是：**先确认评估了哪些 episode、使用什么几何和 stop 语义，再确认每一行 trajectory 能否重算指标，最后才讨论平均值和根因。** 论文数字、leaderboard 行、项目 summary 或训练 loss 都不能替代这条 lineage。

## 3. Success：位置接近不等于协议成功

Habitat-Lab 固定 revision 的 `Success` measure 依赖 `DistanceToGoal`，并要求 agent 调用 STOP，同时满足距离阈值。对 episode (i)，可用下式表达其协议谓词：

\[
s_i=\mathbf{1}\!\left[\operatorname{stop}_i=1\;\land\;d_i^{\mathrm{goal}}<\tau_i^{\mathrm{success}}\right].
\]

这里 \(s_i\) 是 episode-level success，\(\operatorname{stop}_i\) 是 scorer 记录的 STOP 事件，\(d_i^{\mathrm{goal}}\) 是指定距离模式下的目标距离，\(\tau_i^{\mathrm{success}}\) 是 success threshold。直觉是“到过附近”仍可能没有完成任务；实现映射是 `Success.update_metric` 读取 STOP 状态并依赖 `DistanceToGoal`，而不是从最后一帧的欧氏距离直接猜测。该语义来自固定 Habitat-Lab `nav.py`，不能自动推广到任意本地 evaluator。

面试追问时要先问四件事：STOP 是显式 action 还是 episode 截断？距离是 position 还是 viewpoint？阈值是否随 task/config 变化？最后一行是自然终止、timeout 还是 scorer 丢行？任一项缺失，都只能说“候选 success symptom”，不能说 protocol-confirmed success。

## 4. Distance：POINT、VIEW_POINTS 与 geodesic contract

### 4.1 两种 goal 解释

Habitat `DistanceToGoal` 根据 `distance_to` 选择不同语义：

| 模式 | 目标几何 | 评估含义 | 常见误写 |
| --- | --- | --- | --- |
| `POINT` | 到 goal position 的 simulator geodesic distance | 位置接近 | 用直线欧氏距离代替 navmesh 路径 |
| `VIEW_POINTS` | 到一个或多个 goal viewpoint 的 simulator geodesic distance | 需要抵达可观察目标的视点集合 | 把 viewpoint 当成任意 goal center |

对地图上的位置 (x) 和 goal 集合 (G)，可把几何距离抽象为：

\[
d_{\mathrm{geo}}(x,G)=\min_{g\in G}\operatorname{ShortestPath}_{\mathrm{navmesh}}(x,g).
\]

\(x\) 是 simulator pose，\(G\) 是 position 或 viewpoint 集合，\(\operatorname{ShortestPath}_{\mathrm{navmesh}}\) 是受场景 navmesh 约束的最短路径。公式表达的是 geodesic contract 的直觉，不替代具体 simulator API。实现上必须记录 `distance_mode`、scene/navmesh revision 与 goal viewpoint 列表；否则相同坐标可能对应不同的 success 前置量。

### 4.2 轨迹长度不是 action count

Habitat SPL probe 显示实际路径长度累计相邻 simulator positions 的 Euclidean step distance：

\[
L_i=\sum_{t=1}^{T_i}\left\|p_{i,t}-p_{i,t-1}\right\|_2.
\]

\(p_{i,t}\) 是 episode \(i\) 在第 \(t\) 个记录点的位置，\(T_i\) 是 scorer 看到的轨迹长度。直觉是同样执行 20 个 action，如果 controller step size、停顿、碰撞或重复动作不同，物理路径长度可能不同。实现映射是 trajectory trace 中的 ordered poses；不能用 action 数、policy query 数或 wall-clock 秒数替代 \(L_i\)。

## 5. SPL、SoftSPL 与 metric namespace

### 5.1 SPL

令 \(L_i^\star\) 为同一 episode、同一 scene/navmesh 与同一 goal 语义下的参考最短距离，\(L_i\) 为实际路径长度，\(s_i\) 为同一 scorer 的 binary success，则 success-weighted path length 为：

\[
\operatorname{SPL}_i
=s_i\cdot\frac{L_i^\star}{\max\!\left(L_i^\star,L_i\right)}.
\]

变量 \(L_i^\star,L_i,s_i\) 必须来自同一 episode lineage；\(\max\) 惩罚绕路，\(s_i=0\) 时失败 episode 的 SPL 为 0。代码映射对应 `SPL.reset_metric` 保存 start/end distance、`update_metric` 累计路径并读取 `Success`；零距离 episode、缺失路径和重复 episode 需要 scorer 的显式 guard，不能静默除零。

episode-level 汇总通常是：

\[
\overline{\operatorname{SPL}}=\frac{1}{N_{\mathrm{eval}}}\sum_{i\in\mathcal E_{\mathrm{eval}}}\operatorname{SPL}_i,
\qquad
\operatorname{SR}=\frac{1}{N_{\mathrm{eval}}}\sum_{i\in\mathcal E_{\mathrm{eval}}}s_i.
\]

这里 \(\mathcal E_{\mathrm{eval}}\) 是经过 split、inclusion/exclusion 与 invalid-row policy 确认的 episode 集合，\(N_{\mathrm{eval}}=|\mathcal E_{\mathrm{eval}}|\)。实现上必须保存 episode ID set 和 denominator manifest；只汇总成功样本会把 SR/SPL 的 estimand 改成条件均值。

### 5.2 SoftSPL：连续软成功，不是另一种 binary SR

固定 Habitat source probe 只保证 SoftSPL 使用连续的 soft-success 项替换 binary success，再乘 path-length penalty。为避免把未逐行复述的实现写成强 claim，使用下面的**教学抽象**：

\[
\operatorname{SoftSPL}_i
=q_i^{\mathrm{soft}}\cdot\frac{L_i^\star}{\max\!\left(L_i^\star,L_i\right)},
\qquad q_i^{\mathrm{soft}}\in[0,1].
\]

\(q_i^{\mathrm{soft}}\) 表示官方实现计算的连续接近度；它不是 \(s_i\)，也不能在没有固定 scorer 代码时自行指定成某个距离线性函数。直觉是允许“接近目标但未满足 STOP 阈值”的 episode 得到诊断性分数；实现映射是读取 pinned `SoftSPL` 的实际 soft-success 定义，并同时记录 distance mode、threshold、path length 与 denominator。面试中应说“SoftSPL 是同一 path penalty 下的连续 soft-success 指标”，不要把它当成 leaderboard SPL 或 binary success。

### 5.3 NE、OS、TL：名称相同也要绑定协议

| 指标 | 常见语义 | 必须绑定 | 不能直接推出 |
| --- | --- | --- | --- |
| `NE` | 终点到目标的导航误差 | final pose、goal mode、geodesic scorer、episode set | success 或 recovery root cause |
| `OS` | 是否曾到达目标区域或是否满足任务的 oracle-success 条件 | task-specific scorer、是否要求 STOP、时间范围 | 已正确终止或 leaderboard SR |
| `TL` | trajectory length，可能是 steps 或 path length | unit、controller step、timeout policy | efficient execution，除非与 SPL 协议一致 |

`NE/OS/TL` 的缩写在不同 benchmark 中可能有细节差异；因此回答时先给 task/revision/scorer，再给数值。不得把 VLN-CE 的指标表、Habitat 的 measure 名称或项目 JSON 字段直接当成跨 benchmark 同义词。

## 6. Split、denominator 与统计报告

### 6.1 评估对象是一个集合，不是一个平均数

建议把 episode inclusion 写成显式集合：

\[
\mathcal E_{\mathrm{eval}}
=\left\{e\in\mathcal E_{\mathrm{requested}}:\operatorname{split}(e)=\sigma,\;e\notin\mathcal E_{\mathrm{excluded}},\;\operatorname{row}(e)\text{ is valid}\right\}.
\]

\(\sigma\) 是 `train`、`val_seen`、`val_unseen` 或 `test_challenge` 等 split，\(\mathcal E_{\mathrm{excluded}}\) 记录显式过滤项。直觉是 denominator 先于平均值；实现上要保存 requested IDs、included IDs、excluded IDs、missing IDs、duplicate keys 与过滤原因。

VLN-CE README 明确区分 train/val_seen/val_unseen/test-challenge，并说明 `EVAL.EPISODE_COUNT == -1` 才评估全部 episode。若只跑前 (k) 个、只保留 successful rows、过滤 invalid episode 却不写入 manifest，得到的是另一个 estimand，不能复述为同一 leaderboard 结果。

### 6.2 Success rate 的不确定性

VOL 05 EVAL-003 已冻结 episode-level Bernoulli 与 Wilson/Clopper–Pearson 边界。对 \(k=\sum_i s_i\)、\(n=N_{\mathrm{eval}}\)，Wilson 区间的 teaching form 可写为：

\[
\hat p=\frac{k}{n},\qquad
\operatorname{CI}_{\mathrm{Wilson}}
=\frac{\hat p+\frac{z^2}{2n}\pm z\sqrt{\frac{\hat p(1-\hat p)}{n}+\frac{z^2}{4n^2}}}{1+\frac{z^2}{n}}.
\]

\(\hat p\) 是 episode-level SR，\(z\) 是置信水平对应的正态分位数。变量 \(k,n\) 必须来自同一 denominator manifest；zero/all-success、小样本、task/scene/seed clustering 与 optional stopping 应按 EVAL-003 规则处理。这个统计公式只说明报告不确定性，不证明 scorer、policy 或项目 ownership。

## 7. Typed Navigation Evaluation Manifest

任何“navigation score / improved navigation / failure root cause”回答至少需要以下字段：

| Layer | 最低字段 | 缺失时的 fail-closed 结论 |
| --- | --- | --- |
| task | task family、dataset revision/license、scene、episode ID、goal type、action/STOP schema、frame/unit | 不知道评估的任务与几何语义 |
| split | split、scene split、episode inclusion/exclusion、episode count | 不能比较或复述公开数字 |
| simulator | Habitat/VLN-CE commit、scene/navmesh、distance mode、threshold、controller/action step | 不能确认 scorer 与环境一致 |
| trajectory | ordered poses、action、timestamp/step、STOP、termination/truncation、invalid action | 不能重算 path length、stop 或 failure |
| metrics | SR、SPL/SoftSPL、NE、OS、TL、collision/timeout、denominator、missing policy | summary-only 不是完整评估 |
| statistics | episode-level rows、task/scene/seed clustering、CI method、zero/all-success handling | 不报告聚合不确定性 |
| failure | first divergence、taxonomy label、evidence pointer、recovery/terminal outcome | 只能说 symptom，不能说 confirmed root cause |
| ownership | code/config/data/scorer author、operator、reviewer、artifact custodian | upstream code/Git author 不能成为个人 ownership |

推荐 immutable lineage：

```text
task_manifest_sha + split_manifest_sha + simulator/scorer_revision
    -> episode_ids + trajectory_schema + controller_revision
    -> raw_episode_trace + termination_reason
    -> per_episode_metrics + denominator_manifest
    -> aggregate/CI_report + failure_taxonomy
    -> checkpoint_sha + ownership_ledger
```

这条链的作用不是增加文档字段，而是让每个数值都能追溯到 episode、scorer、代码 revision 和责任边界。当前仓库没有五个项目的完整 local-direct navigation bundle，所以该 manifest 是面试设计合同，不是现有项目已实现的统一 evaluator。

## 8. Failure Taxonomy：从 symptom 到 first divergence

诊断顺序固定为：

```text
protocol/data
  -> policy/decision
  -> geometry/localization
  -> control/execution
  -> scorer/statistics
  -> unknown
```

| 类别 | 典型症状 | 首查 artifact | 不能直接推出 |
| --- | --- | --- | --- |
| protocol/data | split 泄漏、episode 缺失、goal/viewpoint 不一致、scene/navmesh mismatch | split manifest、episode ID set、revision SHA | 模型能力退化 |
| policy/decision | invalid action、early STOP、loop、memory reset | raw action、parser error、policy/memory trace | controller 或 scorer 有 bug |
| geometry/localization | frame mismatch、drift、goal distance 异常 | frame IDs、pose transform、navmesh、relocalization log | 平均 NE 已确认根因 |
| control/execution | collision、controller reject、clip、timeout/horizon | controller status、step trace、termination reason | timeout 等于 collision |
| scorer/statistics | denominator、duplicate、missing row、metric mode、CI 单位错误 | denominator manifest、per-episode rows、scorer revision | policy 真失败 |
| unknown | 只有 summary、视频或时间顺序 | 请求 raw trace；保留 `unknown` | 用最接近的故事替代证据 |

一个完整根因表必须写成 `symptom → first verified divergence → root cause → recovery/terminal outcome`。例如“val-unseen SPL 下降”只是 symptom；只有确认 split manifest、scene revision、policy hash、trajectory first divergence 后，才可以把 root cause 收窄到 geometry、policy 或 scorer。

## 9. Fail-Closed 评估伪代码

```python
def evaluate_navigation(manifest, env, policy, scorer):
    # 1. Freeze task/split/simulator/scorer identity before running an episode.
    assert manifest.task_sha and manifest.split_sha
    assert manifest.simulator_sha and manifest.scorer_sha
    expected_ids = manifest.expected_episode_ids()

    rows = []
    for episode_id in expected_ids:
        # 2. Reset the declared scene, goal mode, controller and STOP schema.
        trace = rollout_one_episode(env, policy, episode_id, manifest)
        if trace.policy_sha != manifest.policy_sha:
            return stop("policy_lineage_mismatch")
        if not trace.has_ordered_pose_action_stop_termination:
            return stop("incomplete_episode_trace")

        # 3. Score one complete episode; do not silently drop invalid rows.
        row = scorer.score(trace, manifest.metric_config)
        if row.episode_id != episode_id or row.duplicate_key:
            return stop("duplicate_or_misaligned_episode")
        rows.append(row)

    # 4. Build the denominator from expected/included/excluded IDs explicitly.
    denominator = build_denominator_manifest(expected_ids, rows, manifest)
    if denominator.missing_ids or denominator.invalid_ids:
        return stop("non_recomputable_denominator")

    # 5. Aggregate SR/SPL/NE/OS/TL and attach CI plus failure evidence pointers.
    report = aggregate_with_ci(rows, denominator, manifest.statistics_config)
    return report
```

这段代码是评估身份和安全 gate 的教学目标，不是五个项目已有的统一 scorer。尤其不能用 `except: continue` 隐藏 invalid episode，也不能从 successful rows 反推 denominator。若无法得到 expected/included/excluded IDs 与 raw trace，输出应是 `not_recomputable` 或 `unknown`。

## 10. Deterministic Probes：把 source 语义变成面试检查

| Probe | 固定观察/输入 | 预期结论 | 面试要点 |
| --- | --- | --- | --- |
| P19-01 | `Success.update_metric` 检查 STOP 与 `distance < success_distance` | success 需要 stop + threshold | 位置接近不等于完成 |
| P19-02 | `Success` 依赖 `DistanceToGoal` | measure identity 绑定 | 不能换成任意 distance |
| P19-03 | `POINT` 调用 geodesic distance 到 goal position | POINT 不是欧氏距离 | 记录 navmesh revision |
| P19-04 | `VIEW_POINTS` 调用 geodesic distance 到 viewpoints | viewpoint 集合改变前置量 | 不混 goal center |
| P19-05 | `SPL.reset_metric` 保存 start/end distance 并依赖 Success | shortest/success 同 episode | 不能拼不同 scorer |
| P19-06 | `SPL.update_metric` 累加相邻 pose Euclidean step | path length 不是 action count | 需要 ordered poses |
| P19-07 | `success * shortest / max(shortest, actual)` | 失败 SPL 为 0，绕路降分 | 不把 TL 当 SPL |
| P19-08 | SoftSPL 使用连续 soft-success × path penalty | SoftSPL ≠ binary SPL | 需固定 soft-success 实现 |
| P19-09 | README 列出 split 与 TL/NE/OS/SR/SPL | namespace 进入 protocol tuple | 不能跨 split 平均 |
| P19-10 | `EVAL.EPISODE_COUNT == -1` 才全量评估 | 子集/过滤会改变 estimand | denominator 先于平均数 |

这些 probe 是 source-text contract 和手算检查，不是 simulator runtime、benchmark reproduction、训练稳定性或个人项目结果。

## 11. 方法比较：面试一张表讲清楚

| 对象 | 输入/状态 | 输出或信号 | 最小可审计证据 | 常见误写 |
| --- | --- | --- | --- | --- |
| Success | final pose + STOP + goal mode | binary \(s_i\) | stop flag、distance measure、threshold | 到过附近就成功 |
| SPL | success + shortest + actual path | success-weighted efficiency | shortest、ordered poses、same episode | action count 就是路径 |
| SoftSPL | soft success + path penalty | 连续进度诊断 | pinned scorer 的 \(q_i^{\mathrm{soft}}\) | 直接当 SR/leaderboard SPL |
| NE | final pose + goal geometry | final navigation error | final pose、geodesic scorer | NE 低就一定 stop 成功 |
| OS | task-specific oracle success | progress/any-time signal | exact scorer predicate、time window | 所有 benchmark 的 OS 同义 |
| TL | steps 或 physical path length | trajectory cost | unit、controller step、termination | TL 低就是高效成功 |
| failure taxonomy | raw trace + first divergence | diagnosis label | trace pointer、revision、recovery outcome | summary 能证明根因 |

## 12. 五项目真实性边界

| 项目 | 可以安全连接的局部 hook | 当前不能说 | 若要升级需要 |
| --- | --- | --- | --- |
| OpenPiVLA | image/language/action schema、normalizer/parser/controller contract | 已完成 VLN/ObjectNav evaluator、SPL/NE 或 navigation rollout | local split/scorer、episode trace、checkpoint 与 ownership |
| Robot Harness | semantic-navigation tool schema、2D tri-state occupancy、PCD/map interface | 个人 navigation policy、真实 robot episode、SPL/OS/collision safety | navigation collector、统一 scorer、raw episodes |
| OPD | point/box/text route、strict/lenient scorer、grounding evidence | closed-loop navigation、3D route、导航 success uplift | environment state/action、trajectory、matched eval |
| WAM | camera/controller/provenance、simulator diagnostic | navigation benchmark、移动平台或 navigation metric | navigation task bundle、scorer、ownership |
| UWM/LIBERO | simulated manipulation protocol、loader/launcher diagnosis | VLN/ObjectNav、mobile navigation、navigation generalization | navigation dataset、episode rows、matched protocol |

安全回答顺序是：`public definition → pinned paper/repo → protocol identity → local inventory → local-direct exception → missing artifact → ownership`。当前仓库的结论是“没有个人导航结果”，不是“项目导航失败”。

## 13. 两档面试回答

### 13.1 约 30 秒回答

我会先把 success 定义成协议谓词：必须在指定 `POINT` 或 `VIEW_POINTS` 距离模式下满足 threshold，并且 agent 真正调用 STOP。SPL 再用同一 episode 的参考最短距离、ordered pose 累计路径和 success 计算；SoftSPL 是连续 soft-success 加 path penalty，不能当 binary SR。NE、OS、TL 也必须带 task、split、scorer、unit 和 denominator。评估前我会固定 expected/included/excluded episode IDs、simulator/scorer revision 和 raw trace；缺任何一层就 fail closed。对我的项目，目前只有 schema/interface/upstream hook，没有完整 navigation bundle，所以不会把 summary 或训练 loss说成个人导航结果。

### 13.2 约 2 分钟机制回答

我先问评估对象是谁：task、split、scene、episode ID、goal mode、STOP schema 和 scorer revision。Habitat 的 Success 依赖 DistanceToGoal，并要求 stop 加 threshold；POINT 和 VIEW_POINTS 走不同 goal 几何，距离是 simulator geodesic，不是直接欧氏距离。SPL 用同一 episode 的 shortest path、实际 pose path 和 binary success，SoftSPL 则把 binary success 换成官方实现定义的连续 soft-success，再乘路径惩罚。NE、OS、TL 不能脱离 benchmark 的 exact predicate、unit 和时间窗口。然后我检查 denominator：VLN-CE 的 `EVAL.EPISODE_COUNT=-1` 才是全量，任何只评估成功行、过滤 invalid、丢失 episode 或 duplicate row 都会改变 estimand。最后按 protocol/data、policy/decision、geometry/localization、control/execution、scorer/statistics、unknown 做 first-divergence 诊断；没有 raw trace，只保留 symptom 或 unknown。我的五个项目目前缺少统一 navigation scorer、split manifest、逐 episode trace 和 ownership，因此我会把这些当成面试中的评估合同和补证据计划，而不是声称已有导航 benchmark 结果。

## 14. 高频追问与答题抓手

| 追问 | 回答抓手 |
| --- | --- |
| 到过目标附近但没 STOP，算 success 吗？ | 按固定 Habitat measure 不算；success 同时需要 STOP 与 threshold。 |
| SPL 为什么不能用 action 数计算？ | Habitat probe 累计相邻 pose 的 Euclidean step distance，action count 没有物理单位。 |
| POINT 和 VIEW_POINTS 的差别？ | goal position 与 viewpoint 集合不同，都会影响 geodesic distance 和 success 前置量。 |
| SoftSPL 是不是更宽松的 SR？ | 不是；它是连续 soft-success × path penalty，必须带 scorer 定义，不能替换 binary SR。 |
| `EVAL.EPISODE_COUNT=-1` 为什么重要？ | 它表达全量 episode；子集、过滤和 early cutoff 会改变 denominator/estimand。 |
| 只有平均 NE 能找到根因吗？ | 不能；先要 per-episode trace、first divergence、frame/scorer/revision。 |
| timeout 算 collision 吗？ | 不应默认相同；termination reason、controller status 和 horizon 必须分开。 |
| 论文 SPL 和 leaderboard SPL 不同怎么办？ | 报告 split、revision、hardware/build、scorer 和 protocol tuple，不直接比较裸数字。 |
| 你的项目做过 navigation evaluator 吗？ | 当前没有 local-direct bundle；只能讲 schema/interface/upstream 机制和补证据路径。 |

## 15. 本页证据边界与下一步

本页已把 PER-019 source freeze 转成可学习知识：success/STOP、POINT/VIEW_POINTS、geodesic distance、SPL、SoftSPL 的实现边界、NE/OS/TL namespace、split/denominator、Wilson CI、typed manifest、failure taxonomy、fail-closed 伪代码、10 个 deterministic probes、五项目 truth boundary、两档口述回答与追问抓手均已覆盖。

直接支持来自 [PER-019 Source Freeze](../sources/vol_06_per019_navigation_evaluation_failure_source_freeze.html)、Anderson SPL、Krantz VLN-CE、pinned Habitat-Lab `nav.py`、pinned VLN-CE README、VOL 05 EVAL-003 与 PER-004。SoftSPL 的 \(q_i^{\mathrm{soft}}\) 在本文中明确标为教学抽象；不能把未逐行复核的具体 soft-success 函数写成本地实现事实。

当前仍为 `WARN`：没有五个项目的 local-direct navigation episode bundle、统一 scorer、split manifest、per-episode trace、matched checkpoint/eval 或 ownership confirmation；没有真实口述，所以不创建 coaching state、不生成题卡、不改变 mastery。下一 bounded slice 才考虑生成 `VLA-PER-019` atomic card；PER-020 source gate 与 SYS-VLA-004/ PER-018 真实口述仍是独立队列。

## References

1. Anderson et al., [On Evaluation of Embodied Navigation Agents](https://arxiv.org/pdf/1807.06757v3), arXiv `1807.06757v3`。
2. Krantz et al., [Beyond the NavGraph: VLN in Continuous Environments](https://arxiv.org/pdf/2004.02857v2), arXiv `2004.02857v2`。
3. Habitat-Lab [`nav.py`](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)，commit `0fb6f43ffe806a8088a171b036336c093bcf604e`。
4. VLN-CE [`README.md`](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)，commit `729d141b2ee10628061ada74dd3a5b9f70faeba5`。
5. [VOL 05 EVAL-003 statistical contract](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。
6. [VOL 06 PER-004 VLN/ObjectNav source freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html)。
7. [VOL 06 PER-019 Source Freeze](../sources/vol_06_per019_navigation_evaluation_failure_source_freeze.html)。
