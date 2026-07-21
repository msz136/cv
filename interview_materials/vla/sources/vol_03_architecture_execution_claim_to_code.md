# VOL 03 Source Audit F：VLA 架构、适配、延迟与动作执行 Claim-to-Code

> 审计日期：2026-07-19  
> 状态：`independent_fact_reviewed / landscape_mask_transform_queue_checked / local_runtime_pending / WARN`  
> 论文范围：RT-2 `2307.15818v1`、OpenVLA `2406.09246v3`、Octo `2405.12213v2`、π0 `2410.24164v4`  
> 官方仓库：`openvla/openvla@c8f03f48...`、`octo-models/octo@241fb351...`、`Physical-Intelligence/openpi@15a9616a...`  
> 对应题目：`VLA-ARCH-007..012`、`VLA-ACT-031..032`  
> 本页问题：四类代表性 VLA/GRP 的 backbone、action representation 与训练路线如何比较？sequence layout、attention/loss mask、适配策略、异构动作、延迟和 checkpoint contract 怎样逐项核实？模型输出又怎样经过 decode、反归一化、切片、坐标/单位转换、chunk queue 与安全约束进入 controller？

## 1. 结论先行

1. **RT-2、OpenVLA、Octo 与 π0 不是同一条 action head 路线的不同尺寸**。RT-2/OpenVLA 把离散动作写进语言 token 空间；Octo 用 block-wise transformer 的 readout token 条件化 diffusion action head；π0 用 VLM prefix 条件化约 300M continuous action expert，并通过 Flow Matching 生成 chunk。[1][2][3][4]
2. **sequence layout 同时决定“谁能看谁”和“谁被监督”**。attention mask 决定信息流，label/loss mask 决定梯度流；action token 出现在序列里不等于它参加 loss，反之 readout token 不必是 action label，也能通过独立 action loss 得到梯度。[2][3][5][6]
3. **冻结、全量微调、LoRA 与独立 action expert 是四种不同的容量—显存—遗忘权衡**。OpenVLA flagship 是全量微调；其官方 finetune 脚本支持 all-linear LoRA。Octo 官方 recipe 提供 `head_only`、`head_mlp_only`、`full`；openpi 同时给出 full 与 VLM/action-expert LoRA 配置。不能把“repo 支持 LoRA”说成“论文主结果由 LoRA 得到”。[2][5][7]
4. **异构 action space 必须同时有表示映射和有效维 mask**。Octo 是本批正例：`timestep_pad_mask & action_pad_mask` 进入 MSE/diffusion loss，推理又用 embodiment action dimension 限制 padded diffusion 维；openpi π0 frozen loss 对配置的全部 D 维求 mean，是此前审计的负例边界。[5][6][8]
5. **延迟不能只报一个 `infer_ms`**。至少要拆 capture/preprocess、vision/prefix、token decode 或 NFE、output transform、serialization/network、queue wait 与 controller tick。openpi 同时记录 model sampling、server infer 和上一请求 total time，可作为分层 instrumentation 起点，但这些字段仍不能自动分离视觉编码与每步 sampler。[7][9]
6. **真实推理合同不在论文标题里**。需要形成 `paper → repo commit → config/model class → checkpoint manifest → norm stats → input/output transforms → rollout client → controller` 的闭环；只核对模型权重或只看到 success rate 都不够。[2][5][7]
7. **动作执行是有序函数复合**：decode、denormalize、valid-dimension slicing、absolute/delta 恢复、轴序/坐标/单位映射、安全投影、queue/replan，任何一步换序都可能产生“loss 正常、rollout 0-success”。OpenVLA、Octo 与 openpi 都能证明 decode/unnorm 的一部分；本地 OpenPiVLA 的 axis、unit 和 controller 仍未取证。[2][6][7]
8. **最小闭环单测必须使用可辨识 sentinel，不是只检查 shape**。需要验证 parser/token 边界、norm round-trip、padding 不变量、轴序和单位、chunk FIFO、replan 边界、stale response、安全裁剪与一次 mock-controller execution。[6][7][10]

## 2. 版本、来源与证据边界

