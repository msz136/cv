# Robot Harness Ownership Ledger：Owner 决策、Codex 实现与结果归属

> 状态：`ownership_audited / role_self_attested / codex_primary_implementation / git_process_partial / WARN`
> 审查日期：2026-07-19
> 证据截止：2026-07-19
> 项目范围：`C:\Users\mousongzhe\agent`、Robot Harness 项目页、简历、SFT/GRPO/reward/eval artifacts。
> 结论先行：该项目已经有一条明确且可信的自述边界——候选人以 owner 方式负责问题定义、机器人约束拆解、数据分流、训练/eval 口径、结果判断与验收；Codex 主要负责 harness、schema、训练/评测脚本和字段展开。Git 提供了 initial import、sandbox eval、robot platform integration 与 remote training artifact sync 的增量记录，但 commit author 不改变上述工具辅助事实。本页把 owner/reviewer、主要实现者、运行者和结果归属分开；62,223/8,916/1,200 的数据事实可核，95.4/95.6 与 sandbox 100% 仍受 scorer、n、checkpoint、proxy 和真实闭环边界约束。

## 1. 问题（Question）

面试官问“工程主要由 Codex 完成，那你在 Robot Harness 中到底贡献了什么？”时，回答不能停在“想法是我的”，也不能反过来把所有代码认成手写。需要逐层回答：

1. 谁定义机器人平台的失败问题与产品目标？
2. 谁决定哪些约束进入 runtime、schema、SFT、GRPO reward 和 holdout？
3. Codex 具体实现了哪些文件、字段和评测流程？
4. 候选人如何审查、修改、运行、验收和否决工具生成内容？
5. 训练 checkpoint、scorer、metrics 与真实 robot outcome 分别能归谁、支持什么？

本页只把已有证据组织成 ownership contract；不会把自述自动变成独立验证，也不会把 Git author、report 或 tool metric 当作物理闭环证明。

## 2. Role Fit 与 JD 能力映射

当前未提供具体 JD，按 VLA / Embodied Agent / Multimodal Post-training / Evaluation Platform 岗位映射。

| 岗位能力 | 当前可核证据 | Candidate role | Codex / 工具角色 | 当前面试策略 |
| --- | --- | --- | --- | --- |
| 问题抽象与系统边界 | project page 明确 scope、mutex、cancel/compensation、tool schema 与真实控制边界 | `self-attested primary owner` | 展开工程结构与字段 | 重点讲为什么这些失败值得训练，不能只背代码 |
| 数据工程与 post-training | SFT/GRPO scripts、62,223/8,916 manifests、1,200 restraint mix | 定义分流、约束与验收；角色为自述 | 主要实现脚本/字段 | 用样本准入和拒绝条件证明算法判断 |
| Reward / RL 设计 | schema-aware reward、hard penalties、safety bad case | 决定 reward 目标与取舍；自述 | 主要实现 checker/eval | 主动承认 proxy/hacking/long-horizon 缺口 |
| Runtime / robot integration | PydanticAI runtime、registry、sandbox、robot integration diff | owner/reviewer；具体修改范围待确认 | 主要工程实现 | 不声称手写全部 runtime；能解释关键路径和验收 |
| 实验与评估 | 8B/32B reports、metrics、D/OOD ladder | 设计口径、判断结果和 bad case；自述 | 生成/实现 evaluation pipeline | 每个数字绑定 run/suite/n/scorer；不拼接不存在的曲线 |
| 真实部署能力 | robot tool integration 与 simulator hooks | 平台目标/验收可讲 | 实现细节工具辅助 | tool protocol 只是真实执行的前置层，不是 success rate |

## 3. 双轴 Ownership Contract

### 3.1 贡献向量

把项目贡献拆成五个互不替代的分量：

\[
C=(P,D,I,V,R),
\]

