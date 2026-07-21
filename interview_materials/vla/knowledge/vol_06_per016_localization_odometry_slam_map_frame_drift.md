# VOL 06 Perception / Grounding / Navigation：Localization、Odometry、SLAM、Map Frame 与 Drift（PER-016）

> 状态：`drafted / VLA-PER-016 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-002` calibration/frame、`VLA-PER-003` multi-view/time、`VLA-PER-005` navigation policy；后续：`VLA-PER-017` belief/memory/exploration、`VLA-PER-019` navigation evaluation/failure。  
> 来源入口：[PER-016 Localization / Odometry / SLAM / Map-frame / Drift Source Freeze](../sources/vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html)。本页只把已冻结的六份primary paper、六个official repo、REP-105、10个deterministic probes与五项目local audit转成可教学、可诊断、可面试口述的知识；一张`unseen` atomic card已在后续独立bounded slice同步，不创建训练状态，也不改变任何mastery。

## 问题（Question）

面试官问“机器人怎样知道自己在哪里，odometry、localization和SLAM有什么差别，loop closure怎样修正drift，为什么要区分map与odom frame”时，合格回答不能停在“前端提特征、后端做优化”。必须先冻结sensor、clock、calibration、estimator、frame、map与evaluation身份，再解释local连续状态怎样由propagation/update得到、global loop或relocalization怎样改变`map→odom`、错误约束为什么会污染全图，以及ATE/RPE的alignment怎样改变结论。

本节点主链：

```text
sensor packets + calibration + clock
  -> frontend association / scan match / keyframe
  -> local propagation + filter/window update
  -> continuous odom->base + covariance + tracking state
  -> place candidate
  -> geometric verification + relative transform
  -> robust pose graph / map merge
  -> revisioned map->odom + map state
  -> planner/action consumer freshness gate
  -> timestamp association + SE(3)/Sim(3) evaluation
```

## 知识地图位置与边界

| 相邻节点 | 相邻节点负责 | PER-016负责 |
| --- | --- | --- |
| PER-002 | intrinsics/extrinsics、depth、TF方向与pixel→3D基础 | state、covariance与map/odom语义如何随时间更新 |
| PER-003 | camera/frame/time/presence与multi-view schema | packet order、clock、state history与estimator freshness |
| PER-005 | map-free/map-based、waypoint、planner/controller | planner消费的pose/map revision是否可信 |
| PER-013/014 | point/voxel/occupancy与3D semantic query | geometry/semantic map绑定哪个trajectory与revision |
| PER-015 | reachability、collision、trajectory与controller gate | global correction或lost state怎样让旧action target失效 |
| PER-017 | belief、frontier、memory与active exploration | 不在本页设计POMDP belief或探索策略 |
| PER-019 | episode success、collision/stop与统计 | 不把ATE好或tracking状态直接写成task success |

PER-016是state/map contract节点，不是传感器标定教程、导航policy综述，也不是“任意SLAM系统选型排名”。公开论文与代码只支撑机制；本地项目是否集成、候选人是否实现、真实机器人是否成功必须由独立artifact证明。

## 1. 30秒直觉：局部连续与全局一致不是同一个承诺

一个可靠的30秒回答是：

> 我先区分odometry、localization和SLAM：odometry累积相邻运动，强调连续但会漂；localization在一个有UUID和revision的已知地图里估pose；SLAM同时估trajectory与map。工程上通常发布连续的`odom→base`给局部控制，再让loop closure或relocalization更新`map→odom`，所以global pose可能跳但局部速度不能被伪造。loop candidate必须经过几何验证、relative transform和robust graph residual gate，外观相似不能直接加边。评估时ATE看global trajectory，RPE看local drift，并冻结timestamp association、SE(3)/Sim(3) alignment、单位与lost denominator；特别是Sim(3)会吸收monocular scale error。本地项目当前只有map/PCD/interface资产，没有可核SLAM runtime，所以我只讲接口边界，不讲已部署结果。

这段回答先封住八个偷换：

1. 有pose字段等于已定位；
2. odometry连续等于长期准确；
3. global map pose更准所以可直接做高频控制；
4. place candidate等于loop constraint；
5. loop closure一定改善地图；
6. relocalization、loop closure与map merge是同一事件；
7. ATE低等于尺度、可用性与map质量都好；
8. 有PCD、occupancy或ROS目录等于实现了SLAM。

## 2. 五个概念必须分开

| 概念 | 典型输入 | 主要输出 | map关系 | 典型失败 |
| --- | --- | --- | --- | --- |
| tracking | 当前sensor与local reference/map | current pose/state、tracking status | 消费local reference | blur、textureless、dynamic、association错误 |
| odometry | 连续camera/IMU/LiDAR/encoder | relative motion、continuous local trajectory | 可无global map | 累积translation/yaw/scale drift |
| localization | sensor + fixed/revisioned map | map-frame pose、covariance、status | 消费已知map | wrong map、alias、kidnapped robot |
| mapping | pose estimate + observations | occupancy/landmark/surface map | 生成或更新map | pose error被写入map |
| SLAM | sensor stream | trajectory + map + graph/status | 同时估计 | gauge、wrong association、false loop |

专业表达不是“SLAM包含定位和建图”一句话，而是明确估计变量与条件：

