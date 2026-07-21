# VLA 面试准备仓库路线图

> 规划日期：2026-07-16；最近同步：2026-07-21  
> 当前状态：`G01 researching / G02 drafted / G05 VOL 03 44/44 unseen / Audit A-F facts reviewed / Audit A+C+E public facts PASS WITH WARNING / G06 VOL 04 44/44 unseen / Audit A-E reviewed / G07 VOL 05 44/44 unseen / G08 sources/knowledge/cards 20/20/20 + PER-001..020 triplets synced + PER-020 independent fact review PASS WITH WARNING / G09 five inventories + five ownership ledgers + cross-project evidence reconciliation + Robot Harness 28/40 raw + 6/10 support + 12-slot locator + 17 candidates 0 eligible + project cards 37 unseen / G10 sources/knowledge/card 12/12/12 + SYS-VLA-004 triplet synced + 12 unseen / global 280 cards unseen / 387 canonical triplets / 377 WARN + 10 PASS WITH WARNING / OpenPiVLA runtime rollout, LIBERO load-serve-client, ALOHA action-eval, local file manifest and LIBERO matched-probe preflight frozen / UWM base libero_90.pt local binary manifest frozen / target fine-tune checkpoint, fresh matched rerun and ownership closure still WARN`
> 目标方向：VLA / 具身智能算法 / 多模态机器人策略 / World Model Policy  
> 工作原则：逐波研究、逐页交付、逐题训练、逐条绑定证据；不做一次性大批量生成。

## 1. 本路线图解决什么问题

当前仓库已经有一版可信的项目面试材料，但内容主要围绕五个具体项目展开。下一阶段不是重写已有页面，而是补齐四个彼此联动的系统：

1. **VLA 知识系统**：覆盖机器人基础、VLA 架构、动作建模、数据、训练、World Model、评估、部署与安全。
2. **原子化题库**：每道题有稳定 ID、分层答案、追问树、项目挂钩和训练状态，而不是把问题散落在多个页面里。
3. **项目证据系统**：简历 claim、个人贡献、代码/日志/指标、风险边界和口述答案逐项对应。
4. **持续训练系统**：一次只训练一个高价值分支，记录答题表现、风险变化和下一轮入口。

这里的 “flow matching” 有两层含义：

- 工作流上，持续读取当前仓库状态，只生成最能缩小当前差距的下一小步。
- 技术栈上，把 Flow Matching / Diffusion Policy 作为 VLA 动作生成的重要知识模块严谨准备。

## 2. 当前仓库基线

### 2.1 已有资产

- 主简历：`output/mousongzhe_resume_optimized.html`。
- 五个项目页：Robot Harness、OPD / VLM Grounding、OpenPiVLA、Cosmos / WAM、UWM / LIBERO。
- 项目页已有：研究叙事、真实性边界、简历三档、2-3 分钟口述稿、追问树、高压回答和补证据清单。
- 总索引：`interview_materials/index.html`。
- 简历重构与证据边界：`output/resume_restructure_plan.md`。

### 2.2 当前优势

- 项目不是泛泛 STAR，而是已经能讨论输入输出、训练目标、评估协议和失败归因。
- 多个页面主动承认不能证明的内容，例如 OPD 缺少完整 ablation、LIBERO 高分不等价于真机泛化。
- UWM 页面区分 strict fixed-init 与 reset-style 结果，真实性边界较清晰。
- 已能把项目问题自然转入 action token、normalization、mask/routing、closed-loop eval 等技术八股。

### 2.3 主要缺口

| 维度 | 当前状态 | 下一步 |
| --- | --- | --- |
| VLA 知识覆盖 | 项目驱动，缺少独立、完整的知识树 | 建立 P0/P1/P2 知识图谱与模块化 HTML |
| 题库 | 问题散落在五个项目页，缺少 ID、去重和训练状态 | 建立原子 Question Card 与主索引 |
| 来源 | 五页外部来源链接数约为 0 / 0 / 3 / 2 / 1 | 先做 GitHub 与官方资料 Source Scout，再补来源 |
| 证据分类 | 已有“危险边界”，但公源、本地证据、推断、未核实尚未统一标记 | 建立 Evidence Manifest |
| 简历一致性 | 少数强结果与实际 run 来源需要进一步对齐 | P0 先审 WAM、OpenPiVLA、Harness 三处高风险表达 |
| 训练闭环 | 有答案，没有长期掌握度、复习记录和面试复盘状态 | 建立 coaching state 与练习日志 |
| HTML 质量 | 页面可读，但目录、公式解释、引用密度和证据标签不完全统一 | 每次只升级当前波次涉及的页面 |

### 2.4 P0 真实性风险

以下不是断言简历有误，而是下一阶段必须优先核对的 claim 边界：

1. **Cosmos / WAM**：历史项目页提到 local 0-success，同时旧版简历出现 0.90-0.95 / 0.75；2026-07-17 已完成 optimized resume 安全降级，数字全部退出投递 bullet。checkpoint/protocol provenance 与 raw artifacts 仍待补，因此项目继续保持 WARN。
2. **OpenPiVLA**：真实 deployment repo 已发现并完成第一轮 direct audit。formal trainer、Qwen3-VL + PEFT LoRA、JSON/causal-CE、DROID/MindCube 三类 recipe、smoke/report/diagnostic artifacts 可直接核验；三条 100k 只到 report-supported/remote-referenced，97.4 只到 archive-summary-only，archive→formal lineage、raw benchmark bundle 与 ownership 仍缺。optimized resume/PDF 与项目页已安全重写，投递 release blocker 关闭。
3. **Robot Harness**：项目页说明 Codex 承担了大量工程落地。回答必须把个人贡献稳定落在问题定义、约束取舍、数据/reward/eval 设计和结果归因，不能暗示所有实现均为本人手写。
4. **OPD**：现有证据支持组合效果，不足以把提升单因果归于 OPD；需要继续保留 SFT-only、单 teacher、合成比例 ablation 的缺口。
5. **UWM**：74.4% strict、92.8% reset-style 和官方约 0.79 必须固定标注协议，不允许跨协议比较。

### 2.5 参考骨架：`WinstonJQ/embodied-interview-qa`

已审计参考仓库当前 commit：`fef782564647a5e89e7bed1f60d20b0588c6b3ae`（2026-07-11）。它的可复用骨架是：

- `docs/index.html` 作为主册，先看全局卷目录、状态和使用方式。
- 每卷使用 `Markdown canonical source + 单文件折叠 HTML + review.json`。
- L1 / L2 / L3 难度标签、题源/频次说明和每题“易错”一句，支持快速自测。
- `Phase 1 → 用户审题目清单 → 起草 → 独立审查 → 渲染 → 更新索引` 的流水线。
- 同一份内容同时支持桌面阅读和手机端 `<details>` 折叠复习。

本仓库采用“借骨架、换内容合同”的方式：

| 参考仓库做法 | 本仓库的适配 |
| --- | --- |
| 八卷高频短答案 | 保留 8 个主题卷，但每卷下拆知识模块；不以 425 题作为数量目标 |
| 每题 ≤350 字 | 题库层保留短答案；知识层另有公式、伪代码、实现映射和项目证据 |
| 公开面经频次 | 作为题目优先级信号；技术事实优先使用论文、官方 repo、benchmark 与本地证据 |
| HTML 直接阅读 | 保留单文件、自包含、移动端折叠和总索引 |
| review.json | 为每一卷保存质量检查、来源、修订轮次和未解决风险 |
| 独立 AI 审查 | 采用“内容起草”和“事实/证据审计”分离的质量门，不把未核实内容标为 PASS |

不直接复制参考仓库的答案、频次或个人信息；所有与你的经历有关的 claim 必须回到本地证据合同。

## 3. 目标信息架构

短期不移动现有五个项目页，避免破坏链接和未提交修改。新知识、题库和状态统一放在 `interview_materials/vla/` 下；现有项目页先作为兼容层，后续只通过索引链接，不做目录级大搬迁。

```text
interview_materials/
├── index.html                         # 现有总入口，后续增量更新
├── vla_interview_roadmap.md           # 本路线图
├── vla/
│   ├── README.md                      # VLA 子仓库说明、状态和贡献规则
│   ├── sources/
│   │   ├── README.md
│   │   ├── 00_github_guidance_and_sources.md
│   │   ├── 00_github_guidance_and_sources.html
│   │   └── 00_github_guidance_and_sources.review.json
│   ├── knowledge/
│   │   ├── README.md
│   │   ├── 00_vla_knowledge_map.md/.html
│   │   ├── vol_01_foundations.md/.html
│   │   ├── vol_02_il_rl_posttraining.md/.html
│   │   ├── vol_03_vla_action.md/.html
│   │   ├── vol_04_world_model_sim2real.md/.html
│   │   ├── vol_05_engineering_eval.md/.html
│   │   ├── vol_06_perception_grounding_nav.md/.html
│   │   ├── vol_07_project_deepdives.md/.html
│   │   └── vol_08_coding_system_design.md/.html
│   ├── questions/
│   │   ├── README.md
│   │   ├── 00_master_question_index.md/.html
│   │   ├── vol_01_foundations.md/.html
│   │   ├── vol_02_il_rl_posttraining.md/.html
│   │   ├── vol_03_vla_action.md/.html
│   │   ├── vol_04_world_model_sim2real.md/.html
│   │   ├── vol_05_engineering_eval.md/.html
│   │   ├── vol_06_perception_grounding_nav.md/.html
│   │   ├── vol_07_project_deepdives.md/.html
│   │   └── vol_08_coding_system_design.md/.html
│   ├── evidence/
│   │   ├── README.md
│   │   ├── evidence_manifest.md
│   │   └── claim_reconciliation.md
│   └── practice/
│       ├── README.md
│       ├── coaching_state.md
│       ├── drill_log.md
│       └── interview_postmortems.md
└── 01-05_*.html                     # 现有项目页，暂不移动
```

文件名是当前建议，不是一次性创建清单。只有进入对应波次时才创建文件。`*.md` 是可审计的 canonical source，`*.html` 是浏览与复习产物，`*.review.json` 是质量门记录；三者必须保持同一版本，不单独手改生成 HTML。

### 3.1 持续目标与里程碑

本任务已设置为持续目标；只有所有必需里程碑通过验收后才标记完成。

| Goal ID | 目标 | 验收条件 | 状态 |
| --- | --- | --- | --- |
| G00 | 仓库骨架与执行协议 | 参考仓库审计完成；`vla/` 目录、命名、canonical source 和 review 规则明确 | done |
| G01 | Source Scout | GitHub/官方来源表完成；每个 P0/P1 节点至少有 primary source；license/freshness 可追踪 | researching |
| G02 | Knowledge Map | 八卷、子模块、前置依赖、项目挂钩、Question ID 空间和优先级完整 | drafted |
| G03 | VOL 01 Foundations | DL/Transformer、RL 基础、机器人学、控制与坐标系达到 reviewed + drilled | fact_reviewed_candidate / knowledge+cards 39/39 / completion_reconciled / 39 unseen / WARN |
| G04 | VOL 02 IL / RL / Post-training | BC/DAgger、offline/online RL、PPO/GRPO、SFT/DPO 与 VLA 训练关系达到 reviewed + drilled | fact_reviewed_candidate / 40 unseen / WARN |
| G05 | VOL 03 VLA / Action | VLA 架构、action token、FAST、ACT、Diffusion/Flow Matching、chunk/replan 达到 reviewed + drilled | completion_reconciled_candidate / knowledge+cards 44/44 / Audit A-F public facts reviewed / local gates WARN / 44 unseen / WARN |
| G06 | VOL 04 World Model / Sim2Real | dynamics/world model、value/planning、多目标训练、domain gap 达到 reviewed + drilled | source_registry_reconciled / aggregate knowledge+cards 44/44 unseen / Audit A–E independently reviewed / Audit D 10 PDF + 12 probes + five-project boundary complete / local runtime/ownership/oral WARN |
| G07 | VOL 05 Engineering / Eval | 数据 pipeline、分布式训练、部署、closed-loop eval、failure debugging 达到 reviewed + drilled | completion_audited / knowledge 44/44 / cards 44/44 unseen / Batch 1+2A official-doc reviewed / ENG-012..022 + EVAL-003..022 source+knowledge+card drafted / WARN |
| G08 | VOL 06 Perception / Grounding / Nav | VLM grounding、point/box、3D perception、VLN/ObjectNav 与多视角输入达到 reviewed + drilled | coverage_contract_frozen / planned 20 / sources 20/20 / knowledge 20/20 / cards 20/20 / 20 unseen / page coverage complete, oral drills pending / WARN |
| G09 | VOL 07 Project Deep Dives | 五个项目完成 truth/evidence/claim reconciliation、2 分钟叙事和高压追问 | researching / inventories 5/5 / ownership ledgers 5/5 / Robot Harness 28/40 raw + 6/10 support + 12-slot recovery locator / project cards 37 / UWM ActionHeadFix raw train→closed-loop slice added / WAM safely downgraded / WARN |
| G10 | VOL 08 Coding / System Design | VLA 训练/推理系统设计、机器人系统设计与必要手撕题达到 reviewed + drilled | coverage_contract_frozen / planned 12 / sources 12 / knowledge 12 / cards 12 / SYS-VLA-004 triplet synced + 12 complete cards/unseen / WARN |
| G11 | 集成与模拟面试 | 主索引无断链；题库去重；P0 无高危穿帮点；完成至少一轮综合模拟与复盘 | todo |

状态只允许按真实证据推进：`todo → researching → drafted → reviewed → drilled → done`。HTML 生成不等于模块完成，至少还要通过事实审查和一轮实际口述训练。

## 4. GitHub Source Scout 协议

第一个执行阶段只做来源调研，不直接写大篇 VLA 正文。

### 4.1 检索类别

1. VLA / robot learning 面试准备、课程笔记和 topic map。
2. 官方 VLA 模型仓库、model card、训练和推理文档。
3. Action tokenization、Diffusion Policy、Flow Matching、action chunking 的官方实现。
4. Open X-Embodiment、DROID、BridgeData、LIBERO、RoboCasa 等数据与 benchmark 官方资料。
5. World Model、planning、value / reward conditioning 相关官方实现。
6. 机器人基础、控制、坐标系、kinematics、sim2real 与安全的高质量复习资料。
7. 大模型/多模态算法面试题中可迁移到 VLA 的部分：Transformer、VLM、SFT/RL、分布式训练、推理优化。

### 4.2 搜索词簇

```text
VLA interview questions
vision language action interview preparation
robot learning interview guide
embodied AI interview questions
VLA awesome list
robot policy action tokenization
diffusion policy flow matching action
LIBERO evaluation protocol
RoboCasa policy evaluation
world model robot policy
OpenVLA / Octo / RT-2 / pi0 / pi0.5 official repository
```

实际检索会根据 2026-07-16 的项目状态扩展，不预设某个仓库一定入选。

### 4.3 采信标准

| 字段 | 判定问题 |
| --- | --- |
| Source type | 官方 repo / 论文 repo / 课程 / interview repo / 二手笔记？ |
| Authority | 是否能回溯论文、官方文档或源码？ |
| Maintenance | 最近更新时间、issue 状态、文档是否与当前版本匹配？ |
| Coverage | 能覆盖哪个知识节点或面试问题？ |
| Answer quality | 是否解释机制、trade-off 和 failure case，而非只有定义？ |
| License | 是否允许引用、改写或仅能做链接索引？ |
| Reproducibility | 是否有代码、config、数据契约、eval protocol？ |
| Decision | primary / supporting / inspiration-only / reject |

Stars 只作为弱信号，不作为质量结论。每个入选仓库记录 URL、commit/tag、访问日期、license、用途和限制。

### 4.4 Source Scout 产物

`vla/sources/00_github_guidance_and_sources.html` 至少包含：

- 搜索范围与截止日期。
- 候选仓库评分表与淘汰原因。
- 最终 primary sources 与 supporting sources。
- 来源到知识模块的映射。
- 来源到五个项目页的映射。
- license / freshness / uncertainty 提示。
- 下一页 `00_vla_knowledge_map.html` 的依据。

## 5. VLA 知识覆盖模型

不按“文章数量”判断完整度，而按知识节点是否闭环判断。优先级含义：

- **P0**：VLA 岗位高频必会，回答不上会直接暴露基础不足。
- **P1**：区分普通候选人与强候选人的机制、实验和系统深度。
- **P2**：根据具体 JD、公司和项目再扩展。

| 模块 | 优先级 | 核心内容 | 主要项目挂钩 |
| --- | --- | --- | --- |
| Robotics / Control Foundations | P0 | observation/state/action、坐标系、FK/IK、控制频率、controller、closed loop | OpenPiVLA、UWM |
| VLA Architecture Landscape | P0 | encoder-decoder、VLM backbone、action expert、cross-attention、policy head、模型家族比较 | OpenPiVLA、WAM/UWM |
| Action Representation | P0 | continuous regression、bin/token、FAST、chunking、diffusion、flow matching、denorm | OpenPiVLA、UWM |
| Multimodal Perception / Grounding | P0 | image token、region/point/box、spatial relation、proprio、camera views | OPD、OpenPiVLA |
| Robot Data | P0 | trajectory schema、episode/window、sampling、normalization、augmentation、leakage、mixture | 全部项目 |
| Training Objectives | P0 | BC/SFT、autoregressive、diffusion/flow loss、multi-task mask、LoRA、RL/post-training | Harness、OpenPiVLA、WAM |
| Inference / Closed-loop | P0 | policy server、action chunk、replan、latency、termination、success predicate | OpenPiVLA、UWM |
| Evaluation / Failure Analysis | P0 | offline proxy、online success、fixed-init、seed、置信区间、bad case taxonomy | WAM、UWM |
| World Models / Planning / Value | P1 | dynamics/world prediction、value、latent rollout、planning、辅助目标干扰 | WAM、UWM |
| Scaling / Systems | P1 | distributed training、checkpoint、mixed precision、data loader、跨硬件迁移 | OpenPiVLA、WAM/UWM |
| Sim2Real / Safety | P1 | domain gap、calibration、latency、contact、安全约束、恢复策略 | Harness、UWM |
| Current Literature Comparison | P1 | 模型路线、数据规模、action head、训练目标、benchmark 的可比表 | 所有项目 |
| Company/JD Specials | P2 | 真机平台、teleoperation、RL、world model、数据引擎等专项 | 等 JD 后决定 |

## 6. 单页 HTML 交付合同

每个知识页必须同时满足“能学、能讲、能追问、能回到项目”：

1. `问题（Question）`：本页回答哪些面试问题。
2. `知识地图位置`：前置知识、后续知识和项目挂钩。
3. `通俗直觉`：先用普通语言解释。
4. `严谨定义`：术语、张量、公式和假设。
5. `模型/数据 Pipeline`：带注释伪代码或结构图。
6. `Trade-off`：何时有效、何时失败、如何选型。
7. `实现映射`：对应官方代码/config，或明确尚未映射。
8. `项目映射`：连接到你的 OpenPiVLA、WAM、UWM、OPD 或 Harness。
9. `面试题卡`：从本页抽取高价值原子问题，不复制整页正文。
10. `证据边界`：公源事实、本地证据、本地推断、未核实分开。
11. `参考文献`：论文、官方 repo/doc 优先，二手资料仅补充。
12. `状态`：draft / reviewed / drilled / needs-update 与最后更新时间。

质量门槛：一个显示公式后必须解释变量、直觉和代码/训练映射；一个强 claim 必须有来源；一个指标必须说明协议和可比性。

## 7. 原子题卡协议

每道题使用稳定 ID，建议格式：

```text
VLA-ARCH-001
VLA-ACT-001
VLA-DATA-001
VLA-TRAIN-001
VLA-WM-001
VLA-EVAL-001
PROJ-OPENPIVLA-001
PROJ-WAM-001
```

### 7.1 难度层级

1. **L1 定义**：是什么，解决什么问题。
2. **L2 机制**：为什么工作，数据如何流动。
3. **L3 数学/实现**：公式、shape、loss mask、关键代码。
4. **L4 Trade-off / Bad Case**：何时失败，如何诊断。
5. **L5 设计题**：换数据、换平台、规模变大或线上异常时怎么改。

### 7.2 Question Card 字段

| 字段 | 内容 |
| --- | --- |
| ID / Tags | 模块、难度、项目、JD 标签 |
| Question | 面试官原始问法 |
| Why asked | 面试官在判断什么 |
| 30s answer | 一句话结论 + 核心机制 |
| 2min answer | 机制、公式/实现、trade-off、例子 |
| Project hook | 如何自然连接到你的真实项目 |
| Follow-up tree | 回答 A/B/不清楚时的追问 |
| Dangerous answer | 会夸大、偷换协议或暴露薄弱点的答法 |
| Evidence | 论文/官方代码/本地 artifact |
| Confidence | High / Medium / Low |
| Practice state | unseen / weak / pass / strong / stale |

题目总量服从覆盖和去重，不追求虚高数字。预计 P0/P1 核心题与项目题去重后约 180-260 道，但只有通过题卡合同的题目才进入主库。

## 8. 项目证据合同

每个项目必须完成以下链路：

```text
Resume claim
→ 真实贡献边界
→ 公源与本地证据
→ 输入/输出与关键代码
→ 训练/评估协议
→ 指标可比性
→ Bad case
→ 追问树
→ 30 秒 / 2 分钟 / 深挖回答
→ 补证据动作
```

Evidence Manifest 至少记录：

- claim 原文与所在简历版本。
- 状态：做过 / 参与 / 了解 / 待补做 / 不能写。
- 证据等级：C0-C3。
- 本地 artifact：代码、config、日志、checkpoint、eval summary、视频或设计记录。
- 公源依赖：论文、官方 repo、benchmark 文档。
- 风险：归因、协议、统计、贡献边界或保密问题。
- 处理：保留、降级、补做后写、不写。

## 9. Flow-Matched 执行波次

每个波次把知识、项目、题库和训练一起向前推进，不先写完百科再回头准备项目。

### Wave 0：Source Scout 与总图

1. GitHub / 官方来源调研。
2. 生成 `vla/sources/00_github_guidance_and_sources.html`。
3. 生成 `vla/knowledge/00_vla_knowledge_map.html`，只做知识图谱和优先级，不展开所有正文。
4. 建立 master question index 的空结构与 ID 规则。

退出条件：P0/P1 知识节点、主要来源、五项目挂钩已经可追踪。

### Wave 1：机器人基础、动作表示与 OpenPiVLA

1. Robotics / control foundations。
2. Action representation：tokenization、FAST、diffusion、flow matching、chunk/replan。
3. 核对 OpenPiVLA 的 97.4% 证据链、formal training 证据链和个人贡献。
4. 增量加入动作/控制题卡。
5. 进行 5-8 道口头 drill，再根据回答回写。

### Wave 2：评估协议、闭环诊断与 UWM

1. offline vs online、success predicate、fixed-init、seed、rollout 数和统计不确定性。
2. 对齐 UWM strict / reset-style / official 三套结果。
3. 建立 failure trajectory taxonomy。
4. 进行评估设计题 drill。

### Wave 3：World Model、多目标训练与 WAM

1. world prediction、value、action imitation、gradient conflict、mask/routing。
2. 严格区分 proxy MSE、官方 baseline、本地训练和 online rollout。
3. 完成 WAM claim reconciliation。
4. 训练“失败项目如何可信讲”的高压问题。

### Wave 4：VLM Grounding、数据分布与 OPD

1. point/box/text/bool、坐标协议、teacher routing、pseudo-label noise。
2. 补数据质量、split/leakage、SFT-only/teacher ablation 设计。
3. 只在证据允许的范围内解释 OPD 组合收益。
4. 训练实验设计和因果归因问题。

### Wave 5：SFT/GRPO、工具调用与 Robot Harness

1. schema、reward、holdout eval 的角色区分。
2. SFT、online GRPO、tool/arg/scope metric 与真实机器人能力边界。
3. 核对 Codex 辅助实现与个人 contribution boundary。
4. 训练 ownership、系统设计和部署缺口问题。

### Wave 6：系统、Sim2Real、安全与跨项目综合面

1. policy server、latency、throughput、checkpoint、跨硬件训练和恢复。
2. sim2real、视觉/控制/接触误差、安全边界。
3. 跨项目比较：为什么这个项目用 token action，另一个用 world/value，多种评估为何不可直接比较。
4. 形成 VLA system design 和 research proposal 类题库。

### Wave 7：JD 定制与模拟面试

1. 收集具体 JD，做能力权重与简历证据映射。
2. 按公司/团队生成薄的定制层，不复制核心知识库。
3. 一次只问一个问题；每轮 5-8 题。
4. 记录 Substance、Structure、Relevance、Credibility、Differentiation 五维评分。
5. 每轮更新高危穿帮点、需要降级/升级的表达和下一轮分支。

## 10. 单次迭代协议

每次会话默认只推进一个主交付物：

```text
Sense
  读取路线图、现有页面、用户新增材料和训练状态
Match
  选择当前最高价值缺口，不按文件编号机械推进
Research
  搜集并核验该页所需 primary sources
Write
  新建或更新 1 个主 HTML；必要时同步小型索引/题卡增量
Verify
  检查结构、公式、链接、引用、证据边界和浏览器渲染
Drill
  从该页选择 5-8 个问题，逐题训练
Reconcile
  根据答题和新证据更新项目 claim、风险和掌握度
Index
  更新总索引、coverage 和下一步
```

默认不在一次迭代中同时生成多个完整知识页。基础设施修订、索引更新和一页相关项目的小幅修订可以随主交付物一起完成。

## 11. 质量门槛与自动检查

### 11.1 内容检查

- 每个 P0 知识节点至少有定义、机制、公式/实现、trade-off、bad case、项目挂钩和题卡。
- 每个项目强 claim 都能映射到证据或被显式降级。
- 不把单点最优写成稳定性结论，不把不同协议的成功率直接比较。
- 不把上游公开设计写成本地原创，不把 Codex/同事实现写成本人手写。
- 不用“显著提升”“生产级”“高并发”等词替代证据。

### 11.2 HTML 检查