| 来源 | 冻结版本 | 本页用途 | 不能证明什么 |
| --- | --- | --- | --- |
| RT-2 paper | arXiv `2307.15818v1` | PaLI-X/PaLM-E、256-bin action tokens、web+robot co-fine-tuning、cloud serving frequency | 公开 repo 的具体 tensor/layout；本地模型实现 |
| OpenVLA paper + repo | arXiv `2406.09246v3`；`c8f03f48af692657d3060c19588038c7220e9af9` | Prismatic-7B、action-only labels、full FT / LoRA、token decode 与 q01/q99 unnorm | 本地 OpenPiVLA 是同一 checkpoint 或同一 tokenizer |
| Octo paper + repo | arXiv `2405.12213v2`；`241fb3514b7c40957a86d869fecb7c7fc353f540`，MIT | block-wise attention、readout/diffusion head、三种 FT mode、action padding mask、sample/unnorm | Octo 指标可与 RT-2/OpenVLA/π0 直接横比 |
| π0 paper + openpi | arXiv `2410.24164v4`；`15a9616a00943ada6c20a0f158e3adb39df2ccac`，Apache-2.0 | VLM + action expert、LoRA、output transforms、timing、websocket、chunk broker、DROID execution | 私有 π0 data recipe；本地 OpenPiVLA 的 checkpoint/controller |
| 本仓 Source Audits A/B/E | 2026-07-16 canonical pages | OpenVLA token 端点、π0 time convention、FAST/flow latency、padding loss 边界 | independent fact review 或个人项目事实 |

Octo clone 在本次审计中执行 `git rev-parse HEAD` 得到 `241fb351...`，最后提交日期为 2024-07-30；不能把“2026-07-16 访问到的 HEAD”误写成“2026 年新实现”。RT-2 本页只使用论文与项目页，不声称审计到官方训练源码。

## 3. `VLA-ARCH-007`：四条代表路线如何比较

### 3.1 landscape table

| 方法 | backbone / condition encoder | action representation | 原始训练路线 | 推理关键循环 | 面试边界 |
| --- | --- | --- | --- | --- | --- |
| RT-2 | PaLI-X 5B/55B 或 PaLM-E 12B | 6-DoF pose delta、gripper、termination；连续维 uniform 256 bins 后变成整数 token | 预训练 VLM 上用 robot action data 与原 web data co-fine-tune | 自回归生成 action token；大模型由 multi-TPU cloud service 提供 | 两种 VLM tokenizer 的 action-token 占位方式不同；不是公开 OpenVLA code |
| OpenVLA | Prismatic-7B：DINOv2 + SigLIP → projector → Llama-2 7B | 当前动作每个 scalar 一个 tail-vocabulary token | OXE robot data 上全量微调 7B；官方另有 LoRA finetune 脚本 | 生成 d 个 token → 255-center nuance decode → dataset q01/q99 unnorm | flagship 基础路径是单主视角、单步、无 proprio/history |
| Octo | 27M/93M transformer；轻量 CNN image tokenizer + frozen T5-base language encoder | learned action readout → diffusion action head，默认公开 pretrain config 为 H=4、max D=7 | 800k OXE trajectories 预训练；新域可 head-only / head-MLP-only / full FT | transformer 一次产生 readout embedding；diffusion head 迭代去噪 chunk | 它是 generalist robot policy，不是把大型生成式 VLM LM head 直接当 action head |
| π0 | PaliGemma 2B VLM + 约 300M action expert | H×D continuous action chunk 的 flow velocity | 跨 embodiment 预训练，再对目标数据 post-train；公开 openpi 提供 full/LoRA 示例 | prefix KV 一次，action suffix 做多步 Euler/ODE 更新 | paper data mixture 与公开 repo recipe 不等价；controller 在模型外 |

RT-2 的 action token 和 co-fine-tuning 证据来自论文 §3.2：连续维 uniform 256 bins；PaLI-X 复用整数 token，PaLM-E 覆写 256 个低频 token；web 与 robot data 同批混合并提高 robot sampling weight。[1] §3.3 报告论文部署下 55B 为 1–3 Hz、5B 约 5 Hz，这些是 cloud TPU protocol 的历史测量，不是现代单机基准。[1]

OpenVLA 的架构、全量微调与 code endpoint 已在 [Source Audit A](vol_03_openvla_claim_to_code.html) 核实。Octo 论文明确给出 27M/93M checkpoint、800k Open X-Embodiment trajectories、language/goal-image instruction、diffusion head 与 action chunk。[3] frozen pretrain config 将 T5-base encoder 设为 `finetune_encoder=False`，action readout 接 `DiffusionActionHead(H=4,D=7)`，并冻结 `*hf_model*`。[5]

π0 的 prefix/suffix、action expert 和 Flow Matching 已在 [Source Audit B](vol_03_pi0_fast_openpi_claim_to_code.html) 与 [Source Audit E](vol_03_flow_matching_pi0_claim_to_code.html) 核实。比较时应对齐任务、机器人、数据、trial、controller 和 success predicate；上表只比较机制，不做成功率排名。

## 4. `VLA-ARCH-008`：sequence layout、attention 与 loss 语义

### 4.1 三种 layout 不能只画成同一条 token 串

```text
# RT-2 / OpenVLA: action itself occupies autoregressive label positions.
[image patches / prompt tokens] -> [a_1 token] [a_2 token] ... [a_d token] [EOS?]

# Octo: action readout is a latent query; continuous action is supervised in a separate head.
[task prefix] [obs(t-1), readout(t-1)] [obs(t), readout(t)] -> diffusion H x D

# pi0: condition prefix and continuous noisy-action suffix use a custom block mask.
[image + language prefix] [state token + noisy action_1 ... noisy action_H] -> H x D velocity
```

