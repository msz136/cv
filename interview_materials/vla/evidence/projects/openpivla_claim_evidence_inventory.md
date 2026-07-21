# OpenPiVLA Claim–Evidence Inventory（OPV-01）

> 状态：`drafted / local_direct_audit / ownership_ledger_drafted / WARN / resume_safely_rewritten`  
> 审查日期：2026-07-19  
> 证据截止：2026-07-19  
> 项目范围：OpenPI/OpenPiVLA、归档 LIBERO 97.4%、Qwen3-VL action supervision、MACA/C500 formal runs 与 rollout contract  
> 目标岗位：VLA / Robot Policy / Multimodal Training / Embodied Evaluation  
> 结论先行：frozen OpenPI/FAST source 能支持 π0/π0.5/FAST 的公开 action-modeling、normalization、H/K 与 policy-serving 机制，也直接确认 official `pi05_libero` 平均 96.85。真实项目证据位于 `C:\Users\mousongzhe\Project\openpivla_deployment`：当前可直接读取 formal trainer、recipe/config、启动脚本、smoke summaries、部署记录、诊断 rollout artifact 与一份 committed formal report；远端 formal log/checkpoint 只被报告和部署记录引用，当前未在本地镜像中取得。`224_h10_40000` 的 97.4% 有 committed report 的汇总表支持，但仍缺 checkpoint hash、raw summary、trial/seed/protocol 与 episode records，因此只能标为 `archive-summary-only`。这些证据足以把 Qwen JSON/causal-CE 路径、三类 recipe 和训练工程闭环从纯自述升为 `local-direct`/`report-supported`，但不足以证明 FAST DCT/BPE 等价、97.4 与 formal checkpoint 同源、97.4 高于 official 96.85，或个人 ownership。逐文件 ownership ledger 已建立，但候选人尚未确认亲手/协作/工具辅助边界；optimized resume、PDF 与 OpenPiVLA 项目页已经完成安全重写，项目证据继续保持 `WARN`。

> 2026-07-19 bounded artifact gate：直接执行/读取 `formal_train.py` 的 formatter 与三个 public smoke summaries，确认 `H=15,D=72` recipe/batch contract 与每行 `limit=16` 的 JSON serializer 同时存在；AST probe 得到 `15×16`、tail-repeat 输出。该切片把 `OPV-CL-002` 升为 local-direct with warning，把 `OPV-CL-003` 固定为 representation conflict，把 `OPV-CL-004` 固定为 semantics-open；没有升级 checkpoint、benchmark 或 ownership。

> 2026-07-19 parser/round-trip gate：formal package AST 中没有 `generate/decode/action-output json.loads`，唯一 `json.loads` 是 MindCube 输入 JSONL；72D sentinel 经 formatter/JSON 只保留 `15×16=240` 个标量，相对 `15×72=1080` 少 840（77.78%）。collator 只屏蔽 padding，故 loss 覆盖 full chat 非 padding token，而不是 assistant-token-only。项目中的 7D/4-step WebSocket eval 使用 official `pi0_aloha_sim` checkpoint，不能替 formal Qwen parser/rollout 补 lineage。`OPV-CL-002/004/010` 已据此降级/澄清，ownership 与 mastery 不变。

## 问题（Question）

本页回答：`97.4%` 是哪个 checkpoint、哪套 protocol 的结果；它是否能与官方 `96.85` 直接比较；归档 `224_h10_40000` 与当前 Qwen3-VL/MACA formal runs 是不是同一模型链；assistant-side JSON/token 与 FAST DCT/BPE 是什么关系；哪些属于 upstream，哪些能归入个人贡献；要补什么 artifact 才能形成能投、能讲、能抗追问的 OpenPiVLA 项目。

## 1. Evidence labels 与判定规则

