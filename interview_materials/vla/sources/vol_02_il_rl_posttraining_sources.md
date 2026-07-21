# VOL 02 IL / RL / Post-training：来源计划

> 调研日期：2026-07-16；registry reconciliation：2026-07-19  
> 状态：`source_registry_reconciled / seven_core_methods_independently_reviewed / supporting_sources_registered / local_gates_warn`  
> 目标：为 IL、PPO、offline RL、DPO、GRPO 和 schema-aware reward 建立 primary-source ledger。
> 边界：七个核心方法与 Gymnasium/PyTorch 文档已独立复核；AWAC、LIBERO、SAC、AI Safety、PCGrad 仍是 supporting registry，不宣称达到相同 review 深度。Robot Harness 本地实现是 reward-shaped offline GRPO-style continuation，不是 canonical online GRPO。

## 1. Primary papers

| 主题 | 来源 | 计划支持的 claim | 状态 |
| --- | --- | --- | --- |
| DAgger | [A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning](https://arxiv.org/abs/1011.0686) | expert relabeling、covariate shift 缓解和在线数据聚合 | independently reviewed / WARN |
| GAE | [High-Dimensional Continuous Control Using Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) | bias/variance、\(\lambda\)、advantage estimator | independently reviewed；terminated/truncated boundary patched / WARN |
| PPO | [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) | ratio、clipping、trust-region 近似 | independently reviewed / WARN |
| CQL | [Conservative Q-Learning for Offline Reinforcement Learning](https://arxiv.org/abs/2006.04779) | OOD action、conservative Q、offline extrapolation | independently reviewed；regularizer≠full objective / WARN |
| IQL | [Offline Reinforcement Learning with Implicit Q-Learning](https://arxiv.org/abs/2110.06169) | advantage-weighted policy extraction、避免显式 OOD action evaluation | independently reviewed / WARN |
| AWAC | [Accelerating Online Reinforcement Learning with Offline Datasets](https://arxiv.org/abs/2006.09359) | advantage-weighted regression、offline-to-online policy extraction | URL verified |
| DPO | [Direct Preference Optimization](https://arxiv.org/abs/2305.18290) | preference pair、reference policy、KL-regularized objective | independently reviewed / WARN |
| GRPO | [DeepSeekMath](https://arxiv.org/abs/2402.03300) | group-relative reward、critic-free/relative advantage 叙事边界 | independently reviewed；local implementation separated / WARN |
| LIBERO | [Benchmarking Knowledge Transfer for Lifelong Robot Learning](https://arxiv.org/abs/2306.03310) | task/suite split、机器人评估与 contamination 审计语境 | registered/supporting；VOL 04/05 protocol pages carry deeper review |
| SAC | [Soft Actor-Critic Algorithms and Applications](https://arxiv.org/abs/1812.05905) | tanh-squashed Gaussian 与 log-prob 变量变换；仅作连续动作分布机制来源 | registered/supporting |
| AI Safety | [Concrete Problems in AI Safety](https://arxiv.org/abs/1606.06565) | reward hacking / reward gaming 的目标错配边界 | registered/supporting |
| PCGrad | [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782) | 多目标 gradient interference 的诊断与一种缓解方法 | registered/supporting；VOL 04 auxiliary-gradient pages carry deeper review |

## 2. Official documentation / implementations

| 来源 | 用途 | 状态 |
| --- | --- | --- |
| [Hugging Face TRL](https://github.com/huggingface/trl) | SFT、DPO、GRPO trainer 的 API 和配置边界 | registered only；exact version/API call 未绑定本地项目 |
| [PyTorch KLDivLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.KLDivLoss.html) | KL input/target/reduction 语义 | official docs independently reviewed |
| [Gymnasium: Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | terminated / truncated 与 value bootstrap 语义 | official docs independently reviewed |
| [OpenVLA](https://github.com/openvla/openvla) | VLA imitation / fine-tuning context | frozen/reviewed in VOL 03；只作跨卷语境 |
| [Physical Intelligence openpi](https://github.com/Physical-Intelligence/openpi) | policy fine-tuning / action expert context | frozen/reviewed in VOL 03；不证明 Harness 实现 |
| [NVlabs/cosmos-policy](https://github.com/NVlabs/cosmos-policy) | action/world/value multi-objective context | frozen/reviewed in VOL 04；不证明本地 WAM run |

## 3. 本地项目映射

| VOL 02 主题 | 本地材料 | 不能直接推出的结论 |
| --- | --- | --- |
| SFT / GRPO / schema-aware reward | [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) + [Ownership Ledger](../evidence/projects/robot_harness_ownership_ledger.html) | local trainer 为 offline grouped reward weighting；tool proxy 不等于机器人 success；scorer/n/checkpoint/ownership 仍 WARN |
| action/world/value | [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html) + [Ownership Ledger](../evidence/projects/wam_ownership_ledger.html) | proxy MSE 不等于 online gain；checkpoint/denominator/ownership 未闭合 |
| OPD / teacher ablation | [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | 缺 matched SFT-only/single-teacher raw ablation，不能单因果归因 |
| DeepSeek 数据/偏好样本 | `output/mousongzhe_resume_optimized.html` | 只能讲有证据的样本整理、实验与错误归因；不虚构规模、结果与 ownership |

## 4. Registry reconciliation

| 闭环项 | 当前证据 | 状态 |
| --- | --- | --- |
| DAgger/GAE/PPO/CQL/IQL/DPO/GRPO 核心机制 | [独立事实复核](vol_02_il_rl_posttraining_independent_fact_review.html) | `checked / WARN` |
| terminated/truncated、CQL partial objective、local GRPO boundary | knowledge/questions + independent review | `patched and checked` |
| VOL 02 knowledge / cards | consolidated knowledge + `VLA-RL-001..040` | `40/40 / all unseen` |
| AWAC/LIBERO/SAC/AI Safety/PCGrad | primary URLs 与跨卷 supporting usage | `registered/supporting` |
| TRL exact API/version 与本地调用 | 未绑定 local code/revision | `pending` |
| Harness same-scorer base/SFT/GRPO causal comparison | n/scorer/checkpoint/raw bundle 不齐 | `WARN` |
| candidate ownership 与口述 | ownership ledger 未确认；无真实回答 | `PENDING` |

## 5. 下一 bounded slice

1. 不再生成 VOL 02 题卡；40 张保持 `unseen`。
2. 优先进行 `VLA-RL-011`、`VLA-RL-027` 或 `VLA-RL-028` 单题口述；有真实回答后才创建 coaching state。
3. 无候选人回答时，按相同流程闭合 VOL 04 source registry，消除最后一个 registry-only 例外。
4. 后续若需要提高 VOL 02 source depth，再单独复核 supporting sources 与 TRL exact version，不在本 registry closure 中伪造完成。
