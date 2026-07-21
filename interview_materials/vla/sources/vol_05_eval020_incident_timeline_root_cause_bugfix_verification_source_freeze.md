# VOL 05 EVAL-020 Source Freeze：Incident Timeline、Root Cause 与 Bug-fix Verification

> 状态：`source_frozen / VLA-EVAL-020 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结incident lifecycle、impact与timeline、first verified divergence、hypothesis ledger、proximate/root cause边界、mitigation/recovery/fix/prevention语义、bisect适用条件、same-protocol red→green与fresh regression verification，并映射五项目当前证据；只服务`VLA-EVAL-020`，EVAL-021后置。

## 问题（Question）

线上VLA评估、训练或部署发生事故后，怎样从“什么时候坏了”推进到“为什么坏了”，再证明修复确实消除了目标failure且没有制造相邻回归？可信答案不是“最后一次改动就是根因”或“rollback后恢复所以修好了”，而是保存不可变incident bundle，重建带provenance的timeline，定位first verified divergence，以可证伪hypothesis驱动干预，并用同协议red→green、未受影响controls与fresh neighboring cases闭合verification。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Google SRE Book, *Postmortem Culture: Learning from Failure* | official book page；2016 book chapter；2026-07-19抓取；页面许可未断言 | page `885916e3c46dfb2cf3a506435f9df60ca1bf3e491e521725705f7202ac12eb49` | postmortem记录incident、impact、mitigation/resolution、root causes与follow-up；预先定义trigger；blameless地关注contributing causes | Google流程是VLA专用标准；模板字段本身证明根因；“不责备”等于不追责系统缺口 |
| S2 | Google SRE Workbook, *Postmortem Culture: Learning from Failure* | official workbook page；2018 workbook chapter；2026-07-19抓取；页面许可未断言 | page `68a91385357957faa3d46927b88af63e047cd5e0b228c52a024c6093c24e0018` | standard template、incident roles、detailed timeline/log、affected/root-cause services、severity、detection、action-item质量与复盘文化 | 示例中的某个具体root cause可直接迁移到机器人；写了action item就已验证有效 |
| S3 | Nelson et al., NIST SP 800-61r3, *Incident Response Recommendations and Considerations for Cybersecurity Risk Management* | official final publication；April 2025；DOI `10.6028/NIST.SP.800-61r3`；U.S. government work / NIST attribution requested | landing page `ae9e30e74c12b16123da12cc4b92ba4a5e6bcabf8a3fbdc621751ea1b6270faf`；PDF `e5593d6bb85daecec7e8d9549400c7b3473bcc3f06e469c82218073afa7fba2d` | Detect–Respond–Recover与持续改进、lessons learned和root-cause analysis进入风险管理 | security-specific controls天然是VLA事故规范；该文给出本页的机器人阈值、统计方法或项目结论 |
| S4 | `git/git`, `git-bisect` official documentation | official code/docs；commit `41365c2a9ba347870b80881c0d67454edd22fd49`（2026-07-17）；GPL-2.0 | API snapshot `bde74b0a4fa49338b96cf0fb24ec6f624eb80ad64f81f046eca94cde08491dfa`；`Documentation/git-bisect.adoc` `53541ad4a429c0fb51ada9720ee7356e0fee207ce176cafe53e15bc65a0db3f2`；`COPYING` `5b2198d1645f767585e8a88ac0499b04472164c0d2da22e75ecf97ef443ab32e` | 用known-good/known-bad与可判定测试做二分搜索，定位first bad commit；`skip`/`run`接口 | first bad commit自动等于root cause；数据/环境/scorer漂移或flaky oracle下仍可无条件二分 |
| S5 | 本地前置节点 | canonical local prerequisites | EVAL-008 `580ac70922472453c8806265b2fd4bae8dad7881bad3da2e8f211c870e1f37b0`；EVAL-009 `be6945d2475585f65cd74417070fbd4fee1b148660b35c139370935413b13dea`；EVAL-010 `512d9e16b392e7258358c0092dff6ff5049890040d8d5efd1fdadfe7048b2911`；EVAL-013 `9b47d6cd3dbea63e16d80c2fd25c7d68d1aa8f642b11b75913eb58f7449470bb`；EVAL-014 `2027ea608960749f407099c56bac92528157e2125fd83525618507aa9f9f614a`；EVAL-018 `3798164600cdaacf43473d55e7f8d964cbbcc781e01ef1efa37ca88e82634bfd` | failure taxonomy、recomputable bundle、regression gate、clock/latency、cancel/recovery与因果识别边界 | 五项目已有完整事故闭环；公开框架已在本地实现 |
| S6 | 五项目claim–evidence inventories | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d` | 项目failure、局部干预、诊断与缺失artifact的证据梯度 | 任何项目已有完整timeline、confirmed RCA、paired multi-seed fix verification或预防闭环 |

