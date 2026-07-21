# VOL 05 Engineering / Evaluation：EVAL-012 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-012`  
> 难度：L2 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-012 Robustness Matrix](../knowledge/vol_05_engineering_eval_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix.html)；来源边界见 [Source Freeze](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)。本题不从 OOD 名称、augmentation、camera 字段或不同 protocol 百分比生成鲁棒性结论。

## OOD、扰动、遮挡、视角与鲁棒性矩阵

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-EVAL-012</b> · 怎样设计并证明 VLA 的 OOD / 遮挡 / 视角鲁棒性？</summary>

**面试意图**：判断你能否定义 target envelope，构建 clean–perturbed paired matrix，正确处理 severity、label/visibility/solvability、分格统计和项目证据边界。

**30 秒回答**：先从部署数据定义 target、diagnostic 和 stress 范围。固定 checkpoint 与任务协议，把同 task/init 的 clean 和 factor×severity episode 配对，并验证扰动生效、标签一致、仍可解；逐格报 k/n、drop、curve 与 worst cell，blackout 单看 fallback。

**机制展开（约 2 分钟）**：矩阵分 photometric、viewpoint、occlusion、sensor/missing-view、scene/layout 和 semantic。每格保存 unit/range source、pair ID、code/asset SHA 与 raw trace/video；固定 checkpoint、task/init、controller、predicate，只改一个 factor。不可解样本进 rejection ledger，极端故障进 stress/fallback。先 one-factor 定位，再做有部署依据的组合；逐格算 uncertainty，预注册 critical gate，sim/offline 不替代必要 real canary。

**诊断 / 证据**：查 severity 是否有物理/target 来源、transform 是否实际生效、camera pose 是否改变 reachability、颜色 cue 是否改语义、occlusion 的 per-view visible fraction、clean/perturbed 是否同 support、低 clean 是否让 retention 失真、critical cell 是否被 macro average 掩盖；保存 matrix spec、pair index、accepted/rejected ledger、render overlay、raw episodes、per-cell summary、curve 和 checksums。

**项目挂钩**：Robot Harness 只有 OOD suite 名；OPD 是静态 seen/unseen slice；OpenPiVLA 缺 raw matrix；WAM 只有单 episode 的三 camera 字段；UWM strict/reset 改了 protocol。五者都不能声称已有 closed-loop robustness matrix。

**追问树**：OOD 相对什么？target 与 stress 怎么分？为何要 clean pairing？severity 如何定？ImageNet-C 能借什么、不能借什么？camera pose 为何非普通 augmentation？遮挡如何判可解？retention 何时误导？one-factor 与 composed stress 顺序？worst cell 怎样做统计？sim robustness 能否替代真机？

**易错点**：suite 名即 OOD；augmentation 即鲁棒；不同 init/protocol 直接相减；severity 任意编号；不可解样本算失败；只报 overall；多相机字段当 view ablation；pixel corruption 当真实 camera envelope；组合扰动不先单因素；sim/offline 替代 real canary。

**危险答案**：说“我们有 OOD set 所以鲁棒”“ImageNet-C 五档可直接搬到机器人”“WAM 三路 camera 已证明多视角鲁棒”“UWM 232/250 比 186/250 说明 reset 扰动提升”“遮住目标失败就是模型问题”或为五项目编造 robustness curve。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-012 知识页](../knowledge/vol_05_engineering_eval_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix.html)。
2. [EVAL-012 Source Freeze](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)。
3. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
4. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)与 [Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
7. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
8. [WM-032 / WM-035 / PER-003 prerequisites](../sources/vol_05_eval012_ood_perturbation_occlusion_viewpoint_robustness_matrix_source_freeze.html)。
