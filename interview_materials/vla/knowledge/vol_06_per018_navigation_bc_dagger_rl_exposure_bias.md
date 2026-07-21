# VOL 06 PER-018：Navigation BC、DAgger、RL 与 Exposure Bias

> 状态：`knowledge_drafted / VLA-PER-018 / source_frozen / independent_fact_reviewed / project_truth_bounded / card_synced / WARN`  
> 更新日期：2026-07-20  
> 权威来源：[PER-018 Source Freeze](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html)  
> 学习边界：本页把已冻结的 navigation behavior cloning、teacher/student forcing、scheduled sampling、DAgger、GAE/PPO/DD-PPO 与 train/eval identity 转成面试讲义；本轮不生成题卡、不改变 268 张题卡的 mastery、不创建 coaching state。

## 问题（Question）

VLN、ObjectNav 或 PointGoal 中，离线 behavior cloning（BC）、teacher forcing、student forcing、scheduled sampling、DAgger 与 PPO 到底改变了什么状态分布、监督信号和优化目标？怎样把 oracle、reward、rollout freshness、STOP、termination/truncation、checkpoint 与 metric denominator 冻结成一个可审计的训练—评估合同，并避免把 recovery 数据、文件名或上游代码误写成个人 DAgger/PPO 成果？

## 1. 学习出口

完成本页后，面试中应能做到：

1. 用数据分布和 update object 区分 BC、teacher forcing、student forcing、scheduled sampling、DAgger、PPO 与 DD-PPO。
2. 写出带 action mask、sample weight 和安全分母的 BC 目标，解释为什么 train CE 下降不等于闭环导航成功。
3. 说明 exposure bias 的 history、state、termination 三层含义，并指出 scheduled sampling 与 DAgger 的身份差异。
4. 从 visited state、oracle relabel、immutable aggregate、\(\beta_i\) lineage 四个 gate 判断一个流程是否真的叫 DAgger。
5. 写出 GAE、PPO clip 和完整 value/entropy 目标，区分 true termination 与 time-limit truncation 的 bootstrap。
6. 设计一份 typed navigation training manifest，把 task、split、oracle、policy、rollout、reward、update、result 和 ownership 绑定起来。
7. 按 first-divergence 顺序诊断“loss 变好但 rollout 变差”“reward 上升但 SR 不升”“PPO ratio 异常”等问题。
8. 对 OpenPiVLA、Robot Harness、OPD、UWM、WAM 给出不越界的项目回答。

## 2. 一分钟心智模型

```text
fixed expert trajectories
        ↓
BC / teacher forcing: learn labels on expert-state distribution
        ↓  errors change the next state
student rollout + current-state oracle query
        ↓
DAgger: immutable aggregate rounds, β schedule, retrain
        ↓ or a separate route
fresh policy rollout + reward + old log-prob + value
        ↓
GAE returns → PPO/DD-PPO update → checkpoint lineage
        ↓
matched split / STOP / termination / denominator evaluation
```

主线只有一句话：**先确认训练时策略访问了哪些 state，再确认每个 state 的 target 或 feedback 从哪里来，最后确认 update 与评估 protocol 是否匹配。** 一个叫 `dagger` 的目录、一个叫 `online` 的脚本或一次闭环 evaluation 都不能替代这三层身份。

## 3. BC 与 Teacher Forcing：在 expert 分布上学动作

行为克隆（Behavior Cloning, BC）把 expert trajectory 当作固定监督数据。令 \(D_E\) 为 expert 轨迹集合，\(m_{b,t}\) 为有效 action mask，\(w_{b,t}\) 为 sample/inflection weight，\(\pi_\theta\) 为策略，离散动作的 masked negative log-likelihood 为：

$$
\mathcal{L}_{\mathrm{BC}}(\theta)
=-
\frac{\sum_{b,t}m_{b,t}w_{b,t}\log \pi_\theta(a^*_{b,t}\mid o^E_{b,t},h^E_{b,t},c_b)}
{\sum_{b,t}m_{b,t}w_{b,t}+\varepsilon}.
$$

变量解释：\(a^*\) 是 expert/oracle action，\(o^E,h^E\) 来自 expert trajectory，\(c\) 是 instruction 或 goal，\(m\) 排除 padding/无效 action，\(w\) 可在 action inflection 处加权，\(\varepsilon\) 只用于防止数值除零。直觉是“在已经走过的正确轨迹上模仿下一步”；实现上应对应 R2R 的 cross-entropy target、VLN-CE 的 oracle action/inflection weight 和 fail-closed empty-mask gate。若有效分母为零、oracle action 为 `-1` 或 STOP 语义不明，应停止该 batch，而不是返回一个伪造的 0 loss。

