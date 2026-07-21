# VLA Engineering / Evaluation：VLM / Human Proxy 一致性与偏差

> 节点：`VLA-EVAL-016`  
> 状态：`drafted / knowledge_38_of_44 / card_1_of_1_unseen / WARN`  
> 更新日期：2026-07-19  
> 学习目标：能设计VLM judge与人工/objective predicate的成对验证，区分raw agreement、kappa、rank和calibration，识别位置、风格、视觉、时序、任务slice与prompt-injection偏差，并守住WorldGym/五项目证据边界。

## 1. 一页结论

```text
freeze task + rubric + evidence shown
  -> blind human double labels + adjudication
  -> versioned VLM raw votes/responses
  -> confusion + kappa + rank + calibration
  -> position/visual/temporal/adversarial paired probes
  -> cluster uncertainty + abstention + state/human veto
```

面试先强调：

1. correlation、agreement、classification和calibration不是同一个问题；
2. human label也有噪声，需blind double-label、保留raw disagreement和独立adjudication；
3. 五次同模型投票不是五个独立专家，必须保存raw votes和API/prompt/parser版本；
4. VLM只能在验证过的task/evidence slice做筛选proxy，不能直接替代simulator/real success或安全predicate。

## 2. 先定义评分任务

| 任务 | 输出 | 主指标 |
| --- | --- | --- |
| binary success | fail/success | confusion、sensitivity/specificity、kappa |
| ordinal completion | 0/0.5/1、Likert | weighted kappa、MAE、within-one |
| pairwise | A/B/tie | pair accuracy、swap consistency、tie |
| policy ranking | policy/checkpoint序 | Spearman/Kendall、top-k regret |
| success probability | `P(success)` | Brier、reliability、ECE、coverage-risk |
| failure type | perception/action/contact/... | per-class confusion、macro-F1 |

必须冻结instruction、success/partial/failure predicate、rubric、reference、camera/frame sampling、duration、temporal order、state overlay和language。如果human看完整video+state而VLM只看稀疏frames，差异包含observability gap，不能全部归因judge能力。

## 3. Human Protocol

human不是自动正确的gold。最低合同：

- rubric写成可执行条件，而非“整体看起来成功”；
- annotator先做calibration examples并记录expertise；
- 隐藏policy/checkpoint/provider身份，A/B顺序随机；
- 每个高风险case至少两名独立标注者；
- raw labels、confidence、reason、time全部保留；
- disagreement由第三方按同rubric adjudicate；
- adjudicated label不能覆盖原始human-human disagreement；
- 记录batch/order/fatigue、语言和实际看到的evidence。

human-human agreement反映任务含糊和rubric上限，却不是VLM的通用合格线。若接触、力、碰撞或真实终局无法从视频看到，应引入simulator state、controller event或effect sink，不让human/VLM一起共错。

## 4. Raw Agreement、Confusion 与 Kappa

\[
p_o=\frac{1}{N}\sum_i\mathbb{1}[v_i=h_i],
\qquad
p_e=\sum_c p_v(c)p_h(c),
\qquad
\kappa=\frac{p_o-p_e}{1-p_e}.
\]

变量解释：`p_o`是raw agreement，`p_e`是由两侧边际类别率推导的chance agreement。直觉：90%样本失败时，恒猜失败已有90% agreement；kappa会扣除这种基线。实现映射：保存完整confusion、prevalence、accuracy、success sensitivity、failure specificity、balanced accuracy、kappa和cluster CI。[1]

kappa仍受prevalence和marginal分布影响，不能机械套阈值。critical safety/success minority recall必须单独报；overall kappa高不能抵消rare contact/safety漏判。

## 5. Ordinal / Partial Completion

0/0.5/1或Likert是有序label：

\[
\kappa_w=1-
\frac{\sum_{a,b}w_{ab}O_{ab}}
{\sum_{a,b}w_{ab}E_{ab}}.
\]

变量解释：`O/E`是观察/期望计数，`w_ab`是事前冻结的disagreement cost。直觉：把partial错成success通常比错成failure更接近，但安全任务可能反过来需要非线性代价。实现映射：同时报告exact、within-one、MAE、linear/quadratic weighted kappa和per-class confusion；权重不能看完结果再挑。[1]

MJ-Bench公开实验说明multimodal judge在不同评价维度表现不同，VLM在Likert自然语言反馈上可能比纯数值scale更稳定。[2] 这不表示Likert天然正确，仍要对robot rubric做人标校准。

## 6. Pairwise、Position 与 Tie

\[
A_{\mathrm{pair}}=
\frac{1}{N}\sum_i\mathbb{1}[j_i^{\mathrm{VLM}}=j_i^{\mathrm{human}}],
\qquad j_i\in\{A,B,\mathrm{tie}\}.
\]