| 标签 | 含义 | OpenPiVLA 中的例子 |
| --- | --- | --- |
| `upstream-verified` | frozen paper/official repo 直接支持 | OpenPI policy construction、norm stats、LIBERO client、FAST DCT/BPE、official 96.85 |
| `local-direct` | 当前可读取的本地 code/config/script/report/smoke/eval/episode artifact；不等于 checkpoint 或 benchmark raw bundle 齐全 | `C:\Users\mousongzhe\Project\openpivla_deployment` 下的 formal trainer、recipes、smoke summaries、部署报告与 rollout diagnostics |
| `remote-referenced` | 本地文档给出远端 log/checkpoint 路径，但本地没有对应 immutable 文件 | `/data/msz/openpivla/logs/vla_qwen3_repro/*/formal_train.log` 与 `/data/msz/openpivla/outputs/vla_qwen3_repro/<run>/checkpoint-*` |
| `archive-summary-only` | committed report 中有结果汇总，但缺少可重算 raw bundle | `224_h10_40000` 四套件 97.4% 汇总表 |
| `local-claim-only` | 只出现在简历、项目页或计划 | 未落到代码/报告的个人 ownership 与高于 official 的比较 |
| `run-lineage-open` | archive、formal train、eval checkpoint 的继承关系不清 | `224_h10_40000` vs Qwen3-VL/MACA runs |
| `representation-conflict` | FAST 与 local JSON/token route 被讲成同一实现 | DCT/BPE upstream vs assistant-side serialization |
| `ownership-unverified` | 上游事实有来源，但个人 diff/职责无直接证据 | Qwen 接入、MACA migration、trainer/collator/recipes |

Claim 强度沿用 C0–C3：C0 可由项目文档支撑“了解/参与”；C1 的“实现/迁移”需要 local code/config/log；C2 的“设计/优化/定位”需要 diff、对照和 bad case；C3 的指标/完成态需要 immutable checkpoint、完整 protocol、raw result 与 ownership。[1][3][7][8]

## 2. Role Fit 与岗位能力映射

| 岗位能力项 | 当前材料 | 强度 | 缺口 | 当前策略 |
| --- | --- | --- | --- | --- |
| VLA action representation | source audits 已核对 FAST、flow、chunk、normalize/denormalize；formal code 明确把 DROID action window 序列化为 JSON assistant text | 强（上游 + local-direct） | local route 没有 FAST processor/roundtrip 证据 | 分开讲 upstream FAST 与 local JSON/CE |
| Multimodal model adaptation | formal code 直接加载 `Qwen3VLForConditionalGeneration` 并注入 PEFT LoRA；报告记录 eager attention 与 6.42M trainable params | 强（local-direct） | 缺 checkpoint binary/load smoke 与 per-file ownership | 可讲“formal trainer path 已实现”，不写已验证模型效果 |
| Data contract | recipes/config 与 public smoke 明确 `H=15`、`D=72`；Batch 2 复核发现 current formal JSON formatter 对 action/state 使用 `limit=16` | 中（local-direct + representation-conflict） | parser、valid dims、axis/unit、私有数据 revision 与完整 sampling 仍缺 | 必须同时报告 config/smoke shape 与 formal formatter 宽度冲突，不能只报 `(15,72)` |
| Distributed/hardware migration | formal report 记录三条 100k completion，scripts/config 与 C500/MACA deployment 记录可读 | 中高（report-supported + remote-referenced） | 完整 log/checkpoint/load smoke 不在本地 | 说“报告支持的远端完成态，raw artifact 待补” |
| Closed-loop evaluation | ALOHA 3-episode、LIBERO 单任务 true rollout、Bridge/Fractal replay/adapter diagnostics 有 local-direct artifact；official eval script 可读 | 中（local-direct diagnostics） | formal Qwen checkpoint 的四套件 raw eval 仍缺 | 只讲诊断/官方 baseline rollout，不把它们绑定 97.4 |
| Experimental reasoning | 224/h10/40k 与 resolution/horizon/pretrain 分析 | 低 | 单点最优，缺 factorial/multi-seed | 只能称 hypothesis，不作因果结论 |
| Ownership | Project Git initial snapshot author 为 `mousongzhe`；[逐文件 ledger](openpivla_ownership_ledger.html)已建立 | 中低（Git-supported） | 360 个 OpenPiVLA paths 一次进入 root snapshot；候选人尚未确认亲手/协作/工具边界 | 只能说“提交中包含这些实现”；按 ledger 逐项确认后再升级动词 |

没有具体 JD，因此本页只做 VLA/robot-policy 通用能力映射，不编造公司面试流程。

## 3. Frozen inputs 与官方 baseline 核验

