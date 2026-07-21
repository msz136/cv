# VOL 04 WM-032 Source Freeze：Visual Domain Randomization 与 Relevant-support Contract

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-032 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-032  
> 本轮边界：冻结 visual/domain randomization 的 geometry、appearance、sensor/time、scene/task 因子，label-preserving/equivariant 约束、range 来源、irrelevant-domain rejection、matched ablation 与 distribution update；不展开 WM-033 dynamics SysID，不给个人项目虚构随机化配置或 transfer 指标。

## 1. 结论先行

1. **随机化目标是覆盖 target nuisance，而不是让图像越怪越好。**训练分布应覆盖真实 camera/appearance/sensor 变化，同时排除不可能状态、破坏任务语义的变换和无意义尾部。[S1][S3][S4]
2. **先分四组。**Geometry：camera pose/intrinsics、object pose/scale；appearance：light/material/texture/background/color；sensor/time：noise、blur、compression、occlusion/dropout、timestamp/jitter；scene/task：clutter/distractor/layout，但只能改目标任务实际会变化的部分。[S1][S2][S5]
3. **每个 transform 必须有 label contract。**纯 appearance nuisance 可保持 action/label；camera/object geometry 变化需重新渲染或同步变换 point/box/pose/action target；语言指令含颜色、左右或对象身份时，随机化对应语义必须同步改 prompt/label，否则是在注入错误监督。
4. **Range 应有来源。**可测量变量以 calibration/real-capture statistics 为中心加 residual/margin；未知但 plausible 的变量做 bounded coverage；不应照搬论文的 camera、texture、noise 或物理范围。[S2][S3]
5. **过宽分布有成本。**SimOpt 明确指出 overly wide distributions 会包含不可行场景、阻碍 policy learning 或诱导过度保守；Tan et al. 也把 dynamics randomization 描述为 robustness–optimality trade-off。[S3][S4]
6. **ADR 不是“自动找到真实分布”。**Frozen ADR 从初始窄分布出发，在 boundary performance 超过/低于 threshold 时逐维扩展/收缩 uniform bounds；它生成 curriculum，但仍需要参数语义、硬边界、validity filter 和 real validation。[S5]
7. **Real replay 与闭环证据分层。**Unlabeled real images/calibration 可用于 range/coverage；real replay 可测 processor/feature/action stability；只有 matched closed-loop trials 才能支持 transfer benefit。Sim-only robustness 不等于 Sim2Real。
8. **要做 matched factor ablation。**固定 checkpoint initialization、train/eval budget、sim seeds、task/init/controller，对 no-DR、appearance、geometry、sensor/time、scene、combined、overwide 分组，报告 nominal/randomized/real replay/closed-loop 与 per-stratum failure。[S1][S2]
9. **当前项目证据没有 visual-DR bundle。**相关 evidence 路径未发现 randomization manifest、factor/range/source、sample renders、matched ablation、real calibration/replay 或 real closed-loop ownership；只能说“能设计/审计”，不能说“已用 DR 改善项目迁移”。[S7]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Tobin et al., *Domain Randomization* | arXiv:1703.06907v1；ar5iv snapshot UTF-8 SHA-256 `faba518e98357c65a59d41f340bb723d4bb84c50eb359813597daab113dcd33a` | camera position/orientation/FOV、lighting、object pose、texture、distractor 与 ablation | 其范围/texture count 对任意 VLA 通用；precision localization 等于 policy transfer | primary / checked |
| S2 | OpenAI et al., *Learning Dexterous In-Hand Manipulation* | arXiv:1808.00177v5；ar5iv snapshot SHA-256 `826fb63d545518661a10b9cac05110bf7c813e88f99698d3b9e98cb313f81e93` | calibration-centered physics range、camera/intrinsics/light/material、correlated/un-correlated noise、randomization ablation | Shadow Hand 参数与范围可外推；广泛随机化自动安全 | primary / checked |
| S3 | Tan et al., *Sim-to-Real Agile Locomotion* | arXiv:1804.10332v2；ar5iv snapshot SHA-256 `c34db6210074989010a635a11705e17da4a38d4b105e471159a9cc832a120a49` | measurement-centered ranges、uncertain/drifting parameters、robustness–optimality trade-off | locomotion range 直接用于 camera/VLA；测量即完整 target support | primary / checked |
| S4 | Chebotar et al., *SimOpt* | arXiv:1810.05687v4；ar5iv snapshot SHA-256 `d655425962c13511caf54a1c669144793e0747366db9f9b48d0f0d5d58ca2391` | overly wide distribution 的 infeasible/conservative 风险；少量 real rollout 更新 simulator distribution | 可无安全代价收集 real data；trajectory matching 是 exact SysID | primary / checked |
| S5 | OpenAI et al., *Solving Rubik's Cube with a Robot Hand* | arXiv:1910.07113v1；ar5iv snapshot SHA-256 `a482412afe1c54a733670ef6d5f04126eafc38b32f862b25221248d739520522` | ADR per-dimension uniform bounds、boundary sampling、performance thresholds、逐步扩展；vision factor groups | ADR bounds 等于真实分布；自动避免所有 irrelevant factors | primary / checked |
| S6 | OpenCV calib3d | OpenCV 4.13.0 page；访问 2026-07-18；UTF-8 SHA-256 `e0a638f53a7f09287b8c502a364cfed8afa2fea3531a7dbe81bd30f4583825ce` | intrinsics/extrinsics/distortion 与 world→camera geometry contract | 某项目 calibration/range 已正确 | official-doc / checked |
| S7 | Sim2Real Audit D + WM-031 + Evidence Manifest | Audit D SHA-256 `18318d37f2060a771d3074b3a2d70b7e07487091de23d9cf6a9599f4080ec200`；WM-031 SHA-256 `d25897218b4a276a0d9a981c826e8680ba21db7e64b298963eace10184877a97`；manifest `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6` | taxonomy、range/test matrix 与个人证据缺口 | 本地 DR execution、real transfer benefit 或 ownership | local-audit / WARN |