- odometry主要约束短时间相对运动，误差通常随路径累积；
- localization假定map身份已知，核心风险包括initial pose、map mismatch和data association；
- SLAM把pose与map变量共同放进filter、sliding window、bundle adjustment或pose graph；
- tracking是运行状态/局部过程，不能代替系统类别；
- mapping若消费错误pose，会生成内部一致但物理错误的地图。

“定位有效”至少要绑定`map_uuid/revision`、sensor/calibration SHA、estimator config/checkpoint、timestamp、tracking state与covariance。裸`x,y,yaw`没有可审计身份。

## 3. Typed Localization / SLAM Manifest

```json
{
  "sensor_contract": {
    "camera_imu_lidar_encoder_ids": [],
    "intrinsics_extrinsics_sha256": "...",
    "axis_unit": "REP-103-like or explicit custom",
    "timestamp_clock_sync": "...",
    "noise_bias_rolling_shutter_model": "..."
  },
  "estimator_contract": {
    "family": "VO | VIO | LiDAR odom | localization | SLAM",
    "paper_repo_commit_config_checkpoint": [],
    "initialization_and_scale": "...",
    "frontend_backend_window_marginalization": "..."
  },
  "frame_contract": {
    "map_odom_base_sensor": [],
    "transform_direction": "T_target_source",
    "map_to_odom_authority": "localizer_or_slam",
    "controller_local_frame": "odom"
  },
  "state_contract": {
    "timestamp_ns": 0,
    "pose_velocity_bias_covariance": [],
    "tracking_state": "initializing | tracking | recently_lost | lost | relocalized",
    "state_revision": "..."
  },
  "map_contract": {
    "map_uuid_revision_sha256": "...",
    "keyframe_landmark_submap_pose_graph_revision": "...",
    "loop_constraints_and_rejections": [],
    "map_update_sequence": 0
  },
  "evaluation_contract": {
    "dataset_split_sequence": "...",
    "association_and_alignment": "timestamp + SE3 | Sim3",
    "ate_rpe_drift_lost_relocal_loop_metrics": [],
    "failure_denominator": "..."
  }
}
```

这个manifest的面试价值是把“算法名”转成可失败的合同。比如同一组pose数值若没有map revision，就不知道global correction前后是否混用；同一ATE若不知道Sim(3)还是SE(3)，就不知道scale error是否被alignment消掉；同一“VIO”若没有clock、noise与extrinsic身份，也无法把漂移归因到模型。

## 4. REP-105 Frame Tree：Map负责Global，Odom负责Local

典型组合是：

\[
T^{\mathrm{map}}_{\mathrm{base}}(t)
=
T^{\mathrm{map}}_{\mathrm{odom}}(t)
T^{\mathrm{odom}}_{\mathrm{base}}(t).
\]

变量解释：`T^A_B`把B-frame量变到A-frame；`T^{map}_{odom}`由global localizer/SLAM维护，`T^{odom}_{base}`由local odometry维护。直觉是controller消费连续的local motion，而global correction只改变两个参考系的关系。实现映射：每个consumer记录TF timestamp、direction、map revision和state revision；若PER-015的action target跨越一次global correction，必须重新投影并重做feasibility gate。

### 4.1 为什么不能只保留一个world frame

- 若把loop correction直接写进高频local pose，controller可能把位置跳变解释成巨大速度；
- 若永远只保留continuous odom，长期drift又会让global goal与map障碍错位；
- 分层不是“复制两份pose”，而是把不同连续性承诺显式化；
- ROS REP-105只是约定，不证明本地TF tree、authority或timestamp正确。

### 4.2 Correction jump的固定反例

如果global pose从`10m`修正到`8.6m`，同一时刻local odom只前进`0.1m`，则map-frame delta为`-1.4m`而真实local motion仍约`0.1m`。局部控制、速度估计与motion compensation应消费local连续量；global planner则需要接收新map revision并重新验证旧目标。

## 5. State Estimation：Propagation、Update 与Covariance

常见VIO状态可抽象为：

\[
\mathbf x_t=
\left(
R_t,\mathbf p_t,\mathbf v_t,
\mathbf b^g_t,\mathbf b^a_t
\right),
\qquad
P_{t|t-1}=F_tP_{t-1|t-1}F_t^\top+Q_t.
\]

变量解释：`R,p,v`分别是orientation、position、velocity；`b^g,b^a`是gyro与accelerometer bias；`P`是state covariance；`F,Q`是linearized transition与process noise。直觉是IMU能高频propagate，但noise和bias会持续扩大不确定性。实现映射：OpenVINS `Propagator.cpp`对应propagation，`UpdaterMSCKF.cpp/UpdaterSLAM.cpp`对应不同feature update；这些文件存在不代表任何本地项目的noise、clock与calibration正确。

一个线性化measurement update可写为：

\[
K_t=P^-_tH_t^\top
\left(H_tP^-_tH_t^\top+R_t\right)^{-1},
\qquad
P^+_t=(I-K_tH_t)P^-_t.
\]

变量解释：`H_t`把state perturbation映射到measurement residual，`R_t`是measurement noise，`K_t`是Kalman gain。直觉是prediction uncertainty与measurement uncertainty共同决定信任比例。实现映射：若inlier、innovation、noise model或timestamp错误，covariance数值即使变小也不代表更可信。

