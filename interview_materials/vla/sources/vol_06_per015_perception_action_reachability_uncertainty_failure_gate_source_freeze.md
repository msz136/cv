# VOL 06 PER-015 Source Freeze：Perception→Action、Reachability、Uncertainty 与 Failure Gate

> 状态：`source_frozen / VLA-PER-015 / primary_official_checked / fail_closed_gate / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本source freeze只冻结semantic target到controller-ready candidate之间的schema、workspace/reachability、IK residual、joint limit、Jacobian singularity、self/environment collision、clearance、trajectory/controller约束、uncertainty/abstention/fallback与rejection reason；对应knowledge与一张atomic card已在后续独立bounded slices同步，题卡保持`unseen`。不重讲PER-014的3D grounding，不训练VOL 03 action head，不把静态可行性写成robot success，也不进入PER-016的SLAM/map drift。

## 问题（Question）

面试官问“VLA从视觉或语言目标到机器人动作，中间怎样判断可执行、怎样处理不确定性和失败”时，怎样把semantic target变成带frame、unit、time和controller合同的action target；怎样依次检查workspace、IK、关节限位、奇异性、碰撞、clearance、轨迹与控制器；怎样让uncertainty触发ask/replan/stop；以及本地五项目到底具备了哪一层证据。

## 1. 结论先行

1. perception输出最多是semantic target或action proposal，不是controller-ready action。二者之间至少缺frame/unit/time、robot/tool model、workspace、IK、joint limit、singularity、collision、trajectory和controller schema。
2. reachability不能只看末端点是否落在粗workspace内。还要检查姿态、IK residual、关节限位、branch、Jacobian最小奇异值、self/environment collision和整条轨迹；“solver返回数组”不等于解有效。
3. collision-free goal state不等于collision-free path。OMPL把state validity和motion validation作为外部合同；RRT-Connect依赖`checkMotion`。collision geometry、allowed-collision matrix、离散分辨率、scene revision和安全膨胀都属于结果身份。
4. 几何路径可行也不等于可执行。速度、加速度、采样时间、controller joint集合/顺序/单位、当前状态、超时、取消与执行反馈仍可让轨迹失败。
5. uncertainty不能只有一个未校准“confidence”。KnowNo用校准集的nonconformity quantile形成prediction set；非singleton时求助。其覆盖保证依赖exchangeability、校准协议和正确标签，不自动等价于collision safety或robot success。
6. failure gate应fail closed并返回结构化reason，而不是把异常吞掉后继续执行。推荐状态为`accept / replan / ask_for_help / stop / reject`，并记录首个失败层、所有失败层和输入revision。
7. 本地OPD、Robot Harness、OpenPiVLA、WAM和UWM都有某些perception/action/interface或诊断证据，但没有一个当前inventory支持完整通用gate；尤其不能用action trace、2D occupancy、tool sandbox或单次sim rollout替代IK/collision/controller闭环。

## 2. Primary Paper / Book 冻结矩阵

| 来源 | 固定版本 / 完整性 | PDF SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| Lynch & Park, [Modern Robotics](https://hades.mech.northwestern.edu/images/7/7f/MR.pdf) | 2017-05 preprint；642页；全文解析；IK视觉检查PDF p245、singularity p210 | `BA8B441E970173D0E0E017AD62861D6B453AA3BA75D8672822A4BFE5F02EEFCE` | FK/Jacobian、Newton–Raphson numerical IK、pseudoinverse、rank/singularity | collision、MoveIt runtime、本地机器人结果 |
| Kuffner & LaValle, [RRT-Connect](http://www.kuffner.org/james/papers/kuffner_icra2000.pdf) | ICRA 2000 author PDF；7页；全文解析；algorithm视觉检查p2 | `89891D6EDDCEE06CE16372CE9DED795B7DEA15FB1F2D108DD9D544C335E15825` | configuration space、state/motion collision checking、bidirectional tree connect | 完整动力学、controller execution、概率安全保证 |
| Beeson & Ames, [TRAC-IK](http://irl.cs.brown.edu/pubs/trac-ik.pdf) | Humanoids 2015 author PDF；8页；全文解析；SQP/KDL-RR视觉检查p2；DOI `10.1109/HUMANOIDS.2015.7363472` | `7A467F0C05AC0C633E47DF16FB19297A7EB8F552D2930C6F3E4970DDF1C9F967` | joint-limit-aware IK、KDL-RR与SQP并行、timeout/success比较 | self-collision、environment collision、任意姿态可解 |
| Zeng et al., [Transporter Networks](https://arxiv.org/abs/2010.14406v2) | arXiv `2010.14406v2`；22页；全文解析；pick-conditioned placement视觉检查p4 | `8FE83BED6BB955CE51C9C25F243565DF6CA4F275B3AF8D0AAB1F0ED1E6487192` | pixel/heightmap pick、pick-conditioned place、SE(2)/SE(3) action proposal | IK、collision、控制器安全与本地复现 |
| Shridhar et al., [CLIPort](https://arxiv.org/abs/2109.12098v1) | arXiv `2109.12098v1`；24页；全文解析；two-stream/action interface视觉检查p4 | `3CC19664BEABDA203CB1A1AD86659F75F60A099189820D92D59D20067C9AB003` | language-conditioned pick/place pose、semantic/spatial streams、heightmap到3D映射 | 通用机械臂可达性、真实场景collision gate |
| Ren et al., [KnowNo](https://arxiv.org/abs/2307.01928v2) | arXiv `2307.01928v2`；24页；全文解析；conformal prediction/help视觉检查p3 | `3A1B38DD460E03A19CE0307C135C58B7D3AE544C5FBC4AACC01F8A852A81F9C7` | calibration、prediction set、非singleton求助、marginal coverage | distribution shift免疫、低层collision safety、无条件robot success |

六份PDF均检查`%PDF`、`%%EOF`并用`pypdf`读取全部页面；上表方法页另行渲染PNG并视觉确认正文、算法、公式和图清晰。`pypdf`对Modern Robotics中的少数历史PDF数值对象与CLIPort交叉引用给出可恢复warning，但全页解析、EOF和方法页渲染均完成；warning不被隐去。

## 3. Official Repository 冻结矩阵

| 官方仓库 | 固定revision / date / license | 直接读取文件与SHA-256 | 支持边界 |
| --- | --- | --- | --- |
| [NxRLab/ModernRobotics](https://github.com/NxRLab/ModernRobotics/tree/cbd41fdf0bf75dbd5e986d832ae14226964ff0ac) | `cbd41fdf0bf75dbd5e986d832ae14226964ff0ac`；2026-02-17；MIT | `README 6C075DDADE24130918AE4E3F364B4CABC0D50A331924CA01F4A1CF14EB358D53`；`LICENSE 21ABC6BF4D9DDF323A1780AF31E611B7CF11B2A30B66AE2C8074574394C63578`；`core.py D523077D892569B387204C226B4292D55484ABA6BBFF1685BF1313DF41970E6B`；`IKinBody.m 8F4426BC1C51BD75388C6591C2C5F64B309AA752D090B5158357EBFCD5D72A9F`；`IKinSpace.m 42FED97DA0D006C756866BF23E592C686FF6E09D360C062C6F8E3695B2B8EABB`；`JacobianBody.m E61CFC6B127174607A8E1194715F53A07E48BA45E587BD7E78552647478E4DCE` | 教学型FK/Jacobian/IK与rotation/translation tolerance；README明确不以效率或robustness为目标 |
| [moveit/moveit2](https://github.com/moveit/moveit2/tree/2fb8492b64ceb426d96e7f97e71846fb91394aa2) | `2fb8492b64ceb426d96e7f97e71846fb91394aa2`；2026-07-09；BSD-3-Clause | `README E2BB76C08A540A78A114BB374382772C37B939E93BE1823B63AFDA5987289AA9`；`LICENSE 5C018FDE066441E1295A270B7DE5A32700735D94BA5FB9B92E0410BB8A5DCD15`；`planning_scene.cpp 18860AFFB38301A1BEFE55432CA4E1280BF6821D4A1B91A8F9398C4DAF1998F1`；`robot_state.cpp 63867A7F7CB207B53BF3DB0B817F0A2DB719011981CEA33141DDBAA89468FDCB`；`time_optimal_trajectory_generation.cpp 0B708F24D2F7C8C99D5C12CC68AB464A5C4B4E02F50CB9F3DC6E388E5511C0F5`；`trajectory_execution_manager.cpp 8D2884929E8468D34428DF69A6C89F546B8E27BED3E19D7BB1E6C343B0FFE1EB` | `setFromIK`、bounds/Jacobian、PlanningScene collision/state validity、time parameterization、current-state validation与execution status |
| [ompl/ompl](https://github.com/ompl/ompl/tree/eb3baca772ab2c76f5943934b505751e031ff34c) | `eb3baca772ab2c76f5943934b505751e031ff34c`；2026-07-10；BSD-3-Clause | `README 7AD26E7D7F938A0F245604BAA1FB3921F7F7BB371068EFBB7419F5E1E8E8E16F`；`LICENSE AAEF2BDFFCA9CA63351071448F162E44AE3C6253739D56685FCC57BBB9A642C9`；`SpaceInformation.cpp CAF432E8581D9026E90CE70747F9EC2980C07434F00AC561749E4C4CBA4BCFB5`；`DiscreteMotionValidator.cpp 660DF189A3D0AFC8263D5DC18EA45D40D4C8D7450E6366861384BBE98C86E78E`；`RRTConnect.cpp 5886059EB550BEB080B49FCDCA585E8E36E14A6EC605443F35D06E8926BCDDDA`；`PathSimplifier.cpp 54C838E7DDF62CF4A3392C7A2C3ED1EA2AFB0850AC75F4BEFF0C4C89643DEB8A` | planner依赖外部state validity/motion validator；离散segment resolution影响漏碰风险；不自带具体机器人geometry |
| [TRACLabs/trac_ik](https://bitbucket.org/traclabs/trac_ik/src/57057ce79ec1dd07aa5c1b46e134c701943dee6d/) | `57057ce79ec1dd07aa5c1b46e134c701943dee6d`；2026-05-26；BSD-3-Clause；官方Bitbucket | `README D46F61EE66875783041547C1C71592AE3F67AF897ABCBBC4DBBC2999931F19BA`；`LICENSE 99BF42B7425F9C540D865700225B676922968E568C03F5F7C8887E630E40D524`；`trac_ik.cpp E8A7AD18F85AD504C2F48EAE2F19771ED4949106F6B6D9C0CCEF18D4A2855B7B`；`nlopt_ik.cpp 96519495900478EFDAF0BC5531B74E88532B1565458FBB4F9FA880AE1A9C0B10`；`kdl_tl.cpp CF652E5A3EEB80E787E85FA90EEA48762482E35D55A9CCCD798F1A409FEF9C24`；`plugin.cpp C335D877BE6728A838A0C714FBAD71662D22813EBD53E913A5609EBC32C12ADF` | KDL与NLOpt并发、joint lower/upper bounds、timeout与MoveIt plugin；README明确不做mesh self-collision |
| [cliport/cliport](https://github.com/cliport/cliport/tree/2be5c47b5bb9bb7040ad90693288b87b1e18e7ad) | `2be5c47b5bb9bb7040ad90693288b87b1e18e7ad`；2023-05-22；Apache-2.0 | `README F0D9B90D00180BA2BA33C85F232DE625ACE20E4B6D586F0D464B59B3EC73E1B5`；`LICENSE 1EB85FC97224598DAD1852B5D6483BBCF0AA8608790DCC657A5A2A761AE9C8C6`；`transporter.py D657B94BE0EB0A2CB3BB78657EA86F70846A60EF3B4062669620AC3A8ACFAB5F`；`transporter_lang_goal.py E2CBDF8914F41EE0641ED79BFC6408D78C60FA38307C9C7A8ECF3F2B68069EBA`；`attention.py CB1D44CF81ADDE299F30F87DC21F7A6876C88E0539D7F2A593A66BA13E4F4D59`；`transport.py D1995800A3EA4F0E8480E122CE93FF35FC69D2F0150C2EDC144528434BD222F8` | attention/transport argmax到pick/place pixel/pose，语言条件接口；任务环境承担具体执行语义 |
| [google-research/language_model_uncertainty](https://github.com/google-research/google-research/tree/95e3a1da2d27cb9c8289f6fd3076cfed608c3c94/language_model_uncertainty) | root repo `95e3a1da2d27cb9c8289f6fd3076cfed608c3c94`；2026-07-16；Apache-2.0 | `LICENSE CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30`；`README 7FA870E4BB920960666A5E784146A49714625FBA3AB287EB28290E4AF86E7E99`；`KnowNo_Demo.ipynb C311B6C8DA9C35F60EABAF33173DE5554B26B041922EE10E59742969D8A804F3`；`MobileManipulation.ipynb C0AC18A88EDB110F66F319850CA50047E8BD333C46D78C5CDE9B401D7818DCBF`；`TabletopSim.ipynb D6A024568099F2E490C8D89470829AD208823153FF2145808E253744EA0D11FD` | finite calibration、higher quantile、prediction set与help trigger；notebook模型/场景限制必须保留 |

35个文件的SHA-256均按固定revision工作树或`raw.githubusercontent.com`原始字节计算。代码license不自动覆盖论文、dataset、robot description、mesh、模型权重、OpenAI/PaLM API、PyBullet/MuJoCo、ROS依赖或硬件驱动，部署时要逐项复核。

## 4. 节点边界与主链

```text
PER-014 semantic target / pose / mask
  -> frame + unit + timestamp + covariance validation
  -> workspace / reachability
  -> IK residual + joint limits + singularity
  -> self / environment collision + clearance
  -> path continuity + velocity + acceleration
  -> uncertainty / abstention / fallback
  -> controller schema + execution precheck
  -> controller-ready candidate
