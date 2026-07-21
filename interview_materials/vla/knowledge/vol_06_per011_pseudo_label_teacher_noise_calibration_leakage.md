# VOL 06 Perception / Grounding / Navigation：Pseudo-label、Teacher Noise、Confidence Calibration、Leakage 与 Curriculum（PER-011）

> 状态：`drafted / VLA-PER-011 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-009` matching/loss、`VLA-PER-010` metric/parser、VOL 02 imitation learning；后续：`VLA-PER-012` grounding methods、`VLA-PER-015` perception→action gate。  
> 来源入口：[PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Source Freeze](../sources/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html)。本页只做冻结证据的教学转译；atomic card已在独立切片同步并保持`unseen`，真实口述状态仍未开始。

## 问题（Question）

面试官问“你们用teacher做pseudo-label，怎么保证标签可靠、没有数据泄漏”时，不能只回答“设0.95阈值并做了去重”。需要讲清楚：teacher在什么输入和decode协议下产生hard/soft target；confidence是什么单位；是否在独立有标签validation上校准；threshold后的coverage、accepted error和class/route bias怎样变化；每轮teacher/student怎样版本化；row、image、fingerprint、semantic、teacher-training和model-selection leakage分别怎样检查。

本节点建立的主链是：

```text
candidate provenance
  -> teacher checkpoint + inference protocol
  -> typed hard / soft target
  -> confidence + calibration revision
  -> accept / reject / reweight
  -> coverage + accepted risk + distribution shift
  -> curriculum / iteration manifest
  -> leakage gates
  -> same-protocol student evaluation
  -> project truth boundary
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-011负责 |
| --- | --- | --- |
| VOL 02 IL | behavior cloning、DAgger、covariate shift | perception teacher生成的数据与可靠性合同 |
| PER-006 | image resize/crop、camera/time lineage | lineage怎样写入pseudo record与split gate |
| PER-009 | top-1 CE、full-vocabulary KL、mask与reduction | target由谁产生、为何可信、怎样筛选和迭代 |
| PER-010 | strict parser、metric、denominator、protocol comparability | calibration split、accepted-set quality与leakage层级 |
| PER-012 | 具体grounding/VLM方法谱系 | teacher/data机制，不展开模型百科 |
| PER-015 | uncertainty到reachability/action/robot gate | 不从static pseudo-label或holdout分数推出robot success |
| VOL 05 | 通用CI、paired test、评估工程 | selective risk、teacher lineage和pseudo-feedback leakage |

## 1. 30秒直觉：Pseudo-label是一条有血缘的记录，不是一列Label

一个可靠的30秒回答是：

> 我先把pseudo-label定义成带sample/image fingerprint、teacher checkpoint、prompt/decode、target type、confidence语义、calibration revision、acceptance decision和round的typed record。高confidence只是teacher自认为确定，不等于正确；所以threshold必须和coverage、独立gold audit上的accepted error以及class/route分布一起报告。temperature scaling只在独立有标签validation上拟合，不能把generation temperature或entropy logging叫校准。泄漏也分row、image、content、semantic、teacher training和model selection多层，任一身份未知都应fail closed。

这段回答主动封住四种常见偷换：

1. “teacher输出”被默认等同于gold；
2. “0.95 confidence”被默认等同于95%正确率；
3. “path overlap为0”被默认等同于完全无泄漏；
4. “超参随step变化”被默认等同于有效curriculum。

## 2. Typed Pseudo-label Record：可重放是可靠性的前提

### 2.1 最小Schema

```json
{
  "sample_id": "...",
  "source_id": "...",
  "image_id": "...",
  "content_fingerprint": "sha256:...",
  "split": "train_unlabeled | calibration | validation | holdout",
  "teacher_revision": "checkpoint-sha256:...",
  "teacher_training_manifest": "manifest-sha256:...",
  "prompt_revision": "sha256:...",
  "decode_mode": "teacher_forced | free_generation",
  "target_type": "hard_token | soft_distribution | point | box | text",
  "target": "...",
  "confidence_type": "max_probability | margin | sequence_probability | none",
  "raw_confidence": null,
  "calibration_revision": null,
  "acceptance": {"decision": "accept | reject", "threshold": null, "weight": 1.0},
  "route": "object | region | both | general",
  "round": 0
}
```

工程直觉是：任何会改变target、选择集合或风险解释的字段，都必须成为artifact identity的一部分。只缓存label ID而不缓存teacher和confidence，会导致后续无法回答“哪个teacher在什么阈值下接收了多少样本”。

### 2.2 三个不可混淆的轴

| 轴 | 选项A | 选项B | 为什么不同 |
| --- | --- | --- | --- |
| inference | teacher-forced | free generation | 前者看到gold response prefix/位置；后者自行生成完整结构，exposure与格式失败不同 |
| target | hard argmax | soft distribution | hard target丢弃非top-1概率，无法恢复teacher uncertainty |
| score state | raw confidence | calibrated confidence | 后者还绑定有标签fit split、方法、参数和revision |

对grounding还要区分token correctness、sequence exactness、strict parser validity和parsed geometry correctness。单token概率高，不代表整个point/box sequence格式正确或几何正确。

## 3. Teacher Target 与Noise Taxonomy

设teacher logits为\(z_T(x)\)，温度为\(T>0\)，soft target写为：

\[
q_T^{(T)}(c\mid x)
=\operatorname{softmax}\!\left(\frac{z_T(x)}{T}\right)_c,
\qquad
\tilde y=\arg\max_c q_T(c\mid x).
\]

变量解释：\(x\)是输入，\(c\)是token/class，\(q_T^{(T)}\)是温度化分布，\(\tilde y\)是hard target。直觉上，soft target保留teacher对其他类别的相对判断，hard target只留下冠军。实现映射：PER-011 source显示本地top-1 cache只保存argmax IDs；online trainer才计算full-vocabulary KL，二者不能被统称为同一种pseudo-label。

| Noise层 | 典型失败 | 最小诊断 | 该诊断不能证明 |
| --- | --- | --- | --- |
| semantic | 指错对象、关系判断错 | labeled gold accuracy、accepted precision | robot可执行性 |
| representation | point/box/text不足以下游使用 | representation-specific gold | action reachability |
| format/parser | tag缺失、坐标越界、空结构 | strict validity与invalid reasons | 语义正确 |
| exposure | teacher-forced依赖gold prefix | paired free-generation eval | 所有domain shift |
| domain | 新相机、场景或语言分布外 | per-domain risk–coverage | 未观测OOD |
| class/route | easy/common类被过度接收 | accepted histogram与per-group risk | 分布已公平 |
| correlated | teacher/student共享系统性错误 | gold audit、diverse teachers | 完全独立错误 |
| temporal | 旧cache被新round误消费 | round/checkpoint manifest | 内容无泄漏 |

## 4. Hard、Soft、Teacher-forced 与Free-generation怎样选

| 方案 | 保留信息 | 优点 | 主要风险 | 需要记录 |
| --- | --- | --- | --- | --- |
| hard token | argmax ID | 存储与训练简单 | 丢失uncertainty，错误被当one-hot | teacher、位置、mask、ID、confidence |
| soft token | vocabulary distribution | 可表达相似类别与暗知识 | 存储/计算高，temperature敏感 | logits/probs、T、vocab、mask |
| teacher-forced cache | gold response位置的teacher target | 与监督token对齐稳定 | exposure bias；不是自由生成 | prefix/labels、supervised positions |
| free-generation structure | teacher自己生成point/box/text | 更接近部署输出 | 格式/sequence error与decode随机性 | prompt、decode、raw output、parser |

选择原则不是“soft永远优于hard”，而是目标与风险对齐：若要蒸馏token分布，可用soft KL；若要构建可部署的结构化pseudo dataset，必须自由生成、保存raw output并走strict parser。二者可以共同存在，但应是不同artifact和metric。

## 5. FixMatch式Confidence Gate：Threshold只定义选择

### 5.1 Hard Pseudo-label与Mask

令\(x_i^w,x_i^s\)分别为同一无标签样本的weak和strong view，teacher在weak view上产生hard target：

\[
\tilde y_i=\arg\max_c p_T(c\mid x_i^w),
\qquad
m_i=\mathbf 1\!\left[\max_c p_T(c\mid x_i^w)\ge\tau\right].
\]

变量解释：\(\tau\)是threshold，\(m_i\)是accept mask。直觉上，模型只学习teacher最有把握的样本。实现映射：冻结FixMatch代码对weak logits取argmax与max probability，再用默认0.95阈值形成mask；但代码没有承诺0.95的样本就有95%正确率。

### 5.2 Masked Loss与Reduction Trap

\[
L_u=\frac{1}{B}\sum_{i=1}^{B}m_i\,
\operatorname{CE}\!\left(p_S(\cdot\mid x_i^s),\tilde y_i\right),
\qquad
\rho_\tau=\frac{1}{B}\sum_{i=1}^{B}m_i.
\]

变量解释：\(B\)是全部unlabeled batch size，\(L_u\)是pseudo loss，\(\rho_\tau\)是coverage。直觉上，FixMatch实现的`mean(loss * mask)`仍除以总batch，而不是accepted count；coverage下降会同时缩小有效loss scale。实现映射：复现时必须同时冻结threshold、pseudo-loss weight、batch组成和reduction。

确定性反例：confidence为\([0.96,0.94]\)，\(\tau=0.95\)，per-sample CE为\([0.2,0.8]\)。mask是\([1,0]\)，total-batch mean为0.1，而accepted-only mean为0.2。只说“用了masked CE”不足以复现objective。

## 6. Quality Contract：Coverage、Accepted Error与Risk–Coverage

### 6.1 两个最小量

\[
\operatorname{coverage}(\tau)=\Pr(m=1),
\qquad
\eta_\tau=\Pr(\tilde y\ne y\mid m=1).
\]

变量解释：coverage是候选池中被接收的比例，\(\eta_\tau\)是accepted-set error，需要独立gold labels。直觉上，threshold解决的是“收多少”，gold audit才回答“收进来的有多错”。实现映射：没有gold audit时可以报告score分布与coverage，但不能报告accepted precision或声称teacher可靠。

### 6.2 为什么高Threshold仍可能错

若teacher对错误class给0.99，\(\tau=0.95\)和0.98都会接收它。threshold只能截断teacher自己的score，无法修复overconfidence、domain shift或系统性偏差。

最低报告表应包含：

| Threshold | Candidate N | Accepted N | Coverage | Gold-audit N | Accepted error | Strict validity | Class/route drift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.90 | … | … | … | … | … | … | … |
| 0.95 | … | … | … | … | … | … | … |
| 0.99 | … | … | … | … | … | … | … |

对grounding还要分token/sequence/parser/geometry risk；只用token-level max probability做threshold，不能直接代表结构化输出risk。

## 7. Confidence Calibration：Score怎样变成可解释概率

### 7.1 Temperature Scaling

固定模型参数，在独立有标签calibration set \(\mathcal V\)上拟合标量\(T>0\)：

\[
T^*=\arg\min_{T>0}\sum_{i\in\mathcal V}
-\log \operatorname{softmax}\!\left(\frac{z_i}{T}\right)_{y_i}.
\]

变量解释：\(z_i\)是样本logits，\(y_i\)是真实label，\(T^*\)是validation NLL最优温度。直觉上，它不改argmax class，而是调整分布尖锐程度，使score更接近经验正确率。实现映射：必须保存fit split、logits/checkpoint、optimizer或搜索方法和\(T^*\)；generation `temperature/top_p`控制采样，不是这条校准过程。

### 7.2 ECE有完整协议

把样本按confidence分到bins \(B_b\)，top-label Expected Calibration Error写为：

\[
\operatorname{ECE}=\sum_{b=1}^{M}\frac{|B_b|}{N}
\left|\operatorname{acc}(B_b)-\operatorname{conf}(B_b)\right|.
\]

变量解释：\(M\)是bin数，\(N\)是样本数，acc/conf是每个bin的经验准确率与平均confidence。直觉上，它测量“说有多确定”与“实际多常正确”的差距。实现映射：需冻结bin edges、equal-width/equal-mass、top-label/classwise、sample unit和correctness定义；TorchMetrics的top-label分类实现不能自动定义VLA sequence或point/box正确性。

四样本\((0.55,0),(0.60,1),(0.85,1),(0.90,0)\)分成两bin时，ECE为0.225；改变binning数值会改变。因此ECE只能在同一协议下比较，并应和risk–coverage一起看。

### 7.3 Calibration Set不能被回收进训练

若用于拟合\(T\)或threshold的labels又进入student train，之后还把同一split当独立评估，就产生data reuse。建议把`calibration`、`model_selection_validation`和`sealed_holdout`作为不同ACL角色；任何角色转换都要生成新protocol revision。

## 8. Selection Bias与Route/Class Balance

设\(g\)表示class、route、source或domain，threshold后的训练分布为：

\[
p_\tau(x,y,g)=p(x,y,g\mid m=1)
\propto p(m=1\mid x,y,g)\,p(x,y,g).
\]

变量解释：\(p(m=1\mid x,y,g)\)是某组样本被接收的概率。直觉上，如果common object比rare relation更容易拿高confidence，accepted set会越来越偏向easy/common，而不是原candidate pool的随机子集。实现映射：每次filter后都要保存candidate/accepted/rejected的route、class、source、domain histogram和per-group risk。

常见修正与边界：

| 手段 | 解决什么 | 新风险 |
| --- | --- | --- |
| per-group threshold | 不同组score尺度不同 | 需要每组gold calibration；小组方差高 |
| quota / balancing | 避免rare group被清空 | 可能保留低质量样本 |
| reliability weight | 让低可靠target贡献更小 | 权重本身也要校准 |
| active relabeling | 把困难样本交给human/gold | 成本与抽样偏差 |
| diverse teacher agreement | 降低单teacher偶然错误 | teacher错误可能相关 |

平衡predicted class不等于平衡真实class，更不等于平衡场景难度或route；必须以gold audit和downstream结果复核。

## 9. Noisy Student：Filter、Balance与Iteration都是协议

冻结Noisy Student代码所表达的最小循环是：

```text
labeled data -> train teacher_r
candidate unlabeled -> teacher_r inference -> pseudo_manifest_r
pseudo_manifest_r -> threshold filter + class/route balance
labeled + accepted pseudo -> noisy student_r
student_r same-protocol eval -> promote or reject -> teacher_(r+1)
```

每轮需要版本化：

| Manifest字段 | 防止的问题 |
| --- | --- |
| round与teacher checkpoint | 旧cache被新round误消费 |
| candidate manifest/hash | 候选池悄悄变化 |
| prompt/decode/inference revision | target变化无法解释 |
| calibration与threshold | acceptance policy不可重放 |
| accepted/rejected counts | 有效数据量不透明 |
| route/class/source histogram | selection bias被掩盖 |
| student config/checkpoint | teacher晋升身份不清 |
| evaluation protocol与decision | 用不同口径晋升teacher |

teacher晋升不能只看training loss；应预注册same-protocol validation metric、risk–coverage和failure gates。若换了split、parser、prompt或checkpoint pool，不能把分数差称为单因素teacher迭代收益。

## 10. Curriculum：不是所有Schedule都叫课程学习

一个可验证curriculum至少包含：

1. **ordering signal**：confidence、difficulty、agreement、round或human audit；
2. **schedule**：何时放宽threshold、加入新domain/route或更新teacher；
3. **intervention**：样本以什么顺序和权重进入哪个objective；
4. **counterfactual**：random order、fixed threshold或fixed teacher基线；
5. **promotion gate**：什么证据允许进入下一轮。

示例manifest：

```json
{
  "round": 2,
  "teacher_revision": "sha256:...",
  "calibration_revision": "sha256:...",
  "thresholds": {"object": 0.97, "region": 0.93},
  "accepted_by_route": {"object": 21000, "region": 18000, "both": 3000},
  "gold_audit": {"n": 800, "accepted_error": 0.06},
  "student_revision": "sha256:...",
  "evaluation_protocol": "sha256:...",
  "promotion_decision": "accept"
}
```

本地`veto_beta`随step线性变化，只证明detached student logits混入teacher logits的比例变化。没有easy-to-hard样本顺序、gold-calibrated ordering和fixed-β对照时，安全名称是`target-logit mixing schedule`，不能直接叫“校准curriculum已验证有效”。

## 11. Leakage Taxonomy：从同一Row到Teacher上游数据

### 11.1 十层检查

| 层级 | 典型污染 | 最低Gate | 仍然未知 |
| --- | --- | --- | --- |
| row | 同一JSON row重复 | canonical row hash | 文本改写 |
| source | holdout source混入train | source ACL/blocklist | 跨source复制 |
| image path/ID | 同一路径或ID跨split | normalized key join | alias path、重编码 |
| content fingerprint | 相同bytes/内容重复 | byte/normalized-image SHA | crop、resize、近重复 |
| perceptual duplicate | 不同bytes的近似图 | pHash/embedding NN audit | threshold误差 |
| semantic | 同场景、模板或语义泄漏 | entity/template/cluster audit | 难以穷尽的同源关系 |
| teacher training | teacher上游见过holdout | dataset/checkpoint lineage | 黑盒预训练数据 |
| preprocessing | split前用全数据拟合统计量 | train-only fit manifest | processor隐藏状态 |
| model selection | 反复看test挑模型/阈值 | validation + sealed test | 人工观察后的隐性决策 |
| pseudo feedback | holdout prediction进入下一轮train | immutable ACL与artifact lineage | 缓存/人工复制 |

### 11.2 Alias-path反例

`sourceA/images/001.jpg`和`sourceB/copied/cup.jpg`若内容相同，`hash(source + path)`不同，可能进入不同split；content hash或perceptual fingerprint才会暴露它。因此“image-path overlap=0”只能证明同一个key没重复，不能证明无内容泄漏。

### 11.3 Fail-closed原则

以下任一情况应拒绝生成或消费pseudo-label：

- split未知或sample命中holdout ACL；
- 缺content fingerprint；
- teacher checkpoint/training lineage未知；
- calibration split与train/holdout角色冲突；
- cache round和teacher revision不匹配；
- duplicate check失败或检查程序没有成功退出。

目录名含`high_quality`或`no_eval_holdout`只是字符串，不是审计证据。证据必须是manifest、join结果、hash、脚本revision与退出状态。

## 12. Fail-closed Pipeline与伪代码

```python
def build_pseudo_manifest(candidate, teacher, calibration, acl, policy):
    # 1. Freeze all identities before inference; unknown lineage is a hard failure.
    assert candidate.manifest_sha256
    assert teacher.checkpoint_sha256 and teacher.training_manifest_sha256
    assert calibration.fit_split == "calibration"
    assert calibration.fit_split not in {"train_unlabeled", "holdout"}

    accepted, rejected, seen = [], [], set()
    for sample in candidate.rows:
        # 2. Enforce sample- and content-level holdout isolation.
        assert sample.sample_id not in acl.holdout_sample_ids
        assert sample.content_fingerprint not in acl.holdout_fingerprints
        assert sample.content_fingerprint not in seen
        seen.add(sample.content_fingerprint)

        # 3. Generate under a frozen prompt/decode protocol and keep raw output.
        pred = teacher.infer(sample, protocol=policy.inference_protocol)

        # 4. Transform raw score with a validation-fitted calibration revision.
        conf = calibration.transform(pred.raw_confidence)
        threshold = policy.threshold[(sample.route, sample.source_id)]
        record = typed_record(sample, teacher, pred, conf, calibration, policy)

        # 5. Reject invalid structure before confidence selection.
        if not pred.strict_valid:
            record.reject_reason = "strict_invalid"
            rejected.append(record)
        elif conf < threshold:
            record.reject_reason = "below_threshold"
            rejected.append(record)
        else:
            accepted.append(record)

    # 6. Report coverage, gold-audited risk and distribution shift, then freeze hashes.
    report_coverage_risk_balance(accepted, rejected, policy.gold_audit)
    return freeze_manifest(accepted, rejected, teacher, calibration, acl, policy)
