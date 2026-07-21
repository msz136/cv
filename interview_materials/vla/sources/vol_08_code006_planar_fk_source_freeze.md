# VOL 08 CODE-006 Source Freeze：2-Link Planar Forward Kinematics

> 状态：`source_frozen / CODE-VLA-006 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结二连杆平面 FK、角度/长度单位、frame 与数值测试边界；不把解析 FK 写成 IK、控制或真机成果。

## 问题（Question）

给定两个连杆长度和关节角，如何推导末端位置/姿态，写出齐次变换或解析式，并验证角度单位、坐标方向、Jacobian 直觉和边界姿态？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [Modern Robotics Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/) | textbook/web reference；2026-07-18 | FK、product of exponentials、body/space frame 机制参照 | 用户项目使用同一机器人几何或控制器 |
| [ROS REP-103](https://www.ros.org/reps/rep-0103.html) | standard | SI units、右手系、角度/坐标约定 | 项目实际 joint convention 已核验 |
| 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) | local canonical knowledge | 2D rotation、齐次变换、控制基础 | CODE-VLA-006 数值/符号 parity |
| 本仓库 [CODE-005 Transform](../knowledge/vol_08_code005_transform.html) | local knowledge | frame、composition、point/vector 与 roundtrip | 项目已完成 FK/controller 闭环 |

## 2. 冻结数学与单位

对 base frame 中的二连杆：

\[
x=l_1\cos\theta_1+l_2\cos(\theta_1+\theta_2),\qquad
y=l_1\sin\theta_1+l_2\sin(\theta_1+\theta_2),
\]

末端平面姿态为 (phi=\theta_1+\theta_2)。等价地：

\[
T^0_E=R_z(\theta_1)T_x(l_1)R_z(\theta_2)T_x(l_2).
\]

必须冻结角度是 radians 还是 degrees、长度单位、joint zero、正方向、base/tool frame、是否包含 joint offset 和 tool transform。

## 3. 测试门

最小矩阵：zero angles、(	heta_1=\pi/2)、folded (	heta_2=\pi)、negative angles、(l_i=0)、解析式与矩阵式 parity、batch shape、finite-difference Jacobian、radian/degree mismatch 的显式失败。FK 只给定姿态到位置映射，不证明 IK 唯一、碰撞无关或 controller 成功。

## 4. Source gate 结论

Modern Robotics、ROS REP-103、VOL 01 与 CODE-005 足以冻结 FK、frame、单位和测试合同；当前没有本地 CODE-VLA-006 实现或机器人 calibration/controller artifact，因此保持 `WARN`。

下一步：保持已同步的 CODE-VLA-006 题卡为 `unseen`，进行白板练习或补充 FK/URDF/Jacobian artifact。

## References

1. Modern Robotics [Chapter 4: Forward Kinematics](https://modernrobotics.northwestern.edu/chapters/chapter4/)。
2. [ROS REP-103](https://www.ros.org/reps/rep-0103.html)。
3. 本仓库 [VOL 01 Foundations](../knowledge/vol_01_foundations.html) 与 [CODE-005 Transform](../knowledge/vol_08_code005_transform.html)。