ar5iv 只作为冻结的全文转换 snapshot；论文身份和 revision 以 arXiv 为准。所有公式化 relevance/contamination gate 是基于来源的工程综合，不是论文原定理。

## 3. Randomization 训练合同

令 simulator observation 为 \(o=R_{\psi}(x)\)，\(\psi\sim p_{\phi}(\psi)\) 是 randomization parameter，训练目标为：

\[
\theta^*(\phi)=\arg\min_{\theta}
\mathbb E_{(x,y)\sim\mathcal D_{sim},\,\psi\sim p_\phi}
\left[\ell\left(f_\theta(R_\psi(x)),\,T_\psi(y)\right)\right].
\]

变量解释：\(R_\psi\) 渲染/扰动 observation，\(T_\psi\) 是 label/action 同步变换；若 \(\psi\) 是纯 nuisance，\(T_\psi(y)=y\)；若 camera/object geometry 或 task semantics 改变，必须定义新的 target。实现映射：randomization manifest 需记录 factor、distribution、bounds/source、cadence/correlation、label transform、validity filter 和 seed。

目标不是最大化 distribution entropy，而是让训练后模型在 real target distribution \(q_r\) 上表现良好：

\[
R_{real}(\phi)=
\mathbb E_{z\sim q_r}
\left[\ell_{task}(f_{\theta^*(\phi)}(z),y_z)\right].
\]

变量解释：真实风险通常只能从小规模 real replay/closed-loop 估计；randomized-sim validation 只是 proxy。若没有 real data，必须将 support coverage 标为假设而非已验证。

## 4. 四组 randomization 因子

| 因子组 | 可随机化项 | Label/semantics 风险 | 最小范围来源 |
| --- | --- | --- | --- |
| geometry | camera extrinsics/intrinsics/FOV、mount tolerance、object pose/scale、robot/camera geometry | pixel point/box/pose 要同步；任意 2D warp 未必对应真实 camera；object pose 变化需重算 expert action | calibration residual、mount tolerance、real pose histogram |
| appearance | light direction/intensity/color、exposure/WB/gamma、material/texture、background、shadow/reflection | instruction 含 color/material 时不能随意改；specular/lighting 过强可遮掉 task cue | real capture histogram、lighting envelope、material catalog |
| sensor/time | readout noise/bias、blur、compression、occlusion/dropout、depth holes、timestamp offset/jitter | frame/proprio/action history 要保持时间一致；occlusion 不应让任务不可解 | static/dynamic capture、network/camera trace、dropout/event log |
| scene/task | clutter、distractor、object instance/layout、camera count/availability | target identity、left/right、goal、success、expert action 可能改变；必须同步 prompt/label | deployment inventory、task/init manifest、object/layout split |

Tobin 与 ADR vision recipe提供了许多候选项，但“论文随机化过”不是本任务的 range 依据。[S1][S5]

