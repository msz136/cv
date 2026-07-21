# VOL 06 Perception / Grounding / Navigation：Grounding Metric、Strict Parser 与 Protocol Comparability（PER-010）

> 状态：`drafted / VLA-PER-010 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-001` point/box/text schema、`VLA-PER-008` representation choice；后续：`VLA-PER-011` pseudo-label/noise、`VLA-PER-015` perception→action gate。  
> 来源入口：[PER-010 Grounding Metric / Parser / Protocol Source Freeze](../sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.html)。本页只做已冻结证据的教学转译；atomic card已在独立切片同步并保持`unseen`，真实口述状态仍未开始。

## 问题（Question）

面试官问“你的grounding准确率是多少”时，不能只报一个数字。需要先回答：模型输出是否符合格式、parser如何工作、point/box/mask/keypoint分别用什么metric、invalid与empty是否进入分母、multiple predictions怎样matching，以及两次实验的split/checkpoint/prompt/parser/scorer是否完全可比。

本节点的核心不是多背几个指标名，而是建立一条不会偷换口径的评估链：

```text
raw output
  -> strict parser + typed validity
  -> representation-specific matching
  -> per-sample metric
  -> invalid/empty denominator
  -> aggregation and strata
  -> immutable protocol identity
  -> project claim boundary
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-010负责 |
| --- | --- | --- |
| PER-001 | point/box/text输出schema、坐标范围与basic parser | strict/lenient双轨、invalid taxonomy和metric denominator |
| PER-006 | resize/crop/letterbox、camera与transform lineage | 将这些字段写进protocol identity，不重讲图像变换 |
| PER-007 | open-vocabulary inference、threshold/NMS、phrase与box输出 | scorer怎样读取、match和aggregate输出 |
| PER-008 | point/box/mask/keypoint/affordance表示选择 | 不同表示为什么不能共用同一metric名称 |
| PER-009 | training matcher、negative、loss与reduction | evaluation metric；不把training cost/loss当最终指标 |
| PER-011 | teacher noise、calibration、leakage与curriculum | 只冻结gold/split/scorer身份，不评价teacher可靠性 |
| PER-015 | reachability、uncertainty与action failure gate | 不从static grounding metric推出robot success |
| VOL 05 | 通用置信区间、paired test与评估工程 | grounding特有的parser、matching、representation语义 |

## 1. 30秒直觉：先问“这个数字是怎么产生的”

一个可靠的30秒回答是：

> Grounding评估不是“从文本里抓到坐标就算分”。我先冻结expected representation和strict parser，把tag、syntax、coordinate、geometry四层状态分开；再按box、keypoint或point-set选择IoU、PCK、mask-hit或fixed-distance metric，并预注册invalid/empty分母。最后用dataset、sample IDs、checkpoint、prompt、decode、parser/scorer revision和aggregation生成protocol ID。任何字段不同，数字默认不直接可比。

这段回答主动封住四种常见偷换：格式失败被lenient parser隐藏、metric同名但公式不同、invalid被悄悄drop、不同split/checkpoint被说成单因素提升。

## 2. 评估栈：四层成功不能压成一个`valid`

### 2.1 四层状态

| 层 | 核心问题 | 典型失败 | 是否等于几何错误 |
| --- | --- | --- | --- |
| tag / format | 是否使用要求的`<point>`或`<box>`协议 | missing、mixed、extra tag | 不一定 |
| syntax / parse | 完整字符串是否匹配grammar | trailing prose、wrong arity、ambiguous match | 不一定 |
| coordinate | 数值是否finite、在约定范围、坐标系一致 | NaN、越界、未反归一化 | 不一定 |
| geometry | box是否正面积、集合是否非空、位置是否正确 | degenerate box、empty、large error | 是最终几何层 |

同一个输出可能“坐标几何正确但格式失败”，也可能“tag正确但坐标越界”。如果只保存`valid=false`，后续无法判断是instruction following、parser compatibility、preprocess还是vision localization问题。

### 2.2 Typed record

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

工程上必须保存`raw_output`，否则parser升级后无法在同一generation上做paired reconciliation，只能重新推理并同时引入decode或runtime差异。

## 3. Strict Parser 与 Lenient Diagnostic 必须双轨

### 3.1 Strict的含义

strict parser应对完整字符串做`fullmatch`，而不是在任意prose里搜索数字。示意grammar为：

```text
# Point and box outputs must occupy the complete response.
point       = "[", number, ",", number, "]" ;
point_out   = "<point>", "[", point, {",", point}, "]", "</point>" ;
box_out     = "<box>", "[", number, ",", number, ",", number, ",", number, "]", "</box>" ;
```

grammar通过后还要检查finite、0..1000范围、box的\(x_2>x_1,y_2>y_1\)、空集合、重复tag和mixed representation。strict score衡量“模型能否按部署合同输出”。

### 3.2 Lenient的用途

lenient parser只回答诊断问题：格式错时是否仍存在可恢复几何。它可用于构造如下transition matrix：

| Strict | Lenient geometry | 解释 |
| --- | --- | --- |
| pass | pass | 格式与几何都正确 |
| fail | pass | 可能是instruction following或parser mismatch |
| pass | fail | tag/grammar通过但几何无效 |
| fail | fail | 格式与几何均失败，仍需看invalid reason |

不能只发布lenient数字，也不能用它覆盖历史strict结果。正确做法是发布新的parser revision和protocol ID，并保留old/new paired结果。

## 4. 本地OPD Parser到底做了什么

冻结的`eval_qwen_vl_raw_holdout.py`不是纯strict parser，而是“tag gate + lenient geometry extraction + format-specific scoring”：

1. gold只含`<point>`时路由point，只含`<box>`时路由box；两者都有变成`mixed_grounding`，但没有专门scoring branch，最终落到text；
2. `parse_points`从任意文本搜索`[x,y]`，不要求坐标位于`<point>`内；
3. `parse_box`依次尝试flat tagged box、tag内部前四个数字、文本中的前两个point pairs；
4. `format_pass`另行要求对应tag与坐标合法，因此几何可能有分但格式失败；
5. text branch无条件`format_pass=true`，使mixed grounding的结构错误被隐藏。

确定性probe：

| Raw output | 可抽取point | `format_pass` |
| --- | --- | --- |
| `<point>[[100,200]]</point>` | 是 | true |
| `[[100,200]]` | 是 | false |
| `answer is [100,200]` | 是 | false |
| `[(100,200)]` | 否 | false |

这也说明早期prompt若要求`[(x,y)]`，不能简单说“strict为0只是缺tag”：当前regex连圆括号pair都无法恢复。需要先在raw outputs上做版本化parser reconciliation。

## 5. Box：IoU、Mean IoU 与 Acc@IoU

对corner boxes \(A,B\)，axis-aligned IoU为：

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A|+|B|-|A\cap B|}.
\]

变量解释：\(|A\cap B|\)是intersection area，分母是union area；实现映射到本地`box_iou`的intersection clamp、area与union计算。直觉上它是单对框的连续overlap，不含dataset aggregation，也不判断输出格式。

阈值准确率为：

\[
\operatorname{Acc@IoU}(\tau)=\frac{1}{N}\sum_{i=1}^{N}
\mathbf 1\!\left[\operatorname{IoU}(\hat b_i,b_i)\ge\tau\right].
\]

变量解释：\(\tau\)是overlap threshold，\(N\)必须明确是全部box样本还是valid-parsed subset。本地`Acc@0.3/0.5/0.75`将invalid prediction记为false并除全部box pool；`iou_mean`却只平均存在finite IoU的样本，所以两者分母不同。

边界probe：identical boxes的IoU为1，disjoint为0，touching edge也为0。`Acc@0.5=0.52`不代表mean IoU为0.52；改变`>=`、坐标逆变换、box order、parser或invalid policy都会改数字。

## 6. Referring-expression Recall@k：先冻结Overlap函数

one-expression/one-target场景常写为：

\[
R@k(\tau)=\frac{1}{N}\sum_{i=1}^{N}
\mathbf 1\!\left[
\max_{j\le k}O(\hat b_{i,j},b_i)\ge\tau
\right].
\]

变量解释：\(k\)是取score排序后的top-k boxes，\(O\)必须明确是IoU、GIoU或其他overlap，\(N\)是expression数量。直觉上它问“top-k里是否至少有一个命中”，不是检测任务完整的precision–recall curve。

### 6.1 MDETR的revision trap

MDETR v3论文描述IoU-based Recall@k；固定commit `ea09acc...`的`RefExpEvaluator`实际调用`generalized_box_iou`，以0.5阈值判定，并打印`Precision @ 1,5,10`。下面的反例会翻转结论：

```text
A = [0, 0, 2, 2]
B = [0.34, 0.34, 2.34, 2.34]
IoU  = 0.5254366562  -> pass at 0.5
GIoU = 0.4832129730  -> fail at 0.5
```

面试中最有价值的不是背“MDETR用Recall@1”，而是主动说：paper table、code revision、overlap function和打印名称必须绑定，否则同名scalar可能不是同一protocol。

## 7. COCO AP / AR 为什么不能和RefExp R@k互换

冻结COCO API detection defaults包含：

| 维度 | 默认合同 |
| --- | --- |
| IoU thresholds | 0.50到0.95，步长0.05，共10个 |
| recall positions | 0到1，步长0.01，共101个 |
| max detections | 1、10、100 |
| precision tensor | `[T,R,K,A,M]` |
| recall tensor | `[T,K,A,M]` |
| matching | score排序后按image/category/threshold匹配，处理ignore/crowd/area |
| absent category | 保存为`-1`，summary时排除 |

COCO AP汇总precision–recall envelope，AR也绑定IoU grid、area、category与`maxDets`。RefExp R@k通常对每个expression做一次binary success。两者的统计单元、ranking、matching和denominator都不同；都含“recall”不代表可比较。

## 8. Point Metrics：PCK、Mask-hit 与 Fixed-distance Hit

### 8.1 PCK需要correspondence与normalization

常见normalized keypoint hit可写为：

\[
h_{n,k}(\tau)=
\mathbf 1\!\left[
\left\|\frac{\hat p_{n,k}-p_{n,k}}{s_n}\right\|_2<\tau
\right],
\qquad m_{n,k}=1.
\]

变量解释：\(\hat p_{n,k},p_{n,k}\)是有语义对应的pred/GT keypoint，\(s_n\)是bbox、head或H/W normalization factor，\(m_{n,k}\)是visibility mask。冻结MMPose实现逐维除`norm_factor`、忽略invisible target，并先对每个keypoint type求accuracy再做macro average。直觉上PCK比较的是“相对于对象尺度是否足够近”，不是固定坐标距离。

普通grounding point set若没有keypoint identity，就不能直接套PCK；必须先冻结nearest-neighbor、Hungarian或semantic correspondence。

### 8.2 RoboPoint mask-hit

RoboPoint v1的spatial-affordance accuracy可写为：

\[
\operatorname{MaskHit}=\frac{1}{|P|}\sum_{p\in P}\mathbf 1[p\in M].
\]

变量解释：\(P\)是预测点集合，\(M\)是target mask。它是prediction precision-like度量：一个位于mask内的点就可能得到高分，却不保证覆盖全部target modes，也不等于PCK或GT recall。

### 8.3 本地fixed-coordinate any-pair Hit

本地OPD定义：

\[
d_{\min}=\min_{p\in P,g\in G}\lVert p-g\rVert_2,
\qquad
\operatorname{Hit@r}=\mathbf 1[d_{\min}\le r],
\quad r\in\{50,100\}.
\]

变量解释：\(P,G\)是0..1000规范坐标中的pred/GT point sets；没有image diagonal、bbox或object-size normalization。它只问“是否存在至少一对点足够近”，因此应完整称为`fixed-coordinate any-pair Hit@50/100`，不要简称PCK。

## 9. Multi-point：一个最近点不能代表集合质量

本地还计算两个directed nearest-neighbor mean：

\[
d_{P\to G}=\frac{1}{|P|}\sum_{p\in P}\min_{g\in G}\lVert p-g\rVert_2,
\qquad
d_{G\to P}=\frac{1}{|G|}\sum_{g\in G}\min_{p\in P}\lVert g-p\rVert_2.
\]

变量解释：\(d_{P\to G}\)更接近prediction purity，\(d_{G\to P}\)更接近GT coverage；两者都允许many-to-one，duplicate不会增加coverage。实现映射到本地两个nearest-neighbor list mean。

对`P={(0,0),(1000,1000)}`、`G={(1,1),(900,900)}`，最小距离为1.414，所以Hit@50/100均通过；但两个directed means约71.418。应联合报告point counts、count difference、两个directed means与task-specific coverage；若任务要求一一对应，再引入带unmatched penalty的bipartite matching。

## 10. Invalid、Empty 与 Denominator 是Metric的一部分

### 10.1 先写policy，再跑scorer

| 情况 | 推荐strict主口径 | 本地当前行为 |
| --- | --- | --- |
| 缺tag但坐标可抽 | format fail；几何另作diagnostic | format false，仍可能算geometry |
| out-of-range point | coordinate fail | coord false，但非空时仍可能算distance |
| invalid/degenerate box | bool hit=false，numeric undefined | Acc fields false，IoU/center为`None` |
| empty prediction | explicit empty fail | Hit false，numeric distance为`None` |
| mixed point+box | 单独schema或拒绝 | 落入text，format被记true |
| duplicate points | 预注册dedup或precision penalty | 保留并影响count与pred→gold mean |

### 10.2 分母反例

本地`Metrics.summary`对bool字段除全部pool样本数，对numeric字段只除finite value count。一个invalid box加一个perfect box会得到：

```text
format_pass = 0.5
Acc@IoU0.5 = 0.5
iou_mean    = 1.0
```

这三个数都符合当前代码，但`iou_mean=1.0`若不附`valid_iou_count=1/2`就会误导。minimum report必须给每个field的numerator、denominator与invalid reason counts。

## 11. Aggregation：Micro、Macro 与Episode不是一回事

| Aggregation unit | 含义 | 风险 |
| --- | --- | --- |
| sample micro | 每条prompt/sample等权 | 多prompt image可能权重过大 |
| image | 同图多个prompt先聚合 | 需要定义图内规则 |
| category/task macro | 各类或各representation等权 | 小slice方差大，需附count/CI |
| keypoint type macro | 每类keypoint先跨instance聚合 | 不等于visible joints micro average |
| robot episode | 一次closed-loop任务为单位 | static image metric无法替代 |

本地10k holdout由6,100 box、1,400 point、2,500 text组成。一个overall average容易被pool比例主导，所以至少按representation、object size、point count、prompt template、source dataset、validity reason和checkpoint分层。

## 12. Protocol Identity：什么时候两个数字可比较

最小protocol manifest应包含：

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

canonical serialization后计算SHA-256得到protocol ID。判断规则：

| 差异 | 结论 |
| --- | --- |
| manifest相同，只改变seed | 可做paired或multi-seed比较 |
| 同raw predictions，发布strict parser v2并同时跑v1/v2 | 条件可比；可隔离parser effect |
| IoU改GIoU、threshold或`>=`改`>` | 不直接可比 |
| invalid由false改为drop | 不直接可比，denominator变了 |
| fixed Hit改PCK或mask-hit | 不可比，问题定义变了 |
| split、prompt、checkpoint、transform同时改变 | 不能做单因素归因 |
| static holdout改robot success | 不可比，evaluation unit与闭环语义不同 |

## 13. 可审计Scoring伪代码

```python
def evaluate_row(row, protocol):
    # 1. Keep raw output and freeze the expected representation from the gold schema.
    raw = row["raw_output"]
    expected = protocol.expected_representation(row["gold"])

    # 2. Run the full-match strict parser and preserve typed failure reasons.
    strict = protocol.strict_parser.parse(raw, expected)

    # 3. Run lenient recovery only as a separate diagnostic channel.
    diagnostic = protocol.lenient_parser.parse(raw, expected)

    # 4. Apply the pre-registered invalid/empty policy before aggregation.
    if not strict.is_valid:
        metric = protocol.invalid_policy.score_failure(expected, strict.reason)
    else:
        # 5. Match predictions to targets using the representation-specific rule.
        matching = protocol.matcher.match(strict.value, row["gold"])
        metric = protocol.metric.compute(matching)

    # 6. Persist per-field denominator inclusion; never save only a rounded scalar.
    return {
        "sample_id": row["sample_id"],
        "raw_output": raw,
        "strict_status": strict.to_dict(),
        "lenient_diagnostic": diagnostic.to_dict(),
        "per_sample_metric": metric.values,
        "included_in_denominators": metric.denominator_flags,
        "protocol_id": protocol.sha256,
    }
