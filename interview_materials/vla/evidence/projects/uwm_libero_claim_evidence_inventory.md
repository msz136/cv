# UWM / LIBERO Claim–Evidence Inventory（UWM-01）

> 状态：`drafted / local_direct_plus_user_confirmed_final / ownership_audited / WARN`  
> 审查日期：2026-07-21  
> 证据截止：2026-07-21  
> 项目范围：UWM unified world model、LIBERO-90 → LIBERO-10 finetune、fixed-pruned-init rollout、reset-style 对照、DataLoader/zarr stall debugging、RoboCasa 转向边界  
> 项目仓库：`C:\Users\mousongzhe\Project`，当前 HEAD：`6c524d9c6c6226075f100cdac395fef2fdc37671`  
> 远端主机：`root@100.77.83.126`；当前本地证据包含一条 RoboCasa actionheadfix 30-epoch run 的八份 54-scenario raw rollout JSON，以及 project copy 中可验证的 UWM base `libero_90.pt` binary；仍不包含 produced target checkpoint/hash 或 LIBERO 250-episode raw bundle

## 结论先行

本轮审计可以把 UWM/LIBERO 的训练入口、动作/观测形状、评估脚本、协议开关、数据管线诊断和 RoboCasa 转向记录提升到 `local-direct` 或 `report-supported`。本地 project snapshot 的 commit `0341c50` 添加了 LIBERO official repro recovery artifacts：5 个 LIBERO-10 task 映射、LIBERO-90 checkpoint 入口、8 卡训练/评估 launcher、`pruned_init` helper、5-step zero-action warmup、50 rollouts/task、episode summary 聚合和 zarr DataLoader smoke。[UWM/LIBERO/RoboCasa transfer evidence freeze](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html) 冻结了 actionheadfix、30/100 epoch、convert_action A/B 和 provenance；新增 [ActionHeadFix 30-Epoch Train-to-Closed-Loop P0 Audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) 又从 remote snapshot 独立重算了同一 30-epoch run 的 8×54 raw rollouts：训练进程完成，但 full h1/h2/h4/h5/h8 仅 `2/54、1/54、0/54、1/54、1/54`，三组 h5 input ablation 为 `2/54、2/54、1/54`，全部 env errors 为 0。UWM 的共享 diffusion transformer、action/video 两类输出与 LIBERO 公开 recipe仍由 VOL 04 source audits 分层核对。

关键结果必须按协议分开：

- Book-Caddy 单任务 `42/50=0.84` 是 project report 记录的单任务结果，不是完整 LIBERO benchmark；本地没有对应 checkpoint/raw episode bundle。
- 5-task `186/250=0.744` 来自用户在远端完成后确认的 JSON，本地只保存了 user-confirmed summary；它对应项目的 fixed-pruned-init / 5-step warmup / 50-task rollout 口径。
- 旧的 reset-style `232/250=0.928` 使用 `env.seed(e)+env.reset()`，只能作为 protocol-sensitivity diagnostic，不能作为正式 benchmark 成绩。
- UWM Table II 的论文均值约 `0.79` 使用 OOD initializations、+0.03 object-init shift、移除背景物体和 3 个 finetune seeds；现有 source audit 判定本地 fixed-pruned-init 结果与 Table II **不可直接比较**。因此不能把“74.4% 只低官方 4.6pp”当作严格复现结论，只能作为同任务名下的方向性上下文。

当前 verdict 保持 `WARN`：LIBERO 最终 5-task 数字仍不是本地 raw artifact；RoboCasa actionheadfix 虽有八份完整 denominator 的 raw JSON，且 base `libero_90.pt` 已有独立 SHA，但 produced target checkpoint/hash、base hash 与旧 load report 的 shared run identity、fresh reload、immutable env/scorer revision 和 episode videos 仍缺。[UWM ownership ledger](uwm_libero_ownership_ledger.html) 已建立，但逐文件候选人角色、远端运行者和工具/协作边界仍 pending。RoboCasa-native 方向能证明训练—闭环失败断层，不等于可靠 benchmark success。项目最可信的面试价值是评估协议控制、训练-闭环链路、数据管线诊断和失败分析，而不是宣称超过官方结果。

