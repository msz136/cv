# VOL 04 World Model / Sim2Real：Failure Diagnostics（WM-020）

> 状态：`drafted / VLA-WM-020 / knowledge_22_of_44 / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：`VLA-WM-020`；本页先冻结四类 failure mode 与诊断矩阵，不把未运行 probe 写成项目结果。  
> 前置：[WM-019 Metric Boundary](vol_04_world_model_sim2real_wm019.html)、[WM-020 Source Freeze](../sources/vol_04_wm020_failure_diagnostics_source_freeze.html)。

## 问题（Question）

怎样发现 posterior collapse、action ignoring、future leakage 与 background shortcut？高分回答要先定义 failure，再说明控制变量、干预方式、观测量和不能外推的边界。

## 1. 四类 failure 的共同框架

```text
representation      intervention        time visibility       domain invariance
posterior collapse → action ignoring → future leakage      → background shortcut
       ↓                  ↓                   ↓                         ↓
latent probe        action swap/sweep   causal mask/replay   background/domain holdout
```

四类问题不在同一层：collapse 主要是表示/变分路径失效，action ignoring 是条件变量没有真正改变预测，future leakage 是信息可见性或时间对齐错误，background shortcut 是跨域不稳定的伪因果相关。一个总 loss 下降只能说明优化目标下降，不能告诉你是哪一层出错。[1][2]

## 2. Posterior collapse：latent 被绕过

### 2.1 直觉与形式

在带 latent 的 world model 或 CVAE 中，posterior (q_phi(zmid x,c)) 应该利用当前 observation (x) 提供 prior/context (c) 没有的信息；若 decoder、deterministic state 或 action history 已足够重建目标，优化可能让 (q_phi(zmid x,c)) 接近 (p_	heta(zmid c))，latent 于是几乎不携带样本特有信息。

典型变分项可写为：

\[
\mathcal L=\mathcal L_{\mathrm{recon}}+
\beta\,\mathrm{KL}\big(q_\phi(z\mid x,c)\;\|\;p_\theta(z\mid c)\big).
\]

变量解释：\(x\) 是当前观测，\(c\) 是 history/action/context，\(q\) 是 posterior，\(p\) 是 prior，\(\beta\) 控制 KL 压力。KL 很低是一个信号，但不是充分条件：若 posterior 和 prior 都很宽、decoder 也不依赖 \(z\)，仍可能发生 collapse；实现上还要看 latent usage、sample entropy、ablation 和 downstream response。[2][3]

### 2.2 最小诊断

| Probe | 控制 | 观测 | 解释边界 |
| --- | --- | --- | --- |
| posterior/prior swap | 固定 history 与 target | KL、latent entropy、decoder/reward/action delta | 判断 posterior 是否带来额外信息 |
| latent zero/mean | 只替换 (z) | reconstruction、reward、action、rollout | 结果不变才支持“被绕过”假设 |
| latent shuffle | batch 内交换 (z) | 样本级预测变化 | 变化可能来自 batch artifact，需 matched seed |
| KL/usage curve | 固定 split 与 reduction | per-group KL、active units、entropy | 不用单一 global KL 做结论 |

DreamerV3 的 posterior/prior、dyn/rep KL、stop-gradient 和 free-nats 是实现语义；它们提供审计入口，不等于当前仓库已经跑过 collapse experiment。[2]

## 3. Action ignoring：条件存在但不可干预

### 3.1 从“action-conditioned”到“可干预”

模型写成 (p_\theta(y_{t+1}\mid y_{\le t},a_t)) 只说明 action 出现在输入合同里。若数据中 action 变化很小、action 与 camera/background 共线，或者模型只靠 observation/history 就能预测，模型可能近似：

\[
f_\theta(o_t,a_t)\approx f_\theta(o_t,a'_t)
\]

对固定 observation 做 action swap，比较未来表示或预测的变化：

\[
\Delta_y=\|f_\theta(o,a)-f_\theta(o,a')\|,
\qquad
\Delta_a=\|a-a'\|.
\]

若在动作幅度、方向和 valid dimensions 都合理的范围内，(Delta_y) 长期接近噪声基线，需要怀疑 action ignoring；但低敏感度也可能来自动作本来不影响该时间窗、接触延迟或 measurement noise，必须按 horizon 和 task semantics 分层。[1][2]

### 3.2 诊断矩阵

1. **Zero/swap test**：固定 observation、替换 action 为零或另一条真实 action；记录 future delta、reward/continue delta。
2. **Magnitude/sign sweep**：沿同一 action direction 改变幅度/符号，检查 response curve 是否合理而非只看相关系数。
3. **Gradient/occlusion**：计算 future target 对 action embedding/input 的梯度，或遮掉 action 通道做 matched forward；梯度大不等于物理正确，梯度小也可能是饱和。
4. **Action-only holdout**：固定背景和 observation split，检查 action 变化是否能解释 future；不要把随机切分的高分当作因果证据。

## 4. Future leakage：模型看到了不该看的信息

### 4.1 时间合同

先写出训练时刻 (t) 的可见集合：

\[
\mathcal V_t=\{o_{\le t},a_{<t},r_{\le t},m_t\},
\]

其中 (m_t) 是合法的 mask/metadata。若 terminal observation、未来轨迹、下一步 action label、replay 中的 future frame 或错位 timestamp 进入 (mathcal V_t)，就产生 leakage。teacher-forced accuracy 可能因此虚高，而 online/open-loop 使用自身历史时马上崩溃。

### 4.2 常见泄漏点

| 泄漏点 | 典型症状 | 修复/验证 |
| --- | --- | --- |
| history shift off-by-one | 训练 loss 异常低，shift 后骤降 | 打印每个 token/frame 的时间戳与 label index |
| terminal/future frame | 末端任务准确率远高于中间状态 | 删除 terminal/future frame 做 replay |
| causal mask 方向反 | query 可看见未来 key | 可视化 visibility matrix 与 attention mask |
| repeated frame/padding | 相同数组长度代表不同物理时间 | presence/valid mask、observation age、control Hz |
| normalization/stat leakage | train/test 统计或未来 episode 混用 | split-aware normalizer 与 revision hash |

验证不是“看代码里有 causal=True”就结束，而是要结合 sequence layout、mask、timestamp、replay transform 和 raw batch 做 end-to-end audit。[4][5]

## 5. Background shortcut：学到采集条件而不是任务因果

背景 shortcut 的形式是：训练数据中 (b)（桌面、相机、光照、机器人外壳、采集批次）与目标 (y) 相关，模型学习 (p(ymid b)) 而不是依赖真正的 object/action state (x)。在随机切分里它可能给出很好的 offline score，换 camera/domain 后却崩溃。

最小 counterfactual 设计：固定 task、object state 和 action，仅替换 background/camera；或固定 background，仅改变 object state/action。若预测随背景变化远大于随任务变量变化，说明需要进一步做 object-centric crop、domain holdout、background inpainting 或采集平衡。一次 domain randomization 不是“没有 shortcut”的证明，必须报告 split、强度和 per-domain 结果。

## 6. 四类 failure 的对照表

| 维度 | Posterior collapse | Action ignoring | Future leakage | Background shortcut |
| --- | --- | --- | --- | --- |
| 主要层 | latent/variational | causal intervention | time/mask/data | domain invariance |
| 关键控制变量 | context/observation | fixed observation | allowed visibility | fixed task/action |
| 关键干预 | latent ablation | action swap/sweep | future removal/mask audit | background/camera swap |
| 主要指标 | KL、entropy、latent delta | future/action delta、gradient | teacher/open-loop gap、visibility | per-domain gap、counterfactual delta |
| 不能直接推出 | latent 必须有用 | action correctness | 没有其他 shortcut | 已实现 sim2real |

## 7. 可审计诊断 pipeline

```python
def diagnose_failure_modes(model, batch, protocol):
    # 1. Freeze checkpoint, split, schema, normalizer, seed, horizon and mask revision.
    baseline = rollout_and_record(model, batch, protocol)

    # 2. Probe whether posterior latent changes outputs beyond the prior/context path.
    latent = posterior_prior_and_latent_ablation(model, batch, protocol)

    # 3. Hold observation fixed and perturb only action values/directions.
    action = action_swap_and_magnitude_sweep(model, batch, protocol)

    # 4. Remove future/terminal fields and audit causal visibility plus timestamps.
    leakage = future_removal_and_causal_mask_audit(model, batch, protocol)

    # 5. Hold task/action fixed while swapping background/camera/domain.
    shortcut = background_domain_counterfactual(model, batch, protocol)
    return baseline, latent, action, leakage, shortcut
