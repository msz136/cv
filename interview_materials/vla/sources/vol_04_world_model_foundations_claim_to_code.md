# VOL 04 Source Audit A：World Model / PlaNet / DreamerV3 Foundations Claim-to-Code

> 审计日期：2026-07-16  
> 状态：`drafted / upstream_paper_and_code_reviewed / independent_reviewed_slice / next_knowledge_batch`  
> 覆盖题目：`VLA-WM-001..014`、`VLA-WM-019..021`  
> 本页目的：把 world model 的输入输出合同、latent dynamics、one-step 与 rollout、RSSM、imagination actor-critic 以及评估边界固定成可审计的面试知识。UWM、Cosmos/WAM、LIBERO/RoboCasa 的项目数字不在本页作通用方法证据。

## 1. 结论先行

1. **World model 不是“能生成视频的模型”的同义词。**它是一个条件预测器：给定观测历史、动作以及必要的任务条件，预测未来 latent/observation、reward 和 termination/continuation。是否能支持 action consequence、长时 rollout 或 planning，取决于这些变量和训练/评估合同，而不是画面是否逼真。[1][2][3]
2. **早期 World Models 把视觉压缩和时序预测分开。**VAE 将图像压成 latent，MDN-RNN 建模 \(p(z_{t+1}\mid a_t,z_t,h_t)\)，小 controller 再读取 latent 与 recurrent state；论文甚至在 learned dream 中训练 controller，但这同时暴露了 model exploitation 风险。[1]
3. **PlaNet 的核心是 belief-state latent dynamics + online planning。**它同时使用 deterministic 与 stochastic transition，并用 latent overshooting 让多步 latent prediction 受约束；论文明确把模型误差、误差累积、多未来和 OOD 过度自信列为 planning 难点。[2]
4. **DreamerV3 的 RSSM 将 posterior observation update 与 prior action-conditioned imagination 分开。**论文公式中的 \(h_t=f_\phi(h_{t-1},z_{t-1},a_{t-1})\)、posterior \(q_\phi(z_t\mid h_t,x_t)\)、prior \(p_\phi(\hat z_t\mid h_t)\)、reward/continue/decoder heads，在 frozen repo 中分别对应 `RSSM.observe`、`RSSM.imagine`、`RSSM.loss` 与 `Agent.loss`。[3][4]
5. **Dreamer 的 actor/critic 训练不是把真实像素再喂一遍。**它从 replay 后验状态起点，在 prior dynamics 中生成 imagined latent trajectory，预测 reward/continue，再用 \(\lambda\)-return 更新 actor/critic；world model、actor、critic 的梯度边界由 `stop_gradient` 和不同 loss 路径共同决定。[3][4]
6. **one-step 指标下降不能证明 rollout 可用。**teacher-forced one-step 使用真实上一步 latent/observation；open-loop rollout 使用模型自己的上一步预测。误差可累积，且 action-insensitive、posterior collapse、背景 shortcut 会让 pixel/latent proxy 与 downstream success 脱钩。[2][3]
7. **reward、value、success classifier、termination predictor 不是一回事。**reward 是一步即时任务信号，value 是策略条件下的未来回报估计，success classifier 是评估或目标标签，continuation/termination 表示 episode 是否继续。把它们混成一个“好坏分数”会导致 planning 和审计错误。[3][4]
8. **随机性必须分层。**aleatoric uncertainty 是环境本身的多可能结果，epistemic uncertainty 是数据/模型知识不足；ensemble、posterior samples、disagreement 或 calibrated likelihood 只是估计手段，不能自动等价于真实风险。[2][3]
9. **“action-conditioned”仍不自动等于“可干预”。**如果动作只与背景变化相关、动作覆盖窄、数据存在 confounder，模型可能在观测预测上很好却不反映执行该动作的因果后果；需要 counterfactual/action-swap、action sensitivity 和 closed-loop tests。[2]
10. **DreamerV3 repo 的实现边界必须明说。**README 自称基于 DreamerV2 的 reimplementation，与 Google/DeepMind 无关；它是逐行实现证据，不应被描述为论文作者发布的官方代码，也不能由 repo 直接证明个人项目结果。[4]

