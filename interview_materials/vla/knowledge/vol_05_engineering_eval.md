# VOL 05 Engineering / Evaluation：数据、训练、部署与闭环诊断（Batch 1）

> 状态：`drafted / knowledge_10_of_44 / cards_10_of_44_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前覆盖：`VLA-ENG-001..008`、`VLA-EVAL-001..002`，10/44 个知识节点  
> 当前目标：把数据合同、分布式训练、checkpoint lineage、policy serving、closed-loop protocol 和 first-failure debugging 连成可恢复的工程闭环。  
> 项目边界：本文只使用五项目 inventory 中已冻结的机制与风险；项目数字不会因为进入知识页而升级证据等级。

## 问题（Question）

Batch 1 回答 10 个依赖关系明确的问题：

1. `VLA-ENG-001`：VLA 数据 schema 为什么必须同时描述 observation、action、时间和语义？
2. `VLA-ENG-002`：怎样做 split、dedupe 和 leakage audit，避免同场景或同图片跨集合？
3. `VLA-ENG-003`：DataLoader、预处理、GPU 计算和同步怎样共同决定吞吐？
4. `VLA-ENG-004`：DDP、FSDP 与 ZeRO 分别切分什么，如何选择？
5. `VLA-ENG-005`：mixed precision、gradient accumulation、clipping 和 effective batch 怎样交互？
6. `VLA-ENG-006`：一个可恢复、可审计的 checkpoint bundle 至少包含什么？
7. `VLA-ENG-007`：policy server 的 latency budget 如何影响控制频率、chunk 和 replan？
8. `VLA-ENG-008`：模型 action 输出到 controller 之间需要怎样的 deployment contract？
9. `VLA-EVAL-001`：closed-loop 评估为什么必须冻结 protocol tuple 和 artifact lineage？
10. `VLA-EVAL-002`：offline proxy、format、geometry、sim success 与真机 success 怎样组成 metric ladder，并用 first failure 调试？

这 10 个节点组成以下链路：

```text
dataset schema + temporal/action semantics
  -> grouped split / dedupe / leakage audit
  -> dataloader / preprocessing / device pipeline
  -> DDP/FSDP/ZeRO + precision/accumulation
  -> checkpoint + optimizer + processor + data lineage
  -> policy server + action/controller contract
  -> frozen closed-loop protocol
  -> metric ladder + first-failure trace
  -> data / model / runtime / controller / evaluator owner
