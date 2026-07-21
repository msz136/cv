# VOL 02 IL / RL / Post-training：独立事实与实现边界复核

> 状态：`independent_fact_review / source_checked / local_grpo_boundary_checked / WARN`
> 审查日期：2026-07-19
> 证据截止：2026-07-19
> 范围：VOL 02 knowledge、40 张题卡、primary papers、官方文档与 Robot Harness 本地 GRPO-style trainer。
> 结论先行：DAgger、GAE、PPO、CQL、IQL、DPO、GRPO 的核心机制与现有知识页基本一致；需要明确修正三处容易混淆的口径：GAE 的 terminated/truncated mask、CQL 公式只是保守正则项而非完整 objective、当前 Harness 本地实现是 `offline_grouped_reward_weighted_policy_update`，不能直接称 DeepSeekMath 式 online GRPO。所有题卡继续保持 `unseen`，项目指标与个人 ownership 仍由 VOL 07 evidence gate 约束。

## 1. 问题与审查方法

本复核回答四个问题：

1. VOL 02 的公式、术语和方法边界是否与 primary paper 一致？
2. 哪些内容是论文/官方文档事实，哪些只是面试抽象或本地推断？
3. Robot Harness 的 GRPO、reward、schema 和 eval 是否能绑定到真实本地代码？
4. 哪些修正必须回写 knowledge 或题卡，才能避免高压追问时过度声称？

判定标签：`primary-verified`（论文/官方文档直接支持）、`official-code`（官方实现支持）、`local-direct`（本地文件可读取）、`inference`（由证据推断）、`blocked`（缺 runtime/raw/ownership）。本页不把“公式正确”升级为“个人项目已实现”。

## 2. 冻结来源矩阵

| ID | 来源 | 类型 | 本次核对的范围 | Verdict |
| --- | --- | --- | --- | --- |
| S01 | DAgger, arXiv `1011.0686` | primary paper | expert relabeling、aggregated dataset、no-regret/data-distribution 叙事 | `primary-verified` |
| S02 | GAE, arXiv `1506.02438` | primary paper | TD residual、γ/λ bias-variance、advantage estimate | `primary-verified` |
| S03 | PPO, arXiv `1707.06347` | primary paper | old/new policy ratio、clipped surrogate、trust-region 近似边界 | `primary-verified` |
| S04 | CQL, arXiv `2006.04779` | primary paper | conservative Q regularizer、OOD action overestimation | `primary-verified` |
| S05 | IQL, arXiv `2110.06169` | primary paper | expectile value、advantage-weighted extraction、避免显式 OOD max | `primary-verified` |
| S06 | DPO, arXiv `2305.18290` | primary paper | chosen/rejected、reference policy、KL-regularized log-ratio | `primary-verified` |
| S07 | DeepSeekMath / GRPO, arXiv `2402.03300` | primary paper | group-relative reward、组内相对优势、实现差异边界 | `primary-verified` |
| S08 | Gymnasium time-limit handling | official docs | `terminated` 与 `truncated`、bootstrap 语义 | `official-code` |
| S09 | PyTorch `KLDivLoss` | official docs | input/target/reduction 语义；用于 DPO/KL 面试对照 | `official-code` |
| S10 | [VOL 02 source plan](vol_02_il_rl_posttraining_sources.md) | local canonical source | 来源 URL、项目映射与待核列表 | `local-direct` |
| S11 | `C:\Users\mousongzhe\agent\remote_training_pipeline_scripts\train_grpo.py` | local-direct | reward-shaped grouped weighting、Trainer loss、LoRA/DeepSpeed 参数 | `local-direct` |
| S12 | `...\configs\reward_spec.json` / `eval_grpo_tasks.py` | local-direct | task-family weights、hard penalty 设计、格式/字段覆盖评估 | `local-direct` |
| S13 | [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) | local evidence audit | 数据量、run lineage、scorer、safety/browser 与 ownership 边界 | `local-direct / WARN` |

## 3. Claim-to-source 复核矩阵

