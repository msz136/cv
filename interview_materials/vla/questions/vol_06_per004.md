# VOL 06 Perception / Grounding / Navigation：PER-004 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-PER-004`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-004 VLN / ObjectNav Knowledge](../knowledge/vol_06_per004_vln_objectnav.html)；来源边界见 [PER-004 Source Freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html)。本题不把现有项目证据升级为导航结果。

## 如何设计可复现的 VLN / ObjectNav 评估协议

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-004</b> · VLN、ObjectNav 和 REVERIE 的 success/SPL 协议怎样拆开，为什么不能只报一个成功率？</summary>

**面试意图**：判断你能否先冻结任务合同，再解释 stop、success、路径效率和 simulator-to-real 边界，而不是把不同导航 benchmark 混成一个分数。

**30 秒回答**：先分任务：ObjectNav 是类别/实例与 view-point，VLN 是语言路线，REVERIE 评估 grounding。冻结 scene、起点、split、action/stop、predicate、分母；SR 按 episode success，SPL 依赖 shortest 与实际轨迹。不能横比，更不能把 simulator 分数写成真机结果。

**机制展开（约 2 分钟）**：先冻结 episode 的 scene、起点、goal/instruction、split 和分母；observation 记录 RGB-D、pose、timestamp/valid，action 记录类型与 repeat。Habitat-Lab 的 `stop` 设置 `is_stop_called`，success 要按 POINT/VIEW_POINTS 距离和 predicate 判断。SR 是 episode success 平均；SPL 还用 shortest path 与轨迹长度。保留 TL/NE/OS 和 failure trace，才能区分 grounding、规划、controller。不同 action space、scene 或版本不能横比；不能写成导航结果。

**诊断 / 证据**：建立逐 episode manifest，保存 scene/dataset/navmesh revision、start pose、goal/view-point、language/object parser、sensor/action config、stop reason、pose/action trace、success predicate、shortest path、actual path、seed 和 denominator。用固定 protocol 做 reset/seed replay；对 POINT↔VIEW_POINTS、action repeat、controller latency、navmesh 和 stop threshold 做 matched sensitivity；输出 SR/SPL/TL/NE/OS 与失败分类。若只有论文表格、单个 rollout 或 simulator summary，没有 episode trace 和分母，就保持 `WARN`。

**项目挂钩**：OPD 可连接 point/box/text grounding、坐标和 scorer，Robot Harness 可连接导航工具的 timeout/cancel/compensation；OpenPiVLA 可连接 observation/action packaging 与 chunk/replan；WAM/UWM 可连接 simulator provenance 和 metric ladder。安全表达是“我能把 grounding、导航接口和评估证据拆层”，不把这些项目写成已有 VLN/ObjectNav benchmark 或真机闭环。

**追问树**：ObjectGoal 的 view-point 与目标点有什么区别？为什么经过目标但没 stop 可能仍失败？SPL 的 \(L_i\) 和 \(P_i\) 怎么得到？OS 高而 SR 低说明什么？如何防 reference path 泄漏？navmesh 改变会影响哪些指标？R2R 图导航和 VLN-CE 连续动作能否直接比较？

**易错点**：混淆类别与实例；把 REVERIE grounding 当 ObjectNav success；把 shortest path 当实际轨迹；忽略 stop、timeout、repeat、latency、scene revision 或 denominator；跨 protocol 平均 SR/SPL；把 simulator/offline proxy 写成真机结果。

**危险答案**：说“所有导航只要 final distance 小就成功”“SPL 高就说明真机可靠”“ObjectNav、VLN、REVERIE 可以用同一 success”“论文 baseline 就是我的实验”或“OPD/WAM 已证明导航闭环提升”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-004 VLN / ObjectNav Knowledge](../knowledge/vol_06_per004_vln_objectnav.html)：任务 taxonomy、episode/observation/action/stop、success/SPL、失败树与项目边界。
2. [PER-004 VLN / ObjectNav Source Freeze](../sources/vol_06_per004_vln_objectnav_source_freeze.html)：Habitat-Lab/Habitat-Sim/VLN-CE pinned source、R2R、REVERIE、ObjectNav Revisited 与 SPL 入口。
3. [Habitat-Lab navigation measures](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/nav.py) 与 [ObjectNav task](https://github.com/facebookresearch/habitat-lab/blob/0fb6f43ffe806a8088a171b036336c093bcf604e/habitat-lab/habitat/tasks/nav/object_nav_task.py)。
4. [VLN-CE frozen README](https://github.com/jacobkrantz/VLN-CE/blob/729d141b2ee10628061ada74dd3a5b9f70faeba5/README.md)。
5. [R2R](https://arxiv.org/abs/1711.07280)、[REVERIE](https://arxiv.org/abs/1904.10151)、[ObjectNav Revisited](https://arxiv.org/abs/2006.13171)、[SPL](https://arxiv.org/abs/1807.06757)。
