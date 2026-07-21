# VOL 05 ENG-014：CUDA / MACA / ROCm 硬件迁移与算子兼容性来源冻结

> 审计日期：2026-07-17  
> 状态：`source_frozen / VLA-ENG-014_planned / WARN`  
> 对应问题：`VLA-ENG-014`——VLA 训练或部署从 CUDA 迁移到 MACA、ROCm 等后，怎样判断“能运行”与“算子/数值/性能兼容”？  
> 当前边界：本文件只冻结官方语义、版本/工具链合同和本地项目 hook；ENG-014 知识节点、题卡和真实跨后端 benchmark 均后置。

## 1. 问题与最小范围（Question / Scope）

本切片只回答四个面试准备问题：

1. 为什么 PyTorch 的 `torch.cuda` 接口、CUDA driver compatibility 或 MACA 的 CUDA-like backend 都不能自动证明第三方算子可用？
2. CUDA、ROCm/HIP 和 MACA 之间，哪些层可以复用，哪些层必须重新编译、重新验证或明确降级？
3. 如何设计 forward/backward、dtype、shape、layout、异步计时和分布式通信的最小兼容性矩阵？
4. 结合 OpenPiVLA 本地证据，怎样把 `eager` / MACA 迁移说成稳定性工程，而不是未经验证的性能或算法提升？

本页不声称任何 CUDA kernel、FlashAttention、Triton kernel、NCCL/RCCL/MCCL 或自定义 extension 在三种后端之间自动等价；如果没有对应 backend 的编译、运行和数值 artifact，结论必须降级为 `unverified`。

## 2. 证据类型与冻结输入

| 输入 | 类型 | 版本 / revision | 本页支持 | 本页不支持 |
| --- | --- | --- | --- | --- |
| PyTorch CUDA semantics | primary / official-doc | PyTorch 2.13，访问 2026-07-17 | GPU 默认异步、stream 顺序、显式 synchronize 计时、device 可见性与 CUDA allocator 语义 | 任意第三方 kernel 在 MACA/ROCm 上的实现或性能 |
| PyTorch HIP (ROCm) semantics | primary / official-doc | PyTorch 2.13，访问 2026-07-17 | HIP 是 ROCm 的 C++ dialect；PyTorch HIP 复用 `torch.cuda` 接口以降低迁移改动 | CUDA extension、FlashAttention 或自定义 op 自动可移植 |
| PyTorch C++/CUDA extension | primary / official-doc | PyTorch 2.13，访问 2026-07-17 | `CUDAExtension`、`with_cuda`、Ninja 和编译/链接参数的显式合同 | 这些 CUDA build helpers 对 MACA/ROCm 的自动适配 |
| ROCm compatibility matrix | primary / official-doc | ROCm 7.14.0，页面标注 2026-07-16 | framework、Python、GPU、OS、driver/firmware 需要按矩阵对齐 | 当前工作区的 ROCm runtime 或某个 VLA repo 已验证 |
| NVIDIA CUDA Compatibility | primary / official-doc | 当前官方页面，访问 2026-07-17 | minor-version / forward compatibility 的支持模型与 feature limitation | CUDA driver compatibility 等同于 operator parity |
| `MetaX-MACA/mcPytorch` README | official-code | `b3db5eed6a6e330133cd3d4b173f8da392aa6bcb`，branch `2.4` | mcPytorch 基于 PyTorch 2.4 增加 MetaX GPU 支持；MACA runtime/compiler/operator/communication 环境和版本需要配套 | 任意 CUDA wheel、extension 或 benchmark 在 C500 上无需改动 |
| `MetaX-MACA/mcTriton` README | official-code | `7dd407c26568fceaca44cb894138e5202d369805`，branch `3.0` | mcTriton 需要从 mcPytorch 安装包获取 MetaX LLVM，并用 MACA-specific build script 编译 | 上游 Triton kernel 在 MACA 上直接可运行或性能相同 |
| OpenPiVLA Batch 2 证据冻结 | local-evidence | 本仓库 `sources/openpivla_batch2_evidence_freeze.md` | `eager` call graph、smoke/formal/raw evidence ladder 和当前缺口 | profiler、custom-op matrix、checkpoint lineage 或 MACA 性能 uplift |

