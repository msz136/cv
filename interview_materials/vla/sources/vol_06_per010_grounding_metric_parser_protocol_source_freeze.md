# VOL 06 PER-010 Source Freeze：Grounding Metric、Strict Parser 与 Protocol Comparability

> 状态：`source_frozen / VLA-PER-010 / primary_official_checked / local_parser_scorer_holdout_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结raw output→parser→validity→matching→metric→denominator→protocol identity的评估合同；不生成knowledge/card，不展开PER-011 teacher noise/leakage或PER-015 action gate。

## 问题（Question）

Grounding输出应如何被strict parser解析？IoU、Acc@IoU、Referring-expression Recall@k、COCO AP/AR、PCK、mask-hit和固定像素距离Hit分别回答什么问题？invalid、empty、duplicate和多点匹配如何进入分母？两个都叫“Recall@1”或“Hit@50”的数字在什么条件下才可比较？本地OPD holdout的严格格式失败、宽松几何得分与项目能力边界应如何口述？

本页冻结的可审计链为：

```text
raw model output
  -> expected representation + exact parser grammar/version
  -> syntax / tag / coordinate / geometry validity status
  -> representation-specific matching
  -> per-sample metric and invalid/empty treatment
  -> denominator + aggregation + stratification
  -> split/checkpoint/prompt/scorer protocol identity
  -> comparable / conditionally comparable / not comparable
  -> project claim boundary
