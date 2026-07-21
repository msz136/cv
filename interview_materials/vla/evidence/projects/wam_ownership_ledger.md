# Cosmos / WAM Ownership Ledger：多目标训练、RoboCasa 评测与诊断边界

> 状态：`ownership_audited / diagnostic_artifacts_partial / candidate_confirmation_pending / WARN`
> 审查日期：2026-07-19
> 证据截止：2026-07-19
> 项目范围：`C:\Users\mousongzhe\Project` 中的 Cosmos Policy / WAM 训练适配、RoboCasa rollout、Cosmos/WAM diagnostics 与当前 CoffeePressButton paired artifact。
> 结论先行：Cosmos Policy 的 latent slot、condition/loss mask、policy/world/value routing、32→16 action queue 和 RoboCasa controller 合同由 frozen upstream source 支持；本地 Project snapshot、训练脚本、报告和一组 CoffeePressButton base/trained action trace 可直接读取，但 checkpoint binary、metric denominator、完整 episode suite、local diff 与候选人逐项角色仍未闭合。当前可以讲“训练/评测协议迁移与失败诊断”，不能把 WAM architecture、历史 MSE/成功率或单 episode trace 说成个人原创、benchmark uplift 或已验证 checkpoint 结果。

## 0. 候选人项目范围自述（self-report，不等于 artifact/ownership 证明）

2026-07-21，候选人在本线程明确给出以下项目范围自述：

> “我复现了 Cosmos Policy 的 1 epoch fine-tune，做了 Cosmos Policy 的 eval，做了 UWM 在 LIBERO 的 fine-tune 和 eval，做了 UWM 在 RoboCasa 的尝试，协议对齐和训练评估；具体的指标与日志应该在对应项目下有落档。”

这条自述用于确定面试准备的项目覆盖面和 artifact 搜索优先级；它不自动证明具体代码 ownership、checkpoint lineage、指标分母、运行者或结果归因。当前安全映射如下：

| 自述范围 | 当前证据层 | 现在可用的安全动词 | 仍不能直接说 |
| --- | --- | --- | --- |
| Cosmos Policy 1 epoch fine-tune | `candidate-self-report` + 本地训练 gate / save-load audit 部分支持 | “开展/尝试复现 1-epoch 训练链，并审计训练 gate” | 已完成正式 1 epoch、拥有可加载 checkpoint、取得训练 uplift |
| Cosmos Policy eval | `candidate-self-report` + RoboCasa harness/diagnostic artifacts 部分支持 | “运行/审计 Cosmos Policy eval harness” | 个人模型 benchmark 成绩、官方 scorer 等价、相对 baseline 提升 |
| UWM / LIBERO fine-tune 与 eval | `candidate-self-report` + UWM/LIBERO protocol inventory | “开展 LIBERO 适配、训练与评估对齐” | strict/reset 结果归因、checkpoint ownership、250 episodes 全量闭合 |
| UWM / RoboCasa 尝试 | `candidate-self-report` + RoboCasa actionheadfix / transfer diagnostics | “尝试 RoboCasa 适配并做协议/失败诊断” | 已解决 root cause、完整成功率或稳定迁移结果 |
| 协议对齐与训练评估 | `candidate-self-report` + 多项目 protocol/evidence pages | “对齐输入输出、normalizer、controller、评估协议并复核日志” | 所有实现由候选人独立完成，或所有指标已经 result-owned |

在候选人逐项回答第 6 节 ownership questions 前，这五行保持 `candidate-self-report / role-pending`，不迁移为 `role-confirmed` 或 `result-owned`。

## 1. Ownership 证据合同

强主张“我负责并完成了 X”至少需要同时满足：文件/commit identity、可读取 artifact、设计或修改过程、运行/验收证据、个人/协作者/工具边界。Git author、项目报告、远端路径或一条 summary JSON 均不能单独证明个人 ownership。

