# VOL 06 PER-018 Source Freeze：Navigation BC、DAgger、RL 与 Exposure Bias

> 状态：`source_frozen / VLA-PER-018 / primary_official_checked / independent_fact_reviewed / navigation_training_contract / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本 source slice 只冻结 navigation behavior cloning、teacher/student forcing、scheduled sampling、DAgger、GAE、PPO/DD-PPO、训练—评估身份与五项目真实性边界；不生成 knowledge/card，不修改 268 张题卡的 mastery，不创建 coaching state，也不重写 VOL 02 的通用 IL/RL、PER-004 的任务指标、PER-005 的 policy architecture、PER-017 的 exploration 或 PER-019 的完整评估节点。

## 问题（Question）

VLN/ObjectNav/PointGoal 策略训练中，离线 behavior cloning、teacher forcing、student forcing、scheduled sampling、DAgger 与 RL/PPO 到底改变了什么数据分布、监督信号和优化目标？怎样冻结 oracle、reward、rollout、stop、termination、checkpoint 与 metric contract，避免把 recovery data、离线 action loss、闭环 evaluation 或代码关键词误写成已实现 DAgger/PPO？

## 1. 结论先行

1. **BC 是 expert-distribution 上的监督学习**：训练数据由 expert trajectory 冻结，优化 action negative log-likelihood 或回归 loss；它不自动覆盖策略犯错后访问的 state。
2. **Teacher forcing 与 student forcing 改的是训练时访问分布**：teacher forcing 执行 expert/ground-truth action；student forcing 执行 policy action，再从当前 state 计算 target。R2R 明确把后者写成 online DAgger / always-sampling 的对应形式，但“模型自己滚动”仍不充分：必须有 current-state oracle label 与 aggregation contract。
3. **Exposure bias 是 train/inference history mismatch**：scheduled sampling 用概率在 ground-truth previous token/action 与 model output 间切换；它与 DAgger 都改变访问分布，但 DAgger 还要求在策略访问 state 上查询 expert 并聚合各轮数据。
4. **DAgger 不是 recovery 数据的别名**：最低身份是 `current policy rollout → expert query at visited state → append immutable round → train on aggregate → decay/record β`。只有离线 recovery demonstrations、数据增强或 student rollout 而无 oracle relabel，不能称 canonical DAgger。
5. **RL/PPO 优化 return，不是 action label**：最低 runtime 是 fresh policy rollout、reward/done/truncation、behavior log-prob、value/return/advantage、policy/checkpoint revision与更新日志。PPO clip 只约束 surrogate term，不能替代 rollout freshness、reward validity、value/entropy项或安全保证。
6. **导航训练必须带 protocol identity**：scene/split/episode、observation/action/stop、oracle、reward、horizon、termination/truncation、simulator/controller、seed、policy/value checkpoint、normalizer与 metric denominator 缺一不可；train loss 下降不等于 val-unseen、closed-loop 或真实机器人提升。
7. 本轮冻结 **7 份明确版本 primary PDF / 96 页**、**4 个 official repositories / 27 个 fixed files**、**10 个 deterministic probes**、五份 canonical project inventories 与八个 local-direct files。PDF 全部有 `%PDF`、尾部 `%%EOF`、全文可抽取；7 张代表页在 150 DPI 下视觉可读；probe 为 `10/10`。
8. 五项目当前都没有可归入候选人的 local-direct navigation DAgger/PPO runtime。OpenPiVLA、UWM、Robot Harness、OPD、WAM 分别只有 supervised text/action、offline finetune、tool reward schema、text-teacher rollout 或失败 evaluation trace 等邻接证据；它们不能自动升级为 navigation on-policy training、oracle aggregation、reward improvement 或个人 ownership。

## 2. Primary Paper 冻结矩阵

| ID | Primary source | 固定版本 / 完整性 | 支持的 claim | 不支持的 claim |
| --- | --- | --- | --- | --- |
| P1 | Ross, Gordon & Bagnell, [DAgger](https://arxiv.org/pdf/1011.0686v3) | `1011.0686v3`；9页；551,229 bytes；SHA `12B032CFD451B8ACE4B18145DBE24382D2CBE2EDA6B562331BC86799BBAAFD5E` | current-policy visited states、expert labels、aggregate dataset、mixture `β_i` 与 no-regret reduction | 任意 recovery dataset 都是 DAgger；无需在线 expert/oracle |
| P2 | Bengio et al., [Scheduled Sampling](https://arxiv.org/pdf/1506.03099v3) | `1506.03099v3`；9页；283,137 bytes；SHA `9769DF7150C7686237A2E709FA4FC004BFA03636A8329C9C1FD5C60163CFB00C` | train/inference previous-token mismatch、teacher→model curriculum | navigation oracle、DAgger aggregation 或闭环 success |
| P3 | Anderson et al., [R2R / Matterport3D Simulator](https://arxiv.org/pdf/1711.07280v3) | `1711.07280v3`；13页；9,720,283 bytes；SHA `B7589865EE573D4753EE9E25BDC494CBBB199E6EC17D0A349091AED0FD86C420` | teacher-forcing/student-forcing、current-pose shortest-path target、R2R train/val-seen/val-unseen语境 | continuous low-level control、真实机器人部署、跨协议指标可比 |
| P4 | Krantz et al., [VLN-CE](https://arxiv.org/pdf/2004.02857v2) | `2004.02857v2`；18页；10,596,423 bytes；SHA `8C62871FFB3D266F38EE2FEA944583645F74DBE10AC85213AD536486C18CB1A3` | continuous environment DAgger、`β=0.75^n`、5k trajectories/round、4 IL epochs、inflection weight 与 VLN metrics | 本地复现、任意 task 的超参最优性、DAgger 自动解决 sim-to-real |
| P5 | Wijmans et al., [DD-PPO](https://arxiv.org/pdf/1911.00357v2) | `1911.00357v2`；21页；3,578,072 bytes；SHA `CB9A5B9C603A6EDDD95F6A8D17E946C46681506FD51302371FE67EE208AF6F2D` | decentralized synchronous PPO、rollout straggler preemption、PointGoal scale与 freshness语境 | “分布式”自动带来样本效率/泛化；任意本地 PPO 已复现 2.5B frame result |
| P6 | Schulman et al., [PPO](https://arxiv.org/pdf/1707.06347v2) | `1707.06347v2`；12页；2,923,532 bytes；SHA `E78FEADADBDBB0B601B3C2BCC81404722CD431A489B307545F9B7BEA1E8C4F5B` | old/new policy ratio、clipped surrogate、多 epoch minibatch update | clip 是严格 trust region、安全边界或完整 trainer objective |
| P7 | Schulman et al., [GAE](https://arxiv.org/pdf/1506.02438v6) | `1506.02438v6`；14页；1,798,117 bytes；SHA `5AA736CCF3517A1F36D0CA8146982E69BEAF9A2BDCCAC2AE324F780743BC045E` | TD residual、`γλ` 加权 advantage、bias/variance trade-off | 不区分 termination/truncation；value estimate正确性自动成立 |

完整性检查：7/7 文件以 `%PDF-` 开始，末 2 KiB 内含 `%%EOF`；pypdf 读取 96/96 页且无空白抽取页。代表页为 DAgger p4、Scheduled Sampling p3、R2R p7、VLN-CE p11、DD-PPO p4、PPO p3、GAE p4；均以 150 DPI 渲染，标题、正文、公式、算法框和表格可读。视觉可读只证明文档没有明显损坏，不等于对所有实验数字做独立复现。

## 3. Official Repository 冻结矩阵

| Repo | 固定 revision / commit date | License | 本轮读取 | 主要用途 |
| --- | --- | --- | ---: | --- |
| [jacobkrantz/VLN-CE](https://github.com/jacobkrantz/VLN-CE/tree/729d141b2ee10628061ada74dd3a5b9f70faeba5) | `729d141b2ee10628061ada74dd3a5b9f70faeba5`；2025-01-07 | MIT | 8 files | DAgger `p^iteration`、LMDB aggregation、oracle action、inflection weighting、DD-PPO extension |
| [facebookresearch/habitat-lab](https://github.com/facebookresearch/habitat-lab/tree/0fb6f43ffe806a8088a171b036336c093bcf604e) | `0fb6f43ffe806a8088a171b036336c093bcf604e`；2026-05-07 | MIT | 7 files | PPO ratio/clip/value/entropy、rollout returns/GAE、DDPPO与 PointNav config |
| [airsplay/R2R-EnvDrop](https://github.com/airsplay/R2R-EnvDrop/tree/6f938abcf2db999c0118c7e548d8357ab8f006db) | `6f938abcf2db999c0118c7e548d8357ab8f006db`；2021-10-23 | MIT | 6 files | R2R teacher/sample feedback、ML+RL混合、reward/value/entropy、env/eval |
| [peteanderson80/Matterport3DSimulator](https://github.com/peteanderson80/Matterport3DSimulator/tree/589d091b111333f9e9f9d6cfd021b2eb68435925) | `589d091b111333f9e9f9d6cfd021b2eb68435925`；2021-09-08 | MIT | 6 files | 原始 R2R teacher/argmax/sample feedback、CE trainer、env与 scorer |

四份 LICENSE 都是 MIT，但只覆盖各仓库中相应代码/文档；Matterport3D/R2R/VLN-CE 数据、预训练权重、依赖与第三方资产可能有独立条款，不能把 repo license 外推到所有 dataset/model artifacts。

## 4. Official File Ledger（27 files）

### 4.1 VLN-CE @ `729d141`

| File | bytes / lines | SHA-256 | 直接读取到 |
| --- | ---: | --- | --- |
| `LICENSE` | 1,124 / 23 | `C7C9E93E64F244505D84BA6B0F1D28AB3BD9492B70349727F0F4D0CC4D691200` | MIT 与 copyright |
| `README.md` | 16,460 / 293 | `33C547D6D6FA8A7DECA433C5E441894AAD72D676DFCA152FEA0CD4EF80B9A41C` | installation/data/checkpoint入口与引用 |
| `vlnce_baselines/dagger_trainer.py` | 21,716 / 611 | `924BE549FE25C31AE3E85AF95DE5A9414254323385883A1093EDC830497C0AD7` | `β=p^data_it`、oracle/policy action mix、LMDB round、action/aux loss |
| `vlnce_baselines/common/recollection_dataset.py` | 9,420 / 273 | `61042AADE2CD06AB70D6B8F1B4FD0D19613FC3E0E70D2B6282632650B2EE3DC6` | episode trajectory、prev/oracle action与 inflection weights |
| `vlnce_baselines/common/rollout_storage.py` | 10,602 / 289 | `EF57F404434C4C55F2AF3B904E4FC3C912DAD059BEFA3CFB679C8D88FF28C569` | recurrent rollout fields/returns storage |
| `vlnce_baselines/common/ddppo_alg.py` | 5,532 / 150 | `206F93983D45A34D9E4840B0291BFACC2EBE35FD04618D15F92502F5807B0EC5` | WDDPPO advantage、ratio、clip、value/entropy项 |
| `vlnce_baselines/config/r2r_baselines/seq2seq_da.yaml` | 630 / 28 | `9376FA4E112D1844C5066E0E8FD6E4D07DD585EE590E3ECFFCB1FA2E1D300D44` | 10 rounds、5k update、`p=.75`、4 epochs |
| `vlnce_baselines/models/policy.py` | 1,628 / 59 | `876AB141702F8FA6DC88020ECADFD2662A7CC76923A582ACC7850A04D6BF17F4` | policy registration与 action distribution入口 |

### 4.2 Habitat-Lab @ `0fb6f43`

| File | bytes / lines | SHA-256 | 直接读取到 |
| --- | ---: | --- | --- |
| `LICENSE` | 1,092 / 22 | `2D4C3D00D67067461412A2D9A2F3F8B7B9CDA62B3DB501E4B6844CCF35C949AA` | MIT 与 Meta copyright |
| `habitat-baselines/README.md` | 16,525 / 237 | `676F8DF0A87DBF18E817A6F98E447EFE00684C196A97192E45B23170AF409445` | baseline/config/run入口 |
| `.../rl/ppo/ppo.py` | 12,743 / 385 | `639063D9ADC1AA8D2BFDD0054958177EDD362D90ED43CD2BE05C74A2436C3ECF` | normalized advantage、ratio/clip、value/entropy、grad norm |
| `.../common/rollout_storage.py` | 9,557 / 276 | `914DCA269E640992B5B0343B5811B24110DCCF073B92AE7097F551388DF351B0` | reward/mask/value/return 与 GAE reverse recursion |
| `.../rl/ddppo/algo/ddppo.py` | 5,447 / 158 | `20C91A45BA4F7F857A0EB938A3A404A33EE88F288BF45F41C1A17F3361EC0AFF` | distributed mean/variance、DDP wrapper与 PPO inheritance |
| `.../rl/ppo/ppo_trainer.py` | 33,390 / 912 | `3D092753BF3B0CA6273E0213316C9A66653EED8D519C9DF60F2104CA883FA169` | env sampling、rollout/update/eval orchestration |
| `.../config/pointnav/ddppo_pointnav.yaml` | 1,984 / 77 | `B8B443ACE3E48556E500260606B96390963A84ECDB1E23253918348BF9B3077A` | `2.5e9` steps、clip .2、GAE、γ .99、τ .95、sync .6 |

### 4.3 R2R-EnvDrop @ `6f938ab`

| File | bytes / lines | SHA-256 | 直接读取到 |
| --- | ---: | --- | --- |
| `LICENSE` | 1,110 / 22 | `3B28E3FB157F4975938969424094221A9DBF4BB7B1234F623E11A93A8B4AE8D6` | MIT |
| `README.md` | 4,868 / 99 | `EF69FB7EEA0DB7D66865E41A736FB1C55B666BDF6A2D3F069897528512640577` | R2R/EnvDrop运行与模型入口 |
| `r2r_src/agent.py` | 38,389 / 858 | `13710C80CA462E68379E24CF0D347B8C1934ECD1085450A835C7C69C4CB2F565` | teacher/sample/argmax、CE target、distance reward、value/entropy与 RL loss |
| `r2r_src/train.py` | 18,682 / 473 | `604B35E3F97AE7043EEFAC11E10A05918E8F1907F0F08363AF5534F2A13EA376` | feedback method、GT/aug mix、ML weight、train/validation loop |
| `r2r_src/env.py` | 14,181 / 337 | `D799E17F9DCEF2E169C91F7F3D547E1F78953B192917D2AE6FF73DCD26423380` | state/candidate/teacher/env contract |
| `r2r_src/eval.py` | 6,773 / 168 | `6EED076F81BA5C510793FC3E684110F2992A8E4AEFCFAF0F5FFEF247EFC643C4` | trajectory scorer与 split evaluation |

### 4.4 Matterport3DSimulator @ `589d091`

| File | bytes / lines | SHA-256 | 直接读取到 |
| --- | ---: | --- | --- |
| `LICENSE` | 1,197 / 23 | `95D4B81BA57FC88AAA4568685F96A58C73CB2CE83DB0CD057CA365AF9545F1CB` | MIT |
| `tasks/R2R/README.md` | 2,939 / 76 | `B0996D95562D19D7AFE4548062C99E85EAEAC7E084393282368647A26B859E90` | 原始 baseline运行入口 |
| `tasks/R2R/agent.py` | 11,955 / 321 | `CCE3492EDB2AD0A36CDAF750022052420F3615953DC2DD0CBA0DA26DD9C42F7C` | teacher/sample/argmax、CE与 test-time no-cheat gate |
| `tasks/R2R/train.py` | 6,637 / 165 | `F472A6AA74A1CEFDB2316B51FF745D53008CA4E185D7C65013D028217C0B19F9` | teacher/sample feedback、train/val seen/unseen loop |
| `tasks/R2R/env.py` | 9,855 / 228 | `E8CAA75EC10A76B76A353CCF04FA3B7556B46BCBB4F7310CF7A1C47B8121E2FE` | R2R observation/teacher/state transition |
| `tasks/R2R/eval.py` | 6,022 / 150 | `78E2867DA1C79BA7D2657091FF385CFF622BBF85F07A72A4635A62B2F38E321C` | path length/error/success scorer |

## 5. 节点边界与依赖

| Node | 已负责 | PER-018 只消费/新增 |
| --- | --- | --- |
| VOL 02 IL/RL | DAgger/GAE/PPO通用公式、offline RL/post-training | 消费已独立复核机制；新增 navigation data/oracle/stop/rollout identity |
| PER-004 | VLN/ObjectNav task、episode、action/stop与 SR/SPL/nDTW | 冻结训练数据和 eval split必须对齐 task protocol |
| PER-005 | map-free/map-based policy、planner/controller architecture | 不重复 architecture；只定义 update object与训练 runtime |
| PER-016 | localization/map frame | state/oracle/action label必须绑定 frame/map revision |
| PER-017 | belief/memory/frontier exploration | exploration rollout不自动等于 RL rollout；memory reset仍是训练输入合同 |
| PER-019 | 完整 navigation evaluation、collision/stop、CI/failure taxonomy | 本页只冻结训练所需 metric/denominator identity，不宣称评估节点完成 |

## 6. Typed Navigation Training Manifest

任何 `BC / DAgger / PPO improved navigation` claim 至少绑定以下身份：

| Layer | Required fields | 缺失时的结论 |
| --- | --- | --- |
| task/data | task、dataset revision/license、scene split、episode IDs、observation/action/stop schema、frame/unit、horizon | 不知道在学什么任务或是否泄漏 |
| expert/oracle | expert type、shortest-path/teacher policy revision、map/navmesh revision、query availability、invalid action rule | 不能确认 label 或 DAgger 身份 |
| policy | architecture/config、checkpoint parent/hash、normalizer/tokenizer、memory reset、action distribution | loss/result无法绑定模型 |
| rollout | collector code SHA、policy revision、behavior log-prob、env/simulator/controller revision、seed、timestamp、termination/truncation | 不能确认 on-policy/freshness |
| reward/value | reward components/scale、success/stop predicate、discount、bootstrap rule、value checkpoint | 不能确认 RL objective/credit assignment |
| update | algorithm、loss mask/denominator、optimizer、grad norm、dataset round或 PPO epoch/minibatch、KL/clip stats | 不能确认实际更新了什么 |
| result | checkpoint SHA、split、episode denominator、SR/SPL/nDTW/collision、raw per-episode trace、failure taxonomy | 不能从 train loss 推导 closed-loop能力 |
| ownership | upstream/local diff、author/reviewer、run operator、artifact custodian | 不能把上游或工具生成代码写成个人创新 |

推荐 immutable lineage：

```text
task_manifest_sha + dataset/env revision + oracle/reward revision
-> collector policy_sha / behavior_policy_sha
-> round_or_rollout_id + raw trajectories
-> update_config_sha + loss/ratio/return logs
-> checkpoint_sha + eval_protocol_sha
-> per_episode_results + summary + ownership ledger
```

## 7. Behavior Cloning 与 Teacher Forcing

令 (D_E) 为 expert trajectory 构成的离线数据集，(m_{b,t}) 为有效 action mask，(w_{b,t}) 为 inflection/class/sample weight，(pi_\theta(a\mid o,h,c)) 为策略在 observation、history 与 instruction/goal 条件下的 action distribution。离散 action BC 可写为：

$$
\mathcal{L}_{\mathrm{BC}}(\theta)
=-
\frac{\sum_{b,t}m_{b,t}w_{b,t}\log \pi_\theta(a^*_{b,t}\mid o^E_{b,t},h^E_{b,t},c_b)}
{\sum_{b,t}m_{b,t}w_{b,t}}
$$

变量与实现映射：(a^*) 是 expert/oracle action；上标 (E) 表示 state/history来自 expert trajectory。R2R `agent.py` 以 cross entropy 对 teacher action训练；VLN-CE dataset同时返回 oracle action与 inflection weight。分母为0、oracle action为`-1`、padding/STOP语义未知时应 fail closed，不能返回0 loss并声称训练成功。

Teacher forcing执行 expert action，因此后续 observation 继续位于 expert 轨迹；它的优点是 label稳定、训练便宜，缺点是部署时一个错误会把策略带到训练数据外。单步 accuracy 或 CE 下降不能证明 policy能恢复。

## 8. Student Forcing、Scheduled Sampling 与 Exposure Bias

令 (\epsilon_i) 表示第 (i) 个训练阶段使用 ground-truth previous action/token 的概率：

$$
a^{\mathrm{in}}_{t-1}=
\begin{cases}
a^*_{t-1}, & z_t<\epsilon_i,\\
\hat a_{t-1}\sim\pi_\theta, & z_t\ge\epsilon_i,
\end{cases}
\qquad z_t\sim\mathrm{Uniform}(0,1)
$$

变量与实现映射：`ε=1` 是完整 teacher forcing，`ε=0` 是 always sampling/student forcing。Scheduled Sampling论文把 `ε` 作为 curriculum；R2R p7在当前 pose重新计算 shortest-path target，并把 student forcing解释为 online DAgger / always sampling。若只是把 model token喂回去，却仍使用原 expert path上错位的 label，则不能直接获得 DAgger 的 current-state expert guarantee。

Exposure bias至少分三层：

1. **history exposure**：训练读 expert previous action，部署读 model action；
2. **state exposure**：错误动作改变 pose/observation，后续 state离开 expert distribution；
3. **termination exposure**：训练 trajectory长度/STOP固定，部署的错误 STOP、loop、collision 改变 episode denominator。

## 9. DAgger Identity 与 VLN-CE 实现

第 (i) 轮 mixture policy 为：

$$
\pi_i=\beta_i\pi^*+(1-\beta_i)\hat\pi_i,
\qquad
D\leftarrow D\cup\{(s,\pi^*(s)):s\sim d_{\pi_i}\}
$$

变量与实现映射：(\pi^*) 是 expert/oracle，(hat\pi_i) 是当前 learner，(d_{\pi_i}) 是本轮实际访问 state分布；新 state经 expert relabel后追加到 aggregate dataset。VLN-CE `dagger_trainer.py` 使用 `β=p^data_it`，`seq2seq_da.yaml` 冻结 `p=.75`、10 iterations、每轮5,000 trajectories、4 epochs。代码还对 oracle action变化位置加 inflection weight，并跳过 invalid expert action。

DAgger 的 four gates：

1. rollout确由声明的 current/mixture policy产生；
2. visited state有同一 task/map/oracle revision 的 expert label；
3. 每轮 trajectory不可变且进入 aggregate dataset，round/episode可追溯；
4. policy/checkpoint、`β_i`、invalid/skipped、duplicate与 early termination denominator全部记录。

只有“收集失败轨迹再微调”可能是 recovery BC；只有“student rollout”但 teacher没有在 visited state标注，可能是 self-training/distillation；只有 DAgger 数据文件名而没有 collector/oracle manifest，也不能证明 DAgger runtime。

## 10. Return、GAE、PPO 与 DD-PPO

令 (r_t) 为 reward，(V_\phi(s_t)) 为 value，(d_t^{term}) 为真正 terminal mask。TD residual与 GAE为：

$$
\delta_t=r_t+\gamma(1-d_t^{term})V_\phi(s_{t+1})-V_\phi(s_t),
\qquad
\hat A_t^{\mathrm{GAE}(\gamma,\lambda)}
=\sum_{l=0}^{T-t-1}(\gamma\lambda)^l\delta_{t+l}
$$

变量与实现映射：(gamma) 是 discount，(lambda) 控制 bias/variance；Habitat rollout storage按逆时间计算 returns/GAE。time-limit truncation通常仍需 bootstrap，真正 terminal才把 next value切掉；环境应分别记录 terminated/truncated，而不是一个含糊的`done`。独立复核确认固定commit `0fb6f43` 的`ppo_trainer.py`仍把单一`dones`转成`not_done_masks`，因此双字段分离是本仓库的工程合同，不是该pinned path已经实现的code-exact事实。

PPO old/new policy ratio与 clipped surrogate为：

$$
r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)},
\qquad
L^{CLIP}(\theta)=\mathbb{E}_t\left[
\min\!\left(r_t\hat A_t,
\mathrm{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\right)
\right]
$$

变量与实现映射：behavior log-prob必须来自采样该 action 的 `θ_old`；Habitat `ppo.py`计算 ratio、clipped action loss、value loss、entropy与 grad norm。若 rollout policy/checkpoint hash与 log-prob不一致，或在多轮更新后继续把旧数据叫 fresh on-policy，ratio已失去身份。

典型 trainer还包含：

$$
\mathcal{L}_{\mathrm{PPO-total}}
=-L^{CLIP}+c_v\mathcal{L}_{value}-c_H\mathcal{H}(\pi_\theta)+\mathcal{L}_{aux}
$$

变量与实现映射：(c_v) 和 (c_H) 分别是 value/entropy系数；VLN-CE WDDPPO还拆出 pano/offset/distance entropy。PPO paper的 clip公式不是完整 loss；漏掉 value target、entropy、aux、mask/denominator与 gradient statistic时，不能用一个 surrogate公式声称复现。

DD-PPO 的关键不是“多GPU”三个字，而是同步、去中心化、无参数服务器的 fresh rollout/update；straggler preemption必须记录每个 worker实际贡献的 step与 episode denominator。Habitat config中的 `2.5e9`、sync fraction `.6` 是 frozen official recipe事实，不是本地项目运行规模。

## 11. 方法身份对比

| Method | 访问 state | target/signal | 是否聚合 | 最小 runtime | 常见误写 |
| --- | --- | --- | --- | --- | --- |
| offline BC | fixed expert trajectory | expert action | fixed dataset | dataset+mask+loss+checkpoint | action loss低=闭环好 |
| teacher forcing | expert action产生后续 state | next expert action | 可固定 | ordered trajectory | 没有 exposure bias |
| student forcing | policy action产生后续 state | current-state target | 视实现 | env rollout+target rule | model rollout自动等于 DAgger |
| scheduled sampling | expert/model previous input混合 | sequence label | 通常不是跨轮 aggregate | `ε` schedule+sample trace | 等同 no-regret DAgger |
| DAgger | mixture/current policy state | expert query at visited state | 是 | round collector+oracle+immutable aggregate | recovery demos/文件名=DAgger |
| PPO | fresh current/old-policy rollout | reward/return/advantage | rollout buffer，不是 expert dataset | reward+old logp+value+returns+update | 有reward或GRPO名=PPO |
| DD-PPO | 多worker fresh rollout | 同 PPO + synchronized gradient | distributed rollout | worker/step/preemption/all-reduce ledger | GPU多=复现论文规模 |

## 12. Training ↔ Evaluation Contract

训练与评估至少固定：

- dataset/scene split：train、val-seen、val-unseen、test不能混用；early stopping选择规则单独记录；
- episode：instruction/goal、start/goal、scene、oracle/path revision、seed/init、horizon；
- observation：camera/depth/GPS/compass/proprio、resize、normalization、frame与age；
- action：discrete/continuous、axis/unit、STOP、collision/no-op、action repeat/controller；
- rollout：policy checkpoint、memory reset、determinism、replan/action chunk、termination/truncation；
- reward：distance-progress、success、slack、collision/stop等组件及尺度；reward shaping不能替代 SR/SPL；
- result：episode denominator、lost/crash/timeout是否计失败、SR/SPL/nDTW与 confidence interval、raw trajectory。

R2R teacher/student forcing表格只在其图导航、split与 scorer下成立；VLN-CE DAgger只在continuous environment与其oracle/config下成立；DD-PPO的PointGoal规模结果也不能外推到VLN、ObjectNav或真实机器人。

## 13. First-divergence Failure Diagnosis

| 症状 | first divergence | 首查 artifact | 不应先做 |
| --- | --- | --- | --- |
| BC loss低、rollout立刻偏航 | expert/model state distribution | episode pose/action trace、teacher/student state coverage | 只继续降train loss |
| DAgger轮次越多越差 | oracle/map revision、β、aggregate污染 | round manifest、invalid/skipped、duplicate、oracle query log | 把所有历史LMDB无条件拼接 |
| student forcing不收敛 | current-state target错位或初始policy过弱 | executed action、next state、recomputed target三联 | 改名scheduled sampling |
| PPO reward升、SR不升 | reward hacking/scale/STOP mismatch | reward component、success predicate、raw episode | 把reward当SPL |
| PPO ratio/clip异常 | stale rollout或old log-prob错 | policy hash、collector/update timestamps、ratio histogram | 只调clip epsilon |
| value loss爆炸 | return/terminal/bootstrap错 | reward、terminated/truncated、Vnext、GAE trace | 先换更大backbone |
| DD-PPO结果不可复现 | worker/preemption/step denominator | worker ledger、sync fraction、seed、checkpoint | 只报GPU数和wall time |
| val-seen好、val-unseen差 | scene/instruction overfit | split manifest、duplicate/leakage、per-scene failure | 合并seen/unseen均值 |

诊断顺序固定为：task/split/schema → expert/oracle/reward identity → policy/checkpoint/normalizer → collector state/action/stop → label/log-prob/value/return → mask/denominator → optimizer/grad/ratio → checkpoint save/load → eval protocol/result。不要从最终 success反推中间合同正确。

## 14. Fail-closed Navigation Training 伪代码

```python
def train_navigation(run, manifests, policy, expert=None, value=None):
    # 1. Freeze task/data/env/policy identity before reading a sample or rollout.
    assert manifests.task_sha and manifests.action_schema_sha
    assert manifests.policy_parent_sha and manifests.split_sha

    if run.algorithm == "bc":
        # 2. BC consumes immutable expert trajectories; empty masks are invalid.
        batch = manifests.expert_dataset.next_batch()
        assert batch.oracle_revision == manifests.oracle_revision
        if batch.valid_action_mask.sum() == 0:
            return stop("empty_bc_denominator")
        return update_masked_action_nll(policy, batch)

    if run.algorithm == "dagger":
        # 3. Roll out the declared mixture/current policy and label visited states.
        beta = run.p ** run.round_id
        trajectory = collect_mixture_rollout(policy, expert, beta, manifests.env)
        if trajectory.policy_sha != policy.sha or not trajectory.all_states_labeled:
            return stop("invalid_dagger_round")
        manifests.aggregate.append_immutable(run.round_id, trajectory)
        return update_on_aggregate(policy, manifests.aggregate)

    if run.algorithm == "ppo":
        # 4. PPO requires fresh behavior log-probs, reward, terminal masks and value.
        rollout = collect_fresh_rollout(policy, value, manifests.env)
        if rollout.behavior_policy_sha != policy.sha:
            return stop("stale_behavior_policy")
        if not rollout.has_reward_logp_value_terminated_truncated:
            return stop("incomplete_ppo_rollout")
        advantages, returns = compute_gae_fail_closed(rollout)
        return ppo_update_with_ratio_stats(policy, value, rollout, advantages, returns)

    return stop("unknown_algorithm_identity")
