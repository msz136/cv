# PROJ-UWM-001..004 从项目实现反推的证据约束口述稿

> 状态：`implementation_derived_model_answer / evidence_bounded / not_candidate_transcript / unseen`
> 更新日期：2026-07-22
> 题目：如何介绍 UWM/LIBERO 项目，并解释训练适配、strict/reset 协议、DataLoader stall、ownership 与 RoboCasa 闭环失败？

## 1. 项目定位：讲协议工程，不讲架构原创

这个项目最可信的定位不是“我提出了 UWM 新架构”，而是：在 C500/MACA 环境中开展 UWM 的 LIBERO-90→LIBERO-10 task-specific fine-tune 与闭环评估，对齐数据、训练和 rollout 协议；再把这些合同迁到 RoboCasa，定位 action/state/prompt/normalizer/execution 不一致导致的 train-to-closed-loop 断层。

回答顺序固定为：目标与职责 → 数据/模型/训练链路 → 评估 tuple → 一个 bad case → 结果证据等级 → ownership 与未闭合项。不要先报 `0.744`，也不要把低训练 loss 说成闭环性能提升。

## 2. 30 秒版本

> 我做的是 UWM 从 fine-tune 到闭环评估的协议工程。在 LIBERO 路线，我把五个 LIBERO-10 task 分别接入两路 RGB、7D action、16-step chunk 的训练与 rollout，区分 `env.seed+reset` 和 fixed `pruned_init` 两套评估，并用 DataLoader-only A/B 定位 Zarr 随机读取等待。用户确认的 fixed-init 结果是 `186/250`，但本地没有对应五个 checkpoint 和 250 条 episode raw bundle；RoboCasa actionheadfix 则是训练完成但闭环只有 `0–2/54` 的失败链。所以我讲协议对齐、工程诊断和结果边界，不称 UWM 架构原创或 benchmark 完成。

## 3. 2–3 分钟主叙事

> 项目最初是把 UWM 的 `libero_90.pt` 迁到 RoboCasa，但 action order、state/prompt、normalizer 和 eval harness 没有形成闭环，所以我先回到 UWM/LIBERO 路线建立可解释的训练—评估基线。
>
> 数据侧，项目把五个 LIBERO-10 HDF5 task 各自转成 compressed Zarr buffer。每个训练 window 长 19：前 2 帧作为当前两路 RGB 观测，中间对齐 16 个 7D action，最后 2 帧作为 future observation target。LIBERO adapter 明确关闭 low-dim 和 language 输入；这些是当前 route 的接口，不代表 UWM 在所有数据上都只有这两种输入。
>
> 训练侧，从 `libero_90.pt` strict-load task-specific 模型，8 卡 DDP 训练；image encoder 使用 base learning rate 的 `0.05` 倍，其余参数使用 base learning rate。这里不是一个共享五任务 checkpoint：Book-Caddy 指向单独的 6000-step run，其余四个 task 指向 bs64 epoch-aligned run。所谓 aligned 是把官方 `20k steps × 36 × 2 GPUs` 换算为本地 `64 × 8 GPUs` 下相近的 nominal epoch 数，得到约 `2728–2814` 个 optimizer steps，不是证明优化轨迹与官方一致。
>
> 评估侧，`uwm_reset` 用 `env.seed(e)+env.reset()`；`libero_fixed_init` 按 `.pruned_init` index reset，并先执行 5 个 zero-action warmup。每个 task 50 条 episode，被拆成 8 个 shard；每条记录保存 seed、init index、success 和 policy-action count，task/global summary 用 completed episodes 作分母。用户确认的 fixed-init summary 是 `44/50、40/50、38/50、33/50、31/50`，合计 `186/250=0.744`；旧 reset-style 是 `232/250=0.928`。两者只能说明 protocol sensitivity，论文 Table II 还有 OOD init、object shift、背景和多 seed 差异，不能横比。
>
> 实现复核还有三个边界。第一，LIBERO evaluator 只读取 `ckpt["model"]`，没有读取 action normalizer；base checkpoint 中 normalizer 也是 `None`，因此不能说这条路径“加载并固定了 target normalizer”。第二，五个 task 使用 task-specific checkpoint，不能讲成一次 multi-task fine-tune。第三，聚合器虽然记录 expected=50，却没有 assert completed=50；当前 `186/250` 依赖用户确认的五个 50-rollout summary，本地 raw episode 不在。
>
> 工程 bad case 是周期性 DataLoader wait。finite sampler 的 p95 约 `13.862s`，只换 infinite sampler 仍约 `13.183s`，preload+infinite 后约 `0.194s`。这支持随机 Zarr 读取是主要等待来源，但还不是 GPU 训练吞吐提升。RoboCasa 侧也保持失败结论：actionheadfix 30-epoch run 的 action loss 从 `2.4300` 降到 `0.07689`，而 full-h4 仍 `0/54`、`45/54` 仅发生 robot-env contact。我的结论是训练拟合没有转化为任务成功，下一步要追 expert→x0→sampled→converted→executed action 的 first divergence。

