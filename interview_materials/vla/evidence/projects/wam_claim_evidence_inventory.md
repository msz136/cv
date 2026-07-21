# Cosmos / WAM Claim–Evidence Inventory（WAM-01）

> 状态：`drafted / local_claim_audit / WARN / resume_safe_downgraded / diagnostic_artifacts_partial / ownership_ledger_added`  
> 审查日期：2026-07-21  
> 证据截止：2026-07-21  
> 项目范围：Cosmos Policy / WAM 多目标后训练、RoboCasa official-checkpoint eval 与本地 0-success 诊断  
> 目标岗位：VLA / World Model / Robot Learning 算法与训练评估方向  
> 结论先行：上游 Cosmos Policy 的 action/future/value slot、routing、loss mask 与 RoboCasa protocol 已有 frozen paper/repo 支持；2026-07-17 对 `cv` 工作区的扫描未找到 WAM 训练/评测 raw bundle，因此历史本地数字先保持 `local-claim-only`。2026-07-18 在外部 `C:\Users\mousongzhe\Project\wm\outputs` 发现一组 CoffeePressButton diagnostic artifact；2026-07-21 又冻结了 8 卡 1 epoch gate 的运行合同与失败链、独立 full10k trained `iter_000010000` 的 RoboCasa 24×5 remote-artifact bundle（raw `2/120`、当前本地 policy trusted `0/118`，两个 CoffeeServeMug length=1 artifact success 被排除）、official-HF RoboCasa baseline 的 24×5 remote-artifact bundle（raw `86/120`、trusted `84/118`）、TurnOffMicrowave local 1k checkpoint 的 fixed-batch→closed-loop→same-input first-divergence 审计，以及 DeepSpeed base-load/short-smoke/formal-save gate 审计。新证据支持“trained-run 与 official-HF 评测链路、一个本地 0/1 失败链和 save/load first-divergence 可审计”，但不支持本地 checkpoint binary/hash、训练 uplift、官方 scorer 等价、唯一 root cause 或 ownership。2026-07-17 已完成安全降级：optimized resume 的 WAM 段不再包含 MSE、task success、official-HF reproduction 或 local 0-success 数字；投递 PDF 已从新 HTML 重建并完成 A4 单页视觉/文本检查。投递 release blocker 已关闭，但项目证据仍为 WARN，不能升级为 verified/reviewed。

## 问题（Question）

这份清单回答四个问题：当前 WAM 简历中哪些内容有上游事实支撑，哪些只是本地自述；`0.09718→0.05349`、`84/118`、`0.90–0.95 / 0.75` 与 `0 success` 分别属于哪个证据层；哪些表述现在能安全口述；要补什么 artifact 才能把 claim 从“知道/参与”升级为“负责/优化/结果影响”。

本页不是新的项目成绩报告，也不把已有 HTML 相互引用当作独立证据。它把简历、项目页、旧版简历和 frozen upstream audit 当作不同来源，显式记录一致、冲突和缺失。[1][2][3][4][5][6][7]

## 1. 范围、标签与判定规则

### 1.1 Evidence labels

| 标签 | 定义 | 本页如何使用 |
| --- | --- | --- |
| `upstream-verified` | primary paper、官方 frozen repo/model card 可直接支持 | 只支持 Cosmos Policy 公有机制与官方协议，不支持个人运行 |
| `local-direct` | 当前可读取 code/config/log/checkpoint/eval/episode artifact | `cv` 工作区没有 WAM checkpoint；2026-07-18 在外部 `C:\Users\mousongzhe\Project\wm\outputs` 发现一组 manifest/trace/video diagnostic bundle，已单独登记，checkpoint 仍未验证 |
| `local-claim-only` | 内容只出现在简历、项目页或重构计划 | 可作为待核线索，不能作为结果证明 |
| `inference` | 从同源证据推得，但来源没有直接声明 | 必须写成假设或分析框架 |
| `conflict` | 两个来源的 checkpoint、protocol 或结论无法同时对齐 | 在 provenance 澄清前禁止升级 |
| `ownership-unverified` | 上游设计已核实，但缺 local diff/设计记录证明个人贡献 | 只能说“梳理/对齐/复现尝试”，不能说“设计/提出” |

### 1.2 Claim levels

| 等级 | 允许的表达 | 最低证据 |
| --- | --- | --- |
| C0 | 了解、阅读、参与讨论 | 可解释的项目文档或口述 |
| C1 | 负责模块、实现、迁移 | local code/diff、配置、命令或日志 |
| C2 | 设计、优化、定位根因 | 对照实验、bad case、设计记录、修复前后证据 |
| C3 | 提升 X%、达到成功率、完成上线/正式训练 | 完整 metric protocol、checkpoint、raw summary、可重放记录与 ownership |