## 1. 证据标签与门槛

| 标签 | 含义 | UWM 例子 |
| --- | --- | --- |
| `local-direct` | 当前工作区可直接读取源码、配置、脚本、report 或静态 artifact | rollout protocol 开关、task mapping、DataLoader preload/infinite sampler、RoboCasa 8×54 raw rollout JSON、UWM base binary/hash |
| `upstream-verified` | frozen UWM/LIBERO source audit 对论文/官方 repo 的机制或协议核对 | UWM 双模态 diffusion、LIBERO `pruned_init`/wrapper 语义、Table II OOD 设定 |
| `report-supported` | committed report 有结论，但底层远端 raw artifact 未同步 | Book-Caddy 42/50、训练 loss、远端 checkpoint path |
| `user-confirmed-remote-final` | 用户在远端完成后提供的最终 summary，本地保留 JSON，但无法由本地 raw episode 复算 | 5-task 186/250=0.744 |
| `protocol-limited` | 数字存在，但 init、warmup、seed、horizon、normalizer 或 scorer 不同，不能横比 | fixed-pruned-init vs UWM Table II vs reset-style |
| `local-inference` | 由代码/失败语义推断，缺 paired experiment | soup/mug 低分与接触/恢复分布缺口的解释 |
| `ownership-partial` | Git author 或设计记录提供参与线索，缺逐文件 ownership ledger | `mousongzhe` commits、用户指令中的路线转向 |
| `unverified` | 缺 raw checkpoint、episode、视频、复算命令或无法证明 | RoboCasa benchmark success、完整 5-task run lineage |

面试回答门槛：C0=理解 UWM/LIBERO 概念；C1=能指向 local script/report；C2=能解释协议取舍、stall failure 和结果冲突；C3=有 checkpoint/normalizer/init/episode/scorer/ownership 的 immutable bundle。当前机制与协议达到 C1/C2，强数字多数是 report-supported 或 user-confirmed，尚未形成 C3。

## 2. Claim reconciliation

