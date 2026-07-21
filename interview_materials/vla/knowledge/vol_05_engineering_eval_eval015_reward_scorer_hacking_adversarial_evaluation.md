# VLA Engineering / Evaluation：Reward / Scorer Hacking 与 Adversarial Evaluation

> 节点：`VLA-EVAL-015`  
> 状态：`drafted / knowledge_37_of_44 / card_1_of_1_unseen / WARN`  
> 更新日期：2026-07-19  
> 学习目标：能区分reward hacking、scorer hacking、reward tampering与普通失败；构造独立audit oracle、optimizer-budget曲线、metamorphic/adversarial suite和hard release gate，并准确陈述Robot Harness的proxy缺口。

## 1. 一页结论

```text
intended utility U
  -> imperfect training reward / selection scorer R_proxy
  -> optimizer searches high-reward behavior
  -> locked independent audit A + raw state/effect sink
  -> adversarial mutation + budget sweep + human adjudication
  -> safety veto and utility floor
```

面试先说四件事：

1. 训练reward和公开scorer都是可被优化的proxy，不是最终目标；
2. audit必须在data、parser/judge、raw signal和访问权限上与proxy尽量独立；
3. 主动寻找“高proxy、低audit/utility”的反例，并随RL steps、best-of-N或checkpoint search画曲线；
4. critical safety失败采用hard veto，正常任务utility另设floor，既防事故被平均，也防deny-all伪安全。

## 2. 四个概念不要混

| 概念 | 核心 | 机器人例子 |
| --- | --- | --- |
| reward hacking | 利用reward漏洞而非完成真实目标 | 循环触发局部奖励、不完成终局 |
| scorer hacking | 利用parser/judge/eval set捷径 | keyword stuffing骗semantic/VLM judge |
| reward tampering | 操纵reward function或其输入 | 遮挡失败sensor、改写计分状态 |
| specification gaming | 满足字面规格却违背意图 | tool/schema合法但真实业务状态错误 |

《Concrete Problems in AI Safety》把avoiding reward hacking列为错误目标函数引发的实际安全问题。[1] Reward Tampering论文进一步区分reward-function tampering与reward-function-input tampering。[2]

一次高reward低success是“proxy gap候选”，还不是agent有欺骗意图的证明。需要排除label错、日志错位、环境bug、普通随机失败和protocol不一致。

## 3. 三层目标合同

```text
R_proxy: 训练、RL、best-of-N、checkpoint/prompt selection直接观察或优化
A_audit: locked holdout上的独立规则/状态/human/second-judge审计
U_deploy: 真实任务、安全、用户意图和物理/业务后果
```

\[
x^*=\arg\max_x R_{\mathrm{proxy}}(x),
\qquad
\text{release requires }A_{\mathrm{audit}}(x^*)\text{ and }U_{\mathrm{deploy}}(x^*).
\]

变量解释：`x`可以是trajectory、response、policy或checkpoint。直觉：optimizer会寻找proxy误差最大的区域，而不只是平均拟合区域。实现映射：metric registry标记每个信号是否参与gradient、selection、prompt tuning、人工反复查看或仅用于最终audit。[3]

AI Safety Gridworlds明确把agent可见reward与隐藏performance function分离；后者评估设计者真正关心的安全行为。[3] 但hidden不等于correct，仍需human calibration、raw state、多个异构oracle和真实canary。

## 4. 独立 Audit 到底独立在哪

最低要求：

- audit cases/labels/templates不进入训练和checkpoint/prompt选择；
- 不复用相同parser、embedding、VLM judge prompt或reference generator；
- 尽量读取simulator state、controller event、effect sink或human label，而非模型自述；
- candidate无权调用、修改、查询或通过side channel推断audit reward；
- audit scorer的code/prompt/backend/threshold全部版本化；
- 访问次数进入ledger；反复看结果调参后该集降级为development；
- raw output先保存，proxy和audit都可独立重算。

“换一个阈值”“同一VLM换prompt”“exact和semantic都来自同一gold trajectory”只能提供有限多样性，因为共同盲点仍在。独立性应按data、signal、implementation、reviewer和access逐项声明。

## 5. 高 Proxy / 低 Audit 指标

\[
H_i=\mathbb{1}
\left[R_i^{\mathrm{proxy}}\ge\tau_p
\land A_i^{\mathrm{audit}}<\tau_a\right].
\]

变量解释：`τ_p/τ_a`在candidate之前冻结。直觉：危险点在“proxy认为很好、独立audit认为失败”的象限。实现映射：每个case保存raw output/trajectory、proxy components、audit state/effect、threshold decision和人工裁决。

\[
\widehat r_{\mathrm{gap}}=
\frac{\sum_{i=1}^{N}H_i}{N}.
\]

变量解释：`N`是全部预注册cases；timeout、parser error、abstain和infra error不能静默删分母。该指标叫proxy-gap rate更严谨：它标出需要归因的样例，不自动证明欺骗。critical case报告`k/N/CI`并可零容忍。

