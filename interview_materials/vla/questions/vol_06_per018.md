# VOL 06 Perception / Grounding / Navigation：PER-018 原子题卡

> 状态：`drafted / card_1_of_1 / source_independently_reviewed / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-018`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-018 Navigation BC / DAgger / RL / Exposure Bias Knowledge](../knowledge/vol_06_per018_navigation_bc_dagger_rl_exposure_bias.html)；来源边界见 [PER-018 Source Freeze](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html)。

## Navigation BC、DAgger、PPO 与 Exposure Bias

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-018</b> · VLN/ObjectNav 中 BC、Teacher/Student Forcing、Scheduled Sampling、DAgger 与 PPO 如何区分？怎样判断项目是否真的实现了 DAgger/PPO？</summary>

**面试意图**：判断你能否从 state distribution、target/feedback、update object 和 train/eval protocol 四层区分 imitation/RL，并在项目追问中守住 oracle、reward、rollout freshness、STOP、termination/truncation、checkpoint 与 ownership 边界。

**30 秒回答**：BC在expert分布学action；student forcing改后续state；scheduled sampling混合previous input。DAgger需oracle、immutable aggregate和β；PPO需fresh rollout、reward、old log-prob、GAE。无runtime不宣称实现。

**机制展开（约 2 分钟）**：按state distribution区分：BC/teacher forcing在expert轨迹做masked likelihood；student forcing用learner action推进环境；scheduled sampling只改previous input。DAgger每轮用β混合策略，在visited state查oracle并追加immutable aggregate。PPO需fresh rollout、reward、old log-prob、value/GAE，再做ratio/clip更新。评估绑定split、STOP、denominator；项目仅有offline/tool/teacher/separate eval证据，不能升级成个人DAgger/PPO。

**诊断 / 证据**：先查 task/split/observation/action/STOP schema→expert/oracle或reward revision→policy/checkpoint/normalizer→collector policy hash、visited state和next state→oracle label或behavior log-prob/value/return→mask与denominator→ratio/clip/grad/KL→checkpoint save/load→matched eval protocol。BC loss低但rollout偏航优先查 state-distribution mismatch；DAgger变差查β、oracle/map revision、invalid/skipped/duplicate和aggregate污染；student forcing不收敛查 current-state target是否错位；reward升而SR不升查 reward hacking/STOP；ratio异常查 stale rollout/old log-prob；value爆炸查 terminated/truncated bootstrap。固定Habitat `0fb6f43`仍是单一`dones→masks`，双字段是目标合同。probe至少保留empty-mask拒绝、β `.75/.5625/.421875/.316406`、GAE `2.82504/1.9405/1`、PPO clip `1.2/-0.8`、terminal/truncation `1/10.9`；10/10只证明合同，不是benchmark。

**项目挂钩**：OpenPiVLA 的 action-to-text/full-chat CE、LoRA recipe 与 serialization/rollout lineage只能支持 offline supervision；Robot Harness 有 SFT trajectory、schema-aware reward 和 proxy eval，不能替代 fresh physical rollout/PPO；OPD 是 teacher generation/student CE/distillation，不是 env-state DAgger；UWM 是 offline finetune 后 separate rollout evaluation，不是 evaluation-to-training DAgger/RL；WAM 只有 CoffeePressButton failed traces 与 controller/horizon字段，没有完整 trainer/checkpoint/denominator。`muxi/embodied/` 中 ignored/third-party 的 DAgger/PPO 关键词、Git author、文件名、训练 loss 或 closed-loop eval 都不能证明候选人 ownership。

**追问树**：student forcing何时才接近DAgger？scheduled sampling为什么不是no-regret DAgger？BC action loss下降为何不等于SR/SPL提升？DAgger round最小immutable字段是什么？oracle label如何绑定map/navmesh revision？PPO old log-prob为何必须来自采样policy？ratio与clip异常如何区分stale rollout、advantage符号和mask错误？terminated与truncated如何影响GAE？reward升而SR不升如何查STOP、collision与denominator？DD-PPO的关键是多GPU还是fresh同步rollout？如何给五个项目各写一句不越界回答？

**易错点**：把 student rollout、recovery demos 或名为 `dagger` 的目录当成 DAgger；把 scheduled sampling当作oracle relabel；只背 PPO clip而漏 value/entropy/reward/return/log-prob；把 timeout和true terminal都写成done；把 reward当SPL；把官方 repo、第三方 checkout、Git author或字段名写成个人贡献；把 separate eval episode倒推成online training data；合并seen/unseen或隐藏无效动作/early stop分母。

**危险答案**：说“有失败轨迹就能做DAgger”“模型自己滚动就是on-policy”“PPO就是reward加clip”“train loss降了所以导航成功”“项目里有online/ppo/dagger脚本所以我实现了”，却不能给出 visited-state oracle、aggregate round、fresh behavior log-prob/value/return、termination/truncation、checkpoint/eval protocol 和 ownership证据。

**来源**：[1][2][3][4][5][6][7][8][9]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-018 Navigation BC / DAgger / RL / Exposure Bias Knowledge](../knowledge/vol_06_per018_navigation_bc_dagger_rl_exposure_bias.html)：BC、forcing、exposure bias、DAgger四门、GAE/PPO/DD-PPO、typed manifest、诊断、10 probes、两档回答与五项目边界。
2. [PER-018 Source Freeze](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html)：7份固定版本 primary PDF、4个 official repositories、27个代码文件、10个 deterministic probes 与本地五项目 direct audit。
3. Ross, Gordon & Bagnell, [DAgger](https://arxiv.org/abs/1011.0686), AISTATS 2011；固定版本 `1011.0686v3`。
4. Bengio et al., [Scheduled Sampling](https://arxiv.org/abs/1506.03099), NeurIPS 2015；固定版本 `1506.03099v3`。
5. Anderson et al., [R2R](https://arxiv.org/abs/1711.07280), CVPR 2018；[Matterport3DSimulator](https://github.com/peteanderson80/Matterport3DSimulator/tree/589d091b111333f9e9f9d6cfd021b2eb68435925)。
6. Krantz et al., [VLN-CE](https://arxiv.org/abs/2004.02857)；[official code](https://github.com/jacobkrantz/VLN-CE/tree/729d141b2ee10628061ada74dd3a5b9f70faeba5)。
7. Schulman et al., [PPO](https://arxiv.org/abs/1707.06347) 与 [GAE](https://arxiv.org/abs/1506.02438)；Wijmans et al., [DD-PPO](https://arxiv.org/abs/1911.00357)。
8. [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [WAM](../evidence/projects/wam_claim_evidence_inventory.html) Claim–Evidence Inventories。
9. [PER-018 Independent Fact Review](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html)：7 PDF、10 official files、10 probes、8 local files与Habitat done-mask版本边界复核。
