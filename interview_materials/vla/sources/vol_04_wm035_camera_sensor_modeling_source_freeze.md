# VOL 04 WM-035 Source Freeze：Camera Geometry、Photometric、Occlusion 与 Sensor Modeling

> 冻结日期：2026-07-18  
> 状态：source_frozen / VLA-WM-035 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-035  
> 本轮边界：只冻结 camera intrinsics/extrinsics/distortion、exposure/response/blur、occlusion/visibility、sensor noise/dropout、range provenance、label/time consistency、matched evaluation 与项目真实性边界；不提前展开 WM-036 contact/friction、WM-037 online adaptation 或 WM-038 safety/recovery 总课，也不声称个人项目已完成真实相机标定、camera randomization 或视觉 Sim2Real。

## 1. 一页结论

1. **camera gap 至少分五层。**geometry（\(K,R,t\)、distortion、resolution/crop）、photometric（light/exposure/gain/WB/gamma/response）、temporal（exposure/readout/timestamp/blur/drop）、visibility（occlusion/FOV）、sensor（shot/read/fixed-pattern/quantization/compression/depth holes）。只做 color jitter 覆盖不了其他四层。
2. **geometry 先标定，再随机残差。**OpenCV 明确世界点经 world→camera extrinsics、intrinsics 与 distortion 投影；range 应来自 camera serial 对应的 calibration、reprojection residual、mount tolerance、vibration/thermal drift，而不是统一 ±x%。[S1]
3. **sim camera 必须和 calibration contract 同参。**MuJoCo 支持 FOV，以及 focal/principal point 配合 physical sensor size 和 resolution；默认 perfect point camera 不包含真实 lens 全部 aberration。[S5]
4. **exposure/blur 是时间积分，不只是单帧 filter。**shutter/exposure 决定采光时间，camera/object motion 在此期间形成 motion blur；rolling/readout 与 timestamp 又会让不同行或不同相机看到不同时间。静态 Gaussian blur 只能是 proxy。
5. **sensor noise 通常 signal-dependent 且有时间/空间结构。**shot/read/fixed-pattern/bias/quantization/compression/dropout 不应统一成 i.i.d. Gaussian；OpenAI Dexterous 至少区分 episode-correlated 与 timestep-uncorrelated observation noise，说明 cadence 是合同的一部分。[S3]
6. **occlusion 是可见性/任务事件。**要记录 occluder 来源、深度顺序、target visible fraction、持续时间、多相机相关性和任务可解性；full occlusion/camera failure 应与 nominal training 分开，进入 stress/safety gate。
7. **几何变化必须同步 target。**重新渲染 camera pose/FOV 时，pixel point/box/depth/pose 应由同一 world state 生成；对现成图像做 crop/flip/warp 时同步更新空间 label，必要时更新 camera-frame pose/action。只改像素会制造冲突监督。[S2][S6]
8. **corruption benchmark 不等于 target sensor model。**ImageNet-C 将 corruption 分为 noise、blur、weather、digital 并设 severity，可用于 stress taxonomy；它是 image-classification benchmark，不证明某机器人相机的概率、range 或闭环相关性。[S4]
9. **本地项目没有 camera Sim2Real 闭环。**OPD 有静态 grounding/eval，OpenPiVLA/WAM 有 camera/preprocess/rollout 字段，但缺 calibration/capture/corruption/label/matched real bundle；只能讲设计和证据门。[S9]

## 2. 冻结来源与可支持边界