强度不是按措辞感觉决定，而是按 `claim + protocol + artifact + ownership` 四项共同决定。缺任一项时，C2/C3 必须降级。[8]

## 2. Role Fit 与岗位能力映射

本项目与 VLA/World Model 岗位的匹配点是：多目标训练合同、动作/未来/value 的信息流、RoboCasa closed-loop eval、normalization/controller boundary 和 0-success failure attribution。当前最强的是“能解释上游机制和应如何审计”，最弱的是“本地运行和个人改动没有 raw artifacts”。

| 岗位能力项 | 当前材料 | 强度 | 缺口 | 当前策略 |
| --- | --- | --- | --- | --- |
| WAM/VLA architecture | frozen Cosmos audit 已核对 latent slot、condition/loss mask、direct/planning paths | 中强（上游） | local tensor trace/diff 缺失 | 前置为机制理解，不包装成原创 |
| Multi-objective training | 项目页描述 action/world/value routing 与 loss weighting | 中（叙事） | exact local config、mask smoke、gradient trace 缺失 | 只说“梳理/对齐”，不说“设计并证明有效” |
| Training/debugging | 项目页记录 gripper、high-sigma、5-frame、OOM、state_dict 假设链 | 中低 | 日志、patch、rerun 与因果闭环缺失 | 说“形成诊断假设”，不说“定位根因” |
| Offline evaluation | MSE 0.09718→0.05349 出现在三份自述材料 | 低 | split、metric code、prediction/label artifact 缺失 | 从投递稿移除，待核后恢复 |
| Closed-loop evaluation | full10k trained 24×5 audit：raw 2/120、local-policy trusted 0/118；official-HF 24×5 audit：raw 86/120、trusted 84/118 | 中低 | checkpoint revision/hash、完整 episode JSONL、scorer/version、matched trained-vs-baseline run 缺失 | 可讲两条 eval harness 与日志重算；不写成本地训练结果 uplift 或官方 scorer 等价 |
| Scientific ablation | 已提出 action-only/+world/+value/all | 弱 | 没有执行结果 | 标为可补做，不写成已完成 |
| Ownership | 项目页称“我负责复现/诊断” | 低 | local diff、run ledger、人工贡献边界缺失 | 需要候选人逐项确认 |

没有提供具体 JD，因此这里做的是目标岗位能力映射，不伪造公司面试流程或岗位关键词。

## 3. Frozen inputs 与当前工作区检索

| Source | SHA-256 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| optimized 简历 [1] | `8e9c029d40163c83e9c689e22d326bca23efaf248f046d3fa40b402bd4b470a1` | 当前安全降级后的三条 WAM 表述 | 任一本地数字或完成态 ownership |
| optimized 投递 PDF [11] | `65b1dcd34cd6e357c6264effcf4b2683dea66508c6bc58315762b5e4c03ac74a` | WAM 安全降级与 OpenPiVLA 安全重写已同步到可投递 A4 单页 PDF | 项目 raw evidence |
| WAM 项目页 [2] | `251cbcac43a1acb2052e7866e2d5a9a6f71c01fd07ef0cdb0035d66f5ebc61a5` | evidence-gated 叙事、失败假设、artifact queue | artifact 实际存在或结果已复现 |
| resume restructure plan [3] | `e31ccb40381dc6abe9fd6b9622ab48b9a6cfc8fe71039f6d97db8722450e43e6` | 当前安全口径与 evidence queue | checkpoint/episode 归属 |
| research resume [4] | `9a8828ae0b6317c107ab16ec3d106cad8ba944854469e7919a7ba0c1342b643f` | full10k/loss/sample-count 历史表述 | 与 MACA 1-epoch 分支的关系 |
| engineering resume [5] | `2aa3f0dae040ad5fb6bff32d68b5f4fff574bf4b2be80abc93d9f29b96f78732` | 同上历史表述 | 可加载 checkpoint 与正式 eval |
| Cosmos source audit [6] | `7f620f4ded9766f71bb75b0a927c168b8e5dec1875257dc94e2c8f35fdfd686f` | frozen upstream mechanism、repo/model revision、protocol boundary | 用户本地训练数字与 ownership |
| Benchmark/evidence audit [7] | `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a` | paper→repo→checkpoint→runtime 证据合同 | 当前缺失的 local trained runtime artifacts |
| Official-HF baseline P0 audit [11] | `39E59144D6CE36135A09314294C5E399BC1F2D686A55486C919DA5F5A63972B8`（canonical audit） | 24×5 logs、raw/trusted recount、protocol tuple、action-debug integrity | checkpoint binary/hash、完整 episode JSONL、candidate ownership |
| TurnOffMicrowave trained-failure P0 audit [12] | `80789C958CBDBBEF9FEDEDBA13D6BAFBECAB64FAE1A45E5AFF0C3470FFF57CAB`（canonical audit） | local 1k fixed-batch gate、`0/1` closed-loop、5-frame counterfactual、same-input first divergence、state mining 与 corrected overfit | immutable checkpoint binary/hash、matched patch→rerun、多 episode scorer、candidate ownership |
| Checkpoint save-load gate P0 audit [13] | `D5A4DB639C3C0C152D55F3F9C6F6BEDD8E18408F306036A28DA5154BAB3D9AAC`（canonical audit） | 13 base-load summaries、715-key clean load、1/5-step smoke、9907-step save2k resource line、save1500 `state_dict(destination=...)` first divergence、0 checkpoint-like binaries | produced checkpoint、fresh-process reload parity、matched eval、patch ownership |
| Full10k trained eval P0 audit [16] | `DB83888B1279E548EBCA64260094489366905C632C5CC4F9E44F834BC12D66CF`（canonical audit） | full10k `iter_000010000` remote path 下24×5 status/log/summary 对齐，raw `2/120`、local-policy trusted `0/118`、24 action-debug/4066 lines/32×7 finite | checkpoint binary/hash、fresh-process reload、official scorer equivalence、完整 episode JSONL、matched uplift、candidate ownership |

