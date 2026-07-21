# Cosmos Policy TurnOffMicrowave 本地训练失败：P0 First-Divergence 审计

> 状态：`p0_audited / local-artifact-backed / checkpoint-remote-referenced / root-cause-partial / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 证据截止：2026-06-23  
> 范围：只审计 local negative-only 1k checkpoint 在 TurnOffMicrowave 上的 fixed-batch gate、`0/1` closed-loop、同输入 official-vs-local query probe、5-frame conditioning 对照、eval-state mining 与 corrected single-batch overfit；不把该 checkpoint 与 8-GPU 1-epoch gate、独立 full10k run 或 official-HF `84/118` 合并。

## 1. 结论先行

这批本地归档已经把失败定位到一个更窄、但仍未完全闭合的边界：**训练链路和单个负向 batch 可学习，local checkpoint 也能在缺省 debug conditioning 下采出负向夹爪；但一旦对齐 official 的 5-frame conditioning，输出在同一 HDF5 batch 和 exact eval observation 上都转为小正值。** 因此不能把失败简化成“源数据没有负样本”“第 7 维符号或 normalization 错了”“action slot 没梯度”，也不能把 `num_conditional_frames` 的缺失本身直接称为唯一 root cause。

关键证据链如下：

```text
negative-only 1k fixed batch
  sampled first gripper = -0.827738
  sampled negative fraction = 100%
  trajectory final clean first = -0.827517
              |
              | same remote-referenced checkpoint
              v
TurnOffMicrowave closed-loop
  success = 0/1, episode length = 500
  32 queries, each action chunk = 32x7
  gripper min/max/mean = +0.064589 / +0.561399 / +0.220511
  negative fraction below -0.5 = 0
              |
              | exact same initial observation hashes
              v
