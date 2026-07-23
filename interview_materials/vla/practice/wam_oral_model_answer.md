# PROJ-WAM-001/002 从项目实现反推的证据约束口述稿

> 状态：`implementation_derived_model_answer / PROJ-WAM-001+002 / candidate_self_report_bounded / not_candidate_transcript / unseen`
> 更新日期：2026-07-22
> 题目：如何介绍 Cosmos Policy / WAM 项目，并解释 1 epoch gate、两类训练系统失败、CoffeePressButton 诊断证据与个人 ownership？

## 1. 项目定位

这不是把所有 Cosmos/WAM 日志拼成“一个 1 epoch 结果”的故事。当前需要明确区分两个 run family：第一条是按 Predict2 + T5 + RoboCasa 合同搭建的 8 卡、global batch 128、`9907` steps 单 epoch gate；它先暴露 dataloader 导致的 CPU cgroup OOM，修复后又在 `state_dict(destination=...)` 保存接口处失败。第二条是独立的单卡 GPU7 full10k repro：日志记录 step `10000` loss=`0.0543`、远端 checkpoint 保存成功、`EXIT:0`，随后进入 24 task × 5 episode 的 RoboCasa eval。前者不能称完成的 1 epoch checkpoint，后者可以称独立 full10k 训练与评测链路，但 checkpoint binary/hash、fresh-process reload 与训练带来的 uplift 仍未闭合。

**项目分型**：VLA/WAM 训练复现 + RoboCasa 闭环评测适配 + 失败诊断。**目标岗位**：VLA / embodied-AI 算法与训练评测工程。**当前最强信号**：能把模型训练、checkpoint、normalizer、controller、episode scorer 与 raw artifact 连成协议链；**当前短板**：逐文件 ownership、immutable checkpoint 与修复后 paired rerun 尚未闭合。回答结构固定为：实现链路 → 评测合同 → bad case → 验证与边界，而不是从 paper architecture 开始背诵。

## 2. 30 秒版本

> 我做的是 Cosmos Policy 在 RoboCasa 上的训练与评测复现：训练侧接入 online Reason1 并完成一条单卡 10k-step run，日志记录 loss=`0.0543`、checkpoint saved 和 `EXIT:0`；评测侧把 local DCP 接回官方闭环，固定 chunk 32、执行前 16 步和 5-step denoising。24×5 eval 的 raw 是 `2/120`，但两条都是 length=1 artifact，trusted 为 `0/118`；同一 harness 的 official-HF path 为 `84/118`。所以我强调协议对齐和失败诊断，不宣称 uplift；另一条 8 卡 1-epoch gate 在 OOM 与保存接口处失败，也不和 full10k 合并。

## 3. 2–3 分钟版本

