# VOL 04 World Model / Sim2Real：题目清单（Phase 0）

> 规划日期：2026-07-16  
> 状态：`knowledge_44_of_44 / cards_44_of_44_unseen / source_audit_a_e_and_uwm_b / wm011_014_and_wm030_038_source_frozen / WARN`  
> 目标题数：44（`VLA-WM-001..044`）  
> 核心目标：能从 world model 的概率合同、latent rollout 与训练目标，一直解释到 planning/value、多目标干扰、Sim2Real domain gap、strict closed-loop evaluation 和失败归因。  
> 项目主挂钩：Cosmos / WAM、UWM / LIBERO；本清单只规划通用问题，不把项目页数字、上游架构或后续设计提前写成本人事实。

## 1. 卷间边界

- VOL 01 已覆盖 MDP/POMDP、概率、优化、坐标系与 controller 基础；本卷直接使用。
- VOL 02 已覆盖 value、actor-critic、offline/online RL；本卷聚焦 world model 如何提供 imagination、planning 或辅助目标，不重讲 PPO/GRPO。
- VOL 03 已覆盖 VLA action representation、Diffusion/Flow、chunk/replan 与 controller；本卷只在 UWM/Cosmos 的 joint action-world objective 需要时复用。
- VOL 05 再展开 distributed training、policy server、benchmark harness 与统计工程；本卷只保留 world-model validity 和 Sim2Real 因果所需的最小 protocol。
- VOL 07 再核实 WAM/UWM 的 checkpoint、指标、个人贡献与 run ledger；本卷不把项目页的 45%、71.19%、74.4% 或 92.8% 当通用方法事实。

## A. World Model 基础与范式（10 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-WM-001 | P0 | L1 | 什么是 world model？它与 policy、environment simulator、reward/value model 分别是什么关系？ | 总览 |
| VLA-WM-002 | P0 | L2 | world model 应建模 observation、state、latent、reward、termination 中哪些变量？ | I/O contract |
| VLA-WM-003 | P1 | L2 | deterministic dynamics 与 probabilistic dynamics 各自能表达什么不确定性？ | uncertainty |
| VLA-WM-004 | P0 | L3 | latent world model 的 encoder、transition、decoder、reward 与 continuation head 如何连接？ | Dreamer / RSSM |
| VLA-WM-005 | P0 | L2 | one-step prediction 好为什么不代表 multi-step rollout 可靠？ | compounding error |
| VLA-WM-006 | P1 | L3 | teacher forcing、open-loop rollout 与 scheduled sampling 的分布差异是什么？ | train/eval gap |
| VLA-WM-007 | P1 | L3 | aleatoric 与 epistemic uncertainty 如何区分，分别怎样影响 planning？ | risk |
| VLA-WM-008 | P0 | L2 | video generation model 何时可以叫 actionable world model，何时只是视觉预测器？ | Cosmos / UWM |
| VLA-WM-009 | P1 | L2 | world model 作为 policy auxiliary representation 与作为可查询 simulator 有何区别？ | WAM / planning |
| VLA-WM-010 | P0 | L3 | model bias 与 rollout compounding error 如何导致“想象中很好、真实执行失败”？ | debugging |

## B. 架构、数据与训练目标（10 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-WM-011 | P0 | L2 | reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么？ | objective |
| VLA-WM-012 | P0 | L3 | RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导？ | DreamerV3 |
| VLA-WM-013 | P1 | L3 | latent overshooting 或 multi-step consistency loss 解决什么，可能带来什么偏差？ | long horizon |
| VLA-WM-014 | P0 | L3 | action-conditioned prediction 怎样区分相关性预测与可干预 dynamics？ | causal action |
| VLA-WM-015 | P0 | L3 | UWM 如何把 video diffusion 与 action diffusion 放进统一预训练框架？ | UWM |
| VLA-WM-016 | P1 | L3 | action/video joint objective 的共享表示、condition、noise schedule 和 mask 应怎样审计？ | UWM / WAM |
| VLA-WM-017 | P1 | L3 | heterogeneous robots 的 camera、state、action 和 horizon 如何统一而不污染 world loss？ | cross-embodiment |
| VLA-WM-018 | P1 | L2 | prediction horizon 过短或过长如何影响可控性、细节与训练稳定性？ | horizon |
| VLA-WM-019 | P0 | L2 | PSNR/SSIM/FVD、latent loss、action MSE 与 downstream success 各能证明什么？ | metric boundary |
| VLA-WM-020 | P1 | L3 | 怎样发现 posterior collapse、action ignoring、future leakage 与 background shortcut？ | bad case |

