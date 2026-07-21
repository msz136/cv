# VOL 06 Perception / Grounding / Navigation：PER-011 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-011`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Knowledge](../knowledge/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage.html)；来源边界见 [PER-011 Source Freeze](../sources/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html)。

## Pseudo-label、Teacher Noise、Calibration、Curriculum 与 Leakage

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-011</b> · 用teacher做pseudo-label时，confidence threshold、calibration、selection bias、curriculum和leakage怎么讲？本地OPD现在到底证明了什么？</summary>

**面试意图**：判断你能否把teacher target当作带血缘的数据artifact，区分confidence、correctness与calibration，解释threshold后的risk/coverage和分布偏移，并守住本地OPD teacher-forced cache、静态holdout与robot/ownership之间的真实性边界。

**30 秒回答**：我把伪标签绑定样本指纹、teacher版本、推理协议、target类型、置信度/校准、接收策略和轮次。置信度不等于正确率，阈值须同时报coverage、独立gold上的accepted error及route分布；校准温度只能在独立validation拟合。泄漏还要查内容、语义、teacher训练和模型选择。OPD cache无置信度，不能声称已校准筛选。

**机制展开（约 2 分钟）**：hard取argmax，soft保留分布；teacher-forced在真实response位置读logits，不等于自由生成。FixMatch以max-prob≥τ成mask且loss除总batch，故阈值须配risk–coverage、gold error和route drift。Temperature scaling在独立标注集拟合T，采样温度与entropy日志不是校准。Noisy Student每轮冻结teacher、候选池、filter/balance、student及晋升协议；curriculum还需排序、schedule和固定/随机对照。泄漏从row/path扩展到内容近重复、语义、teacher预训练及test调参，未知身份应fail closed。

**诊断 / 证据**：先diff candidate/teacher/prompt/decode/calibration/round manifest→核验teacher-forced或free-generation与raw output→strict validity→threshold前后score、coverage、accepted/rejected count→gold-audit error与reliability bins→class/route/source/domain drift→cache/checkpoint identity→row/source/path/content/perceptual/semantic overlap→teacher training lineage与sealed model-selection log。确定性probe应覆盖0.96/0.94在τ=.95的mask与总batch reduction、0.99错误仍被接收、ECE换bin变化、同内容不同path穿透split、无confidence cache不可重算coverage、改变veto-beta只改target而不证明correctness。

**项目挂钩**：`build_opd_mix_v1.py`只按source/bucket做35/35/30 mix和obj/reg/both route，不是confidence filter；`prepare_opd_top1_cache.py`在真实assistant supervised positions取teacher argmax，只存top-1 IDs/count；`train_opd_top1_vl.py`直接消费ID，both固定0.5/0.5；online脚本记录entropy/top-k overlap并做veto-beta target mixing，但没有gating或validation-fitted calibration。10k summary报告8,251 unique images、10k unique fingerprints和train-image blocklist，是可见image/fingerprint gate；仍缺near-duplicate/semantic、teacher lineage、sealed selection、exact raw/checkpoint与robot证据。

**追问树**：为什么0.95不代表95%正确？FixMatch masked loss除什么？accepted error没有gold能算吗？sampling temperature和temperature scaling有何区别？ECE为何绑定binning与sample unit？threshold升高为何伤long-tail？class balance为何仍可能错？Noisy Student每轮冻结哪些identity？什么schedule才叫curriculum？path overlap=0为何仍可能泄漏？teacher预训练污染如何查？top-1 cache为何不是自由生成pseudo dataset？entropy下降能否证明更准？static holdout能否推出robot success？

**易错点**：把confidence当correctness；只报threshold不报coverage/risk；accepted-only mean与总batch mean混用；用train或test拟合calibration；把generation temperature叫校准；只平衡predicted class；旧cache与新teacher混用；把线性超参称为curriculum；把path hash当content/semantic dedup；把静态holdout、代码存在或Git身份升级为因果、robot结果或个人ownership。

**危险答案**：说“0.95以上就是高质量伪标签”“entropy下降说明teacher更准”“调temperature就是做校准”“path不重叠所以绝无泄漏”“top-1 cache是teacher自由生成标签”“veto-beta schedule证明curriculum有效”“10k fingerprint唯一说明teacher没见过测试集”，或“我设计并验证了完整OPD伪标签系统”，却不提confidence字段、teacher lineage、gold audit、sealed selection和候选人逐文件确认缺失。

**来源**：[1][2][3][4][5][6][7]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-011 Pseudo-label / Teacher Noise / Calibration / Leakage Knowledge](../knowledge/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage.html)：typed record、risk–coverage、calibration、selection/curriculum、leakage taxonomy、诊断与项目边界。
2. [PER-011 Source Freeze](../sources/vol_06_per011_pseudo_label_teacher_noise_calibration_leakage_source_freeze.html)：固定论文/代码revision、SHA、本地OPD映射与deterministic probes。
3. [FixMatch v2](https://arxiv.org/abs/2001.07685v2) 与 [official implementation](https://github.com/google-research/fixmatch/tree/d4985a158065947dba803e626ee9a6721709c570)。
4. [Noisy Student v4](https://arxiv.org/abs/1911.04252v4) 与 [official implementation](https://github.com/google-research/noisystudent/tree/aac52bf02448f6e45aee6c418f3e588803e4fa43)。
5. Guo et al., [On Calibration of Modern Neural Networks v2](https://arxiv.org/abs/1706.04599v2)。
6. Bengio et al., [Curriculum Learning](https://icml.cc/Conferences/2009/papers/119.pdf)；Kapoor & Narayanan, [Leakage and the Reproducibility Crisis in ML-based Science v1](https://arxiv.org/abs/2207.07048v1)。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
