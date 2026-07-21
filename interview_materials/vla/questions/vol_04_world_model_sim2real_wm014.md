# VOL 04 VLA-WM-014 原子题卡：Action-conditioned、相关性与可干预 Dynamics

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-014  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-014 Knowledge](../knowledge/vol_04_world_model_sim2real_wm014_action_conditioned_correlation_intervention.html)；来源边界见[WM-014 Source Freeze](../sources/vol_04_wm014_action_conditioned_correlation_intervention_source_freeze.html)。

## action-conditioned prediction怎样区分相关性预测与可干预dynamics？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-014</b> · action-conditioned prediction怎样区分相关性预测与可干预dynamics？</summary>

**面试意图**：判断你能否区分action tensor接入、模型敏感、observational fit与do-effect alignment，写出hidden-confounder差异与识别假设，并把same-state action-swap、executed-action contract、support/cross-policy/real evidence闭合。

**30 秒回答**：action入网只证明条件化。若隐藏u同时影响选a和未来y，p(y|x,a)混入p(u|x,a)，不等于do-effect。只有state/history阻断混杂且action有overlap才可识别。验证需同state/seed换action，对齐model/env effect delta，再查跨policy、OOD和closed-loop。

**机制展开（约 2 分钟）**：观测分布积分p(y|x,a,u)p(u|x,a)，干预分布用p(u|x)；还需consistency与正确时间顺序。先做shuffle/zero/Jacobian确认模型使用action，但它不证明effect正确。强测试从同snapshot执行a/a'，比较(ŷ(a)-ŷ(a'))与(y_env(a)-y_env(a'))，随机环境多seed看distribution。treatment应是denorm/clip/controller后的executed action；real端用matched reset和安全小扰动。

**诊断 / 证据**：保存full snapshot/exogenous seed、policy observation、raw/denorm/approved/executed action、controller state/timestamps、action support/OOD、predicted/actual outcome与effect、horizon、contact/reward/termination、repeats/CI、policy ID、nuisance intervention、invalid/reset、安全gate与closed-loop result。

**项目挂钩**：WAM/Cosmos有action/future/value contract，UWM有action/video shared diffusion与sim protocol，但没有cloned-state pair、effect alignment、cross-policy/support或real matched trial。安全说“能按证据阶梯审计”，不能说“action-conditioned所以项目已学到causal dynamics”。

**追问树**：conditioning与do差在哪？何时二者相等？partial observation如何混杂？positivity是什么？Jacobian非零能证明什么？command与executed action区别？怎样clone contact/controller state？随机未来如何比较？real不能clone怎么办？cross-policy为何重要？sim intervention为何不等于real？规划成功是否证明内部因果图正确？

**易错点**：把action拼接当causal；把action sensitivity当effect alignment；忽略hidden state/overlap；用不同initial state比较；只换raw command却被clip；action/observation错位；单seed比较随机结果；sim result外推real；support外强行解释；把WAM/UWM公开coupling写个人因果验证。

**危险答案**：说“神经网络看见action就学到因果”“held-out MSE低等于do-effect正确”“随机swap一次就证明counterfactual”“simulator能reset所以真实也成立”“Jacobian越大因果越强”“WAM/UWM action-conditioned因此已验证可干预dynamics”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-014 Source Freeze](../sources/vol_04_wm014_action_conditioned_correlation_intervention_source_freeze.html)：observational/do公式、识别假设、effect metric与项目边界。
2. Oh et al., [Action-Conditional Video Prediction](https://arxiv.org/abs/1507.08750)。
3. de Haan et al., [Causal Confusion](https://arxiv.org/abs/1905.11979)；Wang et al., [Causal Dynamics Learning](https://arxiv.org/abs/2206.13452)。
4. Buesing et al., [Woulda, Coulda, Shoulda](https://arxiv.org/abs/1811.06272)；Ahmed et al., [CausalWorld](https://arxiv.org/abs/2010.04296)。
5. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 下一步

保持`unseen`，直到候选人完成真实口述。VOL 04知识/题卡达到44/44；下一步转入其他卷的首个source-ready缺口，不创建`coaching_state.md`。
