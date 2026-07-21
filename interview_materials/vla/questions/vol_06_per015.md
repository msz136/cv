# VOL 06 Perception / Grounding / Navigation：PER-015 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-015`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Knowledge](../knowledge/vol_06_per015_perception_action_reachability_uncertainty_failure_gate.html)；来源边界见 [PER-015 Source Freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)。

## Perception→Action、Reachability、Uncertainty 与 Failure Gate

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-015</b> · VLA从semantic target到controller-ready action要过哪些gate？可达性、不确定性和失败怎样处理？</summary>

**面试意图**：判断你能否把semantic target转成typed action target，区分workspace、IK、bounds、singularity、state/motion collision、trajectory、controller与uncertainty的责任边界，并在项目追问中坚持“gate通过不等于robot success”。

**30 秒回答**：先把语义目标补成带坐标系、单位、时间、工具与机器人/场景/控制器版本的动作目标；再查工作空间、IK残差、关节限位、奇异性、状态/路径碰撞、误差膨胀安全间距、速度加速度与控制器字段。任一层未知都拒绝执行，风险超预算就重感知、重规划、求助或停止；全通过也只是控制器候选，不是机器人成功。

**机制展开（约 2 分钟）**：工作空间只做粗拒绝；IK返回后以FK重算SE(3)位置/姿态残差，再验关节界与Jacobian最小奇异值。MoveIt PlanningScene负责状态/碰撞语义，OMPL和RRT-Connect依赖外部状态与边验证，因此终点无碰撞不等于整条路径安全；场景、ACM、膨胀量和离散分辨率都属结果身份。几何路径还要定时并检查速度、加速度、当前状态、关节顺序/单位/执行状态与动作块过期。不确定性分语义、几何、执行；KnowNo式conformal set只给校准假设下的边际覆盖，非单元素时求助，不能当物理安全证明。

**诊断 / 证据**：按first divergence检查frame/unit/time/revision与target age→semantic candidate/score→workspace→IK solver return之后的FK residual、q bounds与σmin→同一scene revision下的goal state、每条edge、ACM/padding/resolution与uncertainty-inflated clearance→q/qdot/qddot、timestamps、branch continuity与chunk staleness→controller shape/semantics/order/unit/current-state/status→calibration split、qhat、prediction-set size→execution/contact/task outcome。确定性probe至少保留2R半径1.8超出上界1.7、IK residual 0.407507m超0.01、q1=π/2超`[-1,1]`、伸直位形σmin=0、端点安全但edge穿AABB、clearance膨胀0.10→0.20使pass翻reject、dt=0.1得到vmax=10/amax=50、risk upper 0.12>α=0.05触发ask、age 240ms>100ms和expected 7D/got 12D拒绝。

**项目挂钩**：OPD只能提供2D point/box/relation与grounding score上游，不能推出metric 3D target、IK或collision。Robot Harness有tool scope、lock、timeout/cancel、best-effort compensation与map/PCD bridge，但tool sandbox不是机械臂物理安全。OpenPiVLA有action JSON/full-chat CE及official checkpoint diagnostics，formal generation/parser/controller仍缺；WAM只有7D→12D、OSC_POSE与失败trace诊断；UWM只有7D/16-step LIBERO和RoboCasa action-order/controller probe。五项目都没有统一robot/tool/scene manifest、IK/collision/TOTG raw report、calibrated risk–coverage、controller execution trace、matched robot episode或已确认ownership，因此只能讲interface/diagnostic hook，不能说已部署通用gate或获得robot uplift。

**追问树**：semantic target与action target字段差在哪？为什么frame/unit/time/revision属于结果身份？workspace内为何仍可能IK无解？solver success后为何重算FK residual？位置与姿态tolerance怎样分开？TRAC-IK改善什么又不负责什么？σmin和manipulability怎样用？goal无碰撞为何不够？state validity与motion validity有何区别？OMPL为何不自带robot collision geometry？resolution、ACM、attached object与padding怎样改变结论？uncertainty inflation如何让pass翻reject？几何path为何还不是trajectory？action chunk何时stale？controller shape相同为何仍可能语义错？conformal prediction保证什么、不保证什么？ask、re-perceive、replan、re-time、reject、stop怎样区分？怎样定位first-divergence？五项目分别最多支持哪一级claim？全部gate通过后为什么仍不能报success？

**易错点**：把3D点直接送IK；把workspace内当pose可达；只看solver return不重算residual；clamp关节后不复验；把TRAC-IK说成带mesh collision；把goal collision-free当整条edge安全；不冻结scene/ACM/resolution；只给target加covariance却不膨胀clearance；把几何path当动态可执行轨迹；silent slice/pad action；把未校准confidence叫逐样本安全概率；把conformal marginal coverage叫硬件认证；把fallback写成默认动作；把server/tool返回或单次sim success当robot success；用公开机制、目录或Git身份替代本地runtime与ownership。

**危险答案**：说“找到目标后做IK和RRT就能执行”“MoveIt会自动保证安全”“confidence低就慢一点”“7D向量shape一致即可”“controller返回success就是任务成功”“Harness已有physical safety gate”“WAM action trace证明reachability改善”，却不交代typed manifest、residual/bounds/singularity、state/edge collision、robust clearance、timing/controller contract、calibration/abstention、fresh-state/cancel acknowledgement、raw episode与ownership缺口。

**来源**：[1][2][3][4][5][6][7][8][9]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-015 Perception→Action / Reachability / Uncertainty / Failure Gate Knowledge](../knowledge/vol_06_per015_perception_action_reachability_uncertainty_failure_gate.html)：typed manifest、九层gate、10个probe、first-divergence diagnosis、两档回答与五项目truth boundary。
2. [PER-015 Source Freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)：六份完整primary PDF、六个official repositories/35文件、10个deterministic probes与11个local-direct文件审计。
3. Lynch & Park, [Modern Robotics](https://hades.mech.northwestern.edu/images/7/7f/MR.pdf)；[official code@cbd41fd](https://github.com/NxRLab/ModernRobotics/tree/cbd41fdf0bf75dbd5e986d832ae14226964ff0ac)。
4. Kuffner & LaValle, [RRT-Connect](http://www.kuffner.org/james/papers/kuffner_icra2000.pdf)；[OMPL official code@eb3baca](https://github.com/ompl/ompl/tree/eb3baca772ab2c76f5943934b505751e031ff34c)。
5. Beeson & Ames, [TRAC-IK](http://irl.cs.brown.edu/pubs/trac-ik.pdf)；[official source@57057ce](https://bitbucket.org/traclabs/trac_ik/src/57057ce79ec1dd07aa5c1b46e134c701943dee6d/)。
6. Ren et al., [KnowNo v2](https://arxiv.org/abs/2307.01928v2)；[official code@95e3a1d](https://github.com/google-research/google-research/tree/95e3a1da2d27cb9c8289f6fd3076cfed608c3c94/language_model_uncertainty)。
7. [MoveIt 2 official code@2fb8492](https://github.com/moveit/moveit2/tree/2fb8492b64ceb426d96e7f97e71846fb91394aa2)。
8. Shridhar et al., [CLIPort v1](https://arxiv.org/abs/2109.12098v1)；[official code@2be5c47](https://github.com/cliport/cliport/tree/2be5c47b5bb9bb7040ad90693288b87b1e18e7ad)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
