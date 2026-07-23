# VOL 05 UWM / LIBERO / RoboCasa Transfer：证据冻结

> 状态：`local_protocol_audited / user_confirmed_remote_final / robocasa_debugging / WARN`
> 复核日期：2026-07-21  
> 证据来源：`C:\Users\mousongzhe\Project\wm` 与 `C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702`（外部工作区只读审计）  
> Bounded slice：本页冻结 UWM 官方 LIBERO reproduction、RoboCasa-native transfer/actionheadfix 训练与闭环评估的协议、指标、修复和 provenance；不把用户确认远端摘要升级为本地 raw benchmark，不改变题卡 mastery 或 ownership。

## 1. 结论先行

这个项目最适合在面试中讲成“训练—评估协议工程与失败诊断”，而不是单纯报成功率：

1. UWM/LIBERO 路线已经有本地脚本、任务映射、`pruned_init`/reset 协议开关、5-step warmup、8-shard launcher 和 DataLoader-only smoke；
2. 用户确认的 strict fixed-init 结果为 `186/250=0.744`，但 JSON 明确标记为 `user-confirmed remote final`，本地没有 checkpoint、normalizer、250 条 episode JSONL 或 scorer，不能称 local raw reproduction；
3. 旧 `232/250=0.928` 使用 `env.seed(e)+env.reset()` 的 reset-style 协议，不能与 strict fixed-init 或 UWM Table II 直接比较；
4. RoboCasa actionheadfix 使 action-head 初始化、open-loop监督和trace诊断更可信；新增raw audit对一条30-epoch openpi-state-3view run重算：full h1/h2/h4/h5/h8为`2/54、1/54、0/54、1/54、1/54`，三组h5 input ablation为`2/54、2/54、1/54`，全部env errors为0；历史30/100-epoch结果属于相邻run，不能混算；
5. 严格 `convert_action` A/B 为 `0/6`、6 个环境错误（`expected 12, got 5`），说明 OpenPI-style dict 不能直接喂给当前 native RoboCasa env；GT bridge replay 的最大绝对差为 `0.0`，但模型闭环仍失败。

## 2. 证据等级与 provenance

| 层级 | 当前材料 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `local-direct` | 本地脚本、repo patch、报告、commit、DataLoader smoke | task map、action/state shape、协议开关、修复逻辑、日志字段 | 远端权重内容或完整 episode 结果 |
| `report-supported` | `uwm_robocasa_libero_reproduction_log_report.html` | Book-Caddy `42/50`、训练曲线片段、RoboCasa run ledger | 本地可重算的 checkpoint/episode bundle |
| `user-confirmed-remote-final` | `final_strict_eval_user_confirmed_20260705.json` | 5-task per-task summary 与协议说明 | 原始 250 episode、checkpoint hash、normalizer/scorer |
| `remote-snapshot-raw` | actionheadfix 30-epoch `train.out` + 8×54 rollout JSON | run completion、paired scenario set、success/env-error/contact recount | produced checkpoint binary/hash、env/scorer revision、videos、ownership |
| `working-tree-evidence` | `sync_manifest.json`、`sync_summary.md` | 远端断联时最后状态、脚本 hash、dirty/未跟踪文件边界 | 将 recovery summary 变成 committed raw result |
| `local-inference` | action/contact/协议对照 | 对失败原因提出可检验假设 | 已确认的唯一 root cause |
| `unverified` | RoboCasa benchmark success、personal end-to-end ownership | 仅列为待补证 | 任何强 C3 结果或原创架构声明 |

外部 Project 当前 HEAD 为 `6c524d9c6c6226075f100cdac395fef2fdc37671`（`Document RoboCasa actionheadfix diagnostics`）。工作树仍有：`sync_manifest.json`、`sync_summary.md` 修改，以及 `final_strict_eval_user_confirmed_20260705.json` 未跟踪。它们必须分别标记为 committed、working-tree、user-confirmed 和 raw-local，不可混为一个“完整复现实验”。

## 3. 官方 Baseline 与 UWM/LIBERO 结果对照