## 5. Label-preserving、equivariant 与 semantic-changing

### 5.1 Label-preserving nuisance

若 transform 不改变世界状态与动作目标：

\[
T_\psi(y)=y.
\]

例如小范围 exposure、white balance、sensor noise、texture nuisance，前提是它们不改变语言/对象语义且不遮蔽完成任务的必要信息。

### 5.2 Equivariant transform

若 geometry 变换 \(g\) 改变 label coordinate：

\[
y'=\rho(g)y.
\]

变量解释：\(\rho(g)\) 是 label/action 的对应变换。例如水平 flip 后 pixel point/box 要 flip；camera frame action/pose 必须按 extrinsics 重算；object pose 变化需要 simulator 重新生成 observation 与 expert/action target。只改 image 不改 target 会制造冲突监督。

### 5.3 Semantic-changing transform

若 instruction 是“抓红色方块”，把目标随机为蓝色但保留 prompt/label 会改变任务。处理只能是：锁定该 factor、同步修改 prompt/target，或将其放入独立 task-generalization 数据，而不是称为 label-preserving DR。

## 6. Relevant support 与 contamination gate

定义 task-plausible set \(\Omega_{valid}\)，概念上的 contamination 为：

\[
C(\phi)=
\Pr_{\psi\sim p_\phi}
\left[\psi\notin\Omega_{valid}\;\lor\;T_\psi\text{ 未定义/不一致}\right].
\]

变量解释：\(\Omega_{valid}\) 包含硬件/场景可实现、任务仍可解、传感器/标签语义一致的参数组合。它通常无法精确计算，但可用 hard constraints、sample render review、label round-trip、task solvability checks 和 rejection reasons 审计。

Real-support coverage 可用有限 calibration/replay 样本做近似：

\[
\widehat G(\phi)=\frac1n
\sum_{i=1}^{n}
\mathbf 1\{\hat\psi_i^r\in\operatorname{supp}(p_\phi)\}.
\]

变量解释：\(\hat\psi_i^r\) 是从 real calibration/capture 估计的 factor；不可观测 factor 用 proxy discrepancy 和 `unknown` 标记。高 coverage 不保证 transfer，高 contamination 也可能被均值指标掩盖。

## 7. Range 设计：四类处理

| 因子 | 处理 | 例子 | 禁止做法 |
| --- | --- | --- | --- |
| measured | nominal + residual/quantile + margin | intrinsics/extrinsics、exposure、latency、noise | 照搬论文 ±x% |
| uncertain but plausible | bounded prior + stress bucket | mounting vibration、lighting、object pose | 无上限无限扩宽 |
| semantic locked | 固定或同步修改 label/prompt | target color、left/right、object identity | 保持旧 label 继续训练 |
| rare/safety | 与 nominal training 分开，event/stress eval | full occlusion、packet loss、camera failure | 用大量不可解样本污染 nominal batch |

Tan/OpenAI dexterous 的直接启发是以测量/calibration 作为中心，对更不确定或会漂移的量扩大覆盖；不是复制其数值。[S2][S3]

## 8. 避免无关分布的八个 Gate

1. **Target inventory**：列 deployment camera/light/object/layout/sensor/event，不从 augmentation library 随机挑项。
2. **Factor hypothesis**：每个 factor 写“它模拟哪种真实变化、影响哪条 failure trace”。
3. **Label/semantic check**：声明 invariant/equivariant/semantic-changing 与 target transform。
4. **Physical/task validity**：检查 camera pose/FOV、object pose、illumination、occlusion 是否可能且任务仍可解。
5. **Range evidence**：绑定 calibration、real capture、manufacturing tolerance、日志或明确 prior；缺失记 `unverified`。
6. **Sample audit**：保存 nominal、low/high boundary、random samples、rejection reason 和 seed。
7. **Matched factor ablation**：固定 data count/compute/checkpoint init，仅替换 one group；combined 与 overwide 为独立 arm。
8. **Real gate + rollback**：real replay/closed-loop 不提升或 nominal/target strata 回退时停止扩宽，恢复上个 distribution revision。

## 9. UDR、ADR、SimOpt 的边界

