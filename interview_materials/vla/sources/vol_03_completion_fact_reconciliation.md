# VOL 03 VLA / Action：44-Card Completion Reconciliation

> 状态：`completion_reconciled_candidate / 44_cards / source_audits_warn / WARN`
> 审查日期：2026-07-19
> 范围：`VLA-ARCH-001..012`、`VLA-ACT-001..032` 的题卡结构、source audit 映射、项目证据边界与静态 HTML 合同。
> 结论先行：44 张卡均已映射到 primary/frozen source 与 Source Audit A–F，OpenPiVLA inventory/ownership 已设为所有项目 hook 的总门；Audit A 的 OpenVLA endpoint/token/mask、Audit B 的 π0.5/FAST/OpenPI、Audit E 的 theorem/endpoint/time-sign/Beta 已完成独立复核，C/D/F 及 A/B/E 的 local runtime gate 仍为 `WARN/PENDING`。本页不能把 VOL 03 升级为 `reviewed/drilled`，44 张卡继续全部 `unseen`。

## 1. Reconciliation 合同

每张卡必须包含：稳定唯一 ID、面试意图、30 秒回答、机制展开、项目挂钩、追问树、危险答案、来源和真实练习状态。项目挂钩必须受 [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html) 约束。

Source Audit A–F 的角色：

| Audit | 主要范围 | 当前边界 |
| --- | --- | --- |
| A OpenVLA | tokenization、255/256 endpoint、CE/metric mask、unnorm | endpoint/mask independent-reviewed；local checkpoint/schema 未核实 |
| B π0/π0.5/FAST/openpi | action expert、time/sign、FAST revision、transforms | pi05/FAST/OpenPI public facts independent-reviewed；local model class/H/D/solver 未核实 |
| C ACT | CVAE、L1/KL、chunk、temporal ensemble | paper/code gap、padding denominator、learned query、oldest weight 与 sentinel 已 independent-reviewed；local use 保持 WARN |
| D Diffusion Policy | epsilon/sample target、scheduler、horizon、receding horizon | paper/code warm-start、loss denominator、boundary padding、step-count 与 real queue 已 independent-reviewed；local scheduler 保持 WARN |
| E Flow Matching/π0 | path/velocity、endpoint、ODE、mask、CFG | theorem/endpoint/time-sign/Beta independent-reviewed；historical package/local implementation 保持 WARN |
| F Architecture/Execution | RT-2/OpenVLA/Octo/π0、mask、adaptation、latency、controller | RT-2/Octo/openpi mask/transform/broker/example 已 independent-reviewed；local timing/axis/tests 未运行 |

## 2. 44 卡逐项映射

