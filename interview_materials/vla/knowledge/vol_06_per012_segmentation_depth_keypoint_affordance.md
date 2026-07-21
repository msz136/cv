# VOL 06 Perception / Grounding / Navigation：Segmentation、Depth、Keypoint 与 Manipulation Affordance（PER-012）

> 状态：`drafted / VLA-PER-012 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-002` 2D→3D lift、`VLA-PER-008` representation choice、`VLA-PER-010` metric/parser；后续：`VLA-PER-013/014` 3D representation/grounding、`VLA-PER-015` perception→action gate。  
> 来源入口：[PER-012 Segmentation / Depth / Keypoint / Affordance Source Freeze](../sources/vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html)；对应自测：[PER-012 Atomic Card](../questions/vol_06_per012.html)。本页只做冻结证据的教学转译；题卡已生成并保持`unseen`，真实口述状态仍未开始。

## 问题（Question）

面试官问“如何把图像中的物体变成机器人可用的操作目标”时，不能只列SAM、Depth Anything或Where2Act模型名。需要讲清：segmentation task到底是semantic、instance、panoptic还是promptable；depth是relative还是metric；mask/depth怎样对齐原图、相机和时间；keypoint为何必须有semantic identity和3D frame；affordance为何绑定primitive、orientation和state；以及这些perception proposal为什么仍需planner、IK、collision和controller gate。

本节点建立的主链是：

```text
RGB + camera/preprocess identity
  -> task-typed segmentation
  -> relative or metric depth + validity
  -> registered mask-conditioned 3D surface
  -> semantic keypoint + visibility/covariance/frame
  -> primitive-conditioned point/orientation proposal
  -> reachability/IK/collision/controller gate
  -> episode trace and success predicate
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-012负责 |
| --- | --- | --- |
| PER-001 | point/box/text schema与coordinate protocol | dense mask/depth/keypoint/affordance方法产生链 |
| PER-002 | pinhole lift、intrinsics、depth validity、TF/time | depth model输出怎样满足metric lift前置条件 |
| PER-006 | generic resize/crop/letterbox与camera lineage | SAM/Mask2Former/Depth Anything specific preprocess/postprocess |
| PER-008 | 为什么选择point/box/mask/keypoint/affordance | 五种代表方法的architecture/output/composition |
| PER-009 | Hungarian、negative、loss/reduction | 只解释Mask2Former mask criterion，不重讲通用loss课 |
| PER-010 | metric/denominator/protocol comparability | 方法输出的task-specific metric字段 |
| PER-011 | pseudo-label/calibration/leakage | Depth Anything teacher/pseudo-data只作来源，不重讲可靠性 |
| PER-013/014 | point cloud/voxel/occupancy与3D grounding | 本页止于depth surface/keypoint/affordance接口 |
| PER-015 | reachability、collision、uncertainty、controller | 本页不从proposal推出可执行或robot success |

## 1. 30秒直觉：先冻结Task与Unit，再谈模型

一个可靠的30秒回答是：

> 我先冻结输出合同：semantic、instance、panoptic和promptable mask不等价；relative depth不能当米制深度。mask和metric depth对齐原图、内参及时间后才能反投影。操作层的keypoint必须带semantic ID、visibility和3D frame，affordance还绑定point、orientation、primitive与state。即使proposal高分，也必须经过reachability、IK、collision和controller；因此单模块mIoU、depth图或actionability都不能直接代表robot success。

这段回答封住五种常见偷换：

1. 一个`mask`字段被默认同时具备类别、实例和时间身份；
2. relative depth可视化被默认当真实米制距离；
3. 无名point被默认当semantic keypoint；
4. “actionable”文本被默认当动作条件化affordance；
5. perception score被默认当closed-loop success。

## 2. Typed Dense Perception Record

### 2.1 最小Schema

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
  "payload": "mask | depth | keypoints | action_proposals",
  "coordinate_space": "original_pixel | resized_pixel | camera_3d | target_3d",
  "unit": "class_id | instance_id | relative | meter | normalized",
  "score_semantics": "class | mask_quality | depth_uncertainty | visibility | success_likelihood",
  "validity_mask": null,
  "frame_transform_revision": null,
  "age_ms": 0
}
```

