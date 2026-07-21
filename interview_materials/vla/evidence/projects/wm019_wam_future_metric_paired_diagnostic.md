# WM-019 WAM Future-Image Metric Paired Diagnostic（CoffeePressButton）

> 状态：`paired_metric_diagnostic / offline-future-image / checkpoint-unverified / WARN`  
> 计算日期：2026-07-18  
> 证据截止：2026-07-18  
> 范围：只比较同一离线 episode/prompt、同一 sample indices、同一 seed=7 下 `iter_000005000` 与 `iter_000010000` 的 future-image PSNR/SSIM JSON；不把视觉指标升级为 action validity、simulator success 或 real success。

## 1. 输入与协议

| 字段 | 值 |
| --- | --- |
| manifest | `cosmos_policy_eval_like_dreamdojo_20260605/manifest.json` |
| manifest SHA-256 | `8C4872F711897F718621C7AE8A6DF49EEDDE759CBECEDE530A3D82ABA819EC71` |
| prompt | `press the button on the coffee machine to serve coffee` |
| episode source | `/data/msz/wm/wm_data/.../ep=16--success=True--regen_demo.hdf5`（远端引用） |
| sample count | 1 |
| future frame count | 12 |
| sample indices | `[11230,11235,11241,11246,11252,11258,11263,11269,11275,11280,11286,11292]` |
| future indices | `[32,37,43,48,54,60,65,71,77,82,88,94]` |
| chunk / steps | `32 / 4` |
| seed | `7` |
| metric implementation | SSIM 标记为 `skimage`；LPIPS 为 `null` |

两个 metrics JSON 的 checkpoint 字段均为 `/data/msz/.../iter_000005000` 或 `/data/msz/.../iter_000010000` 远端路径，本地没有对应 binary/hash。

## 2. Immutable metric inputs

| label | metrics JSON | SHA-256 | summary SHA-256 |
| --- | --- | --- | --- |
| `iter_000005000` | `iter_000005000/0000_metrics.json` | `0FD008BBAD68A9FDD273A7E1DC7659F0F6B66927194671AC112FA5DEDAF72C18` | `9BDC8A438153DB2ED02BAC77DDF5964A7A3BA241BDEEB526D7993507D9CDDDAE` |
| `iter_000010000` | `iter_000010000/0000_metrics.json` | `C9AB7F04AFD9C9057CC548BF0176285E001BA778BCD37DC4FB7D857E29BAEC9D` | `805112AB530C63DD0293E918731C3721707EC508B9239D7EE3F2DB935FC868A1` |

这是一组离线 future-image prediction metrics，不是上一份 seed=195、300-step action-rollout trace；两种协议必须分开记录。

## 3. Metric comparison

| metric | iter 5000 | iter 10000 | delta (10000−5000) | unit/notes |
| --- | ---: | ---: | ---: | --- |
| future-only PSNR | 8.5813418454 | 8.2140051576 | -0.3673366878 | 12 future frames、单 sample |
| future-only SSIM | 0.0452700028 | 0.0428580477 | -0.0024119550 | `skimage`、单 sample |
| with-condition PSNR | 15.5366232419 | 15.1975432224 | -0.3390800195 | 13 frames，含 condition frame |
| with-condition SSIM | 0.1187107718 | 0.1164843517 | -0.0022264201 | `skimage`，含 condition frame |
| LPIPS | null | null | — | 没有 LPIPS 结果 |

PSNR 依赖像素误差，常见形式为：

\[
\operatorname{PSNR}=10\log_{10}\frac{MAX_I^2}{\operatorname{MSE}(I,\hat I)}.
\]

本表的 delta 只表示该离线 sample、该 scorer 和该 checkpoint 引用下的视觉指标差异；它不能证明长时序 action consequence 或策略优劣。

## 4. Evidence interpretation

可以支持：

- 两个 checkpoint label 在同一离线采样协议下都有可读的 PSNR/SSIM JSON；
- `iter_000010000` 在该单 sample 的 future-only 与 condition-inclusive 指标都低于 `iter_000005000`；
- metric 输出记录了 frame count、future-only/condition-inclusive 分层和 scorer implementation。

不能支持：

- “训练到 10000 steps 后视觉质量下降是 checkpoint 的因果结论”：本地没有 checkpoint binary、训练 lineage 或重复 samples；
- “PSNR/SSIM 下降说明 action policy 变差”：没有 action target、controller、closed-loop episode；
- “CoffeePressButton success 下降”：离线 episode source 与 rollout episode protocol 不同，且这里没有 simulator success predicate；
- “WAM benchmark 或 real robot 泛化”：样本数为 1，远端 episode source，缺 denominator 与 multi-seed。

## 5. WM-019 ladder placement

| 层级 | 当前证据 | 仍缺 |
| --- | --- | --- |
| teacher-forced/offline future-image proxy | 12 future frames、PSNR/SSIM、两个 checkpoint label | checkpoint binary/hash、重复 sample、per-offset scoring |
| open-loop action rollout | 另有 seed=195 action trace，但不与本页协议合并 | target-based per-offset error、action sensitivity |
| simulator closed loop | 本页没有 success predicate | 多 episode denominator、controller/reset/init、checkpoint |
| real closed loop | 没有 real hardware artifact | 全部 hardware trace/safety fields |

## 6. 下一最小补件

1. 绑定本地或不可变远端 checkpoint hash、processor/normalizer/config revision。
2. 对同一 checkpoint 收集多个 episode/sample 和 fixed-init/seed manifest。
3. 将 future-image metric 与 action trace、simulator predicate 做 matched checkpoint paired validation。
4. 保持 PSNR/SSIM 为 proxy，不写入 WAM success/uplift 或个人简历结果。

## 参考来源

1. [WAM Artifact Manifest](wm019_wam_artifact_manifest.html)。
2. [WAM Action-Trace Paired Diagnostic](wm019_wam_action_trace_paired_diagnostic.html)。
3. [WM-019 Project Metric Artifact Gate](../../sources/vol_04_wm019_project_metric_artifact_gate.html)。
4. [WM-019 Metric Source Freeze](../../sources/vol_04_wm019_metric_boundary_source_freeze.html)。
