# VOL 04 Source Audit E：Benchmark / Evidence Claim-to-Protocol

> 审计日期：2026-07-16  
> 状态：drafted / primary_protocols_frozen / local_artifacts_pending / independent_review_pending  
> 覆盖题目：VLA-WM-039..044  
> 冻结对象：LIBERO、UWM、Cosmos Policy、RoboCasa、WorldGym 的 paper/repo/eval 入口与项目 claim 边界  
> 核心规则：任务名相同不代表 protocol 相同；只有 protocol tuple 与 artifact manifest 同时闭合，成功率才允许横向比较。

## 1. 结论先行

1. **“strict”不是形容词，而是一份可重放合同。**最少要固定 task/suite、initial state、warmup、camera/preprocess、action schema/normalizer、chunk/replan、controller、horizon、success predicate、seed/determinism、trial count、checkpoint/runtime。[1][2]
2. **LIBERO frozen 官方代码的默认 lifelong eval 是 20 个 fixed `pruned_init`、5 次零动作 warmup、600 policy steps。**环境默认是 20 Hz、`OSC_POSE`、7D action、两路 128×128 RGB；这些是该 commit 的默认值，不是所有 LIBERO 论文的统一协议。[1]
3. **UWM Table II 的 0.79 不是上述默认 fixed-init protocol。**论文 v3 在五个 LIBERO-10 任务上扩大每个物体的初始化范围 0.03、移除背景物体，按 50 个 OOD initializations、3 个 finetune seeds 报告均值与区间。[2]
4. **frozen UWM repo 没有给出 Table II 的 OOD 环境改造入口。**仓库 `eval_robomimic.py` 使用 `env.seed(e) + env.reset()`，没有 `set_init_state`、没有 warmup，默认 rollout length 1000，并整段执行 model sample；`reset_to_state` 只出现在 inverse-dynamics ablation。[3]
5. **因此，当前项目页的 74.4% 只能暂记为“本地 fixed-init claim”，不能写成“与 UWM Table II strict aligned”。**项目材料写的是 `pruned_init + 5-step zero action + 50/task`；论文 Table II 写的是 OOD shifted initialization。二者任务相同，但 initial-state distribution 不同。[2][3][10]
6. **92.8% reset-style 只能作为 protocol sensitivity diagnostic。**当前 workspace 没有该结果的 checkpoint、episode summary、seed/init trace 或同 checkpoint paired run，不能把项目页数字升级为已核验事实。[10]
7. **Cosmos LIBERO 又是第三套协议。**frozen runner 使用默认 initial states 的前 50 个、10 次带闭夹爪的 dummy action、suite-specific 220–520 step horizon、chunk 16 / open-loop 16；官方 README 要求 seeds 195/196/197。[4]
8. **Cosmos RoboCasa 使用的是一个未在安装命令中 pin 的 fork。**`ROBOCASA.md` 安装 `moojink/robocasa-cosmos-policy`；2026-07-16 观察到 fork HEAD 为 v0.2.0，而官方 `robocasa/robocasa` frozen HEAD 是 v1.0.1。两者不能混成一个环境版本。[5][6][7]
9. **RoboCasa 的 84/118=71.19% 是“官方 HF checkpoint 的本地 harness smoke evidence”，不是官方 paper protocol，也不是本地训练收益。**当前只在项目页出现 24 tasks × 5 episodes 与两条剔除；缺少逐 episode artifact，保持待核验。[10]
10. **WorldGym 的“success rate”是 world-model rollout 上的 VLM proxy。**frozen code 从真实初始帧生成视频，用 GPT-4o 五路投票打 0/0.5/1 分，默认 rollout length 40；它不能与 LIBERO/RoboCasa simulator predicate 或真实机器人成功率直接混分。[8][9]
11. **本轮只核验上游协议，不冒充本地复现。**没有下载用户 checkpoint、normalizer、dataset statistics，也没有运行 GPU rollout；所有个人数字继续位于 evidence queue。
12. **Audit E 之后可以开放通用知识页，但项目数字仍受 VOL 07 证据门禁。**知识答案可以讲 protocol 设计；个人回答必须区分“论文值、上游 runner、项目页 claim、已核验 artifact”。

## 2. 来源冻结与许可边界

