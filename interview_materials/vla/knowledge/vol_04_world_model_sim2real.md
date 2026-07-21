# VOL 04 World Model / Sim2Real：Foundations、评估与证据（Batches 1–2）

> 状态：`drafted / aggregate_knowledge_44_of_44 / cards_44_of_44_unseen / review_warn`  
> 报告日期：2026-07-19  
> 证据截止：2026-07-16  
> 基础页覆盖：`VLA-WM-001..010`、`VLA-WM-039..044`，16/44 个知识节点；独立原子知识页 `VLA-WM-011..038`，28/44 个节点  
> VOL 04 aggregate：44/44 个知识节点，所有题卡仍 `unseen`  
> 当前目标：先建立 world-model 定义/I-O、概率 dynamics、RSSM、rollout/uncertainty/actionability 基础，再把 strict protocol、metric ladder、消融、失败回写和 evidence audit 连成诊断闭环。  
> 项目边界：UWM 74.4%/92.8%、WAM 84/118 与离线 MSE 目前只是本地材料中的 claim queue；本页不把它们升级为已核验个人结果。

## 问题（Question）

当前基础页回答 16 个相互依赖的问题；WM-011..038 由同目录独立原子知识页承载，VOL 04 总入口按 aggregate 计数。

### Batch 2：World Model Foundations（本增量）

1. `VLA-WM-001`：world model 与 policy、environment simulator、reward/value model 有什么边界？
2. `VLA-WM-002`：observation、state、latent、reward、termination 应建模哪些变量？
3. `VLA-WM-003`：deterministic 与 probabilistic dynamics 分别表达什么？
4. `VLA-WM-004`：encoder、transition、decoder、reward 与 continuation head 如何连接？
5. `VLA-WM-005`：one-step prediction 好为什么不能保证 multi-step rollout？
6. `VLA-WM-006`：teacher forcing、open-loop 与 scheduled sampling 的分布差异是什么？
7. `VLA-WM-007`：aleatoric 与 epistemic uncertainty 如何影响 planning？
8. `VLA-WM-008`：video generation 何时是 actionable world model？
9. `VLA-WM-009`：auxiliary representation 与 queryable simulator 有何差异？
10. `VLA-WM-010`：model bias 和 compounding error 如何造成“想象成功、执行失败”？

### Batch 1：评估、证据与失败归因（已完成知识与题卡）

1. `VLA-WM-039`：checkpoint、normalizer、init、warmup、horizon 与 rollout 数怎样组成 strict protocol？
2. `VLA-WM-040`：offline/open-loop/world-model proxy 与 closed-loop success 怎样建立联系而不夸大？
3. `VLA-WM-041`：action/future/value loss 下降但 online success 不变时，怎样做可归因消融？
4. `VLA-WM-042`：怎样检测 hallucination、physical inconsistency、action insensitivity 与 causal inconsistency？
5. `VLA-WM-043`：失败轨迹怎样分层归因并回写数据、训练或评估合同？
6. `VLA-WM-044`：怎样从 paper、repo、checkpoint、runtime 到 ownership 核对真实训练和 rollout 合同？

16 个问题组成“先定义可预测世界，再验证它能否安全用于决策”的链条：

```text
# Foundations establish the contract; evaluation gates test its external validity.
define observation/state/latent/action/reward/continuation
          ↓
separate posterior filtering from prior rollout
          ↓
measure one-step → open-loop → closed-loop gaps
          ↓
freeze protocol + artifacts
          ↓
separate offline / open-loop / proxy / simulator / real metrics
          ↓
run action-only / +world / +value / all paired ablations
          ↓
intervene on actions and test physical / causal consistency
          ↓
localize the first failure and route it to the correct owner
          ↓
audit paper → repo → checkpoint → runtime → personal contribution
```

### 一句话总口径

> World-model 评估的核心不是多报几个 loss，而是证明“同一模型、同一协议、同一初始条件下，某个可干预机制改善了可复现的闭环结果”；任何缺失的 checkpoint、normalizer、init、controller 或 episode record 都会切断这条证据链。

## 知识地图位置与当前批次边界

### 前置知识

- VOL 01：MDP/POMDP、随机变量、置信区间、坐标系、控制频率和 simulator/controller 边界。
- VOL 02：BC、offline proxy、value、distribution shift 与消融的基本因果口径。
- VOL 03：action shape/axis/unit、normalization、chunk/replan、decode→controller 执行闭环。
- VOL 04 Source Audit A–E：world-model probability contract、UWM/Cosmos 实现、Sim2Real 与 benchmark protocol；Foundations 与 Batch 1 已有独立 frozen-source 复核。[1][2][3][4][5][16][17]

### 当前两个批次做什么

| 范围 | 深度 | 主要依据 |
| --- | --- | --- |
| world-model contract | observation/state/latent/action/reward/continuation | Audit A + Foundations independent review |
| latent dynamics | deterministic/probabilistic、posterior/prior、RSSM heads | World Models、PlaNet、DreamerV3 paper/repo |
| rollout validity | one-step、teacher-forced、open-loop、scheduled sampling | Audit A、PlaNet/DreamerV3 |
| uncertainty/actionability | aleatoric/epistemic、intervention、auxiliary-vs-simulator | Audit A/B/C |
| strict protocol | 12-field tuple + run/episode manifest | Audit E、LIBERO/UWM/Cosmos frozen runners |
| metric ladder | teacher-forced、open-loop、WM proxy、sim、real | Audit A/B/E、WorldGym |
| multi-objective ablation | 2×2 world/value factorial + paired eval | Audit B/C/E |
| actionable consistency | action intervention、causal alignment、constraint violation | Audit A/B/C |
| failure trace | first-failure taxonomy + artifact routing | Audit C/D/E |
| evidence audit | paper→repo→checkpoint→runtime→ownership | Audit A–E |

### 当前仍不做什么

1. 不展开 `VLA-WM-011..038` 的完整训练目标、planning/value、多目标 routing 与 Sim2Real 方法课；它们属于后续独立批次。
2. 不把 LIBERO/RoboCasa simulation 写成 Sim2Real，也不声称用户做过真实机器人部署。[4]
3. 不把项目页、resume 或口述数字当作 raw artifact；缺少 checkpoint、config、normalizer、episode trace 时统一标为 `claim-only`。[5]
4. 当前只生成 16/44 个知识节点；`VLA-WM-001..010` 与 `VLA-WM-039..044` 均已有题卡，16 张全部保持 `unseen`。

## VLA-WM-001：World Model 不是 Policy、Value 或环境本体

### 先讲直觉

世界模型（world model）是在模型内部回答“如果在当前情境下执行这段动作，后面可能发生什么”的条件预测器。它可以预测未来 observation、latent/state、reward 或 continuation，但它不自动决定该做什么；决定动作的是 policy 或 planner。真实 environment/simulator 负责产生实际 transition，learned world model 只是由数据拟合出的近似。[1][17]

### 概率合同

令 \(o_{\le t}\) 是历史观测，\(a_{t:t+H-1}\) 是候选动作序列，\(g\) 是任务/语言条件。一个通用合同可写成：

\[
p_\theta\!\left(
o_{t+1:t+H},s_{t+1:t+H},r_{t:t+H-1},c_{t+1:t+H}
\mid o_{\le t},a_{t:t+H-1},g
\right).
\]

变量解释：\(s\) 是可选的真实或 latent state，\(r\) 是一步 reward，\(c\in\{0,1\}\) 是 continuation；并非所有实现都预测全部变量。直觉是先明确“条件是什么、未来变量是什么、预测多长”。实现映射：dataset schema、encoder/transition/heads、action horizon 与 loss mask 必须能回到这组变量；只有视频输出而没有 action contract 时，不能默认它可用于控制。[1][2][3][17]

| 模块 | 输入→输出 | 主要职责 | 不能自动证明 |
| --- | --- | --- | --- |
| policy | observation/task → action | 选择或生成动作 | 对未来动力学建模正确 |
| world model | history/action → future variables | 预测动作后果 | 已找到最优动作 |
| environment/simulator | current state/action → actual next state | 产生真实/仿真 transition | learned model 的泛化 |
| reward model | state/transition/task → immediate reward | 给一步偏好/任务信号 | 长期 return 已校准 |
| value model | state/policy → expected future return | 评价长期结果 | world transition 正确 |
| success classifier | trace/final state → success label | 评估或终止判断 | 可替代 reward/value/controller |

