# Cosmos Policy RoboCasa Official-HF Baseline：P0 评测证据审计

> 状态：`p0_audited / remote-artifact-backed / checkpoint-unverified / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计 `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts` 的 official-HF RoboCasa 5-episode-per-task 评测；不把官方 checkpoint 结果写成本地训练 checkpoint 的 uplift，也不改变题卡 `unseen`。

## 1. 结论先行

这批材料已经足够证明一条完整的 **official-HF inference/eval harness** 运行链：24 个 task、每 task 5 个 episode，所有 24 条 formal status 行的 `exit_code=0`；25 个日志中另有一个 CoffeePressButton 1×1 smoke，不计入 24×5 主表。独立从 24 个 raw task log 重算得到：

```text
raw = 86 / 120 = 71.6667%
artifact-successes excluded = 2
trusted = 84 / 118 = 71.1864%
task logs = 24
action-debug files = 24, total JSONL lines = 2692, non-finite bundles = 0
```

这支持的面试口径是：“我运行并审计了 Cosmos Policy 官方 HF RoboCasa baseline 的 24×5 eval，固定了 checkpoint/model-card path、stats/T5、5-step action denoise、chunk/open-loop、seed、controller、layout 与 success predicate，并重算了 raw/trusted denominator。”

它仍不支持：本地保存并 hash 官方 checkpoint、把 `84/118` 归因于个人训练、与 1 epoch/full10k checkpoint 做 uplift、或把 24×5 official-HF baseline 当成个人模型成绩。

## 2. P0 promotion 结论

```text
P0 status = PARTIAL
eligible protocol/eval claims = PRESENT
eligible local checkpoint claims = 0
eligible causal-uplift claims = 0
eligible ownership claims = 0
```

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| task coverage | 24 条 `formal_5ep_status.tsv` 行，task 均 5 trials | `PRESENT` | 可称 24×5 formal eval |
| process completion | 24/24 `exit_code=0` | `PRESENT` | 运行过程正常退出，不等于模型成功 |
| raw success | 24 个 task log 的 `Total successes` 合计 86/120 | `PRESENT / independently recomputed` | 可报告 raw 口径 |
| invalid/artifact policy | 2 个 CoffeeServeMug success 的 length=1 被排除 | `PRESENT` | trusted denominator=118；需明确这是本地审计规则 |
| trusted success | 84/118 | `PRESENT / protocol-bounded` | 不与论文或本地训练 run 自动可比 |
| checkpoint identity | 每条 log 为 `nvidia/Cosmos-Policy-RoboCasa-Predict2-2B` path；bundle 内无 `.pt/.pth/.safetensors/.bin/.ckpt` | `REMOTE-REFERENCED` | path 不是本地 binary/hash |
| model/statistics revision | stats/T5 path 与 ckpt path 固定字符串 | `PARTIAL` | 未形成不可变 revision+SHA manifest |
| raw episode media | 24 task logs、selected rollout manifest 与拷回的视频索引 | `PARTIAL` | selected videos 不是完整 120 episode media bundle |
| scorer / success predicate | log 中有 success/length 与 task aggregate | `PARTIAL` | 独立 scorer commit、invalid policy version、环境版本仍缺 |
| ownership | logs/launcher/wrapper 有来源，但没有候选人逐文件确认 | `PENDING` | 不能从路径或 Git author 推导个人贡献 |

## 3. 原始输入与 SHA-256

| 文件 | SHA-256 | 用途 |
| --- | --- | --- |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\eval_summary_officialhf_baseline.json` | `7B211B9D6F20BC95986A77C3CC901814AB6A705065016D7F68B67548BA6CACE9` | 结构化 totals/task summary/selected video 索引 |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\eval_summary_officialhf_baseline.csv` | `4751FDDBFE73CA237220C171A6C8D560069D31948643DF05820426FCA7A12B63` | task-level CSV 摘要 |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\formal_5ep_status.tsv` | `8B3BAEE9029340387AE803E48152C301C0F6C679461FCF132AF5E6B5E612124E` | 24 条 formal launcher/status 记录 |
| `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\selected_rollouts_manifest.json` | `126F006B952E988512BF88631BC01A8ACF46F38AA54119E6479C3BED9419C566` | 8 个精选 rollout/failure 视频索引，不是完整 episode bundle |