S1—S4冻结复盘、生命周期与二分定位的公共边界；S5—S6把它们映射到VLA。本页的incident schema、cause ladder、verification矩阵与统计合同是source-consistent engineering synthesis，不冒充Google、NIST、Git或五项目原生实现。

## 2. 先分清十一种语义

```text
incident / impact
 -> observed symptom
 -> first verified divergence
 -> hypothesis
 -> contributing condition
 -> proximate cause
 -> confirmed root cause
 -> mitigation / rollback / workaround
 -> recovery
 -> corrective fix
 -> regression prevention
```

| 术语 | 回答的问题 | 证据最低要求 |
| --- | --- | --- |
| incident | 什么异常触发响应 | trigger、time window、owner、severity |
| impact | 谁/什么被影响到什么程度 | support、duration、denominator、forbidden effect |
| symptom | 首先观察到什么 | raw alert/log/trace/video/scorer output |
| first verified divergence | 与known-good相比最早在哪一层不同 | 同源时钟、aligned trace、artifact identity |
| hypothesis | 哪个机制可能解释failure | 可证伪预测与下一实验 |
| contributing condition | 放大概率或blast radius的条件 | 条件存在且与failure路径相关 |
| proximate cause | 直接触发异常的近端事件 | trace/干预支持，但未必解释系统为何允许它发生 |
| root cause | 移除后在目标support上消失的系统性必要/充分因素组合 | 可复现、针对干预、red→green、controls、fresh cases |
| mitigation | 暂时降低影响 | 恢复服务但未必消除原因 |
| corrective fix | 改变失败机制 | patch/config/data/scorer bundle与same-protocol verification |
| prevention | 降低复发或缩短检测/恢复 | guardrail、test、monitor、owner、deadline与后续有效性检查 |

“human error”不能作为根因终点。要继续问：什么界面、默认值、权限、review、自动化、observability或runbook使一个合理的局部动作能扩大为事故。[S1][S2]

## 3. Incident Manifest 与 Impact Contract

事故开始时先保存事实，而不是边修边覆盖现场：

- `incident_id`、trigger、severity与声明时刻；
- affected task/site/robot/model/checkpoint/scorer/data/config/controller；
- start/detect/ack/mitigate/recover/end时间及clock domain；
- expected vs observed、denominator、unknown impact与禁止外推；
- raw log/trace/video/metrics/alerts、版本与SHA；
- responder操作、rollback、restart、manual override与side effects；
- evidence retention、PII/secret redaction和访问控制。

impact不能只写“成功率下降”。至少给出support、基线、窗口、样本量、任务/机器人/用户影响与不确定性；若没有完整denominator就标`lower_bound`或`unknown`。

## 4. Timeline 不是事件列表，而是带 Provenance 的偏序

`timeline.jsonl`每条建议包含：

```json
{
  "event_id": "evt-0042",
  "observed_at_utc": "...",
  "source_clock": "robot_monotonic_ns",
  "clock_sync_error_ms": 3.2,
  "actor": "policy-server",
  "action": "checkpoint_load",
  "object_sha256": "...",
  "evidence_uri": "raw/log.jsonl#L...",
  "fact_or_inference": "fact",
  "confidence": "high"
}
```