## 4. LIBERO-only 90 秒版本

> LIBERO 这条线不是训练一个五任务统一策略，而是把五个 LIBERO-10 task 分别从 `libero_90.pt` 继续训练。数据是两路 `128×128` RGB 和 7D action；window 长 19，模型用 2 帧历史、预测 16-step action chunk 和 2 帧未来观测。模型配置是 ResNet observation encoder、768 hidden、12 层、12 heads、24 registers、100-step diffusion training schedule 和 10-step inference schedule；这是上游 UWM 架构在本地 adapter 中的实例化，不是我的原创。
>
> 训练适配的关键不是直接照搬 20k optimizer steps。官方口径是 per-device batch 36、2 卡；本地是 64、8 卡，所以脚本按每个 task 的 sequence 数换算 nominal epochs，remaining four 得到约 2.7k–2.8k steps；Book-Caddy 仍来自独立 6000-step run。评估再区分 reset-style 和 fixed-pruned-init：后者 5-step zero-action warmup、50 rollouts/task、8 shard。用户确认 fixed-init 为 `186/250`，但 checkpoint/hash/250 episodes 没同步，因此只作为 user-confirmed summary。实现上 evaluator 只 strict-load model weights，没有加载 normalizer；聚合器也没有强制 completed 等于 expected。这两点是我面试中会主动说明的证据边界。

## 5. 从实现讲清数据、训练与评估

### 5.1 数据 window 如何形成

`libero_official_common.py` 固定五个 task、两路 RGB `agentview_rgb` / `eye_in_hand_rgb` 与 7D action。`prepare_libero_buffers.py` 检查每个 task 50 个 episode，将 HDF5 写入 compressed Zarr，并在该 route 中设置 `flip_rgb=True`。

`process_batch` 对长度 19 的 window 做以下切分：

```python
# obs_horizon=2, action_horizon=16, seq_len=19
action_start = 1
action_end = 17
curr_obs = obs[:, :2]       # 两帧当前观测
actions = action[:, 1:17]   # 16×7 action chunk
next_obs = obs[:, 17:]      # 两帧 future observation target
```

口述时要强调：该 LIBERO route 的 `use_low_dim=False`、`use_language=False`；RoboCasa route 的 state/prompt/right-view 是另一套输入合同，不能倒灌进 LIBERO 结果解释。

### 5.2 模型与训练入口

本地 evaluator 实例化的接口为：2-frame observation、`action_len=16`、`action_dim=7`、ResNet encoder、768 embedding、latent patch `[2,4,4]`、12 layers/12 heads、24 registers、100 diffusion train steps 和 10 inference steps。训练 `train_one_step` 同时把 `curr_obs`、`next_obs` 和 action chunk 送入 UWM；shared action/video diffusion 机制属于上游。

`train_robomimic.py` 在 pretrain load 后把 image encoder 参数单独分组为 `0.05×base_lr`，其余 trainable 参数使用 base lr，再包 DDP。`save_every=999999` 不代表不保存：`maybe_save_checkpoint` 仍在 final step 写 `models.pt`。

### 5.3 为什么本地不是简单跑 20k steps

脚本先计算每个 task 在官方与本地 world-size/batch 下的 steps per epoch，再按 nominal epoch 数换算：

\[
N_t^{\mathrm{local}}
=\left\lceil
N^{\mathrm{official}}
\frac{S_t^{\mathrm{local}}}{S_t^{\mathrm{official}}}
\right\rceil,
\qquad N^{\mathrm{official}}=20000.
\]

变量解释：`S` 是脚本用 per-rank sample 数和 per-device batch 计算的 steps per epoch；`t` 表示 task。直觉上，这保留的是近似训练 epoch 数，不是 optimizer update 数、样本顺序或数值轨迹。实现映射是 `remote_muxi_libero_remaining4_bs64_aligned_queue.sh::steps_per_epoch/task_steps`。

