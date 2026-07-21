# VOL 04 VLA-WM-037 原子题卡：Adaptation Method Selection

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-037  
> 难度：L3 1 题  
> 优先级：P1  
> 练习状态：unseen  
> 前置：[WM-037 Knowledge](../knowledge/vol_04_world_model_sim2real_wm037_adaptation_method_selection.html)；来源边界见 [WM-037 Source Freeze](../sources/vol_04_wm037_adaptation_method_selection_source_freeze.html)。

## residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-037</b> · residual policy、online adaptation、test-time system ID 与 data aggregation 如何选择？</summary>

**面试意图**：判断你能否按更新对象、时间尺度、data/actuation authority 与 safety gate 区分 residual、OSI/RMA、SimOpt、DAgger 和在线改权重，而不是把所有方法统称“在线微调”。

**30 秒回答**：先明确更新对象和权限。有可靠base且误差局部，用限幅residual；参数可辨识用OSI，参数难辨但history有信息用RMA latent；少量安全real轨迹调sim分布用SimOpt；expert能标访问状态用DAgger。先shadow再有限接管，记录数据预算、drift和rollback。

**机制展开（约 2 分钟）**：Residual叠加base action，必须闭合frame/unit/timing并记录norm、clip、fallback。OSI从history估物理参数；RMA估task-relevant latent，二者可固定weights，不等于在线训练。SimOpt按real/sim轨迹差异在outer loop更新sim参数分布；DAgger执行当前/混合policy、由expert标访问状态、聚合后训练下一版。直接改weights需可信reward/label、replay、holdout、canary和rollback。固定checkpoint、协议与real/expert预算比较on/off、oracle、stale/OOD和over-update。

**诊断 / 证据**：保存 base/adapter/residual/policy version，history window/timestamp/reset/stale，\(\hat\mu/\hat z\) 与 OOD，base/raw residual/final action，SimOpt old/new distribution、cost/KL，DAgger state/expert label/dataset lineage，以及 real steps、expert queries、interventions、fallback、incident 和 rollback。按 mechanism-read→offline replay→sim matched→real shadow→limited authority→protocol-complete real 建证据阶梯。

**项目挂钩**：UWM 证据是 offline finetune、sim rollout 与协议；OpenPiVLA 只有 action/controller/rollout partial provenance；OPD 的 online student-rollout 是 token-space teacher distillation，不是 robot-state DAgger。当前没有 residual/OSI/RMA/SimOpt、真机 expert-intervention 或 rollback bundle。安全说“能设计 adaptation gate”，不能说“项目已完成真机在线适配”。

**追问树**：test-time SysID 会改weights吗？explicit parameter与latent adaptation区别？history不可辨怎么办？RMA为何需要privileged teacher？residual为何可能破坏base？SimOpt与system ID区别？DAgger为何要expert标learner state？失败轨迹没有expert action能训练吗？怎样比较不同real-data预算？shadow、limited authority、fallback、rollback如何设计？OPD online与robot online有何不同？

**易错点**：把online都叫微调；有base就无限叠residual；忽略frame/unit/timing；把\(\hat\mu\)当真值；直接照搬RMA频率；SimOpt同时换policy/controller；DAgger只追加失败action；不记expert query/intervention；不同real-step预算直接比success；无shadow/rollback；把offline finetune、token rollout或sim rollout写成真机adaptation。

**危险答案**：说“OSI就是在线训练网络”“RMA能精确恢复物理参数”“residual一定保留base稳定性”“SimOpt找到真实唯一参数”“把失败轨迹都加回去就是DAgger”“online fine-tune一定比固定policy强”“UWM/OPD已经证明我做过真机在线适配”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-037 Source Freeze](../sources/vol_04_wm037_adaptation_method_selection_source_freeze.html)：更新对象、authority、时间尺度、matched gates 与项目边界。
2. Johannink et al., [Residual RL](https://arxiv.org/abs/1812.03201v2)；Yu et al., [UP-OSI](https://arxiv.org/abs/1702.02453v3)。
3. Kumar et al., [RMA](https://arxiv.org/abs/2107.04034v1)；Chebotar et al., [SimOpt](https://arxiv.org/abs/1810.05687v4)。
4. Ross et al., [DAgger](https://proceedings.mlr.press/v15/ross11a.html)。
5. [Evidence Manifest](../evidence/evidence_manifest.html) 与 [OPD/UWM/OpenPiVLA inventories](../evidence/projects/opd_claim_evidence_inventory.html)。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-038`，不提前生成其他卷节点，不创建 `coaching_state.md`。
