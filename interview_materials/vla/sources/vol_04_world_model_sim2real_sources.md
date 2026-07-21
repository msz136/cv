# VOL 04 World Model / Sim2Real：来源 Registry

> 调研日期：2026-07-16；registry reconciliation：2026-07-20  
> 状态：`source_registry_reconciled / audits_A_E_present / A_B_C_E_independently_reviewed / D_review_pending / local_gates_warn`  
> 对应题目：[`../questions/vol_04_world_model_sim2real.question_list.md`](../questions/vol_04_world_model_sim2real.question_list.md)  
> 目标：为 world model probability contract、latent dynamics、video/action diffusion、imagination/planning/value、多目标干扰、Sim2Real 与 strict evaluation 建立 primary-source ledger。  
> 边界：五个 source batch 均已有 canonical audit，但审查深度不相同：A/B/C/E 有独立 frozen-source review，D 仍只有 mechanism audit；27 个 WM-011..014、016..038 节点有独立 source-freeze 页面，WM-015 由 UWM Audit B 承载。44/44 knowledge/cards 覆盖不等于 local runtime、因果归因、个人 ownership 或口述 mastery。

## 1. Scope 与研究问题

本卷按五条链组织：

```text
# Source-first sequence for VOL 04; project claims stay behind evidence gates.
observation/state/action/reward/termination contract
        -> latent or video dynamics model
        -> one-step / rollout / imagination objective
        -> planning, value or policy auxiliary use
        -> Sim2Real + strict closed-loop evaluation
```

需要回答：world model 到底预测什么；怎样区分视觉好看与可行动力学；UWM 如何联合 video/action diffusion；Cosmos Policy 如何同时产生 action/future/value 并做 planning；Dreamer 如何在 latent imagination 里训练策略；domain randomization/system ID/latency/contact 如何影响 Sim2Real；最后怎样用 strict protocol 和 failure traces 避免把 offline proxy 写成 online 成功。

## 2. Primary papers / technical reports

