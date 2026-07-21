# VOL 01 Foundations：机器人、深度学习与强化学习的共同语言

> 状态：`batch1+2+3_fact_reviewed_candidate / WARN`  
> 报告日期：2026-07-16  
> 证据截止：2026-07-16  
> 适用岗位：VLA / 具身智能算法 / 多模态机器人策略  
> 本卷不展开：VLA 专属 action head、Flow Matching 细节、World Model 训练细节和个人项目完整复盘；这些内容分别放到 VOL 03、VOL 04、VOL 07。

## 问题（Question）

本卷要让你能用同一套语言回答四类问题：

- **数据/模型问题**：observation、state、action、token、mask 和 loss 在张量层面是什么？
- **机器人问题**：坐标变换、Jacobian、控制频率、延迟和 action denormalization 为什么会影响闭环？
- **训练问题**：Transformer、归一化、MSE、交叉熵、Bellman target 和 advantage 各自监督什么？
- **评估问题**：离线 proxy、online success、reward、value 和 success predicate 为什么不能混为一谈？

### 口述目标

面试官问“你做 VLA 需要哪些基础”时，先给结论：

> VLA 不是只把图像和语言喂给大模型；它把观测和任务条件编码成策略输入，再把输出变成带坐标、尺度、时序和控制约束的动作。因而基础要同时覆盖表示学习、序列建模、机器人几何、控制延迟和闭环评估。

## 背景与动机

VLA 面试常见的失分不是完全不会某个名词，而是把不同层次混在一起：把 `state` 当成 `observation`，把离线动作 MSE 当成真实成功率，把 action token 当成控制器动作，把 reward 当成 value，或者把一个归一化配置当成算法创新。

本卷建立一条最小因果链：

```text
传感器 / 图像 / 语言 / proprioception
                ↓
       observation 与 state 表示
                ↓
   几何坐标、Transformer 表示、策略输出
                ↓
  normalization / denormalization / controller
                ↓
       robot closed-loop rollout 与评估
```

这条链既能解释一般 VLA，也能连接你的 OpenPiVLA、UWM、WAM 和 OPD 项目；但具体项目 claim 仍必须回到本地页面和日志，而不是由基础公式自动推出。

## 基础概念与术语

| 术语 | 口语解释 | 严谨边界 | 常见误区 |
| --- | --- | --- | --- |
| Observation | 机器人此刻能读到的传感器输入 | (o_t)，可能是不完整、有噪声的状态观测 | 直接把 observation 当完整 state |
| State | 足以决定未来转移的系统状态 | (s_t)，在 MDP 中定义转移与奖励 | 只要有一张图就一定是 state |
| Proprioception | 机器人自身关节/末端/速度等本体感知 | 状态向量的一部分，维度和坐标系需明确 | 不说明单位、顺序和时间戳 |
| Action | 策略发给控制器的控制量 | (a_t)，可为位置、速度、力矩或 chunk | 忽略 action 轴顺序、尺度和执行频率 |
| Policy | 从条件到动作的映射 | \(\pi_\theta(a_t\mid o_{\le t},c)\) | 把 action head 等同整个 policy |
| Closed loop | 执行动作后重新观测并纠偏 | rollout 中 \(o_t\to a_t\to o_{t+1}\) 的循环 | 把一次性序列预测当稳定执行 |
| Protocol | 评估时固定的初始化、归一化、步数和成功判定 | benchmark 的可比性条件 | 只比较最终百分比 |

## 几何、状态与控制

### Observation、State、Action 的层次

通俗地说，图像、关节角和任务文本是“模型看见的东西”，state 是描述系统未来演化所需的信息，action 是控制器真正执行的量。真实机器人通常只能获得部分 state，因此策略需要在历史 observation 或记忆上做推断。

专业地说，若系统满足 Markov 性质，状态转移可以写为 \(p(s_{t+1}\mid s_t,a_t)\)。实际 VLA 的输入往往是 \(o_t\)、历史帧、语言条件 \(c\) 和 proprioception 的组合，因此更安全的面试表述是“策略条件输入”，不要未经证据声称它拥有完整 state。

### 齐次坐标与坐标变换

在机器人学里，旋转和平移常合并到齐次变换矩阵：

