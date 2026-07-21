# VOL 06 PER-008 Source Freeze：Point / Box / Mask / Keypoint / Affordance 表示选择

> 状态：`source_frozen / VLA-PER-008 / primary_official_checked / local_point_box_affordance_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结五类 perception output 的语义、信息量、下游充分性、转换损失、uncertainty 与本地项目边界；不生成 knowledge/card，不展开 PER-009 loss、PER-010 metric 或 PER-012 具体模型。

## 问题（Question）

机器人收到“把杯子挂到架子上”“在空位放下物体”或“拉开抽屉”后，perception 应输出 point、box、mask、semantic keypoint 还是 action-conditioned affordance？更密集的表示是否一定更好？一个叫“affordance”的数据字段是否等于系统已经学习并执行了可行动作？

本页冻结的不是五选一排行榜，而是可审计的选择链：

```text
task + downstream consumer + coordinate/time contract
  -> minimum sufficient representation
  -> uncertainty / multimodality / validity schema
  -> optional conversion with explicit information loss
  -> parser / metric / controller gate
  -> evidence-bounded project claim
```

## 1. 结论先行

1. **表示由下游问题决定，不由像素密度决定**：ROI/crop 常用 box；轮廓、遮挡或精细占用需要 mask；一个或多个候选接触位置可用 point set；类别级几何约束需要有稳定语义 ID 的 keypoints；动作原语、方向、工具和状态条件进入后才是 affordance contract。
2. **point 不自动等于 keypoint 或 affordance**：裸坐标只回答“哪里”；semantic keypoint 还回答“这个点在类别中的角色”；affordance 还要回答“在什么动作、方向、工具、状态与 horizon 下可交互”。
3. **box 与 mask 不等价**：mask 可以确定一个包围盒，但多个不同 mask 可共享同一 box；从 box 反推 mask 是欠定问题。把 box 塞满当 mask 会伪造形状、接触和碰撞信息。
4. **SAM 证明 promptable mask I/O，不证明语义或机器人可行动性**：冻结 `SamPredictor` 接收 point/box/mask prompt，返回原图尺寸 masks、predicted mask quality 与低分辨率 logits；这些输出仍需 language/instance binding、坐标和 downstream action gate。
5. **RoboPoint 与 kPAM 的“keypoint”语义不同但都超出裸点**：RoboPoint 用语言条件输出多个 normalized image points，服务 spatial-affordance；kPAM 用 semantic 3D keypoints承载类别级几何 costs/constraints并接 action planning。不能只看二维坐标格式就把两者合并。
6. **Where2Act 的 affordance 是 action-conditioned contract**：冻结公源按 action primitive 在点云/像素位置上预测 actionability、proposal orientation 与 success likelihood；它不是普通 objectness heatmap，也不能迁移为任意 gripper/controller 的已校准成功率。
7. **本地 OPD 有 affordance-named point supervision，但没有已证实的 dense affordance head**：ShareRobot 路径把 `affordance.{x,y}` 归一化为一个 point target，训练/评估主合同仍是 point/box/text generation与parser/scorer。它支持“affordance-pointing 数据路径”，不支持 mask、semantic-keypoint pipeline、Where2Act式 actionability map、controller feasibility或机器人成功。

## 2. Primary / official / local source ledger

论文行的 SHA-256 对 2026-07-20 读取到的 version-pinned PDF bytes 计算；官方文本行按 UTF-8 与 LF 规范化后计算；本地文件使用原始文件 SHA。代码 license 只约束对应 repository source，不能自动覆盖论文、checkpoint、dataset 或第三方 asset。

| 来源 | 类型 / revision / license | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [RoboPoint paper v1](https://arxiv.org/abs/2406.10721v1) | primary；2024-06-15；PDF读取 2026-07-20 | `AE9E8476D63B82CCFA922905E6B410DC9EF302CD0618E11B79F10E06A5C8A1ED` | language-conditioned image keypoint affordance、synthetic instruction tuning与downstream framing | 本地 OPD 已复现RoboPoint结果或真实机器人成功 |
| [RoboPoint README](https://github.com/wentaoyuan/RoboPoint/blob/206cb1e086fc3960a8673725a8540766655cd9c5/README.md) | official-code；`206cb1e...`；Apache-2.0 repo | `DBEF6F10214A3DA0E10F666C230BB9EE8565B72C1FD5A8C42F3509C37107A57B` | 多个`[(x,y),...]`、`[0,1]` normalized image-point output contract | point语义自动等于3D keypoint、dense affordance或controller action |
| [RoboPoint summarize_vqa.py](https://github.com/wentaoyuan/RoboPoint/blob/206cb1e086fc3960a8673725a8540766655cd9c5/robopoint/eval/summarize_vqa.py) | official-code；同一commit | `B5B4617C53785DE459262F0595DF3FFAE643EF232DFCF18ECC24D4D0769349DA` | text→points/box-area parser、坐标缩放与mask-membership平均分 | metric跨项目可比、每个点是可执行接触或机器人成功 |
| [RoboPoint LICENSE](https://github.com/wentaoyuan/RoboPoint/blob/206cb1e086fc3960a8673725a8540766655cd9c5/LICENSE) | official-code；Apache-2.0 text | `C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4` | repository source license线索 | model/data/第三方依赖授权自动闭合 |
| [Segment Anything paper v1](https://arxiv.org/abs/2304.02643v1) | primary；2023-04-05；PDF读取 2026-07-20 | `C6CA524E47200C3E542587CA76AC1DBC89CC67340F948C819250D16FDBD90CFB` | promptable segmentation task/model/data engine与zero-shot framing | 语义label、语言grounding、contact或action feasibility |
| [Segment Anything README](https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/README.md) | official-code；`dca509f...`；Apache-2.0 repo | `CAB2C4900910C9E4AFD64833F57D106B8FC1A27FCA963D4439AE5B8F94CDBCE1` | point/box prompts产生mask、automatic mask generation入口 | 本地项目调用SAM或mask必然比box适合controller |
| [SAM predictor.py](https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/segment_anything/predictor.py) | official-code；同一commit | `AB66C29AC0B5B204D23997EF49D8A2476F71B596CE97E35EFBF116CFC2118FCE` | point/box/mask_input、multimask、`CxHxW` masks、quality与`256×256` low-res logits | quality已校准为任务成功率、mask带语义/实例唯一性或机器人安全 |
| [SAM LICENSE](https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/LICENSE) | official-code；Apache-2.0 text | `C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4` | repository source license线索 | SA-1B、checkpoint和第三方资产授权自动相同 |
| [kPAM paper v2](https://arxiv.org/abs/1903.06684v2) | primary；updated 2019-10-29；PDF读取 2026-07-20 | `37CC5BA0FD585E627E8573FB13C12D909F204B5D347EE4579A7947D8AA2DC7A8` | semantic 3D keypoints、几何cost/constraint、segmentation→keypoint→planning→execution factorization | 任意2D point list已经具备semantic identity、3D frame或planning闭环 |
| [kPAM README](https://github.com/weigao95/kPAM/blob/7214936b619527aee3b02d5306ada15decb95140/README.md) | official-code；`7214936...`；MIT repo | `665E70DCDAB873262458CC748F48A9D4550FA6B4EBFBAC7DD2884464C5636BD3` | category object target定义在semantic keypoints上；公开子模块边界 | private spartan、平台执行或本地项目已实现 |
| [kPAM LICENSE](https://github.com/weigao95/kPAM/blob/7214936b619527aee3b02d5306ada15decb95140/LICENSE) | official-code；MIT text | `0CE9E11A7E6AAEA1B8A0C75D0DBCC507C4F106D6CD7C44AA4C0D4A05F96E82BF` | top-level repository license线索 | 所有submodule、模型和数据授权自动闭合 |
| [Where2Act paper v2](https://arxiv.org/abs/2101.02692v2) | primary；ICCV 2021；updated 2021-08-10；PDF读取 2026-07-20 | `7649D0C8404CA5DD696D94A001D1D3501D789CA58B3002032BF67791D689631F` | action primitive条件下每点actionability、interaction proposal与可动region | 任意场景/机器人/工具上的通用成功概率 |
| [Where2Act README](https://github.com/daerduoCarey/where2act/blob/1daf1a24f7a372599b211108fa851f7ec3581330/README.md) | official-code；`1daf1a2...`；README声明MIT，但commit无LICENSE文件 | `C77FA0975B853BE7A5E081C7B278B82F2382318E359A734845F249984BB35788` | actionability score、trajectory、success likelihood、SAPIEN interaction framing | 完整license packaging、真实机器人结果或OPD同构实现 |
| [Where2Act model_3d.py](https://github.com/daerduoCarey/where2act/blob/1daf1a24f7a372599b211108fa851f7ec3581330/code/models/model_3d.py) | official-code；同一commit；license warning同上 | `968165B68FA9933553497F884F37F484A4F78D70BD647B5C4FF890F0427DE5C2` | PointNet++ feature、per-point ActionScore、6D orientation actor与critic success score | 分数跨primitive/robot校准或下游执行已经安全 |
| [PER-001 Grounding Coordinate Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | point/box/text schema、coordinate、parser与static metric边界 | 五类表示选择已被完整覆盖 |
| [PER-007 Open-vocabulary Grounding Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | Grounding DINO query–token、box/phrase、geometry/NMS contract | mask/keypoint/affordance选择或本地detector部署 |
| `muxi/point/build_expert_mixes_seed0.py` | local-evidence；`muxi@756e27e...` | `60DFDF46FDAC8EB9DBBE38A13298D6D71819EB7AD13F6B0D00A86B87032EABD0` | `<box>`/`<point>` extraction与expert mix | mask、semantic keypoint、dense affordance head或learned representation router |
| `muxi/point/eval_qwen_vl_raw_holdout.py` | local-evidence；同一HEAD | `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B` | point/box/text parser、format gate、IoU与point distance | action-conditioned success、mask IoU、keypoint identity或robot episode |
| `muxi/point/build_clean_grounding_pool.py` | local-evidence；同一HEAD | `A7A5906E11EA687C6FD0DEC40F3D30922A91B538EB98C740230227F9FF943087` | box clip/filter、`xyxy→0..1000`与tagged SFT row | box足以表示shape/contact或部署detector |
| `muxi/opd_project/scripts/build_prompt_pool.py` | local-evidence；同一HEAD | `293C776BA03E28DAC0029F985EEFFDC20036D24A289F3D74B1F761D1C7629315` | ShareRobot `affordance.{x,y}`→`0..1000`单point prompt/`gt_points` | dense affordance map、动作方向、controller feasibility或执行成功 |
| `muxi/point/point_data_only.py` | local-evidence；同一HEAD | `F650CB1F1B4A37566E11FA30C47A855DD59B74052588799839DF28F71EEC5787` | trajectory/affordance records转point answer与“actionable location”prompt | trajectory dynamics、semantic keypoint identity或真实机器人action |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-008只新增 |
| --- | --- | --- |
| PER-001 | point/box/text coordinate、parser、IoU/point metric基础 | 五类representation的语义层级、选择条件与不可逆转换 |
| PER-002 | 2D→3D lift、calibration、frame/TF | keypoint/affordance是否需要3D及其frame字段；不重讲投影公式 |
| PER-006 | image transform、processed/raw inverse、camera identity | 所有representation必须继承同一image/camera/time lineage |
| PER-007 | text-conditioned query–token、box/phrase与optional NMS | box与point/mask/keypoint/affordance的downstream trade-off |
| PER-009 | matching、negative、loss/reduction | 本页不规定每种head的训练loss |
| PER-010 | IoU/PCK/Recall/parser与protocol comparability | 本页只冻结metric所需字段，不选择最终分数或threshold |
| PER-012 | segmentation/depth/keypoint/affordance的具体方法 | 本页只做output/interface choice，不展开模型结构与训练recipe |
| PER-015 | perception→action reachability、uncertainty与failure gate | 本页不把representation输出升级为可执行action |

## 4. 五类表示的最小语义合同

### 4.1 Point：位置候选，不含范围

最小point set可写为`[(x_i,y_i)]_{i=1}^N`。它适合“在哪里点、放、看、接近”的候选位置，序列短、标注与生成便宜，也能表达多模态候选；但裸point没有物体范围、方向、surface normal、semantic role或action precondition。

必须冻结：`N`是否可变、坐标space/unit、点顺序是否有意义、重复点策略、valid radius、score semantics、空集与多解如何处理。RoboPoint README明确要求多个normalized tuples；本地OPD则主要使用`0..1000` tagged point，二者不能无manifest混用。

### 4.2 Box：实例范围近似，不含精细形状

box以`xyxy`或`cxcywh`给出instance extent，适合proposal、ROI crop、tracking association和粗碰撞gate。它比point多范围、比mask便宜，但会把背景和空洞包进矩形，不表达object contour、可抓部位或遮挡层级。

必须冻结：box格式、normalized/pixel、inclusive/exclusive corner、clip/invalid规则、phrase/instance binding、score与NMS policy。PER-007的box score不是mask quality或affordance success。

### 4.3 Mask：像素成员关系，不含任务语义

binary/soft mask回答“哪些像素属于这个region”。SAM predictor把point/box/mask prompt编码后，可返回`C×H×W`原图尺寸masks、长度`C`的predicted quality和`C×256×256` low-resolution logits；单click歧义时可返回多mask候选。

mask适合精细轮廓、重叠、surface extraction、occupancy或collision preprocessing，但成本包括dense storage/compute、component/instance ambiguity、边界噪声和temporal flicker。SAM mask本身没有language label、instance permanence、depth、contact normal或action primitive。

### 4.4 Semantic keypoint：带角色的几何锚点

keypoint不只是point坐标，还应有`semantic_id`、instance/category、visibility与2D/3D frame。kPAM把类别级目标写成semantic 3D keypoints上的几何costs/constraints，并显式分成instance segmentation、3D keypoint detection、optimization planning和local geometry execution。

它适合handle、rim、tip、hinge等少量任务相关结构，能忽略无关shape细节；代价是semantic correspondence难标、遮挡时不确定、跨类别定义可能失效，而且同一坐标若semantic ID不同，controller constraint也不同。

### 4.5 Affordance：动作条件下的可交互性

affordance必须至少绑定`primitive/tool/state`，必要时还要有direction/orientation、force、horizon与success-score semantics。Where2Act的公开合同是在articulated 3D object上，对pushing/pulling等primitive预测per-point actionability、interaction orientation proposal和critic success likelihood。

因此“affordance point”可以用point坐标承载结果，但它的语义不能被坐标本身替代。同一pixel在push与pull、不同gripper、门开/关状态或不同collision context下可以有不同可行性。

## 5. 选择原则：下游最小充分表示

表示选择是一个接口设计，而不是从point到mask的单调升级。下面是source-derived机制加engineering inference的冻结矩阵；“推荐”只表示起始contract，最终选择仍需matched task evidence。

| 下游问题 | 起始表示 | 为什么足够/必要 | 主要代价与失败 |
| --- | --- | --- | --- |
| object proposal、ROI crop、粗tracking | box + phrase/instance | 需要范围但不依赖精细contour | 背景混入、thin/rotated object不紧致 |
| free-space、look-at、粗contact候选 | point set + validity radius | 输出短且能表达多个位置mode | 无extent/normal；单点可能落在不可达或遮挡处 |
| precise overlap、contour、surface/occupancy预处理 | mask + instance/quality | 像素成员关系直接服务几何处理 | dense成本、temporal flicker、语义/深度仍缺 |
| category-level pose-free geometric constraint | semantic 2D/3D keypoints | 少量task-relevant anchors可进入cost/constraint | 语义 correspondence、visibility与frame难题 |
| contact/action proposal conditioned on primitive | affordance field/points + primitive + direction + success semantics | 输出直接绑定“哪里+如何做” | 强task/robot/controller依赖，校准与安全证据要求最高 |

一个可审计的engineering选择目标可写为：

\[
r^*=\arg\min_{r\in\mathcal R}
\left(C_{\mathrm{label}}(r)+C_{\mathrm{infer}}(r)
+\lambda\,\mathbb E[L_{\mathrm{down}}\mid r]
+\mu\,C_{\mathrm{convert}}(r)+\nu\,C_{\mathrm{stale}}(r)\right).
\]

其中`r`是representation，`C_label/C_infer`是标注与推理成本，`L_down`是下游任务损失，`C_convert`是坐标/格式转换与信息损失，`C_stale`是时序陈旧风险，`λ/μ/ν`是部署权重。该式是本页的decision rubric，不是四篇论文共同提出的训练目标；代码映射应落到manifest、latency log、matched ablation和downstream failure trace。

## 6. 转换不等价与确定性probe

### 6.1 Mask→box是有损映射

对非空binary mask `M`，其axis-aligned bounding box可写为：

\[
B(M)=\left(\min_{M(x,y)=1}x,\min_{M(x,y)=1}y,
\max_{M(x,y)=1}x+1,\max_{M(x,y)=1}y+1\right).
\]

变量`M(x,y)`表示pixel membership，`B(M)`使用half-open `xyxy`。直觉上box只保留四个极值；实现上可由`where(mask)`求min/max，但不能从四个数唯一恢复mask。

确定性5×5 probe：一个3×3实心mask和仅保留四角的mask都得到`(1,1,4,4)`，但面积分别为9和4。结论是`mask→box`可复算，`box→mask`不可逆；把box内部全设1不是恢复，而是新假设。

### 6.2 Point不保留semantic/action fields

同一`xy=(200,300)`分别标为`mug_handle`和`mug_rim`，坐标相同但keypoint contract不同；同一`xy=(500,500)`分别绑定`push/+x`和`pull/-x`，坐标相同但affordance contract不同。裸point只能作为完整record的一个field。

### 6.3 表示转换必须标记provenance

| 转换 | 可做 | 丢失/新增假设 |
| --- | --- | --- |
| mask→box | 对foreground取极值 | contour、hole、component与area |
| keypoints→box | 对visible points取极值 | object extent；box可能只包住局部anchors |
| affordance field→top-k points | 按score/spacing取候选 | dense landscape、calibration、被截mode |
| box→mask | 只能调用segmentation model或填充矩形 | model revision/prompt与新prediction；不是inverse |
| point→affordance | 不可仅凭坐标完成 | 必须新增primitive/tool/state/direction与success semantics |

## 7. Typed representation manifest

任何表示都先继承PER-006的image/camera/time lineage，再保存自身字段：

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

`payload`按类型扩展：

| 类型 | 必需payload |
| --- | --- |
| point set | `points,point_scores,valid_radius,ordering,multimodal_group` |
| box | `format,coords,phrase,instance_id,clipped,nms_revision` |
| mask | `shape,encoding,threshold,component_ids,quality_semantics,source_prompt` |
| semantic keypoints | `semantic_ids,coords,visibility,covariance,instance_id,category,frame` |
| affordance | `support_geometry,primitive,tool_or_gripper,state_precondition,direction_or_orientation,horizon,success_score_semantics` |

只保存`payload`而不保存representation type、coordinate space和score semantics，会让同样的两个数字在pixel、normalized、keypoint或action point之间静默漂移。

## 8. 可审计选择伪代码

```python
def choose_perception_representation(task, consumer, evidence):
    # 1) 先冻结下游真正读取的字段；不要先选最复杂的视觉head。
    need = consumer.required_fields(task)

    # 2) 用最小充分表示满足extent、contour、semantic anchor或action条件。
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

    # 3) 验证本地source/label/parser/metric/controller是否真的支持该表示。
    if not evidence.has_schema(rep) or not evidence.has_parser(rep):
        return fail_closed("representation_not_supported")

    # 4) 所有表示继承image/camera/time/coordinate lineage并保留不确定性。
    manifest = build_typed_manifest(rep, task, consumer, evidence)

    # 5) 转换只能作为有provenance的新stage；禁止把有损转换写成等价。
    manifest.conversions = freeze_conversion_chain(evidence.conversions)
    return manifest
