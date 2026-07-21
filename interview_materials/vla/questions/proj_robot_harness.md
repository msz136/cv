# PROJ-HARNESS：Robot Harness 项目原子题卡（Direct-Evidence Batch 1）

> 状态：`drafted / cards_8_of_8 / WARN`  
> 更新日期：2026-07-17  
> 当前题数：8 / 8  
> 覆盖范围：`PROJ-HARNESS-001..008`  
> 难度：L2 4 题 / L3 4 题  
> 优先级：P0 7 题 / P1 1 题  
> 练习状态：全部 `unseen`  
> 使用方式：先闭卷回答 30 秒，再展开代码路径、指标协议和反例；未真实口述前不得改为 `pass/strong`。

## A. Harness runtime 与执行安全

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-HARNESS-001</b> · Robot Harness 解决的核心问题是什么，为什么不只是普通 function calling？</summary>

**面试意图**：判断你能否把平台工程表述成机器人可执行语义问题，又不夸成低层控制成果。

**30 秒回答**：它解决的不是“能否调用函数”，而是同一机器人上的 scope、排他动作、取消补偿和可恢复执行。harness 把约束写进 tool schema/runtime，并沉淀成 SFT/GRPO 与 eval 合同；它仍不等价于视觉或低层控制。

**机制展开（约 2 分钟）**：普通 tool call 只关心名字和参数；机器人执行还要绑定 robot/chat/scope，防止同一机器人同时导航与执行冲突动作，并在用户取消或连接中断时停止任务、释放锁、保留结构化状态。训练侧再把 allowed/forbidden tools、trajectory、success criteria 与 scope 变成监督和 reward。这个链路降低上层动作语义错误，但没有覆盖相机 grounding、控制器时延和接触动力学。

**诊断 / 证据**：从一个导航请求追踪 `AgentDeps → filtered toolset → mutex → dispatch/poll → cancel/compensation → structured result`；再检查同 robot 并发、跨 robot 并发、取消前后和工具异常四类 trace。当前源码证明 contract，真实机器人 success 仍缺 runner/episode 证据。

**项目挂钩**：个人贡献应落在问题定义、约束取舍、数据/reward/eval 设计和验收；不能只说“搭了 Agent 平台”。

**追问树**：scope 与 robotId 有什么区别？为什么要排他动作？哪些约束在 runtime，哪些进入训练？

**危险答案**：说“tool accuracy 高就证明机器人控制成功”，或把 memory/subagent runtime 抽象说成模型已经学会的能力。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-HARNESS-002</b> · PydanticAI runtime 从请求到工具执行的主链路是什么？</summary>

**面试意图**：确认你能从代码解释 context、toolset、流式协议与资源清理，而不是只背框架名。

**30 秒回答**：`_prepare_agent` 将 chat/scope/robot/token/cancel 写入 `AgentDeps`，组装 server/client toolset 后交给 PydanticAI。非流式 `run`，流式 `run_stream_events`；结束时释放 robot lock 与 cancel 状态。

**机制展开（约 2 分钟）**：prompt context 先解析 bound robot 与非 system history；history 会压缩重复 turn，并剥离不应被模型复用的 action-tool 记录。server tools 由 registry 提供，client tools 以 external/deferred schema 加入；重名时 server tool 优先，以保留取消/补偿保证。运行结果转换为 OpenAI 或 UI SSE，并持久化 UI parts；finally 统一释放 request 关联的 robot locks。

**诊断 / 证据**：打印 `AgentDeps`、最终 tool name 集合、server/client 冲突项、stream event 与 cleanup trace；验证非流式、OpenAI SSE、UI SSE 和客户端断开四条路径。源码直接支持 call graph，线上吞吐和稳定性没有由这些文件自动证明。

**项目挂钩**：可讲“把 PydanticAI 作为统一执行入口并保持既有协议兼容”；不要把框架迁移本身称为算法创新。

**追问树**：为什么 server tool 优先？deferred tool 如何返回？action history 为什么要 strip？cancel event 放在哪里？

**危险答案**：把 client deferred tool 当成服务端已经执行，或说 history stripping 等于模型具备长期记忆。

**来源**：[1][3][4][5]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-HARNESS-003</b> · mutex、取消检查和 compensation 为什么必须同时存在？</summary>

**面试意图**：检查你是否理解机器人副作用工具的并发、超时和失败语义。