| Task | train sequences | official steps/epoch | local steps/epoch | aligned optimizer steps | 实际 checkpoint route |
| --- | ---: | ---: | ---: | ---: | --- |
| Book-Caddy | 8243 | 114 | 16 | 2808（公式值） | 严格评估 launcher 实际指向独立 6000-step run |
| Soup-Cheese | 12102 | 168 | 23 | 2739 | remaining4 bs64 aligned run |
| Bowl-Drawer | 11104 | 154 | 21 | 2728 | remaining4 bs64 aligned run |
| Moka-Moka | 18957 | 263 | 37 | 2814 | remaining4 bs64 aligned run |
| Mug-Mug | 11542 | 160 | 22 | 2750 | remaining4 bs64 aligned run |

因此安全表达是“按 task sequence 数做 epoch-aligned step conversion，并使用 task-specific checkpoints”，不是“完全复现官方 20k-step training”。

### 5.4 两套 rollout protocol

| 字段 | `uwm_reset` | `libero_fixed_init` |
| --- | --- | --- |
| reset | `env.seed(seed); env.reset()` | `reset_to_state(pruned_init[index])` |
| init index | 无 | `(init_start+episode) % len(init_states)` |
| warmup | 0 | 5 个 shape `(1,7)` zero actions |
| rollout horizon | 必须看 launcher；evaluator default 1000 | strict launcher 显式传 600，并将 warmup 加到 env max length |
| success | episode 终止时 `bool(info.get("success", False))` | 同左 |
| artifact | shard `episodes.jsonl/summary.json` | 同左，另有 init path/count |

8 shard 对 50 条 episode 的分配是 `7,7,6,6,6,6,6,6`；seed 与 init-start 用相同 offset，目标是覆盖 0–49 且不重叠。并行发生在同一 task 的 shard 内，五个 task 仍按 launcher 顺序处理。

### 5.5 结果分母与聚合风险

代码中的 task/global success rate 都按实际写入的 episode 数计算：

\[
\widehat{p}
=\frac{\sum_{i=1}^{N_{\mathrm{completed}}}\mathbf{1}[s_i=1]}
{N_{\mathrm{completed}}}.
\]

变量解释：`s_i` 是 episode 最终 `info["success"]`；分母是 `num_rollouts_completed`，不是配置的 `num_rollouts_expected`。直觉上，如果一个 shard 没写出 episode，聚合结果仍可能生成但分母变小。实现映射是 5-task parallel launcher 的 per-task/global Python aggregator；当前缺少 `completed==expected` 的 fail-closed assertion。

用户确认的 fixed-init per-task summary为：

| Task | Successes / assumed 50 | Rate |
| --- | ---: | ---: |
| Book-Caddy | 44/50 | 0.88 |
| Soup-Cheese | 40/50 | 0.80 |
| Bowl-Drawer | 38/50 | 0.76 |
| Moka-Moka | 33/50 | 0.66 |
| Mug-Mug | 31/50 | 0.62 |
| 合计 | 186/250 | 0.744 |

这是 `user-confirmed-remote-final`，不是本地由 250 行 JSONL 复算出的 C3 artifact。

## 6. RoboCasa actionheadfix：90 秒专项版本

> RoboCasa 的接口与 LIBERO 不同：旧 base 是 7D action、两路视觉且无 state/language；target route 使用 reordered 12D action，并加入 task、prompt、16D state 和 right-view。actionheadfix 用 shape-compatible partial load：478 个 target keys 中 446 matched，7D→12D action encoder/decoder 的 8 个 key 重置，其余新增条件模块按 missing-init 处理。
>
> 30-epoch run 在 8 卡上完成 3930 steps，打印 total/action/raw-action loss 从 `3.3257/2.4300/0.9986` 降到 `0.25385/0.07689/0.03043`，但 `val_ratio=0`。同 checkpoint 和 normalizer 的八组 54-scenario rollout 都没有 env error，full h1/h2/h4/h5/h8 只有 `2/1/0/1/1` success，no-prompt/no-right/no-state h5 为 `2/2/1`；成功只集中在 Kettle 或 Microwave。h4 虽有 `45/54` robot-env contact，仍是 `0/54` task success。
>
> 我把 execution error 与策略失败分开：native direct `0/6`、env errors 0，是有效但失败的 rollout；strict OpenPI-style `convert_action` `0/6`、env errors 6，全部在 step 0 因 `expected 12, got 5` 退出，不能计成六条模型失败。安全结论是“接口错误被定位，训练 fit 到闭环成功仍未闭合”，不是“actionheadfix 修复成功”。

