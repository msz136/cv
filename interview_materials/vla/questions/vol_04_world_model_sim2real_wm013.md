# VOL 04 VLA-WM-013 原子题卡：Latent Overshooting 与 Multi-step Consistency

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-013  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-013 Knowledge](../knowledge/vol_04_world_model_sim2real_wm013_latent_overshooting_multistep_consistency.html)；来源边界见 [WM-013 Source Freeze](../sources/vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html)。

## latent overshooting 或 multi-step consistency loss 解决什么，可能带来什么偏差？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-013</b> · latent overshooting 或 multi-step consistency loss 解决什么，可能带来什么偏差？</summary>

**面试意图**：判断你能否从一步KL的gradient-distance限制推导多步prior监督，解释posterior target、distance/weight/mask/stop-gradient与official-code路径，并主动指出final/default PlaNet未启用及multi-step regularization的偏差。

**30 秒回答**：单步KL训一步prior；latent overshooting从较早posterior出发，关中间观测，滚d步prior对齐未来posterior，约束多步一致性。可能减小drift，会放大posterior/leakage、action/mask错位、受限分布与过强正则。PlaNet final/default未启用，需D/β sweep和闭环对照验证。

**机制展开（约 2 分钟）**：对每个start和distance d，用记录动作做prior-only rollout，再算KL[sg(q_t)||p_t^(d)]；m_{t,d}切掉padding/terminal，β_d和denominator决定有效权重。PlaNet code先filter posterior，shift action/target/mask，use_obs=false，再可选stop posterior gradient。风险包括learned target错误、多模态family受限、长distance样本少/梯度高方差、计算预算不matched；latent KL好不等于reward/contact/success好。

**诊断 / 证据**：保存per-distance start/action/target/prior/mask、raw/free-nats KL、valid count、β、gradient、entropy/mode usage、action swap、future-frame removal、one-step/posterior/prior-only horizon curves、reward/contact/continue、planning/closed-loop success、steps/tokens/wall-clock/memory与seed CI。

**项目挂钩**：WAM/Cosmos与UWM是diffusion-based action/future/video contract，不是PlaNet overshooting；当前没有per-distance KL、D/β sweep或matched成功率。安全说“能设计可选multi-step消融”，不能说“项目用了overshooting”或“DreamerV3默认采用该loss”。

**追问树**：一步正确为何多步还错？d-step prior怎样构造？target为何是posterior而非真state？为什么d>1 stop-gradient？observation overshooting有何不同？D/β怎么选？长distance denominator怎样算？多模态未来会怎样？为什么final PlaNet未启用？DreamerV3是否使用？怎样证明改进不是更多算力或latent collapse？

**易错点**：把overshooting说成pixel MSE；把posterior当ground truth；rollout继续读中间观测；action错一位/跨terminal；只看总KL；忽略per-distance count与compute；认为D越大越好；把PlaNet提出等同默认启用；把PlaNet机制归给DreamerV3/WAM/UWM。

**危险答案**：说“多步loss能消除compounding error”“posterior一定正确”“一致性越强representation越好”“PlaNet靠overshooting才成功”“DreamerV3默认有latent overshooting”“latent KL下降就证明planning/机器人成功”“我的WAM/UWM已经验证该机制”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-013 Source Freeze](../sources/vol_04_wm013_latent_overshooting_multistep_consistency_source_freeze.html)：PlaNet论文、official-code SHA、公式与偏差边界。
2. Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)。
3. `google-research/planet@c04226b`：`overshooting.py`、`training/utility.py`、`configs.py`。
4. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-014`，不创建 `coaching_state.md`。
