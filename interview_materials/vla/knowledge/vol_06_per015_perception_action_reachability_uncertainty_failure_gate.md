# VOL 06 Perception / Grounding / Navigation：Perception→Action、Reachability、Uncertainty 与 Failure Gate（PER-015）

> 状态：`drafted / VLA-PER-015 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-014` 3D semantic target、`VLA-PER-002` frame/lift、VOL 03 action/controller contract；后续：`VLA-PER-016` localization/SLAM drift、`VLA-PER-019` navigation evaluation/failure。  
> 来源入口：[PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Source Freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)。本页只把已冻结证据转成可教学、可诊断、可面试回答的知识；对应一张原子题卡已在独立bounded slice同步并保持`unseen`，不创建训练状态，也不改变任何mastery。

## 问题（Question）

面试官问“VLA已经找到了目标，怎样把它变成机器人能安全执行的动作”时，最危险的回答是“把3D坐标送给IK，再做碰撞检测”。可靠回答必须先把semantic target转成带frame、unit、timestamp、tool和controller合同的action target，再按workspace、IK residual、joint limit、singularity、self/environment collision、clearance、trajectory dynamics、uncertainty和controller precheck逐层fail closed；任何一层未知都不能默认为pass，最终通过也只得到controller-ready candidate，而不是robot success。

本节点主链：

```text
PER-014 semantic target / pose / mask
  -> identity: frame / unit / timestamp / revision
  -> action target: tool / approach / gripper / controller
  -> workspace / IK / joint bounds / singularity
  -> state + edge collision / robust clearance
  -> trajectory timing / controller precheck
  -> calibrated uncertainty / abstention / fallback
  -> controller-ready candidate
  -> execution feedback (not task success yet)
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-015负责 |
| --- | --- | --- |
| PER-014 | 3D entity、relation、semantic target、score、metric | 判断semantic target能否成为controller-ready candidate |
| PER-002/003 | depth、calibration、frame、multi-view/time lineage | 消费并校验身份；不修复错误TF、pose或时间同步 |
| VOL 03 | action token/chunk、normalization、policy head与controller接口 | 不训练head；验证输出shape/semantics/order/unit/time |
| PER-016 | localization、odometry、SLAM、map-frame drift | 不做SLAM；只拒绝stale或revision不一致的输入 |
| PER-019 | episode、collision/stop、success与统计评估 | 不从单个静态candidate推出benchmark/robot success |

PER-015是接口与可行性节点，不是完整机器人安全认证。接触力、硬件急停、functional safety、真实人机环境法规仍在本页范围之外。

## 1. 30秒直觉：目标不是动作，通过不是成功

一个可靠的30秒回答是：

> 感知输出只是semantic target，我先补齐frame、unit、timestamp、tool和controller schema，把它变成typed action target。然后用workspace做cheap reject，IK返回后重算FK residual，检查joint limit和Jacobian最小奇异值；再对goal state和整条edge做self/environment collision与uncertainty-inflated clearance；几何路径还要通过velocity、acceleration、current-state和controller joint/order/unit/time检查。语义、几何或执行不确定性超过校准风险预算时就ask、re-perceive、replan或stop，不能拿top-1硬执行。所有gate通过只得到controller-ready candidate，执行反馈和任务成功要另算。

这段回答先封住十个偷换：

1. semantic target被当成controller action；
2. 点在粗workspace里被当成指定姿态可达；
3. IK solver返回数组被当成有效解；
4. 数学IK存在被当成joint-limit-aware IK存在；
5. goal无碰撞被当成整条path无碰撞；
6. nominal clearance被当成有感知误差时仍安全；
7. geometric path被当成满足velocity/acceleration的trajectory；
8. action shape相同被当成axis/unit/semantics相同；
9. 未校准confidence被当成逐样本安全概率；
10. candidate accepted被当成robot/task success。

## 2. Typed Perception→Action Manifest

### 2.1 最小 Schema

```json
{
  "candidate_id": "scene/query/proposal revision",
  "semantic_source": {
    "artifact_sha256": "...",
    "query": "pick the red mug",
    "target_id": "mug-17",
    "score_type": "cosine | logit | calibrated_set",
    "raw_score_and_threshold": [0.73, 0.60]
  },
  "target": {
    "type": "point | pose | grasp | pick_place | trajectory",
    "frame": "camera | base | world | map",
    "axis_unit": "x-forward/y-left/z-up, meter/radian",
    "pose_or_waypoints": [],
    "tool_frame": "tcp",
    "timestamp_ns": 0,
    "age_deadline_ms": [0, 100],
    "covariance": []
  },
  "robot_contract": {
    "robot_model_sha256": "...",
    "planning_group": "arm",
    "end_effector": "gripper",
    "joint_order": [],
    "joint_position_velocity_acceleration_limits": [],
    "controller_name": "joint_trajectory_controller",
    "controller_axis_unit_rate": "..., rad, 100Hz"
  },
  "scene_contract": {
    "planning_scene_sha256": "...",
    "collision_geometry_revision": "...",
    "allowed_collision_matrix_sha256": "...",
    "padding_and_scale": [],
    "motion_validation_resolution": 0.0
  },
  "risk_contract": {
    "calibration_split_revision": "...",
    "risk_budget_alpha": 0.05,
    "uncertainty_inflation": [],
    "allowed_outcomes": ["accept", "replan", "ask_for_help", "stop", "reject"]
  }
}
```

### 2.2 为什么Manifest属于结果身份

同一个3D pose在`camera`与`base` frame中数值和语义不同；同一个7D向量可能是Cartesian delta，也可能是joint position；同一条path在不同collision mesh、allowed-collision matrix、padding或motion resolution下可从pass变reject。缺少这些revision时，结果不可复算，也无法解释失败来自perception、planning还是controller。

## 3. 九层Fail-closed Gate

总gate可写为：

\[
G =
G_{\mathrm{identity}}
\land G_{\mathrm{workspace}}
\land G_{\mathrm{IK}}
\land G_{\mathrm{bounds}}
\land G_{\mathrm{singularity}}
\land G_{\mathrm{collision}}
\land G_{\mathrm{trajectory}}
\land G_{\mathrm{uncertainty}}
\land G_{\mathrm{controller}}.
\]

变量解释：\(G_k\)是第\(k\)层布尔gate，但实现中必须保留`pass/fail/not_checked`三态与evidence；`not_checked`在fail-closed模式下不能执行。直觉是整条链是串联系统，任一层未知都不能靠后层“平均掉”。实现映射：source freeze中的typed manifest和reason taxonomy分别给每个gate绑定input revision、threshold与recovery action。

| Gate | 核心问题 | 主要输入 | 失败去向 |
| --- | --- | --- | --- |
| identity | frame/unit/time/revision齐全吗 | target manifest | reject / ask |
| workspace | 粗几何必要条件满足吗 | robot/tool geometry | reject / base reposition |
| IK | 位姿残差在阈值内吗 | target pose、solver | alternate branch / reject |
| bounds | q在joint limits内吗 | robot model | branch / reject |
| singularity | conditioning可接受吗 | Jacobian | change pose / replan |
| collision | state与edge无碰撞吗 | scene、ACM、resolution | replan / reject |
| trajectory | continuity与动态约束满足吗 | waypoints、dt、limits | re-time / replan |
| uncertainty | 校准风险预算满足吗 | score/covariance/calibration | ask / re-perceive |
| controller | shape/semantics/order/unit/state/status对吗 | controller contract | stop / reject |

## 4. Semantic Target → Action Target

PER-014可给出entity ID、box/mask、3D point或pose与semantic score。PER-015需要把它转成任务原子：

```text
semantic_target = {
  entity_id, pose_or_region, frame, semantic_score, timestamp
}

