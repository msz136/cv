# VOL 04 WM-027 Source Freeze：Auxiliary Negative Transfer 与 Gradient Conflict

> 审计日期：2026-07-18  
> 状态：source_frozen / VLA-WM-027 / knowledge_synced / card_synced / WARN  
> 覆盖题目：VLA-WM-027  
> 本轮边界：冻结 negative transfer 的可证伪定义、shared-gradient 诊断、PCGrad 与 GradNorm 的公式和限制；不声称某次负 cosine 已证明用户 WAM 负迁移，也不声称 gradient surgery 已在本地执行或改善闭环。

## 1. 结论先行

1. **负迁移是 matched outcome，不是一个 gradient 图。**只有在同初始化、同数据/算力、同 checkpoint 选择和同评测协议下，加入 world/value auxiliary 后，action 主任务或 closed-loop utility 相对 action-only 稳定变差，才能确认负迁移。
2. **gradient conflict 是局部优化诊断。**PCGrad 将两个梯度的负 cosine 定义为 conflict；它描述某个模型状态、batch、参数子集上的一阶方向，不等价于跨 seed 的泛化或闭环退化。[S1]
3. **先排 contract bug，再做 gradient surgery。**错 label、routing/slot/mask、empty denominator、terminal padding、normalizer、role/domain imbalance 都能制造真实退化或伪 conflict；这些问题不能靠 PCGrad/GradNorm 修好。
4. **PCGrad 管方向，GradNorm 管尺度与训练速率。**PCGrad 对负内积做投影；GradNorm 动态学习 loss weight，使共享层梯度向按相对训练速率设定的目标 norm 靠近。GradNorm 不直接消除负 cosine，PCGrad 不自动平衡长期训练速率。[S1][S3]
5. **WAM 本地仍缺关键证据。**当前 inventory 没有 exact local config/checkpoint、per-role gradient trace、matched action-only/+world/+value/all、跨 seed closed-loop episodes 和 ownership；因此 WM-027 只能提供方法与补证据合同。[S6]

## 2. 来源冻结

| ID | 来源 | 冻结版本 | 可支持 | 不能支持 | 状态 |
| --- | --- | --- | --- | --- | --- |
| S1 | Yu et al., *Gradient Surgery for Multi-Task Learning* | arXiv:2001.06782v4，2020-12-22；PDF SHA-256 `4b960b81a001f376e8cb551c61c5578129dd99a9d1ff147be5ea56b9e578cbdf` | negative cosine 的 conflict 定义、tragic triad、PCGrad 投影、随机 task order、局部理论条件与实验边界 | 任意负 cosine 都会导致负迁移；PCGrad 对 WAM 必然有效 | primary / checked |
| S2 | `tianheyu927/PCGrad` official TensorFlow implementation | commit `c5fbd7c856526373828074f06875230f7f3ee79e`；`PCGrad_tf.py` SHA-256 `1bd41ed5b6ed0cb745f2b2d7892336acb318323f057c29f077be4c6ce6a4d179` | per-task gradient、负投影系数和 projected-gradient sum 的实现映射 | 生产可用性、AMP/DDP/FSDP、WAM 集成或本地执行结果 | official-code / checked with boundary |
| S3 | Chen et al., *GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks* | arXiv:1711.02257v4，2018-06-12；PDF SHA-256 `e72930c1f875396f16955748e5af9f2b14c9365c50c1e055cbc36612f326a726` | shared-layer gradient norm、relative inverse training rate、target norm、weight update/renormalization | 解决方向冲突、自动识别坏任务、WAM 必然收益 | primary / checked |
| S4 | WM-026 Source Freeze / Knowledge | 本地 canonical + review | auxiliary 可能帮助的机制、matched six-arm ablation、gradient 只是诊断 | WM-026 的机制假设是本地因果结果 | supporting / WARN |
| S5 | WM-025 Cosmos/WAM Slot / Mask / Loss | frozen Cosmos paper/code audit | unified EDM target、role routing、condition/target/metric mask、component metric 与 training loss 边界 | 可直接从日志 action/future/value L1 得到 exact per-objective training gradient | primary + official-code audit / WARN |
| S6 | WAM Claim–Evidence Inventory | 2026-07-18 | 本地 diagnostic artifact、缺失的 checkpoint/gradient/paired ablation/ownership 和安全表达 | 历史 MSE、success、0-success、root cause 或 gradient conflict 已核实 | local-evidence / WARN |

