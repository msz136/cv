# VOL 03 VLA / Action：题目清单（Phase 0）

> 规划日期：2026-07-16  
> 状态：`source_batches_A_B_C_D_E_F_audited / knowledge_full_drafted / cards_full_drafted / review_pending`  
> 目标题数：44（`VLA-ARCH-*` 12 题；`VLA-ACT-*` 32 题）  
> 核心目标：能从 observation/text/proprio 的输入合同，一直解释到 action representation、训练目标、denormalization、replan 与 controller 执行。  
> 项目主挂钩：OpenPiVLA；本清单只定义通用问题，不把项目归档结果或上游设计提前写成本人事实。

## 1. 卷间边界

- VOL 01 已覆盖坐标系、控制频率、MDP 和 Transformer 基础，本卷直接使用这些前置知识。
- VOL 02 已覆盖 BC/SFT、PPO/GRPO 与 feedback，本卷只在需要时说明 action head 的监督接口，不重复 post-training 全套推导。
- VOL 05 再展开数据 pipeline、policy server、benchmark protocol 和分布式工程；本卷保留与动作正确性直接相关的最小接口检查。
- VOL 07 再回答 OpenPiVLA 的真实 checkpoint、action shape、97.4% 归属、个人贡献和缺失 artifact。

## A. VLA 架构与输入输出合同（12 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-ARCH-001 | P0 | L1 | VLA 与 VLM、传统 visuomotor policy 的本质区别是什么？ | 定位 |
| VLA-ARCH-002 | P0 | L2 | 一个 VLA 的 observation/text/proprio/action 输入输出合同应包含哪些字段？ | OpenPiVLA |
| VLA-ARCH-003 | P0 | L2 | VLM backbone、action expert、policy head 与 controller 分别负责什么？ | OpenVLA / π 系列 |
| VLA-ARCH-004 | P0 | L2 | 多视角图像、语言与 proprioception 如何进入同一策略？时间对齐在哪里发生？ | OpenPiVLA |
| VLA-ARCH-005 | P0 | L3 | OpenVLA 如何把视觉语言特征映射成离散 action token，再还原连续动作？ | OpenVLA |
| VLA-ARCH-006 | P0 | L3 | π0 的 action expert 与 flow-matching action generation 如何连接？ | openpi |
| VLA-ARCH-007 | P1 | L2 | RT-2、OpenVLA、Octo、π0 的 backbone、action representation 与训练路线如何比较？ | landscape |
| VLA-ARCH-008 | P1 | L3 | VLA 的 token sequence layout、attention mask 和 action positions 为什么会改变 loss 语义？ | implementation |
| VLA-ARCH-009 | P1 | L2 | 冻结 VLM、全量微调、LoRA/adapter 与独立 action expert 如何取舍？ | fine-tuning |
| VLA-ARCH-010 | P1 | L3 | 多机器人异构 action space 如何统一表示，并避免 padding 维污染 loss？ | cross-embodiment |
| VLA-ARCH-011 | P1 | L2 | VLA 延迟主要来自视觉编码、LLM decoding、action sampling 还是通信？怎样拆分？ | deployment boundary |
| VLA-ARCH-012 | P1 | L3 | 如何从论文和仓库核对一个 VLA 的真实 I/O、checkpoint、normalization 与推理合同？ | evidence audit |

## B. Action representation、tokenization 与 FAST（10 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-ACT-001 | P0 | L1 | 连续回归、离散 token、CVAE、Diffusion 与 Flow action head 各自建模什么？ | 总览 |
| VLA-ACT-002 | P0 | L2 | action normalization 与 denormalization 为什么是 VLA 最容易 0-success 的接口之一？ | OpenPiVLA |
| VLA-ACT-003 | P0 | L3 | quantile/bin action discretization 如何编码？分辨率、饱和和分布漂移有什么代价？ | OpenVLA |
| VLA-ACT-004 | P0 | L3 | action token 如何占用语言词表？token offset、vocab collision 和 decode 边界如何检查？ | OpenVLA |
| VLA-ACT-005 | P0 | L2 | FAST 解决了逐标量 action tokenization 的什么效率问题？ | FAST |
| VLA-ACT-006 | P0 | L3 | FAST 的频域变换、量化与 BPE 压缩如何形成 action token 序列？ | FAST |
| VLA-ACT-007 | P1 | L2 | FAST 的 token compression 为什么不等于物理控制误差一定更小？ | FAST |
| VLA-ACT-008 | P0 | L3 | action dimension、padding、mask 和 output slicing 如何写成可验证的张量合同？ | OpenPiVLA |
| VLA-ACT-009 | P1 | L2 | 平移、旋转、gripper 与 base action 应如何表示和归一化？ | robot interface |
| VLA-ACT-010 | P1 | L3 | 如何按多模态性、延迟、数据量和 controller 频率选择 action representation？ | design |

