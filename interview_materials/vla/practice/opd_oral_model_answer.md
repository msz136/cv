# PROJ-OPD-001..009 从项目实现反推的证据约束口述稿

> 状态：`implementation_derived_model_answer / evidence_bounded / not_candidate_transcript / unseen`
> 更新日期：2026-07-22
> 题目：如何介绍 OPD 的五 expert 数据合同、两阶段蒸馏、route/KL、checkpoint/point 协议、因果边界与 ownership？

## 1. 30 秒版本

> OPD 的目标是让一个 student 同时覆盖 reasoning、object、region、spatial relation 和 point 等输出协议，而不是把五个 expert 的样本无标记地混在一起。数据构建阶段保留 target/candidate expert、expected format、seen/unseen、boundary 和 format-conflict metadata；formal `point/` trainer 先用 teacher-rollout full-vocab KL 做 coldstart，再用 student rollout 做 OPD5000，由 route teacher 在同一 response 上给完整词表分布。根目录同名脚本只是 legacy teacher-rollout/top1 CE，不能混为 formal 证据。当前 route 仍是 metadata selection，不是 learned router；组合结果也不能直接证明单因果 uplift 或真实机器人闭环。

## 2. 2 分钟版本

> 我先区分问题、数据合同和训练机制。五个 specialist 分别覆盖 reasoning、object、region、spatial relation 和 RoboPoint point grounding；如果只把数据拼起来，student 可能同时面对不同的输出格式、能力边界和 supervision 来源，最终出现 box/point/text 混淆。因此数据构建不仅保留样本内容，还写入 target/candidate expert、expected format、source line、image fingerprint、seen exposure、boundary 和 format-conflict。
>
> 数据侧先做 image-hash 的 train/eval 隔离，并对 spatial relation 做长尾重采样；student 数据再按 domain、general、boundary、format-conflict 分层。这样可以在评估时按 exposure、format 和 pool 分开看，不把“没有重复”直接说成模型泛化。
>
> 训练侧分两阶段，而且要先区分两份同名 trainer。根目录 legacy 版是 teacher generate、teacher logits 取 argmax、student 用 top1 hard-label CE；正式 new-experts 路线在 `point/train_opd_online_vl.py`。coldstart 从 base student 出发，由 teacher rollout；OPD5000 从 coldstart 输出继续，由 student rollout。两阶段都让 route teacher 在同一 response 上 forward，并计算完整词表的 \(D_{KL}(q_\beta\|p_S)\)。veto 期的 \(q_\beta\) 由 `teacher_logits + beta * stopgrad(student_logits)` 构造，beta 归零后才是纯 \(D_{KL}(p_T\|p_S)\)。这里的 route 来自 metadata，不是额外训练出来的 learned router；如果要称 learned router，还需要 routing model、routing loss 和同协议 ablation。
>
> 评估时我会绑定 raw-holdout、pool、scorer、checkpoint 和 denominator。不同 pool 的最佳 checkpoint 不一致，所以不能把 ckpt5000 说成所有指标最佳；旧版 OPD final 和新版 OPD5000 也不是同一条 run。当前可以讲数据合同、训练链和协议修正，但缺 SFT-only、single-teacher、no-synthetic、raw predictions 和逐文件 ownership，因此不把组合结果包装成 OPD 单因果 uplift 或个人独立完成。

## 3. 证据映射

