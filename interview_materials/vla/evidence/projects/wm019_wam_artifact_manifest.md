# WM-019 WAM Diagnostic Artifact Manifest（CoffeePressButton）

> 状态：`manifested / local-artifacts-partial / checkpoint-unverified / WARN`  
> 盘点日期：2026-07-18  
> 证据截止：2026-07-18  
> 范围：只登记一组 `CoffeePressButton` WAM action-rollout diagnostic bundle 的本地文件、manifest 字段和缺口；不把它升级为完整 benchmark、训练结果、个人 uplift 或 checkpoint-verified run。

## 1. 结论先行

当前工作区外部项目目录存在一组可直接读取的 WAM diagnostic artifact：base/trained 两个 rollout `manifest.json`、两个 `actions.jsonl`、base/trained raw video 与共同 rollout log。两个 manifest 都记录 `task=CoffeePressButton`、`episode_idx=0`、`seed=195`、`env_seed=0`、`max_steps=300`、`num_open_loop_steps=16`、`num_denoising_steps_action=5`，并记录 `success=false`。

但 manifest 中的 base checkpoint 与 trained checkpoint 都是 `/data/msz/...` 路径；在当前 Windows 工作区没有对应 checkpoint binary。trained raw video 已在同一 Project 下的 `cosmos_policy_robocasa_action_rollout_20260605` 目录找到，其 SHA 与 manifest 记录的远端文件名相符，但 output root 与 action-trace目录分离。因此本 manifest 的证据等级是 `local-direct artifact bundle + checkpoint-unverified`，不是完整可复算的 model comparison。

## 2. Bundle identity

```text
project_root = C:\Users\mousongzhe\Project\wm\outputs
task         = CoffeePressButton
episode_idx  = 0
seed         = 195
env_seed     = 0
max_steps    = 300
open_loop    = 16
denoise      = 5
controller   = OSC_POSE / control_delta=true
cameras      = robot0_agentview_left, robot0_agentview_right, robot0_eye_in_hand
```

Manifest 还记录三路 camera 为 `224×224`、PandaMobile、`obj_instance_split=B` 和单个 `[1,1]` layout/style id。action JSONL 的前 3 条记录包含 `policy_action7`、扩展后的 `env_action`、reward、done 和 `success_after_step` 字段；这支持 action/step trace 的存在，不支持任务整体成功率。

## 3. Immutable file inventory

| role | local path | bytes | SHA-256 | 当前可支持 |
| --- | --- | ---: | --- | --- |
| base manifest | `C:\Users\mousongzhe\Project\wm\outputs\cosmos_policy_fourway_robot_eval_20260605\action_base\CoffeePressButton--action_rollout--2026_06_05-23_59_36\manifest.json` | 3901 | `63A518674F061D1C14A880805FF9C23DAC2425C9D7B34CC4C75FD3CEDBD33A86` | base checkpoint 引用、task/seed/horizon/controller/camera 字段、`success=false` |
| base action trace | 同一目录 `actions.jsonl` | 126118 | `C6A3623B26B97F7ED88AA13AE675C8315DC509D3D867CBB6E417CAF51F88525D` | per-step `policy_action7/env_action/reward/done/success_after_step` |
| base raw video | 同一目录 `2026_06_05-23_58_51--episode=0--success=False--task=press_the_button_on_the_coffee_machine_to_serve_coffee.mp4` | 419966 | `D469A8B2CB3686C07C888B637009EE06D8DA10F2B2AEA2A5F3B186AD2E62F388` | 一条失败 episode 的本地视频文件 |
| trained manifest | `C:\Users\mousongzhe\Project\wm\outputs\cosmos_policy_fourway_robot_eval_20260605\action_trained\CoffeePressButton--action_rollout--2026_06_05-22_00_19\manifest.json` | 3918 | `809AE4F879C9421F954C7BFC26C70005B94387412449039F9FA8B6E479EF55CC` | trained checkpoint 引用、同一 task/protocol 字段、`success=false` |
| trained action trace | 同一目录 `actions.jsonl` | 128770 | `9C6A4F00DA8107EB0C1FDDDC642D1986CD510D92F7F6E3A68ADE834E8B82CF2D` | trained per-step action trace |
| trained raw video | `C:\Users\mousongzhe\Project\wm\outputs\cosmos_policy_robocasa_action_rollout_20260605\CoffeePressButton--action_rollout--2026_06_05-22_00_19\2026_06_05-21_59_38--episode=0--success=False--task=press_the_button_on_the_coffee_machine_to_serve_coffee.mp4` | 398103 | `59176353B1E069C6F3A3A20BDF13EE6A9FFD969537C5501B685293D87802877E` | 另一输出 root 的同名 trained 失败视频；需保留 root reconciliation |
| rollout log | `C:\Users\mousongzhe\Project\wm\outputs\cosmos_fourway_robot_eval_20260605_pack\logs\cosmos_action_rollout_trained_20260605.log` | 157555 | `1944896104A97BD9F867E3AD39F53CCB407226E0E942E56AD5545B0AB2A27143` | 运行时模块、`NUM_ACTIONS_CHUNK=32`、`ACTION_DIM=7` 等日志线索 |