| 编号 | 来源与冻结版本 | 本页采用的证据 | 不能由它证明 |
| --- | --- | --- | --- |
| [1] | `Lifelong-Robot-Learning/LIBERO` @ `8f1084e3132a39270c3a13ebe37270a43ece2a01`，`master`，MIT | task suite、pruned init、default eval、environment/controller/camera/success wrapper | UWM/Cosmos 论文一定使用默认 config；用户本地环境版本 |
| [2] | UWM arXiv `2504.02792v3`，Table II 与 Appendix A | 五任务数值、50 OOD init、3 seeds、+0.03 init shift、移除背景物体 | frozen repo 中存在 exact OOD eval code；用户 74.4% 与论文可比 |
| [3] | `WEIRDLabUW/unified-world-model` @ `b7d4067c8859775e5b08f681e76d538015cdd445`，无 LICENSE 文件 | reset-style runner、wrapper、shape、rollout defaults、inverse ablation | 代码复用许可；Google Drive checkpoint revision；Table II runtime |
| [4] | `NVlabs/cosmos-policy` @ `18a2accadf4e7a3531e56754102af5a24d2316da`，Apache-2.0 | LIBERO/RoboCasa eval CLI、init/warmup/chunk/horizon/success/seed | HF 权重商用许可；本地 baseline 或训练结果 |
| [5] | `moojink/robocasa-cosmos-policy` observed HEAD `edd9a328b3ec98050f42d194c1419307a79c4d87`，`main`，MIT，package 0.2.0 | Cosmos 安装目标在访问日的可观察语义 | Cosmos paper/runtime 实际 fork commit；安装命令未 pin |
| [6] | `robocasa/robocasa` @ `b4684e6ee37d377cc392e98302a6b916d588b415`，`main`，MIT，package 1.0.1 | 当前官方 API、controller/eval helper、determinism test 的对照 | Cosmos runner 与 v1.0.1 兼容；旧 fork 结果可直接迁移 |
| [7] | Cosmos `ROBOCASA.md` / `LIBERO.md` frozen 于 [4] | 官方命令、50 trials、3 seeds、runtime/hardware note | 用户真正执行的 CLI、完整日志、paper 数值复现 |
| [8] | WorldGym arXiv `2506.00613v3` | world model 作为 proxy environment、VLM reward 的论文主张 | simulator/real success 等价；本地 checkpoint 可用 |
| [9] | `world-model-eval/world-model-eval` @ `709665b29f5c95124e7dbc05b0d4d47cd353de97`，无 LICENSE 文件 | runner、action conversion、GPT-4o scorer、aggregate | 代码复用许可；Google Drive checkpoint hash；外部 API 可重放 |
| [10] | 本地项目页、resume 和 restructure plan | 待核验个人 claim queue | 原始 checkpoint、episode trace、贡献 ownership |

冻结 commit 只解决“本页看的是哪一版源码”，不解决 dataset/checkpoint/runtime 的版本。尤其是 Cosmos 的 RoboCasa 安装命令没有 commit pin；本页记录 observed fork HEAD 只是访问证据，不反推论文环境。

## 3. 可比性的 protocol tuple

把一次评测写成 protocol tuple：

\[
\mathcal P = (S,I,W,O,A,K,C,H,Y,R,N,M),
\]

其中：

| 字段 | 含义 | 最小证据 |
| --- | --- | --- |
| \(S\) | suite、task list、task version | task IDs、BDD/registry hash、subset |
| \(I\) | initial-state distribution | init file/hash、state index、layout/object split |
| \(W\) | warmup/stabilization | action vector、步数、是否计入 horizon |
| \(O\) | observation contract | camera keys、resolution、flip/crop/JPEG/history |
| \(A\) | action contract | dim/order/unit/frame、normalizer、clip、gripper sign |
| \(K\) | chunk/execution | predicted horizon、executed steps、replan/queue |
| \(C\) | controller/timing | controller config、control Hz、physics Hz、latency |
| \(H\) | episode horizon | task-specific max step、timeout、early termination |
| \(Y\) | success predicate | exact function、threshold、debounce、invalid episode rule |
| \(R\) | randomness | train/eval/reset/sampler seed、determinism flags |
| \(N\) | sampling plan | trials/task、seeds、macro/micro aggregation、CI |
| \(M\) | model/runtime | checkpoint SHA、config、stats、code/env/hardware |