## 3. 两个概念必须分开

### 3.1 Gradient conflict：某一步的一阶几何

对 action 主任务与一个 auxiliary，在共享参数子集 \(\theta_s\) 上：

\[
g_a=\nabla_{\theta_s}\mathcal L_a,\qquad
g_u=\nabla_{\theta_s}\mathcal L_u,
\]

\[
c_{a,u}=
\frac{g_a^\top g_u}
{\lVert g_a\rVert_2\lVert g_u\rVert_2+\epsilon}.
\]

变量解释：\(\mathcal L_a\) 是 exact action-relevant training objective，\(\mathcal L_u\) 是 world 或 value objective；\(c_{a,u}<0\) 是 PCGrad 意义下的局部 conflict。实现中必须记录参数子集、batch/role、loss reduction、valid target 数和 AMP/DDP 状态；zero gradient 应记为 `NA`，不能伪装成 cosine 0。

令实际联合更新方向为

\[
g_{\mathrm{joint}}=g_a+\lambda_w g_w+\lambda_v g_v.
\]

一次梯度下降对 action loss 的一阶变化为：

\[
\Delta\mathcal L_a
\approx -\eta\,g_a^\top g_{\mathrm{joint}}.
\]

变量解释：\(\eta\) 是学习率。若 \(g_a^\top g_{\mathrm{joint}}<0\)，该步在一阶近似下会增加 action loss，比单独看任意一对 cosine 更直接；但高阶曲率、stochastic gradient、后续表示学习和泛化仍可能改变最终结果。[S1]

### 3.2 Negative transfer：matched 主任务结果

令 \(U\) 是“越高越好”的主任务 utility，例如固定协议下的 per-task success 或把 action error 取负后的 utility：

\[
\Delta U=U_{\mathrm{aux}}-U_{\mathrm{action\text{-}only}}.
\]

变量解释：只有当训练资源、数据身份、seed 计划、checkpoint selection 和 eval protocol 匹配，且 \(\Delta U<0\) 在跨 seed / paired episode 的不确定性分析下稳定存在，才称 confirmed negative transfer。单次 loss spike、单层负 cosine 或一个任务下降都只产生假设。

## 4. World/Value Auxiliary 负迁移的七类来源

| 来源 | 机制 | 可见症状 | 优先检查 |
| --- | --- | --- | --- |
| label / semantics | future 目标与控制无关；value return、timeout 或 success 语义错 | auxiliary loss 降，rank/action/closed-loop 退化 | label audit、action sensitivity、calibration |
| routing / mask | role、slot、condition mask、target mask 或 denominator 错 | 某 role zero/huge grad；padding 段异常 | role matrix、non-zero grad、empty-mask fail-fast |
| role / domain imbalance | rollout auxiliary 数量、状态分布或 embodiment 压过 demo | action update 占比下降；per-source regression | effective token/update count、source holdout |
| gradient-scale domination | \(\lambda_u\lVert g_u\rVert\gg\lVert g_a\rVert\) | total loss 看似正常，action 学习停滞 | norm ratio、weight sweep、GradNorm-style rate |
| directional conflict | \(g_a^\top g_u<0\) 且频繁影响 joint update | action loss 在 auxiliary update 后上升 | layer/role conflict matrix、PCGrad A/B |
| capacity competition | world pixel detail/value shortcut 占用 shared trunk | auxiliary 好、action probe/闭环差 | head-only、stop-gradient、width/freeze control |
| padding / system artifact | terminal repeat、normalizer、AMP scale、grad clip、DDP reduction 失真 | 尾部/某 rank/某 dtype 冲突集中 | valid-step A/B、unscale、pre/post clip、global stats |

