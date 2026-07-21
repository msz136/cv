# UWM / LIBERO P0 Bundle Audit：Protocol / Data Pipeline / Remote Result

> 状态：`p0_audited / libero-user-confirmed / robocasa-raw-rollout-backed / checkpoint-unverified / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计 UWM/LIBERO local scripts/reports/protocols、DataLoader-only smoke、user-confirmed remote summary 和 RoboCasa debugging boundary；不把远端 summary 升级为本地可复算 benchmark。

## 1. 结论

UWM/LIBERO 的训练入口、task map、fixed-pruned-init/5-step warmup、normalizer/action shape、rollout evaluator、DataLoader stall benchmark 和 RoboCasa patch 均有 local-direct 或 report-supported 入口。用户确认的 fixed-pruned-init `186/250=0.744` 仍只有 per-task summary，本地没有对应 checkpoint、250 episode JSONL、失败视频或 scorer。RoboCasa 证据则已显著增强：[ActionHeadFix 30-Epoch Train-to-Closed-Loop P0 Audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html) 冻结了一条8卡3930-step run、12D normalizer和八份54-scenario raw rollout JSON；full h1/h2/h4/h5/h8为`2/54、1/54、0/54、1/54、1/54`，三组h5 input ablation为`2/54、2/54、1/54`，全部env errors为0。这证明训练—评测失败链可重算，仍不是 RoboCasa benchmark success。

P0 仍未闭合：LIBERO结果 provenance、论文 Table II comparability、same-checkpoint reset paired run、GPU matched A/B，以及RoboCasa produced checkpoint/env-scorer revision/videos和个人 ownership 都保持未确认。

```text
P0 status = PARTIAL / USER-CONFIRMED-REMOTE-FINAL
eligible local benchmark claims = 0
eligible result ownership claims = 0
allowed = protocol engineering, DataLoader-only diagnosis, RoboCasa raw-rollout failure taxonomy
forbidden = local 0.744 reproduction, Table II 0.79 comparison, RoboCasa success, UWM architecture authorship
```

## 2. P0 gate matrix

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| task / rollout protocol | five LIBERO-10 task map、50 rollouts/task、600-step、5-step warmup、success summary | `PRESENT` | 可讲 protocol tuple |
| checkpoint / normalizer | launcher/path contract、report 引用 | `MISSING` | 远端 path 不是 local weight/hash |
| fixed-pruned-init result | user-confirmed JSON：186/250、per-task summary | `USER-CONFIRMED-REMOTE` | 只能说用户确认的项目 summary |
| reset-style comparison | user-confirmed 232/250 | `PROTOCOL-DIAGNOSTIC` | 不当作模型 uplift 或正式成绩 |
| Table II comparison | paper OOD init、+0.03 shift、background removal、3 seeds | `NON-COMPARABLE` | 不能说只低 4.6pp 或复现论文 |
| episode evidence | 无 250 episode JSONL、视频、terminal reason | `MISSING` | 不可本地复算 success |
| scorer / init manifest | 脚本和报告说明字段 | `PARTIAL` | exact init index/normalizer/scorer hash 缺 |
| DataLoader diagnosis | finite/infinite/preload A/B；p95 wait 13.862s→0.194s | `SMOKE-BOUNDED` | 可讲 DataLoader-only wait，不报 full GPU uplift |
| RoboCasa actionheadfix train/eval | 30-epoch train log/summary、12D normalizer、8×54 raw rollout JSON | `RAW-ROLLOUT-BACKED / CHECKPOINT-UNVERIFIED` | 讲 train→closed-loop failure；不称 benchmark success |
| ownership | 13-row ledger、snapshot/working-tree/recovery 分层 | `PENDING` | 需逐文件、运行者、审查者确认 |

## 3. 已核验的协议边界

- 项目 fixed-pruned-init `186/250=0.744` 与 reset-style `232/250=0.928` 使用不同初始化协议；
- UWM Table II 约 `0.79` 使用 OOD initialization、+0.03 object-init shift、背景移除和 3 个 seed；
- 因此 `0.744 vs 0.79` 不能解释为模型差距，`0.928→0.744` 不能解释为权重退化；
- DataLoader-only smoke 中 preload+infinite 将 p95 wait 从约 13.86s 降至约 0.19s，但没有 matched GPU training throughput/memory 证据；
- RoboCasa 已有一条项目协议下的8×54 raw success bundle，但 produced checkpoint binary、env/scorer revision、videos和benchmark comparability仍缺；只能称 contract debugging 与 failure audit。

## 4. 面试可用与禁用表述

可以说：

> “我主要做的是训练到闭环评估的协议工程：固定 LIBERO task map、pruned-init、warmup、normalizer、horizon、rollout 数和 success predicate，并用 DataLoader-only A/B 定位 zarr 小 chunk 的周期性等待。项目材料里有用户确认的 fixed-pruned-init 186/250 summary，但 checkpoint、250 episode、scorer 不在本地，所以我不称它为 local raw reproduction；reset-style 和 UWM Table II 也按协议分开。RoboCasa 仍是跨 benchmark contract 调试。”

RoboCasa 追问时补充：actionheadfix 的一条30-epoch run已经有八份54-scenario raw JSON，能说full-h4 `0/54`、contact `45/54`与0 env errors；不能说checkpoint binary已验证、接触等于成功或input ablation产生因果提升。

不能说：

1. 本地已复现 LIBERO 0.744；
2. 0.744 与 Table II 0.79 严格可比；
3. reset-style 0.928 证明模型更好；
4. DataLoader-only wait 降低等于 GPU training throughput 提升；
5. RoboCasa benchmark 已完成；
6. UWM shared diffusion architecture 是个人原创。

## 5. 关闭 P0 的最小动作

1. 获取 5-task strict run 的 checkpoint、normalizer、exact config、init index、250 episode JSONL、失败视频和 run manifest；
2. 对同 checkpoint 做 reset-style vs fixed-pruned-init paired run，记录每 episode seed/init/scorer；
3. 做 30–100 step GPU matched DataLoader A/B，保存 data_wait/train/total/memory/throughput；
4. 候选人回答 `OWN-UWM-001`，明确 launcher、patch、远端运行、诊断和工具协作边界。
5. 对 actionheadfix run 回传 `models.pt` SHA/fresh-load parity、完整 train JSONL、RoboCasa/env/scorer revision和episode video locator。

在这些字段闭合前，UWM/LIBERO 保持 `PARTIAL/WARN`，不改变 `PROJ-UWM-*` 或通用题卡 mastery。

## References

1. [UWM/LIBERO Claim–Evidence Inventory](uwm_libero_claim_evidence_inventory.md)
2. [UWM/LIBERO Ownership Ledger](uwm_libero_ownership_ledger.md)
3. [五项目 P0 Artifact Intake Contract](../p0_artifact_intake_contract.md)
4. [UWM/LIBERO/RoboCasa Transfer Evidence Freeze](../../sources/vol_05_uwm_libero_robocasa_transfer_evidence_freeze.md)
5. [UWM RoboCasa ActionHeadFix 30-Epoch P0 Audit](uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.md)
