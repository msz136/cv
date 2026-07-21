# VOL 03 VLA / Action：从多模态条件到可执行动作（完整卷）

> 状态：`completion_reconciled_candidate / source_audits_warn / WARN`  
> 报告日期：2026-07-19  
> 证据截止：2026-07-19  
> 完整覆盖：`VLA-ARCH-001..012`、`VLA-ACT-001..032`，共 44 题  
> 适用岗位：VLA / 具身智能算法 / 多模态机器人策略 / Robot Learning  
> 最后一批增量：补齐 RT-2/OpenVLA/Octo/π0 landscape、sequence/attention/loss mask、适配策略、异构动作、延迟与证据审计，以及 decode→controller 的执行闭环和最小单测。  
> 项目边界：OpenPiVLA 的具体 checkpoint、Qwen/π 路径、action 轴序、horizon、normalization asset、97.4% protocol 与个人贡献仍须本地 artifact 证明。

## 目录

1. [问题（Question）](#question)
2. [知识地图位置与批次边界](#section-4)
3. [VLA、VLM 与传统 visuomotor policy](#vla-vlm-visuomotor-policy)
4. [VLA 输入输出合同与时间对齐](#vla)
5. [Backbone、action expert、policy head 与 controller](#backbone-action-expert-policy-head-controller)
6. [OpenVLA：逐标量 action token 路线](#openvla-action-token)
7. [π0：连续 action expert 与 Flow Matching](#0-action-expert-flow-matching)
8. [VLA 架构路线、mask、适配与部署证据](#vla-mask)
9. [Action representation 总览](#action-representation)
10. [Normalization / denormalization](#normalization-denormalization)
11. [FAST：频域 action token](#fast-action-token)
12. [ACT：CVAE、Action Chunk 与 Temporal Ensemble](#act-cvae-action-chunk-temporal-ensemble)
13. [Diffusion Policy：条件动作扩散与 Receding Horizon](#diffusion-policy-receding-horizon)
14. [Flow Matching：CFM、OT Path、ODE 与 π0](#flow-matching-cfm-ot-path-ode-0)
15. [Action dimension、padding、mask 与 slicing](#action-dimension-padding-mask-slicing)
16. [平移、旋转、gripper 与 base action](#gripper-base-action)
17. [模型输出到 controller 与最小闭环单测](#controller)
18. [如何选择 action representation](#action-representation-2)
19. [训练与闭环推理 Pipeline](#pipeline)
20. [实现证据与 44 题覆盖](#44)
21. [OpenPiVLA 项目挂钩与真实性边界](#openpivla)
22. [Bad Case 与最小检查清单](#bad-case)
23. [后续工作](#section-108)
24. [参考文献（References）](#references)

## 问题（Question）

本卷回答一条从“模型类别”到“机器人执行”的最短闭环：

```text
# Full-volume chain: each arrow remains an auditable interface.
RGB / language / proprioception / masks / timestamps
                         ↓
       VLM backbone or visuomotor encoder
                         ↓
 scalar/FAST token / ACT CVAE / Diffusion / Flow expert
                         ↓
        decode → denormalize → valid-dim slice
                         ↓
       controller units → execute → observe again
```

面试官常以这些问题连续追问：

- VLA 相比 VLM 多了什么，为什么不能把 action token 当普通文本？
- 多视角图像、语言和 proprioception 如何进入模型，时间是谁对齐的？
- OpenVLA 与 π0 的 action output 为什么一个是 token、一个是 continuous flow？
- FAST 为什么先做 DCT，再做 BPE？token 少是否就一定更准？
- ACT 的 posterior latent 为什么训练可见 action、推理却固定 \(z=0\)？temporal ensemble 融合的究竟是哪几个预测？
- Diffusion Policy 的 \(T_o/T_p/T_a\)、diffusion steps 与真实 replan interval 为什么是五条不同时间轴？
- 训练 action dimension 与机器人执行 dimension 不同时，padding、loss mask 和 slicing 怎样证明正确？
- translation、rotation、gripper、base velocity 的单位和统计能否混在一起归一化？
- 如果 offline loss 正常但 rollout 0-success，应先查模型还是 action interface？

### 一句话总口径

> VLA 的核心不是“让 VLM 输出一个动作字符串”，而是建立从多模态观测到可执行控制量的完整策略合同：输入必须有视角、时间与 mask；输出必须有表示、shape、尺度与 axis 语义；训练目标、decode、denormalization、slicing、replan 和 controller 必须前后一致。

## 知识地图位置与批次边界

### 前置知识

- VOL 01：observation/state/action、坐标系、控制频率、Transformer、mask 与 closed loop。
- VOL 02：BC/SFT 的监督语义、token CE、连续 loss、offline proxy 与 online success。

### 完整卷做什么

| 范围 | 本批深度 | 依据 |
| --- | --- | --- |
| VLA definition / I/O | 机制级 | RT-2、OpenVLA、π0 与 frozen repos |
| OpenVLA scalar token | 公式 + code mapping | Source Audit A |
| π0 flow action expert | 公式 + paper/code convention | Source Audit B |
| FAST tokenizer | DCT/round/BPE + frozen Hub code | Source Audit B |
| ACT CVAE / chunk / temporal ensemble | 公式 + code mapping | Source Audit C |
| Diffusion Policy | epsilon/sample target、scheduler、horizon、rollout | Source Audit D |
| Flow Matching / π0 | CNF/CFM、OT path、ODE、time/sign 与 padding/debug | Source Audit E |
| RT-2 / OpenVLA / Octo / π0 landscape | backbone、action representation、training route | Source Audit F |
| sequence / mask / adaptation / latency | attention/loss、full/head/LoRA、timing decomposition | Source Audit F |
| output → controller / tests | decode、unnorm、slice、axis/unit、queue、safety | Source Audit F |
| continuous / token / CVAE / diffusion / flow taxonomy | 机制级对照 | primary papers + Source Audits |
| action semantics / normalization / valid dimensions | tensor contract + design checklist | openpi docs/code + robotics representation source |

### 仍不提前声称什么

1. ACT、Diffusion、Flow 的 upstream implementation 不证明本地 OpenPiVLA 采用相同 head、scheduler、solver 或 rollout。
2. Source Audit E 的通用 CFG example 不证明 frozen openpi Pi0 已启用 guidance。
3. 不用 openpi example config 证明本地 OpenPiVLA 的 H、D、K 或 controller。
4. 不因知识页生成就创建 mastered/pass 状态；后续题卡仍从 unseen 开始。

## VLA、VLM 与传统 visuomotor policy

### 先讲直觉

- **VLM** 回答“图里有什么、任务是什么意思”，输出通常是文本或语义表示。
- **传统 visuomotor policy** 直接把传感器观测映射到机器人动作，常为任务专用，未必继承大规模语言视觉预训练。
- **VLA** 把视觉、语言和机器人动作放进一个端到端策略合同，既利用 VLM 的语义先验，又必须输出能经过机器人接口执行的 action。

RT-2 将机器人动作表达为 text tokens，与视觉语言任务共同训练，并把这类模型称为 Vision-Language-Action model。[1] OpenVLA 延续离散 action token 路线，而 π0 让 VLM context 条件化一个连续 action expert。[2][4]

### 严谨定义

给定观测历史 \(o_{\le t}\)、任务条件 \(c\) 和可能的机器人 state/proprioception \(q_t\)，策略建模：

\[
\pi_\theta(A_t\mid o_{\le t},c,q_t),
\qquad
A_t=[a_t,\ldots,a_{t+H-1}].
\]

变量解释：\(\pi_\theta\) 是整个 policy，不只是 action head；\(A_t\in\mathbb{R}^{H\times d}\) 可以是 H 步连续动作，也可以先被编码成 token sequence。H=1 时是单步 action。实现映射：OpenVLA 原始旗舰路径实际为单图 + 语言 → 单步 d 维动作；π0 paper/openpi 支持多图、state 和 H 步 chunk。[2][3][4][6]

VLA 与 VLM 的分界不在模型名字，而在**是否存在可训练、可解码、可执行、可评估的 action contract**。如果模型只输出“move left”而没有 axis、unit、controller 和闭环执行定义，它仍是语义 planner/VLM component，不是完整低层 VLA policy。

### 面试对比表

| 维度 | VLM | 传统 visuomotor policy | VLA |
| --- | --- | --- | --- |
| 输入 | image/video + text | image/state/history | image/text/state/history 的组合 |
| 输出 | text、box、embedding | continuous/discrete robot action | token action、continuous head 或生成式 action chunk |
| 预训练 | web vision-language 常见 | task/robot data 为主 | VLM prior + robot trajectory adaptation |
| 语言泛化 | 核心能力 | 可选 | 通常是关键条件 |
| 执行合同 | 通常没有 controller action | 必须有 | 必须有，且更容易被 token/normalization 掩盖 |
| 评估 | VQA/caption/grounding | task success / control metrics | 既要语义泛化，也要 closed-loop success |

这张表是职责分类，不意味着 VLA 在任何任务上都优于小型 visuomotor policy。数据不足、延迟严格或语言无关时，较小的专用 policy 可能更合适。

## VLA 输入输出合同与时间对齐

### 输入合同

通用 VLA observation 可以写为：

\[
o_t=
\left(
\{I_{\tau_v}^{v},m_v,\tau_v\}_{v=1}^{V},
\ell,
q_{\tau_q},
h_t
\right).
\]

变量解释：\(I_{\tau_v}^{v}\) 是第 v 路相机在时间 \(\tau_v\) 的图像；\(m_v\) 是该 view 是否有效的 mask；\(\ell\) 是语言指令；\(q_{\tau_q}\) 是 proprioception；\(h_t\) 是可选历史/记忆。直觉是“多模态输入”不只是拼字段，还必须说明每个字段何时采样、是否缺失。openpi model boundary 接收已经对齐和 resize 的 arrays；时间同步通常应在数据转换或环境 wrapper 完成，不能假设 Transformer 自动修正 timestamp mismatch。[6][12]

最小字段表：

| 字段 | 必须说明 | 常见失败 |
| --- | --- | --- |
| image/view | camera name、shape、颜色空间、resize/crop/flip、mask | 训练/推理视角或翻转不一致 |
| language | instruction 来源、模板、tokenizer、截断长度 | prompt 模板改变 action positions |
| proprio | axis order、unit、frame、timestamp、normalization | 位置/速度混淆；state 与图像错帧 |
| history | window、stride、padding、causal rule | history 泄漏未来或顺序颠倒 |
| action target | type、H、d、control frequency、absolute/delta | label 与执行频率不匹配 |
| dataset identity | norm stats key、embodiment/control mode | 使用错误 checkpoint assets |

### 时间对齐

若以 control tick \(t_k\) 为监督锚点，可定义：

\[
I_k^v=I^v_{\arg\min_{\tau}|\,\tau-t_k\,|},
\quad
q_k=\operatorname{interp}(q,t_k),
\quad
A_k=[a(t_k),a(t_k+\Delta t),\ldots,a(t_k+(H-1)\Delta t)].
\]

变量解释：图像可用 nearest timestamp，连续 proprio 可插值，action label 按控制周期 \(\Delta t\) 构造 H 步窗口。该式是通用数据设计合同，不是对 OpenVLA/openpi 某个未读 converter 的事实声明。实现中应记录最大时间差阈值、缺帧 mask 和 episode 边界；窗口越界时不可把下一 episode 的动作拼进来。

### 两个已核实的具体实例

- OpenVLA frozen flagship：`image_primary[0]` + language + `action[0]`；默认 `load_proprio=False`、`window_size=1`、`future_action_window_size=0`，即单图、无 proprio/history、单步动作。[2][3][12]
- π0/openpi：论文为 2–3 张图 + language + proprio，H=50；frozen Pi0Config 默认有三个 image slots、state [B,32]、actions [B,50,32]，但 config 可覆盖。[4][6][12]

## Backbone、action expert、policy head 与 controller

### 职责不能混写

| 组件 | 主要输入 | 主要输出 | 负责什么 | 不负责什么 |
| --- | --- | --- | --- | --- |
| vision encoder / VLM backbone | image + language | contextual tokens | 视觉语义、语言条件与预训练知识 | 不自动定义机器人 axis/unit |
| projector / modality adapter | visual/state features | shared-width tokens | 对齐 embedding space | 不等于完整 action policy |
| action tokenizer | continuous action / chunk | token IDs 或 inverse | 非参数化/轻量表示转换 | 不负责 closed-loop control |
| policy head | context embedding | action logits/continuous params | 直接预测 action distribution | 不一定能表达复杂多模态 |
| action expert | context + noisy/latent action | velocity/noise/action | 独立建模 robot-specific action | 仍需要 normalizer 与 controller |
| output transform | model output | dataset action | decode、denorm、slice、axis conversion | 不学习环境 dynamics |
| controller | dataset/env action | actuator command | position/velocity/torque loop、安全限制 | 不解释任务语言 |

OpenVLA 没有独立 continuous action head：Llama LM head 预测 tail-vocabulary action tokens，ActionTokenizer 做 scalar ↔ token 映射。[2][3][12] π0 则以 VLM prefix 条件化 300M action expert，expert 输出 H×D flow velocity，再由 solver 得到连续 chunk。[4][6][12]

### Policy 是整条链

\[
\pi_{\mathrm{exec}}
=
\mathcal{C}
\circ\mathcal{S}
\circ\mathcal{U}
\circ\mathcal{D}
\circ f_\theta
\circ\mathcal{P},
\]

变量解释：\(\mathcal{P}\) 是输入 preprocess/normalize，\(f_\theta\) 是模型，\(\mathcal{D}\) 是 token/flow decode，\(\mathcal{U}\) 是 unnormalize，\(\mathcal{S}\) 是有效维度与 axis 选择，\(\mathcal{C}\) 是 controller。直觉是任何一个函数错，closed-loop policy 都会错；只验证 \(f_\theta\) 的 loss 不能证明 \(\pi_{\mathrm{exec}}\) 正确。openpi Policy.infer 的 transform 顺序直接体现了这一组合。[6][12]

## OpenVLA：逐标量 action token 路线

### 架构与 I/O

OpenVLA flagship 基于 Prismatic 7B：视觉侧融合 DINOv2 与 SigLIP patch features，经 projector 输入 Llama-2 7B；LM head 自回归生成动作 token。[2][3][12]

```text
# OpenVLA flagship path at the audited commit.
one primary RGB + task prompt
        ↓
DINOv2/SigLIP features → projector → Llama-2
        ↓
d tail-vocabulary token IDs
        ↓
scalar centers → dataset q01/q99 unnormalize
        ↓
one d-dimensional action
```

注意：生成 d 个 token 表示“一个动作的 d 个维度”，不是 H=d 的未来时间窗口。frozen dataset default 的 `future_action_window_size=0` 与论文把 action chunking 列为未来方向相一致。[2][3][12]

### q01/q99 normalization

对真实 action 第 i 维：

\[
\tilde a_i=
\operatorname{clip}
\left(
2\frac{a_i-q_i^{01}}{q_i^{99}-q_i^{01}+\varepsilon}-1,
-1,1
\right).
\]

变量解释：\(q_i^{01},q_i^{99}\) 是当前 dataset/embodiment 的分位统计；\(\tilde a_i\) 进入 scalar tokenizer。OpenVLA frozen preprocessing 对受 mask 管理的维度显式 clip 到 [-1,1]。直觉是压缩 outlier 影响；代价是超出区间的不同物理动作可能饱和到同一 endpoint。[3][12]

### scalar → token

frozen code 构造 256 个均匀 threshold/edge values（论文则抽象为 256 bins）：

\[
e_j=-1+\frac{2j}{255},\quad j=0,\ldots,255,
\qquad
t_i=V-\operatorname{digitize}(\tilde a_i,e).
\]

变量解释：V 是 base tokenizer vocabulary size；`np.digitize` 在 clip 后返回 \(b_i\in\{1,\ldots,256\}\)，所以 \(t_i=V-b_i\) 恰好占用末尾 256 个 token IDs。直觉是把每个 normalized scalar 变成 LLM 可预测的“词”。实现风险是 token offset、special-token collision 和 tokenizer version；不能只看输出 ID 在词表范围内。[3][12]

frozen decoder 使用 255 个相邻 endpoint center：

\[
c_j=\frac{e_j+e_{j+1}}{2},\quad j=0,\ldots,254,
\qquad
\hat{\tilde a}_i=c_{\operatorname{clip}(V-t_i-1,0,254)}.
\]

变量解释：论文写 256-way bins、索引 0..255；该 commit 实际用 256 个 thresholds 编码、255 个相邻 centers 解码。编码的 \(b=255\) 与 \(b=256\) 都被 clip 到 center index 254，因此两个最高 token IDs 重建为同一个 \(0.996078\ldots\) center。面试中应把 paper abstraction、encoder token count 与 decoder reconstruction cardinality 分层说明。[2][3][12]

### masked token CE

\[
\mathcal L_{\mathrm{OpenVLA}}
=-\frac{\sum_k m_k\log p_\theta(y_k\mid y_{<k},I)}
{\sum_k m_k}.
\]

变量解释：\(m_k\) 只让 action tail 和配置允许的 stop/EOS label 参加 loss；prompt 与插入的 image patch positions 使用 IGNORE_INDEX。连续 L1 是 argmax token decode 后的 metric，不是优化目标，也不等于 online success。[3][12]

### quantization 的三类代价

1. **Resolution**：有限 centers 带来不可消除的 reconstruction error。
2. **Saturation**：q01/q99 外被 clip 后失去幅度差异。
3. **Distribution shift**：换 robot/dataset 却沿用旧 stats，会让相同 token 对应错误物理尺度。

## π0：连续 action expert 与 Flow Matching

### I/O 与架构

π0 paper 定义：

\[
o_t=[I_t^1,\ldots,I_t^n,\ell_t,q_t],
\qquad
A_t=[a_t,\ldots,a_{t+H-1}]\in\mathbb{R}^{H\times D}.
\]

变量解释：论文实验用 2–3 路 RGB、language、joint state，H=50；frozen openpi 默认 D=32、H=50。D 是 model action dimension，不代表每个 robot 都有 32 个真实 actuator dimensions。[4][6][12]

VLM 产生 image/language prefix；π0 的 suffix 含一个 continuous state token 与 H 个 noisy-action tokens。action expert 输出每个 noisy-action token 的 D 维 velocity。采样时 prefix KV cache 只算一次，每个 integration step 重算 suffix。[6][12]

### paper convention

\[
A^\tau=\tau A+(1-\tau)\epsilon,
\qquad
u_{\mathrm{paper}}=A-\epsilon,
\quad \epsilon\sim\mathcal N(0,I).
\]

变量解释：\(\tau=0\) 是 noise、\(\tau=1\) 是 data；网络学习沿直线路径的 velocity。训练目标是 \(v_\theta(A^\tau,o)\) 与 \(A-\epsilon\) 的 MSE，作用张量为 [B,H,D]。[4]

\[
\mathcal L_{\mathrm{flow}}
=
\mathbb E\left[
\frac{1}{HD}
\left\|v_\theta(A^\tau,o)-(A-\epsilon)\right\|_2^2
\right].
\]

变量解释：frozen compute_loss 先对 D 求 mean，train.py 再对 H 和 batch 求 mean；公开主路径未显示额外 valid-dimension mask。若某个本地项目 D 大于真实 d，是否对 padding dimensions 监督为零或使用 mask，必须读本地 batch/loss，而不能由 output slicing 反推。[6][12]

### code convention

openpi 反向参数化时间：

\[
x_t=t\epsilon+(1-t)A,
\qquad
u_{\mathrm{code}}=\epsilon-A.
\]

变量解释：代码从 t=1 noise 以 \(dt=-1/N\) 积分到 t=0 data，默认 N=10。令 \(\tau=1-t\)，则 path point 相同，且 \(u_{\mathrm{code}}=-u_{\mathrm{paper}}\)、\(d\tau=-dt\)，所以最终 ODE 轨迹等价。[6][12]

### π0.5 不等于 Pi0FAST

> 2026-07-19 [Audit B 独立复核](../sources/vol_03_pi0_fast_openpi_independent_fact_review.html) 已直接核对 π0.5 paper 的 FAST-pretrain/flow-posttrain hybrid、frozen `Pi0(pi05=True)` 与 `Pi0FAST` 分叉；FAST Hub normalization、model default 与 `pi0_fast_libero` 的 D=7/H=10 override 也已分层。local OpenPiVLA 仍需 artifact，相关题卡保持 `unseen/WARN`。

π0.5 paper 的完整 recipe 在预训练用 FAST action-token CE，post-training 加连续 action expert，并联合优化 CE + flow loss；推理使用 text token 后接 10 步 flow sampling。[5] frozen openpi 的 `Pi0(pi05=True)` 直接证实 state 进入离散 prompt、timestep 用 adaRMSNorm 注入，但审计的 `compute_loss` 只返回 flow MSE。独立 `Pi0FAST` class 才实现 FAST-token CE。[6][12]

因此：

- π0.5 paper = hybrid training design；
- frozen Pi0(pi05=True) = released flow architecture path；
- Pi0FAST = independent autoregressive FAST model type。

三者不能只按名称合并。

## VLA 架构路线、mask、适配与部署证据

> 本节对应 `VLA-ARCH-007..012`。四方法比较、Octo frozen code 与 openpi serving path 来自 [Source Audit F](../sources/vol_03_architecture_execution_claim_to_code.html)，并已完成 [独立事实复核](../sources/vol_03_architecture_execution_independent_fact_review.html)；比较机制，不横比不同 protocol 的 success rate。[19][20][21][27]

### VLA-ARCH-007：RT-2、OpenVLA、Octo、π0 不是同一 head 的尺寸变化

**直觉**：四者都从视觉/任务条件产生机器人动作，但“动作放在哪里、用什么 loss 学、推理要循环什么”完全不同。先说 action representation，再谈 backbone size，能避免只背模型名称。

| 方法 | backbone / condition | action representation | 训练主路线 | 推理循环 |
| --- | --- | --- | --- | --- |
| RT-2 | PaLI-X 5B/55B 或 PaLM-E 12B | pose/gripper 等连续维 uniform 256 bins 后成为 action tokens，另有 termination | 预训练 VLM 上混合 web + robot data co-fine-tune | 自回归生成 action token；论文部署用 cloud TPU |
| OpenVLA | DINOv2 + SigLIP → projector → Llama-2 7B | 当前动作每个 scalar 占一个 tail-vocab token | OXE robot data 上 full fine-tune；official repo 另支持 LoRA | 生成 (d) 个 token → scalar decode → q01/q99 unnorm |
| Octo | 27M/93M block-wise transformer；image tokenizer + frozen T5-base | action readout latent 条件化 diffusion head，公开 pretrain config 为 H=4、D=7 | 800k OXE trajectories 预训练；新域 head-only/head-MLP-only/full FT | backbone 一次产生 readout；diffusion head 多步去噪 chunk |
| π0 | PaliGemma 2B VLM + 约 300M action expert | (H\times D) noisy continuous chunk 的 flow velocity | cross-embodiment pretrain + task post-train；openpi 提供 full/LoRA 示例 | prefix KV 一次；expert 做多步 Euler/ODE update |

RT-2 的论文 tokenization 还随 VLM 而变：PaLI-X 复用整数 token，PaLM-E 覆写 256 个低频 token。OpenVLA 的 frozen implementation 则使用 Llama tail vocab 和特定 255-center decode nuance。它们同属“action as token”范式，但不能交换 tokenizer 细节。[1][2][3][21]

**回答收口**：RT-2 强调 web knowledge co-fine-tuning 与 action-as-text；OpenVLA 将这条路线开放到 7B/OXE；Octo 用小型 modular transformer/readout/diffusion 做可适配 generalist policy；π0 用大 VLM context + 小 continuous expert 做 flow chunk。项目选型要再看 data、latency、H/K 与 controller，而不是把年份当排序。

### VLA-ARCH-008：attention-visible 与 loss-visible 是两件事

**直觉**：token 在序列里出现，只说明它可能参与计算；是否能看见别的位置由 attention mask 决定，是否直接产生监督由 label/loss mask 决定。

对自回归 action-token 路线：

\[
\mathcal L_{\mathrm{AR}}
=-\frac{\sum_i m_i\log p_\theta(y_i\mid y_{<i},c)}
{\sum_i m_i+\epsilon}.
\]

变量与实现：(y_i) 是 token，(c) 是图像/任务条件，(m_i) 是 label mask。OpenVLA prompt labels 与插入的 visual patch labels 是 `IGNORE_INDEX`，action tail 与默认 stop token 才参加 CE；因而“patch 被 action token attend”与“patch 自己有 CE label”完全不同。[2][3][21]

三种典型 layout：

```text
# OpenVLA: action values themselves are autoregressive labels.
[image patches / prompt] -> [a_1] [a_2] ... [a_d] [EOS?]

# Octo: readout tokens are latent queries; a separate diffusion loss supervises actions.
[task prefix] [obs(t-1), readout(t-1)] [obs(t), readout(t)] -> H x D

# pi0: prefix conditions a continuous noisy-action suffix under a block mask.
[image + language prefix] [state + noisy action_1 ... noisy action_H] -> velocity
```

代码块说明：Octo readout 只读取 task/observation/自身 readout，不被 observation 反向读取；π0 action suffix 是连续 latent，不是 LM action label。位置改变会影响 positional embedding、causal context、KV cache 与 loss alignment；一次 off-by-one 就可能把 prompt/EOS 当 action，或让 action 看见未来 label。[6][20][21]

Octo 的 timestep/action target mask 是正例：

\[
M_{b,w,h,d}=T_{b,w}\land A_{b,w,h,d},
\qquad
\mathcal L=\operatorname{continuous\_loss}(\hat z,z;M).
\]

变量与实现：(T) 排除 history padding，(A) 排除 action padding；(b,w,h,d) 是 batch/window/horizon/action dimension。frozen MSE 与 diffusion head 都使用 conjunction。[20] 相比之下，frozen Pi0 flow loss 对 configured D 全维 mean；不能泛称“所有 VLA 都自动 mask padding”。[18][21]

### VLA-ARCH-009：freeze、full、LoRA 与独立 expert 的选择

**直觉**：这不是四个互斥模型名，而是“允许哪些参数适应新数据”的容量预算。数据少、domain 接近时先限制更新；camera/objects/dynamics 变化大时才逐步解冻。

| 方式 | 主要更新 | 合适情形 | 风险 |
| --- | --- | --- | --- |
| freeze VLM / head-only | projector/readout/action head | 新 action space、小数据、视觉语义接近 | backbone domain gap 无法纠正 |
| full FT | vision/projector/LLM/action modules | 数据足、视觉与控制都明显变化 | 显存高、遗忘、过拟合 |
| LoRA / adapter | selected linear layers 的低秩增量 | 需要更多容量但显存有限 | rank/target modules 与 base revision 约束能力 |
| independent action expert | 大 VLM 提供 context，小 expert 专门建模 action | continuous chunk、需要独立 target/width | context/expert interface 与联合训练更复杂 |

LoRA 可写为：

\[
W'=W+\frac{\alpha}{r}BA,
\quad
A\in\mathbb R^{r\times i},\;B\in\mathbb R^{o\times r},
\quad r\ll\min(i,o).
\]

变量与实现：(W) 是 frozen base weight，(r) 是 rank。OpenVLA official finetune 使用 PEFT `all-linear` LoRA；openpi LIBERO low-memory config 同时选择 PaliGemma/action-expert LoRA variant 和匹配 freeze filter；Octo 则明确提供 `head_only`、`head_mlp_only`、`full`。[2][7][20][21]

**证据边界**：OpenVLA flagship 论文结果来自 full fine-tuning；repo 支持 LoRA 不代表主结果或本地 checkpoint 使用 LoRA。项目回答必须补 trainable-parameter log、base/adapter revisions、rank、target modules、merge/load order。

### VLA-ARCH-010：异构动作要统一 schema，也要统一监督语义

令 embodiment \(e\) 的真实动作宽度为 \(d_e\)，模型宽度为 \(D\ge d_e\)，\(P_e\) 把真实维写进统一空间，\(S_e=P_e^\top\) 取回：

\[
\bar a^{(e)}=P_e a^{(e)},
\qquad
\hat a^{(e)}=S_e\hat{\bar a},
\qquad
m^{(e)}_j=\mathbf{1}\!\left[j\in\operatorname{Im}(P_e)\right].
\]

变量与实现：\(P_e\) 只定义维度位置，不会自动统一 absolute/delta、frame、unit、rotation 或 gripper polarity。openpi `PadStatesAndActions` 只做 zero-pad；Octo `action_pad_mask` 则是 loss 中的显式有效维正例。[7][20][21]

masked objective：

\[
\mathcal L_{\mathrm{valid}}
=
\frac{
\sum_{b,h,j}m_{b,h,j}\,
\ell\!\left(\hat{\bar a}_{b,h,j},\bar a_{b,h,j}\right)
}{
\sum_{b,h,j}m_{b,h,j}+\varepsilon
}.
\]

变量与实现：\(m\) 应覆盖 timestep 与 action dimension；若直接对 \(D\) 维 mean，padding zeros 也会产生“逼近 0”的监督，并把有效维梯度按 \(d_e/D\) 稀释或改变。推理 slice 并不能修复训练 target 已被污染的问题。[18][20][21]

跨机器人至少逐组记录：translation axis/frame/unit/type，rotation representation/order/unit，gripper range/polarity，base semantics，control frequency/dt，以及 modality/timestep/action masks。只写“统一成 32D”不是 action unification 设计。

### VLA-ARCH-011：延迟是 pipeline 向量，不是一个数字

远程 chunk query 的端到端时间可拆为：

\[
T_{\mathrm{e2e}}=
T_{\mathrm{capture}}+T_{\mathrm{pre}}+T_{\uparrow}
+T_{\mathrm{vision/prefill}}+N T_{\mathrm{step}}
+T_{\mathrm{post}}+T_{\downarrow}+T_{\mathrm{queue}}.
\]

变量与实现：token policy 的 (N) 是 action token length；FAST 是可变压缩序列长度；diffusion/flow 是 denoise/NFE steps。是否缓存 vision/prefix、每 step 跑大 backbone 还是小 expert，必须看源码。[12][21]

- RT-2 论文在其 multi-TPU cloud protocol 下报告 55B 为 1–3 Hz、5B 约 5 Hz；这包含历史网络/服务条件，不能外推本地 GPU。[1]
- FAST 论文的指定 4090 测量中，π0 flow 约 100 ms/chunk、π0-FAST 约 750 ms/chunk；Source Audit B 将差异映射到 10 次小 expert 与 30–60 次大 VLM token decode。[7][12]
- openpi `Policy.infer` 的 `policy_timing.infer_ms` 包围 model sampling；server `infer_ms` 包围完整 policy infer，`prev_total_ms` 才进一步覆盖上一轮 recv/unpack/send。它们仍未拆出 vision、每步 sampler 和 queue。[6][21]

测量时报告 warm-up、device sync、batch/dtype、payload bytes、H/K、NFE/token length、cache、p50/p95；在异步 GPU 上直接用未同步 wall clock 会低估 kernel 时间。

### VLA-ARCH-012：从 paper 一直核到 runtime trace

**直觉**：模型名是线索，不是合同。真实 I/O 需要四层证据闭环：

```text
# Each layer answers a different question; none may be skipped.
paper/version
  -> repo commit + license + model/loss/infer path
  -> checkpoint manifest + config + tokenizer + norm assets
  -> runtime request/response + transforms + queue + controller trace
```

代码块说明：paper 支持方法定义；repo 支持该 commit 的实现；checkpoint 决定实际权重/资产；runtime 才证明线上收发、denorm、轴序和执行。

openpi `create_trained_policy` 展示了正确的资产绑定：从 checkpoint 加载 model weight，norm stats 默认取 checkpoint `assets/<asset_id>`；input 依次做 repack/data transform、normalize、model transform；output 依次做 model transform、unnormalize、data/repack transform。[6][21] OpenVLA 的 `unnorm_key` 同样决定 action dim 和 q01/q99；多 dataset stats 不显式选 key 会拒绝推理。[2][3]

最小 manifest 应有：paper/repo revision、model class、weight hash/shape、base+adapter、tokenizer/processor revision、image views/resize、state/action schema、H/D/K、norm asset/hash、sampler/NFE、output transform、controller mode/frequency、eval checkpoint/task/trial/seed。对 OpenPiVLA，这些仍是待取证项，不能由上游 Source Audit F 自动补齐。

## Action representation 总览

### 五条路线各自建模什么

| 路线 | 抽象分布/目标 | 优点倾向 | 主要风险 | 本批证据深度 |
| --- | --- | --- | --- | --- |
| deterministic continuous regression | \(\hat A=f_\theta(o)\)，MSE/Huber | 简单、低 decode latency | 多模态 label 下均值化 | 通用机制 |
| scalar discrete token | \(p(y_{1:d}\mid o)\) | 复用 LM next-token infra | 量化、offset、AR latency | OpenVLA 深入 |
| CVAE action chunk | \(p(A\mid o)=\int p(A\mid o,z)p(z\mid o)dz\) | latent 表达 sequence variation | posterior collapse、train/infer latent gap | ACT paper/code 深入 |
| diffusion action | conditional denoising / score | 适合多峰、高维 continuous action | 多步 sampling、scheduler contract | Diffusion Policy paper/code 深入 |
| flow action | conditional velocity field + ODE | 连续多模态、solver 明确 | time convention、integration latency | π0 特化深入 |

表中“优点倾向”不是跨 benchmark 排名。数据、网络规模、H、controller frequency 和 implementation 都会改变结果。

### deterministic regression

\[
\mathcal L_{\mathrm{reg}}
=
\mathbb E_{(o,A)\sim\mathcal D}
\left[
\|f_\theta(o)-A\|_2^2
\right].
\]

变量解释：若同一个 o 在数据中对应左右绕行等多个可行动作，MSE 的条件最优解倾向于条件均值，可能生成物理上不属于任何 mode 的动作。若任务近似单峰、action 定义稳定且延迟严格，direct regression 仍是重要 baseline。

### CVAE 定义级边界

\[
\mathcal L_{\mathrm{CVAE}}
=
\mathbb E_{q_\phi(z\mid o,A)}
\left[-\log p_\theta(A\mid o,z)\right]
+
\beta D_{\mathrm{KL}}
\left(q_\phi(z\mid o,A)\,\|\,p(z\mid o)\right).
\]

变量解释：z 是 sequence/style latent；训练 encoder 可看见 action target，推理只能从 prior 采样或取固定 latent。冻结 ACT path 具体采用 `[CLS]+qpos+actions` posterior、learned action queries，并在推理固定 \(z=0\)；详见后续 ACT 小节。[9][14]

### diffusion 定义级边界

Diffusion Policy 将 visuomotor policy 表示为 conditional denoising diffusion process，并强调 multimodal action distribution、visual conditioning 与 receding-horizon control。[10] Batch 2A 后续小节展开 frozen epsilon/sample target、global condition、DDPM/DDIM 与 \(T_o/T_p/T_a\)。

### flow 与 diffusion 不只是“步数不同”

- diffusion 常学习 noise、score 或 data parameterization，并依赖 noise schedule 与 stochastic/deterministic sampler；
- flow matching 学给定 probability path 的 velocity field，通过 ODE solver transport noise 到 data；
- 两者都可迭代生成 continuous chunk，但训练 target、time convention 与 solver 不同。

本页后续 Flow Matching 小节从 Source Audit E 回填一般 CNF/CFM、OT path、ODE 与 π0 特化；仍不把 current supporting package 冒充 2022 论文历史实现。

## Normalization / denormalization

### 为什么它是 0-success 高风险接口

神经网络只在 normalized space 学习；controller 在 physical units 执行。若训练与推理的 stats key、axis order 或 action type 不一致，模型可在 normalized space 得到很低 loss，却输出错误量级或错误轴的物理动作。

openpi 的 quantile mapping 为：

\[
\tilde a_i=
2\frac{a_i-q_i^{01}}
{q_i^{99}-q_i^{01}+\varepsilon}-1,
\qquad
a_i=
\frac{\tilde a_i+1}{2}
\left(q_i^{99}-q_i^{01}+\varepsilon\right)+q_i^{01}.
\]

变量解释：该 frozen transform 不显式 clip；因此 q01/q99 外值可落在 [-1,1] 之外。Policy factory 从 checkpoint assets 加载训练期 norm stats，输入 sample 前 normalize，output transform 后 unnormalize。[6][12]

OpenVLA 与 openpi 的差别：

| 维度 | OpenVLA audited path | openpi audited path |
| --- | --- | --- |
| stats | dataset-specific q01/q99 | checkpoint asset norm stats |
| quantile mapping | 对受管维度 clip [-1,1] | quantile transform 无显式 clip |
| tokenization | normalize 后 scalar bin | flow 直接用 continuous normalized；FAST 再 DCT/BPE |
| inverse | token center 后 q01/q99 inverse | model output transform 后 inverse |
| extra padded dims | dataset-specific | stats 未覆盖的尾维保持原值，再 output slice |

### 最小 inverse-consistency test

\[
\max_{a\in\mathcal T}
\left\|
\operatorname{unnorm}(\operatorname{norm}(a))-a
\right\|_\infty
<\delta.
\]

变量解释：\(\mathcal T\) 至少包含训练分位内样本、q01/q99 endpoint、outlier、constant dimension 与 padding dimension；\(\delta\) 按物理单位设定。对于有 clip 的 pipeline，outlier 不应期待严格可逆，而应显式测试 saturation behavior。

### 常见穿帮说法

- 错：“归一化只是数值稳定性，不影响策略语义。”
- 对：“归一化 stats 与 axis order 共同定义 token/continuous output 的物理意义，是 checkpoint contract。”
- 错：“FAST 会自动把任何机器人 action 处理到统一尺度。”
- 对：“FAST Hub processor 从 DCT 开始；调用者先做 dataset/embodiment normalization。”

## FAST：频域 action token

> FAST 的 quantile normalization、DCT/round/BPE 顺序、paper vocab=1024 与 Hub vocab=2048、以及 processor 不自动做 normalization，已在 [Audit B 独立复核](../sources/vol_03_pi0_fast_openpi_independent_fact_review.html) 直接核对；这里的上游默认值不等于本地 tokenizer revision。

### 它解决什么

逐 timestep、逐 scalar tokenization 会让高频 action window 产生大量相邻高度相关 token；autoregressive model 可能靠复制最近 token 获得低 loss，而没有学到整段动作形状。FAST 先把时间序列变到频域，让低频整体趋势先出现，再用 BPE 压缩重复系数。[7][8]

### 算法

对 normalized action chunk \(\tilde A\in\mathbb{R}^{H\times D}\)，每维沿时间轴做 DCT：

\[
C_j^i=\operatorname{DCT}(\tilde a_{1:H}^i),
\qquad
\bar C_j^i=\operatorname{round}(\gamma C_j^i).
\]

变量解释：i 是 action dimension，j 是 frequency index，\(\gamma\) 控制量化精度/压缩率。FAST paper 单数据集实验使用 scale 10；frozen FAST+ Hub processor 也使用 scale 10。[7][8][12]

按 frequency-first 展开并做 BPE：

\[
z=[
\bar C_0^1,\ldots,\bar C_0^D,
\bar C_1^1,\ldots,\bar C_1^D,\ldots],
\qquad
y_{1:L}=\operatorname{BPE}_{\Phi}(z).
\]

变量解释：先排所有维度的低频 coefficient，再进入高频；L 是可变 token length；\(\Phi\) 是唯一 learned 的 BPE vocabulary。frozen Hub code 对 [H,D] 的 DCT array 做 row-major flatten，正好得到 frequency-first 顺序。[7][8][12]

inverse decode：

\[
\hat{\tilde A}
=
\operatorname{IDCT}\!\left(
\frac{
\operatorname{unflatten}\!\left(
\operatorname{BPE}^{-1}(y;\Phi);H,D
\right)
}{\gamma}
\right).
\]

变量解释：decode 恢复 normalized H×D chunk，之后仍需 checkpoint-matched unnormalize。Hub decoder 需要 H 与 D；reshape 失败时 frozen code 会返回 zero coefficients，因此部署应增加显式 error/telemetry，而不是静默执行零动作。[8][12]

### paper / artifact / model 的默认值要分开

| 对象 | scale | vocab | H / D |
| --- | ---: | ---: | --- |
| FAST paper 单数据集实验 | 10 | 1024 | 1-second chunk，依 control frequency |
| frozen FAST+ Hub | 10 | 2048 | decode 时传入或缓存 |
| openpi Pi0FASTConfig default | external | external | H=32, D=32 |
| openpi LIBERO example config | external | external | H=10, D=7 |

不能用最后一行证明本地 OpenPiVLA H=10。

### compression 为什么不等于控制误差更小

至少分开五个量：

1. token count / compression ratio；
2. normalized reconstruction error；
3. next-token training loss；
4. physical-unit trajectory error；
5. closed-loop task success。

BPE 减少重复 zero tokens、缩短 AR sequence，论文消融在其任务上提升 policy performance；但更短 token sequence 不在数学上保证更小 reconstruction error，更不保证跨 controller 的 success 提升。[7]

## ACT：CVAE、Action Chunk 与 Temporal Ensemble

> 本节对应 `VLA-ACT-011..017`。直接证据来自 ACT arXiv v1 与 `tonyzhaozh/act@742c753...`；它是 continuous action-chunk CVAE，不是 action-token VLA，也不能证明个人 OpenPiVLA 使用 ACT head。[9][14]

### VLA-ACT-011：H、K、R 与 control period

先把四个时间量拆开：

| 量 | 记号 | 回答什么 | frozen ACT |
| --- | --- | --- | --- |
| prediction horizon / chunk size | \(H\) | 一次 forward 输出几步 | `num_queries` |
| execution window | \(K\) | 一个预测 chunk 实际连续执行几步 | 无独立 CLI field |
| query / replan interval | \(R\) | 相邻两次 policy inference 间隔几步 | `query_frequency` |
| control period | \(\Delta t\) | 每个环境 action 的物理周期 | sim `DT=0.02` |

若 episode 有 \(T\) 个 control steps，无 temporal aggregation 且 \(K=R=H\)，policy query 数近似：

\[
N_{\mathrm{query}}\approx\left\lceil\frac{T}{H}\right\rceil.
\]

变量与实现：\(H\) 是 model tensor 的时间维；\(K/R\) 属于 rollout。冻结 ACT 的无 aggregation 分支每 \(H\) 步 query 一次并消费整段；开启 aggregation 后 \(R=K=1\)，但 model \(H\) 不变。[14]

概念上 \(K\) 与 \(R\) 仍可不同：异步 controller 可先提交较长 queue，却在 queue 未耗尽前生成新计划。不能只看到 `chunk_size=100` 就说“100 步后才闭环”。

### VLA-ACT-012：CVAE-Transformer 如何并行输出 chunk

训练期 posterior encoder 与 decoder 的数据流：

```text
# The posterior sees proprioception and the supervised action chunk.
[CLS] + projected qpos + projected actions[0:H]
                 |
       Transformer encoder
                 |
          mu, logvar [B,32]
                 |
       reparameterized z [B,32]

# The decoder consumes current observation and H learned query slots.
shared multi-camera ResNet + qpos token + z token
                 |
       Transformer encoder/decoder
                 |
       H learned action queries
                 |
          actions [B,H,14]
```

代码映射：posterior 不看图像，使用 `[CLS]+qpos+actions`；相机共享 ResNet18，feature maps 沿 spatial width 拼接；decoder 的 `nn.Embedding(num_queries, hidden_dim)` 是 \(H\) 个 learned output slots，一次 forward 并行得到：

\[
\operatorname{ACT}_\theta(o_t,z)
=
\left(
\hat a_t^{(t)},\ldots,\hat a_{t+H-1}^{(t)}
\right)
\in\mathbb R^{H\times14}.
\]

变量说明：上标 \((t)\) 是 query time，下标是目标物理时刻；14D 是该双臂 setup 的公开 action shape，不是所有机器人通用维数。论文描述 fixed/sinusoidal queries，但 frozen code 实际使用 learned `nn.Embedding`，回答实现时必须保留此差异。[9][14]

### VLA-ACT-013：style latent 的 train / infer gap

训练 posterior 为：

\[
q_\phi(z\mid q_t,A_t)
=
\mathcal N\!\left(
\mu_\phi,\operatorname{diag}(\exp\ell_\phi)
\right),
\quad
z=\mu_\phi+\exp(\tfrac12\ell_\phi)\odot\epsilon,
\quad
\epsilon\sim\mathcal N(0,I).
\]

变量与实现：\(A_t\in\mathbb R^{H\times14}\)，\(z\in\mathbb R^{32}\)，\(\ell_\phi\) 是 `logvar`。target chunk 帮助 posterior 压缩 demonstration style，reparameterization 让 reconstruction gradient 通过 sampling。[14]

推理时 frozen code 不运行 posterior，也不从 prior 随机采样，而是：

\[
z_{\mathrm{test}}=0=\mathbb E_{\mathcal N(0,I)}[z].
\]

这使 evaluation deterministic。它的边界是：训练期 latent 能表达多样性，不等于部署会随机探索多个 mode。若面试回答“ACT 推理采多个 \(z\) 再挑最好动作”，与该 commit 不符。[9][14]

KL 与 reconstruction 的总目标为：

\[
\mathcal L_{\mathrm{ACT}}
=
\mathcal L_{L1}^{\mathrm{code}}
+\beta\,
\frac1B\sum_b\frac12
\sum_{j=1}^{32}
\left(
\mu_{b,j}^2+\exp\ell_{b,j}-1-\ell_{b,j}
\right).
\]

变量与实现：\(\beta\) 是 `kl_weight`；公开 recipe 使用 10，但不是跨任务常数。论文 Algorithm 1 写 MSE，方法正文与 frozen `policy.py` 用 L1；安全口径必须说“paper algorithm 存在不一致，正文/代码是 L1 + KL”。[9][14]

### VLA-ACT-014：temporal ensemble 融合相同 target time

query time \(q\) 会预测 \(q,\ldots,q+H-1\)。当前 target time \(t\) 可由这些历史 query 覆盖：

\[
\mathcal Q_t
=
\{q\mid \max(0,t-H+1)\le q\le t\}.
\]

变量与实现：每个 \(q\in\mathcal Q_t\) 都产生对**同一个** \(a_t\) 的估计 \(\hat a_t^{(q)}\)；代码把 chunk 写入二维 `all_time_actions[q,q:q+H]` 后读取 column \(t\)。这不是把 \(a_{t-1},a_t,a_{t+1}\) 做普通时域平滑。[14]

按 oldest-to-newest 排列 \(q_0<\cdots<q_{n-1}\)：

\[
w_i=\exp(-mi),
\qquad
a_t^{\mathrm{exec}}
=
\frac{\sum_iw_i\hat a_t^{(q_i)}}{\sum_iw_i}.
\]

变量与代码映射：\(m=0.01\) 是 frozen decay；`np.arange` 从 oldest row 开始，因此 \(w_0\) 最大，**最旧预测权重最高**。快速变化环境中这也可能保留 stale plan；“新预测权重最大”是对此实现的错误复述。[9][14]

### VLA-ACT-015：chunking、replan 与 ensemble 如何共同决定闭环

frozen rollout 有两种极端：

| 模式 | model \(H\) | query interval \(R\) | execute \(K\) | 新 observation 如何进入 |
| --- | ---: | ---: | ---: | --- |
| `temporal_agg=False` | 不变 | \(H\) | \(H\) | chunk 边界 |
| `temporal_agg=True` | 不变 | 1 | 1 | 每个 control step |

因此 chunking 是**预测表示**，replanning 是**反馈频率**，ensemble 是**重叠预测融合**。一次输出 \(H\) 步不等于必须 open-loop 执行 \(H\) 步；反过来，每步 query 也不意味着 model horizon 变成 1。[14]

```python
def act_closed_loop_step(obs, t, policy, prediction_table, temporal_agg):
    # Query every step with aggregation, otherwise only at chunk boundaries.
    if temporal_agg or t % policy.horizon == 0:
        chunk = policy(obs, z=zeros())  # Frozen inference uses z=0.

    if temporal_agg:
        # Store each query's predictions under their physical target times.
        add_overlapping_chunk(prediction_table, query_time=t, chunk=chunk)

        # Fuse predictions that all target the current physical time t.
        normalized_action = ensemble_same_target_time(prediction_table[t])
    else:
        # Execute one cached slot; fresh observation changes the next chunk only.
        normalized_action = chunk[t % policy.horizon]

    # Denormalize to absolute joint-position targets before env.step.
    return denormalize(normalized_action)
```

伪代码映射 frozen rollout 的两条 path；真实项目要另报异步 queue、safety clip、action semantics 与 \(K/R\) 是否解耦。

### VLA-ACT-016：chunk 太短或太长

| \(H\) | 主要收益 | 主要代价 |
| --- | --- | --- |
| 太短 / \(H=1\) | 反馈及时、单次输出小 | query 多、长程 coherence 弱、易受局部噪声影响 |
| 中等 | sequence coherence 与 responsiveness 折中 | 需要按任务/控制频率调 |
| 太长 | policy calls 少、覆盖长动作片段 | stale tail、长序列建模难、query slots 计算/显存增加 |

若无 aggregation，最坏 observation staleness 约为：

\[
\Delta t_{\mathrm{stale,max}}\approx(H-1)\Delta t.
\]

变量与直觉：\(\Delta t\) 是 control period；扰动刚发生在 chunk 首步后，最迟到下一 chunk 才进入 policy。ACT 论文的特定 ablation 在 \(H=100\) 附近最好、200/400 略降，只能说明其协议中的折中，不能背成通用最优 horizon。[9][14]

开启 temporal ensemble 可把 feedback interval 降到 1，却把 inference 从约 \(T/H\) 次提高到 \(T\) 次，并引入 overlapping buffer 与 stale-weight 风险。选 \(H\) 时必须同时报 \(K,R,\Delta t\) 和 policy latency。

### VLA-ACT-017：ACT 与 token、Diffusion / Flow 的归纳偏置

| 路线 | 训练 target | 生成计算 | 多模态/随机性 | 部署重点 |
| --- | --- | --- | --- | --- |
| ACT | continuous chunk L1 + CVAE KL | 一次 parallel query decode | train latent；frozen test \(z=0\) deterministic | H/K/R、temporal ensemble |
| OpenVLA | scalar token CE | AR 生成 d 个 token | categorical decoding | bin/offset/单步 |
| FAST | frequency/BPE token CE | AR variable-length tokens | token decoding | tokenizer H/D/revision |
| Diffusion Policy | epsilon/sample MSE | \(K_d\) scheduler steps | Gaussian trajectory init | \(T_o/T_p/T_a/K_d\) |
| π0 Flow | velocity MSE | \(N_f\) ODE/Euler steps | Gaussian action init | time/sign/NFE/H/K |

ACT 的强归纳偏置是“用 \(H\) 个 query 一次给出连续 chunk，并可对重叠 chunk 融合”；它没有量化/AR token latency，也没有 diffusion/flow 的多步 sampler，但 frozen test latent 固定为零，部署多模态性弱于随机生成路线。方法选择必须用同协议的 latency、physical error 与 closed-loop success，而不是按“生成式”标签排序。[14][15][16]

## Diffusion Policy：条件动作扩散与 Receding Horizon

> 本节对应 `VLA-ACT-018..022`。直接证据来自 Diffusion Policy arXiv v5、`real-stanford/diffusion_policy@5ba07ac...` 与其固定的 `diffusers=0.11.1`；warm-start、loss denominator、boundary padding 与 inference-step 数已独立复核，local runtime 仍 WARN。[10][15][26]

### VLA-ACT-018：为什么适合多模态连续动作

Diffusion Policy 直接建模整个 continuous trajectory 的条件分布：

\[
p_\theta(A_t\mid O_t),
\qquad
A_t\in\mathbb R^{T_p\times D_a},
\quad
O_t=(o_{t-T_o+1},\ldots,o_t).
\]

变量与直觉：\(T_o\) 是 observation horizon，\(T_p\) 是 prediction horizon，\(D_a\) 是 action dimension。随机 Gaussian trajectory 经过 conditional denoising 得到一条连贯 action sequence；不同 initial noise 可落到不同动作 mode。[10][15]

它不是每个 timestep 独立采样：

\[
p_\theta(A_t\mid O_t)
\ne
\prod_{h=0}^{T_p-1}p_\theta(a_{t+h}\mid O_t).
\]

实现映射：UNet/Transformer 都以 `[B,T_p,D_a]` 为整体对象，temporal network 在同一次 denoising 过程中耦合相邻 action。多模态性来自 sequence-level stochastic generation，不等于线上必须保持随机；固定 generator 或 deterministic DDIM 会改变部署行为。[15]

### VLA-ACT-019：conditional DDPM 的 noisy action、target 与 condition

clean trajectory \(A^0\) 在随机 diffusion timestep \(k\) 加噪：

\[
A^k
=
\sqrt{\bar\alpha_k}A^0
+\sqrt{1-\bar\alpha_k}\epsilon,
\qquad
\epsilon\sim\mathcal N(0,I).
\]

变量与实现：\(\bar\alpha_k\) 来自 scheduler 的 beta/noise schedule；frozen policy 用 `noise_scheduler.add_noise(trajectory, noise, timesteps)` 构造 `noisy_trajectory`，shape 不变。[10][15]

默认 epsilon objective：

\[
\mathcal L_\epsilon
=
\mathbb E
\left[
\left\|
\epsilon-\epsilon_\theta(O_t,A^k,k)
\right\|_2^2
\right].
\]

变量与实现：condition \(O_t\) 在 default image-hybrid path 经 vision encoder 展平成 `global_cond`；trajectory 只含 action channels。frozen policy 也支持 `prediction_type="sample"` 时 target 为 clean \(A^0\)，但 policy code 没实现 `v_prediction` target，即使底层 diffusers scheduler 支持该 branch。[15]

### VLA-ACT-020：schedule、prediction type 与 horizon 是三组合同

frozen policy target 为：

\[
y=
\begin{cases}
\epsilon,&\texttt{prediction\_type=epsilon},\\
A^0,&\texttt{prediction\_type=sample}.
\end{cases}
\]

变量与边界：prediction type 决定 model output 的监督语义；scheduler 决定如何从 \(A^0\) 构造 \(A^k\) 以及如何解释 model output 做 reverse step。只改 config 字符串而不改 target builder，会训练错误 objective。[15]

必须同时报告五条时间轴：

| 时间量 | field | 作用 |
| --- | --- | --- |
| observation horizon | `n_obs_steps = T_o` | condition 用几帧 |
| prediction horizon | `horizon = T_p` | diffusion trajectory 长度 |
| action slice | `n_action_steps = T_a` | policy 返回几步 |
| replan interval | wrapper / `steps_per_inference` | 多久重新观测/query |
| diffusion iterations | `num_inference_steps = K_d` | 一次 query 内去噪几次 |

noise schedule 控制不同 \(k\) 的 signal-to-noise；\(T_p\) 控制 sequence length；\(K_d\) 控制 reverse approximation compute。三者互相关联但不能互换。frozen boundary padding 重复 episode 首尾 target，且 policy 拒绝 `valid_mask`，重复值会作为普通 target 进入 MSE。[15]

### VLA-ACT-021：receding-horizon 的 action slice 与执行

论文定义：

\[
O_t=(o_{t-T_o+1},\ldots,o_t),
\qquad
A_t=(a_t,\ldots,a_{t+T_p-1}).
\]

policy 生成 \(T_p\) 步后，从最后一帧 observation 对齐：

\[
\hat A_t^{\mathrm{return}}
=
\operatorname{Unnormalize}
\left(
X^{(0)}_{:\,T_o-1:T_o-1+T_a,\,:D_a}
\right).
\]

变量与实现：slice start 是 `T_o-1`，\(T_a\) 是返回 action 数。simulation 的 `MultiStepWrapper` 通常顺序执行整段 \(T_a\) 后再给新 observation；real script 可一次提交更长 timestamped queue，却由 `steps_per_inference` 更早触发新 query。提交长度不等于重规划间隔。[15]

```python
def diffusion_receding_horizon(obs_history, policy, env):
    # Encode exactly To recent observations as the diffusion condition.
    condition = policy.encode_observations(obs_history[:policy.To])

    # One query starts from a fresh Gaussian action trajectory [Tp, Da].
    trajectory = randn([policy.Tp, policy.action_dim])
    for k in policy.scheduler.timesteps:
        # Predict epsilon or clean sample according to the checkpoint contract.
        model_output = policy.model(trajectory, k, global_cond=condition)
        trajectory = policy.scheduler.step(model_output, k, trajectory).prev_sample

    # Return Ta actions aligned with the most recent observation.
    actions = unnormalize(trajectory[policy.To - 1:policy.To - 1 + policy.Ta])

    # The rollout wrapper decides how many returned actions execute before replan.
    return env.step(actions)
```

伪代码表达 frozen global-conditioning/simulation 主链；real robot 的 timestamp queue 与 query schedule 需要单独建模，不能由 `T_a` 推断。

### VLA-ACT-022：去噪步数、sampler 与 warm-start

一次 inference 可写成：

\[
X^{(K_d)}\sim\mathcal N(0,I),
\qquad
X^{(k-1)}
=
\operatorname{SchedulerStep}
\left(
X^{(k)},f_\theta(X^{(k)},k,O_t)
\right).
\]

变量与实现：\(K_d\) 是 denoising iterations；DDPM 通常保留 stochastic reverse transition，DDIM 可在抽稀 time grid 上做更确定的更新。减少 \(K_d\) 会降低 query compute，但改变 reverse approximation，不保证 success 单调不变。[10][15]

版本边界必须原样保留：

- paper main text 的 real-world 例子写 100 train / 10 DDIM eval；
- paper v5 real table rows 出现 16 eval；
- frozen real configs 写 8；
- `eval_real_robot.py` runtime 又强制 16。

paper 称 receding-horizon 可 warm-start 下一次 inference；frozen major policy classes 每次从 `torch.randn` 重启，并拒绝 `past_action`。所以只能说“paper 提供设计选项，当前审计 commit 未实现”。如果自行实现 warm-start，要对齐已执行 prefix、新 observation、trajectory shift 和 scheduler noise level，并用 latency/stability ablation 证明收益。[15]

## Flow Matching：CFM、OT Path、ODE 与 π0

> 本节对应 `VLA-ACT-023..030`。基础定义来自 Flow Matching arXiv v2；现代 `facebookresearch/flow_matching@11568d3...` 只作 path/solver API 补证，不冒充 2022 历史实现；π0/openpi 特化沿用 Source Audit B/E 的 frozen 版本。[16][17][18] 2026-07-19 的 [独立事实复核](../sources/vol_03_flow_pi0_time_sign_independent_fact_review.html) 已直接核对 Theorem 2、paper `sigma_min` endpoint、time/sign/dt、Beta 换元与 10-step oracle；项目 runtime 与口述仍 `WARN/unseen`。

### VLA-ACT-023：probability path 与 velocity field

Continuous Normalizing Flow（CNF）用 vector field 定义 sample trajectory：

\[
\frac{d}{dt}\phi_t(x)=v_t(\phi_t(x)),
\qquad
\phi_0(x)=x,
\qquad
p_t=[\phi_t]_*p_0.
\]

变量与直觉：\(p_0\) 是 source/noise distribution，\(p_t\) 是中间 probability path，\(\phi_t(x)\) 是一个 sample 的 ODE trajectory，\(v_t\) 告诉当前位置下一瞬间往哪里走。path 是分布随时间的变化，不是一条具体 action curve。[17]

Flow Matching 让 network \(v_\theta\) 拟合生成 path 的 target field \(u_t\)：

\[
\mathcal L_{\mathrm{FM}}
=
\mathbb E_{t,x\sim p_t}
\left[
\|v_\theta(x,t)-u_t(x)\|_2^2
\right].
\]

变量与实现：直接 marginal \(u_t\) 通常难算；Conditional Flow Matching（CFM）对每个 data endpoint \(x_1\) 采 conditional path \(p_t(x\mid x_1)\) 与可计算的 \(u_t(x\mid x_1)\)。论文 Theorem 2 在 \(p_t(x)>0\) 的假设下证明两项目标相差与 \(\theta\) 无关的常数，因此 gradients identical；这不等于逐 sample target 或 loss 数值相同。[16][17]

“simulation-free training”表示训练可直接采 path point/target，不需先积分 ODE；inference 仍需 solver。

### VLA-ACT-024：线性 OT path 与 target velocity

基础论文的 Gaussian conditional OT path 是：

\[
x_t=
\left[1-(1-\sigma_{\min})t\right]x_0+tx_1,
\qquad
\dot x_t=x_1-(1-\sigma_{\min})x_0.
\]

变量与边界：\(x_0\sim\mathcal N(0,I)\)，\(x_1\sim q\)；当 \(t=1\) 时仍有 \(\sigma_{\min}x_0\)，所以 paper endpoint 是 data point 周围的小 Gaussian。不能说原论文所有 OT 公式都令 \(\sigma_{\min}=0\)。[16][17]

现代 package 的 `CondOTProbPath` 使用 exact endpoint，即 \(\sigma_{\min}=0\) 特例：

\[
x_t=(1-t)x_0+tx_1,
\qquad
u_t=x_1-x_0.
\]

变量与实现：`CondOTScheduler` 返回 \(\alpha_t=t,\sigma_t=1-t,\dot\alpha_t=1,\dot\sigma_t=-1\)；`AffineProbPath.sample` 产生 `x_t` 与 `dx_t`。continuous example 手写 velocity MSE：

\[
\mathcal L_{\mathrm{CFM}}
=
\mathbb E_{t,x_0,x_1}
\left[
\|v_\theta(x_t,t)-(x_1-x_0)\|_2^2
\right].
\]

公式映射：\(x_1\) 在 VLA 中可替换成 normalized \(H\times D\) action chunk，\(x_0\) 是同形状 Gaussian。conditional target 对一对 endpoints 是常量，不等于 marginal field 在全空间是常量。[16][18]

### VLA-ACT-025：ODE solver 如何从 noise 得到 action chunk

给定 learned velocity，Euler update 为：

\[
x_{k+1}
=
x_k+\Delta t\,v_\theta(x_k,t_k,c),
\qquad
t_{k+1}=t_k+\Delta t.
\]

变量与实现：\(c\) 是 observation condition；\(x_k\in\mathbb R^{B\times H\times D}\) 是当前 noisy action state。现代 package 的 `ODESolver` 可调用 Euler、midpoint、Heun 或 adaptive `dopri5`；fixed step 要报 grid/step size，adaptive solver 要报 tolerance 与实际 NFE。[18]

openpi 的 code convention 从 \(t=1\) noise 以 \(\Delta t=-1/N\) 走到 \(t=0\) data，默认 \(N=10\)：

\[
x_{k+1}=x_k-\frac1N v_\theta^{\mathrm{code}}(x_k,t_k,o).
\]

变量与边界：10 是一次 query 内的 flow integration steps，不是 action horizon \(H\)、执行前缀 \(K\) 或 control steps。prefix image/language KV cache 只计算一次，每个 Euler step 重算 state/noisy-action/time suffix。[6][16]

### VLA-ACT-026：Diffusion epsilon 与 Flow velocity

| 维度 | Frozen Diffusion Policy | π0 / openpi Flow |
| --- | --- | --- |
| time | discrete scheduler index \(k\) | continuous \(t/\tau\) |
| noisy sample | scheduler `add_noise` | explicit affine interpolation |
| default target | epsilon | path velocity |
| inference | DDPM/DDIM scheduler step | ODE/Euler step |
| compute count | \(K_d\) denoising iterations | \(N_f\) field evaluations |
| horizon | \(T_p/T_a/R\) | \(H/K/R\) |

两项常见 loss：

\[
\mathcal L_\epsilon
=
\mathbb E\|\epsilon-\epsilon_\theta(O,A^k,k)\|_2^2,
\qquad
\mathcal L_v
=
\mathbb E\|u_t-v_\theta(o,x_t,t)\|_2^2.
\]

变量与直觉：两者都可从 Gaussian trajectory 开始、都可能使用 MSE，也都能建模 continuous multimodal chunks；但 target、time parameterization 和 sampler contract 不同。Flow Matching 论文还允许 diffusion probability paths，所以“完全无关”与“只是少几步 diffusion”都错误。[15][16][17]

采样步数不是定义：Diffusion 可用少步 DDIM，Flow 也可用很多 ODE steps。延迟必须按 model size、NFE、vision/prefix、transport 与 hardware 实测。

### VLA-ACT-027：π0 action expert 的 condition 与 noisy action

π0 将 data endpoint 具体化为 normalized action chunk：

\[
A^\tau=\tau A+(1-\tau)\epsilon,
\qquad
u_{\mathrm{paper}}=A-\epsilon,
\quad
A,\epsilon\in\mathbb R^{B\times H\times D}.
\]

变量与架构：\(A\) 是 target chunk，\(\epsilon\) 是 Gaussian source；图像与语言进入 VLM prefix，state、noisy action 与 flow time 进入 action-expert suffix，`action_out_proj` 输出同形状 velocity。[4][6][16]

frozen openpi 使用反向坐标：

\[
x_t=t\epsilon+(1-t)A,
\qquad
u_{\mathrm{code}}=\epsilon-A,
\qquad
t=1-\tau.
\]

变量与等价性：\(d\tau=-dt\)，同时 \(u_{\mathrm{code}}=-u_{\mathrm{paper}}\)，所以 \(u_{\mathrm{code}}dt=u_{\mathrm{paper}}d\tau\)。只说时间反向而漏掉 velocity sign，不足以证明 trajectory 等价。[16]

π0 的 timestep 也不是 uniform：若 \(y\sim\operatorname{Beta}(1.5,1)\)、\(\tau=0.999(1-y)\)，则 openpi time：

\[
t=1-\tau=0.001+0.999y.
\]

这直接映射 code 的 `Beta(1.5,1)*0.999+0.001`，强调 high-noise training region；它是 recipe weighting，不是 Flow Matching 的普遍定义。[4][6][16]

### VLA-ACT-028：valid dimensions、padding 与 loss mask

若真实 action dimension 是 \(d\)，model capacity 是 \(D\ge d\)，理想 valid-mask velocity loss 为：

\[
\mathcal L_{\mathrm{masked}}
=
\frac{
\sum_{b,h,j}m_{b,h,j}(v_{b,h,j}-u_{b,h,j})^2
}{
\sum_{b,h,j}m_{b,h,j}+\varepsilon_0
}.
\]

变量与实现要求：\(m\) 同时表达有效 horizon slot 与有效 action axis；它必须来自 dataset/action schema，不能由 inference output slicing 反推。[16]

frozen Pi0 实际先对 configured \(D\) 直接 mean：

\[
\ell_{b,h}
=
\frac1D\sum_{j=1}^{D}
(v_{b,h,j}-u_{b,h,j})^2,
\]

训练脚本再对 batch/horizon mean。若 `PadStatesAndActions` 将真实 \(d\) 补到 \(D\)，padding targets 也进入 gradient 与 denominator；模型可学零，但大量容易维会稀释 effective-action loss。`PadStatesAndActions`、attention mask、token loss mask、action valid mask 与 output slice 是五个不同层次。[6][16]

### VLA-ACT-029：conditional dropout / guidance

现代 flow package 的 image example 在训练随机丢 label condition，推理组合 conditional/unconditional velocities：

\[
v_{\mathrm{cfg}}
=
(1+s)v_{\mathrm{cond}}-s\,v_{\mathrm{uncond}}.
\]

变量与实现：\(s\) 是 guidance scale；\(s\ne0\) 时每次 ODE function evaluation 实际要两次 model forward。这个 example 支持 CFG 机制，不证明 frozen openpi Pi0 action path 已实现 condition dropout/guidance。[16][18]

迁移到 action policy 前必须定义 drop 什么：

- 只 drop language，保留 images/state；
- drop task condition 但保留安全/本体状态；
- 或完全 unconditional branch。

风险包括 double NFE latency、过大 velocity/action magnitude、破坏 smoothness、弱化视觉反馈或生成与 controller constraints 不一致的动作。验收要比较 task compliance、diversity、safety、success 与 latency，不只看 velocity loss。

### VLA-ACT-030：loss 正常但 rollout 失败的四层定位

| 层 | Flow 必查 | Diffusion 必查 | 共用接口 |
| --- | --- | --- | --- |
| A target/path | endpoint、time、velocity sign | add-noise、prediction type | shape/dtype/mask |
| B sampler | grid、dt、NFE、solver | scheduler version、Kd、step order | fixed-noise reproducibility |
| C transforms | norm、d/D、valid mask | norm、padding、clip_sample | axis/unit/action type |
| D controller | H/K/R、queue | Tp/Ta/R、timestamp queue | camera/state time、安全与终止 |

先用 oracle target 测算法不变量。openpi time convention 下，固定 \(A,\epsilon\)：

\[
x_t=t\epsilon+(1-t)A,
\qquad
u_t=\epsilon-A.
\]

变量与测试：用 oracle \(v=u_t\) 从同一 noise 做完整 Euler integration，应恢复 \(A\)；失败说明 target/sign/grid 有错，尚未轮到模型 capacity。之后依次做 tiny-batch overfit、norm round-trip、per-axis sentinel 和 bypass-model controller test。[16]

```python
def debug_generative_action_policy(batch, policy, controller):
    # A. Check target/path algebra with fixed action, noise and time.
    assert_oracle_solver_recovers_target(batch.actions)

    # B. Freeze observation/noise and sweep solver or scheduler steps.
    endpoints = sweep_sampling_steps(policy, fixed_noise=True)
    assert_no_sign_or_step_order_failure(endpoints)

    # C. Verify checkpoint stats, valid dimensions, axes and units.
    assert_normalization_roundtrip(batch.action_schema)
    run_per_axis_sentinel_tests(policy.output_transform)

    # D. Bypass the model with a known-safe action fixture.
    assert_controller_queue_and_replan(controller, batch.safe_fixture)
```

伪代码是可执行检查顺序，不代表本地 OpenPiVLA 已完成这些 tests。只有 checkpoint、action schema、solver/scheduler、H/K/R 与 eval artifacts 齐全后，才能把 failure 归因到个人项目模型。[16]

## Action dimension、padding、mask 与 slicing

### model D 与 environment d

令真实 action \(a\in\mathbb R^d\)，model action dimension 为 D 且 \(d\le D\)。zero-pad 与 output selection 可写为：

\[
a^{model}=Pa=
\begin{bmatrix}I_d\\0\end{bmatrix}a,
\qquad
a^{env}=Sa^{model},
\quad
S=\begin{bmatrix}I_d&0\end{bmatrix},
\quad SP=I_d.
\]

变量解释：P 对应输入/target padding，S 对应 output slicing。openpi `PadStatesAndActions` 将尾维补零；LIBERO output transform 返回前 7 维。`Pi0Config` 默认 D=32，`Pi0FASTConfig` 默认 D=32/H=32；官方 `pi0_fast_libero` training config 才显式 override 为 D=7/H=10。[6][12]

### training loss mask 是另一件事

理想的 valid-dimension masked loss 可写为：

\[
\mathcal L_{\mathrm{valid}}
=
\frac{
\sum_{b,h,i}
m_{bhi}
\left(\hat a_{bhi}-a_{bhi}\right)^2
}{
\sum_{b,h,i}m_{bhi}+\varepsilon
}.
\]

变量解释：\(m_{bhi}=1\) 表示该 batch/example、horizon、dimension 有真实语义；mask 可同时处理 embodiment-specific dims、episode-end horizon padding 和缺失 label。实现映射必须指出 mask 来自哪个 batch field。frozen π0 main loss 对 D 直接 mean，output slicing 发生在推理 transform；所以“有 slicing”不能证明“训练已 mask padding loss”。[6][12]

### 四个不同 mask

| Mask | 管什么 | 错误后果 |
| --- | --- | --- |
| image mask | view 是否真实存在 | zero image 被当有效 view |
| token input mask | padding token 是否参加 attention | 无效 token 污染 context |
| token loss mask | 哪些 output token 参加 CE | prompt/visual/token padding 被错误监督 |
| action valid-dim/horizon mask | 哪些 H×D target 有物理语义 | padding dims 或越界 future actions 污染 loss |

openpi LIBERO 对缺失 right-wrist image 的 mask 在 Pi0 与 Pi0FAST 路径不同，这是 frozen code behavior；本地模型必须按实际 architecture 验证，不能照抄 bool 值。[6][12]

## 平移、旋转、gripper 与 base action

### 先报 action type，再报数值

同一个 7D/8D vector 可表示完全不同控制语义：

- joint position / joint delta / joint velocity；
- end-effector position + orientation；
- gripper absolute position、binary open/close 或 delta；
- mobile base x-y velocity；
- torque/force。

openpi norm_stats 文档说明，其默认 π layout 将前 6/14 维用于左右 arm joint angles、gripper 分列，mobile base 使用 dim 14–15 velocity；DROID 的 8D 却是 7 维 joint velocity + gripper，15 Hz。[6] 因而 shape 相同不等于 action contract 相同。

### translation

必须说明：

- absolute pose 还是 \(\Delta x,\Delta y,\Delta z\)；
- world/base/tool/camera frame；
- meter、centimeter 还是 normalized unit；
- 每 control tick 的 delta 还是每 second velocity。

将位置 delta 当 velocity 会额外乘/除控制周期，造成量级错误。

### rotation

常见表示：

| 表示 | 维度 | 优点 | 风险 |
| --- | ---: | --- | --- |
| Euler angles | 3 | 直观 | singularity、周期跳变、轴顺序 |
| axis-angle / rotation vector | 3 | 适合小旋转增量 | 接近 π 的不连续与 branch |
| quaternion | 4 | 避免 Euler singularity | unit norm、q 与 -q 双覆盖 |
| 6D rotation | 6 | 对 neural regression 更连续 | 需正交化还原 rotation matrix |

Zhou 等指出 3D rotation 在 4D 或以下欧氏表示中存在连续性问题，并提出 5D/6D continuous representation 用于学习。[11] 这不是说所有 policy 都必须用 6D；小角度 delta control、现有 controller API 与 dataset compatibility 仍可能使 axis-angle/quaternion 更合适。

若使用 quaternion \(r\in\mathbb R^4\)，至少检查：

\[
\hat r=\frac{r}{\|r\|_2+\varepsilon},
\qquad
R(\hat r)=R(-\hat r).
\]

变量解释：第一式保证 unit quaternion；第二式说明双覆盖，同一个旋转有两个相反符号表示。dataset 若不做 hemisphere/sign canonicalization，MSE 会把等价旋转误当作相距很远。

### gripper

gripper 常为 absolute [0,1]、binary 或 position/velocity。不要把它与 arm delta 用完全相同的 loss/normalization 假设。OpenVLA OXE materialization 可对最后 gripper 维采用不同 normalization mask；openpi 文档将 gripper position 定义为 0 fully open、1 fully closed，但具体 dataset transform 仍需核对。[3][6][12]

### base action

mobile base 常用 \(v_x,v_y,\omega_z\) 或只用 x-y velocity。必须说明 robot/body frame、最大速度、安全裁剪与是否和 arm 同频执行。public openpi default layout 只列 x-y base velocity，不能据此推断本地项目也有 \(\omega_z\)。[6]

### 按语义组做统计

\[
\tilde a_i=
\mathcal N_{g(i)}(a_i;\eta_{g(i)}),
\]

变量解释：\(g(i)\) 把 dimension i 分到 translation、rotation、gripper、base 等语义组，\(\eta_g\) 是对应 stats/scale。实现中仍通常逐维保存数值，但审计时按语义组检查单位、outlier 与 inverse behavior，避免把不同物理量只因相邻排列而当作同分布。

## 模型输出到 controller 与最小闭环单测

> 本节对应 `VLA-ACT-031..032`。上游 decode/unnorm/queue、Octo mask 与 openpi broker/DROID example 已独立复核；本地 OpenPiVLA 的 axis、unit、controller mode 与 safety policy 仍需项目 artifact。[21][27]

### VLA-ACT-031：decode、unnorm、slice、schema 与 safety 必须有序

**直觉**：模型输出只是 model-space tensor。只有经过正确 tokenizer/solver、正确 normalization asset、正确维度和物理语义，再被 controller 接收，才是可执行动作。

令 raw model output 为 (z)，decoder 为 (mathcal D)，反归一化为 (mathcal U)，有效维选择为 (S_e)，frame/unit/absolute-delta 映射为 (mathcal R_e)，安全投影为 (Pi_{\mathcal A_e})：

\[
a^{\mathrm{ctrl}}
=\Pi_{\mathcal A_e}\!\left(
\mathcal R_e\!\left(S_e\,\mathcal U(\mathcal D(z))\right)
\right).
\]

变量与实现：(mathcal A_e) 是 controller 可接受的动作集合。顺序不能任意交换：normalized-space clip 与 physical velocity clip 不同；先 slice 再用 D 维 stats 与先 unnorm 再 slice 只有在 stats padding 规则匹配时才可能等价。[2][6][20][21]

| 路线 | 已核实输出链 | 仍不属于模型的部分 |
| --- | --- | --- |
| OpenVLA | 生成 d 个 token → tail-vocab decode → q01/q99 unnorm | axis/unit/frame/controller |
| Octo | diffusion action → embodiment D slice → mean/std 或 p01/p99 unnorm | robot-specific controller wrapper |
| openpi flow | sampled H×D → model outputs → checkpoint unnorm → dataset/repack outputs | local eval client 的 K/axis/safety |
| Pi0FAST | AR tokens → FAST inverse → H×D → checkpoint unnorm/output transforms | 同上 |

若 dataset 是部分 delta、controller 接 absolute，公开 openpi 式向量情况可写：

\[
a^{\mathrm{abs}}_{t:t+H-1}
=a^{\mathrm{data}}_{t:t+H-1}+m_\Delta\odot q_t,
\qquad
a^{\mathrm{ctrl}}=s_e\odot R_ea^{\mathrm{abs}}.
\]

变量与实现：(m_\Delta) 选择 delta dimensions，(q_t) 是当前 state，(R_e) 处理轴序/坐标，(s_e) 处理单位。真实 rotation 可能需要 (SO(3)) composition，不能默认向量加法。openpi `AbsoluteActions` 只能证明按 mask 给前若干维加 state；本地 (R_e,s_e) 仍需 wrapper 与 sentinel trace。[7][21]

openpi DROID example 是一条具体而非通用的 execution contract：远程返回 `[10,8]`，client 按 index 取一行、二值化 gripper、clip `[-1,1]`、调用 `env.step` 并按数据频率 sleep。[21] 面试中可以用它解释 chain，但不能把它的 8D schema 套到 OpenPiVLA。

### VLA-ACT-032：最小闭环测试要让错误可辨识

**直觉**：全 0/random tensor 很难发现 transpose、错轴和重复行。用 prime/one-hot sentinel，让每个 horizon row 和 action dimension 都不同，再逐层断言。

| 测试 | sentinel / 故障注入 | 必须断言 |
| --- | --- | --- |
| parser boundary | min/max token、EOS、越界/短序列 | 只接受 action token；严格得到 H×D |
| norm round-trip | q01/mean/q99、gripper mask | `unnorm(norm(a))≈a`；masked 维不变 |
| padding | valid dims 放互异质数，padding 放大常数 | loss/output 对 padding sentinel 不敏感；slice 只保留 d |
| axis/unit | 每组维度 one-hot | controller 轴、符号、m/cm、rad/deg 精确匹配 |
| FIFO chunk | row 编码为 0..H-1 | 连续 K 次严格输出 0..K-1，不重复/跳步 |
| replan/reset | 第 K 步新 chunk，episode 中途 reset | 只在定义边界切换；旧 queue 不泄漏 |
| stale RPC | 延迟、乱序、重复 response ID、断连 | 旧 response 被丢弃；超时进入 fail-safe |
| safety | NaN/Inf/超限 velocity/workspace pose | reject/投影规则明确，保留原值与触发日志 |
| mock controller | 完整 request→一次 `step` | 最终 dtype/shape/value/dt 全部匹配 |

openpi frozen `ActionChunkBroker` 在 cache 为空时 query，随后按 `_cur_step` slice，到 configured horizon 清空；manual test 只断言每步 shape。[9][21] 因此项目 test 仍需补 request ID、axis/unit、NaN、安全和组合顺序。

```python
def test_closed_loop_contract(policy_stub, broker, parser, output_transform, mock_env):
    # Unique rows and dimensions expose transpose, wrong-slice and repeated-row bugs.
    sentinel = make_prime_sentinel_chunk(horizon=4, model_dim=8, valid_dim=7)
    policy_stub.return_value = {"actions": sentinel, "request_id": 42}

    # Execute K=2 actions; FIFO must consume rows 0 and 1 exactly once.
    a0 = broker.infer(make_observation(request_id=42))["actions"]
    a1 = broker.infer(make_observation(request_id=42))["actions"]
    assert not_equal(a0, a1)

    # Apply the declared parse -> denorm -> slice -> schema -> safety sequence.
    c0 = output_transform(parser(a0))
    c1 = output_transform(parser(a1))
    assert c0.shape == c1.shape == (7,)
    assert all_finite_and_within_limits(c0, c1)

    # The final assertion is at the controller boundary, not only model tensors.
    mock_env.step(c0)
    assert mock_env.last_action == expected_controller_sentinel(row=0)
```

代码块说明：真实 suite 还要固定 norm stats hash、tokenizer revision、frame transform、controller mode、control dt 与 timeout policy。合成单测证明接口不变量，不替代 benchmark rollout。

## 如何选择 action representation

### 决策顺序

1. 先定 action contract：type、d、H、control frequency、controller。
2. 再看 conditional action 是否明显多模态。
3. 确定 inference latency 和 replan budget。
4. 检查 robot data 规模与 VLM token infrastructure。
5. 评估 normalized reconstruction 与 physical-unit error。
6. 最后才选 head/tokenizer，不以论文名替代需求。

### 选择表

| 场景 | 优先考虑 | 原因 | 必查反例 |
| --- | --- | --- | --- |
| 近单峰、严格低延迟、数据有限 | direct regression | pipeline 最短、debug 简单 | mode averaging、uncertainty |
| 已有 autoregressive VLM、action 低频/短 | scalar token | 复用 LM head/CE | quantization、AR latency |
| 高频 1-second chunks、需要 token route | FAST | 频域压缩减少相关冗余 | tokenizer revision、H/D reshape |
| 示范存在 sequence style variation | CVAE/ACT family | latent sequence model | posterior collapse、latent inference |
| continuous action 多峰、采样预算充足 | diffusion | generative continuous distribution | schedule/steps/latency |
| 想用 continuous transport + ODE/action expert | flow | velocity target + solver | time convention、solver stability |

### 不能用单个指标选型

FAST paper 报告其 π0-FAST AR inference 比 π0 flow 慢；这是特定 hardware/model 的 measurement，不是“flow 永远更快”。direct regression loss 低也可能 mode-average；token CE 低也可能只复制相邻动作；diffusion/flow offline sample quality 好也可能因 denorm/controller 错误而 0-success。[7][10][12]

### 面试回答模板

> 我会先固定 action type、H、d、控制频率与 replan budget，再判断条件分布是否多模态。若近单峰且延迟严格，continuous regression 是强 baseline；若要复用 VLM autoregressive head，考虑 scalar token 或 FAST，但要核 tokenizer、量化与 AR latency；若需要连续多模态生成，比较 diffusion 与 flow 的 target、sampling steps 和 action expert 成本。最后用 physical-unit reconstruction、latency 和 closed-loop success 联合验收。

## 训练与闭环推理 Pipeline

### Batch 构造与训练

```python
def build_and_train_vla_step(raw_episode, tick, model, representation, norm_stats):
    # 1. Align camera views and proprioception to one control tick.
    images, image_masks = align_views(raw_episode, tick)
    state = interpolate_proprio(raw_episode, tick)

    # 2. Build an H-step target without crossing the episode boundary.
    actions, horizon_mask = build_action_window(raw_episode, tick)

    # 3. Normalize with the exact stats attached to this dataset/checkpoint.
    norm_state = normalize_state(state, norm_stats)
    norm_actions = normalize_actions(actions, norm_stats)

    # 4. Convert only the action target into the selected representation.
    if representation == "openvla_scalar":
        targets, loss_mask = scalar_action_tokens(norm_actions, horizon_mask)
    elif representation == "fast":
        targets, loss_mask = fast_frequency_tokens(norm_actions, horizon_mask)
    elif representation == "act_cvae":
        # ACT posterior may see qpos/actions during training; padded slots need masks.
        targets, loss_mask = act_chunk_targets(norm_actions, horizon_mask)
    elif representation == "diffusion":
        # Diffusion target semantics depend on scheduler prediction_type.
        targets, loss_mask = sample_diffusion_target(norm_actions, horizon_mask)
    elif representation == "pi0_flow":
        targets, loss_mask = sample_flow_target(norm_actions, horizon_mask)
    else:
        targets, loss_mask = continuous_targets(norm_actions, horizon_mask)

    # 5. Model inputs keep view/state masks separate from target loss masks.
    output = model(images, image_masks, norm_state, targets)
    loss = masked_objective(output, targets, loss_mask)
    return loss
```

伪代码是通用审计模板：OpenVLA 原始路径没有多视角/state/H>1；ACT posterior 的 train/infer 输入不同；Diffusion target 必须与 scheduler prediction type 一致；π0 flow 不把 actions 变成 token；Pi0FAST 的 tokenization 与 loss mask 由 transforms 构造。真实实现应替换函数名并链接具体 code。[3][6][12][14][15]

### 闭环推理

```python
def closed_loop_step(env, policy, checkpoint_assets, replan_steps):
    # 1. Observe fresh images/state; preserve camera names and timestamps.
    raw_obs = env.get_observation()

    # 2. Reuse training-time preprocessing and checkpoint normalization stats.
    model_obs = policy.input_transforms(raw_obs, checkpoint_assets)

    # 3. Sample either tokens or a continuous action chunk.
    raw_model_output = policy.model.sample_actions(model_obs)

    # 4. Decode representation, unnormalize, select valid dimensions and convert axes/units.
    action_chunk = policy.output_transforms(raw_model_output, checkpoint_assets)

    # 5. Execute only K actions, then re-observe; H and K are different contracts.
    for action in action_chunk[:replan_steps]:
        checked_action = safety_clip_and_validate(action)
        obs, reward, done, info = env.step(checked_action)
        if done or info.get("success", False):
            break
    return info
```

变量映射：model horizon H 由 checkpoint/config 决定；replan_steps=K 由 rollout client 决定。openpi LIBERO example 默认 K=5，而 Pi0/Pi0FAST configs 可有不同 H。ActionChunkBroker 又可消费整段 H 后再 infer，证明 H 和 K 不是同义词。[6][12]

## 实现证据与 44 题覆盖

### frozen implementation map

| 机制 | 关键路径 | 已核实事实 |
| --- | --- | --- |
| OpenVLA data contract | `prismatic/vla/datasets/datasets.py` | primary image、language、current action；default no proprio/history/future |
| OpenVLA tokenizer | `prismatic/vla/action_tokenizer.py` | tail vocab、256 token IDs、255 reconstruction centers nuance |
| OpenVLA inference | `prismatic/models/vlas/openvla.py` | generated length from dataset action dim、decode、unnorm |
| OpenVLA training | `base_strategy.py` / VLM labels | token CE optimized；continuous L1 metric |
| π0 shape | `src/openpi/models/pi0_config.py` | default three images、state [B,32]、actions [B,50,32] |
| π0 flow | `src/openpi/models/pi0.py` | code convention、flow MSE、10-step default、prefix KV cache |
| π0.5 state/time | `pi0_config.py` / `pi0.py` / `tokenizer.py` | discrete state prompt、adaRMSNorm |
| Pi0FAST CE | `src/openpi/models/pi0_fast.py` | prefix-LM attention、postfix masked next-token CE |
| FAST integration | `tokenizer.py` / `transforms.py` | Hub processor、tail vocab mapping、token decode → H×D |
| policy transforms | `policy_config.py` / `policy.py` | checkpoint stats、normalize/sample/unnormalize/output order |
| LIBERO action interface | `libero_policy.py` / `examples/libero/main.py` | 8D state、7D output、K=5 default、image rotation |
| ACT posterior / decoder | `detr/models/detr_vae.py` / `transformer.py` | `[CLS]+qpos+actions`、32D latent、H learned queries、`[B,H,14]`；论文 fixed/sinusoidal query 与 frozen code 有差异 |
| ACT loss / rollout | `policy.py` / `imitate_episodes.py` | masked L1 但 full `B×H×D` mean、KL、`z=0`、整段执行与 temporal ensemble；oldest row 权重最大、zero sentinel 有边界 |
| Diffusion training | `diffusion_unet_hybrid_image_policy.py` | `[B,Tp,Da]`、epsilon/sample target、global condition、masked MSE |
| Diffusion inference | policy / scheduler / runners | Gaussian restart、DDPM/DDIM、`To-1` action slice、sim/real replan distinction |
| Flow Matching path/solver | `flow_matching/path/affine.py` / `solver/ode_solver.py` | exact CondOT path、velocity target、Euler/adaptive ODE API |
| RT-2 / Octo landscape | RT-2 §3.2–3.3、Octo §III、`octo_pretrain_config.py` | action-as-token、800k OXE、27M/93M、T5/image tokenizers、H=4/D=7 diffusion config |
| Octo mask/readout | `octo_module.py` / `action_heads.py` | block-wise attention、readout isolation、timestep/action conjunction mask、embodiment slice |
| Adaptation modes | OpenVLA `vla-scripts/finetune.py`、Octo `finetune_config.py`、openpi `training/config.py` | full/head-only/head-MLP-only/LoRA boundaries；不替代本地 trainable log |
| Serving/timing/queue | openpi `policy.py`、`websocket_policy_server.py`、`action_chunk_broker.py` | model/server/total timing、ordered output transforms、chunk cache/slice/reset |
| Controller contract tests | Source Audit F test matrix | parser、norm、padding、axis/unit、FIFO/replan、stale RPC、safety 与 mock step 设计 |

详细 frozen commit 与逐行解释见 [Source Audit A](../sources/vol_03_openvla_claim_to_code.html)、[Source Audit B](../sources/vol_03_pi0_fast_openpi_claim_to_code.html)、[Source Audit C](../sources/vol_03_act_claim_to_code.html)、[Source Audit D](../sources/vol_03_diffusion_policy_claim_to_code.html)、[Source Audit E](../sources/vol_03_flow_matching_pi0_claim_to_code.html) 与 [Source Audit F](../sources/vol_03_architecture_execution_claim_to_code.html)。

### 44 题覆盖矩阵

| ID | 本页答案位置 | 当前证据状态 | 后续缺口 |
| --- | --- | --- | --- |
| VLA-ARCH-001 | VLA/VLM/visuomotor 对比 | source-ready | 更多 landscape 对比在 ARCH-007 |
| VLA-ARCH-002 | I/O 字段表与 policy contract | source-ready | local OpenPiVLA contract |
| VLA-ARCH-003 | component responsibility table | source-ready | local model class |
| VLA-ARCH-004 | view/state/timestamp alignment | design-ready + upstream examples | local converter timestamps |
| VLA-ARCH-005 | OpenVLA normalize/token/CE/decode | source-ready / WARN | independent endpoint review |
| VLA-ARCH-006 | π0 prefix/suffix/flow/solver | source-ready / WARN | independent convention review |
| VLA-ARCH-007 | RT-2/OpenVLA/Octo/π0 landscape | independent-fact-reviewed / WARN | local architecture mapping |
| VLA-ARCH-008 | token/readout/suffix layout、attention/loss mask | independent-fact-reviewed / WARN | local layout sentinel test |
| VLA-ARCH-009 | freeze/full/head/LoRA/action expert | independent-fact-reviewed / WARN | target data/hardware ablation |
| VLA-ARCH-010 | unified D/d、Octo valid mask、padding risk | independent-fact-reviewed / WARN | local positive mask evidence |
| VLA-ARCH-011 | latency components、NFE/token/transport/queue | independent-fact-reviewed / WARN | local synchronized timing |
| VLA-ARCH-012 | paper→repo→checkpoint→runtime audit | independent-fact-reviewed / WARN | local manifest/trace |
| VLA-ACT-001 | five-route taxonomy | source-ready / WARN | independent cross-method review |
| VLA-ACT-002 | checkpoint norm contract | source-ready | local norm assets/tests |
| VLA-ACT-003 | OpenVLA quantile/bin trade-offs | source-ready / WARN | distribution-shift experiment |
| VLA-ACT-004 | tail vocab offset/collision/decode | source-ready / WARN | tokenizer version test |
| VLA-ACT-005 | FAST motivation | source-ready | independent review |
| VLA-ACT-006 | DCT/round/BPE/inverse | source-ready / WARN | reconstruction test |
| VLA-ACT-007 | compression vs control metrics | source-ready | local closed-loop ablation |
| VLA-ACT-008 | P/S、valid mask、slicing | source-ready as contract | local loss mask |
| VLA-ACT-009 | action type/unit/rotation/gripper/base | design-ready | local controller schema |
| VLA-ACT-010 | representation decision table | design-ready | JD / hardware-specific constraints |
| VLA-ACT-011 | ACT H/K/R/\(\Delta t\) | source-ready / WARN | local rollout values |
| VLA-ACT-012 | ACT posterior、decoder、learned queries | independent-fact-reviewed / WARN | local ACT usage and oral drill |
| VLA-ACT-013 | CVAE posterior、KL、test \(z=0\) | independent-fact-reviewed / WARN | latent ablation |
| VLA-ACT-014 | overlapping target-time ensemble | independent-fact-reviewed / WARN | local queue and sentinel test |
| VLA-ACT-015 | chunk / replan / ensemble modes | independent-fact-reviewed / WARN | local queue mapping |
| VLA-ACT-016 | horizon trade-off | independent-fact-reviewed / WARN | target hardware/task sweep |
| VLA-ACT-017 | ACT/token/Diffusion/Flow comparison | independent-fact-reviewed / WARN | comparable local ablation; Diffusion audit remains WARN |
| VLA-ACT-018 | sequence-level conditional diffusion | independent-fact-reviewed / WARN | fixed-noise diversity test |
| VLA-ACT-019 | noisy action、epsilon/sample target、condition | independent-fact-reviewed / WARN | local valid-mask evidence |
| VLA-ACT-020 | schedule/prediction type/five time axes | independent-fact-reviewed / WARN | v-pred extension if selected |
| VLA-ACT-021 | `To-1` slice、sim/real replan | independent-fact-reviewed / WARN | local controller queue |
| VLA-ACT-022 | DDPM/DDIM、steps、warm-start gap | independent-fact-reviewed / WARN | target hardware telemetry |
| VLA-ACT-023 | CNF path、sample trajectory、velocity field | source-ready | independent theorem review |
| VLA-ACT-024 | paper \(\sigma_{\min}\) 与 exact-linear CFM | source-ready / WARN | hand derivation |
| VLA-ACT-025 | ODE/Euler、time grid、NFE | source-ready | target hardware telemetry |
| VLA-ACT-026 | Diffusion epsilon vs Flow velocity | source-ready / WARN | controlled local comparison |
| VLA-ACT-027 | π0 prefix/suffix、time/sign、Beta recipe | source-ready / WARN | local model class |
| VLA-ACT-028 | masked ideal vs frozen all-D mean | source-ready / WARN | positive local mask evidence |
| VLA-ACT-029 | generic flow CFG mechanism | source-ready with warning | action-policy implementation |
| VLA-ACT-030 | four-layer target→controller debug | source-ready as framework | local test artifacts |
| VLA-ACT-031 | decode→unnorm→slice→schema→safety→controller | independent-fact-reviewed / WARN | local axis/unit/controller |
| VLA-ACT-032 | parser/FIFO/replan/stale/safety/mock tests | independent-fact-reviewed / WARN | local executable tests |

“source-ready”仍不是“reviewed”。Source Audit C 的 ACT、Audit D 的 Diffusion Policy 与 Audit F 的 architecture/execution 已完成独立事实复核（见 [ACT 独立复核](../sources/vol_03_act_independent_fact_review.html)、[Diffusion 独立复核](../sources/vol_03_diffusion_policy_independent_fact_review.html) 与 [Architecture/Execution 独立复核](../sources/vol_03_architecture_execution_independent_fact_review.html)）；local runtime 与口述训练仍为 WARN/PENDING。

## OpenPiVLA 项目挂钩与真实性边界

### 可以安全连接的上游机制

- OpenVLA 提供 scalar action-token baseline 和 token/CE/unnorm 审计方法。
- FAST 提供 action-window DCT/round/BPE 表示。
- π0/openpi 提供 multi-view/state/action expert、flow sampling、normalization 与 output transform 的公开候选机制。
- ACT 提供 CVAE action chunk、learned query 与 same-target-time temporal ensemble 的对照机制。
- Diffusion Policy 提供 conditional trajectory diffusion、scheduler 与 receding-horizon 的对照机制。
- openpi LIBERO example 提供 H/K、image transform、state/action slicing 的接口检查范式。
- Octo 提供 block-wise mask、readout 与有效 action-dimension mask 的正例；可用于审查“padding 是否真的不进 loss”。
- Source Audit F 提供 paper→repo→checkpoint→runtime 的证据链、延迟分层和 parser/queue/safety 单测模板。

### 不能自动写成本地事实

| Claim | 为什么不能由本页证明 | 需要的本地 artifact |
| --- | --- | --- |
| 使用 Qwen3-VL 或某个 π checkpoint | upstream model 不等于 local load path | config、checkpoint manifest、startup log |
| 使用 FAST+ revision ec4d7aa... | default Hub string 未 pin local cache | tokenizer config/cache/revision |
| horizon=10 | official example 可覆盖 config | dataset target、model output shape、eval config |
| action axes/units | shape 不能推出 controller semantics | schema、norm stats、output transform |
| formal JSON/token supervision | OpenVLA/FAST 都不等于 local formatter | prompt formatter、labels、loss mask、parser |
| 97.4% | upstream 不含该 local eval | checkpoint ID、suite、tasks、trials、seed、summary |
| 本人创新 action expert/FAST | 公开设计属于 upstream | local diff、设计记录、run ledger、ownership |

### 项目口述安全模板

> 上游机制上，我会把 OpenVLA scalar token、FAST frequency token 和 π0 flow action expert 分开解释。对我的项目，我只在本地 config、checkpoint、formatter、norm stats 与 rollout summary 能对应时，才说明实际采用哪条路径。当前整理页中的 97.4%、horizon 和 Qwen/π 关系仍需 artifact reconciliation，因此不会用 upstream repo 代替项目证据。

## Bad Case 与最小检查清单

### offline loss 正常、online 0-success 的排查顺序

1. **Action semantics**：position/velocity/delta、axis order、frame、unit。
2. **Normalization**：asset_id、q01/q99、clip policy、inverse consistency。
3. **Dimension**：D、d、padding、valid loss mask、output slicing。
4. **Tokenizer/decode**：revision、offset、EOS、H/D reshape、malformed fallback。
5. **Observation**：camera name、flip/resize、image mask、state timestamp。
6. **Chunk loop**：H、K、queue reset、control frequency、episode termination。
7. **Model target**：CE label positions、ACT L1/KL 与 pad denominator、Diffusion prediction type/scheduler、Flow time/velocity sign。
8. **最后才谈 capacity/data**：先排除接口错误，再归因模型不足。

### 最小单测矩阵

| Test | 输入 | 断言 |
| --- | --- | --- |
| norm round-trip | q01/q99 内 action | inverse error < δ |
| saturation | q01/q99 外 action | clip/no-clip behavior 与设计一致 |
| axis impulse | 单维非零动作 | 只有预期 actuator/axis 响应 |
| padding | d<D 的 target | extra dims 的 loss/output 行为有显式断言 |
| token round-trip | scalar / FAST known chunk | decode shape、误差、offset 正确 |
| missing view | zero image + mask false/true | architecture-specific mask 正确 |
| chunk queue | H>K、episode reset | 执行正好 K 步并清空旧 queue |
| stale RPC / safety | 乱序 response、NaN/Inf、超限 action | 旧 response 丢弃；fail-safe/投影日志正确 |
| temporal ensemble | 三个 query 覆盖同一 target time | ordering、weights 与 valid sentinel 正确 |
| diffusion scheduler | fixed clean/noise/timestep | add-noise target 与 reverse prediction type 一致 |
| controller rate | constant velocity/delta | 单位与 \(\Delta t\) 转换正确 |

### 高危答案

- “VLA 就是 VLM 多一个 action head。”
- “OpenVLA 一次生成 H 步，因为会生成很多 token。”
- “FAST 是把每个 action scalar 分 bin。”
- “π0.5 和 Pi0FAST 是同一个模型。”
- “padding 后推理 slice 掉，所以训练 loss 不会受影响。”
- “ACT 推理会随机采多个 style latent，再挑最优 chunk。”
- “temporal ensemble 给最新预测最高权重，或平滑相邻物理时刻。”
- “Diffusion Policy 的 horizon、返回 action 数、replan interval 和去噪步数是同一个量。”
- “paper 提 warm-start，所以 frozen repo 默认复用上一段 trajectory。”
- “8D action 就是 xyz + rotation + gripper。”
- “offline action loss 下降说明机器人 success 会提升。”

## 后续工作

本页已完成 VOL 03 的 44/44 知识节点，但仍是 `review_pending / WARN`，不等于已掌握。下一步顺序：

1. 44-card completion reconciliation 已完成；A–F source audits 的独立事实复核仍保持 WARN/PENDING，不提前升 reviewed。
2. 对应 44 道原子题卡全部保持 unseen，等待真实口述。
3. Source Batch C 已完成：ACT paper/repo 的 CVAE latent、chunk query、masked L1 + KL、full-mean padding dilution、learned query 与 temporal ensemble ordering 已独立复核；见 [ACT Claim-to-Code](../sources/vol_03_act_claim_to_code.html) 与 [ACT 独立复核](../sources/vol_03_act_independent_fact_review.html)。
4. Source Batch D 已完成：Diffusion Policy paper/repo 的 target、scheduler、horizon、loss denominator、boundary padding、warm-start 边界与 receding-horizon 已独立复核；见 [Diffusion Policy Claim-to-Code](../sources/vol_03_diffusion_policy_claim_to_code.html) 与 [Diffusion 独立复核](../sources/vol_03_diffusion_policy_independent_fact_review.html)。
5. Source Batch E 已完成：Flow Matching foundation、CFM/OT path、ODE、π0/openpi 时间换元与 Diffusion 对照；见 [Flow Matching / π0 Claim-to-Code](../sources/vol_03_flow_matching_pi0_claim_to_code.html)。
6. Source Batch F 已完成：RT-2/OpenVLA/Octo/π0 architecture、mask、adaptation、latency、checkpoint audit、transform/broker/controller test 已独立复核；见 [Architecture & Execution Claim-to-Code](../sources/vol_03_architecture_execution_claim_to_code.html) 与 [独立复核](../sources/vol_03_architecture_execution_independent_fact_review.html)。
7. 下一阶段只做一题 `VLA-ARCH-010/031`、ACT/Diffusion 或 OpenPiVLA ownership 真实口述；不再新增 VOL 03 卡，不把页面生成计入掌握分数。

## 参考文献（References）

1. Brohan et al., [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/abs/2307.15818), arXiv v1, 2023.
2. Kim et al., [OpenVLA: An Open-Source Vision-Language-Action Model](https://arxiv.org/html/2406.09246v3), arXiv v3, 2024.
3. [openvla/openvla](https://github.com/openvla/openvla/tree/c8f03f48af692657d3060c19588038c7220e9af9), frozen commit `c8f03f48af692657d3060c19588038c7220e9af9`.
4. Black et al., [π0: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/html/2410.24164v4), arXiv v4, 2024.
5. Black et al., [π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/html/2504.16054v1), arXiv v1, 2025.
6. [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), frozen commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`, Apache-2.0.
7. Pertsch et al., [FAST: Efficient Action Tokenization for Vision-Language-Action Models](https://arxiv.org/html/2501.09747v1), arXiv v1, 2025.
8. [physical-intelligence/fast](https://huggingface.co/physical-intelligence/fast/tree/ec4d7aa71691cac0b8bed6942be45684db2110f4), frozen revision `ec4d7aa71691cac0b8bed6942be45684db2110f4`, Apache-2.0.
9. Zhao et al., [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/abs/2304.13705), ACT, arXiv v1, 2023.
10. Chi et al., [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/abs/2303.04137), arXiv v5, 2024.
11. Zhou et al., [On the Continuity of Rotation Representations in Neural Networks](https://arxiv.org/abs/1812.07035), CVPR 2019.
12. 本仓库逐行证据页：[OpenVLA Source Audit A](../sources/vol_03_openvla_claim_to_code.html)；[π0 / π0.5 / FAST / openpi Source Audit B](../sources/vol_03_pi0_fast_openpi_claim_to_code.html)。
13. 本地项目入口：[OpenPiVLA：FAST 动作表示、Metax 迁移与策略评估复现](../../03_openpivla_action_modeling.html)。该页不是缺失 raw artifacts 的替代证据。
14. [ACT CVAE、Action Chunk 与 Temporal Ensemble Source Audit C](../sources/vol_03_act_claim_to_code.html)，frozen commit `742c753c0d4a5d87076c8f69e5628c79a8cc5488`。
15. [Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Source Audit D](../sources/vol_03_diffusion_policy_claim_to_code.html)，frozen commit `5ba07ac6661db573af695b419a7947ecb704690f`。
16. [Flow Matching 基础、π0 特化与 ODE Source Audit E](../sources/vol_03_flow_matching_pi0_claim_to_code.html)，用于 ACT/Diffusion/Flow 方法边界与 Batch 2B 知识/题卡。
17. Lipman et al., [Flow Matching for Generative Modeling](https://arxiv.org/html/2210.02747v2), arXiv `2210.02747v2`, 2023。
18. [facebookresearch/flow_matching](https://github.com/facebookresearch/flow_matching/tree/11568d37f8d5a080e12aa7b5305d9c35ae07d136), frozen commit `11568d37f8d5a080e12aa7b5305d9c35ae07d136`, CC BY-NC 4.0；后续维护包，不作为 2022 历史实现。
19. Octo Model Team et al., [Octo: An Open-Source Generalist Robot Policy](https://arxiv.org/html/2405.12213v2), arXiv `2405.12213v2`, 2024；[§III-A Architecture](https://arxiv.org/html/2405.12213v2#S3.SS1)。
20. [octo-models/octo](https://github.com/octo-models/octo/tree/241fb3514b7c40957a86d869fecb7c7fc353f540), frozen commit `241fb3514b7c40957a86d869fecb7c7fc353f540`, MIT；block-wise transformer、action head、mask 与 fine-tune config。
21. [VLA 架构、适配、延迟与动作执行 Source Audit F](../sources/vol_03_architecture_execution_claim_to_code.html)，用于 `VLA-ARCH-007..012` 与 `VLA-ACT-031..032` 的 claim-to-code 边界。
22. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
23. [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
24. [VOL 03 44-Card Completion Reconciliation](../sources/vol_03_completion_fact_reconciliation.html)。
25. [ACT CVAE / Action Chunk / Temporal Ensemble 独立事实复核](../sources/vol_03_act_independent_fact_review.html)，2026-07-19。
26. [Diffusion Policy 条件扩散独立事实复核](../sources/vol_03_diffusion_policy_independent_fact_review.html)，frozen commit `5ba07ac6661db573af695b419a7947ecb704690f`，2026-07-19。
27. [VLA 架构、Mask、适配与执行独立事实复核](../sources/vol_03_architecture_execution_independent_fact_review.html)，RT-2/Octo/openpi direct source hashes 与 probes，2026-07-19。
