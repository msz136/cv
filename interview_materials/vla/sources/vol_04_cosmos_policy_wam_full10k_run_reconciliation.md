# VOL 04 Cosmos Policy / WAM：1 epoch gate 与 full10k 运行族对账

> 状态：`local_evidence_reconciliation / run_families_separated / WARN`  
> 复核日期：2026-07-21  
> 范围：只对账本地 `Project/report/cosmos_wam_repro` 中的独立 full10k WAM 复现与 `cosmos_policy_eval` 下的 1 epoch gate；不把两个 run family 合并成单一因果结果，也不改变题卡 `unseen` 或 ownership。

## 1. 结论先行

仓库此前把两条不同的 Cosmos/WAM 运行族压缩成“1 epoch 未完成”一条叙事，容易漏掉一条重要事实：

1. `cosmos_policy_eval/muxi_deepspeed_1epoch_20260623` 的 8-GPU、`max_steps=9907` gate，确实在 save-2k 主线遇到 cgroup OOM；no-cycle 修复后的正式 run 又在 step 1500 的 `state_dict(destination=...)` 保存接口处失败。该 run family 没有可用于本轮 eval 的可加载 checkpoint。
2. 独立的 `report/cosmos_wam_repro/cosmos_policy_wam_repro_full10k_20260619.log` 记录了另一个 batch-1、单卡 GPU7 的 full10k run：step 10000 loss=`0.0543`，checkpoint 写入远端路径，trainer `Done with training` 且 `EXIT:0`。
3. 同一 full10k report 登记了 CoffeePressButton、1 episode、`max_steps_override=120` 的 RoboCasa smoke，结果 `0/1`；后续独立 remote-artifact bundle 又冻结了同一 `iter_000010000` path 下的 24×5 formal eval：24/24 process `exit_code=0`，raw `2/120`，两条 CoffeeServeMug length=1 immediate success 按当前本地 policy 排除后 trusted `0/118`。这支持“full10k 训练与正式评测链路均跑通并可审计”，但不能升级为官方 benchmark、成功率 uplift、官方 scorer 等价或本地 checkpoint binary/hash 已核验。

因此面试中应明确说“两个 run family”：**1 epoch gate 的保存失败**与**独立 full10k repro 的远端 checkpoint path + 1×1 smoke + 24×5 formal eval**不能互相替代。

## 2. Run-family 对账表

| run family | 本地证据入口 | 训练事实 | eval 事实 | 当前能否称为完整结果 |
| --- | --- | --- | --- | --- |
| 1 epoch gate | `Project/report/cosmos_policy_eval/muxi_deepspeed_1epoch_20260623` | 8 GPU、global batch 128、`max_steps=9907`；save-2k 在 step 1903 后 cgroup OOM；no-cycle 正式 run 在 step 1500 保存接口失败 | 本轮没有对应可加载 checkpoint/eval bundle | `NO / WARN` |
| full10k repro | `Project/report/cosmos_wam_repro` + `Project/report/cosmos_policy_eval/remote_artifacts` | 单卡 GPU7，`MAX_ITER=10000`；step 10000 loss=`0.0543`；日志记录 checkpoint saved 与 `EXIT:0` | CoffeePressButton 1×1 smoke `0/1`；同一远端 `iter_000010000` path 下24×5 raw `2/120`、local-policy trusted `0/118` | `PARTIAL / WARN` |
| 官方/其他 baseline | 同目录 report 与独立 eval 产物 | 不是上述两条训练 run 的 continuation | 只能作外部 protocol 参照 | `NO causal join` |

## 3. Full10k 证据冻结

### 3.1 原始文件与 SHA-256

| 文件 | SHA-256 | 支持的事实 |
| --- | --- | --- |
| `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\cosmos_policy_wam_repro_full10k_20260619.log` | `403604E8A1C2F77041E5E1ED43B80AE0BDD2630911D8DB1645B6FB6D0F0443EC` | `MAX_ITER=10000`、step 10000 loss、checkpoint path、`Done with training`、`EXIT:0` |
| `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\remote_probe_summary.txt` | `0005153BD899CC16BC7769B47C01B3AA201AAC22BE762424E48222A181C17BC2` | checkpoint 完成摘要、loss JSONL 已回传、CoffeePressButton `0/1` 与 eval 输出路径 |
| `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\cosmos_wam_repro_report.html` | `12BE6C510EC5AF583B571B80B92FC98EB7F63217B543F7CD62CA05B9DF3075D6` | report 对 full10k、loss breakdown、eval smoke 的结构化汇总 |
| `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\loss_breakdown_full10k.jsonl` | `B6CEB4459C8CB5A00AADF3AE7F00F440DC359111B143FE44D5AF21CCB639BDDE` | full10k loss JSONL；report 说明每 iteration 有两个 callback 副本并按 iteration 去重 |

### 3.2 可复核的训练指标

- run name：`cosmos_policy_wam_repro_full10k_20260619`。
- `MAX_ITER=10000`、`BATCH_SIZE=1`、`NUM_WORKERS=1`，日志指向远端 `/data/msz/wm/outputs/...`。
- step `10000`：训练日志显示 `Loss: 0.0543`；report 同时给出 full10k 首末与平均分支诊断：demo action MSE `0.677 → 0.026`、world image MSE `0.787 → 0.159`、value MSE `0.707 → 0.003`，全程平均约 `0.087/0.128/0.069`。
- `Saving last checkpoint file iter_000010000` 后记录 `Saved checkpoint to .../checkpoints/iter_000010000`、`Done with training`、`EXIT:0`。

这些数字是 full10k 这条 run 的训练/诊断证据，不是 8-GPU 1 epoch gate 的最终 loss，也不是闭环成功率。

