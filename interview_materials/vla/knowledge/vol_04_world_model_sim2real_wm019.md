# VOL 04 World Model / Sim2Real：Metric Boundary（WM-019）

> 状态：`drafted / knowledge_21_of_44 / card_deferred / WARN`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-WM-019`；本轮只生成 knowledge node，不生成题卡，不创建 coaching state。  
> 前置：[WM-018 Prediction Horizon](vol_04_world_model_sim2real_wm018.html)、[WM-019 Metric Source Freeze](../sources/vol_04_wm019_metric_boundary_source_freeze.html)、[Benchmark Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。

## 问题（Question）

PSNR/SSIM/FVD、latent loss、action MSE 与 downstream success 各能证明什么？回答必须说明统计单位、prediction target、teacher-forcing/open-loop、protocol 与不可外推边界。

## 证据边界与学习位置

```text
WM-018 horizon / open-loop compounding
                 ↓
WM-019 metric ladder and protocol boundary
                 ↓
WM-020 posterior collapse / action ignoring / shortcut
                 ↓
VOL 05 statistical evaluation and deployment evidence
```

本页基于 world-model foundation、UWM、benchmark/evidence 和 EVAL-003 source audits；不把用户项目页的百分比、MSE 或 proxy score升级为统一 metric contract。[1][2][3][4]

## 1. Metric ladder

| 层级 | 典型指标 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| offline target fit | action MSE、latent MSE/L1、reward/value loss | 固定 split/target/reduction 的拟合 | causal action、rollout stability、success |
| teacher-forced one-step | PSNR/SSIM、one-step latent/video error | 给定真实历史时的局部预测 | 自回归长期误差、控制可用性 |
| open-loop rollout | per-offset error、latent drift、FVD/视频 proxy | 使用自身预测时的稳定性线索 | simulator/real contact 与 task success |
| world-model proxy | WorldGym/VLM scorer、generated-video task score | proxy 环境下的方向性筛选 | simulator predicate、real robot success |
| simulator closed loop | LIBERO/RoboCasa episode success | 固定 env/controller/reset/predicate 的结果 | real hardware transfer、某个 head 的独立因果贡献 |
| real closed loop | hardware success、failure trace | 指定 robot/controller/protocol 的最终结果 | 其他 embodiment 泛化与内部机制解释 |

证据只能逐级建立关联，不能从下一级平均分直接跳到上一级结论。

## 2. PSNR、SSIM 与 FVD

### 2.1 PSNR

PSNR 基于像素均方误差，常见定义是：

\[
\operatorname{PSNR}=10\log_{10}\frac{MAX_I^2}{\operatorname{MSE}(I,\hat I)}.
\]

(MAX_I) 是像素取值上界，(I,hat I) 是真值与预测图像。它能反映像素重建误差，但可能偏好平均/模糊预测；背景和光照变化也会主导分数。

### 2.2 SSIM

SSIM 比较局部亮度、对比度和结构；它比纯像素 MSE 更关注局部结构，却仍不理解机器人动作语义、接触、可抓取性和任务 success predicate。

### 2.3 FVD 类视频指标

FVD/视频感知指标依赖 feature extractor、clip length、sample count、预处理和实现。它能描述视频分布或感知质量的差异，但“看起来真实”不等于 action-conditioned consequence 正确；应配 action perturbation 和物理/任务 probe。

## 3. Latent loss 与 action MSE

latent/video loss 受 VAE/feature scale、prediction target、noise level、normalizer、mask 和 reduction 影响。不同 latent space 的绝对数值通常不能直接排序。

action MSE 则依赖 action unit、absolute/delta/velocity、axis、gripper、horizon、padding 与 normalizer。低 action MSE 可能仍对应错误 controller mapping、错误 replan 或 distribution shift。

UWM validation 记录 marginal/inverse/joint action MSE 与 marginal/forward/joint image MSE；它们是各 conditional slice 的 proxy，不能互相替代，也不能替代 LIBERO rollout success。[2]

## 4. Teacher-forced 与 open-loop

teacher-forced one-step 使用真实上一帧/latent 作为输入；open-loop 在第一步后使用模型自己的预测。两者的误差路径不同：

\[
e_{t+k}\lesssim L^k e_t+\sum_{j=0}^{k-1}L^j\delta_{t+k-1-j}.
\]

(e) 是状态/latent 误差，(L) 表示动力学的误差放大系数，(delta) 是每步模型误差。这是分析框架，不是某论文的 exact bound；它解释为何 one-step MSE 很低仍可能在长 rollout 中漂移。实现映射是按 future offset 报告 error，而不是只报全 horizon 平均值。

## 5. World proxy、simulator 与 real success

WorldGym 等方法在 generated video/world model 上使用 VLM/reward proxy，可以筛选策略、发现 failure mode；其 scorer、rollout length、初始图和 retry contract 与 LIBERO/RoboCasa `check_success` 不同。simulator closed-loop 又与真实机器人 camera、dynamics、latency、controller 和安全停止不同。[3]

正确说法是：proxy 与下游 success 需要 matched checkpoint/task/init 的 paired validation、rank correlation 和 failure analysis；不能把 proxy score、sim success、real success 放进一个平均值。

## 6. 可比性合同

比较两个指标前至少冻结：

- model/checkpoint、processor/normalizer revision；
- data split、target schema、metric script、mask/reduction/valid count；
- camera/preprocess、task/suite、initial state、warmup；
- horizon、chunk/replan、controller、seed/determinism；
- episode/trial denominator、invalid episode rule、success predicate；
- proxy scorer/version 或 simulator/environment version。

若 protocol 不同，差值同时包含 model effect 与 protocol effect；相同任务名、相同分母仍不足以建立可比性。

## 7. 最小评估伪代码

```python
def evaluate_metric_ladder(model, batch, env, protocol):
    # 1. Compute target-specific offline metrics with valid masks and fixed reduction.
    offline = compute_offline_metrics(model, batch, protocol.metric_spec)

    # 2. Compare teacher-forced and open-loop errors by future offset.
    rollout = compute_per_offset_rollout(model, batch, protocol.horizon)

    # 3. Test whether predicted future changes under controlled action perturbations.
    sensitivity = action_perturbation_test(model, batch)

    # 4. Run closed-loop episodes under a frozen reset/controller/success contract.
    success = run_episode_manifest(model, env, protocol)
    return offline, rollout, sensitivity, success
