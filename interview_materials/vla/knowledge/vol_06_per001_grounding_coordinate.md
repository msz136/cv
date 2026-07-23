# VOL 06 Perception / Grounding / Navigation：Point、Box、Text 与坐标协议（PER-001）

> 状态：`drafted / VLA-PER-001 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[PER-001 Grounding / Coordinate Source Freeze](../sources/vol_06_per001_grounding_coordinate_source_freeze.html)。  
> 项目入口：[OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

## 问题（Question）

VLA 或 VLM grounding 面试不能只回答“模型找到了目标”。一个可执行的 grounding 输出必须同时说明：目标是什么、坐标在哪个空间、输出如何解析、怎样逆变换回原图，以及下游是否把它当作静态评估、规划输入还是控制 action。

本页回答五个问题：

1. point、box、text 三种 grounding 输出有什么不同？
2. `normalized cxcywh` 如何转换为 pixel `xyxy`，resize/letterbox 为什么会改变结果？
3. strict parser、lenient parser 和 protocol-fixed scorer 应怎样分层？
4. grounding score 为什么不能直接等价为 action success？
5. 如何把这些合同映射到 OPD 的五 expert、point protocol 和 raw-holdout 证据？

## 知识地图位置与前置依赖

```text
VOL 01 坐标系 / 几何 / 图像尺寸
          ↓
PER-001 point-box-text contract
          ↓
PER-002 3D lift / camera calibration
          ↓
PER-003 multi-view fusion / temporal grounding
          ↓
