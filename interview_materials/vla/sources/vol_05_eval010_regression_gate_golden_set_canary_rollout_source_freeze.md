# VOL 05 EVAL-010 Source Freeze：Regression Gate、Golden Set 与 Canary Rollout

> 状态：`source_frozen / VLA-EVAL-010 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结golden set、paired regression、hard/soft gate、shadow/canary、promotion/abort/rollback与五项目证据边界；只生成一张`VLA-EVAL-010`原子题卡，VOL 05同步为knowledge/cards 32/44。

## 问题（Question）

怎样防止一个新VLA checkpoint在overall分数看似更高时，悄悄破坏关键task、safety、latency或真实执行路径？答案不是“再跑一次benchmark”，而是把固定golden set、预注册regression gate与有限暴露canary串成可审计、可终止、可回滚的release state machine。

## 1. 冻结来源、Revision 与支持边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Breck et al., *The ML Test Score* | primary paper；Proceedings of IEEE Big Data 2017；Google Research页面与PDF，访问2026-07-18；论文再分发许可未断言 | page `e1588aa27c4a0aa74435327e92400443faf0b1ddf623068845571346484e1f6b`；PDF `8db5862dc7c7aaa2c55bb43bd42fc55531a0503782b7026b5811c00c98befd31` | 重要slice的absolute/incremental release tests；serving前自动bless/veto；small-scale canary；old/new并行、小流量逐步增加；rollback与持续质量/性能监控 | 不定义VLA golden schema、paired CI、机器人安全认证或本文阈值 |
| S2 | Argo Rollouts official repository | official-code；HEAD commit `9273b0ee05dbb629cc72fb9d343c08356c8379c8`；Apache-2.0 | LICENSE `c996fc213c94f4a4a838407d355b081226caa7b103a4f239bb87fb8f1d8e3a60`；canary `d50dadb21ed9ec2010be77ec0c7cde8af90a1b32e5af005102fad6a841b8c4ee`；analysis `2e4a68131130e307c396bd0cf431667152e599e056464e6eb22d2e18f348f8ae`；spec `0bcdbf333ffe7978f1530c3b79272a4098948154dde14bbf1807b212b6b8a665` | `setWeight`、pause、inline/background analysis、success/failure/inconclusive、abort与rollback window等progressive-delivery机制 | 不证明用户项目使用Argo，不把pod traffic机制自动映射成机器人动作安全 |
| S3 | Google SRE Workbook, *Canarying Releases* | official documentation；官方URL；当前环境TLS与浏览器导航均失败，未取得2026-07-18响应bytes | `unavailable` | 只作canary术语与baseline/canary比较的补充阅读入口 | 不承担本页任何唯一强主张，不伪造revision、SHA或可达性 |
| S4 | EVAL-004/005/006/007/009 canonical source freezes | local canonical prerequisite | EVAL-004 `c89c052a...427313`；EVAL-005 `16b6a4c7...804ff46`；EVAL-006 `8a2ccfbc...ccd054`；EVAL-007 `66800fd2...6e278`；EVAL-009 `be6945d...13dea` | paired unit、aggregation、protocol identity、coverage与raw-to-summary bundle前置合同 | 不证明regression/canary已实施 |
| S5 | 五项目inventories + WAM artifact manifest | local-evidence | Robot Harness `66acc52c...aa291e`；OPD `0a68251d...db12bb`；OpenPiVLA `a3c644f9...ce293`；WAM `078c86b1...772d`；UWM `728b8326...3674d`；WAM manifest `1ab87092...8f697` | 当前checkpoint、suite、summary、trace与协议缺口 | 不升级为自动gate、线上canary或个人ownership |

S1的PDF明确提出：重要data slice不能被global summary掩盖；serving前应由自动系统bless或veto；offline testing不能保证live production；new/old model可并行并让new model先接小比例流量；rollback需要预先练习。S2则提供一套通用progressive-delivery控制面。本文把它们转换为VLA release合同，转换部分标为engineering synthesis。

S3核验限制是本节点的显式open item，不用搜索摘要或记忆补写网页原文。完整本地SHA见对应review；S4中的省略写法只用于表格可读性。

## 2. 六个对象必须分开

| 对象 | 固定什么 | 回答什么问题 | 不能替代 |
| --- | --- | --- | --- |
| checkpoint curve | 多个training step的summary | 训练过程中哪个点更好 | 同协议release gate |
| smoke test | 少量load/inference/episode | artifact是否基本可运行 | golden suite与统计判断 |
| holdout summary | 固定数据上的aggregate | 候选的离线表现 | raw paired rows与live path |
| golden set | immutable case IDs、expected result/invariant、slice | 每次release必须守住哪些行为 | candidate-specific临时样例 |
| regression gate | 预注册metric、margin、CI、hard veto、missing policy | 候选能否进入下一阶段 | canary泛化与安全系统 |
| shadow/canary | live path的受限exposure、guardrail、abort/rollback | 真实serving/control链路是否出现回归 | 全量部署与分布外保证 |

项目有checkpoint表、smoke或summary，不等于后三项已形成系统。

## 3. Golden Set 合同

本文把黄金集合（golden set）定义为：release决策前冻结、可逐case复算、包含expected output或hard invariant的版本化集合。它至少包含：

```text
golden_case_id, suite_revision, input_or_episode_ref/hash,
task/slice/difficulty/safety labels, init/seed,
expected_output_or_invariants, scorer/parser/protocol revision,
criticality, weight, active_since, retired_at/reason
```

### 3.1 组成

1. **common support**：baseline与candidate在同case、同protocol、同scorer上配对；
2. **critical slices**：grasp/contact、long horizon、OOD view、latency-sensitive path等预先定义；
3. **hard invariants**：shape/axis/unit/finite、allowed action/tool、scope、forbidden side effect、controller limit；
4. **known failures**：历史incident或bad case可进入集合，但必须保存来源、修复与防止训练污染的策略；
5. **private holdback**：避免反复调参只优化公开golden；访问与使用次数应留ledger。

### 3.2 版本与污染

- candidate评估开始后，不因candidate失败而改expected result、slice或margin；修改需新suite revision并让baseline/candidate都重跑。
- golden不是永远不变：新增真实failure、分布变化或标注修正时append新版本；retirement必须有reason、替代case和历史可追踪性。
- release golden、training/dev set与最终holdback分开；发现训练重叠时标记contaminated并fail closed，不能静默换分母。
- safety-critical case不能用overall提升抵消，也不能只因“长期没失败”随意删除。

## 4. Paired Regression 与 Non-inferiority Gate

把每个指标统一成“越大越好”的效用（oriented utility）`u_k`。对同一golden case `i`：

\[
\Delta_{i,k}=u_k(c,i)-u_k(b,i),
\qquad
\bar\Delta_k=\frac{1}{n_k}\sum_{i=1}^{n_k}\Delta_{i,k}.
\]

变量解释：`c/b`分别是candidate与baseline；`k`是success、point hit、negative latency、negative intervention等指标；`n_k`只包含预注册的valid paired support。实现映射：逐case raw row保留两侧输出、valid/exclusion与score contribution；不能从两个独立aggregate相减伪装成paired证据。

对critical metric `k`，给定允许的non-inferiority margin `δ_k`：

\[
G_{offline}=
\mathbb{1}[H_{schema}=H_{safety}=H_{lineage}=1]
\prod_{k\in\mathcal K_{critical}}
\mathbb{1}\!\left[\operatorname{LCB}_{1-\alpha}(\bar\Delta_k)\ge -\delta_k\right].
\]

变量解释：hard gate任何一项失败即为0；`LCB`是预注册方法得到的单侧置信下界；`δ_k`来自业务/安全容忍度，不由candidate结果倒推；`α`与多指标处理在gate config中冻结。实现映射：gate输出每个metric/slice的estimate、interval、margin、decision和raw bundle SHA。样本不足、missing、invalid、CI不可算或protocol漂移默认fail closed。

若没有足够paired样本，可使用预注册的exact/paired bootstrap或纯hard threshold，但必须如实说明统计能力；不能用“p>0.05”推出等价，也不能把overall mean当作所有slice的non-regression证明。

## 5. Hard Gate 与 Soft Guardrail

### 5.1 Hard veto

- model/processor/normalizer/checkpoint/protocol/scorer lineage不完整；
- parser失败、shape/axis/unit错误、NaN/Inf、动作越界；
- critical/safety case出现forbidden side effect、scope violation或emergency-stop触发；
- planned/valid/excluded/missing不守恒，或candidate与baseline不在common support；
- latency deadline、memory limit或controller constraint超过预注册硬限。

### 5.2 Soft metric

overall success、per-task uplift、energy、smoothness、p50/p95 latency、intervention、timeout与drift都可以是多目标指标；但soft不等于可以随意平均。release报告至少同时展示global、per-task、critical slice、safety与systems performance。一个“overall +1% / safety -20%”的candidate必须被critical gate拒绝，不能用weighted sum洗掉。

## 6. Gate 配置必须绑定 EVAL-009 Bundle

```text
release_gate/
  gate_config.json             # baseline/candidate, metrics, margins, CI, decisions
  golden_manifest.json         # case IDs, revision, expected/invariant, slices
  protocol_manifest.json       # env/controller/parser/scorer/policy identities
  raw/base/...                 # EVAL-009 recomputable bundle
  raw/candidate/...
  paired_delta.parquet
  decision.json                # pass/fail + per-gate evidence
  approvals.json               # human/safety sign-off where required
  checksums/manifest-sha256.txt
