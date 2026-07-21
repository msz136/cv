# OPD / VLM Grounding Ownership Ledger：数据、路由、训练与结果归属

> 状态：`ownership_audited / coarse_git_supported / candidate_confirmation_pending / WARN`
> 审查日期：2026-07-19
> 证据截止：2026-07-19
> 项目范围：`C:\Users\mousongzhe\muxi` 的 OPD / VLM grounding 数据管线、五 expert、online OPD、raw-holdout 与报告资产。
> 结论先行：本地仓库能直接核验五 expert mix、student route metadata、coldstart500、student-rollout OPD5000、ZeRO 配置和 10k raw-holdout 表；但 Git 是“大快照 + 后续同步”形态，且初始 OPD scaffold 使用 `msz136` 身份，后续材料使用 `mousongzhe` 身份。它们不能自动合并为“候选人逐文件独立原创”。当前可说“候选账号提交了这些快照，项目材料自述负责数据/训练/评估设计”，不可说所有代码、远端权重和指标均由候选人独立完成或拥有。

## 1. 问题（Question）

面试官问“OPD 哪部分是你做的？”时，需要同时拆开：

1. OPD / 多教师蒸馏的公开背景与项目已有 scaffold；
2. 本地 commit 中确实存在的脚本、配置、manifest、summary 与评估表；
3. 候选人亲手设计、修改、运行、审查或验收的动作；
4. 协作者、历史账号、远端运行者和工具辅助的边界；
5. checkpoint、raw prediction、scorer 和最终数字的结果归属。

本页是 ownership ledger，不是把简历中的“设计/构建”重新认证为个人贡献。没有候选人逐项确认或过程证据的行保持 `role-confirmation-pending`。

## 2. Role Fit 与 JD 能力映射

| 岗位能力 | 本地可核证据 | Ownership 强度 | 当前策略 |
| --- | --- | --- | --- |
| VLM grounding 数据工程 | 五 expert 配额、image-hash split、source-line/fingerprint 与 route metadata | local-direct；个人决策待确认 | 可讲数据合同和泄漏 gate，不说全量数据由本人独立标注 |
| 多教师 / 在线蒸馏 | `point/train_opd_online_vl.py`、coldstart/OPD run summary、full-vocab KL 字段 | 代码和 summary 强；运行者、设计者待确认 | 区分 metadata route 与 learned router，区分 teacher rollout 与 student rollout |
| 分布式训练工程 | `preloaded_zero3`、`zero3_opd_maca_gradclip5.json`、skip/prefix/save 配置 | local-direct；远端运行闭环缺 | 可解释 ZeRO-3 合同，不声称性能或恢复收益 |
| 评估协议设计 | 10k raw-holdout、dedupe audit、strict/protocol-fixed/lenient point 口径 | local-direct / protocol-bounded | 先讲 scorer 和分母，再讲数字；不能把静态 holdout 写成机器人成功率 |
| 结果与因果归因 | ckpt1000–5000 by-format/by-pool 表 | report-supported / C3 未闭合 | 报告组合路线结果，不写 OPD 单因果 uplift 或“本人拥有 checkpoint” |

## 3. Ownership 证据合同

### 3.1 五层 AND-gate

强主张“我负责并完成了 X”需要同时满足：

\[
G(c)=I(c)\land A(c)\land D(c)\land V(c)\land O(c).
\]

`I` 是文件/commit/run identity，`A` 是 artifact，`D` 是设计与修改过程，`V` 是运行或验收，`O` 是个人、协作者、工具和上游边界。Git author 只覆盖 identity 的一部分；代码存在、summary 数字和 report 也不能替代 decision、verification 或 ownership。

### 3.2 状态词汇

| 状态 | 含义 | 可用动词 |
| --- | --- | --- |
| `scaffold-snapshot` | 初始项目快照中存在 | “项目快照包含” |
| `git-coarse` | 候选账号提交，但没有逐文件历史 | “由候选账号提交快照” |
| `self-attested` | 简历/项目页自述本人负责 | “候选人自述负责” |
| `role-confirmed` | 候选人逐项说明亲手/协作/工具边界 | “我负责/我修改” |
| `process-supported` | 有 diff、命令、失败复盘或 review 证据 | “我设计并验证” |
| `result-owned` | checkpoint、协议、raw outputs、运行者和审查角色均闭合 | “我完成并得到……” |