| Source | SHA-256 / revision | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| optimized resume [1] | `5374d4b6f6617394381bb0c17e81c298ccef34bf6c3fc329e6e6bf04d01f1d4c` | 已安全移除 OpenPiVLA 未闭合 benchmark 数字，保留 direct engineering claims | raw provenance |
| optimized PDF [2] | `65b1dcd34cd6e357c6264effcf4b2683dea66508c6bc58315762b5e4c03ac74a` | A4 单页、与安全重写后的 HTML 一致 | 项目 raw C3 证据 |
| OpenPiVLA 项目页 [3] | `ca24762864c998c6fe79812a1bc2aada8e3895773e64fd9c98a86a40464e0059` | 已对齐 archive-summary-only、local JSON/CE 与 formal report-supported 口径 | raw checkpoint/episode 实际存在性 |
| resume plan [4] | `d9ae41dc5d6d8b3601ac4184ba68b9e5b6b8cd4b1b452ec42172768f1d9248af` | 当前安全简历口径与禁写边界 | checkpoint 与 protocol |
| research resume [5] | `9a8828ae0b6317c107ab16ec3d106cad8ba944854469e7919a7ba0c1342b643f` | action JSON、H/D、四套件历史表述 | raw code/eval |
| engineering resume [6] | `2aa3f0dae040ad5fb6bff32d68b5f4fff574bf4b2be80abc93d9f29b96f78732` | trainer/collator/rollout 历史表述 | raw code/eval |
| π0/FAST/OpenPI audit [7] | `ded60a239f8edbf2171096c89fa5fd85e41e51efbbc260df9c188ae57c9fb829` | frozen OpenPI/FAST action path、H/K/norm 边界 | 本地 97.4/Qwen route/ownership |
| architecture/execution audit [8] | `bef8ebb6540644cdbab76a92adaa71ba97523c17e04ce19632b71d54b11db809` | model→decode→controller 与 audit contract | 本地 checkpoint/axis/unit/latency |
| VOL 03 source ledger [9] | `c77e1cc6ee161114ab7c19f0d95ee93bfcaf87ea10c07eccd1212360e0877455` | 明确 archived 97.4 ≠ current formal result | 任一 local result |
| frozen OpenPI root README [10] | `openpi@15a9616a`，raw SHA `567fc57766bd736664f50126cab8145af4071ca16cc5e238f2b11e369169c3b5` | official checkpoint/config 入口 | 96.85 table 的完整行 |
| frozen OpenPI LIBERO README [11] | raw SHA `a2caaf5459c4b01837b73aa93a6f69e8cdf10385b39c34eba36afa85f83fafe9` | π0.5@30k: spatial 98.8、object 98.2、goal 98.0、LIBERO-10 92.4、average 96.85 | 本地协议可比性 |
| Project Git snapshot [12] | repo `C:\Users\mousongzhe\Project`, commit `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`, author `mousongzhe` | OpenPiVLA deployment source/artifact snapshot and coarse authorship | per-file ownership、remote checkpoint provenance |
| formal trainer [13] | SHA `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94` | HF Qwen3-VL + PEFT LoRA、JSON action text、causal CE、save plan | FAST equivalence、actual formal checkpoint load |
| formal report [14] | SHA `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074` | run table、loss curves、100k report-supported completion、archived 97.4 summary and limitations | raw formal logs/checkpoints、raw 97.4 eval bundle |

2026-07-17 重新审计 `C:\Users\mousongzhe\Project` 后，发现上述项目页引用的真实目录已提交到 `c4469eb`。因此当前证据不是“local direct = 0”，而是分层如下：

| Evidence tier | 已发现内容 | 仍不能证明 |
| --- | --- | --- |
| `local-direct` | `DEPLOYMENT.md`、`repro_train/README.md`、三份 YAML、`formal_train.py`/`data.py`/`recipes.py`、三条 `run_formal_*.sh`、三个 smoke summary、formal report、official LIBERO eval launcher、ALOHA/LIBERO/diagnostic rollout artifact | 这些文件本身不包含三条 formal checkpoint binary、完整远端 log、97.4 raw episodes 或 per-suite summary |
| `remote-referenced` | formal report 与 deployment log 指向 `/data/msz/openpivla/logs/vla_qwen3_repro/*/formal_train.log`、`/data/msz/openpivla/outputs/vla_qwen3_repro/<run>/checkpoint-*` | 当前没有 immutable remote export、checkpoint SHA 或 load smoke 可复核 |
| `archive-summary-only` | formal report 的 `224_h10_40000` 表格：spatial 0.98、object 0.995、goal 0.99、libero_10 0.93、average 97.4 | model class、checkpoint、trial/seed/init protocol、raw episode records、与 formal run 的 lineage |