```

## 知识地图位置与边界

### 前置知识

- VOL 01：tensor shape、数值稳定性、坐标系、控制频率与统计估计。
- VOL 02：SFT/RL 数据合同、distribution shift、reward 与 offline/online 指标。
- VOL 03：action representation、normalization、chunk、replan 和 controller boundary。
- VOL 04：world-model proxy、strict protocol、Sim2Real 与 benchmark 可比性。
- VOL 07：五项目 claim–evidence inventory 提供真实工程 bad cases，但不替代通用方法来源。[6][7][8][9][10]

### 当前批次不做什么

1. 不把某个框架写成所有训练的唯一答案；DDP/FSDP/ZeRO 的选择依赖模型、网络、显存和保存需求。
2. 不把 reproducibility 写成“固定随机种子即可”；kernel、数据顺序、环境和外部 simulator 同样属于合同。[11]
3. 不把离线 loss、tool-call accuracy、format pass 或 world-model proxy 外推为机器人闭环成功。
4. 不展开 `VLA-ENG-009..022` 与 `VLA-EVAL-003..022`；它们属于后续 data-scale、observability、serving、safety、统计与 deployment batches。
5. 当前题卡只覆盖这 10 个知识节点；其余 34 个节点仍为 planned，所有练习状态以主索引为准。

## VLA-ENG-001：先冻结数据 Schema，再谈训练

### 最小样本合同

一个 VLA 训练样本不只是 `image + text + action`。至少应明确：

\[
x_i = \left(o_{t-h+1:t},\; g,\; s_t,\; a_{t:t+H-1},\; m,\; \tau,\; \mu,\; \sigma\right).
\]

变量解释：(o) 是一个或多个相机/历史观测，(g) 是语言或任务条件，(s) 是可选 proprio/state，(a) 是动作窗口，(m) 是 padding/valid mask，(	au) 是时间戳/控制频率，(mu,sigma) 表示动作归一化统计。实现上还要记录 dataset/source/episode/robot/camera/action-space/schema-version 等 metadata。

| 合同维度 | 必须回答 | 常见 silent bug |
| --- | --- | --- |
| observation | camera key、分辨率、颜色空间、历史长度、时间对齐 | wrist/base view 交换，RGB/BGR 混用，重复最后帧 |
| action | shape、轴序、单位、绝对/增量、关节/EEF、gripper 语义 | 同为 7D/12D 但维度意义不同 |
| time | observation/action timestamp、control Hz、window stride | 图像和动作错一帧，训练看似收敛但执行滞后 |
| normalization | per-dataset/per-robot stats、clip、denorm | checkpoint 配错 normalizer，动作系统性过冲 |
| mask | padding、invalid step、missing modality | padding 被当真动作，aux loss 污染主任务 |
| provenance | dataset version、episode/group key、transform SHA | 无法复现 split 或追踪异常样本 |

### 实现前置检查

```python
def validate_vla_row(row, schema):
    assert set(row["observations"]) == set(schema.camera_keys)
    assert row["actions"].shape == (schema.horizon, schema.action_dim)
    assert row["valid_mask"].shape == (schema.horizon,)
    assert row["action_space"] == schema.action_space
    assert row["axis_order"] == schema.axis_order
    assert row["unit"] == schema.unit
    assert row["normalizer_id"] == schema.normalizer_id
    assert monotonic(row["timestamps"])
```

**项目映射**：OpenPiVLA 的 `H=15,D=72` 与 formatter `limit=16`、RoboCasa official12 action order、UWM checkpoint/normalizer 都说明“shape 对上”不等于动作语义闭合。[8][10]

## VLA-ENG-002：Split、Dedupe 与 Leakage 是分层问题

### 为什么随机按行切分不够

机器人数据高度相关：同一 episode 的相邻窗口、同一场景的多标注、同一图片的多个 box、同一路径的增强版本可能具有不同 row ID，却共享几乎全部信息。安全 split 应优先按最上层独立单位分组：

```text
robot / site / scene / episode / image identity
  -> group key
  -> train / validation / test assignment
  -> row-level transforms inside the assigned split
