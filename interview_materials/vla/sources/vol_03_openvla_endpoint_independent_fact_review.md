# VOL 03 Source Audit A：OpenVLA Endpoint / Token / Mask 独立事实复核

> 状态：`independent_fact_reviewed / audit_a / endpoint_mask_checked / PASS WITH WARNING`
> 审查日期：2026-07-19
> 冻结版本：OpenVLA paper arXiv `2406.09246v3`；official repo commit `c8f03f48af692657d3060c19588038c7220e9af9`。
> 结论先行：论文明确写“每维 256 bins、整数 0..255、覆盖 Llama 末尾 256 tokens”；frozen code 则构造 256 个 threshold values 与 255 个 centers，encode 仍会产生 256 个 token IDs，但 decode 只有 255 个不同 center，最高两个编码索引都重建为最后 center。训练 CE 的 label mask 与 action accuracy/L1 metric mask 也不是同一掩码。

## 1. 直接复核来源

| ID | 来源 | 本次直接读取内容 | Verdict |
| --- | --- | --- | --- |
| P01 | [OpenVLA paper v3 §3.2](https://arxiv.org/html/2406.09246v3) | 256 bins、整数 0..255、overwrite 256 least-used tokens、action-token-only CE | `primary-verified` |
| C01 | [`action_tokenizer.py`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/action_tokenizer.py) | 256 thresholds、255 centers、digitize、tail-vocab mapping、decode clip | `official-code / frozen` |
| C02 | [`datasets.py`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/vla/datasets/datasets.py) | action+EOS labels、prompt `IGNORE_INDEX`、`predict_stop_token` | `official-code / frozen` |
| C03 | [`prismatic.py`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlms/prismatic.py) | image patches 插入与 patch-label `IGNORE_INDEX` | `official-code / frozen` |
| C04 | [`base_strategy.py`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/training/strategies/base_strategy.py) | CE backward、action-token accuracy mask、decode 后 L1 metric | `official-code / frozen` |
| C05 | [`openvla.py`](https://github.com/openvla/openvla/blob/c8f03f48af692657d3060c19588038c7220e9af9/prismatic/models/vlas/openvla.py) | generate d tokens、decode、unnorm key、q01/q99 inverse | `official-code / frozen` |

## 2. 256 token IDs / 255 centers 的精确推导

代码设置：

\[
e_j=-1+\frac{2j}{255},\quad j=0,\ldots,255,
\qquad
c_j=\frac{e_j+e_{j+1}}2,\quad j=0,\ldots,254.
\]

因此 `self.bins`/thresholds 有 256 个值，`self.bin_centers` 有 255 个值。对 clip 后的 normalized scalar，NumPy 默认 `digitize` 返回：

\[
b=\operatorname{digitize}(\tilde a,e)\in\{1,\ldots,256\},
\qquad t=V-b.
\]

(V) 是 tokenizer vocabulary size，所以 (t\in\{V-256,\ldots,V-1\})，确实使用末尾 256 个 token IDs。decode 做：

\[
j=\operatorname{clip}(V-t-1,0,254),\qquad \hat a=c_j.
\]

于是 (b=255) 与 (b=256) 都变成 (j=254)。本次 deterministic probe 得到：

| 输入 | digitize b | decode index j | reconstructed center |
| --- | ---: | ---: | ---: |
| -1 | 1 | 0 | -0.9960784314 |
| 0 | 128 | 127 | 0 |
| 0.9921568627 | 255 | 254 | 0.9960784314 |
| 1 | 256 | 254 | 0.9960784314 |

因此必须同时说清三件事：paper abstraction 是 256 bins；encoder/token vocabulary 的 cardinality 是 256；frozen decoder 的 unique reconstruction centers 是 255。不能把任何一个数字单独替代另外两个。

## 3. Label mask 与 metric mask

`RLDSBatchTransform` 将 prompt labels 设为 `IGNORE_INDEX`，保留 `len(action)+1` 个尾部 label；默认 `predict_stop_token=True` 时这包含 action tokens 与 stop/EOS。`PrismaticVLM.forward` 还将插入的 image patch labels 设为 `IGNORE_INDEX`。

训练优化使用模型返回的 causal-LM CE；而 `base_strategy.py` 的 action accuracy/L1 metric 使用：

\[
m_k^{metric}=\mathbf 1[y_k>V-(256+1)].
\]

该阈值恰好选中 (V-256..V-1) 的 256 个 action token IDs，排除 prompt、image patches 和 EOS。连续 L1 是 argmax token decode 后的监控 metric，不是训练 objective，也不是 closed-loop success。

## 4. 回写结论

| 下游 | 修正 |
| --- | --- |
| VOL 03 knowledge | “256 endpoints”改为“256 thresholds/edge values”；显式写 b=255/256 alias 到 center 254 |
| VLA-ARCH-005 | 30 秒答案不变；机制答案补 paper/code/cardinality 三层 |
| VLA-ACT-003 | quantization 代价补 highest-two-token decode alias |
| Source Audit A review | independent endpoint/mask review 改为 PASS WITH WARNING；local project gate 不变 |

## 5. 不能推出的项目事实

- 不推出 OpenPiVLA 使用原始 OpenVLA `ActionTokenizer`；FAST、JSON/custom formatter 必须分别取证。
- 不推出本地 tokenizer revision、checkpoint、action dimension、q01/q99、unnorm key、controller 或 97.4% protocol 已闭合。
- 不推出 255-center nuance 是个人发现或个人修复；这是 frozen official code 的直接行为。
- 不改变 44 张 VOL 03 卡的 `unseen` 状态，也不创建 coaching state。

## 6. 下一步

Source Audit A 的 endpoint/token/mask 高风险项已完成独立复核，公共事实层 verdict 为 `PASS WITH WARNING`；这不关闭本地 tokenizer/checkpoint/stats/controller/97.4%/ownership 与口述 gate。下一 bounded slice 优先进行一题真实口述，或收集一个本地 OpenPiVLA immutable artifact。

## 参考入口

- [OpenVLA Source Audit A](vol_03_openvla_claim_to_code.html)
- [VOL 03 Knowledge](../knowledge/vol_03_vla_action.html)
- [VOL 03 Questions](../questions/vol_03_vla_action.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)
