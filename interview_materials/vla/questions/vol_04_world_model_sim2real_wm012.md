# VOL 04 VLA-WM-012 原子题卡：RSSM / Dreamer Posterior、Prior、KL Balancing 与 Imagination

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-012  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-012 Knowledge](../knowledge/vol_04_world_model_sim2real_wm012_rssm_dreamer_posterior_prior_kl_imagination.html)；来源边界见 [WM-012 Source Freeze](../sources/vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)。

## RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-012</b> · RSSM / Dreamer 的 posterior、prior、KL balancing 与 imagined rollout 如何推导？</summary>

**面试意图**：判断你能否从 action-conditioned sequential ELBO 推导 RSSM filtering/prediction，解释 KL 对 prior/posterior 的两条梯度职责，区分 DreamerV2 balancing 与 DreamerV3 dyn/rep/free bits，并闭合 replay posterior start→prior-only imagination 的时间索引。

**30 秒回答**：RSSM状态含记忆h与随机z：posterior读观测校正，prior只靠历史动作预测。KL既训prior追posterior，也约束posterior可预测；V2用stop-gradient加权，V3拆dyn/rep并加free bits。imagination从replay posterior起点开始，随后只用policy与prior，禁读未来观测。

**机制展开（约 2 分钟）**：先由h_t=f(h_{t-1},z_{t-1},a_{t-1})，再比较q(z_t|h_t,o_t)与p(z_t|h_t)。ELBO是prediction likelihood减KL。V2以α=0.8偏重KL[sg(q)||p]；V3分别用dyn=KL[sg(q)||p]、rep=KL[q||sg(p)]，1 nat以下free bits，frozen config scale 1/0.1。replay先observe得posterior entries，选start后循环policy→core→prior→sample，未来token不得进入。

**诊断 / 证据**：保存previous-action/reset对齐、posterior/prior logits与sample、raw/clipped KL、clipping ratio、dyn/rep scale、entropy/category usage、gradient norm、start episode/time、action/prior trace、future-observation removal、zero/shuffled-action、posterior-vs-prior horizon curve、cloned-state consequence与closed-loop结果。

**项目挂钩**：WAM/Cosmos是diffusion slot与action/future/value contract，UWM是action/video shared diffusion，都不是当前材料中的RSSM。安全说“能推导并按frozen Dreamer code审计”，不能说“项目使用KL balancing/Dreamer imagination”或“已复现Dreamer收益”。

**追问树**：为什么同时需要h和z？prior为何不能看o_t？ELBO怎样得到？KL对q和p分别做什么？α=0.8是哪一代？V3为何拆dyn/rep并设free bits？clipped KL恒为1说明什么？previous action为何易错一位？start来自posterior是否仍叫imagination？如何证明未来token没泄漏？posterior rollout与prior rollout怎样比较？

**易错点**：把posterior/prior叫encoder/decoder；写成p(z_t|o_t)而忽略h/action；把V2 α=0.8当V3 config；认为KL越小越好；只记clipped loss；imagination每步喂真实帧；action错位/reset跨episode；把categorical latent当所有RSSM定义；把actor/critic结果当RSSM正确性。

**危险答案**：说“posterior和prior完全一样”“DreamerV3就是α=0.8 KL balancing”“free bits会消除collapse”“imagination可以用未来图像纠偏”“reconstruction好说明prior可靠”“WAM/UWM用了RSSM”“公开Dreamer机制就是我的项目实现”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-012 Source Freeze](../sources/vol_04_wm012_rssm_dreamer_posterior_prior_kl_imagination_source_freeze.html)：RSSM/ELBO/KL/imagination 推导与 frozen-code mapping。
2. Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)；[DreamerV1](https://arxiv.org/abs/1912.01603)。
3. Hafner et al., [DreamerV2](https://arxiv.org/abs/2010.02193)；[DreamerV3](https://arxiv.org/abs/2301.04104)。
4. `danijar/dreamerv3@e3f0224` frozen reimplementation：`rssm.py`、`agent.py`、`configs.yaml`。
5. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-013`，不创建 `coaching_state.md`。
