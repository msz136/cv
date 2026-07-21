# VOL 06 Perception / Grounding / Navigation：3D Grounding、Spatial Relation 与 Open-vocabulary 3D Scene（PER-014）

> 状态：`drafted / VLA-PER-014 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-007` 2D open-vocabulary grounding、`VLA-PER-013` point/voxel/BEV/occupancy representation；后续：`VLA-PER-015` reachability、IK、collision 与 controller gate。  
> 来源入口：[PER-014 3D Grounding / Spatial Relation / Open-vocabulary Source Freeze](../sources/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html)；对应自测：[PER-014 Atomic Card](../questions/vol_06_per014.html)。本页只把已冻结证据转成可教学、可诊断、可面试回答的知识；题卡已生成并保持`unseen`，不创建训练状态，也不改变任何 mastery。

## 问题（Question）

面试官问“3D grounding 怎么做，spatial relation 与 open-vocabulary 3D scene 怎么落地”时，最危险的回答是把所有方法概括成“把 CLIP 特征投到点云上，再做相似度”。一个可靠回答必须先区分输出：是在 raw scene 中定位 3D box、在已分割对象中选 candidate、给每个点赋开放词表语义、返回 3D instance mask、查询连续 language field，还是查询增量 semantic map；再冻结 candidate、frame、relation arity、prompt、negative、normalization、threshold 与 metric；最后说明这些 semantic target 为什么还不是可执行机器人动作。

本节点的主链是：

```text
PER-007 2D region-text semantics
        +
PER-013 metric 3D representation
        |
        v
candidate / point / mask / field / map identity
        -> language score and spatial relation
        -> output-specific metric and failure diagnosis
        -> semantic target with uncertainty
        |
        v
PER-015 reachability / IK / collision / controller gate
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-014负责 |
| --- | --- | --- |
| PER-007 | 2D detector/segmenter、region-text score、prompt/threshold基础 | 把语言绑定到3D candidate、point、mask、field或map |
| PER-013 | point/voxel/BEV/occupancy的frame、量化、sampling、aggregation | 3D entity identity、开放词表feature与spatial relation |
| PER-002/003 | 2D→3D lift、pose/frame/time与multi-view lineage | 消费这些几何合同，不声称semantic score能修复错误pose |
| PER-016 | localization、odometry、SLAM与map drift | 本页只验证map/query接口，不负责闭合SLAM |
| PER-015 | reachability、IK、collision、controller | 本页输出semantic target，不从相似度直接推出action |

PER-014不重复PointNet++、voxel、BEV或occupancy内部结构，也不把论文中的公有机制写成个人项目实现。

## 1. 30秒直觉：先问输出原子，再问模型

一个可靠的30秒回答是：

> 3D grounding不是单一任务。我先写清输出原子和候选来源：ScanRefer从场景proposal里选并回归3D box；ReferIt3D在已分割对象里做top-1 listener；OpenScene给每个3D点开放词表feature；OpenMask3D先有class-agnostic instance masks，再用多视图CLIP查询；LERF是per-scene多尺度连续language field；ConceptFusion是pose/depth约束下的可查询3D feature map。然后我冻结frame、relation arity、encoder/prompt/negative、normalization、threshold和metric。target不在候选集合时准确率上界就是0；point semantic也不会自动变成instance identity。最后这些输出仍要经过reachability、IK、collision和controller gate，不能把cosine或IoU直接叫robot success。

这段回答先封住八个偷换：

1. 3D box、candidate ID、point score、instance mask、field heatmap与map point被混成一种输出；
2. raw-scene detector与已分割对象listener被混成同一任务；
3. per-point semantic class被当作稳定instance identity；
4. target不在candidate set仍假设matching head可以恢复；
5. left/right不记录observer/world/object reference frame；
6. dot、cosine、softmax probability与relative relevance被统称confidence；
7. query heatmap被当作SLAM正确、可达或可抓；
8. public paper、local asset或Git身份被升级为个人实现与收益。

## 2. 六类输出原子

| 任务 | 输入前提 | 最小输出 | 典型方法 | 第一瓶颈 | 对应指标 |
| --- | --- | --- | --- | --- | --- |
| 3D referring localization | raw/encoded scene + utterance，可含proposal generator | 3D box | ScanRefer | proposal recall、box geometry | Acc@3D-IoU 0.25/0.5、oracle recall |
| candidate-object identification | 已分割3D objects + utterance | candidate ID / top-1 | ReferIt3D | segmentation、distractor、relation frame | top-1、easy/hard、view-dependent split |
| open-vocabulary point semantics | points + language-aligned features | per-point label/score | OpenScene | view coverage、distillation、prompt | per-class IoU、mIoU/mAcc/allAcc |
| open-vocabulary 3D instance | class-agnostic masks + posed views | mask ID/class/score | OpenMask3D | mask proposal、visibility、view crop | AP/AP50/AP25、proposal oracle |
| continuous language field | posed images + per-scene optimized field | continuous relevance / heatmap | LERF | scale、negative calibration、per-scene fit | localization/relevancy protocol |
| queryable semantic map | RGB-D + intrinsics + pose + features | scored map points/regions | ConceptFusion | pose/depth drift、fusion、threshold | retrieval/localization/map protocol |

“Open-vocabulary”只说明query/label空间不是一个训练时固定小词表，不说明模型理解所有概念，不说明无需prompt与threshold，也不说明输出具有instance、metric geometry或robot affordance。

## 3. Typed 3D Grounding Manifest

### 3.1 最小 Schema

```json
{
  "sample_id": "scene/query pair",
  "scene_artifact": "point | voxel | mesh | radiance_field | point_map",
  "scene_revision": "sha256:...",
  "query_text": "the chair left of the table",
  "entity_candidates": {
    "source": "detector | segmented_objects | masks | points | continuous_field",
    "revision": "sha256:...",
    "count": 12,
    "target_present": true
  },
  "output_type": "3d_box | candidate_id | point_scores | instance_mask | field_heatmap | map_points",
  "coordinate_frame": "camera | base | map | scene",
  "axis_unit": "x-forward/y-left/z-up, meter",
  "pose_depth_intrinsics_revision": "sha256:...",
  "relation": {
    "predicate": "left_of",
    "arity": 2,
    "reference_frame": "observer | world | anchor_object",
    "entity_ids": ["target", "anchor"],
    "threshold_meter": null
  },
  "encoder": "name/checkpoint/revision",
  "prompt_template": "a photo of {}",
  "negative_prompts": ["object", "things", "stuff", "texture"],
  "feature_normalization": "l2",
  "score": "cosine | dot | relative_softmax | learned_logit",
  "temperature_threshold_topk": [1.0, 0.5, 1],
  "metric_protocol": "top1 | Acc@IoU | semantic_mIoU | instance_AP",
  "metric_revision": "sha256:...",
  "timestamp_and_age": ["t", "age_ms"]
}
```

### 3.2 为什么它属于结果身份

同一句“left chair”在observer yaw改变后可指向另一对象；同一组embedding用dot或cosine会得到不同ranking；同一mask用top-1 view或多视图mean会得到不同score；同一预测box在IoU 0.25与0.5上会得到不同结论。因此scene、candidate、relation、encoder/prompt、score和metric都必须进入manifest/hash。

只保存一张彩色heatmap不能回答：候选是否含target、颜色是否scene-level min-max、query是否用了negative prompt、3D位置是否来自正确pose、阈值如何选、metric按point还是instance聚合。

## 4. 通用 Pipeline：Geometry、Entity、Language、Decision

```text
scene geometry + frame/time/revision
  -> entity atomization
       proposals | segmented objects | points | masks | field samples | map points
  -> language encoding and prompt contract
  -> entity-language score
  -> optional spatial-relation filtering/reasoning
  -> calibrated decision: top-k / threshold / unknown
  -> output-specific metric and raw trace
  -> PER-015 action feasibility
