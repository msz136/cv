# VOL 06 Perception / Grounding / Navigation：Open-vocabulary Grounding Pipeline（PER-007）

> 状态：`drafted / VLA-PER-007 / source_synced / card_synced / WARN`  
> 报告日期：2026-07-19  
> 证据截止：2026-07-19  
> 来源入口：[PER-007 Source Freeze](../sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)。  
> 前置知识：[PER-006 Image Preprocess / Token / Camera](vol_06_per006_image_preprocess_token_camera_contract.html)、[PER-001 Point / Box / Text Contract](vol_06_per001_grounding_coordinate.html)。
> 原子题卡：[VLA-PER-007](../questions/vol_06_per007.html)（`unseen`）。

## 问题（Question）

输入图像和目标文本后，open-vocabulary detector/grounder 如何从跨模态特征得到 region、score 和 phrase？`box_threshold`、`text_threshold`、NMS分别控制什么？为什么同样输出box，本地OPD生成式grounding不能被口述成Grounding DINO式显式detector？

本页回答：

1. Grounding DINO的feature enhancer、language-guided query selection与cross-modality decoder如何组成pipeline？
2. `Q×L` query–token logits的两个轴分别是什么？
3. query gate与phrase-token gate为什么是两个不同阈值？
4. phrase如何从token positions重建，prompt标点/顺序/截断为什么会改变结果？
5. frozen helper没有NMS意味着什么、不意味着什么？
6. 如何设计typed manifest、伪代码、failure taxonomy与项目真实性边界？

## 知识地图位置与边界

```text
PER-006 image/pixel/token/camera contract
  -> PER-007 open-vocabulary detector/grounder pipeline
  -> PER-008 output representation choice
  -> PER-009 training matching/loss
  -> PER-010 metric/parser comparability
  -> PER-015 perception-to-action gate

PER-001 point/box/text + coordinate contract
  <-> PER-007 phrase/region binding + threshold/NMS contract
```

PER-007只负责inference pipeline和可观测接口：prompt如何进入、query如何与text token匹配、哪些query/phrase被筛选、box如何后处理。训练loss属于PER-009，最终metric/scorer属于PER-010，point/box/mask/text表示选择属于PER-008。

## 1. 30秒直觉：不是“文本分类+框”

显式open-vocabulary grounding的中间对象不是一个class ID，而是一组object queries与文本tokens之间的score matrix。每个query同时有一个normalized box；先用query的最大token score筛掉低置信region，再用另一个阈值决定该region绑定哪些tokens并重建phrase。最后才做坐标转换和可选NMS。

因此一个完整回答至少说清四件事：

1. prompt/token contract；
2. `query×token` score semantics；
3. box gate与phrase gate；
4. geometry/NMS/output manifest。

只说“模型输入文字，输出框”无法解释空phrase、复合phrase、重复框、阈值变化、token截断或坐标错位。

## 2. Pipeline总览

Grounding DINO论文把language–vision fusion概念上分成三个阶段：

| 阶段 | 直觉 | 专业表述 | 主要可观测量 |
| --- | --- | --- | --- |
| Feature enhancer | 先让图像和文本上下文互相增强 | multi-scale visual features与encoded text进行cross-modal feature enhancement | visual/text feature shape、mask、revision |
| Language-guided query selection | 从图像候选中选与文本更相关的queries | text-conditioned encoder proposals初始化object queries | proposal/query index、initial reference |
| Cross-modality decoder | query在解码时继续读取图像和文本 | decoder updates query features并预测query-token logits与boxes | decoder query、`pred_logits`、`pred_boxes` |

冻结的数据流可画为：

```text
raw image + raw prompt
  -> PER-006 image transform + normalized prompt/tokenization
  -> visual features + encoded text
  -> feature enhancer
  -> language-guided query selection
  -> cross-modality decoder
  -> pred_logits [B,Q,L_max] + pred_boxes [B,Q,4]
  -> sigmoid + query threshold
  -> token threshold + phrase decode
  -> cxcywh-to-xyxy + PER-006 inverse
  -> optional explicit NMS
  -> typed grounded-region manifest
```

这里`B`是batch size，`Q`是object query数，`L_max`是文本token轴上限。`L_max=256`不表示“最多256个类别”。

## 3. Prompt与token contract

### 3.1 Raw prompt不等于model prompt

冻结GroundingDINO helper会：

1. `lower()`；
2. `strip()`；
3. 若末尾没有句点则补`.`。

