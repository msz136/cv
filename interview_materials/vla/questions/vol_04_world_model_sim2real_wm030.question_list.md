# VOL 04 VLA-WM-030 题卡清单

> 规划日期：2026-07-18  
> 状态：source_frozen / knowledge_drafted / card_drafted / WARN  
> 题数：1  
> 节点：planning critical path、N/P、world/value ensemble、CUDA timing、communication、deadline/freshness/fallback

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-030 | L3 | P1 | test-time planning 增加的 N、world rollout、value scoring 与通信开销怎样计时和限险？ | Cosmos paper/code + PyTorch CUDA + Triton telemetry pattern + ENG-022/WM-023/029；无本地 WAM planning/runtime/controller bundle |

## 2. 题卡退出条件

1. ID 唯一并保持 unseen。
2. 画全 observation→communication/queue→action/world/value→selector→controller apply critical path。
3. 区分 N、P、Ew/Ev、depth、denoise 的 work 与 serial/parallel wall-clock。
4. 正确说明 CUDA Event/synchronize、cold/steady、p50/p95/p99 与 request trace。
5. 区分同步 pause budget 与异步 K/fctrl deadline，并覆盖 TTL/version/cancel/fallback。
6. 30 秒答案 ≤180 字，机制展开 ≤350 字；HTML 可折叠，review 保持 WARN。

## 3. 依赖与下一步

- 前置：[WM-030 Source Freeze](../sources/vol_04_wm030_test_time_planning_latency_risk_source_freeze.html) 与 [WM-030 Knowledge](../knowledge/vol_04_world_model_sim2real_wm030_test_time_planning_latency_risk.html)。
- 依赖缺口：local candidate/world/value ledger、N/P/Ew/Ev/depth sweep、network/IPC trace、controller apply/action age、deadline/fallback drill、matched closed-loop episodes 与 ownership。
- 下一 bounded slice 是 `VLA-WM-031` Sim2Real reality-gap taxonomy；不批量生成 WM-031..038。
