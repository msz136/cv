# VOL 02 IL / RL / Post-training：从示范数据到可验证反馈

> 状态：`fact_reviewed_candidate / WARN`  
> 报告日期：2026-07-19  
> 证据截止：2026-07-16  
> 适用岗位：VLA / 具身智能算法 / 大模型后训练 / 机器人策略学习  
> 本卷边界：解释 imitation learning、policy gradient、offline RL、SFT/DPO/GRPO 和 schema-aware reward 的通用机制；个人项目的具体 run、指标和贡献边界仍以 VOL 07 与现有项目页为准。

## 问题（Question）

本卷回答一条连续的问题链：

```text
示范数据有什么监督信号？
        ↓
策略如何利用 reward / preference / group feedback 更新？
        ↓
离线数据之外的动作为什么危险？
        ↓
schema、reward checker、holdout eval 如何各司其职？
        ↓
怎样把训练结果与真实机器人闭环分开解释？
```

面试官最常用的转场是：

- “你做了 SFT/GRPO，具体优化的 loss 是什么？”
- “为什么不用 PPO / DPO / offline RL？”
- “reward 是怎么定义的，如何防止 reward hacking？”
- “tool accuracy 或 proxy MSE 提升，为什么能/不能说明真实任务变好？”

### 一句话口径

> IL 解决“模仿给定行为”，RL/post-training 解决“根据反馈重新加权行为”；但反馈的可靠性、数据支持范围和评估协议决定了结果是否可信。schema 是输出契约，reward 是训练信号，holdout eval 是验收协议，三者不能混成一个指标。

## 背景与动机

机器人策略训练同时受三种约束：示范昂贵、在线交互风险高、策略输出必须可执行。单纯 BC 可以快速复用示范，却会遇到协变量偏移；纯 online RL 反馈更接近任务目标，却需要大量安全交互；大模型 post-training 又引入 preference、reference policy 和格式约束。

因此回答算法选择时，先说清楚四件事：

1. **数据从哪里来**：expert demo、旧 policy rollout、人工 preference、规则 checker 还是环境 reward。
2. **更新什么对象**：连续 action、离散 token、value、reward model 还是 adapter。
3. **反馈覆盖什么范围**：只判断格式/工具合法性，还是能判断任务成功、接触质量和长期回报。
4. **在哪里验收**：in-domain、OOD、closed-loop、真机，还是仅离线 proxy。

## 模仿学习与数据分布

### Behavior Cloning 与 covariate shift

BC 把专家轨迹中的 ((o_t,a_t^*)) 当监督样本，最小化：

\[
\mathcal L_{BC}(\theta)
=\mathbb E_{(o,a^*)\sim D_E}
\left[\ell\left(\pi_\theta(o),a^*\right)\right].
\]

(D_E) 是专家数据分布，(ell) 可以是连续 action 的 MSE/Huber 或 token action 的 cross-entropy。直觉是策略在“专家访问过的状态”上学得像；一旦自己的小误差把系统带到 (D_E) 之外，后续状态会越来越陌生，误差会复利累积。实现上要记录 observation history、action window、padding/mask 和 train/eval split，不能只说“拿轨迹训练”。

### DAgger：让策略访问它会犯错的状态

DAgger 让当前策略执行，收集它实际访问的状态，再由专家标注动作并加入数据集：

```text
D_0 = expert demonstrations
for iteration k:
    train π_k on aggregated D_{k-1}
    roll out π_k to collect visited observations
    query expert labels on those observations
    D_k = D_{k-1} ∪ newly labeled data
```

它的核心不是某个 optimizer trick，而是改变训练分布，使策略访问的状态被纳入监督。代价是需要在线专家、人工或高质量 oracle，真实机器人上的标注成本和安全风险都很高。VLA 项目中，recovery/intervention 数据、失败轨迹和 synthetic perturbation 可以起到部分相似作用，但不能不加证据地称为 DAgger。

### Action chunking 与误差累积