固定covariance probe：`P0=.01,Q=.04`传播10步得到prior `.41`；以`R=.09`更新时`K=.82`、posterior约`.0738`。它只验证合同算术，不是OpenVINS benchmark。

## 6. IMU Preintegration不是“做平均”

VINS-Mono与Kimera把两个keyframes之间的高频IMU sample压成relative-motion factor。preintegration需要：

- camera与IMU各自timestamp和clock offset；
- gyro/accelerometer bias与noise density；
- gravity direction与unit；
- camera–IMU extrinsic；
- bias linearization point与repropagation策略；
- packet dropout、out-of-order与saturation处理。

它的目标是避免每次nonlinear iteration都从头积分所有raw IMU，而不是丢掉sensor identity。若bias或extrinsic改变却继续复用旧preintegrated factor，会把系统误差写进backend。

## 7. Front-end、Local Estimator、Back-end 与Global Layer

```text
sensor packets
  -> frontend: feature/flow/scan association, motion filter, keyframe
  -> local estimator: propagation + filter/window update
  -> backend: residual factors, robust objective, marginalization
  -> global layer: place recognition, geometric verification, pose graph/map merge
  -> typed map/odom state + covariance + tracking status
```

| 层 | 主要职责 | 必须保留的证据 | 常见误判 |
| --- | --- | --- | --- |
| frontend | detect/track/scan-match、keyframe、association | inliers、residual、blur/dynamic、candidate IDs | 点多等于pose对 |
| local estimator | current pose/velocity/bias/covariance、local map/window | innovation、conditioning、lost status | covariance小等于准确 |
| backend | nonlinear objective、factors、marginal prior | cost、factor residual、solver status | cost下降等于合同正确 |
| global layer | place、loop/relocal/merge、global graph | geometry inliers、relative transform、graph delta | candidate等于constraint |

前端、后端与global layer是责任分解，不是固定线程数。DROID-SLAM把learned update与dense BA耦合，OpenVINS是modular EKF，Cartographer按local submap与global constraint组织；仍需逐层保留输入输出与failure state。

## 8. Robust Objective、Gauge 与可观性

一般估计目标可写成：

\[
\hat{\mathcal X}
=
\arg\min_{\mathcal X}
\sum_{i\in\mathcal F}
\rho_i\!\left(
\|\mathbf r_i(\mathcal X;\mathbf z_i)\|_{\Sigma_i^{-1}}^2
\right).
\]

变量解释：`\mathcal X`包含poses、velocity、bias、landmarks或depth；`\mathcal F`是visual/IMU/scan/loop factors；`\rho_i`是robust loss；`\Sigma_i`是measurement covariance。直觉是多类约束共同决定state，outlier不能与正常measurement等权。实现映射：VINS sliding window、Cartographer scan/pose graph、DROID dense BA和Kimera factor graph的state与residual不同，不能只说“都做BA”。

### 8.1 Gauge freedom

没有global anchor时，把整条trajectory与map共同平移或旋转，relative residual可能不变；monocular还常有scale ambiguity。这意味着：

- optimizer需要fix gauge或引入prior；
- evaluation alignment是在处理坐标自由度，不是美化步骤；
- Sim(3)可吸收scale，SE(3)不能；
- 加IMU能改善metric scale与gravity约束，但bias、excitation、time/extrinsic错误仍会污染可观性；
- “VIO有IMU所以绝不漂”是错误结论。

## 9. Keyframe、Sliding Window 与Marginalization

保留全部frame会让state、memory与optimization不断增长。常见做法是选keyframe、保留fixed-lag window，并把旧变量的影响压成prior。

主要取舍：

- window太短会丢失长期约束，太长会增加latency和memory；
- keyframe阈值影响feature baseline、graph density、loop candidate和metric；
- marginalization把旧信息保留下来，但也可能把错误association固化进prior；
- 线性化点变化会带来consistency风险；
- filter与optimization不是“一个快、一个准”的普遍二选一，必须在同sensor、同预算、同协议下比较。

面试时可把VINS-Mono `estimator.cpp`、Kimera `VioBackend.cpp`与OpenVINS clone/state management作为三种组织方式，但不能反推本地系统选择或效果。

## 10. Loop Closure：四道门，不是一次相似度检索

```text
place candidate
  -> temporal/map exclusion
  -> descriptor or learned match
  -> geometric verification + relative pose
  -> robust residual / inlier / graph-consistency gate
  -> pose graph optimization
  -> map-to-odom correction + new map revision
```

pose graph可写为：

\[
\hat{\{T_i\}}
=
\arg\min_{\{T_i\}}
\sum_{(i,j)\in\mathcal E}
\rho\!\left(
\left\|
\operatorname{Log}\!\left(
Z_{ij}^{-1}T_i^{-1}T_j
\right)
\right\|_{\Omega_{ij}}^2
\right).
\]

变量解释：`Z_{ij}`是odometry或loop relative-pose measurement，`\Omega_{ij}`是information matrix，`T_i`是node pose。直觉是让所有relative constraints一致，同时降低outlier边的破坏力。实现映射：VINS `pose_graph.cpp`维护drift transform并做4-DoF optimize；ORB-SLAM3 `LoopClosing.cc`区分loop与merge；Cartographer构建node/submap constraints；Kimera论文用robust PGO处理outlier。