```

| 相邻节点 | 已负责 | PER-015只新增 |
| --- | --- | --- |
| PER-014 | 3D entity、relation、semantic target、score与metric | 检查该target能否转换为可执行candidate |
| VOL 03 | action representation、chunk、normalization、policy head | 不训练head；只验证其输出到controller的合同 |
| PER-016 | localization、SLAM、map/pose drift | 只消费并核验frame/time/revision；不修复漂移 |
| PER-019 | navigation benchmark与统计评估 | 本页只给per-candidate gate和reason，不宣称benchmark success |

静态gate通过只表示“在冻结scene/model/controller合同下未发现已检查的违规”，不是接触成功、任务成功或安全认证。

## 5. Typed Perception→Action Manifest

任何进入可行性检查的candidate至少应冻结：

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

缺frame、unit、timestamp、robot model、joint order或scene revision时，candidate不能被安全补默认值后执行；应fail closed并返回缺失字段。

## 6. Gate Decomposition 与Reason Taxonomy

推荐把总gate写为：

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

变量解释：每个\(G_k\)都必须返回`pass/fail/not_checked`与证据；`not_checked`在fail-closed模式中等价于不能执行，而不是默认为pass。

| Failure code | 语义 | 默认动作 | 不应做 |
| --- | --- | --- | --- |
| `IDENTITY_MISSING` | frame/unit/time/revision缺失 | reject/ask | 猜默认frame继续 |
| `TARGET_STALE` | target age超过deadline | re-perceive | 复用旧pose |
| `OUTSIDE_WORKSPACE` | 粗workspace不满足 | reject/reframe | 强行调用IK |
| `IK_NO_SOLUTION` | timeout内无满足残差的解 | resample/replan | 使用最后iterate |
| `IK_RESIDUAL_HIGH` | solver返回但pose误差超阈值 | reject | 只看return code |
| `JOINT_LIMIT` | 数学解越界 | alternate branch/reject | clamp后直接执行 |
| `NEAR_SINGULAR` | \(\sigma_{\min}\)过低或condition过高 | change pose/replan | 放大关节速度 |
| `SELF_COLLISION` / `ENV_COLLISION` | 状态或路径碰撞 | replan/reject | 只查goal state |
| `CLEARANCE_LOW` | 安全膨胀后余量不足 | replan/ask | 用nominal mesh硬过 |
| `DYNAMIC_LIMIT` | velocity/acceleration/time失败 | re-time/replan | 原时间戳执行 |
| `UNCERTAIN` | risk/prediction set不满足 | ask/re-perceive | 取top-1强行执行 |
| `CONTROLLER_SCHEMA` | dim/order/unit/rate不匹配 | reject | slice/pad到能跑 |
| `EXECUTION_PRECHECK` | current state/timeout/controller不可用 | stop/recover | 吞异常返回success |

## 7. Semantic Target → Action Target

Transporter/CLIPort把视觉与语言映射成pick/place位置或姿态，是清晰的perception→action proposal范例。CLIPort固定代码从attention和transport heatmap取argmax，构造`pick/place` pixel与rotation，再借相机/heightmap几何形成pose。这个接口仍未回答：

- target在base/world中的frame是否正确；
- gripper/tool transform、pre-grasp与approach direction；
- arm是否能到、选哪个IK branch；
- path是否碰撞、clearance是否充足；
- controller需要absolute/delta/velocity还是joint trajectory；
- target是否已经stale、score是否经过部署分布校准。

因此推荐将semantic output与controller input分成两个不可混淆的原子：

```text
semantic_target = {entity_id, pose/mask, frame, score, timestamp}
action_target   = {tool_pose, approach, gripper, robot_model, limits, controller}
```

从前者到后者的转换函数必须可版本化，并保留失败reason；不能只返回一个7D数组。

## 8. Workspace 与Reachability

对二维二连杆，末端位置半径的必要充分位置条件是：

\[
|l_1-l_2|
\le \|\mathbf p\|_2
\le l_1+l_2.
\]

它适合做cheap reject，但真实机械臂还需姿态、base/tool transform、joint coupling、环境和路径约束。粗workspace通常是必要非充分条件：点在workspace内仍可能因指定orientation、joint limit或障碍而不可达。

工程上至少区分：

1. geometry workspace：由link length和joint range形成；
2. task workspace：加入tool、approach、support surface和姿态；
3. current-state reachability：加入当前关节状态、path和时间；
4. robust reachability：对target covariance、scene误差和controller tracking error膨胀后仍通过。

缓存reachability map时必须绑定robot URDF/SRDF、tool、planning group、joint limits和采样分辨率；换gripper或base pose后不能沿用旧结果。

## 9. IK Residual、Joint Limit 与Singularity

对目标位姿\(T^*\)与当前解\(T(\mathbf q)\)，body-frame pose error可写为：

\[
\mathbf e(\mathbf q)
=
\operatorname{se3ToVec}
\left(
\log\!\left(T(\mathbf q)^{-1}T^*\right)
\right).
\]

应分别检查rotation与translation residual，而不是只看单一return code。Modern Robotics固定`IKinBody/IKinSpace`迭代pseudoinverse Jacobian，并用`eomg/ev`终止；README明确该库以教学可读为主，不是robust production solver。

Jacobian奇异性可用SVD诊断：

\[
J(\mathbf q)=U\Sigma V^\top,\qquad
\sigma_{\min}(J)<\tau_\sigma
\Rightarrow \text{near singular}.
\]

阈值应绑定joint scaling与task Jacobian；旋转和平移单位未归一时，condition number可能没有可比意义。接近奇异时，有限末端速度可对应过大关节速度，必须进入velocity/controller gate。

TRAC-IK固定实现并发运行KDL路径与NLOpt路径，显式接收`q_min/q_max`，KDL-TL在越界或局部最小时重启，NLOpt设置lower/upper bounds。它改善joint-limit场景的求解率，不代表：

- IK solution无self/environment collision；
- 每个solution具有足够clearance或manipulability；
- branch切换在轨迹上连续；
- timeout返回前的最后iterate可直接执行。

TRAC-IK官方README明确mesh self-collision不是IK solver行为，这一negative boundary必须保留。

## 10. Collision、Clearance 与Motion Validation

对机器人几何\(\mathcal R(\mathbf q)\)、障碍\(\mathcal O\)和安全膨胀\(m\)，robust clearance gate可写为：

\[
d_{\min}\!\left(\mathcal R(\mathbf q),\mathcal O\right)
>
r_{\mathrm{robot}}+m_{\mathrm{model}}+m_{\mathrm{uncertainty}}.
\]

实际实现通常直接对collision objects做padding/scale或Minkowski-style inflation。必须冻结：

- robot/self/environment collision geometry；
- attached object与tool geometry；
- allowed collision matrix；
- continuous或discrete checking；
- edge interpolation resolution；
- scene timestamp/revision；
- nominal padding与uncertainty inflation。

MoveIt固定`PlanningScene::isStateValid`先检查collision再检查constraints；轨迹检查会遍历waypoints。OMPL固定`SpaceInformation`委托`StateValidityChecker`和`MotionValidator`，`DiscreteMotionValidator`按`validSegmentCount`离散检查edge；RRT-Connect在扩展树时调用`isValid/checkMotion`。

因此“RRT-Connect是collision-free planner”有前提：具体validity checker、geometry、resolution和scene必须正确。过粗resolution可能穿过薄障碍；只检查waypoints也可能漏掉swept path碰撞。

## 11. Trajectory、Time Parameterization 与Controller Gate

几何路径\(\mathbf q_0,\ldots,\mathbf q_N\)进入controller前至少满足：

\[
\mathbf q_{\min}\le\mathbf q_t\le\mathbf q_{\max},\qquad
|\dot{\mathbf q}_t|\le\dot{\mathbf q}_{\max},\qquad
|\ddot{\mathbf q}_t|\le\ddot{\mathbf q}_{\max}.
\]

MoveIt固定Time-Optimal Trajectory Generation接收velocity/acceleration limits并生成timestamps；TrajectoryExecutionManager在执行前验证current joint state、joint集合与起点容差，并保留controller timeout和execution status。可执行合同还应包括：

| 维度 | 必须冻结 | 典型失败 |
| --- | --- | --- |
| shape | `H×D`、valid mask、joint count | 7D policy送进12D env |
| semantics | absolute/delta/velocity、joint/cartesian | delta被当absolute |
| order | xyz/rpy/gripper或joint names | axis/joint错位 |
| unit | m/mm、rad/deg、normalized/raw | 数量级错误 |
| time | Hz、dt、timestamp、queue/replan K | chunk过期或jerk |
| state | start state与容差 | 当前状态已漂移 |
| status | timeout/cancel/abort/result | failure被包装成success |

对learned action chunk，应在每次replan前重新核验剩余action age、current state和scene revision；chunk第一步通过不保证后续所有步仍有效。

## 12. Uncertainty、Abstention 与Risk–Coverage

KnowNo的nonconformity score可写为：

\[
s_i=1-f(x_i)_{y_i},
\qquad
\hat q=
\operatorname{Quantile}_{\lceil(N+1)(1-\epsilon)\rceil/N}
\{s_i\}_{i=1}^{N}.
\]

test-time prediction set为：

\[
C(x)=\{y:f(x)_y\ge 1-\hat q\}.
\]

固定MobileManipulation/Tabletop notebook使用`method='higher'`求quantile；prediction set非singleton时触发help，mobile notebook还把additional “none of the above” option进入set视为help。其目标是在exchangeable calibration/test条件下给marginal coverage，不是逐样本条件概率或硬件安全证书。

PER-015需要至少拆开三类uncertainty：

1. semantic uncertainty：target/query候选不唯一；
2. geometric uncertainty：pose/depth/calibration/collision geometry误差；
3. execution uncertainty：latency、tracking、contact与controller状态。

它们不能用同一logit代替。一个推荐决策表是：

| 条件 | 决策 |
| --- | --- |
| semantic set非singleton但可人机澄清 | `ask_for_help` |
| geometric covariance使inflated path碰撞 | `re-perceive / replan` |
| controller状态unknown或target stale | `stop / reject` |
| risk budget满足且所有物理gate通过 | `accept candidate` |

distribution shift、calibration set leakage、label ambiguity或model/API变化都会破坏原阈值身份；必须重新校准并报告risk–coverage，而不是复用历史confidence threshold。

## 13. Fallback 与Fail-closed Semantics

fallback不应是“任何异常都执行默认动作”。建议：

```text
perception ambiguous -> ask / re-perceive
workspace or IK fail -> alternate proposal / branch / base reposition
collision fail       -> replan with updated scene
trajectory fail      -> re-time / shorter horizon
controller mismatch  -> reject, never slice/pad silently
execution timeout    -> cancel -> stop -> verify state -> recover
```

每次fallback都要有上限、timeout和状态验证；否则replan loop会变成无限重试，或在scene已变化时执行旧candidate。`stop`也要定义为controller-level可验证状态，不是一条日志字符串。

## 14. Public Method → Code Mapping

| 机制 | 固定实现映射 | 必须保留的边界 |
| --- | --- | --- |
| numerical IK | Modern Robotics `IKinBody/IKinSpace`、Jacobian与pseudoinverse | 教学实现；不含joint/collision生产合同 |
| joint-limit IK | TRAC-IK `CartToJnt`、KDL-TL/NLOpt双solver、q bounds | 不含mesh collision |
| planning scene | MoveIt `checkCollision/isStateValid`、RobotState bounds/IK | 依赖正确URDF/SRDF/scene/ACM |
| sampling planner | OMPL `RRTConnect::solve`调用`isValid/checkMotion` | collision checker由集成方提供 |
| time/controller | MoveIt TOTG与TrajectoryExecutionManager | current state、controller和status仍可失败 |
| pick/place proposal | CLIPort/Transporter attention与transport argmax | pose proposal不等于reachable trajectory |
| uncertainty abstention | KnowNo quantile、prediction set、help trigger | coverage依赖exchangeability与校准协议 |

该表只建立公开机制的source-to-code桥，不证明本地五项目使用了这些固定commit，也不证明候选人ownership。

## 15. Deterministic Probes

| Probe | 固定输入 | 结果 | 只证明 |
| --- | --- | --- | --- |
| workspace annulus | \(l_1=1,l_2=0.7,r=1.8\) | range `[0.3,1.7]`；`REJECT` | cheap workspace必要条件 |
| IK residual | target `[1.3,0.2]`，solver q `[0.1,-0.1]` | residual `0.407507m > 0.01`；`REJECT` | solver输出仍需残差检查 |
| joint limit | reachable q `[π/2,0]`，q1 limit `[-1,1]` | `REJECT` | 数学IK与受限IK不同 |
| singularity | 2R伸直q `[0,0]` | \(\sigma_{\min}=0\)；`REJECT` | rank/conditioning gate |
| segment/AABB | segment `[0,0]→[1,0]`，box x `[.4,.6]`, y `[-.1,.1]` | collision true；`REJECT` | edge不能只查端点 |
| clearance inflation | path y `.25`；nominal `.10`、inflated `.20` | nominal无碰撞、inflated碰撞；`REJECT` | uncertainty可改变结论 |
| velocity/acceleration | q `[0,.5,1.5]`，dt `.1` | vmax `10`、amax `50`超限；`REJECT` | geometric path不等于timed trajectory |
| uncertainty abstain | risk upper `.12`，alpha `.05` | `ASK_FOR_HELP` | 风险预算触发abstain |
| stale target | age `240ms`，deadline `100ms` | `REJECT` | 时间身份属于gate |
| controller schema | expected 7D `xyz_rpy_grip/m_rad`，got 12D `dual_arm_plus_base/normalized` | `REJECT` | shape/order/unit必须fail closed |

10个probe由同一deterministic Python oracle执行，`10/10 expected decisions matched`。它们是机制sanity checks，不是MoveIt/TRAC-IK/CLIPort/KnowNo benchmark复现，也不证明本地robot success。

## 16. 本地五项目 Canonical Inventory Audit

| Inventory | Canonical SHA-256 | 当前安全结论 |
| --- | --- | --- |
| [OPD](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | 2D point/box/relation supervision；无reachability、IK、collision或controller gate |
| [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | action serialization与official-checkpoint diagnostics；formal Qwen generation/parser/controller缺失 |
| [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | tool/schema/scope/timeout与2D occupancy/PCD bridge；非manipulator feasibility gate |
| [WAM](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | OSC_POSE/action trace与失败diagnostic；不支持reachability/collision收益 |
| [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | 7D/16-step action、normalizer与rollout协议；不含通用物理gate |

Inventory是当前已归档证据的边界，不证明每台历史机器、远端主机或未同步分支绝对没有相关实现；因此下面对五个工作区做了直接关键词与文件检查。

## 17. 五项目 Direct Audit 与Negative Evidence

| 项目 / fixed file | SHA-256 | 直接发现 | 不能升级 |
| --- | --- | --- | --- |
| OPD `build_semantic_nav_box_grounding.py` | `C8265C1404009367AF4D3D211E228B88225819E7D5073E4FADFAD52CBAEC622F` | 2D semantic-nav box grounding数据构造 | manipulator workspace/IK/collision |
| OPD `opd_multiteacher_smoke_train.py` | `A9563CC1968221D65FDAE59C7A301ABF3BDC5D7C67771C1250A7EF626CE9F5DE` | `fallback`仅指system prompt/model配置路径 | execution fallback或safety gate |
| Robot `server/tools/registry.py` | `EF1AFE36697D16F4C2A1392F618444712A87F2F88EE3BDABE409BD2948D24CF1` | tool scope、锁、cancel、poll/timeout、best-effort compensation；SemanticNav invalid payload回local cache | arm IK、mesh collision、controller-ready pose |
| Robot `server/sim/ros2_bridge.py` | `8291D64DE01AAC2EFDF52409008EFD7AE18C5FEC0BA7B9D4677F6636F8287A48` | occupancy/PCD/state bridge与fallback state | 通用physical safety；fallback map不是fresh sensing |
| Robot `server/agent/sandbox.py` | `57460FAA62D3B7E5B51DD4B0AF7DC03C62DA48916708FBCE44EAC00B4DE3292C` | tool sandbox与robot ID fallback | real controller feasibility |
| OpenPi formal `formal_train.py` | `51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94` | action window→assistant JSON/full-chat CE | generation/parser/axis/unit/IK/controller gate |
| OpenPi `run_aloha_sim_real_rollout.py` | `E583E4770E4F867FA7B4BEABB3C88964EAB5B3E1AECBD1B59B870B20EF191DE3` | official checkpoint action chunk、finite/action-delta/jerk diagnostics | formal Qwen lineage或通用collision gate |
| OpenPi deprecated MuJoCo adapter | `D87F771120E08066F940022A4E1C4C7FD8F1427D6B6D6C62819BE729D190251F` | 文件自身明确缺official embodiment/controller/IK/workspace/contact semantics | behavior或robot success |
| WAM `cosmos_policy_gt_action_replay_diagnostics.py` | `CDD140108F5B475012FC85BA579E163C3B0D818BC3F49D5A2B10CFC7E7CAE5BD` | 7D→12D环境action拼接、dim mismatch hard error、OSC_POSE相关diagnostic | IK/collision收益；GT replay失败根因 |
| UWM `uwm_libero_rollout_eval.py` | `05E912C2096EFF4BFE8D061E4C334517B03DE80847793D83025A2AA3E18F3943` | `action_len=16/action_dim=7`、warmup与env.step | universal action schema或可达性gate |
| UWM `uwm_robocasa_gt_replay.py` | `E2AFAEF4F5ADA1559922C0FCAA9E694E69F4CB36AA124C5FD2160129EF415EB5` | action order/controller compatibility probe、preclip/env action日志；文件明确不是demo success oracle | exact reset、policy success或通用collision safety |

全仓关键词结果中的`fallback`多数是prompt、UI、map/state或text cleaning fallback；不能仅凭词命中推断physical recovery。Robot Harness第三方SenseBot目录含底盘controller代码和测试，但第三方来源、manipulator scope、当前runtime integration与候选人ownership均未闭合，不能据此把Robot Harness升级成通用PER-015 gate。

## 18. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 最小补强artifact |
| --- | --- | --- | --- |
| OPD | 2D semantic target/box/point可作为gate上游输入 | 已把grounding转成reachable manipulation | typed target、robot/tool model、IK/collision traces |
| Robot Harness | 上层tool scope、timeout/cancel/compensation和map bridge | tool sandbox 100%等于物理执行安全 | planner/controller revision、state/trajectory/collision log、ownership |
| OpenPiVLA | action serialization与official policy/controller diagnostics | formal Qwen已完成parser/controller/IK闭环 | strict parser、axis/unit/normalizer、controller roundtrip、episodes |
| WAM | OSC_POSE/action trace可用于schema与failure diagnosis | action range差异证明reachability/collision根因 | robot model、scene、IK/collision/TOTG report、paired rerun |
| UWM | 7D/16-step LIBERO action与RoboCasa action-order probe | 74.4%证明通用feasibility gate | checkpoint/normalizer、controller mapping、raw episodes与gate logs |

个人项目回答必须继续区分`upstream method`、`local-direct file`、`diagnostic inference`、`missing evidence`和`candidate ownership`。Git author不能替代“亲手/协作/工具辅助”的逐项确认。

## 19. Fail-closed Pipeline 伪代码

```python
def perception_to_action_gate(semantic_target, manifest, robot, scene, controller):
    # 1. Identity first: never guess frame, unit, schema, age, or revision.
    require_fields(semantic_target, ["frame", "axis_unit", "timestamp_ns", "artifact_sha256"])
    require_fields(manifest, ["robot_contract", "scene_contract", "risk_contract"])
    if age_ms(semantic_target) > manifest.target.age_deadline_ms:
        return reject("TARGET_STALE")

    # 2. Convert a semantic entity/pose into a typed tool/action target.
    candidate = build_action_target(semantic_target, manifest)
    validate_controller_schema(candidate, controller)  # dim/order/unit/rate

    # 3. Cheap workspace reject before expensive IK.
    if not robot.workspace_contains(candidate.tool_pose):
        return reject("OUTSIDE_WORKSPACE")

    # 4. IK return code is insufficient: verify residual, bounds, and singularity.
    solutions = robot.solve_ik(candidate.tool_pose, timeout=manifest.ik_timeout)
    valid = []
    for q in solutions:
        if pose_residual(robot.fk(q), candidate.tool_pose) > manifest.ik_tolerance:
            continue
        if not robot.satisfies_bounds(q):
            continue
        if min_singular_value(robot.jacobian(q)) < manifest.sigma_min:
            continue
        valid.append(q)
    if not valid:
        return reject("IK_NO_VALID_SOLUTION")

    # 5. State and edge validity use the same frozen scene/geometry contract.
    plans = plan_from_current_state(valid, scene, manifest.motion_resolution)
    plans = [p for p in plans if collision_free_path(p, scene)]
    plans = [p for p in plans if robust_clearance(p, scene, candidate.covariance)]
    if not plans:
        return replan("COLLISION_OR_CLEARANCE")

    # 6. A geometric path must pass timing and controller prechecks.
    timed = time_parameterize(plans, robot.velocity_limits, robot.acceleration_limits)
    if not timed:
        return replan("DYNAMIC_LIMIT")
    if not controller.precheck(timed, current_state=robot.current_state()):
        return stop("EXECUTION_PRECHECK")

    # 7. Apply a calibrated risk contract after physical checks; unknown is not pass.
    decision = calibrated_risk_decision(candidate, plans, manifest.risk_contract)
    if decision == "ask":
        return ask_for_help("UNCERTAIN")
    if decision != "accept":
        return reject("RISK_BUDGET")

    # 8. Return a candidate, not task success; execution owns feedback and recovery.
    return {
        "status": "controller_ready_candidate",
        "trajectory": timed[0],
        "checked_revisions": manifest.revisions(),
        "robot_success": None
    }
