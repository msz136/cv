# VOL 05 Engineering / Evaluation：EVAL-013 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-013`  
> 难度：L2 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-013 Latency / Deadline / Jitter](../knowledge/vol_05_engineering_eval_eval013_end_to_end_latency_deadline_jitter.html)；来源边界见[Source Freeze](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)。本题不从单次 `infer_ms`、平均值、timeout配置或DataLoader p95生成实时闭环结论。

## 端到端 Latency、Deadline Miss 与 Jitter

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-EVAL-013</b> · 怎样评估 VLA 的 p99 latency、deadline miss 与 control jitter？</summary>

**面试意图**：判断你能否定义capture→apply边界、时钟合同和critical path，区分percentile、deadline、jitter、action age，并避免warm-only、coordinated omission和项目证据越界。

**30 秒回答**：先冻结capture→apply边界、时钟和checkpoint/load/H/K/Hz，记录queue、infer、transport、decode。按cold/warm/目标负载报p50/p95/p99、miss k/n、jitter、per-offset age和drop/fallback；单次infer_ms或平均值不能证明实时性。

**机制展开（约 2 分钟）**：每个request绑定obs/chunk ID与capture、queue、同步GPU infer、receive、decode、apply[j]。E2E看capture→apply[0]，逐条算chunk age；deadline事前冻结，统计miss/lateness/burst，jitter看apply间隔偏离`1/fc`。分别跑cold、steady、target load、burst/overload和fault，记录intended arrivals避免coordinated omission。candidate/baseline固定请求混合、hardware和controller；latency gate不能抵消success/safety回退。

**诊断 / 证据**：检查clock offset是否大于优化量、GPU是否只测launch、p99样本量、warm-up/compile/cache、queue tail、thermal/power、arrival model、drop是否被排除、H/K/frequency的物理时长、late work是否仍执行；保存clock/protocol manifest、raw spans、arrival/queue、action apply、outcomes、CDF/tail/load curve与checksums。

**项目挂钩**：Harness只有tool timeout/cancel；OPD无closed-loop；OpenPiVLA有timeout hook和official `infer_ms`但无capture/apply p99；WAM的300-step视频无timestamp；UWM的`13.86s→0.19s`是训练DataLoader p95。五者均不能报VLA实时闭环SLO。

**追问树**：infer latency与action age差别？为什么p99需要样本量？deadline从哪来？jitter怎样定义？ping jitter够吗？H/K/fc如何换算？GPU计时为何要同步？cold与warm为何分开？coordinated omission是什么？timeout为何不等于cancel？怎样做load/fault gate？

**易错点**：函数return当apply；平均值替代tail；p99无n；wall-clock跨机直减；只测GPU launch；warm单请求外推负载；ping jitter当control jitter；config Hz当实际Hz；只看chunk首动作；drop/timeout从分母删除；训练p95外推rollout。

**危险答案**：说“模型20ms所以能50Hz”“平均低于周期就实时”“100次足够稳定p99”“WebSocket的infer_ms就是端到端”“UWM p95下降证明控制延迟优化”或为五项目编造deadline/jitter结果。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-013 知识页](../knowledge/vol_05_engineering_eval_eval013_end_to_end_latency_deadline_jitter.html)。
2. [EVAL-013 Source Freeze](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与[Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [ENG-022 / WM-034 prerequisites](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)。
