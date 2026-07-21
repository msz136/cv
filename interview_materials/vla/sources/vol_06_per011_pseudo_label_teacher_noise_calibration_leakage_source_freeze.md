# VOL 06 PER-011 Source Freeze：Pseudo-label / Teacher Noise、Confidence Calibration、Leakage 与 Curriculum

> 状态：`source_frozen / VLA-PER-011 / primary_official_checked / local_opd_mix_cache_online_holdout_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结teacher target可靠性、confidence/calibration、selection bias、iteration curriculum与leakage gate；不生成knowledge/card，不重讲PER-009的top-1 CE/full-vocabulary KL，也不把static perception结果升级为PER-015的action/robot结论。

## 问题（Question）

使用teacher给无标注样本生成pseudo-label时，hard/soft target、confidence threshold、temperature calibration、class/route balancing和迭代curriculum应如何定义？teacher noise怎样进入accepted-set误差？row、image、fingerprint、semantic、teacher-training和model-selection leakage如何分层排查？本地OPD的mix、top-1 cache、online KL与raw holdout到底支持哪些项目结论？

本页冻结的可审计链为：

```text
unlabeled sample provenance
  -> teacher checkpoint + inference protocol
  -> hard / soft pseudo target
  -> confidence + calibration state
  -> accept / reject / reweight policy
  -> accepted-set noise + class/route selection bias
  -> curriculum / iteration manifest
  -> student objective
  -> row/source/image/fingerprint/semantic leakage gates
  -> same-protocol evaluation
  -> project claim boundary