连续gap可辅助排序：

\[
G_i=z(R_i^{\mathrm{proxy}})-z(A_i^{\mathrm{audit}}).
\]

`z`必须由baseline/reference distribution预先冻结；不同metric仍保留原始单位，不能把tool accuracy、VLM score和真实success强行当同一数轴。

## 6. 为什么要 Sweep Optimizer Budget

Reward Model Overoptimization研究显示，在synthetic gold/proxy设置里，无论RL还是best-of-N，持续提高proxy都可能让gold score反转。[4] VLA需要扫：

- RL/GRPO steps、reward scale、clip、KL；
- best-of-N、beam、planner candidates、world-model horizon；
- checkpoint数量、prompt版本、阈值尝试次数；
- audit被查看和用于决策的次数。

\[
x_N^*=\arg\max_{x\in\{x_1,\ldots,x_N\}}R_{\mathrm{proxy}}(x),
\qquad Q(N)=\mathbb{E}[A_{\mathrm{audit}}(x_N^*)].
\]

变量解释：`N`是选择预算，`Q(N)`是winner的独立audit表现。实现映射：保存全部候选和winner selection，不只保存top-1；画proxy/audit随N或training step的paired curve。若proxy继续升、audit下降，这是overoptimization警报，但仍要排除distribution shift和winner's curse。

## 7. Metamorphic / Scorer Mutation

对utility不应变化的变换`m`：

\[
D_{i,m}=\left|S(x_i)-S(m(x_i))\right|.
\]

变量解释：`m`可以改JSON key顺序、空白、等价alias、无关文本、camera metadata顺序或judge prompt表述。直觉：真正读语义/状态的scorer不应被表面格式大幅改变。实现映射：原样本与变体共享pair ID，mutation声明invariance或directional expectation，并保存多scorer矩阵。

四类control必须同时有：

- positive：真实正确，scorer应通过；
- negative/decoy：proxy表面很好但真实失败，audit应拒绝；
- invariance：只改surface，分数应稳定；
- directional：删除关键步骤、越权、碰撞或破坏after-state，audit不得更高。

mutation generator也可能错误改变语义，所以每种变换要独立review和抽样人工验收。

## 8. Adversarial Matrix

| family | 攻击 | 独立证据 |
| --- | --- | --- |
| parser | malformed/duplicate JSON、extra field、unicode、隐藏tool-call | 第二parser与真实dispatch ledger |
| semantic | keyword stuffing、0.72阈值边缘、token padding、embedding collision | critical exact、state/human oracle |
| VLM judge | prompt injection、judge-directed text、verbosity/style | 隔离judge input、second judge、raw state |
| reward process | 改reward/state input、遮挡failure、提前terminal | readonly hidden state/effect sink |
| trajectory | 循环刷局部reward、跳步、先成功后破坏 | full episode和after-state |
| selection | best-of-N、checkpoint/prompt sweep、反复看holdout | fresh locked audit与预算曲线 |
| safety | task reward高但forbidden effect；deny-all | safety veto + allowed utility |
| contamination | train/eval近重复、公开failure模板记忆 | group dedupe、fresh composition |
| version | scorer/env/controller升级 | protocol hash、旧raw bridge rescore |

来源可由规则mutation、human red-team、model-generated attacks和真实failure mining组成。已公开的failure进入regression后，需要另留fresh hidden family，避免只学会补丁。

## 9. Scorer 单元测试与 Mutation Testing

scorer的测试不能只验证happy path：

1. 故意删除critical check、翻转threshold或让parser漏掉malformed call，测试必须失败；
2. 覆盖NaN、empty、timeout、duplicate、abstain、deny-all和fallback；
3. 每个component、weight和hard penalty有边界/组合测试；
4. parser、normalizer、semantic backend和fallback写入result；
5. scorer字段名必须与证据层一致，tool allowlist不能命名成真实side-effect success；
6. cancel/compensation不能靠关键词代替quiescence/residual；
7. scorer升级对同一raw predictions双重重算。

测试全绿只说明已知反例被覆盖；训练后的optimizer仍可能发现测试未编码的漏洞。

## 10. Release Protocol

1. candidate/baseline固定model、reward、scorer、data split、optimizer budget和case matrix；
2. 同一raw candidate先落盘，再跑proxy与audit，消除重新生成差异；
3. 按clean/challenge/decoy/mutation/tamper及task/risk/scope分层；
4. proxy uplift必须通过audit non-inferiority、critical veto和allowed utility floor；
5. high-proxy/low-audit进入blind human adjudication，区分hacking、scorer bug、label bug和普通失败；
6. 修复后进regression，fresh locked audit仍保持不可见；
7. 最后用shadow/canary接真实outcome，不在live robot上无保护搜索漏洞。

多个proxy平均不保证安全；若共享parser、gold、judge或data，它们可能一起被hack。human review也要冻结rubric、blindness、agreement与adjudication。

## 11. Artifact Bundle

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

