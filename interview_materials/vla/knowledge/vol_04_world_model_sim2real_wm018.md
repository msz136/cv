# VOL 04 World Model / Sim2Real：Prediction Horizon 与 Replan（WM-018）

> 状态：`drafted / knowledge_20_of_44 / card_deferred / WARN`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-WM-018`；本轮只生成 knowledge node，不生成题卡，不创建 coaching state。  
> 前置：[WM-017 Heterogeneous Embodiment Schema](vol_04_world_model_sim2real_wm017.html)、[WM-018 Horizon Source Freeze](../sources/vol_04_wm018_prediction_horizon_source_freeze.html)、[Diffusion Policy Audit](../sources/vol_03_diffusion_policy_claim_to_code.html)。

## 问题（Question）

prediction horizon 过短或过长如何影响可控性、细节与训练稳定性？回答时必须拆开 observation/history、prediction、execution、replan 和 imagination 五条时间轴；同一个数字不能自动代表同一种 horizon。

## 证据边界与学习位置

```text
WM-017 schema / timestamp / valid mask
                 ↓
WM-018 prediction / execution / replan horizon
                 ↓
WM-019 metric boundary
                 ↓
WM-020 posterior collapse / action ignoring / shortcut
```

本页只把公开 paper/repo 的时间合同写成可审计知识，不把公开配置写成本地最优：

- Diffusion Policy 明确区分 (T_o,T_p,T_a)，实现中对应 observation steps、`horizon` 与 `n_action_steps`。[1]
- ACT 的 `chunk_size/num_queries=H` 是 prediction horizon；是否每 (H) 步 query 取决于 temporal aggregation。[2]
- Cosmos/WAM 的 LIBERO/RoboCasa chunk 与 execution prefix 不同；UWM 的 `action_len`、history/future frames 是 frozen config。[3][4]
- one-step 或 component loss 不能证明长 horizon rollout 和 closed-loop success；本地 horizon A/B 仍待证据。[4][5]

## 1. 五条时间轴

| 时间轴 | 符号 | 它回答的问题 | 不能直接等同 |
| --- | --- | --- | --- |
| observation/history | (T_o) | 读取多少历史 observation | 全部 episode history |
| prediction | (T_p) / (H) | 一次预测多少未来 action/state slots | 执行步数 |
| execution prefix | (T_a) / (K) | 一次 query 后实际执行多少步 | prediction horizon |
| replan interval | (R) | 多久重读 observation 并推理 | model `horizon` |
| imagination/planning | (H_{imag}) | latent/world model 向前 rollout 多远 | future video frame 数 |

控制频率还要显式换算物理时间：

\[
\Delta t_{pred}=T_p/f_{ctrl},\qquad
\Delta t_{exec}=T_a/f_{ctrl},\qquad
\Delta t_{replan}=R/f_{ctrl}.
\]

变量解释：(f_{ctrl}) 是 control frequency。同样的 16 steps，在 5 Hz 与 50 Hz 下分别是 3.2 秒和 0.32 秒；因此跨项目比较必须记录频率、action repeat、timestamp 与 latency。

## 2. horizon 过短与过长

### 2.1 较短 prediction horizon

优点是 target 更近、padding 少、显存/计算小、误差更易控制；缺点是难以表达持续接触、延迟 reward、暂停/连续动作等 sequence structure，可能迫使 policy 频繁重规划。

### 2.2 较长 prediction horizon

优点是能覆盖更长的 temporal structure，为 planner/value 提供更远候选；风险是模型自回归误差、OOD latent、末端动作模糊、padding 比例、训练显存与 step time 增大。若 execution prefix 也变长，新的 observation 更久才被吸收，stale action 和 recovery 风险上升。

### 2.3 imagination horizon

world model 中更长的 imagination 能看到更远 return，但 model bias 也会累积；模型可能在 imagined state 上高估 value。典型防护是缩短 open-loop execution、增加真实 observation 校正、ensemble/disagreement、uncertainty penalty 和 receding-horizon planning。[4]

## 3. 代码与方法对照

### 3.1 Diffusion Policy：(T_o/T_p/T_a) 解耦

frozen repo 的 `horizon` 是 action prediction trajectory 的长度，`n_action_steps` 决定输出/执行多少步；simulation wrapper 和 real CLI 的 `steps_per_inference` 决定 replan interval。论文讨论 warm-start，但 frozen 主要 policy path 从 random noise 重启，不能把论文选项写成 commit 默认行为。[1]

### 3.2 ACT：chunk horizon 与 temporal aggregation

ACT 一次输出 (H\times D_a) 的 chunk。不开 temporal aggregation 时可每 (H) 步 query 并执行缓存段；开启后每个 control step query，并对覆盖同一时刻的多个 chunk 预测做聚合。因此 prediction horizon 可以长，而 replan interval 仍为 1。[2]

### 3.3 Cosmos/WAM 与 UWM

Cosmos/WAM frozen docs 的 LIBERO 默认 16×7 chunk、执行 16 步；RoboCasa 默认预测 32×7、执行前 16 步。UWM 默认 `action_len=16`，同时由 `num_frames`/`obs_num_frames` 定义 history/future frame contract。它们都说明 chunk、future prediction、execution 和 replan 必须分开记录。[3][4]

## 4. Horizon 对训练目标的影响

改变 (T_p) 不只是改变输出 shape，还会改变有效 target 数、padding 比例、sequence difficulty、显存和每 step wall-clock。若 loss 仍按全张量平均，长 horizon 可能稀释关键 early-step error；若按 valid mask 聚合，又必须记录有效元素分母。比较 horizon 时至少记录：

- per-offset action/video error；
- valid target count 与 terminal padding ratio；
- memory、step time、inference latency；
- action sensitivity 与 open-loop rollout error；
- closed-loop success、failure offset 和 recovery time。

不能只用最终平均 MSE 判断 horizon 好坏。

## 5. 最小实验矩阵

| 变量 | 建议对照 | 固定项 | 输出 |
| --- | --- | --- | --- |
| prediction (T_p) | 4/8/16/32 或任务网格 | checkpoint/data/steps/normalizer | per-offset error、memory、step time |
| execution (T_a) | 1/4/8/16 | controller Hz、同一 checkpoint | success、action age、recovery |
| replan (R) | 1/4/8/16 | queue、通信、controller | p50/p95 latency、stale failures |
| imagination (H_{imag}) | short/medium/long | world/value checkpoint、planner budget | imagined-vs-real return、calibration |
| terminal padding | mask on/off | same batch/seed | loss、gradient、per-offset error |

所有 sweep 都要冻结 reset/init、task split、seed、camera、normalizer、checkpoint SHA、success predicate 和 trial denominator。否则 horizon 的变化与 protocol 变化混在一起。

## 6. 最小伪代码

```python
def rollout_with_horizons(policy, env, cfg):
    # 1. Prediction horizon and execution prefix are separate contracts.
    pred = policy.predict(obs, horizon=cfg.prediction_horizon)

    # 2. Execute only a prefix, then absorb a fresh observation.
    prefix = pred[:cfg.execution_prefix]
    for action in prefix:
        obs, reward, done, info = env.step(action)
        if done:
            return info

    # 3. Replan interval is controlled by the outer loop, not model horizon alone.
    return rollout_with_horizons(policy, env, cfg)
