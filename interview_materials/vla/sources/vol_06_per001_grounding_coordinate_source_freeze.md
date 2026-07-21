# VOL 06 PER-001 Source Freeze：Point / Box / Text Grounding 与坐标协议

> 状态：`source_frozen / VLA-PER-001 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片只冻结多模态 grounding 的输出表示、坐标变换、文本/点/框协议和失败诊断入口；不把任何模型的静态指标升级为真实机器人闭环成功率。

## 问题（Question）

VLA 面试中经常把“模型会看懂目标”“模型能输出 box/point”“机器人能执行该坐标”混成一句话。本 source gate 把它拆成四层：

```text
image + language
    → perception / grounding scores
    → representation (point / box / text)
    → parser + coordinate transform + normalization
    → downstream planner / controller / policy action
```

本页要冻结的最小合同是：坐标原点与轴方向、像素/归一化范围、box 参数化、point 序列格式、文本标签与置信度、resize/letterbox 的逆变换、invalid/missing 输出以及评估 scorer。任何一层未闭合，都不能从 grounding score 推出 action success。

## 1. 冻结来源与指纹

SHA 对 2026-07-18 通过 pinned URL 获取的 UTF-8 原文计算；论文 API 响应只用于记录版本与摘要指纹，具体实现优先引用 frozen commit。许可证只说明来源的公开许可，不等于本仓库可以复制完整源码或模型权重。

| 来源 | 类型 / revision | SHA-256 | 可支持的事实 | 不能支持的 claim |
| --- | --- | --- | --- | --- |
| [Grounding DINO paper](https://arxiv.org/abs/2303.05499v1) | primary paper；arXiv API v1，读取 2026-07-18 | `4d7fffc32414405b15e93309c8a7f71f55d831d21dc5ebb9410beefba6a6cb22` | text-conditioned open-set detection 的任务定位与文本/框 grounding 背景 | 某个本地 VLA 已使用 Grounding DINO，或取得特定成功率 |
| [GroundingDINO README](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/README.md) | official-code；commit `856dde20aee659246248e20734ef9ba5214f5e44` | `d69cf3fd022661e6be19c56a421020f3ee9e027375020ef6a3def0149ddf9595` | 官方安装、模型入口、开放词汇检测定位和许可证入口 | 当前项目的 checkpoint、训练 recipe、机器人闭环结果 |
| [GroundingDINO inference.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/util/inference.py) | official-code；同一 commit | `0c06c5dd2fa46ae89a9fa376c0eaa383d12e7fc21aa65d662bcf3e758d26b598` | `pred_boxes` 为四维输出；后处理先乘 `[W,H,W,H]`，再由 `cxcywh` 转为 `xyxy`；box/text threshold 与 phrase extraction 的代码边界 | 该转换已覆盖任意自定义 parser、letterbox、坐标轴、单位或 controller |
| [GroundingDINO LICENSE](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/LICENSE) | official-code；Apache-2.0 文本 | `b403c98ec1ffaccb0124632592a3d99642cddc3031ca412b402568e6c06c202a` | 公开仓库的许可证线索 | 不授权复制 checkpoint、数据或用户项目代码 |
| [RoboPoint paper](https://arxiv.org/abs/2406.10721v1) | primary paper；arXiv API v1，读取 2026-07-18 | `9a442952c7afc0eb47705324ae77fb7cd0b7dadebb6b2d6a40da46655413ff39` | 语言条件 spatial affordance / keypoint prediction 的任务 framing；点可以作为机器人下游动作的中间表示 | 任何个人项目已复现论文数字，或 point 输出已正确映射到真实控制器 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | local-evidence；审计日期 2026-07-17；仓库 HEAD `756e27e16adcfb3ccbfe98c2920dda42095b127f` | inventory 内登记的源码/表格 SHA | 五 expert、point/box/text route、raw-holdout 与 original/protocol-fixed/lenient point scorer 的项目证据边界 | OPD 单独 uplift、真实机器人 grounding success、个人逐文件 ownership |
| `C:\Users\mousongzhe\muxi\train_opd_online_vl.py` | local-evidence；inventory SHA | `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9` | route-based teacher selection、student rollout、full-vocabulary KL 的训练链路 | learned router 已被单独验证，或训练已形成可加载 C3 bundle |
| `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\dedupe_audit.json` | local-evidence；inventory SHA | `2E102BB52B925ABA5AFE9E9111C98B3FA67F7032B266B1D08EBB1164A8FFB96D` | raw-holdout 的 fingerprint/source-line/prompt-answer-image leakage gate | 评估集代表真实部署，或 scorer 已证明跨协议可比 |

## 2. 冻结的表示合同

### 2.1 Box

本切片只把以下表示视为不同的数据类型，不能只看四个数字就互换：

| 表示 | 典型字段 | 必须知道的元数据 | 常见失败 |
| --- | --- | --- | --- |
| normalized `cxcywh` | `(cx, cy, w, h)`，通常相对 `[0,1]` | 原图 `W,H`、中心/角点语义、是否裁剪/letterbox | 直接当成 `xyxy`，或忘记宽高缩放 |
| pixel `xyxy` | `(x_min,y_min,x_max,y_max)` | 原点、像素是否 inclusive、resize/rounding 规则 | x/y 交换、边界越界、rounding 改变 IoU |
| normalized `xyxy` | 四个相对坐标 | normalization axis 与有效范围 | 用 `W` 缩放 y、把模型 padding 区域当原图 |
| center/size + controller frame | perception box 加机器人/相机坐标 | camera intrinsics/extrinsics、深度或平面假设 | 把 2D box 中心直接当 3D grasp point |

GroundingDINO frozen inference code 体现一种具体实现：模型输出 `pred_boxes` 后，按 `[source_w, source_h, source_w, source_h]` 缩放，再把 `cxcywh` 转成 `xyxy`。这是实现样例，不是所有 VLA 的通用接口。

### 2.2 Point

point 可能表示像素点、归一化点、多个候选 keypoint 或 affordance；必须绑定：

```text
(x, y), coordinate_space, image_size, ordering, validity, confidence, parser_version
```

`<point>[[x1,y1],[x2,y2]]</point>`、`[(x1, y1), ...]` 和 JSON `{"points": ...}` 不是同一协议。strict scorer 失败时，先检查 tag、括号、空格、坐标范围和 prompt hash，再讨论几何能力；lenient parser 只能作为兼容性诊断，不能替代部署协议。

### 2.3 Text / phrase

文本 grounding 输出至少要分开：原始 phrase、规范化 label、token span、置信度、box/point 关联和 no-object/ambiguous 状态。GroundingDINO inference code 的 phrase extraction 依赖 tokenized caption 与 text threshold；因此“字符串命中”不等于 phrase 已正确绑定到目标，也不等于下游 action head 能消费该结果。

## 3. 坐标变换与评估边界

对原图宽高 `W,H`，normalized `cxcywh` 到 pixel `xyxy` 的一种明确变换是：

\[
x_1=W\left(c_x-\frac{w}{2}\right),\quad
y_1=H\left(c_y-\frac{h}{2}\right),\quad
x_2=W\left(c_x+\frac{w}{2}\right),\quad
y_2=H\left(c_y+\frac{h}{2}\right).
\]

这里 `cx,cy,w,h` 是相对原图的归一化量；公式只处理尺度和参数化，不处理 letterbox padding、裁剪、相机外参或深度。代码映射对应 GroundingDINO `box_convert` 前的 `[W,H,W,H]` 缩放；项目实现必须另存 transform metadata。

IoU 只衡量二维框重叠：

\[
\operatorname{IoU}(A,B)=\frac{|A\cap B|}{|A\cup B|}.
\]

IoU/Hit@threshold 是静态 grounding 指标；它不包含控制器 latency、动作单位、碰撞、接触或 task success predicate。point Hit@50/100 也必须说明距离单位、图像尺度、有效样本数和 strict/lenient parser。

## 4. 项目证据映射（OPD）

| 项目材料 | 当前可说 | 当前不能说 |
| --- | --- | --- |
| 五 expert mix 与 route metadata | 数据构造明确区分 reasoning/object/region/spatial/point；可解释 target/candidate route | route metadata 已等价于 learned router，或每个 expert 独立最优 |
| raw-holdout dedupe audit | 可说 image/fingerprint/source-line/prompt-answer-image leakage gate 的结果 | raw-holdout 等价真实机器人闭环 |
| point protocol reconciliation | 可区分 original strict、protocol-fixed strict、lenient geometry | strict=0 直接等于不会 point grounding，或 lenient score 可代替部署 score |
| OPD5000 by-format/by-pool table | 可绑定 checkpoint、subset、scorer 和不同最佳点 | 把 5000 说成所有 pool 的全局最佳，或把多因素变化归因于 OPD 单独 |

本地 OPD 证据是项目 hook，不是本页的通用 grounding 定理；任何数字必须沿用 inventory 的 protocol-bounded/WARN 状态。

## 5. Source gate 结论与下游范围

已冻结：

1. point、box、text 是不同的输出合同；parser、坐标空间、尺寸、顺序和 invalid 状态必须显式记录。
2. GroundingDINO 提供一个可核查的 `normalized cxcywh → pixel xyxy` 实现样例，并把 box/text threshold 与 phrase extraction 分开。
3. RoboPoint 说明 point/keypoint affordance 可以成为机器人下游接口，但不自动等于 action 或闭环控制。
4. OPD 的 strict/lenient/protocol-fixed 三套 point scorer 必须分开，不能用格式失败替代能力结论。

仍待下游知识页补充：transform/letterbox 逆变换伪代码、box/point scorer 的逐样本诊断、3D lift 的深度/外参合同、多视角融合、point/box 到 action head 的接口和 `VLA-PER-001` 原子题卡。

当前 verdict：`WARN`。来源支持机制与协议设计，不支持个人项目的未绑定成功率、机器人闭环或 ownership 强结论。

## References

1. Grounding DINO paper，[arXiv:2303.05499v1](https://arxiv.org/abs/2303.05499v1)，API response SHA `4d7fffc32414405b15e93309c8a7f71f55d831d21dc5ebb9410beefba6a6cb22`。
2. IDEA-Research，[GroundingDINO@856dde20](https://github.com/IDEA-Research/GroundingDINO/tree/856dde20aee659246248e20734ef9ba5214f5e44)，README/inference/LICENSE 指纹见表格。
3. RoboPoint，[arXiv:2406.10721v1](https://arxiv.org/abs/2406.10721v1)，API response SHA `9a442952c7afc0eb47705324ae77fb7cd0b7dadebb6b2d6a40da46655413ff39`。
4. 本仓库 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：五 expert、route、point protocol、raw-holdout 与 ownership 边界。