official-HF first gripper = -1.015586
local first gripper       = +0.142931
best-of-8 local first range = +0.105245 .. +0.221671
all eight candidates: no gripper value below -0.5
```

目前最安全的技术结论是：**first divergence 出现在 official 5-frame conditioning 下从 observation-conditioned sampler 到 7D action chunk 的映射，而不是 action tensor 的 shape、slot-5 roundtrip、stats 路径或单 batch 可学习性。** 这仍是 `partially confirmed` 的边界，不是完整因果闭环；缺少 immutable local checkpoint binary/hash、matched patch→rerun、更多 task/episode、完整 scorer/version 与候选人 ownership。

## 2. 问题（Question）

为什么 negative-only 1k checkpoint 在固定负向 batch 上能产生 `< -0.5` 的夹爪动作，到了 TurnOffMicrowave closed-loop 却是 `0/1` 且 32 次 query 全正？失败是负样本缺失、动作接口错误、采样随机性、5-frame conditioning、还是训练 observation 到 exact eval observation 的迁移问题？现有证据能确认到哪一层，面试中又应怎样避免过度归因？

## 3. P0 promotion 结论

```text
P0 status = PARTIAL
eligible local failure claims = PRESENT
eligible first-divergence claims = PRESENT
eligible root-cause claims = PARTIAL
eligible fixed claims = 0
eligible causal-uplift claims = 0
eligible ownership claims = 0
```

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| local checkpoint identity | 所有 summary 指向同一个远端 `iter_000001000` path | `REMOTE-REFERENCED` | 可绑定 run name/path；没有本地 binary/full SHA 或新进程 load parity |
| fixed-batch learnability | sampled first `-0.827738`，trajectory final clean `-0.827517` | `PRESENT` | 证明该 batch 和链路可输出负向，不证明 eval-domain transfer |
| closed-loop symptom | TurnOffMicrowave `0/1`，length `500`，32 次 query 全正 | `PRESENT / ONE-EPISODE` | 可讲最小失败复现；不是 benchmark success rate |
| same-input comparison | official first `-1.015586`，local `+0.142931`，observation/T5/proprio hashes 对齐 | `PRESENT` | 可讲 same-state first divergence；两个模型的 denoise steps 不同，结果是诊断而非公平性能排名 |
| sampling variance | local best-of-8 first gripper `0.105245–0.221671`，无 `<-0.5` | `PRESENT` | 排除该 state 上“单次倒霉 seed”；不能概括全部 states |
| source negative support | 52 个 HDF5、11230 states；top-24 GT first-action negative rate `37.5%` | `PRESENT` | 排除“相似成功数据完全没有负向 first action” |
| 5-frame conditioning effect | 缺省 debug path 为全负；补齐 official 5 frames 后为全正 | `PRESENT / COUNTERFACTUAL` | 证明 conditioning contract 会改变输出；不能单独证明模型为何没有学会该条件分布 |
| corrected overfit transfer | ordinary loss 能拟合 fixed batch，但 exact eval first 仍 `+0.315938` | `PRESENT` | 证明 parameter/update/action path 可学；暴露 observation-conditioned transfer gap |
| repaired final result | 没有 patch 后的 matched multi-episode success rerun | `MISSING` | 不得称 root cause fixed 或成功率恢复 |
| ownership | run/operator/code author/reviewer 未由候选人逐项确认 | `PENDING` | 路径、日志和 Git author 不自动等于个人贡献 |

## 4. Frozen inputs 与 SHA-256

| 本地证据 | SHA-256 | 本页用途 |
| --- | --- | --- |
| `negative_only_gate_iter1000_summary.json` | `87E46164CA21BC302298505E08CF8D15492CBAA16BD75FD30126D7B4B31E9039` | 训练配置、fixed-batch gate、trajectory final clean 与 run exits |
| `eval_action_debug_summary.json` | `7BA5101928FDF089404E033A9C915BEFD678D1D140338A726AE6D1E27531F1C0` | `0/1` closed-loop、500 steps、32 次 query 的 gripper 统计 |
| `query_probe_comparison_summary.json` | `C73FF213B6F584BEF73975BA07E621E26BEEDB294F7C5BF656E80207268C280E` | 同一 initial observation 的 official-vs-local first action |
| `best_of_8_query_probe_summary.json` | `1EA9C2A74B569DDD6811D6DAD41A27C438D17DDEB5FC27E2DDBBF71A5B0EAC49` | 8 个 denoising seeds 的 local query 分布 |
| `eval_state_mining_summary.json` | `0A989EB0A59947156A42A6853785D826F277D0EF52F08F8E92FD3CDCAAB65726` | 52-file/11230-state mining、top-24 标签与早期 overfit 摘要 |
| `eval_vs_hdf5_query_compare.json` | `3548EB7ECECFB5689091E596CCA164A5A3268405009D104D7FB0E06D23A6B52D` | HDF5 nearest state、conditioning-frame counterfactual、exact queries |
| ordinary-loss overfit summary | `E8F10210D1542F5B52BF6CFB527F97F93946967268A3CA3BDBCE628B676EEE9D` | corrected fixed-batch learnability 与 exact-eval non-transfer |
| negative-only strong-reg overfit summary | `2FF4545E75B83BAA83BC39AFDECCE64106FD01842EF485396B627D4E6E85C407` | strong auxiliary 的 clean/sample/exact-eval 三层对照 |

上表冻结的是 Windows 本地归档文件。checkpoint 本身仍只由远端 path 引用：

```text
/data/msz/wm/outputs/cosmos_policy_predict2_official_repro_20260621/
imaginaire_runs/cosmos_policy_repro/predict2_robocasa_official_t5/
train1k_full1199_sampler_gripper_aux_w20_sig200_first8_negonly_neg64/
checkpoints/iter_000001000
```

本页没有把该 path 当作 immutable checkpoint hash，也没有独立复算远端权重内容。

## 5. Run 总账与相邻 Delta

| Run / probe | 相较上一阶段的改造 | 数据/输入 | Checkpoint / steps | 输出产物 | 结果 | 能证明 / 不能证明 |
| --- | --- | --- | --- | --- | --- | --- |
| `negonly_1k_gate` | full1199、action-only、balanced sampler、first8 negative-only aux | fixed negative/positive batch，`32×7` action | local `iter_000001000`，train 1000，sample 35 steps | gate/chain/trajectory JSON | sampled first `-0.8277`，gate pass | 能输出负向；不能证明 closed-loop |
| `turnoff_1ep_smoke` | 从 fixed batch 进入 RoboCasa online rollout | TurnOffMicrowave initial state，5-frame official contract | 同一 local path | eval log、JSONL、2 视频、summary | `0/1`，length 500，32 queries 全正 | closed-loop 症状；单 episode 不是 benchmark |
| `exact_query_official` | 截断到 initial observation 单次 query | 相同 camera/proprio/T5 hashes | official HF，5 denoise steps | comparison JSON | first gripper `-1.0156` | official 能在该 state 输出负向；不是本地训练对照成绩 |
| `exact_query_local` | checkpoint 替换为 local，denoise 35 steps | 同上 | local 1k | comparison JSON | first gripper `+0.1429` | first divergence；不同 denoise steps 不支持性能排名 |
| `best_of_8_local` | seeds 195–202 | 同一 exact eval state | local 1k | summary JSON | first `0.1052–0.2217`；global min `-0.0372` | 排除单 seed；不排除其他 state 能负向 |
| `eval_state_mining` | 从 52 HDF5 搜索 eval-like success states | 11230 states，top-24 | 无新训练 | neighbors/mining JSON | top-24 first negative `37.5%`；nearest GT first `-1` | 相似数据存在负向；不是 exact observation 等价 |
| `conditioning_counterfactual` | 只补 `num_conditional_frames=5` | 同一 nearest HDF5 batch | local 1k | compare JSON | 缺省为全负；5 frames 后全正 | conditioning contract 是高影响变量；不是唯一 root cause |
| `corrected_overfit_none` | official 5-frame eval-like contract，ordinary loss 单 batch 1000 steps | nearest negative + positive samples | in-memory overfit | summary/JSONL | fixed clean `-1.0154`、sampled `-1.0259`；exact eval `+0.3159` | 单 batch可学但不迁移 exact observation |
| `corrected_overfit_negonly` | 加 sampler negative-only strong-reg | 同上 | in-memory overfit 1000 steps | summary/JSONL | clean `-0.9001`、fixed sample `+0.5002`、exact eval `+0.3279` | aux 有梯度但未修复 sampler/eval transfer |

以上 run 只构成诊断序列，不是递增性能曲线。相邻阶段的 Δ 主要落在 observation contract、sampler seed 与 in-memory objective；checkpoint、task set、denoise steps、episode denominator 并非全部 matched，因此禁止把数值差写成 uplift。

## 6. 动作、采样与评测合同

每次 policy query 产生一个动作块 \(A_q\in\mathbb{R}^{H\times D}\)，当前归档中 \(H=32\)、\(D=7\)，第 7 维是 gripper。令 \(g_{q,h}=A_q[h,6]\)，本页使用的负向比例为：

\[
r^-_q=\frac{1}{H}\sum_{h=0}^{H-1}\mathbf{1}[g_{q,h}<-0.5].
\]

变量解释：\(q\) 是 policy query，\(h\) 是 chunk 内 action index，阈值 `-0.5` 来自这些本地 gate/summary 的判定合同。实现映射：`eval_action_debug_summary.json` 对 32 个 query 分别统计 chunk 维度和 gripper 分布；closed-loop 中所有 \(r^-_q=0\)。这是本地证据阈值，不应扩写成 RoboCasa 官方统一成功条件。

同一 initial observation 的 first-action gripper 差异可写为：

\[
\Delta_g=g^{\mathrm{local}}_{0,0}-g^{\mathrm{official}}_{0,0}
=0.142931-(-1.015586)=1.158517.
\]

变量解释：两侧共享 task label、三路 camera、raw/normalized proprio、T5 embedding 与 constructed data batch 的短 SHA；official 使用 5-step action denoise，local 使用 35-step。直觉上这是第一个可观测 action divergence，不是训练提升或同超参模型质量差。实现映射：数字来自 `query_probe_comparison_summary.json`，因此只支持该 state、该 seed 和各自记录的 sampler 配置。

conditioning 对照把 sampler 写成：

\[
\hat A=f_\theta(o, c, z; C),\qquad C\in\{1,5\},
\]

其中 \(o\) 是图像与 proprio observation，\(c\) 是 T5 task condition，\(z\) 是 denoising noise，\(C\) 是 conditional-frame count。缺省 debug path（实质为 \(C=1\)）在 nearest HDF5 batch 上 first gripper 为 `-0.961349`、全 chunk 负向率 `1.0`；对齐 official \(C=5\) 后 first gripper 为 `+0.129789`、负向率 `0.0`。实现映射：两项来自 `eval_vs_hdf5_query_compare.json` 的 `hybrid_sampling`；它证明 \(C\) 改变了模型条件分布，却没有证明“把 \(C\) 改回 1”能修复 official closed-loop。

## 7. Online Rollout 与 First-Divergence 定位

```python
def audit_turnoffmicrowave_rollout(env, policy, checkpoint, task):
    # 1. Reset one TurnOffMicrowave episode and retain exact initial observation hashes.
    obs = env.reset(task=task, seed=195)

    # 2. Build the official Predict2 contract: three cameras, proprio, T5 and 5 conditional frames.
    model_batch = build_predict2_batch(obs, task, num_conditional_frames=5)

    # 3. Query a 32x7 action chunk and record the seventh gripper dimension before execution.
    action_chunk = policy.sample(model_batch, checkpoint=checkpoint, denoise_steps=35)
    record_query(action_chunk, shape=(32, 7), gripper_index=6)

    # 4. Execute only the configured open-loop prefix, then replan until success or horizon 500.
    for action in action_chunk[:16]:
        obs, _, done, info = env.step(action)
        if done or info.get("success", False):
            return info

    # 5. Repeat queries and preserve JSONL/video/episode length for first-divergence analysis.
    return continue_until_horizon(env, policy, max_steps=500)
