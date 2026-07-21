# VOL 06 PER-019 Source Freeze：Navigation Evaluation / Failure Protocol

> 状态：`source_frozen / VLA-PER-019 / primary_official_checked / navigation_eval_contract / knowledge_card_pending / WARN`  
> 冻结日期：2026-07-21  
> 证据截止：2026-07-21  
> 本 source slice 只冻结导航评估指标、episode denominator、stop/success、SPL、SoftSPL、split/protocol identity、统计报告与 failure taxonomy 的公开机制；不生成 knowledge/card，不修改 mastery，不创建 `coaching_state.md`，不把五个项目写成个人导航结果。

## 问题（Question）

在 VLN/ObjectNav/PointGoal 评估中，怎样保证 `success`、`SPL`、`SoftSPL`、`NE`、`OS`、`TL` 与 failure taxonomy 共享同一 episode、split、stop 和 denominator？当本地没有完整 navigation bundle 时，如何 fail closed，而不是从一张 summary 或训练 loss 推断导航能力？

## 1. 结论先行

1. **Success 是带 stop 条件的协议谓词**：固定 Habitat-Lab revision 的 `Success` measure 依赖 `DistanceToGoal`，并要求 agent 调用 stop 且距离低于 `success_distance`；“到过附近”不等于成功。
2. **SPL 是 success-weighted path length**：令 (L^star) 为 episode 的参考最短距离，(L) 为实际轨迹长度，(Sin{0,1}) 为同一协议下的 success，则 (SPL=Scdot L^star/max(L^star,L))。它依赖同一 episode 的 distance、success 与轨迹累计，不能脱离 stop/split 单独比较。
3. **距离定义必须显式绑定**：Habitat-Lab 的 `DistanceToGoal` 根据 `distance_to` 选择 `POINT` 或 `VIEW_POINTS`，使用 simulator geodesic distance；把欧氏距离、geodesic distance、goal viewpoint 和 success threshold 混为一谈会改变指标含义。
4. **SoftSPL 不是另一个 success label**：官方实现用连续的软成功项替代二值 success，再乘以 path-length penalty；它适合诊断进度，但不能直接当作 binary success 或 leaderboard SPL。
5. **评估 denominator 是协议的一部分**：VLN-CE README 明确区分 train/val_seen/val_unseen/test-challenge，并说明 `EVAL.EPISODE_COUNT == -1` 才评估全部 episode；子集、过滤 invalid episode、提前截断或只报成功样本都会改变 estimand。
6. **官方结果也受 build/protocol 影响**：VLN-CE README 记录同一模型在论文与 leaderboard 上的 val-unseen SPL 不一致，并指出 hardware 与 Habitat build 会影响结果；因此复述公开数字时必须带来源、split、revision 和 protocol tuple。
7. **failure taxonomy 必须绑定 raw episode trace**：至少区分 invalid action/parse、early stop、timeout/horizon、collision/constraint、localization/map-frame、goal-distance、controller execution、dataset/split/protocol mismatch 与 unknown；summary-only 不能确认 root cause。
8. 五个本地项目目前没有完整的 navigation episode bundle、统一 scorer、split manifest、逐 episode trace 和候选人 ownership 证据；因此本节点只提供面试评估合同，不升级个人导航 success/SPL/OS/NE claim。

## 2. Primary / official source matrix

