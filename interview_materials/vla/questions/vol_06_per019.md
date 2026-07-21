# VOL 06 Perception / Grounding / Navigation：PER-019 原子题卡

> 状态：`drafted / card_1_of_1 / source_frozen / knowledge_synced / WARN`  
> 更新日期：2026-07-21  
> 覆盖范围：`VLA-PER-019`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-019 Navigation Evaluation / Failure Knowledge](../knowledge/vol_06_per019_navigation_evaluation_failure.html)；来源边界见 [PER-019 Source Freeze](../sources/vol_06_per019_navigation_evaluation_failure_source_freeze.html)。

## Navigation Evaluation、Denominator 与 Failure Taxonomy

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-PER-019</b> · VLN/ObjectNav/PointGoal 中怎样统一 Success、SPL、SoftSPL、NE、OS、TL、split、denominator 与 failure taxonomy？没有完整 navigation bundle 时如何 fail closed？</summary>

**面试意图**：判断你能否把导航指标讲成同一套 task/split/episode/scorer 协议，并在缺少 raw trace 时拒绝从 summary、loss 或项目文件名推断个人导航结果。

**30 秒回答**：先锁 task/split/episode、scorer、STOP、分母。Success=STOP+geodesic阈值；SPL 用同 episode 的 shortest path、pose path、success；SoftSPL 是连续项，不是 SR。NE/OS/TL 要带 unit；无 raw trace 不把 summary/loss 当导航结果。

**机制展开（约 2 分钟）**：先锁 episode IDs、split、navmesh、scorer SHA；确认 Success=STOP+threshold 与 POINT/VIEW_POINTS geodesic。SPL 需 shortest distance、pose path、同一 success；SoftSPL 只按 pinned scorer。NE/OS/TL 绑定 predicate、unit、termination、分母。诊断按 protocol→policy→geometry→control→scorer→unknown，root cause 要 trace；invalid/duplicate/filter 会改分母。五项目无完整 bundle，只讲接口与缺口。

**诊断 / 证据**：先查 task/split/episode ID set→simulator/navmesh/distance mode/threshold→ordered pose/action/STOP/termination trace→per-episode Success/SPL/NE/OS/TL→included/excluded/missing/duplicate denominator→CI method→first-divergence taxonomy→checkpoint/scorer/ownership。`EVAL.EPISODE_COUNT == -1` 才代表全量评估；只保留成功行、过滤 invalid、混合 seen/unseen 或把 timeout 当 collision 都会改变结论。没有这些 artifact 时保留 `not_recomputable` 或 `unknown`。

**项目挂钩**：OpenPiVLA 只能连接 image/language/action schema 与 parser/controller contract；Robot Harness 只能连接 2D occupancy、PCD/map interface；OPD 只能连接 point/box/text scorer；WAM、UWM/LIBERO 只能连接 simulator/provenance 或 manipulation protocol。它们目前都不能证明个人 VLN/ObjectNav evaluator、SPL/NE/OS、navigation rollout、collision safety 或 ownership。

**追问树**：到过目标附近但没 STOP 算 success 吗？POINT 与 VIEW_POINTS 怎样影响距离？SPL 为什么不能用 action count？SoftSPL 能否当 SR？`EVAL.EPISODE_COUNT=-1` 为什么重要？论文 SPL 与 leaderboard SPL 不一致如何解释？NE 下降能否确认根因？timeout 与 collision 如何区分？缺 episode 或 duplicate row 如何处理？如何给五个项目各写一句不越界回答？

**易错点**：把“到过附近”当 Success；把欧氏距离当 geodesic；把 action 数当 path length；把 SoftSPL 当 binary SR；只报成功样本的均值；把 summary、训练 loss、视频或字段名当作 root cause/ownership；把 timeout、invalid action、collision 和 scorer 丢行混成同一种 failure。

**危险答案**：说“项目 SPL 很高所以导航成功”“SoftSPL 就是更宽松的 SR”“NE 降了说明模型修好了”“没有 raw episode 也能从 loss 推断闭环能力”，却不能给出 split、episode denominator、scorer revision、STOP、trajectory trace 与 first divergence。

**来源**：[1][2][3][4][5][6]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-019 Navigation Evaluation / Failure Knowledge](../knowledge/vol_06_per019_navigation_evaluation_failure.html)：Success/STOP、POINT/VIEW_POINTS、geodesic distance、SPL/SoftSPL、denominator、failure taxonomy、fail-closed 伪代码与五项目边界。
2. [PER-019 Source Freeze](../sources/vol_06_per019_navigation_evaluation_failure_source_freeze.html)：2 个 primary papers、2 个 pinned official sources、10/10 deterministic probes 与 claim boundary。
3. Anderson et al., [On Evaluation of Embodied Navigation Agents](https://arxiv.org/pdf/1807.06757v3)，SPL 与 shortest-path 评估语境。
4. Krantz et al., [Beyond the NavGraph: VLN in Continuous Environments](https://arxiv.org/pdf/2004.02857v2)，VLN-CE continuous environment 与 metric namespace。
5. [Habitat-Lab `nav.py`](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py)，Success/DistanceToGoal/SPL/SoftSPL 实现入口。
6. [VLN-CE `README.md`](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)，split、episode count、leaderboard/build protocol 边界。
