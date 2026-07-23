# VOL 03 Source Audit F：VLA 架构、Mask、适配与执行独立事实复核

> 状态：`independent_fact_review / landscape_mask_transform_queue_checked / WARN`
> 审查日期：2026-07-19
> 范围：RT-2、OpenVLA、Octo、π0/openpi 的架构路线、sequence/mask、适配、checkpoint/norm/transform、timing、chunk broker 与 DROID controller example。
> 结论先行：四条路线确实使用不同的 action 监督合同；Octo 的 `timestep_pad_mask & action_pad_mask` 是有效维 mask 的正例，openpi 的 `Policy.infer` 明确执行 checkpoint norm stats 与 input/output transform 链，`ActionChunkBroker` 只在缓存耗尽时重新 query，DROID example 的 `[10,8]` 与 `open_loop_horizon=8` 是特定 example contract。RT-2 的 1–3 Hz/5 Hz 是 cloud-serving 测量，不能迁移为本地 latency；OpenVLA/Octo/π0 上游实现也不能证明 OpenPiVLA 的 checkpoint、axis/unit、controller 或个人贡献。

## 1. 直接复核来源与冻结对象

| ID | 来源 | 本次核对 | SHA / Verdict |
| --- | --- | --- | --- |
| P01 | [RT-2 v1 PDF](https://arxiv.org/pdf/2307.15818v1) | §3.2 action 256 bins/token、PaLI-X/PaLM-E tokenization、co-fine-tune、cloud serving frequency | `0A62DC36BBBFDEA232AD45A0AB75C82E9CF535B55333FF22C02D5DA1897CCAC` / `primary-verified` |
| P02 | [Octo v2 PDF](https://arxiv.org/pdf/2405.12213v2) | readout/block-wise mask、diffusion head、27M/93M、Open X-Embodiment mixture、20-step head | `73BFF297CFAFE523319162124E6B7F96919C0930E0A380F307255C4C7464AC93` / `primary-verified` |
| C01 | [`octo_module.py`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_module.py) | timestep padding、observation/task/readout token masks | `E458062721FD1E72FAD00F7833B749E82D0DF60AA7927557362BDF6463299FBF` / `official-code` |
| C02 | [`action_heads.py`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/components/action_heads.py) | `masked_mean`、timestep/action conjunction、embodiment dimension slice、diffusion mask | `480F374788571DB11F1E3CA2922BEAEC52F752001AE5AC6D284E0F1DFEC40D11` / `official-code` |
| C03 | [`octo_pretrain_config.py`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/scripts/configs/octo_pretrain_config.py) | default `action_horizon=4`, `action_dim=7` | `531A2F056EBCF995FE37DFB99634354D58F167F423C1A97BDF3C5545E425E0DD` / `official-code` |
| C04 | [`octo_model.py`](https://github.com/octo-models/octo/blob/241fb3514b7c40957a86d869fecb7c7fc353f540/octo/model/octo_model.py) | sample action output and `embodiment_action_dim`/unnormalization path | `93D96015BC43EE92910127421E17697D372F0BBC1A4D3589A0ADDB22EFB819E0` / `official-code` |
| C05 | [`openpi/policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py) | input transform、model timing、output transform、`policy_timing.infer_ms` | `A2AC5236E23B11D0F5A840D4A8FEF148D89DBA921D5452EC5DFCD5A6FFA46F20` / `official-code` |
| C06 | [`policy_config.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_config.py) | checkpoint type detection、model/config load、checkpoint norm stats、ordered transforms | `AAF42AB04A33B6C91D2447926211646C33EBD8EBFA427F026D7B6C4F7C45EC52` / `official-code` |
| C07 | [`transforms.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py) | Unnormalize、Delta/Absolute action transforms、pad/repack boundary | `A1B94E9E72849A18834778F229C6BB389A495EB7FBE0AA800EDEA728B9424FF4` / `official-code` |
| C08 | [`training/config.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/config.py) | full/LoRA examples、action horizon/dim overrides、delta masks | `C34231F888DBA5DC981D808765B3D98775AB845B04313BF53FCECD567C520B0D` / `official-code` |
| C09 | [`action_chunk_broker.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/packages/openpi-client/src/openpi_client/action_chunk_broker.py) | cache slice、requery at exhaustion、reset | `019B9D69CB26CC681331A2F95DBE60A2CC7B02D6D309C5D15B6457AB39798234` / `official-code` |
| C10 | [`examples/droid/main.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/droid/main.py) | `open_loop_horizon=8`、`[10,8]` chunk、gripper binarize、clip、control frequency | `4BDBDBDDE068EBB30BA90D62BF8C51DF156B4BAAE5C5AC5870C08F7B03D4AFC2` / `official-code` |
| C11 | [`policy_test.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy_test.py) | broker shape/half-chunk smoke semantics | `9DBB20963600367A7E7ABFC97D1E326916777C57A87B39B1BC4070BA64676683` / `official-code` |
| I01 | 本仓 Source Audits A/B/E | OpenVLA endpoint、π0/FAST、Flow time/sign 与 all-D mask 边界 | `internal-source-reviewed` |
| O01 | 本次 synthetic probes | Octo mask mean、openpi delta/absolute round-trip、broker requery、DROID prefix | `local-evidence / PASS` |

冻结版本：Octo commit `241fb3514b7c40957a86d869fecb7c7fc353f540`（MIT）、OpenPI commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`（Apache-2.0）。本页不把 repo example、Git author、上游 checkpoint 或公开 metric 归为个人贡献。

## 2. Landscape：action 监督合同不同于模型规模

| 路线 | action 表示 | 监督/生成 | 本次可核事实 | 不可推出 |
| --- | --- | --- | --- | --- |
| RT-2 | 6-DoF/夹爪/终止等维度 uniform 256 bins → token | VLM next-token + robot/web co-fine-tune；动作 token 受限采样 | §3.2 明确 256 bins、PaLI-X 与 PaLM-E 使用不同 token 复用方式 | 本地 tokenizer、controller、单机 latency |
| OpenVLA | 每个 scalar 使用尾部 action token | action label 的 causal CE；decoder unnorm 依 dataset stats | 见 Audit A；旗舰路径与 LoRA 脚本需分开 | 本地 Qwen route 或个人改造 |
| Octo | learned readout → continuous diffusion action head | transformer 一次 forward，multi-step denoise 在小 head 内完成；默认 pretrain config `H=4,D=7` | 论文与 frozen config/readout/head 直接支持 | Octo 指标可跨协议比较、任意 embodiment 都是 7D |
| π0/openpi | continuous \(H\times D\) action expert 或 FAST tokens | VLM prefix + flow/FAST；输出 transform 与 broker 在模型外 | `Policy`/transforms/broker/DROID example 直接支持 | 本地 checkpoint/H/K/axis/unit |

RT-2 论文的 55B 1–3 Hz、5B 约 5 Hz 是其 cloud-serving protocol 的历史测量；它们不是 OpenVLA/π0 或本地 OpenPiVLA 的 hardware benchmark。Octo 的 27M/93M、800k OXE 和 20 diffusion steps 属于公开方法/recipe边界，不代表本地训练配置。

## 3. Sequence、attention mask 与 loss mask

### 3.1 Octo 的 readout 与 block-wise mask

Octo 的 `octo_module.py` 将 `timestep_pad_mask` 标记为 `(batch, horizon)`，`False` 表示 padding timestep。观察 token 的 mask 会结合 tokenizer mask 与 timestep mask；task token 有自己的 pad mask；readout token 使用独立的 readout mask。论文同时说明：observation token 只能因果读取同一或更早 timestep 与 task token，readout 能读取前面的 observation/task/readout，但 observation/task 不读取回 readout。

这意味着：

- attention-visible：某 token 是否能读取另一个 token；
- timestep-valid：该 observation window 是否真实存在；
- action-valid：该 embodiment 的 action dimension 是否存在；
- loss-visible：该元素是否进入 continuous/diffusion loss。

它们不是同一个 boolean。

### 3.2 Octo 的有效维 loss

`action_heads.py` 的 `masked_mean` 先将 mask broadcast 到 loss shape，再计算：

\[
\operatorname{masked\_mean}(x,m)
=\frac{\operatorname{mean}(x\odot m)}{\max(\operatorname{mean}(m),10^{-5})}.
\]

变量与直觉：当 (m) 是 0/1 mask 时，这等价于只对有效元素平均（只要有效比例不为 0）。连续 head 与 diffusion head 都构造：

\[
M_{b,w,h,d}=T_{b,w}\land A_{b,w,h,d},
\]

再将 (M) 传入 loss；推理 `sample_actions` 可用 `embodiment_action_dim` 把 padded diffusion dimensions 的 mask 设为 False，并最终 slice 到 stats 长度。

这与此前 frozen Pi0 的 all-D mean 是有意保留的正例/负例对照；不能泛称“所有 VLA 都正确 mask padding”。

## 4. 适配方式：full、head-only、LoRA、action expert

Octo paper/repo 提供轻量 diffusion head 与 readout 结构，公开配置支持更换 observation/task/action head；其 finetune choices 与 OpenVLA/openpi 的 LoRA 例子说明的是“repo 支持的 adaptation route”，不是某个 paper 主结果默认使用 LoRA。

openpi `training/config.py` 直接列出：

- full finetune 配置（例如 `pi0_fast_full_droid_finetune`）；
- PaliGemma 与 action expert 的 LoRA variant；
- action dimension/horizon 随 dataset 调整的配置。

LoRA 的事实仍需按 base checkpoint、target modules、rank、merge state 和 optimizer state 绑定。看到 `lora` 字段不能证明本地 checkpoint 真的用该 config。

## 5. Checkpoint → norm → transform → runtime 合同

openpi `create_trained_policy` 的顺序是可直接核验的：

1. 检查 checkpoint 是否有 `model.safetensors`，据此选择 PyTorch/JAX load path；
2. 用 training config 构造 model/data config；
3. 若未显式传入 norm stats，从 checkpoint `assets/<asset_id>` 读取；
4. input transforms：repack → prompt → data transforms → normalize → model transforms；
5. `Policy.infer` 调用 `sample_actions`；
6. output transforms：model outputs → unnormalize → data outputs → repack outputs。

normalization 的 z-score 反变换为：

\[
x_{\mathrm{physical}}=x_{\mathrm{model}}(\sigma+10^{-6})+\mu.
\]

quantile path 则用 q01/q99 做 ([-1,1]) 到物理区间的逆映射。`DeltaActions`/`AbsoluteActions` 按 boolean mask 对前若干维加减 state；这只完成 declared transform，不自动决定 axis、frame、rotation 或 gripper semantics。

## 6. Timing：`infer_ms` 不是端到端 latency

openpi `Policy.infer` 的 `policy_timing.infer_ms` 只包围 `_sample_actions`，不包括输入 transform、网络传输、server serialization 或 controller queue。要得到端到端值，仍需另记：capture、preprocess、upload、server/model、download、parse/unnorm、queue wait 和 controller tick。一次上游字段不足以证明视觉编码、action expert NFE 或网络分别耗时多少。

## 7. Chunk broker 与 DROID example

`ActionChunkBroker` 的行为是：缓存为空时调用 inner policy；每次返回当前 `_cur_step` 行；当 `_cur_step >= action_horizon` 时清空缓存；`reset()` 清空 policy 与 cache。它假设所有 array action fields 第一维是 chunk length，但不做 request-id/stale-response/NaN/axis/unit 安全检查。

DROID example 另有一层 rollout contract：

```python
# Query a fresh chunk when the configured execution prefix is exhausted.
if actions_from_chunk_completed == 0 or actions_from_chunk_completed >= open_loop_horizon:
    pred_action_chunk = policy_client.infer(request_data)["actions"]  # [10, 8]

# Execute only the selected prefix row, then binarize gripper and clip.
action = pred_action_chunk[actions_from_chunk_completed]
action[-1] = 1.0 if action[-1] > 0.5 else 0.0
action = np.clip(action, -1, 1)
env.step(action)
```

这里的 `[10,8]` 表示 10 行 action、8 个维度（7 joint velocity + 1 gripper position）；`open_loop_horizon=8` 表示执行 8 行后再 query，剩余 2 行不一定被使用。这是该 example 的 H/K 合同，不是 openpi 的 universal default，也不是本地 OpenPiVLA 证据。

## 8. Synthetic probes

| Probe | 结果 | 结论 |
| --- | --- | --- |
| Octo `x=[1,3,5,7]`，mask `[1,1,0,0]` | masked mean `2.0` | action/timestep mask 可排除 padded dims |
| Octo `T=[1,0]` 与 `A` 全 valid | 合并 mask 第二 window 全 0 | padded timestep 不产生 loss |
| openpi z-score round-trip：`mu=[10,20]`,`std=[2,4]`,`x=[14,12]` | normalize `[2,-2]` 后 inverse `[14,12]`（浮点误差内） | norm asset 必须匹配 |
| `DeltaActions`/`AbsoluteActions` mask `[1,0,1]`，state `[10,20,30]`，delta `[1,2,3]` | abs `[11,2,33]`，再 delta `[1,2,3]` | transform 顺序/掩码可单测 |
| `ActionChunkBroker(action_horizon=2)`，inner chunk rows `[0,1,2,3]` | 输出 `0,1` 后第二次 query；reset 清空 cache | broker execution prefix 与 model chunk 可不同 |
| DROID example chunk `[10,8]`, `open_loop_horizon=8` | 只消费 rows `0..7`，第 8 次边界 query | example 不等于执行完整 H |

这些 probes 验证 mask、transform、broker 与 example branch semantics，不证明任何 learned policy success、latency 或本地项目实现。

## 9. 对 `VLA-ARCH-007..012` 与 `VLA-ACT-031..032` 的回写结论

| Question ID | 独立复核结论 | 必须保留的边界 |
| --- | --- | --- |
| `VLA-ARCH-007` | RT-2/OpenVLA/Octo/π0 landscape 与 action contract 可核 | 不做跨 protocol 指标排名 |
| `VLA-ARCH-008` | attention/readout/loss/action mask 分层可核 | 本地 mask 未证 |
| `VLA-ARCH-009` | full/head/LoRA/action expert 的 repo support 可核 | 不把 support 当本地 choice/个人设计 |
| `VLA-ARCH-010` | Octo conjunction mask 与 openpi all-D 对照可核 | 本地 D/d/valid mask 未证 |
| `VLA-ARCH-011` | RT-2/FAST/openpi timing scopes 可核 | 不迁移 source latency 到本地 |
| `VLA-ARCH-012` | paper→repo→checkpoint→runtime 五层审计合同可核 | 本地 manifest/trace 仍缺 |
| `VLA-ACT-031` | decode→unnorm→slice→schema→controller 顺序可核 | 本地 axis/unit/controller 未证 |
| `VLA-ACT-032` | parser/FIFO/replan/stale/safety test matrix 可核 | 上游 broker test 只覆盖 shape，项目 tests 未执行 |

## 10. 项目真实性边界与安全口径

上游 facts 可以帮助面试回答“为什么 mask、为什么要把 norm stats 和 transform 绑到 checkpoint、为什么 action chunk 的 H 与执行 prefix K 分开”。它们不能证明 OpenPiVLA 采用 Octo mask、openpi broker、DROID `[10,8]`、某个 LoRA config、RT-2 latency 或任何 upstream checkpoint。

### 30 秒安全回答

“VLA 的 action head 不能只按 backbone 名字分类：RT-2/OpenVLA 是离散 token，Octo 是 readout 条件化的 diffusion head，π0 是 VLM prefix 条件化的 continuous action expert。Octo 直接把 timestep padding mask 和 embodiment action mask 合并进 loss，而 openpi 的 runtime 还必须把 checkpoint、norm stats、input/output transforms 和 broker 一起审计。DROID example 里模型输出 `[10,8]`，但只按 `open_loop_horizon=8` 消费，说明 model chunk 和 execution prefix 不是一回事。对我的项目，我只有在本地 manifest、parser、norm、axis/unit、queue 和 controller trace 齐全时，才把这些上游机制映射成项目事实。”

## 11. 风险、未决项与下一步

1. **核心 public facts 已独立复核**：RT-2 action token、Octo readout/mask/diffusion、openpi transform/broker/timing/DROID example 已核对。
2. **视觉 QA**：`file://` 浏览器策略限制仍记录为 `BLOCKED`；静态 HTML 校验不等价于视觉验收。
3. **本地项目 gate**：OpenPiVLA checkpoint、tokenizer/norm assets、D/d/H/K、axis/unit、controller trace、latency ledger 与 ownership 仍待本地证据。
4. **下一 bounded slice**：进行一题 `VLA-ARCH-010/031` 或 OpenPiVLA ownership 真实口述；不新增题卡、不创建 `coaching_state.md`。

## 参考文献（References）

1. Brohan et al., [RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control](https://arxiv.org/html/2307.15818v1)，arXiv `2307.15818v1`。
2. Kim et al., [OpenVLA](https://arxiv.org/html/2406.09246v3) 与本仓 Source Audit A。
3. Octo Model Team et al., [Octo: An Open-Source Generalist Robot Policy](https://arxiv.org/html/2405.12213v2)，arXiv `2405.12213v2`。
4. Black et al., [π0](https://arxiv.org/html/2410.24164v4) 与本仓 Source Audits B/E。
5. [octo-models/octo@241fb351](https://github.com/octo-models/octo/tree/241fb3514b7c40957a86d869fecb7c7fc353f540)，MIT。
6. [Physical-Intelligence/openpi@15a9616a](https://github.com/Physical-Intelligence/openpi/tree/15a9616a00943ada6c20a0f158e3adb39df2ccac)，Apache-2.0。
7. [VLA 架构、适配、延迟与动作执行 Claim-to-Code](vol_03_architecture_execution_claim_to_code.html)，本仓先前 source freeze；本页为独立复核。
