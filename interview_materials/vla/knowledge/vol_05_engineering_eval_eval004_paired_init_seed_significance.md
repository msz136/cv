# VOL 05 EVAL-004：Paired Init / Seed Evaluation 与显著性

> 状态：`drafted / VLA-EVAL-004 / knowledge_26_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-003 Success Rate / Confidence Interval](vol_05_engineering_eval_eval003.html)  
> 来源冻结：[EVAL-004 Source Freeze](../sources/vol_05_eval004_paired_init_seed_significance_source_freeze.html)  
> 项目边界：UWM 186/250 与 232/250 不是 matched pairs；OpenPiVLA 97.4% 缺 denominator/lineage；OPD 10k 是静态 row pool。本页不制造本地显著性结果。

## 问题（Question）

如何判断两个 VLA checkpoint 在 paired init/seed evaluation 下是否真的有差异？需要从 pairing key、四格表、效应和区间讲到 exact McNemar、paired randomization/bootstrap、training-seed 层级、power、多重比较与 checkpoint selection。

## 1. 先说直觉：让 A/B 做同一张“考卷”

独立评估像让 A 做一套题、B 做另一套题；难度差会混入模型差。paired evaluation 则让 A/B 面对同 task、同初始状态和同协议。每道题上“都成功/都失败”不能告诉你谁更好；真正区分方向的是“A 成 B 败”和“A 败 B 成”。

因此面试回答的主线应是：

```text
pairing validity -> discordant outcomes -> paired effect/CI/test
                 -> hierarchy/power -> selection/multiplicity
                 -> project evidence boundary
```

## 2. Pair 的专业定义

第 `i` 个 pair 不是“两个数组的第 i 行”，而是同一个预注册实验条件：

\[
P_i=(task_i,init_i,env_i,controller_i,scorer_i,protocol_i,repeat_i).
\]

变量解释：`init_i` 最好由 snapshot/hash 或 reset 后 state/首帧证明；其他字段冻结 simulator、controller、horizon、success predicate 和 repeat。实现上先生成 immutable pair manifest，再让 A/B 分别产生 outcome，最后按 `pair_id` join。join 后缺任一 arm、重复 key 或 protocol hash 不同都应 fail closed。

### 2.1 为什么 same seed 不等于 same init

seed 只是随机数流的入口。simulator version、wrapper reset path、并发顺序和随机调用次数变化，都会让相同整数落到不同状态。最小验证是保存 `init_snapshot_hash`、reset 后 proprio/state 和首帧 checksum；不一致时不能继续称 paired init。

### 2.2 四类 seed

| 类型 | 含义 | 分析层级 |
| --- | --- | --- |
| environment/init seed | 产生任务初态 | pair 条件；仍要 snapshot 验证 |
| rollout stochastic seed | policy/planner sampling noise | pair 内 common-random-number 或重复层 |
| model training seed | 参数初始化、shuffle、优化轨迹 | 顶层 model-run replicate |
| bootstrap/permutation seed | 统计重采样可复算 | 分析配置，不是实验样本 |

training seed 不能被 episode 数替代。如果主张训练算法 A 优于 B，至少要有多个 A/B training-run replicates；单对 checkpoint 上增加 rollout 只减少该 checkpoint pair 的环境噪声，不会展示 training variance。

## 3. Binary paired table 与 effect size

对 `(A_i,B_i)∈{0,1}²` 统计：

| | B success | B failure |
| --- | ---: | ---: |
| A success | `n11` | `n10` |
| A failure | `n01` | `n00` |

令 `n=n11+n10+n01+n00`：

\[
\hat\Delta=\bar A-\bar B=\frac{n_{10}-n_{01}}{n}.
\]

变量解释：`Delta` 是 paired success-rate difference；正数支持 A。实现映射是每个 pair 先算 `D_i=A_i-B_i`，再平均。不能只有 `A_success/total` 和 `B_success/total` 两个 aggregate，因为它们无法恢复哪些 episode discordant。

最小报告包：

- `n11,n10,n01,n00` 与 attempted/valid pair count；
- `Delta` 和 paired 95% CI；
- exact McNemar 或预注册 paired randomization p-value；
- alpha、multiple-comparison family 和 practical threshold/MDE；
- task、training seed、init/rollout cluster 与 invalid-pair 规则。

## 4. Exact McNemar 检验

令 `d=n10+n01`。在无方向差异的 null 下：

\[
n_{10}\mid d\sim\mathrm{Binomial}(d,0.5).
\]

变量解释：test 只问 discordant pair 的方向是否对称；`n11/n00` 不进入 exact test。statsmodels `mcnemar(table, exact=True)` 实现这一 binomial tail。`d=0` 时没有方向差异证据，不等价于证明模型相同。

### 4.1 为什么不能用两个独立比例检验

paired outcomes 共享 init 难度，`Cov(A_i,B_i)` 通常不为 0。把两臂当独立会丢失 covariance，并把实验问题改成两个边际总体比较。正确的 effect/CI/test 都在 `D_i=A_i-B_i` 或 paired table 上完成。

### 4.2 显著性不等于有用

`p<alpha` 只说明在 null 与分析合同下数据不寻常，不说明提升达到部署价值。应预先定义 practical threshold，例如“macro success 至少 +3pp 且 safety 不退化”，并同时看 paired CI 是否越过 0 与 practical threshold。MDE 是设计输入，不应在看完结果后改。

## 5. Paired randomization 与 bootstrap

### 5.1 Pair 内交换标签

paired randomization 在每个 pair 内随机交换 A/B，保持任务难度配对：

```python
from scipy.stats import permutation_test

