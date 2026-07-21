# VOL 06 PER-012 Source Freeze：Segmentation、Depth、Keypoint 与 Manipulation Affordance

> 状态：`source_frozen / VLA-PER-012 / primary_official_checked / local_opd_point_only_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结promptable/universal segmentation、relative/metric monocular depth、semantic 2D/3D keypoint与primitive-conditioned manipulation affordance的方法链；不生成knowledge/card，不重讲PER-008的表示选择，不把dense perception输出升级为PER-015的reachable action或robot success。

## 问题（Question）

Semantic、instance、panoptic和promptable segmentation分别输出什么？SAM与Mask2Former的prompt/query、mask candidate、class/mask/dice objective和postprocess边界是什么？relative depth为何不能直接当米制深度，Depth Anything V2的relative/metric代码路径如何区分？semantic keypoint如何从mask/depth进入3D planning？Where2Act的actionability、orientation proposal和critic success score为何必须绑定primitive、state与机器人？本地OPD的“affordance point”到底支持哪些结论？

本页冻结的可审计链为：

```text
RGB + camera/preprocess identity
  -> semantic / instance / panoptic / promptable mask
  -> relative or metric depth + valid/confidence mask
  -> mask-conditioned surface / 2D-to-3D lift
  -> semantic keypoint identity + visibility + frame
  -> primitive-conditioned point/orientation proposal
  -> planner / collision / reachability / controller gate
  -> episode-level evidence