## 2. 证据层级与冻结对象

| 层级 | 冻结对象 | 本页支持 | 本页不支持 |
| --- | --- | --- | --- |
| [1] 论文 | Ha & Schmidhuber, *World Models*, arXiv `1803.10122`，ar5iv HTML 已保存于 `%TEMP%\\vol04-papers\\worldmodels.html` | VAE/MDN-RNN/controller 分解、dream training、模型漏洞边界 | 现代 RSSM、机器人 action schema、本地项目 |
| [2] 论文 | Hafner et al., *Learning Latent Dynamics for Planning from Pixels*（PlaNet），arXiv `1811.04551`，ar5iv HTML 已保存于 `%TEMP%\\vol04-papers\\planet.html` | latent planning、stochastic+deter­ministic transition、latent overshooting、multi-step/OOD 难点、CEM planning | DreamerV3 的实现、VLA 项目指标 |
| [3] 论文 | Hafner et al., *Mastering Diverse Domains through World Models*（DreamerV3），arXiv `2301.04104`，ar5iv HTML 已保存于 `%TEMP%\\vol04-papers\\dreamer.html` | RSSM 合同、world-model/actor/critic 分工、imagined trajectories、λ-return、symlog/KL/free-bits 设计 | frozen repo 的 exact defaults、用户项目结果 |
| [4] 代码 | `danijar/dreamerv3` frozen commit `e3f02248693a79dc8b0ebd62c93683888ddaccfe` | `rssm.py` observe/imagine/loss、`agent.py` loss graph、config scales/horizon、repo disclaimer | 论文作者官方实现、checkpoint 兼容性、个人贡献 |
| 同源推断 | [1]–[4] 联合分析 | one-step/rollout gap、metric contract、最小测试矩阵 | 未运行的 rollout 成功、未见的本地数据与数字 |

**许可证与可复现边界：**GitHub metadata 将 frozen Dreamer repo 标为 MIT，但本页引用的代码语义仍需以 commit 为准；repo README 明确写 `reimplementation`，因此 license、作者归属、论文结果和本地使用应分别记录。论文 HTML 与 repo commit 已验证，论文 source tar、checkpoint、运行环境和浏览器视觉 QA 未作为已完成证据。

## 3. World model 的概率合同

### 3.1 直觉：在内部预测“采取动作后会发生什么”

普通视频预测只需回答“下一帧像什么”；用于控制的 world model 还要回答“如果我执行动作 \(a_t\)，未来状态、奖励和终止概率怎样变化”。它可以在 pixel、state 或 latent 空间运行，但必须明确 condition、预测 horizon、随机采样方式和输出单位。

专业地，令 \(o_t\) 是观测（observation），\(s_t\) 是隐藏/真实状态（state），\(a_t\) 是动作，\(r_t\) 是即时 reward，\(c_t\) 是 continuation/是否继续。一个最小 action-conditioned 合同是：

\[
p_\theta(z_{t+1},r_{t+1},c_{t+1}\mid z_{\le t},a_{\le t},g),
\]

其中 \(z_t\) 可以是观测压缩后的 latent，\(g\) 是任务/语言条件（若存在）。变量解释：\(p_\theta\) 是模型学习的条件分布，不要求把每一帧都还原到 RGB；实现上必须能指出 latent transition、reward head、continue head 的输入输出。该表达是跨方法的合同框架，DreamerV3 的具体 factorization 见第 6 节；它不是某个项目的已验证接口。[2][3][4]

### 3.2 observation、state、latent、reward、termination 如何取舍

