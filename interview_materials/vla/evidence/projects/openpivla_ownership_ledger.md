# OpenPiVLA Ownership Ledger：个人贡献、文件归属与面试口径

> 状态：`ownership_audited / coarse_git_supported / candidate_confirmation_pending / WARN`
> 审查日期：2026-07-19
> 证据截止：2026-07-19
> 项目范围：`C:\Users\mousongzhe\Project\openpivla_deployment`、OpenPI frozen upstream、当前简历和 OpenPiVLA 项目题卡。
> 结论先行：本地 Qwen3-VL/LoRA trainer、JSON action route、recipes、smoke、deployment/eval scripts 与报告均有可读取的 local-direct 证据；但它们一次性进入一个 1326-path 的初始仓库快照，OpenPiVLA 自身没有更早的逐文件 Git 历史。因此当前可以证明“本地快照包含一套区别于 frozen upstream 的实现”，不能仅凭 commit author 证明每个文件由候选人独立设计、编写和运行。个人 ownership 仍需候选人逐项确认，并补 before/after diff、设计记录、运行日志或协作说明。

> 2026-07-19 evidence update：[`OpenPiVLA JSON/CE + H/D Shape Contract Artifact Gate`](../../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.html) 已直接复核 `formal_train.py` 的 `limit=16` serializer、`H=15,D=72` recipe/smoke 与 AST formatter probe。它强化了 `OPV-OWN-002/003` 的技术事实与风险发现，但不改变个人 role-confirmation-pending、checkpoint lineage 或 benchmark ownership 状态。

> 2026-07-19 parser/round-trip update：[`Action JSON Parser / Round-trip Gate`](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html) 证明 Python JSON 只可逆恢复 `15×16` retained prefix、相对 `15×72` 丢 840 positions；formal package 没有 action-output parser，collator 是 full-sequence CE。`pi0_aloha_sim` 的 7D/4-step official WebSocket artifact 是平行 lineage。技术风险已复核，但谁设计/发现/修复仍由候选人确认。

## 1. 问题（Question）

面试官问“OpenPiVLA 哪部分是你做的？”时，应该怎样把以下五件事分开：

1. OpenPI / FAST 的公开上游设计；
2. 本地仓库中确实存在的代码、配置、脚本和报告；
3. 候选人亲手实现、修改、调试或验收的动作；
4. 协作者、历史归档或工具辅助产生的部分；
5. benchmark 数字、checkpoint 和闭环结果的归属。

本页是 ownership ledger，不是重新认领项目，也不是对 97.4% 的结果升级。没有候选人确认或独立过程证据的条目一律保持 `role-confirmation-pending`。

## 2. Role Fit 与 JD 能力映射

当前没有具体 JD，因此只映射通用 VLA / Robot Policy / Multimodal Training / Embodied Evaluation 岗位。

| 岗位能力 | 本地可核证据 | Ownership 强度 | 当前策略 |
| --- | --- | --- | --- |
| 多模态训练适配 | Qwen3-VL loader、PEFT LoRA、chat template、causal CE、adapter save path | 文件事实强；个人角色待确认 | 面试先解释输入、label、loss、保存语义，再说明个人动作 |
| VLA action representation | action window → compact JSON；`H=15,D=72` 与 formatter `limit=16` 冲突 | 文件事实强；设计决策 ownership 未证实 | 用“采用/实现该路线”替代“发明新 action tokenizer” |
| 数据与 recipe 工程 | VLA-only、VLM-only、co-train recipes/configs/scripts；public smoke manifests | local-direct；full-data 与个人决策部分未闭合 | 可讲 schema、mixture、public/private 边界，不把 smoke 当 formal result |
| 国产算力迁移 | MACA/C500 runtime、eager path、remote layout、formal report | report-supported；raw remote run 与个人操作记录不足 | 可讲迁移问题和验收设计，不写硬件带来算法提升 |
| Policy serving / evaluation | ALOHA、LIBERO、LeRobot action eval scripts 与 artifacts | local-direct；主要绑定 official checkpoint | 可讲 eval engineering，不绑定 formal Qwen 或 97.4% |
| 实验与结果 | formal report、smoke summaries、archive table | summary/report 层；C3 与 ownership 均未闭合 | 禁止“本人训练并超过官方” |

