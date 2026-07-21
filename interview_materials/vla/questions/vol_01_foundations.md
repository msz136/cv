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

**机制展开（约 2 分钟）**：若 (x,y) 未归一化，点积 (x^\top y=\|x\|\|y\|\cos\theta) 会把方向和模长混在一起；这正是 attention 中 logits 既受相似方向又受 feature scale 影响的原因。余弦相似度显式除以两个范数，适合比较语义方向，但会丢掉幅值信息；欧氏距离对坐标偏移敏感，必须先确认 frame、单位和 normalization。机器人 state/action 的不同维度若量纲不统一，直接用欧氏距离会让大尺度轴支配结果；OPD 的 box/point 几何误差应使用几何合同，而不是拿语义余弦替代。

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

**答**：observation 是传感器实际读到的信息；state 是决定未来转移的系统状态；proprioception 是关节角、速度、末端位姿等本体感知，通常只是 observation/state 的一部分；action 是策略发给控制器的命令。四者要说明时间戳、单位、坐标系和维度。

**项目挂钩**：OpenPiVLA 的 observation/state normalization 不能只叫“预处理”。

**追问**：只有单帧图像时是否满足 Markov 性质？

**易错**：可观测到的信息不等于完整 state。

**来源**：[4][5][35][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-031</b> · 世界、相机、base、末端和关节坐标为什么必须区分？</summary>

**答**：同一个点或动作在不同 frame 下数值不同。视觉通常在相机 frame，导航可能在 world/base frame，操作 action 可能是末端增量或关节量；转换需要明确从哪个 frame 到哪个 frame、旋转和平移顺序、单位和轴约定。否则模型输出看似正常，执行方向仍可能整体错误。

**项目挂钩**：OPD 的图像坐标与 OpenPiVLA 的机器人 action 坐标不是同一个空间。

**追问**：相机外参和内参分别负责什么？

**易错**：坐标系命名中的上下标方向不能凭感觉解释。

**来源**：[5][35][44]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-032</b> · 齐次变换矩阵为什么能同时表示旋转和平移？</summary>

**答**：把三维点扩成 \([x,y,z,1]^\top\)，就能用 \(T=[R\ p;0\ 1]\) 的一次矩阵乘法完成旋转和平移。多个 frame 通过矩阵连乘组合，但顺序不可交换。它统一了位姿链和计算接口，也方便求逆；实现中仍要检查 column/row vector 约定。

**项目挂钩**：action contract 若混淆 world/base/end-effector frame，会出现系统性偏差。

**追问**：\(T_{ab}^{-1}\) 如何写？

**易错**：旋转矩阵不能随意当作欧拉角向量相加。

**来源**：[5][35][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-033</b> · FK 与 IK 的输入输出和难点是什么？</summary>

**答**：FK 给定关节配置，计算末端位姿，通常是确定的链式变换；IK 给定目标末端位姿，求关节配置，可能多解、无解或接近奇异。数值 IK 还受初值、关节限位和碰撞约束影响。VLA 若输出末端增量，仍需 IK/controller 才能变成关节命令。

**项目挂钩**：不要把 policy 输出的 7D action 直接说成电机 torque。

**追问**：为什么 redundant arm 的 IK 有无限多解？

**易错**：IK 成功不代表路径无碰撞或动态可行。

**来源**：[5][38][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-034</b> · Jacobian 如何连接关节速度和末端速度？奇异位形有什么影响？</summary>

**答**：局部关系是 \(\dot x=J(q)\dot q\)。Jacobian 每列描述一个关节运动对末端 twist 的贡献。接近奇异位形时 rank 降低或条件数变差，某些末端方向无法产生，伪逆会放大关节速度和噪声；常用阻尼伪逆、限速或改变姿态缓解。

**项目挂钩**：action jerk 或异常幅度可能来自模型，也可能来自 IK/Jacobian 放大。

**追问**：阻尼最小二乘为何更稳？

**易错**：奇异不是单纯数值 bug，而是机构在该姿态的可控方向退化。

**来源**：[37][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-035</b> · position、velocity、torque control 有什么区别？</summary>

**答**：position control 指定目标位置/角度，由底层回路产生控制量；velocity control 指定速度；torque control 直接控制力矩，表达力强但对动力学、安全和频率要求更高。VLA action 的 7D/14D 只是接口维度，必须说明它最终对应哪种 controller 语义。

**项目挂钩**：OpenPiVLA 的 action contract 要与 LIBERO/ALOHA controller 匹配。

**追问**：末端 delta pose 最终如何变成关节命令？

**易错**：action 维度相同不代表控制语义相同。

**来源**：[9][35][36][37][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-036</b> · PID 的 P/I/D 各解决什么问题？</summary>

**答**：P 按当前误差响应，增大后更快但可能振荡；I 累积历史误差以消除稳态偏差，但会积分饱和；D 根据误差变化率增加阻尼，但会放大高频噪声。实现还要处理采样周期、输出限幅、anti-windup 和导数滤波。

**项目挂钩**：闭环轨迹抖动不一定是模型错误，也可能是 controller 参数和延迟问题。

**追问**：为什么 D 项常对测量值而不是误差求导？

**易错**：PID 不是“调大三个系数直到效果好”。

**来源**：[36]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-037</b> · 控制频率、推理延迟和 action chunk 如何共同影响稳定性？</summary>

**答**：控制频率决定动作更新周期，推理延迟让策略使用过时 observation；chunk 可减少模型查询次数，但执行越长越接近开环。短 replan 能及时纠偏但计算和通信更贵，长 chunk 更平滑高效却容易积累误差。要同时报告 policy query rate、controller rate、horizon 和实际执行前缀。

**项目挂钩**：OpenPiVLA 的 action window 与 UWM warmup/rollout protocol 都属于闭环合同。

**追问**：延迟大于控制周期时如何设计异步 pipeline？

**易错**：模型预测 horizon 不等于控制器一次实际执行的步数。

**来源**：[9][10][25][36][41][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-038</b> · denormalization、clipping 和 gripper 维度为什么会造成系统性失败？</summary>

**答**：模型输出通常在标准化空间，推理必须用同一版本的 per-dimension 统计量恢复单位；均值/方差、轴顺序或 gripper 开闭符号错，会让每一步都产生同方向偏差。clipping 能防越界但也可能掩盖尺度错误。应做 round-trip、范围、单位和 checksum 检查。

**项目挂钩**：OpenPiVLA/UWM 的 normalizer 和 action contract 是评估前置条件。

**追问**：怎样区分模型失败与 denormalization bug？

**易错**：动作“在范围内”不代表语义和轴顺序正确。

**来源**：[9][10][35][41][43]　**练习状态**：unseen

</details>

## E. 补齐基础与研究深度

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-005</b> · 期望、方差、协方差和相关系数有什么区别？</summary>

**答**：期望描述平均位置，方差描述单变量波动，协方差描述两个变量是否一起变化，相关系数是归一化后的协方差，范围通常为 \([-1,1]\)。action 统计中要看每个维度的量纲和相关性；方差大不一定代表重要，相关性也不等于因果。

**项目挂钩**：action normalization 需要按维度统计，不能把位置、旋转和 gripper 混成一个均值方差。

**追问**：为什么协方差矩阵必须半正定？

**易错**：相关系数接近 0 只说明线性相关弱，不代表完全独立。

**来源**：[27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-007</b> · KL divergence 的方向为什么重要？</summary>

**答**：\(D_{KL}(P\|Q)\) 用 P 作期望、惩罚 Q 在 P 高概率处估计不足，常有 mode-covering 倾向；\(D_{KL}(Q\|P)\) 更容易集中到 P 的某些 mode，可能 mode-seeking。它不对称，不能当普通距离。实现时还要明确 input/target 的 log-prob 和 reduction。

**项目挂钩**：DPO、蒸馏或 policy regularization 中，KL 方向会改变策略偏离 reference 的方式。

**追问**：为什么 KL 不满足对称性和三角不等式？

**易错**：把 forward/reverse KL 名称记反，或把 KL 当作 metric。

**来源**：[14][31]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-008</b> · bias-variance trade-off 如何影响策略学习和评估？</summary>

**答**：bias 是系统性偏差，variance 是对数据/采样扰动的敏感度。模型过简单可能高 bias，过复杂或数据少可能高 variance；正则、更多覆盖和集成可调节两者。机器人评估中单个 seed 的高 success 可能是高方差，不应替代多 seed、逐任务和失败类型分析。

**项目挂钩**：UWM strict 结果和 WAM offline proxy 都要说明评估样本数与协议，而不是只报一个百分比。

**追问**：增加模型规模通常只会降低 bias 吗？

**易错**：bias-variance 不是“训练误差 vs 测试误差”的同义词。

**来源**：[4][27][42][43]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-FND-009</b> · 为什么深度网络需要非线性激活？GELU 和 SiLU 有何特点？</summary>

**答**：没有非线性时，多层线性层仍可合并成一个线性变换，无法表达复杂决策边界。GELU 用输入的平滑概率门控，Transformer 中常见；SiLU 为 \(x\sigma(x)\)，也平滑且允许小的负值。选择要结合 backbone 和已验证配置，不把激活函数单独包装成性能保证。

**项目挂钩**：Qwen3-VL 等 backbone 的激活配置属于上游事实，面试时应查 config。

**追问**：ReLU 的 dying neuron 问题如何出现？

**易错**：GELU/SiLU 的平滑不等于一定收敛更快。

**来源**：[15][16][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-014</b> · 位置编码解决什么问题？RoPE 如何提供相对位置信息？</summary>

**答**：attention 本身对 token 排列近似置换不变，需要位置编码告诉模型顺序。RoPE 将 query/key 的二维子空间按位置旋转，使二者内积自然包含相对位置差；它不是把绝对位置向量简单相加。长上下文外推还受频率、缩放和训练长度影响。

**项目挂钩**：图像 patch、语言指令和 action 序列的顺序会影响多模态策略的时序解释。

**追问**：为什么 RoPE 只旋转 Q/K，不直接旋转 V？

**易错**：位置编码不是时间同步本身，不能代替传感器 timestamp 对齐。

**来源**：[17]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-015</b> · pre-norm 和 post-norm 的训练差异是什么？</summary>

**答**：pre-norm 通常把归一化放在 attention/FFN 子层之前，残差提供更直接的梯度路径；post-norm 放在残差相加后，原始 Transformer 采用这种布局但深层训练可能更敏感。不能脱离初始化、学习率、深度和实现说某一种绝对更好。

**项目挂钩**：迁移 Qwen3-VL 或 OpenPI 时，norm 位置属于 backbone contract，不应随意改成“训练 trick”。

**追问**：为什么 pre-norm 可能造成表示尺度漂移？

**易错**：pre/post 指的是子层相对 LayerNorm 的位置，不是输入/输出层。

**来源**：[1][2][3][32]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-017</b> · LoRA 为什么能减少可训练参数？低秩假设的代价是什么？</summary>

**答**：LoRA 冻结原权重 \(W\)，只学习低秩更新 \(\Delta W=BA\)，参数量从 \(d'd\) 降到约 \(r(d+d')\)。它节省显存并便于多任务 adapter，但若任务更新不接近低秩子空间，较小 rank 会限制表达；注入层、rank、alpha、dtype 和合并方式都会影响结果。

**项目挂钩**：OpenPiVLA 的 Qwen3-VL + LoRA 可以讲训练路径，但不能把 LoRA 本身说成动作建模创新。

**追问**：为什么只在 attention projection 注入 LoRA 可能不够？

**易错**：可训练参数少不等于总推理参数少，除非做合并或特殊 serving。

**来源**：[18][41]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-FND-018</b> · KV cache 为什么能加速自回归推理？</summary>

**答**：生成第 \(t\) 个 token 时，历史 token 的 key/value 不变，可以缓存并复用；新步只计算当前 query 与缓存的 K/V，避免重复计算整段序列。代价是显存随上下文长度增长，batch、并发、量化和 cache eviction 都要考虑。对 action token 串行解码，cache 只减少重复计算，不消除每个 token 的步数。

**项目挂钩**：离散 action token 的推理延迟分析要区分 KV cache、并行 action head 和 chunk 长度。

**追问**：为什么 KV cache 对 encoder-only 模型不以同样方式使用？

**易错**：cache 加速的是历史 attention 计算，不是把模型变成并行生成。

**来源**：[19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-019</b> · 梯度消失/爆炸如何定位？</summary>

**答**：先看 loss 和 gradient norm 是否同步异常，再检查 activation/weight 分布、norm 层、初始化、学习率、混合精度 scaler、数据 outlier 和 mask 是否全零/全一。梯度爆炸可用 clipping、较小学习率或稳定 loss；消失则检查深度、激活、残差和归一化。不能只凭最终 loss 猜原因。

**项目挂钩**：跨硬件训练迁移时要区分数值库差异、数据 contract 和真正的优化不稳定。

**追问**：gradient norm 正常但 loss 不降，还要查什么？

**易错**：gradient clipping 能止血，但不能证明根因已修复。

**来源**：[1][2][33][34]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-FND-020</b> · 多任务共享 backbone 时如何判断梯度冲突？</summary>

**答**：对同一参数分别计算任务梯度，观察余弦相似度；负值说明更新方向冲突，接近零说明近似正交。可尝试 loss reweight、gradient surgery、任务分支或 stop-gradient，但要同时看各任务指标，不能只追求总 loss。mask/routing 解决样本和目标归属，不自动消除共享层的梯度冲突。

**项目挂钩**：WAM 的 action/world/value 和 OPD 的多任务输出都需要区分 mask、routing 与真正的 gradient interaction。

**追问**：为什么简单调 loss 权重不能保证 Pareto 改善？

**易错**：任务 loss 数值大小不同不等于梯度影响大小不同。

**来源**：[20][42][44]　**练习状态**：unseen

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

**答**：接触/插入任务常让 impedance 规定期望刚度与阻尼；动力学和约束可信、solver 能按 deadline 完成时用 MPC 滚动优化；高维视觉语言和任务变化大时 learned policy 更合适。三者常分层组合：VLA 给 subgoal/reference/chunk，MPC 或 impedance/controller 处理约束和执行。选择要看模型误差、接触、延迟、数据覆盖和安全 fallback。

**项目挂钩**：OpenPiVLA/UWM 只支持 learned policy 与 controller 的接口讨论；当前证据不支持声称个人项目已接入 impedance 或 MPC。

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
