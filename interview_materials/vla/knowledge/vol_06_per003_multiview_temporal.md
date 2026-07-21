# VOL 06 Perception / Grounding / Navigation：多视角、时序与输入 Schema（PER-003）

> 状态：`drafted / VLA-PER-003 / knowledge_1_of_phase / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 来源入口：[PER-003 Multi-view / Temporal Source Freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html)。  
> 前置知识：[PER-001 Grounding](vol_06_per001_grounding_coordinate.html)、[PER-002 3D Lift](vol_06_per002_3d_lift_frame.html)。

## 问题（Question）

多相机、多帧输入经常被简化为“把图片 concat 后喂给模型”。这会隐藏四个关键问题：模型是否知道每张图来自哪台相机、每个像素属于哪个 frame、历史图像和动作是否时间对齐、缺失相机是否被零值误认为真实观测。

本页回答：

1. per-view schema 为什么不能只有 image tensor？
2. camera identity、frame identity、timestamp 与 presence mask 各自解决什么问题？
3. early/token/late fusion 和 temporal queue 的 trade-off 是什么？
4. 多视角预测为什么必须先变到 common frame 再融合？
5. 如何把 view/time schema 接到 grounding、action chunk 和 closed-loop evaluation？

## 知识地图位置与前置依赖

```text
PER-001 point/box/text contract
          ↓
PER-002 depth/calibration/frame contract
          ↓
PER-003 multi-view/temporal schema + fusion
          ↓
PER-004 navigation / VLN / ObjectNav
          ↓
action chunk / planner / controller / closed-loop evaluation
```

Open X-Embodiment 和 WM-017 提供 heterogeneous schema 参照，Octo 提供 observation-group/readout/attention 的公开实现参照；这些来源不等于用户项目已经完成多视角融合。OPD/WAM 仅作为 evidence-boundary hook。

## 1. 30 秒直觉：一张图必须带身份证和时间戳

一个可用的 view/time item 不应只是 `image[T,C,H,W]`，而应像一条记录：

```text
image + camera_id + frame_id + K/T revision
      + timestamp + valid/presence + transform_id