其中 `P` 是问题定义（problem framing），`D` 是约束与实验设计（design），`I` 是工程实现（implementation），`V` 是审查、运行和验收（verification），`R` 是结果/指标 ownership。当前材料对候选人的 `P/D/V` 有明确 self-attestation，对 `I` 明确标为 Codex-primary，对 `R` 仅有 protocol-bounded 支持。直觉上，“owner”不等于“手写所有代码”，而“Codex 实现”也不等于候选人没有贡献；强回答必须证明候选人具体做过哪些取舍、审查和失败判断。实现映射是项目页、Git diff、源码、manifest、测试、run/scorer 与候选人确认表。

### 3.2 状态词汇

| 状态 | 含义 | 允许表述 |
| --- | --- | --- |
| `candidate-self-attested` | 项目页/简历明确声明候选人角色 | “候选人自述负责……” |
| `codex-primary-implementation` | 项目页明确工程实现/字段展开主要由 Codex 完成 | “我定义和验收，Codex 落地实现” |
| `git-diff-supported` | 有独立 commit 与 before/after diff | “候选账号提交了这次集成差异” |
| `local-artifact` | code/config/manifest/metrics 存在 | “工作区包含并可复核……” |
| `execution-supported` | 有命令、run manifest、checkpoint/load 或测试 | “该路径在指定环境被运行/验收” |
| `result-protocol-bounded` | 指标存在但 protocol/scorer/raw/closed-loop 受限 | “在该 run/suite/n/scorer 下……” |
| `role-confirmed` | 候选人逐项确认 owner/reviewer/operator/tool boundary | 才能用精确第一人称动作 |

## 4. Git、artifact 与测试冻结

### 4.1 Git 过程证据

| Commit | 关键变化 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `bd88445f9e6163c26985840eb2a94eacdcc4bdc1` | Initial AceAgent import；registry 1989 行、runtime 481 行、history 646 行首次进入 | 初始代码快照与候选账号提交 | 每行手写 ownership |
| `0d6606ac68c4d45bfff23f1a6180b630f8559349` | agent sandbox RL rollout eval：sandbox `+859/-46`，tests `+23/-2` | sandbox/eval 有可观察增量 | 具体哪些行由候选人还是 Codex 编写 |
| `d9dbd0025cd317b6a747e5d6fb8dd203b238b195` | robot integration：registry `+156/-34`、runtime `+6/-1` | robot/backend/semantic integration 的真实 diff | candidate 独立代码作者身份 |
| `7a8402ff8cb45c579d324490175aa711cd571b18` | remote training sync；SFT/GRPO/restraint/reward 四个关键脚本新增 1,585 行 | 训练资产在该 commit 进入仓库 | 远端生成过程、运行者、checkpoint ownership |
| `b5feead...` / `b4ed713...` | archive remote process artifacts / training reports | 后续归档行为 | raw remote state 天然可信或完整 |

所有这些 commit 的 author/committer 均为 `mousongzhe`。项目页又明确 Codex 是主要工程实现者，因此正确解释是“候选账号提交并维护了由候选人定义、Codex 主要实现的工程资产”，而不是“Git author 推翻工具辅助边界”。

### 4.2 当前 worktree 与定向测试

`C:\Users\mousongzhe\agent` 当前已有用户变化：robot state、ROS2 sim 脚本、C++ runtime node 以及未跟踪报告目录；本轮未修改这些文件。

2026-07-19 只读运行：

```text
python -m pytest server/tests/test_robot_mutex.py
                 server/tests/test_cancel_current_session.py
                 server/tests/test_acerobotics_sim_backend.py -q
result: 11 passed, 1 failed, 2 warnings
```

失败发生在 `test_execute_chat_non_stream_finally_releases_robot_mutex`：测试使用的 `test-model` 不再存在于当前 `llm_configs`，`build_model_settings()` 在 fake agent 返回前抛出 `Unknown model`；日志同时显示 robot mutex 的 finally release 已执行。这是当前 test/config drift，不能写成 runtime 全绿，也不能仅凭 release log 宣称完整请求路径正确。本轮是证据审计，不修复该测试。

