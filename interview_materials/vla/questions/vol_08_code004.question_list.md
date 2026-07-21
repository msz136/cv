# VOL 08 CODE-VLA-004 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：masked MSE/Huber、有效 denominator、empty mask 与 action schema

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-004 | L2 | P0 | 请手写带 mask 的 MSE/Huber loss，并说明 reduction、空 mask、低精度与测试。 | PyTorch MSE/Huber/SmoothL1 与 VOL 03/05 mask 审计；无本地 parity/ablation，不做项目收益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 elementwise loss、valid denominator、empty mask、Huber delta、distributed count 和 loss-mask taxonomy。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-004 Source Freeze](../sources/vol_08_code004_masked_loss_source_freeze.html) 与 [CODE-004 Knowledge](../knowledge/vol_08_code004_masked_loss.html)。
- 依赖缺口：真实手写实现、empty-mask log、forward/backward parity 和 matched MSE/Huber ablation。
- 下一步只进行一次 `CODE-VLA-004` 白板/口述练习，或补一个 parity artifact；不批量扩展手撕题。