```

四层不能颠倒：

1. **Geometry**：point或map位置是否在正确frame、unit、pose与timestamp；
2. **Entity**：什么是一个候选，target是否存在，mask是否split/merge；
3. **Language**：encoder、prompt、negative、normalization与relation语义；
4. **Decision**：score、temperature、threshold、top-k、unknown与metric。

先出现的错误会污染所有下游。一个semantic score很高的点若被错误pose写进墙内，仍是错误3D target；一个完美listener若candidate set漏掉目标，仍无法成功。

## 5. Candidate Grounding 与硬上界

对候选集合\(\mathcal C=\{1,\ldots,M\}\)，通用language-conditioned ranking可写为：

\[
s_j=g_\theta\!\left([\mathbf p_j,\mathbf e_q]\right),
\qquad
\mathcal L_{\mathrm{ref}}
=-\sum_{j=1}^{M}y_j\log\operatorname{softmax}(s)_j.
\]

变量解释：\(\mathbf p_j\)是第\(j\)个proposal/object feature，\(\mathbf e_q\)是query embedding，\(s_j\)是matching logit，\(y_j\)是target分布。直觉：语言只在已有候选中排序。实现映射：ScanRefer固定代码实际对proposal-language feature输出`cluster_ref`并用`SoftmaxRankingLoss`；ReferIt3D固定训练脚本对candidate logits使用cross entropy。上式是统一教学表达，不宣称两份代码逐行相同。

若GT target不在\(\mathcal C\)中，则该sample的最大top-1为0。应同时报告：

- target-present/proposal recall；
- oracle candidate/box质量；
- 给定candidate的listener accuracy；
- end-to-end metric。

只报最后一个数会把“候选漏检”和“语言匹配错误”混在一起。

## 6. ScanRefer：Raw Scene → Proposal → 3D Box

ScanRefer从场景点云与自然语言出发，使用VoteNet-style 3D object proposals，再把proposal feature与language feature拼接，屏蔽invalid objectness，输出每个proposal的reference score。其输出原子是3D box，不只是candidate class。

### 6.1 三条loss/metric链

| 链 | 作用 | 典型证据 | 不能替代 |
| --- | --- | --- | --- |
| objectness + vote/box | 生成与回归3D proposals | `refnet.py`、`loss_helper.py` | language matching |
| reference ranking | 从valid proposals中选query target | `match_module.py`、`SoftmaxRankingLoss` | box geometry质量 |
| language auxiliary | 预测object category等辅助信号 | `lang_scores` CE | end-to-end grounding |

3D box IoU为：

\[
\operatorname{IoU}_{3D}(B_p,B_g)
=\frac{\operatorname{Vol}(B_p\cap B_g)}
{\operatorname{Vol}(B_p\cup B_g)}.
\]

变量解释：\(B_p\)和\(B_g\)分别是预测与GT box。两个unit cube仅在x方向错开0.5时，intersection为0.5、union为1.5，IoU是1/3：通过0.25但失败0.5。实现映射：固定`eval_helper.py`同时维护reference selection与box-overlap评估；`ref_acc`与`Acc@IoU`不可互换。

### 6.2 面试中主动补的诊断

先查proposal recall与oracle IoU，再查objectness mask、candidate score、unique/multiple split，最后查box regression。如果候选index选对但IoU 0.5失败，问题更接近geometry；如果oracle candidate已很好但top-1错，才优先查language/distractor。

## 7. ReferIt3D：已分割对象中的Neural Listener

ReferIt3D假设scene已经被分成对象集合。固定模型用共享object encoder提取每个对象的point/color feature，编码utterance，再用DGCNN构建对象图，并按配置在graph前、后或两处融合language，最终为每个candidate产生logit。

其listener loss为：

\[
\mathcal L_{\mathrm{listener}}
=-\log
\frac{\exp s_{j^*}}
{\sum_{j\in\mathcal C}\exp s_j}.
\]

变量解释：\(j^*\)是被指代对象，\(\mathcal C\)是当前scene的候选对象集合。直觉：对象已经存在，模型学习用类别、属性、几何关系和distractor信息选一个。实现映射：固定`referit3d_net.py`输出`logits`，`train_referit3d.py`用CE；object-class和language auxiliary logits不能被误说成detector head。

### 7.1 ScanRefer与ReferIt3D不可合并

| 维度 | ScanRefer | ReferIt3D |
| --- | --- | --- |
| candidate来源 | 模型从scene生成3D proposals | 数据已提供segmented objects |
| 输出 | 3D referring box | candidate object ID/top-1 |
| 主要上界 | proposal recall + box quality | object segmentation/candidate presence |
| 核心metric | Acc@3D-IoU、ref selection | top-1 accuracy及distractor split |
| 适合追问 | proposal miss还是matching错 | relation/distractor还是object feature错 |

说“ReferIt3D可以直接检测任意3D物体”忽略了它的candidate assumption；说“ScanRefer只做分类”忽略了proposal与box链。

## 8. Spatial Relation：Reference Frame 与Arity

令\(R\)把reference frame的轴映射到世界坐标，target \(a\)相对anchor \(b\)的left relation可写为：

\[
r_{\mathrm{left}}(a,b;R)
=\mathbf 1\!\left[
\left(R^\top(\mathbf p_a-\mathbf p_b)\right)_x<0
\right].
\]

变量解释：\(\mathbf p_a,\mathbf p_b\)是两个entity的位置，\(R\)可来自observer、world或anchor-object frame。直觉：先把相对位移转进声明的参考系，再判断x轴符号。实现映射：Sr3D relation生成与ReferIt3D listener能提供relation/distractor训练入口，但实际artifact仍必须保存frame、anchor IDs、axis和tolerance。

同一对点在yaw 0°时可为left，在yaw 180°时变成right。没有\(R\)的predicate不可复算。

### 8.1 Relation最小合同

| Relation | 最小元数 | 必须冻结 | 典型shortcut |
| --- | ---: | --- | --- |
| left/right/front/behind | 2 | target、anchor、observer/world/object frame、axis | image-left冒充map-left |
| above/below | 2 | gravity/up axis、centroid/box/support定义 | pixel-y冒充metric height |
| near/far | 2 | metric、unit、threshold或rank policy | scene min-max冒充固定距离 |
| inside/on/supporting | 2 | geometry primitive、tolerance/contact policy | bbox overlap冒充support/contact |
| between | 3 | target、两个anchors、segment/corridor tolerance | 只给一个anchor |
| closest/farthest | set-valued | candidate set、distance metric、tie rule | 改候选仍比较accuracy |

### 8.2 View-dependent 与View-independent

left/right/front/behind常随observer变化；above/below通常绑定gravity；inside/support更依赖物体几何。评估应按relation family与view dependence分层，否则模型可以靠绝对位置、类别共现或anchor频率获得表面accuracy。

## 9. Open-vocabulary Score：相似不等于置信

对entity feature \(\mathbf f_j\)与text feature \(\mathbf t_q\)，cosine为：

\[
s_{j,q}=
\frac{\mathbf f_j^\top\mathbf t_q}
{\|\mathbf f_j\|_2\,\|\mathbf t_q\|_2}.
\]

变量解释：cosine只比较方向；raw dot还受feature norm影响。直觉：`[10,0]`和`[1,0]`对query `[1,0]`的dot分别是10和1，但cosine都为1。实现映射：OpenMask3D、OpenScene evaluation与ConceptFusion query路径都显式或隐式依赖feature normalization；是否normalize属于协议身份。

对positive \(s^+\)与negative \(s^-\)，relative probability可写为：

\[
p^+=
\frac{\exp(s^+/\tau)}
{\exp(s^+/\tau)+\exp(s^-/\tau)}.
\]

变量解释：\(\tau\)是temperature。若positive=.55、negative=.60、\(\tau=1\)，则\(p^+=0.4875026\)，不通过0.5。实现映射：固定LERF encoder将positive与`object/things/stuff/texture` negatives两两softmax，并选择最保守comparison；raw cosine不能被叫作同一个relative confidence。

必须冻结：encoder/checkpoint、tokenizer、prompt template/ensemble、大小写与复数、negative set、L2 normalization、temperature、candidate set、top-k、threshold、unknown policy与scene-level min-max。

## 10. OpenScene：把2D开放词表Feature带进3D

OpenScene有两条紧密相关路径：把2D language-aligned pixel feature按几何对应融合到3D points；或训练3D sparse network去蒸馏这些fused features。固定代码的cosine distillation为：

\[
\mathcal L_{\mathrm{distill}}
=1-\cos\!\left(\mathbf f_i^{2D},\mathbf f_i^{3D}\right).
\]

变量解释：\(\mathbf f_i^{2D}\)是投影到第\(i\)个3D点的2D teacher feature，\(\mathbf f_i^{3D}\)是3D network输出。直觉：让3D feature保留视觉-语言embedding方向。实现映射：固定`distill.py`对mask后的feature调用`CosineSimilarity`；`evaluate.py`再与text features计算score并报告semantic mIoU/mAcc/allAcc。

### 10.1 Per-point semantic的能力边界

能回答：哪些points与“chair”相似，或按label set给point分类。不能自动回答：两个chair中哪个是目标、哪些points属于同一个实例、目标box在哪里、哪个抓取点可达。无2D view coverage的point应显式unknown或使用冻结fallback，不能静默当background。

## 11. Semantic 与Instance 是两条轴

若两个chair的per-point class feature相同，语义预测可以完全正确，但“左边那把chair”的instance ID仍未知。实例化至少需要mask partition、connected/graph structure、tracking或proposal identity。

| 情况 | semantic结果 | instance结果 | 诊断 |
| --- | --- | --- | --- |
| 两个chair被同一mask合并 | chair点可能全对 | instance merge | mask proposal/partition错 |
| 一个chair被分成多个mask | class可都为chair | instance split | mask consistency错 |
| target points无teacher coverage | unknown/低质 | target可能漏掉 | view/pose/occlusion错 |
| class正确但left chair选错 | semantic对 | relation/identity错 | frame、anchor或instance graph错 |

因此semantic mIoU不能替代instance AP或referring top-1。

## 12. OpenMask3D：Mask Proposal先于文本查询

OpenMask3D先生成class-agnostic 3D masks；再为每个mask选择top-k可见视图，把3D mask投影点作为SAM辅助，生成多尺度crops，提取normalized CLIP features并跨view聚合。文本query只负责给已有mask排序/分类。

### 12.1 Proposal bottleneck

若mask generator把target漏掉，最大query recall为0；若两个objects被merge，文本score不能无中生有地拆分；若一个object被split，多个高分mask会造成duplicate。应报告class-agnostic proposal oracle与open-vocabulary classification两层结果。

### 12.2 View aggregation

一个可审计的加权聚合为：

\[
\bar{\mathbf f}_m=
\frac{\sum_{v\in\mathcal V_m}w_{m,v}\,\mathbf f_{m,v}}
{\sum_{v\in\mathcal V_m}w_{m,v}+\epsilon}.
\]

变量解释：\(\mathcal V_m\)是mask \(m\)的selected views，\(w_{m,v}\)可由visibility、crop quality或固定平均得到。直觉：只让真正看到对象的视图贡献feature。实现映射：固定OpenMask3D代码选择top-k visible views，对多尺度image feature normalize后取mean；上式是诊断性推广，不声称fixed code已有learned weight。

`[1,0]`与`[-1,0]`均值为零，之后cosine undefined；加入orthogonal view也会让query score从1变成约0.7071。应保存per-view embedding/score、visibility、crop、occlusion和norm，而不是只保存mean。

## 13. LERF：Per-scene Continuous Language Field

LERF将multi-scale CLIP/DINO supervision嵌入per-scene radiance field。沿ray \(r\)、scale \(s\)的rendered feature可写为：

\[
\hat{\mathbf f}(r,s)=
\sum_i w_i(r)F_\theta(\mathbf x_i,s).
\]

变量解释：\(F_\theta(\mathbf x_i,s)\)是在3D sample与physical scale处的language feature，\(w_i(r)\)是volume-rendering weight。直觉：通过posed images学习一个连续、可按尺度查询的3D feature field。实现映射：固定LERF代码在多个scale上求relevance，positive query与固定negatives比较；输出是field relevance，不自动给稳定object ID或box。

### 13.1 论文目标与fixed code边界

当前固定repo对CLIP output使用weight 0.1、delta 1.25的Huber loss，对DINO使用MSE。面试中可以讲“学习language-aligned continuous field”，但不能说“代码逐行就是负余弦loss”。per-scene optimization也意味着它不是一个无需scene fitting的通用3D detector。

### 13.2 Scale是query identity

“mug”和“handle”的适合尺度不同。LERF跨scale搜索relevance，因此scale range、sample count、selection rule和negative set属于结果身份。最大relevance heatmap仍需阈值、component/peak policy才能变成discrete target。

## 14. ConceptFusion：增量可查询Semantic Map

ConceptFusion把global image feature与local region feature结合成pixel-aligned representation，再借助depth、intrinsics与pose把像素提升/关联到3D map points，累积多帧feature。抽象更新为：

\[
\mathbf f_{k,t}=
\frac{\bar c_k\mathbf f_{k,t-1}+\alpha\mathbf f_{u,v,t}}
{\bar c_k+\alpha},
\qquad
\bar c_k\leftarrow\bar c_k+\alpha.
\]

变量解释：\(\mathbf f_{k,t}\)是map point \(k\)在时刻\(t\)的feature，\(\mathbf f_{u,v,t}\)是当前pixel feature，\(\alpha\)是correspondence/confidence weight，\(\bar c_k\)是累计权重。直觉：同一3D位置从多帧获得semantic evidence。实现映射：固定example使用RGB-D、intrinsics、pose与GradSLAM/Pointclouds融合feature；具体邻域、merge与weight以固定revision为准。

固定text-query example对text和map embeddings做L2 normalize、计算cosine，再用top-k或scene-level min-max threshold可视化。min-max结果是相对当前scene的ranking，不是跨scene calibrated probability。

### 14.1 Map query不证明SLAM正确

如果pose或depth错误，正确语义feature会被写进错误3D位置；多帧平均还可能把动态对象拖成ghost。必须同时记录pose revision、depth validity、association distance、update count、age与dynamic-object policy。semantic query成功不能反证geometry、localization或map consistency正确。

## 15. Field、Map、Mask、Box怎样选

| 下游问题 | 最小充分原子 | 推荐方向 | 不必要/不足 |
| --- | --- | --- | --- |
| “那张椅子的3D框” | proposal + box geometry | ScanRefer式box grounding | 只有point heatmap不足 |
| “已分割对象中是哪一个” | candidate IDs + graph | ReferIt3D式listener | 重跑detector可能多引入误差 |
| “场景哪些点像fire extinguisher” | per-point semantic feature | OpenScene式point query | 不需要先承诺instance |
| “返回完整对象mask” | class-agnostic masks + query | OpenMask3D式instance query | point class不等于instance |
| “在连续场中找某概念峰值” | scale-conditioned field | LERF式field | 需per-scene fit与peak policy |
| “跨帧累计并查询语义地图” | pose/depth-aligned map | ConceptFusion式map | 需SLAM/age/dynamic policy |

选择原则是downstream minimum sufficiency、候选来源与runtime budget，而不是把六个方法串成一个越长越好的pipeline。

## 16. Metric 与协议不可互换

| 层 | 报告内容 | 不能替代 |
| --- | --- | --- |
| proposal | target-present recall、oracle IoU、proposal count | listener top-1 |
| referring box | Acc@IoU 0.25/0.5、unique/multiple | `ref_acc`、semantic mIoU |
| candidate listener | top-1、distractor/easy-hard/view split | detector recall/box IoU |
| point semantics | per-class IoU、mIoU/mAcc/allAcc、seen/unseen | instance AP |
| instance semantics | AP/AP50/AP25、mask oracle | point mIoU |
| field/map query | localization/retrieval、threshold calibration、pose quality | robot success |

还要冻结denominator：按query、scene、object、point还是class平均；是否去掉no-target或unknown；threshold是在validation上选还是test后调；是否对同一scene的多个queries视作独立样本。不同protocol的数字不能直接排榜。

## 17. 九个Deterministic Probes

| Probe | 固定输入 | 结果 | 诊断含义 |
| --- | --- | --- | --- |
| 3D box IoU | unit cubes，x错开0.5 | IoU=`1/3`；过0.25、不过0.5 | threshold属于metric identity |
| dot vs cosine | q=`[1,0]`；f=`[10,0]`,`[1,0]` | dot `[10,1]`；cos `[1,1]` | normalization改变ranking/scale |
| candidate bottleneck | GT 7；candidates `[2,4,5]` | 最大top-1=`0` | 先查target-present |
| relation frame | 同两点；yaw 0/180° | left翻为right | predicate必须绑定frame |
| semantic vs instance | 两个同class chair | class相同；instance ID不同 | semantic不自动给identity |
| view cancellation | `[1,0]`,`[-1,0]` mean | `[0,0]`，cos undefined | aggregation需zero-norm gate |
| view selection | top view `[1,0]`，再加orthogonal view | score 1→`0.70710678` | top-k/view policy改变score |
| negative calibration | positive .55，negative .60 | \(p^+=0.4875026\) | raw score不是relative pass |
| prompt identity | q1 scores `[.8,.6]`；q2 `[.6,.8]` | argmax 1→2 | prompt/embedding属于协议 |

这些probe证明机制边界，不是ScanNet benchmark复现，也不支持本地项目收益。

## 18. First-divergence Failure Diagnosis

| 失败症状 | 第一检查层 | 关键字段 | 最小probe |
| --- | --- | --- | --- |
| query落在错误物理位置 | geometry | frame/axis/unit/pose/depth/time | landmark reprojection |
| target完全无分数 | candidate/coverage | target-present、view coverage | oracle candidate |
| 正确类别但选错同类物体 | instance/relation | mask ID、anchor、frame | two-chair relation test |
| box index正确但IoU失败 | geometry/box | center/size/orientation | threshold sweep |
| mask merge/split | proposal | mask count、overlap、component | oracle mask AP |
| 多视图后分数下降 | aggregation | per-view score/norm/visibility | top-1 vs mean |
| prompt微调后ranking翻转 | language | template/tokenizer/negative | prompt matrix |
| scene间阈值失效 | calibration | temperature/min-max/unknown | held-out calibration |
| map里出现semantic ghost | fusion/time | pose/age/dynamic policy | moving-object trace |
| semantic target不可执行 | action gate | reachability/IK/collision/controller | PER-015 rejection log |

推荐顺序：

```text
scene revision / frame / pose / time
  -> candidate source and target-present
  -> point/mask/instance identity
  -> relation arity and reference frame
  -> encoder / prompt / negative / normalization
  -> score / threshold / unknown
  -> output-specific metric
  -> reachability / controller / episode