```

此伪代码不是某个official API；它把本页source facts组织成fail-closed工程gate。knowledge阶段应再展开每种表示的口述比较与matched evaluation设计。

## 9. 四个公开方法的接口对照

| 方法 | 输入条件 | 原生输出 | 适合支持 | 必须补的downstream contract |
| --- | --- | --- | --- | --- |
| Grounding DINO（PER-007） | image + text tokens | query-token score + normalized boxes + phrase | open-vocabulary proposal/ROI | coordinate inverse、NMS、instance/action gate |
| RoboPoint | image + language instruction | multiple normalized image points | spatial relation/free-space/action-point suggestion | parser、mode/valid radius、reachability与controller验证 |
| SAM | image + point/box/mask prompts | one/multiple masks + predicted quality + low-res logits | promptable contour/region extraction | semantic/language binding、instance/time/depth/action gate |
| kPAM | segmented object + semantic keypoint detector | semantic 3D keypoints进入geometric costs/constraints | category-level manipulation geometry | visibility/covariance、frame/calibration、planner/executor |
| Where2Act | articulated point cloud/image-depth + action primitive | per-point actionability、orientation proposal、critic score | primitive-conditioned interaction proposal | robot/tool/state/domain calibration与safe execution |

这些方法不是可互换baseline：输入、输出、监督、metric与机器人条件不同。不能用论文各自数字比较“哪种表示最好”。

## 10. 本地 OPD：affordance-named point，不是dense affordance head

冻结本地HEAD为`756e27e16adcfb3ccbfe98c2920dda42095b127f`；五个直接读取文件无选定路径未提交diff。直接证据链为：

```text
ShareRobot affordance {x,y} / trajectory or point records
  -> normalize or scale to point coordinates
  -> prompt: point to actionable location / predict trajectory
  -> tagged point/box/text SFT target
  -> autoregressive generation
  -> point/box/text parser and static scorer