| ID | 当前 claim | 证据 | Verdict | 面试处理 |
| --- | --- | --- | --- | --- |
| `UWM-CL-001` | 项目主线从 RoboCasa-native 调试转向 UWM 官方 LIBERO reproduction | project report、commit `0341c50`、sync summary | `local-direct / report-supported` | 可讲路线转向与问题边界；RoboCasa 不得写成已完成 benchmark |
| `UWM-CL-002` | UWM LIBERO recipe 从 LIBERO-90 checkpoint finetune 到 5 个 LIBERO-10 task | train launcher、task mapping、report、UWM source audit、base `libero_90.pt` immutable gate | `local-direct / upstream-verified recipe / base-binary-verified` | 可讲训练-评估闭环与 base 文件 hash；不能把 base hash 当作 target fine-tune checkpoint 或完整结果证据 |
| `UWM-CL-003` | LIBERO route 使用两路 RGB、action chunk 与 UWM shared diffusion model | rollout script、repo patch、UWM source audit | `local-direct / upstream-verified` | 可解释 action/video unified modeling；不要混成 Cosmos/WAM 的 value head |
| `UWM-CL-004` | 评估必须固定 init、warmup、normalizer、checkpoint、horizon、rollout 数和 success predicate | rollout script、source audit、project report | `local-direct / protocol-critical` | 用可重放 tuple 回答；任务名相同不代表协议相同 |
| `UWM-CL-005` | Book-Caddy 单任务得到 42/50=0.84 | committed report、远端路径记录 | `report-supported / single-task-only` | 只能说单任务复现实验；不能说完整 LIBERO success |
| `UWM-CL-006` | 5-task fixed-pruned-init 结果为 186/250=0.744 | user-confirmed final JSON、sync summary | `user-confirmed-remote-final / protocol-limited` | 绑定 fixed-pruned-init/5 warmup/50-task；不能称 Table II strict aligned |
| `UWM-CL-007` | reset-style 232/250=0.928 高于 strict 0.744 | user-confirmed JSON、source audit | `protocol-diagnostic` | 只能说明评估分布敏感；不能当模型 uplift 或正式成绩 |
| `UWM-CL-008` | 74.4% 与 UWM Table II 0.79 只差 4.6pp | project page/report + benchmark source audit | `NON_COMPARABLE` | 说明任务同名但 OOD init、seed、背景和训练口径不同；不写“接近官方/复现官方” |
| `UWM-CL-009` | soup_cheese 是相对官方 gap 最大任务，moka/mug 绝对成功率较低 | user-confirmed per-task table、project report | `report-supported / local-inference` | 可提出接触与长时序 recovery 假设；必须说仍需失败视频/trace 验证 |
| `UWM-CL-010` | zarr 小 chunk 随机读造成周期性 DataLoader stall，preload+infinite smoke 后 p95 wait 约 13.86s→0.19s | local benchmark script、report SVG/table、repo patch | `local-direct / smoke-bounded` | 可讲数据管线定位；不能承诺 full GPU training throughput 已提升 |
| `UWM-CL-011` | normalizer/action order、task conditioning、eval output reuse 是 RoboCasa 方向的主要风险 | project report、action/state/eval debug sections | `local-direct / inference` | 讲成排查项和修复方向；RoboCasa success 仍 unverified |
| `UWM-CL-012` | 所有 UWM/RoboCasa 实现与结果均为个人独立完成 | Git author、项目页；已有 [ownership ledger](uwm_libero_ownership_ledger.html)，但候选人逐项确认未完成 | `ownership-partial / unverified` | 说“我负责协议、迁移、诊断和验收的部分”；不把上游 UWM 结构或 Codex/协作实现写成个人原创 |
| `UWM-CL-013` | actionheadfix 30-epoch run 完成训练，但同 checkpoint 的八组 54-scenario rollout 只有 0–2 success；full-h4 `0/54` 且 contact `45/54` | [ActionHeadFix P0 audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) + 8 raw JSON | `remote-snapshot-raw / checkpoint-unverified` | 可讲 train→closed-loop 断层和 run-specific denominator；不能称 RoboCasa benchmark、ablation uplift 或 checkpoint closure |

## 3. Source inventory（冻结输入）