变量解释：tie是正式类别或由冻结margin产生。实现映射：同一pair运行`A,B`和`B,A`，报告human agreement、swap consistency、first-position win rate、tie rate和confusion。

MT-Bench研究公开展示position、verbosity、self-enhancement和reasoning bias。[3] 在VLM里还要随机camera/frame order和model identity。若换序后winner翻转，不能用一次pairwise vote选policy。

## 7. Correlation / Ranking 不等于 Agreement

\[
\rho_s=\operatorname{Spearman}
\left(\{q_j^{\mathrm{VLM}}\}_{j=1}^{J},
\{q_j^{\mathrm{human/real}}\}_{j=1}^{J}\right).
\]

变量解释：`j`是独立policy/checkpoint，不能把同一video的五次judge call当五个点。直觉：VLM若总高估20%，rank可对但absolute success错。实现映射：在相同task/init support下得到多个policy点，报Spearman/Kendall、top-k regret、per-policy uncertainty和task/policy cluster bootstrap。[1][4]

WorldGym论文在其policy/support上报告world-model proxy与real success的高相关和relative ranking保持。[5] 这只支持对应实验，不证明任意WorldGym checkpoint、GPT-4o版本、任务或个人WAM；`J=1`也不能建立rank关系。

## 8. Calibration、Vote 与 Abstention

若judge给`p_i=P(success)`：

\[
\operatorname{Brier}=\frac{1}{N}\sum_i(p_i-y_i)^2.
\]

变量解释：`y_i`是adjudicated/objective outcome。实现映射：画reliability、ECE/Brier、coverage-risk；对unparseable、vote tie、high entropy或judge disagreement显式abstain，报告coverage与selective risk。

五次同一VLM同一prompt采样只表示sampling variation。WorldGym代码调用literal `gpt-4o`、`n=5`，解析0/0.5/1，并在平票时优先`1 > 0.5 > 0`；模型snapshot未冻结。[5] 应保存每次raw response、parsed/invalid、vote histogram、retry/cache/API metadata。majority score不能替代human-human或VLM-human agreement。

## 9. Bias Matrix

| bias | paired probe | 重点读数 |
| --- | --- | --- |
| position | A/B swap、criteria顺序 | winner flip、first-position win |
| verbosity/style | 加长解释、专业语气、自信措辞 | state不变时score drift |
| identity/self | 隐去/替换model/provider名 | identity-conditioned preference |
| rubric/prompt | paraphrase、anchor/criteria order | decision stability |
| visual quality | blur/compress/brightness/artifact | quality-vs-success confusion |
| temporal | sampling、reverse、丢终局、先成后毁 | temporal shortcut |
| camera/view | wrist/third、crop、遮挡 | per-view sensitivity |
| task/prevalence | contact、partial、long-horizon、rare safety | minority recall/kappa |
| adversarial | overlay text、judge instruction injection | attack success |
| language | instruction/rubric翻译 | cross-language agreement |

\[
\Delta_g=M_g-M_{\mathrm{reference}}.
\]

变量解释：`M`必须是同一metric，例如success sensitivity或kappa。实现映射：优先paired mutation，按episode/task/policy cluster给CI，报告worst target slice；不让大量easy/visible case掩盖contact/safety盲区。

## 10. Rubric 与维度分解

Prometheus-Vision展示了custom rubric、reference answer和image grounding的VLM evaluator形式，并在公开数据上报告human correlation。[6] 正确借鉴是把robot criteria拆清，而非直接迁移其相关性。

一个robot video rubric至少分：

- goal completion / partial completion；
- object/robot state与终局保持；
- trajectory efficiency与重复动作；
- collision、forbidden effect和human intervention；
- evidence visibility与judge abstention reason。

MJ-Bench显示alignment、safety、image quality与bias维度的judge相对优劣不同。[2] 因此不能只报一个overall VLM score；每个维度要有人标/状态predicate、混淆和slice。

## 11. Matched Protocol

1. 预注册label/rubric、primary metric、critical slice和可接受margin；
2. 按episode/task/policy分层抽样，近重复视频group split；
3. human blind double-label、保存raw disagreement并独立adjudicate；
4. VLM冻结provider/snapshot、prompt、frame sampler、n、temperature/seed、parser/retry/cache；
5. human/VLM看到相同evidence，或显式设置video-only、video+state information arms；
6. 同一raw bundle跑全部judge与position/visual/temporal/adversarial mutations；
7. frame/vote/annotator是嵌套重复，不是独立episode；按episode/task/policy cluster resample；
8. 同报human-human、VLM-human、confusion/kappa、rank、calibration、bias和abstention；
9. release保留objective state/human critical veto；
10. judge升级对旧raw bundlebridge rescore，fresh holdout防调参泄漏。