单任务成功率只是：

\[
\hat p_t=\frac{1}{N_t}\sum_{i=1}^{N_t}\mathbb 1\{Y(\tau_{t,i})=1\}.
\]

如果 \(\mathcal P_a\neq\mathcal P_b\)，\(\hat p_a-\hat p_b\) 同时混入 model effect 与 protocol effect。任务名、分母和 success 函数相同仍不足以比较；initial-state distribution、chunk 和 controller 任一项不同都可能改变闭环轨迹。

## 4. LIBERO frozen default 到底是什么

### 4.1 Task 与 initial state

frozen benchmark 将 `LIBERO_SPATIAL`、`LIBERO_OBJECT`、`LIBERO_GOAL`、`LIBERO_90`、`LIBERO_10` 注册为 suite；每个 task 绑定 BDDL 文件与 `.pruned_init`。`get_task_init_states` 通过 `torch.load` 载入固定 simulator states。[1]

official lifelong metric 的 default contract 是：

| 字段 | Frozen default | 代码入口 |
| --- | --- | --- |
| suite task order | 10-task suite 支持 21 种 task order；default index 0 | `benchmark/__init__.py` |
| init | `.pruned_init`；按 episode index modulo state count | `metric.py:evaluate_one_task_success` |
| trials | `n_eval=20`，并行进程最多 20 | `configs/eval/default.yaml` |
| warmup | 5 次全零 7D action | `metric.py` |
| camera | agentview + eye-in-hand，128×128 | `configs/data/default.yaml` |
| low-dim | gripper qpos + joint pos | `configs/data/default.yaml` |
| action/control | 7D；`OSC_POSE`；20 Hz | `env_wrapper.py:ControlEnv` |
| horizon | eval max 600；env default horizon 1000 | eval config + env wrapper |
| success record | runner 累积 environment `done`；wrapper 的 `check_success` 转发 `_check_success` | `metric.py` + `env_wrapper.py` |
| seed | global default 10000；env 行为仍需 runtime 版本核验 | `configs/config.yaml` |

`evaluate.py` 的独立入口也固定 20 个环境、5 次 zero step，但其 warmup 后没有把返回 observation 赋回 `obs`；`metric.py` 则正确更新 `obs`。因此只说“用了官方 evaluate.py”还不够，必须记录 exact entrypoint 与 local diff。

### 4.2 “官方 LIBERO”不是唯一数字协议

LIBERO repo 提供 task、state 与 baseline helper；后续论文可以定义新的 OOD init、不同 trial count、不同 action chunk 和 horizon。合规表述是“基于 LIBERO 环境的某 protocol”，而不是把所有论文的 setting 都叫“LIBERO 官方 strict”。

## 5. UWM：Table II、repo reset 与项目 fixed-init 是三套协议

### 5.1 论文 Table II

UWM v3 Table II 的五个 task 与数值为：[2]

| Task | UWM paper mean | 当前项目页 claim | 差值只作描述 |
| --- | ---: | ---: | ---: |
| Book-Caddy | 0.91 | 44/50 = 0.88 | -0.03 |
| Soup-Cheese | 0.93 | 40/50 = 0.80 | -0.13 |
| Bowl-Drawer | 0.80 | 38/50 = 0.76 | -0.04 |
| Moka-Moka | 0.68 | 33/50 = 0.66 | -0.02 |
| Mug-Mug | 0.65 | 31/50 = 0.62 | -0.03 |
| Average | 0.79 | 186/250 = 0.744 | -0.046 |

最后一列**不能解释为模型性能差距**，因为 protocol 不同。论文明确写：LIBERO-90 pretrain 100K steps；五个 LIBERO-10 task 各用 50 demos finetune 10K steps；3 个 random seeds；50 个不同 OOD initializations；对象 initialization range 增加 0.03；删除背景物体造成视觉 shift。Table II 的 `±` 是跨 seed 的区间语义，不是单次 250 rollout 的 binomial CI。[2]

### 5.2 Frozen UWM repo 的 rollout

`eval_robomimic.py` 的实际路径是：dataset HDF5 metadata → one task env → `env.seed(e)` → `env.reset()` → observation history 重复填充 → model sample → wrapper 整段执行 action sequence → `check_success` 或 1000-step truncation。[3]

