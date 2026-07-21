# VOL 06 Perception / Grounding / Navigation：Point / Box / Mask / Keypoint / Affordance 表示选择（PER-008）

> 状态：`drafted / VLA-PER-008 / source_synced / card_synced / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[PER-008 Source Freeze](../sources/vol_06_per008_representation_choice_source_freeze.html)。  
> 前置知识：[PER-001 Point / Box / Text Contract](vol_06_per001_grounding_coordinate.html)、[PER-006 Image Preprocess / Token / Camera](vol_06_per006_image_preprocess_token_camera_contract.html)、[PER-007 Open-vocabulary Grounding](vol_06_per007_open_vocabulary_grounding_pipeline.html)。  
> 原子题卡：[VLA-PER-008](../questions/vol_06_per008.html)（`unseen`）。

## 问题（Question）

机器人收到“把杯子挂到架子上”“在空位放下物体”或“拉开抽屉”后，perception 应输出 point、box、mask、semantic keypoint 还是 action-conditioned affordance？更密集的输出是否一定更好？本地数据里有一个叫`affordance`的字段，是否就能说系统学习了可执行动作？

本页给出的答案不是五类表示的排行榜，而是一条可审计选择链：

```text
task + downstream consumer + image/camera/time contract
  -> consumer真正读取的最小字段
  -> minimum-sufficient representation
  -> uncertainty / multimodality / validity
  -> 有损转换及其provenance
  -> parser / metric / controller gate
  -> evidence-bounded project claim
```

## 知识地图位置与边界

```text
PER-001 point/box/text schema + coordinate/parser basics
  -> PER-006 image/camera/time lineage
  -> PER-007 text-conditioned region proposal
  -> PER-008 representation choice and conversion boundary
  -> PER-009 matching/loss
  -> PER-010 metric/protocol
  -> PER-012 concrete segmentation/keypoint/affordance models
  -> PER-015 perception-to-action gate