必须分开event发生时刻、被观测时刻、被写入时刻和复盘推断时刻。跨robot、server、simulator、GPU和scorer时钟若未同步，只能建立带误差的happens-before或偏序，不能用日志行号伪造精确全序。[S5]

## 5. First Verified Divergence

从incident symptom向前对齐known-good/bad traces，逐层寻找最早可复现差异：

```text
input/data -> preprocess/normalizer -> model outputs
 -> action decode/chunk -> queue/network -> controller
 -> physical state/effect -> scorer/summary
```

“最早看见的告警”通常不是first divergence；“最早divergence”也未必是root cause。例如action解码首次偏离可能由上游processor错配、旧normalizer、stale observation或data shift导致。

每个divergence要绑定same episode/input、same checkpoint lineage、same scorer revision、aligned timestamp与raw values；无法对齐时保持`candidate_divergence`。

## 6. Hypothesis Ledger：可证伪，而不是故事接龙

每个hypothesis至少记录：

| 字段 | 示例语义 |
| --- | --- |
| claim | “strict point parser拒绝裸坐标输出” |
| predicted observation | parser error上升；格式修正后format pass恢复 |
| disconfirming observation | 同parser对known-good也失败，或修格式后failure不变 |
| intervention | 只替换prompt/parser协议，其余锁定 |
| affected controls | strict-format rows |
| unaffected controls | box/text或已合规point rows |
| result | supported / weakened / rejected / inconclusive |
| evidence SHA | exact replay rows、diff与logs |

ledger保留被拒绝路径，避免事后只留下“看起来早就知道”的故事。一次实验若同时改checkpoint、prompt、parser、data与scorer，只能说明bundle change相关，不能识别单一root cause。[S5]

## 7. 时间先后、相关、近端原因与 Root Cause

以下都不自动证明root cause：

- failure发生在某commit之后；
- rollback后指标恢复；
- 最后一次改动恰好触及出错模块；
- 单episode中该信号异常；
- patch后一次rerun通过；
- `git bisect`给出first bad commit。

它们可以提高某个hypothesis优先级。要升级confirmed root cause，至少需要：

1. immutable incident bundle与failure可复现；
2. known-good/bad间first divergence可定位；
3. 干预只针对候选机制，或用factorial/matched design隔离；
4. 同协议、同受影响support实现red→green；
5. unaffected controls不退化；
6. fresh neighboring cases也通过；
7. flaky/seed/task/site不确定性被量化；
8. rollback/mitigation与真正fix的语义分开。

无法稳定复现时，应写`root_cause_status: unknown`或`partially_confirmed`，并列出当前最强证据和替代解释。

## 8. `git bisect` 的正确位置

Git官方文档以known-good与known-bad端点，通过二分选择中间commit并由test判定good/bad，直到找到first bad commit；`git bisect run`可自动执行判定，`skip`用于无法测试的revision。[S4]

可用条件：

- failure在commit序列上近似单调；
- 每个revision可构建并绑定相同data/config/checkpoint/scorer；
- oracle稳定，good/bad阈值预先定义；
- external dependency、driver、hardware和random seed可冻结。

失效条件：flaky test、多处交互change、不可构建commit、数据/模型/环境漂移、非单调修复又复发、score连续且阈值事后改变。此时bisect输出是“first revision classified bad under this oracle”，不是自动的机制证明。

## 9. Mitigation、Rollback、Recovery、Fix 与 Prevention

| 动作 | 典型例子 | 能证明什么 | 不能证明 |
| --- | --- | --- | --- |
| mitigation | 限流、禁用高风险task、切fallback | impact被控制 | 原因消失 |
| rollback | 回到known-good bundle | 旧bundle在当前窗口可恢复 | 最后change是唯一root cause |
| workaround | 强制eager、preload data、人工格式修正 | 绕过特定failure path | 长期机制修复 |
| recovery | service/robot回到SLO或safe state | 当前运行恢复 | regression不会复发 |
| corrective fix | parser合同、chunk schema、guardrail patch | 候选机制被改变 | 没有same-protocol实验时的因果闭环 |
| prevention | CI gate、schema check、monitor、runbook | 复发更难或更快发现 | action item一定长期有效 |

