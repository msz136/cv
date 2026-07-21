# VOL 05 EVAL-009：Raw Predictions、Episode Trace、Video 与可复算 Summary

> 状态：`drafted / VLA-EVAL-009 / knowledge_31_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-005 Aggregation](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)、[EVAL-006 Versioning](vol_05_engineering_eval_eval006_versioned_evaluation_manifest.html)、[EVAL-008 Failure Taxonomy](vol_05_engineering_eval_eval008_failure_taxonomy_recovery.html)  
> 来源冻结：[EVAL-009 Source Freeze](../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)  
> 项目边界：五项目均未闭合checkpoint/protocol、complete raw rows、scorer/reducer与independent recompute，本页不升级metric claim。

## 问题（Question）

怎样设计VLA evaluation artifact，使第三方能从raw predictions/episode trace重算summary，并用video定位失败？关键是把raw作为source of truth，summary作为deterministic derived artifact，video作为timestamp-aligned diagnostic sidecar。

## 1. 四种“有证据”不是同一强度

| 现有物 | 证据等级 | 仍缺什么 |
| --- | --- | --- |
| 报告数字 | claim/summary | raw、scorer、lineage |
| raw rows | rescorable | protocol/checkpoint同源 |
| trace + video | diagnosable | denominator与complete suite |
| immutable bundle + recompute | reproducible metric | ownership/部署泛化 |

“我有视频”不能回答分母，“我有summary JSON”不能回答逐样本排除，“我有JSONL”也不能证明它属于声称的checkpoint。

## 2. Bundle Layout

```text
eval_bundle/
  bundle_manifest.json
  protocol/protocol.json
  schema/raw_record.schema.json
  raw/predictions.parquet
  raw/episodes/episode_index.jsonl
  media/video_index.jsonl + *.mp4
  code/reducer_revision.json
  summary/metrics.json + exclusions.jsonl
  checksums/manifest-sha256.txt
  README.md  # verify + recompute commands
```

RFC 8493 BagIt提供complete/valid payload和checksum manifest；W3C PROV-DM提供entity/activity/agent/derivation。项目不必真的采用BagIt目录名，但必须覆盖完整性、内容hash和lineage语义。[1][2]

## 3. Raw Prediction Schema

### 3.1 Static task

保存`record_id`、input/target ref与hash、checkpoint/processor、raw output、parsed output、parser/scorer revision、valid/invalid reason、metric contribution、weight与slice标签。

OPD类point/box/text评估若只保存最终IoU/Hit/Exact表，就无法重跑新parser或区分format failure与geometry failure。

### 3.2 Rollout step

保存episode/step、env/wall timestamp、obs refs/checksums、raw action chunk、decoded action、controller command、executed state、reward/predicate、terminated/truncated/error，以及policy/server/client/protocol revision。

```text
model raw output != decoded action != controller command != executed state
```

只留最后一个字段会丢掉EVAL-008所需first-divergence证据。

## 4. Episode Index与守恒

\[
N_{planned}=N_{valid}+N_{excluded}+N_{missing}.
\]

变量解释：每个planned episode必须有唯一ID；excluded有冻结reason，missing明确列出。attempted、completed、valid、success分别计数，不能把crash/timeout/缺文件从分母静默删除。

sharded eval记录shard/rank/attempt/completion marker与duplicate resolution。retry产生的新attempt不得被当成新的init或同时进入summary。

## 5. Video Sidecar

视频字段：episode、camera/view、SHA、codec/container、time base/fps、frame count、start/end、frame/timestamp→step mapping、drop frames、overlay来源、raw/derived。

视频用于：人工核验reset、动作、接触、failure mode；不用于：从文件名手算success、替代machine-readable predicate、只保存精选case后推总体。

MCAP可把schema/channel/message timestamp、attachment、metadata、CRC/index装进同一机器人日志；JSONL/Parquet/MP4也可以，只要time/identity/integrity合同等价。[3]

## 6. Summary必须可由Reducer得到

\[
S_{recomputed}=A\big(\{g(r_i;P,S):valid_i=1\},W,E\big),
\qquad |S_{reported}-S_{recomputed}|\le\epsilon.
\]

变量解释：`g`是per-record scorer，`P/S`是protocol与parser/scorer revision，`A`是aggregation，`W`是weights，`E`是exclusion。整数分子/分母exact match；浮点记录dtype、reduction order与tolerance。

reducer输出overall、per-task/slice、numerator/denominator、invalid/excluded/missing。scorer升级时保留同raw rows上的old/new summary，不覆盖历史。

## 7. 六道Gate

1. **complete**：manifest payload齐全，planned守恒；
2. **checksum-valid**：每个payload/tag hash通过；
3. **schema-valid**：ID/type/shape/finite/time monotonic；
4. **lineage-valid**：checkpoint→protocol→raw→scoring activity→summary；
5. **recomputable**：clean command生成同summary；
6. **reviewable**：episode/step能跳到trace/video。

hash只能证明bytes没变，不能证明parser、axis、predicate或分母语义正确。

## 8. Bundle Verifier

```python
def verify_bundle(bundle):
    # 1. Verify manifest completeness and cryptographic payload integrity.
    manifest = load_and_verify_manifest(bundle)

    # 2. Validate raw rows and account for every planned sample/episode.
    rows = load_raw_records(bundle)
    validate_schema_lineage_and_conservation(rows, manifest)

    # 3. Recompute with frozen scorer, exclusions, weights and aggregation.
    result = reduce_rows(rows, manifest.protocol, manifest.scorer,
                         manifest.exclusions, manifest.weights)
    assert_matches_reported(result, bundle / "summary/metrics.json")

    # 4. Cross-link media for diagnosis; never use curated videos as numerator.
    verify_video_step_map(bundle / "media/video_index.jsonl", rows)
    return result
