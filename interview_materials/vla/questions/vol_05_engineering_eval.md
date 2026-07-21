# VOL 05 Engineering / Evaluation：核心面试题卡（Batch 1）

> 状态：`drafted / cards_10_of_44 / review_warn`  
> 更新日期：2026-07-17  
> 当前题数：10 / 44  
> 覆盖范围：`VLA-ENG-001..008`、`VLA-EVAL-001..002`  
> 难度：L2 8 题 / L3 2 题  
> 优先级：P0 10 题  
> 练习状态：全部 `unseen`  
> 使用方式：先闭卷说 30 秒版本，再展开机制与诊断；未真实口述前不得改为 pass/strong。  
> 深度来源：[VOL 05 Engineering / Evaluation Batch 1 知识页](../knowledge/vol_05_engineering_eval.html)；项目 hook 只沿用五项目 inventory 的证据边界，不因进入题卡而升级。

## A. 数据合同、切分与吞吐

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-001</b> · 一个可训练、可部署的 VLA 数据 schema 至少要冻结哪些字段？</summary>

**面试意图**：判断你是否理解 VLA 样本是带时间、动作语义和来源的合同，而不是只检查 tensor shape。

**30 秒回答**：我会同时冻结 observation、语言/状态、action window、mask、timestamp/control Hz、normalizer，以及 robot/camera/source/schema version。action 还要写清轴序、单位、坐标系、绝对或增量语义；shape 相同不代表能被同一 controller 正确执行。

**机制展开（约 2 分钟）**：样本可写成 `history + goal + proprio -> action window`，但每项都要带语义：相机 key、颜色空间、历史对齐，动作的 horizon/维度/轴序/单位/frame，padding/invalid mask，normalizer 与 provenance。训练入口先做 schema assertion；部署前用逐维唯一的 sentinel action 跑 serialize→parse→denorm→frame/axis mapping→controller adapter。这样能把“模型学错”与字段交换、错帧、错单位或统计量错配分开。

**诊断 / 证据**：保存 schema JSON/version、dataset manifest、normalizer hash 与 roundtrip 输出；抽查 timestamp 单调性、camera/action key、mask 和每维 sentinel。只有 tensor shape 或 formatter pass 不能关闭语义风险。

**项目挂钩**：OpenPiVLA 的 `H=15,D=72` 与 formatter `limit=16` 冲突、RoboCasa official12 action order、UWM normalizer 缺口都可作为真实 bad case；不把它们说成已完成闭环修复。

**追问树**：为什么 schema version 必须进 checkpoint？normalizer 属于数据还是模型？padding mask 错会怎样？同为 7D action 为什么不能直接复用？

**危险答案**：说“shape 对上就能训练和部署”，或默认为所有机器人都使用同一轴序、单位和 gripper 语义。

**来源**：[1][8][10]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-002</b> · VLA 数据应怎样做 split、dedupe 和 leakage audit？</summary>

**面试意图**：检查你能否区分 row、episode/scene/image group、语义指纹与媒体复用等不同泄漏层级。

**30 秒回答**：不能随机按行切。先按 robot/site/scene/episode/image 的最高独立单位构造 group key，再分 train/eval；之后审计 source-line、fingerprint、训练图片与 near duplicate。同图多标注不一定是重复样本，但跨 split 共享内容必须阻断。

**机制展开（约 2 分钟）**：相邻窗口、多标注和增强版本可能 row ID 不同却共享几乎全部信息，所以先保证 train/eval 的 group key 不相交，再在已冻结 split 上做 exact、semantic 与 media dedupe。审计至少输出坏行/schema、group overlap、normalized fingerprint、image/video hash、near duplicate 和 source provenance。去重规则还要保留合法的同图多 object/region 标注；先随机切行再各自去重，会把同一 episode 或图片的近邻留在两侧。

**诊断 / 证据**：输出每层 denominator、overlap count、样本 key 与 source line；对命中项人工抽查，并冻结 split manifest/transform SHA。零 exact duplicate 不等于零 near-duplicate 或零分布泄漏。