### 3.1 UWM/LIBERO 任务与协议

本地 `libero_official_common.py`、`uwm_libero_rollout_eval.py` 和 parallel launcher 固化了五个 LIBERO-10 任务：`book_caddy`、`soup_cheese`、`bowl_drawer`、`moka_moka`、`mug_mug`。项目 strict protocol 为：

| 字段 | fixed-init 项目口径 |
| --- | --- |
| initial state | LIBERO `*.pruned_init`，按官方顺序读取 |
| warmup | 5 个 zero-action steps |
| rollouts | 50/task，5 task，共 250 |
| rollout length | policy steps 600 |
| launcher | 8 shards / GPUs 0–7 |
| success | environment `info["success"]` 二值信号 |
| provenance | 用户确认远端 summary；raw episode 未同步 |

SR（success rate）对 (N) 条 rollout 的定义为：

\[
\mathrm{SR}=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}[\mathrm{success}_i].
\]

其中 (N) 是固定 protocol 下的 episode 数，(mathbf{1}[cdot]) 来自环境 success predicate。实现对应 `uwm_libero_rollout_eval.py` 的 per-episode summary 和 task-level aggregation；没有 episode JSONL 时只能信任 summary 的 provenance，不能在本地重新计算。

### 3.2 结果 reconciliation

| 口径 | 结果 | 证据等级 | 解释 |
| --- | ---: | --- | --- |
| Book-Caddy 单任务 report | `42/50=0.84` | `report-supported` | 单任务复现实验，不是完整 LIBERO benchmark |
| UWM reset-style | `232/250=0.928` | `user-confirmed context / protocol-diagnostic` | `env.seed(e)+env.reset()`，随机 reset 分布 |
| fixed-pruned-init strict | `186/250=0.744` | `user-confirmed-remote-final` | 5-step warmup、50/task；本地无 raw bundle |
| UWM Table II reference | 约 `0.79` | `upstream-verified` | OOD init、+0.03 object shift、背景移除、3 seeds |

strict fixed-init per-task summary：

| Task | Strict result | Assumed denominator |
| --- | ---: | ---: |
| `libero_book_caddy` | `0.88` | 44/50 |
| `libero_soup_cheese` | `0.80` | 40/50 |
| `libero_bowl_drawer` | `0.76` | 38/50 |
| `libero_moka_moka` | `0.66` | 33/50 |
| `libero_mug_mug` | `0.62` | 31/50 |
| total | `0.744` | 186/250 |

不能把 `0.744` 与 Table II 的 `0.79` 写成严格复现差距：两者的 initial-state distribution、object shift、background removal、seed 数和训练口径不同。`0.928→0.744` 的 `-18.4pp` 首先是 protocol sensitivity，不是同 checkpoint 的模型退化实验。

## 4. UWM Base I/O 与 LIBERO route

UWM 上游是共享 diffusion transformer，同时预测 action chunk 和未来观测/视频 latent，action/video 使用独立 diffusion timestep。项目 adapter 使用两路 RGB、7D action metadata 与 task-specific UWM wrapper；这属于 UWM 公有机制与本地接口迁移的组合，不应混成 Cosmos/WAM 的 action/world/value 三角色。

```text
LIBERO-90 checkpoint
        |
        v
LIBERO-10 HDF5 -> compressed Zarr buffer -> UWM robomimic trainer
        |                                      |
        |                                      v
        +------------------------------> task checkpoint + normalizer
                                               |
                                               v
                                   LIBERO fixed-init rollout evaluator
```

本地 evidence 支持的输入/输出边界是：两路 `128×128` RGB、proprio/state contract、7D action chunk，经过 UWM model builder 和 normalizer 后由 environment wrapper 执行；具体 action horizon、normalizer 文件和远端 checkpoint binary 仍需要 raw bundle 才能升级为 C3。

## 5. RoboCasa action-space 与 head 改造

