# VOL 03 VLA / Action：核心面试题卡（完整卷）

> 状态：`completion_reconciled_candidate / source_audits_warn / 44 unseen / WARN`  
> 当前题数：44 / 44  
> 覆盖范围：`VLA-ARCH-001..012`、`VLA-ACT-001..032`  
> 难度：L1 2 题 / L2 18 题 / L3 24 题  
> 优先级：P0 26 题 / P1 17 题 / P2 1 题  
> 练习状态：全部 `unseen`  
> 使用方式：先闭卷说 30 秒版本，再展开机制；未真实口述前不得改为 pass/strong。  
> 深度来源：[VOL 03 完整知识卷](../knowledge/vol_03_vla_action.html)；Source Audit A–F 的 public paper/code facts 均已完成独立切片，但本页不替代项目 raw artifacts 或真实口述。
> 项目证据总门：[OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) / [Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)；下列所有项目挂钩均受其 checkpoint、schema、eval 与 ownership 缺口约束。

## A. VLA 架构与输入输出合同

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-ARCH-001</b> · VLA 与 VLM、传统 visuomotor policy 的本质区别是什么？</summary>

**面试意图**：检查你能否区分语义模型、低层策略和完整执行合同。

**30 秒回答**：VLM 主要从图像文本产生语义输出；传统 visuomotor policy 直接从观测到动作；VLA 则把视觉语言先验接入可执行 action contract。区别不只是多一个 head，输出还必须经过表示、反归一化和 controller，在闭环中真正执行。

**机制展开（约 2 分钟）**：RT-2/OpenVLA 把动作编码成 token，让 VLM 用 next-token prediction 学 policy；π0 则用 VLM context 条件化连续 action expert。完整执行策略还包含 preprocess、decode、denormalization、valid-dimension slicing 与 controller。若模型只输出“向左移动”而没有物理 action schema，它更像 semantic planner，不是完整低层 VLA。语言无关、数据少或延迟严格时，小型专用 policy 也可能更合适。

**项目挂钩**：讲 OpenPiVLA 时先核实本地究竟是 scalar token、FAST、flow 还是自定义 Qwen formatter，再谈项目路线。

**追问树**：什么时候传统 policy 更合适？语义 planner + 低层 policy 算不算端到端 VLA？VLA 的 online 指标应如何设计？

**危险答案**：把 VLA 简化成“VLM 后面接一个 action head”，忽略执行接口。