目录级只读计数：`logs=25`（24×5 + 1×1 smoke）、`action_debug=25`（主表 24）、`stdout=25`、`manifests=75`（每 task 3 类 manifest 文件）。bundle 内没有本地 checkpoint binary。

## 4. Protocol tuple

24 条主表日志的首行配置保持一致：

| 字段 | 冻结值 |
| --- | --- |
| model/checkpoint path | `nvidia/Cosmos-Policy-RoboCasa-Predict2-2B` |
| experiment | `cosmos_predict2_2b_480p_robocasa_50_demos_per_task__inference` |
| stats / T5 | `robocasa_dataset_statistics.json` / `robocasa_t5_embeddings.pkl` |
| cameras / proprio | 2 third-person + 1 wrist；proprio enabled |
| image / normalization | flip images、JPEG compression、normalize proprio、unnormalize actions |
| denoising | action 5 steps；future/value 1 step |
| action execution | `chunk_size=32`、`num_open_loop_steps=16`、action dim 7 |
| selection | deterministic、`num_queries_best_of_n=1`、no parallel inference |
| robot/controller | `PandaMobile` / `OSC_POSE` |
| task split/layout | `obj_instance_split=B`；`((1,1),(2,2),(4,4),(6,9),(7,10))` |
| trials/seed | 5 per task；logs use seed 195 |

这些字段支持“协议对齐”叙事；它们不构成模型权重内容或个人训练 ownership 证据。

## 5. 独立重算结果

### 5.1 Task-level trusted table

| task | raw successes / 5 | artifact successes excluded | trusted denominator | trusted rate |
| --- | ---: | ---: | ---: | ---: |
| CloseDoubleDoor | 5 | 0 | 5 | 100% |
| CloseDrawer | 5 | 0 | 5 | 100% |
| CloseSingleDoor | 5 | 0 | 5 | 100% |
| CoffeePressButton | 5 | 0 | 5 | 100% |
| CoffeeServeMug | 3 | 2 | 3 | 33.33% |
| CoffeeSetupMug | 2 | 0 | 5 | 40% |
| OpenDoubleDoor | 2 | 0 | 5 | 40% |
| OpenDrawer | 4 | 0 | 5 | 80% |
| OpenSingleDoor | 5 | 0 | 5 | 100% |
| PnPCabToCounter | 1 | 0 | 5 | 20% |
| PnPCounterToCab | 4 | 0 | 5 | 80% |
| PnPCounterToMicrowave | 2 | 0 | 5 | 40% |
| PnPCounterToSink | 3 | 0 | 5 | 60% |
| PnPCounterToStove | 3 | 0 | 5 | 60% |
| PnPMicrowaveToCounter | 4 | 0 | 5 | 80% |
| PnPSinkToCounter | 3 | 0 | 5 | 60% |
| PnPStoveToCounter | 2 | 0 | 5 | 40% |
| TurnOffMicrowave | 5 | 0 | 5 | 100% |
| TurnOffSinkFaucet | 5 | 0 | 5 | 100% |
| TurnOffStove | 0 | 0 | 5 | 0% |
| TurnOnMicrowave | 5 | 0 | 5 | 100% |
| TurnOnSinkFaucet | 5 | 0 | 5 | 100% |
| TurnOnStove | 3 | 0 | 5 | 60% |
| TurnSinkSpout | 5 | 0 | 5 | 100% |
| **合计** | **86 / 120** | **2** | **118** | **84 / 118 = 71.1864%** |

### 5.2 Artifact-success exclusion

