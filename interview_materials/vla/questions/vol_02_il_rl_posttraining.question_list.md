# VOL 02 IL / RL / Post-training：题目清单（Phase 0）

> 状态：`implemented_40_of_40`  
> 目标：连接 demonstration、offline/online RL、SFT/DPO/GRPO 与机器人策略训练。  
> 与 VOL 01 的边界：VOL 01 讲 MDP、value、advantage 等基础；本卷讲训练算法、数据分布、反馈和 post-training 的取舍。  
> 与 VOL 07 的边界：本卷讲通用机制；个人项目的具体证据和回答放入项目卷。
> 实施记录：40 个稳定 ID 已全部进入 canonical 题卡；范围未扩张到 VOL 03 的 Diffusion / Flow Matching 数学。

## A. 模仿学习与数据分布

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-RL-001 | P0 | L1 | Behavior Cloning 是什么？为什么会有 covariate shift？ | OpenPiVLA |
| VLA-RL-002 | P0 | L1 | BC、DAgger、GAIL、IRL 的差异和适用场景是什么？ | policy learning |
| VLA-RL-003 | P0 | L2 | DAgger 为什么能缓解 compounding error？代价是什么？ | recovery data |
| VLA-RL-004 | P0 | L2 | action chunking 为什么可能缓解行为克隆的误差累积？ | OpenPiVLA |
| VLA-RL-005 | P0 | L2 | 专家轨迹覆盖不足时，如何构造 recovery / intervention 数据？ | UWM / rollout |
| VLA-RL-006 | P0 | L2 | 数据质量、数据量和数据多样性如何取舍？ | OPD / Harness |
| VLA-RL-007 | P1 | L2 | demonstration 中的 suboptimal action 是否应该过滤？ | WAM |
| VLA-RL-008 | P1 | L3 | 如何检测 trajectory leakage、task overlap 和 train/eval contamination？ | 全部 benchmark |

## B. Policy Gradient、Actor-Critic 与 PPO

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-RL-009 | P0 | L1 | REINFORCE 的目标函数和高方差来源是什么？ | RL 基础 |
| VLA-RL-010 | P0 | L2 | actor-critic 为什么比纯 Monte Carlo 更实用？ | WAM value |
| VLA-RL-011 | P0 | L2 | GAE 如何在 bias 和 variance 之间插值？ | PPO / GRPO |
| VLA-RL-012 | P0 | L2 | PPO clipped objective 如何限制策略更新？ | online policy |
| VLA-RL-013 | P1 | L2 | PPO 中 value loss、policy loss、entropy loss 如何平衡？ | post-training |
| VLA-RL-014 | P1 | L3 | PPO ratio、advantage normalization 和 clipping fraction 如何诊断训练？ | run debugging |
| VLA-RL-015 | P1 | L2 | on-policy rollout freshness 为什么影响 PPO 稳定性？ | online GRPO |
| VLA-RL-016 | P2 | L3 | 连续动作 PPO 如何处理 squashed Gaussian、log-prob 和 action bounds？ | robot RL |

## C. Offline RL 与机器人数据

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-RL-017 | P0 | L1 | offline RL 与 online RL 的核心区别是什么？ | 全部训练 |
| VLA-RL-018 | P0 | L2 | offline RL 的 extrapolation error 从哪里来？ | UWM / WAM |
| VLA-RL-019 | P0 | L2 | CQL、IQL、AWAC 等方法如何避免过度相信 OOD action？ | policy improvement |
| VLA-RL-020 | P1 | L2 | behavior constraint、advantage-weighted regression 和 conservatism 如何取舍？ | dataset RL |
| VLA-RL-021 | P1 | L2 | 机器人 offline RL 的 reward labeling、终止和 timeout 如何定义？ | RoboCasa / LIBERO |
| VLA-RL-022 | P1 | L3 | 如何判断 offline RL 失败来自 critic、数据覆盖还是 action parser？ | failure diagnosis |
| VLA-RL-023 | P2 | L3 | 如何把视觉 encoder 的 representation learning 与 offline RL 的 value learning 隔离？ | VLA backbone |

## D. SFT、DPO、GRPO 与后训练

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-RL-024 | P0 | L1 | SFT 在 VLA 或 tool calling 中监督什么？ | Harness / OpenPiVLA |
| VLA-RL-025 | P0 | L2 | DPO 不显式训练 reward model，如何利用 preference pair？ | 大模型实习 |
| VLA-RL-026 | P0 | L2 | DPO 的 reference policy 和 KL 约束分别起什么作用？ | preference tuning |
| VLA-RL-027 | P0 | L2 | GRPO 为什么使用 group-relative reward？与 PPO 有什么关系？ | Harness |
| VLA-RL-028 | P0 | L2 | online GRPO 的 rollout、group、reward checker 和 policy update 如何连接？ | Harness |
| VLA-RL-029 | P1 | L2 | schema、reward、holdout eval 为什么不能混为一谈？ | Robot Harness |
| VLA-RL-030 | P1 | L2 | reward hacking 在工具调用和机器人任务中分别是什么？ | Harness / policy |
| VLA-RL-031 | P1 | L3 | 多目标 reward 如何防止格式正确但语义错误？ | schema-aware reward |
| VLA-RL-032 | P1 | L3 | preference 数据质量、chosen/rejected 构造和 label noise 如何影响 DPO/GRPO？ | 大模型应用实习 |
| VLA-RL-033 | P2 | L3 | 如何把 VLA 的连续动作评价转成可用于 policy optimization 的反馈？ | WAM / VLA-RL |

## E. 训练稳定性、评估与项目转场

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-RL-034 | P0 | L2 | reward scale、advantage scale 和 gradient scale 如何共同影响训练？ | online training |
| VLA-RL-035 | P0 | L2 | policy loss 正常但 success 不涨时，先检查哪些证据？ | WAM / UWM |
| VLA-RL-036 | P1 | L2 | SFT → preference tuning → online RL 的阶段边界如何划分？ | Harness |
| VLA-RL-037 | P1 | L3 | 如何设计 SFT-only、single-teacher、OPD/GRPO ablation 才能支持因果归因？ | OPD / Harness |
| VLA-RL-038 | P1 | L3 | 什么时候辅助目标会帮助 policy，什么时候会造成 gradient interference？ | WAM |
| VLA-RL-039 | P1 | L2 | 如何设计 held-out、OOD、online rollout 三层评估？ | 全部项目 |
| VLA-RL-040 | P2 | L3 | 如果真实机器人交互预算只有 100 episodes，如何分配探索、评估和回放？ | system design |

## 2. 进入正文前的审阅点

1. 是否保留 40 道主问题，并把连续动作反馈、工具调用和机器人 RL 放在同一卷中？
2. 是否同意 VOL 02 重点讲“训练信号和数据分布”，不重复 VOL 03 的 Diffusion/Flow Matching 数学细节？
3. 是否将 VLA-RL-029、030、031、037、038 作为个人项目转场题，但不提前写成你的项目事实？
4. 是否把 `VLA-RL-040` 保留为 L3 系统设计题，等 VOL 08 再扩展完整回答？

用户未提出边界修改后，下一步将先核验 PPO、DPO、GRPO、offline RL 和机器人数据来源，再起草 VOL 02 的 canonical source。
