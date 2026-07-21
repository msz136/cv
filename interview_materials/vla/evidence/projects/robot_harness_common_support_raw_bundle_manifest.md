# Robot Harness 四模型共同支持集 Raw Bundle Manifest

> 状态：`local-raw-partial-recovered / 28-of-40 primary files / common-support-6-of-10 / recovery-search-complete / 0-eligible-replacements / checkpoint-unverified / WARN`  
> 审查日期：2026-07-20  
> 证据截止：2026-07-20  
> 原始文件位置：`C:\Users\mousongzhe\agent\.codex_tmp\remote_sync_20260626_141618\extract\training_pipeline_v2_language_full`；本页只读审计，没有修改 `agent` 或 raw outputs。  
> 边界：本页恢复的是 32B base、SFT、GRPO checkpoint-100/200 的部分 per-sample prediction identity 与共同 ID support；不把 proxy suite 升级为真实机器人成功，不把当前 scorer source 冒充当时 scorer binary，不把远端 checkpoint path 冒充权重 SHA。

## 1. 问题（Question）

上一份十套件 aggregate gate 在 12 个普通同步 run 目录中没有找到 raw predictions，因此无法判断 base、SFT、GRPO100、GRPO200 是否回答了同一组 case。全盘搜索随后在隐藏的 2026-06-26 remote-sync extraction 中发现 132 个 `*.predictions.jsonl`。本轮回答三个更窄的问题：

1. 目标十套件 × 四模型的 40 个 primary prediction 文件实际找回多少？
2. 找回文件能否逐行解析，是否有重复/空 ID、空 output 或 schema 漂移？
3. 哪些 suite 已达到四模型 exact ID-set + exact order 的共同支持集门，哪些仍需要恢复？

结论：**28/40 个 primary 文件可直接读取并通过结构校验；6/10 个 suite 的四模型 ID 集合与顺序完全相同。其余 12 个 primary 文件在该 extraction 中确实缺失，因此只能建立 partial common-support bundle，verdict 保持 `WARN`。**

## 2. 结论先行