2026-07-17 对 `C:\Users\mousongzhe\cv` 做文件名与全文检索时，确实未找到这些外部 Project artifacts；这个历史结论只覆盖当时的 `cv` 工作区。2026-07-21 对 `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts` 做了独立只读审计：full10k trained run 有 24 条 `*-5ep-alltasks-*` logs、24 个 action-debug JSONL、24/24 formal `exit_code=0`，raw `2/120`；两个 `CoffeeServeMug` length=1 success 按当前本地 policy 排除后为 `0/118`。同一目录另有 25 个 command manifest、14 个本地同步 media 和 169-entry light archive；仍没有 `.pt/.ckpt/.safetensors`，不能代替完整 120 episode media/JSONL。official-HF baseline 保持独立 bundle 与 `86/120` raw、`84/118` trusted 口径。

安全降级前的 optimized resume、项目页与 restructure plan SHA 分别为 `58c004d85b60...`、`1de96b9cc2b5...`、`96cb4f8c3168...`；它们保留在本 review 的变更历史中，用于证明本次处理确实移除了投递稿的未核验 C3 表述，而不是重写证据来源。

## 4. Claim reconciliation matrix

| ID | 当前 claim | 出处 | 等级 | 当前证据 | Verdict | 处理动作 |
| --- | --- | --- | --- | --- | --- | --- |
| `WAM-CL-001` | 复现 RoboCasa WAM 1-epoch 后训练 | optimized/project/旧简历 + [save-load gate P0 audit](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html) | C1/C2 | 8-GPU run contract、base-load、smoke、formal save2k/save1500 logs 可复核；长训与 checkpoint gate 失败 | `LOCAL-ARTIFACT-BACKED / GATE-FAILED` | 可说“开展并审计复现 gate”；不能说完成 1 epoch 或有可加载 checkpoint |
| `WAM-CL-002` | 设计 action/world/value 三目标、mask 互斥和 slot routing | optimized/project | C2 | 上游机制已核实；无 local diff | `ownership-unverified` | 改为“按 upstream contract 梳理/对齐”；不得把 slot/mask 称个人原创 |
| `WAM-CL-003` | held-out policy MSE `0.09718→0.05349`，下降约 45% | pre-downgrade resume/project/plan | C3 | 无 split、metric script、pred/label、checkpoint | `C3-BLOCKED / REMOVED` | 已从当前可投递稿移除；四类 artifacts 齐全后才可恢复 |
| `WAM-CL-004` | short-horizon 任务 `0.90–0.95`、pick/place `0.75` | pre-downgrade resume/plan | C3 | 没有 task ID、trial、checkpoint、summary；历史项目页同时记录 local 0-success | `CONFLICT / REMOVED` | 已从当前投递稿移除；先确认是否属于 official checkpoint、其他 run 或误写 |
| `WAM-CL-005` | official HF baseline 24×5 raw `86/120`、trusted `84/118=71.19%` | project page + [official-HF P0 audit](cosmos_policy_robocasa_baseline_p0_audit.html) | C2/C3 | 24 task logs/status/action-debug 可复核；checkpoint 只有 remote path，2 个 artifact success 的 exclusion 规则是本地审计口径 | `REMOTE-ARTIFACT-BACKED / CHECKPOINT-UNVERIFIED` | 可说“运行并审计 official-HF eval harness”；不能说个人训练成绩或 uplift；补 revision/hash、完整 episode JSONL 与 ownership 后再升级 |
| `WAM-CL-006` | 本地训练 checkpoint TurnOffMicrowave closed-loop `0/1` | project page + [TurnOffMicrowave P0 audit](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.html) | C2 | 1 episode、500 steps、32 queries、action-debug 与 same-input summaries 可复核；checkpoint 仍 remote-referenced | `LOCAL-ARTIFACT-BACKED / CHECKPOINT-UNVERIFIED` | 可讲最小失败复现与 first divergence；不能写 benchmark success rate 或本地 checkpoint hash |
| `WAM-CL-007` | failure first divergence 收窄到 5-frame contract 与 exact-observation transfer gap | [TurnOffMicrowave P0 audit](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.html) | C2 | fixed batch sampled `-0.8277`、official/local exact first `-1.0156/+0.1429`、best-of-8 全正、top-24 negative `37.5%`；没有 matched fix→rerun | `PARTIALLY-CONFIRMED / ROOT-CAUSE-OPEN` | 说“已确认 conditioning 差异与 transfer gap”，不说唯一 root cause 或已修复 |
| `WAM-CL-008` | 在 MACA/C500 修复 dataloader cycle OOM 与 DeepSpeed state_dict | project page + [1 epoch freeze](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html) + [save-load gate P0 audit](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html) | C1/C2 | no-cycle 5-step `exit=0`、save2k rank -9/`EXIT=247`、save1500 `state_dict(destination=...)` TypeError/`EXIT=1` 可复核；patch diff/修复后 parity 仍缺 | `LOCAL-ARTIFACT-BACKED / PATCH-UNVERIFIED` | 可讲故障边界与验证设计；不能说修复已完成 |
| `WAM-CL-009` | full10k checkpoint 保存成功，iter 10000 loss=0.0543，sample counts 4950/2519/2531 | research/engineering resume | C3 | 只在旧版简历；项目页又说 C500 1-epoch 无可加载 final checkpoint | `RUN-PROVENANCE-OPEN` | 区分 hardware、run ID、base checkpoint、保存格式；不能合并为同一训练线 |
| `WAM-CL-010` | “我负责”官方路径复现、routing 与失败诊断 | project page | C1/C2 | 无 ownership ledger 或 local diff | `ownership-unverified` | 候选人按“亲手/协作/仅理解/工具辅助”逐项确认 |
| `WAM-CL-011` | full10k trained checkpoint path 下 RoboCasa 24×5 raw `2/120`、local-policy trusted `0/118` | [Full10k trained eval P0 audit](cosmos_policy_full10k_trained_eval_p0_audit.html) | C2 | status/log/summary/action-debug 对齐；checkpoint 只有远端 path，`length<5` exclusion 是本地审计 policy，完整 episode JSONL/scorer/ownership 缺失 | `REMOTE-ARTIFACT-BACKED / CHECKPOINT-UNVERIFIED` | 可说“运行并审计 full10k trained eval harness”；不能写官方 benchmark、checkpoint ownership 或相对 official-HF 的 uplift |

