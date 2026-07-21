# VOL 04 Batch 1：独立事实复核记录（WM-039..044）

> 状态：`reviewed_slice / WARN`  
> 复核日期：2026-07-16  
> 证据截止：2026-07-16  
> 复核范围：`VLA-WM-039..044` 的知识页、6 张题卡，以及它们引用的 UWM、Cosmos Policy、WorldGym primary/official-code 来源。  
> 结论先行：上游协议边界的关键事实已由独立 HTTP 读取的 frozen paper/repo 复核；本地 74.4%、92.8%、WAM 84/118 与 MSE 仍没有 raw artifacts，因此不升级为 verified personal evidence。

## 问题（Question）

本记录回答：六张题卡中的强事实是否能回到独立 primary/official-code 来源？哪些内容是论文/代码直接支持，哪些只是本仓库设计的分析框架，哪些仍被本地证据缺口阻断？

本次复核不是重新执行 UWM、Cosmos 或 WorldGym，也不是浏览器视觉 QA；它只审查 frozen source 的文字与代码路径，并把结果回写到 review JSON。

## 复核方法与证据等级

| 等级 | 本次含义 | 允许的面试口径 |
| --- | --- | --- |
| `primary-checked` | 直接读取论文 HTML 的方法/实验原文 | “论文报告/定义……” |
| `official-code-checked` | 直接读取 frozen commit 的代码或 README | “该 commit 的路径/默认值……” |
| `framework` | 本仓库提出的评估设计、统计或失败归因方案 | “我会这样设计/诊断……” |
| `claim-only` | 只在本地项目页、简历或口述中出现，没有 raw artifact | “项目材料记录为……待核验” |
| `blocked` | 缺 checkpoint、normalizer、环境补丁、episode 或 ownership 证据 | 不升级为复现/个人成果 |

复核入口被冻结为：UWM paper `arXiv 2504.02792v3`、UWM repo `b7d4067c8859775e5b08f681e76d538015cdd445`、Cosmos Policy repo `18a2accadf4e7a3531e56754102af5a24d2316da`、WorldGym repo `709665b29f5c95124e7dbc05b0d4d47cd353de97`。所有链接均在参考文献中给出。

## 1. UWM Table II：关键协议事实已复核

UWM v3 HTML 的实验段落直接写明：每个方法在 multitask dataset 上预训练 100K gradient steps、下游任务 finetune 10K steps；每个 environment 使用 3 个 random seeds，并在 50 个不同 initializations 上评估；Table II 的均值跨 initializations，置信区间跨 random seeds。[1]

同一论文的 OOD 描述写明：为制造未见初态，将每个 object 的 initialization range 增加 `0.03`，并移除 background objects 造成视觉分布变化。[1] Table II 的 UWM average 为 `0.79`，所以题卡把它称为论文内部的 OOD protocol mean 是有 primary 支持的；它不是本地 checkpoint 的成绩。

这里有一个重要的统计边界：论文的 `±` 是跨 finetune seed 的区间语义，不应被题卡改写成一次 250 episode 的 binomial confidence interval。当前题卡没有把它写成 binomial CI，保持正确。

## 2. UWM frozen runner：reset-style 与 Table II 不等价

在 frozen `experiments/uwm/eval_robomimic.py` 中，rollout loop 明确执行 `env.seed(e)` 后 `obs = env.reset()`，然后直接进入 model sampling；`config.rollout_length` 传给环境 wrapper。该入口没有 Table II OOD object-range/background-removal patch，也没有显式 warmup action。[2]

`environments/robomimic/wrappers.py` 进一步显示：`reset()` 调基础环境并用同一 observation 填充 history buffer；`step(actions)` 按 action sequence 逐步执行，并以 `_max_episode_length` 约束长度；`reset_to_state` 虽然存在，但不是上述 eval entrypoint 的默认路径。[3]

因此 `VLA-WM-039` 中“官方仓库 random-reset runner、不是 Table II”是 `official-code-checked`；“本地 fixed-pruned-init 74.4%”仍是 `claim-only`。两者不能因都使用 50 trials 就合并。

## 3. Cosmos Policy：代码默认值与本地 WAM 证据分离

Cosmos frozen LIBERO runner 的 config 注释和默认字段可直接核对：`chunk_size=16`、`num_open_loop_steps=16`、action denoising steps 为 5、future/value prediction 各为 1、`num_trials_per_task=50`；代码还明确检查训练 chunk 与 eval chunk 是否一致。[4]

这些是上游代码合同，不是本地 WAM 的训练结果。`VLA-WM-041` 只把 action-only / +world / +value / all 作为可归因的 factorial 设计；它没有声称论文已经提供这四臂消融，也没有把 WAM 的 84/118 当作已核验结果。

## 4. WorldGym：proxy scorer 的真实边界已复核

WorldGym frozen runner `run_openvla.py` 从每个 trial 的 `trial_png` 初始化 256×256 frame，调用 VLA 产生 action，再由 world model 生成视频；随后把生成视频交给 `predict()`。[5]

