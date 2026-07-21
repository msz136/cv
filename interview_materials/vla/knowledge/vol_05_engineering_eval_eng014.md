# VOL 05 Engineering / Evaluation：CUDA / MACA / ROCm 兼容性与算子验证（ENG-014）

> 状态：`drafted / knowledge_16_of_44 / cards_15_of_44_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-014`；来源已冻结，题卡继续后置。  
> 来源入口：[ENG-014 Hardware / Operator Compatibility Source Freeze](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html)。  
> 核心边界：`torch.cuda` API 能调用、driver compatibility 或 eager fallback 只证明某一层；不自动证明第三方算子、通信、数值、性能或 VLA 闭环等价。

## 问题（Question）

`VLA-ENG-014`：VLA 训练或部署从 CUDA 迁移到 MACA、ROCm 等后，怎样判断“能运行”与“算子/数值/性能兼容”？

面试中不要把兼容性回答成一个布尔值。我会先定位通过了哪一层，再说明下一层仍缺什么 artifact：device/runtime、framework/build、operator/kernel、communication、numerical/runtime、workload/eval。

## 知识地图位置与前置依赖

```text
device/runtime → framework/build → operator/kernel → communication
       → numerical/runtime → VLA data/checkpoint/controller/eval
```

前置：

- `VLA-ENG-003` 的 DataLoader/preprocess/GPU/sync 吞吐分解。
- `VLA-ENG-004..006` 的 DDP/FSDP/ZeRO、AMP、checkpoint/load smoke 合同。
- `VLA-ENG-007..008` 的 policy server、action parser、denorm、frame/controller contract。
- ENG-014 source freeze 中的 PyTorch 2.13 CUDA/HIP/extension、ROCm matrix、NVIDIA Compatibility、MetaX mcPytorch/mcTriton 来源。

## 1. 短答：为什么“能启动”不等于“兼容”

**30 秒回答**：我把迁移拆成六层：先确认 device/runtime 和 PyTorch build，再逐个验证目标 operator 的 forward/backward、dtype、shape、layout；之后验证 DDP/FSDP 所需通信，做同步后的数值 parity 和 p50/p95 latency，最后检查 checkpoint、action parser、denorm、controller 与闭环 eval 是否仍是同一合同。PyTorch HIP 复用 `torch.cuda` 接口能降低 Python 层改动，但不保证 CUDA extension、Triton、FlashAttention 或 MACA custom kernel 自动等价。OpenPiVLA 的 eager/MACA 证据目前只支持稳定性和可诊断 call graph，不能说性能 uplift。

## 2. 六层兼容性合同

### 2.1 直觉

把 VLA 从 CUDA 搬到另一个后端，像把机器人产线搬到另一座工厂：Python API 是操作台，下面还有驱动、编译器、kernel、通信和验收流程。操作台能打开，只说明入口存在；不说明每个按钮、速度和成品质量都一样。

### 2.2 层次、失败模式与证据

| 层 | 面试要问 | 典型失败 | 最小证据 |
| --- | --- | --- | --- |
| L0 device/runtime | 设备、driver、runtime、共享库是否匹配？ | `is_available=False`、动态库缺失、容器看不到设备 | 环境 manifest、device query、版本打印 |
| L1 framework/build | wheel/build 是否针对该 backend？ | CUDA wheel 与 MACA/ROCm runtime 不匹配；Python/framework 不在支持矩阵 | `torch.__version__`、backend version、安装来源 |
| L2 operator/kernel | op 是否注册且覆盖 forward/backward、dtype、shape、layout？ | attention、量化、稀疏或 custom extension 缺失/fallback | op matrix、编译日志、forward/backward smoke |
| L3 communication | DDP/FSDP/ZeRO 所需 collective 是否可用且语义一致？ | collective backend unavailable、all-reduce 失败、rank 不同步 | process-group init、collective parity、rank 日志 |
| L4 numerical/runtime | 精度、随机性、stream、同步、内存行为能否接受？ | FP16/BF16 overflow、未同步计时、跨 stream 竞态 | reference parity、grad check、同步计时 |
| L5 workload/eval | VLA 数据、权重、parser、controller、闭环协议是否一致？ | 训练能跑但动作轴序/单位/反归一化错误 | lineage、eval manifest、rollout trace |