## 3. Ownership 证据合同

### 3.1 五层 AND-gate

一个“我负责并完成了 X”的强主张，至少需要五类证据共同成立：

\[
G(c)=I(c)\land A(c)\land D(c)\land V(c)\land O(c).
\]

变量解释：`I` 是 identity，证明审查的是哪个文件、commit、run 或 checkpoint；`A` 是 artifact，证明实现或结果实体存在；`D` 是 decision/process provenance，证明为什么这样做、由谁决定和如何修改；`V` 是 verification，证明候选实现被运行或验收；`O` 是 ownership boundary，证明个人、协作者、工具和上游各承担什么。直觉上，Git author 只覆盖 `I` 的一部分，代码存在只覆盖 `A`，两者都不能替代 `D/V/O`。实现映射是 `git log/diff`、源码、设计记录、命令日志、review/协作记录与候选人确认表。

### 3.2 状态词汇

| 状态 | 含义 | 可用动词 |
| --- | --- | --- |
| `upstream-verified` | frozen paper/repo 直接支持的公开设计 | “上游实现/论文提出” |
| `local-snapshot` | 本地 commit 中存在文件或 artifact | “本地快照包含” |
| `git-coarse` | commit author/committer 是候选人，但无细粒度历史 | “由候选账号提交快照” |
| `self-attested` | 简历/口述声明本人做过，尚无独立过程证据 | “候选人自述负责” |
| `role-confirmed` | 候选人逐项确认亲手/协作/工具边界 | “我负责/我实现” |
| `process-supported` | 有 before/after diff、设计记录、命令或 review 佐证 | “我设计并完成/定位并修复” |
| `result-owned` | checkpoint、protocol、raw result 和个人角色连续闭合 | “我完成并得到……” |

## 4. Git 与 upstream 冻结事实

### 4.1 本地仓库

| 检查 | 结果 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| Project commit | `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`，2026-06-28，author/committer `mousongzhe` | 候选账号提交了初始快照 | 快照内每个文件均为其独立原创 |
| commit 范围 | root commit 一次加入 1326 paths；其中 OpenPiVLA 360 paths | OpenPiVLA 作为大快照的一部分进入 Git | 生成顺序、协作者、工具或历史来源 |
| numstat | OpenPiVLA text paths 合计约 66,757 additions；binary paths 不计行数 | 快照规模与审查范围 | 工作量归属或代码质量 |
| path history | `git log --all -- openpivla_deployment` 只有上述 1 条 commit | 当前 Git 没有更早/后续 OpenPiVLA diff | 文件在进入 Git 前如何形成 |
| key-file history | `formal_train.py`、`data.py`、`recipes.py`、`DEPLOYMENT.md` 的 `--follow` 均只有 root commit | 关键文件与快照绑定 | 哪些行是手写、移植、生成或协作 |
| current worktree | OpenPiVLA 路径无未提交修改；Project 的 dirty state 位于 UWM 报告文件 | 本轮审查未混入 OpenPiVLA 未提交变化 | remote 主机是否有更新 artifact |

### 4.2 Frozen OpenPI 对照

Physical Intelligence/OpenPI commit `15a9616a00943ada6c20a0f158e3adb39df2ccac` 的 GitHub tree 在 2026-07-19 返回 177 项、`truncated=false`；其中没有 `vla_qwen3_repro` 或 `train_vla_qwen3*` 路径。这个事实支持“本地训练模块不是该 frozen upstream tree 中的原文件”，但不支持“因此必然由候选人独立原创”。本地实现仍可能来自历史私有分支、协作者、工具辅助或重新组织的代码，必须由 role ledger 继续区分。

## 5. Per-file / per-decision ownership matrix