代码块说明：三者都使用 transformer，但 action 的“位置”分别是 LM label、readout latent 和 continuous suffix latent。把它们都叫 action token 会掩盖监督目标与 attention 方向。

对自回归 token 路线，令 (y_i) 为第 (i) 个 token，(m_i\in\{0,1\}) 为 label mask，则：

\[
\mathcal L_{\mathrm{AR}}
=-\frac{\sum_i m_i\log p_\theta(y_i\mid y_{<i},c)}
{\sum_i m_i+\epsilon}.
\]

变量与实现：(c) 是图像/任务条件；causal attention 决定 (y_i) 可读取哪些前缀，(m_i) 决定哪些位置产生 CE 梯度。OpenVLA `RLDSBatchTransform` 把 prompt prefix 设为 `IGNORE_INDEX=-100`，默认保留 action tokens 与 stop token；插入的 image patches 也补 `IGNORE_INDEX`。[2] 因此 attention-visible 不等于 loss-visible。

Octo 的 frozen `octo_module.py` 将 task 作为 prefix；同 timestep 的 observation groups 互相注意并看历史；readout 可读取 task/observation/自身 readout，却不被 observation 写回。其源码注释甚至记录 v1.5 修复过 attention mask 的 off-by-one bug，说明 mask 不是展示性元数据。[5]

Octo 的 action loss 使用两类 mask：

\[
M_{b,w,h,d}=T_{b,w}\land A_{b,w,h,d},
\qquad
\mathcal L_{\mathrm{Octo}}
=\operatorname{continuous\_loss}(\hat z,z;M).
\]

变量与实现：(T) 是 observation-history `timestep_pad_mask`，(A) 是 `action_pad_mask`；(b,w,h,d) 分别为 batch、history window、action horizon、model action dimension。frozen MSE 与 diffusion head 都先构造这个 conjunction，再调用 `continuous_loss`。[6] 这既阻止 padded history 产生监督，也阻止异构 embodiment 的 padded action dimensions 污染 target。

π0 / Pi0FAST 的 prefix/postfix attention、AR mask 与 token loss mask 已在 Source Audit B 精确展开；特别是 frozen Pi0 continuous loss 对配置 D 全维 mean，没有 Octo 式有效维 mask。面试时应说“不同实现的 mask 正例/负例”，不能泛称“VLA 都会自动 mask padding”。

## 5. `VLA-ARCH-009`：冻结、全量、LoRA 与 action expert 的取舍

### 5.1 它们分别在改什么

| 路线 | 更新参数 | 优点 | 主要风险 | 官方证据例 |
| --- | --- | --- | --- | --- |
| freeze backbone / head-only | 只训 projector、readout 或 action head | 显存小、语义先验稳定、少数据不易过拟合 | domain gap 无法进入视觉/语言表征；head 容量成为瓶颈 | Octo `head_only` 冻结 `octo_transformer.*` |
| head-MLP-only | 冻结 transformer 与 readout attention，只训 head MLP | 比 head-only 更强约束，便于快速适配 action space | 不能改变 readout 如何从 context 聚合 | Octo `head_mlp_only` 额外冻结 MAP probe/attention |
| full fine-tuning | 更新 vision/projector/LLM/action modules | 最大任务适配容量；可调整视觉细粒度特征 | 显存与通信大、灾难遗忘、少数据过拟合 | OpenVLA flagship；Octo `full`；openpi LIBERO full config |
| LoRA / adapter | 对选定线性层学习低秩增量 | 训练参数和 optimizer state 小，checkpoint 易管理 | rank/target module 可能限制容量；base revision 与 adapter 必须配对 | OpenVLA all-linear LoRA；openpi VLM + action-expert LoRA |
| independent action expert | 保留大 VLM context，另训较小 continuous expert | robot action 的宽度/目标与 VLM 解耦；多步 flow 的单步计算较小 | context bottleneck、expert 与 backbone 联调复杂 | π0 2B VLM + 300M expert |

LoRA 对冻结权重 (W\in\mathbb R^{o\times i}) 学习低秩增量：

\[
W'=W+\frac{\alpha}{r}BA,
\qquad
A\in\mathbb R^{r\times i},\;B\in\mathbb R^{o\times r}.
\]

变量与实现：(r\ll\min(i,o)) 是 rank，(alpha) 是 scale。OpenVLA official finetune 用 PEFT `target_modules="all-linear"`；openpi LIBERO low-memory 配置把 PaliGemma 与 action expert 都换成 LoRA variant，并用匹配 config 的 `get_freeze_filter()` 冻结非 LoRA 权重。[2][7] 这证明“支持怎样适配”，不证明某个本地 checkpoint 实际采用该路线。

