# Robot Harness 五/八模型 × 十套件聚合证据门

> 状态：`local-aggregate-frozen / arithmetic-reproduced / common-support-partial-6-of-10 / checkpoint-unverified / WARN`  
> 审查日期：2026-07-20  
> 证据截止：2026-07-20  
> 外部仓库：`C:\Users\mousongzhe\agent\`，审计时 HEAD `3f4c8b3a11ff9512bc18ec4a331ae5ea01555f49`；本页只读审计，没有修改该仓库。  
> 范围：冻结 2026-07-07 的五模型与八 checkpoint 十套件 overview、builder、可定位的旧输入和本地 metrics；2026-07-20 勘误补充隐藏 remote-sync extraction 中恢复的 28/40 primary predictions 与 6/10 common-support suite。不把跨 metric 算术平均冒充统一 benchmark，不把 partial raw bundle 冒充十套件完整恢复，不把远端 checkpoint path 冒充权重 SHA。

## 1. 问题（Question）

Robot Harness 已存在两份十套件总览：一份展示 5 个模型，另一份展示 8 个模型/checkpoint。它们能否关闭以下 P0 缺口？

1. base、SFT、GRPO 是否已经在同一 case、同一样本数、同一 scorer 与同一模板上完成 common-support 对比？
2. `37.8% → 95.4% / 95.6%` 是否可以升级为严格、可复算的训练收益？
3. 十套件平均值是否是一个有统一统计含义的总体准确率？
4. 本地是否保存完整 per-sample predictions、checkpoint binary/config hash 与候选人 ownership？

结论：**仍不能关闭这些 P0 门，但能把 overview 的展示合同、算术、metric 语义、样本数差异和本地可复核边界冻结为一个 immutable aggregate bundle；后续 raw audit 另行证明 6/10 suite 已具备四模型 exact ID support。**

## 2. 结论先行

1. 五模型 JSON 有 5 个模型，checkpoint JSON 有 8 个模型；两者共同的 5 行在 `suite_scores` 与 `suite_n` 上 5/5 精确一致。
2. 两份 JSON 共 13 个 model rows；每行 10 个 suite，`D avg`、`OOD avg`、`all avg` 的 13/13 算术重算全部通过。
3. 十套件并非同一个 metric：共有 `tool_name_accuracy`、`plausible_tool_rate`、`safe_refusal_rate`、`policy_compliance_score_mean`、`normalized_text_match` 五种 primary metric。十套件平均只能叫 **descriptive index**，不能叫总体 success/accuracy。
4. 样本数并不统一：`cross_source` 为 1000/1820/2000，`sft_holdout` 为 1000/1333，两个 ToolACE probe 为 1000/5000。报告自己也记录“不同 run/protocol 与 row counts”。
5. 6 个 archived 模型的 12 个 D/OOD run 目录与 60 份 primary metrics JSON 均可在本地定位；2 个新模型的 4 个 run 目录以及它们的上游 comparison JSON 均未进入本地快照。
6. 60 份普通同步目录 metrics 包含 aggregate、分组统计与 0–80 条 failure sample；这些目录没有 full prediction/raw-output 文件。后续在隐藏 `.codex_tmp/remote_sync_20260626_141618/extract/` 恢复 28/40 个目标 primary JSONL：其中 6/10 suite 的四模型 ID set/order exact，另 12 个文件仍缺。
7. overview 引用的 6 个 distinct model/checkpoint path 全是远端路径；映射到当前 Windows 快照后 0/6 存在，0 个权重文件可哈希。
8. builder 与两个 overview 目录在 `agent` 仓库中是 untracked；当前可信 identity 来自逐文件 SHA，而不是 Git commit containment。

因此本页 verdict 为 `WARN`：它提升的是“聚合报表可解释性与失败边界”，不是模型因果收益、真实机器人闭环或个人 ownership。

## 3. 冻结输入与身份

| ID | 本地 artifact | 状态 | SHA-256 | 能支持 | 不能支持 |
| --- | --- | --- | --- | --- | --- |
| RH10-A01 | `reports/eval_5model_10suite_overview/eval_5model_10suite_overview_20260707.json` | local-direct / untracked | `5D79454550C50969A1441C14DA488AE6689E773EE12252EE6B7DE2AA672BF457` | 5-model 展示数据、metric mapping、n、remote run path | 新模型 raw inputs/checkpoint |
| RH10-A02 | 同目录 HTML | local-direct / untracked | `7950E04962D8817E073093793324D8735BF0344E7C1CCE7407CD88AA21FE2C66` | 当时展示视图 | canonical 计算逻辑 |
| RH10-A03 | `reports/eval_checkpoint_10suite_overview/eval_checkpoint_10suite_overview_20260707.json` | local-direct / untracked | `23AB0A9F8CEDEDDA52C65DDD98C8AB779502EA3B6B0705DE45BB427702C18D48` | 8-model/checkpoint aggregate、10-suite 值与 n | common-support paired result |
| RH10-A04 | 同目录 HTML | local-direct / untracked | `C7B851E72203F914352D2A468D48EEF1A35F60F4DE25BD529EB73922262C34DA` | 当时展示视图 | 全量来源证据 |
| RH10-A05 | `tmp_remote_recovery/build_5model_eval_overview.py` | local-direct / untracked | `69126F6A52B094BDC3219CA3CFFC97F58F6E488990B9348969CEC1B599067D47` | primary metric 选择、mean 与 HTML/JSON 生成逻辑 | 谁设计/运行/验收 |
| RH10-A06 | 旧 32B/8B comparison JSON | local-direct | `5B5C47AF71A01D1FE10F14FCCF09BE8B1AA90B2D0251D70EDA683D9EB9DFC70B` | archived 行的上游 aggregate | checkpoint binary、full predictions |
| RH10-A07 | 新 122B/35B comparison JSON | remote-referenced / local-missing | — | overview 声明的输入路径 | 当前无法独立复算新两行 |

A01–A05 的 Git 状态均为 `??`。因此 HEAD 只记录外部仓库背景，不能替代这些文件的内容身份；本页用 full SHA-256 固定它们。

## 4. Builder 的真实计算合同

builder 固定五个 D suites 与五个 OOD suites，为每个 suite 指定一个 high-is-better primary metric，然后对可用值做不加权算术平均：

\[
I_m^{D}=\frac{1}{5}\sum_{j\in\mathcal{D}}s_{m,j},\qquad
I_m^{OOD}=\frac{1}{5}\sum_{j\in\mathcal{O}}s_{m,j},\qquad
I_m^{all}=\frac{1}{10}\sum_{j=1}^{10}s_{m,j}.
\]

变量解释：\(m\) 是展示行；\(\mathcal{D}\) 与 \(\mathcal{O}\) 分别是五个 D/OOD suite；\(s_{m,j}\) 是 suite \(j\) 自己的 primary metric。直觉上它只是“把十个 0–1 分数等权放在一个仪表盘”；实现对应 builder 的 `statistics.mean`。因为 metric 语义、样本数与 protocol 不同，\(I_m^{all}\) 不是 pooled accuracy、episode success rate 或校准概率。

### 4.1 十套件 metric 映射

| split | suite | primary metric | 语义边界 |
| --- | --- | --- | --- |
| D | `sft_tool_call_holdout` | `tool_name_accuracy` | 工具名选择；不等于 argument/trajectory/physical success |
| D | `project_robot_sandbox_eval` | `tool_name_accuracy` | sandbox tool proxy；不含真实机器人 effect sink |
| D | `safety_side_effect_eval` | `tool_name_accuracy` | 多步安全 suite 的工具名层；完整 safety 还需 forbidden/coverage/side effect |
| D | `browser_deferred_eval` | `tool_name_accuracy` | deferred/format eval；不是 browser runner |
| D | `cross_source_generalization_eval` | `tool_name_accuracy` | 混合来源工具名层 |
| OOD | `appworld_ood_api_policy_probe` | `plausible_tool_rate` | API plausibility proxy |
| OOD | `toolace_schema_given_probe` | `tool_name_accuracy` | 给 schema 的工具名选择 |
| OOD | `toolace_schema_absent_probe` | `safe_refusal_rate` | 无 schema 时拒绝；与 accuracy 目标不同 |
| OOD | `quarantine_safety_probe` | `policy_compliance_score_mean` | policy-compliance 连续分数 |
| OOD | `robovlm_point_general_probe` | `normalized_text_match` | 文本匹配 proxy；不是 2D/3D localization metric |

### 4.2 为什么“每列都 high-is-better”仍不够

同方向只保证“数越大在本列越好”，不保证不同列有共同 estimand。拒绝率、tool accuracy、policy score 与 text match 的一个百分点不是同一种单位；把它们等权平均是一种展示选择，不是由 benchmark 或业务成本推导出的权重。

## 5. 样本数与 common-support 门

| suite | overview 中出现的 n | 当前判定 |
| --- | --- | --- |
| `project_robot_sandbox_eval` | 130 | base/SFT/GRPO100/200 ID set/order exact；scorer/checkpoint 仍未统一冻结 |
| `safety_side_effect_eval` | 289 | 四模型 ID set/order exact；scorer backend 仍不同 |
| `browser_deferred_eval` | 930 | 四模型 ID set/order exact；仍是 deferred proxy |
| `appworld_ood_api_policy_probe` | 732 | 四模型 ID set/order exact；122B/35B raw 仍缺 |
| `quarantine_safety_probe` | 976 | 四模型 ID set/order exact；metric 不是 tool accuracy |
| `robovlm_point_general_probe` | 400 | 四模型 ID set/order exact；仍是 text proxy |
| `cross_source_generalization_eval` | 1000 / 1820 / 2000 | 只找回 GRPO100/200 各 1000 raw；base/SFT raw 缺失 |
| `sft_tool_call_holdout` | 1000 / 1333 | 只找回 GRPO100/200 各 1000 raw；base/SFT raw 缺失 |
| `toolace_schema_given_probe` | 1000 / 5000 | 不同 support |
| `toolace_schema_absent_probe` | 1000 / 5000 | 不同 support |

严格 paired 差值至少需要：

\[
\Delta_{a,b}^{(j)}
=\frac{1}{|C_j|}
\sum_{i\in C_j}
\left(g_j(y_{a,i})-g_j(y_{b,i})\right),
\quad
C_j=E_{a,j}\cap E_{b,j}.
\]

变量解释：\(E_{a,j}\) 是模型 \(a\) 在 suite \(j\) 的 case-ID 集合；\(C_j\) 是两模型 common support；\(y\) 是原始输出，\(g_j\) 是同一版本 scorer。直觉是“先把同一道题和同一个评分器对齐，再算差”。overview 本身只保存 aggregate \((n,s)\)；后续 [raw bundle manifest](robot_harness_common_support_raw_bundle_manifest.html) 为六个 suite 恢复了 \(E\) 与 \(y\) 的文件 identity，但尚未冻结统一 \(g_j\)、checkpoint 与逐 case rescoring，因此本页仍不计算严格 paired uplift。

## 6. 三条 32B 结果的协议核对

| 行 | holdout tool accuracy / n | scorer | semantic backend | project sandbox | safety tool accuracy |
| --- | ---: | --- | --- | ---: | ---: |
| 32B base | 0.378095 / 1333 | `schema_aware_v2` | `qwen_hidden:Qwen3-VL-8B-Instruct` | 0.592308 | 0.217993 |
| 32B SFT | 0.954239 / 1333 | `schema_aware_v2` | `token_overlap_fallback` | 1.000000 | 0.408304 |
| 32B GRPO100 | 0.956000 / 1000 | `schema_aware_v2` | `token_overlap_fallback` | 1.000000 | 0.387543 |
| 32B GRPO200 | 0.956000 / 1000 | `schema_aware_v2` | `token_overlap_fallback` | 1.000000 | 0.373702 |

这张表支持“各自 archived protocol 下的 aggregate”。它不能把 base→SFT/GRPO 当严格因果提升：

- base 与 SFT 虽同为 1333 行，但 semantic backend 不同；
- GRPO 两行只取 1000 行，不能与 1333 行直接 paired；
- SFT 的 safety tool accuracy 高于 GRPO100/200，说明“holdout tool name 接近”不等于 safety 单调提升；
- project sandbox 的 1.0 仍只是高层工具协议 proxy。

## 7. 本地 artifact census

### 7.1 已闭合

| 检查 | 结果 |
| --- | --- |
| overview JSON 可解析 | 2/2 |
| model rows | 5 + 8 |
| 每行 suite 数 | 10/10 |
| mean 重算 | 13/13 rows 通过 |
| 两 overview 重叠行 | 5/5 score+n 精确相同 |
| archived D/OOD run 目录 | 12/12 本地存在 |
| archived primary metrics JSON | 60/60 本地存在 |
| metrics `scoring_version` / `model_path` / `data` 字段 | 代表性 D 文件存在 |

### 7.2 未闭合

| 缺口 | 观测 | 后果 |
| --- | --- | --- |
| 122B/35B input comparison | 新 input JSON 本地不存在 | 两个新模型只能 remote-referenced |
| 122B/35B run dirs | 4/4 本地不存在 | 不能逐 suite 独立重算 |
| full raw predictions | 普通同步 run dirs 没有 raw；隐藏 extraction 恢复 28/40 primary files，6/10 suite 四模型 ID set/order exact | 可建立六个 suite 的 support table；不能称十套件完整 raw bundle或直接发布 paired uplift |
| checkpoint binary | 6 个 distinct `model_path` 映射后 0/6 本地存在 | 不能 content-hash 或 load-smoke |
| scorer/code SHA | overview 只给 metric name，不给完整 scorer revision/hash | 不能证明所有行同实现 |
| builder provenance | builder 与 report untracked | 不能从 Git commit 推出 ownership 或不可变性 |
| physical effect sink | project/browser 都是 proxy/deferred | 不能升级真实机器人/browser 成功 |

`rescored_from_predictions=true` 本身只说明生成 metrics 时曾读取 predictions；后续恢复必须由实际文件、full SHA、rows 与 ordered-ID hash 单独证明。当前 28/40 已这样冻结，剩余 12 个不能用 failure sample 或 metrics 代替。

## 8. 八模型 overview 的安全解读

checkpoint overview 中 `8B GRPO` 的 descriptive `all_avg=0.6511435`、`D avg=0.8004548`、`OOD avg=0.5018322`；它略高于同表的 32B GRPO200 `all_avg=0.6247303`。安全口径是：

> “在这份跨 suite 描述性仪表盘里，8B GRPO 行的等权平均最高；但各列 metric、n、run/protocol 与新旧模型来源不同，所以这不能推出 8B 模型总体优于 32B/35B/122B，也不能作为模型 scaling 结论。”

尤其不能把 122B/35B 的较低 aggregate 解释为“大模型更差”：两行来自 docker vLLM + OpenAI tools protocol 的新 run，本地缺 source comparison 和 run dirs；其 protocol 与 archived native eval 不同。

## 9. Fail-closed 校验伪代码

```python
def audit_ten_suite_bundle(bundle):
    # 1. Freeze every report, builder, scorer, run and checkpoint by content hash.
    require(bundle.report_sha and bundle.builder_sha)
    require(bundle.input_report_shas)
    require(bundle.scorer_code_sha and bundle.suite_manifest_sha)

    # 2. Preserve every case ID and raw model output; aggregates are insufficient.
    for model in bundle.models:
        require(model.checkpoint_sha and model.config_sha)
        require(model.full_predictions)
        require(model.case_ids == bundle.common_case_ids)

    # 3. Re-score all models with one scorer version on the common support.
    paired = score_common_support(
        predictions=bundle.full_predictions,
        scorer=bundle.frozen_scorer,
    )

    # 4. Keep heterogeneous suite metrics separate unless weights/utility are predeclared.
    require(bundle.predeclared_utility_weights)
    return paired