### 2.2 Shape相同不等于Semantics相同

同一个`H×W`数组可能是class ID、instance ID、binary mask、relative depth或meter depth；同一个`[x,y]`可能是无名point、`mug_handle` semantic keypoint或`pull` contact proposal。只有payload而没有task、unit、frame和score semantics，接口一定会静默漂移。

## 3. Segmentation四类Task

| Task | 预测单元 | 输出 | 两个同类物体 | Stuff | 操作系统常见用途 |
| --- | --- | --- | --- | --- | --- |
| semantic | pixel→class | class score/map | 合并 | 支持 | 区域语义、scene layout |
| instance | object instance | mask+class+score | 分开 | 通常非主目标 | 选定具体目标、crop/tracking seed |
| panoptic | non-overlap segment | segment ID+category/isthing | thing分开 | 全覆盖 | 完整scene decomposition |
| promptable | prompt-conditioned region | one/multiple binary masks+quality | 取决于prompt | 可返回 | language/point/box驱动轮廓 |

两个mug在semantic map里都可标成`mug`，但操作“拿左边那个”需要instance identity；panoptic还需处理thing/stuff与segment merge；SAM prompt mask可能边界很好，却没有category label或跨帧instance ID。

### 3.1 Task先于Metric

问“分割准确率多少”时，先反问：semantic mIoU、instance mask AP、panoptic PQ还是prompt-conditioned mask IoU？dataset、class set、thing/stuff、candidate policy、threshold、matching和denominator不同，数字不能横比。

## 4. Mask2Former：Query→Class+Mask

### 4.1 Pipeline

```text
image -> normalized/padded batch
  -> backbone + pixel decoder
  -> transformer queries with masked attention
  -> pred_logits [B,Q,C+1] + pred_masks [B,Q,H',W']
  -> Hungarian responsibility
  -> class + sigmoid-mask + Dice supervision
  -> semantic / instance / panoptic postprocess
```

固定代码允许同一架构打开三类inference分支，但并不意味着输出合同统一。semantic输出是class per pixel；instance输出保留ranked masks/instances；panoptic输出是non-overlap segment IDs与`category_id/isthing`。

### 4.2 Criterion：Assignment不是Loss本身

\[
\mathcal L_{\mathrm{seg}}
=\lambda_{\mathrm{cls}}\mathcal L_{\mathrm{cls}}
+\lambda_{\mathrm{mask}}\mathcal L_{\mathrm{sigmoid}}
+\lambda_{\mathrm{dice}}\mathcal L_{\mathrm{dice}}.
\]

变量解释：classification监督matched query类别；sigmoid mask CE监督采样pixel；Dice关注区域overlap；λ来自runtime weight dictionary。直觉上，Hungarian先确定query负责哪个GT，再计算可微loss。实现映射：固定Mask2Former criterion明确调用sigmoid CE与Dice；它与OPD assistant-token CE完全不同。

### 4.3 Semantic Inference

\[
P_{c,h,w}=\sum_{q=1}^{Q}
\operatorname{softmax}(l_q)_c\,
\sigma\!\left(m_q(h,w)\right).
\]

变量解释：\(l_q\)是query class logits，\(m_q\)是mask logits，\(Q\)是query数量。每个query用“属于哪个类×覆盖哪些pixel”对semantic map投票。instance/panoptic还要冻结top-k、object threshold、overlap threshold、metadata与resize/postprocess顺序。

## 5. SAM：Promptable Mask Candidate

### 5.1 输入输出合同

```text
original image -> image embedding
point(+/- labels) OR box OR mask_input
  -> prompt encoder + mask decoder
  -> C original-resolution masks
  -> C predicted quality scores
  -> C x 256 x 256 low-resolution logits
```