Transformers 4.57.1 processor对candidate-label list执行小写并用“`. `”连接，最后补句点。例如：

```text
["red mug", "metal spoon"]
  -> "red mug. metal spoon."
```

这些不是无关紧要的字符串清洗。句点是phrase boundary的一部分；label顺序、同义词、复合表达、标点和tokenizer都会改变token positions，进而改变query–token score与phrase decode。

### 3.2 256是token-axis上限

冻结model对text tensors截断到`max_text_len=256`。需要保存：

| 字段 | 为什么需要 |
| --- | --- |
| `prompt_raw` | 还原用户/任务真实输入 |
| `prompt_normalized` | 复算实际caption |
| `prompt_hash` | 防止实验之间prompt悄然变化 |
| tokenizer/config revision | 解释subword与special token变化 |
| `input_ids/attention_mask` | 复算phrase token positions |
| truncation flag / original token length | 识别后半labels静默丢失 |

长label list的风险不是“类别超过256”，而是tokenization后超过256 positions；一个多词label会占多个subword tokens。

## 4. Query–token matching

### 4.1 Tensor contract

冻结输出：

| Tensor | Shape | 语义 |
| --- | --- | --- |
| query feature `Z` | `[B,Q,D]` | decoder中每个region query的embedding |
| text feature `E` | `[B,L,D]` | 每个有效text token的embedding |
| score/logit `S` | `[B,Q,L_max]` | 每个query对每个token的匹配logit |
| box `C` | `[B,Q,4]` | normalized `cxcywh` |

`ContrastiveEmbed` 对query $z_q∈R^D$ 与token $e_t∈R^D$ 做点积：

\[
s_{q,t}=z_q^\top e_t.
\]

变量解释：$q$是object query，$t$是文本token，$D$是embedding dimension。直觉是每个region query对每个token分别打分；代码映射是`x @ y.transpose(-1,-2)`。

padding token被mask为`-inf`，随后score tensor padding到`L_max=256`。这防止padding位置被phrase gate选中。

### 4.2 Logit、sigmoid与calibration

官方inference使用：

\[
p_{q,t}=\sigma(s_{q,t})=\frac{1}{1+\exp(-s_{q,t})}.
\]

$p_{q,t}$是同一frozen模型/prompt下的token-wise sigmoid值。它没有因“看起来在0到1之间”就自动成为跨prompt、跨checkpoint或跨类别可比较的calibrated probability。

实现与表述边界：

- 可以说：frozen helper用sigmoid后的最大token score筛query；
- 不能直接说：0.7在所有prompts上都代表70%正确率；
- 若要比较threshold，必须固定model、processor、prompt normalization、image transform和evaluation set。

## 5. 双阈值：region gate与phrase gate

### 5.1 Query / box gate

每个query的region score定义为：

\[
r_q=\max_t p_{q,t}.
\]

保留规则：

\[
\operatorname{keep}(q)=\mathbb{1}[r_q>\tau_{\mathrm{box}}].
\]

$τ_box$控制哪些queries进入结果集。代码使用严格大于号；score等于threshold时会被丢弃。

### 5.2 Phrase-token gate

对已保留query：

\[
M_{q,t}=\mathbb{1}[p_{q,t}>\tau_{\mathrm{text}}].
\]

$M_{q,t}$决定哪些token IDs送入phrase decoder。$τ_text$主要改变phrase组成，不一定改变region数量。

### 5.3 两个阈值不能合并

| 调整 | 直接影响 | 不一定直接影响 |
| --- | --- | --- |
| 提高`τ_box` | 保留query数减少，可能提高precision/降低recall | 已保留query的phrase token集合 |
| 降低`τ_box` | 更多regions进入，可能带来冗余/false positives | phrase是否完整 |
| 提高`τ_text` | phrase更短、可能变空或碎片化 | region是否保留 |
| 降低`τ_text` | phrase可能包含更多修饰词/相邻tokens | region数量 |

一个重要edge case：若`r_q>τ_box`，但所有token都不满足`p_{q,t}>τ_text`，box仍被保留而phrase为空。manifest必须支持`invalid_reason="empty_phrase"`，不能凭最近label强行补值。

## 6. Deterministic threshold lab

人工probability matrix：

| Query | token probabilities | `τ_box=0.35` | `τ_text=0.25` |
| --- | --- | --- | --- |
| `q0` | `[0.90,0.20,0.81,0.01]` | keep | `t0,t2` |
| `q1` | `[0.34,0.33,0.01,0.01]` | drop | 不进入phrase gate |
| `q2` | `[0.60,0.24,0.26,0.01]` | keep | `t0,t2` |