**项目挂钩**：OPD raw-holdout 的 source-line、fingerprint、image+prompt+answer 和 train-image gates 是可讲证据；同图多合法标注说明 unique image 少于样本数并不自动等于泄漏。

**追问树**：group key 选 episode 还是 scene？同图多标注如何处理？为什么 split 后去重仍可能泄漏？near duplicate 怎么定阈值？

**危险答案**：说“随机打乱后 8:2 就足够”，或看到重复图片路径就直接判定训练测试泄漏。

**来源**：[1][7]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-003</b> · 怎样定位 VLA 训练吞吐瓶颈，而不是盲目增加 DataLoader workers？</summary>

**面试意图**：判断你能否把 data、compute、communication 和 callback 的时间拆开，用 A/B 证据定位瓶颈。

**30 秒回答**：先拆 step 的 data wait、compute、同步、optimizer 与 callback，记录分位数和 GPU 利用率。依次跑 DataLoader-only、单卡、多卡 timing，再一次只改 workers/prefetch/pin/preload/sampler。prefetch 只能隐藏可并行时间，修不了随机读或内存瓶颈。

**机制展开（约 2 分钟）**：稳态 step 可近似 `max(data, compute)+sync+misc`，但冷启动、epoch boundary 和 checkpoint spike 要另报。DataLoader-only 排除模型，单卡区分数据与 compute，多卡暴露 all-reduce/shard communication；每次 A/B 同时看 p50/p95 wait、CPU 内存、GPU active、samples/tokens/frames per second。workers 增加后若存储争用、decode 饱和或 page cache thrash，吞吐反而下降；preload 也可能用内存换速度。

**诊断 / 证据**：保留阶段 timing trace、硬件/存储、loader config、冷启动与稳态区间；只从 `next(loader)` 变快不能外推 full GPU training 同比例加速。

**项目挂钩**：UWM/LIBERO 的 DataLoader-only A/B 支持 zarr 小 chunk 随机读诊断与 preload 方向，但没有 full training trace，回答时必须保留这一层证据边界。

**追问树**：GPU 利用率低一定是 DataLoader 吗？为什么看 p95？prefetch 何时无效？怎样判断通信而非计算成为瓶颈？

**危险答案**：只说“把 `num_workers` 调大”，或把 DataLoader-only 加速直接写成端到端训练加速。

**来源**：[1][10]　**练习状态**：unseen

</details>

## B. 分布式训练、数值稳定与恢复

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-004</b> · DDP、FSDP 与 ZeRO 分别切分什么，实际如何选择？</summary>

**面试意图**：检查你是否理解复制、分片、通信和 checkpoint 语义，而不是只会说“ZeRO-3 最省显存”。

**30 秒回答**：DDP 每卡复制模型参数并 all-reduce 梯度，optimizer state 通常各 rank 独立持有；ZeRO-1/2/3 依次分片 optimizer、gradient、parameter；FSDP 按 wrap/shard policy 分片三者。选择还要看显存、网络、吞吐及恢复复杂度。

**机制展开（约 2 分钟）**：DDP 简单稳定，适合模型状态能放入单卡；ZeRO-1/2/3 依次切 optimizer、再切 gradient、再切 parameter；FSDP 是 PyTorch-native 的 unit-level all-gather/reduce-scatter。显存账本除参数/梯度/optimizer 外，还包括 activation、temporary buffer、teacher、fragmentation。方案冻结 world size、wrap/shard、precision、activation checkpointing/offload、bucket 与 state-dict 类型，并用 peak memory、step time 和独立 resume test 验收。

**诊断 / 证据**：先单卡测状态与 activation，再逐级启用 sharding；记录 per-rank peak、通信占比、OOM 点、save/load 时间和 world-size reshard。框架机制不等于当前 workload 的性能结论。

**项目挂钩**：OPD 五 teacher `preloaded_zero3` 可说明多模型共存的显存压力；它不证明 ZeRO-3 对所有 VLA workload 最优，也不替代完整 checkpoint bundle。

**追问树**：ZeRO-2 为什么参数仍可能放不下？FSDP wrap policy 影响什么？activation 显存为何没被参数分片解决？怎样保存可部署权重？

**危险答案**：把 FSDP 和 ZeRO-3 说成完全相同实现，或只按“最省显存”选择而不测通信和恢复。

