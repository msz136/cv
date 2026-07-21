# VOL 04 VLA-WM-033 原子题卡：Dynamics Randomization 与 System Identification

> 状态：drafted / card_1_of_1 / WARN  
> 更新日期：2026-07-18  
> 覆盖范围：VLA-WM-033  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：unseen  
> 前置：[WM-033 Knowledge](../knowledge/vol_04_world_model_sim2real_wm033_dynamics_randomization_system_identification.html)；来源边界见 [WM-033 Source Freeze](../sources/vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)。

## dynamics randomization 与 system identification 如何互补，参数范围怎样确定？

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-WM-033</b> · dynamics randomization 与 system identification 如何互补，参数范围怎样确定？</summary>

**面试意图**：判断你能否把“随机几个物理参数”升级为 measurement/SysID、identifiability、calibrated distribution、correlation/cadence、matched transfer 与 truth boundary 的完整合同。

**30 秒回答**：SysID用测量和激励轨迹校准nominal dynamics并给残差区间；DR围绕中心覆盖测量误差、设备差异、漂移和未建模项。Range记录单位、来源、相关性、采样频率与有效性，不抄论文百分比。用baseline、SysID-only、DR-only、combined、overwide对照，再以real replay/闭环决定扩展或回滚。

**机制展开（约 2 分钟）**：先闭合action/controller/timestamp。可测参数做excitation、multi-start fit、held-out residual/bootstrap；难辨识组保留equivalence set，不伪造真值。按posterior、population、drift、model residual构造bounded/log-space分布，保持相关性并区分cadence。记录draw/rejection；固定data/compute/init/controller/protocol比较五arms，分sim、holdout、real报first failure。SimOpt需安全real rollout，behavior match不是exact SysID。

**诊断 / 证据**：检查 parameter manifest 的 name/unit/site/nominal/range/distribution/source/correlation/cadence/validity；检查 excitation coverage、train/held-out residual、sensitivity、bootstrap、parameter correlation 和 multi-start。保存 sampler seeds、draws、rejection reason、boundary samples。Matched arms 统一 checkpoint lineage、task set、controller、success predicate、rollout count；分 nominal/stress/real 报 tracking、return、success/CI、first failure 和 safety events。

**项目挂钩**：当前 evidence 没有 parameter manifest、real excitation trace、fit/identifiability report、sampler audit、SysID-only/DR-only/combined/overwide arms、真机闭环和 ownership。安全说“能设计 calibrated DR/SysID audit”，不能把 simulator config、论文 range、action/latency 字段或 randomized-sim score 写成个人 Sim2Real 成果。

**追问树**：哪些参数先测、哪些拟合、哪些随机？为什么只做 SysID 不够？为什么 DR 不能越宽越好？正参数怎么采样？mass 和 inertia 为什么不能独立乱采？episode-level 与 step-level 有何区别？激励不足怎样发现？fit 好为何参数仍可能错？UP-OSI 与 recurrent implicit SysID 差别？SimOpt 学的是参数真值还是行为匹配分布？怎样证明 combined 比单方法强？没有真机 authority 怎么回答？

**易错点**：复制论文 ±x%；把 fit loss 小当参数真；所有参数独立 uniform；每 step 改 mass；不记 unit/site/cadence；忽略 controller/timestamp；只测 nominal sim；没有 DR-only/SysID-only 对照；把 stress 与 nominal 混报；把 SimOpt 当 exact SysID；没有安全 gate 就收集 real rollout。

**危险答案**：说“SysID 和 DR 二选一”“随机越宽越鲁棒”“95 个参数是标准配置”“轨迹对齐就得到真实物理参数”“有 randomization YAML 就算完成 Sim2Real”“当前项目已通过 SysID+DR 提升真机成功率”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-033 Source Freeze](../sources/vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)：SysID/DR 互补、range provenance、identifiability、correlation/cadence、matched arms 与项目边界。
2. Tan et al., [*Sim-to-Real Agile Locomotion*](https://arxiv.org/abs/1804.10332v2)；Peng et al., [*Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3)。
3. Yu et al., [*Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3)。
4. Chebotar et al., [*SimOpt*](https://arxiv.org/abs/1810.05687v4)；[Evidence Manifest](../evidence/evidence_manifest.html)。

## 下一步

保持 `unseen`，直到候选人完成真实口述。下一 bounded slice 只做 `VLA-WM-034`，不批量生成 WM-034..038，不创建 `coaching_state.md`。