```

`camera_id` 防止 workspace/wrist 或 left/right 顺序交换；`frame_id` 防止不同坐标系直接比较；`timestamp` 防止旧图配新 pose 或新图配旧 action；`presence/valid` 防止缺失相机被零填充伪装成真实黑图。shape 正确只说明张量能进模型，不说明语义正确。

## 2. Per-view schema：把几何和时间作为数据字段

### 2.1 最小字段

| 字段 | 作用 | 缺失时的风险 |
| --- | --- | --- |
| `image` | 经过声明颜色/resize policy 的像素 | 预处理与 calibration space 不一致 |
| `camera_id` | 稳定逻辑身份，如 workspace/wrist | camera order 交换仍能通过 shape check |
| `frame_id` | optical/body/world frame 标识 | 不同 pixel/3D frame 被直接平均 |
| `intrinsics_id` | `K/distortion/image_size` revision | point/box 逆投影使用错误标定 |
| `extrinsics_id` | `T_target←camera` revision | 视角无法变换到共同 frame |
| `timestamp` | capture time | history/action 物理时间错位 |
| `valid/presence` | camera/depth/frame 是否有效 | zero shortcut、loss/scorer 污染 |
| `transform_id` | crop/resize/letterbox metadata | 输出坐标无法逆变换 |

Open X 的 RLDS episode/step container 能统一数据容器，但不代表每个子数据集拥有相同相机、action semantics 或 horizon。WM-017 的 schema freeze 将 camera、state、action、timestamp、mask 和 normalizer 明确拆开；这比“所有数据都有 image 字段”更强。

### 2.2 Camera 与 time embedding

在 token-level fusion 中，可以把每个 view/time 特征写成：

\[
z_{i,t}=f_\theta(x_{i,t})+e^{cam}_{i}+e^{time}_{t}+e^{frame}_{i,t},
\]

其中 `i` 是 camera identity，`t` 是物理时间或经过离散化的时间位置，`e_frame` 可编码 view 的几何/embodiment 条件。公式只是设计模板；代码还必须把 `valid/presence` 和 transform metadata 传到 attention/pooling，而不是只加 embedding。

## 3. Temporal identity：index 不等于物理时间

历史窗口应保留真实时间或可解释的 control-step mapping：

```text
history = [(camera_id, frame_id, t_i, valid_i, image_i), ...]
action_target = (t_action, horizon, control_hz, repeat, replan_policy)
```

至少区分：

- `history_len`：帧数；
- `stride`：采样间隔；
- `control_hz`：控制频率；
- `action_repeat`：一条 action 保持多久；
- `observation_age`：当前 action 使用的观测距采集时间多久；
- `replan_policy`：何时重新 grounding 或刷新 chunk。

frame drop、重复 terminal frame、异步 camera 和 action repeat 都可能让相同的数组长度对应不同物理时长。若历史帧用于训练，必须说明 causal/ordered mask，避免 future frame leakage；若历史帧用于在线推理，还要把 stale observation 纳入 action freshness gate。

## 4. Presence 与 validity：mask 不是可选装饰

缺失相机、无效 depth、掉帧或不同步 frame 应显式记录：

```text
presence[i,t] ∈ {0,1}
valid_depth[i,t] ∈ {0,1}
timestamp_ok[i,t] ∈ {0,1}
```

如果只把缺失 view 置零而不提供 mask，模型可能学习“全零就是某个相机缺失模式”，而不是根据可用视角完成 grounding。mask 必须在以下位置保持一致：

1. token pooling/attention：无效 view 不应拥有与真实 view 相同的权重；
2. loss：缺失 target 或 padding 不应进入监督分母；
3. scorer：无效预测应有明确 reject/skip 规则；
4. planner/controller：高风险或 stale target 应进入 invalid/safe 分支。

## 5. Fusion 位置与 trade-off

| 方式 | 数据流 | 优点 | 风险 |
| --- | --- | --- | --- |
| early pixel/feature concat | view features 在早期拼接 | 交互早、实现直观 | resolution、order、显存和几何对齐复杂 |
| token-level attention | 每个 view/time 保留 token，用 camera/time embedding 和 mask | 可表达跨视角/时序依赖 | attention mask、缺失 view 和计算量需要审计 |
| late prediction fusion | 各 view 独立 grounding，再合并 box/point/score | 单视角模块可复用 | 对象关联、重复检测、置信度校准难 |
| temporal queue/chunk | 重用历史特征、减少重复编码 | 降低部分推理成本 | stale action、frame drop、replan 边界 |
| view dropout/masking | 训练时模拟缺失视角 | 可能提升缺失鲁棒性 | 没有 matched ablation 就不能声称提升 |

Octo 的 observation groups、task prefix、readout token 和历史 attention 是一种公开实现参照：它说明 view/time 信息可以通过 token/group/mask 组织，但不证明所有 VLA 都使用相同融合方式，更不证明用户项目已经复现该行为。

## 6. 多视角几何一致性：先 common frame，再融合

如果不同相机分别输出一个 point/box，不能直接对 pixel `(x,y)` 求平均，因为每个 image plane 的原点、焦距、畸变和视角不同。正确的概念链是：

```text
view_i pixel
  → (K_i, distortion_i) → camera_i ray/3D candidate
  → T_common←camera_i(timestamp_i)
  → common-frame candidate + uncertainty
  → object association / fuse / reject
```

融合前应检查：

- `K_i/distortion_i/image_size` 是否是同一 revision；
- extrinsic 是否静态，或是否需要按 timestamp 查询；
- timestamp skew 是否在运动误差预算内；
- confidence 是否跨视角校准；
- 遮挡、重复检测和 object identity 如何匹配；
- depth/plane hypothesis 是否一致。

只在二维做 late box voting 而没有 frame/association contract，仍是二维 heuristic，不应称为 3D multi-view fusion。

## 7. 可审计的 view/time pipeline

```python
def fuse_views_and_history(samples, model, contract, tf_buffer):
    # 1. Validate identity, shape, timestamps and reversible transforms.
    records = validate_view_time_manifest(samples, contract.schema_version)

    # 2. Preprocess each view independently; retain transform metadata.
    tokens = []
    for rec in records:
        if not rec.presence or not rec.timestamp_ok:
            continue
        image, transform = preprocess(rec.image, rec.resize_policy)
        z = model.encode(image)
        tokens.append(add_camera_time_frame_embedding(
            z, rec.camera_id, rec.timestamp, rec.frame_id, transform))

    # 3. Fuse only through the declared attention/missingness contract.
    fused = masked_view_time_attention(tokens, contract.presence_mask,
                                       contract.causal_mask)

    # 4. Convert per-view predictions to a common frame before association.
    candidates = []
    for pred in model.ground(fused):
        candidate = lift_and_transform(pred, tf_buffer, pred.timestamp,
                                        contract.common_frame)
        if candidate.valid:
            candidates.append(candidate)
    target = associate_fuse_or_reject(candidates, contract.association)

    # 5. Emit observation age and provenance for planner/action freshness.
    return attach_age_uncertainty_and_revision(target, records, contract)
