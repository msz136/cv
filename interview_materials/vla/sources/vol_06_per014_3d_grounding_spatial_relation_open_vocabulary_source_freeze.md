# VOL 06 PER-014 Source Freeze：3D Grounding、Spatial Relation 与 Open-vocabulary 3D Scene

> 状态：`source_frozen / VLA-PER-014 / primary_official_checked / 2d_spatial_relation_not_3d_grounding / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结3D referring localization、候选对象识别、空间关系参考系与元数、逐点开放词表语义、开放词表3D实例mask、连续语言场、可查询语义3D地图及其score/prompt/metric/proposal边界；不生成knowledge/card，不重讲PER-007的2D open-vocabulary detector、不重讲PER-013的point/voxel/BEV/occupancy内部表示，也不进入PER-015的reachability、IK、collision或controller gate。

## 问题（Question）

面试官问“3D grounding怎样做，open-vocabulary 3D scene与spatial relation怎样落地”时，怎样区分从场景中生成3D候选框、在已分割对象中做指代分类、给每个3D点赋开放词表feature、查询3D实例mask、查询连续语言场和查询语义地图；怎样冻结参考系、prompt、normalization、negative、proposal与metric，使结果可复算；以及本地五项目到底具备了哪一层证据。

## 1. 结论先行

1. “3D grounding”不是单一输出。ScanRefer是`point cloud + utterance → proposal-language score → 3D box`；ReferIt3D是`segmented candidate objects + utterance → candidate top-1`；二者的候选假设、loss与metric不能互换。
2. OpenScene把2D开放词表feature融合/蒸馏到3D point feature，支持逐点语义查询；OpenMask3D先生成class-agnostic 3D instance masks，再用可见视图、SAM crop和CLIP形成per-mask embedding。逐点semantic field不自动得到instance identity，instance proposal错误也不会被文本相似度修复。
3. LERF学习per-scene、multi-scale连续language field；ConceptFusion把pixel-aligned multimodal feature在depth/intrinsics/pose约束下增量融合进3D point map。它们能返回relevance/query heatmap，但不自动返回稳定object ID、3D box、可达抓取姿态或controller target。
4. left/right/front/behind必须绑定observer/world/object frame；near可是一元相对阈值或二元metric relation，between至少是三元关系。没有frame、arity、anchor IDs、单位、阈值与时间戳的“空间关系”不可复算。
5. cosine相似度只有在encoder、checkpoint、prompt template、tokenization、normalization、negative prompts、temperature、candidate set和threshold固定时才是一个metric identity。dot product、cosine、softmax probability与relative relevance不可混称“置信度”。
6. proposal recall是grounding硬上界：target不在候选集合时，listener再强也无法选中。ScanRefer的`ref_acc`、3D box `Acc@0.25/0.5 IoU`、ReferIt3D top-1、semantic mIoU和instance AP不是同一指标。
7. 本地OPD只有Visual Genome来源的2D image spatial relationship与0–1000 box/point输出；Robot Harness只有2D tri-state occupancy、非语义PCD与bridge；OpenPiVLA/WAM/UWM只有image/language/action或video/world-model证据。当前没有local 3D semantic grounding head、map、checkpoint、raw query result、matched evaluation或候选人ownership闭环，因此保持`WARN`。

## 2. Primary Paper 冻结矩阵

| 来源 | 固定版本 / 完整性 | PDF SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| Chen et al., [ScanRefer](https://arxiv.org/abs/1912.08830v3) | arXiv `1912.08830v3`；35页；PDF完整解析；method视觉检查p7 | `3E53CD18B4266A16B679DFA7108FE1124F3DED6CA56D2BEE9845CEE8E5B5DB1D` | 3D proposals、language encoding、proposal-language matching、3D referring box与IoU评估 | 已分割对象listener、开放词表逐点/实例语义、本地结果 |
| Achlioptas et al., [ReferIt3D](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460409.pdf) | ECCV 2020 ECVA official PDF；19页；完整解析；method视觉检查p10 | `DA32FBD3EC426A097B99F3E1334A63B2312FC2EDC232697C3D50A4296BB9DBFA` | 已分割3D对象中的fine-grained identification、Nr3D/Sr3D、distractor与spatial language | box proposal/detection、任意open-vocabulary scene map |
| Peng et al., [OpenScene](https://arxiv.org/abs/2211.15654v2) | arXiv `2211.15654v2`；24页；完整解析；method视觉检查p4 | `31A4C88491FA9B38180E251B64422107C7D3028EF21B1C9E01581501B7868F0E` | 2D feature fusion、3D distillation、per-point open-vocabulary semantics | instance identity、3D referring box、robot execution |
| Takmaz et al., [OpenMask3D](https://arxiv.org/abs/2306.13631v2) | arXiv `2306.13631v2`；24页；完整解析；method视觉检查p4 | `DAD614EC86CB8F3778E61E30F0A0142085EDC27CCDD318BFDF75B201427FA42C` | class-agnostic 3D masks、top-view selection、SAM-assisted multi-scale CLIP mask feature、open-vocabulary instance query | proposal-free identity、pose/depth免疫、控制目标 |
| Kerr et al., [LERF](https://arxiv.org/abs/2303.09553v1) | arXiv `2303.09553v1`；15页；完整解析；method视觉检查p3 | `FDFFCCB93E88999FD3258990FF98E3DC902CC0B1B67A4A5CA046AB3DD78A84C9` | per-scene multi-scale language field、volume-rendered feature、query relevance | universal pretrained 3D map、object ID/box、控制闭环 |
| Jatavallabhula et al., [ConceptFusion](https://arxiv.org/abs/2302.07241v3) | arXiv `2302.07241v3`；19页；完整解析；method视觉检查p4 | `5E46DD735FC953C367800ED761AE57A46B158DBE166FAB33D5F4200CD0F7FF5A` | global/local feature、pixel alignment、metric 3D fusion与multimodal query | SLAM正确性、instance segmentation、robot success |

六份PDF都检查了`%PDF`、`%%EOF`并用`pypdf`读取全部页面；上表的method page另行渲染为PNG并确认公式、图与正文清晰。曾被误指向ReferIt3D的arXiv `2003.01199`实际是材料科学论文，未进入本冻结；ReferIt3D使用ECVA官方论文PDF。

## 3. Official Repository 冻结矩阵

| 官方仓库 | 固定revision / date / license | 直接读取文件与SHA-256 | 支持边界 |
| --- | --- | --- | --- |
| [daveredrum/ScanRefer](https://github.com/daveredrum/ScanRefer/tree/9d7483053e8d29acfd4db4eb1bc28f1564f5dddb) | `9d7483053e8d29acfd4db4eb1bc28f1564f5dddb`；2023-02-10；CC BY-NC-SA 3.0，含非商业限制 | `README 62EBAB6225F79ECD673F5B6F344358AFD1AF8BBA7A8DAC233E2407D896F1EDBD`；`LICENSE 65696FBDBF8B1EEE2F75A0D8491FB3E5B7CB012D1FB3EB91BFDAB4DF8C5C68CE`；`refnet.py 8E7A806537ECF9F19BCEE3421A1AA73BD9EBA0C97325634D5A35FBBB77E919BA`；`match_module.py 1CB9034CE6D13487ACB204E515CB1FC4C5150831F1A4D2A256BF568973AD60A5`；`loss_helper.py 87E7B83F744D8E7F9AADDCE7173B4750B319AF526F1358DC925FB4C8E953DAD4`；`eval_helper.py 7D054ED6EF853FCB282FF4F92D80C9842623D5E099DCD319003E01BFC269E11B` | VoteNet-style proposal、language/proposal fusion、`SoftmaxRankingLoss`、`ref_acc`与box IoU路径；不支持商业部署许可或本地复现 |
| [referit3d/referit3d:eccv](https://github.com/referit3d/referit3d/tree/725a5d31b8ff3647b6fb5342304093e9568d1341) | `725a5d31b8ff3647b6fb5342304093e9568d1341`；2021-06-29；MIT | `README DAB689176A19C530FBC3DCAB89A66B3DD0555A401BA6A2625B8E551FF73B51E8`；`LICENSE 4029A1BCEA794DE7C4C2D336C6749A877BC13AD17B819BE1601E5B94FFD2B46B`；`referit3d_net.py 16E95B3F79080C04524845B573420D132A0C1FA8D2DEC5CD5AB6F385FD286B45`；`listening_dataset.py E31C2037D6150BE4F1281C461EC67436D588FBAE99CFFC76EAF9B727FACA7D37`；`sr3d/reference.py 79E746E115490571D97BFD7BA55F825E539A3AFCC899C7CDBB4C5C02E4C0E111`；`train_referit3d.py 5F10D56D3C90D37F8AF0B6F29034126978946590AEBEC36B84219C21135210CF` | segmented object PointNet++ features、language feature、DGCNN graph、candidate logits与CE、Sr3D relation生成；不是detector |
| [pengsongyou/openscene](https://github.com/pengsongyou/openscene/tree/0f369bc73d0724ae24b5e46bbada193f8ee9d193) | `0f369bc73d0724ae24b5e46bbada193f8ee9d193`；2023-10-27；Apache-2.0 | `README 720F7674BB6653FFD9EC868E8E37C805F50EDAF7A8F39053687F2BC78B5A118D`；`LICENSE 1EB85FC97224598DAD1852B5D6483BBCF0AA8608790DCC657A5A2A761AE9C8C6`；`fusion_util.py 9657C8735769933EEE5673B46D959C85288562398C25C5B8FAFB1195D7480D0F`；`disnet.py 737A981E9A038CECC8C10C6DED8A60DC05904E91211CEFD23F1656CA99BCF2DE`；`distill.py 05935DE28576589AFD542EBFAC68CEF781FC7E63B34AB977D12C86C174457076`；`evaluate.py 2E2C5CD533F228882E74D4A3704219AF0B678AD7B4D2514BC10C59145DFF8A04` | 2D→3D feature fusion、sparse 3D distillation、cosine loss、text-feature scoring与semantic metrics |
| [OpenMask3D/openmask3d](https://github.com/OpenMask3D/openmask3d/tree/3bc3fc52693b25668d0e91d55a2ea714544a4749) | `3bc3fc52693b25668d0e91d55a2ea714544a4749`；2023-12-15；MIT | `README 7C1638C43D8760DFD94D5AD5EF306D9402233FF26720E77418B49C53417882AF`；`LICENSE DC14432D818F2017B2007AC617253716480EDE5C88468C7612E8BB8176FDBB6A`；`features_extractor.py D8DD7BC0F9AC44A81690A551DCE1D795C2B64999B0D7FB1FBA9BBC99FD37DEF2`；`compute_features_single_scene.py F396C7424518BFBC4FBFC6BB57B01504870F9B459BE71B916DFB9526D35B7ACB`；`openmask3d_inference.yaml EE26FC055C853331960678A9FF878FCAA09F96135674D25FEBF4512AAC85D2BF`；`evaluate_semantic_instance.py 7D9F68C4BAA5D8D0CE11A4258DE2C2FB460917EBAB2093C7ECCF0B5036E34BDF` | top-k view visibility、SAM mask crop、多尺度CLIP、view mean与instance eval；不消除mask proposal瓶颈 |
| [kerrj/lerf](https://github.com/kerrj/lerf/tree/db08d578038d884542688511bd9ad7b489a65673) | `db08d578038d884542688511bd9ad7b489a65673`；2024-03-13；MIT | `README 355B5E357B55CDF907AAC320511783AB372C69248AE0C40597921FB65F7517BF`；`LICENSE C9C4304E58E5BADCE9E50833B68648B67B80715B706407F07CEC868E7D5032BE`；`lerf.py 445D1FF1DD6D9BB46E23F7343CD1635A667D2511B00441A61C3C55C4BCCBEDA6`；`lerf_field.py 012F381AB5902DDB63C17CF9875C775C5681D0B66A3E6E7315981647A59CC73F`；`openclip_encoder.py 7C3066E36A42437C661FF962F8385A6159EE787342FA2A5B4FCC9F3DDB4C6222`；`pyramid_embedding_dataloader.py E6DC84FFF9D4D0A57EE5A2E4A3E4D8B9B55313D2FEBE09E362E1290C02879D05` | field、scale、fixed negatives、relative relevance；fixed code的CLIP Huber与DINO MSE须与论文表述分开 |
| [concept-fusion/concept-fusion](https://github.com/concept-fusion/concept-fusion/tree/4457c1f718a5612c2efc57b93a2dc152fed8a03d) | `4457c1f718a5612c2efc57b93a2dc152fed8a03d`；2023-05-23；MIT | `README 6A44E7BB89D24A8C97E1C52B5F579531A18FA594686E3CD431225671664A109F`；`LICENSE 28B3C2B50C1AFE54E5080B599610E3F780D27791B0E8820C74CF19F444349184`；`dino_feature_extractor.py 9CB2267CC9AD90D251DEBF1F777697CBA5B02DA9580677BF5E85B051620591E6`；`run_feature_fusion_and_save_map.py 4138B633F814BB2297CDBF9559E3B2D44732B716E4F673EDF9677DEC90F3D0E1`；`demo_text_query.py 90C67114756CCED18A92B9B45F12AEDB94D3881E33CE955A478D6973A97B3438`；`models_common.py 0F48145F482067DD41FA6E5C58A241C201DD56AF8BE5F801532FF890F9CC6314` | RGB-D/intrinsics/pose fusion、map embeddings、normalized text/map cosine与top-k/threshold query |

36个文件的SHA-256按固定commit工作树原始字节计算。仓库license不自动覆盖dataset、模型权重、ScanNet/CLIP/SAM依赖或商业使用；尤其ScanRefer仓库的CC BY-NC-SA 3.0非商业限制必须单独进入部署审计。

## 4. 相邻节点边界

```text
PER-007: 2D open-vocabulary grounding
        +