RoboCasa native full action 是 12D：EEF 7D、base 4D、control 1D。actionheadfix 线将 UWM 的 7D EEF 输出与 RoboCasa 原生字段拆分、重排并加入 hierarchical decoder。可用的抽象映射为：

\[
a^{\mathrm{env}}=\operatorname{concat}\left(a^{\mathrm{eef}}_{7},a^{\mathrm{base}}_{4},a^{\mathrm{control}}_{1}\right),
\]

其中 \(a^{\mathrm{eef}}_7\) 是模型的连续末端动作，\(a^{\mathrm{base}}_4\) 和 \(a^{\mathrm{control}}_1\) 来自额外 head 或统计初始化。实现证据位于 `uwm_robocasa_train.py`、`uwm_robocasa_rollout.py` 与 `NativeRoboCasaDictActionWrapper`；它证明了接口设计和 trace 字段，不证明闭环成功。

actionheadfix 的训练侧改动：

| 改动 | 证据 | 作用 | 边界 |
| --- | --- | --- | --- |
| partial decoder init | commit `a37a386`；`checkpoint_load_report` | 从 `libero_90.pt` 复制 shape-compatible decoder，避免 12D head 全部从零学 | 不是完整 checkpoint identity |
| action stats bias init | 同上 | base/control bias 写入 normalized action space | 统计量 provenance 仍需固定 |
| predicted x0 MSE | 训练脚本与 `teacher_forced_target_atomic_seen.json` | 从 noise prediction 还原 clean action，再按真实 action 单位诊断 | teacher-forced 不等于 rollout |
| group x0 metrics | eef/base/control/gripper 分组 | 暴露总 loss 掩盖的通道错误 | 不自动证明控制策略有效 |
| auxiliary action override | rollout script | 将 gripper/control auxiliary 参与最终 action 组装 | 可能引入执行时序副作用 |
| h4 sharding | commit `1a03fe9` | 54 scenario round-robin 分片后合并 | sharding 不改变任务协议 |

checkpoint load smoke 的可核验摘要为：`matched_count=446`、`skipped_count=8`、`reset_action_head=true`、decoder partial init=true；报告同时记录早期 task embedding concat 会使 AdaLN condition dim 从 `3584` 变为 `3712`，随后改为 residual projection 以保持 trunk shape。不同 smoke 的 target-key 集合不同，`446` 不能和另一个 `196/258` smoke 直接比较。

## 6. RoboCasa Fine-tune 与 Eval Run Ledger

| Run | 数据/初始化 | 关键改动 | 训练证据 | 闭环结果 | 结论 |
| --- | --- | --- | --- | --- | --- |
| early target pilot | `libero_90.pt` → target atomic | 7D/12D 适配、task-id 等 | report/README 有 run path | `0/3`、`0/3`、`1/3` task pilot | 适配链可运行，非 benchmark |
| 30 epoch task-id | target atomic seen | official12 + task-id，`exec_horizon=4` | checkpoint 与 run JSON 已记录 | `1/54`，唯一成功为 `TurnOnElectricKettle` | 仅 task-id 不足 |
| 100 epoch resume | 30 epoch checkpoint 续训 | 继续拉 epoch | final summary：loss 与 checkpoint path | `0/54`，env errors `0` | 更多 target epoch 未解决闭环 |
| strict execution A/B | 同 100 epoch checkpoint | direct vs strict `convert_action` | run-specific logs | direct `0/6`, errors `0`; strict `0/6`, errors `6` | OpenPI dict 不能直送 native env |
| Human300 pretrain | `libero_90.pt` → RoboCasa Human300 | 3 epoch，5271 steps，12D | action stats count `29,106,226`；loss `95.21→0.2265`；action `2.96→0.0411`；x0 `88.80→0.0285` | pretrain 是 offline 训练，不是 success | action head/分布可学习性改善 |
| actionheadfix 30-epoch openpi-state-3view | `libero_90.pt` partial load → target atomic | 30 epoch，3930 steps，12D action、task/prompt/state/right conditioning | printed step0→3929 loss `3.3257→0.25385`；action `2.4300→0.07689`；raw `0.9986→0.03043`；`val_ratio=0` | paired 54-scenario sweep：h4 `0/54`，robot-env contact `45/54`，env errors `0`；其它setting `1–2/54` | 训练fit未转化为稳定closed-loop success；[raw audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) |