postmortem应把action item写成owner、priority、deadline、artifact、verification test和closure evidence；“加强测试”“以后小心”不可验收。[S1][S2]

## 10. Bug-fix Verification：Exact Replay 与 Fresh Regression

验证矩阵至少包含四格：

| Cell | before | after | 目的 |
| --- | --- | --- | --- |
| affected exact replay | RED | GREEN | patch是否消除原failure |
| unaffected exact controls | GREEN | GREEN | 是否破坏已正常路径 |
| fresh affected-neighbor cases | RED/unknown | GREEN | 是否只记住incident样本 |
| stress / boundary / rollback | bounded expectation | bounded expectation | 边界、恢复与fallback是否仍成立 |

同协议意味着checkpoint/data/input IDs/seed/init/processor/normalizer/controller/scorer/hardware或允许差异全部登记；只允许target patch变化。若必须改变多个因素，使用2×2/多臂设计或把结论降级为bundle-level fix。[S5]

## 11. Paired Effect 与不确定性

对相同episode/task-init pair `i` 的failure indicator，令`Y_i^-=1`表示修复前成功，`Y_i^+=1`表示修复后成功，paired uplift为：

\[
\widehat{\Delta}_{fix}=\frac{1}{n}\sum_{i=1}^{n}(Y_i^+-Y_i^-).
\]

变量解释：`n`是完全matched且可判定的pairs；invalid/missing不能静默删除。直觉：同一困难样本前后对照，减少support差异。实现映射：保存pair ID、before/after bundle SHA、raw outputs与McNemar/cluster bootstrap结果；任务/seed/robot相关时按cluster重采样。[S5]

如果原failure是概率性事件，`k`次独立或按cluster设计的reproduction中观察到`r`次，诊断复现率为：

\[
\widehat p_{repro}=\frac{r}{k}.
\]

变量解释：`r`是严格按failure predicate判定的失败次数，`k`是预先计划的尝试数。直觉：`1/1`通过不能排除低频复发。实现映射：报告置信区间、sequential stopping和所有attempt；不能只保留一次绿色结果。

## 12. Flaky、Non-reproducible 与 Confounded Incident

- 先检查oracle/scorer是否稳定，再检查被测系统；
- 固定randomness、clock、resource、dependency、data order和warmup；
- 区分intermittent failure与invalid observation；
- 对rare failure扩大duration/episodes，但预先定义停止规则；
- 若多个因素同时漂移，构造minimal reproducer和factorial cells；
- 无法复现时保留原raw bundle，升级observability，不编造root cause。

`skip`一个不可测commit、重跑到出现期望结果或事后更换failure predicate都会改变证据，应进入bisect/experiment ledger。

## 13. Blameless 不等于无责任边界

Google SRE强调不把个人/团队的“坏行为”作为复盘中心，而是理解当时信息、工具和系统条件。[S1] 对VLA事故应继续追问：

- 为什么unsafe/default配置可被接受？
- 为什么bundle、normalizer或scorer不做identity gate？
- 为什么异常没有在sim/shadow/golden阶段被发现？
- 为什么operator看不到stale observation、queue age或parser rejection？
- 为什么rollback不能一键、安全、可审计？

同时仍要明确decision owner、approval boundary、action-item owner和due date；blameless是提高信息质量，不是抹除职责。

## 14. Incident State Machine

```text
DETECTED
 -> TRIAGED + impact bounded
 -> MITIGATING
 -> RECOVERED (service/safety restored)
 -> INVESTIGATING (timeline + reproducer + hypotheses)
 -> ROOT_CAUSE_UNKNOWN / PARTIAL / CONFIRMED
 -> FIX_CANDIDATE
 -> VERIFIED_ON_INCIDENT_REPLAY
 -> VERIFIED_ON_CONTROLS_AND_FRESH_CASES
 -> PREVENTION_GATES_ACTIVE
 -> CLOSED_WITH_FOLLOWUP
```

