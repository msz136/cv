# 缪宋哲简历重构与优化方案

## 1. 当前简历诊断

原 PDF 是一页传统中文简历，版式干净，但最大问题是高价值经历没有被展开：

- 商汤实习只写了 4 条概括，未体现 Agent 工程、工具调用后训练、schema-aware eval、SFT/GRPO 训练规模和评估闭环。
- `OPD` 与 Qwen3-VL semantic-nav 是实习支线，但原简历完全没有利用到数据构造、8 卡训练、held-out eval 和 raw-holdout 结果。
- `Project` 里的 VLA/WM/WAM 是开源复现与小改造，应作为补充项目，不宜和商汤实习主线同权重。
- 医学图像分割项目缺少 Dice 数值、baseline、消融表和个人贡献边界，暂时只能保留为弱项目。
- 技能区过于泛，建议按 `后训练 / Agent / VLM-VLA / 工程 / 数学` 重组，而不是只列“LLM/VLM/VLA 相关技术栈”。

## 2. 推荐定位

主叙事：

> 数学背景 + 具身智能/Agent 算法实习，能把工具调用、模型后训练、机器人/VLM 评估和工程部署串成闭环。

最适合投递方向：

- 大模型算法实习：Agent、Tool Use、Post-Training、Alignment、RLHF/RLAIF/GRPO。
- Embodied AI / VLA / VLM 算法实习：grounding、semantic navigation、robot policy eval。
- AI infra / LLM application algorithm：OpenAI-compatible serving、tool schema、eval harness、model deployment。

不建议当前主打：

- 纯医学图像算法岗位：证据最弱，缺少可追问指标。
- 纯机器人控制策略岗位：Project 里有复现和评估，但实习主线更强的是 Agent/post-training/eval，不是从零做 policy learning。

## 3. 经历权重排序

| 优先级 | 内容 | 简历处理 |
| --- | --- | --- |
| P0 | 商汤 `agent` 主线 | 放在实习第一段，写成 4 条核心 bullet，覆盖 Agent 工程、SFT/GRPO、schema-aware eval、模型部署。 |
| P1 | 商汤支线 `OPD / muxi` | 放在商汤实习下的支线项目，写 2-3 条，突出数据构造、8 卡训练、held-out/raw-holdout 指标。 |
| P2 | 广州皓岚 DeepSeek SFT/DPO | 保留一条，补数据规模、base model、eval benchmark 后可增强。 |
| P3 | `Project` VLA/WM/WAM 复现 | 放到“开源复现与小改造”，强调部署、评估协议、边界意识，避免写成主实习成果。 |
| P4 | 医学图像分割 | 暂保留一条；补充 Dice 后再决定是否展开。 |

## 4. 可直接使用的重写结构

推荐一页结构：

1. 顶部定位：`大模型算法 / Agent / Embodied AI 实习方向`
2. 教育背景：中山大学 + 上海交通大学推免，保留 GPA 和数学高分课程
3. 专业技能：后训练、Agent、VLM/VLA、工程、数学与英语
4. 实习经历：
   - 商汤科技 | 具身算法实习
   - 商汤支线 | Qwen3-VL semantic-nav / OPD
   - 广州皓岚 | 大模型应用
5. 项目经历：
   - VLA/WM/WAM 开源复现与小改造
   - 医学图像分割

我已按这个结构生成 HTML 草稿：

`C:\Users\mousongzhe\cv\output\mousongzhe_resume_optimized.html`

## 5. 证据审计

### 商汤 Agent 主线

证据强度：强。

可写事实：

- AceAgent 服务支持 OpenAI-compatible `/v1/chat/completions`、`/v1/chat`、工具调用、流式响应、robot prompt、tool_names 筛选、取消补偿、Redis 可恢复流等。
- 训练流水线完成 62,223 条 SFT 数据和 8,916 条 GRPO 数据组织。
- 8 卡环境完成 500-step SFT 与 1007-step online GRPO，报告中记录无 NaN/OOM/traceback/non-finite loss。
- schema-aware native tools eval 中 project robot sandbox 130 条样本达到 tool/arg/scope 100%，SFT tool-call holdout tool accuracy 约 95%+。

谨慎边界：

- 不要写“上线生产”或“主导整个系统”，除非能提供内部上线、负责人边界和用户流量证据。
- 不要写“自主智能体完全自动完成复杂任务”，应写“工具调用、参数约束、沙箱评估和执行边界”。

### OPD / Qwen3-VL 支线

证据强度：强。

可写事实：

- 语义导航 box-grounding 数据：13,879 high-quality base boxes，41,637 high-quality train rows。
- Qwen3-VL-8B semantic-nav SFT：41,637 行，有效 batch size 256，163 optimizer steps，train loss 0.777。
- Held-out object_ref：SFT expert strict format 100%，Mean IoU 0.3501；base lenient Mean IoU 0.1319。
- Raw-holdout 10k：OPD final Box Acc@0.5 51.3%，Point Hit@100 84.1%，Text loose 87.4%，Bool acc 90.0%。