```

不要在candidate recall未知时先调prompt，也不要在pose错误时先换language encoder。

## 19. Fail-closed Inference Pseudocode

```python
def grounded_3d_query(scene, query, manifest):
    # 1. Semantic scoring cannot repair an unidentified physical scene.
    require(scene.revision, scene.frame, scene.axis_unit)
    require(manifest.pose_depth_intrinsics_revision)

    # 2. Freeze the query interface before comparing scores or runs.
    require(manifest.encoder, manifest.prompt_template)
    require(manifest.feature_normalization, manifest.score)
    require(manifest.temperature_threshold_topk)

    # 3. Candidate atoms must match the requested output type.
    candidates = build_candidates(scene, manifest.entity_candidates)
    audit_candidate_count_and_target_presence(candidates)
    if manifest.entity_candidates.target_present is False:
        return {"status": "proposal_miss", "executable": False}

    # 4. Spatial predicates require explicit arity, anchors and reference frame.
    validate_relation_arity(query.relation)
    require(query.relation.reference_frame)

    # 5. Preserve raw per-candidate and per-view evidence before aggregation.
    raw = score_candidates(candidates, query, manifest)
    audit_view_coverage_zero_norm_and_unknown(raw)

    # 6. Apply the frozen decision and an output-specific metric protocol.
    target = apply_frozen_threshold_or_topk(
        raw, manifest.temperature_threshold_topk
    )
    target["metric_protocol"] = manifest.metric_protocol

    # 7. This node returns a semantic target, never an executable action.
    target["executable"] = False
    target["next_gate"] = "VLA-PER-015"
    return target