```

`decision.json`不能只写`pass=true`；必须能回跳到case、raw output、trace/video、scorer与threshold revision。人工override若存在，要记录who/why/expiry，并禁止覆盖hard safety veto。

## 7. Shadow → Canary → Promote / Abort

### 7.1 状态机

```text
candidate built
  -> offline golden gate
  -> shadow: same live observations, no actuator authority
  -> canary-1: allowlisted low-risk task/init/robot or small traffic
  -> canary-2: wider support after minimum exposure + decision window
  -> promote
  -> continuous monitoring

any hard breach / analysis failure / timeout
  -> abort -> traffic/authority back to known-good baseline -> incident bundle
```

Argo Rollouts的`setWeight`、pause、AnalysisRun、failure/success limits、abort与rollback window说明progressive delivery需要显式step与decision对象；机器人/VLA只能借用控制思想，不能把Kubernetes流量权重直接当作机械臂安全认证。[2]

### 7.2 Comparable canary

- baseline与canary尽量处于同时间窗、同输入support、同scorer；不能拿上周baseline与今天canary直接比。
- 冻结exposure unit：request、episode、task-init、robot-hours或control steps；同时冻结minimum exposure与decision window。
- 观测success/safety、p50/p95/p99 latency、deadline miss、timeout、intervention、emergency stop、forbidden action、resource与distribution drift。
- shadow阶段保留candidate raw action但不执行；如果candidate影响环境，后续就不再是paired counterfactual，必须明确因果边界。
- abort是自动停止扩量；rollback是恢复已验证的model+processor+normalizer+controller bundle，两者都要演练。

### 7.3 Canary 的结论边界

canary通过只说明“在已暴露support、时窗、authority与样本量下没有触发预注册拒绝条件”。它不证明全任务泛化、极端tail safety、长期drift稳定或真实机器人认证。对机器人，独立safety controller、workspace/velocity/force limits和human stop不能由模型canary替代。

## 8. Release Decision 伪代码

```python
def release_candidate(base_bundle, candidate_bundle, gate_cfg):
    # 1. Verify immutable lineage and the same golden/protocol/scorer contract.
    verify_bundle_and_common_support(base_bundle, candidate_bundle, gate_cfg)

    # 2. Fail closed on schema, action, safety, missingness, or deadline invariants.
    run_hard_gates(candidate_bundle, gate_cfg.hard_invariants)

    # 3. Compute paired deltas and pre-registered one-sided non-inferiority decisions.
    decision = compare_paired_metrics(base_bundle, candidate_bundle,
                                      margins=gate_cfg.margins,
                                      interval_method=gate_cfg.interval_method)
    if not decision.all_critical_pass:
        return abort_and_record("offline_regression", decision)

    # 4. Shadow first: score live observations without granting actuator authority.
    shadow = run_shadow(candidate_bundle, guardrails=gate_cfg.shadow_guardrails)
    if shadow.hard_breach:
        return abort_and_record("shadow_breach", shadow)

    # 5. Increase allowlisted exposure only after minimum samples and decision windows.
    for stage in gate_cfg.canary_stages:
        result = run_canary(stage, baseline=gate_cfg.known_good)
        if result.hard_breach or not result.analysis_pass:
            return rollback_known_good_and_record(stage, result)

    return promote_with_continuous_monitoring(candidate_bundle)
