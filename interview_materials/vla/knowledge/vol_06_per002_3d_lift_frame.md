# VOL 06 Perception / Grounding / Navigation：2D → 3D Lift 与 Frame Contract（PER-002）

> 状态：`drafted / VLA-PER-002 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[PER-002 3D Lift / Frame Source Freeze](../sources/vol_06_per002_3d_lift_frame_source_freeze.html)。  
> 前置知识：[PER-001 Grounding / Coordinate](vol_06_per001_grounding_coordinate.html)。

## 问题（Question）

图像上的 point 或 box 只是二维观测。要让规划器或控制器使用它，需要补齐深度、相机内参/畸变、frame 变换、时间戳、单位和不确定性。缺任一项时，“模型预测了一个 3D 抓取点”可能只是把二维中心乘了一个未经验证的常数。

本页回答：

1. pixel point 如何反投影到 camera optical frame？
2. depth、intrinsics、distortion、extrinsics 和 image size 如何绑定？
3. ROS 的 base/optical/map/odom convention 能否直接当作项目事实？
4. 时间同步、invalid depth 和不确定性怎样进入 planner/controller gate？
5. 什么证据才能把 projection math 升级为 3D execution 或闭环 success？

## 知识地图位置与前置依赖

```text
PER-001 2D point/box/text + image coordinate
                    ↓
PER-002 depth + calibration + frame transform
                    ↓
PER-003 multi-view / temporal fusion
                    ↓
planner goal / action head / controller / closed-loop predicate
```

OpenCV 的 calibration/depth 文档和 ROS REP-103/105 是公源机制参照；OPD/WAM 仅用于项目真实性边界。当前材料没有用户项目的 calibration、TF、depth 或 3D target bundle，因此本页不声称个人完成了 3D lift。

## 1. 30 秒直觉：3D lift 是一条带时间戳的链

```text
pixel (u,v)
  + depth Z + intrinsics/distortion
  → camera optical point p_c
  + timestamped extrinsic T_target←camera
  → target/world/base point p_t
  + uncertainty/validity gate
  → planner/controller input
```

二维坐标没有深度；深度没有 frame 就无法解释；frame 没有时间戳就可能把运动中的旧位姿应用到新图像。一个能画出投影 overlay 的 demo，只证明部分几何链路，不证明目标被正确抓取或导航。

## 2. Camera model：内参、畸变与 image-size contract

### 2.1 Pinhole intrinsics

相机内参矩阵通常写为：

```text
K = [[fx,  0, cx],
     [ 0, fy, cy],
     [ 0,  0,  1]]