\[
T_{ab}=
\begin{bmatrix}
R_{ab} & p_{ab}\\
0_{1\times3} & 1
\end{bmatrix},\qquad
\tilde p_a=T_{ab}\tilde p_b.
\]

变量解释：\(R_{ab}\in SO(3)\) 表示坐标系 \(b\) 到 \(a\) 的旋转，\(p_{ab}\) 是原点平移，\(\tilde p=[p_x,p_y,p_z,1]^\top\) 是齐次点。直觉是先把点放到统一的坐标协议里，才能比较 action、目标框或末端位姿。实现映射是矩阵乘法；但你当前仓库没有提供 OpenPiVLA 的具体坐标变换代码，因此只能把它作为通用基础，不能声称某个本地函数一定采用此轴序。

矩阵乘法顺序不可随意交换：

\[
T_{ac}=T_{ab}T_{bc},\qquad T_{ab}T_{bc}\ne T_{bc}T_{ab}.
\]

这解释了为什么相机坐标、机器人 base、末端坐标和世界坐标的命名必须写清楚；顺序错时，模型可能在数值上输出“合理”的动作，却在物理空间中朝错误方向运动。

### Forward Kinematics 与 Jacobian

给定关节角 \(q\)，forward kinematics 计算末端位姿 \(x=f(q)\)。局部速度关系由 Jacobian 给出：

\[
\dot x=J(q)\dot q.
\]

变量解释：\(\dot q\) 是关节速度，\(\dot x\) 可包含末端线速度和角速度，\(J(q)\) 是随姿态变化的 Jacobian。直觉是它把“关节空间的小动作”映射到“末端空间的小动作”；接近奇异位形时，\(J\) 的 rank 或条件数退化，在 inverse/伪逆映射中，为实现某些末端速度可能需要很大的关节速度，并放大测量噪声。实现上需要明确 Jacobian 的轴序、单位和参考坐标系；VLA 输出若是末端增量，仍需经过控制器或 IK 才能执行。

### Action 归一化、反归一化与执行

连续 action 常在训练前做逐维归一化：

\[
\hat a_t^{(i)}=\frac{a_t^{(i)}-\mu_i}{\sigma_i+\epsilon},\qquad
a_t^{(i)}=(\sigma_i+\epsilon)\hat a_t^{(i)}+\mu_i.
\]

这里 \(\mu_i,\sigma_i\) 是第 \(i\) 个动作维度的统计量，\(\hat a\) 是模型空间，\(a\) 是控制器空间。直觉是让不同单位和量级的轴在训练中有相近的数值尺度；实现中必须保证训练和推理使用同一版本 normalizer、轴顺序、gripper 约定和 clipping 规则。`denormalization` 正确不等于控制安全，还要检查控制频率、动作范围和执行窗口。

### PID 与延迟

最基础的 PID 控制器可以写为：

\[
u_t=K_Pe_t+K_I\sum_{k=0}^{t}e_k\Delta t+K_D\frac{e_t-e_{t-1}}{\Delta t}.
\]

\(e_t\) 是目标与当前状态的误差，\(u_t\) 是控制输出，\(\Delta t\) 是控制周期。P 项响应当前误差，I 项消除稳态偏差，D 项抑制变化过快；实现时需考虑积分饱和、导数噪声、derivative kick、滤波和输出限幅。VLA 负责高层动作并不意味着可以忽略底层控制器：推理延迟、观测延迟和 replan 间隔会改变闭环有效频率。

### Impedance Control、MPC 与 Learned Policy

这三类方法通常不在同一层竞争。impedance control 规定接触中的力—位移动态关系；MPC 用模型和约束滚动求解有限时域动作；learned policy/VLA 从高维观测与语言条件预测目标、动作或 action chunk。实际系统常让 VLA 给 subgoal/reference，再由 MPC、IK 或 impedance/controller 执行。

令 \(e=x-x_d\)，一种目标阻抗关系可写为：

\[
M_d\ddot e+D_d\dot e+K_de=F_{ext}.
\]

\(M_d,D_d,K_d\) 是期望惯性、阻尼和刚度，\(F_{ext}\) 是外部交互力。直觉是规定机器人受力后的动态响应，而不是只追踪位置。实现上必须说明力/位姿 frame、传感器、底层 torque/position loop、采样周期、饱和和滤波；“用了 impedance”不等于天然安全或稳定。

