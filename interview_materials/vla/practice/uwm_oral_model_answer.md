# PROJ-UWM-001 证据约束下的示范回答

> 状态：`model_answer / evidence_bounded / not_candidate_transcript / unseen`  
> 更新日期：2026-07-21  
> 题目：如何介绍 UWM/LIBERO 项目，并解释协议冲突、RoboCasa actionheadfix 与闭环 0-success？

## 1. 项目定位

这不是“我提出了 UWM 新架构”的故事。最可信的定位是：围绕 UWM 从 LIBERO finetune 到闭环 rollout 的协议迁移、数据管线诊断，以及跨到 RoboCasa 时 action/state/normalizer/execution contract 的失败分析。

回答结构固定为：目标与职责 → 可核验链路 → 一个最有价值的 bad case → 结果证据层级 → 未闭合项。不要先报 `0.744`，也不要把 RoboCasa 的训练 loss 下降说成性能提升。

## 2. 30 秒版本

> 我主要做 UWM 从训练到闭环评估的协议工程：在 C500/MACA 上迁移 LIBERO-90 到多个 LIBERO-10 task 的 finetune/rollout，固定 checkpoint、normalizer、init、horizon、rollout 数和 success predicate，并用 DataLoader-only A/B 定位 zarr 随机读取的周期性等待。LIBERO `186/250` 仍是用户确认summary；RoboCasa则有一条可重算的actionheadfix 30-epoch run：8卡完成3930 steps，同checkpoint的八组54-scenario rollout都无env error，但只有0–2 success，full-h4为`0/54`。所以我讲train-to-closed-loop failure，不称benchmark完成。

## 3. 2 分钟版本

> 项目最初是把 UWM 官方 `libero_90.pt` 迁到 RoboCasa，后来因为 action order、state/prompt、normalizer 和 eval harness 都没有闭合，先回到 UWM/LIBERO 官方路线建立训练—评估基线。我的工作重心是把结果绑定到 `(checkpoint, normalizer, init, seed, warmup, horizon, rollout count, success predicate, scorer, denominator)`，而不是只看一个 success rate。
>
> 在 LIBERO 路线，本地脚本支持五个 LIBERO-10 task、`pruned_init`、5-step zero-action warmup、50 rollout/task 和 8-shard 聚合。`186/250=0.744` 是用户确认的远端 fixed-init summary，本地没有对应 checkpoint、normalizer hash 和 250 条 episode JSONL；`232/250=0.928` 是 `env.seed+reset` 的另一套协议。论文 Table II 还使用 OOD initialization、object shift、背景移除和三个 finetune seeds，所以这三个数字不能直接横比。DataLoader-only A/B 中，preload+infinite sampler 把 p95 wait 从约 `13.86s` 降到约 `0.19s`，它支持数据等待诊断，但还不是 full GPU throughput 提升。
>
> RoboCasa 方向我保留了 run-specific 失败链。actionheadfix 从 `libero_90.pt` partial load：478个target keys中446 matched，7D→12D action encoder/decoder的8个key重置，并加入task/prompt/16D-state/right-view条件。该30-epoch run的打印action loss从`2.4300`降到`0.07689`，但`val_ratio=0`；八份raw rollout JSON共享同一18 task×3 scenario、checkpoint和normalizer，full h1/h2/h4/h5/h8只有`2/1/0/1/1` success，h4虽有`45/54` robot-env contact仍是`0/54`。因此结论不是“修复成功”，而是训练fit没有转化为稳定闭环；下一步要沿同一failure case追 expert→x0→sampled→converted→executed action，而不是继续只压训练loss。

## 4. RoboCasa actionheadfix：90 秒专项版本

> 旧路线的问题是 RoboCasa official12 与 `libero_90.pt` 的7D action head、state和多视角条件不一致。新run用shape-compatible partial load保留446个key，重置8个action encoder/decoder key，训练12D reordered action，并加入task、prompt、16D state和right view；同一个models.pt/normalizer随后进入五组horizon和三组input ablation。
>
> `train.out` 可直接重算41个打印点：step0→3929的total/action/raw-action loss为`3.3257→0.25385`、`2.4300→0.07689`、`0.9986→0.03043`，8个rank正常退出。但没有validation。八个setting都使用相同54 scenario且env errors为0，full h1/h2/h4/h5/h8为`2/1/0/1/1`，no-prompt/no-right/no-state h5为`2/2/1`；成功只集中在Kettle或Microwave。训练稳定只是必要条件，1个episode差异也不能支持ablation因果。
>
> 我还把 execution 错误与策略失败分开：native direct 是 `0/6`、env errors 0，属于有效但失败的 rollout；strict OpenPI-style `convert_action` 是 `0/6`、env errors 6，全部在 step 0 因 `expected 12, got 5` 失败，不能算模型 0-success。GT dict-to-native bridge 的最大绝对差为 0，只说明桥接数值一致，不证明模型动作正确。安全结论是“接口错误已定位，策略闭环仍未解决”。

## 5. Evidence Contract

