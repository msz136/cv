# VOL 06 Perception / Grounding / Navigation：PER-009 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-009`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-009 Grounding Matching / Negative / Loss Knowledge](../knowledge/vol_06_per009_grounding_matching_negative_loss.html)；来源边界见 [PER-009 Source Freeze](../sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.html)。

## Grounding Matching、Negative 与 Loss Reduction

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-009</b> · Grounding模型训练时，Hungarian matching、negative、focal/L1/GIoU和reduction如何配合？为什么本地OPD不能说成detector loss？</summary>

**面试意图**：判断你能否分开matching cost与final loss，解释token-axis negative、mask和distributed reduction，并把公源detector机制与本地生成式CE/KL objective放在正确证据边界内。

**30 秒回答**：Hungarian用token、L1、GIoU cost做一对一分配；cost只定query–GT责任，梯度来自分配后的loss。unmatched query仍是分类负例，padding须mask，权重/reduction须绑定版本。本地OPD是assistant CE、top-1 CE和online KL，没有matcher或box head。

**机制展开（约 2 分钟）**：logits为`[B,Q,L]`，类别轴是text token。matcher在`Q×M` cost上分配；matched query写phrase map并回归box，unmatched query对有效token全为0，padding由`text_mask`排除。分类loss对valid query-token求和后除跨worker平均GT数；box算L1/GIoU，aux层重匹配。paper正文与Table 8权重冲突，须冻结版本/config；cardinality只logging。本地SFT用`-100`屏蔽prompt/padding；top-1 CE与online KL按token→sample→route→batch聚合，均无query set或box head。

**诊断 / 证据**：按prediction/target schema与positive map→positive/negative/masked counts→class/L1/GIoU component costs→Hungarian assignment probe→`cxcywh/xyxy`转换→numerator/`num_boxes` denominator→aux/encoder `weight_dict`→world size与empty-target batch检查。若本地loss异常，再查有效response token、route一致性、zero-loss/dummy/retry ledger和teacher/student checkpoint。任何“质量提升”都要继续绑定immutable checkpoint、raw holdout prediction、strict parser与同protocol metric；2500行optimization trace本身不够。

**项目挂钩**：本地`point_sft.py`只直接证明assistant-token supervision及prompt/padding `-100` mask；`train_opd_top1_vl.py`是object/region teacher top-1 token CE；`train_opd_online_vl.py`是generated-response full-vocabulary KL。三条路径均未读到detector query set、Hungarian matcher、unmatched-query negatives或L1/GIoU head。归档CSV的2500行与summary可复算，只能讲loss/overlap/grad的optimization trend，不能讲checkpoint-bound holdout、teacher正确性、robot uplift或个人ownership。

**追问树**：matching cost为什么不是training loss？Hungarian assignment能否直接反向传播？unmatched query有没有梯度？padding和negative有什么区别？focal loss等于hard-negative mining吗？为何classification numerator除GT box数？aux层是否复用final matching？`cardinality_error`会不会优化？Grounding DINO权重究竟是哪组？top-1 CE与full-vocab KL怎样区分？loss下降如何补成可信grounding提升？

**易错点**：把cost matrix当total loss；把unmatched query、非目标token、padding和negative image混为一谈；认为focal自动完成hard-negative mining；默认所有loss按batch mean；看到loss dict key就认为它反向传播；忽略prompt长度、query数和world size对scale的影响；不绑定revision就背固定权重；把生成式coordinate supervision称为set-prediction detector。

**危险答案**：说“Hungarian cost就是最终loss”“padding也是negative”“未匹配query完全没有梯度”“用了focal就是做了hard-negative mining”“Grounding DINO永远固定使用某一组权重”“OPD有point/box数据所以用了Grounding DINO loss”，或“2500步loss下降证明holdout与机器人成功率提升”。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-009 Grounding Matching / Negative / Loss Knowledge](../knowledge/vol_06_per009_grounding_matching_negative_loss.html)：tensor schema、matching/final loss、negative、reduction、本地objective lineage与面试边界。
2. [PER-009 Source Freeze](../sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.html)：primary/official/local revision、hash、权重冲突、metrics复算与deterministic probes。
3. [Grounding DINO v5](https://arxiv.org/abs/2303.05499v5)。
4. [DETR v3](https://arxiv.org/abs/2005.12872v3)。
5. [Focal Loss v2](https://arxiv.org/abs/1708.02002v2)。
6. [Generalized IoU v2](https://arxiv.org/abs/1902.09630v2)。
7. [Transformers 4.57.1 Grounding DINO loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_grounding_dino.py) 与 [object-detection loss](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/loss/loss_for_object_detection.py)。
8. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