| 变量 | 作用 | 典型监督 | 缺失时风险 |
| --- | --- | --- | --- |
| observation \(o_t/x_t\) | 传感器实际看到的像素、proprio 或多模态输入 | reconstruction / observation likelihood | latent 可能只学 reward shortcut |
| state/belief \(s_t\) | 决策所需但可能不可直接观测的状态 | filtering、latent consistency、任务监督 | POMDP 下记忆不足 |
| latent \(z_t,h_t\) | 便于压缩、预测和 planning 的表示 | posterior/prior、KL、multi-step consistency | 表示错位或 collapse |
| reward \(r_t\) | 一步任务信号 | reward prediction | 想象规划无法比较后果 |
| continuation \(c_t\) / termination | episode 是否还在继续 | Bernoulli head / environment flag | return bootstrapping、horizon 被算错 |
| action \(a_t\) | 干预变量 | transition condition、action sensitivity test | 只能做相关性预测 |

面试中先问“这个模型到底预测哪一个变量、在什么时间索引、使用真实还是模型历史”，比直接背“world model = dynamics model”更可靠。

### 3.3 与相邻模块的边界

- **policy**：给定当前信息选择动作 \(\pi(a_t\mid s_t)\)；world model 预测 action 后果，二者可联合训练但语义不同。
- **environment simulator**：由物理/规则引擎定义的真实交互对象；learned world model 是近似分布，可能在 OOD 或长 rollout 失真。
- **reward model**：只预测/定义 reward；它不必能重建观测或预测 action consequence。
- **value model**：预测给定 policy/return convention 下的未来累计回报；它不是 continuation，也不是物理动力学。
- **video generator**：若不接受 action 或不预测 reward/termination，就只能证明视觉先验；是否 actionable 必须用 intervention 与 closed-loop test 验证。

## 4. World Models：VAE、MDN-RNN 与 dream 中的 controller

### 4.1 论文方法的最短证据链

World Models 论文先用 VAE 将高维图像 frame 压缩为 latent vector，再用 MDN-RNN 预测下一个 latent 的概率分布，最后用小 controller 从 latent 与 RNN hidden state 产生动作。论文摘要和第 2 节明确指出：world model 训练是无监督的，controller 可以完全在模型自己的 hallucinated dream 中训练，再转回真实环境。[1]

MDN-RNN 的条件形式可以写为：

\[
p_\theta(z_{t+1}\mid a_t,z_t,h_t)
=\sum_{k=1}^{K}\pi_k(h_t,z_t,a_t)\,
\mathcal N\!\left(z_{t+1};\mu_k,\Sigma_k\right),
\]

其中 \(h_t\) 是 recurrent hidden state，\(K\) 是 mixture components，\(\pi_k,\mu_k,\Sigma_k\) 是 mixture weight、mean、covariance。直觉是让模型表达多个可能未来，而不是只输出平均 latent；实现映射是 MDN 输出分布参数后采样 \(z_{t+1}\)，不是对 RGB 像素做单一 MSE。[1]

### 4.2 dream training 的收益与漏洞

在 learned dream 里训练 controller 可以省去反复渲染真实环境、把训练信号放在紧凑 latent 空间，并使 controller 很小。[1] 但模型可能存在“漏洞”：policy 学会触发 world model 的分布外错误，使 dream reward 很高，真实环境却失败。这个现象是 model bias 与 model exploitation 的早期例子，不能用 dream return 替代 real rollout success。

最小审计问题：

1. dream 的初始 latent 来自真实观测还是纯模型生成？
2. rollout horizon、多次采样和 termination 如何处理？
3. policy 是否在真实数据分布之外行动？
4. dream reward 与真实 reward 是否在同一 contract、同一单位、同一 success predicate 下？

## 5. PlaNet：belief-state latent planning

### 5.1 为什么需要 deterministic + stochastic transition

PlaNet 从 pixels 学习 latent dynamics，并在线在 latent space 规划动作。论文摘要强调其 transition model 同时含 deterministic 和 stochastic components；这对 partial observability、contact dynamics 和多未来尤为重要。[2]

可用一个抽象 RSSM 写成：