| ID | 来源 | 固定版本 / 读取证据 | 支持的 claim | 不支持的 claim |
| --- | --- | --- | --- | --- |
| P1 | Anderson et al., [On Evaluation of Embodied Navigation Agents](https://arxiv.org/pdf/1807.06757v3) | arXiv `1807.06757v3`；SPL 定义与 shortest-path / trajectory 评估语境 | success-weighted path length、参考路径长度与导航评估协议 | 本地项目复现、任意 split 的可比性、真实机器人安全 |
| P2 | Krantz et al., [Beyond the NavGraph: VLN in Continuous Environments](https://arxiv.org/pdf/2004.02857v2) | arXiv `2004.02857v2`；VLN-CE continuous-environment、R2R split 与指标语境 | continuous VLN 的 episode、stop、trajectory 与 SR/SPL/NE/OS/TL 讨论 | 本地 checkpoint、硬件复现、个人 ownership |
| O1 | [Habitat-Lab `nav.py`](https://raw.githubusercontent.com/facebookresearch/habitat-lab/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) | commit `0fb6f43ffe806a8088a171b036336c093bcf604e`；1342 lines；46925 bytes；SHA `3ce31b1bb75cc733c09d777e1ff0f18fb99c1882206a9496da648c1bd6ee549d` | `Success`、`DistanceToGoal`、`SPL`、`SoftSPL` 的实现依赖与计算顺序 | 任何本地 evaluator 与该实现自动等价 |
| O2 | [VLN-CE README](https://raw.githubusercontent.com/jacobkrantz/VLN-CE/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md) | commit `729d141b2ee10628061ada74dd3a5b9f70faeba5`；293 lines；16460 bytes；SHA `33c547d6d6fa8a7deca433c5e441894aad72d676dfca152fea0cd4ef80b9a41c` | split、leaderboard、full-episode evaluation、build variance 与 trajectory submission 入口 | 公开 README 不能证明候选人运行过该 benchmark |
| O3 | [VOL 05 EVAL-003 statistical contract](vol_05_eval003_success_rate_confidence_interval_source_freeze.md) | repository canonical source + review；已冻结 success denominator、Wilson/Clopper–Pearson、zero/all-success 与 clustering 边界 | 统计报告、置信区间与样本单位的复用边界 | PER-019 的导航 metric 语义、个人结果 |
| O4 | [PER-004 VLN/ObjectNav source freeze](vol_06_per004_vln_objectnav_source_freeze.md) | repository canonical source + review；task/episode/stop/success 入口 | task contract、episode identity、SR/SPL 关联边界 | 评估节点的完整 failure taxonomy 或本地 raw bundle |

## 3. Official implementation probes

以下 probe 只验证公开代码/README 的语义，不等于运行了 Habitat 或 VLN-CE，也不产生个人 benchmark 结果。

| Probe | 固定观察 | 结论 |
| --- | --- | --- |
| P19-01 | Habitat `Success.update_metric` 检查 `is_stop_called` 与 `distance_to_target < success_distance` | success 需要 stop + threshold，不能只看位置 |
| P19-02 | `Success` 依赖 `DistanceToGoal` measure | success 与距离 measure 的 protocol identity 绑定 |
| P19-03 | `DistanceToGoal` 的 `POINT` 分支调用 simulator geodesic distance 到 goal position | POINT 不等于欧氏距离 |
| P19-04 | `DistanceToGoal` 的 `VIEW_POINTS` 分支调用 simulator geodesic distance 到 goal viewpoints | goal viewpoint 选择会改变距离与 success 前置量 |
| P19-05 | `SPL.reset_metric` 保存 start/end distance，并依赖 `DistanceToGoal`、`Success` | SPL 的参考距离和 success 必须来自同一 episode |
| P19-06 | `SPL.update_metric` 累加相邻 simulator positions 的 Euclidean step distance | 实际 path length 不能用 action count 代替 |
| P19-07 | Habitat SPL 使用 `success * shortest / max(shortest, actual)` | 失败 episode 的 SPL 为 0；绕路会降低 SPL |
| P19-08 | `SoftSPL` 用连续 soft-success 替换二值 success，再乘 path penalty | SoftSPL 与 SPL 不能混报 |
| P19-09 | VLN-CE README 列出 `train/val_seen/val_unseen/test_challenge` 与 TL/NE/OS/SR/SPL | split 与 metric namespace 必须进入 protocol tuple |
| P19-10 | VLN-CE README 说明 `EVAL.EPISODE_COUNT == -1` 才评估全部 episode，并记录 leaderboard/build 差异 | 子集评估、硬件或 Habitat revision 差异必须显式披露 |

Probe 状态：`10/10 deterministic source probes checked`。这些 probe 只检查 source text，不替代 simulator runtime、完整 dataset 或候选人项目 artifact。

## 4. Typed navigation evaluation contract

| Layer | 最低字段 | 缺失时的 fail-closed 结论 |
| --- | --- | --- |
| task | task family、dataset revision/license、scene、episode ID、goal type、action/STOP schema、frame/unit | 不知道评估的任务与几何语义 |
| split | train/val_seen/val_unseen/test、scene split、episode inclusion/exclusion、episode count | 不能比较或复述公开数字 |
| simulator | Habitat/VLN-CE commit、scene/navmesh、distance mode、success threshold、controller/action step | 不能确认 scorer 与环境一致 |
| trajectory | ordered poses、action、timestamp/step、STOP、termination/truncation、invalid action | 不能重算 path length、stop 或 failure |
| metrics | SR、SPL/SoftSPL、NE、OS、TL、collision/timeout、denominator 与 missing policy | summary-only 结果不能作为完整评估 |
| statistics | episode-level rows、task/scene/seed clustering、CI method、zero/all-success handling | 不报告聚合不确定性或样本单位 |
| failure | first divergence、taxonomy label、evidence pointer、recovery/terminal outcome | 只能说 symptom，不能说 confirmed root cause |
| ownership | code/config/data/scorer author、operator、reviewer、artifact custodian | upstream code、Git author 或 README 不能成为个人 ownership |

推荐 immutable lineage：

```text
task_manifest_sha + split_manifest_sha + simulator/scorer_revision
-> episode_ids + trajectory_schema + controller_revision
-> raw_episode_trace + termination_reason
-> per_episode_metrics + denominator_manifest
-> aggregate/CI_report + failure_taxonomy
-> checkpoint_sha + ownership_ledger
```

## 5. Failure taxonomy 与诊断顺序

诊断必须按 `symptom → first verified divergence → root cause → recovery/terminal outcome` 分层：

1. **protocol/data**：split 泄漏、episode 缺失、goal/viewpoint 不一致、scene/navmesh revision mismatch；
2. **policy/decision**：invalid action、early STOP、loop、instruction grounding 或 memory reset；
3. **geometry/localization**：map/odom/frame、drift、goal distance、relocalization；
4. **control/execution**：collision、controller rejection、action clipping、timeout/horizon；
5. **scorer/statistics**：denominator、duplicate episode、missing row、metric mode 或 CI 单位错误；
6. **unknown**：没有 raw trace 时保留 unknown，不能用时间顺序代替根因。

最小 fault-injection / audit matrix：

| 注入或审计 | 预期可观察字段 | 不能直接推出 |
| --- | --- | --- |
| early STOP near/far goal | stop flag、distance mode、distance、success | 不能推出 policy 已学会 recovery |
| timeout / horizon | step count、termination reason、last pose、NE/TL | 不能把 timeout 当 collision |
| invalid action / parse | raw action、parser error、fallback、episode row | 不能把 scorer 丢行当成功 |
| map/frame mismatch | frame IDs、scene/navmesh revision、pose transform | 不能只看平均 NE 判定模型退化 |
| duplicate/missing episode | episode ID set、expected denominator、duplicate key | 不能从汇总均值恢复缺失样本 |
| build/scorer revision change | simulator/scorer SHA、metric config | 不能直接纵向比较 SPL |

## 6. 五项目真实性边界

| 项目 | 允许的局部 hook | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | image/language/action schema、normalizer/parser/controller contract 风险 | 已完成 VLN/ObjectNav evaluator、SPL/NE、navigation rollout |
| Robot Harness | semantic-navigation tool schema、2D tri-state occupancy、PCD/map interface | 个人导航 policy、真实机器人 episode、SPL/OS 或 collision safety |
| OPD | point/box/text route、strict/lenient scorer 与 grounding evidence | closed-loop navigation、3D route、导航 success uplift |
| WAM | camera/controller/provenance 与 simulator diagnostic | navigation benchmark、真实移动平台或 navigation metric |
| UWM/LIBERO | simulated manipulation protocol、loader/launcher diagnosis | VLN/ObjectNav、mobile navigation、导航泛化 |

所有项目均应写成 `public upstream mechanism → local evidence → inference → unverified`；当前没有 local-direct navigation bundle 时，最终结论必须保留“无个人导航结果”的表述。

## 7. 退出条件与下一步

本 source slice 的退出条件：

1. 2 个 primary papers、2 个 official code/docs、2 个本地跨卷入口已固定并可追溯；
2. 10/10 source probes 通过；
3. metric、split、denominator、failure taxonomy 与项目边界明确；
4. source artifact 具备 Markdown/HTML/review 三联件；
5. knowledge/card 继续后置，不能把 source freeze 当作掌握或 benchmark 完成。

下一 bounded slice：只生成 `VLA-PER-019` knowledge，复用本 source contract；仍不生成题卡、不修改 mastery。`VLA-PER-018` 真实口述与 `SYS-VLA-004` 系统设计口述保留在独立训练队列。

## 参考来源

1. Anderson et al.，[On Evaluation of Embodied Navigation Agents](https://arxiv.org/pdf/1807.06757v3)。
2. Krantz et al.，[Beyond the NavGraph: VLN in Continuous Environments](https://arxiv.org/pdf/2004.02857v2)。
3. Habitat-Lab [`nav.py`](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)。
4. VLN-CE [`README.md`](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
5. [VOL 05 EVAL-003 source freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.md)。
6. [VOL 06 PER-004 source freeze](vol_06_per004_vln_objectnav_source_freeze.md) 与 [PER-018 source freeze](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.md)。