```

伪代码的关键是先验证 manifest，再独立预处理各视角，保留 mask/transform，最后在 common frame 做 association；它是设计合同，不是 OPD/WAM 已有实现。

## 8. Grounding、action chunk 与 observation age

多视角模型输出一个“正确”的 target，也可能因为 observation 太旧而执行错误 action。因此 planner/policy 接口应至少绑定：

```text
target_frame / target_timestamp / observation_age
valid / uncertainty / source_views
horizon / control_hz / action_repeat / replan_policy
```

如果 `observation_age` 超过 freshness budget，应重新 grounding、缩短执行窗口、进入 safe hold 或拒绝 action。action chunk 的长度不能只用数组 `H` 表示，还要换算为物理时间 `H / control_hz`，并与 replan policy 一起评估。

## 9. 证据阶梯与项目边界

| 层级 | 最小证据 | 不能越级支持 |
| --- | --- | --- |
| schema | per-view manifest、camera order、timestamp、presence mask | view fusion 正确 |
| geometry | per-view calibration/extrinsic、common-frame transform、roundtrip | temporal consistency |
| fusion | matched multi-view target、association/uncertainty、view ablation | action/controller success |
| temporal | frame-drop/jitter/replay、observation age、causal mask audit | long-horizon task success |
| closed-loop | same task/init/seed/controller、episode denominator、failure trace | 跨 embodiment/真机泛化 |

OPD 当前是 static point/box/text holdout，WAM bundle 只有有限 rollout provenance；二者都没有 multi-view calibration、sync、view ablation 或 temporal replay artifact。不能把“多路 camera 字段存在”写成完成了多视角模型。

## 10. 项目映射与常见 bad case

### OPD

可用于说明 point/box/text route、strict/lenient scorer、raw-holdout 和格式冲突。它不能证明多相机 fusion、temporal consistency 或机器人闭环。

### WAM

manifest 的 camera resolution、controller、horizon 和 rollout files 可说明接口 provenance；它没有 per-camera calibration、同步记录、view association、temporal replay 或 3D target，因此不能说完成多视角/时序 grounding。

### Bad cases

- workspace/wrist 或 left/right camera order 交换，但 shape 仍正确；
- 不同 image size 使用同一个 `K`，或 resize 后忘记更新 transform；
- 把多个 pixel frame 直接平均；
- 只用数组 index 表示时间，忽略 frame drop/action repeat；
- 缺失 camera 置零却不提供 presence mask；
- 将旧观察的 target 沿用到新 action chunk；
- 用 view dropout 后的单次指标声称鲁棒性提升；
- 将 Octo/Open X 的公开 schema 直接写成个人项目实现。

## 11. 面试回答检查表

回答 PER-003 至少覆盖：

1. per-view schema：camera/frame identity、K/T revision、timestamp、presence/valid、transform；
2. temporal schema：history、stride、control Hz、repeat、replan、observation age；
3. fusion：early/token/late/queue 的取舍；
4. common-frame association，而不是 pixel 直接平均；
5. causal/missingness mask 与 action/loss/scorer 的一致性；
6. view/geometry/fusion/temporal/closed-loop 五层证据；
7. OPD/WAM 当前没有 multi-view/temporal artifact 的边界。

## 12. 结论与下一步

多视角/时序 grounding 的难点不是输入图片数量，而是 identity、geometry、time、mask 和 fusion contract 是否保持一致。Open X/WM-017 支持 heterogeneous schema 审计，Octo 提供 observation group/readout/attention 参照；它们不能替代用户项目的 per-view calibration、sync、ablation 和 replay evidence。PER-003 保持 `WARN`，对应题卡已生成并保持 `unseen`；下一步进行 PER-001..004 真实口述或补一个本地 multi-view artifact。

## References

1. [PER-003 Multi-view / Temporal Source Freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html)。
2. [Open X-Embodiment frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md)。
3. [Octo architecture/execution source audit](../sources/vol_03_architecture_execution_claim_to_code.html)。
4. [WM-017 heterogeneous schema source freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)。
5. [PER-001 Grounding / Coordinate Knowledge](vol_06_per001_grounding_coordinate.html) 与 [PER-002 3D Lift / Frame Knowledge](vol_06_per002_3d_lift_frame.html)。
6. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 与 [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