### 5.2 面试决策顺序

1. 先看 dataset size/diversity、视觉 domain shift、语言变化、action schema 变化和显存预算。
2. 若只是新 action 维度、视觉近似且数据少，先 head-only / adapter；若 camera、objects、dynamics 变化明显，考虑解冻视觉/projector。
3. 若语义与控制都显著变化且有足够数据，再 full FT；同时保留 upstream/task eval 监控遗忘。
4. 对 LoRA 必报 base checkpoint revision、target modules、rank、merge 状态和加载顺序。
5. 对 action expert 必报 context interface、expert width、训练 target、是否共同更新 VLM，以及 sampling NFE。

## 6. `VLA-ARCH-010`：跨 embodiment action 统一与 padding loss

设 robot (e) 的真实动作 (a^{(e)}\in\mathbb R^{d_e})，模型统一宽度为 (D\ge d_e)。用 embedding matrix (P_e\in\{0,1\}^{D\times d_e}) 写入统一空间，用 selection matrix (S_e=P_e^\top) 取回：

\[
\bar a^{(e)}=P_ea^{(e)},
\qquad
\hat a^{(e)}=S_e\hat{\bar a},
\qquad
m^{(e)}_j=\mathbb 1[j\in\operatorname{Im}(P_e)].
\]

变量与实现：(P_e) 只能表示“维度放到哪里”，不能自动统一 axis、unit、absolute/delta、rotation 或 gripper semantics；这些还需要 schema transform。openpi `PadStatesAndActions` 只做 zero-pad，不能据此假设 loss mask 存在。[7]

正确的 masked continuous objective 应明确 normalization 和有效维：

\[
\mathcal L_{mathrm{valid}}
=\frac{\sum_{b,h,j}m_{b,h,j}\ell(\hat{\bar a}_{b,h,j},\bar a_{b,h,j})}
{\sum_{b,h,j}m_{b,h,j}+\epsilon}.
\]

变量与实现：(m) 同时排除 padding timestep 与 padding dimension；Octo 的 `action_pad_mask` 是直接正例。[6] 若对全部 D 维 mean，zero padded axes 也会产生“逼近 0”的监督，并随 (d_e/D) 改变有效维梯度占比。此前 frozen π0 审计只看到 all-D mean，因此本地若声称避免 padding loss，必须提供自己的 mask path。

### 6.1 schema 统一检查表

| 字段 | 必须记录 | 常见错误 |
| --- | --- | --- |
| translation | x/y/z axis、frame、m 或 cm、absolute/delta/velocity | 只按列号 pad，未统一 frame/unit |
| rotation | Euler/quaternion/6D、顺序、弧度/角度、delta composition | quaternion sign、Euler order 或单位不一致 |
| gripper | position/velocity/binary、open polarity、range | 把 continuous gripper 当普通 z-score 维 |
| base | vx/vy/yaw-rate 或 pose、body/world frame | mobile-base 维与 arm 维错位 |
| timestep | control frequency、label horizon、timestamp | 同一个 delta 在不同 dt 下物理量不同 |
| mask | timestep/action/modality valid mask | 只 pad input，不 mask target/loss |

## 7. `VLA-ARCH-011`：延迟如何分层而不是猜瓶颈

对一次远程 chunk query，端到端延迟写为：

\[
T_{\mathrm{e2e}}=
T_{\mathrm{capture}}+T_{\mathrm{pre}}+T_{\uparrow}
+T_{\mathrm{vision/prefill}}+N\,T_{\mathrm{decode/step}}
+T_{\mathrm{post}}+T_{\downarrow}+T_{\mathrm{queue}}.
\]

变量与实现：(N=d) 可表示 OpenVLA/RT-2 的 action-token 数；对 Pi0FAST 是可变 FAST token length；对 flow/diffusion 是 NFE/denoise steps。`vision/prefill` 是否可缓存、每步是否只跑 action expert，取决于真实实现。openpi `Policy.infer` 的 `policy_timing.infer_ms` 只包围 `sample_actions`；server 的 `server_timing.infer_ms` 包围完整 policy infer，`prev_total_ms` 还包括 recv/unpack/send 的上一轮总时长。[7][9]

RT-2 论文的 55B 1–3 Hz / 5B 约 5 Hz 包含其 cloud serving protocol，说明 network 不能从大模型部署中忽略，但不能直接外推 openpi。FAST 论文在指定 4090 实现下报告 π0 flow 约 100 ms/chunk、π0-FAST 约 750 ms/chunk；解释是后者用 2B backbone 自回归生成约 30–60 tokens，前者做 10 次较小 expert step。[11] 这同样只是 source-specific measurement。

### 7.1 可执行 timing pseudocode

