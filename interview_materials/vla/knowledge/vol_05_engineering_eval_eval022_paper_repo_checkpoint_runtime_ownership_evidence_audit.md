# VOL 05 Engineering / Evaluation：EVAL-022 Paper→Repo→Checkpoint→Runtime→Ownership Evidence Audit

> 状态：`drafted / VLA-EVAL-022 / knowledge_44_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 难度：L3　优先级：P0  
> 来源冻结：[EVAL-022 Source Freeze](../sources/vol_05_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit_source_freeze.html)  
> 本页建立claim→paper/data/model docs→repo/code/config→run→checkpoint→runtime→raw eval→metric与独立ownership链；不把paper、路径、report、hash、commit author或签名替代完整复现与个人贡献证据。

## 1. 问题与30秒框架

面试里的强claim要拆成两条相交但独立的链：技术证据链证明“哪个版本、什么数据和配置、哪个checkpoint/runtime产生了什么raw结果”；贡献链证明“你在哪些文件、决策、实验和验收中承担了什么角色”。paper、repo、checkpoint path、summary和Git author各只覆盖一层，任一必需边缺失就把表述降到前一层。

```text
claim atoms
 -> paper/model card/datasheet
 -> official repo revision + exact code/config
 -> dataset + resolved run
 -> checkpoint bytes/load
 -> runtime + raw outputs
 -> scorer/protocol/result

parallel: contribution role -> scope -> diff/decision/run/review evidence
```

## 2. 九级证据链

| 层级 | 证明什么 | 不证明 |
| --- | --- | --- |
| E0 claim | 某人/文档曾这样说 | claim正确 |
| E1 docs | paper/model/dataset公开设计与声明 | 本地采用/复现 |
| E2 repo | 某revision有相关实现 | 实际执行 |
| E3 run intent | config/data/command计划了run | run完成 |
| E4 checkpoint | bytes可识别、可加载、lineage明确 | metric有效 |
| E5 runtime | 指定环境真正执行该bundle | benchmark正确 |
| E6 raw eval | predictions/episodes/traces存在 | aggregate解释正确 |
| E7 result | 同协议可重算summary | 因果、部署价值 |
| E8 ownership | role/scope有独立证据 | 独立完成全部项目 |

远端路径最多是E3线索；summary没有raw rows最多是report-supported E7输入，不会反向补齐E4–E6。

## 3. 四个正交问题

| 问题 | 证据 |
| --- | --- |
| Identity：到底是哪一个对象？ | immutable ID、version、SHA、lineage |
| Integrity：bytes是否漂移/篡改？ | digest、signature、attestation |
| Semantic validity：对象是否支持claim？ | code path、resolved config、runtime/raw/protocol |
| Ownership：谁做了什么？ | contribution role、scope、diff、decision、execution、review |

hash或签名能强化identity/integrity，但不能自动证明算法语义、指标或个人贡献。

## 4. Claim Atomization

“我复现论文并将成功率提升到X”至少拆成：

1. paper/version和方法定义；
2. official repo/revision与code path；
3. local diff/config/data是否走该路径；
4. run是否开始/结束；
5. checkpoint bytes与load；
6. runtime是否加载该bundle；
7. raw eval是否由该runtime产生；
8. scorer/protocol是否算出X；
9. baseline是否同协议；
10. 个人Methodology/Software/Investigation/Validation贡献。

面试回答按原子claim逐项给证据；不要用一句模糊“复现了”遮住断边。

## 5. Model Card / Datasheet 的作用

Model Cards建议记录model version/details、intended/out-of-scope use、factors、metrics、training/evaluation data与limitations。[1] Datasheets记录dataset motivation、composition、collection、preprocessing/labeling、uses、distribution和maintenance。[2]

它们帮助解释“发布者声称什么、适用边界是什么”，但不替代：

- checkpoint或dataset bytes；
- 当前snapshot SHA；
- local run/load/forward；
- raw benchmark；
- personal contribution。

对VLA还需camera/state/action/time/robot/site/task、normalizer、controller和license字段。

## 6. Repo / Code / Config Gate

official repo由paper/model card/组织主页交叉指定。冻结URL、commit/tag、submodule/LFS、dirty diff、license、exact symbol/call path、config default及CLI/env override。

三个高频误区：

- README写了feature，不等于当前revision实现或启用；
- config有字段，不等于forward/loss消费；
- 本地有源码，不等于正式run走到该branch。

需要static mapping与runtime branch evidence共同闭合。

## 7. Data / Run Gate

run至少绑定：code/patch、dataset snapshot/split、resolved config、base checkpoint、processor/normalizer、seed/sampler、hardware/runtime、job ID、start/end/exit和output manifest。

launcher或配置只能证明intent。完整run evidence应包含scheduler/job记录、完整log、loss/异常、checkpoint save manifest和所有失败attempt；不能只保留成功目录。

## 8. Checkpoint Gate

路径不是checkpoint。完整bundle包括：

- weight bytes、size、format、SHA；
- model config/class、processor/tokenizer、normalizer/stats；
- action dimension/order/unit/frame、chunk与controller；
- parent run/step、optimizer/scheduler（若claim含resume）；
- strict load、fixed-input forward、shape/finite和round-trip；
- weights/repo/data各自license。

load report若未绑定被测binary SHA，也不能证明当前文件可加载。[3]

## 9. Runtime / Raw Eval Gate

runtime证据包含exact command、cwd、env/container、deps、driver/backend/hardware、resolved branch、load/forward/rollout、exit/retry以及raw output SHA。

metric链：

```text
raw prediction/episode
 -> versioned parser/scorer
 -> per-unit result
 -> slice/aggregate + denominator
 -> uncertainty + invalid/missing
