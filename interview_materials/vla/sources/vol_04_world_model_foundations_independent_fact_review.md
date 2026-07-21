# VOL 04 Source Audit A：World Model / PlaNet / DreamerV3 独立事实复核

> 状态：`reviewed_slice / WARN`  
> 复核日期：2026-07-16  
> 证据截止：2026-07-16  
> 复核范围：`VLA-WM-001..014`、`VLA-WM-019..021` 的 source audit；下一知识批只开放 `VLA-WM-001..010`。  
> 结论先行：World Models、PlaNet、DreamerV3 的关键方法事实和 DreamerV3 frozen repo 的实现边界已独立核对；DreamerV3 repo 是 reimplementation，不应称作论文作者官方代码；PlaNet latent overshooting 不能外推为 DreamerV3 的实现事实。

## 问题（Question）

本记录回答：Source Audit A 中关于 world-model 概率合同、World Models、PlaNet、DreamerV3 RSSM、imagination actor-critic、KL/free-nats、one-step/open-loop 和 metric boundary 的主张，哪些可回到 primary paper 或 frozen official-code，哪些只能作为分析框架？

本次复核只读取 frozen paper/repository 内容，不执行 DreamerV3 训练、不下载 checkpoint、不声称复现论文结果，也不把通用机制写成本地项目贡献。

## 复核方法与证据等级

| 等级 | 含义 | 面试口径 |
| --- | --- | --- |
| `primary-checked` | 直接核对论文 HTML/Ar5iv 的正文、公式或实验描述 | “论文定义/报告……” |
| `official-code-checked` | 直接读取 frozen repo 的 README、源码或配置 | “该 commit 的实现……” |
| `framework` | 根据论文/代码抽出的评估或诊断设计 | “我会这样区分/测试……” |
| `warning` | 事实方向正确，但来源是 reimplementation、配置依赖或缺实验 artifact | “在该来源/配置范围内……” |
| `blocked` | 本地 checkpoint、运行日志、结果或 ownership 缺失 | 不升级为复现或个人成果 |

冻结对象：World Models `arXiv 1803.10122`、PlaNet `arXiv 1811.04551`、DreamerV3 `arXiv 2301.04104`，以及 `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`。

## 1. World Models：VAE、MDN-RNN 与 controller 的分解已核对

World Models 论文把系统拆成视觉模型 V、记忆模型 M 和 controller C。VAE 把每帧图像压成 latent (z_t)；MDN-RNN 预测动作和历史条件下的未来 latent 分布；controller 读取 latent 与 recurrent state 产生动作。论文给出了 `env.reset → vae.encode → controller.action → env.step → rnn.forward` 的 rollout 逻辑。[1]

论文还明确展示了在模型生成的 dream 中训练/部署 controller，并把 decoder 用于可视化。因此 Audit A 中“world model 不等于视频生成器；是否可行动要看 action condition、状态变量和执行合同”的表述有 primary 支持；“dream controller 的收益与 model exploitation 风险需要单独审计”属于同源分析边界，不是本地实验结果。

## 2. PlaNet：deterministic/stochastic latent、overshooting 与 online planning 已核对

PlaNet 论文摘要和方法部分直接写明：latent dynamics 同时包含 deterministic 与 stochastic transition；提出 multi-step variational inference objective `latent overshooting`；利用 learned latent dynamics 在 latent space 进行 online planning，并采用 receding-horizon 方式每步重新规划。[2]

论文还讨论了 learned model planning 的风险，包括多个可能未来、分布外过度自信，以及模型误差造成的规划问题。因此 Audit A 中“latent overshooting 约束多步预测”和“不能从视觉质量直接推导 long-horizon planning 成功”是有 primary 依据的。

一个必须保留的边界是：PlaNet 的 overshooting 是 PlaNet 论文机制；当前 DreamerV3 frozen repo 的 `rssm.py` 显示 observe/imagine、dyn/rep KL 和 free-nats，但没有足够证据把它命名为 PlaNet overshooting。题库和知识页不得写成“DreamerV3 使用 PlaNet overshooting”。

## 3. DreamerV3 RSSM：论文因子分解与 frozen repo 路径已核对

DreamerV3 论文把 world model 写成 RSSM：序列模型由前一时刻 (h_{t-1},z_{t-1},a_{t-1}) 得到 (h_t)，posterior (q_phi(z_tmid h_t,x_t)) 使用当前 observation，prior (p_phi(z_tmid h_t)) 在 imagination 时不读取未来 observation；decoder、reward、continue 预测器作用在 latent feature 上。[3]

frozen repo 的 `dreamerv3/rssm.py` 与论文合同逐项对应：

| 论文/概念 | frozen code evidence | 复核结论 |
| --- | --- | --- |
| posterior filtering | `RSSM.observe` | `official-code-checked` |
| action-conditioned prior imagination | `RSSM.imagine` | `official-code-checked` |
| dynamics/representation KL | `RSSM.loss` 中 `dyn` / `rep` | `official-code-checked` |
| stop-gradient 方向 | `sg(post)` 与 `sg(prior)` 两条 KL | `official-code-checked` |
| free nats | `free_nats=1.0` 与 `jnp.maximum` | `official-code-checked` |
| actor/critic imagination | `Agent.loss` 调用 `dyn.imagine`、lambda-return 与 policy/value loss | `official-code-checked` |

DreamerV3 论文也直接描述 world model 预测 future representation/reward、actor 选择 action、critic 评估 outcome，并使用 imagined trajectories 学习 actor/critic。[3] 因而 Audit A 的 posterior/prior、imagination 和 actor-critic 主线可以保留。

