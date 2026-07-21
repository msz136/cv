# VOL 04 WM-020 Source Freeze：Posterior Collapse、Action Ignoring 与 Shortcut Diagnostics

> 审计日期：2026-07-18  
> 状态：`source_frozen / VLA-WM-020 / knowledge_synced / card_synced / WARN`  
> 覆盖题目：`VLA-WM-020`  
> 本轮边界：冻结四类 failure mode 的定义、可观测信号与最小诊断矩阵；不把未运行的 probe、world-model loss 或项目结果写成已验证结论。

## 1. 问题与结论边界

题目：**怎样发现 posterior collapse、action ignoring、future leakage 与 background shortcut？**

冻结结论：

1. posterior collapse 是 latent posterior 不再携带有用信息、趋近 prior 或 decoder 主要依赖 deterministic/context path 的训练失败；不能只凭 KL 低或 reconstruction 好下结论。[S1][S2]
2. action ignoring 是模型在预测未来时对 action 条件不敏感，可能表现为 action swap、magnitude sweep 后预测变化很小；“action-conditioned”字段存在不等于真正可干预。[S1][S3]
3. future leakage 是训练/评估输入通过 terminal frame、未来轨迹、错位 history、label shift 或非因果 mask 获得了本不该可见的信息；teacher-forced accuracy 高不能排除它。[S4][S5]
4. background shortcut 是模型用背景、相机、光照、桌面或数据采集批次等与标签相关但非任务因果的特征做预测；需要 counterfactual background、camera/domain split 或 object/action masking 才能定位。[S1][S3]
5. 四类 failure 必须分开做 intervention、control、split 和 rollout tests；单一 pixel/latent/action loss 不能区分 representation、causal action、leakage 与 shortcut。

## 2. 来源冻结

| ID | 来源 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- |
| S1 | [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html) | action-conditioned world-model contract、one-step/open-loop gap、model exploitation、action sensitivity 与长期 rollout 的诊断边界 | 用户项目已经发现某种 failure、任意 probe 的数值阈值 | checked / WARN |
| S2 | [DreamerV3 independent fact review](vol_04_world_model_foundations_independent_fact_review.html) 与 `danijar/dreamerv3@e3f0224` | RSSM posterior/prior、dyn/rep KL、stop-gradient、free-nats 与 latent information 的实现语义 | DreamerV3 repo 是论文作者官方代码、未运行的 collapse 结果 | official-code-checked / WARN |
| S3 | [VOL 03 ACT claim-to-code audit](vol_03_act_claim_to_code.html) | CVAE posterior/prior、KL、action chunk、latent train/infer gap 与 temporal aggregation 的 failure hooks | ACT 或用户项目一定存在 posterior collapse、latent quality 已量化 | checked / WARN |
| S4 | [VOL 03 Architecture / execution audit](vol_03_architecture_execution_claim_to_code.html) | sequence layout、causal attention、loss mask、action suffix 与 off-by-one/future visibility 边界 | 某项目一定使用正确 mask、没有数据泄漏 | checked / WARN |
| S5 | [VOL 06 PER-003 Multi-view / Temporal](../knowledge/vol_06_per003_multiview_temporal.html) | camera/time identity、presence/missingness、observation age、causal/ordered mask 与 replay leakage 诊断 | 多视角项目已完成 calibration/sync 或 leakage audit | supporting / WARN |
| S6 | [VOL 04 WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html) | per-offset/open-loop、action sensitivity、proxy/simulator/real metric ladder 与 paired protocol | proxy 或 loss 已证明 causal action / closed-loop success | supporting / WARN |

## 3. 四类 failure 的最小定义

| failure | 典型症状 | 首要干预 | 不能误判为 |
| --- | --- | --- | --- |
| posterior collapse | KL/latent usage 长期接近零、不同样本 posterior 相同、decoder/context 单独已能重建 | posterior-vs-prior probe、latent ablation、free-bits/KL balance A/B | 任何低 KL 都是 collapse；高 reconstruction 就代表 latent 有用 |
| action ignoring | action swap/zero/perturbation 后 future delta 几乎不变；action gradient 或 mutual information 很低 | 固定 observation 做 action intervention、magnitude sweep、action head/gradient probe | action MSE 低、action token 存在就代表模型使用动作 |
| future leakage | 打乱未来/terminal/history 后指标突然坍塌；label shift 与 causal mask 对不上 | temporal split、causal mask visualization、future-frame removal、replay audit | teacher-forced accuracy 高；长度相同就没有泄漏 |
| background shortcut | 换桌面/相机/颜色/采集批次后性能坍塌；遮挡背景后任务预测变化大 | background swap/inpainting、camera/domain holdout、object-centric crop | domain randomization 一次就证明没有 shortcut |