```

代码只展示时间轴分离；真实实现还需处理 queue、timestamp、controller timeout、terminal mask、normalizer 和 maximum episode steps。

## 7. 失败诊断与项目边界

| 症状 | 优先检查 | 不应直接结论 |
| --- | --- | --- |
| chunk 后半段漂移 | per-offset error、action age、control Hz、replan | horizon 必然过长 |
| one-step 好、long rollout 差 | model rollout、OOD、uncertainty、reset | world model 没有用 |
| 频繁 replan 抖动 | latency、queue、action smoothing、controller | 短 horizon 必然更好 |
| imagined value 高、真实 success 低 | imagined-vs-real calibration、model bias | planner 一定失败 |

UWM/LIBERO 可讲 `action_len`、history/future、normalizer、reset 和 rollout protocol 的核对；WAM 可讲 LIBERO/RoboCasa chunk/execution 差异；OpenPiVLA 的本地 horizon/replan 必须回到 config、checkpoint、inference loop 和 eval summary。ACT/Diffusion Policy 的公开 recipe 不能替代个人项目事实。

## 8. 结论与后续

WM-018 的核心是：prediction horizon 决定模型看多远，execution prefix 决定执行多久，replan interval 决定多久吸收新 observation，imagination horizon 决定 world/value 看多远。过短损失长期结构，过长放大 compounding、latency 和 stale action；最终判断必须基于 matched horizon sweep、分 offset 误差、物理时间、closed-loop success 和 failure trace。

本节点为 `WARN`：公开 horizon 合同与代码边界已冻结，本地 A/B、closed-loop trace 和个人项目 lineage 尚未完成。本轮不生成 WM-018 题卡；下一步可单独生成一张保持 `unseen` 的题卡。

## 参考文献（References）

1. [Diffusion Policy Audit](../sources/vol_03_diffusion_policy_claim_to_code.html)。
2. [ACT Audit](../sources/vol_03_act_claim_to_code.html)。
3. [Cosmos/WAM Audit C](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)。
4. [World Model Foundations Audit](../sources/vol_04_world_model_foundations_claim_to_code.html)。
5. [UWM Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。
6. [WM-018 Horizon Source Freeze](../sources/vol_04_wm018_prediction_horizon_source_freeze.html)。
