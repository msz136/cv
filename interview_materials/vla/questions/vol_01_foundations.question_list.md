# VOL 01 Foundations：题目清单（Phase 0）

> 状态：`awaiting_user_review`  
> 目的：先审边界和题目集合，再开始写 canonical answers。  
> 题目不按公司分类；`P0/P1/P2` 是本仓库的准备优先级，不是公开面经频次。

## 1. 题目范围

VOL 01 只负责“机器人、深度学习和 RL 的共同语言”，不提前展开 VLA 专属 action head、world model 或个人项目细节。它会为后续 VOL 02-VOL 05 提供可复用的基础题。

## 2. 高频基础题清单

### A. 线性代数、概率与优化

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-FND-001 | P0 | L1 | 为什么机器人策略和 VLM 都需要向量化表示？embedding 的维度代表什么？ | OpenPiVLA |
| VLA-FND-002 | P0 | L1 | 点积、余弦相似度和欧氏距离分别适合什么场景？ | OPD / grounding |
| VLA-FND-003 | P0 | L1 | 梯度、Jacobian 和 Hessian 分别描述什么？训练和控制中如何使用？ | 全部项目 |
| VLA-FND-004 | P0 | L2 | 为什么归一化会改变优化难度？LayerNorm、BatchNorm、RMSNorm 如何取舍？ | OpenPiVLA / Qwen3-VL |
| VLA-FND-005 | P0 | L1 | 期望、方差、协方差和相关系数有什么区别？ | 轨迹 / action 统计 |
| VLA-FND-006 | P0 | L2 | MSE、MAE、Huber loss 什么时候使用？对 action outlier 有什么影响？ | WAM / action regression |
| VLA-FND-007 | P1 | L2 | KL divergence 的方向为什么重要？forward KL 和 reverse KL 的行为差异是什么？ | DPO / policy distillation |
| VLA-FND-008 | P1 | L2 | bias-variance trade-off 如何影响策略学习和评估？ | offline proxy / rollout |

### B. 深度学习与 Transformer

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-FND-009 | P0 | L1 | 为什么深度网络需要非线性激活？ReLU、GELU、SiLU 的差异是什么？ | VLM backbone |
| VLA-FND-010 | P0 | L1 | softmax 如何把 logits 变成概率？如何处理数值溢出？ | action token / tool token |
| VLA-FND-011 | P0 | L1 | cross-entropy 与 MSE 的监督对象分别是什么？ | token action / continuous action |
| VLA-FND-012 | P0 | L2 | scaled dot-product attention 为什么需要除以 \(\sqrt{d_k}\)？ | VLA / grounding |
| VLA-FND-013 | P0 | L2 | self-attention、cross-attention、causal mask 和 padding mask 如何区分？ | VLM / policy input |
| VLA-FND-014 | P0 | L2 | Transformer 的位置编码解决什么问题？RoPE 的旋转如何影响相对位置信息？ | 图像/文本/action 序列 |
| VLA-FND-015 | P0 | L2 | pre-norm 和 post-norm 的训练稳定性差异是什么？ | Qwen3-VL / LoRA |
| VLA-FND-016 | P0 | L2 | 多模态输入如何拼接或对齐？图像 token、文本 token、proprio token 的 mask 如何设计？ | OpenPiVLA |
| VLA-FND-017 | P1 | L2 | LoRA 为什么能减少可训练参数？低秩假设的代价是什么？ | OpenPiVLA / Harness |
| VLA-FND-018 | P1 | L2 | KV cache 为什么能加速自回归推理？对 action chunk 生成有什么影响？ | action token |
| VLA-FND-019 | P1 | L3 | 梯度消失/爆炸如何定位？从 loss、gradient norm、activation 和 optimizer 哪些证据入手？ | 训练迁移 |
| VLA-FND-020 | P1 | L3 | 多任务共享 backbone 时，如何判断不同任务的梯度发生冲突？ | WAM / OPD |