- 单文件可直接打开，UTF-8、一个 `<h1>`、目录锚点有效。
- MathJax delimiter 正确；显示公式后有变量、直觉和代码映射。
- 代码/伪代码含注释。
- 强 claim 有来源；不确定内容有显式 warning。
- 表格在窄屏可横向滚动。
- 新页面经过实际浏览器渲染检查。

### 11.3 题库检查

- ID 唯一，题意去重。
- 题目能映射知识节点、项目或 JD，不能进入“无归属题池”。
- 30 秒答案先给结论，2 分钟答案不写成论文摘要。
- 关键问题有危险/可过/强回答边界。
- 练习状态按实际回答更新，不能因为页面生成完成就标记为掌握。

## 12. 完成定义

仓库不是在“HTML 数量够多”时完成，而是在以下条件同时满足时进入稳定维护：

1. P0 知识节点全部达到 `reviewed`，并至少完成一轮 drill。
2. P1 节点按目标 JD 覆盖，无明显关键空洞。
3. 五个项目页均完成 Truth Boundary、Evidence Contract、Question Tree 和 2-3 分钟叙事核对。
4. 每条主简历强 claim 有证据、协议和个人贡献边界。
5. 主题库无明显重复，所有题目有稳定 ID 和掌握状态。
6. 能分别完成 VLA 基础面、项目深挖面、系统/场景面和研究讨论面。
7. 最近模拟面试不再出现 P0 高危穿帮点。

## 13. 最近进展与三个可执行增量

当前 authoritative snapshot（由 `vla/tools/validate_academic_repo.py` 于 2026-07-21 重算）：387 个 canonical Markdown 均有匹配 HTML/review，SHA、H1、公式、链接与 ARIS academic template 检查全部通过；题库 280 张且 ID 唯一，全部 `unseen`，尚未创建 `coaching_state.md`。八卷当前计划覆盖为 VOL 01 `39`、VOL 02 `40`、VOL 03 `44`、VOL 04 `44`、VOL 05 `44`、VOL 06 `20`、VOL 08 `12`，VOL 07 五项目题卡合计 `37`（OpenPiVLA `12`，其中 Batch 1 `8` + Batch 2 `4`；Robot Harness `8`、OPD `9`、WAM `4`、UWM `4`）。五项目 claim-evidence inventory、ownership ledger 与 P0 bundle audit 均为 `5/5`；现有 review 分布为 `377 WARN + 10 PASS WITH WARNING`，因此“页面覆盖完成”仍不等于 reviewed/drilled/done。

当前只保留三个可执行入口，避免历史增量记录误导调度：

1. **优先入口：一题真实口述。** 当前排队题为 `PROJ-OPENPIVLA-007`，回答后再创建训练记录、评分并决定是否回写题卡；没有真实回答时不改变 mastery。
2. **证据入口：一个 immutable runtime bundle。** OpenPiVLA 优先补 checkpoint/norm-stats SHA、effective argv、server response、raw observation/action 与 scorer；UWM/WAM 优先补 checkpoint fresh-load、versioned scorer、episode trace 和 ownership confirmation。
3. **集成入口：G11 综合模拟。** 只有在至少完成一轮基础面、项目深挖、系统设计与复盘后，才评估 G03–G10 是否能从 WARN/candidate 升级；静态 validator PASS 不能替代口述与项目真实性门。

下面保留的是 append-only 历史切片，用于追溯仓库如何从早期 195/265 等中间计数演进到当前 280 题；其中的“下一步”只代表当时决策，不覆盖上述 authoritative snapshot。

### 当前切片：VOL 04 UWM Audit B 独立事实复核（已完成，WARN）

- 已生成 [`vol_04_uwm_independent_fact_review`](vla/sources/vol_04_uwm_independent_fact_review.html) 及 canonical Markdown/review；从冻结 commit 重新获取 `configs/model/uwm.yaml`、`models/uwm/uwm.py`、`experiments/uwm/train.py`、`train_robomimic.py`、LIBERO wrapper、README 和官方项目页。
- 独立确认 dual modality、独立 timestep、action-free video 的最大 timestep、`action_mask` 不等于 action loss mask、sampling mode、validation metric ladder 与 checkpoint/license 边界；不升级本地 UWM 数字或个人 ownership。
- 该 source slice 的 review JSON 已更新为新的 canonical SHA；浏览器 `file://` 视觉检查仍 BLOCKED，不能以静态检查冒充视觉验收。

### 当前切片：VOL 04 WM-015 UWM Video–Action Coupling（已完成，WARN）

- 已生成 `knowledge/vol_04_world_model_sim2real_wm015.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm015.md/.html/.question_list.md/.review.json`；覆盖共享 video/action diffusion transformer、独立 timestep、sampling mode、action-mask/loss 边界与项目 truth boundary。
- WM-015 题卡保持 `unseen`；VOL 04 已同步到 knowledge/cards 19/44，全局题库同步到 195，全部 unseen；未创建 `coaching_state.md`。
- 下一步只做一次 WM-015 真实口述；若继续内容建设，则先对 WM-016 做 source-first 冻结，不能批量展开 WM-016..038。

### 当前切片：VOL 04 WM-016 Joint Objective Source Freeze（已完成，WARN）

- 已生成 `sources/vol_04_wm016_joint_objective_source_freeze.md/.html/.review.json`；冻结 UWM shared DiT / dual timestep 与 Cosmos/WAM latent slot / EDM / routing 的 claim-to-code 边界。
- 已明确 condition mask、sample routing、target loss mask、reduction、prediction target 和 metric ladder 不可互换；P0/P1 gradient、mask A/B、paired ablation、checkpoint lineage 与 scheduler smoke 仍为 pending。
- 本切片不生成 WM-016 knowledge/card；下一步只能生成一个 WM-016 knowledge node，或先进行 WM-015 真实口述，不能批量展开 WM-016..038。

### 当前切片：VOL 04 WM-017 Heterogeneous Embodiment Schema Source Freeze（已完成，WARN）

- 已生成 `sources/vol_04_wm017_heterogeneous_schema_source_freeze.md/.html/.review.json`；冻结 Open X-Embodiment RLDS/RT-1-X README 与 UWM LIBERO/DROID 的 camera、state、action、timestamp、horizon、valid/presence mask、normalizer 和 per-source loss 边界。
- 已记录 Open X README/LICENSE 的 frozen commit 与 SHA fingerprint；adapter manifest、normalize round-trip、terminal-mask A/B、per-embodiment evaluation 与个人项目统一证据仍 pending。
- 本切片已完成 WM-017 knowledge/card；下一步进行 WM-015/016/017 真实口述，WM-018..038 继续后置。

### 当前切片：VOL 04 WM-018 Prediction Horizon Source Freeze（已完成，WARN）

- 已生成 `sources/vol_04_wm018_prediction_horizon_source_freeze.md/.html/.review.json`；冻结 observation/prediction/execution/replan/imagination 五条时间轴，并对照 Diffusion Policy、ACT、Cosmos/WAM 与 UWM 的 horizon/chunk/replan 实现边界。
- 已加入物理时间换算、过短/过长 trade-off、per-offset error、action-age/latency、terminal padding 与 matched horizon sweep；本地 A/B、closed-loop traces 和个人项目 lineage 仍 pending。
- 本切片不生成 WM-018 knowledge/card；下一步只生成一个 WM-018 knowledge node，WM-019..038 继续后置。

### 当前切片：VOL 04 WM-018 Prediction Horizon Knowledge（已完成，WARN）

- 已生成 `knowledge/vol_04_world_model_sim2real_wm018.md/.html/.review.json`；覆盖五条 horizon 时间轴、物理时间换算、短/长 horizon trade-off、Diffusion Policy/ACT/Cosmos/UWM 实现对照与 matched sweep。
- 本切片未生成 WM-018 题卡；本地 horizon A/B、closed-loop trace 与个人项目 lineage 仍 pending。下一步可生成一张 WM-018 unseen 题卡，或先进行 WM-015/016/017 真实口述。

### 当前切片：VOL 04 WM-019 Metric Boundary Source Freeze（已完成，WARN）

- 已生成 `sources/vol_04_wm019_metric_boundary_source_freeze.md/.html/.review.json`；冻结 PSNR/SSIM/FVD、latent/action loss、one-step/open-loop、WorldGym proxy、simulator success 与 real closed-loop 的 metric ladder。
- 已明确 episode/row/step 统计单位、checkpoint/schema/normalizer/horizon/reset/controller/seed/predicate protocol tuple 与不可外推边界；per-offset、proxy-vs-simulator paired test、denominator/checkpoint artifacts 仍 pending。
- 本 source-freeze 切片没有同时生成 knowledge/card；后续独立 knowledge 与 card slices 现已完成且题卡保持 unseen，WM-020..038 继续后置。

### 当前切片：VOL 04 WM-019 Metric Boundary Knowledge（已完成，WARN）

- 已生成 `knowledge/vol_04_world_model_sim2real_wm019.md/.html/.review.json`；覆盖 PSNR/SSIM/FVD、latent/action loss、teacher-forced/open-loop、WorldGym proxy、simulator/real closed-loop 的证据阶梯与统计单位。
- VOL 04 已同步到 knowledge 21/44、cards 21/44，题库总数在本轮前为 197；新增 WAM 项目题卡后全局为 198，全部 `unseen`；paired validation、episode artifacts 与真实口述仍 pending。
- WM-019 题卡已单独生成并保持 `unseen`；下一 bounded slice 只进行 WM-015..019 真实口述或补 paired/evidence artifacts，WM-020..038 继续后置。

### 当前切片：VOL 04 WM-019 Project Metric Artifact Gate（已完成，WARN）

- 已生成 `sources/vol_04_wm019_project_metric_artifact_gate.md/.html/.review.json`；按 UWM/LIBERO 与 Cosmos/WAM inventory 盘点 metric ladder、protocol tuple、paired validation、denominator 和 ownership 边界。
- UWM 的 `186/250` 保持 `user-confirmed / protocol-limited`，缺 checkpoint/normalizer/init/episode/scorer bundle；WAM 新发现一组 CoffeePressButton diagnostic bundle，但 checkpoint 仍未验证，历史 MSE/success/uplift/root-cause 不升级。
- 已生成 `evidence/projects/wm019_wam_artifact_manifest.md/.html/.review.json`：base/trained manifest、action trace、两条 raw video 与 rollout log 已哈希登记；trained video 位于 alternate output root，checkpoint binary、完整 denominator 和 target metric 仍缺。
- 已生成 `evidence/projects/wm019_wam_action_trace_paired_diagnostic.md/.html/.review.json`：同一 CoffeePressButton episode 0 的两份 trace 均为 300 行，policy/env shape 为 300×7/300×12、无非有限值、success 字段均为 false；逐步 `MAE=0.3100783611`、`RMSE=0.3906446459` 仅表示 trace geometry，不是 action loss 或 uplift。
- 已生成 `evidence/projects/wm019_wam_future_metric_paired_diagnostic.md/.html/.review.json`：同一离线 episode 的两个 checkpoint label 有 future-only PSNR `8.5813→8.2140`、SSIM `0.04527→0.04286`，sample_count=1；这是 offline visual proxy，不升级为 action/simulator/real success。
- 已生成 `evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.md/.html/.review.json`：离线 `iter_000010000` metrics 与 trained rollout manifest 的 checkpoint path exact match（path SHA `6CAE0B...`），但 seed、episode、horizon 和 denominator 不同，因此仅作为 provenance bridge，不做 proxy-success correlation。
- 已生成 `questions/proj_wam.md/.html/.question_list.md/.review.json` 的 `PROJ-WAM-001`：把 manifest、trace geometry、offline visual proxy、checkpoint path bridge 与 simulator outcome 分层成一张项目题卡；短答 167 字、机制展开 349 字，保持 `unseen/WARN`。
- 已生成 `evidence/projects/wam_ownership_ledger.md/.html/.review.json`：13 行 per-file/per-decision ledger 区分 upstream mechanism、Project snapshot、RoboCasa launcher、CoffeePressButton partial artifact、历史 claim 与 candidate/operator/reviewer 边界；状态 `WARN / candidate_confirmation_pending`。
- 已新增 `PROJ-WAM-002` ownership 题卡；WAM 题卡累计 2 张，全部保持 `unseen`，全局题库同步为 256；短答 ≤180 字、机制展开 ≤350 字，review JSON 与 master index 已同步。
- 本切片只把一组 CoffeePressButton manifest/trace/video 登记为 trace-level diagnostic，不把 WAM 历史 MSE、success、uplift 或 root-cause claim 恢复为强结论，也没有创建 coaching state。下一 bounded slice 只进行两题 WAM ownership/diagnostic 真实口述，或补一个 P0 checkpoint/episode/metric artifact；不生成 WM-020..038。

### 当前切片：OpenPiVLA Batch 1（已完成，WARN）

- OpenPiVLA 12 条 claim 已分级；official OpenPI 96.85 已由 frozen README 核实；Qwen JSON/causal-CE、三类 recipe、formal trainer、smoke/report/diagnostic artifacts 已进入 local-direct，three 100k 为 report-supported/remote-referenced，97.4 为 archive-summary-only。
- 安全重写已完成：简历/PDF 保留 direct engineering evidence，移除 97.4 与 official 96.85 的强比较、无条件 100k 完成态和 formal Qwen rollout 暗示。
- 已生成并渲染 `PROJ-OPENPIVLA-001..008`，覆盖 Qwen/LoRA、JSON/causal-CE、recipe、formal completion、97.4 比较边界、rollout artifact 与 ownership；短答案均 ≤180 字、机制展开均 ≤350 字，review JSON 与主索引已同步。
- 97.4、formal lineage、official comparison 与 ownership 继续保持高压待核项，不因题卡完成升级证据等级。

### 当前切片：OpenPiVLA Batch 2 evidence freeze（已完成，WARN）

- 已冻结 eager attention / MACA 稳定性、smoke summary vs formal report vs raw log、checkpoint lineage manifest、DROID `H=15/D=72` shape 与 axis/unit 缺口。
- 新发现并记录：recipe/public smoke 的 `D=72` 与 current formal JSON formatter 的 `limit=16` 不一致；历史 `flow_matching_loss` metadata 与 current Qwen `outputs.loss` 是不同证据路径。
- verdict 保持 `WARN`：raw formal log、checkpoint/processor hash、load smoke、parser/normalizer/controller roundtrip 未闭合。

### 当前切片：OpenPiVLA Batch 2 题卡（已完成，WARN）

- 已生成 `PROJ-OPENPIVLA-009..012`，分别覆盖 eager/MACA、smoke/formal/raw evidence ladder、checkpoint lineage manifest 与 `H=15,D=72`/`limit=16` representation conflict。
- 四题全部保持 `unseen`；master index 已同步到 159 题。Batch 2 的 `WARN` 只反映缺 raw checkpoint/parser/roundtrip，不影响题卡进入题库。

### 当前切片：Robot Harness evidence inventory（已完成，WARN）

- 已只读审计 `C:\Users\mousongzhe\agent`：PydanticAI runtime、server/client toolset、robot scope、mutex、取消/补偿、history stripping、SFT/GRPO 数据构造与 tool-restraint mix。
- 已冻结 62,223 SFT、8,916 canonical GRPO、1,200 restraint generated / 9,252 mixed train，并拆开 8B full pipeline、32B base、32B SFT、GRPO checkpoint-100/200 的 model/run/suite/n/scorer。
- 关键 WARN：32B base 使用 Qwen hidden embedding，而 ladder run manifest 使用 `token_overlap_fallback`；holdout n 也不同；project 100% 是 schema/protocol proxy，safety 与 browser 仍未闭环；Git authorship 不等于 ownership。
- 已生成 [Robot Harness inventory](vla/evidence/projects/robot_harness_claim_evidence_inventory.html)（canonical：[Markdown](vla/evidence/projects/robot_harness_claim_evidence_inventory.md)，review：[JSON](vla/evidence/projects/robot_harness_claim_evidence_inventory.review.json)）。inventory 保持 `WARN`，并已作为 Harness 题卡的唯一事实边界。

### 当前切片：Robot Harness Batch 1 题卡（已完成，WARN）

- 已生成 `PROJ-HARNESS-001..008`，覆盖 harness/function-calling 边界、PydanticAI runtime、mutex/cancel/compensation、SFT/GRPO 路由、reward/restraint、8B/32B scorer/n 差异、proxy metric 与 ownership 防线。
- 8 张题卡全部保持 `unseen`；canonical Markdown、HTML、question list、review JSON 与 master index 已同步，短答案均 ≤180 字、机制展开均 ≤350 字。
- 题卡不把 project sandbox 100% 写成真实机器人成功，不把 browser deferred 写成真实 runner，也不把 Git author 写成完整 ownership。

### 当前切片：OPD claim–evidence inventory（已完成，WARN）

- 已生成 [OPD inventory](vla/evidence/projects/opd_claim_evidence_inventory.html)（canonical：[Markdown](vla/evidence/projects/opd_claim_evidence_inventory.md)，review：[JSON](vla/evidence/projects/opd_claim_evidence_inventory.review.json)）。
- 本轮只完成证据清单与静态 HTML 校验，没有创建 OPD 题卡；全局题库仍保持 159 张、全部 `unseen`。
- 已显式分离旧版 `OPD final` 与新版 `OPD5000 checkpoint-5000`，并记录 original strict / protocol-fixed strict / lenient geometry 三种 point 口径。

### 当前切片：OPD Batch 1 题卡（已完成，WARN）

- 已生成 `PROJ-OPD-001..008`，覆盖五 expert 问题定义、数据路由、student exposure/boundary、coldstart/online OPD、route teacher、checkpoint selection、holdout leakage 与 point protocol/因果边界。
- 8 张题卡全部保持 `unseen`；短答案 ≤180 字、机制答案 ≤350 字；canonical Markdown、HTML、question list、review JSON 已同步。
- 题卡没有把 route metadata 写成 learned router，没有把 checkpoint-5000 写成所有指标最佳，也没有把 OPD uplift 写成单因果结论。

### 当前切片：OPD ownership ledger（已完成，WARN）

- 已审计 `C:\Users\mousongzhe\muxi` 的 Git lineage：`msz136` 初始 scaffold、`mousongzhe` 后续 data/eval 与 OPD5000 sync；同时确认 OPD5000 manifest 指向 `point/train_opd_online_vl.py`，不能用根目录 trainer 副本替代实际 run。
- 已生成 [OPD ownership ledger](vla/evidence/projects/opd_ownership_ledger.html)（canonical Markdown + review JSON），13 个文件/决策行分别标记 scaffold、候选账号提交、候选人自述、远端 summary、checkpoint/result 与工具/协作待确认边界。
- 已新增 `PROJ-OPD-009` ownership 题卡；9 张 OPD cards 全部保持 `unseen`，全局题库同步为 255，未创建 coaching state。
- 结果仍保持 `WARN`：weights、optimizer/RNG、raw predictions、统一 ablation、`msz136`/`mousongzhe` 现实身份映射和候选人逐文件确认均未闭合。下一 bounded slice 只做一次 ownership drill 或补一个 P0 checkpoint/raw bundle。

### 当前切片：UWM / LIBERO ownership ledger（已完成，WARN）

- 已审计 `C:\Users\mousongzhe\Project` 的 Git lineage：official repro 的 18 个路径在 `0341c50` 一次进入，RoboCasa transfer 经历多次候选账号提交；当前 recovery manifest 有未提交修改，strict final JSON 为未跟踪 user-confirmed remote summary。
- 已生成 [UWM ownership ledger](vla/evidence/projects/uwm_libero_ownership_ledger.html)（canonical Markdown + review JSON），13 个文件/决策行分别标记上游、snapshot、协议迁移、DataLoader diagnosis、RoboCasa contract、工作树 recovery 和结果归属。
- 已新增 `PROJ-UWM-002` ownership 题卡；2 张 UWM cards 全部保持 `unseen`，全局题库同步为 255，未创建 coaching state。
- 结果仍保持 `WARN`：checkpoint、normalizer、250 episode bundle、GPU matched A/B、RoboCasa success、候选人逐文件与工具/运行角色均未闭合。下一 bounded slice 只做一次 ownership drill 或补一个 P0 checkpoint/episode bundle。

### 当前切片：UWM / LIBERO evidence inventory（已完成，WARN）

- 已生成 [UWM/LIBERO inventory](vla/evidence/projects/uwm_libero_claim_evidence_inventory.html)（canonical：[Markdown](vla/evidence/projects/uwm_libero_claim_evidence_inventory.md)，review：[JSON](vla/evidence/projects/uwm_libero_claim_evidence_inventory.review.json)）。
- 已冻结 LIBERO-90→LIBERO-10 route、两路 RGB/action chunk、fixed-pruned-init/5-step warmup/50-task、reset-style 对照、DataLoader stall smoke、RoboCasa 转向和 ownership 边界。
- 已显式记录：5-task `186/250=0.744` 是 user-confirmed remote final；UWM Table II 的 OOD initialization、+0.03 object shift、背景移除和 3-seed protocol 与项目 fixed-pruned-init 不同，不能直接说“复现官方 0.79”。
- 本轮没有生成 UWM 题卡；该切片结束时题库为 167 张，全部 `unseen`。

### 前一切片：VOL 05 Engineering / Evaluation Batch 1 知识（已完成，WARN）

- 已规划 44 个 Phase 0 节点，并完成 `VLA-ENG-001..008`、`VLA-EVAL-001..002` 共 10/44 个知识节点。
- Batch 1 覆盖数据 schema、grouped split/leakage、DataLoader、DDP/FSDP/ZeRO、AMP/accumulation、checkpoint lineage、policy latency、action/controller contract、closed-loop protocol 与 metric ladder/first failure。
- 已生成 canonical Markdown、HTML、review JSON 与 Phase 0 question list；知识切片结束时未生成题卡，现已由下一独立切片补齐。
- 官方 DDP/FSDP/ZeRO/AMP/DCP/Reproducibility 已完成独立复核，结果记录在 [`vol_05_batch1_independent_fact_review`](vla/sources/vol_05_batch1_independent_fact_review.html)；ENG-004..006 的本地 artifact gate 也已完成，结果记录在 [`vol_05_local_artifact_gate_eng004_006`](vla/sources/vol_05_local_artifact_gate_eng004_006.html)。当前仍缺 checkpoint binary、optimizer lineage、fixed-batch resume/performance smoke 与真实口述，不能升级为 drilled。

### 当前切片：VOL 05 Engineering / Evaluation Batch 1 题卡（已完成，WARN）

- 已生成 `VLA-ENG-001..008`、`VLA-EVAL-001..002` 共 10 张折叠题卡；字段包含面试意图、30 秒回答、机制、诊断证据、项目挂钩、追问、危险答案、来源与练习状态。
- 难度沿用 Phase 0 合同为 L2 8 / L3 2，优先级为 P0 10；短答全部 ≤180 字，机制展开全部 ≤350 字。
- canonical Markdown、HTML、review JSON、Phase 0 清单、主索引与进度入口已同步；全局题库增至 177 张，全部保持 `unseen`。
- 项目 hook 只复用五项目 inventory 的已冻结 bad cases；没有升级 checkpoint、延迟、闭环、proxy 或个人贡献证据。

### 当前切片：VOL 05 Batch 1 独立官方文档复核（已完成，WARN）

- 直接核对 PyTorch 2.13 DDP/FSDP/AMP/Distributed Checkpoint/Reproducibility 与 DeepSpeed ZeRO tutorial；固定版本 URL、读取日期、响应摘要和逐节点 verdict 已写入 source audit。
- DDP 的 gradient all-reduce、输入不自动 shard、FSDP 的 all-gather/reduce-scatter/reshard、ZeRO Stage 1/2/3、AMP unscale-before-clipping/effective-batch 与 DCP load-time reshard 均有官方依据。
- DDP optimizer-state duplication、吞吐时间分解、checkpoint lineage/RNG/data cursor、resume/performance smoke 明确标为 inference/framework/blocked；没有升级项目结果或个人 ownership。
- `VLA-ENG-004` 题卡与知识页已做最小措辞收紧；10 张题卡仍全部 `unseen`。

### 当前切片：VOL 05 ENG-004..006 本地 Artifact Gate（已完成，WARN）

- UWM snapshot 提供 8 卡 DeepSpeed 训练 summary、checkpoint-load report、12D action normalizer、effective config；OPD snapshot 提供 ZeRO-2/3 config 和 final-only run manifest。
- 两个扫描根目录均没有 `.pt/.pth/.ckpt/.safetensors/.bin`，所以报告中的 `/data/msz/.../models.pt` 只能标为 report-supported remote path，不是本地 checkpoint-verified。
- OPD continuation manifest 明确写出 `final_weights_no_optimizer_state`；UWM load report 有 matched/skipped keys，但没有固定 batch pre/post-load diff 或续训一步记录。
- 证据足以把 ENG-004..006 从“全缺 artifact”提升到 `PASS WITH WARNING`，不足以关闭 resume/lineage gate。

### 当前切片：VOL 05 Batch 2A 数据可追溯与批处理知识（已完成，WARN）

- 已生成 `VLA-ENG-009..011` 三个 canonical knowledge 节点：dataset/version/transform manifest、multimodal decode/cache/determinism、variable-length batching/padding waste。
- 已生成并静态校验 `knowledge/vol_05_engineering_eval_batch2a.md/.html/.review.json`；source SHA、节点边界、公式/伪代码、项目 bad-case hook 与 `WARN` open items 已记录。
- 知识切片完成时题卡暂后置；随后已在独立 bounded slice 生成 `VLA-ENG-009..011` 三张题卡，全部保持 `unseen`。
- DVC/DataLoader/padding/HF cache-collator 官方语义已完成独立复核；manifest schema、cache key、dynamic batching 与 padding A/B 仍是工程合同/待验证项。

### 当前切片：VOL 05 Batch 2A 原子题卡（已完成，WARN）

- 已生成 `VLA-ENG-009..011` 三张折叠题卡，覆盖 manifest provenance、decode/cache/determinism、dynamic batching/padding；短答均 ≤180 字，机制展开均 ≤350 字。
- canonical Markdown、HTML、题目清单、review JSON、主索引与练习进度已同步；三张题卡全部保持 `unseen`，全局题库从 177 增至 180。
- 题卡将 DVC/DataLoader/pad_sequence 作为官方语义，将 manifest/cache/dynamic batching 作为工程合同；OpenPiVLA/UWM/OPD 只作为真实 bad case，不升级为已完成 A/B。