```

这段伪代码重建归档中的 control flow，不声称函数名逐字存在于项目。直接证据是 `num_open_loop_steps=16`、chunk `32×7`、5-frame slot contract、seed 195、500-step episode 与 action-debug JSONL；环境 success predicate 的具体源码 revision 仍未冻结。

### 7.1 Closed-loop 症状

`eval_action_debug_summary.json` 记录：1 个有效 episode、success `0/1`、length `500`、32 次 action query。把全部 query 的第 7 维汇总后，最小值 `+0.064589`、最大值 `+0.561399`、query mean 的均值 `+0.220511`，所有 query 的 `<-0.5` 比例都是 `0`。first-row gripper 甚至只落在 `+0.131084..+0.145603`。

这说明“第一个动作恰好为正”不足以解释失败：在整个 episode 的记录 query 中，没有一次进入本地 gate 定义的负向区间。但它仍然只有 1 episode；不能把 `0/1` 写成任务族 success rate。

### 7.2 Same-input official-vs-local probe

comparison summary 冻结了 primary/secondary/wrist image、raw proprio、constructed video batch、T5 embedding 与 normalized proprio 的短 SHA。官方 checkpoint 在同一 initial observation 上 first gripper 为 `-1.015586`；local 1k 为 `+0.142931`。local 的 best-of-8 seeds 195–202 全部为正，first range `+0.105245..+0.221671`，所有 chunk 元素的最小值也只有 `-0.037203`。

因此，在这个 state 上可以排除“local 只是碰到一个倒霉 denoising seed”以及“只有 best-of-N value selection 选错候选”。不能排除的是：其他 states、其他 checkpoint step、不同训练 distribution 或 matched denoise setting 下可能出现不同结果。

## 8. 负样本、5-frame 与 Exact-Observation Transfer

### 8.1 不是简单的“没有负样本”

state mining 扫描 52 个 HDF5、11230 个 states。按图像/proprio 相似度选出的 top-24 中，GT first gripper `<-0.5` 的比例为 `37.5%`；最近邻 first gripper 是 `-1.0`，其 chunk 同时包含负/正动作。这证明 eval-like success data 中存在关闭夹爪方向的监督信号。

同时，full1199 stats 中 gripper action 的 min/max 是 `-1/+1`，full1199 与 subset8 stats 的最大绝对差为 `0.0`。因此“源 gripper 第 7 维只有正值”与“eval 误用了另一套 subset stats”都被现有 structured summaries 反驳。

### 8.2 历史 debug sampler 漏了关键 conditioning 字段

早期 fixed-batch/debug path 没有显式传入 `num_conditional_frames`。在 nearest HDF5 batch 上，它可以得到全负 chunk；一旦设置为 official contract 的 5 frames，同一 checkpoint 的 chunk 变为全正。这不是无关紧要的参数变化，而是改变 observation information flow 的输入合同差异。

但安全结论不是“5 frames 是 bug”。official checkpoint 在相同 5-frame eval contract 上能输出 `-1.0156`；真正的问题更接近 local model 没有把训练监督迁移到 official 5-frame conditioned exact observation。要确认根因，仍需 matched training/eval：训练期显式固定相同 \(C=5\)，保存 immutable checkpoint，再对同一 state 与多 episode 做 patch 前后 rerun。

### 8.3 Corrected overfit 揭示 transfer gap

在对齐 5-frame 的 eval-like overfit 中，ordinary action loss 训练 1000 steps 后：

| 层级 | ordinary loss | negative-only strong-reg | 解释 |
| --- | ---: | ---: | --- |
| fixed-batch clean first | `-1.015420` | `-0.900114` | 两种目标都能把 clean prediction 拉负 |
| fixed-batch sampled first | `-1.025936` | `+0.500155` | ordinary loss 在该 seed/batch 可过 sampler；strong-reg 反而未过 |
| exact eval first | `+0.315938` | `+0.327874` | 两者都没有迁移到 exact eval observation |
| exact eval negative frac | `0` | `0` | 没有形成 `<-0.5` action |

ordinary loss 的 final base loss 是 `0.267922`；strong-reg 的 base/aux/total 是 `1.138504 / 0.039185 / 1.922204`，第 7 维 target gradient L2 为 `7.924779`。这说明 auxiliary 不是“写了但没有梯度”，却也没有保证 full sampler 或 exact observation 的正确条件映射。

本页不画跨 run loss curve：这些 summary 只有少量 step snapshots，且目标函数不同，把它们连接成平滑曲线会制造可比性。可复核的做法是保留 step-level JSONL，并把上述终点作为诊断表，而不是伪造训练趋势。

## 9. 0-Success 假设审计

| 假设 | 支持/反驳证据 | 当前动作 | 再评估结果 | 状态 |
| --- | --- | --- | --- | --- |
| 源数据没有负向 gripper | 52 HDF5/11230 states；top-24 first negative `37.5%`；stats min `-1` | mining + stats 对照 | 找到 eval-like negative windows | `REJECTED` |
| 第 7 维 action shape/order 已断 | action chunk 始终 `32×7`；gripper index 6；slot-5 roundtrip error `1.19e-7` | chain trace | fixed batch 可输出 `-0.8277` | `REJECTED FOR BASIC PATH` |
| normalization/stats path 错配 | full1199 vs subset8 stats max diff `0.0`；dataset/manual normalize error `5.96e-8` | stats/roundtrip audit | basic mismatch 未发现 | `REJECTED FOR ARCHIVED CASE` |
| 单个 denoising seed 倒霉 | best-of-8 全部 first 为正，无 `<-0.5` | seeds 195–202 | 仍全正 | `REJECTED FOR THIS STATE` |
| debug sampler 与 official eval 输入合同不同 | 缺省 conditional frames 时全负；5 frames 后全正 | 补齐 `num_conditional_frames=5` | counterfactual 稳定复现 | `CONFIRMED CONTRACT DIFFERENCE` |
| 训练链路/参数完全不可学 | ordinary overfit clean/sample 达 `-1.015/-1.026` | corrected 1000-step single-batch overfit | fixed batch 学会 | `REJECTED` |
| exact eval observation 没有被模型正确条件化 | fixed batch 学会，但 exact eval 仍 `+0.316`；official 同 state 为 `-1.016` | same-input + overfit | gap 仍存在 | `PARTIALLY CONFIRMED` |
| negative-only strong-reg 已修复 | clean 为负但 fixed sample `+0.500`、exact eval `+0.328` | 1000-step corrected overfit | 未修复 | `REJECTED` |
| gripper 是 `0/1` 的唯一原因 | 当前只有 action/debug 与单 episode；未冻结完整 state/video causal trace | 需要 patch→rerun | 尚无成功恢复 | `OPEN` |

这里的“rejected”都带作用域：例如 basic action path 通过，不代表 controller axis semantics、environment success predicate 或所有 episode 都已核验。

## 10. 面试可用口径

### 30 秒版本

> 我把 local 1k checkpoint 的 fixed-batch gate 和 closed-loop 结果分开。它在负向 fixed batch 上确实能采出 first gripper `-0.8277`，但 TurnOffMicrowave 1-episode eval 是 `0/1`，500 steps 的 32 次 query 第 7 维全为正。对同一个 initial observation，official-HF first gripper 是 `-1.0156`，local 是 `+0.1429`，best-of-8 local 也没有 `<-0.5`。进一步发现早期 debug sampler 没带 official 的 5-frame conditioning：补齐后同一 HDF5 batch 会从全负转成全正。corrected overfit 说明单 batch 和参数链路可学，但 exact eval observation 仍不迁移，所以我把结论定为 observation-conditioned sampler transfer gap，尚不称唯一 root cause 或已修复。

### 2 分钟版本

> 我先固定身份：这是 full1199 上 negative-only auxiliary 的 local 1k checkpoint，不是 8-GPU 1-epoch gate、独立 full10k，也不是 official-HF `84/118`。固定 batch 的动作 shape 是 `32×7`，slot-5 roundtrip 和 normalization 都通过，35-step sampler first gripper 能到 `-0.8277`，所以基础链路不是完全学不会。真正进入 TurnOffMicrowave closed-loop 后，1 episode 跑满 500 steps 仍是 `0/1`；32 次 query 的 gripper min 都在正区间，整体最小值是 `+0.0646`。
>
> 为了找 first divergence，我截取同一个 initial observation，对齐三路图像、proprio、T5 和 batch hash。official-HF 输出 `-1.0156`，local 输出 `+0.1429`；local 换 8 个 seed，first 仍在 `0.1052–0.2217`。数据侧也不是完全没负样本：52 个 HDF5、11230 states 的 top-24 eval-like neighbors 中有 `37.5%` GT first action 为负。
>
> 最关键的 protocol bug 是历史 debug sampler 缺 `num_conditional_frames`；缺省时同一 HDF5 batch 可全负，按 official 的 5 frames 后转成全正。但我不把它直接叫唯一根因，因为 official 模型在 5-frame contract 下工作正常，而且 corrected single-batch overfit 虽然能把 fixed clean/sample 拉到约 `-1.02`，exact eval first 仍是 `+0.316`。所以已确认的是 conditioning contract 差异和 exact-observation transfer gap；未确认的是哪种训练数据/条件建模改动能恢复 multi-episode success。

### 高压追问：所以是因为训练集负样本太少吗？

**强回答：**

> 不能这样归因。数据不平衡可能是背景风险，但现有证据已经找到 eval-like negative windows：top-24 first-action negative rate 是 `37.5%`，nearest GT first 是 `-1`；ordinary single-batch overfit 也能把 fixed sampled first 拉到 `-1.026`。失败发生在 5-frame conditioned exact eval observation 上，所以“没有负样本”不足以解释。下一步应做 matched (C=5) 训练、immutable checkpoint、同 state probe 和多 episode rerun，而不是只加负样本权重。

### 高压追问：你定位并修复了 root cause 吗？

**强回答：**

> 我定位了两个可复核边界：历史 debug sampler 与 official eval 的 5-frame contract 不一致；local checkpoint 从 fixed batch 到 exact eval observation 存在 first-action gripper divergence。还没有修复后的 matched success rerun，所以我不会说 root cause 已修复。negative-only strong-reg 的 corrected overfit 也失败了，这反而说明单纯加强夹爪 auxiliary 不是充分解。

## 11. 公源、本地证据与 Ownership 边界

| 层级 | 本页如何使用 | 不能越界到 |
| --- | --- | --- |
| 公有上游 | Cosmos Policy Predict2/RoboCasa 的 5-frame、action chunk 与 official checkpoint path | 个人提出模型架构、个人训练 official 权重 |
| 本地证据 | JSON summaries、logs、JSONL、视频、mining/overfit outputs | checkpoint binary 已 hash、本地结果可严格复现 |
| 本地推断 | first divergence 位于 5-frame observation-conditioned sampler transfer | 唯一 root cause、gripper 必然导致所有 success failure |
| 未核实 | operator、code author、reviewer、checkpoint lineage、scorer revision、controller semantics | 个人主导、修复已上线、benchmark uplift |

候选人可以认领哪些具体脚本、运行、分析和结论，仍需 ownership ledger 的人工确认；本页不从 Windows 用户名、远端路径或文件作者自动推断。

## 12. 关闭 P0 的最小动作

1. 把 local `iter_000001000` checkpoint、config、stats、T5 与代码 revision 形成 immutable manifest，并在新进程做 load/query parity。
2. 用同一 training/eval contract 显式固定 `num_conditional_frames=5`；保留 patch、训练日志和 step-level sampler diagnostics。
3. 对 patch 前后 checkpoint 跑 matched exact-state query：同 task、初始 state、三路图像/proprio/T5 hash、denoise steps、seed set 和 output transform。
4. 把 TurnOffMicrowave 从 1 episode 扩到预注册 seeds/episodes，冻结 success predicate、controller、horizon、JSONL 与视频，并报告 denominator。
5. 对 first divergence 做逐层 trace：condition tensor、slot mask、action latent、denoising trajectory、denormalized 7D action 与 controller input；不要只看 final gripper histogram。
6. 由候选人逐文件确认 run operator、脚本/patch author、分析者和 reviewer；工具生成与人工判断分开记录。

在这些字段闭合前，本页保持 `PARTIAL/WARN`。允许讲“我复现了一个可审计的 0/1 failure，并把 first divergence 收窄到 official 5-frame conditioned exact-observation transfer”；不允许讲“我修好了 Cosmos Policy 的 gripper root cause”、训练提升或本地 checkpoint benchmark 成绩。

## References

1. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\negative_only_aux_gate_20260622\train1k_full1199_sampler_gripper_aux_w20_sig200_first8_negonly_neg64\negative_only_gate_iter1000_summary.json`。
2. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\negative_only_aux_gate_20260622\eval_1k_TurnOffMicrowave_1ep_cudaenv\eval_action_debug_summary.json`。
3. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\query_probe_20260622\query_probe_comparison_summary.json`。
4. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\query_probe_20260622\best_of_8_query_probe_summary.json`。
5. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\eval_state_mining_20260622\eval_state_mining_summary.json`。
6. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\eval_state_compare_20260622\eval_vs_hdf5_query_compare.json`。
7. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\eval_state_mining_20260622\eval_like_overfit_none_steps1000_w0_sig200\single_batch_overfit_none_summary.json`。
8. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\eval_state_mining_20260622\eval_like_overfit_sampler_negonly_strong_reg_steps1000_w20_sig200\single_batch_overfit_sampler_negonly_strong_reg_summary.json`。
9. [Cosmos Policy RoboCasa Official-HF Baseline P0 Audit](cosmos_policy_robocasa_baseline_p0_audit.html)。
10. [Cosmos / WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
11. [Cosmos / WAM 口述 Model Answer](../../practice/wam_oral_model_answer.html)。
