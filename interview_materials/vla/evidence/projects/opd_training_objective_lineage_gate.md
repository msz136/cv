# OPD Training Objective Lineage Gate：top1 CE、Full-Vocabulary KL 与 Rollout Source

> 状态：`local_code_reconciled / run_summary_bounded / checkpoint_unverified / WARN`
> 审计日期：2026-07-22
> 审计对象：OPD legacy 根目录 trainer、formal `point/` trainer、coldstart-500 与 OPD5000 launcher/run summary
> 核心问题：当前口述中的“student rollout + full-vocabulary KL”究竟由哪份实现支持？KL 的方向、veto target、token mask 和 run lineage是什么？

## 1. 结论先行

本地存在两份同名但目标不同的 trainer，不能用路径末尾的 `train_opd_online_vl.py` 把它们合并：

1. `C:\Users\mousongzhe\muxi\train_opd_online_vl.py` 是 **legacy teacher rollout + teacher top1 hard-label CE**。teacher 先生成 response，再在该 response 上 forward，取 `argmax` 作为 token label，student 用逐 token NLL/CE 学习；run summary 的 `opd_mode` 固定写成 `five_expert_online_teacher_rollout_top1`。
2. `C:\Users\mousongzhe\muxi\point\train_opd_online_vl.py` 才是当前 formal **configurable teacher/student rollout + full-vocabulary forward KL** 实现。`--opd-rollout-source` 默认 `student`，也支持 `teacher`；teacher 在同一 response 上 forward，loss 使用完整词表分布。
3. coldstart-500 launcher 显式传 `--opd-rollout-source teacher`，run summary 记录 `teacher rollout + full_vocab KL + veto/prefix`；OPD5000 launcher 显式传 `student`，summary 记录 `student rollout + full_vocab KL + veto/prefix`。因此 coldstart 不是 student rollout，OPD5000 也不是 legacy top1 CE。
4. 当 `veto_beta=0` 时，formal loss 是 \(D_{KL}(p_T\|p_S)\)，即 teacher/target 分布对 student 分布的 forward KL；veto 期内 target 不是纯 teacher，而是由 `teacher_logits + beta * stopgrad(student_logits)` 构造的分布。口述不能把整个 500-step warmup 都简写成纯 teacher-to-student KL。
5. artifact manifest 明确本地同步范围排除了 model weights、optimizer `.pt`、raw holdout JSONL 和 predictions JSONL；因此本页能闭合 **objective/code/run-summary lineage**，不能闭合 checkpoint binary、训练完成的独立重放或因果 uplift。

## 2. 两份 trainer 的实现差异

| 维度 | Legacy root trainer | Formal `point/` trainer |
| --- | --- | --- |
| 路径 | `muxi/train_opd_online_vl.py` | `muxi/point/train_opd_online_vl.py` |
| SHA-256 | `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9` | `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336` |
| rollout source | teacher 固定 | `student` / `teacher` 参数化，默认 student |
| teacher target | `argmax` token ID | response token 位置的完整 vocab logits |
| student loss | `F.nll_loss(log_softmax(student_logits), teacher_top1)` | target distribution 与 student distribution 的 full-vocabulary KL |
| token support | teacher top1 label | 完整词表；run summary 记录 `opd_distill_support=full_vocab` |
| prefix | response 全段 | `opd_prefix_loss_tokens` 可截断 loss response |
| veto | 无 | `target_logits = teacher_logits + beta * stopgrad(student_logits)` |
| summary mode | `five_expert_online_teacher_rollout_top1` | `five_expert_online_{rollout_source}_rollout_teacher_full_vocab_kl_veto_prefix` |
| 可映射 run | 早期 off-policy/top1 路线 | coldstart-500 与 OPD5000 new-experts 路线 |

### 2.1 Legacy top1 CE

legacy 实现先执行：

```text
teacher.generate(prompt)
  -> teacher(response) logits
  -> argmax over vocabulary at every response position
  -> hard token labels
  -> student(response) logits
  -> token NLL / CE
```

它只要求 student 提高 teacher top1 token 的概率，没有直接约束 teacher 对其余词表 token 的相对置信度。该路线可以称为 online teacher rollout + top1 distillation，不应称为 full-vocabulary KL，也不应称为 student rollout。

### 2.2 Formal full-vocabulary KL

formal trainer 根据 `opd_rollout_source` 由 teacher 或 student 生成 response；之后 teacher 与 student 都在同一截断 response 上 forward。令 response token 位置 \(t\) 的 student logits 为 \(z^S_t\)，teacher logits 为 \(z^T_t\)，veto 系数为 \(\beta\)：