```

## 1. 结论先行

1. **Segmentation首先是task semantics，不是一个通用`mask`字段**：semantic map按类别聚合，instance map分开同类对象，panoptic同时覆盖thing/stuff，promptable mask回答给定point/box/mask prompt下的区域候选；四者的输出、分母和下游用途不同。
2. **SAM的mask没有天然语义与实例持久身份**：固定predictor返回原图尺寸的多个mask、predicted quality和低分辨率logits；multimask选择、prompt坐标变换、threshold和temporal association必须显式冻结。
3. **Mask2Former统一架构不等于统一输出协议**：同一模型可打开semantic/instance/panoptic分支，但postprocess、thing/stuff metadata、top-k、object/overlap threshold与metric仍随任务变化。
4. **Mask query assignment和最终loss要分开**：固定代码用Hungarian matcher建立prediction–GT责任，再以classification、sigmoid mask CE和Dice组成criterion；这与生成式OPD的assistant-token CE不是同一objective。
5. **Relative depth不是米制深度**：Depth Anything V2 relative代码输出非负dense map，却不提供`max_depth`或meter contract；metric路径使用单独checkpoint/code并把sigmoid输出乘`max_depth`。没有checkpoint family、dataset、range与unit，不能直接反投影到机器人坐标。
6. **Depth resize回原图不等于恢复metric geometry**：固定代码先保持长宽比、lower-bound resize到14的倍数，再把预测双线性插回原\(H\times W\)；这是shape alignment，不修复scale、shift、相机内参、边界混合或反射/透明失效。
7. **Semantic keypoint不是无名point**：kPAM把类别级操作目标写成带语义的3D keypoint costs/constraints，并分解为instance segmentation→3D keypoint detection→optimization planning→local geometry execution；缺semantic ID、visibility和frame的坐标不能冒充该合同。
8. **Affordance必须绑定动作条件**：Where2Act的per-point actionability、orientation actor和critic success likelihood面向articulated object及push/pull等primitive；同一点在不同primitive、gripper、state和orientation下可完全不同。
9. **组合链按最弱环节失效**：mask正确但depth scale错会得到错误3D surface；keypoint正确但frame/time错会误导planner；affordance score高但reachability/collision/controller不通过仍不可执行。
10. **本地OPD只支持affordance-labelled point supervision**：选定代码把ShareRobot affordance坐标缩放到0..1000并输出`<point>`；五个文件中没有SAM/mask/keypoint/depth显式实现。不能声称完成segmentation、metric depth、semantic keypoint、dense/action-conditioned affordance或机器人闭环。

## 2. Primary / official / local source ledger

论文SHA对固定版本PDF bytes计算；GitHub文件对固定commit raw bytes计算；本地脚本按原始bytes。repository code license不自动覆盖论文、dataset、checkpoint、submodule或第三方asset。

| 来源 | 类型 / revision / license | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [Mask2Former paper v3](https://arxiv.org/abs/2112.01527v3) | primary；2022-06-15 v3；PDF读取2026-07-20 | `A360185A7682EFB920247C916C448555A5262E3C52E0710192626592EA267D6F` | masked attention；统一semantic/instance/panoptic image segmentation架构 | 任意checkpoint、本地机器人任务或跨协议SOTA仍成立 |
| [Mask2Former README](https://github.com/facebookresearch/Mask2Former/blob/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a/README.md) | official-code；`9b0651c...`；top-level MIT，部分依赖另有license | `E679DDC5C12D9A4984D2DB7DC8A4CDFC779D30192CD69D46945A19D68087BDF3` | 三类segmentation支持、数据集/安装/依赖边界 | checkpoint/依赖license自动相同或本地部署 |
| [Mask2Former model](https://github.com/facebookresearch/Mask2Former/blob/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a/mask2former/maskformer_model.py) | official-code；同commit | `FA52D4F9CCC8055C69A034933809DEFC5CB487B2CD6331727D07CB104148EC23` | semantic/instance/panoptic switches与outputs、Hungarian、weight_dict、resize/postprocess、thing/stuff metadata | 所有任务共用同一threshold/metric或mask足以操作 |
| [Mask2Former criterion](https://github.com/facebookresearch/Mask2Former/blob/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a/mask2former/modeling/criterion.py) | official-code；同commit | `B80C583C1DCFC63F9FBDAEA3D0509A7908D161FC348AEFDBF6746FFFF53A88DA` | matched class supervision、point-sampled sigmoid CE和Dice mask loss | SAM objective、本地OPD CE或robot success |
| [Mask2Former LICENSE](https://github.com/facebookresearch/Mask2Former/blob/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a/LICENSE) | official top-level MIT text | `99566A874D9DECD98DC3CEA026C314AD255D8798D7D51E121FE1413F4D2750BB` | top-level source license | README列出的Swin/Deformable-DETR等依赖授权闭合 |
| [Segment Anything paper v1](https://arxiv.org/abs/2304.02643v1) | primary；2023-04-05 v1；PDF读取2026-07-20 | `C6CA524E47200C3E542587CA76AC1DBC89CC67340F948C819250D16FDBD90CFB` | promptable segmentation task/model/data-engine与zero-shot framing | 语义label、实例跟踪、depth或action success |
| [SAM predictor.py](https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/segment_anything/predictor.py) | official-code；`dca509f...`；Apache-2.0 repo | `AB66C29AC0B5B204D23997EF49D8A2476F71B596CE97E35EFBF116CFC2118FCE` | point/box/mask_input、multimask、原图mask、quality与`256×256` low-res logits | quality校准成robot success或mask带语义/时间身份 |
| [Depth Anything V2 paper v2](https://arxiv.org/abs/2406.09414v2) | primary；2024-10-20 v2；PDF读取2026-07-20 | `B156A023AA9A5E33BDA60489962AF809A67E748797D4357C790D063739FED2D7` | synthetic labeled images、larger teacher、pseudo-labeled real images、relative模型与metric fine-tuning framing | 任意场景米制精度、透明/反射物可靠性或机器人3D安全 |
| [Depth Anything V2 README](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/README.md) | official-code/docs；`a561b84...`；code与model license分层 | `987D1AB991C1B149276A0426BEC7D8F3472D85C29EC976D96EA657AA960FAD50` | relative model family、518默认input、metric models入口、checkpoint license差异 | 所有checkpoint Apache-2.0或relative output可直接当meter |
| [Depth Anything V2 relative DPT](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/depth_anything_v2/dpt.py) | official-code；同commit | `7CC9A29B41D31E1628E5C8B8705E25AE95BC6490F779DBB695297CE2341566F5` | DINOv2 intermediate layers→DPT head→ReLU depth、aspect-ratio resize/14 multiple、原图插值 | meter unit、metric range或calibrated uncertainty |
| [Depth Anything V2 metric DPT](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/metric_depth/depth_anything_v2/dpt.py) | official-code；同commit | `120698FD0AD9A4D169B4B9EF26035AD0CB11EED4089AF53E07E38F5717024B1D` | sigmoid head、`max_depth`与separate metric path | checkpoint dataset/range可省略或跨域无偏 |
| [Depth Anything V2 transform](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/depth_anything_v2/util/transform.py) | official-code；同commit | `A97DF1DBB687457A40C387FDC3482EDEE7DDC5C142C7D2735CA6235A8AE2885F` | resize/normalize/preparation实现桥接 | camera intrinsics或metric geometry自动同步 |
| [Depth Anything V2 LICENSE](https://github.com/DepthAnything/Depth-Anything-V2/blob/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf/LICENSE) | official code Apache-2.0 text；checkpoint license见README | `C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4` | source code license | Base/Large/Giant model按README自动可商用 |
| [kPAM paper v2](https://arxiv.org/abs/1903.06684v2) | primary；2019-10-29 v2；PDF读取2026-07-20 | `37CC5BA0FD585E627E8573FB13C12D909F204B5D347EE4579A7947D8AA2DC7A8` | semantic 3D keypoints、geometric costs/constraints与四段manipulation pipeline | 任意2D point已有semantic identity、3D frame或执行闭环 |
| [kPAM README](https://github.com/weigao95/kPAM/blob/7214936b619527aee3b02d5306ada15decb95140/README.md) | official-code；`7214936...`；MIT top-level | `665E70DCDAB873262458CC748F48A9D4550FA6B4EBFBAC7DD2884464C5636BD3` | category manipulation目标定义在semantic keypoints上；公开模块/依赖边界 | private spartan、完整detector或本地执行已实现 |
| [Where2Act paper v2](https://arxiv.org/abs/2101.02692v2) | primary；ICCV 2021；PDF读取2026-07-20 | `7649D0C8404CA5DD696D94A001D1D3501D789CA58B3002032BF67791D689631F` | image+depth下point-wise action proposal与simulation interaction learning | 任意机器人/primitive/domain的通用成功概率 |
| [Where2Act model_3d.py](https://github.com/daerduoCarey/where2act/blob/1daf1a24f7a372599b211108fa851f7ec3581330/code/models/model_3d.py) | official-code；`1daf1a2...`；README声称MIT但commit无LICENSE | `968165B68FA9933553497F884F37F484A4F78D70BD647B5C4FF890F0427DE5C2` | PointNet++ feature、per-point ActionScore、6D orientation actor与critic score | score跨robot/primitive校准、license packaging或safe execution |
| [PER-002 3D Lift / Frame Source Freeze](vol_06_per002_3d_lift_frame_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | pixel→camera→target、intrinsics/depth/TF/time/uncertainty合同 | 本页具体depth model或project已有3D evidence |
| [PER-008 Representation Choice Source Freeze](vol_06_per008_representation_choice_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | mask/keypoint/affordance表示语义与SAM/kPAM/Where2Act基础证据 | PER-012方法链和训练/组合诊断 |
| `muxi/opd_project/scripts/build_prompt_pool.py` | local-evidence；`muxi@756e27e...` | `293C776BA03E28DAC0029F985EEFFDC20036D24A289F3D74B1F761D1C7629315` | ShareRobot `affordance.{x,y}`→0..1000单point与`gt_points` | mask/depth/keypoint/dense affordance/controller |
| `muxi/point/point_data_only.py` | local-evidence；同HEAD | `F650CB1F1B4A37566E11FA30C47A855DD59B74052588799839DF28F71EEC5787` | trajectory/affordance record→`<point>`与actionable-location prompt | dynamics、semantic keypoint、orientation或执行成功 |
| `muxi/point/build_expert_mixes_seed0.py` | local-evidence；同HEAD | `60DFDF46FDAC8EB9DBBE38A13298D6D71819EB7AD13F6B0D00A86B87032EABD0` | point/box extraction、route mix和path split | mask/keypoint/depth head或3D pipeline |
| `muxi/point/eval_qwen_vl_raw_holdout.py` | local-evidence；同HEAD | `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B` | point/box/text parser与metric | mask IoU、depth error、keypoint identity或affordance execution |
| `muxi/point/build_clean_grounding_pool.py` | local-evidence；同HEAD | `A7A5906E11EA687C6FD0DEC40F3D30922A91B538EB98C740230227F9FF943087` | box clip/filter、coordinate/tag SFT rows | segmentation/depth/keypoint/affordance method |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | repository local inventory | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | local point/box/text training/eval、leakage和claim边界 | 本页新增dense method、robot result或candidate ownership |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-012只新增 |
| --- | --- | --- |
| PER-001 | point/box/text schema与坐标协议 | dense mask/depth/keypoint/affordance方法产生链 |
| PER-002 | pinhole lift、depth validity、frame/TF/time、3D uncertainty | relative/metric depth model输出如何进入该合同 |
| PER-006 | resize/crop/letterbox、patch token、camera lineage | SAM/Mask2Former/Depth Anything的method-specific preprocess/postprocess |
| PER-007 | open-vocabulary box/phrase inference | mask task semantics与prompt/query pipeline |
| PER-008 | point/box/mask/keypoint/affordance表示选择与转换损失 | Mask2Former/SAM/Depth Anything/kPAM/Where2Act具体方法链 |
| PER-009 | detector matching、negative、loss/reduction | 只说明mask criterion接口，不重讲通用Hungarian/focal细节 |
| PER-010 | IoU/PCK/Recall/parser与protocol comparability | 方法输出需哪些metric字段；不重建完整评估百科 |
| PER-011 | pseudo-label、teacher noise、calibration与leakage | 只记录Depth Anything pseudo-label训练来源，不重讲teacher可靠性 |
| PER-013/014 | point cloud/voxel/occupancy与3D grounding | 本页只把depth/keypoint/affordance送到3D接口 |
| PER-015 | reachability、collision、uncertainty与controller gate | 本页止于perception/action proposal，不宣称可执行 |

## 4. Typed Dense Perception Record

所有方法输出先落到统一但不抹平语义的record：

```json
{
  "sample_id": "...",
  "image_id": "...",
  "camera_id": "...",
  "timestamp": "...",
  "model_revision": "checkpoint-sha256:...",
  "preprocess_revision": "sha256:...",
  "task": "semantic | instance | panoptic | promptable | relative_depth | metric_depth | semantic_keypoint | affordance",
  "prompt_or_primitive": null,
  "payload": "mask | depth | keypoints | action proposals",
  "coordinate_space": "original_pixel | resized_pixel | camera_3d | target_3d",
  "unit": "class_id | instance_id | relative | meter | normalized",
  "score_semantics": "class | mask_quality | depth_uncertainty | visibility | success_likelihood",
  "validity_mask": null,
  "frame_transform_revision": null,
  "age_ms": 0
}
```

相同`HxW`数组可能分别表示class ID、instance ID、binary mask、relative depth或meter depth；相同point可能是无名位置、semantic keypoint或primitive-conditioned contact proposal。`dtype/shape`相同不代表合同相同。

## 5. Segmentation Task Taxonomy

| Task | 单元 | 输出 | 同类对象 | Stuff | 典型下游 | 主要风险 |
| --- | --- | --- | --- | --- | --- | --- |
| semantic | pixel→class | `C×H×W` score或`H×W` class map | 合并 | 支持 | 区域类别/scene layout | instance混淆 |
| instance | object instance | masks+class+score | 分开 | 通常非主目标 | object crop、tracking seed | top-k/NMS/duplicate |
| panoptic | non-overlap segments | segment ID+`category_id/isthing` | thing分开 | 全覆盖 | scene decomposition | merge/overlap rules |
| promptable | prompt-conditioned candidate | binary masks+quality+logits | 取决于prompt | 可返回区域 | interactive/grounded contour | prompt歧义与语义缺失 |

语义map不能区分两个同类mug；instance mask不能自动保证完整stuff覆盖；panoptic输出需要thing/stuff metadata和non-overlap merge；SAM prompt mask没有category label或跨帧identity。面试中必须先命名task，再谈“分割准确率”。

## 6. Mask2Former：Query Mask Classification

固定`maskformer_model.py`把backbone feature送入segmentation head，输出`pred_logits`与`pred_masks`；criterion先用Hungarian matcher建立query–GT assignment，weight dictionary包含`loss_ce/loss_mask/loss_dice`。可用的抽象目标为：

\[
\mathcal L_{\mathrm{seg}}
=\lambda_{\mathrm{cls}}\mathcal L_{\mathrm{cls}}
+\lambda_{\mathrm{mask}}\mathcal L_{\mathrm{sigmoid}}
+\lambda_{\mathrm{dice}}\mathcal L_{\mathrm{dice}}.
\]

变量解释：三项分别监督matched query的class、point-sampled binary mask与overlap；λ由runtime config/weight dictionary决定。实现映射：固定criterion明确调用sigmoid CE与Dice，assignment与loss仍是两阶段；不能把这条objective移植成OPD token CE的描述。

固定semantic inference把query class probability与mask probability组合：

\[
P_{c,h,w}=\sum_{q=1}^{Q}
\operatorname{softmax}(l_q)_c\,
\sigma\!\left(m_q(h,w)\right).
\]

变量解释：\(l_q\)是query class logits，\(m_q\)是mask logits，\(Q\)是query数。直觉上，每个query对某类别和某区域共同投票。实现映射：instance/panoptic分支还会使用top-k、object threshold、overlap threshold与thing/stuff metadata，因此不能只保存最终PNG而丢失task/postprocess identity。

## 7. SAM：Promptable Mask Candidate，不是Semantic Oracle

SAM predictor冻结的输入/输出为：

```text
original image -> set_image / image embedding
point coordinates + labels OR box OR mask_input
  -> prompt encoder + mask decoder
  -> C original-resolution masks
  -> C predicted quality scores
  -> C x 256 x 256 low-resolution logits