1. Windows 传统路径探针把若干超过 260 字符的路径误报为 missing；使用 `\\?\` extended-length prefix 后，找回并流式校验 28 个 primary JSONL。
2. 28 个文件合计 `17,117,873` bytes、`17,828` rows；`bad_json=0`、`missing_id=0`、`duplicate_ids=0`、`empty_output=0`。
3. 所有 28 个文件共享同一 top-level schema 与同一 11-field embedded-metrics schema；这证明字段合同一致，不证明 scorer revision 或 semantic backend 一致。
4. `project_robot_sandbox_eval`、`safety_side_effect_eval`、`browser_deferred_eval`、`appworld_ood_api_policy_probe`、`quarantine_safety_probe`、`robovlm_point_general_probe` 六个 suite 的四模型 ID set 与 order 均完全一致，共覆盖每模型 `3,457` 个 case。
5. `sft_tool_call_holdout` 与 `cross_source_generalization_eval` 只找回 GRPO100/200 各 1000 行；base/SFT raw 缺失。两个 ToolACE suite 的四模型 primary raw 全部缺失。
6. 另发现 9 个 `.schema_aware.predictions.jsonl` 和 4 个 `.ood_scored.predictions.jsonl`；它们不是 40 个 primary 文件的替代品，也没有补齐四个缺口 suite。
7. 本轮只冻结文件 identity 与 support；没有以当前代码重新评分，也没有生成 base→SFT→GRPO uplift、置信区间或 checkpoint 因果结论。
8. 对 `agent`、`Project` 与原始 `remote_small.tar.gz` 做定向 recovery search：发现 17 个同名候选，但全部属于 GRPO 其他 attempt/singleload、8B 两行 smoke 或已存在的目标文件；**0 个可以填入 12 个缺失 slot**。

## 3. 对上一份 aggregate gate 的勘误

原 gate 的“12 个 archived run 目录中没有 full prediction 文件”只对普通同步目录成立。历史同步 manifest 明确排除了 `predictions.jsonl`；隐藏的 `.codex_tmp/remote_sync_20260626_141618/extract/` 保留了其中一部分。因此正确表述是：

> 普通同步目录没有 raw predictions；隐藏 remote-sync extraction 中恢复出目标 40 文件中的 28 个。六个 suite 已形成四模型 exact common support，四个 suite 仍缺 12 个 primary 文件。

这项勘误不会把旧 aggregate 的五种 metric、不同 `n`、semantic backend、122B/35B input、checkpoint binary 或 ownership 缺口自动关闭。

## 4. 冻结的工具与生成合同

| artifact | SHA-256 | 本轮用途 | 边界 |
| --- | --- | --- | --- |
| `tools/audit_robot_harness_raw_bundle.py` | `A2F3E54493097602918C4333D1C8AC03C0D6E88F9034D61AC0E9B0B186C81FC4` | 长路径读取、JSONL 校验、common-support、12-slot locator 与候选拒绝审计 | 本轮审计工具，不是原训练/eval 实现 |
| `robot_harness_common_support_raw_bundle_manifest.json` | `9FABE3E449D85DF10F998DE7C88BF1EAE110E52386D7E5AA29403EDBF2B1AB2F` | 40 个 expected slots、28 个 file records、12 个 recovery slots、17 个 candidate records | 轻量 manifest；不包含 raw output 文本 |
| `native_tools_eval.py` | `F01EF13A029567297B35646AB5B2A17F7E8762D77FFE739370365848638FCEC4` | `<suite>.predictions.jsonl` 生成合同 | 当前本地 source identity，不证明每个历史 run 使用同一字节 |
| `schema_aware_rescore.py` | `7918D6644BF49031E907D973C34A1B3CC0E88AB89EC09F3A29AFA4927E5695A7` | 读取 primary 并生成 `.schema_aware.predictions.jsonl` | derived 文件不能替代缺失 primary |
| `score_ood_probe.py` | `6BBA56DBDE4947DE62B9A8FF38A8F215C828D556E193AA88E1E3F5AF4ABB76C2` | 读取 primary 并生成 `.ood_scored.predictions.jsonl` | 本轮未重新 OOD scoring |
| `openai_vllm_eval.py` | `F7B7920349C1574E75F60DC6192A7EA3AD607AD7CACCC921C61D22E4C84E959D` | reuse 前验证 expected ID exact order | 新 122B/35B workflow 只作 contract 旁证 |
| `eval_32b_service_client.py` | `25DB3FC22EBBA517DD988E4ED789DCB40173F77DD36C38AC5C5A598172ABFA14` | 另一条 `<suite>.predictions.jsonl` writer | 不证明本轮 28 文件由该 writer 生成 |

ordered-ID fingerprint 对文件顺序敏感：

\[
H_{\mathrm{id}}=\operatorname{SHA256}\!\left(\big\Vert_{i=1}^{n}\operatorname{u64be}(|b_i|)\Vert b_i\right),
\qquad b_i=\operatorname{UTF8}(\mathrm{id}_i).
\]

变量解释：`u64be` 是 8-byte big-endian 长度前缀，避免简单字符串拼接歧义；随后按 JSONL 原顺序串联。实现映射是本轮 audit tool 的 `ordered_id_digest`。它证明相同 ordered ID stream，不证明输入 prompt、tool schema、generation config、scorer 或 checkpoint 相同。

## 5. 40-slot Primary 文件覆盖

| suite | base32 | sft32 | grpo100 | grpo200 | 四模型 common support |
| --- | ---: | ---: | ---: | ---: | --- |
| `sft_tool_call_holdout` | missing | missing | 1000 | 1000 | 否；只可比较两条 GRPO |
| `project_robot_sandbox_eval` | 130 | 130 | 130 | 130 | 是；set/order exact |
| `safety_side_effect_eval` | 289 | 289 | 289 | 289 | 是；set/order exact |
| `browser_deferred_eval` | 930 | 930 | 930 | 930 | 是；set/order exact |
| `cross_source_generalization_eval` | missing | missing | 1000 | 1000 | 否；只可比较两条 GRPO |
| `appworld_ood_api_policy_probe` | 732 | 732 | 732 | 732 | 是；set/order exact |
| `toolace_schema_given_probe` | missing | missing | missing | missing | 否 |
| `toolace_schema_absent_probe` | missing | missing | missing | missing | 否 |
| `quarantine_safety_probe` | 976 | 976 | 976 | 976 | 是；set/order exact |
| `robovlm_point_general_probe` | 400 | 400 | 400 | 400 | 是；set/order exact |

## 6. 六个四模型共同支持集

| split | suite | 每模型 rows | set equal | order equal | ordered common-ID SHA-256 |
| --- | --- | ---: | --- | --- | --- |
| D | `project_robot_sandbox_eval` | 130 | true | true | `03329BE9FADB6A33C268EC18C4B22E8B41A6D5CC3499D9AF570AA6D93E9AB49D` |
| D | `safety_side_effect_eval` | 289 | true | true | `C9B9ACB006EF0BB5ECE55FAD83AE9E69F0FC9DE65B0A7A14D38DE816100AACBC` |
| D | `browser_deferred_eval` | 930 | true | true | `CABD9FA27ACB4115C58CC373CA83CA800AADE588BBF9046B5CEF82104E26E66C` |
| OOD | `appworld_ood_api_policy_probe` | 732 | true | true | `5083FDEBB7DA7FFCA4B0466024A1AC25CD4B9853B310210074BBC6F839EA76C1` |
| OOD | `quarantine_safety_probe` | 976 | true | true | `D45AE832A8CDF1180001FF4299E9419EA312FF9EA4F5619653AA65073055DF87` |
| OOD | `robovlm_point_general_probe` | 400 | true | true | `F744D0D352036D4C3A9DA20007DAEF8BED406A760C7047DF831099A8A7DBEC61` |

若未来冻结同一 scorer (g_j)，这六个 suite 已具备逐 case paired 计算的 ID 前提：

\[
\Delta_{a,b}^{(j)}=\frac{1}{|C_j|}\sum_{i\in C_j}\left[g_j(y_{a,i})-g_j(y_{b,i})\right].
\]

变量解释：(C_j) 是上表冻结的共同 ID support，(y_{a,i}) 是 raw output。本轮只证明 (C_j) 的 set/order identity；`g_j` 的 code/config/backend identity 与 checkpoint binary 仍未冻结，所以本页不报告这条差值。

## 7. 28 个 Primary 文件身份

### 7.1 D suites

| suite | model | rows | bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `sft_tool_call_holdout` | grpo100 | 1000 | 990586 | `EF56A8F8670899561331CF3969AF91B7E2DC1C1581A1470E43DC93A1FA81A174` |
| `sft_tool_call_holdout` | grpo200 | 1000 | 992363 | `4BA80F83572A96709F51D492168ED159D049FF2AEAC24ED0FA7D9693710AFB56` |
| `project_robot_sandbox_eval` | base32 | 130 | 122749 | `E10A82A28BE175B888A827A87CBB85B82BE20FCDB985B2E6537DBE0C639507C8` |
| `project_robot_sandbox_eval` | sft32 | 130 | 125909 | `6B09FAF5C85756318D1AF3632EF17203B7FE63E4B7BBD5A24EA2CD060385A18E` |
| `project_robot_sandbox_eval` | grpo100 | 130 | 126213 | `1DC753581D9081724448BA16FADE68DCC9A2294EC45AE8E5FECB29E9DBDCB310` |
| `project_robot_sandbox_eval` | grpo200 | 130 | 126367 | `31886143CDE02CA3B58E1AF7AECE77ADD11A2CA26DF46A8FCC28403461853A71` |
| `safety_side_effect_eval` | base32 | 289 | 338848 | `B427489969141A4A6EFAF493A13501C4F9DEA9F7A6AD1019B619F1C111292A49` |
| `safety_side_effect_eval` | sft32 | 289 | 334405 | `59224D84E2361E8027B4307EEE39E35A8F740E730A045EA61C34918ECDB54038` |
| `safety_side_effect_eval` | grpo100 | 289 | 336629 | `103C4281DEC2016BEA71E9712EBB43D3825400EAD291370ED2F697673483935B` |
| `safety_side_effect_eval` | grpo200 | 289 | 337777 | `5D8A15789CB05304F510C2A5672B5256EC9EFABEAD22DC129E0FA7471DE5E147` |
| `browser_deferred_eval` | base32 | 930 | 808466 | `C8F2F480F07BA787801C04439EA13A3F90CE9628E9235DFC019E0EE16DEB6FCF` |
| `browser_deferred_eval` | sft32 | 930 | 843644 | `11C8899540534E0E692D0E3FBD9BCD721436E2AD659D96FFB806CAEF51D8A3F0` |
| `browser_deferred_eval` | grpo100 | 930 | 843924 | `9C7C0EC7992FA83A10548C3ECFD005222C550A2618DC074C566553A071C9FDB2` |
| `browser_deferred_eval` | grpo200 | 930 | 840685 | `1D4BE1A286F6E825B6193ED33D287274DE5B03EF972242150662F4A1C04605EA` |
| `cross_source_generalization_eval` | grpo100 | 1000 | 979978 | `FD3D8C1CD6E85E71AC3A0EB79D2F7FED4BCCBE192894E785F1CF05ABA7E33A4F` |
| `cross_source_generalization_eval` | grpo200 | 1000 | 979460 | `BB476D0B53AD58ED7E31CC1D7D804D3D3E3F32BCA12BB2F85CD307126F5685BC` |

### 7.2 OOD suites

| suite | model | rows | bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `appworld_ood_api_policy_probe` | base32 | 732 | 832866 | `FAC5FDE4026489480460ED549C6EF69E9E746DAB44F8310EFC0953067D3EB64C` |
| `appworld_ood_api_policy_probe` | sft32 | 732 | 767117 | `530FC6552A076CEBB802A32A6A45D236778B7C61A35C3BEB427F837D2FB995CC` |
| `appworld_ood_api_policy_probe` | grpo100 | 732 | 814884 | `A79E00AF2DFD71A971494F837F26B31CD8C24F06F6176A79D53A54FD4BFAC4F4` |
| `appworld_ood_api_policy_probe` | grpo200 | 732 | 829542 | `DC426DEF5CD31A13C6DF2B6061790AB2133CDD50BE23C9EB205038ABB93504A6` |
| `quarantine_safety_probe` | base32 | 976 | 998642 | `2EAFDF1098BC78CE84BD536F3B0E33822C636BF31484E404C9FC66B11CC45089` |
| `quarantine_safety_probe` | sft32 | 976 | 894153 | `A7D5E4FA2FF2DAF02DBD1B1EA156749092228363CFEE28A3251D06E425D4F3F2` |
| `quarantine_safety_probe` | grpo100 | 976 | 942873 | `599ACEEE1F4B0B64DFB59DAC72F9B5BAB9AB26B1713F0BA6BA70AA380DB93EA9` |
| `quarantine_safety_probe` | grpo200 | 976 | 949895 | `8A88FB4FE8282518AB1C950B5134222C50820696007F5E824F20CFBD6D39A025` |
| `robovlm_point_general_probe` | base32 | 400 | 253918 | `1A66123A191EB28CC77B2BAF5C3081AE0A77AFECEF72EEFDEC023162F373194C` |
| `robovlm_point_general_probe` | sft32 | 400 | 235328 | `214254664FC32EA9AE56F67D232576D3CDDECCF27B5A6F42A78EC057A2AE15E2` |
| `robovlm_point_general_probe` | grpo100 | 400 | 235328 | `06AF42AF35552098E25761FD71F5DCF50F113782F20B83E263B65E2F20AD0043` |
| `robovlm_point_general_probe` | grpo200 | 400 | 235324 | `7BEB8770050D1BB33608F75238057268B5C363CEA771CD58F221361965B458FC` |

完整 relative paths、ordered-ID SHA、derived-file flags 与 validation counters 保存在同目录 JSON manifest；本页不复制 raw output 内容。

## 8. Schema 与 Derived 文件边界

28 个 primary 文件的唯一 top-level schema profile 是：

```text
gold_signature, id, metrics, output, pred_signature,
source, task_family, tool_family
```

唯一 embedded metrics profile 有 11 项：`argument_exact_match`、`argument_semantic_match`、`bound_robot_or_scope_respected`、`browser_project_mixing`、`final_answer_contains`、`forbidden_tool`、`hallucinated_tool`、`malformed_tool_call`、`required_tool_coverage`、`tool_name_accuracy`、`valid_json_or_tool_call`。

这只证明 archived rows 的字段集合一致。`metrics` 是随文件保存的历史结果，不能在未冻结 scorer revision/backend 时当成严格统一实现。9 个 schema-aware derived 文件分布在 project/safety 四模型和 base-browser；4 个 OOD-scored derived 文件只覆盖 RoboVLM 四模型。derived 文件没有使十套件 primary coverage 从 28/40 变成 40/40。

## 9. 12 个缺失文件的 Recovery Manifest

| split | suite | 缺失模型 | 需要恢复的文件数 | 验收条件 |
| --- | --- | --- | ---: | --- |
| D | `sft_tool_call_holdout` | base32、sft32 | 2 | primary JSONL；full SHA；1333/实际 rows；unique ID；与 GRPO1000 support 的交集 |
| D | `cross_source_generalization_eval` | base32、sft32 | 2 | primary JSONL；full SHA；1820/2000/实际 rows；unique ID；与 GRPO1000 support 的交集 |
| OOD | `toolace_schema_given_probe` | base32、sft32、grpo100、grpo200 | 4 | 四模型 primary JSONL；full SHA；exact ID-set/order；同 scorer input schema |
| OOD | `toolace_schema_absent_probe` | base32、sft32、grpo100、grpo200 | 4 | 四模型 primary JSONL；full SHA；exact ID-set/order；拒绝规则与 offered-schema 状态冻结 |

恢复时不能只复制 metrics JSON 或 failure samples。必须保留 primary raw output、ID、source suite SHA、prompt/tool schema、generation config、scorer code/config/backend identity 与 exclusion ledger。

### 9.1 12-slot Metrics 与 Run 身份

| split | suite | model | expected rows | metrics SHA-256 | run-manifest SHA-256 |
| --- | --- | --- | ---: | --- | --- |
| D | `sft_tool_call_holdout` | base32 | 1333 | `B8F8AA8C74B6C836459E623BC9ECD07872F7ABB91C8ED205A71BBA6803448D47` | `E5955AF82EC29DED60951CAEF8F7FC5D47930DBA1036D76C934979D09EF68291` |
| D | `sft_tool_call_holdout` | sft32 | 1333 | `747AAFF2D5E77F5FAE470F4A574532C8F0780BC9908C781137B6DF5641290CC0` | `F36A53ED1CAB05E0099CEDCCE30C1AFD35613C47F4E4801AC72C7D6BC4899635` |
| D | `cross_source_generalization_eval` | base32 | 1820 | `3D7E4DEFCCE90358E4663A3179FD55B08DE8049EA181548DA718B9B8D5C7E0D2` | `E5955AF82EC29DED60951CAEF8F7FC5D47930DBA1036D76C934979D09EF68291` |
| D | `cross_source_generalization_eval` | sft32 | 1820 | `3A25EA2E69015DB11A6EA2AB9B4794872CE3B07738B5A9EECE1858B0CD4D21CE` | `F36A53ED1CAB05E0099CEDCCE30C1AFD35613C47F4E4801AC72C7D6BC4899635` |
| OOD | `toolace_schema_given_probe` | base32 | 1000 | `1278C5949FDF98AC95B4D3740EDCB56CB26AE8F3B40C16B61EA2391B39531A6C` | `B479F5813C30E8559C5E808B065CDF3CF2CCC8B234CD202770AA0002B938DC1E` |
| OOD | `toolace_schema_given_probe` | sft32 | 1000 | `93C43A16F00ABA89841A6DBB95094D13184CD6F428A1A17DB72B5AADD7FEC999` | `26A61E9B12D8E63DB4C873BBE719B43DBFBE92C73FC5FBCEA97BB1B9E588BBFE` |
| OOD | `toolace_schema_given_probe` | grpo100 | 1000 | `FDFD63F3780B7DC7899DB8057C16A39AE8E214275E9D8D7584E1E86101F9E546` | `537F9D690FADA2EFB62F1E2ACDA54DBAC689497B3922E7E7F6C5DF7655C8B230` |
| OOD | `toolace_schema_given_probe` | grpo200 | 1000 | `6293C4C1DFEA786B6C9D697400E7871572694CAA71F9E5E440B72107D1902422` | `A73AA460B1C6D6E754BB9871B2119F0FD172585329077B053591AAFD5D6EF544` |
| OOD | `toolace_schema_absent_probe` | base32 | 1000 | `E53BD9A6D5CE00B8F1315AA22E22B91B4E5053D999F65BA95D739D93C4FED1D8` | `B479F5813C30E8559C5E808B065CDF3CF2CCC8B234CD202770AA0002B938DC1E` |
| OOD | `toolace_schema_absent_probe` | sft32 | 1000 | `E8DAEADE3229AA8A9C9CBA6B68EA65250C848F0F13187F710C467E3FAE441C88` | `26A61E9B12D8E63DB4C873BBE719B43DBFBE92C73FC5FBCEA97BB1B9E588BBFE` |
| OOD | `toolace_schema_absent_probe` | grpo100 | 1000 | `3F6F453F5977A31EC14C86BCAE7BDCF5EA0C16F4D57953ECE477B4D183E3CE52` | `537F9D690FADA2EFB62F1E2ACDA54DBAC689497B3922E7E7F6C5DF7655C8B230` |
| OOD | `toolace_schema_absent_probe` | grpo200 | 1000 | `0B37777D6B7927135C1D137B21DDEA65C327BC079F88876E0E78896ADE945E02` | `A73AA460B1C6D6E754BB9871B2119F0FD172585329077B053591AAFD5D6EF544` |

D 的 `max_samples=0`，所以 metrics 冻结的 1333/1820 是实际 expected rows；OOD 的四条 run 都是 `max_samples=1000`、`max_seq_length=4096`、`max_new_tokens=128`。machine manifest 为每个 slot 保存完整 remote prediction path、source-suite remote path、model path、metrics/run/launch SHA；本地 12/12 slot 的 source-suite 文件均不存在，不能从 metrics 逆推出原 prompt/tools。

### 9.2 全盘候选搜索与拒绝理由

| 扫描域 | 同名候选 | 可填缺失 slot | 结论 |
| --- | ---: | ---: | --- |
| `C:\Users\mousongzhe\agent` | 17 | 0 | 15 个 D 候选 + 2 个 ToolACE smoke；都不匹配缺失模型/规模/rows |
| `C:\Users\mousongzhe\Project` | 0 | 0 | 没有额外 raw |
| `remote_small.tar.gz`，SHA `2C1BF435...EFA8CC` | 17 members / 718 total | 0 exact target member | tar 与 extraction 的候选集合一致，没有被漏解压的目标文件 |

| candidate 类别 | 文件数 | 直接拒绝原因 |
| --- | ---: | --- |
| GRPO100/200 attempt1/2/3 与 singleload 的 holdout/cross-source | 13 | 缺失 slot 是 base32/SFT32；这些文件只重复已有 GRPO 模型，且不同 attempt 的 raw SHA 多数不同 |
| `smoke_native_base5_20260617_135957` holdout/cross-source | 2 | manifest 实际是 `base_8b`、`Qwen3-VL-8B-Instruct`、`max_samples=2`，不是 32B base/SFT full run |
| `smoke_base_8b_20260617_232315` 两个 ToolACE | 2 | 实际 8B、每套 2 rows，不能填四个 32B model × 1000 rows slot |

候选总数按 path 是17；其中GRPO100 singleload holdout与attempt3 holdout的SHA完全相同，所以按content SHA去重会少1。machine manifest保留17条path provenance并全部标为`REJECT`，`eligible_candidates=[]`。这里的reject是“不能填当前12-slot recovery contract”，不是说这些文件本身损坏。

### 9.3 精确远端定位合同

D 缺失文件应位于两份 launch manifest 的 `output_root` 下：

```text
/data/msz/dataset/online_agent/training_pipeline_v2_language_full/eval/native_tools_v1/results/
  native_qwen3vl_32b_schemaaware_full_20260617_2114/{suite}.predictions.jsonl
  native_tool_restraint_32b_sft_20260618_114113/{suite}.predictions.jsonl