```

这是release-contract伪代码，不是五项目已有部署系统。

## 9. 五项目 Evidence Mapping

| 项目 | 当前证据 | 可作为的输入 | 当前不能声称 |
| --- | --- | --- | --- |
| Robot Harness | 8B/32B base/SFT/GRPO suite与checkpoint metrics；base/SFT `n=1333`、GRPO `n=1000`；hidden-embedding与token-overlap scorer不同；safety弱、browser format-only | 对齐common suite/scorer后构造tool/scope/safety golden；safety应hard gate | 已有同协议base→GRPO regression gate；已有真实browser/robot canary |
| OPD | 10k raw-holdout input、ckpt1000–5000 by-format/by-pool curve；不同pool最佳checkpoint不同 | 设计box/point/text与pool vector golden，禁止单一overall选择 | 已有raw-prediction paired gate、统一lineage、自动promotion或canary |
| OpenPiVLA | public smoke、formal report、official-checkpoint diagnostics；97.4为archive summary | load/parser/action-shape smoke可作hard gate候选 | formal Qwen checkpoint与97.4已闭合golden regression；diagnostic rollout能替代其lineage |
| WAM | CoffeePressButton episode0 base/trained paired trace/video | 一个diagnostic regression case | golden suite、完整分母、自动gate或canary |
| UWM | user-confirmed `186/250` summary与协议脚本 | 固定task/init/warmup/normalizer字段作为未来golden manifest | 250 raw episode paired gate、checkpoint-bound regression或canary |

因此五项目当前均处于“可以设计与补做”而非“已实现release system”。面试中可讲gate设计、证据缺口和补强顺序，不可把本文伪代码改成经历完成时态。

## 10. 高频反例

1. 每次candidate失败就把golden case删掉或改阈值；
2. 用不同n、不同scorer、不同init的两个summary相减；
3. overall提升掩盖critical slice或safety下降；
4. missing/timeout/crash从分母静默移除；
5. 只设“成功阈值”，不设minimum exposure与decision window；
6. canary和baseline不在同时间窗或不同版本serving path；
7. abort只有命令没有known-good bundle与rollback drill；
8. shadow candidate动作实际影响环境，却继续声称严格paired；
9. canary通过后声称全量泛化或安全认证；
10. 把部署框架能力写成项目已使用事实。

## 11. Source Gate 结论与下一入口

EVAL-010保持`WARN`：公开来源足以支持slice-aware release tests、automated bless/veto、small-scale canary、progressive analysis、abort/rollback；本文已冻结golden/gate/canary的VLA工程合同。五项目没有同时闭合common-support raw bundle、预注册gate decision与live canary evidence，SRE页面当前也未重新抓取。

下一节点固定为`VLA-EVAL-011`：offline metric与online success的相关性分析。真实口述前不创建`coaching_state.md`。

## References

1. Eric Breck et al., [*The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/), IEEE Big Data 2017；[frozen PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/4156.pdf)。
2. Argo Rollouts, [Canary strategy](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/canary/index.md), [Analysis](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/analysis.md), [Specification](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/specification.md)。
3. Google SRE Workbook, [*Canarying Releases*](https://sre.google/workbook/canarying-releases/)（当前环境抓取受阻，只作补充入口）。
4. [EVAL-004](vol_05_eval004_paired_init_seed_significance_source_freeze.html)、[EVAL-005](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-007](vol_05_eval007_init_seed_task_coverage_difficulty_source_freeze.html)、[EVAL-009](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。
5. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
