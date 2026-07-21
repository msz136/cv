# VOL 06 Perception / Grounding / Navigation：Grounding Matching、Negative 与 Loss Reduction（PER-009）

> 状态：`drafted / VLA-PER-009 / source_synced / card_synced / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[PER-009 Source Freeze](../sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.html)。  
> 前置知识：[PER-001 Point / Box / Text Contract](vol_06_per001_grounding_coordinate.html)、[PER-006 Image / Token / Camera](vol_06_per006_image_preprocess_token_camera_contract.html)、[PER-007 Open-vocabulary Grounding](vol_06_per007_open_vocabulary_grounding_pipeline.html)、[PER-008 Representation Choice](vol_06_per008_representation_choice.html)。  
> 原子题卡：[VLA-PER-009](../questions/vol_06_per009.html)（`unseen`）。

## 问题（Question）

Grounding detector训练时，Hungarian matching到底匹配什么？matching cost和最终training loss有什么区别？未匹配query、非目标token、padding、negative image与hard negative分别如何进入目标？focal、L1、GIoU、auxiliary loss又如何reduction？最后，本地OPD的assistant-token CE、routed top-1 CE和online teacher-KL能不能讲成Grounding DINO式detector loss？

本页用一条可审计链回答：

```text
prediction/target schema + positive token map
  -> pairwise cost matrix
  -> Hungarian one-to-one assignment
  -> matched/unmatched token targets
  -> classification + localization components
  -> token/object/sample/batch/worker reduction
  -> auxiliary/encoder branches + diagnostics
  -> project-specific objective and evidence boundary
```

## 知识地图位置与边界

```text
PER-001 schema / coordinate / parser
  -> PER-006 image-token-camera-time lineage
  -> PER-007 open-vocabulary inference dataflow
  -> PER-008 output representation choice
  -> PER-009 training matching / negative / loss / reduction
  -> PER-010 metric / parser / protocol comparability
  -> PER-011 pseudo-label / teacher noise
  -> PER-015 perception-to-action gate
