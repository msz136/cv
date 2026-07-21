# VOL 01 Foundations Batch 1：独立事实复核与公式边界

> 状态：`independent_fact_review / batch1 / WARN`
> 审查日期：2026-07-19
> 范围：VOL 01 knowledge 中表示、attention、归一化、损失与基础机器人几何的高频入口；不宣称整卷 39 张题卡已审查或已口述。
> 结论先行：核心机制与 primary sources 一致，但 canonical knowledge 曾出现 `\theta`、`\mid`、`\in`、`\tilde` 被写成控制字符/缺失反斜杠的问题；已回写修复。Qwen3-VL/本地 LoRA、OpenPiVLA 轴序和 UWM normalizer 仍保持未核实边界。

## 1. 冻结来源

| ID | 来源 | 类型 | 覆盖 |
| --- | --- | --- | --- |
| S01 | Vaswani et al., [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | primary paper | scaled dot-product attention、残差与位置编码的基础语义 |
| S02 | Ba et al., [Layer Normalization](https://arxiv.org/abs/1607.06450) | primary paper | LayerNorm 的按样本/特征归一化与训练时行为 |
| S03 | Zhang & Sennrich, [RMSNorm](https://arxiv.org/abs/1910.07467) | primary paper | 去均值 RMS 归一化与 re-scaling invariance 动机 |
| S04 | PyTorch [`scaled_dot_product_attention`](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html) | official docs | Q/K/V shape、scale、mask API 边界 |
| S05 | PyTorch [`LayerNorm`](https://docs.pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html) | official docs | normalized shape、affine、epsilon |
| S06 | PyTorch [`MSELoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.MSELoss.html)、[`HuberLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html)、[`CrossEntropyLoss`](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html) | official docs | reduction、连续回归与离散 token 监督边界 |
| S07 | Lynch & Park, [Modern Robotics Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/) | primary textbook/site | 齐次变换、FK 与 frame composition |
| S08 | [OpenVLA official repository](https://github.com/openvla/openvla)、[openpi official repository](https://github.com/Physical-Intelligence/openpi) | official-code | 仅用于确认项目接口应回到官方源码；不支持本地 ownership |

## 2. Claim-to-source 复核

| Claim | Verdict | 保留边界 |
| --- | --- | --- |
| attention 使用 (QK^\top/\sqrt{d_k}) | `PASS / primary-verified` | 除法是尺度控制；mask 语义取决于 bool/additive API |
| LayerNorm 减均值，RMSNorm 不减均值 | `PASS / primary-verified` | 具体 backbone 的 norm 选择不能由基础原理推出 |
| MSE/Huber/CrossEntropy 监督对象不同 | `PASS / official-docs` | reduction、mask、ignore index 和 dtype 仍是实现合同 |
| 齐次变换可组合旋转和平移 | `PASS / primary-verified` | 必须声明 (T^A_B) 方向、列向量约定、单位与时间戳 |
| LoRA 是低秩更新 | `PASS / method-level` | 本地 rank、注入层、alpha 和 ownership 未核实 |
| OpenVLA/openpi 的具体 action 轴序 | `UNVERIFIED` | 需要 frozen commit、配置和本地 artifact，不能从基础页推出 |

## 3. 本次修复

1. 将 Policy 术语中的 `pi_\theta(a_t\mid o_{\le t},c)` 恢复为完整 LaTeX。
2. 将状态转移中的 `p(s_{t+1}\mid s_t,a_t)` 恢复为完整 LaTeX。
3. 将齐次坐标说明中的 `R_{ab}\in SO(3)` 与 `\tilde p` 恢复为完整 LaTeX。
4. 保留 `done`、timeout、normalizer、axis order 和 controller 的实现风险，不把通用伪代码写成项目代码证据。

## 4. 复核边界

- 本页只审查 VOL 01 knowledge 的高频公式与基础术语，不代表 39 张题卡全部独立事实审查完成。
- 所有 39 张题卡继续 `unseen`；没有真实口述就不更新 weak/pass/strong，也不创建 coaching state。
- Qwen3-VL 具体 normalization、LoRA 注入层、OpenPiVLA action schema、UWM normalizer/checkpoint 仍需项目证据。
- 浏览器 `file://` 视觉 QA 受当前环境策略阻断，静态 HTML 校验单独记录。

## 5. 下一步

优先做一题真实口述（VOL 02 `VLA-RL-011` 或 VOL 01 `VLA-FND-012`）；若继续 source-first，则审查 VOL 01 的 MDP/TD/机器人控制 batch，而不是一次性重写整卷。

## 参考文献

以上 S01–S08 已在本页逐条冻结；本地项目映射仍以 `interview_materials/01..05_*.html` 与 VOL 07 evidence ledger 为准。