| 状态 | 含义 | 当前可用动词 |
| --- | --- | --- |
| `upstream-verified` | frozen Cosmos paper/repo/model card 支持的公开机制或协议 | “上游定义/实现” |
| `snapshot-local` | Project Git snapshot 中存在脚本、配置、报告或输出 | “本地快照包含” |
| `artifact-local-partial` | 可读取 manifest/trace/video，但 checkpoint 或 protocol bundle 不完整 | “复核到诊断 artifact” |
| `report-supported` | 只有项目报告/历史材料支持 | “材料记录/项目描述” |
| `role-confirmed` | 候选人逐项确认亲手、协作、工具、运行或审查角色 | “我修改/我运行/我验收” |
| `result-owned` | checkpoint、normalizer、protocol、episode、scorer 与角色全部闭合 | “我完成并得到……” |

## 2. Git、上游与工作树冻结事实

| 检查 | 结果 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| Project HEAD | `6c524d9c6c6226075f100cdac395fef2fdc37671`，`Document RoboCasa actionheadfix diagnostics` | 当前提交包含 WAM/UWM 诊断报告和 loss summary | 每个文件由候选人独立设计、编写或运行 |
| Project initial snapshot | `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea` | 初始快照与 WAM 目录边界 | pre-snapshot 来源、协作者和工具链 |
| Cosmos/WAM training line | `wm/cosmos_policy_*` scripts、`cosmos_policy_deepspeed_train.py`、RoboCasa dataset/rollout scripts | 本地存在训练/推理适配入口与参数合同 | 正式 1-epoch、full10k 或 checkpoint ownership |
| RoboCasa evolution | `796374c` → `57bf4ea` → `a37a386` → `2a2912d` → `1a03fe` → `8eaddf` → `6c524d9` | actionheadfix、single-task gate、sharded eval、loss reports 经多次提交演化 | 每次修改由谁决定、谁在 remote 执行、谁验收 |
| Current worktree | `Project` 当前有 recovery 文件修改；WAM outputs 在外部目录 | working-tree 状态和外部 diagnostic 文件存在 | dirty recovery 或远端路径不等于可复算 raw run |
| Frozen upstream | `NVlabs/cosmos-policy@18a2accadf4e7a3531e56754102af5a24d2316da`；论文 arXiv `2601.16163v1` | latent slot、mask、routing、direct/planning、RoboCasa 32→16 合同 | 用户本地改动、结果、ownership 或 license 可自动继承 |

## 3. Per-file / per-decision ownership matrix