## 5. Per-file / per-decision ownership matrix

| ID | 文件 / 决策 | Local / Git 证据 | Candidate role | Codex / 其他角色 | Verdict | 当前安全口径 |
| --- | --- | --- | --- | --- | --- | --- |
| `RH-OWN-001` | 把 robot scope、mutex、cancel/compensation 转成可训练问题 | 项目页与 inventory 反复声明该 framing | `primary owner / self-attested` | Codex 协助结构化 | `role-clear / independently-unverified` | “我负责定义问题、约束与验收口径” |
| `RH-OWN-002` | `server/tools/registry.py` | 2111 行，SHA `ef1afe...24cf1`；initial import 后 robot commit `+156/-34` | owner/reviewer；具体函数待确认 | 项目页声明工程主要由 Codex 完成 | `git-diff + codex-primary` | “我定义并验收 tool/scope/cancel contract；Codex 主要实现 registry” |
| `RH-OWN-003` | `server/agent/runtime.py` | 486 行，SHA `cee914...77280`；robot commit `+6/-1` | runtime contract owner/reviewer | Codex-primary implementation | `local-direct / role-scope-pending` | “负责迁移目标与兼容验收，不说手写全部 runtime” |
| `RH-OWN-004` | `server/agent/history.py` | 646 行，SHA `cad470...805fc`；只有 initial import | 理解/验收范围待确认 | initial/Codex provenance未细分 | `snapshot-only` | “工作区包含 history 策略；不自动认领设计” |
| `RH-OWN-005` | `server/agent/sandbox.py` / rollout eval | 2318 行，SHA `57460f...3292c`；`0d660` 有 `+859/-46` | sandbox 目标、case 和验收 self-attested | Codex-primary engineering | `git-diff / process-partial` | “以 owner 方式推进 sandbox eval，代码主要由 Codex 落地” |
| `RH-OWN-006` | `prepare_sft_data.py` | 377 行，SHA `af75e0...5589`；`7a840` 一次新增 | 数据准入/过滤/split 规则 owner self-attested | Codex/remote pipeline 实现 | `artifact-direct / author-tool-assisted` | “我决定 SFT 分流与验收；脚本由 Codex 主要实现” |
| `RH-OWN-007` | `prepare_grpo_data.py` | 253 行，SHA `eaa413...8250`；`7a840` 一次新增 | rewardable-task 准入 owner self-attested | Codex implementation | `artifact-direct / role-clear-high-level` | “我定义哪些样本能进入 GRPO及原因” |
| `RH-OWN-008` | restraint mix + schema-aware reward | 271/684 行；SHA `7c0983...925d` / `a402d2...5e1a`；同一 sync commit | no-call、scope、hard-penalty 取舍 self-attested | Codex 实现字段/checker/eval | `design-self-attested / code-tool-assisted` | “我负责 reward 目标和 failure gate，Codex落地 checker” |
| `RH-OWN-009` | SFT/GRPO/mix manifests | totals 62,223 / 8,916 / 1,200；生成时间和 source/task family 可读 | 口径选择与 acceptance owner self-attested | remote scripts生成，Codex实现 | `count-verified / generation-role-partial` | “我负责数据口径和验收；数量由 manifest 支持” |
| `RH-OWN-010` | 8B/32B training / checkpoint | reports 与 run manifests 可读；model paths remote | training strategy/results interpretation self-attested | remote launcher/implementation tool-assisted；operator待确认 | `report/run-supported / checkpoint-owner-open` | “在各自 run 中评估；不说所有 checkpoint 本地可加载或独立训练” |
| `RH-OWN-011` | native-tools / D+OOD eval | metrics、failure/change samples、scoring backend 与 run manifests direct | eval protocol、验收与归因 self-attested | Codex 主要实现 scorer/report | `local-direct / raw-full-predictions-open` | “我设计分层 suite 并解释结果；代码由 Codex主要实现” |
| `RH-OWN-012` | 37.8→95.4/95.6、sandbox 100% | base/SFT n=1333，GRPO n=1000；semantic backend不同；proxy-only | result selection/interpretation self-attested | report generation tool-assisted | `C3-protocol-warning` | 每个数字绑定 run/n/scorer，不写真实 robot success或严格因果 |
| `RH-OWN-013` | PydanticAI / open datasets / Qwen | requirements 与数据来源可定位 | 采用、适配、取舍 | public upstream | `upstream-only` | 不把框架、模型和开源数据原创算作个人成果 |