固定false-loop probe：odometry chain要求`x_2=2`，外观candidate却要求`x_2=0`，loop residual为`2>.5`时必须拒绝。若系统为了“闭环成功率”直接加入该边，optimizer可能把全图拉成错误但低cost的形状。

## 11. Relocalization、Loop Closure 与Map Merge

| 事件 | 触发 | 主要输出 | 不可偷换 |
| --- | --- | --- | --- |
| relocalization | tracking lost / known map | 恢复current pose、tracking state变化 | 不一定新增loop或改全图 |
| loop closure | current与history同地点 | verified loop constraint、global correction | candidate不是constraint |
| map merge | current map与另一map/session重叠 | inter-map transform、map fusion/revision | 不是拼接point clouds |

ORB-SLAM3 Atlas允许tracking lost后新建map，并尝试跨map relocalization/merge；VINS-Mono提供relocalization与4-DoF pose graph。这些公开设计可用于比较state machine，但不能说本地Robot Harness已有相同Atlas、thread或recovery机制。

## 12. Drift Taxonomy：先找第一处分叉

| Drift / failure | 常见来源 | 第一检查 | 不能直接归因 |
| --- | --- | --- | --- |
| translation drift | incremental noise、poor geometry、mismatch | RPE、inliers、motion excitation | “缺global BA” |
| yaw drift | gyro bias、弱heading约束 | bias、gravity、loop evidence | “视觉模型差” |
| scale drift | monocular gauge、弱excitation | sensor mode、SE3/Sim3 | “单位换算” |
| vertical drift | bias、gravity、ground assumption | gravity、axis、bias | “地图高度错” |
| time drift | clock skew、delay、interpolation | timestamps、queue age | “随机抖动” |
| map corruption | false loop、dynamic、wrong map | loop residual、graph delta、map UUID | “optimizer失败” |
| tracking loss | blur、occlusion、textureless、dynamic | frontend status、relocal log | “直接多加keyframe” |
| global jump | loop/relocal correction | map→odom event、consumer frame | “机器人高速移动” |

IMU改善某些短期约束与可观性，但不会修复错误clock/extrinsic；loop closure改善长期一致性，但false loop可能比不闭环更坏。回答要讲“哪个error source由哪个measurement约束”，而不是堆sensor名称。

## 13. Learned SLAM：学习模块仍受几何与协议约束

DROID-SLAM在dynamic frame graph上用recurrent update operator预测correspondence update，再调用differentiable dense BA更新pose和inverse depth。它说明learned front/back-end coupling可以成立，但仍需要：

- camera intrinsics与input preprocessing；
- checkpoint、training domain与sensor mode；
- frame graph、keyframe与memory threshold；
- GPU memory、latency与termination；
- lost/failure status与trajectory filling；
- 同association/alignment协议的ATE/RPE。

因此“learned”不等于不需要geometry，“end-to-end”不等于没有graph/state，“benchmark好”也不等于目标机器人上无distribution shift。

## 14. ATE、RPE 与Alignment Protocol

Absolute Trajectory Error在timestamp association与alignment后可写为：

\[
\operatorname{ATE}_{\mathrm{RMSE}}
=
\sqrt{
\frac1N
\sum_{i=1}^{N}
\left\|
\operatorname{trans}\!\left(
T_{\mathrm{align}}\hat T_i(T_i^*)^{-1}
\right)
\right\|_2^2
}.
\]

变量解释：`\hat T_i`是estimate，`T_i^*`是ground truth，`T_{align}`来自SE(3)或Sim(3) alignment。直觉是测global trajectory形状/位置误差。实现映射：必须保存association tolerance、alignment family、单位、采样频率、轨迹截断与lost段处理。

Relative Pose Error可写为：

\[
E_i^{\Delta}
=
\left(
(T_i^*)^{-1}T_{i+\Delta}^*
\right)^{-1}
\left(
\hat T_i^{-1}\hat T_{i+\Delta}
\right).
\]

变量解释：`\Delta`按frame、time或distance定义；RPE关注local incremental error，较少受global offset影响。实现映射：GT step为`1`、estimate step为`1.1`时translation RPE RMSE为`.1`，但必须说明delta和reduction。

| Metric | 回答什么 | 必须冻结 | 不能推出 |
| --- | --- | --- | --- |
| ATE | global trajectory一致性 | association、SE3/Sim3、unit、lost truncation | local control稳定 |
| RPE | local incremental drift | delta、translation/rotation reduction | map全局正确 |
| drift % | 路程归一化长期误差 | segment length、route、loop policy | 任意路径泛化 |
| lost/relocal | 可用性与恢复 | lost定义、timeout、denominator | pose精度 |
| loop precision/recall | place/constraint质量 | candidate/verified、GT loop定义 | map geometry质量 |
| map quality | occupancy/mesh/landmark质量 | pose source、coverage、resolution、threshold | policy success |

### 14.1 Alignment反例

- GT `[0,1,2]`、estimate `[5,6,7]`的raw RMSE为`5`；translation alignment后可变成`0`；
- estimate `[0,1.2,2.4]`在SE(3)下RMSE约`.1633`，Sim(3)用scale `.8333`后可变成`0`。

因此alignment不是脚注。对monocular结果用Sim(3)合理处理scale gauge时，必须同时承认“metric scale没有被该分数验证”。

