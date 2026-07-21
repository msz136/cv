# VOL 05 EVAL-022 Source Freeze：Paper→Repo→Checkpoint→Runtime→Ownership Evidence Audit

> 状态：`source_frozen / VLA-EVAL-022 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结claim atomization、paper/model/data documentation、source/build provenance、repo/config/data/run/checkpoint/runtime/raw-eval证据边、identity/integrity/semantic-validity/ownership正交边界、contribution-role ledger、license分层与五项目真实性；只服务`VLA-EVAL-022`，不在本切片扩张新知识节点或口述状态。

## 问题（Question）

面试官问“论文方法是否真的落到你跑出的checkpoint、指标是不是这条runtime产生、哪些部分是你做的”时，怎样给出可审计答案？可靠做法不是甩出paper、GitHub链接、远端路径或commit author，而是把复合claim拆成原子命题，逐边证明paper→official repo revision→code/config/data→run→checkpoint bytes/load→runtime→raw outputs→scorer/result，并用独立贡献角色与文件/决策证据回答ownership。任何断边都必须降级表述。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Mitchell et al., *Model Cards for Model Reporting* | primary paper；FAT* 2019；arXiv `1810.03993v2`；ACM论文使用条件见PDF | PDF `a4049cdc78c3d635bdfb5165e495b0672d85690d66ccd6f149079d6e11e64aa1` | model details/version、intended/out-of-scope use、factors、metrics、training/evaluation data、limitations与分解评估 | model card等于checkpoint bytes、runtime执行、项目复现或个人ownership |
| S2 | Gebru et al., *Datasheets for Datasets* | primary paper；CACM/2021；arXiv `1803.09010v8`；论文许可未在本冻结中断言 | PDF `c7f595988ee2c109631d5173fdae37ff1774c68ec17add51bd012f2a6e8792d0` | motivation、composition、collection、preprocessing/labeling、uses、distribution与maintenance文档框架 | datasheet等于dataset bytes、当前snapshot、无泄漏、许可完备或本地训练使用证明 |
| S3 | SLSA v1.2 Provenance / Build Provenance | official specification；tag `v1.2` object `19e4e2f005f871270c4f555fc47afecfb37f3efe`；Community Specification License 1.0 | rendered page `9a176a8193aff28144dbab80584f0e9dd707a7c24f98c436349674a4a0e51e44`；tag zip `c6acc0f08e20e2cc329225da77dad864479d697bc214c87d0a8593d0c185808b`；`provenance.md` `89cae36d81bdd593b728ca09ff6804e87b07a762a36704c591ab784da5c9395e`；`build-provenance.md` `182ab5cf823c374874136371466ba43f99f0a9ba87a8046757d26a2ed74854a0`；schema `ea548207a78bd81b809a449edd5ed36a011a665ca7d15831d1133fe674fc41de`；LICENSE `f40b1d00369c21b963293189b4617b5de439a11858541c07c620984634fb63b7` | artifact subject、buildDefinition、external/internal parameters、resolvedDependencies、builder/runDetails/byproducts与可验证来源 | SLSA直接证明ML训练语义、benchmark有效性、checkpoint质量、论文一致性或个人贡献 |
| S4 | `git/git` commit / signature documentation | official-code/docs；commit `41365c2a9ba347870b80881c0d67454edd22fd49`；GPL-2.0 | `git-commit.adoc` `ec670cfacaf3df8745e9cfe2fa68b74247cb111e4208e1a0095036732cb5e717`；`git-commit-tree.adoc` `608e33a487db93f76d82401ac00110738f4569e31ce08c731cd7587a5ffb022d`；`gitformat-signature.adoc` `e99e9de49bb4d7566199956a44e886643faaf68333974ed055099a310595daf4`；COPYING `5b2198d1645f767585e8a88ac0499b04472164c0d2da22e75ecf97ef443ab32e` | commit对象中的author/committer、可覆盖author、环境变量身份、commit/tag签名格式 | Git name提供认证；签名证明独立设计/全部代码/运行结果；commit author等于exclusive ownership |
| S5 | CRediT Contributor Role Taxonomy | official NISO resource；ANSI/NISO standard approved 2022；CC BY 4.0；2026-07-19抓取 | home `cfdeb42ee05bad7321dca0892e475d1e8ed436ed89358909fd214a6cdf90d27f`；role descriptors `a06f925327fb1c2d4ebbbb35fdcfe97ee5f537d9dfcb2f2b0dc2dfdc64fa9ab9` | 14种contribution roles，如Conceptualization、Data curation、Methodology、Software、Validation、Writing | CRediT角色表本身决定authorship或证明某人实际完成某角色；项目贡献可用百分比随意分配 |
| S6 | 本地跨卷前置审计 | canonical local prerequisites | VOL03 Audit F `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809`；VOL04 benchmark audit `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a`；VOL04 independent review `115eed1c2c3d0d98adc46acde2e8effe12f0305b2f7ea2a81c7fa3ffac2503c1`；local ENG-004..006 gate `2ca6e710d21157a262391501e3c00838a718e84bce0bcc26e6b5eb8c816ef15d`；ENG-013 `af21822b7617fb3117768034c985737833de6a2a34f58ca42766f8a03c9b56ee`；ENG-021 `3159fd3b7e3331394ace1415b071e487cfebfb8a2ba06b94a7508803ae672bea`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-019 `01446407420dae1382eaccf503b66e1a06b2017e46a10b81bd13af81dc9568a0`；EVAL-020 `c85f5ca7ac79d3e942b0ba29916212435d7fe58ab6a28c254e1e25868a51397d` | paper/code/runtime chain、benchmark protocol、checkpoint artifact、reproducibility、bundle packaging、selection和incident证据合同 | 下游项目缺口已自动闭合或ownership已证明 |
| S7 | Evidence Manifest 与五项目inventories | local evidence | manifest `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6`；Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 当前workspace里每个项目的code/config/report/metric/checkpoint/runtime/ownership证据与缺口 | 其他机器/远端一定没有artifact；inventory作者等于项目全部ownership |

S1—S5冻结documentation、artifact provenance、Git identity与contribution roles；S6—S7把它们映射到VLA。下面的证据等级、claim graph、断边规则和ownership ledger是source-consistent engineering synthesis，不冒充这些来源的原始评分体系。

## 2. 先把一句强 Claim 拆成原子命题

“我复现了论文方法并提升到97.4%”至少包含：

1. 指定paper/version确实定义该方法与protocol；
2. 指定repo/revision是相关实现，而非同名fork；
3. 本地diff/config/data确实选择该实现路径；
4. run实际启动并完成目标训练/eval；
5. checkpoint bytes存在、可加载且来自该run；
6. runtime加载该checkpoint与配套processor/normalizer/controller；
7. raw outputs由该runtime产生；
8. scorer按冻结protocol复算出该数字；
9. 数字的scope/denominator/uncertainty正确；
10. “我”的Methodology/Software/Investigation/Validation贡献有独立证据。

只要其中一项缺失，必须把claim降级到已证明的前一层，不能用其他层的材料补洞。

## 3. 九级 Evidence Chain

| 级别 | 必要对象 | 最低证据 | 仍不能证明 |
| --- | --- | --- | --- |
| E0 claim | 简历/项目页/口述 | 原文、日期、版本 | 事实正确 |
| E1 paper/model/data docs | paper、model card、datasheet | version、DOI/URL、license、支持/不支持 | 本地采用 |
| E2 repo/source | official repo/revision/code path | commit/tag、tree/file SHA、license | code被执行 |
| E3 config/data/run intent | config、dataset manifest、command | resolved config、data SHA、run ID | run完成 |
| E4 checkpoint artifact | weights + config + processor/stats | bytes/size/SHA、parent run、strict load | 该runtime/metric正确 |
| E5 runtime execution | env/container/hardware/command/log | dependency lock、start/end、exit、load/forward smoke | benchmark结果有效 |
| E6 raw evaluation | predictions/episode/trace/video | sample IDs、raw rows、scorer bundle | summary解释正确 |
| E7 result/protocol | summary + recompute | denominator、support、CI、same protocol | 因果/部署价值 |
| E8 ownership | contribution ledger | role、file/diff/decision/review/witness | 独立完成全部项目 |

等级不是平均分。`E7 result`若checkpoint只到remote path，仍不能写成local-direct完整复现。

## 4. 四个问题必须正交

| 维度 | 问题 | 常见误替代 |
| --- | --- | --- |
| identity | 这是哪个paper/repo/data/checkpoint/run？ | 同名路径或latest标签 |
| integrity | bytes/manifest/attestation是否被篡改或漂移？ | 只有文件名/截图 |
| semantic validity | 实际执行的算法、protocol、metric是否匹配claim？ | SHA相同就认为结果正确 |
| ownership | 谁提出、实现、执行、验证、写作？ | Git author、目录owner或报告作者 |

签名和hash提高identity/integrity，不自动回答semantic validity或ownership。

## 5. Paper / Model Card / Datasheet Gate

### Paper gate

- 固定title、authors、venue/arXiv version、发布日期与license；
- 把claim定位到section/table/equation/appendix；
- 区分论文main method、ablation、future work与作者推测；
- 记录benchmark、dataset split、seed/trials、hardware和scorer；
- 不把论文数字写成本地数字。

### Model card gate

Model Cards建议记录model details/version、intended/out-of-scope use、factors、metrics、training/evaluation data与限制。[S1] 它能解释模型发布者的声明，但不是checkpoint byte attestation，也不证明本地load或eval。

### Datasheet gate

Datasheets覆盖motivation、composition、collection、preprocessing/labeling、uses、distribution和maintenance。[S2] 对VLA还要补observation/action schema、robot/site/task、camera、timestamp、normalizer、license和split/dedupe；文档存在不等于当前data snapshot与文档一致。

## 6. Official Repo 与 Source Revision Gate

“官方repo”需由paper/project/model card/组织主页交叉指定；fork可作为local implementation，但不能冒充upstream。冻结：

- repo URL、commit/tag、submodule/LFS、dirty diff；
- exact code symbol、call path、config default与CLI/env override；
- dependency/patch/license；
- paper claim到code path的语义映射与未实现项。

README写了feature不等于当前revision执行了feature；config字段存在不等于forward/loss/rollout消费它。

## 7. Data / Config / Run Gate

run intent至少绑定：

```text
run_id + parent_run
code/patch commit
dataset snapshot + split/dedupe
resolved config + CLI/env
base checkpoint + processor/tokenizer/normalizer
seed/sampler cursor/hardware/runtime
output root + retention
```

config模板、launcher和远端路径只证明“可计划/曾配置”，不证明job启动、完成或生成了正确artifact。需要scheduler/job ID、start/end/exit、完整resolved config、logs和artifact manifest。

## 8. Checkpoint Gate：路径不是权重

完整checkpoint bundle至少包含：

- weight bytes、size、SHA与format；
- config/model class、processor/tokenizer、normalizer/stats；
- action dimension/order/unit/frame、chunk/horizon与controller contract；
- parent run、step/tokens、optimizer/scheduler（若claim涉及resume）；
- strict load、fixed-input forward、output shape/finite与round-trip；
- checkpoint/model-card/repo各自license。

`/remote/path/ckpt-5000`、manifest里写`final_model`、训练日志写“saved”都不是本地checkpoint bytes。load report若不伴随被测binary SHA，也只能证明报告内容，不证明当前文件可加载。

## 9. Runtime Gate：代码存在不等于走到该分支

runtime证据至少回答：

- exact command、cwd、env/container、dependency lock、driver/backend/hardware；
- code/config/data/checkpoint/scorer full SHA；
- selected branch/feature flag与resolved values；
- load/forward/rollout start-end、exit code、exceptions/retries；
- input/output tensor/action schema、denormalize/controller path；
- raw predictions/episode trace/video/log位置与SHA。

一个smoke可以证明某条短路径可执行，但不能替代formal training、完整benchmark或真实机器人部署。

## 10. Raw Eval / Metric Gate

result必须从raw units可重算：

```text
raw prediction / episode
 -> versioned parser + scorer
 -> per-unit result
 -> slice/aggregate + denominator
 -> uncertainty + invalid/missing ledger