| ID | 文件 / 决策 | Local artifact 事实 | Git / upstream 事实 | 当前 role verdict | 当前安全口径 | 升级所需证据 |
| --- | --- | --- | --- | --- | --- | --- |
| `OPV-OWN-001` | `formal_train.py`：Qwen3-VL + LoRA trainer | 608 行；加载 `Qwen3VLForConditionalGeneration`、注入 LoRA、计算 `outputs.loss`、保存 adapter/processor；SHA `51b67d...ccc6f94` | blob `aafd6e...`; 仅 root commit；frozen upstream 无该路径 | `local-snapshot / git-coarse / role-pending` | “项目快照包含一条 Qwen3-VL+LoRA formal training path” | 候选人确认具体函数；pre-snapshot diff；运行命令和 review |
| `OPV-OWN-002` | action JSON dataset / collator | `DroidActionTextDataset` 构造 `{"actions":...}`；Qwen chat template；只有 padding label 为 `-100`，其余 full chat token 监督 | 位于同一 608 行文件；无逐函数历史 | `local-direct / full-sequence-CE / decision-owner-pending` | “本地路线采用 assistant JSON content + full-chat causal CE，不等价于 FAST” | 为什么选 JSON、为何没有 assistant mask、parser/round-trip、候选人修改点 |
| `OPV-OWN-003` | `H=15,D=72` 与 `limit=16` | recipe/smoke 输出 `(B,15,72)`；formatter 每步最多 16 数；probe 确认丢 840/1080 positions，parser missing | 冲突与 negative evidence 可直接复核 | `technical-finding-verified / parser-missing / fixer-pending` | “审计发现 lossy shape contract 尚未闭合” | 谁发现、何时、是否在别处修复、strict parser 与 controller mapping |
| `OPV-OWN-004` | `recipes.py` + YAML + launch scripts | 三类 mode、数据组、100k 计划、batch/save/eager 参数可读 | recipes blob `89a076...`; 三组文件都只在 root commit | `local-snapshot / role-pending` | “本地工程组织了三类可审计 recipe” | 逐文件亲手/协作确认；历史 shell/config diff；run manifest |
| `OPV-OWN-005` | `data.py` / public smoke | 288 行；public robot/VLM roots、shape padding/repeat、manifest 与 batch；三份 smoke summary 可读 | blob `ed7b80...`; root commit；smoke 明确 `private_data_deployed=false` | `local-direct / verification-local / role-pending` | “public smoke 验证 schema、shape 和 tiny step” | smoke command/stdout、谁运行、private data manifest、同 formatter parity |
| `OPV-OWN-006` | `runner.py` / `model_probe.py` | runtime、base-model probe、tiny train step、public/full plan 分层 | blobs `878184...` / `3d87d1...`; root commit | `local-snapshot / role-pending` | “项目提供分层 smoke/probe 工具” | 候选人实现范围、failure log、工具辅助与 review 记录 |
| `OPV-OWN-007` | eager / MACA formal path | CLI 默认 eager；deployment/report 记录 MACA Torch 与历史 flash-attention failure | code + report 直接；full formal logs/checkpoints 仅 remote-referenced | `engineering-choice-supported / decision-owner-pending` | “在 MACA 上采用 eager 作为兼容路径” | 候选人决策确认、eager/flash A/B、raw traceback、remote log/export |
| `OPV-OWN-008` | formal 100k runs / checkpoint saving | report 记录三条 `complete @ 100000`；代码可保存 adapter/processor | remote log/checkpoint 不在本地；path 不是 bytes | `report-supported / result-owner-blocked` | “报告记录三条 formal completion” | 三条 raw log、checkpoint SHA、load smoke、run operator 与 reviewer |
| `OPV-OWN-009` | LIBERO / ALOHA rollout scripts | 322 行 LIBERO true rollout、265 行 ALOHA rollout；episode/video/summary artifacts 可读 | blobs `57a976...` / `a29f98...`; root commit；使用 official checkpoints | `local-direct / execution-role-pending` | “项目搭建 official-checkpoint rollout diagnostics” | 谁编写/运行、命令、env commit、formal Qwen checkpoint parity |
| `OPV-OWN-010` | LeRobot action eval / dashboards | 457 行 server eval；timeout、future-window、L1/action norm、summary/dashboard | blob `5dcefd...`; artifacts 在 root snapshot | `local-direct / execution-role-pending` | “项目提供 offline action-interface diagnostics” | 运行者/作者确认、raw request trace、metric reducer tests |
| `OPV-OWN-011` | `DEPLOYMENT.md` / remote operations | 543 行记录 remote layout、stop boundary、checkpoint/log 路径和 simulator classification | blob `b358c4...`; root commit；文档不是 remote state proof | `documentation-direct / operator-pending` | “部署记录定义了环境和证据边界” | shell history、sync manifest、remote file hashes、候选人操作范围 |
| `OPV-OWN-012` | formal report / archived 97.4 | 1439 行报告；含 formal run table、loss curves、`224_h10_40000` 97.4 summary | blob `bd0fbe...`; raw checkpoint/protocol/episodes 缺失 | `report-supported / C3-and-owner-blocked` | “committed report 汇总 archived 97.4%” | raw eval bundle、reducer、checkpoint lineage、运行/分析/审查角色 |
| `OPV-OWN-013` | OpenPI / FAST 方法 | frozen upstream 直接支持 policy、normalizer、FAST DCT/BPE、official LIBERO baseline | public upstream；本地 custom path不在 frozen tree | `upstream-only` | “我基于/对照 OpenPI 与 FAST” | 永远不升级为个人原创；只确认适配或复现部分 |