```

若 \(G(x_i)\) 是样本的 group key，则基本约束是：

\[
G(\mathcal D_{train}) \cap G(\mathcal D_{eval}) = \varnothing.
\]

这只是必要条件。还应检查 source-line、内容 fingerprint、image hash、prompt-answer-image key、near duplicate 和训练图片集合。OPD raw-holdout 同时冻结了 source-line、fingerprint、image+prompt+answer 与 train-image gates；它也保留同图不同合法标注，因此“重复图片”与“重复样本”不能混为一谈。[7]

### Audit 输出

| 层级 | 推荐输出 | 解释 |
| --- | --- | --- |
| row | bad JSON、exact duplicate、schema violation | 文件级完整性 |
| group | episode/scene/image overlap | 独立性主门槛 |
| semantic | normalized prompt/action fingerprint | 重写或增强后的近重复 |
| media | image/video hash、near-duplicate embedding | 媒体复用与裁剪风险 |
| provenance | source file/line、transform/version | 可追溯性 |

**危险做法**：先随机行切分，再在每个 split 中独立去重；这样同一 episode/图片的近邻可能已泄漏到两边。

## VLA-ENG-003：吞吐是流水线最慢阶段的函数

### Step 时间分解

一个训练 step 可粗略写成：

\[
T_{step} \approx \max(T_{data},T_{compute}) + T_{sync} + T_{misc}.
\]

其中 \(T_{data}\) 包含存储读取、decode、augmentation、collate 和 host→device；\(T_{compute}\) 包含 forward/backward/optimizer；\(T_{sync}\) 是梯度或参数通信；\(T_{misc}\) 包含 logging、checkpoint、eval callback。prefetch 只能隐藏可并行的数据时间，不能消除磁盘随机读、epoch boundary 或内存不足。

### 诊断顺序

1. DataLoader-only benchmark：不建模型，测 `next(loader)` wait 分布。
2. 单卡 no-sync GPU smoke：区分 compute 与数据。
3. 多卡 step timing：记录 data_wait、forward/backward、all-reduce、optimizer、checkpoint。
4. 改一个变量做 A/B：workers、prefetch、persistent、pin、preload、chunk size、sampler。
5. 同时报告冷启动时间、CPU 内存、GPU 利用率与稳态吞吐。

UWM/LIBERO 的 DataLoader-only A/B 中，finite/infinite 的 p95 wait 都约 13s，preload+infinite 后约 0.19s；这支持 zarr 小 chunk 随机读的诊断，但不能直接宣称 full GPU training 已同比加速。[10]

## VLA-ENG-004：DDP、FSDP 与 ZeRO 切分的对象不同

| 方法 | 每卡保留 | 通信主路径 | 适合情况 | 主要风险 |
| --- | --- | --- | --- | --- |
| DDP | 完整参数、梯度；optimizer state 通常由各 rank 独立持有 | backward all-reduce gradient | 模型能单卡装下、追求简单稳定 | 显存随模型增大，optimizer state 重复 |
| ZeRO-1 | 参数/梯度完整，切 optimizer state | optimizer state partition | optimizer state 是主要压力 | 框架 checkpoint/恢复语义更复杂 |
| ZeRO-2 | 参数完整，切 optimizer state + gradient | reduce-scatter/all-gather | 模型参数可装下，梯度压力大 | 通信与 bucket 配置敏感 |
| ZeRO-3 | 参数、梯度、optimizer state 都切分 | layer-wise all-gather/reduce-scatter | 单卡装不下完整模型 | 通信/保存/加载复杂，外部模型共存更难 |
| FSDP | 参数/梯度/optimizer state 按 shard policy | unit-level all-gather/reduce-scatter | PyTorch-native sharding、可配置 wrap | wrap policy、state-dict 类型和 tied weights |

DDP 的核心语义是各 rank 复制模型、对梯度同步；FSDP/ZeRO-3 在执行层附近聚合分片参数。不能只按“哪个更省显存”选择，还要冻结：world size、shard/wrap policy、precision、activation checkpointing、offload、通信 bucket、save/load state dict 与 resume test。[1][2][4]

> 复核注：DDP 文档直接保证 replica、gradient all-reduce 与输入不自动 shard；“optimizer state 重复”是每进程 optimizer 的常见实现推论，不是 DDP 通信 API 单独保证的对象。详见 [VOL 05 Batch 1 独立官方文档复核](../sources/vol_05_batch1_independent_fact_review.html)。

### 粗略显存账本

设参数量为 \(P\)，每参数权重、梯度、optimizer state 分别占 \((b_w,b_g,b_o)\) bytes，未分片训练状态近似：

\[
M_{state} \approx P(b_w+b_g+b_o).
\]

实际显存还包括 activation、temporary buffer、KV/cache、teacher models、fragmentation 和 framework overhead；因此参数账本不能替代实测峰值。OPD 五 teacher `preloaded_zero3` 是“多个教师共存+分片”的项目例子，但不证明 ZeRO-3 对所有 VLA workload 最优。[7]

## VLA-ENG-005：Mixed Precision、Accumulation 与 Clipping

### Effective batch

若每卡 micro batch 为 \(B_\mu\)，梯度累积步数为 \(A\)，world size 为 \(W\)，则全局 batch 近似：

\[
B_{global}=B_\mu \times A \times W.
\]

还必须说明这是 sample、sequence、frame 还是 token 数；多模态样本长度差异大时，同一个 sample batch 的实际 token/pixel/action workload 可能相差很大。

### 精度与稳定性合同

- FP16 通常需要 dynamic loss scaling 保护小梯度；BF16 exponent 范围更大，但并不保证所有算子稳定。[3]
- accumulation 前应按框架语义正确缩放 loss；scheduler/optimizer step 频率必须按 optimizer step 而非 micro step 解释。
- gradient clipping 应在 unscale 后、optimizer step 前执行；分片训练要使用框架提供的 global norm 语义。
- 日志至少记录 loss、grad norm、scale、overflow/skipped step、learning rate、effective batch、tokens/frames per step。

**项目映射**：OPD report 记录 grad norm、entropy、overlap 与 route loss；OpenPiVLA 的 eager/MACA 属于兼容性路径，不等于 mixed precision 自动稳定。[7][8]

## VLA-ENG-006：Checkpoint 不是一个 `models.pt` 路径

### 可恢复 bundle

最小 checkpoint lineage 应绑定：

```text
run_id + git/source SHA + config/CLI/env
  + base model / adapter / processor
  + model state + optimizer + scheduler + scaler
  + global step / epoch / sampler RNG / data cursor
  + dataset manifest + normalizer + schema
  + checkpoint hash + load-smoke stdout
  + eval harness/scorer/protocol + raw predictions/episodes