```

关键是同一 checkpoint 的多层指标共同保存，而不是用一列 MSE 代替完整 evidence chain。

## 8. 统计单位与项目边界

rollout success 的基本单位通常是预先定义的 episode，需记录 task/init/seed/controller/predicate 和 (k/n)。action step、video frame、OPD raw row、box/point/text scorer 不能自动当作独立 Bernoulli episode。[4]

- UWM 的 action/image MSE、reset-style、fixed-pruned-init 与 LIBERO result 必须分开命名。
- WAM held-out MSE、World/value proxy、planning uplift、0-success 与官方 baseline 需要 checkpoint、prediction/label、episode trace、scorer 和 denominator。
- OpenPiVLA 97.4% 与 OPD 10k raw-holdout 必须先定义 metric-specific denominator，不能直接套 rollout success CI。

## 9. 结论与后续

WM-019 的核心是 metric ladder：视觉指标说明视觉相似，latent/action loss说明特定 target 的拟合，open-loop指标说明自回归稳定性线索，proxy/simulator/real success分别绑定不同环境与统计合同。只有协议冻结并做 paired validation，才能讨论相关性或下游收益。

本节点为 `WARN`：公开 metric/protocol 边界已冻结，本地 per-offset、action sensitivity、proxy-vs-simulator paired test、checkpoint/denominator artifacts 仍 pending。本轮不生成 WM-019 题卡；下一步可单独生成一张保持 `unseen` 的题卡。

## 参考文献（References）

1. [World Model Foundations Audit](../sources/vol_04_world_model_foundations_claim_to_code.html)。
2. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。
3. [Benchmark / Evidence Audit E](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
4. [EVAL-003 statistical source freeze](../sources/vol_05_eval003_success_rate_confidence_interval_source_freeze.html)。
5. [WM-019 Metric Source Freeze](../sources/vol_04_wm019_metric_boundary_source_freeze.html)。