```

实现审查顺序应固定为：identity/ACL → raw generation → strict validity → calibration → threshold → balance → gold audit → immutable manifest。若先filter后丢弃raw output，就无法区分teacher语义错、格式错和parser错。

## 13. 本地OPD：四条链必须分开口述

### 13.1 Mix Builder：人工Route，不是Confidence Gate

`build_opd_mix_v1.py`按source/bucket指定`teacher=obj/reg/both`，目标比例35% object、35% region、30% general，样本不足时回采。它没有读取teacher confidence、entropy或calibration，也没有在该层做fingerprint dedup。

安全表述：

> 这一层做的是数据配比和teacher route assignment，不是基于校准置信度的pseudo-label筛选。目录名里的high-quality/no-holdout需要另用manifest和重叠检查验证。

### 13.2 Top-1 Cache：Teacher-forced Token Distillation

`prepare_opd_top1_cache.py`让teacher进入`eval()`和`inference_mode()`，在真实assistant response的supervised token positions上取logits argmax，保存`obj_top1_ids/reg_top1_ids`及count。

```text
image + prompt + gold response positions
  -> teacher-forced token logits
  -> per-position argmax IDs
  -> cached hard distillation targets
```

它不是`image + prompt -> teacher自由生成point/box -> parser`。cache也没有confidence、margin、entropy、temperature、threshold或accept/reject字段，因此不能事后重算coverage与accepted error。

### 13.3 Top-1 Trainer：固定Route权重

`train_opd_top1_vl.py`直接消费缓存IDs；`both` route固定0.5/0.5。它支持“hard teacher targets进入训练”的代码事实，不支持“target经过校准过滤”或“权重反映teacher可靠性”。hard CE公式属于PER-009，本页只解释target quality evidence。

### 13.4 Online KL / Veto：Logging不是Quality Gate

`train_opd_online_vl.py`冻结teacher、使用`eval()`、可选teacher/student rollout并计算full-vocabulary KL；teacher entropy与top-k overlap被记录，但未据此拒绝或降权target。sampling temperature/top-p控制rollout采样，不是calibration。

若target logits为：

\[
z'=z_T+\beta z_S^{\operatorname{detach}},
\]

变量解释：\(z_T\)是teacher logits，\(z_S^{\operatorname{detach}}\)是不回传梯度的student logits，\(\beta\)是`veto_beta`。改变\(\beta\)会改变soft target，但没有gold \(y\)就不能判断它更正确。实现映射：安全名称是target-logit mixing，不是confidence calibration或已验证curriculum。

## 14. 本地Raw Holdout：强证据与剩余未知

`eval_raw_holdout_v1/summary.json`报告：10,000 rows、8,251 unique images、10,000 unique fingerprints、reported fingerprint duplicate=0；10,000 rows均`image_seen_in_train=false`，blocklist覆盖source keys、fingerprints和713,545 train images。

| 可以说 | 不能说 |
| --- | --- |
| 当前summary对应manifest通过了记录中的row/image/fingerprint可见gate | teacher checkpoint从未见过相同上游数据 |
| blocklist和fingerprint检查是比路径名更强的证据 | semantic/near-duplicate完全为零 |
| static holdout支持格式/几何诊断 | static grounding等同robot success |
| 可见train-image overlap被报告为false | test从未参与prompt/parser/checkpoint选择 |

安全结论应分层写：`row/source/image/fingerprint checked`；`near-duplicate/semantic/teacher lineage unknown`；`model-selection process not sealed`。不能压成一个`no_leakage=true`。

## 15. 诊断Playbook：Student没提升时先查哪里

| 症状 | 首查证据 | 常见根因 | 下一Probe |
| --- | --- | --- | --- |
| accepted N突然下降 | threshold、calibration revision、score histogram | 温度/teacher/domain变化 | 固定candidate做paired score diff |
| overall涨、rare route跌 | accepted-by-route、per-group risk | selection bias | per-route threshold/quota matched A/B |
| train loss低、free generation差 | teacher-forced vs free mode | exposure/format error | 同checkpoint paired free-generation eval |
| confidence高但gold错 | reliability bins、risk–coverage | overconfidence/OOD | labeled audit + temperature scaling |
| 新round结果不可复现 | teacher/cache/manifest hash | revision混用 | fail round identity check |
| holdout异常高 | overlap、teacher lineage、selection log | content/semantic/model-selection leakage | near-dup audit + sealed rerun |
| entropy下降但效果不升 | gold risk与strict validity | score更尖锐而非更正确 | paired correctness/calibration audit |
| veto schedule有变化无收益 | β日志、fixed-β baseline | target mixing无有效机制 | matched ablation |

推荐诊断顺序：先检查identity和split，再检查target mode与strict validity，然后检查calibration/risk–coverage，最后才讨论student architecture或优化器。数据身份不稳定时，调模型无法产生可信因果结论。

## 16. 面试回答模板、追问与危险答案

### 16.1 两分钟结构化回答

> 我把teacher supervision拆成生成、选择、训练和评估四段。生成段冻结teacher checkpoint、prompt/decode和teacher-forced/free-generation模式，并保存typed target和raw output。选择段不把confidence当正确率，而是在独立有标签calibration set上拟合temperature，按threshold报告coverage、accepted error和class/route分布；FixMatch式masked loss还要说明分母是总batch。迭代段记录每轮teacher、candidate、filter/balance、student和promotion manifest。泄漏段分别检查row、source、image/path、content/near-duplicate、semantic、teacher training和model selection。对本地OPD，我只能说有人工route mix、teacher-forced top-1 token cache、online KL/veto和10k holdout gate；cache没有confidence，entropy只是logging，所以不能说伪标签已校准，也不能从static holdout推出robot成功率。

### 16.2 高频追问

1. 为什么0.95 confidence不代表95%正确率？
2. FixMatch的masked loss到底除accepted count还是总batch？
3. temperature scaling和generation temperature有什么区别？
4. ECE为什么不能脱离binning、sample unit和correctness定义？
5. sequence/point/box pseudo-label的confidence怎么定义？
6. threshold升高为什么可能让long-tail更差？
7. class balance为什么不等于真实分布无偏？
8. Noisy Student每轮必须冻结哪些identity？
9. 什么条件下一个schedule才配称curriculum？
10. path overlap=0为什么仍可能image leakage？
11. teacher预训练污染和student split污染怎样区分？
12. 为什么本地top-1 cache不是自由生成pseudo-label dataset？
13. entropy下降为何不能证明校准变好？
14. 10k holdout当前证明了哪几层、没证明哪几层？

### 16.3 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “0.95以上就是高质量标签” | confidence≠correctness | 报coverage、gold accepted error与分层risk |
| “调temperature做了校准” | 可能只是sampling temperature | 说明独立validation拟合\(T\)与held-out检验 |
| “entropy越来越低，teacher更准” | 可能只是更尖锐/过度自信 | 配对gold accuracy与calibration |
| “image path不重叠，所以没泄漏” | alias/content/semantic仍可能重叠 | 加content/perceptual/semantic audit |
| “top-1 cache是teacher生成标签” | 隐藏teacher-forced exposure | 说清监督token位置argmax |
| “veto beta是curriculum” | 只有schedule，没有ordering/baseline/effect | 称target-logit mixing schedule |
| “holdout无重复，结果绝对可信” | teacher/model-selection污染未封 | 分层陈述checked与unknown |
| “静态grounding提升就能上机器人” | perception→action gate缺失 | 留给PER-015和closed-loop证据 |

## 17. Project Truth Boundary与项目Hook

| 证据层 | 当前可以说 | 当前不能说 | 补强动作 |
| --- | --- | --- | --- |
| public mechanism | FixMatch threshold/mask；Noisy Student filter/balance/iteration；calibration与curriculum合同 | 已在OPD等价复现并有效 | 配置、日志与matched result |
| local code | mix route、path-hash split、top-1 cache、hard trainer、online KL/veto存在 | 全部由候选人原创/亲自实现 | git blame/PR/周报/本人确认 |
| target semantics | cache是teacher-forced token argmax | 自由生成point/box pseudo dataset | raw generation + parser manifest |
| confidence | online记录entropy/top-k overlap | 已做gating/calibration | labeled calibration、\(T^*\)、risk–coverage |
| leakage | 10k summary报告image/fingerprint gate | semantic/teacher/model-selection完全无污染 | near-dup、teacher lineage、sealed test |
| outcome | static raw holdout summary存在 | pseudo-label因果提升或robot success | exact raw/checkpoint、ablation、robot trials |

### 17.1 OPD Hook

OPD是本节点的主要项目hook，但答案必须按“公开机制→本地代码事实→缺失证据”三层展开。最有区分度的点不是声称teacher pipeline先进，而是准确发现：top-1 cache缺confidence字段、teacher-forced与free-generation不同、online entropy没有成为selection gate、visible leakage gate仍留teacher lineage未知。

### 17.2 Robot Harness Hook

Robot Harness只能作为下游消费与安全门提醒：即使static perception pseudo-label可靠，仍需PER-015的reachability、uncertainty、controller和closed-loop failure gate。本节点没有证据把OPD holdout结果映射成robot成功率。

## 18. 白板Checklist与练习标准

面试前能在白板上独立写出：

- typed pseudo-label record的十个关键identity；
- hard/soft与teacher-forced/free-generation四象限；
- threshold mask、masked loss、coverage和accepted error公式；
- temperature scaling与ECE，并说明sample unit/binning；
- selection后的条件分布与route/class drift；
- Noisy Student round manifest和promotion gate；
- curriculum的ordering/schedule/intervention/baseline；
- 十层leakage taxonomy和alias-path反例；
- 本地OPD四条链及每条claim boundary；
- 一段两分钟回答和至少六个追问。

本页`drafted`不等于掌握。只有候选人真实口述、追问、纠错并记录状态后，题卡才可从`unseen`推进；本轮不创建`coaching_state.md`。

## 19. 结论与下一步

Pseudo-label系统的核心不是选一个threshold，而是建立可重放的teacher/data/selection/iteration身份，并用独立gold证据测量risk–coverage。Calibration解决score解释，balance处理selection distribution，curriculum规定有对照的呈现顺序，leakage gate保护评估独立性；四者不能互相替代。

本地OPD当前最准确的结论是：存在人工route mix、teacher-forced top-1 token cache、hard-target/online KL训练代码与10k raw holdout的可见image/fingerprint gate；但尚无confidence-aware cache、独立calibration、accepted-set gold audit、teacher lineage、sealed model selection或robot结果。

下一bounded slice只冻结`VLA-PER-012` segmentation/depth/keypoint/affordance source；不生成knowledge/card，不创建`coaching_state.md`，不改变任何既有mastery。

## References

1. [PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Source Freeze](../sources/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html)：固定论文、官方代码、本地OPD脚本、SHA、deterministic probes与truth boundary。
2. Sohn et al., [FixMatch v2](https://arxiv.org/abs/2001.07685v2)；[official implementation@d4985a1](https://github.com/google-research/fixmatch/tree/d4985a158065947dba803e626ee9a6721709c570)。
3. Xie et al., [Noisy Student v4](https://arxiv.org/abs/1911.04252v4)；[official implementation@aac52bf](https://github.com/google-research/noisystudent/tree/aac52bf02448f6e45aee6c418f3e588803e4fa43)。
4. Guo et al., [On Calibration of Modern Neural Networks v2](https://arxiv.org/abs/1706.04599v2)。
5. [TorchMetrics Calibration Error@37a8080](https://github.com/Lightning-AI/torchmetrics/blob/37a808094850aa1e05bc6e9fcf63fae86dfd01ce/src/torchmetrics/classification/calibration_error.py)。
6. Bengio et al., [Curriculum Learning](https://icml.cc/Conferences/2009/papers/119.pdf)，ICML 2009。
7. Kapoor & Narayanan, [Leakage and the Reproducibility Crisis in ML-based Science v1](https://arxiv.org/abs/2207.07048v1)。
8. [PER-009 Grounding Matching / Negative / Loss](vol_06_per009_grounding_matching_negative_loss.html) 与 [PER-010 Grounding Metric / Parser / Protocol](vol_06_per010_grounding_metric_parser_protocol.html)。
9. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：本地mix/cache/train/eval事实与ownership/robot边界。
