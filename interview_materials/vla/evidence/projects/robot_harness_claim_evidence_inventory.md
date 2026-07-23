# Robot Harness Claim–Evidence Inventory（RH-01）

> 状态：`drafted / local_direct_audit / ownership_ledger_drafted / WARN`
> 审查日期：2026-07-17
> 证据截止：2026-07-17
> 项目范围：AceAgent robot harness、PydanticAI runtime、SFT/GRPO 数据路由、schema-aware reward、8B/32B native-tools 评测
> 证据仓库：`C:\Users\mousongzhe\agent`（只读审计；该仓库原有 dirty worktree 未清理）

## 结论先行

本轮审计可以把 Robot Harness 的工程边界、数据构造规则、reward 组件和多组 eval artifact 从项目页自述提升到 `local-direct`。`server/tools/registry.py` 直接显示 PydanticAI toolset、server/client tool 分离、robot scope 过滤、互斥锁、取消检查、轮询超时和 best-effort compensation；`prepare_sft_data.py`、`prepare_grpo_data.py` 与 v2 manifest 直接支持 62,223 条 SFT、8,916 条 canonical GRPO，以及 1,200 条 tool-restraint 合成样本的路由事实。

评测结果必须拆成不同 run/模型/协议：

- 8B v3 full pipeline 的 report 记录 SFT tool-call holdout 95.3%、project sandbox 100%、safety side-effect 44.3%、browser deferred 74.8%、cross-source 85.8%。这是 8B `native_v3_full_grpo_schemaaware_20260617_2022` 的结果，不是 32B 主结果。
- 32B base `native_qwen3vl_32b_schemaaware_full_20260617_2114` 很弱：tool-call holdout 37.8%、project sandbox 59.2%、safety 21.8%、browser 4.2%、cross-source 23.8%。
- 32B SFT 与 GRPO checkpoint-100/200 ladder 的 95.42%/95.6% 等数字有本地 metrics/report 文件，但 SFT 是 `n=1333`，GRPO ladder 是 `n=1000`；ladder 的 run manifest 标记 `token_overlap_fallback`，而早期 32B base 报告使用 Qwen hidden embedding rescore。它们可作为“各自协议下的结果”，不能直接写成同 scorer、同样本量的 base→SFT/GRPO 因果提升。
- project robot sandbox 的 100% tool/scope、92.31% exact、96.92% semantic 仅说明结构化工具协议层；不能推出真实机器人闭环成功率，也没有真实 browser runner 证据。

当前 verdict 保持 `WARN`。ownership ledger 已明确候选人 self-attested owner/reviewer 与 Codex-primary implementation 的双轴边界，并把 13 个文件/决策分层；候选人逐项确认、review history、run/checkpoint lineage、scoring protocol 对齐及完整 raw prediction/effect-sink bundle仍缺。Git commit author 为 `mousongzhe` 只能作为提交线索，不能自动等于个人独立实现。

## 1. 证据标签与判定规则

| 标签 | 含义 | 本项目例子 |
| --- | --- | --- |
| `local-direct` | 当前工作区可读取的 source/config/manifest/report/metrics | registry、数据脚本、v2 manifests、native-tools metrics |
| `local-inference` | 由同一份源码或相邻 artifact 推断，未被单独实验直接证明 | tool accuracy 是闭环前置代理；memory/subagent 是否被模型学会 |
| `report-supported` | committed report 有结论，但底层远端/raw 文件不在本地 | 8B full pipeline report 的完成状态与部分训练摘要 |
| `protocol-limited` | 指标存在，但 scorer、样本量、任务协议或 runner 需要特别说明 | 32B ladder 的 95.6%、browser deferred |
| `ownership-partial` | Git 作者或项目页支持参与线索，但没有逐文件 diff/贡献分类 | `mousongzhe` commit author |
| `unverified` | 缺失 checkpoint、raw log、episode、代码 diff 或无法复算 | 生产机器人成功率、个人独立 ownership |