## 5. 三个关键冲突

### 5.1 `0.90–0.95 / 0.75` 与 local 0-success

两组表述不一定逻辑上绝对矛盾：成功率可能来自 official checkpoint、另一 local checkpoint、不同任务子集或不同协议。但当前材料没有给出身份元组：

```text
(run_id, checkpoint_sha, model_role, task_id, init_set, trial_count,
 horizon, controller, success_predicate, summary_path)
```

因此现在无法判断它们能否并存。2026-07-17 已把成功率从投递稿移除；在身份元组和 raw episode records 完整前，不恢复该表述。

### 5.2 full10k eval 与 C500 final checkpoint 缺失

旧版 research/engineering resume 说 `full10k checkpoint 保存成功`；新增 remote-artifact audit 证明该独立 run 的 `iter_000010000` path 进入了完整 24×5 eval，raw `2/120`、当前本地 policy trusted `0/118`。项目页的高压回答说 MACA/C500 1-epoch 主线“当前没有可加载 final checkpoint”。这仍是两条不同硬件或不同阶段的 run：full10k 的 path、训练/eval logs 和 8-GPU save1500 failure 不能互相替代，且 full10k checkpoint binary/hash、fresh reload 和完整 scorer bundle 仍未闭合。面试中不得把 full10k 的 `0/118` 直接与 official-HF `84/118` 做 uplift。

### 5.3 “三个 head”与 upstream slot/mask contract