| 方法 | Distribution update | 优点 | 不能自动解决 |
| --- | --- | --- | --- |
| fixed/UDR | 人工设定 \(p_\phi\)，训练期固定 | 简单、可复现 | range 来源、factor relevance、real coverage |
| ADR | 从窄 bounds 开始，按 boundary performance thresholds 扩/缩维度 | curriculum、减少人工逐维调参 | target-real alignment、semantic validity、维度相关性 |
| SimOpt | 用少量 real trajectory 与 sim behavior discrepancy 更新 distribution | 直接利用 transfer-relevant real behavior | real rollout safety/cost、metric shortcut、exact SysID |

ADR 的 boundary performance 说明当前 policy 是否能处理该边界，不说明该边界在现实中有多大概率；仍需 hard bounds 与 real replay。SimOpt 也不应在 policy 不安全时无约束收集 real rollout。[S4][S5]

## 10. Matched ablation 与指标

最小 arms：

1. no DR；
2. appearance only；
3. geometry only；
4. sensor/time only；
5. scene/task-relevant only；
6. relevant combined；
7. overwide/invalid stress（诊断用，不与 nominal batch 混合）。

固定 dataset episode/state、render count、train steps/effective batch、checkpoint init、task/init、controller、seed plan。输出：

| Eval stratum | 指标 | 主要问题 |
| --- | --- | --- |
| nominal sim | task metric/loss | 是否牺牲 nominal optimality |
| randomized in-support | per-factor metric | 是否学到预期 robustness |
| held-out composition | unseen factor combination | 是否只记住训练组合 |
| real replay | feature/point/box/action stability、failure strata | support 是否更接近真实 observation |
| real closed-loop | success + CI、first failure、safety events | transfer 是否真正改善 |

同时报告 factor draw/rejection counts、distribution revision、sample bytes/renders、train cost。只报 combined success 无法识别无效或负迁移 factor。

## 11. 可审计伪代码

```python
def sample_visual_domain(manifest, rng, task):
    # 1. Sample only factors registered for this deployment/task contract.
    params = manifest.sample(rng)

    # 2. Reject physically impossible, unsolvable or semantically inconsistent samples.
    valid, reason = validate_physics_task_semantics(params, task)
    if not valid:
        log_rejection(params, reason)
        return None

    # 3. Render observation and transform labels/actions when geometry or semantics change.
    obs = render(task.state, params)
    target = transform_target(task.target, params.label_transform)
    assert label_roundtrip_passes(obs, target, params)

    # 4. Persist factor values, source, seed and distribution revision for ablation/replay.
    log_sample(params, rng.seed, manifest.revision)
    return obs, target
```

这是 randomization data contract，不是个人项目已存在的实现。真实 pipeline 还需 processor parity、dataset caching/versioning、camera correlation、multi-view/time consistency 与 safety-stress split。

## 12. 项目真实性边界

对 `interview_materials/vla/evidence/`、OpenPiVLA evidence freeze 和本地 artifact gate 的本轮检索没有发现可闭合 WM-032 的 visual-DR bundle：factor/range/source manifest、sample render ledger、label transform tests、matched arms、real calibration/replay、closed-loop result 与 ownership 未同时存在。[S7]

安全表达：**“我会先用 calibration/real capture 定义 relevant support，为每个 factor写 label contract 和 validity gate，再做 factorized matched ablation与 real replay/closed-loop验证；当前项目没有足够证据声称已完成这些实验。”**

不能说：**“我给图像加了增强，所以项目具备 domain randomization / Sim2Real 提升。”**常规 train-time augmentation、上游配置字段、simulator camera变化或 sample render 均不等于 matched transfer evidence。

## 13. 下一入口

下一 bounded slice 是 `VLA-WM-033`：dynamics randomization 与 system identification 如何互补，参数范围怎样确定。本页不提前给 mass/friction/actuator range。

## 参考文献（References）

1. Tobin et al., [Domain Randomization](https://arxiv.org/abs/1703.06907v1), 2017。
2. OpenAI et al., [Learning Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5), 2019。
3. Tan et al., [Sim-to-Real Agile Locomotion](https://arxiv.org/abs/1804.10332v2), 2018。
4. Chebotar et al., [SimOpt](https://arxiv.org/abs/1810.05687v4), 2019。
5. OpenAI et al., [Solving Rubik's Cube with a Robot Hand](https://arxiv.org/abs/1910.07113v1), 2019。
6. [OpenCV Camera Calibration and 3D Reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)。
7. [VOL 04 Source Audit D：Sim2Real](vol_04_sim2real_claim_to_mechanism.html)。
8. [WM-031 Reality-gap Taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html)。
9. [VLA Project Evidence Manifest](../evidence/evidence_manifest.html)。
