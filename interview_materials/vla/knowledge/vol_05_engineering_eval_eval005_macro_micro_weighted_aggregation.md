# VOL 05 EVAL-005：Macro / Micro / Per-task / Weighted Aggregation

> 状态：`drafted / VLA-EVAL-005 / knowledge_27_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-003 Success Rate / CI](vol_05_engineering_eval_eval003.html) 与 [EVAL-004 Paired Significance](vol_05_engineering_eval_eval004_paired_init_seed_significance.html)  
> 来源冻结：[EVAL-005 Source Freeze](../sources/vol_05_eval005_aggregation_estimand_source_freeze.html)  
> 项目边界：UWM 0.744 只做 final summary 算术一致性检查；OpenPiVLA 97.4 只到 equal-suite archive summary；OPD box/point/text 不压成统一总分。

## 问题（Question）

多 task VLA 成功率该报 macro、micro、per-task 还是 weighted？强回答要先定义 estimand 和 task/suite/run 层级，再给公式、权重、missingness、uncertainty 和项目边界，而不是说“macro 更公平、micro 更稳定”。

## 1. 直觉：平均分之前先决定“谁有几票”

macro 给每个 task 一票；micro 给每个 episode 一票；weighted 给外部定义的 task 重要性投票；per-task 则把每张选票原样公开。没有一种平均天然正确，只有与目标总体、部署 mixture 和风险约束一致的平均。

回答顺序：

```text
target population -> task registry -> per-task k/n
                  -> fixed weights -> aggregate + CI
                  -> coverage/missingness -> project boundary
```

## 2. Per-task 是主表，不是附录

第 `t` 个 task：

\[
\hat p_t=\frac{k_t}{n_t}.
\]

变量解释：`k_t` 是成功 episode 数，`n_t` 是按预注册 validity rule 计入的 episode 数。实现映射必须包括 suite/task revision、checkpoint、protocol/scorer hash、planned/attempted/valid `n` 和 exclusion。只报一个 overall average 会掩盖失败集中在哪个 task。

最低 per-task table：

| task | k/n | rate + CI | protocol | coverage/exclusion | weight |
| --- | --- | --- | --- | --- | --- |
| task_t | `k_t/n_t` | point + interval | version/hash | planned/valid/reason | macro/micro/deploy |

## 3. 三种 scalar aggregate

### 3.1 Macro：每 task 等权

\[
\hat p_{macro}=\frac{1}{T}\sum_{t=1}^{T}\hat p_t.
\]

变量解释：每个 task 权重 `1/T`。它适合固定 benchmark task 清单上的“equal-task average”，但会受 task taxonomy 粒度影响：拆分某个 task 等于增加其票数。

### 3.2 Micro：按 episode 分母加权

\[
\hat p_{micro}=\frac{\sum_t k_t}{\sum_t n_t}
=\sum_t\frac{n_t}{\sum_j n_j}\hat p_t.
\]

变量解释：每个 task 权重是其 episode count 占比。如果 rollout 数来自实验预算而非部署流量，micro 把采样计划变成了业务权重。它通常数值更受大分母 task 支配，不等于“更真实”。

### 3.3 Weighted：显式目标权重

\[
\hat p_w=\sum_t w_t\hat p_t,\qquad
w_t\ge0,\quad\sum_t w_t=1.
\]

变量解释：`w_t` 可来自冻结的部署频率、业务风险或 benchmark contract。权重必须在看结果前确定，并在 A/B 比较中保持相同。safety-critical task 更适合作为 gate/constraint，而不是给一个小权重后平均掉。

macro 和 micro 都是 weighted 的特例；面试中把完整 `w_t` 或生成规则说出来，比只报名字更重要。

## 4. Macro = Micro 只是平衡设计的巧合

当所有 task 都有相同分母 `n_0`：

\[
\hat p_{micro}=\frac{n_0\sum_t \hat p_t}{Tn_0}=\hat p_{macro}.
\]

变量解释：这是代数相等，不是统计语义相同。只要 task 缺 episode、无效规则不同或 rollout 预算改变，micro 权重就变；macro 的 task 权重不变，但 coverage 仍可能变。

## 5. 权重不一致会制造 Simpson-style reversal

| model | easy | hard | macro | 各自 micro |
| --- | --- | --- | ---: | ---: |
| A | 9/10 = 0.90 | 60/100 = 0.60 | 0.75 | 0.627 |
| B | 80/100 = 0.80 | 5/10 = 0.50 | 0.65 | 0.773 |

A 在每个 task 都更高，但因为 A/B 的 task episode allocation 相反，直接比较各自 micro 会得到 B 更高。修复不是争论 macro/micro，而是在共同 task registry 上使用同一个权重向量；paired init/seed 时先算 pair-level `A-B`，再聚合。

## 6. Suite 平均与 task 平均不是同一件事

设 suite `s` 内有多个 task：

\[
w_{s,t}=w_s w_{t\mid s}.
\]

变量解释：equal-suite average 先让每个 suite 等权，再决定 suite 内 task 权重；equal-task average 则让所有 task 等权。suite 的 task 数不同时，两者不同。“四 suite 平均 97.4”不能恢复 suite 内 per-task 分母。

建议报告 hierarchy：

```text
benchmark revision
  -> suite
      -> task revision
          -> training seed / checkpoint run
              -> init / rollout episode
