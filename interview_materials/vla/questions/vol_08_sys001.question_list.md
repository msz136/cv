# VOL 08 SYS-001 题卡清单

> 规划日期：2026-07-18  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：VLA 训练—checkpoint—评估—rollout 的可复现系统设计

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| SYS-VLA-001 | L3 | P0 | 如何设计一个可复现的 VLA 训练—评估平台，避免数据、checkpoint、评估协议和 rollout 互相污染？ | PyTorch DCP/reproducibility、Open X、LIBERO、OpenPI 与五项目局部证据；缺统一 registry、raw rollout 与 ownership，不称平台已完成 |

## 2. 题卡退出条件

1. ID 唯一并保持 `unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 明确区分 dataset/run/bundle/evaluation/rollout，以及 train/offline/sim/real/proxy metric namespace。
4. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 `WARN`。

## 3. 依赖与下一步

- 前置：[SYS-001 Source Freeze](../sources/vol_08_sys001_vla_training_eval_platform_source_freeze.html) 与 [SYS-001 Knowledge](../knowledge/vol_08_sys001_vla_training_eval_platform.html)。
- 依赖缺口：统一 artifact registry、checkpoint/normalizer hash、raw episode bundle、paired protocol 与 ownership ledger。
- 下一步只进行一次 `SYS-VLA-001` 真实口述，或补一个平台 artifact；不批量扩展 VOL 08。