frozen source audit 显示 Cosmos Policy 更接近在统一 latent video sequence 中注入/抽取 proprio、action、future 与 value，并用 condition/loss mask 和 sample routing 切换任务；把它简化成独立的 action/world/value 三个 head 适合初级直觉，但不能当作实现事实。[6] 面试安全说法是“共享 diffusion backbone，隔离的是 latent slots、condition/loss mask 和 sample route”。

## 6. Truth boundary 与安全口径

| 内容 | 当前状态 | 简历 | 面试 | 证据到位后 |
| --- | --- | --- | --- | --- |
| 阅读并解释 Cosmos Policy action/future/value contract | `upstream-verified` | 可写为技术栈/理解，不作项目成果 | 可以机制级解释 | 无需升级为个人原创 |
| 开展 local WAM 复现 | `local-claim-only` | 仅在候选人确认后用“开展/尝试复现” | 说明当前材料缺 raw bundle | code/config/log/checkpoint 到位后升 C1 |
| MSE 45% | `C3-BLOCKED / REMOVED` | 已从当前简历移除 | 不主动报数 | split/script/prediction/checkpoint 齐全后恢复 |
| RoboCasa 0.90–0.95 / 0.75 | `CONFLICT / REMOVED` | 已从当前简历移除 | 不报数 | checkpoint/task/trials/episodes 完整后重新判定 |
| official HF 71.19% | `remote-artifact-backed / checkpoint-unverified` | 不写成本人模型成绩 | 可说按官方 checkpoint path 跑过并重算 eval；必须说明 86/120 vs 84/118 口径和缺失 local binary/hash | revision/hash + 完整 episode JSONL + scorer/version + ownership 后才可写“复现官方 checkpoint” |
| full10k trained 24×5 `2/120` raw、`0/118` local-policy trusted | `remote-artifact-backed / checkpoint-unverified` | 可写“审计 full10k trained eval harness”，不写官方 benchmark | 说明两条 length=1 artifact、local invalid policy、24×5 protocol 与 remote checkpoint path；不把结果写成官方 scorer 或 uplift | checkpoint binary/hash + fresh reload + versioned scorer + complete episode JSONL + matched baseline + ownership |
| local 0-success 与 root cause | `claim-only / inference` | 不写性能结果 | 可以讲诊断框架，原因用“候选/待确认” | 修复前后 paired rerun 后写 confirmed/partially confirmed |
| 上游 routing/mask | `upstream-verified` | 不写“我设计” | 说“我按 upstream contract 审计/对齐” | local substantive diff 到位后再描述个人修改 |

### 当前仍不能升级成强结果项目的原因

1. 最强的四组数字都没有 raw artifact。
2. 历史 optimized resume 与项目页对本地 closed-loop 结果没有统一 provenance；当前简历已降级，但事实缺口仍未关闭。
3. full10k 与 MACA/C500 训练线没有 run ledger，可能被面试官一问即穿。
4. upstream architecture 与 personal contribution 没有 diff/ownership 分界。
5. 现有诊断是合理假设链，但没有修复后的因果对照。

### 当前保守表达

仅在候选人确认“确实亲手做过该复现”后，当前可用的最低风险版本是；optimized resume 已按这一边界落地：

> 基于 Cosmos Policy / RoboCasa 公开 recipe 开展 WAM 后训练复现与失败诊断，重点梳理 action/future/value latent slot、condition/loss mask、action normalization 与 closed-loop eval contract；当前成果定位为复现与诊断，不宣称本地策略成功率提升。

这句话是 C0/C1 边界表达，仍需候选人确认 ownership；它刻意不包含 45% MSE、0.90–0.95、0.75、71.19% 和已确认 root cause。

## 7. P0 artifact manifest