```

## 1. 结论先行

1. **Pseudo-label不是一个裸标签，而是一条带血缘的typed record**：至少要保存sample/image identity、teacher revision、prompt/decode、target type、confidence语义、acceptance policy、round和split membership；否则无法重放、校准或排查污染。
2. **High confidence不等于high correctness**：threshold只选择teacher自认为确定的样本；若teacher过度自信、域外或类偏，τ=0.95仍可接收错误target。需要带gold的独立validation估计reliability、accepted precision与coverage。
3. **Calibration与sampling temperature不是一回事**：temperature scaling是在独立validation labels上拟合logit temperature，再用同一任务定义检验；generation temperature/top-p控制采样，不自动校准teacher probability。
4. **Threshold必须和coverage、accepted error及分布漂移一起报告**：提高τ通常降低覆盖率，但未必单调降低所有class/route/domain的错误；只报“用了0.95”没有质量含义。
5. **FixMatch式masked loss按总unlabeled batch求mean**：accepted count变化同时改变有效loss scale；它不是对accepted samples重新归一化。reduction、pseudo-loss weight与coverage必须共同进入协议。
6. **Noisy Student是有身份的迭代合同**：teacher推理、filter/balance、带噪student训练、student晋升下一轮teacher；每一轮都应冻结teacher/student revision、threshold、accepted count与class/route distribution。
7. **Curriculum不等于任何随step变化的超参**：需要明确排序信号、呈现顺序、schedule、基线和预期机制。本地`veto_beta`线性变化只证明target logits的混合系数变化，不能直接称为已验证的confidence curriculum。
8. **Leakage不是单个boolean**：row/source/image/path/fingerprint/content/semantic、teacher pretraining、checkpoint selection与test-time tuning是不同层级；path hash split只能挡住同路径重叠，挡不住alias path或内容重复。
9. **本地top-1 cache是teacher-forced token distillation cache**：teacher在真实assistant response的监督token位置取argmax，并非自由生成point/box pseudo-label dataset；cache没有confidence/entropy字段，不能事后重算threshold coverage或accepted error。
10. **本地证据支持“有mix/cache/train/eval机制和静态holdout gate”，不支持“伪标签已校准”“无任何语义污染”“OPD使robot成功率提升”或候选人ownership**。这些结论必须分别补validation、content dedup、checkpoint lineage、ablation和个人证据。

## 2. Primary / official / local source ledger

论文SHA对固定版本PDF bytes计算；GitHub文本按固定commit的UTF-8/LF bytes冻结；本地脚本与JSON按原始bytes。repository license只约束相应source code，不自动覆盖paper、dataset、checkpoint或第三方asset。

| 来源 | 类型 / revision / license | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [FixMatch paper v2](https://arxiv.org/abs/2001.07685v2) | primary；2020-11-25 v2；PDF读取2026-07-20 | `6CD643401271C6F4946A9B982C670C2B65B486842EB974ABD1DEDCCA704DCB88` | weak-view hard pseudo-label、confidence threshold与strong-view consistency框架 | 任意VLA teacher已校准或0.95必然可靠 |
| [FixMatch implementation](https://github.com/google-research/fixmatch/blob/d4985a158065947dba803e626ee9a6721709c570/fixmatch.py) | official-code；`d4985a...`；Apache-2.0 repo | `5AB77199CC2C408A02CDEA5FFA093474E7A488723FE210018306BB114B36948F` | weak-view argmax、max-prob mask、strong-view CE、默认confidence 0.95与masked batch mean | threshold precision、VLA sequence token semantics |
| [FixMatch pseudo-label baseline](https://github.com/google-research/fixmatch/blob/d4985a158065947dba803e626ee9a6721709c570/pseudo_label.py) | official-code；同commit | `BB050CCFE3E8EFEB69C8AB35432033F83C66F4A53E272288947D24B5D08E9751` | hard pseudo-labeling实现桥接 | 本地OPD target生成方式 |
| [FixMatch README](https://github.com/google-research/fixmatch/blob/d4985a158065947dba803e626ee9a6721709c570/README.md) | official docs；同commit | `014B1A33E1FFFFE70BFEE2CA347A385872623BE92A5E82EFB5308F224A452C1E` | repo运行与数据命名上下文 | paper外的质量保证 |
| [FixMatch LICENSE](https://github.com/google-research/fixmatch/blob/d4985a158065947dba803e626ee9a6721709c570/LICENSE) | official license text；同commit | `3DDF9BE5C28FE27DAD143A5DC76EEA25222AD1DD68934A047064E56ED2FA40C5` | repository source code的Apache-2.0授权文本 | paper、dataset、checkpoint或第三方asset授权 |
| [Noisy Student paper v4](https://arxiv.org/abs/1911.04252v4) | primary；2020-06-19 v4；PDF读取2026-07-20 | `7D14856FC292AB6F9BFE84497E16526431B402CE7235C2AC5A82BE9B014B9A3A` | teacher→pseudo-label→noisy student→new teacher迭代框架 | 本地route balance或teacher正确率 |
| [Noisy Student label prediction](https://github.com/google-research/noisystudent/blob/aac52bf02448f6e45aee6c418f3e588803e4fa43/predict_label.py) | official-code；`aac52bf...`；Apache-2.0 repo | `1D5438A4F4FEC7D0764658AE6B93367C7432FEB44B671FDEB739FFC0596584B0` | teacher inference与pseudo-label产物桥接 | filter后分布自动无偏 |
| [Noisy Student filtering](https://github.com/google-research/noisystudent/blob/aac52bf02448f6e45aee6c418f3e588803e4fa43/filter_unlabel.py) | official-code；同commit | `14868361B19F5D2B7DE5EE79A7D5B872B9FCB2848CF82E667A7EB244CD38D24E` | predicted-class probability threshold与class balancing | threshold已校准或下游VLA route充分覆盖 |
| [Noisy Student training](https://github.com/google-research/noisystudent/blob/aac52bf02448f6e45aee6c418f3e588803e4fa43/main.py) | official-code；同commit | `DAF7C94E823CECFB188933DA59E27CA00FEC76BD16489FB35153739D446293CA` | student训练实现上下文 | 本地OPD objective等价性 |
| [Noisy Student README](https://github.com/google-research/noisystudent/blob/aac52bf02448f6e45aee6c418f3e588803e4fa43/README.md) | official docs；同commit | `5763F32A2AA3B835AD4A701FE8A6CB69C4E0D3DC3C615EE1762C2DD1D082472A` | repo workflow与artifact上下文 | 任意本地复现已经等价完成 |
| [Noisy Student LICENSE](https://github.com/google-research/noisystudent/blob/aac52bf02448f6e45aee6c418f3e588803e4fa43/LICENSE) | official license text；同commit | `6535845CA8C5703D99A7492941CFB6C94B52DF96AD8F2CEFB43EDEA899C44985` | repository source code的Apache-2.0授权文本 | paper、dataset、checkpoint或第三方asset授权 |
| [Calibration paper v2](https://arxiv.org/abs/1706.04599v2) | primary；2017-08-03 v2；PDF读取2026-07-20 | `CB654A65ACB785ED4387D6C2DB1301D065075DDDC2D363676836A2F2A14BC50D` | confidence calibration、reliability diagram、ECE与temperature scaling | 单个entropy值证明校准、无label validation拟合温度 |
| [TorchMetrics calibration error](https://github.com/Lightning-AI/torchmetrics/blob/37a808094850aa1e05bc6e9fcf63fae86dfd01ce/src/torchmetrics/classification/calibration_error.py) | implementation bridge；`37a8080...`；Apache-2.0 repo | `64980971BB4230F804DA3830AD5E8A97EBE5C86EFC2497D331AE3DAE13BDB4B1` | top-label calibration error、`n_bins`、L1 ECE/L2 RMSCE/max MCE | sequence-level、structured grounding或selective calibration自动定义 |
| [Curriculum Learning](https://icml.cc/Conferences/2009/papers/119.pdf) | primary；ICML 2009 PDF读取2026-07-20 | `BE4BD220A1FD82D979CF08FA90520787EAA2EC24745AB9A35E90054A8FEB9E7B` | easy-to-hard或有组织样本呈现的优化框架 | 任意线性schedule必然是有效curriculum |
| [Leakage and the Reproducibility Crisis in ML-based Science](https://arxiv.org/abs/2207.07048v1) | survey/taxonomy bridge；2022-07-14 v1；PDF读取2026-07-20 | `C433BCEDA841CA09FE2FD7DDF857FC0818FDF98553E62E54A37CC394C6F70C42` | train/test contamination、preprocessing与model-selection leakage分类 | 本地数据已经通过全部污染审计 |
| `muxi/point/build_opd_mix_v1.py` | local mix builder；`muxi@756e27e...`；selected path read | `D27EF9D59F33936CF91DB6C3CAC4DDAC09FE6416FC40DDF6B325360EDE810A3D` | source/bucket→teacher路由、35/35/30 mix与不足时回采 | high-quality/no-holdout命名真实性、confidence gate或fingerprint dedup |
| `muxi/point/build_expert_mixes_seed0.py` | local split builder；同commit | `60DFDF46FDAC8EB9DBBE38A13298D6D71819EB7AD13F6B0D00A86B87032EABD0` | `source + image/path`稳定hash的5% image-level split及每expert path-overlap检查 | 跨source alias、相同内容不同路径或semantic duplicate为零 |
| `muxi/point/prepare_opd_top1_cache.py` | local cache builder；同commit | `39494090DC1F98A238F223AC74D6687DDABF5E43C1BA47182EF3B8F3C9E88369` | eval/inference teacher在supervised token positions取argmax并缓存IDs/count | 自由生成pseudo-label、confidence、entropy、temperature或threshold |
| `muxi/point/train_opd_top1_vl.py` | local cached-target trainer；同commit | `66C53F80844D476D34F507315A5A829E58F10F44D9CFB4F44FC868817D4443EC` | 直接消费top-1 IDs；both route固定0.5/0.5 | confidence-gated、calibrated或teacher-quality-weighted训练 |
| `muxi/point/train_opd_online_vl.py` | local online distillation trainer；同commit | `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336` | frozen eval teacher、full-vocabulary KL、rollout选择、entropy/top-k overlap logging与`veto_beta` schedule | entropy gate、calibration、teacher correctness或holdout uplift证明 |
| `muxi/point/eval_raw_holdout_v1/summary.json` | local evaluation summary；同workspace bytes | `200F7A8B00CDD989D4E8D19B6CD3EB5B47B75B87799394438169702F8BBF6485` | 10,000 rows、8,251 unique images、10,000 unique fingerprints、reported duplicate=0与train-image blocklist gate | teacher pretraining/semantic/model-selection leakage为零 |
| [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | repository local evidence inventory | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | local revision、mix/cache/train/eval证据与truth boundary汇总 | 候选人ownership、closed-loop robot success或未归档artifact |
| [PER-009 Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | top-1 CE、full-vocabulary KL、mask/reduction与loss边界 | teacher target为何可信 |
| [PER-010 Source Freeze](vol_06_per010_grounding_metric_parser_protocol_source_freeze.html) | repository-reviewed bridge | review SHA见对应记录 | parser、metric、denominator与same-protocol comparability | pseudo-label selection或teacher calibration |

## 3. 与相邻节点的去重边界

| 节点 | 已负责 | PER-011只新增 |
| --- | --- | --- |
| VOL 02 IL | behavior cloning、DAgger、covariate shift与imitation基础 | teacher-generated perception target的可靠性与污染边界 |
| PER-006 | image resize/crop/letterbox与camera/time lineage | lineage字段如何进入pseudo-label record和split gate |
| PER-009 | hard top-1 CE、soft full-vocabulary KL、mask与reduction | target由谁产生、是否可信、如何选择与迭代 |
| PER-010 | strict parser、metric、denominator、protocol identity | validation/calibration、accepted-set quality与leakage层级 |
| PER-012 | Grounding/VLM具体方法谱系 | 本页只给teacher机制与数据合同，不展开模型百科 |
| PER-015 | perception uncertainty到action/reachability/robot gate | 不从static pseudo-label或holdout metric推出可执行性 |
| VOL 05 | 通用CI、paired test与评估工程 | pseudo-label selective risk、curriculum manifest和teacher-specific leakage |

## 4. Typed Pseudo-label Record：先冻结“谁在什么协议下教了什么”

最小record不能只有`input`和`label`：

```json
{
  "sample_id": "...",
  "source_id": "...",
  "image_id": "...",
  "image_path": "...",
  "content_fingerprint": "sha256:...",
  "split": "train_unlabeled | calibration | validation | holdout",
  "teacher_revision": "checkpoint-sha256:...",
  "teacher_training_manifest": "manifest-sha256:...",
  "prompt_revision": "sha256:...",
  "decode": {"mode": "teacher_forced | free_generation", "temperature": 0.0},
  "target_type": "hard_token | soft_distribution | point | box | text",
  "target": "...",
  "confidence_type": "max_probability | sequence_probability | margin | none",
  "confidence": null,
  "calibration_revision": null,
  "acceptance_policy": {"threshold": null, "weight": 1.0, "reason": "unfiltered"},
  "route": "object | region | both | general",
  "round": 0
}
```

关键区分有三组：

1. `teacher_forced`与`free_generation`不同：前者在给定gold prefix/response位置读取teacher分布，后者让teacher自己生成整个结构；exposure、格式失败和sequence confidence都不同。
2. `hard_token`与`soft_distribution`不同：前者只保留argmax ID，后者保留完整或压缩分布；前者无法恢复teacher uncertainty。
3. `confidence`与`calibration_revision`不同：一个是原始score，一个是用哪组有label validation、什么方法与参数把score映射到经验正确率。

## 5. Teacher Target Taxonomy 与 Noise 来源

对输入(x)，teacher logits为(z_T(x))，soft target可写为：

\[
q_T^{(T)}(c\mid x)=\operatorname{softmax}\!\left(\frac{z_T(x)}{T}\right)_c,
\]

hard target为(	ilde y=\arg\max_c q_T(c\mid x))。结构化输出还需要区分token-level、sequence-level和parsed-object-leveltarget：一个sequence可能token confidence高，却因坐标tag、数值或几何关系而整体错误。

Teacher noise至少分为：

| Noise层 | 例子 | 可观测信号 | 不能被该信号排除 |
| --- | --- | --- | --- |
| label/semantic | 指错对象、关系误判 | labeled validation accuracy、accepted precision | calibration好但任务本身accuracy低 |
| representation | point/box/text不满足下游需求 | representation-specific gold与parser | action feasibility |
| format/parser | tag缺失、坐标越界、多个答案 | strict validity、invalid reasons | 语义正确性 |
| exposure | teacher-forced时依赖gold prefix | free-generation paired eval | 所有domain shift |
| domain | 新场景/相机/语言分布外 | domain-stratified risk与coverage | 未观测OOD |
| class/route | easy/common类别被过度接收 | accepted distribution、per-stratum risk | 隐藏属性偏差 |
| correlated | teacher与student共享pretraining错误 | diverse teacher/gold audit | 真正独立错误 |
| temporal | 旧teacher生成的cache被新代码消费 | round/revision manifest | 数据内容污染 |

## 6. FixMatch Confidence Gate：选择规则不等于质量证明

FixMatch式hard pseudo-labeling可写为：

\[
\tilde y_i=\arg\max_c p_T(c\mid x_i^w),\qquad
m_i=\mathbf 1\!\left[\max_c p_T(c\mid x_i^w)\ge\tau\right],
\]

\[
L_u=\frac{1}{B}\sum_{i=1}^{B}m_i\,
\operatorname{CE}\!\left(p_S(\cdot\mid x_i^s),\tilde y_i\right),
\qquad
\rho_\tau=\frac{1}{B}\sum_{i=1}^{B}m_i.
\]

变量解释：(x^w,x^s)分别为weak/strong view，τ是confidence threshold，(m_i)是accept mask，(B)是全部unlabeled batch size，ρ是coverage。固定实现的核心语义是`mean(loss * mask)`，分母仍是(B)，不是(sum_i m_i)。因此两次实验即便accepted样本的平均CE相同，只要coverage不同，(L_u)的scale也会变化。

应同时报告：

\[
\eta_\tau=\Pr(\tilde y\ne y\mid m=1),\qquad
\operatorname{coverage}_\tau=\Pr(m=1),
\]

以及每个class、route、source、domain的(eta_{τ,g})和coverage。没有一组独立gold audit，就只能报告score分布与coverage，不能声称accepted precision。

### 6.1 两样本reduction probe

confidence为([0.96,0.94])，τ=0.95，per-sample CE为([0.2,0.8])：mask是([1,0])。FixMatch-style batch mean为((0.2+0)/2=0.1)，accepted-only mean为(0.2/1=0.2)。两者差一倍，说明“masked CE”若不写reduction就不是完整协议。

### 6.2 过度自信错误probe

若teacher对错误class给0.99，则τ从0.95升至0.98仍会接收它。threshold只表达teacher score排序与截断，无法单独证明correctness；错误是否下降必须由同任务、同单位、同分层的gold validation估计。

## 7. Noisy Student：迭代、过滤与平衡都属于协议

冻结repo所表达的最小循环是：

```text
labeled data -> train teacher_r
unlabeled data -> teacher_r inference -> pseudo manifest_r
pseudo manifest_r -> probability filtering + class balancing
labeled + accepted pseudo -> noisy student_r training
student_r evaluation -> promote as teacher_(r+1) or reject
```

每轮至少冻结：

| 字段 | 为什么必要 |
| --- | --- |
| `round_id` | 防止旧cache与新teacher混用 |
| teacher checkpoint/hash | 确定target生成者 |
| unlabeled manifest/hash | 确定候选池与去重结果 |
| inference protocol/hash | prompt、view、decode和batch都可能改target |
| filter threshold | 决定coverage与selective risk |
| accepted/rejected counts | 暴露有效数据量 |
| class/route/source histogram | 暴露selection bias |
| student config/hash | 确定noise、objective和capacity |
| evaluation protocol/hash | 决定是否允许晋升 |

`filter_unlabel.py`中的predicted-class probability threshold与class balancing说明过滤不是预处理尾声，而是学习分布的一部分。对VLA/grounding还应按route、representation、scene和language bucket检查；只平衡predicted class可能仍丢失稀有关系、困难视角或失败case。

## 8. Confidence、Calibration 与 Selective Risk

### 8.1 Temperature scaling合同

Temperature scaling通常固定model参数，只在独立、有label的validation set上拟合标量(T>0)：

\[
T^*=\arg\min_{T>0}\sum_{i\in\mathcal V}
-\log \operatorname{softmax}\!\left(\frac{z_i}{T}\right)_{y_i}.
\]

然后在未用于拟合(T)的evaluation split上检查calibration与selective risk。它不改变argmax class，但会改变max probability、threshold acceptance与soft-target温度；所以`calibration_revision`和threshold必须共同版本化。

Generation `temperature`/`top_p`用于从token分布采样，改变输出随机性；若没有独立gold validation优化与检验，不得把它称为temperature calibration。

### 8.2 ECE是带定义的估计量

把样本按confidence分到bins (B_b)，top-label ECE为：

\[
\operatorname{ECE}=\sum_{b=1}^{M}\frac{|B_b|}{N}
\left|\operatorname{acc}(B_b)-\operatorname{conf}(B_b)\right|.
\]

必须同时写明：bin edges/数量、equal-width或equal-mass、top-label或classwise、sample unit、structured prediction correctness定义、空bin处理与split。TorchMetrics固定实现提供`n_bins`和L1/L2/max三类norm，但这只是分类桥接；VLA token、sequence、point/box correctness需要另行定义。

### 8.3 ECE binning probe

四个样本confidence/正确性为((0.55,0),(0.60,1),(0.85,1),(0.90,0))。若分成([0.5,0.75),[0.75,1])两bin：第一binacc=0.5、conf=0.575，第二binacc=0.5、conf=0.875，ECE=(0.5\times0.075+0.5\times0.375=0.225)。若改变bin边界或使用每样本bin，数值会改变；所以ECE不可脱离binning合同横比。

### 8.4 应优先画risk–coverage而非只报ECE

对pseudo-label selection，面试中更直接的问题是“在接收多少样本时，错误率是多少”。建议对τ sweep记录：overall与stratified coverage、accepted error、strict validity、class/route distribution、student downstream metric。ECE可以辅助解释score，但不能取代risk–coverage曲线。

## 9. Selection Bias：高阈值会改训练分布

设候选分布为(p(x,y,g))，其中(g)是class/route/source；accept事件(m=1)后实际训练分布变为：

\[
p_\tau(x,y,g)=p(x,y,g\mid m=1)
\propto p(m=1\mid x,y,g)\,p(x,y,g).
\]

只要accept概率依赖难度、类别、视角或domain，accepted set就不是原unlabeled pool的无偏子集。常见failure包括：

- common object和短答案被过度接收，rare relation被清空；
- object teacher比region teacher更尖锐，固定τ导致route比例漂移；
- teacher在近域相机上confidence高，跨相机样本被拒绝；
- 只保留top confidence使student重复teacher已会的easy cases；
- 按predicted class balance仍会保留系统性错标。

处理手段包括per-group threshold、quota、importance/reliability weighting、gold-audited hard-negative pool与active relabeling；任何方法都必须同时报告coverage和accepted error，不能只把histogram“调平”。

## 10. Curriculum / Iteration Contract

Curriculum至少需要四件事：

1. **ordering signal**：teacher confidence、difficulty、agreement、round或human audit；
2. **schedule**：何时放宽threshold、增加domain/route、更新teacher；
3. **learning intervention**：哪些样本以什么权重进入哪个objective；
4. **counterfactual baseline**：random order、fixed threshold、fixed teacher或无curriculum。

推荐manifest：

```json
{
  "round": 2,
  "teacher_revision": "sha256:...",
  "calibration_revision": "sha256:...",
  "candidate_manifest": "sha256:...",
  "thresholds": {"object": 0.97, "region": 0.93},
  "accepted_count": 42000,
  "accepted_by_route": {"object": 21000, "region": 18000, "both": 3000},
  "gold_audit": {"n": 800, "accepted_error": 0.06},
  "student_revision": "sha256:...",
  "evaluation_protocol": "sha256:...",
  "promotion_decision": "accept | reject"
}
```

本地online脚本中的`veto_beta`若从(β_0)线性变化到(β_1)，只说明detached student logits混入teacher target logits的比例发生变化。它没有独立validation-fitted confidence mapping，也没有easy-to-hard样本顺序或fixed-β对照；安全名称是`target-logit mixing schedule`，不是“已验证的confidence calibration/curriculum”。

## 11. Leakage Taxonomy 与分层Gate

| 层级 | 典型污染 | 最低gate | 残余边界 |
| --- | --- | --- | --- |
| row | 同一JSON row重复 | canonical row hash | 文本改写或字段顺序变化 |
| source | holdout source被混入train | source allow/block list | 跨source复制 |
| image path/ID | 同一路径或ID跨split | normalized path/ID join | alias path、重编码 |
| content fingerprint | 相同bytes/标准化内容重复 | byte SHA、normalized image hash | crop、resize、近重复 |
| perceptual/near duplicate | 相似画面不同bytes | pHash/embedding/nearest-neighbor audit | threshold与false positive |
| semantic | 同场景/问答模板或标注语义泄漏 | cluster/entity/template audit | 难以穷尽的语义同源 |
| teacher training | teacher预训练/微调见过holdout | dataset/checkpoint lineage | 上游黑盒数据不可知 |
| preprocessing | 全数据统计或词表在split前拟合 | train-only fit manifest | 第三方processor隐藏状态 |
| model selection | test反复选checkpoint/threshold | sealed validation + one-shot test | 人工观察test后的决策 |
| pseudo-label feedback | holdout prediction进入下一轮train | immutable split ACL + artifact lineage | 手工复制或缓存混用 |

应把gate写成fail-closed：未知split、无fingerprint、teacher lineage缺失或holdout ID命中时，不生成/不消费pseudo-label。`no_eval_holdout`路径名只是字符串，不是gate证据；需要manifest、join结果、hash和退出码。

### 11.1 Alias-path probe

若`sourceA/images/001.jpg`与`sourceB/copied/cup.jpg`内容相同，`hash(source + image_path)`不同，可分别进入train/eval；内容SHA或perceptual fingerprint才会暴露它。因此“image-path overlap=0”只能证明同一规范化键未重复，不能证明无图像内容泄漏。

### 11.2 Teacher-training与model-selection边界

即使当前student train/eval在row、image和fingerprint上完全分离，teacher可能已在上游训练中见过同一数据；反复查看holdout summary并选择checkpoint、threshold或parser也会产生model-selection leakage。没有teacher data lineage或sealed test流程时，结论应写成“在当前可见manifest的这些层级未发现重叠”，不能写“完全无泄漏”。

## 12. 本地OPD Mix：人工Teacher路由，不是置信度筛选

`build_opd_mix_v1.py`按source/bucket人工指定`teacher=obj/reg/both`，目标比例为35% object、35% region、30% general；样本不足时会回采。这个阶段没有读取teacher confidence、entropy、校准参数或label-quality audit，也没有content fingerprint dedup。

因此安全描述是：

> 我们构建了按来源与任务桶路由的混合数据，并给样本指定object/region/both teacher消费路径；这是数据配比与route assignment，不是基于校准置信度的pseudo-label过滤。目录名含`high_quality`或`no_eval_holdout`只作为provenance线索，必须另用manifest与重叠检查验证。

不能描述为“我们只用了高置信伪标签”“35/35/30由质量最优搜索得到”或“脚本保证了eval完全隔离”。

## 13. 本地Top-1 Cache：Teacher-forced Token Distillation

`prepare_opd_top1_cache.py`把teacher设为`eval()`并在`inference_mode()`下运行；在真实assistant response的supervised token positions上读取teacher logits并取argmax，保存`obj_top1_ids`、`reg_top1_ids`及token count。

这条链不是：

```text
image + prompt -> teacher free generation -> parsed point/box pseudo-label
```

而是：

```text
image + prompt + gold response prefix/positions
  -> teacher-forced logits at supervised tokens
  -> per-token argmax IDs
  -> cached distillation targets