def paired_effect(a, b, axis=-1):
    # Effect is computed after preserving A/B observation pairs.
    return (a - b).mean(axis=axis)

test = permutation_test(
    (a, b), paired_effect,
    permutation_type="samples",  # swap sample labels within pairs
    alternative="two-sided",
)
```

`permutation_type="pairings"` 会重排 observation associations，不是 A/B assignment test；这是高频 API 陷阱。

### 5.2 同 index 的 paired bootstrap

```python
from scipy.stats import bootstrap

ci = bootstrap(
    (a, b), paired_effect,
    paired=True,  # both arms reuse exactly the same resampled indices
    confidence_level=0.95,
)
```

若手写，必须抽 index 后同时索引 `a[idx]`、`b[idx]`。A/B 各自独立 bootstrap 会破坏 pairing。对于多个 task，应按目标 estimand 选择 task-stratified/cluster bootstrap；先在 EVAL-005 冻结 macro/micro/weighted 目标，不能让 resampling 顺手决定权重。

## 6. 层级：task / init / rollout / training seed

正确的数据结构通常是：

```text
training seed pair
  └─ task
      └─ init snapshot
          └─ rollout repeat
              ├─ A outcome
              └─ B outcome
```

不能把以下对象展开成 iid：同一 episode 的 frame/step、同一 init 的重复 rollout、同一 task 的所有 init、同一 checkpoint 的所有 episode、OPD 中重复 image/path 的多行标注。选择 cluster bootstrap、mixed/hierarchical model 或先聚合到顶层单位，取决于目标是“这个 checkpoint 在固定 grid 上”还是“训练方法在 task/training-seed 总体上”。

## 7. Power、discordant rate 与样本计划

McNemar 的有效 direction trial 数是：

\[
d=n_{10}+n_{01},\qquad q=\frac{d}{n}.
\]

变量解释：`q` 是 discordant rate。总 pair 数 `n` 只有通过预期 `q` 才变成可供 exact test 使用的 `d`。两个模型几乎总是一起成败时，250 对也可能只有很少 discordant pairs；因此 power/MDE 规划要同时给 baseline、预期 `q`、direction imbalance、alpha、power、task 数和 training runs。

推荐先用独立 pilot 估计 `q`，再锁定 final pair count；pilot/validation 不进入最终 holdout p-value。若未做 power analysis，面试中应说“当前只报告 effect/CI 与 observed discordance，不能声称 no-difference”。

## 8. Invalid pair 与 missingness

在跑实验前分类：

| 事件 | 可选规则 | 必须报告 |
| --- | --- | --- |
| env/scorer 对双臂共同无效 | pair invalid/exclude | 原因和 count |
| A 单臂 server crash | 预注册为 failure 或 infrastructure invalid | 不得看完结果后静默删除 |
| safety termination | 通常属于评估 outcome | success/failure 与 safety reason |
| missing trace / join mismatch | fail closed | attempted、missing arm、duplicate key |

规则没有唯一答案，但必须在 outcomes 之前冻结，并做 sensitivity analysis。只删掉新模型崩溃的 episode 会系统性抬高新模型。

## 9. Selection、holdout 与 multiplicity

同一 init grid 既用于选择 checkpoint/horizon，又用于最终显著性，会产生 winner's curse。安全流程：validation grid 选 checkpoint；锁定模型、processor/normalizer、controller 和 scorer；再在 untouched holdout grid 上做一次 primary comparison。

多个 task/checkpoint/horizon/metric 同时检验时：预注册 primary endpoint；有限 family 可用 Holm step-down；大量 task/run 可使用层级或预注册 aggregate，并完整报告 per-task effects。Holm 只能控制多重检验错误，不能修复 protocol drift 或坏 pairing。

## 10. 可执行 pipeline

```python
def paired_eval(rows, alpha=0.05):
    # 1. Validate immutable keys before looking at success outcomes.
    pairs = validate_and_join_by_pair_id(rows)
    assert all(p.a_protocol_hash == p.b_protocol_hash for p in pairs)
    assert all(p.a_init_hash == p.b_init_hash for p in pairs)

    # 2. Apply the pre-registered invalid-pair rule; preserve audit counts.
    valid, exclusions = apply_preregistered_rule(pairs)
    a = np.asarray([p.a_success for p in valid], dtype=int)
    b = np.asarray([p.b_success for p in valid], dtype=int)

    # 3. Build the four cells and paired effect.
    n11 = int(((a == 1) & (b == 1)).sum())
    n10 = int(((a == 1) & (b == 0)).sum())
    n01 = int(((a == 0) & (b == 1)).sum())
    n00 = int(((a == 0) & (b == 0)).sum())
    effect = float((a - b).mean())

    # 4. Use exact McNemar plus a paired CI; never bootstrap arms separately.
    table = [[n11, n10], [n01, n00]]
    pvalue = statsmodels.stats.contingency_tables.mcnemar(
        table, exact=True
    ).pvalue
    ci = scipy.stats.bootstrap(
        (a, b), lambda x, y, axis: (x-y).mean(axis=axis),
        paired=True, confidence_level=1-alpha
    ).confidence_interval
    return {"cells": table, "effect": effect, "ci": ci,
            "pvalue": pvalue, "exclusions": exclusions}