| Priority | Artifact | 最低字段 | 关闭哪些 claim | 当前状态 |
| --- | --- | --- | --- | --- |
| P0 | `wam_run_manifest.json` | run ID、hardware、repo commit、base/model checkpoint SHA、config SHA、dataset/stats SHA、command、start/end/status | CL-001/009 | `MISSING` |
| P0 | local code/config diff | changed files、diff、为什么改、author/tool boundary | CL-002/008/010 | `MISSING` |
| P0 | MSE eval bundle | split manifest、metric code SHA、baseline/prediction/label、per-dim/aggregate result | CL-003 | `MISSING` |
| P0 | task-success provenance | checkpoint、task IDs、init、trial count、horizon、controller、success predicate、episode records | CL-004/011 | `PARTIAL / full10k remote-artifact-backed; binary/hash, scorer version and complete episode records missing` |
| P0 | full10k trained eval bundle | 24×5 status/log/summary/action-debug、checkpoint/stats/embedding identity、raw/trusted recount、run-family join key | CL-011 | `PARTIAL / REMOTE-ARTIFACT-BACKED`; current local policy excludes two length=1 artifacts; checkpoint/reload/scorer/ownership remain open |
| P0 | official-HF eval bundle | HF repo+revision、config/stats SHA、24×5 episode records、raw/trusted exclusion reason、summary/videos | CL-005 | `PARTIAL / REMOTE-ARTIFACT-BACKED` |
| P0 | local 0-success bundle | local checkpoint load log、same-protocol episodes、action/gripper hist、first-divergence trace | CL-006/007 | `PARTIAL / TURN-OFF-MICROWAVE ARTIFACT-BACKED`; immutable checkpoint、matched fix→rerun、multi-episode denominator 与 ownership 仍缺 |
| P0 | checkpoint save-load gate bundle | base-load summaries、run contracts、short-smoke exit/metrics、formal save logs、checkpoint file manifest、fresh-process reload | CL-001/008/009 | `PARTIAL / BASE-LOAD-BACKED`; current archive has 0 produced checkpoint-like binaries and no reload parity |
| P1 | training curves | total/action/world/value diagnostic scalars、step、smoothing rule | CL-001/009 | `MISSING` |
| P1 | debug patch bundle | OOM/state_dict before log、patch/diff、rerun log、checkpoint load smoke | CL-008 | `MISSING` |
| P1 | ownership ledger | 亲手实现、协作、只阅读、Codex/工具生成、上游未改五类 | CL-002/010 | `MISSING` |

### Evidence promotion pseudocode

```python
def promote_claim(claim, bundle):
    # 1. A metric claim must bind to one immutable run and checkpoint.
    require(bundle.run_id and bundle.checkpoint_sha and bundle.config_sha)

    # 2. Evaluation must expose the complete protocol and raw episode records.
    require(bundle.protocol and bundle.episode_records and bundle.metric_code_sha)

    # 3. Personal ownership must be separated from frozen upstream code.
    require(bundle.ownership_ledger and bundle.local_diff)

    # 4. Only then may a C2/C3 claim enter the resume or strong oral answer.
    return "verified" if all_checks_pass(bundle) else "claim-only"
```

该伪代码表达的是证据门，不是用户项目中已经存在的实现。

## 8. 必须回答的六个问题

1. `0.90–0.95 / 0.75` 分别对应哪些 RoboCasa task、哪个 checkpoint、每项多少 trial、何种 init/horizon/controller？
2. `full10k checkpoint` 与 MACA/C500 “无可加载 final checkpoint”是否是两条 run？各自的硬件、base checkpoint、run ID 和保存路径是什么？
3. `0.09718→0.05349` 的 held-out split 怎样生成，MSE 对哪些 action steps/dimensions 求平均，prediction/label 文件在哪里？
4. `84/118` 被排除的 2 条 episode 是什么异常？`86/120`、`84/118` 的 raw summary、视频与 model revision 在哪里？
5. 哪些 WAM code/config 是你亲手改的，哪些来自 upstream，哪些由 Codex/同事/脚本完成？
6. gripper/high-sigma/conditioning/DeepSpeed 中，哪些只是假设，哪些有修复后的 paired rerun 能确认因果？

## 9. Preliminary SP/SSP project scorecard

这是“项目证据就绪度”而不是候选人能力评分；由于 raw artifacts 缺失，置信度为 `Medium-Low`。

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.0 | WAM、multi-objective、RoboCasa eval 与 VLA 岗位高度相关 |
| 机制深度 | 3.5 | source audit 已达到 slot/mask/sampler/protocol 层，但项目页仍有 three-head 简化 |
| 工程闭环 | 2.0 | 有诊断 bundle 与叙事，但缺完整 run bundle 与可加载 checkpoint |
| 指标可信度 | 1.0 | 四组本地/复现数字均无 raw artifact，且一组存在 provenance 冲突 |
| Ownership 清晰度 | 1.5 | 有自述，缺 local diff 与贡献分类 |
| 抗追问能力 | 2.5 | 边界意识较好，但数字和 run 身份会被高压追问击穿 |
| 合计 | **14.5 / 30** | 投递稿已安全降级，但当前仍不具备强结果项目的 raw evidence |

强结果升级阻断项：full10k/C500 run provenance 未拆开；现有 local direct 仅覆盖一组 CoffeePressButton diagnostic bundle，checkpoint/metric/denominator/ownership 仍未闭合。原 `WAM-CL-004` 投递 blocker 已通过安全降级关闭。

## 9.5 Artifact Discovery Addendum（2026-07-18）

