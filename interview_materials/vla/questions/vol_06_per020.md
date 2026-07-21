# VOL 06 Perception / Grounding / Navigation：PER-020 原子题卡

> 状态：`drafted / card_1_of_1 / source_frozen / knowledge_synced / WARN`  
> 更新日期：2026-07-21  
> 覆盖范围：`VLA-PER-020`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 短答限制：≤180字；机制展开限制：≤330字  
> 前置知识：[PER-020 Robustness / Safety Knowledge](../knowledge/vol_06_per020_robustness_safety_fallback.html)；来源边界见 [PER-020 Source Freeze](../sources/vol_06_per020_robustness_safety_fallback_source_freeze.html)。

## Robustness、Risk Gate、Fallback 与 E-stop

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-020</b> · VLA 面对 corruption、sensor dropout、dataset shift 或风险动作时，怎样证明 robustness、uncertainty、risk gate、fallback 与 E-stop 是同一套可复现协议？</summary>

**面试意图**：判断你能否把 shifted-input measurement、uncertainty calibration 和 chunked action safety 连接起来，并在项目追问中区分公开机制、局部接口、推断与未核实的个人安全结果。

**30 秒回答**：先锁 corruption/severity、denominator；shift 看 calibration 与 risk-coverage。风险门检查观测、硬约束、不确定性；触发即 flush 旧 chunk，按 recovery/fallback 处理，无法恢复才 E-stop。缺 raw shift、risk log、硬件审计时，不声称个人安全结果。

**机制展开（约 2 分钟）**：冻结 family/severity、RNG、shift set、denominator；不同 family 同号 severity 不横比。shifted split 看 calibration、risk-coverage、false-safe/false-alarm，保留拒答。执行层串起 validity→risk gate→hard constraint；风险后 flush chunk，按 recoverable 选择 reobserve、fallback 或 E-stop。五项目只有 schema/confidence hook；缺 raw shift、risk trace、matched eval、ownership，不声称安全提升。

**诊断 / 证据**：先查 sensor validity、timestamp、clean/shifted pair、family/severity/RNG→policy checkpoint、uncertainty/calibration bin→risk threshold/gate reason→action age、queue length、flush event→controller constraint/fallback/E-stop response→per-episode metric、cost、denominator→first-divergence taxonomy→ownership。camera severity sweep只能证明输入 shift协议；Safety Gym `cost_hazards`只能证明模拟器记录了cost。没有逐步trace时保留 `unknown/not_recomputable`。

**项目挂钩**：OpenPiVLA可谈image/action normalizer、parser、controller contract与shifted eval design；Robot Harness可谈tool schema、地图/点云和日志字段；OPD可谈confidence、negative case、risk-coverage；WAM/Cosmos可谈simulator diagnostics与visual shift taxonomy；UWM/LIBERO可谈fixed-init/reset、strict denominator。五者目前都不能证明个人OOD robustness、calibration uplift、fallback成功率、真实collision safety或E-stop ownership。

**追问树**：severity=5一定比另一个family的3严重吗？预生成JPEG和在线Gaussian能直接比较吗？confidence高但动作错是什么风险？风险门触发后为什么必须flush chunk？fallback与retry区别？Safety Gym cost=0能否代表真实安全？randomize_layout=False/True是否同一泛化协议？没有raw trace能否确认collision根因？如何给五个项目各写一句不越界回答？

**易错点**：把severity跨family当物理量；把clean accuracy或confidence当OOD safety；把阈值叫calibration却不报告risk-coverage；风险后继续执行旧chunk；把retry当fallback；把Safety Gym cost、randomization、simulator rollout或上游代码写成个人安全结果；把Git author、字段名或summary当ownership。

**危险答案**：说“confidence高所以动作安全”“Safety Gym cost为0所以真实机器人安全”“风险门触发后执行完当前chunk再说”“有randomization就证明sim2real”“项目已经有robustness提升”，却不能给出family/severity、shifted denominator、calibration、queue flush、fallback/E-stop trace与个人证据。

**来源**：[1][2][3][4][5][6]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-020 Robustness / Safety Knowledge](../knowledge/vol_06_per020_robustness_safety_fallback.html)：corruption protocol、risk–coverage、risk gate、queue flush、fallback/recovery/E-stop、五项目边界与两档回答。
2. [PER-020 Source Freeze](../sources/vol_06_per020_robustness_safety_fallback_source_freeze.html)：2 个 primary papers、4 个 official code/docs、10/10 probes 与 claim boundary。
3. Hendrycks & Dietterich，[Benchmarking Neural Network Robustness to Common Corruptions and Perturbations](https://arxiv.org/pdf/1903.12261)。
4. Ovadia et al.，[Can You Trust Your Model's Uncertainty?](https://arxiv.org/pdf/1906.02530v2)。
5. Hendrycks robustness [`corruptions.py`](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/imagenet_c/imagenet_c/corruptions.py) 与 OpenAI Safety Gym [`engine.py`](https://github.com/openai/safety-gym/blob/f31042f2f9ee61b9034dd6a416955972911544f5/safety_gym/envs/engine.py)。
6. [VOL 04 WM-038 uncertainty/safety/fallback source freeze](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。