### 3.1 Teacher forcing 与 covariate shift

teacher forcing 在第 \(t\) 步执行 expert action，再读取下一 observation。因此训练访问分布接近 \(d_{\pi^*}\)，而部署时错误动作会使 state 分布转向 \(d_{\pi_\theta}\)。单步 action accuracy 或 CE 只能回答“在 expert state 上是否像”，不能回答“犯错后能否恢复”。

| 机制 | 下一 state 由谁产生 | target | 主要优点 | 主要风险 |
| --- | --- | --- | --- | --- |
| offline BC | 数据集已固定 | expert action | 便宜、可复现 | 不覆盖策略犯错后的 state |
| teacher forcing | expert action | 下一步 expert action | label 稳定、训练简单 | history/state exposure bias |
| student forcing | learner action | 当前 state 的 target | 可暴露恢复状态 | 需要环境与正确 current-state target |

## 4. Exposure Bias、Student Forcing 与 Scheduled Sampling

exposure bias 至少有三层：

1. **history exposure**：训练输入 previous action/token 是 ground truth，部署输入是 model output。
2. **state exposure**：错误动作改变 pose、view 或 collision 状态，后续 observation 脱离 expert distribution。
3. **termination exposure**：错误 STOP、loop、timeout 或 collision 改变 episode 长度与 metric denominator。

scheduled sampling 以概率 \(\epsilon_i\) 选择 ground-truth previous input，否则把模型输出喂回下一步：

$$
a^{\mathrm{in}}_{t-1}=
\begin{cases}
a^*_{t-1}, & z_t<\epsilon_i,\\
\hat a_{t-1}\sim\pi_\theta, & z_t\ge\epsilon_i,
\end{cases}
\qquad z_t\sim\mathrm{Uniform}(0,1).
$$

变量解释：\(\epsilon_i=1\) 是完整 teacher forcing，\(\epsilon_i=0\) 是 always sampling/student forcing，\(z_t\) 是随机门。它改变的是序列输入和访问历史的 curriculum；它本身没有要求在每个 learner-visited state 查询 external oracle，也没有跨轮 immutable aggregate。面试中应明确说：**scheduled sampling 可以缓解 history mismatch，但不自动满足 DAgger 的 current-state expert-label contract。**

student forcing 若由 learner action 推进环境，并在当前 pose 重新计算 oracle target，可以成为 online imitation 的组成部分；若只是把 model token 喂回去，仍在旧 expert path 上套错位 label，则不能声称拥有 current-state guarantee。

## 5. DAgger：四道身份门

DAgger 的第 \(i\) 轮混合策略和 aggregate dataset 可写为：

$$
\pi_i=\beta_i\pi^*+(1-\beta_i)\hat\pi_i,
\qquad
D\leftarrow D\cup\{(s,\pi^*(s)):s\sim d_{\pi_i}\}.
$$

变量解释：\(\pi^*\) 是 expert/oracle，\(\hat\pi_i\) 是当前 learner，\(d_{\pi_i}\) 是这一轮实际访问的 state 分布，\(\beta_i\) 记录 expert/learner 混合比例。直觉是“让 learner 真正走到会犯错的地方，再让同一个 oracle 在这些地方重新标注”，而不是把旧 demonstration 再复制一次。VLN-CE source freeze 记录的实现使用 \(\beta=p^{\mathrm{data\_it}}\)，`p=.75`、10 轮、每轮 nominal 5,000 trajectories、4 个 IL epochs，并带 oracle action 与 inflection weight。

一个可审计的 DAgger round 必须同时通过：

| Gate | 必须有的证据 | 缺失时的结论 |
| --- | --- | --- |
| policy rollout | trajectory 的 policy/checkpoint hash 与声明的 current/mixture policy 一致 | 不能确认访问分布 |
| oracle query | 同一 task/map/oracle revision 在 visited state 给出 label | 只有 self-training 或 recovery BC 候选 |
| aggregation | round、episode、invalid/skipped、duplicate 可追溯，样本不可变地追加 | 不能确认 aggregate dataset |
| schedule | \(\beta_i\)、round id、训练 config 与 checkpoint lineage | 不能重建 curriculum |