## 6. Claim → ownership reconciliation

| Claim | 等级 | 当前证据 | 处理 |
| --- | ---: | --- | --- |
| “设计 robot task harness 调度与表征框架” | C2 | candidate self-attested framing + runtime/local diff；工程 Codex-primary | 可写“设计约束框架并负责验收”；不写手写全部工程 |
| “构建 62,223 SFT / 8,916 GRPO” | C1/C2 | scripts/manifests direct；candidate owns routing criteria，Codex owns most implementation | 数量可写；必须解释混合数据不是 robot trajectories |
| “设计 schema-aware reward” | C2 | checker/source direct + candidate self-attested reward choices；无 matched ablation | 可写“设计 reward 口径/约束”；不写已证明因果 uplift |
| “SFT/GRPO 后 37.8→95.4/95.6” | C3 | base/SFT 1333、GRPO 1000；backend/protocol不同，full raw predictions缺 | 改为“各自保存的 holdout artifacts 为……”；严格 uplift 需统一重算 |
| “sandbox tool/scope 100%” | C3/proxy | n=130 structured-protocol suite | 可写 proxy metric；禁止真实 robot 100% |
| “safety side effect 已解决” | C3 | safety 仍约 37–44%，直接反证 | 禁写；作为高价值 bad case |
| “browser 能力已验证” | C3 | deferred/format only，无 runner | 禁写 closed-loop；只说 schema/format eval |
| “所有代码都是我独立完成” | C2/C3 | 与 project page 的 Codex-primary 说明冲突 | 明确拒绝；用 owner/reviewer + tool-assisted implementation 口径 |

## 7. Production Gap

| 当前做法 | 大厂追问 | 缺口 | 最小补证据 | 安全表达 |
| --- | --- | ---: | --- | --- |
| owner + Codex 实现 | 你实际做了哪些 review/修改？ | P0 | prompt/decision log、rejected alternatives、manual diff、review checklist | “我负责定义和验收，Codex主要实现” |
| commit author | 哪些行是你写的？ | P0 | 逐文件 role ledger + candidate confirmation | “提交者不是独立代码作者证明” |
| 数据 totals | 多少是真实机器人轨迹？ | P0 | source/license/robot subset/duplicate ledger | “62k 是混合 SFT；project robot 4,726” |
| schema-aware reward | 如何防 reward hacking？ | P0 | paired adversarial suite + no-scope/no-restraint ablation | “规则可解释但覆盖有限，safety仍弱” |
| 32B metrics | base/SFT/GRPO 是否同 protocol？ | P0 | common-support raw rerun，同 n/scorer/template | “当前为各自 protocol 下的结果” |
| project sandbox | 与真实执行相关吗？ | P0 | simulator/shadow effect-sink episodes | “高层协议 proxy，不是闭环 success” |
| browser deferred | 有没有真实网页执行？ | P1 | runner、trace、side-effect-disabled test | “只完成 format/schema eval” |
| 当前 test drift | runtime 是否全绿？ | P1 | 修复 model fixture 后同三组 tests rerun | “11 pass/1 config-drift failure” |

## 8. Question Tree 与回答分层

