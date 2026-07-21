# VOL 05 Engineering / Evaluation：EVAL-016 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-016`  
> 难度：L2 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-016 VLM / Human Proxy 一致性与偏差](../knowledge/vol_05_engineering_eval_eval016_vlm_human_proxy_agreement_bias.html)；来源边界见[Source Freeze](../sources/vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)。本题不从raw agreement、Pearson、同模型多票或公开WorldGym相关性生成“VLM可替代人工/真实环境”结论。

## VLM / Human Proxy 一致性与偏差

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-EVAL-016</b> · 怎样评估VLM judge与human评分的一致性和偏差？</summary>

**面试意图**：判断你能否先冻结评分estimand和human protocol，再选择confusion/kappa/rank/calibration，设计position/visual/temporal/adversarial probes，并守住proxy、simulator与real success边界。

**30 秒回答**：冻结评分rubric和输入证据，人类盲法双标、保留分歧并裁决。VLM固定snapshot、prompt、帧采样、票数和parser，报告混淆、critical recall、kappa、rank、calibration与cluster CI；做顺序/风格/画质/时序/视角/注入成对测试。低置信abstain，关键判定由state/human兜底。

**机制展开（约 2 分钟）**：binary看confusion、recall和kappa；0/0.5/1看weighted kappa/MAE；pairwise做A/B交换与tie；选policy看Spearman/Kendall；概率看Brier/reliability。human先校准rubric、隐藏模型身份、双标+adjudication，VLM与human尽量看相同video/state。按episode/task/policy cluster bootstrap，不把帧、五次同模型vote或annotator当独立样本。分层测contact/safety/partial/长时域与prompt injection；VLM只在验证support做triage/ranking，不能替代真实predicate。

**诊断 / 证据**：检查label prevalence、完整confusion、人-人/人-VLM agreement、raw human labels、adjudication、VLM model snapshot/API、prompt/rubric/frame sampler、所有votes/invalid/retry、tie-break、camera/temporal visibility、A/B swap、verbosity/identity/overlay mutation、per-slice CI、abstention coverage和state/effect对照。

**项目挂钩**：WorldGym公开代码是generated video→literal `gpt-4o`五票→0/0.5/1，平票偏向1；它是上游proxy，不是个人WAM结果。本地WAM仅单episode diagnostic；UWM/OpenPiVLA/OPD/Harness均无VLM×human×objective predicate成对bundle，不能报agreement、kappa或替代真实success。

**追问树**：80% agreement为何不够？kappa解决什么又不解决什么？partial label为何加权？Pearson/Spearman与agreement区别？五票为何不独立？human多数票可靠吗？信息集不同怎么办？position/verbosity/画质/时序bias怎么测？何时abstain？VLM什么时候只适合ranking？WorldGym能否替代sim/real？

**易错点**：恒猜多数类；只报accuracy；相关当一致；同一video五票当n=5；majority覆盖原始分歧；human/VLM看到不同证据却归因模型；同一VLM换prompt当独立；忽略tie/invalid/retry；把画质当成功；frame当episode；overall掩盖rare safety；公开相关性外推个人项目。

**危险答案**：说“GPT-4o和人80%一致所以可替代人工”“Pearson高就能报success”“五票多数等于五个专家”“WorldGym已证明所有机器人策略可用VLM评分”“WAM视频已有human agreement”，或为五项目编造VLM judge、人工标注与kappa结果。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-016 知识页](../knowledge/vol_05_engineering_eval_eval016_vlm_human_proxy_agreement_bias.html)。
2. [EVAL-016 Source Freeze](../sources/vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)。
3. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与[Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
4. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
7. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
8. [EVAL-011 / EVAL-015 / WM-019 / WorldGym prerequisites](../sources/vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)。