action_target = {
  tool_pose, pregrasp_pose, approach_direction, gripper_command,
  robot_model, planning_group, joint/controller contract
}
```

Transporter Networks与CLIPort提供清晰范例：从heightmap上预测pick，再以pick-conditioned correlation预测place；CLIPort加入language-conditioned semantic/spatial streams。它们说明perception如何输出pick/place proposal，但不自动提供：

- tool-center-point transform；
- grasp width、surface normal、force closure；
- joint-limit-aware IK branch；
- self/environment collision；
- velocity/acceleration timestamps；
- real controller status。

所以模型输出`pick/place pose`时，面试回答应主动说“proposal进入feasibility gate”，而不是“模型直接控制机械臂”。

## 5. Workspace：Cheap Reject，不是最终证明

### 5.1 二连杆可达环

对link length \(l_1,l_2\)和目标位置\(\mathbf p\)，二维二连杆的位置可达条件为：

\[
|l_1-l_2|
\le \|\mathbf p\|_2
\le l_1+l_2.
\]

变量解释：\(\|\mathbf p\|_2\)是目标到base的半径；内半径来自两杆相折，外半径来自两杆伸直。直觉是先用极便宜的几何条件拒绝明显不可能目标。实现映射：deterministic probe固定\(l_1=1,l_2=0.7,r=1.8\)，因上界为1.7而直接`OUTSIDE_WORKSPACE`。

### 5.2 四级Reachability

| 层 | 新增约束 | 为什么上一层不够 |
| --- | --- | --- |
| geometry workspace | link length、粗joint range | 不含orientation/tool |
| task workspace | tool、approach、support surface | 不含current state/path |
| current-state reachability | 当前q、branch、obstacle、path | 不含model/sensor uncertainty |
| robust reachability | covariance、tracking error、inflation | nominal pass可能变reject |

一个点在workspace内，指定orientation仍可能无解；换gripper、base pose或URDF后，旧reachability map也失效。

## 6. IK：返回值之后还要验证Residual

### 6.1 SE(3) Pose Error

对目标位姿\(T^*\)与候选关节\(\mathbf q\)的forward kinematics \(T(\mathbf q)\)，body-frame误差可写为：

\[
\mathbf e(\mathbf q)
=
\operatorname{se3ToVec}
\left(
\log\!\left(T(\mathbf q)^{-1}T^*\right)
\right).
\]

变量解释：\(\mathbf e\in\mathbb R^6\)含rotation与translation误差；\(T(\mathbf q)\)来自FK。直觉是solver说“成功”后，用独立FK重新计算“实际到了哪里”。实现映射：Modern Robotics固定`IKinBody/IKinSpace`分别以`eomg`和`ev`终止；工程gate也应分开记录角度与位置tolerance，不能只看一个return code。

### 6.2 Newton–Raphson 与Pseudoinverse

数值IK的一步可写成：

\[
\Delta\mathbf q
=
J(\mathbf q)^\dagger \mathbf e,
\qquad
\mathbf q_{k+1}=\mathbf q_k+\Delta\mathbf q.
\]

变量解释：\(J^\dagger\)是Jacobian pseudoinverse，\(\mathbf e\)是task-space error。直觉是用局部线性近似把末端误差映射到关节修正。实现映射：Modern Robotics教学代码直接迭代该结构；README明确代码优先可读性而非robustness，所以production系统还需bounds、timeout、branch、collision与conditioning。

常见失败：

1. 初值落入错误branch或局部极小；
2. translation通过但rotation超阈值；
3. solver timeout却留下“看起来合理”的最后iterate；
4. q被clamp到limit后未重算residual；
5. 单位或frame错误导致“稳定收敛到错误目标”。

## 7. Joint Limit 与TRAC-IK

数学IK解存在，不代表受限IK解存在。最小合同是：

\[
\mathbf q_{\min}
\le \mathbf q
\le \mathbf q_{\max}.
\]

变量解释：上下界来自冻结robot model；continuous joint与bounded revolute joint要分开处理。直觉是“末端能到”还要问“关节是否允许这样到”。实现映射：TRAC-IK固定代码显式接收`q_min/q_max`；KDL-TL会处理越界与随机重启，NLOpt路径设置lower/upper bounds。

TRAC-IK并发运行KDL-style路径与SQP/NLOpt路径，可改善joint-limit附近的求解率，但官方README明确：

- solver不使用mesh判断self-collision；
- IK solution不保证environment collision-free；
- 多解排序不等于轨迹branch连续；
- timeout/success统计不等于具体部署task success。

deterministic probe中\(\mathbf q=[\pi/2,0]\)满足纯几何目标，但q1 limit为`[-1,1]`，因此必须`JOINT_LIMIT`拒绝，不能clamp后直接执行。

## 8. Singularity、Conditioning 与Manipulability

对Jacobian做SVD：

\[
J(\mathbf q)=U\Sigma V^\top,
\qquad
\sigma_{\min}(J)<\tau_\sigma
\Rightarrow \text{near singular}.
\]

变量解释：\(\sigma_{\min}\)是最小奇异值，\(\tau_\sigma\)是协议阈值。直觉是某个末端运动方向几乎无法由关节产生，微小末端速度会要求巨大关节速度。实现映射：MoveIt `RobotState::getJacobian`或Modern Robotics Jacobian可生成矩阵；gate必须记录joint scaling、task dimensions和阈值。

可选的Yoshikawa manipulability为：

\[
w(\mathbf q)=\sqrt{\det\!\left(JJ^\top\right)}
=\prod_i \sigma_i.
\]

变量解释：\(w\)越小通常越接近rank loss。直觉是末端局部速度椭球体积缩小。实现映射：它适合排序多个IK candidates，不应取代hard bounds、collision或velocity check；rotation与translation单位混合时，数值需要scale，否则不同实现不可直接比较。

二维2R在完全伸直\(\mathbf q=[0,0]\)时，deterministic probe得到\(\sigma_{\min}=0\)，因此即使目标位置可达也要change pose或replan。

## 9. Collision：State Validity 与Motion Validity

### 9.1 Goal State无碰撞仍不够

要区分：

```text
state validity  : q 本身是否满足bounds/collision/constraints
motion validity : q_a -> q_b 的整条edge是否有效
path validity   : 所有states与edges是否有效
```

RRT-Connect论文把free configuration space作为搜索域；OMPL固定`RRTConnect.cpp`在扩展时调用`isValid/checkMotion`。因此“RRT-Connect生成collision-free path”的前提是集成方提供了正确的state validity、motion validator、geometry与resolution。

### 9.2 MoveIt PlanningScene

MoveIt固定代码中：

- `RobotState::satisfiesBounds`检查joint bounds；
- `RobotState::setFromIK`调用kinematics solver；
- `PlanningScene::checkCollision/isStateColliding`处理collision；
- `PlanningScene::isStateValid`组合collision与constraints；
- trajectory相关路径遍历waypoints。

这些API存在不等于部署正确。还要冻结URDF/SRDF、attached object、tool geometry、allowed-collision matrix、padding、octomap/scene revision和current state。

### 9.3 Discrete Motion Validation

OMPL `DiscreteMotionValidator`依据`validSegmentCount`插值检查edge。步长过粗会穿过薄障碍；步长极细会增加开销。deterministic segment/AABB probe中端点都在box外，但segment穿过box，因此只查端点会产生false pass。

## 10. Clearance 与Uncertainty Inflation

robust clearance gate可写为：

\[
d_{\min}\!\left(\mathcal R(\mathbf q),\mathcal O\right)
>
r_{\mathrm{robot}}
+m_{\mathrm{model}}
+m_{\mathrm{uncertainty}}.
\]

变量解释：\(\mathcal R(\mathbf q)\)是机器人几何，\(\mathcal O\)是障碍，\(m_{\mathrm{model}}\)覆盖mesh/标定误差，\(m_{\mathrm{uncertainty}}\)覆盖target/obstacle covariance。直觉是不能用“零误差的薄模型”贴障碍执行。实现映射：可通过collision padding、scale或显式inflated geometry实现，但必须把膨胀量与scene revision写入manifest。

deterministic probe中path位于y=0.25：nominal margin 0.10时不碰撞，uncertainty inflation增至0.20后碰撞，结论从pass翻为reject。这证明covariance不是只写日志的附加字段，而会改变动作决策。

常见错误：

- 对target加covariance，却不对obstacle/robot model加；
- 只在goal pose算clearance，不检查swept path；
- 把visual bbox边界当physical collision mesh；
- 感知分数低时只降速度，却不增加margin或abstain。

## 11. Planning 与RRT-Connect

RRT-Connect维护从start与goal生长的两棵树，`EXTEND`向sample推进，`CONNECT`贪心尝试连接另一棵树。它适合高维single-query planning，但面试中必须补四点：

1. sampling planner是probabilistically complete类思想，不承诺有限时间一定找到解；
2. 找不到路径不一定证明路径不存在，可能是timeout/resolution/sampler问题；
3. 找到几何path不代表满足dynamics或controller limits；
4. shortcut/smoothing后必须重新做motion validation。

OMPL把具体robot collision checker留给集成层，这是清晰的责任边界：planner负责搜索，MoveIt PlanningScene等负责physical validity。

## 12. Trajectory：Geometry、Continuity 与Time

几何waypoints进入controller前至少满足：

\[
\mathbf q_{\min}\le\mathbf q_t\le\mathbf q_{\max},\qquad
|\dot{\mathbf q}_t|\le\dot{\mathbf q}_{\max},\qquad
|\ddot{\mathbf q}_t|\le\ddot{\mathbf q}_{\max}.
\]

变量解释：\(\mathbf q_t,\dot{\mathbf q}_t,\ddot{\mathbf q}_t\)是位置、速度与加速度；上限来自joint/controller contract。直觉是空间中平滑的线，若时间给得太短仍不可执行。实现映射：MoveIt固定Time-Optimal Trajectory Generation接收velocity/acceleration limits并生成timestamps；deterministic probe固定q `[0,.5,1.5]`、dt `.1`，得到vmax 10、amax 50，必须`DYNAMIC_LIMIT`。

还要检查：

- branch continuity：相邻IK解不能跳到另一branch；
- unwrap：continuous joint不能错误跨\(2\pi\)；
- jerk与controller interpolation；
- start-state tolerance；
- partial execution后的replan起点；
- attached object和scene在trajectory期间是否变化。

## 13. Controller Contract：Shape相同仍可能语义错

| 维度 | 必须冻结 | 典型静默错误 |
| --- | --- | --- |
| shape | `H×D`、valid dims、mask、joint count | 72D被截成16D |
| semantics | absolute/delta/velocity、joint/cartesian | delta当absolute |
| order | xyz/rpy/gripper或joint names | roll与gripper错位 |
| unit | m/mm、rad/deg、normalized/raw | 数量级错 |
| time | Hz、dt、timestamp、chunk H、replan K | stale action继续执行 |
| state | current q与start tolerance | 轨迹从错误状态起步 |
| status | ready/abort/timeout/cancel/result | failure被包装为success |

deterministic schema probe期望7D `xyz_rpy_grip/m_rad`，却收到12D `dual_arm_plus_base/normalized`，必须`CONTROLLER_SCHEMA`拒绝。安全实现不能为了“能跑”而silently slice/pad。

MoveIt `TrajectoryExecutionManager`在执行前验证current joint state、trajectory joint集合和起点容差，并保留controller timeout/status。VLA policy server的成功返回只说明网络调用成功，不说明controller接受或完成了动作。

## 14. Action Chunk 与Staleness

若policy一次预测horizon \(H\)，系统每次只执行前\(K\)步再replan，则第\(j\)步action的age近似为：

\[
\operatorname{age}(a_j)
=
t_{\mathrm{execute},j}
-t_{\mathrm{observe}}.
\]

变量解释：\(t_{\mathrm{observe}}\)是生成chunk所依据观测时间，\(t_{\mathrm{execute},j}\)是第\(j\)步实际执行时刻。直觉是chunk越靠后，依赖的世界状态越旧。实现映射：manifest应记录observation timestamp、queue、H/K/Hz和deadline；PER-015 probe中target age 240ms超过100ms deadline，直接`TARGET_STALE`。

每次replan前要重新核验：

- scene revision和attached object；
- current robot state；
- 剩余target/action age；
- controller queue是否已cancel/flush；
- 新轨迹与已执行prefix的continuity。

## 15. 三类Uncertainty不能混成一个Confidence

| 类型 | 来源 | 可见信号 | 合适动作 |
| --- | --- | --- | --- |
| semantic | 多个对象/指令解释 | candidate set、class/LLM score | ask / clarify |
| geometric | depth/pose/calibration/shape | covariance、view disagreement | re-perceive / inflate / replan |
| execution | latency/tracking/contact/controller | state error、timeout、status | slow/stop/recover |

semantic cosine高不能证明geometry准确；geometry covariance小不能证明controller ready；controller online也不能修复选错对象。first-divergence diagnosis必须从最早失败层开始。

一个实用risk contract至少包含：

- calibration split与revision；
- target error definition；
- desired coverage/risk budget；
- uncertainty到margin或abstention的映射；
- distribution-shift detector；
- `accept/replan/ask/stop/reject`状态机。

## 16. KnowNo 与Conformal Prediction

### 16.1 Calibration

对calibration样本\((x_i,y_i)\)，以正确option的score \(f(x_i)_{y_i}\)构造nonconformity：

\[
s_i=1-f(x_i)_{y_i},
\qquad
\hat q=
\operatorname{Quantile}_{\lceil(N+1)(1-\epsilon)\rceil/N}
\{s_i\}_{i=1}^{N}.
\]

变量解释：\(N\)是calibration size，\(\epsilon\)是目标error level，\(\hat q\)是higher quantile。直觉是用历史正确答案的“低置信程度”确定test threshold。实现映射：KnowNo官方MobileManipulation/Tabletop notebooks用`np.quantile(..., method='higher')`计算该阈值。

test prediction set为：

\[
C(x)=\{y:f(x)_y\ge 1-\hat q\}.
\]

变量解释：\(C(x)\)保留所有超过校准threshold的options。直觉是当多个解释都合理时，不强迫模型假装只知道一个。实现映射：KnowNo notebook在set非singleton时触发human help；mobile版本还把“none of the above” option进入set视为help。

### 16.2 保证边界

在exchangeability等条件下，conformal prediction提供marginal coverage目标，而不是：

- 每一个单样本都有相同条件成功率；
- collision-free或硬件安全保证；
- distribution shift下阈值永久有效；
- 错误label、漏候选或parser bug免疫；
- help之后human一定选择正确。

因此PER-015可以借鉴“集合预测→abstain”的结构，但low-level collision/trajectory仍要独立hard gate。

## 17. Abstention、Fallback 与Recovery状态机

推荐状态：

```text
ACCEPT       all checked gates pass; return candidate only
REPLAN       target valid, current path/clearance/dynamics fail
ASK          semantic ambiguity or calibrated set non-singleton
REPERCEIVE   target stale or geometry uncertainty too large
STOP         controller/status/state unknown or execution unsafe
REJECT       schema/workspace/IK/bounds hard failure
```

fallback不是默认动作，而是受限状态转移：

```text
semantic ambiguous -> ask / re-perceive
workspace or IK fail -> alternate proposal / branch / base reposition
collision fail -> update scene and replan
trajectory fail -> re-time or shorten horizon
controller mismatch -> reject; never silently slice/pad
execution timeout -> cancel -> verify stop -> read state -> recover
```

每条transition必须有retry上限、timeout、cancel acknowledgement和fresh-state check。否则“自动恢复”可能变成无限replan或执行旧轨迹。

## 18. 十个Deterministic Probes

| Probe | 固定输入 | 结果 | 教学结论 |
| --- | --- | --- | --- |
| workspace annulus | \(l_1=1,l_2=.7,r=1.8\) | range `[.3,1.7]`，reject | cheap必要条件 |
| IK residual | target `[1.3,.2]`，q `[.1,-.1]` | residual `.407507m>.01` | return后重算FK |
| joint limit | q `[π/2,0]`，q1 `[-1,1]` | reject | 几何解不等于受限解 |
| singularity | 2R q `[0,0]` | \(\sigma_{\min}=0\) | 可达不等于well-conditioned |
| segment/AABB | edge穿过box | collision true | 端点pass不够 |
| clearance inflation | nominal `.10`，inflated `.20` | pass翻reject | covariance改变决策 |
| dynamics | q `[0,.5,1.5]`，dt `.1` | vmax 10、amax 50 | path不等于trajectory |
| abstention | risk upper `.12`，alpha `.05` | ask | 风险超预算不取top-1 |
| stale target | age 240ms，deadline 100ms | reject | 时间属于身份 |
| controller schema | expected 7D，got 12D | reject | dim/order/unit fail closed |

10个probe的deterministic oracle结果为`10/10 expected decisions matched`。它们只验证合同逻辑，不是MoveIt、TRAC-IK、CLIPort或KnowNo benchmark复现。

## 19. First-divergence Failure Diagnosis

| 表面症状 | 第一检查层 | 关键证据 | 常见误诊 |
| --- | --- | --- | --- |
| 抓错对象 | semantic identity | candidate/raw scores/query | 调IK参数 |
| pose方向错 | frame/tool transform | TF、axis、tcp | 加planning time |
| IK timeout | workspace/IK | target pose、seed、residual | 直接称模型差 |
| q贴limit | bounds/branch | q min/max、alternate solutions | clamp后执行 |
| 末端抖动 | singularity/controller | sigma、qdot、rate | 只平滑视觉 |
| 起终点都安全却碰撞 | motion validity | edge samples/resolution | 只查goal |
| 靠障碍偶发失败 | clearance/uncertainty | covariance、padding | 只降速度 |
| simulator能跑真机不能 | controller schema | order/unit/rate/driver | 归因Sim2Real大词 |
| chunk后段发散 | staleness/replan | H/K/Hz/age/state | 只改action loss |
| policy server返回但不动 | execution precheck | controller status/joints/start | 报推理成功 |
| help率异常高 | calibration/option bias | split、qhat、set size | 降threshold硬执行 |
| 单次success但总体差 | evaluation downstream | episode denominator/failure codes | 把gate pass当success |

诊断顺序：

```text
identity/time
 -> semantic target
 -> workspace
 -> IK residual/bounds/singularity
 -> state/edge collision + clearance
 -> timing/controller schema/status
 -> calibrated uncertainty
 -> execution/contact/task outcome