`multimask_output=true`意味着一个ambiguous click可返回多个合理candidate。因此SAM integration至少冻结：

- prompt坐标在original还是resized image；
- positive/negative point label；
- box corner convention；
- multimask选择policy；
- mask threshold、component与hole policy；
- category/instance/language binding；
- temporal ID、observation age和resegment条件。

### 5.2 Predicted Quality不是Robot Success

SAM score用于候选mask质量排序，不自动等于语义正确、接触面安全或机器人成功概率。若用它触发动作，需在独立task validation上验证calibration与risk–coverage，并继续过PER-015的reachability/collision/controller gate。

## 6. Depth四种合同

| 类型 | Unit/Ambiguity | 可否直接Lift | 必须记录 |
| --- | --- | --- | --- |
| relative monocular | near/far结构，无meter contract | 否 | checkpoint、alignment policy、range |
| metric monocular | 训练域/range定义的metric output | 有条件 | unit、max depth、dataset、validity |
| RGB-D/stereo sensor | 设备unit、invalid code与noise | 有条件 | scale、intrinsics、registration、timestamp |
| aligned relative | reference拟合scale/shift | 仅fit域内 | fit split、scale/shift、residual |

若用reference将relative prediction对齐：

\[
\hat d_m(u,v)=s\,\hat d_r(u,v)+t.
\]

变量解释：\(s,t\)是从合法reference拟合的scale/shift，\(\hat d_r\)是relative prediction，\(\hat d_m\)只是aligned metric candidate。直觉上，排序正确不等于距离正确。实现映射：Depth Anything relative code不会自动执行该对齐，必须保存fit split、reference和residual。

## 7. Depth Anything V2代码合同

### 7.1 Relative Path

固定代码为DINOv2 intermediate features→DPT fusion head→ReLU dense depth。`infer_image`默认518；保持aspect ratio、lower-bound resize、保证14的倍数、ImageNet normalize，最后双线性插值回original \(H\times W\)。README把主模型称为relative depth models，因此“输出shape与原图相同”不等于“单位为米”。

### 7.2 Metric Path

固定metric path使用单独代码与checkpoint：head末端Sigmoid，forward乘`max_depth`，默认20.0。对同一raw head output 0.8，`max_depth=20/80`会得到16/64；所以checkpoint family、训练dataset、range与unit必须进入artifact identity。把relative checkpoint塞入metric code或手动乘常数不构成metric calibration。

### 7.3 Preprocess与Postprocess Trap

把prediction resize回原图只恢复array shape，不会自动修复：

- relative scale/shift；
- resized image与camera intrinsics关系；
- RGB-depth registration；
- thin structure的双线性混合；
- transparent/reflective surface；
- invalid/uncertainty mask；
- temporal staleness。

### 7.4 License也属于Artifact

固定README声明Small model为Apache-2.0，Base/Large/Giant models为CC-BY-NC-4.0；code LICENSE为Apache-2.0。部署或分发必须分别冻结source、checkpoint hash与checkpoint license。

## 8. Mask+Metric Depth→3D Surface

### 8.1 Pixel Backprojection

对original pixel \((u,v)\)、metric depth \(d\)与intrinsics \(K\)：

\[
X_c=d\,K^{-1}
\begin{bmatrix}u\\v\\1\end{bmatrix}.
\]

变量解释：\(X_c\)是camera-frame 3D point，\(d\)必须与该original pixel、camera、timestamp和intrinsics匹配。直觉上，depth unit或pixel transform错一点，3D位置会沿ray整体漂移。实现映射：Depth Anything output还需unit/range/validity，随后才进入PER-002的TF与target frame。

### 8.2 Mask-conditioned Surface

\[
\mathcal P_M=\left\{
d(u,v)K^{-1}[u,v,1]^\top
\mid M(u,v)=1,\ d(u,v)\ \mathrm{valid}
\right\}.
\]

