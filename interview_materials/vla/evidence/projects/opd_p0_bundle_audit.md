# OPD / VLM Grounding P0 Bundle Audit：Data Route / Distillation / Holdout

> 状态：`p0_audited / protocol-bounded / raw-prediction-missing / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计五 expert 数据构造、student route metadata、coldstart/online OPD summary、10k raw-holdout manifest/table 和 point scorer 记录；不把组合路线结果升级为单因果 OPD uplift。

## 1. 结论

OPD 已具备可定位的数据和训练机制证据：image-hash split、五 expert 配额、route metadata、coldstart teacher rollout、student-rollout/full-vocabulary KL、OPD5000 checkpoint 曲线、10k holdout quota 和 leakage audit 均有本地脚本/表格/summary。结果可以绑定到具体 checkpoint、format/pool 子集和 protocol-limited scorer。

P0 仍未闭合：模型权重、optimizer/RNG、完整 raw predictions、统一 scorer manifest、旧版 OPD final 与新版 OPD5000 的单一 lineage、SFT-only/single-teacher/no-synthetic ablation、operator/reviewer 和逐文件 ownership 缺失。

```text
P0 status = PARTIAL / PROTOCOL-BOUNDED
eligible causal claims = 0
eligible checkpoint/result ownership = 0
allowed = data route, teacher/student mechanism, leakage gate, bounded tables
forbidden = “OPD alone caused uplift”, “I own OPD5000 checkpoint”, “static holdout = robot success”
```

## 2. P0 gate matrix

| P0 字段 | 当前证据 | 状态 | 安全解释 |
| --- | --- | --- | --- |
| data split / quota | 800k/20k builder、image-hash split、五 expert、10k holdout quota | `PRESENT` | 可讲数据合同与 leakage gate |
| route metadata | target/candidate expert、seen/unseen、boundary/format-conflict | `PRESENT` | metadata route，不称 learned router |
| teacher/student training | coldstart500、student rollout、full-vocab KL、skip=64k | `PRESENT WITH WARNING` | 可讲训练机制；coldstart-only 增益未隔离 |
| checkpoint curve | ckpt1000–5000 by-format/by-pool tables | `PARTIAL` | 必须绑定 pool；不同指标最佳 checkpoint 不同 |
| raw holdout | 10k manifest、dedupe/leakage audit、aggregate tables | `PARTIAL` | raw predictions/per-sample JSON 缺 |
| scorer/protocol | original strict、protocol-fixed strict、lenient point tables | `PARTIAL` | prompt/scorer hash 和统一版本仍缺 |
| model lineage | OPD final 与 OPD5000 new-experts 分开报告 | `CONFLICT OPEN` | 不能拼成单调训练曲线 |
| ablation | 无 SFT-only、single-teacher、no-synthetic、ratio 对照 | `MISSING` | 不能归因 OPD 单因素 |
| checkpoint/optimizer | artifact manifest 明确排除 weights/optimizer/raw predictions | `MISSING` | 不称 checkpoint/result-owned |
| ownership | 13-row ledger，`msz136`/`mousongzhe` scaffold 与后续同步分开 | `PENDING` | Git author 不等于逐文件 ownership |

## 3. 已核验的结果边界

- 10k holdout quota：box 6,100、point 1,400、text 2,500；unique images 8,251；三类 leakage fingerprint 为 0，但重复图片路径不等于重复样本；
- OPD5000 ckpt5000 的 Box Acc@0.5=`0.5238`、Point Hit@100=`0.8729`、Text exact=`0.8724`，必须带 pool/format/protocol；
- box IoU 最佳点在 ckpt3000，keepalive text 在 ckpt4000，不能称 ckpt5000 全局最佳；
- 旧版 OPD final 与新版 OPD5000 ckpt5000 是不同 run lineage；
- 静态 grounding/VQA holdout 不等于 VLN/ObjectNav 或机器人闭环成功。

## 4. 面试可用与禁用表述

可以说：

> “我把数据先按 image-hash 做隔离，再把 reasoning、object、region、spatial relation 和 RoboPoint 组织成五个 expert；student 里保留 route metadata，先做五教师 coldstart，再做 student rollout/full-vocabulary KL。评估时我把 10k raw-holdout 按 box/point/text 和 original/protocol-fixed/lenient scorer 分开，且不同 pool 的最佳 checkpoint 不同。由于权重、raw predictions、统一 scorer 和 matched ablation 未闭合，我把这些称为组合路线的 protocol-bounded evidence，不把它归因成 OPD 单独 uplift。”

不能说：

1. OPD 单独带来全部提升；
2. OPD5000 ckpt5000 是所有任务的全局最佳；
3. 报告数字是本人拥有的可加载 checkpoint 结果；
4. 10k static holdout 等于真实机器人/导航成功率；
5. `msz136`/`mousongzhe` Git author 自动证明所有文件由本人独立实现。

## 5. 关闭 P0 的最小动作

1. 将 OPD final、coldstart500、OPD5000 的 code/config/data/scorer/checkpoint parent SHA 收敛为 lineage manifest；
2. 同一 holdout、n 和 scorer 重跑 base/SFT-only/coldstart-only/OPD，并保留 raw predictions/per-sample JSON；
3. 固定三套 point scorer、prompt hash 和 parser tests；
4. 候选人回答 `OWN-OPD-001`，明确数据、训练、评估、运行和工具协作边界。

在这些字段闭合前，OPD 保持 `PARTIAL/WARN`，不改变 `PROJ-OPD-*` 或通用题卡 mastery。

## References

1. [OPD Claim–Evidence Inventory](opd_claim_evidence_inventory.md)
2. [OPD Ownership Ledger](opd_ownership_ledger.md)
3. [五项目 P0 Artifact Intake Contract](../p0_artifact_intake_contract.md)