### 当前切片：VOL 05 Batch 2A 独立官方文档复核（已完成，WARN）

- 已生成 `sources/vol_05_batch2a_independent_fact_review.md/.html/.review.json`，逐项核对 DVC、PyTorch 2.13 DataLoader/`pad_sequence`/Reproducibility、HF Datasets v4.8.4 cache/fingerprint 与 Transformers v5.14.0 collator。
- 三个节点均为 `PASS WITH WARNING`：官方 API 语义通过；custom cache key、manifest schema、dynamic budget、三层 mask、项目 A/B 与视觉 QA 保持边界。
- 本轮还修正了 Batch 2A 知识页/题卡的 PyTorch response SHA、HF 稳定版本链接，以及 `persistent_workers` RNG 影响的措辞。

### 当前切片：VOL 05 ENG-012 存储格式 Source Freeze（已完成，WARN）

- 已冻结 h5py 3.15.0、Zarr v3.2.1、WebDataset commit、Apache Parquet format commit 与 PyArrow 22.0 的官方来源、commit/license 和可重复指纹。
- Source freeze 明确区分 HDF5/Zarr 数组存储、WebDataset tar-shard streaming、Parquet columnar table；workload shortlist 覆盖 random window、sequential stream、column scan、hybrid layout。
- source freeze 完成时只冻结来源与 benchmark contract；随后已在独立切片生成 `VLA-ENG-012` 知识正文与单张题卡，题卡保持 unseen。不把 UWM DataLoader-only stall 写成格式根因或 full-training uplift。

### 当前切片：VOL 05 ENG-012 存储布局知识（已完成，WARN）

- 已生成 `knowledge/vol_05_engineering_eval_eng012.md/.html/.review.json`，覆盖四类系统抽象层、chunk/shard/row-group 机制、`A_read`、workload shortlist、benchmark contract、trade-off 与 bad cases。
- 知识总覆盖从 13/44 增至 14/44；题卡仍为 13/44 unseen，没有把知识生成计入题库或掌握状态。
- 项目 hook 只使用 UWM DataLoader-only stall 作为 `local clue / A-B pending`；没有声称 Zarr 根因、格式转换收益或 full-training throughput。

### 当前切片：VOL 05 ENG-012 原子题卡（已完成，WARN）

- 已生成 `VLA-ENG-012` 单张折叠题卡，短答 150 字、机制展开 335 字，覆盖 workload-to-layout、matched benchmark 与 UWM evidence boundary。
- canonical Markdown、HTML、题目清单、review JSON、主索引与进度入口已同步；全局题库从 180 增至 181，题卡保持 `unseen`。
- 题卡没有把 WebDataset README 的 3–10 倍描述写成通用 benchmark，也没有把 UWM stall 升级为格式根因。

### 当前切片：VOL 05 ENG-013 Reproducibility Source Freeze（已完成，WARN）

- 已冻结 PyTorch 2.13 Reproducibility、DataLoader/DistributedSampler、CPU/CUDA RNG state API 与 NumPy 1.26 seed 的规范化正文指纹。
- 明确区分固定 seed、可复现实验和精确 mid-epoch resume；`set_epoch`、dataset constant-size/order、RNG state API 有官方依据，sampler cursor/prefetch replay 是工程合同。
- 当前没有本地 fixed-batch/mid-epoch replay artifact；不升级任何个人项目的 sampler cursor、RNG bundle 或精确续训 claim。

### 当前切片：VOL 05 ENG-013 Reproducibility 知识（已完成，WARN）

- 已生成 `knowledge/vol_05_engineering_eval_eng013.md/.html/.review.json`，覆盖 seed ownership、DistributedSampler/set_epoch、RNG state、epoch/mid-epoch resume、replay smoke、trade-off 与项目边界。
- VOL 05 知识覆盖从 14/44 增至 15/44；题卡仍为 14/44 unseen，未把知识生成计入题卡或掌握状态。
- 没有本地 fixed-batch/mid-epoch replay artifact；ENG-013 仍保持 WARN，题卡后置。

### 当前切片：VOL 05 ENG-013 原子题卡（已完成，WARN）

- 已生成 `VLA-ENG-013` 单张折叠题卡，短答 169 字、机制展开 339 字，覆盖 seed/replay 强度、DistributedSampler/set_epoch、RNG/cursor bundle 与项目 evidence boundary。
- canonical Markdown、HTML、题目清单、review JSON、主索引与练习进度已同步；全局题库从 181 增至 182，题卡保持 `unseen`。
- 题卡没有把 fixed seed、checkpoint load 或 DistributedSampler 写成精确 mid-epoch resume 证明。

### 前一切片：VOL 05 ENG-014 原子题卡（已完成，WARN）

- 已完成 ENG-014 CUDA/MACA/ROCm 来源冻结：PyTorch 2.13 CUDA/HIP/extension、ROCm 7.14.0 compatibility matrix、NVIDIA CUDA Compatibility、MetaX `mcPytorch@b3db5e` / `mcTriton@7dd407`，并将兼容性拆成 L0 device/runtime 到 L5 workload/eval。
- 已完成 `VLA-ENG-014` 单节点知识与单张折叠题卡：六层兼容合同、operator matrix、数值 parity、同步计时、验证伪代码与 OpenPiVLA eager/MACA 证据边界；知识 16/44、题卡 16/44，题卡保持 unseen。
- canonical Markdown、HTML、题目清单、review JSON、主索引与练习进度已同步；全局题库从 182 增至 183，未创建 coaching state。
- 下一轮只选择一个 bounded slice：A) 一次只问 `VLA-ENG-014` 并记录真实回答；或 B) 继续 ENG-015 的 knowledge+card 小切片；ENG-016 继续后置。
- 若转入真实口述，先一次只问一个 `PROJ-HARNESS-001..008` 或 Batch 2A 题卡；候选人回答后再创建/更新 coaching state。
- ENG-004..006 的 checkpoint binary、optimizer lineage、fixed-batch resume 与 matched throughput 仍可作为后续补证据支线，但不与 Batch 2A 事实复核/口述在同一轮展开。

### 前一切片：VOL 05 ENG-015 Knowledge + 原子题卡（已完成，WARN）

- 已完成 ENG-015 source freeze：PyTorch 2.13 activation checkpoint/FSDP CPU offload、DeepSpeed frozen commit 的 activation-checkpointing/ZeRO-3 文档，以及 ZeRO-Offload/Infinity 论文背景。
- 已生成 `VLA-ENG-015` 单节点知识与一张原子题卡，覆盖 activation recompute、FSDP CPU offload、ZeRO CPU/NVMe state offload、显存/step-time 账本、matched A/B 和 fixed-next-batch resume；题卡保持 unseen。
- UWM/OPD 的配置、summary、load report 与 final-only manifest 继续保持 local evidence；当前没有 binary、optimizer/RNG/sampler lineage、matched throughput A/B 或 fixed-batch resume，不能说显存/吞吐/恢复收益。
- 下一轮进入 ENG-015 一题口述或补本地 artifact；ENG-016 继续后置。

### 前一切片：VOL 05 ENG-016 Knowledge + 原子题卡（已完成，WARN）

- 已完成 ENG-016 source freeze：Hinton distillation、PyTorch 2.13 `kl_div`/`no_grad`/FSDP 与 DeepSpeed ZeRO-3，明确 soft target、temperature、log-probability input、reduction、teacher freeze/no-grad 和 state ownership 合同。
- 已生成 `VLA-ENG-016` 单节点知识与一张原子题卡，覆盖 resident/sequential/staged schedule、显存/step-time A/B、student-only backward 与 OPD 因果边界；题卡保持 unseen。
- OPD 本地证据支持五 expert mix、`preloaded_zero3`、route-driven teacher selection、coldstart full-vocab KL 和 student-rollout→teacher-KL 链路；不支持 learned router、多教师 uplift 或完整权重/optimizer bundle。
- single-teacher/SFT-only/no-synthetic/synthetic-ratio ablation 与 matched memory/latency A/B 仍缺；下一轮进入 ENG-016 一题口述或补 artifact，ENG-017 不展开。

### 前一切片：VOL 05 ENG-017 Knowledge + 原子题卡（已完成，WARN）

- 已完成 ENG-017 source freeze：PyTorch 2.13 AMP、Profiler、Autograd anomaly、DDP、`clip_grad_norm_`、DataLoader，以及 DeepSpeed `steps_per_print`/`wall_clock_breakdown` 配置语义。
- 已生成 `VLA-ENG-017` 单节点知识与一张原子题卡，覆盖 numerical/data/compute/distributed/lifecycle 五层事件、AMP skipped step、step timeline、first-failure replay 与项目边界；题卡保持 unseen。
- UWM/OPD 当前有 GradScaler/throughput/profile 配置和部分 loss/overlap/route summary，但没有完整 overflow 时间序列、rank-level data_wait/comm trace、matched A/B 或 first-failure replay。
- 下一轮进入 ENG-017 一题口述或补 observability artifact；ENG-018 不展开。

### 前一切片：VOL 05 ENG-018 Source Freeze（已完成，WARN）

- 已冻结 PyTorch 2.13 TorchElastic/torchrun/DCP、Kubernetes Job/Pod Lifecycle 与 DeepSpeed model checkpointing，明确 rank/world-size 不稳定、duplicate execution、SIGTERM/grace、multi-file checkpoint 与 load-time reshard 边界。
- Source freeze 将 logical run、attempt、worker group、rank 四层 identity 分开，并定义 attempt temp generation、manifest-last COMMITTED、stable operation key 去重和 immutable final promotion。
- UWM/OPD/OpenPiVLA 当前只有 save/load metadata、final-only/no-optimizer-state manifest 或远端 path；没有 binary、attempt ledger、signal/retry/duplicate/world-size drill，不能声称无损弹性续训。
- 下游知识节点与一张 `unseen` 题卡已在下一 bounded slice 完成；ENG-019 仍未展开。

### 前一切片：VOL 05 ENG-018 Knowledge + 原子题卡（已完成，WARN）

- 已生成 `knowledge/vol_05_engineering_eval_eng018.md/.html/.review.json`，覆盖 logical run/attempt/worker group/rank、SIGTERM/grace、safe-boundary checkpoint、DCP/DeepSpeed multi-file generation、manifest-last `COMMITTED`、幂等副作用和 recovery drill matrix。
- 已生成 `VLA-ENG-018` 单张折叠题卡；短答 176 字、机制展开 346 字，状态保持 `unseen`。VOL 05 知识与题卡同步到 20/44，全局题库同步到 187。
- UWM/OPD/OpenPiVLA 仍只有 save/load metadata、final-only/no-optimizer-state manifest 或远端 path；没有 binary、attempt ledger、signal/retry/duplicate/world-size drill，不能声称 exact resume 或 exactly-once。
- canonical SHA、HTML 结构、本地链接、题号唯一性、长度与 `coaching_state.md` absence 进入本切片验证；浏览器视觉检查仍受 file:// 策略阻断。下一 bounded slice 可做 ENG-018 一题口述/补 recovery artifact，或为 ENG-019 单独做 Source Freeze。

### 前一切片：VOL 05 ENG-019 Config Resolution / Run Identity Source Freeze（已完成，WARN）

- 已冻结 Hydra 1.3.2 Defaults/override、pydantic-settings 2.14.1 priority/deep update、CPython 3.14 argparse、PyTorch 2.13 torchrun runtime env 与 RFC 8785 canonical JSON。
- Source gate 定义 declared precedence、typed effective config、逐字段 winning source/overridden values、secret allowlist/redaction、canonical semantic run key，并与 logical run、scheduler attempt、rank/restart identity 分离。
- UWM launcher 直接显示 env default→Hydra CLI override，OpenPiVLA formal trainer 会保存 argparse/plan snapshot，OPD 会按 `WORLD_SIZE` 改写 DeepSpeed `auto`；三者仍缺统一 source map、secret-safe canonical hash 和 run→checkpoint→eval immutable manifest。
- 下游知识节点与一张 `unseen` 题卡已在下一 bounded slice 完成；ENG-020 已收口，保持 WARN。

### 前一切片：VOL 05 ENG-019 Knowledge + 原子题卡（已完成，WARN）

- 已生成 `knowledge/vol_05_engineering_eval_eng019.md/.html/.review.json`，覆盖 framework-specific precedence、typed effective config、field provenance、semantic/execution/attempt/secret 分类、RFC 8785 canonical run key、resolver 伪代码和验证矩阵。
- 已生成 `VLA-ENG-019` 单张折叠题卡；短答 174 字、机制展开 346 字，状态保持 `unseen`。该历史切片结束时 VOL 05 knowledge/cards 为 21/44，全局题库为 188；后续 ENG-020 已增量收口。
- UWM/OpenPiVLA/OPD 的 env/CLI/args/effective mutation 只作为 local-direct hook；统一 source map、secret-safe canonical hash 和 run→checkpoint→eval immutable lineage 仍缺，不能升级为已实现系统。
- 下一 bounded slice 可做 ENG-019 一题口述/补 resolver artifact，或为 ENG-020 单独做 Source Freeze；不得因页面生成创建 coaching state。

### 当前切片：VOL 05 ENG-020 Secret / Permission / Logging Knowledge + 原子题卡（已完成，WARN）

- 已冻结 OWASP Secrets/Logging/Authorization、Kubernetes Secret/Good Practices、NIST SP 800-53 Rev.5 AC-3/AC-6/AU-9/IA-5 与 pydantic-settings debug secret warning。
- Source gate 定义 short-lived scoped secret、lease/rotate/revoke、deny-by-default/least privilege/every-request authorization、dataset purpose/retention/export manifest、allowlist-first redaction 和 canary/negative/incident drill。
- Robot Harness 直接支持特定 `__access_token` masking、dedup exclusion 与 robot/tool scope；UWM/OpenPiVLA/OPD 提供 args/path/summary 暴露面的真实 bad case，但统一 secret manager/IAM/generic redaction/audit protection 尚未闭合。
- 已生成 `knowledge/vol_05_engineering_eval_eng020.md/.html/.review.json` 与 `VLA-ENG-020` 单张题卡及清单/review；短答 180 字、机制展开 334 字，题卡保持 `unseen`。VOL 05 同步到 knowledge/cards 22/44，全局题库增至 189。

### 当前切片：VOL 05 ENG-021 Model / Processor / Normalizer Packaging Knowledge + 原子题卡（已完成，WARN）

- 已冻结 Transformers `save_pretrained/from_pretrained`、`ProcessorMixin`、Hub revision/snapshot、safetensors tensor-only 边界，以及 OpenPI params/assets/train_state/norm-stats/transforms/shape 语义。
- 已生成 `knowledge/vol_05_engineering_eval_eng021.md/.html/.review.json` 与 `VLA-ENG-021` 单张题卡及清单/review；短答 165 字、机制展开 340 字，题卡保持 `unseen`。VOL 05 同步到 knowledge/cards 23/44，全局题库增至 190。
- OpenPiVLA 当前只有 processor/collator、recipe 和远端 checkpoint/path；UWM 有 normalizer/load metadata；OPD 有 final-only/no-optimizer-state manifest。formal binary、processor/norm hash binding、round-trip 与 backend A/B 仍缺。

### 当前切片：VOL 05 ENG-022 Policy Server Resilience Knowledge + 原子题卡（已完成，WARN）

- 已冻结 CPython asyncio bounded queue/timeout/cancellation、Triton `max_batch_size`/dynamic batcher/queue delay/timeout action，以及 OpenPI WebSocket server 的逐请求 infer/timing/error 语义。
- 已生成 `knowledge/vol_05_engineering_eval_eng022.md/.html/.review.json` 与 `VLA-ENG-022` 单张题卡及清单/review；短答 166 字、机制展开 318 字，题卡保持 `unseen`。VOL 05 同步到 knowledge/cards 24/44，全局题库增至 191。
- OpenPiVLA 只有 connect/infer timeout 与 `server_unavailable`/`infer_failed` reports；Robot Harness 只有 tool polling timeout/cancel/compensation。统一 admission queue、batching、p99/action-age SLO、safe fallback、watchdog 和 load/chaos drills 仍缺；后续 resilience 节点后置。

### 前一切片：VOL 05 EVAL-003 Success Rate / Confidence Interval Source Freeze（已完成，WARN）

- 已冻结 SciPy `v1.16.3` `binomtest().proportion_ci()`、statsmodels `v0.14.6` `proportion_confint()` / normal sample-size approximation；官方实现 raw SHA、tag commit、Wilson/Clopper–Pearson 论文和 cluster/sequential inference 边界已写入 source freeze。
- Source gate 固定 episode-level Bernoulli 单元、Wilson/exact 区间、zero/all-success、margin 规划与 `p=0.5` 最坏情况，并明确 task/seed/init clustering、decision threshold、可选停止和重复测试风险。
- UWM `186/250` 仍是 user-confirmed/protocol-limited 的 naive diagnostic；OpenPiVLA `97.4%` 仍缺分母和 raw trial/seed/init；OPD `10k` 是 box/point/text raw-holdout，不能混成 robot rollout success。
- 下游 knowledge 已在下一独立 slice 生成；source freeze 自身不计题卡或 mastery。

### 前一切片：VOL 05 EVAL-003 Success Rate / Confidence Interval Knowledge（已完成，WARN）

- 已生成 `knowledge/vol_05_engineering_eval_eval003.md/.html/.review.json`，覆盖 episode-level Bernoulli contract、Wilson/Clopper–Pearson、zero/all-success、normal sample-size planning、task/seed/init cluster dependence、optional stopping 和实现伪代码。
- 项目 hook 严格分层：UWM 186/250 只计算 naive interval；OpenPiVLA 97.4 因缺分母不可算 CI；OPD 10k 只按 metric-specific observation unit 解释，不冒充 robot rollout success。
- VOL 05 knowledge 同步到 25/44，cards 同步到 25/44 unseen，全局题库同步到 195；未创建 coaching state。下一步只做 `VLA-EVAL-003` 真实口述或补 statistical artifacts。

### 当前切片：VOL 05 EVAL-003 原子题卡（已完成，WARN）

- 已生成 `questions/vol_05_engineering_eval_eval003.md/.html/.question_list.md/.review.json`，短答 178 字、机制展开 286 字，覆盖 episode contract、Wilson/exact、最小 rollout、cluster dependence、stopping risk 与 UWM/OpenPiVLA/OPD 证据边界。
- 题号 `VLA-EVAL-003` 已加入主索引，VOL 05 cards 同步到 25/44，全局题库同步到 195；题卡保持 `unseen`，未创建 coaching state。
- 下一步不扩展 EVAL-004/EVAL-005；先进行一次真实口述，或补齐 UWM episode、OpenPiVLA denominator/lineage、OPD metric-specific statistical artifacts。

### 当前切片：VOL 05 EVAL-003 本地统计 Artifact Gate（已完成，WARN）

- 已生成 `sources/vol_05_eval003_local_statistical_artifact_gate.md/.html/.review.json`，审计 UWM `186/250` summary-only、OpenPiVLA `97.4%` archive-summary-only、OPD 10k metric-specific row evidence。
- 已对 UWM、OPD 的可读分母做 naive Wilson smoke，并显式标注 task/image clustering、远端 prediction/input、checkpoint/lineage 与 scorer 缺口；OpenPiVLA 97.4% 保持 fail-closed，不计算 CI。
- `sources/README.md` 已加入 gate 入口；本切片前 198 张题卡均为 `unseen`，PER-001 题卡加入后为 199 张，仍全部 `unseen`；不创建 coaching state，也不生成 EVAL-004/EVAL-005。
- 下一步：优先进行一次 `VLA-EVAL-003` 真实口述；若继续证据线，只补一个 P0 artifact gap，不并行扩展统计节点。

### 当前切片：VOL 06 PER-001 Grounding / Coordinate Source + Knowledge + Card（已完成，WARN）

- 已冻结 Grounding DINO paper/repository/inference code（commit `856dde20...`）、RoboPoint paper 与 OPD local inventory；记录了原文/API 指纹、许可证线索、支持/不支持的 claim。
- Source gate 明确区分 point、box、text 三种输出合同，冻结 `normalized cxcywh → pixel xyxy` 的实现样例、parser/letterbox/坐标轴/单位边界，以及 strict、protocol-fixed、lenient 三套 point scorer 语义。
- 已生成 `knowledge/vol_06_per001_grounding_coordinate.md/.html/.review.json` 与 `questions/vol_06_per001.md/.html/.question_list.md/.review.json`；知识覆盖表示合同、变换公式、parser/scorer、grounding-to-action 与 OPD 边界，题卡短答 146 字、机制展开 318 字，保持 `unseen/WARN`。
- 下一 bounded slice 先进行 `VLA-PER-001` 真实口述或补 parser/3D roundtrip evidence；PER-002 3D lift 继续后置，不能批量展开 VOL 06。

### 当前切片：VOL 06 PER-002 3D Lift / Frame Source + Knowledge + Card（已完成，WARN）

- 已冻结 OpenCV camera calibration/depth 教程（commit `f7dd7df1...`）与 ROS REP-103/105（commit `11ca24a4...`），记录 raw response SHA、camera matrix/distortion、depth/disparity、frame convention 与 map/odom/base_link 语义边界。
- Source gate 明确 pixel→camera→target 的反投影公式、深度来源/单位、`T_target←camera(timestamp)`、TF/registration/uncertainty 账本和 projection→calibration→TF→planner→controller→closed-loop 证据阶梯。
- 已生成 `knowledge/vol_06_per002_3d_lift_frame.md/.html/.review.json` 与 `questions/vol_06_per002.md/.html/.question_list.md/.review.json`；覆盖内参/畸变、深度来源、反投影、timestamped TF、uncertainty、3D evidence ladder 与 OPD/WAM 边界，题卡短答 166 字、机制展开 349 字，保持 `unseen/WARN`。
- 不把 OPD static holdout 或 WAM camera/controller 字段升级为 3D lift、抓取、导航或真机成功。下一 bounded slice 先口述 PER-001/PER-002 或补 3D roundtrip artifact，PER-003 继续后置。

### 当前切片：VOL 06 PER-003 Multi-view / Temporal Source + Knowledge + Card（已完成，WARN）

- 已冻结 Open X-Embodiment README、Octo frozen code、WM-017 schema freeze 与 PER-001/002 的多视角/时序依赖；明确 camera/frame identity、timestamp、presence mask、view/time fusion、common-frame association 与 observation-age 合同。
- Source gate 区分 schema、geometry、fusion、temporal replay、closed-loop 五层证据；OPD/WAM 当前只有 static holdout 或有限 rollout provenance，没有 multi-view calibration、sync、view ablation 或 temporal replay artifact。
- 已生成 `knowledge/vol_06_per003_multiview_temporal.md/.html/.review.json` 与 `questions/vol_06_per003.md/.html/.question_list.md/.review.json`；覆盖 per-view schema、camera/time embedding、presence/causal mask、common-frame association、fusion trade-off 与 observation-age，题卡短答 178 字、机制展开 347 字，保持 `unseen/WARN`。
- 不把 OPD/WAM 的 static/limited provenance 升级为多视角或时序结果。下一 bounded slice 先口述 PER-001..003 或补 multi-view artifact，PER-004/VLN/ObjectNav 继续后置。

### 当前切片：VOL 06 PER-004 VLN / ObjectNav Source Freeze（已完成，WARN）

- 已冻结 Habitat-Lab `0fb6f43ffe806a8088a171b036336c093bcf604e`、Habitat-Sim `57ee4941dc4765240f0f91f70b2c97a919bf9038`、VLN-CE `729d141b2ee10628061ada74dd3a5b9f70faeba5` 的 README/源码快照，并记录原始文件 SHA；补充 R2R、REVERIE、ObjectNav Revisited 与 SPL 原始论文入口。
- Source gate 区分 VLN、ObjectNav、REVERIE 的 goal/instruction/action/stop/success 合同，冻结 ObjectGoal/view-point、navmesh、SR/SPL/TL/NE/OS 及 simulator-to-real 证据边界。
- 已生成 `sources/vol_06_per004_vln_objectnav_source_freeze.md/.html/.review.json`，保持 `WARN`；source gate 没有把 OPD/Harness/WAM/UWM 的现有证据升级为导航结果，knowledge/card 已在独立 slice 同步。
- 该 PER-004 source slice 完成时全局题库为 203 张、全部 `unseen`；随后已完成 PER-005 与 UWM 单题卡，当前状态见文末最新切片。

### 当前切片：VOL 06 PER-004 VLN / ObjectNav Knowledge（已完成，WARN）

- 已生成 `knowledge/vol_06_per004_vln_objectnav.md/.html/.review.json`，覆盖 VLN/ObjectNav/REVERIE taxonomy、episode/observation/action/stop contract、ObjectGoal/view-point、SR/SPL/TL/NE/OS、Habitat navmesh、失败树与 simulator-to-real evidence ladder。
- 伪代码要求先校验 episode identity、scene revision、split 与 path，再调用 task-specific success predicate；不把 shortest reference path 当作实际 controller trace，也不把 simulator success 升级为真机结果。
- 该 UWM slice 完成时全局题库为 204 张、全部 `unseen`；随后已开始 G10 SYS-VLA-001，当前下一步见文末最新切片。

### 当前切片：PER-004 Navigation Artifact Gate（已完成，WARN）

- 已生成 `evidence/projects/per004_navigation_artifact_gate.md/.html/.review.json`，逐项目盘点 OPD、Robot Harness、OpenPiVLA、WAM、UWM/LIBERO 的导航相关证据。
- 扫描没有发现 protocol-complete 的 VLN/ObjectNav episode、scene/navmesh revision、continuous action trace、stop predicate、SR/SPL denominator 或 real-navigation safety log；Robot Harness 的 semantic-navigation 只保留为高层工具接口证据。
- 当前 gate 为 `WARN / 0_local_direct_navigation_bundles`，不修改简历或项目强回答；下一 bounded slice 只进行 `PER-001..005` 真实口述，或在用户提供 bundle 后逐字段核验。

后续 source-first 入口：VOL 06 PER-005 与 VOL 07 PROJ-UWM-001 已完成 source/evidence→card；下一步转入 `PROJ-UWM-001` 真实口述或补 UWM raw artifact，不把远端确认结果写成本地 benchmark。