```

当`multimask_output=true`时，同一ambiguous prompt可返回多个候选。部署必须冻结：

1. prompt坐标在original还是resized image；
2. positive/negative point label语义；
3. box corner convention与clip；
4. multimask选择规则，是max predicted quality、task scorer还是human selection；
5. mask threshold、connected component与hole policy；
6. instance/category/language binding；
7. temporal ID、observation age与重分割策略。

`predicted quality`是模型输出的mask-quality proxy，不是PER-011意义下已经对robot task success校准的confidence；若要用作执行gate，需要独立validation与downstream risk–coverage。

## 8. Depth：Relative、Metric与Sensor Depth不能互换

| Depth类型 | 典型来源 | 单位/ambiguity | 可否直接反投影 | 必需metadata |
| --- | --- | --- | --- | --- |
| relative monocular | Depth Anything relative branch | 顺序/相对结构；无meter contract | 否 | model/checkpoint、alignment policy、range |
| metric monocular | metric-finetuned checkpoint | 目标dataset/range定义的metric值 | 有条件 | unit、max depth、dataset、calibration/validity |
| active/stereo sensor | RGB-D/stereo device | 设备unit、invalid code与noise model | 有条件 | intrinsics、scale、timestamp、validity |
| aligned relative | 用reference拟合scale/shift | 依赖alignment samples | 仅在fit域内 | fit split、scale/shift、residual、failure mask |

若用scale/shift把relative prediction \(\hat d_r\)对齐为metric candidate：

\[
\hat d_m(u,v)=s\,\hat d_r(u,v)+t,
\]

变量解释：\(s,t\)必须由合法reference估计，且要保存fit split和residual。直觉上，正确的near/far ordering不等于绝对距离正确。该式是alignment contract，不是Depth Anything代码自动执行的步骤；没有reference时不得凭视觉效果猜meter depth。

## 9. Depth Anything V2：Relative与Metric是两条代码/Checkpoint路径

### 9.1 Relative path

固定relative代码：DINOv2 intermediate features→DPT fusion head→ReLU non-negative depth。`infer_image`默认input size 518；preprocess保持aspect ratio、lower-bound resize、保证14的倍数、ImageNet normalize，最后把dense prediction双线性插值回原图\(H\times W\)。

这支持“原图shape的relative depth map”，不支持“输出单位是米”。README明确把四个主模型称为relative depth models。

### 9.2 Metric path

固定metric代码使用separate path：head末端Sigmoid，forward乘`max_depth`，默认20.0；但真正语义仍绑定metric checkpoint、训练dataset和配置。只把relative checkpoint放入metric code或手工乘20不会获得可信metric depth。

### 9.3 License与artifact identity

README声明Small model为Apache-2.0，Base/Large/Giant models为CC-BY-NC-4.0；top-level source LICENSE是Apache-2.0。报告必须分别记录source revision、model checkpoint/hash与model license，不能用code LICENSE覆盖checkpoint。

## 10. Depth→3D：Dense Map只有进入Camera Contract才成为Geometry

对original pixel \((u,v)\)、metric depth \(d\)和intrinsics \(K\)，PER-002冻结的camera-frame lift为：

\[
X_c=d\,K^{-1}
\begin{bmatrix}u\\v\\1\end{bmatrix}.
\]

变量解释：\(X_c\)是camera-frame 3D point；\(d\)必须是与original pixel、同一timestamp和intrinsics匹配的metric depth。实现映射：Depth Anything把prediction resize回\(H\times W\)只解决array alignment；仍需checkpoint unit、camera identity、invalid/confidence mask、depth-to-RGB registration与后续TF。

对mask \(M\)，object surface可写为：

\[
\mathcal P_M=\left\{d(u,v)K^{-1}[u,v,1]^\top\mid M(u,v)=1,\ d(u,v)\ \text{valid}\right\}.
\]

变量解释：每个mask pixel只在depth valid时进入surface。直觉上，mask边界混入background depth会产生飞点；透明、反射、遮挡和双线性resize会扩大错误。需要erode/boundary audit、robust statistic、uncertainty和outlier gate，不能只看彩色depth visualization。

## 11. kPAM：Semantic 3D Keypoint到Planning Constraint

kPAM的关键不是检测若干坐标，而是把类别级task target定义在semantic 3D keypoints上。其公开factorization为：

```text
instance segmentation
  -> semantic 3D keypoint detection
  -> optimization-based robot action planning
  -> local dense-geometry action execution
