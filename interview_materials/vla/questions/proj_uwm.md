# VOL 07 UWM / LIBERO 项目原子题卡（Protocol Boundary Batch 1 + Ownership）

> 状态：`drafted / cards_4_of_4 / WARN`  
> 更新日期：2026-07-21  
> 当前题数：4 / 4  
> 覆盖范围：`PROJ-UWM-001..004`  
> 难度：L3 4 题  
> 优先级：P0 4 题  
> 练习状态：`unseen`  
> 前置证据：[UWM / LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)；协议来源见 [VOL 04 benchmark evidence audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)；RoboCasa 训练/0-success 边界见 [UWM/LIBERO/RoboCasa transfer evidence freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)。

## 评估协议冲突如何安全回答

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-UWM-001</b> · UWM/LIBERO 中 0.744、0.928 和论文约 0.79 三个结果如何解释，为什么不能直接比较？</summary>

**面试意图**：判断你能否固定评估 tuple、区分本地证据与远端确认结果，并在结果冲突时避免把协议差异包装成模型 uplift 或官方复现。

**30 秒回答**：先冻结协议：186/250=0.744 是 fixed-pruned-init+5-step warmup 的用户确认结果；0.928 是 reset-style diagnostic；论文约0.79 用 OOD init、shift、背景移除和多 seed。三者不能横比，当前缺 checkpoint/episode bundle，只能讲协议敏感性。

**机制展开（约 2 分钟）**：先把 init/seed/warmup/horizon/normalizer/checkpoint、predicate、分母写入 manifest。186/250 是 fixed-pruned-init 的 5×50 结果，缺 raw JSONL/权重；0.928 用 env.seed+reset，协议更容易；论文约0.79 用 OOD init、shift、去背景、3 seeds。三者不可横比，0.928→0.744 只说明 protocol sensitivity。要归因模型，需同 checkpoint paired init、episode trace、scorer、ownership；只能讲 report/user-confirmed evidence，不称 benchmark。

**诊断 / 证据**：逐 episode 保存 task、init index、seed、warmup、horizon、camera/state/action schema、normalizer hash、checkpoint hash、success predicate、terminal reason 和 denominator。先做同 checkpoint 的 reset-style↔fixed-pruned-init paired run，再按 task/失败类型分层；若要对齐论文，还要复现 OOD initialization、object shift、背景设置与多 seed，并冻结 scorer 版本。当前本地有 launcher、task mapping、协议开关、report 和用户确认 summary，但缺 250 条 raw episode、checkpoint/normalizer immutable bundle 与 ownership ledger，保持 `WARN`。

**项目挂钩**：可讲我负责把 LIBERO-90→LIBERO-10 的 UWM finetune/rollout 路径、pruned-init、warmup、rollout 数和 success predicate 固定下来，并定位 zarr 小 chunk 导致的 DataLoader stall。RoboCasa 可讲 actionheadfix 的 partial decoder init、12D contract 与 raw sweep：一条30-epoch run的full-h4为`0/54`、robot-env contact `45/54`，其它setting也只有`1–2/54`，所以只称训练/诊断推进，不称性能修复。历史`27/54`来自未对齐run摘要，不能混用。安全口径是“我负责协议迁移、诊断和验收”，不把 UWM shared diffusion architecture、远端 checkpoint 或结果写成个人原创/严格复现。

**追问树**：为什么 reset-style 更高？`0.744 vs 0.79` 能否说只差 4.6pp？如何证明 checkpoint 相同？DataLoader stall 如何定位？actionheadfix 为什么 loss 改善仍 `0/54`？teacher-forced x0 MSE 与 closed-loop success 差在哪里？strict `convert_action` 的 `0/6` 为什么不能算六条模型失败？

**易错点**：混用 strict/fixed/reset 口径；把用户确认 JSON 当本地 raw artifact；把 Table II 论文均值当同协议 baseline；忽略 normalizer、init、seed、warmup、horizon 或 success predicate；把 DataLoader smoke 写成完整训练吞吐提升。

**危险答案**：说“0.928 证明模型最好”“0.744 只比官方低 4.6pp”“loss 从 95 降到 0.22 所以 actionheadfix 已成功”“strict convert_action 0/6 都是模型失败”“Git author 证明全部代码是我写的”或“RoboCasa 已完成 benchmark”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## Ownership 与结果归属

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-UWM-002</b> · UWM/LIBERO 哪些部分能说是你做的？如何区分上游、Git 快照、远端结果和个人 ownership？</summary>

**面试意图**：判断你能否把迁移、协议、诊断、运行和结果归属拆开，而不是把一次性 snapshot 或用户确认 summary 认领为全部个人工作。

