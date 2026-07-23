# VOL 08 CODE-006：2-Link Planar Forward Kinematics

> 状态：`drafted / CODE-VLA-006 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-006 Source Freeze](../sources/vol_08_code006_planar_fk_source_freeze.html)。

## 问题（Question）

二连杆平面 FK 是机器人几何题的最小闭环：给定 \((l_1,l_2,\theta_1,\theta_2)\)，输出末端位置与平面姿态，并能解释 frame、单位、组合顺序、Jacobian 和边界姿态。

## 1. 解析推导

第一杆末端：

\[
p_1=\begin{bmatrix}l_1\cos\theta_1\\l_1\sin\theta_1\end{bmatrix}.
\]

第二杆相对第一杆的方向是 \(\theta_1+\theta_2\)，所以：

\[
x=l_1\cos\theta_1+l_2\cos(\theta_1+\theta_2),\quad
y=l_1\sin\theta_1+l_2\sin(\theta_1+\theta_2).
\]

末端平面姿态：

\[
\phi=\theta_1+\theta_2.
\]

这里 \(\theta_2\) 是相对 joint angle；若输入给的是 world/global angle，第二项不能再次加 \(\theta_1\)。

## 2. 齐次变换形式

```python
def planar_fk(l1, l2, theta1, theta2):
    # Inputs use radians and the base frame is x-right/y-up.
    c1, s1 = torch.cos(theta1), torch.sin(theta1)
    c12, s12 = torch.cos(theta1 + theta2), torch.sin(theta1 + theta2)
    x = l1 * c1 + l2 * c12
    y = l1 * s1 + l2 * s12
    phi = theta1 + theta2
    return torch.stack((x, y, phi), dim=-1)
```

等价的矩阵链：

\[
T^0_E=R_z(\theta_1)T_x(l_1)R_z(\theta_2)T_x(l_2).
\]

矩阵乘法右到左，先做 joint rotation，再沿当前 link frame 平移。若把 \(T_x(l_2)\) 放到 rotation 前，结果会错误但 shape 仍然正确。

## 3. 角度、长度与 frame

冻结：radian/degree、长度单位、joint zero、正方向、base frame、tool offset 和是否包含 calibration。ROS REP-103 推荐 SI units 和右手系，但项目自己的 joint convention 仍需从 URDF/config/driver 核验。角度忘记从 degree 转 radian 往往不会报 shape 错，只会产生完全错误的位置。

## 4. Jacobian 直觉

对位置 (p=[x,y]^T)：

\[
J=\frac{\partial p}{\partial[\theta_1,\theta_2]}=
\begin{bmatrix}
-l_1\sin\theta_1-l_2\sin(\theta_1+\theta_2)&-l_2\sin(\theta_1+\theta_2)\\
l_1\cos\theta_1+l_2\cos(\theta_1+\theta_2)&l_2\cos(\theta_1+\theta_2)
\end{bmatrix}.
\]

小角度下 \(\Delta p\approx J\Delta\theta\)。当两杆伸直或折叠时，Jacobian 可能退化，某些笛卡尔方向难以通过小关节变化实现；这只是局部可动性提示，不是完整控制器证明。

## 5. 测试矩阵

| 测试 | 断言 | 典型 bug |
| --- | --- | --- |
| zero angles | `(x,y)=(l1+l2,0)` | sin/cos 或 frame 错 |
| \(\theta_1=\pi/2\) | 末端沿 y 方向 | degree/radian、轴方向错 |
| folded \(\theta_2=\pi\) | 两杆相反 | 把 θ2 当 global angle |
| negative angles | 右手系方向一致 | 符号 convention 错 |
| matrix/analytic parity | 两种 FK 误差在阈值内 | composition 顺序错 |
| finite-difference Jacobian | 数值导数接近解析 J | Jacobian 符号错 |
| batch | `[B,2]→[B,3]` shape 正确 | 只支持 scalar |
| unit mismatch | 显式拒绝 degree/mm 配置 | 静默错单位 |

## 6. VLA / 项目映射

grounding point 进入 robot base、waypoint 进入 planner、action pose 进入 controller 时，都可以复用 FK/SE(3) 的 frame 和单位审计。FK 只说明 joint→pose 的几何映射，不包含 IK、碰撞、动力学、接触或 closed-loop success。

OPD/WAM/OpenPiVLA 的 camera/action 字段可作为接口讨论；Robot Harness/UWM 的 robot state schema 可作为 frame/shape 检查点。当前没有 CODE-VLA-006 的本地 URDF、joint calibration、controller trace 或真机结果。

## 7. 结论与下一步

二连杆 FK 的高分答案是：明确相对 joint angle、frame/单位，写出解析式和矩阵链，说明右到左 composition，再用 zero/90°/folded、matrix parity 和 finite-difference Jacobian 验证。它是几何层证据，不等于 IK、控制或真机成功。

下一步：保持 `CODE-VLA-006` 题卡为 `unseen`，进行一次白板/口述练习，或补充本地 FK/URDF/Jacobian artifact。

## References

1. [CODE-006 Source Freeze](../sources/vol_08_code006_planar_fk_source_freeze.html)。
2. Modern Robotics [Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/) 与 [ROS REP-103](https://www.ros.org/reps/rep-0103.html)。
3. 本仓库 [CODE-005 Transform](vol_08_code005_transform.html) 与 [VOL 01 Foundations](vol_01_foundations.html)。