## 15. 六类系统怎样比较

| 系统 | 核心组织 | 强项式回答 | 必须保留的边界 |
| --- | --- | --- | --- |
| ORB-SLAM3 | tracking/local mapping/loop & merge/Atlas | visual-inertial multi-map、relocal/merge | sensor/setup与local deployment |
| VINS-Mono | IMU preintegration + sliding-window VIO + 4DoF pose graph | bias/scale、marginalization、relocal | calibration/time/excitation |
| Cartographer | local scan/submap + global constraints | local continuity与global loop分层 | LiDAR/map config与robot TF |
| DROID-SLAM | recurrent update + dynamic graph + dense BA | learned correspondence与geometry coupling | checkpoint/domain/latency/global behavior |
| OpenVINS | modular on-manifold EKF + MSCKF/SLAM updates | state/covariance与filter模块化 | 不含完整loop-closing global SLAM |
| Kimera | stereo/IMU frontend + factor backend + loop/semantic stack | metric-semantic modular pipeline | VIO repo不等于全Kimera stack |

安全比较顺序是`input sensor → state/map → local/global architecture → failure/status → compute → metric protocol`。不要做“哪个最好”的无条件排名。

## 16. 十个Deterministic Probes

| Probe | 固定输入 | 结果 | 教学结论 |
| --- | --- | --- | --- |
| map/odom composition | `map→odom=-2m`，`odom→base=10m` | `map→base=8m` | frame chain必须显式 |
| SE(2) roundtrip | yaw 90°、t `[2,3]`、p `[1,0]` | q `[2,4]`，inverse error `6.12e-17` | transform方向可测 |
| covariance | P0 `.01`、Q `.04`、10步、R `.09` | prior `.41`，K `.82`，post `.0738` | 无update uncertainty增长 |
| ATE alignment | GT `[0,1,2]`，est `[5,6,7]` | raw 5，aligned 0 | alignment属于身份 |
| RPE | GT step 1，est step 1.1 | RMSE `.1` | local drift与offset分开 |
| false loop | chain x2=2，loop要求x2=0 | residual 2>.5，reject | candidate不能直接加边 |
| scale protocol | est `[0,1.2,2.4]` | SE3 `.1633`，Sim3后0 | Sim3隐藏scale error |
| correction jump | map pose `10→8.6`，odom delta `.1` | map `-1.4` vs odom `.1` | controller避免global jump |
| timestamp | `[0,.1,.09]` | non-monotonic reject | order/clock属于输入身份 |
| local fallback | `runtimeReady=false/softwareOnly=true` | localization gate false | map asset不是live localization |

10个probe得到`10/10 expected decisions matched`。它们验证frame、state、metric与failure合同，不是ORB-SLAM3、VINS、Cartographer、DROID、OpenVINS或Kimera benchmark复现。

## 17. First-divergence Failure Diagnosis

| 表面症状 | 第一检查层 | 关键证据 | 常见误诊 |
| --- | --- | --- | --- |
| pose整体翻转/旋转 | frame direction/axis | T convention、REP/custom axes | 调loop threshold |
| 开始即漂 | initialization/scale/gravity | excitation、bias、sensor mode | 只怪地图 |
| 匀速累积误差 | frontend/local estimator | RPE、bias、inliers | 直接加global BA |
| 某时刻突然跳 | map→odom correction | loop/relocal event、graph delta | 当真实高速运动 |
| 闭环后全图扭曲 | false loop/weight | geometry inliers、residual | 说optimizer随机坏了 |
| tracking反复lost | sensor/frontend | blur、texture、dynamic、timestamp | 只多加keyframe |
| ATE很好但尺度错 | alignment | Sim3/SE3、estimated scale | 报metric scale正确 |
| map可见但机器人不动 | localization/runtime boundary | runtimeReady、pose age、frame | 报SLAM成功 |
| 同轨迹不同分数 | evaluation protocol | association/alignment/truncation | 报模型回归 |
| 重启后位置错误 | map/session identity | UUID、load path、relocal log | 归因random seed |

诊断顺序：

```text
sensor identity / packet order / clock
  -> calibration / frame direction
  -> initialization / scale / gravity
  -> frontend association
  -> local state / covariance / marginal prior
  -> loop geometric gate
  -> graph correction / map revision
  -> ATE/RPE protocol
  -> planner / controller consumer
```

## 18. Fail-closed Localization Pipeline