| ID | 主要 evidence chain | 必须保留的边界 | Verdict |
| --- | --- | --- | --- |
| VLA-ARCH-001 | RT-2/OpenVLA/π0 + A/B | semantic planner、policy、controller 分层 | `PASS/WARN` |
| VLA-ARCH-002 | A/B + inventory | view/state/time/H/K 不能由项目名反推 | `PASS/WARN` |
| VLA-ARCH-003 | A/B + inventory/ledger | backbone/head/expert/controller ownership 分开 | `PASS/WARN` |
| VLA-ARCH-004 | B/F | camera/mask/time alignment 是 converter/wrapper contract | `PASS/WARN` |
| VLA-ARCH-005 | A | paper 256-way 与 frozen 255-center decode 分开 | `PASS/WARN` |
| VLA-ARCH-006 | π0/B/E | action expert、H、solver 不反推本地实现 | `PASS/WARN` |
| VLA-ARCH-007 | RT-2/OpenVLA/Octo/π0/F | 不做跨协议指标排名 | `PASS/WARN` |
| VLA-ARCH-008 | A/B/F | attention-visible、label-visible、action mask 分开 | `PASS/WARN` |
| VLA-ARCH-009 | A/F | full/head/LoRA/expert 选择不冒充项目贡献 | `PASS/WARN` |
| VLA-ARCH-010 | B/F | d/D、padding、loss denominator 与 output slice 分开 | `PASS/WARN` |
| VLA-ARCH-011 | RT-2/FAST/openpi/F | source latency 不写成本地 timing | `PASS/WARN` |
| VLA-ARCH-012 | A–F + inventory/ledger | paper→repo→checkpoint→runtime→ownership 五层审计 | `PASS/WARN` |
| VLA-ACT-001 | π0/FAST/ACT/Diffusion + B–E | supervision/decoder 先于方法标签 | `PASS/WARN` |
| VLA-ACT-002 | A/B/F | normalization asset、axis 与 controller 前置 | `PASS/WARN` |
| VLA-ACT-003 | A | scalar bins 不解释 FAST/JSON 路线 | `PASS/WARN` |
| VLA-ACT-004 | A/B | vocab offset 与 custom formatter 分开 | `PASS/WARN` |
| VLA-ACT-005 | FAST/B | token compression 不等于 success uplift | `PASS/WARN` |
| VLA-ACT-006 | FAST/B | DCT/quantization/BPE 与 pinned revision 绑定 | `PASS/WARN` |
| VLA-ACT-007 | FAST/B + project page | 97.4% 不归因 FAST，protocol/artifact 缺口保留 | `PASS/WARN` |
| VLA-ACT-008 | B/F | H×D、valid d、padding/mask/slice 可验证 | `PASS/WARN` |
| VLA-ACT-009 | rotation + B/F | translation/rotation/gripper/base frame 不混用 | `PASS/WARN` |
| VLA-ACT-010 | ACT/Diffusion/FAST + B–E | 选型理由不代替 matched ablation | `PASS/WARN` |
| VLA-ACT-011 | ACT/C | prediction H、execution K、replan R 分开 | `PASS/WARN` |
| VLA-ACT-012 | ACT/C | CVAE chunk 只作方法/baseline，不冒充本地架构 | `PASS/WARN` |
| VLA-ACT-013 | ACT/C | train posterior 与 inference z=0 分开 | `PASS/WARN` |
| VLA-ACT-014 | ACT/C | oldest-weight ordering 与 query/target 轴显式 | `PASS/WARN` |
| VLA-ACT-015 | ACT/C | chunk、replan、temporal ensemble 三机制分开 | `PASS/WARN` |
| VLA-ACT-016 | ACT/C | horizon sweep 需 fixed checkpoint/protocol | `PASS/WARN` |
| VLA-ACT-017 | ACT/Diffusion/Flow + C–E | inductive bias 比较不等于本地 ablation | `PASS/WARN` |
| VLA-ACT-018 | Diffusion/D | 多模态生成直觉不自动证明 safety/success | `PASS/WARN` |
| VLA-ACT-019 | Diffusion/D | noisy action/noise target/condition 与 code target 绑定 | `PASS/WARN` |
| VLA-ACT-020 | Diffusion/D | schedule/prediction type/horizon/steps 分开 | `PASS/WARN` |
| VLA-ACT-021 | Diffusion/D | returned batch、executed prefix、re-observation 分开 | `PASS/WARN` |
| VLA-ACT-022 | Diffusion/D | paper 10/16、frozen config 8 与 warm-start gap 保留 | `PASS/WARN` |
| VLA-ACT-023 | Flow/E | probability path、velocity field、historical code 分开 | `PASS/WARN` |
| VLA-ACT-024 | Flow/E | exact-linear 与 sigma-min endpoint 分开 | `PASS/WARN` |
| VLA-ACT-025 | π0/openpi/E | time direction、velocity sign、NFE/solver 显式 | `PASS/WARN` |
| VLA-ACT-026 | Diffusion/Flow/D/E | target、time、sampler、budget 同协议比较 | `PASS/WARN` |
| VLA-ACT-027 | π0/B/E | local class/forward 才能证明 action expert | `PASS/WARN` |
| VLA-ACT-028 | openpi/B/E/F | all-D mean 与 valid-dim mask 不混称 | `PASS/WARN` |
| VLA-ACT-029 | Flow/E | CFG 仅作候选设计，未写成本地贡献 | `PASS/WARN` |
| VLA-ACT-030 | Diffusion/Flow/D/E | target→solver→norm/schema→controller 逐层排查 | `PASS/WARN` |
| VLA-ACT-031 | A/B/F | decode→unnorm→slice→frame/unit→safety 顺序明确 | `PASS/WARN` |
| VLA-ACT-032 | openpi/F | sentinel/FIFO/replan/stale RPC/NaN 测试是设计，未本地执行 | `PASS/WARN` |