## 7. Run ledger：哪些结果能放在同一张表

| Run / 阶段 | Checkpoint / schedule | Protocol | Denominator | 结果 | 可说什么 |
| --- | --- | --- | --- | --- | --- |
| Book-Caddy early | task-specific 6000-step `models.pt` | reset-style parallel rollout | report 50 | `42/50=0.84` | 单任务 report-supported；不等于五任务结果 |
| Five-task reset-style | Book 6000 + remaining4 aligned task checkpoints | `env.seed+reset` | user-confirmed 250 | `232/250=0.928` | protocol diagnostic，不是 uplift |
| Five-task fixed-init | 同一 launcher 的 task-specific checkpoint mapping | `pruned_init` + 5 warmup + horizon 600 | user-confirmed assumed 50/task | `186/250=0.744` | 项目 fixed-init summary；raw bundle缺 |
| Paper Table II | upstream recipe / 3 seeds | OOD init + object shift + background changes | paper protocol | 约 `0.79` | 只作上游上下文，不与本地直接减法归因 |
| RoboCasa actionheadfix | remote 30-epoch / 3930-step run | 18 tasks×3 scenarios，multiple horizons/inputs | raw 54 per setting | `0–2/54` | train→closed-loop failure，不称 benchmark success |

## 8. Evidence Contract

| Claim | 证据 | 等级 | 当前能否强说 |
| --- | --- | --- | --- |
| 五 task、两路 RGB、7D action | `libero_official_common.py` | `local-direct / C1` | 可讲 adapter contract |
| 2 obs +16 actions +2 future obs | dataset `seq_len=19` + `process_batch` | `local-direct / C2` | 可现场解释 tensor slicing |
| ResNet/768/12-layer/24-register/16×7/10-step inference | evaluator `build_model` | `local-direct / upstream-instance` | 可讲实例化，不说个人架构原创 |
| image encoder `0.05×lr`、DDP、final save | trainer patch | `snapshot-local / C1-C2` | 可讲代码路径；个人函数 ownership待确认 |
| task-specific/mixed schedule checkpoints | 5-task launcher checkpoint mapping | `local-direct / C2` | 必须纠正 multi-task checkpoint 说法 |
| epoch-aligned约2728–2814 steps | bs64 aligned queue arithmetic | `local-direct / C2` | 可讲 nominal epoch conversion，不说同优化轨迹 |
| fixed-init/warmup/8-shard/50 rollout | evaluator + parallel launcher | `local-direct / C2` | 可讲协议与设计取舍 |
| evaluator不加载normalizer | `build_model` 只读取 `ckpt["model"]` | `local-direct / negative code evidence` | 应主动说明；不能说 target normalizer 被固定 |
| `186/250=0.744` | user-confirmed remote JSON | `user-confirmed / raw-missing` | 只能带 provenance |
| `232/250=0.928` | reset-style report context | `protocol-diagnostic` | 不能讲模型 uplift |
| DataLoader p95 `13.862→0.194s` | DataLoader-only benchmark/report | `smoke-bounded / C2` | 可讲 wait first-divergence，不报 GPU uplift |
| Actionheadfix h4 `0/54`、contact `45/54` | ActionHeadFix P0 Audit | `remote-snapshot-raw / checkpoint-unverified` | 可讲 run-specific failure，不称 benchmark完成 |
| 个人 ownership | UWM Ownership Ledger + 用户范围自述 | `self-report / role-confirmation-pending` | 可说做了 fine-tune/eval/protocol alignment；逐函数仍保守 |

## 9. 关键问题三档回答

### 9.1 “0.744 能写成我复现了官方 UWM 吗？”

**危险回答**：可以，我严格复现了官方 UWM，成功率 74.4%，只比官方低 4.6pp。

**可过回答**：这是远端 fixed-init 结果，但与论文还有一些设置差异。

**强回答**：

> 我不会写成严格复现。`186/250` 是用户确认的项目 fixed-pruned-init summary，本地缺五个 target checkpoint、250 条 episode、scorer 和完整 manifest；论文 Table II 使用 OOD init、object shift、背景调整和多个 finetune seeds。它可以证明我做过协议对齐和结果 reconciliation，但当前不是与论文完全同口径的 C3 benchmark。

