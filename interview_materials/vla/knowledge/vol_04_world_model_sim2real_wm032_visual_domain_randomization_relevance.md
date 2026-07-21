# VOL 04 World Model / Sim2Real：Visual Domain Randomization 与 Relevant-support Design（WM-032）

> 状态：drafted / VLA-WM-032 / knowledge_34_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释 visual/domain randomization 的因子、label contract、range、irrelevant-domain gate 与 matched evaluation；不声称本地项目已实施或改善真实迁移。  
> 前置：[WM-031 Reality-gap Taxonomy](vol_04_world_model_sim2real_wm031_reality_gap_taxonomy.html)、[WM-032 Source Freeze](../sources/vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)。

## 问题（Question）

Visual/domain randomization 该随机化什么，怎样避免随机化到无关分布？高分回答不能只列 color jitter、texture 和 camera pose，还要说明 task relevance、label-preserving/equivariant、range evidence、validity filter、factor ablation 与 real gate。

## 1. 30 秒结论

我会把 visual DR 分成 geometry、appearance、sensor/time、scene/task 四组。每个 factor 先写它模拟哪种真实变化，再冻结 range 来源、采样时间尺度和 label contract：纯 appearance 可保持 target，camera/object geometry 要同步变 point/pose/action，颜色/左右等语言语义变化要同步改 prompt 或锁定。

范围不照搬论文：从 calibration、real capture、mount tolerance 和日志出发，小步扩展；用 physical/task validity、sample render 和 label round-trip 拒绝不可能或不可解样本。最后做 no-DR/分组/combined/overwide matched arms，在 nominal sim、randomized holdout、real replay、real closed-loop 上检查 robustness–optimality；ADR/SimOpt 也必须有硬边界与 rollback。

## 2. Randomization 训练目标

令 \(R_\psi\) 是按参数 \(\psi\) 渲染或扰动 observation，\(\psi\sim p_\phi\)，训练写为：

\[
\theta^*(\phi)=\arg\min_\theta
\mathbb E_{(x,y)\sim\mathcal D_{sim},\,\psi\sim p_\phi}
\left[\ell\left(f_\theta(R_\psi(x)),T_\psi(y)\right)\right].
\]

变量解释：\(p_\phi\) 是 randomization distribution；\(T_\psi\) 是 target/action 同步变换。实现映射：manifest 保存 factor、distribution、bounds/source、cadence/correlation、label transform、validity filter、seed 和 revision。只记录“用了 augmentation”无法复现该目标。

真正关心的是 real target risk：

\[
R_{real}(\phi)=
\mathbb E_{z\sim q_r}
\left[\ell_{task}(f_{\theta^*(\phi)}(z),y_z)\right].
\]

变量解释：\(q_r\) 是真实 deployment distribution。Randomized-sim score 只是 proxy；small real calibration/replay 可用于设计 range，matched real closed-loop 才能支持 transfer benefit。

## 3. 四组视觉随机化

### 3.1 Geometry

- camera extrinsics：mount position/orientation、vibration；
- intrinsics：focal length/FOV、principal point、distortion；
- object/robot pose、scale、camera count/view availability；
- crop/resize/flip 及其对应 geometry。

Geometry 影响 pixel→camera→robot mapping。任意 2D warp 不一定对应真实 camera；camera/object pose 变化通常需要 simulator 重渲染并同步 target，而不是对现有图片随手旋转。[1][6]

### 3.2 Appearance

- lighting direction/intensity/color、shadow；
- exposure、white balance、gamma、contrast；
- material、texture、background、reflection；
- object color/appearance，但要检查 language/task semantics。

Tobin et al. 随机化 camera、light、object pose、texture 与 distractor；OpenAI dexterous work还覆盖 intrinsics、materials 与多相机视觉。[1][2] 这些是候选项，不是通用默认范围。

### 3.3 Sensor/time

- readout noise、bias、dead pixel、depth hole；
- blur、compression、occlusion、dropout；
- exposure/readout delay、frame timestamp/jitter；
- multi-view/proprio/history alignment。

Noise 要匹配时间尺度：episode-correlated bias、step noise、drift 和 rare dropout 不能全用 i.i.d. Gaussian 表示。[2]

### 3.4 Scene/task

- clutter/distractor、object instance、layout、initial pose；
- camera availability、background objects；
- deployment 会出现的遮挡或动态物体。

这里最容易破坏任务：变了目标 identity、left/right、颜色或 object pose，prompt、success 和 expert action 可能都要同步。

## 4. 三类 label contract

### 4.1 Invariant / label-preserving

\[
T_\psi(y)=y.
\]

变量解释：transform 只改变 nuisance，不改变任务状态和 target。小范围 exposure、white balance、sensor noise可能属于此类，但前提是没有抹去必要视觉 cue，也没有改变语言语义。

### 4.2 Equivariant

\[
y'=\rho(g)y.
\]

变量解释：geometry transform \(g\) 改变 label coordinate，\(\rho(g)\) 同步变换 point/box/pose/action。例如 horizontal flip 后 pixel label 要 flip；camera-frame pose/action 要按新 extrinsics 重算；object pose改变需重生成 expert target。

