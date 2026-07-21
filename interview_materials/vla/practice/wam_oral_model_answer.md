# PROJ-WAM-001 证据约束下的示范回答

> 状态：`model_answer / evidence_bounded / not_candidate_transcript / unseen`  
> 更新日期：2026-07-21  
> 题目：如何介绍 Cosmos Policy / WAM 项目，并解释 1 epoch gate、两类训练系统失败与 CoffeePressButton 诊断证据？

## 1. 项目定位

这不是把所有 Cosmos/WAM 日志拼成“一个 1 epoch 结果”的故事。当前需要明确区分两个 run family：第一条是按 Predict2 + T5 + RoboCasa 合同搭建的 8 卡、global batch 128、`9907` steps 单 epoch gate；它先暴露 dataloader 导致的 CPU cgroup OOM，修复后又在 `state_dict(destination=...)` 保存接口处失败。第二条是独立的单卡 GPU7 full10k repro：日志记录 step `10000` loss=`0.0543`、远端 checkpoint 保存成功、`EXIT:0`，随后 CoffeePressButton 1-episode RoboCasa smoke 为 `0/1`。前者不能称完成的 1 epoch checkpoint，后者可以称独立 full10k 训练与最小 eval smoke，但仍不是完整 benchmark 或本地 hash 已核验的最终结果。

回答结构固定为：先拆 run family → 1 epoch gate 的故障链 → full10k 的训练/最小 eval 证据 → 两者的 P0 缺口。CoffeePressButton 的 paired manifest、trace、失败视频和离线 visual proxy 仍是诊断层，不能与单 episode `0/1` 拼成 benchmark uplift。

## 2. 30 秒版本

> 我把两条运行分开讲：8 卡、global batch 128 的 `9907`-step 单 epoch gate 在 step 1903 暴露 `cycle(dataloader)` 的 CPU cgroup OOM，no-cycle 5-step smoke 通过，但正式 run 在 step 1500 的 `state_dict` 签名兼容性处保存失败；另一个独立的单卡 full10k repro 跑到 step 10000，loss 是 `0.0543`，日志有远端 checkpoint saved 和 `EXIT:0`，随后 CoffeePressButton 1-episode smoke 是 `0/1`。所以我能认领两条训练/评测链路与故障边界，但不把它们合成一个 1 epoch benchmark 结果。

## 3. 2 分钟版本

> 我的目标不是跑出一个孤立 loss，而是把 Cosmos Policy 的训练和评估拆成可验收的 run family。8-GPU gate 的合同是每卡 batch 16、global batch 128、`max_steps=9907`，RoboCasa 数据运行时统计为 1,199 个 demo episodes、1,291 个 rollout episodes、343,635 个 rollout steps 和 242 条 command；只有达到 `9907` steps、checkpoint 能保存并重新加载、再进入同协议 eval，才算这条 1 epoch gate 完成。独立的 `cosmos_policy_wam_repro_full10k_20260619` 则是单卡 GPU7、`BATCH_SIZE=1` 的另一条 run，原始日志和 report 记录了 step 10000 loss=`0.0543`、`iter_000010000` 远端保存、`Done with training` 和 `EXIT:0`。
>
> 第一条 save-2k run 在 step 1903 后退出，launcher 是 `EXIT=247`、一个 rank 是 `-9`，没有 GPU OOM 栈，也没有 step-2000 checkpoint；结合 cgroup 记录和内存增长，定位到 `itertools.cycle(dataloader)` 会缓存迭代过的 batch，长跑时持续占用 CPU 内存。修复方式是使用普通 iterator，在 `StopIteration` 时显式重建。8 卡、5 steps、关闭保存的 smoke 返回 `EXIT=0`，这只验证了迭代器修复，不代表完整训练成功。
>
> 修复后的 1 epoch 正式 run 到 step 1500 保存点时又退出：DeepSpeed 按 PyTorch 标准调用 `state_dict(destination=..., prefix=..., keep_vars=...)`，而 Cosmos `DiffusionModel.state_dict()` 不接受这些参数。虽然出现了 `step_001500` 目录，但没有可用权重，不能叫这条 gate 的 checkpoint。与此同时，full10k report 记录 CoffeePressButton、1 episode、`max_steps_override=120` 的 smoke 为 `0/1`，并回传了 eval log 和视频；这证明独立 full10k 的最小闭环链路可运行，但不证明完整 suite，也没有本地 checkpoint binary/hash 或新进程 load parity。我的结论是：1 epoch gate 的 dataloader 与保存接口 first divergence 已定位，独立 full10k 训练与单 episode smoke 已有证据，但两条 run 不能合并成一个最终 uplift。