## C. ACT、action chunking 与 temporal ensembling（7 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-ACT-011 | P0 | L2 | action chunk、prediction horizon、execution window 与 replan interval 有何区别？ | OpenPiVLA |
| VLA-ACT-012 | P0 | L3 | ACT 的 CVAE-Transformer 如何一次预测 action chunk？ | ACT |
| VLA-ACT-013 | P1 | L3 | ACT 的 latent/style variable 在训练和推理时如何使用？ | ACT |
| VLA-ACT-014 | P1 | L2 | temporal ensembling 如何融合不同时间预测的同一步动作？ | ACT |
| VLA-ACT-015 | P0 | L3 | chunking、replanning 与 temporal ensembling 如何共同影响闭环性？ | ACT / rollout |
| VLA-ACT-016 | P1 | L2 | chunk 太长或太短分别导致什么误差、延迟和吞吐问题？ | OpenPiVLA |
| VLA-ACT-017 | P1 | L3 | ACT 与 autoregressive token、Diffusion/Flow policy 的归纳偏置如何比较？ | method choice |

## D. Diffusion Policy 与 Flow Matching（13 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-ACT-018 | P0 | L2 | Diffusion Policy 为什么对多模态连续动作有吸引力？ | Diffusion Policy |
| VLA-ACT-019 | P0 | L3 | conditional DDPM action objective 中的 noisy action、noise target 与 condition 是什么？ | Diffusion Policy |
| VLA-ACT-020 | P1 | L3 | noise schedule、prediction type 和 action horizon 如何影响训练与采样？ | Diffusion Policy |
| VLA-ACT-021 | P0 | L2 | receding-horizon action diffusion 如何执行 chunk 并重新观测？ | rollout |
| VLA-ACT-022 | P1 | L2 | 去噪步数、sampler 与 warm start 如何影响策略延迟和稳定性？ | deployment boundary |
| VLA-ACT-023 | P0 | L2 | Flow Matching 的 probability path 与 velocity field 直觉是什么？ | Flow Matching |
| VLA-ACT-024 | P0 | L3 | 线性插值路径下 target velocity 和 flow-matching loss 如何推导？ | Flow Matching |
| VLA-ACT-025 | P1 | L3 | Flow policy 推理时如何通过 ODE solver 从 noise 得到 action chunk？ | openpi |
| VLA-ACT-026 | P0 | L3 | Diffusion noise prediction 与 Flow velocity prediction 的目标和采样有何区别？ | comparison |
| VLA-ACT-027 | P0 | L3 | π0 如何把 VLM context、state 与 noisy action 输入 action expert？ | openpi |
| VLA-ACT-028 | P0 | L3 | action loss mask、有效维度与 padded model dimension 如何避免错误监督？ | OpenPiVLA |
| VLA-ACT-029 | P2 | L2 | conditional dropout / guidance 在 action generation 中何时有意义，风险是什么？ | advanced |
| VLA-ACT-030 | P1 | L3 | Flow/Diffusion loss 正常但 rollout 失败时，如何区分 target、scheduler、normalization 与 controller 问题？ | debugging |

## E. 动作输出到机器人执行（2 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-ACT-031 | P0 | L3 | 模型输出如何经过 slicing、denormalization、坐标/单位转换进入 controller？ | OpenPiVLA |
| VLA-ACT-032 | P0 | L3 | 如何为 action parser、chunk queue、replan 与安全裁剪设计最小闭环单测？ | OpenPiVLA / UWM |

## 2. Phase 0 退出条件

当前检查点：Source Audit A–F 已形成 canonical Markdown、HTML 与 WARN review；`ARCH-001..012` + `ACT-001..032` 的 44 题知识正文和原子题卡均已起草，题卡全部 unseen。Phase 0 的 source/ID/content 条件已满足；独立事实审查与口述训练属于后续质量门，不能因 full draft 自动通过。

1. 44 道题都映射到论文/官方 repo，或被显式标为设计题而非方法事实。
2. OpenVLA、openpi、FAST、ACT、Diffusion Policy、Flow Matching 的版本与关键 I/O 路径冻结。
3. VOL 02/05/07 的边界不重叠：本卷讲动作机制，项目数字和 ownership 后置。
4. OpenPiVLA 的 action dimension、horizon、normalization、checkpoint 和 eval artifact 建立待核对清单。
5. 44 题已按 Source Audit A–F 分批生成完毕；后续只在新证据或独立审查发现问题时改 canonical 内容。
