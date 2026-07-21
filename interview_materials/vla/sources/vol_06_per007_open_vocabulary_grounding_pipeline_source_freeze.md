# VOL 06 PER-007 Source Freeze：Open-vocabulary Grounding Pipeline 与 Text–Region Matching

> 状态：`source_frozen / VLA-PER-007 / primary_official_checked / local_generative_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片只冻结 text-conditioned detector/grounder 的 prompt、query–token score、box/text threshold、phrase binding、坐标后处理与 NMS policy；不生成 knowledge/card，不把公开 detector 机制归为个人项目实现。

## 问题（Question）

从“输入一句目标描述”到“得到带 phrase、score 和 box 的 grounded regions”，中间到底有哪些可审计阶段？`box_threshold`、`text_threshold` 和 NMS 是否是同一个门？Grounding DINO 的 query–token logits 如何绑定 phrase？本地 OPD 是不是这类显式 detector pipeline？

本页冻结的最小数据流是：

```text
image + candidate labels / referring expression
  -> image/text preprocessing
  -> visual and text features
  -> language-guided query selection + cross-modal decoder
  -> query-token logits + normalized boxes
  -> query filtering by box score
  -> token filtering + phrase reconstruction
  -> coordinate conversion / optional downstream NMS
  -> typed grounded-region manifest