负 cosine 也可能只是不同数据分布：若 action、world、value 来自不同 routed samples，两个 gradient 不一定在同一 observation 上可比。应同时报告“matched-state probe”和“真实 routed schedule”的统计，不把 domain shift 简化成纯优化冲突。

## 5. Gradient 诊断合同

### 5.1 最小指标

对每个 shared layer \(\ell\) 和 role pair \((i,j)\)：

\[
c_{ij}^{(\ell)}=
\frac{g_i^{(\ell)\top}g_j^{(\ell)}}
{\lVert g_i^{(\ell)}\rVert\lVert g_j^{(\ell)}\rVert+\epsilon},
\quad
\rho_{u/a}^{(\ell)}=
\frac{\lVert\lambda_u g_u^{(\ell)}\rVert}
{\lVert g_a^{(\ell)}\rVert+\epsilon}.
\]

变量解释：\(c\) 看方向，\(\rho\) 看辅助梯度是否在尺度上淹没 action。不要只报全模型平均；至少保存 shared trunk、modality/slot projection 和 task-specific head 的分布，因为聚合值会掩盖层间符号反转。

每个 window 同时记录：

- conflict rate \(P(c<0)\)、cosine 分位数和连续冲突时长；
- per-role valid target、sample/token/update count 与 loss weight；
- raw norm、weighted norm、joint-update alignment；
- action loss/metric 的 next-step change、EMA 和 checkpoint-level outcome；
- pre-clip 与 post-clip，AMP unscale 后统计；DDP/FSDP 下用全局一致的 per-role gradient 或 exact sharded dot/norm，不平均各 rank cosine。

### 5.2 Cosmos/WAM 特殊边界

Cosmos/WAM frozen contract 的主反向项是 unified noise-weighted latent EDM loss；action/future/value component L1/MSE 是日志 metric，不天然等于三条可分离 training gradient。[S5] 若要得到 per-role/per-target gradient，必须基于 exact target mask、role-conditioned training loss 或重算的 masked EDM loss；不能对 component metric 反向后称“官方 objective gradient”。

## 6. PCGrad：方向冲突的投影

PCGrad 对 task \(i\) 的梯度按随机 task order 检查其他梯度；若
\(g_i^{\mathrm{PC}\top}g_j<0\)，则：[S1]

\[
g_i^{\mathrm{PC}}
\leftarrow
g_i^{\mathrm{PC}}
-\frac{g_i^{\mathrm{PC}\top}g_j}
{\lVert g_j\rVert_2^2}
g_j.
\]

变量解释：该投影去掉 \(g_i^{\mathrm{PC}}\) 在 \(g_j\) 上的冲突分量，使当前 pair 的内积归零；最后对 projected task gradients 求和更新。作者实现按 per-task gradient flatten、投影、unpack、sum 映射该公式。[S2]

适用限制：

1. 需要 per-task backward/gradient，增加显存、通信与训练时间；多任务时顺序会影响有限步结果，论文使用随机顺序使其在期望上对称。[S1]
2. 它只处理负方向，不修 label、routing、domain、capacity 或 calibration；也不证明被投影后的方向能改善闭环。
3. 论文理论结果依赖局部条件；“tragic triad”还包含高正曲率与 gradient magnitude 差异，不能把任何负 cosine 都解释成灾难。[S1]
4. action 是唯一主任务时，可以设计“只投影 auxiliary、保护 action”的非对称变体；这是任务优先级设计，不是原始 PCGrad 的无条件结论，必须单独做 A/B。

## 7. GradNorm：尺度与相对训练速率