```

## 20. Fail-closed Pseudocode

```python
def perception_to_action_gate(semantic_target, manifest, robot, scene, controller):
    # 1. Identity first: never guess frame, unit, timestamp, or revision.
    require_fields(semantic_target, ["frame", "axis_unit", "timestamp_ns", "artifact_sha256"])
    require_fields(manifest, ["robot_contract", "scene_contract", "risk_contract"])
    if age_ms(semantic_target) > manifest.target.age_deadline_ms:
        return {"status": "reperceive", "reason": "TARGET_STALE"}

    # 2. Convert entity/pose into a typed tool/action target.
    candidate = build_action_target(semantic_target, manifest)
    if not controller.schema_matches(candidate):
        return {"status": "reject", "reason": "CONTROLLER_SCHEMA"}

    # 3. Cheap workspace reject before expensive IK.
    if not robot.workspace_contains(candidate.tool_pose):
        return {"status": "reject", "reason": "OUTSIDE_WORKSPACE"}

    # 4. Verify every IK result independently with FK, bounds, and SVD.
    valid_q = []
    for q in robot.solve_ik(candidate.tool_pose, timeout=manifest.ik_timeout):
        if pose_residual(robot.fk(q), candidate.tool_pose) > manifest.ik_tolerance:
            continue
        if not robot.satisfies_bounds(q):
            continue
        if min_singular_value(robot.jacobian(q)) < manifest.sigma_min:
            continue
        valid_q.append(q)
    if not valid_q:
        return {"status": "reject", "reason": "IK_NO_VALID_SOLUTION"}

    # 5. Check state and every edge with one frozen planning scene.
    paths = plan_from_current_state(valid_q, scene, manifest.motion_resolution)
    paths = [p for p in paths if collision_free_path(p, scene)]
    paths = [p for p in paths if robust_clearance(p, scene, candidate.covariance)]
    if not paths:
        return {"status": "replan", "reason": "COLLISION_OR_CLEARANCE"}

    # 6. Convert geometry to a timed trajectory and validate current controller state.
    timed = time_parameterize(paths, robot.velocity_limits, robot.acceleration_limits)
    if not timed:
        return {"status": "replan", "reason": "DYNAMIC_LIMIT"}
    if not controller.precheck(timed, current_state=robot.current_state()):
        return {"status": "stop", "reason": "EXECUTION_PRECHECK"}

    # 7. Unknown or over-budget risk is not a pass.
    decision = calibrated_risk_decision(candidate, timed, manifest.risk_contract)
    if decision == "ask":
        return {"status": "ask_for_help", "reason": "UNCERTAIN"}
    if decision != "accept":
        return {"status": "reject", "reason": "RISK_BUDGET"}

    # 8. Return a candidate only; execution feedback owns robot/task success.
    return {
        "status": "controller_ready_candidate",
        "trajectory": timed[0],
        "checked_revisions": manifest.revisions(),
        "robot_success": None
    }