```

## 1. 结论先行

1. Grounding DINO 论文 v5把 open-set detector 的跨模态融合分成 feature enhancer、language-guided query selection 和 cross-modality decoder；这支持 pipeline taxonomy，不支持本地项目已复现论文指标。
2. 冻结官方代码的分类输出不是单一 class ID，而是 `pred_logits∈R^{B×Q×L_max}`：每个 object query 对文本 token 产生分数；`pred_boxes∈R^{B×Q×4}` 为 normalized `cxcywh`。
3. `ContrastiveEmbed` 直接计算 query embedding 与 encoded text 的点积，并把 padding token mask 为 `-inf`；官方 inference 再对 logits 做 sigmoid。
4. `box_threshold` 先按每个 query 的最大 token probability 决定是否保留 query；`text_threshold` 再决定哪些 token 拼成 phrase。两者不能合并，也不等于 NMS。
5. 冻结的 GroundingDINO `inference.py` 没有 NMS 调用：它做 threshold、phrase extraction 与 `cxcywh→xyxy`。若部署另加 NMS，必须单独冻结 IoU threshold、class/phrase grouping、排序和 max-detections。
6. Transformers 4.57.1 的 `GroundingDinoProcessor` 会把候选 label 小写并用句点连接；post-process 从 `input_ids` 重建 `text_labels`，而传入的 `text_labels` 参数当前不参与绑定。API key/type 语义存在版本风险，必须 pin revision。
7. 本地 OPD 冻结文件体现的是 Qwen3-VL 生成 tagged point/box/text 的 SFT + autoregressive generation + parser/scorer 路径；当前 repo 静态搜索没有发现 GroundingDINO/NMS import 或调用。它可作为“生成式 grounding”对照，不能写成显式 open-vocabulary detector 已部署。

## 2. Primary / official / local source ledger

SHA-256 对 2026-07-19 访问到的 UTF-8 文本按 LF 规范化后计算；本地文件使用原始文件 SHA。来源只支持其所在层，不能把上游实现、静态 absence search 或数据字段归为个人贡献。

| 来源 | 类型 / revision | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [Grounding DINO paper v5](https://arxiv.org/abs/2303.05499v5) | primary；arXiv API v5，updated 2024-07-19；读取 2026-07-19 | `B73D956641C71C5F006F618049BEA3F544BE17F555E74F8BD8F92F7A0ED1A8F0` | open-set framing；feature enhancer、language-guided query selection、cross-modality decoder | 本地 checkpoint、阈值、latency、robot success 或个人 ownership |
| [GroundingDINO README](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/README.md) | official-code；commit `856dde20...`；Apache-2.0 repo | `D69CF3FD022661E6BE19C56A421020F3EE9E027375020EF6A3DEF0149DDF9595` | 官方入口、prompt 示例、checkpoint/config 使用和 license 线索 | 任意本地系统实际调用该 repo |
| [groundingdino.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/models/GroundingDINO/groundingdino.py) | official-code；同一 commit | `CDFB48D5B15D6B98F3D2002F59AE4730740A1ECFBAEBA324F6840C5E4666A5B8` | tokenizer/text mask、`max_text_len=256`、query/text/box heads、`pred_logits/pred_boxes` contract | frozen helper之外的部署后处理或性能 |
| [GroundingDINO utils.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/models/GroundingDINO/utils.py) | official-code；同一 commit | `2827BA921ACAA263DB7533AFB6A818473A957FB2EF559C4F3407DA72028A0842` | `ContrastiveEmbed` 的 query–text dot product、padding mask 和 max-text padding | calibrated probability、cosine normalization 或 temperature scaling |
| [GroundingDINO inference.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/util/inference.py) | official-code；同一 commit | `0C06C5DD2FA46AE89A9FA376C0EAA383D12E7FC21AA65D662BCF3E758D26B598` | caption normalization、box/text thresholds、phrase extraction、score 与 box conversion；无 NMS call | threshold calibration、duplicate-free guarantee 或项目 scorer |
| [Transformers GroundingDINO modeling](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino/modeling_grounding_dino.py) | official-code；`v4.57.1 / 8cb5963...`；Apache-2.0 | `BA98EB52ACBD8A7E36BAB581FD0F9B092FED3579E37CD6E69C55EA153504B2E0` | release-pinned model output and implementation bridge | 本地实际加载的 class/config/checkpoint |
| [Transformers GroundingDINO processor](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino/processing_grounding_dino.py) | official-code；同一 release | `07204D1BBFAF9A4F8E9367C7B303883F19850DBEA9C98F45302371C4F000A239` | label merge、`threshold/text_threshold`、phrase decode、`target_sizes` 与 output keys | 任意其他 Transformers version 的 key/type 兼容性 |
| [GroundingDINO LICENSE](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/LICENSE) | official-code；Apache-2.0 文本 | `B403C98EC1FFACCB0124632592A3D99642CDDC3031CA412B402568E6C06C202A` | repo source license 线索 | checkpoint、dataset 或第三方 asset 的授权 |
| [PER-001 Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html) | repository-reviewed bridge | review SHA 见对应记录 | point/box/text 表示、坐标、parser/scorer 边界 | PER-007 pipeline 已被 PER-001 完整覆盖 |
| [PER-006 Source Freeze](vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html) | repository-reviewed bridge | review SHA 见对应记录 | raw→processed→grid→token 与 camera/order contract | detector matching、threshold 或 phrase binding |
| `build_clean_grounding_pool.py` | local-evidence；`muxi@756e27e...` | `A7A5906E11EA687C6FD0DEC40F3D30922A91B538EB98C740230227F9FF943087` | annotation clip/filter、`xyxy→0..1000`、tagged box SFT row | online detector、query-token score、NMS 或 deployed checkpoint |
| `build_expert_mixes_seed0.py` | local-evidence；同一 HEAD | `60DFDF46FDAC8EB9DBBE38A13298D6D71819EB7AD13F6B0D00A86B87032EABD0` | point/box extraction、expert mix 与 route metadata | learned detector/router 的独立效果 |
| `expert_sft.py` | local-evidence；同一 HEAD | `2A1D37F5912C91B952C529B3B80C8609D7E3105DC57BBDB2D906EA288B58EA98` | Qwen3-VL processor、image/text messages、prompt-masked causal labels | GroundingDINO、region proposals、box/text threshold 或 NMS |
| `eval_qwen_vl_raw_holdout.py` | local-evidence；同一 HEAD | `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B` | autoregressive `generate`、point/box/text parser 与 static metrics | explicit open-vocabulary detector、closed-loop robot result |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-007 只新增 |
| --- | --- | --- |
| PER-006 | image resize、pixel range、patch/grid/token、camera/order | detector 接收的 image/text 输入必须继承该 manifest |
| PER-001 | point/box/text schema、normalized/pixel coordinates、parser、IoU/point metric | query-token matching、two-threshold selection、phrase reconstruction、NMS policy |
| PER-008 | point/box/mask/text 表示选择 | 本页不评价哪种输出表示最适合 controller |
| PER-009 | matching objective、negative、loss/reduction | 本页只冻结 inference score contract，不展开训练损失 |
| PER-010 | metric/parser comparability | 本页只要求 output manifest；不把 threshold sweep 写成最终 benchmark |
| PER-012 | segmentation/depth/keypoint/affordance | 本页不把 SAM、depth 或 affordance head 合并进 detector source gate |

## 4. 冻结的 Grounding DINO pipeline

### 4.1 Prompt 与 token contract

冻结官方 helper 会先 `lower().strip()`，并确保 caption 以句点结尾。Transformers processor 对 candidate-label list 同样执行小写，再用 “`. `” 连接并补末尾句点。因此下面三项必须随 run 保存：

1. 原始用户表达；
2. 实际送入 tokenizer 的 normalized caption；
3. tokenizer/config revision、`input_ids`、attention mask 与 truncation。

官方 model 将文本截断到 `max_text_len=256`。这不是“最多256个类别”；它是 token-axis 上限。多词短语、标点、special tokens 和 padding 都占用/影响 token positions。

### 4.2 Query–token matching

冻结 `ContrastiveEmbed` 对 object-query feature $z_q$ 与 encoded-text token feature $e_t$ 做点积：

\[
s_{q,t}=z_q^\top e_t.
\]

其中 $q∈\{1,\ldots,Q\}$ 是 object query，$t∈\{1,\ldots,L\}$ 是有效文本 token；padding token 在代码中被 mask 为 `-inf`，然后输出 padding 到 `L_max=256`。该代码没有 cosine normalization 或 temperature，因此不能把 $s_{q,t}$ 口述成已校准的跨样本概率。

官方 inference 对 logits 做 sigmoid：

\[
p_{q,t}=\sigma(s_{q,t}).
\]

该值用于同一次 prompt 内的筛选；是否能跨 prompt、跨 checkpoint 或跨类别比较，需要单独 calibration evidence。

### 4.3 Box gate 与 phrase gate

query 保留规则为：

\[
\operatorname{keep}(q)=\mathbb{1}\left[\max_t p_{q,t}>\tau_{\mathrm{box}}\right].
\]

对已保留 query，phrase token mask 为：

\[
M_{q,t}=\mathbb{1}\left[p_{q,t}>\tau_{\mathrm{text}}\right].
\]

`τ_box` 控制“保留哪些 region query”，`τ_text` 控制“每个 region 绑定哪些 token”。若 `τ_text` 高于一个已保留 query 的全部 token probability，region 仍可能保留但 phrase 为空；因此 output schema必须允许 `empty/invalid/ambiguous phrase`，不能强行补最近 label。

### 4.4 Box conversion 与 NMS boundary

冻结 output box 是 normalized `cxcywh`。官方 helper只做：

```text
normalized cxcywh
  -> multiply [W,H,W,H]
  -> pixel cxcywh
  -> pixel xyxy