## 4. Full10k eval：从 1×1 smoke 到 24×5 formal audit

`remote_probe_summary.txt` 与 report 一致登记：CoffeePressButton、1 episode、`max_steps_override=120`、success `0/1`，并回传 `ENV_EVAL-CoffeePressButton-full10k-official-eval-smoke.txt`、`full10k_rollout.mp4` 与 `full10k_with_future_img.mp4`。后续 [Full10k Trained Eval P0 Audit](../evidence/projects/cosmos_policy_full10k_trained_eval_p0_audit.html) 对 `Project/report/cosmos_policy_eval/remote_artifacts` 做了独立只读审计：24 unique tasks、120 episodes、24/24 formal `exit_code=0`；24 个 task log 重算为 raw `2/120`；两条 raw success 都是 CoffeeServeMug episode 1/2 的 `SUCCESS:length=1`，按当前本地 policy 排除后为 trusted `0/118`。

合并这两层证据后，可以支持四件事：

1. full10k checkpoint reference 能进入一次最小 RoboCasa eval smoke；
2. 同一远端 `iter_000010000` path 能进入 24×5 formal eval，status/log/summary task set 与 denominator 对齐；
3. 24 个 action-debug JSONL 共 4066 行，全部 `32×7`、finite，并指向同一远端 checkpoint path；
4. raw `2/120` 与 local-policy trusted `0/118` 两种口径可独立重算，且 denominator 变化有明确的两条 length=1 artifact 记录。

它仍不支持：把 `0/118` 称为 RoboCasa 官方统一 scorer 的 benchmark、与 official-HF `84/118` 做严格因果差值、full10k 相对 base 的 uplift、checkpoint binary/hash 与 fresh-process reload 的本地重算，或个人独立 ownership。目录中的 14 个本地 media 也不是完整 120 episode bundle。

## 5. 与 1 epoch gate 的关系

`vol_04_cosmos_policy_1epoch_evidence_freeze` 仍然正确描述 8-GPU `9907`-step gate 的 OOM 与保存接口失败；本页只是补充另一条独立的 full10k repro。两者不能用字符串“full10k”或“iter_000010000”直接 join，因为：

- run name、日期、目录和 batch/硬件不同；
- 1 epoch gate 的远端输出位于 `cosmos_policy_eval/muxi_deepspeed_1epoch_20260623`，full10k 位于 `cosmos_wam_repro`；
- 没有共同的 checkpoint hash、config SHA、dataset revision、normalizer/statistics manifest 和同一 eval denominator。

推荐的 interview phrasing 是：

> “我有两条需要分开讲的证据：一条是 8 卡、global batch 128 的 9907-step 单 epoch gate，定位了 dataloader cgroup OOM 和 state_dict 保存兼容性；另一条是独立的 full10k WAM repro，日志显示 step 10000 loss 0.0543、远端 checkpoint 保存成功，先在 CoffeePressButton 1×1 smoke 中得到 0/1，后续同一路径的 24×5 formal eval 重算为 raw 2/120、按当前本地 policy trusted 0/118。后者证明训练和评测链路可运行并可审计，不等于官方 benchmark 或 uplift，也不能替代前一条 gate 的 save/load 闭环。”

## 6. 仍未闭合的 P0 字段

| 字段 | full10k 当前状态 | 下一动作 |
| --- | --- | --- |
| checkpoint binary/hash | 只有远端 path 与 saved log；本地未保存 binary/hash | 回传不可变 manifest 与 SHA-256 |
| reload smoke | 当前 report 未给出新进程 load parity | 1-step save→销毁进程→load→fixed-input parity |
| eval denominator | 24×5 status/log/summary 已对齐，raw `2/120`、local-policy trusted `0/118`；完整 episode JSONL 与 scorer version 仍缺 | 固定 scorer/invalid policy、termination/error 与120条 raw episode records |
| config/data/normalizer SHA | report 有脚本和摘要，但未形成 run-specific immutable manifest | 记录 code/config/data/stats revision |
| ownership | report/日志存在不等于候选人逐文件 ownership | 按 WAM ownership ledger 逐项确认 |

## 7. 结论与禁止升级

当前可以升级的项目叙事是“完成了一条独立 full10k 训练—1×1 smoke—24×5 formal eval 的审计链，并保留了 8-GPU 1 epoch gate 的系统排障链”。仍禁止写成：

1. “我完成并严格复现了 8-GPU 9907-step 1 epoch，并得到 full10k 的 loss/成功率”；
2. “Cosmos Policy full10k 在 RoboCasa 官方 benchmark 成功率为 0%”——当前只能说 raw `2/120`、按本地 policy trusted `0/118`；
3. “训练 loss 下降导致 benchmark uplift”；
4. “远端 checkpoint path 就是本地已验证权重”；
5. “报告中的脚本、日志或 Git author 自动等于个人独立实现”。

## References

1. `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\cosmos_wam_repro_report.html`（本地 report，full10k 与 eval smoke 汇总）。
2. `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\remote_probe_summary.txt`（full10k checkpoint/eval 摘要）。
3. `C:\Users\mousongzhe\Project\report\cosmos_wam_repro\cosmos_policy_wam_repro_full10k_20260619.log`（原始训练日志）。
4. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623`（8-GPU 1 epoch gate source freeze）。
5. [Cosmos Policy 1 Epoch Evidence Freeze](vol_04_cosmos_policy_1epoch_evidence_freeze.html)。
6. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
7. [Cosmos Policy full10k Trained Eval P0 Audit](../evidence/projects/cosmos_policy_full10k_trained_eval_p0_audit.html)。