> 这个项目的目标是把 Cosmos Policy 的 WAM 训练从“能启动”推进到“训练、保存、加载、闭环评测都能按协议验收”。我先保留官方 experiment、trainer、model 和 RoboCasa dataset 路径，在训练入口里启用 online Reason1 文本编码；由于在线编码不需要巨大的预计算 embedding 字典，我放了只在模型重算前被消费的 placeholder，同时补齐 lazy success-rollout-as-demo 路径里缺失的 `success=True` metadata。单卡 full10k recipe 使用 batch 1、chunk 32、demo/rollout 各 0.5、`p_world_model=0.5`，原始日志在 step 10000 记录 loss=`0.0543`、保存 `iter_000010000`、`Done with training` 和 `EXIT:0`。
>
> 评测时我没有重写 RoboCasa 主循环，而是只替换 local DCP model loader，并给 action/future/value inference 加 BF16 autocast。链路仍是官方的 create env→prepare observation→get action→env.step→save rollout video；同时旁路记录每次 `32×7` action chunk 的 min/max/mean/std 和 first row，日志故障不影响 eval。协议固定为 24 个任务、每任务 5 个 episode、chunk 32、每次执行前 16 步、action denoising 5 步、固定 seed。full10k summary 的 raw 是 `2/120`，但两个 success 都发生在 length=1，按预注册的同一 invalid policy 排除后是 `0/118`；同一 harness 下 official-HF path 是 raw `86/120`、trusted `84/118`。这说明环境、controller、success predicate 和 rollout 保存链不是天然全坏，但不能据此断言唯一根因；排查优先级转向 checkpoint/config、Reason1 embedding、dataset statistics、action unnormalization 与训练退化。
>
> 我还单独搭了 8-GPU、每卡 batch 16、global batch 128、`9907` steps 的 1-epoch gate。它先在 step 1903 以后出现 rank `-9`/`EXIT=247`，结合 cgroup 记录定位 `itertools.cycle(dataloader)` 缓存 batch 的 CPU 内存增长；改成普通 iterator 并在 `StopIteration` 重建后，8 卡 5-step smoke `EXIT=0`。但正式 run 到 step 1500 保存时，DeepSpeed 调用标准 `state_dict(destination, prefix, keep_vars)`，Cosmos override 不兼容并以 `EXIT=1` 结束，所以这条 gate 没有可用 checkpoint。面试中我会把个人价值讲成训练/评测协议迁移、可观测性和 first-divergence 诊断；不会把 upstream architecture 说成原创，也不会把 full10k 与失败的 1-epoch gate 拼成一个成功结果。

### 3.1 从实现读出的训练与评测链路

```text
RoboCasa demos / rollout episodes / command
  -> official Cosmos dataset + online Reason1 conditioning
  -> action/world sample routing + masked training_step
  -> full10k DCP checkpoint path
  -> local DCP loader + official RoboCasa eval loop
  -> 32x7 action chunk -> execute first 16 -> controller/env step
  -> per-episode success/video + action-debug JSONL
  -> raw/trusted recount + bad-case diagnosis
```

训练适配中真正改变的是文本条件与 lazy-data 边界，不是 Cosmos Policy 的 backbone：`enable_official_online_text_encoder()` 把 `compute_online` 打开，`OnlineTextEmbeddingPlaceholder` 避免强依赖预计算 embedding，`repair_success_rollout_demo_metadata()` 修补 success rollout 被当作 demo 时缺失的 metadata。评测适配中真正改变的是 checkpoint loader、process compatibility、BF16 autocast 与旁路 action logging；环境创建、observation preparation、官方 `get_action`、controller step、success predicate 和视频保存仍走 upstream eval loop。

### 3.2 Implementation anchors：文件、SHA 与能证明的内容

