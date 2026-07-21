# VOL 06 Perception / Grounding / Navigation：PER-001 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-PER-001`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-001 Grounding / Coordinate Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html)；来源边界见 [Source Freeze](../sources/vol_06_per001_grounding_coordinate_source_freeze.html)。

## Point / Box / Text Grounding 与坐标协议

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-001</b> · 为什么 grounding 面试必须先讲 coordinate contract，而不能只报 IoU 或 point hit？</summary>

**面试意图**：判断你能否把表示、预处理、解析、评估和下游 action 接口串起来，并识别 strict=0 可能是协议失败而非能力为零。

**30 秒回答**：point/box/text 不是同一输出：要固定坐标空间、图像尺寸、参数化、parser 和 scorer。`cxcywh` 需按 `W,H` 转 `xyxy`，还要逆 letterbox；strict/lenient 结果不能混报，IoU/Hit 也不等于 action success。

**机制展开（约 2 分钟）**：先记录表示、空间、尺寸、顺序和 parser。normalized `cxcywh` 先乘 `[W,H,W,H]` 再转 `xyxy`；有 crop/letterbox 时还要减 padding、除 scale。strict 检查部署格式，protocol-fixed 统一 prompt，lenient 只作兼容诊断。IoU/Hit 只说明二维几何，后面仍有 parser、深度/外参、planner、action normalization 和 controller predicate。OPD 的五 expert/point/box/text route 是项目证据，不能推出 learned router 或单独 uplift。

**诊断 / 证据**：固定 prompt、image size、transform、parser 和 scorer；用 sentinel box/point 做 round-trip，分别测 original strict、protocol-fixed strict、lenient geometry，记录有效样本、距离单位和每个失败阶段。若 strict=0，先检查 tag、括号、坐标范围、x/y 轴、`W/H` 缩放和 padding offset，再判断模型几何能力；同时保存 raw output、transform metadata 和 downstream action trace。

**项目挂钩**：OPD 的 raw-holdout、point protocol reconciliation、format-conflict metadata 和 by-format/by-pool checkpoint 表可作为真实例子；安全表述是“我把 grounding 结果按协议和证据层拆开”，不把静态 holdout 写成机器人闭环成功。

**追问树**：`cxcywh` 与 `xyxy` 怎样互转？为什么 letterbox 会造成系统偏移？point 中心能否直接当抓取点？strict=0 是否说明模型不会 grounding？IoU 高但任务失败可能在哪一层？lenient parser 何时可以使用？

**易错点**：把四个数默认当 `xyxy`；x/y 乘错 `W/H`；忽略 crop/padding；把 phrase 命中当目标绑定；把 strict=0 当能力为零；把 IoU/Hit 当 action success；把 OPD 组合结果写成单一 OPD uplift。

**危险答案**：说“坐标归一化后任何分辨率都天然一致”“IoU 高就能抓到目标”“lenient 分数更高所以模型更强”“point 就是 3D grasp pose”或“OPD 的 10k holdout 证明真机泛化”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-001 Grounding / Coordinate Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html)：表示合同、变换公式、评估阶梯、pipeline 与 OPD 边界。
2. [PER-001 Grounding / Coordinate Source Freeze](../sources/vol_06_per001_grounding_coordinate_source_freeze.html)：Grounding DINO、RoboPoint 和 protocol 指纹。
3. [Grounding DINO official inference.py](https://github.com/IDEA-Research/GroundingDINO/blob/856dde20aee659246248e20734ef9ba5214f5e44/groundingdino/util/inference.py)：`cxcywh → xyxy` 后处理实现。
4. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：point/box/text route、strict/lenient/protocol-fixed scorer 与项目 ownership 边界。
