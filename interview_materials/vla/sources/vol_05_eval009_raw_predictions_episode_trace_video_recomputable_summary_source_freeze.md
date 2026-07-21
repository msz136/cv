# VOL 05 EVAL-009 Source Freeze：Raw Predictions、Episode Trace、Video 与可复算 Summary

> 状态：`source_frozen / VLA-EVAL-009 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结raw row/step、episode trace、media sidecar、derived summary、checksum/provenance、reducer与独立复算合同；下游只生成一张`VLA-EVAL-009`原子题卡，VOL 05同步为knowledge/cards 31/44。

## 问题（Question）

“报告里有97.4”“有失败视频”“有JSONL trace”分别能证明什么？高分回答要把human-readable evidence与machine-recomputable evidence分开，确保summary能从固定raw records、scorer、exclusion与aggregation重新得到。

## 1. 冻结来源、revision与边界

| ID | 来源 | 类型 / revision | SHA-256 | 支持范围 |
| --- | --- | --- | --- | --- |
| S1 | RFC 8493, BagIt v1.0 | IETF standard / October 2018 | `4964147d2e6e16442d4a6dbfbe68178a8f33c3e791c06d68a8b33f51ad821537` | payload/tag manifest、checksum、complete与valid package；不定义VLA schema/metric |
| S2 | W3C PROV-DM | W3C Recommendation / 2013-04-30 | `5c925c21bc96c285b25017c3b90d82cf74251d07713b71fcb81ca60f873c9e88` | entity/activity/agent、generation/usage/derivation/attribution与bundle；不证明本地ownership |
| S3 | Foxglove MCAP | official-code / commit `413b6b2aa49665ba4af25c718261f47ec61e9814`, MIT | README `d666ab2171490ce69d7b8aa2f6c850fcdf1a310a8d88424e07cfb81e5f5dfcab`; spec `64d1ae52d16d5ef32a6d857cd34cc866d5583db09a715afdafd7fcbf98e13caa`; Kaitai `7ae83a344d515c29ee4fb433f6dd6273296beceb3e4d41bce359012cd1e63be8`; LICENSE `da11235665c17d4c1634072dae92b8ba1b38d6fdde2ccf19a6bbede33253f58d` | schema/channel/message、log/publish time、attachment/metadata、CRC/index/summary；不要求项目使用MCAP |
| S4 | EVAL-005/006/008与ENG-012 | canonical local source freezes | `16b6a4c7...804ff46`; `8a2ccfbc...320c20`; `580ac709...f37b0`; `f13c9524...d11f2f` | aggregation、protocol identity、failure trace与storage-format前置合同 |
| S5 | 五项目inventories + WAM manifest | local evidence | full hashes见review | 当前summary/raw/trace/video/checkpoint缺口；不升级项目metric |

完整本地SHA：EVAL-005 `16b6a4c7c8e284ca8bd8a7cc831c3fc553405668ea87a071c23147f8f804ff46`；EVAL-006 `8a2ccfbc382537d13e95feefe4ec146342d7478432a9a645344a64b302ccd054`；EVAL-008 `580ac70922472453c8806265b2fd4bae8dad7881bad3da2e8f211c870e1f37b0`；ENG-012 `f13c9524a9ebc182985772069bb4696058639527699bd9d627cbf2b863d11f2f`；WAM manifest `1ab8709201e2e75f580cb0aa0f8465defb546d63b2aab70a1752239a7da8f697`；五inventory为`66acc52c...aa291e`、`078c86b1...772d`、`728b8326...3674d`、`a3c644f9...ce293`、`0a68251d...12bb`。

## 2. Evidence Ladder

| 层 | artifact | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| L0 claim | 简历/口述数字 | 存在一个claim | 数字来源与正确性 |
| L1 summary | table/JSON aggregate | 报告记录了分子分母/指标 | raw records、排除、scorer可重算 |
| L2 raw rows | per-sample prediction或episode outcome | 可重跑parser/scorer/reducer | checkpoint/protocol同源 |
| L3 aligned trace/media | step events、video、timestamp map | 可诊断时序与失败 | aggregate完整、因果root cause |
| L4 immutable bundle | manifest、hash、schema、code、raw、summary | 完整性与lineage可验证 | 他人已成功复算 |
| L5 independent recompute | clean-environment command + matching output | 指标可复算 | 项目ownership或部署泛化 |

## 3. Canonical Bundle

```text
eval_bundle/
  bundle_manifest.json
  protocol/protocol.json          # benchmark/env/controller/scorer/policy IDs
  schema/raw_record.schema.json
  raw/predictions.parquet         # or per-episode JSONL/MCAP
  raw/episodes/episode_index.jsonl
  media/video_index.jsonl
  media/*.mp4                     # qualitative sidecars
  code/reducer_revision.json
  summary/metrics.json
  summary/exclusions.jsonl
  checksums/manifest-sha256.txt
  README.md                       # exact verify/recompute commands
```

BagIt支持payload completeness与checksum validity；PROV-DM支持把raw entity、scoring activity、summary entity与responsible agent关联。格式可替换，但这些语义不能缺。

## 4. Raw Record：保存模型输出，不只保存分数

### 4.1 Static prediction

```text
record_id, dataset/sample/revision, input_ref/hash, target_ref/hash,
checkpoint_sha, processor/normalizer_sha, raw_output, parsed_output,
parser/scorer_sha, valid, invalid_reason, metric_contribution,
weight, split/pool/task labels
```

OPD类任务需同时保存原始文本/token输出与parsed box/point/text；否则无法区分模型能力、format、parser和scorer。

### 4.2 Rollout step

```text
episode_id, step_id, env_time, wall_time, obs_refs/checksums,
raw_action_chunk, decoded_action, controller_command, executed_state,
reward, success_predicate, terminated, truncated, error/event,
policy/server/client/protocol revisions
```

raw model output、decoded action、command与executed state是四个证据层，不能只留最终env action。

## 5. Episode Index与Conservation

每个planned episode必须落入valid、excluded或missing：

\[
N_{planned}=N_{valid}+N_{excluded}+N_{missing}.
\]

变量解释：excluded需reason/code/version，missing是应有而未产出的记录。attempted、completed、valid、success分别统计；静默丢失失败episode会抬高success。

episode index至少绑定task/init/seed、checkpoint、protocol SHA、trace/media路径与hash、outcome、exclusion、first error。sharded eval还需shard/rank/attempt、completion marker和duplicate resolution。

## 6. Video是Sidecar，不是Metric Numerator

视频用于人审与failure localization，但可能被裁剪、变速、掉帧、overlay或只保存best/worst cases。最小video index：

```text
episode_id, camera/view, file_sha256, codec/container,
time_base/fps, frame_count, start/end time,
frame_or_timestamp_to_step mapping, dropped_frames,
overlay_source, raw_or_derived
```

summary不能从“数视频文件名里的success=True”生成；primary outcome来自machine-readable predicate/episode rows。视频与trace不同步时标`diagnostic-only`。

MCAP提供带schema/channel、log/publish timestamp、attachment、metadata、CRC与index/summary的通用机器人日志容器；JSONL+Parquet+MP4也可达到同语义，不强制MCAP。

## 7. Deterministic Reducer

设raw valid rows为`r_i`、固定scorer为`g`、聚合器为`A`：

\[
S_{recomputed}=A\big(\{g(r_i;P,S):valid_i=1\},W,E\big),
\qquad
|S_{reported}-S_{recomputed}|\le\epsilon.
\]

变量解释：`P`是protocol、`S`是scorer/parser revision、`W`是target weights、`E`是exclusion rules。integer count要求exact match；floating metric记录dtype、reduction order与tolerance。reducer必须输出分子/分母、per-task/slice与invalid/excluded counts。

summary文件是derived cache，不是source of truth。改scorer时在同一raw rows上生成新summary并保留旧revision，不能覆盖历史。

## 8. Integrity与Provenance Gate

1. `complete`：manifest列出的payload全在，planned/valid/excluded/missing守恒；
2. `valid`：payload与tag checksums验证通过；
3. `schema-valid`：required fields、types、IDs、finite/shape/time monotonic通过；
4. `lineage-valid`：checkpoint/protocol/scorer/raw/summary形成PROV derivation；
5. `recomputable`：clean command从raw生成同summary；
6. `reviewable`：trace/video可由episode_id和timestamp交叉定位。

只有summary SHA不能证明raw完整；只有payload SHA也不能证明语义正确。

## 9. 五项目边界

- **WAM**：一组CoffeePressButton episode0已有base/trained manifest、300-step JSONL、双视频与hash，达到L3 partial；checkpoint是远端引用、trained video跨output root、无target/scorer/multi-episode，因此不是完整可复算comparison。
- **OpenPiVLA**：97.4是committed report summary，缺checkpoint hash、raw per-suite summary与episodes，属L1；official-checkpoint diagnostic rollouts是另一lineage，不能补齐97.4。
- **OPD**：10k raw-holdout input manifest、by-format/by-pool tables与run summaries存在，但完整model raw predictions/weights/recompute bundle缺失；表格不能替代逐样本raw output+parser result。
- **Robot Harness**：metrics/report与部分manifest存在，但32B base/SFT/GRPO的n/scorer不同，缺共同suite raw predictions；browser是format-only，无真实runner episode/video。
- **UWM**：186/250 user-confirmed JSON与per-task summary存在，缺250 episode rows、checkpoint/normalizer hash、exact init与失败视频；属summary层，不是本地independent recompute。

## 10. Bundle Verifier伪代码

```python
def verify_and_recompute(bundle):
    # Verify payload completeness and cryptographic integrity first.
    manifest = load_manifest(bundle)
    verify_all_paths_and_hashes(manifest)

    # Validate raw schemas and account for every planned record.
    rows = load_raw_rows(bundle)
    validate_ids_shapes_times_and_lineage(rows, manifest)
    assert_conservation(manifest, rows)

    # Recompute from raw rows with frozen parser/scorer/exclusion/weights.
    result = reduce_rows(rows, protocol=manifest.protocol,
                         scorer=manifest.scorer,
                         weights=manifest.weights,
                         exclusions=manifest.exclusions)
    compare_with_reported(result, bundle / "summary/metrics.json")

    # Media is cross-linked for diagnosis, not used as the primary numerator.
    verify_media_step_alignment(bundle / "media/video_index.jsonl", rows)
    return result
```

这是artifact contract，不是五项目已实现bundle verifier。

## 11. Source Gate结论与下一入口

EVAL-009保持`WARN`：raw/trace/video/summary证据梯度、bundle layout、conservation、checksum/provenance与deterministic recompute已冻结；五项目均未同时闭合immutable checkpoint/protocol、complete raw rows、scorer/reducer与独立复算。

下一节点固定为`VLA-EVAL-010`：regression gate、golden set与canary rollout。真实口述前不创建`coaching_state.md`。

## References

1. [RFC 8493 BagIt](https://www.rfc-editor.org/rfc/rfc8493)。
2. [W3C PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/)。
3. [MCAP frozen specification](https://github.com/foxglove/mcap/blob/413b6b2aa49665ba4af25c718261f47ec61e9814/website/docs/spec/index.md)。
4. [EVAL-005](vol_05_eval005_aggregation_estimand_source_freeze.html)、[EVAL-006](vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)、[EVAL-008](vol_05_eval008_perception_action_controller_recovery_failure_taxonomy_source_freeze.html)、[ENG-012](vol_05_eng012_storage_formats_source_freeze.html)。
5. [Evidence Manifest](../evidence/evidence_manifest.html)与五项目inventories。
