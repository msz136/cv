# VOL 05 Engineering / Evaluation：Student + Multiple Teachers 的显存与调度（ENG-016）

> 状态：`drafted / knowledge_18_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-016`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-016 Student + Multiple Teachers Source Freeze](../sources/vol_05_eng016_multiteacher_memory_scheduling_source_freeze.html)。  
> 核心边界：teacher 参数冻结、`no_grad`、output `detach`、CPU/NVMe offload 和多教师 route 是不同合同；OPD 五教师链路存在不等于多教师收益已被单教师 ablation 证明。

## 问题（Question）

`VLA-ENG-016`：student 同时使用多个 teacher 做蒸馏时，如何安排显存、teacher forward、KL/hard loss 和调度？如何证明多教师方案没有把显存和 latency 风险隐藏起来？

回答要分三层：

1. **训练语义**：哪些参数更新，teacher 输出是否建立 autograd graph，KL 的 input/target/reduction/mask 是什么？
2. **系统调度**：teacher 是常驻 GPU、逐个 forward，还是 CPU/NVMe staging？peak memory 和 step time 如何变化？
3. **项目证据**：OPD 的五教师 route/coldstart/online KL 能支持什么，哪些需要 single-teacher 或 SFT-only 对照？

## 知识地图位置与前置依赖

```text
ENG-013 RNG / replay + ENG-015 memory/offload
                 ↓
teacher freeze/no_grad → KL/mask → multi-teacher route
                 ↓
resident / sequential / staged schedule
                 ↓
peak memory + latency A/B → checkpoint lineage → closed-loop eval
```

前置：