```

伪代码是面试与目标系统合同，不是五个本地项目已有实现。真实系统还需并发scene update、force/contact gate、cancel acknowledgement、hardware stop与episode logger。

## 21. Public Method → Code Mapping

| 机制 | 固定实现 | 面试可讲 | 不能反推 |
| --- | --- | --- | --- |
| numerical IK | Modern Robotics `IKinBody/IKinSpace` | residual/Jacobian/pseudoinverse | production robustness |
| bounded IK | TRAC-IK KDL-TL + NLOpt | q bounds、dual solver、timeout | collision-free path |
| planning scene | MoveIt RobotState/PlanningScene | bounds、IK、collision、constraints | URDF/scene一定正确 |
| sampling planner | OMPL RRTConnect/MotionValidator | state vs edge validity | finite-time必有解 |
| trajectory/execution | MoveIt TOTG/ExecutionManager | limits、timestamps、precheck/status | task success |
| pick/place proposal | Transporter/CLIPort | perception→action atom | reachable/control-ready |
| calibrated abstention | KnowNo notebooks | higher quantile、prediction set、help | low-level safety证书 |

这张表建立公开机制的source-to-code桥，不证明本地项目用了固定commit，也不证明候选人ownership。

## 22. OPD 与Robot Harness：最容易被过度包装的两类Hook

### 22.1 OPD

OPD direct evidence支持2D point/box/relation supervision与semantic-nav box数据构造。项目中的`fallback`命中是system prompt、model path或text cleaning fallback，不是physical recovery。

安全表述：

> OPD可以为gate提供2D semantic target或grounding score，但当前没有robot/tool model、metric 3D action target、IK/collision trace或controller gate。我会把它讲成perception upstream，不讲成已闭环执行。

### 22.2 Robot Harness

Robot Harness固定文件支持tool scope、锁、cancel、poll/timeout、best-effort compensation，以及2D occupancy/PCD/state bridge。map/state fallback不是fresh sensing；第三方SenseBot底盘controller目录也不自动证明当前runtime integration、manipulator scope或候选人ownership。

安全表述：

> Harness的强项是上层tool/runtime约束和取消补偿，不是机械臂IK与mesh collision。tool sandbox通过只能说明调用合同更干净，不能替代低层controller、接触和真实机器人成功。

## 23. OpenPiVLA、WAM、UWM 的Action Interface边界

### 23.1 OpenPiVLA

本地formal trainer把action window序列化为assistant JSON并做full-chat causal CE；formal package仍缺generation/parser/controller。official-checkpoint ALOHA/LIBERO diagnostics是平行lineage。deprecated MuJoCo adapter文件自身明确缺official embodiment、controller、IK、workspace和contact semantics。

因此可讲action schema与diagnostic，不能说formal Qwen已经通过PER-015 gate。

### 23.2 WAM

WAM diagnostic可见7D→12D环境action拼接、dim mismatch hard error、OSC_POSE字段与有限action trace。它们适合检查shape/order/normalizer/controller边界；episode仍失败，缺robot model、planning scene、IK/collision/TOTG报告，不能归因reachability或collision收益。

### 23.3 UWM

UWM/LIBERO固定脚本有`action_len=16/action_dim=7`、warmup与env.step；RoboCasa GT replay明确定位为action-order/controller probe，不是demo success oracle。74.4%等协议结果不能反向证明通用feasibility gate。

## 24. 五项目 Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 升级所需artifact |
| --- | --- | --- | --- |
| OPD | 2D semantic target/box/point可作为上游输入 | 已转成reachable manipulation | typed target、robot/tool、IK/collision trace |
| Robot Harness | tool scope、timeout/cancel/compensation、map bridge | sandbox等于物理执行安全 | controller/trajectory/collision logs、ownership |
| OpenPiVLA | action serialization与official baseline diagnostics | formal Qwen已闭环parser/controller/IK | strict parser、axis/unit/norm、roundtrip、episodes |
| WAM | OSC_POSE/action trace与shape诊断 | 已定位reachability/collision根因 | scene/model/gate reports、paired rerun |
| UWM | 7D/16-step LIBERO与RoboCasa action-order probe | 结果证明通用gate | checkpoint/norm/controller、raw gate logs |

表述顺序必须是：

```text
public upstream mechanism
 -> local inventory
 -> local-direct file
 -> diagnostic inference
 -> missing evidence
 -> candidate ownership