有限时域 MPC 可抽象为：

\[
\min_{u_{0:H-1}}
\sum_{k=0}^{H-1}\ell(x_k,u_k)+\ell_f(x_H),
\quad
x_{k+1}=f(x_k,u_k),
\quad
x_k\in\mathcal X,\ u_k\in\mathcal U.
\]

\(H\) 是规划 horizon，\(f\) 是动力学模型，\(\ell,\ell_f\) 是阶段/终端代价，\(\mathcal X,\mathcal U\) 是状态和控制约束。MPC 每次只执行第一步或短前缀后重新估计和求解；它能显式处理约束，但会受模型失配、状态估计、solver deadline 和 terminal design 影响。

learned policy 可写为 \(\pi_\theta(a_t\mid o_{\le t},c)\) 或 chunk distribution。它擅长视觉/语言条件与复杂数据分布，却仍依赖 action normalization、frame/unit、controller rate、replan、safety limit 和 success predicate。模型输出可能是直接 action、末端目标、MPC reference 或 residual；接口语义不同，不能仅按维度判断。

| 场景 | 合理组合 | 首要检查 |
| --- | --- | --- |
| 接触、插入、表面跟随 | policy 给目标，impedance/admittance 处理力—位移关系 | force sensing、stiffness/damping、delay |
| 动力学和约束较可信 | policy/world model 给 reference/model，MPC 做 constrained replan | model error、state estimate、solver deadline |
| 高维视觉语言与多任务 | learned policy/VLA 负责条件理解，controller 负责执行 | data coverage、OOD、action contract |
| 长时序且模型不准 | subgoal/chunk + 短 horizon replan + recovery/fallback | observation age、failure detector、fallback |

## 深度学习与 Transformer

### MSE、Huber 与交叉熵

连续动作回归常用带 mask 的均方误差：

\[
\mathcal L_{\text{MSE}}
=\frac{\sum_{t,d}m_{t,d}(\hat a_{t,d}-a_{t,d})^2}
{\sum_{t,d}m_{t,d}+\epsilon}.
\]

(m_{t,d}) 表示第 (t) 步第 (d) 个动作维度是否有效。它与 action padding、缺失标签或只训练部分 head 直接对应；不能只写“算 MSE”，还要说明 mask 和 reduction。Huber loss 在小误差区近似二次、大误差区近似一次，通常更抗 outlier。离散 token 或工具调用则常用 cross-entropy，监督对象是目标 token 的类别，而不是连续坐标本身。

### Scaled Dot-Product Attention

Transformer 的核心注意力为：

\[
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.
\]

(Q,K,V) 分别是 query、key、value，(d_k) 是 key 的通道维度，(M) 是 causal/padding 等 mask。除以 (sqrt{d_k}) 可以抑制点积随维度增长造成的 softmax 饱和；mask 负责禁止无效位置或未来 token。实现映射是 `scaled_dot_product_attention` 或等价的矩阵运算；在 VLA 中，图像、语言、proprio 和 action token 的拼接顺序及 mask 决定信息能否跨模态流动。

### LayerNorm 与 RMSNorm

LayerNorm 对一个 token 的特征维度做标准化：

\[
\operatorname{LN}(x)=\gamma\odot\frac{x-\mu(x)}{\sqrt{\sigma^2(x)+\epsilon}}+\beta.
\]

它减去均值并除以标准差；\(\gamma,\beta\) 是可学习的缩放与偏置。RMSNorm 去掉均值中心化，只使用均方根：

\[
\operatorname{RMSNorm}(x)=g\odot\frac{x}{\sqrt{\frac1d\sum_{i=1}^d x_i^2+\epsilon}}.
\]

两式的变量和实现都对应最后一维的 hidden state。面试不要绝对化地说 RMSNorm 一定更好：它减少了计算和参数，但是否更稳定要看 backbone、精度和训练设置。Qwen3-VL 的具体 norm 配置属于上游模型事实，应以官方模型卡/源码为准；本卷只准备原理。

### Pre-Norm、残差与 LoRA

