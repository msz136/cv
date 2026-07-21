# Robot Harness P0 Bundle Audit：Runtime / Post-training / Eval

> 状态：`p0_audited / partial-raw / scorer-mixed / checkpoint-unverified / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计现有 runtime、数据、reward、十套件 aggregate 和 common-support raw evidence；不把 tool/schema proxy 分数升级为真实机器人闭环成功率。

## 1. 结论

Robot Harness 的问题定义、scope/mutex/cancel/compensation runtime、SFT/GRPO data contract、schema-aware reward 和聚合报表均有 local-direct 入口。十套件 bundle 的 arithmetic、5/5 overlap、12/12 run locator 和 28/40 primary JSONL 已复核，6/10 suite 具备四模型 exact ID support。

但 P0 仍未闭合：checkpoint binary/hash、统一 scorer/backend、base/SFT/GRPO common-support raw predictions、完整 10-suite raw、effect-sink/episode runner、operator/reviewer 和逐文件 ownership 缺失或不一致。

```text
P0 status = PARTIAL
eligible physical-success claims = 0
eligible causal-uplift claims = 0
allowed = constraint/runtime/data/reward/proxy-eval evidence
forbidden = real-robot success rate, strict 37.8→95.6 uplift, independent ownership of all code
```

## 2. P0 gate matrix

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| problem / system boundary | project scope、robot scope、mutex、cancel/compensation、tool schema | `PRESENT` | 可讲问题抽象与约束取舍 |
| runtime implementation | registry、agent runtime、sandbox/robot integration diff | `PARTIAL` | Codex-primary implementation 与候选人 owner/reviewer 分开 |
| SFT/GRPO data | 62,223 SFT、8,916 canonical GRPO、1,200 restraint manifest/script | `PRESENT WITH WARNING` | 可讲数据合同；不自动证明独立设计 |
| reward / constraint | schema-aware reward、tool restraint、safety side-effect fields | `PARTIAL` | proxy 与真实物理 effect 分离 |
| aggregate report | 5/8-model ten-suite overview、13/13 arithmetic、60/60 metrics | `PRESENT WITH WARNING` | descriptive dashboard，不是统一 benchmark |
| raw predictions | 普通目录无 full raw；hidden extraction 恢复 28/40 primary，6/10 exact support | `PARTIAL` | 不能称十套件完整 raw 或严格 paired uplift |
| scorer/backend | token-overlap fallback 与 qwen-hidden 等协议混用；完整 scorer SHA 未冻结 | `MISSING` | 37.8→95.6 不构成严格因果提升 |
| checkpoint lineage | overview 为 remote paths，0/6 本地 binary 可 hash/load | `MISSING` | 不称 checkpoint-verified |
| effect-sink / runner | project sandbox 是结构化协议层；真实 robot/browser runner 缺 | `MISSING` | 100% proxy 不等于物理成功 |
| ownership | 13-row ledger、candidate owner/reviewer 与 Codex-primary 边界 | `PENDING` | 需逐文件回答，不用 Git author 代替 |

## 3. 已核验的边界

- 8B v3 full pipeline 的 95.3/100%/44.3% 等数字与 32B ladder 分开记录；
- 32B SFT 的 `n=1333`、GRPO ladder 的 `n=1000`，且 scorer/backend 不完全一致；
- project sandbox 130-case 的 tool/scope 100%、argument exact/semantic 92.31/96.92% 只说明 schema/reference-trajectory 层；
- safety 多步任务仍弱，browser 是 deferred/format eval，没有真实浏览器 runner；
- hidden extraction 的 28/40 primary JSONL 与 6/10 exact ID support 不等于 checkpoint、scorer、protocol 已统一。

## 4. 面试可用与禁用表述

可以说：

> “我把机器人执行失败拆成 scope、互斥、取消补偿、数据路由和分层评估，并能从 runtime/schema/reward/aggregate/raw manifest 解释证据边界。十套件目前有可复算的聚合算术和部分 common-support raw，但 scorer、checkpoint、四个 suite raw 和 physical effect-sink 没闭合，所以我把 95.x 和 sandbox 100% 定位为协议层/描述性结果，不说真实机器人成功率或严格 uplift。”

不能说：

1. 37.8→95.6 是同 scorer、同 n、同 checkpoint 的 GRPO 因果提升；
2. project sandbox 100% 等于机器人闭环成功率；
3. 已完成八模型统一 benchmark；
4. 所有 runtime/training/eval 文件均由本人独立实现；
5. partial raw bundle 可以替代 checkpoint、scorer 和 effect-sink。

## 5. 关闭 P0 的最小动作

1. 为每个 run 冻结 repo/config/data/scorer/checkpoint/parent SHA；
2. 用同一 scorer、同一 n、同一 suite 重跑 base/SFT/GRPO，并保留 per-sample JSON；
3. 补齐缺失 12 个 primary JSONL、project/safety/browser effect-sink 和失败 trace；
4. 候选人回答 `OWN-RH-001`，逐项说明决定、审查、修改、运行和 Codex/协作边界。

在字段闭合前，Robot Harness 保持 `PARTIAL/WARN`，不改变 `PROJ-HARNESS-*` 或通用题卡 mastery。

## References

1. [Robot Harness Claim–Evidence Inventory](robot_harness_claim_evidence_inventory.md)
2. [Robot Harness Aggregate Bundle Gate](robot_harness_10suite_aggregate_bundle_gate.md)
3. [Robot Harness Common-Support Raw Manifest](robot_harness_common_support_raw_bundle_manifest.md)
4. [Robot Harness Ownership Ledger](robot_harness_ownership_ledger.md)
5. [五项目 P0 Artifact Intake Contract](../p0_artifact_intake_contract.md)
