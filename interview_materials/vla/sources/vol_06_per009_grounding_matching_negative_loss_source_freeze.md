# VOL 06 PER-009 Source Freeze：Grounding Matching、Negative 与 Loss Reduction

> 状态：`source_frozen / VLA-PER-009 / primary_official_checked / local_ce_top1_kl_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结显式grounding detector与本地OPD生成式训练的objective、matching、negative和reduction合同；不生成knowledge/card，不展开PER-010 metric/parser、PER-011 pseudo-label/noise或PER-015 controller gate。

## 问题（Question）

Grounding模型训练时，Hungarian matching究竟匹配什么？matching cost和最终training loss为什么不能混用？未匹配query、非目标token、padding、负图像和hard negative分别是什么？focal、L1、GIoU、auxiliary loss如何reduction？本地OPD的assistant-token CE、routed top-1 CE与teacher-KL能否口述成Grounding DINO式detector loss？

本页冻结的可审计链为：

```text
prediction/target schema + positive token map
  -> pairwise matching cost matrix
  -> one-to-one assignment
  -> matched positive + unmatched/token negative targets
  -> classification/localization loss components
  -> token/object/sample/batch/distributed reduction
  -> auxiliary/encoder branches and logged diagnostics
  -> project-specific objective boundary
```

## 1. 结论先行

1. **matching cost不是training loss**：Hungarian阶段只决定query与GT的离散一对一assignment；最终梯度来自assignment后的classification、L1、GIoU及可选auxiliary/encoder losses。两阶段即使使用同名组件，也可能有不同权重与计算形式。
2. **Grounding DINO的类别轴是text-token轴**：冻结的Transformers 4.57.1实现将class label映射为token positions；matching class cost聚合目标phrase的token focal-style cost，最终classification对有效text positions做binary focal loss。
3. **negative至少分四层**：未匹配query的全零token target、匹配query中的非目标token、dataset级negative image/prompt、以及挖掘或采样出的hard negative不是同一概念。当前source只直接冻结前两类；dataset/hard-negative recipe仍未验证。
4. **padding不是negative**：Transformers实现用`text_mask`排除padding；本地生成式路径用`labels=-100`排除prompt/padding。把masked位置当negative会改变分母与梯度。
5. **reduction顺序是objective的一部分**：GroundingDINO focal/L1/GIoU按跨worker平均GT box数归一化；本地top-1先对每个样本的有效token求mean，再route加权，再对batch求mean；online KL也先token mean、再sample weight、再batch mean。交换顺序并不等价。
6. **focal loss处理easy-negative dominance，不自动完成negative mining**：它以`alpha`平衡正负，以`gamma`下调well-classified examples；它不能替代dataset-level negative coverage、label correctness或calibration。
7. **版本权重不能靠记忆**：Grounding DINO v5正文叙述与附录Table 8在classification matching/final loss权重上不一致；Transformers 4.57.1默认值与Table 8一致。因此必须保存paper revision、config与runtime loss dictionary，不能口述一个无revision的“官方权重”。
8. **本地OPD不是显式detector criterion**：`point_sft.py`是assistant-token supervision；`train_opd_top1_vl.py`是object/region teacher top-1 token CE；`train_opd_online_vl.py`是full-vocabulary teacher distribution KL。所读路径没有query set、Hungarian matcher、unmatched-query negatives、L1/GIoU head或detector auxiliary loss。
9. **loss下降不等于grounding或robot成功**：2500行本地metrics可复算first/last窗口的optimization信号，但没有在本切片绑定同protocol holdout、checkpoint、parser输出或robot episode，不能据此推出quality uplift。

## 2. Primary / official / local source ledger

论文SHA对version-pinned PDF bytes计算；GitHub/Hugging Face文本按UTF-8与LF规范化；本地文件与CSV使用原始bytes。repository license只约束相应source code，不能自动覆盖paper、checkpoint、dataset或第三方asset。

| 来源 | 类型 / revision / license | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [Grounding DINO paper v5](https://arxiv.org/abs/2303.05499v5) | primary；2024-04-15 v5；PDF读取2026-07-20 | `BA1C64EC2AC4FEDEB50B269EADC994456A8428DBE64A8DBA2673F22DF0FA20B3` | token focal classification、L1/GIoU、bipartite matching、decoder/encoder auxiliary loss与paper权重描述 | 冻结repo公开了完整criterion、HF/本地实现与论文完全相同 |
| [DETR paper v3](https://arxiv.org/abs/2005.12872v3) | primary；2020-05-28 v3 | `D4B846BD44896E1D21527F48EDDC422C263C9A4F8A3FA4BE249750956882698D` | set prediction、Hungarian assignment、unmatched=no-object与box/class loss分层 | Grounding DINO token-axis实现细节或本地OPD loss |
| [Focal Loss paper v2](https://arxiv.org/abs/1708.02002v2) | primary；2018-02-07 v2 | `2E6F45B97007009F32B82A3C19F35638D8DA7022D8D4E4416B9078DE91339F71` | alpha-balanced focal loss、easy-negative down-weighting与gamma作用 | 任意grounding模型的negative sampling、calibration或最佳alpha/gamma |
| [GIoU paper v2](https://arxiv.org/abs/1902.09630v2) | primary；2019-04-05 v2 | `56FCEEDBBE952FD132EB75A6E6BC637028C365FA5A8C6B584E4020DDF01F291E` | IoU非重叠plateau、GIoU定义与box regression loss动机 | Grounding DINO的完整总loss、metric comparability或robot结果 |
| [GroundingDINO utils.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/models/GroundingDINO/utils.py) | official-code；`856dde20...`；Apache-2.0 | `2827BA921ACAA263DB7533AFB6A818473A957FB2EF559C4F3407DA72028A0842` | sigmoid focal实现、`alpha=.25/gamma=2`与`mean(1).sum()/num_boxes` | 该commit存在完整matcher/criterion调用链 |
| [GroundingDINO vl_utils.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/util/vl_utils.py) | official-code；同一commit | `19ECD4BEADCD2E9A1900E6F6B884040E1000A7783AC235D9E3138D0FAC874150` | char span→token positive map与phrase内token归一化 | unmatched query、box loss或dataset negative policy |
| [GroundingDINO model](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/models/GroundingDINO/groundingdino.py) | official-code；同一commit | `CDFB48D5B15D6B98F3D2002F59AE4730740A1ECFBAEBA324F6840C5E4666A5B8` | query-token logits与box head的model-side接口 | repo当前公开完整training criterion或local deployment |
| [GroundingDINO LICENSE](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/LICENSE) | official-code；Apache-2.0 text | `B403C98EC1FFACCB0124632592A3D99642CDDC3031CA412B402568E6C06C202A` | repository source license线索 | checkpoint/dataset/第三方asset授权自动相同 |
| [Transformers Grounding DINO modeling](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino/modeling_grounding_dino.py) | implementation bridge；v4.57.1 / `8cb5963...`；Apache-2.0 | `BA98EB52ACBD8A7E36BAB581FD0F9B092FED3579E37CD6E69C55EA153504B2E0` | label map/text mask构造、loss_function输入、aux/encoder tensors | first-party training recipe或本地实际class/config |
| [Transformers Grounding DINO loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_grounding_dino.py) | implementation bridge；同一release | `11F8791A64736478CADD9A0D08D091854D4657DA5C06D1C32B115BAC9C2BDCAD` | token-aware Hungarian cost、all-zero negatives、masked focal、weighted total、aux/encoder loss | 与任意其他Transformers版本或paper narrative权重相同 |
| [Transformers object-detection loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_for_object_detection.py) | implementation bridge；同一release | `7D9B8B58ACDA0AD1AF0A69697AFA479C81A9E011483C920853819C16A0CEEEBD` | box L1/GIoU、Hungarian base、distributed `num_boxes` normalization与aux loop | Grounding-specific token map由本文件独立定义 |
| [Transformers Grounding DINO config](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/grounding_dino/configuration_grounding_dino.py) | implementation bridge；同一release | `BF48EC785C4EC1F99D3B17ACDE82FBE5EF869887632049E09C974C34F0844BF4` | default class/bbox/GIoU matching costs、loss coefficients、focal alpha、two-stage/aux flags | local checkpoint的实际override |
| [Transformers LICENSE](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/LICENSE) | Apache-2.0 text | `77FD4710DEF9EC3C0F6225800E0235F15A425ABD4A8B03559127FCD782612049` | repository source license线索 | model/data license自动闭合 |
| `muxi/point/point_sft.py` | local-evidence；`muxi@756e27e...`；selected path clean | `356FDC67449D2E419BAF2BD4729AC2C9A6D452BB66C6E5CED80BDCC87B04CC7F` | prompt tokens与padding用`-100`屏蔽、assistant-token supervision、SafeTrainer zero-loss fallback | detector matcher、exact model-internal CE reduction或quality uplift |
| `muxi/point/train_opd_top1_vl.py` | local-evidence；同一HEAD；selected path clean | `66C53F80844D476D34F507315A5A829E58F10F44D9CFB4F44FC868817D4443EC` | object/region top-1 labels、per-sample token mean CE、route weights与batch mean | full teacher distribution、Hungarian/box loss或robot result |
| `muxi/point/train_opd_online_vl.py` | local-evidence；同一HEAD；selected path clean | `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336` | student/teacher rollout、full-vocab KL、prefix token mask、sample weight/batch mean、route invariants | detector query loss、holdout metric uplift或closed-loop success |
| `opd_p0p1_training_metrics.csv` | local-evidence；2500 rows；selected path clean | `C8632C6351106DF3B155BEA4CB0087FC3A70A35A014854063EC4D263E0DF4BB3` | step/loss/KL/entropy/overlap/grad/token-count可复算序列 | checkpoint identity、eval denominator或因果效果 |
| `opd_p0p1_training_curve_summary.json` | local-evidence；CSV summary；selected path clean | `43176CA5A69F73FBAFDC3654D5C413D1AAADD972D2B713E593D5C40C99C5F775` | first/last窗口与last-step摘要；本轮可由CSV重算一致 | raw prediction、holdout/robot performance或唯一root cause |
| [PER-007 Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | query-token/box/phrase inference合同 | matching/loss已完整冻结 |
| [PER-008 Source Freeze](vol_06_per008_representation_choice_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | output representation选择与转换边界 | training objective或metric protocol |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-009只新增 |
| --- | --- | --- |
| PER-001 | point/box/text schema、coordinate、parser和basic static metric | 不重讲坐标格式，只冻结loss读取的target字段 |
| PER-006 | image transform、token/camera/time lineage | 不重讲preprocess，只要求train/eval lineage一致 |
| PER-007 | prompt/token、query-token logits、box/phrase、threshold/NMS inference | matching、negative target、loss component与reduction |
| PER-008 | point/box/mask/keypoint/affordance representation choice | 不评价表示优劣，只冻结当前box/token与local generation目标 |
| PER-010 | IoU/PCK/Recall、strict parser与protocol comparability | 本页不把training loss当最终metric |
| PER-011 | pseudo-label/teacher noise、confidence、leakage与curriculum | 本页只冻结teacher target如何进入loss，不评价teacher可靠性 |
| PER-015 | perception→action reachability/uncertainty/failure gate | 本页不从offline loss推出controller或robot success |
| VOL 01 Loss | CE/KL/focal等通用数学 | 本页新增grounding tensor、matching、mask与项目代码映射 |

## 4. 显式Grounding Detector的训练schema

Transformers 4.57.1实现所需最小tensor合同：

| 对象 | Shape / 语义 | 关键约束 |
| --- | --- | --- |
| `logits` | `[B,Q,L]` query×text-token logits | `L`是token positions，不是固定class数 |
| `pred_boxes` | `[B,Q,4]` normalized `cxcywh` | matching与loss前格式固定，GIoU时转corners |
| `labels[b].class_labels` | `[M_b]` | 索引当前sample的label map |
| `labels[b].boxes` | `[M_b,4]` normalized `cxcywh` | `M_b`可随sample变化 |
| `label_maps[b]` | `[C_b,L]` | class/phrase→token positions；phrase内token归一化用于matching |
| `text_mask` | `[B,Q,L]` bool | 只允许有效attention positions进入classification loss |
| `indices[b]` | `(query_idx,target_idx)` | Hungarian一对一assignment，长度为`min(Q,M_b)` |
| `num_boxes` | scalar | 跨worker平均GT数并`clamp_min(1)` |

原始GroundingDINO repo的`create_positive_map_from_span`从character spans构造`[num_boxes,256]` map并对phrase token归一化；Transformers 4.57.1则按delimiter/special-token groups构造`label_maps`。两种map construction不能在无golden test时视为完全等价。

## 5. Hungarian Matching：离散assignment合同

令第\(i\)个query为\(q_i\)，第\(j\)个GT为\(t_j\)，pairwise cost可抽象为：

\[
C_{ij}=\lambda_{\mathrm{cls}}C^{\mathrm{token}}_{ij}
+\lambda_{1}\lVert \hat b_i-b_j\rVert_1
+\lambda_{G}\bigl(-\operatorname{GIoU}(\hat b_i,b_j)\bigr),
\qquad
\hat\sigma=\arg\min_{\sigma}\sum_j C_{\sigma(j),j}.
\]

变量解释：\(\hat b_i,b_j\)是predicted/target normalized boxes；\(C^{\mathrm{token}}\)是query对目标phrase tokens聚合的classification cost；\(\lambda_{\mathrm{cls}},\lambda_1,\lambda_G\)是matching阶段权重；\(\hat\sigma\)是一对一assignment。

直觉：先决定“哪一个query负责哪一个GT”，再计算梯度；assignment本身是离散选择。实现映射：Transformers的`GroundingDinoHungarianMatcher`先算focal-style positive/negative token cost、`torch.cdist(...,p=1)`与negative GIoU，再调用SciPy `linear_sum_assignment`。证据边界：该式概括paper与version-pinned implementation bridge，不证明本地OPD存在此matcher。

matching的三个关键边界：

1. cost矩阵不是loss tensor，不能把matching cost曲线当train loss；
2. unmatched queries不会获得box regression target，但仍可能进入classification negative loss；
3. 每个auxiliary decoder output会重新matching，不保证所有层复用final assignment。

## 6. Token Classification、Negative与Focal Loss

### 6.1 Grounding DINO token target

Transformers bridge先创建全零`target_classes_onehot`，只在matched query位置写入目标phrase token map。随后用`text_mask`选择有效text positions：

```text
matched query + target phrase tokens -> positive target 1
matched query + other valid tokens  -> negative target 0
unmatched query + all valid tokens  -> negative target 0
padding/out-of-attention positions  -> masked out, not negative
```

这说明“background/no-object”在该实现中不是DETR categorical classifier的单独最后一类，而是所有有效token均为0的binary target。dataset-level negative image、wrong phrase采样或hard-negative mining没有被这段实现自动定义。

### 6.2 Focal loss

对binary target，令\(p_t\)是正确标签的模型概率，focal loss为：

\[
\operatorname{FL}(p_t)=-\alpha_t(1-p_t)^\gamma\log p_t.
\]

变量解释：\(\alpha_t\)平衡positive/negative类别；\(\gamma\)控制easy-example down-weighting；GroundingDINO/HF冻结实现使用`alpha=0.25`、`gamma=2`作为相应路径默认值。

直觉：当\(p_t\to1\)时，easy example的贡献按\((1-p_t)^\gamma\)快速衰减，但hard example仍保留较大梯度。实现映射：先`binary_cross_entropy_with_logits(reduction="none")`，再乘modulating factor和alpha，最后按冻结reduction归一化。证据边界：focal loss只能证明loss重加权，不能证明negative dataset覆盖或probability calibration。

确定性probe（negative的\(\alpha_t=0.75,\gamma=2\)）：`p_t=0.99`时loss约`7.54e-7`，`p_t=0.5`时约`0.129965`，hard/easy约`1.72e5`倍。该probe只验证公式，不是训练效果。

## 7. Box L1与GIoU Loss

assignment之后，仅matched pairs进入box supervision：

\[
\mathcal L_{\mathrm{box}}
=\frac{1}{N_{\mathrm{gt}}}
\sum_{(i,j)\in\hat\sigma}
\left[
\lambda_1\lVert\hat b_i-b_j\rVert_1
+\lambda_G\bigl(1-\operatorname{GIoU}(\hat b_i,b_j)\bigr)
\right].
\]

变量解释：\(N_{\mathrm{gt}}\)是跨worker平均后、至少为1的GT box数；\(\hat\sigma\)是matching结果；L1作用于normalized `cxcywh`；GIoU前转为corner format。

直觉：L1直接约束坐标，GIoU补充overlap/relative geometry，尤其避免普通IoU在不重叠时完全无区分。实现映射：HF base loss用`l1_loss(reduction="none").sum()/num_boxes`与`(1-diag(generalized_box_iou)).sum()/num_boxes`。证据边界：training GIoU loss不是PER-010中的evaluation IoU protocol，二者不能共享分母或threshold。

## 8. Reduction、Distributed Normalization与Auxiliary Loss

### 8.1 Classification numerator与GT denominator

HF GroundingDINO focal bridge对`text_mask`后的所有valid query-token logits求sum，再除以`num_boxes`。因此：

- unmatched-query negatives进入numerator；
- padding不进入numerator；
- denominator是GT box count，不是valid token数、query数或batch size；
- negative数量随prompt length与Q变化时，loss scale也可能变化。

### 8.2 Distributed denominator

base loss先统计local `sum(len(class_labels))`，若distributed/Accelerate已初始化则跨rank reduce，再除world size并`clamp(min=1)`。这近似每worker平均GT数，而不是全局token mean。复现必须保存world size、per-rank targets、gradient accumulation与empty-target batch行为。

### 8.3 Weighted total与auxiliary branches

Transformers 4.57.1的version-specific总loss为：

\[
\mathcal L
=2\mathcal L_{\mathrm{ce}}
+\lambda_{\mathrm{bbox}}\mathcal L_{1}
+\lambda_{\mathrm{giou}}\mathcal L_{\mathrm{giou}}
+\sum_{l\in\mathrm{aux}}\mathcal L^{(l)}
+\mathcal L_{\mathrm{enc}},
\]

其中默认`bbox_loss_coefficient=5`、`giou_loss_coefficient=2`，classification final coefficient在该loss bridge写死为2；auxiliary decoder层与two-stage encoder复制对应weight dictionary。变量解释：\(\mathcal L^{(l)}\)是intermediate decoder loss；\(\mathcal L_{\mathrm{enc}}\)仅在two-stage路径出现。

直觉：深监督让中间层也直接收到matching/class/box梯度；实现映射：`auxiliary_loss`和`two_stage`来自config，且每个aux output重新matching。证据边界：这些是Transformers 4.57.1实现值，不是所有GroundingDINO checkpoint的实际runtime config。

`cardinality_error`在base criterion中只作logging，不在GroundingDINO `weight_dict`中，因此不反向传播。不要把loss dictionary中的每个key都当成优化目标。

## 9. 权重冲突与版本门

Grounding DINO v5存在必须显式记录的source discrepancy：

| 来源位置 | Matching class/L1/GIoU | Final class/L1/GIoU |
| --- | --- | --- |
| v5正文3.5/实验段叙述 | `2 / 5 / 2` | `1 / 5 / 2` |
| v5附录Table 8 | `1 / 5 / 2` | `2 / 5 / 2` |
| Transformers 4.57.1 defaults/bridge | `1 / 5 / 2` | `2 / 5 / 2` |

因此安全口径是：论文确认三类component与Hungarian/aux structure；具体系数必须引用paper位置或runtime config。不能把一个位置的权重无条件称为“Grounding DINO官方唯一默认”。冻结官方GroundingDINO commit本身没有matcher/criterion Python主体，无法用该repo消除冲突。

## 10. 三个确定性Probe

### 10.1 Hungarian assignment

对cost matrix`[[0.2,1.3],[1.2,0.1]]`，SciPy assignment为`q0→t0,q1→t1`，总cost`0.3`；alternate总cost`2.5`。该probe证明全局一对一最小化，不证明任何模型分数正确。

### 10.2 Focal easy/hard negative

前述`p_t=.99/.5`得到约`7.54e-7/0.129965`。该probe证明easy negative被强烈下调，不证明hard-negative mining或calibration。

### 10.3 Local route reduction

若一个`both`样本的object/region token-mean CE为`2/4`，weights为`.5/.5`，sample loss为`3`；第二个object样本loss为`8`，batch mean为`5.5`。先拼所有token再求global mean通常不会得到同一结果，说明reduction order必须进入manifest。

## 11. 本地OPD三条Objective Lineage

### 11.1 Assistant-token SFT

`point_sft.py`对full conversation与prompt-only conversation分别tokenize，用`prompt_len`把`labels[:prompt_len]`设为`-100`；collator也以`-100`补齐labels。它证明prompt/padding不计入model loss，assistant output token被监督。

但该文件把实际CE交给loaded model/Transformers `Trainer`；仅凭本地wrapper不能冻结具体model class内部的shift/reduction。更重要的是`SafeTrainer`会在encode/filter失败、non-finite loss或training exception时返回zero-loss step并记录bad-batch log。若只看aggregate train loss而不统计zero-loss/dummy/retry事件，会低估数据与数值问题。

### 11.2 Routed object/region top-1 CE

`train_opd_top1_vl.py`构造`obj_top1_labels/reg_top1_labels`，只在原assistant supervised positions写teacher token ID，其余为`-100`。对每个样本分别求valid-token mean CE：

\[
L_b=w_{b,o}\,\operatorname{mean}_{t\in T_b}\operatorname{CE}(z_{b,t},y^o_{b,t})
+w_{b,r}\,\operatorname{mean}_{t\in T_b}\operatorname{CE}(z_{b,t},y^r_{b,t}),
\qquad
L=\operatorname{mean}_{b}L_b.
\]

变量解释：\(T_b\)是sample \(b\)未被`-100`屏蔽的response positions；\(w_o,w_r\)在single route为`1/0`或`0/1`，`both`为`.5/.5`；\(z\)是student logits，\(y^o,y^r\)是teacher top-1 token IDs。

直觉：每个样本先等权平均自身token，再按route混合，最后样本等权。实现映射：`F.cross_entropy(...,reduction="mean")`返回sample CE，`sample_loss.mean()`形成batch loss。证据边界：这不是full-distribution distillation，也没有detector query/box matching。

### 11.3 Online full-vocabulary KL

`train_opd_online_vl.py`先由student或teacher生成response，只取全部或prefix (T_b) positions，teacher/student在同一generated sequence上输出full-vocabulary logits：

\[
q_{b,t}=\operatorname{softmax}(z^T_{b,t}+\beta\,\operatorname{stopgrad}(z^S_{b,t})),
\qquad
L_b=\frac{1}{|T_b|}\sum_{t\in T_b}\operatorname{KL}(q_{b,t}\Vert p^S_{b,t}),
\qquad
L=\operatorname{mean}_b(w_bL_b).
\]

变量解释：\(z^T,z^S\)是teacher/student logits；\(\beta\)是veto schedule系数，0时target就是teacher distribution；\(p^S\)是student softmax；\(T_b\)由response/prefix长度决定；\(w_b\)是sample route weight。

直觉：它监督整个vocabulary distribution而非单个top-1 token；实现映射：代码先逐token求KL，再以`token_mask.sum(...).clamp_min(1)`做sample mean，最后`(sample_loss*weights).mean()`。route必须在microbatch内一致，ZeRO-3预载teacher时各rank也必须同route。证据边界：KL下降不证明teacher正确、parser输出改善或robot成功，teacher noise属于PER-011。

## 12. 本地2500行Metrics可复算边界

CSV有2500行，字段包括`step/loss/opd_loss/grad_norm/entropy/student_entropy/teacher_entropy/opd_topk_overlap/opd_loss_tokens/opd_response_tokens/route_id/veto_beta`。本轮从CSV直接重算，与summary JSON一致：

| Window | loss | opd_loss | top-k overlap | grad_norm | opd_loss_tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| first 100 mean | 0.107026 | 0.091948 | 0.610231 | 8.164954 | 35.02 |
| last 100 mean | 0.029667 | 0.029326 | 0.828569 | 1.841578 | 33.29 |
| last row / step 2500 | 0.0288 | 0.020672 | 0.806510 | 0.671648 | 24.0 |

该表只证明归档CSV内部的optimization/logging trend与summary算术一致。当前没有在本切片绑定checkpoint hash、training command/config、holdout raw predictions、同protocol parser metric或robot rollout，因此不能把first→last变化归因于某一设计，也不能声称grounding quality提升。

## 13. Typed Loss Manifest

最小可复现loss record应包含：

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

只有一个scalar `loss`无法回答：哪些targets生效、negative如何定义、分母是什么、是否有zero-loss fallback、auxiliary是否计权、distributed世界大小是否改变scale。

## 14. Project Truth Boundary与补证顺序

| 项目口径 | 当前可安全表述 | 当前不能声称 |
| --- | --- | --- |
| Public detector | 能解释GroundingDINO paper与HF 4.57.1的matching/focal/L1/GIoU/reduction差异 | 本地部署或复现了GroundingDINO training |
| OPD SFT | prompt/padding mask为`-100`，assistant tokens进入model loss | exact internal CE reduction已从wrapper证明 |
| OPD top-1 | object/region teacher top-1 token CE、route weights和sample→batch reduction | Hungarian detector、full-distribution KL或box head |
| OPD online | generated-response full-vocab KL、prefix mask、route/worker invariants | teacher可靠、holdout/robot uplift或安全校准 |
| Curve artifact | 2500 rows可复算，summary与CSV一致 | checkpoint/eval绑定、因果改进或个人ownership |

补证顺序：freeze exact command/config/checkpoint→archive batch target/mask/route manifest→保存raw per-component loss与denominator→统计zero-loss/dummy/retry→绑定per-step checkpoint→同protocol holdout parser/raw prediction→matched ablation→最后才连接action/robot结果与候选人ownership。

## 15. Source Gate结论与下一Bounded Slice

本切片已冻结：

1. Grounding DINO token-aware Hungarian matching、focal classification、L1/GIoU与aux/encoder structure；
2. unmatched query、non-target token、padding与dataset/hard-negative的非等价边界；
3. GT-box distributed normalization、valid-token numerator、weighted total与cardinality logging边界；
4. paper v5正文/Table 8/HF 4.57.1权重冲突；
5. 本地assistant-token CE、routed top-1 CE与online full-vocab KL三条objective lineage；
6. 本地2500行CSV与summary算术一致，但checkpoint/eval/robot因果未闭合；
7. 三个deterministic probe与typed loss manifest。

当前verdict为`WARN`：公源机制与实现bridge已冻结，但first-party GroundingDINO commit缺完整training criterion；本地没有显式detector matcher/box loss，SFT model-internal CE reduction未由wrapper完全证明，zero-loss fallback需要事件账本，2500步metrics未绑定checkpoint与holdout/robot结果，candidate ownership仍未确认。

`VLA-PER-009` knowledge与atomic card已在独立切片同步，题卡保持`unseen`。下一bounded slice只做`VLA-PER-010` metric/parser source freeze；不生成knowledge/card，不创建`coaching_state.md`，不改变260张题卡的状态。

## References

1. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
2. [DETR v3](https://arxiv.org/abs/2005.12872v3)。
3. [Focal Loss v2](https://arxiv.org/abs/1708.02002v2)。
4. [Generalized IoU v2](https://arxiv.org/abs/1902.09630v2)。
5. [IDEA-Research/GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)。
6. [Transformers 4.57.1 Grounding DINO loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_grounding_dino.py) 与 [object-detection loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_for_object_detection.py)。
7. [PER-007 Open-vocabulary Grounding Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)。
8. [PER-008 Representation Choice Source Freeze](vol_06_per008_representation_choice_source_freeze.html)。
9. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