## 4. CoffeePressButton：另一层诊断证据

> 除训练 gate 外，项目还有一组 CoffeePressButton diagnostic bundle：base/trained manifest、两侧各 300 步的 action trace、失败视频、单样本 future-image PSNR/SSIM proxy 和 checkpoint path bridge。它能验证文件 provenance、trace shape/finite、逐步动作差异和失败样例，但不能证明这次 1 epoch run 有 checkpoint，也不能给出 benchmark success。policy 侧 7D 到 environment 侧 12D 的 MAE/RMSE 是 trace geometry，不是 action-label loss；PSNR/SSIM 是 offline proxy，不是 closed-loop metric；路径字符串相同也不是 binary hash。两层材料可以共同支持“我做了协议审计和失败诊断”，不能拼接为“训练后效果提升”。

## 5. Evidence Contract

| Claim | 证据 | 等级 | 当前口径 |
| --- | --- | --- | --- |
| 8 卡、每卡 16、global batch 128、`max_steps=9907` | [1 Epoch Evidence Freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html) 的 run contract | `local-direct / C1` | 可讲训练合同与完成 gate |
| 数据集运行时统计 | 同页 `dataset_runtime_summary.json` 冻结值 | `local-direct / C1` | 可讲 1,199 demo、1,291 rollout episodes、343,635 steps、242 commands |
| step 1903 后 cgroup CPU OOM | launch/status log、`EXIT=247`、rank `-9` 与 cgroup 诊断 | `local-direct + local-inference / C2` | 可讲定位过程；不要称已完成修复闭环 |
| `cycle(dataloader)` 缓存 batch 与 no-cycle smoke | 根因报告；8 卡 5-step、`SAVE_EVERY=0`、`EXIT=0` | `local-report / C2` | 可讲迭代器假设被 smoke 支持 |
| step 1500 保存签名失败 | DeepSpeed/Cosmos error stack；空的 `step_001500` | `local-direct / C2` | 可讲保存接口 first divergence；不能称 checkpoint |
| step 1900 loss `0.2945` | save-2k 中断前 metric | `local-direct / diagnostic-only` | 只能称中间快照，不能称 final/best/epoch loss |
| 完整 1 epoch、可加载 checkpoint、本轮 eval | 当前不存在 | `C3 / unverified` | 禁止宣称 |
| full10k step 10000 loss `0.0543`、远端 checkpoint saved、CoffeePressButton `0/1` | 独立 `cosmos_wam_repro` run；日志/report 可复核 | `local-report / partial` | 可作为独立训练与最小 eval smoke 证据；不能当作 8-GPU 1 epoch gate 的结果或完整 benchmark |
| official-HF baseline raw `86/120`、trusted `84/118` | [RoboCasa Baseline P0 Audit](../evidence/projects/cosmos_policy_robocasa_baseline_p0_audit.html)：24 task logs、24/24 exit 0、2692 action-debug rows | `remote-artifact-backed / checkpoint-unverified` | 可讲运行与协议审计；禁止归属于 1 epoch/full10k 训练或个人模型 uplift |
| CoffeePressButton trace/video/proxy | [WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html) 与 paired diagnostics | `local-direct / diagnostic-only` | 可讲评测诊断，不讲 uplift |
| 个人 ownership | [WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html) | `candidate-confirmation-pending` | 只能按本人确认的文件、函数、命令和验收动作回答 |

