# VOL 04 World Model / Sim2Real：Dreamer Imagination、Actor/Critic 与 Model Bias（WM-021）

> 状态：`drafted / VLA-WM-021 / knowledge_23_of_44 / card_synced / WARN`  
> 报告日期：2026-07-18  
> 证据截止：2026-07-18  
> 当前节点：`VLA-WM-021`；本页解释 Dreamer 的 imagined actor-critic 机制和 model-bias 边界，不声明本地复现。  
> 前置：[WM-020 Failure Diagnostics](vol_04_world_model_sim2real_wm020_failure_diagnostics.html)、[WM-021 Source Freeze](../sources/vol_04_wm021_dreamer_imagination_actor_critic_source_freeze.html)。

## 问题（Question）

Dreamer 如何在 latent imagination 中训练 actor/critic，为什么仍受 model bias 影响？回答必须拆开真实 replay 起点、prior imagination、reward/continue、lambda-return、梯度边界和真实闭环验证。

## 1. 一句话直觉

Dreamer 不让 actor 每次更新都与真实环境交互，而是从真实 replay 的 posterior state 出发，在 action-conditioned prior 中“想象”一段 latent trajectory，再用预测 reward/continue 计算 return，更新 actor 与 critic。省下真实交互成本的同时，也把 world model 的错误带进了训练：actor 可能学会让模型开心，而不是让真实环境成功。[1][2]

## 2. 端到端数据流

```text
real replay observations
        ↓ posterior filtering
      s0=(h0,z0)
        ↓ actor π(a|s) + prior dynamics
   imagined s1...sH, r̂, ĉ
        ↓ lambda-return / value target
 actor loss + critic loss
        ↓
 simulator/real paired validation
```

### 2.1 Replay posterior 是起点，不是整个 imagination

RSSM 在真实序列上使用 observation posterior (q_phi(z_tmid h_t,x_t)) 更新 belief；imagination 从某个 replay state (s_0=(h_0,z_0)) 开始，之后由 prior (p_phi(z_{t+1}mid h_{t+1})) 和 actor 产生未来。若每一步都喂真实 observation，就变成 teacher-forced filtering，而不是纯 imagined rollout。[1][2]

### 2.2 Actor 与 critic 的职责

\[
\pi_\theta(a_t\mid s_t)\quad\text{and}\quad v_\psi(s_t)\approx\mathbb E_{p_\phi,\pi_\theta}[G_t].
\]

变量解释：(pi_	heta) 是 actor 的动作分布，(v_psi) 是当前 world model 与 policy 下的未来回报估计，(s_t=(h_t,z_t)) 是 RSSM feature。actor 负责选动作，critic 负责提供 value baseline/target；两者都不等同于 reward、success classifier 或 termination head。

## 3. Lambda-return 与 target 合同

一个常见的抽象形式是：

\[
G_t^\lambda=r_t+\gamma c_t\left((1-\lambda)v_\psi(s_{t+1})+\lambda G_{t+1}^\lambda\right),
\]

其中 (r_t) 是 imagined reward，(c_t) 是 continuation，(gamma) 是 discount，(lambda) 控制多步 target 与 bootstrap value 的混合。代码映射通常包含 `lambda_return`、continuation mask、horizon truncation、target stop-gradient 和 value loss；具体 reward transform、symlog、reduction 与 config 必须按 frozen code 核对，不应把公式当作某项目默认值。[1][2]

常见错误：

- 把 (c_t) 当作 reward 或把 terminal episode 继续 bootstrap；
- 用真实未来 observation 计算 target，却称它为 open-loop imagination；
- 只报告 imagined return，不保存 horizon、init、seed、controller 和 real/sim episode denominator；
- 把 critic 的 value 当作真实 success probability。

## 4. 梯度边界与实现映射

DreamerV3 frozen reimplementation 的 `RSSM.observe`、`RSSM.imagine`、`RSSM.loss` 和 `Agent.loss` 可以映射到 filtering、prior rollout、KL/world loss 与 actor-critic imagination；repo README 明确它是 reimplementation，不应称为论文作者官方代码。[2]

actor/critic 是否把梯度传回 world model，取决于 `stop_gradient`、actor/world update schedule、reward/representation gradient 配置和 loss scale。高分回答应先画：