### 项目与答题边界

- WAM/Cosmos 的 world/value/action slot 是上游公开设计；没有 local checkpoint/diff 时不能称为个人提出。[3]
- UWM 的 video/action diffusion 可具备 world-model 角色，但项目名或视频质量不证明 local checkpoint 的 action consequence 正确。[2]
- 面试中先说“在这个项目里 world head 是 auxiliary 还是 rollout-time query”，再谈收益。

## VLA-WM-002：选择 Observation、State、Latent、Reward 与 Termination

### POMDP 视角

机器人通常只有部分可观测信息。可用一组分解表达：

\[
s_{t+1}\sim p(s_{t+1}\mid s_t,a_t),\qquad
o_t\sim p(o_t\mid s_t),\qquad
r_t\sim p(r_t\mid s_t,a_t),\qquad
c_t\sim p(c_t\mid s_t).
\]

变量解释：\(s_t\) 是 Markov state，\(o_t\) 是相机/proprio 等 observation，\(a_t\) 是执行动作，\(r_t\) 是一步 reward，\(c_t\) 表示 episode 是否继续。直觉是环境在 state 上转移，传感器只露出 observation。实现映射：真实 simulator state 可能只用于评估，模型内部以 encoder 产生的 \(z_t\) 或 recurrent belief \((h_t,z_t)\) 近似 state；字段必须在 dataset 与 eval manifest 中分开。[1][17]

### 变量取舍表

| 变量 | 何时必须 | 何时可省 | 省略风险 |
| --- | --- | --- | --- |
| observation | 几乎总是，作为感知输入/重建目标 | state-only 控制实验 | 无法审计相机/遮挡/视角 shift |
| privileged state | simulator training/eval、几何/接触诊断 | 真实部署不可得 | 把 privileged input 泄漏到 policy |
| latent/belief | 高维 observation、部分可观测、多步 rollout | 小型 fully observed state | latent 可能丢任务细节或 collapse |
| reward | model-based RL、planning scoring | 纯 representation auxiliary | 无法评价候选 trajectory |
| continuation/termination | variable-length episode、return bootstrapping | 固定无终止 horizon | imagined rollout 穿过 terminal |
| future observation/state | world prediction 或 consistency | 只学 reward/value 的抽象模型 | 无法做状态级 intervention 诊断 |

### 最小 I/O 合同

一次样本至少记录 obs_keys/history、action shape/axis/unit、state/privileged flags、future horizon、reward semantics、termination vs truncation、mask/padding。termination 是任务/环境终止，truncation 是评测时限；把二者都当 \(c=0\) 会错误截断 value target。

## VLA-WM-003：Deterministic 与 Probabilistic Dynamics

### 两种合同

deterministic dynamics 输出一个点：

\[
\hat s_{t+1}=f_\theta(s_t,a_t).
\]

probabilistic dynamics 输出分布：

\[
\hat s_{t+1}\sim p_\theta(s_{t+1}\mid s_t,a_t).
\]

变量解释：\(f_\theta\) 常对应均值/单一路径，\(p_\theta\) 可由 Gaussian、mixture、categorical latent 或 diffusion 表示多种 future。直觉是前者回答“最可能下一步是什么”，后者回答“有哪些可能、各有多不确定”。实现映射：输出 head 决定参数形状，loss 分别可能是 MSE、NLL、KL 或生成式 denoising；采样次数、temperature 与 seed 属于 rollout contract。[1][2][17]

### 能表达什么，不能表达什么

| 设计 | 优势 | 主要风险 | 合适场景 |
| --- | --- | --- | --- |
| deterministic | 训练/推理简单、速度快、轨迹稳定 | 对多未来取平均，接触/遮挡可能被模糊 | 低噪声 state dynamics、短 horizon |
| stochastic single model | 能表达 aleatoric 多模态 | likelihood 失配、采样方差 | 多未来、视频/接触 uncertainty |
| ensemble | 可用 disagreement 估计 epistemic | 计算/存储成本，成员相关性 | OOD 检测、风险敏感 planning |
| stochastic latent + ensemble | 同时覆盖多模态与知识不足 | 校准困难、planner 易钻漏洞 | 高风险候选筛选，需严格校准 |

**高频误区**：stochastic latent 不自动等于 epistemic uncertainty；单模型可能只学到数据噪声。deterministic model 也不是“没有不确定性”，只是没有在输出合同中显式表达。

## VLA-WM-004：Latent World Model 与 RSSM 的完整数据流

### Encoder、Posterior、Prior 与 Heads

DreamerV3 风格 RSSM 可写成：[1][17]

\[
h_t=f_\phi(h_{t-1},z_{t-1},a_{t-1}),\qquad
z_t\sim q_\phi(z_t\mid h_t,o_t),\qquad
\hat z_t\sim p_\phi(z_t\mid h_t).
\]

变量解释：\(h_t\) 是 deterministic recurrent state，\(z_t\) 是 stochastic latent；posterior \(q\) 在训练/filtering 时读取当前 observation，prior \(p\) 在 imagination 时只依赖历史与动作。直觉是“看见现实时校正 belief，想象未来时不能偷看未来图像”。实现映射：frozen danijar/dreamerv3 reimplementation 的 RSSM.observe、RSSM.imagine、RSSM.loss 分别对应 filtering、prior rollout 与 dyn/rep KL；它不是 Google/DeepMind 官方代码。[1][17]

heads 在 feature \(x_t=[h_t,z_t]\) 上预测：

\[
p_\phi(o_t\mid x_t),\qquad
p_\phi(r_t\mid x_t),\qquad
p_\phi(c_t\mid x_t).
\]

变量解释：decoder/reconstruction head 保留 observation 信息，reward head 提供一步任务信号，continue head 控制 imagined return 的 discount/termination。实现映射：每个 head 要有独立 target、loss scale 与 mask；不能把 total loss 下降解释为每个 head 都变好。[1][17]

```python
def rssm_train_and_imagine(batch, model):
    # 1. Encode real observations and update posterior states with o_t.
    tokens = model.encoder(batch["observation"])
    posterior = model.rssm.observe(tokens, batch["action"], batch["reset"])

    # 2. Fit reconstruction, reward, continuation, dynamics and representation losses.
    losses = model.world_model_losses(posterior, batch)

    # 3. Start from replay posterior states, then roll the prior without future observations.
    imagined = model.rssm.imagine(posterior.start_states, model.policy,
                                  horizon=model.imag_horizon)

    # 4. Predict imagined reward/continuation for actor-critic or diagnostic rollout.
    return losses, model.reward(imagined), model.continue_head(imagined)
```

这段是机制映射，不是用户项目执行日志。项目若声称使用 RSSM，必须补 local module path、config、checkpoint 与 tensor trace。

## VLA-WM-005：One-Step 好不代表 Multi-Step 可靠

### Teacher-Forced 与 Autoregressive 的输入分布不同

one-step evaluation 每步用真实 history；open-loop rollout 从第二步开始使用模型自己的预测。若局部误差为 \(e_t\)，局部 transition 对 state perturbation 的放大因子为 \(L\)，可用分析上界理解：

\[
\|\hat s_{t+h}-s_{t+h}\|
\lesssim
\sum_{j=0}^{h-1}L^{h-1-j}e_{t+j}.
\]

变量解释：\(h\) 是 rollout horizon，\(e_{t+j}\) 是每个局部 prediction error，\(L\) 是局部 sensitivity 的直觉量而非固定常数。当 \(L>1\) 或 rollout 进入训练分布外 state，小误差会放大。实现映射：评测必须输出 error_by_horizon[h]，同时记录 teacher-forced/open-loop、sampler seed、action sequence 与 reset；不能只报平均 one-step MSE。[1][17]

### 常见断点

| one-step 看起来好 | multi-step 失败原因 | 最小检查 |
| --- | --- | --- |
| pixel MSE 低 | 背景占比大、任务对象误差被平均 | task-object pose/error crop |
| latent loss 低 | latent 丢 action/contact 信息 | action probe + contact probe |
| reward error 低 | rollout state OOD、reward shortcut | expert-state vs rollout-state error |
| future video逼真 | action ignoring 或 sign/scale错 | same-state action swap |
| 短 horizon稳定 | compounding 与 terminal 漏建模 | horizon curve + continuation audit |

