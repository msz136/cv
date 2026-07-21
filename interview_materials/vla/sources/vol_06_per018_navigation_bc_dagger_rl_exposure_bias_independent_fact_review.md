# VOL 06 PER-018：Navigation BC、DAgger、RL 与 Exposure Bias 独立事实复核

> 状态：`independent_fact_review / VLA-PER-018 / paper_code_refetched / source_knowledge_card_reconciled / PASS_WITH_WARNING`  
> 审查日期：2026-07-20  
> 证据截止：2026-07-20  
> 范围：独立重新下载并哈希7份primary PDF，重新抓取并哈希4个fixed official repositories中的10个代表文件，重跑10个deterministic probes，复核source→knowledge→card与五项目truth boundary；不生成新题卡、不改变269张题卡的`unseen`状态、不启动PER-019、不创建coaching state。

## 问题（Question）

PER-018 source、knowledge 与 atomic card 对 BC、teacher/student forcing、scheduled sampling、DAgger、GAE/PPO/DD-PPO、termination/truncation 和项目真实性边界的表述，是否能被重新获取的 primary paper、fixed official code 与当前local-direct artifacts逐项支持？哪些内容是paper-exact、code-exact、工程综合或仍未验证？

## 1. 结论先行

1. **7/7 primary PDFs byte-identical**：重新下载的版本、bytes与SHA全部命中source freeze，合计96页；DAgger aggregate、Scheduled Sampling previous-input mismatch、R2R teacher/student forcing、VLN-CE `0.75^n/5,000/4 epochs`、DD-PPO同步去中心化与preemption、PPO ratio/clip、多epoch minibatch、GAE的\(\gamma\lambda\) advantage均可直接定位。
2. **10/10代表official files byte-identical**：VLN-CE 3个、Habitat-Lab 5个、R2R-EnvDrop 1个、Matterport R2R 1个文件全部命中source freeze SHA。VLN-CE code确实执行`p ** data_it`、expert/policy action mix、LMDB append和oracle-action inflection weighting；Habitat code确实保存action log-prob、计算GAE、PPO ratio/clip、value/entropy与grad statistics。
3. **R2R语境中的student forcing可以称online DAgger，但不能无条件泛化**：论文p7明确写“equivalent to an online version of DAgger / always sampling”，前提是target始终从agent当前pose到goal的shortest path重新计算。knowledge/card把general case继续要求current-state oracle label是正确收紧，不与论文冲突。
4. **Scheduled Sampling与DAgger仍须分开**：前者直接支持true/generated previous token curriculum；它不提供navigation oracle、immutable aggregate或no-regret身份。把`ε=0`叫always sampling是paper-exact，把任意always-sampling流程叫canonical DAgger则不成立。
5. **termination/truncation分离是本仓库的工程合同，不是pinned Habitat路径的code-exact事实**：固定commit `0fb6f43` 的`ppo_trainer.py`读取单一`dones`并生成`not_done_masks`，`rollout_storage.py`只消费`masks`；该路径没有显式`terminated/truncated`字段。知识页说“真正terminal切bootstrap、time-limit truncation通常保留bootstrap”是合理目标，但必须标为engineering requirement，不能说该官方代码已经实现。
6. **PPO完整loss是实现相关的**：PPO论文直接支持ratio、clipped surrogate和多epoch minibatch；pinned Habitat实现还包含clipped value、entropy、aux loss、可选VER importance coefficients与adaptive entropy。知识页的`-Lclip + value - entropy + aux`是教学综合，不是该commit逐项完全展开式。
7. **10/10 probes独立复算通过**；它们只验证identity、mask、schedule、GAE、clip和bootstrap反例，不是训练稳定性、论文benchmark或个人项目结果。
8. **五项目边界再次成立**：8个local-direct files重新哈希命中；定向关键词审查只发现UWM的separate rollout eval、OPD teacher rollout和Harness reward spec邻接事实，没有local navigation DAgger collector、visited-state oracle aggregate、fresh PPO behavior log-prob/value/return或matched result。ignored/third-party代码仍不能计入候选人ownership。

本页 verdict 为`PASS WITH WARNING`：public mechanism与source→knowledge→card对齐通过；pinned Habitat terminated/truncated差异、local runtime、ownership与真实口述仍为warning/pending。

## 2. Primary PDF 再获取与完整性

