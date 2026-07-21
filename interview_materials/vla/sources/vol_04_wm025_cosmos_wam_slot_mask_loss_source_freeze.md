# VOL 04 WM-025 Source Freeze：Cosmos/WAM Action、Future/World、Value 的 Slot、Mask 与 Loss

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-025 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-025  
> 本轮边界：冻结 Cosmos Policy/WAM 的统一 latent sequence、action/future/value slot、sample routing、condition mask、target loss mask 与 EDM loss；不把上游结构、公开分数或未核验本地 run 写成个人设计与结果。

## 1. 题目与核心结论

题目：**Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？**

核心结论：

1. **不是视频 backbone 后简单外挂三个独立 head。**frozen paper/code 将当前 proprio、相机、action chunk、future proprio/images 与 value 编排进同一 latent-video sequence；共享 diffusion transformer 通过输入 slot、condition mask、sample routing 和可选 target mask 切换 policy/world/value 角色。[S1]
2. **Slot 定义数据放在哪里，condition mask 定义哪些 slot 是已知条件，target loss mask 定义哪些预测误差进入反向。**三者属于不同层，不能把 mask=1 的 condition 语义直接当作 loss 权重。
3. **训练主项是 noise-weighted latent EDM MSE。**action/future/value 的 component L1/MSE 可用于日志诊断，但不等于主反向 loss；action_loss_multiplier 和 mask_loss_for_action_future_state_prediction 属于可选分支，必须核对主 config 与调用点。
4. **Dataset routing 决定样本承担哪种角色。**demo、success rollout、failure rollout 进入统一索引空间；base recipe 约形成 policy/world/value 50/25/25 的角色比例，但这只支持指定 frozen contract，不是所有 checkpoint 的通用事实。
5. **本地 WAM 项目目前只能安全说“按上游 contract 梳理/对齐 slot、mask、routing 与评测边界”。**raw config、run log、checkpoint、gradient trace、paired ablation 和 ownership 仍不完整，不能说本人设计三目标或证明 auxiliary objective 有收益。[S3]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Cosmos Policy paper + NVlabs/cosmos-policy claim-to-code audit | arXiv:2601.16163v1；repo commit 18a2accadf4e7a3531e56754102af5a24d2316da，Apache-2.0 | latent layout、action/value injection/extraction、dataset routing、condition mask、EDM loss、direct/planning contract | 用户本地 checkpoint/run、个人原创、公开结果是本地结果 | primary + official-code audit / WARN |
| S2 | WM-016 Joint Objective Source Freeze | 本地 canonical + review | shared representation、sample routing、condition/noise/target/metric mask 分层、reduction/gradient 审计模板 | WM-016 的抽象式就是所有 Cosmos config 的 exact loss | supporting / WARN |
| S3 | WAM Claim–Evidence Inventory | 2026-07-17/18 evidence audit | 上游机制已核；本地 raw bundle、ownership、MSE/success/0-success claim 风险与安全口径 | 历史数字、root cause 或个人模块已核实 | local evidence / WARN |
| S4 | WM-024 Reward / Value / Success / Termination | 本地 canonical + review | value/return、success、termination 的语义分离和 calibration 要求 | value frame 是校准 success probability | supporting / WARN |
| S5 | Benchmark / Evidence + WM-019 Metric Boundary | 本地 frozen audits | component loss、future proxy、direct success、planning score 的 metric ladder | 离线 component loss 下降证明闭环提升 | supporting / WARN |

## 3. 概率角色与统一布局