## VLA-WM-006：Teacher Forcing、Open-Loop 与 Scheduled Sampling

### 三种训练/评估分布

teacher forcing 使用真实前一步 \(x_t\) 预测 \(x_{t+1}\)；open-loop 使用 \(\hat x_t\) 继续预测；scheduled sampling 在训练时随机混用二者：

\[
\tilde x_t=b_t x_t+(1-b_t)\hat x_t,
\qquad b_t\sim\operatorname{Bernoulli}(\rho_t).
\]

变量解释：\(\rho_t\) 是使用真实输入的概率，可随训练下降；图像/离散 latent 中“加法”只是选择器的简写，不一定做数值插值。直觉是逐步暴露模型自己的错误状态。实现映射：training batch 要记录 teacher/predicted mask、stop-gradient 规则、schedule 与跨 episode padding；否则无法判断模型是否真正见过 rollout-state distribution。

| Protocol | 输入来源 | 主要用途 | 风险 |
| --- | --- | --- | --- |
| teacher forcing | 全部真实 history | 稳定监督、component fit | exposure bias |
| scheduled sampling | 真实/预测混合 | 缓解 train-rollout gap | schedule bias、目标不一致 |
| open-loop eval | 模型预测 history | 测 compounding | 不代表 controller 可执行 |
| closed-loop eval | 环境真实 observation 回流 | 测 policy+model+controller | 难以单独归因 world head |

```python
def evaluate_rollout_modes(model, episode, horizons):
    # 1. Reuse the same start state, actions and sampler seeds across modes.
    one_step = model.teacher_forced_predict(episode.observation, episode.action)

    # 2. Feed predictions back only in open-loop mode to expose compounding error.
    open_loop = model.autoregressive_rollout(episode.start, episode.action,
                                             max(horizons), fixed_seed=0)

    # 3. Report each horizon separately; never collapse both modes into one MSE.
    return compare_by_horizon(one_step, open_loop, episode.target, horizons)
```

scheduled sampling 是设计选项，不是保证；若 action、termination 或 observation schema 本身错误，混入预测输入只会训练模型适应错误分布。

## VLA-WM-007：Aleatoric 与 Epistemic Uncertainty

### 两类不确定性的来源

- **Aleatoric**：环境/观测本身存在不可消除的多结果，例如遮挡后物体位置、接触滑移或人类行为随机性；更多同分布数据也不一定消失。
- **Epistemic**：数据覆盖不足或模型知识有限，例如新物体、新相机、未见 action magnitude；补相应数据或模型 ensemble 可能降低。

总预测方差可用 law of total variance 作分析分解：

\[
\operatorname{Var}(Y\mid x)
=
\mathbb E_{\theta}\!\left[\operatorname{Var}(Y\mid x,\theta)\right]
+
\operatorname{Var}_{\theta}\!\left(\mathbb E[Y\mid x,\theta]\right).
\]

变量解释：第一项近似成员内部的 aleatoric predictive variance，第二项近似不同模型/参数间的 epistemic disagreement。直觉是区分“世界本来就多解”和“模型没见过”。实现映射：ensemble member/checkpoint、采样 seed、distribution head 与 calibration split 必须冻结；单次 diffusion sample 的变化不能直接当 epistemic uncertainty。[1][17]

### Planning 中怎样使用

可用风险敏感目标表达：

\[
a^*=\arg\max_a\left(\mathbb E[\hat R(a)]-\beta\,U(a)\right).
\]

变量解释：\(\hat R(a)\) 是 predicted return，\(U(a)\) 是 uncertainty/constraint risk，\(\beta\ge0\) 是风险权重。直觉是高均值候选若来自模型不确定区域，应降权或触发 fallback。实现映射：需要 calibration curve、coverage/abstention、N sweep 与真实 return 对照；未校准 disagreement 可能奖励多样性而非风险。

## VLA-WM-008：Video Generator 何时是 Actionable World Model

### 必须通过的四道门

1. **Action condition**：候选 action sequence 以明确 axis/unit/time 进入 transition，而不是只用文本描述动作。
2. **Sensitivity**：固定 observation 与 sampler seed，改变 direction/magnitude/gripper/order 时 future 有可辨识差异。
3. **Alignment**：这种差异与 simulator/真实 intervention 的对象 pose、joint/contact 方向一致。
4. **Decision utility**：生成 future 能在冻结协议下改善候选筛选、planning 或 failure detection，而非只提高视觉分数。

条件分布可写为：

\[
p_\theta(o_{t+1:t+H}\mid o_{\le t},a_{t:t+H-1},g).
\]

变量解释：\(g\) 是任务条件，\(a\) 必须是实际可执行动作合同。直觉是同一画面下“向左”和“向右”要产生不同且方向正确的未来。实现映射：保存 paired actions/videos、sampler seed、normalizer、horizon 与 environment clone state；只有 FVD/PSNR 或主观逼真度时，最多称 action-conditioned video predictor。[1][2][3][16][17]

| 证据 | 可以说 | 不能说 |
| --- | --- | --- |
| action token/latent进入模型 | 模型结构上有 action condition | 模型真的使用 action |
| action swap 产生不同视频 | 有 action sensitivity | 变化方向正确 |
| cloned-state alignment | 局部动作后果与环境一致 | 长 horizon/真实物理全部正确 |
| proxy rank 有效 | 可筛选所测候选 | 可替代 simulator/real eval |

UWM/Cosmos 的上游结构可以作为实现例子，但当前 local 项目没有 checkpoint-level sensitivity/alignment artifact，不能说本人已经验证 actionable dynamics。

## VLA-WM-009：Auxiliary Representation 与 Queryable Simulator

### 两种使用方式

| 维度 | Auxiliary world objective | Queryable simulator |
| --- | --- | --- |
| 训练目的 | 用 future/reconstruction 改善共享表示 | 学可供候选 action 查询的 transition |
| 推理时是否调用 | 可以完全不用 world head | 必须对一个或多个 action rollout |
| 输出要求 | latent feature 对 policy 有帮助即可 | future/reward/continuation 有稳定合同 |
| action coverage | 与训练 policy 分布一致即可起作用 | 需覆盖 planner proposal/OOD action |
| 核心证据 | action-only vs +world online消融 | prediction/calibration + planning uplift |
| 主要风险 | gradient conflict、shortcut、额外数据混杂 | model exploitation、latency、compounding |

auxiliary 训练常写成：

\[
\mathcal L=\mathcal L_{policy}+\lambda_w\mathcal L_{world}.
\]

变量解释：\(\lambda_w\) 是 world auxiliary weight；只有 same-data/same-budget 的 action-only 与 +world 消融，才能把差异归因给目标。实现映射：必须记录 sample routing、loss mask、gradient scope 与每项 loss，不能用 total loss 证明 policy 改善。[3][16]

queryable simulator 则在推理时显式比较候选：

\[
a^*=\arg\max_{a\in\mathcal A}
\widehat V\!\left(\widehat T(s_t,a)\right).
\]

变量解释：\(\widehat T\) 是 learned transition，\(\widehat V\) 是 learned value/scorer，\(\mathcal A\) 是 policy proposal set。实现映射：必须记录 proposal N、world/value checkpoint、denoise/rollout steps、selector 与 latency；world head 只在训练中出现时不能称 model-based planning。[3]

## VLA-WM-010：Model Bias、Compounding 与“想象成功”

### 三层误差会被 Planner 放大

planner 不是被动使用 world model，而会主动寻找评分最高的 action：

\[
\hat a=\arg\max_{a\in\mathcal A}
\widehat V\!\left(\widehat T^{(H)}(s_t,a)\right).
\]

变量解释：\(\widehat T^{(H)}\) 是 \(H\) 步 imagined transition，\(\widehat V\) 是 scorer。直觉是 optimizer 会寻找模型最乐观的位置；候选越多，越可能选中 hallucination、物理漏洞或 value overestimate。实现映射：需要 random/median/top selector、N sweep、horizon sweep、selected-vs-unselected real outcome 与 latency，不可只报 best-of-N 最终分数。[3][16]