### 9.2 “0.928 更高，为什么不报它？”

**危险回答**：因为我们的模型比官方更强，超过了 13.8pp。

**可过回答**：reset-style 更容易，所以不作为正式结果。

**强回答**：

> `0.928` 和 `0.744` 的模型权重映射大体来自同一 task-specific run family，但 init distribution 明确不同，旧 run 的 exact horizon/raw manifest 也没有完整同步。它首先是 protocol sensitivity diagnostic。只有同 checkpoint、同 horizon、同 seed/init mapping、同 scorer 的 paired episodes，才能把差异归因到 reset protocol；更不能用它和论文 0.79 做模型 uplift。

### 9.3 “你到底有没有用 normalizer？”

**危险回答**：用了，所有 checkpoint 都绑定了 action normalizer。

**可过回答**：checkpoint里可能有，但现在缺 hash。

**强回答**：

> 对 LIBERO 这条 evaluator，我从代码只能确认 `torch.load` 后 strict-load `ckpt["model"]`，没有读取 `action_normalizer`；本地 base `libero_90.pt` 的 normalizer 字段也是 `None`。因此我会把“normalizer presence/usage”登记为协议字段，但不会说这条 rollout 加载了 target normalizer。RoboCasa route 有独立 normalizer 证据，不能和 LIBERO 混用。

### 9.4 “五个任务是不是一个 multi-task checkpoint？”

**危险回答**：是，我训练了一个覆盖五任务的 UWM 模型。

**可过回答**：五个任务分别训练，但一起评估。

**强回答**：

> 是 task-specific fine-tune。launcher 对 Book-Caddy 映射独立 6000-step checkpoint，对其余四个任务映射各自的 bs64 epoch-aligned checkpoint。五任务只在结果聚合层汇总，模型权重不是一个共享 multi-task binary。

### 9.5 “186/250 的分母可靠吗？”

**危险回答**：脚本配置50条，所以一定是250条。

**可过回答**：用户确认每个任务50条，但本地没有raw。

**强回答**：

> 当前数字依赖用户确认的五个 50-rollout summary。代码层 aggregate 用 `num_rollouts_completed` 作分母，虽然保存 expected=50，但没有 fail-closed assert；如果 shard 缺失，仍可能生成缩小分母的 summary。所以升级到 C3 前必须拿到五个 task summary、250 行 episode JSONL，并校验 seed/init 0–49 无重缺。

### 9.6 “DataLoader stall 已经解决了吗？”

**危险回答**：解决了，训练速度提升了七十多倍。

**可过回答**：DataLoader-only wait 明显下降，但完整训练还需验证。

**强回答**：

> 我定位了 DataLoader wait 的 first divergence：finite 和 infinite-only 的 p95 都在约 13 秒，preload+infinite 降到 0.194 秒，说明主要矛盾是 Zarr 随机读取而不是单纯 epoch iterator 重建。但没有 matched GPU samples/s、显存、loss parity 和长期稳定性，因此只能说数据等待 smoke 改善，不能报端到端训练 uplift。

## 10. PROJ-UWM-002：哪些部分能说是我做的

### 10.1 30 秒 ownership 版本

> 用户范围自述已经确认我做过 UWM/LIBERO fine-tune、eval，以及 UWM/RoboCasa 的协议对齐和训练评估。因此我可以说“我开展、运行、对齐、审计并定位了这些链路”。但 `0341c50` 是一次性 recovery snapshot，Git author 不能证明每个函数独立编写；UWM shared diffusion 属于 upstream，`186/250` 仍是 user-confirmed summary。现场我会落到一个具体 launcher/evaluator 解释输入、协议分支、artifact 和限制，不把整仓库认领为原创。

### 10.2 Role matrix

| 层 | 当前可核事实 | 安全第一人称 | 禁止自动升级 |
| --- | --- | --- | --- |
| UWM architecture | upstream shared action/video diffusion | “我基于 UWM 做适配” | “我设计了 UWM” |
| LIBERO fine-tune | 用户自述 + local launcher/patch | “我开展/运行了 task-specific fine-tune” | “所有 trainer 函数由我独立编写” |
| eval protocol | 用户自述 + reset/fixed code | “我对齐并审计了评估协议” | “0.744 是本地 raw verified benchmark” |
| DataLoader | local benchmark/patch | “我定位了 data-wait first divergence” | “我证明了完整训练吞吐提升” |
| RoboCasa | 用户自述 + raw run audit | “我尝试迁移并做失败诊断” | “RoboCasa benchmark 已完成” |
| result operation | remote path + user-confirmed JSON | “我记录并核对了结果边界” | “我拥有 checkpoint/operator/reviewer 全链路” |
| Codex/interview pages | 当前 `cv` 仓库产物 | “我用材料复盘口述” | 把生成页算作原项目工程贡献 |

