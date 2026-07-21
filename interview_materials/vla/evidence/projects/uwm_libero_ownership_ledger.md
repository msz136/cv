# UWM / LIBERO Ownership Ledger：协议迁移、数据管线与结果边界

> 状态：`ownership_audited / coarse_git_supported / candidate_confirmation_pending / WARN`
> 审查日期：2026-07-21
> 证据截止：2026-07-21
> 项目范围：`C:\Users\mousongzhe\Project` 中的 UWM/LIBERO official repro、RoboCasa transfer、DataLoader stall diagnosis、strict/reset recovery 与用户确认结果。
> 结论先行：本地可以核验 LIBERO task mapping、finetune/rollout launcher、`pruned_init`/warmup 协议、DataLoader-only smoke，以及RoboCasa actionheadfix一条30-epoch run的8×54 raw rollout；但 project snapshot 是一次性快照，RoboCasa 路径经历多次同步。当前 `mousongzhe` 提交证明的是候选账号提交了这些 artifact，不证明每个函数由候选人独立设计、编写、运行或验收。LIBERO `186/250` 仍是用户确认summary；RoboCasa raw denominator虽已存在，produced checkpoint binary/hash、env/scorer/videos与个人角色仍未闭合。

## 0. 候选人项目范围自述（self-report，不等于 artifact/ownership 证明）

2026-07-21，候选人在本线程明确表示：

> “做了 UWM 在 LIBERO 的 fine-tune 和 eval，做了 UWM 在 RoboCasa 的尝试，协议对齐和训练评估。”

这条自述用于把 UWM 两条线纳入面试准备和 artifact 搜索范围；它不自动证明具体代码 ownership、checkpoint lineage、严格/重置协议下的结果归因，或 RoboCasa 的 root cause。当前安全映射如下：

| 自述范围 | 当前证据层 | 现在可用的安全动词 | 仍不能直接说 |
| --- | --- | --- | --- |
| UWM / LIBERO fine-tune | `candidate-self-report` + local launcher/protocol inventory | “开展 LIBERO 适配与 fine-tune 训练链对齐” | 独立设计 UWM architecture、拥有可加载 checkpoint、结果已 result-owned |
| UWM / LIBERO eval | `candidate-self-report` + strict/reset/Table II protocol evidence | “运行/审计 LIBERO 评估协议” | 把 strict、reset-style、Table II 结果混成一个分数，或把用户确认数字写成 raw 本地结果 |
| UWM / RoboCasa 尝试、协议对齐与训练评估 | `candidate-self-report` + actionheadfix/raw rollout 与诊断部分支持 | “尝试 RoboCasa 迁移、对齐 action/normalizer/controller/eval contract 并做训练诊断” | 已定位 root cause、完整成功率、checkpoint/env/scorer ownership |

在候选人逐项回答本页 ownership questions 前，这三行保持 `candidate-self-report / role-confirmation-pending`，不迁移为 `role-confirmed` 或 `result-owned`。

## 1. 问题（Question）

面试官问“UWM/LIBERO 哪些是你做的？”时，要拆开：

1. UWM shared diffusion 与 LIBERO benchmark 的上游机制；
2. 本地 snapshot 中的迁移脚本、patch、配置、报告和诊断 artifact；
3. 候选人亲手设计、修改、运行、审查或验收的动作；
4. 上游 repo、远端运行者、协作者和工具辅助的边界；
5. checkpoint、normalizer、episode trace、success summary 与论文比较的归属。

本页不是把项目页中的“负责/迁移”自动认证为个人贡献。没有候选人逐项确认或过程证据的行保持 `role-confirmation-pending`。

## 2. Role Fit 与 JD 能力映射