“收集失败轨迹再微调”可能是 recovery BC；“student rollout”可能是 self-training/distillation；只有四道 gate 都满足，才安全地叫 canonical DAgger。

## 6. GAE、PPO 与 DD-PPO：从 action label 转向 return

令 \(r_t\) 为 reward，\(V_\phi(s_t)\) 为 value，\(d_t^{\mathrm{term}}\) 只表示真正 terminal。TD residual 与 GAE 为：

$$
\delta_t=r_t+\gamma(1-d_t^{\mathrm{term}})V_\phi(s_{t+1})-V_\phi(s_t),
\qquad
\hat A_t=\delta_t+\gamma\lambda(1-d_t^{\mathrm{term}})\hat A_{t+1}.
$$

变量解释：\(\gamma\) 是 discount，\(\lambda\) 控制 bias/variance，\(\hat A_t\) 是 advantage。直觉是把未来多个 TD error 按 \(\gamma\lambda\) 逆时间累积；实现要保存 reward、value、mask、return，并按 episode 边界反向递推。time-limit truncation 通常仍需 bootstrap，真正 terminal 才把 next value 切掉；把两者都压成一个 `done` 会污染 return。独立复核确认固定 Habitat-Lab `0fb6f43` 的 trainer 本身仍是 `dones → not_done_masks`，所以这里是目标工程合同，不是该pinned code已完成双字段分离。

PPO 使用采样时的 old policy 与更新中 new policy 的概率比：

$$
r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)},
\qquad
L^{\mathrm{CLIP}}(\theta)=\mathbb E_t\left[\min\left(r_t\hat A_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\right)\right].
$$

变量解释：\(r_t\) 是 policy ratio，\(\epsilon\) 是 clip 范围，\(\hat A_t\) 来自 GAE。直觉是允许有益的小更新，同时限制 ratio 把旧 rollout 推得太远。Habitat/VLN-CE code mapping 还包含 value loss、entropy、auxiliary loss、advantage normalization 和 gradient statistics；PPO clip 公式本身不是完整 trainer。若 behavior log-prob 不是采样该 action 的 \(\theta_{old}\)，或 rollout 在多次更新后仍被叫作 fresh on-policy，ratio 就失去身份。

典型完整目标可写成：

$$
\mathcal L_{\mathrm{total}}
=-L^{\mathrm{CLIP}}+c_v\mathcal L_{\mathrm{value}}-c_H\mathcal H(\pi_\theta)+\mathcal L_{\mathrm{aux}}.
$$

变量解释：\(c_v\) 与 \(c_H\) 是 value/entropy 权重，\(\mathcal H\) 是策略熵，\(\mathcal L_{\mathrm{aux}}\) 代表实现中的辅助项。面试时应把 reward、value target、entropy、mask、denominator 和 clip/ratio 统计一起讲，而不是用一个 surrogate equation 代替整个训练器。

DD-PPO 的关键不是“用了多 GPU”，而是多 worker 采集 fresh rollout、同步更新、无参数服务器的去中心化训练，以及 straggler preemption。官方 PointGoal 配置中的 `2.5e9` frames、clip `.2`、\(\gamma=.99\)、GAE \(\lambda=.95\) 是 frozen public recipe，不是本地运行规模。

## 7. Navigation Training Manifest：把身份写进数据

任何 `BC / DAgger / PPO improved navigation` claim 至少绑定以下层级：

| Layer | 必备字段 | 缺失时不能回答 |
| --- | --- | --- |
| task/data | task、dataset revision/license、scene split、episode IDs、observation/action/STOP schema、frame/unit、horizon | 学的是什么、是否泄漏 |
| expert/oracle | oracle type、shortest-path/navmesh revision、query availability、invalid-action rule | label 是否可信、是否 DAgger |
| policy | architecture/config、parent checkpoint/hash、normalizer/tokenizer、memory reset、action distribution | loss/result 属于哪个模型 |
| rollout | collector SHA、policy SHA、behavior log-prob、env/controller revision、seed、timestamp、termination/truncation | 是否 fresh/on-policy |
| reward/value | reward components/scale、success/STOP predicate、discount、bootstrap rule、value checkpoint | 是否真在优化 RL objective |
| update | algorithm、loss mask/denominator、optimizer、grad norm、round 或 PPO epoch/minibatch、KL/clip stats | 更新了什么 |
| result | checkpoint SHA、split、episode denominator、SR/SPL/nDTW/collision、raw trace、failure taxonomy | 指标能否比较 |
| ownership | upstream/local diff、author/reviewer、run operator、artifact custodian | 谁真正做了什么 |