| 字段 | UWM repo runner | 与 Table II 的缺口 |
| --- | --- | --- |
| init | random reset；wrapper seed 只调用 `np.random.seed` | 没有 +0.03 / background removal manifest |
| trials | 50 | 数量相同不代表 init 相同 |
| warmup | 无 | 论文未由 repo entry 明示 |
| camera | two RGB 128，wrapper vertical flip；model resize 240 | OOD visual modification未实现 |
| chunk | sample 返回整段，wrapper for-loop 执行到 success | action horizon/endpoint依赖 model config |
| horizon | 1000 | Table II exact horizon 未由论文表格或 repo entry闭合 |
| success | `env.check_success()` | predicate family一致，environment version仍需固定 |
| checkpoint | `models.pt`；README Google Drive 无 hash | 不能绑定 paper seed/checkpoint |

`LIBEROEnvWrapper.reset_to_state` 存在，但只在 inverse-dynamics trajectory-tracking ablation 中由 `demo["states"][0]` 调用。它不能证明 policy rollout 使用 fixed init。LIBERO-90 pretraining 还在 `maybe_collect_rollout` 中被直接跳过。[3]

### 5.3 当前项目 claim 的正确层级

workspace 的 [UWM 项目页](../../05_uwm_libero_eval_protocol.html) 与 [resume restructure plan](../../../output/resume_restructure_plan.md) 写了：五任务、50/task、`.pruned_init`、5-step zero action、186/250=74.4%；另有 reset-style 232/250=92.8%。本轮没有发现对应 raw summary/checkpoint/normalizer/init index/video/action trace，所以证据层级是：

| Claim | 当前等级 | 允许表述 | 禁止表述 |
| --- | --- | --- | --- |
| 74.4% fixed-init | `CLAIM_ONLY` | “当前项目材料记录为 186/250，待 artifact 复核” | “已严格复现 Table II” |
| 92.8% reset-style | `CLAIM_ONLY / DIAGNOSTIC` | “项目材料记录的 protocol sensitivity 对照” | “UWM 正式 benchmark 92.8%” |
| 0.79 Table II | `UPSTREAM_VERIFIED` | “UWM v3 的 OOD protocol mean” | “我的 checkpoint 官方成绩” |
| 74.4 vs 0.79 | `NON_COMPARABLE` | “同任务名下的方向性上下文” | “只低 4.6pp，已接近复现” |

恢复可比性的两条路径二选一：复现 Table II 的 environment modifications + 3 seeds；或把本地 protocol 明确命名为 `fixed-pruned-init-50-v1`，只和同一 protocol 下的 baseline/checkpoint 做 paired comparison。

## 6. Cosmos LIBERO protocol

frozen Cosmos README 的 public command 使用 checkpoint `nvidia/Cosmos-Policy-LIBERO-Predict2-2B`、dataset stats、T5 embeddings、two cameras/proprio、chunk 16、open-loop 16、5 denoise steps、deterministic true、seeds 195/196/197；每 suite 10 tasks × 50 episodes。[4]

| 字段 | Frozen Cosmos LIBERO runner | 边界 |
| --- | --- | --- |
| init | official task init states；默认取 `[episode_idx]`，50 trials | 需要 state count ≥ 50；没有 modulo/bounds guard |
| env seed | `env.seed(0)` | 注释称 fixed state 下仍影响 object position |
| warmup | 10 次 `[0,0,0,0,0,0,-1]` | 与 LIBERO default 5 次全零不同；gripper语义也不同 |
| camera | agentview + wrist，environment 256，vertical flip，JPEG path | model resize另由 model family决定 |
| action | stats unnormalize；chunk 16；execute 16 | config 与 train chunk有 assert |
| horizon | spatial 220、object 280、goal 300、LIBERO-10 520、LIBERO-90 400 | 与 default 600 不同 |
| success | runner 把 `done` 直接标成 success；frozen LIBERO BDDL base 将 `done` 设为 `_check_success()` | 必须同时冻结 benchmark version，不能只看 runner |
| determinism | deterministic 模式每 policy step 重置 RNG 到 0 | 与只固定 reset seed不同 |
| aggregation | 50/task；README 说对 seeds 195/196/197 平均 | 单 seed log不能替代论文 aggregate |