```

smoke只证明短路径，不能替代formal training、完整benchmark或real deployment。summary-only不能升级为raw-verified。

## 10. Evidence Graph 是 AND Gate

claim `c`需要节点`R(c)`和语义边`E(c)`：

\[
V(c)=
\left(\bigwedge_{v\in R(c)}I_v\right)
\land
\left(\bigwedge_{(u,v)\in E(c)}M_{uv}\right).
\]

变量解释：`I_v`检查对象身份/完整性，`M_uv`检查相邻层语义关系。直觉：paper和checkpoint都有，但run lineage缺失，强claim仍断。实现映射：claim registry列required nodes/edges、SHA与`PASS/OPEN/CONFLICT`。[4]

保守表述上限：

\[
L(c)=\min_{e\in R(c)}L(e).
\]

变量解释：`L(e)`是必需证据等级。直觉：强度受最弱必需环节限制。实现映射：这是审核规则，不是统计量；必要性必须在claim spec中预先定义。

## 11. SLSA Provenance 如何借鉴

SLSA把provenance定义为artifact从何处、何时、如何产生的可验证信息，并用subject、buildDefinition、external/internal parameters、resolvedDependencies、builder与runDetails组织。[3]

| SLSA | VLA训练/eval扩展 |
| --- | --- |
| subject | checkpoint/eval bundle + processor/normalizer/scorer |
| buildDefinition | trainer/evaluator + objective/protocol语义 |
| externalParameters | CLI/data/base checkpoint refs + resolved values |
| resolvedDependencies | code/data/base weights/deps digest |
| builder/runDetails | scheduler/container/GPU/backend/robot/simulator |
| byproducts | logs/loss/raw eval/incident artifacts |

本页只借其结构，不宣称五项目达到SLSA level。

## 12. Hash 绑定的边界

相邻artifact可通过manifest hash链绑定：

\[
h_{k+1}=SHA256\!\left(h_k\parallel m_k\parallel bytes_{k+1}\right).
\]

变量解释：`h_k`是上游digest，`m_k`是映射manifest。直觉：任一bytes变化都会改变链。实现映射：manifest引用data/config/checkpoint/scorer SHA；hash不证明code实现paper、data无泄漏、metric正确或ownership。

## 13. Git Identity 不是 Ownership

Git允许`--author`覆盖author，author/committer可来自环境变量；name本身不做authentication。[5] 签名能验证对象与key的关系，但不能证明：独立设计、全部代码为手写、目标run执行、指标产生或协作/工具辅助不存在。

所以Git author/committer只是ownership clue，需要file/function diff、review、decision和run evidence补强。

## 14. Contribution Role Ledger

CRediT提供Conceptualization、Data curation、Methodology、Software、Investigation、Validation等角色，且明确不用于决定authorship。[6]

每项贡献记录：person/actor、role、file/function/decision/experiment scope、proposed/implemented/reviewed/executed/verified activity、diff/run/review/witness evidence、solo/pair/team/upstream/tool-assisted及confidence。

不要伪造百分比。安全回答是“我设计了哪条protocol、改了哪个module、跑了哪些run、如何验收；上游/协作/工具分别是什么”。

## 15. License 分层

paper、repo、dataset、base weights、fine-tuned weights和runtime dependencies可能使用不同license。repo Apache/MIT不覆盖checkpoint或dataset。license manifest逐artifact记录source/version/text/hash、用途、再分发与商业限制；未知为`UNKNOWN`。

## 16. Contradiction Ledger

需要显式记录：paper/default与repo冲突、README/config/code/runtime冲突、report与raw冲突、path存在但binary缺、各层license不同、author与贡献口述冲突。

“当前workspace没找到”只证明审计scope内缺失；必须记录date、roots、pattern和excluded paths，不能断言远端永不存在。

## 17. 五项目真实性映射

### OPD

已闭合local code/config/manifests、data route、10k holdout leakage audit、by-format/by-pool tables和point protocol。缺checkpoint weights/optimizer、raw predictions、统一ablation、old-final→OPD5000 lineage。可讲设计和protocol-bounded结果，不能称完整复现或OPD单因果；Git author仍需逐文件/决策/协作ledger。[7]

### Robot Harness

runtime/tool registry、SFT/GRPO data、schema-aware reward和eval summaries可核。缺checkpoint/raw outputs、共同n/scorer、真实browser/robot episodes与完整lineage。可讲结构化工具/eval设计，不能把所有runtime/data/reward归为个人独立完成。

### OpenPiVLA

formal trainer、JSON/causal-CE、三类recipe、smoke/report/diagnostic和launcher是local-direct。formal checkpoint bytes/load、97.4 raw bundle与archive→formal lineage缺失，且`H=15,D=72`与formal `limit=16`冲突。97.4保持archive-summary-only，ownership为partial。

### WAM

public Cosmos paper→repo→model card→eval path已审计，本地简历已降级；当前workspace没有完整raw run/checkpoint/config/log/metric/episode bundle。只能讲上游审计、diagnostic和补证据设计，不能讲本地复现/uplift/root cause；public architecture不是个人原创。

### UWM / LIBERO

local scripts/report、protocol tuple、normalizer/action metadata、DataLoader smoke和user-confirmed summary存在；checkpoint binary、250 raw episodes/video、formal OOD/3-seed、fixed/reset pairs和ownership缺失。可讲迁移/协议/诊断，`186/250`保持user-confirmed/protocol-limited；UWM architecture属于upstream。

五项目都有清晰inventory，但都未完成E1→E8全链；本页不提升metric、复现、部署、因果或ownership等级。

## 18. 面试追问防线

- **有repo为什么不算复现？** repo证明实现存在；还缺data/config/run/checkpoint/runtime/raw eval链。
- **有checkpoint path还缺什么？** bytes/size/SHA、parent run、配套processor/stats、strict load和runtime绑定。
- **有summary为什么不能报？** 可以按summary等级报，但不能称raw-verified或独立复算。
- **commit author不是你吗？** 是参与线索；author可覆盖，且不能描述设计/协作/工具和运行验收。
- **签名能证明什么？** 对象与key关系，不证明semantic correctness或贡献范围。
- **怎么讲ownership？** 角色+scope+activity+diff/decision/run/review evidence，明确upstream与协作。
- **哪个项目链最完整？** OPD/OpenPiVLA/Harness有较多local-direct中间层，但强结果仍被checkpoint/raw/lineage/ownership断边限制。

## 19. 审计伪代码

```python
def audit_resume_claim(claim, graph, roles):
    # Split the statement into paper, execution, result and ownership atoms.
    atoms = atomize(claim)

    verdicts = []
    for atom in atoms:
        # Verify every mandatory artifact and semantic mapping edge.
        technical = graph.verify(required_contract(atom))

        # Verify contribution independently from Git identity or artifact integrity.
        ownership = roles.verify(atom.role, atom.scope)

        # Downgrade wording when any required edge is missing or conflicting.
        verdicts.append(limit_wording(atom, technical, ownership))

    return persist_verdicts_and_open_gaps(verdicts)
```

这是本仓库未来自动审计合同，不代表已存在claim verifier。[7]

## 20. 本节点状态

EVAL-022知识节点与一张题卡已起草并保持`WARN/unseen`；VOL 05知识/题卡达到`44/44`，但页面完成不等于口述掌握或五项目证据闭环。没有真实口述前不创建`coaching_state.md`。下一bounded slice建议做VOL 05 completion audit / independent fact review，随后再决定跨卷补证据或逐题口述。

## 参考文献（References）

1. Mitchell et al., [*Model Cards for Model Reporting*](https://arxiv.org/abs/1810.03993v2), 2019。
2. Gebru et al., [*Datasheets for Datasets*](https://arxiv.org/abs/1803.09010v8), 2021。
3. SLSA, [Provenance v1.2](https://slsa.dev/spec/v1.2/provenance)与[Build Provenance](https://slsa.dev/spec/v1.2/build-provenance)。
4. [EVAL-022 Source Freeze](../sources/vol_05_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit_source_freeze.html)。
5. Git, [`git-commit`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-commit.adoc)与[`git-commit-tree`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-commit-tree.adoc)。
6. NISO, [CRediT Role Descriptors](https://credit.niso.org/contributor-roles-defined/)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目claim–evidence inventories。