| ID | 文件 / 决策 | 当前可核验事实 | Git / artifact 事实 | 当前 role verdict | 安全口径 | 升级所需证据 |
| --- | --- | --- | --- | --- | --- | --- |
| `WAM-OWN-001` | Project initial snapshot 与 WAM 目录来源 | `c4469eb` 是根快照；包含 `wm/cosmos_policy_*` 与 RoboCasa 适配目录 | 一次性 snapshot；无 pre-snapshot history | `snapshot-local / role-pending` | “项目快照包含 Cosmos/WAM 训练与评测材料” | pre-snapshot 来源、贡献记录、候选人确认 |
| `WAM-OWN-002` | Cosmos Policy upstream mechanism | paper/repo 支持 unified latent video sequence、action/future/value slot、sample route、condition/loss mask | frozen commit `18a2acc…`；上游 Apache-2.0；model card 另有 NSCLv1 | `upstream-verified / upstream-only` | “我按 upstream contract 梳理/对齐”，不说原创 architecture | 永远不升级为个人原创；只绑定本地 substantive diff |
| `WAM-OWN-003` | `wm/cosmos_policy_deepspeed_train.py` 训练适配 | 参数包含 chunk=32、action multiplier、world/value sampling、normalization、DeepSpeed 与 dataset contract；代码是 proxy/objective-compatible harness | Project snapshot 可读；未闭合 full model run | `snapshot-local / implementation-role-pending` | “本地有 DeepSpeed 训练适配与目标合同” | before/after diff、运行命令、effective config、load/checkpoint log |
| `WAM-OWN-004` | RoboCasa dataset / action schema | `uwm_robocasa_lerobot_dataset.py`、`uwm_robocasa_dataset.py`、tasksets 固定图像/proprio/action/normalizer 与 7D→12D controller 边界 | 多次 `796374c`→`6c524d9` 提交 | `snapshot-local / decision-owner-pending` | “项目适配了 RoboCasa 数据与动作接口” | 数据 manifest、schema roundtrip、候选人具体改动和 review |
| `WAM-OWN-005` | action rollout launcher | `run_cosmos_policy_robocasa_action_rollout_now.sh`、`cosmos_policy_robocasa_action_rollout_video.py` 提供 32 chunk、16 open-loop、5 denoise 与 episode output | 入口脚本和日志可读取；远端 checkpoint path | `process-supported / operator-pending` | “项目提供可审计的 rollout launcher” | remote shell history、runtime env、完整 episode manifest、运行者 |
| `WAM-OWN-006` | official checkpoint / HF baseline eval path | wrapper、task list、controller、success predicate 与 24×5/50×3 协议在材料中可定位 | 上游 model card 数字不是本地运行；本地 historical 84/118 仍 claim-only | `upstream+report-supported / result-owner-blocked` | “我建立了 harness 验证路径”，不报历史分数为个人结果 | model revision、checkpoint/config/stats hash、raw episodes、summary/videos |
| `WAM-OWN-007` | training report / loss summary | `uwm_robocasa_transfer_report.html`、`human300_*` summary 与图表记录 action/aux/lr/memory 线索 | `6c524d9` 加入报告与 PNG/CSV/JSON；不是独立 raw checkpoint | `report-supported / analysis-role-pending` | “报告记录训练诊断线索” | run manifest、metric code、原始 logs、checkpoint lineage、审查角色 |
| `WAM-OWN-008` | WAM historical MSE claim `0.09718→0.05349` | 只出现在旧简历/项目叙事，缺 split、prediction/label、metric script | inventory 判定 `C3-BLOCKED / REMOVED` | `local-claim-only / result-blocked` | 当前不报数；只讲应如何建立 held-out metric bundle | split manifest、metric SHA、pred/label、checkpoint/config/stats SHA |
| `WAM-OWN-009` | historical success `0.90–0.95 / 0.75` 与 `84/118` | 历史材料中的 task/denominator/checkpoint 未闭合，且与 local 0-success 叙事存在 provenance conflict | inventory 判定 `CONFLICT / REMOVED` | `claim-only / protocol-blocked` | 不恢复到简历或强回答 | task IDs、trial/init/seed/horizon/controller、raw episodes、invalid rule、model revision |
| `WAM-OWN-010` | local 0-success / root-cause chain | 项目页提出 gripper、high-sigma、5-frame conditioning、normalizer/slot roundtrip、OOM/state_dict 等候选原因 | 未发现完整 fix→paired rerun 因果链 | `inference / diagnosis-pending` | “我列出并排序了诊断假设”，不说已定位根因 | failure trace、patch、unit test、修复后同协议 rerun |
| `WAM-OWN-011` | CoffeePressButton base/trained manifests | 两个 manifest SHA：base `63A518…33A86`、trained `809AE4…55CC`；同 task/episode/seed/env_seed/max_steps/open-loop/denoise；均 success=false | `C:\Users\mousongzhe\Project\wm\outputs` 可读；checkpoint 字段是远端路径 | `artifact-local-partial / checkpoint-unverified` | “复核到一组 paired diagnostic manifest” | checkpoint binary/immutable remote hash、processor/normalizer/config SHA、完整 suite |
| `WAM-OWN-012` | CoffeePressButton action trace 与 video | base trace SHA `C6A362…88525D`、trained trace SHA `9C6A4F…82CF2D`；300×7 policy、300×12 env、无 NaN/Inf；trained video SHA `591763…2877` | action trace MAE `0.3100783611`、RMSE `0.3906446459`；两边 episode 0 均失败 | `local-direct / diagnostic-only` | “trace 几何差异与失败字段可复核”，不称 uplift/MSE/benchmark | target/pred metric、controller roundtrip、多 episode denominator、same-checkpoint paired run |
| `WAM-OWN-013` | iter_000010000 matched path bridge 与个人总边界 | offline future metric 与 trained rollout 逐字引用同一 checkpoint path；path string SHA `6CAE0B…14E833` | 这是路径 fingerprint，不是 binary SHA；offline n=1，输入/seed/horizon 与 rollout 不同 | `local-direct / protocol-limited / candidate-confirmation-pending` | “我能把 offline 与 rollout 绑定到同一路径，但不能做相关/因果结论；个人 ownership 仍按前 12 行确认” | binary hash/load smoke、matched protocol、candidate role ledger、reviewer/operator 记录 |