### C. MDP、强化学习与策略评估

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-FND-021 | P0 | L1 | MDP 的 \(S,A,P,R,\gamma\) 分别是什么？机器人任务中如何实例化？ | WAM / UWM |
| VLA-FND-022 | P0 | L1 | value function、Q function 和 advantage 有什么区别？ | WAM value head |
| VLA-FND-023 | P0 | L2 | Bellman expectation equation 和 optimality equation 分别解决什么问题？ | RL 基础 |
| VLA-FND-024 | P0 | L2 | on-policy 与 off-policy 的数据分布差异是什么？为什么 replay buffer 有用？ | RL-VLA |
| VLA-FND-025 | P0 | L2 | policy gradient 为什么需要 advantage？baseline 如何降低方差？ | PPO / GRPO |
| VLA-FND-026 | P1 | L2 | PPO clipping 的直觉是什么？它解决了什么更新风险？ | VOL 02 预告 |
| VLA-FND-027 | P1 | L2 | reward、return、value target 和 success predicate 如何区分？ | WAM / UWM eval |
| VLA-FND-028 | P1 | L3 | offline policy 的 distribution shift 与 extrapolation error 如何导致闭环失败？ | UWM / LIBERO |
| VLA-FND-029 | P0 | L2 | 为什么 offline action MSE 下降不一定带来 online success 提升？ | WAM |

### D. 机器人学、几何与控制

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-FND-030 | P0 | L1 | observation、state、proprioception、action 在机器人策略中分别是什么？ | 全部策略项目 |
| VLA-FND-031 | P0 | L1 | 世界坐标、相机坐标、末端坐标和关节坐标如何转换？ | OpenPiVLA / OPD |
| VLA-FND-032 | P0 | L2 | 齐次变换矩阵如何同时表示旋转和平移？坐标变换顺序为什么重要？ | action contract |
| VLA-FND-033 | P0 | L2 | forward kinematics 与 inverse kinematics 的输入输出和数值难点是什么？ | action execution |
| VLA-FND-034 | P0 | L2 | Jacobian 如何把关节速度映射到末端速度？奇异位形会造成什么问题？ | controller |
| VLA-FND-035 | P0 | L1 | position、velocity、torque control 的差异和适用场景是什么？ | policy/controller boundary |
| VLA-FND-036 | P0 | L2 | PID 中 P/I/D 三项各自解决什么问题？积分饱和如何处理？ | rollout debugging |
| VLA-FND-037 | P1 | L2 | 控制频率、观测延迟、推理延迟和 action chunk 如何共同影响稳定性？ | OpenPiVLA / UWM |
| VLA-FND-038 | P1 | L2 | 为什么 action denormalization、clipping 和 gripper 维度顺序会造成系统性失败？ | OpenPiVLA / UWM |
| VLA-FND-039 | P1 | L3 | 什么时候使用 impedance control、MPC 或 learned policy？如何划分职责？ | system design |

## 3. 手撕题候选（VOL 08 也会复用）

| ID | 难度 | 题目 | 说明 |
| --- | --- | --- | --- |
| CODE-VLA-001 | L1 | numerically stable softmax | 解释减去 max 的原因 |
| CODE-VLA-002 | L2 | scaled dot-product attention | 明确 mask 与 shape |
| CODE-VLA-003 | L1 | LayerNorm / RMSNorm | 区分训练/推理与 epsilon |
| CODE-VLA-004 | L1 | MSE / Huber loss with mask | 对应 action loss mask |
| CODE-VLA-005 | L2 | homogeneous transform composition | 维度和乘法顺序 |
| CODE-VLA-006 | L2 | 2-link planar forward kinematics | 从关节角得到末端位姿 |
| CODE-VLA-007 | L2 | PID update with anti-windup | 处理积分项和饱和 |
| CODE-VLA-008 | L2 | Bellman TD(0) update | 正确处理 done 截断 |

## 4. 进入正文前的审阅点

请先确认：

1. VOL 01 是否保留这四个基础域；是否要把 SLAM / 3D perception 放到 VOL 06 而不是本卷。
2. 题量是否先以 39 道基础题 + 8 道手撕候选作为边界，不为了凑数量继续扩张。
3. 是否同意把“Flow Matching、Diffusion Policy、VLA 架构”留到 VOL 03，VOL 01 只准备其所需的数学/优化/控制前置。
4. 是否允许先写 P0 题和基础知识，P1/P2 在第一轮口述暴露缺口后再补。

用户确认后，下一步将：

- 为 P0 题绑定官方/教材来源；
- 写 `knowledge/vol_01_foundations.md` 的第一批正文；
- 生成 `questions/vol_01_foundations.md` 的折叠题卡；
- 创建对应 review JSON，并进行第一轮逐题训练。