变量解释：\(M\)是选定instance/prompt mask，只有valid depth pixel进入surface。边界pixel若混入background depth会产生飞点；应记录erode policy、boundary band、robust statistic、outlier removal与保留比例。

### 8.3 Weakest-link反例

若mask完全正确，但depth整体scale×2，则所有3D surface point沿ray距离×2；2D IoU仍可满分，机器人接触点却完全错误。这说明“segmentation高分”不能替代3D和action evaluation。

## 9. kPAM：Semantic Keypoint是可解释Task State

### 9.1 四段Factorization

```text
instance segmentation
  -> semantic 3D keypoint detection
  -> optimization-based robot action planning
  -> local dense-geometry execution
```

kPAM不是把物体压成若干无名点，而是用`mug_handle`、`rim`等semantic anchors表达category-level task geometry。相同坐标若semantic ID不同，规划含义就不同。

### 9.2 Planning Contract

\[
T^*=\arg\min_T\sum_j w_j c_j(Tk_j)
\quad\mathrm{s.t.}\quad g_r(Tk_{1:J})\le 0.
\]

变量解释：\(k_j\in\mathbb R^3\)是semantic keypoint，\(T\)是candidate transform，\(c_j\)是几何cost，\(g_r\)是关系/可行性constraint，\(w_j\)可结合visibility/covariance。实现映射：具体detector、private dependency、planner和execution需逐revision审计；公式只表达已冻结的几何合同。

### 9.3 最小Record

```json
{
  "semantic_id": "mug_handle",
  "instance_id": "...",
  "category": "mug",
  "coordinates": [0.1, -0.2, 0.7],
  "frame": "camera | base | object",
  "visibility": true,
  "covariance": [[0.0, 0.0, 0.0]],
  "timestamp": "..."
}
```

只有`[[x,y]]`无法支持category-level 3D planning。

## 10. Where2Act：Affordance是条件成功分布

### 10.1 Model Components

固定3D model包含：

- PointNet++ point feature；
- ActionScore：每点actionability；
- Actor：给定point feature提出6D orientation/action；
- Critic：评估point+orientation interaction success；
- simulation interaction与online sampling，面向articulated object的push/pull。

### 10.2 Score Semantics

\[
A(p,R\mid \pi,s,e)
=\Pr(\mathrm{success}\mid p,R,\pi,s,e).
\]

变量解释：\(p\)是contact point，\(R\)是orientation，\(\pi\)是primitive，\(s\)是object/environment state，\(e\)是训练/eval protocol。直觉上，同一点对push与pull、不同gripper或door state的actionability可相反。实现映射：固定score不自动跨robot/primitive/domain校准。

### 10.3 Proposal不是Controller Action

从affordance proposal到执行仍缺：3D frame、tool/end-effector transform、IK、reachability、collision、force/trajectory、controller rate、replan与recovery。PER-012止于proposal；PER-015负责action gate。

## 11. 端到端Typed Composition

```text
language / point / box prompt
  -> SAM candidate masks OR Mask2Former task-specific segments
  -> explicit instance/category selection
  -> metric Depth Anything checkpoint OR registered sensor depth
  -> valid mask-conditioned 3D surface
  -> semantic keypoint detector + covariance/frame
  -> primitive-conditioned contact/orientation proposals
  -> planner/IK/collision/controller
  -> episode success/failure trace
```

每个artifact都要保存upstream ID：mask必须能追到prompt/model，surface能追到mask/depth/camera，keypoint能追到surface/semantic model，affordance能追到primitive/state，action能追到planner/controller revision。否则无法定位first divergence。

## 12. Objective与Metric对照