```

给semantic keypoints \(k_j\in\mathbb R^3\)和candidate transform \(T\)，规划可抽象为：

\[
T^*=\arg\min_T\sum_j w_j c_j(Tk_j)
\quad\text{s.t.}\quad g_r(Tk_{1:J})\le 0.
\]

变量解释：\(c_j\)是目标几何cost，\(g_r\)是关系/可行性constraint，\(w_j\)可结合visibility/uncertainty。直觉上，mug handle与rim即使坐标接近，semantic ID不同会产生不同task cost。该式是kPAM几何合同抽象；具体detector、planner和private submodule需另按revision审计。

最小keypoint record必须包含`semantic_id, instance_id, category, coordinates, coordinate_frame, visibility, covariance, timestamp`。只有`[[x,y]]`不能支持category-level manipulation planning。

## 12. Where2Act：Point-wise Action Proposal需要Primitive与Orientation

固定Where2Act 3D model以PointNet++ feature为基础，包含：

- ActionScore：每点actionability；
- Actor：给定point feature提出6D orientation/action proposal；
- Critic：评估point+orientation interaction的success likelihood；
- simulation interaction/data sampling：面向articulated object的push/pull等primitive。

安全的score语义为：

\[
A(p,R\mid \pi,s,e)=
\Pr(\text{interaction succeeds}\mid p,R,\pi,s,e),
\]

其中\(p\)是contact point，\(R\)是orientation，\(\pi\)是primitive，\(s\)是object/environment state，\(e\)是训练/eval protocol。直觉上，同一点对push和pull、不同gripper或door state的actionability不同。固定model score不自动跨robot、primitive或domain校准。

Affordance proposal仍不是controller action：至少还需3D frame、end-effector/tool transform、reachability、IK、collision、force/trajectory、controller frequency与online failure recovery；这些属于PER-015/robot evidence gate。

## 13. 四类方法如何组合

推荐的typed composition为：

```text
language/box/point prompt
  -> SAM candidate masks OR Mask2Former task-specific segments
  -> choose instance/category with explicit score semantics
  -> Depth Anything metric branch or registered sensor depth
  -> valid mask + mask-conditioned 3D surface
  -> semantic keypoint detector + covariance/frame
  -> primitive-conditioned affordance point/orientation proposals
  -> planner/IK/collision/controller gate
  -> episode trace and success predicate
