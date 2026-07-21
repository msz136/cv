# VOL 06 PER-020：Robustness、Safety、Fallback 与风险门独立事实复核

> 状态：`independent_fact_review / VLA-PER-020 / paper_code_refetched / source_knowledge_card_reconciled / PASS_WITH_WARNING`  
> 审查日期：2026-07-21  
> 证据截止：2026-07-21  
> 范围：重新获取 2 份 primary PDF、4 个 fixed official files，重跑 bounded source probes，并复核 PER-020 source→knowledge→card；不生成新题卡、不改变 276 张题卡的 `unseen` 状态、不创建 `coaching_state.md`。

## 问题（Question）

PER-020 对 corruption family/severity、dataset shift uncertainty、risk–coverage、Safety Gym cost、queue flush、fallback/recovery/E-stop 的表述，是否能被重新获取的 primary paper、fixed official code 与当前仓库证据逐项支持？哪些内容仍只能作为工程合同或面试回答，不能升级为个人项目安全/鲁棒性结果？

## 1. 结论先行

1. **6/6 外部文件重新获取成功并命中 source freeze SHA**：Hendrycks & Dietterich PDF 1,080,004 bytes / 16 pages；Ovadia et al. PDF 5,887,184 bytes / 25 pages；robustness README、`corruptions.py`、Safety Gym README、`engine.py` 均与冻结记录 byte-identical。
2. **公开机制边界成立**：README 同时区分 ImageNet-C 与 ImageNet-P；`corruptions.py` 保留 severity 1–5 的 family-specific 参数与随机/clip 行为；Safety Gym `engine.py` 暴露 `constrain_hazards`、`cost_hazards`、`cost` 与 `randomize_layout` 语义。这些只支持 benchmark/environment 机制，不支持本地 VLA 已跑过对应协议。
3. **Ovadia 的可安全转译结论是“confidence ≠ shifted risk”**：应报告 calibration、selective risk–coverage 与 false-safe/false-alarm；不能把 clean confidence 或单一平均分当作安全保证。
4. **queue flush / fallback / recovery / E-stop 仍是 cross-volume WM-038 的工程合同**：本轮没有发现任何五项目 raw step trace、硬件审计或 ownership ledger，不能把该合同说成项目已经实现。
5. **source→knowledge→card 八个 claim cluster 对齐**：corruption/severity、shifted calibration、risk–coverage、hard constraint、chunk flush、fallback/recovery/E-stop 与五项目 truth boundary 在三层页面中语义一致；题卡仍 `unseen`。
6. 本页 verdict 为 **`PASS WITH WARNING`**：外部事实与下游映射通过；本地 robustness/safety runtime、真实机器人 cost、零事故、fallback 成功率和候选人 ownership 仍为 `unverified`。

## 2. 外部文件再获取与 SHA