PER-002 owns 2D-to-3D lift and frame transforms.
```

PER-008只回答“下游需要什么信息、应选择什么输出合同、转换会丢什么”。它不重讲投影、训练loss、最终metric、具体模型recipe或controller feasibility。这样可以避免把“选了affordance表示”偷换成“已经闭环执行成功”。

## 1. 30秒直觉：表示不是越密越好

最短可用回答是：

> 我先看downstream consumer需要哪些字段。只要ROI或粗tracking，box通常够；要轮廓、占用或精细重叠才需要mask；只问一个或多个候选位置可以用point set；类别级几何角色需要带semantic ID与frame的keypoints；只有当primitive、tool、state、方向和success semantics进入合同后，才能叫action-conditioned affordance。密度不等于语义，也不等于可执行性。

五个容易混淆的反例：

1. 一个pixel坐标不知道自己是`handle`还是`rim`；
2. 一个box不知道杯柄轮廓或中间空洞；
3. 一个SAM mask不知道“这是要拉的把手”；
4. 一个名为`affordance_pointing`的point target不包含push/pull方向；
5. 一个actionability score也不自动等于特定机器人上的已校准成功率。

## 2. 先从downstream consumer反推字段

### 2.1 “最小充分”不是“最简单”

表示应当同时满足两个条件：

- **充分**：consumer所需的extent、contour、semantic role、frame或action condition都存在；
- **最小**：不为未被消费的dense字段支付标注、存储、推理、同步与评估成本。

一个可审计的工程目标可写为：

\[
r^*=\arg\min_{r\in\mathcal R}
\left(C_{\mathrm{label}}(r)+C_{\mathrm{infer}}(r)
+\lambda\,\mathbb E[L_{\mathrm{down}}\mid r]
+\mu\,C_{\mathrm{convert}}(r)+\nu\,C_{\mathrm{stale}}(r)\right).
\]

变量解释：\(r\)是候选representation；\(C_{\mathrm{label}}\)和\(C_{\mathrm{infer}}\)分别是标注与推理成本；\(L_{\mathrm{down}}\)是consumer上的任务损失；\(C_{\mathrm{convert}}\)记录格式/坐标转换及信息损失；\(C_{\mathrm{stale}}\)表示输出随时间陈旧的风险；\(\lambda,\mu,\nu\)是部署权重。

直觉：更复杂的表示只有在降低downstream failure足以覆盖额外成本时才值得选。实现映射：这些量来自labeling ledger、latency/memory log、conversion manifest、timestamp trace与matched downstream ablation。证据边界：这是从冻结source合同推导出的decision rubric，不是RoboPoint、SAM、kPAM或Where2Act共同提出的训练目标。

### 2.2 Required-fields矩阵

| Downstream consumer | 真正读取的字段 | 起始表示 | 为什么不是别的表示 |
| --- | --- | --- | --- |
| proposal / ROI crop / 粗tracking | instance extent、phrase/ID、score | box | point无extent；mask可能是无必要的dense成本 |
| look-at / free-space / 粗contact候选 | 一个或多个位置、valid radius、score | point set | box/mask提供的形状若不被使用就是冗余 |
| contour / overlap / occupancy预处理 | pixel membership、instance、quality | mask | box把背景、空洞与细长结构混入 |
| 类别级几何约束 | semantic role、visibility、2D/3D frame、covariance | semantic keypoints | 裸point没有role；mask未必提供可迁移的几何锚点 |
| primitive-conditioned interaction | support geometry、primitive、tool、state、direction、horizon、success semantics | affordance field/points | 任何纯几何表示都缺action condition |

这张表只给default starting contract。若ROI consumer后来需要碰撞边界，box可能升级为mask；若mask最后只被压成中心点，反而应审计是否能直接训练point output。

## 3. 五类表示的严格合同

### 3.1 Point set：回答“哪里”，不回答“是什么角色”

一个最小point set不应只存坐标，而应至少冻结：

```text
points / coordinate_space / count policy / ordering
point_scores + score_semantics / valid_radius
multimodal_group / empty-set policy / image-camera-time lineage
```

它适合低带宽位置建议，也天然允许输出多个mode。RoboPoint的公开README以多个`[(x,y),...]` normalized image points作为输出合同；本地OPD主要使用`0..1000` tagged point。两者的坐标space、parser与metric不同，不能只因都长得像二元组就混用。

point的主要信息缺口是extent、surface normal、semantic role、action precondition与reachability。单点“落在目标上”也不等于末端执行器能以安全姿态到达。

### 3.2 Box：回答“粗范围”，不回答“精细形状”

box需要声明`xyxy`或`cxcywh`、pixel或normalized、corner inclusive/exclusive、clip规则、instance/phrase binding、score与NMS revision。它适合proposal、crop与association，因为四个数就能表示粗范围。

代价是矩形会包含背景、孔洞与其他实例；对细长、旋转或部分遮挡物体尤其不紧致。box score、mask quality与affordance success是三种不同语义，不能放在同一阈值表里直接比较。

### 3.3 Mask：回答“哪些像素属于region”，不回答“应该怎么做”

binary或soft mask需要保存shape、encoding、threshold、component/instance、quality semantics、source prompt和transform lineage。SAM的`SamPredictor`公开合同支持point/box/mask prompt，并返回原图尺寸的一个或多个masks、predicted mask quality与低分辨率logits。

这证明promptable segmentation I/O，不证明mask自带language label、instance permanence、depth、contact normal或robot actionability。mask适合轮廓、遮挡、surface/occupancy预处理，但会引入dense storage、边界噪声、component ambiguity与temporal flicker。

### 3.4 Semantic keypoints：回答“哪个几何角色在哪里”

一个可用keypoint set可写为：

\[
K=\{(s_i,p_i,v_i,\Sigma_i)\}_{i=1}^{N}.
\]

变量解释：\(s_i\)是semantic ID，如`handle_center`或`rim_left`；\(p_i\)是2D或3D坐标；\(v_i\)是visibility/validity；\(\Sigma_i\)是位置不确定性；\(N\)是定义或检测到的anchor数。

直觉：坐标相同而\(s_i\)不同，controller中的几何constraint就可能完全不同。实现映射：schema要把`semantic_ids, coords, visibility, covariance, instance_id, category, frame`绑定在同一record。证据边界：kPAM支持semantic 3D keypoints进入几何cost/constraint与planning factorization；本地OPD没有由所读文件证明这条pipeline。

### 3.5 Action-conditioned affordance：回答“在什么条件下哪里可如何交互”

affordance不应只写成一个heatmap名称。抽象合同可记为：

\[
A(p\mid \pi,g,s,d,h).
\]

变量解释：\(p\)是候选位置或support geometry；\(\pi\)是action primitive，如push/pull；\(g\)是tool或gripper；\(s\)是object/environment state；\(d\)是方向或orientation；\(h\)是时间horizon；\(A\)的数值必须另行声明是ranking score、likelihood还是校准后的成功概率。

直觉：同一pixel对push和pull、不同gripper、门开与关、不同碰撞上下文可以有不同可行性。实现映射：manifest必须显式存`primitive, tool_or_gripper, state_precondition, direction_or_orientation, horizon, success_score_semantics`。Where2Act支持按action primitive预测per-point actionability、orientation proposal与critic success likelihood；它不支持把分数迁移为任意机器人上的通用成功率。

## 4. Point、Keypoint与Affordance为何不能按坐标形式合并

### 4.1 三层语义阶梯

```text
point:       xy/xyz + coordinate contract
keypoint:    point + semantic ID + visibility + frame/covariance
affordance:  support geometry + primitive/tool/state/direction/horizon + score semantics
```

这不是“point < keypoint < affordance”的通用性能排名，而是字段合同逐步增加。一个affordance可以最终以top-k points输出，但每个point仍必须携带action condition；一个semantic keypoint也可以是2D point，但semantic ID不能丢。

### 4.2 两个确定性反例

| 相同坐标 | Record A | Record B | 裸坐标丢掉什么 |
| --- | --- | --- | --- |
| `(200,300)` | `mug_handle` | `mug_rim` | semantic role与不同几何constraint |
| `(500,500)` | `push / +x` | `pull / -x` | primitive、direction与不同执行假设 |

因此“模型输出了point”只能证明位置字段；是否是keypoint或affordance，必须看坐标外的typed fields、监督目标、head、parser与下游消费方式。

## 5. Box与Mask的信息量、成本与不可逆性

### 5.1 Mask到box可计算但有损

对非空binary mask \(M\)，half-open axis-aligned box为：

\[
B(M)=\left(
\min_{M(x,y)=1}x,\min_{M(x,y)=1}y,
\max_{M(x,y)=1}x+1,\max_{M(x,y)=1}y+1
\right).
\]

变量解释：\(M(x,y)=1\)表示foreground membership；\(B(M)\)只保存四个坐标极值。直觉：contour、hole、component与area都会丢失。实现映射：可用`where(mask)`求min/max并在conversion manifest中记录`mask_to_xyxy_half_open`；这不是可逆codec。

确定性5×5 probe：3×3实心mask和只保留四角的mask都得到`(1,1,4,4)`，面积却分别为9和4。由此可知`box -> filled rectangle`是新增假设，不是恢复原mask。

### 5.2 什么时候box比mask更好

如果consumer只做crop、proposal ranking或粗association，mask的额外像素可能没有收益，反而增加label、memory、latency与temporal instability。只有consumer真的读取contour、overlap、thin structure、hole或occupancy时，mask的额外信息才成为必要字段。

### 5.3 什么时候两者都不够

box和mask都主要描述视觉region。它们没有自动提供3D frame、surface normal、force closure、action direction或reachability。因此“用了mask就更适合抓取”仍需depth/geometry与PER-015 action gate证据。

## 6. 转换图：可计算不代表等价

| 转换 | 操作 | 信息损失或新增假设 | 必需provenance |
| --- | --- | --- | --- |
| mask → box | foreground极值 | contour、hole、component、area | mask hash、threshold、corner convention |
| keypoints → box | visible points极值 | object extent未知，可能只包局部anchors | semantic IDs、visibility filter |
| affordance field → top-k points | score排序与空间抑制 | dense landscape、校准与被截mode | primitive、score semantics、k、spacing |
| box → mask | segmentation model或矩形填充 | 新prediction或强矩形假设 | model/prompt revision或fill policy |
| point → keypoint | 不能只靠坐标 | 必须新增semantic identity | ontology/relabel source |
| point → affordance | 不能只靠坐标 | 必须新增action conditions | primitive/tool/state/direction source |

每次转换都应生成新artifact stage，而不是覆盖原输出。最小记录包括input hash、converter revision、parameters、output hash、declared loss与validity。

## 7. Uncertainty、Multimodality与Validity

### 7.1 表示不同，不确定性也不同

| 表示 | 至少保留的不确定性 | 常见错误压缩 |
| --- | --- | --- |
| point set | per-point score、mode group、valid radius、empty set | 只取均值点，落到所有mode之外 |
| box | proposal score、coordinate uncertainty、duplicate grouping | NMS后只留一个框且不保留pre-NMS trace |
| mask | multimask candidates、quality semantics、soft logits、components | 强制二值化并删掉替代mask |
| keypoints | visibility、covariance、missing/occluded state | 把遮挡点填0并当成真实坐标 |
| affordance | score semantics、orientation proposals、state/primitive validity | 把ranking score口述成成功概率 |

RoboPoint的多个points与SAM的multimask都提醒：歧义是输出合同的一部分。强行压成单点或单mask会把模型不确定性变成下游的隐式错误。

### 7.2 Fail-closed validity

一个representation record至少区分：

- `valid=true`：schema、坐标、lineage与必需语义字段完整；
- `valid=false`：记录明确`invalid_reason`，禁止controller静默消费；
- empty but valid：模型明确预测“无候选”，不等于parser失败；
- missing/unverified：artifact或字段没有被归档，不能填默认值冒充证据。

## 8. Typed Representation Manifest

所有类型先继承PER-006的image/camera/time lineage：

```json
{
  "sample_id": "...",
  "image_id": "...",
  "camera_id": "...",
  "frame_id": "...",
  "timestamp": 0.0,
  "representation_type": "point_set | box | mask | semantic_keypoints | affordance",
  "coordinate_space": "original_pixel | processed_pixel | normalized_0_1 | normalized_0_1000 | world",
  "transform_revision": "...",
  "prompt_hash": "...",
  "model_processor_code_revision": "...",
  "score": 0.0,
  "score_semantics": "...",
  "uncertainty": {},
  "valid": true,
  "invalid_reason": null,
  "payload": {}
}
```

类型特有payload：

| 类型 | 最小字段 |
| --- | --- |
| point set | `points, point_scores, valid_radius, ordering, multimodal_group` |
| box | `format, coords, phrase, instance_id, clipped, nms_revision` |
| mask | `shape, encoding, threshold, component_ids, quality_semantics, source_prompt` |
| semantic keypoints | `semantic_ids, coords, visibility, covariance, instance_id, category, frame` |
| affordance | `support_geometry, primitive, tool_or_gripper, state_precondition, direction_or_orientation, horizon, success_score_semantics` |

只保存`payload`会让相同的两个数字在pixel、normalized、semantic anchor与action point之间静默漂移。只保存一个`score`又会混淆objectness、mask quality、point hit与action success。

## 9. 可审计选择算法

```python
def choose_representation(task, consumer, evidence):
    # 1. Freeze fields that the downstream consumer actually reads.
    need = consumer.required_fields(task)

    # 2. Select the minimum representation whose native contract is sufficient.
    if need.action_primitive or need.contact_orientation:
        rep = "affordance"
    elif need.semantic_anchor or need.geometric_constraint:
        rep = "semantic_keypoints"
    elif need.contour or need.pixel_occupancy:
        rep = "mask"
    elif need.extent or need.roi:
        rep = "box"
    else:
        rep = "point_set"

    # 3. Fail closed if local schema/parser/evaluator cannot consume it.
    required = ["schema", "parser", "lineage", "validity"]
    if not all(evidence.has(rep, item) for item in required):
        return invalid("representation_not_supported")

    # 4. Preserve raw multimodal output and every conversion stage.
    record = build_typed_manifest(rep, task, consumer, evidence)
    record["conversions"] = freeze_conversion_chain(evidence.conversions)

    # 5. Action consumption remains gated by PER-015 evidence.
    record["controller_ready"] = False
    return record