| Project 相对路径 | SHA-256 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| `wm/launch_cosmos_policy_online_text_formal.sh` | `8C67A97288341A1875FC46C95AB3AD77F05516F7DEA273BA823CE1B5FB093806` | single-GPU、10k、batch 1、dataset mix、base/tokenizer 与保存配置 | 实际运行成功或个人独立编写 |
| `wm/cosmos_policy_train_with_consolidated_online_text.py` | `FBE879A3AD6E3E77B258AE971480338CF41D6EC3378E29C9DE05209CF9D38DF8` | online Reason1、placeholder、lazy success metadata repair 与 official trainer path | 每个函数的个人 authorship |
| `report/cosmos_wam_repro/cosmos_policy_wam_repro_full10k_20260619.log` | `403604E8A1C2F77041E5E1ED43B80AE0BDD2630911D8DB1645B6FB6D0F0443EC` | step 10000 loss=`0.0543`、checkpoint path、`Done with training`、`EXIT:0` | 本地 checkpoint binary/hash 与 reload parity |
| `report/cosmos_wam_repro/loss_breakdown_full10k.jsonl` | `B6CEB4459C8CB5A00AADF3AE7F00F440DC359111B143FE44D5AF21CCB639BDDE` | full10k 逐步训练诊断记录存在 | held-out performance 或 closed-loop uplift |
| `wm/cosmos_policy_robocasa_official_eval_wrapper.py` | `45CB2D44A547C645D15AE890DCFF023569CF126FC20E85A88B7160AED2CF5E42` | local DCP loader、official loop、BF16 autocast、action-debug schema | official scorer 等价或个人模型效果 |
| `wm/launch_cosmos_policy_robocasa_eval_20260620.sh` | `AFD68C7405EA1465D6E1D2B2AFDB387D6FF9085FDD3C75B729AF3E9FDB054DB0` | checkpoint/stats/embedding/task/seed/open-loop/denoise 命令合同 | episode 结果本身 |
| `wm/run_cosmos_policy_robocasa_eval_5ep_tasks_20260620.sh` | `C94DB66F67920CBABA0B3FBBE492967F85DE5080F7F25C774A8D579967B77DEC` | 24 task × 5 episode sweep 与 per-task status | 24 个任务都由同一 immutable checkpoint 内容运行 |
| `report/cosmos_policy_eval/remote_artifacts/eval_summary_conservative.json` | `C9538A2E418BCBEDD88B8DCFB308F0E1AF428DBA2912A959DEA946872A3247BE` | full10k raw `2/120`、artifact=2、trusted `0/118` | benchmark uplift、唯一 root cause |
| `report/cosmos_policy_eval/baseline_remote_artifacts/eval_summary_officialhf_baseline.json` | `7B211B9D6F20BC95986A77C3CC901814AB6A705065016D7F68B67548BA6CACE9` | official-HF path raw `86/120`、artifact=2、trusted `84/118` 的本地重算材料 | official checkpoint ownership 或与 full10k 的严格 matched causal comparison |
| `report/cosmos_policy_eval/.../CoffeePressButton...smoke-1x1.log` | `B5FF9DB2129EBC0B41CA2D0C11911C94753B5400A8BBACFFBAB1F3109CB2938F` | 1 episode、`success=false`、`0/1`、`EXIT:0`、视频保存 | 多 episode success 或 checkpoint uplift |
| `report/cosmos_policy_eval/.../CoffeePressButton...smoke-1x1.jsonl` | `6357CD83CB4A40B184B42721110A7FADD4693DED75E68685FD6C2B6949557018` | 19 次 query、每次 `32×7` action chunk、有限值与 checkpoint path | action-label loss、7D→12D controller roundtrip |
| `report/cosmos_policy_eval/muxi_deepspeed_1epoch_20260623/run_contract.json` | `9CAAC2937AC14AAA69DF2EBFD3C7603CB92B34254879BD1CD599C9FE73749D7A` | 8 卡、per-GPU 16、global batch 128、`9907` steps、5-frame condition | 1 epoch 已完成 |
| `.../nocycle_fix_20260624/...no_cycle_20260624.py` | `FD5F96C4C9004A5FBFE35B80504C034B83FEDEC0431C47EAD91D958A379DE07D` | iterator 修复实现快照 | matched long-run 内存因果已完全闭合 |
| `.../nocycle_fix_20260624/smoke5_launch.log` | `76378669F19CCC87E9418241A7EB17AFD0854BE704362CA30EFF5491BE66D94E` | 8 卡 no-cycle 5-step smoke，exit 0 | 长跑、save/load 或 eval 成功 |
| `.../ds_8gpu_bs16_1epoch_nocycle_save1500.../launch.log` | `8FEC262805242AFC3FCD7846A3DDB1043860E17BF5DEB008369D7CD9F67061C3` | step 1500 `state_dict(destination=...)` TypeError、exit 1 | checkpoint 已生成 |

`...` 只为表格可读性缩短公共前缀，所有原文件均位于 `C:\Users\mousongzhe\Project`；本页没有修改该 Project 工作树。

### 3.3 Truth Boundary 与 ownership 用词

