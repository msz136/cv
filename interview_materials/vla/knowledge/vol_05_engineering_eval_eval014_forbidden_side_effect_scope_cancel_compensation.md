# VLA Engineering / Evaluation：Forbidden Side Effect、Scope、取消与补偿

> 节点：`VLA-EVAL-014`  
> 状态：`drafted / knowledge_36_of_44 / card_1_of_1_unseen / WARN`  
> 更新日期：2026-07-19  
> 学习目标：能从authority、dispatch、effect sink、cancel/quiescence、compensation和irreversible residual构造可复算评估；不把文本安全、tool-call格式、timeout或cancel acknowledgement误写成真实副作用安全。

## 1. 一页结论

```text
request + current state
  -> resolve real tool/resource/parameters
  -> server-side authorization at dispatch time
  -> execute with operation/idempotency key
  -> observe authoritative effect sink
  -> on cancel: stop new dispatch -> reach quiescence
  -> inspect committed effects -> compensate or manual reconcile
```

面试时先给四条边界：

1. forbidden effect在真实sink/state diff判定，不能用“模型没说危险话”代替；
2. scope至少绑定subject、resource、action、parameters、time/purpose、approval与state version；
3. cancellation不是rollback，accepted也不等于executor已经静止；
4. compensation是可能失败的领域化新动作，不可逆点必须事前审批并人工处置。

## 2. 从 Intent 到 Committed Effect

同一操作要拆成四层：

| 层 | 观测对象 | 为什么保留 |
| --- | --- | --- |
| attempted | model/agent intent、resolved plan | 衡量攻击与策略倾向 |
| authorized | policy decision与granted scope | 评估false allow/false deny |
| dispatched | server发给真实executor的命令 | 查绕过、late/duplicate dispatch |
| committed | actuator、订单、数据库等权威sink改变 | 判定真正forbidden side effect |

对预注册的forbidden case：

\[
V_i=\mathbb{1}[\text{forbidden effect committed at authoritative sink}].
\]

变量解释：`V_i`只在禁止的effect真正提交时为1。直觉：一个危险intent被server拒绝，是防线成功而非事故；一个无显式tool-call的后台effect仍可能是事故。实现映射：保存case/operation ID、auth、dispatch、sink before/after及effect reference。[1]

因此“unsafe response rate”“tool-call validity”和“forbidden commit rate”必须分开。文本scorer适合早期coverage，不能承担最终真实副作用判定。

## 3. Scope 的完整上下文

OAuth scope说明requested scope可以被server缩小，实际granted scope需要明确返回；OWASP强调least privilege、deny by default和每个请求都校验。[2][3] 在embodied系统中，一个`robot:control`字符串仍过粗，最小scope合同应含：

```text
subject / tenant
robot, resource, workspace
resolved tool and action
normalized parameter constraints
valid time and purpose/task
approval and risk tier
operation/idempotency key
expected state version
```

授权函数可表示为：

\[
A_i=\pi_{\mathrm{auth}}(s_i,r_i,a_i,p_i,t_i,u_i,v_i)\in\{0,1\}.
\]

变量解释：`s`是subject，`r`是resource，`a`是action，`p`是参数，`t/u`是时间与用途/审批，`v`是状态版本。直觉：同一工具换机器人、区域、力阈值、有效期或当前状态后，授权结论可能相反。实现映射：在dispatch前对resolved action重新求值，日志保存policy version、完整input、decision、reason、granted scope和expiry。

### 3.1 为什么 planner 检查不够

planner可能看到alias而非最终executor，可能在计划后等待导致approval过期，也可能被另一个worker重绑resource。执行server必须是enforcement point；缺attribute、无法解析resource或policy timeout时默认deny，并把infra error与policy deny分开记录。

### 3.2 False Allow 与 False Deny

false allow是本应拒绝却放行，可能产生安全事故；false deny是合法动作被拒绝，降低任务成功。不能用总accuracy平均：安全gate看false allow/forbidden commit，utility gate独立看allowed-case success与false deny。deny-all不是好系统。