## 6. Claim → ownership reconciliation

| 面试/简历 claim | Claim 等级 | 当前 Evidence Contract | 当前处理 |
| --- | ---: | --- | --- |
| “实现 Qwen3-VL + PEFT LoRA formal trainer” | C1 | code exists + custom path absent upstream + coarse Git；缺个人逐项确认/diff | 候选人确认 `OPV-OWN-001/002` 后可保留；否则降为“参与搭建” |
| “设计 assistant-side JSON action representation” | C2 | code fact成立；设计动机、alternative、owner、roundtrip 缺 | 当前改为“采用/实现 JSON action route” |
| “组织三类 recipe” | C1/C2 | recipes/config/scripts direct；个人决策和 formal raw artifacts不全 | 候选人确认后可写“负责组织”；不写三条模型均验证 |
| “完成 MACA/C500 迁移” | C2 | eager/runtime/deployment/report支持；raw remote run和operator history缺 | 写“迁移训练路径/处理兼容性”；不要写性能 uplift |
| “完成三条 100k 训练” | C3 | report-supported + remote-referenced | 不作为独立 verified 结果；面试主动说明 raw artifact pending |
| “取得 LIBERO 97.4%，高于官方” | C3 | archive summary；protocol/lineage/raw/ownership 均缺 | 禁写“高于官方”；只可陈述报告中存在该归档汇总 |
| “完成 LIBERO/ALOHA rollout 验证” | C2/C3 | local artifacts存在，但使用 official checkpoints | 可讲 eval engineering；不能绑定 formal Qwen/97.4 |
| “OpenPiVLA 核心方法是我原创” | C2/C3 | 与 frozen OpenPI/FAST 冲突 | 明确拒绝；贡献应落在适配、contract、诊断和证据工程 |

## 7. Production Gap：从快照到可抗追问 ownership

| 当前做法 | 大厂面试官会追问 | 缺口等级 | 最小补证据 | 安全表达 |
| --- | --- | ---: | --- | --- |
| 一次性 initial snapshot | 哪个文件是你改的？相对上游 diff 在哪？ | P0 | 导出 pre-snapshot 来源、逐文件 diff/patch、角色确认 | “本地快照包含；个人改动以 ledger 为准” |
| 文档引用 remote checkpoint | checkpoint 能加载吗？和 log 对得上吗？ | P0 | checkpoint/processor SHA、load stdout、run manifest | “报告记录完成，权重待核” |
| JSON action route | 为什么这样设计？为何 full-sequence CE？如何 decode/controller round-trip？ | P0 | schema、assistant span、strict parser、sentinel、axis/unit/normalizer | “本地采用 JSON/full-chat CE，parser/controller 闭环仍缺” |
| official checkpoint diagnostics | 是你训练的模型吗？ | P0 | formal Qwen checkpoint → same harness manifest | “只证明 eval pipeline，不证明 formal 模型效果” |
| report 97.4 | trial/seed/init/protocol/raw episodes 呢？ | P0 | raw eval bundle与冻结 reducer | “archive-summary-only” |
| 未记录协作者/工具 | 哪段由 AI/同事生成？你如何审查？ | P0 | contribution ledger、review notes、现场解释 | “按亲手/协作/工具辅助逐项说明” |
| 只有最终代码 | 遇到什么 bad case，怎么定位？ | P1 | failure→hypothesis→diff→rerun timeline | “当前代码证明结果形态，不证明问题解决过程” |