**来源**：[1][2][4][7]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-005</b> · mixed precision、gradient accumulation、clipping 与 effective batch 怎样正确组合？</summary>

**面试意图**：判断你能否说清 optimizer-step 语义、数值顺序和可观察信号，而不是只背一个 batch 公式。

**30 秒回答**：batch≈micro×accum×world，并说明按 sample/token/frame/action 计。micro step 只累积；完成后先 unscale，再算 global grad norm 与 clipping，最后 optimizer/scheduler step。FP16 另看 scale、overflow、skipped step。

**机制展开（约 2 分钟）**：accumulation 改变 optimizer 更新频率，scheduler、logging 和 checkpoint 的 step 定义必须一致；多模态 variable-length 样本即使 sample batch 相同，pixel/token/action workload 也不同。FP16 常靠 dynamic loss scaling，BF16 范围更大但不保证所有算子稳定。若在 unscale 前裁剪，阈值语义会错；分片训练要用框架的 global norm。增大 global batch 还可能需要重调学习率与 warmup，不能只为“等价单卡”。

**诊断 / 证据**：记录 micro/optimizer step、effective workload、loss scale、overflow/skipped、grad norm、clip ratio、LR 与 finite check；比较配置时按相同 optimizer-step 或样本预算对齐。

**项目挂钩**：OPD 的 grad norm、entropy、overlap 和 route loss 可作为训练可观察性 hook；OpenPiVLA 的 eager/MACA 是兼容路径，不代表 mixed precision 已自动稳定。

**追问树**：scheduler 按 micro step 会怎样？BF16 是否完全不需要检查溢出？为什么 clipping 要在 unscale 后？global batch 增大后 LR 是否必然线性放大？

**危险答案**：说“BF16 永远稳定”，或在每个 micro step 都执行 optimizer/scheduler，却仍声称做了梯度累积。

**来源**：[1][3][7][8]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ENG-006</b> · 什么才算可恢复、可审计的 VLA checkpoint bundle？</summary>

**面试意图**：考查你能否区分权重路径、推理候选、训练恢复与评估可追溯性，并给出实际验收步骤。

**30 秒回答**：checkpoint 不只是权重：需绑定源码/config、processor、optimizer/scheduler/scaler、step、RNG、data cursor、dataset/normalizer/schema 与 SHA。独立进程加载后，复现固定 batch 输出、续训一步，再跑同协议 eval smoke。

**机制展开（约 2 分钟）**：权重+processor+normalizer 可形成 inference candidate，但无 optimizer/scheduler/scaler 不能无缝续训；无 RNG、sampler 与 data cursor，样本顺序和增强会漂移。分布式保存还要说明 full/sharded state dict、rank ownership、world-size reshard 与原子完成。验收流程是在 step k 保存，独立进程校验 hash，对固定 batch 比较 pre/post-load 输出，继续一步检查 finite loss/grad/step，再用同一 harness 跑最小 eval smoke。

**诊断 / 证据**：保留 manifest、SHA、保存成功标记、load stdout、固定 batch diff、resume step 与 eval smoke；“远端有一个路径”或“报告写完成”都不是 checkpoint-verified。

**项目挂钩**：OpenPiVLA remote path 缺本地 checkpoint/load smoke，UWM 5-task final 缺 raw bundle；它们适合说明 lineage gap，不应在题卡中升级为已验证模型资产。

**追问树**：为什么只保存 RNG 仍不够？processor/normalizer 为什么要跟权重绑定？sharded checkpoint 如何跨 world size？怎样防止半写入 checkpoint 被加载？

**危险答案**：说“保存 `model.pt` 就能完全 resume”，或把文件存在、能下载与能重放评估视为同一证据等级。

**来源**：[1][2][8][10][12]　**练习状态**：unseen

</details>

## C. Policy Serving 与动作执行

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-007</b> · policy server 的 latency budget 如何影响 action chunk 与 replan？</summary>

**面试意图**：检查你能否把端到端 tail latency、控制周期和开闭环 trade-off 连起来，而不是只报模型推理耗时。