| ID | 一手来源 / 本地证据 | 冻结版本与快照 | 本节点可支持 | 不能外推 |
| --- | --- | --- | --- | --- |
| S1 | OpenCV camera calibration / calib3d | official GitHub commit `f7dd7df170add1655de75b5e95f20f41d2a88293` raw SHA-256 `72f48a264d331a7d81dcd9463b98f096871cb140105f96f08abdf954d84203c4`；4.x calib3d response SHA-256 `564e922f60635d1be9d8da36e60f42eb1dc1d53f884e0fe447d54ba08648b50b` | pinhole \(K[R|t]\)、radial/tangential/prism distortion、reprojection optimization/diagnostics | API 文档证明用户相机标定正确；低 reprojection error 自动证明外参/部署正确 |
| S2 | Tobin et al., *Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World* | arXiv:1703.06907v1；ar5iv response SHA-256 `faba518e98357c65a59d41f340bb723d4bb84c50eb359813597daab113dcd33a` | camera position、lighting、object pose、texture、distractor/partial occlusion 与 ablation 的 real detection/grasping case | 论文 randomization range 是所有 VLA 默认；object detector transfer 等于用户 policy transfer |
| S3 | OpenAI et al., *Learning Dexterous In-Hand Manipulation* | arXiv:1808.00177v5；ar5iv response SHA-256 `826fb63d545518661a10b9cac05110bf7c813e88f99698d3b9e98cb313f81e93` | multi-camera、camera positions/intrinsics、lighting/material/texture、correlated/uncorrelated noise 与 calibration-centered randomization | Shadow Hand visual recipe 普适；大规模 randomization 自动证明安全或用户成果 |
| S4 | Hendrycks & Dietterich, *Benchmarking Neural Network Robustness to Common Corruptions and Perturbations* | arXiv:1903.12261v1；ar5iv response SHA-256 `d3c445b259eb3af5381f0bba396d902bc28923fb8f743ce95107df734e33381f` | noise/blur/weather/digital corruption taxonomy、five severity levels、classification robustness benchmark | ImageNet-C severity 是真实 camera range；classification robustness 等于 closed-loop VLA robustness |
| S5 | MuJoCo official *Modeling / Camera intrinsics* docs | `stable` 页面，2026-07-18 response SHA-256 `505230785371f9e6e54575b5178950ffbce4b5b2fa9db7a0a393f91adc1315da` | perspective/orthographic、FOV、focal、principal、sensor size/resolution 与 body-fixed camera | mutable stable 页等于固定 simulator version；renderer 自动包含真实 distortion/noise |
| S6 | [WM-032 Visual DR / Relevant Support](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html) | canonical SHA-256 `9086b6072047f3578cb731f48f08c48b509d7d38924b801728039b83d6245710` | factor/label/range/validity/rejection/overwide contract | WM-032 设计等于 camera factor 已本地执行 |
| S7 | [WM-034 Timing / Controller Source Freeze](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html) | canonical SHA-256 `106fe97d60e78505ae71e7a8667499a615d71b2e1f0099c1da474713ecf940f8` | exposure/readout/timestamp 与 action-age 边界 | camera temporal contract 已有真实 trace |
| S8 | [PER-002 3D Lift / Calibration Source Freeze](vol_06_per002_3d_lift_frame_source_freeze.html) | canonical SHA-256 `a91a32eca547738c0cc76895f299dfae49ea134fd54944dc9eb538fba1228b93` | K/distortion/image-size、depth、extrinsics/TF、round-trip 与 3D evidence ladder | projection math 是 camera Sim2Real/closed-loop 结果 |
| S9 | [Evidence Manifest](../evidence/evidence_manifest.html)、OPD/OpenPiVLA inventories | manifest SHA-256 `f3826289cdf2451758da11e0dddab3a7bb43d88b9a656fa340c08f71d16a21b6`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293` | 本地静态视觉、camera/preprocess 与 rollout 证据边界 | camera 字段/静态指标可升级为 calibration、DR 或 real transfer 成果 |

## 3. Geometry contract：\(K,R,t\)、distortion 与 image space

对 world point \(P_w=[X_w,Y_w,Z_w,1]^T\)，理想 pinhole projection 为：

\[
s\begin{bmatrix}u\\v\\1\end{bmatrix}
=K[R\mid t]P_w,
\qquad
K=\begin{bmatrix}
f_x&0&c_x\\
0&f_y&c_y\\
0&0&1
\end{bmatrix}.
\]

变量解释：\([R|t]\) 是 world→camera change of basis，\(f_x,f_y,c_x,c_y\) 是 intrinsics，\((u,v)\) 是 pixel。实现映射：manifest 必须保存 camera serial/name、optical frame、image size、K/distortion/extrinsics revision、calibration timestamp 与 reprojection diagnostics。[S1]

distortion 可抽象为：

\[
(x_d,y_d)=D(x_n,y_n;k_1,k_2,k_3,\ldots,p_1,p_2,\ldots),
\]

其中 \((x_n,y_n)=(X_c/Z_c,Y_c/Z_c)\)，\(k_i\) 是 radial coefficients，\(p_i\) 是 tangential coefficients。OpenCV 还支持 higher-order/prism 等项，并提醒非单调 radial result 可视为 calibration failure。[S1]

必须说明 pixel 属于 raw distorted、rectified、resized 还是 cropped space。若 image 被 resize：

\[
f_x'=s_xf_x,\;c_x'=s_xc_x,\qquad
f_y'=s_yf_y,\;c_y'=s_yc_y,
\]

crop 还要减去 offset。实现映射：不要拿 raw K 直接投影到 cropped/resized tensor。

## 4. Intrinsics/extrinsics range 从哪里来

| 因素 | nominal 来源 | residual/range 来源 | 常见错误 |
| --- | --- | --- | --- |
| intrinsics/distortion | per-serial calibration | repeated calibration、reprojection residual、focus/temperature | 所有 camera 共用 K |
| static extrinsics | hand-eye/rig calibration、CAD/mount | repeated mount、calibration residual、assembly tolerance | 把 world→camera 与 camera→world 反了 |
| wrist-camera extrinsics | robot pose + hand-eye | joint/load-dependent flex、vibration、timestamp | 固定彩色噪声代替几何偏移 |
| image size/crop | runtime preprocess manifest | pipeline variants | resize 后不更新 K/label |
| multi-camera rig | joint calibration/shared frame | correlated mount/clock residual | 每个 view 独立随机到不可能 rig |

随机化应围绕 calibrated center，并保存 correlation。rig 整体平移/旋转与单相机 mount flex 是两种不同 factor；多相机必须共享 world state、timestamp 和 label generation。

## 5. Photometric image-formation contract

一个简化的 pixel formation 可写为：

\[
y=Q\left(\Gamma\left(g\cdot
\frac{1}{T_e}\int_{t_0}^{t_0+T_e}E(x(t),t)\,dt+b+n_{read}\right)\right),
\]

变量解释：\(E\) 是到达 sensor 的 irradiance/radiance proxy，\(T_e\) 是 exposure time，\(g\) 是 analog/digital gain，\(b\) 是 bias/black level，\(\Gamma\) 是 camera response/gamma/white-balance/color pipeline，\(Q\) 是 quantization/compression。该式是审计抽象，不代表某品牌 ISP 的完整实现。

因此 appearance 因素至少分：

- illumination direction/intensity/color temperature、shadow、reflection；
- aperture/exposure/gain/auto-exposure state；
- white balance、color correction、gamma/tone map；
- material/texture/background；
- quantization、JPEG/video compression、color format；
- saturation/clipping、black level 与 dynamic range。

若语言包含 color/material，改变颜色必须同步语义或锁定 task cue，不能把所有 photometric transform 当 label-preserving。[S6]

## 6. Blur 与 temporal camera model

motion blur 是 exposure interval 内 camera/object motion 的积分。静态 convolution proxy：

\[
I_{blur}(x)\approx(k_{motion}*I_{sharp})(x),
\]

只能近似 constant-depth/constant-motion 场景；真实 blur 与 depth、rotation、object motion、exposure 和 rolling/readout 相关。

camera temporal manifest 应记录：

- exposure start/end 与 frame timestamp 定义；
- global/rolling shutter、readout direction/duration；
- sensor/transport/preprocess latency；
- frame rate、jitter、duplicate/drop；
- multi-camera sync/trigger/clock offset；
- 与 proprio/action 的 observation age。

完整 timing/action-age 诊断见 WM-034；本节点只规定 camera 侧字段。[S7]

## 7. Sensor noise 不是单一 Gaussian

一个常用审计近似是 signal-dependent shot noise 加 read noise：

\[
Y\sim\operatorname{Poisson}(g\lambda)+\mathcal N(b,\sigma_{read}^2),
\]

其中 \(\lambda\) 是 expected photon/electron count proxy，\(g\) 是 gain，\(b\) 是 bias。实现时还可能有 fixed-pattern/hot pixel、dark current、row/column banding、quantization、compression、auto-exposure feedback 和 temporal denoising；不能从这个式子推出真实 camera 的全部 noise model。

cadence 分层：

| noise | cadence | 测量方式 |
| --- | --- | --- |
| per-pixel/read/shot | frame-level、signal-dependent | dark/flat-field、不同曝光/增益重复 capture |
| bias/fixed pattern | camera/session-level | static scene + per-pixel statistics |
| auto-exposure/WB drift | segment-level | lighting transition trace |
| compression/packet artifact | network/event-level | bitrate/packet/drop logs |
| frame dropout/duplicate | event-level | timestamp/sequence continuity |
| depth holes/scale/bias | geometry/surface-conditioned | known geometry、material/distance strata |

OpenAI Dexterous 区分 episode-correlated 与 timestep-uncorrelated observation noise，支持把 cadence 写进合同，而不是只记一个 sigma。[S3]

## 8. Occlusion 与 visibility

对 target mask \(M_t\) 和 visible mask \(M_v\)，定义：

\[
r_{vis}=\frac{|M_t\cap M_v|}{|M_t|+\epsilon}.
\]

变量解释：\(r_{vis}\) 是 target visible fraction；实现映射：render/annotation 保存 occluder ID、depth order、target-visible mask、持续时间与每相机可见率。单个 2D rectangle occluder 只是 proxy。

必须区分：

- task-natural occlusion：hand/object/robot/self-occlusion；
- environmental occlusion：工具、容器、人或背景物体；
- sensor obstruction：污渍、反光、镜头遮挡；
- camera failure/full blackout：stress/safety event；
- multi-view complementarity：一个 view 被挡，另一个 view 仍可见。

nominal training 需保留任务可解性；full occlusion/camera failure 应单独报告 fallback/recovery，不与普通 visible-fraction 样本混报。

## 9. Range provenance 与采样合同

| factor | range source | distribution/correlation | cadence |
| --- | --- | --- | --- |
| K/distortion | repeated calibration/serial variation | bounded posterior/correlation | camera/session |
| extrinsics | hand-eye/rig residual、mount tolerance、vibration | rig-global + per-camera residual | build/episode/time |
| exposure/gain/WB | real lighting/capture survey | controller/state-conditioned | frame/segment |
| blur | exposure + camera/object velocity distribution | depth/motion-conditioned | frame/segment |
| occlusion | task/scene event log、visibility histogram | object/view/time-correlated | event/segment |
| noise | dark/flat-field/signal sweep、network logs | signal/gain/time-conditioned | frame/session/event |

每项记录 `factor/unit/source/lower-upper/distribution/correlation/cadence/label mode/validity/revision`。ImageNet-C severity 可做外部 stress reference，不能替换 target capture survey。[S4]

## 10. Label、geometry 与 task consistency

| 变换 | target 处理 |
| --- | --- |
| simulator camera pose/FOV/distortion | 从同一 world state 重新 render，并重新投影 point/box/depth/pose |
| crop/resize/pad | 同步更新 pixel label、K 与 valid ROI |
| flip/warp | 只有在物理/语义成立时，按 transform 更新 label；camera-frame pose/action 需重算 |
| exposure/noise/compression | 通常 label invariant，但不得抹去必要 cue |
| occlusion | 保存 visible/full target；不可解样本 reject 或进入 stress |
| frame drop/time shift | 同步 history/proprio/action timestamp 与 valid mask |

几何 round-trip：world point→distorted/raw pixel→rectify/resize/crop→model pixel，并做逆向/known-geometry smoke。对多相机保存 camera identity，不能直接平均 pixel coordinates。[S1][S8]

## 11. Validity、rejection 与 rollback

拒绝或分流：

- camera pose/FOV 看不到 workspace 或穿入几何体；
- distortion mapping 非法/非单调或 ROI 大量无效；
- exposure/blur/noise 使必要 task cue 消失；
- occlusion 让 task 不可解却混入 nominal batch；
- independent multi-camera sampling 破坏 rig geometry/time；
- crop/flip 后 label/K/action 未同步；
- noise/compression 产生 NaN、非法 dtype/range 或 preprocess mismatch；
- combined arm nominal performance 下降且 real gate 无收益。

每次 sampler revision 保存 accepted/rejected sample、reason、seed、low/high/boundary render 与 target overlay。

## 12. Diagnostic ladder

1. **camera identity/preprocess**：view order、RGB/BGR、orientation、resize/crop/hash；
2. **geometry**：K/distortion/image size、extrinsics direction、reprojection/round-trip；
3. **static photometric**：exposure/gain/WB/gamma/saturation/color cue；
4. **dynamic camera**：exposure/readout/blur/timestamp/drop/multi-view sync；
5. **visibility**：target visible fraction、occluder、task solvability；
6. **sensor**：signal-dependent noise、bias/pattern/compression/depth invalid；
7. **real replay**：按 camera/light/motion/occlusion/noise strata 比 feature/action drift；
8. **closed loop**：固定 protocol 看 first failure、success/CI、fallback/safety event。

固定方向 pixel/pose 偏差优先查 K/R/t/frame；只在动态运动时失败查 exposure/blur/timing；特定亮度失败查 photometric/ISP；随机闪烁查 dropout/auto-exposure/network。

## 13. Matched factor matrix

固定 dataset states、render count、train steps、checkpoint init、seed、model、task/init、controller、rollout count 和 success predicate：

| arm | 变化 | 目的 |
| --- | --- | --- |
| A | nominal camera | baseline |
| B | geometry only | K/R/t/distortion sensitivity |
| C | photometric only | light/exposure/WB/gamma/material |
| D | temporal/blur only | exposure/readout/motion/drop |
| E | occlusion only | visibility/solvability/multi-view |
| F | sensor only | signal/noise/bias/compression/depth invalid |
| G | calibrated combined | complementarity |
| H | overwide/irrelevant | contamination/robustness cost |

分 nominal sim、factor holdout、real replay、sim closed-loop、real closed-loop 报告；ImageNet-C-style stress score与目标 camera/closed-loop score分栏。[S4]

## 14. 最小 artifact bundle

| Artifact | 必须字段 | 能证明 | 不能单独证明 |
| --- | --- | --- | --- |
| `camera_rig_manifest` | serial/name/frame、resolution、K/distortion/extrinsics、revision/time | camera geometry 可追溯 | calibration 足够好 |
| `calibration_bundle` | images/targets、method、reprojection/per-view error、hand-eye/rig residual | 标定过程与残差 | policy transfer 成功 |
| `capture_survey` | lighting/exposure/gain/WB、motion、timestamp、noise/depth stats | target range 有真实依据 | randomization 有收益 |
| `camera_factor_manifest` | distribution/correlation/cadence/label/validity/revision | sampler contract | sample 物理/任务完全正确 |
| `sample_rejection_ledger` | seed、factor、accepted/rejected、reason、overlay | 实际采样可审计 | policy 鲁棒 |
| `matched_camera_ablation` | A–H arms、固定项、sim/replay/closed-loop results | factor 因果对照 | 未做的 real result |
| `ownership_ledger` | 谁标定、capture、实现、训练、评估 | 个人贡献 | 效果本身 |

## 15. 注释伪代码：calibrated camera sampler

```python
def sample_camera_observation(world_state, rig, factor_contract, seed):
    # 1. Sample calibrated residuals while preserving rig correlations and camera identity.
    geometry = sample_geometry(
        rig.nominal_calibration,
        factor_contract.geometry,
        correlations=rig.correlation_constraints,
        seed=seed,
    )

    # 2. Re-render the same world state so geometry labels remain physically consistent.
    rgb_raw, geometry_targets = render_with_targets(world_state, geometry)

    # 3. Apply measured photometric, exposure/blur and signal-dependent sensor models.
    rgb_photo = apply_photometric_pipeline(rgb_raw, factor_contract.photometric)
    rgb_time = apply_exposure_and_motion_blur(rgb_photo, world_state.motion)
    rgb_sensor = apply_sensor_noise_and_compression(rgb_time, factor_contract.sensor)

    # 4. Add task-valid occlusion and save full/visible masks for solvability checks.
    rgb_occ, visibility = apply_occlusion(rgb_sensor, world_state, factor_contract.occlusion)

    # 5. Apply crop/resize and synchronize K, pixel labels, masks and timestamps.
    model_image, targets = preprocess_and_transform_targets(
        rgb_occ, geometry_targets, visibility, factor_contract.preprocess
    )

    # 6. Reject impossible/unsolvable/label-inconsistent samples and log the reason.
    return validate_and_log(model_image, targets, geometry, factor_contract, seed)
