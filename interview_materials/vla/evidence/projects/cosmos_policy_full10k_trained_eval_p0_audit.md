# Cosmos Policy full10k trained checkpoint：RoboCasa 24×5 P0 评测证据审计

> 状态：`p0_audited / trained-run-remote-artifact-backed / checkpoint-unverified / scorer-policy-local / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计 `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts` 中 run id 为 `full10k-20260620-5ep-alltasks` 的 24 个 formal task；不把它与 8-GPU `max_steps=9907` gate、Cosmos official-HF baseline、TurnOffMicrowave local 1k failure 或 CoffeePressButton 1×1 smoke 合并为同一 run。

## 1. 问题（Question）

这份审计回答四个问题：full10k 训练 checkpoint path 是否实际进入了完整 24×5 RoboCasa eval；status、task log、summary 与 action-debug 是否互相对齐；raw `2/120` 与 trusted `0/118` 如何在面试中准确解释；以及哪些结果仍不能升级为 checkpoint ownership、benchmark 或训练 uplift。

## 2. 结论先行

当前 bundle 足够证明：一条独立的 full10k trained-run eval harness 已完成 24 个 task、每 task 5 个 episode；`formal_5ep_status.tsv` 的 24 行全部 `exit_code=0`；24 个 task log 与 conservative summary 的 task set、episode 数和 success 数一致；action-debug 的 24 个 formal JSONL 共 4066 行，全部可解析、`32×7`、finite，并且都指向同一个远端 `iter_000010000` checkpoint path。

独立重算得到：

```text
raw successes       = 2 / 120 = 1.6667%
artifact successes  = 2       (CoffeeServeMug episode 1/2, each length=1)
eligible episodes   = 118
trusted successes   = 0 / 118 = 0%
conservative rate   = 0 / 120 = 0%
```

这支持的面试口径是：“我把独立 full10k trained checkpoint path 接入了固定的 RoboCasa 24×5 eval，完成了日志、status、summary 和 action-debug 的交叉审计；原始日志有 2 条 CoffeeServeMug 的 length=1 immediate success，按当前本地审计规则排除后 trusted 是 `0/118`。”

它不支持：本地持有或 hash 了 checkpoint binary；证明 full10k 训练带来 benchmark uplift；把 `0/118` 写成 RoboCasa 官方统一 scorer 的结果；把 full10k 与 official-HF `84/118` 做因果比较；或从 launcher、远端路径、Git author 推导个人独立 ownership。

## 3. P0 promotion 结论

```text
P0 status = PARTIAL
eligible trained-run eval claims = PRESENT / remote-artifact-backed
eligible raw/trusted recount = PRESENT / local-policy-bounded
eligible local checkpoint claims = 0
eligible matched-uplift claims = 0
eligible ownership claims = 0
```

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| task coverage | `formal_5ep_status.tsv` 24 行、24 unique tasks、每 task 5 trials | `PRESENT` | 可称 full10k trained-run 的 24×5 formal eval |
| process completion | 24/24 formal rows `exit_code=0` | `PRESENT` | 进程正常退出，不等于策略成功 |
| task-log recount | 24 logs、120 episodes、2 successes | `PRESENT / independently recomputed` | 可报告 raw `2/120` |
| summary alignment | conservative JSON 24 rows 与 status task set 完全一致 | `PRESENT` | summary 不是 checkpoint ownership 证据 |
| artifact policy | CoffeeServeMug 两条 `SUCCESS:length=1` 被排除 | `LOCAL POLICY` | 只能称当前审计规则，不称官方通用定义 |
| trusted recount | 118 eligible episodes、0 trusted successes | `PRESENT / protocol-bounded` | 可报告 `0/118`，须同时说明 denominator 规则 |
| checkpoint identity | 4066 行 action-debug 都指向 `/data/msz/wm/outputs/cosmos_policy_wam_repro_full10k_20260619/.../iter_000010000` | `REMOTE-REFERENCED` | path 不是本地 binary、revision 或 hash |
| action-debug integrity | 24 files、4066 lines、`32×7`、`float64`、无 malformed/non-finite | `PRESENT` | 结构健康，不证明动作语义或 success 原因 |
| media completeness | 本地同步 14 个 media；archive 169 entries | `PARTIAL` | 不能当作 120 episode 完整 media bundle |
| scorer/version | log 有 SUCCESS/FAILURE/length；`length<5` exclusion 是本地 policy | `PARTIAL` | 仍缺 immutable scorer/version 与 raw episode JSONL |
| ownership | launcher、wrapper、远端 operator/reviewer 未逐文件确认 | `PENDING` | 不从路径或报告作者推导“我负责” |

## 4. Frozen inputs 与 SHA-256

| 文件 | SHA-256 | 用途 |
| --- | --- | --- |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\formal_5ep_status.tsv` | `7FCA2C1C57EEAD560D602A6F3CFAF6D0BE7C21F747AEF8F567662C66B2BEC55C` | 24 条 formal launcher/status 记录 |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\eval_summary_conservative.json` | `C9538A2E418BCBEDD88B8DCFB308F0E1AF428DBA2912A959DEA946872A3247BE` | conservative task/episode summary |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\eval_summary_conservative.csv` | `676062F1318ADF3CC7DE4188AE575878BA1A779EFBE7214CA49FE6F2341D06BB` | task-level CSV summary |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\dataset_statistics.json` | `BFEC3286EF23AADF19B42C33937118C540073C44F668BA012D9E8B773AA77E41` | action/proprio normalization source |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\dataset_stats_contract.json` | `D41BC62760B937939067958D4FAAE78F08CFD0D823C4BD74F9A10F7265B8EA8A` | action dim 7、proprio dim 9 contract |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\cosmos_policy_eval_light_20260620.tgz` | `853E2434EF48AA774FAB59C13EED663AA85364956AB3E3F50A76CEF4B2B715C3` | 169-entry light archive |

目录审计计数：`logs=25`、`stdout=25`、`action_debug=25`、`manifests=75`；其中各类 25/25 中有 1 份 CoffeePressButton smoke，24 份才进入本页 formal 主表。archive 为 `8,403,550` bytes、169 entries；本地同步 media 计数为 14，不能替代完整 120 episode 视频或 JSONL。

## 5. Protocol tuple

25 个 command manifest 共享同一运行合同；本页只取其中 24 个 `5ep-alltasks` formal manifest。

| 字段 | 冻结值 |
| --- | --- |
| host / GPU | `iv-yej2jeh2bkay8n70cofj` / `CUDA_VISIBLE_DEVICES=7` |
| seed | `195` |
| checkpoint path | `/data/msz/wm/outputs/cosmos_policy_wam_repro_full10k_20260619/cosmos_policy/cosmos_v2_finetune/cosmos_policy_wam_repro_full10k_20260619/checkpoints/iter_000010000` |
| stats / embeddings | `/data/msz/wm/cosmos_policy_stats_only/dataset_statistics.json` / `/data/msz/wm/outputs/cosmos_policy_robocasa_eval_20260620/reason1_eval_embeddings.pkl` |
| launcher / wrapper | `launch_cosmos_policy_robocasa_official_eval.sh` / `cosmos_policy_robocasa_official_eval_wrapper.py` |
| eval config | `cosmos_predict2p5_2b_480p_robocasa_50_demos_per_task__inference_no_s3` |
| observation | 2 third-person + 1 wrist image；proprio enabled |
| normalization / denoise | image flip + JPEG；normalize proprio；unnormalize action；action denoise 5 steps；shift 5 |
| action execution | `chunk_size=32`；`num_open_loop_steps=16`；action dim 7 |
| policy selection | deterministic；best-of-N queries 1；no parallel inference |
| robot/controller | `PandaMobile` / `OSC_POSE` |
| task split / layout | object split `B`；`((1,1),(2,2),(4,4),(6,9),(7,10))` |
| formal trials | 5 per task；`deterministic_reset=false` |

这组字段支持“协议固定/对齐”的叙事，不构成模型权重内容、训练有效性或个人 ownership 证据。

## 6. 独立重算与 task-level result

### 6.1 Recompute gates

| 检查 | 结果 |
| --- | --- |
| status rows / unique tasks / trial sum | `24 / 24 / 120` |
| status exit code | `24/24 = 0` |
| summary rows / task-set match | `24 / true` |
| formal task logs / task-set match | `24 / true` |
| log episodes / successes | `120 / 2` |
| action-debug files / lines | `24 / 4066` |
| malformed JSON / bad shape / non-finite / task mismatch | `0 / 0 / 0 / 0` |
| action shape / dtype / chunk / open-loop | `32×7 / float64 / 32 / 16` |

### 6.2 Task-level summary

| task | raw success / 5 | artifact excluded | eligible | trusted success |
| --- | ---: | ---: | ---: | ---: |
| CloseDoubleDoor | 0 | 0 | 5 | 0 |
| CloseDrawer | 0 | 0 | 5 | 0 |
| CloseSingleDoor | 0 | 0 | 5 | 0 |
| CoffeePressButton | 0 | 0 | 5 | 0 |
| CoffeeServeMug | 2 | 2 | 3 | 0 |
| CoffeeSetupMug | 0 | 0 | 5 | 0 |
| OpenDoubleDoor | 0 | 0 | 5 | 0 |
| OpenDrawer | 0 | 0 | 5 | 0 |
| OpenSingleDoor | 0 | 0 | 5 | 0 |
| PnPCabToCounter | 0 | 0 | 5 | 0 |
| PnPCounterToCab | 0 | 0 | 5 | 0 |
| PnPCounterToMicrowave | 0 | 0 | 5 | 0 |
| PnPCounterToSink | 0 | 0 | 5 | 0 |
| PnPCounterToStove | 0 | 0 | 5 | 0 |
| PnPMicrowaveToCounter | 0 | 0 | 5 | 0 |
| PnPSinkToCounter | 0 | 0 | 5 | 0 |
| PnPStoveToCounter | 0 | 0 | 5 | 0 |
| TurnOffMicrowave | 0 | 0 | 5 | 0 |
| TurnOffSinkFaucet | 0 | 0 | 5 | 0 |
| TurnOffStove | 0 | 0 | 5 | 0 |
| TurnOnMicrowave | 0 | 0 | 5 | 0 |
| TurnOnSinkFaucet | 0 | 0 | 5 | 0 |
| TurnOnStove | 0 | 0 | 5 | 0 |
| TurnSinkSpout | 0 | 0 | 5 | 0 |
| **合计** | **2 / 120** | **2** | **118** | **0 / 118** |

### 6.3 Artifact-success boundary

两条 raw success 都来自 `CoffeeServeMug` episode 1/2，日志标记为 `SUCCESS:length=1`。本地 conservative summary 将它们标为 `immediate_success_artifact`，所以 trusted 分母从 120 变为 118，trusted successes 为 0。`length<5` 是本地审计 policy；在 scorer/version、termination reason 与完整 episode JSONL 未冻结前，不能把它写成 RoboCasa 官方统一 invalid 定义。

## 7. Action-debug integrity

24 个 formal action-debug JSONL 共 4066 行，逐行 JSON 解析无 malformed；`action.shape=[32,7]`、`dtype=float64`、`chunk_size=32`、`num_open_loop_steps=16` 保持一致；对 action summary 与 `first_row` 做 finite 检查无 `NaN/Inf`；task name 与文件名无 mismatch。单文件行数范围为 95–315。

这只能证明 inference 输出的记录结构可读、形状和数值有限，不能证明 action normalization 的语义正确、控制器执行正确、策略学到了任务，或某个失败由单一模块造成。

## 8. 与相邻 run family 的分离

| run family | checkpoint / 运行线 | 本页关系 |
| --- | --- | --- |
| full10k trained eval（本页） | 远端 `iter_000010000`；单卡 GPU7；24×5；raw `2/120`、trusted `0/118` | 本页主证据 |
| official-HF baseline | `nvidia/Cosmos-Policy-RoboCasa-Predict2-2B`；24×5；raw `86/120`、trusted `84/118` | 外部 baseline；不能当本地成绩 |
| 8-GPU 1 epoch gate | `max_steps=9907`；save-2k cgroup OOM；save1500 `state_dict(destination=...)` first divergence | 未完成训练/save gate；不能用本页 eval 替代 |
| TurnOffMicrowave local 1k | local negative-only 1k；single-task `0/1` failure 与 same-input probe | 诊断 run；不并入本页分母 |
| CoffeePressButton smoke | 1×1 smoke | 本地目录中的代表性 smoke；不进入 24×5 主表 |

没有共同的 checkpoint binary/hash、config/data/stats immutable manifest、scorer version 与 episode-level paired join，因此不能计算 full10k 相对 official-HF 的 uplift，也不能把 `2/120` 或 `0/118` 与其它 run 族拼成一条训练曲线。

## 9. 面试可用与禁用表述

### 30 秒回答

> 我把 full10k trained run、official-HF baseline 和 8 卡 1 epoch gate 分开管理。对 full10k 的远端 `iter_000010000` path，我跑了 RoboCasa 24 个 task、每 task 5 个 episode，24 条 formal status 全部正常退出；从 task logs 独立重算是 raw `2/120`。两条 success 都是 CoffeeServeMug 的 length=1 immediate artifact，按当前本地 policy 排除后是 trusted `0/118`。我还核了 24 个 action-debug JSONL，4066 行全部 `32×7` 且 finite。这个结果证明评测链和审计闭环，不证明 benchmark uplift、官方 scorer 等价或本地 checkpoint binary ownership。

### 高压追问：为什么不是直接报告 2/120？

> `2/120` 是 raw log 口径，我不会隐藏它。因为两条成功都在 length=1，conservative summary 把它们标成 immediate artifact；如果采用这份本地审计 policy，eligible denominator 是 118，trusted success 是 `0/118`。这不是 RoboCasa 官方统一定义，所以我同时保留 raw 和 trusted，并把 scorer/version 与完整 episode JSONL 列为 P0 缺口。

### 高压追问：full10k 比 official-HF 差多少？

> 目前不能给因果差值。两者 checkpoint identity、revision、raw episode bundle、scorer/invalid policy 和 ownership 还没有完全 matched；能说的是本页 full10k trained-run audit 为 raw `2/120`、local trusted `0/118`，official-HF audit 为 raw `86/120`、local trusted `84/118`。这两组数字必须标注 run family，不能把后者写成本地模型成绩。

### 禁用表述

| 不安全说法 | 原因 | 安全替代 |
| --- | --- | --- |
| “full10k 在 RoboCasa 是 0%” | `0/118` 是本地 invalid policy，不是官方 scorer | “按当前本地 policy，trusted 为 `0/118`；raw 为 `2/120`。” |
| “我的模型达到 71.19%” | `84/118` 属于 official-HF path | “我运行并审计了 official-HF baseline，不把它归因于训练模型。” |
| “训练提升/下降了 X%” | 没有 matched paired eval | “当前只有跨 run 的分布对账，不能宣称 uplift。” |
| “checkpoint 已保存并验证” | 当前只有远端 path，无 binary/hash/reload parity | “action-debug 与 manifest 引用了远端 path，checkpoint gate 仍未闭合。” |

## 10. 关闭 P0 的最小动作

1. 回传 `iter_000010000` checkpoint binary 或 immutable revision/ETag/SHA，并做 fresh-process load parity。
2. 冻结训练 config、代码 revision、dataset/statistics/embedding SHA 与 run manifest，确认 full10k 训练日志和 eval 的 lineage。
3. 保存 120 个 episode 的原始 JSONL（termination、length、success predicate、error）并给 `length<5` policy 一个版本化 scorer；保留 raw 与 trusted 两套结果。
4. 完整同步 episode media 或至少提供每条 episode 的可核验 media locator；当前 14 个 local media 不是完整 bundle。
5. 逐文件确认 launcher、wrapper、协议 patch、operator 与 reviewer 的候选人角色。
6. 若要写 uplift，用同一 checkpoint lineage、stats、seed/init、controller、task/layout、scorer 和 24×5 denominator 做 paired eval；在此之前保持 `WARN`。

## References

1. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\formal_5ep_status.tsv`。
2. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\eval_summary_conservative.json` 与 `eval_summary_conservative.csv`。
3. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\logs\ENV_EVAL-*.txt`（24 formal task logs；另有 1 份 smoke）。
4. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\action_debug\*.jsonl`（24 formal action-debug files）。
5. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\remote_artifacts\manifests\*_command.txt`（24 formal + 1 smoke）。
6. [Cosmos Policy RoboCasa Official-HF Baseline P0 Audit](cosmos_policy_robocasa_baseline_p0_audit.html)。
7. [Cosmos / WAM 1 epoch–full10k Run Reconciliation](../../sources/vol_04_cosmos_policy_wam_full10k_run_reconciliation.html)。
8. [WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
9. [VOL 07 五项目证据 Reconciliation](../../sources/vol_07_project_evidence_reconciliation.html)。