谨慎边界：

- `region_ref` transfer 仍弱，不要写“全面解决 semantic navigation”。
- OPD 是实习支线，建议作为支线项目而不是压过 Agent 主线。

### VLA / WM / WAM 开源复现

证据强度：中。

可写事实：

- OpenPiVLA / OpenPI 部署有正式 remote deployment log，包含官方 checkpoint、MuJoCo rollout、LIBERO/robosuite 路径和 action eval。
- ALOHA official checkpoint smoke 有 2/3 success；LIBERO first smoke success 为 0，需要如实表述为 simulator path 验证。
- UWM/LIBERO 有 strict fixed-init 评估脚本和部分 50-rollout/task 结果，但最终 5-task strict average 未确认。
- Cosmos/WAM 有训练和 eval 记录，但部分正式 eval 结果较弱，不适合作为“效果提升”主卖点。

推荐写法：

> 复现并小改造 VLA/WM/WAM 开源项目，完成远端环境部署、评估协议整理、rollout/eval 脚本适配和可视化报告；区分真实 simulator rollout、replay-only 可视化和 action-vector 诊断，避免将 smoke/proxy 结果误写成正式 benchmark。

### 广州皓岚 DeepSeek 蒸馏

证据强度：中。

当前可写：

- 数据准备、SFT、DPO、评估、数学推理场景。

需要补证据：

- 数据量、base/distilled model 名称、benchmark 名称、前后准确率或 pass@k、DPO 偏好对来源。

### 医学图像分割

证据强度：弱到中。

当前可写：

- Transformer/attention 模块、UNet/AUNet、Kvasir/Polygen、Dice、消融。

需要补证据：

- baseline Dice、改进后 Dice、是否有统计均值、训练配置、代码仓库或实验表。

## 6. 可替换进简历的核心 Bullet

### 商汤 Agent 主线

- 参与机器人 Agent 对话与工具调用链路建设，支持 OpenAI-compatible tools、SSE 流式响应、robot scope 绑定、工具筛选和取消补偿，沉淀可评估的 tool schema 与执行边界。
- 参与 Qwen3-VL 工具调用后训练流水线，组织 62,223 条 SFT 数据与 8,916 条 GRPO 数据，在 8 卡环境完成 500-step SFT 与 1007-step online GRPO，训练日志未出现 NaN/OOM/traceback。
- 基于 AceAgent 原生工具 schema 设计 schema-aware reward 与 native tools eval；project robot sandbox 130 条样本达到 tool/arg/scope 100%，SFT tool-call holdout tool accuracy 约 95%+。

### OPD 支线

- 构建 semantic-nav box-grounding 数据链路，将 RoboPoint object_ref 样本转为 box manifest，并结合 Qwen-122B crop 标注扩展为 41,637 条高质量训练样本。
- 在 MACA C500 8 卡上完成 Qwen3-VL-8B semantic-nav SFT，held-out object_ref 上 strict format 达到 100%，Mean IoU 从 base lenient 0.1319 提升到 0.3501。
- 参与 OPD 多教师融合评估，构建 10k raw-holdout 审计；OPD final 在综合评估中达到 Box Acc@0.5 51.3%、Point Hit@100 84.1%、Text loose 87.4%。

### 开源复现项目

- 复现 OpenPiVLA、UWM/LIBERO、Cosmos Policy/WAM 等开源机器人学习项目，完成远端部署、脚本适配、评估协议整理和可视化报告。
- 搭建 LIBERO/MuJoCo rollout 与 action-eval 记录链路，明确区分正式 simulator rollout、replay-only 可视化和 proxy action-vector 诊断，保证实验结论可追溯且不过度外推。

## 7. 面试前必须补齐的问题

1. 商汤 `agent/teamagent` 中你本人负责的模块边界是什么？是数据、训练、eval、服务接口、工具 schema，还是全链路联调？
2. BERT 输入过滤模型的数据来源、正负样本规模、指标和上线/试用状态是什么？
3. MiniMax-M2.5、Qwen3.5-122B、AceBrain 部署与推理优化里，你具体做了哪些优化？吞吐、延迟、显存、并发有没有数字？
4. DeepSeek 蒸馏项目的数学推理评估集、baseline 和提升幅度是多少？DPO 偏好对怎么构造？
5. 医学分割项目的 Dice baseline 和提升后结果是多少？是否有代码、实验表或报告？

## 8. 下一步建议

- 若要投具体 JD：先贴 JD，再按 `Agent / Post-Training / Embodied AI` 三类岗位分别定制版本。
- 若要形成长期简历库：把商汤 Agent、OPD、广州皓岚、开源复现分别整理成 `timeline` 条目，后续可以自动按 JD 组合。
- 若要生成最终 PDF：在确认上述 5 个问题后，基于 HTML 草稿做一轮压缩和打印检查，再导出一页 PDF。