被排除的两个 success 都来自 `CoffeeServeMug`：episode 1 与 episode 2 的 log length 均为 `1`。它们计入 raw `86/120`，但不进入 trusted `84/118`。这里的 `length<5` 是当前本地审计规则，不应在没有 scorer/version 记录时写成 RoboCasa 官方通用定义。

### 5.3 Action-debug integrity

对 24 个 `*-5ep-alltasks-*.jsonl` 独立解析：共 `2692` 行；每行 action shape 均为 `32×7`；数值摘要与 `first_row` 中未发现 `NaN/Inf`。这说明 action-debug 文件结构和 finite 检查可复核，但不等于 action 语义正确或 episode success 的因果解释。

## 6. 面试可用口径

### 30 秒版本

> 我先把 official-HF baseline 和自己的训练 run 分开。基于固定的 Cosmos Policy RoboCasa inference contract，我跑了 24 个 task、每 task 5 个 episode；24 条 formal status 全部正常退出。按 raw log 独立重算是 `86/120`，其中 CoffeeServeMug 有两个 length=1 的 artifact success，按审计规则排除后是 `84/118=71.19%`。我还核了 24 个 action-debug JSONL，2692 行都是 `32×7` 且 finite。这个结果证明我跑通并审计了 eval harness，不是我训练 checkpoint 的 uplift；官方 checkpoint 在当前 bundle 中仍只有远端 path，没有本地 binary/hash。

### 高压追问：`84/118` 是不是你的模型成绩？

**强回答：**

> 它是 official-HF checkpoint path 下的 baseline eval summary，不是我 1 epoch 或 full10k 训练 checkpoint 的结果。`86/120` 与 `84/118` 的差异来自本地审计里对两个 length=1 success artifact 的 trusted denominator 处理；我会同时报告两个口径并解释排除规则。可以认领的是 launcher、协议固定、日志重算和 action-debug integrity audit；不能认领官方权重训练、结果 uplift 或 checkpoint ownership。要比较本地训练模型，必须拿到同一 checkpoint lineage、同一 scorer/invalid policy、同一 24×5 denominator 和 paired raw episode bundle。

### 高压追问：为什么不能直接拿 71.19% 和论文数字比？

因为仍需确认论文/模型卡的 checkpoint revision、task/layout/init/seed、success scorer、artifact policy 和 trial denominator 完全一致。当前页只冻结本地 remote-artifact eval 的 protocol tuple，不宣称论文 strict reproduction。

## 7. 关闭 P0 的最小动作

1. 保存 official checkpoint、stats、T5 embedding 的 immutable revision/ETag/SHA manifest，或保留可审计的远端 revision identity。
2. 把 `length<5` invalid/artifact policy 固定成带版本的 scorer contract，并保留原始 episode JSONL。
3. 将 120 个 episode 的 raw success/termination/error manifest 与选定视频索引对齐；当前 8 个 selected videos 不能替代完整 bundle。
4. 逐文件确认候选人负责的 launcher、wrapper、protocol patch、运行者与 reviewer；不要从远端路径或 Git author 推导 ownership。
5. 若要写 uplift，必须与本地训练 checkpoint 做 matched 24×5 paired eval；当前没有这样的因果 join。

在这些字段闭合前，本页保持 `PARTIAL/WARN`：允许讲评测协议、日志重算与失败分布，不允许讲个人模型达到 `71.19%` 或“训练提升了 baseline”。

## References

1. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\eval_summary_officialhf_baseline.json`。
2. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\formal_5ep_status.tsv`。
3. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\logs\ENV_EVAL-*-officialhf-predict2-20260620-5ep-alltasks-*.txt`（24 条 task logs）。
4. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\baseline_remote_artifacts\action_debug\*-officialhf-predict2-20260620-5ep-alltasks-*.jsonl`（24 个 action-debug JSONL）。
5. [Cosmos / WAM 1 epoch–full10k Run Reconciliation](../../sources/vol_04_cosmos_policy_wam_full10k_run_reconciliation.html)。
6. [WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