## 4. Git 与 run lineage 冻结事实

### 4.1 仓库与身份

| 检查 | 结果 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| 当前 HEAD | `756e27e16adcfb3ccbfe98c2920dda42095b127f`，2026-07-07；author/committer `mousongzhe <mousongzhe@acerobotics.com>` | 当前 snapshot 的提交身份与版本 | 每一行代码均由该人独立编写 |
| 初始 project code | `929e650fa1e6d745942eed1eab64dd8fb7833d2a`，author/committer `msz136 <msz136@users.noreply.github.com>` | 仓库最早的代码快照身份 | `msz136` 与候选人的现实身份是否相同 |
| OPD scaffold | `9700efb301fef4253ef3a703d91ba61e69cae1a6`，45 files / 5,912 additions，`msz136` | `opd_project` 训练/eval scaffold 在该快照进入 | 候选人是否亲手写、移植或审查 scaffold |
| OPD data/eval batch | `3ef636bdbfcf9654bd47719acc0dffb3b9095b6f`，`mousongzhe` | 五 expert builder、student builder、audit、raw-holdout evaluator/report 进入候选账号提交 | 远端运行者、个人设计过程和逐行 ownership |
| OPD5000 sync | `4c4bbfd42b1d7efee87de0d7eff78d4277fe38d4`，`mousongzhe` | `point/train_opd_online_vl.py`（1,015 行）及 coldstart/OPD5000 launch、manifest/table 进入 | summary 中的远端权重和 raw predictions 属于谁 |

`point/train_opd_online_vl.py` 与根目录 `train_opd_online_vl.py` 不是同一 artifact：当前 SHA-256 分别为 `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336`（1,015 行）和 `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9`（832 行），二者差异为 203 additions / 20 deletions。OPD5000 manifest 指向 `/data/msz/point/train_opd_online_vl.py`，所以结果叙事必须绑定 `point/` 版本和对应 run，而不是用根目录副本代替。

### 4.2 结果与资产边界

`report/opd5000_newexperts_20260601/artifact_manifest.json` 明确本地只同步 code/scripts/configs/logs/eval summaries，排除模型权重、optimizer `.pt`、raw holdout JSONL 和 `predictions.jsonl`。因此：

- `local-direct`：源码、配置、manifest、summary/table 的字节和 SHA；
- `report-supported`：远端 run 的参数、路径和指标摘要；
- `protocol-bounded`：10k raw-holdout 的 scorer、pool、checkpoint 和 n 可读，但不能复算所有样本；
- `result-owned`：当前未达到，不能把 `OPD final` 或 `OPD5000 ckpt5000` 写成候选人个人 checkpoint/result ownership。

## 5. Per-file / per-decision ownership matrix