\[
h_t=f_\theta(h_{t-1},z_{t-1},a_{t-1}),\qquad
z_t\sim q_\phi(z_t\mid h_t,o_t),
\]

\[
\hat z_t\sim p_\theta(\hat z_t\mid h_t),\qquad
\hat r_t\sim p_\theta(r_t\mid h_t,z_t).
\]

变量解释：\(h_t\) 保存动作与历史，\(z_t\) 表示当前观测提供的 stochastic belief，posterior \(q\) 使用真实观测，prior \(p\) 在 imagination 时只依赖历史与动作。实现映射：planning 期间不能偷偷读取未来真实 observation，否则不再是 open-loop latent planning。[2]

### 5.2 latent overshooting 的作用

单步 KL 只约束一步 prior/posterior；latent overshooting 将更远的 multi-step prior 与 posterior 也纳入变分目标，使模型对长期 latent transition 更一致。其目的不是保证 RGB 细节漂亮，而是提升 reward-relevant long-horizon prediction；PlaNet 论文明确将它描述为 generalized variational objective。[2]

抽象的 (k)-step 正则可写为：

\[
\mathcal L_{\mathrm{over}}^{(k)}
=\mathbb E\left[
\operatorname{KL}\left(
q_\phi(z_{t+k}\mid o_{\le t+k},a_{<t+k})
\;\middle\|\;
p_\theta^{(k)}(z_{t+k}\mid h_t,a_{t:t+k-1})
\right)\right].
\]

这里 \(p_\theta^{(k)}\) 是从当前 belief 连续执行 \(k\) 个动作得到的 prior；它是对 PlaNet 机制的形式化表达，变量、方向和是否加权必须按具体实现确认。不能把它误说成“多步 pixel MSE”。[2]

### 5.3 online planning 与 receding horizon

PlaNet 在每次决策时从当前 belief 初始化 action-sequence distribution，用 CEM 等方法采样、在 latent model 中 rollout、按 predicted reward 选择动作，并只执行第一步/短段后重新观测和规划。[2] 这是一种 receding-horizon contract：增加 planning compute 可能提升搜索，但会增加 latency；模型偏差越大，越应该缩短 open-loop execution 和增加真实观测校正。

## 6. DreamerV3 RSSM：论文合同到 frozen repo

### 6.1 论文中的完整 factorization

DreamerV3 论文给出 RSSM 的核心关系：

\[
h_t=f_\phi(h_{t-1},z_{t-1},a_{t-1}),\quad
z_t\sim q_\phi(z_t\mid h_t,x_t),\quad
\hat z_t\sim p_\phi(\hat z_t\mid h_t),
\]

\[
\hat r_t\sim p_\phi(\hat r_t\mid h_t,z_t),\quad
\hat c_t\sim p_\phi(\hat c_t\mid h_t,z_t),\quad
\hat x_t\sim p_\phi(\hat x_t\mid h_t,z_t).
\]

其中 \(x_t\) 是 sensory input，\(z_t\) 是 stochastic representation，\(h_t\) 是 deterministic recurrent state，\(a_t\) 是 action，\(r_t\) 是 reward，\(c_t\) 是 continuation。posterior 使用观测进行 filtering；prior 不读当前观测，因而可用于 imagined rollout。[3]

### 6.2 `rssm.py` 的逐行映射

| 机制 | frozen commit 证据 | 面试口径 |
| --- | --- | --- |
| state shape | `dreamerv3/rssm.py` `entry_space`：`deter=[B,4096]`、`stoch=[B,32,32]`（默认配置） | stochastic latent 是 grouped categorical representation；不要只说一个连续向量 |
| posterior observe | `observe` / `_observe`：读取 `tokens, action, reset`，先 `_core` 再 `_logit('obslogit', ...)`，从 `_dist(logit).sample` 得到 stoch | 真实序列用 observation posterior 更新 belief |
| prior imagine | `imagine`：由 policy 产生 action，调用 `_core` 与 `_prior(deter)`，采样 prior stoch | imagined sequence 不读未来 observation |
| dynamics loss | `loss`：`dyn = KL(stop_gradient(post) ∥ prior)`、`rep = KL(post ∥ stop_gradient(prior))`，可用 `free_nats` 截断 | dyn/rep 两个方向表达不同梯度边界，不能只写“一个 KL” |
| reset | `_observe` 对 `reset` mask carry/action | episode 边界必须进入 world-model state contract |
| action normalization | `_core` 中按 stop-gradient 最大绝对值缩放 action | 这是 repo 实现细节，不应泛化成所有 RSSM 的必然设计 |