### 8.1 主追问树

```text
工程主要由 Codex 完成，你贡献了什么？
  ├─ 回答“问题定义”
  │    ├─ 哪个真实 failure 让你加入 scope/cancel/restraint？
  │    ├─ 哪些约束进 schema、reward、eval，为什么？
  │    └─ Codex 给出错误实现时你否决过什么？
  ├─ 回答“数据设计”
  │    ├─ SFT 与 GRPO 的准入/拒绝条件？
  │    ├─ 62k 中 robot subset 多大？如何防泄漏？
  │    └─ 1,200 no-call 为什么不是空轨迹伪标签？
  ├─ 回答“结果验收”
  │    ├─ base/SFT/GRPO 的 n、scorer、checkpoint是否一致？
  │    ├─ safety 为什么仍差？
  │    └─ sandbox 100% 为何不是 robot success？
  └─ 回答“我写了全部代码”
       └─ 与项目页 Codex-primary 声明冲突，直接进入真实性风险
```

### 8.2 高压题：Codex 写了代码，你是不是只提需求？

- **危险回答**：想法都是我的，Codex 只是打字，所以代码也算我写的。
- **可过回答**：我把 Codex 当实现加速器。我的责任是定义机器人高层失败、决定 schema/SFT/GRPO/reward/eval 的分层、审查生成代码和验收指标；工程实现与字段展开主要由 Codex 完成，我不会认领手写全部代码。
- **强回答（需候选人确认细节）**：我能给出三个具体 owner 决策：第一，project 空轨迹不进入 GRPO，避免无 runner 被误标为 no-call；第二，scope/cancel/compensation 分别落到 runtime 与 reward，而不是只用格式 reward；第三，32B ladder 不能直接把 37.8→95.6 当同协议 uplift，因为 n 和 semantic backend 不同。Codex 落地脚本，我逐项审查 schema、manifest、failure samples 和验收门；例如当前 targeted tests 仍有一个 `test-model` 配置漂移，我不会说 runtime 全绿。

强回答中的“三个具体决策”和 review 行为仍需候选人确认；不能因为本页写出示例就视为真实口述证据。

## 9. SP/SSP 证据就绪度

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.5 | Embodied Agent、tool post-training、runtime/eval 与目标岗位高度相关 |
| 机制深度 | 4.0 | schema/runtime/SFT/GRPO/reward/scorer 可机制级解释 |
| 工程闭环 | 4.0 | runtime、数据、reward、run、metrics、failure samples 齐；真实 effect-sink 缺 |
| 指标可信度 | 3.0 | local metrics 与 run manifest 丰富；common scorer/n、checkpoint/raw prediction bundle 未闭合 |
| Ownership 清晰度 | 3.0 | candidate-owner / Codex-primary 边界已明确；逐文件确认与 review history 仍缺 |
| 抗追问能力 | 3.5 | proxy/safety/browser/scorer 边界清楚；当前简历强 uplift 仍需口径防线 |
| 合计 | **22.0 / 30** | 这是证据就绪度，不是候选人能力评分 |

一票否决项：隐瞒 Codex-primary engineering；把 tool metric 写成真实 robot success；把 safety 说成解决；把 browser deferred 说成上线；把 scorer/n 不同的数字称严格因果提升。

## 10. 候选人确认表

下一次 ownership drill 逐项回答“我决定 / 我审查 / 我修改 / Codex 实现 / 协作 / 不确定”，并给一个具体例子：

1. 哪个真实机器人/平台 failure 由你首先抽象为 scope、mutex 或 cancel/compensation？
2. `d9db` robot integration 中哪些行为是你明确要求和验收的？
3. SFT 脚本的 ToolACE 排除、project trajectory 准入和 group split 是谁决定的？
4. GRPO 的五类 task family、hard penalties 和 browser disabled 是谁决定的？
5. 1,200 restraint mix 的候选/重复策略是你选择、Codex建议还是远端复原？
6. 你亲自运行或查看过哪些 8B/32B checkpoint、日志和 metrics？
7. 你否决或修正过 Codex 哪个错误 schema、reward、scorer 或结论？
8. 简历中 37.8→95.4/95.6 与 sandbox 100% 的最终口径是谁确认的？

