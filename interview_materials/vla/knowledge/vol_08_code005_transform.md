# VOL 08 CODE-005：Homogeneous Transform Composition

> 状态：`drafted / CODE-VLA-005 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[CODE-005 Source Freeze](../sources/vol_08_code005_transform_source_freeze.html)。

## 问题（Question）

机器人面试中的 4×4 变换题，真正考的是 frame/方向/单位和组合顺序。一个矩阵 shape 正确、overlay 看起来差不多，也可能把 camera→base 写反或把毫米当米。

## 1. 齐次矩阵与方向

\[
T^A_B=\begin{bmatrix}R^A_B&t^A_B\\0&1\end{bmatrix},\qquad
\tilde p_A=T^A_B\tilde p_B.
\]

记号约定：上标是输出/目标 frame，下标是输入 frame。若点 (p_B) 在 B frame，乘 (T^A_B) 得 A frame。复合必须右到左：

\[
T^A_C=T^A_B T^B_C.
\]

不能把 `T_B_A` 和 `T_A_B` 当作转置名称；它们通常互为逆，而不是简单转置整个 4×4 矩阵。

## 2. 手写实现

```python
def make_transform(R, t):
    # R: [..., 3, 3], t: [..., 3]; preserve batch dimensions.
    T = torch.eye(4, dtype=R.dtype, device=R.device).expand(R.shape[:-2] + (4, 4)).clone()
    T[..., :3, :3] = R
    T[..., :3, 3] = t
    return T

def compose(T_A_B, T_B_C):
    # Matrix multiplication composes B->C after A<-B.
    return T_A_B @ T_B_C

def inverse_transform(T_A_B):
    # For a rigid transform, inverse rotation is transpose.
    R = T_A_B[..., :3, :3]
    t = T_A_B[..., :3, 3]
    T_B_A = torch.zeros_like(T_A_B)
    R_T = R.transpose(-2, -1)
    T_B_A[..., :3, :3] = R_T
    T_B_A[..., :3, 3] = -(R_T @ t.unsqueeze(-1)).squeeze(-1)
    T_B_A[..., 3, 3] = 1
    return T_B_A
```

实际代码还应检查 `RᵀR≈I`、`det(R)≈1`、底行 `[0,0,0,1]`、finite、单位和 frame metadata。若矩阵包含 scale/shear，则不能使用 rigid inverse 公式。

## 3. 点、方向与 pose

- **point**：齐次坐标 ([x,y,z,1])，平移会生效。
- **direction/vector**：齐次坐标 ([x,y,z,0])，只旋转不平移。
- **pose**：位置和姿态一起变换；姿态表示可用 rotation matrix/quaternion/SE(3)，不能只对 xyz 乘矩阵就声称 pose 完整变换。

## 4. 逆变换与 roundtrip

对 rigid transform：

\[
(T^A_B)^{-1}=\begin{bmatrix}R^\top&-R^\top t\\0&1\end{bmatrix}.
\]

roundtrip 测试：随机或已知 (p_B)，先 (p_A=T^A_Bp_B)，再 (p'_B=(T^A_B)^{-1}p_A)，检查 (|p'_B-p_B|) 小于阈值。还要测试 `compose(T_A_B,T_B_C) @ p_C` 与先后两次变换相同。

## 5. Frame、单位与时间

ROS REP-103/105 提供右手系、SI 单位和移动平台 frame 语义参照，但项目必须记录自己的 `frame_id、parent、child、timestamp、calibration_revision、source`。`camera→base` 与 `base→camera` 方向、米/毫米、光学轴 convention、旧 TF 和新标定 revision 都是高危边界。

如果 observation 在 (	au_o) 捕获，而 TF 在 (	au_{tf}) 更新，不能默认二者同步；移动机器人应使用 capture-time TF 或插值，并把时间差/pose uncertainty 进入 downstream gate。

## 6. 测试矩阵

| 测试 | 断言 | 典型 bug |
| --- | --- | --- |
| identity | 不改变点/pose | 底行/shape 错 |
| translation | 点平移、direction 不平移 | w 写错 |
| known rotation | 90° 方向符合右手系 | 轴/方向反 |
| composition | 右到左与逐步结果一致 | 乘法顺序错 |
| inverse roundtrip | 点误差在阈值内 | 平移逆公式错 |
| rotation check | `RᵀR≈I, det≈1` | 非刚体矩阵误用 |
| batch | `[...,4,4]` 广播正确 | 只支持单矩阵 |
| unit/frame mismatch | smoke 能显式失败 | 米/mm 或 label 静默错 |
| timestamp revision | 使用 capture-time TF | 取 latest TF 造成漂移 |

## 7. VLA 映射

PER-002 的 pixel→camera→target、grounding point、waypoint/subgoal、camera/base/world action 都依赖 transform contract。transform 正确只证明几何链路，不证明 depth、planner、controller、grasp 或导航闭环正确；应分层记录 projection、calibration、TF、planner/controller 和 safety evidence。

## 8. 项目挂钩与真实性边界

OPD 可连接 point/box/text 坐标协议；WAM/OpenPiVLA 可连接 camera/action packaging；Robot Harness 可连接 frame-aware tool schema；UWM/LIBERO 可连接 camera/state/action shape。当前没有本地 CODE-VLA-005 标定/TF parity 或闭环 artifact，不能把通用矩阵代码写成项目贡献或 3D 成功。

## 9. 结论与下一步

手写 transform 的高分答案是：明确 (T^A_B) 方向、右到左组合、rigid inverse、point/vector/pose 的 w 差异、frame/单位/时间戳和 roundtrip 测试。矩阵运算正确只是几何层证据，不等于机器人执行成功。

下一步：保持 `CODE-VLA-005` 题卡为 `unseen`，进行一次白板/实现练习，或补充 TF/calibration roundtrip artifact。

## References

1. [CODE-005 Source Freeze](../sources/vol_08_code005_transform_source_freeze.html)。
2. [ROS REP-103](https://www.ros.org/reps/rep-0103.html)、[REP-105](https://www.ros.org/reps/rep-0105.html) 与 SciPy [`Rotation`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html)。
3. 本仓库 [VOL 06 PER-002](../knowledge/vol_06_per002_3d_lift_frame.html)。