**30 秒回答**：预算要覆盖 sense、preprocess、queue、infer、network、decode 和 control，不是只有 GPU time。若每次预测 H 步、执行 K 步、周期为 Δt，最好让端到端延迟小于 `KΔt` 并留 jitter/timeout 余量。K 大能掩盖慢推理但更开环，K 小纠偏快却增加请求与算力压力。

**机制展开（约 2 分钟）**：server 要记录 sensor timestamp、queue depth、request/episode correlation ID、模型/processor 版本、p50/p95/p99、chunk age 与 valid horizon。动态 batching 可提高吞吐却增加排队；网络抖动或 stale observation 会让平均延迟正常但错过 deadline。执行当前子块时可异步请求下一块，但必须定义过期、乱序、取消、fallback 和安全 stop；不能用旧 action 填满空窗而无告警。

**诊断 / 证据**：分别压测 ingest、queue、inference、network、decode 和 controller，报告 deadline miss、drop、stale chunk 与尾延迟；对 K/replan 做 same-task A/B，同时看 success 与安全事件。

**项目挂钩**：Harness 的 cancel/compensation 与 OpenPiVLA 的 action/controller roundtrip 缺口可作为追问；当前证据不能证明真实机器人 latency 或 safety 已闭环。

**追问树**：为什么平均 latency 不够？动态 batching 的风险？K=H 有什么问题？timeout 后应该 stop、hold 还是 fallback？

**危险答案**：只报模型 forward 毫秒数就称达到控制频率，或认为增大 chunk 永远能解决延迟。

**来源**：[1][8][9]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-ENG-008</b> · 模型 action 到 controller 之间需要怎样的 deployment contract？</summary>

**面试意图**：考查你能否把 parser、denormalization、坐标变换、安全限制与 acknowledgement 做成逐维可验证的接口。

**30 秒回答**：链路为 parse/shape→denorm→axis/unit/frame→absolute/delta→limits→controller→ack。请求带 schema、checkpoint、normalizer、轴序、单位、frame、H/K、Hz 和有效期；禁用 silent default，并以逐维 sentinel 做 roundtrip。

**机制展开（约 2 分钟）**：模型数值本身不具备可执行语义，adapter 必须把训练合同显式映射到 controller。用 `0.01,0.02,...` 的 sentinel action 跑 serialize→parse→denorm→坐标/轴变换→adapter，逐维检查位置、符号、单位与饱和；再测试 NaN、缺维、额外字段、旧 schema、过期时间、乱序和取消。controller 的 accepted/rejected、实际 command、clipping 与 stop reason 要回写同一 correlation ID，才能找 first failure。

**诊断 / 证据**：保存 contract schema、golden roundtrip、每维误差、异常输入结果、controller ack 与 observation feedback；offline action metric 不能代替这条执行链。

**项目挂钩**：RoboCasa official12 action order、OpenPiVLA formatter shape 冲突和 Harness schema-aware runtime 是可用 hook；不把 browser/sandbox tool success 说成真实 controller success。

**追问树**：为什么 clip 不能静默？绝对与增量动作如何测试？frame 变换错一轴会怎样？controller 拒绝后 episode 应如何记账？

**危险答案**：认为 parser 能输出浮点列表就代表部署完成，或让 normalizer、单位与坐标系使用未记录默认值。

**来源**：[1][8][9][10]　**练习状态**：unseen

</details>

## D. Closed-loop 评估与 First-Failure

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-001</b> · 怎样把 closed-loop 评估协议写成可重放、可比较的合同？</summary>

**面试意图**：判断你是否会冻结模型、环境、初态、执行与判定全链路，而不是把“strict”当形容词。

**30 秒回答**：冻结 task/env、init/warmup、obs、action/normalizer、chunk、controller/Hz、horizon、success、seed/trials、checkpoint/runtime。manifest 绑代码/资产 SHA；episode record 留输出、command、终止与 first failure。

**机制展开（约 2 分钟）**：同一任务名不代表协议相同。比较模型时先 diff protocol tuple，关键字段一致后才优先归因 checkpoint；A/B 复用相同 task/init/seed 做 paired eval。每个 run 保存 repo/config/checkpoint/processor/normalizer/environment/scorer 版本和 launcher；每个 episode 是 immutable record，保留成功分母、invalid/timeout 规则与原始 trace。聚合时同时报总数、per-task、置信区间和 failure distribution，不能只留一个 macro average。

