# VOL 08 CODE-VLA-001 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：数值稳定 softmax/log-softmax、mask、低精度、梯度与 VLA 映射

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| CODE-VLA-001 | L2 | P0 | 请手写数值稳定的 softmax 或 log-softmax，并说明 mask、低精度和测试怎么处理。 | PyTorch 官方 API 与 VOL 01 基础；无本地手写/parity artifact，不做项目收益 claim |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答、机制、诊断/测试、项目挂钩、追问、易错点、危险答案和来源。
3. 明确 max-shift、logsumexp、dim/keepdim、mask、全 masked 行、fp16/bf16 和 autograd parity。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[CODE-001 Source Freeze](../sources/vol_08_code001_softmax_source_freeze.html) 与 [CODE-001 Knowledge](../knowledge/vol_08_code001_softmax.html)。
- 依赖缺口：真实手写实现、dtype/device 矩阵、forward/backward parity 与 VLA 项目调用点。
- 下一步只进行一次 `CODE-VLA-001` 白板/口述练习，或补一个 parity artifact；不批量扩展手撕题。