```

每层必须保存upstream IDs，才能定位：

| Failure | 表面症状 | 首查 |
| --- | --- | --- |
| wrong segment | 抓错同类对象 | task semantics、prompt/instance binding |
| boundary leak | 3D surface飞点 | mask boundary、depth discontinuity、resize |
| scale error | 方向对但距离错 | relative/metric checkpoint、unit、range |
| keypoint swap | 把rim当handle | semantic ID、visibility、category mapping |
| primitive mismatch | push score用于pull | primitive/state/model identity |
| frame/time mismatch | 视觉点正确、执行偏移 | camera/TF/timestamp/age |
| controller rejection | proposal高分却不可达 | IK/collision/tool/controller gate |

## 14. Objective与Metric不能跨Task偷换

| 输出 | 训练/评分单元 | 常见metric | 不等价于 |
| --- | --- | --- | --- |
| semantic mask | class per pixel/query-mask mixture | mIoU/pixel accuracy | instance AP、PQ、robot contact |
| instance mask | ranked instance masks | mask AP/AR | semantic mIoU或persistent tracking |
| panoptic | non-overlap segments | PQ/SQ/RQ | arbitrary overlapping proposals |
| promptable mask | prompt-conditioned candidate | mask IoU/quality by prompt | semantic correctness或task success |
| relative depth | aligned/rank structure | aligned AbsRel/δ1等，绑定alignment | meter error |
| metric depth | valid metric pixels | AbsRel/RMSE/δ threshold | 3D/task success |
| semantic keypoint | named visible anchors | PCK/3D distance，绑定normalizer/frame | naked point hit |
| affordance | point+orientation+primitive interaction | success/recall/ranking，绑定sim/robot | objectness、mask quality或reachability |

任何比较都要继承PER-010的protocol identity：dataset/split、checkpoint、preprocess、output task、postprocess、matching、valid denominator、threshold、aggregation和sample unit。

## 15. 本地OPD：Affordance-named Point，不是Dense Perception Stack

本地真实链为：

```text
ShareRobot affordance {x, y} or trajectory points
  -> scale image coordinates to 0..1000
  -> prompt says actionable affordance location
  -> target remains <point>[[x,y], ...]</point>
  -> point/box/text parser and static metric
