# VLA Knowledge Map：八卷知识图谱与项目挂钩

> 状态：`drafted`  
> 规划日期：2026-07-16；最近同步：2026-07-21  
> 目的：固定学习顺序、模块边界、题目 ID 和项目连接点，避免后续知识页互相重复或脱离个人经历。

## 1. 一句话总图

```text
# Dependency map: arrows show the dominant learning path, not a hard sequence.
VOL 01 Foundations
      ↓
VOL 02 IL / RL / Post-training ─────┐
      ↓                              │
VOL 03 VLA / Action                  │
      ↓                              │
VOL 04 World Model / Sim2Real        │
      ↓                              │
VOL 05 Engineering / Evaluation ←───┘
      ↓
VOL 06 Perception / Grounding / Nav
      ↓
VOL 07 Personal Project Deep Dives
      ↓
VOL 08 Coding / System Design + 综合模拟面
```

这不是严格线性课程：当某个项目暴露高危缺口时，可以回跳前置模块；但没有通过前置模块的基本检查，不直接进入 L3 研究/系统设计题。

## 2. 八卷范围与完成条件

| 卷 | 必须回答的核心问题 | 子模块 | 项目挂钩 | 完成条件 |
| --- | --- | --- | --- | --- |
| VOL 01 Foundations | 机器人、深度学习和 RL 的共同语言是什么？ | 线性代数/概率、Transformer、优化、MDP、坐标系、控制频率 | OpenPiVLA / UWM | 每个 P0 节点有 L1 定义、L2 机制和 5 道基础题 |
| VOL 02 IL / RL / Post-training | 从 demonstration 到 preference/online feedback 如何训练策略？ | BC、covariate shift、DAgger、PPO、GRPO、SFT/DPO、offline/online RL | Harness / WAM | 能解释目标函数、数据分布和何时会失败 |
| VOL 03 VLA / Action | VLM 如何产生可执行动作？ | VLA 架构、action token、continuous head、FAST、ACT、Diffusion、Flow Matching、chunk/replan | OpenPiVLA | 能对比至少三种 action head，并映射到 action shape/normalization |
| VOL 04 World Model / Sim2Real | 模型如何预测未来、利用价值并跨环境执行？ | dynamics、latent/world rollout、value、planning、domain randomization、sim2real | WAM / UWM | 能区分 offline proxy、world loss、online success 和真实泛化 |
| VOL 05 Engineering / Evaluation | 如何把训练和评估做成可复现、可诊断、可部署的系统？ | data pipeline、distributed training、checkpoint、policy server、latency、fixed-init、failure debugging | 全部项目 | 每个指标都有 protocol、baseline、artifact 和可比性说明 |
| VOL 06 Perception / Grounding / Nav | 视觉、语言、空间和导航信息如何进入策略？ | planned `VLA-PER-001..020`：image/token、point/box/mask、grounding loss/metric、3D/multi-view、VLN/ObjectNav、SLAM/memory、robustness/safety | OPD / Harness | 20/20 source；20/20 knowledge；20/20 card；四学习簇完成 fact review；至少 8 次真实 drill；保持项目 truth boundary |
| VOL 07 Project Deep Dives | 我的项目到底做了什么，哪些不能说？ | five project evidence audit、ownership、immutable/runtime bundle gate、2 分钟叙事、追问树、bad case、claim reconciliation | Robot Harness、OPD、OpenPiVLA、WAM、UWM | 每个强 claim 有证据、个人贡献边界和三档回答 |
| VOL 08 Coding / System Design | 能否把知识落到代码、接口和系统取舍？ | frozen `SYS-VLA-001..004` + `CODE-VLA-001..008`：attention/loss/normalization、transform/FK/PID/TD(0)、train platform、policy service、robot fleet、故障恢复 | 训练/评估工程 | 12/12 source+knowledge+card；4个SYS限时口述；8个CODE白板/runtime练习；保持项目truth boundary |

## 3. 题目 ID 空间

| 前缀 | 范围 |
| --- | --- |
| `VLA-FND-*` | VOL 01 Foundations |
| `VLA-RL-*` | VOL 02 IL / RL / Post-training |
| `VLA-ACT-*` | VOL 03 Action Representation |
| `VLA-ARCH-*` | VOL 03 VLA Architecture |
| `VLA-WM-*` | VOL 04 World Model / Sim2Real |
| `VLA-EVAL-*` | VOL 05 Evaluation / Debugging |
| `VLA-ENG-*` | VOL 05 Engineering / Deployment |
| `VLA-PER-*` | VOL 06 Perception / Grounding / Navigation |
| `PROJ-HARNESS-*` | Robot Harness |
| `PROJ-OPD-*` | OPD / VLM Grounding |
| `PROJ-OPENPIVLA-*` | OpenPiVLA |
| `PROJ-WAM-*` | Cosmos / WAM |
| `PROJ-UWM-*` | UWM / LIBERO |
| `SYS-VLA-*` | VOL 08 系统设计 |
| `CODE-VLA-*` | VOL 08 手撕/实现题 |

## 4. 每个模块的最小闭环

```text
# Minimum module loop: generated artifacts do not imply mastery.
知识页
  → 10-20 个去重后的高价值题卡
  → 至少 2 个项目 hook
  → 1 个公式/实现/shape 追问
  → 1 个 trade-off 或 bad case
  → 5-8 题逐题 drill
  → 根据回答回写知识页或项目 claim
```

“知识页写完”只表示 `drafted`；通过来源审计、HTML 校验和一次口述训练后才进入 `reviewed/drilled`。