```

伪代码是 identity/gate目标，不是五项目已存在的统一 trainer。生产环境还需并发 collector、backpressure、oracle限流、dataset version transaction、distributed worker failure、NaN rollback、checkpoint atomics、evaluation canary与安全 stop。

## 15. 十个 Deterministic Probes

| Probe | 固定输入 | 结果 | 教学结论 |
| --- | --- | --- | --- |
| masked BC NLL | `p=.8`有效、`.5`被mask | `.2231435513` | denominator只含有效label |
| empty mask | mask `[0,0]` | gate=`false` | 不返回伪0 loss |
| exposure state shift | expert首步`+1`，model首步`-1` | visited state不同 | 单个错误改变后续分布 |
| scheduled endpoints | `ε=1/0` | teacher/model input | schedule identity可测 |
| DAgger beta | `p=.75`，round `1..4` | `.75/.5625/.421875/.316406` | 与 fixed code一致 |
| nominal aggregate | 10 rounds × 5,000 | 50,000 | 仍需扣invalid/duplicate/early stop |
| inflection weight | actions `0,0,1,1,2`，coef 3.2 | `1,1,3.2,1,3.2` | action change位置加权 |
| GAE reverse | `δ=[1,1,1]`，γ=.99，λ=.95 | `2.82504,1.9405,1` | 逆时间递推 |
| PPO clip | `(r,A)=(1.3,1)/(.7,-1)`，ε=.2 | `1.2/-0.8` | 正负advantage方向不同 |
| terminal/truncation | `r=1,γ=.99,Vnext=10` | `1 / 10.9` | true terminal与timeout bootstrap分开 |

实际执行得到 `10/10 expected decisions matched`。附加 method gate 判定：无 on-policy/expert/aggregate 的离线数据不通过 DAgger；有 fresh rollout/reward/old-logp/returns 才进入 PPO candidate。probe只验证合同与数值反例，不是论文 benchmark、训练稳定性或本地项目结果。

## 16. Public Method → Code Mapping

| Mechanism | Fixed source/code | 本页直接确认 | 仍需单独验证 |
| --- | --- | --- | --- |
| BC/teacher forcing | R2R paper + Matterport R2R code | CE target、teacher executed action、test no-cheat | continuous action regression/local checkpoint |
| student forcing | R2R paper/code | policy action进入next state、current target | oracle correctness与local run |
| scheduled sampling | Bengio et al. | `ε`切换 previous truth/model output | navigation effectiveness |
| DAgger | Ross + VLN-CE | aggregate、`β=p^i`、5k×10、oracle action、inflection weight | local collector/oracle/LMDB lineage |
| PPO/GAE | PPO/GAE + Habitat-Lab | ratio/clip、returns/GAE、value/entropy、grad stats | reward validity、fresh rollout、local result |
| DD-PPO | DD-PPO + Habitat-Lab | distributed sync、preemption与 config | local worker/run/2.5B-scale reproduction |
| IL+RL hybrid | R2R-EnvDrop | teacher CE、sample action、distance reward、value/entropy | 与 PPO/DAgger身份不能混写 |

## 17. 本地五项目 Inventory 与 Direct Audit

### 17.1 Canonical Inventory

| Inventory | Canonical SHA-256 | 与 PER-018 的安全映射 |
| --- | --- | --- |
| [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | action JSON/full-chat CE与offline recipe；不是 continuous-action BC、navigation DAgger或PPO |
| [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | SFT trajectory与tool reward schema；不是 fresh robot-navigation rollout/PPO |
| [OPD](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | text teacher generation与student CE/distillation；不是 env-state DAgger |
| [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | offline finetune launcher与closed-loop eval；无 online expert/reward update |
| [WAM](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | one-task failed action rollout trace；无完整 trainer/checkpoint/denominator |

### 17.2 Local-direct Files

| Fixed local file | SHA-256 | 直接支持 | 不能升级 |
| --- | --- | --- | --- |
| OpenPiVLA `formal_train.py` | `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94` | DROID action window→assistant JSON、padding-only mask、full-chat causal CE、LoRA trainer | FAST等价、assistant-only loss、DAgger/PPO或formal rollout |
| Harness `prepare_sft_data.py` | `AF75E07ED5F2483686D0E4DFADFE23D7F50BD31FE3455FCC3BC7354AB5E85589` | tool/project trajectory、group split、SFT mix | physical navigation action BC |
| Harness `prepare_grpo_data.py` | `EAA4136BE5159E894A70D755B93C1BA427CAF6E47E6AB2802B3670E2DDB28250` | rewardable task/schema、tool/state/proxy weights | trainer、fresh rollout、PPO/online GRPO或robot success |
| UWM finetune launcher | `E5B6DCB03FD6612B996AB9DFD3227CB2426E0A147F21FACEE383BBF56EC29D92` | LIBERO-90 parent、5-task offline finetune、buffer/output contract | DAgger oracle、PPO reward或checkpoint内容 |
| UWM rollout eval | `05E912C2096EFF4BFE8D061E4C334517B03DE80847793D83025A2AA3E18F3943` | reset style、warmup、seed、checkpoint prefix、success summary | eval trajectory反向成为online training data |
| OPD `train_opd_online_vl.py` | `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9` | route teacher generation、student CE、loss/teacher counters | navigation state/oracle aggregation；canonical DAgger |
| WAM base manifest | `63A518674F061D1C14A880805FF9C23DAC2425C9D7B34CC4C75FD3CEDBD33A86` | CoffeePressButton episode0、seed/horizon/controller、`success=false` | policy update或benchmark denominator |
| WAM trained manifest | `809AE4F879C9421F954C7BFC26C70005B94387412449039F9FA8B6E479EF55CC` | 同协议trained-side失败trace引用 | matched checkpoint因果、RL/BC收益 |

本轮逐字节重算八个 local-direct SHA，8/8 与 canonical inventories一致。定向扫描 Agent server 58 files、Harness training pipeline 45、OpenPiVLA deployment 93、UWM repro 17、`muxi` code/config 3,720：前四处没有 `DAgger/teacher forcing/student forcing/PPO/GAE/old_log_prob/compute_returns` 精确实现命中；`muxi`有11个命中文件，但均位于 `embodied/`、dependency或第三方navigation树。代表性的 `StreamVLN/streamvln_dagger.py` 被 `muxi/.gitignore:53 embodied/` 排除，README署名上游作者，不能计入 canonical OPD inventory、local run或候选人ownership。检索没有覆盖未同步远端、历史分支或其他机器，故结论是“当前检查范围内未绑定”，不是绝对不存在。

## 18. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 最小补强 artifact |
| --- | --- | --- | --- |
| OpenPiVLA | offline action-to-text supervision、recipe/mask/serialization冲突与rollout lineage缺口 | 已做navigation BC/DAgger/PPO、formal checkpoint闭环提升 | continuous action target/parser/controller、collector/oracle/reward、checkpoint+episode bundle |
| Robot Harness | tool trajectory SFT、schema-aware reward与proxy eval | PPO/GRPO已在线提升机器人导航成功率 | actual trainer revision、generation groups、fresh effect-sink rollout、old logp/returns或canonical GRPO fields、robot episodes |
| OPD | teacher generation/student CE与route-conditioned distillation | “online”即env on-policy、DAgger或RL | environment state/action、current student rollout、expert relabel、round aggregate与navigation eval |
| UWM | offline finetune→separate rollout eval、reset/seed/protocol工程 | evaluation episode被用于DAgger/RL更新、0.744证明online RL | immutable train dataset/checkpoint、online collector/oracle/reward/update logs、matched evaluation |
| WAM | action trace、controller/horizon字段与失败诊断 | trained manifest证明BC/RL improvement | loadable matched checkpoints、training objective/log、完整 episode denominator与ownership |

安全回答顺序：`public definition → fixed paper/repo → algorithm identity gates → local inventory → local-direct exception → missing runtime/result → candidate ownership`。文件名含 `dagger/ppo/online/reward`、ignored upstream checkout、train loss、Git author或closed-loop eval都不能替代状态分布、oracle/reward、update、result和个人贡献证据。

## 19. Source Gate 与下一切片

本轮已关闭：

- 7份 primary paper 的明确版本、PDF SHA、页数、全文抽取与代表页视觉检查；
- 4个 official repos 的 fixed commit/date/license 与27个核心文件 byte-level SHA；
- BC/teacher/student forcing、scheduled sampling、DAgger、GAE/PPO/DD-PPO 的 update-object 与 runtime identity；
- typed navigation training manifest、train/eval linkage、termination/truncation、STOP/reward/denominator与 first-divergence诊断；
- 10个 deterministic probes，全部命中预期；
- 五份 canonical inventory、八个 local-direct files及 ignored third-party navigation checkout边界。

仍为 `WARN`：本地没有归属于候选人的 navigation expert/oracle、current-policy DAgger collector、immutable aggregation rounds、fresh PPO rollout、behavior log-prob/value/return、reward/STOP contract、matched checkpoint/eval episode、跨seed结果或逐文件ownership闭环。论文与official code只能证明公共机制，不能补成本地结果。

下游 [PER-018 Independent Fact Review](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html) 已完成7/7 PDF、10/10 official files、10/10 probes、8/8 local files与source→knowledge→card reconciliation；public facts为`PASS WITH WARNING`。下一 bounded slice优先进行一题真实口述；保持269张题卡`unseen`，不启动PER-019、不创建 coaching state。

## References

1. Ross, Gordon & Bagnell, [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning](https://arxiv.org/abs/1011.0686), AISTATS 2011.
2. Bengio et al., [Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks](https://arxiv.org/abs/1506.03099), NeurIPS 2015.
3. Anderson et al., [Vision-and-Language Navigation: Interpreting visually-grounded navigation instructions in real environments](https://arxiv.org/abs/1711.07280), CVPR 2018；[official simulator/code](https://github.com/peteanderson80/Matterport3DSimulator/tree/589d091b111333f9e9f9d6cfd021b2eb68435925).
4. Krantz et al., [Beyond the Nav-Graph: Vision-and-Language Navigation in Continuous Environments](https://arxiv.org/abs/2004.02857)；[official code](https://github.com/jacobkrantz/VLN-CE/tree/729d141b2ee10628061ada74dd3a5b9f70faeba5).
5. Wijmans et al., [DD-PPO: Learning Near-Perfect PointGoal Navigators from 2.5 Billion Frames](https://arxiv.org/abs/1911.00357), ICLR 2020；[Habitat-Lab](https://github.com/facebookresearch/habitat-lab/tree/0fb6f43ffe806a8088a171b036336c093bcf604e).
6. Schulman et al., [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347), 2017.
7. Schulman et al., [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438), ICLR 2016.
8. Tan, Yu & Bansal, [Learning to Navigate Unseen Environments: Back Translation with Environmental Dropout](https://arxiv.org/abs/1904.04195)；[official code](https://github.com/airsplay/R2R-EnvDrop/tree/6f938abcf2db999c0118c7e548d8357ab8f006db).
9. [VOL 02 IL / RL / Post-training Source Registry](vol_02_il_rl_posttraining_sources.html) 与 [Independent Fact Review](vol_02_il_rl_posttraining_independent_fact_review.html).
10. [PER-004 VLN / ObjectNav](vol_06_per004_vln_objectnav_source_freeze.html)、[PER-005 Navigation Policy Architecture](vol_06_per005_navigation_policy_architecture_source_freeze.html)、[PER-017 Belief / Memory / Exploration](vol_06_per017_belief_memory_frontier_active_exploration_source_freeze.html).
11. [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [WAM](../evidence/projects/wam_claim_evidence_inventory.html) Claim–Evidence Inventories.
12. [PER-018 Independent Fact Review](vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html)：PDF/code重新获取、Habitat done-mask版本边界、10 probes与local rehash。
