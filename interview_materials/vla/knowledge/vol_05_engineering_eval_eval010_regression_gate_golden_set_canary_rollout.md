# VOL 05 EVAL-010：Regression Gate、Golden Set 与 Canary Rollout

> 状态：`drafted / VLA-EVAL-010 / knowledge_32_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-004 Paired Eval](vol_05_engineering_eval_eval004_paired_init_seed_significance.html)、[EVAL-005 Aggregation](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)、[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)  
> 来源冻结：[EVAL-010 Source Freeze](../sources/vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)  
> 项目边界：五项目有checkpoint曲线、smoke、summary或单episode trace，但都没有闭合统一offline regression gate与live canary；本页只给工程合同。

## 问题（Question）

怎样让VLA新checkpoint经过可重复的离线回归判定，再以可回滚的小暴露进入真实serving/control path？核心是：golden固定题目，gate固定判法，canary固定暴露与退出条件；三者都绑定immutable baseline/candidate bundle。

## 1. 三层 Release Funnel

```text
versioned candidate bundle
  -> golden set: fixed cases + expected result / hard invariant
  -> regression gate: paired deltas + critical veto + systems limits
  -> shadow: live inputs, candidate has no actuator authority
  -> canary: allowlisted small exposure + concurrent known-good baseline
  -> promote / abort / rollback + continuous monitoring
```

checkpoint curve回答“训练过程中哪个点更好”；smoke回答“能否load/run”；holdout summary回答“某数据上的aggregate”。它们都不能自动回答“是否可发布”。[1]

## 2. Golden Set：固定题目，不固定模型

### 2.1 最小字段

```text
case_id, suite_revision, input_or_episode_ref/hash,
task/slice/difficulty/safety, init/seed,
expected_output_or_invariants, scorer/parser/protocol_sha,
criticality, weight, active_since, retired_at/reason
```

golden至少包含common support、critical/safety slices、历史bad case和private holdback。VLA hard invariant应覆盖action shape/order/unit、finite、workspace/controller limit、allowed tool/scope与forbidden side effect；它们不是普通平均分。

### 2.2 防止 Golden Overfit

- training/dev、release golden与最终holdback分开；
- candidate运行前冻结case、expected、slice、weight、margin与exclusion；
- candidate失败后不能删case或改gold；修订必须发新suite version并让baseline/candidate一起重跑；
- 新incident可以append，retirement需reason、replacement与历史lineage；
- 训练重叠或泄漏标contaminated并fail closed。

## 3. Paired Delta，而非两个 Summary 相减

令`u_k`为方向统一成“越大越好”的指标。对相同case `i`：

\[
\Delta_{i,k}=u_k(c,i)-u_k(b,i),
\qquad
\bar\Delta_k=\frac{1}{n_k}\sum_i\Delta_{i,k}.
\]

变量解释：`c/b`是candidate/baseline；`k`可以是success、negative latency、negative intervention；`n_k`是valid paired common support。实现映射：EVAL-009 bundle保存两侧raw/parsed output、valid/exclusion、scorer contribution与case ID。不同`n`、scorer、init或protocol的aggregate差不是paired regression。

## 4. Non-inferiority Gate

对critical metric `k`冻结可容忍退化`δ_k`，并要求单侧置信下界不低于`-δ_k`：

\[
G_{offline}=
\mathbb{1}[H_{schema}=H_{safety}=H_{lineage}=1]
\prod_{k\in\mathcal K_{critical}}
\mathbb{1}\!\left[\operatorname{LCB}_{1-\alpha}(\bar\Delta_k)\ge-\delta_k\right].
\]

变量解释：`H`是不可被平均抵消的hard gate；`LCB`方法、`α`与多指标规则预注册；`δ_k`来自业务/安全容忍度，不从candidate结果倒推。实现映射：gate config和decision记录metric/slice、estimate、interval、margin、pass/fail及raw bundle SHA。missing、invalid、样本不足、CI不可算或protocol漂移默认fail closed。

“不显著”不等于“等价”；“overall更高”也不等于每个critical slice无回归。[1]

## 5. Hard Gate 与多目标 Guardrail

| 类型 | 例子 | 决策 |
| --- | --- | --- |
| lineage | checkpoint/processor/normalizer/protocol/scorer不完整 | veto |
| schema | parser、shape、axis、unit、NaN/Inf、动作越界 | veto |
| safety | forbidden side effect、scope、emergency stop、force/workspace limit | veto |
| accounting | planned/valid/excluded/missing不守恒、两侧非common support | veto |
| quality | overall/per-task/critical success、point/box/text | 分别做margin/CI |
| systems | p50/p95/p99 latency、deadline miss、timeout、memory | hard limit + trend |
| operations | intervention、fallback、cancel、recovery、drift | guardrail / veto |

不能把success、safety和latency压成一个overall weighted score后互相抵消。Breck等明确建议对重要slice设置absolute与incremental release tests，并由自动系统在serving前bless或veto。[1]

## 6. Decision Artifact

```text
release_gate/
  gate_config.json
  golden_manifest.json
  protocol_manifest.json
  raw/base/... + raw/candidate/...
  paired_delta.parquet
  decision.json
  approvals.json
  checksums/manifest-sha256.txt
