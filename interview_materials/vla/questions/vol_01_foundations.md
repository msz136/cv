# VOL 01 Foundations：核心面试题卡（Batch 1）

> 状态：`drafted`  
> 题数：39  
> 难度：L1 12 题 / L2 23 题 / L3 4 题  
> 练习状态：全部 `unseen`  
> 说明：P0 表示本仓库必须掌握，不代表公开面经频次。

## A. 表示、优化与损失

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-001</b> · 为什么机器人策略和 VLM 都需要向量化表示？embedding 维度代表什么？</summary>

**30 秒回答**：模型只能处理数值张量，所以图像 patch、文本 token、proprioception 和 action 都要先向量化。embedding 维度是表示空间的通道数，不等于类别数；维度增大通常提高容量，但也增加显存、计算和过拟合风险。多模态进入共享 backbone 前还必须对齐 shape、位置与 mask。

**机制展开（约 2 分钟）**：图像由视觉编码器变成 patch/token 序列，文本由 tokenizer 与语言 embedding 变成 token，proprioception/action window 则通过连续特征投影或 action head 的输入映射进入同一计算图。所谓“对齐”不只是把最后一维设成相同大小，还包括时间/空间位置编码、模态类型标识、padding/valid mask，以及 batch、sequence、feature 三个轴的约定。维度选择要和 attention 的计算量、数据量、冻结/微调策略一起看，不能把更大的 embedding 直接说成更强的语义理解。

**项目挂钩**：OpenPiVLA 中图像、指令和 action window 最终都要进入统一训练 contract。

**追问**：多模态 embedding 如何对齐？拼接和 cross-attention 有什么区别？

**易错**：embedding 的单个维度通常没有稳定、可解释的一一语义。

**来源**：[1][27][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-002</b> · 点积、余弦相似度和欧氏距离分别适合什么场景？</summary>

**30 秒回答**：点积同时受方向和模长影响，常用于 attention logits；余弦相似度先归一化、主要比较方向，适合语义 embedding；欧氏距离衡量绝对空间距离，适合坐标或已统一尺度的特征。选择前要确认归一化、模长意义和量纲是否一致。

**机制展开（约 2 分钟）**：若 \(x,y\) 未归一化，点积 \(x^\top y=\|x\|\|y\|\cos\theta\) 会把方向和模长混在一起；这正是 attention 中 logits 既受相似方向又受 feature scale 影响的原因。余弦相似度显式除以两个范数，适合比较语义方向，但会丢掉幅值信息；欧氏距离对坐标偏移敏感，必须先确认 frame、单位和 normalization。机器人 state/action 的不同维度若量纲不统一，直接用欧氏距离会让大尺度轴支配结果；OPD 的 box/point 几何误差应使用几何合同，而不是拿语义余弦替代。

**项目挂钩**：OPD 的 box/point 几何误差不能直接用语义余弦相似度代替。

**追问**：为什么 CLIP 常用归一化后的点积？

**易错**：不能在未统一量纲的机器人 state/action 上直接比较欧氏距离。

**来源**：[1][27][44]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-003</b> · gradient、Jacobian 和 Hessian 分别是什么？</summary>

**30 秒回答**：gradient 是标量函数的一阶导数，Jacobian 是向量输出对向量输入的一阶偏导矩阵，Hessian 是标量函数的二阶导数矩阵。训练里 gradient 用于更新参数；机器人里 Jacobian 把关节速度映射为末端速度；Hessian 描述局部曲率。三者输入输出类型不同，不能混为一谈。

**机制展开（约 2 分钟）**：对标量 \(f(x)\)，gradient 可写成 \(\nabla_x f\)；对向量 \(y(x)\)，Jacobian 为 \(J_{ij}=\partial y_i/\partial x_j\)；Hessian 为 \(H_{ij}=\partial^2 f/(\partial x_i\partial x_j)\)。机械臂在当前关节位姿 \(q\) 附近满足 \(\dot{x}=J(q)\dot{q}\)，因此 Jacobian 的小奇异值会让伪逆放大观测噪声和控制误差，常用阻尼最小二乘或限幅来稳定 IK。VLA 训练中的 \(\nabla_\theta \mathcal{L}\) 是损失对模型参数的梯度，不等于机器人运动 Jacobian；action denormalization、controller 和环境 step 还可能包含不可微或安全限幅环节。面试时要先说明变量的输入输出，再谈数值稳定性。

**项目挂钩**：动作空间和 controller contract 的解释需要区分参数梯度与机器人运动 Jacobian。

**追问**：为什么 Jacobian 条件数大时 IK 不稳定？

**易错**：Jacobian 不是“更大的 gradient”，要先看输入输出是否都是向量。

**来源**：[27][37][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-004</b> · LayerNorm、BatchNorm、RMSNorm 如何取舍？</summary>

**30 秒回答**：BatchNorm 按通道使用 batch/空间统计，依赖 batch 稳定性且训练、推理统计不同；LayerNorm 对每个样本或 token 的特征维归一化，适合 Transformer；RMSNorm 只按均方根缩放、不减均值，形式更简。选型首先服从 pretrained backbone 和兼容性，不能脱离统计轴说谁绝对更好。

**机制展开（约 2 分钟）**：BatchNorm 在训练时使用当前 mini-batch 的均值/方差，并维护 running statistics 供推理使用，所以 batch 很小、跨设备统计不同或数据分布漂移时容易不稳。LayerNorm 对单个 token 的 hidden dimension 计算均值和方差，不依赖其他样本，适合变长序列；RMSNorm 可写为 \(y_i=\gamma_i x_i/\sqrt{\frac{1}{d}\sum_j x_j^2+\epsilon}\)，保留均值方向，只控制均方根尺度。实际迁移 Qwen3-VL 等 pretrained backbone 时，norm 类型、Pre-Norm/Post-Norm 位置、\(\epsilon\)、权重名称和 dtype 都属于 checkpoint contract，随意替换会破坏加载与训练行为。它们处理的是网络 activation；action normalization 则把物理动作按数据统计映射到模型尺度，两者目的和证据完全不同。

**项目挂钩**：Qwen3-VL 的具体 norm 类型应查官方模型配置，不凭印象回答。

**追问**：为什么小 batch 训练时 BatchNorm 容易不稳定？

**易错**：归一化层与 action normalization 不是同一件事。

**来源**：[2][3][6][28]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-006</b> · MSE、MAE、Huber loss 什么时候使用？</summary>

**30 秒回答**：MSE 对误差平方求平均，梯度平滑但会放大 outlier；MAE 使用绝对误差，对 outlier 更稳但零点不可微；Huber 在小误差区用二次项、大误差区用一次项，是两者折中。连续 action 选 loss 前还要固定维度尺度、normalization、valid mask 和 reduction，否则数值不能比较。

**机制展开（约 2 分钟）**：令误差 \(e=\hat y-y\)，MSE 为 \(\mathbb{E}[e^2]\)，MAE 为 \(\mathbb{E}[|e|]\)。Huber loss 写成：

\[
\ell_\delta(e)=
\begin{cases}
\frac{1}{2}e^2, & |e|\le \delta,\\
\delta\left(|e|-\frac{1}{2}\delta\right), & |e|>\delta.
\end{cases}
\]

变量解释：\(\delta\) 决定二次区与一次区的切换点；小误差保持平滑梯度，大误差的梯度被限制，降低异常值主导。对 action tensor，正确 reduction 应按 valid mask 的有效元素数归一，而不是把 padding 或不存在的 action 维度算进分母；不同轴还应先统一物理单位或使用训练 normalizer。gripper 若是离散开合语义，可能更适合分类/BCE 或单独加权，而不是和位姿轴无条件共享 MSE。即使 teacher-forced policy MSE 下降，也只说明离线标签拟合更好；闭环还受 observation shift、采样、反归一化、controller 和 success predicate 影响，不能直接推出 WAM task success。

**项目挂钩**：WAM 的 policy MSE 是离线代理，不自动推出闭环成功率。

**追问**：gripper 二值维度是否应该和连续位姿用同一种 loss？

**易错**：loss 越小不一定任务成功率越高。

**来源**：[11][12][29][42]　**练习状态**：unseen

</details>

## B. Transformer 与多模态输入

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-010</b> · softmax 如何把 logits 变成概率？怎样保证数值稳定？</summary>

**30 秒回答**：softmax 把 logits 变成和为 1 的概率分布；实现时先减去最大 logit，因为整体平移不改变结果，却能避免指数溢出。训练交叉熵通常直接用 `log_softmax` 或 fused cross-entropy，避免先算概率再取 log。temperature 和 mask 必须在 softmax 前处理。

**机制展开（约 2 分钟）**：原式是 \(p_i=\exp(z_i)/\sum_j\exp(z_j)\)。令 \(m=\max_j z_j\)，稳定实现为 \(p_i=\exp(z_i-m)/\sum_j\exp(z_j-m)\)，它利用了 log-sum-exp 的平移不变性；极端 logits 仍应关注 dtype、溢出和 underflow。temperature \(T\) 通常使用 \(z_i/T\)：\(T\) 越大分布越平，越小越尖锐；它改变采样/分类分布，不等于自动完成 calibration。无效 token 或 padding 应在 softmax 前加 mask（通常置为 \(-\infty\) 或使用框架 masked kernel），而不是先归一化后再把概率清零。交叉熵可直接计算 `log_softmax(z) - target`，数值更稳定。VLA 中 action token、tool token 和文本 token 共用分类 logits 时，必须说明 vocabulary mask、padding mask 和 temperature 的作用域；softmax 输出也不等于已校准的置信度。

**项目挂钩**：action token、tool token 和 VLM 文本输出都依赖稳定的分类 logits。

**追问**：temperature 如何改变分布尖锐度？

**易错**：softmax 输出是模型分布，不是置信度已校准的证明。

**来源**：[1][13][30]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-011</b> · cross-entropy 与 MSE 的监督对象有什么区别？</summary>

**30 秒回答**：cross-entropy 监督离散类别或 token 的概率分布，MSE 监督连续数值误差。文本、action token 和工具选择通常用 cross-entropy；连续 action、state 或 value regression 通常用 MSE。把动作离散化后，必须额外评估 decode 回连续动作后的误差、控制接口和闭环结果。

**机制展开（约 2 分钟）**：对 one-hot 目标 \(y\) 和 logits \(z\)，交叉熵可写为 \(\mathcal{L}_{CE}=-\sum_k y_k\log p_k\)，其中 \(p=\operatorname{softmax}(z)\)；它关心正确类别相对其他类别的概率质量。连续回归常写为 \(\mathcal{L}_{MSE}=\frac{1}{N}\sum_i m_i(\hat a_i-a_i)^2\)，其中 \(m_i\) 是 valid/action mask，分母必须与有效元素一致。动作离散化会引入 bin width、边界和 vocabulary/sequence length 的选择：bin 更多可能降低量化误差，却增加 token 数、稀疏监督和 decode 复杂度；CE 变好不保证反归一化后的连续 action 更准。反过来，MSE 的数值也受 action normalization、维度权重和 reduction 影响。OpenPiVLA 的 assistant-side action token 与 WAM 的连续 action MSE 属于不同监督协议，不能直接比较 loss 数值；必须在同一 decode、单位、mask、控制器和 success predicate 下比较下游结果。

**项目挂钩**：OpenPiVLA 的 assistant-side action token 与 WAM 连续 action MSE 属于不同监督协议。

**追问**：离散 bin 越多是否一定更精确？

**易错**：训练 loss 不同，数值大小不能横向直接比较。

**来源**：[8][9][11][13][41][42]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-012</b> · attention 为什么除以 \(\sqrt{d_k}\)？</summary>

**30 秒回答**：若 query/key 各维独立且方差相近，点积的方差会随 \(d_k\) 增长。logits 过大时 softmax 饱和、梯度变小；除以 \(\sqrt{d_k}\) 把尺度拉回稳定范围。它控制的是 logits 的数值尺度，不是为了让概率和为 1。

**机制展开（约 2 分钟）**：scaled dot-product attention 可写为：

\[
\operatorname{Attn}(Q,K,V)=
\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V .
\]

若 \(q_i,k_i\) 独立、零均值且方差为 1，则 \(q^\top k=\sum_{i=1}^{d_k}q_i k_i\) 的方差约为 \(d_k\)，标准差约为 \(\sqrt{d_k}\)。不缩放时 logits 随 head dimension 变大，softmax 容易进入近似 one-hot 区域，反向梯度变小；除法把典型标准差恢复到常数级。\(M\) 是 attention mask，应在 softmax 前加入（无效位置通常为 \(-\infty\)），不能先得到概率再清零后重新假设归一化。temperature 也能改变 logits 尖锐度，但它是显式分布温度，不能替代对 \(d_k\) 的结构性缩放。VLA 中 \(Q/K/V\) 可能混合图像、文本、proprio 或 action tokens，仍要先核对 batch、head、sequence、head-dimension 的 shape；缩放不能修复错误的 token mask 或模态位置编码。

**项目挂钩**：VLM backbone 处理图像、文本和动作条件时都依赖 attention 的稳定尺度。

**追问**：temperature 与 \(1/\sqrt{d_k}\) 有什么联系？

**易错**：softmax 本身就保证和为 1，缩放解决的是饱和问题。

**来源**：[1][7]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-013</b> · self-attention、cross-attention、causal mask 和 padding mask 如何区分？</summary>

**30 秒回答**：self-attention 的 Q/K/V 来自同一序列，cross-attention 的 query 与 key/value 来自不同序列或模态。causal mask 禁止看未来位置，padding mask 屏蔽补齐 token；loss mask 只决定哪些目标计入损失，不一定改变 attention。多模态 VLA 中必须分清 attention mask、condition mask 和 loss mask。

**机制展开（约 2 分钟）**：若 \(Q\in\mathbb{R}^{B\times h\times L_q\times d}\)、\(K,V\in\mathbb{R}^{B\times h\times L_k\times d}\)，attention score 的形状是 \(B\times h\times L_q\times L_k\)，通常计算 \(\operatorname{softmax}(QK^\top/\sqrt d+M)V\)。self-attention 取 \(L_q=L_k\) 且来自同一 token 序列；cross-attention 允许 query 来自语言/动作流，而 key/value 来自图像或另一模态。causal mask 是时间方向的上三角约束；padding mask 根据有效长度屏蔽 key/value 位置；二者可叠加。loss mask 则在 logits/target reduction 阶段过滤监督项，即使某个 token 不计 loss，它仍可能被模型作为上下文读取。WAM 的 world/value/action target mask、sample routing 与 Transformer attention mask 是不同控制面，必须分别记录 broadcast shape、取值约定和作用阶段；只做 loss mask 可能仍让无效条件污染上下文，反过来只做 attention mask 也不会自动改变 loss 分母。

**项目挂钩**：WAM 的 world/value mask 与 Transformer attention mask 不应混成同一概念。

**追问**：只做 loss mask、不做 attention mask 会发生什么？

**易错**：mask 的值约定和 broadcast shape 要查具体实现。

**来源**：[1][7][42]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-016</b> · 图像、文本、proprio 和 action token 如何进入同一个模型？</summary>

**30 秒回答**：图像、文本、proprio 和 action 先经各自 encoder/tokenizer，再投影到兼容的 hidden size，通过拼接、自注意力、cross-attention 或独立 expert 交互。必须同时固定模态标识、位置/时间、有效 mask 和 action loss 区域；hidden size 相同不等于语义已经对齐。

**机制展开（约 2 分钟）**：可以把每种输入写成 \(z_m=P_m(E_m(x_m))\)，其中 \(E_m\) 是模态编码器、\(P_m\) 把输出投影到共享 hidden size；之后再由 token order、modality/type embedding、position/time embedding 和 attention mask 定义信息流。图像通常是 patch/token 序列，文本要遵守 tokenizer 与 chat template，proprio 可压成单 token 或按时间/关节拆成多个 token，action 既可能是连续 head 输入，也可能是离散 token 目标。多模态拼接降低接口复杂度但依赖长序列和 mask；cross-attention 可隔离 query/key/value 角色但增加模块和 shape 合同；独立 expert 便于专门处理 action，却需要明确交互层和梯度路由。OpenPiVLA 的 image/instruction/action window 不能只说“拼起来”，还要核对 chat template、时间对齐、padding、action formatter 与哪些 assistant positions 进入 causal-CE。

**项目挂钩**：OpenPiVLA 需要对齐 image/instruction/action window 与 Qwen chat template。

**追问**：proprio 作为单 token 和多 token 的 trade-off 是什么？

**易错**：hidden size 对齐不等于语义已经对齐。

**来源**：[8][9][41]　**练习状态**：unseen

</details>

## C. MDP、RL 与策略评估

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-021</b> · MDP 的 \(S,A,P,R,\gamma\) 分别是什么？</summary>

**30 秒回答**：MDP 用 \(S,A,P,R,\gamma\) 描述状态空间、动作空间、转移分布、奖励和折扣因子。机器人里 observation 可能不是完整 state，action 必须说明位置/速度/力矩、单位与控制频率；reward、done 和 success predicate 也要分别定义。语言指令通常是条件，不自动等于 state。

**机制展开（约 2 分钟）**：策略通常写成 \(\pi(a_t\mid s_t)\)，回报为 \(G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k+1}\)。\(P(s'|s,a)\) 描述环境动力学，\(R\) 可以是 dense shaping、cost 或 sparse task reward；\(\gamma\) 决定远期回报的权重。实际机器人往往只能得到 \(o_t\)，若 \(o_t\) 不满足 Markov 性，就需要历史窗口、recurrent state、belief 或显式 memory；带语言指令时更安全地写成 \(\pi(a_t\mid o_{\le t},\,l)\)，而不是把 \(l\) 直接当作物理 state。动作还要绑定 frame、单位、维度、chunk/horizon、controller 与 frequency。episode 的真正 terminal 应停止 bootstrap，time-limit truncated 通常仍可 bootstrap；具体实现要看环境 API。UWM/LIBERO 的 binary success、WAM 的 value/world target 和训练 proxy reward 不是同一个量，比较时必须保留 protocol tuple。

**项目挂钩**：UWM 的 rollout success 与 WAM 的 value target 不能只用“奖励”统称。

**追问**：部分可观测时为什么需要历史或 memory？

**易错**：语言指令通常是条件，不自动等于 MDP state。

**来源**：[4][42][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-022</b> · value、Q 和 advantage 有什么区别？</summary>

**30 秒回答**：\(V^\pi(s)\) 是按策略从状态 \(s\) 出发的期望回报；\(Q^\pi(s,a)\) 固定第一步动作后的期望回报；\(A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s)\) 表示该动作比策略平均水平好多少。advantage 常用于策略更新，value 常作 baseline，target 取法取决于算法和 termination 语义。

**机制展开（约 2 分钟）**：三者关系为 \(V^\pi(s)=\mathbb{E}_{a\sim\pi}[Q^\pi(s,a)]\) 与 \(A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s)\)。一步 TD 误差常写成 \(\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t)\)，其中 \(d_t\) 必须区分真正 terminal 与 time-limit truncated；GAE 再对多步 \(\delta\) 做带 \(\lambda\) 的加权累积。减去只依赖 state 的 baseline 不改变 policy-gradient 的期望，却能降低方差。Q/value 还可以通过 Monte Carlo、TD、n-step 或 lambda-return 构造，不能把一个实现的 target 当成所有 RL/VLA 的默认。WAM 的 value/world auxiliary head 若存在，只能按项目合同解释为辅助预测或 ranking 信号；它不自动等于控制动作，也不证明 online RL policy improvement。面试时要同时说清输入、target、mask、bootstrap 和评估协议。

**项目挂钩**：WAM 的 value head 是辅助目标，不能说它直接输出控制动作。

**追问**：为什么减 baseline 不改变 policy gradient 的期望？

**易错**：value 不是当前即时 reward。

**来源**：[4][42]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-023</b> · Bellman expectation equation 与 optimality equation 有什么不同？</summary>

**30 秒回答**：Bellman expectation equation 固定策略 \(\pi\)，对下一动作按 \(\pi\) 求期望，回答“这条策略有多好”；optimality equation 对动作取最大值，定义 \(V^*,Q^*\) 并隐含 greedy policy improvement，回答“最优能有多好”。连续高维动作不能枚举 max，通常由 actor 或候选动作搜索近似；benchmark success 也不能证明达到 Bellman optimum。

**机制展开（约 2 分钟）**：对 state value，可写成 \((\mathcal T^\pi V)(s)=\mathbb E_{a\sim\pi,s'\sim P}[r+\gamma V(s')]\) 与 \((\mathcal T^*V)(s)=\max_a\mathbb E_{s'\sim P}[r+\gamma V(s')]\)；对 action value，则是 \((\mathcal T^\pi Q)(s,a)=\mathbb E[r+\gamma\mathbb E_{a'\sim\pi}Q(s',a')]\) 和 \((\mathcal T^*Q)(s,a)=\mathbb E[r+\gamma\max_{a'}Q(s',a')]\)。\(\mathcal T^\pi\) 只评估固定策略，\(\mathcal T^*\) 把评估与改进耦合起来。连续动作中的 actor-critic 用 critic 估计 \(Q\)，再让 actor 近似 \(\arg\max_a Q(s,a)\) 或最大化其期望；这不是解析枚举，也受函数逼近、数据覆盖和 critic 误差限制。许多 BC、diffusion 或 flow-matching VLA 只是条件动作生成器，除非训练目标和运行证据明确包含 Bellman backup，不能称为在求最优 Q。WAM value proxy 与 LIBERO success 统计同样不是 Bellman optimality 的解或证明。