| 岗位能力 | 本地可核证据 | Ownership 强度 | 当前策略 |
| --- | --- | --- | --- |
| VLA/VLM 训练迁移 | LIBERO-90→LIBERO-10 finetune launcher、DDP patch、task map、checkpoint path contract | local-direct；个人动作待确认 | 可讲训练/评估接口迁移，不说原创 UWM architecture |
| Policy rollout / benchmark protocol | fixed-pruned-init、5-step warmup、50 rollouts/task、success summary | local-direct / user-confirmed final | 先绑定 init/seed/normalizer/horizon/scorer，再说数字 |
| 数据管线工程 | Zarr/HDF5 buffer、infinite sampler、preload、workers/prefetch/pin 与 stall benchmark | local-direct；full GPU A/B 缺 | 可讲 DataLoader diagnosis，不承诺训练吞吐 uplift |
| 跨 benchmark 适配 | RoboCasa action/state/prompt/normalizer/eval patches、30-epoch train log与8×54 raw rollout | local-direct / remote-snapshot-raw | 讲train→closed-loop failure，不写RoboCasa benchmark success |
| 结果与可比性 | 0.744、0.928、Table II≈0.79 的 protocol reconciliation | user-confirmed/report-supported；C3 未闭合 | 不把 0.744 写成本地 raw verified 或严格论文复现 |

## 3. Ownership 证据合同

### 3.1 五层 AND-gate

强主张“我负责并完成了 X”至少需要：

\[
G(c)=I(c)\land A(c)\land D(c)\land V(c)\land O(c).
\]

`I` 是 file/commit/run identity，`A` 是 artifact，`D` 是设计与修改过程，`V` 是运行/验收，`O` 是个人、上游、协作者和工具边界。commit author、项目 report、远端 path 和一个 summary JSON 都只能覆盖部分层级。

### 3.2 状态词汇

| 状态 | 含义 | 可用动词 |
| --- | --- | --- |
| `upstream-verified` | frozen UWM/LIBERO source audit 支持的公开机制/协议 | “上游定义/论文使用” |
| `snapshot-local` | 本地 Git snapshot 中存在文件或报告 | “本地快照包含” |
| `git-coarse` | 候选账号提交，但没有逐文件历史 | “候选账号提交了快照” |
| `self-attested` | 简历/项目页自述本人负责 | “候选人自述负责” |
| `role-confirmed` | 候选人逐项确认亲手/协作/工具/运行角色 | “我负责/我修改” |
| `result-owned` | checkpoint、normalizer、protocol、episodes、scorer 与角色闭合 | “我完成并得到……” |

## 4. Git、工作树与 run lineage 冻结事实

### 4.1 Project history

| 检查 | 结果 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| 当前 HEAD | `6c524d9c6c6226075f100cdac395fef2fdc37671`，2026-07-02；author/committer `mousongzhe` | 当前 committed snapshot 的提交身份 | 每个文件由候选人独立完成 |
| 初始 Project snapshot | `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`，root commit | 初始项目材料一次进入 Git；UWM official repro 当时尚不存在 | 初始文件来源、协作者和生成顺序 |
| UWM official repro recovery | `0341c5016a63c4160a9027e5c333a33ce880bd1d`；21 files / 3,784 additions | 18 个 `uwm_libero_official_repro` 路径和 recovery report 在候选账号提交中进入 | 远端训练/rollout 是否由候选人执行，逐行 ownership |
| RoboCasa transfer evolution | `796374c`、`57bf4e`、`a37a386`、`2a2912d`、`1a03fe`、`8eaddf`、`6c524d9` | 路径经历多次候选账号提交和诊断迭代 | 每次修改的设计者、运行者、reviewer |

### 4.2 Current worktree boundary

`Project` 当前不是 clean worktree：`report/uwm_libero_strict_eval_recovery_20260702/sync_manifest.json` 与 `sync_summary.md` 有未提交修改，`final_strict_eval_user_confirmed_20260705.json` 是未跟踪文件。这个状态能证明“当前工作区保存了 recovery/user-confirmed material”，不能证明它们已经进入 HEAD，也不能把用户确认 JSON 变成本地 raw episode bundle。