## 4. Cancellation 状态机

可靠评估使用如下阶段，而不是一个`cancelled=true`：

```text
cancel requested
  -> accepted | rejected
  -> new dispatch gated
  -> executor/actuator quiescent
  -> committed effects classified
  -> compensated | residual | irreversible/manual
```

ROS 2 Actions允许cancel被拒绝，`CANCELING`只是过渡态；server可在最终`CANCELED`前执行用户清理。[4] `asyncio`取消也可能等待cleanup，且不会撤销外部系统已经接受的命令。[5]

### 4.1 Quiescence 而非 API Latency

\[
T_i^{\mathrm{quiesce}}
=t_i^{\mathrm{last\ effect}}-t_i^{\mathrm{cancel\ request}}.
\]

变量解释：终点是权威sink上最后一次相关effect，不是HTTP 200或task抛出`CancelledError`。直觉：controller已经回复“收到”，机械臂仍可能执行在途chunk。实现映射：把cancel request/accept、last dispatch、executor ack、每次effect和观察窗连接到同一operation ID。

还应报告post-cancel effect count、late completion、cancel rejection、观察窗内是否继续运动/写入，以及accepted→quiescent分段时间。timeout和cancel也要分开：timeout是调用方不再等待，后台work可能继续。

### 4.2 取消时机矩阵

| 注入点 | 主要预期 |
| --- | --- |
| authorization之前 | 无auth/dispatch/effect |
| auth之后、dispatch之前 | gate阻止新dispatch |
| execution中 | cancel可接受或拒绝；测quiescence和残留 |
| effect commit之后 | stop未来动作，分类并补偿已提交effect |
| point-of-no-return之后 | 不承诺rollback；进入manual reconciliation |

注入点应用事件条件定义，避免`Sleep(100ms)`在不同负载下落入不同阶段。

## 5. Compensation 不是 Undo 按钮

补偿事务模式把undo理解为新的、领域化动作：可能不能还原原状态，执行顺序也不一定严格逆序；补偿本身可能失败，需要持久化、恢复、幂等和审计。[6]

例如：

- 已移动物体：可尝试放回，但位置误差、碰撞和场景变化形成残留；
- 已创建订单：可能只能提交取消/退款，而非让订单从未存在；
- 已发消息：不能“取消接收者已看见”，只能发更正并升级人工；
- 已写外部系统：需要对方支持幂等key、版本条件或补偿API。

最终残留：

\[
R_i=d\!\left(S_i^{\mathrm{final}},S_i^{\mathrm{expected\ safe/compensated}}\right).
\]

变量解释：`d`是每种领域预注册的状态比较器。直觉：补偿API成功不等于业务/物理状态已安全。实现映射：保存initial、committed、post-compensation snapshots，记录allowed residual、failed steps、owner和manual ticket。

每个forward step记录effect ref、compensation action/precondition、operation key、state version、attempts、terminal result与residual。补偿失败重试必须幂等；否则恢复流程会制造第二次副作用。

## 6. Point of No Return 与人工审批

不可逆或高影响步骤需要在执行前标记：

- 是否存在可靠补偿；
- 到哪一个事件后不可逆；
- 需要何种human approval、双人复核或hardware interlock；
- approval绑定的resource、parameter、state version与expiry；
- 失败时谁接管、如何隔离与记录。

不能把“稍后可以补偿”当作放宽权限的理由。越过point of no return前应采用更窄scope、fresh approval和commit-time revalidation；信息不足时阻断或转人工。

## 7. 间接工具、组合风险与重试

只检查tool name会漏掉三类风险：

1. **间接执行**：alias、semantic navigation、nested tool或后台job最终调用未授权executor；
2. **组合风险**：两个单独允许的动作组合成禁区进入、数据外发或危险状态；
3. **交付语义**：retry、duplicate、out-of-order、late response或stale state造成重复effect。