面试回答使用四级门槛：C0=知道/参与；C1=有本地代码或配置证据；C2=有设计取舍、对照或 bad case；C3=有 immutable run、checkpoint、完整 protocol、raw result 与 ownership。没有 C3 bundle 时，指标只能带协议限定语。

## 2. Resume / 项目页 claim reconciliation

| ID | 当前 claim | 证据 | Verdict | 面试处理 |
| --- | --- | --- | --- | --- |
| `RH-CL-001` | 机器人集群控制需要 task/action schema、robot scope、取消补偿和排他动作 | `server/agent/runtime.py`、`server/tools/registry.py`、`AGENTS.md` | `local-direct` | 可讲 runtime contract；不要把它说成模型已经具备长期 memory/subagent 能力 |
| `RH-CL-002` | 构建 62,223 条 SFT 数据 | `sft_data_manifest.json`：train/dev/test=55,967/3,164/3,092 | `local-direct` | 可报数量，同时说明来源混合与过滤规则 |
| `RH-CL-003` | 构建 8,916 条 canonical GRPO 数据 | `grpo_data_manifest.json`：8,052/439/425 | `local-direct` | 可报数量；强调 browser 默认 deferred、project 空轨迹会跳过 |
| `RH-CL-004` | tool-restraint mix 增加 1,200 条，mixed train=9,252 | `tool_restraint_mix_manifest.json`、生成脚本 | `local-direct` | 可讲 no-call/clarification/refusal 目标；不能说 1,200 条来自真实 runner 轨迹 |
| `RH-CL-005` | reward 约束 tool name/order、参数语义、scope、forbidden side effect、clarification、cancel compensation | `prepare_grpo_data.py` reward spec 与 `schema_aware_reward.py` | `local-direct` | 可解释组件与 hard penalty；先承认权重不是物理成功率 |
| `RH-CL-006` | 8B full pipeline 达到 95.3/100/44.3/74.8/85.8 | `final_pipeline_report.md`、`eval_report.md` | `report-supported / protocol-bounded` | 必须绑定 8B v3 run 与 suite，不能迁移成 32B 成绩 |
| `RH-CL-007` | 32B base→SFT/GRPO 达到 37.8→95.4/95.6 | base report、SFT metrics、GRPO ladder report | `local-direct / protocol-warning` | 分开讲 base、SFT、ckpt100/200；说明 scorer、n、checkpoint 不完全一致 |
| `RH-CL-008` | project robot sandbox 达到 tool/scope 100%，argument exact/semantic 92.3/96.9 | 32B ladder metrics，`n=130` | `local-direct / proxy-only` | 说“结构化工具协议层”，不能说真实机器人成功率 |
| `RH-CL-009` | safety side-effect 已解决 | safety suite：GRPO ckpt100/200 tool accuracy 38.75/37.37，coverage 44.98/43.25 | `FAIL` | 主动讲它仍是 gating weakness，并给出失败样例 |
| `RH-CL-010` | browser 能力已验证 | browser suite 是 deferred/format eval，未执行真实 runner | `FAIL` | 只能讲 schema/format 评测，不讲网页闭环 |
| `RH-CL-011` | 所有 runtime/training/eval 实现均为个人独立完成 | 项目页明确 candidate-owner / Codex-primary implementation；13-row ownership ledger 已建立 | `REJECT-INDEPENDENT / LEDGER-DRAFTED / CONFIRMATION-PENDING` | 使用“我负责约束定义、数据/reward/eval 设计与验收；Codex主要实现，具体review/修改按文件说明” |

## 3. Source inventory（冻结输入）

