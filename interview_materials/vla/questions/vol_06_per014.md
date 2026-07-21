# VOL 06 Perception / Grounding / Navigation：PER-014 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-014`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-014 3D Grounding / Spatial Relation / Open-vocabulary Knowledge](../knowledge/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.html)；来源边界见 [PER-014 Source Freeze](../sources/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html)。

## 3D Grounding、Spatial Relation 与 Open-vocabulary 3D Scene

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-014</b> · 3D grounding有哪些输出？candidate、spatial relation、open-vocabulary score和metric该怎样冻结？</summary>

**面试意图**：判断你能否先区分3D box、candidate ID、point semantics、instance mask、continuous field与semantic map六类输出，再说明proposal hard upper bound、relation frame/arity、prompt/negative/score/metric identity、first-divergence diagnosis与项目真实性边界。

**30 秒回答**：先定输出：3D框、候选ID、点语义、实例mask、连续场或语义地图；再冻结候选来源/目标覆盖、坐标时间、关系元数与参考系、prompt/negative/归一化、阈值和指标。目标不在候选中时top-1上界为0，点语义不等于实例。语义目标还要过可达性、IK、碰撞与控制器，不能把cosine或IoU叫机器人成功。

**机制展开（约 2 分钟）**：ScanRefer先做3D proposal，再做语言排序与框IoU；ReferIt3D只在已分割对象中做top-1。OpenScene给点语言特征但无实例；OpenMask3D先有class-agnostic mask，再经视图、SAM crop和CLIP查询。LERF是逐场景多尺度连续场；ConceptFusion依赖RGB-D/内外参/pose融合语义地图。left/right须绑observer/world/object frame，between是三元关系；dot、cosine与正负relative probability不可混。指标按proposal recall、Acc@IoU、top-1、mIoU、AP、场/地图定位分层，输出再交PER-015。

**诊断 / 证据**：按first-divergence检查scene revision/frame/axis/unit/pose/depth/time→candidate source/count/target-present与proposal oracle→point/mask/instance的merge、split与view coverage→relation target/anchors/arity/reference frame/tolerance→encoder/checkpoint/prompt/tokenizer/negative/L2 normalization→dot/cosine/temperature/threshold/top-k/unknown→与输出匹配的metric与denominator→reachability/IK/collision/controller rejection。确定性probe至少保留unit-cube x错0.5得到IoU=1/3、GT 7不在`[2,4,5]`中top-1上界0、yaw 0/180°使left翻转、同类双chair的semantic/instance差异、多视图`[1,0]+[-1,0]`零范数、positive .55对negative .60得到relative probability 0.4875。

**项目挂钩**：本地OPD的`spatial_rel_expert`来自Visual Genome 2D relationship，prompt明确写“in the image”；point路径只有x/y与0–1000 `<point>/<box>`或boolean，不含z、meter、3D frame或instance graph。Robot Harness只有0/127/255三态2D occupancy、54,856点且字段为`x y z intensity timestamp ring`的non-semantic PCD，以及暴露path/URL的bridge；没有semantic label、instance ID、language embedding/query service。OpenPiVLA/WAM/UWM只有image/language/action或video/world-model证据。因此只能把这些项目讲成2D supervision、geometry/interface或未来扩展入口，不能说候选人已实现ScanRefer/OpenScene/OpenMask3D/LERF/ConceptFusion、获得3D grounding uplift或robot success；Git身份也不能替代ownership确认。

**追问树**：ScanRefer和ReferIt3D的candidate assumption有什么根本差异？proposal recall为何是硬上界？`ref_acc`为何不等于`Acc@IoU 0.5`？point mIoU为何不等于instance AP？两个同类chair怎样暴露identity缺口？OpenMask3D的mask proposal、view selection、SAM crop和CLIP各负责什么？多视图mean为何可能降低score？LERF为何是per-scene且需要scale？ConceptFusion为何依赖pose/depth且query成功不能证明SLAM正确？left/right绑定哪个frame？between为何是三元关系？closest为何依赖candidate set？dot、cosine、relative probability有何差异？negative prompt与temperature为何属于协议？scene-level min-max为何不是跨scene calibration？你会怎样拆分geometry、candidate、relation、language与action failure？本地五项目当前最多支持哪一级claim？

**易错点**：把六类输出统称“3D grounding”；把ReferIt3D说成raw-scene detector；忽略target-present/proposal oracle；把point semantic当instance；把image-left当map-left；把between写成二元；把cosine 0.8叫80%概率；把多视图平均当必然增益；把field heatmap当box/object ID；用semantic mIoU替代instance AP或robot success；用query heatmap反证SLAM；把OPD 2D relation、Harness PCD/occupancy asset、公开代码或Git身份升级为个人3D系统。

**危险答案**：说“把CLIP特征投到点云就完成3D grounding”“语言能找回proposal漏掉的目标”“left就是x小”“point mIoU高就能区分实例”“多视图平均一定更稳”“cosine就是confidence”“semantic map可直接发动作”“Harness已经有语言可查询3D地图”，却不交代output atom、candidate source/target-present、frame/pose/time、relation arity/anchors、prompt/negative/normalization、threshold/metric、PER-015 gate、raw artifact与ownership缺口。

**来源**：[1][2][3][4][5][6][7][8][9]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary Knowledge](../knowledge/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary.html)：六类输出、typed manifest、candidate上界、relation、score、metric、diagnostic、面试回答与项目边界。
2. [PER-014 Source Freeze](../sources/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html)：六篇完整primary PDF、六个official repositories、36个文件SHA、九个deterministic probes与五项目audit。
3. Chen et al., [ScanRefer v3](https://arxiv.org/abs/1912.08830v3)；[official repository](https://github.com/daveredrum/ScanRefer/tree/9d7483053e8d29acfd4db4eb1bc28f1564f5dddb)。
4. Achlioptas et al., [ReferIt3D, ECCV 2020](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460409.pdf)；[official repository](https://github.com/referit3d/referit3d/tree/725a5d31b8ff3647b6fb5342304093e9568d1341)。
5. Peng et al., [OpenScene v2](https://arxiv.org/abs/2211.15654v2)；[official repository](https://github.com/pengsongyou/openscene/tree/0f369bc73d0724ae24b5e46bbada193f8ee9d193)。
6. Takmaz et al., [OpenMask3D v2](https://arxiv.org/abs/2306.13631v2)；[official repository](https://github.com/OpenMask3D/openmask3d/tree/3bc3fc52693b25668d0e91d55a2ea714544a4749)。
7. Kerr et al., [LERF v1](https://arxiv.org/abs/2303.09553v1)；[official repository](https://github.com/kerrj/lerf/tree/db08d578038d884542688511bd9ad7b489a65673)。
8. Jatavallabhula et al., [ConceptFusion v3](https://arxiv.org/abs/2302.07241v3)；[official repository](https://github.com/concept-fusion/concept-fusion/tree/4457c1f718a5612c2efc57b93a2dc152fed8a03d)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
