# VOL 01 Foundations Batch 2：MDP / TD / 机器人控制独立事实复核

> 状态：`independent_fact_review / batch2 / WARN`
> 审查日期：2026-07-19
> 范围：VOL 01 knowledge 与 `VLA-FND-021..039` 中的 MDP、Bellman、TD、on/off-policy、termination/truncation、Jacobian、PID、控制频率和闭环执行边界。
> 结论先行：MDP/Bellman/on-off-policy 的核心定义可保留；TD 与 rollout 必须把 `terminated` 和 `truncated` 分开；Jacobian 奇异性的风险应表述为 inverse/伪逆放大关节速度与噪声，而不是笼统说“小关节误差导致末端不稳定”。Robot Harness 只能绑定本地 offline GRPO-style continuation，WAM/UWM 指标只能按 evidence gate 降级表述。

## 1. 冻结来源

| ID | 来源 | 类型 | 本次支持的 claim | 不支持的 claim |
| --- | --- | --- | --- | --- |
| S01 | Sutton & Barto, [Reinforcement Learning: An Introduction, 2nd ed.](http://incompleteideas.net/book/the-book-2nd.html) | primary textbook | MDP、return、value/Q/advantage、Bellman、TD、on/off-policy | 不支持某个本地项目使用了特定 RL 算法 |
| S02 | Gymnasium, [Handling Time Limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/) | official docs | `terminated`/`truncated`、timeout bootstrap | 不支持所有环境都采用同一 success predicate |
| S03 | Lynch & Park, [Modern Robotics Chapter 5](https://modernrobotics.northwestern.edu/chapters/chapter5/) | primary textbook/site | twist、Jacobian、singularity、velocity kinematics | 不支持本地 action axis/frame |
| S04 | Lynch & Park, [Modern Robotics Chapter 6](https://modernrobotics.northwestern.edu/chapters/chapter6/) | primary textbook/site | numerical IK、多解、初值与 singularity 边界 | 不支持 IK 成功等于碰撞/动力学可行 |
| S05 | ROS REP-103, [Standard Units of Measure and Coordinate Conventions](https://www.ros.org/reps/rep-0103.html) | official standard | SI units、right-handed frame、axis convention | 不支持某个项目已遵守该规范 |
| S06 | Åström & Murray, [Feedback Systems](https://fbsbook.org/) | primary textbook/site | feedback、PID、delay、stability 的基础关系 | 不支持任意 PID 参数或真实控制稳定性 |
| S07 | [VOL 02 Independent Fact Review](vol_02_il_rl_posttraining_independent_fact_review.html) | local fact review | GAE/PPO/GRPO 与 local Harness implementation 边界 | 不支持 online robot rollout 或个人 ownership |
| S08 | [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | local evidence audit | 指标、协议和 artifact 缺口 | 不支持将历史 proxy 升级为 benchmark success |

## 2. Claim-to-source 复核

| Claim | Verdict | 必须保留的边界 |
| --- | --- | --- |
| \(V^\pi,Q^\pi,A^\pi\) 的定义与 Bellman expectation relation | `PASS / primary-verified` | 即时 reward 与期望 reward 的记号需说明；Bellman relation 不是单一网络 loss |
| on-policy 与 off-policy 的差异 | `PASS / primary-verified` | off-policy 不等于 offline RL；数据复用需要分布修正/保守性边界 |
| TD terminal mask | `FIX_REQUIRED` | true termination 通常停止 bootstrap；time-limit truncation 通常仍 bootstrap |
| Jacobian singularity | `PASS WITH WORDING FIX` | rank/condition 问题主要在 inverse mapping 中放大 joint velocity/noise |
| PID 的 P/I/D 直觉 | `PASS / textbook-consistent` | D 项会放大噪声；anti-windup、滤波、采样周期和 delay 是实现合同 |
| chunk 减少 policy query、长执行前缀更开环 | `PASS / engineering inference` | prediction horizon、execution horizon、controller rate 和 observation age 必须分开 |
| Harness 的“online GRPO”项目挂钩 | `FAIL / OVERCLAIM` | 当前本地直接证据只支持 offline reward-shaped grouped weighting |
| WAM 约 45% MSE 改善 | `WARN / protocol-limited` | 当前 evidence gate 不支持把历史比例写成已核验强结果 |
| UWM 0.744 / 74.4% | `WARN / user-confirmed remote` | 不是本地 raw bundle 验证的 benchmark；必须带协议和来源标签 |

## 3. 回写动作

1. TD residual 改用 \(d_t^{term}\)，并明确 time-limit truncation 的 bootstrap 语义。
2. 闭环伪代码改为显式处理 `terminated`、`truncated` 与 `success`，避免一个无语义 `done` 混合训练和评估边界。
3. Jacobian 文字改为 inverse/伪逆的速度与噪声放大，不把 singularity 误写成 forward kinematics 的普遍误差放大。
4. `VLA-FND-024/026` 的 Harness 项目挂钩改为 canonical online GRPO 与本地 offline GRPO-style 的对照。
5. `VLA-FND-029` 的 WAM 历史比例降级为“离线 proxy 趋势需同协议 artifact 复核”；`VLA-FND-028` 的 UWM 根因改为诊断假设。

## 4. 边界与下一步

- 本批完成后，VOL 01 knowledge 的两批高频基础事实可进入 candidate 状态，但整卷 39 卡仍未逐卡独立审查，也没有真实口述。
- `VLA-FND-039` 的 impedance/MPC/learned-policy 选择仍需单独控制方法 batch；本页只保留分层组合的工程直觉。
- 所有卡保持 `unseen`；不创建 `coaching_state.md`，不把静态审查当 mastery。
- 浏览器 `file://` 视觉 QA 保持 `BLOCKED`；完成后仍需 SHA、单 H1、公式和本地链接静态校验。

## 参考文献

本页使用 S01–S08 作为冻结入口；具体项目数字与 ownership 必须回到 VOL 07 inventory/ledger，不由基础知识页反向证明。