这轮审计只升级证据等级，不升级简历强度；投递稿和项目页仍需下一切片重写。

## 4. Claim reconciliation matrix

| ID | 当前 claim | 等级 | 当前证据 | Verdict | 处理动作 |
| --- | --- | --- | --- | --- | --- |
| `OPV-CL-001` | 基于 OpenPI 改造 Qwen3-VL-2B + LoRA VLA 路径 | C1/C2 | `formal_train.py` 直接加载 `Qwen3VLForConditionalGeneration`、`LoraConfig`/`get_peft_model`；三份 recipe/config 与 formal report 可读 | `local-direct / ownership-open` | 可说“formal trainer path 已实现”；不能把可读源码等同于本人独立设计或已加载最终模型 |
| `OPV-CL-002` | local route 将 continuous action window 编成 assistant JSON content | C2 | `DroidActionTextDataset` 生成 `{"actions": ...}`；collator 只屏蔽 padding，prompt/wrapper/assistant 全部非 padding token 进入 CE；formatter probe 复核 `15×16` | `local-direct / full-sequence-CE / PASS WITH WARNING` | 还缺 generation/parser/controller；不得称 assistant-token-only CE 或连续 action loss |
| `OPV-CL-003` | local route 复用了 FAST DCT/BPE | C2 | recipe 保留 `fast_tokenizer` 字段，但 formal trainer 未调用 FAST processor；report 明确 JSON/CE 与 FAST 分离 | `REPRESENTATION-CONFLICT` | 禁止把 local JSON 路径称为 FAST；FAST 只作 upstream 对照 |
| `OPV-CL-004` | DROID `H=15/D=72` 与 MindCube QA 统一训练 | C1/C2 | recipes/config 与 smoke 报 `(B,15,72)`；current formatter 每步 `limit=16`；72D probe 丢 840/1080 positions，empty/NaN/ragged cases 无 schema gate | `LOSSY-SERIALIZATION / PARSER-MISSING / semantics-open` | 不能声称 current formal path 保留 72 维；先实现 strict parser、axis/unit、normalizer 与 controller round-trip |
| `OPV-CL-005` | VLA-only、VLM-only、co-train 三类 recipe | C1/C2 | `recipes.py`、三份 YAML、三条 launch script、smoke summaries、formal report run table | `local-direct + report-supported` | recipe 定义可核；三条远端完成态仍需 immutable logs/checkpoints/load smoke |
| `OPV-CL-006` | 在 MACA/C500 完成三条 100k-step formal runs 与多 checkpoint 保存 | C3 | committed formal report 记录三条 `complete @ 100000`、保存点与远端路径；deployment/launch script 可读 | `REPORT-SUPPORTED / REMOTE-ARTIFACT-PENDING` | 不写“本地 checkpoint 可加载”；补三条 log、checkpoint SHA、load smoke 后才升 verified C3 |
| `OPV-CL-007` | archived `224_h10_40000` 四套件 99.0/99.5/98.0/93.0，平均 97.4 | C3 | committed formal report 有该汇总表 | `ARCHIVE-SUMMARY-ONLY` | 可说“归档报告汇总为 97.4%”；不能声称 raw eval、checkpoint 或 formal lineage 已闭合 |
| `OPV-CL-008` | local 97.4 高于 official OpenPI 96.85 | C3 | official 96.85 已核实；local side 与 protocol comparability 未核 | `COMPARISON-FAIL` | 不写“高于”；需 same-suite/trial/seed/harness 与 uncertainty |
| `OPV-CL-009` | 224/h10/40k、resolution/horizon/pretrain 导致更稳策略 | C2/C3 | 单点最优自述；无 controlled ablation | `INFERENCE` | 改成“候选解释”；不得作因果归因 |
| `OPV-CL-010` | formal Qwen runs 通过 LIBERO/ALOHA rollout 验证 controller 语义 | C2/C3 | official WebSocket eval 直接返回 numeric actions，A01 为 `pi0_aloha_sim`, `D=7,H=4`；formal Qwen package 无 generation/parser | `PARALLEL-OFFICIAL-LINEAGE / FORMAL-QWEN-MISSING` | 可讲 official-checkpoint eval diagnostics；不能绑定 formal Qwen、JSON route 或 97.4 |
| `OPV-CL-011` | archived 97.4 与 formal Qwen/MACA runs 构成同一项目结果链 | C3 | source ledger 明确二者不能直接等同 | `RUN-LINEAGE-OPEN` | 建 `archive→base→formal→eval` checkpoint lineage；当前分开讲 |
| `OPV-CL-012` | Qwen 接入、MACA migration、trainer/collator/recipes 是个人核心贡献 | C1/C2 | 相关文件在 Project `c4469eb` 初始 snapshot；逐文件 ledger 已将 13 个文件/决策分层 | `GIT-SUPPORTED / LEDGER-DRAFTED / ROLE-CONFIRMATION-PENDING` | Git authorship 不是个人贡献证明；候选人需确认亲手/协作/工具边界并补 diff |

