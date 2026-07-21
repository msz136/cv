# VOL 06 Perception / Grounding / Navigation：PER-008 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-008`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-008 Representation Choice Knowledge](../knowledge/vol_06_per008_representation_choice.html)；来源边界见 [PER-008 Source Freeze](../sources/vol_06_per008_representation_choice_source_freeze.html)。

## Point / Box / Mask / Keypoint / Affordance 的最小充分选择

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-PER-008</b> · 机器人视觉什么时候该输出 point、box、mask、semantic keypoint 或 affordance？为什么更密不一定更好，OPD 的 affordance point 能说到哪一步？</summary>

**面试意图**：判断你能否从downstream consumer反推最小充分表示，区分几何密度、semantic role与action condition，并守住本地OPD项目证据边界。

**30 秒回答**：我按下游最小充分字段选：定位用point，ROI用box，轮廓/占用用mask，类别级几何角色用带ID与frame的keypoints；绑定动作原语、工具、状态、方向和分数语义才叫affordance。mask→box有损，坐标不能还原语义。OPD仅证明带affordance语义的point监督，不证明dense head或机器人成功。

**机制展开（约 2 分钟）**：先看consumer需要范围、轮廓、语义锚点还是动作条件。point存坐标/mode；box存format/instance；mask存shape/threshold；keypoint增加semantic ID、visibility和frame；affordance再绑定primitive、tool/state、direction、horizon和score语义。`mask→box`只留四个极值，`box→mask`产生新prediction；同一坐标可对应不同role或push/pull。输出继承image/camera/time lineage，保留uncertainty、validity和conversion provenance，仍需PER-015 controller gate。

**诊断 / 证据**：按consumer required-fields→native schema→image/coordinate/time lineage→raw multimodal candidates→conversion trace→parser golden test→matched metric→controller gate检查。matched A/B固定task、data、backbone budget、transform、consumer与protocol，分别报告native质量、invalid/empty、latency/memory、conversion loss和downstream outcome；不能拿不同论文headline metric比较表示优劣。若score含义不清，先区分objectness、mask quality、point hit、ranking score和校准成功概率。

**项目挂钩**：本地`build_prompt_pool.py`把ShareRobot `affordance.{x,y}`缩放为单个`0..1000` point，`point_data_only.py`最终也生成point answer；训练/评估证据是tagged point/box/text generation与static parser/scorer。因此可讲“affordance-labelled point supervision”，不可讲SAM/keypoint pipeline、dense actionability map、primitive/direction success calibration、controller feasibility、robot success或个人ownership。若未来补到真实head/schema，也要先归档revision、raw output、matched ablation与episode bundle。

**追问树**：为什么不用mask统一所有任务？point何时能叫semantic keypoint？affordance point最少还缺哪些字段？SAM mask quality能当抓取成功率吗？mask与box能否互相无损转换？多解point/multimask如何保留？如何设计matched representation ablation？Where2Act score能否跨robot比较？OPD字段名为什么不能证明闭环能力？

**易错点**：按输出密度排性能；把point/keypoint/affordance当同义词；把box填满称为恢复mask；只存payload不存representation/coordinate/score semantics；过早压掉多模态候选；把SAM mask当语义/动作理解；把offline表示质量升级为controller success；用不同任务与metric横比论文数字。

**危险答案**：说“mask信息最多所以任何任务都最好”“keypoint就是point”“affordance就是可交互坐标”“SAM quality就是抓取成功率”“box可以无损恢复mask”“Where2Act分数是任意机器人成功概率”，或“OPD有affordance字段，所以我实现了dense affordance和机器人闭环”。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-008 Representation Choice Knowledge](../knowledge/vol_06_per008_representation_choice.html)：minimum-sufficient选择、五类typed合同、不可逆转换、matched evaluation与项目边界。
2. [PER-008 Representation Choice Source Freeze](../sources/vol_06_per008_representation_choice_source_freeze.html)：RoboPoint、SAM、kPAM、Where2Act与五个本地OPD文件的冻结证据。
3. [RoboPoint v1](https://arxiv.org/abs/2406.10721v1) 与 [official repository](https://github.com/wentaoyuan/RoboPoint/tree/206cb1e086fc3960a8673725a8540766655cd9c5)。
4. [Segment Anything v1](https://arxiv.org/abs/2304.02643v1) 与 [official repository](https://github.com/facebookresearch/segment-anything/tree/dca509fe793f601edb92606367a655c15ac00fdf)。
5. [kPAM v2](https://arxiv.org/abs/1903.06684v2) 与 [official repository](https://github.com/weigao95/kPAM/tree/7214936b619527aee3b02d5306ada15decb95140)。
6. [Where2Act v2](https://arxiv.org/abs/2101.02692v2) 与 [official repository](https://github.com/daerduoCarey/where2act/tree/1daf1a24f7a372599b211108fa851f7ec3581330)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