### 当前切片：VOL 06 PER-005 Navigation Policy Architecture Source Freeze（已完成，WARN）

- 已冻结 Habitat-Lab/Habitat-Sim/VLN-CE pinned source，以及 GOSE、ObjectNav Revisited、VLN-CE、Waypoint Models、R2R、REVERIE primary papers。
- Source gate 区分 map-free、semantic map-based、waypoint、hybrid learned/classical policy，并冻结 planner/controller 的 frame、unit、uncertainty、observation age、replan、stop、repeat 与 latency 合同。
- 已生成 `sources/vol_06_per005_navigation_policy_architecture_source_freeze.md/.html/.review.json`；知识页与一张 unseen 题卡已同步，保持 `WARN`。

### 当前切片：VOL 06 PER-005 Navigation Policy Architecture Knowledge + Atomic Card（已完成，WARN）

- 已生成 `knowledge/vol_06_per005_navigation_policy_architecture.md/.html/.review.json`，覆盖 map-free/map-based/waypoint/hybrid taxonomy、semantic map/frontier scoring、subgoal frame/uncertainty/age、planner/controller、stop/replan、latency ledger、伪代码与 evidence ladder。
- PER-004 navigation artifact gate 仍为 `WARN / 0_local_direct_navigation_bundles`；OPD/Harness/OpenPiVLA/WAM/UWM 只作为接口或证据边界，未升级为个人导航实现。
- 该 PER-005 切片完成时全局题库为 203 张、全部 `unseen`；随后已完成 PROJ-UWM-001，当前下一步见下方 UWM 切片。

### 当前切片：VOL 07 PROJ-UWM-001 UWM / LIBERO Protocol Boundary Card（已完成，WARN）

- 已基于 UWM/LIBERO Claim–Evidence Inventory、VOL 04 benchmark protocol audit 和项目页生成 `questions/proj_uwm.md/.html/.question_list.md/.review.json`。
- 题卡只讨论 fixed-pruned-init 的 186/250、reset-style 的 0.928、论文约 0.79 之间的协议差异；短答 176 字、机制展开 348 字，保持 `unseen/WARN`。
- 已明确缺口：checkpoint/normalizer immutable bundle、250 条 episode JSONL、exact init/seed manifest、同 checkpoint paired protocol 与 ownership ledger；RoboCasa-native success 仍为 `unverified`。
- 该 UWM 题卡完成时全局题库为 204 张、全部 `unseen`；当前下一步转入 SYS-VLA-001 口述或平台 artifact。

### Next 2：WAM 保持安全降级并等待 raw evidence

- WAM 投递 release blocker 已关闭，但 raw run/checkpoint/metric/episode/ownership artifacts 仍为 MISSING。
- 有 artifacts 时回填；不恢复历史数字，不生成强回答，不升级 reviewed。

### 当前切片：VOL 08 SYS-VLA-001 可复现 VLA 训练—评估平台（已完成，WARN）

- 已冻结 PyTorch DCP/reproducibility、Open X、LIBERO、OpenPI 以及 ENG-013/021 与五项目 evidence inventory 的系统边界。
- 已生成 `sources/vol_08_sys001_vla_training_eval_platform_source_freeze.md/.html/.review.json`、`knowledge/vol_08_sys001_vla_training_eval_platform.md/.html/.review.json` 与 `questions/vol_08_sys001.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 dataset/run/bundle/evaluation/rollout lineage、metric namespaces、roundtrip/load gate 和项目真实性边界；短答 179 字、机制展开 344 字，保持 `unseen/WARN`。
- 当前缺统一 registry、checkpoint/normalizer hash、raw rollout 与 ownership ledger；下一 bounded slice 只进行 `SYS-VLA-001` 真实口述或补一个平台 artifact。

### 当前切片：VOL 08 CODE-VLA-001 数值稳定 softmax / log-softmax（已完成，WARN）

- 已冻结 PyTorch softmax、log-softmax、CrossEntropyLoss、scaled dot-product attention 官方 API 与 VOL 01/03 基础边界。
- 已生成 `sources/vol_08_code001_softmax_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code001_softmax.md/.html/.review.json` 与 `questions/vol_08_code001.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 max-shift、logsumexp、dim/keepdim、bool/加性 mask、全 masked 行、fp16/bf16、autograd parity 和 VLA action-loss 边界；短答 139 字、机制展开 349 字，保持 `unseen/WARN`。
- 当前缺本地手写实现与 dtype/device parity artifact；下一 bounded slice 只进行 `CODE-VLA-001` 白板/口述练习或补一个 parity artifact。

### 当前切片：VOL 08 CODE-VLA-002 Scaled Dot-Product Attention（已完成，WARN）

- 已冻结 PyTorch SDPA/MultiheadAttention、Transformer paper 与 VOL 01/03 sequence/mask 实现边界。
- 已生成 `sources/vol_08_code002_attention_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code002_attention.md/.html/.review.json` 与 `questions/vol_08_code002.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 `[B,H,L,D]`、`Lq/Lk`、scale、bool/additive/causal/padding mask、dropout、fp16/bf16、all-masked row、complexity 与 SDPA parity；短答 130 字、机制展开 316 字，保持 `unseen/WARN`。
- 当前缺本地多 backend forward/backward parity 与 profile artifact；下一 bounded slice 只进行 `CODE-VLA-002` 白板/口述练习或补一个 attention parity artifact。

### 当前切片：VOL 08 CODE-VLA-003 LayerNorm / RMSNorm（已完成，WARN）

- 已冻结 PyTorch LayerNorm/RMSNorm、RMSNorm paper 与 VOL 01 pre/post-norm 基础边界。
- 已生成 `sources/vol_08_code003_norm_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code003_norm.md/.html/.review.json` 与 `questions/vol_08_code003.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 normalized shape、population variance、RMS 不减均值、epsilon、affine、fp32 accumulation、无 running stats、train/eval 与 autograd parity；短答 171 字、机制展开 321 字，保持 `unseen/WARN`。
- 当前缺本地 forward/backward parity 与 matched norm ablation；下一 bounded slice 只进行 `CODE-VLA-003` 白板/口述练习或补一个 norm parity artifact。

### 当前切片：VOL 08 CODE-VLA-004 Masked MSE / Huber Loss（已完成，WARN）

- 已冻结 PyTorch MSELoss/HuberLoss/SmoothL1Loss 与 VOL 03/05 action mask/reduction 边界。
- 已生成 `sources/vol_08_code004_masked_loss_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code004_masked_loss.md/.html/.review.json` 与 `questions/vol_08_code004.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 elementwise MSE/Huber、valid denominator、empty mask、task/sample weight、distributed numerator/denominator、fp32 accumulation 与 VLA action/token/diffusion loss 边界；短答 166 字、机制展开 338 字，保持 `unseen/WARN`。
- 当前缺本地 parity/empty-mask log 与 matched MSE/Huber ablation；下一 bounded slice 只进行 `CODE-VLA-004` 白板/口述练习或补一个 masked-loss parity artifact。

### 当前切片：VOL 08 CODE-VLA-005 Homogeneous Transform Composition（已完成，WARN）

- 已冻结 ROS REP-103/105、SciPy Rotation 与 VOL 06 PER-002 的 SE(3)、frame、单位和 timestamped TF 边界。
- 已生成 `sources/vol_08_code005_transform_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code005_transform.md/.html/.review.json` 与 `questions/vol_08_code005.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 `T^A_B` 方向、右到左 composition、rigid inverse、point/vector/pose、frame/单位/时间戳、roundtrip 与 VLA 几何边界；短答 124 字、机制展开 294 字，保持 `unseen/WARN`。
- 当前缺本地 TF/calibration roundtrip；下一 bounded slice 只进行 `CODE-VLA-005` 白板/口述练习或补一个 transform artifact。

### 当前切片：VOL 08 CODE-VLA-006 2-Link Planar Forward Kinematics（已完成，WARN）

- 已冻结 Modern Robotics、ROS REP-103 与 VOL 01/CODE-005 的 planar FK、relative joint angle、frame/单位和 Jacobian 测试边界。
- 已生成 `sources/vol_08_code006_planar_fk_source_freeze.md/.html/.review.json`、`knowledge/vol_08_code006_planar_fk.md/.html/.review.json` 与 `questions/vol_08_code006.md/.html/.question_list.md/.review.json`。
- 题卡覆盖解析式、`Rz·Tx·Rz·Tx`、radian/degree、tool offset、zero/90/folded/negative、matrix parity、finite-difference Jacobian 与 FK/IK/controller 边界；短答 164 字、机制展开 240 字，保持 `unseen/WARN`。
- 当前缺本地 URDF/joint calibration/FK roundtrip artifact；下一 bounded slice 只进行 `CODE-VLA-006` 白板/口述练习或补一个 FK artifact。

### 一致性修复切片：VOL 08 CODE-VLA-001..006 source/knowledge 状态（已完成，WARN）

- 审计发现六个 VOL 08 CODE 节点的 review 已标记下游同步，但部分 canonical Markdown 仍残留 `knowledge_pending`、`card_pending` 或“下一步生成题卡”旧措辞。
- 已统一 `source freeze → knowledge → card` 状态为 `knowledge_synced / card_synced`，重新渲染 6 个 source HTML 与 6 个 knowledge HTML，并更新 12 个 review SHA。
- 知识地图、`vla/README.md`、`sources/README.md` 已同步；自动校验确认 12 个 HTML 的 source SHA 与 canonical Markdown 一致，所有 review JSON 可解析。
- 下一 bounded slice：修复 `SYS-VLA-001` 与 VOL 06 `PER-001/PER-005` 中同类的 stale source/knowledge 状态，再决定是否新增知识节点。

### 一致性修复切片：SYS-VLA-001 + VOL 06 PER-001/PER-005（已完成，WARN）

- `SYS-VLA-001`、`VLA-PER-001`、`VLA-PER-005` 的 source/knowledge canonical 已改为明确的 `knowledge_synced / card_synced` 状态；过期的“下一步生成题卡”措辞已替换为口述练习或 artifact 收集。
- 重新渲染 6 个受影响 HTML，并更新对应 source/knowledge review SHA；PER-001 的下游 review 从 `PENDING` 收口为“知识页与题卡已同步”。
- 静态校验确认受影响 HTML 各有一个 `h1`、canonical SHA 一致、review JSON 可解析；视觉 QA 仍受 `file://` 策略阻断，节点保持 `WARN`。
- 下一 bounded slice：做一次 `SYS-VLA-001` 或 `VLA-PER-001..005` 真实口述，或补一个平台/grounding/navigation artifact；不因状态修复升级 mastery。

### 当前切片：VOL 04 VLA-WM-020 Failure Diagnostics（已完成，WARN）

- 已冻结 posterior collapse、action ignoring、future leakage、background shortcut 的 primary/official-code 边界与最小诊断矩阵；不把未运行 probe 写成项目结果。
- 已生成 `sources/vol_04_wm020_failure_diagnostics_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm020_failure_diagnostics.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm020.md/.html/.question_list.md/.review.json`。
- 题卡覆盖 latent ablation、action swap/sweep、future-removal/causal-mask audit、background/domain holdout 和 counterfactual；短答 176 字、机制展开 331 字，保持 `unseen/WARN`。
- VOL 04 已同步到 knowledge/cards `22/44`，全局题库从 211 增至 212；下一 bounded slice 只进行 WM-020 真实口述或补一个诊断 artifact，WM-021..038 继续后置。

### 当前切片：VOL 04 VLA-WM-021 Dreamer Imagination Actor/Critic（已完成，WARN）

- 已冻结 DreamerV3 的 replay posterior 起点、prior latent imagination、actor/critic、lambda-return、gradient routing 与 model-bias 证据边界；保留 reimplementation provenance，不称作者官方代码。
- 已生成 `sources/vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm021_dreamer_imagination_actor_critic.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm021.md/.html/.question_list.md/.review.json`。
- 题卡短答 175 字、机制展开 305 字，保持 `unseen/WARN`；本地 checkpoint、imagined/real paired trace、horizon sweep、value calibration 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `23/44`，全局题库从 212 增至 213；下一 bounded slice 只进行 WM-021 真实口述或补一个 paired artifact，WM-022..038 继续后置。

### 当前切片：VOL 04 VLA-WM-022 MPC/CEM/MPPI/Best-of-N（已完成，WARN）

- 已冻结 MPC 闭环范式、CEM/MPPI proposal update、best-of-N selector、N/H/K、scorer、latency、controller 与 model/scorer optimism 的边界。
- 已生成 `sources/vol_04_wm022_mpc_cem_mppi_best_of_n_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm022_mpc_cem_mppi_best_of_n.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm022.md/.html/.question_list.md/.review.json`。
- 题卡短答 171 字、机制展开 278 字，保持 `unseen/WARN`；本地 planner runtime、checkpoint、N/H sweep、selected-vs-unselected episodes、latency trace 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `24/44`，全局题库从 213 增至 214；下一 bounded slice 只进行 WM-022 真实口述或补一个 planning artifact，WM-023..038 继续后置。

### 当前切片：VOL 04 VLA-WM-023 Open-loop / Receding-horizon Replanning（已完成，WARN）

- 已冻结 PlaNet 的每时刻 first-action planning、Diffusion Policy 的 \(T_o/T_p/T_a\)、ACT 的 action chunk/temporal ensemble，以及 Cosmos/WAM 的 16-step open-loop 与 32→16 requery protocol；重点拆开 prediction horizon \(H\)、execution horizon \(K\)、observation age、queue、同步/异步/event-trigger replan。
- 已生成 `sources/vol_04_wm023_open_loop_receding_horizon_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm023_open_loop_receding_horizon.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm023.md/.html/.question_list.md/.review.json`。
- 题卡短答 175 字、机制展开 325 字，保持 `unseen/WARN`；本地 planning runtime、同 checkpoint \(H/K\) paired curve、latency trace、扰动 bundle 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `25/44`，全局题库从 214 增至 215；下一 bounded slice 只进行 WM-023 真实口述或补一个 horizon/latency artifact，WM-024..038 继续后置。

### 当前切片：VOL 04 VLA-WM-024 Reward / Value / Success / Termination（已完成，WARN）

- 已冻结 step reward、policy-conditioned V/Q、task success predicate/classifier、termination/continuation、timeout/truncation 的时间粒度、label、return/bootstrap 与 protocol 边界。
- 已生成 `sources/vol_04_wm024_reward_value_success_termination_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm024.md/.html/.question_list.md/.review.json`。
- 题卡短答 180 字、机制展开 328 字，保持 `unseen/WARN`；本地 reward/value/success/termination artifact、calibration、paired candidate outcome 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `26/44`，全局题库从 215 增至 216；下一 bounded slice 只进行 WM-024 真实口述或补一个 value/success artifact，WM-025..038 继续后置。

### 当前切片：VOL 04 VLA-WM-025 Cosmos/WAM Slot / Mask / Loss（已完成，WARN）

- 已冻结 Cosmos/WAM 的 policy/world/value 概率角色、LIBERO/RoboCasa unified latent layout、action/future/value inject/extract、sample routing、condition/target/metric mask、EDM loss 与最小单测。
- 已生成 `sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm025.md/.html/.question_list.md/.review.json`。
- 题卡短答 180 字、机制展开 350 字，保持 `unseen/WARN`；exact local config、checkpoint、role-slot trace、gradient、paired ablation 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `27/44`，全局题库从 216 增至 217；下一 bounded slice 只进行 WM-025 真实口述或补一个 slot/mask artifact，WM-026..038 继续后置。

### 当前切片：VOL 04 VLA-WM-026 World/Value Auxiliary → Action Imitation（已完成，WARN）

- 已冻结 action-consequence representation、value/task-progress signal、rollout data coverage、shared-gradient alignment、same-data/same-compute matched ablation、metric ladder 与负迁移矩阵。
- 已生成 `sources/vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.md/.html/.review.json`、`knowledge/vol_04_world_model_sim2real_wm026_world_value_auxiliary_action_imitation.md/.html/.review.json` 与 `questions/vol_04_world_model_sim2real_wm026.md/.html/.question_list.md/.review.json`。
- 题卡短答 165 字、机制展开 341 字，保持 `unseen/WARN`；local config/checkpoint、gradient alignment、matched metric、episode 与 ownership 仍缺。
- VOL 04 已同步到 knowledge/cards `28/44`，全局题库从 217 增至 218；下一 bounded slice 只进行 WM-026 真实口述或补一个 auxiliary-ablation artifact，WM-027..038 继续后置。

### Next 3：真实口述与其余本地证据

- 256 张题卡继续保持 `unseen`，等待候选人真实口述；不得因 HTML 生成创建 coaching state。
- 五项目 inventories 与 ownership ledgers 已完成 5/5；继续收集 OpenPiVLA checkpoint/action schema/eval summary、WAM checkpoint/metric/episode/ownership bundle、UWM checkpoint/normalizer/episode 与候选人角色确认。
- VOL 03 Source Audit A–F 仍保留 WARN；后续需独立核对 paper/repo 版本、mask、solver 与 controller 边界。
- VOL 04 aggregate knowledge/cards 当前覆盖 WM-001..044（44/44）；WM-011..038 使用独立原子页承载，基础页保留 WM-001..010 与 WM-039..044。所有 44 张题卡仍 `unseen`；下一步只进行一题真实口述或补 UWM/WAM P0 artifact，不重新生成已存在节点。视觉 QA 当前受 in-app Browser 的 file:// 策略阻断。

### 一致性修复切片：VOL 04 Aggregate 44/44（已完成，WARN）

- 状态审计发现 WM-011..038 的 source/knowledge/card 文件均已存在，但卷级 knowledge/question review 仍残留“16/44、其余未生成”的旧状态。
- 已把基础页明确定位为 16 个入口节点，将 WM-011..038 的 28 个独立原子页计入 aggregate；卷级 knowledge/cards 同步为 44/44，题卡全部保持 `unseen`。
- README、Knowledge Map、master index 和路线图按 aggregate contract 统一；页面完成不升级 `reviewed/drilled`，UWM/WAM local runtime 与 browser visual QA 缺口仍保持 WARN。

### 当前切片：VOL 02 独立事实复核与边界回写（已完成，WARN）

- 已冻结 DAgger、GAE、PPO、CQL、IQL、DPO、GRPO 七篇 primary paper，以及 Gymnasium timeout 与 PyTorch KLDivLoss 官方文档；复核记录在 [`vol_02_il_rl_posttraining_independent_fact_review`](vla/sources/vol_02_il_rl_posttraining_independent_fact_review.html)。
- 已把 GAE 的 `terminated/truncated` bootstrap 语义、CQL “核心正则项而非完整 objective”与 Robot Harness `offline_grouped_reward_weighted_policy_update` 边界回写到 VOL 02 knowledge/question canonical，并重新渲染；SHA、单 H1、公式 `<em>` 污染、链接均静态通过。
- VOL 02 当前为 `fact_reviewed_candidate / 40 unseen / WARN`；浏览器 `file://` 视觉 QA 仍 `BLOCKED`，Robot Harness scorer/ownership 与真实口述仍未闭合。
- 下一 bounded slice：只做一题真实口述，优先 `VLA-RL-011`、`VLA-RL-027` 或 `VLA-RL-028`；不创建 `coaching_state.md`，不改变其余题卡状态。

### 当前切片：VOL 01 Foundations Batch 1 独立事实复核（已完成，WARN）

- 已冻结 Transformer、LayerNorm、RMSNorm、PyTorch loss/SDPA 与 Modern Robotics 的 primary/official source，形成 `sources/vol_01_batch1_independent_fact_review.md/.html/.review.json`。
- 发现 canonical knowledge 中 `\\theta`、`\\mid`、`\\in`、`\\tilde` 曾被控制字符或缺失反斜杠破坏；已在 Markdown 修复并重新渲染，不手改 HTML。
- 本切片只覆盖 representation/attention/norm/loss/geometry 高频入口；MDP/TD/control、Qwen3-VL/LoRA exact config、OpenPiVLA 轴序、UWM normalizer 和 39 张题卡口述仍为 WARN/PENDING。
- 下一 bounded slice：一题真实口述，或 VOL 01 MDP/TD/control 独立复核；不因 Batch 1 静态完成升级整卷 mastery。

### 当前切片：VOL 01 Foundations Batch 2 MDP / TD / Control（已完成，WARN）

- 已冻结 Sutton–Barto、Gymnasium timeout、Modern Robotics Jacobian/IK、ROS REP-103 与 Feedback Systems，生成 `sources/vol_01_batch2_mdp_td_control_independent_fact_review.md/.html/.review.json`。
- knowledge 已显式区分 `terminated` 与 `truncated`、修正 Jacobian inverse/伪逆风险，并让闭环伪代码分别保存 termination、truncation、success 与 trace。
- `VLA-FND-024/026/028/029` 项目挂钩已降级：Harness 不再称 online GRPO，WAM 历史比例不再作为强结果，UWM root cause 保持诊断假设；39 张题卡仍全部 `unseen`。
- SHA、单 H1、链接、公式、details 平衡与控制字符静态校验通过；advanced control（impedance/MPC）与真实口述仍为下一 evidence gate。

### 当前切片：VOL 01 Foundations Batch 3 Advanced Control（已完成，WARN）

- 已冻结 Hogan impedance、Rawlings MPC、Diffusion Policy 与 OpenVLA，生成 `sources/vol_01_batch3_advanced_control_independent_fact_review.md/.html/.review.json`。
- knowledge 新增 impedance 目标动态关系、受约束 finite-horizon MPC objective、learned policy 输出接口和四类场景的分层组合矩阵；每个公式均补充变量、直觉和实现 gate。
- `VLA-FND-039` 已更新为 contact/model/constraint/latency/data/fallback 选择逻辑，来源从单一 Modern Robotics 扩展至 control/policy primary sources；项目挂钩明确不声称 OpenPiVLA/UWM 已实现 impedance 或 MPC。
- SHA、单 H1、链接、公式污染、控制字符、39/39 details 和答案长度静态通过；VOL 01 仍为 candidate/WARN，39 张题卡全部 `unseen`。

### 当前切片：VOL 01 39-Card Completion Fact Reconciliation（已完成，WARN）

- 已生成 `sources/vol_01_completion_independent_fact_review.md/.html/.review.json`，逐卡核对 `VLA-FND-001..039` 的 ID、短答、来源、项目 hook、追问、易错点与练习状态。
- 题卡来源表扩展到 45 个 primary/official/local-evidence 入口；Deep Learning、BatchNorm、L1/Softmax、KL divergence、Pre-LN、AMP、clip、REP-103、Feedback、Modern Robotics Ch.5/6、DAgger、Gymnasium 与五项目 inventories 已补齐，45/45 定义且均被使用。
- 确定性校验：39 unique IDs 完整覆盖 001..039，39/39 六字段齐全，答案 101–210 字，39/39 `unseen`，details 39/39 平衡；SHA/H1/公式/链接/控制字符与 275 个 review JSON 解析通过。
- VOL 01 当前为 `fact_reviewed_candidate / completion_reconciled / WARN`；不再生成新卡，下一步只做真实口述或转入另一卷事实审查。

### 当前切片：VOL 03 44-Card Completion Reconciliation（已完成，WARN）

- 已生成 `sources/vol_03_completion_fact_reconciliation.md/.html/.review.json`，覆盖 12 个 `VLA-ARCH` 与 32 个 `VLA-ACT` 稳定 ID，并逐组映射 Source Audit A–F。
- 题卡新增 OpenPiVLA Claim–Evidence Inventory 与 Ownership Ledger 总门；π0.5、inventory、ownership 纳入 24 个来源，24/24 均有定义且被使用。
- 修复六个 A–F review 的 12 位截断 SHA；六者现均为完整 64 位且匹配 canonical/HTML metadata。另修复 ACT-031 MathJax controller transform 与 ACT-032 `np.clip`/NaN 追问。
- 确定性校验：44 unique expected IDs、44/44 八字段、短答 113–176 字、机制 192–345 字、44/44 `unseen`、details/links/SHA/H1/formula/control-char 与 276 个 review JSON 解析通过。
- 当前只升级为 `completion_reconciled_candidate / source_audits_warn / WARN`；A–F independent review 与 OpenPiVLA local runtime/ownership 仍未闭合，不升级 reviewed/drilled。

### 当前切片：VOL 03 Source Audit A OpenVLA Endpoint / Token / Mask（已完成，WARN）

- 已直接读取 OpenVLA paper `2406.09246v3` 与 frozen commit `c8f03f...` 的 `action_tokenizer.py`、`datasets.py`、`prismatic.py`、`base_strategy.py` 和 `openvla.py`，生成独立复核 `sources/vol_03_openvla_endpoint_independent_fact_review.md/.html/.review.json`。
- 确认 paper abstraction 为 256 bins / 0..255；frozen encoder 用 256 thresholds 生成尾部 256 token IDs，decoder 只有 255 centers，`b=255` 与 `b=256` 均 alias 到 center 254（0.996078...）。
- 确认训练 CE 可包含 action + optional EOS，而 action accuracy/L1 metric mask 只选 256 个 action IDs；连续 L1 不是 optimization objective 或 closed-loop success。
- knowledge、`VLA-ARCH-005`、`VLA-ACT-003` 已回写三层 cardinality；Audit A review 改为 independent PASS WITH WARNING，local tokenizer/checkpoint/stats/controller/97.4%/ownership 仍 WARN。
- 静态校验通过；44 张卡继续 `unseen`。下一 source slice 转入 Audit E Flow/π0 time-direction/sign。

### 当前切片：VOL 03 Source Audit E Flow Matching / π0 Time–Sign（已完成，WARN）