改变一个变量：

1. `τ_text:0.25→0.30`：`q0/q2`仍保留，`q2` phrase由`t0,t2`变成`t0`；
2. `τ_box:0.35→0.65`：只保留`q0`；
3. query max恰为0.35：严格`>`判断为drop。

这只验证逻辑，不代表真实模型分布。面试中不要把synthetic probe说成calibration experiment。

## 7. Phrase reconstruction

### 7.1 从token mask到phrase

冻结路径用`input_ids`和boolean token mask恢复phrase。需要区分：

- token index；
- tokenizer subword；
- decoded span；
- normalized label；
- canonical downstream category。

同一个label可能被拆成多个subwords；一个query也可能对多个相邻/不相邻tokens高分。直接对最终字符串做exact match会丢失这些诊断信息。

### 7.2 标点与复合phrase

句点既是prompt规范化结果，也是candidate label boundary。冻结official helper的`remove_combined`分支会借助`[CLS]/[SEP]/.` token positions把phrase限制到对应区间；默认分支则从所有positive tokens恢复phrase。

因此manifest应同时保存`phrase_token_indices`和`phrase_text`。只保存decoded string无法判断错误来自matching还是decode。

### 7.3 Transformers API drift

Transformers 4.57.1的`GroundingDinoProcessor.post_process_grounded_object_detection`：

1. 从`outputs.input_ids`或显式`input_ids`恢复phrase；
2. `text_labels` argument在frozen code中存在但不参与绑定；
3. result同时返回`text_labels`和`labels`，当前两者都是decoded strings；
4. code包含deprecation/migration warning，未来`labels`可能变成integer IDs。

工程上必须为output key和value type做golden test，不能跨版本只靠字段名。

## 8. Box geometry与NMS boundary

### 8.1 Normalized `cxcywh` 到pixel `xyxy`

对target image width $W$、height $H$：

\[
x_1=W(c_x-w/2),\quad y_1=H(c_y-h/2),
\]

\[
x_2=W(c_x+w/2),\quad y_2=H(c_y+h/2).
\]

变量解释：$(c_x,c_y,w,h)$是normalized center/size；$(x_1,y_1,x_2,y_2)$是pixel corners。代码映射是先乘`[W,H,W,H]`，再`cxcywh→xyxy`。`target_sizes`在Transformers中按`(height,width)`传入。

该公式只恢复到指定target image space。若模型看到的是processed image，还要调用PER-006记录的crop/pad/scale inverse回到raw image。

### 8.2 Frozen helper没有NMS

冻结`inference.py`做threshold、phrase extraction和box conversion，没有NMS call。这意味着：

- 不能把`box_threshold`叫作NMS threshold；
- 不能假设输出已经做class-wise或class-agnostic suppression；
- 也不能反推模型一定产生重复框。

如果部署增加NMS，它是一个新的pipeline stage，必须保存：

| 字段 | 原因 |
| --- | --- |
| pre-NMS indices/boxes/scores/phrases | 复算被删候选 |
| IoU threshold | 控制suppression强度 |
| phrase grouping policy | “red mug”和“mug”是否互相suppression |
| class-agnostic flag | 决定跨phrase竞争 |
| sort/tie-break/max detections | 保证确定性 |
| post-NMS selected indices | 绑定后续region/action |
| coordinate space | 保证IoU在同一空间计算 |

NMS可以缓解重复region，但可能错误删除相邻同类物体；是否需要、如何分组必须由任务和matched evaluation决定。

## 9. Typed grounded-region manifest

推荐把每个region记录为：

| 层 | 必需字段 |
| --- | --- |
| sample/image | `sample_id,image_id,camera_id,frame_id,timestamp` |
| prompt | `prompt_raw,prompt_normalized,prompt_hash,input_ids` |
| revision | `model,checkpoint,processor,tokenizer,code` hashes |
| raw output | `query_index,query_token_logits,pred_box_cxcywh_norm` |
| threshold | `score,score_semantics,box_threshold,text_threshold` |
| phrase | `phrase_token_indices,phrase_text,canonical_label` |
| geometry | processed/raw `xyxy`、transform revision |
| NMS | policy revision、pre/post indices |
| validity | `valid,invalid_reason,ambiguous` |

