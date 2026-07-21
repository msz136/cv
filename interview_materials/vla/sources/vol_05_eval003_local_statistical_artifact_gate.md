# VOL 05 EVAL-003：本地统计 Artifact Gate

> 状态：`audited / 3 projects / WARN`  
> 审查日期：2026-07-17  
> 证据截止：2026-07-17  
> 目标：把 UWM、OpenPiVLA、OPD 中与成功率/二元指标有关的本地 artifacts 分层，决定哪些数字可以做诊断性区间，哪些必须 fail-closed。

## 问题与结论

EVAL-003 需要的不只是一个百分比，而是 observation unit、分母、checkpoint/processor lineage、task/seed/init、success predicate、raw record 和停止规则。本 gate 只审计当前工作区能直接读取的文件，不尝试连接远端、不把报告中的路径当作本地 artifact，也不把静态 grounding 指标改名为 robot rollout success。

结论先行：

| 项目 | 当前可读证据 | 统计单元 | EVAL-003 判定 | 面试安全表述 |
| --- | --- | --- | --- | --- |
| UWM/LIBERO | 用户确认的 `186/250` JSON、同步 manifest、评估脚本摘要；无 250 条 episode trace | 项目汇总声称是 episode，但 task/init/seed 记录不在本地 | `WARN / naive-only` | 可说“固定项目协议下的 user-confirmed summary”；不能说 cluster-aware CI 或本地 raw verified |
| OpenPiVLA | formal reproduction report、官方 checkpoint 的少量 ALOHA/LIBERO rollout；`97.4%` 只有 archive table | archive 的 suite aggregate，缺 denominator lineage、trial/seed/init 和 raw episode | `FAIL CLOSED` for 97.4 CI | 可说“归档报告汇总为 97.4%”；不能把它绑定到 formal Qwen checkpoint 或声称高于 official |
| OPD | ckpt5000 `metrics.json`、10k evalset manifest、dedupe audit、按格式/按 pool n | 静态 row/metric-specific observation；不是 episode | `WARN / metric-specific only` | 可报告 `box/point/text` 各自 n 与指标；不能称机器人 rollout success 或做统一 aggregate CI |

因此，本 gate 不提升任何简历强度，不更新 mastery，不生成 EVAL-004 paired significance 或 EVAL-005 aggregation。

## 证据等级与门槛

本报告沿用项目证据官的 claim contract：`local-direct` 表示文件可直接读取，`report-supported` 表示报告有结论但底层 raw artifact 缺失，`user-confirmed-remote-final` 表示用户确认的远端结果，`archive-summary-only` 表示只有归档汇总，`fail-closed` 表示不能安全计算或比较。

要把一个二元结果提升到 C3，需要同时具备：immutable checkpoint/processor/normalizer、明确的数据/环境版本、每个 observation 的 raw record、success predicate/scorer、task/seed/init 或等价 cluster 字段、可重算 summary，以及个人 ownership 边界。当前三个项目均至少缺其中一项。

## 统计映射

对同一 observation unit，记成功数为 (k)、有效样本数为 (n)，点估计为：

\[
\hat p = k/n
\]

这里的 (n) 只能来自同一 protocol 下的有效记录；失败排除、不同 task 的混合或未知分母都会改变 estimand。实现上，UWM 的 `186/250` 和 OPD 的按格式 n 可以做 naive Wilson smoke，但不能由此证明独立同分布或消除 task/image clustering。

对 95% Wilson 区间，本 gate 只把结果标为“诊断性”而不是最终 benchmark CI：

\[
\left[
\frac{\hat p+z^2/(2n)-z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n},
\frac{\hat p+z^2/(2n)+z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n}
\right]
\]

其中 (z=1.96)。数值由 SciPy `binomtest(...).proportion_ci(method="wilson")` 对当前 (k,n) 计算；它没有替代 cluster-robust 或 metric-specific dependence 分析。

## UWM / LIBERO：汇总可读，episode bundle 缺失

### 直接证据

| 文件 | 直接观察 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `Project/report/uwm_libero_strict_eval_recovery_20260702/final_strict_eval_user_confirmed_20260705.json` | 5 task × 50、`successes_assuming_250_total=186`、macro/micro `0.744`，并记录 reset-style `232/250` | 用户确认的 protocol-limited summary、task-level counts | 250 条 episode raw、每条 init/seed、checkpoint/normalizer hash、scorer 可复算性 |
| `.../sync_manifest.json` | 记录远端 eval root、脚本 hash、`episodes_written=18` 的早期 partial 状态；remote host 后续不可达 | 远端路径和协议合同、snapshot 边界 | 不能把 partial remote check 当作最终 250 条结果 |
| `Project/wm/.../scripts/uwm_libero_rollout_eval.py` | 本地脚本定义 `libero_fixed_init`、5-step warmup、50 rollouts/task 和 summary 字段 | 评估 protocol contract | 当前本地脚本不能证明远端执行输出仍与其完全一致 |