- 已直接读取 Flow Matching paper `2210.02747v2`、π0 paper `2410.24164v4` 与 frozen OpenPI commit `15a9616...` 的 `pi0.py`，生成 `sources/vol_03_flow_pi0_time_sign_independent_fact_review.md/.html/.review.json`。
- 确认 Theorem 2 在 positivity assumption 下给出 objectives 相差参数无关常数与 gradient equivalence；原论文 OT endpoint 保留 `sigma_min`，exact-linear 是特例。
- 确认 `t=1-tau`、`u_code=-u_paper` 与负 `dt` 共同保持轨迹；10-step deterministic oracle 两种 convention 均恢复同一 action，最大误差 `2.22e-16`，Beta fixed-grid 均满足 `t+tau=1`。
- Audit E、knowledge、`VLA-ACT-023`、completion、README 与知识地图已同步；本地 model class/checkpoint/mask/normalizer/H/K/solver/controller/97.4%/ownership 和口述仍保持 `WARN/PENDING`，44 张卡继续 `unseen`。
- 下一 bounded slice 已在下方接续为 Source Audit B 的 π0/π0.5/FAST/OpenPI 独立事实复核；不因本次事实复核升级 mastery。

### 当前切片：VOL 03 Source Audit B π0 / π0.5 / FAST / OpenPI（已完成，WARN）

- 已直接读取 π0.5 v1、FAST v1 PDF、OpenPI frozen commit 的 `pi0_fast.py`、`pi0_config.py`、`tokenizer.py`、`transforms.py`、`libero_policy.py`、`main.py`、`training/config.py` 与 FAST Hub revision，生成 `sources/vol_03_pi0_fast_openpi_independent_fact_review.md/.html/.review.json`。
- 确认 π0.5 paper 的 FAST pre-training + flow post-training hybrid 与 frozen `Pi0(pi05=True)`/`Pi0FAST` 分叉；确认 paper vocab=1024、Hub vocab=2048、processor 外置 normalization、D/H defaults 与 `pi0_fast_libero` D=7/H=10 override。
- 确认 FAST prefix/postfix/loss mask、special-token skip、malformed decode zero fallback、PadStatesAndActions、LIBERO 7D output slice、norm stats contract、180° image flip 与 replan=5 example；deterministic probes 已通过。
- Audit B、knowledge、题卡、completion、README 与知识地图已同步；local checkpoint/tokenizer revision/stats/axis/unit/H/K/controller/eval/ownership 与口述仍保持 `WARN/PENDING`，44 张卡继续 `unseen`。
- 下一 bounded slice：Source Audit C ACT paper/code gap 已完成；下一步为 Audit D 或一题真实口述，不因事实复核升级 mastery。

### 当前切片：VOL 03 Source Audit C ACT paper/code 独立事实复核（已完成，PASS WITH WARNING）

- 已直接复核 ACT v1 PDF 与 frozen commit `742c753c0d4a5d87076c8f69e5628c79a8cc5488` 的 `detr_vae.py`、`transformer.py`、`policy.py`、`utils.py`、`imitate_episodes.py`、`constants.py`，生成 `sources/vol_03_act_independent_fact_review.md/.html/.review.json`。
- 事实闭环：posterior 只看 qpos/action chunk；latent 为 32D，推理固定 `z=0`；正文/代码为 masked L1 + KL，Algorithm 1 仍写 MSE；padding numerator masked 但 full `B×H×D` mean 稀释分母；frozen query 为 learned `nn.Embedding`；temporal ensemble 融合同一 target time 的 query，oldest row 权重最大；zero sentinel、query cadence 与 H/K/R synthetic probes 已通过。
- 下游已同步 knowledge/questions/completion/README/knowledge map；`VLA-ACT-011..017` 与全卷 44 张题卡继续 `unseen`，local OpenPiVLA H/K/action schema/normalization/controller/eval/ownership 仍 `WARN/PENDING`。
- HTML 已从 canonical Markdown 重渲染；source SHA、review SHA、单 H1、MathJax 与 local-link 静态合同待本轮统一校验；浏览器 `file://` 视觉 QA 记录为 `BLOCKED`。
- 下一 bounded slice：Source Audit D Diffusion Policy，或进行一题 ACT 真实口述；不批量新增题卡，不创建 `coaching_state.md`。

### 当前切片：VOL 03 Source Audit D Diffusion Policy 独立事实复核（已完成，PASS WITH WARNING）

- 已直接复核 Diffusion Policy v5 PDF、`real-stanford/diffusion_policy@5ba07ac6661db573af695b419a7947ecb704690f` 的 UNet/Transformer policy、sampler、PushT runner、MultiStepWrapper、real eval 与 `diffusers=0.11.1` scheduler，生成 `sources/vol_03_diffusion_policy_independent_fact_review.md/.html/.review.json`。
- 事实闭环：epsilon/sample target 与 unsupported v-pred 分支、condition mask 后 full-element mean、boundary-repeat padding、(T_o/T_p/T_a/K_d/R) 分离、`To-1` action slice、论文 warm-start 与 frozen fresh-Gaussian/reject-`past_action` gap、paper 10/16 与 runtime 16 steps、sim wrapper 和 real timestamp queue 已核对；synthetic probes 已通过。
- 下游已同步 knowledge/questions/completion/README/knowledge map；`VLA-ACT-017..022` 与全卷 44 张题卡继续 `unseen`，local OpenPiVLA scheduler/normalizer/action schema/H/K/R/controller/eval/ownership 仍 `WARN/PENDING`。
- HTML 已从 canonical Markdown 重渲染；本地 `file://` 视觉 QA 继续记录为 `BLOCKED`。
- 下一 bounded slice：进行一题 ACT/Diffusion 真实口述，或收集一个本地 OpenPiVLA runtime artifact；不批量新增 VOL 03 题卡，不创建 `coaching_state.md`。

### 当前切片：OpenPiVLA 本地 JSON/CE + H/D Shape Contract Artifact Gate（已完成，WARN）

- 直接读取项目外本地 `C:\Users\mousongzhe\Project\openpivla_deployment` 的 `formal_train.py`、`recipes.py`、`data.py` 与三个 public smoke summary；生成 `sources/openpivla_formal_json_ce_shape_contract_artifact_gate.md/.html/.review.json`。
- 证据闭环：formal path 使用 assistant JSON content + full-chat Qwen causal CE（只屏蔽 padding，不是 assistant-token-only）；recipe/smoke contract 为 `H=15,D=72`；formatter 每行 `limit=16`，不足 horizon 时重复末行。`fast_tokenizer` 字段本身不证明调用 FAST DCT/BPE。
- 已同步 OpenPiVLA Claim–Evidence Inventory、Ownership Ledger、sources/README、VLA README；`OPV-CL-002` 为 local-direct with warning，`OPV-CL-003` 为 representation-conflict，`OPV-CL-004` 为 semantics-open。没有升级 checkpoint、97.4 benchmark、formal lineage 或个人 ownership。
- 下一 bounded slice 已接续完成 parser/round-trip artifact gate；仍不创建 `coaching_state.md`。

### 当前切片：VOL 03 Source Audit F Architecture / Mask / Execution 独立事实复核（已完成，PASS WITH WARNING）

- 已直接复核 RT-2 v1、Octo v2 与 `octo-models/octo@241fb351...`、`openpi@15a9616...` 的 module/action-head/pretrain config/policy config/transforms/training config/chunk broker/DROID example；生成 `sources/vol_03_architecture_execution_independent_fact_review.md/.html/.review.json`。
- 事实闭环：RT-2 256-bin/token 与 cloud-serving frequency、Octo block-wise readout 与 `timestep_pad_mask & action_pad_mask` valid-count loss、embodiment slice、openpi checkpoint→norm→ordered transforms、`infer_ms` scope、broker cache/requery/reset、DROID `[10,8]` chunk 与 `K=8` execution prefix 已核对；mask/norm/delta/broker/H-K probes 已通过。
- 已同步 Audit F claim-to-code、knowledge/questions/completion/README/knowledge map；VOL 03 Audit A–F public facts 均完成独立切片，但 44 张题卡继续 `unseen`，local checkpoint/schema/controller/latency/ownership 与口述保持 WARN。
- 下一 bounded slice：一题 `VLA-ARCH-010/031` 或 OpenPiVLA ownership 真实口述；不新增题卡、不创建 `coaching_state.md`。

### 当前切片：Repository Completion Audit（已完成，WARN）

- 已生成 `sources/repository_completion_audit.md/.html/.review.json`，从 question summary stable ID 重算八卷与五项目：256 unique cards、无重复，全部 `unseen`；`coaching_state.md` 不存在。
- 明确拆分 coverage、fact/evidence review、artifact lifecycle 与 oral mastery：VOL 01–05 达到当前计划覆盖，VOL 06 只有 PER-001..005，VOL 07 为 inventories/ownership + 33 cards，VOL 08 只有 SYS-001 + CODE-001..006，后三卷未达到整卷退出条件。
- 三联件审计覆盖 286 份 canonical Markdown：283 份有 HTML/review；三份早期 source-plan registry 为显式例外。283 份 review JSON 可解析，verdict 为 280 WARN + 3 PASS WITH WARNING + 0 PASS。
- 已同步 G07 的陈旧 `25/44` 为 `44/44`，修复三份旧式 12 位 SHA、一份 63 位 SHA、两处遗留控制字符，以及 VOL 01/02 consolidated knowledge 的重复手写目录；renderer SHA 按 UTF-8 文本规范化换行计算，避免把 CRLF byte hash 差异误报为 stale；修复不改变题卡状态。
- 下一 bounded slice：OpenPiVLA parser/round-trip artifact gate，或候选人真实回答 `H=15,D=72` 与 formatter `limit=16` 的 contract 风险；不继续批量扩题。

### 当前切片：OpenPiVLA Action JSON Parser / Round-trip Artifact Gate（已完成，WARN）

- 已生成 `sources/openpivla_action_json_parser_roundtrip_artifact_gate.md/.html/.review.json`；直接读取 formal package、official WebSocket eval script 与冻结 summary，并运行内存 AST/probes。
- 72D sentinel 经真实 formatter/JSON 只恢复 `15×16=240` 个标量，相对 `15×72=1080` 少 840（77.78%）；tail-repeat 13 行，empty window/row 可产生 `15×1/15×0`，NaN 没有 strict JSON/finiteness gate。
- `Qwen3VLCollator` 只屏蔽 padding，因此 user prompt、wrapper 与 assistant JSON 全部非 padding token进入 full-sequence CE；旧的 assistant-token-only 口径已在 source gate、inventory、ownership 和项目题卡中纠正。
- formal package AST 中没有 `generate/decode/action-output json.loads`；唯一 `json.loads` 是 MindCube 输入 JSONL。`pi0_aloha_sim` 7D/4-step official WebSocket artifact 是平行 lineage，不能替 formal Qwen parser/controller 补证据。
- 12 张 OpenPiVLA 卡继续 `unseen`；checkpoint、97.4、formal rollout 与 candidate ownership 均未升级。下一 bounded slice 优先 ownership confirmation，或补 immutable formal checkpoint/generation bundle。
- 该 parser gate 完成时仓库为 288 canonical / 285 triplets；随后 VOL 03 registry closure 已把当前值推进为 286 triplets，全局题卡仍为 256 unique unseen。

### 当前切片：VOL 03 Source Registry Lifecycle Closure（已完成，WARN）

- `sources/vol_03_vla_action_sources.md` 已从历史 source plan reconciliation 为当前 registry，并新增 `.html/.review.json`；九篇核心 paper、七个 official repo 与 Audit A–F claim-to-code/independent-review 链均有入口。
- 修复 C–F “independent review 尚未完成”等陈旧状态；当前准确边界为 A/B/E `WARN`、C/D/F `PASS WITH WARNING`，但 local checkpoint/parser/normalizer/controller/97.4 lineage/ownership/oral gates 仍未闭合。
- completion audit、README、sources README 与 knowledge map 已同步为 288 canonical / 286 triplets；剩余 registry-only 例外为 VOL 02 与 VOL 04，两者后续逐个处理。
- 44 张 VOL 03 题卡继续 `unseen`，不新增 ID，不创建 coaching state。下一 bounded slice 在无候选人回答时闭合 VOL 02 source registry。

### 当前切片：VOL 02 Source Registry Lifecycle Closure（已完成，WARN）

- `sources/vol_02_il_rl_posttraining_sources.md` 已从历史 source plan reconciliation 为当前 registry，并新增 `.html/.review.json`；12 篇 primary paper 与 6 个 official docs/repos 均有清晰的 review-depth 边界。
- DAgger、GAE、PPO、CQL、IQL、DPO、GRPO 七个核心方法已独立复核；AWAC、LIBERO、SAC、AI Safety、PCGrad 仍是 supporting registry，TRL exact version/API 未绑定本地实现。
- Robot Harness 保持 reward-shaped offline GRPO-style continuation，不升级为 canonical online GRPO；40 张 VOL 02 卡继续 `unseen`，不创建 coaching state。
- completion audit、README、sources README 与 knowledge map 已同步为 288 canonical / 287 triplets；唯一 registry-only 例外为 VOL 04。下一 bounded slice 在无候选人回答时闭合 VOL 04 source registry。

### 当前切片：VOL 04 Source Registry Lifecycle Closure（已完成，WARN）

- `sources/vol_04_world_model_sim2real_sources.md` 已从历史 source plan reconciliation 为当前 registry，并新增 `.html/.review.json`；16 篇 primary paper/report、9 个 official repo 与五个 source batch 均有入口。
- Audit A Foundations、B UWM、E Benchmark/Protocol 有独立 frozen-source review；Audit C Cosmos/WAM 与 D Sim2Real 仍只有 canonical claim audit，volume-level independent review 明确保留 `PENDING/WARN`。
- 27 个 node source-freeze 覆盖 WM-011..014、WM-016..038，WM-015 由 UWM Audit B 承载，另有 WM-019 local artifact gate；VOL 04 aggregate knowledge/cards 保持 44/44，全部 `unseen`。
- completion audit、README、sources README 与 knowledge map 已同步为 288 canonical / 288 triplets；当前不再有 registry-only 例外。下一 bounded slice 为 VOL 06 Perception/Grounding/Navigation coverage-gap audit，不批量生成节点。

### 当前切片：VOL 06 Perception / Grounding / Navigation Coverage-Gap Audit（已完成，WARN）

- 已生成 `questions/vol_06_perception_grounding_navigation.question_list.md` 与 `sources/vol_06_perception_grounding_navigation_coverage_gap_audit.md/.html/.review.json`，把整卷冻结为 `VLA-PER-001..020`：12 个 P0、8 个 P1。
- 现有 `PER-001..005` 的 source/knowledge/card 三联件重算为 5/20（25%）；`PER-006..020` 只是 planned registry，不进入 256 张已生成题卡，也不改变 mastery。
- 四个学习簇为输入/2D grounding、3D/multi-view/action interface、navigation/map/training、evaluation/robustness/safety；覆盖完成、事实审查、项目证据、视觉 QA 与至少 8 次真实 drill 分开计数。
- 五项目仍为 interface/evidence hook，PER-004 artifact gate 保持 `0_local_direct_navigation_bundles`；下一 bounded slice 只做 `VLA-PER-006` image preprocess/token contract source freeze，不生成 knowledge/card。

### 当前切片：VOL 06 VLA-PER-006 Image Preprocess / Token / Camera Source Freeze（已完成，WARN）

- 已直接冻结 ViT v2、`QwenLM/Qwen3-VL@96588727...`、`qwen-vl-utils=0.0.14`、`transformers=4.57.1@8cb5963...` 与 `Qwen/Qwen3-VL-8B-Instruct@0c351dd...` 的 processor/model artifacts。
- Qwen3-VL-8B contract 为 patch16、merge2、factor32，image placeholder 数来自 `prod(image_grid_thw)/merge²`；official qwen-vl-utils path 是 aspect-preserving smart resize，不是 crop/letterbox。
- 本地 OPD 调用默认 `process_vision_info`（patch14/factor28）后再次进入 Qwen3 processor（factor32），且未传 `do_resize=False`；三组 source-derived probes 记录 shape/token 差异，但没有把静态 mismatch 升级为性能因果结论。
- OpenPiVLA formal MindCube、image-free DROID action 与 square-224 dry-run image lineage 已分离；camera/frame/timestamp/original-resized-grid/inverse manifest 仍缺。下游 knowledge 已在独立切片同步。

### 当前切片：VOL 06 VLA-PER-006 Image Preprocess / Token / Camera Knowledge（已完成，WARN）

- 已生成 `knowledge/vol_06_per006_image_preprocess_token_camera_contract.md/.html/.review.json`，把 raw image、processed image、patch grid 与 language-side image token 四层表示分开。
- 已写入 smart resize、`patch_size=16`、`merge_size=2`、factor32、`N_img=prod(image_grid_thw)/merge²`、pixel normalization，以及 direct resize/crop/letterbox 的正逆坐标映射。
- OPD factor28→32 double-resize 仍只记为静态 contract risk；OpenPiVLA formal/dry-run/image-free lineage 与 camera/order manifest 保持分层，不升级为性能根因或个人贡献。
- 仓库随后在独立切片同步 PER-006 atomic card；knowledge-only 阶段没有提前创建 mastery。

### 当前切片：VOL 06 VLA-PER-006 Atomic Card（已完成，WARN）

- 已生成 `questions/vol_06_per006.md/.html/.review.json` 与单题 question list；题卡包含短答、机制展开、诊断证据、项目挂钩、追问、易错点、危险答案和来源。
- 30 秒答案 158 字、机制展开 343 字；折叠结构、ARIS academic v1、MathJax、本地链接与 canonical/HTML/review SHA 已通过静态验收。
- 题卡只把 OPD factor28→32 写成静态 contract risk，分开 OpenPiVLA formal MindCube、image-free DROID action 与 square-224 dry-run lineage；不写成性能根因或个人创新。
- 仓库同步为 292/292 canonical triplets；全局为 257 张唯一 `unseen` 题卡，`coaching_state.md` 不存在。下一 bounded slice 只做 `VLA-PER-007` source freeze，不生成 knowledge/card。

### 当前切片：VOL 06 VLA-PER-007 Open-vocabulary Grounding Pipeline Source Freeze（已完成，WARN）

- 已生成 `sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.md/.html/.review.json`，冻结Grounding DINO v5、`IDEA-Research/GroundingDINO@856dde20...`与Transformers `4.57.1@8cb5963...`。
- 直接核对query–token dot-product logits、text-token mask、`max_text_len=256`、prompt句点规范化、box/text双阈值、phrase extraction、`cxcywh→xyxy`与frozen helper无NMS调用的边界。
- 本地`muxi@756e27e...`四个文件表明OPD是Qwen3-VL生成式tagged point/box/text SFT+generation+parser路径；repo静态搜索没有显式GroundingDINO/NMS匹配，但不排除未归档runtime。
- 浏览器仍因URL安全策略拒绝`file://`，视觉门保持`BLOCKED`；静态ARIS/SHA/MathJax/anchor/link检查通过。仓库同步目标为293/293 triplets，257张卡继续unseen。
- 下游knowledge已在独立切片同步；source-only阶段没有提前生成card或修改mastery。

### 当前切片：VOL 06 VLA-PER-007 Open-vocabulary Grounding Pipeline Knowledge（已完成，WARN）

- 已生成`knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.md/.html/.review.json`，覆盖三阶段Grounding DINO pipeline、`Q×L` query–token tensor、prompt/token contract与score-calibration边界。
- 已写入query/box gate与phrase-token gate公式、strict-greater-than edge case、deterministic threshold lab、phrase reconstruction与Transformers`labels/text_labels` API drift。
- box geometry继承PER-006 inverse；frozen helper无NMS不被改写成duplicate-free guarantee，新增typed manifest与可审计伪代码。
- 本地OPD保持生成式tagged-coordinate SFT+generation+parser边界，不升级为GroundingDINO/NMS部署、机器人成功或个人ownership。
- 仓库同步目标为294/294 triplets；257张卡继续unseen。下一bounded slice只生成`VLA-PER-007` atomic card，不启动PER-008。

### 当前切片：VOL 06 VLA-PER-007 Atomic Card（已完成，WARN）

- 已生成`questions/vol_06_per007.md/.html/.review.json`与单题question list；题卡覆盖`Q×L` tensor、`L_max=256` token-axis、严格`>`双阈值、phrase reconstruction、coordinate inverse、optional NMS与Transformers API drift。
- 题卡以短答、机制、诊断、项目挂钩、追问、易错点、危险答案和来源组织；保持`L2/P0/unseen`，没有真实回答，因此不创建`coaching_state.md`。
- OPD只作为生成式tagged-coordinate SFT→generation→parser/scorer对照；不升级为GroundingDINO/NMS部署、learned router、机器人成功或个人ownership。
- 仓库同步目标为295/295 triplets；258张卡全部unseen。下一bounded slice只冻结`VLA-PER-008` source，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-008 Representation Choice Source Freeze（已完成，WARN）

- 已生成`sources/vol_06_per008_representation_choice_source_freeze.md/.html/.review.json`，冻结RoboPoint v1、Segment Anything v1、kPAM v2、Where2Act v2及四个official repo的commit/hash/license边界。
- source contract按downstream minimum sufficiency区分point、box、mask、semantic keypoint与action-conditioned affordance；记录mask→box、point→keypoint/affordance不可逆信息损失与typed manifest。
- 本地OPD直接证据显示ShareRobot affordance字段被转换为point target；这支持affordance-labelled point supervision，不支持dense affordance head、SAM/keypoint pipeline、controller feasibility或robot success。
- 仓库同步目标为296/296 triplets；258张卡继续unseen。下一bounded slice只生成`VLA-PER-008` knowledge，不生成card或启动PER-009。

### 当前切片：VOL 06 VLA-PER-008 Representation Choice Knowledge（已完成，WARN）

- 已生成`knowledge/vol_06_per008_representation_choice.md/.html/.review.json`，按downstream minimum-sufficient fields区分point、box、mask、semantic keypoint与action-conditioned affordance。
- 已写入mask→box有损公式与5×5 probe、point/keypoint/affordance非等价、uncertainty/multimodality、typed manifest、选择伪代码、matched representation evaluation与failure taxonomy。
- RoboPoint、SAM、kPAM、Where2Act按native I/O对照；本地OPD继续限定为affordance-labelled point supervision与point/box/text静态pipeline，不升级为dense affordance、controller feasibility或robot success。
- 仓库同步目标为297/297 triplets；258张卡继续unseen。下一bounded slice只生成`VLA-PER-008` atomic card并保持unseen，不启动PER-009。

### 当前切片：VOL 06 VLA-PER-008 Representation Choice Atomic Card（已完成，WARN）

- 已生成`questions/vol_06_per008.md/.html/.review.json`与独立question list；单题为L2/P0，保持`unseen`，未创建`coaching_state.md`。
- 30秒答案169字、机制展开349字；覆盖minimum-sufficient选择、五类typed合同、mask/box与point/semantic/action非等价、diagnostic order和matched evaluation。
- OPD只表述为affordance-labelled point supervision与point/box/text静态pipeline，不升级为SAM/keypoint/dense affordance、controller feasibility、robot success或个人ownership。
- 仓库同步目标为298/298 triplets；259张卡全部unseen。下一bounded slice只冻结`VLA-PER-009` source，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-009 Grounding Matching / Negative / Loss Source Freeze（已完成，WARN）

- 已生成`sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.md/.html/.review.json`，冻结GroundingDINO v5、DETR、Focal Loss、GIoU与固定official/Transformers实现revision。
- 显式区分matching cost与final loss、unmatched-query/non-target-token/padding/dataset negative、GT-box distributed denominator、auxiliary/encoder branches与logging-only cardinality。
- 发现Grounding DINO v5正文与Table 8的classification matching/final权重相反；HF 4.57.1与Table 8一致，因此权重被标记为revision/config-dependent WARN。
- 本地OPD按assistant-token CE、routed top-1 CE与online full-vocab KL三条lineage冻结；2500行metrics复算通过，但不升级为checkpoint/holdout/robot uplift或个人ownership。
- 仓库在source-only切片同步为299/299 triplets；下游knowledge已在独立切片完成。

### 当前切片：VOL 06 VLA-PER-009 Grounding Matching / Negative / Loss Knowledge（已完成，WARN）

- 已生成`knowledge/vol_06_per009_grounding_matching_negative_loss.md/.html/.review.json`，按tensor schema→pairwise cost→Hungarian assignment→negative target→focal/L1/GIoU→reduction→project objective boundary组织。
- 已明确matching cost不等于final loss，区分unmatched query、non-target token、padding、dataset/hard negative，并记录GT-box distributed denominator、auxiliary re-matching和cardinality logging边界。
- Grounding DINO v5正文/Table 8/HF 4.57.1权重冲突保持revision/config gate；本地OPD只按assistant-token CE、routed top-1 CE和online full-vocab KL三条lineage陈述。
- typed loss manifest、可审计训练伪代码、failure taxonomy、两分钟回答与危险答案已写入；2500行metrics仍只支持optimization trace，不支持holdout/robot uplift。
- 仓库同步目标为300/300 triplets；259张卡继续全部`unseen`，PER-009 card不存在。下一bounded slice只生成`VLA-PER-009` atomic card并保持unseen，不启动PER-010。

### 当前切片：VOL 06 VLA-PER-009 Atomic Card（已完成，WARN）

- 已生成`questions/vol_06_per009.md/.html/.review.json`与独立question list；单题为L3/P1，保持`unseen`，未创建`coaching_state.md`。
- 30秒答案175字、机制展开344字；覆盖matching cost与final loss、token-axis negatives、focal/L1/GIoU、distributed reduction、auxiliary re-matching与revision/config权重门。
- OPD只按assistant-token CE、routed top-1 CE和online full-vocabulary KL三条lineage陈述；2500行metrics仍只支持optimization trace，不升级为checkpoint-bound holdout、robot uplift或个人ownership。
- 仓库同步目标为301/301 triplets；260张卡全部`unseen`。下一bounded slice只做`VLA-PER-010` metric/parser source freeze，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-010 Grounding Metric / Parser / Protocol Source Freeze（已完成，WARN）

- 已生成`sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.md/.html/.review.json`，冻结MDETR、COCO API、RoboPoint、MPII/MMPose与本地OPD evaluator/inventory证据。
- 已区分strict/lenient parser、tag/syntax/coordinate/geometry状态、IoU/Acc、RefExp Recall@k、COCO AP/AR、PCK、mask-hit、fixed-coordinate Hit、invalid denominator与aggregation。
- MDETR paper IoU/Recall描述与固定commit的GIoU threshold/Precision打印冲突通过deterministic box probe复现；指标必须绑定revision与scorer code。
- 本地OPD只支持static holdout parser/scorer与inventory边界，不升级为standard PCK、robot success、单因素因果或candidate ownership。
- 仓库同步为302/302 triplets；260张卡继续全部`unseen`。下一bounded slice只生成PER-010 knowledge，不生成card或启动PER-011。

