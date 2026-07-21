# VOL 06 PER-020 Source Freeze：Robustness、Safety、Fallback 与风险门

> 状态：`source_frozen / VLA-PER-020 / primary_official_checked / robustness_safety_contract / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-21  
> 证据截止：2026-07-21  
> 本 source slice 只冻结视觉/传感器扰动、dataset shift、不确定性、风险门、fallback、recovery 与急停的公开机制；knowledge/card 已在独立下游切片同步，仍不修改 mastery、不创建 `coaching_state.md`，不把公开 benchmark、Safety Gym 或上游随机化机制写成个人项目安全结果。

## 问题（Question）

VLA 在输入腐蚀、传感器失效、分布外场景或控制风险出现时，怎样把 robustness measurement、uncertainty calibration、hard constraint、risk gate、fallback、recovery 和 E-stop 组织成可复现且 fail-closed 的协议？哪些结论只能停留在公开方法，不能升级为本地项目的安全或泛化结果？

## 1. 结论先行

1. **robustness 必须绑定 corruption family、severity、split、seed、metric 与 denominator**。ImageNet-C 的 severity 是离散等级，不同 family 的同号 severity 不是同一物理量；clean score 不能替代 shifted score。
2. **预计算 corruption 与在线随机注入不是同一协议**。官方实现为多种 corruption 提供 severity 参数表；Gaussian、shot、impulse、speckle 等会使用随机数，若在线生成必须冻结 RNG 或保存输出以保证可复现。
3. **dataset shift 下的高置信度不等于低风险**。不确定性评估需要同时看 shifted calibration、selective prediction 的 risk–coverage、false-safe 与 false-alarm，而不是只报平均 confidence 或 clean accuracy。
4. **安全不是一个模型分数**。应分层记录 observation validity、policy uncertainty、hard constraint、risk gate、recovery、fallback 与 E-stop；每层都要有输入、触发条件、动作、日志和终止语义。
5. **chunked VLA 的风险门必须处理已排队动作**。风险事件出现后应立即停止继续 apply，flush queued actions 或进入安全姿态；只在 chunk 末端检查会制造过期动作继续执行的窗口。
6. **随机化、Safety Gym、模拟器 rollout 和公开论文只支持机制级解释**。没有本地 raw trace、配置、checkpoint、逐 episode cost 与 ownership ledger，不能声称个人项目获得安全提升、真实机器人零事故或 OOD 泛化。

## 2. Primary / official source matrix

| ID | 来源 | 固定版本 / 读取证据 | 支持的 claim | 不支持的 claim |
| --- | --- | --- | --- | --- |
| P1 | Hendrycks & Dietterich，[Benchmarking Neural Network Robustness to Common Corruptions and Perturbations](https://arxiv.org/pdf/1903.12261) | arXiv `1903.12261`；PDF bytes 1,080,004；SHA-256 `c9df5483aa331dd99808350608a795c4bd9b84a7ee50396748c7d258903ea582` | ImageNet-C/P 的 corruption family、severity、mCE/relative robustness 语境 | 任意 VLA、任意机器人传感器或本地项目的鲁棒性结果 |
| P2 | Ovadia et al，[Can You Trust Your Model's Uncertainty? Evaluating Predictive Uncertainty Under Dataset Shift](https://arxiv.org/pdf/1906.02530v2) | arXiv `1906.02530v2`；PDF bytes 5,887,184；SHA-256 `1610d04d7f69d10751f0e9ff1db9fbd8b3fdf5306798879016192eb2dbf17a6f` | dataset shift 下 predictive uncertainty、calibration 与 selective risk 的评估动机 | OOD confidence 自动等于 calibrated risk，或个人系统已有安全保证 |
| O1 | [Hendrycks robustness README](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f) | commit `8190fe329f5f072a06e3a2aea02bb5dda69aed9f`；README SHA-256 `718d37a53a84615961dcdf519602cfaf1467b192bb691f8e880fbadf9e92de0d` | ImageNet-C/P 目录、预生成数据与评估入口、deterministic 运行建议 | 本地运行过 benchmark 或拥有对应数据许可 |
| O2 | [`corruptions.py`](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/imagenet_c/imagenet_c/corruptions.py) | 同一 commit；文件 SHA-256 `fb962115845e0a7ceaf5a6e3cda17f4aab07c66e3c367c219cafc7032c4a43fb` | severity 1–5 参数表、随机 corruption 与 clip/normalization 细节 | 不同 family 的 severity 可当作统一物理单位 |
| O3 | [OpenAI Safety Gym README](https://github.com/openai/safety-gym/tree/f31042f2f9ee61b9034dd6a416955972911544f5) | commit `f31042f2f9ee61b9034dd6a416955972911544f5`；README SHA-256 `2728e304d7b8483ce910d60c4880782aeb111c5fa127614b0a1d3f8bfd4653b5` | constrained RL、cost 与 safety task 的公开语境 | 使用 Safety Gym 就等于真实机器人安全或 zero violation |
| O4 | [Safety Gym `engine.py`](https://github.com/openai/safety-gym/blob/f31042f2f9ee61b9034dd6a416955972911544f5/safety_gym/envs/engine.py) | 同一 commit；文件 SHA-256 `9d52a3206648938408c05473eb48f12a78230938ea5c4b9ca878afaab087693c` | `constrain_hazards`、hazard cost、layout randomization 与 info 字段 | 没有逐 step cost/seed/布局记录时的个人安全结论 |
| L1 | [VOL 04 WM-031 reality-gap taxonomy](vol_04_wm031_reality_gap_taxonomy_source_freeze.md) | repository canonical source；SHA-256 `D25897218B4A276A0D9A981C826E8680BA21DB7E64B298963EACE10184877A97` | visual/sensor/time/geometry/dynamics/control/task/protocol 分层 | 上游 taxonomy 是本地 failure diagnosis |
| L2 | [VOL 04 WM-038 uncertainty/safety/fallback](vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.md) | repository canonical source；SHA-256 `017DBE706784AEE02ADCAA8393D34A281CAB4BEA07128DA56F3D71A65EABBB3C` | risk gate、short-prefix、queue flush、fallback/E-stop 的项目边界 | 五项目已经有完整安全闭环 |

## 3. Official implementation probes

以下 probe 只验证公开 README/源码的语义，不等于运行 ImageNet-C、Safety Gym 或任何本地机器人。

| Probe | 固定观察 | 结论 |
| --- | --- | --- |
| P20-01 | robustness README 同时列出 ImageNet-C 与 ImageNet-P | robustness 至少包含静态 corruption 与 temporal perturbation 两类协议，不能只说一个分数 |
| P20-02 | README 推荐使用预生成 JPEG corruption 数据评估 | 预生成样本优先保证 deterministic；在线随机注入必须另外记录 RNG/输出 |
| P20-03 | `corruptions.py` 为每个 corruption 提供 severity 1–5 的参数表 | severity 是 family-specific 离散索引，不是跨 family 的统一物理量 |
| P20-04 | Gaussian/shot/impulse/speckle 路径使用 NumPy random 并做归一化或 clip | 在线生成需冻结 RNG、dtype、clip 与保存策略 |
| P20-05 | brightness 与 jpeg_compression 使用各自 severity 参数表 | 两种 corruption 的 severity 不能直接相减或平均解释 |
| P20-06 | Ovadia 研究 dataset shift 下 uncertainty 的 calibration 与 risk 行为 | clean confidence 不能直接当作 shifted risk |
| P20-07 | Safety Gym 环境需要显式 `constrain_hazards=True` 才启用 hazard constraint 语义 | 没有 constraint 配置不能声称评估了 safety cost |
| P20-08 | Safety Gym `info` 暴露 `cost_hazards` 与聚合 `cost` 字段 | safety 结论必须保留逐 episode/step cost 与 denominator |
| P20-09 | `randomize_layout=False` 可复用同一布局 | 固定布局与随机布局是不同泛化协议，不能混报 |
| P20-10 | WM-038 要求风险事件后 short-prefix、queue flush、fallback/E-stop | chunked action 需要风险后的执行语义，而非仅在下一 chunk 重规划 |

Probe 状态：`10/10 deterministic source probes checked`。这些 probe 检查的是 source text，不替代硬件、仿真 runtime、传感器故障注入或独立安全审计。

## 4. Robustness protocol contract

### 4.1 Corruption 与 shift identity

最小 immutable manifest 应至少包含：

| Layer | 必填字段 | 缺失时的 fail-closed 结论 |
| --- | --- | --- |
| input | sensor/camera name、resolution、dtype、normalization、timestamp | 不知道 corruption 作用在哪个输入契约 |
| corruption | family、severity、parameter table、online/offline、RNG seed、generated artifact SHA | 不能复现或比较 shifted input |
| data | dataset revision、scene/object split、episode ID、clean/shifted pair | 不能区分 clean gain 与 shift robustness |
| policy | checkpoint SHA、pre/post-processing、action head、chunk horizon | 不能把分数绑定到具体策略 |
| metric | clean/shifted score、mCE 或 task metric、risk-coverage、denominator | 单一平均分不足以支持鲁棒性结论 |
| statistics | seed、episode-level rows、CI method、missing/invalid policy | 不能判断方差与失败样本是否被丢弃 |

对一个 corruption family `c` 与 severity `s`，可把任务分数写成：

$$
M_{c,s}(\theta)=\frac{1}{|E_{c,s}|}\sum_{e\in E_{c,s}}m\!\left(\pi_\theta,x_{e,c,s}\right).
$$

这里 `E_{c,s}` 是固定的 episode 集合，`m` 是任务指标，`x_{e,c,s}` 是由明确 corruption 协议生成的输入。若 clean 与 shifted 使用不同 episode denominator，差值就不再是纯粹的 robustness effect。

### 4.2 Calibration 与 risk–coverage

风险门不应只读取最大 softmax 或 policy confidence。一个可审计的 selective policy 需要报告 coverage `C` 与被接受样本的 risk：

$$
\operatorname{Risk}(C)=\mathbb{E}\!\left[\ell(\hat y,y)\mid \operatorname{accept}=1\right],
\qquad
C=\Pr(\operatorname{accept}=1).
$$

变量与实现映射：`accept` 由 uncertainty/risk gate 决定，`ell` 可是动作违规、goal failure、collision 或任务损失；报告必须保留拒答/转 fallback 的样本，而不是只在成功样本上平均。高置信度但高 risk 是典型 false-safe；低置信度但实际安全则可能造成 false-alarm。

## 5. Safety、fallback 与 recovery contract

建议把执行器写成有优先级的状态机：

```text
observation_valid
  -> policy_proposal
  -> uncertainty/risk_gate
       -> accept: apply bounded action prefix
       -> reject: flush queued chunk
                 -> recover: reobserve / stop / retreat / retry
                 -> fallback: safe controller or human handoff
                 -> E-stop: cut actuation and latch terminal state
