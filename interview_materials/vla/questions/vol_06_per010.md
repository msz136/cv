# VOL 06 Perception / Grounding / Navigation：PER-010 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-010`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-010 Grounding Metric / Parser / Protocol Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.html)；来源边界见 [PER-010 Source Freeze](../sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.html)。

## Grounding Metric、Strict Parser 与 Protocol Comparability

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-PER-010</b> · Grounding评估时，strict parser、IoU/PCK/Recall和protocol comparability该怎么讲？为什么本地OPD的Hit@50/100不能直接叫PCK？</summary>

**面试意图**：判断你能否把parser、validity、matching、metric、denominator和aggregation连成可复现合同，识别同名指标的口径漂移，并守住本地OPD静态评估的项目证据边界。

**30 秒回答**：我把parser纳入metric：拆格式/语法/坐标/几何，strict主评、lenient仅诊断；再按表示选IoU、R@k、PCK或mask-hit，固定invalid与分母。跨实验还要对齐数据、checkpoint、prompt、scorer和聚合。OPD Hit@50/100只是在规范坐标中找最近点对，没有PCK的尺度归一化、可见性和点对应，不能混称。

**机制展开（约 2 分钟）**：输出先按预期表示完整匹配，分开记录格式、语法、坐标、几何；宽松恢复另栏。IoU是单框连续重叠，Acc@τ是阈值样本率；RefExp R@k还绑定top-k排序、重叠函数和GT单元，COCO AP/AR另含阈值网格、匹配、面积和maxDets。PCK需点对应、尺度、阈值、可见性；mask-hit以预测点为分母。本地Hit只取任意预测—GT最小距离，一个近邻即可通过。若invalid的布尔项记false而数值项跳过，会出现Acc=.5但IoU均值=1，因此每字段须报分子/分母。最后把数据、checkpoint、prompt/decode、transform、parser/scorer、matching、threshold和aggregation写入protocol ID。

**诊断 / 证据**：依次查expected-format与raw gold→strict/lenient golden cases→transform与坐标范围→pairwise box/point matrix→overlap/matching函数和threshold→invalid/empty/duplicate policy→每字段numerator/denominator→micro/macro与slice→两份protocol manifest diff→checkpoint/raw prediction绑定。确定性probe应覆盖identical/disjoint/touching IoU、tagged/bare/prose/圆括号point、任意点对Hit与双向mean、invalid+perfect box分母，以及MDETR IoU=.525/GIoU=.483的0.5判定翻转。

**项目挂钩**：本地`eval_qwen_vl_raw_holdout.py`会全局抓`[x,y]`，box还可从tag内数字或前两个point pairs恢复；format gate与geometry score分离，`mixed_grounding`却落入text，bool rate除全pool而numeric mean跳`None`。inventory记录10k静态holdout与限定pool metrics，但raw predictions、exact checkpoint hashes和parser-v2 paired rerun未归档。因此只能讲original-strict / protocol-fixed-strict / lenient-diagnostic三口径方案，不能把Hit叫标准PCK、把静态分数升级为robot success、单因素因果或个人ownership。

**追问树**：格式错但坐标对算不算正确？Mean IoU和Acc@0.5有什么区别？Recall@1一定用IoU吗？MDETR论文与代码为什么会翻转判定？COCO AR与RefExp R@k能否比较？PCK最少要冻结哪些字段？mask-hit偏precision还是recall？多点min distance为何乐观？invalid该drop还是记false？同raw output换parser怎样公平比较？static grounding高能否说明robot success？

**易错点**：把regex抽取当strict parse；用一个`valid`吞掉四层状态；混用IoU、Acc、R@k、AP/AR；把fixed Hit叫PCK；忽略point correspondence与normalizer；只报numeric mean不报valid count；把invalid静默drop；只凭指标名横比；整体平均掩盖box/point/text slice；把parser修复、checkpoint和prompt同时变化说成单因素提升。

**危险答案**：说“能抓到坐标就算格式正确”“IoU、Recall@1和AP都是定位准确率，直接比较即可”“Hit@50就是PCK@50”“invalid删掉不影响结果”“MDETR官方固定用某个overlap，不必绑定revision”“OPD point分数高证明机器人操作成功”，或“我实现了严格scorer”，却不提mixed→text、lenient fallback和字段分母差异。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-010 Grounding Metric / Parser / Protocol Knowledge](../knowledge/vol_06_per010_grounding_metric_parser_protocol.html)：四层validity、metric family、protocol identity、伪代码、failure taxonomy与项目边界。
2. [PER-010 Source Freeze](../sources/vol_06_per010_grounding_metric_parser_protocol_source_freeze.html)：MDETR、COCO API、RoboPoint、MMPose、本地evaluator/inventory与deterministic probes。
3. [MDETR v3](https://arxiv.org/abs/2104.12763v3) 与 [fixed RefExp evaluator](https://github.com/ashkamath/mdetr/blob/ea09acc44ca067072c4b143b726447ee7ff66f5f/datasets/refexp.py)。
4. [COCO API cocoeval.py](https://github.com/cocodataset/cocoapi/blob/8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9/PythonAPI/pycocotools/cocoeval.py)。
5. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1)。
6. [MMPose keypoint_eval.py](https://github.com/open-mmlab/mmpose/blob/759b39c13fea6ba094afc1fa932f51dc1b11cbf9/mmpose/evaluation/functional/keypoint_eval.py)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