| ID | 文件 / 决策 | Local artifact 事实 | Git / run 事实 | 当前 role verdict | 当前安全口径 | 升级所需证据 |
| --- | --- | --- | --- | --- | --- | --- |
| `OPD-OWN-001` | `opd_project/` 初始训练/eval scaffold | 配置、teacher forward、smoke、eval、REPORT 由 `9700efb` 一次加入 | author 是 `msz136`；无更早逐文件历史 | `scaffold-snapshot / identity-unverified` | “项目快照包含 OPD scaffold” | 账号映射、来源/patch、候选人 review 或修改记录 |
| `OPD-OWN-002` | `build_expert_mixes_seed0_v2.py` 五 expert mix | 800k/20k、image-hash 5% candidate split、五域配额和 relation buckets；SHA `19D5…F2C2C` | 580 行一次进入 `3ef636b`，候选账号提交 | `local-direct / git-coarse / role-pending` | “本地实现了可追溯的五 expert 数据构造脚本” | 设计决策记录、替代配比、运行 stdout、候选人逐项确认 |
| `OPD-OWN-003` | `build_opd_student_v1.py` route metadata | 999,900 train、46,599 eval、target/candidate/seen/unseen/hard/boundary/format-conflict 字段；SHA `44BC…D3BE` | 700 行一次进入 `3ef636b` | `local-direct / git-coarse / role-pending` | “student 数据写入了 route 与格式合同” | 选 60/25/10/5 的依据、现场解释函数、实际生成日志 |
| `OPD-OWN-004` | `audit_opd_student_v1.py` 数据审计 | JSON、坐标、长度、图片/fingerprint/overlap 检查；SHA `B38F…D6BB` | 431 行一次进入 `3ef636b` | `local-direct / verification-role-pending` | “本地有硬校验和 leakage audit” | 谁运行、失败样例、修复 diff、审查结论 |
| `OPD-OWN-005` | semantic-nav box 清洗与伪标签筛选 | `point/build_clean_grounding_pool.py`、`build_semantic_nav_eval_set.py`；简历自述 13,879 boxes / 41,637 rows | 两文件在 `9df95cc` 一次加入；底层标注和远端执行不在本地 | `self-attested / artifact-direct / role-pending` | “项目材料自述先做 box 清洗和场景数据扩充” | 原始输入、过滤阈值、人工/模型标注角色、held-out raw bundle |
| `OPD-OWN-006` | raw-holdout 构造与去重 gate | 10k quota、0 fingerprint/source-line/prompt-answer-image duplicate、0 train-image leakage；`evalset_summary` SHA `200F…6485`，`dedupe_audit` SHA `2E10…F96D` | 进入 `3ef636b`；评估样本和 predictions 未完整同步 | `process-supported / result-role-pending` | “我能解释评估集阻断泄漏的规则”仅在候选人确认后使用 | build command、冻结 prompt hash、逐样本 JSON、候选人运行/审查记录 |
| `OPD-OWN-007` | `point/train_opd_online_vl.py` teacher route 与 full-vocab KL | 1,015 行；`target` route、`preloaded_zero3`、teacher/student rollout、prefix loss、full-vocab support | 9df 初始进入，4c4 增补；实际 manifest 指向 `point/` SHA `7103…6336` | `local-direct / git-coarse / role-pending` | “项目实现了 route-driven online OPD 训练路径” | 亲手函数清单、before/after diff、训练命令、失败复盘与 review |
| `OPD-OWN-008` | coldstart500 launch 与 summary | teacher rollout、max_new_tokens=128、prefix=64、500 steps；summary SHA `90FD…D5FC0` | launch/summary 在 `4c4bbf`；模型权重和 optimizer state 排除 | `report-supported / operator-pending` | “报告记录五教师 coldstart500 配置” | remote log、checkpoint load smoke、运行者与候选人验收角色 |
| `OPD-OWN-009` | OPD5000 launch、skip 和 checkpoint schedule | student rollout、skip=64,000、max_new_tokens=64、prefix=64、save 1000–5000；summary SHA `2D67…547CE` | launch/summary 在 `4c4bbf`；manifest remote root `/data/msz/point` | `report-supported / result-owner-blocked` | “报告记录 OPD5000 run lineage 与 checkpoint 曲线” | immutable run manifest、权重/optimizer/RNG、raw predictions、operator/reviewer |
| `OPD-OWN-010` | ZeRO-3/MACA 与 teacher residency contract | `point/configs/zero3_opd_maca_gradclip5.json` SHA `CA5C…655F`；summary 写 `preloaded_zero3` | config 由 9df/3ef/4c4 逐步出现；无 matched memory/throughput A/B | `engineering-choice-supported / decision-owner-pending` | “采用了 ZeRO-3 与 resident teacher 约束” | 为什么常驻、显存/吞吐对照、MACA traceback、候选人决策记录 |
| `OPD-OWN-011` | raw evaluator 与 point protocol | `eval_qwen_vl_raw_holdout.py`、strict/protocol-fixed/lenient 口径；evaluator SHA `2957…206B` | evaluator 在 3ef/4c4；早期 prompt/parser mismatch 已在报告修正 | `process-supported / scorer-owner-pending` | “我把格式合规和几何能力分开审计”需候选人确认 | scorer version/prompt hash、parser tests、逐样本 predictions、review history |
| `OPD-OWN-012` | by-format / by-pool checkpoint 表与综合选择 | ckpt3000 IoU 最佳、ckpt5000 point/box Acc、ckpt4000 text 最佳；表 SHA `7D79…9934` / `54CA…ADCA` | tables/model assets 在 `4c4bbf`；不同 pool 最佳点不一致 | `report-supported / selection-role-pending` | “checkpoint 选择是多目标 trade-off，不是单一全局最佳” | selection freeze、未触碰 holdout 的选择集、候选人判断记录 |
| `OPD-OWN-013` | 结果归属与简历数字 | `REPORT.md` SHA `0EC1…4170`、manifest SHA `0357…21A`；OPD final 与 OPD5000 分离 | report/summary 是候选账号提交的文本快照；无本地 weights/raw predictions | `report-supported / C3-blocked / candidate-confirmation-pending` | “报告记录组合路线结果；我不把它升级为个人独立 checkpoint ownership 或单因果 uplift” | checkpoint bytes/load、同 suite ablation、raw scorer bundle、运行/分析/审查三方角色 |

