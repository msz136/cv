# VOL 06 PER-003 Source Freeze：多视角 / 时序 Grounding 与输入 Schema

> 状态：`source_frozen / VLA-PER-003 / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结多相机、多帧 grounding 的 camera identity、时间、几何、mask 与融合合同；不把“堆了多张图”升级为多视角融合能力或闭环收益。

## 问题（Question）

当一个 VLA 同时输入 workspace camera、wrist camera 或历史帧，怎样确保每张图仍带有正确的 camera identity、frame、intrinsics/extrinsics、timestamp、resize policy 和 validity mask？多视角融合、时序堆叠和缺失相机处理又如何与 action/chunk 对齐？

最小链路：

```text
per-view image + camera_id + frame_id + K/T + timestamp + valid
  → per-view preprocess / tokens
  → view/time fusion with masks
  → grounding target + uncertainty
  → action/planner input with observation-age contract
```

## 1. 冻结来源与指纹

| 来源 | 类型 / revision | SHA-256 | 可支持的事实 | 不能支持的 claim |
| --- | --- | --- | --- | --- |
| [Open X-Embodiment README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md) | official-code/data entry；commit `9eeb68b989efbcf474e8fb9019e01d02b962a604` | `e7dbf6bb04559e981b7eab2e0f4510579bf82b09948a0fe6471ba1794f86ae59` | RLDS episode/step organization、RT-1-X camera/action README 与数据许可边界 | 所有子数据集视角、action semantics、horizon 或 calibration 已统一 |
| [Octo paper/code audit](../sources/vol_03_architecture_execution_claim_to_code.html) | official-code；`octo-models/octo@241fb3514b7c40957a86d869fecb7c7fc353f540` | `octo_module.py` raw SHA `e458062721fd1e72fad00f7833b749e82d0df60aa7927557362bdf6463299fbf` | observation groups、task prefix、readout token、历史 observation attention 和 action mask 的实现参照 | 当前用户项目采用同一 view order、fusion 或 temporal policy |
| [WM-017 heterogeneous schema freeze](vol_04_wm017_heterogeneous_schema_source_freeze.html) | local canonical source | 本仓库登记 | camera/state/action/timestamp/horizon/presence mask/normalizer 的跨 embodiment 审计框架 | 多视角 adapter、roundtrip 或 per-view ablation 已完成 |
| [PER-001 Grounding Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html) | local canonical knowledge | 本仓库登记 | point/box/text representation、parser、2D coordinate transform 与 scorer boundary | 多视角 geometry 或 temporal consistency 已闭合 |
| [PER-002 3D Lift Knowledge](../knowledge/vol_06_per002_3d_lift_frame.html) | local canonical knowledge | 本仓库登记 | depth、calibration、frame、timestamp、uncertainty 的单视角合同 | 多相机 extrinsic、同步或 fusion 已在用户项目取证 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | local-evidence；2026-07-17 | inventory 内源码/表格 SHA | static point/box/text holdout、route metadata、protocol-fixed scorer | 多视角/时序 grounding、相机 calibration、机器人闭环 |
| [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html) | local-evidence；CoffeePressButton bundle | manifest SHA 见页面 | rollout camera count/resolution、controller、horizon 与 provenance 字段 | multi-camera fusion、timestamped calibration、真实 3D target |

## 2. 冻结的 per-view schema

每个 view/time item 不能只是一张 tensor，应至少包含：

```text
image              # pixels after declared color/resize policy
camera_id          # stable logical identity, e.g. workspace/wrist
frame_id           # coordinate frame for the optical ray
intrinsics_id      # K/distortion/image_size revision
extrinsics_id      # T_target←camera revision, if needed
timestamp          # capture time, not batch index
valid/presence     # camera/frame/depth validity
transform_id       # crop/resize/letterbox inversion metadata
```

`camera_id` 解决“第 0 路到底是哪台相机”；`frame_id` 解决“它在什么几何 frame”；`timestamp` 解决“历史帧和 action 是否同步”；`presence/valid` 解决“缺失 modality 是否被零值伪装成真实黑图”。Open X/RT-1-X 的统一 episode container 不等于每个数据集共享 camera semantics；WM-017 已将这一点冻结为跨 embodiment 边界。

## 3. 多视角与时序的三类合同

### 3.1 View identity

view order、camera name、image orientation、crop/resize、intrinsics/extrinsics 必须是 manifest 字段。交换 workspace/wrist 或 left/right camera 可能仍产生合法 tensor，却让 grounding/action 语义整体错位；shape 检查无法发现此类错误。

### 3.2 Temporal identity

时间窗口应记录真实 timestamp 或可解释的 control-step mapping：

```text
history = [(camera_id, frame_id, t_i, valid_i, image_i), ...]
action_target = (t_action, horizon, control_hz, repeat, replan_policy)
```

不能用数组 index 自动当作物理时间；frame drop、重复 terminal frame、异步 camera 和 action repeat 都会改变 observation age。历史帧若进入模型，必须说明 causal/ordered mask 与是否允许未来信息泄漏。

### 3.3 Presence/validity mask

缺失相机、无效 depth、掉帧或不同步 frame 应使用显式 mask/presence token，并在 pooling/loss/scorer 中保持一致。零填充只是存储策略；如果没有 mask，模型可能把“黑图/零 state”当成一种 shortcut，而不是学习缺失情况。

## 4. Fusion 位置与 trade-off

| 方式 | 直觉 | 风险 |
| --- | --- | --- |
| early pixel/feature concat | 视角信息尽早交互 | resolution、camera order、显存和几何对齐复杂 |
| token-level attention | 每个 view/time 保留独立 token，使用 camera/time embedding | mask、位置编码、缺失 view 和计算量需明确 |
| late prediction fusion | 各 view 先独立 grounding，再合并 box/point/score | 跨视角对应、重复目标和冲突置信度难处理 |
| temporal queue/chunk | 重用历史特征，减少重复编码 | stale observation、frame drop 和 action-age 风险 |
| view dropout / masking | 训练缺失相机鲁棒性 | 若没有 matched ablation，不能声称泛化提升 |

Octo 的 observation groups、task prefix、readout 与历史 attention 是一种公开实现参照；它支持“如何在 token/attention 层组织 observation”，不支持用户项目已经采用该 fusion 或获得同样效果。

## 5. 多视角几何一致性

当多个 camera 输出同一目标时，至少要把每个 prediction 变到共同 frame，再做融合：

```text
view_i pixel → (K_i, distortion_i) → camera_i point/ray
             → T_common←camera_i(t_i)
             → common-frame candidate + uncertainty
             → association / fuse / reject