PER-013: point / voxel / BEV / occupancy representation
        |
        v
PER-014: 3D entity-language-spatial binding
        |
        v
PER-015: reachability / IK / collision / controller gate
```

| 节点 | 已负责 | PER-014只新增 |
| --- | --- | --- |
| PER-007 | 2D detector/segmenter、region-text score、prompt/threshold基础 | 把language绑定到3D candidate、point、mask、field或map |
| PER-013 | point/voxel/BEV/occupancy的坐标、量化、sampling、aggregation | 表示上的entity identity、language feature与spatial relation |
| PER-002/003/016 | 2D→3D lift、multi-view/time、SLAM/localization/drift | 只消费并核验pose/frame/time，不宣称修复几何或漂移 |
| PER-015 | reachability、IK、collision、controller | 本页输出至多是semantic target/proposal，不是可执行action |

已核验桥接入口：[PER-007 source](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)、[PER-013 source](vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html)与[PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html)。

## 5. Typed 3D Grounding Manifest

任何可比较的3D grounding/query artifact至少应冻结：

```json
{
  "sample_id": "scene/query pair",
  "scene_artifact": "point | voxel | mesh | radiance_field | point_map",
  "scene_revision": "sha256:...",
  "query_text": "the chair left of the table",
  "query_language": "en",
  "entity_candidates": {
    "source": "detector | segmented_objects | class_agnostic_masks | points | continuous_field",
    "revision": "sha256:...",
    "count": 0,
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

只有一句query与一张彩色heatmap，没有候选集合、frame、encoder/prompt、score与metric revision，无法判断模型在“理解关系”还是利用类别/位置偏差，也无法复算阈值或比较两个run。

## 6. Task / Output Taxonomy

| 任务 | 输入假设 | 输出原子 | 典型方法 | 主要瓶颈 | 合适指标 |
| --- | --- | --- | --- | --- | --- |
| 3D referring localization | raw/encoded scene + utterance，可含proposal generator | 3D box | ScanRefer | proposal recall、box geometry、language matching | Acc@3D IoU 0.25/0.5、proposal oracle |
| candidate-object identification | 已分割对象集合 + utterance | candidate ID/top-1 | ReferIt3D | segmentation、distractor、relation/reference frame | top-1 accuracy，按easy/hard/view-dependent分层 |
| open-vocabulary point semantics | 3D point + language-aligned feature | per-point label/score | OpenScene | view coverage、feature distillation、label prompt | semantic mIoU/mAcc/allAcc、seen/unseen split |
| open-vocabulary 3D instance | class-agnostic masks + views | mask ID/class/score | OpenMask3D | mask proposal、visibility、view/crop | instance AP/AP50/AP25、class split |
| continuous language field | posed images + per-scene field | 3D relevance/heatmap | LERF | per-scene optimization、scale、negative calibration | localization/relevancy protocol、qualitative query |
| queryable semantic map | RGB-D + intrinsics + pose + features | scored map points/regions | ConceptFusion | pose/depth drift、fusion/correspondence、threshold | retrieval/localization/map-quality protocol |

“open-vocabulary”描述query/label空间，不等于“无需冻结候选、prompt或阈值”，也不等于zero-shot机器人执行。

## 7. ScanRefer：Proposal-conditioned 3D Box Grounding

固定代码先生成3D proposals，再把每个proposal feature与language feature拼接，经过matching module输出`cluster_ref`。可抽象为：

\[
s_j=g_\theta\!\left([\mathbf p_j,\mathbf e_q]\right),
\qquad
\mathcal L_{\mathrm{ref}}
=-\sum_j y_j\log\operatorname{softmax}(s)_j.
\]

变量解释：\(\mathbf p_j\)是第\(j\)个3D proposal feature，\(\mathbf e_q\)是utterance embedding，\(s_j\)是候选匹配logit，\(y_j\)标记与GT box最匹配的proposal。直觉是“先找到可能的对象，再让语言从中排序”。实现映射：固定`match_module.py`对proposal与language做concat并屏蔽invalid objectness；`loss_helper.py`实际调用`SoftmaxRankingLoss`，所以该CE式是通用候选分类表达，不宣称与代码逐行等价。

必须区分三条链：proposal/objectness与box regression、reference ranking、language auxiliary classification。target proposal缺失时，ranking head无法恢复；因此至少报告proposal oracle recall与end-to-end grounding，而不是只报listener accuracy。

固定`eval_helper.py`中的`ref_acc`检查选中的proposal index是否是reference label；3D IoU阈值再检查预测box与GT box的几何重叠。两者可以出现“候选index选对但IoU 0.5失败”，不得互换。

## 8. ReferIt3D：Segmented Candidate Listener 与Spatial Distractor

ReferIt3D的输入已经是segmented 3D objects，不承担从raw scene生成3D boxes。固定模型对每个对象用共享object encoder提feature，对utterance编码，再由DGCNN建object graph，按配置在graph前/后融合language，最终为每个候选产生logit；训练脚本使用cross entropy：

\[
\mathcal L_{\mathrm{listener}}
=-\log
\frac{\exp s_{j^*}}
{\sum_{j\in\mathcal C}\exp s_j}.
\]

变量解释：\(\mathcal C\)是当前scan的候选对象集合，\(j^*\)是被指代对象。候选集合、padding/mask、distractor composition与object segmentation revision都属于metric identity。固定代码还可含object-class与language auxiliary CE；不能只看到总loss就说它训练了detector。

Sr3D通过模板化spatial relation生成指代表达，Nr3D来自自然语言。它们能用于诊断relation、distractor与view dependence，但“在候选中选对”不等于输出准确3D box，也不等于open-vocabulary instance segmentation。

## 9. OpenScene：Per-point Open-vocabulary Semantics

OpenScene先把2D视觉-语言feature按几何对应融合到3D，或用3D sparse network从点/voxel输入蒸馏该feature。固定代码的cosine distillation为：

\[
\mathcal L_{\mathrm{distill}}
=1-cos\!\left(\mathbf f_i^{2D},\mathbf f_i^{3D}\right).
\]

变量解释：\(\mathbf f_i^{2D}\)是投影到第\(i\)个3D点的2D teacher feature，\(\mathbf f_i^{3D}\)是3D network输出。直觉是把开放词表embedding geometry搬到3D。实现映射：固定`distill.py`在mask后的3D feature与fused feature间调用`CosineSimilarity`；`evaluate.py`再与text features相乘并计算mIoU/mAcc/allAcc。

per-point feature支持“哪些点像chair”的语义查询，但两个相邻chair可共享相同class feature；没有instance partition、tracking与relation graph时，不能可靠回答“左边那把chair是哪一个”。无2D feature覆盖的points也必须显式标unknown或另设policy，不能默认为background。

## 10. OpenMask3D：Class-agnostic Mask → Open-vocabulary Instance

OpenMask3D把两件事分开：先产生class-agnostic 3D masks，再为每个mask选择top-k可见视图、把投影点用于SAM-assisted crop、在多尺度crop上提CLIP feature并跨view聚合。固定`features_extractor.py`对image feature做L2 normalize，最后对selected views取mean。

对mask \(m\)与文本query \(q\)，基本score可写为：

\[
s_{m,q}=
\frac{\mathbf f_m^\top\mathbf t_q}
{\|\mathbf f_m\|_2\,\|\mathbf t_q\|_2}.
\]

变量解释：\(\mathbf f_m\)是per-mask multi-view embedding，\(\mathbf t_q\)是text embedding。实现必须冻结CLIP model、crop levels、SAM revision、top-k、visibility rule、view aggregation与prompt。若class-agnostic proposal把两个objects合并或漏掉target，text score无法凭空拆分/恢复实例。

简单平均还可能发生view cancellation：相反或低质embedding会使norm接近0。应保留per-view score、visibility、occlusion与aggregation诊断，而不是只存最终mean vector。

## 11. LERF：Continuous Multi-scale Language Field

LERF把不同物理scale的CLIP supervision嵌入per-scene radiance field。沿ray \(r\)对scale \(s\)的rendered feature可写为：

\[
\hat{\mathbf f}(r,s)
=\sum_i w_i(r)F_\theta(\mathbf x_i,s).
\]

变量解释：\(F_\theta(\mathbf x_i,s)\)是在3D sample与scale处的language feature，\(w_i\)由volume rendering权重给出。直觉是用相机射线监督连续3D field，并允许query在多尺度上找最相关区域。输出是relevance field，不天然是object ID或box。

固定`openclip_encoder.py`把positive query与negatives `object/things/stuff/texture`形成二类softmax并选最保守的negative comparison；`lerf.py`跨scale求高relevance。negative集合、temperature与scale search因此属于结果身份。

论文目标与当前fixed repo实现必须分层：当前代码对CLIP输出使用weight 0.1、delta 1.25的Huber loss，对DINO使用MSE。不能把论文中的feature alignment描述写成“代码逐行就是负余弦”。

## 12. ConceptFusion：Queryable Semantic 3D Map

ConceptFusion将global image feature与local region feature结合为pixel-aligned embedding，再利用depth、intrinsics与camera pose把像素提升到3D，并对已有map point做增量feature fusion。一个抽象更新为：

\[
\mathbf f_{k,t}
=\frac{\bar c_k\mathbf f_{k,t-1}+\alpha\mathbf f_{u,v,t}}
{\bar c_k+\alpha},
\qquad
\bar c_k\leftarrow\bar c_k+\alpha.
\]

变量解释：\(\mathbf f_{k,t}\)是map point \(k\)在时刻\(t\)的feature，\(\mathbf f_{u,v,t}\)是当前像素feature，\(\alpha\)是correspondence/confidence权重，\(\bar c_k\)是累计权重。该式表达论文的增量融合逻辑；固定example代码通过RGB-D、intrinsics、pose与GradSLAM/Pointclouds执行map fusion，具体邻域与权重以固定revision为准。

固定`demo_text_query.py`L2-normalize text与map embeddings后计算cosine，并支持top-k或min-max relative threshold可视化。min-max相对分数依赖当前scene与candidate range，不是跨scene calibrated probability。pose/depth漂移会把正确semantic feature写入错误3D位置；map query成功不能反证SLAM正确。

## 13. Spatial Relation：Reference Frame、Arity 与Threshold

以reference frame旋转\(R\)表示坐标轴，left relation可写为：

\[
r_{\mathrm{left}}(a,b;R)
=\mathbf 1\!\left[
\left(R^\top(\mathbf p_a-\mathbf p_b)\right)_x<0
\right].
\]

变量解释：\(a\)是target，\(b\)是anchor，\(R\)可来自observer/world/object frame。相同两点在yaw 0与yaw 180°参考系中会从left翻为right；只存predicate不存frame是不完整标注。

| Relation | 最小元数 | 必须冻结 | 常见坏例 |
| --- | ---: | --- | --- |
| left/right/front/behind | 2 | target、anchor、observer/world/object frame、axis | 用image left替代map-frame left |
| above/below | 2 | gravity/up axis、centroid/box/support definition | 相机roll后仍按pixel y判断 |
| near/far | 2 | metric、单位、threshold或rank policy | 每个scene动态min-max却称固定距离 |
| inside/on/supporting | 2 | geometry primitive、tolerance/contact policy | bbox overlap当真实support/contact |
| between | 3 | target与两个anchors、segment/corridor tolerance | 只给一个anchor仍叫between |
| closest/farthest | set-valued | candidate set、distance metric、tie rule | 改candidate set后仍比较accuracy |

空间语言benchmark可能含observer-dependent与view-independent表达；必须分层报告，不能把类别识别或绝对位置shortcut当relation reasoning。

## 14. Prompt、Score、Normalization 与Negative Calibration

开放词表query至少有四种不同量：raw dot、cosine、temperature-scaled logits、positive-vs-negative relative probability。对positive score \(s^+\)与negative \(s^-\)：

\[
p^+
=\frac{\exp(s^+/\tau)}
{\exp(s^+/\tau)+\exp(s^-/\tau)}.
\]

变量解释：\(\tau\)是temperature。即使raw positive cosine为0.55，只要negative为0.60，\(\tau=1\)时relative positive probability约0.4875，并不通过0.5。相似度高不等于绝对置信度高。

必须冻结：text/image encoder与checkpoint、tokenizer、prompt template/ensemble、大小写与复数、positive/negative集合、feature L2 normalization、temperature、candidate set、top-k、threshold、unknown policy、scene-level min-max以及score是否经过softmax。prompt change可改变ranking；这属于model-query interface，不应被包装为物理场景发生变化。

## 15. Metric 与Proposal Bottleneck

对axis-aligned 3D boxes，IoU为：

\[
\operatorname{IoU}_{3D}(B_p,B_g)
=\frac{\operatorname{Vol}(B_p\cap B_g)}
{\operatorname{Vol}(B_p\cup B_g)}.
\]

两个unit cube只在x方向错开0.5时，intersection volume为0.5、union为1.5，IoU为1/3：通过0.25却失败0.5。报告`Acc@0.25`时不能省略阈值或暗示`Acc@0.5`也成立。

| 层 | 应报告 | 不能替代 |
| --- | --- | --- |
| proposal | target-present recall、oracle IoU、proposal count | listener top-1 |
| referring box | Acc@IoU 0.25/0.5、unique/multiple split | `ref_acc`或semantic mIoU |
| candidate listener | top-1、distractor/easy-hard/view split | detector recall/box IoU |
| point semantics | per-class IoU、mIoU/mAcc/allAcc、seen/unseen | instance AP |
| instance semantics | AP/AP50/AP25、mask proposal oracle | point mIoU |
| field/map query | localization/retrieval protocol、threshold calibration、pose quality | robot success |

若GT target ID 7不在候选`[2,4,5]`中，则该sample的最大top-1为0。任何end-to-end提升都要拆成proposal、matching与geometry来源，否则无法定位收益。

## 16. Deterministic Probes

| Probe | 固定输入 | 结果 | 只证明 |
| --- | --- | --- | --- |
| 3D box IoU threshold | 两个unit cube，x错开0.5 | IoU=`1/3`；过0.25、不过0.5 | metric threshold改变结论 |
| dot vs cosine | query `[1,0]`；feature `[10,0]`,`[1,0]` | dot `[10,1]`；cosine `[1,1]` | normalization属于score identity |
| candidate bottleneck | GT 7；candidates `[2,4,5]` | 最大top-1=`0` | target absent无法由listener恢复 |
| relation frame | 同两点；yaw 0/180° | left翻为right | predicate必须绑定frame |
| semantic vs instance | 两个同class chair，仅一个在左 | class相同；instance ID可区分 | per-point semantic不自动给identity |
| multi-view cancellation | embeddings `[1,0]`,`[-1,0]`均值 | `[0,0]`，cosine undefined | view mean需norm/quality gate |
| view selection | top view `[1,0]`；加orthogonal view | top-1 score 1；两视图均值cosine `0.70710678` | top-k/aggregation改变score |
| negative calibration | positive .55；negative .60；temperature 1 | \(p^+=0.4875026\) | raw positive score不是relative pass |
| synthetic prompt identity | q1 scores `[.8,.6]`；q2 `[.6,.8]` | q1选1；q2选2 | embedding identity可改ranking；不声称真实CLIP必然如此 |

所有probe是机制级sanity check，不是论文benchmark复现，也不证明任一方法在本地机器人任务更好。

## 17. 本地五项目 Audit

五份canonical Claim–Evidence Inventory固定为：

| Inventory | Canonical SHA-256 | 当前安全结论 |
| --- | --- | --- |
| [OPD](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | 有2D region/point/box与image relation数据构造，不支持3D grounding |
| [OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | image/language/action policy evidence，不含local 3D semantic head/map |
| [Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | direct repo有2D occupancy/PCD/bridge exception，但没有semantic query字段 |
| [WAM](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | camera/video/world-model evidence，不自动含3D language field |
| [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | image/action/video与LIBERO evidence，不含3D semantic map/query eval |

Inventory是已归档claim的证据，不是“历史与远端所有文件绝对不存在”的证明；因此还对OPD与Robot Harness做了direct exception检查。

## 18. OPD Direct Exception：2D Image Relation 不是3D Grounding

`C:\Users\mousongzhe\muxi@756e27e16adcfb3ccbfe98c2920dda42095b127f`直接核验：

| 文件 | SHA-256 | 直接支持 | 不支持 |
| --- | --- | --- | --- |
| `build_expert_mixes_seed0_v2.py` | `19D5EF9E25D8664EA983880B79373098A77D19D5DA11D5B2AD17BEE6195C2F2C` | `spatial_rel_expert`来自Visual Genome 2D relationship；prompt写明“spatial relationship ... in the image” | 3D reference frame、object graph、3D box/mask、language field |
| `point/point_data_only.py` | `F650CB1F1B4A37566E11FA30C47A855DD59B74052588799839DF28F71EEC5787` | 2D annotation points经x/y几何变成box；输出可为0–1000 `<box>/<point>`或true/false | z、metric unit、camera/map frame、3D instance identity |

因此安全表述是“构造过2D image spatial-relation与point/box supervision”；危险表述是“实现了3D spatial grounding/open-vocabulary scene”。要升级后者，至少需要3D scene/entity schema、frame/pose、语言query输出、checkpoint与raw metric bundle。

## 19. Robot Harness Direct Exception：Non-semantic PCD/Occupancy

固定Robot Harness direct evidence显示：2D occupancy JSON/PNG使用0/127/255 tri-state；PCD有54,856 points，字段为`x y z intensity timestamp ring`；bridge暴露occupancy/pointcloud path与URL。PCD header没有semantic label、instance ID、language embedding、query score或relation edge。

这支持“系统能引用地图与点云资产，并把路径/URL暴露给上层”；不支持“已运行OpenScene/OpenMask3D/ScanRefer/ReferIt3D/LERF/ConceptFusion”“地图可按语言查询”或“语义grounding提高了planner/robot success”。第三方目录中的感知/地图代码也不能自动归为候选人实现。

## 20. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 补强artifact |
| --- | --- | --- | --- |
| OPD | 2D Visual Genome relation、point/box监督与image-frame prompt | 3D relation frame、3D grounding或semantic map | typed 3D entities/relations、frame/pose、model head/checkpoint/raw eval |
| Robot Harness | 2D tri-state occupancy、non-semantic PCD schema、bridge/interface | language-queryable 3D map、instance grounding、robot收益或个人ownership | semantic/instance fields、query server、pose lineage、episodes、ownership ledger |
| OpenPiVLA | end-to-end image/language/action，可讨论显式3D intermediate的trade-off | 已集成3D grounding或其导致97.4 | module/config/checkpoint、same-protocol ablation与rollouts |
| WAM | future-image/world-model output可作为geometry/semantic consistency诊断候选 | LERF/OpenScene式field或semantic-map收益 | 3D head/loss/data、query artifacts、matched metric |
| UWM | image/action/video world model与LIBERO协议 | 3D semantic map、spatial listener或3D泛化结果 | exact model diff、3D data、checkpoint、raw query/rollout bundle |

面试回答应明确分层：`public method`、`local inventory`、`local-direct file`、`same-source inference`、`missing evidence`、`candidate ownership`。只有前两层时不能说“我实现并验证了该方法”。

## 21. Fail-closed Pipeline 伪代码

```python
def grounded_3d_query(scene, query, manifest):
    # 1. 拒绝缺少坐标、版本与时间身份的场景；semantic score不能修复错误几何。
    require(scene.frame, scene.axis_unit, scene.revision)
    require(manifest.pose_depth_intrinsics_revision)

    # 2. 固定query interface；encoder/prompt/negative/normalization改变就视为新协议。
    require(manifest.encoder, manifest.prompt_template)
    require(manifest.feature_normalization, manifest.score)
    require(manifest.temperature_threshold_topk)

    # 3. 按任务选择候选原子，不能把point、box、mask、field混成同一输出。
    candidates = build_candidates(scene, manifest.entity_candidates)
    if manifest.entity_candidates.target_present is False:
        return {"status": "proposal_miss", "score": None}

    # 4. 关系query必须有正确元数、anchor IDs与reference frame。
    validate_relation_arity(query.relation)
    require(query.relation.reference_frame)

    # 5. 计算冻结score并保留per-candidate/per-view raw evidence，避免只存heatmap。
    raw = score_candidates(candidates, query, manifest)
    audit_zero_norm_and_view_coverage(raw)

    # 6. 用与output type匹配的metric；top-1、IoU、mIoU、AP不可互换。
    result = apply_frozen_decision(raw, manifest.temperature_threshold_topk)
    result["metric_protocol"] = manifest.metric_protocol

    # 7. 到semantic target为止；交给PER-015再检查reachability/collision/controller。
    result["executable"] = False
    return result
```

该流程的核心不是多加一个CLIP相似度，而是在任何身份缺失时拒绝给出强结论，并让proposal miss、geometry/frame错、semantic mismatch、relation错与action gate失败可分别定位。

## 22. Source Gate 与下一切片

本轮已关闭：

- 六篇primary paper固定版本、完整PDF SHA与method-page视觉检查；
- 六个official repository固定commit/date/license，36个关键文件逐字节SHA；
- box localization、candidate listener、per-point semantics、instance mask、continuous field与semantic map的输入/输出合同分离；
- reference frame/arity、prompt/negative/normalization、proposal bottleneck与metric identity显式化；
- 九个deterministic probe固定输入与结果；
- 五份项目inventory、OPD direct exception与Robot Harness non-semantic PCD/occupancy边界完成。

仍为`WARN`：本地没有3D semantic grounding model/config/checkpoint、typed candidate/scene manifest、semantic/instance map、pose-aligned raw query、proposal oracle、same-protocol metrics、robot execution trace或候选人逐文件ownership确认；浏览器`file://`视觉QA仍受环境策略限制。

`VLA-PER-001..014` source/knowledge/card已在独立bounded slices同步；265张题卡全部`unseen`，不创建`coaching_state.md`，不改变mastery。下一bounded slice只冻结`VLA-PER-015` perception→action/reachability/uncertainty/failure-gate source，不生成knowledge/card。

## References

1. Chen et al., [ScanRefer: 3D Object Localization in RGB-D Scans using Natural Language, v3](https://arxiv.org/abs/1912.08830v3)；[official code@9d74830](https://github.com/daveredrum/ScanRefer/tree/9d7483053e8d29acfd4db4eb1bc28f1564f5dddb)。
2. Achlioptas et al., [ReferIt3D: Neural Listeners for Fine-Grained 3D Object Identification in Real-World Scenes, ECCV 2020](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123460409.pdf)；[official code eccv@725a5d3](https://github.com/referit3d/referit3d/tree/725a5d31b8ff3647b6fb5342304093e9568d1341)。
3. Peng et al., [OpenScene: 3D Scene Understanding with Open Vocabularies, v2](https://arxiv.org/abs/2211.15654v2)；[official code@0f369bc](https://github.com/pengsongyou/openscene/tree/0f369bc73d0724ae24b5e46bbada193f8ee9d193)。
4. Takmaz et al., [OpenMask3D: Open-Vocabulary 3D Instance Segmentation, v2](https://arxiv.org/abs/2306.13631v2)；[official code@3bc3fc5](https://github.com/OpenMask3D/openmask3d/tree/3bc3fc52693b25668d0e91d55a2ea714544a4749)。
5. Kerr et al., [LERF: Language Embedded Radiance Fields, v1](https://arxiv.org/abs/2303.09553v1)；[official code@db08d57](https://github.com/kerrj/lerf/tree/db08d578038d884542688511bd9ad7b489a65673)。
6. Jatavallabhula et al., [ConceptFusion: Open-set Multimodal 3D Mapping, v3](https://arxiv.org/abs/2302.07241v3)；[official code@4457c1f](https://github.com/concept-fusion/concept-fusion/tree/4457c1f718a5612c2efc57b93a2dc152fed8a03d)。
7. [PER-007 Open-vocabulary Grounding Pipeline](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)、[PER-013 Point/Voxel/BEV/Occupancy](vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html) 与 [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html)。
8. [OPD](../evidence/projects/opd_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) Claim–Evidence Inventories。