```

`fx,fy` 是像素尺度焦距，`cx,cy` 是主点。它们只对特定 image size、裁剪和 resize 语义有效；如果把 640×480 的主点直接用于 224×224 的 letterboxed tensor，必须先证明 transform 如何更新 `K`。

### 2.2 Distortion / rectification

现实镜头存在径向和切向畸变。point 位于原始畸变图像还是 rectified 图像，必须写在 schema 中。两种合法路径是：

1. 先对图像和 point 一起 `undistort/rectify`，再使用 rectified `K`；
2. 保留原始 point，使用带 distortion 的反投影函数。

不能对畸变 pixel 直接套无畸变 pinhole 公式，并把系统偏差归因给 grounding 模型。

### 2.3 Calibration evidence

一个可复查的 calibration record 至少包括：标定板/场景、视角数量、image size、`K`、distortion coefficients、reprojection error、工具版本、时间和 revision。OpenCV 教程支持这些概念和实现入口，但不证明任何本地相机已经通过标定门。

## 3. Depth：没有 Z 就没有唯一的 3D 点

### 3.1 深度来源对照

| 来源 | 适用前提 | 关键风险 | 需要记录 |
| --- | --- | --- | --- |
| RGB-D aligned depth | RGB/depth 已配准且单位已知 | hole、边缘混合、遮挡、时间偏移 | depth unit、invalid code、registration revision |
| stereo disparity | baseline、左右相机模型和对应有效 | 远处误差放大、遮挡无视差 | baseline、disparity scale、valid mask |
| multi-view triangulation | 多视角 pose 和匹配可信 | pose/匹配误差、动态物体 | view IDs、pose timestamps、inlier rule |
| plane/table hypothesis | 目标落在已知平面 | 目标不在平面、遮挡和倾斜 | plane frame、residual、valid region |
| monocular depth | 模型提供尺度或可校准深度 | scale ambiguity、domain shift | model revision、scale calibration、uncertainty |

RGB 图像本身只提供射线，不提供唯一的 `Z`。`0`、NaN、饱和、边缘混合和超出 range 的值必须进入 invalid 或 uncertainty 分支，不能静默当作真实深度。

## 4. 反投影与 frame transform

### 4.1 Pixel → camera optical frame

对 rectified pixel `(u,v)`、深度 `Z` 和内参 `K`，相机 optical frame 中的 pinhole 反投影为：

\[
X_c=\frac{u-c_x}{f_x}Z,\qquad
Y_c=\frac{v-c_y}{f_y}Z,\qquad
Z_c=Z.
\]

`u,v` 的原点、`Z` 的单位和 `K` 的 image-size revision 必须一致。若 point 来自 letterbox 图像，先逆 resize/padding 到 calibration image space，再采样 depth；否则 `u,v` 会带有系统偏移。

### 4.2 Camera → target/world frame

用齐次变换把 camera point 变到目标 frame：

\[
\begin{bmatrix}p_t\\1\end{bmatrix}
=T_{t\leftarrow c}(\tau)\begin{bmatrix}p_c\\1\end{bmatrix},
\qquad
T_{t\leftarrow c}=\begin{bmatrix}R_{t\leftarrow c}&t_{t\leftarrow c}\\0&1\end{bmatrix}.
\]

`R` 是旋转，`t` 是平移，`τ` 是图像采集时刻或明确的插值时刻。下标要能回答“变换从哪一个 frame 到哪一个 frame”；只保存一个无标签 4×4 矩阵不够复现。

### 4.3 ROS convention 是参照，不是事实

REP-103 提供右手系、SI 单位和 body/optical frame 的常见约定；REP-105 讨论 `map`、`odom`、`base_link` 等移动平台 frame 语义。项目可以采用自己的 convention，但必须显式写轴方向、单位、frame ID 和变换方向，不能默认所有 VLA 项目都运行 ROS TF。

## 5. 时间同步与不确定性账本

至少保留以下时间戳：

```text
t_image, t_depth, t_calibration, t_tf, t_robot_state, t_action
```

检查项包括：

- RGB 与 depth 是否属于同一 capture 或经过可解释配准；
- `T_target←camera` 是否在 `t_image` 插值，而不是使用未来 pose 或过期 pose；
- 机器人/目标运动期间，时间偏差造成的空间误差是否小于 freshness budget；
- depth 与 RGB 的 resolution、crop、registration 是否同源；
- action 发出时，3D target 是否仍有效。

不确定性账本可以按来源拆分：

| 来源 | 对 3D 结果的影响 |
| --- | --- |
| pixel/parser error | 深度越大，横向 `X/Y` 误差通常越大 |
| depth noise | 直接扰动 `Z`，并通过反投影影响 `X/Y` |
| intrinsics/distortion | 系统性投影偏差 |
| extrinsics/TF | 整体旋转/平移偏差 |
| timestamp skew | 运动场景中的动态偏差 |
| axis/unit/frame bug | 可能产生大幅、非随机错误 |

uncertainty gate 可以在 planner 前拒绝 invalid/高风险目标，或把协方差/置信度作为 planner 输入；但 gate 的阈值和 fallback 仍需与任务安全合同绑定。

## 6. 可审计 3D-lift pipeline

```python
def lift_grounding(point, rgb, depth, calib, tf_buffer, contract):
    # 1. Validate image/depth size, timestamp, units and invalid-depth policy.
    assert contract.image_size == calib.image_size
    z = sample_depth(depth, point, contract.depth_sampling)
    if not valid_depth(z, contract.depth_range):
        return Invalid(reason="depth", timestamp=rgb.timestamp)

    # 2. Move the point into rectified calibration pixels.
    uv = undo_resize_crop_letterbox(point, contract.transform)
    uv_rect = rectify_or_validate(uv, calib, contract.distortion_mode)

    # 3. Back-project to the camera optical frame.
    p_camera = backproject_pinhole(uv_rect, z, calib.K, calib.depth_unit)

    # 4. Interpolate the timestamped camera->target transform.
    T = tf_buffer.lookup(calib.camera_frame, contract.target_frame,
                         rgb.timestamp, contract.tf_policy)
    p_target = transform_point(T, p_camera)

    # 5. Apply uncertainty/safety gate and emit full provenance.
    uncertainty = propagate_uncertainty(point, z, calib, T)
    if not contract.gate(uncertainty, p_target):
        return Invalid(reason="uncertainty", timestamp=rgb.timestamp)
    return Target3D(point=p_target, frame=contract.target_frame,
                    timestamp=rgb.timestamp, uncertainty=uncertainty,
                    calib_revision=calib.revision, tf_revision=T.revision)