**30 秒回答**：执行类 tool 先按 robot/request/chat 申请互斥锁，调用前后检查 cancel；导航和订单轮询在 tool 内处理超时，取消时 best-effort stop/cancel，并返回结构化 error。它防止并发冲突和悬挂副作用，但不保证补偿必然成功。

**机制展开（约 2 分钟）**：mutex 解决“同一 robot 两个排他任务”冲突；cancel event/registry 解决请求生命周期变化；compensation 处理动作已经发出后的外部副作用。导航 dispatch 后若取消，tool 会尝试 stop navigation；订单轮询取消则尝试 cancel order；协程被取消时还会安排 detached best-effort cleanup。三者缺一都会出现竞态、假完成或后台任务继续执行。

**诊断 / 证据**：做取消时序矩阵：dispatch 前、dispatch 后、poll sleep 前后、timeout、producer task cancellation；记录 lock、task/order id、stop/cancel result 和最终 error payload。补偿失败必须显式返回，不能吞掉异常后说系统安全。

**项目挂钩**：这类设计适合回答“机器人 Agent 与普通聊天 Agent 的系统差异”，也是取消补偿 reward 样本的 runtime 来源。

**追问树**：为什么是 best-effort？锁何时释放？跨 robot 是否可并发？超时后如何避免外部任务继续？

**危险答案**：说“收到 cancel 就一定停止物理机器人”，或用 mutex 代替外部系统的幂等和状态核验。

**来源**：[1][3][4]　**练习状态**：unseen

</details>

## B. SFT / GRPO 数据与 reward

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-HARNESS-004</b> · 62,223 条 SFT 数据是怎样构造的，哪些口径不能混淆？</summary>

**面试意图**：看你能否讲清 schema、过滤、分组、来源构成，而不把混合数据说成机器人轨迹。

**30 秒回答**：62,223 是规范化混合 SFT 样本，不是机器人轨迹数。脚本统一 messages/tools/tool_calls，按 goal+trajectory 去重；project 只收非空 trajectory，ToolACE 排除，browser 保持 deferred，point/box/action-token auxiliary 过滤。

**机制展开（约 2 分钟）**：manifest 为 train/dev/test 55,967/3,164/3,092；任务族含 core tool 26,114、browser deferred 18,221、project robot 4,726、general capability 10,000、workflow safety 2,930。project trajectory 转成 assistant tool_calls，并把 scope 写入 metadata；稳定 hash 防止同一 goal/trajectory 跨 split。低层坐标/框/action token 被排除，只保留高层 VQA 辅助。

**诊断 / 证据**：复算 manifest 总量、来源/任务族分布、split group overlap、project 空轨迹拒绝数和 ToolACE 过滤数；抽样检查 tools schema 与 assistant tool_calls。数量正确不代表来源质量、真实机器人覆盖或所有样本均为多模态。

**项目挂钩**：面试先报“混合 SFT 总量”，再给 project robot 子集和过滤逻辑；这是比只报 62k 更可信的数据设计回答。

**追问树**：为什么 ToolACE 排除？browser 为什么保留在 SFT？group key 如何防泄漏？VQA 会不会稀释 tool call？

**危险答案**：说“62,223 条全是真实机器人轨迹”，或只凭总量证明模型具备机器人闭环能力。

**来源**：[1][6]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-HARNESS-005</b> · GRPO 数据为什么不能直接复用全部 SFT 样本？</summary>

**面试意图**：判断你是否理解 teacher forcing 与可验证 reward task 的数据合同差异。

**30 秒回答**：GRPO 只保留可规则判分 task：allowed/forbidden tools、reference trajectory、success criteria、constraints、minefields；空轨迹 project、WebLINX/Mind2Web 不进 runner。8,916 条，train/dev/test=8,052/439/425。

**机制展开（约 2 分钟）**：SFT 只需标准答案；GRPO 必须让 rollout 可评分，因此要保留 initial state、可用/禁用工具、参考轨迹、成功条件与风险字段。任务族包括 clarification 2,300、no-forbidden-side-effect 3,735、project robot 2,748、cancel compensation 120、bound scope 13。browser 没有 runner 时默认 disabled，project 没有轨迹时跳过，避免把不可执行样本硬塞进 reward。