## 8. Question Tree 与回答分层

### 8.1 主追问树

```text
你个人做了什么？
  ├─ 回答 trainer
  │    ├─ 哪些 class/function 亲手写？
  │    ├─ 相对 frozen OpenPI 的 diff 在哪？
  │    └─ 为什么 JSON/CE，不用 FAST/action expert？
  ├─ 回答 MACA 迁移
  │    ├─ 原始 traceback 是什么？
  │    ├─ 为什么选 eager？做过 A/B 吗？
  │    └─ 哪条 checkpoint 真正加载过？
  ├─ 回答评估
  │    ├─ official checkpoint 还是 formal Qwen？
  │    ├─ H/K、normalizer、controller、success predicate是什么？
  │    └─ 97.4 的 raw episodes 在哪？
  └─ 回答“全部负责”
       ├─ 初始快照为何没有逐文件历史？
       ├─ 协作者和工具辅助边界是什么？
       └─ 现场选一个函数解释输入、输出、失败和验收
```

### 8.2 高压题：这个项目到底哪部分是你写的？

- **危险回答**：整个 OpenPiVLA 都是我写的；Git author 是我，所以这些代码全是我的。
- **可过回答**：我负责本地 Qwen/LoRA formal path、recipe 和评估适配；OpenPI/FAST 是上游。当前 Git 是一次性快照，逐文件历史不完整，所以我会按文件说明亲手、协作和工具辅助边界。
- **强回答（仅在候选人确认后使用）**：我亲手负责 `formal_train.py` 中的 Qwen/LoRA load、JSON action dataset/collator 和 adapter save，负责 `recipes.py` 与三类 launcher 的 run contract，并在 MACA 上处理 eager fallback；rollout scripts 中我负责的是某几个明确函数和验收。OpenPI policy/FAST 不属于我的原创，97.4 也只是 archive summary。可以现场从一个 sample 进入 formatter、labels、`outputs.loss` 和 checkpoint save 逐行解释，同时指出 `D=72` 与 `limit=16` 尚未闭合。

强回答不是自动批准稿；候选人没有逐项确认前，只能使用“可过回答”。

## 9. SP/SSP 证据就绪度评分

这不是候选人能力评分，而是 OpenPiVLA 项目当前能否抗大厂追问的证据评分。

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.5 | VLA action、multimodal training、policy serving 和 LIBERO 高相关 |
| 机制深度 | 4.0 | 能解释 Qwen/LoRA、JSON/CE、FAST 边界、H/D/K 与 controller contract |
| 工程闭环 | 3.5 | trainer/recipe/smoke/deployment/eval artifact 齐；formal raw checkpoint 与 lineage 缺 |
| 指标可信度 | 1.5 | 97.4 仍是 archive-summary-only；official 96.85 不可直接比较 |
| Ownership 清晰度 | 2.0 | 本页完成逐文件分类，但个人动作、协作和工具边界尚未由候选人确认 |
| 抗追问能力 | 3.0 | 技术路径可讲；一旦追问 diff、运行者、checkpoint 与 raw result 仍有断点 |
| 合计 | **18.5 / 30** | ownership 结构已建立，但没有新增独立个人贡献证据，不人为加分 |

一票否决项：把 upstream 当原创；把 root commit author 当全部文件作者；把 official checkpoint rollout 绑定 formal Qwen；把 report/path 当 checkpoint；把 archive 97.4 写成本人超过官方。

## 10. 候选人确认表

下一次口述或材料核对时，只需逐项回答“亲手 / 协作 / 工具辅助 / 上游 / 不确定”，并给出一条可验证细节：

