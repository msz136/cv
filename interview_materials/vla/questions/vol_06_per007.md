# VOL 06 Perception / Grounding / Navigation：PER-007 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-PER-007`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-007 Open-vocabulary Grounding Pipeline Knowledge](../knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.html)；来源边界见 [PER-007 Source Freeze](../sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)。

## Open-vocabulary grounding、双阈值与生成式边界

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-PER-007</b> · Grounding DINO 式 open-vocabulary grounding 如何从文本得到带 phrase 的框？box/text threshold 与 NMS 分别做什么？</summary>

**面试意图**：判断你能否把“文本找框”展开为 prompt/token、query–token matching、双阈值、phrase、geometry 与 optional NMS 的可复算 pipeline，并区分显式 detector 与本地生成式 grounding。

**30 秒回答**：Grounding DINO输出query对文本token的`Q×L` logits和normalized box。先按query最大sigmoid分数过box threshold，再按text threshold选token重建phrase；坐标逆变换后才可选NMS。OPD是生成式坐标路径，不能借用显式detector的score语义。

**机制展开（约 2 分钟）**：feature enhancer→query selection→cross-modal decoder输出`[B,Q,L_max]` logits和`[B,Q,4]` normalized `cxcywh`。$s_{q,t}=z_q^\top e_t$经sigmoid；$\max_t p_{q,t}>\tau_{box}$保留query，$p_{q,t}>\tau_{text}$选token解码phrase，均用严格大于。`L_max=256`是token位置。box转processed `xyxy`后按PER-006 inverse回原图。官方helper无NMS；下游若添加，需冻结IoU、phrase grouping和pre/post indices。

**诊断 / 证据**：先保存 raw/normalized prompt、tokenizer 与 `input_ids`，再保存 raw `Q×L` logits、padding mask、query index、normalized box、两个 threshold、phrase token indices/text、processed/raw `xyxy`、transform revision 与 NMS trace。按 prompt/token→matching→query gate→phrase gate→geometry→NMS 顺序定位；threshold sweep 固定模型、processor、prompt、图像变换、split 与 seed，缓存 raw output 后重放。静态 probe 只证明严格 `>` 和两道门的逻辑，不证明 calibration、precision/recall 或机器人成功。

**项目挂钩**：本地 OPD 证据支持 annotation→tagged `<box>/<point>/text` SFT→Qwen3-VL `generate`→parser/scorer 的生成式 grounding，可讲 prompt/schema/parser、坐标与 evidence manifest；当前静态搜索没有显式 GroundingDINO/NMS 路径。安全表述是“能审计并对比两类 pipeline”，不能说项目部署了 Grounding DINO、route metadata 是 learned detector/router、静态 IoU 等于闭环成功，或用 Git/本次审计自动证明个人贡献。

**追问树**：`Q` 和 `L` 两个轴是什么？为什么 256 不是类别数？score 等于 threshold 时保留吗？提高 `τ_text` 为什么可能让 phrase 变空却不删 box？`text_labels` 参数一定决定输出 label 吗？官方 helper 没有 NMS 意味着什么？phrase-aware NMS 如何分组？怎样做 matched threshold sweep？OPD 与显式 detector 的 raw artifact 有什么不同？

**易错点**：把 query 当 class ID；把 max-token sigmoid 当跨 prompt 已校准概率；合并 box/text threshold；把 box threshold 叫 NMS threshold；只存 decoded phrase 不存 token indices；传错 `(height,width)` 或丢失 preprocess inverse；把 frozen helper 无 NMS 说成不会有重复框；把 OPD 的 box 文本输出说成显式 detector。

**危险答案**：说“Grounding DINO 最多支持 256 类”“每个 query 只匹配一个 class”“text threshold 只改置信度”“官方默认已经做 NMS”“HF 的 `text_labels` 直接决定 phrase”，或“OPD 能输出 box，所以项目使用了 Grounding DINO并证明机器人成功”。

**来源**：[1][2][3][4][5][6]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-007 Open-vocabulary Grounding Pipeline Knowledge](../knowledge/vol_06_per007_open_vocabulary_grounding_pipeline.html)：三阶段 pipeline、query–token math、双阈值、phrase、geometry/NMS、manifest 与项目边界。
2. [PER-007 Open-vocabulary Grounding Pipeline Source Freeze](../sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)：Grounding DINO v5、官方实现、Transformers 4.57.1 与本地 OPD 证据冻结。
3. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
4. [IDEA-Research/GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)。
5. [Transformers 4.57.1 Grounding DINO](https://github.com/huggingface/transformers/tree/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino)。
6. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