**诊断 / 证据**：统计每个 split 的空 trajectory、missing tools/success criteria、browser disabled 和 group duplicate；对每个 task family 运行 gold trajectory scorer。若没有 executable runner 或规则 oracle，应降级为 SFT/OOD probe，而不是假装可做 online RL。

**项目挂钩**：个人设计价值在“把哪些样本放进 SFT、哪些能进入 GRPO、哪些只做 eval”这一分流，而不是把所有数据平均混合。

**追问树**：没有 reference trajectory 能不能做 RL？bound scope 为什么只有 13 条？browser runner 缺失会造成什么假标签？

**危险答案**：说“只要有 prompt 就能做 GRPO”，或把 browser deferred 样本当作真实网页执行轨迹。

**来源**：[1][7]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-HARNESS-006</b> · schema-aware reward 与 1,200 条 tool-restraint 样本解决什么问题？</summary>

**面试意图**：检查你能否解释 reward 分解、hard penalty、no-call 标签与 reward hacking 风险。

**30 秒回答**：reward 按 task family 加权 tool name/order/coverage、参数语义、scope、澄清、状态和取消补偿，并对 forbidden、越权、缺信息仍执行设 hard penalty；另合成 1,200 条 no-call restraint。AppWorld 空轨迹被排除，避免把 runner 缺失误标成拒绝。

**机制展开（约 2 分钟）**：规则可写成组件加权和加 hard penalty；不同 family 强调不同目标，例如 project robot 偏 state/scope/order/arguments，clarification 偏先澄清和不执行。restraint 样本让工具可见但正确动作是拒绝或追问，最终 mixed train=9,252。脚本只从有 no-action 文本证据的候选生成；空轨迹本身不是 no-call 证据。安全 suite 仍弱，说明规则并未消除 hacking 或长链漏步。

**诊断 / 证据**：对 gold、空调用、只调用一步、越权 scope、带额外参数、正确拒绝做 reward unit test；比较 old/new reward 的 large drops，并做 no-restraint/no-scope/no-arg ablation。当前有规则和离线检查，缺同 protocol 因果消融。

**项目挂钩**：可讲“从平台失败模式反推 reward schema”；不能说 hard penalty 自动保证真实世界安全。

**追问树**：semantic match 怎样防宽松过头？为什么 exact 只作 diagnostic？no-call 如何避免全拒绝策略？GRPO 会不会 exploit scorer？

**危险答案**：把空 trajectory 一律当拒绝标签，或说 reward 达到高分就已经解决 side effect safety。

**来源**：[1][7][8][9]　**练习状态**：unseen

</details>

## C. Run lineage、指标与真实性边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-HARNESS-007</b> · 8B、32B base、32B SFT 和 GRPO checkpoint 指标应如何分层陈述？</summary>

**面试意图**：训练你主动绑定 model/run/checkpoint/suite/n/scorer，避免用好看的数字拼接一条不存在的曲线。

**30 秒回答**：需分 run：8B v3 holdout 95.3%；32B base 37.8%；32B SFT 95.42%；GRPO ckpt100/200 为 95.6%。但前两类 n=1333、GRPO n=1000，base 还用 Qwen-hidden scorer，不能直接宣称严格因果提升。

**机制展开（约 2 分钟）**：8B v3 是独立 full pipeline；32B base 单模型报告使用 schema-aware_v2 + Qwen hidden embedding。32B SFT 与 GRPO ladder 有本地 metrics，但 SFT/GRPO run manifest 使用 token-overlap fallback，GRPO 还截到 1,000 条 holdout。project suite 虽同为 n=130，也只证明结构化协议。面试可报每个 artifact 的值，但“37.8→95.6”必须先补同 scorer、同 n、同 suite 的 raw rerun。

**诊断 / 证据**：冻结 run ID、parent/checkpoint SHA、data/suite SHA、prompt/template、scorer/version/backend、n、raw predictions 和 summary；用统一 scorer 重算 base/SFT/ckpt100/200，再做逐样本 paired diff。当前 run/metrics 可读，统一比较 gate 未关闭。

**项目挂钩**：安全表达是“各自协议下分别达到”，并主动指出 comparator 缺口；这比把所有最好数字堆进简历更抗追问。

**追问树**：95.6 是哪个 checkpoint？为什么 n 不同？token overlap 和 hidden embedding 会影响什么？ckpt200 比 100 好吗？

