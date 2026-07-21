# VOL 05 Engineering / Evaluation：EVAL-009 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-009`  
> 难度：L2 1题  
> 优先级：P0 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-009 Recomputable Bundle](../knowledge/vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)；来源边界见[Source Freeze](../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。本题不把summary表、精选视频或无lineage JSONL包装成可复算结果。

## Raw Predictions、Episode Trace、Video 与可复算 Summary

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-009</b> · 怎样设计评估artifact，让summary可从raw predictions/episode trace重算？</summary>

**面试意图**：判断你能否把summary、raw rows、step trace、video和immutable bundle分层，设计守恒、checksum/provenance、deterministic reducer与独立复算门。

**30 秒回答**：raw是source，summary是derived。绑定run/protocol/scorer，保留raw/parsed output、valid/exclusion/贡献；rollout存obs→action→command→state。planned=valid+excluded+missing，video作sidecar；reducer从raw重算。

**机制展开（约 2 分钟）**：bundle含manifest、protocol/schema、raw rows或episode trace、video index、scorer/reducer revision、summary、exclusions和checksums。先验payload/hash，再查ID/shape/time/lineage与planned守恒；用冻结parser/scorer、weights、exclusion、aggregation重算分子分母、per-task和overall，整数exact、浮点声明dtype/tolerance。video映射episode/step但不作分母；scorer升级在同raw生成新summary。clean环境复算一致才称recomputable。

**诊断 / 证据**：测试缺文件、重复episode/retry、crash/timeout、invalid parser、non-finite/shape错、timestamp不单调、video掉帧/错episode、summary手改、scorer/hash漂移、partial shard和alternate output root。保存verify/recompute命令、stdout、exit code与新summary hash。

**项目挂钩**：WAM达到单episode trace/video L3 partial但不可重算comparison；OpenPiVLA 97.4与UWM 186/250仍是summary层；OPD有10k input manifest和tables但缺raw predictions；Robot Harness缺共同n/scorer的base/SFT/GRPO raw outputs，browser无runner trace。

**追问树**：summary为何不够？raw与parsed为何都存？video为何不能算分母？crash/missing如何处理？retry如何去重？hash能证明什么？scorer升级怎么重算？MCAP是否强制？clean recompute如何验收？五项目各在哪层？

**易错点**：只存aggregate；只存parsed不存raw；从video文件名统计；失败episode静默丢弃；retry重复计数；summary覆盖历史；有SHA就说语义正确；checkpoint/protocol不绑定；媒体与trace无timestamp map；只在原机器脚本能跑。

**危险答案**：说“有summary JSON就可复现”“有视频就能算success”“JSONL存在就属于该checkpoint”“hash一致说明metric一定正确”“crash episode不算评估”或“重新手算表格就是independent recompute”。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-009 知识页](../knowledge/vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)。
2. [EVAL-009 Source Freeze](../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。
3. [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
5. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
7. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
8. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
