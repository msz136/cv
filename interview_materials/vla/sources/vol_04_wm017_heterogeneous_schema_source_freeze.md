# VOL 04 WM-017 Source Freeze：Heterogeneous Embodiment Schema

> 审计日期：2026-07-17  
> 状态：`source_frozen / cross-embodiment / WARN`  
> 覆盖题目：`VLA-WM-017`  
> 本轮边界：只冻结 camera、state、action、horizon 的 schema 与证据边界；不生成 knowledge page，不生成题卡。

## 1. 问题与结论边界

题目：**heterogeneous robots 的 camera、state、action 和 horizon 如何统一而不污染 world loss？**

“统一格式”不等于把所有机器人强行 pad 成同一张量。安全的统一至少要分成：语义字段、坐标/单位、有效性 mask、时间对齐、embodiment/task condition、prediction target 与 loss reduction。缺少任何一层，都可能把 padding、重复 terminal action、相机缺失或不同 action semantics 当成真实监督。

本轮冻结的最小结论：

1. Open X-Embodiment 官方仓库把开源机器人数据组织为 RLDS episode 序列，目标是提供统一格式供下游消费；这支持 episode/step 级 schema 统一，不支持所有数据拥有相同 camera、action semantics 或 horizon。[S1]
2. 官方 RT-1-X README 只描述一个 workspace RGB camera、task string 和 7 个 gripper action 变量；它明确不接 wrist camera、depth，也说明 action 可是 absolute、delta 或 velocity。不能把 RT-1-X 的 7D 解释为所有 embodiment 的通用 action contract。[S1]
3. UWM frozen config 同时出现 LIBERO [7] action 与 DROID [10] action 的差异；其 `action_len=16`、`num_frames=19` 等是配置合同，不是跨机器人方法常数。[S2]
4. world/video loss 只应在字段语义、有效 frame/step、camera transform、normalizer、horizon 和 target mask 对齐后聚合；统一 padding 本身不能证明可比性。[S2][S3]

## 2. 来源冻结