## 4. DreamerV3 的 KL/free-nats 与 repo provenance 边界

论文给出 prediction、dynamics 和 representation loss，并说明 dynamics/representation loss 的 stop-gradient 方向、loss scale 与 free bits clipping；论文文字写的是低于 `1 nat` 时裁剪相关项。[3]

frozen `rssm.py` 采用 `free_nats: float = 1.0`，并分别计算 `KL[sg(post) || prior]` 与 `KL[post || sg(prior)]` 后用 `jnp.maximum` 截断；`configs.yaml` 另记录 `loss_scales`、RSSM 维度和 replay-value 相关配置。[4] 这支持机制映射，但具体训练结果仍依赖 config、数据、checkpoint 和运行环境。

README 的 Disclaimer 直接称该仓库是基于开源 DreamerV2 的 DreamerV3 reimplementation，并与 Google/DeepMind 无关。[4] 因此面试中应说“该 frozen repo 的 reimplementation code path”，不能说“DreamerV3 官方作者代码”或从 repo 推导个人项目结果。

## 5. one-step、open-loop、actionability 与 metric boundary

以下内容属于 `framework`，不是某个论文的单一 benchmark recipe：

1. teacher-forced one-step 使用真实历史，open-loop rollout 使用模型自己的前一步预测；两者必须分开报告。
2. action-conditioned 只说明 action 进入条件，不自动证明可干预；action-swap、magnitude sweep、cloned-state intervention 与 closed-loop trace 是合理的验证设计。
3. PSNR/SSIM/FVD、latent KL、reward/value loss、action loss、open-loop error 与 closed-loop success 处于不同证据层，不能跨层替代。
4. aleatoric/epistemic 是分析分类；ensemble、posterior sample 或 disagreement 只是估计手段，不能自动等价于真实风险。

这些框架与 PlaNet/DreamerV3 对 long-horizon model bias、future prediction 和 imagined control 的讨论一致，但本地尚无 calibration、action-swap、world-model checkpoint 或 rollout trace，不能写成“已验证”。

```python
def audit_world_model_claim(claim, paper, repo, local_artifacts):
    # 1. Split the claim into method, implementation, metric and ownership atoms.
    atoms = split_claim_into_atoms(claim)

    # 2. Match each atom to primary paper and frozen-code evidence.
    upstream = [match_primary_or_code(atom, paper, repo) for atom in atoms]

    # 3. Require checkpoint/runtime artifacts before calling a local result reproduced.
    if local_artifacts.missing("checkpoint", "config", "episodes"):
        return phrase_as_upstream_or_framework(upstream)

    # 4. Only a continuous paper -> repo -> runtime -> ownership chain allows a strong claim.
    return build_evidence_bounded_answer(upstream, local_artifacts)
```

## 6. 题目覆盖与回写矩阵

| 范围 | 复核状态 | 允许动作 |
| --- | --- | --- |
| `VLA-WM-001..010` | `PASS WITH WARNING` | 可进入下一批知识页；保留 paper/reimplementation/local boundary |
| `VLA-WM-011..014` | `PASS WITH WARNING` | 继续留在 Source Audit A，后续单独生成知识批 |
| `VLA-WM-019..021` | `PASS AS FRAMEWORK` | 指标与 imagination 机制可教，但不写本地结果 |
| DreamerV3 repo provenance | `PASS WITH WARNING` | 不称官方作者代码 |
| PlaNet overshooting → DreamerV3 | `BLOCKED FOR STRONG CLAIM` | 不做跨方法实现归因 |
| 用户 WAM/UWM 项目证据 | `BLOCKED` | 等 checkpoint、normalizer、run/episode artifact |

本次没有发现需要改写 Audit A 核心技术事实的错误；新增的边界是把“PlaNet overshooting 不可外推到 DreamerV3”显式列为禁止升级项。下一知识批只开放 `VLA-WM-001..010`，不生成题卡。

## 复核结论与未解决项

Source Audit A 的关键 primary/official-code 事实已独立复核，review 仍保持 `WARN`，原因是：没有 DreamerV3 checkpoint/result reproduction、没有用户本地 world-model artifacts、浏览器 `file://` 视觉 QA 受策略阻断、也没有真实口述。知识页可以进入下一增量，但不能把模块状态推进到 `reviewed` 或 `drilled`。

## 参考文献（References）

1. Ha & Schmidhuber, “World Models”, arXiv `1803.10122`，[Ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1803.10122)；[arXiv record](https://arxiv.org/abs/1803.10122)。
2. Hafner et al., “Learning Latent Dynamics for Planning from Pixels” (PlaNet), arXiv `1811.04551`，[Ar5iv HTML](https://ar5iv.labs.arxiv.org/html/1811.04551)；[arXiv record](https://arxiv.org/abs/1811.04551)。
3. Hafner et al., “Mastering Diverse Domains through World Models” (DreamerV3), arXiv `2301.04104`，[HTML](https://arxiv.org/html/2301.04104)。
4. `danijar/dreamerv3@e3f02248693a79dc8b0ebd62c93683888ddaccfe`，[README](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/README.md)、[`rssm.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/rssm.py)、[`agent.py`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/agent.py)、[`configs.yaml`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/dreamerv3/configs.yaml)、[`LICENSE`](https://github.com/danijar/dreamerv3/blob/e3f02248693a79dc8b0ebd62c93683888ddaccfe/LICENSE)。
5. 本仓库 [Source Audit A canonical Markdown](vol_04_world_model_foundations_claim_to_code.md)、[HTML](vol_04_world_model_foundations_claim_to_code.html) 与 [review](vol_04_world_model_foundations_claim_to_code.review.json)。