```

该流程保留每层失败身份，并把“candidate accepted”与“execution/task success”分开。生产实现还要处理并发scene update、controller cancel acknowledgement、contact/force限制与硬件急停；本source freeze不把伪代码包装成已部署系统。

## 20. Source Gate 与下一切片

本轮已关闭：

- 六份primary paper/book完整PDF、SHA与方法页视觉检查；
- 六个official source repository固定commit/date/license，35个关键文件逐字节SHA；
- semantic target→action target typed manifest与九层fail-closed gate；
- workspace、IK residual、joint limit、singularity、collision/clearance、trajectory/controller与uncertainty边界；
- 10个deterministic probes，全部命中预期拒绝/求助决策；
- 五份canonical inventory与11个local-direct file的项目真实性边界。

仍为`WARN`：本地没有统一typed gate manifest、robot/tool/scene immutable bundle、IK/collision/TOTG raw reports、calibrated risk–coverage、controller execution trace、matched robot episodes或五项目逐文件候选人ownership确认；primary paper和official code也不能替代本地部署证据。

`VLA-PER-015 source freeze`、knowledge与一张atomic card已在三个独立bounded slices同步；不创建`coaching_state.md`，266张题卡继续全部`unseen`，不改变任何mastery。下一bounded slice只冻结`VLA-PER-016` localization/odometry/SLAM/map-frame/drift source；不生成其knowledge/card。

## References

1. Lynch & Park, [Modern Robotics: Mechanics, Planning, and Control](https://hades.mech.northwestern.edu/images/7/7f/MR.pdf)；[official code@cbd41fd](https://github.com/NxRLab/ModernRobotics/tree/cbd41fdf0bf75dbd5e986d832ae14226964ff0ac)。
2. Kuffner & LaValle, [RRT-Connect: An Efficient Approach to Single-Query Path Planning](http://www.kuffner.org/james/papers/kuffner_icra2000.pdf)；[OMPL official code@eb3baca](https://github.com/ompl/ompl/tree/eb3baca772ab2c76f5943934b505751e031ff34c)。
3. Beeson & Ames, [TRAC-IK: An Open-Source Library for Improved Solving of Generic Inverse Kinematics](http://irl.cs.brown.edu/pubs/trac-ik.pdf)；[official code@57057ce](https://bitbucket.org/traclabs/trac_ik/src/57057ce79ec1dd07aa5c1b46e134c701943dee6d/)。
4. Zeng et al., [Transporter Networks: Rearranging the Visual World for Robotic Manipulation, v2](https://arxiv.org/abs/2010.14406v2)。
5. Shridhar et al., [CLIPort: What and Where Pathways for Robotic Manipulation, v1](https://arxiv.org/abs/2109.12098v1)；[official code@2be5c47](https://github.com/cliport/cliport/tree/2be5c47b5bb9bb7040ad90693288b87b1e18e7ad)。
6. Ren et al., [Robots That Ask For Help: Uncertainty Alignment for Large Language Model Planners, v2](https://arxiv.org/abs/2307.01928v2)；[official code@95e3a1d](https://github.com/google-research/google-research/tree/95e3a1da2d27cb9c8289f6fd3076cfed608c3c94/language_model_uncertainty)。
7. [MoveIt 2 official code@2fb8492](https://github.com/moveit/moveit2/tree/2fb8492b64ceb426d96e7f97e71846fb91394aa2)。
8. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary Source Freeze](vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html) 与 [VOL 03 Action Knowledge](../knowledge/vol_03_vla_action.html)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
