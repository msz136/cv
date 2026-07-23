# WM-019 WAM Action-Trace Paired Diagnostic（CoffeePressButton）

> 状态：`paired_diagnostic / local-direct-trace-math / checkpoint-unverified / WARN`  
> 计算日期：2026-07-18  
> 证据截止：2026-07-18  
> 范围：只比较同一 CoffeePressButton episode 0、相同 seed/env_seed 和相同 300-step protocol 下的 base/trained `actions.jsonl`；不把 trace 差异解释为 checkpoint 因果、success uplift 或 benchmark 结果。

## 1. 目的与边界

WM-019 要求把 action MSE、open-loop trace 与 downstream success 分层。本切片只回答三个低层问题：

1. base/trained action trace 是否逐步对齐、shape 是否一致、是否有非有限值？
2. 两条 trace 的逐步差异有多大？
3. 两条 trace 的 `success_after_step`、reward 和 episode 长度是否支持更高层结论？

它不回答：哪个 checkpoint 更好、为什么不同、是否提升成功率、是否代表 WAM 全部任务。

## 2. 输入 identity

| side | manifest SHA | action trace SHA | protocol |
| --- | --- | --- | --- |
| base | `63A518674F061D1C14A880805FF9C23DAC2425C9D7B34CC4C75FD3CEDBD33A86` | `C6A3623B26B97F7ED88AA13AE675C8315DC509D3D867CBB6E417CAF51F88525D` | CoffeePressButton、episode 0、seed 195、env_seed 0、300 steps、open-loop 16、denoise 5 |
| trained | `809AE4F879C9421F954C7BFC26C70005B94387412449039F9FA8B6E479EF55CC` | `9C6A4F00DA8107EB0C1FDDDC642D1986CD510D92F7F6E3A68ADE834E8B82CF2D` | 同上；checkpoint 字段仍为远端路径 |

输入文件均来自 [WM-019 WAM Artifact Manifest](wm019_wam_artifact_manifest.html)。本报告没有读取或修改远端 checkpoint。

## 3. Trace integrity

| check | base | trained | 结论 |
| --- | ---: | ---: | --- |
| rows | 300 | 300 | 一致 |
| `t` range | 0..299 | 0..299 | 逐步对齐 |
| `policy_action7` shape | 300×7 | 300×7 | 一致 |
| `env_action` shape | 300×12 | 300×12 | 一致 |
| non-finite policy values | 0 | 0 | 未发现 NaN/Inf |
| `success_after_step=True` | 0 | 0 | 两条 trace 都未触发成功字段 |
| reward sum | 0.0 | 0.0 | 不能作为更高层 success 证明 |

shape 与有限性检查只证明 JSONL 的结构可读；不证明动作语义、controller 映射或 checkpoint 内容正确。

## 4. Paired difference

对齐同一 `t` 后，令 \(a_t^{(b)}\) 和 \(a_t^{(t)}\) 分别为 base/trained 的 7 维 `policy_action7`，计算：

\[
\operatorname{MAE}=\frac{1}{Td}\sum_{t=1}^{T}\sum_{j=1}^{d}|a_{t,j}^{(b)}-a_{t,j}^{(t)}|,
\qquad
\operatorname{RMSE}=\sqrt{\frac{1}{Td}\sum_{t=1}^{T}\sum_{j=1}^{d}(a_{t,j}^{(b)}-a_{t,j}^{(t)})^2}.
\]

这里 (T=300,d=7)。它们只是两份 action trace 的几何差异，不是 action-label loss，也不等于成功率。

| measure | value |
| --- | ---: |
| policy MAE | `0.3100783611` |
| policy RMSE | `0.3906446459` |
| per-dimension MAE | `[0.38234915, 0.31824048, 0.27147196, 0.38302800, 0.30951413, 0.24404278, 0.26190202]` |
| mean policy norm, base | `0.6584048120` |
| mean policy norm, trained | `0.6782378918` |

逐步差异明显，但由于两个 checkpoint binary 不在本地、没有 prediction target/metric script，也没有成功 episode，不能把差异归因于某个训练改动，更不能说 trained “更好”或“更差”。

## 5. Range diagnostic

| dimension | base min | base max | trained min | trained max |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0.074116 | 0.389210 | -0.569726 | 0.206362 |
| 1 | 0.064427 | 0.395674 | -0.485705 | 0.294611 |
| 2 | 0.081652 | 0.409145 | -0.454376 | 0.420165 |
| 3 | 0.050104 | 0.426199 | -0.686172 | 0.402813 |
| 4 | 0.027087 | 0.366351 | -0.622367 | 0.335208 |
| 5 | -0.017900 | 0.354746 | -0.501100 | 0.373214 |
| 6 | -0.049619 | 0.515565 | -0.428721 | 0.371992 |

范围差异可以作为 controller/action-normalizer 排查入口，但不能单凭 range 断言 high-sigma、gripper、normalizer 或动作顺序是根因。需要 action schema、normalizer、checkpoint 和 paired rerun 才能继续归因。

## 6. WM-019 ladder placement

| 层级 | 本切片能支持什么 | 仍不能支持什么 |
| --- | --- | --- |
| trace integrity | 两份 JSONL 的 row/t/shape/finite/success 字段可审计 | checkpoint 可加载、动作语义正确 |
| open-loop diagnostic | 300-step trace 的逐步差异与范围差异 | per-offset prediction error、action sensitivity causal test |
| simulator success | episode 0 两边 `success=false` 字段 | denominator、完整 suite success、模型比较 |
| project claim | “有一组可复核的 action-rollout diagnostic bundle” | WAM MSE、uplift、0-success benchmark、个人原创 architecture |

## 7. 下一最小补件

1. 补 base/trained checkpoint 或 immutable remote hash，并绑定 processor/normalizer/config SHA。
2. 把 alternate trained-video output root 绑定进 run manifest，并建立多 episode manifest 和 success predicate/denominator。
3. 用同一 target/schema 计算 per-offset prediction error、action sensitivity 与 controller round-trip。
4. 只有 paired rerun 显示固定 protocol 下的 success 差异，才讨论 model effect；当前不更新简历数字。

## 参考来源

1. [WAM Artifact Manifest](wm019_wam_artifact_manifest.html)。
2. [WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
3. [WM-019 Project Metric Artifact Gate](../../sources/vol_04_wm019_project_metric_artifact_gate.html)。
4. [WM-019 Metric Source Freeze](../../sources/vol_04_wm019_metric_boundary_source_freeze.html)。