## 12. Artifact Bundle

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

```python
def evaluate_vlm_judge(episodes, humans, judge, protocol):
    spec = freeze_rubric_sampling_judge_and_metrics(protocol)
    sample = group_stratified_locked_sample(episodes, spec)
    raw_human = humans.blind_double_label(sample, spec.rubric)
    adjudicated = independent_adjudication(raw_human, hide_model_identity=True)

    raw_vlm = judge.score(sample, spec, keep_all_votes=True)
    mutations = run_position_visual_temporal_and_injection_pairs(sample, judge, spec)

    return cluster_recompute_confusion_kappa_rank_calibration_bias_abstention(
        raw_human, adjudicated, raw_vlm, mutations,
        clusters=("episode", "policy", "task"),
    )
```

这是验证合同，不代表本地项目已执行。

## 13. 五项目面试边界

### WAM / Cosmos

可讲WorldGym公开机制，以及本地单episode三camera、300-step action/video diagnostic适合未来抽样。不能说本地跑过WorldGym/GPT-4o、人标一致性或proxy替代真实success。[5][7]

### UWM / OpenPiVLA

二者有environment/official rollout协议或summary，可作为未来objective predicate对照；当前没有VLM raw responses与blind human labels，不能报agreement、kappa或bias。

### OPD

point/box/text是deterministic static scorers，不是VLM video judge。可做人标geometry calibration，但当前没有paired human bundle。

### Robot Harness

schema-aware text/tool scorer可复用versioning、mutation和raw bundle思想；它不是VLM judge，也没有robot video-human agreement。

## 14. 追问防线

- **80% agreement够吗？** 不够；看prevalence、confusion、human-human、kappa、critical recall和CI。
- **Pearson高能替代人工吗？** 只能说明线性association；absolute threshold、bias和calibration可能错。
- **五票GPT-4o是五个专家吗？** 不是；同模型同prompt相关采样，只测sampling variation。
- **majority human就是gold吗？** 保存raw disagreement并adjudicate；video不可见状态仍需objective predicate。
- **position bias怎么测？** A/B与B/A成对，报告winner flip、first-position rate与tie。
- **生成视频很逼真是否更可靠？** 可能把画质当成功；需state/real paired validation。
- **什么时候可用VLM？** 在验证support内做triage/ranking，低置信abstain，critical decision保留human/state veto。
- **项目证据？** 只有公开WorldGym机制和本地可设计入口，没有个人agreement数字。

## 15. 本节点状态

EVAL-016知识与一张题卡保持`WARN/unseen`。五项目缺`episode/video × raw human labels × VLM responses × objective predicate`四方bundle。本节点不生成agreement数字。下一节点是`VLA-EVAL-017`：simulator success、shadow mode与真机gate；没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. scikit-learn, [`cohen_kappa_score@6d7f1f1`](https://github.com/scikit-learn/scikit-learn/blob/6d7f1f12c792bb17dd92b4bfbc86b9392e0f5ef6/sklearn/metrics/_classification.py)；SciPy [`stats@v1.16.3`](https://github.com/scipy/scipy/tree/v1.16.3/scipy/stats)。
2. Chen et al., [*MJ-Bench*, arXiv:2407.04842v1](https://arxiv.org/abs/2407.04842v1)。
3. Zheng et al., [*Judging LLM-as-a-Judge*, arXiv:2306.05685v4](https://arxiv.org/abs/2306.05685v4)与[FastChat judge](https://github.com/lm-sys/FastChat/tree/587d5cfa1609a43d192cedb8441cac3c17db105d/fastchat/llm_judge)。
4. [EVAL-011 Offline/Online Correlation](vol_05_engineering_eval_eval011_offline_online_correlation.html)。
5. Quevedo et al., [*WorldGym*, arXiv:2506.00613v3](https://arxiv.org/abs/2506.00613v3)；[official repo](https://github.com/world-model-eval/world-model-eval/tree/709665b29f5c95124e7dbc05b0d4d47cd353de97)。
6. Lee et al., [*Prometheus-Vision*, arXiv:2401.06591v1](https://arxiv.org/abs/2401.06591v1)。
7. [EVAL-016 Source Freeze](../sources/vol_05_eval016_vlm_human_proxy_agreement_bias_source_freeze.html)、[WAM](../evidence/projects/wam_claim_evidence_inventory.html)、[UWM/LIBERO](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html)、[OPD](../evidence/projects/opd_claim_evidence_inventory.html)与[Robot Harness](../evidence/projects/robot_harness_claim_evidence_inventory.html) inventories。