## 5. 三个高风险断点

### 5.1 archived 97.4 ≠ current formal runs

项目页已经承认 97.4 是 strongest archived eval evidence，而 formal Qwen/MACA 训练只证明训练 contract 可恢复，不能直接称为 97.4 checkpoint 的来源。[3][9] 但 optimized resume 连续排列两组 bullet，面试官容易追问：“97.4 是哪条 100k run 的哪个 checkpoint？”当前没有 lineage 可以回答。

最小 lineage 必须是：

```text
archive_run_id -> model_class/base_checkpoint -> local_diff/config
-> train_run_id/checkpoint_sha -> norm_stats_sha
-> eval_run_id/suite/trials/seeds -> episode_records/summary
```

### 5.2 97.4 与 official 96.85 的比较没有闭合

official 96.85 是 frozen OpenPI LIBERO README 的 π0.5@30k 表格事实。[11] 本地 97.4 现在有 committed report summary，但没有 raw eval bundle。即使汇总数字真实，也要对齐 suite order、task version、trials、seeds、init states、checkpoint、image preprocessing、H/K、controller、success predicate 与 aggregation。单点差 0.55pp 也不能自动称 statistically meaningful uplift。

### 5.3 FAST 与 assistant JSON/token 不能混写

FAST 是 normalization→DCT→quantization/BPE→token→decode/IDCT 的公开路径；项目页又描述 local Qwen LoRA 将 action window 序列化为 assistant-side JSON/token。除非 local formatter 明确调用 frozen FAST processor 并有 roundtrip test，这两者只能是“上游机制对照”与“本地候选表示”两条线，不能说 local route 完整复用了 FAST。[3][7]

## 6. Truth boundary 与当前安全口径

| 内容 | 当前状态 | 简历 | 面试 | 证据到位后 |
| --- | --- | --- | --- | --- |
| OpenPI/FAST 机制理解 | `upstream-verified` | 可作技术栈，不作个人成果 | 可机制级回答 | 不升级为原创 |
| Qwen3-VL/LoRA local route | `local-direct / ownership-open` | 可写“实现 formal trainer 路径/梳理 contract”，不写模型效果 | 指向真实源码；说明 adapter/CE/eager 与 upstream 的差异 | per-file ownership + checkpoint/load smoke 后可升 C1/C2 |
| assistant action JSON content | `local-direct / full-sequence-CE` | 可写“将 action window 序列化为 assistant JSON content，并在 full-chat causal CE 中训练” | 与 FAST DCT/BPE、assistant-only mask 明确分开 | generation/parser/controller robustness 后升更强 |
| three formal 100k runs | `report-supported / remote-artifact-pending` | 暂不写“本人完成且 checkpoint 可用” | 可说报告记录三条 `complete @ 100000`，raw logs/checkpoints 待核 | immutable manifests + load smoke 后恢复 C3 |
| archived 97.4 | `archive-summary-only` | 暂不放投递强结果 | 可说“committed archive report 汇总 97.4%，raw eval pending” | exact checkpoint/eval bundle 后恢复 |
| high vs 96.85 | `COMPARISON-FAIL` | 不写“高于” | 只说明 official baseline 已核实 | same-protocol paired evidence 后再判断 |
| resolution/horizon/pretrain 影响 | `INFERENCE` | 不写因果 | 说“待验证假设” | controlled ablation 后升级 |
| personal ownership | `ownership-unverified` | 用保守动词 | 逐项说明边界 | diff/ledger 到位后写具体模块 |