```text
replay → posterior state → prior rollout → reward/value target
          └─ world-model loss       └─ actor/critic loss
```

再指出每条边是否允许 gradient；不能笼统说“actor loss 端到端更新 RSSM”。

## 5. Model bias 与 exploitation

真实转移为 (F)，模型转移为 (hat F=F+epsilon)。即使单步误差很小，长 horizon 仍可能累积；更危险的是 actor 会主动选择模型高估 reward 的 OOD state，使：

\[
J_{\mathrm{imagined}}(\pi)\gg J_{\mathrm{real}}(\pi).
\]

这不是精确理论 bound，而是 model exploitation 的诊断表达。典型症状：imagined reward/value 上升但真实 success 不变；长 horizon 崩溃；模型对 action/uncertainty 不敏感；actor 进入训练数据没有覆盖的 latent 区域。World Models 早期的 dream controller 也说明了“在模型里成功”不能替代真实环境验证。[1][3]

## 6. 最小防护与评估

| 方法 | 要冻结的字段 | 目标 | 边界 |
| --- | --- | --- | --- |
| horizon sweep | imagination H、execution prefix、per-offset metric | 找 compounding gap | 不等于 real generalization |
| receding-horizon replan | replan interval、latency、controller | 缩短开放环暴露 | 不证明 world model 正确 |
| uncertainty/disagreement | ensemble/seed/posterior、calibration | 识别 OOD state | disagreement 未校准不等于风险 |
| replay refresh | real/data mix、coverage、revision | 减少 state distribution gap | 不自动消除 leakage/shortcut |
| pessimistic value | penalty、ensemble lower bound | 限制模型漏洞 | 不保证任务成功 |
| paired validation | same checkpoint/init/task/controller | 对齐 imagined/sim/real | 不同 protocol 不能直接比较 |

至少同时报告 imagined return、per-offset open-loop error、action sensitivity、simulator/real episode success 和 failure trace；否则无法判断是 actor、critic、world model 还是 protocol 造成差异。[4]

## 7. 可审计伪代码

```python
def train_imagined_actor_critic(agent, replay, protocol):
    # 1. Encode real replay and choose a posterior state as imagination start.
    start = agent.world_model.posterior_state(replay, protocol)

    # 2. Roll out only with prior dynamics and actor actions; do not read future frames.
    imagined = agent.world_model.imagine(start, agent.actor, protocol.horizon)

    # 3. Predict reward/continuation and build a lambda-return target.
    target = lambda_return(imagined.reward, imagined.continue_, agent.critic, protocol)

    # 4. Apply the implementation's explicit stop-gradient/gradient routing.
    actor_loss, critic_loss = agent.imagined_losses(imagined, target, protocol)
    return actor_loss, critic_loss, imagined
```

这段伪代码只说明 mechanism；真实实现还需保存 checkpoint、normalizer、horizon、reset/init、seed、controller、episode trace 和 metric script。

## 8. 项目挂钩与真实性边界

- UWM/LIBERO：可连接 action/image conditional loss、fixed/reset protocol、normalizer、horizon 和 rollout wrapper；当前无 Dreamer-style actor/critic imagination 或 model-bias ablation artifact。
- WAM/Cosmos：可连接 world/value/action slots、offline proxy、planning 与 0-success；不能把离线 MSE 或 proxy 直接说成 imagined actor-critic 已验证。
- OpenPiVLA、OPD、Robot Harness：可讨论 action schema、mask、scorer、timeout 和 episode trace，但不支持把通用 Dreamer 机制写成个人实现或收益。

## 9. 结论与下一步

Dreamer 的关键链路是“真实 posterior 起点 → prior latent imagination → reward/continue → lambda-return → actor/critic”，关键风险是“actor 优化 world-model 的错误”。因此必须把 imagined proxy、open-loop、simulator 和 real success 分层，并审计 horizon、gradient routing、uncertainty、reset 和 controller。当前节点保持 `WARN`，题卡已同步并保持 `unseen`；下一步进行真实口述或补一个 paired artifact。

## 参考文献（References）

1. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)。
2. [DreamerV3 independent fact review](../sources/vol_04_world_model_foundations_independent_fact_review.html)。
3. [World Models / PlaNet audit](../sources/vol_04_world_model_foundations_claim_to_code.html)。
4. [WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)。
