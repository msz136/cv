# VOL 06 PER-020：Robustness、Safety、Fallback 与风险门

> 状态：`knowledge_drafted / VLA-PER-020 / source_frozen / project_truth_bounded / card_synced / WARN`  
> 更新日期：2026-07-21  
> 权威来源：[PER-020 Robustness / Safety Source Freeze](../sources/vol_06_per020_robustness_safety_fallback_source_freeze.html)  
> 学习边界：本页把 corruption protocol、dataset shift uncertainty、risk–coverage、hard constraint、风险门、chunk queue flush、fallback、recovery 与 E-stop 转成可面试、可审计的知识；题卡已在独立切片同步并保持 `unseen`，不修改 276 张题卡的 mastery，不创建 `coaching_state.md`。

## 问题（Question）

VLA 面对视觉腐蚀、传感器 dropout、OOD 场景或执行风险时，怎样区分 robustness score、uncertainty calibration、hard constraint、risk gate、fallback、recovery 与 E-stop？如何让每个结论都能回到 corruption family、severity、split、seed、denominator、checkpoint 和 raw trace，而不是把高 confidence 或模拟器 cost 误写成安全保证？

## 1. 学习出口

完成本页后，面试中应能做到：

1. 解释为什么 robustness 不是一个裸分数，而是 corruption family、severity、split、seed、metric、denominator 的协议元组。
2. 区分预生成 corruption 与在线随机注入，说明 severity 表、RNG、dtype、clip 与 artifact SHA 对复现的影响。
3. 说明 clean accuracy、OOD confidence、calibration、risk–coverage、false-safe 和 false-alarm 的边界。
4. 设计从 observation validity 到 policy proposal、risk gate、bounded prefix、queue flush、recovery、fallback、E-stop 的执行状态机。
5. 写出 chunked VLA 风险事件后的 fail-closed 伪代码，并说明 stale action 为什么必须被丢弃。
6. 用 visual/sensor、representation/model、geometry/time、dynamics/control、protocol 和 safety orchestration 组织 failure diagnosis。
7. 对 OpenPiVLA、Robot Harness、OPD、WAM/Cosmos、UWM/LIBERO 给出不越界的项目回答。
8. 明确哪些只是公开机制、哪些是本地证据、哪些是推断、哪些仍未核实。

## 2. 一分钟心智模型

```text
fixed task / split / clean-shift pair
              ↓
corruption family + severity + seed + generated artifact
              ↓
policy output + uncertainty + validity bits
              ↓
risk gate: accept / reject
              ↓
bounded action prefix or flush queued chunk
              ↓
recover → fallback → E-stop (latched terminal state)
              ↓
episode trace + cost/risk/coverage + failure taxonomy
```

主线只有一句话：**先冻结输入与评估协议，再判断模型是否知道自己不确定，最后把不确定性连接到有日志、有终止语义的控制动作。** `randomize`、`confidence`、`cost` 或 `safety` 这些字段名本身，都不能替代这三层证据。

## 3. Robustness：先冻结 shifted input，再谈分数

### 3.1 Corruption family 与 severity

Hendrycks & Dietterich 的 ImageNet-C/P 语境把常见扰动按 family 组织，并为每个 family 设定离散 severity。它的启发不是“所有 corruption 都能统一排序”，而是要求比较时写清楚：

| 字段 | 面试中的含义 | 缺失时的结论 |
| --- | --- | --- |
| family | Gaussian noise、shot noise、brightness、JPEG 等具体扰动 | 不知道变了哪一种输入因素 |
| severity | family-specific 的 1–5 参数档位 | 不能把不同 family 的同号 severity 当作同一物理量 |
| source mode | 预生成样本或在线随机生成 | 不能判断 deterministic 与 RNG 语义 |
| seed/RNG | NumPy 或其他随机数状态 | 不能重现随机 corruption |
| clean/shifted pair | 同一任务样本的 clean 与 shifted 对照 | 不能把模型差异归因于 shift |
| denominator | 有效 episode、图像或样本集合 | 平均分可能改变 estimand |