这意味着 Cosmos-LIBERO、LIBERO default、UWM Table II、UWM repo reset-style 至少是四套 protocol。可以比较架构思想，不能直接比较成功率。

## 7. Cosmos RoboCasa protocol 与版本陷阱

### 7.1 Environment fork

Cosmos `ROBOCASA.md` 明确 clone `moojink/robocasa-cosmos-policy`，但没有 SHA。访问日 observed fork HEAD `edd9a...` 的 package version 是 0.2.0、MuJoCo pin 3.2.6；官方 `robocasa/robocasa` frozen `b468...` 是 package 1.0.1、MuJoCo pin 3.3.1。官方 v1.0.1 可以解释当前 API，但不能作为 Cosmos run 的环境 provenance。[5][6][7]

### 7.2 Runner contract

| 字段 | Frozen Cosmos RoboCasa | 必须保存的 artifact |
| --- | --- | --- |
| task set | runner列出 24 tasks | exact task list/registry hash |
| trials | 50/task default；README要求3 seeds | per-task per-seed summary |
| scenes | 5 个 `(layout,style)`；每 10 episodes 切一个 | episode→scene mapping |
| object split | `B` held-out objects | fork commit + object registry |
| env seed | deterministic 时 `seed = base_seed × episode_idx × 256` | seed log；episode 0 为 0 |
| warmup | 10 次全 0 的 environment-dimensional action | warmup是否计入视频/horizon |
| camera | left/right/wrist，224×224，vertical flip，JPEG input path | raw/preprocessed frame pair |
| controller | pickle `robocasa_controller_configs.pkl` | pickle SHA + decoded JSON summary |
| action | policy 7D；environment 12D 时追加 `[0,0,0,0,-1]` mobile base | action axis/unit/gripper/mobile schema |
| chunk | predict 32，execute first 16 then requery | queue/replan trace |
| horizon | task-specific 300–1000 | exact task horizon |
| success | `env._check_success()` | task class/predicate commit |
| invalid episode | data collection时少于5步只是不保存，仍已计入 success list | denominator与剔除规则须另写 |

当前 WAM 项目页写 `raw 86/120=71.67%`、`trusted 84/118=71.19%`。若“trusted”删除两个 early-success/bug episode，这已经改变分母；必须保存两条 episode ID、原始 predicate、删除理由和预注册规则。事后看视频再删 episode 只能叫 cleaned diagnostic，不能叫官方 success rate。[10]

## 8. WorldGym：world-model proxy 不等于 closed-loop benchmark

WorldGym v3 的目标是用 action-conditioned video world model 作为真实部署前 proxy；frozen repo runner 从一张 trial PNG 初始化 world model，policy 每步读取生成历史，world model 生成下一帧，再由 GPT-4o 对完整生成视频评分。[8][9]

| 字段 | Frozen code | 风险 |
| --- | --- | --- |
| initial state | root 下 PNG + JSON instruction | 静态帧不包含真实 dynamics state |
| action | policy-specific转换后 pad到10D | conversion可能改变 scale/gripper semantics |
| rollout | default 40，world model chunk size 1 | error autoregressively accumulation |
| reward | GPT-4o `n=5` votes；0/0.5/1 | API/model version、prompt与解析会漂移 |
| tie break | 优先 1，再 0.5，再 0 | optimistic tie bias |
| aggregation | trial fractional score mean | 非 simulator binary predicate |
| checkpoint | Google Drive约9GB，无 hash | runner commit不能绑定 tensor |
| license | frozen tree无 LICENSE | 暂不执行或复用代码 |

正确关系是 `offline action/video metrics → WorldGym proxy → simulator closed loop → real closed loop` 的证据阶梯，不是四个可互换的指标。WorldGym 可以筛选候选策略与发现 failure mode，但仍需 simulator/real paired validation。

## 9. Strict / reset-style / paper / proxy 可比矩阵