```

直接证据：

1. `build_prompt_pool.py`从`affordance.x/y`生成一个`gt_points`，标`task_type=affordance_pointing`；无primitive、orientation、gripper、state或success head。
2. `point_data_only.py`读取trajectory/affordance record，最终仍调用`point_answer(scaled)`；prompt中的“actionable”不会把representation变成dense affordance field。
3. `build_expert_mixes_seed0.py`与`eval_qwen_vl_raw_holdout.py`只识别point/box/text路径；没有mask/depth/keypoint metric。
4. 对五个固定文件的静态case-insensitive search，`keypoint/segment_anything/sam_model/mask_rle/polygon/<mask>/depth`均为0匹配。该结论只覆盖选定路径，不排除远端、历史或未归档代码。

安全表述：

> OPD包含affordance-labelled point supervision和point/box/text静态评估。我会把数据语义与模型输出合同分开：当前证据不支持SAM/Mask2Former pipeline、relative/metric depth head、semantic 3D keypoint、Where2Act式primitive-conditioned affordance或robot execution。

## 16. 项目Hook与Truth Boundary

| 项目 | 可用Hook | 当前证据 | 禁止升级 |
| --- | --- | --- | --- |
| OPD | affordance-labelled point、box/point parser、static holdout | local-direct selected scripts/inventory | dense affordance、mask/depth/keypoint、robot success、ownership |
| WAM | future/action/value与RoboCasa诊断可提出“未来帧是否保留contact geometry”问题 | inventory主要是upstream与partial diagnostic | 已训练segmentation/depth auxiliary head或抓取提升 |
| Robot Harness | 可消费typed perception result并做tool/scope/cancel gate | tool/runtime proxy evidence | 真实perception model、3D controller或physical success |
| OpenPiVLA | image→action policy接口可讨论是否显式使用dense intermediate | formal checkpoint/image lineage仍有缺口 | 已集成SAM/depth/keypoint或其因果收益 |
| UWM | simulator/world-model可提供future observation diagnostic | raw checkpoint/episode evidence不足 | learned affordance map或real robot transfer |

没有local model checkpoint、inference script、mask/depth/keypoint output、3D frame manifest、planner/controller trace与episode result时，公共方法只能作为设计参照，不是个人项目完成证据。

## 17. Deterministic Probes

| Probe | 固定输入 | 预期结论 | 防止的偷换 |
| --- | --- | --- | --- |
| semantic vs instance | 两个同类mug | semantic可同class；instance必须不同ID | semantic map=instance tracking |
| SAM multimask | 同一ambiguous click返回3 masks | 选择policy改变结果 | SAM只有唯一真mask |
| relative scale | prediction `[1,2]`，physical `[0.5,1]m` | ordering正确但meter错误 | relative=metric |
| metric range | sigmoid=.8，`max_depth=20/80` | 输出16m/64m | code path名足以定义unit |
| resize boundary | thin object mask跨depth edge | bilinear/边界pixel产生混合depth | resize回原图=几何正确 |
| semantic identity | 同坐标分别标handle/rim | planning cost不同 | naked point=semantic keypoint |
| affordance condition | 同一点push/+x与pull/-x | actionability不同 | point坐标=affordance |
| weakest-link | perfect mask + depth scale×2 | 3D surface距离×2 | 某一模块高分=链路正确 |
| local schema | OPD row只有`<point>`与prompt | 不支持mask/depth/keypoint/primitive | affordance命名=Where2Act实现 |

## 18. Fail-closed Pseudocode

```python
def build_manipulation_proposal(image, camera, prompt, primitive, artifacts):
    # 1. Require immutable model/preprocess/checkpoint identities.
    assert artifacts.segmenter.sha256 and artifacts.depth_model.sha256
    assert camera.intrinsics_sha256 and camera.timestamp is not None

    # 2. Produce task-typed segments; do not collapse semantic/instance/promptable outputs.
    segments = artifacts.segmenter.predict(image, prompt=prompt)
    target = select_segment(segments, task=artifacts.segmentation_task)
    if target is None or target.score < artifacts.mask_threshold:
        return reject("no_valid_segment")

    # 3. Require metric depth and a validity map before any 3D lift.
    depth = artifacts.depth_model.predict(image)
    assert depth.unit == "meter" and depth.checkpoint_family == "metric"
    valid = target.mask & depth.validity_mask
    if valid.sum() < artifacts.min_surface_pixels:
        return reject("insufficient_metric_surface")

    # 4. Lift only registered original-image pixels into the camera/target frame.
    surface = backproject(valid, depth.values, camera.intrinsics)
    surface = transform_at_timestamp(surface, camera.tf_revision, camera.timestamp)

    # 5. Preserve semantic keypoint identity and uncertainty.
    keypoints = artifacts.keypoint_model.predict(target, surface)
    if any((not k.visible) or k.covariance > artifacts.max_cov for k in keypoints):
        return reject("uncertain_semantic_keypoint")

    # 6. Affordance is conditioned on primitive, state and orientation.
    proposals = artifacts.affordance_model.propose(surface, primitive=primitive)

    # 7. Perception score never bypasses reachability, collision and controller gates.
    feasible = planner_filter(proposals, keypoints, camera.robot_state)
    return feasible if feasible else reject("no_reachable_collision_free_action")
