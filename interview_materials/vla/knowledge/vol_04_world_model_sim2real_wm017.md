# VOL 04 World Model / Sim2Real：Heterogeneous Embodiment Schema（WM-017）

> 状态：`drafted / knowledge_19_of_44 / card_deferred / WARN`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-WM-017`；本轮只生成 knowledge node，不生成题卡，不创建 coaching state。  
> 前置：[WM-016 Joint Objective](vol_04_world_model_sim2real_wm016.html)、[WM-017 Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)、[UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。

## 问题（Question）

heterogeneous robots 的 camera、state、action 和 horizon 如何统一而不污染 world loss？核心不是把不同机器人 zero-pad 成同一 shape，而是同时冻结字段语义、坐标/单位、时间、有效性 mask、embodiment condition、normalizer、prediction target 和 reduction。

## 证据边界与学习位置

```text
WM-015 video/action coupling
                 ↓
WM-016 joint objective / mask / reduction
                 ↓
WM-017 heterogeneous camera/state/action/horizon schema
                 ↓
WM-018 horizon trade-off；WM-019 metric boundary；WM-020 bad cases
```

本页的来源边界：

- Open X-Embodiment frozen README 支持 RLDS episode/step 容器、dataset metadata 入口，以及 RT-1-X 的 workspace RGB/task string/7D action 说明；不支持所有子数据集共享 camera、action semantics 或 horizon。[1][2]
- UWM frozen code 同时存在 LIBERO [7] action 与 DROID [10] action；`action_len=16`、`num_frames=19` 是配置合同，不是跨 embodiment 方法常数。[3]
- 用户项目的 adapter、normalizer、checkpoint 和跨机器人结果仍需本地 artifacts；本页不把 Open X 统一格式写成个人已完成的转换工程。[4]

## 1. 统一容器不等于统一语义

Open X-Embodiment 用 RLDS episode 形式组织 step 序列，便于下游读取；这解决的是 container/schema 的互操作性。它没有自动解决以下问题：

1. action 是 absolute、delta 还是 velocity；
2. gripper 值是 opening、binary command 还是另一种 actuator convention；
3. state 是 proprio、机器人状态还是 simulator ground truth；
4. workspace、wrist、agentview 的视角、内外参和 crop 是否一致；
5. control frequency、action repeat、timestamp 与 history/future horizon 是否一致。

RT-1-X README 只描述 workspace RGB camera 和 task string，明确不接 wrist camera 或 depth；它的 7 个变量也不能外推为所有机器人 action 维度。面试中应把“官方示例的输入合同”与“跨 embodiment 统一合同”分开。

## 2. 七层 schema 合同

| 层 | 要冻结的字段 | 未冻结时的风险 | 必要证据 |
| --- | --- | --- | --- |
| 语义 | action/state/gripper 的单位和含义 | 同名 action 被错误拼接 | dataset card、adapter、unit test |
| 几何 | camera intrinsics/extrinsics、frame、axis、flip/crop | wrist 与 workspace 或左右视角混淆 | calibration manifest、round-trip |
| 时间 | timestamp、control Hz、action repeat、history/future、terminal | index 代替时间；重复 terminal 被当 target | timestamp/valid-step audit |
| 形状 | camera 数量、resolution、state/action dim、chunk | zero-pad 没有 valid-axis mask | shape manifest、field mask |
| 条件 | embodiment/robot/task/camera availability | missing modality 只填零，模型学 zero shortcut | presence mask、condition token |
| 归一化 | per-source/per-robot stats、clipping、dtype | 不同 unit/range 共用错误统计量 | stats SHA、round-trip |
| 目标 | video latent、action、value、continuation 与 reduction | padding/缺失输入进入 world loss | target mask、有效分母、分源 loss |

这七层是审计清单，不是要求所有项目最终使用同一表示。统一前先保留 source metadata，统一后仍能追溯原始字段。

## 3. Batch 合同与 mask

可以用如下抽象 batch 表达“同 shape 但语义仍可追溯”：

\[
\mathcal{B}=\{x_{b,t},m^{obs}_{b,t},m^{act}_{b,t},e_b,\tau_{b,t},s_b\}.
\]

变量解释：(x) 是转换后的观测/动作字段；(m^{obs})、(m^{act}) 是观测和动作有效 mask；(e_b) 是 embodiment/task condition；(	au) 是 timestamp；(s_b) 是 source、normalizer、version metadata。直觉是 padding 只改变存储 shape，mask 和 metadata 才保留语义。实现映射是 dataset adapter、collator、normalizer registry、model condition 和 loss reduction。

### 3.1 Missing modality

如果机器人没有 wrist camera，直接用零图像会让模型把“全零”误当作稳定的视觉模式。更安全的做法是：保留 camera-presence mask 或 condition token，并在目标构造时防止缺失 frame 进入 video/world loss；评估时要单独报告 workspace-only、wrist-only、both 和 missingness 条件。

### 3.2 Terminal padding

不同 episode 的 horizon 不同时常需要 padding。padding action、重复最后一帧或 repeated terminal action 都必须带 valid-step mask；否则 world loss 会把“没有真实未来”的复制值当成真实 transition。mask 应参与 reduction，而不是只在 dataloader 中记录后丢失。

## 4. Action 与 horizon 的对齐

UWM 的 LIBERO 与 DROID shape 已显示：action dimension 可为 [7] 或 [10]，而 `action_len=16` 属于 frozen config。跨机器人 adapter 必须显式记录：

- action dimension 与每一维单位；
- absolute/delta/velocity 语义；
- rotation representation 与 gripper convention；
- control frequency、timestamp 和 action repeat；
- history length、future length、chunk length 与 replan horizon；
- normalize/denormalize 的统计量、版本和 clipping。

若只在最后补零，模型无法知道缺少的是维度、时间步还是 modality。应保留 `valid_axis_mask`、`valid_step_mask` 和 `camera_presence`，并在 action execution 前做 normalize→denormalize→controller round-trip。

## 5. 不污染 world loss 的训练路径

1. **数据入口**：adapter 输出 canonical fields、source id、embodiment id、camera presence、timestamp 和 valid masks。
2. **模型入口**：missing camera/state 使用 presence token/mask；action 与 future video 保持各自 schema。
3. **目标构造**：terminal padding、缺失 camera、无 action sample 不得静默进入对应 world/action loss。
4. **归一化**：按 source/robot 记录 stats SHA，不把不同单位混用同一统计量。
5. **聚合**：记录 per-source/per-embodiment loss 和有效元素分母，再决定 weighting；数据最多的来源不能自动定义 joint objective。
6. **评估**：按 embodiment、camera availability、horizon 和 task family 分层，不能只报混合平均值。

## 6. 最小审计伪代码

```python
def convert_and_mask(step, adapter, normalizers):
    # 1. Preserve source and embodiment metadata before tensor padding.
    item = adapter.to_canonical(step)

    # 2. Convert units/frames and retain explicit presence/valid masks.
    item = adapter.align_geometry_and_time(item)
    item["action"] = normalizers[item["source_id"]].normalize(item["action"])

    # 3. Padding changes shape only; invalid steps must not become targets.
    item["target_mask"] = item["valid_step_mask"] & item["camera_presence"]
    return item