推荐 immutable lineage：

```text
task_manifest_sha + dataset/env revision + oracle/reward revision
    → collector policy_sha / behavior_policy_sha
    → round_or_rollout_id + raw trajectories
    → update_config_sha + loss/ratio/return logs
    → checkpoint_sha + eval_protocol_sha
    → per_episode_results + summary + ownership ledger
```

## 8. Training ↔ Evaluation Protocol

训练和评估要冻结同一套身份，但不能把训练输入当作评估真值：

| Contract | 需要明确的字段 | 典型错误 |
| --- | --- | --- |
| split | train、val-seen、val-unseen、test；early-stop 规则 | 合并 seen/unseen 报平均 |
| episode | instruction/goal、scene、start/goal、seed、horizon | 不报 timeout/lost denominator |
| observation | RGB/depth/GPS/compass/proprio、resize、normalization、frame、age | 训练看 GT，部署看传感器 |
| action | discrete/continuous、axis/unit、STOP、collision/no-op、repeat/controller | action 顺序或单位错位 |
| rollout | checkpoint、memory reset、determinism、replan/chunk、termination/truncation | 旧 memory 或 stale policy |
| reward | distance-progress、success、slack、collision/stop 组件及尺度 | reward 上升直接等同 SR |
| result | SR/SPL/nDTW、episode denominator、raw trace、failure taxonomy | 只报最终一个百分比 |

R2R teacher/student forcing 的结论只在其图导航、split 和 scorer 下成立；VLN-CE DAgger 的超参只支持其 continuous environment 与 oracle/config；DD-PPO 的 PointGoal 结果不能外推到 VLN、ObjectNav 或真实机器人。

## 9. 方法比较：面试一张表讲清楚

| Method | state distribution | target/signal | aggregation | 最小 runtime | 常见误写 |
| --- | --- | --- | --- | --- | --- |
| offline BC | fixed expert states | expert action | fixed dataset | dataset + mask + loss + checkpoint | action loss 低 = 闭环好 |
| teacher forcing | expert action 产生后续 state | next expert action | 可固定 | ordered trajectory | 没有 exposure bias |
| student forcing | learner action 产生后续 state | current-state target | 视实现 | env rollout + target rule | model rollout自动等于 DAgger |
| scheduled sampling | expert/model previous input 混合 | sequence label | 通常不是跨轮 aggregate | \(\epsilon\) schedule + trace | 等同 no-regret DAgger |
| DAgger | mixture/current policy states | visited-state oracle action | 是 | round collector + oracle + immutable aggregate | recovery demos = DAgger |
| PPO | fresh current/old-policy rollout | reward/return/advantage | rollout buffer | reward + old logp + value + GAE + update | 有 reward 就是 PPO |
| DD-PPO | 多 worker fresh rollout | 同 PPO + synchronized gradient | distributed rollout | worker/step/preemption ledger | GPU 多 = 复现论文规模 |

## 10. First-Divergence Diagnosis

诊断顺序固定为：

```text
task/split/schema
  → expert/oracle/reward identity
  → policy/checkpoint/normalizer
  → collector state/action/STOP
  → label/log-prob/value/return
  → mask/denominator
  → optimizer/grad/ratio
  → checkpoint save/load
  → eval protocol/result
```

| 症状 | 首个分叉假设 | 首查 artifact | 不应先做 |
| --- | --- | --- | --- |
| BC loss 低、rollout 立刻偏航 | expert/model state distribution 不同 | pose/action trace、teacher/student coverage | 只继续降 train loss |
| DAgger 越迭代越差 | oracle/map revision、\(\beta\)、aggregate 污染 | round manifest、invalid/skipped、duplicate | 无条件拼全部旧 LMDB |
| student forcing 不收敛 | current-state target 错位或 learner 太弱 | executed action、next state、recomputed target 三联 | 直接改名 scheduled sampling |
| PPO reward 升、SR 不升 | reward hacking 或 STOP mismatch | reward components、success predicate、raw episode | 把 reward 当 SPL |
| PPO ratio/clip 异常 | stale rollout 或 old logp 错 | policy hash、collector/update timestamps、ratio histogram | 只调 clip epsilon |
| value loss 爆炸 | return/terminal/bootstrap 错 | reward、terminated/truncated、Vnext、GAE trace | 先换大 backbone |
| DD-PPO 不可复现 | worker/preemption/denominator 不一致 | worker ledger、sync fraction、seed | 只报 GPU 数和 wall time |
| val-seen 好、val-unseen 差 | scene/instruction overfit | split manifest、duplicate/leakage、per-scene failure | 合并两个 split |

