# VOL 05 ENG-016：Student + Multiple Teachers 显存与调度来源冻结

> 审计日期：2026-07-17  
> 状态：`source_frozen / VLA-ENG-016_knowledge+card_drafted / WARN`  
> 对应问题：`VLA-ENG-016`——student 同时使用多个 teacher 时，如何安排显存、forward、蒸馏 loss 与调度？  
> 当前边界：本文件冻结蒸馏目标、teacher no-grad、FSDP/ZeRO state 语义和本地 OPD hook；ENG-016 知识正文与一张 `unseen` 题卡已生成，single-teacher ablation、吞吐/显存 A/B 和个人收益结论仍后置。

## 1. 问题与最小范围（Question / Scope）

本切片只回答五个面试准备问题：

1. teacher 为什么要冻结参数并在 `no_grad` 下 forward？`detach`、`no_grad` 和 CPU/NVMe offload 分别解决什么问题？
2. 多教师的 logits/representation 如何聚合？route metadata、confidence weighting 和 learned router 的边界是什么？
3. “全部 teacher 常驻 GPU”“逐个 teacher 顺序 forward”“CPU/NVMe staging”分别如何影响 peak memory、copy/I/O 和 latency？
4. 如何设计 student hard-label loss、teacher KL loss、mask、temperature 和 teacher weight 的可复现合同？
5. 结合 OPD 本地证据，怎样描述五教师 coldstart/online OPD，而不把组合路线写成单因果提升？

本页不声称多个 teacher 已经优于单 teacher，不声称 OPD 的 loss/吞吐/成功率收益，也不把 `preloaded_zero3` 或 route metadata 写成完整的 learned router 或已验证的显存优化。

## 2. 证据类型与冻结输入

