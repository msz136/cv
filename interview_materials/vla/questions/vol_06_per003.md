# VOL 06 Perception / Grounding / Navigation：PER-003 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-PER-003`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-003 Multi-view / Temporal Knowledge](../knowledge/vol_06_per003_multiview_temporal.html)；来源边界见 [Source Freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html)。

## 多视角 / 时序 Grounding 为什么必须绑定 Schema

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-003</b> · 多相机、多帧输入为什么不能只是把图片 concat 后喂给模型？</summary>

**面试意图**：判断你能否处理 camera identity、frame、timestamp、presence mask、common-frame fusion 和 action freshness，而不是只谈“更多视觉信息”。

**30 秒回答**：view/time 都要带 `camera_id、frame_id、K/T revision、timestamp、presence/valid、transform`。先独立预处理，再按 mask fusion；多视角预测先变到 common frame 再关联，history 绑定 control-hz、replan 和 observation age。

**机制展开（约 2 分钟）**：workspace/wrist 顺序错了，shape 仍可能正确但语义全错；缺失相机不能只置零，要有 presence mask。历史帧用真实 timestamp/stride，不能把 index 当物理时间；frame drop、action repeat 和 replan 会改变 observation age。各 view 输出先经过 `K/distortion` 与 `T_common←camera(timestamp)` 变到共同 frame，再 association/fusion，不能直接平均 pixel。Open X/WM-017/Octo 是机制参照；OPD 是静态 holdout，WAM 是有限 rollout provenance，不能声称项目已有多视角时序闭环。

**诊断 / 证据**：冻结 per-view manifest、camera order、image size、K/T revision、timestamps、valid mask 和 transform；做 camera swap、掉帧/jitter、missing-view、common-frame roundtrip、view ablation、causal-mask 和 observation-age replay。记录每视角 raw output、association、uncertainty、replan/action trace；缺 calibration/sync/replay 就停在 schema 或 geometry 层。

**项目挂钩**：OPD 可讲 point/box/text route、strict scorer 和静态 raw-holdout；WAM manifest 可讲 camera resolution、controller、horizon 和 rollout provenance。安全表达是“我能审计多视角/时序接口缺口”，不把多路 camera 字段写成 fusion 或真机收益。

**追问树**：为什么不同 pixel frame 不能平均？camera_id 和 frame_id 有什么区别？缺 view 为什么不能只补零？history stride 如何换成物理时间？怎样防 future leakage？observation age 超阈值怎么办？Octo 的 observation group 能证明你的项目用了同样 fusion 吗？

**易错点**：交换 workspace/wrist 顺序；不同分辨率复用同一 K；忽略 timestamp/TF；zero padding 无 presence mask；index 当时间；不做 common-frame association；用 view dropout 单次结果宣称鲁棒性；把静态 holdout 当闭环。

**危险答案**：说“相机越多一定越准”“concat 后模型自动知道视角”“缺失图置零即可”“历史帧天然没有泄漏”“把不同 camera 的坐标直接平均”或“OPD/WAM 已证明 multi-view temporal fusion 提升真机成功”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-003 Multi-view / Temporal Knowledge](../knowledge/vol_06_per003_multiview_temporal.html)：per-view schema、fusion、common-frame、mask 与 observation-age。
2. [PER-003 Multi-view / Temporal Source Freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html)：Open X、Octo、WM-017 与 OPD/WAM 边界。
3. [Octo architecture/execution source audit](../sources/vol_03_architecture_execution_claim_to_code.html)：observation groups、task/readout token 与 attention 参照。
4. [WM-017 Heterogeneous Schema Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)：camera/state/action/timestamp/mask/normalizer 的跨 embodiment 合同。