## 4. Claim → ownership reconciliation

| 面试/简历 claim | 当前证据合同 | 安全处理 |
| --- | --- | --- |
| “我设计了 action/world/value 三目标与 slot routing” | 上游机制已核实，本地缺 substantive diff 与 ownership | 改为“按 upstream contract 梳理/对齐”；确认本地改动后再描述修改 |
| “我完成了 Cosmos/WAM 后训练” | 有训练适配入口与报告，但缺 immutable run/checkpoint/metric chain | 说“参与/开展训练适配与评测诊断”，不说完成正式训练结果 |
| “MSE 下降约 45%” | split、metric code、prediction/label、checkpoint 缺失 | 当前移除；补齐四类 artifact 后重新判定 |
| “RoboCasa 达到 0.90–0.95 / 0.75 或 84/118” | task/seed/trial/checkpoint/episode provenance 未闭合且存在冲突 | 禁止恢复；先建立 protocol-complete raw bundle |
| “trained action trace 比 base 更好/更差” | 只有单 episode trace 差异，checkpoint binary 未验证，两边 success 都 false | 只说 trace-level diagnostic，不做模型效果结论 |
| “我定位了 0-success 根因” | 目前是候选假设链，无修复前后 paired rerun | 说“形成诊断矩阵/优先级”，原因用“待确认” |
| “Git author 证明这些代码都是我写的” | 多次提交和一次性 snapshot 只能证明提交身份 | 必须按文件、commit、运行者和工具边界回答 |
| “iter_000010000 的 offline metric 解释了 rollout 失败” | 只证明 path string 相同；n=1 且 episode/seed/horizon 不同 | 只说 checkpoint-reference bridge，不做相关或因果结论 |

## 5. Production gap 与最小补证据

| Gap | 面试官追问 | 最小补证据 | 当前表达 |
| --- | --- | --- | --- |
| checkpoint lineage | base/trained 的权重和 normalizer 是什么？ | binary/remote content hash、processor、stats/config SHA、load smoke | `checkpoint-unverified` |
| metric contract | MSE 对哪些 action steps/dims 求平均？ | split manifest、metric script SHA、pred/label、valid denominator | `C3-blocked` |
| episode denominator | 84/118 为什么删 2 条？ | 预注册 invalid rule、逐 episode JSONL、视频与 scorer | `conflict` |
| action semantics | 7D policy 如何变成 12D controller action？ | schema、normalizer roundtrip、controller config/hash、timestamped trace | `diagnostic pending` |
| root cause | gripper/high-sigma/5-frame 谁被验证了？ | failure trace、patch、unit test、同协议 paired rerun | `inference` |
| ownership | 哪个函数是你亲手写/改的？ | before/after diff、review note、候选人逐项确认 | `role-pending` |
| offline→online bridge | PSNR/SSIM 能否预测 success？ | matched task/init/seed、同 checkpoint、多样本 paired bundle | 当前只能说 path bridge |
| collaboration/tool boundary | Codex/同事/远端运行者分别做了什么？ | contribution ledger、shell history、operator/reviewer 记录 | 不推断 |

## 6. 候选人确认表

真实口述或材料核对时，请逐项回答“亲手 / 协作 / 工具辅助 / 只审查 / 只运行 / 不确定”：

1. `c4469eb` 初始 snapshot 中的 WAM/Cosmos 文件来自哪里？哪些是在 `796374c` 之后由你修改？
2. `cosmos_policy_deepspeed_train.py` 的 proxy/objective-compatible 训练适配由谁设计、编写、运行和验收？
3. RoboCasa dataset、7D→12D action、normalizer、camera 与 taskset contract 中哪些字段是你的决策？
4. action rollout launcher 与 official/HF baseline harness 谁编写、谁在 remote 执行、谁检查 success predicate？
5. historical MSE、84/118、0.90–0.95/0.75、full10k 分别属于哪条 run？checkpoint、split、denominator 和运行者是什么？
6. CoffeePressButton base/trained manifest、action trace、video 是谁生成、收集、审查和保存的？
7. gripper、high-sigma、5-frame conditioning、normalizer/slot roundtrip、OOM/state_dict 中哪些有修复后的 paired rerun？
8. 哪些代码来自 NVlabs upstream、哪些来自协作者或工具，哪些 substantive diff 确实由你亲手完成？