## 6. Claim → ownership reconciliation

| 面试/简历 claim | 当前证据合同 | 安全处理 |
| --- | --- | --- |
| “设计五域数据与 OPD 路由” | 脚本和项目页支持设计形态；个人决策与过程记录未闭合 | 候选人确认前用“项目构建/本地实现”；确认后再用“我设计” |
| “训练了五个 expert 并完成 OPD5000” | summary/report 支持 run 参数和曲线；权重、optimizer、operator 缺 | 说“报告记录该 run”，不说“我独立训练并拥有 checkpoint” |
| “OPD 比 SFT 高 11.5pp” | 旧版/新版 lineage、数据和 scorer 不完全同一；无 SFT-only / single-teacher ablation | 禁止单因果归因；拆为组合路线和 protocol-bounded comparison |
| “point strict=0 说明 base 不会定位” | prompt/parser mismatch；lenient 与 protocol-fixed 结果相反 | 必须同时讲 original strict、protocol-fixed strict、lenient geometry |
| “10k raw-holdout 证明真实导航成功率” | 静态 box/point/text，虽有 semantic-nav 字段但无 episode/action trace | 只说静态 grounding/VQA holdout，不写 VLN/ObjectNav 或真机成功 |
| “这些代码都是我写的” | 候选账号 coarse commits + 初始 `msz136` scaffold，没逐文件历史 | 用 per-file ledger；明确 candidate confirmation pending |

## 7. Production Gap：抗追问最小补证据

| Gap | 面试官追问 | 最小补证据 | 当前表达 |
| --- | --- | --- | --- |
| 身份/快照边界 | `msz136` 和 `mousongzhe` 是谁？ | 账号映射、贡献记录、pre-snapshot patch | 保持 `identity-unverified` |
| trainer 版本 | 为什么根目录和 `point/` 不同？ | run manifest 绑定 script SHA、命令和代码 diff | 只绑定 manifest 指向的 `point/` |
| checkpoint | 权重能加载吗？ | binary SHA、processor/config、load smoke | `report-supported` |
| raw result | 0.5238/0.8729 如何复算？ | raw predictions、scorer commit、逐样本 JSON | `protocol-bounded` |
| 因果 | OPD 单独贡献多少？ | matched SFT-only/single-teacher/no-synthetic ablation | 不做单因果归因 |
| 运行角色 | 谁在 remote 执行和验收？ | shell history、run owner、reviewer、failure timeline | `operator-pending` |
| 数据质量 | 13,879 boxes 谁标注/筛选？ | 输入 manifest、过滤日志、抽检与标注角色 | 只说项目材料自述 |
| 工具协作 | 哪些由 AI/协作者生成？ | contribution ledger、review notes、现场解释 | 不推断 Codex-primary |

## 8. Question Tree 与回答分层

```text
你个人做了什么？
  ├─ 数据：五 expert 配额、hash split、route metadata 的设计者是谁？
  ├─ 训练：point/根目录脚本哪一版真的跑了？为什么 full-vocab KL？
  ├─ 评估：strict/parser mismatch 如何发现？holdout 如何阻断泄漏？
  ├─ 结果：ckpt5000 为什么不是所有 pool 最好？旧版 OPD final 是否同一 run？
  └─ ownership：哪些亲手、协作、工具辅助、只审查或只运行？
```