### 4.3 Result artifact boundary

当前没有本地 5-task checkpoint、normalizer hash、250 条 episode JSONL、失败视频、逐样本 scorer 或完整 remote log。因此：

- `local-direct`：脚本、patch、静态报告、DataLoader-only smoke 和 Git blob；
- `report-supported`：项目 report 中的 Book-Caddy 42/50、路径和诊断叙事；
- `user-confirmed-remote-final`：用户确认的 186/250 及 per-task summary；
- `protocol-limited`：fixed-pruned-init、reset-style 与 Table II OOD 之间的数字；
- `remote-snapshot-raw`：RoboCasa actionheadfix同一run的train log、normalizer与8×54 raw rollout；
- `result-owned`：当前未达到，不能说候选人拥有 0.744 的 checkpoint/result。

## 5. Per-file / per-decision ownership matrix

| ID | 文件 / 决策 | Local artifact 事实 | Git / run 事实 | 当前 role verdict | 当前安全口径 | 升级所需证据 |
| --- | --- | --- | --- | --- | --- | --- |
| `UWM-OWN-001` | Project initial snapshot 与 UWM/RoboCasa 路径来源 | `c4469eb` 是 root snapshot；当时 `uwm_libero_official_repro` 不存在，RoboCasa transfer 有 50 个初始路径 | author `mousongzhe`；无 pre-snapshot history | `snapshot-local / git-coarse / role-pending` | “项目快照包含 UWM/RoboCasa 相关材料” | pre-snapshot 来源、协作者/工具记录、候选人逐项确认 |
| `UWM-OWN-002` | `scripts/libero_official_common.py` task map / shape contract | 五 task、HDF5/BDDL/pruned-init/buffer、RGB `[128,128,3]`、LIBERO action `[7]`；SHA `DE9D…7E2B` | 87 行在 `0341c50` 一次进入 | `local-direct / decision-owner-pending` | “本地 adapter 固定了 task 与 shape 合同” | 为什么选这些字段、原始 upstream diff、运行命令、review |
| `UWM-OWN-003` | `scripts/uwm_libero_rollout_eval.py` strict/reset evaluator | `uwm_reset` 与 `libero_fixed_init`、5-step warmup、seed/init/checkpoint/horizon/summary；SHA `05E9…F3943` | 211 行在 `0341c50` 一次进入 | `local-direct / process-role-pending` | “本地实现了可审计 rollout protocol” | 亲手函数、same-checkpoint paired run、episode trace、scorer tests |
| `UWM-OWN-004` | 5-task rollout launcher | 8 shard、50 rollouts/task、600-step/manifest/output-root contract；SHA `C61C…EE32` | 270 行在 `0341c50` 一次进入 | `local-direct / operator-pending` | “项目提供 5-task rollout launcher” | remote shell history、运行者、完整 output manifest、失败重试记录 |
| `UWM-OWN-005` | 5-task finetune launcher + DDP path | LIBERO-90 checkpoint、5 task、DDP、batch/steps、output checkpoint contract；SHA `E5B6…9D92` | 101 行在 `0341c50` 一次进入 | `local-direct / role-pending` | “本地组织了 LIBERO finetune path” | base checkpoint/normalizer、effective config、train log、候选人改动点 |
| `UWM-OWN-006` | `prepare_libero_buffers.py` 与 dataset buffer route | HDF5/BDDL → compressed Zarr buffer 的准备脚本；SHA `2517…4E8A` | 106 行在 `0341c50` 一次进入 | `local-direct / data-owner-pending` | “项目建立了 LIBERO buffer preparation path” | 数据来源、过滤/切分决策、运行输出、hash manifest |
| `UWM-OWN-007` | DataLoader stall benchmark | finite/infinite/preload A/B；p95 wait 13.862s→0.194s；SHA `47A2…6B36` | 141 行在 `0341c50`；DataLoader-only，不是 GPU training | `process-supported / verification-role-pending` | “我定位了数据等待路径的候选原因”需候选人确认 | benchmark command、raw timing、memory/throughput matched GPU smoke |
| `UWM-OWN-008` | `repo_patch/datasets/utils/loader.py` + sampler | infinite sampler、workers/prefetch/pin；loader SHA `FC8E…3551`，sampler SHA `6B45…DA95` | patch 在 `0341c50`；无 upstream before/after provenance | `snapshot-local / implementation-role-pending` | “本地 patch 包含 preload/infinite loader 选项” | upstream diff、亲手/协作/工具边界、unit test、full run验证 |
| `UWM-OWN-009` | `repo_patch/experiments/uwm/train_robomimic.py` 与 `train.py` | pretrain load、num_steps、rollout hooks、timing；train_robomimic SHA `8423…40BD` | 228 行 patch 在 `0341c50`，无逐函数历史 | `snapshot-local / role-pending` | “项目 patch 扩展了训练与 rollout hooks” | patch 来源、代码 review、实际执行命令、checkpoint load |
| `UWM-OWN-010` | `sync_manifest.json` / `sync_summary.md` recovery | 记录 remote host、script hashes、strict/reset 差异；当前文件已被工作树修改 | committed blob 与 current SHA 不同；final JSON 未跟踪 | `working-tree / report-editor-pending` | “当前工作树保存了 recovery note” | 谁修改、SSH/raw output、manifest commit、reviewer确认 |
| `UWM-OWN-011` | `final_strict_eval_user_confirmed_20260705.json` | user-confirmed per-task 0.88/0.80/0.76/0.66/0.62，186/250=0.744；当前 SHA `7616…6D11` | 未跟踪文件；result source 明确为 user-confirmed remote final | `user-confirmed-remote-final / result-owner-blocked` | “用户确认的 fixed-pruned-init summary” | checkpoint/normalizer/init/episode/scorer bundle、运行/审查角色 |
| `UWM-OWN-012` | RoboCasa transfer patch/actionhead diagnostics | train/rollout code、30-epoch train log、12D normalizer与8×54 raw JSON；full-h4 `0/54`/contact `45/54`；train SHA `EFC5…1FFE` | `796374c`→`6c524d9`迭代；remote_sync cache非committed result bundle | `remote-snapshot-raw / checkpoint-unverified / role-pending` | “参与跨 benchmark contract 调试并审计train→closed-loop断层” | upstream diff、produced checkpoint SHA/fresh-load、env/scorer/videos、候选人/远端运行者确认 |
| `UWM-OWN-013` | UWM shared diffusion / LIBERO benchmark method | source audits 支持 shared action/video diffusion、独立 timestep、LIBERO protocol 与 Table II OOD | upstream revisions `b7d4067…` / `8f1084e…`；不属于本地原创 | `upstream-verified / upstream-only` | “基于/对照 UWM 与 LIBERO 上游方法” | 永远不升级为个人原创；只确认适配、迁移或复现工作 |

