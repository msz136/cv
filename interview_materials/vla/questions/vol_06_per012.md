# VOL 06 Perception / Grounding / Navigation：PER-012 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-012`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-012 Segmentation / Depth / Keypoint / Affordance Knowledge](../knowledge/vol_06_per012_segmentation_depth_keypoint_affordance.html)；来源边界见 [PER-012 Source Freeze](../sources/vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html)。

## Segmentation、Depth、Semantic Keypoint 与 Manipulation Affordance

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-012</b> · 如何把segmentation、depth、keypoint与affordance串成机器人可用的操作目标？为什么单模块高分不等于robot success？</summary>

**面试意图**：判断你能否先冻结segmentation/depth/keypoint/affordance的task、unit、frame与score semantics，再把2D输出组合成3D proposal并经过planner/controller gate；同时识别public method、本地point supervision和真实机器人闭环之间的证据边界。

**30 秒回答**：先冻结task/unit：四类mask不等价，relative depth不能当米。mask与metric depth对齐原图、内参和时间才能lift；keypoint需语义ID、frame与不确定性，affordance绑定点、方向、primitive和state，最后过IK、碰撞与控制门。OPD证明affordance-labelled point监督。

**机制展开（约 2 分钟）**：Mask2Former的class+mask需按semantic/instance/panoptic分别后处理；SAM的prompt、多候选和quality没有类别、跨帧身份或robot校准。Depth Anything V2 relative路径是ReLU图，metric路径是独立checkpoint与Sigmoid×max_depth，resize只恢复shape。只有米制depth与mask、原像素、内参、配准和时间一致才能lift。kPAM keypoint带语义ID、visibility、covariance与frame；Where2Act proposal绑定点、方向、primitive和state，最终过reachability、IK、collision与controller。

**诊断 / 证据**：按first-divergence检查task/schema→prompt/candidate policy→model/checkpoint/license→pre/postprocess→depth relative/metric、unit/range/validity→RGB-depth registration、intrinsics、TF/time→semantic keypoint identity/visibility/covariance→affordance primitive/state/orientation→planner rejection与episode trace。确定性probe应覆盖two-mug semantic/instance差异、同click的SAM multimask、relative scale×2、metric `max_depth=20/80`、resize后仅shape恢复、同坐标不同keypoint语义、同点push/pull score变化，以及正确mask+错误depth导致3D整体漂移。

**项目挂钩**：本地OPD的ShareRobot `affordance{x,y}`被缩放为0..1000并写成`<point>[[x,y]]</point>`；prompt虽写actionable location，训练与评估仍走point/box/text target、parser和static metric。选定五个文件没有显式SAM/mask polygon/depth/keypoint实现命中，这只支持“affordance-labelled point supervision”，不排除远端或未归档路径，也不证明dense affordance、metric 3D、planner/controller、robot result或个人ownership。WAM、OpenPiVLA、UWM与Harness只能作为待补artifact的接口对照。

**追问树**：semantic、instance、panoptic、promptable mask如何区分？Mask2Former为何统一架构却不能统一metric？SAM quality代表什么、不代表什么？relative depth为何不能直接反投影？metric `max_depth`怎样绑定checkpoint？resize回原图为何不等于camera registration？mask边界为何产生飞点？semantic keypoint比普通point多哪些字段？kPAM怎样把keypoint转成cost/constraint？Where2Act的ActionScore、Actor、Critic分别做什么？affordance为何绑定primitive与state？proposal高分为何还要IK/collision/controller？OPD point target和Where2Act有何本质差别？

**易错点**：把任意mask当category+instance；把SAM quality当robot-success confidence；把relative depth或手乘常数叫米制；把output resize当intrinsics/registration恢复；忽略invalid depth、边界飞点、frame和staleness；把无名point叫semantic keypoint；把actionable文本叫primitive-conditioned affordance；用2D IoU替代3D/episode metric；把公开模型、代码零匹配或Git身份升级为本地集成、效果或个人贡献。

**危险答案**：说“有mask就知道抓哪个”“Depth Anything输出就是米”“resize回原图就对齐相机”“一个point就是keypoint”“SAM/affordance分数高就直接执行”“OPD已经实现SAM+depth+kPAM+Where2Act完整栈”，却不交代task、checkpoint、unit、camera/frame/time、primitive、planner/controller、raw artifact与ownership缺口。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-012 Segmentation / Depth / Keypoint / Affordance Knowledge](../knowledge/vol_06_per012_segmentation_depth_keypoint_affordance.html)：typed composition、方法合同、诊断顺序、项目边界与面试模板。
2. [PER-012 Source Freeze](../sources/vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html)：固定paper/code revision、SHA、license、本地OPD audit与deterministic probes。
3. Cheng et al., [Mask2Former v3](https://arxiv.org/abs/2112.01527v3)；[official repository](https://github.com/facebookresearch/Mask2Former/tree/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a)。
4. Kirillov et al., [Segment Anything v1](https://arxiv.org/abs/2304.02643v1)；[official repository](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
5. Yang et al., [Depth Anything V2 v2](https://arxiv.org/abs/2406.09414v2)；[official repository](https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf)。
6. Gao & Tedrake, [kPAM v2](https://arxiv.org/abs/1903.06684v2)；[official repository](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
7. Mo et al., [Where2Act v2](https://arxiv.org/abs/2101.02692v2)；[official repository](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
8. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