当前 C1/C2 可讲：run contract、数据统计、OOM 分析、no-cycle 修改与 smoke、保存接口定位、full10k 的 step-10000 训练与 `0/1` smoke、诊断 bundle 分层。当前 C3 禁止讲：8-GPU gate 的完整 1 epoch、该 gate 的 final loss、任一 run 的本地 checkpoint binary/hash、完整 suite success、官方 baseline ownership 或训练带来的 uplift。

## 6. 关键问题三档回答

### “你到底有没有完成 1 epoch？”

**危险回答**：完成了，已经跑到 1900 step，loss 也降到 `0.2945`。

**可过回答**：没有完整跑完，但训练主体基本成功，后来只是保存出了问题。

**强回答**：

> 对 8-GPU、global batch 128 的 `9907`-step gate，答案是没有：完成定义是达到 `9907` steps、保存并在新进程加载 checkpoint、再跑固定协议 eval；它在 step 1903 和 step 1500 分别卡在 OOM 与保存接口。另有一条独立的单卡 full10k repro 确实记录了 step 10000、loss=`0.0543`、远端 checkpoint saved、`EXIT:0`，并做了 CoffeePressButton `0/1` smoke，但它不是前一条 gate 的 continuation，也没有本地 binary/hash 与 load parity。因此我能认领两条运行链路的实现/排障边界，不能把 full10k 数字包装成 8-GPU 1 epoch 的最终结果。

需要补的证据：完整 `9907`-step log、checkpoint 文件清单与 SHA-256、新进程 load smoke、run-specific eval bundle。

### “step 1900 loss 0.2945 能不能当最终结果？”

**危险回答**：可以，这是训练最后记录到的 loss，所以就是 final loss。

**可过回答**：它只是中间 loss，但可以大致代表这一轮效果。

**强回答**：

> 不能。它来自 save-2k run 的中断前快照，距离 `9907`-step gate 很远，且没有与它绑定的可加载 checkpoint。它最多证明当时优化过程有一个可观测值；不能叫 epoch loss、best loss，更不能外推 closed-loop success。要成为结果，至少要绑定 step、checkpoint identity、验证集或 rollout protocol 和完整 denominator。

需要补的证据：同 step checkpoint、loss 定义与聚合口径、完整训练曲线、固定协议 eval。

### “OOM 修复算不算训练成功？”

**危险回答**：算，5-step smoke 已经 `EXIT=0`，说明 1 epoch 没问题。

**可过回答**：算修掉了一个 bug，但训练还没有最终完成。

**强回答**：

> 它只算“迭代器修复通过了最小验证”。`cycle(dataloader)` 会保存已经 yield 的 batch 以便之后回放，对大 tensor batch 的长跑会持续占用 CPU 内存；改为普通 iterator 并在 `StopIteration` 时重建后，8 卡 5-step smoke `EXIT=0`，支持根因假设。但 smoke 关闭了保存、步数极短，不能覆盖长时内存、checkpoint 或 `9907`-step 完成条件。后续正式 run 在保存接口失败，正说明一个 gate 通过不等于训练系统成功。

需要补的证据：matched long-run RSS/cgroup memory A/B、完整 gate、save/load 与 eval。

### “为什么没有 checkpoint？”

**危险回答**：目录已经生成了，checkpoint 应该只是还没同步回来。

**可过回答**：保存时接口报错，所以 checkpoint 不完整。

**强回答**：