```

伪代码是目标合同，不是本地已实现事实。真实系统还要冻结depth scale/range、mask candidate policy、frame/time covariance、tool geometry、planner/IK revision、controller limits与episode logging。

## 19. 面试中的项目Truth Boundary

推荐口述：

> 我会先区分segmentation task：semantic合并同类、instance分对象、panoptic还要thing/stuff，SAM则是prompt-conditioned mask candidates。Depth也先分relative与metric；Depth Anything V2固定代码中relative是ReLU dense map，metric是单独Sigmoid×max-depth路径和checkpoint，resize回原图不代表恢复米制几何。进入操作时，kPAM式keypoint必须有semantic ID、3D frame和visibility；Where2Act式affordance还绑定point、orientation、primitive和state。最后仍要过reachability、collision与controller。对本地OPD，我只能说有affordance-labelled point监督：脚本把x/y缩到0..1000并输出point，没有mask/depth/keypoint/dense affordance证据，因此不能把数据命名升级成完整操作感知栈。

| 证据层 | 可以说 | 不能说 |
| --- | --- | --- |
| public primary/code | 解释Mask2Former、SAM、Depth Anything V2、kPAM、Where2Act的固定方法合同 | 它们已在用户项目中集成或有效 |
| local-direct | OPD选定脚本产生affordance-named point并只评point/box/text | 存在mask/depth/keypoint head |
| local-inference | 可提出typed composition与fail-closed gate | 组合链已经运行 |
| unverified | 远端/历史可能存在其他artifact | 用可能性恢复项目claim |
| ownership | Git/文件存在只给候选线索 | 未确认逐文件贡献前说“我设计/实现” |

## 20. Source Gate 与下一Slice

本页达到source-freeze条件：

- Mask2Former、SAM、Depth Anything V2、kPAM、Where2Act的paper/code revision、SHA与license边界已冻结；
- segmentation四类task、relative/metric depth、semantic keypoint和primitive-conditioned affordance不再混称；
- mask→depth→3D→keypoint→affordance→planner/controller的typed composition与最弱环节failure已明确；
- 本地OPD五文件静态审计与affordance-labelled point真实性边界已重复核验；
- deterministic probes和fail-closed pseudocode覆盖task、scale、identity、frame与action gate。

仍为`WARN`，因为本地没有mask/depth/keypoint/affordance model checkpoint、raw dense outputs、3D frame/time manifest、matched ablation、planner/controller trace、robot episode或candidate ownership confirmation；Mask2Former依赖与Depth Anything checkpoint license也必须逐artifact审查。

`VLA-PER-001..012` source/knowledge/card已在独立bounded slices同步，263张题卡全部`unseen`。下一bounded slice只冻结`VLA-PER-013` point-cloud/voxel/BEV/occupancy representation source；不生成knowledge/card，不创建`coaching_state.md`，不改变mastery。

## 21. References

1. Cheng et al., [Mask2Former v3](https://arxiv.org/abs/2112.01527v3)；[official repository@9b0651c](https://github.com/facebookresearch/Mask2Former/tree/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a)。
2. Kirillov et al., [Segment Anything v1](https://arxiv.org/abs/2304.02643v1)；[official repository@dca509f](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
3. Yang et al., [Depth Anything V2 v2](https://arxiv.org/abs/2406.09414v2)；[official repository@a561b84](https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf)。
4. Gao & Tedrake, [kPAM v2](https://arxiv.org/abs/1903.06684v2)；[official repository@7214936](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
5. Mo et al., [Where2Act v2](https://arxiv.org/abs/2101.02692v2)；[official repository@1daf1a2](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
6. 本仓库 [PER-002 3D Lift / Frame](vol_06_per002_3d_lift_frame_source_freeze.html)、[PER-008 Representation Choice](vol_06_per008_representation_choice_source_freeze.html)、[PER-010 Metric / Parser / Protocol](vol_06_per010_grounding_metric_parser_protocol_source_freeze.html) 与 [PER-011 Teacher Noise / Calibration / Leakage](vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html)。
7. 本地`muxi@756e27e16adcfb3ccbfe98c2920dda42095b127f`的五个固定脚本与 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