### 6.3 KL balancing、free nats 与 collapse

DreamerV3 的 `rssm.py` 用两项 KL：

\[
\mathcal L_{\mathrm{dyn}}=
\operatorname{KL}(\operatorname{sg}(q)\|p),\qquad
\mathcal L_{\mathrm{rep}}=
\operatorname{KL}(q\|\operatorname{sg}(p)).
\]

`sg` 是 stop-gradient；前一项主要推动 prior 追 posterior，后一项主要推动 posterior 与 prior 对齐但不让 prior 通过该项获得梯度。repo 还用 `free_nats` 做下限裁剪，避免极小 KL 过早压掉 stochastic information。具体 loss scales 来自 `configs.yaml`，不能仅凭论文摘要声称某个数值是 universal default。[3][4]

常见 failure：

- **posterior collapse**：\(q(z_t\mid h_t,x_t)\) 忽略 observation，KL 接近零且重建/任务性能无改善；应检查 latent entropy、KL、observation ablation。
- **prior collapse / action ignoring**：prior 对 action 改变不敏感；做 action-swap、finite-difference 或 counterfactual rollout。
- **free-nats 过大**：可能让 KL 误差长期不回传，需看裁剪前后统计。
- **reset 泄漏**：episode 首帧 carry 未清空，导致跨 episode 信息污染。

## 7. DreamerV3 的 world-model loss、imagination 与 actor-critic

### 7.1 world-model loss 的组成

frozen `dreamerv3/agent.py` 的 `loss` 先编码 observation，再调用 `dyn.loss`，随后 decoder reconstruction、reward head 和 continuation head：

\[
\mathcal L_{\mathrm{wm}}
=\mathcal L_{\mathrm{dyn}}+\mathcal L_{\mathrm{rep}}
+\lambda_{\mathrm{rec}}\mathcal L_{\mathrm{rec}}
+\lambda_r\mathcal L_r
+\lambda_c\mathcal L_c.
\]

变量解释：\(\mathcal L_{\mathrm{rec}}\) 重建输入，\(\mathcal L_r\) 预测 reward，\(\mathcal L_c\) 预测 continuation，\(\lambda\) 由 `config.loss_scales` 展开；代码还可能为不同 observation key 复制 reconstruction scale。该式是对 repo loss dictionary 的结构化总结，不表示所有项目都使用相同 head 或权重。[3][4]

DreamerV3 论文还讨论 symlog prediction：decoder、reward predictor、critic 使用 symlog 形式以跨 reward scale 稳定训练。[3] 这是 DreamerV3 的设计，不应写成 world model 的必要组件。

### 7.2 imagined trajectory 的数据流

`Agent.loss` 的 imagination 流程是：

1. 从 replay sequence 的最后 \(K=\min(\texttt{imag\_last},T)\) 个 posterior states 取 starts；
2. 用 `policyfn` 从当前 latent feature 采样 action；
3. `dyn.imagine(starts, policyfn, H, ...)` 通过 prior dynamics 生成 (H) 步 latent/action；
4. reward/continue/policy/value heads 作用于 imagined features；
5. `imag_loss` 用 λ-return、advantage 和 entropy 更新 actor/critic；
6. 可选 replay value loss 直接用真实 replay features 做 value regularization。

用张量合同表达：