对任务 \(i\) 的 weighted loss \(w_i(t)L_i(t)\)，在选定共享参数 \(W\) 上：[S3]

\[
G_W^{(i)}(t)=
\left\lVert\nabla_W\,w_i(t)L_i(t)\right\rVert_2,
\quad
\widetilde L_i(t)=\frac{L_i(t)}{L_i(0)},
\]

\[
r_i(t)=
\frac{\widetilde L_i(t)}
{E_{\mathrm{task}}[\widetilde L_i(t)]},
\quad
G_i^*(t)=\overline G_W(t)[r_i(t)]^\alpha.
\]

变量解释：\(G_W^{(i)}\) 是 task gradient norm，\(r_i>1\) 表示该任务相对学得慢，\(\alpha\) 控制拉回共同训练速率的强度。GradNorm 用

\[
\mathcal L_{\mathrm{grad}}
=\sum_i\left|G_W^{(i)}(t)-G_i^*(t)\right|_1
\]

更新 \(w_i\)，target 在该更新中视为常量；每步再归一化使 \(\sum_iw_i=T\)，从而与全局 learning rate 解耦。[S3]

适用限制：GradNorm 不看 cosine，不能直接消除方向冲突；\(L_i(0)\) 对初始化敏感，论文建议必要时用理论初始 loss；高 \(\alpha\) 可能持续放大噪声大、不可学或错误标注的任务。对 sparse routed roles、empty mask 和不同 cadence，必须先定义可比的 loss/EMA 与有效更新单位。

## 8. 处置顺序与 matched 验证

1. **确认退化**：action-only 与 auxiliary arm 做同数据、同 compute、同 seed 计划、同 checkpoint rule 的 paired comparison。
2. **修 contract**：先查 label、role、slot、condition/target mask、valid count、padding、normalizer 和 protocol。
3. **再改共享方式**：降低/调度 weight，改变 role ratio，stop-gradient、head-only、分层共享或增加 capacity。
4. **最后做优化器干预**：方向冲突稳定存在时试 PCGrad；尺度/训练速率失衡时试 GradNorm；若组合使用，冻结运算顺序并记录 surgery 前后统计。
5. **回到主任务**：至少报告 action proxy、world/value quality、per-task closed-loop、paired episode、seed/CI 和 first-failure；只有主任务稳定改善才能说 mitigation 有效。

## 9. WAM 真实性边界

WAM inventory 当前的 CoffeePressButton base/trained trace 只支持单 episode 接口/失败诊断；checkpoint binary、完整 denominator、target metric、gradient trace、matched objective ablation 和 ownership 仍缺。现有 action 几何差异和单样本 future PSNR/SSIM 不能证明 gradient conflict 或负迁移。[S6]

安全口径：**“我会先用 exact training loss 做逐层、逐角色 gradient audit，再用 matched action-only/+world/+value/all 与闭环 episode 判断是否负迁移；当前本地证据尚不能确认根因。”**

## 10. 下一入口

本节点把“诊断与优化器干预”冻结完成。下一 bounded slice 是 `VLA-WM-028`：sample routing、slot mask 与 loss weight 如何在数据合同层避免 action/world/value 互相污染；它应复用本页的 contract-first 结论，而不是重复 PCGrad/GradNorm。

## 参考文献（References）

1. Tianhe Yu et al., [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782v4), ICLR 2020。
2. Tianhe Yu et al., [`tianheyu927/PCGrad@c5fbd7c`](https://github.com/tianheyu927/PCGrad/tree/c5fbd7c856526373828074f06875230f7f3ee79e)，official TensorFlow implementation。
3. Zhao Chen et al., [GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks](https://arxiv.org/abs/1711.02257v4), ICML 2018。
4. [WM-026 World/Value Auxiliary Source Freeze](vol_04_wm026_world_value_auxiliary_action_imitation_source_freeze.html)。
5. [WM-025 Cosmos/WAM Slot / Mask / Loss](vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。
6. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。