```

PER-009只负责训练目标。它不把loss下降解释成IoU/PCK/Recall提升，不评价teacher是否可靠，也不从offline objective推出controller或robot success。VOL 01已讲CE、KL、focal等通用数学；本页新增grounding tensor、assignment、mask、distributed denominator和本地代码映射。

## 1. 30秒直觉：先分配责任，再计算梯度

最短可用回答是：

> Set-prediction detector先构造每个query和每个GT之间的class/token、L1与GIoU cost，再用Hungarian算法做一对一assignment；这个cost只决定“谁负责谁”，不是最终反向传播的loss。assignment之后，matched query有token与box监督，unmatched query通常仍作为classification negative，但没有box target。padding必须被mask掉，不能当negative。最终loss的组件、权重和reduction必须按paper revision与runtime config冻结。本地OPD所读代码是生成式CE/KL lineage，没有query set、Hungarian或L1/GIoU head，所以不能口述成detector criterion。

面试中最容易失分的四个混淆：

1. 把Hungarian cost当作可直接求梯度的total loss；
2. 把padding、unmatched query、wrong token与negative image都叫“负样本”；
3. 只背`1/5/2`或`2/5/2`，却不说matching/final与版本位置；
4. 看见本地有grounding数据与loss曲线，就声称训练了Grounding DINO或grounding质量提升。

## 2. Detector训练数据流与Tensor合同

### 2.1 最小schema

以冻结的Transformers 4.57.1 Grounding DINO bridge为例：

| 对象 | Shape / 语义 | 必须冻结的约束 |
| --- | --- | --- |
| `logits` | `[B,Q,L]`，query×text-token logits | `L`是当前prompt token positions，不是固定class数 |
| `pred_boxes` | `[B,Q,4]`，normalized `cxcywh` | GIoU前转换为corner format |
| `labels[b].class_labels` | `[M_b]` | 索引当前sample的label/phrase map |
| `labels[b].boxes` | `[M_b,4]`，normalized `cxcywh` | sample间GT数量可变 |
| `label_maps[b]` | `[C_b,L]` | class/phrase映射到一个或多个token positions |
| `text_mask` | `[B,Q,L]` bool | 只让有效attention positions进入classification loss |
| `indices[b]` | `(query_idx,target_idx)` | Hungarian一对一assignment |
| `num_boxes` | scalar | 跨worker平均GT数并至少为1 |

### 2.2 Positive token map为什么重要

Open-vocabulary grounding不一定把类别轴做成固定的`C`个object classes，而是让query与text tokens对齐。一个phrase可能覆盖多个subword token，因此target需要`phrase/class -> token positions`的映射。

冻结的first-party GroundingDINO代码从character spans构造固定宽度positive map，并在phrase内部做token归一化；Transformers 4.57.1则按delimiter与special-token group构造label map。两条map construction没有golden test时不能当成bitwise或语义完全等价。

## 3. Matching Cost与Final Training Loss必须分开

### 3.1 Pairwise cost与Hungarian assignment

令query (i)与GT (j)的pairwise cost为：

\[
C_{ij}=\lambda_{\mathrm{cls}}C^{\mathrm{token}}_{ij}
+\lambda_1\lVert \hat b_i-b_j\rVert_1
+\lambda_G\bigl(-\operatorname{GIoU}(\hat b_i,b_j)\bigr),
\qquad
\hat\sigma=\arg\min_{\sigma}\sum_j C_{\sigma(j),j}.
\]

变量解释：\(\hat b_i\)和\(b_j\)是predicted/target normalized boxes；\(C^{\mathrm{token}}_{ij}\)是query对目标phrase tokens聚合后的classification cost；\(\lambda_{\mathrm{cls}},\lambda_1,\lambda_G\)是matching阶段权重；\(\hat\sigma\)是离散的一对一assignment。直觉上，先比较所有“query负责GT”的候选代价，再选全局最小组合。实现映射：Transformers bridge计算focal-style token cost、`torch.cdist(..., p=1)`和negative GIoU，再调用SciPy `linear_sum_assignment`。证据边界：该式概括version-pinned paper/implementation bridge，不证明本地OPD存在matcher。

一个2×2 probe足以说明“全局”而非逐行贪心：对`[[0.2,1.3],[1.2,0.1]]`，assignment是`q0→t0,q1→t1`，总cost为`0.3`；交换后为`2.5`。这个probe只验证assignment逻辑，不验证任何模型预测正确。

### 3.2 为什么cost不是loss

| 比较项 | Matching cost | Final training loss |
| --- | --- | --- |
| 作用 | 选择离散assignment | 对选定targets形成梯度 |
| 输入 | 所有query×GT pair | matched pairs + classification negatives |
| 权重 | matcher coefficients | criterion coefficients |
| 形式 | 可为排序友好的近似cost | 按实现定义的可微loss |
| 输出 | integer index pairs | scalar与per-component loss dict |

即便两边都写class/L1/GIoU，它们也可以有不同系数和具体公式。auxiliary decoder层在冻结bridge里还会重新matching，不能默认所有层复用final layer的assignment。

## 4. Negative Taxonomy：至少拆成五类

### 4.1 Query-token target matrix

冻结bridge先建立全零`target_classes_onehot`，再只在matched query位置写入目标phrase的token map：

```text
matched query + target phrase tokens -> positive target 1
matched query + other valid tokens  -> negative target 0
unmatched query + all valid tokens  -> negative target 0
padding/out-of-attention positions  -> masked out; no loss
```

因此该实现中的background并不是DETR categorical classifier末尾一个独立`no-object`类，而是“对所有有效text tokens均为0”的binary target。

### 4.2 五类概念不能合并

| 类型 | 在冻结实现中的语义 | 是否进入loss | 不应偷换成 |
| --- | --- | --- | --- |
| matched positive token | query对应GT phrase token | 正focal target | 整个phrase只有一个固定class ID |
| matched query的其他有效token | wrong/non-target token | 负focal target | dataset negative image |
| unmatched query | 所有有效token target为0 | classification negative；无box target | padding或显式no-object class |
| padding/special masked position | 无有效监督语义 | 由`text_mask`或`-100`排除 | easy negative |
| dataset/hard negative | 负图、wrong prompt、挖掘样本等recipe | 取决于数据构造 | focal loss自动提供的能力 |

focal loss可以降低easy-negative dominance，但不会自动构造negative image、选择hard negatives或修正错误标签。负样本的“来源”与loss的“加权方式”是两个不同设计层。

## 5. Focal Loss：处理不平衡，不负责采样

对binary target，令\(p_t\)为正确标签的模型概率：

\[
\operatorname{FL}(p_t)
=-\alpha_t(1-p_t)^\gamma\log p_t.
\]

变量解释：\(\alpha_t\)平衡positive/negative类别；\(\gamma\)控制well-classified example的down-weighting；冻结的GroundingDINO/HF相关路径使用`alpha=0.25`、`gamma=2`。直觉上，\(p_t\to1\)时，modulating factor \((1-p_t)^\gamma\)快速变小。实现映射：先做`binary_cross_entropy_with_logits(reduction="none")`，再乘modulating factor与alpha，最后按冻结reduction聚合。证据边界：该式不证明概率校准、negative coverage或最佳超参数。

确定性probe中，对negative target取\(\alpha_t=0.75,\gamma=2\)：\(p_t=0.99\)时loss约`7.54e-7`，\(p_t=0.5\)时约`0.129965`，hard/easy约`1.72e5`倍。这只说明easy negative被强烈降权，不说明hard-negative mining已经发生。

## 6. L1与GIoU：只监督Matched Box Pairs

assignment之后，box supervision可写为：

\[
\mathcal L_{\mathrm{box}}
=\frac{1}{N_{\mathrm{gt}}}
\sum_{(i,j)\in\hat\sigma}
\left[
\lambda_1\lVert\hat b_i-b_j\rVert_1
+\lambda_G\bigl(1-\operatorname{GIoU}(\hat b_i,b_j)\bigr)
\right].
\]

变量解释：\(\hat\sigma\)是matching pairs；\(N_{\mathrm{gt}}\)是跨worker平均后且至少为1的GT box数；L1作用在normalized `cxcywh`，GIoU前转corner format。直觉上，L1直接约束坐标，GIoU补充overlap与relative geometry，特别是在boxes不重叠时仍能提供区分。实现映射：冻结HF base loss分别做elementwise L1求和和`1-diag(generalized_box_iou)`求和，再除`num_boxes`。证据边界：training GIoU loss不是PER-010的evaluation IoU protocol。

unmatched query没有box target，因此不会进入L1/GIoU；但它仍可在classification tensor里产生负监督。这正是“no box loss”不等于“no gradient”。

## 7. Reduction顺序属于Objective合同

### 7.1 Detector classification与box denominator

冻结HF GroundingDINO classification bridge对`text_mask`后的valid query-token loss求sum，再除`num_boxes`。因此：

- unmatched-query negatives进入numerator；
- padding不进入numerator；
- denominator是GT box count，不是valid token数、query数或batch size；
- prompt长度或query数改变时，negative数量及loss scale可能改变。

base criterion先统计local GT count；distributed/Accelerate初始化时跨rank reduce，再除world size并`clamp(min=1)`。它近似“每worker平均GT数”，不是global token mean。复现时必须保存world size、per-rank targets、gradient accumulation与empty-target batch行为。

### 7.2 Weighted total、auxiliary与encoder分支

Transformers 4.57.1的version-specific总loss可概括为：

\[
\mathcal L
=2\mathcal L_{\mathrm{ce}}
+\lambda_{\mathrm{bbox}}\mathcal L_1
+\lambda_{\mathrm{giou}}\mathcal L_{\mathrm{giou}}
+\sum_{l\in\mathrm{aux}}\mathcal L^{(l)}
+\mathcal L_{\mathrm{enc}}.
\]

变量解释：\(\mathcal L^{(l)}\)是intermediate decoder层的loss；\(\mathcal L_{\mathrm{enc}}\)只在two-stage路径出现；该bridge默认`bbox_loss_coefficient=5`、`giou_loss_coefficient=2`，final classification coefficient为2。直觉上，auxiliary深监督让中间层直接收到matching/class/box梯度。实现映射：`auxiliary_loss`、`two_stage`与weight dictionary由该版本config/loss bridge控制。证据边界：这些值不是所有checkpoint或其他版本的runtime truth。

`cardinality_error`可以出现在loss dictionary中用于logging，但冻结Grounding DINO weight dictionary并未给它优化权重。看到loss dict中的key，必须继续检查它是否乘权后进入total loss。

## 8. Grounding DINO权重冲突：版本门比背数字重要

Grounding DINO v5正文与附录Table 8在classification matching/final权重上相反：

| 来源位置 | Matching class/L1/GIoU | Final class/L1/GIoU |
| --- | --- | --- |
| v5正文3.5与实验段叙述 | `2 / 5 / 2` | `1 / 5 / 2` |
| v5附录Table 8 | `1 / 5 / 2` | `2 / 5 / 2` |
| Transformers 4.57.1 bridge | `1 / 5 / 2` | `2 / 5 / 2` |

安全口径是：论文确认token focal classification、L1/GIoU、bipartite matching及auxiliary structure；具体系数必须绑定paper位置、implementation revision、resolved config和runtime weight dictionary。冻结的first-party GroundingDINO commit没有公开完整matcher/criterion主体，不能靠该repo消除冲突。

面试官若追问“到底哪个对”，可以回答：

> 对我冻结的HF 4.57.1实现，matching是`1/5/2`、final是`2/5/2`，与paper Table 8一致；但paper正文给了相反的classification系数。因此我不会把任一组说成跨版本唯一官方值，会查看实际config和loss code。

## 9. 本地OPD三条Objective Lineage

### 9.1 Assistant-token SFT

`point_sft.py`分别tokenize full conversation和prompt-only conversation，用`prompt_len`把`labels[:prompt_len]`设为`-100`，collator也用`-100`补齐labels。直接证据只支持：prompt/padding不进入model loss，assistant response tokens被监督。

它把实际CE交给loaded model与Transformers `Trainer`，所以wrapper本身没有冻结具体model class内部shift/reduction。`SafeTrainer`还会在encode/filter失败、non-finite loss或training exception时产生zero-loss fallback step并写bad-batch log。aggregate loss必须与zero-loss/dummy/retry事件账本一起看。

### 9.2 Routed object/region top-1 CE

`train_opd_top1_vl.py`只在原assistant supervised positions写object/region teacher top-1 token ID，其余位置为`-100`。sample-level objective为：

\[
L_b=w_{b,o}\operatorname{mean}_{t\in T_b}\operatorname{CE}(z_{b,t},y^o_{b,t})
+w_{b,r}\operatorname{mean}_{t\in T_b}\operatorname{CE}(z_{b,t},y^r_{b,t}),
\qquad
L=\operatorname{mean}_b L_b.
\]

变量解释：\(T_b\)是sample \(b\)未被`-100`屏蔽的response positions；\(w_{b,o},w_{b,r}\)由object/region/both route决定，`both`为`.5/.5`；\(z\)是student logits，\(y^o,y^r\)是teacher top-1 token IDs。直觉上，每个样本先对自己的有效tokens求mean，再按route混合，最后样本等权。实现映射：代码以`F.cross_entropy(..., reduction="mean")`得到sample CE，再做`sample_loss.mean()`。证据边界：这不是full-distribution distillation，也没有detector query/box matching。

确定性reduction probe：一个`both`样本的object/region token-mean CE为`2/4`，sample loss为`3`；另一个object样本loss为`8`，batch mean为`5.5`。把所有tokens拼接后直接global mean通常不会得到`5.5`。

### 9.3 Online full-vocabulary teacher KL

`train_opd_online_vl.py`由student或teacher生成response，再在同一generated sequence上计算teacher/student full-vocabulary logits：

\[
q_{b,t}=\operatorname{softmax}\!\left(z^T_{b,t}+\beta\operatorname{stopgrad}(z^S_{b,t})\right),
\qquad
L_b=\frac{1}{|T_b|}\sum_{t\in T_b}\operatorname{KL}(q_{b,t}\Vert p^S_{b,t}),
\qquad
L=\operatorname{mean}_b(w_bL_b).
\]

变量解释：\(z^T,z^S\)是teacher/student logits；\(\beta\)是veto schedule coefficient，0时target退化为teacher distribution；\(p^S\)是student softmax；\(T_b\)是full response或prefix positions；\(w_b\)是route weight。直觉上，它让student拟合整个vocabulary distribution，而非只拟合teacher argmax token。实现映射：代码先逐token KL，再以`token_mask.sum(...).clamp_min(1)`做sample mean，最后`(sample_loss*weights).mean()`。证据边界：KL下降不证明teacher正确、parser改善或robot成功；teacher noise属于PER-011。

online路径还要求microbatch内route一致；ZeRO-3预载teacher时，各rank也必须走一致route，否则teacher调用和collective sequence可能失配。

## 10. 为什么三条本地Loss都不是Hungarian Detector Loss

| 能力/字段 | 显式Grounding detector | 本地SFT | 本地top-1 CE | 本地online KL |
| --- | --- | --- | --- | --- |
| query set `[B,Q,*]` | 有 | 无直接证据 | 无 | 无 |
| Hungarian assignment | 有 | 无 | 无 | 无 |
| unmatched-query negative | 有 | 无 | 无 | 无 |
| box L1/GIoU head | 有 | 无 | 无 | 无 |
| response token mask | 非主要接口 | `-100` | `-100` | prefix/full mask |
| teacher target | 非必要 | gold assistant token | teacher top-1 token | full-vocab distribution |
| reduction unit | query-token/GT boxes | model内部未完全冻结 | token→sample→route→batch | token→sample→route→batch |

“grounding数据 + 生成式token loss”可以训练模型输出point/box/text，但不能因此把其architecture/objective重命名为set-prediction detector。面试中先说objective family，再说target、mask与reduction，能够避免术语漂移。

## 11. 2500行Metrics应该怎样解释

冻结CSV共2500行，从raw rows重算后与summary JSON一致：

| Window | loss | opd_loss | top-k overlap | grad_norm | opd_loss_tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| first 100 mean | 0.107026 | 0.091948 | 0.610231 | 8.164954 | 35.02 |
| last 100 mean | 0.029667 | 0.029326 | 0.828569 | 1.841578 | 33.29 |
| last row / step 2500 | 0.0288 | 0.020672 | 0.806510 | 0.671648 | 24.0 |

这支持“归档optimization/logging trace内部存在下降趋势，summary算术可复算”。它不支持：

- 某一设计是唯一原因；
- checkpoint已经不可变绑定到这些rows；
- same-protocol holdout parser或grounding metric提升；
- teacher target更正确；
- robot rollout或closed-loop success提升。

更可信的证据链应为`step -> resolved config/command -> immutable checkpoint -> raw holdout prediction -> parser/metric protocol -> robot episode`。缺任一层时，只在已闭合层陈述结论。

## 12. Typed Loss Manifest

只记录一个scalar `loss`无法复现objective。建议最小记录：

```json
{
  "sample_ids": [],
  "model_checkpoint_revision": "...",
  "code_config_processor_revision": "...",
  "objective_family": "hungarian_detector | assistant_ce | routed_top1_ce | online_teacher_kl",
  "prediction_schema": {},
  "target_schema": {},
  "positive_map_revision": "...",
  "matching_costs": {},
  "loss_coefficients": {},
  "negative_semantics": {},
  "masks": {"text": null, "prompt": null, "padding": null, "token": null},
  "reduction_order": ["element", "token_or_object", "sample", "batch", "worker"],
  "num_targets_per_rank": [],
  "auxiliary_encoder_branches": {},
  "zero_loss_dummy_retry_counts": {},
  "raw_loss_dict": {},
  "valid": true,
  "invalid_reason": null
}
```

这个manifest把“什么被监督、哪些位置被mask、怎么归一化、哪些分支计权、是否有fallback”从口头假设变成运行证据。对于本地OPD，还应保存route、response/prefix长度和teacher/student checkpoint；对于detector，还要保存positive map与per-rank GT counts。

## 13. 可审计训练Step伪代码

```python
def detector_training_step(batch, model, matcher, criterion):
    # 1. Freeze prediction/target schema and valid text positions.
    outputs = model(batch["images"], batch["text_tokens"])
    targets = build_box_and_token_targets(batch)
    text_mask = batch["text_mask"]

    # 2. Build pairwise class/L1/GIoU costs only for assignment.
    cost = matcher.pairwise_cost(outputs, targets, text_mask)
    indices = matcher.hungarian(cost)

    # 3. Compute final differentiable losses after assignment.
    loss_dict = criterion(outputs, targets, indices, text_mask)

    # 4. Apply runtime weight_dict; logging-only keys get no gradient weight.
    total = sum(loss_dict[k] * criterion.weight_dict[k]
                for k in loss_dict if k in criterion.weight_dict)

    # 5. Persist denominators, masks, assignments and fallback events.
    save_loss_manifest(batch, outputs, targets, indices, loss_dict, total)
    return total