官方 `corruptions.py` 为 family 提供 severity 参数表；Gaussian、shot、impulse、speckle 等路径使用随机数，并涉及归一化与 clip。因此在线注入必须记录 RNG、dtype、clip 和输出 artifact；预生成 JPEG corruption 更适合做可重复的评估输入，但不等于真实传感器噪声。

### 3.2 一个可审计的 shifted metric

对 corruption family \(c\)、severity \(s\)，令 \(\mathcal E_{c,s}\) 为固定的有效 episode 集合，\(x_{e,c,s}\) 为按协议生成的输入，\(m\) 为任务 metric，则：

$$
M_{c,s}(\theta)
=
\frac{1}{|\mathcal E_{c,s}|}
\sum_{e\in\mathcal E_{c,s}}
m\!\left(\pi_\theta,x_{e,c,s}\right).
$$

变量解释：\(\theta\) 是固定 checkpoint，\(c,s\) 指定 corruption family 与 severity，\(m\) 可以是任务 success、动作误差或 collision-related metric。直觉是“先固定被评估的样本集合，再计算 shift 下的策略分数”；实现上对应 clean/shifted pair、episode ID、checkpoint SHA 和 denominator manifest。若 clean 与 shifted 使用不同 episode 集合，\(M_{c,s}-M_{\mathrm{clean}}\) 就不再是纯粹的 robustness effect。

### 3.3 汇总分数不能隐藏 family

当需要汇总多个 family 时，可以报告 normalized degradation 或 mean corruption error，但必须保留 family-level rows。平均值适合做导航指标，不适合隐藏某一类传感器故障。面试回答应同时给 clean metric、每个 family/severity 的 shifted metric、worst-case 或分位数、失败样本与 denominator、seed/CI 或 episode-level variability。

## 4. Dataset shift 下的 uncertainty 与 calibration

### 4.1 Confidence 不是 risk

Ovadia et al. 研究的是 dataset shift 下 predictive uncertainty 的行为。迁移到 VLA 时，关键问题不是“模型有没有一个 confidence 字段”，而是 confidence 是否随 shift 仍有排序能力、接受的动作是否真的比拒答更安全、高 confidence 错误是否形成 false-safe、低 confidence 但实际安全是否造成 false-alarm，以及 calibration 是否在 shifted split 上重新测量。

因此 clean accuracy 或平均 confidence 都不能单独证明 OOD safety。至少要同时报告 shifted calibration、selective prediction 的 risk–coverage 和拒答样本的处理结果。

### 4.2 Risk–coverage

令 `accept=1` 表示风险门允许执行，\(C\) 为 coverage，\(\ell\) 为动作或任务损失，则：

$$
\operatorname{Risk}(C)
=
\mathbb E\!\left[
\ell(\hat y,y)
\mid \operatorname{accept}=1
\right],
\qquad
C=\Pr(\operatorname{accept}=1).
$$

变量解释：\(\hat y\) 可以是动作、目标 grounding 或任务结果，\(y\) 是对应真值，\(\ell\) 可以是动作违规、collision、goal failure 或任务损失。直觉是 coverage 越低，系统只执行更有把握的样本；实现上必须保留被拒答的样本、转交 fallback 的原因和最终 outcome，不能只对成功执行的样本求平均。

### 4.3 Uncertainty 的三层输入

| 层 | 可观测量 | 不能直接推出 |
| --- | --- | --- |
| observation validity | missing frame、depth invalid、timestamp age、camera mask | 模型已经知道语义风险 |
| policy uncertainty | ensemble/variance、distribution entropy、calibrated score | confidence 高就一定安全 |
| outcome risk | collision、goal failure、constraint cost、fallback outcome | 一次成功就证明 calibration |

## 5. Safety：把风险连接到执行状态机

### 5.1 从 proposal 到 E-stop

一个 fail-closed 执行器至少应区分以下状态：

```text
observation_valid
  -> policy_proposal
  -> uncertainty/risk_gate
       -> accept: apply bounded action prefix
       -> reject: stop applying queued chunk
                 -> recover: reobserve / stop / retreat / retry
                 -> fallback: safe controller or human handoff
                 -> E-stop: cut actuation and latch terminal state
```