### 6.1 Teacher-forced 诊断

在 256 action rows 上，报告记录：

| 指标 | 值 |
| --- | ---: |
| `x0_mse_total` | `0.0647` |
| `x0_mse_base` | `2.68e-6` |
| `x0_mse_control` | `4.47e-5` |
| `x0_mse_eef_pos` | `0.1489` |
| `x0_mse_gripper` | `0.3093` |

这说明 base/control 通道在 teacher-forced/open-loop 分布上更接近标签，而 EEF position 与 gripper 仍是高误差通道；它不能直接推出 simulator success。

## 7. Online Rollout 与 0-success 诊断

实际评估由 `uwm_robocasa_rollout.py`、`remote_muxi_eval_h4_sharded.sh` 和 env wrapper 组成，核心路径可抽象为：

```python
def rollout_one_scenario(env, policy, task, replan_steps=4):
    # 1. Reset task and collect camera/state/prompt observation.
    obs = env.reset(task)
    # 2. Build model input and sample a normalized action chunk.
    chunk = policy.sample(build_observation(obs, task))
    # 3. Denormalize, reorder to native 12D, and apply optional aux override.
    env_actions = action_dict_to_native_array(denormalize_and_parse(chunk))
    # 4. Execute only the first replan_steps actions, then query again.
    for action in env_actions[:replan_steps]:
        obs, reward, done, info = env.step(action)
        if done or info.get("success", False):
            break
    # 5. Persist trace/video/success/error fields for this scenario.
    return info
```

对新冻结的30-epoch openpi-state-3view run，full-h4 raw JSON 的直接症状是：`0/54`、`num_env_errors=0`、`45/54` rollout 出现至少一次 robot-env contact。此前报告中的 `27/54` 属于未冻结相同run identity的历史摘要，不能替代本页精确recount。八份54-scenario raw JSON已经提供完整config内denominator，但没有checkpoint binary、视频和immutable env/scorer revision；trace中的普通counter/link/hand接触仍不能等价为有效抓取、按键或开门，也不能宣布唯一根因。

### 7.1 convert_action A/B

| 路径 | 结果 | 解释 |
| --- | --- | --- |
| native direct | `0/6`，env errors `0` | 12D array 可以执行，但没有成功 |
| strict OpenPI-style `convert_action` | `0/6`，env errors `6` | 每条在 step 0 报 `expected 12, got 5` |
| GT action bridge replay | `bridge_max_abs_diff_max=0.0` | dict→native 12D bridge 数值一致；不能证明模型动作正确 |

因此 execution bridge 是需要固定的协议字段；strict path 的 6 个错误不能和有效 rollout 的 0 success 混合计算。

## 8. DataLoader Stall 诊断

UWM/LIBERO 本地 `benchmark_libero_dataloader_stall.py` 只构建 DataLoader，不建模型、不占 GPU。报告记录的 A/B：

| 设置 | p95 wait |
| --- | ---: |
| finite，workers=8，prefetch=2 | `13.862 s` |
| infinite sampler | `13.183 s` |
| preload + infinite | `0.194 s` |
| bs128 preload + infinite | `0.209 s` |

这支持“zarr 小 chunk 随机读取造成周期性等待”的工程假设，但不等于完整 GPU training throughput、显存或最终训练时间已提升。要升级结论，仍需 30–100 step matched GPU A/B 并记录 `data_wait_sec/train_sec/total_sec/memory/throughput`。

## 9. 公有设计、本地证据与个人边界