## C. Imagination、Planning、Value 与多目标训练（10 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-WM-021 | P0 | L3 | Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？ | DreamerV3 |
| VLA-WM-022 | P0 | L2 | MPC、CEM/MPPI 与 best-of-N trajectory selection 的共同点和差异是什么？ | planning |
| VLA-WM-023 | P0 | L2 | open-loop plan 与 receding-horizon replanning 如何权衡 latency、鲁棒性和 horizon？ | Cosmos planning |
| VLA-WM-024 | P0 | L2 | reward model、value function、success classifier 与 termination predictor 如何区分？ | value semantics |
| VLA-WM-025 | P0 | L3 | Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？ | WAM |
| VLA-WM-026 | P0 | L2 | world/value auxiliary objective 为什么可能帮助 action imitation？ | WAM |
| VLA-WM-027 | P1 | L3 | 什么时候 auxiliary world/value 会负迁移，如何识别 gradient conflict？ | interference |
| VLA-WM-028 | P0 | L3 | sample routing、slot mask 与 loss weight 怎样避免 action/world/value 互相污染？ | WAM |
| VLA-WM-029 | P1 | L3 | value 在 imagined/OOD state 上为何容易失准，如何做 calibration 或 pessimism？ | risk-aware planning |
| VLA-WM-030 | P1 | L3 | test-time planning 增加的 N、world rollout、value scoring 与通信开销怎样计时和限险？ | deployment |

## D. Sim2Real、Domain Gap 与安全（8 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-WM-031 | P0 | L1 | Sim2Real reality gap 主要来自视觉、动力学、控制、任务与随机性哪些层？ | taxonomy |
| VLA-WM-032 | P0 | L2 | visual/domain randomization 该随机化什么，怎样避免随机化到无关分布？ | perception gap |
| VLA-WM-033 | P0 | L3 | dynamics randomization 与 system identification 如何互补，参数范围怎样确定？ | dynamics gap |
| VLA-WM-034 | P0 | L3 | control frequency、action latency、actuator dynamics 与 controller mismatch 如何破坏 Sim2Real？ | control gap |
| VLA-WM-035 | P1 | L2 | camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模？ | calibration |
| VLA-WM-036 | P0 | L3 | friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点？ | contact |
| VLA-WM-037 | P1 | L3 | residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择？ | adaptation |
| VLA-WM-038 | P0 | L3 | uncertainty-aware planning、安全约束、fallback 和 recovery policy 如何形成最小闭环？ | safety |

## E. World Model 评估与失败归因（6 题）

| ID | 优先级 | 难度 | 题目 | 主要挂钩 |
| --- | --- | --- | --- | --- |
| VLA-WM-039 | P0 | L3 | UWM / LIBERO 的 checkpoint、normalizer、init、warmup、horizon 与 rollout 数怎样构成 strict protocol？ | UWM |
| VLA-WM-040 | P0 | L2 | world model open-loop prediction metric 与 closed-loop policy success 怎样建立但不夸大关联？ | eval |
| VLA-WM-041 | P0 | L3 | offline future/action/value loss 下降但 online success 不变时，如何设计消融？ | WAM / UWM |
| VLA-WM-042 | P1 | L3 | 如何检测 hallucination、physical inconsistency、action insensitivity 与 causal inconsistency？ | world-model eval |
| VLA-WM-043 | P0 | L2 | 失败轨迹怎样按 perception、dynamics、contact、planning、controller 和 recovery 分层回写数据？ | debugging |
| VLA-WM-044 | P0 | L3 | 如何从 paper/repo/checkpoint/eval harness 核对 world model 的真实训练和 rollout 合同？ | evidence audit |

## 2. Phase 0 退出条件

1. 44 道题都有 primary paper / official repo / benchmark source，或被明确标为设计框架。
2. UWM、Cosmos Policy、DreamerV3、LIBERO、RoboCasa 的 paper/repo/checkpoint/eval 角色分开，不把名字相近的 world model 混写。
3. `VLA-WM-015..016` 和 `025..030` 已完成 UWM/Cosmos claim-to-code；`031..038` 已完成 Sim2Real source freeze；`039..044` 已完成 benchmark/evidence Audit E。
4. 项目数字只进入 VOL 07 evidence：WAM 的离线 MSE/官方 baseline、本地 0-success；UWM 的 strict/reset/official 三套结果不得提前揉成方法结论。
5. 题卡生成后全部从 `unseen` 开始；没有真实口述就不创建 coaching state。

## 3. 当前已交付切片

`VLA-WM-001..010`、`VLA-WM-015..029` 与 `VLA-WM-039..044` 已完成 canonical knowledge/card，共 31 张题卡全部保持 `unseen`。WM-029 已冻结 calibration/PETS/MOPO/CQL 与 Cosmos LCB 边界；剩余 13 个节点继续 source-first。