```python
def timed_policy_query(raw_obs, client, policy, controller):
    # Synchronize device events; otherwise asynchronous GPU work makes timers invalid.
    t0 = sync_clock()
    obs = preprocess_and_resize(raw_obs)
    t_pre = sync_clock()

    # Measure serialization/transport separately from server-side model timing.
    response = client.infer(obs)
    t_roundtrip = sync_clock()

    # Read server/model fields, then time local parse, denorm, slicing and safety.
    model_ms = response["policy_timing"]["infer_ms"]
    server_ms = response["server_timing"]["infer_ms"]
    action_chunk = parse_and_validate(response["actions"])
    env_actions = output_transform_and_safety(action_chunk)
    t_post = sync_clock()

    # Queue wait and controller step need their own timestamp at the consumer side.
    controller.enqueue(env_actions)
    return make_timing_record(t0, t_pre, t_roundtrip, t_post, model_ms, server_ms)
```

代码块说明：真实 CUDA/JAX 计时需 device synchronization 与 warm-up；至少报告 p50/p95、payload bytes、H/K、NFE/token length、batch、dtype、device、是否缓存 prefix。只报一次 wall clock 不足以定位瓶颈。

## 8. `VLA-ARCH-012`：paper / repo / checkpoint / I/O 证据审计

### 8.1 四层证据不能互相替代

| 层 | 要回答的问题 | 最小 artifact | 典型误判 |
| --- | --- | --- | --- |
| paper | 方法声称什么、实验 protocol 是什么 | 版本号、section/table、公式 | 用 paper 抽象当 frozen code 细节 |
| repo | 某 commit 实际实现什么 | commit、license、model class、loss/infer path | 用 main HEAD 解释旧 checkpoint |
| checkpoint | 权重对应什么模型与资产 | manifest/config、weight shape/hash、tokenizer、norm stats | 只凭目录名猜 backbone/H/D |
| runtime | 真正收发和执行什么 | startup log、request/response schema、transforms、rollout trace | 模型 output shape 对就认为 controller 正确 |

openpi `create_trained_policy` 是正例：先从 checkpoint 判断 JAX/PyTorch weight，再由 training config 构造 model/data config；norm stats 默认从 checkpoint `assets/<asset_id>` 读取，随后固定 input transforms → normalize → model transforms，以及 model outputs → unnormalize → data/repack outputs 的顺序。[7] OpenVLA 的 `unnorm_key` 同样决定生成 token 数和 q01/q99 stats；多 dataset checkpoint 不显式选择 key 会报错。[2]

```python
def audit_vla_release(paper, repo, checkpoint, runtime_sample):
    # Freeze provenance before reading implementation claims.
    assert paper.version and repo.commit and repo.license

    # Reconstruct the model from the exact checkpoint config, not a similarly named default.
    manifest = load_checkpoint_manifest(checkpoint)
    assert hash_file(checkpoint.weights) == manifest.weight_sha256
    assert manifest.model_class == runtime_sample.startup_model_class

    # Verify tokenizer, normalization assets and tensor contract as one bundle.
    assert manifest.tokenizer_revision == runtime_sample.tokenizer_revision
    assert manifest.norm_asset_id == runtime_sample.norm_asset_id
    assert runtime_sample.output_shape == (manifest.horizon, manifest.action_dim)

    # Trace one sentinel action through decode -> unnorm -> schema -> controller.
    trace = replay_sentinel(runtime_sample)
    assert trace.controller_action == trace.expected_controller_action
    return trace
```

代码块说明：这是审计框架，不声称本地已有这些字段。对 OpenPiVLA，checkpoint、Qwen/π model class、tokenizer revision、norm asset、H/D/K、axis/unit、rollout trace 与 97.4% eval summary 仍待本地 artifact。

## 9. `VLA-ACT-031`：模型输出到 controller 的有序链

### 9.1 一般形式

令模型原始输出为 \(z\)，token/FAST/flow decoder 为 \(\mathcal D\)，反归一化为 \(\mathcal U\)，有效维选择为 \(S_e\)，absolute/delta 与 frame/unit 映射为 \(\mathcal R_e\)，安全投影为 \(\Pi_{\mathcal A_e}\)：

\[
a^{\mathrm{ctrl}}
=\Pi_{\mathcal A_e}\!\left(
\mathcal R_e\!\left(S_e\,\mathcal U(\mathcal D(z))\right)
\right).
\]

变量与实现：(mathcal A_e) 是 robot/controller 允许的动作集合。函数顺序不能随意交换：例如在 normalized space clip 与在物理 velocity space clip 的含义不同；delta action 必须在正确 state/frame 上恢复。openpi 的 `Policy.infer` 明确在 model sampling 后执行 output transform，`policy_config` 把 `model_transforms.outputs`、`Unnormalize`、dataset outputs 和 repack outputs 依次组合。[7]

具体公开实现边界：