| 类别 | 当前可安全说法 | 禁止升级 |
| --- | --- | --- |
| 公有上游 | UWM shared diffusion、LIBERO recipe、Table II protocol | 把 UWM architecture 说成个人原创 |
| 本地迁移 | 我迁移/整理了 UWM-LIBERO launcher、RoboCasa action mapping、strict/reset protocol 和诊断脚本 | “独立完成全部 upstream patch” |
| 本地诊断 | 我用 DataLoader-only A/B 定位 zarr wait，用 trace 观察 contact/夹爪/control 失配 | “已证明唯一 root cause” |
| 用户确认结果 | 可以报告 `186/250`，并明确 `user-confirmed-remote-final` | “本地已复现 74.4%” |
| RoboCasa | 可以讲 30/100 epoch、actionheadfix 和 A/B 失败路径 | “完成 RoboCasa benchmark” |

推荐 60 秒回答：

> UWM 项目我主要负责训练到闭环评估的协议工程。我在 C500/MACA 上迁移 LIBERO-90 到多个 LIBERO-10 task 的 finetune/rollout，固定 pruned-init、warmup、normalizer、horizon、rollout 数和 success predicate，并用 DataLoader-only A/B 定位 zarr 小 chunk 的周期性等待。LIBERO `186/250` 仍是用户确认summary；RoboCasa则有一条可重算的actionheadfix 30-epoch raw sweep：8卡3930 steps完成，同checkpoint的八组54-scenario rollout都没有env error，但只有0–2 success，full-h4为`0/54`且`45/54`有robot-env contact。因此我把它定位为train-to-closed-loop contract debugging，而不是benchmark成功。

## 10. 待补 P0 与恢复清单

1. 获取 strict run 的 checkpoint binary/hash、normalizer、exact config、init index、250 episode JSONL、失败视频和 scorer。
2. 用同一 checkpoint 做 reset-style vs fixed-pruned-init paired evaluation，记录每个 episode 的 seed/init/horizon。
3. 运行 30–100 step GPU matched DataLoader A/B，验证 preload/infinite 对真实训练吞吐的影响。
4. 对 soup/moka/mug 失败做 video/action trace/contact 分类，区分动作语义、空间定位、接触和长时序 recovery。
5. 对 RoboCasa wrapper bridge 重新跑 run-specific eval，明确 direct、strict convert_action、wrapper-convert 三种结果不混算。
6. 完成 `OWN-UWM-001`：逐文件标注上游、本人、协作、工具辅助、只运行、只审查和 operator/reviewer。

## References

1. UWM/LIBERO 本地复现报告：`C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\reports\uwm_robocasa_libero_reproduction_log_report.html`，SHA-256 `F5B268F2E7108DF548309BBA869E0099F46A6F4D5CE8A31742D002570317DB62`。
2. RoboCasa transfer/actionheadfix 报告：`C:\Users\mousongzhe\Project\wm\uwm_robocasa_transfer\uwm_robocasa_transfer_report.html`，SHA-256 `D0ADC3C46D824242E5F8E4D7D1F787CA09810FAA108CA8C79C4E7110A1B00518`。
3. Strict recovery manifest：`C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702\sync_manifest.json`，SHA-256 `9077C45992BF6852F5A8F4FA28ED3735FA590817D227A62D4179CCF239358D5F`。
4. User-confirmed final：`C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702\final_strict_eval_user_confirmed_20260705.json`，SHA-256 `7616111AE7C7CA35CB10E8788ADCB1E8837D9B6F656B49553B6C7AFCCD586D11`。
5. UWM project inventory：[UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)；P0 gate：[UWM/LIBERO P0 Bundle Audit](../evidence/projects/uwm_libero_p0_bundle_audit.html)。
6. UWM upstream source audit：[UWM video–action claim-to-code](vol_04_uwm_video_action_claim_to_code.html)；benchmark protocol：[Benchmark evidence claim-to-protocol](vol_04_benchmark_evidence_claim_to_protocol.html)。
7. UWM paper：Zhu et al., “Unified World Models: Coupling Video and Action Diffusion for Pretraining on Large Robotic Datasets,” RSS 2025；LIBERO official benchmark documentation；RoboCasa benchmarking documentation。
8. [UWM RoboCasa ActionHeadFix 30-Epoch Train-to-Closed-Loop P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)。