```

## 16. 项目真实性边界

对 Evidence Manifest、OPD/OpenPiVLA inventories、PER-002 与已有 Sim2Real audit 的检索，没有形成 WM-035 本地 bundle：

- 缺 camera serial/name→K/distortion/extrinsics/revision 的 rig manifest；
- 缺真实 calibration images、reprojection/hand-eye/rig residual；
- 缺 exposure/gain/WB/blur/noise/dropout/depth capture survey；
- 缺 camera factor sampler、accepted/rejected render 与 label overlay；
- 缺 crop/resize/K/point/box/pose/action round-trip tests；
- 缺 geometry/photometric/temporal/occlusion/sensor/combined/overwide matched arms；
- 缺 protocol-complete real replay/closed-loop 与 ownership。[S8][S9]

安全表达：

- 可以说：“我会先绑定 camera serial、calibration 与 preprocess revision，再从实拍 survey 建五层 camera factor，并做 label/visibility/solvability 与 matched gate。”
- 可以说：“OPD 支持静态 grounding/eval，OpenPiVLA/WAM 支持 camera/preprocess/rollout provenance 的部分审计，但没有 camera Sim2Real 闭环。”
- 不能说：“做 color jitter/blur 就完成了 camera randomization”“有 K 字段就完成标定”“ImageNet-C 更鲁棒等于 VLA 闭环更鲁棒”“项目已通过 camera DR 提升真机成功率”。

按照 evidence contract，camera/config 理解最多 C0/C1；本地 factor harness/ablation 才可能支持 C2；真实 closed-loop uplift 需要 C3 raw protocol 与 ownership。

## 17. Claim ledger

| Claim | 支持来源 | 证据等级 | 状态 |
| --- | --- | --- | --- |
| camera geometry 依赖 K/R/t/distortion 与 image space | S1 | official docs/code | checked |
| camera/light/object/texture/occlusion 是 visual DR 候选 | S2、S3 | primary | checked with task scope |
| correlated/uncorrelated noise cadence 需要区分 | S3 | primary | checked |
| noise/blur/weather/digital severity 可构成通用 corruption taxonomy | S4 | primary benchmark | checked / not target model |
| MuJoCo camera intrinsics 支持 focal/principal/sensor-size/resolution contract | S5 | official docs | checked |
| exposure/blur/noise/occlusion 的物理与任务一致性合同 | S1–S7 + engineering synthesis | synthesis | WARN / needs local execution |
| 用户项目已完成 camera calibration/DR/real transfer | S9 | missing local evidence | rejected |

## 18. 仍待独立复核与补证据

1. 一手论文/官方 docs 已复核；source freeze 保持 `independent_fact_review=PENDING`。
2. 需要真实 calibration/capture/factor/label/matched/replay/closed-loop bundle。
3. 需要真实口述后才更新练习状态；不得创建 `coaching_state.md`。
4. 浏览器本地 `file://` 若被策略阻断，只记录静态验证，不能写 visual PASS。

## 19. 参考来源

1. OpenCV, [Camera Calibration and 3D Reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) 与 [pinned calibration tutorial](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.markdown)。
2. Tobin et al., [*Domain Randomization*](https://arxiv.org/abs/1703.06907v1)。
3. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5)。
4. Hendrycks & Dietterich, [*Benchmarking Neural Network Robustness to Common Corruptions and Perturbations*](https://arxiv.org/abs/1903.12261v1)。
5. MuJoCo, [*Modeling: Camera intrinsics*](https://mujoco.readthedocs.io/en/stable/modeling.html#cameras)。
6. [WM-032 Visual DR / Relevant Support](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)。
7. [WM-034 Timing / Controller](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)。
8. [PER-002 3D Lift / Calibration](vol_06_per002_3d_lift_frame_source_freeze.html)。
9. [Evidence Manifest](../evidence/evidence_manifest.html)。

## 20. 下一边界

下一 bounded slice 是 `VLA-WM-036`：friction、contact、compliance 和 gripper semantics 为什么是 manipulation Sim2Real 的高风险点。本页不提前展开 contact solver、friction cone、gripper/controller 或 force/compliance 机制。