| Source | 再获取版本 | Pages / bytes | SHA-256 | 独立定位到的核心事实 |
| --- | --- | ---: | --- | --- |
| DAgger | `1011.0686v3` | 9 / 551,229 | `12B032CFD451B8ACE4B18145DBE24382D2CBE2EDA6B562331BC86799BBAAFD5E` | Algorithm 3.1：mixture policy、visited states、expert actions、aggregate、retrain |
| Scheduled Sampling | `1506.03099v3` | 9 / 283,137 | `9769DF7150C7686237A2E709FA4FC004BFA03636A8329C9C1FD5C60163CFB00C` | train用true previous token、inference用generated token、\(\epsilon_i\) curriculum与always sampling |
| R2R | `1711.07280v3` | 13 / 9,720,283 | `B7589865EE573D4753EE9E25BDC494CBBB199E6EC17D0A349091AED0FD86C420` | p7 teacher/student forcing；target从current pose到goal shortest path；online DAgger限定语境 |
| VLN-CE | `2004.02857v2` | 18 / 10,596,423 | `8C62871FFB3D266F38EE2FEA944583645F74DBE10AC85213AD536486C18CB1A3` | \(\beta=0.75^n\)、每阶段5,000 trajectories、4 IL epochs、inflection weighting |
| DD-PPO | `1911.00357v2` | 21 / 3,578,072 | `CB9A5B9C603A6EDDD95F6A8D17E946C46681506FD51302371FE67EE208AF6F2D` | distributed、decentralized、synchronous、straggler preemption与2.5B-step experiment |
| PPO | `1707.06347v2` | 12 / 2,923,532 | `E78FEADADBDBB0B601B3C2BCC81404722CD431A489B307545F9B7BEA1E8C4F5B` | old/new ratio、clipped surrogate、多epoch minibatch update |
| GAE | `1506.02438v6` | 14 / 1,798,117 | `5AA736CCF3517A1F36D0CA8146982E69BEAF9A2BDCCAC2AE324F780743BC045E` | TD residual、\(\sum_l(\gamma\lambda)^l\delta_{t+l}\)、bias/variance trade-off |

7个文件均重新从明确version URL获取；byte SHA与source freeze完全一致。PDF文本重新抽取96/96页；代表性公式与算法段可定位。此前150 DPI视觉检查证明可读，本轮不重复生成第二套图片，避免把重复渲染冒充额外事实证据。

## 3. Official Code 独立抽样

| Repo / file | Fixed commit | 再取SHA | 复核结果 |
| --- | --- | --- | --- |
| VLN-CE `dagger_trainer.py` | `729d141` | `924BE549FE25C31AE3E85AF95DE5A9414254323385883A1093EDC830497C0AD7` | `beta=p**data_it`；random gate选expert/policy action；LMDB从existing entries追加 |
| VLN-CE `recollection_dataset.py` | `729d141` | `61042AADE2CD06AB70D6B8F1B4FD0D19613FC3E0E70D2B6282632650B2EE3DC6` | prev/oracle action；oracle-action change位置生成inflection weights |
| VLN-CE `seq2seq_da.yaml` | `729d141` | `9376FA4E112D1844C5066E0E8FD6E4D07DD585EE590E3ECFFCB1FA2E1D300D44` | iterations=10、update_size=5000、p=.75、epochs=4 |
| Habitat `ppo.py` | `0fb6f43` | `639063D9ADC1AA8D2BFDD0054958177EDD362D90ED43CD2BE05C74A2436C3ECF` | log-prob ratio、clip、value、entropy、aux、grad/ratio stats |
| Habitat `rollout_storage.py` | `0fb6f43` | `914DCA269E640992B5B0343B5811B24110DCCF073B92AE7097F551388DF351B0` | rewards/value/action_log_probs/masks；reverse GAE/returns |
| Habitat `ppo_trainer.py` | `0fb6f43` | `3D092753BF3B0CA6273E0213316C9A66653EED8D519C9DF60F2104CA883FA169` | env `dones`→`not_done_masks`；未显式拆terminated/truncated |
| Habitat `ddppo.py` | `0fb6f43` | `20C91A45BA4F7F857A0EB938A3A404A33EE88F288BF45F41C1A17F3361EC0AFF` | distributed mean/variance、DDP wrapper、继承PPO |
| Habitat `ddppo_pointnav.yaml` | `0fb6f43` | `B8B443ACE3E48556E500260606B96390963A84ECDB1E23253918348BF9B3077A` | 2.5e9、clip=.2、GAE、γ=.99、τ=.95、sync_frac=.6 |
| R2R-EnvDrop `agent.py` | `6f938ab` | `13710C80CA462E68379E24CF0D347B8C1934ECD1085450A835C7C69C4CB2F565` | teacher/sample/argmax、CE、distance reward、value/entropy、policy gradient混合 |
| Matterport R2R `agent.py` | `589d091` | `CCE3492EDB2AD0A36CDAF750022052420F3615953DC2DD0CBA0DA26DD9C42F7C` | teacher/sample/argmax、CE、test时禁止teacher cheat |