def aggregate_world_loss(items, per_element_loss):
    # 4. Aggregate by valid elements and report source/embodiment strata.
    return masked_mean(per_element_loss, items["target_mask"])
```

代码映射：`to_canonical` 是字段语义转换，`align_geometry_and_time` 处理 frame/timestamp，normalizer 必须按 source/robot 绑定，`target_mask` 才能进入最终 reduction。伪代码不声称某个现有项目已经实现这些接口；它是审计与设计模板。

## 7. 评估与失败诊断

| 症状 | 优先检查 | 不应直接结论 |
| --- | --- | --- |
| 混合 loss 下降、某机器人 success 降 | per-embodiment loss、normalizer、action semantics、camera presence | 统一训练无效 |
| video loss 降、contact fail | camera/frame、horizon、control Hz、terminal mask | world model 学坏 |
| action round-trip 失败 | absolute/delta/velocity、axis、gripper、stats SHA | policy head 不兼容 |
| 长 horizon 末端漂移 | timestamp、repeat、valid-step、replan horizon | 模型容量不足 |
| 缺 wrist camera 时性能异常 | presence token、zero shortcut、camera-specific normalization | 数据质量差 |

最小实验队列：schema manifest、normalize/denormalize/controller round-trip、terminal-mask loss A/B、camera presence ablation、per-embodiment weighted/unweighted loss、fixed/variable-horizon paired rollout 和 timestamp/control-frequency smoke。

## 8. 项目挂钩与真实性边界

UWM/LIBERO 项目可讲 action/history/normalizer/reset/checkpoint/rollout protocol 的核对；不能声称已经完成 Open X-style 全数据统一。OpenPiVLA、WAM、Harness 的 camera/action schema 必须分别回到 config、processor、controller 与 eval wrapper 取证；它们都叫 `action` 不代表语义相同。

任何“跨 embodiment 统一提升”都需要 per-source/per-robot result、有效分母、normalizer/version 和 paired protocol。混合 world loss 下降只能说明训练信号变化，不能直接证明跨机器人 success 提升。

## 9. 结论与后续

WM-017 的核心答案是：统一 episode container 和字段入口，但保留 action/camera/state/horizon 的语义、单位、时间、presence/valid mask、normalizer 和 source metadata；只有在 target mask 与有效分母正确后，才聚合 world/action loss，并按 embodiment 分层评估。

本节点为 `WARN`：Open X 与 UWM 的公开 schema 边界已核验，adapter manifest、round-trip、terminal-mask A/B、per-embodiment eval 和个人项目统一证据仍 pending。本轮不生成 WM-017 题卡；下一步可单独生成一张保持 `unseen` 的题卡。

## 参考文献（References）

1. [Open X-Embodiment frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md)。
2. [Open X-Embodiment / RT-X paper landing page](https://robotics-transformer-x.github.io/)。
3. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。
4. [WM-017 Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)。
5. [UWM/LIBERO evidence inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