```

## 7. 多 training seed 怎么进 aggregate

如果结论是“训练方法的平均表现”，training run 是顶层 replicate。构造 `num_runs × num_tasks` score matrix，明确顺序：

1. 对每个 run/task 固定 protocol 得到 task score；
2. 对 run 求 task conditional mean 或保留完整分布；
3. 按预注册 task weights 聚合；
4. 在 run/task 层做 stratified uncertainty。

`rliable.aggregate_mean` 对完整矩阵先按 run 得每 task mean，再对 task 等权；它对应 equal-task mean，不自动支持不平衡 raw episode table。单 checkpoint 跑很多 episode不能替代多个 training seeds。

## 8. 区间：你想推广到哪一层

### 8.1 固定 task set

只推广到换一组 run/seed：保持 task strata，resample run/seed 或 task 内 init cluster，并用同一权重重算。`rliable task_bootstrap=False` 对应这个问题。

### 8.2 未知 task population

希望推广到新 task：只有当 task sampling/exchangeability 可解释时才对 task 重采样；`task_bootstrap=True` 还重采样 tasks。hand-picked benchmark task 并不自动代表部署总体，因此这个 CI 仍需 caveat。

### 8.3 不能只报 pooled binomial CI

naive micro binomial CI 把所有 episode 当同分布 iid，不能表达 task heterogeneity、training seed 或 init cluster。至少同时给 per-task CI、aggregate cluster/stratified CI、task/run coverage 和 resampling seed。

## 9. Missingness 与 coverage gate

| 风险 | 防线 |
| --- | --- |
| 模型缺整个难 task | 对预注册 registry fail closed；不得各自平均 available tasks |
| 单臂 crash 后删 episode | 沿用 EVAL-004 invalid-pair rule，报告 attempted/valid/excluded |
| task version/scorer 变化 | task/scorer/protocol hash 参与 join |
| suite 新增 task | 先在旧共同 registry 重算，再单列新增 coverage |
| observed weights 不满 1 | 报 `weight_coverage`，不得静默 renormalize |

如果预注册规则把 missing 计 failure，要写明；如果判 infrastructure invalid，也要同时报告 sensitivity。关键是不能看完结果再选择。

## 10. 模型比较与统一权重

对 A/B 使用：

\[
\hat\Delta_w=\sum_t w_t(\hat p_{A,t}-\hat p_{B,t}).
\]

变量解释：共同的 `w_t` 确保比较的是同一个 target mixture。若有 paired init/seed raw data，应先在 pair 层算差值，再按 task/run hierarchy聚合；显著性、multiple testing 与 final holdout 继续遵循 EVAL-004。

## 11. Mean、median、IQM 与 profile

当 run/task 少且分布偏斜，median、IQM、optimality gap、performance profile 能补充 mean。frozen `rliable.aggregate_iqm` 对 run-task entries 做 25% trimmed mean，它不是 macro success 的别名，也不能隐藏 per-task failure。

建议最小组合：

- per-task `k/n + CI`；
- 一个预注册 primary aggregate（macro 或 deployment-weighted）；
- micro 作为样本池描述，若权重有业务意义；
- task/run 分布图或 IQM/profile 作为 robustness 补充；
- safety/recovery 另作 gate，不混进单一 success scalar。

## 12. 项目挂钩

### 12.1 UWM

final user-confirmed 五 task rates 为 `0.88/0.80/0.76/0.66/0.62`，且各 50 次，因此 macro 和 micro 都是 `0.744`。这只说明 summary arithmetic 一致；缺 250 raw episodes/checkpoint/normalizer/scorer。较早材料另有 `book_caddy=42/50`，final summary 是 `44/50`，不能跨版本拼接。reset-style `232/250` 属于另一 protocol。

### 12.2 OpenPiVLA

archive 四 suite summary `0.98/0.995/0.99/0.93` 的 equal-suite mean 是 `0.97375→97.4%`；official OpenPI 四行 mean 是 `96.85%`。当前只能做表内 arithmetic audit，不能恢复 per-task/micro/CI，也不能声称 0.55pp improvement，因为 denominator、seed/init、raw episodes 和 lineage 未闭合。

### 12.3 OPD

box 6100、point 1400、text 2500 使用不同 metric。不能按 6100/1400/2500 做一个 micro “总准确率”；应按格式/池分别报告，在同 metric 内再使用冻结 pool weights。重复 image/path 需要 image-cluster uncertainty，静态指标不能叫 robot rollout success。

## 13. 可执行 aggregation contract

```python
def report_aggregates(rows, deploy_weights):
    # 1. Validate a common task/version/protocol registry first.
    task_rows = summarize_per_task(rows, fail_on_missing=True)
    rates = {r.task_id: r.success_k / r.valid_n for r in task_rows}

    # 2. Compute labeled estimands using explicit, frozen weights.
    macro = sum(rates.values()) / len(rates)
    micro = sum(r.success_k for r in task_rows) / sum(r.valid_n for r in task_rows)
    weighted = sum(deploy_weights[t] * rates[t] for t in rates)

    # 3. Recompute the same statistics inside run/task/init-aware bootstrap.
    ci = cluster_bootstrap(rows, weights=deploy_weights,
                           top_level="training_seed",
                           strata=["task_id", "init_cluster"])
    return {"per_task": task_rows, "macro": macro,
            "micro": micro, "weighted": weighted, "ci": ci}