| 名称 | Init / reset | Warmup | Trial / seed | Horizon / chunk | 当前可比结论 |
| --- | --- | --- | --- | --- | --- |
| LIBERO frozen default | first 20 pruned states | 5 × zero7 | 20/task，default seed 10000 | 600，policy-specific single action | 只与相同 config 比 |
| UWM Table II v3 | 50 OOD init；+0.03 range；remove background | paper未由公开 runner闭合 | 50/task × 3 finetune seeds | exact eval runner未提供 | 上游论文内部可比 |
| UWM repo rollout | `env.seed(e)+reset` | none | 50/task，runner seed 0 | 1000，execute sampled sequence | reset-style；不等于 Table II |
| 项目 fixed-init claim | pruned init | 5 × zero7 | 50/task，seed artifact缺失 | chunk/horizon artifact缺失 | 74.4%待核；不与0.79直比 |
| 项目 reset claim | random reset | 项目页未闭合 | 50/task，artifact缺失 | artifact缺失 | 92.8%仅 diagnostic |
| Cosmos LIBERO | first 50 default states | 10 × close-gripper noop | 50/task × seeds 195/196/197 | 220–520，16/16 | 只与 Cosmos同 protocol 比 |
| Cosmos RoboCasa | generated scene/object split B | 10 × zero12 | 50/task × 3 seeds | 300–1000，32/16 | 需 frozen fork/controller |
| 项目 HF RoboCasa smoke | 项目页称 24×5 | 项目页未闭合 | raw120 / trusted118 | artifact缺失 | harness smoke；非官方 aggregate |
| WorldGym | real initial PNG | none | discovered PNG trials / retries | generated 40，chunk1 | VLM proxy；不与 env success 混分 |

## 10. Local evidence manifest

### 10.1 Run-level manifest

每个可对外数字必须有一个 immutable run manifest：

| 分组 | 必填字段 |
| --- | --- |
| identity | `run_id`、开始/结束时间、owner、purpose、git dirty diff hash |
| model | upstream model ID/revision、checkpoint path、SHA-256、bytes、config SHA |
| stats | action/proprio normalizer SHA、dataset stats revision、T5/tokenizer revision |
| code | policy repo SHA、eval harness SHA、benchmark/fork SHA、local patch SHA |
| runtime | Python、PyTorch、CUDA/MACA、MuJoCo、robosuite、driver、GPU/accelerator |
| protocol | \(S,I,W,O,A,K,C,H,Y,R,N\) 的结构化值 |
| outputs | raw episode JSONL、summary JSON、videos、action traces、stderr/stdout SHA |

### 10.2 Episode-level record

| 字段 | 例子 / 说明 |
| --- | --- |
| task identity | suite、task ID、language、BDD/task class hash |
| episode identity | episode index、seed、init state index/hash、layout/style/object split |
| observation | camera keys、first-frame SHA、preprocessed-frame SHA |
| action | normalized/raw action、timestamp、chunk index、executed count、clip flag |
| result | success bool、predicate output、step、timeout、exception |
| failure | perception、action-scale、gripper、contact、recovery、protocol、infra |
| artifacts | video path/SHA、trace path/SHA、checkpoint SHA |

### 10.3 当前 workspace 证据缺口

本轮只扫描 `C:\Users\mousongzhe\cv`。发现 resume、project HTML 与 roadmap claim，未发现 UWM/WAM raw checkpoint、normalizer、per-episode JSON/CSV、rollout videos、exact eval config、controller dump 或 local diff。因此：

| 项目 claim | 当前证据 | 下一件最小补证据 |
| --- | --- | --- |
| UWM 186/250 | resume + project page | per-task summary + 250 episode IDs + checkpoint/config/stats SHA |
| UWM 232/250 | project page | same checkpoint paired protocol manifest + init distribution diff |
| UWM 对齐 Table II | paper task names相同 | OOD env patch、50 init manifest、3 seeds；否则改名 local fixed-init |
| WAM 84/118 | project page | raw 120 records、2 deleted IDs、predeclared validity rule、HF revision |
| WAM local 0-success | project narrative | load log、checkpoint SHA、action/gripper stats、failure videos |
| MSE 0.09718→0.05349 | project narrative | split/metric script、prediction/label tensors、paired checkpoint |

## 11. 失败分类与归因顺序

