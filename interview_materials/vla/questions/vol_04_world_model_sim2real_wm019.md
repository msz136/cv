# VOL 04 World Model / Sim2Real：WM-019 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-WM-019`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[WM-019 Metric Boundary](../knowledge/vol_04_world_model_sim2real_wm019.html)；来源边界见 [WM-019 Metric Source Freeze](../sources/vol_04_wm019_metric_boundary_source_freeze.html)、[World Model Foundations Audit](../sources/vol_04_world_model_foundations_claim_to_code.html)、[UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)、[Benchmark / Evidence Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html) 与 [EVAL-003 statistical freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。本题不把项目页数字升级为个人结果。

## Metric ladder 与下游成功的证据边界

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-019</b> · PSNR/SSIM/FVD、latent/action MSE 与 downstream success 各能证明什么？</summary>

**面试意图**：判断你能否把视觉/latent/action proxy、open-loop 稳定性、simulator success 和 real closed-loop success 放在正确证据层级，并说清统计单位与可比协议。

**30 秒回答**：视觉指标只说明像素/视频相似，latent/action loss 只说明固定 target 的拟合；teacher-forced 看一步，open-loop 看累积。proxy、simulator、real success 合同不同，不能混成成功率；比较要固定 checkpoint、reset、predicate 和分母。

**机制展开（约 2 分钟）**：按证据阶梯：offline → teacher-forced → open-loop → proxy → simulator → real。PSNR/SSIM/FVD 只说明视觉，不证明动作；latent loss 依赖尺度、mask、reduction，action MSE 依赖动作语义、axis、horizon、normalizer。teacher-forced 喂真实历史，open-loop 喂自身预测，报告 offset/drift。success 按 episode 计，frame/step/row 不独立。paired validation 固定 checkpoint 和 init，保存脚本、分母、predicate；协议不同拆 model/protocol effect。

**诊断 / 证据**：建立逐 episode manifest，记录 task、init、seed、checkpoint、schema/normalizer、camera/preprocess、horizon、chunk/replan、controller、scorer/environment version、success predicate 和有效分母；同时保存 one-step/open-loop per-offset、action perturbation、proxy-vs-simulator paired table 及 failure trace。没有 checkpoint、脚本和分母，只能把项目数字标为 `WARN`，不能声称 uplift 或泛化。

**项目挂钩**：UWM/LIBERO 可讲 action/image MSE、fixed-pruned-init、reset-style 与 LIBERO success 必须分开命名；WAM 的 held-out MSE、World/value proxy、planning uplift 和 0-success 需要各自的 checkpoint、prediction/label、scorer、episode trace 与 denominator。OpenPiVLA、OPD 的百分比或 raw-holdout 规模只有在 metric-specific protocol 明确后才能引用；没有本地 artifact 时只讲审计方法，不声称自己跑出了该结果。

**追问树**：为什么低 action MSE 仍可能失败？FVD 如何避免被背景变化误导？teacher-forced 与 open-loop 的差异怎样用 tensor/rollout 表示？为什么 frame accuracy 不能直接算 success CI？如何做 proxy 与 simulator 的 paired validation？如果两个 checkpoint 的协议不同，怎样拆分 model effect 与 protocol effect？

**易错点**：把视觉指标叫作控制指标；把 one-step loss 当长时序可控性；把 action MSE 的 absolute/delta/axis/normalizer 忘掉；混淆 episode、step、frame、row 分母；把 WorldGym scorer、simulator predicate 和真实机器人 success 放在同一列平均；把公开 UWM/WAM/OpenPiVLA 数字写成个人实验。

**危险答案**：说“PSNR/FVD 高所以一定能抓取”“action MSE 降低就证明 online success 提升”“所有 success 都能用 episode-level CI”“WorldGym 分数就是 LIBERO/真实机器人成功率”或“论文数字就是我的项目结果”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-019 Metric Boundary 知识页](../knowledge/vol_04_world_model_sim2real_wm019.html)：metric ladder、统计单位、protocol tuple 与项目边界。
2. [WM-019 Metric Source Freeze](../sources/vol_04_wm019_metric_boundary_source_freeze.html)：PSNR/SSIM/FVD、latent/action loss、proxy/simulator/real success 的冻结语义。
3. [World Model Foundations Audit](../sources/vol_04_world_model_foundations_claim_to_code.html)：one-step/open-loop 与预测误差边界。
4. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)：conditional action/image MSE、LIBERO wrapper 与 checkpoint 边界。
5. [Benchmark / Evidence Audit E 与 EVAL-003](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)：strict protocol、reset/init、scorer 与 episode-level statistics。
