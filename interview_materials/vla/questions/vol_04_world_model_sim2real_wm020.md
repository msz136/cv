# VOL 04 VLA-WM-020 原子题卡：Posterior Collapse / Action Ignoring / Leakage / Shortcut

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`VLA-WM-020`  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：`unseen`  
> 前置知识：[WM-020 Knowledge](../knowledge/vol_04_world_model_sim2real_wm020_failure_diagnostics.html)；来源边界见 [WM-020 Source Freeze](../sources/vol_04_wm020_failure_diagnostics_source_freeze.html)。

## World model 四类 failure 如何诊断

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-020</b> · 怎样发现 posterior collapse、action ignoring、future leakage 与 background shortcut？</summary>

**面试意图**：判断你能否把 failure 映射到不同控制变量和干预，而不是用一个 loss 解释所有 world-model 问题。

**30 秒回答**：四层排查：collapse 看 posterior/prior 与 latent ablation；ignoring 固定观测做 action swap；leakage 查时间戳、causal mask、未来帧和 shift；shortcut 固定任务动作换背景。冻结 split、mask、seed、horizon；单一 loss 不能证明因果有效。

**机制展开（约 2 分钟）**：collapse 查 posterior/prior、KL、latent usage 和 zero/mean ablation；低 KL 不是充分条件。ignoring 用固定 observation 做 action swap/sweep，看 future delta。leakage 画可见集合，移除未来帧并核对 timestamp、shift、causal mask 和 teacher/open-loop gap。shortcut 固定 task/action 换背景或相机，再做 counterfactual。所有结果绑定 checkpoint、split、mask、seed、horizon 和 raw trace；没有 probe 只能说测试方案。

**诊断 / 证据**：输出 latent usage、action intervention delta、visibility matrix、future-removal replay、per-offset teacher/open-loop，以及 background/domain holdout。action sensitivity 低时先排除延迟、接触时间窗、归一化和噪声；换背景掉点后仍需 object/action counterfactual 才能称 shortcut。

**项目挂钩**：UWM/LIBERO 可挂 action/image conditional loss、normalizer、fixed/reset protocol 与 mask；WAM/Cosmos 可挂 world/value/action slot 与 offline proxy；OpenPiVLA 可挂 causal-CE/sequence mask；OPD/Harness 可挂 schema、scorer 和 episode trace。安全表达是“我能设计并审计这些 probe”，不把项目已有 MSE、0-success、格式 scorer 或公开代码写成 WM-020 failure 的个人实验证据。

**追问树**：低 KL 是否一定 collapse？action token 存在为何仍会 ignoring？怎样区分 action delay 与 ignoring？causal mask 正确但仍 leakage 可能在哪？为什么随机 split 会掩盖 background shortcut？background swap 与 domain randomization 有何差异？teacher-forced 高分为什么不能证明闭环？需要哪些 raw artifacts 才能升级结论？

**易错点**：把 KL 低直接等于 collapse；把 attention/action gradient 当因果证明；只检查 `causal=True` 不查数据 shift；把背景增强一次当作 shortcut 已消除；把 offline loss 或 video quality 当作 action consequence；忽略 horizon、timestamp、normalizer、valid mask 和 episode denominator。

**危险答案**：说“action 在输入里所以模型一定用了它”“teacher-forced accuracy 高就没有泄漏”“domain randomization 后 shortcut 肯定消失”“低 KL 说明模型坏了”“一个 world-model loss 下降证明项目闭环成功”。

**来源**：[1][2][3][4][5][6]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-020 Source Freeze](../sources/vol_04_wm020_failure_diagnostics_source_freeze.html)：四类 failure、诊断矩阵和项目边界。
2. [World Model Foundations Audit A](../sources/vol_04_world_model_foundations_claim_to_code.html)：RSSM、one-step/open-loop、actionability 与 model bias。
3. [DreamerV3 independent fact review](../sources/vol_04_world_model_foundations_independent_fact_review.html)：posterior/prior、dyn/rep KL、free-nats 与 reimplementation 边界。
4. [ACT claim-to-code audit](../sources/vol_03_act_claim_to_code.html)：CVAE posterior/prior、KL、action chunk 与 latent train/infer gap。
5. [Architecture / execution audit](../sources/vol_03_architecture_execution_claim_to_code.html)：sequence、causal mask、loss mask 与 future visibility。
6. [PER-003 Multi-view / Temporal](../knowledge/vol_06_per003_multiview_temporal.html)：timestamp、presence、causal/ordered mask 与 replay leakage。
