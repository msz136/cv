# WM-019 WAM P0 Bundle Audit：CoffeePressButton

> 状态：`p0_audited / partial / checkpoint-unverified / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 范围：只审计仓库已登记的 CoffeePressButton diagnostic bundle、paired action trace 和 future-image proxy；不新增 benchmark 结果，不把 episode 0 升级成成功率，也不确认个人 ownership。

## 1. 审计结论

该 bundle 已经满足“存在可读取诊断 artifact”的最低门槛，但没有满足 `ELIGIBLE` 的 P0 结果门槛。可以复核 base/trained 两份 manifest、300×7 action trace、失败视频、rollout log 以及一组单样本 future-image PSNR/SSIM；两个 manifest 的 checkpoint 仍是远端路径，本地没有 binary/hash，metric scorer、完整 denominator、run lineage 和候选人角色也没有闭合。

因此本页的 promotion 结果是：

```text
P0 status = PARTIAL
eligible metric claims = 0
eligible ownership claims = 0
allowed = diagnostic/interface evidence
forbidden = uplift, benchmark success rate, checkpoint-verified comparison, personal authorship
```

## 2. Bundle identity

| side | task / episode | seed | env_seed | horizon | open-loop | denoise | manifest | action trace |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| base | CoffeePressButton / 0 | 195 | 0 | 300 | 16 | 5 | `63A518...3A86` | `C6A362...85D` |
| trained | CoffeePressButton / 0 | 195 | 0 | 300 | 16 | 5 | `809AE4...5CC` | `9C6A4F...2D` |

两侧均记录 `OSC_POSE`、`control_delta=true`、三路 camera 和 `success=false`。它们是同一 episode protocol 下的 paired diagnostic，但 checkpoint binary 不在当前工作区。

## 3. P0 field gate

| P0 字段 | 当前证据 | 状态 | 不能推断 |
| --- | --- | --- | --- |
| checkpoint identity | manifest 中有 base/trained 远端 path | `PARTIAL` | 本地可加载、binary 相同/不同的完整 hash |
| parent/run lineage | 输出目录、log 与 path bridge 有线索 | `PARTIAL` | 训练命令、parent checkpoint、完整 run DAG |
| code/config/data SHA | manifest/config 字段和既有项目 snapshot | `PARTIAL` | 本次 rollout 使用的所有文件内容与版本 |
| protocol tuple | task、episode、seed、env_seed、horizon、controller、camera、open-loop、denoise | `PRESENT` | 多 episode、multi-seed 或跨任务性能 |
| raw action output | base/trained `actions.jsonl`，各 300 行 | `PRESENT` | action label loss、target fit 或 controller correctness |
| raw video | 两条失败视频，trained video 有 alternate output root | `PRESENT` | video 差异的 checkpoint 因果归因 |
| scorer / denominator | trace integrity 与 paired MAE/RMSE 脚本结果 | `PARTIAL` | action MSE、success rate、完整 suite aggregate |
| invalid policy | JSONL 中 finite/row/t-range 检查 | `PARTIAL` | benchmark 级 invalid handling contract |
| operator / reviewer | 未登记候选人、远端 operator 和 reviewer | `MISSING` | “我运行/我验收/我负责结果” |
| ownership diff | ledger 已列候选问题，但没有候选人确认 | `PENDING` | 个人原创 architecture 或逐文件实现 |

## 4. Deterministic checks already supported

- base/trained 均为 300 行，`t=0..299`；
- `policy_action7` 均为 `300×7`，`env_action` 均为 `300×12`；
- 两侧 policy action 均未发现 NaN/Inf；
- 两侧 `success_after_step=True` 次数均为 0，reward sum 均为 0.0；
- paired policy trace 的 MAE=`0.3100783611`、RMSE=`0.3906446459`；这只是几何差异，不是 action-label loss；
- future-image proxy 只有单样本、12 个 future frames，PSNR/SSIM 不能与 action rollout 或 success 合并解释。

这些检查证明文件结构和诊断计算可复核，不证明 checkpoint 内容、动作语义、控制器闭环或模型优劣。

## 5. 面试可用与禁用表述

可以说：

> “我能从一组 CoffeePressButton diagnostic bundle 复核 base/trained 的 rollout manifest、action trace、controller/camera/horizon 字段和失败视频；我还检查了 trace 的 shape、finite 和逐步差异。由于 checkpoint 仍是远端 path，缺少完整 scorer、denominator 和 ownership，所以我把它定位为接口与失败诊断证据，不把它说成 benchmark uplift。”

不能说：

1. 本地已经 load/hash 验证 base 或 trained checkpoint；
2. trained 比 base 成功率更高/更低；
3. episode 0 失败等于 WAM 0-success；
4. `0.3100783611` 是 action MSE 或训练 loss；
5. 上游 Cosmos slot/mask/routing 是个人原创；
6. 文件存在或 Git author 自动等于本人实现和运行。

## 6. 关闭 P0 的最小动作

按优先级只补一项即可继续：

1. 为 base/trained 提供不可变 checkpoint hash、processor/normalizer/config SHA；
2. 为同一 protocol 收集完整 episode manifest、success predicate 和 denominator；
3. 提供 prediction/label 与 metric script，使 action error 可重算；
4. 候选人回答 `OWN-WAM-001`，明确设计、实现、协作、工具、运行和审查角色。

在上述字段闭合前，本 bundle 保持 `PARTIAL/WARN`，不进入简历强 claim，也不改变 `PROJ-WAM-001` 或通用题卡 mastery。

## References

1. [WM-019 WAM Artifact Manifest](wm019_wam_artifact_manifest.md)
2. [WM-019 Action-Trace Paired Diagnostic](wm019_wam_action_trace_paired_diagnostic.md)
3. [WM-019 Future-Image Metric Paired Diagnostic](wm019_wam_future_metric_paired_diagnostic.md)
4. [WAM Ownership Ledger](wam_ownership_ledger.md)
5. [五项目 P0 Artifact Intake Contract](../p0_artifact_intake_contract.md)