授权和policy state必须看resolved executor、完整参数、prior effects与current state。operation/idempotency key用于识别同一意图，state version防止旧授权在新状态下提交；二者不能互相替代。

## 8. 指标体系

主安全率：

\[
\widehat r_{\mathrm{forbidden}}
=\frac{\sum_{i=1}^{N_f}V_i}{N_f}.
\]

变量解释：`N_f`是预注册的forbidden test cases；timeout、reject和infra failure不能静默移出分母。直觉：对critical effect通常用hard veto，并报告`k/N_f`与区间，而非和success加权。实现映射：raw case ledger可独立重算，另列invalid/infra状态。

完整dashboard至少包含：

| 维度 | 读数 |
| --- | --- |
| authority | false allow / false deny；按resource/parameter/time/approval分层 |
| dispatch | forbidden、late、duplicate、wrong-resource dispatch |
| sink | forbidden commit、duplicate effect、irreversible exposure |
| cancel | request/accept/reject、quiescence latency、post-cancel effect |
| compensation | attempted/success/failed/manual、residual、retries |
| evidence | event join completeness、clock anomaly、checksum/recompute |
| utility | allowed task success、latency、unnecessary deny |

critical forbidden commit不能由平均reward、任务成功或补偿成功抵消；但零事故也不能掩盖全拒绝。采用hard safety gate + separate utility floor。

## 9. Adversarial Test Matrix

| family | 示例 | oracle |
| --- | --- | --- |
| identity/resource | wrong tenant、robot B、未绑定resource | deny且sink无变化 |
| parameters | 合法tool + 禁区/超力/超数量 | 参数级deny |
| lifecycle | expired/revoked approval、policy更新 | dispatch前重验 |
| indirection | alias、hidden/composite/background | resolved action受同一policy |
| cancellation | before dispatch、during、after commit | no-new-dispatch、quiescence、residual |
| delivery | retry storm、duplicate、out-of-order | 最多一次预期effect |
| compensation | failure、restart、partial success | durable/resumable/manual |
| irreversibility | commit前后取消 | approval或人工reconcile |
| composition | 单项允许但序列禁止 | state/plan级阻断 |
| legitimate | 正常scope与正常任务 | 控制false deny和utility |

每个case冻结initial snapshot、principal、requested/granted scope、expected auth、allowed/forbidden effect、cancel event、compensation oracle和terminal window。攻击样例与正常样例都要覆盖，避免只优化安全拒绝率。

## 10. Evidence Protocol 与 Gate

1. 固定candidate/baseline、tool registry、auth policy/version、executor、initial state和fault schedule；
2. 在可恢复sandbox先测，再用低能量、隔离、hardware interlock和人工监督逐级canary；
3. auth、dispatch、executor、sink与compensation用case/operation/step IDs连接；
4. 保存sink before/committed/after-compensation三份证据；
5. 关键case按seed/state snapshot配对，raw ledger先落盘、summary后计算；
6. critical forbidden commit、wrong-resource effect或未审批不可逆操作为hard veto；
7. 同时要求allowed-case utility floor，防止deny-all；
8. 使用EVAL-009可复算bundle和EVAL-010 golden/adversarial/canary gate。[7][8]

proxy scorer、mock executor和simulator用于扩coverage，不替代真实sink。真机测试范围必须由风险评估授权；知识页本身不授权执行危险动作。

## 11. Artifact Bundle

```text
side_effect_eval/
  policy_scope_manifest.json
  test_cases.jsonl
  auth_decisions.jsonl
  operation_event_ledger.parquet
  effect_sink_before_after/
  cancel_traces.jsonl
  compensation_ledger.jsonl
  irreversible_manual_review.jsonl
  summaries/by_case.json
  checksums/manifest-sha256.txt
  reproduce.ps1
```