| Source | 类型 | SHA-256（当前工作区） | 能支持 | 不能支持 |
| --- | --- | --- | --- | --- |
| `server/tools/registry.py` | local evidence | `EF1AFE36697D16F4C2A1392F618444712A87F2F88EE3BDABE409BD2948D24CF1` | tool 注册、过滤、scope、mutex、取消/补偿、结构化错误 | 个人 ownership、模型训练效果 |
| `server/agent/runtime.py` | local evidence | `CEE9148C2987DA7FF6839534EBCFED75B953A8678742AD9442523F96A6A77280` | PydanticAI Agent、deps、chat/scope/robot/cancel、stream/non-stream | 线上流量或真实机器人 success |
| `server/agent/history.py` | local evidence | `CAD470FC6B00470C37636285A3F84732EBFCDEB824612D0439AA65B70B5FC805` | history compaction、action tool history stripping、消息转换 | 训练数据是否覆盖 memory 能力 |
| `remote_training_pipeline_scripts/prepare_sft_data.py` | local evidence | `AF75E07ED5F2483686D0E4DFADFE23D7F50BD31FE3455FCC3BC7354AB5E85589` | SFT schema、过滤、去重、project trajectory、split | 个人设计 ownership、数据原始来源质量 |
| `remote_training_pipeline_scripts/prepare_grpo_data.py` | local evidence | `EAA4136BE5159E894A70D755B93C1BA427CAF6E47E6AB2802B3670E2DDB28250` | rewardable task 字段、任务分流、权重/hard penalty | reward 与真实物理成功的等价性 |
| `remote_training_pipeline_v2/scripts/build_grpo_tool_restraint_mix.py` | local evidence | `7C0983317F1A645F748F1FBB9D6D84B7CA03A415CF3344193F86724F20DF925D` | 1,200 合成 restraint、AppWorld 排除理由 | 合成样本的真实执行覆盖 |
| v2 manifests | local evidence | 见 `pipeline_manifest.json`、`sft_data_manifest.json`、`grpo_data_manifest.json`、`tool_restraint_mix_manifest.json` | 数量、run path、split、来源族、mix | checkpoint binary、raw logs |
| 8B/32B reports | report-supported/local evidence | 见对应报告 SHA | 指标表、失败样例、评测限制 | 未列出的 protocol 或闭环结果 |

## 4. Harness runtime boundary

### 4.1 请求到 Agent 的信息流

`runtime.py` 的 `_prepare_agent` 将 `chat_id`、`scope_type/scope_id`、`robot_id`、`bound_robot_id`、access token、cancel event 放入 `AgentDeps`；根据 `tool_names` 构造 server toolset，并把客户端 deferred tools 作为独立 toolset 加入 PydanticAI `Agent`。非流式走 `agent.run`，流式走 `agent.run_stream_events`；取消时返回 499/abort，并在 finally 释放 robot locks、清理 cancel registry。

`registry.py` 的 server tools 统一使用 `RunContext[AgentDeps]`。机器人互斥任务先申请 `RobotSessionLock`；底层调用前后检查取消状态；导航和订单轮询在 tool 内处理 timeout、取消和 best-effort stop/cancel compensation；异常经 `build_tool_error`/`normalize_tool_result` 结构化返回。`build_server_toolset` 还会按请求 tool 名和 semantic-navigation allowed robot IDs 过滤工具。

这证明了“可执行协议边界”，不证明模型懂得物理动力学、视觉 grounding 或长期 memory。history 中的 action-tool stripping 也更像运行时安全策略，不应写成模型训练目标。

### 4.2 面试可画的最小链路

```text
HTTP/OpenAI or UI request
  -> prompt + scope/robot/cancel context
  -> PydanticAI Agent
  -> server toolset (filtered) + client deferred toolset
  -> mutex / loop guard / tool execution
  -> structured result or cancellation compensation
  -> SSE/OpenAI response + persisted UI message
```

## 5. SFT 数据路由证据

`sft_data_manifest.json` 记录总计 62,223 条：train 55,967、dev 3,164、test 3,092。任务族分布为 core tool call 26,114、browser deferred 18,221、project robot 4,726、general capability 10,000、workflow safety 2,930、general agent SFT 232。

脚本直接支持以下规则：