本 addendum 不回溯改写 2026-07-17 的 `cv` 工作区扫描，而是记录一次外部 Project 目录的只读发现。详细文件、SHA、manifest 字段和缺口见 [WM-019 WAM Diagnostic Artifact Manifest](wm019_wam_artifact_manifest.html)；同一输入的结构/逐步差异计算见 [WM-019 WAM Action-Trace Paired Diagnostic](wm019_wam_action_trace_paired_diagnostic.html)，离线 future-image PSNR/SSIM 对照见 [WM-019 WAM Future-Metric Paired Diagnostic](wm019_wam_future_metric_paired_diagnostic.html)，两侧 `iter_000010000` 的 exact checkpoint-path bridge 见 [WM-019 Matched-Checkpoint Protocol Bridge](wm019_wam_matched_checkpoint_protocol_bridge.html)。

发现的代表性文件包括 CoffeePressButton base/trained diagnostic bundle、full10k trained 的 `eval_summary_conservative.json`/`formal_5ep_status.tsv`/24 条 task logs/24 个 action-debug JSONL、official-HF baseline 的 `eval_summary_officialhf_baseline.json`/`formal_5ep_status.tsv`/24 条 task logs/24 个 action-debug JSONL，以及 TurnOffMicrowave local 1k 的 fixed-batch、query-probe、state-mining 与 `0/1` eval summaries。四类证据必须分开：CoffeePressButton 是单 episode 失败诊断，full10k trained 是远端 `iter_000010000` path 下的 24×5 eval（raw `2/120`、local-policy trusted `0/118`），official-HF 是另一官方 checkpoint path 下的 24×5 eval，TurnOffMicrowave 是 local checkpoint 的一条可复核失败链。full10k、official-HF 与 TurnOffMicrowave 的 checkpoint、stats 与 T5 仍含 remote path reference；没有 local binary/hash，selected/local videos 也不能替代完整 episode bundle。

因此：

- `WAM-CL-001` 可新增一条 `local-direct diagnostic / checkpoint-unverified` 证据线，但不能升级为完成 WAM 复现；
- `WAM-CL-005` 可从 `local-claim-only` 提升为 `remote-artifact-backed / checkpoint-unverified`，但不进入个人模型成绩或 uplift；
- `WAM-CL-011` 可登记为 full10k trained 24×5 的 `remote-artifact-backed / checkpoint-unverified`，raw/trusted 两套口径必须同时保留，不能与 official-HF 结果直接做因果 join；
- `WAM-CL-003..004/008..009` 的历史 MSE、task-success、uplift 与 full10k/C500 join 仍保持 `REMOVED`、`local-claim-only` 或 `RUN-PROVENANCE-OPEN`；`WAM-CL-006/007` 已有一条 local artifact-backed 的 TurnOffMicrowave 失败/first-divergence 证据线，但仍不升级为 benchmark 或 fixed root cause；
- action trace 和 episode-0 `success=false` 只能支撑接口/失败诊断，不能构成 benchmark denominator、模型比较或 0-success 结论；
- base/trained trace 的 `MAE=0.3100783611`、`RMSE=0.3906446459` 只是 JSONL 几何差异，不能替代 target-based action loss、checkpoint causal comparison 或 success uplift；
- `iter_000005000` 与 `iter_000010000` 的单 sample future-only PSNR 为 `8.5813` 与 `8.2140`、SSIM 为 `0.04527` 与 `0.04286`；它们是 offline visual proxy，样本数为 1，不能替代 action/simulator/real success。
- ownership 仍需要逐文件 ledger，不能由 artifact 所在目录或 Git author 推断。

## 10. 分阶段补强计划

| 时间 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 回答六个问题；补充 WAM diagnostic manifest；建立 run/metric/ownership 三张 manifest；先从投递稿降级冲突数字 | 每个数字都有唯一 run ID 或明确删除 | `部分完成 / P0 仍待补` |
| 1 天 | 收集 config、command、checkpoint/load log、MSE script、official/local eval summary | P0 artifact 表至少关闭 4 项 | `待补做` |
| 3 天 | 在同 split 重算 repeat/model MSE；做 official checkpoint 同协议重放；生成 per-episode ledger | 数值可由命令重算，异常 episode 有原因 | `待补做` |
| 1 周 | 在可加载 local checkpoint 上做 action-only/+world/+value/all 或最小 paired ablation，并记录 closed-loop failure trace | 可以区分表示收益、接口错误和 closed-loop 失败 | `待补做` |

任何补强只有在 artifacts 实际生成后才能改为“已做”。

## 11. 下一切片