```

Transformers post-process则先 `center_to_corners_format`，再用 `target_sizes=(height,width)` 缩放。两条实现的方向一致，但调用方仍必须冻结 target size 是原图还是处理图，并继承 PER-006 的 inverse transform。

冻结的 `inference.py` 没有调用 NMS。不能把“官方 helper无 NMS”改写成“Grounding DINO 永不产生重复框”；它只说明当前 helper的后处理合同。若下游增加 NMS，至少记录：

- pre-NMS boxes/scores/phrases；
- IoU threshold；
- class-agnostic 还是按 canonical phrase grouping；
- score排序、max detections 与 tie-break；
- post-NMS indices；
- NMS 在坐标 inverse 前还是后。

## 5. Transformers 4.57.1 API contract

冻结 `GroundingDinoProcessor.post_process_grounded_object_detection` 的主要行为是：

| 字段 / 参数 | 冻结语义 | 风险 |
| --- | --- | --- |
| `threshold` | `max(sigmoid(logits), token-axis)>threshold` 才保留 query | 不是 IoU/NMS threshold |
| `text_threshold` | token probability 超阈值后从 `input_ids` decode phrase | 改变 phrase边界，不一定改变 box数量 |
| `target_sizes` | 按 `(height,width)` 把 relative boxes缩放到 pixel `xyxy` | 顺序写反或传 processed size 会错位 |
| `text_labels` argument | frozen code签名中存在，但当前不用于 phrase binding | 不能假设传入 list 就决定 output label |
| `text_labels` output | decoded string list | 与 `labels` key/type 的版本迁移需 pin |
| `labels` output | frozen code仍复制 decoded strings，并包 deprecation warning | 下游不能跨版本假设始终是 string 或 integer |

运行 manifest 至少保存 Transformers revision、processor class、output key/type snapshot 和一个 golden sample；只写“用了 Hugging Face pipeline”不够。

## 6. Deterministic threshold probe

以下是人工构造的 probability matrix，只验证冻结筛选逻辑，不代表模型输出或性能：

| Query | token probabilities | `τ_box=0.35` | `τ_text=0.25` phrase tokens |
| --- | --- | --- | --- |
| `q0` | `[0.90,0.20,0.81,0.01]` | keep | `t0,t2` |
| `q1` | `[0.34,0.33,0.01,0.01]` | drop | 不进入 phrase gate |
| `q2` | `[0.60,0.24,0.26,0.01]` | keep | `t0,t2` |

确定性结论：

1. 把 `τ_text` 从0.25提高到0.30，`q2` 仍保留，但 phrase从 `t0,t2` 变为 `t0`；
2. 把 `τ_box` 从0.35提高到0.65，只保留 `q0`；
3. 代码使用严格大于号，score恰等于 threshold 时不保留；
4. threshold probe不能证明真实校准、precision/recall 或 robot success。

## 7. Typed grounded-region manifest

一个能跨 detector、parser 和 controller 审计的最小结果应为：

```json
{
  "sample_id": "...",
  "image_id": "...",
  "camera_id": "...",
  "prompt_raw": "...",
  "prompt_normalized": "...",
  "prompt_hash": "...",
  "model_revision": "...",
  "processor_revision": "...",
  "query_index": 0,
  "score": 0.0,
  "score_semantics": "max_token_sigmoid",
  "phrase_text": "...",
  "phrase_token_indices": [],
  "box_cxcywh_norm": [],
  "box_xyxy_processed": [],
  "box_xyxy_original": [],
  "box_threshold": 0.0,
  "text_threshold": 0.0,
  "nms_policy": "none | explicit revision",
  "valid": true,
  "invalid_reason": null
}
```

`score_semantics`、threshold revision 与 prompt hash 是必要字段：同一个数值在 max-token score、class probability、cosine similarity或VLM sequence likelihood下不可直接比较。

## 8. 本地 OPD：生成式 grounding，不是显式 detector

冻结本地 HEAD为 `756e27e16adcfb3ccbfe98c2920dda42095b127f`；四个直接读取文件在该 HEAD下无未提交 diff。对 muxi 中 `*.py/*.yaml/*.yml/*.json` 的静态搜索未发现 `GroundingDINO/groundingdino/torchvision.ops.nms/nms(` 匹配。该 absence只支持“当前可搜索源码没有显式调用”，不排除远端环境、未归档脚本、外部服务或历史版本。

| 本地阶段 | 直接证据 | 与显式 detector 的差异 |
| --- | --- | --- |
| 数据清洗 | clip invalid box、过滤tiny/huge、转 `0..1000 xyxy`、构造 `<box>...` answer | 使用已有annotation生成SFT target，不产生region proposal/logit |
| Expert mix | point/box tag解析、pool quota与route metadata | route metadata不是query–token detector score |
| SFT | Qwen3-VL image/text messages；prompt token mask为 `-100`，对answer token做causal loss | 没有 `Q×L` region-token matrix或box/text threshold |
| Eval | `model.generate` 后解析point/box/text；算IoU、distance、text match | parser/scorer不是detector post-process；无pre-NMS region manifest |

安全表述：

> 我把显式Grounding DINO式query–token detection pipeline与本地OPD生成式tagged-coordinate pipeline分开审计。OPD可连接prompt/schema/parser/scorer和数据mix，但当前证据不支持“项目部署了GroundingDINO/NMS”或把静态grounding直接升级为机器人闭环。

## 9. Failure taxonomy 与补证顺序

| 层 | 失败 | 最小诊断 |
| --- | --- | --- |
| prompt/token | label顺序、句点、同义词、截断改变 | raw/normalized prompt、token IDs、prompt hash |
| matching | query对错token高分、padding泄漏、score不校准 | query-token heatmap、token mask、revision |
| selection | `τ_box` 导致漏检/冗余 | pre-threshold query score分布、matched sweep |
| phrase | `τ_text` 产生空/碎片/复合phrase | token indices、decoded phrase、invalid reason |
| geometry | `cxcywh/xyxy`、target size或inverse错误 | processed/original round-trip sentinel |
| duplicate | 下游NMS改变region/phrase关联 | pre/post NMS indices和policy |
| project | generative output被误称detector或robot success | pipeline type、raw outputs、controller/episode evidence |

补证顺序：先 pin prompt/model/processor → 保存 raw logits/boxes/input_ids → 复算 two-threshold output → 做坐标 round-trip → 明确 NMS policy → 再做 matched threshold/calibration evaluation → 最后才连接 action/robot success。

## 10. Source gate 结论与下一 bounded slice

已冻结：

1. Grounding DINO的三阶段跨模态架构与 `Q×L` query-token score contract；
2. prompt normalization、max-text truncation、box/text双阈值与phrase extraction；
3. normalized `cxcywh` 到 pixel `xyxy` 的后处理，以及 frozen helper无NMS的边界；
4. Transformers 4.57.1 output key/type与 `text_labels` argument未参与绑定的版本风险；
5. typed grounded-region manifest、deterministic threshold probe和failure taxonomy；
6. 本地OPD是生成式grounding对照，不是已证实的GroundingDINO detector。

当前 verdict为 `WARN`：公开机制已冻结，但本地没有raw query-token logits、detector checkpoint/config、threshold calibration、pre/post NMS artifact或机器人闭环证据。

`VLA-PER-007..009` source/knowledge/card现已同步，题卡保持`unseen`。下一 bounded slice只做PER-010 metric/parser source freeze，不生成knowledge/card，不修改任何mastery。

## References

1. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
2. [IDEA-Research/GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)：README、model、utils、inference与LICENSE指纹见source ledger。
3. [Transformers 4.57.1 Grounding DINO](https://github.com/huggingface/transformers/tree/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino)：modeling与processor指纹见source ledger。
4. [PER-001 Point / Box / Text Grounding Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html)。
5. [PER-006 Image Preprocess / Token / Camera Source Freeze](vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html)。
6. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