| 断点 | 典型症状 | 诊断 |
| --- | --- | --- |
| transition bias | action effect 方向/幅度错 | cloned-state intervention |
| compounding | 短时对、长时漂 | error/violation by horizon |
| reward/value bias | 失败 future 得高分 | calibration + rank trace |
| proposal OOD | planner 提出训练外动作 | action density/disagreement |
| terminal/contact漏建模 | 穿过 terminal、无接触抓取 | continuation/contact constraint |
| controller mismatch | imagined delta 无法物理执行 | output-transform + tracking trace |
| no recovery | 首次偏离后持续恶化 | first-divergence + recovery-state eval |

```python
def diagnose_imagination_gap(model, planner, cloned_env, start_state):
    # 1. Freeze candidates so planner and environment evaluate identical actions.
    candidates = planner.propose(start_state, fixed_seed=0)

    # 2. Save imagined futures, values and uncertainty for every candidate.
    imagined = [model.rollout(start_state.obs, a) for a in candidates]
    scores = planner.score(imagined)

    # 3. Execute selected and control candidates from cloned simulator states.
    real = [cloned_env.rollout(start_state.clone(), a) for a in candidates]

    # 4. Compare model/environment deltas by horizon and locate first divergence.
    return compare_transition_value_and_constraints(imagined, scores, real)
```

### 最小防守口径

“我不会因为 imagined video 或 value 看起来好就说 world model 可用于规划。我会固定 candidate/action contract，先做 horizon-wise transition 与 action intervention，再看 value calibration 和 selected-vs-control closed loop；最后核对 controller、contact 与 recovery。缺 local checkpoint/episode trace 时，这是一套设计方案，不是我已经跑出的结果。”

## Foundations：从定义到可诊断 Rollout 的最小 Pipeline

```text
# Each arrow is an interface that needs a schema and an evaluation gate.
observation/history/task
        ↓ encoder + posterior filtering
belief state (h_t, z_t)
        ↓ action-conditioned prior transition
future latent/state/observation
        ↓ reward + continuation + optional value
candidate return / risk
        ↓ planner or policy selector
controller action
        ↓ same-protocol environment rollout
error-by-horizon + first-divergence trace
```

这条 pipeline 同时解释了十个基础问题：WM-001/002 定义变量与模块，003/004 定义 dynamics 与 latent data flow，005/006 解释 train-rollout gap，007 定义风险，008/009 决定 world model 是否可查询，010 解释为何 optimizer 会放大模型漏洞。

## VLA-WM-039：Strict Protocol 是可重放合同

### 先讲直觉

strict 不是“我更严格地跑了一遍”，而是任何人拿到同一批 artifact 都能回答三个问题：**用了什么模型、从什么状态开始、怎样执行与判成功。**如果两个结果只共享 task 名，却使用不同 init distribution、warmup、chunk、controller 或 denominator，它们不是同一实验。

### 12-field protocol tuple

一次闭环评测写成：

\[
\mathcal P=(S,I,W,O,A,K,C,H,Y,R,N,M).
\]

变量解释：\(S\) 是 suite/task；\(I\) 是 initial-state distribution；\(W\) 是 warmup；\(O\) 是 observation/preprocess；\(A\) 是 action/normalizer；\(K\) 是 chunk 与 replan；\(C\) 是 controller/timing；\(H\) 是 horizon；\(Y\) 是 success predicate；\(R\) 是 randomness；\(N\) 是 trials/aggregation；\(M\) 是 checkpoint、代码与 runtime。直觉上，这 12 个字段共同定义“同一场考试”。实现映射：它们应进入 run manifest，而不是散落在命令、README 和口述里。[5]

| 字段 | 必须冻结 | 常见伪对齐 |
| --- | --- | --- |
| \(S\) suite/task | task IDs、task class/BDD hash、subset | 只写“LIBERO-10” |
| \(I\) init | state file/hash/index、layout/style、object split | 都是 50 rollouts 就认为相同 |
| \(W\) warmup | action vector、步数、是否计 horizon | 5 个 zero7 与 10 个 close-gripper noop 混用 |
| \(O\) observation | camera keys、history、flip/crop/resize/JPEG | 只对齐最终分辨率 |
| \(A\) action | dim/order/unit/frame、stats、clip、gripper sign | 都是 7D 就认为相同 |
| \(K\) chunk | predicted H、executed K、queue/requery | chunk 16 但每次只执行 1 与执行 16 混用 |
| \(C\) controller | config/hash、Hz、physics step、latency | 都叫 OSC_POSE 就认为参数相同 |
| \(H\) horizon | task max step、timeout、early stop | env horizon 与 eval horizon 混写 |
| \(Y\) success | exact predicate、threshold、invalid rule | 事后删 episode 后仍用原分母名 |
| \(R\) randomness | train/eval/reset/sampler seed、determinism | 只记录一个 global seed |
| \(N\) sampling | trials/task、seeds、macro/micro、CI | 单 seed 与三 seed均值比较 |
| \(M\) model/runtime | checkpoint SHA、stats/config/code/env/hardware | model ID 代替具体 tensor |

### 成功率与 paired effect

固定 task \(t\) 后，二元成功率是：

\[
\hat p_t=\frac{1}{N_t}\sum_{i=1}^{N_t}y_{t,i},
\qquad y_{t,i}\in\{0,1\}.
\]

变量解释：\(N_t\) 是该 task 的有效 episode 数，\(y_{t,i}\) 必须由冻结的 success predicate 产生。直觉是分子和分母都要能回到 episode ID；只保存百分比会失去 invalid episode、init 与失败类型。实现映射：summary JSON 应由 immutable episode JSONL 聚合，而不是手工录入。

比较两个 checkpoint A/B 时，优先在相同 task/init/seed 上做 paired evaluation：

\[
\hat\Delta
=\frac{1}{N}\sum_{i=1}^{N}\left(y_i^{B}-y_i^{A}\right),
\qquad
\widehat{\mathrm{SE}}(\hat\Delta)
=\sqrt{\frac{1}{N(N-1)}
\sum_{i=1}^{N}(d_i-\bar d)^2},
\]

其中 \(d_i=y_i^B-y_i^A\)，\(\bar d=\hat\Delta\)。paired 设计让每个 init 充当自己的对照，减少 init 难度差异；二元小样本时应使用 paired bootstrap 或 exact paired test，而不是把正态近似当保证。实现映射：A/B 的 episode record 必须共享 `pair_id=(task, init_id, seed)`，否则不能计算这组差值。

### UWM 三协议不能混名

| 协议 | Init/reset | Warmup | Trial/seed | 当前证据结论 |
| --- | --- | --- | --- | --- |
| UWM Table II v3 | 50 个 OOD init；扩大 object range 0.03；移除背景物体 | 公开 runner 未闭合 | 50/task × 3 finetune seeds | paper 内部 setting；0.79 属于该 setting [6] |
| frozen UWM repo rollout | `env.seed(e)+env.reset()` | 无 | template 50/task | reset-style；不是 Table II [2][7] |
| 本地项目 fixed-init claim | 项目页称 pruned init | 项目页称 5×zero7 | 项目页称 50/task | 缺 raw artifacts；74.4% 暂为 claim-only [5][14] |

任务名相同不消除第一列的分布差异。正确表达是“`fixed-pruned-init-50-v1` 下的待核验结果”，而不是“Table II strict aligned”。[5][6]

### Run 与 episode manifest

| 层级 | 最小字段 | 作用 |
| --- | --- | --- |
| run | run ID、owner、purpose、git diff hash | 说明谁在何种代码状态执行 |
| model | model/revision、checkpoint SHA/bytes、config SHA | 防止同名 checkpoint 漂移 |
| stats | action/proprio stats SHA、tokenizer/T5 revision | 固定输入输出尺度与条件 |
| runtime | Python、Torch、CUDA/MACA、MuJoCo、robosuite、hardware | 解释数值与 sampler 差异 |
| episode | task/init/seed、success/step、exception、video/trace SHA | 让百分比可回放和清洗 |
| protocol | \(S..M\) 的结构化值 | 决定哪些 run 可比较 |