## 5. 跨卷连接

| 连接 | 面试中要能回答 |
| --- | --- |
| Foundations → Action | 为什么 action normalization、坐标系和 controller contract 会影响 VLA 成功率？ |
| IL/RL → VLA | BC、Diffusion/Flow Matching 和 GRPO 的监督/反馈边界分别是什么？ |
| Action → Eval | horizon、chunk、replan、denormalization 如何形成闭环 trade-off？ |
| World Model → Eval | world/value 辅助目标为什么可能帮助 action，又为什么可能干扰？ |
| Perception → Project | point/box/text 的格式协议、几何误差和下游可执行性如何区分？ |
| Engineering → Ownership | 哪些是开源基础设施，哪些是我的设计判断、改动和验收？ |
| Project → System Design | 如果任务规模、机器人数量或延迟翻倍，现有方案哪里先失效？ |

## 6. 目前状态

| 资产 | 状态 | 下一步 |
| --- | --- | --- |
| 八卷边界 | drafted | 用户确认后不再随意扩张 |
| 来源入口 | researching | 381/381 canonical生命周期已闭合；VOL 01/02 completion为candidate，VOL 03 Audit A–F与VOL 04 Audit A–E public facts已独立复核，VOL 05当前计划覆盖完成，PER-018 facts已复核；PER-019与PER-020 source/knowledge/card均已冻结并保持unseen；VOL 08 coverage contract冻结为12节点、sources/knowledge/cards 12/12/12，SYS-VLA-004三联件已同步；Robot Harness为28/40 raw、6/10 exact support、12-slot locator，17个候选0 eligible，UWM ActionHeadFix P0 audit已完成但checkpoint/fresh-load/scorer/ownership仍WARN |
| Knowledge HTML | drafted / VOL 01–06 与 VOL 08 当前计划节点均已生成 | VOL 01–05已完成计划内知识/题卡覆盖；VOL 04与VOL 05均为44/44且全部unseen；VOL 06 `VLA-PER-001..020` source/knowledge/card已同步且unseen；VOL 08 十二个 SYS/CODE 节点三联件已同步，所有卡均保持WARN/unseen |
| Question bank | drafted | VOL 01 39 + VOL 02 40 + VOL 03 44 + VOL 04 44 + VOL 05 44 + VOL 06 20 + Project 37 + VOL 08 12，合计280题全部unseen |
| Project evidence | drafted / WARN | 五项目inventories/ownership ledgers均5/5；OpenPiVLA parser gate与Robot Harness aggregate/raw/recovery gates已冻结；后者证明13/13均值、28/40 primary、6/10 exact support并定位12个remote slot，但17个本地候选均不合格，不关闭统一scorer/checkpoint/ownership |
| Practice state | todo | 第一次真实口述后才创建 coaching state；页面生成不计训练成绩 |

## 7. 下一步

1. VOL 01、VOL 02 与 VOL 03 card-level completion 已进入 candidate/WARN；VOL 03 Source Audit A–F 的 public paper/code facts 均已完成独立切片，下一步只做一题真实口述或补本地 runtime artifact。
2. ACT、Diffusion、Flow、Octo mask、openpi checkpoint/norm/transforms/broker 与 RT-2 action-token 事实已复核；local runtime 仍待取证。
3. `VLA-ARCH-007..012` 与 `VLA-ACT-031..032` 已回填并 source-reviewed；整卷不因页面复核升级为 drilled。
4. 保持现有 44 道 VOL 03 题卡为 unseen；真实口述后才更新 coaching state。
5. 仓库completion audit已同步VOL 08 SYS-004 三联件、CODE-008三联件、五项目 P0 audit 与 UWM ActionHeadFix raw train→closed-loop slice：VOL 04与VOL 05均达到knowledge/cards44/44；280 cards全部`unseen`；381/381 canonical artifacts有三联件。VOL 06 planned20、source/knowledge/card20/20/20，PER-001..020三联件已同步；VOL 08 planned12、sources/knowledge/card12/12/12；reference-only probe 不计入候选 ownership；VOL 07已有28/40 raw、6/10 support与12-slot locator，但17个本地候选0 eligible，UWM strict/RoboCasa仍缺trained checkpoint/fresh-load/scorer/ownership，VOL 07/08仍不满足退出条件。
6. VOL 05 Phase 0 已完成44个知识节点与44张题卡；ENG-012..022与EVAL-003..022均完成来源冻结、知识页和单张题卡。强指标仍缺五项目完整paper→runtime→ownership链、timestamped monitoring、confirmed incident RCA、selection→fresh-audit、matched factorial、VLM-human bundle、真实effect-sink、capture→apply latency、offline-online panel与same-bundle sim→shadow→real canary。
7. OpenPiVLA parser/round-trip gate 已完成：Python JSON 只恢复 `15×16` prefix，formal generation/parser/controller 仍缺；下一 bounded slice 优先做 ownership confirmation，或补 immutable formal checkpoint/generation bundle。没有真实回答时不扩题、不升级 mastery。
8. VOL 06 coverage contract冻结为`VLA-PER-001..020`；`001..020`三联件已生成且unseen，source/knowledge/card覆盖为20/20/20。下一 bounded slice只做真实口述或独立fact review；不预改mastery。
9. VOL 08 coverage contract冻结为`SYS-VLA-001..004`与`CODE-VLA-001..008`；当前source/knowledge/card为12/12/12，`SYS-VLA-004` 三联件已同步，十二张卡全部unseen。下一 bounded slice只进行 `SYS-VLA-004` 真实系统设计口述；不修改 mastery。
