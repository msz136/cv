# OpenPiVLA Official Checkpoint Immutable Manifest Gate

> 状态：`local-file-manifest-complete / remote-checkpoint-unavailable / norm-stats-unhashed / WARN`
> 审查日期：2026-07-21
> 范围：`C:\Users\mousongzhe\Project\openpivla_deployment` 中 ALOHA action-level eval 与 LIBERO/Franka rollout 的本地文件，以及部署记录中声明的 `pi0_aloha_sim` / `pi05_libero` checkpoint 目录。
> 结论先行：本页已对本地 rollout、summary、脚本、图片和视频逐文件计算 SHA-256；但两个 checkpoint 的 `params` 与 checkpoint 内 norm-stats 目录只存在于部署记录的远端 `/data/msz/...` 路径，当前 Windows 工作区不可访问。因此可以冻结“本地证据 bundle”，不能声称已经完成 checkpoint binary 或 norm-stats 的 immutable manifest。

## 1. Question 与证据边界

上一组 [LIBERO Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html) 和 [ALOHA Action Eval Load Gate](openpivla_aloha_action_eval_load_gate.html) 已证明 server 进程实际 restore 了官方 checkpoint、加载了 checkpoint assets 中的 normalization stats，并产生了 rollout/action-level eval 结果。本页只进一步回答：

1. 本地归档中哪些文件可以逐文件重算 SHA-256；
2. `pi0_aloha_sim` 与 `pi05_libero` 的 checkpoint 目录是否在当前工作区可读；
3. 如果 checkpoint 仍不可读，面试回答中哪些 lineage 结论必须保留为 warning。

本页不复制远端权重、不重新下载 checkpoint、不把官方 checkpoint 改写为候选人的 fine-tune 产物，也不把文件级 manifest 缺口用目录大小或 restore 成功事件替代。

## 2. Manifest contract

对一个真正可复用的 immutable artifact，最小记录单元定义为：

\[
M_i=(r_i, s_i, b_i, h_i, t_i, q_i)
\]

其中 `r_i` 是相对路径，`s_i` 是文件角色，`b_i` 是字节数，`h_i` 是 SHA-256，`t_i` 是本地最后修改时间，`q_i` 是证据等级。直觉上，只有路径、大小、hash 与角色同时冻结，后续面试追问才可以从“我看过一个目录”缩小到“这一次 run 使用的具体文件集合”。本页对本地文件直接记录这些字段；对远端 checkpoint 只能记录部署文档声称的路径和历史体量，`h_i` 与完整 `r_i` 列表均缺失。

```python
def freeze_local_manifest(root, relative_paths):
    # 1. 只读取用户已归档的本地文件，不复制权重或改变项目目录。
    records = []
    for rel in sorted(relative_paths):
        path = root / rel
        # 2. 对每个文件记录字节数、修改时间和 SHA-256。
        records.append({
            "path": rel,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "role": classify(rel),
        })
    # 3. 缺失的远端 checkpoint 不填假 hash，而是单独进入 open gate。
    return records
```

## 3. Checkpoint target audit

| Config | 部署记录中的 checkpoint 根目录 | 部署记录的历史描述 | 当前 Windows 工作区 | 可支持的结论 |
| --- | --- | --- | --- | --- |
| `pi0_aloha_sim` | `/data/msz/openpivla/models/openpi-assets/checkpoints/pi0_aloha_sim` | Present；约 11.189 GiB、21 files | `Test-Path` 不存在；没有 `params` 或 `assets` 文件可读取 | `serve.log` 证明当时约 6.0 GiB Orbax restore 与 checkpoint norm-stats load；不能提供本地 binary SHA |
| `pi05_libero` | `/data/msz/openpivla/models/openpi-assets/checkpoints/pi05_libero` | Present；下载完成约 11.6 GiB | `Test-Path` 不存在；没有 `params` 或 `assets` 文件可读取 | `serve.log` 证明当时约 6.2 GiB Orbax restore 与 LIBERO norm-stats load；不能提供本地 binary SHA |

