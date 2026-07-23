# VOL 04 Source Audit C：Cosmos Policy / WAM Claim-to-Code

> 审计日期：2026-07-16  
> 状态：drafted / paper_v1_full_text_reviewed / repo_frozen_and_line_audited / hf_model_revisions_frozen / independent_fact_reviewed / WARN  
> 覆盖题目：VLA-WM-008..009、VLA-WM-022..030、VLA-WM-040..044  
> frozen repo：NVlabs/cosmos-policy @ 18a2accadf4e7a3531e56754102af5a24d2316da（commit date 2026-01-22）

## 1. 结论先行

1. **Cosmos Policy 不是在视频 backbone 后外挂 action/world/value 三个 head。**论文和 frozen code 都把当前 proprio、action chunk、未来 proprio、future images 与 value 编排进同一 video latent sequence；低维量通过 latent injection 覆写 placeholder frame，训练与采样继续复用 Cosmos-Predict2 的 diffusion transformer。[1][2]
2. **“同一模型有三种角色”由 conditioning 与 loss routing 决定。**base training 的示范/rollout sample 约按 50% policy、25% world model、25% value function 分流；policy、world、value 分别对不同 latent prefix 条件化并预测不同 target slot，而不是仅靠三个 loss 名称。[1][2]
3. **direct policy 与 planning 是两个不同推理合同。**direct eval 一次并行生成 action/future/value，但只执行 action；planning 先采样 action，再条件生成 future state，再评分 value，best-of-N 选择最高分候选。[1][2]
4. **可用 planning 需要 rollout distribution 与独立 planning checkpoint。**论文明确 base demonstration-only model 的 world/value 对失败分布覆盖不足；其 ALOHA planning 实验使用 rollout 数据细化 world/value，并 dual-deploy 原 policy checkpoint 与 refined planning checkpoint。[1]
5. **latent injection 不是“语义 token”。**action \(K\times D_a\) 被 flatten/repeat 到 \(16\times 28\times 28\) latent volume；解码时把可整除的完整 action copies reshape 后求均值。value 则把整个 value frame 求均值，再从 \([-1,1]\) 映射到 \([0,1]\)。[1][2]
6. **LIBERO 与 RoboCasa 的执行合同不同。**LIBERO 是 16×7 action chunk 并默认全 16 步 open-loop；RoboCasa 是 32×7 chunk、默认执行前 16 步，再在环境侧拼接 5 维 inactive mobile-base action 形成 12D controller action。[2][3][4][5]
7. **官方 direct-policy 分数不能写成本地 WAM 结果。**论文/模型卡报告 LIBERO 98.5% 和 RoboCasa 67.1%，它们绑定官方 checkpoint、task set、50 trials、三 seeds 与指定 runtime；任何本地 45%、71.19%、0-success 或 offline MSE 必须由本地 artifact 单独证明。[1][6][7]
8. **论文、代码与权重许可证不同。**arXiv v1 是 CC BY 4.0，frozen GitHub tree 是 Apache-2.0，而两个 HF policy model card 声明 NVIDIA One-Way Noncommercial License；不能用 repo license 推断 checkpoint 可商用。[1][2][6][7]
9. **当前审计与后续独立复核均未运行 GPU inference 或新 rollout。**已核对 paper→repo→model card→eval path，并在独立复核中下载固定 config/statistics、重哈希本地 diagnostic；checkpoint tensor、完整 dataset revision、runtime reproduction 与候选人 ownership 仍未闭合，review 必须保持 WARN。[8]

## 2. 来源与证据边界