| 顺序 | 题目 | 主要 source audit | 本批必须产出 |
| --- | --- | --- | --- |
| 1 | `VLA-WM-039` strict protocol | Audit B + E | 12-field protocol tuple、UWM三协议对照、manifest |
| 2 | `VLA-WM-040` metric ladder | Audit A + B + E | one-step/open-loop/proxy/sim/real 证据阶梯 |
| 3 | `VLA-WM-041` offline↓ online不变 | Audit B + C + E | action-only/+world/+value/all 与 protocol paired ablation |
| 4 | `VLA-WM-042` physical/causal inconsistency | Audit A + B + E | action perturbation、cycle、contact、long-rollout tests |
| 5 | `VLA-WM-043` failure trace | Audit D + E | protocol/checkpoint/observation/action/contact/recovery taxonomy |
| 6 | `VLA-WM-044` evidence audit | Audit A–E | paper→repo→checkpoint→runtime→ownership ledger |

## 4. Batch 1 交付与验收

1. 已完成：增量创建 `knowledge/vol_04_world_model_sim2real.md`，首批只覆盖 6/44；渲染 HTML 并生成 `WARN` review。
2. 已完成：增量创建 `questions/vol_04_world_model_sim2real.md`，只生成 6 张原子题卡，全部初始状态为 `unseen`。
3. 已验收：每题包含 30 秒回答、机制展开、诊断/消融、项目挂钩、危险回答和 primary sources；项目数字只以 `claim-only` 例子出现。
4. 已同步 master question index 和 module progress；未把任何题改成 reviewed、drilled 或 mastered。
5. Batch 1 已完成独立 frozen-source 事实复核并保持 WARN；后续 foundations 小批另行完成，不改变这一批的历史验收边界。

## 5. Foundations 题卡批次交付

Source Audit A 的独立复核、`VLA-WM-001..010` foundations 知识页和 10 张对应题卡均已完成，覆盖 world-model 定义/I-O、deterministic/probabilistic dynamics、RSSM、one-step/open-loop、uncertainty、actionable video model、auxiliary-vs-simulator 与 model bias。10 张 foundations 卡与既有 6 张 evaluation 卡全部为 `unseen`。

## 6. WM-015 UWM Coupling 单节点交付

- UWM Audit B 已完成 canonical audit 与独立 frozen-raw-source 复核。
- 已生成 [`VLA-WM-015` 知识页](../knowledge/vol_04_world_model_sim2real_wm015.html) 和 [单张折叠题卡](vol_04_world_model_sim2real_wm015.html)，覆盖 robot/action-free tuple、共享 DiT、独立 timestep、sampling mode 与 `action_mask`/loss 边界。
- 题卡保持 `unseen`；不绑定用户 UWM 74.4%/92.8%、checkpoint provenance 或个人原创。
- WM-015..018 共 4 张原子题卡均保持 `unseen`；未发生真实口述，不创建 `coaching_state.md`。

## 7. WM-019 Metric Boundary 历史检查点

- 已生成 [`VLA-WM-019` 知识页](../knowledge/vol_04_world_model_sim2real_wm019.html)，覆盖 PSNR/SSIM/FVD、latent/action loss、teacher-forced/open-loop、WorldGym proxy 与 sim/real closed-loop 的证据阶梯、统计单位和 protocol tuple。
- 该历史检查点完成时 VOL 04 为 knowledge 21/44、cards 21/44、全局 197 cards；后续增量不回写成当时已完成。

## 8. WM-020..038 单节点链交付

- 已逐节点完成 WM-020 failure diagnostics、WM-021 Dreamer imagination、WM-022 MPC/CEM/MPPI、WM-023 receding horizon、WM-024 value semantics、WM-025 Cosmos slot/mask/loss、WM-026 auxiliary benefit、WM-027 negative transfer、WM-028 routing/mask/effective weight 与 WM-029 value calibration/pessimism。
- 已继续完成 WM-030 test-time planning latency risk、WM-031 reality-gap taxonomy、WM-032 visual DR/relevant support、WM-033 dynamics DR/SysID、WM-034 control/latency/actuator/controller mismatch、WM-035 camera/sensor modeling、WM-036 contact/friction/compliance/gripper semantics、WM-037 adaptation method selection 与 WM-038 uncertainty/safety/fallback/recovery。
- 当前 VOL 04 为knowledge 44/44、cards 44/44；全局题库234 cards，全部保持`unseen`；WM-011..014架构/目标子链与WM-031..038 Sim2Real子链均已闭合。
- WM-027 明确区分 matched negative transfer 与局部 gradient conflict，并冻结 PCGrad/GradNorm 公式、限制和 contract-first 排查。
- WM-029 独立冻结 Calibration/PETS/MOPO/CQL primary sources，并回查 frozen Cosmos same-model sampling LCB、post-clip std、β=1 与默认 ensemble-off 边界。
- VOL 04页面覆盖已收口但仍为WARN/unseen；下一bounded slice转VOL 05 `VLA-EVAL-004` paired init/seed evaluation与显著性，不创建coaching state。