```

当前十套件 bundle 仍会在 `input_report_shas`、`checkpoint_sha`、四个 suite 的 `full_predictions/common_case_ids` 和 `predeclared_utility_weights` 处 fail closed；六个 suite 的 ID support 通过不代表其 scorer/checkpoint gate 已通过。

## 10. 项目真实性与 ownership 边界

### 可以说

> “项目里有一份五/八模型、十套件的聚合仪表盘。我重新冻结了 report 与 builder，13 个 model rows 的均值都能重算；又从隐藏 extraction 恢复了 28/40 个 primary JSONL，六个 suite 的 base/SFT/GRPO100/200 ID set/order exact。它仍混合五种 primary metric，四个 suite raw 不完整，新 122B/35B 输入和所有 checkpoint binary 也不在本地。因此我只把它当 descriptive dashboard 加 partial common-support bundle，不能说已经完成严格同协议因果对照。”

### 不能说

1. “我完成了八模型统一 benchmark”——没有同 support、同 scorer implementation、同 protocol。
2. “8B GRPO 总体优于 122B/35B/32B”——aggregate 的 metric/n/protocol 混合。
3. “37.8→95.6 是 GRPO 的严格 uplift”——SFT 已到 95.4，GRPO n 变为 1000，且缺 paired raw output。
4. “project sandbox 100% 代表真实机器人成功率”——没有 low-level controller、sensor/contact/latency/effect-sink。
5. “这些文件是我独立实现的”——builder/report untracked，候选人尚未完成 ownership confirmation。

## 11. 最小升级路径

1. 从远端归档 `openai_vllm_2models_20260706_1119_comparison.json` 与 122B/35B 四个 run 目录，记录完整 SHA manifest。
2. 恢复缺失的 base/SFT holdout/cross-source 与四模型 ToolACE 两套件共 12 个 primary 文件；随后冻结六个已对齐 suite 的 input/prompt/schema/scorer/backend/checkpoint，并生成逐项 scorer contribution。
3. 固定 scorer code、schema、suite JSONL、prompt/template、generation config 与 semantic backend SHA；不再混用 `qwen_hidden` 与 `token_overlap_fallback`。
4. 获取 checkpoint binary 或 immutable remote content manifest，至少闭合 checkpoint/config/tokenizer/parent lineage。
5. 预先声明 suite 权重或保持十列分开；不把等权 index 命名为总体准确率。
6. 由候选人完成 Robot Harness ownership drill，逐项确认 builder/metric choice/result interpretation 的决定、审查、修改与运行角色。

这些门关闭前，Robot Harness inventory 继续 `WARN`，所有 8 张项目题卡与全局 269 张题卡保持 `unseen`；本页不创建 `coaching_state.md`，也不启动 `PER-019`。

## 参考来源（References）

1. [Robot Harness Claim–Evidence Inventory](robot_harness_claim_evidence_inventory.html)。
2. [Robot Harness Ownership Ledger](robot_harness_ownership_ledger.html)。
3. [Evidence Manifest](../evidence_manifest.html)。
4. [VOL 05 EVAL-005 Aggregation Knowledge](../../knowledge/vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)。
5. [VOL 05 EVAL-006 Benchmark/Scorer Versioning Source Freeze](../../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)。
6. [VOL 05 EVAL-009 Recomputable Raw-Bundle Source Freeze](../../sources/vol_05_eval009_raw_predictions_episode_trace_video_recomputable_summary_source_freeze.html)。
7. [Robot Harness Project Cards](../../questions/proj_robot_harness.html)。
8. Local bundle `C:\Users\mousongzhe\agent\reports\eval_5model_10suite_overview\`。
9. Local bundle `C:\Users\mousongzhe\agent\reports\eval_checkpoint_10suite_overview\`。
10. Local builder `C:\Users\mousongzhe\agent\tmp_remote_recovery\build_5model_eval_overview.py`。
11. [Robot Harness Common-Support Raw Bundle Manifest](robot_harness_common_support_raw_bundle_manifest.html)。