10/10文件的bytes与source freeze记录一致。这个抽样覆盖关键机制路径，但不替代27文件的source ledger，也不证明任何本地复现或运行规模。

## 4. BC、Forcing 与 Scheduled Sampling 复核

BC教学目标写为：

$$
\mathcal L_{\mathrm{BC}}(	heta)=
-\frac{\sum_{b,t}m_{b,t}w_{b,t}\log\pi_\theta(a^*_{b,t}\mid o^E_{b,t},h^E_{b,t},c_b)}
{\sum_{b,t}m_{b,t}w_{b,t}+\varepsilon}.
$$

变量与映射：\(a^*\)是expert action，\(m\)是valid-action mask，\(w\)可表达inflection/sample weighting；R2R official code直接支持cross-entropy target，VLN-CE dataset支持oracle action与inflection weight。此式是对离散action trainer的安全教学综合，不是R2R论文逐字公式。empty denominator必须在公式外先gate；\(\varepsilon\)不能把空batch变成有效更新。

Scheduled Sampling的核心门为：

$$
a^{\mathrm{in}}_{t-1}=
\begin{cases}
a^*_{t-1},&z_t<\epsilon_i,\\
\hat a_{t-1},&z_t\ge\epsilon_i.
\end{cases}
$$

变量与映射：\(\epsilon_i\)控制true/generated previous input比例；paper直接支持从fully guided到mostly generated的curriculum。它没有定义navigation shortest-path oracle、round dataset或cross-round aggregation，因此knowledge/card说“Scheduled Sampling不自动等于DAgger”通过。

R2R的特殊点是target \(a_t^*\)始终根据agent当前pose重算。论文因此把student forcing称为online DAgger / always sampling。安全口述应说：“在R2R这个current-pose shortest-path oracle语境下等价；离开该语境必须重新检查oracle relabel和aggregation。”

## 5. DAgger Identity 与 VLN-CE 映射

$$
\pi_i=\beta_i\pi^*+(1-\beta_i)\hat\pi_i,
\qquad
D\leftarrow D\cup\{(s,\pi^*(s)):s\sim d_{\pi_i}\}.
$$

变量与映射：\(\pi^*\)为expert，\(\hat\pi_i\)为learner，\(d_{\pi_i}\)为实际visited-state distribution。DAgger Algorithm 3.1直接包含mixture、visited state expert action、dataset aggregate与retrain；VLN-CE code把`p ** data_it`映射到\(\beta_i\)，用`torch.where(rand < beta, expert, policy)`推进环境，并将trajectory追加到LMDB。

独立复核后的四门不变：

| Gate | Paper/code evidence | 不能用什么替代 |
| --- | --- | --- |
| rollout identity | mixture/current policy实际产生visited states | 文件名、旧demo、静态sample |
| oracle identity | visited state上的同revision expert action | 原expert path错位label、self label |
| aggregation identity | round append、episode/invalid/skipped/duplicate可追溯 | 无lineage拼接、recovery数据别名 |
| schedule/checkpoint | round、\(\beta_i\)、policy SHA、train config | “online”字样或最终loss |

VLN-CE的10×5,000是nominal config规模；paper还写6–10次collection取决于model/convergence。知识页把50,000标为nominal并要求扣除invalid/duplicate/early stop是正确边界，不能把配置乘法当实际有效trajectory denominator。

## 6. GAE、PPO 与 termination/truncation 差异

GAE的paper-exact主体为：

$$
\delta_t^V=r_t+\gamma V(s_{t+1})-V(s_t),
\qquad
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}=
\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l}^V.
$$

变量与映射：\(\delta_t^V\)是TD residual，\(\lambda\)控制多步bias/variance；Habitat storage用reverse recursion和`masks[step+1]`实现有限rollout版本。GAE paper讨论terminal absorbing state，但没有现代Gymnasium式terminated/truncated双字段。

PPO paper-exact主体为：

