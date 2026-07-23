# VOL 08 CODE-VLA-005 原子手撕题卡：Homogeneous Transform Composition

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`CODE-VLA-005`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-005 Knowledge](../knowledge/vol_08_code005_transform.html)；来源边界见 [CODE-005 Source Freeze](../sources/vol_08_code005_transform_source_freeze.html)。

## 手写 SE(3) 齐次变换与 roundtrip

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-005</b> · 请解释并手写 4×4 homogeneous transform composition，说明 frame 方向、逆变换和测试。</summary>

**面试意图**：判断你能否处理 \(T^A_B\) 方向、组合顺序、point/vector/pose、刚体逆、frame/单位/时间戳和 roundtrip，而不是只会矩阵乘法。

**30 秒回答**：先定义 T^A_B 是 B→A，点用 [x,y,z,1]，direction 用 w=0；组合 T^A_C=T^A_B T^B_C，刚体逆为 Rᵀ、-Rᵀt。冻结 frame/单位/时间戳，做 identity、逆变换和 roundtrip 测试。

**机制展开（约 2 分钟）**：写 T=[R,t;0,1]，明确上标目标、下标输入；compose 右到左。点乘 w=1，方向 w=0，pose 还要变换姿态。刚体 inverse 用 Rᵀ 和 -Rᵀt，并检查 RᵀR≈I、det≈1。记录 frame_id、parent/child、米/mm、timestamp、calibration revision；用 known rotation、composition/inverse roundtrip、batch、unit/frame mismatch 和 capture-time TF 测试。几何正确不等于 depth/planner/controller 成功。

**诊断 / 证据**：先用 identity、pure translation、90° rotation 手算，再做 `compose(T_A_B,T_B_C)` 与逐步变换 parity；随机点做 inverse roundtrip，验证 rotation orthogonality/determinant、bottom row、finite、batch broadcast。对 camera/base/world 记录 parent/child、matrix revision、capture-time timestamp、unit 和 uncertainty；若 overlay 对但 frame/时间不一致，不能把它当 controller 正确。

**项目挂钩**：OPD 可连接 point/box/text 坐标协议；OpenPiVLA/WAM 可连接 camera/action packaging；Robot Harness 可连接 frame-aware tool schema；UWM/LIBERO 可连接 camera/state/action shape。安全表达是“我能实现并审计 SE(3) 接口”，不把通用矩阵代码写成项目标定、抓取或导航成功。

**追问树**：T^A_B 的上下标怎样读？为什么不能直接转置整个 4×4？point 与 direction 的 w 有何不同？组合为何右到左？刚体 inverse 的平移项为何是 -Rᵀt？米/mm 错会怎样？latest TF 能否替代 capture-time TF？overlay 对能证明什么？

**易错点**：把 B→A 写成 A→B；乘法顺序反；把 direction 也平移；把 pose 只变换 xyz；用一般矩阵 inverse 代替 rigid inverse 却不检查 R；忽略 frame/单位/时间戳/revision；把几何 roundtrip 当闭环成功。

**危险答案**：说“4×4 矩阵转置就是逆”“只要 overlay 看起来对就行”“ROS 轴序默认适用于所有项目”“最新 TF 总是最好”或“point 变换成功就证明抓取/导航成功”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-005 Knowledge](../knowledge/vol_08_code005_transform.html)：SE(3)、方向、point/vector/pose、inverse、frame/单位/时间和测试矩阵。
2. [CODE-005 Source Freeze](../sources/vol_08_code005_transform_source_freeze.html)：ROS REP-103/105、SciPy Rotation 与 PER-002 边界。
3. [ROS REP-103](https://www.ros.org/reps/rep-0103.html)、[REP-105](https://www.ros.org/reps/rep-0105.html) 与 SciPy [`Rotation`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html)。