### 2.1 官方来源 normalized text 指纹

HTML 来源使用本仓库统一规范化：HTTP GET 后移除 `script/style/nav/header/footer/svg`，合并正文空白，再计算 normalized main-text SHA-256；GitHub frozen README 使用 raw Markdown bytes SHA-256。连续 GET 的 raw HTML 可能含动态资源，不以 raw HTML 指纹作为稳定证据。

| 来源 | normalized text 长度 | SHA-256 |
| --- | ---: | --- |
| [PyTorch 2.13 CUDA semantics](https://docs.pytorch.org/docs/2.13/notes/cuda.html) | 74135 | `1537cdfe8dd17c4180c1447b04d45b0bc86115f98e1b110225827a425e7445ed` |
| [PyTorch 2.13 HIP (ROCm) semantics](https://docs.pytorch.org/docs/2.13/notes/hip.html) | 8179 | `f3be3994e659d0adac61cfc2e24b824b33ffd899b8732dc13e2c7880a19f3dfb` |
| [PyTorch 2.13 C++ extension](https://docs.pytorch.org/docs/2.13/cpp_extension.html) | 22640 | `c8e00d9715e7db1edf259128149f1fb98ed8d21a1c2f533e4b4a7f80f73b1cf9` |
| [ROCm 7.14.0 compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html) | 11210 | `bb3071cd6b2e8cdbdbea5190731b497cc80867a593690884e4be556c97ed8ad0` |
| [NVIDIA CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/) | 1484 | `0964aa382ab5d31e83e490d2e31542d8601ff39fcef62221ae5dfc7edab20aa9` |
| [`mcPytorch@b3db5e` README](https://raw.githubusercontent.com/MetaX-MACA/mcPytorch/b3db5eed6a6e330133cd3d4b173f8da392aa6bcb/README.md) | 6775 bytes | `3fc2c258bf98718de80b62faea90e6d1a65a605aada1f4f65d89224bc455744d` |
| [`mcTriton@7dd407` README](https://raw.githubusercontent.com/MetaX-MACA/mcTriton/7dd407c26568fceaca44cb894138e5202d369805/README.md) | 1096 bytes | `82a3029dc001b38cd9c28a355c98170259f29c216b81aef322c9bda69c5441ed` |

## 3. “兼容”不是一个布尔值：六层合同

### 3.1 直觉

把 CUDA 迁移到另一个后端，像把同一套机器人策略搬到另一座工厂：Python API 只是操作台，下面还有 runtime/driver、编译器、kernel、通信、dtype/数值和评估协议六层。操作台能打开，只说明入口存在；不说明每个按钮、速度和结果都一致。

### 3.2 分层定义

| 层 | 要回答的问题 | 失败例子 | 最小证据 |
| --- | --- | --- | --- |
| L0 device/runtime | device 能发现吗？runtime、driver、共享库是否匹配？ | `is_available=False`、动态库缺失、容器无设备节点 | 环境 manifest、device query、版本打印 |
| L1 framework/build | 当前 PyTorch wheel/build 是否针对该 backend？ | CUDA wheel 误装到 MACA；ROCm/PyTorch/Python 不在支持矩阵 | `torch.__version__`、backend version、安装来源 |
| L2 operator/kernel | 目标 op 是否注册、能否 forward/backward、shape/layout/dtype 是否覆盖？ | attention、custom CUDA extension、稀疏/量化 op 缺失或 fallback | op matrix、compile log、forward/backward smoke |
| L3 communication | DDP/FSDP/ZeRO 所需 collective 是否工作且语义一致？ | collective backend unavailable、all-reduce 初始化失败、异步 collective 未同步 | 进程组 init、collective parity、rank 日志 |
| L4 numerical/runtime | 精度、随机性、stream、同步和内存行为是否可接受？ | FP16/BF16 overflow、未同步计时、不同 layout 误差放大 | reference parity、grad check、synchronized latency |
| L5 workload/eval | VLA 的数据、checkpoint、controller、闭环评估是否仍是同一合同？ | 能训练但 action parser/denorm/controller 不兼容 | lineage、eval manifest、rollout trace |

由此，面试中的安全句式是：**“我先证明 L0/L1 可启动，再用 L2/L3 smoke，最后用 L4 数值/性能和 L5 任务协议闭环；只通过前一层不能替代后一层。”** 这是工程分层归纳，不是某个官方文档给出的单一公式。

## 4. CUDA、HIP/ROCm 与 MACA 的来源边界

### 4.1 CUDA：异步执行和 driver compatibility 都有前提

PyTorch 2.13 CUDA 文档明确说明 GPU 操作默认异步排队；不同 stream 的操作除非显式同步，不保证相对执行顺序，因此未经 `torch.cuda.synchronize()` 或 CUDA Event 的 wall-clock 不能当作准确算子性能。NVIDIA 的 Compatibility 文档则把 minor-version compatibility 和 forward compatibility 定义为受支持的 driver/toolkit 升级路径，并明确存在 feature limitation 与平台/GPU 支持条件。

这两条事实不能推出“所有 CUDA extension 都可运行”：driver 兼容解决的是某一类运行时/工具链组合，算子还要满足编译目标、ABI、依赖库、shape/dtype 和 kernel 实现合同。

### 4.2 HIP/ROCm：接口复用降低迁移成本，不等于实现复用

PyTorch HIP 文档把 HIP 定义为 ROCm 的 C++ dialect，并说明 PyTorch for HIP 有意复用现有 `torch.cuda` interfaces，让很多 Python 层代码少改或不改。这个事实支持“先把 device abstraction 和高层训练代码分离”的迁移策略，但不支持“CUDA `.cu` 自定义 kernel、第三方 wheel 或 NCCL 语义自动可用”。

ROCm 官方 compatibility matrix 进一步把 PyTorch、Python、GPU、OS、driver/firmware 作为组合表管理；面试中应说“按 matrix 选经过验证的组合”，而不是只报一个 ROCm 版本。

### 4.3 MACA：CUDA-like surface 仍需要专用软件栈

`mcPytorch@b3db5e` README 写明项目在 PyTorch 2.4 基础上增加 MetaX GPU 支持，并要求准备 MACA driver、compiler、operator/数学库和通信库；README 的安装示例还要求 `MACA_PATH`、`MACA_CLANG_PATH` 等环境变量。它说明 MACA 可以提供与 CUDA 生态相近的 PyTorch 使用方式，但没有证明任意 upstream CUDA wheel、FlashAttention、Triton kernel 或 custom extension 不需重编译。

`mcTriton@7dd407` README 还要求从 mcPytorch 安装包取得 MetaX LLVM，再执行 MACA-specific build script。这是 custom-kernel 层需要独立 toolchain gate 的直接证据；不能把“Python 模型能跑”升级成“kernel backend 已兼容”。

## 5. 算子兼容性最小验证矩阵

### 5.1 矩阵维度

一个可审计的 operator row 至少固定：`backend`、`framework build`、`op/version`、`dtype`、`shape`、`layout/stride`、`requires_grad`、`forward/backward`、`reference`、`stream/sync`、`status`。对 VLA，额外加入 action horizon、图像尺寸、batch、mask 和 controller-facing output shape。

| 维度 | 最小取值示例 | 为什么不能省略 |
| --- | --- | --- |
| backend | CUDA / MACA / ROCm | Python 代码相同不代表 dispatch 相同 |
| dtype | FP32 / FP16 / BF16（按后端支持） | 精度、overflow、accumulation 路径可能不同 |
| shape | tiny、真实 batch、边界 horizon/sequence | kernel 常在非典型 shape 走 fallback 或报错 |
| layout | contiguous / non-contiguous、channels-last（若使用） | stride 语义影响 kernel dispatch |
| grad | forward-only / backward / optimizer step | 推理能跑不等于训练闭环可用 |
| async | default stream / explicit stream | 未同步计时和跨 stream 依赖会制造假结果 |
| distributed | 单卡 / 2-rank init + all-reduce | DDP/FSDP 额外依赖通信 backend |
| VLA contract | action mask、denorm、parser、controller | 算子通过不等于动作可执行 |

### 5.2 数值与延迟指标

令 (y_{mathrm{ref}}) 是参考 backend 的输出，(y_b) 是待验证 backend 的输出，(epsilon) 防止参考范数为零。逐元素误差可先汇总为：

\[
e_{\mathrm{rel}}(b)=\frac{\lVert y_b-y_{\mathrm{ref}}\rVert_2}{\max(\lVert y_{\mathrm{ref}}\rVert_2,\epsilon)}
\]

变量解释：(b) 是待测 backend，(y) 可是 forward 输出、gradient 或最终 action tensor；该式是本项目的 parity 检查指标设计，不是 CUDA/ROCm 官方承诺。实现上必须固定同一输入、dtype、shape、随机 seed，并按算子类型设定容差；对 action 还要检查反归一化后的单位、轴序和 controller 输入，而不是只比较 token logits。

GPU 计时必须把异步队列纳入合同。对一次测量，可写为：

\[
T_{\mathrm{ms}}=t_{\mathrm{end}}-t_{\mathrm{start}},\qquad
t_{\mathrm{start}},t_{\mathrm{end}}\text{ 在对应 device/stream 完成同步后读取}
\]

这里的同步不是一个返回时间戳的数学函数：实际实现可在计时前后调用 `torch.cuda.synchronize()`，或用 CUDA Event 记录并在完成后读取 elapsed time（HIP 复用相应 PyTorch CUDA interface）。应报告 warm-up 后的 p50/p95，而不是一次未同步 wall-clock。MACA 的同步 API、Event 精度和 stream 行为仍需在其 runtime 上实测，不能由 CUDA 文档直接推断。

## 6. 迁移 / 验证伪代码（工程合同，不是 upstream 实现）

```python
def verify_operator_case(case, reference_backend):
    # 1. Freeze backend build, device visibility, dtype, shape and random input.
    env = load_backend_manifest(case.backend, case.framework_build)
    x = make_fixed_input(case.shape, case.dtype, case.layout, seed=case.seed)

    # 2. Run a forward pass and a backward/optimizer smoke when the op is trainable.
    y = run_forward(case.op, x, backend=case.backend)
    if case.requires_grad:
        loss = reduce_for_smoke(y)
        loss.backward()

    # 3. Synchronize before timing; otherwise asynchronous execution is not measured.
    synchronize_backend(case.backend)
    latency = timed_p50_p95(case.op, x, warmup=case.warmup)

    # 4. Compare with a frozen reference using the declared tolerance, not exact bytes.
    y_ref = run_forward(case.op, x, backend=reference_backend)
    rel_error = l2(y - y_ref) / max(l2(y_ref), case.eps)

    # 5. Record missing kernels, fallback warnings, gradients and artifact hashes.
    return record_matrix_row(case, rel_error, latency, collect_runtime_warnings())
```

该伪代码只表达验证顺序：environment → forward/backward → synchronize → parity/latency → artifact row。`synchronize_backend`、容差和 fallback warning 的具体 API 必须由 CUDA、ROCm 或 MACA runtime 各自实现；不能把这段伪代码当作任一厂商的兼容性证明。

## 7. OpenPiVLA 本地证据与项目边界

本仓库的 [OpenPiVLA Batch 2 证据冻结](openpivla_batch2_evidence_freeze.html) 能直接支持：当前 local formal trainer 将 attention 参数设为 `eager`，调用 Qwen 的 `outputs.loss`；public smoke 能跑出 `(B,15,72)` 的占位 tensor contract；formal report、checkpoint binary、raw log、parser roundtrip 和 profiler 尚未在当前快照闭合。

因此可以这样回答：

> “我在 C500/MACA 迁移时先把 attention 走 eager，目标是避开已记录的 flash-attention / position-id 兼容失败点，让训练、保存和诊断路径先可执行。这个证据只说明 local call graph 和 smoke contract 可读，不能说明 eager 比 flash 快，也不能说明所有 custom op、AMP、通信和 action parser 已经兼容。下一步我会用固定输入做 forward/backward parity，再补同步计时、dtype/shape 矩阵和 checkpoint→eval roundtrip。”

| 口径 | 证据等级 | 安全表述 |
| --- | --- | --- |
| `attn_implementation=eager` 的调用位置 | local-direct | 可说“作为兼容性/稳定性选择” |
| public smoke `(B,15,72)` | local-direct | 可说“占位 tensor contract 能走 tiny step” |
| MACA 性能优于 CUDA/flash | unverified | 没有 profiler 与 matched benchmark，不能说 |
| 所有算子/第三方库已适配 | unverified | 没有 operator matrix、build log、fallback audit，不能说 |
| 三后端闭环任务成功率等价 | unverified | 没有同一 checkpoint、eval manifest 和 rollout trace，不能说 |

## 8. 当前 Gate、风险与下一步

| Gate | 当前状态 | 下一动作 |
| --- | --- | --- |
| 官方 CUDA/HIP/ROCm/MACA 来源 | `PASS WITH WARNING` | 保留版本与 commit；ROCm matrix 和 MACA README 随版本变化需复核 |
| driver/framework/toolchain 分层 | `PASS` | 知识页沿用 L0–L5 合同，不写单一 `compatible=true` |
| custom operator / extension | `WARN` | 为 attention、量化、Triton/CUDA extension 建 backend×dtype×shape×grad 矩阵 |
| distributed communication | `WARN` | 单独跑 process-group init、all-reduce、2-rank smoke；不要从单卡结果推断 |
| numerical parity / synchronized latency | `WARN` | 补 reference output、gradient、容差、warm-up、p50/p95 和同步方式 |
| OpenPiVLA project boundary | `PASS WITH WARNING` | 保留 eager/MACA 稳定性表述，不升级性能/benchmark claim |
| knowledge/card | `PENDING` | 先做 ENG-014 独立 wording review，再写一个知识节点和一张 unseen 题卡 |

## 参考来源（References）

1. PyTorch 2.13，[CUDA semantics](https://docs.pytorch.org/docs/2.13/notes/cuda.html)。GPU 异步、stream、synchronize、device visibility 与内存语义。
2. PyTorch 2.13，[HIP (ROCm) semantics](https://docs.pytorch.org/docs/2.13/notes/hip.html)。HIP dialect 与 `torch.cuda` interface reuse。
3. PyTorch 2.13，[C++/CUDA extension](https://docs.pytorch.org/docs/2.13/cpp_extension.html)。`CUDAExtension`、`with_cuda`、Ninja 和显式编译合同。
4. AMD，[ROCm 7.14.0 compatibility matrix](https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html)。framework/Python/GPU/OS/driver 组合验证。
5. NVIDIA，[CUDA Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/)。minor-version 与 forward compatibility 及其限制。
6. MetaX-MACA，[mcPytorch@b3db5e](https://github.com/MetaX-MACA/mcPytorch/tree/b3db5eed6a6e330133cd3d4b173f8da392aa6bcb)，环境与工具链边界以 README 和该 revision 的 LICENSE 文件为准。
7. MetaX-MACA，[mcTriton@7dd407](https://github.com/MetaX-MACA/mcTriton/tree/7dd407c26568fceaca44cb894138e5202d369805)，MetaX LLVM 与 MACA-specific build path。
8. 本仓库，[OpenPiVLA Batch 2 证据冻结](openpivla_batch2_evidence_freeze.html)。当前 eager/MACA、smoke/formal/raw 和 `H=15,D=72`/`limit=16` 证据边界。