| 输出 | 训练/预测单元 | 代表Metric | 不等价于 |
| --- | --- | --- | --- |
| semantic mask | class per pixel/query mixture | mIoU/pixel accuracy | instance AP、PQ、robot contact |
| instance mask | ranked instance masks | mask AP/AR | semantic mIoU、tracking |
| panoptic | non-overlap segments | PQ/SQ/RQ | arbitrary overlap proposals |
| promptable mask | prompt-conditioned candidate | mask IoU/quality | semantic/task success |
| relative depth | aligned/rank structure | aligned AbsRel/δ1，绑定alignment | meter error |
| metric depth | valid metric pixels | AbsRel/RMSE/δ threshold | 3D/robot success |
| semantic keypoint | named visible anchors | PCK/3D distance，绑定frame | naked point hit |
| affordance | point+orientation+primitive | interaction success/ranking | objectness、reachability |

任何数字都继承PER-010 protocol identity：dataset/split、checkpoint、preprocess、task、postprocess、matching、valid denominator、threshold、aggregation和sample unit。

## 13. Failure Taxonomy与诊断顺序

| Failure | 表面症状 | 首查字段 | 最小Probe |
| --- | --- | --- | --- |
| task mismatch | 同类对象被合并 | semantic/instance/panoptic | two-mug case |
| prompt ambiguity | SAM候选不稳定 | prompt+multimask policy | same-click candidates |
| boundary leakage | surface出现飞点 | mask edge/depth discontinuity | erode vs raw surface |
| depth scale | 方向对、距离错 | relative/metric/checkpoint/range | known-distance plane |
| registration | RGB对、depth偏 | camera IDs/extrinsics/timestamp | RGB-depth edge overlay |
| keypoint swap | rim/handle互换 | semantic ID/category mapping | same-coordinate labels |
| keypoint uncertainty | planner抖动 | visibility/covariance | occlusion sweep |
| primitive mismatch | pull点用于push | primitive/state/model ID | same-point push/pull |
| frame/time | proposal正确、执行偏移 | TF/timestamp/age | roundtrip+latency trace |
| controller reject | 高score但不可达 | IK/collision/tool limits | planner rejection reasons |

推荐顺序：task/schema→pre/postprocess→model/checkpoint→depth unit/validity→camera/frame/time→semantic identity→primitive/state→planner/controller→episode metric。不要在depth unit未知时先调IK。

## 14. Fail-closed Pseudocode

```python
def propose_action(image, camera, prompt, primitive, models, policy):
    # 1. Every model and transform must have an immutable identity.
    assert models.segmenter.sha256 and models.depth.sha256
    assert camera.intrinsics_sha256 and camera.timestamp is not None

    # 2. Keep segmentation task semantics; never collapse all outputs into "mask".
    segments = models.segmenter.predict(image, prompt=prompt)
    target = select_segment(segments, task=policy.segmentation_task)
    if target is None or target.score < policy.mask_threshold:
        return reject("no_valid_segment")

    # 3. 3D lift requires metric depth, valid pixels and matching original-image geometry.
    depth = models.depth.predict(image)
    assert depth.unit == "meter" and depth.checkpoint_family == "metric"
    valid = target.mask & depth.validity_mask
    if valid.sum() < policy.min_surface_pixels:
        return reject("insufficient_metric_surface")

    # 4. Backproject and transform at the same camera timestamp.
    surface = backproject(valid, depth.values, camera.intrinsics)
    surface = transform_at_timestamp(surface, camera.tf_revision, camera.timestamp)

    # 5. Semantic keypoints keep identity, visibility and covariance.
    keypoints = models.keypoint.predict(target, surface)
    if any((not k.visible) or k.covariance > policy.max_cov for k in keypoints):
        return reject("uncertain_semantic_keypoint")

    # 6. Affordance proposals are conditioned on primitive and current state.
    proposals = models.affordance.propose(surface, primitive, camera.robot_state)

    # 7. Perception scores never bypass reachability, IK, collision or controller gates.
    feasible = planner_filter(proposals, keypoints, camera.robot_state)
    return feasible if feasible else reject("no_feasible_action")
```

这段是目标合同，不是本地实现事实。真实系统还需checkpoint/license、depth uncertainty、mask candidate policy、tool geometry、planner/IK/controller revision与episode logger。