\[
s_0\sim q_\phi(s_t\mid x_{\le t},a_{<t}),\quad
a_{1:H}\sim\pi_\theta(\cdot\mid s_{0:H-1}),\quad
s_{1:H}\sim p_\phi(\cdot\mid s_{0:H-1},a_{1:H}).
\]

变量 \(s_t=(h_t,z_t)\) 是 RSSM feature；前缀 \(s_0\) 来自真实 replay，之后的 \(s_{1:H}\) 是模型想象。这样既利用真实数据校准起点，又避免每个 actor update 都与真实环境交互。[3][4]

### 7.3 actor、critic 与 λ-return

论文把 actor 写成 \(a_t\sim\pi_\theta(a_t\mid s_t)\)，critic 写成 \(v_\psi(s_t)\approx\mathbb E_{p_\phi,\pi_\theta}[R_t]\)。frozen repo 的 `imag_loss` 计算 continuation-weighted return、advantage、policy log-probability/entropy 与 value target；`lambda_return` 反向递推得到 bootstrap return。[3][4]

可用标准形式概括：

\[
R_t^\lambda=r_t+\gamma c_t\big((1-\lambda)v_\psi(s_{t+1})
+\lambda R_{t+1}^\lambda\big).
\]

这里 \(c_t\) 是 continuation mask，\(\gamma\) 是 discount，\(\lambda\) 控制 bootstrap 与多步 return 的混合。实现映射：repo 先从 `con` 与 `term/last` 生成 `weight`，再调用 `lambda_return`；具体 `disc` 还受 `contdisc` 与 `horizon` 配置影响。[4]

### 7.4 梯度边界与 model bias

Dreamer 的 actor/critic 依赖 model-generated states，因此 world model bias 会进入 imagined return。repo 通过 `sg`、`ac_grads`、`reward_grad`、`repval_grad` 等配置控制哪些梯度可回到 world model；不能笼统说“actor loss 反向更新整个 world model”。

如果 world model 在 OOD state 上高估 reward/value，actor 会主动寻找模型漏洞；典型防护包括：缩短 imagination horizon、增加真实数据覆盖、ensemble/disagreement penalty、uncertainty-aware value、receding-horizon replan，以及把 imagined proxy 与 real success 分开报告。[2][3][4]

## 8. one-step、teacher forcing、open-loop rollout 与 scheduled sampling

### 8.1 四种 protocol 必须拆开

| Protocol | 下一步输入 | 证明什么 | 不能证明 |
| --- | --- | --- | --- |
| teacher-forced one-step | 真实 \(o_t/z_t\) + \(a_t\) | 局部条件预测能力 | 长时稳定、闭环成功 |
| teacher-forced multi-step | 每步仍注入真实 latent/observation | 多步监督下的局部一致性 | 纯模型 rollout |
| open-loop rollout | 第一步后使用模型自己的预测 | 误差累积与长期稳定性 | 真实环境可控性 |
| closed-loop policy | 真实环境重新观测并执行动作 | 任务成功与控制合同 | world model 所有细节都正确 |

**scheduled sampling** 在训练中以一定概率把模型自己的预测替代真实历史，试图缩小 train/eval exposure bias；但它会改变训练分布、梯度路径和目标一致性，不能当作免费修复。面试回答应给出 schedule、替换粒度（observation/latent/action）和真实评估 protocol。[2][3]

### 8.2 误差为何会累积

若单步误差为 \(e_t\)，局部 Lipschitz 常数约为 \(L\)，粗略上可有：

\[
\|\hat s_{t+k}-s_{t+k}\|
\lesssim\sum_{i=0}^{k-1}L^{k-1-i}e_{t+i}.
\]

这不是任一论文的 exact bound，而是解释 rollout compounding 的分析框架：当动力学放大误差（\(L>1\)）或进入训练分布外区域，长 horizon 误差可能超线性增长。应通过真实 open-loop traces、latent disagreement 和 downstream task probes 验证，而不是从 one-step MSE 外推 success。[2]

## 9. uncertainty、actionability 与可查询 simulator 边界

