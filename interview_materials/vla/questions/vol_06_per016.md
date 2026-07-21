# VOL 06 Perception / Grounding / Navigation：PER-016 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-016`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-016 Localization / Odometry / SLAM / Map-frame / Drift Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.html)；来源边界见 [PER-016 Source Freeze](../sources/vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html)。

## Localization、Odometry、SLAM、Map Frame 与 Drift

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-016</b> · 机器人怎样定位自己？Odometry、Localization和SLAM如何区分，map/odom、loop closure、drift与ATE/RPE怎样讲？</summary>

**面试意图**：判断你能否从sensor/clock/calibration身份讲到state/covariance、local/global frame、verified loop与map revision，再用ATE/RPE/alignment解释评估，并在项目追问中坚持“map资产不等于SLAM runtime”。

**30 秒回答**：Odometry积累相邻运动，连续但会漂；localization在有UUID和版本的已知地图里估位姿；SLAM共同估轨迹与地图。控制用连续`odom→base`，回环或重定位更新跳变的`map→odom`。回环候选须过几何验证、相对位姿和图残差门。ATE看全局轨迹，RPE看局部漂移，并冻结时间关联、SE3/Sim3、单位与丢失段；Sim3会隐藏尺度误差。

**机制展开（约 2 分钟）**：先固定sensor、时钟、内外参、噪声、estimator/config/checkpoint和map revision。IMU传播pose/velocity/bias与covariance，视觉或scan更新；VINS/Kimera用preintegration与滑窗，OpenVINS是EKF。前端关联、局部估计、后端因子和全局层分责。Loop按候选→几何→relative transform→robust pose graph→新map版本，false loop会毁图；relocalization恢复当前pose，map merge对齐不同session。ATE/RPE要报告alignment、delta和failure denominator，不能用一个分数代表可用性、尺度和地图质量。

**诊断 / 证据**：按first divergence检查sensor ID/packet order/clock→calibration与frame方向→initialization/scale/gravity→frontend inliers/geometry residual→local state、bias、covariance、conditioning与marginal prior→loop candidate、geometric inliers、relative transform、graph residual与map revision→timestamp association、SE3/Sim3、RPE delta、unit与lost denominator→planner/controller是否消费stale或jumped pose。确定性probe至少保留`map→odom=-2m`与`odom→base=10m`合成8m、SE2 roundtrip误差`6.12e-17`、P0=.01/Q=.04十步得到prior .41且update后.0738、ATE raw 5对齐后0、RPE .1、false-loop residual 2>.5拒绝、scale 1.2经Sim3归零、map delta -1.4而odom delta .1、非单调时间拒绝和`runtimeReady=false/softwareOnly=true`不通过localization gate。

**项目挂钩**：Robot Harness有0/127/255三态occupancy、0.02m resolution、54,856点`x y z intensity timestamp ring` PCD、`reloc_map/poses.txt`、pixel/world与state bridge；fallback targeted test为`1 passed`，但明确`runtimeReady=false/runtimeRealApiCalls=false`，没有sensor bag、clock/calibration lineage、estimator config/checkpoint、live TF、pose/covariance、keyframe/pose graph、loop accept/reject或ATE/RPE bundle。OPD只有2D point/box/relation上游；OpenPiVLA只有image/state/action接口；WAM只有video/world/action诊断；UWM用sim ground-truth state。五项目都不能升级为候选人已实现SLAM、定位提升或真实robot result，Git身份、ROS目录与map资产也不能替代runtime和ownership。

