# UWM RoboCasa ActionHeadFix 30 Epoch：Train-to-Closed-Loop P0 证据审计

> 状态：`p0_audited / remote-snapshot-raw-rollouts / checkpoint-path-only / protocol-bounded / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计 `target_atomic_seen_official12_task_30epoch_muxi_20260628_openpi_state_3view_phase_30ep` 这一条 30-epoch run、对应的八组 54-scenario rollout 与同阶段 preflight；不把 Human300、100-epoch resume、其它 taskcondfix/state-weighted run、LIBERO `186/250` 或不同 action bridge 合并进主结果。

## 1. 问题（Question）

这条 UWM→RoboCasa actionheadfix 运行线是否真的完成了训练、保存引用和 closed-loop evaluation？训练端的 loss 下降能否转化为任务成功？`exec_horizon`、prompt/state/right-view ablation 的八组 rollout 有什么可复核结论？哪些字段仍不足以称为 RoboCasa benchmark、checkpoint closure 或个人独立成果？

## 2. 结论先行

当前 remote snapshot 已经超过 report-only：它保留了训练命令与 `train.out`、run summary、DeepSpeed effective config、12D normalizer、三类 preflight、八份原始 rollout JSON 和八份 eval log。独立复核可以证明：

1. 8 卡 MetaX C500 的 30-epoch run 完成 `3930` steps；8/8 process 成功退出，未发现 traceback 或 CUDA OOM；
2. 训练使用 18 个 atomic-seen task、9126 episodes、133457 sequences、12D reordered action、16D state、三视角、task/prompt/state conditioning；
3. `train.out` 中 41 个打印 metric point 从 step 0 的 loss/action/raw-action `3.3257/2.4300/0.9986` 到 step 3929 的 `0.25385/0.07689/0.03043`；但 `val_ratio=0`、`eval_every=0`，这些只是训练 batch 指标，不是 held-out generalization；
4. 八个 rollout JSON 都包含相同的 54 个 `(scenario, task, seed)`，覆盖 18 task×3 trials；全部使用同一远端 `models.pt` path、同一 normalizer path、`official12 + convert_action`，共 432 条配置内 record，环境错误为 0；
5. closed-loop success 极低且不稳定：full input 的 h1/h2/h4/h5/h8 分别为 `2/54、1/54、0/54、1/54、1/54`；h5 ablation 的 no-prompt/no-right/no-state 为 `2/54、2/54、1/54`；所有 success 只出现在 TurnOnElectricKettle 或 TurnOnMicrowave；
6. full-h4 有 `45/54` episode 记录 robot-env contact，但 success 为 `0/54`，说明“产生接触”不等于“完成任务”。

因此，安全结论是：**训练链、12D action contract 和 54-scenario eval harness 可以审计；训练 loss 明显下降，但没有转化为稳定的 closed-loop task success。** 当前不能宣称 actionheadfix 已解决 RoboCasa transfer，也不能从 1–2 个 success 推导 prompt/right-view ablation 的因果收益。

## 3. P0 promotion 结论

```text
P0 status = PARTIAL
eligible training-completion claim = PRESENT / remote-snapshot-backed
eligible raw-rollout recount = PRESENT / 8 x 54 records
eligible checkpoint-binary claim = 0
eligible benchmark claim = 0
eligible ablation-uplift claim = 0
eligible ownership claim = 0
```

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| run identity | 单一 run name、output/checkpoint/normalizer path 一致 | `PRESENT` | 可以按 run family 讲，不与其它 30/100 epoch 混用 |
| training completion | 3930 steps、30 epochs、8/8 process exit success | `PRESENT` | 可说训练进程完成 |
| training metrics | `train.out` 有 41 个打印 point；derived verifier 声称读取 3930 records | `PARTIAL` | 直接可重算 41 点；完整 `train.jsonl` 未同步 |
| validation | `val_ratio=0`、`eval_every=0` | `ABSENT BY CONFIG` | 训练 loss 不能包装成 held-out metric |
| dataset contract | 18 tasks、9126 episodes、133457 sequences、seq 19、stride 16、12D action | `PRESENT` | 支持输入输出和 sampling contract |
| base load | 446 matched、8 action-head keys skipped、32 missing-after-partial-load、0 unexpected | `PRESENT / RESET-HEAD` | 证明迁移策略，不证明新 head 已学好 |
| produced checkpoint | summary 与 rollout 指向同一 `checkpoints/models.pt` | `REMOTE-REFERENCED` | 当前 snapshot 中 checkpoint-like binary 为 0 |
| normalizer | 本地 12D normalizer JSON 与 rollout path 对齐 | `PRESENT` | 可 hash；第 11 个重排维度 std=0 需保持 contract 解释 |
| raw rollout | 8 JSON×54 records，task/seed/scenario 可逐条复算 | `PRESENT` | 每个 config 的 denominator 完整 |
| environment health | 八组均 `num_env_errors=0` | `PRESENT` | 失败不是 env exception，但仍可能是 protocol/model failure |
| scorer | JSON 有 runtime `success` 与 per-task aggregation | `PARTIAL` | 缺 immutable RoboCasa/env/scorer revision 与 episode videos |
| ownership | Project commit、脚本和 Codex-derived verifier 存在 | `PENDING` | 不从路径、Git author 或工具生成 summary 推导个人独立实现 |

## 4. Frozen inputs 与 SHA-256

### 4.1 Run、preflight 与 aggregate files

| 文件 | SHA-256 | 用途 |
| --- | --- | --- |
| `logs/.../train.out` | `4C56A7181A912156C482D7982B7568FBAB1FE597DC25702B318D615BD3588B80` | 训练命令、打印 metrics、run summary、8-rank exit |
| `runs/.../train_summary.json` | `88EDF9D28C7EF5D40316A7C71DE0C8E932492257A50383397C497974568C8E93` | steps/epochs/dataset/checkpoint path/memory/load report |
| `runs/.../ds_config_effective.json` | `2BF8216F04391CE4323FC79AE74AAE9728E8B13F8D4057F281734A0A4DA54642` | global batch 1024、micro batch 128、ZeRO 0 |
| `runs/.../artifacts/dataset_ready.json` | `B9AF4A9118F83F466DACD1CBE0AE7F56A37BA0AB932E50BB992392A0571CB38B` | rank-0 dataset-ready marker |
| `runs/.../artifacts/target_atomic_seen_action_normalizer.json` | `27D2E8E24B3FDD43A841597D0CF3CF9CF322829FB28A26B663012338B1E48500` | 12D action normalizer |
| `sweep_summary.json` | `F4426789264BD5165363AD3F416B574C4C4ADB463D434C7C2182D428B835371F` | 八组 rollout aggregate |
| `sweep_summary_codex_verified.json` | `3AD967659D8208C2B67F0AE421E29353317BF067792878AEA14EF883B853BFC6` | tool-derived training/rollout reconciliation；不替代 raw files |
| `checkpoint_smoke.json` | `BC95D7EEFC162D7A0BEE432424FF80B982B05562A5D6755A44EC8528B99C39F4` | base UWM partial-load / reset-head preflight |
| `dataset_smoke.json` | `63A6DF7EE65C59560F2A58B2E73B13C8B52FBA91837FD1E3A7DE8B2D6681E681` | 三视角、state/action shape 与 task sample smoke |
| `save_smoke.json` | `5132415BA944C4DB7BC0E8FA992B537675FC73EB6DC51E598340A5073FCD9442` | 独立 10-step save smoke；不是本页 30-epoch binary |

本地代码快照：`uwm_robocasa_train.py` SHA `EFC53BB652302183F56B6F1BB9ACEB7ABDE31D01D953720EA1C05BB605A91FFE`；`uwm_robocasa_rollout.py` SHA `E43D3751F8D079DAC54C902B5B222A13242FF5A9CE0F3975FB00D630DA53775E`；evidence collector SHA `A0651BC6E1569A48D48F723770C86EC4FEF0290D62F89F7D32ACD5684856CC67`。Project HEAD 为 `6c524d9c6c6226075f100cdac395fef2fdc37671`，但 `remote_sync` 是本地缓存，commit 与路径都不能自动证明 candidate ownership。

### 4.2 Raw rollout files

| setting | raw JSON SHA-256 | bytes |
| --- | --- | ---: |
| full_h1 | `7FECC56D94A5BEBB44E78944015351F5E4B8EA7EFC684306204595B9F5EF5E44` | 197952 |
| full_h2 | `31310DB9852B4FF49F393C8066CFC71C713C639BEA57C23FCE38F561D1C4D2E7` | 200613 |
| full_h4 | `7284F7F3E713F1987A74041EA51B48B8EB8E7510A7E296CE695FBE1EA89B287E` | 200242 |
| full_h5 | `0CE505AA8D820B9F59432CC90C54869D691525FC726A183DAB234A6B827A0156` | 193888 |
| full_h8 | `7E9A6257D8993397E167EB6E2716A6C6558BFE334CA7CE3EDC627D7D0810E458` | 196528 |
| no_prompt_h5 | `A6CBE854FA7E3A06671EA148B82AE46AF702FBB5BCEF28130F7D58F5D4741B77` | 193775 |
| no_right_h5 | `F4A8D28921ABB82430D88BE85B1DA8BB706C2D9C470583A72C45CC3EBBDA2557` | 194197 |
| no_state_h5 | `933DBFDBA2DC1D67C6BE7E9FA18226DDE17BA80086C42511959EA2224B7BB740` | 198679 |

## 5. Preflight 与训练合同

### 5.1 Base-load / reset-head contract

base checkpoint 为远端 `libero_90.pt`、checkpoint step 100000。preflight 显示 `target_key_count=478`、`matched_count=446`、`skipped_count=8`、`unexpected=0`；被跳过的 8 个 key 是 7D→12D action encoder/decoder 的 weight/bias，且 `reset_action_head=true`。新增 task/prompt/state/right-view projection、action head 和 gripper phase head 共 32 个 missing-after-partial-load key，normalizer 也不从 base checkpoint 继承。

这说明 actionheadfix 的基本迁移逻辑是：保留能 shape-match 的 UWM trunk，重置 12D action I/O 与新增 conditioning 模块。它不证明这些新参数经过 30 epoch 后产生了稳健策略。

### 5.2 Dataset / observation / action contract

| 字段 | 值 |
| --- | --- |
| dataset | LeRobot `target_atomic_seen` |
| tasks / episodes / sequences | 18 / 9126 / 133457 |
| seq_len / stride | 19 / 16 |
| images | agentview + right-view + eye-in-hand，4 frames，224×224 |
| state | 16D：EEF relative pos/rot、base pos/rot、gripper qpos |
| action | 12D，indices `5,6,7,8,9,10,11,0,1,2,3,4` |
| condition | task ID + text prompt + state + right view |
| weighted loss | EEF-pos 2.0、EEF-rot 1.0、gripper 3.0、base 1.5、control 1.0 |
| train batch | 8 GPUs × micro-batch 128 = global batch 1024 |
| save policy | epoch 30，limit 1，remote `models.pt` path |

normalizer 的一个重排维度 `std=0`、scale=`1e-6`；这与源数据该维度恒为 0 相符，但它是重要的 action-contract 风险，不能在 adapter 或 action-order 改动时静默复用。

## 6. 训练完成与 metric 边界

`train.out` 可独立解析出 41 条打印 metric point：step 0、每 100 step 和 step 3929。首末值为：

| metric | step 0 | step 3929 |
| --- | ---: | ---: |
| total loss | 3.325663 | 0.253850 |
| action loss | 2.430044 | 0.076886 |
| raw action loss | 0.998558 | 0.030433 |
| epoch | 0.0076 | 30.0 |

日志末尾 8 个 rank 都是 `exits successfully`，没有 traceback 或 CUDA OOM。`sweep_summary_codex_verified.json` 另称读取了 3930 个 training record，并给出 tail-100 average；但原始 `runs/.../logs/train.jsonl` 没有同步到当前 snapshot，因此本页不把 tail-100 值升级为独立重算结果。

更关键的是，训练命令设置 `val_ratio=0`、`eval_every=0`。所以这张表只支持“optimizer 在训练分布上显著降低 loss”，不支持 held-out action accuracy、OOD generalization 或 closed-loop improvement。

## 7. Closed-loop protocol tuple

八组 raw JSON 的共同 tuple 为：

```text
task_set=atomic_seen
split=target
tasks=18
scenario_sampling=round_robin
scenarios=54 (3/task)
scenario/seed set identical across all 8 settings
action_mode=official12
adapter_mode=official12
action_execution_mode=convert_action
checkpoint=<same remote models.pt path>
normalizer=<same local-hashable 12D normalizer path>
env_errors=0
```

full settings只改变 `exec_horizon ∈ {1,2,4,5,8}`；三组 h5 ablation 分别屏蔽 prompt、right-view 或 state input。因为同一组 54 scenario 被重复评估，所以 432 records 不是 432 个独立 benchmark trial，不能把各 setting 的 success 简单相加。

## 8. 八组 raw rollout 独立重算

| setting | horizon | success / 54 | env errors | robot-env contact episodes | 成功 task / seed |
| --- | ---: | ---: | ---: | ---: | --- |
| full_h1 | 1 | 2 | 0 | 42 | TurnOnElectricKettle / 15, 33 |
| full_h2 | 2 | 1 | 0 | 47 | TurnOnElectricKettle / 33 |
| full_h4 | 4 | 0 | 0 | 45 | — |
| full_h5 | 5 | 1 | 0 | 43 | TurnOnMicrowave / 34 |
| full_h8 | 8 | 1 | 0 | 45 | TurnOnElectricKettle / 51 |
| no_prompt_h5 | 5 | 2 | 0 | 46 | TurnOnElectricKettle / 15, 33 |
| no_right_h5 | 5 | 2 | 0 | 45 | TurnOnElectricKettle / 15, 33 |
| no_state_h5 | 5 | 1 | 0 | 43 | TurnOnElectricKettle / 15 |

每份 raw JSON 都满足：54 records、18 unique tasks、每 task 3 records、54 unique seeds；field `num_successes` 与逐 record recount 完全一致；per-task aggregation 与 micro/macro summary 一致；八份 JSON 的 scenario/task/seed set 完全相同。

### 8.1 为什么不能声称 ablation 结论

full_h5 是 `1/54`，no-prompt/no-right 是 `2/54`，差值只有一个 episode，而且成功集中在单一 TurnOnElectricKettle task。缺多 seed repeat、checkpoint repeat 和置信区间时，不能说“去掉 prompt/right view 提升性能”，也不能据此证明这些输入无用。它只告诉我们：当前 success 稀疏，ablation signal 被单任务和单 episode 主导。

### 8.2 为什么 contact 不是 success

full_h4 的 45 个 episode 至少一次记录到 robot-env contact，但 54 个 episode全部失败。contact pair 可能是手、link、柜门、台面等几何接触；它没有包含任务谓词、目标物体状态或有效抓取/按键语义。因此接触率只能作为“策略是否靠近交互区域”的诊断 proxy，不能替代 RoboCasa success。

## 9. Train → Closed-loop first divergence

当前最稳健的链路判断是：

```text
base partial load passes
  -> 12D/action-state-view dataset smoke passes
  -> 30-epoch 8-GPU training exits cleanly
  -> training action/raw-action loss decreases
  -> same checkpoint and normalizer load into 8 rollout settings
  -> env execution has 0 exceptions
  -> task success remains 0–2 / 54 and concentrates in 1–2 tasks
