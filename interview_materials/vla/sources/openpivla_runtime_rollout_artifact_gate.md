# OpenPiVLA 本地 Runtime Rollout Artifact Gate：ALOHA 与 LIBERO

> 状态：`local-direct / immutable-summary-read / true-physics-rollout / WARN`
> 审查日期：2026-07-21
> 范围：`C:\Users\mousongzhe\project\openpivla_deployment` 的部署记录与已落档 rollout summary；本页只冻结运行时证据，不把上游 checkpoint 结果改写成个人训练成果。
> 结论先行：本地 artifact 直接支持 **官方 OpenPI checkpoint 在 ALOHA MuJoCo 与 LIBERO/robosuite 物理环境中完成了可审计的 policy inference 与视频/轨迹落档**。ALOHA transfer-cube 三回合为 `2/3`，多视角两回合为 `1/2`；LIBERO spatial task 0 的 `pi05_libero` model-policy smoke 为 `0/1`，同时记录了 no-op reference。当前仍不能据此声称 OpenPiVLA 私有微调、个人 ownership、泛化 benchmark 或 archived `97.4%` lineage 已闭合。

## 1. Evidence freeze

| ID | 本地对象 | 直接核对 | SHA-256 / 状态 |
| --- | --- | --- | --- |
| D01 | `C:\Users\mousongzhe\project\openpivla_deployment\DEPLOYMENT.md` | checkpoint、环境、运行目录、结果表、失败边界与 provenance 说明 | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14E` / local-direct |
| R01 | `artifacts\aloha_sim_real_rollout_20260608_154324\summary.json` | `pi0_aloha_sim`、`gym_aloha/AlohaTransferCube-v0`、3 episodes、success/reward/action/state 指标 | `27E4A04C01FD3AA6DDB387B59B519C4B3CC17DF94961EEB17686A160AECE1C13` / immutable-summary |
| R02 | `artifacts\aloha_sim_visual_rollout_real_v1\summary.json` | 6 路相机、2 episodes、多视角 true-physics rollout 指标 | `CB1E331A82AE032C564FD74CE5F6E01CB1875EAC3A3DF4479943E7C8B4891687` / immutable-summary |
| R03 | `artifacts\libero_franka_true_rollout_v1\summary.json` | `pi05_libero`、`libero_spatial/task_id=0`、model/no-op 对照、视频文件名 | `341E77110D75E50B601A078923F51EF8FA39AAA045FA491843A1003B0320E1DB` / immutable-summary |

本页引用的 summary 文件位于用户项目目录，未复制进本仓库，也未修改其代码或运行产物。`DEPLOYMENT.md` 中的 remote path 只用于记录 provenance；本页的运行结果以本地 summary JSON 与同目录视频/轨迹文件为准。

## 2. ALOHA：真实 MuJoCo policy inference

### 2.1 三回合基础 rollout

`R01` 的 summary 写明：配置为 `pi0_aloha_sim`，任务为 `gym_aloha/AlohaTransferCube-v0`，最大步数 300，3 个 episode，`state_diverged_count=0`。成功率为 `2/3=0.6667`，平均最大 reward 为 `3.3333`，平均 action delta 为 `0.0201277`，平均 action jerk 为 `0.0079451`。每回合的成功布尔值、有限状态、轨迹 JSON 与 camera MP4 均存在于 artifact 目录。

这能支持的面试表述是：

> “我把官方 OpenPI policy 接到 ALOHA transfer-cube 的 MuJoCo 环境，做了 3 回合闭环推理；2 回合成功，所有状态保持 finite，没有 state divergence，同时把每步 trajectory、相机视频和 action smoothness 指标落档。”

这不能支持“我训练出了这个 checkpoint”或“该结果是大规模 benchmark”。summary 的 checkpoint 路径是 `/data/msz/openpivla/models/openpi-assets/checkpoints/pi0_aloha_sim`，而本页没有私有微调 checkpoint、训练 config lineage 或候选人 pre-snapshot diff。

### 2.2 多视角 rollout

`R02` 标记 `visualization_type=true_physics_rollout`，相机为 `top`、`angle`、`front_close`、`left_wrist`、`right_wrist`、`left_pillar`。2 回合的成功率为 `0.5`，平均最大 reward 为 `2.5`，平均 action norm 为 `2.0879`，平均 action delta 为 `0.02402`，`state_diverged_count=0`。每回合有 `multiview_overlay.mp4`、各相机视频、trajectory JSON 与 metrics JSON。

多视角视频是部署/诊断证据，不等价于新算法贡献。面试中应把“相机渲染、轨迹记录、状态/动作统计”与“策略本身的训练 ownership”分开。

## 3. LIBERO：任务级物理 rollout 的失败样本

`R03` 的任务是 `libero_spatial`、`task_id=0`：`pick up the black bowl between the plate and the ramekin and place it on the plate`。`pi05_libero` model-policy 与 zero-reference 各执行 70 步，二者 total reward 都为 `0.0`、success 都为 `false`；model-policy 的平均 action norm 为 `1.2689`，最终 state norm 为 `3.2866`。对照视频 `zero_reference_vs_model.mp4`、两条 rollout 视频与 metrics PNG 均已落档。

这里的关键面试结论是：

- 这是 task-level MuJoCo/robosuite rollout，不是只做 import 或离线 action plot 的 smoke；
- 结果是失败，不应包装为 LIBERO 成功率；
- zero-reference 是 no-op baseline，因为当前官方 checkout 没有随附 LIBERO demonstration action file；它不是 GT demonstration；
- 失败首先证明“策略在该任务/配置下未完成目标”，不自动证明 simulator 不可用，也不自动定位到 action axis、normalizer 或 controller 的唯一根因。

## 4. 证据边界与 claim 回写

| Claim | 当前 verdict | 面试安全口径 | 升级所需 artifact |
| --- | --- | --- | --- |
| 官方 OpenPI checkpoint 能在 ALOHA MuJoCo 推理 | `local-direct / PASS WITH WARNING` | “官方 `pi0_aloha_sim` 在 3 回合 transfer-cube rollout 中完成了可复核 inference，2/3 成功。” | ALOHA 专属 checkpoint manifest/load log；当前新增的 [LIBERO load-lineage gate](openpivla_libero_checkpoint_load_lineage_gate.html) 只闭合 `pi05_libero` server restore |
| 多视角 ALOHA true-physics rollout | `local-direct / PASS WITH WARNING` | “6 路相机、视频、trajectory、action/state 指标均有落档；2 回合为 1/2。” | 更大 episode 数、固定 protocol 与独立 evaluator |
| `pi05_libero` 任务级 rollout | `local-direct / WARN` | “LIBERO spatial task 0 的 70-step model-policy smoke 为 0 reward/false success，失败结果可复现读取。” | 完整 task matrix、checkpoint load log、独立 success scorer 与 matched reference |
| OpenPiVLA 私有微调已产生上述结果 | `UNVERIFIED` | 不把官方 checkpoint deployment 与个人 fine-tune 混写。 | immutable fine-tune checkpoint、config、训练日志、load/reload 与 lineage |
| 个人 ownership / 创新点 | `PENDING` | “我能确认运行与结果文件，但具体由我负责的代码边界仍需逐文件确认。” | candidate role confirmation、pre-snapshot diff、协作工具边界 |
| archived `97.4%` 属于本地 rollout | `ARCHIVE-SUMMARY-ONLY` | “归档报告中有该数字，但本页 rollout summary 不证明同一 checkpoint/protocol/lineage。” | 原始 benchmark manifest、checkpoint hash、评估脚本与 raw episodes |

## 5. 面试回答模板与追问

### 30 秒回答

“我先把官方 OpenPI policy 接入两个 task-native simulator 做部署验证。在 ALOHA transfer-cube 上，`pi0_aloha_sim` 做了 3 回合闭环 rollout，成功 2 回合，并落了相机视频、trajectory、reward、state norm、action delta/jerk；多视角版本 2 回合成功 1 回合。随后在 LIBERO spatial 的一个 Franka 任务上用 `pi05_libero` 做 70 步真实物理 rollout，model-policy 和 no-op reference 都是 0 reward、false success，所以我把它归为失败诊断样本，而不是 benchmark 成绩。这里能证明的是官方 checkpoint 的 runtime 与评估链路，不是我训练了 checkpoint，也不能把它和 97.4% 归到同一 lineage。”

### 高频追问

1. **为什么 ALOHA 成功而 LIBERO 失败？** 目前只能说任务、checkpoint/config、embodiment 与控制链路不同；summary 没有足够证据把原因唯一归到 axis、normalizer、相机或 controller，下一步要做 matched probe。
2. **你如何确认不是 fake rollout？** ALOHA 与 LIBERO 都有 simulator step、逐步 trajectory、reward/state/action 指标和视频；但这仍不替代独立 scorer 与 checkpoint manifest。
3. **你做了什么改动？** 当前证据只支持“部署脚本、环境隔离、评估/可视化产物已落档”；具体个人 ownership 尚未关闭，不能把 routine path/config 说成算法创新。
4. **为什么不把 2/3 写成 benchmark？** episode 数小、protocol 是 smoke/deployment run，且没有与官方 benchmark evaluator 和完整任务矩阵对齐。

## 6. 下一步

1. LIBERO server/client load log 已由 [Checkpoint Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html) 冻结；下一步补 checkpoint 逐文件 SHA、norm stats SHA、精确 argv 与 shared run UUID，才能形成 immutable manifest。
2. 对 LIBERO 失败做一个最小 matched probe：固定 observation keys、action shape、axis/order/unit、normalizer、controller 与 scorer，并保留 zero-reference/model 对照。
3. 逐文件确认候选人的 ownership，再把本页事实映射到项目题卡；在真实口述前不新增 mastery 记录。

## 参考文献（References）

1. Local deployment record：`C:\Users\mousongzhe\project\openpivla_deployment\DEPLOYMENT.md`（D01）。
2. Local ALOHA rollout summary（R01）及同目录 `episode_*/trajectory.json`、`episode_*/camera.mp4`。
3. Local ALOHA visual rollout summary（R02）及同目录多视角视频/trajectory。
4. Local LIBERO rollout summary（R03）及 `model_policy/`、`zero_reference/` 视频与 metrics。
5. [OpenPiVLA formal JSON/CE artifact gate](openpivla_formal_json_ce_shape_contract_artifact_gate.html)，用于区分 local training representation 与官方 deployment runtime。
6. [OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html)，用于补充 Orbax restore、normalizer、listen/connect 与 code contract 证据。
