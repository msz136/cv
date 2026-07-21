# VOL 06 PER-016 Source Freeze：Localization、Odometry、SLAM、Map Frame 与 Drift

> 状态：`source_frozen / VLA-PER-016 / primary_official_checked / localization_slam_contract / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本source切片只冻结localization、visual/visual-inertial odometry、SLAM、`map→odom→base` frame语义、state estimation、front-end/back-end、loop closure、relocalization、map merge、drift与ATE/RPE protocol；下游knowledge与一张`unseen` atomic card已在后续两个独立bounded slices同步；不重写PER-002的calibration/TF基础、不重写PER-003的multi-view/time schema、不重写PER-005的navigation policy/planner，也不进入PER-017的belief/memory/exploration。

## 问题（Question）

面试官问“机器人怎样知道自己在哪里，odometry和SLAM有什么差别，loop closure如何修正drift，map/odom frame为什么要分开”时，怎样给出带sensor/config/map/protocol身份的回答；怎样区分连续但会漂的local odometry与可能跳变的global localization；怎样验证loop closure而不是把错误地点强行拉到一起；以及五个本地项目到底有什么SLAM证据。

## 1. 结论先行

1. localization是“在已知或正在构建的地图中估计状态”，odometry主要累积相邻时刻运动，SLAM同时估计trajectory与map。三者输入、状态、地图假设与评估协议不同，不能用“都有pose输出”合并。
2. `odom`应连续、适合局部控制，但允许长期无界漂移；`map`是global/world-fixed参考，长期更一致但loop closure或relocalization后可跳变。REP-105的典型链为`map→odom→base_link`，global correction应更新`map→odom`，不应伪造传感器或让局部控制直接吃全局跳变。
3. drift来自sensor bias/noise、scale、time/extrinsic误差、feature/scan association、rolling shutter、dynamic object、linearization与marginalization等。加IMU或loop closure可以改善某些可观性与长期一致性，不代表误差自动消失。
4. loop closure至少需要place candidate、geometric verification、relative transform与robust graph optimization。外观相似不是约束成立；false loop可能让全图“看起来闭合”但物理错误。
5. relocalization是在tracking lost或已有map条件下恢复当前pose；loop closure是识别当前trajectory与历史位置的重复并加入global constraint；map merging是对不同map/session建立变换并融合。三者不能互换。
6. ATE、RPE、drift%、lost/relocalization rate、loop precision/recall和map quality分别回答不同问题。ATE必须冻结SE(3)/Sim(3) alignment、时间关联、轨迹截断、单位、采样频率与failure denominator；对monocular轨迹做Sim(3)后不能再把scale正确性当已验证。
7. 本地Robot Harness有2D occupancy、54,856点PCD、`reloc_map/poses.txt`、pixel/world变换和ROS2 state bridge，但fallback明确`runtimeReady=false/softwareOnly=true`；没有sensor packet、estimator config/checkpoint、live TF、pose graph、loop closure、ATE/RPE或matched robot trajectory。OPD、OpenPiVLA、WAM、UWM也没有当前可核SLAM runtime，因此保持`WARN`。

## 2. Primary Paper 冻结矩阵

| 来源 | 固定版本 / 完整性 | PDF SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| Campos et al., [ORB-SLAM3 v2](https://arxiv.org/pdf/2007.11898v2) | arXiv `2007.11898v2` / IEEE T-RO 2021；18页；全文解析；Atlas/tracking/local mapping/loop & map merging视觉检查PDF p5 | `4D119517BE7565C9651FBF1E36A330D605B7A534D738558858C96FECA7B99156` | visual/visual-inertial multi-map SLAM、tracking loss、relocalization、loop closure、map merging、Atlas | 任意本地项目已集成、所有sensor条件都鲁棒、真机结果 |
| Qin et al., [VINS-Mono v1](https://arxiv.org/pdf/1708.03852v1) | arXiv `1708.03852v1` / IEEE T-RO 2018；17页；全文解析；VIO/relocalization/4-DoF pose graph视觉检查PDF p3 | `1F44F92F057CBB05A6570F14D2FE5CAE2B9736198A8EECA7C93438ADBC38A087` | IMU preintegration、sliding-window optimization、marginalization、failure recovery、relocalization、4-DoF pose graph | 无标定/同步也能工作、任意尺度与yaw可观、本地无人机结果 |
| Hess et al., [Real-Time Loop Closure in 2D LIDAR SLAM](https://research.google.com/pubs/archive/45466.pdf) | ICRA 2016 official PDF；8页；全文解析；local 2D SLAM/submap/scan matching视觉检查PDF p2 | `351EDB45CD478C8CF2E22E375B8565A7ABB3455E92F45E7A7F4163130BDE69A2` | local scan matching/submaps、global loop constraint、sparse pose adjustment、occupancy update | 视觉SLAM、3D semantics、ROS部署一定正确 |
| Teed & Deng, [DROID-SLAM v2](https://arxiv.org/pdf/2108.10869v2) | arXiv `2108.10869v2` / NeurIPS 2021；15页；全文解析；frame graph/dense BA方法页视觉检查PDF p3 | `0E15F20BFF5F7CEAC468C2899BAAFC8C114A3018C7A7B213EED7C402E5CCEC90` | learned iterative updates、dynamic frame graph、dense bundle adjustment、monocular/stereo/RGB-D | distribution shift免疫、部署实时性、loop/global consistency无条件成立 |
| Geneva et al., [OpenVINS ICRA 2020](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf) | ICRA 2020 author PDF；7页；全文解析；on-manifold EKF state/covariance视觉检查PDF p2 | `194E432EDA4462DFB831108C62A486CA72BECC03C90DC53DB81087A04E683A11` | modular EKF、IMU state propagation、MSCKF/SLAM feature update、calibration state、covariance | full loop-closing SLAM、global map consistency、任意项目已部署 |
| Rosinol et al., [Kimera v3](https://arxiv.org/pdf/1910.02490v3) | arXiv `1910.02490v3` / ICRA 2020；8页；全文解析；VIO/RPGO/metric-semantic architecture视觉检查PDF p3 | `B2C27E2B111D59C8560B6ACCE5BD58528E1C810AD66D853BAF42D9337A9789E9` | VIO front/back end、preintegration/factor graph、loop detection、robust pose graph、metric-semantic stack | 选定Kimera-VIO repo单独包含全部RPGO/semantics、本地语义地图结果 |

六份PDF均检查`%PDF`、`%%EOF`并用`pypdf`读取全部页面；上述代表页另以Poppler 150 DPI渲染并视觉确认正文、公式、系统图和流程图清晰。解析与视觉检查只证明source可读，不证明论文算法在五项目中出现。

## 3. Official Repository 冻结矩阵

| 官方仓库 | 固定revision / date / license | 直接读取文件与SHA-256 | 支持边界 |
| --- | --- | --- | --- |
| [UZ-SLAMLab/ORB_SLAM3@4452a3c](https://github.com/UZ-SLAMLab/ORB_SLAM3/tree/4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4) | `4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4`；2022-02-10；GPL-3.0 | `README C043CB9E5136CC55323A7EF5C25B85E7BB28910679FC7B810FDA262F42E67507`；`LICENSE 53927BD0B739D38C87A0A82236FD9B070C2DFFF11C0C119BE50372005D5047AD`；`Tracking.h BA988CD16A0C49C69E5296B53E0B5896D53E936915CB61FAA4F7406EF1CE4FED`；`Tracking.cc A5828543839A42E0BB499E3325E32DDDFA20D5F7F00DB2D9B99F58F2FBDB9743`；`LoopClosing.cc B17BE9D654564603A409FC92213F6CCC889F6969426C04B8CD74BACBFEAF3B00`；`Atlas.cc E21F879FC9E811280C6158FE85FC955C6DF8FD0597A050664C3B1BBD2A788CF2` | tracking states、`Relocalization`、new-map creation、loop/merge与Atlas map集合；不支持本地集成或无失败保证 |
| [HKUST-Aerial-Robotics/VINS-Mono@90dabb5](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/tree/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d) | `90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d`；2024-05-23；GPL-3.0 | `README 67BDD390A496E3BEBAECAF00BC5CDD3DB4B16BADD85D4BB618DF9475681F1B67`；`LICENCE 53927BD0B739D38C87A0A82236FD9B070C2DFFF11C0C119BE50372005D5047AD`；`estimator.cpp ED7694B267BFC63E9897CD26812B633239872D06DA34D12BE1BA89B0BA26A42C`；`integration_base.h B4AFEDE059BF546F8B82823CD17AD71E51CDCB9D75BA36C09BD06E89D5632D4B`；`pose_graph.cpp 4C4D94034CC7988F2822A06D38DFF51B9DB8E1CD0E3C30C99B93DC60D7D34FF3`；`pose_graph_node.cpp B6153CECE247D6704CF0123E791ED2582E162291629E3174A497BE58E5368C5F` | preintegration/sliding window、loop detection、world↔VIO alignment、drift state与4-DoF optimize；不支持错误loop自动无害 |
| [cartographer-project/cartographer@877157a](https://github.com/cartographer-project/cartographer/tree/877157a0d91788a7700221d87232d412cb3c1ef4) | `877157a0d91788a7700221d87232d412cb3c1ef4`；2024-01-05；Apache-2.0 | `README 76EF5687E64FF7B419D96A4974B8A79A26EA078B698B3F4863BD258438FD2023`；`LICENSE 3DDF9BE5C28FE27DAD143A5DC76EEA25222AD1DD68934A047064E56ED2FA40C5`；`local_trajectory_builder_2d.cc A9FF133AE6A58ED81A7988AE450893AE2E85A9317FC4EC41AB0F3A0B577612B6`；`pose_graph_2d.cc 22050D76D1DD618B8C4D41EBEAF6196788E5F36DA0A7791D43D5E36277607E43`；`constraint_builder_2d.cc A03A964083330F3CDA4D3D1A1CF39F8CC8B36E32398782CE71D4259E28F8D991`；`optimization_problem_2d.cc 1DA2DDEB00FFC110877EC6C2820F397030D3F2EDFE5FF32C9A9A1087FBEA394C` | local trajectory、scan match、node/submap constraints与global optimization；不支持具体robot sensor/TF配置正确 |
| [princeton-vl/DROID-SLAM@2dfd39f](https://github.com/princeton-vl/DROID-SLAM/tree/2dfd39f0dcad44012ca7bbb8aa70b55edbfa9c99) | `2dfd39f0dcad44012ca7bbb8aa70b55edbfa9c99`；2025-05-04；BSD-3-Clause | `README C8A3FA5E27D904F6B1829A53E14250A54C409C5D26BF5D54C9DF7010C9BBA98D`；`LICENSE 4E5C4E3DDC06B6EF9EC8B24F57D6EDB7B8DEB12A32D8F7E525094B07E2D4C389`；`droid.py 35C7C0EE0FF83EA22808886BA6AB7EA354BD50592B3B249BAC887E24923ADF1B`；`factor_graph.py E491F3A5685CA08A4F2E6170B65878CBD87FC6E9E1D615D55BBBE611E07842E9`；`droid_backend.py 2066BB196294CEF776796C01FF8394740E81A36C670545D2F011B677C27D7E88`；`trajectory_filler.py 786EA1F95A9C95D529ACD07AF544920C8687D793589BF011FECEF36590D06A12` | front/back end、factor graph update、trajectory fill与dense BA调用；不支持任意checkpoint/generalization/latency claim |
| [rpng/open_vins@6948812](https://github.com/rpng/open_vins/tree/69488123ed9362dd44b6f28e7f4680abbff1442b) | `69488123ed9362dd44b6f28e7f4680abbff1442b`；2025-11-30；GPL-3.0 | `ReadMe F3E10779872D3FCD386E3FADDB543D264B896C8B64D258CE1DC7C31B3FD07518`；`LICENSE 230184F60BAE2FEAF244F10A8BAC053C8FF33A183BCC365B4D8B876D2B7F4809`；`VioManager.cpp 5E4C9B1AA087F7A7A89A5A093EAB7387734319481730EF78E497EC2CA9992D1C`；`Propagator.cpp B4F65173046D54DE5279CD1BD936F09C2E4B4CD49B46DF377B49D46E5C36D6DD`；`UpdaterMSCKF.cpp BEE6541A13C9F1CEB123B40D48AFEC4E8DC38280AB9B65519CF968C0644582DD`；`UpdaterSLAM.cpp FCA5D645773C896F4147EC6DE79B7AD2334D6C6E0ECA1208DC35B0B8A1F87CFD` | propagation、clone/state/covariance、MSCKF/SLAM feature updates；不支持loop-closure pose graph或global map |
| [MIT-SPARK/Kimera-VIO@ce8c59b](https://github.com/MIT-SPARK/Kimera-VIO/tree/ce8c59b7b273ab5ac29db7e5572e1623760e19c7) | `ce8c59b7b273ab5ac29db7e5572e1623760e19c7`；2025-02-10；BSD-2-Clause | `README 212633EB938586E6E33993FAC21B639BCBACA858F1CDA2EF0F9EF157D7DE9772`；`LICENSE.BSD C3FE35DBF24E3476A7995B77F84A07394AAC21BAAB8CFB1E04CE2EE3BB770E28`；`StereoVisionImuFrontend.cpp DD94E4932EF15AE55541685D8198E18454440D1312AF5E3752B040DD61E149DB`；`ImuFrontend.cpp 1BE186920111327A42FA1D8BB4303CBCCB345BAF7673BBC491455ADFDFF088E5`；`VioBackend.cpp 7903CB92A876F03204B4F06B0CF4599C0409E52BF26B6E64F5F7C5A1F98883BA`；`LoopClosureDetector.cpp 2F878CDCD23BC71BE1CD02EB1A42FE338DC3B2ECDB3A4F9A4700C8D268345A10` | stereo/IMU frontend、preintegration、factor-graph backend与loop candidate detection；完整RPGO/semantics仍跨repo/module |

36个文件均从上述fixed checkout按原始字节计算SHA-256。代码license不自动覆盖论文、dataset、sensor driver、camera model、vocabulary、pretrained weights、ROS package、地图资产或第三方依赖；面试中不能把开源license说成部署链已经合规。

## 4. 节点边界与依赖

| 相邻节点 | 已负责 | PER-016只新增 |
| --- | --- | --- |
| PER-002 | intrinsics/extrinsics、depth、pixel→camera→target、REP-103/105 frame基础 | state estimate与map/odom语义怎样随时间更新 |
| PER-003 | per-view camera/frame/time/presence与multi-view fusion schema | sensor stream如何进入estimator、timestamp/order gate与state history |
| PER-005 | map-free/map-based/waypoint policy、planner/controller/replan | planner消费的global pose/map revision是否可信 |
| PER-013/014 | point/voxel/occupancy与3D semantic query | map geometry/semantic层使用哪个trajectory与map revision |
| PER-015 | action reachability、collision、controller gate | stale/jumped localization怎样使action candidate失效 |
| PER-017 | belief、memory、frontier与active exploration | 不在本页实现POMDP belief或探索策略 |

ROS REP-105沿用PER-002固定commit `ros-infrastructure/rep@11ca24a41f31480dfb9562ba99f2a5b93d3ebda5`，`rep-0105.rst` SHA-256为`6BCA6AE2B392BBB8E95C283C672549B832C58128FEACCC4D77B6BF65534F565E`。它提供frame convention，不证明任一项目存在有效TF tree。

## 5. 五个概念必须分开

| 概念 | 典型输入 | 主要输出 | 是否维护map | 典型失败 |
| --- | --- | --- | --- | --- |
| tracking | 当前sensor与local map/reference frame | 当前pose/state与tracking status | 消费local map | feature不足、blur、dynamic |
| odometry | 连续camera/IMU/LiDAR/encoder | 相对运动与连续local trajectory | 可无global map | 累积drift、scale/bias |
| localization | sensor + 已知map | map-frame pose/covariance | 消费fixed/revisioned map | wrong map、alias、kidnapped robot |
| mapping | pose estimate + observations | occupancy/landmark/surface map | 生成或更新map | pose error写进map |
| SLAM | sensor stream | trajectory + map + graph/status | 同时估计 | wrong association、gauge、loop outlier |

“定位成功”至少要说明map UUID/revision、sensor contract、estimator revision、initialization、tracking state、pose timestamp与covariance；只有一个`x,y,yaw`或`localization_valid=true`字段不能证明这些条件。

## 6. Typed Localization / SLAM Manifest

```json
{
  "sensor_contract": {
    "camera_imu_lidar_encoder_ids": [],
    "intrinsics_extrinsics_sha256": "...",
    "axis_unit": "REP-103-like or explicit custom convention",
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

同一个pose若缺map revision、estimator state或alignment protocol，既不可复算也不可用于比较；同一数值在`map`与`odom`中的控制语义也不同。

## 7. Frame Tree：Global Consistency 与Local Continuity分工

典型组合为：

\[
T^{\mathrm{map}}_{\mathrm{base}}(t)
=
T^{\mathrm{map}}_{\mathrm{odom}}(t)
T^{\mathrm{odom}}_{\mathrm{base}}(t).
\]

变量解释：`T^A_B`把B-frame量变到A-frame；`odom→base`来自连续local odometry，`map→odom`来自global localization/SLAM correction。直觉是局部控制保持连续，而global loop/relocalization通过更新`map→odom`修正长期漂移。实现映射：consumer必须记录使用的frame、TF timestamp与revision；PER-015 action target若跨一次global correction必须重新验证，而不是把旧map pose静默复用。

不能写成“map比odom更准所以控制一律用map”：global correction可产生跳变；若controller把跳变当真实速度，会形成危险命令。也不能写成“odom连续所以真实”：连续只是不跳，不代表长期无漂移。

## 8. State Estimation、IMU Propagation 与Update

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

变量解释：`R,p,v`是orientation、position、velocity，`b^g,b^a`是gyro/accelerometer bias，`P`是state covariance，`F,Q`是linearized transition与process noise。直觉是IMU高频propagation快速给pose，但noise和bias会让uncertainty增长；camera/feature update再约束状态。实现映射：OpenVINS `Propagator.cpp`负责propagation，`UpdaterMSCKF.cpp/UpdaterSLAM.cpp`负责不同feature update；代码存在不代表本地noise/calibration参数正确。

VINS-Mono和Kimera使用preintegration把两个keyframes间许多IMU sample压成relative-motion factor，并在bias更新后修正。preintegration不是“把IMU平均一下”；它需要timestamp、gravity、bias、noise与camera–IMU extrinsic合同。

## 9. Front-end 与Back-end

```text
sensor packets
  -> frontend: detect/track/scan-match, keyframe, candidate association
  -> local estimator: propagation + local window/filter update
  -> backend: factors/constraints, marginalization, robust optimization
  -> global layer: place recognition, geometric verification, pose graph/map merge
  -> typed map/odom state + covariance + tracking status
```

| 层 | 主要职责 | 失败证据 |
| --- | --- | --- |
| frontend | feature/scan/data association、motion filter、keyframe | inlier count、photometric/geometric residual、blur/dynamic mask |
| local estimator | current state、bias、scale、local map/window | innovation、covariance、conditioning、lost state |
| backend | nonlinear objective、marginalization、factor consistency | cost、marginal prior、factor residual、solver status |
| global | place recognition、loop/map merge、global consistency | candidate score、geometric inliers、loop residual、graph delta |

前端“跟到了很多点”不等于后端状态正确；后端cost下降也不等于frame/time/scale合同正确。

## 10. Local Optimization 与Gauge

一般鲁棒估计目标可写为：

\[
\hat{\mathcal X}
=
\arg\min_{\mathcal X}
\sum_{i\in\mathcal F}
\rho_i\!\left(
\|\mathbf r_i(\mathcal X;\mathbf z_i)\|_{\Sigma_i^{-1}}^2
\right).
\]

变量解释：`\mathcal X`含poses、velocity、bias、landmarks或depth；`\mathcal F`是visual/IMU/scan/loop factors；`\rho`是robust loss；`\Sigma`是measurement covariance。直觉是不同sensor约束共同决定状态，outlier需要robust handling。实现映射：VINS sliding window、Cartographer scan/pose graph、DROID dense BA、Kimera factor graph使用不同residual和solver，不能只比较“都做optimization”。

SLAM存在gauge freedom：没有anchor时，整条trajectory与map可共同平移/旋转而不改变relative residual；monocular还常有scale ambiguity。评估中的alignment处理gauge，但alignment本身必须进入协议身份。

## 11. Keyframe、Sliding Window 与Marginalization

保留所有frame会使状态与计算不断增长；keyframe/window只保留信息量更高的状态，并把旧变量影响压入prior。风险是：

- marginalization linearization point固定后可能产生inconsistency；
- 错误data association可进入prior并长期影响；
- window太短丢长期约束，太长增加latency/memory；
- keyframe规则改变graph、loop candidate与metric，属于protocol identity。

VINS-Mono `estimator.cpp`与Kimera `VioBackend.cpp`支撑window/factor backend；OpenVINS clone/state management支撑filter family。不能把“filter一定快、optimization一定准”当普遍结论。

## 12. Loop Closure、Relocalization 与Map Merge

### 12.1 Loop Closure合同

```text
place candidate
 -> temporal / map exclusion
 -> descriptor or learned match
 -> geometric verification + relative pose
 -> robust residual / switch / inlier gate
 -> pose-graph optimization
 -> map-to-odom correction + map revision
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

变量解释：`Z_{ij}`是odometry或loop relative-pose measurement，`\Omega_{ij}`是information matrix，`T_i`是node pose。直觉是让graph中所有relative constraints尽量一致，同时让robust loss抑制outlier。实现映射：VINS `pose_graph.cpp`保存drift transform并做4-DoF optimization；ORB-SLAM3 `LoopClosing.cc`区分loop与merge；Cartographer构建node/submap constraint；Kimera论文的RPGO强调robust PGO。

### 12.2 三者差别

| 事件 | 触发 | 输出 | 不能偷换 |
| --- | --- | --- | --- |
| relocalization | tracking lost / known map | current pose恢复、tracking state变化 | 不一定新增loop或改全图 |
| loop closure | current与history同地点 | loop constraint、global correction | candidate不是verified constraint |
| map merge | current map与another map/session重叠 | inter-map transform与map fusion | 不等于简单拼接point clouds |

ORB-SLAM3 Atlas在tracking lost时可新建map并尝试跨map relocalization/merge；VINS-Mono把relocalization与4-DoF global pose graph并发。公开机制不能反推用户项目具有相同thread/state machine。

## 13. Drift Taxonomy 与可观性

| Drift / failure | 来源 | 第一检查 |
| --- | --- | --- |
| translation drift | incremental noise、poor geometry、scan/feature mismatch | RPE、inliers、motion excitation |
| yaw drift | gyro bias、弱heading约束 | bias、gravity alignment、loop |
| scale drift | monocular gauge/weak excitation | sensor mode、Sim(3) vs SE(3) |
| vertical drift | IMU bias/gravity/ground assumption | gravity、bias、frame convention |
| time drift | clock skew、delayed packet、wrong interpolation | timestamp/clock/queue age |
| map corruption | false loop、dynamic object、wrong map | loop residual、graph delta、map UUID |
| tracking loss | blur、occlusion、textureless/dynamic scene | frontend status、relocalization log |
| jump | global correction/relocalization | map→odom update、consumer frame |

IMU提高metric scale、gravity与short-term motion约束，但bias和extrinsic/time错误也会系统性污染估计；loop closure减长期drift，但false loop可能比不闭环更坏。

## 14. Learned SLAM 的位置

DROID-SLAM通过recurrent update operator在dynamic frame graph上预测correspondence update，再调用differentiable dense BA更新pose与inverse depth。它展示learned front/back-end coupling，但仍需要：

- camera intrinsics与input preprocessing；
- checkpoint/training-domain identity；
- frame graph/keyframe/memory阈值；
- inference latency与GPU memory；
- trajectory filling、termination与failure status；
- same-protocol ATE/RPE comparison。

所以“learned”不意味着不需要geometry/protocol；“端到端”也不意味着没有graph、BA或显式state。

## 15. ATE、RPE 与Alignment Protocol

Absolute Trajectory Error在时间关联和alignment后可写为：

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

变量解释：`\hat T_i`是estimate，`T_i^*`是ground truth，`T_{\mathrm{align}}`由SE(3)或Sim(3) alignment得到。直觉是比较global trajectory shape/pose；实现映射：必须记录association tolerance、alignment family、失败段与单位。给`[5,6,7]`对`[0,1,2]`做translation alignment可把raw RMSE 5降到0，说明alignment不是无关细节。

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

变量解释：`\Delta`可按frame、time或distance定义。直觉是测local motion drift，较少受global offset影响。实现映射：probe中GT step为1、estimate step为1.1，translation RPE RMSE为0.1；必须报告`\Delta`和采样方式。

| Metric | 主要回答 | 必须冻结 |
| --- | --- | --- |
| ATE | global trajectory一致性 | association、SE3/Sim3、unit、failure truncation |
| RPE | local incremental drift | delta definition、rotation/translation reduction |
| drift % | 路程归一化长期误差 | segment length、route、loop policy |
| lost/relocal | 可用性与恢复 | lost definition、timeout、denominator |
| loop P/R | place/constraint质量 | candidate vs verified、GT loop definition |
| map quality | occupancy/mesh/landmark | pose source、coverage、resolution、threshold |

## 16. 十个Deterministic Probes

| Probe | 固定输入 | 结果 | 教学结论 |
| --- | --- | --- | --- |
| map/odom composition | `map→odom=-2m`，`odom→base=10m` | `map→base=8m` | frame chain必须显式 |
| SE(2) roundtrip | yaw 90°、t `[2,3]`、p `[1,0]` | q `[2,4]`，inverse error `6.12e-17` | 方向/inverse可测 |
| covariance | P0 `.01`、Q `.04`、10步、R `.09` | prior `.41`，K `.82`，post `.0738` | 无update uncertainty增长 |
| ATE alignment | GT `[0,1,2]`，est `[5,6,7]` | raw 5，aligned 0 | alignment属于metric身份 |
| RPE | GT step 1，est step 1.1 | RMSE `.1` | local drift与global offset分开 |
| false loop | chain x2=2，loop要求x2=0 | residual 2>.5，reject | candidate不能直接进graph |
| scale protocol | est `[0,1.2,2.4]` | SE3 RMSE `.1633`，Sim3 scale `.8333`后0 | Sim3会隐藏scale error |
| correction jump | map pose `10→8.6`，odom delta `.1` | map delta `-1.4` vs odom `.1` | controller避免global jump |
| timestamp | `[0,.1,.09]` | non-monotonic reject | order/clock属于输入身份 |
| local fallback | `runtimeReady=false/softwareOnly=true` | localization gate false | map asset不等于live localization |

10个probe得到`10/10 expected decisions matched`。它们验证合同和metric反例，不是六个系统的benchmark复现。

## 17. First-divergence Failure Diagnosis

| 表面症状 | 第一检查层 | 关键证据 | 常见误诊 |
| --- | --- | --- | --- |
| pose整体翻转/旋转 | frame direction/axis | T convention、REP/custom axes | 调loop threshold |
| 开始即漂 | init/scale/gravity | excitation、bias、sensor mode | 只怪地图 |
| 匀速累积误差 | odometry frontend/local estimator | RPE、bias、inliers | 直接加global BA |
| 某时刻突然跳 | map→odom correction | loop/relocal event、graph delta | 当真实高速运动 |
| 闭环后全图扭曲 | false loop/weight | geometric inliers、loop residual | 说optimizer失败 |
| tracking反复lost | frontend/sensor | blur、texture、dynamic、timestamp | 只加keyframes |
| ATE很好但尺度错 | alignment | Sim3/SE3与scale output | 报metric scale成功 |
| map可见但机器人不动 | localization/controller boundary | runtimeReady、pose age、frame | 报SLAM成功 |
| 同轨迹不同分数 | evaluation protocol | association/alignment/truncation | 报模型回归 |
| 重启后位置错误 | map/session identity | map UUID、load path、relocal log | 归因random seed |

诊断顺序：`sensor/time/calibration → frame/init/scale → frontend association → local estimator/covariance → loop geometric gate → graph correction/map revision → metric protocol → planner/controller consumer`。

## 18. Fail-closed Localization Pipeline 伪代码

```python
def update_localization(packet, manifest, estimator, map_bundle):
    # 1. Reject missing identity; never guess sensor/frame/time/map revision.
    require(packet, ["sensor_id", "timestamp_ns", "frame_id", "calibration_sha256"])
    require(manifest, ["estimator_revision", "frame_contract", "evaluation_contract"])
    if packet.timestamp_ns <= estimator.last_timestamp_ns:
        return {"status": "reject", "reason": "NON_MONOTONIC_TIME"}

    # 2. Propagate local state and covariance with the frozen sensor model.
    predicted = estimator.propagate(packet.imu, manifest.noise_bias_model)
    if not predicted.finite or predicted.covariance_exceeds(manifest.local_risk_budget):
        return {"status": "lost", "reason": "PROPAGATION_UNCERTAIN"}

    # 3. Frontend measurements may be absent or outliers; keep status explicit.
    measurements = estimator.frontend(packet)
    local = estimator.local_update(predicted, measurements)
    if not local.valid:
        relocalized = estimator.relocalize(packet, map_bundle)
        if not relocalized.geometrically_verified:
            return {"status": "lost", "reason": "RELOCALIZATION_FAILED"}
        local = relocalized.state

    # 4. A place candidate is not a loop constraint until geometry passes.
    candidate = estimator.detect_loop(local, map_bundle)
    if candidate is not None:
        verified = estimator.verify_loop(candidate, manifest.loop_gate)
        if verified.accepted:
            optimized = estimator.optimize_pose_graph(verified.constraint)
            if optimized.max_residual > manifest.graph_residual_limit:
                return {"status": "reject_loop", "reason": "GRAPH_INCONSISTENT"}
            map_bundle = optimized.new_map_revision

    # 5. Publish continuous odom->base and separately revisioned map->odom.
    return {
        "status": "tracking",
        "odom_to_base": local.odom_to_base,
        "map_to_odom": estimator.map_to_odom(map_bundle),
        "covariance": local.covariance,
        "map_revision": map_bundle.revision,
        "robot_success": None,
    }
```

伪代码保留`initializing/tracking/lost/relocalized/reject_loop`状态与map revision；它是目标合同，不是五项目已有实现。生产系统还需queue/backpressure、sensor dropout、concurrent map update、TF cache、kidnapped-robot处理、watchdog与controller stop。

## 19. Public Method → Code Mapping

| 机制 | fixed code | 面试可讲 | 不能反推 |
| --- | --- | --- | --- |
| tracking/relocal/map atlas | ORB-SLAM3 Tracking/LoopClosing/Atlas | lost/relocalization、loop vs merge、multi-map | local deployment |
| sliding-window VIO | VINS estimator/IntegrationBase | preintegration、marginalization、bias/scale | arbitrary sensor robustness |
| drift/pose graph | VINS pose_graph | world↔VIO transform、4-DoF optimize | false loop automatically rejected |
| local/global LiDAR SLAM | Cartographer local builder/constraint/pose graph | submap、scan match、global loop | visual/map semantics |
| learned dense BA | DROID droid/factor graph/backend | recurrent update + dense BA | checkpoint/latency/generalization |
| modular EKF | OpenVINS manager/propagator/updaters | state/covariance、MSCKF vs SLAM update | full global SLAM |
| VIO + loop candidate | Kimera frontend/backend/LCD | stereo+IMU、factor graph、loop detection | selected repo alone equals full Kimera stack |

## 20. 本地五项目 Inventory 与Direct Audit

### 20.1 Canonical Inventory

| Inventory | Canonical SHA-256 | 当前安全结论 |
| --- | --- | --- |
| [OPD](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | 2D point/box/relation与static holdout；无sensor trajectory/SLAM |
| [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | image/language/action training与sim diagnostics；无localization/map graph |
| [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | occupancy/PCD/map/state bridge；fallback不是live localization |
| [WAM](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | video/action/world-model diagnostic；无sensor estimator/SLAM result |
| [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | LIBERO/RoboCasa state/action protocol；sim state不是SLAM |

### 20.2 Robot Harness Local-direct Exceptions

| fixed file | SHA-256 | 直接发现 | 不能升级 |
| --- | --- | --- | --- |
| `server/sim/ros2_bridge.py` | `8291D64DE01AAC2EFDF52409008EFD7AE18C5FEC0BA7B9D4677F6636F8287A48` | occupancy/PCD/reloc poses路径、pixel↔world、state file与fallback enrichment | estimator、live TF、loop closure |
| `server/sim/acerobotics_sim.py` | `E373090035AADBCBECD7016698175345804194CC727969ECC972AC97CCCE9EBE` | simulator fixture含`localization_mode/map_id/valid`字段 | field来自真实localizer |
| `server/tests/test_acerobotics_ros2_backend.py` | `A0FE082007E68BBFA8CA7A535E67ECBF5935B55DB28C52A449694B3C0773B1FB` | fallback test断言`runtimeReady=false`与map asset | live runtime pass |
| `occupancy2d_map.json` | `40A2CE540AC214CABA987BB2BCF3542B197207A9F25D96298C2E65167808EA37` | 0/127/255语义、0.02m resolution、origin与conversion params | map trajectory/loop provenance |
| `world.pcd` | `494A53320AF2EC10C4D1AADD17CE0F7D943820BA34536C23871BB5CA711F0B42` | PCD v0.7，`x y z intensity timestamp ring`，54,856点 | active localization或semantic map |
| `reloc_map/poses.txt` | `C0FBC83966782D16A91886B7627CAF9597D87F076934CC7CBC097D851477315C` | timestamp + pose/quaternion-like 8列asset | estimator/config/map UUID/online relocalization success |

定向测试`python -m pytest -q server/tests/test_acerobotics_ros2_backend.py::test_ros2_state_fallback_uses_real_sensebot_asset`结果为`1 passed`并有2条Tortoise `pk` deprecation warnings。它只证明offline fallback能装载real map asset；测试明确断言`runtimeReady is False`、`runtimeRealApiCalls is False`。OPD/OpenPiVLA/WAM/UWM的选定本地实现路径对`SLAM/odometry/map_frame/pose graph/loop closure/relocalization/drift`没有direct estimator命中；inventory不证明所有远端/历史分支绝对不存在。

## 21. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 最小补强artifact |
| --- | --- | --- | --- |
| OPD | 2D grounding可为localizer/semantic map提供上游观测 | 已做3D localization/semantic SLAM | sensor/pose/map manifest、trajectory与query绑定 |
| Robot Harness | map asset schema、pixel/world bridge、software-only state接口 | 已实现/部署SLAM、loop closure或可靠relocalization | sensor bag、calibration、estimator config/commit、TF/pose graph、ATE/RPE、live logs |
| OpenPiVLA | policy消费image/state/action的接口诊断 | policy结果证明localization正确 | frame/pose lineage、localizer status、matched rollout |
| WAM | video/world/action trace可讨论pose-error sensitivity | world model等于SLAM或定位提升 | camera trajectory、estimator/map revision、paired evaluation |
| UWM | simulator state/action protocol | simulator ground-truth state等于估计器输出 | noisy observation estimator、pose protocol与raw trajectory |

安全回答顺序：`public method → fixed official code → local inventory → local-direct asset/interface → missing estimator/runtime → candidate ownership`。地图文件、字段名、ROS目录或Git author都不能替代个人实现与matched result证据。

## 22. Source Gate 与下一切片

本轮已关闭：

- 六份primary paper完整PDF、SHA、全文解析与代表页视觉检查；
- 六个official repo固定commit/date/license，36个核心文件逐字节SHA；
- localization/odometry/SLAM/relocalization/loop/map-merge边界；
- `map→odom→base`、typed manifest、state/covariance、front/back end、pose graph、drift与ATE/RPE protocol；
- 10个deterministic probes，全部命中预期结果；
- 五份canonical inventory、Robot Harness六个local-direct exceptions与一个fallback test的真实性边界。

仍为`WARN`：本地没有sensor bag/clock/calibration lineage、estimator config/checkpoint、live TF、pose/covariance stream、keyframe/landmark/submap/pose graph、loop accept/reject log、map UUID/revision、ATE/RPE trajectory bundle、lost/relocalization denominator、matched planner/controller episode或逐文件候选人ownership闭环。primary paper与official code不能替代这些artifact。

`VLA-PER-016 source freeze`、下游knowledge与一张atomic card已在三个独立bounded slices同步；新卡与其余266张题卡共267张均保持`unseen`，不创建`coaching_state.md`，不改变任何mastery。下一bounded slice只冻结`VLA-PER-017` belief/memory/frontier/active-exploration source；不生成其knowledge/card。

## References

1. Campos et al., [ORB-SLAM3 v2](https://arxiv.org/pdf/2007.11898v2)；[official code@4452a3c](https://github.com/UZ-SLAMLab/ORB_SLAM3/tree/4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4)。
2. Qin et al., [VINS-Mono v1](https://arxiv.org/pdf/1708.03852v1)；[official code@90dabb5](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/tree/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d)。
3. Hess et al., [Real-Time Loop Closure in 2D LIDAR SLAM](https://research.google.com/pubs/archive/45466.pdf)；[Cartographer code@877157a](https://github.com/cartographer-project/cartographer/tree/877157a0d91788a7700221d87232d412cb3c1ef4)。
4. Teed & Deng, [DROID-SLAM v2](https://arxiv.org/pdf/2108.10869v2)；[official code@2dfd39f](https://github.com/princeton-vl/DROID-SLAM/tree/2dfd39f0dcad44012ca7bbb8aa70b55edbfa9c99)。
5. Geneva et al., [OpenVINS ICRA 2020](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf)；[official code@6948812](https://github.com/rpng/open_vins/tree/69488123ed9362dd44b6f28e7f4680abbff1442b)。
6. Rosinol et al., [Kimera v3](https://arxiv.org/pdf/1910.02490v3)；[Kimera-VIO code@ce8c59b](https://github.com/MIT-SPARK/Kimera-VIO/tree/ce8c59b7b273ab5ac29db7e5572e1623760e19c7)。
7. ROS REP-105，[Coordinate Frames for Mobile Platforms@11ca24a](https://github.com/ros-infrastructure/rep/blob/11ca24a41f31480dfb9562ba99f2a5b93d3ebda5/rep-0105.rst)。
8. [PER-002 3D Lift / Frame Source](vol_06_per002_3d_lift_frame_source_freeze.html)、[PER-003 Multi-view / Temporal Source](vol_06_per003_multiview_temporal_source_freeze.html)、[PER-005 Navigation Policy Source](vol_06_per005_navigation_policy_architecture_source_freeze.html) 与 [PER-015 Perception→Action Gate Source](vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