### 10.3 Ownership 追问树

```text
你具体做了什么？
  ├─ 训练：指出一个 launcher/config override，解释输入、checkpoint 和输出。
  ├─ 评估：解释 reset_to_state、warmup、8-shard、success 与 denominator。
  ├─ 数据：解释 seq_len=19、preload/infinite A/B 和验证范围。
  ├─ 结果：区分 user-confirmed、local-direct、remote-snapshot-raw。
  └─ 边界：说明 upstream、协作/工具、远端 operator 和个人动作。
```

最小表达合同：先说“我做过的范围”，再说“实现里能证明的机制”，最后说“不能从快照证明的 ownership”。

## 11. P9 面试就绪度

### 11.1 Role Fit 与 JD Mapping

| VLA 岗能力 | 项目证据 | 强度 | 面试策略 |
| --- | --- | --- | --- |
| 多模态/action接口 | 两路RGB、2-frame obs、16×7 action、future obs | 强 | 现场画 tensor timeline |
| 分布式训练迁移 | 8卡DDP、lr分组、epoch-aligned steps、final checkpoint | 中强 | 解释为何不能照搬20k steps |
| Closed-loop eval | reset/fixed init、warmup、shard、success predicate | 强 | 先报协议tuple再报数字 |
| 数据工程 | HDF5→Zarr、preload/infinite benchmark | 中强 | 只报DataLoader-only范围 |
| 跨benchmark迁移 | LIBERO 7D→RoboCasa 12D/state/prompt/view | 中 | 以失败链展示诊断能力 |
| Ownership/结果可信度 | self-report+snapshot+user-confirmed/raw audit | 中弱 | 主动降级强结果，绑定证据等级 |

### 11.2 Truth Boundary

- **做过范围**：UWM/LIBERO fine-tune 与 eval；UWM/RoboCasa 尝试；协议对齐与训练评估。
- **本地实现直接支持**：task/data/model interface、trainer/evaluator/launcher、stall smoke、RoboCasa raw sweep。
- **只能 user-confirmed**：LIBERO fixed-init `186/250` 及每任务结果。
- **不能写**：UWM architecture 个人原创、一个共享五任务 checkpoint、LIBERO evaluator 已加载 normalizer、Table II 严格复现、RoboCasa 性能修复完成。

### 11.3 Production Gap

| 缺口 | 面试官会问 | 最小补件 |
| --- | --- | --- |
| Target checkpoints | 五个 `models.pt` 是什么hash？ | task→checkpoint SHA、step、fresh-load |
| Denominator | 真有250条吗？ | merged JSONL + expected/completed assertion |
| Protocol parity | reset/fixed是否只差init？ | same-checkpoint paired run + exact horizon/env revision |
| Normalizer | 哪条路径用了哪个统计？ | presence/absence manifest；不得假设 |
| GPU throughput | preload是否端到端有效？ | 30–100 step matched GPU A/B |
| Failure taxonomy | soup/mug为何低？ | video/action/state/terminal trace |
| Ownership | 谁写、谁跑、谁review？ | per-file role + shell/run/review record |

### 11.4 SP/SSP 证据就绪度

当前材料就绪度为 `20.6/30`：岗位相关性 `4.5`、机制深度 `4.4`、工程闭环 `3.8`、指标可信度 `2.6`、ownership `2.1`、抗追问 `3.2`。这不是候选人能力分；提升来自实现合同更清晰，checkpoint/raw/operator 缺口仍是一票否决项。

### 11.5 补强计划与简历三档

| 时间 | 动作 | 状态 |
| --- | --- | --- |
| 半天 | 口述一个 task 的 data→train→eval；确认具体亲手/协作/工具角色 | `可补做` |
| 1天 | 为 aggregator 加 completed==expected、seed/init uniqueness gate；整理现有 raw | `可补做` |
| 3天 | 同 checkpoint paired reset/fixed eval；冻结env/scorer/horizon | `可补做` |
| 1周 | 获取五checkpoint与250 episodes；做GPU stall matched A/B和failure taxonomy | `可补做` |