## 11. Fail-Closed Navigation Training Pseudocode

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

这段代码是 identity/gate 目标，不是五个本地项目已有的统一 trainer。生产实现还要处理并发 collector、oracle 限流、dataset transaction、distributed worker failure、NaN rollback、atomic checkpoint、evaluation canary 和安全 STOP。

## 12. 十个 Deterministic Probes

| Probe | 固定输入 | 预期结果 | 面试要点 |
| --- | --- | --- | --- |
| masked BC NLL | `p=.8` 有效、`.5` 被 mask | `.2231435513` | denominator 只含有效 label |
| empty mask | mask `[0,0]` | `gate=false` | 不返回伪 0 loss |
| exposure shift | expert 首步 `+1`、model 首步 `-1` | visited state 不同 | 单个错误改变后续分布 |
| scheduled endpoints | `ε=1/0` | teacher/model input | schedule identity 可测 |
| DAgger beta | `p=.75`，round `1..4` | `.75/.5625/.421875/.316406` | 记录 round 与 policy |
| nominal aggregate | 10×5,000 trajectories | 50,000 nominal | 仍需扣 invalid/duplicate/early stop |
| inflection weight | actions `0,0,1,1,2`，coef `3.2` | `1,1,3.2,1,3.2` | 只在 change 位置加权 |
| GAE reverse | `δ=[1,1,1]`，\(\gamma=.99,\lambda=.95\) | `2.82504,1.9405,1` | 逆时间递推 |
| PPO clip | `(r,A)=(1.3,1)/(.7,-1)`，\(\epsilon=.2\) | `1.2/-0.8` | 正负 advantage 方向不同 |
| terminal/truncation | `r=1,γ=.99,Vnext=10` | `1 / 10.9` | true terminal 与 timeout 分开 |

Source freeze 中的 deterministic probes 已得到 `10/10 expected decisions matched`。它们是合同和数值反例，不是论文 benchmark、训练稳定性或本地项目结果。

## 13. Public Method → Code Mapping

| Mechanism | 固定来源/代码 | 可以直接讲 | 仍需单独核实 |
| --- | --- | --- | --- |
| BC/teacher forcing | R2R paper + Matterport R2R | CE target、teacher executed action、test no-cheat gate | continuous regression/local checkpoint |
| student forcing | R2R paper/code | policy action 进入 next state、current target | oracle correctness、local run |
| scheduled sampling | Bengio et al. | \(\epsilon\) 切换 previous truth/model output | navigation effectiveness |
| DAgger | Ross + VLN-CE | aggregate、\(\beta=p^i\)、5k×10、oracle action、inflection weight | local collector/oracle/LMDB lineage |
| PPO/GAE | PPO/GAE + Habitat-Lab | ratio/clip、returns/GAE、value/entropy、grad stats | reward validity、fresh rollout、local result |
| DD-PPO | DD-PPO + Habitat-Lab | distributed sync、preemption、PointGoal config | local worker/run/2.5B-scale reproduction |
| IL+RL hybrid | R2R-EnvDrop | teacher CE、sample action、distance reward、value/entropy | 与 PPO/DAgger 的身份不能混写 |

## 14. 五个项目的 Truth Boundary

| 项目 | 可以安全讲 | 当前不能说 | 最小补强 artifact |
| --- | --- | --- | --- |
| OpenPiVLA | offline action-to-text supervision、recipe/mask/serialization 冲突与 rollout lineage 缺口 | 已做 navigation BC/DAgger/PPO、formal checkpoint 闭环提升 | continuous action target/parser/controller、collector/oracle/reward、checkpoint+episode bundle |
| Robot Harness | tool trajectory SFT、schema-aware reward 与 proxy eval | PPO/GRPO 已在线提升机器人导航成功率 | actual trainer revision、fresh effect-sink rollout、old logp/returns 或 GRPO fields、robot episodes |
| OPD | teacher generation/student CE 与 route-conditioned distillation | “online”就等于 env on-policy、DAgger 或 RL | environment state/action、current rollout、expert relabel、round aggregate、navigation eval |
| UWM | offline finetune → separate rollout eval、reset/seed/protocol 工程 | evaluation episode 被用于 DAgger/RL 更新、0.744 证明 online RL | immutable train dataset/checkpoint、online collector/oracle/reward/update logs、matched eval |
| WAM | action trace、controller/horizon 字段与失败诊断 | trained manifest 证明 BC/RL improvement | loadable matched checkpoints、training objective/log、完整 denominator 与 ownership |