**危险回答**：Git author 是我，所以五个 expert、远端训练、checkpoint 和所有指标都是我独立完成的。

**可过回答**：我会把项目拆成数据、训练、评估和结果四条链。当前本地能直接核验五 expert mix、route metadata、`point/` 训练脚本、scorer 和报告表；但初始 scaffold 使用另一 Git 身份，OPD5000 权重/raw predictions 未同步，所以我只把候选账号提交的快照和项目自述称为参与证据，逐文件亲手/协作边界等候确认。

**强回答（候选人确认并补证后才可用）**：我能从一个具体函数说明输入、route、teacher forward、KL、保存和 scorer 的完整链路，并指出哪些决策由我做、哪些由协作者或工具实现；对于 `OPD final` 与 OPD5000，我会给出独立 manifest、checkpoint、prompt/scorer hash 和 raw predictions，不把组合提升包装成 OPD 单因果结果。

## 9. SP/SSP 证据就绪度

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.5 | grounding、蒸馏、分布式训练与评估均直接相关 |
| 机制深度 | 4.0 | 五 expert、route、coldstart、student rollout、full-vocab KL 和 protocol boundary 可解释 |
| 工程闭环 | 3.5 | scripts/configs/reports 完整；weights/optimizer/RNG/load smoke 缺 |
| 指标可信度 | 2.5 | raw-holdout table 与 leakage audit 可读；raw predictions/scorer bundle 未闭合 |
| Ownership 清晰度 | 2.0 | 13-row ledger 已建立；初始身份、逐文件角色和运行者仍待确认 |
| 抗追问能力 | 3.0 | 机制与限制可讲；diff、checkpoint、因果和工具边界仍有断点 |
| 合计 | **19.5 / 30** | 这是证据就绪度，不是候选人能力评分；WARN 不变 |

## 10. 候选人确认表

下一次口述或材料核对时逐项回答“亲手 / 协作 / 工具辅助 / 只审查 / 只运行 / 不确定”：

1. `msz136` 与 `mousongzhe` 是否为同一实际贡献者？如果是，依据是什么？
2. 五 expert 配额、image-hash split 和 relation bucket 是谁决定的？有哪些被否决的配比？
3. `build_opd_student_v1.py` 中的 `seen/unseen/hard` 和 `format_conflict` 哪些字段由你设计或修改？
4. `point/train_opd_online_vl.py` 哪些函数由你亲手写、修改、review 或只运行？实际 run 是否就是该 SHA？
5. coldstart500 与 OPD5000 是谁在 remote 执行、监控和验收？你看过哪些原始日志？
6. point strict/protocol-fixed/lenient scorer 的 mismatch 是谁发现和修正的？
7. `OPD final`、OPD5000 ckpt5000 的 checkpoint、raw predictions 和结果表分别由谁生成、审查和保管？
8. 哪些数据清洗、伪标签、报告或脚本由协作者、历史代码或 AI 工具产生？你如何验证它们？

这些问题没有真实回答前，不创建 `coaching_state.md`，不把任一行升级为 `role-confirmed` 或 `result-owned`。

## 11. 分阶段补强计划

| 阶段 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 完成 8 项候选人 ownership drill；每个关键函数选一个现场解释点 | 13 行均有 role/source/verification 字段 | 待候选人确认 |
| 1 天 | 导出 `point/` run 的 script/config/data/scorer manifest，标记 `msz136` 与 `mousongzhe` 身份关系 | OPD5000 lineage 不再依赖 path/summary 单点 | 待补做 |
| 3 天 | 补 checkpoint load smoke、raw predictions 和三套 point scorer | C3 结果链至少可复算一条 checkpoint | 待补做 |
| 1 周 | 固定同一 raw-holdout 做 SFT-only、single-teacher、no-synthetic/synthetic-ratio 对照 | 组合效果可拆为可审查的机制证据 | 待补做 |

## 12. Output Pack

### 12.1 简历 bullet 三档