| Source | 类型 | SHA-256 | 能支持 | 不能支持 |
| --- | --- | --- | --- | --- |
| `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\reports\uwm_robocasa_libero_reproduction_log_report.html` | local report | `F5B268F2E7108DF548309BBA869E0099F46A6F4D5CE8A31742D002570317DB62` | 路线转向、UWM/LIBERO task、Book-Caddy 42/50、strict/reset 叙事、stall smoke、RoboCasa 风险 | 远端 checkpoint/raw episode、完整 5-task 可复算结果 |
| `scripts/libero_official_common.py` | local code | `DE9DB94113554DB50B151900647E6D32BFFB9649C7F4D1D97EA0D65A8A937E2B` | 五 task、HDF5/BDDL/pruned-init/buffer path、RGB/action shape metadata | 远端文件是否与当前本地版本一致之外的训练结果 |
| `scripts/uwm_libero_rollout_eval.py` | local code | `05E912C2096EFF4BFE8D061E4C334517B03DE80847793D83025A2AA3E18F3943` | `uwm_reset` vs `libero_fixed_init`、5-step warmup、seed/init、checkpoint prefix、success summary | raw remote episodes、target fine-tune binary、Table II OOD environment |
| `scripts/remote_muxi_libero_rollout_eval_5tasks_parallel.sh` | local launcher | `C61C7E6C5E187A640205D8F6EF609E32FE515AFE4B3687D1F47D8AF17932EE32` | 5 task/8 shard/50 rollout/600 step launcher、manifest fields、run-specific eval root | 该 launcher 实际远端完成的全部输出 |
| `scripts/remote_muxi_libero_finetune_5tasks_ddp.sh` | local launcher | `E5B6DCB03FD6612B996AB9DFD3227CB2426E0A147F21FACEE383BBF56EC29D92` | LIBERO-90 checkpoint、5 task、DDP、batch/step、buffer path、checkpoint output contract | 远端 checkpoint contents、loss/episode raw log |
| `scripts/benchmark_libero_dataloader_stall.py` | local code | `47A2A545E5FC6B0D6E540839BDD02D7C4C054B8B5A9D36D90B05B356C36B6B36` | finite/infinite/preload DataLoader-only benchmark schema | full GPU training speedup |
| `repo_patch/experiments/uwm/train_robomimic.py` | local patch | `842302703CB09A75A34611CD6B289D18C0268B710BCC2C0F9D0138192E2640BD` | pretrain load、num_steps、rollout hooks、step timing | upstream patch deployment state beyond sync report |
| `repo_patch/datasets/utils/loader.py` | local patch | `FC8E43D8D852794157B490ED7E00A68978803D5C9FE30CF6569CD640423E3551` | infinite sampler、workers/prefetch/pin controls | formal training throughput result |
| `repo_patch/datasets/robomimic/dataset.py` | local patch | `002065D77A59C81E9CD84445EA58AE3939FDA84681B7CCC79E38F182FF8B5B0E` | optional zarr preload and data slicing | memory cost/speed at production scale |
| `report/uwm_libero_strict_eval_recovery_20260702/sync_manifest.json` | local sync manifest | `9077C45992BF6852F5A8F4FA28ED3735FA590817D227A62D4179CCF239358D5F` | last remote state, protocol settings, script hashes, upstream revisions, caveat that final is superseded | final raw remote summary; partial run is not final |
| `report/uwm_libero_strict_eval_recovery_20260702/sync_summary.md` | local recovery report | `103E2E1EEA40DE384941081C78050E922D3914E54435A819DD921F54A68C1AB4` | user-confirmed final context, strict/reset distinction, recovery boundary | local independent reproduction |
| `report/.../final_strict_eval_user_confirmed_20260705.json` | user-confirmed remote final | `7616111AE7C7CA35CB10E8788ADCB1E8837D9B6F656B49553B6C7AFCCD586D11` | per-task 0.88/0.80/0.76/0.66/0.62, 186/250, reset comparison and interpretation | raw episode IDs/videos/checkpoint/normalizer hash |
| `interview_materials/vla/sources/vol_04_benchmark_evidence_claim_to_protocol.md` | source audit | `58A5636E953F44C2AA27E3ACF65C621460186DAF3732B916EAC70E6FFAB2DE6A` | LIBERO defaults、UWM Table II OOD、repo reset、project fixed-init 的不可比性 | 完整 paper source tar 或本地 user checkpoint |
| `interview_materials/vla/sources/vol_04_uwm_video_action_claim_to_code.md` | source audit | `B031B1BBF8326CBFD03FFB21AC69DB070FAC2CBFF723A16F3545D378E1354B60` | UWM shared diffusion、独立 timestep、action shape/normalizer、upstream/local boundary | 本地 UWM run success、mask ablation、checkpoint contents |
| `interview_materials/05_uwm_libero_eval_protocol.html` | project page | `89C9958EE0129C99D0CD77867E0E337E53FCF787BB62CC55EDCE9BB6BB93BF80` | resume/project narrative、74.4/92.8 claims and interview framing | independently verified final run |
| `evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.md` | canonical P0 audit | `41B9CDDDB95163A369719E007EA11AD3A7776E79F0901F80DCACD34FAA83F117` | 3930-step completion、18-task×3-scenario paired sweep、8 raw JSON recount、contact/success boundary | target checkpoint binary/hash（base `libero_90.pt` 已单独冻结）、official benchmark、ablation causality、candidate ownership |