| Failure family | 先查 artifact | 可下结论前需要 |
| --- | --- | --- |
| protocol | init/warmup/horizon/success/denominator diff | same checkpoint paired rerun |
| checkpoint | SHA、missing/unexpected keys、EMA/normalizer | load log + tensor stats |
| observation | camera key、flip/crop/JPEG/history | raw/preprocessed frame pair |
| action | axis/unit/frame/gripper/clip | normalize round-trip + action trace |
| chunk/control | predicted vs executed、queue、controller Hz | timestamped command/state trace |
| perception | target localization、occlusion、language mismatch | image overlays + policy attention/probe |
| contact | grasp pose、friction、collision、gripper force | simulator state/contact trace |
| recovery | first error后是否重规划、OOD state | failure timeline + counterfactual reset |
| infrastructure | exception、timeout、OOM、dropped episode | stderr + exit code + denominator rule |

诊断顺序应先排 protocol/checkpoint/observation/action contract，再讨论模型机制。否则“world model 没学到 contact”可能只是图像上下翻转或 gripper sign 错。

## 12. Protocol gate 伪代码

```python
# Protocol comparison gate: compare fields before comparing scores.
REQUIRED = [
    "suite", "tasks", "init", "warmup", "observation", "action",
    "chunk", "controller", "horizon", "success", "randomness",
    "trials", "checkpoint", "runtime",
]

def compare_runs(run_a, run_b):
    # Missing values are not wildcards; they block a strong comparison.
    missing = [k for k in REQUIRED if not run_a.get(k) or not run_b.get(k)]
    if missing:
        return {"verdict": "UNKNOWN", "missing": missing}

    mismatches = {
        k: (run_a[k], run_b[k])
        for k in REQUIRED
        if canonicalize(run_a[k]) != canonicalize(run_b[k])
    }
    if mismatches:
        return {
            "verdict": "NON_COMPARABLE",
            "mismatches": mismatches,
            "allowed_claim": "protocol sensitivity or directional context only",
        }

    # Score comparison opens only after artifact and protocol identity checks pass.
    assert sha256_exists(run_a["episodes"])
    assert sha256_exists(run_b["episodes"])
    return paired_or_interval_test(run_a, run_b)
```

这个 gate 故意把 unknown 当 blocker。面试中最危险的不是承认 unknown，而是把 unknown 默认为相同。

## 13. 面试回答骨架

### 13.1 30 秒：什么叫 strict eval

“我不会把 strict 当成‘跑得更认真’，而是把评测写成可重放 tuple：task、init、warmup、camera、action/normalizer、chunk/replan、controller、horizon、success、seed、trials 和 checkpoint/runtime。只有这些字段相同，成功率差值才主要反映模型。以 UWM 为例，论文 Table II 是五个 LIBERO-10 任务上的 OOD 初始化，还扩大 object init range 并移除背景物体；repo 默认 runner 则是 random reset。我的 fixed-pruned-init 结果必须单独命名，不能只因任务相同就说严格复现 0.79。”

### 13.2 90 秒：怎样讲当前 UWM 项目

“这个项目目前最可信的贡献方向是评估协议工程，而不是宣称超过论文。项目材料记录五个任务 fixed-init 186/250，以及 random-reset 232/250；我会把后者只当 protocol sensitivity diagnostic。进一步 source audit 后，我发现论文 v3 的 0.79 使用 50 个 OOD initialization、三次 finetune seed，并做 +0.03 object-init shift 和背景物体移除，所以本地 pruned-init 不能叫 Table II strict aligned。下一步我会冻结 checkpoint、normalizer、250 条 episode trace、init index、warmup、chunk/horizon 与 harness diff；若复现论文环境改造，就报告 three-seed OOD result；否则把协议正式命名为 fixed-pruned-init-50-v1，只和同协议 baseline 做 paired comparison。”

### 13.3 RoboCasa 71.19% 的防守口径

“71.19% 是官方 HF checkpoint 在我这套 harness 上的 smoke result，不是我的训练结果，也不是官方 50 trials × 3 seeds protocol。项目页记录 raw 86/120 和 trusted 84/118，说明我还必须给出被剔除的两条 episode、预先定义的 invalid rule、fork/controller/checkpoint revision；在这些 artifact 齐全前，我只用它证明 harness 能产出非零可信行为，不把它当正式 benchmark。”

## 14. 尚未核实与下一步