`RECOVERED`不等于`FIXED`，`FIXED`不等于`PREVENTED`。关闭事故前若root cause仍unknown，可以诚实关闭服务响应阶段，但RCA/action items保持open。

## 15. 最小 Artifact Bundle

```text
incident/
  incident_manifest.json
  impact_scope.json
  timeline.jsonl
  raw_logs_traces_video/
  first_divergence.json
  hypothesis_ledger.jsonl
  code_config_data_model_scorer_diffs/
  minimal_reproducer/
  bisect_ledger.jsonl
  fix_patch_manifest.json
  exact_replay_before_after.parquet
  affected_slice_regression.parquet
  unaffected_controls.parquet
  fresh_neighbor_cases.parquet
  rollback_recovery_log.jsonl
  action_items.jsonl
  checksums/manifest-sha256.txt
  reproduce.ps1
```

`incident_manifest`引用全部子artifact SHA与retention policy；`fix_patch_manifest`只声明允许变化；before/after rows必须能回算failure predicate和summary。

## 16. 调查与验证伪代码

```python
def investigate_and_verify(incident, known_good, candidate_fix, spec):
    bundle = freeze_incident_bundle(incident, spec.retention)
    timeline = build_clock_aware_timeline(bundle)
    impact = bound_impact(bundle, spec.impact_contract)

    reproducer = minimize_while_preserving_failure(bundle, spec.failure_predicate)
    divergence = align_and_find_first_verified_divergence(known_good, reproducer)
    hypotheses = run_falsifiable_interventions(divergence, spec.hypothesis_ledger)

    cause = classify_cause_strength(hypotheses)
    if cause.status not in {"confirmed", "partially_confirmed"}:
        persist_unknowns_and_improve_observability()

    before_after = exact_same_protocol_replay(reproducer, candidate_fix)
    controls = run_unaffected_controls(candidate_fix, spec.controls)
    fresh = run_fresh_neighbor_cases(candidate_fix, spec.fresh_support)
    return close_only_if_evidence_complete(
        impact, cause, before_after, controls, fresh, spec.action_items
    )
```

伪代码是未来验收合同，不代表五项目已有incident platform或完整RCA。

## 17. 五项目 Evidence Mapping

| 项目 | 当前failure / intervention证据 | 可安全解释 | 不能说 / 缺口 | 下一验证 |
| --- | --- | --- | --- | --- |
| OPD | 早期point prompt示例使用裸`[(x,y)]`，strict parser要求`<point>[[...]]</point>`；原strict下base等为0；protocol-fixed后Qwen-122B format `0.9986`、Hit@100 `0.8200`，Qwen3-35B-VL format `0.9857`、Hit@100 `0.7871` | 强局部“协议/解析层RED→GREEN”案例；支持格式契约导致strict rejection的局部解释 | 不能外推模型整体point能力、所有checkpoint、全部root cause或fresh regression已闭环 | 冻结相同rows/checkpoint/scorer；保留unaffected box/text controls与fresh point templates |
| UWM / LIBERO | zarr小chunk随机读导致DataLoader stall的bounded smoke；preload+infinite后p95 wait约`13.86s→0.19s` | DataLoader-only A/B支持输入等待定位与局部mitigation | 不是完整GPU训练吞吐root cause；缺matched end-to-end rerun；`186/250` raw仍缺 | 同config/hardware做loader与step-time paired trace、GPU idle control与长跑稳定性 |
| WAM | gripper/high-sigma/conditioning/DeepSpeed/OOM/state_dict多为hypotheses；单episode diagnostic与单sample 5k/10k proxy | 可展示hypothesis ledger和需要的反证实验 | 无paired fix rerun，不能称confirmed root cause或bug fixed | minimal reproducer、binary/checkpoint锁定、同seed多episodebefore/after |
| OpenPiVLA | formal Qwen路径使用eager attention；源码/report可读 | eager可描述为兼容/稳定性选择或workaround | 缺checkpoint binary/load smoke与正式benchmark；不能称质量root-cause fix | locked bundle load/forward parity、same-checkpoint eager/alternative A/B与fresh suite |
| Robot Harness | safety多步telecom repair的gold需5个tool steps，模型只选1个；safety tool accuracy约`38–44%` | 清晰failure case，可建立first divergence与hypothesis tree | 当前是失败，不是已修复事故；缺per-sample trace和matched fix rerun | 保存tool trace，区分planner/router/runtime/scorer，做exact replay与neighbor workflows |