```

summary JSON、截图或README数字若缺raw rows，证据等级是report-supported/summary-only。不同checkpoint、task set、n、scorer或protocol不能拼成单一曲线或“提升”。

## 11. Evidence Graph：强 Claim 是 AND Gate

令claim `c`需要的证据节点集合为`R(c)`，要求的证据边为`E(c)`：

\[
V(c)=
\left(\bigwedge_{v\in R(c)} I_v\right)
\land
\left(\bigwedge_{(u,v)\in E(c)} M_{uv}\right).
\]

变量解释：`I_v`表示artifact身份/完整性通过，`M_uv`表示两层的语义映射已证明。直觉：有paper和checkpoint但无法证明中间run lineage，强claim仍断链。实现映射：claim registry逐项引用artifact SHA与edge evidence；缺边标`OPEN/CONFLICT`，不能靠总分平均掉。

保守的claim上限可写成：

\[
L(c)=\min_{e\in R(c)}L(e).
\]

变量解释：`L(e)`是每个必需证据的等级。直觉：强结论受最弱必需环节限制。实现映射：这是仓库审核gate，不是统计估计；若某项对该claim并非必要，应在claim spec中事前删除，而不是看到缺口后临时豁免。

## 12. Hash / Attestation 能证明什么

可用hash链绑定相邻manifest：

\[
h_{k+1}=SHA256\!\left(h_k\parallel m_k\parallel bytes_{k+1}\right).
\]

变量解释：`h_k`是上游artifact digest，`m_k`是映射manifest，`bytes_{k+1}`是下游artifact。直觉：任何内容变化都会改变后续digest。实现映射：SLSA的subject、resolvedDependencies、buildDefinition和runDetails提供通用provenance思想；ML训练还要自定义data/config/checkpoint/scorer字段。[S3]

hash只绑定bytes，不证明这些bytes实现论文、数据无泄漏、指标正确或谁写了代码。

## 13. SLSA 到 ML Run Provenance 的映射

| SLSA字段 | ML/VLA映射 | 额外必需字段 |
| --- | --- | --- |
| subject | checkpoint/eval bundle | processor/normalizer/controller/scorer bundle |
| buildDefinition | trainer/evaluator recipe | objective、mask、task/protocol语义 |
| externalParameters | CLI、dataset/checkpoint refs | resolved values与allowlist |
| resolvedDependencies | code/data/base weights/deps digests | dataset split、license、model card |
| runDetails.builder | scheduler/container/hardware platform | GPU/backend/driver/robot/simulator |
| metadata/byproducts | start/end/invocation/logs | loss/eval/trace/invalid ledger |

SLSA是软件供应链provenance标准，本页只借其结构；不能宣称五项目达到某SLSA level。

## 14. Git Author、Committer 与 Signature 边界

Git官方文档显示author可用`--author`覆盖，author/committer字段可由环境变量提供；name本身不产生authentication作用。[S4] commit/tag签名可验证对象与签名key关系，但仍不能自动证明：

- 该人独立设计全部方法；
- diff全由该人手写；
- 该commit在目标run中执行；
- 指标由该commit产生；
- 协作者、上游与工具辅助不存在。

因此Git author/committer是`authorship clue`，不是exclusive ownership verdict。

## 15. Contribution / Ownership Ledger

CRediT提供Conceptualization、Data curation、Formal analysis、Investigation、Methodology、Project administration、Resources、Software、Supervision、Validation、Visualization与Writing等14种角色，并明确它不用于决定authorship。[S5]

项目ledger对每个artifact/decision记录：

| 字段 | 例子 |
| --- | --- |
| person / actor | 候选人、同事、upstream、tool-assisted |
| role | Methodology / Software / Validation / Data curation |
| scope | file/function/config/experiment/report section |
| activity | proposed / implemented / reviewed / executed / verified |
| evidence | diff、commit、review、meeting/decision、run/log、witness |
| collaboration | solo / pair / team / upstream adaptation |
| confidence | direct / corroborated / partial / unverified |
| forbidden inference | “参与review”不得写“独立实现” |

不要伪造百分比。面试中用具体模块、决策、实现和验收边界说明贡献。

## 16. License 也是逐层证据

paper、repo、dataset、base checkpoint、fine-tuned checkpoint和runtime依赖可能有不同license。repo Apache/MIT不能自动覆盖model weights或dataset；本地有bytes也不自动获得发布/商用权。license manifest需逐artifact记录source、version、text/hash、用途、再分发与商业限制；未知就标`UNKNOWN`。

## 17. Contradiction 与 Negative Evidence

以下不能静默覆盖：

- paper/default与repo/current不同；
- README、config、code和runtime resolved value冲突；
- report metric与raw recompute不同；
- checkpoint path存在但binary缺失；
- model card、repo和weight license不同；
- commit author与贡献口述冲突；
- current workspace未找到artifact。

“当前workspace未找到”只证明本次审计范围内缺失，不证明其他机器或远端一定不存在。记录search scope、date、pattern与excluded roots。

## 18. 最小 Artifact Bundle

```text
evidence_audit/
  claim_registry.jsonl
  paper_model_data_source_freeze.json
  repo_revision_tree_manifest.json
  code_symbol_to_claim_edges.jsonl
  dataset_and_split_manifest.json
  resolved_run_config.json
  run_invocation_and_exit.json
  checkpoint_bundle_manifest.json
  load_forward_roundtrip.json
  runtime_environment_lock.json
  raw_eval_and_recompute/
  protocol_metric_registry.json
  evidence_graph.json
  contradiction_ledger.jsonl
  contribution_role_ledger.jsonl
  license_manifest.jsonl
  checksums/manifest-sha256.txt
  verify_claims.ps1