**项目挂钩**：WAM value 估计与 LIBERO success 统计都不是在求解析的 Bellman 最优解。

**追问**：actor-critic 如何绕过连续动作的显式 max？

**易错**：Bellman 方程不是某个神经网络结构。

**来源**：[4][42][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-024</b> · on-policy 与 off-policy 的核心差异是什么？</summary>

**30 秒回答**：on-policy 用当前或近当前目标策略 \(\pi\) 产生的数据更新，估计分布直接，但策略一变数据就迅速变旧，样本复用有限；off-policy 允许行为策略 \(\mu\neq\pi\)，可复用 replay、历史或其他策略数据，样本效率更高，却要处理分布修正、OOD 动作和估计偏差。off-policy 仍可持续交互，不等于只有固定数据的 offline RL。

**机制展开（约 2 分钟）**：on-policy estimator 的轨迹来自 \(\tau\sim\pi_\theta\)，PPO 只允许有限轮次、有限策略偏移地复用 rollout；off-policy 数据则来自 \(d^\mu(s)\mu(a\mid s)\)。若行为概率可得且 support 覆盖，可用 importance ratio \(\rho_t=\pi(a_t\mid s_t)/\mu(a_t\mid s_t)\) 重加权，但长轨迹的 ratio 乘积方差很高，clip、truncate 或 per-decision correction 又会引入 bias–variance trade-off，而且 \(\mu(a\mid s)=0\) 的动作无法靠重加权补出来。Q-learning 用 \(r+\gamma\max_{a'}Q_{target}(s',a')\) 构造与行为动作不同的 target，是典型 off-policy 思路；深度实现还需 replay、target network、double-Q 或 conservative regularization 控制 bootstrap 与 OOD 误差。offline RL 是 off-policy 学习的更强约束场景：数据集固定，不能主动补覆盖。Robot Harness 当前只是固定 candidate group 上的 reward-shaped weighted token CE；它不是 canonical online GRPO，也不能仅因复用离线样本就称为标准 off-policy RL。

**项目挂钩**：canonical online GRPO 与当前 Harness 的 offline reward-shaped grouped weighting 承担不同训练角色，不能混称为同一实现。

**追问**：importance sampling 为什么能修正分布差异？

**易错**：off-policy 不等于 offline RL；前者仍可持续交互。

**来源**：[4][45]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-025</b> · policy gradient 为什么需要 advantage/baseline？</summary>

**30 秒回答**：REINFORCE 用 return 给动作加权，但同一状态下整条轨迹的随机性会让梯度方差很大。减去只依赖 state 的 baseline 不改变期望梯度，却能减少这种共同噪声；advantage 就是动作相对该状态平均水平的增量。实际通常用 value network、TD/GAE 来估计它，而不是把 advantage 当作已知标签。

**机制展开（约 2 分钟）**：策略梯度可写成 \(\nabla_\theta J(\theta)=\mathbb{E}[\nabla_\theta\log\pi_\theta(a_t\mid s_t)G_t]\)。若换成 \(G_t-b(s_t)\)，因为 baseline 不依赖当前采样动作，有 \(\mathbb{E}_{a\sim\pi}[\nabla_\theta\log\pi_\theta(a\mid s)b(s)]=0\)，所以期望梯度不变，但方差通常下降。令 \(V^\pi(s)\) 近似状态平均回报，则 \(A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s)\) 表示该动作相对基准的贡献；一步 TD 可用 \(\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t)\)，GAE 再对多个 \(\delta\) 做 \(\lambda\) 加权。baseline 过弱，降方差有限；过强或 target/termination/mask 写错，会把偏差带进更新。GRPO 的组内相对信号可以起到 baseline-like 的作用，但不能直接说它等于机器人 value head；Robot Harness 的 reward-shaped weighted token CE 也不能据此改称 canonical online GRPO。

**项目挂钩**：GRPO 使用组内相对信号，但不能把它和机器人 value head 直接等同。

**追问**：为什么 baseline 不能依赖当前采样动作？

**易错**：advantage 不是天然已知，需要估计。

**来源**：[4][45]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-029</b> · 为什么 offline action MSE 降低不一定提高 online success？</summary>

**30 秒回答**：offline action MSE 只比较数据集状态上的动作误差；closed loop 中一个小误差可能改变后续 observation，使策略进入未见状态并累积偏差。online success 还受 action denormalization、控制频率/延迟、接触动力学、replan 和 success predicate 影响，所以 MSE 是诊断 proxy，不是成功率的充分条件。

**机制展开（约 2 分钟）**：连续动作的 masked MSE 可写成 \(\mathcal{L}_{MSE}=\frac{\sum_i m_i(\hat a_i-a_i)^2}{\max(1,\sum_i m_i)}\)，但这个数值依赖 action normalization、维度权重、mask、reduction 和数据状态分布。即便 teacher-forced 或 fixed-window MSE 下降，部署时仍要经过反归一化、chunk 切片、控制器执行和环境 step；误差会改变下一帧视觉/proprio，导致 \(d^\pi(s)\) 偏离离线数据分布。接触任务还可能存在“位置误差很小但接触时序失败”，而低频重规划、延迟或错误的 success predicate 也会让相同动作误差对应不同成功结果。更接近 online 的离线诊断应至少固定 checkpoint、数据 split、state coverage、normalizer、action horizon、seed 和 protocol，并报告 per-task/per-init 的 failure slice；最终仍需 matched closed-loop rollouts。WAM 的离线 MSE 趋势只能支持 proxy 或 root-cause 候选，历史改善比例在没有同 checkpoint、同脚本和原始 artifact 时不能升级为成功率提升。

**项目挂钩**：WAM 的离线 MSE 趋势只能作为 proxy；历史改善比例仍需同数据、同 checkpoint、同脚本 artifact 复核，不能写成成功率提升。

**追问**：如何设计更接近在线表现的离线评估？

**易错**：离线指标没有价值是另一个极端；它适合快速定位和消融。

**来源**：[4][10][39][42]　**练习状态**：unseen

</details>

## D. 机器人几何、控制与闭环

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-030</b> · observation、state、proprioception、action 如何区分？</summary>

**30 秒回答**：observation 是传感器实际读到的量，可能有噪声且不完全；state 是在 Markov 假设下足以决定下一步转移分布的系统状态；proprioception 是关节角、速度、末端位姿、夹爪等本体感知，通常只是 observation/state 的一部分；action 是策略发给控制器的命令。回答时必须补时间戳、单位、坐标系、维度和控制频率。

**机制展开（约 2 分钟）**：环境可写成 \(s_{t+1}\sim P(\cdot\mid s_t,a_t)\)，传感器再由 \(o_t\sim O(\cdot\mid s_t)\) 产生 observation。真实机器人常只得到多视角图像、深度和 proprio，因此单帧 \(o_t\) 未必满足 Markov 性；可用历史窗口、recurrent memory、state estimator 或 belief \(b_t(s)=p(s_t\mid o_{\le t},a_{<t})\) 补偿。proprio 的“末端位姿”还要说明是在 base/world/camera frame，下游是否已做 normalization。action 可能是关节位置/速度/力矩、末端位姿 delta、夹爪指令或 action chunk；策略输出通常还要经过 denormalization、限幅、坐标变换和 low-level controller，才真正影响动力学。OpenPiVLA/UWM 的 image、instruction、proprio、action window 不能笼统叫输入输出：要冻结 shape、frame、unit、timestamp、valid mask、chunk/horizon 与 controller contract，否则 offline loss、server response 和 closed-loop rollout 无法对齐。

**项目挂钩**：OpenPiVLA 的 observation/state normalization 不能只叫“预处理”。

**追问**：只有单帧图像时是否满足 Markov 性质？

**易错**：可观测到的信息不等于完整 state。

**来源**：[4][5][35][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-031</b> · 世界、相机、base、末端和关节坐标为什么必须区分？</summary>

**30 秒回答**：同一个点或动作在不同 frame 下数值不同：视觉观测通常在 camera frame，机器人控制常在 base/world、末端 frame 或 joint space。必须明确变换方向、旋转和平移顺序、单位、轴约定和时间戳；否则数值看似合理，执行方向仍可能整体反掉。相机内参负责像素与相机射线，外参负责 camera 与机器人/world frame 的关系。

**机制展开（约 2 分钟）**：齐次变换可写成 \(T^A_B=\begin{bmatrix}R^A_B&t^A_B\\0&1\end{bmatrix}\)，若点在 frame \(B\) 中表示为 \(\tilde p_B=[p_B,1]^\top\)，则 \(\tilde p_A=T^A_B\tilde p_B\)，组合时必须按实际链路顺序相乘，例如 \(T^W_C=T^W_B T^B_E T^E_C\) 只在每个下标方向定义一致时成立。旋转可用矩阵、四元数或 axis-angle 表示，但要固定左/右乘、主动/被动旋转、角度单位和 quaternion 排列。相机内参 \(K\) 描述焦距、主点和像素尺度；外参 \(T^B_C\) 描述相机相对 base 的位姿，二者不能互换。操作 action 还要区分绝对 pose、delta pose、joint command 与 controller 输入，保证 transform、normalizer 和 gripper convention 一致。OPD 的 box/point 像素坐标、OpenPiVLA 的末端 action、UWM 的 controller action 不是同一空间，必须在接口处显式记录 frame contract 和 round-trip 检查。

**项目挂钩**：OPD 的图像坐标与 OpenPiVLA 的机器人 action 坐标不是同一个空间。

**追问**：相机外参和内参分别负责什么？

**易错**：坐标系命名中的上下标方向不能凭感觉解释。

**来源**：[5][35][44]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-032</b> · 齐次变换矩阵为什么能同时表示旋转和平移？</summary>

**30 秒回答**：把三维点扩成齐次坐标 \([x,y,z,1]^\top\)，就能用 \(T=\begin{bmatrix}R&p\\0&1\end{bmatrix}\) 的一次矩阵乘法同时完成旋转和平移。多个 frame 通过矩阵连乘组合，但顺序不可交换；实现前还要固定 column/row vector、主动/被动旋转和下标方向。

**机制展开（约 2 分钟）**：在 column-vector 约定下，\(\tilde p_A=T^A_B\tilde p_B\)，其中 \(R\in SO(3)\) 满足正交和单位行列式，\(p\) 是平移；这让刚体位姿落在 \(SE(3)\) 的统一接口中。若 \(T=\begin{bmatrix}R&p\\0&1\end{bmatrix}\)，则 \(T^{-1}=\begin{bmatrix}R^\top&-R^\top p\\0&1\end{bmatrix}\)，不能只把平移取负而忽略旋转。组合链例如 \(T^W_C=T^W_B T^B_E T^E_C\) 必须从右到左作用在点上；row-vector 实现或右乘约定会改变写法。工程中还要处理单位（m/mm、rad/deg）、axis order、quaternion 排列、时间同步和数值正交化。VLA action contract 如果把 world/base/end-effector frame 混用，offline parser 可能仍能通过 shape 检查，但 closed-loop 会出现系统性方向或尺度偏差，因此应加入 transform round-trip、identity 和 inverse consistency 测试。

**项目挂钩**：action contract 若混淆 world/base/end-effector frame，会出现系统性偏差。

**追问**：\(T_{ab}^{-1}\) 如何写？

**易错**：旋转矩阵不能随意当作欧拉角向量相加。

**来源**：[5][35][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-033</b> · FK 与 IK 的输入输出和难点是什么？</summary>

**30 秒回答**：FK 输入关节位置/姿态 \(q\)，沿机器人链计算末端 pose，通常是确定映射；IK 反过来给定目标末端 pose，求满足 \(f(q)=T^*\) 的关节配置，可能多解、无解或处于奇异附近。数值 IK 还受初值、关节限位、碰撞和连续性约束影响。VLA 输出 7D 末端 action 仍需 IK/controller 才能变成关节命令，不能直接说成电机 torque。

**机制展开（约 2 分钟）**：FK 可写成 \(T^W_E(q)=T^W_{B}\prod_i T_i(q_i)\)，输入是关节配置和固定 link/工具外参，输出是某个 frame 下的末端位姿。IK 则求解 \(q^*=\arg\min_q\,d(T^W_E(q),T^*)\)，其中距离可同时包含位置、旋转、平滑、关节限位和碰撞 penalty；冗余机械臂自由度多于任务约束时会有多解，目标超出 workspace 或违反 limit 时无解。数值方法常用 Jacobian transpose、伪逆或阻尼最小二乘，且必须检查 residual、limit、collision 和 step continuity；找到一个 IK 解不代表整条轨迹动态可行。对于策略输出的末端 delta pose，要先按 frame 和 unit 累积/变换，再交给 IK、impedance 或其他 low-level controller；控制频率、插值、夹爪通道和安全限幅也会改变实际执行。面试时要把“policy action → controller input → joint command → simulator/robot step”接口说完整，不能把 7D/12D action 维度直接等同于执行器物理量。

**项目挂钩**：不要把 policy 输出的 7D action 直接说成电机 torque。

**追问**：为什么 redundant arm 的 IK 有无限多解？

**易错**：IK 成功不代表路径无碰撞或动态可行。

**来源**：[5][38][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-034</b> · Jacobian 如何连接关节速度和末端速度？奇异位形有什么影响？</summary>

**30 秒回答**：局部关系是 \(\dot x=J(q)\dot q\)，其中 Jacobian 把关节速度映射为末端 linear/angular velocity（twist），每一列对应一个关节的局部贡献。接近奇异位形时 rank 降低或条件数变差，某些末端方向不可控，伪逆会放大关节速度和噪声；可用阻尼伪逆、限速或改变姿态缓解。

**机制展开（约 2 分钟）**：对末端 pose 映射 \(x=f(q)\)，Jacobian 是 \(J(q)=\partial x/\partial q\)，速度控制常求 \(\dot q=J^\#\dot x^*\)。普通伪逆在最小二乘意义下追踪目标，但当最小奇异值接近 0 时，\(J^\#\) 会把观测噪声、量化误差或 policy jerk 放大到关节速度；这不是单纯数值 bug，而是机构在该姿态的可控方向退化。阻尼最小二乘可写成 \(\dot q=J^\top(JJ^\top+\lambda^2I)^{-1}\dot x^*\)，通过 \(\lambda\) 换取少量 tracking bias 来降低速度爆炸；实际还要加入 joint-limit null-space、velocity/acceleration limit、碰撞约束和 controller rate。VLA action 的异常幅度可能来自模型，也可能来自 frame/normalization 错误、IK/Jacobian 放大或低层控制器，因此诊断要分别记录 raw action、denormalized action、IK residual、singular values、joint velocity 与最终 env step，不能只看 policy 输出。

**项目挂钩**：action jerk 或异常幅度可能来自模型，也可能来自 IK/Jacobian 放大。

**追问**：阻尼最小二乘为何更稳？

**易错**：奇异不是单纯数值 bug，而是机构在该姿态的可控方向退化。

**来源**：[37][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-035</b> · position、velocity、torque control 有什么区别？</summary>

**30 秒回答**：position control 给目标位置/角度，由底层回路产生速度或力矩；velocity control 给目标速度；torque control 直接给关节力矩，表达力强但对动力学模型、实时频率、接触稳定和安全限幅要求更高。VLA action 的 7D/14D 只是接口维度，必须说明最终 controller 语义和单位。

**机制展开（约 2 分钟）**：三者主要区别在控制层级、闭环带宽和对模型/安全的依赖：position/velocity 往往由成熟 servo 或 impedance loop 负责稳定性，policy 只需输出较高层 reference；torque control 让策略直接影响动力学，但噪声、延迟、负载变化和接触冲击会更直接地传到机器人。末端 delta pose 通常先在指定 frame 中反归一化，再经 IK/Jacobian 或 impedance controller 转成 joint target，最后由 position/velocity/torque loop 执行；同样的 7D 向量如果被解释为 pose delta、joint velocity 或 torque，系统行为完全不同。选型要看任务接触性、控制频率、动力学可信度、action horizon、sim2real gap 和 safety fallback；面试时应说明 saturate、rate limit、workspace/torque limit、E-stop 与 termination。OpenPiVLA 的 action contract 只有在与 LIBERO/ALOHA 的 controller、normalizer、gripper convention 和 step frequency 对齐后，才有可比的 offline/closed-loop 结果。

**项目挂钩**：OpenPiVLA 的 action contract 要与 LIBERO/ALOHA controller 匹配。

**追问**：末端 delta pose 最终如何变成关节命令？

**易错**：action 维度相同不代表控制语义相同。

**来源**：[9][35][36][37][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-036</b> · PID 的 P/I/D 各解决什么问题？</summary>

**30 秒回答**：P 对当前误差响应，增大通常更快但可能振荡；I 累积历史误差以消除稳态偏差，但会积分饱和；D 看误差变化趋势、提供阻尼，却容易放大测量噪声。实现必须同时处理采样周期、输出限幅、anti-windup、导数滤波和延迟。

**机制展开（约 2 分钟）**：离散 PID 可写成 \(u_t=K_pe_t+K_i\sum_{k\le t}e_k\Delta t+K_d(e_t-e_{t-1})/\Delta t\)，其中 \(e_t=r_t-y_t\)。P 主要决定局部刚度/响应速度；I 抵消持续偏差，但当输出饱和时继续累积会产生 windup，解除饱和后出现大 overshoot；D 提前感知变化、增加阻尼，但对高频 measurement noise 和 \(1/\Delta t\) 敏感，工程上常对 measurement 求导并加低通滤波，避免 setpoint jump 造成 derivative kick。anti-windup 可用 conditional integration（饱和且误差继续推向饱和时暂停积分）或 back-calculation，把 \(u_{sat}-u_{raw}\) 反馈到积分状态；还要记录积分限幅、输出 rate limit、单位、采样时间和 reset/termination 时的状态清理。闭环抖动不能只归因于 policy：action chunk、server latency、控制频率、normalizer、接触和 PID 参数都会改变误差序列，因此应分别记录 raw/commanded action、controller output、saturation、tracking error 与 timestamp。

**项目挂钩**：闭环轨迹抖动不一定是模型错误，也可能是 controller 参数和延迟问题。

**追问**：为什么 D 项常对测量值而不是误差求导？

**易错**：PID 不是“调大三个系数直到效果好”。

**来源**：[36]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-037</b> · 控制频率、推理延迟和 action chunk 如何共同影响稳定性？</summary>

**30 秒回答**：控制频率决定动作多久更新一次，推理/通信延迟会让策略基于过时 observation；action chunk 减少模型查询但执行越长越接近 open loop。短 replan 纠偏及时却更耗算力和带宽，长 chunk 更高效但误差积累更大。评估必须同时报告 policy query rate、controller rate、端到端 latency、预测 horizon 和实际执行前缀。

**机制展开（约 2 分钟）**：设 controller period 为 \(\Delta t_c\)，policy query period 为 \(\Delta t_p\)，端到端延迟为 \(\tau\)，则 observation 到 action 生效期间系统可能已经执行了约 \(\tau/\Delta t_c\) 个旧动作；chunk 长度 \(H\) 还决定了两次 replan 之间的最大 open-loop 步数。若 \(\tau\) 接近或超过控制周期，直接同步调用会阻塞控制 loop；常见设计是 observation buffer + inference worker + timestamped action queue，控制线程按 deadline 取最新可用前缀，过期或缺失时触发 hold/zero/fallback，而不是无限等待。chunk 执行可以用 early termination、receding-horizon overlap 或 uncertainty-triggered replan 折中；但 action overlap、队列丢弃、server retry、clock drift 和 reset/termination 语义必须记录。模型预测 horizon 不等于 controller 实际执行步数，尤其在 OpenPiVLA/UWM 的 action window、warmup、denormalization 和 controller slicing 之间。面试时要把 query rate、controller rate、latency percentiles、queue depth、executed prefix、termination 与 success predicate 放在同一 closed-loop protocol 中比较。

**项目挂钩**：OpenPiVLA 的 action window 与 UWM warmup/rollout protocol 都属于闭环合同。

**追问**：延迟大于控制周期时如何设计异步 pipeline？

**易错**：模型预测 horizon 不等于控制器一次实际执行的步数。

**来源**：[9][10][25][36][41][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-038</b> · denormalization、clipping 和 gripper 维度为什么会造成系统性失败？</summary>

**30 秒回答**：policy 输出通常仍在模型的 normalized space；执行前必须用训练时完全相同的方法、逐维统计量和维度顺序恢复 controller unit。normalizer 版本、axis/frame/unit 或 gripper 开闭编码错，会在每一步制造同方向的 scale/bias；clipping 虽能把数值压回合法范围，却可能让大量维度饱和并掩盖合同错误。诊断要做 action round-trip、逐维 sentinel、normalizer checksum，并同时记录 clipping rate 与最终 controller command。

**机制展开（约 2 分钟）**：对逐维 affine normalizer，可写成 \(z_i=(a_i-c_i)/s_i\)、\(a_i=s_i z_i+c_i\)；这里 \(z_i\) 是模型空间 action，\(a_i\) 是物理/控制器空间 action，\(c_i,s_i\) 可以来自 mean/std、quantile range 或其他训练时冻结的统计协议。公式可逆不代表实现一定正确：checkpoint 必须绑定 normalizer method/revision、dimension layout、absolute/delta 语义、frame、unit、valid dims 与 gripper convention。若 x/y 轴互换、角度 rad/deg 混用、不同数据集统计量复用，或者把 gripper 的 `[-1,1]`、`[0,1]`、开合宽度、binary open/close 符号混写，shape 检查仍可能通过，但闭环会出现稳定的方向、尺度或夹爪状态错误。随后 \(a'_i=\operatorname{clip}(a_i,l_i,u_i)\) 只能提供 safety saturation，不能修复 calibration；高 saturation ratio、长期贴边或 clipping 前后差值很大反而是 normalizer/schema 错配信号。定位时先对数据集 action 做 `denormalize(normalize(a))` round-trip，再让每个维度依次通过 one-hot/sentinel，核对 axis、sign、unit 与 gripper；然后用记录的 expert action 绕过 policy 走同一 adapter/controller，最后比较 raw model action、denormalized action、clipped action、controller command 和实际 state delta。这样才能区分模型预测错误、action adapter bug 与 controller/environment 问题。现有 OpenPiVLA inventory 仍把 axis/unit/normalizer/parser 标为 semantics-open，UWM inventory 也把 normalizer checksum 和 RoboCasa action order 列为缺口，因此可以把它们讲成评估前置 gate 和诊断风险，不能直接宣称已经证明某次失败的唯一根因。

**项目挂钩**：OpenPiVLA/UWM 的 normalizer、action order 与 gripper contract 是评估前置条件；当前证据只支持合同审计和风险定位，不支持把 normalizer 错配写成已闭合 root cause。

**追问**：怎样区分模型失败与 denormalization bug？

**易错**：动作“在范围内”不代表语义和轴顺序正确。

**来源**：[9][10][35][41][43]　**练习状态**：unseen

</details>

## E. 补齐基础与研究深度

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-005</b> · 期望、方差、协方差和相关系数有什么区别？</summary>

**30 秒回答**：期望 \(\mathbb E[X]\) 描述随机变量的平均位置；方差 \(\operatorname{Var}(X)\) 描述单变量围绕均值的平方波动；协方差 \(\operatorname{Cov}(X,Y)\) 描述两个变量的线性共同变化，但受量纲影响；相关系数 \(\rho_{XY}\) 再除以两边标准差，通常落在 \([-1,1]\)。在机器人 action 统计里必须逐维保留单位、valid mask 和数据切分；零相关不等于独立，相关也不代表因果。

**机制展开（约 2 分钟）**：令 \(\mu_X=\mathbb E[X]\)，则 \(\operatorname{Var}(X)=\mathbb E[(X-\mu_X)^2]=\mathbb E[X^2]-\mu_X^2\)，\(\operatorname{Cov}(X,Y)=\mathbb E[(X-\mu_X)(Y-\mu_Y)]\)，而 \(\rho_{XY}=\operatorname{Cov}(X,Y)/(\sigma_X\sigma_Y)\)。方差有平方量纲，协方差的量纲是两变量单位之积，所以位置、旋转和 gripper 维度不能靠原始数值大小直接比较；相关系数消除了尺度，却只刻画线性关系，而且当某一维 \(\sigma=0\) 时没有定义。对随机向量 \(a\)，协方差矩阵 \(\Sigma=\mathbb E[(a-\mu)(a-\mu)^\top]\) 必须半正定，因为任意向量 \(v\) 都满足 \(v^\top\Sigma v=\operatorname{Var}(v^\top a)\ge 0\)。工程上要说明统计量来自 train split，按 action layout 与任务/机器人域计算，并正确处理 padding、invalid dimensions、episode 长度和时间相关性；样本方差采用 \(n\) 还是 \(n-1\) 也要与实现一致。逐维 normalizer 通常只使用边缘均值/尺度，不会自动消除维度间相关性；若混入不同 frame、unit、absolute/delta 语义或 gripper 编码，得到的均值和协方差即使数值稳定也没有统一物理含义。OpenPiVLA/UWM 当前 inventory 只支持把 normalizer revision、action order、valid mask 和 train/eval split 当作审计项，尚无证据支持声称已得到某组个人项目 action 统计或由它闭合了失败根因。

**项目挂钩**：OpenPiVLA/UWM 的 action normalization 应按维度绑定 layout、unit、mask 与统计版本；当前证据只支持合同审计，不支持把某个统计异常写成已验证 root cause。

**追问**：为什么协方差矩阵必须半正定？

**易错**：相关系数接近 0 只说明线性相关弱，不代表完全独立。

**来源**：[27][41][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-007</b> · KL divergence 的方向为什么重要？</summary>

**30 秒回答**：\(D_{KL}(P\|Q)=\mathbb E_{x\sim P}[\log P(x)-\log Q(x)]\) 由 P 决定期望区域；Q 若漏掉 P 有质量的 mode 会被强罚，所以近似优化常更偏 mode-covering。反向 \(D_{KL}(Q\|P)\) 只在 Q 自己覆盖的区域取期望，更可能选中 P 的一个 mode。它不对称、没有三角不等式，不是普通距离；代码里必须说明谁是 target、谁是 student、输入是 logits/log-prob/prob、mask 和 reduction。

**机制展开（约 2 分钟）**：KL 的定义是 \(D_{KL}(P\|Q)=\sum_x P(x)\log\frac{P(x)}{Q(x)}\ge 0\)，等号只在几乎处处 \(P=Q\) 时成立。方向重要的根源是权重分布不同：forward KL 用 P 加权，若 \(P(x)>0\) 而 \(Q(x)\to0\)，代价趋于无穷；reverse KL 用 Q 加权，Q 没覆盖的 P mode 几乎不进入期望，但 Q 若把质量放到 \(P(x)=0\) 的区域同样会发散。“mode-covering/mode-seeking”是多峰近似族受限时的常见行为，不是无条件定理；若模型族足以精确表示 P，两种方向的最优解都可为 P。实现层面要先对齐同一 token/动作 support：teacher logits \(z_T\)、student logits \(z_S\) 经 log-softmax 得到 \(\log p_T,\log p_S\)，teacher-to-student 蒸馏常计算 \(\sum_v p_T(v)(\log p_T(v)-\log p_S(v))\)。PyTorch `KLDivLoss` 默认把 `input` 解释为 log-prob、`target` 解释为 probability；`log_target=True` 时 target 才是 log-prob，且 `batchmean` 才与“按 batch 求和再除 batch size”的 KL 定义对齐。token mask、temperature、vocab revision、padding 和 denominator 任一不一致，都可能让“方向正确”的公式落到错误实现。

**项目挂钩**：OPD formal `point/train_opd_online_vl.py` 计算 \(D_{KL}(q_\beta\|p_S)\)：veto beta=0 时为 teacher∥student，beta>0 时 target logits 还加入 detached student logits；根目录同名 legacy trainer 则是 teacher top1 hard-label CE。两份实现必须按完整路径和 run summary 分开，详见 [OPD Training Objective Lineage Gate](../evidence/projects/opd_training_objective_lineage_gate.html)。

**追问**：为什么 KL 不满足对称性和三角不等式？`KLDivLoss(mean)` 与 `batchmean` 有什么差别？为什么 mode-covering/mode-seeking 只能作为近似族受限时的经验描述？

**易错**：把 forward/reverse 名称记反；把 logits 直接传给 `KLDivLoss`；忽略 target 是否为 log；把 mode-covering/mode-seeking 说成无条件定理；把 KL 当作 metric。

**来源**：[14][31][44]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-008</b> · bias-variance trade-off 如何影响策略学习和评估？</summary>

**30 秒回答**：bias 是学习器平均预测相对真实目标的系统性误差，variance 是训练数据、初始化或优化随机性变化时模型输出的波动。更大模型通常能降低近似 bias，但不保证只降低 bias，也可能放大估计方差和优化不稳定。机器人评估还要把 training-seed variance、task/init 差异和固定 policy 的 episode 二项噪声分开；多跑同一 checkpoint 只能估计后者，不能替代多个独立训练 run。

**机制展开（约 2 分钟）**：在平方误差和固定输入 \(x\) 下，若训练集为随机变量 \(\mathcal D\)，经典分解为

\[
\mathbb E_{\mathcal D,\epsilon}\!\left[(y-\hat f_{\mathcal D}(x))^2\right]
=\sigma_\epsilon^2
+\left(\mathbb E_{\mathcal D}[\hat f_{\mathcal D}(x)]-f(x)\right)^2
+\operatorname{Var}_{\mathcal D}[\hat f_{\mathcal D}(x)].
\]

第一项是不可约噪声，第二项是 squared bias，第三项是 estimator variance。它依赖损失、数据生成过程和模型族，不能把训练误差直接叫 bias、测试误差直接叫 variance。正则、更强先验、数据增强或早停常以增加部分 bias 换取更低 variance；更多独立覆盖通常降低估计方差；增大模型容量可能降低 approximation bias，但有限数据下的方差、优化路径和分布外行为未必单调。对 VLA policy，还要把 action-supervision bias、dataset coverage、closed-loop compounding error 和 evaluator noise 分层。固定 checkpoint、task/init protocol 下，二元 success 的条件方差约为 \(p(1-p)/n\)；它只描述 episode sampling，不包含换训练 seed 后 policy 本身的变化。可信比较应保存 training/data/env/rollout/bootstrap seed，先在同 task/init 上做 paired episode 比较，再把独立 training run 作为顶层 replicate，报告逐任务分布和区间，而不是把同一 checkpoint 的几百个 episode 当成几百个训练样本。

**项目挂钩**：UWM 的 `186/250` 是用户确认的 fixed-pruned-init summary，五个 task 使用 task-specific checkpoints，本地缺多 training-seed panel 和 250 条 raw episode，因此既不能估 training variance，也不能把它与论文三 seed/OOD protocol直接比较。WAM full10k 与 official-HF path 的 checkpoint/config lineage也未做 matched join，`0/118` 与 `84/118` 不能解释为 bias–variance 分解或训练因果效果。

**追问**：增加模型规模通常只会降低 bias 吗？同一 checkpoint 跑 250 个 episode 为什么不能估计 training-seed variance？paired init 能消除哪些方差、不能消除哪些？

**易错**：bias–variance 不是“训练误差 vs 测试误差”的同义词；episode 数不等于独立 training runs；不同协议的百分比不能拿来估计方差或 bias。

**来源**：[4][27][42][43][46]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-009</b> · 为什么深度网络需要非线性激活？GELU 和 SiLU 有何特点？</summary>

**30 秒回答**：连续仿射层之间若没有非线性，任意深度都可合并为一个仿射变换，深度不会增加这部分网络的函数表达力。GELU 是 \(x\Phi(x)\) 的高斯 CDF 自门控，SiLU 是 \(x\sigma(x)\) 的 sigmoid 自门控；二者都平滑、保留小负值，但不存在脱离架构与训练协议的必然优劣，微调预训练模型时应服从原 checkpoint/config。

**机制展开（约 2 分钟）**：若每层只有 \(h_{k+1}=W_kh_k+b_k\)，则多层复合仍满足

\[
h_L=W_{\mathrm{eff}}x+b_{\mathrm{eff}},
\]

其中 \(W_{\mathrm{eff}}\) 是各层权重的连乘，偏置也能合并。逐元素非线性 \(\phi\) 把下一层变成 \(h_{k+1}=\phi(W_kh_k+b_k)\)，从而产生随输入变化的门控和曲率，网络才可组合出复杂分段或平滑决策边界。这里要限定口径：Transformer 即使拿掉 MLP 激活，attention softmax 和 normalization 仍可能提供非线性；“退化为单层”说的是纯仿射链，不是所有现代网络的完整计算图。

两种平滑激活及其梯度可写为

\[
\begin{aligned}
\operatorname{GELU}(x)&=x\Phi(x), &
\operatorname{GELU}'(x)&=\Phi(x)+x\varphi(x), \\
\operatorname{SiLU}(x)&=x\sigma(x), &
\operatorname{SiLU}'(x)&=\sigma(x)+x\sigma(x)(1-\sigma(x)).
\end{aligned}
\]

这里 \(\Phi\) 和 \(\varphi\) 分别是标准高斯 CDF 与 PDF，\(\sigma\) 是 logistic sigmoid。GELU 常用 exact 或 tanh approximation；SiLU 也称 Swish（无可学习缩放的常用形式）。二者在负半轴允许有限负输出，零点附近梯度连续，不像 ReLU 在全部负输入上梯度恒为 0；但它们在很负的区域梯度仍会趋近 0，所以“平滑”不等于消除梯度消失。SwiGLU 则是带两路线性投影和乘法门的 MLP 结构，不能与单个 SiLU 激活混为一谈。

**项目挂钩**：本地 `Project` 快照中，`uwm_robocasa_transfer/uwm_robocasa_train.py` 在 state/right-view residual projection 和 phase/control/contact/progress auxiliary heads 使用 `nn.SiLU()`；`cosmos_policy_deepspeed_train.py` 也使用 `nn.SiLU()`，但类注释明确它只是 objective-compatible DeepSpeed proxy，不是完整 Cosmos Policy。面试时可说“我从实现核对了新增模块/代理模型的激活与 checkpoint compatibility”，不能说完整上游 backbone 都采用 SiLU，也不能把某次训练或闭环结果因果归因于它。[49]

**追问**：ReLU 的 dying neuron 如何出现？为什么不能在加载预训练权重后随意把 GELU 换成 SiLU？

**易错**：GELU/SiLU 平滑不等于一定收敛更快或永不饱和；SiLU 与 SwiGLU 不是同一层级的概念；不要由局部 adapter/proxy 实现外推完整 backbone。

**来源**：[15][16][27][47][48][49]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-014</b> · 位置编码解决什么问题？RoPE 如何提供相对位置信息？</summary>

**30 秒回答**：不含位置相关 mask/encoding 的 content-only self-attention 对 token 置换是等变的，能看内容关系却不知道顺序和距离。RoPE 按位置把 query/key 的每个二维通道对旋转；因为 \(R_m^\top R_n=R_{n-m}\)，旋转后的 QK 内积自然依赖相对位移 \(n-m\)。它不是简单相加绝对位置，也不自动保证长上下文外推。

**机制展开（约 2 分钟）**：对没有位置相关 mask 的 self-attention，若 \(P\) 是 token 维的置换矩阵，则

\[
\operatorname{SA}(PX)=P\operatorname{SA}(X).
\]

这表示输入 token 怎样重排，输出只会跟着同样重排；模型没有单独的“第几个 token”信号。causal mask 本身会引入前后可见性的偏序，但仍不等于给出了可泛化的相对距离表示。位置编码的作用，是把序号、二维 patch 坐标或其他位置结构注入 attention 计算。

RoPE 对 head dimension 中第 \(j\) 个二维通道对使用位置 \(m\) 与频率 \(\theta_j\) 形成旋转：

\[
R(m\theta_j)=
\begin{bmatrix}
\cos(m\theta_j) & -\sin(m\theta_j) \\
\sin(m\theta_j) & \cos(m\theta_j)
\end{bmatrix},\qquad
\widetilde q_m^{(j)}=R(m\theta_j)q_m^{(j)},\quad
\widetilde k_n^{(j)}=R(n\theta_j)k_n^{(j)}.
\]

其中 \(m,n\) 是 position id，\(\theta_j\) 是第 \(j\) 个频率。旋转不改变 Q/K tensor shape；关键是正交旋转满足

\[
\left(\widetilde q_m^{(j)}\right)^\top\widetilde k_n^{(j)}
=\left(q_m^{(j)}\right)^\top R\!\left((n-m)\theta_j\right)k_n^{(j)},
\]

所以 attention logit 同时保留内容相似度并显式依赖相对位移。标准 RoPE 旋转 Q/K，是因为它们决定 attention routing；V 是按这些权重聚合的内容。旋转 V 并非数学上绝对禁止，但会把内容放进位置相关坐标系，需要额外一致性设计，不能当作标准 RoPE 的默认做法。

实现时还要核对 `position_ids`、padding/packing 重置规则、head dimension、频率表、最大训练长度与 scaling recipe。长上下文失败可能来自未见过的相位组合、频率分布或 scaling 不匹配；RoPE 的相对内积形式不等于无限外推保证。对 VLA，多模态 token 序列中的 image patch、instruction 和 action token 都有序，但 token position 不是机器人 timestamp、控制频率或传感器同步；二维/时间位置还需要模型自己的映射规则。

**项目挂钩**：本地 `Project` HEAD `6c524d9` 的 Cosmos/WAM Transformer Engine shim 用 `_rotate_half` 和 `tensor * cos + rotate_half(tensor) * sin` 应用预计算 RoPE，并处理 `bshd/sbhd` layout 与维度检查；这能支持“我核对了旋转 kernel 的 tensor contract”。但 shim 不生成频率，也未证明完整模型的 Q/K call site、长上下文能力或指标效果。OpenPiVLA formal path 只确认加载 Qwen3-VL，本地没有冻结 base `config.json` 的 RoPE 参数，因此不能宣称 exact multimodal RoPE 配置。[41][42][50]

**追问**：为什么标准 RoPE 主要旋转 Q/K 而不直接旋转 V？packed sequence 的 `position_ids` 若不重置会发生什么？一维 token position 为什么不能替代图像二维坐标或机器人 timestamp？

**易错**：self-attention 是置换等变而非简单“置换不变”；相对位置进入 QK 内积不代表模型只含相对信息；RoPE 不等于无限长外推，也不能完成传感器时间对齐。

**来源**：[1][17][41][42][50]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-015</b> · pre-norm 和 post-norm 的训练差异是什么？</summary>

**30 秒回答**：pre-norm 写成 \(x_{l+1}=x_l+F_l(N(x_l))\)，归一化在子层前，残差主干保留显式 identity path，深层优化通常更稳；post-norm 是 \(x_{l+1}=N(x_l+F_l(x_l))\)，每层输出被重新归一化，但反向梯度必须经过 norm Jacobian，对初始化、学习率和 warmup 往往更敏感。它讨论的是 norm 相对子层/残差的位置，不是 LayerNorm 与 RMSNorm 的区别。

**机制展开（约 2 分钟）**：令 \(F_l\) 表示 attention 或 MLP 子层，\(N\) 表示 LayerNorm/RMSNorm 一类归一化，则两种残差块可抽象为

\[
\begin{aligned}
x_{l+1}^{\mathrm{pre}} &= x_l+F_l\!\left(N(x_l)\right), \\
x_{l+1}^{\mathrm{post}} &= N\!\left(x_l+F_l(x_l)\right).
\end{aligned}
\]

对应的局部 Jacobian 结构是

\[
\frac{\partial x_{l+1}^{\mathrm{pre}}}{\partial x_l}
=I+J_{F_l}J_N,
\qquad
\frac{\partial x_{l+1}^{\mathrm{post}}}{\partial x_l}
=J_N\!\left(I+J_{F_l}\right).
\]

pre-norm 中的 \(I\) 给残差流提供不经过 norm 的直接梯度项；post-norm 则在每个 block 输出端乘上 \(J_N\)，深层连乘更依赖初始化和优化 recipe。Xiong 等人的理论与实验结论是在其假设和设置下：Post-LN 初始化时靠近输出层的期望梯度可能较大，warmup 有助于稳定；Pre-LN 梯度更平衡，并可在相应设置下减少 warmup 依赖。面试时不能把它升级成“Pre-LN 永远不需要 warmup”。[32]

代价也要讲清：pre-norm 的 raw residual stream 不在每个 block 末端重新归一化，\(x_l\) 会累加各层增量，尺度可能随深度增长，因此通常还要 final norm、合理初始化或 residual scaling；这不等于必然发散。post-norm 每层输出尺度受控，但优化可能更敏感。最终收敛质量还取决于深度、初始化、残差缩放、optimizer、学习率、warmup、精度和数据，不能只靠 norm 位置排序。

**项目挂钩**：OpenPiVLA formal trainer 直接 `from_pretrained` 加载 `Qwen3VLForConditionalGeneration`，LoRA 默认只命中 `q_proj,k_proj,v_proj,o_proj`，没有重写 decoder norm/residual 顺序。与本地环境记录的 Transformers `4.57.1` 对应的官方 Qwen3-VL 代码中，`input_layernorm → self_attn → residual add`，再 `post_attention_layernorm → MLP → residual add`，所以两个子层都是 pre-norm；变量名 `post_attention_layernorm` 只是“位于 attention 之后”，因为它在 MLP 之前，不能误判为 Post-LN。当前缺远端 runtime source hash 与 base config snapshot，因此这是 version-matched official-code mapping，不是运行时 binary 证明，也不能把上游结构说成个人设计。[41][51]

Cosmos/WAM 本地 `RMSNorm` compatibility shim 只实现均方根归一化算子，没有 frozen full-block call site；它能证明 norm operator contract，不能证明完整 Cosmos block 是 pre-norm 还是 post-norm，更不能解释训练指标。[42][51]

**追问**：为什么 `post_attention_layernorm` 仍可属于 pre-norm？pre-norm residual stream 的尺度为什么可能增长？能否把预训练 Post-LN checkpoint 直接改成 Pre-LN 后继续加载？

**易错**：pre/post 说的是 norm 相对子层与 residual add 的位置；不要与 LayerNorm/RMSNorm 类型混淆，也不要把“通常更稳”说成“必然更优或无需 warmup”。

**来源**：[1][2][3][32][41][42][51]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-017</b> · LoRA 为什么能减少可训练参数？低秩假设的代价是什么？</summary>

**30 秒回答**：LoRA 冻结 \(W_0\in\mathbb R^{d_{out}\times d_{in}}\)，只学习 \(BA\) 的 rank-\(r\) 更新，使可训练参数从 \(d_{out}d_{in}\) 降到 \(r(d_{in}+d_{out})\)。它主要节省参数梯度和 optimizer states，不会让 base weights 或 activation 自动消失。代价是更新被限制在低秩子空间；rank、target modules、alpha、dropout 和数据若不匹配，会欠拟合或漏掉关键适配方向。

**机制展开（约 2 分钟）**：标准 LoRA 线性层可写成

\[
\begin{aligned}
y &= W_0x+sBAx,\qquad s=\frac{\alpha}{r}, \\
A&\in\mathbb R^{r\times d_{in}},\qquad
B\in\mathbb R^{d_{out}\times r},\qquad r\ll\min(d_{in},d_{out}), \\
N_{\mathrm{LoRA}}&=r(d_{in}+d_{out})\ll d_{out}d_{in}.
\end{aligned}
\]

这里 \(W_0\) 冻结，\(A,B\) 和允许训练的其他参数进入 optimizer；\(\alpha/r\) 是常见 scaling，具体实现还要检查是否启用 rsLoRA 等变体。LoRA 的效率来自“不为整块 \(W_0\) 保存 weight gradient 和 Adam 一、二阶状态”，不是不经过 base network：前向仍需要 base weights，反向仍要穿过冻结层计算 adapter 梯度，activation memory 也受 batch、sequence、checkpointing 和精度影响。QLoRA 的 base quantization 是另一项机制，不能与普通 LoRA 混为一谈。

低秩假设是“任务所需的有效权重增量近似落在低维子空间”。若真实更新的有效 rank 大于 \(r\)，或者只把 adapter 放进 Q/K/V/O 而任务主要需要 MLP、vision encoder、cross-modal connector 或 action head 改变，LoRA 会形成容量瓶颈。提高 rank 或扩大 target modules 能增强表达，但会增加 trainable params、optimizer memory、adapter storage 和过拟合风险；\(\alpha\) 改变更新尺度，dropout 改变训练时支路，不能只报一个 rank 就说 recipe 相同。

推理侧也要分清：未 merge 时需要额外计算 \(BAx\)，可能有 kernel/serving 开销；merge 后用 \(W'=W_0+sBA\) 可消除额外支路，但 dense weight 的形状、基础参数规模与主要 dense FLOPs 没变。LoRA 的优势是训练和多 adapter 存储/切换，不是天然模型压缩。

**项目挂钩**：当前 OpenPiVLA formal trainer 使用 PEFT `LoraConfig(r=16, alpha=32, dropout=0.05, bias="none")`，默认 target 为 `q_proj,k_proj,v_proj,o_proj`；代码按 `requires_grad` 统计并打印 trainable/total params。committed report 记录 `6,422,528 / 2,133,954,560 ≈ 0.301%`，但 raw start log、adapter binary/hash 与 fresh-load smoke 未同步，所以该数字只能说 `report-supported`，不能说本地已由 checkpoint 复算。更关键的是归档目标 YAML 为 `lora: False`，其中 `lora_r: 32` 只是未启用字段；当前 sanitized LoRA formal path 不能倒推成历史原 run 也使用 LoRA。[41][52]

面试 ownership 只能说“核对/接入了 Qwen3-VL + PEFT LoRA formal path、target modules 和参数账本”，不能把 LoRA 算法或 Qwen upstream architecture 说成个人创新，也不能把 6.42M 参数直接等同于 benchmark 效果。[41][52]

**追问**：为什么 LoRA 明显减少 optimizer memory，却不按相同比例减少总训练显存？只在 attention projection 注入可能漏掉什么？merge 后为什么不等于模型被压缩？如何证明一个 adapter checkpoint 可独立加载？

**易错**：可训练参数少不等于 base parameters、activation、推理 FLOPs 同比例下降；配置中出现 `lora_r` 不等于 LoRA 已启用；不要把当前 adapter recipe 归属于 lineage 未闭合的历史 run。

**来源**：[18][41][51][52]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-018</b> · KV cache 为什么能加速自回归推理？</summary>

**30 秒回答**：自回归第 \(t\) 步只新增一个 token，历史 token 在各层的 K/V 不再变化；KV cache 保存它们，新步只算当前 token 的 Q/K/V，再让 \(q_t\) 关注缓存前缀，避免每一步重跑整个 prefix。它主要加速 decode，不消除串行 token 数；代价是 cache 显存随 layer、batch、KV heads、上下文长度和 dtype 线性增长，长上下文/高并发时可能由 compute-bound 变成 memory-bound。

**机制展开（约 2 分钟）**：对 decoder 第 \(l\) 层的第 \(t\) 个 token，cache 更新和 attention 可写为

\[
\begin{aligned}
K_{1:t}^{(l)}&=\operatorname{concat}\!\left(K_{1:t-1,\mathrm{cache}}^{(l)},k_t^{(l)}\right), \\
V_{1:t}^{(l)}&=\operatorname{concat}\!\left(V_{1:t-1,\mathrm{cache}}^{(l)},v_t^{(l)}\right), \\
o_t^{(l)}&=\operatorname{softmax}\!\left(\frac{q_t^{(l)}K_{1:t}^{(l)\top}}{\sqrt{d_h}}+M_t\right)V_{1:t}^{(l)}.
\end{aligned}
\]

这里 \(M_t\) 是 causal/padding mask，\(d_h\) 是 head dimension。没有 cache 时，每个 decode step 会再次计算历史 token 的 layer states 和 K/V projection；有 cache 时历史 K/V 直接复用。但当前 query 仍要与长度 \(t\) 的 K 做 attention，所以单步 attention 成本仍随上下文增长；生成 \(T\) 个 token 仍有 \(T\) 次串行 forward，KV cache 不会把 autoregressive decoding 变成一次并行 action head。

常规 dense cache 的近似字节数为

\[
M_{\mathrm{KV}}\approx 2LBT H_{\mathrm{kv}}d_h\,b,
\]

其中系数 2 对应 K 和 V，\(L\) 是 decoder layers，\(B\) 是含 beam/并发展开后的 batch，\(T\) 是已缓存序列长度，\(H_{\mathrm{kv}}\) 是 KV heads，\(b\) 是每元素字节数。GQA/MQA 通过减少 \(H_{\mathrm{kv}}\) 降低 cache；quantized/offloaded/sliding-window cache 则以精度、带宽或有效上下文换显存。cache 必须和相同模型权重、prefix、position ids、mask 与 batch reorder 对齐，否则复用会产生错误结果。

prefill 与 decode 也要分开：prefill 仍要并行处理完整 prompt 并建立首份 cache；cache 的主要收益出现在后续逐 token decode。teacher-forcing 训练一次并行计算整段 labels，没有跨 decode step 的前缀复用，保留 cache 反而增加状态/显存并常与 gradient checkpointing 冲突，所以训练代码通常关闭 `use_cache`。encoder-only 一次处理完整输入，也没有同样的 decoder self-attention 逐步追加场景；encoder-decoder 可以另行缓存 encoder/cross-attention K/V，概念相近但生命周期不同。

**项目挂钩**：OpenPiVLA formal trainer 在加载 Qwen3-VL 后显式 `model.config.use_cache=False`，这属于 full-chat causal-CE 训练合同；formal package 又缺 generation/parser/controller，所以当前没有 formal action-token decode latency 可以声称。OPD raw-holdout eval 则显式设置 `model.config.use_cache=True`，并调用 `generate(..., use_cache=True)`；这能证明 eval generation 请求了 cache，但没有 cache-on/off matched benchmark、peak-memory trace 或机器人控制延迟，因此不能量化加速。OPD full-vocab teacher/student loss forward 仍显式 `use_cache=False`。[41][44][53]

对 VLA 还要先判断 action 输出范式：离散 action text/token 的逐 token generation 可受益于 KV cache；一次并行连续 action head、diffusion denoising 或已生成的 action chunk 不会因为“有 KV cache”就减少自身 denoising/控制步数。[41][42][43]

**追问**：为什么 KV cache 降低重复计算却可能让 decode 更 memory-bound？GQA/MQA 如何改变 cache 大小？training 为什么通常关闭 cache？encoder-decoder 的 cross-attention cache 与 decoder self-attention cache 有何不同？

**易错**：cache 不是把生成并行化，也不消除当前 token 对全部历史 K/V 的读取；`use_cache=True` 只能证明请求了功能，不能替代 on/off latency、显存和输出一致性实验。

**来源**：[19][41][42][43][44][51][53]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-019</b> · 梯度消失/爆炸如何定位？</summary>

**30 秒回答**：我不会从最终 loss 直接猜“梯度爆炸”。先冻结代码、checkpoint、数据顺序、精度和第一个异常 step，用同一 batch 重放；在 optimizer step 前，FP16 要先 unscale，再同时看 loss、scaler 是否跳步、全局及逐层 grad norm、参数/梯度非有限值。爆炸表现为 norm 突增或 NaN/Inf，消失表现为早层长期接近零，但还要排除空 mask、错误分母、detach、学习率/调度器、累积与 `zero_grad` 顺序。最后用 FP32/小 batch 重放定位；clipping 只能止血，不能代替根因修复。

**机制展开（约 2 分钟）**：深层网络的反向传播是 Jacobian 连乘。若 \(h_{k+1}=f_k(h_k)\)，则

\[
\frac{\partial \mathcal L}{\partial h_l}
=
\left(\prod_{k=l}^{L-1}J_k^{\top}\right)
\frac{\partial \mathcal L}{\partial h_L},
\qquad
J_k=\frac{\partial h_{k+1}}{\partial h_k}.
\]

这里 \(J_k\) 是第 \(k\) 层局部 Jacobian；连乘的有效奇异值长期小于 1 会让早层梯度衰减，长期大于 1 会放大梯度。残差路径、归一化、激活饱和、初始化和序列长度都会改变这条链，所以“模型很深”只是风险因素，不是根因证据。

我的定位顺序是：第一，固定 run identity，并找到 first bad step，而不是只比较两个 run 的最终 loss。第二，在 backward 后、optimizer step 前记录未裁剪的 global norm；混合精度若用了 `GradScaler`，必须先 `unscale_(optimizer)`，否则看到的是放大后的梯度。第三，把统计下钻到 trainable parameter group/layer：记录 grad L2、max、p99、零梯度比例，并配对看 activation、weight、optimizer state 是否 finite；global norm 正常也可能掩盖某个早层长期接近零。第四，检查 loss contract 和数据：有效 token/action mask 分母是否为零、label 是否全 ignore、异常图像/动作是否进入 batch、loss reduction 是否随序列长度突变，以及梯度累积时是否过早 `zero_grad`、少除或多除 accumulation steps。第五，保存首个坏 batch，用 FP32、batch=1、关闭可选 head/AMP 的 matched replay 二分定位；若 FP32 正常而低精度失败，才把精度路径升级为强嫌疑。

全局范数裁剪可写为

\[
g\leftarrow g\,\min\!\left(1,\frac{\tau}{\lVert g\rVert_2+\epsilon}\right),
\]

其中 \(g\) 是所有待更新参数梯度拼接后的向量，\(\tau\) 是阈值。它保留方向并限制范数；PyTorch `clip_grad_norm_` 的返回值是裁剪前 total norm，因此适合记录，但要注明统计时点。持续触发 clipping 说明优化仍在撞阈值，后续应通过 matched rerun 检查学习率/warmup、loss 尺度、数据 outlier、残差/归一化或初始化，而不能把“训练没 NaN”写成根因已解决。[27][32][33][34]

**项目挂钩**：OpenPiVLA formal trainer 对 `requires_grad` 参数在 accumulation 边界调用 `clip_grad_norm_`，随后记录其返回的 `grad_norm`，再 `optimizer.step()` 与 `zero_grad()`；默认阈值是 1.0，但代码没有逐层 activation/grad trace，也没有显式 non-finite gradient gate，所以只能证明“有全局止血与稀疏日志”，不能证明某次 run 没有梯度异常。UWM/LIBERO 与 UWM/RoboCasa 的本地非 DeepSpeed AMP 路径都先 `scaler.unscale_` 再裁剪，符合统计/裁剪顺序，但返回 norm 被丢弃；RoboCasa 的 DeepSpeed 分支绕过这段本地 clip，实际行为还要对账当次 DeepSpeed config。formal OPD 明确拒绝 non-finite loss，TrainingArguments 传入 `max_grad_norm`，回调检查已记录的 loss/grad_norm/lr；这仍不等于 layer-wise 根因定位。当前没有可复算的 matched bad-step bundle，因此 WAM step-1500 save API failure、UWM DataLoader stall 或闭环 eval 失败都不能反推为梯度爆炸。[41][43][44][54]

**追问**：`clip_grad_norm_` 返回的是裁剪前还是裁剪后 norm？为什么 FP16 要先 unscale 再裁剪？global norm 正常但 loss 不降，还要查哪些 trainable-parameter、mask/target、optimizer/scheduler 和数据问题？如何构造 first-bad-batch 的 matched replay？

**易错**：clipping 是 containment，不是 diagnosis；loss spike、OOM、DataLoader stall、checkpoint 保存异常或 online success 低都不能单独证明梯度爆炸。只有日志里出现 `grad_norm` 字段，也不等于已经记录了逐层、未裁剪、正确 unscale 时点的梯度证据。

**来源**：[27][32][33][34][41][43][44][54]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-020</b> · 多任务共享 backbone 时如何判断梯度冲突？</summary>

**30 秒回答**：我会在同一个参数快照上，把每个任务对共享参数的梯度单独算出来，再看 pairwise cosine、梯度范数比例和各任务验证指标。余弦为负表示一阶局部冲突：沿任务 \(i\) 的下降方向会抬高任务 \(j\)；但零梯度时 cosine 无定义，正余弦也可能被数量级失衡掩盖。mask、route 或独立 head 只隔离样本/输出路径；只要 backbone 仍被多个任务更新，就要用 matched task batches 实测，不能从 loss 大小或指标涨跌直接下结论。

**机制展开（约 2 分钟）**：只在真正共享的参数 \(\theta_s\) 上定义任务梯度 \(g_i=\nabla_{\theta_s}\mathcal L_i\)。同一参数快照、同一 train/eval mode 和固定随机性下，pairwise 诊断为

\[
c_{ij}=\frac{g_i^{\top}g_j}{\lVert g_i\rVert_2\lVert g_j\rVert_2},
\qquad
\mathcal L_j(\theta_s-\eta g_i)
\approx \mathcal L_j(\theta_s)-\eta g_j^{\top}g_i.
\]

这里 \(c_{ij}<0\) 表示当前点附近的 first-order conflict；\(c_{ij}>0\) 是局部对齐，不保证长期 joint training 更好。若任一 \(\lVert g_i\rVert\) 接近零，应报告“cosine undefined/低信号”，而不是解释成正交。工程上我会在 optimizer step 前，对每个 active task/route 分别调用 `autograd.grad(loss_i, shared_params)`，不让梯度先累积；同时记录 active mask/token/sample 分母、global 与 layer-wise norm、cosine 分布、负余弦频率和 norm ratio。大模型算不起全参数时可固定一组共享 block 或 LoRA 参数做 probe，但必须写清采样参数集合，不能把局部 probe 冒充全模型结论。

若训练实际使用 \(g=\sum_i w_i g_i\)，任务 \(i\) 的一阶变化和 PCGrad-style 投影可写成

\[
\Delta\mathcal L_i\approx-\eta g_i^{\top}\!\left(\sum_jw_jg_j\right),
\qquad
\tilde g_i
=g_i-\frac{\min(0,g_i^{\top}g_j)}{\lVert g_j\rVert_2^2+\epsilon}g_j.
\]

第一式说明调 loss weight 只会重标梯度，不能保证所有 \(g_i^{\top}g>0\)；所以总 loss 下降不等于每个任务改善。第二式在 pairwise dot product 为负时去掉冲突分量，但会改变优化问题，也不保证有限步、非凸训练中的 Pareto 改善。是否采用 reweight、gradient surgery、任务 adapter/branch 或 stop-gradient，必须用固定数据比例、相同训练预算和每任务指标做 matched ablation，而不是只比较 aggregate loss。[20]

**项目挂钩**：WAM 正式合同是共享 diffusion backbone 上的 action/future/value latent slots、condition/loss mask 与 policy/world/value sample routing，并非三个独立 head；本地 online-text 入口继续调用 official trainer/model/dataloader，没有 per-role `autograd.grad` 或 gradient-cosine 记录。另一个 MetaX DeepSpeed 文件确实用共享 proxy trunk、四个显式 head 和加权 MSE，但文件自述为兼容 adapter/proxy，不能反推正式 Cosmos checkpoint 的优化行为。要验证 WAM 冲突，应在同一 checkpoint 上各取 policy/world/value matched routed batch，对相同 diffusion blocks 分别求梯度。formal OPD 则强制一个 microbatch 内 route 一致，只计算该 routed teacher 的 full-vocabulary KL，再乘 sample weight；五条 route 是跨 step 共享 student 的多域训练，不是五个 loss 同时反传。应在同一 student snapshot 上各取一个 matched route batch 测共享参数梯度；route count、loss weight、不同 pool 的最佳 checkpoint 分散都不是 gradient conflict 的直接证据。[42][44][55]

**追问**：为什么 loss 数值更大不一定梯度更大？为什么 \(c_{ij}<0\) 只是局部一阶证据？route-homogeneous microbatch 如何做跨 route matched gradient probe？简单调权重为什么不能保证 Pareto 改善？PCGrad 可能牺牲什么？

**易错**：loss 曲线相反、不同任务最佳 checkpoint 不同、mask 非重叠或 route 分开都不能单独证明共享参数梯度冲突；head-specific 参数没有跨 head 冲突，但 shared backbone 仍可能有。计算 cosine 前要对齐同一参数快照、未混合的任务梯度、有效 mask 分母和参数集合。

**来源**：[20][42][44][55]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-026</b> · PPO clipping 的直觉是什么？</summary>

**30 秒回答**：PPO 用新旧策略的概率比 \(r_t(\theta)\) 加权 advantage，但把 surrogate objective 的贡献限制在 \([1-\epsilon,1+\epsilon]\) 的邻域，避免一次更新把策略推离采样 rollout 的旧策略太远。clipping 是近似 trust region，不是严格 KL 约束；还要看 value loss、entropy、advantage normalization 和 rollout freshness。

**机制展开（约 2 分钟）**：先定义 \(r_t(\theta)=\pi_\theta(a_t\mid s_t)/\pi_{\theta_{old}}(a_t\mid s_t)\)，PPO-Clip 常写成 \(L^{CLIP}=\mathbb{E}_t[\min(r_tA_t,\operatorname{clip}(r_t,1-\epsilon,1+\epsilon)A_t)]\)。取 `min` 是为了在策略朝“有利方向”更新过头时采用更保守的项：当 \(A_t>0\) 时，ratio 太大不会继续增加收益；当 \(A_t<0\) 时，ratio 太小也不会让惩罚无限放大。注意这只改变 surrogate 的梯度贡献，不是直接截断 action，也不保证实际 KL 永远小于阈值。训练仍依赖相对新鲜的 on-policy rollout、正确的 old log-prob、advantage/return 的 termination 处理，以及 value clipping 或 entropy 等辅助项；\(\epsilon\) 太小会限制学习，太大则失去保护。当前 Robot Harness 的固定 candidate group、reward-shaped weighted token CE 与 PPO 的 rollout/ratio/clipped objective 不同，不能因为都出现“相对 reward”就称为 canonical online GRPO 或 PPO。

**项目挂钩**：canonical online GRPO 不能直接称为 PPO；当前 Harness 本地脚本又是 offline GRPO-style continuation，回答时要分别说明采样、objective 与 reward/checker。

**追问**：为什么 clipped objective 要取 min？

**易错**：clip ratio 不是把 action 本身截断。

**来源**：[21][45]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-027</b> · reward、return、value target 和 success predicate 如何区分？</summary>

**30 秒回答**：reward 是每一步给出的反馈或代价，return 是从当前时刻累积折扣后的回报，value target 是用来回归 value function 的某种估计目标，success predicate 则是评估器根据状态/轨迹判定任务是否成功的布尔规则。四者可能有关，但分母、时间范围和实现位置不同；尤其要区分真正 terminal、time-limit truncated，以及训练 reward 和 benchmark success。

**机制展开（约 2 分钟）**：单步奖励记为 \(r_t\)，有限时域 return 可写为 \(G_t=\sum_{k=0}^{T-t-1}\gamma^k r_{t+k}\)；value target 则可能是 Monte Carlo 的 \(G_t\)、一步 TD 的 \(r_t+\gamma(1-d_t)V(s_{t+1})\)、n-step 或 GAE-derived target，具体取法取决于算法。这里的 \(d_t\) 只应在真正终止时阻断 bootstrap；时间上限导致的 truncated 通常仍保留下一状态价值。success predicate 不是把 reward 求平均，而是由任务状态、接触条件、物体位姿、轨迹终止或脚本阈值组成的可复现实验判定，success rate 再对 episode 级布尔结果取均值并绑定分母、seed、初始化和环境版本。于是 shaped reward 可以上升而 success 不变：策略可能更快靠近目标却没有完成接触，或 reward 只覆盖代理目标；反过来 sparse success reward 也可能长期几乎不变而动作质量已改善。WAM 的 value/world auxiliary、RoboCasa 的训练/控制 reward 与 LIBERO 的 success predicate 必须分别记录 input、target、mask、reduction 和评估协议，不能把任一 proxy 直接写成任务成功率。

**项目挂钩**：WAM value head、RoboCasa reward 和 LIBERO success rate 必须分开讲。

**追问**：为什么一个任务可以 reward 上升但 success 不变？

**易错**：success rate 不是 reward 的简单平均。

**来源**：[4][10][40][42][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-028</b> · offline policy 的 distribution shift 与 extrapolation error 如何导致闭环失败？</summary>

**30 秒回答**：offline policy 只在数据分布上被监督；闭环执行中一个小动作误差就可能把状态推到训练分布之外，随后 policy 或 critic 对 OOD state-action 的估计不可靠，错误继续累积。缓解要从数据覆盖、行为约束、保守估计、recovery 数据和 matched OOD eval 入手，不能只靠把模型变大。

**机制展开（约 2 分钟）**：设行为数据来自 \(d^\beta(s)\beta(a\mid s)\)，而部署策略诱导的状态分布是 \(d^\pi(s)\)。即使单步行为克隆误差很小，只要 \(d^\pi\neq d^\beta\)，策略就会在未覆盖状态上外推；在长时序中，早期错误改变后续 observation，形成 compounding error。offline RL 还会遇到 critic 在数据外动作上的 extrapolation error：若 bootstrap 使用了不可靠的 \(Q(s',a')\)，过高估计会把策略推向 dataset support 之外。数据聚合或 intervention recovery 可以扩大状态覆盖，behavior regularization/BC constraint 与 conservative Q 可以限制危险外推，短 horizon、uncertainty/risk gate 和失败后 reset 也能缩短误差链；但每种缓解都要绑定具体 protocol，不能把“加入 recovery 数据”直接写成已解决。UWM/LIBERO 中接触精度、长时序 recovery coverage 目前只能作为候选诊断假设；升级为根因需要 raw episode trace、matched intervention、同初始化/seed 的对照和可复算的失败分层。

**项目挂钩**：接触精度和长时序 recovery coverage 只是 UWM 的候选诊断假设，需 raw episode trace 与 matched intervention 才能升级为根因。

**追问**：为什么行为克隆在短任务上可能仍然有效？

**易错**：distribution shift 不是只发生在真实机器人，仿真 closed loop 同样存在。

**来源**：[22][39][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-039</b> · 什么时候使用 impedance control、MPC 或 learned policy？</summary>

**30 秒回答**：impedance control 适合接触、插入和表面跟随，因为它规定机器人受外力后的期望刚度、阻尼和惯性；MPC 适合动力学、状态估计和约束较可信，且 solver 能在控制 deadline 内完成的场景；learned policy/VLA 更擅长从图像、语言和历史观测处理多任务变化，但依赖数据覆盖且本身不提供稳定性保证。三者通常分层组合：VLA 给 subgoal/reference/chunk，MPC 处理有限时域约束，impedance/servo 负责接触执行和安全边界。

**机制展开（约 2 分钟）**：impedance 的典型目标关系可写成 \(M_d\ddot e+D_d\dot e+K_de=F_{ext}\)，其中 \(e=x-x_d\)，\(M_d,D_d,K_d\) 分别是期望惯性、阻尼和刚度；它不是直接预测任务动作，而是塑造末端受力后的动态响应。实际使用必须说明 force/torque sensing、frame、采样周期、滤波、saturation，以及底层是 torque loop、position-based impedance 还是 admittance；“有 compliance”不等于天然安全。MPC 则在每个时刻求解 \(\min_{u_{0:H-1}}\sum_{k=0}^{H-1}\ell(x_k,u_k)+\ell_f(x_H)\)，满足 \(x_{k+1}=f(x_k,u_k)\)、\(x_k\in\mathcal X\)、\(u_k\in\mathcal U\)，通常只执行第一步或短前缀再重估。它能显式纳入 workspace、velocity、collision 或 force constraint，但受 model mismatch、state-estimation error、terminal design 和 solver deadline 约束。learned policy 可写成 \(\pi_\theta(a_t\mid o_{\le t},c)\) 或 action-chunk distribution，擅长视觉语言条件和复杂数据分布，却仍要经过 normalizer、frame/unit conversion、controller、rate limit 和 failure fallback。工程上应按风险分层：接触任务可用 policy 给目标、impedance/admittance 执行；约束可信时由 policy/world-model 给 reference，MPC 做 receding-horizon control；模型不准时缩短 horizon、提高 replan、加入 uncertainty/robust constraint 或 residual model，并保留可验证的安全控制器。不能因为 WAM/UWM 名为 world model 就直接把它当作可用于 MPC 的 calibrated dynamics model；还需要 state/action rollout contract、closed-loop error、uncertainty、constraint interface 和 deadline 证据。当前 OpenPiVLA/UWM 材料只证明 learned-policy 与 controller/action contract 的讨论，未发现个人项目接入 impedance/MPC 的实现和运行证据。

**项目挂钩**：OpenPiVLA/UWM 只支持 learned policy、world/action prediction 与 controller contract 的分析；当前证据不支持声称个人项目已部署 impedance/MPC，也不能把 WAM/UWM world model 自动等同于 MPC dynamics model。

**追问**：如果动力学模型不准，MPC 还值得用吗？

**易错**：三者不是互斥模型类别，常见答案是分层组合而不是二选一。

**来源**：[23][24][25][26][41][43]　**练习状态**：unseen

</details>

## 参考来源

1. Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762), 2017.
2. Ba et al., [Layer Normalization](https://arxiv.org/abs/1607.06450), 2016.
3. Zhang and Sennrich, [RMSNorm](https://arxiv.org/abs/1910.07467), 2019.
4. Sutton and Barto, [Reinforcement Learning: An Introduction](http://incompleteideas.net/book/the-book-2nd.html), 2nd ed.
5. Lynch and Park, [Modern Robotics, Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/).
6. PyTorch, [LayerNorm documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html).
7. PyTorch, [scaled dot-product attention documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html).
8. [OpenVLA official repository](https://github.com/openvla/openvla).
9. [Physical Intelligence openpi](https://github.com/Physical-Intelligence/openpi).
10. [LIBERO official repository](https://github.com/Lifelong-Robot-Learning/LIBERO).
11. PyTorch, [MSELoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html).
12. PyTorch, [HuberLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html).
13. PyTorch, [CrossEntropyLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html).
14. PyTorch, [KLDivLoss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.KLDivLoss.html).
15. PyTorch, [GELU documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.GELU.html).
16. PyTorch, [SiLU documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.SiLU.html).
17. Su et al., [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864), 2021.
18. Hu et al., [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685), 2021.
19. Hugging Face Transformers, [KV cache documentation](https://huggingface.co/docs/transformers/main/en/kv_cache).
20. Yu et al., [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782), 2020.
21. Schulman et al., [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347), 2017.
22. Fujimoto et al., [Off-Policy Deep Reinforcement Learning without Exploration](https://arxiv.org/abs/1812.02900), 2019.
23. Hogan, [Impedance Control: An Approach to Manipulation, Part I](https://doi.org/10.1115/1.3140702), 1985.
24. Rawlings, Mayne, Diehl, [Model Predictive Control: Theory, Computation, and Design](https://sites.engineering.ucsb.edu/~jbraw/mpc/MPC-book-2nd-edition-5th-printing.pdf).
25. Chi et al., [Diffusion Policy](https://arxiv.org/abs/2303.04137), 2023.
26. Kim et al., [OpenVLA](https://arxiv.org/abs/2406.09246), 2024.
27. Goodfellow, Bengio, Courville, [Deep Learning](https://www.deeplearningbook.org/), 2016.
28. Ioffe and Szegedy, [Batch Normalization](https://arxiv.org/abs/1502.03167), 2015.
29. PyTorch, [L1Loss documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.L1Loss.html).
30. PyTorch, [Softmax documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.Softmax.html).
31. Minka, [Divergence Measures and Message Passing](https://tminka.github.io/papers/minka-divergence.pdf), 2005.
32. Xiong et al., [On Layer Normalization in the Transformer Architecture](https://arxiv.org/abs/2002.04745), 2020.
33. PyTorch, [Automatic Mixed Precision Examples](https://docs.pytorch.org/docs/stable/notes/amp_examples.html).
34. PyTorch, [`clip_grad_norm_` documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html).
35. ROS REP-103, [Standard Units of Measure and Coordinate Conventions](https://www.ros.org/reps/rep-0103.html).
36. Åström and Murray, [Feedback Systems](https://fbsbook.org/).
37. Lynch and Park, [Modern Robotics, Chapter 5](https://modernrobotics.northwestern.edu/chapters/chapter5/).
38. Lynch and Park, [Modern Robotics, Chapter 6](https://modernrobotics.northwestern.edu/chapters/chapter6/).
39. Ross, Gordon, Bagnell, [DAgger](https://arxiv.org/abs/1011.0686), 2011.
40. Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/).
41. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html).
42. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html).
43. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html).
44. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html).
45. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html).
46. Agarwal et al., [*Deep RL at the Edge of the Statistical Precipice*](https://arxiv.org/abs/2108.13264), 2021；实现参考 [`google-research/rliable@3ccd9f4`](https://github.com/google-research/rliable/tree/3ccd9f4dea577a04d3d2b557f259aac08badbd81)。
47. Hendrycks and Gimpel, [*Gaussian Error Linear Units (GELUs)*](https://arxiv.org/abs/1606.08415), 2016。
48. Ramachandran, Zoph, Le, [*Searching for Activation Functions*](https://arxiv.org/abs/1710.05941), 2017。
49. 本地实现快照，`C:\Users\mousongzhe\Project` HEAD `6c524d9c6c6226075f100cdac395fef2fdc37671`：`wm/uwm_robocasa_transfer/uwm_robocasa_train.py`（SHA-256 `EFC53BB652302183F56B6F1BB9ACEB7ABDE31D01D953720EA1C05BB605A91FFE`）与 `wm/cosmos_policy_deepspeed_train.py`（SHA-256 `2A95D52DE64A5B46BC7C72C30B20BEC07C715FBF4FB590BF5DEA239CBA858680`）；仅支持局部 transfer/proxy 模块事实，不支持完整 upstream backbone 或性能因果归因。
50. 本地 RoPE implementation snapshot，`C:\Users\mousongzhe\Project` HEAD `6c524d9c6c6226075f100cdac395fef2fdc37671`：`wm/compat_transformer_engine/transformer_engine/pytorch/attention/__init__.py`（SHA-256 `375A646579C12E9D69EDAB96B4B01D583022407E826BDE241B6AA3C7C413AF63`）与 `scripts/muxi_write_te_torch_compat.py`（SHA-256 `7DC7994532D4EFEF72524932684756779034380E3889D72CBFCBF74A0ACCE66A`）；支持 Cosmos smoke compatibility shim 的 rotate-half、cos/sin application、layout/dimension contract，不支持完整模型频率生成、Q/K call site、Qwen3-VL exact config 或性能归因。
51. Qwen3-VL norm/residual implementation lineage：Hugging Face Transformers [`v4.57.1`（commit `8cb5963`）](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/modeling_qwen3_vl.py#L476-L519)，该文件下载内容 SHA-256 `DD63ED3B124232735B3DCA1BFA28F9D6B0D3F7182AFCB75DDE8F3E724B2B22DA`；本地 `muxi/metax_pkgs/pip-list.json`（SHA-256 `2A73054308392E14531544E471C790E8B500E449DB9442EB80C865B9197A170C`）记录 Transformers `4.57.1`，OpenPiVLA `formal_train.py`（SHA-256 `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94`）加载该模型类并只向 Q/K/V/O 注入 LoRA；Cosmos `RMSNorm` shim（SHA-256 `1D2CB070B7C9FE21438C35ED059E99C081744105482847061AEB9F2CE1F539FA`）只支持算子语义。上述证据不替代远端 runtime source/config hash，也不证明完整 Cosmos block placement 或指标因果。
52. OpenPiVLA LoRA run-contract snapshot：`formal_train.py`（SHA-256 `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94`）定义 `r=16`、`alpha=32`、`dropout=0.05`、`bias=none`、Q/K/V/O targets，并打印 `requires_grad` 参数账本；committed formal report（SHA-256 `D74126A3896F68AD44B75C7A88F1B7B9A90CB55DF0C6C6BEB90A5748E9E8E074`）记录 `trainable_params=6422528`、`total_params_seen=2133954560`（约 `0.301%`），同时说明历史目标 YAML 的 `lora: False`。该证据支持 local trainer contract/report summary，不支持 raw log 复算、adapter binary/load smoke、历史 run lineage、个人 authorship 或性能因果。
53. KV-cache official/local contract：Hugging Face Transformers [`v4.57.1` cache documentation](https://huggingface.co/docs/transformers/v4.57.1/en/kv_cache)（2026-07-22 抓取内容 SHA-256 `FCB47131204FBF721CB59014CF3E5CF1307471F1F3E2DB13579820B38436014A`）；OpenPiVLA `formal_train.py`（SHA-256 `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94`）设置训练 `use_cache=False`；OPD `point/eval_qwen_vl_raw_holdout.py`（SHA-256 `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B`）在 eval generation 同时设置 config 与 call-site `use_cache=True`；formal OPD trainer（SHA-256 `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336`）对 teacher/student full-vocab loss forward 使用 `use_cache=False`。这些证据支持代码路径区分，不支持 cache on/off 加速比、peak memory、输出 parity 或机器人闭环延迟。
54. 本地梯度稳定性实现快照：`C:\Users\mousongzhe\Project` HEAD `6c524d9c6c6226075f100cdac395fef2fdc37671` 下，OpenPiVLA `formal_train.py`（SHA-256 `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94`）实现 accumulation-boundary global clipping 与 `grad_norm` 日志；UWM/LIBERO `experiments/uwm/train.py`（SHA-256 `CFB4010A1DCA274C904295A7A937D2E1C5C3B08101A036D738F9C2B1560B4879`）和 UWM/RoboCasa `uwm_robocasa_train.py`（SHA-256 `EFC53BB652302183F56B6F1BB9ACEB7ABDE31D01D953720EA1C05BB605A91FFE`）在本地 AMP 路径先 unscale 再 clip；`C:\Users\mousongzhe\muxi` HEAD `756e27e16adcfb3ccbfe98c2920dda42095b127f` 下，formal OPD trainer（SHA-256 `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336`）检查 non-finite loss，`expert_sft.py`（SHA-256 `2A1D37F5912C91B952C529B3B80C8609D7E3105DC57BBDB2D906EA288B58EA98`）向 TrainingArguments 传入 `max_grad_norm` 并对已记录的 loss/grad_norm/lr 做 finite callback。上述证据只支持实现合同，不支持实际 run 的逐层梯度/激活轨迹、爆炸根因、跨硬件数值因果或个人逐文件 ownership。
55. 本地多目标/routing 实现边界快照：`C:\Users\mousongzhe\Project` HEAD `6c524d9c6c6226075f100cdac395fef2fdc37671` 下，official-path `wm/cosmos_policy_train_with_consolidated_online_text.py`（SHA-256 `FBE879A3AD6E3E77B258AE971480338CF41D6EC3378E29C9DE05209CF9D38DF8`）保留 official trainer/model/dataloader 并启用 online Reason1；`wm/cosmos_policy_deepspeed_train.py`（SHA-256 `2A95D52DE64A5B46BC7C72C30B20BEC07C715FBF4FB590BF5DEA239CBA858680`）自述为 MetaX-safe adapter，使用 proxy trunk/heads、sample masks 与显式加权 MSE，不能替代正式 Cosmos diffusion loss。`C:\Users\mousongzhe\muxi` HEAD `756e27e16adcfb3ccbfe98c2920dda42095b127f` 下，formal OPD `point/train_opd_online_vl.py`（SHA-256 `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336`）强制 route-homogeneous microbatch、选择单个 routed teacher，并对 weighted full-vocabulary KL 反传。上述文件与定向源码扫描未发现 per-task/route `autograd.grad`、gradient cosine 或 PCGrad 记录；该证据支持“当前未实现直接冲突测量”的代码边界，不支持实际 run 存在/不存在冲突、Pareto 改善、性能因果或个人逐文件 ownership。