**30 秒回答**：我把贡献拆成训练迁移、评估协议、数据管线和失败诊断。源码/patch/report 可核验，但 Git 提交不等于逐文件原创；UWM architecture 属于上游，`186/250` 是用户确认的远端 summary，checkpoint/normalizer/episodes 未闭合，ownership 需按 ledger 保守表述。

**机制展开（约 2 分钟）**：`0341c50` 一次加入 official repro，`a37a386/2a2912d/1a03fe9/8eaddf2` 记录 actionheadfix、single-task gate、h4 sharding 与 aux 参数修复；可讲 evaluator、launcher、loader patch 和训练诊断的文件事实，但 commit 仍不等于逐文件原创。再固定 fixed-pruned-init、warmup、normalizer、horizon、scorer，不能混入 reset-style。最后说明 recovery manifest 有未提交修改，strict JSON 是 user-confirmed remote final，不是本地 raw verified；现场解释一个函数并划清亲手、协作、工具和运行边界。

**诊断 / 证据**：[UWM Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html) 的 13 行矩阵；检查 Git path history、blob/SHA、工作树 status、sync manifest、user-confirmed JSON 和 upstream audit。未口述前保持 `candidate_confirmation_pending / unseen`，不创建 coaching state。

**项目挂钩**：可以可信地讲协议迁移、strict/reset reconciliation、zarr/DataLoader first failure 和 RoboCasa contract debugging，同时明确不把 UWM shared diffusion、远端 checkpoint 或 0.744 写成个人原创/严格复现。

**追问树**：哪个函数是你亲手改的？谁运行 remote？actionheadfix 的 partial init/x0 metric/h4 launcher 各由谁设计、实现和验收？0.744 的 checkpoint/normalizer/episodes 在哪？preload 是否提升 GPU throughput？RoboCasa 0/54 的 raw trace 在哪？

**危险答案**：说“Git author 证明全部 patch 是我写的”“0.744 是我的本地 benchmark”“UWM architecture 是我设计的”或“有 summary 就等于有 checkpoint”。

**来源**：[1][5][6]　**练习状态**：unseen

</details>

## 数据管线停顿与证据边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-UWM-003</b> · zarr DataLoader 的周期性长停是怎么定位的？为什么 preload+infinite smoke 不能直接写成训练吞吐提升？</summary>

**面试意图**：判断你能否把数据等待、GPU 计算、DDP 同步拆开，用最小 A/B 找 first divergence，并区分 DataLoader-only 诊断与真实 GPU 训练收益。

**30 秒回答**：拆开 `data_wait/train/total` 后，DataLoader-only A/B 的 `bs64 finite` p95 wait 从 `13.862s` 降到 preload+infinite 的 `0.194s`，支持 zarr 小 chunk 是主要等待来源；没有 GPU 吞吐、显存和 loss parity，不能称端到端提速。

**机制展开（约 2 分钟）**：用 \(T_{step}\approx\max(T_{GPU},T_{data})+T_{sync}\) 分层，固定数据和加载配置，记录 `data_wait_sec/train_sec/total_sec`。`bs64` finite 复现 5 次超过 10 秒的长停；只开 infinite sampler 仍约 `13.183s`，而 preload zarr 后降到 `0.194s`，说明主要等待在随机 chunk 读取。下一步做 30–100 step matched GPU A/B，比较 samples/sec、显存、三段耗时、loss 和 checkpoint，确认没有改变数据顺序或目标。

**诊断 / 证据**：local report、`benchmark_libero_dataloader_stall.py` 和 dataset/loader patch 给出四组 smoke 数字与开关：`UWM_INFINITE_TRAIN_SAMPLER`、`UWM_ROBOMIMIC_PRELOAD`、workers/prefetch/pin、`UWM_STEP_TIMING_EVERY`。现有证据不包含正式 GPU matched A/B、长期吞吐、显存曲线或收敛 parity，因此根因表述应是“证据支持的主要等待来源”，不是已证明唯一 root cause。

**项目挂钩**：可讲 UWM LIBERO-90→LIBERO-10 迁移中，训练出现周期性停顿时如何先隔离数据管线，再决定是否预载；这与 0.744/0.928 评估协议问题是两条证据链，不能用 DataLoader smoke 补出 benchmark uplift，也不能把 patch 或 Git author 自动升级为个人独立 ownership。

**追问树**：为什么 infinite sampler 没解决长停？preload 的内存代价如何测？如何保证 A/B 数据顺序与 normalizer 一致？`T_data` 与 DDP `T_sync` 怎么区分？为什么不能用 `median sec/it` 证明吞吐提升？下一步 GPU smoke 的最小样本量和验收字段是什么？