```python
def update_localization(packet, manifest, estimator, map_bundle):
    # 1. Identity first: never guess sensor, frame, time, or calibration.
    require(packet, ["sensor_id", "timestamp_ns", "frame_id", "calibration_sha256"])
    require(manifest, ["estimator_revision", "frame_contract", "evaluation_contract"])
    if packet.timestamp_ns <= estimator.last_timestamp_ns:
        return {"status": "reject", "reason": "NON_MONOTONIC_TIME"}

    # 2. Propagate local state and covariance with the frozen sensor model.
    predicted = estimator.propagate(packet.imu, manifest.noise_bias_model)
    if not predicted.finite or predicted.covariance_exceeds(manifest.local_risk_budget):
        return {"status": "lost", "reason": "PROPAGATION_UNCERTAIN"}

    # 3. Frontend measurements may be absent or outliers; status stays explicit.
    measurements = estimator.frontend(packet)
    local = estimator.local_update(predicted, measurements)
    if not local.valid:
        relocalized = estimator.relocalize(packet, map_bundle)
        if not relocalized.geometrically_verified:
            return {"status": "lost", "reason": "RELOCALIZATION_FAILED"}
        local = relocalized.state

    # 4. A visual/place candidate is not a graph edge until geometry passes.
    candidate = estimator.detect_loop(local, map_bundle)
    if candidate is not None:
        verified = estimator.verify_loop(candidate, manifest.loop_gate)
        if verified.accepted:
            optimized = estimator.optimize_pose_graph(verified.constraint)
            if optimized.max_residual > manifest.graph_residual_limit:
                return {"status": "reject_loop", "reason": "GRAPH_INCONSISTENT"}
            map_bundle = optimized.new_map_revision

    # 5. Publish local continuity and global correction separately.
    return {
        "status": "tracking",
        "odom_to_base": local.odom_to_base,
        "map_to_odom": estimator.map_to_odom(map_bundle),
        "covariance": local.covariance,
        "map_revision": map_bundle.revision,
        "robot_success": None,
    }
```

伪代码保留`initializing/tracking/lost/relocalized/reject_loop`语义与map revision。它是面试中的目标合同，不是五项目现有实现。生产系统还要处理queue/backpressure、sensor dropout、concurrent map update、TF cache、watchdog、kidnapped robot、controller stop与immutable evaluation bundle。

## 19. Public Method → Code Mapping

| 机制 | fixed official code | 面试可讲 | 不能反推 |
| --- | --- | --- | --- |
| tracking/relocal/map atlas | ORB-SLAM3 Tracking/LoopClosing/Atlas | lost/relocal、loop vs merge、multi-map | local deployment |
| sliding-window VIO | VINS estimator/IntegrationBase | preintegration、marginalization、bias/scale | arbitrary sensor robustness |
| drift/pose graph | VINS pose_graph | world↔VIO transform、4DoF optimize | false loop自动无害 |
| local/global LiDAR SLAM | Cartographer local builder/constraint/pose graph | submap、scan match、global loop | visual/semantic mapping |
| learned dense BA | DROID droid/factor graph/backend | recurrent update + dense BA | checkpoint/latency/generalization |
| modular EKF | OpenVINS manager/propagator/updaters | state/covariance、MSCKF vs SLAM feature | full global SLAM |
| VIO + loop candidate | Kimera frontend/backend/LCD | stereo+IMU、factor graph、loop detection | VIO repo等于完整Kimera stack |

代码映射用于回答“机制落到哪里”，不是ownership证据。固定commit、license和文件SHA已经在source freeze中记录；论文、dataset、driver、map、weights与第三方依赖仍有独立license和provenance边界。

## 20. Robot Harness：Map Asset 与Live Localization的边界

Robot Harness的local-direct证据包括：

- `occupancy2d_map.json`：0/127/255语义、0.02m resolution、origin与conversion参数；
- `world.pcd`：PCD v0.7，含`x y z intensity timestamp ring`，共54,856点；
- `reloc_map/poses.txt`：timestamp与pose/quaternion-like八列资产；
- `ros2_bridge.py`：map/PCD/reloc路径、pixel↔world与state fallback；
- simulator fixture：`localization_mode/map_id/valid`字段；
- fallback targeted test：`1 passed`，并明确`runtimeReady=false/runtimeRealApiCalls=false`。

这些证据能支持“系统有地图资产schema与software-only bridge”，不能支持“实现了SLAM、loop closure或可靠relocalization”。缺失项包括sensor bag、clock/calibration lineage、estimator config/commit、live TF、pose/covariance stream、keyframe/pose graph、loop accept/reject、map UUID lineage和ATE/RPE trajectory bundle。

安全表述：

> Robot Harness里我能核验的是occupancy、PCD、reloc pose资产以及pixel/world和state bridge；fallback测试明确不是live runtime。没有estimator和trajectory证据前，我不会把这些资产包装成自研SLAM或真实定位结果。

## 21. 其余四项目的Localization Hook

### 21.1 OPD

OPD支持2D point/box/relation supervision与static holdout，可作为semantic observation upstream；没有sensor trajectory、3D map、localizer status或SLAM graph。不能说“做了semantic SLAM”。

### 21.2 OpenPiVLA

OpenPiVLA支持image/language/action训练与sim diagnostic。policy消费state或image不证明state来自可审计localizer；至少需要frame/pose lineage、localizer status、map revision与matched rollout。

### 21.3 WAM

WAM有video/world/action diagnostic，可讨论prediction对pose error的敏感性；world model latent不是机器人pose graph，也不能从video prediction推出定位改善。

### 21.4 UWM / LIBERO

UWM/LIBERO使用simulator state/action protocol；sim ground-truth state不是estimator output。若要研究localization robustness，应显式加入noisy observation estimator并保存raw estimated/GT trajectory与protocol。

