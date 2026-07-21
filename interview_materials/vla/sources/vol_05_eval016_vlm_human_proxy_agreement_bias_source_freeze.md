# VOL 05 EVAL-016 Source Freeze：VLM / Human Proxy 一致性与偏差

> 状态：`source_frozen / VLA-EVAL-016 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本切片冻结VLM-as-judge任务定义、human annotation protocol、chance-corrected agreement、ordinal/rank/calibration、position/verbosity/self-enhancement与视觉/时序bias、WorldGym GPT-4o scorer边界、abstention和paired human validation；只生成一张`VLA-EVAL-016`原子题卡，EVAL-017后置。

## 问题（Question）

怎样判断VLM judge能否代替人工或真实环境给机器人视频评分？“VLM和多数票80%一致”“Pearson很高”“五次GPT-4o投票稳定”都不够。必须先冻结评分任务和human protocol，再同时报告混淆、chance-corrected agreement、排序、校准、slice/bias与cluster uncertainty，并验证judge看到的证据是否足以判断接触、终局和安全。

## 1. 冻结来源、Revision 与边界

| ID | 来源 | 类型 / revision / license | SHA-256 | 支持范围 | 不支持 |
| --- | --- | --- | --- | --- | --- |
| S1 | Quevedo et al., *WorldGym* + official repo | primary paper；arXiv `2506.00613v3`，2025；official-code `world-model-eval/world-model-eval@709665b29f5c95124e7dbc05b0d4d47cd353de97`；frozen tree未发现LICENSE | PDF `81ac9b9109a60c39b5c739dcd0484750f4d9c29e70f87666601076993ab8dd24`；README `d74b879b809fd054fa8418247365cb0bc1d7f267ae7122526b081a840e409243`；`utils.py` `e7a8b19278c8c7a798cc13557fb9b646a0f42ea3b87234a1a236ab856d31f630`；`world_model.py` `8171fca40ea924b48f73331ee5cd0c2a8462d3e9de5f9ce649ba5513fecb1ce5` | world model作为robot policy proxy；generated video由VLM给reward；代码中GPT-4o多票0/0.5/1、聚合入口 | VLM score等于sim/real success；API可重放；本地WAM已验证human agreement |
| S2 | Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* + FastChat | primary paper + official-code/data；arXiv `2306.05685v4`；`lm-sys/FastChat@587d5cfa1609a43d192cedb8441cac3c17db105d`；Apache-2.0 | PDF `1574982845157569b85c1214bfa9987000384d7a5e3b5fbdcc5a29afec59cb81`；judge README `4104f9e877fe04a4a87a5b6618114adc8604f09ceca09be198f96189c4c2238e`；LICENSE `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | position、verbosity、self-enhancement与reasoning bias；controlled/crowd human agreement实例；pairwise/single grading入口 | 文本judge的80%自动迁移VLM/robot video；agreement证明无系统偏差 |
| S3 | Lee et al., *Prometheus-Vision* + official repo | primary paper + official-code；arXiv `2401.06591v1`；`kaistAI/prometheus-vision@fe668b5e7e120e5bea8a3821eeb468ddf719c23c`；Apache-2.0 | PDF `b50eeac024f34ba41052fd7eb03259f1e6a93cdf023dded50d902a4c9004336e`；README `a62f1c579d2fb3e3d9b9830330e17be9b1eb8d98755d5d25452520f6c3018b7b`；LICENSE `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | customized rubric、reference answer、image-grounded evaluator；公开实验报告human correlation | 任意rubric都可靠；correlation等于agreement/calibration；机器人时序/物理可见性 |
| S4 | Chen et al., *MJ-Bench* | primary paper；arXiv `2407.04842v1`，2024；论文许可未断言 | PDF `89cadf93084abcb7c117bb67d813a6c2e012d211efbaafa5b49902893b46eaee` | multimodal judge在alignment/safety/image quality/bias维度表现不同；judge family差异；Likert与numerical反馈差异；human end-to-end validation | 图像生成结论自动迁移机器人视频；某个judge全维度最佳 |
| S5 | scikit-learn Cohen kappa + SciPy rank/bootstrap | official-code；`scikit-learn@6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6`，BSD-3-Clause；SciPy `v1.16.3` tag object `56e567e70ccad213d04ab04e7cfe7365562a71f1`，BSD-3-Clause | sklearn `_classification.py` `f88e79761ea9bb9b100c2019f33c4d9dcd98e9d46d21f22f703563bdf80e8451`；COPYING `50d6a9d340f19ab355609917993114daf5f47e3161067bcf34955bbd05cd9cb0`；SciPy `_stats_py.py` `c1f98867bce4a0bdb336b6c33bd930bcf50f8b9aae6a654e1f9a6d2064bda3b4`；`_resampling.py` `ad8335279281c69d4a3bbf4449100e3ac5e1f5bc7af360963133973ed2a64d7e` | un/weighted Cohen kappa、Spearman/Kendall、paired bootstrap实现入口 | 自动选择统计单元、human gold、权重或可接受阈值 |
| S6 | 本地前置节点 | canonical local prerequisites | EVAL-011 `c4a085e96e8ae6ed4d22660b49d26d8faad0b338e8990b132ae3288ee28eb0dd`；EVAL-015 `9136d4de46b2c754ba4ed23c6ac0515f2239d2031e246c7479876fb6baf5d872`；WM-019 `2cff5c30c82ec70901957fd244f056fa32982b9be10411735c0a8aa6214b08a5`；Benchmark Audit `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a`；Batch1 Review `115eed1c2c3d0d98adc46acde2e8effe12f0305b2f7ea2a81c7fa3ffac2503c1` | proxy-online panel、judge hacking、metric ladder、WorldGym code事实与证据边界 | 五项目已有VLM-human agreement study |
| S7 | 五项目inventories + WAM manifest | local evidence | Harness `66acc52c685d5ace6926a42976b7ba59b6f889d6848f74bfd8216cad92aa291e`；OPD `0a68251de06bc8494b7d2be5e6dc169fc860a629c2f312e623db69ed29db12bb`；OpenPiVLA `a3c644f949295d72889b2acf6456bfd050e05c147b14381bbb067504a34ce293`；WAM `078c86b1484fe38fdd136428123c9529c6b750dfea5e031ec506cf617517772d`；UWM `728b8326dc345072886d0909fe2b8d81dfde3993771e7febed446d471bd3674d`；WAM manifest `1ab8709201e2e75f580cb0aa0f8465defb546d63b2aab70a1752239a7da8f697` | 当前视频/metric/scorer artifacts与缺口 | 任一项目已有paired VLM-human labels、agreement或bias结论 |

S1是机器人proxy实例，S2—S4提供judge机制与公开实验，S5只提供统计实现。下面的human annotation、cluster inference、visual/temporal bias matrix和release gate是source-consistent engineering synthesis，不冒充论文原协议或项目既有结果。

## 2. 先冻结 Judge 在回答什么

同一个“VLM score”可能是完全不同的estimand：

| task | label/输出 | 回答 | 适合指标 |
| --- | --- | --- | --- |
| binary success | fail/success | 是否达到冻结终局predicate | confusion、sensitivity/specificity、kappa |
| ordinal completion | 0/0.5/1或Likert | 完成程度 | weighted kappa、MAE、within-one |
| pairwise preference | A/B/tie | 哪个更好 | pair accuracy、tie、position-swap consistency |
| ranking | policy/checkpoint排序 | 能否筛选候选 | Spearman/Kendall、top-k regret |
| continuous quality | 0–100/概率 | 程度或概率 | calibration、Brier、reliability、MAE |
| failure taxonomy | perception/action/contact/... | 失败属于哪类 | per-class confusion、macro-F1、human adjudication |

correlation、agreement、classification、calibration和causal validity回答不同问题。若VLM只看采样video frames，而human看完整video+state，二者信息集不同；此时差异不全是模型bias，也可能是observability gap。protocol必须列出frame rate、camera、crop、duration、temporal order、state overlay、instruction、rubric和reference。

## 3. Human Label 也不是无噪声 Gold

可信human protocol至少包括：

- rubric把success、partial、failure、safety/forbidden effect写成可操作条件；
- annotator先在calibration set训练，再进入blind labeling；
- 隐藏model/policy/checkpoint/provider身份，随机化A/B顺序；
- 每个高风险case至少双标，保存raw labels，不只存majority；
- disagreement进入独立adjudication，adjudicated label与原始意见分开；
- 记录annotator ID、expertise、language、batch/order、time/fatigue和evidence shown；
- human-human agreement作为可达上限/任务含糊度信号，但不自动定义VLM合格线。

若human rubric依赖不可见的force/contact或环境内部predicate，而只给视频，人工也可能系统性误判。必要时用simulator state/effect sink建立objective predicate，并把human定位为语义/质量/异常补充。

## 4. Raw Agreement 与 Cohen Kappa

对二分类VLM `v_i`与human/adjudicated `h_i`，先建完整confusion matrix。observed agreement与chance agreement：

\[
p_o=\frac{1}{N}\sum_{i=1}^{N}\mathbb{1}[v_i=h_i],
\qquad
p_e=\sum_{c}p_v(c)p_h(c),
\qquad
\kappa=\frac{p_o-p_e}{1-p_e}.
\]

变量解释：`p_v(c),p_h(c)`是两侧边际类别率。直觉：若90%都是失败，恒预测失败可有90% raw agreement，kappa会扣除边际偶合。实现映射：报告confusion、prevalence、accuracy、sensitivity/specificity、balanced accuracy、kappa和cluster CI；不只报一个百分比。[S5]

kappa受prevalence与marginal distribution影响，不能机械套“0.8很好”。class imbalance、tie策略和label collapse要单独展示；critical success/safety cell即使overall kappa高也可hard fail。

## 5. Ordinal Label 与 Weighted Kappa

0/0.5/1或Likert分数有顺序，错一档与错两档代价不同：

\[
\kappa_w=1-
\frac{\sum_{a,b}w_{ab}O_{ab}}
{\sum_{a,b}w_{ab}E_{ab}}.
\]

变量解释：`O/E`是观察/边际期望计数，`w_ab`是事前冻结的disagreement weight，可用linear或quadratic。直觉：binary collapse会丢失partial completion信息。实现映射：同时报exact、within-one、weighted kappa、per-class confusion和failure severity；scikit-learn实现支持unweighted/linear/quadratic。[S5]

权重必须由决策风险决定，不能看完结果再选quadratic让数字更好。WorldGym代码的0/0.5/1只在任务声明partial description时使用；不同task label space不能直接平均。[S1]

## 6. Pairwise、Position Swap 与 Ranking

pairwise human/VLM agreement：

\[
A_{\mathrm{pair}}=
\frac{1}{N}\sum_i\mathbb{1}[j_i^{\mathrm{VLM}}=j_i^{\mathrm{human}}],
\quad j_i\in\{A,B,\mathrm{tie}\}.
\]

变量解释：tie必须作为正式类别或有预注册margin，不能强拆。实现映射：每对样本同时跑`A,B`和`B,A`，分别报human agreement、swap consistency、first-position win rate和tie rate。

MT-Bench公开研究报告position、verbosity、self-enhancement与有限reasoning bias，并在其文本域数据上比较human agreement。[S2] 这些bias是VLM judge的必测启发，不是机器人域已发生的证据。pairwise排序还要按policy/task cluster计算Spearman/Kendall与top-k regret；高pair agreement不代表absolute success threshold正确。

## 7. Correlation 不是 Agreement

若VLM总比human高2分，Pearson/Spearman可很高但absolute agreement差；若只保持排序，可能适合筛选checkpoint，不适合宣布success rate。对policy `j`：

\[
\rho_{\mathrm{rank}}=
\operatorname{Spearman}\!\left(
\{q_j^{\mathrm{VLM}}\}_{j=1}^{J},
\{q_j^{\mathrm{human/real}}\}_{j=1}^{J}
\right).
\]

变量解释：独立变异单位是policy/checkpoint，不是同一video的五次judge调用。实现映射：固定task/init support，保存每个policy的uncertainty，使用task/policy cluster bootstrap；`J=1`无法证明ranking能力。[S5][S6]

WorldGym论文在所测policy集合上主张world-model success与real success高度相关并保留relative ranking。[S1] 安全解释只限其protocol/support；不能外推任意task、world model、VLM/API版本或个人WAM。

## 8. Probability Calibration 与 Abstention

若通过多次采样或logit得到`p_i=P(success)`，Brier score：

\[
\operatorname{Brier}=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2.
\]

变量解释：`y_i`是adjudicated/objective binary outcome。实现映射：画reliability diagram、ECE/Brier、coverage-risk与selective accuracy；把unparseable、tie和judge disagreement纳入abstain，不静默重试到有利结果。

同一VLM同一prompt的五次采样只测sampling variation，不是五个独立专家。WorldGym `predict()`调用literal `gpt-4o`、默认`n=5`，解析0/0.5/1，并在平票时按`1 > 0.5 > 0`选择；这是一条明确的optimistic tie-break边界，且没有冻结provider snapshot。[S1] 必须保存五个raw responses、parsed count、vote distribution、retry和API metadata，不能只存majority score。

## 9. Bias / Perturbation Matrix

| family | paired probe | 失败信号 |
| --- | --- | --- |
| position/order | A/B swap、frame sequence reverse、camera order swap | preference随位置翻转 |
| verbosity/style | 相同结果加长解释、专业措辞、置信语气 | 与真实状态无关的加分 |
| identity/self | 隐藏/替换model/provider/checkpoint名称 | judge偏向同源/知名模型 |
| rubric/prompt | paraphrase、criteria顺序、score anchor变化 | decision大幅漂移 |
| visual quality | blur、compression、brightness、world-model artifacts | 画质被误当任务成功 |
| temporal | frame sampling、丢终局帧、先成功后破坏 | 只看关键帧/首尾shortcut |
| viewpoint | third/wrist camera、遮挡、crop | 可见性slice差异 |
| task/class | long horizon、contact、partial、rare safety | minority/高风险recall低 |
| adversarial | overlay文字、judge prompt injection、success自述 | follow image/text injection |
| language/culture | instruction/rubric语言、术语 | 跨语言agreement下降 |

对每个group `g`报告bias gap：

\[
\Delta_g=M_g-M_{\mathrm{reference}},
\]

变量解释：`M`可以是kappa、sensitivity、pair accuracy或Brier，必须同metric同protocol。实现映射：paired mutation优先，给cluster CI和worst target slice；overall平均不能抵消rare safety/contact failure。

## 10. MJ-Bench 与 Prometheus-Vision 给出的边界

Prometheus-Vision强调customized rubric、reference与image grounding，并报告公开实验中的human correlation。[S3] 它支持“rubric-conditioned evaluator值得研究”，不支持任意rubric、任意domain或absolute agreement。

MJ-Bench把multimodal judge分成alignment、safety、image quality和bias维度，公开实验显示不同judge family的优势不同，VLM对Likert自然语言反馈相对数值scale更稳定。[S4] 这说明不能用一个overall judge score覆盖所有机器人风险；rubric维度、label scale与human validation必须分别验。

## 11. Matched Evaluation Protocol

1. 预注册task、label scale、rubric、success/partial/failure predicate与主要metric；
2. 从真实episode/task/policy分层抽样，group split防视频近重复泄漏；
3. human blind double-label + adjudication，保存raw opinions；
4. VLM冻结provider/model snapshot、prompt、frame sampler、temperature/seed、n、parser、retry/cache；
5. human与VLM尽量看到相同evidence；不同则显式建information-arm；
6. 同一raw bundle跑全部judge，做position/visual/temporal/adversarial paired probes；
7. 以episode/policy/task为cluster给CI，不把frames、votes或annotators当独立任务样本；
8. 同报human-human、VLM-human、confusion/kappa、rank、calibration、bias slices与abstention；
9. 若用于release，关键safety/terminal predicate仍由state/effect或human veto兜底；
10. scorer升级对旧raw bundlebridge rescore，fresh holdout防反复调参。

## 12. 最小 Artifact Bundle

```text
vlm_human_agreement/
  protocol_manifest.json
  rubric_and_label_schema.json
  episode_sample_manifest.json
  evidence_shown/
  human_raw_labels.jsonl
  human_adjudication.jsonl
  vlm_raw_responses.jsonl
  scorer_runs.jsonl
  paired_bias_mutations.jsonl
  confusion_rank_calibration.parquet
  summaries/by_slice.json
  checksums/manifest-sha256.txt
  reproduce.ps1