这六层是工程验证模型，不是单一厂商的 API 公式。安全句式是：“我先证明 L0/L1 可启动，再用 L2/L3 smoke，最后用 L4 数值/性能和 L5 任务协议闭环；前一层通过不能替代后一层。”

## 3. CUDA、HIP/ROCm 与 MACA：可复用层和必须重验层

### 3.1 CUDA：异步执行与 driver compatibility 各自有边界

PyTorch 2.13 CUDA 文档说明 GPU 操作默认异步排队；同一 stream 内按顺序执行，不同 stream 需要显式同步或事件建立依赖。NVIDIA CUDA Compatibility 文档则描述 minor-version 与 forward compatibility 的支持模型，并保留 feature limitation、平台和 GPU 前提。

因此，driver/toolkit 兼容只回答“某类运行时组合能否被支持”，不回答第三方 kernel 的 ABI、编译目标、依赖库、shape/dtype 覆盖或性能。未经 `torch.cuda.synchronize()` / CUDA Event 的一次 wall-clock 也不能作为算子性能证据。

### 3.2 HIP/ROCm：接口复用降低改动，不等于 kernel 复用

PyTorch HIP 文档把 HIP 定义为 ROCm 的 C++ dialect，并说明 PyTorch for HIP 有意复用 `torch.cuda` interfaces。这样高层 Python 代码可能少改，但 `.cu` extension、第三方 wheel、通信 backend 和特定 kernel 仍要走自己的编译/运行 gate。

ROCm compatibility matrix 把 PyTorch、Python、GPU、OS、driver/firmware 作为组合进行验证。面试中应说“选择矩阵中已验证的组合”，而不是只报一个 ROCm 版本。

### 3.3 MACA：CUDA-like surface 仍依赖专用软件栈

MetaX `mcPytorch@b3db5e` README 说明其在 PyTorch 2.4 基础上增加 MetaX GPU 支持，并要求 MACA driver、compiler、数学/算子库和通信库配套；安装/运行还依赖 `MACA_PATH`、`MACA_CLANG_PATH` 等环境变量。它支持“高层 PyTorch 使用方式相近”的表述，但不能推出任意 upstream CUDA wheel 或 custom extension 无需重编译。

MetaX `mcTriton@7dd407` README 要求从 mcPytorch 安装包获取 MetaX LLVM，并使用 MACA-specific build script。因此 Triton/custom-kernel 兼容必须单独记录 compiler、SDK、build log 和运行 parity，不能由 Python 模型启动替代。

## 4. 最小 operator matrix：把“可用”变成可审计行

### 4.1 必须固定的字段

一个 operator row 至少固定 `backend`、`framework build`、`op/version`、`dtype`、`shape`、`layout/stride`、`requires_grad`、`forward/backward`、`reference`、`stream/sync`、`status`。VLA 还要加入 action horizon、图像尺寸、batch、mask 和 controller-facing output shape。

| 维度 | 最小取值示例 | 不固定的后果 |
| --- | --- | --- |
| backend | CUDA / MACA / ROCm | 相同 Python 代码可能走不同 dispatch |
| dtype | FP32 / FP16 / BF16（按后端支持） | accumulation、overflow 和容差不可比 |
| shape | tiny、真实 batch、边界 horizon/sequence | 非典型 shape 可能 fallback 或报错 |
| layout | contiguous / non-contiguous、channels-last（若用） | stride 变化会改变 kernel 路径 |
| grad | forward-only / backward / optimizer step | 推理通过不等于训练闭环可用 |
| async | default stream / explicit stream | 未同步计时或跨 stream 竞态 |
| distributed | 单卡 / 2-rank init + all-reduce | 单卡通过不能推出通信可用 |
| VLA contract | mask、denorm、parser、controller | kernel 通过不等于动作可执行 |

### 4.2 forward/backward smoke 的顺序

