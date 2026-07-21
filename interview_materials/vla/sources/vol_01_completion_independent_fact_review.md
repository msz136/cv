# VOL 01 Foundations：39 卡 Completion Fact Reconciliation

> 状态：`completion_fact_reconciliation / 39_cards / WARN`
> 审查日期：2026-07-19
> 范围：`VLA-FND-001..039` 的稳定 ID、短答、来源编号、项目挂钩、追问、易错点和练习状态。
> 结论先行：39 张卡均有可解析结构和直接来源入口，Batch 1–3 发现的公式、timeout、Jacobian、GRPO、WAM/UWM 与 advanced-control 边界已回写。这里的 completion 只表示“题卡事实链已 reconciliation”，不表示候选人已口述掌握；39 张卡继续全部 `unseen`，VOL 01 verdict 仍为 `WARN`。

## 1. 审查合同

每张卡必须同时满足：稳定唯一 ID、机制级短答、至少一个 primary/official source、项目挂钩有 local evidence 或明确 caveat、一个 follow-up、一个 pitfall、答案不超过 350 字、练习状态与真实口述一致。

来源分四层：

1. `primary/official`：论文、教材、官方 API/标准；支持通用机制。
2. `official-code`：OpenVLA/openpi/LIBERO；支持上游接口，不支持本地 ownership。
3. `local-evidence-audit`：五项目 inventory；支持当前证据边界，不自动支持强结果。
4. `unverified`：具体 Qwen3-VL config、OpenPiVLA axis、UWM normalizer、WAM matched metric 与个人逐文件 ownership。

## 2. 39 卡逐项 reconciliation

| ID | 核心机制来源 | 项目挂钩审查 | Verdict |
| --- | --- | --- | --- |
| VLA-FND-001 | Transformer + Deep Learning | OpenPiVLA 仅作 multimodal/action contract 入口 | `PASS/WARN` |
| VLA-FND-002 | Transformer + Deep Learning | OPD 几何误差与语义相似度分层 | `PASS/WARN` |
| VLA-FND-003 | Deep Learning + Modern Robotics Ch.5 | 参数导数与机器人 Jacobian 分开 | `PASS/WARN` |
| VLA-FND-004 | LayerNorm/RMSNorm/BatchNorm primary + PyTorch | Qwen3-VL exact norm 仍查 config | `PASS/WARN` |
| VLA-FND-005 | Deep Learning 概率基础 | action 逐维统计是 contract，不是项目结果 | `PASS/WARN` |
| VLA-FND-006 | PyTorch MSE/Huber/L1 | WAM MSE 只作 proxy | `PASS/WARN` |
| VLA-FND-007 | PyTorch KL + Minka divergence | DPO/KL 方向只讲机制 | `PASS/WARN` |
| VLA-FND-008 | RL/Deep Learning + WAM/UWM inventories | seed/denominator 仍需 raw artifact | `PASS/WARN` |
| VLA-FND-009 | GELU/SiLU docs + Deep Learning | backbone activation 需 frozen config | `PASS/WARN` |
| VLA-FND-010 | Transformer + PyTorch CE/Softmax | token/action logits 只讲数值机制 | `PASS` |
| VLA-FND-011 | OpenVLA/openpi + PyTorch losses | token vs continuous action 与项目 evidence 分层 | `PASS/WARN` |
| VLA-FND-012 | Transformer + SDPA docs | attention scale 为通用机制 | `PASS` |
| VLA-FND-013 | Transformer + SDPA + WAM inventory | attention mask 与 loss/routing mask 分开 | `PASS/WARN` |
| VLA-FND-014 | RoFormer | 多模态时序只作机制，不推本地 layout | `PASS/WARN` |
| VLA-FND-015 | Transformer/LN + Xiong et al. | pre/post norm 不包装为训练创新 | `PASS/WARN` |
| VLA-FND-016 | OpenVLA/openpi + OpenPiVLA inventory | 模态拼接/独立 expert 不混称 | `PASS/WARN` |
| VLA-FND-017 | LoRA + OpenPiVLA inventory | rank/target modules/ownership 仍未核实 | `PASS/WARN` |
| VLA-FND-018 | HF KV cache docs | cache 不消除串行 token steps | `PASS` |
| VLA-FND-019 | Transformer/LN + PyTorch AMP/clip docs | 跨硬件问题保持诊断树 | `PASS/WARN` |
| VLA-FND-020 | PCGrad + WAM/OPD inventories | mask/routing 不自动等于 gradient conflict 解决 | `PASS/WARN` |
| VLA-FND-021 | Sutton–Barto + WAM/UWM inventories | reward/value/success 分层 | `PASS/WARN` |
| VLA-FND-022 | Sutton–Barto + WAM inventory | value head 不等于 action | `PASS/WARN` |
| VLA-FND-023 | Sutton–Barto + WAM/UWM inventories | benchmark success 不等于 Bellman optimum | `PASS/WARN` |
| VLA-FND-024 | Sutton–Barto + Harness inventory | canonical online 与 local offline GRPO-style 分开 | `PASS/WARN` |
| VLA-FND-025 | Sutton–Barto + Harness inventory | group-relative signal 不等于 robot value head | `PASS/WARN` |
| VLA-FND-026 | PPO + Harness inventory | PPO/GRPO/local offline objective 分层 | `PASS/WARN` |
| VLA-FND-027 | Sutton–Barto/Gymnasium + WAM/UWM inventories | terminated/truncated/success 分开 | `PASS/WARN` |
| VLA-FND-028 | BCQ/DAgger + UWM inventory | contact/recovery 只作诊断假设 | `PASS/WARN` |
| VLA-FND-029 | Sutton–Barto/DAgger + WAM inventory | 历史 MSE 比例已移除，保留 proxy 口径 | `PASS/WARN` |
| VLA-FND-030 | RL/Modern Robotics/REP-103 + OpenPiVLA inventory | observation/state/action contract 分层 | `PASS/WARN` |
| VLA-FND-031 | Modern Robotics/REP-103 + OPD inventory | image frame 与 robot action frame 分开 | `PASS/WARN` |
| VLA-FND-032 | Modern Robotics/REP-103 + OpenPiVLA inventory | 方向、列/行向量、单位仍需本地 schema | `PASS/WARN` |
| VLA-FND-033 | Modern Robotics Ch.4/6 + OpenPiVLA inventory | IK 成功不等于安全可执行 | `PASS/WARN` |
| VLA-FND-034 | Modern Robotics Ch.5 + OpenPiVLA inventory | singularity 以 inverse amplification 表述 | `PASS/WARN` |
| VLA-FND-035 | openpi/REP-103/Feedback/Modern Robotics + inventory | 7D/14D 不等于 torque 语义 | `PASS/WARN` |
| VLA-FND-036 | Feedback Systems | PID 是底层机制，不冒充项目实现 | `PASS/WARN` |
| VLA-FND-037 | openpi/LIBERO/Diffusion Policy/Feedback + inventories | query/controller rate 与 execution prefix 分开 | `PASS/WARN` |
| VLA-FND-038 | openpi/LIBERO/REP-103 + inventories | normalizer/axis/gripper checksum 仍缺 | `PASS/WARN` |
| VLA-FND-039 | Hogan/Rawlings/Diffusion Policy/OpenVLA + inventories | 不声称本地接入 impedance/MPC | `PASS/WARN` |