```

这是面试与目标实现合同，不是本地项目已有代码。真实系统还需local candidate generator、pose/depth lineage、model/checkpoint、query service、raw predictions、calibration set、latency/memory和controller integration。

## 20. OPD：2D Image Relation 不是3D Relation

固定`muxi@756e27e...`直接证据：

| Artifact | 直接支持 | 不能支持 |
| --- | --- | --- |
| `build_expert_mixes_seed0_v2.py` | `spatial_rel_expert`来自Visual Genome 2D relationship；prompt明确写“in the image” | observer/world 3D frame、3D object graph、3D box/mask |
| `point/point_data_only.py` | 2D annotation points经x/y几何转box；输出可为0–1000 point/box或boolean | z、meter、pose、3D instance、language field |

安全项目表述：

> 我构造过2D image spatial-relation和point/box监督，重点是数据路由、输出格式与解析边界。它没有3D metric frame、entity graph或semantic map，所以我不会把这段经历说成3D grounding；如果扩展，会先定义typed 3D entities、frame/pose、relation arity，再做candidate oracle和raw query评估。

## 21. Robot Harness：PCD存在不等于Semantic Map

固定direct evidence显示：2D occupancy JSON/PNG编码0 occupied、127 unknown、255 free；`world.pcd`有54,856 points，字段为`x y z intensity timestamp ring`；bridge暴露occupancy/pointcloud path与URL。

PCD header没有semantic label、instance ID、language embedding、query score或relation edge。它支持“存在3D点云资产与接口路径”，不支持“运行OpenScene/OpenMask3D/ScanRefer/ReferIt3D/LERF/ConceptFusion”“可以按语言查地图”或“semantic grounding提升了planner/robot success”。

安全项目表述：

> Harness当前可见的是三态2D occupancy、非语义PCD schema和path/URL bridge。我会把它当作未来semantic map的geometry/interface入口，但在没有semantic field、query server、pose lineage、raw episode和ownership确认前，不声称已经实现语言可查询3D地图。

## 22. 五项目 Project Truth Boundary

| 项目 | 当前可讲 | 当前不能说 | 升级所需artifact |
| --- | --- | --- | --- |
| OPD | 2D Visual Genome relation、point/box监督、image-frame prompt | 3D relation frame、3D grounding、semantic map | typed 3D entities/relations、pose、head/checkpoint/raw eval |
| Robot Harness | 2D tri-state occupancy、non-semantic PCD、bridge/interface | language-queryable 3D map、instance grounding、robot benefit、ownership | semantic/instance fields、query server、pose lineage、episodes |
| OpenPiVLA | image/language/action policy，可讨论显式3D中间表示trade-off | 已集成3D grounding或其导致97.4 | module/config/checkpoint、matched ablation/rollouts |
| WAM | future-image/world-model可作为geometry/semantic consistency诊断候选 | LERF/OpenScene式field或semantic-map收益 | 3D head/loss/data、query artifacts、matched metric |
| UWM | image/action/video world model与LIBERO protocol | 3D semantic map、spatial listener、3D泛化 | model diff、3D data、checkpoint、raw query/rollout |

面试表述按`public upstream → local inventory → local-direct file → same-source inference → missing evidence → candidate ownership`分层。public mechanism说明“我理解什么”，local direct artifact才说明“项目里确实有什么”，两者都不能单独证明“我实现并验证”。

## 23. 两分钟结构化回答

> 我会先定义3D grounding的输出原子。ScanRefer是raw scene中先做3D proposal，再用语言给proposal排序并评估box IoU；ReferIt3D假设对象已分割，只在candidate中做top-1，所以二者的proposal上界和metric不同。OpenScene把2D语言对齐feature融合或蒸馏到3D points，适合point semantics，但两个同类对象仍缺instance identity。OpenMask3D先生成class-agnostic masks，选择可见视图、用SAM crop和多尺度CLIP得到per-mask embedding，所以mask proposal、pose和view aggregation是硬门。LERF是per-scene、multi-scale连续language field；ConceptFusion则在RGB-D、intrinsics和pose约束下增量融合queryable point map。对spatial relation，我会记录target、anchor、arity、observer/world/object frame、axis和metric threshold；between是三元关系，left/right会随observer旋转。开放词表score还必须冻结encoder、prompt、negative、L2 normalization、temperature与threshold，cosine不是校准概率。评估按proposal recall、Acc@3D-IoU、listener top-1、semantic mIoU、instance AP和field/map localization分层。最后这些都只输出semantic target，还要过reachability、IK、collision与controller。本地OPD只支持2D image relation，Harness只有非语义PCD/occupancy接口，因此不能讲成我已经实现3D semantic grounding。

## 24. 高频追问

1. ScanRefer与ReferIt3D的candidate assumption有什么根本差异？
2. 为什么proposal recall是end-to-end grounding硬上界？
3. `ref_acc`与`Acc@IoU 0.5`为什么可能不一致？
4. ReferIt3D为什么不是3D detector？
5. Sr3D与Nr3D分别适合诊断什么？
6. left/right到底绑定camera、observer、world还是object frame？
7. between为什么至少需要三个entity？
8. point semantic正确为什么仍可能选错“左边那把chair”？
9. OpenScene的2D fusion与3D distillation有何关系？
10. 无view coverage的3D points该怎么处理？
11. OpenMask3D的mask proposal、SAM crop和CLIP各负责什么？
12. 为什么多视图mean可能降低而不是提高score？
13. LERF为什么需要scale，为什么是per-scene field？
14. LERF fixed code的CLIP/DINO loss是什么？
15. ConceptFusion的map query为什么不能证明SLAM正确？
16. dot、cosine和relative softmax分别是什么量？
17. negative prompt为什么会改变“confidence”？
18. semantic mIoU、instance AP与referring top-1为什么不可互换？
19. 怎样拆分geometry、candidate、language和decision错误？
20. 本地五项目现在最多能支持哪一级3D claim？

## 25. 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “3D grounding就是CLIP投点云” | 忽略六类输出与candidate identity | 先定义box/ID/point/mask/field/map |
| “ReferIt3D能从raw scene检测物体” | 输入已是segmented objects | 称为candidate listener |
| “target漏检还能靠语言找回来” | 候选集合没有目标 | 报proposal oracle/target-present |
| “point mIoU高就能区分两个chair” | semantic不等于instance | 加mask/instance/graph identity |
| “left就是x更小” | x轴依赖reference frame | 冻结observer/world/object frame |
| “between是二元关系” | 缺第二个anchor | target + two anchors + tolerance |
| “cosine 0.8就是80%置信度” | cosine不是校准概率 | 报normalization、negative、temperature |
| “多视图平均一定更稳” | cancellation/低质view可降score | 保存per-view与zero-norm诊断 |
| “LERF直接输出object box” | 输出连续relevance | 另需peak/component/instance policy |
| “ConceptFusion能查询说明SLAM对” | feature可被写到错误位置 | 单独评估pose/depth/map geometry |
| “semantic target可以直接执行” | 缺reachability/IK/collision | 进入PER-015 gate |
| “Harness已有semantic 3D map” | PCD无semantic/query字段 | 只说非语义PCD与bridge |

## 26. 白板 Checklist 与练习标准

能够不看材料完成：

- 画出geometry→entity→language→decision→action gate主链；
- 列出box、candidate ID、point、mask、field、map六种输出；
- 写出typed grounding manifest中的candidate/frame/relation/prompt/metric字段；
- 推导candidate CE并解释proposal hard upper bound；
- 用unit-cube probe算出3D IoU 1/3；
- 比较ScanRefer与ReferIt3D的输入、输出和metric；
- 写出reference-frame left relation并解释yaw flip；
- 说明between的三元合同与closest的candidate-set合同；
- 区分dot、cosine和positive-vs-negative relative probability；
- 解释OpenScene的per-point semantics与instance缺口；
- 画出OpenMask3D mask→view→SAM crop→CLIP→query链；
- 解释LERF scale-conditioned field与fixed code loss；
- 解释ConceptFusion增量map update与pose drift；
- 按first-divergence顺序诊断十类失败；
- 说清OPD、Robot Harness与其余三项目的真实性边界；
- 完成两分钟回答并接住至少十个追问。

`drafted`不等于掌握。只有真实口述、追问、评分与纠错后才能改变题卡状态；PER-014题卡已生成并保持`unseen`，`coaching_state.md`也不应创建。

## 27. 结论与下一步

可靠的3D grounding答案不是背六个模型名字，而是建立一套类型系统：scene geometry是否可信、entity如何产生、target是否在candidate中、relation参考系与元数是否完整、language score是否冻结并校准、metric是否与输出原子匹配。ScanRefer、ReferIt3D、OpenScene、OpenMask3D、LERF与ConceptFusion分别占据这套类型系统中的不同位置，不能用一个“CLIP+点云”概括。

本地项目当前最强边界是：OPD有2D image spatial-relation与point/box监督；Robot Harness有2D tri-state occupancy、non-semantic PCD与bridge；OpenPiVLA/WAM/UWM只有image/language/action或video/world-model证据。没有local 3D semantic head/map/checkpoint、raw query、proposal oracle、same-protocol metric、robot episode或ownership闭环。

`VLA-PER-014` source、knowledge与card已在独立bounded slices同步；265张题卡继续全部`unseen`。下一bounded slice只冻结`VLA-PER-015` perception→action/reachability/uncertainty/failure-gate source；不生成其knowledge/card，不创建`coaching_state.md`，不改变任何mastery。

## References

1. [PER-014 3D Grounding / Spatial Relation / Open-vocabulary Source Freeze](../sources/vol_06_per014_3d_grounding_spatial_relation_open_vocabulary_source_freeze.html)：六篇完整primary PDF、六个official repo、36个文件SHA、九个probe与五项目audit。
2. Chen et al., [ScanRefer v3](https://arxiv.org/abs/1912.08830v3)；[official code@9d74830](https://github.com/daveredrum/ScanRefer/tree/9d7483053e8d29acfd4db4eb1bc28f1564f5dddb)。
3. Achlioptas et al., [ReferIt3D, ECCV 2020 official PDF](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460409.pdf)；[official code eccv@725a5d3](https://github.com/referit3d/referit3d/tree/725a5d31b8ff3647b6fb5342304093e9568d1341)。
4. Peng et al., [OpenScene v2](https://arxiv.org/abs/2211.15654v2)；[official code@0f369bc](https://github.com/pengsongyou/openscene/tree/0f369bc73d0724ae24b5e46bbada193f8ee9d193)。
5. Takmaz et al., [OpenMask3D v2](https://arxiv.org/abs/2306.13631v2)；[official code@3bc3fc5](https://github.com/OpenMask3D/openmask3d/tree/3bc3fc52693b25668d0e91d55a2ea714544a4749)。
6. Kerr et al., [LERF v1](https://arxiv.org/abs/2303.09553v1)；[official code@db08d57](https://github.com/kerrj/lerf/tree/db08d578038d884542688511bd9ad7b489a65673)。
7. Jatavallabhula et al., [ConceptFusion v3](https://arxiv.org/abs/2302.07241v3)；[official code@4457c1f](https://github.com/concept-fusion/concept-fusion/tree/4457c1f718a5612c2efc57b93a2dc152fed8a03d)。
8. [PER-007 Open-vocabulary Grounding](vol_06_per007_open_vocabulary_grounding_pipeline.html) 与 [PER-013 Point/Voxel/BEV/Occupancy](vol_06_per013_pointcloud_voxel_bev_occupancy.html)。
9. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