1. 冻结 backend build、device visibility、dtype、shape、layout 和随机输入。
2. 先跑 forward，再在可训练 op 上跑 backward/optimizer step。
3. 收集 missing kernel、fallback、warning、梯度和显存异常。
4. 与冻结 reference backend 比较输出、梯度和 action contract。
5. 只有在同步方式明确后，才记录 warm-up 后 p50/p95 latency。

## 5. 数值 parity 与同步计时

令 (y_{mathrm{ref}}) 是 reference backend 输出，(y_b) 是待测 backend 输出，(epsilon) 防止参考范数为零。可以使用相对误差作为项目验证指标：

\[
e_{\mathrm{rel}}(b)=\frac{\lVert y_b-y_{\mathrm{ref}}\rVert_2}{\max(\lVert y_{\mathrm{ref}}\rVert_2,\epsilon)}
\]

变量解释：(b) 是待测 backend，(y) 可以是 forward 输出、gradient 或最终 action tensor。它是本项目的 parity 设计，不是 CUDA/ROCm 官方保证；必须固定同一输入、dtype、shape 和随机协议，并按 op 设定 tolerance。对 action 还要检查反归一化后的单位、轴序与 controller 输入。

GPU 计时要等待异步队列完成：

\[
T_{\mathrm{ms}}=t_{\mathrm{end}}-t_{\mathrm{start}},\qquad
t_{\mathrm{start}},t_{\mathrm{end}}\text{ 在对应 device/stream 完成同步后读取}
\]

这里的同步不是一个返回时间戳的数学函数：实现可在计时前后调用 `torch.cuda.synchronize()`，或用 CUDA Event 记录并在完成后读取 elapsed time。HIP 复用 PyTorch CUDA interface，但 MACA 的同步 API、Event 精度和 stream 行为仍需实测；不能从 CUDA 文档直接外推。

## 6. 迁移验证伪代码

```python
def verify_operator_case(case, reference_backend):
    # 1. Freeze backend build, visibility, dtype, shape, layout and input seed.
    env = load_backend_manifest(case.backend, case.framework_build)
    x = make_fixed_input(case.shape, case.dtype, case.layout, seed=case.seed)

    # 2. Run forward and, when trainable, backward/optimizer smoke.
    y = run_forward(case.op, x, backend=case.backend)
    if case.requires_grad:
        reduce_for_smoke(y).backward()

    # 3. Synchronize before timing; asynchronous wall-clock is not sufficient.
    synchronize_backend(case.backend)
    latency = timed_p50_p95(case.op, x, warmup=case.warmup)

    # 4. Compare with a frozen reference using declared tolerance, not exact bytes.
    y_ref = run_forward(case.op, x, backend=reference_backend)
    rel_error = l2(y - y_ref) / max(l2(y_ref), case.eps)

    # 5. Persist fallback warnings, gradients, latency and artifact hashes.
    return record_matrix_row(case, rel_error, latency, collect_runtime_warnings())
```

这是验证顺序的机制模型：environment → forward/backward → synchronize → parity/latency → artifact row。`synchronize_backend`、tolerance 和 fallback warning 的具体 API 必须由各 backend 实现，伪代码本身不是任何厂商的兼容性证明。

## 7. OpenPiVLA 项目映射与真实性边界

本地 [OpenPiVLA Batch 2 证据冻结](../sources/openpivla_batch2_evidence_freeze.html) 直接支持：formal trainer 将 attention 参数设为 `eager`，训练循环使用 Qwen `outputs.loss`；public smoke 能走 `(B,15,72)` 占位 tensor 和 tiny step。当前快照没有 formal checkpoint binary、immutable raw log、parser roundtrip、custom-op matrix 或 profiler。

因此项目中可以说：

> 我在 C500/MACA 迁移时先把 attention 走 eager，目标是避开已记录的 flash-attention / position-id 兼容失败点，让训练、保存和诊断路径先可执行。这个证据只说明 local call graph 和 smoke contract 可读；我不会把它说成 eager 比 flash 快，也不会说所有 custom op、AMP、通信和 action parser 已经兼容。下一步要用固定输入做 forward/backward parity，再补同步计时、dtype/shape 矩阵和 checkpoint→eval roundtrip。