### 当前切片：VOL 06 VLA-PER-010 Grounding Metric / Parser / Protocol Knowledge（已完成，WARN）

- 已生成`knowledge/vol_06_per010_grounding_metric_parser_protocol.md/.html/.review.json`，把source contract转译为四层validity、metric family、protocol identity、failure taxonomy与面试回答结构。
- 公式覆盖IoU/Acc、RefExp top-k、PCK、RoboPoint mask-hit、fixed-coordinate any-pair Hit与双向point-set distance；每个公式均含变量、直觉与实现映射。
- 已加入strict/lenient transition matrix、field-specific denominator反例、commented scoring pseudocode、OPD original-strict/protocol-fixed-strict/lenient三口径reconciliation及两个项目hook。
- 仓库同步为303/303 triplets；260张卡继续全部`unseen`，PER-010 card不存在。下一bounded slice只生成PER-010 atomic card并保持unseen，不启动PER-011。

### 当前切片：VOL 06 VLA-PER-010 Atomic Card（已完成，WARN）

- 已生成`questions/vol_06_per010.md/.html/.review.json`与独立question list；单题为L2/P0，保持`unseen`，未创建`coaching_state.md`。
- 30秒答案180字、机制展开338字；覆盖四层validity、strict/lenient双轨、IoU/Acc/RefExp/COCO/PCK/mask-hit/fixed Hit非等价、invalid denominator与protocol identity。
- 诊断链保留MDETR IoU/GIoU判定翻转、本地mixed→text/lenient fallback/字段分母差异与OPD original-strict/protocol-fixed-strict/lenient三口径边界。
- 本卡不把fixed Hit叫标准PCK，不把10k static holdout升级为robot success、单因素因果或candidate ownership。
- 仓库同步为304/304 triplets；261张卡全部`unseen`。下一bounded slice只做`VLA-PER-011` pseudo-label/teacher-noise source freeze，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Source Freeze（已完成，WARN）

- 新增canonical source、ARIS HTML与review三联件；固定FixMatch、Noisy Student、calibration、curriculum与leakage来源版本/SHA，并把typed pseudo record、risk–coverage、iteration manifest和分层leakage gate写成可审计合同。
- 本地OPD按文件区分人工mix route、path-hash split、teacher-forced top-1 token cache、hard-target trainer、online KL/veto与10k raw holdout；不把logging/sampling schedule升级为confidence calibration，也不把path/fingerprint gate升级为semantic/teacher-lineage无污染。
- 仓库同步为305/305 triplets；review为302 WARN + 3 PASS WITH WARNING；261张卡继续全部`unseen`，PER-011 knowledge/card均不存在。下一bounded slice只生成`VLA-PER-011` knowledge，不生成card或启动PER-012。

### 当前切片：VOL 06 VLA-PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；将source freeze转译为typed pseudo record、hard/soft与teacher-forced/free-generation四象限、FixMatch reduction、risk–coverage、temperature/ECE、selection bias、Noisy Student iteration、curriculum和十层leakage白板链。
- 本地OPD按mix route、top-1 cache、hard trainer、online KL/veto和10k raw holdout分开口述；包含两分钟回答、十四个追问、危险答案修正、诊断playbook与project truth boundary。
- 仓库同步为306/306 triplets；review为303 WARN + 3 PASS WITH WARNING；261张卡继续全部`unseen`，PER-011 card不存在。下一bounded slice只生成一张`VLA-PER-011` atomic card并保持unseen，不启动PER-012。

### 当前切片：VOL 06 VLA-PER-011 Atomic Card（已完成，WARN）

- 新增一张L3/P0折叠题卡、question-list、ARIS HTML与review；30秒/机制答案为179/338字符，包含typed identity、risk–coverage、calibration、Noisy Student/curriculum、十层leakage、OPD四链、诊断probe与truth boundary。
- `VLA-PER-011`全局仅出现一次并保持`unseen`；未创建口述记录、`coaching_state.md`或PER-012 artifact。
- 仓库同步为307/307 triplets；review为304 WARN + 3 PASS WITH WARNING；262张卡全部`unseen`。下一bounded slice只做`VLA-PER-012` segmentation/depth/keypoint/affordance source freeze，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-012 Segmentation / Depth / Keypoint / Affordance Source Freeze（已完成，WARN）

- 新增canonical source、ARIS HTML与review三联件；固定Mask2Former、SAM、Depth Anything V2、kPAM、Where2Act的paper/code revision、SHA和license边界。
- 冻结semantic/instance/panoptic/promptable task、relative/metric depth代码路径、mask→depth→3D→semantic keypoint→primitive-conditioned affordance→planner/controller链与九个deterministic probes。
- 本地OPD五文件复核只支持affordance-labelled point监督，不支持mask/depth/keypoint/dense affordance；仓库同步为308/308 triplets，review为305 WARN + 3 PASS WITH WARNING，262张卡继续`unseen`。下一bounded slice只生成PER-012 knowledge。

### 当前切片：VOL 06 VLA-PER-012 Segmentation / Depth / Keypoint / Affordance Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；把冻结证据转译为task-typed segmentation→relative/metric depth→registered 3D surface→semantic keypoint→primitive-conditioned affordance→planner/IK/collision/controller gate。
- 明确SAM quality不等于robot-success confidence、Depth Anything V2 relative/metric路径与resize边界、kPAM semantic keypoint字段、Where2Act primitive/state/orientation条件，以及本地OPD只支持affordance-labelled point supervision。
- 仓库同步为309/309 triplets；review为306 WARN + 3 PASS WITH WARNING，262张卡继续全部`unseen`。下一bounded slice只生成一张`VLA-PER-012` atomic card并保持unseen，不启动PER-013。

### 当前切片：VOL 06 VLA-PER-012 Segmentation / Depth / Keypoint / Affordance Atomic Card（已完成，WARN）

- 新增一张L3/P1折叠题卡、question-list、ARIS HTML与review；30秒/机制答案为180/350字符，覆盖task-typed segmentation、relative/metric depth、registered 3D surface、semantic keypoint、primitive-conditioned affordance与planner/controller gate。
- 题卡保留SAM quality、Depth Anything checkpoint/unit、camera/frame/time、keypoint covariance、primitive/state与OPD point-only真实性边界；不把public method、selected-path zero match或Git身份升级为本地集成、robot result或个人ownership。
- `VLA-PER-012`全局仅出现一次并保持`unseen`；仓库同步为310/310 triplets，review为307 WARN + 3 PASS WITH WARNING，263张卡全部`unseen`。下一bounded slice只冻结`VLA-PER-013` source，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-013 Point Cloud / Voxel / BEV / Occupancy Source Freeze（已完成，WARN）

- 新增canonical source、ARIS HTML与review三联件；固定六篇完整PDF、六个official repo commit/date/license与32个关键文件SHA，区分PointNet++ sampling/grouping、voxel/VFE、sparse convolution、pillar/BEV、probabilistic octree和implicit occupancy。
- 九个probe覆盖FPS coverage、voxel boundary、mean alias、dense/sparse memory、pillar z-bin、implicit threshold、local pixel/world、PCD header与local path census。
- Robot Harness直接证据支持2D tri-state occupancy、54,856点PCD资产和path/URL bridge，但不支持自研3D encoder、local BEV/OctoMap、representation benefit或个人ownership；仓库同步为311/311 triplets，review为308 WARN + 3 PASS WITH WARNING，263张卡继续unseen。下一bounded slice只生成PER-013 knowledge。

### 当前切片：VOL 06 VLA-PER-013 Point Cloud / Voxel / BEV / Occupancy Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；把冻结证据转译为metric points→sampling/grouping→voxel/VFE→sparse 3D→pillar/BEV→explicit/octree/implicit occupancy→semantic/action gate。
- 完成typed 3D manifest、PointNet++、FPS/ball/kNN、quantization/aggregation alias、SubM/Sparse/Inverse convolution、height compression、BEV calibration、unknown-not-free、memory/metric、十二类failure与面试回答。
- Robot Harness仍只安全映射到2D tri-state map、54,856点PCD schema和path/URL bridge；仓库同步为312/312 triplets，review为309 WARN + 3 PASS WITH WARNING，263张卡继续unseen。下一bounded slice只生成一张PER-013 atomic card并保持unseen。

### 当前切片：VOL 06 VLA-PER-013 Point Cloud / Voxel / BEV / Occupancy Atomic Card（已完成，WARN）

- 新增一张L3/P1折叠题卡、question-list、ARIS HTML与review；30秒回答180字、机制回答348字，覆盖sampling、voxel/VFE、sparse convolution、pillar/BEV、三类occupancy、unknown-not-free与action gate。
- 诊断段保留FPS coverage、voxel boundary、MeanVFE alias、dense memory、pillar z collapse与implicit threshold probes；项目段只映射Robot Harness 2D map、54,856点PCD schema和bridge。
- `VLA-PER-013`全局仅出现一次并保持`unseen`；仓库同步为313/313 triplets，review为310 WARN + 3 PASS WITH WARNING，264张卡全部`unseen`。下一bounded slice只冻结`VLA-PER-014` 3D semantic/open-vocabulary grounding source。

### 当前切片：VOL 06 VLA-PER-014 3D Grounding / Spatial Relation / Open-vocabulary 3D Scene Source Freeze（已完成，WARN）

- 新增canonical source、ARIS HTML与review三联件；固定ScanRefer、ReferIt3D、OpenScene、OpenMask3D、LERF、ConceptFusion六篇完整PDF，六个official repo commit/date/license与36个关键文件SHA。
- 分离3D referring box、candidate listener、per-point semantics、instance mask、continuous language field与semantic map query，冻结relation frame/arity、prompt/negative/normalization、proposal bottleneck、metric identity与九个deterministic probes。
- OPD direct evidence只支持Visual Genome 2D image relation与0–1000 point/box；Robot Harness只有2D tri-state occupancy、non-semantic PCD和bridge。仓库同步为314/314 triplets，review为311 WARN + 3 PASS WITH WARNING，264张卡继续全部`unseen`。下一bounded slice只生成PER-014 knowledge。

### 当前切片：VOL 06 VLA-PER-014 3D Grounding / Spatial Relation / Open-vocabulary Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；把冻结证据转成geometry→entity→language→decision→action-gate教学链，区分box、candidate、point、mask、field、map六类输出。
- 完成typed manifest、candidate hard upper bound、ScanRefer/ReferIt3D/OpenScene/OpenMask3D/LERF/ConceptFusion机制、relation frame/arity、score calibration、metric protocol、九个probe、first-divergence diagnosis与两档面试回答。
- OPD仍只支持2D image relation/point-box监督，Robot Harness仍只支持2D occupancy/non-semantic PCD/bridge；仓库同步为315/315 triplets，review为312 WARN + 3 PASS WITH WARNING，264张卡继续全部`unseen`。下一bounded slice只生成一张PER-014 atomic card。

### 当前切片：VOL 06 VLA-PER-014 3D Grounding / Spatial Relation / Open-vocabulary Atomic Card（已完成，WARN）

- 新增一张L3/P1折叠题卡、question-list、ARIS HTML与review；30秒/机制回答为155/335字符，覆盖六类output、candidate hard bound、relation frame/arity、score calibration、metric protocol与PER-015 action gate。
- 诊断段保留IoU 1/3、target-absent top-1=0、yaw frame flip、semantic/instance、view cancellation和negative calibration probes；项目段只映射OPD 2D image relation与Robot Harness non-semantic PCD/occupancy/bridge。
- `VLA-PER-014`全局仅出现一次并保持`unseen`；仓库同步为316/316 triplets，review为313 WARN + 3 PASS WITH WARNING，265张卡全部`unseen`。下一bounded slice只冻结`VLA-PER-015` perception→action/reachability/uncertainty/failure-gate source。

### 当前切片：VOL 06 VLA-PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Source Freeze（已完成，WARN）

- 六份完整PDF与六个official repo/35文件已固定版本、license与SHA；typed manifest和identity/workspace/IK/bounds/singularity/collision/trajectory/uncertainty/controller九层gate已建立。
- 10个deterministic probe全部命中预期拒绝/求助决策；五项目11个local-direct文件只支持接口或诊断例外，不支持通用物理gate、robot success或候选人ownership。
- 仓库同步为317/317 triplets，review为314 WARN + 3 PASS WITH WARNING，265张卡继续全部`unseen`。下一bounded slice只生成PER-015 knowledge，不生成card、不启动PER-016。

### 当前切片：VOL 06 VLA-PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；把冻结证据转译为typed perception→action manifest，以及identity/workspace/IK/bounds/singularity/collision/trajectory/uncertainty/controller九层fail-closed gate。
- 已覆盖2R workspace、SE(3) residual、pseudoinverse IK、TRAC-IK能力边界、Jacobian SVD、MoveIt PlanningScene、OMPL/RRT-Connect、robust clearance、trajectory dynamics、controller schema、action chunk staleness、KnowNo conformal abstention、10个probe与first-divergence diagnosis。
- 五项目仍只按local-direct接口/诊断证据口述，不升级为通用物理gate、robot success或候选人ownership；仓库同步为318/318 triplets，review为315 WARN + 3 PASS WITH WARNING，265张卡继续全部`unseen`。下一bounded slice只生成一张PER-015 atomic card并保持unseen，不启动PER-016。

### 当前切片：VOL 06 VLA-PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Atomic Card（已完成，WARN）

- 新增一张L3/P0折叠题卡、question-list、ARIS HTML与review；30秒/机制回答为141/257字符，覆盖typed action manifest、workspace/IK/bounds/singularity、state/motion collision、robust clearance、trajectory/controller、uncertainty/abstention与failure recovery。
- 诊断段保留10个deterministic probes和first-divergence顺序；项目段只映射OPD、Robot Harness、OpenPiVLA、WAM、UWM的local interface/diagnostic evidence，不升级为通用physical gate、robot uplift或候选人ownership。
- `VLA-PER-015`全局仅出现一次并保持`unseen`；仓库同步为319/319 triplets，review为316 WARN + 3 PASS WITH WARNING，266张卡全部`unseen`。下一bounded slice只冻结`VLA-PER-016` localization/odometry/SLAM/map-frame/drift source，不生成knowledge/card。

### 当前切片：VOL 06 VLA-PER-016 Localization / Odometry / SLAM / Map-frame / Drift Source Freeze（已完成，WARN）

- 冻结六份完整PDF、六个official repo/36个核心文件，覆盖localization/odometry/mapping/SLAM/tracking区分、REP-105 `map→odom→base`、VIO state/covariance、front-end/back-end、preintegration/marginalization、loop/relocal/map merge、pose graph、DROID learned SLAM与ATE/RPE alignment。
- 10个deterministic probes命中预期；Robot Harness六个local-direct bridge/map文件和一项fallback targeted test只支持资产/接口与software-only fallback，不证明本地SLAM实现或结果。
- 仓库同步为320/320 triplets，review为317 WARN + 3 PASS WITH WARNING，266张卡继续全部`unseen`；PER-016 knowledge/card不存在，PER-017未启动，`coaching_state.md`不存在。下一bounded slice只生成PER-016 knowledge。

### 当前切片：VOL 06 VLA-PER-016 Localization / Odometry / SLAM / Map-frame / Drift Knowledge（已完成，WARN）

- 新增canonical knowledge、ARIS HTML与review三联件；651行内容把冻结来源转译为tracking/odometry/localization/mapping/SLAM taxonomy、typed manifest、REP-105 `map→odom→base`、state/covariance、preintegration、front/local/backend/global分层、gauge/keyframe/marginalization与loop/relocal/map-merge合同。
- 已覆盖pose graph、八类drift、DROID learned-SLAM边界、ATE/RPE与SE3/Sim3 alignment、六系统比较、10个deterministic probes、first-divergence诊断、fail-closed pseudocode、30秒/2分钟回答、26个追问、16个危险回答与五项目truth boundary。
- 仓库同步为321/321 triplets，review为318 WARN + 3 PASS WITH WARNING，266张卡继续全部`unseen`；PER-016 card不存在，PER-017未启动，`coaching_state.md`不存在。下一bounded slice只生成一张PER-016 atomic card并保持unseen。

### 当前切片：VOL 06 VLA-PER-016 Localization / Odometry / SLAM / Map-frame / Drift Atomic Card（已完成，WARN）

- 新增一张L3/P1折叠题卡、question-list、ARIS HTML与review；30秒/机制回答为179/350字符，覆盖taxonomy、typed identity、map/odom、state/covariance、preintegration、front/back end、loop/relocal/map merge、drift与ATE/RPE alignment。
- 诊断段保留10个deterministic probes和sensor→metric→consumer的first-divergence顺序；项目段只映射Robot Harness map/PCD/software-only bridge与其余四项目upstream/interface evidence，不升级为本地SLAM、robot result或候选人ownership。
- `VLA-PER-016`全局仅出现一次并保持`unseen`；仓库同步为322/322 triplets，review为319 WARN + 3 PASS WITH WARNING，267张卡全部`unseen`。PER-017未启动，`coaching_state.md`不存在；下一bounded slice只冻结PER-017 belief/memory/frontier/active-exploration source。

### 当前切片：VOL 04 Audit C Cosmos Policy / WAM Independent Fact Review（已完成，PASS WITH WARNING）

- 重新获取arXiv `2601.16163v1` 22页paper、`NVlabs/cosmos-policy@18a2acc`的13个代表文件与664-entry tree、三份固定HF model revision；13/13 Git blob、两份policy config/statistics SHA与base/policy license分层均闭合。
- 独立复核统一latent slot、50/25/25 routing、condition/target/metric mask、EDM loss、5-step sampler、direct/dual-checkpoint planning、LIBERO/RoboCasa protocol；10/10 deterministic probes通过，并确认`mask_value_prediction_loss_for_policy_prediction`未进入final apply-mask条件的风险。
- WAM 9/9 local artifact SHA重新命中；base/trained两侧均为CoffeePressButton episode0 `success=false`，300×7→300×12 trace只支持diagnostic，远端checkpoint path不升级为binary hash或uplift。仓库同步为330/330 triplets，review为325 WARN + 5 PASS WITH WARNING，269张卡继续全部`unseen`，`coaching_state.md`不存在。下一bounded slice优先真实口述；若继续文档复核，只做Audit D，不启动PER-019。

### 当前切片：VOL 04 Audit D Sim2Real Independent Fact Review（已完成，PASS WITH WARNING）

- 重新获取10份固定arXiv PDF，合计124页/0空白页；固定MuJoCo `3.10.0@28009f9`源码、OpenCV fixed commit与robosuite `v1.5.1@51cc017`，并把mutable stable docs响应SHA与runtime build identity分开。
- 独立复核六层reality-gap、DR并非越宽越好、SysID+DR互补、SimOpt distribution adaptation、UP-OSI/RMA、residual、latency/contact、chance/recovery边界；12/12 deterministic probes通过，WM-031..038与WM-040..044 source→knowledge→card一致。
- 五项目仍只有simulator/offline/interface/diagnostic/高层cancel证据，不支持真机Sim2Real或physical safety；仓库同步为331/331 triplets，review为325 WARN + 6 PASS WITH WARNING，269张卡继续全部`unseen`，`coaching_state.md`不存在。VOL 04 Audit A–E public facts现均已独立复核；下一bounded slice优先真实口述或P0 immutable project bundle，不启动PER-019。

### 当前切片：Robot Harness 五/八模型 × 十套件聚合证据门（已完成，WARN）

- 新增canonical evidence、ARIS HTML与review三联件；固定两份2026-07-07 overview JSON/HTML、builder与旧32B/8B comparison SHA，外部`agent`仓库保持只读。
- 13/13 D/OOD/all mean probes、5/5 overview overlap、12/12 archived D/OOD run与60/60 primary metrics均通过；十套件实际混合五种primary metric，`n`分布含1000/1333/1820/2000/5000，因此all-avg只保留为descriptive index。
- 122B/35B input与4个run dir本地缺失；普通同步的60份metrics目录没有full raw predictions（后续切片在隐藏extraction恢复部分raw）；6个distinct model/checkpoint path映射后0/6本地存在，builder/report均untracked，candidate ownership仍PENDING。
- localhost视觉QA在1440×1000与800×1000通过：260px sticky TOC按900px断点折叠为753px static，窄屏document width为785/785，MathJax已渲染且无page-wide横向溢出。
- 仓库同步为332/332 triplets，review为326 WARN + 6 PASS WITH WARNING，269张卡继续全部`unseen`，`coaching_state.md`不存在；本轮没有启动PER-019。下一bounded slice优先真实口述或导入一份common-support raw bundle。

### 当前切片：Robot Harness 四模型 Common-Support Raw Bundle Manifest（已完成，WARN）

- 新增长路径审计工具、machine-readable JSON manifest、canonical evidence、ARIS HTML与review；不复制约61 MB全局raw outputs，只保存目标文件path/SHA/rows/schema与ordered-ID fingerprint。
- 对十套件×base32/SFT32/GRPO100/GRPO200的40个primary slots，实际找回28个、17,117,873 bytes、17,828 rows；全部`bad_json/missing_id/duplicate_id/empty_output=0`，schema/metrics profile各1种。
- `project/safety/browser/appworld/quarantine/robovlm`六个suite的四模型ID set/order exact，每模型共同support共3,457 cases；base/SFT的holdout/cross-source与四模型两套ToolACE共12个primary仍缺。
- 已勘误上一aggregate gate：raw只在普通同步目录缺失，隐藏2026-06-26 extraction保留部分；仍不发布paired uplift，不关闭统一scorer/backend、checkpoint、122B/35B、effect-sink或ownership。
- 仓库同步为333/333 triplets，review为327 WARN + 6 PASS WITH WARNING，269张卡继续全部`unseen`，`coaching_state.md`不存在；本轮未启动PER-019。下一bounded slice优先真实口述；若继续证据，只恢复12个缺失primary或冻结统一scorer/checkpoint后做paired rescoring。

### 当前切片：Robot Harness Missing-12 Recovery Candidate Search（已完成，WARN）

- 扩展既有审计工具与machine manifest，不新增同义报告：为12个缺失slot冻结metrics/run/launch SHA、expected rows、model path、source-suite path和完整remote prediction path。
- 扫描`agent`、`Project`及SHA为`2C1BF435...EFA8CC`的718-member原tar；找到17个同名candidate path，但全是GRPO其他attempt/singleload或8B两行smoke，`eligible_candidates=[]`，tar内0条exact missing target member。
- D缺口expected rows为base/SFT各1333 holdout和1820 cross-source；OOD八个ToolACE slot各1000。12/12 source-suite local locator均不存在，metrics不能替代raw/prompt/tools。
- 仓库仍为333/333 triplets、327 WARN + 6 PASS WITH WARNING、269 cards全部unseen；没有`coaching_state.md`、没有PER-019。下一slice优先真实口述；若用户提供远端只读访问或文件，则按12条locator恢复，不用同名候选凑数。

### 当前切片：VOL 08 Coding / System Design Coverage-Gap Audit（已完成，WARN）

- 冻结`SYS-VLA-001..004`与`CODE-VLA-001..008`共12节点；当前`SYS-VLA-001`与`CODE-VLA-001..006`已有source/knowledge/card，覆盖为7/12，七张卡全部`unseen`。
- `SYS-VLA-002..004`与`CODE-VLA-007..008`保持planned；后两者只在早期registry登记，不进入269张generated-card计数。本轮没有生成`SYS-VLA-002`、没有创建`coaching_state.md`、没有启动PER-019。
- 明确VOL 05负责组件机制、VOL 08负责requirements/capacity、API/schema、state ownership、SLO/deadline/backpressure、failure/degradation/rollback、scaling/cost/safety与项目证据边界；五项目hook仍按public/local/inference/unverified分层。
- 全量生命周期检查额外修复VOL 04 WAM独立复核中一处U+000C导致的`\frac`破损与七个inline MathJax span；重新渲染后12个MathJax容器（5个display）在桌面/窄屏均无可见LaTeX source，技术结论与verdict不变。
- 仓库同步为334/334 triplets、328 WARN + 6 PASS WITH WARNING、269 cards全部unseen。下一bounded slice只冻结`SYS-VLA-002` source contract，不在同一轮生成knowledge/card。

### 当前切片：VOL 08 SYS-VLA-002 Policy Serving / Real-time Control Loop Knowledge（已完成，WARN）

- 重新获取并重哈希OpenPI `15a9616a`的server/serve-entry/policy/client/broker/LIBERO/DROID/LICENSE 8个文件，CPython queue/timeout、Triton batching、gRPC deadline与ROS 2 QoS/real-time fixed docs；14/14 deterministic probes通过。
- 冻结metadata→request→infer→response、client-side chunk cursor/replan、E2E/action-age/deadline公式、bounded admission/compatible batching与soft/hard real-time边界；OpenPI frozen client/server没有显式request ID、deadline、queue/batcher或cancel→physical-stop证明。
- 重哈希3个local OpenPiVLA文件：offline WebSocket action eval有connect/infer alarm，但ALOHA rollout是in-process policy + broker，不是network service；五项目均不升级为production policy service或个人端到端ownership。
- 在 source freeze 基础上新增 knowledge 与原子题卡 canonical/HTML/review：policy serving schema、server/client/controller 状态所有权、chunk/replan、E2E/action-age/deadline、bounded admission、real-time/fail-safe、五项目边界与一张 30 秒/机制展开/诊断题卡；题卡保持 `unseen`。
- 仓库同步为337/337 triplets、331 WARN + 6 PASS WITH WARNING、270 cards全部unseen；没有`coaching_state.md`或PER-019。下一 bounded slice 只做 SYS-VLA-002 真实口述或 request-ID + capture→apply trace artifact，不启动 SYS-VLA-003。

### 当前切片：VOL 08 SYS-VLA-003 Robot Fleet / Multi-tenant GPU Scheduling Knowledge（已完成，WARN）