```

OOD 缺失文件应位于四份 attempt3 run dir 下，文件名分别是 `toolace_schema_given_probe.predictions.jsonl` 与 `toolace_schema_absent_probe.predictions.jsonl`。`launch_eval_32b_ckpt100_200_d_ood_compare_20260622.sh` 的 SHA 为 `BF45E2A5903C2A28826828033E876521909D76E7D87F83536EC3644F5821B15F`；它把 `--suites-dir` 固定为 `${OOD_ROOT}/suites`、`--output-root` 固定为 `${OOD_ROOT}/results/${run_id}`。本地 machine manifest 已展开 12 条完整 remote path，可直接作为远端只读复制清单。

## 10. 为什么标准同步里没有 Raw 文件

`local_process_archive_20260629.json` 的 SHA 是 `EF4D98EAFAB166170696B7A44CA9CEF29DF8A193850E381ADF18B81A3095710E`，其 `excluded` 明列 `predictions.jsonl`。`Project/report/muxi_alignment_20260629/sync_manifest.json` 的 SHA 是 `4BEFF4CBE0FA441AB88E66843432545BDEC8525BDD13FA38B230BA054A476BC1`，policy 同样写明排除 raw predictions。因而“普通同步目录没有”和“隐藏 extraction 保留部分 raw”可以同时成立。

原始 `remote_small.tar.gz`（SHA `2C1BF435FDC42EDBDC376A03105B63E345E289B986D83BADA0152F7081EFA8CC`）共有718个普通文件；定向枚举找到17个缺口-suite同名 member，但0个是12条 exact target path。因此缺口不是 extraction 漏解压，而是 small archive 创建时就未包含。

这也解释了为什么本轮不把 61 MB 全局 132 文件复制进 `cv`：简历仓库只保存审计程序、轻量 JSON manifest 和人可读报告；原始内容留在只读 extraction，由 full SHA 定位。

## 11. Fail-closed 后续计算

```python
def paired_suite_ready(bundle, suite):
    rows = bundle.common_support[suite]
    require(rows.all_four)
    require(rows.set_equal and rows.order_equal)
    require(bundle.suite_input_sha[suite])
    require(bundle.prompt_and_schema_sha[suite])
    require(bundle.generation_config_sha)
    require(bundle.scorer_code_and_backend_sha[suite])
    require(bundle.checkpoint_content_sha)
    return True