2026-07-21 已完成五个独立 bounded slices：[Cosmos 1 epoch evidence freeze](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html) 冻结 9907-step gate、step-1900 cgroup-OOM 与 step-1500 `state_dict` 保存失败；[full10k trained eval P0 audit](cosmos_policy_full10k_trained_eval_p0_audit.html) 审计远端 `iter_000010000` path 下24×5 raw/trusted 与4066行 action-debug；[official-HF RoboCasa baseline P0 audit](cosmos_policy_robocasa_baseline_p0_audit.html) 重算 24×5 raw/trusted 结果并冻结 action-debug integrity；[TurnOffMicrowave trained-failure P0 audit](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.html) 把 local `0/1` 收窄到 fixed-batch 可学但 official 5-frame exact-observation 不迁移；[checkpoint save-load gate P0 audit](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html) 将 base-load、short smoke、resource failure 与 save API first divergence 分开。五者提升了 WAM 的训练/评测/诊断/保存门证据等级，但不改变 local trained checkpoint hash、1 epoch completion、paired uplift、唯一 root cause 和 ownership gates。

优先级最高的下一步是二选一：

1. 先补齐 [WAM diagnostic manifest](wm019_wam_artifact_manifest.html) 与 [full10k trained eval P0 audit](cosmos_policy_full10k_trained_eval_p0_audit.html) 的 checkpoint/hash、fresh reload、完整 denominator、versioned scorer 和 metric script，再决定是否能升级 `WAM-CL-003..004/006/011`；official-HF `WAM-CL-005` 的 24×5 remote-artifact audit 已完成，但仍需 revision/hash、完整 episode JSONL 与 ownership；或
2. 在 WAM 保持 WARN 的同时，OpenPiVLA 已完成 direct audit 与安全简历重写；后续按 direct-evidence-bounded 题卡批次推进，WAM raw bundle 仍独立排队。

WAM optimized resume 安全降级已完成；raw evidence gate 未关闭前仍不生成 WAM 强回答卡，不创建 mastery/coaching state，也不把 G09 推进到 reviewed。

## 参考文献（References）

1. [optimized resume](../../../../output/mousongzhe_resume_optimized.html)，当前投递稿，WAM 三条 bullet。
2. [Cosmos / WAM 项目面试页](../../../04_cosmos_wam_multitask_training.html)，现有叙事、诊断与 artifact queue。
3. [resume restructure plan](../../../../output/resume_restructure_plan.md)，WAM 数字与谨慎边界。
4. [research resume](../../../../output/mousongzhe_resume_research.html)，历史 full10k/loss/sample-count 表述。
5. [engineering resume](../../../../output/mousongzhe_resume_engineering.html)，历史 full10k/loss/sample-count 表述。
6. [VOL 04 Cosmos Policy / WAM frozen source audit](../../sources/vol_04_cosmos_policy_wam_claim_to_code.html)；canonical [Markdown](../../sources/vol_04_cosmos_policy_wam_claim_to_code.md)，review [JSON](../../sources/vol_04_cosmos_policy_wam_claim_to_code.review.json)。
7. [VOL 04 Benchmark / Evidence audit](../../sources/vol_04_benchmark_evidence_claim_to_protocol.html)；canonical [Markdown](../../sources/vol_04_benchmark_evidence_claim_to_protocol.md)，review [JSON](../../sources/vol_04_benchmark_evidence_claim_to_protocol.review.json)。
8. ProjectProof evidence contract：本轮使用的 C0–C3 规则；该规则只定义证据门，不是用户项目事实。
9. Kim et al., [Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning](https://arxiv.org/abs/2601.16163v1), 2026。
10. [Cosmos 1 epoch evidence freeze](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)；canonical [Markdown](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.md)，review [JSON](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.review.json)。
11. [Cosmos official-HF RoboCasa baseline P0 audit](cosmos_policy_robocasa_baseline_p0_audit.html)；canonical [Markdown](cosmos_policy_robocasa_baseline_p0_audit.md)，review [JSON](cosmos_policy_robocasa_baseline_p0_audit.review.json)。
12. NVlabs, [`cosmos-policy@18a2acc`](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)，Apache-2.0 code；model weights 另受 model-card license 约束。
13. [optimized resume PDF](../../../../output/pdf/mousongzhe_resume_after.pdf)，由当前 optimized HTML 重新生成；PDF SHA-256 `65b1dcd34cd6e357c6264effcf4b2683dea66508c6bc58315762b5e4c03ac74a`，A4 单页，旧 WAM 数字文本检索为 0。
14. [TurnOffMicrowave trained-failure P0 audit](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.html)；canonical [Markdown](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.md)，review [JSON](cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.review.json)。
15. [Checkpoint save-load gate P0 audit](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html)；canonical [Markdown](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.md)，review [JSON](cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.review.json)。
16. [Cosmos full10k trained eval P0 audit](cosmos_policy_full10k_trained_eval_p0_audit.html)；canonical [Markdown](cosmos_policy_full10k_trained_eval_p0_audit.md)，review [JSON](cosmos_policy_full10k_trained_eval_p0_audit.review.json)。