```

实现映射：每个返回值都应包含 raw trace、protocol revision、valid count 和失败解释；没有这些 artifact 时只能把结果写成 diagnostic design。

## 8. 项目挂钩与真实性边界

- **UWM/LIBERO**：可挂接 action/image conditional MSE、normalizer/action shape、fixed/reset protocol 与 future/action mask；当前没有 WM-020 专用 action-swap、latent-usage 或 background holdout artifact。
- **WAM/Cosmos**：可挂接 world/value/action slot、offline proxy 与 closed-loop boundary；不能把历史 0-success 或离线 MSE 直接归因为 action ignoring 或 posterior collapse。
- **OpenPiVLA**：可讨论 action packaging、causal-CE、sequence/mask 与 formal trainer，但不等于 world-model latent 诊断。
- **OPD/Robot Harness**：可作为 point/box/text schema、timeout、episode trace 和 scorer 的接口例子；不支持 world-model failure 的个人实验 claim。

## 9. 结论与下一步

WM-020 的高分回答不是列四个 buzzword，而是把 failure 映射到不同控制变量：latent 用 ablation，action 用 intervention，future 用 visibility/replay audit，background 用 counterfactual/domain holdout。单一 loss、teacher-forced score 或生成画面不能替代这四类证据。当前节点保持 `WARN`，对应题卡已同步并保持 `unseen`；下一步进行真实口述或补一个诊断 artifact。

## 参考文献（References）

1. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)。
2. [DreamerV3 independent fact review](../sources/vol_04_world_model_foundations_independent_fact_review.html)。
3. [ACT claim-to-code audit](../sources/vol_03_act_claim_to_code.html)。
4. [Architecture / execution audit](../sources/vol_03_architecture_execution_claim_to_code.html)。
5. [PER-003 Multi-view / Temporal](../knowledge/vol_06_per003_multiview_temporal.html)。
6. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)。
