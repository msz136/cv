# VOL 03 VLA / Action：来源计划

> 调研日期：2026-07-16；registry reconciliation：2026-07-19  
> 状态：`source_registry_reconciled / audits_A_F_public_facts_reviewed / local_gates_warn`  
> 目标：为 VLA 架构、action token、FAST、ACT、Diffusion Policy、Flow Matching 和 openpi action expert 建立 primary-source ledger。  
> 边界：Audit A–F 的 public paper/code facts 已分别完成 claim-to-code 与 independent review；这不证明本地 OpenPiVLA checkpoint、action parser/controller、97.4 lineage、个人 ownership 或口述 mastery。

## 1. Primary papers / technical reports

| 主题 | 来源与冻结版本 | 计划支持的 claim | 当前状态 |
| --- | --- | --- | --- |
| OpenVLA | [OpenVLA: An Open-Source Vision-Language-Action Model](https://arxiv.org/abs/2406.09246), arXiv v3 | VLM-to-action token、action discretization、open VLA landscape | Audit A endpoint/token/mask independently checked / PASS WITH WARNING |
| RT-2 | [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/abs/2307.15818), arXiv v1 | web/VLM knowledge 与 action-as-token 路线 | Audit F action-token/serving boundary independently checked / WARN |
| Octo | [Octo: An Open-Source Generalist Robot Policy](https://arxiv.org/abs/2405.12213), arXiv v2 | generalist policy、task/action readout 对照 | Audit F readout/mask independently checked / WARN |
| π0 | [π0: A Vision-Language-Action Flow Model for General Robot Control](https://arxiv.org/abs/2410.24164), arXiv v4 | VLM context、action expert、flow-matching action generation | Audit E time/sign + Audit B/F config/rollout independently checked / WARN |
| π0.5 | [π0.5: a Vision-Language-Action Model with Open-World Generalization](https://arxiv.org/abs/2504.16054), arXiv v1 | π 系列后续架构与 open-world 语境；不替代项目 checkpoint 证据 | Audit B hybrid boundary independently checked / WARN |
| FAST | [FAST: Efficient Action Tokenization for Vision-Language-Action Models](https://arxiv.org/abs/2501.09747), arXiv v1 | frequency-space transform、quantization、BPE action compression | Audit B paper/Hub/defaults/mask independently checked / WARN |
| ACT | [Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware](https://arxiv.org/abs/2304.13705), arXiv v1 | CVAE action chunking、temporal ensembling | Audit C paper/code gaps independently checked / PASS WITH WARNING |
| Diffusion Policy | [Diffusion Policy: Visuomotor Policy Learning via Action Diffusion](https://arxiv.org/abs/2303.04137), arXiv v5 | conditional action diffusion、receding-horizon control | Audit D target/mask/horizon/runtime independently checked / PASS WITH WARNING |
| Flow Matching | [Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747), arXiv v2 | probability path、conditional vector field、ODE sampling 基础 | Audit E theorem/endpoint/time-sign independently checked / WARN |

## 2. Official repositories frozen at 2026-07-16

| Official repo | Frozen HEAD / branch | License evidence | 本卷用途 |
| --- | --- | --- | --- |
| [openvla/openvla](https://github.com/openvla/openvla) | `c8f03f48af692657d3060c19588038c7220e9af9` / `main` | MIT（Source Scout） | action tokenizer、model/prompt contract、inference decode |
| [octo-models/octo](https://github.com/octo-models/octo) | `241fb3514b7c40957a86d869fecb7c7fc353f540` / `main` | MIT（LICENSE 已复核） | block-wise attention、readout/diffusion head、FT mode、action padding mask |
| [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | `15a9616a00943ada6c20a0f158e3adb39df2ccac` / `main` | Apache-2.0（LICENSE 已复核） | π policy config、action expert、normalization 与 policy I/O |
| [real-stanford/diffusion_policy](https://github.com/real-stanford/diffusion_policy) | `5ba07ac6661db573af695b419a7947ecb704690f` / `main` | MIT | action diffusion training/inference implementation |
| [tonyzhaozh/act](https://github.com/tonyzhaozh/act) | `742c753c0d4a5d87076c8f69e5628c79a8cc5488` / `main` | MIT | CVAE chunk、temporal ensemble 与 evaluation path |
| [facebookresearch/flow_matching](https://github.com/facebookresearch/flow_matching) | `11568d37f8d5a080e12aa7b5305d9c35ae07d136` / `main` | CC BY-NC 4.0 | 后续维护包；只补证现代 probability path / ODE solver / CFG API，不冒充 2022 历史实现 |
| [QwenLM/Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) | `96588727e44c78b25ba03ea03b8e12f7e64fd0da` / `main` | Apache-2.0 | 仅作本地 VLM backbone 语境；不能证明 action head |

## 3. 逐源阅读与实现映射队列

| Batch | 必须回答 | 证据动作 | 未完成前禁止的表述 |
| --- | --- | --- | --- |
| A：OpenVLA | action token 对应哪些维度、如何离散/反离散、哪些 token 参与 loss？ | 论文公式 → repo tokenizer/model/inference 路径 → tensor shape 表 | “所有 action-token VLA 都按 OpenVLA 实现” |
| B：π0 / π0.5 / openpi + FAST | observation/state/noisy action 怎样进入 action expert？flow 与 FAST 的 target、mask、normalization、solver/decode 在哪里？ | π0/π0.5/FAST 论文 → frozen openpi + FAST Hub → 两条 train/infer 对照 | “OpenPiVLA 与公开 π0/π0.5 完全相同”或“压缩率更高必然提升成功率” |
| C：ACT | CVAE latent、chunk query、temporal ensemble 的训练/推理差异是什么？ | 论文 → ACT repo model/eval path | “action chunking 等于 ACT” |
| D：Diffusion Policy | condition、prediction target、scheduler、horizon 与 receding-horizon 执行如何映射？ | 论文 → official workspace/policy/config path | “所有连续生成 head 都是 diffusion” |
| E：Flow Matching | probability path、target velocity 与 ODE integration 如何映射到 π0 action tensor？ | Flow Matching 基础 → π0 特化 → openpi code | “flow matching 只是少几步的 diffusion” |
| F：架构与执行 | RT-2/OpenVLA/Octo/π0 如何比较？mask、FT、异构动作、延迟、checkpoint 与 controller 如何闭环？ | 四篇论文 → frozen OpenVLA/Octo/openpi → action parser/queue/test matrix | “repo example 即本地合同”或“shape 对就代表可执行” |

### Batch A：OpenVLA（public facts independently reviewed）

- [OpenVLA Action Token 与 I/O Claim-to-Code](vol_03_openvla_claim_to_code.md)：覆盖 `VLA-ARCH-001..005`、`VLA-ACT-002..004` 的上游论文与 frozen commit。
- 已冻结路径：`prismatic/vla/action_tokenizer.py`、`prismatic/vla/datasets/datasets.py`、`prismatic/models/vlas/openvla.py`、`prismatic/extern/hf/modeling_prismatic.py`、`prismatic/vla/datasets/rlds/utils/data_utils.py`、`prismatic/conf/vla.py`。
- [独立复核](vol_03_openvla_endpoint_independent_fact_review.html) 已确认 256-bin paper abstraction、encoder 256 IDs、decoder 255 centers、endpoint alias 与 CE/metric mask；本地 tokenizer/checkpoint/stats/controller/ownership 仍 WARN。

### Batch B：π0 / π0.5 / openpi + FAST（public facts independently reviewed）

- [π0 / π0.5 / FAST / openpi Claim-to-Code](vol_03_pi0_fast_openpi_claim_to_code.md)：覆盖 flow paper/code 时间约定、π0.5 hybrid objective 边界、FAST DCT/量化/BPE、Pi0FAST masked CE、normalization、padding/slicing 与 H/K rollout contract。
- openpi 已冻结到 `15a9616a00943ada6c20a0f158e3adb39df2ccac`；FAST Hub 已冻结到 `ec4d7aa71691cac0b8bed6942be45684db2110f4`。
- 关键 warning：π0.5 论文联合 FAST-token CE 与 flow loss；当前审计的 `Pi0(pi05=True)` 主 loss 路径只直接实现 flow MSE，不能称该 commit 完整复现论文 hybrid pre-training。
- [独立复核](vol_03_pi0_fast_openpi_independent_fact_review.html) 已确认 π0.5 two-stage boundary、FAST paper/Hub defaults、prefix/postfix mask、normalization、padding/output slice 与 LIBERO example；本地 formal Qwen route 已另证为 JSON/full-chat CE，不能称 FAST 等价。

### Batch C：ACT（public facts independently reviewed）

- [ACT CVAE、Action Chunk 与 Temporal Ensemble Claim-to-Code](vol_03_act_claim_to_code.md)：覆盖 `VLA-ACT-011..017` 的上游 source contract。
- 已核对 arXiv `2304.13705v1` 与 `tonyzhaozh/act@742c753...`；明确 train-time posterior、test-time `z=0`、`[B,H,14]`、masked L1 + KL、整段执行和 per-step temporal aggregation。
- 关键 warning：论文 Algorithm 1 的 MSE 与正文/代码 L1 不一致；论文的 fixed/sinusoidal query 描述与 frozen code 的 learned `nn.Embedding` 不一致；masked L1 的 denominator 仍含 padded slots。
- [独立复核](vol_03_act_independent_fact_review.html) 已完成 posterior/`z=0`、L1/KL denominator、learned query、temporal weight、zero sentinel 与 H/K/R probes，公共事实层为 `PASS WITH WARNING`；本地 OpenPiVLA action schema/controller 仍 WARN。

### Batch D：Diffusion Policy（public facts independently reviewed）

- [Diffusion Policy 条件扩散、Horizon 与 Receding-Horizon Claim-to-Code](vol_03_diffusion_policy_claim_to_code.md)：覆盖 `VLA-ACT-018..022`，并补 `VLA-ACT-017` 的 diffusion 对照。
- 已核对 arXiv `2303.04137v5`、`real-stanford/diffusion_policy@5ba07ac...` 与 frozen `diffusers=0.11.1` scheduler。
- 关键 warning：paper 提出的 warm-start 未出现在 frozen policy；paper main text / table / config / runtime 的 inference steps 分别出现 10 / 16 / 8 / 16；boundary padding 是 repeat-edge target，不是 valid-mask padding。
- [独立复核](vol_03_diffusion_policy_independent_fact_review.html) 已完成 epsilon/sample target、full-mean mask、boundary repeat、To/Tp/Ta/Kd/R、warm-start gap、10/16 steps 与 sim/real queue probes；本地 scheduler/normalizer/controller 仍 WARN。

### Batch E：Flow Matching / π0（public facts independently reviewed）

- [Flow Matching 基础、π0 特化与 ODE Claim-to-Code](vol_03_flow_matching_pi0_claim_to_code.md)：覆盖 `VLA-ACT-023..030`，并完成 `VLA-ACT-026` 的 Diffusion epsilon / Flow velocity 对照。
- 已核对 arXiv `2210.02747v2`、`facebookresearch/flow_matching@11568d3...`、π0 v4 与 `openpi@15a9616...`。
- 关键 warning：基础论文 OT path 保留 \(\sigma_{\min}\)，后续 package 的 `CondOTProbPath` 才使用 exact endpoint；current package 不是 2022 历史实现且 license 为 CC BY-NC 4.0；openpi Pi0 loss 对 configured D 维直接 mean。
- [独立复核](vol_03_flow_pi0_time_sign_independent_fact_review.html) 已完成 Theorem 2、`sigma_min` endpoint、`t=1-τ`、velocity/sign/dt 与 10-step oracle；本地 target/solver/valid-dim/controller 仍 WARN。

### Batch F：VLA 架构与动作执行（public facts independently reviewed）

- [VLA 架构、适配、延迟与动作执行 Claim-to-Code](vol_03_architecture_execution_claim_to_code.md)：覆盖 `VLA-ARCH-007..012` 与 `VLA-ACT-031..032`。
- 已核对 RT-2 v1、OpenVLA v3、Octo v2、π0 v4，以及 `octo-models/octo@241fb351...`、既有 frozen OpenVLA/openpi commits。
- 关键 warning：Octo 提供 `timestep_pad_mask & action_pad_mask` 的有效维正例，而 frozen Pi0 仍是 all-D mean；openpi timing 只分到 model/server/previous-total，未自动拆 vision、sampler、network 与 queue；上游 DROID `[10,8]` example 不能证明本地 controller contract。
- [独立复核](vol_03_architecture_execution_independent_fact_review.html) 已完成 RT-2 token/frequency、Octo readout/valid-count mask、openpi checkpoint→norm→transform、timing、chunk broker 与 DROID H/K probes；本地 checkpoint/latency/controller 仍 WARN。

## 4. OpenPiVLA 本地证据待核对表

| Claim / contract | 当前边界 | 进入 VOL 03 正文前需要的证据 |
| --- | --- | --- |
| base checkpoint / backbone | local formal source 使用 Qwen3-VL + LoRA；immutable formal checkpoint/load smoke 仍缺 | checkpoint manifest、processor/base revision、加载日志 |
| action dimension / axis order / unit | recipe/smoke 为 D=72，但 formal JSON 每行 `limit=16`；axis/unit 未核 | strict schema、parser、policy config、output transform |
| action horizon / executed prefix / replan | formal H=15；official WebSocket artifact 为 H=4/D=7 的平行 lineage | formal generation/parser、rollout client 与 controller loop |
| normalization / denormalization | formal JSON route 未发现 normalizer/controller round-trip | norm stats、transform code、sentinel 回放 |
| archived 97.4% | 归档最强 eval，不等于当前 formal training 直接所得 | eval summary、checkpoint ID、task/trial/split/protocol |
| personal contribution | 上游架构不是个人原创 | local diff、设计记录、run ledger、本人负责边界 |

## 5. 来源质量门

1. 论文支持方法定义；官方 repo 支持实现和接口；本地 artifact 才支持个人项目事实。
2. 每个显示公式必须写变量 shape、目标张量、mask 和 train/infer 映射。
3. 同名术语先核实现：action horizon、chunk、window、replan、control step 不默认同义。
4. 对比表只在 checkpoint、数据、任务、trial、controller 和 success protocol 可比时讨论指标。
5. 若源码路径或项目 artifact 缺失，标为 `未核实`，不以“通常实现”补齐本地事实。

## 6. Registry reconciliation 与下一批工作

1. Audit A–F 的 public paper/code independent review 均已完成；A/C/D/F 为 PASS WITH WARNING，B/E 的 claim-to-code registry 仍保留 WARN（其独立事实切片已单独记录），local/runtime/oral warning 不因此消失。
2. `VLA-ARCH-001..012` 与 `VLA-ACT-001..032` 的 knowledge/cards 44/44 已完成；44 张题卡全部 `unseen`。
3. OpenPiVLA local gates 已新增 formatter、full-sequence CE、72→16 lossy serialization、parser absence 与 official/Qwen parallel-lineage 证据；checkpoint、normalizer、controller、97.4 lineage 与 ownership 仍开放。
4. 下一 bounded slice 优先做候选人 ownership confirmation，或补 immutable formal checkpoint/generation bundle；无候选人回答时继续关闭 VOL 02 source registry 生命周期。

## 7. 本 registry 能证明与不能证明什么

| 结论 | 状态 |
| --- | --- |
| 九篇核心 paper/technical report 与七个 official repo 的用途和冻结版本已登记 | `checked` |
| Audit A–F public facts 均有独立 review 页面 | `checked` |
| VOL 03 knowledge/cards 44/44、stable ID 无缺口 | `checked / all unseen` |
| 本地 OpenPiVLA formal Qwen parser/controller round-trip | `missing` |
| archived 97.4 与 formal Qwen/official checkpoint 的同一 lineage | `unverified` |
| candidate 对 trainer/formatter/diagnostics 的个人 ownership | `pending confirmation` |
| 浏览器 desktop/narrow visual QA | `PASS WITH WARNING (localhost 1440×1000 / 800×1000；local runtime/ownership/oral gates remain open)` |

因此本 registry 的 verdict 保持 `WARN`：来源和 public facts 已闭环，项目真实性与训练掌握尚未闭环。
