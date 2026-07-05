# 缪宋哲简历重构与优化方案

## 1. 本轮结论

本轮不再维护工程取向版本，`mousongzhe_resume_engineering.html` 仅保留为历史文件，不继续同步。统一维护目标改为：

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_optimized.html`

`optimized` 已对齐 research-forward 口径，并进一步强化算法设计、数据设计、训练目标、评估协议和指标解释。正文重点放在可以被面试追问的设计判断与结果证据上。

## 2. 叙事定位

当前主线：

> 数学背景 + 商汤具身算法实习 + VLA/WAM/UWM 开源复现与改造。重点展示机器人任务表示、VLM grounding 数据分布、schema-aware SFT/GRPO、OPD 多教师融合、VLA 动作表示、WAM/UWM 训练目标与评估协议。

适合投递：

- 具身智能算法实习：VLA、VLM grounding、semantic navigation、robot policy eval。
- 多模态算法实习：Qwen3-VL、box/point grounding、held-out eval、bad case 分析。
- 大模型训练与评估实习：SFT、GRPO、schema-aware reward、native tools eval。
- Research / 算法实习：robot learning、world model policy、data-centric evaluation。

不建议当前主打：

- 纯后端或平台岗位：会稀释具身/VLA 叙事。
- 纯硬件控制岗位：当前证据更强的是策略训练、评估协议、grounding 与复现实验。

## 3. 经历取舍

| 优先级 | 内容 | 简历处理 |
| --- | --- | --- |
| P0 | 商汤 `agent` 主体 | 写成面向机器人集群控制的 task harness 与训练监督设计，包含 memory、subagent、排他动作、取消补偿、多机器人并发边界。 |
| P0 | 商汤 `muxi/OPD` | 并入同一段商汤实习，作为语义导航 grounding、数据分布设计和 OPD online multi-teacher 融合训练成果。 |
| P1 | `Project/openpivla_deployment` | 单独写成 VLA 大项目，突出 Qwen3-VL 接入、assistant 侧离散动作 token、三类训练策略、LIBERO 指标与 MACA/C500 跨算力迁移。 |
| P1 | Cosmos Policy / Predict2.5 | 单独写成 WAM 项目，突出 action/world/value 多目标训练、样本路由与损失权重、RoboCasa eval 复现和失败类型分析。 |
| P1 | UWM / LIBERO | 单独写成 UWM 项目，突出 LIBERO-90 到 LIBERO-10 finetune、fixed-init 封闭循环评估与最新 strict 5-task 结果。 |
| P2 | 广州皓岚 DeepSeek | 保留一条，作为早期大模型训练经历，不加入无证据数值。 |
| P3 | 医学图像分割等弱相关经历 | 移出本版，给具身方向留篇幅。 |

## 4. 关键证据边界

### 商汤机器人任务与 native tools 训练

可以写：

- 机器人集群控制 task harness：统一 task/action 表示，多会话任务上下文、robot memory、subagent 分工、排他动作、取消补偿、多机器人并发边界。
- 数据规模：62,223 条 SFT，8,916 条 GRPO。
- 8B 只作为数据分布和 reward 规则的可行性验证，不作为主成果；主线迁移到 Qwen3-VL-32B SFT/GRPO。
- 32B 是主结果：SFT/GRPO 后 holdout tool accuracy 由 base 的 37.8% 提升至 95.4%/95.6%，coverage 稳定在 96% 左右。
- 严格 held-out 130 条样本中，工具选择、robot scope 与关键动作约束达到 100%，GRPO argument exact 92.3%、semantic 96.9%。

谨慎边界：

- 不把 base 8B 与训练后模型做不公平协议对比。
- 不写未经证实的生产状态或整体负责人表述。
- 不把任务并行写成主成果，它只是 harness 的一个 feature。

### 商汤 VLM Grounding 与 OPD

可以写：

- 数据由开源清洗样本与场景标注/合成样本共同组成，先初始化 box grounding 能力，再扩充长尾语义/空间分布，统一成 OPD 训练分布。
- 13,879 个 high-quality base boxes，41,637 条训练样本。
- held-out Mean IoU 从 0.1319 提升到 0.3501。
- OPD final 10k raw-holdout：Box Acc@0.5 51.3%、Point Hit@100 84.1%、Text loose 87.4%、Bool acc 90.0%。
- 相比 Qwen3-VL-8B-Instruct，Box +8.0pp，Text +35.4pp，Bool +8.8pp；简历正文保留正向提升项，不展开降点或无增益项。

谨慎边界：

- OPD final 不是所有单项最佳，表达为综合均衡结果。
- 数据内部来源名不进入简历正文。
- SFT 是冷启动与格式对齐证据，OPD 才是主成果。

### OpenPiVLA / OpenPI VLA

可以写：

- 官方 OpenPI 上改造 Qwen3-VL-2B + LoRA 训练复现。
- 连续 action window 到 assistant 侧离散动作 token 的动作表示设计。
- `RunRecipe`、DROID/MindCube iterable dataset、`Qwen3VLCollator`、统一 trainer/checkpoint。
- 三类训练策略：VLA-only、VLM-only、co-train。
- LIBERO 四套件结果：goal/object/spatial/libero_10 = 0.99/0.995/0.98/0.93，四套件平均 97.4%，高于官方 OpenPI `pi05_libero` 96.85%。
- 在沐曦 C500/MACA 环境迁移三条 100k-step formal runs，并保留官方 policy server 与 task-native rollout 评估证据。

谨慎边界：

- 不声称等价复刻原全参 Pi0/Qwen-VL action expert。
- 不把内部 run 名或内部消融指标写入正式简历；分辨率、horizon、pretrain 的影响只作为面试分析思路。
- ALOHA 与单任务 LIBERO 小样本只作为评估协议与动作诊断证据，不当作核心 benchmark。
- 标题避免把项目降格为“训练复现”，正文以动作表示改造、多模态协同训练和公开指标为主线。

### Cosmos Policy / WAM

可以写：

- RoboCasa WAM 1-epoch 后训练目标复现。
- action/world/value 三类监督信号、world/value mask、demo/world/value slot routing。
- action/world/value 三类监督信号、world/value mask、demo/world/value slot routing，用于隔离动作学习与世界/价值预测信号。
- held-out proxy 上 policy MSE 0.05349，较 first-action-repeat baseline 0.09718 降低约 45%，这是正文主要指标。
- RoboCasa kitchen24：短时序开关门任务成功率 0.90-0.95，抓取/放置代表任务 0.75，用于失败类型分析。

谨慎边界：

- 不把低样本或非严格评估写成策略性能提升。
- 正文定位为 WAM 训练目标复现、动作头诊断和失败类型分析。
- loss 绝对值、样本计数和超参数罗列留在面试材料，不进入一页简历正文。

### UWM / LIBERO

可以写：

- 在 MACA/C500 环境迁移 UWM 官方训练到评估流程。
- 从 LIBERO-90 checkpoint 到 5 个 LIBERO-10 下游任务 finetune。
- strict benchmark：pruned_init、5-step zero-action warmup、50 rollouts/task。
- 最新 5-task average：74.4% (186/250)，任务间成功率分布 0.62-0.88。
- 当前结果低于官方 Table II rounded average 0.79，简历正文不强调负向对比，改为说明 strict 协议与失败轨迹归因。

谨慎边界：

- 不使用宽松 reset-style 结果做正式对比。
- 强调 fixed-init 评估协议与结果可比性。

## 5. 最终结构

1. 顶部信息：姓名、联系方式、2026 届本科 / 硕士推免身份。
2. 教育背景：中山大学数学本科 + 上海交通大学数学硕士推免。
3. 专业技能：具身学习、算法设计、数据设计、训练评估、模型栈、英语。
4. 实习经历：商汤科技具身算法实习、广州皓岚大模型应用实习。
5. 项目经历：OpenPiVLA、Cosmos/WAM、UWM，三者纵向排列。

## 6. 面试表达建议

- 商汤实习：从“机器人平台需要怎样表示和约束可执行任务”切入，再讲 harness 如何把平台控制约束转成 schema-aware 数据与 reward。
- OPD：先讲数据分布设计，再讲多教师在线融合，最后用 raw-holdout 指标解释综合能力。
- OpenPiVLA：先抛 LIBERO 0.99/0.995/0.98/0.93 与官方 OpenPI 结果对比，再展开 assistant 侧动作 token 与训练目标改造。
- WAM：讲清 action/world/value 三目标、离线 MSE 正向对比与失败类型分析，不把项目包装成策略成功率提升。
- UWM：突出严格 fixed-init 协议和与官方 Table II 的可比性，主动解释 soup_cheese 夹取精度与长时序恢复是主要差距。
