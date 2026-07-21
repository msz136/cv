# VOL 04 VLA-WM-032 原子题卡：Visual Domain Randomization 与 Relevant Support

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-032  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-032 Knowledge](../knowledge/vol_04_world_model_sim2real_wm032_visual_domain_randomization_relevance.html)；来源边界见 [WM-032 Source Freeze](../sources/vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)。

## visual/domain randomization 该随机化什么，怎样避免随机化到无关分布？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-032</b> · visual/domain randomization 该随机化什么，怎样避免随机化到无关分布？</summary>

**面试意图**：判断你能否把 augmentation list 升级为有 target-support、label semantics、range provenance、validity、matched ablation 与 rollback 的数据合同，而不是认为“越随机越鲁棒”。

**30 秒回答**：分几何、外观、传感/时间、场景/任务。每项绑定 range 和 label；几何同步 pose/action，颜色身份同步 prompt。用 validity、边界样本、round-trip 拒绝无关域；做分组/combined/overwide 对照，以 real replay/closed-loop 决定扩展或回滚。

**机制展开（约 2 分钟）**：训练是 Eψ~pφℓ(f(Rψ(x)),Tψ(y))，manifest 要记 factor/bounds/source/cadence/label transform/validity/seed。Range 从 calibration、real capture、tolerance 建中心和 residual；task cue 锁定或同步。过宽会含不可行域、诱导保守。ADR 按边界性能扩范围，SimOpt 用少量 real trajectory 更新，都不证明真实 support。固定 data/compute/init 做 factor ablation，分 nominal sim、holdout、real replay、closed-loop 报结果和 rollback。

**诊断 / 证据**：建立 target inventory；逐 factor 写 failure hypothesis、unit/frame、range source、sampling cadence、label mode、validity rule。保存 nominal/low/high/random/rejected render 与 seed；对 point/box/pose/action/prompt 做 round-trip。固定 dataset states/render count/train steps/checkpoint init/seed，对 no-DR、appearance、geometry、sensor/time、scene、combined、overwide 做对照；报告 per-factor draw/reject、nominal loss、real replay strata、closed-loop success/CI 与 first failure。

**项目挂钩**：当前 evidence 未形成 visual-DR bundle：缺 factor/range/source manifest、sample render/rejection、label transform tests、matched arms、real calibration/replay、closed-loop result 与 ownership。安全说“能设计 relevant-support audit”，不能把普通 image augmentation、camera/preprocess 字段或 simulator variation 写成已完成 DR/Sim2Real 提升。

**追问树**：geometry/appearance/sensor/time/scene 分别随机什么？horizontal flip 后 action/point 怎么变？哪些因素必须锁定？Range 怎样从 real data 来？为什么越宽越差？怎样定义 invalid/unsolvable？ADR 与 UDR 差异？ADR 为何不等于真实分布？SimOpt 需要什么 authority？怎么做 matched factor ablation？real replay 能证明闭环 transfer 吗？

**易错点**：照搬论文范围；把所有 transform 当 label-preserving；改颜色不改语言；各相机独立随机破坏共同几何；只看随机化 sim；combined arm 不做单组消融；把 stress event 混进 nominal batch；ADR 无 hard cap/rollback；把 augmentation config 当 Sim2Real 结果。

**危险答案**：说“随机化越宽越好”“texture 足够多即可覆盖真实世界”“所有图像增强都不改 action label”“ADR 自动学到真实分布”“real replay 变好就证明闭环成功”“当前项目已通过 visual DR 提升真机成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-032 Source Freeze](../sources/vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)：factor groups、label contract、range、contamination gate、ADR/SimOpt 与项目边界。
2. Tobin et al., [Domain Randomization](https://arxiv.org/abs/1703.06907v1)。
3. OpenAI et al., [Learning Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5) 与 [Solving Rubik's Cube](https://arxiv.org/abs/1910.07113v1)。
4. Tan et al., [Sim-to-Real Agile Locomotion](https://arxiv.org/abs/1804.10332v2)。
5. Chebotar et al., [SimOpt](https://arxiv.org/abs/1810.05687v4) 与 [Evidence Manifest](../evidence/evidence_manifest.html)。