## 4. Checkpoint 与 provenance gate

| 字段 | base | trained | 结论 |
| --- | --- | --- | --- |
| manifest checkpoint | `/data/msz/models/cosmos_predict2p5_2b_base/base/pre-trained/308eb96c-c4c0-4a06-9cc1-103a43beff28/model_ema_bf16.pt` | `/data/msz/wm/outputs/cosmos_policy_online_text_formal_20260605/cosmos_policy/cosmos_v2_finetune/cosmos_policy_online_text_formal_20260605/checkpoints/iter_000010000` | 两者均是远端引用 |
| local binary | 未找到 | 未找到 | 不能做独立 load/hash/fixed-batch replay |
| config/statistics | manifest 的 `config` 与 `dataset_stats_path` 字段存在 | 同左 | 只支持引用关系，不支持文件内容同源 |
| output video | base raw video 存在 | trained raw video 在另一 Project output root 找到，SHA 已登记 | video 文件齐，但 output-root provenance 需写入 run manifest |

因此不能把 base/trained 的 action trace 差异写成“checkpoint 导致的因果变化”，也不能把 episode 0 的 `success=false` 外推成 WAM 任务成功率或 0-success benchmark。

## 5. WM-019 metric mapping

| WM-019 层级 | 本 bundle 有什么 | 缺什么 | 当前 verdict |
| --- | --- | --- | --- |
| offline target fit | 无 prediction/label metric script | split、target、mask、reduction、valid count | `MISSING` |
| teacher-forced one-step | manifest 有 protocol/horizon 字段 | per-offset target error、checkpoint binary | `MISSING` |
| open-loop | action trace、300-step episode、16-step open-loop 字段、base/trained raw video | per-offset scorer、action-sensitivity probe、root reconciliation | `PARTIAL / WARN` |
| simulator closed loop | base/trained manifest 各有 episode 0 `success=false` | 多 episode denominator、同 checkpoint 可复算、完整 environment version | `DIAGNOSTIC ONLY` |
| real closed loop | 无 real hardware artifact | controller/camera/latency/安全 trace | `MISSING` |

## 6. 允许的面试口径

可以说：

> “我能从一个 CoffeePressButton 诊断 bundle 复核到 base/trained 的 rollout manifest、action trace、controller/camera/horizon 字段和两条失败视频；但 checkpoint 仍是远端路径，输出 root 与多 episode denominator 还需 reconciliation，所以我把它作为接口与失败诊断证据，不把它说成完整 benchmark 或模型 uplift。”

不能说：

1. “本地已经加载并验证了 base/trained checkpoint。”
2. “trained 比 base 成功率提升/下降。”
3. “episode 0 失败证明 WAM 是 0-success。”
4. “action trace 存在就等于 action MSE、proxy score 或 closed-loop success 已闭合。”

## 7. 下一步最小补件

1. 为 base/trained 各补 checkpoint binary 或不可变远端 hash、processor/normalizer/config SHA。
2. 把 trained 视频的 alternate output root 写入 immutable run manifest，并为同一 protocol 收集完整 episode manifest，而非只保留 episode 0。
3. 添加 prediction/label 与 metric script，报告 per-offset/action-sensitivity，而不是只保存 action JSONL。
4. 建立 run/ownership tuple：`(run_id, checkpoint_sha, config_sha, task, init, seed, controller, predicate, summary_path, owner)`。

当前结论保持 `WARN`；本 manifest 只关闭“本地完全没有任何 WAM rollout artifact”的旧疑问，不关闭 checkpoint、metric、denominator、ownership 或 uplift gate。

## 参考来源

1. [Cosmos/WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
2. [WM-019 Project Metric Artifact Gate](../../sources/vol_04_wm019_project_metric_artifact_gate.html)。
3. [WM-019 Metric Source Freeze](../../sources/vol_04_wm019_metric_boundary_source_freeze.html)。
4. [Benchmark / Evidence Audit E](../../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