```

伪代码把 invalid depth、逆预处理、去畸变、反投影、时间戳 TF、uncertainty 和 provenance 作为同一条链；它是面试设计合同，不是用户项目已有实现。

## 7. 证据阶梯：从几何到闭环

| 层级 | 最小可审计证据 | 不能越级支持 |
| --- | --- | --- |
| projection math | 固定 `K/distortion/image_size` 的 pixel→camera→pixel roundtrip | 深度正确、外参正确 |
| calibration | calibration inputs、reprojection error、版本、单位 | 运行时 TF 和同步正确 |
| frame transform | `T_target←camera`、frame IDs、timestamp、逆变换 smoke | 目标一定被抓取/导航 |
| planner interface | 3D target、uncertainty gate、planner input/output trace | controller 已执行成功 |
| closed-loop episode | same protocol、controller trace、success predicate、failure video、完整分母 | 跨任务/真机泛化，除非协议一致 |

OPD 当前是 static point/box/text holdout，缺 depth/TF/3D planner trace；WAM bundle 有 camera/controller/horizon 字段，仍缺 calibration、depth、3D target 和 checkpoint verification。因此二者都不能作为 PER-002 的个人 3D 成果证明。

## 8. 项目映射与回答边界

### OPD

可以讲：2D point/box/text 的协议、route metadata、strict/lenient scorer 和 raw-holdout leakage gate。不能讲：point 已自动 lift 到 base frame、五 expert 已解决深度、或 static holdout 证明机器人抓取。

### WAM

manifest 中的 camera resolution、controller、open-loop 和 action shape 可用于说明 rollout provenance；它们不包含 calibration matrix、depth stream、TF tree、3D target 或真机 success。应把它们定位为 rollout interface evidence，而不是 3D perception evidence。

### 个人 ownership

如果没有 calibration script、TF config、roundtrip log、failure trace 或逐文件 ledger，只能说“理解并审计 3D lift 合同”，不能说“我完成了相机标定/外参标定/3D grasp pipeline”。

## 9. Trade-off 与高概率 bad case

| 选择 | 优点 | 风险 |
| --- | --- | --- |
| RGB-D | 单帧可得 Z，链路短 | 配准、边缘 hole、单位和时间同步 |
| stereo | 不需要主动深度 | 视差、baseline、遮挡和远距离误差 |
| plane hypothesis | 桌面任务简单稳定 | 非平面目标和遮挡会系统偏差 |
| monocular depth | 硬件简单 | scale/domain shift/uncertainty |
| static extrinsic | 简单、低运行时成本 | 相机移动或机械臂 flex 后失效 |
| timestamped TF | 可处理运动 | 需要 buffer、插值和时钟同步 |

常见 bad case：用 2D box 中心当 3D grasp 点；把 RGB resolution 的 `K` 用到 resized tensor；畸变点直接套 pinhole；深度单位 mm/m 混淆；忽略 depth invalid code；camera→base 方向写反；使用最新 TF 而不是 capture-time TF；只看 overlay 不做 roundtrip；把 ROS frame convention 当作项目事实；把 planner trace 当作 controller success。

## 10. 面试回答检查表

回答 PER-002 至少覆盖：

1. 深度来源和 invalid policy；
2. `K/distortion/image_size` 与 pixel/rectified space；
3. (X_c,Y_c,Z_c) 反投影公式；
4. `T_target←camera(timestamp)` 的方向、frame ID、单位和 revision；
5. RGB/depth/TF/robot-state 时间同步；
6. uncertainty gate 与 planner/controller 分层；
7. OPD/WAM 当前没有 3D artifact 的证据边界。

## 11. 结论与下一步

3D lift 的关键不是记住一个反投影公式，而是把 depth、calibration、frame、timestamp、uncertainty 和 downstream predicate 绑定成可复查链路。OpenCV 和 ROS 文档支持机制与 convention；当前项目材料只能支持 2D grounding 或 rollout provenance，不能升级为个人 3D lift 或真机成果。节点保持 `WARN`，对应题卡已生成并保持 `unseen`；下一步进行 PER-001..004 真实口述或补一个本地 3D roundtrip artifact。

## References

1. [PER-002 3D Lift / Frame Source Freeze](../sources/vol_06_per002_3d_lift_frame_source_freeze.html)。
2. OpenCV，[camera calibration](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.markdown) 与 [depth/stereo](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_depthmap/py_depthmap.markdown)。
3. ROS [REP-103](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0103.rst) 与 [REP-105](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0105.rst)。
4. [PER-001 Grounding / Coordinate Knowledge](vol_06_per001_grounding_coordinate.html)。
5. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 与 [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