每次状态转移必须记录 `event_id`、时间戳、observation/action/checkpoint SHA、gate reason、queue length、termination reason 与 operator/ownership。`fallback` 是控制权转移，不是换一个 prompt；`recovery` 是有次数上限、重新观测和升级条件的状态，不是隐含 retry。

### 5.2 Hard constraint 与风险门

Safety Gym 的公开语境把 hazard constraint 与 cost 放在环境接口中，并要求显式配置约束开关；`info` 中的 `cost_hazards` 与聚合 `cost` 只能说明该模拟器记录了什么，不能直接说明真实机器人安全。

面试中可把风险门抽象为：

$$
g(o_t,\hat a_t,u_t)
=
\mathbf 1[
\operatorname{valid}(o_t)
\land
\operatorname{risk}(u_t)\le \tau
\land
\operatorname{constraint}(\hat a_t)=1
].
$$

变量解释：\(o_t\) 是观测，\(\hat a_t\) 是策略提议，\(u_t\) 是不确定性或风险估计，\(\tau\) 是门限。直觉是“只有输入有效、风险不超过阈值、动作满足硬约束才允许 apply”；实现上要绑定 validity bit、risk estimator、constraint checker、gate reason 和日志。这个公式是教学抽象，不能被写成五个项目已经拥有的安全控制器。

### 5.3 Chunked VLA 的 stale action

VLA 往往一次产生动作 chunk，再执行前 \(K\) 个动作。若在第 \(t\) 步出现风险事件 \(r_t=1\)，继续执行原 chunk 会把已经过期的决策施加到新状态。最低安全语义是先停止 apply，再 flush queue：

$$
\operatorname{execute}(a_t)=
\begin{cases}
a_t, & r_t=0\land \operatorname{valid}(o_t),\\
\operatorname{safe\_prefix}(o_t), & r_t=1\land \operatorname{recoverable}(o_t),\\
\operatorname{EStop}, & r_t=1\land \neg\operatorname{recoverable}(o_t).
\end{cases}
$$

变量解释：\(r_t\) 是风险事件，`safe_prefix` 是经过控制器和约束检查的短动作前缀，`recoverable` 是明确的状态判定。直觉是“风险发生后，旧队列不再拥有默认执行权”；实现上必须记录 action age、queue length、flush event、controller state 和 E-stop latch。公式只定义执行合同，不证明任意项目满足硬件安全。

## 6. Robustness、Safety 与 Recovery 的最小 manifest

| Layer | 必填字段 | 失败时的回答 |
| --- | --- | --- |
| input | camera/sensor name、resolution、dtype、normalization、timestamp | 不知道扰动作用在哪个输入 |
| corruption | family、severity、parameter table、online/offline、RNG、artifact SHA | 不能复现 shifted input |
| data | dataset revision、scene/object split、episode ID、clean/shifted pair | 不能比较 clean 与 shift |
| policy | checkpoint SHA、pre/post-process、action head、chunk horizon | 分数无法绑定模型 |
| risk | uncertainty estimator、threshold、calibration split、accept/reject rule | 不能解释 gate |
| safety | hard constraint、controller、safe prefix、fallback、E-stop latch | 不能把 cost 当 safety |
| metric | clean/shifted score、risk–coverage、cost、denominator | 平均分不是完整结论 |
| statistics | seed、episode rows、CI、missing/invalid policy | 不能判断方差或丢样本 |
| ownership | code/config/data/scorer author、operator、reviewer、artifact custodian | upstream 不是个人贡献 |

推荐 immutable lineage：

```text
task/split manifest SHA + corruption/config SHA
    -> generated clean/shifted artifact + RNG state
    -> policy checkpoint + risk/calibration revision
    -> action proposal + gate/queue/flush trace
    -> per-episode metric + cost + failure label
    -> aggregate report + ownership ledger
```

这条链的目的不是增加字段，而是让一个风险结论能回到输入、模型、门控、执行、结果和责任边界。

## 7. Fail-Closed 伪代码