### 当前仍不能升级为 verified C3 的原因

1. 97.4 的 checkpoint、trial/seed、summary 与 episodes 全缺。
2. three 100k formal runs 有 launch scripts 与 committed report，但缺 immutable formal logs、checkpoint SHA 和 load smoke。
3. archived eval 与 formal Qwen/MACA 没有 checkpoint lineage。
4. local JSON/token 已有源码证据，且与 upstream FAST 实现不同；项目页已分开表述，但 parser/roundtrip 仍待补。
5. ownership ledger 已把个人、历史项目、上游和工具辅助拆成 13 行，但候选人角色确认与 pre-snapshot diff 仍缺。

### 当前保守表达

在候选人确认自己确实参与该复现后，当前可用：

> 在 OpenPI 工程框架上实现 Qwen3-VL + PEFT LoRA formal trainer，将 DROID action window 序列化为 assistant JSON content，并在 full-chat causal LM CE 中与 MindCube QA 共同训练；用 vla-only、vlm-only、co-train 三类 recipe 组织 MACA/C500 训练与部署诊断。审计确认这不等价于 FAST DCT/BPE，且 `D=72` 经 `limit=16` 后为 lossy serialization，formal package 尚无 generation/parser/controller。committed report 的 100k/97.4 仍缺 raw checkpoint、protocol、episode bundle 和 archive→formal lineage，不能写“高于 official 96.85”或 formal checkpoint rollout 已验证。

## 7. P0 artifact manifest

| Priority | Artifact | 最低字段 | 关闭 claim | 当前状态 |
| --- | --- | --- | --- | --- |
| P0 | archived eval bundle | `224_h10_40000` checkpoint SHA、model class、config、norm stats、suite/task/trial/seed、summary、episodes/videos | CL-007/008/009 | `PARTIAL`（committed report summary；raw bundle missing） |
| P0 | checkpoint lineage | archive/base/formal/eval run ID、parent SHA、hardware、date、status | CL-006/007/011 | `MISSING` |
| P0 | local model/diff bundle | Qwen model class、forward/loss、LoRA targets、changed files、startup/load log | CL-001/012 | `PARTIAL`（源码/config direct；diff/ownership/load smoke missing） |
| P0 | action representation bundle | formatter、FAST processor revision if used、JSON schema、labels/loss mask、decode/parser/roundtrip tests | CL-002/003 | `PARTIAL`（JSON/CE direct；FAST/parser/roundtrip missing） |
| P0 | data contract bundle | DROID/MindCube revision、sample schema、H/D valid dims、axis/unit、mixture/sampling、padding mask | CL-004/005 | `PARTIAL`（recipe/shape direct；semantic/provenance fields missing） |
| P0 | formal run ledger | three commands/config SHAs、logs、steps reached、checkpoint hashes、load smoke | CL-005/006 | `PARTIAL`（scripts/report direct；logs/checkpoints/load smoke remote-pending） |
| P0 | rollout bundle | policy server/client revision、H/K/Hz、preprocess、normalizer、controller、episodes、success predicate | CL-010 | `PARTIAL`（official baseline + diagnostics direct；formal Qwen rollout missing） |
| P1 | comparison/ablation | official-vs-local protocol diff、resolution×H×checkpoint factorial、multi-seed CI | CL-008/009 | `MISSING` |
| P1 | ownership ledger | 亲手、协作、历史归档、上游、Codex/工具辅助 | CL-012 | `PARTIAL`（13-row ledger drafted；candidate confirmation / pre-snapshot diff missing） |

