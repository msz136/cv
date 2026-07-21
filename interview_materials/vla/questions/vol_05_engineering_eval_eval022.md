# VOL 05 Engineering / Evaluation：EVAL-022 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-022`  
> 难度：L3 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-022 Paper→Repo→Checkpoint→Runtime→Ownership Evidence Audit](../knowledge/vol_05_engineering_eval_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit.html)；来源边界见[Source Freeze](../sources/vol_05_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit_source_freeze.html)。本题不把paper、repo、path、summary、hash、Git author或signature替代完整复现与个人贡献证据。

## Paper→Repo→Checkpoint→Runtime→Ownership Evidence Audit

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-EVAL-022</b> · 怎样证明论文方法真的跑到你的checkpoint、指标和个人贡献？</summary>

**面试意图**：判断你能否拆解强claim，审计paper/repo/data/config/run/checkpoint/runtime/raw-eval/protocol链，并把identity、integrity、semantic validity与ownership分开。

**30 秒回答**：把“我复现并提升”拆成方法、执行、结果和贡献；逐边绑定paper版本、repo commit、code/config/data、run、checkpoint bytes/load、runtime、raw output与scorer。贡献另用角色ledger绑定文件、决策、实验和diff/review。任一必需断边就降级，Git author或路径不能补洞。

**机制展开（约 2 分钟）**：paper/model card只证明公开设计，repo只证明某revision有实现，config只证明意图。checkpoint需bytes/SHA、parent run、配套processor/stats与strict load；runtime需环境锁、resolved branch、start/end/exit和raw artifacts；指标由raw unit经固定scorer复算。SLSA字段可组织provenance，但不证明ML语义/ownership。Git author可覆盖，签名只绑定key；贡献需按Methodology/Software/Validation等角色给scope与证据。强claim是AND gate，受最弱必需环节限制。

**诊断 / 证据**：claim registry、paper/model/data version、official repo/tree/file SHA、code-symbol mapping、dataset/split、resolved config、job/start/end/exit、checkpoint bytes/load/roundtrip、runtime/deps/hardware、raw prediction/episode、scorer/protocol/recompute、contradiction、license与contribution-role ledger。

**项目挂钩**：OPD有代码/manifests/tables但缺weights/raw predictions；OpenPiVLA有formal code/smoke但缺formal checkpoint与97.4 raw lineage；Harness缺共同scorer/raw episodes；UWM的186/250是user-confirmed summary；WAM当前无完整raw run bundle。五项目ownership均未闭合。

**追问树**：official repo怎样确认？README和code冲突听谁？path为何不算checkpoint？load report够吗？smoke和formal run区别？summary能否写？hash/签名证明什么？SLSA能否证明复现？Git author为何不等于ownership？协作/工具辅助怎么讲？license为何分层？哪个项目链最完整？

**易错点**：paper结果写成本地；fork冒充official；config存在=执行；远端path=weights；summary=raw；smoke=formal benchmark；hash=语义正确；signature=独立实现；Git author=全部ownership；repo license覆盖weights/data；删冲突；未找到=远端不存在；用证据总分平均断边。

**危险答案**：说“论文有开源仓库所以我算复现了”“checkpoint路径和训练报告足够证明结果”“commit作者是我所以项目都是我独立完成”“签名能证明代码和指标都属于我”，或把五项目缺失的checkpoint/raw/ownership伪装成已闭合。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-022 知识页](../knowledge/vol_05_engineering_eval_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit.html)。
2. [EVAL-022 Source Freeze](../sources/vol_05_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit_source_freeze.html)。
3. [Model Cards](https://arxiv.org/abs/1810.03993v2)。
4. [Datasheets for Datasets](https://arxiv.org/abs/1803.09010v8)。
5. [SLSA Provenance v1.2](https://slsa.dev/spec/v1.2/provenance)。
6. [Git commit documentation](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-commit.adoc)。
7. [CRediT Role Descriptors](https://credit.niso.org/contributor-roles-defined/)。
8. [Evidence Manifest / five project inventories](../evidence/evidence_manifest.html)。