```

cache没有max probability、margin、entropy、temperature、threshold、accepted/rejected状态或calibration revision。因此无法从现有cache回答：某个token为何被接收、τ=0.95时coverage多少、accepted error多少、sequence-level置信度是否可靠。

`train_opd_top1_vl.py`直接消费这些IDs；`both` route使用固定0.5/0.5权重，没有confidence gate、校准或按teacher可靠性加权。PER-009负责解释它怎样进入hard CE；本页只判定target可靠性证据缺口。

## 14. 本地Online KL / Veto：可记录不等于可筛选

`train_opd_online_vl.py`冻结teacher参数，使用`eval()`，可选择teacher或student rollout，默认student rollout，并对full vocabulary计算KL。teacher entropy与top-k overlap被记录，但当前没有：

- 根据entropy/confidence拒绝或降权target；
- 用有label validation拟合temperature；
- teacher correctness或accepted error gate；
- 同协议holdout uplift作为teacher/student promotion条件。

sampling的temperature/top-p只控制rollout采样，不是probability calibration。`veto_beta`把detached student logits按schedule混入teacher logits；它改变target分布，但不能从“β随step变化”推出confidence已经校准或curriculum有效。

### 14.1 Veto schedule probe

固定teacher logits (z_T)和detached student logits (z_S)，若target logits形如(z'=z_T+βz_S)，改变β会改变softmax target；但没有gold (y)就无法判断新分布更接近真实标签，也无法得到reliability mapping。它是target construction intervention，不是calibration proof。

## 15. Raw Holdout：强可见Gate与剩余未知

`eval_raw_holdout_v1/summary.json`记录：

- 10,000 rows；
- 8,251 unique images；
- 10,000 unique fingerprints，reported duplicate count为0；
- 10,000 rows的`image_seen_in_train=false`；
- blocklist包含source keys、fingerprints与713,545 train images。

这是当前本地最强的row/fingerprint/image可见证据，支持“该summary对应的10,000-row manifest通过了这些明确gate”。但它仍不证明：

1. teacher checkpoint从未在pretraining/fine-tuning中见过相同或近重复内容；
2. 相同语义、模板、scene或重编码图片不存在；
3. holdout从未被用于checkpoint、parser、threshold或prompt选择；
4. summary对应raw predictions、exact checkpoint hash、generation config均已在本仓库归档；
5. static holdout metric等同于robot closed-loop success。

报告时应按层写：`row/source/image/fingerprint checked`、`near-duplicate/semantic/teacher-lineage unknown`、`model-selection process not sealed`，而不是压成一个`no_leakage=true`。

## 16. Deterministic Probes 与最小测试集

| Probe | 固定输入 | 预期结果 | 防止的错误结论 |
| --- | --- | --- | --- |
| threshold/reduction | conf=[.96,.94]，τ=.95，CE=[.2,.8] | mask=[1,0]；batch mean=.1；accepted mean=.2 | masked loss分母被误读 |
| overconfidence | 错误class conf=.99 | τ=.95仍接收 | confidence=correctness |
| ECE bins | 四样本、两bin | ECE=.225；换bin可变 | ECE脱离binning横比 |
| cache schema | top1 IDs/count、无score字段 | threshold coverage/error不可重建 | cache=calibrated pseudo dataset |
| alias leakage | 相同content、不同source/path | path key不同，content hash相同 | path split=无内容泄漏 |
| veto schedule | 固定(z_T,z_S)，改变β | target logits/prob变化，correctness未知 | schedule=calibration/curriculum proof |

建议golden tests覆盖：empty candidate pool、exact-threshold equality、NaN/Inf confidence、route缺失、teacher revision不匹配、calibration split误入train、same content/different path、holdout ID命中、round cache错配与accepted count为0时的reduction。

## 17. Fail-closed Pseudocode

```python
def build_pseudo_manifest(candidate, teacher, calibration, split_acl, policy):
    assert candidate.manifest_sha256
    assert teacher.checkpoint_sha256 and teacher.training_manifest_sha256
    assert calibration.fit_split == "calibration"
    assert calibration.fit_split not in {"train_unlabeled", "holdout"}

    seen = set()
    accepted, rejected = [], []
    for sample in candidate.rows:
        assert sample.sample_id not in split_acl.holdout_sample_ids
        assert sample.content_fingerprint not in split_acl.holdout_fingerprints
        assert sample.content_fingerprint not in seen
        seen.add(sample.content_fingerprint)

        pred = teacher.infer(sample, protocol=policy.inference_protocol)
        conf = calibration.transform(pred.raw_confidence)
        group = (sample.route, sample.source_id)
        threshold = policy.threshold[group]
        record = typed_record(sample, teacher, pred, conf, calibration, policy)

        if not pred.strict_valid:
            record.reject_reason = "strict_invalid"
            rejected.append(record)
        elif conf < threshold:
            record.reject_reason = "below_threshold"
            rejected.append(record)
        else:
            accepted.append(record)

    report_coverage_risk_balance(accepted, rejected, policy.gold_audit)
    freeze_hashes(accepted, rejected, teacher, calibration, split_acl, policy)
    return accepted