## 6. Claim → ownership reconciliation

| 面试/简历 claim | 当前证据合同 | 安全处理 |
| --- | --- | --- |
| “我迁移并完成 UWM/LIBERO 训练闭环” | scripts/patch/report direct；远端 train/checkpoint/operator/role 未闭合 | 候选确认前用“项目包含/参与迁移”；确认后绑定具体文件和命令 |
| “我取得 LIBERO 5-task 74.4%” | 0.744 是 user-confirmed remote final，无本地 checkpoint/episodes | 说“用户确认的 fixed-pruned-init summary”，不说 local raw verified |
| “74.4% 复现官方 0.79” | init/shift/background/seeds/scorer 不同，inventory 判定 NON_COMPARABLE | 禁止“严格复现/只差4.6pp”作为强结论 |
| “0.928 说明模型成功率更高” | reset-style 与 fixed-pruned-init 协议不同 | 只说 protocol sensitivity diagnostic |
| “我解决了 DataLoader 性能问题” | DataLoader-only p95 A/B 有直接证据；GPU throughput/memory 未验证 | 说“定位并验证 DataLoader-only wait 降低”，不报训练吞吐 uplift |
| “RoboCasa benchmark 已完成” | 有一条8×54 raw success bundle但只有项目协议、无produced checkpoint/env-scorer/videos | 保持`protocol-bounded`，讲跨benchmark train→closed-loop failure |
| “UWM architecture 是我设计的” | source audit 指向 upstream shared diffusion mechanism | 明确上游；个人贡献只落在迁移、协议、诊断和验收 |
| “Git author 证明所有代码是我写的” | 一次性 snapshot + 多次同步；无逐文件 provenance | 用 13 行 ledger 区分 snapshot、self-attested、role pending 和 upstream |

