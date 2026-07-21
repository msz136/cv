# VOL 04 WM-021 Source Freeze：Dreamer Latent Imagination、Actor/Critic 与 Model Bias

> 审计日期：2026-07-18  
> 状态：`source_frozen / VLA-WM-021 / knowledge_synced / card_synced / WARN`  
> 覆盖题目：`VLA-WM-021`  
> 本轮边界：冻结 DreamerV3 的 latent imagination、actor/critic、lambda-return、梯度边界和 model-bias 诊断；不把公开机制写成本地训练或项目收益。

## 1. 问题与结论边界

题目：**Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？**

冻结结论：

1. Dreamer 从 replay 中的真实 posterior state 作为 imagination 起点，使用 action-conditioned prior dynamics 生成 latent trajectory、reward 和 continuation，再用 imagined return 更新 actor/critic；这减少真实环境交互，但不是无模型训练。[S1][S2]
2. actor 选择动作，critic 估计在当前 policy/model 下的未来 return；lambda-return、discount/continuation、entropy 与 value target 的具体实现必须按论文或 frozen code 核对，不能把三者混成一个 loss。[S1][S2]
3. imagined state、reward 和 value 都由近似 world model 产生；模型在 OOD state 上的偏差会被 actor 优化放大，造成 dream reward 高、真实 rollout 差的 model exploitation。[S1][S3]
4. 梯度是否回到 world model 取决于 stop-gradient、actor/world-model update schedule、reward/representation gradient 配置；不能笼统说 actor loss 总是端到端更新整个 RSSM。[S2]
5. 防护要把 imagination proxy 与真实/模拟闭环分开评估，并用 horizon sweep、uncertainty/disagreement、receding-horizon replan、real-data refresh 或 pessimistic value 等手段验证，而不是只看 imagined return。[S1][S4]

## 2. 来源冻结

| ID | 来源 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- |
| S1 | [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html) | Dreamer RSSM、posterior/prior、imagined actor-critic、lambda-return、model bias 与 dream/real 边界 | 用户项目已复现 Dreamer、任何具体成功率或最优 horizon | checked / WARN |
| S2 | [DreamerV3 independent fact review](vol_04_world_model_foundations_independent_fact_review.html) 与 `danijar/dreamerv3@e3f0224` | `RSSM.observe/imagine/loss`、`Agent.loss`、dyn/rep KL、stop-gradient、imagined loss 与 repo provenance | 论文作者官方代码、未运行 checkpoint 的结果或个人 ownership | official-code-checked / WARN |
| S3 | [World Models / PlaNet audit](vol_04_world_model_foundations_claim_to_code.html) | dream controller/model exploitation、latent planning、long-horizon/OOD model bias | DreamerV3 与 PlaNet 的实现完全相同、真实环境风险已量化 | primary + framework / WARN |
| S4 | [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html) 与 [WM-020 Failure Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html) | imagined proxy、open-loop、action sensitivity、protocol tuple 与 failure probe 的分层 | proxy/loss 已证明 real success 或某项目因果提升 | supporting / WARN |
| S5 | project inventories | UWM/WAM/OpenPiVLA/OPD/Harness 的局部 protocol、lineage 与缺口 | 任何项目已完成 Dreamer actor-critic 训练或 model-bias ablation | local-evidence / WARN |

## 3. Imagination 数据流

| 步骤 | 输入/输出 | 关键合同 | 典型错误 |
| --- | --- | --- | --- |
| replay posterior | 真实 observation/history → (s_0=(h_0,z_0)) | 起点来自固定 replay，记录 reset、mask、timestamp | 把纯模型生成 state 当真实起点 |
| prior rollout | (s_t,a_t) → (s_{t+1}) | prior 不读取未来 observation，明确 horizon/continue | 偷看未来帧或混用 teacher forcing |
| reward/continue | imagined state → (hat r_t,hat c_t) | reward、termination、discount 的单位与时间索引一致 | 把 value/success/termination 当一回事 |
| actor | state → action distribution (pi_	heta(a_tmid s_t)) | action schema、entropy、normalizer、exploration contract | 只最大化 dream reward，不查 real action |
| critic | state → (v_psi(s_t)) | target return、bootstrap、discount/continue、stop-gradient | 用 model-biased target 当真实 value |
| evaluation | imagined proxy + simulator/real | matched checkpoint、init、controller、episode denominator | 只报告 imagined return |