> 对 8-GPU 1 epoch gate，DeepSpeed 在 step 1500 调用模型的标准 `state_dict(destination, prefix, keep_vars)` 接口，而 Cosmos 的 override 不接受这些关键字，调用在实际写出可用权重前失败；目录存在只证明保存流程开始过。独立 full10k 日志另有 `Saved checkpoint to ...iter_000010000`，但那是远端 path reference，不等于我已在本地拿到 binary 或完成新进程 load parity。修复 gate 仍应让 override 兼容标准签名，然后做 1-step train→save→销毁进程→新进程 load；检查文件非空、参数 key/shape、global step、optimizer/scheduler state 和固定输入前向一致性，再重跑长任务。

需要补的证据：兼容层 diff、save/load smoke log、checkpoint manifest/hash 和 reload forward parity。

### “full10k loss=0.0543 能不能作为最终结果？”

**危险回答**：可以，0.0543 说明模型已经学会了，RoboCasa 只是偶然失败。

**可过回答**：可以作为 full10k 训练结果，但闭环只有一个失败样本。

**强回答**：

> 我会把它限定为独立 full10k run 的 step-10000 training metric。原始日志有 checkpoint saved、`Done with training` 和 `EXIT:0`，report 也有 action/world/value 的 loss breakdown；但 eval 只有 CoffeePressButton 1 episode 的 `0/1`，没有完整 denominator、同 checkpoint 的 raw episode bundle、本地 binary/hash 或 base paired control。因此它能证明训练和最小 eval smoke 链路跑通，不能证明 benchmark 成功或“loss 下降导致 uplift”，更不能替代 8-GPU 1 epoch gate 的 save/load 闭环。

需要补的证据：full10k checkpoint immutable manifest、同 checkpoint 新进程 load parity、固定 task/trial/scorer 的 raw episode JSONL，以及 base/paired control。

### “84/118 是不是你的 1 epoch 结果？”

**危险回答**：是，1 epoch 后 RoboCasa 达到了 84/118。

**可过回答**：不是同一条 run，是官方结果，但可以当作我的 baseline。

**强回答**：

> 不是。它是我按 official-HF checkpoint path 跑并审计的一条独立 24×5 RoboCasa baseline eval：raw logs 重算为 `86/120`；其中 CoffeeServeMug 两个 length=1 success 按当前 artifact policy 排除后是 `84/118=71.19%`。24 条 formal status 都是 `exit_code=0`，24 个 action-debug 文件共 2692 行、shape 都是 `32×7` 且 finite。可以认领的是评测运行、协议固定和日志重算；不能把官方权重训练归到个人，也不能把 71.19% 写成 1 epoch/full10k checkpoint 的成绩或 uplift。当前 bundle 仍缺官方 checkpoint binary/hash、完整 episode JSONL 与 scorer/version，所以我会同时报告 raw/trusted 两个口径和排除规则。

需要补的证据：official checkpoint/stats/T5 的 immutable revision/hash、完整 120 episode JSONL、scorer/invalid policy version、operator/reviewer，以及任何本地训练 checkpoint 与该 baseline 的 matched join key。

### “为什么 fixed batch 能输出负 gripper，TurnOffMicrowave 还是 0/1？”

**危险回答**：训练集没有负样本，或者 action 第 7 维符号反了。

**可过回答**：可能是 gripper collapse，但需要更多 debug。

**强回答**：

> 我把它拆成 fixed-batch gate、closed-loop 和 same-input probe 三层。local negative-only 1k checkpoint 在固定 `32×7` batch 上的 sampled first gripper 是 `-0.8277`，trajectory final clean 是 `-0.8275`，slot-5 roundtrip 与 normalization 也通过；所以基本 action path 可学。进入 TurnOffMicrowave 后，1 episode 是 `0/1`、跑满 500 steps，32 次 query 的第 7 维全部为正，整体 min/max/mean 是 `+0.0646/+0.5614/+0.2205`。
>
> 为找 first divergence，我对齐同一个 initial observation 的三路相机、proprio、T5 和 data-batch hash。official-HF first gripper 是 `-1.0156`，local 是 `+0.1429`；local 换 8 个 seed，first 仍在 `+0.1052..+0.2217`，所以不是单次随机采样。数据侧也不是完全没负向监督：52 个 HDF5、11230 states 的 top-24 eval-like neighbors 中 first-action negative rate 是 `37.5%`。
>
> 更关键的是旧 debug sampler 没显式传 official 的 `num_conditional_frames=5`：缺省条件下同一 HDF5 batch 可全负，补齐 5 frames 后转为全正。corrected single-batch overfit 仍能把 fixed clean/sample 拉到约 `-1.02`，但 exact eval first 仍 `+0.316`，negative-only strong-reg 也没有修复。因此我会说“conditioning contract 差异和 exact-observation transfer gap 已被证据支持，唯一 root cause 与修复效果还没确认”，不会把它包装成已修复的 gripper bug 或 benchmark 成绩。