## 7. Production Gap：抗追问最小补证据

| Gap | 面试官追问 | 最小补证据 | 当前表达 |
| --- | --- | --- | --- |
| 快照来源 | `c4469eb` 之前代码从哪来？ | pre-snapshot source/patch/contributor record | `git-coarse` |
| trainer ownership | 哪个函数是你亲手改的？ | before/after diff、review note、现场解释 | `role-pending` |
| checkpoint/normalizer | 0.744 用的权重和 normalizer 是什么？ | binary/config/normalizer hash + load smoke | `user-confirmed-remote-final` |
| episode evidence | 186/250 的 250 个 episode 在哪？ | per-episode JSONL/video/terminal reason/scorer | `raw bundle missing` |
| protocol comparison | 为什么不和 0.79 直接比？ | exact init/seed/shift/background/scorer manifest | `NON_COMPARABLE` |
| DataLoader diagnosis | preload 是否提高完整训练吞吐？ | 30–100 step GPU matched A/B、memory、data_wait/train/total | `smoke-bounded` |
| RoboCasa result | actionheadfix 后 success 多少？ | 8×54 raw JSON已存在；仍需checkpoint SHA/fresh-load、env/scorer/videos和repeat | `raw-rollout-backed / result-owner-blocked` |
| tool/collaboration | 哪些由协作者或 AI 辅助？ | contribution ledger、review记录、运行者名单 | 不推断 Codex-primary |

## 8. Question Tree 与回答分层

```text
你个人做了什么？
  ├─ 训练：LIBERO-90→LIBERO-10 的 launcher、patch、normalizer 和 checkpoint contract 哪些是你改的？
  ├─ 评估：fixed-pruned-init、reset-style、Table II OOD 的 tuple 如何冻结？
  ├─ 数据：zarr 小 chunk 的 first failure、preload/infinite 的验证范围是什么？
  ├─ 结果：0.744 的 checkpoint、250 episodes、scorer 和运行者在哪？
  └─ 归属：UWM architecture、上游 patch、协作者、工具和你自己的动作如何分开？
```

**危险回答**：说“我把 UWM 完整复现了，74.4% 就是我的 benchmark 结果，Git author 证明所有 patch 都是我写的”。

**可过回答**：我把贡献拆成迁移、协议、数据管线和诊断。LIBERO 186/250仍是用户确认summary；RoboCasa一条30-epoch run已有8×54 raw rollout，可讲full-h4 `0/54`和contact `45/54`的失败断层，但checkpoint/env-scorer/ownership仍未闭合。UWM architecture属于上游，我的具体ownership按文件、命令、远端运行和验收记录回答。

**强回答（补证后才可用）**：我能从一个具体 launcher/patch 说明输入、改动、失败、验证和输出 manifest，并给出同 checkpoint paired protocol、normalizer hash、episode JSONL 和 scorer；对不能闭合的部分主动降级为 report-supported 或 user-confirmed。

