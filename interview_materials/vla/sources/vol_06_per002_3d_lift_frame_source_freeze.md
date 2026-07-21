# VOL 06 PER-002 Source Freeze：2D Grounding → 3D Lift、相机标定与 Frame Contract

> 状态：`source_frozen / VLA-PER-002 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结从像素 point/box 到相机/机器人坐标的最小合同；不把 2D grounding 结果升级为已验证的 3D grasp、导航或真机控制结果。

## 问题（Question）

当模型在图像上输出一个 point 或 box，如何把它变成机器人可以使用的 3D 目标？至少要回答：深度来自哪里、内参/畸变如何处理、相机坐标和机器人 base 坐标如何变换、时间戳是否对齐、frame convention 是什么、误差如何传播，以及哪些证据才能证明 downstream action 真的使用了正确的 3D 点。

最小链路：

```text
pixel point/box
  → rectified pixel + depth sample/plane hypothesis
  → camera intrinsics inverse projection
  → camera optical frame
  → timestamped extrinsic transform
  → robot/world frame
  → target/affordance + uncertainty gate
  → planner/controller contract
```

## 1. 冻结来源与指纹

SHA 对 2026-07-18 通过 pinned URL 获取的 UTF-8 原文计算。官方文档支持几何和 frame 语义；本地 OPD/WAM 材料只用于声明“当前项目缺哪些 3D artifact”，不能反推已经完成 3D lift。

| 来源 | 类型 / revision | SHA-256 | 可支持的事实 | 不能支持的 claim |
| --- | --- | --- | --- | --- |
| [OpenCV camera calibration tutorial](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.markdown) | official-code/docs；commit `f7dd7df170add1655de75b5e95f20f41d2a88293` | `72f48a264d331a7d81dcd9463b98f096871cb140105f96f08abdf954d84203c4` | camera matrix、distortion、calibration views、reprojection-error 语义 | 当前项目相机已经标定、误差足够小或外参正确 |
| [OpenCV depth / stereo tutorial](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_depthmap/py_depthmap.markdown) | official-code/docs；同一 commit | `e41cd9a9b4b8674c5b50009e9e6519c8e94853762a43ab1afb1232d6874ee826` | disparity/depth、stereo geometry 与深度恢复的实现背景 | 单目 point 已自动拥有可靠深度，或深度单位/同步已经闭合 |
| [ROS REP-103](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0103.rst) | primary robotics convention；commit `11ca24a41f31480dfb9562ba99f2a5b93d3ebda5` | `bf397ddcab96cc1d10d8f5893960cb1d5e50154dd96462433a5ac342237a0c20` | SI units、right-handed frames、base/body 与 optical frame 约定 | 任意项目一定使用 ROS frames 或遵守同一轴序 |
| [ROS REP-105](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0105.rst) | primary robotics convention；同一 commit | `6bca6ae2b392bbb8e95c283c672549b832c58128feaccc4d77b6bf65534f565e` | `map/odom/base_link` 等移动机器人 frame 关系与语义边界 | 当前导航系统已经有可靠 localization、TF tree 或 loop closure |
| [PER-001 Grounding Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html) | local canonical source | 本仓库已登记 | 2D point/box/text 表示、normalized→pixel 变换与 parser boundary | 2D output 自带深度、外参或 controller contract |
| [PER-001 Grounding Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html) | local canonical knowledge | 本仓库已登记 | grounding valid、geometric match、task success 三层分离 | 3D lift 或多视角融合已在个人项目中完成 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | local-evidence；审计日期 2026-07-17 | inventory 内源码/表格 SHA | point/box/text static holdout、strict/lenient/protocol-fixed boundary | depth/extrinsic/3D controller、真机闭环或 ownership C3 |
| [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html) | local-evidence；诊断 bundle | manifest SHA 见页面 | camera resolution、controller 与 rollout provenance 字段 | checkpoint binary、camera calibration、3D target 或真机成功 |

## 2. 冻结的 3D lift 合同

### 2.1 相机内参与去畸变

针孔模型的核心字段是：

```text
K = [[fx, 0, cx],
     [0, fy, cy],
     [0,  0,  1]]