## 4. 训练与模型边界

### 4.1 UWM/LIBERO route

本地项目报告和 source audit 支持的最小链路是：

```text
LIBERO-90 checkpoint
  -> LIBERO-10 HDF5 + compressed Zarr buffer
  -> UWM train_robomimic.py / DDP finetune
  -> task checkpoint + action normalizer
  -> LIBERO environment rollout
  -> binary success summary / episode trace
```

LIBERO route 的本地 task map 是 `book_caddy`、`soup_cheese`、`bowl_drawer`、`moka_moka`、`mug_mug` 五个任务。`libero_official_common.py` 将两路 RGB 设为 `[128,128,3]`，LIBERO action metadata 为 `[7]`；rollout script 的 model builder 设 `action_len=16`、`action_dim=7`。这证明的是当前 LIBERO adapter 的接口合同，不应泛化为所有 UWM 数据集固定 7D/16-step。

UWM 的上游机制由 source audit 记录为共享 diffusion transformer，同时建模 action chunk 与 next-observation latent video，action/video 使用独立 diffusion timestep；它不是 Cosmos/WAM 的 action/world/value 三头。项目个人贡献边界应落在环境/数据/训练脚本迁移、协议固定、诊断和验收，而不是把上游 UWM 结构说成原创。

### 4.2 RoboCasa 转向边界

原路线尝试 UWM `libero_90.pt` → RoboCasa target finetune，并遇到 official12 action order、state/proprio、task prompt、AdaLN conditioning、normalizer reuse、eval output reuse 等问题。actionheadfix 30-epoch raw audit 已证明一条具体链：8卡3930 steps完成、训练打印 loss下降、同一 remote `models.pt`/normalizer 进入八组54-scenario rollout且env errors为0，但每组仅0–2 success；full-h4 `0/54`、robot-env contact `45/54`。这把问题收窄到 train/open-loop→closed-loop transfer，不等于 benchmark success，也不能把接触当任务完成。

## 5. 评估协议 reconciliation

| 口径 | init | warmup | rollouts | 结果 | 证据等级 | 可否与论文 Table II 比 |
| --- | --- | --- | ---: | --- | --- | --- |
| UWM repo reset-style | `env.seed(e)+env.reset()` | 无项目 fixed warmup | 50/task | 232/250=0.928 | report/user-confirmed context | 否 |
| 项目 fixed-pruned-init | LIBERO `.pruned_init` | 5 zero-action | 50/task | 186/250=0.744 | user-confirmed remote final | 不能直接比 |
| UWM Table II v3 | OOD initializations，+0.03 object init shift，移除背景 | paper-specific | 50 OOD init × 3 seeds | avg≈0.79 | upstream-verified source audit | 论文内部可比 |
| LIBERO frozen default | fixed pruned states | 5 zero7 default contract | default suite-specific | protocol reference | upstream-verified source audit | 只与同 config 比 |

因此，“strict”在本项目内只能作为固定项目 protocol 的名称；它不自动等于 UWM paper Table II strict aligned。`0.928→0.744` 的 `-18.4pp` 主要是协议分布变化的诊断，不能当成模型权重退化；`0.744 vs 0.79` 的 `-4.6pp` 也不能在不同 OOD/init/seed 口径下解释成真实模型差距。

## 6. 结果与失败分析边界