```python
def freeze_eval_run(cfg, checkpoint, episodes):
    # 1. Hash every mutable model/config/stat asset used at inference.
    model_manifest = hash_assets(checkpoint, cfg.model, cfg.normalizer)

    # 2. Serialize the full protocol tuple; unknown is a blocker, not a wildcard.
    protocol = build_protocol_tuple(cfg)
    assert all(protocol[field] is not None for field in REQUIRED_PROTOCOL_FIELDS)

    # 3. Attach task/init/seed and raw artifact hashes to every episode.
    records = [attach_pair_id_and_hashes(ep) for ep in episodes]

    # 4. Derive summary from records so deleted/invalid episodes remain auditable.
    summary = aggregate_without_dropping_history(records)
    return {"model": model_manifest, "protocol": protocol,
            "episodes": records, "summary": summary}
```

## VLA-WM-040：Metric Ladder 不允许跨层替代

### 五层证据阶梯

| 层级 | 例子 | 主要证明 | 不能直接证明 |
| --- | --- | --- | --- |
| L0 component fit | action/future/value L1/MSE、KL | 某 target 在 frozen split/noise 下被拟合 | causal dynamics、controller success |
| L1 teacher-forced | one-step image/latent/reward error | 真实历史条件下的局部预测 | 自回归稳定性 |
| L2 open-loop | horizon-wise rollout error、action sensitivity | 模型使用自己预测后的误差累积 | 真实环境可执行性 |
| L3 WM proxy | WorldGym/VLM score、imagined value/rank | learned environment 中的筛选/排序能力 | simulator 或真实 success 等价 |
| L4 simulator closed loop | LIBERO/RoboCasa task success | 固定 simulator/controller protocol 下的行为 | real-world transfer |
| L5 real closed loop | real robot success、constraint/recovery trace | 指定 hardware/protocol 下的部署证据 | 其他机器人/环境泛化 |

从 L0 到 L5 是逐层增加外部有效性，不是指标必然单调。一个模型可能 image MSE 更低，却因 action ignoring、contact shortcut 或 value miscalibration 在 L4 更差。[1][2][3]

### one-step 好为何不能外推 long rollout

若第 \(t\) 步局部误差是 \(e_t\)，局部 dynamics 对 state 误差的放大因子近似为 \(L\)，可用分析框架表示：

\[
\|\hat s_{t+h}-s_{t+h}\|
\lesssim
\sum_{j=0}^{h-1}L^{h-1-j}e_{t+j}.
\]

变量解释：\(h\) 是 rollout horizon，\(L\) 不是固定的论文常数，而是局部 sensitivity 的直觉量。当 \(L>1\) 或预测进入 OOD state，小 one-step error 也会被放大。实现映射：评估必须输出 `error_by_horizon[h]`，并同时标注 teacher-forced 或 autoregressive；不能只报一个平均 MSE。[1]

### 如何验证 proxy 与真实 success 的关系

不要在单个 checkpoint 上说“相关”。至少准备多个真实不同的 policy variants \(j=1..J\)，在同一 task distribution 上分别得到 proxy score \(q_j\) 与 simulator/real success \(p_j\)，再看 rank consistency：

\[
\rho_s=\operatorname{Corr}
\left(\operatorname{rank}(q_1,\ldots,q_J),
\operatorname{rank}(p_1,\ldots,p_J)\right).
\]

变量解释：\(\rho_s\) 是 Spearman-style rank correlation，用于回答 proxy 能否排序候选，而不是两者数值是否相等。实现映射：variants 必须在 checkpoint、规模、训练阶段等维度预先定义；每个 \(q_j,p_j\) 都要有 uncertainty/seed。即使 \(\rho_s\) 高，也只支持所测 policy/task 分布；WorldGym 的 VLM scorer、checkpoint 和 API version 仍需冻结。[11][12]

### 不夸大的三档结论

| 证据 | 安全结论 | 危险结论 |
| --- | --- | --- |
| action MSE 降 | “held-out action fitting 改善” | “policy success 提升” |
| future error 降 | “该 horizon 的预测更接近 target” | “学会真实物理” |
| proxy rank 与 sim rank相关 | “可用于所测候选的前置筛选” | “可替代 simulator/real eval” |
| sim success 提升 | “该 frozen sim protocol 下更好” | “已完成 Sim2Real” |
| real paired trials 提升 | “指定 hardware/task/protocol 下改善” | “泛化到所有真实场景” |

## VLA-WM-041：Offline 下降但 Online 不变时怎样消融

### 先把“多目标有效”拆成四个训练臂

对 action 主任务，world/value 的最小 2×2 factorial 是：

| Arm | Action loss | World loss | Value loss | 回答的问题 |
| --- | --- | --- | --- | --- |
| A00 action-only | on | off | off | 主任务基线 |
| A10 +world | on | on | off | world 的边际作用 |
| A01 +value | on | off | on | value 的边际作用 |
| A11 all | on | on | on | 联合与 interaction |

四个 arm 必须共享 data split、initial checkpoint、train steps/tokens、optimizer budget、batch composition、action labels 与 eval protocol。若 `+world` 额外看更多 robot/video data，应把“objective effect”和“data amount effect”再拆开，不允许把二者都归因于 world loss。[2][3]

### Factorial effect

对任一结果 \(Y\)（offline loss、proxy 或 online success）可写一个解释性模型：

\[
Y_{w,v}
=\beta_0+\beta_W w+\beta_V v+\beta_{WV}wv+\varepsilon,
\qquad w,v\in\{0,1\}.
\]

变量解释：\(w\) 与 \(v\) 表示是否启用 world/value；\(\beta_W\) 和 \(\beta_V\) 是在另一目标关闭时的边际 effect；\(\beta_{WV}\) 是联合目标超出简单相加的 interaction。直觉是 A11 更好不能自动说明两个 auxiliary 都有用。实现映射：每个 cell 至少多个 training seeds，并在相同 paired episodes 上评估；binary success 可用 paired bootstrap/分层模型，而不是只拟合一次线性回归。

### Offline→online 断点矩阵

| 观察 | 更可能的断点 | 下一实验 |
| --- | --- | --- |
| action MSE↓，success↔ | normalizer/axis、distribution shift、recovery缺失 | action round-trip、expert-state vs rollout-state error |
| world loss↓，action/success↔ | world 表示未进入 action decision、目标过易 | frozen encoder probe、action intervention |
| value MSE↓，best-of-N↓ | OOD overestimate、optimizer's curse | reliability/rank、random/median/top selector、N sweep |
| A10↑、A01↔、A11↓ | world有益但 value冲突 | gradient cosine、value label audit、weight sweep |
| all offline均↓、sim success↓ | protocol/checkpoint 或 closed-loop drift | same-run manifest diff、horizon/K sweep |
| sim↑、real↔ | reality gap/controller/contact | paired real trace、SysID/latency/contact tests |

### 必须同时报告的四类结果

1. **Component metrics**：action/world/value 各自的 loss，不能只报 total loss。
2. **Representation/consistency probes**：action sensitivity、horizon error、value calibration。
3. **Closed-loop**：same-protocol paired task success、episode length、failure family。
4. **Cost**：train compute、inference latency、planning N 与 executed replan K。

```python
def run_factorial_ablation(base_cfg, seeds, paired_eval_set):
    # 1. Create action-only, +world, +value and all with identical budgets.
    arms = make_2x2_arms(base_cfg, factors=["world_loss", "value_loss"])
    results = []
    for arm in arms:
        for seed in seeds:
            # 2. Train from the same initialization and record every config delta.
            ckpt = train_with_manifest(arm, seed, init=base_cfg.initial_checkpoint)

            # 3. Evaluate component metrics and consistency before closed-loop rollout.
            offline = evaluate_components(ckpt, base_cfg.frozen_holdout)
            probes = run_action_world_value_probes(ckpt)

            # 4. Reuse identical task/init pair IDs for online comparison.
            online = evaluate_paired(ckpt, paired_eval_set)
            results.append(record(arm, seed, offline, probes, online))

    # 5. Estimate main/interaction effects with seed and episode uncertainty.
    return summarize_factorial_effects(results)
```

## VLA-WM-042：检测 Hallucination 与物理/因果不一致

### 四个概念先分开