- OpenVLA：生成数量由 dataset stats 的 action dim 决定；token decode 后按 q01/q99 与 optional mask unnormalize。它没有证明 controller axis/unit。[2]
- Octo：`sample_actions` 用 `embodiment_action_dim=len(stats["mean"])` 限制 diffusion padded 维，再 slice 到 stats 长度并用 mean/std 或 p01/p99 unnormalize。[6]
- openpi：FAST path 先 `ExtractFASTActions`；continuous/FAST 共同经过 checkpoint norm stats 的 `Unnormalize`；`AbsoluteActions` 可按 mask 把 delta 加回 state；具体 data output transform 还可能重排 robot schema。[7]
- openpi DROID example：server 返回 `[10,8]`，client 取 chunk 当前行、二值化 gripper、clip 到 `[-1,1]`，再 `env.step`，并按数据采集频率 sleep。[10] 这是 DROID example 的合同，不是通用 controller 标准。

### 9.2 axis/unit 映射必须显式

若 dataset delta (a^{\mathrm{data}}) 与 controller action 的轴序/单位关系为矩阵 (R_e) 和 scale (s_e)，且部分维为 absolute 恢复，则可写：

\[
a^{\mathrm{abs}}_{t:t+H-1}
=a^{\mathrm{data}}_{t:t+H-1}+m_\Delta\odot q_t,
\qquad
a^{\mathrm{ctrl}}=s_e\odot R_e a^{\mathrm{abs}}.
\]

变量与实现：(m_\Delta) 只在 delta dimensions 为 1，(q_t) 是当前 state；真实 rotation 可能需要群上的 composition，不能总用向量加法。openpi `AbsoluteActions` 只对 mask 覆盖的前 dims 加 state，是可核代码例；本地 axis matrix、unit scale 与 rotation semantics 仍需 controller wrapper 证明。[7]

## 10. `VLA-ACT-032`：parser、queue、replan 与 safety 的最小闭环测试

### 10.1 必测矩阵

| Test ID | 输入 sentinel / 扰动 | 应检查的不变量 | 能抓住的错误 |
| --- | --- | --- | --- |
| T1 parser boundary | 最小/最大合法 token、EOS、越界 token、短 chunk | 非 action token 被拒绝；shape 恰为 H×D | vocab offset、EOS 混入、silent reshape |
| T2 norm round-trip | 每维 `q01/mean/q99` 与 gripper mask | `unnorm(norm(a))≈a`；masked dim 原值保留 | stats key/revision、广播维错误 |
| T3 padding sentinel | valid dims 放互异质数，padding 放大常数 | slice 后只保留 d；loss 对 padding sentinel 不变 | padding loss 污染、wrong-axis slice |
| T4 frame/unit | x/y/z/rot/gripper 各放独立 one-hot | controller 对应轴、符号、单位精确匹配 | frame rotation、cm/m、degree/radian、gripper polarity |
| T5 FIFO chunk | chunk 行编码为 step index 0..H-1 | 连续 K 次输出严格 0..K-1，无重复/跳步 | off-by-one、queue reset 错误 |
| T6 replan | 第 K 步注入新观测/新 chunk | 只在定义边界切换；旧 chunk 不泄漏 | H/K 混淆、stale chunk |
| T7 stale/RPC | 延迟、乱序、断连、重复 response ID | 超时 fail-safe；旧 response 不覆盖新 plan | 网络乱序与无 request id |
| T8 safety | NaN/Inf/超限 velocity/workspace pose | reject 或投影；记录原值与触发规则 | `np.clip` 吞掉 NaN、错误空间裁剪 |
| T9 mock controller | 完整 request → one mock `step` | controller 收到预期 dtype/shape/value/time | 单模块都通过但组合换序 |

openpi frozen `ActionChunkBroker` 只在 cache 为空时 query inner policy，按 `_cur_step` slice，并在达到 configured action horizon 后清空；manual test 只验证每步 shape。[9] 这提供最小行为实现，但没有覆盖 request ID、stale response、NaN、axis/unit 或 safety。因此项目级 test 必须扩展。

```python
def test_closed_loop_contract(policy_stub, parser, output_transform, broker, mock_env):
    # Each row and dimension is unique, so transpose/slice/queue bugs cannot hide behind zeros.
    sentinel = make_prime_sentinel_chunk(horizon=4, model_dim=8, valid_dim=7)
    policy_stub.return_value = {"actions": sentinel, "request_id": 42}

    # Execute K=2 rows; the broker must consume rows 0 and 1 exactly once.
    a0 = broker.infer(make_observation(request_id=42))["actions"]
    a1 = broker.infer(make_observation(request_id=42))["actions"]
    assert not_equal(a0, a1)

    # Parse, unnormalize, slice, map axes/units and apply safety in the declared order.
    c0 = output_transform(parser(a0))
    c1 = output_transform(parser(a1))
    assert c0.shape == c1.shape == (7,)
    assert all_finite_and_within_limits(c0, c1)

    # A mock controller checks the final physical contract, not only intermediate tensors.
    mock_env.step(c0)
    assert mock_env.last_action == expected_controller_sentinel(row=0)
```