```

`decision.json`至少保存baseline/candidate IDs、每个gate的输入与结论、missing/invalid、override、时间与SHA。人工override要有who/why/expiry，不能覆盖hard safety veto。

## 7. Shadow 与 Canary

### 7.1 Shadow

candidate读取live observations并产生raw action/tool plan，但不获得actuator或外部side-effect authority。比较candidate与known-good输出、延迟、invalid、constraint breach与分布漂移。shadow适合发现serving artifact、processor、schema或latency问题；它不能证明闭环恢复能力，因为candidate没有改变环境。

### 7.2 Canary

把exposure unit定义为request、episode、task-init、robot-hours或control steps，然后冻结：

- allowlisted低风险task/init/robot与authority；
- baseline/canary同时间窗、同scorer与尽可能相同support；
- minimum exposure与decision window；
- success、safety、latency、deadline、intervention、emergency stop、forbidden action与drift guardrails；
- 自动abort、known-good完整bundle与rollback drill；
- 每阶段promotion条件，禁止只凭“前几次没出错”扩量。

Argo Rollouts用`setWeight`、pause、analysis、success/failure condition、abort与rollback window表达progressive delivery；VLA借用状态机思想，但机器人还需要独立safety controller、速度/力/空间限制与human stop。[2]

## 8. Canary 通过能证明什么

只能证明：在已暴露support、时窗、authority、样本量与预注册guardrail下，没有触发拒绝条件。不能证明：全任务泛化、极端tail safety、长期drift稳定、counterfactual superiority或机器人安全认证。

如果candidate动作已经影响环境，baseline就没有同一counterfactual trajectory；此时只能报告observed canary outcome，不能把它包装成严格paired episode差异。

## 9. Release State Machine 伪代码

```python
def release_candidate(base, candidate, cfg):
    # 1. Verify hashes, identities, the same golden revision and common support.
    verify_lineage_protocol_and_support(base, candidate, cfg)

    # 2. Run fail-closed schema/action/safety/accounting hard gates.
    run_hard_gates(candidate, cfg.hard_invariants)

    # 3. Decide pre-registered paired non-inferiority per critical metric/slice.
    offline = paired_gate(base, candidate, cfg.margins, cfg.interval_method)
    if not offline.all_critical_pass:
        return abort_with_bundle("offline_regression", offline)

    # 4. Shadow live inputs without granting actuator authority.
    shadow = shadow_run(candidate, cfg.shadow_guardrails)
    if shadow.hard_breach:
        return abort_with_bundle("shadow_breach", shadow)

    # 5. Expand only after minimum exposure and the full decision window.
    for stage in cfg.canary_stages:
        result = canary_run(stage, known_good=base)
        if result.hard_breach or not result.analysis_pass:
            return rollback_known_good_with_bundle(stage, result)

    return promote_and_monitor(candidate)
```

这是面试中的工程设计，不代表五项目已运行统一平台。

## 10. 五项目怎么讲

### Robot Harness

有base/SFT/GRPO checkpoint和suite，但base/SFT `n=1333`、GRPO `n=1000`，hidden-embedding与token-overlap scorer不同；不能声称同协议regression。safety目前仍弱，应是hard gate而非被tool overall掩盖；browser只有format eval，没有runner canary。

### OPD

10k raw-holdout和ckpt1000–5000 by-format/by-pool曲线适合设计vector golden；不同pool最佳checkpoint不同，正说明不能选一个overall冠军。本地缺完整raw predictions、统一lineage与automatic gate。

### OpenPiVLA

public smoke、formal report和official-checkpoint diagnostics是不同lineage。97.4只是archive summary；formal Qwen checkpoint/raw eval缺失，因此不能用diagnostic rollout给97.4补golden gate。

### WAM

CoffeePressButton episode0 paired trace/video只能作一个diagnostic case；没有suite denominator、checkpoint-bound raw bundle或canary。

### UWM

`186/250`是user-confirmed summary，协议脚本有价值，但缺250 raw episodes与checkpoint/normalizer hash；可设计future golden manifest，不能说已有automatic regression。

## 11. 面试防线

- “我们每个checkpoint都跑评估”不等于“我们有regression gate”。
- “small canary无事故”不等于“证明安全”；要给exposure、window、guardrail与rollback。
- “p>0.05”不等于candidate non-inferior；margin与单侧决策要预注册。
- “overall涨了”不能抵消safety、critical slice或deadline下降。
- “项目用了某部署框架”只有本地配置/运行证据才能说；本页Argo仅作公开机制参考。

## 12. 最小补强顺序

1. 先闭合EVAL-009：两侧immutable raw bundle与同protocol/scorer；
2. 冻结golden manifest、critical slices、hard invariants、margin与missing policy；
3. 生成paired decision artifact并注入schema/safety/latency失败测试；
4. 做no-authority shadow；
5. 在有独立safety约束、known-good bundle和rollback drill后才做有限canary。

## 13. 本节点结论与下一入口

EVAL-010知识与一张题卡保持`WARN/unseen`。公开来源支持release test、automated veto、small-scale canary、progressive analysis与rollback；五项目均没有完整实现证据，面试回答必须使用“我会如何设计 / 当前缺什么”，不能改成“我们已经上线”。

下一节点是`VLA-EVAL-011`：offline metric与online success的相关性分析。没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. Breck et al., [*The ML Test Score*](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/), IEEE Big Data 2017。
2. Argo Rollouts, [Canary](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/canary/index.md)、[Analysis](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/analysis.md)、[Specification](https://github.com/argoproj/argo-rollouts/blob/9273b0ee05dbb629cc72fb9d343c08356c8379c8/docs/features/specification.md)。
3. Google SRE Workbook, [*Canarying Releases*](https://sre.google/workbook/canarying-releases/)（当前环境抓取受阻，仅作补充入口）。
4. [EVAL-010 Source Freeze](../sources/vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)。
5. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