1. `formal_train.py` 的哪些函数由你从零写、改写或审查？原始来源在哪里？
2. JSON action representation 是谁决定的？为什么设 `limit=16`？是否有 parser？
3. `recipes.py` 的三条 recipe 是你根据哪些历史日志恢复的？哪些字段只是归档转述？
4. 三条 `run_formal_*.sh` 是谁编写并在 remote 执行的？你是否亲自查看过最终 checkpoint？
5. eager fallback 是你定位并决定的吗？原始 flash-attention traceback 和验证命令是什么？
6. ALOHA、LIBERO、LeRobot 三类 eval scripts 中哪些由你编写、修改或只负责运行？
7. formal report 与 dashboard 是手写、脚本生成、AI 辅助还是协作产物？你审查了哪些结论？
8. 参与该项目的其他人、AI 工具或历史代码分别贡献了什么？

这些回答没有发生前，不创建 coaching state，也不把本页状态升级为 `role-confirmed`。

## 11. 分阶段补强计划

| 时间 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 完成上述 8 项角色确认；每个关键文件选择 1 个可现场解释的函数 | 13 个 ledger 行都有 `role` 和 `source` | `待候选人确认` |
| 1 天 | 找回 pre-snapshot 来源，生成 custom path 相对上游/历史分支的 diff；记录工具/协作者 | Qwen/JSON/recipe/eval 的 authored/modified/reviewed 边界可复查 | `待补做` |
| 3 天 | 导出三条 formal log/checkpoint manifest，并做 load smoke；补 action roundtrip | C1/C2 和 run ownership 不再只靠快照/报告 | `待补做` |
| 1 周 | 补 formal Qwen same-harness eval、raw episodes、protocol diff 和失败复盘 | C3 才有升级可能；不保证得到 uplift | `待补做` |

## 12. Output Pack：当前可用与补证后表达

### 12.1 简历 bullet 三档

- **保守版（当前外部证据即可支持）**：参与 OpenPI/OpenPiVLA 训练复现，搭建 Qwen3-VL + PEFT LoRA formal training path、VLA/VLM/co-train recipes 与 public smoke/eval diagnostics；明确 local JSON/causal-CE 与 FAST/action expert 的实现边界。
- **标准版（候选人逐文件确认后）**：负责 Qwen3-VL + LoRA trainer、assistant-side JSON action supervision 与三类训练 recipe 的实现和 MACA 兼容性适配，并通过 public smoke、checkpoint 保存合同与 official-checkpoint rollout diagnostics 验证训练/评估接口。
- **偏强版（必须补 diff、checkpoint/load、formal eval 后）**：设计并落地可追溯的 Qwen-based VLA training/eval pipeline，闭合数据、动作表示、checkpoint、policy serving 与 LIBERO raw evaluation lineage；具体结果只使用同协议可重算数据。当前禁止写成已完成态。

### 12.2 两分钟项目叙事骨架

> 这个项目的上游基础是 OpenPI 和 FAST，我不会把 policy/action tokenizer 的公开方法算成个人原创。项目本地恢复出一条可审查的 formal path：Qwen3-VL + PEFT LoRA，机器人 action window 写入 assistant JSON content，当前 collator 实际优化 full-chat causal CE，并组织 VLA-only、VLM-only、co-train 三类 recipe；在 MACA/C500 环境里用 eager、public smoke、adapter/processor 保存和 deployment diagnostics 检查 contract。
>
> 当前最重要的技术发现是三条边界：FAST DCT/BPE 与 local JSON text 不能混写；`H=15,D=72` 经 `limit=16` 丢失 77.78% schema positions 且没有 formal parser/controller；7D/4-step official WebSocket eval 也不是 formal Qwen lineage。项目报告的 100k/97.4 仍缺 checkpoint、raw episodes、protocol 与 lineage，所以我不声称超过 official 96.85。个人贡献只按候选人确认的 trainer、recipe、兼容性与评估脚本逐项说明。

叙事最后一句必须依据候选人确认表改写；未确认前不要把“项目本地做的是”自动替换为“我独立完成”。

### 12.3 面试前 6 题