```

这段伪代码是工程gate，不是某个official API。它要求先冻结consumer fields，再检查本地schema/parser/lineage，而不是看到一个模型能输出mask就默认升级整个系统。`controller_ready=false`也提醒表示选择与可执行性是两个节点。

## 10. RoboPoint、SAM、kPAM与Where2Act接口对照

| 方法 | 输入条件 | 原生输出合同 | 能支持的口述 | 不能偷换成 |
| --- | --- | --- | --- | --- |
| Grounding DINO（PER-007） | image + text tokens | query-token scores + boxes + phrase | open-vocabulary proposal/ROI | mask、semantic keypoint或action feasibility |
| RoboPoint | image + language instruction | multiple normalized image points | spatial relation/free-space/action-point suggestion | 3D semantic keypoints或已执行contact |
| SAM | image + point/box/mask prompt | one/multiple masks + quality + low-res logits | promptable region/contour extraction | language semantics或robot affordance |
| kPAM | segmented object + semantic keypoint detector | semantic 3D keypoints进入geometric costs/constraints | category-level manipulation geometry | 任意2D point list已具备planning合同 |
| Where2Act | articulated geometry + action primitive | per-point actionability + orientation proposals + critic score | primitive-conditioned interaction proposal | 任意robot/tool上的校准成功率 |

这五个接口的input、supervision、output、metric与下游都不同，不能引用各论文数字做横向“表示冠军”比较。正确比较应在同一任务、数据、compute、consumer与metric下做matched ablation。

## 11. 本地OPD：Affordance-labelled Point的真实性边界

冻结本地`muxi` HEAD为`756e27e16adcfb3ccbfe98c2920dda42095b127f`。五个直接读取文件支持的链路是：

```text
ShareRobot affordance {x,y} / trajectory or point records
  -> normalize or scale to point coordinates
  -> "point to actionable location" prompt
  -> tagged point/box/text SFT target
  -> autoregressive generation
  -> point/box/text parser and static scorer