最终 user-confirmed per-task 表为：`book_caddy=0.88`、`soup_cheese=0.80`、`bowl_drawer=0.76`、`moka_moka=0.66`、`mug_mug=0.62`。可以把它作为项目材料中的“用户确认的 fixed-pruned-init 结果”，但不能升级为本地 raw verified。`soup_cheese` 相对论文列表值差距最大，`moka/mug` 绝对成功率较低；接触精度、对象放置和长时序 recovery 是合理的 failure hypotheses，但当前缺失败视频、action trace、per-episode JSON 和 paired protocol ablation，因此这些仍是 `local-inference`。

推荐的失败分析顺序：

1. 先核对 checkpoint、action normalizer、camera keys、init index、warmup、horizon、success predicate 和 run-specific output root；
2. 再把失败按 grasp/contact、placement、action scale、long-horizon recovery、OOD initialization 分类；
3. 最后才决定补 recovery data、contact-sensitive task 或 world-rollout perturbation。

RoboCasa actionheadfix 的 run-specific raw sweep 必须单列：八个 setting 使用相同的 54 个 scenario/task/seed、同一 checkpoint path 与 normalizer，full h1/h2/h4/h5/h8 为 `2/54、1/54、0/54、1/54、1/54`，no-prompt/no-right/no-state h5 为 `2/54、2/54、1/54`。成功只出现在 TurnOnElectricKettle 或 TurnOnMicrowave；0–2 个 success 的差异不足以证明 prompt、state 或 right-view 的因果效果。

## 7. DataLoader stall 诊断

项目 report 记录的 DataLoader-only smoke 是一个相对强的 local-direct 工程证据：`bs64 finite workers8 pf2` 的 p95 wait 为 13.862s；只开 infinite sampler 仍为 13.183s；`preload+infinite` 降到 0.194s；`bs128 preload+infinite` 为 0.209s。该结果支持“zarr 小 chunk 随机读是主要数据等待来源”的诊断，但不等于完整 GPU 训练的吞吐/显存提升。代码开关包括 `UWM_INFINITE_TRAIN_SAMPLER`、`UWM_ROBOMIMIC_PRELOAD`、DataLoader workers/prefetch/pin 和 `UWM_STEP_TIMING_EVERY`；正式训练仍需 30–100 step GPU smoke 验证。

## 8. 个人贡献与 ownership 边界

可安全表述为：参与/负责在 C500/MACA 上迁移 UWM/LIBERO 训练与 rollout 脚本，固定项目级评估 tuple，定位 zarr/DataLoader 周期性停顿，整理 strict/reset 结果和失败分析，并据此调整项目叙事。不能自动表述为：个人原创 UWM architecture、独立完成全部 upstream repo patch、已经验证 5-task raw result、完成 RoboCasa benchmark 或单独证明 74.4% 与 Table II 的可比性。Git commits (`c4469eb`、`0341c50`、`6c524d9`) 只提供提交署名线索；逐文件 personal/collaboration/tool-assisted ledger 仍待补。

## 9. 面试安全表述

推荐 60 秒版本：

> UWM 这个项目我主要做的是训练到闭环评估的协议工程。我在 C500/MACA 上迁移 LIBERO-90 到多个 LIBERO-10 task 的 UWM finetune/rollout 路径，固定 checkpoint、normalizer、pruned-init、warmup、rollout 数和 success predicate，并排查 zarr 小 chunk 导致的 DataLoader 周期性长停。LIBERO 的 `186/250` 仍只是用户确认 summary，不能与 Table II 直接比较；RoboCasa 则有一条可重算的 actionheadfix 30-epoch raw sweep：8卡训练完成、同 checkpoint 的八组54-scenario rollout都无环境错误，但只有0–2 success，full-h4是`0/54`。所以我把它定位为 train-to-closed-loop transfer debugging，不宣称完成 benchmark。

高压追问：