Transformer block 中，pre-norm 常把归一化放在子层之前，post-norm 放在残差相加之后。回答时重点讲梯度路径和深层训练稳定性，不要只背位置。

LoRA 将可训练更新限制为低秩矩阵：

\[
W'=W+\frac{\alpha}{r}BA,
\]

其中 (W) 是冻结的原权重，(A\in\mathbb R^{r\times d})、(B\in\mathbb R^{d'\times r})，(r\ll\min(d,d'))。直觉是用低秩子空间近似任务更新；它节省显存和优化参数，但低秩假设可能限制任务适应能力。OpenPiVLA 页面中的 Qwen3-VL + LoRA 属于你的本地训练路径，具体注入层和 rank 仍需以项目代码/配置核对。

## MDP、RL 与策略评估

### MDP 与 Bellman 方程

Markov Decision Process 可表示为 \((\mathcal S,\mathcal A,P,R,\gamma)\)。给定策略 \(\pi\)，状态价值为：

\[
V^\pi(s)=\mathbb E_{a\sim\pi,\,s'\sim P}
\left[r(s,a)+\gamma V^\pi(s')\right].
\]

\(P(s'\mid s,a)\) 是转移分布，\(r\) 是即时奖励，\(\gamma\) 是折扣因子。这里公式把 \(r(s,a)\) 视为条件期望 reward；若 reward 还依赖 \(s'\)，应把它放进对转移的期望。Bellman 方程表达“当前价值等于即时收益加折扣后的未来价值”；它不等于某个模型的训练 loss，必须先说明 value target 的构造。

动作价值和优势函数为：

\[
Q^\pi(s,a)=\mathbb E[r_t+\gamma V^\pi(s_{t+1})\mid s_t=s,a_t=a],\qquad
A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s).
\]

优势表示某个动作相对于当前状态平均水平好多少。PPO/GRPO 等算法会用到 advantage 或相对优势，但 WAM 中的 value head、离线 MSE 和在线 reward 不是同一对象。

### TD 误差与 on/off-policy

一步 TD 误差可写成：

\[
\delta_t=r_t+\gamma(1-d_t^{term})V_\phi(s_{t+1})-V_\phi(s_t),
\]

其中 \(d_t^{term}\in\{0,1\}\) 只表示真实环境终止。真实终止通常停止 bootstrap；time-limit `truncated` 通常仍应从 \(V_\phi(s_{t+1})\) bootstrap，不能无条件把两者压成一个 `done`。on-policy 方法使用当前或近当前策略采样的数据，分布更新更贴近当前 policy 但样本复用受限；off-policy 方法可以复用 replay/history，但要处理行为策略与目标策略的分布差异。off-policy 不等于 offline RL，前者仍可持续与环境交互。

### 为什么离线 proxy 不等于 online success

离线 action MSE 只衡量数据集状态上的动作接近程度：

\[
\mathbb E_{(o,a)\sim D}\left[\|\pi_\theta(o)-a\|^2\right].
\]

online success 还受到动作误差累积、接触动力学、视觉分布偏移、控制延迟、重规划和 success predicate 的影响。因此 WAM 面试回答必须把 policy MSE 说成离线代理指标，而不是“策略成功率提升”；UWM 的 0.744 目前只保留为 user-confirmed remote final，必须带 strict fixed-init 等协议与 raw-bundle 缺口，不能写成本地 artifact-verified benchmark。

## Pipeline 与伪代码

### 训练 step：带 mask 的连续 action 监督

```python
def masked_action_step(batch, policy, optimizer, normalizer):
    # Read images, language, proprioception, action labels, and valid masks.
    obs = batch["observation"]
    action = batch["action"]
    mask = batch["action_mask"]

    # Normalize action with the same statistics used by the dataset contract.
    target = normalizer.normalize(action)

    # Encode multimodal inputs and predict the action representation.
    pred = policy(obs)

    # Only valid time/dimension entries contribute to the regression objective.
    loss = ((pred - target) ** 2 * mask).sum() / (mask.sum() + 1e-6)

    # Update the trainable parameters and clear gradients for the next step.
    loss.backward()
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    return loss
```

这是知识层伪代码，不声称与你本地 OpenPiVLA trainer 的函数名一致；真实字段、action window 和 collator 需要在 VOL 07 的项目证据中逐项核对。

### 闭环执行：重新观测、反归一化与重规划

```python
def closed_loop_rollout(env, policy, normalizer, task, replan_steps):
    # Reset the environment with the benchmark's declared initialization protocol.
    obs, info = env.reset(task)
    terminated, truncated, success = False, False, False

    while not (terminated or truncated or success):
        # Build the policy input from images, language, and proprioception.
        model_obs = build_observation(obs, task)

        # Predict a normalized action chunk, not yet a controller-space command.
        normalized_chunk = policy(model_obs)

        # Convert back to controller units and enforce the declared action limits.
        action_chunk = normalizer.denormalize(normalized_chunk)
        action_chunk = clip_to_controller_range(action_chunk)

        # Execute only a short prefix, then re-observe to reduce open-loop drift.
        for action in action_chunk[:replan_steps]:
            obs, reward, terminated, truncated, info = env.step(action)
            success = bool(info.get("success", False))
            if terminated or truncated or success:
                break

    # Keep task success separate from termination/truncation and preserve traces.
    return success, info.get("trace", [])
```

闭环的关键不是“模型输出了一个 chunk”，而是 chunk 执行多少步、何时重新观测、如何反归一化、如何判定终止和如何记录失败。它直接连接 OpenPiVLA 的 action window/controller 讨论和 UWM 的 strict eval 讨论。

## 实现映射与项目挂钩

| 基础概念 | 本地项目证据 | 当前能安全说的内容 | 尚待核对 |
| --- | --- | --- | --- |
| action window / normalization / controller | `interview_materials/03_openpivla_action_modeling.html` | 你理解并复原了动作表示、归一化、chunk 和 controller 的闭环关系 | 具体源码函数、轴顺序和归一化文件路径 |
| offline action MSE vs online rollout | `interview_materials/04_cosmos_wam_multitask_training.html` | WAM 页把 policy MSE 作为离线代理，并主动区分 online success | 每个 MSE 数字的完整数据划分和脚本路径 |
| fixed-init / warmup / normalizer | `interview_materials/05_uwm_libero_eval_protocol.html` | UWM 的 strict 协议是可比性前提 | 所有 checkpoint 与 normalizer checksum |
| Transformer / VLM backbone | `interview_materials/02_opd_vlm_grounding.html`、简历 HTML | 可以讲多模态输入、grounding 输出协议和数据分布 | Qwen3-VL 具体 layer/config 需官方源码或本地 config |
| schema / reward / eval | `interview_materials/01_robot_harness_tool_training.html` | 可解释三者在工具调用训练中的不同角色 | runtime 代码、训练字段覆盖统计和完整 reward checker |

## 公源/本地设计边界

### 公有设计 / 上游公开流程

- Transformer attention、LayerNorm、RMSNorm、MDP、Bellman 和经典机器人几何属于公开基础知识。
- OpenVLA、openpi、Diffusion Policy、ACT、LIBERO 等仓库和论文的具体接口与 benchmark 以其官方版本为准。

### 本地证据

- 五个现有项目 HTML、简历 HTML 和 `output/resume_restructure_plan.md` 是当前工作区可直接读取的证据。
- 它们支持你如何叙述项目、哪些指标出现过以及哪些风险已经被主动承认。

### 本地推断

- 从项目页可以推断你需要把 action normalization、评估协议和数据分布作为统一的解释链；这不是某个单一源码函数的直接证明。

### 尚未核实

<div class="warning">⚠️ 当前工作区没有 OpenPiVLA、WAM、UWM 的完整源码、normalizer 文件和训练日志，因此本卷不把伪代码中的字段名、函数名或张量 shape 写成本地实现事实。</div>

## 方法对比与选择建议

| 问题 | 选择/解释 | 面试防线 |
| --- | --- | --- |
| 连续动作监督 | MSE 简单稳定；Huber 更抗 outlier；是否有效取决于 action normalization 和闭环执行 | 不把 MSE 下降说成成功率提升 |
| 离散 token 监督 | Cross-entropy 适合 token 序列，复用语言模型解码；动作精度和串行延迟需要额外讨论 | 不说 token 化“没有精度损失” |
| on-policy vs off-policy | 前者数据贴近当前策略，后者复用数据但有 distribution shift | 先问数据来自哪个 policy |
| pre-norm vs post-norm | 关注深层梯度路径与训练稳定性，不背绝对结论 | 具体 backbone 配置要查源码 |
| 高层 policy vs 低层 controller | policy 负责任务条件下的动作意图，controller 负责时序、限幅、动力学和安全 | 明确接口和单位 |
| offline proxy vs online eval | proxy 便宜、可定位，online 更接近任务目标但受 protocol 影响 | 同时报告数据划分和 rollout 协议 |

## 风险与后续建议

1. **基础概念不能只背公式**：每个公式都要能说明变量、shape、代码位置和失败模式。
2. **坐标协议是高危点**：仍需补一张 action axis/order/coordinate checklist，连接 OpenPiVLA 和 UWM；本轮只修复公式转义，不把轴序写成本地事实。
3. **缺源码时要主动降级**：当前本卷只写通用机制，不把伪代码说成已验证的本地实现。
4. **题卡需要口述校准**：本卷清单中的 P0 题先进入题库，P1/P2 根据第一次 drill 的表现调整。
5. **下一卷衔接**：VOL 02 进入 BC、DAgger、PPO、GRPO、SFT/DPO 和数据分布；VOL 03 再展开 VLA action head、Diffusion/Flow Matching。

## 参考文献（References）

1. Vaswani et al., [“Attention Is All You Need,”](https://arxiv.org/abs/1706.03762) 2017.
2. Ba, Kiros, Hinton, [“Layer Normalization,”](https://arxiv.org/abs/1607.06450) 2016.
3. Zhang and Sennrich, [“Root Mean Square Layer Normalization,”](https://arxiv.org/abs/1910.07467) 2019.
4. Sutton and Barto, [*Reinforcement Learning: An Introduction*, 2nd ed.](http://incompleteideas.net/book/the-book-2nd.html)
5. Lynch and Park, [*Modern Robotics*, Chapter 4: Forward Kinematics.](https://modernrobotics.northwestern.edu/chapters/chapter4/)
6. PyTorch, [`torch.nn.LayerNorm` documentation.](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html)
7. PyTorch, [`scaled_dot_product_attention` documentation.](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html)
8. [OpenVLA official repository.](https://github.com/openvla/openvla)
9. Physical Intelligence, [`openpi` official repository.](https://github.com/Physical-Intelligence/openpi)
10. [LIBERO official repository.](https://github.com/Lifelong-Robot-Learning/LIBERO)
11. 本地项目证据：`interview_materials/01_robot_harness_tool_training.html`、`02_opd_vlm_grounding.html`、`03_openpivla_action_modeling.html`、`04_cosmos_wam_multitask_training.html`、`05_uwm_libero_eval_protocol.html`。
12. PyTorch, [`torch.nn.MSELoss` documentation.](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)
13. PyTorch, [`torch.nn.HuberLoss` documentation.](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html)
14. PyTorch, [`torch.nn.CrossEntropyLoss` documentation.](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html)
15. Gymnasium, [Handling Time Limits.](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)
16. Lynch and Park, [*Modern Robotics*, Chapter 5: Velocity Kinematics and Statics.](https://modernrobotics.northwestern.edu/chapters/chapter5/)
17. Åström and Murray, [*Feedback Systems*.](https://fbsbook.org/)
18. [VOL 01 Batch 2 MDP / TD / Control Independent Fact Review.](../sources/vol_01_batch2_mdp_td_control_independent_fact_review.html)
19. Hogan, [Impedance Control: An Approach to Manipulation, Part I.](https://doi.org/10.1115/1.3140702)
20. Rawlings, Mayne, Diehl, [*Model Predictive Control: Theory, Computation, and Design*.](https://sites.engineering.ucsb.edu/~jbraw/mpc/MPC-book-2nd-edition-5th-printing.pdf)
21. Chi et al., [Diffusion Policy.](https://arxiv.org/abs/2303.04137)
22. Kim et al., [OpenVLA.](https://arxiv.org/abs/2406.09246)
23. [VOL 01 Batch 3 Advanced Control Independent Fact Review.](../sources/vol_01_batch3_advanced_control_independent_fact_review.html)
