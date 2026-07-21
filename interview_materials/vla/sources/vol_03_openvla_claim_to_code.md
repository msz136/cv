# VOL 03 Source Audit A：OpenVLA Action Token 与 I/O Claim-to-Code

> 审计日期：2026-07-16  
> 状态：`independent_fact_reviewed / endpoint_mask_checked / project_boundary_pending / WARN`  
> 论文版本：OpenVLA arXiv `2406.09246v3`  
> 官方仓库：`openvla/openvla` frozen commit `c8f03f48af692657d3060c19588038c7220e9af9`  
> 对应题目：`VLA-ARCH-001..005`、`VLA-ACT-002..004`  
> 本页问题：OpenVLA 到底接收什么、训练什么、生成什么、怎样把 token 还原为机器人动作？哪些事实不能迁移到 OpenPiVLA / FAST？

## 1. 结论先行

1. **OpenVLA 不是“VLM 外接连续 action head”**。冻结代码中的 `OpenVLA` 继承 `PrismaticVLM`，由 DINOv2 + SigLIP 视觉特征、投影器和 Llama-2 语言模型组成；动作通过语言模型末尾词表 token 自回归生成。[1][2]
2. **旗舰 OpenVLA 的基础 I/O 是单主视角 RGB + 语言 → 单步连续动作向量**。默认数据路径只加载 `image_primary` 和语言，`load_proprio=False`、`window_size=1`、`future_action_window_size=0`。[1][2]
3. **训练优化目标是 masked next-token cross-entropy**，不是连续动作 L1。代码中的连续 L1 用于把预测/标签 token 解码后做监控；默认配置还可把 stop/EOS token 纳入 CE，但 action accuracy mask 不把 EOS 算作 action token。[1][2]
4. **动作先按数据集每维 q01/q99 归一化到 [-1,1]，再逐标量离散**。论文称每维 256 bins；冻结实现使用 256 个均匀网格点、255 个 bin center，并把上端点折到最后 center，同时仍占用末尾 256 个词表 token。[1][2]
5. **推理生成 token 数等于所选 `unnorm_key` 的动作维数**；随后 token → normalized scalar → q01/q99 反归一化。模型输出的不是 controller 命令语义本身，坐标轴、单位和执行频率仍属于环境/机器人接口。[2]
6. **OpenVLA 2024 的 tokenization 不是 FAST**。OpenVLA 是“每个动作维度一个离散 token”的标量方案；FAST 是后续的 action-window 频域/BPE 路线。两者不能因为都输出 token 就混写。[1][3]
7. **本地 OpenPiVLA 页不能用 OpenVLA 源码补证据**。其中的 FAST、Qwen3-VL、assistant-side JSON/token、action horizon 10 与归档 97.4% 都需要 openpi/FAST 或本地 artifact 单独证明。[3]

## 2. 证据层级与审计范围

| 层级 | 本页使用方式 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| 论文原文 | OpenVLA v3 的 `3.2`、`3.3`、`3.4`、`3.5`、`6` | 方法定义、旗舰模型、公开实验和局限 | frozen commit 的逐行行为；个人项目事实 |
| frozen official repo | commit `c8f03f...` 的 Python/README/config | tokenizer、mask、I/O、normalization、训练/推理路径 | 本地 OpenPiVLA 实际采用了同一实现 |
| 本地项目页 | `../../03_openpivla_action_modeling.html` | 当前整理出的口述口径和待补证据项 | 未附原始 config/log 的强指标与因果归因 |
| 同源推断 | 由论文与 frozen code 联合推出 | tensor contract、公式到代码的映射 | 未出现的 action axis、controller、真实 rollout 行为 |

本页只审计原始 OpenVLA 主路径。OpenVLA-OFT、π0/π0.5、openpi、FAST、ACT、Diffusion Policy 与 Flow Matching 分属后续 source batch，除边界提示外不在这里提前总结其实现。

## 3. 架构与输入输出合同

### 3.1 旗舰架构

论文与 README 将 `openvla-7b` 描述为：Prismatic 7B VLM，视觉侧融合 DINOv2 与 SigLIP，语言侧使用 Llama-2。[1][2] 冻结代码把这一声明落实为：