需要补的证据：显式 5-frame matched training patch、immutable checkpoint/load parity、同 state 的 patch 前后 query trace，以及多 episode 的 scorer/controller/denominator bundle。

### “base_load_summary 有 715 个 key，为什么还不能说 checkpoint 可加载？”

**危险回答**：因为远端文件还没同步回来，应该已经保存了。

**可过回答**：base model 能加载，但训练 checkpoint 的保存失败了。

**强回答**：

> 我把 gate 拆成 base load、短训练、长跑、save、fresh-process reload 和 matched eval。13 个 base-load summary 都指向同一个 HF cache snapshot，`715` keys、missing/unexpected 都是 `0`；fixed-optional/bs8 1-step 和 no-cycle 5-step smoke 也有 `exit=0`。但这些只证明上游 base 初始化和短路径通过，不证明训练产物存在。9907-step save2k 线以 rank `-9`/`EXIT=247` 结束，no-cycle save1500 线在 DeepSpeed 调用 `state_dict(destination=..., prefix=..., keep_vars=...)` 时 TypeError/`EXIT=1`。归档 65 个文件里 checkpoint-like binary 数量是 `0`，也没有 save→销毁进程→fresh load 的 parity artifact，所以我不能把 base-load summary 说成训练 checkpoint 的 load proof。

需要补的证据：`state_dict(destination=None, prefix='', keep_vars=False)` compatibility patch、真实 1-step save/load smoke、checkpoint shard/optimizer/scheduler/global-step manifest 与 SHA，以及固定输入 reload forward parity。

## 7. 面试官追问树

### Root：你做的 1 epoch finetune 结果是什么？

- 若回答“完成了”：要求给出 `9907`-step 终点、checkpoint SHA、reload log 与 run-specific eval；任一缺失即降级为未完成 gate。
- 若回答“到 step 1903”：继续问 `EXIT=247` 与 rank `-9` 如何解释，证据为何指向 cgroup CPU OOM 而不是 GPU OOM。
- 若回答“修复了 OOM”：继续问 `itertools.cycle(dataloader)` 为什么会缓存 batch，5-step smoke 覆盖了什么、没覆盖什么。
- 若回答“保存失败”：继续问 `state_dict(destination=...)` 兼容层如何设计，为什么空目录不是 checkpoint。
- 若回答“full10k loss 0.0543”：要求给出 run name、checkpoint identity、CoffeePressButton denominator 与 eval artifact，禁止把它和 9907-step gate 或官方 baseline 做无 key join。
- 若回答“准备重跑”：继续问 save/load smoke 的最小验收项，以及怎样防止花费 8 卡长跑后才暴露保存错误。
- 若回答“84/118”：要求指出它的 run、checkpoint、协议和 operator，禁止与本轮中间 loss 拼接。
- 若回答“715 keys 说明 checkpoint 没问题”：追问它是 HF base snapshot 还是 produced checkpoint，是否有 save manifest、fresh-process reload 和 matched eval；没有就降级为 base-load evidence。
- 最后追 ownership：谁设计合同、谁改 iterator、谁运行远端 8 卡、谁定位 error stack、谁 review；按 `candidate / operator / reviewer / collaborator / tool / upstream` 分开。