在候选人真实回答前，不创建 `coaching_state.md`，不把任何行升级为 `role-confirmed` 或 `result-owned`。

## 7. 两分钟叙事骨架（当前安全版）

> Cosmos/WAM 这条线我会拆成上游机制、训练适配、评测协议和诊断四层。上游 Cosmos Policy 把 action、future、value 放进统一 latent sequence，通过 condition/loss mask 和 sample routing 切换 policy/world/value 角色；这部分属于上游，不是我的原创。我的项目材料与 Project snapshot 可以核验 DeepSpeed 训练适配、RoboCasa 数据/动作接口、32→16 open-loop rollout 和多轮 actionheadfix 诊断。现在最强的本地证据是一组 CoffeePressButton episode 0 的 base/trained manifest、300×7 action trace、失败视频和逐步差异计算；但两侧 checkpoint 仍是远端路径，只有 path fingerprint，不能证明 binary 内容或 uplift。历史 MSE 和成功率没有完整 split、denominator、episode、checkpoint 链，已从安全简历口径移除。我的个人贡献需要按 ledger 的脚本、提交、命令和验收记录逐项确认，因此当前我会把它讲成协议迁移与失败诊断，而不是已验证的 benchmark 提升。

## 8. 面试前 6 题

1. 为什么 Cosmos Policy 不能简单描述成 video backbone 后面接 action/world/value 三个独立 head？
2. `mask=1` 在 Cosmos dataset/training contract 中表示什么？它和 attention mask 有何区别？
3. 为什么 RoboCasa 的 7D policy action 会变成 12D controller action，且只执行 32-step chunk 的前 16 步？
4. 单 episode base/trained action MAE/RMSE 能证明 checkpoint uplift 吗？缺哪些证据？
5. 为什么 offline future-image metric 与 rollout success 不能直接做相关或因果解释？
6. 请从 `cosmos_policy_deepspeed_train.py` 或 action rollout launcher 的一个函数开始，说明哪些是你亲手、协作、工具辅助、只审查或只运行的。

## 参考文献（References）

1. [Cosmos/WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)：历史 claim、冲突、artifact gate 与安全口径。
2. [WM-019 WAM Diagnostic Artifact Manifest](wm019_wam_artifact_manifest.html)：CoffeePressButton manifest、trace、video 和 checkpoint 缺口。
3. [WM-019 WAM Action-Trace Paired Diagnostic](wm019_wam_action_trace_paired_diagnostic.html)：300×7/300×12 trace integrity 与 MAE/RMSE 边界。
4. [WM-019 Matched-Checkpoint Protocol Bridge](wm019_wam_matched_checkpoint_protocol_bridge.html)：iter_000010000 path bridge 与 n=1/协议差异。
5. [Cosmos Policy / WAM Source Audit](../../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：frozen upstream mechanism、slot/mask/routing 与 RoboCasa contract。
6. [Cosmos/WAM Project Page](../../../04_cosmos_wam_multitask_training.html)：项目叙事与历史问题树；不替代 raw evidence。

## 9. Ownership 审计伪代码

```python
def accept_wam_claim(claim, ledger):
    # Upstream mechanism is not personal ownership.
    if claim.is_upstream and not ledger.local_diff(claim):
        return "upstream_only"
    # A metric requires protocol, checkpoint and raw outputs, not a report number.
    if claim.level >= "C2" and not ledger.protocol_checkpoint_raw_chain(claim):
        return "downgrade_to_claim_only"
    # Personal result language waits for explicit role and verification evidence.
    if not ledger.role_confirmed(claim) or not ledger.verification(claim):
        return "candidate_confirmation_pending"
    return "claim_allowed_with_exact_scope"
```

这段伪代码是本仓库的 ownership gate，不是 Cosmos/WAM 官方实现。