若每步动作误差期望为 (epsilon)，长时序 rollout 可能出现随时间增长的累积误差。action chunking 一次预测 (H) 步、只执行 (Kle H) 步后重新观测，可把策略查询次数从 (T) 降到约 (T/K)，同时保留纠偏机会。(H) 决定预测视野，(K) 决定开环执行长度；二者不是同一个参数。VOL 03 会专门讨论 action representation，VOL 05 会讨论延迟和评估协议。

### 数据质量、覆盖与 suboptimal demo

“更多 demo”不是无条件答案。需要分别检查：

- **覆盖**：任务、对象、视角、初始状态、失败恢复是否出现；
- **一致性**：action 轴顺序、单位、时间同步和语言条件是否统一；
- **质量**：轨迹是否含卡顿、错误 gripper、异常 reset 或 label leakage；
- **目标**：suboptimal demo 是噪声、可学习的次优策略，还是需要保留的 recovery 经验。

过滤掉所有“看起来不完美”的轨迹可能丢失恢复分布；全部保留又可能把错误行为变成监督。面试中要先说明过滤规则和评估依据，再说数据量。

## Policy Gradient、GAE 与 PPO

### REINFORCE 与 baseline

策略梯度可写为：

\[
\nabla_\theta J(\theta)
=\mathbb E_{\tau\sim\pi_\theta}
\left[\sum_t \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right],
\]

其中 (G_t) 是从 (t) 开始的 return。直接使用 return 方差很大；减去只依赖状态的 baseline (b(s_t)) 不改变期望梯度，却能减少方差。用 (A_t=G_t-b(s_t)) 后，baseline 通常由 value network 估计。机器人场景还要面对 reward 稀疏、长 horizon 和昂贵 rollout。

### GAE：在 TD 与 Monte Carlo 之间插值

GAE 用 TD residual 的折扣和估计 advantage：

\[
\hat A_t^{GAE(\gamma,\lambda)}
=\sum_{l=0}^{\infty}(\gamma\lambda)^l\delta_{t+l},
\qquad
\delta_t=r_t+\gamma(1-d_t^{term})V(s_{t+1})-V(s_t).
\]

(gamma) 控制长期回报折扣，(lambda) 在低方差/高 bias 的 TD 和高方差/低 bias 的 Monte Carlo 之间插值，(d_t^{term}) 只表示真实终止。时间上限截断 `truncated` 通常仍允许 bootstrap，不能把它和 `terminated` 无条件合成一个 `done`。实现时要检查 episode boundary、timeout、value bootstrap 和 advantage normalization；GAE 不是 PPO 专属，但常与 PPO 配套。

### PPO clipped objective

PPO 用旧策略与新策略的概率比：

\[
r_t(\theta)=
\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)},
\qquad
\mathcal L^{CLIP}
=\mathbb E_t\left[
\min\left(r_t\hat A_t,
\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\right)
\right].
\]

当更新让 ratio 偏离过远时，clip 项限制其继续获益，近似 trust-region；它不是严格约束，也不替代 value loss、entropy regularization 或 rollout freshness。面试时要区分 ratio clipping 与 action clipping：前者限制策略更新比率，后者限制控制量范围。

### PPO 训练诊断

除了 policy loss，还应观察：

- `approx_kl`：新旧策略偏离程度；
- `clip_fraction`：多少样本触发 clip；
- `value explained variance`：value 是否跟上回报；
- entropy：策略是否过早塌缩；
- reward/success 与 episode length：是否出现 reward hacking 或短路。

如果 policy loss 正常但 success 不涨，先查 reward/checker、action parser、终止逻辑和 rollout 分布，再调模型。仅看 loss 曲线无法证明闭环策略正确。

## Offline RL：保守性与行为约束

### 为什么离线数据外的动作危险