```

这是评估合同伪代码，不是本地scorer的直接API。关键是raw preservation、strict/lenient分流、invalid policy先于summary、matching依representation选择，以及每个field保存denominator inclusion。

## 14. 本地OPD三口径Reconciliation

现有inventory记录：raw holdout 10,000条、8,251 unique images，box/point/text分别6,100/1,400/2,500；fingerprint、source-line、image+prompt+answer重复为0，与train image交集为0。OPD5000 checkpoint 5000的已记录数字包括Box Acc@0.5 `0.5238`、Point Hit@50/100 `0.7493/0.8729`、Text exact `0.8724`，但不同pool最佳checkpoint不同。

这些数字只支持冻结inventory中的static holdout语境。下一次评估必须分三栏：

1. **original strict**：原prompt、原parser、原scorer，保留历史可复现性；
2. **protocol-fixed strict**：修复prompt/parser合同，发布新protocol ID；
3. **lenient geometry diagnostic**：同raw outputs上做恢复分析，不替换主指标。

最可信的证据顺序是：归档raw predictions与checkpoint/generation config→同raw output跑parser v1/v2→输出paired transition matrix→必要时再固定decode重新generation。`strict=0`不等于几何能力为0，lenient较高也不能抹去部署格式失败。

## 15. Failure Taxonomy 与诊断顺序

| 失败层 | 症状 | 常见根因 | 首个检查 |
| --- | --- | --- | --- |
| schema | point/box/text路由异常 | gold tag或mixed representation | expected-format counts + raw gold |
| parser | strict低、lenient高 | prompt/tag/grammar mismatch | raw output + parser golden tests |
| coordinate | 大量越界或退化box | transform/normalization/order错 | pre/post image transform与range |
| matching | point-set score异常乐观 | any-pair minimum、duplicates | pairwise distance matrix + counts |
| metric | paper与code数字对不上 | IoU/GIoU、threshold或name drift | exact scorer function/revision |
| denominator | mean很高但valid很少 | numeric drop、invalid exclusion | numerator/denominator per field |
| aggregation | overall升而point降 | pool比例或micro/macro变化 | representation-stratified table |
| protocol | “改了一个点”但多项变化 | split/checkpoint/prompt/decode漂移 | two protocol manifests diff |
| project claim | static metric被说成robot成功 | evaluation unit越界 | episode/controller evidence gate |

推荐顺序：schema→raw parser cases→coordinate transform→pairwise matching→metric function→denominator→aggregation→protocol diff→project claim。先查合同，通常比先调threshold更能定位根因。

## 16. 面试回答模板、追问与危险答案

### 16.1 两分钟结构化回答

1. 先说parser是metric的一部分，并拆tag/syntax/coordinate/geometry；
2. 给出strict主口径与lenient diagnostic双轨；
3. 按representation说明IoU/Acc、RefExp R@k、PCK、mask-hit、fixed Hit的不同问题；
4. 主动说明invalid/empty、matching与field-specific denominator；
5. 用protocol manifest判断两次结果是否可比；
6. 落到本地OPD code：mixed fallback、regex、any-pair hit和numeric denominator；
7. 最后把static holdout与robot success、因果提升、ownership分开。

### 16.2 高频追问

| 追问 | 回答抓手 |
| --- | --- |
| 为什么parser也算metric protocol？ | raw→typed prediction决定哪些样本与几何进入scorer |
| 格式错但坐标对，算不算正确？ | strict主指标失败；lenient另报diagnostic，不静默替换 |
| Mean IoU与Acc@0.5区别？ | 连续overlap mean vs thresholded sample success，分母也可能不同 |
| Recall@1一定是IoU@0.5吗？ | 不一定；要问overlap、threshold、ranking、GT unit与code revision |
| PCK与Hit@50一样吗？ | 不一样；PCK有normalizer、visibility与correspondence |
| 多点只看min distance有什么问题？ | 一个近邻pair可通过，无法反映purity/coverage/duplicates |
| invalid prediction要不要drop？ | 预注册；部署主口径通常应失败计入，numeric可undefined但必须附count |
| overall metric为什么危险？ | box/point/text pool比例与aggregation unit可能掩盖slice回退 |
| 何时能说新模型提升？ | protocol manifest相同或差异被隔离，并绑定raw predictions/checkpoint |
| static grounding高能否说明机器人成功？ | 不能；还缺reachability、controller、闭环episode与failure semantics |

### 16.3 危险答案

- “能从文本里抓到数字就算格式正确”；
- “IoU、Acc@0.5、Recall@1和AP都是定位准确率，差不多”；
- “Hit@50就是PCK@50”；
- “invalid样本删掉即可，不影响比较”；
- “同一指标名就能横向比较”；
- “MDETR官方就是固定用IoU/GIoU中的某一个”，却不绑定paper/code revision；
- “point Hit提高，所以机器人操作成功率提高”；
- “我实现了严格评估器”，但本地代码仍有mixed→text和lenient fallback。

## 17. Project Truth Boundary 与两个项目Hook

| 项目Hook | 当前可安全表述 | 当前不能声称 |
| --- | --- | --- |
| OPD direct evidence | 能逐函数解释point/box/text routing、tag gate、lenient parse、IoU/Hit、mixed fallback与field-specific denominator；inventory记录10k holdout构成和限定metrics | scorer是标准PCK/RefCOCO evaluator；raw predictions/checkpoint hashes已闭合；OPD单因素因果；候选人ownership |
| Robot Harness / downstream interface | grounding metric可作为perception diagnostic；进入controller前仍需PER-015 reachability/action gate与episode protocol | static holdout数字等于closed-loop manipulation/navigation success，或已有local-direct navigation bundle |

补证优先级：raw predictions→sample/image/gold hashes→parser golden tests→strict parser v2→old/new paired matrix→fixed generation rerun→representation-stratified report→candidate ownership→最后连接controller/episode证据。

## 18. 结论与下一步

PER-010的核心是：metric从raw output进入parser时已经开始。strict与lenient必须双轨，tag/syntax/coordinate/geometry必须typed；IoU、Acc、RefExp R@k、COCO AP/AR、PCK、mask-hit和fixed-distance Hit回答不同问题；invalid、empty、matching、denominator和aggregation都属于protocol，而不是报告阶段的可选细节。

本地OPD可以安全讲清parser/scorer的真实代码、10k holdout inventory和三口径reconciliation方案，但不能把当前fixed-distance Hit叫PCK，不能把lenient geometry覆盖strict failure，也不能从static holdout推出robot success或个人贡献。由于raw predictions、checkpoint hashes、strict parser v2 paired rerun和ownership仍缺，本节点保持`WARN`。

当前PER-010 source、knowledge与atomic card已同步；全局261张题卡全部保持`unseen`。下一bounded slice只冻结`VLA-PER-011` pseudo-label/teacher-noise source；不生成其knowledge/card，不创建`coaching_state.md`，不改变任何既有题卡状态。

## References

1. [PER-010 Grounding Metric / Parser / Protocol Source Freeze](../sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.html)。
2. [MDETR v3](https://arxiv.org/abs/2104.12763v3) 与 [mdetr@ea09acc RefExp evaluator](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/datasets/refexp.py)。
3. [COCO API@8c9bcc cocoeval.py](https://github.com/cocodataset/cocoapi/blob/8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9/PythonAPI/pycocotools/cocoeval.py)。
4. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1)。
5. [MPII Human Pose v1](https://arxiv.org/abs/1406.2984v1) 与 [MMPose@759b39 keypoint_eval.py](https://github.com/open-mmlab/mmpose/blob/759b39c13fea6ba094afc1fa932f51dc1b11cbf9/mmpose/evaluation/functional/keypoint_eval.py)。
6. [PER-001 Point / Box / Text Grounding](vol_06_per001_grounding_coordinate.html)。
7. [PER-008 Representation Choice](vol_06_per008_representation_choice.html) 与 [PER-009 Matching / Negative / Loss](vol_06_per009_grounding_matching_negative_loss.html)。
8. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
9. [VOL 06 Coverage-Gap Audit](../sources/vol_06_perception_grounding_navigation_coverage_gap_audit.html)。
10. [PER-010 Atomic Card](../questions/vol_06_per010.html)。