这些问题没有真实回答前，不创建 coaching state；ledger 状态保持 `candidate-confirmation-pending`。

## 11. 分阶段补强计划

| 时间 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 回答 8 项确认题；为 owner 决策各给一个 rejected alternative/bad case | 13-row ledger 的 candidate/Codex/operator/reviewer 字段闭合 | `待确认` |
| 1 天 | 修复 test-model fixture 后 rerun；导出 review/checklist 与关键 prompt/decision log | targeted tests 全绿或有明确 residual，工具辅助过程可讲 | `待补做` |
| 3 天 | 同 n/scorer/template 重算 base/SFT/ckpt100/200，保留 full per-sample predictions | 37.8/95.x 进入 common-support paired table | `待补做` |
| 1 周 | 做 no-scope/no-arg/no-restraint ablation + simulator/shadow effect-sink | reward 因果与 proxy→execution gap 得到直接证据 | `待补做` |

## 12. Output Pack

### 12.1 简历 bullet 三档

- **保守版（当前证据）**：以 owner 方式定义机器人工具协议训练问题，负责 scope、取消补偿、数据分流、schema-aware reward 与分层评估口径；借助 Codex 完成 runtime 和 SFT/GRPO 工程实现，构建 62,223 条 SFT、8,916 条 canonical GRPO 及 1,200 条 restraint 样本。
- **标准版（完成候选人确认与 common-support 口径后）**：主导 Robot Harness 的约束建模与 post-training 验收，将 robot scope、forbidden side effect、clarification 和 cancel/compensation 映射为 SFT/GRPO schema 与 rule-based reward，并通过统一 holdout 和 safety suites 验证工具协议能力。
- **偏强版（必须补统一 raw eval 与 effect-sink）**：建立从 runtime failure taxonomy、可验证 reward 到 simulator/shadow rollout 的端到端训练评估闭环，量化各 reward component 对 tool protocol 与真实执行的因果贡献。当前禁止写成已完成。

### 12.2 两分钟项目叙事

> 这个项目是我以 owner 方式推进、Codex 主要负责工程实现的机器人工具调用训练项目。我的核心工作不是声称手写所有代码，而是决定什么问题值得训练、如何转成可验证约束以及怎样验收。机器人执行相比普通 function calling 多了 robot scope、排他动作、取消补偿和真实副作用，所以我把这些约束分层：runtime 负责执行前后的 hard boundary，SFT 负责稳定工具协议，GRPO 只接收有 allowed/forbidden tools、reference trajectory、success criteria 或 minefields 的可判分任务；另加 no-call/clarification restraint，避免模型看到工具就调用。
>
> 数据侧形成 62,223 条混合 SFT、8,916 条 canonical GRPO 和 1,200 条 restraint；这些不是全部机器人轨迹。评估侧我把 8B pilot、32B base、32B SFT 与 GRPO checkpoint 分开，并主动保留两条限制：base/SFT/GRPO 的 n 和 semantic backend 不完全一致，因此 37.8→95.x 不是已经闭合的严格因果对照；project sandbox 的高分只证明 tool/schema/scope 层，safety 多步任务仍弱、browser 也只是 deferred eval。Codex 完成主要脚本和字段展开，我负责约束取舍、review、结果判断和验收；具体文件按 ownership ledger 逐项说明。

### 12.3 面试前 6 题