```

## 1. 结论先行

1. **Parser是metric的一部分，不是清洗细节**：同一raw output在strict与lenient parser下可能分别得到format failure和有效几何；只报告后者会把instruction following缺陷隐藏掉。
2. **解析成功、格式合规、坐标合法、几何正确是四个不同事件**：应保存typed status，而不是用一个`valid=true`吞并所有失败原因。
3. **IoU本身不是Acc@IoU，也不是AP/AR**：IoU是单对框overlap；Acc@\(\tau\)是阈值后的样本成功率；COCO AP/AR还绑定ranking、matching、IoU threshold grid、area range、category与`maxDets`。
4. **Referring-expression Recall@k只在明确top-k、overlap函数、阈值和每表达式GT结构后有意义**。MDETR论文描述IoU-based Recall@k；冻结commit却以GIoU阈值判定并打印`Precision @ 1,5,10`，说明名字不能替代代码审计。
5. **PCK不是任意point distance threshold**：它需要pred/GT keypoint对应关系、normalization factor、threshold、visibility mask与aggregation规则。本地`Hit@50/100`使用0..1000坐标上的任意pred–gold最近距离，不应称为标准PCK。
6. **RoboPoint mask-hit也不是PCK或point recall**：其论文口径是预测点落入target mask的比例，分母是预测点；它不要求命中每个GT keypoint，也不惩罚遗漏全部target modes。
7. **多点集合不能只看最小任意对距离**：一个准确点就能令本地`Hit@50`通过，即使其余预测/GT覆盖很差；至少要同时看pred→gold、gold→pred、count差异，必要时冻结one-to-one matching。
8. **invalid/empty必须预先写入denominator policy**：本地bool rate按全部对应format样本数除，numeric mean跳过`None`；所以同一summary中的`format_pass`与`iou_mean`可能根本不是同一分母。
9. **Protocol identity必须包含split/data hash、sample IDs、checkpoint、prompt/template、decode、parser/scorer revision、representation、坐标系、matching、阈值、invalid policy与aggregation**。字段不一致时，默认不可直接比较。
10. **本地OPD结论必须分三层**：original strict、protocol-fixed strict、lenient geometry。现有inventory可支持静态holdout数字与格式诊断；不能把它升级为机器人成功率、OPD单因素因果或候选人ownership。

## 2. Primary / official / local source ledger

论文SHA对version-pinned PDF bytes计算；GitHub文本按UTF-8/LF冻结；本地文件按原始bytes。repository license只约束相应source code，不能自动覆盖paper、dataset、checkpoint或第三方asset。

| 来源 | 类型 / revision / license | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [MDETR paper v3](https://arxiv.org/abs/2104.12763v3) | primary；2022-03-25 v3；PDF读取2026-07-20 | `797ABB81609E021C653B9B435E56C7E8F9EDB784C04ACAE1F8E0EC375517C421` | grounding Recall@k按top-k中是否存在IoU超过阈值的box；one-to-one referring-expression场景 | 冻结repo evaluator与论文文字完全同构 |
| [MDETR RefExp evaluator](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/datasets/refexp.py) | official-code；`ea09acc...`；Apache-2.0 header | `FB53B06A4F8ACA0DCD64AEAB9E82000E81CCAFD8D2B5362EEFA5F3DB011FBC36` | `k=(1,5,10)`、threshold=.5、score排序、每expression success与dataset denominator；实际调用GIoU并打印Precision | 所有MDETR revision、论文IoU描述或COCO AP |
| [MDETR refexp guide](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/.github/refexp.md) | official-code/docs；同一commit | `C53E16E40AF5DD0D5F929CFC1530BFF56E5AF1AAACC79157B9548D63735BF6A6` | RefCOCO/+/g运行与split配置线索 | evaluator内部overlap函数无需代码核验 |
| [MDETR postprocessors](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/models/postprocessors.py) | official-code；同一commit | `F1A3C4926A053B69FC421BF5468DCFF78CA6CF211E6E0D09647872419FA311A8` | score/box postprocessing bridge | final RefExp denominator或paper claim |
| [COCO API cocoeval.py](https://github.com/cocodataset/cocoapi/blob/8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9/PythonAPI/pycocotools/cocoeval.py) | official-code；`8c9bcc...`；BSD-style repo license | `E514AF401848D5A4CC5D3512BD93D2C317F92272C6D30F218E0F00B7B4110534` | IoU/recall grids、score排序、matching/ignore、precision/recall tensor、area/maxDets/category contracts | Referring-expression Recall@k、PCK或本地OPD scorer |
| [COCO API license](https://github.com/cocodataset/cocoapi/blob/8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9/license.txt) | official license text | `BD8EF15597B3B292F3BB0FEED9701C1ACE5BCEBE07F28FB5047EC8D3D89471B1` | repository source license线索 | dataset media或第三方授权 |
| [RoboPoint paper v1](https://arxiv.org/abs/2406.10721v1) | primary；2024-06-15 v1；PDF读取2026-07-20 | `AE9E8476D63B82CCFA922905E6B410DC9EF302CD0618E11B79F10E06A5C8A1ED` | spatial-affordance accuracy为predicted points落在target mask内的比例 | 标准PCK、本地fixed-distance Hit或robot success |
| [MPII Human Pose paper v1](https://arxiv.org/abs/1406.2984v1) | primary benchmark context；2014-06-11 v1 | `36E62198F0405D2E96C5FF6E965D689565A084860D152E235899DCCA4E92B476` | MPII pose benchmark与PCKh语境 | 本轮直接从PDF冻结通用PCK实现公式；公式由下列implementation bridge限定 |
| [MMPose keypoint_eval.py](https://github.com/open-mmlab/mmpose/blob/759b39c13fea6ba094afc1fa932f51dc1b11cbf9/mmpose/evaluation/functional/keypoint_eval.py) | implementation bridge；`759b39c...`；Apache-2.0 | `70892DE7B0378366F56B4474EE4C282181619BFDE38C627D41907A582E5F080A` | normalized coordinate distance、visibility mask、threshold、missing target与per-keypoint aggregation | grounding point-set天然具有keypoint correspondence |
| [MMPose LICENSE](https://github.com/open-mmlab/mmpose/blob/759b39c13fea6ba094afc1fa932f51dc1b11cbf9/LICENSE) | Apache-2.0 text | `AA2C6F3408169B96E5547C875DEB481C91502514C1885FA0ACB4B596C8909CB9` | repository source license线索 | dataset/model license自动闭合 |
| `muxi/point/eval_qwen_vl_raw_holdout.py` | local evaluator；`muxi@756e27e...`；selected path clean | `29574ADCE53B254BC33ED39C370642707F570000F7F3FB8F037DBD1F5E0D206B` | expected-format routing、lenient geometry parser、format gate、IoU/point/text score、mixed fallback与field-specific denominator | 标准PCK/RefCOCO/COCO等价性、robot result或因果提升 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | repository local evidence inventory | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | raw holdout构成/去重/leakage检查、checkpoint pool metrics、strict-vs-lenient诊断与claim边界 | raw prediction已在本页重新归档、候选人ownership或closed-loop success |
| [PER-001 Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | point/box/text schema、0..1000 coordinate与basic parser | PER-010的完整metric comparability |
| [PER-008 Source Freeze](vol_06_per008_representation_choice_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | representation choice与转换损失 | parser、denominator或protocol identity |
| [PER-009 Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | training matching/loss/reduction | evaluation metric或holdout comparability |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-010只新增 |
| --- | --- | --- |
| PER-001 | point/box/text schema、坐标协议、basic parser | strict/lenient双轨、invalid taxonomy与metric denominator |
| PER-006 | resize/crop/letterbox、camera/time lineage | 只要求这些字段进入protocol identity，不重讲变换 |
| PER-007 | open-vocabulary inference、threshold/NMS与phrase/box输出 | evaluator读取什么、如何match和aggregate |
| PER-008 | point/box/mask/keypoint/affordance表示选择 | representation-specific metric不可互换 |
| PER-009 | Hungarian training matching、negative、loss/reduction | 不把training cost/loss叫evaluation metric |
| PER-011 | teacher noise、confidence calibration、leakage、curriculum | 本页只记录gold/split/protocol identity，不判断teacher可靠性 |
| PER-015 | perception→action reachability、uncertainty与failure gate | 不从static metric推出可执行动作或robot success |
| VOL 05 | 通用统计、CI、paired test与evaluation engineering | 本页新增grounding parser、matching和representation语义 |

## 4. Typed Prediction 与 Strict Parser 合同

最小prediction record应同时保留raw与typed字段：

```json
{
  "sample_id": "...",
  "expected_representation": "point | box | text",
  "raw_output": "...",
  "parser_revision": "sha256:...",
  "parse_mode": "strict | lenient_diagnostic",
  "tag_status": "pass | missing | mixed | extra",
  "syntax_status": "pass | no_match | ambiguous | trailing_content",
  "coordinate_status": "pass | out_of_range | non_finite | wrong_arity",
  "geometry_status": "pass | degenerate | empty",
  "parsed_prediction": null,
  "invalid_reason": null
}
```

推荐strict grammar对完整字符串做`fullmatch`，而不是从任意prose中搜索数字。示意EBNF为：

```text
number      = optional_sign, digits, optional_decimal ;
point       = "[", number, ",", number, "]" ;
point_out   = "<point>", "[", point, {",", point}, "]", "</point>" ;
box_out     = "<box>", "[", number, ",", number, ",", number, ",", number, "]", "</box>" ;
```

grammar只是第一层；还应检查finite、坐标范围、arity、box的\(x_2>x_1,y_2>y_1\)，并明确是否允许空集合、额外文本、多个tag或point+box混合。strict score用于部署/指令遵循主结论；lenient parser只用于定位“格式错但几何可能对”的诊断，不得静默替换主口径。

## 5. 本地 Parser 的真实语义

`expected_format`从gold answer中的tag路由：只有`<point>`为point、只有`<box>`为box、两者都有为`mixed_grounding`、都没有为text。当前scorer没有`mixed_grounding`专门分支，因此该类会落入text scoring。

本地几何parser比format gate更宽松：

1. `parse_points`用全局regex搜索任意`[x,y]`，不要求它位于`<point>...</point>`内；
2. `parse_box`先匹配flat tagged box，再读取`<box>...</box>`内前四个数字，最后可把文本中的前两个point pairs当box；
3. `valid_box`要求四个坐标在0..1000且严格正面积；
4. box `format_pass`还要求raw string含`<box>`，point `format_pass`要求含`<point>`且所有parsed points在范围内；
5. 几何metric仍可使用lenient parse结果，即使`format_pass=false`；
6. text branch无条件令`format_pass=true`，所以mixed grounding被错误路由后不会暴露grounding format failure。

这不是一个纯strict evaluator，而是“tag gate + lenient geometry extraction + format-specific scoring”的组合。安全报告必须同时给出strict format rate、lenient geometry coverage和原始invalid reasons。

## 6. Box IoU 与 Acc@Threshold

对corner boxes \(A,B\)，标准axis-aligned IoU为：

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}.
\]

本地实现对intersection宽高做non-negative clamp，并把union denominator下限设为\(10^{-9}\)。对有效pred/gold box，单样本`iou`是连续值；阈值准确率为：

\[
\operatorname{Acc@IoU}(\tau)=\frac{1}{N}\sum_{i=1}^{N}
\mathbf 1\!\left[\operatorname{IoU}(\hat b_i,b_i)\ge\tau\right].
\]

变量解释：\(N\)必须写明是全部box样本、成功解析样本还是其他subset；本地`acc_iou_0_3/0_5/0_75`把invalid prediction记为false并除全部box样本，而`iou_mean`只在pred/gold都valid时记录numeric value。

因此`Acc@0.5=0.52`不能推出mean IoU为0.52，反之亦然；改变inclusive `>=`为strict `>`、坐标反归一化、box order、parser或invalid denominator都可能改变数字。

## 7. Referring-expression Recall@k 与 MDETR Revision Trap

在one-expression/one-target的常见RefCOCO设置中，可抽象为：

\[
R@k(\tau)=\frac{1}{N}\sum_{i=1}^{N}
\mathbf 1\!\left[\max_{j\le k} O(\hat b_{i,j},b_i)\ge\tau\right],
\]

其中\(O\)应被明确冻结为IoU、GIoU或其他overlap，预测框按何种score排序也属于protocol。这个量更像“每个expression的top-k success fraction”；在单GT设置下某些论文称Recall@k，冻结MDETR代码却打印Precision@k。名称本身不能消除语义歧义。

MDETR v3论文说明用IoU threshold（通常0.5）判断top-k是否命中；`mdetr@ea09acc.../datasets/refexp.py`却调用`generalized_box_iou`，再以`>=0.5`判定。确定性反例：

```text
A = [0, 0, 2, 2]
B = [0.34, 0.34, 2.34, 2.34]
IoU(A,B)  = 0.5254366562  -> pass at 0.5
GIoU(A,B) = 0.4832129730  -> fail at 0.5
```

所以引用MDETR数字时必须绑定paper table或code revision；不能把paper的“IoU Recall@1”和该commit运行得到的“GIoU-threshold Precision@1”当成无条件同protocol结果。

## 8. COCO AP / AR 不是 RefExp Recall@k

冻结COCO API detection defaults包括：

- `iouThrs = 0.50:0.05:0.95`，共10个threshold；
- `recThrs = 0:0.01:1`，共101个recall positions；
- detection `maxDets = [1,10,100]`；
- precision tensor shape为`[T,R,K,A,M]`，recall为`[T,K,A,M]`；
- absent categories以`-1`保存并在summary均值中排除；
- detections按score稳定排序，随后按category/image/IoU threshold做matching，并处理ignore、crowd与area range。

COCO AP是precision–recall envelope在指定维度上的汇总，AR也依赖IoU grid、area与maxDets。RefExp R@k通常按expression做binary success。二者即使都含“recall”也不共享sample unit、matching、ranking、denominator或aggregation，不能只凭scalar名字比较。

## 9. PCK：Normalization、Visibility 与 Correspondence

一个常见normalized keypoint hit可写为：

\[
h_{n,k}(\tau)=
\mathbf 1\!\left[
\left\|\frac{\hat p_{n,k}-p_{n,k}}{s_n}\right\|_2<\tau
\right],
\qquad m_{n,k}=1,
\]

其中\(s_n\)可为bbox尺度、head尺度或按H/W的二维normalization factor；\(m_{n,k}\)是visibility/validity mask。PCK还必须说明是先按keypoint type求accuracy再macro average，还是对全部visible joints做micro average。

冻结MMPose实现对coordinate difference按`norm_factor[:,None,:]`逐维归一化，再取L2 distance；invisible target被mask掉，zero norm会令该sample所有keypoints无效，missing distance记为`-1`。`keypoint_pck_accuracy`先对每个keypoint type跨instances算threshold accuracy，再对有效keypoint types求mean。因此仅报告“PCK@0.2”仍不足以复现，必须给出normalizer、visibility与macro/micro规则。

普通grounding point set往往没有固定keypoint identity。若pred point与GT point没有一一对应，直接套PCK公式会偷偷引入matching假设；应先冻结nearest-neighbor、Hungarian或semantic keypoint correspondence。

## 10. RoboPoint Mask-hit 与本地 Fixed-distance Hit

RoboPoint v1将spatial-affordance accuracy定义为预测点落入ground-truth target mask的比例，可抽象为：

\[
\operatorname{MaskHit}=\frac{1}{|P|}\sum_{p\in P}\mathbf 1[p\in M].
\]

它主要衡量预测点precision-like有效性：如果只给一个位于mask内的点，score可很高；它不要求覆盖mask全部区域，也不等于GT point recall或PCK。

本地point score先计算所有pred–gold pairs的Euclidean distance，再用全局最小值定义：

\[
d_{\min}=\min_{p\in P,g\in G}\lVert p-g\rVert_2,
\qquad
\operatorname{Hit@r}=\mathbf 1[d_{\min}\le r],
\quad r\in\{50,100\}.
\]

坐标位于0..1000规范空间；没有image diagonal、bbox、head或object size normalization。它回答“是否至少有一对点足够近”，而不是“多少pred有效”“多少GT被覆盖”或“对应keypoint是否正确”。因此报告时应称`fixed-coordinate any-pair Hit@50/100`，不要简称PCK。

## 11. Multi-point Matching、Coverage 与 Duplicate

本地还记录两个directed nearest-neighbor mean：

\[
d_{P\to G}=\frac{1}{|P|}\sum_{p\in P}\min_{g\in G}\lVert p-g\rVert_2,
\qquad
d_{G\to P}=\frac{1}{|G|}\sum_{g\in G}\min_{p\in P}\lVert g-p\rVert_2.
\]

前者更接近prediction purity，后者更接近GT coverage，但两者都允许many-to-one匹配；duplicate predictions会重复进入\(P\to G\)，却不增加\(G\to P\)覆盖。若任务要求一一对应，应改用version-pinned bipartite matching并冻结unmatched penalty。

确定性probe：`P={(0,0),(1000,1000)}`、`G={(1,1),(900,900)}`时，\(d_{\min}=1.414\)，所以Hit@50/100都通过；但两个directed mean均约71.418。一个boolean hit掩盖了集合其余部分的偏差。必须联合报告count difference、两个directed means与任务相关coverage，不能只挑最好看的一个指标。

## 12. Invalid、Empty、Mixed 与 Denominator Policy

| 情况 | Strict主指标建议 | Lenient诊断 | 本地当前行为 |
| --- | --- | --- | --- |
| 缺tag但坐标可抽取 | format failure；几何主指标按预注册policy记失败或separate | 可计算diagnostic geometry | `format_pass=false`，仍可能计算IoU/distance |
| prose含`[x,y]` | trailing/prose failure | 可抽取point | point regex会抽取 |
| `[(x,y)]`括号形式 | syntax failure | parser若有显式legacy mode才可恢复 | 当前regex无法抽取 |
| out-of-range point | coordinate failure | 保留raw与reason | `coord_valid=false`，但若pred/gold非空仍计算distance |
| degenerate/invalid box | geometry failure | 不应伪造box | bool IoU hits=false，numeric IoU/center为`None` |
| empty prediction | explicit empty failure | 记录empty而非parser crash | point hits=false，numeric distance为`None` |
| point+box mixed gold | 单独mixed schema或拒绝 | 不应自动当text | `expected_format=mixed_grounding`后落入text，`format_pass=true` |
| duplicate points | 依任务去重或计入precision penalty | 报告pre/post-dedup | 当前保留，影响count与pred→gold mean |

本地`Metrics.summary`对bool字段以全部该format pool的`n`为分母；对numeric字段只除实际出现且finite的count。两条样本中一条invalid box、一条perfect box的probe得到：`format_pass=0.5`、`Acc@0.5=0.5`，但`iou_mean=1.0`。这不是矛盾，而是分母不同；若报告里不附`iou__count`，`1.0`会极具误导性。

## 13. Aggregation 与 Stratification

至少区分以下aggregation unit：

1. sample/micro：每条样本等权；
2. image：同图多个prompt先聚合，避免多prompt图权重过大；
3. category/task/macro：各类别或point/box/text pool等权；
4. keypoint type：先跨instances聚合，再对valid types求mean；
5. episode/robot：属于另一evaluation unit，不能由static image sample替代。

同时应按expected representation、object size、point count、prompt template、source dataset、image uniqueness、validity reason与checkpoint分层。overall scalar可能被2,500条text、6,100条box和1,400条point的pool比例主导，不代表每个slice都改善。

## 14. Protocol Identity 与 Comparability Matrix

建议protocol ID由canonical manifest序列化后计算SHA-256：

```json
{
  "dataset_revision": "...",
  "split_and_sample_ids_sha256": "...",
  "image_and_gold_sha256": "...",
  "checkpoint_sha256": "...",
  "processor_prompt_template": "...",
  "decode_config": {},
  "expected_representation": "...",
  "coordinate_and_image_transform": {},
  "parser_revision_and_mode": "...",
  "matching_and_overlap": {},
  "thresholds": [],
  "invalid_empty_duplicate_policy": {},
  "denominators": {},
  "aggregation_and_strata": {},
  "scorer_runtime_revision": "..."
}
```

| 差异 | 可比结论 | 理由 |
| --- | --- | --- |
| 所有manifest字段相同，仅随机seed不同 | 可直接paired比较，另报不确定性 | sample与scorer identity一致 |
| 同raw predictions，仅strict parser修复且同时报告旧/新口径 | 条件可比 | 可隔离parser effect，但新旧scalar不能混成同一leaderboard |
| IoU改GIoU、`>=`改`>`或threshold改变 | 不直接可比 | per-sample success可能翻转 |
| invalid从false改为drop | 不直接可比 | denominator和selection改变 |
| fixed distance Hit改PCK | 不可比 | normalizer、correspondence和任务问题不同 |
| RefExp R@1改COCO AP | 不可比 | unit、ranking、matching、threshold grid不同 |
| split、image transform、prompt或checkpoint改变 | 不做单因素归因 | 多个causal factors同时变化 |
| static holdout改robot episode success | 不可比 | observation/action/unit/failure semantics不同 |

## 15. 本地 OPD Evaluator Code Mapping

本地code-to-metric映射如下：

| Expected pool | Parse / gate | Per-sample fields | 主要风险 |
| --- | --- | --- | --- |
| box | flat tag→tag body numbers→two point pairs；0..1000且正面积 | format/coord、IoU、Acc@.3/.5/.75、center distance | lenient fallback可在format fail时仍得几何分；numeric denominator跳invalid |
| point | 任意文本全局抓`[x,y]`；tag与range另判 | format/coord、counts、min/双向mean distance、Hit@50/100 | any-pair hit过于乐观、无normalization、out-of-range仍可能算distance |
| text | normalize后exact/loose/bool/MC | format恒true、text scores | loose match可能容忍额外文本 |
| mixed | 没有专门branch | 实际走text | grounding结构错误被隐藏 |

这张表说明parser、format gate和metric computation必须分别记录。若要修复本地scorer，应先保存现有raw predictions并建立golden tests，再发布新parser revision；不能覆盖旧结果后仍沿用同一protocol名称。

## 16. Raw Holdout Protocol Reconciliation

现有OPD inventory记录raw holdout为10,000条：box 6,100、point 1,400、text 2,500，共8,251 unique images；fingerprint、source-line、image+prompt+answer重复均为0，且与train image交集为0。OPD5000 checkpoint 5000在已记录pool上的数字包括Box Acc@0.5 `0.5238`、Point Hit@50/100 `0.7493/0.8729`、Text exact `0.8724`；不同pool最佳checkpoint并不相同。

这些数字只在inventory冻结的dataset/evaluator语境内成立，且本页未重新归档对应raw predictions。早期point prompt要求裸`[(x,y)]`，当前strict gate要求`<point>...</point>`；更具体地说，当前regex甚至不能解析圆括号pair形式，而能从裸`[x,y]`或prose中抽取坐标。因此需要分开：

1. **original strict**：完全按原prompt、原parser与原scorer复现，作为历史结果；
2. **protocol-fixed strict**：修复prompt/parser合同后重跑同raw sample IDs，发布新protocol ID；
3. **lenient geometry diagnostic**：在raw outputs上尝试versioned recovery，只用于分析潜在几何能力。

`strict=0`不能直接解释为几何能力为0；lenient geometry较高也不能抹去部署格式失败。最可信的修复证据是同一raw output同时跑old/new parser的paired transition matrix，再决定是否需要重新generation。

## 17. 五个确定性 Probes

### 17.1 IoU edge cases

本地函数得到identical boxes=`1.0`、disjoint=`0.0`、touching edge=`0.0`。该probe验证continuous overlap边界，不验证parser或dataset。

### 17.2 Strict gate 与 lenient parse

| Raw output | Parsed points | `format_pass` |
| --- | --- | --- |
| `<point>[[100,200]]</point>` | `(100,200)` | true |
| `[[100,200]]` | `(100,200)` | false |
| `answer is [100,200]` | `(100,200)` | false |
| `[(100,200)]` | empty | false |

该probe证明“能抽坐标”与“格式合规”不是同一事件，也纠正了把所有裸point形式都视为可恢复的错误假设。

### 17.3 Any-pair Hit 与 set quality

前述two-point probe得到`min=1.414`、Hit@50/100=true，而两个directed means约71.418，说明一个近邻pair即可通过boolean hit。

### 17.4 Field-specific denominator

一个invalid box加一个perfect box得到bool `format_pass=0.5`、`Acc@0.5=0.5`，但numeric `iou_mean=1.0`。metric output必须附每字段count。

### 17.5 MDETR IoU / GIoU discrepancy

偏移框probe在0.5阈值下产生IoU pass、GIoU fail，证明paper文字、打印名称与code function必须同时冻结。

## 18. Typed Metric Manifest 与 Minimum Report

每次evaluation至少输出：

```json
{
  "protocol_id": "sha256:...",
  "sample_id": "...",
  "raw_output": "...",
  "expected_representation": "...",
  "parser_status": {},
  "parsed_prediction": null,
  "gold": null,
  "matching_trace": null,
  "per_sample_metrics": {},
  "included_in_denominators": {},
  "invalid_reason": null
}
```

summary层至少给出每个field的numerator/denominator、invalid/empty/mixed counts、micro与pre-registered macro、slice表、checkpoint与protocol ID。只保存四舍五入scalar，无法重算parser transition、threshold curve、paired difference或bad-case taxonomy。

## 19. Project Truth Boundary 与补证顺序

| 项目口径 | 当前可安全表述 | 当前不能声称 |
| --- | --- | --- |
| Public metrics | 能解释IoU/Acc、RefExp top-k、COCO AP/AR、PCK、mask-hit和fixed-distance Hit的不同合同 | 名称相同即protocol相同 |
| MDETR audit | 固定commit确有GIoU threshold与Precision打印，且可构造IoU/GIoU翻转样本 | 任意其他revision或公开leaderboard都受同一bug影响 |
| OPD parser | 能逐函数说明strict gate与lenient geometry、mixed fallback和field-specific denominator | 当前scorer是严格parser或标准PCK evaluator |
| OPD holdout | inventory记录10k构成、去重/leakage检查和checkpoint-pool metrics | 本页已绑定raw predictions、所有checkpoint hashes或新protocol重跑 |
| Robot claim | static grounding可作为perception诊断 | robot task success、可达性、安全性或OPD单因素因果 |
| Ownership | 能说明repo中观察到的代码与artifact | 候选人亲自设计/实现/跑数，尚需真实口述与commit/日志证据 |

补证顺序：archive raw predictions→冻结sample/image/gold hashes→给现有scorer加golden tests→发布strict parser v2而不覆盖v1→同raw output做paired reconciliation→必要时固定generation config重跑→按representation/slice报告counts与metrics→绑定candidate ownership→最后再接robot episode证据。

## 20. Source Gate 结论与下一 Bounded Slice

本切片已冻结：

1. raw output、strict/lenient parser、tag/syntax/coordinate/geometry status的typed边界；
2. box IoU、Acc@threshold、RefExp Recall@k与COCO AP/AR的非等价合同；
3. PCK的normalization/visibility/correspondence、RoboPoint mask-hit与本地fixed-distance Hit差异；
4. multi-point any-pair、directed coverage、duplicate与matching风险；
5. invalid/empty/mixed的分母和aggregation policy；
6. MDETR paper/code/name discrepancy及五个deterministic probes；
7. 本地OPD scorer逐函数映射、10k holdout现有证据与三口径reconciliation；
8. protocol identity、comparability matrix、typed metric manifest与项目真实性边界。

当前verdict为`WARN`：primary/official/implementation/local code已冻结，但MDETR paper与固定commit存在IoU/GIoU口径差异；本地mixed grounding被当text、parser并非严格、numeric与bool denominator不同；早期point prompt与当前tag/regex不一致；raw predictions、exact checkpoint hashes、parser v2 paired rerun与candidate ownership仍未闭合。

`VLA-PER-010` knowledge与atomic card已在独立bounded slices同步，题卡保持`unseen`。下一bounded slice只冻结`VLA-PER-011` pseudo-label/teacher-noise source；不生成其knowledge/card，不创建`coaching_state.md`，不改变261张题卡的状态。

## References

1. [MDETR v3](https://arxiv.org/abs/2104.12763v3) 与 [mdetr@ea09acc RefExp evaluator](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/datasets/refexp.py)。
2. [COCO API@8c9bcc cocoeval.py](https://github.com/cocodataset/cocoapi/blob/8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9/PythonAPI/pycocotools/cocoeval.py)。
3. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1)。
4. [MPII Human Pose v1](https://arxiv.org/abs/1406.2984v1) 与 [MMPose@759b39 keypoint_eval.py](https://github.com/open-mmlab/mmpose/blob/759b39c13fea6ba094afc1fa932f51dc1b11cbf9/mmpose/evaluation/functional/keypoint_eval.py)。
5. [PER-001 Point / Box / Text Grounding Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.html)。
6. [PER-008 Representation Choice Source Freeze](vol_06_per008_representation_choice_source_freeze.html)。
7. [PER-009 Matching / Negative / Loss Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.html)。
8. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
9. [PER-010 Grounding Metric / Parser / Protocol Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.html)。
10. [PER-010 Grounding Metric / Parser / Protocol Atomic Card](../questions/vol_06_per010.html)。