### 4.3 Semantic-changing

如果指令是“抓红块”，把红块变蓝但 prompt 不改，训练目标已改变。三种安全选择：

1. 锁定 factor；
2. 同步改 prompt/label/success；
3. 作为独立 task-generalization 数据，不混进 label-preserving DR。

工程上每个 factor 必须标一个 `label_mode=invariant|equivariant|semantic`，缺失就不能进入正式数据生成。

## 5. Range 从哪里来

| 因子类型 | Range 来源 | 例子 | 不宜做法 |
| --- | --- | --- | --- |
| measured | nominal + calibration residual/quantile + margin | K/R/t、exposure、latency、noise | 复制论文 ±x% |
| manufacturing/operation tolerance | spec、mount tolerance、deployment inventory | camera vibration、illumination envelope | 没有单位/frame |
| uncertain but plausible | bounded prior + separate stress bucket | clutter、object pose、partial occlusion | 无限制扩宽 |
| semantic locked | fixed 或同步 target | target color/identity、left/right | 保留旧 prompt/label |
| rare/safety | event/stress eval | camera loss、full occlusion、packet drop | 大量混入 nominal training |

OpenAI dexterous work围绕 calibration center 随机物理参数；Tan et al. 对测得更准的参数用较保守范围，对 inertia、wear、control step/latency 等不确定项扩大覆盖，并明确 robustness–optimality trade-off。[2][3]

一个实用范围模型是：

\[
\psi=\hat\psi_{calib}+\delta_{residual}+\delta_{drift},
\]

其中 \(\hat\psi_{calib}\) 是 nominal calibration，\(\delta_{residual}\) 来自标定/测量残差，\(\delta_{drift}\) 来自部署时间、温度、wear 或 mount variation。变量解释：三项需分开版本化；它不是假设所有分布都 Gaussian。

## 6. 为什么越宽不一定越好

SimOpt 明确指出 overly wide simulation distributions 可能包含 infeasible scenarios、阻碍 policy learning 或产生 excessively conservative policy；Tan et al. 也指出随机化在 robustness 与 optimality 之间取舍。[3][4]

常见污染：

- camera 在真实机械结构不可能到达的位置；
- FOV/畸变超出传感器范围；
- 光照/occlusion 使必要信息完全不可见；
- 改 target color/identity 却不改 instruction；
- object pose 物理穿透或任务无解；
- sensor dropout 比真实系统高几个数量级；
- 不同 view/time 独立随机，破坏多视角几何与时序一致性。

概念上的 contamination：

\[
C(\phi)=\Pr_{\psi\sim p_\phi}
\left[\psi\notin\Omega_{valid}\lor T_\psi\text{ 不一致}\right].
\]

变量解释：\(\Omega_{valid}\) 是硬件可实现、任务可解、语义一致的参数集。实现用 hard constraints、sample renders、label round-trip、solvability check 和 rejection ledger 近似审计，不声称能精确计算。

## 7. Relevant-support Gate

### Gate 1：Target inventory

从真实部署列 camera、lighting、surface、object、layout、sensor failure 与时间变化，不从 augmentation library 反向挑参数。

### Gate 2：Factor hypothesis

每个 factor 写：模拟的真实变化、预期 failure、作用层、数据来源、是否与 task cue 冲突。

### Gate 3：Label semantics

声明 invariant/equivariant/semantic-changing，并对 point/box/pose/action/prompt 做 round-trip test。

### Gate 4：Validity

检查 camera pose/FOV、object placement、illumination、occlusion、multi-view/time consistency 和 task solvability。

### Gate 5：Range evidence

绑定 calibration/capture/spec/log；没有证据标 `unverified prior`，不能写“覆盖真实分布”。

### Gate 6：Boundary sample audit

保存 nominal、lower/upper boundary、random draw、rejected sample、reason、seed 与 revision。

### Gate 7：Matched ablation

固定 data count、train compute、checkpoint init、seed/task/controller，仅替换 factor group。

### Gate 8：Real gate + rollback

Real replay/closed-loop 不提升，或 nominal/关键 strata 回退时，停止扩宽并回滚 distribution revision。

## 8. Fixed DR、ADR 与 SimOpt

### 8.1 Fixed/UDR

人工设定分布并保持固定。优点是简单可复现；风险是 factor/range/source靠经验，容易 coverage 不足或污染。

### 8.2 ADR

Rubik's Cube work 将每维参数采自 uniform bounds，从初始窄分布出发，在 boundary evaluation 超过/低于 performance thresholds 时扩展/收缩。[5] 它是 curriculum：

\[
p_\phi(\psi)=\prod_{i=1}^{d}U(\phi_i^L,\phi_i^H).
\]

变量解释：\(\phi_i^L,\phi_i^H\) 是第 i 维 bounds。Boundary performance 说明 policy 是否能处理该边界，不说明该边界在 real world 的概率；仍要有 hard bounds、semantic validity、dimension dependency 和 real replay。