离线数据只有 ((s,a,r,s')) 的有限支持。策略如果选择数据中很少出现的动作，critic 需要在缺乏证据的区域外推 Q 值；一旦 Q 过估，actor 会主动追逐这些虚假的高价值动作。机器人上，这种 OOD action 可能直接导致碰撞或不可恢复状态。

### CQL：惩罚 OOD Q 过估

CQL 的核心思想是让数据外动作的 Q 保守，离散动作的简化项可写成：

\[
\mathcal L_{CQL}
=\alpha\left(
\mathbb E_s\log\sum_a\exp Q(s,a)
-\mathbb E_{(s,a)\sim D}Q(s,a)
\right).
\]

第一项鼓励降低所有候选动作的过高 Q，第二项保留数据动作的价值。连续动作需要采样或重要性近似；具体实现有多种变体。面试时不要说 CQL“保证安全”，它只是减少一类 OOD 过估风险。

### IQL：不显式查询数据外动作

IQL 通过 expectile value learning 和 advantage-weighted behavior cloning 提取策略，避免在训练中直接对数据外动作做 max-Q 查询。直觉是先估计数据支持范围内哪些行为更好，再用加权 BC 复制高优势行为。它适合静态数据，但效果仍取决于 reward、数据覆盖和 value 估计。

### Offline RL 的诊断分层

当 offline RL 或行为策略失败时，按层定位：

1. **数据层**：任务覆盖、action normalization、终止/timeout、reward label；
2. **critic/value 层**：Q 过估、target 失真、OOD action 比例；
3. **policy 层**：动作分布、行为约束、采样温度；
4. **执行层**：denormalization、controller、接触和闭环恢复。

这套分层与 UWM/WAM 的失败分析兼容，但不自动说明你的项目使用了 CQL/IQL。

## SFT、DPO、GRPO 与 schema-aware reward

### SFT：对已确定的目标序列做 teacher forcing

SFT 对目标 token 序列做 masked cross-entropy：

\[
\mathcal L_{SFT}
=-\frac{1}{\sum_t m_t}
\sum_t m_t\log\pi_\theta(y_t\mid x,y_{<t}),
\]

(x) 是图像/文本/状态等条件，(y_t) 是目标 token，(m_t) 决定哪些位置计入 loss。工具调用中，(m_t) 可只覆盖 assistant/tool JSON；VLA 中则要明确 action token 是否与文本共同训练。SFT 学的是数据中给出的行为，不会自动学会未覆盖的失败恢复。

### DPO：用 preference pair 隐式吸收 reward

DPO 对 chosen (y_w) 与 rejected (y_l) 的相对 log-ratio 优化：

\[
\mathcal L_{DPO}
=-\mathbb E\log\sigma\left(
\beta\left[
\log\frac{\pi_\theta(y_w\mid x)}{\pi_{ref}(y_w\mid x)}
-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{ref}(y_l\mid x)}
\right]
\right).
\]

reference policy 提供锚点，\(\beta\) 控制偏离程度。DPO 不代表没有 reward 假设，而是把 preference 关系直接写进分类式目标；chosen/rejected 的质量和 pair 构造决定结果。

### GRPO：组内相对反馈

GRPO 对同一 prompt 采样一组回答/轨迹，用组内 reward 归一化形成相对优势的简化形式：

\[
\hat A_i=\frac{r_i-\operatorname{mean}(r_{1:G})}
{\operatorname{std}(r_{1:G})+\epsilon}.
\]

随后仍需结合 policy ratio、clip、reference/KL 或具体实现的正则项进行更新。面试时应说“group-relative feedback 减少了独立 value model 的依赖/提供相对信号”，不要把所有 GRPO 实现说成完全相同，也不要把组内分数直接当真实 task success。

### Schema、reward、holdout eval 三层分工

对于工具调用或结构化机器人 action，可以把设计分成三层：

| 层 | 适合放什么 | 不应声称什么 |
| --- | --- | --- |
| Schema / output contract | 工具名、字段类型、robot scope、JSON 可解析性、动作维度 | schema 合法不等于任务正确 |
| Reward / checker | 可程序化判分的工具选择、参数、scope、顺序和禁止动作 | checker 分数不等于真实物理成功 |
| Holdout eval | in-domain、OOD、安全边界、业务分布、闭环任务 | holdout 一次通过不等于泛化已证明 |

可写成一个设计模板：

\[
R=\sum_j w_jR_j,
\]

其中 (R_j) 是不同约束项，(w_j) 是权重。这个公式只表达 reward decomposition 的通用机制；你现有 Robot Harness 页面支持“schema-aware reward”这一项目方向，但具体权重和 checker 字段仍需以本地数据/代码证据为准。

## Pipeline 与伪代码

### SFT → preference/online feedback 的训练路径

```python
def post_training_pipeline(dataset, base_policy, checker, evaluator):
    # 1. Split demonstrations and preference/rollout data before training.
    sft_data, preference_data, holdout = split_by_episode_and_task(dataset)

    # 2. Train the base behavior with masked teacher-forcing supervision.
    policy = sft(base_policy, sft_data, loss_mask="assistant_or_action_slots")

    # 3. Score candidates with a checker/reward function, keeping raw traces.
    scored = score_with_checker(policy, preference_data, checker)

    # 4. Apply DPO/GRPO only to the feedback format that is actually available.
    policy = preference_or_group_update(policy, scored)

    # 5. Evaluate holdout separately from the reward used during training.
    metrics = evaluator(policy, holdout)
    return policy, metrics
```

关键是先固定 split 和协议，再把 reward/checker 与 holdout 分离；否则可能出现训练 checker 变高但独立评估不变的 reward hacking。

### 一轮 GRPO 风格更新的抽象

```python
def group_relative_update(policy, prompts, rollout_env, optimizer):
    # Sample multiple trajectories for each prompt/task condition.
    groups = [rollout_env.sample(policy, prompt, num_samples=G) for prompt in prompts]

    # Compute rewards from the declared checker/environment, preserving traces.
    rewards = [rollout_env.score(group) for group in groups]

    # Normalize within each group so the update uses relative rather than raw scale.
    advantages = normalize_within_group(rewards)

    # Compute the implementation-specific clipped/KL-regularized policy objective.
    loss = policy_objective(policy, groups, advantages)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    return loss, rewards
```

伪代码没有假定你的 Harness 使用哪一种 exact GRPO loss；它只映射“采样—判分—组内相对化—更新—独立 eval”的数据流。

## 实现映射与项目挂钩

| 通用机制 | 本地材料 | 当前安全表达 | 未核实/不能直接推出 |
| --- | --- | --- | --- |
| SFT / GRPO-style / schema-aware reward | `C:\Users\mousongzhe\agent\remote_training_pipeline_scripts\train_grpo.py`、`configs/reward_spec.json`、`eval_grpo_tasks.py`；另见 [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) | 本地存在 reward-shaped grouped weighting、11 类 reward component、task-family weights 和字段 coverage evaluator；可讲“GRPO-style continuation” | 不能把它说成 canonical online multi-candidate GRPOTrainer、真实物理 reward 或个人独立 ownership |
| action/world/value 多目标 | `interview_materials/04_cosmos_wam_multitask_training.html` | 可以解释 action imitation、world/value 辅助目标和 mask/routing 的潜在互助/干扰 | 不能把通用 PPO/GRPO 结论写成 WAM 使用的算法 |
| DPO / preference sample | `output/mousongzhe_resume_optimized.html` | 可以说参与样本与偏好样本整理、SFT/DPO 实验和错误归因 | 不能虚构 preference pair 数、reward model 或独立 ownership |
| OPD ablation | `interview_materials/02_opd_vlm_grounding.html` | 可用作“如何设计因果 ablation”的项目转场 | 现有材料没有完整 SFT-only/single-teacher 因果表 |
| offline proxy / online rollout | `interview_materials/05_uwm_libero_eval_protocol.html`、WAM 页 | 可以区分 fixed-init strict eval、离线 proxy 和闭环成功 | 不能从基础算法公式推出具体 UWM 根因 |

## 公源/本地设计边界

### 公有设计 / 上游公开流程

- DAgger、GAE、PPO、CQL、IQL、DPO、GRPO 的论文目标和基本假设。
- OpenVLA、openpi、Cosmos Policy 等公开仓库的上游接口与 recipe，具体版本以 Source Scout 冻结为准。

### 本地证据

- 五个项目页、简历 HTML 和 `resume_restructure_plan.md` 支持项目范围、指标和当前已承认的风险。
- Robot Harness 页支持 schema/reward/holdout 的项目叙事，但不替代完整训练代码。

### 本地推断

- 由项目页可推断你需要把训练信号和评估协议分开讲；这是一条叙事/诊断原则，不是某个官方算法的新颖性 claim。

### 当前仍未核实

<div class="warning">⚠️ Harness 的 GRPO-style trainer、reward spec 和字段 evaluator 已能在外部 Project 工作区读取，但 canonical online GRPO、多候选环境 rollout、同 scorer base→SFT→GRPO 因果 bundle 与个人逐文件 ownership 仍未闭合；WAM/UWM 训练源码与完整 rollout logs 仍缺。因此本卷的通用 GRPO 公式与本地脚本必须分层表述。</div>

## 方法对比与选择建议

| 方法 | 优点 | 主要风险 | 面试时先问 |
| --- | --- | --- | --- |
| BC / SFT | 简单、稳定、易扩展到 token/连续 action | covariate shift、示范偏差 | 数据覆盖和 loss mask |
| DAgger | 直接补策略访问态 | 需要专家在线标注，真实机器人昂贵 | expert oracle 是否可用 |
| PPO / online RL | 直接优化环境反馈 | rollout 成本、reward hacking、训练不稳 | reward/checker 和安全边界 |
| CQL / IQL | 可在静态数据上保守改进 | reward/critic/OOD 误差 | 数据支持范围 |
| DPO | 不必显式训练 reward model，适合 preference pair | pair 质量、reference、KL 偏移 | chosen/rejected 如何构造 |
| GRPO | 组内相对反馈，适合可采样/可判分任务 | reward scale、group variance、实现差异 | group、checker、clip/KL 细节 |

## 风险与后续建议

1. 不要把“用了 GRPO”当作结果解释；先说明 group、reward、policy objective 和独立 eval。
2. 不要把 schema 合法、tool accuracy 或 proxy MSE 说成真实物理成功的充分条件。
3. DPO/GRPO 的答案必须区分通用论文机制与个人项目实际使用的实现。
4. VOL 02 下一批题卡应优先绑定 Robot Harness 的 schema/reward/holdout 与“offline GRPO-style ≠ online GRPO”边界、WAM 的 proxy/online gap 和 OPD 的 ablation 缺口。
5. VOL 03 再展开 Diffusion/Flow Matching；不要在本卷用几句带过复杂 action head。

## 参考文献（References）

1. Ross, Gordon, Bagnell, [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning](https://arxiv.org/abs/1011.0686), 2011.
2. Schulman et al., [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438), 2016.
3. Schulman et al., [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347), 2017.
4. Kumar et al., [Conservative Q-Learning for Offline Reinforcement Learning](https://arxiv.org/abs/2006.04779), 2020.
5. Kostrikov et al., [Offline Reinforcement Learning with Implicit Q-Learning](https://arxiv.org/abs/2110.06169), 2022.
6. Rafailov et al., [Direct Preference Optimization](https://arxiv.org/abs/2305.18290), 2023.
7. Shao et al., [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300), 2024.
8. [Hugging Face TRL](https://github.com/huggingface/trl), official training library.
9. 本地项目证据：`interview_materials/01_robot_harness_tool_training.html`、`02_opd_vlm_grounding.html`、`03_openpivla_action_modeling.html`、`04_cosmos_wam_multitask_training.html`、`05_uwm_libero_eval_protocol.html`。
10. [VOL 02 独立事实与实现边界复核](../sources/vol_02_il_rl_posttraining_independent_fact_review.html)：primary source、GAE timeout、CQL partial objective 与本地 GRPO-style trainer 的冻结口径。
