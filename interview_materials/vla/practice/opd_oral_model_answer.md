# PROJ-OPD-001 证据约束下的示范回答

> 状态：`model_answer / evidence_bounded / not_candidate_transcript / unseen`  
> 更新日期：2026-07-21  
> 题目：OPD 这条路线要解决什么问题，为什么不是简单把五个 expert 的数据混在一起？

## 1. 30 秒版本

> OPD 的目标是让一个 student 同时覆盖 reasoning、object、region、spatial relation 和 point 等输出协议，而不是把五个 expert 的样本无标记地混在一起。数据构建阶段保留 target/candidate expert、expected format、seen/unseen、boundary 和 format-conflict metadata；训练先做五教师 coldstart，再做 student rollout，由 route 对应的 teacher 在同一 response 上计算 full-vocabulary KL。当前 route 是 metadata 驱动的 teacher selection，不是已验证的 learned router；OPD5000 的结果是组合路线在固定 holdout 上的证据，不能单因果归因给 OPD，也不能自动证明真实机器人闭环。

## 2. 2 分钟版本

> 我先区分问题、数据合同和训练机制。五个 specialist 分别覆盖 reasoning、object、region、spatial relation 和 RoboPoint point grounding；如果只把数据拼起来，student 可能同时面对不同的输出格式、能力边界和 supervision 来源，最终出现 box/point/text 混淆。因此数据构建不仅保留样本内容，还写入 target/candidate expert、expected format、source line、image fingerprint、seen exposure、boundary 和 format-conflict。
>
> 数据侧先做 image-hash 的 train/eval 隔离，并对 spatial relation 做长尾重采样；student 数据再按 domain、general、boundary、format-conflict 分层。这样可以在评估时按 exposure、format 和 pool 分开看，不把“没有重复”直接说成模型泛化。
>
> 训练侧分两阶段。coldstart 从 base student 出发，使用五个 teacher rollout 和 full-vocabulary KL，先让 student 获得基本的格式和能力分布；正式 OPD 阶段让 student 自己 rollout，再让 route 指定的 teacher 对同一 response forward，计算 full-vocab KL，保存多个 checkpoint。这里的 route 来自 metadata，不是一个额外训练出来的 learned router；如果要称 learned router，还需要 routing model、routing loss 和同协议 ablation。
>
> 评估时我会绑定 raw-holdout、pool、scorer、checkpoint 和 denominator。不同 pool 的最佳 checkpoint 不一致，所以不能把 ckpt5000 说成所有指标最佳；旧版 OPD final 和新版 OPD5000 也不是同一条 run。当前可以讲数据合同、训练链和协议修正，但缺 SFT-only、single-teacher、no-synthetic、raw predictions 和逐文件 ownership，因此不把组合结果包装成 OPD 单因果 uplift 或个人独立完成。

## 3. 证据映射

| 结论 | 证据 | 当前强度 |
| --- | --- | --- |
| 五 expert 配额、image-hash split、relation bucket | [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | `local-direct / data-contract` |
| student route metadata、boundary、format-conflict | 同上及 student builder/audit 记录 | `local-direct / quality-gate` |
| coldstart + student rollout + route teacher + full-vocab KL | run summaries、training script、inventory | `local-direct / report-supported` |
| OPD5000 by-format/by-pool 曲线 | inventory 的 checkpoint tables | `protocol-bounded / raw predictions missing` |
| point strict 修正 | OPD inventory 与 point protocol reconciliation | `protocol-limited` |
| 个人 ownership | [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html) | `candidate-confirmation-pending` |

## 4. 高频追问答法

### “route metadata 是 learned router 吗？”

不是。当前实现按样本中的 `target_expert/candidate_experts` 选择 teacher；它是数据/训练路由合同。learned router 需要额外模型、routing objective、部署时输入和 ablation，不能从 route id 自动推断。

### “为什么一定要 full-vocabulary KL？”

它保留 teacher 在整个词表上的概率分布、格式偏好和不确定性，而不只复制 top-k；代价是显存和计算更高，也可能复制 teacher 错误。是否优于 top-k 需要 matched ablation，当前不能直接宣称。

### “ckpt5000 是全局最佳吗？”

不是。point 和部分 box 指标偏向 5000，但整体 box IoU、某些 region/relation 和 text pool 的最佳 checkpoint 分散在其他 step。应按部署目标和 Pareto trade-off 选择，并报告 selection rationale。

### “point strict=0 是模型不会定位吗？”

不一定。早期 prompt 与 strict parser 的 tag 格式不一致，可能把协议失败误判成几何能力失败；要同时报告 original strict、protocol-fixed strict 和 lenient geometry，并冻结 prompt/parser hash。

### “OPD 提升了多少？”

只能按明确的同一 holdout、scorer、checkpoint 和 pool 报告组合路线结果。缺 SFT-only、single-teacher、no-synthetic 和 raw prediction 对照时，不能把差值单因果归因给 OPD。

### “哪些是你做的？”

逐文件看 ownership ledger，区分 scaffold、个人设计、个人实现、协作、工具辅助、远端运行和 reviewer；`mousongzhe` 或其他账号的 commit 只能作为 lineage 线索，不能替代确认。

## 5. 练习边界

- 这是 model answer，不是候选人的真实 transcript。
- 使用时必须替换“我负责”的内容，并绑定具体脚本、commit、命令、评估或验收证据。
- 真实口述前保持 `PROJ-OPD-001` 为 `unseen`，不创建 `coaching_state.md`。

## References

1. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
2. [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html)。
3. [PROJ-OPD-001..009 Atomic Cards](../questions/proj_opd.html)。