```

claim registry中的每个强表述必须列required nodes/edges、当前status、safe wording和补证据动作。

## 19. 审计伪代码

```python
def audit_claim(claim, evidence_graph, ownership_ledger):
    # 1. Split a compound resume statement into independently falsifiable atoms.
    atoms = atomize_claim(claim)
    verdicts = []

    for atom in atoms:
        # 2. Require identities and semantic edges through the full execution chain.
        required = load_required_nodes_and_edges(atom)
        chain = evidence_graph.match(required)

        # 3. Keep integrity, runtime validity, result validity and ownership separate.
        technical = verify_identity_integrity_semantics(chain)
        contribution = verify_role_scope_evidence(atom, ownership_ledger)

        # 4. Any missing or conflicting mandatory edge lowers the safe wording.
        verdicts.append(bound_claim_to_weakest_required_evidence(
            atom, technical, contribution
        ))

    return persist_claim_verdicts_and_open_gaps(verdicts)
```

伪代码是本仓库审计合同，不代表五项目已有自动claim verifier。

## 20. 五项目 Evidence Mapping

| 项目 | 已闭合链段 | 关键断边 | 当前安全上限 | Ownership边界 |
| --- | --- | --- | --- | --- |
| OPD | local code/config/manifests、数据route、10k holdout leakage audit、by-format/by-pool tables与point协议修正 | checkpoint weights/optimizer、raw predictions、统一ablation、old-final→OPD5000 lineage | 可讲设计/实现路径和protocol-bounded表格；不能说完整可复现或OPD单因果 | Git author只作参与线索；缺逐文件/决策/协作/tool ledger |
| Robot Harness | runtime/tool registry、SFT/GRPO数据脚本、schema-aware reward与多组eval summaries | checkpoint/raw predictions、共同n/scorer、真实browser/robot episode、完整run lineage | 可讲结构化工具与评测设计；强结果保持summary/protocol-bound | runtime/data/reward分别记录角色；不能写独立完成全部harness |
| OpenPiVLA | formal trainer、JSON/causal-CE路径、三类recipe、smoke/report/diagnostic、official launcher | formal checkpoint bytes/load、97.4 raw bundle、archive→formal lineage、`H=15,D=72`与`limit=16`冲突 | 可讲local-direct code/config/smoke；97.4仅archive-summary-only | commit与项目页支持参与，仍缺file/decision/review ledger |
| WAM | public Cosmos paper→repo→model card→eval path；本地简历已安全降级；少量diagnostic manifests | 当前workspace无raw run/checkpoint/config/log/metric/episode完整bundle；historical数字仅claim | 只能讲上游审计、诊断设计和待补证据；不能讲本地复现/uplift/root cause | public architecture非个人原创；local ownership未验证 |
| UWM / LIBERO | local scripts/report、protocol tuple、normalizer/action metadata、DataLoader smoke、user-confirmed summary | checkpoint binary、250 raw episodes/video、formal OOD/3-seed、fixed/reset pairs、ownership | 可讲迁移/协议/诊断；`186/250`保持user-confirmed/protocol-limited | upstream UWM结构与个人迁移/诊断分开；缺逐文件ledger |

五项目inventories都达到“能清楚说已有什么和缺什么”，但没有一个完成E1→E8全链。EVAL-022不提升任何项目metric、复现、部署、因果或ownership等级。

## 21. 面试三档表达

| 档位 | 表述 |
| --- | --- |
| 危险 | “论文代码我都跑了，Git记录也能证明全是我做的。” |
| 可过 | “我核对了paper与固定repo revision，本地有脚本/config/report；checkpoint或raw缺失的数字只按summary讲。” |
| 强 | “我把claim拆成paper→code→run→checkpoint→runtime→raw→metric与独立ownership两条链；逐项给SHA、protocol和缺口，只在已闭合层级陈述贡献与结果。” |

强回答不是更大胆，而是更精确、更可复核。

## 22. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 理解/审计上游方法 | paper/model/data docs与固定revision |
| C1 | 参与本地实现/迁移 | code/config/diff + contribution scope |
| C2 | 执行并验证run | resolved run、checkpoint bytes/load、runtime/raw outputs |
| C3 | 报告可靠结果 | recomputable protocol、denominator、uncertainty、selection边界 |
| C4 | 主导/生产影响 | decision/ownership ledger、release/monitor/incident与外部影响证据 |

当前五项目各claim分布在C0–C2输入，强结果与ownership多不到完整C2/C3。本节点保持`WARN`，VOL 05达到知识/题卡`44/44`但全部仍为`unseen`。下一bounded slice应执行VOL 05 completion audit / independent fact review，或从现有题卡中选择一题进行真实口述；本切片不创建`coaching_state.md`。

## 参考文献（References）

1. Mitchell et al., [*Model Cards for Model Reporting*](https://arxiv.org/abs/1810.03993v2), FAT* 2019。
2. Gebru et al., [*Datasheets for Datasets*](https://arxiv.org/abs/1803.09010v8), 2021。
3. SLSA, [Provenance v1.2](https://slsa.dev/spec/v1.2/provenance)与[Build Provenance v1.2](https://slsa.dev/spec/v1.2/build-provenance)。
4. `git/git`, [`git-commit`@`41365c2`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-commit.adoc)、[`git-commit-tree`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-commit-tree.adoc)与[`gitformat-signature`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/gitformat-signature.adoc)。
5. NISO, [CRediT Contributor Role Taxonomy](https://credit.niso.org/)与[role descriptors](https://credit.niso.org/contributor-roles-defined/)。
6. [VOL 03 Architecture / Execution Audit](vol_03_architecture_execution_claim_to_code.html)、[VOL 04 Benchmark Evidence Audit](vol_04_benchmark_evidence_claim_to_protocol.html)、[VOL 05 Local Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)、[ENG-021 Bundle Packaging](vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)、[EVAL-009 Recomputable Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)与[EVAL-020 Incident Evidence](vol_05_eval020_incident_timeline_root_cause_bugfix_verification_source_freeze.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目claim–evidence inventories。
