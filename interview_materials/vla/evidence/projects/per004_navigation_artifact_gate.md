# PER-004 Navigation Artifact Gate：VLN / ObjectNav 项目证据盘点

> 状态：`WARN / navigation_artifact_gate / 0_local_direct_navigation_bundles`  
> 盘点日期：2026-07-18  
> 目的：核对五个个人项目是否存在可支持 VLN/ObjectNav 任务、episode、轨迹、SR/SPL 或真机导航 claim 的本地直接证据；本页只盘点证据，不把缺失写成结果。

## 1. 结论

当前工作区没有可复核的 VLN/ObjectNav navigation bundle。已找到的是 grounding、工具协议、VLA action packaging、simulator rollout provenance 或 LIBERO/World-Model 评估材料；它们可以支持接口和证据分层讨论，不能支持个人 VLN/ObjectNav benchmark、导航成功率、SPL 或真实移动闭环。

```text
可支持：task/schema 讨论、grounding→navigation 接口、timeout/cancel、metric/evidence boundary
不可支持：R2R/RxR/VLN-CE episode success、ObjectNav SR/SPL、navmesh trajectory、真机导航成功
```

## 2. 盘点范围与搜索证据

本轮只检查当前工作区的 `interview_materials/`、项目 inventories、evidence manifests、题卡/知识页和已有项目 artifact 入口；使用文件名与文本检索寻找：

- `VLN`、`ObjectNav`、`R2R`、`REVERIE`、`navmesh`、`episode_id`、`stop_called`、`SPL`；
- `trajectory`、`move_forward`、`turn_left`、`waypoint`、`action trace`、`scene revision`；
- episode denominator、success predicate、controller log、real-navigation log。

检索结果中的导航术语若只出现在本知识库、论文链接或设计文档，不计为个人项目的 local-direct artifact。远端路径、项目页自述、Git author 和公开 benchmark 数字也不计为本人运行证据。

## 3. 五项目证据矩阵

| 项目 | 本地可直接支持的相关内容 | 导航证据缺口 | 当前处理 |
| --- | --- | --- | --- |
| OPD / VLM Grounding | point/box/text route、坐标变换、strict/lenient/protocol-fixed scorer、raw-holdout leakage inventory | 无 VLN/ObjectNav episode、scene/start pose、navmesh、移动 action trace、stop predicate、SR/SPL denominator | 可作为导航前的目标 grounding hook；不能写成导航结果 |
| Robot Harness | semantic-navigation tool schema、allowed robot scope、timeout/cancel/compensation、结构化 tool result | 无 Habitat/R2R/RxR episode、RGB-D/pose trajectory、controller trace、navmesh 或真实底盘 log；project sandbox 不是物理导航 | 可讨论导航服务接口和失败恢复；不能写成 VLN/ObjectNav success |
| OpenPiVLA | observation/action packaging、action chunk、latency/processor/normalizer 证据 | 无导航 split、scene/goal manifest、stop/SPL evaluator、连续导航轨迹或真机移动记录 | 可讨论 policy-to-controller contract；不计 navigation benchmark |
| WAM / Cosmos | CoffeePressButton rollout manifest、camera/controller/horizon provenance、action trace 与 offline visual proxy | 任务不是 VLN/ObjectNav；无 navigation scene/navmesh、language route、goal/view-point、SR/SPL 或真机导航 | 保持 simulator/metric provenance；不升级为导航 claim |
| UWM / LIBERO | simulator reset、LIBERO task/eval protocol、world/action metric boundary | 无语言导航 instruction、ObjectGoal、navmesh trajectory、VLN/ObjectNav denominator 或真机 navigation log | 可迁移 protocol/evidence 方法；不计导航结果 |

## 4. Robot Harness 的特殊边界

Robot Harness inventory 中的 `semantic-navigation` 允许讨论一个高层工具如何按 robot scope、timeout、取消和 compensation 组织请求；这证明的是 tool/interface 与 runtime safety 设计，不是底层导航执行。

要把它升级为导航证据，至少还需要：

```text
episode_id / scene_id / start pose / goal or instruction
sensor config + timestamp + frame/calibration revision
action trace + controller status + collision + stop/terminal reason
navmesh/scene revision + seed + split + evaluated denominator
success predicate + SR/SPL/TL/NE/OS + per-episode failure trace
```

当前没有这些字段绑定成同一份 local-direct bundle，因此回答应说“设计了导航工具的约束接口”，而不是“完成了 VLN/ObjectNav 导航”。

## 5. Evidence ladder

| 层级 | 最小 artifact | 当前状态 |
| --- | --- | --- |
| task schema | episode JSON、goal/instruction parser、split manifest | 公源协议已冻结；项目 local-direct 缺失 |
| simulator setup | scene/navmesh revision、sensor/action config、reset log | 项目未发现 VLN/ObjectNav bundle |
| offline/teacher-forced | reference path、per-step action/grounding trace | 未发现 |
| simulated closed-loop | episode denominator、SR/SPL/TL/NE/OS、failure traces | 未发现 |
| real closed-loop | camera/pose/controller/collision/safety logs、matched protocol | 未发现 |

任何未来 bundle 都必须绑定 immutable path/hash、dataset/scene revision、seed、controller、success predicate 和 denominator；否则仍保持 `WARN`。

## 6. 与 PER-004 的关系

PER-004 知识页和题卡可以用于准备“如何设计和审计 VLN/ObjectNav protocol”的面试回答；本 gate 说明当前个人项目没有可用于回答“我在 R2R/ObjectNav 上取得了多少 SR/SPL”的直接证据。

安全口径：

> 我能解释 VLN/ObjectNav 的 episode、stop、success、SPL 和 simulator-to-real 评估合同，也能把 OPD grounding 或 Robot Harness 的高层工具接口接到导航系统设计中；但当前项目材料没有可核验的 VLN/ObjectNav episode bundle，因此不把它写成个人 benchmark 或真机导航成果。

## 7. Gate 结论与下一步

当前 verdict：`WARN`。本轮没有发现 local-direct navigation artifact，故不创建 success 数字、不创建真实导航 ownership claim，也不修改 resume bullet。

下一步只能二选一：

1. 候选人进行一次 `VLA-PER-004` 真实口述，记录答题表现但不改变项目证据等级；或
2. 用户提供/在工作区发现一份带 episode、轨迹、协议和分母的导航 bundle，再做逐字段核验。

## References

1. [PER-004 VLN / ObjectNav Knowledge](../../knowledge/vol_06_per004_vln_objectnav.html)。
2. [PER-004 VLN / ObjectNav Source Freeze](../../sources/vol_06_per004_vln_objectnav_source_freeze.html)。
3. [Robot Harness Claim–Evidence Inventory](robot_harness_claim_evidence_inventory.html)。
4. [OPD Claim–Evidence Inventory](opd_claim_evidence_inventory.html)。
5. [OpenPiVLA Claim–Evidence Inventory](openpivla_claim_evidence_inventory.html)。
6. [WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
7. [UWM / LIBERO Claim–Evidence Inventory](uwm_libero_claim_evidence_inventory.html)。
