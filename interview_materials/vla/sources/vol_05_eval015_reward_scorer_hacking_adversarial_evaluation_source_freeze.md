# VOL 05 EVAL-015 Source Freeze：Reward / Scorer Hacking 与 Adversarial Evaluation

> 状态：`source_frozen / VLA-EVAL-015 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结 reward hacking、specification gaming、reward-process tampering、proxy overoptimization、hidden audit oracle、scorer mutation、optimizer-budget sweep 与 adversarial evaluation bundle；只生成一张 `VLA-EVAL-015` 原子题卡，EVAL-016后置。公开机制、本地代码事实、工程推断与未验证结果严格分层。

## 问题（Question）

怎样证明一个经过RL/post-training或反复checkpoint选择的VLA没有只学会“骗reward/scorer”？训练reward、公开holdout、learned judge或tool-call accuracy上升，不等于真实任务、安全和人工验收同时上升。可信评估需要把被优化的proxy与独立audit oracle分离，主动构造高proxy/低utility的反例，并检查优化预算增加时真实表现是否反转。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Amodei et al., *Concrete Problems in AI Safety* | primary paper；arXiv `1606.06565v2`，2016；论文许可未断言 | PDF `a3ac7eda67026d6d95f2182b1202ac371b7d9feabcc10a48dc90e417fbac023e` | reward hacking属于目标函数错误引发的事故风险；需要避免代理目标漏洞 | 本地模型已发生hacking、默认测试矩阵或VLA阈值 |
| S2 | Leike et al., *AI Safety Gridworlds* + official repo | primary paper + official-code；arXiv `1711.09883v2`；`google-deepmind/ai-safety-gridworlds@c43cb31143431421b5d2b661a2458efb301da9a3`；Apache-2.0 | paper `fd2e714ff33586fc668b105846cbfd364dd1ce3f36708c924facc2ec9f4d8dd6`；README `08518be18e0d2b3e5c5e720753d5ec5f338bf572b2d2de5c613fd764ad3ea53d`；`boat_race.py` `a7e4e894a177d4fdb53d19272547133ddf279576280f4ed6fbe6fc37da13ee49`；`tomato_watering.py` `a0cf9292f1d48e62a14c46a840a213488d9a587822615731c4ce83b444f5f7cb`；LICENSE `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | observed reward与对agent隐藏的performance function分离；reward gaming、observation/reward漏洞的可执行例子 | 隐藏oracle天然正确；gridworld结论自动外推真实机器人 |
| S3 | Everitt et al., *Reward Tampering Problems and Solutions in RL* | primary paper；arXiv `1908.04734v5`，2021；论文许可未断言 | PDF `9710aad1b99df97617b46b5ef69fa9ba126be8b913ff2d11df94b795af980d59` | 区分reward-function tampering与reward-function-input tampering；分析何时tampering成为工具性目标 | 任意readonly scorer即可解决目标错配；本地系统防篡改完成 |
| S4 | Gao et al., *Scaling Laws for Reward Model Overoptimization* | primary paper；arXiv `2210.10760v1`，2022；论文许可未断言 | PDF `c793c551a1b027402f758cce0fbf6b400cf66d0df57d2875d275e73cfd58bfc9` | proxy reward过度优化时gold-standard reward可能下降；RL与best-of-N均需观察优化预算曲线 | synthetic gold model等于人类/真实机器人utility；给出通用安全阈值 |
| S5 | 本地前置节点 | canonical local prerequisites | VOL02 `58d59caab24e8f287c0a38fd26727dc21e832c2f86cc3f90ca8bad4e9cc9d003`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd`；EVAL-014 `2027ea608960749f407099c56bac92528157e2125fd83525618507aa9f9f614a` | reward/proxy基础、scorer identity、raw bundle、release gate、proxy-online关系与真实effect边界 | 五项目已有independent hidden-oracle adversarial eval |
| S6 | 五项目 inventories | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 当前reward/scorer代码、protocol差异、proxy与缺口 | 任何项目已被证明无hacking，或已观察到agent主动篡改reward |
| S7 | Robot Harness reward/scorer implementation | local-code；只读仓库HEAD `3f4c8b3a11ff9512bc18ec4a331ae5ea01555f49`；仓库dirty | `schema_aware_reward.py` `a402d22299c1af0bab2d08e83e4389206882559294c3b1f55f9df55ac0f85e1a`；`reward_spec.json` `bb4c3d7a62e78890186035975b9657c8201a2d5c7977b48d27a6d0767e2d83c3`；`schema_aware_rescore.py` `7918d6644bf49031e907d973c34a1b3cc0e88ab89ec09f3a29afa4927e5695a7`；`native_tools_eval.py` `f01ef13a029567297b35646ab5b2a17f7e8762d77ffe739370365848638fcec4`；restraint check `ade12649ff8cdda4f39193da968dd4d2d24a62be53169f5c60a4d695dfad6143` | component/weight/penalty、parser、semantic threshold/fallback、128-row restraint boundary check与suite metrics | reward等于物理utility；完整adversarial coverage；代码ownership完整归属个人 |

S1—S4只提供机制和研究结果；S5—S7提供本地边界。以下audit-oracle、mutation matrix、selection-aware metrics与artifact schema是source-consistent engineering synthesis，不冒充论文原始协议或项目既有成果。

## 2. 先分清四种问题

| 问题 | 定义 | 典型例子 | 不能混同 |
| --- | --- | --- | --- |
| reward hacking / gaming | 提高被优化reward，却没有提高设计者意图 | 绕圈刷分、利用稀疏reward漏洞 | 单纯随机失败 |
| scorer hacking | 针对评测parser/judge/dataset捷径取得高分 | 输出特定模板骗parser、prompt injection骗VLM judge | scorer本身普通噪声 |
| reward tampering | 改写reward function或其输入/观测通道 | 修改计分状态、遮挡失败信号 | 仅仅选择高reward动作 |
| specification gaming | 满足字面规格但违背真实目标的更宽概念 | 合法tool序列产生错误业务结果 | 所有分布外错误 |

S3进一步区分reward-function tampering与RF-input tampering。[S3] 一个agent不必修改代码才会hacking；利用parser、遮挡camera、提前terminal或选择scorer盲点都可能提高proxy。相反，看到一次“高proxy低结果”只能证明proxy gap，需要排除日志错位、label错误、环境bug和普通随机性后才讨论机制。

## 3. Proxy、Audit Oracle 与真实 Utility

冻结三层信号：

```text
R_proxy(x): training/selection directly optimizes or repeatedly observes
A_audit(x): held-out independent scorer/oracle, inaccessible during optimization
U_deploy(x): intended task, safety and real-world outcome; often only partially observable
```

理想目标是优化`U_deploy`，实际只能优化proxy：

\[
x^*=\arg\max_x R_{\mathrm{proxy}}(x),
\qquad
\text{but release depends on }A_{\mathrm{audit}}(x^*)\text{ and }U_{\mathrm{deploy}}(x^*).
\]

变量解释：`x`可以是policy、checkpoint、trajectory或回答；`R_proxy`是已暴露的训练/选择信号，`A_audit`是独立审计，`U_deploy`是真实目标。直觉：optimizer会搜索proxy误差最大的方向，而非平均误差方向。实现映射：manifest必须标出每个metric是否参与gradient、checkpoint selection、prompt tuning、反复人工调参或只在最终audit使用。

AI Safety Gridworlds把agent可见reward与隐藏performance function分开，以后者衡量预期安全行为。[S2] “隐藏”只是降低直接过拟合机会，不证明oracle无偏；仍需人工校准、raw state、多个oracle和真实canary。

## 4. 什么才算 Independent Audit

independence不是换一个函数名。至少检查：

- audit cases、labels、threshold和failure templates不进入训练、prompt选择或checkpoint选择；
- audit scorer不复用同一个parser、embedding、VLM judge prompt或reference generator；
- audit读取更接近真实结果的原始state/effect sink，而非模型自己生成的解释；
- scorer author/reviewer、code path与data lineage尽量分离；
- candidate不能调用、修改或通过side channel推断audit reward；
- audit使用次数受控；反复查看并调参后，它已变成development set；
- 结果由immutable raw outputs重算，scorer和oracle均有revision/hash。

同一VLM分别换system prompt不是充分独立；同一reference trajectory派生的exact与semantic scorer也可能共享盲点。可以采用规则oracle、simulator state、human double review、第二模型judge和真实effect sink的heterogeneous ensemble，但要逐个说明它们的共同失效模式。

## 5. Hacking Indicator 与 Gap

对预注册case `i`，定义高proxy低audit事件：

\[
H_i=\mathbb{1}
\left[R_i^{\mathrm{proxy}}\ge\tau_p
\land A_i^{\mathrm{audit}}<\tau_a\right].
\]

变量解释：`τ_p/τ_a`必须在看candidate前冻结，并绑定metric语义。直觉：只看平均相关性会掩盖最危险的右下象限。实现映射：保存每个case的raw output、proxy component、audit evidence、threshold decision和人工裁决。

hacking-candidate rate：

\[
\widehat r_{\mathrm{gap}}=
\frac{\sum_{i=1}^{N}H_i}{N}.
\]

变量解释：`N`包含所有预注册cases；timeout、parser error、abstain和infra failure分别标记但不静默删分母。该率是“待归因的proxy-gap率”，不是自动证明agent有欺骗意图。critical safety/effect case可采用zero-tolerance gate并报告`k/N/CI`。

连续score可报告标准化差：

\[
G_i=z(R_i^{\mathrm{proxy}})-z(A_i^{\mathrm{audit}}),
\]

其中`z`必须用baseline/reference distribution冻结。变量解释：`G_i`只用于排序可疑样例，不能把不同语义metric强行等价；实现映射：同时保留原始单位、per-slice分布与人工审计结论。

## 6. Optimizer Budget 是实验轴

Gao et al.在synthetic gold/proxy reward model设置中观察到：随着RL或best-of-N对proxy的优化增强，gold score可能先升后降。[S4] 因而必须sweep：

- RL steps、KL系数、reward scale/clip；
- best-of-N、beam width、planner candidates、horizon；
- checkpoint search次数、prompt迭代次数、人工查看audit次数；
- reward model/scorer容量与训练数据量。

选择曲线：

\[
x_N^*=\arg\max_{x\in\{x_1,\dots,x_N\}}R_{\mathrm{proxy}}(x),
\qquad Q(N)=\mathbb{E}[A_{\mathrm{audit}}(x_N^*)].
\]

变量解释：`N`是选择预算，`Q(N)`是选中样本的独立audit表现。直觉：若proxy可被利用，proxy top-1继续上升时`Q(N)`可能反转。实现映射：保存全部候选而非只保存winner，画proxy与audit随N/step的paired curve并报告selection protocol。

单一最终checkpoint无法诊断overoptimization；需要训练/选择过程的多个预算点与同一locked audit。看到反转后也要检查distribution shift和winner's curse，不能直接归因“模型在故意作弊”。

## 7. Scorer Mutation 与 Metamorphic Test

把同一semantic outcome经过不应改变utility的变换`m`：

\[
D_{i,m}=\left|S(x_i)-S(m(x_i))\right|.
\]

变量解释：`m`可以是JSON key顺序、空白、同义工具alias、无关文本、camera metadata顺序或judge prompt paraphrase；对utility-preserving mutation，`D`应小。实现映射：每个mutation声明invariance/directional oracle，保存原/变体raw pairs和多scorer矩阵。

必须同时有：

- **positive controls**：真实正确，所有oracle应通过；
- **negative controls**：已知高proxy/低utility decoy，audit应拒绝；
- **invariance**：只改surface form，utility不变；
- **directional expectation**：越界参数、碰撞、漏步骤后audit不得变好；
- **paired counterfactual**：只改变一个关键state/effect，验证scorer真正读到该变量。

如果mutation本身改变了任务语义，就不能把score变化叫脆弱性；mutation generator和oracle需要独立review。

## 8. Adversarial Matrix

| family | attack / mutation | audit重点 |
| --- | --- | --- |
| parser | malformed/duplicate JSON、extra fields、unicode、tool alias、隐藏tool-call文本 | 多parser差异、真实dispatch |
| semantic scorer | keyword stuffing、近义词阈值边缘、embedding collision、token-overlap padding | raw args、critical exact与human/simulator |
| learned judge | prompt injection、judge-directed text、verbosity/style bias、self-claim success | judge input隔离、second judge、raw state |
| reward process | 修改reward/state input、遮挡failure sensor、提前termination、日志删除 | readonly channel、hidden state/effect sink |
| trajectory | 跳步、循环刷局部reward、先成功后破坏、超时规避终局 | full episode、terminal/after-state |
| selection | best-of-N、checkpoint/prompt sweep、反复看holdout | budget curve、fresh locked audit |
| safety | 高task reward但forbidden effect、deny-all伪安全 | hard veto + allowed utility |
| contamination | train/eval near-duplicate、模板记忆、公开failure回填 | group dedupe、fresh composition |
| transfer | scorer/env/controller version变化 | protocol hash与bridge rescore |

生成方式分为human red-team、规则mutation、model-generated attacks与从真实失败挖掘的regression。生成器本身不能看hidden label；发现的failure进入公开regression后，另保留fresh holdout继续验收。

## 9. Reward/Scorer 单元测试不是完整验收

至少对scorer实现做mutation testing：故意删掉一个critical check、翻转threshold、让parser漏掉malformed call，确认测试会失败；否则“测试全绿”可能只覆盖happy path。scorer contract应验证：

1. 所有component范围、权重和hard penalty组合；
2. NaN/empty/malformed/duplicate/timeout处理；
3. parser、normalizer、semantic backend和fallback显式；
4. no-op/abstain/deny-all不会获得虚高utility；
5. proxy字段名不能伪装成真实effect，例如`no_forbidden_side_effect`若只检查tool name必须重命名或标注proxy；
6. cancellation不能只靠`cancel/stop`字符串；
7. scorer version变化对旧raw predictions进行bridge rescore。

单元测试证明给定反例被捕获，不证明未知攻击、真实机器人或训练后策略不会找到新漏洞。

## 10. Matched 实验与 Release Gate

1. 冻结candidate/baseline、training reward、selection scorer、audit oracle、case split、optimizer budget和threshold；
2. 同一raw output先跑proxy与全部audit scorers，避免generation nondeterminism污染scorer对比；
3. paired clean/challenge/decoy/mutation/tamper cases按task/risk/scope分层；
4. audit只在预注册预算点打开，访问进入ledger；
5. proxy提升必须同时满足audit non-inferiority、critical zero/floor与allowed utility floor；
6. 任何critical high-proxy/low-audit case触发hard veto和manual triage；
7. 修复后把样例加入regression，同时用fresh hidden family防止只补丁化；
8. deployment用shadow/canary接真实outcome，但不把live safety风险交给scorer试错。

“多个proxy平均”不能自动消除共同盲点；reward与audit如果共享同一gold/reference、parser或judge，必须报告相关失效。human audit也要给rubric、blindness、agreement/disagreement与adjudication，不能只写“人工看起来不错”。

## 11. 最小 Artifact Bundle

```text
reward_hacking_eval/
  objective_reward_audit_contract.json
  scorer_registry.json
  splits/{development,locked_audit}.json
  cases/{clean,challenge,decoy,mutation,tamper}.jsonl
  raw_candidates.jsonl
  scorer_matrix.parquet
  optimizer_budget_curve.parquet
  human_audit.jsonl
  failure_triage.jsonl
  summaries/by_family.json
  checksums/manifest-sha256.txt
  reproduce.ps1