```

这是设计合同，不代表项目已有统一verifier。

## 9. 五项目映射

### WAM

manifest、双侧300-step JSONL、双视频与hash已构成L3 partial；只有CoffeePressButton episode0，checkpoint远端、trained video跨root、target/scorer缺失，不能重算模型comparison或task success。

### OpenPiVLA

97.4是L1 archive summary；缺checkpoint hash、per-suite raw summary、episodes与reducer。official-checkpoint diagnostics属于另一lineage，不能替代formal/archive bundle。

### OPD

有10k input manifest、dedupe与by-format/by-pool tables，但完整raw predictions与远端weights缺失。需要逐样本raw text、parsed point/box/text、invalid reason和metric contribution重跑三套point protocol。

### Robot Harness

32B metrics/ladder与manifests存在，但base/SFT/GRPO的n/scorer不完全一致；共同suite raw predictions缺失，browser也无runner episode/video。

### UWM

186/250与per-task user-confirmed summary存在，但缺250 episode rows、checkpoint/normalizer hash、exact init、trace/video与recompute command；安全口径仍是summary-supported。

## 10. 高频追问

1. summary JSON为何不等于可复算？
2. raw output与parsed prediction为何都要存？
3. video为什么不能当分子分母？
4. crash/timeout/missing怎样进入分母？
5. retry/attempt怎样去重？
6. hash验证能证明哪些、不能证明哪些？
7. scorer升级后怎样重算？
8. MCAP是否强制？
9. independent recompute的验收条件是什么？
10. 五项目各在证据梯度哪一层？

## 11. Review Checklist与下一入口

- [ ] raw rows包含原始输出、parsed输出与metric contribution；
- [ ] planned/valid/excluded/missing守恒；
- [ ] step trace保留obs→action→command→state；
- [ ] video有timestamp/step mapping且只作sidecar；
- [ ] checkpoint/protocol/scorer/reducer与raw/summarylineage闭合；
- [ ] payload checksum与schema验证通过；
- [ ] clean command重算分子、分母、slice与overall；
- [ ] 项目只有summary时保持WARN。

本节点保持`WARN/unseen`。下一节点固定为`VLA-EVAL-010`：regression gate、golden set与canary rollout；真实口述前不创建coaching state。

## References

1. [EVAL-009 Source Freeze](../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。
2. RFC 8493、W3C PROV-DM与MCAP frozen source见source freeze。
3. [WAM Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
5. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
7. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
8. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。
