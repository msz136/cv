# VOL 06 PER-006 题卡清单

> 规划日期：2026-07-19  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：Image preprocess、pixel normalization、patch/grid/token、coordinate inverse 与 camera identity contract

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-006 | L3 | P0 | 图像进入 Qwen3-VL 前，如何审计 preprocess、patch token、坐标逆变换与 camera identity？ | Qwen3-VL/Transformers/qwen-vl-utils frozen contract 与本地静态调用链；无 matched A/B、processor run bundle 或 image-conditioned DROID 证据 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 raw/processed/grid/token、resize ownership、coordinate inverse、camera order 与 performance causality。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[PER-006 Source Freeze](../sources/vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html) 与 [PER-006 Knowledge](../knowledge/vol_06_per006_image_preprocess_token_camera_contract.html)。
- 依赖缺口：per-run processor/config hash、original/resized/grid/token/camera manifest、coordinate round-trip 与 matched preprocessing A/B。
- `VLA-PER-007..008` source/knowledge/card已同步且保持`unseen`；PER-009 source已冻结，下一bounded slice只生成其knowledge，不生成card。