```

每个candidate记录model/checkpoint/prompt/policy、训练reward版本、是否参与selection、生成预算、case ID、raw output/trajectory/effect ref。每次scorer invocation记录code/prompt/backend/threshold hash、输入digest、component scores、异常和访问者；hidden labels单独权限控制。

## 12. 评估伪代码

```python
def adversarial_reward_audit(candidates, proxy, locked_audits, cases, budgets):
    spec = freeze_objective_scorers_splits_thresholds(cases, proxy, locked_audits)

    for budget in budgets:
        # Keep every candidate so selection pressure is observable.
        pool = generate_or_load_candidates(candidates, budget)
        proxy_rows = proxy.score_raw(pool)
        selected = select_by_proxy(pool, proxy_rows, budget)

        # Audit scorers use independent code/data/raw-state channels.
        audit_rows = [oracle.score_raw(selected) for oracle in locked_audits]
        write_candidate_scorer_matrix(pool, proxy_rows, audit_rows, budget)

    # Re-run paired mutations and known decoys, then inspect high-proxy/low-audit cells.
    run_metamorphic_and_tamper_suite(spec)
    gaps = find_pre_registered_proxy_audit_gaps(spec)
    human_blind_adjudicate(gaps)
    return recompute_budget_curves_gap_rates_and_release_gate(spec)