- 冻结 Kubernetes scheduler/quota/priority/Lease、NVIDIA device plugin、Volcano fair-share/capacity/priority、Triton model/rate limiter、Ray resources/placement/Serve、ROS 2 lifecycle 共 15 个公开 source rows；15/15 deterministic probes 通过。
- 冻结 tenant/robot/model/request/placement identity、capacity vector、queue/fairness/preemption、GPU heterogeneity/cache、robot lease/fencing、replica/canary/cost 与五项目真实性边界；上游机制不被升级为个人 production fleet。
- 在 source freeze 基础上新增 knowledge 与原子题卡 canonical/HTML/review：fleet identity、state ownership、capacity/placement、fairness/preemption、heterogeneous GPU/replica/cache、robot lease/fencing、canary/cost、伪代码、五项目边界与一张 30 秒/机制展开/诊断题卡；题卡保持 `unseen`。
- 仓库同步为340/340 triplets、334 WARN + 6 PASS WITH WARNING、271 cards全部unseen；SYS-VLA-003 三联件已同步，`coaching_state.md`与PER-019均不存在。下一 bounded slice 只做 SYS-VLA-003 真实口述或 tenant/robot/model/request/placement trace artifact，不启动 SYS-VLA-004 或 CODE-VLA-007/008。

### 当前切片：VOL 08 downstream status reconciliation（已完成，WARN）

- 扫描本地 evidence、项目 inventory 与代码路径，没有发现可核验的 `tenant/robot/model/request/placement` fleet trace；不把 OpenPiVLA WebSocket、Robot Harness tool timeout 或其他局部 hook 升级为 fleet scheduler、fairness、lease fencing 或 production ownership 证据。
- 修正 SYS-VLA-002 与 SYS-VLA-003 source-freeze / knowledge review 的旧状态：两者的 knowledge/card 均已独立同步，题卡仍为 `unseen`；同步 sources README、completion audit 与对应 HTML/review SHA。
- 当前全量静态账本保持 `340/340/340` canonical triplets、`271` unique cards、`334 WARN + 6 PASS WITH WARNING`、全部 `unseen`，`coaching_state.md` 不存在。
- 下一 bounded slice 仍只做 `SYS-VLA-003` 真实口述或一份 trace artifact；在真实输入到达前不启动 `SYS-VLA-004`、`CODE-VLA-007/008`，也不修改 mastery。

### 当前切片：VOL 08 CODE-VLA-007 PID Anti-windup Source Freeze（已完成，WARN）

- 冻结 ROS 2 control PID userdoc、WPILib PIDController 文档、Feedback Systems 入口与 VOL 01 advanced-control review；记录响应 SHA、PID `dt`/error/state/trace 接口、输出/积分 clamp、conditional integration、back-calculation、reset 与 8 个 deterministic probes。
- 该切片只新增 `sources/vol_08_code007_pid_anti_windup_source_freeze.md/.html/.review.json`；未生成 CODE-007 knowledge/card，不改变 271 张题卡的 unseen 状态，也未启动 CODE-008 或 SYS-004。
- 仓库同步为 `341/341/341` canonical triplets、`335 WARN + 6 PASS WITH WARNING`、271 张卡全部 unseen；下一 bounded slice 只生成 CODE-VLA-007 knowledge，SYS-VLA-003 真实口述仍保留在独立练习队列。

### 当前切片：VOL 08 CODE-VLA-007 PID Anti-windup Knowledge（已完成，WARN）

- 将冻结的 PID `dt/error/state/trace`、输出/积分 clamp、conditional integration、back-calculation、reset 与 8 probes 转译为 knowledge：公式、逐元素伪代码、first-divergence 诊断、VLA action/normalizer/controller 边界与五项目 truth boundary 均已写入。
- 该切片只新增 `knowledge/vol_08_code007_pid_anti_windup.md/.html/.review.json`；CODE-007 atomic card 仍后置，271 张题卡全部 `unseen`，没有创建 `coaching_state.md`。
- 仓库同步为 `342/342/342` canonical triplets、`336 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 10/10/9`。下一 bounded slice 只生成 CODE-VLA-007 atomic card，不启动 CODE-VLA-008 或 SYS-VLA-004。

### 当前切片：VOL 08 CODE-VLA-007 Atomic Card（已完成，WARN）

- 新增 `questions/vol_08_code007.md/.html/.question_list.md/.review.json`；短答 177 字、机制展开 341 字，覆盖 PID state、saturation、conditional integration、back-calculation、reset、probe 与 VLA truth boundary。
- 题卡保持 `unseen`，没有真实白板/runtime 回答，因此没有创建 `coaching_state.md` 或修改 mastery。
- 仓库同步为 `344/344/344` canonical triplets、`338 WARN + 6 PASS WITH WARNING`、272 张卡全部 unseen；reference-only probe 不计入候选 ownership。下一 bounded slice 做 CODE-007 白板/runtime 练习或补 project artifact，不启动 CODE-VLA-008/SYS-VLA-004。

### 当前切片：VOL 08 CODE-VLA-008 Bellman TD(0) Source Freeze（已完成，WARN）

- 冻结 Sutton–Barto、Gymnasium Handling Time Limits、VOL 01 Batch 2 与 VOL 02 fact review；定义 transition schema、terminal mask、timeout bootstrap、discount、target detach、batch/reduction 与 8 个 deterministic probes。
- 该切片只新增 `sources/vol_08_code008_bellman_td0_source_freeze.md/.html/.review.json`；未生成 CODE-008 knowledge/card，不改变 272 张题卡 unseen 状态，也未启动 SYS-004。
- 仓库同步为 `345/345/345` canonical triplets、`339 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 11/10/10`。下一 bounded slice 只生成 CODE-008 knowledge，不启动 SYS-VLA-004。

### 当前切片：VOL 08 CODE-VLA-008 Bellman TD(0) Knowledge（已完成，WARN）

- 将冻结的 transition schema、terminated/truncated 语义、timeout bootstrap、discount、target detach、batch/reduction 与 8 个 deterministic probes 转译为 knowledge；明确 state-value/Q-learning target、valid denominator、first-divergence 诊断与五项目真实性边界。
- 该切片只新增 `knowledge/vol_08_code008_bellman_td0.md/.html/.review.json`；CODE-008 atomic card 仍后置，272 张题卡全部 `unseen`，没有创建 `coaching_state.md`。
- 当前真实账本为 `346/346/346` canonical triplets、`340 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 11/11/10`。下一 bounded slice 只生成一张 `CODE-VLA-008` atomic card，保持 unseen，不启动 `SYS-VLA-004`。

### 当前切片：VOL 08 CODE-VLA-008 Bellman TD(0) Atomic Card（已完成，WARN）

- 新增 `questions/vol_08_code008.md/.html/.question_list.md/.review.json`；短答180字、机制展开317字，覆盖 terminal/timeout semantics、target detach、valid denominator、shape 对齐、8 probes 与五项目 truth boundary。
- 题卡保持 `unseen`，没有真实白板/runtime 回答，因此没有创建 `coaching_state.md` 或修改 mastery。
- 当前真实账本为 `347/347/347` canonical triplets、`341 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 11/11/11`，全局273张卡全部 unseen。下一 bounded slice 优先只冻结 `SYS-VLA-004` source contract，不在同一轮生成 knowledge/card。

### 当前切片：VOL 08 SYS-VLA-004 Fault Recovery / Safety / Observability Source Freeze（已完成，WARN）

- 新增 `sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.md/.html/.review.json`；冻结 ROS 2 lifecycle/controller/QoS、Kubernetes probes/rollback、OpenTelemetry signals、fault state、first-divergence、safety/replay boundary 与 12/12 probes。
- 本切片只完成 source gate；未生成 SYS-004 knowledge/card，273 张题卡全部 `unseen`，没有创建 `coaching_state.md` 或修改 mastery。SRE monitoring 页面因 TLS 不稳定未纳入 checked source。
- 当前账本为 `348/348/348` canonical triplets、`342 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 12/11/11`。下一 bounded slice 只生成 `SYS-VLA-004` knowledge，不在同一轮生成题卡。

### 当前切片：VOL 08 CODE-VLA-007 Atomic Card（已完成，WARN）

- 新增 `questions/vol_08_code007.md/.html/.question_list.md/.review.json`；短答 177 字、机制展开 341 字，覆盖 PID state、saturation、conditional integration、back-calculation、reset、probe 与 VLA truth boundary。
- 题卡保持 `unseen`，没有真实白板/runtime 回答，因此没有创建 `coaching_state.md` 或修改 mastery。
- 仓库同步为 `343/343/343` canonical triplets、`337 WARN + 6 PASS WITH WARNING`、272 张卡全部 unseen；下一 bounded slice 做 CODE-007 白板/runtime 练习或补 probe artifact，不启动 CODE-VLA-008/SYS-VLA-004。

### 当前切片：VOL 08 SYS-VLA-004 Fault Recovery / Safety / Observability Knowledge（已完成，WARN）

- 在已冻结的 SYS-VLA-004 source contract 上新增 knowledge canonical/HTML/review：fault state、first-divergence、liveness/readiness/startup、QoS/telemetry、safe-apply、lease fencing、rollback/replay 与五项目真实性边界均已写入。
- 本切片只完成 knowledge gate；atomic card 仍后置，273 张题卡全部 `unseen`，没有创建 `coaching_state.md` 或修改 mastery。knowledge review 的 browser visual check 仍需 localhost 桌面/窄屏确认。
- 索引与审计已收口为 `349/349/349` canonical triplets、`343 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 12/12/11`。下一 bounded slice 只生成 `SYS-VLA-004` atomic card，不启动其它 VOL 08 节点。

### 当前切片：VOL 08 SYS-VLA-004 Fault Recovery / Safety / Observability Atomic Card（已完成，WARN）

- 新增 `questions/vol_08_sys004.md/.html/.question_list.md/.review.json`；短答 174 字、机制展开 348 字，覆盖 first divergence、fault state、safe-apply、lease fencing、rollback/replay、observability 与 e-stop 边界。
- 题卡保持 `unseen`，没有真实系统设计回答，因此没有创建 `coaching_state.md` 或修改 mastery；review 保持 `WARN`，browser visual check 已在 localhost 桌面页完成，窄屏规则做静态核验。
- 当前账本为 `350/350/350` canonical triplets、`344 WARN + 6 PASS WITH WARNING`、VOL 08 `sources/knowledge/cards = 12/12/12`，全局 274 张卡全部 unseen。下一 bounded slice 只进行 `SYS-VLA-004` 真实系统设计口述。

### 当前切片：VOL 06 VLA-PER-019 Navigation Evaluation / Failure Source Freeze（已完成，WARN）

- 新增 `sources/vol_06_per019_navigation_evaluation_failure_source_freeze.md/.html/.review.json`；冻结 Habitat `Success`、`DistanceToGoal`、`POINT/VIEW_POINTS` geodesic distance、SPL/SoftSPL、VLN-CE split/episode protocol、denominator、failure taxonomy 与 10/10 deterministic probes。
- 本切片只完成 source gate；PER-019 knowledge/card 后置，PER-020 仍为 registry-only；274 张题卡全部 `unseen`，没有创建 `coaching_state.md` 或修改 mastery。没有 local-direct navigation bundle 时，不把公开指标或项目接口升级为个人导航结果。
- 当前账本为 `351/351/351` canonical triplets、`345 WARN + 6 PASS WITH WARNING`、VOL 06 `sources/knowledge/cards = 19/18/18`，全局 274 张卡全部 unseen。下一 bounded slice 只生成 `VLA-PER-019` knowledge，不在同一轮生成题卡。

### 当前切片：VOL 06 VLA-PER-019 Navigation Evaluation / Failure Knowledge（已完成，WARN）

- 新增 `knowledge/vol_06_per019_navigation_evaluation_failure.md/.html/.review.json`；覆盖 Success/STOP、POINT/VIEW_POINTS、geodesic distance、SPL/SoftSPL、NE/OS/TL namespace、split/denominator、Wilson teaching form、typed manifest、failure taxonomy、fail-closed scorer、10 probes、五项目边界与两档面试回答。
- 本切片只完成 knowledge gate；PER-019 atomic card 后置，274 张题卡全部 `unseen`，没有创建 `coaching_state.md` 或修改 mastery。SoftSPL 的连续 soft-success 明确保留为 scorer-bound teaching abstraction，不写成未核实的本地函数。
- 当前账本为 `352/352/352` canonical triplets、`346 WARN + 6 PASS WITH WARNING`、VOL 06 `sources/knowledge/cards = 19/19/18`，全局 274 张卡全部 unseen。下一 bounded slice 只生成 `VLA-PER-019` atomic card，不启动 PER-020 source gate。

### 当前切片：VOL 06 VLA-PER-019 Navigation Evaluation / Failure Atomic Card（已完成，WARN）

- 新增 `questions/vol_06_per019.md/.html/.review.json` 与 question-list 更新；短答严格 180 字、机制展开 330 字，覆盖 Success/STOP、SPL/SoftSPL、denominator、failure taxonomy、五项目边界与 fail-closed 证据链。
- 题卡保持 `unseen`，没有真实口述，因此没有创建 `coaching_state.md` 或修改 mastery。当前所有 275 张题卡均保持 unseen。
- 当前账本为 `353/353/353` canonical triplets、`347 WARN + 6 PASS WITH WARNING`、VOL 06 `sources/knowledge/cards = 19/19/19`。下一 bounded slice 只冻结 `VLA-PER-020` source，不在同一轮生成其 knowledge/card。

### 当前切片：VOL 06 VLA-PER-020 Robustness / Safety 独立事实复核（已完成，PASS WITH WARNING）

- 新增 `sources/vol_06_per020_robustness_safety_fallback_independent_fact_review.md/.html/.review.json`；重新获取 2 份 primary PDF 与 4 个 fixed official files，6/6 SHA 命中，10/10 bounded source probes 通过，并复核 source→knowledge→card 八个 claim clusters。
- 本切片不新增题卡、不改变 `unseen`、不创建 `coaching_state.md`；Safety Gym cost、randomization、公开 fallback 机制仍不升级为个人项目安全结果。浏览器 connector 不可用，视觉检查保持 `PASS WITH WARNING`。
- 当前账本为 `357/357/357` canonical triplets、`350 WARN + 7 PASS WITH WARNING`、VOL 06 `sources/knowledge/cards = 20/20/20`，全局 276 张题卡全部 unseen。下一 bounded slice 优先进行一题真实 PER-020 口述；若暂不练习，再选择 VOL 04 Audit C/D 独立复核，不启动新卷。

### 当前切片：VOL 07 五项目 Evidence / Ownership Reconciliation（已完成，WARN）

- 新增 `sources/vol_07_project_evidence_reconciliation.md/.html/.review.json`；统一五份 claim inventory、五份 ownership ledger、33 张项目题卡、四层真实性边界、协议/分母合同与高压追问入口。
- 本切片不新增题卡、不改变 `unseen`、不创建 `coaching_state.md`；OpenPiVLA、Harness、OPD、WAM、UWM/LIBERO 的缺失 checkpoint/raw bundle/ownership 仍显式保留。
- 当前账本为 `358/358/358` canonical triplets、`351 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。下一 bounded slice 优先进行一题 WAM 或 OpenPiVLA 真实项目口述，或只审计一个新提供的 P0 immutable bundle。

### 当前切片：首轮真实口述 Drill Queue（已完成，WARN）

- 新增 `practice/oral_drill_queue.md/.html/.review.json`；只定义 12 题的逐题顺序、五维评分卡、回答提交格式和证据边界，不记录候选人回答。
- 不创建 `coaching_state.md`，不改变任何题卡 mastery；队首为 `PROJ-WAM-001`，需要候选人真实回答后才进入反馈流程。
- 当前账本为 `359/359/359` canonical triplets、`352 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。下一步只问队首一题。

### 当前切片：PROJ-WAM-001 口述捕获模板（已完成，WARN）

- 新增 `practice/wam_oral_capture_template.md/.html/.review.json`；预填 manifest、action trace、video、future-image metric 与 checkpoint path bridge 的证据边界，并保留候选人填写区、五维评分区和九项防越界清单。
- 模板没有填写候选人答案、分数或个人 ownership，不创建 `coaching_state.md`，不改变 `PROJ-WAM-001` 的 `unseen` 状态。
- 当前账本为 `360/360/360` canonical triplets、`353 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。下一步仍只收集 `PROJ-WAM-001` 的真实回答。

### 当前切片：PROJ-WAM-001 证据约束示范回答（已完成，WARN）

- 新增 `practice/wam_oral_model_answer.md/.html/.review.json`；提供 30 秒、2 分钟、逐句证据映射和五个高频追问的保守答法。
- 页面明确标注为 model answer，不是候选人 transcript；不填写 personal ownership、分数或 mastery，不创建 `coaching_state.md`。
- 当前账本为 `361/361/361` canonical triplets、`354 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。下一步仍只收集真实 `PROJ-WAM-001` 回答。

### 当前切片：PROJ-OPENPIVLA-001 Formal Trainer 示范回答（已完成，WARN）

- 新增 `practice/openpivla_oral_model_answer.md/.html/.review.json`；覆盖 Qwen3-VL、PEFT LoRA、`model(**batch)`、padding-only label mask、full-chat causal CE 与 FAST/flow/97.4 边界。
- 页面仍是 model answer，不是候选人 transcript；不认领 trainer/collator/recipe ownership，不迁移 `PROJ-OPENPIVLA-001` 状态。
- 当前账本为 `362/362/362` canonical triplets、`355 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。真实口述队首仍为 `PROJ-WAM-001`。

### 当前切片：PROJ-HARNESS-001 Runtime / Data / Reward 示范回答（已完成，WARN）

- 新增 `practice/robot_harness_oral_model_answer.md/.html/.review.json`；覆盖 scope/mutex/cancel/compensation、SFT/GRPO 数据合同、schema-aware reward、proxy safety、run/scorer 边界与 Codex/个人 ownership。
- 页面是 evidence-bounded model answer，不是候选人 transcript；不迁移 `PROJ-HARNESS-001` 状态，不创建 `coaching_state.md`。
- 当前账本为 `363/363/363` canonical triplets、`356 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。真实口述队首仍为 `PROJ-WAM-001`。

### 当前切片：PROJ-OPD-001 数据路由 / 蒸馏 / 评估示范回答（已完成，WARN）

- 新增 `practice/opd_oral_model_answer.md/.html/.review.json`；覆盖五 expert 数据合同、route metadata 与 learned router 的边界、coldstart/online OPD、full-vocabulary KL、point protocol、checkpoint selection、ablation 与 ownership。
- 页面是 evidence-bounded model answer，不是候选人 transcript；不迁移 `PROJ-OPD-001` 状态，不创建 `coaching_state.md`。
- 当前账本为 `364/364/364` canonical triplets、`357 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。真实口述队首仍为 `PROJ-WAM-001`。

### 当前切片：PROJ-UWM-001 Strict / Reset / Paper Protocol 示范回答（已完成，WARN）

- 新增 `practice/uwm_oral_model_answer.md/.html/.review.json`；覆盖 `186/250`、`232/250`、论文约 `0.79` 的 protocol tuple、normalizer/checkpoint/episode 边界、DataLoader stall 诊断与 RoboCasa ownership 防线。
- 页面是 evidence-bounded model answer，不是候选人 transcript；不迁移 `PROJ-UWM-001` 状态，不创建 `coaching_state.md`。
- 当前账本为 `365/365/365` canonical triplets、`358 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。五项目示范回答已覆盖，真实口述仍未开始。

### 当前切片：首轮口述队列 Readiness Audit（已完成，WARN）

- 新增 `practice/oral_drill_readiness_audit.md/.html/.review.json`；核对 12/12 Stable ID、题卡、evidence/knowledge/system 入口，7/12 有项目 model answer，全部 276 张题卡仍 unseen。
- 该审计只证明材料齐备，不代表 drilled；不创建 `coaching_state.md`，不改变 mastery。真实口述队首仍为 `PROJ-WAM-001`。
- 当前账本为 `366/366/366` canonical triplets、`359 WARN + 7 PASS WITH WARNING`、全局 276 张题卡全部 unseen。下一步只收集队首回答。

### 当前切片：ARIS Academic v1 遗留页面统一重渲染（已完成，PASS WITH WARNING）

- 发现并从 canonical Markdown 重新渲染 181 个早期白底/Segoe UI 页面；没有修改 Markdown 技术内容、review SHA 或题卡状态。
- 全仓 388 个 HTML 现在统一具备 academic palette、serif typography、260px sticky TOC、约 900px responsive rule、MathJax 3、Highlight.js、contained overflow 与单 H1；浏览器 connector 仍不可用，因此视觉截图保持 warning。
- canonical 账本保持 `366/366/366`、`359 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen；下一步回到真实 `PROJ-WAM-001` 口述。

### 当前切片：可重复静态验证器（已完成，PASS）

- 新增 `interview_materials/vla/tools/validate_academic_repo.py`，固化三联件、SHA、单 H1、MathJax、公式 `<em>`、本地链接、ARIS CSS、题卡 ID/unseen 和 `coaching_state.md` 检查。
- 运行结果：`canonical_markdown=366`、所有 failure counters 为 `0`、`cards=276`、`unique_ids=276`、`unseen=276`、`status=PASS`。
- 该工具只读，不改变内容或训练状态；下一步仍需真实 `PROJ-WAM-001` transcript。

### 当前切片：五项目 P0 Artifact Intake Contract（已完成，WARN）

- 新增 `interview_materials/vla/evidence/p0_artifact_intake_contract.md/.html/.review.json`，统一 checkpoint、parent lineage、code/config/data/scorer SHA、protocol tuple、raw output、denominator、invalid policy、first divergence 与 ownership 的最低 intake schema。
- 逐项目映射 OpenPiVLA、Robot Harness、OPD、WAM、UWM/LIBERO 的当前 `PARTIAL/WARN` 状态和最小下一件 P0 artifact；没有提升任何结果、ownership 或题卡 mastery。
- 静态验证后账本为 `367/367/367` canonical triplets、`276` 张唯一题卡、`276 unseen`、`coaching_state.md` 不存在、validator `PASS`。下一 bounded slice 只收集一份 WAM P0 bundle 或 `PROJ-WAM-001` 真实口述，两者择一。

### 当前切片：五项目 Ownership Confirmation Queue（已完成，WARN）

- 新增 `practice/ownership_confirmation_queue.md/.html/.review.json`，将五份 ownership ledger 的确认入口整理为 40 个稳定 queue slot：WAM、OpenPiVLA、Robot Harness、OPD、UWM/LIBERO 各 8 题。
- 每题要求角色词汇、文件/函数 locator、过程证据、运行/验收证据和协作边界；队列只定义问题和状态，未填写候选人答案，不创建 `coaching_state.md`，不改变 276 张通用题卡的 `unseen`。
- 同步 Completion Audit、VLA README 与 index；当前账本为 `368/368/368` canonical triplets、`361 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。下一 bounded slice 只问 `OWN-WAM-001` 或 `PROJ-WAM-001`，一次一题。

### 当前切片：WAM CoffeePressButton P0 Bundle Audit（已完成，WARN）

- 新增 `evidence/projects/wm019_wam_p0_bundle_audit.md/.html/.review.json`；只读审计已有 base/trained manifest、300×7 action trace、失败视频、paired MAE/RMSE 与 future-image proxy。
- 审计确认 bundle 为 `PARTIAL`：protocol、raw trace 和结构完整性可复核，但 checkpoint binary/hash、完整 scorer/denominator、run lineage、operator/reviewer 与候选人 ownership 未闭合；没有把任何 uplift、benchmark success 或个人原创升级为强 claim。
- 同步 evidence README、Completion Audit、VLA README 与 index；当前账本为 `369/369/369` canonical triplets、`362 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。下一 bounded slice 只收集 `OWN-WAM-001` 或 `PROJ-WAM-001` 真实回答。

### 当前切片：OpenPiVLA P0 Bundle Audit（已完成，WARN）

- 新增 `evidence/projects/openpivla_p0_bundle_audit.md/.html/.review.json`；审计 Qwen3-VL + LoRA trainer、recipe/config、JSON/CE、`H=15,D=72` 与 `limit=16` shape conflict、official rollout lineage、checkpoint、raw benchmark、parser/controller 和 ownership gates。
- 当前只允许讲 trainer/data/loss/recipe/interface 证据；97.4、优于 official 96.85、FAST-equivalent、formal Qwen 闭环和个人 end-to-end ownership 均保持禁用。
- 同步 Evidence Manifest、Completion Audit、VLA README 与 index；当前账本为 `370/370/370` canonical triplets、`363 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。下一 bounded slice 仍只收集 `OWN-WAM-001` 或 `PROJ-WAM-001` 真实回答。

### 当前切片：Robot Harness P0 Bundle Audit（已完成，WARN）

- 新增 `evidence/projects/robot_harness_p0_bundle_audit.md/.html/.review.json`；审计 runtime/data/reward、十套件 aggregate arithmetic、28/40 primary raw、6/10 exact support、scorer、checkpoint、effect-sink 与 ownership gates。
- 当前允许讲约束建模、数据/reward 设计和协议层评估；不允许讲真实机器人成功率、严格 37.8→95.6 uplift 或全部代码的个人独立 ownership。
- 同步 Evidence Manifest、Completion Audit、VLA README 与 index；当前账本为 `371/371/371` canonical triplets、`364 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。下一 bounded slice 仍只收集 `OWN-WAM-001` 或 `PROJ-WAM-001` 真实回答。

### 当前切片：OPD / VLM Grounding P0 Bundle Audit（已完成，WARN）

- 新增 `evidence/projects/opd_p0_bundle_audit.md/.html/.review.json`；审计五 expert data route、coldstart/student rollout、10k holdout leakage、checkpoint by-format/by-pool、scorer/protocol、lineage、raw predictions、ablation 与 ownership gates。
- 当前允许讲组合路线与 protocol-bounded table；不允许讲 OPD 单因果 uplift、checkpoint/result ownership 或静态 holdout 的机器人成功率。
- 同步 Evidence Manifest、Completion Audit、VLA README 与 index；当前账本为 `372/372/372` canonical triplets、`365 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。下一 bounded slice 仍只收集 `OWN-WAM-001` 或 `PROJ-WAM-001` 真实回答。

### 当前切片：UWM / LIBERO P0 Bundle Audit（已完成，WARN）