### 统计判定

按用户确认 summary 的 (k=186,n=250) 做一个明确标注为 naive 的 Wilson smoke：

| 结果 | k | n | 点估计 | 95% naive Wilson |
| --- | ---: | ---: | ---: | ---: |
| fixed-pruned-init summary | 186 | 250 | 0.744000 | [0.686493, 0.794122] |

这个区间只回答“若把 summary 当成 250 个独立 Bernoulli episode，会得到什么诊断区间”。它不能替代 task/seed/init cluster-aware CI；也不能把旧的 `232/250=0.928` 与新的 fixed-pruned-init 结果当作同一 protocol 的 paired comparison。下一步若要升 gate，必须导出 250 条 episode JSON/视频索引、init manifest、checkpoint/normalizer hash 和 scorer version。

## OpenPiVLA：97.4% 归档汇总 fail-closed

### 直接证据

| 文件 | 直接观察 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `Project/openpivla_deployment/artifacts/vla_formal_reproduction_report_20260617.html` | formal report 记录三条 100k training complete；归档 `224_h10_40000` 表含 spatial/object/goal/LIBERO 汇总，整体标作 97.4% | 报告中确实存在 archive-summary-only 数字；formal trainer path 可读 | 97.4 对应哪个 checkpoint、raw episode、trial/seed/init、success predicate 或与 formal Qwen run 的 lineage |
| `Project/openpivla_deployment/artifacts/libero_franka_true_rollout_v1/summary.json` | 官方 `pi05_libero` 单任务/单 episode 诊断，`success=false` | 官方 checkpoint 的局部 rollout 接口证据 | 不能绑定到 97.4，也不能代表四套件 benchmark |
| `Project/openpivla_deployment/artifacts/aloha_sim_real_rollout_20260608_154324/summary.json` | 官方 `pi0_aloha_sim` 3 episodes 的小规模 rollout summary | 少量官方 baseline rollout 与动作链诊断 | 不能证明 formal Qwen checkpoint 或 archive 97.4 |
| `Project/openpivla_deployment/repro_train/` 与 `artifacts/vla_train_repro/` | formal scripts、configs、smoke summaries 可读；正式 checkpoint/log 仍以 `/data/msz/...` 远端路径引用 | 训练合同、数据字段、保存策略 | 本地没有 immutable checkpoint、raw formal eval、97.4 episode records 或 archive→train→eval lineage |

### 统计判定

`97.4%` 没有可审计的 (n)。因此本 gate 不计算 CI、不比较 official `96.85`、不把 archive table 解释为当前 formal run 的结果。最小补证据链为：

```text
# 证据链示意（不可执行；每一跳都需要 immutable artifact）
archive_run_id
  -> model class / base checkpoint
  -> train run + config SHA
  -> checkpoint SHA + processor/normalizer SHA
  -> eval suite / task order / trials / seeds / init states
  -> raw episode records + success predicate + summary
```

在该链闭合前，面试中只能说“归档报告汇总为 97.4%，当前 raw provenance 未闭合”。

## OPD：metric-specific row evidence，不是 rollout success

### 直接证据

| 文件 | 直接观察 | 能支持 | 不能支持 |
| --- | --- | --- | --- |
| `muxi/point/eval_raw_holdout_v1/.../opd5000_ckpt5000/metrics.json` | `overall.n=10000`；by-format 为 box `n=6100`、point `n=1400`、text `n=2500`；保存 format pass、IoU、Hit@100、text exact | 同一 ckpt5000/同一 raw-holdout 下的 metric-specific count 与结果 | prediction file 仍指向远端 `/data/msz/.../predictions.jsonl`；不能把 row 当 episode |
| `muxi/report/raw_holdout_eval_8models_20260525/evalset_summary.json` | 10k quotas、0 bad JSON、10k unique fingerprints、8,251 unique images、train image seen 为 0 | eval-set 构造、leakage gate、format/pool n | 不能证明模型因果、真实部署代表性或图片级独立性 |
| `.../dedupe_audit.json` | fingerprint/source-line/prompt-answer-image 重复为 0，但 1,168 repeated image paths、2,917 rows on repeated images | 需要报告 repeated-image clustering 风险 | 不能直接使用 iid CI |
| `muxi/report/opd5000_newexperts_20260601/remote_model_summaries/opd5000_opd_online_run_summary.json` | student rollout→teacher full-vocab KL、5 teacher route、skip 64k、训练摘要与远端 model paths | 训练机制和 run summary | 不能证明 checkpoint binary、optimizer state、raw prediction 的本地可复算性 |