| 现象 | 定义 | 典型症状 |
| --- | --- | --- |
| hallucination | 生成了数据/环境不支持的对象、状态或成功线索 | 物体凭空出现、门未开却预测完成 |
| physical inconsistency | 违反几何、接触、连续性或约束 | 穿透、无支撑悬浮、夹爪未闭却抓起 |
| action insensitivity | 不同有效动作产生近似相同 future | action swap 后视频几乎不变 |
| causal inconsistency | 预测会变化，但变化方向与真实 intervention 不一致 | 向左动作预测向右移动、gripper sign反转 |

画面“好看”只能反驳明显视觉崩坏，不能反驳后三项。[1][2][3]

### Action sensitivity 不是 action correctness

固定 observation \(o_t\)，构造语义上有差异的 action sequences \(a\) 与 \(a'\)，定义 horizon \(h\) 的 sensitivity：

\[
S_{act}(h)=
\mathbb E\left[
\frac{d_\phi\left(\hat o_{t+h}(o_t,a),
\hat o_{t+h}(o_t,a')\right)}
{\|a-a'\|_2+\epsilon}
\right].
\]

变量解释：\(d_\phi\) 可以是 task-relevant feature/pose distance，\(\epsilon\) 防止分母为零。\(S_{act}\) 过低提示 action ignoring；过高也可能是噪声放大。实现映射：action pair 应覆盖 direction、magnitude、gripper、noop 与时间置换，并保存相同 sampler seed 的 paired videos，避免 sampling noise 冒充 sensitivity。

### Causal alignment 需要真实或 simulator intervention

从同一可克隆 state 分别执行 baseline action \(a^0\) 和候选 action \(a\)，比较模型与环境中的 task-relevant change：

\[
C(h)=\mathbb E\left[
\cos\left(
\Delta\hat\phi_h(a,a^0),
\Delta\phi^{env}_h(a,a^0)
\right)
\right].
\]

其中 \(\Delta\hat\phi_h=\phi(\hat o_{t+h}(a))-\phi(\hat o_{t+h}(a^0))\)，环境项同理。直觉是模型不仅要“对 action 有反应”，还要沿正确方向反应。实现映射：LIBERO 可从同一 simulator state clone 两条 rollout；feature 应优先使用 object pose、joint/contact state 等可解释量，而不是只用像素 embedding。该测试证明局部 intervention alignment，不证明任意长 horizon 因果正确。

### Physical violation 与 horizon curve

令 \(g_j(x)\le 0\) 表示第 \(j\) 个物理/任务约束，例如穿透深度、支撑关系、关节限位或对象守恒，可定义：

\[
V_{phys}(h)=
\mathbb E\left[
\sum_j w_j\,\mathbf 1\{g_j(\hat x_{t+h})>0\}
\right],
\qquad
E(h)=\mathbb E[d(\hat x_{t+h},x_{t+h})].
\]

变量解释：\(w_j\) 是约束严重度，\(V_{phys}\) 统计 violation，\(E(h)\) 画出 error 随 horizon 的变化。实现映射：能取得 simulator state 时直接用 pose/contact/joint；只有视频时，几何或 VLM judge 只能作为 proxy，必须标记 scorer version 与 uncertainty。[4][11][12]

### 最小 consistency suite

| Test | 固定 | 改变 | 观测 | 失败说明 |
| --- | --- | --- | --- | --- |
| action swap | observation、sampler seed | action direction | future delta | action ignoring / sign error |
| magnitude sweep | state、axis | action magnitude | monotonic pose change | saturation / scaling mismatch |
| gripper counterfactual | arm trajectory | open/close sign | contact/grasp state | gripper semantics错误 |
| noop test | state | valid noop vs motion | background/object motion | uncontrolled hallucination |
| temporal permutation | action multiset | order | endpoint/trajectory | time conditioning失效 |
| cloned-state env pair | exact state | candidate action | model-vs-env delta | causal inconsistency |
| long-horizon rollout | start state | horizon \(h\) | \(E(h),V_{phys}(h)\) | compounding / physics drift |
| value consistency | same candidates | N/selector | rank vs real return | OOD value overestimate |

```python
def consistency_suite(world_model, cloned_env, start_state, action_pairs):
    # 1. Reuse the same state and sampler seeds for every counterfactual pair.
    reports = []
    for action_a, action_b in action_pairs:
        pred_a = world_model.rollout(start_state.obs, action_a, fixed_seed=0)
        pred_b = world_model.rollout(start_state.obs, action_b, fixed_seed=0)

        # 2. Measure whether the model reacts to the action at each horizon.
        sensitivity = feature_delta_by_horizon(pred_a, pred_b)

        # 3. Execute both actions from cloned simulator states for causal alignment.
        real_a = cloned_env.rollout(start_state.clone(), action_a)
        real_b = cloned_env.rollout(start_state.clone(), action_b)
        alignment = causal_alignment(pred_a, pred_b, real_a, real_b)

        # 4. Count task-specific geometry/contact/constraint violations.
        violations = physical_constraint_checks(pred_a, pred_b)
        reports.append((sensitivity, alignment, violations))
    return aggregate_with_horizon_and_seed_uncertainty(reports)
```

## VLA-WM-043：Failure Trace 要定位第一处断点

### 不从 success=0 直接猜 backbone

最终失败通常是上游小误差级联的结果。应定位 first observable divergence：第一次相机/状态不一致、第一次 action 反向/饱和、第一次 controller 跟踪失败、第一次接触丢失、第一次规划选错或第一次无法恢复。只看最后一帧会把 recovery failure 错归因给 perception。

推荐顺序：

```text
# Stop at the first layer that differs from the frozen contract.
protocol / checkpoint
        ↓
observation and prompt
        ↓
action transform / gripper
        ↓
chunk queue / controller / timing
        ↓
free-space dynamics
        ↓
contact / object interaction
        ↓
planning / value selection
        ↓
recovery / fallback / success predicate
```

### Failure taxonomy 与证据

| Layer | 最小 trace | 常见 failure | 先做什么 |
| --- | --- | --- | --- |
| protocol | run manifest、task/init/seed | 不同分布或 denominator | protocol diff + paired rerun |
| checkpoint | SHA、load keys、stats SHA | 错 tensor/EMA/normalizer | strict load + tensor stats |
| observation | raw/preprocessed frame、prompt、history | view/flip/crop/time mismatch | image pair + timestamp replay |
| action | normalized/raw/env action | axis/unit/gripper/clip错误 | round-trip + expert action replay |
| chunk/control | query/queue/command/state timestamps | stale chunk、延迟、controller mismatch | K sweep + tracking error |
| dynamics | predicted/real free-space pose | action consequence失真 | cloned-state intervention |
| contact | contact force、grasp/object state | slip、penetration、wrong compliance | contact/gripper trace |
| planning/value | candidates、future/value/rank | hallucination被高 value选中 | N/selector/calibration sweep |
| recovery | first error、replan、fallback event | 无法从 OOD state返回 | recovery-state dataset |
| success/infra | predicate、timeout、exception | false positive/negative、漏计 | exact predicate + invalid rule |

### 回写不是把所有失败都加回训练集

| Failure family | 回写目标 | 不应做的事 |
| --- | --- | --- |
| observation | 修 converter/wrapper；补 view/time hard cases | 用更多模型容量掩盖 flip bug |
| action contract | 修 stats/axis/unit；加 round-trip unit tests | 把错误动作当新标签训练 |
| action coverage | 补转折、gripper、recovery states | 只重复 easy demos |
| world dynamics | 补 action-diverse transition 与 long rollout supervision | 只优化像素细节 |
| contact | 补高频 contact/gripper state 与 hard negatives | 仅凭视频主观标物理正确 |
| value/planning | 补 OOD failure/value label；做 calibration | 直接增大 N 追逐高估值 |
| recovery | 从 first deviation 后采集 corrective trajectories | 只从专家初始分布重跑 |
| protocol/infra | 修 harness、manifest、validity rule | 把无效 episode 当模型失败 |

```python
def classify_and_route_failure(episode, frozen_protocol):
    # 1. Reject protocol/checkpoint mismatches before model diagnosis.
    assert_manifest_matches(episode.run_manifest, frozen_protocol)

    # 2. Find the earliest timestamp where an interface or behavior diverges.
    first = find_first_divergence(episode.raw_obs, episode.model_obs,
                                  episode.model_action, episode.env_action,
                                  episode.controller_state)

    # 3. Attach evidence, not only a human-readable label.
    family = classify_with_traces(first, episode.contact,
                                  episode.candidates, episode.success_predicate)

    # 4. Route only confirmed failures to code, data, objective or eval owners.
    destination = ROUTING_TABLE[family]
    return create_failure_record(first, family, destination,
                                 artifact_hashes=episode.hashes)
```

## VLA-WM-044：从 Paper 到 Ownership 的 Evidence Audit

### 五层链条

| 层 | 能证明 | 不能跨越 |
| --- | --- | --- |
| paper | 方法定义、实验 setting、论文报告结果 | 当前 repo default、checkpoint tensor |
| official repo | frozen commit 的代码路径和默认/示例 config | 论文实际 run、用户 local diff |
| checkpoint/assets | 某组 tensor、stats、tokenizer/T5 与 license | 环境能加载、成功率 |
| runtime/eval | exact environment/controller/protocol 下的 episode records | 个人原创机制、其他 protocol 泛化 |
| ownership | local diff、design note、commands/logs、负责范围 | 上游公开结构归为个人创新 |

强 claim 需要链条连续。例如“我复现 UWM Table II”至少需要 paper OOD setting → 对应 env patch → checkpoint/config/stats → 3-seed 50-init episode records → local execution/ownership。仅有 task 名、README command 和一个成功率不够。[2][5][6]

### Evidence labels

| Label | 定义 | 推荐语气 |
| --- | --- | --- |
| `primary` | paper、benchmark paper、官方技术报告 | “论文定义/报告……” |
| `official-code` | frozen official repo、docs、model/dataset card | “该 commit 的代码路径……” |
| `local-evidence` | local code/config/log/checkpoint/eval artifact | “本地 artifact 显示……” |
| `inference` | 多项证据支持但未直接记录 | “由同源证据推断……” |
| `unverified` | 缺 source、revision、artifact 或相互矛盾 | “尚未核实，不能确认……” |

### Claim ledger

每条面试 claim 建议记录：

| 字段 | 问题 |
| --- | --- |
| claim | 具体说了什么，是否含数字、因果或 ownership？ |
| source | primary/official/local 的 URL/path/revision？ |
| supports | source 真正支持哪一部分？ |
| does not support | 最容易被错误外推的是什么？ |
| protocol | \(\mathcal P\) 是否完整且与 baseline 相同？ |
| artifact | checkpoint、stats、episodes、trace 是否有 SHA？ |
| ownership | 上游、本人、团队分别做了什么？ |
| verdict | verified / directional / claim-only / blocked |

```python
def audit_interview_claim(claim, evidence_graph):
    # 1. Parse method, metric, protocol and ownership subclaims separately.
    atoms = decompose_claim(claim)
    verdicts = []
    for atom in atoms:
        # 2. Walk primary → code → checkpoint → runtime → ownership evidence.
        chain = evidence_graph.find_chain(atom)

        # 3. Missing revisions or artifacts stop the chain; intent is not evidence.
        if chain.has_gap() or chain.has_protocol_mismatch():
            verdicts.append((atom, "claim-only", chain.gaps()))
        else:
            verdicts.append((atom, "verified", chain.artifact_hashes()))

    # 4. Phrase the final answer at the weakest supported atom, not the strongest one.
    return build_truth_bounded_answer(verdicts)
```

### 一个典型的错误升级

```text
# Each gap below requires a new source or runtime artifact.
paper reports 0.79 on five named tasks
        ≠ repo default runner reproduces 0.79
        ≠ my fixed-init run is protocol-equivalent
        ≠ my checkpoint achieved the paper result
        ≠ I invented UWM's architecture
```

每个 `≠` 都需要新的证据层。面试中主动指出边界通常比给出一个无法防守的强数字更可信。

## 跨六题的最小执行 Pipeline

```python
def evaluate_world_model_policy(candidate_runs, source_ledger):
    # Gate 1: audit paper/repo/checkpoint/runtime and freeze protocol tuples.
    audited = [audit_run_sources(run, source_ledger) for run in candidate_runs]
    comparable = select_runs_with_identical_protocol(audited)

    # Gate 2: compute component, teacher-forced, open-loop and proxy metrics separately.
    ladder = evaluate_metric_ladder(comparable)

    # Gate 3: if an auxiliary objective is claimed, require the 2x2 factorial arms.
    effects = run_or_load_world_value_factorial(comparable)

    # Gate 4: intervene on actions and compare predictions with cloned env rollouts.
    consistency = run_action_and_physics_consistency_tests(comparable)

    # Gate 5: run same-init closed-loop episodes and record the first divergence.
    episodes = paired_closed_loop_eval(comparable)
    failures = [classify_and_route_failure(ep, comparable.protocol)
                for ep in episodes if not ep.success]

    # Gate 6: emit claim ledger; unsupported personal claims remain blocked.
    return build_evidence_report(ladder, effects, consistency,
                                 episodes, failures, source_ledger)
```

这段 pipeline 的顺序很重要：protocol 不同就不进入 score comparison；没有 2×2 arm 就不归因 auxiliary；没有 intervention 就不声称 causal dynamics；没有 runtime/ownership artifact 就不升级个人贡献。

## UWM / WAM 项目挂钩与真实性边界

### 当前可以安全讲什么

| 项目 | 安全口径 | 仍缺证据 |
| --- | --- | --- |
| UWM/LIBERO | “我把 fixed-init 与 reset-style 分开，并通过 source audit 发现它们都不能直接称为 UWM Table II setting。” | checkpoint/config/stats SHA、250 episode records、exact init/horizon/chunk、OOD env patch |
| Cosmos/WAM | “我把 action/world/value component fit、direct policy 与 planning selection 分开，知道 auxiliary 收益需要 action-only/+world/+value/all 消融。” | local checkpoint、split/metric tensors、24-task raw episodes、controller/fork manifest |
| WorldGym/WM proxy | “它可作为 deployment 前筛选 proxy，但要用多 policy variants 验证 rank consistency。” | local WM checkpoint、scorer/API revision、sim/real paired validation |
| Sim2Real | “我会按 observation→control→dynamics→contact 做 paired trace。” | 任何真实 hardware/calibration/latency/contact/rollout artifact |

### 当前不能说什么

1. “我的 74.4% 已严格复现 UWM Table II。”——论文 OOD init 与项目 fixed-pruned-init 不等价。[5][6][14]
2. “92.8% 是正式 UWM benchmark。”——项目页缺 same-checkpoint protocol manifest，最多是 reset-style diagnostic claim。[5][14]
3. “84/118 是我的 WAM 训练结果。”——项目页把它描述为 official HF baseline 的本地 smoke，而且两条 episode 的清洗规则未由 raw records核验。[5][15]
4. “world/value loss 下降证明辅助目标提升 policy。”——没有 factorial arm 与 same-protocol online result，不能做因果归因。[3]
5. “LIBERO/RoboCasa success 说明完成 Sim2Real。”——simulation 与真实硬件 evidence 是不同层。[4]

### 90 秒项目防守稿

“我会先区分方法、协议和个人证据。对 UWM，论文 Table II 的五任务均值来自 OOD initialization、背景物体改造和三次 finetune seed；frozen repo 默认 rollout 是 random reset，而我现有材料记录的是 fixed-pruned-init，所以不能只因任务相同就叫 strict reproduction。我会把本地 setting 命名成独立 protocol，补 checkpoint、normalizer、init ID、chunk/horizon 与 250 条 episode record，只和完全相同 protocol 的 baseline 做 paired comparison。对 WAM，action/world/value 的离线 loss、direct-policy success 和 planning uplift 是三层证据；若要说 auxiliary 帮助 action，必须做 action-only、+world、+value、all 四臂消融，再配 action intervention、value calibration 和 same-init closed-loop trace。缺 artifact 的数字我只当 claim queue，不当个人已验证结果。”

## 十六题覆盖矩阵

| ID | 本页核心位置 | 已给出的机制 | 项目挂钩 | 状态 |
| --- | --- | --- | --- | --- |
| VLA-WM-001 | World model boundary | probability contract、policy/simulator/reward/value 边界 | UWM/Cosmos/WAM claim boundary | knowledge drafted / card unseen |
| VLA-WM-002 | Variable contract | observation/state/latent/reward/continuation 与 POMDP | dataset/eval schema | knowledge drafted / card unseen |
| VLA-WM-003 | Dynamics | deterministic/probabilistic、ensemble 与 uncertainty | world prediction risk | knowledge drafted / card unseen |
| VLA-WM-004 | RSSM data flow | encoder、posterior/prior、decoder/reward/continue heads | DreamerV3 reimplementation boundary | knowledge drafted / card unseen |
| VLA-WM-005 | Rollout validity | one-step、compounding、horizon error | UWM/WAM open-loop proxy | knowledge drafted / card unseen |
| VLA-WM-006 | Train/eval gap | teacher forcing、scheduled sampling、open-loop | data/rollout contract | knowledge drafted / card unseen |
| VLA-WM-007 | Uncertainty | aleatoric/epistemic、risk-sensitive planning | calibration/OOD | knowledge drafted / card unseen |
| VLA-WM-008 | Actionability | action condition、sensitivity、causal alignment | UWM/Cosmos world head | knowledge drafted / card unseen |
| VLA-WM-009 | Usage boundary | auxiliary representation vs queryable simulator | WAM planning claim | knowledge drafted / card unseen |
| VLA-WM-010 | Model bias | planner exploitation、value bias、recovery | UWM/WAM failure diagnosis | knowledge drafted / card unseen |
| VLA-WM-039 | Strict Protocol | 12-field tuple、paired effect、run/episode manifest | UWM three-protocol split | knowledge drafted / card unseen |
| VLA-WM-040 | Metric Ladder | L0–L5、compounding、rank validation | WorldGym/UWM/WAM | knowledge drafted / card unseen |
| VLA-WM-041 | Offline→Online Ablation | 2×2 factorial、interaction、断点矩阵 | WAM/UWM auxiliary | knowledge drafted / card unseen |
| VLA-WM-042 | Consistency Tests | action sensitivity、causal alignment、physical violation | UWM/Cosmos world head | knowledge drafted / card unseen |
| VLA-WM-043 | Failure Trace | first divergence、taxonomy、data routing | LIBERO/RoboCasa 0-success | knowledge drafted / card unseen |
| VLA-WM-044 | Evidence Audit | five-layer chain、labels、claim ledger | 五项目 truth boundary | knowledge drafted / card unseen |

知识与题卡覆盖不等于面试掌握。本批 16 个知识节点的上游关键事实已完成对应 source review，16 张题卡均为 unseen、尚未真实口述；因此不能标记 drilled 或 mastered，整体 review 仍为 WARN。

## Bad Case 与最小检查清单

| Bad case | 最小检查 | 需要避免的解释 |
| --- | --- | --- |
| task 名相同但结果差 4.6pp | 完整 \(\mathcal P\) diff | 直接归因 checkpoint质量 |
| total loss 降、success 不变 | component loss + factorial arms | “多任务一般有用” |
| video好看、action无效 | action swap + cloned-state alignment | “画面真实所以 dynamics正确” |
| value MAE低、N 越大越差 | calibration + N/selector sweep | “采样不够多” |
| fixed-init高、random-reset低/反之 | init distribution + same checkpoint | 选更高分作为正式成绩 |
| 0-success | protocol→action→controller first divergence | 先怪 world-model backbone |
| 两条 episode被删除 | raw records + predeclared invalid rule | 事后清洗仍称官方分数 |
| simulator成功 | real paired trials + safety trace | “已完成 Sim2Real” |

## 后续工作

1. 已完成 `VLA-WM-001..010` foundations 与 `VLA-WM-039..044` evaluation 的知识页和 16 张题卡；全部 `unseen`。
2. 下一步优先真实口述或补 UWM/WAM raw artifacts；不生成 `WM-011..038`。
3. 若找到用户的 UWM/WAM run bundle，优先建立 checkpoint/config/stats/episode manifest，不先改强回答。
4. 本增量在渲染与静态校验后停止；后续仅在新的 source-ready 小批被明确选择后继续，不一次性生成剩余 28 个知识节点。

## 参考文献（References）

1. [VOL 04 Source Audit A：World Model Foundations](../sources/vol_04_world_model_foundations_claim_to_code.html)，World Models/PlaNet/Dreamer、one-step/open-loop/closed-loop 与 metric boundary；canonical [Markdown](../sources/vol_04_world_model_foundations_claim_to_code.md)。
2. [VOL 04 Source Audit B：UWM Video / Action Diffusion](../sources/vol_04_uwm_video_action_claim_to_code.html)，frozen UWM model、metric、normalizer、wrapper 与 reset-style 边界；canonical [Markdown](../sources/vol_04_uwm_video_action_claim_to_code.md)。
3. [VOL 04 Source Audit C：Cosmos Policy / WAM](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)，action/future/value routing、best-of-N、offline/online 与 eval contract；canonical [Markdown](../sources/vol_04_cosmos_policy_wam_claim_to_code.md)。
4. [VOL 04 Source Audit D：Sim2Real](../sources/vol_04_sim2real_claim_to_mechanism.html)，六层 reality gap、paired test、failure attribution 与真实性边界；canonical [Markdown](../sources/vol_04_sim2real_claim_to_mechanism.md)。
5. [VOL 04 Source Audit E：Benchmark / Evidence](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)，12-field protocol、UWM/Cosmos/RoboCasa/WorldGym 可比性与 local manifest；canonical [Markdown](../sources/vol_04_benchmark_evidence_claim_to_protocol.md)。
6. Zhu et al., “Unified World Models: Coupling Video and Action Diffusion for Pretraining on Large Robotic Datasets”, arXiv `2504.02792v3`, [Table II](https://arxiv.org/html/2504.02792v3#S4.T2) 与 Appendix A。
7. WEIRDLabUW, `unified-world-model` frozen commit `b7d4067c8859775e5b08f681e76d538015cdd445`: [eval_robomimic.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/experiments/uwm/eval_robomimic.py), [wrappers.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/environments/robomimic/wrappers.py)；frozen tree 未发现 LICENSE。
8. Lifelong Robot Learning, `LIBERO` frozen commit `8f1084e3132a39270c3a13ebe37270a43ece2a01`: [metric.py](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/lifelong/metric.py), [eval config](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/configs/eval/default.yaml), MIT。
9. Kim et al., “Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning”, arXiv `2601.16163v1`, [HTML](https://arxiv.org/html/2601.16163v1)。
10. NVIDIA, `cosmos-policy` frozen commit `18a2accadf4e7a3531e56754102af5a24d2316da`: [LIBERO runner](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/libero/run_libero_eval.py), [RoboCasa runner](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/robocasa/run_robocasa_eval.py), Apache-2.0 code。
11. Quevedo et al., “WorldGym: World Model as An Environment for Policy Evaluation”, arXiv `2506.00613v3`, [arXiv](https://arxiv.org/abs/2506.00613v3)。
12. `world-model-eval/world-model-eval` frozen commit `709665b29f5c95124e7dbc05b0d4d47cd353de97`: [utils.py](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/utils.py), [world_model.py](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/world_model.py)；frozen tree 未发现 LICENSE。
13. MuJoCo official docs, [Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html) / [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)；robosuite 1.5 [Controllers](https://robosuite.ai/docs/modules/controllers.html)，accessed 2026-07-16。
14. 本地待核验材料：[UWM / LIBERO 项目页](../../05_uwm_libero_eval_protocol.html)。该页的 74.4%/92.8% 不替代 raw run artifacts。
15. 本地待核验材料：[Cosmos / WAM 项目页](../../04_cosmos_wam_multitask_training.html)。该页的 MSE、84/118 与 0-success narrative 不替代 checkpoint/episode evidence。
16. [VOL 04 Batch 1 独立事实复核](../sources/vol_04_batch1_independent_fact_review.html)；canonical [Markdown](../sources/vol_04_batch1_independent_fact_review.md)，状态：[`review`](../sources/vol_04_batch1_independent_fact_review.review.json)。
17. [VOL 04 Foundations 独立事实复核](../sources/vol_04_world_model_foundations_independent_fact_review.html)；canonical [Markdown](../sources/vol_04_world_model_foundations_independent_fact_review.md)，状态：[`review`](../sources/vol_04_world_model_foundations_independent_fact_review.review.json)。