```

每条记录绑定episode/policy/task/init、evidence digest、human annotators、VLM snapshot/prompt/frame sampler、raw response/votes/parser、label、confidence/abstain和adjudication。只有summary截图无法重算agreement或排查bias。

## 13. 评估伪代码

```python
def evaluate_vlm_human_agreement(episodes, human_panel, vlm_judge, protocol):
    spec = freeze_rubric_labels_sampling_judge_and_metrics(protocol)
    sample = group_stratified_locked_sample(episodes, spec)

    # Keep raw independent labels before majority/adjudication.
    human_rows = human_panel.blind_double_label(sample, spec.rubric)
    gold_rows = adjudicate_without_model_identity(human_rows, sample)

    # Judge the same evidence and persist every vote, parse and retry.
    vlm_rows = vlm_judge.score_all(sample, spec, keep_raw_votes=True)
    mutation_rows = run_position_visual_temporal_and_injection_pairs(sample, vlm_judge, spec)

    # Resample episode/policy/task clusters rather than frames or votes.
    return recompute_confusion_kappa_rank_calibration_bias_and_abstention(
        human_rows, gold_rows, vlm_rows, mutation_rows, cluster=spec.cluster
    )
```

这是评估合同，不是五项目已有实现；human adjudication和VLM都可能共享video observability盲点，真实安全仍需state/effect证据。

## 14. 五项目 Evidence Mapping

| 项目 | 已有证据 | 能安全说 | 不能说 / 缺口 |
| --- | --- | --- | --- |
| WAM / Cosmos | WorldGym公开机制；本地单episode三camera/300-step action-video diagnostic与manifest | 可设计generated-video VLM-vs-human/state协议；解释WorldGym proxy边界 | 本地运行WorldGym、GPT-4o score、human labels、agreement或真实success替代 |
| UWM / LIBERO | user-confirmed 5-task summary与env success protocol | environment predicate可作为未来VLM对照的一层 | 没有VLM judge输出、人标video或paired agreement |
| OpenPiVLA | official baseline rollout diagnostics与archive summary | 可从raw episode抽样做人/VLM盲评（若补齐bundle） | 97.4已被VLM/human验证；formal checkpoint有paired labels |
| OPD | deterministic point/box/text scorer与raw-holdout协议 | 可将human point/box质量作为scorer校准补充 | static scorer是VLM judge；已有human agreement |
| Robot Harness | text/tool parser、semantic scorer与proxy suite | 可复用judge versioning、mutation、raw bundle思想 | schema-aware scorer是VLM video judge；已有human/video一致性 |

五项目当前没有`episode/video × raw human labels × VLM responses × objective predicate`四方bundle。本节点不生成任何agreement、kappa、rank或bias项目数字。

## 15. Claim Ladder 与下一入口

| 级别 | 可接受表述 | 所需证据 |
| --- | --- | --- |
| C0 | 理解VLM judge局限与统计指标 | 公开来源、口述 |
| C1 | 实现版本化VLM scorer | code/prompt/frame/parser SHA与raw responses |
| C2 | 在locked样本上测human agreement/bias | raw double labels、adjudication、kappa/rank/calibration/slices |
| C3 | 对所测policy/task支持proxy筛选 | matched policy panel、cluster CI、fresh holdout与state predicate |
| C4 | 用于部署release的一部分 | 持续human/state audit、abstention、incident/drift与hard veto |

当前项目最多支持C0与评估设计；WorldGym是公开上游机制，不是个人C1/C2证据。

本节点保持`WARN/unseen`。下一内容节点固定为`VLA-EVAL-017`：simulator success、shadow mode与真机gate；本切片不生成该节点，也不创建`coaching_state.md`。

## 参考文献（References）

1. Quevedo et al., [*WorldGym*, arXiv:2506.00613v3](https://arxiv.org/abs/2506.00613v3)；[official repo@709665b](https://github.com/world-model-eval/world-model-eval/tree/709665b29f5c95124e7dbc05b0d4d47cd353de97)。
2. Zheng et al., [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, arXiv:2306.05685v4](https://arxiv.org/abs/2306.05685v4)；[FastChat judge@587d5cf](https://github.com/lm-sys/FastChat/tree/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge)。
3. Lee et al., [*Prometheus-Vision*, arXiv:2401.06591v1](https://arxiv.org/abs/2401.06591v1)；[official repo@fe668b5](https://github.com/kaistAI/prometheus-vision/tree/fe668b5e7e120e5bea8a3821eeb468ddf719c23c)。
4. Chen et al., [*MJ-Bench*, arXiv:2407.04842v1](https://arxiv.org/abs/2407.04842v1)。
5. scikit-learn, [`cohen_kappa_score@6d7f1f1`](https://github.com/scikit-learn/scikit-learn/blob/6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6/sklearn/metrics/_classification.py)；SciPy [`stats@v1.16.3`](https://github.com/scipy/scipy/tree/v1.16.3/scipy/stats)。
6. [EVAL-011 Proxy/Online Correlation](vol_05_eval011_offline_metric_online_success_correlation_source_freeze.html)、[EVAL-015 Reward/Scorer Hacking](vol_05_eval015_reward_scorer_hacking_adversarial_evaluation_source_freeze.html)、[WM-019 Metric Boundary](vol_04_wm019_metric_boundary_source_freeze.html)与[Benchmark Audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
7. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)与[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) inventories。