`utils.py` 的 `predict()` 将视频帧编码后发送给 `gpt-4o`，要求返回离散 `Final Score`，默认进行多次采样并解析投票；`aggregate_model_results()` 再把每个 trial score 聚合为均值与标准误。[6] 这直接支持“WorldGym 是 generated-video/VLM scorer proxy”的说法，但不支持它等价于 simulator success 或真实机器人 success。

## 5. 六张题卡逐题复核矩阵

| 题卡 | 独立核对结果 | 事实/框架边界 | 当前动作 |
| --- | --- | --- | --- |
| `VLA-WM-039` | `PASS WITH WARNING` | UWM paper OOD、repo reset、Table-II gap 已核对；12-field tuple 与 paired effect 是本仓库 framework | 保持题卡；74.4%/92.8% 继续 claim-only |
| `VLA-WM-040` | `PASS WITH WARNING` | WorldGym PNG→video→GPT-4o scorer 已核对；L0–L5、horizon curve、rank test 是分析框架 | 保持题卡；不把 proxy 当 sim/real |
| `VLA-WM-041` | `PASS WITH WARNING` | Cosmos action/future/value eval defaults 已核对；2×2 factorial 与 interaction 是设计建议 | 保持题卡；WAM 数字不升级 |
| `VLA-WM-042` | `FRAMEWORK / SOURCE-CONSISTENT` | action swap、cloned-state causal alignment、physical violation 是测试设计，不是已执行结果 | 明确“需 runtime” |
| `VLA-WM-043` | `FRAMEWORK / SOURCE-CONSISTENT` | first-divergence taxonomy 与 routing 是诊断框架 | 没有 episode trace 不命名具体 root cause |
| `VLA-WM-044` | `PASS WITH WARNING` | paper→repo→checkpoint→runtime→ownership 是证据审计框架，source 层级已核对 | 缺 checkpoint/runtime/ownership 时保持 claim-only |

## 6. 回写与未解决项

本次没有发现需要改写题卡核心事实的错误；修订重点是把“已核对的上游事实”和“本仓库设计的实验框架”分开记录。题卡仍全部 `unseen`，因为事实复核不等于候选人口述掌握。

仍然阻断强结论的证据包括：

1. 用户本地 UWM checkpoint、normalizer、config、OOD environment patch、init IDs 和逐 episode JSONL。
2. WAM 的 local checkpoint、action/world/value split、prediction/label artifacts、controller/fork manifest 与 raw episodes。
3. WorldGym scorer/API version、local world-model checkpoint 与 simulator/real paired validation。
4. 浏览器视觉 QA 与候选人的真实口述记录。

```python
def phrase_claim_at_weakest_evidence(atoms, evidence_graph):
    # Split a sentence into method, metric, protocol and ownership atoms.
    verdicts = [evidence_graph.lookup(atom) for atom in atoms]

    # A missing checkpoint/runtime/protocol edge blocks a strong reproduction claim.
    if any(v in {"claim-only", "blocked"} for v in verdicts):
        return "按最弱证据逐原子表述，并保留待核验边界"

    # Only a continuous primary→code→runtime→ownership chain permits a strong claim.
    return "可以在对应 protocol 范围内给出已核验口径"
```

## 复核结论

本批 6 张题卡的关键上游事实现在有独立 primary/official-code 依据；统计、consistency、failure taxonomy 和 evidence chain 中明确标注为 framework 的部分没有被伪装成论文结论或本地实验结果。总体 verdict 仍为 `WARN`，原因是本地运行 artifacts、浏览器视觉 QA 和真实口述尚未完成。

## 参考文献（References）

1. Zhu et al., “Unified World Models: Coupling Video and Action Diffusion for Pretraining on Large Robotic Datasets”, arXiv `2504.02792v3`，[HTML](https://arxiv.org/html/2504.02792v3)。
2. WEIRDLabUW, `unified-world-model` frozen commit `b7d4067c8859775e5b08f681e76d538015cdd445`，[`eval_robomimic.py`](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/experiments/uwm/eval_robomimic.py)。
3. 同上 frozen commit，[`wrappers.py`](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/environments/robomimic/wrappers.py)。
4. NVIDIA, `cosmos-policy` frozen commit `18a2accadf4e7a3531e56754102af5a24d2316da`，[`run_libero_eval.py`](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/experiments/robot/libero/run_libero_eval.py)。
5. `world-model-eval/world-model-eval` frozen commit `709665b29f5c95124e7dbc05b0d4d47cd353de97`，[`run_openvla.py`](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/run_openvla.py)。
6. 同上 frozen commit，[`utils.py`](https://github.com/world-model-eval/world-model-eval/blob/709665b29f5c95124e7dbc05b0d4d47cd353de97/src/world_model_eval/utils.py)。
7. 本仓库 [VOL 04 Audit E](vol_04_benchmark_evidence_claim_to_protocol.html)，canonical [Markdown](vol_04_benchmark_evidence_claim_to_protocol.md)。
8. 本仓库 [VOL 04 Batch 1 知识页](../knowledge/vol_04_world_model_sim2real.html) 与 [6 张题卡](../questions/vol_04_world_model_sim2real.html)。
