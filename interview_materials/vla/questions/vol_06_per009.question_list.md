# VOL 06 PER-009 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：token-aware Hungarian matching、negative taxonomy、focal/L1/GIoU、distributed reduction、本地assistant CE/top-1 CE/online KL与loss证据边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-009 | L3 | P1 | Grounding模型训练时，Hungarian matching、negative、focal/L1/GIoU和reduction如何配合？为什么本地OPD不能说成detector loss？ | Grounding DINO/DETR/focal/GIoU、HF 4.57.1固定实现与本地OPD三条objective lineage；无first-party完整criterion、本地detector matcher/box head、checkpoint-bound holdout/robot uplift或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确matching cost只负责assignment，final criterion才产生梯度。
4. 分开unmatched query、non-target token、padding、dataset negative与hard-negative mining。
5. 冻结valid-token numerator、GT-box distributed denominator、auxiliary re-matching与revision/config权重门。
6. 本地OPD只表述为assistant-token CE、routed top-1 CE与online full-vocabulary KL，不升级为Hungarian detector loss。
7. 2500行metrics只支持optimization trace，不升级为checkpoint-bound holdout、robot uplift或个人ownership。
8. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-009 Source Freeze](../sources/vol_06_per009_grounding_matching_negative_loss_source_freeze.html) 与 [PER-009 Knowledge](../knowledge/vol_06_per009_grounding_matching_negative_loss.html)。
- 依赖缺口：first-party完整matcher/criterion、exact local command/config/checkpoint/model class、raw component loss/denominator、zero-loss/dummy/retry ledger、same-protocol holdout raw predictions、controller/robot bundle与候选人ownership confirmation。
- `VLA-PER-009` source/knowledge/card已同步且题卡保持`unseen`；下一bounded slice只做`VLA-PER-010` source freeze，不生成knowledge/card。
