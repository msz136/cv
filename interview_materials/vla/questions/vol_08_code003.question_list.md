# VOL 08 CODE-VLA-003 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：LayerNorm/RMSNorm、normalized shape、epsilon、dtype 与 parity

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-003 | L2 | P0 | 请手写 LayerNorm 和 RMSNorm，并说明归一化轴、epsilon、低精度与训练/推理差异。 | PyTorch LN/RMSNorm、RMSNorm paper 与 VOL 01 基础；无本地 parity/ablation，不做项目收益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 normalized shape、population variance、RMS 不减均值、eps、affine、低精度和无 running stats。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-003 Source Freeze](../sources/vol_08_code003_norm_source_freeze.html) 与 [CODE-003 Knowledge](../knowledge/vol_08_code003_norm.html)。
- 依赖缺口：真实手写实现、forward/backward parity、profile 和 matched norm ablation。
- 下一步只进行一次 `CODE-VLA-003` 白板/口述练习，或补一个 parity artifact；不批量扩展手撕题。