```python
def accept_openpivla_result(bundle):
    # Bind the metric to one immutable model lineage, not a project title.
    require(bundle.checkpoint_sha and bundle.parent_checkpoint_sha)

    # Freeze data/action semantics and the complete closed-loop protocol.
    require(bundle.norm_stats_sha and bundle.action_schema and bundle.rollout_protocol)

    # Keep raw episode records and metric code so the score can be recomputed.
    require(bundle.episode_records and bundle.summary and bundle.metric_code_sha)

    # Separate upstream, archive, personal and tool-assisted contributions.
    require(bundle.ownership_ledger and bundle.local_diff)
    return "verified" if all_checks_pass(bundle) else "claim-only"
```

这是证据门伪代码，不是项目现有实现。

## 8. 必须回答的六个问题

1. `224_h10_40000` 的 model class、base checkpoint、checkpoint SHA、norm stats、eval summary 与 episode 路径是什么？
2. 97.4% 的每 suite trial 数、seed、init state、task version、H/K、controller 和 success predicate是什么？
3. archived 97.4% 与三条 Qwen3-VL/MACA 100k formal runs 是什么继承关系；哪条 formal checkpoint 做过四套件 eval？
4. local action route 是 FAST DCT/BPE、普通离散 token、JSON 文本，还是它们的组合；formatter、loss mask 和 decode/parser 在哪里？
5. DROID `H=15/D=72` 的 72 维哪些有效，axis/unit 是什么，如何映射到 LIBERO/ALOHA controller？
6. `RunRecipe`、collator、trainer、MACA migration、eval scripts 中哪些是你亲手改，哪些来自 archive/upstream，哪些由工具或协作者完成？

## 9. Preliminary SP/SSP project scorecard

这是项目证据就绪度，不是候选人能力评分；置信度为 `Medium`。local-direct 工程证据提高了工程闭环判断，但 C3 指标与 ownership 仍未闭合。

| 维度 | 分数（5） | 依据 |
| --- | ---: | --- |
| 岗位相关性 | 4.5 | VLA action、multimodal training、LIBERO eval 与目标岗位直接相关 |
| 机制深度 | 4.0 | 上游 audit 已覆盖 FAST/flow/H-D-K/norm/controller |
| 工程闭环 | 3.5 | Project snapshot 有 trainer/recipe/script/report/smoke/rollout diagnostics；formal raw logs/checkpoints 仍 remote-pending |
| 指标可信度 | 1.5 | official 96.85 可核；97.4 仅 committed report summary；formal 100k 为 report-supported |
| Ownership 清晰度 | 2.0 | per-file ledger 已建立，但没有新增个人角色确认或过程证据，因此不加分 |
| 抗追问能力 | 3.0 | 能讲 JSON/CE、LoRA、recipe、eager 与 deployment；lineage/FAST/protocol 仍是高风险分叉 |
| 合计 | **18.5 / 30** | 代码与工程证据已出现，C3 结果与 ownership 仍是主要短板 |

一票否决项：current resume/PDF 仍含未核验 97.4 与“高于官方”；archive/formal lineage 未闭合；formal Qwen checkpoint/load smoke 与 raw benchmark bundle 缺失。

## 10. 分阶段补强计划

| 时间 | 动作 | 完成标准 | 状态 |
| --- | --- | --- | --- |
| 半天 | 用已发现源码/报告回答 representation、recipe、formal-run 状态；逐项确认 ownership ledger；先降级投递稿 | 13 个 ledger 行有亲手/协作/工具/上游角色，强数字保持唯一 lineage | `ledger drafted / candidate confirmation pending` |
| 1 天 | 收集远端 model/config/diff、formatter/loss/parser、三条 formal run logs/checkpoints/load smoke | P0 manifest 至少关闭 4 项 | `待补做` |
| 3 天 | 从 raw episodes 重算四套件分数；冻结 official/local protocol diff | 97.4 可由命令和 records 重算 | `待补做` |
| 1 周 | 做 resolution×H×checkpoint 最小 ablation、多 seed 与 action roundtrip/controller replay | 因果与可比性不再依赖单点叙事 | `待补做` |

## 11. 下一切片