- 新增 `evidence/projects/uwm_libero_p0_bundle_audit.md/.html/.review.json`；审计 fixed-pruned-init、reset-style、UWM Table II comparability、DataLoader-only smoke、user-confirmed remote summary、RoboCasa debugging 和 ownership gates。
- 当前允许讲 protocol engineering、DataLoader wait diagnosis 和 failure taxonomy；不允许讲 local 0.744 reproduction、Table II 严格复现、RoboCasa benchmark success 或 UWM architecture 个人原创。
- 同步 Evidence Manifest、Completion Audit、VLA README 与 index；当前账本为 `373/373/373` canonical triplets、`366 WARN + 7 PASS WITH WARNING`、276 张题卡全部 unseen。五项目 P0 audit 已全部建立，下一 bounded slice 只收集 `OWN-WAM-001` 或 `PROJ-WAM-001` 真实回答。

### 当前切片：UWM RoboCasa ActionHeadFix 证据搜寻与账本 reconciliation（已完成，WARN）

- 全量检查 `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro`、`uwm_robocasa_transfer` 与 `report\uwm_libero_strict_eval_recovery_20260702`：本地发现的是 `libero_90.pt` base checkpoint、脚本/报告和 user-confirmed strict JSON；没有发现 0.744 对应的本地 trained checkpoint、250 条 LIBERO episode JSONL、fresh-load bundle 或 RoboCasa produced `models.pt` binary/video/scorer revision。
- 因此不提升任何 LIBERO/RoboCasa 结果等级，也不创建新题卡或 `coaching_state.md`。`186/250` 继续标为 `user-confirmed-remote-final`；RoboCasa 30-epoch 8×54 继续标为 `remote-snapshot-raw / checkpoint-unverified`。
- 已同步路线图的当前计数：`381/381` canonical triplets、`374 WARN + 7 PASS WITH WARNING`、280 张题卡全部 `unseen`、项目卡 37 张；下一 bounded slice 优先收集一题真实口述，或审计用户新提供的 immutable checkpoint bundle。

### 当前切片：VOL 03 Flow Matching / π0 Time–Sign 独立事实复核收口（已完成，PASS WITH WARNING）

- Theorem 2 的 positivity assumption / parameter-independent constant、OT `sigma_min` endpoint、π0 与 OpenPI 的 time/velocity/dt 换元、shifted-Beta coordinate identity 和十步 deterministic endpoint oracle 均已直接核对；公共事实复核从 `WARN` 规范化为 `PASS WITH WARNING`。
- 本切片没有新增题卡、没有改变 `unseen`、没有创建 `coaching_state.md`；local OpenPiVLA class/checkpoint/mask/controller/ownership 与真实口述仍保持 `WARN/PENDING`，不能把 upstream convention 写成个人项目事实。
- 已同步 Completion Audit、VLA README 与 review SHA；当前账本为 `381/381` canonical triplets、`373 WARN + 8 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先继续 Audit B 的 π0/π0.5/FAST/OpenPI 风险，或进行一题真实口述。

### 当前切片：VOL 03 Audit C ACT 公共事实与视觉门禁收口（已完成，PASS WITH WARNING）

- 本轮没有新增知识节点、题卡或 mastery 状态；仅将 ACT paper/frozen-code/synthetic-probe 事实链与 localhost 视觉门禁收口。ACT claim-to-code 与独立复核页面均确认一处 H1、MathJax/公式安全、academic palette、桌面 sticky TOC、窄屏 static TOC 与无页面级横向溢出。
- 公共事实 verdict 为 `PASS WITH WARNING`；local OpenPiVLA action schema、checkpoint、controller、runtime、ownership 与口述仍为 `WARN/PENDING`，44 张 VOL 03 题卡继续 `unseen`，不把 ACT 上游合同迁移为个人项目事实。
- 当前账本保持 `381/381` canonical triplets、`372 WARN + 9 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先进行一题 ACT/Diffusion 真实口述，或收集一个本地 OpenPiVLA immutable runtime artifact。

### 当前切片：VOL 03 Audit A OpenVLA 公共事实与视觉门禁收口（已完成，PASS WITH WARNING）

- 本轮没有新增知识节点、题卡或 mastery 状态；仅将 OpenVLA paper/frozen-code/endpoint-probe 事实链与 localhost 视觉门禁收口。256 bins、256 encoder IDs、255 decoder centers、top-two alias 以及 CE/metric mask 差异均保留原实现边界。
- public facts verdict 为 `PASS WITH WARNING`；local OpenPiVLA tokenizer/checkpoint/stats/controller、97.4% lineage、ownership 与口述仍为 `WARN/PENDING`，不能把 OpenVLA scalar token contract 当作个人项目事实。
- 当前账本保持 `381/381` canonical triplets、`371 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先进行一题真实口述，或审计一个本地 OpenPiVLA immutable artifact。

### 当前切片：VOL 03 Audit A OpenVLA 公共事实与视觉门禁收口（已完成，PASS WITH WARNING）

- 本轮没有新增知识节点、题卡或 mastery 状态；仅将 OpenVLA paper/frozen-code/endpoint-probe 事实链与 localhost 视觉门禁收口。256 bins、256 encoder IDs、255 decoder centers、top-two alias 以及 CE/metric mask 差异均保留原实现边界。
- public facts verdict 为 `PASS WITH WARNING`；local OpenPiVLA tokenizer/checkpoint/stats/controller、97.4% lineage、ownership 与口述仍为 `WARN/PENDING`，不能把 OpenVLA scalar token contract 当作个人项目事实。
- 当前账本保持 `381/381` canonical triplets、`372 WARN + 9 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先进行一题真实口述，或审计一个本地 OpenPiVLA immutable artifact。

### 当前切片：VOL 03 Audit E Flow Matching / π0 claim-to-code 状态收口（已完成，PASS WITH WARNING）

- 本轮没有新增知识节点、题卡或 mastery 状态；仅同步 claim-to-code 与独立 time/sign review 的边界。Theorem 2、`sigma_min`、time/velocity/dt、shifted Beta 与 deterministic oracle 保持 `PASS WITH WARNING`；arXiv source tar truncated 仍明确标记，不能声称 TeX source 已成功解包。
- Flow claim-to-code 页面整体继续 `WARN/PENDING`，原因是 local OpenPiVLA runtime/mask/controller/ownership/oral gate 未闭合；localhost 桌面/窄屏视觉 QA 已通过。
- 当前账本保持 `381/381` canonical triplets、`371 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先进行一题 Flow/Diffusion 真实口述，或审计一个本地 OpenPiVLA immutable artifact。

### 当前切片：VOL 03 Audit B π0 / π0.5 / FAST / OpenPI claim-to-code 视觉状态收口（已完成，WARN）

- 本轮没有新增知识节点、题卡或 mastery 状态；public π0.5 hybrid、FAST、OpenPI shape/norm/padding/rollout facts 仍由独立复核页标为 `PASS WITH WARNING`。
- claim-to-code 页面整体仍为 `WARN/PENDING`，因为本地 checkpoint、tokenizer revision、axis/unit、H/K、controller、eval bundle、ownership 和口述未闭合；localhost 桌面/窄屏视觉 QA 已通过。
- 当前账本保持 `381/381` canonical triplets、`371 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先进行一题 π0/FAST/Flow 真实口述，或收集本地 OpenPiVLA immutable artifact。

### Audit B 渲染器溢出修复复核（已完成，PASS）

- 发现 Audit B 页面此前仍由旧模板生成，桌面 `1440×1000` 的表格宽度越过主列并把 `documentElement.scrollWidth` 推到 `1628px`；未直接手改 HTML，而是使用当前 academic renderer 重新生成 canonical 对应页面。
- 重新渲染后，桌面视口 `pageOverflow=false`、表格均限制在 `908px` 主列且 TOC 为 `sticky`；窄屏 `800×1000` 视口 `pageOverflow=false`、TOC 为 `static`，7 张表格均在页面内可用。
- 全仓静态审计重新通过：`381` 个 canonical triplets、`sha_mismatch=0`、`h1=0`、`formula_em=0`、`local_links=0`、academic template checks 全为 `0`；账本仍为 `371 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`，未创建 coaching state 或改变 mastery。
- 下一 bounded slice：进行一题真实 π0/FAST/Flow 口述，或收集一个本地 OpenPiVLA immutable runtime artifact；继续保持 claim-to-code 的 local runtime/ownership/口述门为 `WARN/PENDING`。

### 当前切片：OpenPiVLA Runtime Rollout Artifact Gate（已完成，WARN）

- 已从 `C:\Users\mousongzhe\project\openpivla_deployment` 冻结部署记录与三个 immutable summary：ALOHA `pi0_aloha_sim` 基础 rollout 为 `2/3`，六相机 true-physics rollout 为 `1/2`，LIBERO `pi05_libero` spatial task 0 的 70-step model/no-op 对照为 `0/1`。
- 新增 source artifact gate，明确区分“官方 checkpoint 的 runtime / task-native simulator / 视频轨迹落档”与“私有 fine-tune、checkpoint lineage、ownership、benchmark、97.4% 归属”。LIBERO 失败结果保留为失败诊断证据，不包装成成功率。
- canonical/HTML/review 与 sources README、VLA README、Completion Audit 已同步；当前账本为 `382/382` canonical triplets、`372 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 优先补一份 checkpoint manifest + server/client launch log，或做一次固定 observation/action/axis/unit/normalizer/controller/scorer 的 matched LIBERO probe。题卡仍不新增 mastery，当前 `unseen` 状态不变。

### 当前切片：将 Runtime Rollout 证据回写至 PROJ-OPENPIVLA-007（已完成，WARN）

- 复用现有题卡，不新增 stable ID：短答与机制展开已回写 ALOHA `2/3`、六相机 `1/2`、LIBERO task-0 `0/1` 的精确边界，并加入 Runtime Rollout Artifact Gate 作为来源 `[20]`。
- 题卡仍明确区分 official deployment/runtime、formal Qwen training、replay-only/action-adapter 诊断和个人 ownership；没有把 rollout 结果升级为 97.4% 或个人 fine-tune 成绩。
- canonical question HTML/review SHA 已同步；所有 8 张 OpenPiVLA Batch 1 卡仍为 `unseen`。后续 load-lineage 证据另由下一条切片映射到同一题卡。

### 当前切片：OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate（已完成，WARN）

- 冻结 `serve.log`、`client.log`、`run_libero_true_rollout.py` 与 `DEPLOYMENT.md` 的 SHA；server log 直接确认 Orbax 0.11.13 从 `pi05_libero/params` 恢复约 6.2 GiB、17 秒完成、加载 checkpoint 内 norm stats、监听 8399 并接受 localhost client。
- hashed rollout script 固定 observation image/wrist/state/prompt、eef+axis-angle+gripper state、action chunk 前 `replan_steps×7D` 的 contract；但本次精确 argv、shared run UUID、server-side request/response trace 与独立 scorer 仍缺，task-0 结果继续保留为 `0 reward / false success`。
- 该切片关闭的是官方 checkpoint 的 load/serve/client 主要疑问，不是 immutable binary manifest，更不是私有 Qwen3-VL LoRA fine-tune lineage、97.4% 归属或个人 ownership。账本同步为 `383/383` canonical triplets、`373 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。
- 下一 bounded slice：把 load-lineage 证据回写一张现有 OpenPiVLA 题卡，或补 checkpoint/norm-stats 逐文件 SHA + exact argv/shared run identity；另一个独立选项是 matched LIBERO failure probe。

### 当前切片：将 LIBERO Load–Serve–Client Lineage 证据回写至 PROJ-OPENPIVLA-007（已完成，WARN）

- 不新增 stable ID、不改变 mastery：PROJ-OPENPIVLA-007 已加入 Orbax restore、checkpoint norm stats、8399 listen、localhost connect 与 hashed rollout contract 的安全口径，来源新增 `[21]`。
- 30 秒回答 `169` 字、机制展开 `339` 字，均通过既有长度门；题卡仍显式保留 checkpoint binary SHA、exact argv/run UUID、独立 scorer、private formal Qwen lineage 与 ownership 缺口。
- `proj_openpivla.md/.html/.review.json`、题库 README、VLA README、Completion Audit 与路线图已同步；下一 bounded slice 只补 immutable manifest / matched LIBERO probe，或收集真实口述，不迁移 `unseen`。

### 当前切片：OpenPiVLA ALOHA Action-Level Eval Load Gate（已完成，WARN）

- 冻结 ALOHA LeRobot action-eval `serve.log`、`summary.json`、evaluator 与 launcher SHA；server log 直接确认 `pi0_aloha_sim` restore 约 6.0 GiB/17.31 s、checkpoint norm stats、8020 listen 与 localhost connection。
- summary 记录 4 个 episode-0 采样点、每个 horizon 50、action dim 14，mean L1 `0.0330713950`、std `0.0205169544`；该结果严格标为 offline action-vector/harness diagnostic，不是 task success 或 fine-tune benchmark。
- 新 source gate 与 `PROJ-OPENPIVLA-007` 来源 `[22]`、README、Completion Audit 已同步；账本为 `384/384` canonical triplets、`374 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice 只做 immutable official-checkpoint manifest、matched LIBERO failure probe 或真实口述。
- 本轮收口时已完成 localhost 浏览器 QA：ALOHA source gate 在 `800×1000` 窄屏保持零页面级溢出、TOC 转为 `static`、table/code/formula 均内部滚动；`PROJ-OPENPIVLA` 题卡在桌面 `sticky` / 窄屏 `static` 两种布局均为 8/8 折叠卡、单 H1、零坏锚点。`review.json` 已从 `PENDING` 回写为实际结果。

### 当前切片：OpenPiVLA Official Checkpoint Immutable Manifest Gate（已完成，WARN）

- 对 `C:\Users\mousongzhe\Project\openpivla_deployment` 的 deployment/code 4 个文件、ALOHA action-eval bundle 13 个文件、LIBERO rollout bundle 9 个文件逐文件重算 bytes 与 SHA-256；本地 manifest 共 26 个文件，均可直接复核。
- 重新确认 `pi0_aloha_sim` 与 `pi05_libero` 的 `params`、checkpoint norm-stats 仅存在于部署记录的远端 `/data/msz/...` 路径，当前 Windows 工作区没有这些目录；因此 binary/norm-stats manifest 继续为 `UNVERIFIED`，不把历史 GiB/file-count 摘要升级为 immutable checkpoint SHA。
- 已新增 `sources/openpivla_official_checkpoint_immutable_manifest_gate.md/.html/.review.json`，同步 sources README、VLA README 与 Completion Audit；账本为 `385/385` canonical triplets、`375 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice：尝试原远端只读 checkpoint manifest；若不可达，则做 matched LIBERO failure probe 或收集一题真实口述。

### 当前切片：OpenPiVLA / LIBERO Matched Failure Probe Readiness Gate（已完成，WARN）

- 对 `libero_franka_true_rollout_v1/summary.json` 做了 9/9 项本地一致性 preflight：`status=ok`、`libero_spatial/task-0/episode-0`、model/no-op 两条 70-step run、reward/success 边界、finite scalar、success-rate 重算与所有结果文件引用均通过。
- 从 `run_libero_true_rollout.py` 冻结了 image flip/resize、eef quaternion→axis-angle、gripper state、action chunk 前 7D、replan queue 与 `done` 聚合 contract；但 effective argv、逐步 raw observation/action、server response、独立 scorer 与 fresh A/B rerun 均未落档，因此本页是 readiness gate，不是 root-cause 结论。
- 已新增 `sources/openpivla_libero_matched_failure_probe_readiness_gate.md/.html/.review.json`，同步 sources README、VLA README 与 Completion Audit；账本为 `386/386` canonical triplets、`376 WARN + 10 PASS WITH WARNING`、280 张题卡全部 `unseen`。下一 bounded slice：原远端生成 trace-complete matched probe；若不可达，补 trace-export patch 或收集一题真实口述。

### 当前切片：VOL 01 Foundations VLA-FND-022 分层回答试点收口（已完成，WARN）

- `VLA-FND-022` 已补齐 30 秒回答与约 2 分钟机制展开：value / Q / advantage 定义、TD error、GAE、baseline 降方差、terminated 与 time-limit truncation，以及 WAM value/world auxiliary head 不等同控制动作的项目边界。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `462FC80CFA2DEFB77AB7FDB7399D79D6DA76E0F2AC3099024EB043136867B498`，题卡仍 `unseen`。本卷分层试点覆盖 `VLA-FND-001..004、006、010..013、016、021、022`，其余卡片保留 legacy 答案格式并延后。
- 全仓 validator 通过：`387/387` canonical triplets、`sha_mismatch=0`、`h1=0`、`formula_em=0`、`local_links=0`、ARIS academic template 全部通过；题卡 `280/280` unique 且全部 `unseen`，`coaching_state.md` 不存在。localhost 视觉 QA 通过：桌面 TOC `sticky`，`800×1000` 窄屏 TOC `static`，页面级横向溢出为 0，公式无 `<em>` 污染。
- 该切片不改变任何 mastery，也不把示范回答当作候选人回答。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 的一份真实口述；若继续知识试点，再处理 `VLA-FND-023`，但不与真实训练并行批量推进。

### 当前切片：VOL 01 Foundations VLA-FND-023 分层回答试点收口（已完成，WARN）

- `VLA-FND-023` 已补齐 30 秒回答与约 2 分钟机制展开：Bellman expectation / optimality operator、state/action value 两组递推、固定策略评估与 greedy improvement、连续动作 actor 近似，以及函数逼近和数据覆盖边界。
- 题卡明确保留项目真实性边界：BC、diffusion、flow-matching VLA 若没有 Bellman backup 训练合同，不能称为在求最优 Q；WAM value proxy 与 LIBERO success 统计也不是 Bellman optimum 的解或证明。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `04DD76134BCA984BB81DF1AA7E377B831954C3E01058DFBC5BEB1F2F939330C2`，分层试点现覆盖 13 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 继续通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure，`coaching_state.md` 不存在。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述；若继续知识试点，再处理 `VLA-FND-024`。

### 当前切片：VOL 01 Foundations VLA-FND-024 分层回答试点收口（已完成，WARN）

- `VLA-FND-024` 已补齐 30 秒回答与约 2 分钟机制展开：on-policy / off-policy 的行为策略与目标策略、importance ratio、support 与 bias–variance、Q-learning 的 off-policy target，以及 offline RL 的更强数据约束。
- 题卡明确保留 Robot Harness 边界：本地是固定 candidate group 上的 reward-shaped weighted token CE，不能称 canonical online GRPO，也不能仅凭历史数据复用就升级为标准 off-policy RL。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `DA7BA1B59C9A3B1A998DFC11CEFFFCC5EF29C769CEF9CE1BA6D0B3C20D189678`，分层试点现覆盖 14 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure，`coaching_state.md` 不存在。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述；若继续知识试点，再处理 `VLA-FND-025`。

### 当前切片：VOL 01 Foundations VLA-FND-025 分层回答试点收口（已完成，WARN）

- `VLA-FND-025` 已补齐 30 秒回答与约 2 分钟机制展开：policy-gradient estimator、state-only baseline 的零期望项、advantage、TD error、GAE，以及 baseline 质量、termination 与 mask 对估计的影响。
- 题卡明确保留项目真实性边界：GRPO 的组内相对信号只可解释为 baseline-like signal，不能直接等同机器人 value head；Robot Harness 的 reward-shaped weighted token CE 不能据此改称 canonical online GRPO。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `6C1CD8916DACF85A65143D5FC73B10371F6A85103CB155DA7700FD04F51443B7`，分层试点现覆盖 15 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure，`coaching_state.md` 不存在。桌面 `1280×1000` 与窄屏 `800×1000` 浏览器 QA 均通过；下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述，若继续知识试点则处理 `VLA-FND-026`。

### 当前切片：VOL 01 Foundations VLA-FND-026 分层回答试点收口（已完成，WARN）

- `VLA-FND-026` 已补齐 30 秒回答与约 2 分钟机制展开：old/new policy ratio、PPO-Clip 的 `min` 方向、advantage 符号、近似 trust region、rollout freshness，以及 value/entropy/termination 辅助约束。
- 题卡明确保留项目真实性边界：clipping 不是 action 截断，也不是严格 KL 约束；Robot Harness 的固定 candidate group、reward-shaped weighted token CE 与 PPO 的 rollout/ratio/clipped objective 不同，不能混称 canonical online GRPO 或 PPO。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `EAB4C1E692B176B0717BC4275BCE7E3469B5C2ACB86457826115D7F828BBF6FA`，分层试点现覆盖 16 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure；桌面 `1280×1000` 与窄屏 `800×1000` 浏览器 QA 均通过。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述，若继续知识试点则处理 `VLA-FND-027`。

### 当前切片：VOL 01 Foundations VLA-FND-027 分层回答试点收口（已完成，WARN）

- `VLA-FND-027` 已补齐 30 秒回答与约 2 分钟机制展开：reward、discounted return、Monte Carlo/TD/n-step value target、terminal/truncated bootstrap，以及 episode-level success predicate 和 success-rate denominator。
- 题卡明确保留跨项目协议边界：WAM 的 value/world auxiliary、RoboCasa 的训练/控制 reward 与 LIBERO 的 success predicate 必须分别记录 input、target、mask、reduction 和环境评估协议，任一 proxy 都不能直接写成任务成功率。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `534E52888F00FB7FD77C9A574C55A315A5B7E4E31A61EA6347F40075006738B1`，分层试点现覆盖 17 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure；桌面 `1280×1000` 与窄屏 `800×1000` 浏览器 QA 均通过。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述，若继续知识试点则处理 `VLA-FND-028`。

### 当前切片：VOL 01 Foundations VLA-FND-028 分层回答试点收口（已完成，WARN）

- `VLA-FND-028` 已补齐 30 秒回答与约 2 分钟机制展开：behavior/deployment state distribution、compounding error、offline critic extrapolation、dataset support、recovery/intervention、behavior constraint 与 conservative Q。
- 题卡明确保留项目真实性边界：UWM/LIBERO 的接触精度与长时序 recovery coverage 目前只是候选诊断假设；升级为根因仍需 raw episode trace、matched intervention、同初始化/seed 对照和可复算失败分层。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `BC759FA1C9D366D50183448D1E8A1F93766A965C6E7C5434B29EFF37AABDC40B`，分层试点现覆盖 18 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure；桌面 `1280×1000` 与窄屏 `800×1000` 浏览器 QA 均通过。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述，若继续知识试点则处理 `VLA-FND-029`。

### 当前切片：VOL 01 Foundations VLA-FND-029 分层回答试点收口（已完成，WARN）

- `VLA-FND-029` 已补齐 30 秒回答与约 2 分钟机制展开：masked action MSE denominator、normalization/维度权重、teacher-forced 与 closed-loop gap、denormalization/chunk/controller、接触失败与 success predicate、matched rollout 协议。
- 题卡明确保留 WAM 证据边界：离线 MSE 只能支持 proxy 或 root-cause 候选；历史改善比例在缺少同 checkpoint、同脚本和原始 artifact 时不能升级为成功率提升。
- 已同步 `questions/vol_01_foundations.md/.html/.review.json`；canonical SHA 为 `B358EF99638E2AE266ADB46BC55CFF6165EDEE4EA7ECD2D7722FF3B0658A88D2`，分层试点现覆盖 19 张卡，39 张题卡仍全部 `unseen`。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure；桌面 `1280×1000` 与窄屏 `800×1000` 浏览器 QA 均通过。下一 bounded slice 回到 `PROJ-WAM-001` 真实口述；若继续知识试点，从后续未分层题卡中选择。

### 当前切片：WAM 候选人项目范围自述 Intake（已完成，WARN）

- 将候选人在本线程明确给出的五项范围自述登记到 `evidence/projects/wam_ownership_ledger.md`：Cosmos Policy 1-epoch fine-tune、Cosmos eval、UWM/LIBERO fine-tune+eval、UWM/RoboCasa 尝试、协议对齐与训练评估。
- 这五行只标为 `candidate-self-report / role-pending`，用于确定面试准备范围和 artifact 搜索优先级；不升级为 `role-confirmed`、`result-owned`，不新增指标或 checkpoint claim。
- 已同步 `wam_ownership_ledger.md/.html/.review.json`；canonical SHA 为 `931A7FAE9C6D224EAC292D63EEFFDFA374504318F8181E6F610F15D25F7C0D07`。浏览器 QA：桌面 `1280×1000` sticky TOC、窄屏 `800×1000` static TOC，页面级溢出为 0。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述；收到后再按 ownership ledger 八问进行反馈，不创建 coaching state 之前不迁移 mastery。

### 当前切片：UWM / LIBERO 候选人项目范围自述 Intake（已完成，WARN）

- 将候选人在本线程明确给出的三项 UWM 范围自述登记到 `evidence/projects/uwm_libero_ownership_ledger.md`：UWM/LIBERO fine-tune、UWM/LIBERO eval、UWM/RoboCasa 尝试及协议/训练评估对齐。
- 三行均保持 `candidate-self-report / role-confirmation-pending`；不把 strict/reset/Table II 结果合并，不把 RoboCasa 诊断升级为 root cause、完整成功率或 checkpoint/env/scorer ownership。
- 已同步 `uwm_libero_ownership_ledger.md/.html/.review.json`；canonical SHA 为 `8BB8E60A91111D1A15E4101A49A4E31D42750EFCC92F5BA154DFAF98D4789E2F`。浏览器 QA：桌面 `1280×1000` sticky TOC、窄屏 `800×1000` static TOC，页面级溢出为 0。
- 全仓 validator 通过：`387/387` canonical triplets、280 张唯一题卡、SHA/单 H1/公式/链接/ARIS template 全部无 failure。下一 bounded slice 仍优先收集 `PROJ-WAM-001` 真实口述；UWM 继续保持 `WARN` 与题卡 `unseen`。

## 14. 变更纪律

- 当前工作区已有未提交修改；后续不覆盖或回滚这些改动。
- 每轮开始先检查 `git status` 和本路线图状态。
- 未经用户要求，不创建分支、不提交、不推送。
- 新来源、新指标或新项目材料先进入 Evidence Manifest，再进入简历或强回答。
- 路线图允许重排：如果出现目标 JD、临近面试或关键新证据，优先级可以调整，但必须记录原因。
