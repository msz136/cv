# VOL 08 CODE-VLA-006 原子手撕题卡：2-Link Planar Forward Kinematics

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-006`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-006 Knowledge](../knowledge/vol_08_code006_planar_fk.html)；来源边界见 [CODE-006 Source Freeze](../sources/vol_08_code006_planar_fk_source_freeze.html)。

## 手写二连杆平面正运动学

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-006</b> · 请推导并实现 2-link planar forward kinematics，说明角度/坐标约定和测试。</summary>

**面试意图**：判断你能否处理相对 joint angle、frame/单位、解析式、齐次变换链、Jacobian 直觉和边界姿态，而不是只背结果。

**30 秒回答**：先冻结 radians、base frame 和相对 joint angle：x=l1 cosθ1+l2 cos(θ1+θ2)，y 同理，φ=θ1+θ2。也可用 Rz(θ1)Tx(l1)Rz(θ2)Tx(l2)。用 zero/90/folded、矩阵 parity 和 Jacobian finite difference 测。

**机制展开（约 2 分钟）**：对 [B,2] 输入，先算 c1/s1 与 c12/s12，再输出 x=l1c1+l2c12、y=l1s1+l2s12、φ=θ1+θ2；θ2 是相对角。矩阵链右到左，平移沿当前 link frame。冻结 rad/deg、米/mm、joint zero、正方向和 tool offset。测试 zero、90°、folded、负角、解析/矩阵 parity、batch、单位 mismatch 与有限差分 Jacobian；FK 不等于 IK、碰撞或 controller 成功。

**诊断 / 证据**：先用 zero、π/2、π folded 手算，再对解析式和 `Rz·Tx·Rz·Tx` 做数值 parity；随机角度做 finite-difference Jacobian，检查 batch `[B,2]→[B,3]`、finite、单位和 frame metadata。若接入项目，固定 URDF/joint zero/limit、tool transform、angle unit 和 calibration revision；不要只用一张 overlay 证明几何或控制正确。

**项目挂钩**：OPD 可连接 point/box 坐标协议；OpenPiVLA/WAM 可连接 camera/action packaging；Robot Harness/UWM 可连接 robot state schema。安全表达是“我能实现和审计 FK 接口”，不把通用二连杆代码写成项目标定、IK、控制或真机成功。

**追问树**：θ2 是 relative 还是 global？为什么第二项用 θ1+θ2？矩阵链为何右到左？角度 degree 忘转 radian 会怎样？Jacobian 何时退化？FK 能否解决 IK？tool offset 放在哪里？如何验证 frame 方向？

**易错点**：把 θ2 当 global angle；sin/cos 轴方向反；degree/radian 混用；link 平移在错误 frame；忘记 tool transform；把 finite-difference Jacobian 当完整 controller；把 FK 结果当抓取/导航成功。

**危险答案**：说“FK 直接给 IK”“θ1、θ2 可以任意相加不看 convention”“长度单位不影响结果”“zero pose 看起来对就证明模型正确”或“二连杆 FK 证明项目真机控制成功”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-006 Knowledge](../knowledge/vol_08_code006_planar_fk.html)：解析 FK、齐次链、frame/单位、Jacobian 与测试矩阵。
2. [CODE-006 Source Freeze](../sources/vol_08_code006_planar_fk_source_freeze.html)：Modern Robotics、ROS REP-103 与项目边界。
3. Modern Robotics [Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/) 与 [ROS REP-103](https://www.ros.org/reps/rep-0103.html)。