代码块说明：使用质数/one-hot sentinel 是为了让 transpose、错轴、padding 与重复行产生可观察差异；真实测试还需固定 norm stats、frame transform、controller mode 和 control dt。

## 11. Claim-to-code matrix

| Claim | paper | frozen repo | 判定 | 关键证据 |
| --- | --- | --- | --- | --- |
| RT-2 有 PaLI-X/PaLM-E 两个 backbone family | direct | 本页未审计 repo | paper-direct | RT-2 §3.1 / appendix |
| RT-2 action 连续维为 uniform 256 bins 并映射成 token | direct | 本页未审计 repo | paper-direct | RT-2 §3.2 |
| RT-2 主 recipe 混合 web + robot co-fine-tuning | direct | 本页未审计 repo | paper-direct | RT-2 §3.2 |
| OpenVLA flagship 是 DINOv2+SigLIP / Llama-2 7B，full FT | direct | direct | source-ready / WARN | Source Audit A |
| OpenVLA loss 只监督 action tail 与可选 stop，patch labels ignore | paper overview | direct | source-ready | `datasets.py` / `modeling_prismatic.py` |
| Octo 是 27M/93M transformer generalist policy，800k OXE | direct | checkpoint config compatible | source-ready | Octo abstract / §III |
| Octo block-wise attention 的 readout 只读 condition | direct | direct | source-ready | `octo_module.py` |
| Octo diffusion loss 排除 padded timestep/action dims | method overview | direct | source-ready | `action_heads.py` |
| Octo 支持 head-only/head-MLP-only/full FT | paper + docs | direct config | source-ready | `finetune_config.py` |
| π0 是 2B VLM + 300M action expert continuous flow | direct | direct config/path | source-ready / WARN | Source Audits B/E |
| openpi 支持 full 与 LoRA LIBERO adaptation | 不属于 π0 paper 主结果 | direct | repo-supported option | `training/config.py` |
| openpi output transforms 从 model decode 到 unnorm/data outputs 有序组合 | architecture overview | direct | source-ready | `policy_config.py` |
| openpi timing 已完全拆分 vision、expert、network 与 queue | no | no | rejected | 当前只有 model/server/previous total 三层 |
| 本地 OpenPiVLA 采用上述任一 checkpoint/H/D/K/controller | no | no | unverified | 需要本地 artifacts |

## 12. 公源 / 本地项目边界

| 本地 claim | 最小证据 | 当前状态 |
| --- | --- | --- |
| base 是 OpenVLA、Pi0、Pi0FAST、π0.5 或自定义 Qwen route | startup config、model class、checkpoint manifest、forward/loss path | pending |
| frozen/full/LoRA/action-expert adaptation | train config、trainable-parameter log、adapter/base revisions | pending |
| H/D/K 与 action schema | dataset target、model output、queue/replan config、controller wrapper | pending |
| padding 不污染 loss | actual loss mask、synthetic padding sentinel test | pending |
| end-to-end latency | synchronized p50/p95 timing ledger + payload/device/NFE/token length | pending |
| decode/denorm/slice/axis/unit 正确 | tokenizer/norm assets、output transform、mock controller trace | pending |
| 97.4% 与 checkpoint 对应 | eval summary、checkpoint ID/hash、task/trial/split/seed/protocol | pending |
| personal contribution | local diff、设计记录、run ledger、ownership boundary | pending |

本页所有架构、loss、transform 与 serving 实现都属于上游公开设计。除非本地 diff 与运行 artifact 另行证明，不得写成本人的原创贡献，也不得用 upstream example 的 `[10,8]`、H=50 或某个 norm asset 推断本地值。

## 13. 题目覆盖与剩余验证

| Question ID | 本页支持 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ARCH-007 | RT-2/OpenVLA/Octo/π0 landscape | independent-fact-reviewed / WARN | local architecture mapping |
| VLA-ARCH-008 | token/readout/suffix layout、attention/loss masks | independent-fact-reviewed / WARN | local layout sentinel test |
| VLA-ARCH-009 | freeze/full/head/LoRA/expert decision | independent-fact-reviewed / WARN | target hardware/data ablation |
| VLA-ARCH-010 | unified D/d、Octo positive mask、openpi negative boundary | independent-fact-reviewed / WARN | local mask evidence |
| VLA-ARCH-011 | latency equation、RT-2/FAST context、openpi timings | independent-fact-reviewed / WARN | local synchronized timing |
| VLA-ARCH-012 | paper→repo→checkpoint→runtime audit | independent-fact-reviewed / WARN | local manifest and trace |
| VLA-ACT-031 | decode→unnorm→slice→schema→safety→controller | independent-fact-reviewed / WARN | local axis/unit/controller |
| VLA-ACT-032 | parser/queue/replan/safety test matrix | independent-fact-reviewed / WARN | local executable tests |