### 9.1 aleatoric vs epistemic

- **Aleatoric**：同一 state/action 即使无限数据仍有多个结果，例如接触摩擦、遮挡后的不可见分支、随机环境；应输出条件分布或采样多模态结果。
- **Epistemic**：模型没见过该 state/action 或数据不足，随着覆盖增加理论上可降低；ensemble disagreement、dropout/posterior sampling、density/novelty score 是代理。

二者在 planning 中不同：aleatoric 可通过风险敏感期望/分位数处理；epistemic 更适合触发探索、保守 penalty 或 fallback。单个 Gaussian variance 无法自动区分两种来源。[2]

### 9.2 video model 什么时候 actionable

至少需要同时满足：

1. action 明确进入 transition condition，并做 action-swap/counterfactual 检验；
2. 预测变量含 reward、termination 或与控制目标有可验证关联；
3. open-loop 与 closed-loop 评估使用固定 schema、horizon、normalizer 和 reset；
4. 在分布外/失败轨迹上检查物理一致性与 action sensitivity。

否则最多称为“视觉预测器/视频生成器”。同一模型可以具备视频生成能力而没有可用 dynamics；不能用 FVD、PSNR 或画面主观质量直接证明 policy 成功。[1][2][3]

### 9.3 auxiliary representation vs queryable simulator

**辅助表示**：只要求 encoder/latent 对 action policy、reward 或 representation learning 有帮助；可不解码像素、可不支持任意 counterfactual action。

**可查询 simulator**：给定任意候选 action sequence，能在明确概率合同下预测未来 state/observation/reward/termination，且有 rollout horizon、uncertainty 和 reset 语义；planning 或 best-of-N 才能把它当作模拟器。

回答项目问题时，先写“本实验只用 world head 作为 auxiliary loss”还是“eval 真的查询 world model 选择 action”，否则很容易把 multi-task pretraining 夸成 model-based control。

## 10. metric boundary：proxy 不是 success

| 指标 | 主要证明 | 常见误读 |
| --- | --- | --- |
| PSNR/SSIM | 像素重建局部相似 | 认为物理、动作、任务都正确 |
| FVD/视频感知分数 | 视频分布/视觉质量（依实现而定） | 认为 action consequence 正确 |
| latent KL / reconstruction | 表示与 dynamics 训练目标拟合 | 认为长 horizon 可规划 |
| reward/value MSE | 任务信号预测或价值拟合 | 认为 controller closed-loop success |
| action MSE | 行为标签拟合 | 认为 rollout 不会漂移 |
| open-loop rollout error | 模型自回归稳定性 | 认为真实环境能执行 |
| closed-loop success | 固定 protocol 下的任务结果 | 不能单独解释 world model 哪个 head 正确 |

最小可比报告应同时记录 horizon、teacher forcing/open-loop、任务 split、reset、episode 数、seed、normalizer、checkpoint 和 success predicate。没有这些字段，数字只能作为方向性 context，不能声称“world model 更好”。

## 11. 从论文到代码的最小审计矩阵

| Claim | 论文证据 | frozen repo 证据 | 仍未证明 |
| --- | --- | --- | --- |
| RSSM posterior/prior 分离 | DreamerV3 Eq. 3 / Figure 3 | `rssm.py` `observe` vs `imagine` | 用户项目是否复用此 RSSM |
| reward/continue/reconstruction heads | DreamerV3 World Model Learning | `agent.py` `rew`, `con`, `dec` 与 `loss` | head 的本地数据字段、权重和结果 |
| latent imagination actor-critic | DreamerV3 Eq. 6–7 | `Agent.loss` imagination + `imag_loss` | 任何具体 VLA/WAM downstream gain |
| KL balancing/free nats | DreamerV3 训练目标与 appendix | `rssm.py` `dyn/rep/free_nats`；`configs.yaml` scales | 不同配置的可比性 |
| latent overshooting | PlaNet paper | DreamerV3 frozen repo README/代码未作为同一机制证据 | DreamerV3 是否启用 PlaNet overshooting |
| dream controller | World Models paper | 无需现代 repo 才成立 | 真实机器人可迁移性 |

