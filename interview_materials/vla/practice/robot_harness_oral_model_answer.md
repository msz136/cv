# PROJ-HARNESS-001 + P0 Audit 证据约束下的示范回答

> 状态：`model_answer / evidence_bounded / not_candidate_transcript / unseen`  
> 更新日期：2026-07-21  
> 题目：Robot Harness 解决的核心问题是什么，如何解释 partial raw、proxy 指标、测试漂移与 Codex ownership？

## 1. 30 秒版本

> Robot Harness 解决的不是“模型能不能调用函数”，而是高层工具调用如何在具体机器人、scope 和请求生命周期内安全执行。runtime 需要处理 robot 互斥、取消、超时、补偿和结构化错误；训练侧再把 allowed/forbidden tools、reference trajectory、success criteria 和约束转成 SFT/GRPO-style 数据与 reward。当前证据能支持 schema、runtime、数据和评测合同，但 project sandbox 100% 仍只是结构化协议分数，不能直接等同真实机器人成功率。个人贡献必须按问题定义、约束取舍、数据/reward/eval 设计和逐文件 ownership 分开说明。

## 2. 2 分钟版本

> 普通 function calling 只关注函数名和参数是否生成；机器人 harness 还要把请求绑定到 chat、scope 和 robot，并管理副作用。典型链路是：请求进入后构造 `AgentDeps`，过滤 server/client toolset，获取 robot mutex，再 dispatch/poll；在取消、超时或连接断开时检查 cancel event，尝试 stop/cancel compensation，最后返回结构化结果并释放锁。这样解决的是执行语义、并发和生命周期问题，不是低层视觉 grounding、控制器延迟或接触动力学。
>
> 数据侧我会把 SFT 与 GRPO 分开。SFT 可以使用规范化的 messages/tools/tool_calls；GRPO 只有在存在 allowed/forbidden tools、reference trajectory、success criteria 和可执行 scorer 时才进入 rewardable runner。no-call 或 clarification 样本不能从空 trajectory 直接伪造出来，browser deferred 也不能在没有 runner 时冒充真实执行轨迹。reward 可以包含 tool name/order、参数语义、scope、澄清和取消补偿，并对越权或 forbidden side effect 施加 hard penalty，但这仍然是 proxy，不是物理安全证明。
>
> 评测时我会分开 8B baseline、32B base、32B SFT 和 GRPO checkpoint，不把不同 scorer、不同 n 或不同 holdout 拼成一条因果曲线。project sandbox 的 100% 只说明在该 reference trajectory/schema 环境中通过；safety 多步任务仍弱，browser 还是 deferred，缺真实 controller/effect-sink。因此个人贡献应落在问题定义、约束取舍、数据/reward/eval 设计与结果归因，代码实现和 Codex 协作边界要按 ownership ledger 逐项确认。

## 3. 证据映射