| 口述内容 | 当前证据等级 | 推荐第一人称 | 禁止升级 |
| --- | --- | --- | --- |
| Cosmos fine-tune 与 eval 项目范围 | 候选人已 self-report；代码与日志部分支持 | “我开展了训练/评测复现并按协议验收” | “所有代码均由我独立编写” |
| online Reason1、metadata repair、DCP eval wrapper | implementation-local；逐函数角色仍未确认 | “这条实现中我采用/接入了……” | 未确认前不说“我原创设计” |
| full10k 训练终点 | log-backed / checkpoint-path-only | “该独立 run 到 10k 并记录保存成功” | “本地 immutable checkpoint 已验证” |
| 8-GPU 1-epoch gate | run-contract + failure-log-backed | “我搭建并排查了 1-epoch gate” | “我完成了 1 epoch” |
| full10k `0/118` 与 official-HF `84/118` | remote-artifact-backed / checkpoint-unverified | “我按同一 invalid policy 重算并用于诊断” | “训练导致下降 71.19 个百分点” |
| Cosmos slot/mask/routing architecture | upstream-verified | “我按 upstream contract 对齐” | “我设计了 WAM architecture” |

### 3.4 面向 VLA 岗位的能力映射

| 岗位能力 | 当前实现证据 | 强度 | 面试策略 |
| --- | --- | --- | --- |
| 多模态训练理解 | online Reason1、demo/rollout mix、world-policy routing 与 loss diagnostics | 强 | 讲输入、mask、route 与训练 target，不背抽象名词 |
| 大模型训练工程 | single-GPU full10k、8-GPU gate、cgroup OOM、DeepSpeed save first divergence | 中强 | 重点讲 gate 与验证覆盖面 |
| 机器人闭环评测 | official RoboCasa loop、chunk/replan、controller、raw/trusted recount | 强 | 讲协议 tuple 与 invalid rule |
| 数据与 action contract | dataset statistics、normalizer、7D action、32→16 execution | 中强 | 主动承认 7D→12D roundtrip 仍缺 bundle |
| 结果可信度 | 有 raw logs/summary/action trace，但 checkpoint identity 与 paired rerun 未闭合 | 中 | 不用 loss 或单 episode替代 success |

### 3.5 Production Gap、补强状态与 SP/SSP 材料就绪度

| Gap | 大厂追问 | 当前状态 | 下一证据 |
| --- | --- | --- | --- |
| checkpoint lineage | 跑 eval 的 binary 到底是哪一个？ | `可补做` | remote content hash、local manifest、fresh-process reload parity |
| matched comparison | official-HF 与 full10k 是否只差权重？ | `可补做` | config/stats/T5/scorer/seed 全字段 join key |
| action semantics | `32×7` 如何变成 controller `12D`？ | `部分已做` | normalizer roundtrip、7D→12D adapter trace、executed prefix |
| root cause | 0-success 是 conditioning、stats 还是退化？ | `部分已做` | 同 checkpoint、同 init 的 patch→paired rerun |
| ownership | 哪些函数是本人/协作/工具？ | `待确认` | per-file role ledger 与 review/operator 记录 |

当前分数是**材料就绪度**，不是候选人 mastery：业务真实性 `2/5`、贡献边界 `2.5/5`、技术深度 `4/5`、数据理解 `3.5/5`、评估可信度 `4/5`、工程闭环 `3/5`、生产差距认知 `4.5/5`、抗追问材料 `4/5`、VLA 岗位匹配 `4.5/5`、ownership `2.5/5`，合计 **34.5/50，强可投材料档**。SP 阻断项是 checkpoint lineage、逐文件 ownership 和修复后 paired rerun；在真实口述前不把这一分数记入 coaching state。

补强顺序：`半天` 完成 per-file role ledger 与三遍口述计时（`可补做`）；`1 天` 完成 save→destroy→fresh-load manifest（`可补做`）；`3 天` 冻结 full10k/official-HF 的 matched protocol tuple（`部分已做`）；`1 周` 完成至少一个候选根因的同 init paired rerun（`可补做`）。当前简历安全表达是“开展 Cosmos Policy / RoboCasa 训练与评测复现，完成协议对齐、运行审计与失败诊断”；只有前三个 gate 闭合后才可升级为“负责实现/优化”，只有 paired result bundle 到位后才可写具体效果。

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