- **当前保守版**：参与 VLM grounding 数据清洗、五 expert 路由与 online OPD 训练/评估闭环；以 raw-holdout、point protocol 和 checkpoint 曲线拆分组合结果与证据边界。
- **候选确认后标准版**：负责五域数据配比、route metadata、五教师 coldstart/OPD 训练 contract 及 strict holdout scorer 的设计与审查；具体文件按 ownership ledger 说明亲手与协作边界。
- **补齐 C3 后偏强版**：在固定数据、scorer、checkpoint lineage 和 raw predictions 下，完成 SFT-only/single-teacher/OPD 对照并给出可复算的多格式结果；当前禁止提前使用。

### 12.2 两分钟叙事骨架

> 我先按 image-hash 做 train/eval 隔离，再把 reasoning、object、region、spatial relation 和 RoboPoint 组织成五个 expert，并在 student 行里保留 target/candidate route、seen/unseen、boundary 和 format-conflict。训练先用五教师 rollout 做 coldstart，再让 student rollout，由 route 对应 teacher 在同一 response 上做 full-vocabulary KL；这里的 route 是 metadata 驱动，不是已验证的 learned router。评估用 10k raw-holdout 按 box/point/text 分开，并区分 original strict、protocol-fixed strict 和 lenient geometry。OPD5000 ckpt5000 的 point/box/text 数字属于一条 report-supported new-experts run，不和旧版 OPD final 拼成一条曲线。我的具体个人贡献要按 ledger 中逐文件回答，当前不把 Git author、summary 或 report 当作独立 ownership 证明。

### 12.3 面试前 6 题

1. 为什么五 expert 不直接混合成一个 SFT 数据集？
2. `target_expert` route 和 learned router 的训练/部署差别是什么？
3. coldstart teacher rollout 与 OPD5000 student rollout 的数据流和 loss 有何不同？
4. 为什么 full-vocabulary KL、prefix=64、skip=64,000、`preloaded_zero3` 会同时影响工程合同？
5. point strict=0、protocol-fixed strict 和 lenient geometry 如何避免错误归因？
6. 请从 `point/train_opd_online_vl.py` 的一个函数开始，说明哪些是你亲手、协作、工具辅助、只审查或只运行的。

## 13. Ownership 审计伪代码

```python
def accept_opd_claim(claim, ledger):
    if not ledger.identity_and_artifact(claim):
        return "reject_strong_claim"
    if not ledger.role_confirmed(claim):
        return "use_project_contains_or_candidate_attested"
    if claim.level >= "C2" and not ledger.process_and_verification(claim):
        return "downgrade_to_implemented_or_reviewed"
    if claim.level == "C3" and not ledger.checkpoint_protocol_raw_chain(claim):
        return "report_summary_only"
    return "claim_allowed_with_exact_scope"
```

这段伪代码是本仓库的真实性 gate，不是 OPD 官方实现。

## 参考文献（References）

1. [OPD Claim–Evidence Inventory](opd_claim_evidence_inventory.html)：五 expert、student route、训练 lineage、raw-holdout、point protocol 与当前 WARN 边界。
2. [OPD Batch 1 项目题卡](../../questions/proj_opd.html)：8 张 direct-evidence-bounded unseen cards；本 ledger 新增 ownership 题卡。
3. [Evidence Manifest](../evidence_manifest.html)：五项目 evidence 与 ownership 状态总索引。
4. [VLA Knowledge Map](../../knowledge/00_vla_knowledge_map.html)：VOL 07 项目深挖与题目 ID 空间。
5. Local Git repository `C:\Users\mousongzhe\muxi`，HEAD `756e27e16adcfb3ccbfe98c2920dda42095b127f`；初始 scaffold `9700efb301fef4253ef3a703d91ba61e69cae1a6`；OPD data/eval `3ef636bdbfcf9654bd47719acc0dffb3b9095b6f`；OPD5000 sync `4c4bbfd42b1d7efee87de0d7eff78d4277fe38d4`。
6. `report/opd5000_newexperts_20260601/artifact_manifest.json`（SHA-256 `035764A0461DEE5942AB25AF1BDFCD2514BD69AAC473B2DE8E43F3A7EC86021A`）：明确排除 weights、optimizer、raw holdout 与 predictions。
7. [Optimized Resume](../../../../output/mousongzhe_resume_optimized.html) 与 [OPD 项目面试页](../../../02_opd_vlm_grounding.html)：当前候选人自述和投递口径，未经本 ledger 自动认证。