```

具体证据与边界：

1. `opd_project/scripts/build_prompt_pool.py`把`affordance.x/y`缩放到`0..1000`，输出单个`gt_points`并标为`affordance_pointing`；没有primitive、direction、gripper、state或success head。
2. `point/point_data_only.py`最终仍生成point answer；prompt里的“actionable”不会自动改变representation type。
3. `point/build_expert_mixes_seed0.py`提取`<box>`与`<point>`；`point/eval_qwen_vl_raw_holdout.py`按point/box/text做format与static geometry/text scoring。
4. 选定五个文件中没有直接证明`keypoint`、SAM、mask encoding、dense actionability head或controller episode；静态未发现也不代表仓库其他位置或历史上绝对不存在。

面试安全表述：

> 我的本地证据支持affordance-labelled point supervision，以及point/box/text生成与静态评估。这里“affordance”描述数据问题，“point”描述输出表示；当前证据不支持dense affordance map、semantic-keypoint/SAM pipeline、action-conditioned success calibration或机器人执行闭环。

本地关键证据hash：

| 文件 | SHA-256 |
| --- | --- |
| `build_expert_mixes_seed0.py` | `60DFDF46FDAC8EB9DBBE38A13298D6D71819EB7AD13F6B0D00A86B87032EABD0` |
| `eval_qwen_vl_raw_holdout.py` | `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B` |
| `build_clean_grounding_pool.py` | `A7A5906E11EA687C6FD0DEC40F3D30922A91B538EB98C740230227F9FF943087` |
| `opd_project/scripts/build_prompt_pool.py` | `293C776BA03E28DAC0029F985EEFFDC20036D24A289F3D74B1F761D1C7629315` |
| `point/point_data_only.py` | `F650CB1F1B4A37566E11FA30C47A855DD59B74052588799839DF28F71EEC5787` |

## 12. Matched Representation Evaluation设计

PER-008只规定比较设计，metric公式和threshold细节留给PER-010。一个可信A/B至少固定：

1. 相同task/split/seed与原始输入；
2. 相同image transform、camera/time lineage；
3. 尽可能匹配backbone、training budget与data volume；
4. 每种表示使用正确的native parser，而不是把所有输出先转成box；
5. 同一downstream consumer与controller gate；
6. 同时报告表示自身质量、conversion failure、latency/memory与downstream outcome；
7. 保存per-sample raw outputs、invalid/empty/multimodal cases；
8. 禁止用不同论文的headline metric直接推断表示优劣。

建议实验表：

| Factor | 固定项 | 变化项 | 观察项 |
| --- | --- | --- | --- |
| representation native | task/data/backbone budget | point/box/mask/keypoint/affordance head | native validity、latency、storage |
| conversion | 同一raw output | direct native vs converted | information loss、invalid rate |
| consumer | 同一prediction bundle | ROI/contact/geometry consumer | downstream failure taxonomy |
| uncertainty | 同一candidate set | top-1 vs multimodal retention | mode miss、calibration、safety reject |

如果同时换dataset、model、metric与controller，就无法把结果归因给representation。

## 13. Failure Taxonomy与诊断顺序

| 失败层 | 症状 | 常见根因 | 首个检查 |
| --- | --- | --- | --- |
| task sufficiency | point无法支持contour，box无法支持contact | consumer字段没冻结 | required-fields table |
| semantic collapse | 把裸point叫keypoint/affordance | semantic/action fields缺失 | typed payload |
| geometry | 2D/3D、pixel/normalized、raw/processed混用 | coordinate/frame lineage缺失 | transform + round-trip |
| ambiguity | 单点或单mask压掉多解 | top-1过早 | raw candidate/multimask trace |
| conversion | box填充成mask后当真值 | 把prediction当inverse | conversion provenance |
| temporal | mask/keypoint已陈旧仍执行 | timestamp/instance association缺失 | observation age |
| score | quality/objectness/action success混比 | score semantics缺失 | score definition + calibration split |
| parser | empty prediction被当成no-object | format failure与valid empty混淆 | raw text/output + parser status |
| project claim | affordance-named数据被说成机器人能力 | supervision、head、controller证据混淆 | claim-evidence chain |

推荐诊断顺序：consumer fields → native schema → image/coordinate/time lineage → raw uncertainty → conversion trace → parser golden test → matched metric → reachability/controller → robot episode。先从接口查起，比直接换模型更可解释。

## 14. 面试回答模板、追问与危险答案

### 14.1 两分钟结构化回答

1. 先说“按downstream minimum-sufficient fields选，不按密度排”；
2. 用一句话区分point、box、mask、keypoint、affordance；
3. 给出`mask -> box`有损和`point != keypoint/affordance`两个反例；
4. 提到uncertainty、multimodality与typed manifest；
5. 用RoboPoint/SAM/kPAM/Where2Act做接口对照；
6. 落到OPD：affordance-labelled point supervision，不夸成dense/controller能力；
7. 说明最终要做matched downstream evaluation与PER-015 gate。

### 14.2 高频追问

| 追问 | 回答抓手 |
| --- | --- |
| 为什么不用mask统一所有任务？ | extra density不等于consumer收益；成本、temporal flicker与语义仍缺 |
| 一个point什么时候能叫keypoint？ | 有稳定semantic ID、instance/category、visibility与2D/3D frame |
| 一个point什么时候能叫affordance point？ | 绑定primitive/tool/state/direction/horizon与score semantics |
| SAM的quality能当抓取成功率吗？ | 不能；它是mask输出侧quality，不是controller success calibration |
| box转mask是否可逆？ | 不可逆；分割模型会产生新prediction，矩形填充是新假设 |
| 多模态候选怎么处理？ | 保留candidate groups/scores/validity，在consumer端显式选择或拒绝 |
| 如何证明某表示更好？ | matched task/data/compute/consumer/metric，报告native与downstream结果 |

### 14.3 危险答案

- “mask信息最多，所以任何任务都最好”；
- “keypoint就是point的别名”；
- “affordance就是可交互点坐标”；
- “SAM输出mask，所以它理解了物体语义”；
- “Where2Act score就是任意机器人成功率”；
- “box内部填满就恢复了mask”；
- “OPD训练了affordance，所以已经能做机器人action”；
- “不同论文各自metric更高就能说明表示更优”。

## 15. 项目补证清单

若要把当前`WARN`升级，优先归档：

1. 真实local mask、semantic-keypoint或dense affordance schema/head/parser（若存在）；
2. primitive、tool/gripper、state、direction、horizon与score-calibration字段；
3. raw multimodal outputs与conversion manifests；
4. matched representation ablation，包含latency/memory/invalid与downstream outcome；
5. perception-to-action reachability、controller reject与episode bundle；
6. Where2Act相关复用若发生时的实际license审查，因为冻结commit只有README中的MIT声明而没有LICENSE文件。

这些补证没有归档前，最强可信结论仍是“表示合同和本地point supervision已审计”，不是“系统已选择并验证最优affordance表示”。

## 16. 结论与下一步

PER-008的核心是把representation choice变成接口工程：point回答位置，box回答粗范围，mask回答pixel membership，semantic keypoint增加几何角色，action-conditioned affordance再增加primitive/tool/state/direction/horizon与score semantics。`mask -> box`可算但有损，`box -> mask`不可逆；同样的point坐标也不能恢复semantic或action fields。

当前source、knowledge与card已同步；本地OPD的证据边界已明确为affordance-labelled point supervision和point/box/text静态pipeline。由于缺少local mask/keypoint/dense-affordance head、matched representation ablation、success calibration与controller/robot bundle，本节点保持`WARN`，题卡保持`unseen`且尚无真实口述记录。

`VLA-PER-009` source/knowledge/card已同步并保持`unseen`。下一bounded slice只做PER-010 metric/parser source freeze；不生成knowledge/card，不创建`coaching_state.md`，不改变260张题卡的mastery。

## References

1. [PER-008 Representation Choice Source Freeze](../sources/vol_06_per008_representation_choice_source_freeze.html)。
2. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1) 与 [wentaoyuan/RoboPoint@206cb1e](https://github.com/wentaoyuan/RoboPoint/tree/206cb1e086fc3960a8673725a8540766655cd9c5)。
3. [Segment Anything v1](https://arxiv.org/abs/2304.02643v1) 与 [facebookresearch/segment-anything@dca509f](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
4. [kPAM v2](https://arxiv.org/abs/1903.06684v2) 与 [weigao95/kPAM@7214936](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
5. [Where2Act v2](https://arxiv.org/abs/2101.02692v2) 与 [daerduoCarey/where2act@1daf1a2](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
6. [PER-001 Grounding / Coordinate](vol_06_per001_grounding_coordinate.html)、[PER-006 Image / Token / Camera](vol_06_per006_image_preprocess_token_camera_contract.html)、[PER-007 Open-vocabulary Grounding](vol_06_per007_open_vocabulary_grounding_pipeline.html)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