| 编号 | 来源 | 冻结版本 | 可支持 | 不能支持 |
| --- | --- | --- | --- | --- |
| [1] | Kim et al., Cosmos Policy paper | arXiv 2601.16163v1，提交 2026-01-22；CC BY 4.0 | latent injection、三类概率合同、50/25/25 routing、rollout refinement、best-of-N、论文 protocol/metric | 用户本地 checkpoint、日志、0-success、个人贡献 |
| [2] | NVlabs/cosmos-policy | commit 18a2accadf4e7a3531e56754102af5a24d2316da；Apache-2.0 | dataset slot、mask、loss、sampler、get_action、planning、eval wrapper 的 frozen code 行为 | 命令未执行；main/commit 与任一缓存权重不自动兼容 |
| [3] | 同 commit 的 README / LIBERO.md | 同上 | 官方 quickstart、model ID、16-step chunk、5-step denoise、500 trials/suite、训练命令 | README command 不证明本机复现 |
| [4] | 同 commit 的 ROBOCASA.md | 同上 | 24 tasks、50 demos/task、32-step chunk、16-step execution、50 trials/task、seeds | 文档默认值不等于用户项目 protocol |
| [5] | Frozen LIBERO/RoboCasa eval source | 同上 | reset/warmup/init/camera/controller/action queue/success predicate | 尚未与外部 benchmark commit 做独立复核 |
| [6] | nvidia/Cosmos-Policy-LIBERO-Predict2-2B model card/API | revision cb689ec0e3347c13667d70a78a3447388f5c3bb8 | model I/O、official checkpoint files、98.5% protocol、NSCLv1 | 未下载 checkpoint；card 的数字仍是上游声明 |
| [7] | nvidia/Cosmos-Policy-RoboCasa-Predict2-2B model card/API | revision 4b2a04c80d97202f86127ebec80461e8016ec1dc | model I/O、official checkpoint files、67.1% protocol、NSCLv1 | 未下载 checkpoint；不能证明某个本地 cache revision |
| 同源推断 | [1]–[7] 联合分析 | evidence cutoff 2026-07-16 | claim-to-code、shape、mask、protocol 与风险边界 | 不替代 runtime experiment、独立事实审查和视觉 QA |

基础权重 `nvidia/Cosmos-Predict2-2B-Video2World` 的 HF API revision 冻结为 `f50c09f5d8ab133a90cac3f4886a6471e9ba3f18`。训练 config 的 `load_path` 指向其中 `model-480p-16fps.pt`，但本轮没有下载该权重或验证文件 hash。[2]

## 3. 概率合同：policy、world model 与 value