## 9. SP/SSP 证据就绪度

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.5 | VLA 训练迁移、闭环 rollout、benchmark protocol 和数据管线高度相关 |
| 机制深度 | 4.0 | shared diffusion、task map、init/warmup、normalizer、stall diagnosis 可解释 |
| 工程闭环 | 3.7 | scripts/patch/report与RoboCasa 8×54 raw齐；produced checkpoint/load/env-scorer/videos仍缺 |
| 指标可信度 | 2.5 | LIBERO 0.744 user-confirmed；RoboCasa raw denominator可复算但协议/权重未闭合 |
| Ownership 清晰度 | 2.0 | 13-row ledger 建立；逐文件、工具、运行者确认 pending |
| 抗追问能力 | 3.0 | protocol boundary 强；结果和个人实现仍有断点 |
| 合计 | **19.7 / 30** | 证据就绪度，不是候选人能力评分；项目保持 WARN |

## 10. 候选人确认表

请逐项回答“亲手 / 协作 / 工具辅助 / 只审查 / 只运行 / 不确定”：

1. `c4469eb` 初始 snapshot 中的 UWM/RoboCasa 文件来自哪里？`0341c50` 的 official repro 由谁设计、实现和 review？
2. `libero_official_common.py` 的五 task、shape、pruned-init 和 buffer 选择是谁决定的？
3. `uwm_libero_rollout_eval.py` 中 strict/reset、warmup、seed/init、horizon 和 summary 逻辑哪些由你修改？
4. finetune/rollout launcher 与 `train_robomimic.py` patch 谁编写、谁在 remote 执行、谁验收 checkpoint？
5. DataLoader stall benchmark 与 loader/sampler patch 的 first failure、修改和 matched validation 是什么？
6. 0.744 的 checkpoint、normalizer、250 episodes 和 scorer 由谁生成、保管、审查？
7. RoboCasa actionheadfix、dataset、rollout 和 loss report 中哪些是你亲手、协作或工具辅助？
8. UWM shared diffusion architecture 与 LIBERO Table II 哪些明确属于上游，你的个人贡献如何界定？

在真实回答发生前，不创建 `coaching_state.md`，不把任一行升级为 `role-confirmed` 或 `result-owned`。

## 11. 分阶段补强计划

| 阶段 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 完成 8 项 ownership drill；每个关键脚本选一个现场解释点 | 13 行均有 role/source/verification | 待候选人确认 |
| 1 天 | 将 committed sync manifest、工作树 recovery 和 user-confirmed JSON 标成不同 lineage | final result 不再依赖单个 summary/path | 待补做 |
| 3 天 | 获取 checkpoint/normalizer/init/episode/scorer，做 load smoke 与 same-checkpoint paired protocol | 0.744 至少形成可复算 C3 bundle | 待补做 |
| 1 周 | 做 30–100 step GPU DataLoader matched A/B，并为 RoboCasa 建 action/state/normalizer/eval manifest | stall 诊断与跨 benchmark 迁移均有可验证闭环 | 待补做 |

## 12. Output Pack

### 12.1 简历 bullet 三档

- **当前保守版**：参与 UWM/LIBERO 训练与 rollout 迁移、固定 strict/reset 评估协议、定位 Zarr/DataLoader stall，并整理用户确认的 fixed-pruned-init 结果及不可比性边界。
- **候选确认后标准版**：负责指定 UWM/LIBERO launcher、协议开关、数据管线诊断和评估验收；以文件/commit/命令说明个人、协作与上游边界。
- **补齐 C3 后偏强版**：在 checkpoint、normalizer、episode、scorer 和 paired protocol 完整后，给出可复算的 LIBERO 结果与 GPU stall A/B；当前禁止提前使用。

### 12.2 两分钟叙事骨架