`score_semantics`必须显式写`max_token_sigmoid`；否则它可能被误解成class softmax、cosine similarity、sequence likelihood或calibrated confidence。

## 10. 可审计伪代码

```python
def ground_one(sample, candidate_labels, cfg):
    # 1) 继承PER-006图像/camera contract，不能丢original->processed变换
    image, image_meta = preprocess_image(sample.image, cfg.image_processor)

    # 2) 保存raw与normalized prompt；句点、顺序和tokenizer都属于合同
    prompt_raw = candidate_labels
    prompt = normalize_candidate_labels(candidate_labels)
    inputs = processor(image=image, text=prompt, return_tensors=True)

    # 3) 保存raw QxL logits与normalized cxcywh，便于重放threshold
    outputs = model(**inputs)
    probs = sigmoid(outputs.pred_logits)
    boxes = outputs.pred_boxes

    pre_nms = []
    for q in range(boxes.shape[1]):
        score = probs[0, q].max()

        # 4) query/box gate使用严格大于号
        if not (score > cfg.box_threshold):
            continue

        # 5) phrase gate独立于query gate；允许empty phrase并标无效原因
        token_idx = where(probs[0, q] > cfg.text_threshold)
        phrase = decode_phrase(inputs.input_ids[0], token_idx)
        invalid_reason = "empty_phrase" if len(token_idx) == 0 else None

        # 6) box先到processed xyxy，再按PER-006 manifest逆变换到raw image
        xyxy_processed = cxcywh_norm_to_xyxy(boxes[0, q], image_meta.processed_size)
        xyxy_raw = inverse_transform(xyxy_processed, image_meta.transform)

        pre_nms.append(make_region_record(
            query_index=q,
            score=score,
            phrase_token_indices=token_idx,
            phrase_text=phrase,
            box_processed=xyxy_processed,
            box_raw=xyxy_raw,
            invalid_reason=invalid_reason,
        ))

    # 7) frozen official helper没有NMS；只有显式配置时才运行并记录selected indices
    regions = apply_nms_with_trace(pre_nms, cfg.nms) if cfg.nms.enabled else pre_nms

    # 8) 输出raw revision/threshold/geometry/NMS manifest，不只返回boxes
    return write_grounding_manifest(sample, inputs, outputs, regions, cfg, image_meta)
```

伪代码的关键不是复刻某个库API，而是保留可重放的raw outputs、两个threshold、phrase tokens、坐标inverse和NMS trace。

## 11. 显式detector与生成式grounding

| 维度 | Grounding DINO式显式detector | Qwen/OPD式生成式grounding |
| --- | --- | --- |
| 核心输出 | `Q×L` logits + `Q×4` boxes | autoregressive text/token sequence |
| region候选 | object queries显式存在 | 坐标作为生成内容出现 |
| phrase绑定 | token score mask + decode | prompt/answer grammar中的tag/text |
| 置信度 | max-token sigmoid等显式score | 通常需token likelihood或另建scorer，不能直接等价 |
| threshold | box/text两个后处理阈值 | generation config、parser、format/geometry gate |
| NMS | frozen helper无；可由下游显式添加 | 通常无region set NMS，除非另建解析后候选集 |
| 主要debug artifact | logits、query/token heatmap、pre/post threshold boxes | generated text、token logprobs、parser trace、tag/coordinate validity |

“open-vocabulary”描述任务能力，不要求所有系统都采用同一种网络。生成式VLM可以完成referring/coordinate输出，但不能借用显式detector的score、threshold和NMS语义。

## 12. 本地OPD项目边界

冻结本地证据链：

```text
annotation/data pool
  -> clip/filter box + normalize to 0..1000
  -> construct tagged <box>/<point>/text SFT rows
  -> expert mix + route metadata
  -> Qwen3-VL causal SFT
  -> model.generate
  -> tag/coordinate parser
  -> IoU / distance / text scorer
```

当前四个直接文件和repo静态搜索支持：

- 有生成式point/box/text数据、训练和评估路径；
- 有prompt、tag、`0..1000`坐标、parser/scorer与route metadata；
- 没有在可搜索源码中发现显式GroundingDINO/NMS调用。

当前不能声称：

- OPD部署了GroundingDINO、region proposal或query–token detector；
- route metadata就是learned detector/router效果；
- 生成式IoU/point/static text指标等于机器人执行成功；
- absence search证明远端/历史/未归档环境绝对没有detector；
- Git metadata或本次审计自动证明候选人个人贡献。

面试安全表达：