被 ignored/third-party checkout 命中的 `StreamVLN/streamvln_dagger.py` 等关键词不能计入候选人 ownership；Git author、文件名、训练 loss 或 closed-loop evaluation 也不能替代 runtime、oracle/reward、update 和 result 证据。

安全回答顺序是：`public definition → fixed paper/repo → algorithm identity gates → local inventory → local-direct exception → missing runtime/result → candidate ownership`。

## 15. 两档面试回答

### 15.1 约 30 秒回答

BC 在 expert-state distribution 上用 action label 训练，teacher forcing 继续执行 expert action，所以 train loss 低不代表策略犯错后能恢复。student forcing 让 learner action 改变后续 state；scheduled sampling 主要缓解 previous-input mismatch。DAgger 更严格：current/mixture policy rollout、visited-state oracle relabel、immutable aggregate 和 \(\beta_i\) lineage 四道门都要有。PPO 则不吃 expert action label，而是用 fresh rollout 的 reward、old log-prob、value 和 GAE advantage 做 clipped policy update；time-limit truncation 还要 bootstrap。我的项目目前没有 navigation oracle/DAgger collector 或 fresh PPO runtime，因此不会把 offline recipe 或上游代码说成个人闭环成果。

### 15.2 约 2 分钟机制回答

我会先按 state distribution 组织答案。BC/teacher forcing 访问的是 expert trajectory，目标是 expert action 的 masked likelihood；一个动作出错，部署时的 pose、observation 和后续 STOP 就可能脱离训练分布，这就是 exposure bias。scheduled sampling 逐步把 previous ground truth 换成 model output，但它不自动拥有 current-state oracle。student forcing 如果真的在当前环境 state 重新查询 oracle，可以成为 online imitation 的组成部分。DAgger 的身份更严格：第 (i) 轮用 \(\beta_i\) 混合 expert 与 learner，记录 learner 实际访问的 states，在这些 states 上查询同一 revision 的 expert，再把不可变 round 追加到 aggregate dataset，最后重训。PPO 是另一条路线：采集与 old policy 对齐的 fresh rollout，区分 terminated 和 truncated，计算 GAE、return、ratio/clip，同时记录 value、entropy、KL、grad 和 checkpoint lineage；DD-PPO 再加入同步多 worker 与 straggler 处理。评估时必须绑定 split、STOP、horizon、controller、seed、episode denominator 和 raw trace。对我的五个项目，我能把 offline action/text supervision、tool reward schema、teacher distillation 或 separate rollout eval 映射到这些概念，但当前没有完整 navigation DAgger/PPO runtime 和 matched result，所以会明确说“可迁移的设计边界”，不声称已经实现。

## 16. 高频追问与答题抓手

| 追问 | 回答抓手 |
| --- | --- |
| student forcing 等于 DAgger 吗？ | 不一定；必须有 learner-visited state 的同源 oracle label 与 aggregate lineage。 |
| scheduled sampling 为什么不保证 no-regret？ | 它主要改变 previous input curriculum，没有 DAgger 的跨轮 oracle aggregation contract。 |
| BC loss 下降为何 SR 不升？ | state distribution、STOP、action unit、horizon 或 metric denominator 可能已变。 |
| PPO 为什么需要 old log-prob？ | ratio 要比较同一 action 在 old/new policy 下的概率；stale logp 会破坏 surrogate。 |
| truncation 和 termination 有什么区别？ | timeout 不是任务完成失败，通常仍 bootstrap；true terminal 才切 next value。 |
| reward 上升为什么不等于 SPL 上升？ | reward 可能被 shaping/STOP/collision hack，SPL 需要独立路径和成功协议。 |
| DD-PPO 的关键是什么？ | fresh rollout、同步更新、worker/preemption/step ledger，不是 GPU 数量。 |
| 如何判断 recovery 数据是不是 DAgger？ | 查 collector policy、visited-state oracle、round manifest、immutable append、\(\beta\) schedule。 |
| 你在项目里实现了吗？ | 当前证据只支持 offline/interface/upstream 邻接，不支持个人 navigation DAgger/PPO ownership。 |

