# VOL 08 CODE-005 Source Freeze：Homogeneous Transform Composition

> 状态：`source_frozen / CODE-VLA-005 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 SE(3) 齐次矩阵、frame/方向/单位、点与 pose 变换、逆变换和 roundtrip 测试边界；不把通用几何代码写成项目标定或控制成果。

## 问题（Question）

手撕 4×4 homogeneous transform composition 时，如何解释 (T^A_B) 的方向、点/pose 的乘法、逆变换、旋转正交性、单位和 frame，并设计 roundtrip 测试？

## 1. 来源与实现参照

| 来源 | 类型 / revision | 可支持 | 不能支持 |
| --- | --- | --- | --- |
| [ROS REP-103](https://www.ros.org/reps/rep-0103.html) | standard；2026-07-18 | SI units、坐标轴、右手系与 frame 约定 | 用户项目实际 frame/axis 已正确 |
| [ROS REP-105](https://www.ros.org/reps/rep-0105.html) | standard；2026-07-18 | map/odom/base_link 等移动机器人 frame 语义 | 项目已有同步 TF 或闭环定位 |
| [SciPy Rotation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html) | official API docs；2026-07-18 | rotation representation、compose、inverse、apply | 用户项目使用同一 convention |
| 本仓库 [VOL 06 PER-002](../knowledge/vol_06_per002_3d_lift_frame.html) | local knowledge | pixel→camera→target、timestamped TF 与 uncertainty | 项目已有真实 3D/控制成功 |

## 2. 冻结数学与方向

齐次变换：

\[
T^A_B=\begin{bmatrix}R^A_B&t^A_B\\0&1\end{bmatrix},\qquad
\tilde p_A=T^A_B\tilde p_B.
\]

上标表示目标 frame，下标表示输入 frame；复合遵守矩阵右到左：(T^A_C=T^A_B T^B_C)。逆变换：

\[
(T^A_B)^{-1}=\begin{bmatrix}(R^A_B)^\top&-(R^A_B)^\top t^A_B\\0&1\end{bmatrix}.
\]

必须冻结列/行向量 convention、米/毫米、右手系、旋转表示、时间戳和 frame id；shape 正确不等于方向正确。

## 3. 测试门

最小矩阵：identity、pure translation、known 90° rotation、composition order、inverse roundtrip、point vs pose、rotation orthogonality/determinant、unit mismatch、frame label mismatch、batch shape 和 finite/NaN。不能只用可视化 overlay；应保存输入 frame、输出 frame、矩阵 revision 和误差阈值。

## 4. VLA 边界

grounding point/box、depth lift、waypoint、robot action 都可能跨 camera/base/world frame；transform 只完成几何变换，不证明 planner/controller 或抓取成功。时间不同的 TF、标定 revision、pose uncertainty 和 action age 要独立记录。

## 5. Source gate 结论

ROS 标准、SciPy API 与 PER-002 足以冻结 SE(3)、frame、单位和 roundtrip 合同；当前没有本地 CODE-VLA-005 实现、标定/TF parity 或 controller artifact，因此保持 `WARN`。

下一步：保持已同步的 CODE-VLA-005 题卡为 `unseen`，进行白板练习或补充 TF/calibration roundtrip artifact。

## References

1. [ROS REP-103](https://www.ros.org/reps/rep-0103.html) 与 [REP-105](https://www.ros.org/reps/rep-0105.html)。
2. SciPy [`Rotation`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html)。
3. 本仓库 [VOL 06 PER-002](../knowledge/vol_06_per002_3d_lift_frame.html)。