| ID | 来源 | revision / fingerprint | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment) | `9eeb68b989efbcf474e8fb9019e01d02b962a604`；README SHA `E7DBF6BB04559E981B7EAB2E0F4510579BF82B09948A0FE6471BA1794F86AE59`；LICENSE SHA `CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30` | RLDS episode structure、dataset list/metadata入口、RT-1-X observation/action README、Apache-2.0 software / CC-BY other-material boundary | 所有子数据集已同一 camera、action units、horizon 或 quality | checked / WARN |
| S2 | [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html) | UWM `b7d4067c8859775e5b08f681e76d538015cdd445` | LIBERO/DROID shape、action_len、obs/future frame contract、normalizer 与 action-free tuple | 跨数据集自动可比、个人项目数据已统一 | checked / WARN |
| S3 | [WM-016 Joint Objective Source Freeze](vol_04_wm016_joint_objective_source_freeze.html) | 本仓库 canonical freeze | target mask、route、reduction、prediction target 的审计框架 | runtime gradient、paired ablation、checkpoint lineage | checked / WARN |
| S4 | [Open X-Embodiment paper / RT-X](https://robotics-transformer-x.github.io/) | primary paper landing page | 跨数据集联合训练的 motivation 与数据规模方向 | 本地转换脚本、每个数据集的字段事实 | supporting / WARN |
| S5 | [UWM/LIBERO inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | local evidence | 用户项目 action/history/normalizer/checkpoint/protocol 的证据缺口 | 上游 Open X schema 已在本地完整实现 | local / WARN |

## 3. Schema 分层

| 层 | 必须冻结的字段 | 常见污染方式 | 最小审计 |
| --- | --- | --- | --- |
| 语义 | action 是 absolute/delta/velocity？gripper 是 opening/command？state 是 proprio 还是 simulator state？ | 把同名 `action` 直接拼接 | dataset card + conversion code + unit test |
| 几何 | camera intrinsics/extrinsics、world/robot/camera frame、axis convention、image flip/crop | 把 wrist/agentview 或左右手相机当同一视角 | calibration manifest + pixel/pose round-trip |
| 时间 | control Hz、frame timestamp、action repeat、history/future horizon、terminal padding | 以 index 代替 timestamp；把 repeated terminal action 当真实 target | timestamp delta、valid-step mask、terminal audit |
| 形状 | camera count/resolution、state/action dim、chunk length | zero-pad 后不记录 valid axis | shape manifest + per-field mask |
| 条件 | embodiment id、task language、camera availability、robot family | 用 zero 填 missing modality 却不提供 missingness signal | explicit presence mask / condition token |
| 归一化 | min/max、mean/std、per-dataset/per-robot stats、clipping | 共享一个统计量覆盖不同 unit/range | normalize→denormalize round-trip |
| 目标 | video latent、action、reward/value、continuation | padding/missing camera 进入 world loss | target mask、reduction denominator、per-source loss |

## 4. 统一与不统一的边界

可统一的是：RLDS episode/step container、字段命名约定、timestamp/valid mask、task/embodiment metadata、转换与 manifest 版本。不能未经证据统一的是：camera 数量与视角、action dimension、坐标系、absolute/delta/velocity 语义、gripper semantics、control frequency、horizon 和 normalizer。

一个安全的 batch 合同可以写成：

\[
\mathcal{B}=\{x_{b,t},\ m^{obs}_{b,t},\ m^{act}_{b,t},\ e_b,\ \tau_{b,t},\ s_b\},
\]

其中 (x) 是经过 schema conversion 的字段，(m^{obs}) 与 (m^{act}) 是观测/动作有效 mask，(e_b) 是 embodiment condition，(	au) 是 timestamp，(s_b) 是 source/normalizer/version metadata。直觉是“padding 只是存储形状，mask 和 metadata 才保留语义”。实现映射是 collator、dataset adapter、normalizer registry 和 loss reduction；若这些字段未进入模型或 loss，统一容器并不能消除分布差异。

## 5. 防止 world loss 被污染

1. **数据入口**：转换脚本输出 canonical fields、source id、embodiment id、camera presence、timestamp 和 valid masks。
2. **模型入口**：missing camera/state 使用显式 presence token/mask，不能只用零值；action 与 future video 保留各自 schema。
3. **目标构造**：对每个 modality/axis 使用有效 target mask；terminal padding、缺失相机和无 action sample 不得静默进入 world loss。
4. **归一化**：按数据源/机器人记录 stats SHA；在 action execution 前做反归一化 round-trip。
5. **聚合**：记录 per-source/per-embodiment loss 与有效元素分母，再决定是否加权；不能让样本数最多的数据源自动定义“统一目标”。
6. **评估**：按 embodiment、camera availability、horizon、task family 分层报告，不能只报混合平均值。

## 6. 证据与实验队列

| 优先级 | 检查 | 目的 | 当前状态 |
| --- | --- | --- | --- |
| P0 | 每个 dataset adapter 输出 schema manifest（camera/state/action/horizon/unit/frame/normalizer） | 证明转换没有静默改语义 | pending |
| P0 | action normalize→denormalize→controller round-trip | 发现 absolute/delta/velocity、axis、gripper 错位 | pending；UWM inventory 仍缺完整 bundle |
| P0 | valid-step/terminal padding mask 的 loss A/B | 证明 world loss 不吃重复 terminal target | pending |
| P1 | camera ablation：workspace only / wrist only / both / missingness token | 区分视觉信息缺失与 zero-padding shortcut | pending |
| P1 | per-embodiment loss 与 mixed-loss weighted/unweighted 对照 | 发现大数据源或长 horizon 主导 joint objective | pending |
| P1 | fixed-horizon 与 variable-horizon paired rollout | 检查 horizon conversion 是否改变 policy/world behavior | pending |
| P2 | timestamp jitter、control-frequency 和 action-repeat smoke | 评估时间对齐与 latency gap | pending |

## 7. 项目证据边界

- UWM/LIBERO inventory 可以支持 action/history/normalizer/reset/checkpoint/protocol 的核对与缺口，不支持声称已完成 Open X-style 全数据统一。
- OpenPiVLA、WAM、Harness 的 camera/action schema 必须分别从各自 config、processor、controller 和 eval wrapper 取证；不能因为都叫 `action` 就合并。
- 任何跨 embodiment 的“统一提升”都需要 per-source/per-robot result、有效分母、normalizer/version 和 paired protocol；混合 loss 下降不等于跨机器人 success 提升。

## 8. Review 结论与下一步

本 source freeze 为 `WARN`：Open X 官方 RLDS/RT-1-X schema 与 UWM 的 LIBERO/DROID shape 差异已冻结，camera、state、action、horizon、mask、normalizer 和 loss aggregation 的审计清单已建立；本地 adapter、round-trip、terminal-mask A/B、per-embodiment evaluation 与个人项目统一证据仍 pending。

本轮已完成 `knowledge/vol_04_world_model_sim2real_wm017.*` 与 `questions/vol_04_world_model_sim2real_wm017.*`；下一步进行 WM-015/016/017 真实口述，WM-018..038 继续后置。

## 参考来源

1. [Open X-Embodiment frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md)。
2. [Open X-Embodiment frozen LICENSE](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/LICENSE)。
3. [Open X-Embodiment / RT-X paper landing page](https://robotics-transformer-x.github.io/)。
4. [UWM Source Audit B](vol_04_uwm_video_action_claim_to_code.html)。
5. [WM-016 Joint Objective Source Freeze](vol_04_wm016_joint_objective_source_freeze.html)。
6. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