$$
r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)},
\qquad
L^{\mathrm{CLIP}}=\mathbb E_t
\left[\min\left(r_t\hat A_t,
\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\right)\right].
$$

变量与映射：old log-prob必须与采样action的behavior policy对齐；Habitat code以`exp(new_logp-buffer_logp)`求ratio，再计算clipped action loss、value loss、entropy、aux和grad statistics。knowledge页的total objective是教学层综合；pinned code还含可选VER importance coefficients、clipped value与adaptive entropy，不能把简式说成该commit逐行等价。

### 6.1 新确认的 pinned-code warning

`ppo_trainer.py`只接收env返回的`dones`，再构造：

```python
# Fixed Habitat-Lab path: one done flag becomes the bootstrap mask.
not_done_masks = torch.tensor([[not done] for done in dones])

# Rollout storage uses the same mask in TD and GAE recursion.
delta = reward + gamma * next_value * next_mask - value
gae = delta + gamma * tau * gae * next_mask
```

代码注释与结论：该路径没有显式`terminated`与`truncated`字段，因此不能证明time-limit truncation被正确bootstrap。PER-018中“true terminal切bootstrap、time-limit truncation通常保留bootstrap”保留为**engineering contract / failure gate**；若项目采用这个pinned path，必须另查env wrapper是否在进入`dones`前处理time-limit信息。

## 7. DD-PPO 与分布式边界

DD-PPO paper直接支持distributed、decentralized、synchronous、no-stale与straggler preemption。pinned code把DDP wrapper/跨worker mean-variance放在`ddppo.py`，PPO update放在父类，preemption orchestration位于trainer而不是这个短mix-in文件。配置的`sync_frac=.6`和`total_num_steps=2.5e9`是public recipe；不能由“本地多GPU”反推完成论文规模。

工程上仍应记录每worker collected steps、preemption、episode termination与global denominator；这是可复现性要求，不是DD-PPO论文保证每个本地系统自动拥有的artifact。

## 8. 10个 Deterministic Probes 独立重算

| Probe | 独立结果 | Verdict |
| --- | --- | --- |
| masked BC NLL | `-log(.8)=.2231435513142097` | PASS |
| empty mask | `gate=false`，明确拒绝 | PASS |
| exposure shift | expert `+1` 与model `-1`访问不同state | PASS |
| scheduled endpoints | `ε=1→teacher`，`ε=0→model` | PASS |
| DAgger beta | `.75,.5625,.421875,.31640625` | PASS |
| nominal aggregate | `10×5000=50000`，只作nominal | PASS |
| inflection | `0,0,1,1,2→1,1,3.2,1,3.2` | PASS |
| GAE reverse | `2.82504025,1.9405,1` | PASS |
| PPO clip | `(1.3,+1)→1.2`；`(.7,-1)→-.8` | PASS |
| terminal/truncation counterexample | `1` 与 `1+.99×10=10.9` | PASS |

结果为`10/10`。第10项是目标合同反例，不是pinned Habitat code已经拆分双字段的证明。

## 9. Source → Knowledge → Card Claim Reconciliation

| Claim cluster | Source | Knowledge | Card | Verdict / correction |
| --- | --- | --- | --- | --- |
| BC/teacher forcing | expert distribution、CE、current state/action | masked NLL、covariate shift | 30秒/机制答保留 | PASS；empty denominator须公式外gate |
| student forcing | R2R current-pose oracle与explicit online-DAgger表述 | general case增加oracle gate | 追问保留scope | PASS；R2R限定等价，非全局同义词 |
| scheduled sampling | true/generated previous input curriculum | 与DAgger分开 | 简答保留 | PASS |
| DAgger | Algorithm 3.1 + VLN-CE paper/code/config | 四门、manifest、nominal denominator | oracle/aggregate/β | PASS |
| GAE/PPO | paper公式 + Habitat storage/update | reward/value/logp/ratio/clip/entropy | fresh runtime门 | PASS WITH WARNING；total loss为教学综合 |
| terminated/truncated | engineering requirement + counterexample | 明确双字段与bootstrap | diagnosis追问 | PASS WITH WARNING；pinned trainer未显式实现 |
| DD-PPO | paper sync/decentralized/preemption + code/config | worker/denominator contract | “不等于多GPU” | PASS |
| project mapping | inventories + 8 local files | 五项目truth table | 五项目安全回答 | PASS WITH WARNING；local runtime/ownership缺失 |