## 9. PROJ-WAM-002：哪些部分能说是我做的？

### 9.1 30 秒 ownership 版本

> 我能认领的是 Cosmos Policy / RoboCasa 的训练评测复现、协议对齐和失败诊断：我能沿 full10k、8-GPU gate、DCP eval、action trace 与 raw/trusted summary 解释验收链。latent slot、mask、routing 属于 upstream，不是我的原创；六个关键 WAM 文件只保留 `c4469eb` initial snapshot，没有增量 diff，因此我不凭 Git author 声称所有函数独立编写。面试中我用“开展、接入、运行、审计、定位”，并明确协作、工具和 operator/reviewer 边界仍待逐项确认。

### 9.2 2–3 分钟 ownership 版本

> 我会把贡献拆成四层。第一层是 upstream：Cosmos Policy 在统一 latent sequence 里组织 action、future、value，并通过 condition/loss mask 和 sample routing 切换训练角色；这些机制来自 NVlabs paper/repo，我只按合同理解和对齐，不说是我设计的。
>
> 第二层是本地训练与评测实现。项目里的训练入口启用了 online Reason1，处理 placeholder embedding 和 lazy success-rollout metadata；评测 wrapper 把 local DCP checkpoint 接回官方 RoboCasa loop，固定 chunk 32、执行前 16 步、5-step action denoising，并旁路写 action-debug。根据我已明确的项目范围，我可以说自己开展了 Cosmos fine-tune、eval 和协议对齐；但六个关键 WAM 文件在 Git 中都只来自 `c4469eb` initial snapshot，没有 pre-snapshot commit 或 before/after diff，因此更安全的说法是“我的项目实现采用/接入了这些路径，我负责把它们运行、核对并用于诊断”，而不是“每个函数都由我从零独立编写”。
>
> 第三层是运行与故障闭环。我能讲清 full10k 日志到 step 10000、8-GPU `9907`-step gate 的 cgroup OOM/no-cycle smoke、step 1500 `state_dict(destination=...)` first divergence，以及 24×5 eval 的 raw/trusted 重算。这里也要把 role 拆开：代码存在不等于我就是原作者，远端 path 存在不等于我就是 operator，报告存在不等于我就是 reviewer；当前缺 shell history、review record 和逐文件工具/协作者说明，所以我认领的是项目级训练评测与证据审计，不认领尚未闭合的逐文件 authorship。
>
> 第四层是结果归属。full10k 的 `0/118`、official-HF path 的 `84/118`、CoffeePressButton 失败 trace 和 offline proxy 都可以作为诊断材料，但 official checkpoint 不是我训练的，8-GPU gate 也没有完成，历史 MSE/uplift 更没有完整 provenance。我的强项是把实现、运行、metric 和 unknown 分开，并给出下一步 save/load、matched protocol、7D→12D roundtrip 和 paired rerun；我的边界是暂不宣称 architecture 原创、完整 1 epoch、benchmark uplift 或唯一 root cause。

### 9.3 从实现与 Git 能得到的 role matrix

| 层级 | 当前证据 | 能说的第一人称 | 不能说 |
| --- | --- | --- | --- |
| Upstream architecture | frozen paper/repo：latent slots、mask、routing、sampler | “我按 upstream contract 理解并对齐” | “我设计了 WAM architecture” |
| 项目范围 | 候选人 self-report：Cosmos 1-epoch fine-tune、eval、协议对齐 | “我开展了训练、评测与协议核对” | self-report 自动证明逐文件 authorship |
| WAM 训练入口 | `c4469eb` snapshot + current full-SHA code | “项目实现接入 online Reason1、placeholder 与 metadata repair；我能解释并运行这条链” | “我从零独立编写全部函数” |
| RoboCasa eval wrapper | `c4469eb` snapshot + DCP loader/action-debug/eval logs | “我把 local checkpoint 接到官方闭环并审计 action/episode artifact” | “官方 evaluator、controller 或 scorer 是我实现的” |
| full10k / 8-GPU runs | run contract、launch log、summary、failure stack | “我搭建/运行/排查这些 run family”是项目级 self-report 口径 | 没有 operator record 时声称每次远端命令均由本人执行 |
| raw/trusted recount | 两份 summary 与 audit code/artifact | “我按相同 invalid policy 复核并用于诊断” | 把 official `84/118` 写成本人模型成绩 |
| `cv` evidence pages | 当前面试仓库的 Codex/工具辅助审查产物 | “我用这些材料准备和复核口述” | 把面试准备文档当成原项目个人贡献 |