## 8. 高频技术追问答法

### “`cycle(dataloader)` 为什么会缓存 batch？”

`itertools.cycle` 为了在源 iterator 耗尽后重复输出，会把首轮迭代得到的每个对象保存在内部缓存。对 DataLoader 而言，这些对象可能包含大 tensor、worker 返回结构或 pinned-memory 引用；如果一个 epoch 很长，缓存会随已见 batch 数增长。无限训练应重建 iterator，而不是用 `cycle` 保存整轮 batch。

### “怎么验证是 cgroup OOM，不是 GPU OOM？”

看证据链而不是只看进程被杀：是否有 CUDA allocator/OOM traceback；主机或容器的 `memory.current`、`memory.events`、`oom_kill` 是否增长；launcher 的 `EXIT=247` 与 rank `-9` 是否对应 SIGKILL；GPU 显存是否稳定；no-cycle matched smoke/长跑的 CPU RSS 是否停止线性增长。当前材料支持 cgroup CPU OOM 诊断，但完整 matched 长跑 A/B 仍可补强。

### “`EXIT=247` 和 rank `-9` 怎么解释？”

rank `-9` 表示该子进程被 SIGKILL，常见于外部 OOM killer；顶层 `247` 是 launcher 汇总后的退出码，不能单独当根因。需要把它与 cgroup memory event、无 Python/CUDA OOM 栈、其他 ranks 被连带终止和时间线对齐。

### “保存接口应该怎么修？”

让 Cosmos 的 override 兼容 PyTorch 标准签名 `state_dict(destination=None, prefix='', keep_vars=False)`，并把参数正确传给父类/实际 state dict 生成逻辑；不要只吞掉参数。还要覆盖 DeepSpeed 所需的 optimizer、scheduler、global step 和分片元数据。这个方案目前是下一步，不应说成已实现。

### “怎样设计 save/load smoke？”

用真实 DeepSpeed 配置和最小 batch 跑 1 step，在计划保存路径写 checkpoint；进程完全退出后从空的新进程加载，核对文件清单与 hash、参数 key/shape、global step、optimizer/scheduler state，并在固定随机种子和固定输入上比较 reload 前后输出。多卡时还要检查所有 rank barrier 与 shard completeness。

## 9. 练习边界

- 这是 model answer，不是候选人的真实 transcript；题卡继续保持 `unseen`。
- “我搭建/定位/修改/运行”必须替换为候选人可确认的文件、函数、命令、operator/reviewer 和验收 artifact。
- 上游 Predict2/WAM 机制、官方 HF baseline、远端路径与 Git author 不能自动升级为个人 ownership。
- 新增 checkpoint 或 eval 证据时，先更新 evidence freeze、inventory 与 ownership ledger，再升级回答。
- 真实口述前不创建 `coaching_state.md`。

## References

1. [Cosmos Policy 1 Epoch Evidence Freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)。
2. [WAM 1 epoch / full10k Run Reconciliation](../sources/vol_04_cosmos_policy_wam_full10k_run_reconciliation.html)。
3. [Cosmos Policy RoboCasa Official-HF Baseline P0 Audit](../evidence/projects/cosmos_policy_robocasa_baseline_p0_audit.html)。
4. [Cosmos Policy / WAM Claim-to-Code Audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
5. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html)。
7. [WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
8. [WM-019 Action-Trace Diagnostic](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html)。
9. [WM-019 Future-Metric Diagnostic](../evidence/projects/wm019_wam_future_metric_paired_diagnostic.html)。
10. [WM-019 Matched-Checkpoint Bridge](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.html)。
11. [TurnOffMicrowave trained-failure P0 audit](../evidence/projects/cosmos_policy_turnoffmicrowave_trained_failure_p0_audit.html)。
12. [Checkpoint save-load gate P0 audit](../evidence/projects/cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html)。