`DEPLOYMENT.md` 的“Present”是部署记录中的远端状态，不是当前工作区的文件存在证明。当前不能从 Windows 目录读取 `/data/msz/...`，也没有远端只读 manifest、对象存储 revision、Merkle root 或下载清单。因此：

- `checkpoint path + restore success`：`PASS WITH WARNING`；
- `checkpoint per-file SHA / total manifest`：`UNVERIFIED`；
- `norm-stats content + SHA`：`UNVERIFIED`；
- `private Qwen3-VL/LoRA fine-tune lineage`：`UNVERIFIED`，且不应由 official checkpoint 推断。

## 4. Local immutable manifest：deployment and code

以下对象均在用户本地项目中，SHA-256 于 2026-07-21 重新计算。`local-direct` 只表示文件确实可读并被哈希，不表示文件内部的所有运行依赖都已闭合。

| ID | 相对路径 | 字节数 | SHA-256 | 角色 |
| --- | --- | ---: | --- | --- |
| D01 | `DEPLOYMENT.md` | 28695 | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14E` | 部署路径、官方 checkpoint inventory、环境与结果边界 |
| C01 | `scripts/eval_lerobot_action_server.py` | 19702 | `B1B7FB9B7A86355B9C1843CDE971B38FD26A2DAB1F18550128671F79F1AB4F39` | ALOHA action-level eval、shape/L1 汇总与 dashboard writer |
| C02 | `scripts/run_lerobot_action_eval.sh` | 3053 | `61DFE972B20722CF08B3FA139D68B29B6C1B52286671A7705000AE3738A8BF60` | ALOHA server/client launcher 与 checkpoint/config 参数 |
| C03 | `scripts/run_libero_true_rollout.py` | 12841 | `1C7F74DE83FD373A27FEDC70D863D5F0BF164B4512ED63E1D76552A0F22C3016` | LIBERO observation、action slice、replan 与 summary writer |

## 5. Local immutable manifest：ALOHA action-level bundle

目录：`artifacts/lerobot_action_eval_aloha_sample_real_v2/`。该 bundle 的 `summary.json` 记录 4 个 sample、horizon 50、action dimension 14、mean L1 `0.0330713950`、std `0.0205169544`；这些文件支持 action-vector/harness diagnostic，不支持 task success 或 fine-tune benchmark。

| ID | 相对路径 | 字节数 | SHA-256 | 角色 |
| --- | --- | ---: | --- | --- |
| A01 | `index.html` | 3519 | `AE7C0B0D7D1523E3896B11A584BD8B0B335705538A78B804376701E844A6CA9F` | 本地 action-eval dashboard |
| A02 | `sample_000_action_compare.png` | 90142 | `CE2034EEB3EEE3FDD55E0C5F18D1DD37859331CE7F1940492312DFE5551BFF14` | sample 0 action comparison plot |
| A03 | `sample_000_frame.png` | 30109 | `F1D624D774529E9BFF0AA06C77DAC1B0E9C31DEB5A5A5CE8B704A0041EE95BD7` | sample 0 frame snapshot |
| A04 | `sample_001_action_compare.png` | 85942 | `4E9A6DA5FE5DF4BC796FFE9215530EA7ED2625DA6E45050198A425B376090FEA` | sample 1 action comparison plot |
| A05 | `sample_001_frame.png` | 33874 | `33D7F9D9BFE615C6A72B4DBA32CBA299F01423D4E045ABF825F2011914F67AFF` | sample 1 frame snapshot |
| A06 | `sample_002_action_compare.png` | 87720 | `B76F05DB82D7CDFF0D572BDC082E14C946D6AE8A8A092EDDF48594198DACA245` | sample 2 action comparison plot |
| A07 | `sample_002_frame.png` | 33580 | `0C36C5AF43FC3EA1CBB383E10DEAB395B568A843869CAB9130B67353B8465922` | sample 2 frame snapshot |
| A08 | `sample_003_action_compare.png` | 87738 | `A76C2EBC45C5802A4CF13499F0E68D5F6379EEF61986614A1680290410CDE7E2` | sample 3 action comparison plot |
| A09 | `sample_003_frame.png` | 31141 | `0C22B8B65CE4391CA484AFBC32075565287D0CF287A422FCF4C40EA3FC1F69ED` | sample 3 frame snapshot |
| A10 | `samples.jsonl` | 1219 | `6570879E9242F89700F2CBD2898BA5988A2BB0CE41E475483C403F152A529E82` | 4 sampled action/GT records |
| A11 | `serve.log` | 3191 | `F02D0E4D08D6879C2F080B3DA905B4EA11A73B7510B7D8867785FFD1384A0868` | Orbax restore、norm-stats、8020 listen/connection |
| A12 | `summary.json` | 2261 | `D367885AFB621469C81CB885C53FD36A87F02F06B8F4ED9B854F32BDB6663BAC` | mean/std、four L1 records、checkpoint/config summary |
| A13 | `summary_l1.png` | 39519 | `C7A17CC82EE02DB89DB5CD7EC1E7C5404E36D16FADE096B3402F587701EFAC26` | aggregate L1 visualization |

## 6. Local immutable manifest：LIBERO/Franka rollout bundle

目录：`artifacts/libero_franka_true_rollout_v1/`。`summary.json` 与 model/no-op video 共同支持 task-0 70-step rollout 的 `0.0 reward / false success` 边界；zero-reference 是 no-op 对照，不是 demonstration ground truth。

| ID | 相对路径 | 字节数 | SHA-256 | 角色 |
| --- | --- | ---: | --- | --- |
| L01 | `client.log` | 2717 | `BC1B7FE6E54735B4623062D151D47667BD418F4F7A46B6CC471EC1F961869572` | client checkpoint/config、task summary、result paths |
| L02 | `index.html` | 1168 | `9CF3D32F8B22444F38AEF7CD27511E6783A9B149240488AF13DDBCBEC762311F` | rollout dashboard |
| L03 | `model_policy/model_policy_metrics.png` | 95686 | `D5EDB3193BCD2257771304CA97CB226A55CA0567267A9CC209DAC810D7C7CC28` | model rollout metric plot |
| L04 | `model_policy/model_policy_rollout.mp4` | 211605 | `B8C14912B1202085581286B05949D8957A5AA77E040AE52AB91FFC0F67A60ED6` | model rollout video |
| L05 | `serve.log` | 2679 | `FF0B39D7B87D604D86486A0088E7CF7FD2D3EA99CB151B99FD5D9B9E60AACD2A` | Orbax restore、norm-stats、8399 listen/connection |
| L06 | `summary.json` | 1450 | `341E77110D75E50B601A078923F51EF8FA39AAA045FA491843A1003B0320E1DB` | model/no-op reward/success summary |
| L07 | `zero_reference_vs_model.mp4` | 269652 | `226953734221483E03B509C03AE997B98C256722B9281A78A39C86D226D2ECE1` | model vs no-op comparison video |
| L08 | `zero_reference/zero_reference_metrics.png` | 68808 | `0214FC58F66A3CEFFB9A4B2F652369F76F9C3620E96ED4EF8D06FE5443ED4020` | no-op metric plot |
| L09 | `zero_reference/zero_reference_rollout.mp4` | 70571 | `27BFAB393ECF92E3092D768A6294759287D6F779527EEEB2CE6160F26E7063FA` | no-op rollout video |

## 7. Gate reconciliation

| Gate | 状态 | 直接证据 | 当前不能推出 |
| --- | --- | --- | --- |
| local deployment/code manifest | `PASS` | D01、C01–C03 的 bytes/SHA 已重算 | 不能推出远端 checkpoint 与本地文件完全同一版本 |
| ALOHA action-eval artifact manifest | `PASS WITH WARNING` | A01–A13 全部存在且逐文件哈希 | offline action L1 不是 task success；checkpoint binary 仍未哈希 |
| LIBERO rollout artifact manifest | `PASS WITH WARNING` | L01–L09 全部存在且逐文件哈希 | `0/1` 仍不能归因于单一 action/controller/preprocess 原因 |
| `pi0_aloha_sim/params` binary manifest | `UNVERIFIED` | 仅有 deployment path、restore log、历史 11.189 GiB/21 files | 无逐文件 SHA、Merkle root 或 remote revision |
| `pi0_aloha_sim` norm-stats manifest | `UNVERIFIED` | serve log 有 loaded path | stats 文件内容与 SHA 未落档 |
| `pi05_libero/params` binary manifest | `UNVERIFIED` | 仅有 deployment path、restore log、历史约 11.6 GiB | 无逐文件 SHA、Merkle root 或 remote revision |
| `pi05_libero` norm-stats manifest | `UNVERIFIED` | serve log 有 loaded path | stats 文件内容与 SHA 未落档 |
| private fine-tune lineage | `UNVERIFIED` | 当前 bundle 只指向 official configs | 不能把 official checkpoint 说成 Qwen/LoRA 个人训练结果 |
| ownership | `PENDING` | 无 pre-snapshot diff 与真实口述 | 不能使用“我实现了整个 deployment/checkpoint” |

## 8. 面试安全口径

### 30 秒回答

“我把本地 OpenPiVLA deployment bundle 做了逐文件 SHA-256 manifest：ALOHA action-eval 的 13 个文件、LIBERO rollout 的 9 个文件，以及部署记录和 3 个运行脚本都能在本地直接重算。与此同时，我确认 `pi0_aloha_sim` 和 `pi05_libero` 的 `params`、checkpoint norm-stats 只出现在远端 `/data/msz/...` 路径，当前 Windows 工作区没有这些目录，所以我不会伪称已经有 checkpoint binary SHA。现有日志能证明官方 checkpoint 当时被 Orbax restore 并完成 server/client rollout，但不能闭合远端权重不可变性，也不能证明 private Qwen3-VL/LoRA lineage 或个人 ownership。”

### 高频追问

1. **为什么不把 `DEPLOYMENT.md` 的 11.189 GiB/21 files 当 manifest？** 因为它是历史摘要，没有每个文件的 path/size/SHA，无法检测目录替换或缺文件。
2. **本地视频和 summary 的 SHA 能证明 checkpoint 没变吗？** 不能；它们只能冻结结果 bundle。checkpoint binary 与结果 artifact 是两个独立 lineage 节点。
3. **norm stats 是否已经 frozen？** 只 frozen 了 server log 中的加载路径和事件；stats 内容、文件列表和 SHA 尚未可读。
4. **这是否影响 `0 reward / false success` 的结论？** 不影响该次本地 rollout 产物的记录；它影响的是跨机器重跑、checkpoint identity 和根因归因的强度。
5. **下一步怎样闭合？** 在原远端环境以只读方式导出 `params` / `assets` 逐文件清单、SHA、OpenPI commit、processor/tokenizer revision，并把 manifest ID 写入 server/client summary。

## 9. 下一步

1. 如果远端仍可访问，只读导出两个 checkpoint 的 `params` 与 `assets` manifest，不复制权重进本仓库。
2. 给 server/client 启动脚本保存完整 argv、UTC timestamp、shared run UUID 和 request IDs。
3. 若远端不可再访问，下一 bounded slice 转向 matched LIBERO failure probe，固定 observation、flip/resize、state axis/unit、7D action order、normalizer、replan、controller 与 scorer。
4. 本页不新增题卡、不改变 mastery；`PROJ-OPENPIVLA-007/008` 仍保持 `unseen`。

## 参考文献（References）

1. Local deployment record：`C:\Users\mousongzhe\Project\openpivla_deployment\DEPLOYMENT.md`（D01）。
2. Local ALOHA artifact bundle：`artifacts/lerobot_action_eval_aloha_sample_real_v2/`（A01–A13）。
3. Local LIBERO artifact bundle：`artifacts/libero_franka_true_rollout_v1/`（L01–L09）。
4. Local evaluation/rollout scripts：`scripts/eval_lerobot_action_server.py`、`scripts/run_lerobot_action_eval.sh`、`scripts/run_libero_true_rollout.py`（C01–C03）。
5. [OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html)。
6. [OpenPiVLA ALOHA Action-Level Eval Load Gate](openpivla_aloha_action_eval_load_gate.html)。