```

真实系统还要定义sequence/structured confidence、per-route threshold、calibration failure fallback、near-duplicate search、atomic write与multi-worker determinism；伪代码的重点是缺少identity或split证据时立即失败，而不是默默继续。

## 18. 面试中的项目Truth Boundary

| 证据层 | 现在可以说 | 现在不能说 | 补强动作 |
| --- | --- | --- | --- |
| public mechanism | FixMatch/Noisy Student的threshold、filter、balance、iteration；calibration/ECE/curriculum定义 | 公共方法已在OPD复现并有效 | 保存实验配置、日志与paired结果 |
| local code fact | mix route、top-1 cache、hard target trainer、online KL/veto、hash split存在 | 都由候选人设计或完整实现 | git blame/PR/周报/主管确认 |
| target semantics | cache是teacher-forced supervised-token argmax | 自由生成point/box伪标签集 | 归档free-generation manifest与parser |
| confidence | online记录entropy/top-k overlap | 已做confidence gating/calibration | labeled calibration split、T拟合、risk–coverage |
| leakage | summary报告10k fingerprint unique、train-image gate | teacher/semantic/model-selection完全无污染 | teacher lineage、near-dup audit、sealed test |
| evaluation | 有static raw holdout summary与parser诊断 | robot closed-loop或因果提升 | exact checkpoint/raw outputs、ablation、robot trials |

推荐口述：

> 我会先把pseudo-label当作带teacher、decode、confidence和split血缘的版本化记录，而不是一列label。公开方法里，FixMatch说明threshold加masked consistency，Noisy Student说明filter/balance和teacher迭代；但confidence本身不是正确率，temperature calibration必须在独立有标签validation上拟合并看risk–coverage。本地OPD目前更准确地说是teacher-forced token target与online distillation：top-1 cache没有confidence字段，online entropy也只是logging，没有quality gate。我们有10k raw holdout的image/fingerprint可见检查，但teacher pretraining、semantic近重复和model-selection污染仍是未知。因此我只陈述现有代码与静态证据，若要声称伪标签可靠和有效，还要补校准集、accepted-error分层、exact checkpoint/raw outputs、fixed-teacher/fixed-threshold ablation与sealed evaluation。

## 19. Source Gate 与下一Slice

本页达到source-freeze的条件：

- FixMatch、Noisy Student、calibration、curriculum与leakage来源均固定版本、链接与SHA；
- typed record、hard/soft target、confidence/calibration、coverage/error、selection/curriculum与leakage taxonomy均有明确合同；
- 本地mix、split、top-1 cache、hard-target trainer、online KL/veto与10k holdout逐文件映射；
- deterministic probes明确reduction、overconfidence、ECE binning、cache缺字段、alias leakage和veto边界；
- project claim、robot claim与ownership缺口保持分离。

仍为`WARN`，因为本地尚无独立calibration labels/T参数、accepted-set gold audit、confidence-aware cache、near-duplicate/semantic audit、teacher training lineage、sealed model-selection日志、exact raw predictions/checkpoint hashes或closed-loop robot result。

`VLA-PER-001..011` source/knowledge/card已在独立bounded slices同步，262张题卡全部`unseen`。下一bounded slice只冻结`VLA-PER-012` segmentation/depth/keypoint/affordance source；不生成knowledge/card，不创建`coaching_state.md`，不改变mastery。

## 20. References

1. [FixMatch v2](https://arxiv.org/abs/2001.07685v2) 与 [official implementation@d4985a1](https://github.com/google-research/fixmatch/tree/d4985a158065947dba803e626ee9a6721709c570)。
2. [Noisy Student v4](https://arxiv.org/abs/1911.04252v4) 与 [official implementation@aac52bf](https://github.com/google-research/noisystudent/tree/aac52bf02448f6e45aee6c418f3e588803e4fa43)。
3. Guo et al., [On Calibration of Modern Neural Networks v2](https://arxiv.org/abs/1706.04599v2)。
4. [TorchMetrics calibration error@37a8080](https://github.com/Lightning-AI/torchmetrics/blob/37a808094850aa1e05bc6e9fcf63fae86dfd01ce/src/torchmetrics/classification/calibration_error.py)。
5. Bengio et al., [Curriculum Learning](https://icml.cc/Conferences/2009/papers/119.pdf)，ICML 2009。注意：`arXiv:0909.5166`不是该论文，不作为本页来源。
6. Kapoor & Narayanan, [Leakage and the Reproducibility Crisis in ML-based Science v1](https://arxiv.org/abs/2207.07048v1)，作为leakage taxonomy bridge。
7. 本地`muxi@756e27e16adcfb3ccbfe98c2920dda42095b127f`中列出的mix/cache/train/eval脚本与 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
8. 本仓库 [PER-009 Source Freeze](vol_06_per009_grounding_matching_negative_loss_source_freeze.html) 与 [PER-010 Source Freeze](vol_06_per010_grounding_metric_parser_protocol_source_freeze.html)。