## 12. 面试答题骨架与失败追问

### 12.1 30 秒主回答

“我会先把 world model 定义成 action-conditioned 的未来分布，而不是泛化成视频生成器。输入通常是 observation/history/action，输出至少要明确 latent/observation、reward 和 continuation。World Models 是 VAE+MDN-RNN 的早期分解；PlaNet 在 stochastic+deter­ministic latent belief 上在线规划，并用 latent overshooting 约束多步；DreamerV3 用 RSSM 的 posterior 从真实 observation 更新起点，再用 action-conditioned prior 做 imagination，reward/continue head 生成 return，actor/critic 在想象轨迹上更新。判断它是否有用要把 one-step、open-loop、closed-loop success 分开，并审计 action sensitivity、uncertainty、reset、normalizer 和模型漏洞。”

### 12.2 面试官继续追问时的机制点

- “为什么 one-step MSE 很低还会失败？”——真实历史 vs 自回归历史、error compounding、OOD、action ignoring。
- “Dreamer 的 posterior/prior 为什么分开？”——posterior 可用当前观测做 filtering；prior 才能在 imagination 不读未来观测。
- “reward head 和 value head 有何区别？”——一步信号 vs policy-conditioned cumulative return；训练/评估时间索引不同。
- “如何证明是 action-conditioned？”——action intervention/swap、finite difference、counterfactual rollout、real controller test。
- “DreamerV3 repo 是官方代码吗？”——不是；README 自称 reimplementation，论文事实和代码证据分开。

## 13. 当前证据边界与后续动作

- 已核实：World Models、PlaNet、DreamerV3 论文 HTML；DreamerV3 frozen commit 的 README、RSSM observe/imagine/loss、Agent world-model/imagination/replay-value loss、configs loss scales/RSSM/imagination horizon。
- 尚未核实：PlaNet source tar、Dreamer repo checkpoint 与 exact paper result reproduction、任何用户本地 world-model/WAM/UWM artifact、浏览器视觉 QA、真实口述。独立 frozen-source 事实复核已记录在 [复核报告](vol_04_world_model_foundations_independent_fact_review.html)。
- 不写入本页：UWM/Cosmos 的 action/video/value slots、LIBERO/RoboCasa strict 数字、WAM/UWM 的本地 MSE/success、个人贡献边界；这些要到对应 Source Audit 与 VOL 07 项目证据后再写。
- 下一步：基于独立复核先生成 `VLA-WM-001..010` 知识页；之后再进入 Source Audit B（UWM）的完整审查，确认 video/action diffusion、license、checkpoint、mask/horizon 与 LIBERO eval contract。

## 14. 参考文献（References）

1. Ha & Schmidhuber, “World Models”, 2018. [arXiv](https://arxiv.org/abs/1803.10122)；本地论文快照：`%TEMP%\\vol04-papers\\worldmodels.html`。
2. Hafner et al., “Learning Latent Dynamics for Planning from Pixels” (PlaNet), 2019. [arXiv](https://arxiv.org/abs/1811.04551)；本地论文快照：`%TEMP%\\vol04-papers\\planet.html`。
3. Hafner et al., “Mastering Diverse Domains through World Models” (DreamerV3), 2023/2025. [arXiv](https://arxiv.org/abs/2301.04104)；本地论文快照：`%TEMP%\\vol04-papers\\dreamer.html`。
4. `danijar/dreamerv3`, frozen commit `e3f02248693a79dc8b0ebd62c93683888ddaccfe`. [GitHub](https://github.com/danijar/dreamerv3/tree/e3f02248693a79dc8b0ebd62c93683888ddaccfe)；重点文件：[`rssm.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/rssm.py)、[`agent.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/agent.py)、[`configs.yaml`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/configs.yaml)。