| Source | Fixed revision / URL | Bytes / pages | Re-fetched SHA-256 | 结果 |
| --- | --- | ---: | --- | --- |
| Hendrycks & Dietterich | [arXiv 1903.12261](https://arxiv.org/pdf/1903.12261) | 1,080,004 / 16 | `c9df5483aa331dd99808350608a795c4bd9b84a7ee50396748c7d258903ea582` | PASS |
| Ovadia et al. | [arXiv 1906.02530v2](https://arxiv.org/pdf/1906.02530v2) | 5,887,184 / 25 | `1610d04d7f69d10751f0e9ff1db9fbd8b3fdf5306798879016192eb2dbf17a6f` | PASS |
| robustness README | commit `8190fe329f5f072a06e3a2aea02bb5dda69aed9f` | 7,354 | `718d37a53a84615961dcdf519602cfaf1467b192bb691f8e880fbadf9e92de0d` | PASS |
| `corruptions.py` | same commit | 14,857 | `fb962115845e0a7ceaf5a6e3cda17f4aab07c66e3c367c219cafc7032c4a43fb` | PASS |
| Safety Gym README | commit `f31042f2f9ee61b9034dd6a416955972911544f5` | 11,348 | `2728e304d7b8483ce910d60c4880782aeb111c5fa127614b0a1d3f8bfd4653b5` | PASS |
| Safety Gym `engine.py` | same commit | 72,367 | `9d52a3206648938408c05473eb48f12a78230938ea5c4b9ca878afaab087693c` | PASS |

PDF 页数由独立 `pypdf` 读取；文件 bytes 与冻结记录完全一致。重新获取证明 source identity，不证明任何训练、仿真或硬件运行。

## 3. 独立 source probes

| Probe | 重新观察 | 支持的窄结论 |
| --- | --- | --- |
| P20-R1 | robustness README 含 `ImageNet-C` | README 明确静态 common-corruption 评估入口 |
| P20-R2 | robustness README 含 `ImageNet-P` | README 同时覆盖 temporal perturbation 语境 |
| P20-R3 | `corruptions.py` 含 40 处 `severity` 参数引用 | severity 是实现参数，不是跨 family 的统一物理量 |
| P20-R4 | `corruptions.py` 的 Gaussian/shot/impulse/speckle 路径使用随机与 clip/归一化 | 在线注入必须记录 RNG、dtype、clip 与输出策略 |
| P20-R5 | Safety Gym `engine.py` 含 `constrain_hazards` | 未启用 constraint 配置不能声称测过 hazard constraint |
| P20-R6 | `engine.py` 含 `cost_hazards` 与聚合 `cost` | safety 记录应保留逐 step/episode cost 与 denominator |
| P20-R7 | `engine.py` 含 `randomize_layout` | 固定布局与随机布局是不同 protocol，不能混报泛化 |
| P20-R8 | Ovadia PDF 可重新读取 uncertainty/calibration/dataset-shift 章节 | confidence 不能直接替代 shifted risk |
| P20-R9 | WM-038 source freeze SHA `017dbe706784...eabbb3c` 命中本地文件 | queue flush、short-prefix、fallback/E-stop 是本仓库工程合同 |
| P20-R10 | PER-020 source/knowledge/card 的 stable ID 均为 `VLA-PER-020` | downstream identity 与题卡映射一致，不新增题卡 |

结果：**10/10 probes 通过**。P20-R1–R7 是 source-text probes，P20-R8 是 paper retrieval/section probe，P20-R9–R10 是 local identity probes；它们都不是 benchmark runtime 或硬件安全证据。

## 4. Claim boundary：论文、官方代码与工程合同

### 4.1 Corruption 与 severity

Hendrycks & Dietterich 支持 common corruptions/perturbations 与 ImageNet-C/P 的 benchmark 语境；官方 `corruptions.py` 的 severity 参数是每个 family 自己定义的离散等级。安全的面试说法是：“我会固定 family、severity、clean/shifted pair、split、seed、checkpoint 和 denominator，再比较同一 protocol 下的指标。”不能说 severity 5 的 Gaussian 一定比 severity 3 的 JPEG 更严重，也不能把预生成 JPEG 与在线随机 Gaussian 当作同一个实验。

### 4.2 Uncertainty 与 selective risk

Ovadia 支持 dataset shift 下对 predictive uncertainty、calibration 和 risk 行为进行评估。风险–coverage 的教学表达为：

$$
\operatorname{Risk}(C)=\mathbb{E}[\ell(\hat y,y)\mid\operatorname{accept}=1],
\qquad C=\Pr(\operatorname{accept}=1).
$$

`accept` 由 risk gate 决定，`ell` 可是任务错误、约束违规或失败损失。公式只定义 selective evaluation，不证明模型已校准；拒答/fallback 样本必须保留，否则会制造 false-safe。

### 4.3 Safety Gym 与真实安全的边界

Safety Gym README/`engine.py` 支持 constrained task、hazard cost 与布局随机化配置。它不支持以下升级：

- 使用 Safety Gym 就等于真实机器人 safety；
- `cost=0` 就等于 zero collision 或 zero accident；
- `randomize_layout=True` 就等于 sim-to-real 泛化；
- 没有逐 episode/step cost、seed、布局与 checkpoint，就能复算个人结果。

### 4.4 Queue flush、fallback、recovery 与 E-stop

WM-038 的工程合同把执行语义写成：风险门触发后停止继续 apply，清空过期 chunk，再选择 re-observe、safe controller、人工接管或 E-stop。该合同解决的是“系统应该如何 fail-closed”，不是“项目已经安全”。若没有 action-age、queue length、flush event、gate reason、controller response 与 E-stop latch 的 raw trace，结论必须保持 `unknown/not_recomputable`。

## 5. Source → Knowledge → Card reconciliation

| Claim cluster | Source evidence | Knowledge page | Atomic card | Verdict |
| --- | --- | --- | --- | --- |
| family/severity/RNG | Hendrycks paper + `corruptions.py` | §3 protocol/manifest | 30秒答先锁 family/severity/denominator | PASS |
| clean vs shifted | ImageNet-C/P and fixed pair semantics | shifted metric + denominator | clean score 不替代 shifted score | PASS |
| confidence/calibration | Ovadia paper | calibration、risk–coverage、false-safe | confidence 不等于 safety | PASS |
| hard constraint/risk gate | Safety Gym contract + WM-038 | validity→risk→constraint state machine | gate reason 与 evidence gate | PASS |
| stale chunk | WM-038 | queue flush / action age | 风险后必须 flush | PASS |
| fallback/recovery/E-stop | WM-038 engineering boundary | recoverable vs terminal state | fallback≠retry；不可恢复才 E-stop | PASS WITH WARNING |
| five projects | local inventories and absence checks | interface hooks only | 不声称 personal OOD/safety result | PASS WITH WARNING |
| practice state | local card/review metadata | card remains unseen | no mastery/coaching update | PASS |

本轮没有发现需要改写 PER-020 30 秒答案或机制展开的事实错误；新增的最稳妥限定仍是：“Safety Gym、randomization 和公开 queue/fallback 机制是协议参照，不是我的个人安全结果。”

## 6. 五项目真实性复核

| 项目 | 当前可说 | 本轮仍不能说 |
| --- | --- | --- |
| OpenPiVLA | image/action normalizer、parser、controller contract、shifted-eval 设计 | 已完成 OOD robustness、calibration uplift、zero-accident 或 E-stop ownership |
| Robot Harness | tool schema、地图/点云输入、约束与日志字段设计 | Safety Gym cost、fallback success rate、真实硬件 safety |
| OPD | grounding confidence、negative case、risk–coverage 设计 | grounding robustness uplift 或 deployed safety guarantee |
| WAM / Cosmos | simulator diagnostics、visual-shift taxonomy、失败 trace | 上游 randomization/rollout 是个人 sim-to-real 或安全结果 |
| UWM / LIBERO | fixed-init/reset、strict denominator、failure taxonomy | 真实机器人 OOD 泛化、碰撞率或安全控制器结果 |

当前检查的 local-direct 入口仍只支持 `public upstream mechanism → local evidence/interface → inference → unverified` 四层边界。没有新发现可把任何项目升级为已完成安全闭环。

## 7. 静态结构与状态检查

- PER-020 source、knowledge、card canonical Markdown SHA 与各自 review JSON 已存在且一致；本页 source SHA 为 `独立复核文件写入后生成`。
- 题卡 stable ID 仍只有 `VLA-PER-020`；global card count 不变，`unseen=276`。
- 本轮不创建、不修改 `interview_materials/vla/practice/coaching_state.md`。
- 新 HTML 必须由 academic renderer 生成，并执行 one-H1、heading hierarchy、MathJax balance、`.formula em = 0`、contained overflow、local-link 与 SHA 检查。
- 浏览器 connector 当前不可用，因此只能报告静态 ARIS/responsive 检查；不把缺失截图写成 browser PASS。

## 8. 审查状态与下一步

本轮的一个 bounded primary deliverable 是 PER-020 independent fact-review 三联件。其退出条件已满足：6/6 外部文件 SHA 命中、10/10 probes 通过、source→knowledge→card 对齐、五项目边界未升级、mastery 未变化。

仍开放：

1. 本地 shifted-input bundle、逐步 risk log、matched robustness panel、硬件 E-stop audit 与 candidate ownership ledger；
2. 一题真实 PER-020 口述，之后才允许更新 mastery 或创建 coaching state；
3. 若用户暂不练习，下一切片选择 VOL 04 Audit C/D 独立复核，不启动新卷或批量生成。

## References

1. [PER-020 Source Freeze](vol_06_per020_robustness_safety_fallback_source_freeze.html)。
2. [PER-020 Knowledge](../knowledge/vol_06_per020_robustness_safety_fallback.html)。
3. [PER-020 Atomic Card](../questions/vol_06_per020.html)。
4. Hendrycks & Dietterich，[Benchmarking Neural Network Robustness to Common Corruptions and Perturbations](https://arxiv.org/pdf/1903.12261)。
5. Ovadia et al.，[Can You Trust Your Model's Uncertainty?](https://arxiv.org/pdf/1906.02530v2)。
6. Hendrycks robustness [`README.md`](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f) 与 [`corruptions.py`](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/imagenet_c/imagenet_c/corruptions.py)。
7. OpenAI Safety Gym [`README.md`](https://github.com/openai/safety-gym/tree/f31042f2f9ee61b9034dd6a416955972911544f5) 与 [`engine.py`](https://github.com/openai/safety-gym/blob/f31042f2f9ee61b9034dd6a416955972911544f5/safety_gym/envs/engine.py)。
8. [VOL 04 WM-031 reality-gap taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.html) 与 [VOL 04 WM-038 uncertainty/safety/fallback](vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。