```

这将 first divergence 收窄到“训练目标/teacher-forced action fit 到 long-horizon closed-loop control”之间，但不能唯一归因于 action head。仍可能包括：action semantics/normalizer 的细微错位、diffusion sampling误差、exec horizon、observation/state distribution shift、controller dynamics、gripper phase、recovery 缺失与 runtime scorer sensitivity。

## 10. Run-family 与 ownership 边界

| 相邻证据 | 与本页关系 | 不允许的 join |
| --- | --- | --- |
| Human300 pretrain / target continuation | 另一 curriculum/run family | 不把其 loss 或 checkpoint 当成本页 base/结果 |
| 100-epoch resume | 另一 checkpoint 与训练阶段 | 不用 `0/54` 或其它结果替代本页 30 epoch sweep |
| state_prompt_weighted strict/direct A/B | 另一 run 和 action bridge | 不把 `expected 12, got 5` 错误混入本页零 env-error denominator |
| LIBERO fixed-init `186/250` | user-confirmed remote summary、不同 benchmark | 不与 RoboCasa 54-scenario success 比较 |
| `sweep_summary_codex_verified.json` | 工具生成 reconciliation | 不把工具生成文件当 candidate ownership 或 raw source |

当前能认领到项目层的是：这条训练/评测运行发生过，run tuple 与失败断层可复核。个人“亲手实现/设计/运行/验收”的具体边界仍需用户按脚本、command、remote operator、analysis 和 reviewer 逐项确认。

## 11. 面试可用口径

### 30 秒版本

> 我在 UWM→RoboCasa 迁移里做过一条 actionheadfix 30-epoch run 的训练—评测审计。它把 LIBERO 7D action head 重置成 RoboCasa official12，并加入 task、prompt、16D state 和第三视角条件；8 卡跑完 3930 steps，训练 action loss 从打印点的 2.43 降到 0.0769。之后我固定同一 checkpoint、normalizer 和 18 task×3 scenario，扫了 h1/2/4/5/8 以及三组输入 ablation。八组都没有环境异常，但每组只有 0–2/54 success，h4 是 0/54；而 h4 有 45/54 episode 出现接触，说明接触和训练 loss 都没有转化为稳定任务完成。我把它定位为 train-to-closed-loop transfer failure，不宣称完成 RoboCasa benchmark。

### 高压追问：训练 loss 降这么多，为什么 rollout 还是几乎 0？

> 因为训练侧没有 validation，loss 是 teacher-forced 训练分布指标；closed-loop 会累积 observation shift、sampling error 和 controller/action-contract误差。当前证据已经排除了“训练进程没跑完”和“env 全部 crash”，但还没有排除 normalizer/action semantics、exec horizon、gripper phase和 recovery。正确下一步是固定一个 failure scenario，对 expert action、model x0、sampled 12D action、adapter 后 action和环境状态做逐步 first-divergence，而不是继续只压训练 loss。

### 高压追问：no-prompt 比 full-h5 高，是不是 prompt 有害？

> 不能。`2/54` 对 `1/54` 只差一个 episode，成功集中在 TurnOnElectricKettle，且只有一个 checkpoint/run。它可以作为下一轮 matched repeat 的假设，不能作为 prompt causality 或 ablation uplift。

### 禁用表述

1. “actionheadfix 已解决 RoboCasa transfer”；
2. “30 epoch 模型在 RoboCasa 达到 X% benchmark”——当前只是 18-task×3-scenario 项目协议；
3. “训练 loss 下降证明泛化提升”——没有 validation；
4. “prompt/right view 有害”——成功数过少且无 repeat；
5. “checkpoint 已在本地验证”——只有远端 path，本地没有 binary/hash/fresh reload；
6. “所有代码和实验都是我独立完成”——ownership 尚未确认。

## 12. 关闭 P0 的最小动作

1. 回传或登记 30-epoch `models.pt` 的 immutable SHA/ETag，做 fresh-process load 与 fixed-input parity；当前 snapshot checkpoint-like binary 为 0。
2. 同步完整 `train.jsonl`，独立重算 3930 training records；增加 held-out split 或固定 teacher-forced eval，避免只看训练点。
3. 冻结 RoboCasa、MuJoCo、controller、success predicate 与 env revision；保存 54 episode 的视频或可审计 locator。
4. 对相同 54 scenario、多个 checkpoint seed 重复 h5/full/no-prompt/no-right/no-state，报告 paired difference 与置信区间。
5. 选择 full-h4 的 matched failure case，记录 expert/model-x0/sampled/converted/executed action、state、contact 和 task predicate 的逐步 first-divergence。
6. 逐文件确认候选人对 train/rollout/dataset/evidence collector、远端运行和结果审查的 ownership；工具生成 summary 单列。

在这些字段闭合前，本页保持 `PARTIAL/WARN`：允许讲完整训练—评测失败链和协议工程，不允许讲 RoboCasa benchmark 已完成或训练取得稳定成功。

## References

1. `C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\logs\target_atomic_seen_official12_task_30epoch_muxi_20260628_openpi_state_3view_phase_30ep\train.out`。
2. `C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\runs\target_atomic_seen_official12_task_30epoch_muxi_20260628_openpi_state_3view_phase_30ep\` 下的 summary/config/normalizer。
3. `C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\logs\rollout_sweeps_atomic_seen_target\target_atomic_seen_official12_task_30epoch_muxi_20260628_openpi_state_3view_phase_30ep\` 下八份 raw rollout JSON 与 eval log。
4. `C:\Users\mousongzhe\Project\remote_sync\muxi_20260629\uwm_robocasa_transfer_muxi\diagnostics\openpi_state_3view_phase_20260628\` 下的 checkpoint/dataset/save smoke。
5. [UWM / LIBERO Claim–Evidence Inventory](uwm_libero_claim_evidence_inventory.html)。
6. [UWM / LIBERO P0 Bundle Audit](uwm_libero_p0_bundle_audit.html)。
7. [UWM / LIBERO / RoboCasa Transfer Evidence Freeze](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)。
8. [UWM Project Cards](../../questions/proj_uwm.html)。
