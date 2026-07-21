# VOL 04 World Model / Sim2Real：Camera Geometry 与 Sensor Modeling（WM-035）

> 状态：drafted / VLA-WM-035 / knowledge_37_of_44 / card_synced / WARN  
> 更新日期：2026-07-18  
> 核心问题：camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模？  
> 前置：[WM-032 Visual DR](vol_04_world_model_sim2real_wm032_visual_domain_randomization_relevance.html)、[WM-034 Timing / Controller](vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)、[WM-035 Source Freeze](../sources/vol_04_wm035_camera_sensor_modeling_source_freeze.html)。

## 1. 面试结论

camera/sensor modeling 分五层：

1. geometry：K、R/t、distortion、resolution/crop；
2. photometric：light、exposure、gain、WB、gamma、material/compression；
3. temporal：exposure/readout、blur、timestamp、drop/sync；
4. visibility：FOV、occlusion、visible fraction、task solvability；
5. sensor：shot/read/bias/fixed-pattern/quantization/depth invalid。

每层都要有 real range source、correlation/cadence、label transform、validity/rejection 和 matched evaluation。color jitter 只覆盖很小一部分。

## 2. Geometry：像素从哪里来

\[
s\begin{bmatrix}u\\v\\1\end{bmatrix}
=K[R\mid t]P_w,
\qquad
K=\begin{bmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{bmatrix}.
\]

变量解释：\([R|t]\) 是 world→camera extrinsics，\(K\) 是 intrinsics，\((u,v)\) 是 pixel。实现映射：绑定 camera serial/name、optical frame、image size、K/distortion/extrinsics revision、calibration time 与 reprojection diagnostics。[1]

distortion 写为：

\[
(x_d,y_d)=D(x_n,y_n;k_i,p_i,\ldots),
\]

其中 \(k_i\) 是 radial、\(p_i\) 是 tangential coefficients。OpenCV 还支持更高阶模型，并提示非单调 radial estimate 可视为 calibration failure。[1]

## 3. Raw、rectified、resized、cropped 不能混

pixel label 必须说明在哪个 image space。resize 后：

\[
f_x'=s_xf_x,\;c_x'=s_xc_x,
\qquad
f_y'=s_yf_y,\;c_y'=s_yc_y,
\]

crop 还要减 offset。实现映射：保存 raw size、rectification map、crop box、resize mode、padding、flip、output size 与 preprocess hash；用 raw K 投影到 cropped tensor 会产生系统偏差。

## 4. Intrinsics/extrinsics 怎样给 range

| factor | center | range |
| --- | --- | --- |
| K/distortion | per-serial calibration | repeated calibration、focus/temperature、residual |
| static extrinsics | hand-eye/rig/CAD | repeated mount、assembly tolerance |
| wrist extrinsics | robot pose + hand-eye | load/vibration/flex/timestamp |
| multi-camera rig | joint calibration | rig-global + per-camera correlated residual |
| image/crop | runtime pipeline | allowed preprocess revisions |

MuJoCo 支持 FOV、focal、principal point 以及 sensor size/resolution；默认 point camera 仍不等于真实 lens/ISP。[2]

## 5. Photometric chain

\[
y=Q\left(\Gamma\left(g\cdot
\frac{1}{T_e}\int_{t_0}^{t_0+T_e}E(x(t),t)dt+b+n_{read}\right)\right).
\]

变量解释：\(T_e\) 是 exposure，\(g\) 是 gain，\(b\) 是 bias，\(\Gamma\) 是 response/WB/gamma/color pipeline，\(Q\) 是 quantization/compression。实现映射：从真实 lighting/exposure/gain/WB survey 建条件分布，不把 brightness jitter 当完整 camera model。

若 instruction 使用颜色/材质，photometric transform 可能改变语义，必须锁定或同步 prompt/label。

## 6. Blur 是时间模型

\[
I_{blur}(x)\approx(k_{motion}*I_{sharp})(x).
\]

该卷积只是一种 proxy。真实 blur 来自 exposure interval 内 camera/object motion，依赖 depth、rotation、velocity、shutter/readout。实现映射：保存 exposure start/end、global/rolling shutter、readout direction/time、frame timestamp、camera/object velocity、multi-view sync。

只在动态运动失败而静态图正常时，应优先检查 exposure/blur/timestamp，而不是扩大 texture randomization。

## 7. Sensor noise 分层

\[
Y\sim\operatorname{Poisson}(g\lambda)+\mathcal N(b,\sigma_{read}^2).
\]

变量解释：\(\lambda\) 是 signal level proxy，第一项表示 signal-dependent shot noise，第二项表示 read noise/bias。实现映射：dark/flat-field、不同 exposure/gain 重复 capture；再补 fixed-pattern、hot pixel、banding、quantization、compression、auto-exposure drift、frame dropout 和 depth holes。

OpenAI Dexterous 区分 episode-correlated 与 timestep-uncorrelated noise，因此 noise cadence 不能省略。[3]

## 8. Occlusion 是 visibility 事件

\[
r_{vis}=\frac{|M_t\cap M_v|}{|M_t|+\epsilon}.
\]

变量解释：\(M_t\) 是完整 target mask，\(M_v\) 是 visible mask。实现映射：保存 occluder ID/depth、visible fraction、持续时间、每相机 visibility、task solvability。

区分 self/object/environment occlusion、sensor obstruction 和 full camera failure。后两者可能需要 stress/fallback，不应混入普通 nominal augmentation。

## 9. Multi-camera correlation

三路 camera 不是三张独立随机图：

- 同一 world state、object pose 与 task label；
- rig-global pose 与 per-camera residual 分开；
- lighting/material 在视角间相关；
- exposure/WB 可按 hardware 是否联动建相关；
- occlusion 按真实 depth/order 生成；
- capture timestamp/trigger/clock offset 可追溯；
- camera identity、presence/valid mask 不可丢失。

OpenAI Dexterous 同时输入三路 camera 并随机 positions/intrinsics/lighting/material，支持“多视角视觉因素需进合同”，不支持独立乱采到不可能 rig。[3]

## 10. Range 与 cadence

| factor | source | cadence |
| --- | --- | --- |
| K/distortion | calibration posterior/residual | camera/session |
| extrinsics | hand-eye/rig/mount/vibration | build/episode/time |
| exposure/gain/WB | capture/light survey | frame/segment |
| blur | exposure × motion distribution | frame/segment |
| occlusion | task/event/visibility logs | event/segment |
| noise/dropout | dark/flat-field/signal/network logs | frame/session/event |

ImageNet-C 的 noise/blur/weather/digital 与 severity 可作 stress taxonomy，但不是 target camera distribution。[4]

## 11. Label consistency

| transform | 同步动作 |
| --- | --- |
| camera pose/FOV/distortion | 从 world state 重投影 point/box/depth/pose |
| crop/resize/pad | 更新 K、pixel label、ROI/mask |
| flip/warp | 验证物理/语义，并更新 label/pose/action frame |
| exposure/noise/compression | 通常 label invariant，但保留 cue gate |
| occlusion | 保存 full/visible target；不可解样本分流 |
| frame drop/time shift | 同步 history/proprio/action timestamp/valid mask |

Tobin/OpenAI 的 simulator randomization从一致 world state render；对现成 image 做 2D augmentation 时，工程方必须自己保证 target equivariance。[3][5]

## 12. Validity 与 rejection

拒绝或分流：

- FOV 不见 workspace、camera 穿模；
- distortion 非法/ROI 大面积无效；
- exposure/blur/noise 抹去必要 cue；
- occlusion 使任务不可解；
- multi-camera rig/time 不一致；
- crop/flip 后 K/label 未更新；
- dtype/range/color order/preprocess 不符；
- combined arm nominal 下降且 real gate 无收益。

保存 nominal/low/high/random/rejected render、seed、factor、target overlay 与 rejection reason。

## 13. Diagnostic ladder

1. camera identity、RGB/BGR、orientation、preprocess hash；
2. K/distortion/image size、extrinsics direction、projection round-trip；
3. static exposure/gain/WB/gamma/saturation；
4. blur/readout/timestamp/drop/sync；
5. occlusion/visible fraction/solvability；
6. signal-dependent noise/bias/compression/depth invalid；
7. real replay strata 的 feature/action drift；
8. fixed-protocol closed-loop first failure/success/CI。

固定方向偏差查 geometry；只在运动中错查 temporal；只在某亮度错查 photometric；随机闪烁查 dropout/auto-exposure/network。

## 14. Matched camera ablation

固定 data states、render count、train steps、init、seed、model、task、controller 和 rollout protocol：

| arm | 内容 |
| --- | --- |
| nominal | calibrated center |
| geometry | K/R/t/distortion |
| photometric | light/exposure/WB/gamma/material |
| temporal | exposure/blur/readout/drop |
| occlusion | visibility/solvability/multi-view |
| sensor | shot/read/bias/compression/depth invalid |
| combined | calibrated groups |
| overwide | irrelevant/unsolvable stress |

分别报告 sim、factor holdout、real replay、closed-loop；通用 corruption score与目标 camera score分开。

## 15. 实现伪代码

```python
def calibrated_camera_sample(world_state, rig, contract, seed):
    # 1. Sample calibration-centered geometry while preserving rig correlations.
    geometry = sample_camera_geometry(rig.calibration, contract.geometry, seed)

    # 2. Re-render from the same world state so spatial targets stay consistent.
    rgb, targets = render_rgb_and_geometry_targets(world_state, geometry)

    # 3. Apply measured photometric, exposure/blur and signal-dependent sensor models.
    rgb = apply_photometric(rgb, contract.photometric)
    rgb = apply_exposure_blur(rgb, world_state.motion, contract.temporal)
    rgb = apply_sensor_model(rgb, contract.sensor)

    # 4. Add task-valid occlusion and save full/visible masks.
    rgb, visibility = apply_occlusion(rgb, world_state, contract.occlusion)

    # 5. Preprocess and synchronize K, pixel labels, masks and timestamps.
    image, targets = preprocess_with_targets(rgb, targets, visibility, contract.preprocess)

    # 6. Reject impossible, unsolvable or label-inconsistent samples and log them.
    return validate_log_sample(image, targets, geometry, contract, seed)
```

## 16. 项目挂钩与真实性边界

当前 [Evidence Manifest](../evidence/evidence_manifest.html)、OPD/OpenPiVLA inventories 与 PER-002 支持静态 grounding、camera/preprocess/rollout 字段和 projection/calibration 知识，但缺真实 rig/calibration/capture survey、factor sampler、label/rejection ledger、matched camera arms、real replay/closed-loop 和 ownership。

面试安全回答：

> 我会先绑定 camera serial、K/distortion、world→camera extrinsics、image space 和 preprocess revision；再从重复 calibration、lighting/exposure/gain、motion、visibility 和 noise capture 建 geometry、photometric、temporal、occlusion、sensor 五层分布。几何变化同步 K/label/pose，occlusion 做 visible-fraction/solvability gate，最后做单组/combined/overwide 与 real replay/闭环对照。当前项目没有这套真实 camera bundle，所以不声称已提升真机成功率。

不能说：

- “color jitter 覆盖了 camera gap”；
- “有 K 字段就完成标定”；
- “Gaussian noise 能模拟所有 sensor noise”；
- “random erasing 就是物理 occlusion”；
- “ImageNet-C 更好就证明 VLA 闭环更稳”；
- “当前项目已完成 camera DR/real transfer”。

## 17. 实战审计清单

- [ ] camera serial/name/frame/image-space/preprocess revision 完整；
- [ ] K/distortion/extrinsics/calibration residual 可追溯；
- [ ] crop/resize/flip 后 K/label round-trip；
- [ ] exposure/gain/WB/gamma/lighting capture survey；
- [ ] blur/readout/timestamp/drop/multi-view sync；
- [ ] signal-dependent noise/bias/pattern/compression/depth invalid；
- [ ] occluder/visible fraction/duration/solvability；
- [ ] sampler seed/accepted/rejected/overlay ledger；
- [ ] factor/combined/overwide matched arms；
- [ ] real replay/closed-loop/ownership 与 C0–C3 对齐。

## 18. 参考来源

1. OpenCV, [calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)。
2. MuJoCo, [Camera intrinsics](https://mujoco.readthedocs.io/en/stable/modeling.html#cameras)。
3. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
4. Hendrycks & Dietterich, [*Common Corruptions and Perturbations*](https://arxiv.org/abs/1903.12261v1)。
5. Tobin et al., [*Domain Randomization*](https://arxiv.org/abs/1703.06907v1)。
6. [WM-035 Source Freeze](../sources/vol_04_wm035_camera_sensor_modeling_source_freeze.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 19. 下一节点

下一节点是 `VLA-WM-036`：friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点。本节点保持 WARN，题卡在真实口述前保持 unseen。