> 公源上我能解释并审计Grounding DINO式显式query–token pipeline；本地OPD证据对应生成式tagged-coordinate pipeline。我会把两者按output tensor、threshold、parser和debug artifact分开，不把公开detector机制归到项目，也不从静态grounding跳到机器人成功。

## 13. Failure taxonomy

| 层 | 症状 | 常见根因 | 首个检查 |
| --- | --- | --- | --- |
| prompt | 同义词/顺序变化导致输出漂移 | normalization、label boundary、tokenization | raw/normalized prompt + input IDs |
| truncation | 后半labels完全不响应 | 超过`max_text_len` | original/effective token length |
| matching | region绑定错误token | feature/query/text alignment | query-token heatmap + token mask |
| query gate | 漏检或候选过多 | `τ_box`不匹配分布 | pre-threshold max-score histogram |
| phrase gate | 空phrase/碎片/复合词 | `τ_text`或token boundary | positive token indices + decode |
| geometry | 框整体偏移/拉伸 | target size、cxcywh/xyxy、inverse | processed/raw round-trip |
| duplicate | 相邻/重复regions不稳定 | 无NMS或NMS grouping错误 | pre/post NMS trace |
| API | label key/type突变 | Transformers版本迁移 | golden output schema test |
| project | 把生成式路径说成detector | pipeline类型与证据混淆 | model output contract + local imports |

诊断顺序遵循“先合同、后模型”：prompt/token → raw logits/boxes → two-threshold → phrase decode → geometry → NMS → metric/action。

## 14. Threshold与evaluation设计

PER-007只规定如何保留raw evidence，最终metric协议由PER-010展开。最小matched sweep应：

1. 固定model/checkpoint、processor、prompt、image transform、split与seed；
2. 缓存raw logits/boxes/input IDs，不为每个threshold重跑模型；
3. 对`τ_box`与`τ_text`做二维grid，但分开观察region count和phrase integrity；
4. NMS off/on作为独立factor，固定IoU/grouping policy；
5. 保存per-sample prediction，而不是只报aggregate；
6. 明确空phrase、no-object、ambiguous和invalid boxes的分母处理；
7. 不从offline detector结果推断controller/robot success。

若同时改变prompt wording、threshold与NMS，不能把结果变化归因给其中一个因素。

## 15. 实现与面试检查表

回答PER-007至少覆盖：

1. 画image/text→features→queries→`Q×L` logits+boxes→双阈值→phrase/geometry/NMS；
2. 说明`L_max=256`是token positions，不是classes；
3. 写出query–token dot product和sigmoid；
4. 分开`τ_box`与`τ_text`；
5. 说明frozen helper无NMS，但不保证无重复框；
6. 保存raw logits、input IDs、query index、phrase tokens、processed/raw boxes与revision；
7. 解释Transformers`labels/text_labels`版本风险；
8. 对比显式detector与OPD生成式grounding；
9. 明确offline grounding不等于action/robot success。

常见危险答案：

- “每个query只对应一个class”；
- “256就是最多256类”；
- “box threshold就是NMS threshold”；
- “text threshold只影响置信度，不影响phrase”；
- “HF的text_labels参数直接决定输出label”；
- “Grounding DINO官方默认已经做NMS”；
- “OPD有box输出，所以项目用了Grounding DINO”。

## 16. 结论与下一步

PER-007的核心是把open-vocabulary grounding从一句“文本找框”展开为可复算pipeline：prompt/token、query–token logits、query gate、phrase gate、geometry、optional NMS和typed manifest必须逐层显式。当前source/knowledge/card已闭合且题卡保持`unseen`；本地detector checkpoint/raw logits/threshold calibration/NMS trace和closed-loop evidence仍缺，因此保持`WARN`。

`VLA-PER-008..009` source/knowledge/card已同步且保持`unseen`。下一bounded slice只做PER-010 metric/parser source freeze，不生成knowledge/card，不创建`coaching_state.md`。

## References

1. [PER-007 Open-vocabulary Grounding Pipeline Source Freeze](../sources/vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)。
2. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
3. [IDEA-Research/GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)。
4. [Transformers 4.57.1 Grounding DINO](https://github.com/huggingface/transformers/tree/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino)。
5. [PER-006 Image Preprocess / Token / Camera](vol_06_per006_image_preprocess_token_camera_contract.html)。
6. [PER-001 Point / Box / Text Grounding](vol_06_per001_grounding_coordinate.html)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