```

不能在不同 pixel frame 直接平均 `(x,y)`。融合前需要考虑：

- intrinsics/distortion/image-size 是否同一 revision；
- extrinsics 是否静态或随时间变化；
- timestamp skew 是否可接受；
- 各视角 confidence 是否校准；
- 遮挡、重复检测和 object identity 如何关联；
- 3D depth/plane hypothesis 是否一致。

如果只做 late box voting 而没有 frame/association contract，它仍是二维 heuristic，不应称为 3D multi-view fusion。

## 6. 时序与 action 对齐

观测与动作至少需要以下字段：

| 字段 | 作用 | 失败表现 |
| --- | --- | --- |
| `t_image/t_depth/t_tf` | 把观测和几何变换对齐 | 运动目标出现系统偏差 |
| `history_len/stride` | 定义历史窗口 | index 与物理秒数不一致 |
| `control_hz/action_repeat` | 把 horizon 转成物理时间 | chunk 看似相同但执行时长不同 |
| `observation_age` | 判断 action freshness | 执行 stale target |
| `replan_policy` | 定义何时重新 grounding | 旧目标持续执行或频繁抖动 |
| `valid/presence` | 屏蔽掉帧/缺失 view | zero shortcut、loss/scorer 污染 |

PER-002 的 `T_target←camera(τ)` 只解决单视角 frame transform；PER-003 需要扩展为每个 view/time 的 transform 和同步记录，并在 action/chunk/replan 层保持同一 protocol。

## 7. 证据阶梯与项目边界

| 层级 | 最小证据 | 仍不能支持 |
| --- | --- | --- |
| schema | per-view manifest、camera order、timestamp、presence mask | view fusion 正确 |
| geometry | per-view calibration/extrinsic、common-frame transform、roundtrip | temporal consistency |
| fusion | matched multi-view target、association/uncertainty、view ablation | action/controller success |
| temporal | frame-drop/jitter/replay、observation age、causal mask audit | long-horizon task success |
| closed-loop | same task/init/seed/controller、episode denominator、failure traces | 跨 embodiment/真机泛化 |

当前 OPD 是静态 point/box/text holdout，WAM bundle 是有限 rollout provenance；二者都没有 multi-view fusion、camera calibration、temporal replay 或 per-view ablation artifact。不能把“多路 camera 字段存在”写成完成多视角模型。

## 8. Source gate 结论与下游范围

已冻结：

1. 多视角输入必须携带 camera/frame identity、intrinsics/extrinsics、timestamp、transform metadata 和 presence/valid mask。
2. 多帧输入必须区分物理时间、控制频率、action repeat、history stride、replan 和 observation age；index 不能代替 timestamp。
3. 多视角融合需要 common-frame transform 和 target association；不同 pixel frame 不能直接平均。
4. Open X、Octo 和 WM-017 提供 schema/attention/heterogeneous embodiment 参照，不证明个人项目已有 multi-view/temporal fusion。

知识页与 `VLA-PER-003` 原子题卡已补充 view/time manifest、camera/time embedding、causal/missingness mask、common-frame association、view dropout 与 temporal replay；本地 multi-view calibration/sync artifact 仍缺。

当前 verdict：`WARN`。来源支持 schema 和 fusion 设计，不支持 OPD/WAM 已完成多视角或时序 grounding 结果。

## References

1. [Open X-Embodiment frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md)。
2. [Octo architecture/execution source audit](vol_03_architecture_execution_claim_to_code.html) 与 `octo-models/octo@241fb3514b7c40957a86d869fecb7c7fc353f540`。
3. [WM-017 heterogeneous schema source freeze](vol_04_wm017_heterogeneous_schema_source_freeze.html)。
4. [PER-001 Grounding / Coordinate Knowledge](../knowledge/vol_06_per001_grounding_coordinate.html)。
5. [PER-002 3D Lift / Frame Knowledge](../knowledge/vol_06_per002_3d_lift_frame.html)。
6. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 与 [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