distortion = (k1, k2, p1, p2, ...)
image_size = (W, H)
```

point 在原图还是 rectified image 上，必须显式声明。若 point 在畸变原图中，不能直接套 rectified pinhole 公式；应先 `undistort/rectify` 或用同一模型反投影。标定结果还要记录 calibration board/视角、重投影误差、图像尺寸和版本，不能只保存一个 `K`。

### 2.2 深度来源与单位

2D 点到 3D 点需要一个深度约束，常见来源包括：

| 深度来源 | 可用假设 | 主要风险 |
| --- | --- | --- |
| RGB-D aligned depth | RGB 与 depth 已配准、单位和 invalid code 已知 | 深度空洞、边缘混合、时间不同步 |
| stereo disparity | baseline、左右内参和视差有效 | disparity noise 随深度放大，遮挡区域缺失 |
| multi-view triangulation | 相机位姿和跨帧对应已知 | pose/匹配误差、动态物体 |
| plane/table hypothesis | 目标落在已知平面 | 目标不在平面或遮挡时产生系统偏差 |
| monocular estimate | 模型给出相对/绝对深度 | scale、domain shift 与 uncertainty 未闭合 |

“有 RGB 图像”本身不能推出 3D depth；`depth=0`、NaN、远距离饱和和边缘混合都应进入 invalid/uncertainty 分支。

### 2.3 反投影与 frame transform

对 rectified pixel `(u,v)` 和相机深度 `Z`，相机 optical frame 中的一种反投影是：

\[
X_c=\frac{u-c_x}{f_x}Z,\qquad
Y_c=\frac{v-c_y}{f_y}Z,\qquad
Z_c=Z.
\]

这里 `u,v` 的原点、`Z` 的单位、`fx,fy,cx,cy` 的 image-size 版本必须一致。然后用带时间戳的齐次变换到目标 frame：

\[
\begin{bmatrix}p_t\\1\end{bmatrix}
=
T_{t\leftarrow c}(\tau)
\begin{bmatrix}p_c\\1\end{bmatrix},
\qquad
T=\begin{bmatrix}R&t\\0&1\end{bmatrix}.
\]

`R` 是旋转、`t` 是平移；下标明确“从 camera 到 target”的方向。不能只保存一个 4×4 数字而省略 frame ID、时间戳、单位和 calibration revision。

### 2.4 Frame convention

ROS REP-103 是一个可核查的 convention 参照：机器人 body/base frame 与 camera optical frame 的轴方向不同；REP-105 进一步定义 map/odom/base_link 等移动机器人 frame 语义。项目可以采用自己的约定，但必须写出轴方向、右手性、单位和变换方向，不可把 ROS 约定默认成事实。

## 3. 时间同步与不确定性

3D lift 不是静态数学题。相机、深度、机器人状态和 TF 都带时间戳：

```text
t_image, t_depth, t_tf, t_robot_state, t_action
```

至少要检查：image/depth 是否同一 frame、TF 是否在 `t_image` 插值或 extrapolate、机器人运动期间的 pose 差异、depth 与 RGB 的 registration，以及 action 发出时目标是否仍在 freshness budget 内。

一个简化的不确定性账本可以分为：

| 来源 | 影响 |
| --- | --- |
| pixel/parser error | 横向 `X/Y` 误差随深度放大 |
| depth noise | 直接影响 `Z`，并通过内参传播到 `X/Y` |
| intrinsics/distortion | 系统性投影偏差 |
| extrinsics/TF | 整体平移/旋转偏差 |
| timestamp skew | 运动物体或机械臂运动时产生动态偏差 |
| frame/axis/unit bug | 可能是大幅、非随机错误 |

不能用单次视觉 overlay 证明 3D contract 正确；至少需要 sentinel target、known geometry、静态/运动时序和 controller-side roundtrip。

## 4. 3D 证据阶梯

| 层级 | 最小证据 | 仍不能支持 |
| --- | --- | --- |
| projection math | 固定 `K/distortion/image_size`，pixel→camera roundtrip | 深度或外参正确 |
| calibration | calibration dataset、reprojection error、版本和单位 | 运行时 TF/同步正确 |
| frame transform | `T_target←camera`、frame ID、timestamp、逆变换 smoke | 目标被正确抓取/导航 |
| perception-to-planner | 3D target、uncertainty gate、planner input/output trace | controller 执行成功 |
| closed-loop | same protocol episode、controller trace、success predicate、failure video | 跨任务/真机泛化，除非分母和协议完整 |

当前 OPD 证据主要停留在 static point/box/text holdout；WAM bundle 有 camera/controller 字段但没有 calibration/3D target；因此本仓库不能把任何项目数字升级为 PER-002 的 3D 成果。

## 5. Source gate 结论与下游范围

已冻结：

1. 2D grounding 只有在深度/平面假设、内参、去畸变和 image-size contract 齐全后，才可反投影为 3D 点。
2. 3D 点必须绑定 camera optical frame、target frame、时间戳、单位、`K/distortion` 和 `T` revision。
3. ROS REP-103/105 是 convention 参照，不是用户项目已经采用的事实；OpenCV 文档支持 calibration/depth 机制，不支持本地运行结果。
4. projection、calibration、TF、planner、controller、closed-loop 是证据阶梯，不能跨层外推。

知识页与 `VLA-PER-002` 原子题卡已补充 3D lift 伪代码、深度采样/平面拟合、uncertainty gate 与 TF roundtrip；multi-view fusion 仍由 PER-003 单独承载。

当前 verdict：`WARN`。来源支持几何与 frame 设计，不支持用户项目已完成 3D lift、真机抓取或导航成功。

## References

1. OpenCV，[camera calibration tutorial @f7dd7df](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.markdown) 与 [depth tutorial](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_depthmap/py_depthmap.markdown)。
2. ROS REP-103，[Standard Units of Measure and Coordinate Conventions](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0103.rst)。
3. ROS REP-105，[Coordinate Frames for Mobile Platforms](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0105.rst)。
4. [PER-001 Grounding / Coordinate Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html)。
5. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 与 [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