1. scope、mutex、cancel 和 compensation 分别解决什么失败，哪些不能互相替代？
2. 62,223 条 SFT 中真实 project robot 子集有多少，为什么不能混称机器人轨迹？
3. 哪些样本必须进 SFT、能进 GRPO、只能做 eval 或应该 drop？
4. tool-restraint 如何防止“全拒绝”与空轨迹伪标签？
5. 37.8→95.4/95.6 的 n、scorer、checkpoint 和 common-support 缺口是什么？
6. Codex 实现了什么，你做过哪些决定、审查、修改和验收？

## 13. Ownership 审计伪代码

```python
def phrase_harness_claim(claim, ledger):
    # Separate owner decisions from primary code implementation.
    role = ledger.role_vector(claim)  # P, D, I, V, R

    # Git author proves submission identity, not handwritten implementation.
    if role.implementation == "codex_primary":
        implementation_phrase = "借助 Codex 完成工程实现"
    else:
        implementation_phrase = ledger.confirmed_implementation_phrase(claim)

    # Numeric claims require a common protocol and full result lineage.
    if claim.level == "C3" and not ledger.common_protocol_raw_bundle(claim):
        return implementation_phrase + "；指标按 run/suite/n/scorer 限定"

    # Physical success additionally needs an effect-sink episode bundle.
    if claim.kind == "robot_success" and not ledger.effect_sink_verified(claim):
        return "只表述为高层工具协议 proxy"

    return ledger.exact_scoped_phrase(claim, implementation_phrase)
```

该伪代码是面试真实性 gate，不是 AceAgent/PydanticAI 的运行时代码。它把 candidate owner、Codex implementation、protocol-bounded result 与 physical effect-sink 分开。

## 参考文献（References）

1. [Robot Harness Claim–Evidence Inventory](robot_harness_claim_evidence_inventory.html)，11 条 claim、runtime/data/reward/eval 边界。
2. [Robot Harness Project Cards](../../questions/proj_robot_harness.html)，8 张题卡，全部 unseen。
3. [Robot Harness 项目页](../../../01_robot_harness_tool_training.html)，candidate-owner / Codex-primary implementation 自述与面试口径。
4. Local repo `C:\Users\mousongzhe\agent`：commits `bd88445f`、`0d6606ac`、`d9dbd002`、`7a8402ff`。
5. `server/tools/registry.py` SHA-256 `ef1afe36697d16f4c2a1392f618444712a87f2f88ee3bdabe409bd2948d24cf1`；`server/agent/runtime.py` SHA-256 `cee9148c2987da7ff6839534ebcfed75b953a8678742ad9442523f96a6a77280`。
6. `server/agent/sandbox.py` SHA-256 `57460faa62d3b7e5b51dd4b0af7dc03c62da48916708fbce44eac00b4de3292c`。
7. `prepare_sft_data.py` SHA-256 `af75e07ed5f2483686d0e4dfadfe23d7f50bd31fe3455fcc3bc7354ab5e85589`；`prepare_grpo_data.py` SHA-256 `eaa4136be5159e894a70d755b93c1ba427caf6e47e6ab2802b3670e2ddb28250`。
8. `build_grpo_tool_restraint_mix.py` SHA-256 `7c0983317f1a645f748f1fbb9d6d84b7ca03a415cf3344193f86724f20df925d`；`schema_aware_reward.py` SHA-256 `a402d22299c1af0bab2d08e83e4389206882559294c3b1f55f9df55ac0f85e1a`。
9. SFT/GRPO/restraint manifests：SHA-256 `6700f4...72395`、`ae249f...c795`、`2d0821...b14ee`。
10. 32B base report SHA-256 `c8a00d531f90ad952f52dae563d276f0c73b88e189bc00f00840e72d553c8145`；D/OOD comparison SHA-256 `ab19733ad451af08d1b85bd3f41fe0051f76aa0e71f74580ce553b5c30465085`。
11. [Optimized Resume](../../../../output/mousongzhe_resume_optimized.html) 与 [Resume Restructure Plan](../../../../output/resume_restructure_plan.md)，当前投递 claim。