```

这段是工程伪代码，不是某个repository的可直接调用API。关键检查点是matching与criterion分层、`weight_dict`决定哪些key进入total、manifest保存真实denominator与mask。

## 14. Failure Taxonomy与诊断顺序

| 失败层 | 症状 | 常见根因 | 首个检查 |
| --- | --- | --- | --- |
| target/map | phrase对错token，特殊字符下异常 | char span/tokenizer/map revision错 | raw tokens + positive map golden case |
| matching | assignment频繁跳、duplicate责任 | cost尺度/格式/系数错 | component cost matrix + box format |
| negative | loss被大量easy negatives主导 | Q/L变化、mask漏、target全零异常 | positive/negative/masked counts |
| box | GIoU/L1异常或NaN | `cxcywh/xyxy`、归一化、degenerate box | pre/post conversion tensors |
| reduction | world size或batch变化时scale漂移 | denominator/reduction顺序错 | numerator + per-rank num_boxes |
| auxiliary | total loss多出或少掉层 | weight dict/two-stage flag不一致 | raw loss dict + resolved config |
| local SFT | loss虚低、有效token骤降 | `-100` mask或zero-loss fallback | valid-token与fallback ledger |
| local route | object/region loss不可比 | route混批、sample/global mean混淆 | per-sample route + token counts |
| evidence | loss下降却metric不升 | checkpoint/parser/protocol未绑定 | immutable eval bundle |

推荐顺序：schema与token map → raw target/mask counts → cost components → assignment probe → box format → numerator/denominator → auxiliary weight dict → zero-loss/route events → immutable checkpoint → PER-010 holdout protocol。先查合同，通常比先调learning rate更有解释力。

## 15. 面试回答模板、追问与危险答案

### 15.1 两分钟结构化回答

1. 用一句话分开matching cost与final loss；
2. 报出`[B,Q,L]` token-axis logits、`[B,Q,4]` boxes和positive map；
3. 解释matched/unmatched/non-target/padding/dataset negative；
4. 说明focal、L1/GIoU及GT-box distributed normalization；
5. 主动指出paper正文/Table 8权重冲突与runtime config门；
6. 落到本地OPD三条CE/KL lineage，不夸成Hungarian detector；
7. 最后说loss曲线只证明optimization trace，metric/robot证据仍需绑定。

### 15.2 高频追问

| 追问 | 回答抓手 |
| --- | --- |
| Hungarian matching可反向传播吗？ | assignment是离散责任分配；梯度来自assignment后的可微loss |
| unmatched query完全没loss吗？ | 无box target，但通常仍有全零token classification target |
| padding算negative吗？ | 不算；由`text_mask`或`labels=-100`排除 |
| focal loss等于hard-negative mining吗？ | 不等于；一个是loss reweighting，一个是数据/样本选择 |
| 为什么除GT boxes而不是tokens？ | 这是冻结criterion的scale合同；必须和valid-token numerator一起理解 |
| aux层复用final matching吗？ | 冻结HF bridge会对每个aux output重新matching |
| `cardinality_error`是否优化？ | 该bridge只logging，未进weight dict |
| Grounding DINO权重是多少？ | 先问matching还是final、paper位置与版本；HF 4.57.1与Table 8一致 |
| OPD top-1和online KL差别？ | argmax token CE vs full-vocabulary distribution KL，mask/reduction也需分别冻结 |
| loss下降能证明grounding提升吗？ | 不能；要绑定checkpoint、raw prediction和同protocol metric |

### 15.3 危险答案

- “Hungarian cost就是训练总loss”；
- “未匹配query和padding都是negative”；
- “用了focal loss就做了hard-negative mining”；
- “所有loss都按batch mean”；
- “loss dict里出现的项都会反向传播”；
- “Grounding DINO官方权重固定就是某一组数字”；
- “OPD用了point/box数据，所以loss就是Grounding DINO loss”；
- “2500步loss下降证明holdout和机器人效果提升”。

## 16. Project Truth Boundary与补证顺序

| 项目口径 | 当前可安全表述 | 当前不能声称 |
| --- | --- | --- |
| Public detector | 能解释Grounding DINO paper与HF 4.57.1 matching/focal/L1/GIoU/reduction | 本地部署或复现了Grounding DINO training |
| OPD SFT | prompt/padding以`-100` mask，assistant tokens被监督 | wrapper证明了exact model-internal CE reduction |
| OPD top-1 | object/region teacher top-1 CE、route weights、sample→batch reduction | Hungarian、box head或full-distribution KL |
| OPD online | generated-response full-vocab KL、prefix mask、route/rank invariants | teacher可靠、holdout/robot uplift |
| Metrics | 2500 rows与summary算术一致，optimization trace可复算 | checkpoint/eval绑定、因果改进或candidate ownership |

补证优先级：

1. exact command、resolved config、model class与immutable checkpoint；
2. batch target/mask/route manifest与raw per-component loss；
3. numerator、denominator、world size及zero-loss/dummy/retry ledger；
4. per-step或interval checkpoint到metrics的绑定；
5. same-protocol holdout raw predictions、strict parser与PER-010 metrics；
6. matched ablation和error taxonomy；
7. 最后才连接controller/robot result与candidate ownership。

## 17. 结论与下一步

PER-009的核心是把“责任分配”和“梯度目标”分开：Hungarian matcher在query×GT pairwise cost上选一对一assignment；final criterion再对matched token/box和unmatched token negatives计算focal、L1、GIoU及auxiliary/encoder loss。padding通过mask排除，dataset/hard negative需要单独recipe，reduction顺序与distributed denominator必须视为objective的一部分。

本地OPD的直接证据支持assistant-token SFT、routed teacher top-1 CE和generated-response full-vocabulary KL三条lineage，但没有显式query set、Hungarian matcher、unmatched-query negatives或L1/GIoU head。2500行metrics只闭合optimization trace算术，未闭合checkpoint→holdout→robot因果链。因此本节点保持`WARN`。

当前PER-009 source、knowledge与atomic card已同步；全局260张题卡仍全部`unseen`。下一bounded slice只做`VLA-PER-010` metric/parser source freeze；不生成knowledge/card，不创建`coaching_state.md`，不改变任何mastery。

## References

1. [PER-009 Grounding Matching / Negative / Loss Source Freeze](../sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.html)。
2. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
3. [DETR v3](https://arxiv.org/abs/2005.12872v3)。
4. [Focal Loss v2](https://arxiv.org/abs/1708.02002v2)。
5. [Generalized IoU v2](https://arxiv.org/abs/1902.09630v2)。
6. [IDEA-Research/GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)。
7. [Transformers 4.57.1 Grounding DINO loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_grounding_dino.py) 与 [object-detection loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_for_object_detection.py)。
8. [PER-007 Open-vocabulary Grounding](vol_06_per007_open_vocabulary_grounding_pipeline.html) 与 [PER-008 Representation Choice](vol_06_per008_representation_choice.html)。
9. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
