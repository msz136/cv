# GitHub Source Scout：面试题库骨架与 VLA 来源入口

> 调研日期：2026-07-16  
> 目标：为本仓库选择可复用的题库骨架和后续技术来源入口。  
> 重要边界：本文件记录“来源选择”，不是技术事实的最终证明；具体方法、指标和项目 claim 仍需回到论文、官方 repo、benchmark 文档或本地 artifact。

## 1. 结论摘要

`WinstonJQ/embodied-interview-qa` 适合作为本仓库的主骨架：它已经验证了“主索引 → 分卷 → Markdown canonical source → 折叠 HTML → review.json”的长期维护方式，并且有 L1/L2/L3、易错点、来源和移动端自测设计。

它不应被当作 VLA 技术事实的唯一来源。后续技术写作需要使用官方仓库、论文、benchmark 文档和本地项目证据；awesome 列表只做检索入口。

## 2. 候选仓库审计

| Source | 用途 | 快照/状态 | 许可与风险 | 决策 |
| --- | --- | --- | --- | --- |
| [WinstonJQ/embodied-interview-qa](https://github.com/WinstonJQ/embodied-interview-qa) | 题库分卷、总索引、折叠题卡、审查记录、发布流程 | commit `fef782564647a5e89e7bed1f60d20b0588c6b3ae`；2026-07-11；GitHub API 2026-07-16 显示约 103 stars、2026-07-15 更新 | MIT；可借鉴结构，不复制答案、频次或个人信息 | **primary skeleton** |
| [BarisYazici/ml_robotics_interview_prep](https://github.com/BarisYazici/ml_robotics_interview_prep) | 机器人学、ML、SLAM、3D geometry、RL 和系统设计的基础路径 | commit `5c586a8603efb8594f0983eadb1b93ddf7c5aab6`；2025-03-26；约 62 个文件 | Apache-2.0；VLA/Flow Matching 较少，部分内容偏旧 | **supporting foundation** |
| [jonyzhang2023/awesome-embodied-vla-va-vln](https://github.com/jonyzhang2023/awesome-embodied-vla-va-vln) | VLA/WAM/VLN/VA 论文、benchmark、simulator 和 survey 发现 | commit `f43f364b6ab03ffaedd5fd5f3d961b1acf2a7e71`；2026-07-07；README 700+ papers 级别 | 当前未发现 LICENSE 文件；不直接复制条目，必须回溯链接 | **discovery only** |
| [DravenALG/awesome-vla-wam](https://github.com/DravenALG/awesome-vla-wam) | VLA、WAM、数据集、benchmark、simulator 分类索引 | commit `f0bb547fb706dccd416085834b1102c93bd051c7`；2026-07-15；约 848 stars | 当前未发现 LICENSE 文件；仅作检索地图 | **discovery only** |
| [Denghaoyuan123/Awesome-RL-VLA](https://github.com/Denghaoyuan123/Awesome-RL-VLA) | Offline / Online / Test-time RL-VLA 分类和论文入口 | commit `d5bd9593ac4defcc14f2e04e331d7ee4923508bc`；2026-05-18；约 791 stars | 当前未发现 LICENSE 文件；survey PDF 与条目需逐项核验 | **discovery only** |

### 2.1 搜索结果的限制

- GitHub 仓库搜索对“VLA 面试题”中文/英文关键词返回很少，不能把星数或搜索排名当作题目频次。
- “awesome”仓库擅长发现论文和项目，不等于答案经过审查；它们的 license 状态也不一致。
- 本仓库的目标是个人面试准备，不按公司标签组织题目，也不把公开面经内容改写成个人经历。

## 3. 采用的骨架规则

从 `WinstonJQ/embodied-interview-qa` 继承：

1. 主索引先于分卷，分卷有明确状态和范围。
2. Markdown 是 canonical source，HTML 是生成视图，review JSON 记录审查。
3. 题卡默认折叠，先自测再看答案。
4. 使用 L1 / L2 / L3 进行认知难度分层。
5. 每题保留“易错”一句，并在进入主库前合并同义题。
6. 每个知识卷开始前先列题目清单，作为本轮可审阅边界。

本仓库额外增加：

1. 深度 Knowledge HTML：公式、张量 shape、伪代码、实现映射和方法比较。
2. Project hook：每道高价值题必须能连接到 OpenPiVLA、WAM、UWM、OPD 或 Harness，且不越过证据边界。
3. Evidence Manifest：记录 claim、artifact、协议、个人贡献和风险。
4. 训练状态：题库生成后仍是 `unseen`，只有实际口述训练后才能升级。

## 4. 到八卷的来源映射

| 卷 | 主要来源类型 | 第一批官方/原始资料方向 | 个人项目挂钩 |
| --- | --- | --- | --- |
| VOL 01 Foundations | 机器人基础、ML/RL 教材、官方文档 | 线性代数、Transformer、MDP、坐标与控制 | OpenPiVLA / UWM |
| VOL 02 IL / RL / Post-training | 论文、算法官方实现、RL-VLA survey | BC、DAgger、PPO、GRPO、SFT/DPO、offline/online RL | Harness / WAM |
| VOL 03 VLA / Action | VLA 论文与官方 repo | OpenVLA、π 系列、ACT、Diffusion Policy、Flow Matching、FAST | OpenPiVLA |
| VOL 04 World Model / Sim2Real | world model 论文、官方 benchmark、simulator docs | dynamics、value、planning、domain randomization、sim2real | WAM / UWM |
| VOL 05 Engineering / Evaluation | 官方训练框架、benchmark protocol、部署文档 | data pipeline、distributed training、policy server、closed-loop eval | 全部项目 |
| VOL 06 Perception / Grounding / Nav | VLM/grounding 论文、导航 benchmark | point/box/text、3D perception、VLN/ObjectNav、多视角 | OPD / Harness |
| VOL 07 Project Deep Dives | 本地代码、config、log、eval、resume | 五项目 claim reconciliation 和追问树 | 五个现有项目页 |
| VOL 08 Coding / System Design | 官方 API/源码、经典题、系统设计参考 | attention、loss、normalization、VLA train/eval service | 训练/评估工程 |

## 5. 下一批核验清单

这些是下一轮要逐个核验的原始技术来源入口，不在本文件中提前断言其最新内容：

- OpenVLA / OpenVLA-OFT 官方仓库与论文。
- Physical Intelligence `openpi` 与 π 系列公开资料。
- Diffusion Policy、ACT、Flow Matching / FAST 的论文与官方实现。
- Open X-Embodiment、DROID、LIBERO、RoboCasa 的官方数据/benchmark 文档。
- NVIDIA Cosmos Policy / UWM 相关公开仓库或技术报告。
- Qwen3-VL 官方模型卡和训练/推理文档。
- FSDP / DeepSpeed、PyTorch、JAX/Flax 官方文档。

本轮已完成 GitHub 可达性、默认分支和 HEAD 的第一轮冻结；方法、数据和 benchmark claim 仍需逐页阅读官方 README/论文后才能进入强答案。

| Official source | HEAD at 2026-07-16 | branch | license observed | planned use |
| --- | --- | --- | --- | --- |
| [openvla/openvla](https://github.com/openvla/openvla) | `c8f03f48af692657d3060c19588038c7220e9af9` | `main` | MIT | VOL 03：OpenVLA 架构、action token、OFT |
| [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | `15a9616a00943ada6c20a0f158e3adb39df2ccac` | `main` | Apache-2.0（GitHub search metadata） | VOL 03/05：π 系列、训练与推理 contract |
| [real-stanford/diffusion_policy](https://github.com/real-stanford/diffusion_policy) | `5ba07ac6661db573af695b419a7947ecb704690f` | `main` | MIT | VOL 03：Diffusion Policy action head |
| [tonyzhaozh/act](https://github.com/tonyzhaozh/act) | `742c753c0d4a5d87076c8f69e5628c79a8cc5488` | `main` | MIT | VOL 03：ACT / action chunking |
| [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment) | `9eeb68b989efbcf474e8fb9019e01d02b962a604` | `main` | Apache-2.0 | VOL 02/05：数据集与跨 embodiment |
| [Lifelong-Robot-Learning/LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) | `8f1084e3132a39270c3a13ebe37270a43ece2a01` | `master` | MIT | VOL 05：任务、评估和 fixed-init 协议 |
| [robocasa/robocasa](https://github.com/robocasa/robocasa) | `b4684e6ee37d377cc392e98302a6b916d588b415` | `main` | NOASSERTION（需查看仓库许可文件） | VOL 04/05：仿真与 RoboCasa eval |
| [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) | `96588727e44c78b25ba03ea03b8e12f7e64fd0da` | `main` | Apache-2.0 | VOL 03/06：VLM backbone 与 grounding |
| [NVlabs/cosmos-policy](https://github.com/NVlabs/cosmos-policy) | `18a2accadf4e7a3531e56754102af5a24d2316da` | `main` | Apache-2.0（GitHub search metadata） | VOL 04/07：WAM / Cosmos Policy |
| [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | `9c7e746b2cd37a810070a98ef41d290a07e806c2` | `main` | Apache-2.0（GitHub search metadata） | VOL 03/05：VLA deployment / policy stack |

说明：`git ls-remote --symref` 用于确认 branch 与 HEAD；GitHub API 用于补充 stars、更新时间和 license 元数据。API 对部分 NVIDIA/Physical Intelligence repo 返回 403，因此这些条目的 license 标为“search metadata”，后续仍要以仓库许可证文件为准。

本页的 canonical Markdown、HTML 与 review JSON 已生成；后续按卷逐一核验 README、论文、输入输出 contract、训练/评估命令和版本差异。VOL 02、VOL 03 的专项 ledger 已进入 `sources/`，但总来源图在 code-level reading 完成前仍保持 `researching / WARN`。

## 6. 证据使用规则

- 论文/官方仓库支持方法和接口事实。
- benchmark 官方文档支持任务、协议和指标定义。
- 本地代码/config/log 支持你的实际运行、修改和结果。
- awesome 列表只支持“发现该来源”，不直接支持方法结论。
- 未完成核验的条目显式标记 `planned / unverified`，不进入强答案。