**诊断 / 证据**：先做 manifest diff 和缺失字段 gate，再核对 episode denominator、seed/init coverage、success predicate 与 raw trace；协议不一致时只报告不同 setting，不做模型排名。

**项目挂钩**：UWM fixed-pruned-init 的 0.744、Table II OOD 的 0.79、reset-style diagnostic 的 0.928 使用不同协议，必须分层叙述，不能直接比较。

**追问树**：为什么 warmup 与 horizon 都要冻结？paired eval 有什么价值？invalid episode 是否可删除？macro 与 micro 何时不同？

**危险答案**：说“都是 LIBERO、都是 50 rollouts，所以可以直接比较”，或只保存 aggregate success rate。

**来源**：[1][5][10]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-EVAL-002</b> · offline proxy 到真机 success 的 metric ladder 如何划分？闭环失败怎样找 first failure？</summary>

**面试意图**：检查你能否限制不同指标的证据范围，并沿时间把失败路由到正确 owner。

**30 秒回答**：指标分 training、offline action、format/geometry、world proxy、sim/robot closed-loop；低层不能外推高层。失败时沿 obs→decode→parser/normalizer→network→controller→environment→predicate 找首个偏差，再定 owner。

**机制展开（约 2 分钟）**：loss/grad 证明优化在运行；MSE/NLL 证明 demonstration split 上拟合；format/IoU/Hit@K 证明接口或 grounding；world proxy 证明特定 scorer 下未来预测；sim/robot success 只在冻结协议和硬件范围内成立。调试时用同一 correlation ID 对齐 raw observation、prediction、denorm action、queue、controller ack、transition 与 scorer。第一处合同破坏决定数据/模型/serving/controller/environment/evaluator owner，后续失败只是传播结果。

**诊断 / 证据**：固定 checkpoint 改 protocol、固定 protocol 改 checkpoint、固定输入重放 parser/controller、固定动作比较 environment transition，并保存 raw episode 与 paired diff。

**项目挂钩**：OPD point protocol mismatch、Harness proxy/safety 边界、UWM 三种协议和 WAM raw-artifact 缺口分别位于 ladder 的不同层，不应合并成机器人成功结论。

**追问树**：tool accuracy 能证明什么？sim success 为什么不等于真机？normalizer 错时谁是 owner？action trace 正确但 success predicate 错该修哪里？

**危险答案**：看到 loss 或 proxy 变好就声称机器人能力提升，或从“抓取失败”直接反推 backbone 不够强。

**来源**：[1][5][6][7][9][10]　**练习状态**：unseen

</details>

## 参考来源

1. [VOL 05 Engineering / Evaluation Batch 1 知识页](../knowledge/vol_05_engineering_eval.html)；canonical [Markdown](../knowledge/vol_05_engineering_eval.md)。
2. PyTorch official documentation, [FullyShardedDataParallel](https://pytorch.org/docs/stable/fsdp.html)。
3. PyTorch official documentation, [Automatic Mixed Precision](https://pytorch.org/docs/stable/amp.html)。
4. Microsoft DeepSpeed official documentation, [ZeRO](https://www.deepspeed.ai/tutorials/zero/)。
5. [VOL 04 Benchmark / Evidence Source Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)：LIBERO/UWM/Cosmos protocol tuple 与可比性。
6. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：raw artifact 和 metric provenance 缺口。
7. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：data routing、raw-holdout、point protocol 与 checkpoint selection。
8. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：checkpoint lineage、action representation 与 parser/controller 缺口。
9. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：runtime、cancel/compensation、proxy/safety/browser 边界。
10. [UWM / LIBERO Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：fixed-pruned-init/reset/Table II、normalizer、stall 与 RoboCasa boundary。
11. PyTorch official documentation, [DistributedDataParallel](https://pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)。
12. PyTorch official documentation, [Distributed Checkpoint](https://pytorch.org/docs/stable/distributed.checkpoint.html)。