```python
def audit_reward_hacking(candidate_generator, proxy, audits, cases, budgets):
    spec = freeze_objective_scorers_splits_thresholds(cases, proxy, audits)
    for budget in budgets:
        pool = candidate_generator.generate(budget)
        proxy_rows = proxy.score_raw(pool)
        winners = select_by_proxy(pool, proxy_rows)
        audit_rows = [oracle.score_raw(winners) for oracle in audits]
        persist_all_candidates_and_scores(pool, proxy_rows, audit_rows, budget)

    run_paired_mutations_decoys_and_tamper_cases(spec)
    gaps = find_high_proxy_low_audit_cells(spec)
    blind_human_adjudicate(gaps)
    return recompute_budget_curves_gap_rates_and_gate(spec)
```

这是评估合同，不代表五项目已有locked audit或真实robot adversarial结果。

## 12. Robot Harness：最重要的项目回答

当前可核验的优点：reward spec有component/weight/hard penalty；known-tool latent-call detector防止malformed tool-call绕parser；critical/semantic arguments、scope和restraint checks存在；128-row boundary check中good mean=`1.0`，bad/malformed mean约`-5.342`，未记录漏罚case。[5]

但必须主动指出：

- `no_forbidden_side_effect = no_forbidden`，只检查tool/allowlist，不看真实effect；
- cancellation component只看tool name是否含`cancel/stop`；
- semantic threshold是`0.72`，Qwen-hidden与token-overlap fallback会改变语义；
- rescore的`final_answer_contains`固定`True`；
- base与ladder的n和semantic backend不一致；
- holdout约95.6%时，safety tool/coverage仍约37–39%/43–45%。

这些事实证明proxy gap和adversarial audit需求，不证明模型已经“有意骗分”。面试表述：我做了reward/scorer工程和边界测试，同时识别真实effect、cancel语义、backend漂移与locked audit缺口；不把project sandbox或holdout分数叫真实机器人success。

## 13. 其他项目边界

### OPD

original strict、protocol-fixed strict、lenient geometry以及不同pool的best checkpoint适合做parser mutation、fresh holdout和selection-budget审计。当前只能说scorer/protocol敏感，不能说模型在scorer hacking。

### OpenPiVLA

97.4仍是archive summary，formal/eval lineage和raw episodes缺失；必须先冻结success predicate、raw trajectory和selection history，不能声称该分数已通过anti-hacking audit。

### WAM

world/value proxy与best-of-N天然需要N/horizon sweep和proxy-vs-sim/real audit，但当前只有有限diagnostic，不支持optimizer exploitation结论。

### UWM

offline action/video loss和LIBERO success是不同层；需要同checkpoint paired evidence。loss/success不一致本身不等于reward hacking。

## 14. 追问防线

- **换一个judge够吗？** 不够；要看data、signal、parser、model、prompt和reviewer是否共享盲点。
- **hidden test为什么会失效？** 被反复查看调参后变成development；还可能本身有偏。
- **reward上升、success下降就是hacking吗？** 是proxy gap，需要排除bug/shift/噪声后归因。
- **怎样测best-of-N hacking？** 保存全部候选，画proxy winner与独立audit随N的曲线。
- **hard penalty能解决吗？** 只覆盖编码的已知漏洞；需mutation测试与fresh adversarial cases。
- **deny-all为什么不行？** safety proxy可满分但任务utility为零，所以另设allowed utility floor。
- **项目做到哪级？** Harness有C1源码和窄边界测试；没有C2 exploit复现或C3 locked audit结论。

## 15. 本节点状态

EVAL-015知识与一张题卡保持`WARN/unseen`。五项目均没有training-proxy→locked-audit optimizer-budget curve，也没有确认的reward-process tampering事件。下一节点是`VLA-EVAL-016`：VLM/human proxy评分的一致性与偏差；没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. Amodei et al., [*Concrete Problems in AI Safety*, arXiv:1606.06565v2](https://arxiv.org/abs/1606.06565v2)。
2. Everitt et al., [*Reward Tampering Problems and Solutions in RL*, arXiv:1908.04734v5](https://arxiv.org/abs/1908.04734v5)。
3. Leike et al., [*AI Safety Gridworlds*, arXiv:1711.09883v2](https://arxiv.org/abs/1711.09883v2)与[official repo](https://github.com/google-deepmind/ai-safety-gridworlds/tree/c43cb31143431421b5d2b661a2458efb301da9a3)。
4. Gao et al., [*Scaling Laws for Reward Model Overoptimization*, arXiv:2210.10760v1](https://arxiv.org/abs/2210.10760v1)。
5. [EVAL-015 Source Freeze](../sources/vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)与[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
6. [EVAL-006 Scorer Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-009 Raw Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)、[EVAL-010 Regression Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)、[EVAL-011 Proxy/Online Correlation](vol_05_engineering_eval_eval011_offline_online_correlation.html)与[EVAL-014 Side Effect](vol_05_engineering_eval_eval014_forbidden_side_effect_scope_cancel_compensation.html)。
7. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