> UWM 项目我主要做的是训练到闭环评估的协议工程：LIBERO侧固定task map、pruned-init、warmup、normalizer和success tuple，并用DataLoader-only smoke定位zarr等待；`186/250`仍是用户确认summary，不能与Table II直接横比。RoboCasa侧有一条actionheadfix 30-epoch raw sweep：8卡训练完成，同checkpoint的8×54 rollout都无env error但只有0–2 success，full-h4 `0/54`且contact `45/54`，所以定位为train→closed-loop failure。UWM架构属于上游；我的具体贡献按脚本、命令、远端运行和验收记录逐项确认。

### 12.3 面试前 6 题

1. fixed-pruned-init、reset-style、UWM Table II OOD 三种评估 tuple 分别是什么？
2. 为什么 `0.928→0.744` 主要应解释为 protocol gap，而不是模型权重退化？
3. `libero_official_common.py`、rollout evaluator 与 finetune launcher 如何串成一条 lineage？
4. Zarr preload/infinite 为什么能降低 DataLoader-only p95 wait？怎样证明 GPU training 也受益？
5. RoboCasa action/state/prompt/normalizer/eval contract 的 first-failure 如何定位？
6. 哪些是 UWM/LIBERO 上游，哪些文件/决策是你亲手、协作、工具辅助、只运行或只审查？

## 13. Ownership 审计伪代码

```python
def accept_uwm_claim(claim, ledger):
    if not ledger.identity_and_artifact(claim):
        return "reject_strong_claim"
    if not ledger.role_confirmed(claim):
        return "use_snapshot_or_user_confirmed_wording"
    if claim.level >= "C2" and not ledger.process_and_verification(claim):
        return "downgrade_to_migrated_or_reviewed"
    if claim.level == "C3" and not ledger.checkpoint_protocol_episode_chain(claim):
        return "report_or_user_summary_only"
    return "claim_allowed_with_exact_scope"
```

这段伪代码是本仓库真实性 gate，不是 UWM 官方实现。

## 参考文献（References）

1. [UWM / LIBERO Claim–Evidence Inventory](uwm_libero_claim_evidence_inventory.html)：12 条 claim、strict/reset、DataLoader 和 RoboCasa 边界。
2. [UWM 项目题卡](../../questions/proj_uwm.html)：当前 `PROJ-UWM-001` protocol-boundary card；本 ledger 将新增 ownership card。
3. [Evidence Manifest](../evidence_manifest.html)：五项目 evidence 与 ownership 状态总索引。
4. [VLA Knowledge Map](../../knowledge/00_vla_knowledge_map.html)：VOL 07 项目深挖与题目 ID 空间。
5. Local Git repository `C:\Users\mousongzhe\Project`，HEAD `6c524d9c6c6226075f100cdac395fef2fdc37671`；official repro `0341c5016a63c4160a9027e5c333a33ce880bd1d`；RoboCasa evolution `796374c`→`6c524d9`。
6. `wm/uwm_libero_official_repro/scripts/uwm_libero_rollout_eval.py` SHA-256 `05E912C2096EFF4BFE8D061E4C334517B03DE80847793D83025A2AA3E18F3943` 与 `scripts/libero_official_common.py` SHA-256 `DE9DB94113554DB50B151900647E6D32BFFB9649C7F4D1D97EA0D65A8A937E2B`。
7. [UWM benchmark evidence audit](../../sources/vol_04_benchmark_evidence_claim_to_protocol.html) 与 [UWM video/action audit](../../sources/vol_04_uwm_video_action_claim_to_code.html)：上游/本地机制和 Table II 协议边界。
8. [Optimized Resume](../../../../output/mousongzhe_resume_optimized.html) 与 [UWM 项目面试页](../../../05_uwm_libero_eval_protocol.html)：候选人自述和投递口径，未经本 ledger 自动认证。
9. [UWM RoboCasa ActionHeadFix 30-Epoch P0 Audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)：run-specific raw rollout与checkpoint/ownership边界。