```
RGB image
  ├─ DINOv2 ViT patches ─┐
  └─ SigLIP ViT patches ─┴─ concatenate channel features
                                  │
                                  v
                         fused MLP projector
                                  │
                                  v
task prompt tokens + projected image patches + Llama-2
                                  │
                                  v
                         autoregressive action tokens
                                  │
                                  v
                      scalar decode + denormalization
```

代码证据：

- [`conf/models.py#L491-L497`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/conf/models.py#L491-L497)：224px DINO-SigLIP、Llama-2 7B 与 fused GELU MLP 配置。
- [`dinosiglip_vit.py#L20-L29`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/backbones/vision/dinosiglip_vit.py#L20-L29) 与 [`#L142-L160`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/backbones/vision/dinosiglip_vit.py#L142-L160)：两个视觉 encoder 的具体标识和 patch feature 拼接。
- [`prismatic.py#L38-L75`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlms/prismatic.py#L38-L75)：vision backbone、LLM backbone 与 projector 三部分。
- [`prismatic.py#L367-L420`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlms/prismatic.py#L367-L420)：视觉 patch 被投影后插在 BOS 与其余文本 token 之间，patch labels 设为 `IGNORE_INDEX`。

**面试安全说法**：OpenVLA 的“action head”不是独立连续 MLP；在原始路径里，Llama-2 的 LM head 直接预测被复用为 action vocabulary 的 token，`ActionTokenizer` 负责非参数化的连续值 ↔ token 映射。

### 3.2 训练样本 I/O

`RLDSBatchTransform` 直接读取：

| 字段 | frozen code 行为 | shape / 语义 |
| --- | --- | --- |
| `observation.image_primary[0]` | 变为 PIL image 后走 DINO/SigLIP transform | 单张主视角 RGB |
| `task.language_instruction` | decode、lowercase，写入固定问句 prompt | 一条任务语言 |
| `action[0]` | q99 normalization 后逐维 tokenization | 当前时刻动作向量 `a∈R^d` |
| proprio / history / extra view | 默认不加载 | 原始旗舰路径不存在 |

直接证据：

- [`datasets.py#L38-L67`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/datasets.py#L38-L67)：image、language、current action 和 labels 构造。
- [`datasets.py#L91-L105`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/datasets.py#L91-L105)：只加载 primary camera、`load_proprio=False`、`window_size=1`、`future_action_window_size=0`。
- 论文 [`Section 6`](https://arxiv.org/html/2406.09246v3#S6)：明确将多图、proprio 与 observation history 列为未来工作。

因此，`VLA-ARCH-004` 的正确回答不能说“OpenVLA 已把多视角和 proprio 全部融合”；它应以 OpenVLA 作为反例，再由 Octo/π 系列等后续来源补完整比较。

### 3.3 推理 I/O

`predict_action` 的公开合同是：

```python
def predict_action(image, instruction, unnorm_key):
    # 1. Build the same language prompt used during training.
    prompt = build_prompt(instruction.lower())

    # 2. Transform one RGB image and run autoregressive generation.
    token_ids = generate(
        image=image,
        prompt=prompt,
        max_new_tokens=get_action_dim(unnorm_key),
    )

    # 3. Decode exactly d final tokens to normalized scalar actions.
    normalized_action = decode_last_d_tokens(token_ids)

    # 4. Select dataset statistics and map normalized dimensions back to units.
    return q99_unnormalize(normalized_action, stats=norm_stats[unnorm_key])
```

这段伪代码映射到 [`openvla.py#L35-L103`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlas/openvla.py#L35-L103)。动作维数来自 [`openvla.py#L121-L131`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlas/openvla.py#L121-L131) 中所选数据集统计的 `q01` 长度，而不是一个跨机器人固定常数。

## 4. Action normalization 与 tokenizer 的精确数学

### 4.1 q01/q99 归一化

令原始动作 `a∈R^d`，训练集每维统计为 `q_i^{01}`、`q_i^{99}`，归一化 mask 为 `m_i∈{0,1}`。冻结实现等价于：

\[
\tilde a_i=
\begin{cases}
\operatorname{clip}\left(
2\frac{a_i-q_i^{01}}{q_i^{99}-q_i^{01}+\epsilon}-1,\,-1,\,1
\right), & m_i=1,\\
a_i, & m_i=0.
\end{cases}
\]

变量与直觉：`d` 是当前数据集 action dimension；q01/q99 把大部分训练动作铺到 [-1,1]，并通过 clipping 降低极端值对离散分辨率的影响。实现映射在 [`data_utils.py#L48-L103`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/rlds/utils/data_utils.py#L48-L103)，统计计算在 [`#L240-L260`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/rlds/utils/data_utils.py#L240-L260)。OXE 路径默认不归一化最后的 gripper 维，见 [`materialize.py#L31-L43`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/rlds/oxe/materialize.py#L31-L43)；具体 gripper 标准化仍受各 dataset transform 约束。

### 4.2 normalized scalar → token ID

令 `V` 为基础 tokenizer 的词表大小。代码构造 256 个均匀网格点

\[
e_j=-1+\frac{2j}{255},\qquad j=0,\ldots,255,
\]

然后对每个归一化标量做 `np.digitize`：

\[
b_i=\operatorname{digitize}(\operatorname{clip}(\tilde a_i,-1,1),e),\qquad
t_i=V-b_i.
\]

这里 `b_i∈{1,\ldots,256}`，因此 `t_i` 落在词表末尾 256 个 ID。直觉是把每个动作维当作一个“特殊词”，使 LLM 能以标准 next-token prediction 生成动作。实现证据是 [`action_tokenizer.py#L13-L47`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/action_tokenizer.py#L13-L47)。

### 4.3 token ID → normalized scalar

代码以相邻网格点中心

\[
c_j=\frac{e_j+e_{j+1}}{2},\qquad j=0,\ldots,254
\]

作为重建值，并计算

\[
j_i=\operatorname{clip}(V-t_i-1,0,254),\qquad
\hat{\tilde a}_i=c_{j_i}.
\]

变量与实现：`j_i` 是 255 个 center 的索引；由于 `np.digitize` 可能返回 256，代码把最后一个索引折叠到 `c_{254}`，见 [`action_tokenizer.py#L49-L68`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/action_tokenizer.py#L49-L68)。

**论文—代码精确边界**：

- 论文 `3.2` 的抽象表述是“每维 256 bins、得到 0…255 的整数、覆盖末尾 256 tokens”。[1]
- frozen code 的实际重建表有 255 个 center；最大端点对应的两个离散索引最终映射到同一个最后 center。[2]
- 因而面试中可说“论文层是 256-way action token；这个 commit 的 decode 有 255 个 center 并处理上端点”，不要无条件说“存在 256 个不同连续重建值”。

### 4.4 反归一化

\[
\hat a_i=
\begin{cases}
\frac{\hat{\tilde a}_i+1}{2}(q_i^{99}-q_i^{01})+q_i^{01}, & m_i=1,\\
\hat{\tilde a}_i, & m_i=0.
\end{cases}
\]

该公式直接映射 [`openvla.py#L89-L103`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlas/openvla.py#L89-L103)。它只恢复数据集 action units；代码没有证明各轴最终如何进入某个 controller，因此 controller axis/order/频率仍需具体 eval 或机器人 wrapper 证据。

## 5. 训练目标、labels 与监控指标

令 `y_1,\ldots,y_T` 是 prompt、可选 stop token 与 action tokens 组成的语言序列，`M_k` 表示第 `k` 个 label 是否参与 loss。训练目标为：

\[
\mathcal L_{\mathrm{CE}}
=-\frac{1}{\sum_k M_k}
\sum_{k=1}^{T}M_k\log p_\theta(y_k\mid y_{<k},I),
\]

其中 `I` 是投影后的图像 patch 条件。`RLDSBatchTransform` 把 prompt 部分设为 `IGNORE_INDEX=-100`；`PrismaticVLM.forward` 又给插入的视觉 patch 位置补 `IGNORE_INDEX`。默认 `predict_stop_token=True` 时，代码保留 `len(action)+1` 个尾部 labels，意味着 action token 加 stop/EOS；关闭后再 mask 最后一位。[2]

实现链：

1. [`datasets.py#L44-L67`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/datasets.py#L44-L67)：prompt/action token 序列和 prefix mask。
2. [`prismatic.py#L388-L420`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlms/prismatic.py#L388-L420)：图像 patch 插入及 patch-label mask。
3. [`base_strategy.py#L285-L332`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/training/strategies/base_strategy.py#L285-L332)：`output.loss.backward()` 是优化路径；action token accuracy 与 continuous L1 在其后计算并提交为 metrics。

**关键面试防线**：

- 不能说“OpenVLA 用 L1 直接回归连续动作”；它用 token CE 训练。
- 也不能说“训练 loss 包含所有文本位置”；prompt 与 image patch labels 被 mask。
- 连续 L1 是将 argmax token 解码后的离线量化/预测误差指标，不等于 closed-loop success。

## 6. 全量微调、单图限制与 action chunk 边界

### 6.1 旗舰训练是全量微调

论文 `3.4` 说明最终训练中微调全部 7B 参数，并认为 vision encoder fine-tuning 对精细控制重要。[1] frozen config 的旗舰 OXE 变体继承 `freeze_vision_backbone=False`、`freeze_llm_backbone=False`；`train.py` 将其解析为 `vla-full-train`。[2]

- [`conf/vla.py#L63-L91`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/conf/vla.py#L63-L91)
- [`conf/vla.py#L124-L136`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/conf/vla.py#L124-L136)
- [`train.py#L159-L180`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/vla-scripts/train.py#L159-L180)

LoRA、冻结视觉 encoder、只解冻最后一层是支持的适配选项，不是旗舰预训练 recipe 的同义词。

### 6.2 base OpenVLA 不是 chunk policy

论文的对照实验把 matched Diffusion Policy 配置成与 OpenVLA 一样：单图、无 proprio、无历史、单步相对动作；`Section 6` 又把 action chunking 列为未来改进方向。[1] frozen dataset config 的 `future_action_window_size=0` 与之对齐。[2]

所以：

- “OpenVLA 支持自回归生成多个 action dimensions”不等于“它预测未来 H 步 action chunk”。
- 生成 `d` 个 token 是一个 `d` 维当前动作，不是 `H×d` 的时间窗口。
- OpenPiVLA 页面里的 `horizon=10` 必须由 openpi/FAST 或本地 eval config 证明，不能回填成 OpenVLA 机制。

## 7. Claim-to-code 总表

| Claim | 论文证据 | frozen code 证据 | 判定 | 面试口径 |
| --- | --- | --- | --- | --- |
| 视觉侧融合 DINOv2 + SigLIP，语言侧 Llama-2 7B | Abstract / `3.4` | `conf/models.py`、`dinosiglip_vit.py` | direct | “Prismatic VLM backbone，融合两套视觉特征后投影进 Llama-2” |
| 输入为 image + language | `3.2` | `RLDSBatchTransform`、`predict_action` | direct | “旗舰路径是单 RGB 主视角 + 任务语言” |
| 默认包含 proprio / history / multi-view | `6` 明确列为未来工作 | `load_proprio=False`、primary-only、window=1 | rejected | 不得这样描述原始 OpenVLA |
| 每个动作维度离散为 action token | `3.2` | `ActionTokenizer` | direct with nuance | 论文 256-way；代码精确讲 256 token IDs / 255 centers |
| 占用 Llama 词表末尾 256 token | `3.2` | `V-b_i` 映射 | direct | “复用 least-used tail tokens，不新增完整 256 special tokens” |
| 训练用 action-token CE | `3.2` | masked labels + `output.loss.backward` | direct | CE 是优化目标；L1 是 metric |
| 生成长度是固定 7 | README Bridge 示例是 7-DoF | `get_action_dim(unnorm_key)` | rejected as universal | 维度由 dataset norm stats 决定 |
| q01/q99 normalization | `3.2` | `BOUNDS_Q99` 与 unnormalize | direct | 训练、checkpoint 与 eval 必须共享同一 stats key |
| 原始 OpenVLA 使用 action chunk | `6` 列为未来方向 | `future_action_window_size=0` | rejected | 单步动作；chunk 属其他路线/后续改造 |
| OpenVLA code 证明本地 FAST/Qwen/97.4% | 无 | 无 | rejected | 只能进入 OpenPiVLA 独立证据合同 |

## 8. 与 OpenPiVLA / FAST 的真实性边界

| 名称 | 本页已核实的 action 表示 | 与本地项目的关系 | 当前状态 |
| --- | --- | --- | --- |
| OpenVLA | q01/q99 scalar normalization → 每维离散 token → LM next-token CE → 单步动作 | 只能提供 action-token 对照和审计方法 | upstream verified |
| FAST | action window 的频域变换、量化与 BPE | 本地页主要口述机制；不能由 OpenVLA 证明 | 下一个 source batch |
| openpi / π0 | 本页不展开；需核对 flow action expert、state/action mask、solver | 本地项目命名和 policy/eval contract 的主要上游候选 | 下一个 source batch |
| 本地 Qwen formal reproduction | assistant-side action JSON/token + LoRA | 工程折中与训练语义恢复，不等同于 OpenVLA tokenizer 或原 action expert | local artifact pending |
| `224_h10_40000` / 97.4% | 与 OpenVLA paper/repo 无直接关系 | strongest archived eval，需 checkpoint + summary + protocol | local evidence pending |

对本地项目最重要的改写原则：

1. 讲“action token”时先报具体 tokenizer 名称，不把 OpenVLA scalar bins、FAST 和 JSON serialization 混成同一算法。
2. 讲“horizon”时说明它是 dataset target horizon、model output horizon 还是 controller execution/replan interval。
3. 讲“97.4%”时先报 run/checkpoint/protocol，再讲方法；不能用上游 architecture 代替本地归因证据。

## 9. 对 Phase 0 题目的支持状态

| Question ID | OpenVLA 证据覆盖 | 状态 | 仍缺 |
| --- | --- | --- | --- |
| VLA-ARCH-001 | VLM 通过可执行 action token 成为 policy | ready for OpenVLA example | 传统 policy 与其他 VLA 对照 |
| VLA-ARCH-002 | 单图、语言、dataset-specific action stats 与 output | ready for OpenVLA subtype | generic proprio/multi-view schema |
| VLA-ARCH-003 | vision backbone + projector + LLM；无独立 continuous head | partial | π0 action expert / continuous heads |
| VLA-ARCH-004 | 直接证明原 OpenVLA 缺 multi-view/proprio/history | negative evidence ready | Octo/π 系列正例 |
| VLA-ARCH-005 | tokenization、mask、generation、decode、unnormalize 全链 | ready | independent fact review |
| VLA-ACT-002 | q99 normalize / dataset-key unnormalize | ready for OpenVLA | openpi normalizer 与 controller |
| VLA-ACT-003 | quantile、网格、token、endpoint nuance | ready | 量化误差实验与分布漂移案例 |
| VLA-ACT-004 | tail-vocab mapping、begin index、decode | ready | FAST vocab/BPE 对照 |

这些题仍然只是 `source-ready`，不是候选人已经掌握；正式题卡生成后仍应标为 `unseen`。

## 10. 风险与下一步

1. **独立审查已完成**：paper v3、frozen tokenizer/dataset/model/strategy 与 endpoint probe 已在 [独立复核页](vol_03_openvla_endpoint_independent_fact_review.html) 直接核对，公共事实层为 `PASS WITH WARNING`；本页整体仍因本地项目边界保持 `WARN/PENDING`。
2. **paper/code 数值表述要分层**：256 bins 是论文抽象；255 centers 是此 commit 的 decode 行为。
3. **checkpoint/config 仍是变量**：Hugging Face exported implementation 与 Prismatic path 均存在，具体面试答案要报所使用路径。
4. **OpenPiVLA raw artifacts 未进入本页**：不能据现有项目 HTML 确认 action axis、horizon、normalizer、controller 或 97.4% checkpoint。
5. π0、FAST 与 frozen `openpi` 已在后续 Audit B/E/F 页面分别复核；下一步只收集本地 OpenPiVLA checkpoint/action schema/normalization/controller artifact 或进行真实口述，不把 OpenVLA 上游合同迁移为个人项目事实。

## 参考文献（References）

1. Kim et al., [OpenVLA: An Open-Source Vision-Language-Action Model](https://arxiv.org/html/2406.09246v3), arXiv v3, 2024.
2. [openvla/openvla](https://github.com/openvla/openvla/tree/c8f03f48af692657d3060c19588038c7220e9af9), frozen commit `c8f03f48af692657d3060c19588038c7220e9af9`, accessed 2026-07-16.
3. 本地项目页：[OpenPiVLA：FAST 动作表示、Metax 迁移与策略评估复现](../../03_openpivla_action_modeling.html)，当前为整理材料而非原始 artifact manifest。
