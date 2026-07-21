# VOL 06 Perception / Grounding / Navigation：PER-002 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-PER-002`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-002 3D Lift / Frame Knowledge](../knowledge/vol_06_per002_3d_lift_frame.html)；来源边界见 [Source Freeze](../sources/vol_06_per002_3d_lift_frame_source_freeze.html)。

## 2D Grounding 如何变成可信的 3D Target

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-002</b> · 一个 grounding point 怎样才能安全地进入 planner 或 controller？</summary>

**面试意图**：判断你能否把深度、标定、frame、时间同步和不确定性组成可审计链路，而不是把二维中心直接当抓取点。

**30 秒回答**：先固定 rectified pixel、depth 单位和 `K/distortion`，用反投影得到 camera point，再用带时间戳的 `T_target←camera` 变到目标 frame；做 invalid/uncertainty gate 后才交给 planner。2D holdout 不等于 3D 或闭环成功。

**机制展开（约 2 分钟）**：深度可来自 RGB-D、stereo、triangulation 或平面假设，记录单位、invalid 和 registration。对 rectified `(u,v,Z)`，`X=(u-cx)Z/fx`、`Y=(v-cy)Z/fy`、`Zc=Z`；再用 `T_target←camera(τ)` 变换，绑定 frame、timestamp、calibration revision。crop/letterbox 要先逆变换；depth 无效、TF 不同步或 uncertainty 超阈值就返回 invalid/safe branch。OpenCV/ROS 只支持机制；OPD 是 2D holdout，WAM 只有 camera/controller 字段，不能声称个人完成 3D lift。

**诊断 / 证据**：固定 `K/distortion/image_size`、depth unit、frame IDs 和 timestamp，使用 known geometry 做 pixel→camera→pixel roundtrip；再做 camera↔target 逆变换 smoke、静态/运动同步对照、invalid-depth 注入和 uncertainty gate。保存 calibration/reprojection error、TF revision、depth valid mask、planner input/output 与 controller trace；缺任一项就停在 projection/calibration 层。

**项目挂钩**：OPD 可用于说明 point/box/text 协议与静态 scorer；WAM manifest 可说明 camera、controller、horizon 的 rollout provenance。安全表达是“我能审计 3D lift 合同和缺口”，不把这些材料升级为抓取、导航或真机成功。

**追问树**：为什么 RGB 图像没有唯一深度？畸变 pixel 能否直接套 pinhole？`T_target←camera` 方向怎样核对？为什么要用 capture-time TF？depth 单位错会怎样？ROS REP-103 是项目事实吗？overlay 看起来对能否证明 controller 正确？

**易错点**：把 2D 中心当 3D 点；`K` 与 resize image size 不匹配；忽略畸变、padding、depth invalid 或 mm/m；camera→base 方向写反；使用最新而非 capture-time TF；只做 overlay 不做 roundtrip。

**危险答案**：说“有 RGB 就能恢复深度”“4×4 外参矩阵不需要 frame/时间戳”“ROS 轴序默认适用于所有项目”“3D 点生成就等于抓取成功”或“OPD/WAM 的静态/rollout证据证明 3D 泛化”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-002 3D Lift / Frame Knowledge](../knowledge/vol_06_per002_3d_lift_frame.html)：内参、深度、反投影、TF、同步、不确定性与证据阶梯。
2. [PER-002 3D Lift / Frame Source Freeze](../sources/vol_06_per002_3d_lift_frame_source_freeze.html)：OpenCV、ROS REP-103/105 与项目边界。
3. [OpenCV calibration/depth tutorials](https://github.com/opencv/opencv/tree/f7dd7df170add1655de75b5e95f20f41d2a88293)：camera matrix、distortion、stereo/depth 机制。
4. [ROS REP-103/105](https://github.com/ros-infrastructure/rep/tree/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5)：单位、坐标和移动平台 frame convention。