1. OpenAI-compatible `messages + tools` 规范化为 assistant-side `tool_calls`；按归一化 user goal / expected trajectory 做稳定分组与去重。
2. ToolACE 显式排除；WebLINX/Mind2Web 保留为 browser deferred，但不混入 project robot GRPO。
3. project sandbox 只有 expected trajectory 非空且存在 tool call 才转入 project SFT；scope_type/scope_id 写入 metadata。
4. point/general auxiliary 排除 `<point>/<box>`、coordinate/bbox、低层 action-token 目标，保留高层 VQA 以补通用能力。

因此 62,223 是“规范化后数据集总量”，不是 62,223 条真实机器人轨迹；project robot 只有 4,726 条，且仍需区分训练/评测 split。

## 6. GRPO、reward 与 tool-restraint

### 6.1 canonical GRPO

`grpo_data_manifest.json` 记录 8,916 条：train 8,052、dev 439、test 425。任务族为 clarification_before_action 2,300、no_forbidden_side_effect 3,735、project_robot_task 2,748、cancellation_compensation 120、bound_scope_respected 13。WebLINX/Mind2Web 默认不进入 GRPO runner；project sandbox 空 trajectory 被跳过；行级字段保留 `allowed_tools`、`forbidden_tools`、`reference_trajectory`、`success_criteria`、`policy_constraints`、`minefields`。

### 6.2 reward 组成

可以把规则奖励抽象为：

\[
R=\sum_i w_i c_i+\sum_j p_j\,\mathbf{1}[h_j\text{ 被触发}],
\]

其中 \(c_i\) 是 tool name/order、required coverage、argument semantic、scope、clarification、state success、cancellation compensation 等组件，\(w_i\) 随 task family 变化；\(p_j<0\) 是 forbidden tool、缺失澄清仍执行、scope 忽略、取消不补偿等 hard penalty。该式是对 `reward_spec()` 的结构化解释，不是新的训练实现。

### 6.3 tool-restraint mix

`build_grpo_tool_restraint_mix.py` 从有工具池但无 reference trajectory、且文本证据支持 no-action/clarification/refusal 的候选生成 1,200 条；最终 mixed train=8,052+1,200=9,252。每条样本把“工具可见但不能调用”写入 policy constraint，success criteria 要求不调用工具并澄清或拒绝。AppWorld 空轨迹被排除，因为空轨迹可能表示 runner 缺失，不等于 no-call 标签。

## 7. Run / eval lineage 与指标协议

### 7.1 8B full pipeline（独立基线）

| Run / model | suite（n） | 关键结果 | 证据边界 |
| --- | --- | --- | --- |
| `native_v3_full_grpo_schemaaware_20260617_2022`（8B v3） | SFT holdout 1333 | tool 95.3%、coverage 96.4% | schema_aware_v2，Qwen hidden embedding；report + metrics |
| 同上 | project sandbox 130 | tool/scope/critical/semantic 100% | 协议层，不是物理成功 |
| 同上 | safety 289 | tool 44.3%、coverage 49.1% | 多步 telecom/workflow 仍弱 |
| 同上 | browser 930 | tool 74.8% | deferred/format-only，无真实 browser runner |
| 同上 | cross 1820 | tool 85.8%、coverage 86.5% | source 混合，不能当 robot-only |

### 7.2 32B base、SFT、GRPO ladder

| run | model/checkpoint | suite n | tool accuracy | coverage | argument exact / semantic | scorer / protocol |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `native_qwen3vl_32b_schemaaware_full_20260617_2114` | Qwen3-VL-32B base | holdout 1333 | 37.8% | 39.4% | 22.1% / 27.4% | `schema_aware_v2` + Qwen hidden embedding |
| `native_tool_restraint_32b_sft_20260618_114113` | 32B SFT model | holdout 1333 | 95.42% | 96.25% | 74.57% / 77.87% | `schema_aware_v2` + token-overlap fallback |
| same SFT run | same | project 130 | 100% | 100% | 91.54% / 96.15% | 结构化协议层 |
| `...d_grpo32b_ckpt100` | checkpoint-100 | holdout 1000 | 95.6% | 96.3% | 75.3% / 78.5% | `schema_aware_v2` + token-overlap fallback |
| same | checkpoint-100 | project 130 | 100% | 100% | 92.31% / 96.92% | 结构化协议层 |
| same | checkpoint-100 | safety 289 | 38.75% | 44.98% | 5.19% / 9.69% | safety仍弱 |
| `...d_grpo32b_ckpt200` | checkpoint-200 | holdout 1000 | 95.6% | 96.3% | 75.1% / 78.3% | 同 ladder scorer |
| same | checkpoint-200 | safety 289 | 37.37% | 43.25% | 5.19% / 9.00% | 比 ckpt100 更差 |