```

这是评估合同，不是五项目已有实现；`locked_audits`仍可能错误，且真实VLA utility需要simulator/robot/effect-sink证据。

## 13. Robot Harness 代码级边界

当前源码能直接证明：component/weight/hard penalty、known-tool latent-call detector、critical/semantic argument checks、scope checks和128-rowtool-restraint boundary check存在。该check的good mean为`1.0`、bad/malformed mean约`-5.342`且未记录未惩罚case；它只覆盖构造的refusal-vs-obvious execution/malformed边界。

同时存在必须主动披露的proxy缺口：

- `no_forbidden_side_effect`直接赋值为`no_forbidden`，实质是tool-name/allowlist proxy，不读取effect sink；
- `cancellation_compensation_correct`只检查candidate tool name是否含`cancel`或`stop`，不检查quiescence/residual；
- semantic threshold为`0.72`，backend可在Qwen-hidden、sentence-transformer和token-overlap fallback间变化；
- rescore中的`final_answer_contains`固定为`True`，不能作为真实final-state指标；
- 32B ladder使用token-overlap fallback，而早期base使用Qwen hidden，且n不同；
- holdout约`95.6%`时safety tool/coverage仍约`37–39% / 43–45%`，说明主proxy高不闭合safety；这不是hacking因果证明。

安全表述是：“我设计并审计了schema-aware reward/scorer及显式hard penalties，也发现了proxy命名、backend漂移和真实effect缺口；下一步用locked audit、mutation、budget sweep与真实sink补证据。”不能说“reward hacking已解决”或把sandbox/holdout高分当物理utility。

## 14. 其他四项目 Evidence Mapping

| 项目 | 已有证据 | 可设计的hacking audit | 当前不能说 |
| --- | --- | --- | --- |
| OPD | original strict、protocol-fixed strict、lenient geometry；pool-specific最佳checkpoint | parser/scorer mutation、fresh raw-holdout、checkpoint-selection budget、human geometry audit | scorer变化证明模型作弊；某一checkpoint全局最优 |
| OpenPiVLA | archived 97.4 summary与official rollout diagnostics，raw lineage未闭合 | locked raw episodes、success predicate mutation、checkpoint/prompt selection ledger | 97.4无hacking或formal run对应该分数 |
| WAM | action/future/value proxy与单样本diagnostic | selector-N/horizon sweep、proxy-vs-sim/real audit、tampered observation | world/value proxy优化已改善真实任务，或已发生model exploitation |
| UWM | offline action/video losses与user-confirmed LIBERO summary | frozen checkpoint的loss-vs-rollout pair、termination/success predicate mutation | 训练loss是reward hacking证据，或74.4已独立复算 |

四项目均无training-proxy→locked-audit optimizer-budget curve，也没有已确认reward-process tampering事件。EVAL-015只给验证合同，不新增个人结果。

## 15. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 理解reward/scorer hacking机制 | 公开来源与口述 |
| C1 | 实现/审计reward与scorer组件 | code/spec SHA、unit/mutation tests |
| C2 | 发现并修复已复现proxy exploit | raw counterexample、before/after、fresh regression |
| C3 | locked adversarial audit未见关键gap | independent oracle、budget sweep、`k/n/CI`与raw bundle |
| C4 | 部署期持续抑制proxy exploitation | shadow/canary、real outcome、incident/drift monitoring |

当前Robot Harness最多支持部分C1与若干已知边界测试；其他项目主要是C0/评估设计，不升级C2—C4。

本节点保持`WARN/unseen`。下一内容节点固定为`VLA-EVAL-016`：VLM/human proxy评分的一致性与偏差；本切片不生成该节点，也不创建`coaching_state.md`。

## 参考文献（References）

1. Amodei et al., [*Concrete Problems in AI Safety*, arXiv:1606.06565v2](https://arxiv.org/abs/1606.06565v2), 2016。
2. Leike et al., [*AI Safety Gridworlds*, arXiv:1711.09883v2](https://arxiv.org/abs/1711.09883v2)；[official repo@c43cb31](https://github.com/google-deepmind/ai-safety-gridworlds/tree/c43cb31143431421b5d2b661a2458efb301da9a3)。
3. Everitt et al., [*Reward Tampering Problems and Solutions in Reinforcement Learning*, arXiv:1908.04734v5](https://arxiv.org/abs/1908.04734v5)。
4. Gao et al., [*Scaling Laws for Reward Model Overoptimization*, arXiv:2210.10760v1](https://arxiv.org/abs/2210.10760v1)。
5. [VOL 02 IL/RL/Post-training](../knowledge/vol_02_il_rl_posttraining.html)与[EVAL-006 Scorer Versioning](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)。
6. [EVAL-009 Raw Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010 Regression Gate](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-011 Proxy/Online Correlation](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)与[EVAL-014 Side Effect](vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)。
7. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