| Claim | 复核结论 | 必须保留的边界 |
| --- | --- | --- |
| BC 在 expert distribution 上拟合 action | `primary-verified / textbook-consistent` | 不自动解决 covariate shift；action window、padding、split 仍是实现合同 |
| DAgger 通过策略访问态再让 expert 标注 | `primary-verified` | 需要在线 expert/oracle；recovery 数据只能说“类似作用”，不能直接称 DAgger |
| GAE 是 TD residual 的 γλ 加权和 | `primary-verified` | `d_t` 必须区分 true termination 与 time-limit truncation；timeout 通常需要 bootstrap |
| PPO clipping 近似 trust region | `primary-verified` | clip 只覆盖 surrogate policy term，不是严格 KL 约束，也不替代 value/entropy/rollout freshness |
| CQL 惩罚数据外动作的 Q 过估 | `primary-verified` | α(log-sum-exp − data-Q) 是核心正则化示意，不是完整 CQL loss 或安全保证 |
| IQL 不显式对数据外 action 做 max-Q | `primary-verified` | 仍依赖 reward、expectile value、数据覆盖和 advantage-weighted extraction |
| DPO 用 chosen/rejected 相对 reference log-ratio | `primary-verified` | β 与 reference/KL 锚点必须绑定；pair 质量决定结果，不代表无 reward 假设 |
| GRPO 使用同 prompt 的 group-relative reward | `primary-verified` | 具体实现可能有 clip/KL、std=0 处理、采样/过滤差异，不能把所有 GRPO 代码视为相同 |
| schema 是输出契约，reward/checker 是训练信号，holdout 是验收协议 | `inference / engineering contract` | 这是面试系统设计抽象，不是某篇论文的统一算法定理 |
| Robot Harness 有 GRPO trainer | `local-direct` | 本地脚本日志写明 `offline_grouped_reward_weighted_policy_update`；它不是已核验的 online multi-candidate GRPOTrainer |
| Robot Harness reward 约束 tool/scope/cancel 等组件 | `local-direct` | reward_spec 是高层工具协议 proxy；不等于真实物理成功、安全闭环或个人独立 ownership |
| Robot Harness 95.6% ladder 是 GRPO uplift | `protocol-limited / WARN` | base/SFT/GRPO 的 n、scorer 与 checkpoint lineage 不完全相同，不能做无条件因果归因 |

## 4. 关键公式与实现核对

### 4.1 GAE 的 termination / truncation 修正

令 (d_t^{term}) 表示环境真正终止，(d_t^{trunc}) 表示时间上限截断。GAE 的 TD residual 可写为：

\[
\delta_t=r_t+\gamma(1-d_t^{term})V(s_{t+1})-V(s_t),\qquad
\hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}.
\]

这里 (d_t^{term}) 决定是否允许 bootstrap；time-limit truncation 通常不能当作真实 terminal。实现映射：batch 必须保存 `terminated` 与 `truncated`，不能把 Gymnasium 两个 flag 合成一个无语义的 `done`。当前 VOL 02 原文已有“termination/timeout”提醒，本复核把变量边界正式写清。

### 4.2 CQL 只是完整 objective 的核心正则项

离散动作的常见核心项可写为：

\[
\mathcal L_{CQL}^{reg}=\alpha\left(\mathbb E_s\log\sum_a\exp Q(s,a)-\mathbb E_{(s,a)\sim D}Q(s,a)\right).
\]

第一项压低候选动作的过高 Q，第二项保留数据动作的相对价值；真正训练还要和 Bellman/TD 误差、target network、优化器和实现变体组合。当前 VOL 02 的“简化项”表述是可接受的，但题卡答案不得说 CQL 单独保证安全。

### 4.3 本地 Harness 的 GRPO-style 更新

本地 `train_grpo.py` 先从 reference trajectory 构造 reference、empty、wrong-tool、reversed 等候选，按 `reward_spec.json` 计算 reward，再用样本权重进入 token CE：

\[
\mathcal L_{local}=\frac{\sum_i w_i\,\ell_{CE}(y_i\mid x_i)}{\sum_i w_i+\epsilon},
\qquad
w_i=\operatorname{clip}(1+(r_i-\bar r),0.2,2.0).
\]