```

Git author、目录名、official example或一个可运行脚本都不能替代逐文件ownership与matched result。

## 25. 两分钟结构化回答

> 我会把perception→action拆成typed interface和九层fail-closed gate。首先semantic target必须带entity、frame、unit、timestamp、score与artifact revision，再结合tool frame、approach、gripper和controller schema形成action target。先用workspace做cheap reject，但它只是必要条件；IK返回后我会独立FK重算SE(3) residual，检查joint limits和Jacobian最小奇异值。TRAC-IK能通过KDL与NLOpt双路径改善joint-limit场景，但官方边界是不做mesh self-collision。接下来区分state和motion validity：MoveIt PlanningScene负责robot/scene collision与constraints，OMPL RRT-Connect依赖外部isValid/checkMotion，resolution、ACM、padding和scene revision都是结果身份。nominal path还要用pose/collision uncertainty膨胀clearance。几何path通过后，TOTG或等价模块生成timestamps并检查velocity、acceleration；controller侧再核验H×D、absolute/delta/velocity、axis、unit、Hz、current state、timeout和status，绝不silent slice/pad。uncertainty要拆成semantic、geometric和execution三类；像KnowNo可用calibration quantile形成prediction set，非singleton就ask，但这只是marginal coverage，不替代碰撞安全。最后输出是controller-ready candidate，execution feedback和task success另算。本地五项目目前只有perception/action/interface或diagnostic hook，没有完整通用gate，所以我会明确哪些是上游方法、哪些是local direct evidence、哪些仍缺。

## 26. 高频追问

1. semantic target与action target字段有什么本质差别？
2. 为什么frame/unit/timestamp属于结果身份而不是日志字段？
3. workspace内为什么仍可能IK无解？
4. IK solver返回success后为何还要独立算FK residual？
5. rotation与translation tolerance该怎样分开？
6. pseudoinverse IK在joint limit附近为什么容易失败？
7. TRAC-IK两条solver路径分别解决什么，仍缺什么？
8. \(\sigma_{\min}\)与manipulability各有什么优缺点？
9. rotation/translation单位为什么影响condition number？
10. goal state collision-free为什么不代表path collision-free？
11. OMPL为什么不自动知道机器人collision geometry？
12. motion validation resolution太粗和太细分别有什么问题？
13. attached object与allowed collision matrix为什么会改变结果？
14. clearance inflation怎样由pose/depth uncertainty决定？
15. RRT-Connect timeout能否证明无路径？
16. geometric path为什么还要time parameterization？
17. 7D action shape一致时仍有哪些semantic mismatch？
18. action chunk的H、K、Hz和staleness怎样关联？
19. semantic/geometric/execution uncertainty为何不能用一个confidence？
20. KnowNo的marginal coverage为什么不是collision safety？
21. prediction set为空、单例、多例时分别怎样处理？
22. ask-for-help与replan的触发层有什么区别？
23. cancel发出后为什么还要ack与fresh-state check？
24. 怎样用first-divergence定位“policy server返回但机器人不动”？
25. 本地五项目哪一层有direct evidence，哪一层仍缺？

## 27. 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “检测到3D点就能执行” | 缺tool/action/controller合同 | 先构造typed action target |
| “点在workspace里就是reachable” | orientation/joints/path未检查 | workspace只做cheap reject |
| “IK返回了数组就是解” | residual/bounds/singularity未知 | 独立FK与SVD验证 |
| “TRAC-IK会处理碰撞” | 官方明确不做mesh self-collision | IK后单独PlanningScene |
| “goal不碰撞就行” | edge可能穿障碍 | state+motion validity |
| “RRT-Connect找不到就是无解” | sampling/timeout/resolution影响 | 只能报本次protocol失败 |
| “clearance大于0就安全” | model/sensor/tracking有误差 | 加model+uncertainty margin |
| “path平滑就能执行” | 没有timestamps与limits | time parameterization |
| “都是7D所以接口一致” | semantics/order/unit可不同 | schema roundtrip |
| “policy server成功就是机器人成功” | 只是RPC返回 | 查controller status与episode |
| “confidence 0.9就是90%安全” | score未校准且安全层不同 | 报calibration/risk–coverage |
| “conformal保证每个样本” | 通常是marginal coverage | 明确exchangeability与边界 |
| “不确定就执行慢一点” | ambiguity可能选错对象/路径 | ask/re-perceive/replan/stop |
| “fallback就是默认动作” | unknown被强行执行 | 有界状态机、fail closed |
| “Harness已有physical safety gate” | tool sandbox不含物理闭环 | 只说上层runtime约束 |
| “WAM action trace证明IK没问题” | trace无robot/scene/gate | 只作shape/controller诊断 |

## 28. 白板 Checklist 与练习标准

能够不看材料完成：

- 画出semantic target→action target→九层gate→execution主链；
- 写出typed manifest的semantic/target/robot/scene/risk五组字段；
- 解释`pass/fail/not_checked`为何需要三态；
- 推导2R annulus并完成workspace probe；
- 写出SE(3) residual与pseudoinverse IK update；
- 区分solver return、residual、bounds与branch；
- 写出Jacobian SVD并解释\(\sigma_{\min}\)；
- 解释TRAC-IK能力与self-collision边界；
- 区分state、motion和path validity；
- 画出MoveIt PlanningScene与OMPL planner责任边界；
- 解释resolution、ACM、attached object与scene revision；
- 推导robust clearance inequality；
- 写出q/qdot/qddot约束与time parameterization；
- 列出controller shape/semantics/order/unit/time/state/status；
- 解释action chunk staleness与replan；
- 区分三类uncertainty；
- 推导conformal qhat与prediction set；
- 画出accept/replan/ask/reperceive/stop/reject状态机；
- 走完first-divergence failure diagnosis；
- 复述10个deterministic probes；
- 说清五项目truth boundary；
- 完成两分钟回答并接住至少十二个追问。

`drafted`不等于掌握。PER-015一张L3/P0题卡已生成但仍为`unseen`；只有真实口述、追问、评分、纠错后才能改变状态。当前266张题卡全部`unseen`，`coaching_state.md`不应创建。

## 29. 结论与下一步

可靠的perception→action答案不是背“IK、RRT、MoveIt”三个名词，而是建立可审计类型系统：semantic target是否有物理身份，action target是否匹配robot/tool/controller，workspace是否只做cheap reject，IK是否通过residual/bounds/singularity，state与edge是否在冻结scene中无碰撞，uncertainty inflation后是否有clearance，path是否能被time-parameterize，controller current state与schema/status是否一致，风险超过预算时是否abstain。

Modern Robotics、TRAC-IK、MoveIt、OMPL、Transporter/CLIPort和KnowNo分别支撑这条链中的不同原子，不能互相替代；尤其IK不负责mesh collision，planner不自带robot validity，pick/place proposal不是trajectory，conformal coverage不是硬件安全。

本地五项目当前最强的是perception/action/interface或diagnostic evidence：OPD为2D grounding upstream；Robot Harness为tool/runtime与map bridge；OpenPiVLA为action serialization及official diagnostics；WAM/UWM为action/controller protocol probes。没有统一typed gate、robot/tool/scene immutable bundle、IK/collision/TOTG raw report、calibrated risk–coverage、controller execution trace、matched robot episodes或ownership闭环。

`VLA-PER-015` source、knowledge与一张atomic card已在三个独立bounded slices同步；题卡保持`unseen`。下一bounded slice只冻结`VLA-PER-016` localization/odometry/SLAM/map-frame/drift source；不生成其knowledge/card，不创建`coaching_state.md`，不改变任何mastery。

## References

1. [PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Source Freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)：六份完整PDF、六个official repo/35文件、10个probe与五项目direct audit。
2. Lynch & Park, [Modern Robotics](https://hades.mech.northwestern.edu/images/7/7f/MR.pdf)；[official code@cbd41fd](https://github.com/NxRLab/ModernRobotics/tree/cbd41fdf0bf75dbd5e986d832ae14226964ff0ac)。
3. Kuffner & LaValle, [RRT-Connect](http://www.kuffner.org/james/papers/kuffner_icra2000.pdf)；[OMPL official code@eb3baca](https://github.com/ompl/ompl/tree/eb3baca772ab2c76f5943934b505751e031ff34c)。
4. Beeson & Ames, [TRAC-IK](http://irl.cs.brown.edu/pubs/trac-ik.pdf)；[official source@57057ce](https://bitbucket.org/traclabs/trac_ik/src/57057ce79ec1dd07aa5c1b46e134c701943dee6d/)。
5. Zeng et al., [Transporter Networks v2](https://arxiv.org/abs/2010.14406v2)。
6. Shridhar et al., [CLIPort v1](https://arxiv.org/abs/2109.12098v1)；[official code@2be5c47](https://github.com/cliport/cliport/tree/2be5c47b5bb9bb7040ad90693288b87b1e18e7ad)。
7. Ren et al., [KnowNo v2](https://arxiv.org/abs/2307.01928v2)；[official code@95e3a1d](https://github.com/google-research/google-research/tree/95e3a1da2d27cb9c8289f6fd3076cfed608c3c94/language_model_uncertainty)。
8. [MoveIt 2 official code@2fb8492](https://github.com/moveit/moveit2/tree/2fb8492b64ceb426d96e7f97e71846fb91394aa2)。
9. [PER-014 3D Grounding Knowledge](vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.html) 与 [VOL 03 Action Knowledge](vol_03_vla_action.html)。
10. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
