# VOL 04 World Model / Sim2Real：Cosmos/WAM Action、Future、Value 的 Slot、Mask 与 Loss（WM-025）

> 状态：drafted / VLA-WM-025 / knowledge_27_of_44 / card_synced / WARN  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：解释 frozen upstream contract 与项目审计，不把公开机制称个人原创或本地收益。  
> 前置：[WM-024 Reward / Value / Success / Termination](vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)、[WM-025 Source Freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。

## 问题（Question）

Cosmos/WAM 的 action、future/world、value 三类目标怎样映射到数据 slot、mask 和 loss？高分回答要按“概率角色 → latent layout → sample routing → condition mask → target loss mask → metric/gradient”逐层展开。

## 1. 先纠正“三个 head”

初级回答可以说模型同时处理 action、world 和 value；实现级回答不能说成“视频 backbone 后挂三个独立 head”。frozen Cosmos Policy 将 current proprio/cameras、action chunk、future proprio/images 和 value 都编码进统一 latent-video sequence，共享 diffusion transformer；角色由 slot、condition mask、sample routing 和可选 target mask 决定。[1]

\[
\begin{aligned}
\text{policy: }&p_\theta(a,s',G\mid s),\\
\text{world: }&p_\theta(s',G\mid s,a),\\
\text{value: }&p_\theta(G\mid s,a,s').
\end{aligned}
\]

变量解释：\(s\) 是当前 observation/proprio/language，\(a\) 是 action chunk，\(s'\) 是 \(t+K\) future observation proxy，\(G\) 是 rollout return；三种角色共享参数 \(\theta\)，但 clean conditions 和 denoise targets 不同。该式不代表一个 joint loss 自动获得 planning 能力。

## 2. Frozen slot layout

| Suite | Slot 顺序 | 关键 shape |
| --- | --- | --- |
| LIBERO | blank、current proprio、wrist、primary、action、future proprio、future wrist、future primary、value | action 16×7；proprio 9D |
| RoboCasa | blank、current proprio、wrist、left primary、right primary、action、future proprio、future wrist、future left、future right、value | action 32×7；proprio 9D |

每个 semantic frame 对应 \(16\times28\times28\) latent volume。这个 layout 是 frozen commit 的事实，不是所有 video-VLA 的标准。

### 2.1 Action slot

action \(A\in[-1,1]^{K\times D_a}\) 先 flatten，再重复填入 action latent volume；提取时取完整 copies，reshape 后平均，最后按 dataset actions_min/actions_max 反归一化。审计项包括 \(K,D_a\)、latent index、normalizer revision、完整 copy 数、round-trip error 和 controller mapping。

### 2.2 Future/world slots

future target 是 \(t+K\) 的 proprio 和 camera observations，不是完整 simulator state。episode 尾部会 clamp，action 不足会重复最后一步；缺少 valid-step mask 时，padding 可能污染 future/action target。future image 解码还要恢复非图像 slot 的 placeholder latent。

### 2.3 Value slot

value scalar 被扩展到整个 value frame；采样后对 frame 求均值，并映射/clip 到 \([0,1]\)。label 使用 future index 的 return。value frame 高分只能证明指定 scorer 的输出，不能直接等价于 calibrated success probability。

## 3. 四个容易混淆的开关

| 名称 | 它决定什么 | Cosmos/WAM 实例 | 不是 |
| --- | --- | --- | --- |
| sample routing | 一条 sample 扮演 policy/world/value 哪种角色 | demo、success/failure rollout、V/Q variant | loss 权重 |
| condition mask | 哪些 slot 是 clean known condition | mask=1 clean，mask=0 denoise/predict | attention mask、target loss mask |
| target loss mask | 哪些预测误差进入反向 | 可选保留 action/future/value 对应 slots | sample role 本身 |
| metric mask | 日志统计哪些 component | action/future/value L1/MSE | 主 EDM loss 或闭环成功率 |

回答 mask 时必须带上：mask 名称、1/0 语义、shape、slot index、作用位置、reduction denominator 和 config revision。

## 4. Role 到 condition/target 的映射

| 训练角色 | Clean condition | 主要 target / 用途 |
| --- | --- | --- |
| policy demo | current state \(s\) | action、future、value 可联合生成 |
| world rollout | current state + action | future proprio/images；value 可 auxiliary |
| value rollout | full prefix \(s,a,s'\) | value frame |
| state-value variant | future state only | \(V(s')\)，mask current/action |
| Q variant | current state + action | \(Q(s,a)\)，mask future |

base dataset 将 demo、success rollout、failure rollout 编入索引；指定 recipe 约形成 policy/world/value 50/25/25 的角色比例。future index 固定在 \(t+K\)，尾部 clamp；这两点都必须与 checkpoint/config 一起冻结。

## 5. Loss：主训练项不等于 component L1

clean latent \(x_0\) 经 HybridEDMSDE 得到 noisy \(x_t\)，denoiser 输出 \(\hat x_0\)。审计化主项：

\[
\mathcal L_{\mathrm{EDM}}=
\frac{\sum m_{b,t}\,w(\sigma_{b,t})
\lVert x_{0,b,t}-\hat x_{0,b,t}\rVert_2^2}
\sum m_{b,t}}.
\]

变量解释：\(m_{b,t}\) 是 target loss mask，\(w(\sigma)\) 是 noise-level weight；实现还要核对 spatial/channel reduction、empty mask、dtype 和 distributed all-reduce。它不是“action loss + future loss + value loss 三个标量简单相加”的充分描述。

可选 mask_loss_for_action_future_state_prediction 分支能让 demo 只保留 action slot、world sample 只保留 future slots、value sample 只保留 value slot；action_loss_multiplier 可重权 action slot。但 frozen audit 未证明该 target-mask flag 是所有官方 checkpoint 的统一默认，面试必须说“需查 exact config”。

component action/future/value L1/MSE 是诊断日志；主反向 loss 是 noise-weighted latent MSE。component loss 下降不能直接证明 direct-policy success 或 planning uplift。

## 6. 可审计伪代码

```python
def route_and_mask(sample, layout, config):
    # 1. Resolve the sample role before constructing any condition/loss mask.
    role = resolve_role(sample, config.routing)
    clean = encode_slots(sample, layout)

    # 2. Build clean-condition slots; mask=1 means known condition here.
    condition_mask = build_condition_mask(role, layout, config)
    noisy = add_edm_noise(clean, condition_mask, config.sde)

    # 3. Build a separate target mask for the backward reduction.
    target_mask = build_target_mask(role, layout, config)
    prediction = denoise(noisy, condition_mask)
    loss = masked_weighted_mse(prediction, clean, target_mask)

    # 4. Log component metrics without calling them the main training loss.
    metrics = component_metrics(prediction, clean, layout)
    return loss, metrics, role, condition_mask, target_mask
```

伪代码的关键是先 route，再分别构造 condition mask 和 target mask；日志 metric 单独计算。真实实现还需要输出每个 slot 的 non-zero gradient、denominator、sigma 和 normalizer revision。

## 7. 最小单测与失败模式

| 检查 | 目的 | 失败信号 |
| --- | --- | --- |
| action/value round-trip | 验证 inject/extract/normalizer | shape 对但数值错、gripper/axis 漂移 |
| role×slot matrix | 验证 clean/target 组合 | world sample 更新 action 或 value sample 更新 future |
| non-zero gradient | 验证目标真的进入反向 | 配置打开但 gradient 为零 |
| empty-mask fail-fast | 防止 denominator=0/NaN | silent zero loss 或跨 rank 不一致 |
| terminal padding A/B | 检查 repeated terminal target | 尾部 loss 虚低/虚高 |
| action-only/+world/+value/all | 判断 auxiliary 因果影响 | component loss 好但 action success 不变 |

常见错误：

- 把 condition mask 当 attention mask；
- 把 mask=1 的 clean condition 当成“这个 slot 参与 loss”；
- 只看配置名，不查 exact branch、调用点和主 config；
- 把 action/future/value L1 当主 EDM loss；
- 把统一 latent sequence 说成个人原创三个 head；
- 把公开 checkpoint 或历史 claim 写成本地结果。

## 8. 项目挂钩与安全口述

当前 WAM inventory 的最强证据是 upstream mechanism audit 与项目证据合同；本地 raw config/run/checkpoint/gradient/paired ablation 和 ownership 仍不闭合。CoffeePressButton diagnostic 只支持部分 trace/proxy，不能证明 WM-025 的 exact training route。

安全口述：

> “我按 frozen Cosmos contract 梳理了统一 latent sequence 中 action/future/value 的 slot、condition/loss mask 和 sample routing，并设计了 round-trip、role×slot、non-zero-gradient 与 action-only/+world/+value/all 的审计矩阵。”

危险口述：

> “我原创了三个 head，并证明 world/value auxiliary 提升成功率。”

## 9. 结论

高分回答的顺序是：**先讲三种概率角色，再讲 slot layout，然后拆 sample routing、condition mask、target loss mask 和 metric，最后讲 EDM reduction、padding/normalizer/gradient 单测与项目证据边界。**

本节点保持 WARN，题卡保持 unseen；真实口述前不创建 coaching state。

参考：[WM-025 Source Freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)、[Cosmos/WAM audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)、[WM-016](vol_04_world_model_sim2real_wm016.html)、[WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[WM-024](vol_04_world_model_sim2real_wm024_reward_value_success_termination.html)。