## 3. 本次来源修复

- 新增 Deep Learning、BatchNorm、L1Loss、Softmax、Minka divergence、Pre-LN、AMP、gradient clipping、REP-103、Feedback Systems、Modern Robotics Ch.5/6、DAgger 与 Gymnasium timeout。
- 五个 local inventory 进入题卡来源表，用于约束项目 hook；Git author、项目页存在或官方实现均不当作个人 ownership。
- 45 个来源编号全部定义；所有题卡来源编号必须解析到该表，不允许悬空编号。

## 4. 完成度与未完成项

### 已完成

- 39/39 stable IDs；39/39 source blocks；39/39 project hooks；39/39 follow-ups；39/39 pitfalls。
- Batch 1–3 knowledge 与题卡边界回写。
- canonical SHA、HTML H1、公式污染、控制字符、details balance、本地链接和 review JSON 可解析性校验。

### 仍未完成

- 39/39 真实口述均未发生，因此练习状态继续 `unseen`。
- Qwen3-VL exact config、OpenPiVLA axis/normalizer/controller、WAM matched metric、UWM raw episode/checkpoint 与个人 ownership 仍依赖 VOL 07 evidence gate。
- 浏览器 `file://` 视觉 QA 仍 `BLOCKED`。

## 5. 下一步

VOL 01 不再继续批量生成新卡。下一 bounded slice 应是一次真实口述（优先 `VLA-FND-030`、`012`、`021`、`029`、`037` 中的一题）或转入 VOL 03 独立事实 completion audit；没有真实回答前不创建 coaching state，不更新 mastery。

## 参考入口

- [Batch 1 Independent Fact Review](vol_01_batch1_independent_fact_review.html)
- [Batch 2 MDP / TD / Control Review](vol_01_batch2_mdp_td_control_independent_fact_review.html)
- [Batch 3 Advanced Control Review](vol_01_batch3_advanced_control_independent_fact_review.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)
- [UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)
- [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)
- [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)