| 结论 | 证据 | 当前强度 |
| --- | --- | --- |
| 五 expert 配额、image-hash split、relation bucket | [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | `local-direct / data-contract` |
| student route metadata、boundary、format-conflict | 同上及 student builder/audit 记录 | `local-direct / quality-gate` |
| legacy top1 CE vs formal full-vocab KL、coldstart teacher rollout vs OPD5000 student rollout | [OPD Training Objective Lineage Gate](../evidence/projects/opd_training_objective_lineage_gate.html) | `local-code-reconciled / run-summary-bounded` |
| OPD5000 by-format/by-pool 曲线 | inventory 的 checkpoint tables | `protocol-bounded / raw predictions missing` |
| point strict 修正 | OPD inventory 与 point protocol reconciliation | `protocol-limited` |
| 个人 ownership | [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html) | `candidate-confirmation-pending` |

## 4. 题卡覆盖映射

| Question ID | 实现主题 | 本页回答入口 |
| --- | --- | --- |
| `PROJ-OPD-001` | 为什么不是无标记混合五个 expert | 30 秒版本与项目定位 |
| `PROJ-OPD-002` | expert 配额与 relation 重采样 | 2 分钟版本的数据合同 |
| `PROJ-OPD-003` | seen/unseen/boundary/format-conflict | 2 分钟版本的数据分层 |
| `PROJ-OPD-004` | coldstart500 与 OPD5000 | 2 分钟版本的两阶段训练 |
| `PROJ-OPD-005` | route teacher 与 full-vocabulary KL | 训练机制与高频追问 |
| `PROJ-OPD-006` | checkpoint selection | metric/protocol 追问 |
| `PROJ-OPD-007` | raw-holdout 与重复图片 | image-hash split 追问 |
| `PROJ-OPD-008` | point protocol 与因果归因 | point/uplift 追问 |
| `PROJ-OPD-009` | 个人、Git、远端和工具边界 | ownership 追问与 ledger |

## 5. 高频追问答法

### “route metadata 是 learned router 吗？”

不是。当前实现按样本中的 `target_expert/candidate_experts` 选择 teacher；它是数据/训练路由合同。learned router 需要额外模型、routing objective、部署时输入和 ablation，不能从 route id 自动推断。

### “为什么一定要 full-vocabulary KL？”

它保留 teacher/target 在整个词表上的概率分布、格式偏好和不确定性，而不只复制 top1；代价是显存和计算更高，也可能复制 teacher 错误。当前 formal 代码计算的是 \(D_{KL}(q_\beta\|p_S)\)，beta=0 时为 teacher∥student，不是 student∥teacher。是否优于 top1/top-k 仍需要同数据、同 budget、同 scorer 的 matched ablation，当前不能直接宣称。

### “为什么仓库里两份同名脚本，一份没有 KL？”

根目录 `train_opd_online_vl.py` 是旧版 teacher-rollout/top1-CE 实现；new-experts artifact manifest、launchers 和 run summaries 指向 `/data/msz/point/train_opd_online_vl.py`，对应本地 `point/` formal trainer。面试时我会按完整相对路径和 SHA 说明 lineage，不用同名文件末尾偷换实现版本。

### “coldstart 和 OPD5000 是两种 KL 方向吗？”

不是。两者都用 formal \(D_{KL}(q_\beta\|p_S)\)；差异主要是 rollout distribution、parent checkpoint、max-new/prefix、veto schedule 与训练步数。coldstart 是 teacher rollout，OPD5000 是 student rollout。beta 大于 0 时 target 还混入 detached student logits，归零后才是纯 teacher-to-student forward KL。

### “ckpt5000 是全局最佳吗？”

不是。point 和部分 box 指标偏向 5000，但整体 box IoU、某些 region/relation 和 text pool 的最佳 checkpoint 分散在其他 step。应按部署目标和 Pareto trade-off 选择，并报告 selection rationale。

### “raw-holdout 说 0 泄漏，为什么仍能看到重复图片？”

0 泄漏指按 image hash 分组后，train 与 eval 的 hash 交集为 0；它不自动保证 eval 内每张图片只出现一次。同一图片可以对应多个 question、format 或 expert annotation，所以还要同时报告 unique-image 数、per-hash sample 数和 grouped denominator，不能把 sample-level 重复误说成跨 split 泄漏，也不能把 hash 隔离直接等同语义泛化。

### “point strict=0 是模型不会定位吗？”

不一定。早期 prompt 与 strict parser 的 tag 格式不一致，可能把协议失败误判成几何能力失败；要同时报告 original strict、protocol-fixed strict 和 lenient geometry，并冻结 prompt/parser hash。

### “OPD 提升了多少？”

只能按明确的同一 holdout、scorer、checkpoint 和 pool 报告组合路线结果。缺 SFT-only、single-teacher、no-synthetic 和 raw prediction 对照时，不能把差值单因果归因给 OPD。

### “哪些是你做的？”

逐文件看 ownership ledger，区分 scaffold、个人设计、个人实现、协作、工具辅助、远端运行和 reviewer；`mousongzhe` 或其他账号的 commit 只能作为 lineage 线索，不能替代确认。

## 6. 练习边界

- 这是 model answer，不是候选人的真实 transcript。
- 使用时必须替换“我负责”的内容，并绑定具体脚本、commit、命令、评估或验收证据。
- 真实口述前保持 `PROJ-OPD-001..009` 全部为 `unseen`，不创建 `coaching_state.md`。

## References

1. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
2. [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html)。
3. [PROJ-OPD-001..009 Atomic Cards](../questions/proj_opd.html)。