```

这是设计合同，不是本地已存在 scorer。实现前还需决定 task fixed/random、missingness、paired comparison 和 deployment-weight uncertainty。

## 14. 高频追问

1. macro 与 micro 的权重分别是什么？
2. 为什么每 task 50 次时二者相等？
3. micro 为什么可能被 rollout budget 支配？
4. 两模型各自 micro 为什么会 ranking reversal？
5. equal-suite 和 equal-task average 有什么差别？
6. training seed、task、init、episode 如何分层？
7. task-bootstrap 何时有意义？
8. 缺 task 时能否重归一化？
9. IQM 为什么不是 macro 的替代名？
10. UWM/OpenPiVLA/OPD 各自能安全聚合到哪一层？

## 15. Review checklist 与下一入口

- [ ] per-task `k/n/CI`、task/version/protocol 与 coverage 可回查；
- [ ] primary estimand 和 weight vector 在结果前冻结；
- [ ] A/B 使用共同 registry 和共同 weights；
- [ ] training seed 是顶层 replicate，init/episode cluster 不展开为 iid；
- [ ] missing task/episode 规则与 weight coverage 显式报告；
- [ ] robust aggregate 写全定义，不冒充 macro；
- [ ] 不跨 metric、protocol 或 evidence level 合成总分。

本节点保持 `WARN/unseen`。下一内容节点固定为 `VLA-EVAL-006`：benchmark / environment / controller / scorer versioning；真实口述前不创建 coaching state。

## References

1. [EVAL-005 Source Freeze](../sources/vol_05_eval005_aggregation_estimand_source_freeze.html)。
2. Agarwal et al. 与 `rliable`：run/task uncertainty、aggregate mean/IQM 和 performance profiles。
3. LIBERO frozen `metric.py`：per-task success vector；OpenPI LIBERO README：四 suite summary 与 official average。
4. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
5. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
6. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