| 结论 | 证据 | 当前强度 |
| --- | --- | --- |
| AgentDeps、toolset、stream/non-stream、cleanup | runtime.py / [Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `local-direct / runtime-contract` |
| robot scope、mutex、cancel、compensation | registry.py 与 ownership ledger | `local-direct / safety-proxy` |
| SFT 62,223 与 GRPO 8,916 路由 | data-preparation scripts、manifests | `local-direct / data-contract` |
| 1,200 tool-restraint mix | restraint build script、manifest | `local-direct / reward-design` |
| 32B ladder、sandbox/safety/browser 分项 | local reports/metrics | `protocol-warning / proxy-only` |
| 个人 ownership | [Robot Harness Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html) | `candidate-confirmation-pending` |

## 4. 高频追问答法

### “为什么 mutex、cancel 和 compensation 必须一起？”

mutex 处理同一 robot 的排他冲突，cancel 处理请求生命周期变化，compensation 处理动作已经发出后的外部副作用。三者分别覆盖 before-dispatch、in-flight 和 after-side-effect；任一缺失都可能留下竞态或悬挂任务。best-effort stop/cancel 也不等于物理停止一定成功。

### “SFT 和 GRPO 数据为什么不能全部混用？”

SFT 只需要可监督的消息/工具调用；GRPO 还需要可执行的 rollout、规则 scorer、成功条件和约束。没有 runner 或 reference trajectory 的样本应跳过、降级为 SFT 或单独做 probe，不能硬塞进在线 RL。

### “sandbox 100% 是不是机器人成功 100%？”

不是。sandbox 主要检查 schema、tool/scope、reference trajectory 和参数约束，没有相机、controller、时延、接触和真实 effect-sink；它最多证明结构化协议层。

### “95.6% 是否证明 GRPO 比 base 提升？”

不能直接证明。必须绑定 run/checkpoint、suite、scorer backend、holdout n、prompt/template、数据 revision 和 raw predictions；当前 base 与 ladder 的 scorer/n 不完全一致，只能各自按协议陈述。

### “哪些代码是你写的？”

按 ownership ledger 逐文件说明亲手修改、协作、工具辅助、仅审查和仅运行；Git author 或 Codex 主要实现记录都不能自动等于独立原创。

## 5. P0 Audit：如何把工程结果讲到可核验边界

### 5.1 30 秒版本

> 我把 Robot Harness 讲成高层机器人工具协议与 post-training 评估项目：runtime 负责 scope、mutex、cancel 和 compensation，数据侧形成 SFT/GRPO/restraint 合同，评估侧再分 run、scorer 和 suite。当前 P0 只部分闭合：聚合算术、5/5 overlap、12/12 locator 可复核，但 raw primary JSONL 是 28/40，四模型 exact support 是 6/10；checkpoint、统一 scorer 和真实 effect-sink 缺失，所以 proxy 100% 不是机器人成功率，37.8→95.6 也不是严格因果 uplift。

### 5.2 2 分钟版本

> 这个项目的核心难点不是“让模型调用一个函数”，而是把高层动作绑定到具体 robot/scope/request 生命周期，并控制副作用。请求进入 `AgentDeps` 后，server/client toolset 按 scope 过滤；排他 robot action 申请 mutex；dispatch/poll 期间检查 cancel 和 timeout；取消或断开时执行 best-effort stop/cancel compensation；最后返回结构化错误并在 finally 释放锁。它覆盖执行语义和并发生命周期，不等于视觉 grounding、控制器时延或接触动力学。
>
> 数据侧不能把所有样本混成机器人轨迹。SFT manifest 是 62,223 条（55,967/3,164/3,092），canonical GRPO 是 8,916 条（8,052/439/425），另有 1,200 条有 no-action 证据的 restraint mix；空 trajectory、没有 runner 的 browser 数据不能伪造为可执行 reward task。reward 可以对 tool name/order、argument semantic、scope、clarification、forbidden side effect 和 cancel compensation 做分解与 hard penalty，但它仍是 proxy。
>
> 评估时我把 8B v3、32B base、32B SFT、GRPO checkpoint-100/200 分开。P0 审计已经复核十套件的聚合算术、5/5 overlap 和 12/12 run locator，但只有 28/40 primary JSONL、6/10 exact common-support；checkpoint binary/hash 为 0/6 本地可核验，scorer/backend 也混用 token-overlap fallback 与 Qwen hidden embedding。于是 `sandbox 100%` 只能说明结构化协议层，`37.8→95.6` 不能写成同 scorer、同 n、同 checkpoint 的因果提升；safety 多步仍弱、browser 仍 deferred，真实 effect-sink/runner 也没有闭合。当前 targeted tests 是 11 passed、1 个 `test-model` 配置漂移失败，我不会报 runtime 全绿。

### 5.3 P0 Evidence Contract

| Claim | 证据 | 等级 | 当前口径 |
| --- | --- | --- | --- |
| scope/mutex/cancel/compensation runtime | `runtime.py`、`registry.py`、ownership/P0 audit | `local-direct / C1-C2` | 可讲执行合同与约束取舍；不讲低层控制 |
| 62,223 SFT / 8,916 GRPO / 1,200 restraint | manifests、prepare/build scripts | `local-direct / C1-C2` | 可讲数据路由；不是全量机器人轨迹 |
| schema-aware reward | reward spec/checker、task-family fields | `local-direct / C2` | 可讲 proxy 设计与 hard penalty；不讲物理安全保证 |
| aggregate arithmetic/overlap/locators | P0 audit：13/13 arithmetic、5/5 overlap、12/12 locator | `local-direct / C2` | 可讲报表/对账正确性 |
| raw predictions | hidden extraction 28/40 primary、6/10 exact support | `partial-raw / C2` | 可讲部分 common-support；禁止称 full raw/paired benchmark |
| checkpoint lineage | 0/6 本地 binary 可 hash/load | `missing / C3` | 禁止称 checkpoint-verified |
| scorer/backend | token-overlap fallback 与 Qwen hidden embedding 混用 | `protocol-warning / C2` | 禁止把 37.8→95.6 当严格因果提升 |
| sandbox 100% | project 130-case structured protocol suite | `proxy-only / C2` | 只能讲 tool/schema/scope proxy |
| real robot/browser success | effect-sink/physical runner/browser runner 缺失 | `unverified / C3` | 禁止宣称真实闭环成功 |
| targeted tests | 11 passed、1 `Unknown model test-model` config drift | `local-direct / P1` | 可讲 residual/test drift，不能称全绿 |
| personal ownership | 13-row ledger；Codex-primary implementation boundary | `candidate-confirmation-pending` | 用 owner/reviewer/implementation 三轴表述 |

### 5.4 高压追问的三档回答

#### “37.8% 到 95.6% 是不是 GRPO 提升？”

**危险回答**：是，GRPO 把 32B 从 37.8% 提升到 95.6%。

**可过回答**：不能直接这么说，因为 n 和 scorer 不完全一致。

**强回答**：

> 目前只能分别陈述各 run 的协议结果。base holdout 是 `n=1333`，GRPO ladder 是 `n=1000`；base 使用 Qwen hidden embedding backend，而 SFT/GRPO ladder 标记为 token-overlap fallback，checkpoint lineage 也没有本地 binary/hash。要说因果提升，必须冻结相同 suite、n、prompt/template、scorer、checkpoint parent 和 raw per-sample predictions，再做 paired diff；当前证据只支持“不同 run 各自的 descriptive metrics”。

#### “sandbox tool/scope 100% 是不是机器人成功 100%？”

**危险回答**：是，工具调用正确就说明机器人能完成任务。

**可过回答**：不是，它只测结构化协议，不包含真实控制。

**强回答**：

> sandbox 的 130 个 case 检查 tool/scope/reference trajectory 和参数约束，没有相机观测、controller latency、接触动力学、effect-sink 或真实 success predicate。它证明的是高层协议在 reference schema 下可通过；要升级为机器人成功，至少要有同 checkpoint 的 simulator/shadow/real runner、逐 episode action/state/contact trace、termination predicate 和 invalid-policy。当前 physical-success eligible claims 是 0。

#### “P0 说 raw 有 28/40，能否算完整 benchmark？”

**危险回答**：28/40 已经覆盖大部分，足以代表十套件。

**可过回答**：只能算 partial raw，不能代表完整 benchmark。

**强回答**：

> 28/40 是 primary JSONL 的恢复数量，6/10 suite 有四模型 exact ID support；它能支持部分 common-support 对账，但余下 raw、统一 scorer、checkpoint identity 和 effect-sink 仍缺。P0 audit 明确把 eligible causal uplift 和 physical-success claims 置为 0，所以我会说“部分 raw artifact 已审计”，不会说“十套件统一 benchmark 已完成”。

#### “Codex 主要实现，你到底贡献了什么？”

**危险回答**：Codex 只是打字，代码都算我写的。

**可过回答**：我负责问题定义、约束和验收，Codex 主要实现工程代码。

**强回答**：

> 我把贡献拆成 owner decision、review/验收和 implementation 三轴。能安全讲的是：我决定把 scope/mutex/cancel/compensation 分层，把无 runner 的空 trajectory 排除出 GRPO，把 no-call restraint 只建立在有文本证据的样本上，并拒绝把 scorer/n 不一致的 37.8→95.6 写成 uplift；Codex 主要展开 runtime、数据脚本和 checker。逐文件谁改、谁 review、谁运行，要按 13-row ledger 和本人确认回答，Git author 不能替代。

#### “测试 11 passed、1 failed，runtime 能说稳定吗？”

**危险回答**：11 个通过，整体稳定，1 个失败可以忽略。

**可过回答**：有一个配置漂移失败，不能说全绿。

**强回答**：

> 这次 targeted tests 是 11 passed、1 failed、2 warnings；失败点是 `test_execute_chat_non_stream_finally_releases_robot_mutex` 使用已不存在的 `test-model`，`build_model_settings()` 在 fake agent 返回前抛 `Unknown model`，同时日志显示 finally release 执行了。它暴露的是 test/config drift，不足以证明完整请求路径全绿；修 fixture 后需要重跑同三组测试，并保留 residual。也不能把 release log 单独升级成 runtime 可靠性结论。

### 5.5 P0 追问树

```text
“你们的结果提升了多少？”
  -> 追问 run/checkpoint/suite/n/scorer/backend/raw predictions
  -> 缺任一项：降级为协议限定的 descriptive metric

“sandbox 100%”
  -> 追问 effect-sink、controller、termination predicate、episode trace
  -> 没有 runner：明确 proxy-only

“十套件都做完了”
  -> 追问 raw JSONL 数量与四模型 exact ID support
  -> 28/40、6/10：明确 partial raw，不称 full benchmark

“你写了全部代码”
  -> 追问具体 diff、review、operator、Codex 边界
  -> 项目页/ledger显示 Codex-primary：改用三轴 ownership 口径

“runtime 稳定”
  -> 追问 targeted test residual 与 config revision
  -> 11/1：报告 test drift，不报全绿
```

## 6. 练习边界

- 这是 model answer，不是候选人的真实 transcript。
- 使用时必须替换“我负责”的部分，并提供具体文件、决策、命令或验收证据。
- 真实口述前保持 `PROJ-HARNESS-001` 为 `unseen`，不创建 `coaching_state.md`。

## References

1. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
2. [Robot Harness Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html)。
3. [PROJ-HARNESS-001..008 Atomic Cards](../questions/proj_robot_harness.html)。
4. [Robot Harness P0 Bundle Audit](../evidence/projects/robot_harness_p0_bundle_audit.html)。
5. [Robot Harness Common-Support Raw Manifest](../evidence/projects/robot_harness_common_support_raw_bundle_manifest.html)。