注意三层不可比性：

1. base 的 1333 holdout 与 GRPO ladder 的 1000 holdout 不是同一 n；
2. base 早期报告最终使用 Qwen hidden embedding，ladder manifest 明确为 `token_overlap_fallback`；
3. browser 仍是 deferred/format eval，OOD suite 与 D suite 也要分开看。简历若保留 95.4/95.6，必须绑定 run、checkpoint、suite、n 与 scorer。

## 8. 失败模式与真实能力边界

报告给出的安全失败样例是多步 telecom repair：gold 需要 5 个工具步骤，模型只选 1 个工具；这解释了 safety tool accuracy 仍只有 38–44%。browser 失败主要是 uid/target grounding，且没有真实浏览器执行器；project sandbox 的 100% 只能说明 reference trajectory 与 schema 约束在该 sandbox 上可满足。

所以更准确的因果链是：

```text
schema / scope / reward 约束
  -> 降低高层 tool-call 格式、选择和参数错误
  -> 为低层 controller 提供更干净的调用输入（前置代理）
  -/-> 直接推出视觉、控制延迟、接触动力学或真实机器人 success
```

## 9. Ownership boundary

`git log --follow` 显示 `server/tools/registry.py` 与 `server/agent/runtime.py` 的相关提交作者为 `mousongzhe`；`d9db` 对 registry/runtime 有 `+156/-34` 与 `+6/-1` 的 robot integration diff，训练脚本在 `7a8402f Sync remote training artifacts` 中由同一作者一次加入。项目页明确说工程实现和 schema 字段展开主要由 Codex 完成，因此正确口径是“候选账号提交并维护，候选人负责 owner/reviewer 决策，Codex 主要实现”。[Ownership Ledger](robot_harness_ownership_ledger.html)进一步记录了 13 个文件/决策与 8 项确认问题。

2026-07-19 的三组 targeted runtime tests 为 11 passed / 1 failed；失败来自测试使用已不在当前配置中的 `test-model`，mutex finally release 日志仍出现。该结果说明当前存在 test/config drift，不能写 runtime 全绿；修复应放入独立 implementation slice。

当前安全口径：

> 我负责把机器人平台的失败模式抽象成可训练、可验收的 schema / reward / eval 合同，推进 SFT/GRPO 数据路由、scope 与取消补偿约束，并用分层 suite 做结果归因；runtime 工程实现按仓库提交与文件逐项核对，不能把 Git author 自动说成全部代码 ownership。

## 10. 面试安全表述（约 2 分钟）

> 这个项目的核心不是单纯接几个 function，而是把机器人执行的高层语义先变成可检查的 task/action schema。runtime 里通过 robot scope、互斥锁、取消事件和补偿动作保证请求不会越权或留下悬挂任务；训练侧把 OpenAI-compatible tool-call 数据规范化成 SFT，把带 reference trajectory、allowed/forbidden tools 和 success criteria 的任务转成 GRPO reward。数据规模是 62,223 条 SFT 和 8,916 条 canonical GRPO，另有 1,200 条 no-call/clarification restraint mix。评测时我把 8B baseline、32B base、32B SFT、GRPO checkpoint-100/200 分开报告：project robot sandbox 的结构化协议分数很高，但 safety 多步任务仍弱，browser 只是 deferred format eval，所以不能把 tool accuracy 直接等同真实机器人 success。我的贡献边界是问题定义、约束取舍、数据/reward/eval 设计和结果归因，具体代码 ownership 需要按文件 ledger 继续核对。