| 主题 | 来源 | 计划支持的 claim | 当前状态 |
| --- | --- | --- | --- |
| World Models | Ha & Schmidhuber, [World Models](https://arxiv.org/abs/1803.10122), 2018 | compressed spatial/temporal model、policy in learned environment 的历史范式 | Audit A + independent review / WARN |
| PlaNet / latent planning | Hafner et al., [Learning Latent Dynamics for Planning from Pixels](https://arxiv.org/abs/1811.04551), 2019 | latent dynamics、planning from pixels、multi-step objective | Audit A + independent review / WARN |
| DreamerV3 | Hafner et al., [Mastering Diverse Domains through World Models](https://arxiv.org/abs/2301.04104), arXiv / Nature 2025 | RSSM、reconstruction/reward/continuation、latent imagination actor-critic | Audit A + independent review；repo reimplementation boundary retained / WARN |
| TD-MPC2 | Hansen et al., [TD-MPC2](https://arxiv.org/abs/2310.16828), 2024 | latent model-based RL、value/planning 对照 | registered + WM-022 node source freeze；volume-level independent review pending / WARN |
| UWM | Zhu et al., [Unified World Models](https://arxiv.org/abs/2504.02792), RSS 2025 | video/action diffusion coupling、heterogeneous robot pretraining、LIBERO/DROID | Audit B + UWM independent review；checkpoint/runtime/license pending / WARN |
| Cosmos Policy | Kim et al., [Cosmos Policy](https://arxiv.org/abs/2601.16163v1), 2026 | video model fine-tune、action/future/value outputs、best-of-N planning | Audit C + independent review + node source freezes；checkpoint/runtime/ownership pending / WARN |
| Domain randomization | Tobin et al., [Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World](https://arxiv.org/abs/1703.06907v1), 2017 | visual randomization 与 reality gap | Audit D + WM-032 node source freeze；volume-level independent review pending / WARN |
| Dynamics randomization | Peng et al., [Sim-to-Real Transfer of Robotic Control with Dynamics Randomization](https://arxiv.org/abs/1710.06537v3), 2018 | dynamics parameter randomization、control transfer | Audit D + WM-033 node source freeze；95-parameter recipe not generalized / WARN |
| SimOpt | Chebotar et al., [Closing the Sim-to-Real Loop](https://arxiv.org/abs/1810.05687v4), 2019 | real-trajectory-guided simulation-distribution adaptation | Audit D + WM-037 node source freeze；safe real rollout authority required / WARN |
| Actuator / latency | Tan et al., [Learning Agile Locomotion for Quadruped Robots](https://arxiv.org/abs/1804.10332v2), 2018 | measured SysID、actuator model、latency、range margin | Audit D + WM-034 node source freeze；locomotion numbers not transferred / WARN |
| Online adaptation | Yu et al. [UP-OSI](https://arxiv.org/abs/1702.02453v3) / Kumar et al. [RMA](https://arxiv.org/abs/2107.04034v1) | explicit parameter vs task-relevant latent adaptation | Audit D + WM-037 node source freeze；volume-level independent review pending / WARN |
| Residual / recovery / cautious MPC | [Residual RL](https://arxiv.org/abs/1812.03201v2) / [Recovery RL](https://arxiv.org/abs/2010.15920v2) / [Cautious MPC](https://arxiv.org/abs/1705.10702v4) | contact residual、risk gate、chance-constrained planning | Audit D + WM-037/038 node source freezes；no generic formal safety claim / WARN |
| Robot policy eval in WMs | [WorldGym](https://arxiv.org/abs/2506.00613v3) / [world-model-eval](https://github.com/world-model-eval/world-model-eval) | 用 learned world model 评估 policy 的 validity / failure boundary | Audit E + Batch 1 independent review；proxy≠closed-loop success / WARN |

## 3. Official repository ledger frozen at 2026-07-16

| Repo | Frozen HEAD / branch | License status | 本卷用途 |
| --- | --- | --- | --- |
| [NVlabs/cosmos-policy](https://github.com/NVlabs/cosmos-policy) | `18a2accadf4e7a3531e56754102af5a24d2316da` / `main` | Apache-2.0（frozen root LICENSE verified）；HF policy weights 另为 NSCLv1 | action/future/value I/O、Predict2 configs、denoising、planning、LIBERO/RoboCasa eval |
| [WEIRDLabUW/unified-world-model](https://github.com/WEIRDLabUW/unified-world-model) | `b7d4067c8859775e5b08f681e76d538015cdd445` / `main` | frozen tree 无 LICENSE/COPYING/NOTICE；不能假定复用许可 | video/action diffusion、pretrain/cotrain/finetune、LIBERO/DROID |
| [danijar/dreamerv3](https://github.com/danijar/dreamerv3) | `e3f02248693a79dc8b0ebd62c93683888ddaccfe` / `main` | MIT（GitHub metadata） | world model、imagination actor-critic、config/metric 对照；README 自称 reimplementation |
| [Lifelong-Robot-Learning/LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) | `8f1084e3132a39270c3a13ebe37270a43ece2a01` / `master` | MIT（frozen LICENSE） | task suites、pruned init、default eval、environment/controller/success |
| [robocasa/robocasa](https://github.com/robocasa/robocasa) | `b4684e6ee37d377cc392e98302a6b916d588b415` / `main` / package 1.0.1 | MIT（frozen LICENSE） | 当前官方 API/语义对照；不是 Cosmos runtime provenance |
| [moojink/robocasa-cosmos-policy](https://github.com/moojink/robocasa-cosmos-policy) | observed `edd9a328b3ec98050f42d194c1419307a79c4d87` / `main` / package 0.2.0 | MIT（observed frozen LICENSE） | Cosmos `ROBOCASA.md` 的安装目标；命令未 pin，不能反推论文 runtime |
| [world-model-eval/world-model-eval](https://github.com/world-model-eval/world-model-eval) | `709665b29f5c95124e7dbc05b0d4d47cd353de97` / `master` | no license found in initial metadata/raw check | policy-in-world-model evaluation boundary；暂不执行/复用代码 |
| [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | `0ce5e98916d8128ddb0eeb2f17304d2d9d29eecf` / observed HEAD | Apache-2.0（raw frozen LICENSE） | contact/friction/solver/actuator/timestep parameter semantics；docs build commit未绑定 |
| [ARISE-Initiative/robosuite](https://github.com/ARISE-Initiative/robosuite) | `5ce6643f3092639d08f7b0f90ed1c6a84f50552c` / observed HEAD | MIT（raw frozen LICENSE） | controller/action split semantics；不是项目 local controller config |

冻结 HEAD 只记录访问时版本，不等于相应 checkpoint 与当前 main 兼容。特别是 DreamerV3 repo README 明确称其为基于 DreamerV2 的 reimplementation，不能冒充论文作者官方实现；使用前需在 Audit A 标清同源/作者与实现边界。

## 4. Source batches

| Batch | 覆盖题目 | 必须回答 | 证据动作 | 未完成前禁止的表述 |
| --- | --- | --- | --- | --- |
| A：Foundations / Dreamer | `WM-001..014`、`019..021` | world model I/O、RSSM、KL、one-step/rollout、imagination 与 metric boundary | **canonical audit + 独立 frozen-source 复核完成 / WARN**：[Audit HTML](vol_04_world_model_foundations_claim_to_code.html) / [Audit Markdown](vol_04_world_model_foundations_claim_to_code.md) / [Audit review](vol_04_world_model_foundations_claim_to_code.review.json) / [独立复核](vol_04_world_model_foundations_independent_fact_review.html)；对应 knowledge/cards 已同步 | “world model 就是视频生成器” |
| B：UWM | `WM-015..020`、`039..044` | video/action diffusion 如何耦合、mask/horizon/dataset、LIBERO pretrain/finetune/eval | **canonical audit + UWM/Batch 1 独立复核完成 / WARN**：[HTML](vol_04_uwm_video_action_claim_to_code.html) / [Markdown](vol_04_uwm_video_action_claim_to_code.md) / [review](vol_04_uwm_video_action_claim_to_code.review.json) / [UWM 独立复核](vol_04_uwm_independent_fact_review.html) / [Batch 1 独立复核](vol_04_batch1_independent_fact_review.html)；checkpoint/runtime/license 与本地结果仍待完成 | “UWM 名称能证明本地 74.4% checkpoint” |
| C：Cosmos Policy / WAM | `WM-008..009`、`022..030`、`040..044` | action/future/value outputs、sample routing、denoise、best-of-N planning、RoboCasa/LIBERO | **canonical audit + volume-level independent review + WM-022..030 node source freezes 完成 / WARN**：[Audit HTML](vol_04_cosmos_policy_wam_claim_to_code.html) / [Audit Markdown](vol_04_cosmos_policy_wam_claim_to_code.md) / [Audit review](vol_04_cosmos_policy_wam_claim_to_code.review.json) / [独立复核](vol_04_cosmos_policy_wam_independent_fact_review.html)；checkpoint tensor、dataset revision、local result与ownership仍待完成 | “官方 98.5%/67.1% 或历史数字是本地训练收益” |
| D：Sim2Real | `WM-031..038`、`040..044` | visual/dynamics/control/contact gap、randomization、system ID、adaptation、safety | **canonical audit + WM-031..038 node source freezes + volume-level independent fact review 完成 / PASS WITH WARNING**：[Audit HTML](vol_04_sim2real_claim_to_mechanism.html) / [Audit Markdown](vol_04_sim2real_claim_to_mechanism.md) / [Audit review](vol_04_sim2real_claim_to_mechanism.review.json) / [独立复核](vol_04_sim2real_independent_fact_review.html)；10 篇 fixed PDF、MuJoCo/OpenCV/robosuite semantics 与 12 probes 已复核，真实硬件、runtime、ownership 与 oral gate 仍 WARN | “randomization 越宽越鲁棒” |
| E：Benchmark / Evidence | `WM-039..044` | strict init/warmup/norm/checkpoint/rollout、WM metrics vs success、failure taxonomy | **canonical audit + 独立事实复核完成 / WARN**：[Audit HTML](vol_04_benchmark_evidence_claim_to_protocol.html) / [Audit Markdown](vol_04_benchmark_evidence_claim_to_protocol.md) / [Audit review](vol_04_benchmark_evidence_claim_to_protocol.review.json) / [独立复核](vol_04_batch1_independent_fact_review.html) | 跨 fixed/reset/paper/proxy protocol 混分；把 74.4% 称为 Table-II strict aligned |

## 5. Literature reconciliation matrix

| Source | Method / mechanism | Dataset / task | 对本卷的作用 | 已知限制 / 待核 |
| --- | --- | --- | --- | --- |
| World Models | VAE + recurrent dynamics + controller | VizDoom / CarRacing | 历史直觉：压缩表征中学习 dynamics | 不等同现代 robot video diffusion |
| DreamerV3 | latent world model + imagined actor-critic | diverse RL domains | imagination/value/planning 主对照 | repo 为 reimplementation；robot/VLA 迁移需谨慎 |
| UWM | coupled video and action diffusion | DROID、Robomimic、LIBERO | 用户 UWM 项目最直接上游 | paper/repo 已审计；checkpoint/runtime/license 仍待本地取证 |
| Cosmos Policy | fine-tuned video model，action/future/value，best-of-N | LIBERO、RoboCasa、ALOHA | 用户 WAM/Cosmos 项目最直接上游 | paper/13 official files/三份HF revision/10 probes已独立复核；checkpoint tensor、dataset revision与本地运行仍待核 |
| LIBERO | lifelong robot learning suites | manipulation sim | task/pruned-init/default eval contract | default 20×5×600 不是所有论文 protocol |
| RoboCasa | kitchen manipulation benchmark | simulation + assets | WAM/Cosmos eval context | Cosmos 使用未 pin 的 0.2 fork；当前 official 1.0.1 不能替代 runtime provenance |
| domain/dynamics randomization | simulator parameter distributions | Sim2Real robotics | reality-gap 基础 | 不能替代 target-domain system ID |
| SimOpt / UP-OSI / RMA | distribution adaptation / explicit or latent online adaptation | pushing、locomotion、manipulation | real-data authority 与 adaptation 选择 | 需要任务匹配、可辨识性与安全 rollout |
| Residual / Recovery / cautious MPC | bounded correction、risk gate、chance constraint | contact-rich control / safe RL / racing | safety/recovery 设计边界 | 经验安全不等于 formal certification |

## 6. Local evidence boundary

| 项目 claim | 当前项目页口径 | 进入 VOL 04/07 前需要的 artifact |
| --- | --- | --- |
| WAM action/world/value 三目标 | 上游机制 + 本地复现/诊断混合 | exact model/config、slot/loss mask、dataset schema、run ledger |
| held-out MSE 0.09718→0.05349 | 离线 proxy，非 closed-loop success | split、metric script、checkpoint、prediction/label artifacts |
| official HF baseline 71.19% | 验证 harness，不是本地训练结果 | model ID/revision、24×5 protocol、summary/videos |
| local WAM 0-success | failure diagnosis，不是成功性能 | local checkpoint/load log、sampler、action/gripper stats、rollouts |
| UWM strict 74.4% | 5 tasks × 50 rollouts；低于 official rounded avg | per-task summary、checkpoint/normalizer、init/warmup/eval code hashes |
| UWM reset-style 92.8% | diagnostic only，不与 strict 直接比较 | reset distribution、episodes、same checkpoint/harness delta |
| personal contribution | 迁移/协议/诊断需与上游分离 | local diff、design notes、commands、logs、ownership boundary |

上述数字当前只作为后续 evidence queue，不进入通用知识答案。上游 UWM/Cosmos architecture 也不能写成本人原创。

## 7. Quality gates

1. 先冻结论文版本、repo commit、license、checkpoint/model-card revision，再引用实现。
2. display formula 必须连接 tensor shape、condition、mask、target、train/infer 或 planning step。
3. 一步预测、open-loop rollout、imagined planning、real closed-loop 分四个 protocol；指标不可互相替代。
4. world/value/action auxiliary claim 至少需要 action-only / +world / +value / all 消融才能说“帮助”；没有消融只写机制假设或相关观察。
5. Sim2Real claim 必须说明 randomized parameters/distributions、target hardware、controller、latency 与 safety；“加噪声”不是完整方案。
6. 项目 hook 保留 checkpoint/normalizer/init/rollout/ownership 边界；不把官方 baseline 或 reset-style 数字写成本地强结果。

## 8. Registry reconciliation

| 闭环项 | 当前证据 | 状态 |
| --- | --- | --- |
| primary paper / technical-report ledger | 16 篇独立 paper/report URL；复合行仍逐篇计数 | `16 registered` |
| official repository ledger | 9 个 frozen/observed revisions；license 与 checkpoint compatibility 分离 | `9 registered / warning retained` |
| Source Audit A–E | 五份 canonical audit 均有 HTML/review | `5/5 present` |
| 独立事实复核 | A Foundations、B UWM、C Cosmos/WAM、E Benchmark/Protocol 有独立 frozen-source record | `4/5 independently reviewed` |
| 尚未独立复核 | D Sim2Real 的 volume-level audit | `1/5 pending` |
| 原子 source freeze | WM-011..014、WM-016..038 共 27 个 node source-freeze；WM-015 由 Audit B/UWM 独立复核承载；另有 WM-019 local artifact gate | `28 source/artifact records / WARN` |
| VOL 04 knowledge / cards | base 16 + atomic 28，覆盖 `VLA-WM-001..044` | `44/44 / all unseen` |
| UWM/WAM local evidence | inventories、ownership ledgers 与有限 diagnostic artifacts 已链接；checkpoint/normalizer/controller/episode/ownership 未闭合 | `WARN` |
| candidate oral mastery | 没有真实回答；`coaching_state.md` 不存在 | `PENDING` |

Registry closure 只消除文件生命周期例外；Audit C 已由独立页面升级为 public-facts reviewed，但 Audit D 仍 pending，44/44 页面覆盖也不等于 reviewed/drilled。

## 9. 下一 bounded slice

1. 不再生成 VOL 04 knowledge/card；44 张保持 `unseen`。
2. 若继续提高本卷 source depth，只单独进行 Audit D Sim2Real 独立事实复核；Audit C 不再重复审查。
3. 若继续完成八卷范围，下一轮先做 VOL 06 Perception/Grounding/Navigation coverage-gap audit，冻结整卷题目范围与退出条件，再决定一个原子知识切片。
4. UWM 74.4%/92.8%、WAM 84/118 与 MSE 继续留在 VOL 07 evidence queue；找到 checkpoint、normalizer、config、episode manifest 与 ownership confirmation 前不升级为 verified personal evidence。