## 15. 本地OPD：名字是Affordance，输出仍是Point

### 15.1 真实链

```text
ShareRobot affordance {x,y} / trajectory points
  -> scale to 0..1000
  -> prompt: actionable affordance location
  -> target: <point>[[x,y], ...]</point>
  -> point/box/text parser and static metric
```

### 15.2 五文件Audit

1. `build_prompt_pool.py`把`affordance.x/y`变成单个`gt_points`与`task_type=affordance_pointing`；无primitive/orientation/state/success head。
2. `point_data_only.py`最终调用`point_answer(scaled)`；prompt语义不改变representation。
3. `build_expert_mixes_seed0.py`与`eval_qwen_vl_raw_holdout.py`只有point/box/text route/parser/metric。
4. 五个固定文件对`keypoint/segment_anything/sam_model/mask_rle/polygon/<mask>/depth`均为0匹配。

静态zero-match只覆盖选定路径，不排除远端、历史或未归档artifact。但在证据出现前，安全结论是“affordance-labelled point supervision”，不是dense perception stack。

## 16. Project Truth Boundary

| 项目 | 当前可以挂钩 | 当前不能说 | 补强Artifact |
| --- | --- | --- | --- |
| OPD | affordance-labelled point、point/box parser/static holdout | mask/depth/keypoint/dense affordance/robot result | model/checkpoint/raw dense outputs、3D/episode bundle |
| WAM | 可讨论future frame是否保存contact geometry | 已训练seg/depth auxiliary或其提升 | local head/config/loss curve/matched eval |
| Robot Harness | typed perception result可进入tool/scope/cancel gate | 已运行视觉模型或真实3D controller | perception server、controller trace、episodes |
| OpenPiVLA | end-to-end image→action可比较显式dense intermediate | 已集成SAM/depth/keypoint | code/checkpoint/ablation/rollout |
| UWM | future observation可作为geometry diagnostic | learned affordance map或real transfer | raw predictions/checkpoints/episodes |

公共方法只能证明机制可解释，不证明已被个人项目集成。Git文件存在也不能替代候选人逐文件ownership确认。

## 17. 面试回答模板、追问与危险答案

### 17.1 两分钟结构化回答

> 我把操作感知拆成task-typed segmentation、metric geometry、semantic anchors和action-conditioned proposal。Mask2Former可统一semantic/instance/panoptic architecture，但各分支postprocess与metric不同；SAM给prompt-conditioned mask candidates和quality，不自带类别或robot-success校准。Depth Anything V2的relative路径是ReLU dense map，metric路径是独立Sigmoid×max-depth代码和checkpoint，resize回原图不等于恢复米制几何。只有metric depth与mask、内参、时间对齐后才能形成3D surface。kPAM式keypoint还要semantic ID、visibility、frame；Where2Act式affordance绑定point、orientation、primitive和state。最后必须过IK、collision和controller。本地OPD目前只是affordance-labelled point target，不能称完整感知栈。

### 17.2 高频追问

1. semantic、instance、panoptic和promptable mask分别解决什么？
2. Mask2Former为什么能用同一架构做三种task，但metric仍不同？
3. Hungarian assignment与mask loss怎样分工？
4. SAM multimask该怎样选？predicted quality代表什么？
5. relative depth为何不能直接反投影？
6. `max_depth`改变会怎样影响metric output？
7. resize回原图为何不等于几何对齐？
8. mask边界为何容易产生3D飞点？
9. semantic keypoint比普通point多哪些字段？
10. kPAM如何把keypoint变成planning cost/constraint？
11. Where2Act的ActionScore、Actor和Critic各负责什么？
12. affordance为何必须绑定primitive和state？
13. proposal高分为何仍不能执行？
14. OPD的affordance point和Where2Act有什么本质差别？