这描述的是当前本地脚本的 reward-shaped offline continuation，不是 DeepSeekMath 论文的完整 online group policy optimization。实现证据来自脚本 SHA `5BF8D38FB6AEB9A21D125CC50031EDE25EEEE52A54F139876F9CA59E33490852`；它能支持“本地实现了 GRPO-style reward weighting”，不能支持“已运行标准 online GRPO 并证明真实机器人收益”。

## 5. 本地实现与项目 ownership 边界

### 5.1 直接可读的本地证据

- `train_grpo.py`：`GRPODataset`、candidate group、`score_candidate`、`RewardWeightedTrainer.compute_loss`、LoRA/DeepSpeed/Trainer 参数。
- `reward_spec.json`：11 类 reward components、task-family weights 和 hard-penalty 字段；SHA `DBDF3569A4F5C90E55520AEE56E5B32DA2CE447A12580717B86A060236F88F6B`。
- `eval_grpo_tasks.py`：只验证数据字段和 reward-family coverage，不运行真实 robot/environment。
- `grpo_report.md`：记录 200-step completed run 与三次失败/中断尝试，但明确注明这是 reward-shaped GRPO-style continuation；报告 SHA `121D3781415FA784CB99DA609E0998844EB032E5E32DDAF811B433F6BA22F9BC`。

### 5.2 不能从这些文件推出的结论

1. 不推出 online multi-sample environment rollout 已闭合。
2. 不推出 schema reward 等价于真实物理 success 或 safety。
3. 不推出 95.6% ladder 是同 scorer、同 n、同 checkpoint lineage 的 base→GRPO 因果提升。
4. 不推出 Git author 或 Codex 生成记录等于候选人逐文件独立 ownership。

个人项目口述应使用：[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) 与 [Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html) 的分层口径。

## 6. 修正动作与验证状态

| 动作 | 结果 | 状态 |
| --- | --- | --- |
| 对照 DAgger/GAE/PPO/CQL/IQL/DPO/GRPO primary source | 核心机制一致；补充边界 | `PASS` |
| 对照 Gymnasium terminated/truncated | 已回写 knowledge 与题卡，显式区分 timeout bootstrap | `PASS WITH WARNING` |
| 对照本地 `train_grpo.py` | 确认是 reward-shaped offline GRPO-style continuation | `PASS WITH WARNING` |
| 对照 reward/eval scripts | 证明 schema/reward/holdout 是不同层，不是物理 success | `PASS` |
| 对照 Robot Harness inventory/ledger | 数据、scorer、n、ownership 保持 WARN | `PASS WITH WARNING` |
| 真实口述 | 尚未进行；40 张题卡继续 `unseen` | `PENDING` |

## 7. 结论与下一步

VOL 02 的通用知识可以进入 `fact_reviewed_candidate` 候选状态，但不能进入 `reviewed/drilled`：仍没有用户真实口述。GAE timeout 与 local GRPO-style implementation 两处边界已回写并完成静态校验。下一小步不是再生成更多题，而是做一题口述，例如 `VLA-RL-011`、`VLA-RL-027` 或 `VLA-RL-028`。所有 40 张题卡继续 `unseen`，不创建 `coaching_state.md`。

## 参考文献（References）

1. Ross et al., DAgger, [arXiv:1011.0686](https://arxiv.org/abs/1011.0686)。
2. Schulman et al., GAE, [arXiv:1506.02438](https://arxiv.org/abs/1506.02438)。
3. Schulman et al., PPO, [arXiv:1707.06347](https://arxiv.org/abs/1707.06347)。
4. Kumar et al., CQL, [arXiv:2006.04779](https://arxiv.org/abs/2006.04779)。
5. Kostrikov et al., IQL, [arXiv:2110.06169](https://arxiv.org/abs/2110.06169)。
6. Rafailov et al., DPO, [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)。
7. Shao et al., DeepSeekMath / GRPO, [arXiv:2402.03300](https://arxiv.org/abs/2402.03300)。
8. Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)。
9. PyTorch, [`KLDivLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.KLDivLoss.html)。
10. [VOL 02 source plan](vol_02_il_rl_posttraining_sources.md)。
11. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
12. [Robot Harness Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html)。