| Claim | 证据 | 等级 | 当前能否强说 |
| --- | --- | --- | --- |
| fixed-pruned-init、warmup、rollout、success tuple | [UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与本地 evaluator/launcher | `local-direct / C1-C2` | 可讲协议迁移与设计取舍 |
| `186/250=0.744` | user-confirmed remote final summary | `user-confirmed / raw-missing` | 只能带 provenance 报告 |
| `232/250=0.928` | reset-style report context | `protocol-diagnostic` | 不能讲模型 uplift |
| Table II 约 0.79 | [Benchmark Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html) | `upstream-verified / non-comparable` | 不能说严格只差 4.6pp |
| actionheadfix partial init/x0/group metrics | [Transfer Evidence Freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html) | `local-report / C1-C2` | 可讲训练与诊断机制 |
| 30-epoch 8×54 raw sweep；h4 `0/54`、contact `45/54` | [ActionHeadFix P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) | `remote-snapshot-raw / checkpoint-unverified` | 可讲run-specific失败链，不称benchmark完成 |
| DataLoader p95 `13.86s→0.19s` | DataLoader-only benchmark/report | `smoke-bounded / C2` | 可讲 wait first-divergence，不报 GPU uplift |
| 个人 ownership | [UWM Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html) | `candidate-confirmation-pending` | 只能按已确认文件/角色回答 |

## 6. 关键问题三档回答

### “训练指标都改善了，为什么还是 0/54？”

**危险回答**：loss 已经很低，应该只是 RoboCasa 环境太难或者算力数值误差。

**可过回答**：teacher-forced 指标和闭环成功率不等价，模型可能有 distribution shift 或 contact 问题。

**强回答**：

> 我先固定一条run。训练层，8卡3930 steps正常完成，打印action loss从`2.4300`降到`0.07689`，但没有validation；closed-loop层，同checkpoint和normalizer的八组raw JSON都是54个相同scenario、env errors为0，却只有0–2 success，h4 `0/54`且`45/54`有robot-env contact。接触不等于任务谓词完成，说明first divergence在训练fit到闭环执行之间。下一步沿同一h4 failure比较expert、model x0、sampled 12D、converted/executed action和env state，而不是继续只堆epoch。

需要补的证据：produced checkpoint binary/hash和fresh-load、完整train JSONL、env/scorer revision、failure video，以及跨checkpoint seed的同54-scenario paired rerun。

### “actionheadfix 算修复成功吗？”

**危险回答**：成功，loss 从 95 降到了 0.22。

**可过回答**：训练侧修复成功，但闭环还没成功。

**强回答**：

> 我只把它称为“训练侧假设被部分验证”。checkpoint partial init、x0 loss 和 teacher-forced 指标证明 12D head 不再完全从坏初始化开始，且模型能拟合一部分 action 分布；但闭环 success 没改善，所以不能写性能修复。这个区分能避免把优化器收敛、open-loop action fit 和 environment success 混成一个指标。

需要补的证据：同 protocol 的 before/after checkpoint、teacher-forced、single-task closed-loop 与 54-scenario paired summary。

### “0.744 能写进简历吗？”

**危险回答**：可以，我复现了官方 UWM，成功率 74.4%。

**可过回答**：可以写，但需要说明是远端结果。

**强回答**：

> 目前更适合在面试中带 provenance 讲，不建议作为无条件 C3 bullet。它是用户确认的远端 fixed-init summary，本地缺 checkpoint、normalizer 和 250 episode bundle；同时与 Table II 协议不可比。若写简历，保守表达应是“搭建并对齐 5-task fixed-init rollout 协议，记录用户确认的 186/250 summary，并识别 reset-style 与论文 OOD 协议差异”，而不是“复现官方 74.4%”。

需要补的证据：immutable run bundle、operator/reviewer、same-protocol baseline 和候选人 ownership。

## 7. 高频追问答法

### “0.928 不是更高，所以模型更好吗？”

不一定。reset-style 改变了初始状态分布，可能更容易；它首先说明 protocol sensitivity，而不是模型能力 uplift。要比较模型，必须固定 checkpoint、init distribution、seed、warmup、scorer 和 denominator。

### “0.744 比 0.79 低 4.6pp，能说接近官方吗？”

不能。论文使用 OOD init、object shift、背景设置和多 seed，项目使用 fixed-pruned-init 与另一条 warmup/评测协议；差值没有严格比较意义。

### “DataLoader stall 是不是已经定位根因？”

可以说定位了 DataLoader wait 的 first divergence：preload+infinite 在 DataLoader-only smoke 中把 p95 wait 从约 13.86s 降到约 0.19s。不能说完整训练已提速，需要 matched GPU throughput/memory A/B。

### “convert_action 的 0/6 怎么解释？”

必须先看 invalid policy。strict path 6 条都在 step 0 因维度错误退出，不是六条有效模型失败；native direct 的 `0/6` 才是有效但不成功的 rollout。两者不能混算 success rate。

### “哪些是你做的？”

按 ledger 区分训练迁移、评估协议、数据管线、action adapter、诊断、远端运行、协作和工具辅助。UWM architecture 属于 upstream，Git author 和 report path 都不能替代逐文件角色确认。

## 8. 练习边界

- 这是 model answer，不是候选人的真实 transcript。
- 使用时必须把“我做了什么”替换为本人可确认的 launcher、函数、patch、命令或验收 artifact。
- `0.744` 继续标记 `user-confirmed-remote-final`；actionheadfix `0/54` 标记为 `remote-snapshot-raw / checkpoint-unverified`。
- 真实口述前保持 `PROJ-UWM-001` 为 `unseen`，不创建 `coaching_state.md`。

## References

1. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
2. [UWM/LIBERO P0 Bundle Audit](../evidence/projects/uwm_libero_p0_bundle_audit.html)。
3. [UWM/LIBERO/RoboCasa Transfer Evidence Freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)。
4. [UWM Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html)。
5. [VOL 04 Benchmark Evidence Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
6. [UWM Video/Action Source Audit](../sources/vol_04_uwm_video_action_claim_to_code.html)。
7. [PROJ-UWM-001..004 Atomic Cards](../questions/proj_uwm.html)。
8. [UWM RoboCasa ActionHeadFix 30-Epoch Train-to-Closed-Loop P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)。