| 输入 | 类型 | 版本 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| Hinton et al. knowledge distillation | primary / paper | [arXiv:1503.02531](https://arxiv.org/abs/1503.02531)，访问 2026-07-17 | soft target、temperature 和 teacher→student transfer 的方法背景 | 当前 OPD 的 teacher 数量、路由、显存或指标 |
| PyTorch `kl_div` | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | input 是 log-probability、target 同 shape、`batchmean`/`mean` reduction 差异、`log_target` 语义 | 某个 reduction 或 temperature 一定适合 VLA；多教师权重策略 |
| PyTorch `no_grad` | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | 关闭 gradient calculation、减少需要保存的 autograd memory、thread-local 与 factory-function exception | teacher 参数自动移出 GPU、teacher forward 自动变快或不占 activation |
| PyTorch FSDP | primary / official-doc | PyTorch 2.13；访问 2026-07-17 | parameter sharding、CPU offload、state 生命周期和通信/内存边界 | 多 teacher 调度器、跨 teacher 的统一吞吐保证 |
| DeepSpeed ZeRO-3 | official-code / official-doc source | `microsoft/DeepSpeed@de1846cf6fbdd6f1c2adf046f319791ca78cc547` | 参数/梯度/optimizer 分片、CPU/NVMe offload、gather/partition assumptions | 当前 OPD 运行是否完成、teacher weight 是否可复算、显存/吞吐收益 |
| ENG-015 memory/offload contract | local-source / reviewed | 本仓库 `sources/vol_05_eng015_activation_offload_source_freeze.html` | activation 与 state offload 的区别、matched A/B、resume gate | ENG-016 的具体 teacher schedule 已实测 |
| OPD claim–evidence inventory | local-evidence | 本仓库 `evidence/projects/opd_claim_evidence_inventory.html` | 五 expert mix、`preloaded_zero3`、teacher selection、coldstart/full-vocab KL、student rollout/route KL 与证据缺口 | single-teacher/SFT-only/no-synthetic ablation、checkpoint binary、完整 raw prediction 与单因果 uplift |

### 2.1 官方来源 normalized / raw 指纹

HTML 来源按仓库统一规则：移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256；DeepSpeed RST 使用 frozen commit 的 raw bytes SHA-256。论文以 arXiv 版本和链接作为版本锚点。

| 来源 | URL | 指纹类型 | 长度 | SHA-256 |
| --- | --- | --- | ---: | --- |
| PyTorch `kl_div` | [2.13/kl_div.html](https://docs.pytorch.org/docs/2.13/generated/torch.nn.functional.kl_div.html) | normalized main text | 2336 | `c0a91e0e86816e476c8228c5b2b32c43a0ae192bb6858bad2c100f0b047cf79f` |
| PyTorch `no_grad` | [2.13/no_grad.html](https://docs.pytorch.org/docs/2.13/generated/torch.no_grad.html) | normalized main text | 2427 | `29bfe53b651ec45fa25acb9efae83c8ce7d8e47a8e97868d6fdc0436eafce0f4` |
| PyTorch FSDP | [2.13/fsdp.html](https://docs.pytorch.org/docs/2.13/fsdp.html) | normalized main text | 61919 | `9f14bed9d2267151f21bd7c0a61007e25f7443e877ab16a047fd29a28aa87810` |
| DeepSpeed ZeRO-3 | [zero3.rst](https://raw.githubusercontent.com/microsoft/DeepSpeed/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst) | raw RST bytes | 22955 | `e8eeb0ccfd067c371e522b494d70e0a233e7aeda4d5ccf6dd1a200d01a4b6847` |

## 3. Student/teacher 的最小计算合同

### 3.1 Teacher 冻结不等于 teacher 不占显存

三件事要分开：

| 操作 | 解决的问题 | 不自动解决 |
| --- | --- | --- |
| `requires_grad_(False)` / 不把 teacher 参数放进 optimizer | 不更新 teacher 参数 | 参数仍可能驻留 GPU；forward 仍可能保存 autograd graph（若未 `no_grad`） |
| `torch.no_grad()` | 不构建 teacher 的 gradient graph，减少需要保存的 autograd memory | 不搬走参数，不保证没有 activation/temporary buffer，不保证速度提升 |
| `detach()` teacher output | 切断 student loss 对 teacher output 的反向路径 | 若 teacher forward 已在 grad mode 执行，之前的中间图可能已经产生；不替代 `no_grad` |

PyTorch 2.13 文档明确把 `no_grad` 定义为关闭 gradient calculation，并说明对本来需要 gradient 的计算可减少 memory consumption；同时保留 factory-function exception 和 thread-local 边界。因此安全实现是：teacher 参数冻结、teacher forward 包在 `no_grad`、只保留 loss 需要的 logits/representation，再在 student 上反向。

### 3.2 Soft-target KL 与 hard-label loss

设 teacher (m) 的 logits 为 (z_t^{(m)})，student logits 为 (z_s)，temperature 为 (T>0)：

\[
p_t^{(m)}=\operatorname{softmax}(z_t^{(m)}/T),\qquad
\log p_s=\operatorname{log\_softmax}(z_s/T)
\]

PyTorch `kl_div(input, target)` 的 `input` 是 log-probability，`target` 与其同 shape；若用 `reduction="batchmean"`，输出是 sum 除以 batch size。标准 distillation 可写成：

\[
L_{\mathrm{KD}}^{(m)}=T^2\,\mathrm{KL}\left(p_t^{(m)}\,\|\,p_s\right)
\]

其中 (T^2) 是经典蒸馏中用于保持梯度量级的缩放；temperature、reduction、token mask 和 vocabulary 对齐必须写入 run manifest。`mean` 与 `batchmean` 不等价，不能只说“用了 KL”而不报 reduction。[1][2]

### 3.3 多教师聚合是一个额外的工程设计

若样本 (x) 由 route (r(x)) 指向教师集合 (mathcal M(x))，可先定义：

\[
L(x)=\lambda_{\mathrm{hard}}L_{\mathrm{hard}}(x)+
\lambda_{\mathrm{KD}}\sum_{m\in\mathcal M(x)}w_m(x)L_{\mathrm{KD}}^{(m)}(x)
\]

这里 (w_m(x)) 可以来自固定 route、置信度或显式实验权重；若是 route metadata，就应称为 **metadata-driven selection**，不能称为 learned router。权重归一化、teacher 缺失时的 fallback、不同 teacher 的 vocabulary/format 对齐和有效 token mask 都是工程合同，不是 Hinton 论文自动给出的默认值。

## 4. 多教师显存与调度策略

### 4.1 三种基本 schedule

| schedule | GPU peak | 计算/传输 | 适合情况 | 风险 |
| --- | --- | --- | --- | --- |
| all teachers resident | 高：参数、temporary buffer 和 concurrent outputs 叠加 | teacher forward 可并行，重复加载少 | teacher 较小、GPU 余量足、延迟敏感 | 峰值 O(∑ teacher states)，易与 student/optimizer 冲突 |
| sequential teacher forward | 较低：一次只保留一个 teacher 的活跃 state/output | teacher forward 串行，可能重复读取/同步 | teacher 大、显存紧张、吞吐可让步 | latency 叠加；若缓存所有 logits，仍会出现 output peak |
| staged CPU/NVMe | GPU 低一些，CPU/NVMe 较高 | CPU↔GPU/NVMe copy、queue、prefetch、overlap | 参数总量超过 GPU/CPU 单层容量 | I/O wait、带宽抖动、restore/lineage 复杂 |

这三种 schedule 是设计空间，不是性能结论。FSDP/ZeRO 的参数分片和 offload 可以嵌入其中，但要明确 teacher state 的 ownership、gather 时机和 optimizer 是否绝不触碰 teacher。

### 4.2 Peak memory 账本

多教师 step 可拆成：

\[
M_{\mathrm{peak}}\approx M_s+M_{t,\mathrm{resident}}+M_{t,\mathrm{active}}+M_{\mathrm{logits}}+M_{\mathrm{act}}+M_{\mathrm{optim}}+M_{\mathrm{temp}}+M_{\mathrm{comm}}
\]

(M_s) 是 student 参数/梯度，(M_{t,\mathrm{resident}}) 是常驻 teacher state，(M_{t,\mathrm{active}}) 是当前 forward 的参数/activation，(M_{\mathrm{logits}}) 是保留的 teacher 输出。顺序 schedule 主要减少 (M_{t,\mathrm{active}})；如果把所有 teacher logits 存到 batch 末尾，(M_{\mathrm{logits}}) 仍可能成为峰值。这个公式是本节点的审计账本，不是官方内存上界。

### 4.3 Step-time 与调度代价

\[
T_{\mathrm{step}}=T_s+\sum_{m\in\mathcal M}T_{t,m}+T_{\mathrm{copy}}+T_{\mathrm{io}}+T_{\mathrm{comm}}+T_{\mathrm{sync}}
\]

student backward 主要在 (T_s)；teacher no-grad forward 仍消耗 (T_{t,m})，CPU/NVMe staging 增加 (T_{\mathrm{copy}})/(T_{\mathrm{io}})。多教师并行是否能 overlap 取决于 stream、通信和内存带宽，不能由“没有 grad”推出吞吐提升。

## 5. 验证矩阵与最小 replay

每个 teacher/student run 固定：teacher revision、student revision、route schema、temperature、KL reduction、hard/KD loss weights、valid-token mask、dtype、micro/effective batch、teacher schedule、offload device、world-size、warm-up 和 measurement window。

| 轴 | baseline | candidate | 必须记录 |
| --- | --- | --- | --- |
| teacher count | single teacher | multiple teachers | teacher IDs、route distribution、missing/fallback count |
| schedule | resident | sequential/staged | peak GPU/CPU/NVMe、teacher forward ms、copy/I/O wait |
| loss | hard label only | hard + KL | (T)、reduction、mask、per-teacher loss、weight sum |
| gradient | student only | student + accidental teacher path check | teacher `grad is None`、student grad norm、overflow/scaler |
| data | fixed request trace | same trace | sample IDs、route metadata、format/length distribution |
| checkpoint | model-only | full training bundle | teacher/student revisions、optimizer/RNG/sampler、next-batch IDs |

最小 replay 不需要把所有 teacher logits 永久保存：可以在固定 request trace 上按 schedule 重新生成，并比较 route、masked KL、student logits、gradient norm、optimizer step 和下一批 sample IDs。只比较 aggregate loss，无法发现 teacher 顺序、mask 或 route drift。

## 6. 本地 OPD 证据与安全口径

本仓库 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 直接支持：

- 数据层有五个 expert mix、image-hash split、target/candidate expert 与 format metadata；
- coldstart summary 记录五教师 `preloaded_zero3`、teacher rollout 和 full-vocab KL；
- 正式 online OPD 记录 student rollout 后，在同一 response 上执行 route-based teacher forward，再做 full-vocab KL；
- 当前实现中的 teacher selection 是 route metadata 驱动，不是已经独立验证的 learned router。

同一 inventory 也明确：没有 model weights/optimizer state 的完整 bundle、single-teacher/SFT-only/no-synthetic/synthetic-ratio ablation，且旧版 OPD final 与新版 OPD5000 checkpoint 不是同一 run lineage。因此可说“我实现/复核了五教师 coldstart 与 student-rollout→teacher-KL 的训练链路及证据边界”，不能说“多教师本身带来全部 uplift”或“已证明五教师优于单教师”。

## 7. 来源到 claim 的边界

| Claim | 证据等级 | 当前安全表述 |
| --- | --- | --- |
| KL 的 input/target/reduction 语义 | primary official-doc | PyTorch 2.13 `kl_div` 合同 |
| teacher no-grad 可减少 autograd memory | primary official-doc | `no_grad` 关闭梯度计算；参数/IO 仍需单独设计 |
| 多 teacher 的权重/route 公式 | inference / engineering contract | 设计候选，需固定 manifest 与 ablation |
| OPD 五教师 `preloaded_zero3` 与 rollout/KL | local-direct / report-supported | 当前源码/summary 支持链路存在 |
| 多教师带来吞吐、显存或成功率提升 | unverified | 没有 matched single-teacher/A-B，不能说 |
| Git author 或 route metadata 等于个人 ownership/learned router | reject | 需 ownership ledger 和 learned-router artifact |

## 8. 最小验证伪代码（工程合同，不是 upstream 实现）

```python
def multi_teacher_step(student, teachers, batch, route, cfg):
    # 1. Freeze teacher parameters and keep only the student in the optimizer.
    freeze_parameters(teachers)
    student_logits = student(batch.inputs)

    # 2. Run only routed teachers under no_grad; avoid building teacher graphs.
    teacher_losses = []
    with no_grad():
        for teacher_id in route.teacher_ids:
            teacher_logits = teachers[teacher_id](batch.inputs)
            teacher_losses.append(masked_kl(student_logits, teacher_logits,
                                            temperature=cfg.temperature,
                                            reduction=cfg.kl_reduction,
                                            mask=batch.valid_mask))

    # 3. Combine hard labels and explicitly normalized teacher weights.
    loss = cfg.hard_weight * hard_loss(student_logits, batch.labels)
    loss += cfg.kd_weight * weighted_sum(teacher_losses, route.weights)

    # 4. Backprop only through the student, then record peak memory and timing.
    loss.backward()
    optimizer_step(student)
    return record_route_loss_memory_latency(route, teacher_losses)
```

伪代码只表达冻结、route、mask、KL 和 student-only backward 的顺序；teacher schedule、FSDP/ZeRO gather、CPU/NVMe staging、容错和 exact API 必须在具体环境中实现和测量。

## 9. Gate、风险与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| distillation/temperature/KL | `PASS WITH WARNING` | 后续知识页固定 log-prob、target、reduction、(T^2) 与 mask |
| teacher no-grad/freeze | `PASS WITH WARNING` | 区分参数冻结、no-grad、detach 和 offload；检查 teacher grad/peak |
| multi-teacher schedule | `WARN / engineering contract` | 对 resident/sequential/staged 做 matched memory/latency A/B |
| FSDP/ZeRO state ownership | `PASS WITH WARNING` | 记录 teacher/student revision、gather/offload、CPU/NVMe 与 checkpoint lineage |
| OPD project boundary | `PASS WITH WARNING` | 保留五教师链路 local-direct；补 single-teacher/SFT-only/synthetic-ratio ablation |
| knowledge/card | `DRAFTED / UNSEEN` | 保持题卡 `unseen`；后续补 single-teacher/A-B/lineage；不展开 ENG-017 |

## 参考来源（References）

1. Hinton, Vinyals, Dean，[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531)，soft target 与 temperature 的原始论文背景。
2. PyTorch 2.13，[`torch.nn.functional.kl_div`](https://docs.pytorch.org/docs/2.13/generated/torch.nn.functional.kl_div.html)，log-probability input、target shape 与 reduction 语义。
3. PyTorch 2.13，[`torch.no_grad`](https://docs.pytorch.org/docs/2.13/generated/torch.no_grad.html)，gradient calculation 与 memory 边界。
4. PyTorch 2.13，[FSDP](https://docs.pytorch.org/docs/2.13/fsdp.html)，parameter sharding、CPU offload 与 state 生命周期。
5. Microsoft DeepSpeed，[`zero3.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst)，ZeRO-3 partition/offload 与 assumptions。
6. 本仓库，[ENG-015 memory/offload source freeze](vol_05_eng015_activation_offload_source_freeze.html)，显存/step-time/resume 合同。
7. 本仓库，[OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)，五教师、route、coldstart、online KL 与 ablation/ownership 缺口。
