# VOL 05 Engineering / Evaluation：EVAL-006 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-EVAL-006`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-006 Versioned Evaluation Manifest](../knowledge/vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)；来源边界见 [Source Freeze](../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)。本题不把同名 benchmark、package version 或 scorer label 当成项目结果可比证据。

## Benchmark / Environment / Controller / Scorer Versioning

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-006</b> · 怎样版本化 benchmark、environment、controller 和 scorer，保证评测可重放、可比较？</summary>

**面试意图**：判断你能否区分 label/SemVer/tag、immutable revision、content digest与resolved semantics，并把protocol identity绑定到episode/summary，而不是只说“记Git commit和seed”。

**30 秒回答**：冻结task/init、env/wrappers、controller gains/Hz、scorer predicate/parser、policy/runtime到manifest；类型校验/脱敏后做JCS+SHA256并绑定episode/summary。先diff；除model外一致才exact，否则bridge或fail closed。

**机制展开（约 2 分钟）**：label交流，revision定位，digest验bytes；SemVer patch仍可改score，unversioned env可指latest，commit要配dirty diff。manifest含task registry、env assets/reset、controller mapping/gains/timing、scorer threshold/parser/invalid rule、policy和runtime。除model外semantic fields一致才exact；diff需同checkpoint/init或raw outputs双跑/双评分，否则non-comparable。task/controller/scorer变化生成新protocol SHA。

**诊断 / 证据**：测试tag object→commit dereference、mutable tag→OCI digest、unversioned→resolved EnvSpec、dirty diff、task/assets/wrapper hash、controller config/decoded pickle、scorer threshold/parser/prompt、JCS key-order invariance与semantic-value sensitivity。检查每个episode/summary只有一个protocol SHA，并保存old/new bridge、migration diff与无法重算原因。

**项目挂钩**：UWM四套LIBERO protocol不能混；WAM的RoboCasa fork 0.2/official 1.0.1、controller pickle与84/118 exclusion未闭合；OpenPiVLA 97.4缺env/controller/scorer/lineage；OPD strict/protocol-fixed/lenient是不同scorer；Robot Harness base与SFT/GRPO的n和embedding/token-overlap scorer不同。

**追问树**：SemVer patch为何可能改score？tag/commit/blob/digest差别？unversioned env为何危险？同OSC_POSE为何仍不可比？controller pickle怎样审计？scorer bug fix怎样bridge？VLM scorer怎么freeze？protocol hash哪些字段要进？dirty repo如何记录？什么时候exact/bridge/non-comparable？五项目各缺什么？

**易错点**：只存版本字符串、seed或command；把latest/tag当immutable；commit忽略dirty diff/LFS/assets；container digest忽略mounted config；controller只存名字；scorer只存metric名；raw YAML直接hash；summary混多个protocol；有hash就声称实验正确。

**危险答案**：说“同benchmark名就能比”“都是v1.x所以兼容”“同seed保证同环境”“镜像tag固定即可”“scorer修bug不影响结果”“只要Git commit相同就能复现”。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-006 知识页](../knowledge/vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)：四层身份、六部分manifest、protocol hash、comparability与migration tests。
2. [EVAL-006 Source Freeze](../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)：SemVer/Gymnasium/OCI/RFC 8785 frozen sources与五项目边界。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：n/scorer/checkpoint protocol drift。
4. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：fork/controller/exclusion/provenance缺口。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：四套LIBERO protocol与raw lineage缺口。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：archive/formal checkpoint与eval version断点。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：strict/protocol-fixed/lenient scorer版本边界。
