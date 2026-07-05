# 缪宋哲简历重构与优化方案

## 1. 本轮改写结论

本轮按“具身智能 / VLA-VLM Grounding / 机器人策略评估”重新组织简历，不再把 VLM/WM/WAM 压缩为一个小项目，也不把 OPD 单独分成商汤科技之外的一段经历。

改写后的 HTML 简历在：

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_optimized.html`

核心变化：

- 商汤实习合并为一个主体经历，覆盖机器人任务执行、工具使用训练、schema-aware reward/eval、semantic navigation grounding、OPD 多专家融合评估。
- 删除未形成可验证产出的输入过滤工作。
- 项目经历拆成三个独立项目：`OpenPiVLA / OpenPI` 表述为 VLA 项目；`Cosmos Policy / Predict2.5 1 epoch` 表述为 WAM 项目；`UWM / LIBERO` 单独表述为 UWM 项目。
- 工作内容从“工程串接”改为“任务表示、训练目标、评估协议、指标口径、失败归因和报告产出”。
- 指标只使用本地报告中能追溯的数字，避免把 smoke、proxy 或 partial eval 写成正式性能收益。

## 2. 推荐定位

主叙事：

> 数学背景 + 商汤具身算法实习 + VLA/WAM/UWM 机器人学习复现，具备从任务数据、训练目标、评估协议到失败归因的闭环能力。

适合投递：

- 具身智能算法实习：VLA、VLM grounding、semantic navigation、robot policy eval。
- 多模态算法实习：Qwen3-VL、box/point grounding、held-out eval、bad case 分析。
- 大模型训练与评估实习：SFT、GRPO、schema-aware reward、native tools eval。

不建议当前主打：

- 纯后端或平台岗位：会稀释具身/VLA 叙事。
- 纯医学图像岗位：原医学分割项目证据弱，且与当前最强经历不一致。
- 强硬件机器人控制岗位：目前证据更强的是策略评估、grounding 与复现实验，不是自研控制器。

## 3. 经历重排

| 优先级 | 内容 | 简历处理 |
| --- | --- | --- |
| P0 | 商汤 `agent` 主体 | 写成具身算法实习，强调机器人任务执行、工具使用行为建模、SFT/GRPO 与 native tools eval。 |
| P0 | 商汤 `muxi/OPD` | 并入同一段商汤实习，作为 VLM grounding 与多专家融合评估成果呈现。 |
| P1 | `Project/openpivla_deployment` | 单独写成 VLA 项目，突出 OpenPI/OpenPiVLA 策略评估、ALOHA 真实仿真结果和 LIBERO 失败边界。 |
| P1 | `Project/reproduction_plan.md` Cosmos Policy | 单独写成 WAM 项目，突出 1 epoch 后训练复现、loss/data contract、RoboCasa 失败分析。 |
| P1 | `Project/report/uwm_libero...` | 单独写成 UWM 项目，突出 LIBERO strict fixed-init 协议、partial results 和 benchmark 口径控制。 |
| P2 | 广州皓岚 DeepSeek | 保留一条，作为早期大模型训练经历，不加入未经证实的数值。 |
| P3 | 医学图像分割 | 本轮移出简历，给具身方向项目留空间。 |

## 4. 证据审计

### 商汤机器人任务执行与工具使用训练

可以写：

- SFT 数据 62,223 条，GRPO 数据 8,916 条。
- 500-step SFT 与 1007-step online GRPO 完成，日志未出现 NaN/OOM/traceback/non-finite loss。
- Project robot sandbox 130 条样本 tool/arg/scope 全为 100%。
- SFT tool-call holdout tool accuracy 95.3%。
- 报告建议进入 constrained shadow eval，而不是直接自动执行；safety side-effect 覆盖不足是后续风险。

谨慎边界：

- 不写未经证实的生产状态或整体负责人表述。
- 不写超出当前评估边界的机器人自主执行结论。
- 不把 tool-use 训练写成纯 Agent 岗位主叙事，简历中将其放在机器人任务执行与评估边界下。

### 商汤 VLM grounding 与 OPD

可以写：

- 13,879 个 high-quality base boxes。
- 41,637 条 high-quality train rows。
- Qwen3-VL-8B semantic-nav SFT：163 optimizer steps，train loss 0.777。
- held-out object_ref：strict format 100%，Mean IoU 0.3501；base lenient Mean IoU 0.1319。
- OPD final raw-holdout 10k：Box Acc@0.5 51.3%，Point Hit@100 84.1%，Text loose 87.4%，Bool acc 90.0%。

谨慎边界：

- semantic-nav box 仍是 OPD 的短板，不能写“解决语义导航”。
- OPD final 不是所有单项最佳，应该写“综合均衡”“形成 checkpoint 选择与数据配比建议”。

### VLA 项目：OpenPiVLA / OpenPI

可以写：

- ALOHA official OpenPI MuJoCo rollout：3 episodes success 2/3 = 0.6667。
- ALOHA multi-view visual rollout：2 episodes success 0.5。
- LIBERO true simulator smoke 已跑通，但 first smoke success 0.0。
- Bridge/Fractal 当前不具备 task-level success/reward result，只能写 renderer/blocker 与 proxy action 诊断。
- 项目价值在于 VLA 评估协议、动作语义、controller、视频证据和 task-level result 边界。

谨慎边界：

- 不把 Bridge/Fractal proxy 写成正式 rollout。
- 不把 LIBERO smoke 写成性能成果。

### WAM 项目：Cosmos Policy / Predict2.5 1 epoch

可以写：

- 10-step、100-step、1k-step 与 full10k 训练均完成，full10k 保存 `iter_000010000` checkpoint。
- WAM 数据合同覆盖 video、action、value、mask、slot index。
- full10k 去重后 demo=4950、world=2519、value=2531；iter 10000 loss=0.0543。
- 24 tasks × 5 episodes RoboCasa 小规模评估全部 exit code 0。
- conservative trusted success = 0/118，应写作失败分析和训练复现，不写作策略性能提升。

谨慎边界：

- 1-episode smoke、future prediction 视频、PSNR/SSIM 不能写成整体 policy success。
- 当前项目的亮点是 WAM 训练合同、loss 诊断、评估失败归因，而不是 benchmark 成绩。

### UWM 项目

可以写：

- strict fixed-init 协议使用 `pruned_init`、5-step zero-action warmup、50 rollouts/task、8 shards、600 rollout length。
- strict partial result：`libero_book_caddy` 34/50 = 0.68，`libero_soup_cheese` 30/50 = 0.60。
- 旧的 UWM reset-style 结果 232/250 = 0.928 只能作为非严格对照。
- 5-task strict average 尚未确认，不能写最终平均。

谨慎边界：

- 不把 UWM reset-style 写成 LIBERO strict benchmark。
- 不报告未完成的 5-task strict average。

## 5. 最终简历结构

1. 顶部定位：具身智能 / VLA-VLM Grounding / 机器人策略评估
2. 教育背景：中山大学数学本科 + 上海交通大学数学硕士推免
3. 专业技能：具身方向、策略评估、模型训练、VLM/WAM、工程工具、英语
4. 实习经历：
   - 商汤科技 | 具身算法实习
   - 广州皓岚信息技术有限公司 | 大模型应用实习
5. 项目经历：
   - OpenPiVLA / OpenPI VLA 机器人策略评估
   - Cosmos Policy / WAM 后训练 1 epoch 复现
   - UWM / LIBERO 世界模型策略评估

## 6. 面试表达建议

最稳的讲法：

- 商汤实习：从“机器人任务怎样被表示、训练和评估”切入，而不是从服务开发切入。
- VLA 项目：强调动作语义、仿真器、controller、success/reward/video 证据，不夸大失败结果。
- WAM 项目：强调 action/world/value 三类训练信号、loss mask、1 epoch 复现和 RoboCasa failure analysis。
- UWM 项目：强调评估协议差异和 benchmark 口径，主动说明 partial results 与 non-strict results 的区别。

最高风险追问：

- “你本人负责的边界是什么？”答法应围绕数据、训练目标、reward/eval、报告与失败归因，不抢全部 owner。
- “为什么 Cosmos Policy 评估结果是 0？”答法应说明这是 WAM 复现与诊断项目，正式结论是训练可跑通但策略成功率不足。
- “UWM 0.928 为什么不能写成正式成绩？”答法应说明 reset-style 与 LIBERO fixed-init 的协议不同，正式比较必须用 strict fixed-init。
- “OPD 是否解决 semantic-nav？”答法应说明 object_ref 有明确提升，但 semantic-nav box 仍是短板，后续应改进数据配比与 hard/boundary 样本。