### 诊断性区间（不升级为 benchmark CI）

在“按 metric 的 row 作为 observation unit”这一明确假设下，可以复算以下 Wilson smoke；这些数字不能合并成一个机器人成功率：

| 指标 | k | n | 点估计 | 95% naive Wilson | 依赖/限制 |
| --- | ---: | ---: | ---: | ---: | --- |
| box Acc@0.5 | 3,195 | 6,100 | 0.523770 | [0.511226, 0.536285] | repeated image paths；box row 不是 episode |
| point Hit@100 | 1,222 | 1,400 | 0.872857 | [0.854381, 0.889293] | point metric-specific；多点匹配与图片重复需单独处理 |
| text exact | 2,181 | 2,500 | 0.872400 | [0.858748, 0.884910] | VQA/text row；不等同 grounding/rollout success |

OPD 的 `format_pass=1.0` 也只是输出格式通过率，不能被解释成任务成功率。若要进行正式比较，需要冻结同一 checkpoint、prompt/scorer、raw prediction、按 pool 的统计单元与 cluster-aware uncertainty。

## Claim-to-evidence 与面试守线

| Claim | 当前等级 | 安全说法 | 禁止升级为 |
| --- | --- | --- | --- |
| UWM `186/250` | `user-confirmed-remote-final / protocol-limited` | “固定项目协议下的用户确认汇总；naive CI 约 [0.686, 0.794]，raw episode 尚缺。” | “本地复算的 cluster-aware benchmark CI” |
| OpenPiVLA `97.4%` | `archive-summary-only / run-lineage-open` | “归档报告汇总为 97.4%，当前 formal lineage 和 denominator 未闭合。” | “我的 formal Qwen checkpoint 达到 97.4%”或“超过 official 96.85” |
| OPD ckpt5000 box/point/text | `local-direct metrics / protocol-bounded` | “10k static raw-holdout 中按格式分别报告 n 和指标；按指标做 naive smoke。” | “10k robot rollouts 成功率”或“OPD 单独带来 uplift” |
| 个人 ownership | `ownership-partial` | 只说自己能证明的迁移、协议、诊断、评估工作 | “所有上游结构和远端训练由我独立完成” |

面试回答应先说 observation unit，再说分子/分母，再说 protocol 和 evidence tier。若对方追问“为什么不直接比较三个百分比”，回答是：UWM 是 task/episode 汇总、OpenPiVLA 缺分母与 lineage、OPD 是静态 row-level 多指标；它们的 estimand 不同，不能排序。

## 下一步 Artifact Queue

### P0：关闭当前 EVAL-003 gate

1. UWM：导出 250 条 episode record、exact init/seed/task manifest、checkpoint/normalizer/scorer hash 与失败视频索引。
2. OpenPiVLA：建立 archive→base→formal train→checkpoint→eval 的 immutable lineage，补 denominator、suite/trial/seed/init、raw episodes 和 scorer。
3. OPD：保留 raw prediction 与 eval input 的本地快照，冻结 original/protocol-fixed/lenient point scorer，并确认 repeated-image cluster 处理。
4. 三个项目分别补逐文件 ownership ledger；Git author 只作为线索，不作为独立贡献证明。

### P1：统计与训练准备

- 只有 P0 闭合后，才进入 EVAL-004 paired significance 或 EVAL-005 aggregation。
- 口述训练前保持 `VLA-EVAL-003` 为 `unseen`；真实回答出现后再更新 coaching state。

## 参考资料

1. [EVAL-003 知识页](../knowledge/vol_05_engineering_eval_eval003.html)：episode-level Bernoulli、Wilson/exact、cluster 与 stopping rule。
2. [EVAL-003 Source Freeze](vol_05_eval003_success_rate_confidence_interval_source_freeze.html)：SciPy/statsmodels 版本、方法边界和原有证据清单。
3. [UWM Claim–Evidence Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)：UWM protocol、186/250 与 raw artifact 缺口。
4. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：97.4 archive、formal run 与 lineage 缺口。
5. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：10k raw-holdout、metric-specific n 与 ownership 边界。
6. [UWM 项目页](../../05_uwm_libero_eval_protocol.html)、[OpenPiVLA 项目页](../../03_openpivla_action_modeling.html)、[OPD 项目页](../../02_opd_vlm_grounding.html)。
