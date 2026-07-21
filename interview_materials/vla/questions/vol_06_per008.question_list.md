# VOL 06 PER-008 题卡清单

> 规划日期：2026-07-20  
> 状态：`source_frozen / knowledge_drafted / card_drafted / WARN`  
> 题数：1  
> 节点：downstream minimum-sufficient representation、point/box/mask/semantic-keypoint/affordance合同、不可逆转换与OPD真实性边界

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-PER-008 | L2 | P0 | 机器人视觉什么时候该输出 point、box、mask、semantic keypoint 或 affordance？为什么更密不一定更好，OPD 的 affordance point 能说到哪一步？ | RoboPoint/SAM/kPAM/Where2Act pinned source与本地OPD五文件；无local mask/keypoint/dense-affordance head、matched ablation、success calibration、controller/robot bundle或个人ownership证据 |

## 2. 题卡退出条件

1. ID唯一并保持`unseen`。
2. 包含短答案、机制展开、诊断/证据、项目挂钩、追问、易错点、危险答案和来源。
3. 按consumer required-fields选最小充分表示，不能按point→box→mask密度排序。
4. 明确point不等于semantic keypoint/affordance，`mask→box`有损、`box→mask`不可逆。
5. OPD只表述为affordance-labelled point supervision，不升级为dense affordance、controller feasibility或robot success。
6. 30秒答案≤180字，机制展开≤350字；HTML可折叠，review保持`WARN`。

## 3. 依赖与下一步

- 前置：[PER-008 Source Freeze](../sources/vol_06_per008_representation_choice_source_freeze.html) 与 [PER-008 Knowledge](../knowledge/vol_06_per008_representation_choice.html)。
- 依赖缺口：local mask/keypoint/dense-affordance schema/head/parser、primitive/tool/state/direction/horizon、score calibration、matched downstream ablation、controller/episode bundle与候选人ownership confirmation。
- `VLA-PER-008..009` source/knowledge/card均已同步且保持`unseen`；下一bounded slice只做`VLA-PER-010` metric/parser source freeze，不生成knowledge/card。
