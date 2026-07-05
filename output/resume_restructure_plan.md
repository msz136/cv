# 缪宋哲简历重构与优化方案

## 1. 本轮改写结论

本轮重构简历时去掉顶部自我定位摘要，把商汤经历合并为一个主体实习，突出面向平台级机器人集群控制的 task harness、schema-aware SFT/GRPO、语义导航 grounding 与 OPD 指标；项目经历拆成 VLA、WAM、UWM 三个独立项目，不再把 VLM/WAM/UWM 压缩为一个小项目。

当前同时维护两个取向：

- 工程版本：强调平台侧机器人集群控制、执行语义、训练评估闭环与可复现实验，适合偏工程落地、算法工程、具身平台方向。
- Research 版本：强调算法设计、数据设计、训练目标、benchmark protocol 与 failure diagnosis，适合具身智能算法、VLA/VLM grounding、robot learning research 实习方向。

改写后的 HTML 简历在：

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_optimized.html`

命名版本在：

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_engineering.html`

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_research.html`

核心变化：

- 商汤实习从低价值过程表述转为“robot task harness、训练目标、reward 设计、可验证指标”。
- OPD 支线并入商汤实习，作为 VLM grounding 与多任务融合成果呈现。
- 删除未形成有效产出的经历，给具身方向项目留出篇幅。
- VLA 项目保留 OpenPI/OpenPiVLA 的策略训练与评估设计；本地暂未检索到 LIBERO 超官方 baseline 的落档指标，HTML 正文先留空，不放低价值 smoke 指标。
- WAM 项目强调 1-epoch 后训练复现、action/world/value 多目标训练合同、loss breakdown 与可视化诊断。
- UWM 项目改为训练与评估全流程复现：LIBERO-90 checkpoint 到 5 个 LIBERO-10 下游任务 finetune，配套 checkpoint / normalizer / eval manifest，并使用最新 strict aligned 5-task 指标。
- Research 版本将 task harness 改写为“机器人任务表示与训练监督设计”，将 WAM/UWM 改写为“训练目标复现、数据/loss routing、benchmark 口径对齐”，减少平台执行与工程流程措辞。

## 2. 推荐定位

工程版本主叙事：

> 数学背景 + 商汤具身算法实习 + VLA/WAM/UWM 机器人学习复现，具备从任务表示、训练目标、reward/eval 到指标复盘的闭环能力。

Research 版本主叙事：

> 数学背景 + 具身学习训练/评估实践，重点在机器人任务表示、VLM grounding 数据构造、schema-aware reward、WAM/UWM 训练目标复现与 benchmark protocol 对齐。

适合投递：

- 具身智能算法实习：VLA、VLM grounding、semantic navigation、robot policy eval。
- 多模态算法实习：Qwen3-VL、box/point grounding、held-out eval、bad case 分析。
- 大模型训练与评估实习：SFT、GRPO、schema-aware reward、native tools eval。
- Research / 算法实习：robot learning、VLA/VLM grounding、world model policy、post-training objective、data-centric evaluation。

不建议当前主打：

- 纯后端或平台岗位：会稀释具身/VLA 叙事。
- 纯医学图像岗位：原医学分割项目证据弱，且与当前最强经历不一致。
- 强硬件机器人控制岗位：目前证据更强的是策略评估、grounding 与复现实验，不是自研控制器。

## 3. 经历重排

| 优先级 | 内容 | 简历处理 |
| --- | --- | --- |
| P0 | 商汤 `agent` 主体 | 写成具身算法实习，强调面向机器人集群控制的 task harness、memory/subagent/并行控制、schema-aware SFT/GRPO 与 robot sandbox 指标。 |
| P0 | 商汤 `muxi/OPD` | 并入同一段商汤实习，作为语义导航 grounding 与 OPD 多任务融合成果呈现。 |
| P1 | `Project/openpivla_deployment` | 单独写成 VLA 项目，突出 OpenPI/OpenPiVLA 策略训练、动作语义和 LIBERO/ALOHA 评估口径；LIBERO 超 baseline 指标待落档后补。 |
| P1 | `Project/reproduction_plan.md` Cosmos Policy | 单独写成 WAM 项目，突出 1 epoch 后训练复现、loss/data contract、future prediction 诊断。 |
| P1 | `Project/wm/uwm_libero_official_repro` + `Project/report/uwm_libero_strict_eval_recovery_20260702` | 单独写成 UWM 项目，突出 LIBERO-90 到 LIBERO-10 的训练复现、fixed-init 评估协议和最新 5-task strict aligned 结果。 |
| P2 | 广州皓岚 DeepSeek | 保留一条，作为早期大模型训练经历，不加入未经证实的数值。 |
| P3 | 医学图像分割 | 本轮移出简历，给具身方向项目留空间。 |

## 3.1 双版本口径差异

| 模块 | 工程版本 | Research 版本 |
| --- | --- | --- |
| 商汤 task harness | 平台侧机器人集群控制、memory/subagent/并行调度、排他动作控制 | 机器人任务表示、action/tool 语义、schema 对齐监督、reward 设计 |
| 商汤 grounding / OPD | 语义导航 grounding 与 OPD 多任务融合结果 | box-grounding 数据筛选、held-out split、Mean IoU 与 raw-holdout 多任务指标 |
| VLA | 策略训练与评估路径、controller/simulator contract | observation/state 归一化、action chunk、动作语义与 rollout 可比性 |
| WAM | 1 epoch 后训练复现、loss/data contract、future prediction 诊断 | action/world/value 三目标、mask / slot loss routing、误差来源分析 |
| UWM | 多卡训练、checkpoint / normalizer / eval manifest、fixed-init eval | checkpoint 继承、动作归一化、benchmark protocol、strict 5-task 指标 |

## 4. 证据审计

### 商汤机器人任务执行与工具使用训练

可以写：

- 平台级机器人集群控制 task harness：任务上下文、机器人状态 memory、subagent 分工、排他动作控制与取消补偿。
- 任务并行只作为 harness 的其中一项能力：支持多机器人任务与非物理任务并发，避免在简历中喧宾夺主。
- SFT 数据 62,223 条，GRPO 数据 8,916 条。
- Qwen3-VL-8B 完成 500-step SFT 与 1007-step online GRPO。
- SFT tool-call holdout：tool accuracy 95.3%，critical 94.7%，coverage 96.4%。
- Project robot sandbox：130 条样本 tool/arg/scope 均为 100%。
- 对比集证据：base 8B 在 robot sandbox tool accuracy 为 0%，post SFT/GRPO 为 100%。

谨慎边界：

- 不写未经证实的生产状态或整体负责人表述。
- 不把 tool-use 训练写成纯 Agent 岗位主叙事，简历中放在机器人任务表示、训练目标和执行边界下。
- safety side-effect 覆盖不足属于后续优化点，不作为简历正文成果。

### 商汤 VLM Grounding 与 OPD

可以写：

- 13,879 个 high-quality base boxes。
- 41,637 条 high-quality train rows。
- Qwen3-VL-8B semantic-nav SFT：163 optimizer steps，train loss 0.777。
- held-out strict format：100%，Mean IoU 从 0.1319 提升到 0.3501。
- OPD final raw-holdout 10k：Box Acc@0.5 51.3%，Point Hit@100 84.1%，Text loose 87.4%，Bool acc 90.0%。

谨慎边界：

- 简历不出现数据集内部来源名，只写“语义导航 grounding 数据”。
- OPD final 不是所有单项最佳，简历用“OPD final 在 10k raw-holdout 达到...”的事实表述。

### VLA 项目：OpenPiVLA / OpenPI

可以写：

- OpenPI/OpenPiVLA 策略训练与评估路径。
- LIBERO/ALOHA observation/state 归一化、action chunk、controller 与 simulator contract。
- MuJoCo / robosuite 7D action contract、action norm/delta/jerk、state divergence、reward/success、轨迹视频。
- LIBERO 超官方 baseline 指标待用户落档后补入。

谨慎边界：

- 暂不把本地已检索到的 LIBERO smoke 指标写入简历正文。
- 暂不把 ALOHA 2/3 作为主成果，以免稀释用户希望强调的 LIBERO VLA 成绩。

### WAM 项目：Cosmos Policy / Predict2.5 1 Epoch

可以写：

- 复现 RoboCasa WAM 1-epoch 后训练。
- 保持 `p_world_model=0.5`、`gamma=0.99`、`action_loss_multiplier=16` 等关键设定。
- WAM 数据合同覆盖 video、action、value、world/value mask、slot index。
- full10k checkpoint 保存成功，iter 10000 loss = 0.0543。
- full10k loss breakdown：demo=4950、world=2519、value=2531。
- rollout / future prediction 可视化用于诊断 action loss、world model sample mask 与 value head 的误差来源。

谨慎边界：

- 策略成功率不足不作为简历正文成果。
- 1-episode smoke、future prediction 视频、PSNR/SSIM 不能代表整体 policy success。

### UWM 项目

可以写：

- 复现 UWM 官方 LIBERO 训练到评估全流程：从 LIBERO-90 checkpoint 初始化，到 5 个 LIBERO-10 下游任务 finetune，再到 fixed-init closed-loop rollout。
- 训练侧证据包括 8 卡 Muxi DDP finetune wrapper、任务列表、checkpoint、batch / steps 配置、checkpoint / normalizer / eval manifest 和 run-specific 输出。
- LIBERO fixed-init 评估协议：`pruned_init`、5-step zero-action warmup、50 rollouts/task、8 shards、600 rollout length。
- 最新 strict aligned 5-task result：186/250 = 74.4%，其中 `libero_book_caddy` 44/50，`libero_soup_cheese` 40/50，`libero_bowl_drawer` 38/50，`libero_moka_moka` 33/50，`libero_mug_mug` 31/50。
- 与官方 Table II rounded average 0.79 口径接近，差距约 4.6 个百分点；简历正文采用“接近官方 Table II 0.79 口径”的保守表达。

谨慎边界：

- 不使用早期宽松评估口径做正式 benchmark 对比。
- RoboCasa 低成功率诊断不作为 UWM 项目的简历成果；UWM 正文聚焦 LIBERO full-flow 训练复现与最新 strict aligned 指标。

## 5. 最终简历结构

1. 顶部信息：姓名、联系方式、2026 届本科 / 硕士推免身份
2. 教育背景：中山大学数学本科 + 上海交通大学数学硕士推免
3. 专业技能：具身方向、策略评估、模型训练、VLM/WAM、工程工具、英语
4. 实习经历：
   - 商汤科技 | 具身算法实习
   - 广州皓岚信息技术有限公司 | 大模型应用实习
5. 项目经历：
   - OpenPiVLA / OpenPI VLA 机器人策略评估
   - Cosmos Policy / WAM 后训练 1 epoch 复现
   - UWM / LIBERO 世界模型策略训练与评估复现

## 6. 面试表达建议

最稳的讲法：

- 商汤实习：从“平台如何表示、分解、记忆和调度机器人控制任务”切入，再讲并行控制与训练评估。
- VLA 项目：强调动作语义、仿真器、controller、success/reward/video 证据，LIBERO 指标补档后再做强表达。
- WAM 项目：强调 action/world/value 三类训练信号、loss mask、1 epoch 复现和 future rollout 诊断。
- UWM 项目：强调训练复现、fixed-init 评估协议、5-task strict aligned 指标和与官方口径的可比性。

最高风险追问：

- “你本人负责的边界是什么？”答法应围绕数据、训练目标、reward/eval、报告与失败归因，不抢全部 owner。
- “为什么 Cosmos Policy 没写策略性能提升？”答法应说明这是 WAM 后训练复现与诊断项目，主要产出是训练合同、loss 归因和可复现 checkpoint。
- “OPD 是否解决 semantic-nav？”答法应说明 held-out Mean IoU 有明确提升，OPD raw-holdout 多任务指标达到可报告水平，但仍需继续做 hard/boundary 数据。