## 17. 常见错误

1. 把文件名带 `dagger` 或 `online` 当成 algorithm identity。
2. 把离线 recovery demonstrations 或 student rollout 自动升级为 DAgger。
3. 用单步 CE/动作 loss 推断闭环 SR、SPL 或真实机器人泛化。
4. 把 reward、advantage、PPO clip 混成一个公式，漏掉 value、entropy、mask 与 denominator。
5. 把 timeout、collision、STOP 和 true terminal 都编码成同一个 `done`。
6. 用 stale rollout 或错误 old log-prob 计算 PPO ratio。
7. 把官方 repo 的超大 frame 数、配置或第三方 checkout 写成个人运行规模。
8. 把 ignored upstream navigation tree、Git author 或自动生成 manifest 写成个人贡献。
9. 合并 val-seen 与 val-unseen，或隐藏 early termination/invalid action 的分母。
10. 没有 task/oracle/policy/collector/checkpoint hash 就声称“可复现”。

## 18. 本页证据边界与下一步

本页已把 PER-018 source freeze 转成可学习知识：BC/teacher forcing、exposure bias、student forcing、scheduled sampling、DAgger 四门、GAE/PPO/DD-PPO、typed manifest、train/eval contract、方法比较、first-divergence、fail-closed 伪代码、10 probes、public-code mapping、五项目 truth boundary、两档口述回答和追问抓手均已覆盖。

独立 fact-review 已重新命中7/7 primary PDF、10/10代表official files、10/10 probes与8/8 local-direct SHA，并补充pinned Habitat done-mask版本边界。仍为 `WARN`：没有真实口述、本地 navigation expert/oracle、current-policy collector、immutable DAgger rounds、fresh PPO rollout、behavior log-prob/value/return、matched checkpoint/eval episode、跨 seed 结果或逐文件 ownership 闭环。页面生成与事实复核不改变 mastery。

下游 [VLA-PER-018 Atomic Card](../questions/vol_06_per018.html) 已在独立 bounded slice 同步并保持 `unseen/WARN`；[Independent Fact Review](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html) 已完成。下一 bounded slice 优先进行一题真实口述；不启动 PER-019、不创建 coaching state。

## References

1. Ross, Gordon & Bagnell, [DAgger](https://arxiv.org/abs/1011.0686), AISTATS 2011；固定版本 `1011.0686v3`。
2. Bengio et al., [Scheduled Sampling](https://arxiv.org/abs/1506.03099), NeurIPS 2015；固定版本 `1506.03099v3`。
3. Anderson et al., [R2R](https://arxiv.org/abs/1711.07280), CVPR 2018；[Matterport3DSimulator](https://github.com/peteanderson80/Matterport3DSimulator/tree/589d091b111333f9e9f9d6cfd021b2eb68435925)。
4. Krantz et al., [VLN-CE](https://arxiv.org/abs/2004.02857)；[official code](https://github.com/jacobkrantz/VLN-CE/tree/729d141b2ee10628061ada74dd3a5b9f70faeba5)。
5. Wijmans et al., [DD-PPO](https://arxiv.org/abs/1911.00357), ICLR 2020；[Habitat-Lab](https://github.com/facebookresearch/habitat-lab/tree/0fb6f43ffe806a8088a171b036336c093bcf604e)。
6. Schulman et al., [PPO](https://arxiv.org/abs/1707.06347), 2017；[GAE](https://arxiv.org/abs/1506.02438), ICLR 2016。
7. Tan, Yu & Bansal, [R2R-EnvDrop](https://arxiv.org/abs/1904.04195)；[official code](https://github.com/airsplay/R2R-EnvDrop/tree/6f938abcf2db999c0118c7e548d8357ab8f006db)。
8. [PER-018 Source Freeze](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_source_freeze.html) 与五项目 Claim–Evidence Inventories。
9. [PER-018 Independent Fact Review](../sources/vol_06_per018_navigation_bc_dagger_rl_exposure_bias_independent_fact_review.html)：7 PDF/10 official files/10 probes/8 local files的独立再获取与reconciliation。
