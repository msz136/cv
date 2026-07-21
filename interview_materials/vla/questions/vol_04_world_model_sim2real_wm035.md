# VOL 04 VLA-WM-035 原子题卡：Camera Geometry 与 Sensor Modeling

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-035  
> 难度：L2 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-035 Knowledge](../knowledge/vol_04_world_model_sim2real_wm035_camera_sensor_modeling.html)；来源边界见 [WM-035 Source Freeze](../sources/vol_04_wm035_camera_sensor_modeling_source_freeze.html)。

## camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-WM-035</b> · camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模？</summary>

**面试意图**：判断你能否把“color jitter + Gaussian noise”升级为 calibration-centered geometry、physical/temporal image formation、visibility/solvability、signal-dependent sensor 与 label-consistent matched evaluation。

**30 秒回答**：先分几何、成像、时间、遮挡、噪声五层。K/R/t/distortion来自标定与挂载残差；exposure/WB/gamma、blur、shot/read noise来自重复实拍和时间戳；occlusion按可见率与可解性建模。几何变化同步K/label/pose，做单组、combined、overwide与real replay/闭环对照。

**机制展开（约 2 分钟）**：绑定camera serial、image space、K/distortion与world→camera外参。range来自repeated calibration、mount tolerance、曝光/增益survey、运动、dark/flat-field与drop log；多相机保留rig/time correlation。改camera时重投影label，crop/resize更新K，occlusion保存visible mask并拒绝不可解样本。固定data/compute/init/protocol比较五组、combined、overwide；ImageNet-C仅作stress taxonomy。当前无camera bundle，不声称transfer。

**诊断 / 证据**：先核 camera identity、RGB/BGR、raw/rectified/cropped space 与 preprocess hash；再做 K/distortion/image-size、外参方向、world→pixel→model-pixel round-trip。按 static exposure/gain/WB、dynamic blur/readout/timestamp、visible fraction/occluder、signal-dependent noise/bias/compression/depth invalid 分层保存 real capture。记录 sampler seed、factor、accepted/rejected、overlay；分 sim/holdout/real replay/closed-loop 报 feature/action drift、success/CI 与 first failure。

**项目挂钩**：OPD 支持静态 grounding/eval，OpenPiVLA/WAM 支持 camera/preprocess/rollout provenance，PER-002 支持 projection/calibration 合同；但缺真实 rig/calibration/capture survey、factor sampler、label/rejection ledger、matched camera arms、real closed-loop 和 ownership。安全说“能设计五层 camera audit”，不能把 camera 字段、静态 box/point 指标或普通 augmentation 写成个人 camera Sim2Real 成果。

**追问树**：K/R/t 分别是什么？world→camera 方向为什么易错？resize/crop 后 K 怎么变？distorted 与 rectified pixel 能混吗？exposure 与 brightness jitter 差别？motion blur 为什么与时间/深度有关？shot/read/fixed-pattern noise 怎样区分？为什么 i.i.d. Gaussian 不够？occlusion 如何定义可见率和可解性？多相机能独立随机吗？ImageNet-C 能证明什么？怎样做 matched camera ablation？

**易错点**：所有 camera 共用 K；外参方向反；raw K 用于 cropped tensor；color jitter 代替 exposure/ISP；Gaussian blur 代替动态 blur；所有 noise i.i.d.；random erasing 代替物理 occlusion；full blackout 混进 nominal；多相机独立乱采；几何变化不改 label/K；只看 corruption score；把 camera config 当 transfer 结果。

**危险答案**：说“做 color jitter/blur/noise 就覆盖 camera gap”“有 K 字段就说明标定正确”“Gaussian noise 足够模拟真实 sensor”“ImageNet-C 鲁棒就等于 VLA 闭环鲁棒”“当前项目已通过 camera randomization 提升真机成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-035 Source Freeze](../sources/vol_04_wm035_camera_sensor_modeling_source_freeze.html)：geometry/photometric/temporal/visibility/sensor、label/range/matched gates 与项目边界。
2. OpenCV, [calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)；MuJoCo [Camera intrinsics](https://mujoco.readthedocs.io/en/stable/modeling.html#cameras)。
3. Tobin et al., [*Domain Randomization*](https://arxiv.org/abs/1703.06907v1)。
4. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
5. Hendrycks & Dietterich, [*Common Corruptions*](https://arxiv.org/abs/1903.12261v1)；[Evidence Manifest](../evidence/evidence_manifest.html)。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-036`，不批量生成 WM-036..038，不创建 `coaching_state.md`。