\[
\log p_S(v\mid x,y_{<t})=\operatorname{logsoftmax}(z^S_t)_v
\]

\[
\log q_{\beta}(v\mid x,y_{<t})=
\operatorname{logsoftmax}\!\left(z^T_t+\beta\,\operatorname{stopgrad}(z^S_t)\right)_v
\]

\[
\mathcal L_t
=D_{KL}(q_{\beta,t}\|p_{S,t})
=\sum_v q_{\beta,t}(v)\left[\log q_{\beta,t}(v)-\log p_{S,t}(v)\right]
\]

当 \(\beta=0\) 时，\(q_{\beta}=p_T\)，得到 \(D_{KL}(p_T\|p_S)\)。这个方向以 teacher/target 分布作期望：teacher 赋予非零概率的 token 都会进入 loss，student 若在 teacher 高概率区域分配不足会受罚。它不是 \(D_{KL}(p_S\|p_T)\)，也不是 Jensen–Shannon divergence。

代码按每个 sample 的有效 response token 数归一化：

\[
\mathcal L_i=
\frac{\sum_t m_{i,t}\,D_{KL}(q_{\beta,i,t}\|p_{S,i,t})}
{\max\!\left(1,\sum_t m_{i,t}\right)},
\qquad
\mathcal L=\frac{1}{B}\sum_i w_i\mathcal L_i
\]

其中 \(m_{i,t}\) 是 response/prefix token mask，\(w_i\) 是 `_opd_loss_weight`。当前实现为已截断 response 构造全 1 mask；padding/prompt 不进入该 token KL。run summary 还记录 student/teacher entropy、top-k overlap、loss token 数与 vocab size，便于区分“loss 下降”和“输出分布结构一致”。

## 3. Coldstart-500 与 OPD5000 的 lineage

| Run | Student parent | Rollout | Objective | Prefix / veto | Steps / save | 本地证据 |
| --- | --- | --- | --- | --- | --- | --- |
| coldstart-500 | `/data/msz/models/8b_base` | teacher | full-vocab `KL(target || student)` | max new 128；loss prefix 64；beta 1→0 / 100 steps | 500；final only | launcher + coldstart summary |
| OPD5000 | coldstart-500 output | student | full-vocab `KL(target || student)` | max new 64；loss prefix 64；beta 1→0 / 500 steps | 5000；save every 1000 | launcher + OPD5000 summary |

coldstart summary 的关键字段为：`opd_rollout_source=teacher`、`opd_distill_support=full_vocab`、`opd_mode=five_expert_online_teacher_rollout_teacher_full_vocab_kl_veto_prefix`。OPD5000 summary 对应为 `student`、`full_vocab` 和 `five_expert_online_student_rollout_teacher_full_vocab_kl_veto_prefix`。

两条 run 的 route teacher 都由 sample metadata 选择；`route-block-shuffle` 保证 ZeRO-3 下每个 microstep 的 rank 进入同一 teacher。该设计证明的是 deterministic metadata routing，不是训练出了 learned router。

## 4. Implementation anchors

| Source | SHA-256 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `muxi/train_opd_online_vl.py` | `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9` | legacy teacher rollout、teacher top1 label、token CE、legacy mode string | coldstart/OPD5000 full-vocab KL |
| `muxi/point/train_opd_online_vl.py` | `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336` | rollout-source switch、full-vocab KL 方向、veto、prefix、entropy/top-k diagnostics | 远端实际执行内容与本地文件逐字一致之外的结果 |
| coldstart launcher | `06F349A4631D30F9533746CE7B8F852C14FC49A02FC04796839A7F3C3BADCE10` | teacher rollout、base parent、500 steps、prefix/veto/ZeRO-3 参数 | 完成状态、权重内容 |
| OPD5000 launcher | `DEEB0F93336C99AA54BC4D34F95315C5A2D60E0F9968293B20D9F3A961491BAF` | student rollout、coldstart parent、skip64k、5000 steps、save cadence | checkpoint binary 与 eval uplift |
| coldstart run summary | `90FD5A0A5983FEB5673D44CA087F597F0EBCACFD63DF1305C37C297F213D5FC0` | run parameters、last loss/entropy/overlap、mode | raw log、weights、独立复算 |
| OPD5000 run summary | `2D670DE0707CD2C6A9D1D4C7EC109C86F0A3F8F87EDE5D6959367017231547CE` | run parameters、route counts、last loss/entropy/overlap、mode | checkpoint binary、optimizer、raw predictions |
| OPD5000 artifact manifest | `035764A0461DEE5942AB25AF1BDFCD2514BD69AAC473B2DE8E43F3A7EC86021A` | remote root、formal code path、launchers、final model path、sync exclusion | binary/hash/load parity |