### 8.3 SimOpt

用少量 real trajectory 与 simulated behavior discrepancy 更新 distribution。[4] 它可减少盲目过宽，但需要 safe real rollout、discrepancy metric 与 distribution regularization；不等于 exact system ID，也不能无约束采集 real data。

## 9. Matched factor ablation

最小 arms：no DR、appearance、geometry、sensor/time、scene/task-relevant、relevant combined、overwide stress。

固定：dataset states/episodes、render count、train steps/effective batch、checkpoint init、optimizer、task/init、controller、seed plan。报告：

| Stratum | 指标 | 解释边界 |
| --- | --- | --- |
| nominal sim | task metric/loss | nominal optimality；不是 transfer |
| randomized in-support | per-factor metric | learned robustness；不是 real coverage |
| held-out composition | unseen factor combination | compositional generalization |
| real replay | feature/point/box/action stability + failure strata | observation support proxy |
| real closed-loop | success + CI、first failure、安全事件 | transfer evidence；需完整 protocol |

还要记录 factor draw/rejection count、distribution revision、sample render、data generation cost。Combined arm 变好不能证明每个 factor 有用，必须看 single-factor/leave-one-out。

## 10. 可审计 pipeline

```python
def build_randomized_sample(task, manifest, rng):
    # 1. Draw only factors registered for this deployment/task.
    params = manifest.sample(rng)

    # 2. Reject impossible, unsolvable or semantically inconsistent domains.
    ok, reason = validate_domain(params, task)
    if not ok:
        log_rejection(params, reason, manifest.revision)
        return None

    # 3. Render and transform labels/actions/prompts according to the label contract.
    obs = render(task.state, params)
    target = transform_target(task.target, params.label_transform)
    assert label_roundtrip(obs, target, params)

    # 4. Persist exact draw/source/seed so matched ablations are replayable.
    log_draw(params, rng.seed, manifest.revision)
    return obs, target
```

Randomization manifest 最少字段：`factor_name, group, unit/frame, distribution, lower/upper, center, range_source, cadence, correlation, label_mode/transform, validity_rule, task_scope, seed, revision`。

## 11. 失败症状与诊断

| 症状 | 先查 | 对照 |
| --- | --- | --- |
| randomized sim 更强，nominal 大幅掉点 | range/ratio 过宽、capacity/compute不够 | narrow/medium/wide + fixed sample count |
| real replay 无改善 | target factor 未覆盖、preprocess/calibration根因 | factor sensitivity + real capture strata |
| pixel metric 好，action 变差 | geometry/label transform 错 | point/pose/action round-trip |
| 特定颜色/对象失败 | semantic-changing DR 或 prompt冲突 | lock/sync color/identity ablation |
| 多视角模型变差 | 各 view 独立随机破坏共同几何/time | shared camera rig/time draw |
| ADR bounds 持续扩张但 real 不升 | boundary threshold与target misaligned | hard cap + real replay + rollback |
| combined 变好但不知原因 | factor confounding | single-group / leave-one-out |

## 12. 项目与真实性边界

当前证据仓库没有可闭合的 visual-DR bundle：randomization manifest、range/source、sample render/rejection、label transform tests、matched factor arms、real calibration/replay、real closed-loop 与 ownership 未同时存在。[7]

安全说法：**“我能设计 relevant-support、label/semantic 与 matched ablation 合同；项目现有 image augmentation、camera/preprocess 或 simulator variation 不能直接证明做了 domain randomization 或提升 Sim2Real。”**

不能说：**“我给图像加了增强，所以项目已完成 visual DR”“用了论文同款 range，所以覆盖真实分布。”**

ProjectProof 证据等级：当前 C0“机制理解/方案设计”；C1 要个人 config/code/render bundle，C2 要 matched ablation 与 real replay，C3 transfer 数字要 protocol-complete real closed-loop。

## 13. 一句话收束与下一入口

**Visual DR 的核心不是“加多少噪声”，而是每个 factor 都有真实变化假设、range 来源、label/semantic contract、validity gate、factorized ablation 和 real rollback；否则增加的是 distribution contamination，不是 transfer robustness。**

下一节点是 `VLA-WM-033`：dynamics randomization 与 system identification 如何互补，参数范围怎样确定。本节点保持 WARN，题卡在真实口述前保持 unseen。

## 参考文献（References）

1. Tobin et al., [Domain Randomization](https://arxiv.org/abs/1703.06907v1), 2017。
2. OpenAI et al., [Learning Dexterous In-Hand Manipulation](https://arxiv.org/abs/1808.00177v5), 2019。
3. Tan et al., [Sim-to-Real Agile Locomotion](https://arxiv.org/abs/1804.10332v2), 2018。
4. Chebotar et al., [SimOpt](https://arxiv.org/abs/1810.05687v4), 2019。
5. OpenAI et al., [Solving Rubik's Cube with a Robot Hand](https://arxiv.org/abs/1910.07113v1), 2019。
6. [OpenCV calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)。
7. [VLA Project Evidence Manifest](../evidence/evidence_manifest.html)。