```

该伪代码是评估合同，不是本地已存在 scorer。真实实现还需 task/training-seed cluster、Holm family、holdout identity 和 resampling seed。

## 11. 项目挂钩与面试防线

### 11.1 UWM

`186/250=0.744` 是 fixed-pruned-init；`232/250=0.928` 是 reset-style。两者 protocol 不同，且当前没有 250 条 matched `task/init/seed/A_success/B_success` rows，也缺同 checkpoint/normalizer/scorer lineage。因此只能说“结果暴露 protocol sensitivity”，不能做 McNemar、不能称 reset protocol 显著提升模型。

### 11.2 OpenPiVLA

`97.4%` 缺 denominator、trial/seed/init、raw episode 和 archive-to-checkpoint lineage；连单臂 CI 都不能闭合，更不能进入 paired comparison。

### 11.3 OPD

10k 是 box/point/text 静态 row-level evaluation。重复 image/path 和同图多标注会形成 cluster；它可以另建 paired scorer/model comparison，但 pair unit 应是预注册的 sample/image cluster，不是 robot rollout，也不能与 UWM episode 合并。

## 12. 高频追问与回答骨架

1. **为什么 paired 更有 power？**控制相同 init 难度，直接分析 `A-B`；但 power 仍由 discordant rate 和方向不平衡决定。
2. **McNemar 为什么不看 n11/n00？**双方同结果不提供方向信息，exact null 只条件在 `d=n10+n01`。
3. **same seed 足够吗？**不够；还需 init snapshot/hash、首帧/state 与 protocol hash。
4. **训练 seed 和 rollout seed 区别？**前者是 model-run replicate，后者是固定 checkpoint 内的执行随机性；episode 不能替代 training runs。
5. **p<0.05 就上线吗？**不；还要 effect、paired CI、practical threshold、安全指标、multiplicity 和 holdout。
6. **多个 task 怎么做？**先在 EVAL-005 定义 estimand/权重，再做 per-task effect 与 stratified/hierarchical inference。
7. **单臂 crash 怎么办？**按预注册规则记 failure 或 invalid，报告 count 和 sensitivity；不能事后删除。
8. **为何不能比较 UWM 两个 aggregate？**protocol 和 pair lineage 都不一致，四格表不可恢复。

## 13. Review checklist 与下一入口

- [ ] pairing key 含 task、init snapshot/hash、protocol 和 repeat；
- [ ] 四类 seed 分开；training run 是顶层 replicate；
- [ ] 报 `n11/n10/n01/n00`、effect、paired CI、p-value；
- [ ] McNemar 只使用 discordant pairs；
- [ ] permutation 用 SciPy `samples`，bootstrap 用 `paired=True`；
- [ ] invalid-pair、checkpoint selection、holdout 和 multiplicity 预注册；
- [ ] practical threshold/MDE 与统计显著性分开；
- [ ] 本地项目没有 raw pairs 时保持 WARN，不输出显著性 claim。

本节点保持 `WARN/unseen`。下一内容节点固定为 `VLA-EVAL-005`：macro / micro / per-task / weighted aggregation；真实口述前不创建 coaching state。

## References

1. [EVAL-004 Source Freeze](../sources/vol_05_eval004_paired_init_seed_significance_source_freeze.html)。
2. McNemar (1947) 与 Newcombe (1998) paired proportions 方法，固定 DOI 见 source freeze。
3. statsmodels `mcnemar@v0.14.6` 与 SciPy `permutation_test/bootstrap@v1.16.3`，固定 blob 与 SHA 见 source freeze。
4. Henderson et al., Colas et al., Agarwal et al. 与 `rliable`：training seed、task/run uncertainty 与统计报告边界。
5. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
6. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
7. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