**易错点**：把 `p95 wait` 当 samples/sec；把 DataLoader-only 结果当 GPU 训练结果；只跑 preload 没有 baseline；忽略 zarr chunk、epoch 边界、workers/prefetch 和 batch 改变；把数据等待改善写成模型 loss 或 closed-loop success 提升。

**危险答案**：说“preload 后训练吞吐提升已证明”“infinite sampler 解决了根因”“13.862→0.194 就是端到端加速”“DataLoader smoke 证明模型收敛更好”或“这个 patch 一定是我独立原创”。

**来源**：[1][4][6]　**练习状态**：unseen

</details>

## 训练拟合、Open-loop 与 Closed-loop 的断层

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-UWM-004</b> · actionheadfix 的 loss 和 teacher-forced x0 都改善了，为什么 RoboCasa h4 仍是 0/54？你如何定位 first divergence？</summary>

**面试意图**：判断你能否把优化器收敛、open-loop action fit、execution validity、关键目标接触和任务成功分层，而不是用低 loss 宣称闭环修复。

**30 秒回答**：训练 loss 从`2.4300`降到`0.07689`，但无 validation；同 checkpoint/normalizer 下 full h4 仍`0/54`，仅`0–2/54`成功，env errors=0且`45/54`有contact；first divergence 在 fit 到闭环之间，不能称修复。

**机制展开（约 2 分钟）**：base-load preflight是478 target keys中446 matched，7D→12D action encoder/decoder的8个key重置，task/prompt/state/right-view等新增模块保持missing-init；训练用12D reordered action、16D state和三视角。八份raw JSON共享同一54-scenario集合、checkpoint和normalizer，full h1/h2/h4/h5/h8为`2/1/0/1/1` success，no-prompt/no-right/no-state h5为`2/2/1`。差值被一两个Kettle/Microwave episode主导，不能做ablation因果；普通接触也不等于命中任务谓词。

**诊断 / 证据**：[ActionHeadFix P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) 独立解析8×54 records：每task 3 trials、scenario/seed set完全相同、success field与record recount一致、env errors全0。full-h4 `45/54`有robot-env contact但`0/54` success；checkpoint只剩remote `models.pt` path，本地有normalizer hash但没有binary/fresh-load。历史30/100 epoch、strict/direct A/B与Human300属于相邻run family，只作旁证不混分母。

**项目挂钩**：可讲从 LIBERO 7D action 迁到 RoboCasa native 12D 时，如何做 partial init、分组 x0 gate、execution bridge 和 contact taxonomy；不可把 UWM 架构、低训练 loss、任意接触或 GT bridge parity 说成个人原创、闭环成功或唯一 root cause。

**追问树**：为什么没有validation仍能说训练完成？teacher-forced与rollout分布差在哪里？`45/54` contact为什么不等于成功？为什么432 records不是432个独立benchmark trial？no-prompt `2/54`能否说prompt有害？checkpoint path为什么不等于binary验证？single-task overfit gate应验收什么？

**易错点**：把训练 loss、x0 MSE、任意 contact、valid rollout 和 success 混成一个指标；把 step-0 env error 计为模型失败；只比较 epoch，不固定 checkpoint、normalizer、horizon、aux 与 init；从 GT bridge parity 推导模型 action 正确。

**危险答案**：说“loss降到0.0769所以修复成功”“0/54只是环境太难”“45/54接触率证明策略有效”“no-prompt多一个success证明prompt有害”“432 records可以合并成总成功率”或“远端models.pt path等于本地checkpoint已验证”。

**来源**：[1][3][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [UWM / LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：claim 分层、strict/reset 协议、数据管线诊断与 ownership 边界。
2. [VOL 04 benchmark evidence audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)：LIBERO 默认、UWM Table II OOD 与项目 fixed-init 的不可比性。
3. [UWM video/action claim-to-code audit](../sources/vol_04_uwm_video_action_claim_to_code.html)：shared diffusion、action/video target、normalizer 与上游/本地边界。
4. [UWM/LIBERO project page](../../05_uwm_libero_eval_protocol.html)：项目叙事、报告结果和评估协议上下文。
5. [UWM Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html)：Git history、13 行 ownership matrix、工作树与 user-confirmed result boundary。
6. [UWM/LIBERO/RoboCasa Transfer Evidence Freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)：actionheadfix、Human300/target/x0 指标、30/100 epoch、h4 `0/54` 与 convert_action A/B。
7. [UWM RoboCasa ActionHeadFix 30-Epoch P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)：8卡3930-step训练、12D normalizer、8×54 raw rollouts、full-h4 `0/54`/contact `45/54`与checkpoint/ownership边界。