**来源**：[1][2][4][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ARCH-002</b> · 一个 VLA 的 observation/text/proprio/action 输入输出合同应包含哪些字段？</summary>

**面试意图**：判断你是否会把“多模态”落实成可复现的 tensor 和机器人接口。

**30 秒回答**：输入要报 view、图像预处理/mask、语言模板、proprio 轴序单位与时间戳、可选 history；输出要报 action type、\(H\times d\)、absolute/delta、控制频率、norm/decode、执行前缀 \(K\) 和 controller。H 与 K 必须分开。

**机制展开（约 2 分钟）**：以 control tick 为锚点，图像可取最近时间戳，连续 proprio 插值，action label 构造 H 步窗口且不能跨 episode。OpenVLA 原始旗舰是单主视角 + 语言 → 单步 d 维动作，无 proprio/history；π0 论文是 2–3 图 + language + proprio → H=50 chunk。模型接收到的通常是已对齐数组，时间同步应由 dataset converter 或 environment wrapper 证明。

**项目挂钩**：本地 OpenPiVLA 仍需补 config、dataset schema、norm asset、output transform 和 rollout client，不能从项目名猜合同。

**追问树**：时间对齐在哪里做？缺一张 wrist image 怎么处理？H 与 K 为什么不是同一个参数？

**危险答案**：只报“图像、文本、动作”，不报 shape、时间、mask、单位和执行语义。

**来源**：[2][3][4][6][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ARCH-003</b> · VLM backbone、action expert、policy head 与 controller 分别负责什么？</summary>

**面试意图**：检查你能否沿模型边界追到物理执行，而不是混淆模块职责。

**30 秒回答**：VLM backbone 编码视觉语言；policy head 直接给 action logits/参数，action expert 可独立建模 noisy/latent action；output transform 做 decode、denorm、slice；controller 才产生位置、速度或力矩闭环。整条链才是 policy。

**机制展开（约 2 分钟）**：OpenVLA 没有独立 continuous head，Llama LM head 预测 tail-vocab action tokens，ActionTokenizer 做 scalar 映射。π0 用 PaliGemma prefix 条件化较小 action expert，expert 输出 H×D flow velocity，再由 ODE solver 得到 chunk。无论哪条路，backbone 都不自动定义 axis/unit；controller 也不负责理解任务语言。接口错误与模型能力不足应分层排查。

**项目挂钩**：项目叙述要把上游 VLM、本人修改的 action formatter/head、policy server 和 LIBERO controller 分开标 ownership。

**追问树**：projector 算 action head 吗？action tokenizer 是否可训练？为什么 output transform 也属于 policy contract？

**危险答案**：把 action expert、tokenizer、controller 都称为“action head”。

**来源**：[2][3][4][6][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ARCH-004</b> · 多视角图像、语言与 proprioception 如何进入同一策略？时间对齐在哪里发生？</summary>

**面试意图**：判断你是否理解 modality fusion 之前的数据同步和缺失模态处理。

**30 秒回答**：先按 control tick 对齐相机与 proprio：图像取最近时间戳、连续 state 可插值，缺失 view 用 mask；再编码、投影并由 attention 融合。模型通常只看到已对齐数组，因此同步责任在 dataset converter 或 environment wrapper，不是 Transformer。

**机制展开（约 2 分钟）**：每路 view 必须固定 camera name、颜色空间、resize/flip 和有效 mask；language 还要固定 prompt template 与 truncation；proprio 要报 axis、frame、unit 和 timestamp。窗口构造时需限制最大时间差、处理 episode-end padding，禁止 future leakage。openpi frozen model 有三个 image slots 和 masks；LIBERO 缺右腕图时填 zero image，但 Pi0/Pi0FAST 的 mask 规则不同，不能无条件照抄。

**项目挂钩**：核对 OpenPiVLA 训练图像与 LIBERO eval 是否同样旋转、resize、camera-key 映射和 state 时序。

**追问树**：不同相机频率怎么办？zero image 与 mask false 有何区别？history window 如何避免跨 episode？

**危险答案**：说“把多模态 token concat 就完成对齐”，完全不谈 timestamp。

**来源**：[4][6][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ARCH-005</b> · OpenVLA 如何把视觉语言特征映射成离散 action token，再还原连续动作？</summary>

**面试意图**：检查你能否把 architecture、tokenizer、loss 和 inference 连成一条 code-level 链。

**30 秒回答**：OpenVLA 将 DINOv2+SigLIP 特征投影进 Llama-2；动作按 dataset q01/q99 归一化、clip，再逐维映射到词表尾部。训练做 masked token CE；推理生成 d 个 token，解码并用同一 stats 反归一化成单步 d 维动作。

**机制展开（约 2 分钟）**：论文写 256 bins；frozen code 实际构造 256 个 thresholds，digitize 得到 1..256 并映射尾部 256 IDs。decoder 只有 255 个相邻 centers，\(b=255,256\) 都 clip 到 center 254，因此最高两个 token IDs 重建相同。生成 d 个 token 是一个动作的 d 个维度，不是 H 步 chunk；连续 L1 是 metric，优化目标是 masked token CE。

**项目挂钩**：OpenPiVLA 若使用 FAST 或 JSON serialization，必须明确说它不是原始 OpenVLA scalar tokenizer。

**追问树**：为什么是 256 IDs/255 centers？EOS 是否参加 loss？换 dataset 时为什么必须换 unnorm key？

**危险答案**：说 OpenVLA 直接用 L1 回归连续 action，或把 d 个 token 解释为 d 个时间步。

**来源**：[2][3][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ARCH-006</b> · π0 的 action expert 与 flow-matching action generation 如何连接？</summary>

**面试意图**：检查你能否解释 VLM context、noisy action、velocity target 与 ODE sampling。

**30 秒回答**：π0 用 VLM prefix 条件化 state 和 noisy action chunk；action expert 输出 H×D velocity，训练拟合 flow target；推理缓存 prefix KV，经默认 10 个 Euler steps 将高斯噪声变为连续 chunk。

**机制展开（约 2 分钟）**：论文写 \(A^\tau=\tau A+(1-\tau)\epsilon,\ u=A-\epsilon\)，从 \(\tau=0\) noise 到 1 data。openpi 写 \(x_t=t\epsilon+(1-t)A,\ u=\epsilon-A\)，从 t=1 以负 dt 到 0；令 \(\tau=1-t\)，path point 相同，velocity 与时间方向同时取反，因此等价。frozen loss 对 D、H、batch 求 mean，是否 mask padding dimensions 仍需按具体项目核对。

**项目挂钩**：不能仅因项目名含 π 就声称本地使用相同 action expert、H=50 或 10-step solver。

**追问树**：为什么 action tokens 可双向 attention？paper/code 时间约定为何等价？prefix cache 节省哪部分计算？

**危险答案**：只说“flow 比 diffusion 少几步”，不报 path、target 和 solver。

**来源**：[4][6][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ARCH-007</b> · RT-2、OpenVLA、Octo、π0 的 backbone、action representation 与训练路线如何比较？</summary>

**面试意图**：检查你能否比较机制，而不是只背模型规模或 benchmark 排名。

**30 秒回答**：RT-2/OpenVLA 是语言 action token；Octo 是 readout + diffusion；π0 是 VLM context + continuous flow expert。训练路线和数据 protocol 不同，先比较 action/loss/sampler，再谈 backbone，不能直接横比 success rate。

**机制展开（约 2 分钟）**：RT-2 是 PaLI-X/PaLM-E 的 action-as-token 路线，OpenVLA 延续 scalar tail-vocab token；Octo 用 27M/93M modular transformer、image/T5 tokenizer、readout 与 H×D diffusion；π0 用约 2B PaliGemma context 加约 300M action expert 输出 velocity。回答先报 action unit、loss、sampler，再报 backbone；若没有 local checkpoint，不把项目名归到任何一条。

**项目挂钩**：OpenPiVLA 要用 model class、config、checkpoint 和 output shape 证明是 FAST、Pi0 flow 或自定义 Qwen path。

**追问树**：哪条支持多模态连续动作？Octo 为什么不是 VLM LM head？RT-2 的 cloud 频率能否外推本地？

**危险答案**：把“更大 backbone”当成四种方法的唯一差异，或直接比较未经对齐 protocol 的 success rate。

**来源**：[1][2][4][20][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ARCH-008</b> · VLA 的 token sequence layout、attention mask 和 action positions 为什么会改变 loss 语义？</summary>

**面试意图**：确认你能把信息流和梯度流分开解释。

**30 秒回答**：attention mask 决定能看谁，label/loss mask 决定谁有梯度。OpenVLA 监督 action tail，Octo 监督 readout 后的 diffusion，π0 用 prefix 条件化连续 suffix；错一位就可能把 prompt/EOS 当动作或泄露未来。

**机制展开（约 2 分钟）**：先写 masked CE，再画三种 layout。OpenVLA prompt 与 visual patch labels 为 `IGNORE_INDEX`；Octo observation 只看 task/历史 observation，readout 只读前文和自身，action loss 另用 timestep/action mask；π0 suffix 的 H 个 noisy action 是连续 expert 输入，不是自回归 token labels。因此“被 attend”不等于“被 supervise”。

**项目挂钩**：对本地 formatter 要打印 input IDs、attention mask、loss mask、action positions 和 H/D reshape 的 sentinel batch。

**追问树**：为什么 image patch 不应有 CE？Octo readout 为什么不能被 observation 写回？如何查 off-by-one？

**危险答案**：看到 action 出现在序列里就默认所有位置参加 next-token loss。

**来源**：[2][3][6][20][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ARCH-009</b> · 冻结 VLM、全量微调、LoRA/adapter 与独立 action expert 如何取舍？</summary>

**面试意图**：判断你能否按数据、domain gap、显存和遗忘风险做决策。

**30 秒回答**：新 action head、近似视觉域且数据少时先 head-only/adapter；视觉和动力学明显变时逐步解冻，数据足再 full FT。LoRA 省显存但受 rank/target module 限制；独立 action expert 解耦连续控制容量，却增加 context/采样接口。repo 支持某路线不等于论文主结果或本地训练采用它。

**机制展开（约 2 分钟）**：OpenVLA flagship 是 full 7B FT，但脚本支持 all-linear LoRA；Octo 有 head-only、head-MLP-only、full；openpi 有 full 与 PaliGemma/action-expert LoRA config。要核对 trainable-parameter log、base/adapter revision、rank、target modules、merge 顺序、action expert width 和 joint loss，而不是只看配置名。

**项目挂钩**：若 OpenPiVLA 的 config、显存日志或 diff 缺失，只能给候选方案，不能说本人做过 LoRA 或冻结策略。

**追问树**：什么时候解冻 vision encoder？LoRA rank 太小的症状？为什么 π0 需要小 expert？

**危险答案**：把 LoRA 当作所有 VLA 的默认训练方式，或把 action head 参数变化叫架构创新。

**来源**：[2][7][20][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ARCH-010</b> · 多机器人异构 action space 如何统一表示，并避免 padding 维污染 loss？</summary>

**面试意图**：检查你是否能把“统一 D 维”落实为 schema、mask、loss 与 slicing 合同。

**30 秒回答**：用 P 把真实 d 维写入统一 D 维，用 valid mask 计算 loss，推理再用 S slice 回 d。P/S 不会统一 axis、unit、absolute/delta、rotation 或 gripper polarity，还要有 schema transform。

**机制展开（约 2 分钟）**：Octo 是公开正例：`timestep_pad_mask & action_pad_mask` 进入 MSE/diffusion loss，sample 时用 embodiment action dim 限制 padded diffusion 维。openpi `PadStatesAndActions` 只 zero-pad，而 frozen Pi0 loss 对 configured D mean，属于负例边界。故“推理 slice 掉”不能证明训练 target 未被 padding 污染，denominator 也必须按 valid 元素解释。

**项目挂钩**：本地需要 d/D、P/S、mask 来源、per-axis loss 和 padding sentinel test；没有这些 artifact 就不能声称跨机器人统一完成。

**追问树**：gripper 是否单独统计？padding zero target 与 mask 掉的梯度差别？怎么处理 mobile base？

**危险答案**：只说“把短向量补零，最后 slice”，不提 loss mask 和单位/轴序。

**来源**：[6][7][20][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ARCH-011</b> · VLA 延迟主要来自视觉编码、LLM decoding、action sampling 还是通信？怎样拆分？</summary>

**面试意图**：判断你能否设计可复现 timing，而不是凭经验猜瓶颈。

**30 秒回答**：分层测 capture/preprocess、网络、vision/prefix、token/NFE、postprocess、queue 和 controller，报 warm-up 后 p50/p95。RT-2/FAST 数值只属于指定硬件；openpi timing 仍未拆 vision、sampler、queue。

**机制展开（约 2 分钟）**：token 路线的 N 近似 action token length，FAST 是可变压缩长度，flow/diffusion 是 NFE/denoise steps；是否缓存 prefix、每步跑大 backbone 还是小 expert 决定曲线。要同步 CUDA/JAX device，记录 payload bytes、H/K、dtype、batch、cache、网络 RTT 和 controller wait。否则一次 wall clock 无法区分模型慢还是 transport 慢。

**项目挂钩**：OpenPiVLA 若没有 timing log，只能给 instrumentation plan，不能把 RT-2 的 1–3 Hz 或 FAST 的 100/750 ms 写成本地结果。

**追问树**：为什么 flow 10 step 仍可能比 FAST 快？怎样测 prefix cache？p95 突刺如何定位？

**危险答案**：只测 `policy.infer` 或只看 GPU kernel，就宣称端到端 latency。

**来源**：[1][7][12][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ARCH-012</b> · 如何从论文和仓库核对一个 VLA 的真实 I/O、checkpoint、normalization 与推理合同？</summary>

**面试意图**：考查你是否能建立 paper→repo→checkpoint→runtime 的证据链。

**30 秒回答**：冻结论文/repo 版本，读 model/loss/infer；核对 checkpoint、model class、tokenizer、norm、H/D/K 和 transforms，最后用 sentinel request 回放到 mock controller。缺证据就标未核实，不用模型名或 benchmark 补齐。

**机制展开（约 2 分钟）**：openpi policy loader 从 checkpoint 取 weights 与 norm assets，并按 input repack→normalize→model transform、model output→unnormalize→data/repack output 组合；OpenVLA `unnorm_key` 决定 action dim 和 q01/q99。审计表还要记录 base/adapter revision、image resize/views、sampler/NFE、axis/unit、controller mode、task/trial/seed。论文支持方法，repo 支持实现，checkpoint/runtime 才支持“这一次运行”。

**项目挂钩**：OpenPiVLA 的 checkpoint、Qwen/π class、FAST revision、norm asset、action schema、97.4% summary 和 ownership 都要回到本地文件，不能由本页上游证据代答。

**追问树**：多 dataset norm stats 怎么选？如何证明 output shape 不是 accidental？缺 checkpoint manifest 怎么说？

**危险答案**：拿官方 example config、论文 H=50 或项目页面指标冒充本地运行合同。

**来源**：[2][3][5][6][7][14][20][21][22][23][24][27]　**练习状态**：unseen

</details>

## B. Action representation、tokenization 与 FAST

> 2026-07-19 独立复核已核对 π0.5 hybrid 与 `Pi0FAST` 分叉、FAST paper/Hub 默认值、normalization 外置、token mask/fallback、D/H config override 与 LIBERO replan example；以下题卡仍只代表公共机制，项目 hook 继续要求本地 artifact，状态保持 `unseen/WARN`。

<details class="qa">
<summary><span class="lv lv-l1">L1</span> <span class="freq">P0</span> <b>VLA-ACT-001</b> · 连续回归、离散 token、CVAE、Diffusion 与 Flow action head 各自建模什么？</summary>

**面试意图**：判断你能否先按分布和训练目标分类，再讨论算法名字。

**30 秒回答**：连续回归给确定性 action；离散 token 建模 categorical sequence；CVAE 用 latent 表达序列变化；Diffusion 学条件去噪/score；Flow 学 probability path 的 velocity 并用 ODE 采样。选型看多模态性、延迟、数据和控制频率。

**机制展开（约 2 分钟）**：MSE regression 在多峰标签下可能输出条件均值；token route 可复用 LM CE，但有量化和 autoregressive latency；CVAE 有 posterior collapse 与 train/infer latent gap；Diffusion/Flow 都能生成连续多模态 chunk，但 target、time parameterization 和 sampler 不同。本卷后续卡分别展开 ACT 与 Diffusion，不把 π0 flow 当作所有生成式 policy 的模板。

**项目挂钩**：OpenPiVLA 选型回答应先确认本地 supervision/decoder，再按 latency、H、control rate 和 closed-loop evidence解释。

**追问树**：为什么 MSE 会 mode-average？CVAE 推理时 z 从哪里来？Diffusion 与 Flow 的 target 有何差异？

**危险答案**：用“连续/离散”两类覆盖所有方法，或把 Flow 称为换名字的 Diffusion。

**来源**：[4][7][9][10][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-002</b> · action normalization 与 denormalization 为什么是 VLA 最容易 0-success 的接口之一？</summary>

**面试意图**：检查你是否理解 normalized loss 与 physical execution 之间的断层。

**30 秒回答**：模型在 normalized space 学习，controller 在物理单位执行；stats、axis order、action type 或 inverse 任一错位，都可能 loss 正常却执行错误。因此 normalization 是 checkpoint contract，必须与 output interface 一起版本化。

**机制展开（约 2 分钟）**：OpenVLA 对受管维度做 q01/q99 映射并 clip；openpi quantile transform 不显式 clip，policy 从 checkpoint assets 加载训练 stats，sample 后再 unnormalize。最小测试包括 norm→unnorm round-trip、q01/q99 endpoint、outlier saturation、constant dimension、padding dimension 和 axis impulse。FAST Hub processor 从 DCT 开始，不替调用者完成 normalization。

**项目挂钩**：OpenPiVLA 需要保存实际 asset_id/norm file，并在 LIBERO client 前验证 denorm 后的 7D/目标 action schema。

**追问树**：clip 与 no-clip 各有什么代价？为什么换 robot 不能沿用旧 stats？constant dimension 怎么处理？

**危险答案**：说 normalization 只是优化稳定性，与机器人行为语义无关。

**来源**：[2][3][6][7][8][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-003</b> · quantile/bin action discretization 如何编码？分辨率、饱和和分布漂移有什么代价？</summary>

**面试意图**：考查你能否从公式解释 tokenization 的物理误差，而非只背“256 bins”。

**30 秒回答**：先用每维 q01/q99 把 action 映射到 \([-1,1]\)，再按网格 digitize 成 token；推理取 center 并反归一化。代价是有限 bin 的 resolution error、quantile 外的 saturation，以及换数据/stats 后同一 token 对应错误物理尺度。

**机制展开（约 2 分钟）**：OpenVLA paper 写 256 bins；frozen path 用 256 thresholds 与尾部 256 token IDs，但 decode table 只有 255 个相邻 centers，最高两个编码索引都落到最后 center。单维 normalized quantization error 还会被物理 quantile range 放大。审计时要画每维 histogram/饱和率，测 encode→decode 的 normalized/physical error，并用 held-out/OOD stats 检查 shift。

**项目挂钩**：若本地项目改用 FAST/JSON token，不能继续拿 OpenVLA scalar-bin 误差解释本地结果。

**追问树**：bin 数越多一定越好吗？gripper 需要同样分 bin 吗？如何测 saturation rate？

**危险答案**：只说“256 bins 精度足够”，不说明 range、center 和 controller unit。

**来源**：[2][3][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-004</b> · action token 如何占用语言词表？token offset、vocab collision 和 decode 边界如何检查？</summary>

**面试意图**：判断你是否能审计 action vocabulary，而不把 token ID 当无语义整数。

**30 秒回答**：常见做法是复用 VLM 词表尾部并定义可逆 offset。必须固定 tokenizer/version、action-token 数、special-token 保留区、BOS/EOS 和 loss positions；再用边界值与随机 action 做 encode→ID range→decode round-trip，排除碰撞。

**机制展开（约 2 分钟）**：OpenVLA 用 \(t_i=V-b_i\) 占末尾 256 IDs；openpi FAST 将 BPE token 映到 PaliGemma tail，同时跳过最后 128 special-token slots。两条映射不同。检查至少覆盖最小/最大 bin、未知/EOS、生成截断、错误 unnorm key、tokenizer vocab size变化，以及 malformed FAST sequence。loss mask 还要确保 prompt/image padding 不被当 action target。

**项目挂钩**：若 OpenPiVLA 用 assistant-side JSON/token，需单独验证 formatter、labels、parser 与 vocab contract，不能称为原生 FAST/OpenVLA offset。

**追问树**：为什么 tokenizer 升级会破坏 checkpoint？EOS 是否属于 action loss？FAST token length 为什么可变？

**危险答案**：只要 ID 没越界就认为 decode 正确。

**来源**：[3][6][8][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-005</b> · FAST 解决了逐标量 action tokenization 的什么效率问题？</summary>

**面试意图**：检查你是否理解 FAST 的问题设定，而非只会展开缩写。

**30 秒回答**：高频 action chunk 若逐 timestep/逐 scalar token 化，会产生大量相邻相关 token，模型可能靠复制取得低 CE。FAST 先用 DCT 把轨迹集中到少数低频系数，再量化并用 BPE 合并重复 pattern，减少冗余并提高 token 信息量。

**机制展开（约 2 分钟）**：DCT 是解析变换，把平滑轨迹能量集中到低频；frequency-first flatten 先预测各维整体趋势；round 产生稀疏整数，BPE 再压缩大量 zero 和常见 coefficient pattern。BPE 是 learned component，但 FAST processor 不负责 q01/q99 normalization。它主要改善 token sequence 与学习信号，不保证 physical reconstruction 或 closed-loop success 必然更好。

**项目挂钩**：本地若声称“FAST 提升”，至少要提供 token length、reconstruction、latency 和 rollout ablation，而不只报最终成功率。

**追问树**：为什么先低频更稳定？去掉 BPE 会怎样？FAST 与 OpenVLA scalar token 的基本单位是什么？

**危险答案**：把 FAST 说成对每个 scalar 做更细的 binning。

**来源**：[7][8][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-006</b> · FAST 的频域变换、量化与 BPE 压缩如何形成 action token 序列？</summary>

**面试意图**：考查你能否按 shape 和顺序复述完整可逆 pipeline。

**30 秒回答**：对 normalized \(H\times D\) chunk 的每维沿时间做 DCT，系数乘 scale 后 round；按 frequency-first 展平，再用 BPE 编成可变长 token。解码反向执行 BPE inverse、reshape、除 scale、IDCT，最后再 denormalize。

**机制展开（约 2 分钟）**：frozen Hub code 对 [B,H,D] 在 time axis 做 DCT，row-major flatten 实现“所有维度低频在前”。FAST paper 单数据集实验是 scale=10、vocab=1024；frozen FAST+ Hub artifact 是 scale=10、vocab=2048；openpi Pi0FASTConfig default H=32,D=32，LIBERO example H=10,D=7。默认值必须连同对象/version 回答，reshape 失败应显式报错。

**项目挂钩**：核对 OpenPiVLA 保存的 tokenizer revision、scale/vocab、H/D 与 norm stats，避免依赖未 pin 的 Hub default。

**追问树**：为什么 flatten order 重要？scale 如何影响重建/压缩？BPE 是有损还是无损步骤？

**危险答案**：把 paper 1024、Hub 2048 和 model H/D 混成一个“FAST 默认配置”。

**来源**：[7][8][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ACT-007</b> · FAST 的 token compression 为什么不等于物理控制误差一定更小？</summary>

**面试意图**：判断你能否区分表示压缩、离线误差和闭环成功率。

**30 秒回答**：token 少只说明 sequence 更短，不直接约束 IDCT 重建误差；normalized error 还会被 quantile range 放大成物理误差，controller/replan 又会改变闭环结果。因此要分报压缩率、重建、CE、延迟、物理轨迹误差和成功率。

**机制展开（约 2 分钟）**：round scale 决定有损精度，BPE 主要无损合并整数 pattern；低频优先可能改善 AR 学习，但 tokenizer reconstruction 好不代表 policy 预测对，policy offline 对也不代表 denorm/axis/controller 对。FAST 论文的 no-BPE 消融说明 BPE 在其任务上有帮助，不能推成所有 robot/checkpoint 的因果保证。选型还要与 scalar token、flow 的同协议 baseline 比较。

**项目挂钩**：97.4% 若无 tokenizer ablation、相同 checkpoint/protocol 和失败分解，不能单因果归因给 FAST。

**追问树**：应该画哪些曲线？physical error 如何按 semantic group 报告？token 更短为何可能重建更差？

**危险答案**：把压缩率提升直接翻译为成功率提升。

**来源**：[7][8][12][13][14]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-008</b> · action dimension、padding、mask 和 output slicing 如何写成可验证的张量合同？</summary>

**面试意图**：检查你是否会区分 model capacity、有效监督和环境动作。

**30 秒回答**：设真实 action 为 d 维、model 为 D 维，输入用 \(P=[I_d;0]\) 补到 D，输出用 \(S=[I_d,0]\) 取回 d，且 \(SP=I_d\)。训练还需 valid mask 排除无语义维度和越界 horizon；推理 slicing 不能证明 loss 已 mask。

**机制展开（约 2 分钟）**：要分别记录 image mask、token input mask、token loss mask 和 action valid-dim/horizon mask。openpi `PadStatesAndActions` 可补 state/action，LIBERO output transform 切前 7 维；frozen π0 main loss 对 D 直接 mean，所以某个项目若 D>d，要证明 padding target 为零是否有意，或提供实际 loss mask。还需测试 episode-end window、不同 embodiment 的有效维和 batch broadcasting。

**项目挂钩**：OpenPiVLA 必须给出 local D、LIBERO d、padding 位置、loss 维度和 output parser 单测。

**追问树**：padding target 监督为零与 mask 掉有何不同？rotation/gripper 可否不连续排列？multi-embodiment mask 怎么存？

**危险答案**：说“最后 slice 掉 padding，所以训练不会受影响”。

**来源**：[6][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ACT-009</b> · 平移、旋转、gripper 与 base action 应如何表示和归一化？</summary>

**面试意图**：判断你是否会先定义物理语义，再谈网络输出。

**30 秒回答**：先报 action 的 type、frame、unit 和时间语义：translation 区分 absolute/delta/velocity；rotation 说明表示；gripper 说明 absolute/binary/delta；base 说明 velocity frame。统计逐维保存、按语义组审计。

**机制展开（约 2 分钟）**：translation 要区分 meter、每 tick delta 与每 second velocity；rotation 要处理 Euler singularity、axis-angle branch、quaternion unit norm/双覆盖或 6D 正交化；gripper 常为 [0,1] absolute，可能需要独立 mask/loss；base 要说明 \(v_x,v_y,\omega_z\)、frame 和安全限幅。相同 8D shape 可分别表示 pose delta 或 7 joint velocities+gripper，shape 对齐不等于 controller contract 对齐。

**项目挂钩**：本地 OpenPiVLA action schema 未核实前，只能列待查 axis/unit，不能从 LIBERO 7D 或 openpi 默认 layout 反推。

**追问树**：quaternion 为什么要 canonicalize sign？delta 与 velocity 如何用 \(\Delta t\) 转换？gripper 为什么常单独处理？

**危险答案**：看到 7D/8D 就直接说 xyz + rotation + gripper。

**来源**：[3][6][11][12][13]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-010</b> · 如何按多模态性、延迟、数据量和 controller 频率选择 action representation？</summary>

**面试意图**：考查你能否从需求做系统选型，而不是按论文热度排序。

**30 秒回答**：先锁 action type、d、H、控制频率和 replan budget，再判断 action 是否多模态。近单峰、低延迟先做 regression；复用 VLM AR head 可选 scalar/FAST token；连续多峰再比较 CVAE、Diffusion、Flow，并用重建、延迟和闭环成功联合验收。

**机制展开（约 2 分钟）**：scalar token 简单但有量化/AR latency；FAST 适合高频 chunk token route，但依赖 H/D/tokenizer revision；CVAE 关注 latent train/infer gap；Diffusion/Flow 有迭代 sampling，需比较 target、steps、action expert 和通信开销。数据有限时复杂生成 head 未必占优；controller 高频时必须看每 chunk 推理、执行 K 与网络抖动。所有选择都应保留 direct regression 或简单 token baseline。

**项目挂钩**：项目回答用同一 protocol 比较候选路线；没有 ablation 时只讲设计理由，不把最终分数强归因给表示。

**追问树**：多模态性如何从数据诊断？控制频率升高时 FAST/Flow 怎样变化？为什么需要 simple baseline？

**危险答案**：说“最新模型一定最好”，或只比较 offline loss。

**来源**：[4][7][9][10][12][13][14]　**练习状态**：unseen

</details>

## C. ACT、Action Chunking 与 Temporal Ensemble

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-011</b> · action chunk、prediction horizon、execution window 与 replan interval 有何区别？</summary>

**面试意图**：检查你是否会把 model shape、执行队列和反馈频率分开。

**30 秒回答**：\(H\) 是一次预测的 chunk 长度，\(K\) 是实际执行的前缀，\(R\) 是两次 policy query 间隔，\(\Delta t\) 是控制周期。它们可以不同；一次输出 H 步不等于必须 H 步后才重新观测。

**机制展开（约 2 分钟）**：冻结 ACT 无 temporal aggregation 时把 \(K=R=H\)：每 H 步 query 并消费整段；开启后 \(K=R=1\)，但 model H 不变。概念上异步 queue 还能让 K 与 R 解耦。episode T 步时，整段执行约需 \(\lceil T/H\rceil\) 次 inference；反馈 staleness 与 R、\(\Delta t\) 共同决定。

**项目挂钩**：OpenPiVLA 必须从 local model config、client queue 和 controller loop 分别取 H/K/R，不能用 official example 代证。

**追问树**：K<R 或 R<K 可否存在？H=50、K=5 表示什么？网络延迟应算在哪一层？

**危险答案**：把 horizon、返回 action 数、replan 和控制频率称为同一个参数。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-012</b> · ACT 的 CVAE-Transformer 如何一次预测 action chunk？</summary>

**面试意图**：考查你能否按 train/infer 输入与 tensor shape 解释 ACT，而非只说“Transformer + chunk”。

**30 秒回答**：训练 posterior 用 `[CLS]+qpos+target actions` 得到 32D latent；decoder 融合共享多相机特征、qpos、latent 和 H 个 learned queries，一次并行输出 `[B,H,14]`，不是自回归 token decoding。

**机制展开（约 2 分钟）**：posterior encoder 为加速不看图像；decoder 的相机共享 ResNet18，feature 沿 width 拼接，latent/qpos 作为额外 token。`nn.Embedding(num_queries,hidden_dim)` 提供 H 个输出槽，action head 每槽输出 14D。论文把 query 描述成 fixed/sinusoidal，但 frozen commit 实际 learned；`is_pad_head` 未进入 loss/推理。

**项目挂钩**：若本地使用 Qwen/π action expert，ACT 只能作为 action-chunk baseline，不能写成本人架构。

**追问树**：posterior 为什么不看图像？H 个 query 是否 autoregressive？14D 能否迁移到 LIBERO 7D？

**危险答案**：说 ACT 逐步生成 H 个 token，或说 frozen queries 是固定正弦位置。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-013</b> · ACT 的 latent/style variable 在训练和推理时如何使用？</summary>

**面试意图**：检查你是否理解 CVAE posterior、KL 和部署多模态性的边界。

**30 秒回答**：训练时 posterior 看 qpos 和 target chunk，输出 \(\mu,\log\sigma^2\)，重参数采样 z，并用 L1 + \(\beta\)KL；冻结推理不跑 posterior，也不随机采样，而固定 \(z=0\)，因此 evaluation 是 deterministic。

**机制展开（约 2 分钟）**：z 为 32D style latent，KL 将 posterior 拉向单位高斯。训练 action target 可见、推理不可见形成 train/infer gap；固定 prior mean 提高可复现性，却不等于部署会探索多个 demonstration mode。论文 Algorithm 1 写 MSE，但方法正文与 frozen `policy.py` 用 masked L1；公开 \(\beta=10\) 不是通用常数。

**项目挂钩**：项目若声称 CVAE 多模态部署，要给出实际 z sampling/selection code 和 rollout ablation。

**追问树**：posterior collapse 怎么看？为什么 \(z=0\) 是 prior mean？随机采 z 有何安全风险？

**危险答案**：说 ACT 推理会采多个 style latent 后自动选出最好 chunk。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ACT-014</b> · temporal ensembling 如何融合不同时间预测的同一步动作？</summary>

**面试意图**：判断你是否能区分 same-target ensemble 与相邻动作 smoothing。

**30 秒回答**：每个 query 预测未来 H 步；当前物理时刻 t 会被过去最多 H 个 chunk 覆盖。temporal ensemble 只融合这些对同一 \(a_t\) 的估计，不平均 \(a_{t-1},a_t,a_{t+1}\)。

**机制展开（约 2 分钟）**：代码把 query q 的 chunk 写到 `all_time_actions[q,q:q+H]`，再读 column t。按 oldest-to-newest 排列后用 \(w_i=e^{-mi}\) 加权；frozen `m=0.01` 且 oldest row 对应 i=0，所以最旧预测权重最大。这样避免普通时域 smoothing 的 phase shift，但快速变化时也可能保留 stale plan。

**项目挂钩**：若本地实现 overlapping chunks，要用 synthetic table 验证 query/target 轴、权重顺序和有效 sentinel。

**追问树**：为什么最旧预测权重更大？m 越大怎样？zero sentinel 有什么风险？

**危险答案**：说它给最新预测最高权重，或说它平滑相邻物理时刻的动作。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-015</b> · chunking、replanning 与 temporal ensembling 如何共同影响闭环性？</summary>

**面试意图**：检查你能否从预测表示走到在线反馈与计算代价。

**30 秒回答**：chunking 决定一次预测 H 步，replan 决定多久吸收新观测，ensemble 融合重叠 chunk 对同一时刻的估计。ACT 可 H 步 query/整段执行，也可每步 query/ensemble；H 不随之变成 1。

**机制展开（约 2 分钟）**：整段模式 query 少、chunk 内 sequence coherence 强，但反馈只在边界进入；aggregation 模式每步 query，执行当前融合 action，闭环更强却把 inference 次数从约 T/H 提到 T，并维护 H 长 overlap buffer。平滑不等于安全：多个一致但错误的预测仍会被融合。真实系统还要报告 K/R、queue reset 与 latency。

**项目挂钩**：将 OpenPiVLA 的 action chunk queue 与 ACT 两种模式做结构对照，但不假定采用 temporal ensemble。

**追问树**：每步 query 是否一定更好？异步 server 怎么做 overlap？episode reset 要清什么状态？

**危险答案**：说 action chunking 天然 open-loop，或 temporal ensemble 不增加 inference 成本。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ACT-016</b> · chunk 太长或太短分别导致什么误差、延迟和吞吐问题？</summary>

**面试意图**：考查你是否能把 horizon 选型转成可测 trade-off。

**30 秒回答**：H 太短会频繁 query、缺少长程 coherence；H 太长会让 chunk 尾部 stale、长序列更难建模并增加 query-slot 计算。最优值依赖控制周期、K/R、扰动和 latency，不能背成固定 100。

**机制展开（约 2 分钟）**：无 aggregation 时最大反馈等待约 \((H-1)\Delta t\)，query 数约 T/H。H=1 反馈最快但 policy calls 最大；大 H 降低调用数，却让早期误差污染后半段。ACT 论文在其特定 ablation 中 H=100 最好、200/400 略降，只证明该协议的折中。开启 aggregation 可降反馈间隔，却恢复每步 inference。

**项目挂钩**：本地 sweep 必须固定 checkpoint、controller、task/trials，联合画 latency、physical error 和 success。

**追问树**：控制频率翻倍时 H 怎么理解？K<H 能缓解什么？如何测 stale tail？

**危险答案**：把 ACT 的 H=100 写成所有机器人和 VLA 的最优 horizon。

**来源**：[9][15][25]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-017</b> · ACT 与 autoregressive token、Diffusion/Flow policy 的归纳偏置如何比较？</summary>

**面试意图**：判断你是否能比较 target、生成计算、多模态和闭环，而非按论文新旧排序。

**30 秒回答**：ACT 用 L1+KL 一次并行出 continuous chunk，冻结推理 z=0；token 路线用 CE 自回归；Diffusion 预测 epsilon/sample 走 scheduler；Flow 预测 velocity 解 ODE。选型要联合看多模态、NFE/AR 延迟和 H/K/R。

**机制展开（约 2 分钟）**：ACT 无量化和多步 sampler，适合低 inference-step chunking，但 test 随机性弱；scalar/FAST token 复用 LM，却有量化或 AR token latency；Diffusion/Flow 从 Gaussian 初始化，显式建连续多峰，但每 query 多次 network evaluation。比较需固定数据、backbone、action schema、controller 和 trial protocol，不能用跨论文成功率下结论。

**项目挂钩**：OpenPiVLA 只在 local model/target/decoder 取证后选择对应比较列，未做 ablation 时只讲设计理由。

**追问树**：哪条路线最容易 mode-average？ACT 为什么不等于 deterministic regression？Flow 与 Diffusion 只差步数吗？

**危险答案**：说 ACT 是 diffusion 的单步版本，或说生成式方法天然闭环更强。

**来源**：[9][10][15][16][17]　**练习状态**：unseen

</details>

## D. Diffusion Policy 与 Receding-Horizon

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-018</b> · Diffusion Policy 为什么对多模态连续动作有吸引力？</summary>

**面试意图**：检查你是否理解 sequence-level stochastic generation，而非只会说“扩散能多模态”。

**30 秒回答**：它把整个 \(T_p\times D_a\) continuous trajectory 作为联合随机变量，从 Gaussian trajectory 条件去噪。不同初始噪声可落到不同动作 mode，temporal network 又让同一 mode 内的动作序列保持连贯。

**机制展开（约 2 分钟）**：policy 建模 \(p_\theta(A_t\mid O_t)\)，不是逐时刻独立分布乘积；UNet/Transformer 每步处理 `[B,Tp,Da]`。这避免 deterministic MSE 在多峰标签下只给条件均值，但不保证线上必须随机：固定 seed、DDIM、smoothing 和执行窗口都会改变 diversity。还需用 closed-loop success 验证 mode 是否可执行。

**项目挂钩**：本地若声称多模态收益，要固定 observation，用多 noise sample 展示连贯候选并做 success/安全分析。

**追问树**：联合 trajectory 与逐步独立有何区别？固定 seed 还多模态吗？怎样避免 unsafe mode？

**危险答案**：说每个 action timestep 独立采一个 Gaussian，所以能多模态。

**来源**：[10][16][26]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-019</b> · conditional DDPM action objective 中的 noisy action、noise target 与 condition 是什么？</summary>

**面试意图**：考查你能否把加噪公式、target 和 tensor condition 对到代码。

**30 秒回答**：对 clean trajectory \(A^0\) 随机选 k，用 schedule 得到 \(A^k=\sqrt{\bar\alpha_k}A^0+\sqrt{1-\bar\alpha_k}\epsilon\)。默认模型以最近 \(T_o\) 帧视觉/state 为 condition，预测同形状 epsilon，做 MSE。

**机制展开（约 2 分钟）**：frozen image-hybrid 默认把前 To 帧过 encoder 后 flatten 为 `global_cond`，diffusion trajectory 只含 action channels `[B,Tp,Da]`。`add_noise` 构造 noisy sample，prediction type=epsilon 时 target 是 noise；sample 时 target 是 clean trajectory。condition mask 与 valid padding mask 不同，default global action mask 全 false。

**项目挂钩**：审计本地 target builder 时固定一组 clean/noise/k 手算 `add_noise` 与 MSE target。

**追问树**：\(\bar\alpha_k\) 从哪里来？condition 是否拼进 action channel？sample target 有何变化？

**危险答案**：说默认 MSE 直接回归 clean action，或把 observation 当 noise target。

**来源**：[10][16][26]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-020</b> · noise schedule、prediction type 和 action horizon 如何影响训练与采样？</summary>

**面试意图**：判断你是否会分开 scheduler、监督参数化和机器人时间轴。

**30 秒回答**：schedule 决定每个 k 的信噪比与 reverse 系数；prediction type 决定模型学 epsilon 还是 clean sample；\(T_p\) 决定 trajectory 长度。它们还要与 \(T_o,T_a\)、replan interval 和去噪步数 \(K_d\) 分开。

**机制展开（约 2 分钟）**：frozen policy 只实现 epsilon/sample target；dependency 虽支持 v_prediction，policy target builder 没有对应分支。Tp 变长增加 sequence compute 并可能让尾部 stale，Kd 决定每次 query 的 scheduler iterations。boundary sampler 会重复首尾 target，且 policy 拒绝 valid_mask，所以 padding 行为也会改变 loss。必须锁 diffusers 版本与 runtime override。

**项目挂钩**：本地 manifest 应一起记录 scheduler config、prediction type、Tp/To/Ta、Kd 和 controller replan。

**追问树**：只把 config 改成 v_prediction 会怎样？Tp 与 Kd 哪个是控制步？padding 怎么进 loss？

**危险答案**：把 diffusion timesteps、prediction horizon 和 action execution steps 混为一谈。

**来源**：[10][16][26]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-021</b> · receding-horizon action diffusion 如何执行 chunk 并重新观测？</summary>

**面试意图**：检查你能否从 \(T_o/T_p/T_a\) 走到真实 wrapper/queue。

**30 秒回答**：policy 用最近 \(T_o\) 帧生成 \(T_p\) 步 trajectory，从 index \(T_o-1\) 起切出 \(T_a\) 步并反归一化；simulation 通常执行这段后重观测。real queue 可能提交更长，但 query interval 另由调度器决定。

**机制展开（约 2 分钟）**：global path 从 `[B,Tp,Da]` Gaussian 开始，完成 Kd 次 reverse step 后 slice `To-1:To-1+Ta`。PushT runner 把返回 batch 交给 `MultiStepWrapper` 逐步执行；real script 可提交 timestamped actions，并按 `steps_per_inference` 重新 query。返回 15 步不等于一定 15 步后才重规划。

**项目挂钩**：OpenPiVLA client 要分别记录 model H、returned slice、submitted queue 和 actual executed-before-replan。

**追问树**：为什么 slice 从 To-1 开始？sim/real 有何区别？controller 超时如何处理？

**危险答案**：看到 horizon=16 就断言每次执行 16 步。

**来源**：[10][16][26]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ACT-022</b> · 去噪步数、sampler 与 warm start 如何影响策略延迟和稳定性？</summary>

**面试意图**：判断你是否会保留 paper/config/runtime 差异并做部署权衡。

**30 秒回答**：\(K_d\) 越少通常更快，但 reverse approximation 可能变差；DDPM/DDIM 的随机性和 time grid 不同。论文说可 warm-start，但 frozen policy 每次从 `torch.randn` 重启并拒绝 `past_action`。

**机制展开（约 2 分钟）**：DDIM 可用抽稀 inference grid，不能说训练也只剩 8 步。版本中 paper 正文/表格、config、runtime 分别出现 10/16/8/16 steps，回答必须带对象。warm-start 若补做，要 shift 未执行 trajectory、匹配新 observation 和 scheduler noise level；它可能降抖动/计算，也可能把 stale plan 带进下一轮。

**项目挂钩**：本地用 fixed observation/noise sweep Kd，记录真正 model forwards、latency、trajectory error 与 closed-loop success。

**追问树**：DDIM 是否必然 deterministic？warm-start 从哪个 noise level 开始？NFE 与 controller step 怎么拆？

**危险答案**：说代码默认 warm-start，或把 100 train timesteps 当成 100 个机器人控制步。

**来源**：[10][16][26]　**练习状态**：unseen

</details>

## E. Flow Matching、π0 与生成式 Action Debug

> 2026-07-19 独立复核已直接核对 Theorem 2、paper `sigma_min` endpoint、π0/OpenPI time-sign-dt、shifted Beta 换元与 10-step oracle；以下八卡的通用机制口径通过，但项目 runtime 与真实口述仍为 `WARN/unseen`。

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ACT-023</b> · Flow Matching 的 probability path 与 velocity field 直觉是什么？</summary>

**面试意图**：检查你能否区分分布路径、sample trajectory、target field 和网络输出。

**30 秒回答**：probability path \(p_t\) 描述分布从 noise 到 data 如何变化；velocity field \(u_t(x)\) 描述位于 x 的样本此刻该往哪里走。模型 \(v_\theta\) 拟合这个速度，推理解 ODE transport noise。

**机制展开（约 2 分钟）**：CNF 满足 \(d\phi_t(x)/dt=v_t(\phi_t(x))\)，且 \(p_t=[\phi_t]_*p_0\)。直接 marginal field 难算，CFM 对每个 data endpoint 设计 conditional path/velocity；Theorem 2 在 \(p_t(x)>0\) 的假设下证明两项目标相差参数无关常数，因此梯度相同，不是逐样本 loss 相同。“simulation-free”只指训练无需先跑 ODE，采样仍要 solver。

**项目挂钩**：本地 action head 必须找到 path builder、velocity target、time sampler 和 solver，不能只凭项目名认定是 Flow。

**追问树**：path 与 trajectory 有何区别？CFM 为什么可训练？推理为什么仍迭代？

**危险答案**：说 Flow Matching 直接回归 clean action，或 simulation-free 表示推理一步完成。

**来源**：[17][18][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-024</b> · 线性插值路径下 target velocity 和 flow-matching loss 如何推导？</summary>

**面试意图**：考查你能否从 path 求导，并保留 paper/package endpoint 差异。

**30 秒回答**：exact-linear path 是 \(x_t=(1-t)x_0+tx_1\)，对 t 求导得 \(u_t=x_1-x_0\)，因此 CFM loss 是 \(\mathbb E\|v_\theta(x_t,t)-(x_1-x_0)\|^2\)。

**机制展开（约 2 分钟）**：现代 `CondOTProbPath` 用 \(\alpha=t,\sigma=1-t\)。但基础论文 OT path 是 \(x_t=[1-(1-\sigma_{\min})t]x_0+tx_1\)，target 为 \(x_1-(1-\sigma_{\min})x_0\)，endpoint 仍有小 Gaussian noise。线性 target 对一对 endpoints 为常量，不代表 marginal field 全局常量。

**项目挂钩**：把 \(x_1\) 换成 normalized \(H\times D\) action chunk 前，先核本地是否 exact endpoint、time weighting 和 valid mask。

**追问树**：\(\sigma_{\min}\) 为何保留？target 为什么不依赖 t？conditional 与 marginal field 怎么区别？

**危险答案**：说所有 Flow Matching 都是 exact-linear path，或原论文必然令 \(\sigma_{\min}=0\)。

**来源**：[17][18][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-025</b> · Flow policy 推理时如何通过 ODE solver 从 noise 得到 action chunk？</summary>

**面试意图**：检查你是否会把 velocity、time grid、NFE 与 action horizon 分开。

**30 秒回答**：先采同形状 Gaussian action chunk，再沿 time grid 多次算 \(v_\theta(x_k,t_k,c)\)，用 Euler 等更新 \(x_{k+1}=x_k+\Delta t v_\theta\)，终点才是 normalized action chunk。

**机制展开（约 2 分钟）**：solver 可 fixed-step Euler/Heun，也可 adaptive method；要报 grid、step、tolerance 和 NFE。openpi 从 code time t=1 noise 以负 dt 到 0 data，默认 10 Euler steps，并缓存视觉语言 prefix、每步重算 action suffix。10 是 integration steps，不是 H、K 或 controller steps。

**项目挂钩**：本地记录 solver runtime override、fixed-noise output、每 NFE latency、unnorm 和执行前缀。

**追问树**：高阶 solver 能修复 target sign 吗？NFE 与 H 有何关系？adaptive solver 如何复现？

**危险答案**：把 10 次 Euler 说成一次输出 10 个 action，或漏掉终点仍需 unnormalize。

**来源**：[4][6][17][18][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-026</b> · Diffusion noise prediction 与 Flow velocity prediction 的目标和采样有何区别？</summary>

**面试意图**：判断你是否能按 target/time/sampler 对照，而不是只比较步数。

**30 秒回答**：冻结 Diffusion Policy 在离散 k 上默认预测 epsilon，由 DDPM/DDIM scheduler 更新；Flow 在连续 t 上预测 probability path velocity，由 ODE solver 更新。两者都可从 Gaussian chunk 开始，但合同不同。

**机制展开（约 2 分钟）**：Diffusion objective 是 \(\|\epsilon-\epsilon_\theta(O,A^k,k)\|^2\)；Flow 是 \(\|u_t-v_\theta(o,x_t,t)\|^2\)。FM 可选 diffusion probability path，所以两类理论有联系，但 prediction parameterization 和 sampler 不能混用。步数不是本质：DDIM 可少步，Flow 也可多 NFE；延迟还取决于 model size 和 prefix。

**项目挂钩**：比较本地路线时固定 backbone/data/action schema/controller，分别锁 scheduler 或 solver 和 sampling budget。

**追问树**：都用 MSE 为什么 target 不同？Flow 一定更快吗？v_prediction 属于哪类参数化？

**危险答案**：说 Flow 只是少几步的 Diffusion，或二者完全无关。

**来源**：[10][16][17][18]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-027</b> · π0 如何把 VLM context、state 与 noisy action 输入 action expert？</summary>

**面试意图**：考查你能否把 π0 architecture、tensor shape、time recipe 与 openpi code 对齐。

**30 秒回答**：图像和语言组成 VLM prefix；state、`[B,H,D]` noisy actions 与 flow time 组成 suffix，action expert 输出同形状 velocity。采样时 prefix KV 缓存，每个 Euler step 只重算 suffix。

**机制展开（约 2 分钟）**：paper 写 \(A^\tau=\tau A+(1-\tau)\epsilon,\ u=A-\epsilon\)，从 noise 0 到 data 1；openpi 写 \(x_t=t\epsilon+(1-t)A,\ u=\epsilon-A\)，从 t=1 负步长到 0。令 \(\tau=1-t\)，time 和 velocity 同时翻转而 trajectory 等价。code 的 shifted Beta time也在该换元下对应论文 recipe。

**项目挂钩**：OpenPiVLA 必须用 local class/forward 证明采用 action expert，不能由 π/FAST 名称或 Qwen backbone 推断。

**追问树**：state 在 π0/π0.5 怎样不同？为什么 prefix 可缓存？Beta time强调哪一区域？

**危险答案**：只说 paper/code 时间相反，不说明 velocity sign 与 \(d\tau=-dt\)。

**来源**：[4][6][17]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-028</b> · action loss mask、有效维度与 padded model dimension 如何避免错误监督？</summary>

**面试意图**：检查你是否会区分 padding、attention mask、loss mask 和 output slicing。

**30 秒回答**：真实 d 维补到 model D 维后，训练应由 action-valid mask 决定哪些 horizon/axis 进 loss；推理 slice 只控制输出，不能替代训练 mask。mask denominator 也要按有效元素归一化。

**机制展开（约 2 分钟）**：理想 loss 是 \(\sum m(v-u)^2/(\sum m+\epsilon)\)。frozen Pi0 对 configured D 直接 mean，训练再平均 batch/H；若 D>d，padding zero targets 仍进 gradient 和 denominator，可能稀释有效轴误差。`PadStatesAndActions`、image/token attention mask、token loss mask、action valid mask 和 output slice 是不同层。

**项目挂钩**：本地需给出 d/D、mask 来源、episode-end slots、per-axis loss 和 output parser 单测。

**追问树**：监督 padding 为零与 mask 掉有何区别？denominator 为什么重要？multi-embodiment 怎么存 mask？

**危险答案**：说推理最后 slice 掉 padding，所以训练不会受影响。

**来源**：[6][17]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P2</span> <b>VLA-ACT-029</b> · conditional dropout / guidance 在 action generation 中何时有意义，风险是什么？</summary>

**面试意图**：判断你能否从通用 CFG 机制落到 action safety/latency，而不虚构 openpi 功能。

**30 秒回答**：训练可随机 drop task condition，推理用 \(v_{\rm cfg}=(1+s)v_{\rm cond}-sv_{\rm uncond}\) 强化条件遵循；但每 NFE 约双倍 forward，过强 guidance 还可能放大动作、破坏平滑或安全。

**机制展开（约 2 分钟）**：现代 flow package 的 image example 支持 class dropout/CFG，但 frozen openpi Pi0 没有对应 action branch。迁移时要定义只 drop language、保留 image/state，还是完全 unconditional；同时评估 task compliance、diversity、action magnitude、smoothness、success 和真实 model forwards。不能只复制 guidance scale。

**项目挂钩**：除非 local config/code/ablation 存在，只把 CFG 作为可补做设计，不写成已完成贡献。

**追问树**：为什么不能 drop proprio？CFG scale 越大越好吗？NFE counter 会漏算什么？

**危险答案**：因为官方 flow package 有 CFG，就说 π0/openpi 默认启用 guidance。

**来源**：[17][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-ACT-030</b> · Flow/Diffusion loss 正常但 rollout 失败时，如何区分 target、scheduler、normalization 与 controller 问题？</summary>

**面试意图**：考查你能否按 causal distance 调试 0-success，而不是直接归因数据或模型容量。

**30 秒回答**：按四层查：先手算 target/path，再用固定 noise 查 solver/scheduler；随后做 norm、mask、axis/unit round-trip；最后 bypass model 验证 H/K/R、queue 与 controller。每层先建立不变量。

**机制展开（约 2 分钟）**：Flow 用 oracle velocity 验证 endpoint、time/sign/NFE；Diffusion固定 clean/noise/k 核 `add_noise`、prediction type 和 step order。再 overfit tiny batch、测 q01/q99 或 min/max inverse、d/D/padding、per-axis sentinel。最后直接执行已知安全 action，查 camera/state timestamp、queue、clip和 success predicate。loss 只证明 normalized target fit。

**项目挂钩**：把每层结果存为 test/log artifact并绑定 exact checkpoint；缺证据时只说待核实，不能把 upstream bug 当本人修复。

**追问树**：为什么先 oracle 再训练？步数增大仍发散先查什么？如何隔离 controller？

**危险答案**：看到 loss 正常就跳到“数据不够”，或先调 learning rate 而不查 action contract。

**来源**：[16][17]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-031</b> · 模型输出如何经过 slicing、denormalization、坐标/单位转换进入 controller？</summary>

**面试意图**：检查你能否把 model-space tensor 追到物理执行边界。

**30 秒回答**：依次做 token/FAST/flow decode、checkpoint unnorm、valid-dim slice、absolute/delta 与 axis/frame/unit 映射，再安全投影进 controller。每步都要有 shape、单位和 sentinel trace；output shape 不是 controller 语义。

**机制展开（约 2 分钟）**：可写成 \(a^{ctrl}=\Pi(R(S(U(D(z)))))\)。OpenVLA 是 token→normalized scalar→q01/q99；Octo 会按 embodiment action dim slice 后 unnorm；openpi 按 model/data output transforms→Unnormalize→repack，DROID example 还二值化 gripper、clip `[-1,1]`、按频率 `env.step`。delta→absolute 要用正确 state/frame，rotation 可能要在 \(SO(3)\) 上 composition；local axis/unit/controller 仍需 artifact。

**项目挂钩**：OpenPiVLA 的 output transform、norm stats、axis order、H/K 与 controller wrapper 任何一项缺失，都只能说待核实。

**追问树**：为什么不能先 clip 再 denorm？gripper 要不要单独处理？如何证明 slice 不是错轴？

**危险答案**：说模型直接输出 controller command，或用 upstream DROID 的 8D 例子代替本地 schema。

**来源**：[2][6][7][14][20][21][22][27]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ACT-032</b> · 如何为 action parser、chunk queue、replan 与安全裁剪设计最小闭环单测？</summary>

**面试意图**：判断你是否能用可辨识输入测试组合接口，而不是只 assert tensor shape。

**30 秒回答**：用 prime/one-hot sentinel 测 token、norm、padding、axis/unit、FIFO、K 边界、reset、stale RPC、NaN/超限和 mock step。断言每步只消费一次、旧 chunk 不泄漏、无效维不进 loss/输出、最终动作满足安全规则。

**机制展开（约 2 分钟）**：先构造 H×D 每行每维不同的 chunk；parser 检查 EOS/越界，unnorm 检查逆变换，slice 检查 valid d，axis impulse 检查 frame/unit；broker 在 K 步后重新 query，乱序 response 依 request id 丢弃，NaN/Inf 进入 fail-safe。openpi broker 的公开测试只验证 chunk shape，因此项目还必须补这些不变量和一次真实/仿真 controller `step`。

**项目挂钩**：测试产物要绑定 tokenizer/norm/config/checkpoint revision，并记录输入 sentinel、输出 action、控制 dt、触发 safety 规则和日志路径。

**追问树**：H=10/K=5 怎么测？怎样测试 reset 清空 queue？为什么不能依赖 `np.clip` 处理 NaN？

**危险答案**：只写一个 shape assert，或把成功 rollout 当作 parser/安全单测。

**来源**：[6][7][14][20][21][22][27]　**练习状态**：unseen

</details>

## 参考来源

1. Brohan et al., [RT-2](https://arxiv.org/abs/2307.15818), 2023.
2. Kim et al., [OpenVLA](https://arxiv.org/html/2406.09246v3), arXiv v3, 2024.
3. [openvla/openvla](https://github.com/openvla/openvla/tree/c8f03f48af692657d3060c19588038c7220e9af9), frozen commit `c8f03f48af692657d3060c19588038c7220e9af9`.
4. Black et al., [π0](https://arxiv.org/html/2410.24164v4), arXiv v4, 2024.
5. Black et al., [π0.5](https://arxiv.org/html/2504.16054v1), arXiv v1, 2025.
6. [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), frozen commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`.
7. Pertsch et al., [FAST](https://arxiv.org/html/2501.09747v1), arXiv v1, 2025.
8. [physical-intelligence/fast](https://huggingface.co/physical-intelligence/fast/tree/ec4d7aa71691cac0b8bed6942be45684db2110f4), frozen revision `ec4d7aa71691cac0b8bed6942be45684db2110f4`.
9. Zhao et al., [ACT](https://arxiv.org/abs/2304.13705), 2023.
10. Chi et al., [Diffusion Policy](https://arxiv.org/abs/2303.04137), arXiv v5.
11. Zhou et al., [On the Continuity of Rotation Representations in Neural Networks](https://arxiv.org/abs/1812.07035), CVPR 2019.
12. [VOL 03 完整知识卷](../knowledge/vol_03_vla_action.html)。
13. [OpenVLA Source Audit A](../sources/vol_03_openvla_claim_to_code.html)；[π0 / π0.5 / FAST / openpi Source Audit B](../sources/vol_03_pi0_fast_openpi_claim_to_code.html)。
14. 本地项目入口：[OpenPiVLA](../../03_openpivla_action_modeling.html)。该页不替代缺失的 config、checkpoint、norm stats、diff 与 eval summary。
15. [ACT CVAE、Action Chunk 与 Temporal Ensemble Source Audit C](../sources/vol_03_act_claim_to_code.html)。
16. [Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Source Audit D](../sources/vol_03_diffusion_policy_claim_to_code.html)。
17. [Flow Matching 基础、π0 特化与 ODE Source Audit E](../sources/vol_03_flow_matching_pi0_claim_to_code.html)。
18. Lipman et al., [Flow Matching for Generative Modeling](https://arxiv.org/html/2210.02747v2), arXiv `2210.02747v2`。
19. [facebookresearch/flow_matching](https://github.com/facebookresearch/flow_matching/tree/11568d37f8d5a080e12aa7b5305d9c35ae07d136), frozen commit `11568d37f8d5a080e12aa7b5305d9c35ae07d136`, CC BY-NC 4.0。
20. Octo Model Team et al., [Octo: An Open-Source Generalist Robot Policy](https://arxiv.org/html/2405.12213v2), arXiv v2；[octo-models/octo@241fb351](https://github.com/octo-models/octo/tree/241fb3514b7c40957a86d869fecb7c7fc353f540), MIT。
21. [VLA 架构、适配、延迟与动作执行 Source Audit F](../sources/vol_03_architecture_execution_claim_to_code.html)。
22. openpi serving / queue / DROID execution：[`policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py)、[`action_chunk_broker.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/action_chunk_broker.py)、[`examples/droid/main.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/droid/main.py)。
23. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
24. [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)。
25. [ACT CVAE / Action Chunk / Temporal Ensemble 独立事实复核](../sources/vol_03_act_independent_fact_review.html)，本仓库二次 paper/frozen-code 复核与 synthetic probes，2026-07-19。
26. [Diffusion Policy 条件扩散独立事实复核](../sources/vol_03_diffusion_policy_independent_fact_review.html)，本仓库二次 paper/frozen-code 复核与 synthetic probes，2026-07-19。
27. [VLA 架构、Mask、适配与执行独立事实复核](../sources/vol_03_architecture_execution_independent_fact_review.html)，RT-2/Octo/openpi direct source hashes 与 probes，2026-07-19。