Git 的可核验事实是：`wm/cosmos_policy_train_with_consolidated_online_text.py`、训练 launcher、RoboCasa eval wrapper、eval launcher、24-task sweep 和报告生成器均只显示 `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`（`Initial project snapshot`，author identity 为 `mousongzhe`）；当前 HEAD 对这些路径没有后续增量 history。author identity 是 lineage 线索，不是 authorship、operator 或 reviewer 的充分证据。

### 9.4 危险 / 可过 / 强回答

**危险回答**：

> Cosmos Policy 的 action/world/value architecture 是我设计的，代码都是我写的；我完成了 1 epoch，并用自己的模型跑到了 `84/118`。

问题：同时混淆 upstream architecture、snapshot author、失败的 8-GPU gate、official checkpoint 和本地 full10k。

**可过回答**：

> 我主要做 Cosmos Policy 的训练和 RoboCasa 评测复现，architecture 是上游的。我做了训练适配、跑实验并分析失败，但部分代码和运行角色需要再核对。

优点：没有抢占 upstream；缺点：没有文件、函数、run 与验收证据，仍像泛泛“参与”。

**强回答**：

> 我能确认的项目边界是训练评测复现与协议诊断，不是 architecture 原创。训练侧我沿 `launch_cosmos_policy_online_text_formal.sh` 和 online-text entry 解释 Reason1、dataset mix 与 full10k；评测侧我沿 local DCP loader、24-task sweep、action-debug 和 raw/trusted summary 解释 checkpoint→action→controller→episode 链。8-GPU gate 的 no-cycle smoke 与 `state_dict` failure 也能用日志复核。个人逐文件 ownership 仍有一个诚实缺口：这些 WAM 文件只保留 initial snapshot，缺 before/after diff，operator/reviewer/tool 记录也不完整。因此我说“我开展、接入、运行并审计了这条复现链”，不说“所有函数独立编写”；官方 `84/118` 只作为同 harness 诊断对照，也不写成我的模型结果。

需要补的证据：per-file role ledger、pre-snapshot diff 或设计记录、远端 command/operator record、review/验收记录，以及工具/协作者边界。

### 9.5 Ownership 追问树与最小表达合同

```text
“哪些是你做的？”
  -> 先报项目级职责：训练 / 评测 / 协议 / 诊断
  -> 再给一个训练文件 + 一个评测文件 + 一个运行 artifact
  -> 每个 claim 说明 action、evidence、verification、boundary

“这个函数是你写的吗？”
  -> 有 pre-snapshot diff / review：按真实角色回答
  -> 只有 initial snapshot：说实现路径与自己如何使用，authorship 保持 pending

“远端 8 卡是谁跑的？”
  -> 有 shell history/operator record：报 operator 与 reviewer
  -> 没有：只说项目 run artifact 可复核，不推断执行者

“84/118 是你的成绩吗？”
  -> 明确是 official-HF checkpoint path 的 eval 对照
  -> 个人贡献是 harness 运行/审计与 denominator 重算，不是权重训练
```

口述时每个 ownership claim 应满足：`我做的动作 + 文件/函数/命令 + 如何验收 + upstream/协作/工具边界`。缺任一项就降级为“项目实现包含 / 我参与使用或审查”，而不是用 Git author 或目录位置补齐。

## 10. 练习边界

- 这是 `PROJ-WAM-001/002` 的 model answer，不是候选人的真实 transcript；两张题卡继续保持 `unseen`。
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
