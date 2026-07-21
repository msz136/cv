# VOL 04 VLA-WM-011 原子题卡：Objective Semantics

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-011  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-011 Knowledge](../knowledge/vol_04_world_model_sim2real_wm011_objective_semantics.html)；来源边界见 [WM-011 Source Freeze](../sources/vol_04_wm011_objective_semantics_source_freeze.html)。

## reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么？

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-WM-011</b> · reconstruction、latent dynamics、reward、continuation 与 perceptual loss 分别监督什么？</summary>

**面试意图**：判断你能否从 loss 名称下钻到 prediction/target/time-index/mask/reduction/gradient，区分 observation、prior/posterior、一步 reward、learned discount 与 feature distance，并拒绝从 loss 下降直接外推 policy success。

**30 秒回答**：reconstruction让latent可解码观测；dynamics让action-conditioned prior对齐观测posterior；reward预测一步即时信号；continuation预测是否继续或折扣；perceptual比较深层特征。每项还要闭合时间索引、mask、reduction、权重和梯度路径，loss下降不等于闭环成功。

**机制展开（约 2 分钟）**：重建可用pixel likelihood/MSE，但posterior重建好不证明prior rollout；Dreamer式dyn/rep KL用相反stop-gradient分别训prior和posterior，并受free nats影响。reward不是value/success；continue要区分terminal、timeout与off-by-one。perceptual需固定backbone/layer/normalize/frozen状态，可能忽略接触几何。最终按有效denominator聚合并记录scaled loss与梯度。

**诊断 / 证据**：保存每项prediction/target schema、time index、valid mask、numerator/denominator、raw/reduced/scaled loss、route count、gradient norm/cosine、prior/posterior entropy、free-nats clipping、reward/continue calibration、action-swap、teacher-forced/open-loop horizon curve和closed-loop success。

**项目挂钩**：WAM仅支持upstream action/future/value slot、mask与待补action-only/+world/+value/all设计；历史MSE/成功率已降级。UWM支持action/video shared diffusion与协议材料，但无objective单项消融。安全说“能审计并设计matched arms”，不能说“某项loss已提升74.4%或项目成功率”。

**追问树**：为什么posterior重建好但prior会漂？dyn/rep KL为何要两个stop-gradient方向？free nats做什么？reward和value区别？`is_last`、`is_terminal`、timeout怎么处理？continuation错一位有何后果？LPIPS能否保证接触正确？不同loss scalar能直接比较吗？怎么证明perceptual或reward head真的有用？

**易错点**：把reconstruction等同world model能力；把PlaNet overshooting归给DreamerV3 frozen repo；reward/value/success混用；timeout一律当terminal；忽略mask denominator；只看nominal loss weight；perceptual backbone联合漂移；以loss下降代替matched ablation与closed-loop。

**危险答案**：说“像素越清晰动力学越好”“KL越低越好”“reward head就是value head”“done就是success”“LPIPS高就说明机器人可执行”“所有loss都是MSE所以数值能直接比”“WAM/UWM已证明辅助loss提升成功率”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-011 Source Freeze](../sources/vol_04_wm011_objective_semantics_source_freeze.html)：objective contract、Dreamer frozen code、perceptual primary sources 与项目边界。
2. Hafner et al., [DreamerV3](https://arxiv.org/abs/2301.04104)；`danijar/dreamerv3@e3f0224` frozen reimplementation。
3. Hafner et al., [PlaNet](https://arxiv.org/abs/1811.04551)；Ha & Schmidhuber, [World Models](https://arxiv.org/abs/1803.10122)。
4. Johnson et al., [Perceptual Losses](https://arxiv.org/abs/1603.08155)；Zhang et al., [LPIPS](https://arxiv.org/abs/1801.03924)。
5. [WAM](../evidence/projects/wam_claim_evidence_inventory.html) 与 [UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html) inventories。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-012`，不创建 `coaching_state.md`。