安全重写、Batch 1/2 的 12 张题卡、13-row ownership ledger 与 parser/round-trip negative-evidence gate 已完成。ledger 证明 custom path 不在 frozen upstream tree，并记录 root snapshot 的粗粒度 Git 边界；它没有替候选人完成角色确认。下一步优先做 ownership confirmation drill，或补 immutable formal checkpoint/generation/parser bundle；97.4、formal lineage 与 official comparison 继续作为高压待核项。

## 参考文献（References）

1. [optimized resume](../../../../output/mousongzhe_resume_optimized.html)，已安全重写 OpenPiVLA bullet。
2. [optimized resume PDF](../../../../output/pdf/mousongzhe_resume_after.pdf)，A4 单页安全重写派生版本，SHA `65b1dcd34cd6e357c6264effcf4b2683dea66508c6bc58315762b5e4c03ac74a`。
3. [OpenPiVLA 项目面试页](../../../03_openpivla_action_modeling.html)，archived/formal/Qwen/ownership claim 入口。
4. [resume restructure plan](../../../../output/resume_restructure_plan.md)，当前 OpenPiVLA 简历口径。
5. [research resume](../../../../output/mousongzhe_resume_research.html)，历史 action representation 与指标表述。
6. [engineering resume](../../../../output/mousongzhe_resume_engineering.html)，历史 trainer/collator 与 rollout 表述。
7. [VOL 03 π0/FAST/OpenPI source audit](../../sources/vol_03_pi0_fast_openpi_claim_to_code.html)；canonical [Markdown](../../sources/vol_03_pi0_fast_openpi_claim_to_code.md)，review [JSON](../../sources/vol_03_pi0_fast_openpi_claim_to_code.review.json)。
8. [VOL 03 Architecture / Execution audit](../../sources/vol_03_architecture_execution_claim_to_code.html)；canonical [Markdown](../../sources/vol_03_architecture_execution_claim_to_code.md)，review [JSON](../../sources/vol_03_architecture_execution_claim_to_code.review.json)。
9. [VOL 03 source ledger](../../sources/vol_03_vla_action_sources.md)，记录 archived 97.4 与 current formal run 边界。
10. Physical Intelligence, [`openpi@15a9616a` README](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/README.md)，Apache-2.0 code，访问 2026-07-17。
11. Physical Intelligence, [`openpi@15a9616a` LIBERO README](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/README.md)，lines 66–71 给出 official checkpoint 和 96.85 table，访问 2026-07-17。
12. Pertsch et al., [FAST: Efficient Action Tokenization for Vision-Language-Action Models](https://arxiv.org/abs/2501.09747), 2025。
13. 本地 formal trainer：`C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py`，SHA `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94`。
14. 本地 formal report：`C:\Users\mousongzhe\Project\openpivla_deployment\artifacts\vla_formal_reproduction_report_20260617.html`，SHA `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074`。
15. 本地部署记录：`C:\Users\mousongzhe\Project\openpivla_deployment\DEPLOYMENT.md`，SHA `c0a3dd0c0da8c1c0d36023046d5337900a71680b413657bc9b1062eef2eea14e`。
16. 本地 official LIBERO launcher：`C:\Users\mousongzhe\Project\openpivla_run_libero_official_eval.sh`，SHA `0bc9186f10b6a91ede65d933f1d99dab09827b2285ee1a437a96148dc35e13a3`。
17. [OpenPiVLA Batch 2 evidence freeze](../../sources/openpivla_batch2_evidence_freeze.html)；canonical [Markdown](../../sources/openpivla_batch2_evidence_freeze.md)，review [JSON](../../sources/openpivla_batch2_evidence_freeze.review.json)。
18. [OpenPiVLA Ownership Ledger](openpivla_ownership_ledger.html)；canonical [Markdown](openpivla_ownership_ledger.md)，review [JSON](openpivla_ownership_ledger.review.json)。
19. [OpenPiVLA JSON/CE + H/D Shape Contract Artifact Gate](../../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.html)；canonical [Markdown](../../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.md)，review [JSON](../../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.review.json)。
20. [OpenPiVLA Action JSON Parser / Round-trip Artifact Gate](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html)；canonical [Markdown](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.md)，review [JSON](../../sources/openpivla_action_json_parser_roundtrip_artifact_gate.review.json)。