**追问树**：tracking、odometry、localization、mapping与SLAM各估什么？有`x,y,yaw`为何不等于定位有效？`map→odom→base`各由谁维护？为什么map可跳而odom可漂？controller直接吃map pose有什么风险？IMU传播为何增大covariance？preintegration依赖哪些clock/bias/extrinsic合同？前端点多为何仍可能错？cost下降为何不证明frame/time正确？filter与sliding window怎样公平比较？gauge和monocular scale ambiguity是什么？keyframe/window/marginalization怎样取舍？loop candidate到graph edge有哪些门？false loop为何比不闭环更坏？relocalization、loop closure与map merge怎样区分？pose graph中的`Z_ij/Ω_ij`是什么？DROID learned为何仍有graph与BA？ATE与RPE分别回答什么？SE3与Sim3隐藏什么？lost/relocal denominator怎样定？map quality与trajectory quality为何分开？Robot Harness的PCD、reloc poses与green fallback test最多支持什么claim？

**易错点**：把tracking/odometry/localization/SLAM混成pose输出；把连续当准确、global当平滑；让controller消费global correction jump；说IMU自动消除scale/drift；把preintegration说成平均；用inlier多或cost低代替frame/time验证；把place similarity直接加图边；把relocalization等同loop、点云拼接等同map merge；无条件声称filter快、optimization准；只报ATE不报alignment、RPE、lost；用Sim3后ATE证明metric scale；把DROID说成无geometry；用PCD、occupancy、ROS路径、fallback test或Git身份证明本地SLAM与ownership。

**危险答案**：说“SLAM就是前端提特征、后端BA”“map比odom准所以控制都用map”“有IMU就不漂”“检索到相似地点就闭环”“ATE低就是定位好”“Sim3只是换坐标”“DROID端到端不需要几何”“Harness已经有PCD和reloc map，所以做了SLAM”，却不交代sensor/clock/calibration、state/covariance、frame authority、loop geometry/graph residual、map revision、alignment/delta/denominator、live estimator artifact与候选人ownership。

**来源**：[1][2][3][4][5][6][7][8][9]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-016 Localization / Odometry / SLAM / Map-frame / Drift Knowledge](../knowledge/vol_06_per016_localization_odometry_slam_map_frame_drift.html)：typed manifest、map/odom、state/covariance、loop/relocal/map merge、drift、ATE/RPE、10 probes、两档回答与五项目truth boundary。
2. [PER-016 Source Freeze](../sources/vol_06_per016_localization_odometry_slam_map_frame_drift_source_freeze.html)：六份完整primary PDF、六个official repositories/36文件、REP-105、10个deterministic probes与Robot Harness local-direct audit。
3. Campos et al., [ORB-SLAM3 v2](https://arxiv.org/pdf/2007.11898v2)；[official code@4452a3c](https://github.com/UZ-SLAMLab/ORB_SLAM3/tree/4452a3c4ab75b1cde34e5505a36ec3f9edcdc4c4)。
4. Qin et al., [VINS-Mono v1](https://arxiv.org/pdf/1708.03852v1)；[official code@90dabb5](https://github.com/HKUST-Aerial-Robotics/VINS-Mono/tree/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d)。
5. Hess et al., [Real-Time Loop Closure in 2D LIDAR SLAM](https://research.google.com/pubs/archive/45466.pdf)；[Cartographer code@877157a](https://github.com/cartographer-project/cartographer/tree/877157a0d91788a7700221d87232d412cb3c1ef4)。
6. Teed & Deng, [DROID-SLAM v2](https://arxiv.org/pdf/2108.10869v2)；[official code@2dfd39f](https://github.com/princeton-vl/DROID-SLAM/tree/2dfd39f0dcad44012ca7bbb8aa70b55edbfa9c99)。
7. Geneva et al., [OpenVINS ICRA 2020](https://pgeneva.com/downloads/papers/Geneva2020ICRA.pdf)；[official code@6948812](https://github.com/rpng/open_vins/tree/69488123ed9362dd44b6f28e7f4680abbff1442b)。
8. Rosinol et al., [Kimera v3](https://arxiv.org/pdf/1910.02490v3)；[Kimera-VIO code@ce8c59b](https://github.com/MIT-SPARK/Kimera-VIO/tree/ce8c59b7b273ab5ac29db7e5572e1623760e19c7)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