令 \(s_t=(o_t,p_t,c)\) 表示当前多视角 observation \(o_t\)、proprio \(p_t\) 与任务文本 \(c\)，\(a_{t:t+K-1}\in\mathbb R^{K\times D_a}\) 是 action chunk，\(s'\approx s_{t+K}\) 是未来 observation proxy，\(G_{t+K}\) 是 Monte Carlo return。论文把三种训练角色写成：[1]

\[
\begin{aligned}
\text{policy: }&p_\theta(a,s',G\mid s),\\
\text{world: }&p_\theta(s',G\mid s,a),\\
\text{value: }&p_\theta(G\mid s,a,s').
\end{aligned}
\]

变量解释：这里的 \(s'\) 实际只包含 \(t+K\) 时刻的 proprio 与 camera observations，并非可直接访问的完整 simulator state；\(G\) 是终局稀疏奖励按 \(\gamma^{H-t}\) 折扣后的 empirical return。实现映射：同一 latent sequence 保持固定布局，`num_conditional_frames`、input mask 与 sample mask 改变哪部分是 clean condition、哪部分参与 denoising target。[1][2]

这三条合同不能合并成“一个 joint loss 自动学会 planning”。base policy 可以并行生成三个 output，但只有在 world/value 对候选 action 的 OOD future 可靠且 value 已校准时，才可用于 action selection。论文自己也把 demonstration-only direct policy 与 rollout-refined planning model 分开。[1]

## 4. Latent sequence 与注入/提取

### 4.1 Frozen layouts

| Suite | latent sequence（去掉 tokenizer 内部 spatial token） | state_t | action / proprio |
| --- | --- | --- | --- |
| LIBERO | blank, current proprio, wrist, primary, action, future proprio, future wrist, future primary, value | 9 | action 16×7；proprio 9D |
| RoboCasa | blank, current proprio, wrist, left primary, right primary, action, future proprio, future wrist, future left, future right, value | 11 | action 32×7；proprio 9D |

每个语义 frame 对应 \(C'\times H'\times W'=16\times28\times28\) latent volume。Wan2.1 tokenizer 的 temporal compression factor 是 4，所以 config 以一张首 blank 加每个 semantic frame 的四张重复 image 组织 33-frame LIBERO input 或 41-frame RoboCasa input。[1][2]

### 4.2 Action latent injection

令归一化 action chunk 为 \(A\in[-1,1]^{K\times D_a}\)，latent volume 元素数为 \(M=C'H'W'\)，action 元素数为 \(L=KD_a\)。frozen code 的注入可写为：

\[
z_a=\operatorname{reshape}\left(
\operatorname{repeat}(\operatorname{vec}(A),\lceil M/L\rceil)_{1:M}
\right)\in\mathbb R^{C'\times H'\times W'}.
\]

变量解释：`replace_latent_with_action_chunk` 先 flatten (A)，按 ceiling repeat 填满 latent，再覆写 action latent index。它没有 action-specific learned encoder；学习发生在共享 diffusion transformer 中。[2]

提取时，`extract_action_chunk_from_latent_sequence` 只取可组成完整 action copies 的前 \(qL\) 个元素，其中 \(q=\lfloor M/L\rfloor\)，reshape 成 \(q\times K\times D_a\) 后平均：

\[
\hat A=\frac{1}{q}\sum_{j=1}^{q}\operatorname{reshape}(z_a^{(j)},K,D_a).
\]

实现含义：注入时可能存在最后一个不完整重复片段，提取时它被丢弃；这应在极端 \((K,D_a)\) 组合与换机器人时单测。输出随后按 dataset `actions_min/actions_max` 反归一化，不能跳过 checkpoint 对应的 statistics 文件。[2]

### 4.3 Value 与 future image

value scalar 被扩展到整个 value frame；采样后对该 frame 的全部元素求均值，并计算 \(\hat V=\operatorname{clip}((\bar z_v+1)/2,0,1)\)。future images 需要先把 blank/proprio/action 注入位置换回 VAE 编码前的 clean placeholder latent，再用 tokenizer decode；因此“保存了 future image”不代表执行时这些 latent 会送入 controller。[1][2]

## 5. 训练 routing、conditioning 与 loss

### 5.1 Dataset routing

LIBERO/RoboCasa dataset 把索引空间组织为 demos、success rollouts、failure rollouts。demo sample 的 `rollout_data_mask=0`；rollout sample 为 1。若 `return_value_function_returns=True`，rollout sample 再随机选择 world-model 或 value-function 角色。base config 令 demonstration sampling probability 0.5、success rollout sampling probability 0.5，而每个 rollout sample 内 world/value 默认各占一半，对应论文约 50/25/25 的 batch 角色比例。[1][2]

future index 固定为 (t+K)，episode 尾部 clamp 到最后一帧；action chunk 不足时重复最后动作补齐。value label 使用 future index 对应的 return。尾部 padding 没有独立 valid-step mask，因而边界样本会把 repeated terminal actions 作为真实 target；这是 frozen behavior，不应当作通用设计最优解。[2]

### 5.2 Conditioning mask

| 角色 | clean condition | target/主要用途 |
| --- | --- | --- |
| policy demo | current state (s) | action、future state、value 可联合预测 |
| world rollout | current state + action | future proprio/images；value 可作为 auxiliary |
| value rollout | full prefix (s,a,s') | value frame |
| rollout state-value variant | future state only | (V(s'))，mask current state/action |
| rollout Q variant | current state + action only | (Q(s,a))，mask future state |

`CosmosPolicyVideo2WorldModel.get_data_and_condition` 对 world sample 把 action frame 置为 clean condition；对 value sample 把除 value frame 之外的 frames 置 clean。V/Q 变体再对 current/action 或 future slots 做 input masking。这里 `mask=1` 表示 clean condition，`mask=0` 表示需 denoise/predict；与某些 attention mask 语义相反，面试时必须说清 mask 类型。[2]

### 5.3 EDM loss 与 target mask

frozen training 先把 action/proprio/value 写入 clean latent \(x_0\)，按 HybridEDMSDE 产生 noisy \(x_t\)，denoiser 输出 \(\hat x_0\)。主项可抽象为：

\[
\mathcal L_{EDM}=
\frac{1}{BCTHW}
\sum_{b,t,c,h,w}
m_{b,t}\,w(\sigma_{b,t})
\left(x_{0,bcthw}-\hat x_{0,bcthw}\right)^2.
\]

变量解释：\(m_{b,t}\) 是 latent-frame loss mask，\(w(\sigma)\) 是 noise-level weight。`mask_loss_for_action_future_state_prediction=True` 时 demo 仅保留 action slot、world sample 仅保留 future state slots、value sample 仅保留 value slot；默认 config 未在本轮确认该 flag 被主实验打开，因此不能把可选分支写成所有 checkpoint 的既定 loss。[2]

代码还可对 action slot 乘 `action_loss_multiplier`。各 action/future/value L1/MSE 同时被记录用于诊断，但主反向 loss 是 noise-weighted latent MSE，而不是日志里的 unweighted component L1。README 的“训练到 action L1 约 0.010/0.015”是经验阈值，不等于 closed-loop early stopping 充分条件。[2][3][4]

另有一个必须保留为 WARN 的 frozen-code 风险：`mask_value_prediction_loss_for_policy_prediction` 分支会构造 `final_mask_B_T`，但随后决定是否把 mask 乘到 `kendall_loss` 的条件没有列入这个 flag。主 LIBERO/RoboCasa config 没有打开该 flag，所以不能据此否定官方 checkpoint；但如果个人 WAM 配置单独启用它，应先做非零 mask/gradient 单测，不能仅凭配置名声称 auxiliary value loss 已排除。[2]

## 6. Sampling：parallel、autoregressive 与 denoising steps

### 6.1 Sampler contract

`CosmosPolicySampler` 在 `sample_clean=True` 且请求 steps (>1) 时，将 ODE solver 的 timestamp 数减一，最后再做一次 clean denoise；请求 1 step 时直接在首 sigma 上调用 denoiser。因此 CLI 的 `num_denoising_steps_action=5` 表示总 denoiser schedule contract，不应简单解读为“solver loop 五次”。[2]

LIBERO/RoboCasa inference config 将 SDE range 覆盖为 \(\sigma_{min}=4,\sigma_{max}=80\)，默认 direct policy 用 5 denoising steps。论文报告 H100 上 5-step action/future/value parallel generation 约 0.61 s/chunk、1-step 约 0.16 s/chunk；这些是指定硬件 wall-clock，不是本机 latency 事实。[1][2]

### 6.2 Direct policy

`get_action` 构造完整 latent sequence，以 current state slots 为 condition，一次采样得到 action/future/value。action 被反归一化后执行；future image/value 可用于可视化，但 direct eval 的 action selection 不读取它们。故“模型输出 value”不等于“在线 rollout 使用 value”。[1][2][5]

### 6.3 Autoregressive planning

planning path 的顺序是：

```python
def best_of_n_step(observation, task, N):
    # 1. Policy checkpoint samples N candidate action chunks using distinct seeds.
    proposals = [policy.sample_action(observation, task, seed=i) for i in range(N)]

    # 2. Planning checkpoint conditions on each proposal and predicts future state samples.
    futures = [planning_model.sample_future(observation, action) for action in proposals]

    # 3. Predict and aggregate values; paper uses future/value ensembles for ALOHA planning.
    scores = [aggregate_value(planning_model.sample_value(future)) for future in futures]

    # 4. Execute only the configured open-loop prefix, then observe the real environment again.
    best = proposals[argmax(scores)]
    return best[:num_open_loop_steps]
```

代码映射：`get_action` → `get_future_state_prediction` → `get_value_prediction`/`get_qvalue_prediction` → `max(seed_to_return_dict, key=value)` → action queue。论文 ALOHA planning 使用 (N=8)、每个 action 三个 future samples、每个 future 五个 value samples；repo 支持 serial/parallel worker pool、ensemble aggregation 与有限 search depth。[1][2][5]

## 7. Best-of-N 与 value 风险

best-of-N 的选择规则是：

\[
a^*=\arg\max_{a^{(i)}\sim\pi(\cdot\mid s),\;i=1..N}
\widehat V\!\left(\hat s'^{(i)}\right),
\qquad
\hat s'^{(i)}\sim\hat T(\cdot\mid s,a^{(i)}).
\]

变量解释：(pi) 是原 policy checkpoint，(hat T,widehat V) 来自 refined planning checkpoint。它不是 CEM/MPPI：没有迭代更新 action distribution，只对 policy proposals 排序；search depth 默认为 1，论文也明确主要使用 one-layer search。[1][2]

风险来自两层 optimizer's curse：候选越多，越容易选择 world-model hallucination 或过高 value estimate。论文用 rollout refinement、future/value ensemble 与 majority-mean 缓解，但不能消除 OOD calibration 问题。最小审计应同时报告：proposal diversity、future error、value calibration、rank correlation、selected-vs-random action success、N/latency 曲线与 failure traces。[1]

repo 的 `aggregate_value_predictions` 支持 average、LCB、success_vote、majority_mean 等 scheme；默认 LIBERO/RoboCasa config 是 average。论文 ALOHA planning 的 majority-mean 不能自动外推为所有官方 checkpoint 的默认 runtime。[1][2]

## 8. LIBERO / RoboCasa eval 合同

### 8.1 LIBERO

1. 使用 official suite task 与 default init states；每 task 取 `initial_states[episode_idx]` 后调用 `env.set_init_state`。
2. reset 后先执行 10 个 dummy actions 让物体稳定。
3. observation 为 agentview、wrist、9D proprio；图片按配置 vertical flip、JPEG、resize 与 center crop。
4. action queue 空时查询；默认 chunk 16、open-loop 16。
5. `env.step(action.tolist())` 返回 `done` 即记 success；需在独立 benchmark audit 中确认 wrapper 的 done/success 等价和版本。
6. 每 suite 默认 10 tasks×50 episodes=500 trials；paper/model card 的 98.5% 是四 suites、三 seeds 汇总口径。[1][3][5][6]

### 8.2 RoboCasa

1. controller 为 OSC_POSE，robot 是 PandaMobile，object split B；默认 5 个 layout/style scenes，每 10 个 episode 切一个 scene。
2. 每 episode 重建 env，seed 与 scene selection 进入 env kwargs；先 10 个 zero actions warmup。
3. observation 是 left/right third-person、wrist 与 9D proprio。
4. policy 输出 7D manipulation action；环境若要求 12D，则拼 `[0,0,0,0,-1]` 作为 inactive mobile-base controls。
5. default chunk 32，执行前 16 步再 requery；success 由 `env._check_success()`。
6. paper/model card 的 67.1% 是 24 tasks×50 trials×3 seeds=3600 trials；单 task 的 50 trials 不能直接称为 24-task average。[1][4][5][7]

### 8.3 Protocol comparability

必须冻结 checkpoint/model revision、dataset stats、T5 cache、repo commit、Python/PyTorch/CUDA、GPU、task/suite、init state、seed、determinism、camera flip/JPEG/crop、chunk/open-loop horizon、denoise steps、controller、max steps、success predicate、trial count。缺任一项时，跨报告差异最多是 directional context。

## 9. Checkpoint、资产与许可证边界

| Artifact | Frozen revision / file manifest | License / 风险 |
| --- | --- | --- |
| GitHub code | 18a2acc…；LICENSE、README、model/dataset/eval source | Apache-2.0；个别源文件头部出现与根 license 不同的历史版权措辞，复用仍需法务审查 |
| LIBERO policy model | cb689ec…；`.pt`、config.json、stats JSON、T5 pickle、README | model card 声明 NSCLv1、非商用 |
| RoboCasa policy model | 4b2a04…；`.pt`、config.json、stats JSON、T5 pickle、README | model card声明 NSCLv1、非商用 |
| Base Predict2 model | f50c09…；含 `model-480p-16fps.pt` | gated=auto；本轮未下载；2026-07-20 独立复核确认 model card 为 NVIDIA Open Model License。[8] |
| LIBERO/RoboCasa modified datasets | repo docs 给出 HF IDs | API/raw card 访问在本轮返回 401；数据条款与 artifact revision 尚未冻结 |

`snapshot_download(repo_id=...)` 在 code 中未传 revision，因此真实运行会解析当时的 remote HEAD。严格复现应改为显式 revision 或记录 cache snapshot SHA，并对 `.pt`、config、stats、T5 embedding 建 manifest/hash。[2]

## 10. Offline proxy、online success 与 WAM 项目边界

| 证据 | 可以证明 | 不能证明 |
| --- | --- | --- |
| action/future/value latent L1/MSE | frozen split/noise 下 component fitting | controller execution、causal dynamics、task success |
| future image visualization | 某候选的视觉预测 | contact correctness、proprio/action axis、calibrated transition |
| value MAE/MSE | labeled state distribution 上的 regression | top-N selection calibration、OOD ranking |
| direct-policy success | 固定 protocol 下 action execution | world/value auxiliary 的独立因果收益 |
| planning uplift | policy/planning/model/protocol 全部固定时的 selection gain | 单独归因于 world、value 或 N，除非有消融 |

WAM 项目数字必须留在 VOL 07 evidence layer：held-out MSE 需要 split、metric script、prediction/label artifact；官方 baseline 需要 model revision、24×5 或论文 protocol 的 summary；0-success 需要 local checkpoint load log、stats、action/gripper distribution、rollout video 与 harness hash。上游 latent injection、三目标 routing、best-of-N 均不能写成本人原创。

## 11. 失败诊断与最小测试矩阵

| 症状 | 首要证据 | 可能原因 | 最小实验 |
| --- | --- | --- | --- |
| loss 正常、0 success | action hist、stats SHA、controller trace | normalizer/axis/gripper/controller mismatch | dataset action round-trip + one-step env replay |
| future image好看、动作无效 | action sensitivity、contact trace | action ignoring / visual shortcut | 固定 observation，置换 action，测 future delta |
| value loss低、best-of-N 更差 | calibration/reliability、rank correlation | optimizer's curse / OOD overestimate | N sweep + random/median/top selector 对照 |
| direct policy可用、planning失败 | policy/planning checkpoint manifest | planning model distribution shift | original vs refined world/value blind eval |
| LIBERO高、RoboCasa低 | suite I/O/controller/protocol | camera/action/chunk/contact difference | per-layer contract diff，而非只比平均分 |
| 换硬件/torch 后掉点 | env lockfile、determinism log | numeric sampling sensitivity | three-seed paired rerun |
| chunk 前半好、后半漂 | per-step action error/success | open-loop horizon过长 | \(K_{exec}\in\{1,4,8,16\}\) paired sweep |

还应加入四个 deterministic unit tests：action latent injection→extraction round trip；value frame→scalar round trip；normalization→denormalization round trip；LIBERO 7D / RoboCasa 7→12D controller mapping。它们只验证接口，不替代 closed-loop rollout。

## 12. 面试答题骨架与当前边界

### 12.1 30 秒回答

“Cosmos Policy 的关键不是给视频模型加三个 head，而是把 proprio、action chunk、future observation 和 value 都编码成同一 latent video sequence 的 frame。通过 condition mask 和 sample routing，同一 diffusion backbone 可以学 \(p(a,s',V\mid s)\)、\(p(s',V\mid s,a)\) 和 \(p(V\mid s,a,s')\)。direct policy 一次并行生成三者但只执行 action；planning 则用原 policy 采样 N 个 action，再用 rollout-refined planning checkpoint 自回归预测 future/value，选最高 value。工程审计重点是 latent slot、loss mask、action stats、chunk/replan、checkpoint revision、init/warmup/controller 与 value calibration。论文官方分数不是我的本地项目结果。”

### 12.2 尚未核实

- 已核实：arXiv v1 full text、paper license、frozen repo commit/date/root license、latent injection/extraction、routing/mask/loss/sampler、LIBERO/RoboCasa config/eval path、两个 HF policy model revision/file list/model-card license；2026-07-20 独立复核重新命中13/13 official files、三份 HF revision、10/10 probes、9/9 local artifacts，并补核 base model license。[8]
- 尚未核实：checkpoint tensor/local hash、modified dataset card/revision、真实 inference、official result reproduction、external benchmark commit 与本地 WAM result/ownership。
- 用户本地待取证：WAM config/checkpoint、training/held-out metric artifact、official baseline cache revision、0-success rollouts、personal diff/ownership。
- 本页不把任何 WAM 本地数字写成 verified result，不把 Cosmos 上游设计写成本人贡献。
- 下一步：Audit C public facts 已独立复核；若继续文档复核，只选择 Source Audit D（Sim2Real）。VOL 04 aggregate knowledge/cards 已为44/44且全部 `unseen`，真实口述前不改变 mastery。

## 13. 参考文献（References）

1. Kim et al., “Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning”, arXiv 2601.16163v1, 2026. [arXiv](https://arxiv.org/abs/2601.16163v1) / [HTML](https://arxiv.org/html/2601.16163v1)。
2. NVlabs/cosmos-policy, frozen commit `18a2accadf4e7a3531e56754102af5a24d2316da`. [GitHub](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)。重点文件：`policy_text2world_model.py`、`policy_video2world_model.py`、`cosmos_sampler.py`、`cosmos_utils.py`、dataset/config files。
3. Cosmos Policy LIBERO guide at the frozen commit. [LIBERO.md](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/LIBERO.md)。
4. Cosmos Policy RoboCasa guide at the frozen commit. [ROBOCASA.md](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/ROBOCASA.md)。
5. Frozen eval sources: [LIBERO](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/libero/run_libero_eval.py) / [RoboCasa](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/robocasa/run_robocasa_eval.py)。
6. NVIDIA, Cosmos-Policy-LIBERO-Predict2-2B model card, revision `cb689ec0e3347c13667d70a78a3447388f5c3bb8`. [Hugging Face](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B/tree/cb689ec0e3347c13667d70a78a3447388f5c3bb8)。
7. NVIDIA, Cosmos-Policy-RoboCasa-Predict2-2B model card, revision `4b2a04c80d97202f86127ebec80461e8016ec1dc`. [Hugging Face](https://huggingface.co/nvidia/Cosmos-Policy-RoboCasa-Predict2-2B/tree/4b2a04c80d97202f86127ebec80461e8016ec1dc)。
8. [VOL 04 Audit C 独立事实复核](vol_04_cosmos_policy_wam_independent_fact_review.html)：paper、13个fixed-commit文件、HF revisions/config/statistics、10个deterministic probes与本地WAM artifacts已重新获取和reconcile，verdict为`PASS WITH WARNING`。