- `VLA-ENG-005`：effective batch、AMP、梯度与 overflow。
- `VLA-ENG-006/013`：checkpoint lineage、RNG、sampler cursor 和 replay。
- `VLA-ENG-015`：activation checkpoint、CPU/NVMe offload、显存/step-time 账本。
- [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：五教师、route、coldstart、online KL 与证据缺口。

## 1. 短答：先分清训练图，再选择 schedule

**30 秒回答**：先冻结 teacher 参数，只让 student 进 optimizer；teacher forward 放在 `no_grad`，再按 route 计算带 temperature、reduction 和 valid-token mask 的 KL。显存上比较 all-resident、sequential、CPU/NVMe staged 三种 schedule，同时固定 batch、dtype、world-size 和 request trace，测 peak、teacher latency、I/O wait、student gradient 与 next-batch replay。OPD 当前能证明五教师训练链路和 route metadata，不能证明多教师优于单教师或带来吞吐提升。

## 2. 直觉：老师不做反向，但仍然占教室

把 student 想成正在考试的学生，teacher 只负责给出参考分布：

- `requires_grad_(False)` 表示 teacher 不更新，但参数仍可能在 GPU；
- `no_grad()` 表示 teacher forward 不建立用于反向的 autograd graph，减少保存的梯度中间量；
- `detach()` 只切断输出向后的梯度路径，不能替代在 forward 期间关闭 graph；
- 多个 teacher 若同时常驻，参数和临时 buffer 叠加；若逐个调用，峰值下降但 teacher latency 累加；若放到 CPU/NVMe，又新增 copy/I/O 和调度等待。

因此“teacher 不反向”不等于“teacher 免费”。需要同时报告 teacher state ownership、输出缓存、copy/I/O 和 student 更新路径。

## 3. Student/teacher 训练合同

### 3.1 参数、graph 和 optimizer ownership

| 对象 | 是否更新 | 是否进 optimizer | 必须检查 |
| --- | --- | --- | --- |
| student parameters | 是 | 是 | gradient norm、overflow、optimizer step |
| teacher parameters | 否 | 否 | `requires_grad=False`、revision/hash、无 teacher grad |
| teacher forward graph | 不应保留 | 不适用 | `torch.no_grad()` 覆盖完整 teacher forward |
| teacher logits/representation | 只读 | 不适用 | dtype、vocabulary/format 对齐、mask 后的 lifetime |
| route/weight metadata | 不更新模型 | 不适用 | source line、teacher IDs、fallback 和权重归一化 |

PyTorch 2.13 文档把 `no_grad` 定义为关闭 gradient calculation，并说明它可以减少原本需要梯度的计算所占 memory；但 factory functions 有例外，且上下文是 thread-local。工程上仍要显式冻结 teacher 参数、排除 optimizer、记录 teacher revision，不能只依赖上下文管理器。

### 3.2 Distillation KL 的 shape 和方向

设 teacher (m) 的 logits 是 (z_t^{(m)})，student logits 是 (z_s)，temperature 为 (T>0)：

\[
p_t^{(m)}=\operatorname{softmax}(z_t^{(m)}/T),\qquad
\log p_s=\operatorname{log\_softmax}(z_s/T)
\]

PyTorch `torch.nn.functional.kl_div` 的 `input` 需要 log-probability，`target` 与 `input` 同 shape。标准 teacher-to-student 蒸馏可写成：

\[
L_{\mathrm{KD}}^{(m)}=T^2\,\mathrm{KL}\left(p_t^{(m)}\,\|\,p_s\right)
\]

其中 (T^2) 是经典蒸馏中的梯度尺度修正；`reduction="batchmean"` 表示输出求和后除以 batch size，和默认 `mean` 不等价。实现必须固定 `T`、`reduction`、`log_target`、vocabulary 对齐和 valid-token mask，不能只记录“用了 KL”。[1][2]

### 3.3 Hard loss + 多教师 loss

若样本 (x) 的 route 指定教师集合 (mathcal M(x))，可写成：

\[
L(x)=\lambda_{\mathrm{hard}}L_{\mathrm{hard}}(x)+
\lambda_{\mathrm{KD}}\sum_{m\in\mathcal M(x)}w_m(x)L_{\mathrm{KD}}^{(m)}(x)
\]

(w_m(x)) 可以是固定 route、置信度或实验设定；若它来自数据中的 `target_expert`/`candidate_experts`，应称为 **metadata-driven selection**，不应称为 learned router。(L_{\mathrm{hard}}) 负责保留真实标签/格式约束，KD 项负责传递 soft distribution；两个项都要按有效 token、response mask 或 action/grounding format 对齐。

## 4. 三种 teacher schedule

| schedule | 显存特征 | 时间特征 | 适用情形 | 主要风险 |
| --- | --- | --- | --- | --- |
| all teachers resident | 参数、active buffer、输出可能同时叠加，peak 高 | 可并行但受 GPU compute/memory bandwidth 限制 | teacher 小、GPU 余量足、latency 优先 | student/optimizer 峰值冲突；容易 OOM |
| sequential teacher forward | 一次只保留一个 active teacher，peak 较低 | teacher forward 串行，latency 近似求和 | teacher 大、显存紧、训练可让步 | 输出缓存和重复同步仍可能形成峰值 |
| staged CPU/NVMe | GPU state 下降，CPU/NVMe state 上升 | copy、queue、prefetch、I/O wait 变多 | 总 teacher state 超过单层容量 | 带宽抖动、恢复复杂、overlap 未验证 |

FSDP/ZeRO 可以作为 schedule 的底层 state 分片或 offload 工具，但它们不自动决定 teacher 的调用顺序、route 权重、KL mask 或输出缓存生命周期。DeepSpeed ZeRO-3 文档中的 CPU/NVMe offload 能力支持“状态可以分层管理”的语义，不能推出当前 OPD 的 latency 或显存收益。

## 5. 显存与 step-time 账本

### 5.1 Peak memory

多教师 step 的近似账本为：

\[
M_{\mathrm{peak}}\approx M_s+M_{t,\mathrm{resident}}+M_{t,\mathrm{active}}+M_{\mathrm{logits}}+M_{\mathrm{act}}+M_{\mathrm{optim}}+M_{\mathrm{temp}}+M_{\mathrm{comm}}
\]

其中 (M_s) 是 student 参数/梯度，(M_{t,\mathrm{resident}}) 是常驻 teacher state，(M_{t,\mathrm{active}}) 是当前 teacher forward 的活跃状态，(M_{\mathrm{logits}}) 是保留的输出，后几项是 activation、optimizer、临时 buffer 和通信峰值。sequential schedule 主要减少 (M_{t,\mathrm{active}})；如果把全部 teacher logits 缓存到 batch 结束，(M_{\mathrm{logits}}) 仍可能主导峰值。

### 5.2 Step time

\[
T_{\mathrm{step}}=T_s+\sum_{m\in\mathcal M}T_{t,m}+T_{\mathrm{copy}}+T_{\mathrm{io}}+T_{\mathrm{comm}}+T_{\mathrm{sync}}
\]

(T_s) 是 student forward/backward，(T_{t,m}) 是 teacher no-grad forward；CPU/NVMe staging 贡献 (T_{\mathrm{copy}}) 与 (T_{\mathrm{io}})。是否能与 student 或通信 overlap 由 stream、带宽和实现决定，不能由 `no_grad` 自动推出吞吐提升。

## 6. Matched A/B 与 replay 协议

固定以下字段：teacher/student revision、route schema、teacher count、temperature、KL reduction、hard/KD weights、valid-token mask、dtype、micro/effective batch、teacher schedule、offload device、world-size、warm-up、measurement window 和 request trace。

| A/B 轴 | baseline | candidate | 关键输出 |
| --- | --- | --- | --- |
| teacher count | single teacher | multiple teachers | teacher IDs、route distribution、fallback count |
| schedule | resident | sequential/staged | peak GPU/CPU/NVMe、teacher ms、copy/I/O wait |
| loss | hard only | hard + masked KL | (T)、reduction、mask、每教师 loss、权重和 |
| graph | teacher grad mode | `no_grad` + frozen params | teacher grad 是否为空、student grad norm、overflow |
| replay | fixed request trace | 同一 trace | sample IDs、route、masked loss、optimizer step |

只看 aggregate loss 无法发现 route drift、teacher 顺序、padding/mask 或 format conflict。若要声称恢复，需要把 teacher/student revision、optimizer/scheduler/scaler、RNG/sampler 和 expected next sample IDs 一起写进 checkpoint bundle。

## 7. OPD 项目映射与真实性边界

本仓库 [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html) 支持以下 local-direct 或 report-supported 事实：

- 五个 expert mix、image-hash split、`target_expert`/`candidate_experts` 和 format metadata；
- coldstart 阶段五教师 `preloaded_zero3`、teacher rollout、full-vocabulary KL；
- online OPD 阶段 student rollout 后，在同一 response 上执行 route-based teacher forward，再做 full-vocab KL；
- 当前 teacher selection 是 route metadata 驱动，不是独立验证的 learned router。

同一 inventory 明确缺少 model weights/optimizer bundle、single-teacher/SFT-only/no-synthetic/synthetic-ratio ablation，并区分旧版 OPD final 与新版 OPD5000 lineage。因此安全回答是：

> “我能讲清五教师 coldstart 与 student-rollout→teacher-KL 的训练链路，并把 route、format 和 evidence gate 写进协议；但当前证据不能证明多教师本身带来全部 uplift，也不能说五教师一定优于单教师。下一步是固定数据和 route，做 single-teacher/multi-teacher matched A/B，再补 teacher/student checkpoint 与显存/latency telemetry。”

| 口径 | 证据等级 | 面试安全表述 |
| --- | --- | --- |
| `preloaded_zero3`、五教师 route、coldstart/online KL | local-direct / report-supported | 训练链路和配置存在 |
| teacher no-grad 减少 autograd memory | primary mechanism | 机制成立；参数/I/O/peak 仍需测 |
| 多教师优于单教师 | unverified | 缺 matched ablation，不能说 |
| route metadata 是 learned router | reject | 当前实现是 metadata-driven selection |
| OPD uplift 全部来自多教师 | reject | 数据配比、coldstart、route、student rollout 等同时变化 |

## 8. 验证伪代码（工程合同，不是 upstream 实现）

```python
def multi_teacher_step(student, teachers, batch, route, cfg):
    # 1. Freeze teacher parameters; only student parameters enter the optimizer.
    freeze_parameters(teachers)
    student_logits = student(batch.inputs)

    # 2. Run routed teachers under no_grad and retain only masked outputs needed for KL.
    teacher_losses = []
    with torch.no_grad():
        for teacher_id in route.teacher_ids:
            logits_t = teachers[teacher_id](batch.inputs)
            teacher_losses.append(masked_kl(student_logits, logits_t,
                                            temperature=cfg.temperature,
                                            reduction=cfg.kl_reduction,
                                            mask=batch.valid_mask))

    # 3. Combine hard labels and explicitly normalized teacher weights.
    loss = cfg.hard_weight * hard_loss(student_logits, batch.labels)
    loss += cfg.kd_weight * weighted_sum(teacher_losses, route.weights)

    # 4. Backprop only through student; record peak memory and timing per route.
    loss.backward()
    optimizer_step(student)
    return record_route_loss_memory_latency(route, teacher_losses)
```

伪代码表达冻结、route、mask、KL 和 student-only backward 的顺序；teacher 的 resident/sequential/staged 实现、FSDP/ZeRO gather、CPU/NVMe staging、异常恢复和具体 API 必须在目标环境中实现与测量。

## 9. Trade-off、bad case 与追问

### 9.1 Trade-off

- all-resident 减少 teacher reload，但可能让 student/optimizer 峰值 OOM。
- sequential 降低 peak，但 teacher latency 和同步次数增加。
- CPU/NVMe staging 扩大容量，但 copy/I/O wait、带宽抖动和 lineage 复杂度增加。
- 更高 temperature 让 soft distribution 更平滑，但有效梯度尺度与 hard/KD 权重必须重新校准。
- 固定 route 简化复现，confidence/learned weighting 可能更灵活，却引入额外校准和 ablation 需求。

### 9.2 高概率 bad case

1. teacher 参数 `requires_grad=False`，却忘记 `no_grad`，仍保留巨大 autograd graph。
2. teacher logits 没有 valid-token mask，padding 或格式 token 污染 KL。
3. PyTorch `kl_div` 的 input/target 方向或 `mean`/`batchmean` 记录错误。
4. 把 route metadata 直接说成 learned router。
5. 用不同 teacher 数量、effective batch 或 route 分布做 A/B，却把 loss/吞吐差异归因于多教师。
6. `load()` 成功就声称 teacher/student、optimizer、RNG 和 sampler 完整恢复。

### 9.3 面试追问顺序

1. teacher 为什么要 `no_grad`，只 `detach` 不够吗？
2. KL 的 input、target、temperature、reduction 和 mask 怎么写？
3. 五个 teacher 是同时常驻还是顺序调用？峰值在哪一刻？
4. route metadata 与 learned router 有什么证据差别？
5. 如何设计 single-teacher/multi-teacher matched A/B？
6. 如果多教师 peak 降了但 p95 latency 翻倍，是否接受？

## 10. 结论与下一步

多教师蒸馏的正确回答是“语义合同 + memory schedule + evidence protocol”三件事同时闭合：先确保 teacher 不更新且不建立无用 graph，再固定 KL/mask/temperature，最后用 resident/sequential/staged 的 matched A/B 和 checkpoint replay 验证。OPD 当前证据能支持五教师训练链路和 route-driven selection，但不足以证明 uplift、learned router 或完整恢复。

当前节点已完成知识页和一张 `unseen` 题卡；仍保持 `WARN`。下一步可进行 ENG-016 一题口述，或补 single-teacher/memory/lineage artifacts；ENG-017 继续后置。

## References

1. Hinton, Vinyals, Dean，[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531)：soft target、temperature 与蒸馏背景。
2. PyTorch 2.13，[`torch.nn.functional.kl_div`](https://docs.pytorch.org/docs/2.13/generated/torch.nn.functional.kl_div.html)：log-probability input、target shape 与 reduction。
3. PyTorch 2.13，[`torch.no_grad`](https://docs.pytorch.org/docs/2.13/generated/torch.no_grad.html)：关闭 gradient calculation 与 memory 边界。
4. PyTorch 2.13，[FSDP](https://docs.pytorch.org/docs/2.13/fsdp.html)：parameter sharding、CPU offload 与 state lifecycle。
5. Microsoft DeepSpeed，[`zero3.rst`](https://github.com/microsoft/DeepSpeed/blob/de1846cf6fbdd6f1c2adf046f319791ca78cc547/docs/code-docs/source/zero3.rst)：ZeRO-3 partition/offload 与 assumptions。
6. 本仓库，[ENG-015 memory/offload source freeze](../sources/vol_05_eng015_activation_offload_source_freeze.html)：显存/step-time/resume 合同。
7. 本仓库，[OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：五教师、route、coldstart、online KL 与 ablation/ownership 缺口。