VLA action head / planner / controller / closed-loop evaluation
```

前置知识是图像尺寸、坐标系、归一化和 parser 基础；后续节点将讨论深度、内外参、多视角融合和导航。Grounding DINO 和 RoboPoint 是公源机制参照，OPD 是项目证据 hook，不把项目数字当成通用算法结论。

## 1. 30 秒直觉：grounding 是接口合同，不是一个分数

grounding 的输出要像一个带 schema 的消息：`target`、`representation`、`coordinate_space`、`image_size`、`values`、`confidence`、`validity` 和 `parser_version`。同样四个数字，可能是 normalized `cxcywh`，也可能是 pixel `xyxy`；同样一串点，可能是部署要求的 `<point>...</point>`，也可能只是 lenient parser 接受的 Python 风格字符串。若这些字段不固定，IoU 或 Hit@threshold 的变化无法判断来自模型、预处理、解析还是坐标换算。

## 2. 三类输出合同

### 2.1 Box：目标区域

| 表示 | 例子 | 需要绑定 | 典型风险 |
| --- | --- | --- | --- |
| normalized `cxcywh` | `(0.50, 0.40, 0.20, 0.10)` | 原图宽高、中心/尺寸语义、范围 `[0,1]` | 当成角点或使用错误宽高缩放 |
| pixel `xyxy` | `(x_min,y_min,x_max,y_max)` | 原点、边界是否 inclusive、rounding | x/y 交换、越界、IoU 改变 |
| normalized `xyxy` | 四个相对角点 | normalization 轴、裁剪/填充规则 | 直接乘错 `W/H` |
| camera/world box | 2D 区域加深度或平面假设 | intrinsics、extrinsics、深度来源、frame ID | 把 2D 区域中心当成 3D 抓取点 |

Grounding DINO frozen inference code 给出一个具体实现：模型输出 `pred_boxes` 后先乘 `[W,H,W,H]`，再用 `box_convert(..., in_fmt="cxcywh", out_fmt="xyxy")`。这说明代码路径，但不说明任何自定义模型已经遵守同一合同。

### 2.2 Point：位置或 affordance

point 可以是目标中心、抓取候选、导航 waypoint 或 RoboPoint 风格的 spatial affordance keypoint。至少要记录：

```text
(x, y), coordinate_space, image_width, image_height,
ordering, confidence, valid, parser_version
```

`<point>[[x1,y1],[x2,y2]]</point>`、`[(x1, y1), ...]` 和 JSON `{"points": ...}` 是三个不同的接口。多点输出还要定义顺序：按置信度、从左到右、沿轨迹，还是无序集合。顺序不清时，几何误差可能看似相同，但下游动作会执行到不同的点。

### 2.3 Text：语言标签或 phrase grounding

文本输出不能只保存最终字符串。应区分原始 phrase、规范化 label、token span、confidence、与 box/point 的关联，以及 `no-object`/`ambiguous` 状态。Grounding DINO 的 phrase extraction 使用 tokenized caption 和 text threshold；因此 phrase 命中不等于目标绑定正确，也不等于 action head 已消费该结果。

## 3. 坐标变换：先声明假设，再写公式

令原图宽高为 \((W,H)\)，模型输出 normalized `cxcywh=(c_x,c_y,w,h)`。当没有裁剪或 padding 时，一种明确的 pixel `xyxy` 转换是：

\[
x_1=W\left(c_x-\frac{w}{2}\right),\qquad
y_1=H\left(c_y-\frac{h}{2}\right),\qquad
x_2=W\left(c_x+\frac{w}{2}\right),\qquad
y_2=H\left(c_y+\frac{h}{2}\right).
\]

这里的 \((c_x,c_y,w,h)\) 是相对于原图的归一化量；公式只负责尺度和参数化，不负责 letterbox padding、crop offset、相机外参、深度或控制器 frame。代码实现必须保留 transform metadata，否则只能得到“看起来在图上”的框。

若预处理先把原图缩放为 \((sW,sH)\)，并在左、上方向加入 padding \((p_x,p_y)\)，则模型坐标到预处理图坐标的框为：

\[
(x'_1,y'_1,x'_2,y'_2)=(s x_1+p_x,;s y_1+p_y,;s x_2+p_x,;s y_2+p_y).
\]

逆变换必须执行 \(x=(x'-p_x)/s,\;y=(y'-p_y)/s\)，并在最终 rounding 前裁剪到原图边界。若把 \((p_x,p_y)\) 忽略，目标会随横纵比变化系统性偏移；这不是模型“空间理解变差”的充分证据。

## 4. 评估指标与证据阶梯

### 4.1 Box IoU

两个二维框 (A,B) 的交并比为：

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}.
\]

IoU 只描述平面区域重叠；要报告阈值、样本数、空预测处理、坐标协议和 scorer 版本。它不包含动作单位、控制延迟、碰撞、接触稳定性或任务 success predicate。

### 4.2 Point Hit@threshold

point 指标应明确距离单位：像素距离、归一化距离还是相机/世界坐标距离。`Hit@50` 与 `Hit@100` 只有在图像尺寸、有效样本、parser mode 和距离定义都固定时才可比较。strict parser=0 可能是格式不匹配；lenient parser 的提升只能说明兼容格式的几何估计，不可自动替代部署协议。

### 4.3 Text / phrase score

text exact、token overlap、phrase grounding accuracy 和 box/point pairing 是不同指标。字符串正确但坐标错，或者坐标正确但标签格式不符，都会在不同 scorer 下产生相反结论。因此结果表必须按 representation 和 protocol 分栏，不能把所有输出平均成一个“grounding accuracy”。

## 5. 一个可审计的 grounding pipeline

```python
def ground_and_validate(image, prompt, model, contract):
    # 1. Preserve the original image size and reversible preprocess metadata.
    preprocessed, transform = preprocess(image, contract.resize_policy)

    # 2. Run the model; output type is explicit, not inferred from four numbers.
    raw = model(preprocessed, prompt)
    parsed = parse_output(raw, contract.parser_version)

    # 3. Reject malformed or ambiguous outputs before any coordinate transform.
    validate_representation(parsed, contract.representation,
                            contract.coordinate_space, contract.value_range)

    # 4. Undo padding/crop/resize and clip only under the declared policy.
    original_space = inverse_transform(parsed, transform)
    original_space = clip_or_reject(original_space, contract.boundary_policy)

    # 5. Emit an auditable record for scorer and downstream planner/controller.
    return {
        "target": parsed.target,
        "representation": contract.representation,
        "coordinate_space": "original_pixel",
        "values": original_space.values,
        "confidence": parsed.confidence,
        "valid": parsed.valid,
        "parser_version": contract.parser_version,
        "transform_id": transform.id,
    }
```

伪代码的关键是先解析和验证，再做逆变换；不能看到四个浮点数就直接 reshape。真正进入 action head 前，还需增加深度/外参、frame ID、单位和 controller schema 检查。

## 6. 从 grounding 到 action：中间接口不能省略

```text
grounding output
  → representation parser
  → original-image coordinate
  → camera/world lift (optional)
  → target/affordance selection
  → policy observation or planner goal
  → normalized action + denormalization
  → controller / safety predicate