## 3. 本次修复

1. 六个 Source Audit review 的 12 位截断 SHA 修复为完整 SHA-256，并与 canonical Markdown/HTML metadata 对齐。
2. 题卡增加 OpenPiVLA inventory 与 ownership ledger 总门；项目页存在、Git author 或上游实现不视为个人 ownership。
3. `VLA-ACT-031` 的 controller transform 与 (SO(3)) 改为有效 MathJax。
4. `VLA-ACT-032` 的追问改为“为什么不能依赖 `np.clip` 处理 NaN”，避免暗示 clip 会完成 sanitization。
5. π0.5、inventory、ownership 与 ACT/Diffusion/Architecture 三个独立复核入口纳入题卡来源表；27 个来源编号均需有定义和使用记录。

## 4. 可完成与不可完成

### 本页可以证明

- 12 个 ARCH + 32 个 ACT stable IDs 完整；44 张卡结构、长度、来源与项目 hook 可静态核验。
- 所有方法都能追到 primary/frozen source 或 A–F claim-to-code audit。
- 本地 OpenPiVLA 强 claim 继续受 checkpoint/schema/eval/ownership gate 约束。

### 本页不能证明

- Audit A/B/E 的局部 `independent_fact_review` 不会自动让 C/D/F 或 local project gate 变成 PASS；未复核项与本地 runtime/ownership 仍是 WARN。
- OpenPiVLA 的 model class、checkpoint、FAST revision、action axes、H/D/K、normalizer、solver、controller、97.4% protocol 或个人 ownership 已闭合。
- 44 张卡已经会讲；没有真实口述，全部继续 `unseen`。

## 5. 下一步

完成确定性校验后，VOL 03 状态仍为 `completion_reconciled_candidate / source_audits_warn / 44 unseen / WARN`。Audit A–F 的 public paper/code facts 均已完成独立切片；local checkpoint/schema/controller/latency/ownership 与真实口述仍未闭合。下一 bounded slice 改为一题真实口述或本地 runtime artifact，不得继续批量生成 VOL 03 卡。

## 参考入口

- [OpenVLA Audit A](vol_03_openvla_claim_to_code.html)
- [OpenVLA Endpoint / Token / Mask Independent Review](vol_03_openvla_endpoint_independent_fact_review.html)
- [π0 / π0.5 / FAST / openpi Audit B](vol_03_pi0_fast_openpi_claim_to_code.html)
- [ACT Audit C](vol_03_act_claim_to_code.html)
- [ACT Audit C 独立事实复核](vol_03_act_independent_fact_review.html)
- [Diffusion Policy Audit D](vol_03_diffusion_policy_claim_to_code.html)
- [Diffusion Policy Audit D 独立事实复核](vol_03_diffusion_policy_independent_fact_review.html)
- [Flow Matching / π0 Audit E](vol_03_flow_matching_pi0_claim_to_code.html)
- [Flow Matching / π0 Time–Sign Independent Review](vol_03_flow_pi0_time_sign_independent_fact_review.html)
- [π0 / π0.5 / FAST / OpenPI Independent Review](vol_03_pi0_fast_openpi_independent_fact_review.html)
- [Architecture / Execution Audit F](vol_03_architecture_execution_claim_to_code.html)
- [Architecture / Execution Audit F 独立事实复核](vol_03_architecture_execution_independent_fact_review.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)