```python
def safe_chunk_step(manifest, obs, action_chunk, risk_estimator, controller):
    # 1. Reject invalid observations before trusting model uncertainty.
    if not obs.valid or obs.timestamp_age > manifest.max_observation_age:
        flush_queue(reason="invalid_observation")
        return fallback_or_estop("observation_invalid")

    # 2. Evaluate risk and hard constraints on the current state.
    risk = risk_estimator.score(obs, action_chunk)
    if risk > manifest.risk_threshold:
        flush_queue(reason="risk_gate")
        if controller.recoverable(obs, risk):
            return controller.safe_prefix(obs)
        return estop_latched("unrecoverable_risk")

    # 3. Apply only a bounded prefix; never assume a stale chunk is valid forever.
    prefix = action_chunk[:manifest.replan_steps]
    if not controller.constraint_ok(obs, prefix):
        flush_queue(reason="constraint_violation")
        return fallback_or_estop("hard_constraint")

    # 4. Record lineage and execute; the next observation can trigger a new gate.
    log_event(manifest, obs, prefix, risk, queue_length=len(action_chunk))
    return controller.apply(prefix)
```

这段伪代码是风险门的教学目标，不是五个本地项目已有的统一安全 runtime。真实实现还要处理并发 action broker、controller acknowledgement、sensor watchdog、hardware E-stop、human handoff、retry budget、atomic logs 和 replay。

## 8. Failure Taxonomy：从 symptom 到 first divergence

诊断顺序固定为：

```text
input validity
  -> corruption/shift identity
  -> representation/model calibration
  -> geometry/time synchronization
  -> dynamics/control execution
  -> risk orchestration
  -> unknown
```

| 类别 | 典型症状 | 首查 artifact | 不能直接推出 |
| --- | --- | --- | --- |
| visual/sensor | 遮挡、曝光、深度空洞、dropout、timestamp stale | validity bit、sensor trace、clean/shifted pair | 模型语义理解退化 |
| representation/model | OOD embedding、confidence miscalibration、action collapse | calibration bin、risk–coverage、checkpoint | 一定是传感器问题 |
| geometry/time | frame、标定、延迟、单位、轨迹同步错误 | frame IDs、timestamps、transform log | policy 已经失效 |
| dynamics/control | saturation、collision、controller reject、stale chunk | controller status、action age、queue trace | risk estimator 错 |
| task/protocol | split、severity、layout randomization、denominator mismatch | manifest、config、episode set | 模型鲁棒性差 |
| safety orchestration | gate 未触发、fallback 不可用、E-stop 未 latch | event log、state transition、hardware audit | 仅靠最终 success 能解释 |
| unknown | 只有 summary、视频或时间顺序 | 请求 raw trace；保留 `unknown` | 用最接近的故事替代证据 |

最小故障注入矩阵：

| 注入 | 应观察 | 面试结论 |
| --- | --- | --- |
| camera severity 1→5 | clean/shifted pair、family、seed、risk–coverage | 只能谈视觉 shift 协议 |
| depth dropout / invalid timestamp | last valid frame、gate reason、queue flush | 不能只看最终成功率 |
| high-confidence wrong action | calibration bin、false-safe、fallback outcome | 高 confidence 不等于安全 |
| hazard proximity | constraint flag、cost_hazards、safe prefix、E-stop latch | Safety Gym cost 不等于硬件安全 |
| stale action chunk | queue length、action age、flush event、controller state | 需要风险后的执行语义 |

完整根因表必须写成 `symptom → first verified divergence → root cause → recovery/terminal outcome`。没有 first divergence，最多只能报告 symptom 或 unknown。

## 9. 方法比较：面试一张表讲清楚