## 4. 诊断合同

任何结果都要记录：checkpoint、data split、observation/history window、action schema/normalizer、seed、intervention、future horizon、metric script、valid mask、episode denominator 和 protocol revision。动作敏感性要固定观测、只改变动作；shortcut probe 要固定任务/动作、只改变背景；leakage probe 要明确训练输入在时间 (t) 允许看到哪些字段。

`WARN` 边界：本仓库当前没有 WM-020 专用的 latent-usage log、action-swap trace、future-removal replay 或 background-domain holdout，因此以下矩阵是 interview-ready diagnostic design，不是用户项目已完成实验。

## 5. 最小测试矩阵

| 测试 | 控制变量 | 观察量 | 可能结论 |
| --- | --- | --- | --- |
| posterior/prior probe | 同一 history、不同 observation/posterior sample | KL、latent entropy、decoder/reward delta | latent 是否携带额外观测信息 |
| latent ablation | replace posterior latent with prior/mean/zero | reconstruction、reward、action、rollout | decoder 是否绕过 stochastic latent |
| action swap | 固定 observation/history，交换 action | future delta、latent delta、reward/continue delta | action condition 是否可干预 |
| action magnitude sweep | 固定方向，改变幅度/符号 | response curve、gradient norm | action sensitivity 是否单调/饱和/为零 |
| future removal | 删除 terminal/future frame、右移 label | teacher/open-loop gap、loss | 是否依赖不应可见信息 |
| causal mask audit | 可见性矩阵、position/label shift | attention visibility、loss positions | future token 是否进入输入或梯度 |
| background domain holdout | 固定 task/action，替换背景/相机/光照 | task/action/rollout metrics | 是否依赖采集 shortcut |
| counterfactual object/action | 固定背景，替换物体状态或动作 | future/contact/task predicate | 是否抓住真正任务因果 |

## 6. 伪代码边界

```python
def diagnose_world_model(model, batch, protocol):
    # 1. Freeze the observation/history and record the exact protocol revision.
    baseline = model.rollout(batch.obs, batch.action, protocol)

    # 2. Probe latent usage without claiming that a low KL alone proves collapse.
    latent = posterior_prior_probe(model, batch, protocol)

    # 3. Change only action values and measure future/actionable deltas.
    action_probe = action_swap_and_sweep(model, batch, protocol)

    # 4. Remove future/terminal fields and verify causal visibility and label shift.
    leakage_probe = future_removal_and_mask_audit(model, batch, protocol)

    # 5. Hold task/action fixed while swapping background/camera/domain.
    shortcut_probe = background_domain_holdout(model, batch, protocol)
    return baseline, latent, action_probe, leakage_probe, shortcut_probe
```

代码只表达诊断流程，不产生任何项目指标；每个 probe 必须绑定 matched checkpoint、seed、mask、normalizer 和原始 trace。

## 7. 项目证据边界

- UWM/LIBERO：可以讨论 action/image conditional slices、normalizer/action shape、fixed/reset protocol 与 future/action mask；当前没有 WM-020 专用 action-swap 或 shortcut artifact。
- WAM/Cosmos：可以讨论 world/value/action slot、offline proxy 与 closed-loop boundary；不能把离线 MSE 或历史 0-success 直接解释为某个 failure mode 的因果诊断。
- OpenPiVLA/OPD/Robot Harness：可作为 sequence mask、point/box/text schema、timeout/episode trace 的接口挂钩，但不支持 world-model latent collapse 或 background shortcut 的个人实验 claim。

## 8. Source gate 结论与下一步

本 source freeze 为 `WARN`：定义、primary/official-code 边界和最小诊断矩阵已冻结；本地 latent/action/future/background probe、raw traces 与 ownership 仍缺。下游 knowledge 与单张题卡已同步，题卡保持 `unseen`；下一步进行真实口述或补一个诊断 artifact。

## 参考来源

1. [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html)。
2. [DreamerV3 independent fact review](vol_04_world_model_foundations_independent_fact_review.html)。
3. [ACT claim-to-code audit](vol_03_act_claim_to_code.html)。
4. [Architecture / execution audit](vol_03_architecture_execution_claim_to_code.html)。
5. [PER-003 Multi-view / Temporal](../knowledge/vol_06_per003_multiview_temporal.html)。
6. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