```

具体边界：

1. `build_prompt_pool.py`把`affordance.x/y`按原图宽高缩放到`0..1000`，输出一个`gt_points=[[x,y]]`并标`task_type=affordance_pointing`；没有primitive、direction、gripper、state或success head。
2. `point_data_only.py`读取trajectory/affordance records，最终仍调用`point_answer(scaled)`；“Point to the actionable affordance location”是prompt语义，不改变point representation本身。
3. `build_expert_mixes_seed0.py`显式提取`<box>`和`<point>`；`eval_qwen_vl_raw_holdout.py`按point/box/text走format与geometry/static text评分。
4. 对这五个选定文件的静态搜索中，`keypoint`、`segment_anything`、`sam_model`、`mask_rle`、`polygon`和`<mask>`均为0匹配；这只说明选定路径没有显式实现，不排除未归档、远端、历史或其他文件。

安全表述：

> 本地OPD含affordance-labelled point supervision和point/box/text生成评估。我会把“affordance数据语义”与“representation type=point”分开；当前证据不支持dense affordance map、semantic keypoint/SAM pipeline、action-conditioned success calibration或机器人执行闭环。

## 11. Failure taxonomy 与补证顺序

| 层 | 失败 | 首个检查 |
| --- | --- | --- |
| task sufficiency | point无法支持contour/collision，box无法支持contact | downstream consumer required-fields |
| semantic collapse | 把裸point叫keypoint/affordance | semantic ID、primitive/tool/state fields |
| geometry | pixel/normalized、processed/raw、2D/3D混用 | coordinate space、transform、frame与round-trip |
| ambiguity | 单点/单mask强行压掉多解 | candidate set、multimask、mode group与uncertainty |
| conversion | box填充成mask或points极值当object box | conversion provenance与loss declaration |
| temporal | mask/keypoint/affordance已陈旧仍执行 | timestamp、observation age、tracking/instance ID |
| score | mask quality、objectness、point hit、affordance success混比 | score semantics、calibration split与protocol revision |
| project | affordance-named dataset被说成机器人能力 | raw target、model head、parser、controller与episode artifact |

补证顺序：冻结consumer字段→选择最小表示→保存raw/multimodal output→坐标与time round-trip→解析/metric golden test→matched downstream ablation→controller/reachability gate→最后才谈robot success。

## 12. Source gate 结论与下一 bounded slice

本切片已冻结：

1. point、box、mask、semantic keypoint与affordance的最小语义差异；
2. RoboPoint、SAM、kPAM、Where2Act的version-pinned paper/repo/output contracts；
3. downstream minimum-sufficient selection、不可逆转换与typed manifest；
4. 三个deterministic non-equivalence probes；
5. OPD中“affordance-labelled point supervision”与“dense/action-conditioned affordance model”的真实性边界；
6. 与PER-001/002/006/007/009/010/012/015的责任去重。

当前verdict为`WARN`：公源表示合同已冻结，但本地没有mask/semantic-keypoint head、dense affordance map、action primitive/direction/success-calibration、matched representation ablation或controller/robot bundle；Where2Act pinned commit只有README中的MIT声明而无LICENSE文件。

`VLA-PER-008..009` source/knowledge/card均已在独立切片同步，题卡保持`unseen`。下一 bounded slice只做PER-010 metric/parser source freeze；不生成knowledge/card，不创建`coaching_state.md`，不改变260张题卡的状态。

## References

1. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1) 与 [official repository@206cb1e](https://github.com/wentaoyuan/RoboPoint/tree/206cb1e086fc3960a8673725a8540766655cd9c5)。
2. [Segment Anything v1](https://arxiv.org/abs/2304.02643v1) 与 [official repository@dca509f](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
3. [kPAM v2](https://arxiv.org/abs/1903.06684v2) 与 [official repository@7214936](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
4. [Where2Act v2](https://arxiv.org/abs/2101.02692v2) 与 [official repository@1daf1a2](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
5. [PER-001 Grounding Coordinate Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html)。
6. [PER-007 Open-vocabulary Grounding Source Freeze](vol_06_per007_open_vocabulary_grounding_pipeline_source_freeze.html)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
8. Local read-only evidence：`C:\Users\mousongzhe\muxi` at `756e27e16adcfb3ccbfe98c2920dda42095b127f`；selected file hashes见source ledger。