| 对象 | 主要作用 | 最小可审计证据 | 常见误写 |
| --- | --- | --- | --- |
| corruption benchmark | 测量输入 shift 下的性能变化 | family、severity、pair、seed、denominator | 一个平均分代表所有鲁棒性 |
| calibration | 检查不确定性与真实风险的关系 | shifted bins、reliability/risk curve、拒答结果 | confidence 就是 calibrated risk |
| hard constraint | 禁止不可接受动作或状态 | constraint checker、单位、controller response | reward/cost 自动等于约束 |
| risk gate | 决定 accept/reject/transfer | threshold、gate reason、policy version | 阈值没有 protocol |
| fallback | 转移控制权到安全 controller/人 | entry/exit、max retry、owner、trace | 换 prompt 就是 fallback |
| recovery | 重新观测、短动作、重试或退避 | budget、backoff、state reset、outcome | retry 不需要上限 |
| E-stop | 切断执行并锁存终止状态 | hardware event、latch、operator、reset policy | simulator stop 就是 physical E-stop |

## 10. 五项目真实性边界

| 项目 | 可以安全连接的局部 hook | 当前不能说 | 若要升级需要 |
| --- | --- | --- | --- |
| OpenPiVLA | image/action normalizer、parser、controller contract、shifted-input eval design | 已有 OOD robustness、calibration、zero-accident safety | clean/shifted bundle、risk log、checkpoint、matched eval、ownership |
| Robot Harness | tool schema、地图/点云输入、约束与日志字段设计 | Safety Gym/真实机器人 cost、fallback 成功率或 E-stop ownership | local risk/fallback runtime、逐 step trace、hardware audit |
| OPD | grounding confidence、negative/ambiguous case、risk–coverage 设计 | grounding robustness uplift 或部署安全保证 | shifted holdout、calibration report、failure trace、owner |
| WAM / Cosmos | simulator diagnostics、visual shift taxonomy、失败 trace | 上游 randomization 或公开 rollout 是个人 sim-to-real/安全结果 | fixed artifact、paired shift eval、controller/safety bundle |
| UWM / LIBERO | fixed-init/reset protocol、strict denominator、failure taxonomy | 真实机器人 OOD 泛化、碰撞率或安全 controller 结果 | matched episode rows、risk/cost trace、hardware or simulator gate |

回答顺序是：`public mechanism → fixed source → local evidence → inference → unverified → missing artifact → ownership`。当前结论是“有可迁移的协议与接口 hook”，不是“已有个人安全结果”。

## 11. 两档面试回答

### 11.1 约 30 秒回答

我会先冻结 robustness protocol：corruption family、severity、clean/shifted pair、split、seed、checkpoint 和 denominator 都要固定。预生成 corruption 与在线随机注入不能混为一谈，severity 也不是跨 family 的统一物理量。然后在 shifted split 上检查 calibration 和 risk–coverage，不能只看 confidence。执行时把 observation validity、risk gate、hard constraint、chunk queue flush、recovery、fallback 和 E-stop 分层；风险事件出现后先停止旧 chunk，只有明确 recoverable 才执行 safe prefix。我的五个项目目前没有完整 local corruption bundle、逐 step risk log 或硬件 E-stop audit，所以我会讲机制和补证据路径，不把 Safety Gym 或上游 randomization 说成个人安全结果。

### 11.2 约 2 分钟机制回答

我会把问题拆成 measurement、uncertainty 和 execution 三层。Measurement 层先固定 task、split、episode IDs、输入传感器、corruption family/severity、RNG、checkpoint 和 denominator；clean 与 shifted 必须是可配对、可复现的输入，不能只报一个平均分。ImageNet-C 的 severity 是 family-specific 参数档位，Gaussian 等 corruption 的在线生成还涉及随机数、归一化和 clip。Uncertainty 层不把最大 softmax 当安全证据，而是在 shift 下看 calibration、risk–coverage、false-safe 和 false-alarm，保留被拒答和转 fallback 的样本。Execution 层把风险门接到控制权：观测无效或风险超阈值时 flush 排队 chunk；如果能恢复，就重新观测或执行受约束的短前缀；不能恢复则转 safe controller、人接管或锁存 E-stop。每次转移都记录 gate reason、action age、queue length、controller response 和 outcome。对我的项目，我可以把 normalizer/parser/controller contract、tool schema、grounding confidence 或 fixed-init denominator 作为局部 hook，但当前没有统一 shifted-input bundle、逐步 risk trace 和 hardware audit，因此不会声称已经完成 OOD 泛化或真实安全闭环。