- **当前保守版**：开展 UWM/LIBERO task-specific fine-tune 与闭环评估，对齐 fixed-init/reset 协议，定位 Zarr/DataLoader wait，并分析 RoboCasa 跨接口训练—闭环失败。
- **补 ownership 后标准版**：负责指定 launcher/evaluator/loader 适配与协议验收，以文件、命令和 artifact 说明个人边界。
- **C3 后偏强版**：只有补齐 checkpoint、episode、scorer、paired eval 与 GPU A/B 后，才能写可复算结果和端到端工程收益。

## 12. 练习边界

- 这是从实现反推的 model answer，不是候选人的真实 transcript。
- `PROJ-UWM-001..004` 继续保持 `unseen`；不创建 `coaching_state.md`。
- 真实口述时先答一题，不把本页四题自动计为已练习。
- `0.744` 标记 `user-confirmed-remote-final`；RoboCasa actionheadfix 标记 `remote-snapshot-raw / checkpoint-unverified`。
- 任何“我修改了某函数”的表述仍需本人按 ownership ledger 确认。

## 13. Implementation Anchors 与 References

### 13.1 现场可解释的 anchors

| Anchor | Locator | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| A1 | `scripts/libero_official_common.py:17-47` | 五task与HDF5映射 | 选择者个人ownership |
| A2 | `scripts/libero_official_common.py:41-48` | 两路RGB与7D action | 所有UWM数据schema |
| A3 | `scripts/prepare_libero_buffers.py:61-99` | 50 episode检查、seq_len19、flip_rgb、Zarr | 训练实际完成 |
| A4 | `repo_patch/experiments/uwm/train.py:20-31` | 2 obs/16 action/2 future切分 | 上游模型原创 |
| A5 | `scripts/uwm_libero_rollout_eval.py:35-70` | 模型接口与diffusion实例化 | 本地设计了UWM architecture |
| A6 | `repo_patch/experiments/uwm/train_robomimic.py:102-141` | pretrain strict-load与0.05×encoder lr | 远端effective config完整一致 |
| A7 | `scripts/remote_muxi_libero_remaining4_bs64_aligned_queue.sh:46-99` | epoch-aligned换算 | 完全等价官方优化轨迹 |
| A8 | `scripts/remote_muxi_libero_rollout_eval_5tasks_parallel.sh:10-17` | mixed task-specific checkpoint与strict defaults | checkpoint binary存在于本地 |
| A9 | `scripts/uwm_libero_rollout_eval.py:113-150` | reset/fixed分支、warmup、sample、success | 论文Table II同协议 |
| A10 | `scripts/uwm_libero_rollout_eval.py:169-195` | checkpoint/data prefix与episode summary | 250条raw已同步 |
| A11 | `scripts/remote_muxi_libero_rollout_eval_5tasks_parallel.sh:139-165` | 8-shard episode分配 | shard全部成功 |
| A12 | `scripts/remote_muxi_libero_rollout_eval_5tasks_parallel.sh:217-262` | completed denominator与global aggregation | expected==completed fail-closed |
| A13 | `repo_patch/datasets/robomimic/dataset.py:153-172` | optional Zarr preload | GPU吞吐提升 |
| A14 | `repo_patch/datasets/utils/loader.py:23-62` | infinite distributed sampler | 唯一root cause |
| A15 | `scripts/benchmark_libero_dataloader_stall.py:64-139` | DataLoader-only timing schema | full training parity |

### 13.2 References

1. [UWM/LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
2. [UWM/LIBERO P0 Bundle Audit](../evidence/projects/uwm_libero_p0_bundle_audit.html)。
3. [UWM Ownership Ledger](../evidence/projects/uwm_libero_ownership_ledger.html)。
4. [UWM Base Checkpoint Immutable Gate](../sources/uwm_libero90_checkpoint_immutable_manifest_gate.html)。
5. [VOL 04 Benchmark Evidence Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
6. [UWM Video/Action Source Audit](../sources/vol_04_uwm_video_action_claim_to_code.html)。
7. [UWM/LIBERO/RoboCasa Transfer Evidence Freeze](../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)。
8. [UWM RoboCasa ActionHeadFix 30-Epoch P0 Audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)。
9. [PROJ-UWM-001..004 Atomic Cards](../questions/proj_uwm.html)。