- “为什么 0.744 还值得讲？”——因为它是用户确认的固定项目协议结果，能暴露任务级失败和评估差异；我不会把它叫 Table II 复现。
- “0.928 是否说明模型很好？”——不能，random reset 更容易且协议不同，只能说明 protocol sensitivity。
- “你怎么证明 stall 是 zarr？”——DataLoader-only A/B 中 preload+infinite 将 p95 wait 从约 13.86s 降到约 0.19s；full GPU throughput 仍需独立 smoke。
- “哪些是你原创的？”——我按 ownership ledger 区分迁移、协议、诊断和协作实现；UWM shared diffusion architecture 属于上游机制。

## 10. P0/P1 artifact queue

### P0

1. 获取 5-task strict run 的 target checkpoint、normalizer、exact config、init index、250 episode JSONL、失败视频和 run-specific manifest；base `libero_90.pt` 的本地 hash 已单独冻结，但尚未与该 run shared-ID 绑定。
2. 明确项目 fixed-pruned-init protocol 与 UWM Table II OOD protocol 的差异；如要声称 reproduction，必须补 OOD environment patch、3 seeds 和同 scorer。
3. 对 reset-style 与 fixed-pruned-init 做同 checkpoint paired run，记录每 episode seed/init/step/horizon。
4. 逐文件 ownership ledger 已建立；下一步补候选人确认，标注 upstream、个人、协作、工具辅助、只运行和仅读审计。
5. 对 RoboCasa actionheadfix 回传 `models.pt` hash/fresh-load parity、完整 train JSONL、env/scorer revision 与54条 episode video locator；当前 raw denominator 与 base hash 已有，但 target checkpoint和可重放环境仍未闭合。

### P1

1. 对 soup/moka/mug 失败做 video/action trace 分类，并验证 contact/placement/recovery 假设。
2. 做 30–100 step GPU smoke，比较 preload/infinite 与 baseline 的 `data_wait_sec/train_sec/total_sec`、显存和吞吐。
3. 对 actionheadfix 的相同54 scenario做多 checkpoint seed repeat，报告 paired interval；沿 full-h4 matched failure 建立 expert→x0→sampled→converted→executed action 的 first-divergence trace。

## 11. References

- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\reports\uwm_robocasa_libero_reproduction_log_report.html`
- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\libero_official_common.py`
- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\uwm_libero_rollout_eval.py`
- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\remote_muxi_libero_rollout_eval_5tasks_parallel.sh`
- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\remote_muxi_libero_finetune_5tasks_ddp.sh`
- `C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\benchmark_libero_dataloader_stall.py`
- `C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702\sync_manifest.json`
- `C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702\sync_summary.md`
- `C:\Users\mousongzhe\Project\report\uwm_libero_strict_eval_recovery_20260702\final_strict_eval_user_confirmed_20260705.json`
- `C:\Users\mousongzhe\cv\interview_materials\vla\sources\vol_04_benchmark_evidence_claim_to_protocol.md`
- `C:\Users\mousongzhe\cv\interview_materials\vla\sources\vol_04_uwm_video_action_claim_to_code.md`
- `C:\Users\mousongzhe\cv\interview_materials\vla\evidence\projects\uwm_libero_ownership_ledger.md`
- UWM upstream revision recorded in sync manifest: `b7d4067c8859775e5b08f681e76d538015cdd445`
- LIBERO upstream revision recorded in sync manifest: `8f1084e3132a39270c3a13ebe37270a43ece2a01`
- [UWM/LIBERO/RoboCasa Transfer Evidence Freeze](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)；canonical [Markdown](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.md)，review [JSON](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.review.json)。
- [UWM RoboCasa ActionHeadFix 30-Epoch Train-to-Closed-Loop P0 Audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)；canonical [Markdown](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.md)，review [JSON](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.review.json)。
- [UWM `libero_90.pt` 本地 immutable checkpoint manifest gate](../../sources/uwm_libero90_checkpoint_immutable_manifest_gate.html)；canonical [Markdown](../../sources/uwm_libero90_checkpoint_immutable_manifest_gate.md)，review [JSON](../../sources/uwm_libero90_checkpoint_immutable_manifest_gate.review.json)。