## 11. 高压追问与回答钩子

| 追问 | 当前可答 | 不能越过的边界 |
| --- | --- | --- |
| 95.6% 是怎么来的？ | 32B GRPO checkpoint-100/200 ladder 的 `sft_tool_call_holdout`，n=1000，schema-aware_v2，token-overlap fallback | 不说与 Qwen-hidden base 同 protocol 的严格提升 |
| 为什么 project sandbox 100% 还不能说机器人成功？ | 它只检查 tool/schema/argument/scope/reference trajectory；没有低层 controller、视觉、时延、接触与物理环境 | 不报真实机器人 success rate |
| reward 是否会被 hack？ | 有 hard penalty、schema-aware critical/semantic 分解；safety 仍弱，报告有多步漏调用样例 | 不说 reward 已彻底解决 |
| browser 是否上线？ | deferred/format eval，真实 runner 未执行 | 不说 browser closed-loop 已验证 |
| 哪些代码是你写的？ | 先按 ownership ledger 分亲手、协作、上游、工具辅助、仅理解 | Git author 不等于独立 ownership |

## 12. P0 缺口与下一步

| 优先级 | 需要补的 artifact | 关闭的 claim |
| --- | --- | --- |
| P0 | 每个 32B run 的 `run_id + repo/config/data/scorer SHA + checkpoint SHA + parent model` | base→SFT→GRPO lineage |
| P0 | 同一 scorer、同一 n、同一 suite 的 base/SFT/GRPO raw predictions 与 summary | 95.4/95.6 的可比性 |
| P0 | project/safety/browser 的 per-sample JSON、episode/runner 状态、失败 trace | proxy 与 closed-loop 边界 |
| P0 | ownership confirmation：逐文件决定/审查/修改/运行/Codex实现/协作边界 | `RH-CL-011`；ledger结构已完成，候选人回答待补 |
| P1 | reward ablation：无 scope/no-arg/no-restraint 与 paired rerun | reward 设计因果性 |
| P1 | 真实 simulator 或 shadow robot runner，side-effect disabled | tool metric→闭环能力的下一层证据 |

第一批 `PROJ-HARNESS-001..008` 题卡和 13-row ownership ledger 已完成，全部保持 `unseen`。下一切片优先做 ownership confirmation drill，或补 common-protocol raw eval；不创建 coaching state，除非候选人真实回答。

## 参考文献（References）

1. [Robot Harness 项目页](../../../01_robot_harness_tool_training.html)，用于核对简历叙事与原有问题树。
2. `C:\Users\mousongzhe\agent\AGENTS.md`，PydanticAI、tool registry、取消/补偿约束。
3. `C:\Users\mousongzhe\agent\server\tools\registry.py`、`server\agent\runtime.py`、`server\agent\history.py`。
4. `C:\Users\mousongzhe\agent\remote_training_pipeline_scripts\prepare_sft_data.py`、`prepare_grpo_data.py`。
5. `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\scripts\build_grpo_tool_restraint_mix.py`。
6. v2 manifests：`manifests\pipeline_manifest.json`、`sft_data_manifest.json`、`grpo_data_manifest.json`、`tool_restraint_mix_manifest.json`、`latest_32b_eval.json`、`latest_32b_eval_ladder.json`。
7. `reports\final_pipeline_report.md`、`reports\eval_report.md`、`reports\32b_native_tools_eval_report.md`。
8. `reports\eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_comparison.md`。
9. `C:\Users\mousongzhe\agent\git log --follow` 输出：仅作 authorship 线索，不作 ownership 证明。
10. [Robot Harness Ownership Ledger](robot_harness_ownership_ledger.html)；canonical [Markdown](robot_harness_ownership_ledger.md)，review [JSON](robot_harness_ownership_ledger.review.json)。