令 \(s=(o,p,c)\) 表示当前 cameras、proprio 和任务文本，\(a\in\mathbb R^{K\times D_a}\) 是 action chunk，\(s'\) 是 \(t+K\) 的 future proprio/images proxy，\(G\) 是 rollout return。frozen paper 将三种角色写成：

\[
\begin{aligned}
\text{policy: }&p_\theta(a,s',G\mid s),\\
\text{world: }&p_\theta(s',G\mid s,a),\\
\text{value: }&p_\theta(G\mid s,a,s').
\end{aligned}
\]

变量解释：同一个 \(\theta\) 表示共享 diffusion backbone；角色差异来自哪些 slot 被提供为 clean condition、哪些 slot 需要 denoise/predict。这里的 \(s'\) 是 future observation proxy，不是可直接读取的完整 simulator state；\(G\) 是指定 return contract，不自动等于成功概率。

冻结 layout：

| Suite | 语义 slot 顺序 | action/proprio |
| --- | --- | --- |
| LIBERO | blank、current proprio、wrist、primary、action、future proprio、future wrist、future primary、value | action 16×7；proprio 9D |
| RoboCasa | blank、current proprio、wrist、left primary、right primary、action、future proprio、future wrist、future left、future right、value | action 32×7；proprio 9D |

每个语义 frame 对应 \(16\times28\times28\) latent volume；tokenizer 的 temporal compression 使输入按重复 semantic frame 组织为指定长度。这个 layout 是 frozen commit 的实现事实，不能外推为所有 video-VLA。

## 4. Action、Future 与 Value 如何进入 slot

### 4.1 Action

归一化 action chunk \(A\in[-1,1]^{K\times D_a}\) 被 flatten、重复并填入 action latent volume；提取时只保留可组成完整 action copy 的元素，reshape 后跨 copy 求均值，再按 dataset actions_min/actions_max 反归一化。[S1]

因此 action slot 的审计必须包含：\(K,D_a\)、normalizer revision、latent index、完整 copy 数、尾部不完整片段、round-trip error、controller mapping。它不是一个 action-specific learned encoder，也不能跳过 statistics 文件。

### 4.2 Future/world

future target 由 \(t+K\) 的 proprio 和 camera observations 构成。episode 尾部会 clamp 到最后一帧，action 不足会重复最后动作；frozen behavior 没有独立 valid-step mask，因此 terminal padding 可能作为真实 target 参与训练。future image 解码前还要恢复 blank/proprio/action 位置的 clean placeholder latent。

### 4.3 Value

value scalar 扩展到整个 value frame；采样后对 value frame 求均值，并从 \([-1,1]\) 映射/clip 到 \([0,1]\)。value label 使用 future index 对应的 return。value slot 的低 loss 或高 score只证明指定 latent/return contract 的拟合或排序信号，不证明 closed-loop success。

## 5. 四种 mask / routing 不可混淆

| 层 | 回答的问题 | Frozen Cosmos/WAM 语义 | 常见错误 |
| --- | --- | --- | --- |
| sample routing | 这条样本扮演什么训练角色？ | demo / world rollout / value rollout / V/Q variant | 只看 batch 名称，不看 role flag |
| condition/input mask | 哪些 slot 保持 clean、哪些需生成？ | mask=1 表示 clean condition，mask=0 表示 denoise/predict | 当成 attention mask 或 loss mask |
| target loss mask | 哪些预测元素进入反向 reduction？ | 可选按 policy/world/value 保留 action/future/value target | 看到配置名就断言主实验启用 |
| metric mask | 日志统计哪些 component？ | action/future/value L1/MSE、planning/direct metrics | 把日志 L1 当主训练 loss |

角色到 condition 的映射：

| 角色 | Clean condition | 主要 target |
| --- | --- | --- |
| policy demo | current state \(s\) | action、future、value 可联合生成 |
| world rollout | current state + action | future proprio/images；value 可 auxiliary |
| value rollout | full prefix \(s,a,s'\) | value frame |
| state-value variant | future state only | \(V(s')\)，mask current/action |
| Q variant | current state + action | \(Q(s,a)\)，mask future state |

get_data_and_condition 对 world sample 把 action slot 置 clean，对 value sample 把除 value 之外的 slots 置 clean；V/Q variant 再改变 current/action/future 的 input mask。必须把 mask 类型、1/0 方向、shape、dtype 和 slot index 一起记录。

## 6. Loss 与 reduction

frozen training 先得到 clean latent \(x_0\)，按 HybridEDMSDE 产生 noisy \(x_t\)，denoiser 预测 \(\hat x_0\)。主项可抽象为：

\[
\mathcal L_{\mathrm{EDM}}=
\frac{\sum_{b,t,c,h,w}
m_{b,t}\,w(\sigma_{b,t})
\left(x_{0,bcthw}-\hat x_{0,bcthw}\right)^2}
\sum_{b,t,c,h,w}m_{b,t}}.
\]

变量解释：\(m_{b,t}\) 是真正参与 loss 的 latent-frame target mask，\(w(\sigma)\) 是 noise-level weight；实现必须核对 empty mask、denominator、dtype 和 distributed reduction。该式是审计化表达，不能据此声称所有 frozen config 都启用了同一 target mask。

当 mask_loss_for_action_future_state_prediction 打开时，可让 demo 只保留 action slot、world sample 只保留 future slots、value sample 只保留 value slot。代码还支持 action_loss_multiplier。当前 audit 没有确认该 target-mask flag 是所有官方 checkpoint 的主训练默认，因此回答必须说“可选分支 + 需查 config”。

各 action/future/value component L1/MSE 是诊断 metric；主反向项仍是 noise-weighted latent MSE。README 的 action L1 经验阈值也不能替代 checkpoint、closed-loop success 或 early-stopping 充分条件。

## 7. Routing、padding 与 mask 的最小单测

1. **Slot round-trip**：action normalize→inject→extract→denormalize；value scalar→frame→scalar；检查 shape、finite、误差与尾部 copy。
2. **Role matrix**：各取一条 demo、world rollout、value rollout、V/Q sample，打印 role flag、clean condition slots、target slots、sigma 与 loss denominator。
3. **Non-zero gradient**：对 action/future/value target 分别检查 masked loss、gradient norm 与 shared backbone gradient；empty mask 必须 fail-fast。
4. **Padding A/B**：episode 尾部 repeated action/future 与 valid-step masked 版本配对，检查 component loss 和 closed-loop 影响。
5. **Objective ablation**：action-only、+world、+value、all；固定 dataset split、checkpoint init、steps、scheduler、normalizer 和 eval protocol。

## 8. 项目真实性边界

WAM inventory 的当前安全口径是：上游 slot/mask/routing 已核实，个人可以解释并设计审计；当前工作区的 WAM raw run bundle、可加载 checkpoint、exact local config、loss/gradient trace、closed-loop paired ablation 和 ownership 未闭合。外部 CoffeePressButton diagnostic 仅支持部分 trace/proxy，checkpoint 与目标 metric 仍未验证。

因此面试可说：

> “我按 frozen Cosmos contract 梳理了 action/future/value 的 latent slots、condition/loss mask、sample routing、normalization 与 eval gate，并把缺失 artifact 列成单测和 paired ablation。”

不能说：

> “我原创设计三个 head，并证明 world/value auxiliary 提升了成功率。”

## 9. Source gate 结论

本 source freeze 为 WARN：三种概率角色、LIBERO/RoboCasa layout、action/future/value 注入、condition/target/metric mask、EDM loss 与最小单测已冻结；主 checkpoint 的 exact config、local runtime gradient、paired ablation、closed-loop result 和 ownership 仍缺。下游知识页和题卡只能写机制与审计合同。

## 参考来源

1. [Cosmos Policy / WAM claim-to-code audit](vol_04_cosmos_policy_wam_claim_to_code.html)。
2. [WM-016 Joint Objective Source Freeze](vol_04_wm016_joint_objective_source_freeze.html)。
3. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
4. [WM-024 Reward / Value / Success / Termination](../knowledge/vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)。
5. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
6. [Benchmark / Evidence audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
