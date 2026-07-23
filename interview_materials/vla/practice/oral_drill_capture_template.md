# VLA 单题真实口述捕获模板

> 状态：`capture_template / awaiting_candidate_answer / no_mastery_change`
> 更新日期：2026-07-22
> 用途：为真实口述保留原始回答、自评、证据核验、反馈和状态迁移记录。每次只复制并填写一题；模板本身不是 transcript，不创建 `coaching_state.md`。

## 1. 使用协议

1. 从 [真实口述队列](oral_drill_queue.html) 只选择当前队首的一题。
2. 候选人先提交自然口述或逐字稿；不要先阅读对应 model answer。
3. 保存原始回答后，候选人先写自评，再由教练核验事实和评分。
4. 没有真实回答时，下面所有评分保持空白，题卡继续为 `unseen`。
5. 收到真实回答后，才允许创建或更新 `coaching_state.md`，并且只迁移本题状态。

## 2. 题目与会话身份

| 字段 | 填写值 |
| --- | --- |
| Session ID | 【回答后填写；建议 `YYYYMMDD-HHMM-<stable-id>`】 |
| 日期/时区 | 【回答后填写】 |
| Stable ID | 【例如 `PROJ-WAM-001`】 |
| 原始题目 | 【从题卡原样复制】 |
| 回答形式 | 【语音转写 / 现场逐字稿 / 手写复述】 |
| 目标时长 | 【30 秒 / 90 秒 / 2 分钟】 |
| 实际时长 | 【回答后填写】 |
| 是否先看 model answer | 【是 / 否；如是必须记录】 |

## 3. 原始回答：先保存，不润色

### 3.1 Verbatim transcript

> 【候选人的原始回答；保留停顿、改口、数字和不确定表达，不在这里替换成标准答案】

### 3.2 候选人自评

- 我认为回答最强的一点：【填写】
- 我最不确定的一点：【填写】
- 我可能越过证据边界的 claim：【填写；没有也要写“未发现”】
- 如果重答一次，我首先会改：【填写】

## 4. Claim–Evidence–Ownership 核验

| 回答中的 claim | 证据文件/锚点 | 证据等级 | checkpoint/protocol/分母 | ownership | 处理 |
| --- | --- | --- | --- | --- | --- |
| 【逐条摘录】 | 【本地路径、日志行、题卡来源】 | `local-direct / report-supported / inference / unverified` | 【缺失则明确写 missing】 | `hands-on / collaboration / tool-assisted / review-only / run-only / unverified` | `保留 / 降级 / 删除 / 待补证` |

证据入口可从 [Evidence Manifest](../evidence/evidence_manifest.html)、[P0 Artifact Intake Contract](../evidence/p0_artifact_intake_contract.html) 和对应项目 inventory/ownership ledger 中选择。不能用 Git author、文件名、上游论文、model answer 或 summary 本身替代个人 ownership 与 raw artifact。

## 5. 防越界检查

- [ ] 没有把上游架构或论文机制写成个人原创。
- [ ] 每个强数字都绑定 checkpoint、数据版本、protocol、分母、scorer 和 raw/summary 等级。
- [ ] 没有把用户确认、远端路径或报告摘要冒充本地 raw bundle。
- [ ] 没有把训练 loss、offline metric、contact 或单条 episode 直接等同 closed-loop success。
- [ ] 明确区分 first verified divergence、root-cause hypothesis 与已验证修复。
- [ ] 明确区分亲手实现、协作、工具辅助、只审查、只运行和未知 ownership。
- [ ] 没有把 implementation-derived model answer 当作候选人 transcript。
- [ ] 至少主动说明一个当前 `unverified` 缺口及最小补证动作。

## 6. 教练反馈：回答后填写

### What I Heard

【用中性语言复述候选人实际说了什么，不加入标准答案】

### What Is Working

【先记录真实优势，绑定 transcript 片段】

### Gaps To Close

【记录最关键的机制、结构、相关性、可信度或差异化缺口】

### Scorecard

| 维度 | 分数 1–5 | transcript/证据依据 |
| --- | ---: | --- |
| Substance |  |  |
| Structure |  |  |
| Relevance |  |  |
| Credibility |  |  |
| Differentiation |  |  |

**Confidence**：【`High / Medium / Low`；说明 transcript 完整度和证据覆盖】。

### Priority Move

【只写下一次重答最重要的一个动作】

### Next Step

【默认仍处理本题重答；只有达到当前 gate 后，才由队列进入下一 Stable ID】

## 7. 状态迁移规则

| 条件 | 允许状态 | 禁止动作 |
| --- | --- | --- |
| 没有候选人回答 | `unseen` | 不评分、不创建 coaching state |
| 有回答但关键机制/证据错误 | `weak` | 不因表达流畅升级为 pass |
| 30–90 秒内正确回答且不越界 | `pass` | 不自动声称项目结果已 verified |
| 能补机制、trade-off、项目锚点和追问 | `strong` | 不把一次强回答扩展到其他题卡 |
| 过去通过但证据或间隔已变化 | `stale` | 不沿用旧分数替代复练 |

真实回答完成后，应把 verbatim transcript、五维评分、Confidence、证据缺口和下一步写入正式训练状态；题卡、master index 与 review 只同步本题的实际迁移。保留本模板为空白基线，不直接覆盖它。

## 8. 入口

- [真实口述队列](oral_drill_queue.html)
- [队列 Readiness Audit](oral_drill_readiness_audit.html)
- [题卡总索引](../questions/00_master_question_index.html)
- [Ownership Confirmation Queue](ownership_confirmation_queue.html)
- [五项目 Evidence / Ownership Reconciliation](../sources/vol_07_project_evidence_reconciliation.html)