```python
def run_case(case, agent, authz, executor, sink):
    sink.restore(case.initial_snapshot)  # Sandbox only.
    ledger = begin(case)
    for action in resolve(agent.plan(case.request)):
        decision = authz.check(action, case.context, at="pre_dispatch")
        ledger.auth(decision)
        if decision.allowed:
            executor.dispatch(action, operation_key=case.operation_key)
        inject_cancel_on_registered_event(case, executor, ledger)

    executor.await_quiescence(case.terminal_window)
    committed = sink.diff(case.initial_snapshot)
    residual = compensate_then_recheck(case, committed, sink, ledger)
    persist_raw_case(ledger, committed, residual)
```

这是测量合同，不代表本地项目已经具备restore、quiescence或compensation实现。

## 12. 五项目面试边界

### Robot Harness

可直接核验的入口包括scope/robot绑定、tool allowlist、cancel event、499/abort、tool前后取消检查、timeout、lock cleanup和best-effort stop/cancel。它支持“我设计/核验了控制入口与proxy评估”，不支持“所有越权均阻断”“cancel后零effect”“已发生副作用完整恢复”或真机认证。[9]

inventory中`RH-CL-009 safety side-effect 已解决`仍为`FAIL`。safety suite测的是结构化tool/scope proxy：8B约44.3% tool、49.1% coverage，32B约37–39% tool、43–45% coverage；sandbox 100%也只说明相应结构化proxy通过。面试应主动说清分母、scorer和真实sink缺口。

### OPD / OpenPiVLA / WAM / UWM

- OPD是静态感知评估，没有side-effect authority或executor；
- OpenPiVLA有serving timeout入口，但timeout不证明取消和静止；
- WAM action/video trace可做离线constraint检查，不能证明真实授权或sink；
- UWM训练数据流水线与side-effect安全没有直接证据。

四者均不可编造cancel、compensation或forbidden commit结果。

## 13. 面试追问防线

- **cancel API返回200够吗？** 不够；要看accepted、last dispatch、quiescence与post-cancel sink effect。
- **stop和rollback区别？** stop阻止后续执行；rollback/compensation处理已提交状态，且可能不完整或失败。
- **有allowlist还要什么？** resolved resource、参数、时效、approval、state version、组合序列和每次dispatch重验。
- **零unsafe tool call能证明安全吗？** 不能；可能是scorer漏检、间接effect或deny-all，最终看sink commit与正常任务utility。
- **补偿成功是否事故清零？** 不能；看最终residual、不可逆信息暴露和审计/人工成本。
- **retry怎样安全？** operation/idempotency key避免重复意图，state version避免旧状态提交，sink仍需去重与核验。
- **项目里做到了哪一级？** 当前是局部入口与proxy证据；真实effect-sink C2—C4没有材料，不越界。

## 14. 本节点状态

EVAL-014知识与一张题卡保持`WARN/unseen`，因为五项目缺少protocol-complete真实effect-sink评估。下一节点是`VLA-EVAL-015`：reward/scorer hacking与adversarial evaluation。没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. [EVAL-014 Source Freeze](../sources/vol_05_eval014_forbidden_side_effect_scope_cancel_compensation_source_freeze.html)。
2. IETF, [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749), 2012。
3. OWASP, [Authorization Cheat Sheet@ae0b3f2](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Authorization_Cheat_Sheet.md)。
4. ROS 2 Design, [Actions@93a415b](https://github.com/ros2/design/blob/93a415bf928751d37fce6f83215c521658e20c93/articles/actions.md)。
5. CPython, [`asyncio-task.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/asyncio-task.rst)。
6. Microsoft Architecture Center, [Compensating Transaction pattern@e76b316](https://github.com/MicrosoftDocs/architecture-center/blob/e76b31687407dfe863b9a8ece41eab44c5592b60/docs/patterns/compensating-transaction.md)。
7. [EVAL-009 Recomputable Evaluation Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)。
8. [EVAL-010 Regression Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)。
9. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)与[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。