```

每次转移都要写入 `event_id`、时间戳、observation/action/checkpoint SHA、gate reason、queue length、termination reason 与 operator/ownership。`fallback` 不是“模型换一个 prompt”，而是明确的控制权转移；`recovery` 也不是隐含的重试，必须定义最大次数、退避、是否重新观测和何时升级 E-stop。

对 chunked VLA，风险事件 `r_t=1` 时可用如下执行规则：

$$
\operatorname{execute}(a_t)=
\begin{cases}
a_t, & r_t=0\ \land\ \operatorname{valid}(o_t),\\
\operatorname{safe\_prefix}(o_t), & r_t=1\ \land\ \operatorname{recoverable}(o_t),\\
\operatorname{EStop}, & r_t=1\ \land\ \neg\operatorname{recoverable}(o_t).
\end{cases}
$$

公式只定义控制语义，不证明任何项目已经满足安全要求；`safe_prefix`、recoverability 与 E-stop 必须由硬件/控制器/审计证据支持。

## 6. Failure taxonomy 与诊断顺序

按 `symptom → first verified divergence → root cause → recovery/terminal outcome` 记录：

1. **visual/sensor**：遮挡、曝光、深度空洞、时间戳错位、传感器 dropout；
2. **representation/model**：OOD embedding、confidence miscalibration、action distribution collapse；
3. **geometry/time**：frame、标定、延迟、轨迹同步与单位错误；
4. **dynamics/control**：饱和、碰撞、执行器拒绝、队列过期；
5. **task/protocol**：scene/split、corruption severity、layout randomization、denominator 或 scorer mismatch；
6. **safety orchestration**：risk gate 未触发、fallback 不可用、E-stop 未 latch；
7. **unknown**：没有 raw trace 时只保留 unknown，不用 summary 或时间先后冒充根因。

最小故障注入矩阵：

| 注入 | 应观察 | 不能直接推出 |
| --- | --- | --- |
| camera corruption severity 1→5 | clean/shifted pair、family、seed、metric、risk-coverage | 不能推出真实机器人耐受性 |
| depth dropout / invalid timestamp | validity bit、last valid frame、gate reason、queue flush | 不能只从最终成功率判定 recovery |
| high-confidence wrong action | confidence、calibration bin、false-safe、fallback outcome | confidence 高不等于安全 |
| hazard proximity | constraint flag、cost_hazards、safe prefix、E-stop latch | Safety Gym cost 不等于 hardware safety |
| stale action chunk | queue length、action age、flush event、controller state | 下一 chunk 才检查会掩盖过期动作 |

## 7. 五项目真实性边界

| 项目 | 允许的局部 hook | 当前不能说 |
| --- | --- | --- |
| OpenPiVLA | image/action normalizer、parser、controller contract 与 shifted-input 评估设计 | 已完成 OOD robustness、calibration 或零事故安全结果 |
| Robot Harness | tool schema、地图/点云输入、约束与日志字段设计 | Safety Gym/真实机器人 cost、fallback 成功率或 E-stop ownership |
| OPD | grounding confidence、negative/ambiguous case 与 risk-coverage 设计 | grounding robustness uplift 或部署安全保证 |
| WAM / Cosmos | simulator diagnostics、visual shift taxonomy、失败 trace | 把上游 randomization 或公开 rollout 写成个人 sim-to-real/安全结果 |
| UWM / LIBERO | fixed-init/reset protocol、strict denominator、failure taxonomy | 真实机器人 OOD 泛化、碰撞率或安全控制器结果 |

所有项目继续采用 `public upstream mechanism → local evidence → inference → unverified` 四层标记。当前没有统一的 local raw corruption bundle、逐 step risk log、hardware E-stop audit 与候选人 ownership ledger，因此本节点只能提供面试中的机制回答与证据边界。

## 8. 退出条件与下一步

本 source slice 的退出条件：

1. 2 个 primary papers、4 个 official code/docs、2 个本地跨卷入口已固定并可追溯；
2. 10/10 source probes 通过；
3. corruption、shift、calibration、risk gate、queue flush、fallback、recovery 与 E-stop 的协议边界明确；
4. source artifact 具备 Markdown/HTML/review 三联件；
5. knowledge/card 已在独立切片同步并保持 `unseen`，不能把页面覆盖当作掌握、OOD 分数或安全完成。

下游 [VLA-PER-020 Knowledge](../knowledge/vol_06_per020_robustness_safety_fallback.html) 与 [Atomic Card](../questions/vol_06_per020.html) 已同步；题卡保持 `unseen/WARN`。下一 bounded slice 选择一题真实口述或独立 fact review，不修改 mastery，除非收到候选人的真实回答。

## 参考来源

1. Hendrycks & Dietterich，[Benchmarking Neural Network Robustness to Common Corruptions and Perturbations](https://arxiv.org/pdf/1903.12261)。
2. Ovadia et al，[Can You Trust Your Model's Uncertainty?](https://arxiv.org/pdf/1906.02530v2)。
3. Hendrycks robustness [`README.md`](https://github.com/hendrycks/robustness/tree/8190fe329f5f072a06e3a2aea02bb5dda69aed9f) 与 [`corruptions.py`](https://github.com/hendrycks/robustness/blob/8190fe329f5f072a06e3a2aea02bb5dda69aed9f/ImageNet-C/imagenet_c/imagenet_c/corruptions.py)。
4. OpenAI Safety Gym [`README.md`](https://github.com/openai/safety-gym/tree/f31042f2f9ee61b9034dd6a416955972911544f5) 与 [`engine.py`](https://github.com/openai/safety-gym/blob/f31042f2f9ee61b9034dd6a416955972911544f5/safety_gym/envs/engine.py)。
5. [VOL 04 WM-031 source freeze](vol_04_wm031_reality_gap_taxonomy_source_freeze.md) 与 [VOL 04 WM-038 source freeze](vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.md)。
6. [VOL 06 PER-003 source freeze](vol_06_per003_multiview_temporal_source_freeze.md) 与 [VOL 06 PER-015 source freeze](vol_06_per015_perception_action_reachability_uncertainty_failure_gate_source_freeze.md)。