RT-2/Octo 论文措辞、Octo `continuous_loss` denominator、openpi output transform、broker 与 DROID example 已在 [独立事实复核页](vol_03_architecture_execution_independent_fact_review.html) 核对。下一步只进行一题真实口述或补本地 manifest/trace；所有 8 张卡继续 `unseen`。

## 14. 参考文献（References）

1. Brohan et al., [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/abs/2307.15818), arXiv v1, 2023；[§3.2 Robot-Action Fine-tuning](https://ar5iv.labs.arxiv.org/html/2307.15818#S3.SS2)；[§3.3 Real-Time Inference](https://ar5iv.labs.arxiv.org/html/2307.15818#S3.SS3)。
2. Kim et al., [OpenVLA](https://arxiv.org/html/2406.09246v3), arXiv v3；[`openvla/openvla@c8f03f48`](https://github.com/openvla/openvla/tree/c8f03f48af692657d3060c19588038c7220e9af9)；[Source Audit A](vol_03_openvla_claim_to_code.html)。重点代码：[`datasets.py#L44-L67`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/datasets.py#L44-L67)、[`modeling_prismatic.py#L388-L410`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/extern/hf/modeling_prismatic.py#L388-L410)、[`finetune.py#L98-L103`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/vla-scripts/finetune.py#L98-L103)、[`#L172-L182`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/vla-scripts/finetune.py#L172-L182)、[`openvla.py#L80-L103`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlas/openvla.py#L80-L103)。
3. Octo Model Team et al., [Octo: An Open-Source Generalist Robot Policy](https://arxiv.org/html/2405.12213v2), arXiv v2, 2024；[§III-A Architecture](https://arxiv.org/html/2405.12213v2#S3.SS1)、[§III-C Training Objective](https://arxiv.org/html/2405.12213v2#S3.SS3)。
4. Black et al., [π0](https://arxiv.org/html/2410.24164v4), arXiv v4；[Source Audit B](vol_03_pi0_fast_openpi_claim_to_code.html)；[Source Audit E](vol_03_flow_matching_pi0_claim_to_code.html)。
5. [`octo-models/octo@241fb351`](https://github.com/octo-models/octo/tree/241fb3514b7c40957a86d869fecb7c7fc353f540), MIT. 重点：[`octo_module.py#L24-L63`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_module.py#L24-L63)、[`#L138-L168`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_module.py#L138-L168)、[`#L241-L268`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_module.py#L241-L268)、[`octo_pretrain_config.py#L45-L62`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/scripts/configs/octo_pretrain_config.py#L45-L62)、[`#L107-L125`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/scripts/configs/octo_pretrain_config.py#L107-L125)。
6. Octo action contract：[`action_heads.py#L175-L207`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/components/action_heads.py#L175-L207)、[`#L466-L526`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/components/action_heads.py#L466-L526)、[`#L540-L610`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/components/action_heads.py#L540-L610)、[`octo_model.py#L174-L250`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_model.py#L174-L250)。
7. [`Physical-Intelligence/openpi@15a9616a`](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac), Apache-2.0. 重点：[`policy_config.py#L16-L64`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_config.py#L16-L64)、[`#L75-L94`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_config.py#L75-L94)、[`transforms.py#L115-L181`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py#L115-L181)、[`#L204-L244`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py#L204-L244)、[`#L328-L337`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py#L328-L337)、[`training/config.py#L651-L698`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/config.py#L651-L698)。
8. [Source Audit E：Flow Matching / π0](vol_03_flow_matching_pi0_claim_to_code.html)，frozen Pi0 all-D mean 与有效维 mask 边界。
9. openpi serving / queue：[`policy.py#L68-L105`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py#L68-L105)、[`websocket_policy_server.py#L48-L72`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/serving/websocket_policy_server.py#L48-L72)、[`websocket_client_policy.py#L46-L54`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/websocket_client_policy.py#L46-L54)、[`action_chunk_broker.py#L10-L50`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/action_chunk_broker.py#L10-L50)。
10. openpi DROID example：[`examples/droid/main.py#L113-L156`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/droid/main.py#L113-L156)；manual shape/broker test：[`policy_test.py#L9-L34`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_test.py#L9-L34)。
11. Pertsch et al., [FAST](https://arxiv.org/html/2501.09747v1), arXiv v1；latency 条件与路径已在 [Source Audit B](vol_03_pi0_fast_openpi_claim_to_code.html) 核对。
12. [VLA 架构、Mask、适配与执行独立事实复核](vol_03_architecture_execution_independent_fact_review.html)，RT-2/Octo/openpi direct source hashes 与 synthetic probes，2026-07-19。