```

当前六个 suite 只通过前三行中的 common-support 部分；suite input、prompt/schema、generation、scorer backend 与 checkpoint content identity 尚未整体闭合。四个缺口 suite 连 `all_four` 都不满足。因此本轮不运行 paired bootstrap、不发布 uplift，也不把 `37.8→95.4/95.6` 改写成同协议因果收益。

## 12. 面试口径与 Ownership 边界

### 可以说

> “我对十套件 dashboard 做了第二层 raw audit。隐藏 extraction 找回28/40个primary JSONL、17,828行，六个suite的四模型ID set/order exact。我又扫描agent、Project和原始tar：17个同名候选全部是GRPO其他attempt或8B两行smoke，0个能填12个缺失slot；但每个slot的metrics/run SHA、expected rows和remote path已经冻结。因此我没有用同名文件凑数，也没有把partial support包装成完整统一benchmark。”

### 不能说

1. “十套件 raw bundle 已完整恢复”——只有 28/40、6/10 common-support。
2. “六个 suite 已证明 SFT/GRPO 因果提升”——只闭合 ID support，未闭合统一 scorer/backend/checkpoint。
3. “project/browser/point proxy 等于真实机器人/browser 成功”——仍没有 effect sink、controller、episode 或物理 outcome。
4. “我实现并运行了历史 evaluator”——本轮证明的是候选人/助手对 archived artifacts 的审计，不改变既有 ownership ledger。
5. “checkpoint 已可复现”——0/6 本地 checkpoint binary 与 load smoke 缺口仍在。
6. “17 个候选说明 raw 已经找齐”——候选的模型、run 或 rows 不匹配；eligible replacement 是 0。

## 13. 下一步

1. 使用 machine manifest 的12条 `expected_remote_path` 做一次受控远端只读复制；若只能恢复一批，先取base/SFT holdout与cross-source，以便与GRPO的1000-case support对齐。
2. 冻结六个已对齐 suite 的 input JSONL、prompt/tool schema、generation config、scorer code/config/semantic backend 和 checkpoint content manifest。
3. 在同一 frozen scorer 上逐 raw output 重算 per-case contribution，再做 paired difference、bootstrap interval 与 failure transition matrix。
4. 由候选人完成 Robot Harness ownership/结果解释口述；在此之前 8 张项目卡与全局 269 张卡继续 `unseen`。
5. 不创建 `coaching_state.md`，不启动 `PER-019`，不增加同义 aggregate 页面。

## 参考来源（References）

1. [Robot Harness Ten-Suite Aggregate Bundle Gate](robot_harness_10suite_aggregate_bundle_gate.html)。
2. [Machine-readable Raw Bundle Manifest](robot_harness_common_support_raw_bundle_manifest.json)。
3. [Robot Harness Claim–Evidence Inventory](robot_harness_claim_evidence_inventory.html)。
4. [Robot Harness Ownership Ledger](robot_harness_ownership_ledger.html)。
5. [Evidence Manifest](../evidence_manifest.html)。
6. [VOL 05 EVAL-009 Recomputable Raw-Bundle Source Freeze](../../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。
7. Local extraction `C:\Users\mousongzhe\agent\.codex_tmp\remote_sync_20260626_141618\extract\training_pipeline_v2_language_full\`。
8. Local archive policy `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\manifests\local_process_archive_20260629.json`。
9. Local sync policy `C:\Users\mousongzhe\Project\report\muxi_alignment_20260629\sync_manifest.json`。
10. Local archive `C:\Users\mousongzhe\agent\.codex_tmp\remote_sync_20260626_141618\remote_small.tar.gz`。
11. Local launcher `C:\Users\mousongzhe\agent\remote_training_pipeline_v2\scripts\launch_eval_32b_ckpt100_200_d_ood_compare_20260622.sh`。