OPD是当前最接近局部fix verification的案例，但仍缺完整incident timeline、same-row before/after bundle、unaffected controls和fresh neighboring templates；因此只到`partially_confirmed / protocol-bounded`。UWM是DataLoader子系统A/B，不能升级为端到端训练事故根因。其余项目保持hypothesis/failure层。

## 18. 常见失败模式

| 失败模式 | 症状 | 修复 |
| --- | --- | --- |
| last-change bias | 自动把最后commit写成根因 | timeline + competing hypotheses + targeted intervention |
| rollback proof | 恢复后宣布机制已证实 | rollback只记recovery；另做fix verification |
| one-green-run | 只展示一次通过 | 预注册attempt、paired/fresh/cluster不确定性 |
| metric drift | before/after scorer不同 | scorer bundle lock与semantic diff |
| support drift | 换了更容易的episode | exact pair registry与fresh support说明 |
| post-hoc predicate | 看结果后改failure定义 | 事前failure contract与deviation ledger |
| human-error stop | 归咎操作员 | 追到系统条件、guardrail、review与observability |
| action-item theater | “加强测试/培训” | owner、deadline、test、artifact与closure证据 |
| hidden invalids | build/load/timeout被删 | planned/valid/failed守恒 |
| bisect overclaim | first bad commit=根因 | 稳定oracle、环境锁定与机制干预 |

## 19. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 设计incident/postmortem流程 | 本页、schema与review |
| C1 | 描述已观察failure与局部时间线 | raw log/trace/video、bundle身份与impact scope |
| C2 | 候选机制被局部支持 | reproducer、first divergence、targeted intervention与替代解释 |
| C3 | root cause/fix在目标support确认 | same-protocol red→green、controls、fresh cases与不确定性 |
| C4 | 预防措施长期有效 | regression gate、monitor、owner、后续incident/drift统计 |

当前OPD最多是局部C2并接近狭窄C3输入，UWM是子系统C2输入，其余主要C1/hypothesis；五项目都不到完整C3/C4。本节点保持`WARN`；下一内容节点固定为`VLA-EVAL-021`：deployment drift、data shift与持续监控。本切片不生成EVAL-021，也不创建`coaching_state.md`。

## 参考文献（References）

1. Google SRE, [*Postmortem Culture: Learning from Failure*](https://sre.google/sre-book/postmortem-culture/), Site Reliability Engineering。
2. Google SRE Workbook, [*Postmortem Culture: Learning from Failure*](https://sre.google/workbook/postmortem-culture/)。
3. Nelson et al., [NIST SP 800-61r3](https://doi.org/10.6028/NIST.SP.800-61r3), April 2025。
4. `git/git`, [`git-bisect` documentation@`41365c2`](https://github.com/git/git/blob/41365c2a9ba347870b80881c0d67454edd22fd49/Documentation/git-bisect.adoc)。
5. [EVAL-008 Failure Taxonomy](vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)、[EVAL-009 Recomputable Bundle](vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)、[EVAL-010 Regression Gate](vol_05_eval010_regression_gate_golden_set_canary_rollout_source_freeze.html)、[EVAL-013 Clock / Latency](vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)、[EVAL-014 Recovery](vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)与[EVAL-018 Causal Boundary](vol_05_eval018_factorial_ablation_matched_baseline_causal_boundary_source_freeze.html)。
6. [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