## 5. 面试口述修正

### 30 秒版本

> OPD 有两代同名 trainer，不能混讲。根目录 legacy 版是 teacher rollout 后取 teacher top1 token，用 hard-label CE 蒸馏；正式 new-experts 路线在 `point/train_opd_online_vl.py`，coldstart 用 teacher rollout、OPD5000 用 student rollout，两者都让 route 对应 teacher 在同一 response 上 forward，并做完整词表的 \(D_{KL}(q_\beta\|p_S)\)。veto 期的 target 还混入 stop-gradient student logits，beta 归零后才是纯 \(D_{KL}(p_T\|p_S)\)。本地缺权重和 raw predictions，所以我能证明目标实现和 summary lineage，不能把它直接升级成因果 uplift。

### “为什么 KL 方向重要？”

> 这里代码的 expectation 在 teacher/target 分布一侧，是 \(D_{KL}(q_\beta\|p_S)\)，beta=0 时就是 teacher-to-student forward KL。这样 teacher 认为有概率的完整词表区域都会约束 student；如果反过来做 \(D_{KL}(p_S\|p_T)\)，优化压力和 mode behavior 会不同。工程上还必须说清 logits 的 token 对齐、response prefix、mask、vocab revision 和 reduction，否则只说“用了 KL”没有可复核意义。

### “coldstart 和正式 OPD 的区别是什么？”

> 两者使用同一 formal full-vocab KL trainer，但 rollout distribution 不同。coldstart 从 8B base 出发，用 teacher 生成 response，降低 student 初始分布太差带来的 on-policy风险；OPD5000 从 coldstart 输出继续，用 student 自己生成 response，再让 route teacher 在该 response 上给完整词表分布。它们不是两种 KL 方向，也不是一个 top1 CE、一个 KL。

## 6. 必须保留的边界

- 不再用 root `train_opd_online_vl.py` 支持 formal full-vocabulary KL claim；该文件只能支持 legacy top1 CE。
- 不把 coldstart 说成 student rollout；summary 和 launcher均明确为 teacher rollout。
- 不把 OPD5000 说成 teacher rollout；它显式为 student rollout。
- veto beta 大于 0 时，target 是 teacher/student detached logit mixture，不是纯 teacher distribution。
- full-vocabulary 表示 loss support，不代表所有 vocabulary token 在每个位置都有较大概率，也不等于生成时没有 top-p/temperature 配置。
- 现有 summary/manifest 不包含 model weights、optimizer、raw predictions；训练完成、checkpoint 可加载和 uplift 仍需 P0 bundle。

## 7. 下一证据门

1. 从远端回传 formal `point/train_opd_online_vl.py`、launchers、DeepSpeed config 与每个 checkpoint 的 content hash，建立 run-specific manifest。
2. 新进程加载 coldstart final 与 checkpoint-1000..5000，固定 prompt/tokenizer/vocab revision 做 loss/entropy/top-k parity smoke。
3. 同一 raw-holdout、同 scorer 保留 per-sample predictions，比较 SFT-only、legacy top1、coldstart、OPD5000；没有 paired raw 前不做 objective 单因果归因。
4. 对 `veto_beta=0` 与 schedule 做 matched ablation，区分 stabilization 与最终分布拟合贡献。

## 8. References

- [OPD Claim–Evidence Inventory](opd_claim_evidence_inventory.html)
- [OPD P0 Bundle Audit](opd_p0_bundle_audit.html)
- [OPD implementation-derived oral answer](../../practice/opd_oral_model_answer.html)
- [VLA-FND-007 KL direction card](../../questions/vol_01_foundations.html)
- `C:\Users\mousongzhe\muxi\train_opd_online_vl.py`
- `C:\Users\mousongzhe\muxi\point\train_opd_online_vl.py`
- `C:\Users\mousongzhe\muxi\point\run_opd_offpolicy_coldstart500_p0p1_zero3_mb16_accum1_newexperts.sh`
- `C:\Users\mousongzhe\muxi\point\run_opd_p0p1_studentrollout_full5000_skip64000_save1000_zero3_mb16_accum1_from_coldstart500_newexperts.sh`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\artifact_manifest.json`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\remote_model_summaries\coldstart500_opd_online_run_summary.json`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\remote_model_summaries\opd5000_opd_online_run_summary.json`