### 17.3 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “有mask就知道是哪个物体” | prompt mask未必有class/instance ID | 冻结task与binding |
| “SAM quality高就能抓” | score未对robot success校准 | 加task validation和action gate |
| “Depth Anything输出就是米” | relative/metric路径混用 | 绑定metric checkpoint、range和unit |
| “resize回原图就对齐相机” | array shape≠camera registration | 对齐intrinsics/extrinsics/time |
| “一个point就是keypoint” | 缺semantic ID/frame/visibility | 用typed keypoint record |
| “actionable point就是affordance model” | 缺primitive/orientation/state/success | 明确point supervision边界 |
| “affordance score高就执行” | 无IK/collision/controller | fail-closed planner gate |
| “我实现了完整OPD操作感知” | selected code只有point/box/text | 只陈述直接文件证据与ownership缺口 |

## 18. 白板Checklist与练习标准

能够不看材料完成：

- segmentation四类task与输出/metric；
- Mask2Former class+mask query、assignment和三项loss；
- SAM prompt/multimask/quality边界；
- relative/metric/sensor/aligned depth四类合同；
- Depth Anything V2 relative与metric代码差异；
- mask+metric depth反投影与边界飞点；
- semantic keypoint record和kPAM planning公式；
- Where2Act ActionScore/Actor/Critic与条件score；
- 完整typed composition和failure诊断顺序；
- OPD point-only真实性边界；
- 两分钟回答与至少六个追问。

`drafted`不等于掌握。只有真实口述、追问与纠错后才能改变题卡状态；本轮不创建`coaching_state.md`。

## 19. 结论与下一步

Dense perception对机器人有价值的前提不是“模型更强”，而是task、unit、frame、time、score和downstream gate全都可追溯。Segmentation提供区域，metric depth提供几何，semantic keypoint提供可解释task state，primitive-conditioned affordance提供候选交互；任何一层语义或坐标漂移都会让后续模块失效。

本地OPD当前最准确的结论仍是affordance-labelled point supervision和point/box/text静态评估；没有证据支持SAM/Mask2Former、relative/metric depth、semantic keypoint、Where2Act式head或robot闭环。

`VLA-PER-012` source/knowledge/card已在独立bounded slices同步，题卡保持`unseen`。下一bounded slice只冻结`VLA-PER-013` point-cloud/voxel/BEV/occupancy representation source；不生成knowledge/card，不创建`coaching_state.md`，不改变任何mastery。

## References

1. [PER-012 Segmentation / Depth / Keypoint / Affordance Source Freeze](../sources/vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html)：固定论文/代码revision、SHA、license、本地OPD audit与deterministic probes。
2. Cheng et al., [Mask2Former v3](https://arxiv.org/abs/2112.01527v3)；[official repository@9b0651c](https://github.com/facebookresearch/Mask2Former/tree/9b0651c6c1d5b3af2e6da0589b719c514ec0d69a)。
3. Kirillov et al., [Segment Anything v1](https://arxiv.org/abs/2304.02643v1)；[official repository@dca509f](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
4. Yang et al., [Depth Anything V2 v2](https://arxiv.org/abs/2406.09414v2)；[official repository@a561b84](https://github.com/DepthAnything/Depth-Anything-V2/tree/a561b849ebae10a6f5ef49e26c83cbbcd36c71bf)。
5. Gao & Tedrake, [kPAM v2](https://arxiv.org/abs/1903.06684v2)；[official repository@7214936](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
6. Mo et al., [Where2Act v2](https://arxiv.org/abs/2101.02692v2)；[official repository@1daf1a2](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
7. [PER-002 3D Lift / Frame](vol_06_per002_3d_lift_frame.html)、[PER-008 Representation Choice](vol_06_per008_representation_choice.html)、[PER-010 Metric / Parser](vol_06_per010_grounding_metric_parser_protocol.html) 与 [PER-011 Teacher Noise / Calibration / Leakage](vol_06_per011_pseudo_label_teacher_noise_calibration_leakage.html)。
8. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