```

只保存模型权重可以做 inference candidate，却不能保证训练无缝 resume；只保存 optimizer 而缺 sampler/data cursor，恢复后的样本顺序和随机增强仍会变化。分布式 checkpoint 还要明确 full/sharded state dict、world-size reshard、rank ownership 和原子完成标记。[2][4][12]

### Resume 验收

1. 在 step (k) 保存，独立进程加载；
2. 校验参数/processor/normalizer/config hash；
3. 对固定 batch 比较 pre-save 与 post-load 输出；
4. 继续至少一个 optimizer step，检查 finite loss/grad 与 step 递增；
5. 用同 eval harness 跑最小 smoke。

OpenPiVLA 的 remote path 无本地 checkpoint/load smoke、UWM 5-task final 无 raw checkpoint bundle，正说明“报告完成”与“lineage verified”是不同证据等级。[8][10]

## VLA-ENG-007：Policy Server 的 Latency Budget

### 端到端延迟

\[
T_{loop}=T_{sense}+T_{pre}+T_{queue}+T_{infer}+T_{network}+T_{decode}+T_{control}.
\]

若每次请求输出 \(H\) 步、实际执行 \(K\le H\) 步，控制周期为 \(\Delta t\)，策略最好满足：

\[
T_{loop} < K\Delta t
\]

才能在执行完当前子块前得到下一次决策。更严格的闭环还要预留 jitter、timeout 和安全 stop。提升 (K) 可以容忍更大推理延迟，却增加开环误差；减小 (K) 提高纠偏频率，却增加 server/网络/推理负载。

### 服务端必须记录

| 层 | 指标 | 失败模式 |
| --- | --- | --- |
| ingest | sensor timestamp、queue depth、drop rate | stale observation、拥塞 |
| inference | batch size、model/processor version、p50/p95/p99 | tail latency、OOM、动态 batching 抖动 |
| action | chunk age、valid horizon、decode/denorm time | 执行过期动作、维度/单位错误 |
| controller | accepted/rejected、saturation、stop reason | 控制器拒绝或裁剪模型动作 |
| episode | request/action/observation correlation ID | 无法定位 first failure |

Harness 的 cancel/compensation、OpenPiVLA 的 action/controller roundtrip 缺口可直接作为 latency 与执行语义的项目追问。[8][9]

## VLA-ENG-008：Action → Controller Deployment Contract

模型输出到控制器之间至少需要以下握手：

```text
model output
  -> parser / format validation
  -> action tensor shape check
  -> denormalization
  -> axis/order/unit transform
  -> absolute/delta integration
  -> clipping / rate / workspace limits
  -> controller command
  -> acknowledgement / observation feedback