- 已核实：LIBERO default eval code；UWM v3 Table II 与 Appendix OOD setting；UWM frozen reset-style runner；Cosmos LIBERO/RoboCasa frozen runners；RoboCasa official/fork version split；WorldGym frozen proxy scorer。
- 尚未核实：用户 local repos/runs、checkpoint tensor、normalizer、dataset revision、250/250 episode artifacts、RoboCasa 120 raw episodes、controller pickle semantic dump、browser visual QA、独立 fact review、真实口述。
- 当前 verdict：`WARN`。原因不是上游来源不足，而是个人数字与 runtime artifact 尚未闭合，且“Table II strict aligned”表述已被 source audit 发现 protocol mismatch。
- 后续动作：WM-039..044 的第一批 benchmark/evidence 知识页与 6 张题卡已完成；下一步独立事实复核并补 local run artifacts。所有题卡保持 `unseen`，项目数字不进入强答案，直到 VOL 07 evidence gate 通过。

## 15. 参考文献（References）

1. Lifelong Robot Learning, `LIBERO` frozen commit `8f1084e3132a39270c3a13ebe37270a43ece2a01`: [metric.py](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/lifelong/metric.py), [eval config](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/configs/eval/default.yaml), [environment wrapper](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/envs/env_wrapper.py), [benchmark registry](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/8f1084e3132a39270c3a13ebe37270a43ece2a01/libero/libero/benchmark/__init__.py), MIT.
2. Zhu et al., “Unified World Models: Coupling Video and Action Diffusion for Pretraining on Large Robotic Datasets”, arXiv `2504.02792v3`, [Table II](https://arxiv.org/html/2504.02792v3#S4.T2) and Appendix A, accessed 2026-07-16.
3. WEIRDLabUW, `unified-world-model` frozen commit `b7d4067c8859775e5b08f681e76d538015cdd445`: [eval_robomimic.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/experiments/uwm/eval_robomimic.py), [wrappers.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/environments/robomimic/wrappers.py), [template config](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/configs/template_train_robomimic.yaml); no license file found in frozen tree.
4. NVIDIA, `cosmos-policy` frozen commit `18a2accadf4e7a3531e56754102af5a24d2316da`: [LIBERO runner](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/libero/run_libero_eval.py), [LIBERO utils](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/libero/libero_utils.py), [RoboCasa runner](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/robocasa/run_robocasa_eval.py), Apache-2.0 code.
5. `moojink/robocasa-cosmos-policy`, observed HEAD `edd9a328b3ec98050f42d194c1419307a79c4d87`, [setup.py](https://github.com/moojink/robocasa-cosmos-policy/blob/edd9a328b3ec98050f42d194c1419307a79c4d87/setup.py), [eval helper](https://github.com/moojink/robocasa-cosmos-policy/blob/edd9a328b3ec98050f42d194c1419307a79c4d87/robocasa/utils/eval_utils.py), MIT; observed 2026-07-16, not a verified paper pin.
6. RoboCasa, official repo frozen commit `b4684e6ee37d377cc392e98302a6b916d588b415`, [setup.py](https://github.com/robocasa/robocasa/blob/b4684e6ee37d377cc392e98302a6b916d588b415/setup.py), [eval_utils.py](https://github.com/robocasa/robocasa/blob/b4684e6ee37d377cc392e98302a6b916d588b415/robocasa/utils/eval_utils.py), [determinism test](https://github.com/robocasa/robocasa/blob/b4684e6ee37d377cc392e98302a6b916d588b415/tests/test_env_determinism.py), MIT.
7. NVIDIA Cosmos Policy frozen docs: [LIBERO.md](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LIBERO.md), [ROBOCASA.md](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/ROBOCASA.md).
8. Quevedo et al., “WorldGym: World Model as An Environment for Policy Evaluation”, arXiv `2506.00613v3`, [abstract](https://arxiv.org/abs/2506.00613v3), 2025.
9. `world-model-eval/world-model-eval` frozen commit `709665b29f5c95124e7dbc05b0d4d47cd353de97`: [README](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/README.md), [utils.py](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/utils.py), [world_model.py](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/world_model.py); no license file found in frozen tree.
10. 本地待核验材料：[UWM/LIBERO 项目页](../../05_uwm_libero_eval_protocol.html)、[Cosmos/WAM 项目页](../../04_cosmos_wam_multitask_training.html)、[resume restructure plan](../../../output/resume_restructure_plan.md)、[optimized resume](../../../output/mousongzhe_resume_optimized.html)。