```

这里至少有三个不同的成功事件：

1. **grounding valid**：格式、范围和坐标合同通过；
2. **geometric match**：IoU/Hit/距离达到 scorer 阈值；
3. **task success**：规划器、控制器和环境 predicate 均通过。

第 1、2 层通过不能推出第 3 层。尤其是 point 中心不一定是抓取点，box 不含深度和遮挡信息，text label 也不包含动作方向或接触力。

## 7. OPD 项目映射与真实性边界

| OPD 证据 | 面试可说 | 不能升级为 |
| --- | --- | --- |
| 五 expert mix：reasoning/object/region/spatial/point | 数据构造显式分域，point/box/text 有不同 route | 五个 expert 已分别独立最优或 route 已是 learned router |
| `target_expert` / `candidate_experts` / format-conflict metadata | 路由监督和协议边界被写入样本 | student 一定在推理时选择正确 expert |
| raw-holdout dedupe audit | 可审计 image/fingerprint/source-line/prompt-answer-image leakage gate | 静态 holdout 等价真实机器人泛化 |
| original strict / protocol-fixed strict / lenient point scorer | 能区分格式失败和几何能力 | strict=0 直接等于模型不会 point grounding |
| by-format / by-pool checkpoint table | 结果必须绑定 checkpoint、子集和 scorer，且最佳点可能不同 | ckpt5000 是所有任务池全局最佳，或提升由 OPD 单独造成 |

项目材料支持的是数据路由、协议核对和评估边界；模型权重、完整 raw predictions、单因素 ablation 和逐文件 ownership 仍缺，题卡和口述应保持 `WARN/unseen`。

## 8. Trade-off 与高概率 bad case

| 决策 | 好处 | 风险 / 诊断 |
| --- | --- | --- |
| strict parser | 部署协议稳定、失败可见 | 格式错误会掩盖几何能力；需 protocol-fixed 对照 |
| lenient parser | 兼容历史输出、适合定位 parser bug | 可能接受错误 axis/unit，不能作为生产 scorer |
| normalized coordinates | 跨分辨率方便 | 忘记 padding/crop 或 `W/H` 轴会产生系统偏移 |
| pixel coordinates | 直观、易画框 | 强依赖 image size、resize 和 rounding |
| point affordance | 比 box 更接近抓取/导航候选 | 单点不含深度、姿态、遮挡与接触语义 |
| 多点候选 | 可表达路径/抓取备选 | 顺序、去重、置信度和下游选择必须固定 |

常见 bad case：把 `cxcywh` 当 `xyxy`；x/y 乘错图像尺寸；忽略 letterbox offset；用字符串命中代替 phrase grounding；strict=0 就断言能力为零；用 IoU/Hit 推断 controller success；把 OPD 的组合结果写成单一 OPD uplift；把 Git author 当作完整 ownership。

## 9. 面试回答检查表

回答 PER-001 时至少覆盖：

1. 表示：point、box、text 的输出字段和用途；
2. 坐标：原点、轴、范围、图像尺寸、resize/letterbox 逆变换；
3. 解析：strict/lenient/protocol-fixed、invalid/no-object 和 parser version；
4. 指标：IoU、Hit、text score 的单位、阈值、分母和 scorer；
5. 闭环：grounding valid → geometric match → task success 的三层差异；
6. 项目：OPD route/raw-holdout/point protocol 的可说与不可说边界。

## 10. 结论与下一步

Grounding 的核心不是“输出一个框或点”，而是把 representation、coordinate transform、parser、scorer 和 downstream interface 固定成可审计合同。Grounding DINO 的 `cxcywh → xyxy` 代码是具体实现样例，RoboPoint 说明 point affordance 的机器人语义，OPD 提供真实项目中的多 expert、格式冲突和 raw-holdout 边界。当前节点 verdict 为 `WARN`；对应 `VLA-PER-001` 题卡已同步并保持 `unseen`，下一步进入真实口述或补 parser/normalizer roundtrip，再进入 3D lift / multi-view 的后续训练。

## References

1. [PER-001 Grounding / Coordinate Source Freeze](../sources/vol_06_per001_grounding_coordinate_source_freeze.html)。
2. Grounding DINO，[arXiv:2303.05499v1](https://arxiv.org/abs/2303.05499v1) 与 [official repository @856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)。
3. RoboPoint，[arXiv:2406.10721v1](https://arxiv.org/abs/2406.10721v1)。
4. 本仓库 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