```

合同字段包括：`schema_version`、`model/checkpoint`、`normalizer_id`、`action_space`、`axis_order`、`unit`、`frame`、`horizon`、`execution_steps`、`control_hz`、`timestamp`、`valid_until`。任何 silent default 都可能让 offline prediction 看起来正确、closed-loop 却完全失败。

### Roundtrip 测试

用 sentinel action 对每个维度赋唯一值：

\[
a=[0.01,0.02,\dots,0.01D].
\]

依次通过 serialize→parse→denorm→frame/axis mapping→controller adapter，再检查每一维的位置、符号、单位和饱和。还要测试 NaN、缺维、额外字段、旧 schema、过期 timestamp 和取消。RoboCasa action order、OpenPiVLA formatter shape 冲突、Harness schema-aware runtime 都是该节点的真实 hook。[8][9][10]

## VLA-EVAL-001：Closed-Loop Protocol 是可重放 Tuple

“strict”不是形容词，而是一组可核对字段：

\[
\Pi=(task,env,init,warmup,obs,action,normalizer,chunk,controller,horizon,success,seed,trials,checkpoint,runtime).
\]

只有关键字段一致，成功率差异才主要能归因于模型；任务名相同不等于 protocol 相同。UWM fixed-pruned-init、UWM Table II OOD 和 repo reset-style 使用不同 init/seed/环境设置，所以 0.744、0.79、0.928 不能直接排成模型榜单。[5][10]

### Run / Episode manifest

每个 run 保存：repo/config/checkpoint/processor/normalizer SHA、environment commit、task list、protocol tuple、launcher CLI、机器/依赖和 scorer。每个 episode 保存：episode ID、seed/init index、observation/action timestamps、模型输出、controller command、success/termination、视频/trace path 和 first failure。

成功率估计：

\[
\hat p=\frac{1}{N}\sum_{i=1}^{N}\mathbf 1[success_i].
\]

若比较两个策略，优先在相同 init/seed 上做 paired eval，并同时报告分母、per-task、置信区间和 failure distribution；只报 macro average 会隐藏任务难度差异。

## VLA-EVAL-002：Metric Ladder 与 First-Failure Debugging

### 指标层级

| 层级 | 例子 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| training | loss、grad norm、entropy | 优化是否运行、数值是否异常 | 策略能完成任务 |
| offline action | MSE、NLL、token/format exact | demonstration distribution 上的拟合 | closed-loop recovery |
| semantic/geometry | tool schema、box IoU、point Hit@K | 接口/grounding 子能力 | 控制器/环境成功 |
| world-model proxy | open-loop prediction、VLM score | 未来预测/语义一致性 | 可执行因果与真实 success |
| simulator closed-loop | environment binary success | 指定 simulator/protocol 下成功 | 真机泛化、不同 protocol |
| robot closed-loop | task success、safety/latency | 指定硬件/场景的部署结果 | 所有地点/机器人泛化 |

### First-failure trace

不要从最终失败反向猜一个故事；按时间找第一个合同被破坏的位置：

```text
data / observation
  -> perception / grounding
  -> model decode
  -> parser / normalizer / action mapping
  -> network / queue / timeout
  -> controller acceptance
  -> environment transition
  -> success predicate / logging