## 22. 五项目 Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 最小补强artifact |
| --- | --- | --- | --- |
| OPD | 2D grounding可作semantic observation | 已做3D localization/semantic SLAM | sensor/pose/map manifest、trajectory-query绑定 |
| Robot Harness | map asset schema、pixel/world bridge、software-only state | 已部署SLAM、loop或relocalization | sensor bag、config、TF/graph、ATE/RPE、live logs |
| OpenPiVLA | policy侧image/state/action接口诊断 | policy结果证明localization正确 | pose lineage、status、map revision、matched rollout |
| WAM | video/world/action trace与pose-error sensitivity假设 | world model等于SLAM或提升定位 | camera trajectory、estimator/map revision、paired eval |
| UWM | simulator state/action protocol | simulator GT等于估计器输出 | noisy estimator、raw estimated/GT trajectory |

回答顺序必须是：

```text
public paper mechanism
  -> fixed official code
  -> local canonical inventory
  -> local-direct asset/interface
  -> missing estimator/runtime/result
  -> candidate ownership confirmation
```

Git author、目录名、ROS package、地图文件和一个green fallback test都不能替代个人实现与matched result。

## 23. 两分钟结构化回答

> 我会先把问题拆成odometry、localization和SLAM。Odometry主要从相邻sensor估relative motion，给连续local trajectory但误差累积；localization在一个有UUID/revision的已知map里估pose；SLAM共同估trajectory与map。系统身份不能只有算法名，还要固定camera/IMU/LiDAR、clock、intrinsic/extrinsic SHA、noise/bias、estimator commit/config/checkpoint、frame direction、map revision与tracking state。状态侧，IMU propagation更新pose、velocity、bias和covariance，视觉或scan measurement再update；VINS/Kimera常用preintegration与sliding window，OpenVINS是modular EKF，但filter和optimization不能脱离同协议排名。工程上按REP-105把连续`odom→base`与可能跳变的`map→odom`分开，loop或relocalization更新global relation，局部controller不应把jump当真实速度。Loop closure也不是检索到相似图就加边，而是candidate、geometry、relative transform、robust graph residual和new map revision五步；relocalization恢复current pose，map merge对齐不同session，它们不是同一事件。误差要按translation/yaw/scale/time/false-loop/lost分类，从sensor与clock开始找第一处分叉。评估时ATE看global trajectory、RPE看local drift，必须报告timestamp association、SE(3)/Sim(3)、delta、unit与lost denominator，因为Sim(3)会隐藏monocular scale error。公开ORB-SLAM3、VINS、Cartographer、DROID、OpenVINS和Kimera只支撑这些机制。本地五项目目前没有完整SLAM runtime；Robot Harness只有map/PCD/reloc assets和software-only bridge，所以我会明确讲接口证据，不声称自研SLAM或真实定位指标。

## 24. 高频追问

1. tracking、odometry、localization、mapping和SLAM的state分别是什么？
2. 为什么有pose字段不能证明localization有效？
3. `map→odom→base`每条边由谁维护？
4. map pose为什么允许跳，odom为什么允许漂？
5. controller直接消费map-frame pose有什么风险？
6. IMU propagation为什么会让covariance增长？
7. measurement update中`Q`与`R`各表示什么？
8. IMU preintegration为什么依赖bias linearization point？
9. frontend inlier很多为什么仍可能pose错？
10. backend cost下降为什么不证明frame/time合同正确？
11. filter与sliding-window optimization怎样公平比较？
12. gauge freedom是什么，为什么需要anchor或alignment？
13. monocular scale ambiguity怎样影响metric claim？
14. keyframe阈值怎样影响compute与loop？
15. marginalization为什么可能引入inconsistency？
16. loop candidate到graph edge之间有哪些门？
17. false loop为什么可能比不闭环更糟？
18. relocalization、loop closure与map merge怎样区分？
19. pose graph中的`Z_ij`与`Omega_ij`是什么？
20. DROID-SLAM既learned又为什么仍有BA与graph？
21. ATE与RPE分别对global offset和local drift多敏感？
22. SE(3)与Sim(3) alignment何时使用，隐藏什么？
23. lost/relocalization rate的denominator怎样定义？
24. map quality与trajectory quality为什么不能用一个分数？
25. Robot Harness的PCD与reloc poses为什么不是SLAM证据？
26. 怎样把localization revision传播给planner与PER-015 action gate？

## 25. 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “SLAM就是定位加建图” | 没有state/map/protocol | 先区分输入、估计变量与map假设 |
| “里程计一直有pose所以可靠” | 连续不等于无漂移 | 报RPE、covariance与lost state |
| “map frame一定比odom准” | global correction可跳 | global一致与local连续分工 |
| “VIO有IMU就有metric scale且不漂” | bias/excitation/time仍影响 | 报sensor mode与observability |
| “前端点多说明tracking好” | association可系统性错误 | 查geometry residual与state innovation |
| “optimizer cost降了所以对” | 错误模型也可低cost | 查frame/time/scale与held-out residual |
| “检索相似地点就能闭环” | 缺geometry与relative pose | candidate后做verify与graph gate |
| “loop closure一定修正drift” | false loop会毁图 | 报precision、residual与reject log |
| “relocalization就是loop closure” | trigger/output不同 | 分开current pose恢复与global edge |
| “拼两张点云就是map merge” | 缺inter-map transform与revision | 保存verified transform与map lineage |
| “ATE低说明定位各方面都好” | 不含local drift/lost/map quality | 配套RPE、availability和map metric |
| “Sim3对齐只是坐标换一下” | scale error被吸收 | 明确scale与SE3对照 |
| “DROID端到端不需要几何” | 仍有frame graph与dense BA | 讲learned update与geometry coupling |
| “有world.pcd说明做了SLAM” | 资产无producer lineage | 要sensor/config/graph/trajectory |
| “fallback test过了说明定位上线” | 明确softwareOnly | 只说offline asset bridge可用 |
| “Git里有代码就是我实现的” | ownership未确认 | 分开upstream、local file与个人决策 |