**危险答案**：直接说“同协议从 37.8 提升到 95.6”，或把 8B 95.3 当成 32B GRPO 结果。

**来源**：[1][9][10][11][12]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>PROJ-HARNESS-008</b> · project sandbox 100% 为什么仍不能证明真实机器人成功，项目贡献应怎样表述？</summary>

**面试意图**：检查你能否同时守住 proxy metric、safety/browser 和个人 ownership 三条边界。

**30 秒回答**：sandbox 的 100% 与 argument 92.31/96.92 只证明结构化协议；safety 仍约 38%，browser 只是 deferred。候选人负责问题/约束/数据/reward/eval，Codex 主要实现；13-row ledger 不把 Git author 当手写证明。

**机制展开（约 2 分钟）**：sandbox scorer 没有相机、控制器、接触和真实 success predicate；ckpt100/200 safety tool accuracy 约 38.75%/37.37%，browser 无 runner。ownership ledger 进一步区分：候选人 self-attested owner/reviewer，Codex-primary engineering；Git 中有 sandbox `+859/-46`、robot registry `+156/-34` 和训练 artifact sync，但 commit author 仍不等于代码作者。强项应落在具体约束取舍、review、验收和 bad-case 判断。

**诊断 / 证据**：ledger 结构已完成；下一 gate 是回答 8 个角色问题并给 decision/review 证据。当前 targeted tests 为 11 pass/1 config-drift fail，不能说 runtime 全绿；真实 effect-sink 仍缺。

**项目挂钩**：项目结尾先给协议层结果，再主动说明 safety/browser/effect-sink 和 Codex implementation 边界。

**追问树**：真实 success 还差哪些层？为什么 safety 比 project suite 差？哪些代码是你亲手写的？Codex 做了什么？

**危险答案**：说“sandbox 100% 所以机器人任务成功率 100%”，或把 Git commit author 当作全部 runtime/training/eval 的独立 ownership。

**来源**：[1][2][10][11][13][14]　**练习状态**：unseen

</details>

## 参考来源

1. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：runtime、数据、reward、run/scorer 与 ownership 的冻结边界。
2. [Robot Harness 项目页](../../01_robot_harness_tool_training.html)：原有项目叙事、research framing 与高压追问。
3. `C:\Users\mousongzhe\agent\server\agent\runtime.py`：PydanticAI Agent、AgentDeps、server/client toolset、stream/non-stream 和 cleanup。
4. `C:\Users\mousongzhe\agent\server\tools\registry.py`：tool schema/过滤、robot mutex、取消、轮询、compensation 和 structured error。
5. `C:\Users\mousongzhe\agent\server\agent\history.py`：history compaction、action tool history stripping 与消息转换。
6. `C:\Users\mousongzhe\agent\remote_training_pipeline_scripts\prepare_sft_data.py` 与 `remote_training_pipeline_v2\manifests\sft_data_manifest.json`：SFT schema、过滤、split 与 62,223 条统计。
7. `C:\Users\mousongzhe\agent\remote_training_pipeline_scripts\prepare_grpo_data.py` 与 `remote_training_pipeline_v2\manifests\grpo_data_manifest.json`：rewardable task contract、8,916 条统计与 eval suite 路由。
8. `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\scripts\build_grpo_tool_restraint_mix.py` 与 manifest：1,200 restraint、9,252 mixed train 和 AppWorld 排除。
9. `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\reports\final_pipeline_report.md`：8B v3 pipeline、suite 指标、failure samples 与 browser/safety 边界。
10. `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\reports\32b_native_tools_eval_report.md`：32B base run 与 Qwen-hidden rescore。
11. `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\reports\eval_32b_ckpt100_200_d_ood_compare_1000_ladder_20260622_140818_attempt3_d32_ood32_comparison.md`：32B SFT/GRPO ladder 与 D/OOD 分项。
12. 本地 `native_tool_restraint_32b_sft_20260618_114113`、`...d_grpo32b_ckpt100/200` metrics/run manifests：n、scoring backend、checkpoint 与分项结果。
13. 本地 `git log --follow`：只作 commit authorship signal；ledger 已建立但候选人角色确认仍缺。
14. 本地 [Robot Harness Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html)：candidate-owner / Codex-primary implementation、13 个文件/决策、Git diff 与 targeted-test warning。