```

第一处偏差决定主要 owner：数据/感知、模型、serving、controller、environment 或 evaluator。若第一处错误是 normalizer，后面的“抓取失败”只是后果；若 action trace 正确但 success predicate 错，训练模型没有意义。

### 最小诊断矩阵

1. 固定 checkpoint，变化 protocol：检测 eval confound。
2. 固定 protocol，变化 checkpoint：做真正模型比较。
3. 固定输入，重放 parser/denorm/controller：检测 deployment contract。
4. 固定动作，比较 simulator/robot transition：检测 environment gap。
5. 保留 raw sample/episode 与 paired diff：避免只看 aggregate。

OPD 的 point protocol mismatch、Harness 的 proxy/safety/browser 边界、UWM 的 reset/fixed/Table II 分层和 WAM 的 raw-artifact 缺口分别对应 ladder 中不同断点。[6][7][9][10]

## Batch 1 复习表

| ID | 30 秒抓手 | 必须追问的证据 |
| --- | --- | --- |
| `VLA-ENG-001` | schema 不只写 shape，还写轴序、单位、时间、normalizer | schema/version + sentinel roundtrip |
| `VLA-ENG-002` | 按 episode/scene/image group split，再做多层 dedupe | overlap/fingerprint/image audit |
| `VLA-ENG-003` | step 时间由 data、compute、sync、misc 共同决定 | 分阶段 timing + A/B |
| `VLA-ENG-004` | DDP 复制；FSDP/ZeRO 分片对象与保存语义不同 | world/wrap/shard/state-dict |
| `VLA-ENG-005` | global batch=micro×accum×world；精度和 clipping 有顺序 | scale/overflow/grad norm/step |
| `VLA-ENG-006` | checkpoint 是可恢复 lineage，不是路径 | optimizer/scheduler/RNG/data cursor/load smoke |
| `VLA-ENG-007` | latency budget 决定 chunk/replan trade-off | p95/p99、queue、chunk age |
| `VLA-ENG-008` | action 到 controller 必须逐维可验证 | normalizer/axis/unit/frame/expiry |
| `VLA-EVAL-001` | protocol 是 tuple；同任务不等于可比 | init/warmup/horizon/success/seed/checkpoint |
| `VLA-EVAL-002` | metric 有层级；沿时间找 first failure | raw episode + paired diff |

## 证据与真实性边界

| 类型 | 本批使用方式 |
| --- | --- |
| 官方文档/仓库 | 支持 DDP/FSDP/AMP/ZeRO/checkpoint 与 LIBERO protocol 的机制事实 |
| 本地 source audit | 支持 UWM/LIBERO protocol、UWM architecture 和项目数字不可比性 |
| 项目 inventory | 提供 schema、lineage、protocol、latency、proxy 和 ownership 的真实 bad case |
| 推断 | 只用于提出诊断假设，必须给 paired test 或缺失 artifact |

当前 review 保持 `WARN`：DDP/FSDP/ZeRO/AMP/DCP/Reproducibility 的官方机制已完成独立复核，但本地 workload artifacts、resume/performance smoke 和候选人口述仍缺失；HTML 生成或 source review 不等于 drilled。

## References

1. PyTorch official documentation, `DistributedDataParallel`. [Docs](https://pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)
2. PyTorch official documentation, `FullyShardedDataParallel`. [Docs](https://pytorch.org/docs/stable/fsdp.html)
3. PyTorch official documentation, Automatic Mixed Precision. [Docs](https://pytorch.org/docs/stable/amp.html)
4. Microsoft DeepSpeed official documentation, ZeRO. [Docs](https://www.deepspeed.ai/tutorials/zero/)
5. [VOL 04 Benchmark / Evidence Source Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)：LIBERO/UWM/Cosmos protocol tuple 与可比性。
6. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：raw artifact 和 metric provenance 缺口。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：data routing、raw-holdout、point protocol 与 checkpoint selection。
8. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：checkpoint lineage、action representation 与 parser/controller 缺口。
9. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：runtime、cancel/compensation、proxy/safety/browser 边界。
10. [UWM / LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：fixed-pruned-init/reset/Table II、normalizer、stall 与 RoboCasa boundary。
11. PyTorch official documentation, Reproducibility. [Docs](https://pytorch.org/docs/stable/notes/randomness.html)
12. PyTorch official documentation, Distributed Checkpoint. [Docs](https://pytorch.org/docs/stable/distributed.checkpoint.html)
13. [VOL 05 Batch 1 独立官方文档事实复核](../sources/vol_05_batch1_independent_fact_review.html)；版本化 PyTorch 2.13 与 DeepSpeed ZeRO tutorial 的逐条核对。