## 26. 白板 Checklist 与练习标准

能够不看材料完成：

- 用表格区分tracking/odometry/localization/mapping/SLAM；
- 写出sensor/estimator/frame/state/map/evaluation六组manifest；
- 推导`map→odom→base`组合并解释authority；
- 用correction-jump反例说明local controller选择；
- 写出VIO state、covariance propagation和measurement update；
- 解释preintegration的clock/bias/extrinsic依赖；
- 画出frontend/local/backend/global分层；
- 写出robust residual objective并解释gauge；
- 说明keyframe/window/marginalization取舍；
- 写出loop candidate→geometry→graph→revision链；
- 区分relocalization、loop closure与map merge；
- 写出pose-graph residual与information matrix；
- 复述八类drift与first-divergence顺序；
- 说明DROID learned update与dense BA边界；
- 写出ATE、RPE与SE3/Sim3协议；
- 复算10个deterministic probes；
- 走通fail-closed pseudocode；
- 比较六类公开系统而不做无条件排名；
- 说清五项目truth boundary；
- 完成两分钟回答并接住至少十二个追问。

`drafted`不等于掌握。PER-016一张L3/P1题卡已在后续独立card slice生成并保持`unseen`；当前267张题卡全部`unseen`。只有真实口述、追问、评分、纠错后，相关状态才可能变化。

## 27. 结论与下一步

可靠的localization/SLAM回答不是堆“特征、BA、回环”名词，而是建立三条可审计链：第一条是sensor/clock/calibration到state/covariance的local estimation链；第二条是candidate、geometry、relative pose、robust graph到map revision的global correction链；第三条是timestamp association、SE(3)/Sim(3)、ATE/RPE与failure denominator的evaluation链。

`odom`承诺local continuity但允许drift，`map`追求global consistency但允许correction jump；loop closure、relocalization和map merge有不同trigger与output；ATE、RPE、scale、lost与map quality也不能合并。ORB-SLAM3、VINS-Mono、Cartographer、DROID-SLAM、OpenVINS与Kimera分别支撑不同机制，不能反推本地部署或candidate ownership。

本地最接近本节点的是Robot Harness的occupancy、PCD、reloc poses与software-only state bridge，但没有producer estimator、live TF、pose graph、loop log或trajectory evaluation。OPD、OpenPiVLA、WAM与UWM也只有上游/interface hook。因此所有项目叙述继续保持`WARN`和evidence boundary。

`VLA-PER-016` source、knowledge与一张atomic card已在三个独立bounded slices同步；题卡保持`unseen`，不创建`coaching_state.md`、不改变任何mastery。下一bounded slice只冻结`VLA-PER-017` belief/memory/frontier/active-exploration source；不生成其knowledge/card。

## References

1. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Source Freeze](../sources/vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html)：六份完整PDF、六个official repo/36文件、REP-105、10个probe与五项目local audit。
2. Campos et al., [ORB-SLAM3 v2](https://arxiv.org/pdf/2007.11898v2)；[official code@4452a3c](https://github.com/UZ-SLAMLab/ORB_SLAM3/tree/4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4)。
3. Qin et al., [VINS-Mono v1](https://arxiv.org/pdf/1708.03852v1)；[official code@90dabb5](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/tree/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d)。
4. Hess et al., [Real-Time Loop Closure in 2D LIDAR SLAM](https://research.google.com/pubs/archive/45466.pdf)；[Cartographer code@877157a](https://github.com/cartographer-project/cartographer/tree/877157a0d91788a7700221d87232d412cb3c1ef4)。
5. Teed & Deng, [DROID-SLAM v2](https://arxiv.org/pdf/2108.10869v2)；[official code@2dfd39f](https://github.com/princeton-vl/DROID-SLAM/tree/2dfd39f0dcad44012ca7bbb8aa70b55edbfa9c99)。
6. Geneva et al., [OpenVINS ICRA 2020](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf)；[official code@6948812](https://github.com/rpng/open_vins/tree/69488123ed9362dd44b6f28e7f4680abbff1442b)。
7. Rosinol et al., [Kimera v3](https://arxiv.org/pdf/1910.02490v3)；[Kimera-VIO code@ce8c59b](https://github.com/MIT-SPARK/Kimera-VIO/tree/ce8c59b7b273ab5ac29db7e5572e1623760e19c7)。
8. ROS REP-105, [Coordinate Frames for Mobile Platforms@11ca24a](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0105.rst)。
9. [PER-002 3D Lift / Frame Knowledge](vol_06_per002_3d_lift_frame.html)、[PER-003 Multi-view / Temporal Knowledge](vol_06_per003_multiview_temporal.html)、[PER-005 Navigation Policy Knowledge](vol_06_per005_navigation_policy_architecture.html) 与 [PER-015 Perception→Action Gate Knowledge](vol_06_per015_perception_action_reachability_uncertainty_failure_gate.html)。
10. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