## 12. 高频追问与答题抓手

| 追问 | 回答抓手 |
| --- | --- |
| severity=5 一定比另一个 family 的 severity=3 更严重吗？ | 不一定；severity 是 family-specific 参数索引，不能当统一物理单位。 |
| 预生成 JPEG 与在线 Gaussian noise 能直接比较吗？ | 不能直接比较；source mode、RNG、dtype、clip 和 sensor semantics 不同。 |
| confidence 高但动作错，说明什么？ | 可能是 shifted miscalibration，需查 risk–coverage、false-safe 和 calibration bin。 |
| risk gate 触发后能继续执行旧 chunk 吗？ | 默认不能；先停止 apply、flush queue，再决定 recovery/fallback/E-stop。 |
| Safety Gym 的 cost=0 是否代表真实安全？ | 不代表；它只是在固定 simulator/config 下的 cost 记录。 |
| randomize_layout=False 与 True 是同一泛化评估吗？ | 不是，布局分布不同，必须分别报告。 |
| fallback 和 retry 有什么区别？ | fallback 是控制权转移，retry 是有预算和状态条件的 recovery。 |
| 没有 raw trace 能确认 collision 根因吗？ | 不能；只保留 symptom/unknown，先找 first verified divergence。 |
| 你的项目做过 robustness/safety 吗？ | 当前只有接口、协议或诊断 hook，没有可复算 shifted bundle、逐 step risk log 或硬件 E-stop ownership。 |

## 13. 本页证据边界与下一步

本页已把 PER-020 source freeze 转成可学习知识：corruption identity、severity/RNG、clean-shift metric、dataset-shift calibration、risk–coverage、risk gate、hard constraint、queue flush、fallback/recovery/E-stop、typed manifest、fail-closed 伪代码、故障注入思路、五项目 truth boundary、两档口述回答与追问抓手均已覆盖。

直接支持来自 [PER-020 Source Freeze](../sources/vol_06_per020_robustness_safety_fallback_source_freeze.html)、Hendrycks & Dietterich、Ovadia et al.、Hendrycks robustness README/`corruptions.py`、OpenAI Safety Gym README/`engine.py`、VOL 04 WM-031 与 WM-038。风险门和 chunk 执行公式是教学抽象；它们不证明任何本地项目已经有安全 controller 或 E-stop 审计。

当前仍为 `WARN`：没有五个项目的 local-direct shifted-input bundle、逐 step risk log、hardware E-stop audit、matched robustness panel 或 ownership confirmation；没有真实口述，所以不创建 coaching state、不改变 mastery。下游 [VLA-PER-020 Atomic Card](../questions/vol_06_per020.html) 已同步并保持 `unseen/WARN`；下一 bounded slice 选择一题真实口述或独立 fact review。

## References

1. Hendrycks & Dietterich，[Benchmarking Neural Network Robustness to Common Corruptions and Perturbations](https://arxiv.org/pdf/1903.12261)，arXiv `1903.12261`。
2. Ovadia et al.，[Can You Trust Your Model's Uncertainty?](https://arxiv.org/pdf/1906.02530v2)，arXiv `1906.02530v2`。
3. Hendrycks robustness [`README.md`](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f) 与 [`corruptions.py`](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/imagenet_c/imagenet_c/corruptions.py)。
4. OpenAI Safety Gym [`README.md`](https://github.com/openai/safety-gym/tree/f31042f2f9ee61b9034dd6a416955972911544f5) 与 [`engine.py`](https://github.com/openai/safety-gym/blob/f31042f2f9ee61b9034dd6a416955972911544f5/safety_gym/envs/engine.py)。
5. [VOL 04 WM-031 reality-gap taxonomy](../sources/vol_04_wm031_reality_gap_taxonomy_source_freeze.html) 与 [VOL 04 WM-038 uncertainty/safety/fallback](../sources/vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。
6. [VOL 06 PER-003 multiview/temporal source freeze](../sources/vol_06_per003_multiview_temporal_source_freeze.html) 与 [VOL 06 PER-015 perception-action gate source freeze](../sources/vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.html)。