本轮没有发现必须重写30秒答案的错误。面试时新增一句版本限定最稳妥：“terminated/truncated分离是我要求系统补齐的合同，固定Habitat路径本身仍只有done mask。”

## 10. Local-direct 再哈希与 Truth Boundary

| Local artifact | SHA重新命中 | 直接支持 | 仍不能升级 |
| --- | --- | --- | --- |
| OpenPiVLA `formal_train.py` | `51B67D...CC6F94` | action JSON/full-chat CE、LoRA trainer | navigation DAgger/PPO、formal closed-loop result |
| Harness `prepare_sft_data.py` | `AF75E0...85589` | SFT trajectory/split | physical navigation BC |
| Harness `prepare_grpo_data.py` | `EAA413...28250` | reward schema/proxy weights | trainer、fresh rollout、PPO/online GRPO、robot success |
| UWM finetune launcher | `E5B6DC...9D92` | offline finetune recipe | oracle/reward update、checkpoint content |
| UWM rollout eval | `05E912...F3943` | separate env rollout/eval loop | eval episode进入online update |
| OPD root trainer | `BF9120...D8D9` | teacher generation、student CE/distillation | env-state DAgger、navigation RL |
| WAM base manifest | `63A518...33A86` | matched protocol字段、`success=false` | trainer、checkpoint binary、denominator |
| WAM trained manifest | `809AE4...55CC` | trained-side失败trace引用 | BC/RL uplift或checkpoint因果 |

六个代码/launcher文件的定向关键词复核只发现：UWM `rollout_eval`执行separate evaluation；OPD使用teacher rollout/logits；Harness生成reward spec。没有`old_log_prob/compute_returns/GAE/PPO`训练链，也没有navigation visited-state oracle aggregate。WAM两份manifest仍是single-task failed diagnostic。结论仍为“当前检查范围内未绑定”，不是对未同步远端或历史分支的绝对不存在声明。

## 11. 审查状态与下一步

本次独立再获取、哈希、paper/code定位、10 probes、local rehash与source→knowledge→card reconciliation均完成。PER-018 public facts可从`WARN`提升为`independent_fact_reviewed / PASS WITH WARNING`，但题卡仍保持`unseen`，整个节点仍不能升级为drilled/done。

仍开放：

- pinned Habitat path的terminated/truncated处理需要项目级wrapper或新实现证据；
- local navigation oracle/DAgger rounds或fresh PPO rollout/checkpoint/eval bundle缺失；
- 五项目逐文件候选人ownership待本人确认；
- 没有真实口述，不创建coaching state。

下一 bounded slice优先进行一题真实口述；若用户暂不练习，可再选择VOL 04 Audit C/D独立复核，不启动PER-019。

## References

1. [PER-018 Source Freeze](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html)。
2. [PER-018 Knowledge](../knowledge/vol_06_per018_navigation_bc_dagger_rl_exposure_bias.html)。
3. [PER-018 Atomic Card](../questions/vol_06_per018.html)。
4. Ross, Gordon & Bagnell, [DAgger](https://arxiv.org/abs/1011.0686), AISTATS 2011。
5. Bengio et al., [Scheduled Sampling](https://arxiv.org/abs/1506.03099), NeurIPS 2015。
6. Anderson et al., [R2R](https://arxiv.org/abs/1711.07280), CVPR 2018。
7. Krantz et al., [VLN-CE](https://arxiv.org/abs/2004.02857)；[official code@729d141](https://github.com/jacobkrantz/VLN-CE/tree/729d141b2ee10628061ada74dd3a5b9f70faeba5)。
8. Schulman et al., [PPO](https://arxiv.org/abs/1707.06347) 与 [GAE](https://arxiv.org/abs/1506.02438)。
9. Wijmans et al., [DD-PPO](https://arxiv.org/abs/1911.00357)；[Habitat-Lab@0fb6f43](https://github.com/facebookresearch/habitat-lab/tree/0fb6f43ffe806a8088a171b036336c093bcf604e)。
10. [R2R-EnvDrop@6f938ab](https://github.com/airsplay/R2R-EnvDrop/tree/6f938abcf2db999c0118c7e548d8357ab8f006db) 与 [Matterport3DSimulator@589d091](https://github.com/peteanderson80/Matterport3DSimulator/tree/589d091b111333f9e9f9d6cfd021b2eb68435925)。
11. [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [WAM](../evidence/projects/wam_claim_evidence_inventory.html) Claim–Evidence Inventories。