1. 从 DROID row 到 Qwen `outputs.loss` 的完整数据流是什么？
2. JSON/CE 路线与 FAST DCT/BPE 的目标、token 和 decode 差异是什么？
3. `H=15,D=72` 与 `limit=16` 为什么是高危 bug，而不是普通配置差异？
4. eager fallback 解决了什么已知失败，又牺牲了什么？怎样做 matched A/B？
5. report-supported 100k、checkpoint verified、benchmark verified 三者差在哪？
6. 请逐文件说明你的亲手、协作、工具辅助与上游边界。

## 13. Ownership 审计伪代码

```python
def accept_personal_claim(claim, ledger):
    # 1. File/run identity must be frozen; a path without bytes is insufficient.
    if not ledger.identity_and_artifact(claim):
        return "reject_strong_claim"

    # 2. A snapshot author does not prove who designed or wrote each file.
    if not ledger.role_confirmed(claim):
        return "use_participated_or_project_contains"

    # 3. Strong design/fix language requires decision history and verification.
    if claim.level >= "C2" and not ledger.process_and_test_supported(claim):
        return "downgrade_to_implemented_or_adapted"

    # 4. Numeric result ownership requires checkpoint, protocol and raw outputs.
    if claim.level == "C3" and not ledger.raw_result_chain_complete(claim):
        return "report_summary_only"

    return "claim_allowed_with_exact_scope"
```

该伪代码是本仓库的面试真实性 gate，不是 OpenPI 的官方实现。它把本页 `identity/artifact/decision/verification/ownership` 五层合同映射成可执行的审查顺序。

## 参考文献（References）

1. [OpenPiVLA Claim–Evidence Inventory](openpivla_claim_evidence_inventory.html)，12 条 claim 与 evidence tier。
2. [OpenPiVLA Batch 2 Evidence Freeze](../../sources/openpivla_batch2_evidence_freeze.html)，eager、smoke/formal/raw ladder、lineage 与 shape conflict。
3. [VOL 05 EVAL-022 Evidence Audit](../../knowledge/vol_05_engineering_eval_eval022_paper_repo_checkpoint_runtime_ownership_evidence_audit.html)，Git identity、artifact integrity 与 ownership 非替代关系。
4. [OpenPiVLA Batch 1 Cards](../../questions/proj_openpivla.html) 与 [Batch 2 Cards](../../questions/proj_openpivla_batch2.html)，12 张题卡，全部 unseen。
5. Local Project Git：`C:\Users\mousongzhe\Project`，commit `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`。
6. Local formal trainer：`openpivla_deployment/repro_train/openpi_src/src/openpi/training/vla_qwen3_repro/formal_train.py`，SHA-256 `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94`。
7. Local recipes/data：`recipes.py` SHA-256 `397d1b384a2bd93d9dc81b7003e6ab7bfac3fc458ea04008197c3f503f9d780e`；`data.py` SHA-256 `32c6aa76929d941c4832d2eb4c2550527d3e607e31c2a9f5507cc76eeedbc2ec`。
8. Local deployment record：`openpivla_deployment/DEPLOYMENT.md`，SHA-256 `c0a3dd0c0da8c1c0d36023046d5337900a71680b413657bc9b1062eef2eea14e`。
9. Local formal report：`openpivla_deployment/artifacts/vla_formal_reproduction_report_20260617.html`，SHA-256 `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074`。
10. Physical Intelligence, [OpenPI commit API](https://api.github.com/repos/Physical-Intelligence/openpi/commits/15a9616a)，resolved commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`；tree checked 2026-07-19。
11. Physical Intelligence, [FAST](https://arxiv.org/abs/2501.09747)，upstream action tokenization method；不证明 local formal route 使用 FAST。
12. [Optimized Resume](../../../../output/mousongzhe_resume_optimized.html) 与 [OpenPiVLA 项目面试页](../../../03_openpivla_action_modeling.html)，当前候选人自述与安全投递口径。
13. [OpenPiVLA Action JSON Parser / Round-trip Artifact Gate](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html)，72→16、full-sequence CE、parser absence 与 official-eval parallel lineage。