| 口径 | 证据等级 | 面试安全表述 |
| --- | --- | --- |
| `attn_implementation=eager` 调用位置 | local-direct | 兼容性/稳定性选择 |
| public smoke `(B,15,72)` | local-direct | 占位 tensor contract 能走 tiny step |
| MACA 性能优于 CUDA/flash | unverified | 没有 profiler/matched benchmark，不能说 |
| 所有算子/第三方库已适配 | unverified | 没有 operator matrix/build log/fallback audit，不能说 |
| 三后端闭环成功率等价 | unverified | 没有同一 checkpoint、eval manifest、rollout trace，不能说 |

## 8. Trade-off、追问与 bad case

### 8.1 Trade-off

- 更强的 parity/determinism 需要更多同步、固定输入与 artifact，可能牺牲吞吐。
- 纯 Python/eager fallback 往往先提高可诊断性，但不自动带来性能提升。
- 为某个 backend 重编译 custom kernel 可能恢复功能，却引入 compiler/SDK/ABI 的新维护面。
- 单卡 operator smoke 成本低，但不能替代 2-rank collective、真实 batch 和 closed-loop rollout。

### 8.2 高概率 bad case

1. 只检查 `torch.cuda.is_available()`，忽略 wheel、driver、共享库和 backend version。
2. CUDA/HIP 复用 `torch.cuda` API 后，误以为 `.cu` extension、Triton 或 FlashAttention 自动可用。
3. 未同步就比较一次 wall-clock，把 enqueue 时间当成 kernel latency。
4. forward 能跑就宣称训练可用，实际 backward、BF16、非 contiguous layout 或 all-reduce 失败。
5. eager 在 MACA 上能启动，就把它包装成性能 uplift 或 benchmark 因果。

## 9. 结论与下一步

硬件迁移的核心不是替换一个 device 字符串，而是逐层闭合 runtime、build、operator、communication、numerical/runtime 和 VLA workload/eval 合同。PyTorch HIP 的 `torch.cuda` interface reuse 可以降低高层代码改动；ROCm compatibility matrix、NVIDIA compatibility 文档与 MetaX mcPytorch/mcTriton README 同时提醒版本、工具链和 kernel 仍需独立验证。当前个人项目只拥有 eager/MACA local call graph 与 smoke 级证据，仍不能声称算子 parity、性能提升或三后端闭环等价。

下一步：补独立 operator wording review 与 backend×dtype×shape×layout×grad smoke 计划；然后再决定是否生成 `VLA-ENG-014` 单张题卡。题卡生成后默认保持 `unseen`，不会因页面生成升级掌握状态。

## References

1. [PyTorch 2.13 CUDA semantics](https://docs.pytorch.org/docs/2.13/notes/cuda.html)。GPU 异步、stream、synchronize 与 device visibility。
2. [PyTorch 2.13 HIP (ROCm) semantics](https://docs.pytorch.org/docs/2.13/notes/hip.html)。HIP dialect 与 `torch.cuda` interface reuse。
3. [PyTorch 2.13 C++/CUDA extension](https://docs.pytorch.org/docs/2.13/cpp_extension.html)。`CUDAExtension`、`with_cuda`、Ninja 和显式 build contract。
4. [ROCm 7.14.0 compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html)。framework/Python/GPU/OS/driver 组合验证。
5. [NVIDIA CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/)。minor-version / forward compatibility 与限制。
6. [MetaX-MACA mcPytorch@b3db5e](https://github.com/MetaX-MACA/mcPytorch/tree/b3db5eed6a6e330133cd3d4b173f8da392aa6bcb)。PyTorch 2.4 / MACA 环境与工具链边界。
7. [MetaX-MACA mcTriton@7dd407](https://github.com/MetaX-MACA/mcTriton/tree/7dd407c26568fceaca44cb894138e5202d369805)。MetaX LLVM 与 MACA-specific build path。
8. 本仓库 [ENG-014 Source Freeze](../sources/vol_05_eng014_hardware_operator_compatibility_source_freeze.html) 与 [OpenPiVLA Batch 2 证据冻结](../sources/openpivla_batch2_evidence_freeze.html)。