## 4. Return 与梯度边界

Dreamer 风格的抽象 lambda-return 可以写为：

\[
G_t^\lambda = r_t+\gamma c_t\big((1-\lambda)v_\psi(s_{t+1})+\lambda G_{t+1}^\lambda\big),
\]

其中 (r_t) 是 imagined reward，(c_t) 是 continuation，(gamma) 是 discount，(lambda) 控制多步 target 与 bootstrap 的混合。该式是机制框架；实际项目还要冻结 horizon、terminal mask、symlog/reward transform、target stop-gradient 和 reduction。[S1][S2]

抽象训练链：

```text
replay observation → posterior state s0
                   → prior imagination s1...sH
                   → reward/continue/value targets
                   → actor loss + critic loss
                   → real/simulator validation
```

actor/critic 是否更新 world model 要看实现配置：有的路径对 imagined feature stop-gradient，有的路径允许特定 reward/representation gradient；`sg`、update schedule 和 loss scale 必须从 code/config 逐项核对。[S2]

## 5. Model bias 为什么会被放大

令真实转移为 (F)，world model 为 (hat F=F+epsilon)。在 imagined rollout 中，误差会随 horizon 传播；actor 还会主动选择模型认为高 reward 的区域：

\[
\hat J(\pi)-J(\pi)
\quad\text{可能随 }H\text{、OOD 程度和 policy exploitation 增大}.
\]

这不是一个可直接用于项目的精确 bound，而是解释框架。常见症状包括 imagined reward 上升但 real success 不变、value 在模型生成 state 上过度自信、action sensitivity 在真实数据和 imagined data 间不一致、长 horizon 失败率陡增。[S1][S3]

## 6. 最小防护与评估矩阵

| 防护/诊断 | 记录 | 作用 | 不能单独证明 |
| --- | --- | --- | --- |
| horizon sweep | H、per-offset error、imagined/real return | 发现 compounding/model bias | 真实泛化 |
| receding-horizon replan | execution prefix、latency、replan count | 缩短开放环误差积累 | world model 正确 |
| uncertainty/disagreement | ensemble/seed/posterior、calibration | 识别 OOD state 并限险 | uncertainty 已校准 |
| real-data refresh | replay mix、on-policy coverage、版本 | 减少 state-distribution gap | 无 leakage/shortcut |
| pessimistic value | penalty/critic ensemble/lower bound | 限制模型漏洞 exploitation | 任务 success 必然提升 |
| paired validation | same checkpoint/init/controller、episode trace | 对齐 imagined、sim、real 层级 | 跨 protocol 差异可忽略 |

## 7. 项目证据边界

- UWM/LIBERO：可讨论 action/image conditional loss、fixed/reset protocol、normalizer、horizon 与 rollout wrapper；当前没有 Dreamer-style actor/critic imagination 或 model-bias ablation artifact。
- WAM/Cosmos：可讨论 world/value/action slots、offline proxy、planning 与 0-success 边界；不能把离线 loss 或 proxy 当作 imagined actor-critic 已验证。
- OpenPiVLA、OPD、Robot Harness：可挂接 action schema、mask、scorer、timeout、episode trace，但不支持把通用 Dreamer 机制写成个人实现或收益。

## 8. Source gate 结论与下一步

本 source freeze 为 `WARN`：DreamerV3 actor/critic imagination、return、梯度边界和 model-bias 诊断已冻结；本地 checkpoint、imagined/real paired trace、horizon sweep、value calibration 与 ownership 仍缺。下游 knowledge 与题卡已同步，题卡保持 `unseen`；下一步进行真实口述或补一个 paired artifact。

## 参考来源

1. [World Model Foundations Audit A](vol_04_world_model_foundations_claim_to_code.html)。
2. [DreamerV3 independent fact review](vol_04_world_model_foundations_independent_fact_review.html)。
3. [WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)。
4. [WM-020 Failure Diagnostics](vol_04_wm020_failure_diagnostics_source_freeze.html)。
5. [UWM/WAM project evidence inventories](../evidence/evidence_manifest.html)。
