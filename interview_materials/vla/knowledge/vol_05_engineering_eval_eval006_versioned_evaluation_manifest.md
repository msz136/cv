# VOL 05 EVAL-006：Benchmark / Environment / Controller / Scorer Versioning

> 状态：`drafted / VLA-EVAL-006 / knowledge_28_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-18  
> 前置：[EVAL-001 Protocol Tuple](vol_05_engineering_eval.html)、[EVAL-004 Paired Significance](vol_05_engineering_eval_eval004_paired_init_seed_significance.html)、[EVAL-005 Aggregation](vol_05_engineering_eval_eval005_macro_micro_weighted_aggregation.html)  
> 来源冻结：[EVAL-006 Source Freeze](../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)  
> 项目边界：五项目目前都缺至少一段 run-specific benchmark→env→controller→scorer→raw-result lineage，本页不升级任何成绩。

## 问题（Question）

怎样给 VLA benchmark、environment、controller 和 scorer 做版本管理，确保两次结果可重放、可diff、可比较？关键是同时保存人类可读版本与不可变内容身份，并生成 resolved semantic manifest 的 protocol hash。

## 1. 直觉：同名考试可能不是同一张卷

`LIBERO-10` 是考试名字，但 task registry/init states 是试卷；environment/assets 是考场；controller 是答题动作如何执行；scorer 是阅卷规则。任一项改变，成功率都可能改变。只记模型 checkpoint，就像只记考生名字却不记试卷和评分标准。

最小链路：

```text
label -> immutable revision/content digest -> resolved manifest
      -> protocol SHA -> episode/summary binding -> semantic diff
```

## 2. Label、SemVer、revision、digest 各做什么

| 身份 | 例子 | 用途 | 风险 |
| --- | --- | --- | --- |
| label | `LIBERO-10`, `latest` | 人类交流 | 可重名、可漂移 |
| SemVer/tag | `v1.2.2` | release/API lineage | API compatible 不等于 score compatible；tag还可能是 object |
| revision | Git/HF/dataset commit | 定位树 | 不含 dirty diff/effective config |
| digest | file/OCI/manifest SHA | exact bytes/semantic identity | 不解释内容是否正确 |

强回答不是“都用 hash”，而是 label + revision + digest + resolved semantics 四层一起保存。

### 2.1 SemVer 的边界

SemVer 的 major/minor/patch描述 public API兼容性。修复 success predicate、reset 或 parser 的 patch 可能保持 API，却改变指标。评测需要独立的 semantic diff 和 protocol digest。

### 2.2 Env ID 的边界

Gymnasium 的 versioned ID 能区分 `name-vN`，但 unversioned name 可能解析到 latest。manifest 必须保存 resolved EnvSpec、entry point、kwargs、wrapper graph和 max steps，而不是用户输入字符串。

### 2.3 Runtime tag 的边界

OCI digest 是 content identity；`image:latest` 不是。保存 `repo@sha256:...`，并补 mounted code/data/config、lockfile和 driver/hardware，因为 container digest 不覆盖宿主与外部挂载。

## 3. Evaluation Manifest 六部分

\[
M_{eval}=(B,E,C,S,P,R).
\]

变量解释：`B` benchmark、`E` environment、`C` controller、`S` scorer、`P` policy bundle、`R` runtime。实现中每部分包含 resolved value、revision、digest与 provenance。

### 3.1 Benchmark

- repo/release/commit；
- ordered suite/task registry 与 task class/instruction；
- split/demo/init/scene/object/assets hashes；
- coverage、seed、aggregation和 local patch；
- task-level override 与 license。

新增 task 或改变 task taxonomy 会改变 target population，必须产生新 benchmark identity。

### 3.2 Environment

- simulator/physics/package/commit/container；
- scene XML/MJCF/URDF、mesh、texture；
- init/reset distribution 与 wrapper graph；
- observation/camera/preprocess；
- physics dt、frame skip、horizon、termination/truncation；
- resolved kwargs/env/CLI source。

same seed 在 environment version变化时不保证same state；仍需 init snapshot/hash。

### 3.3 Controller

- controller type + config bytes/hash + decoded typed summary；
- action dim/order/unit/frame、normalizer、clip和 gripper；
- gains、impedance、interpolation、control/physics Hz；
- action repeat、chunk K、replan queue、latency/fallback；
- policy output到环境command的 mapping hash。

两个 `OSC_POSE` 若 gains、frequency或 gripper sign不同，就是不同 closed-loop protocol。

### 3.4 Scorer

- metric/scorer code/hash；
- predicate/threshold/tolerance/debounce/window；
- parser/normalization/postprocess；
- termination、invalid/exclusion/missing rule；
- aggregation/CI；
- VLM scorer 的 model snapshot、prompt hash、temperature/seed/cache与 human calibration。

scorer bug fix 后应在同一 raw predictions/episodes上跑 old/new scorer，形成 version bridge；没有 raw artifact 时旧新 summary不可比。

### 3.5 Policy 与 runtime

policy bundle：checkpoint/config/processor/normalizer/action schema/load report。runtime：OCI digest、dependency lock、Python/framework/backend/driver/hardware。Git repo若 dirty，commit外再保存 diff hash。

## 4. Protocol Hash 怎么算

\[
protocol\_sha=\operatorname{SHA256}\left(JCS(M_{eval}^{semantic})\right).
\]

变量解释：先 resolve/typed validate/path-normalize/redact/select semantic fields，再按 RFC 8785 canonicalize。key order 或 whitespace 不应改变 hash；controller gain、scorer threshold、task registry或环境asset改变必须改变。

job ID、hostname、临时路径属于 attempt ledger；若 hardware/world-size改变数值或sampler语义，则升级为 semantic field。secret只存provider/key-version reference，不存raw value或可猜测digest。

每个 episode row、video index、summary 和 eval lineage必须引用 `protocol_sha`；同一 aggregate出现多个 protocol hashes时 fail closed。

## 5. Comparability Matrix

| Verdict | 规则 | 可以说什么 |
| --- | --- | --- |
| exact comparable | 除model variable外 semantic manifest相同 | 模型差异 + paired/CI |
| bridge diagnostic | known diff + same checkpoint/init/raw outputs的双跑/双评分 | protocol sensitivity |
| non-comparable | unknown/missing benchmark/env/controller/scorer或多项同时变 | 分开报告，不作模型归因 |

比较顺序永远是 manifest diff → raw/bridge availability → score，不是先看分数再找版本理由。

## 6. 变更与迁移测试

| 组件 | 最小测试 |
| --- | --- |
| manifest canonicalization | reorder keys不变hash；typed semantic值改变hash |
| environment | fixed init reset state/first frame checksum |
| controller | fixed action的command/next-state/clip/gripper round-trip |
| scorer | success/failure/boundary/invalid golden raw outputs old-vs-new replay |
| runtime | fixed batch/episode load、first action与tolerance parity |
| benchmark | ordered registry/split/init/assets diff与common-subset重算 |

发布说明写 semantic diff、expected score impact、bridge result和哪些旧结果不再可比。SemVer patch级别不能跳过这些测试。

## 7. Versioned Manifest Schema

```json
{
  "schema": "eval-manifest-v1",
  "benchmark": {
    "label": "example-suite",
    "repo_commit": "...",
    "task_registry_sha256": "...",
    "init_assets_sha256": "..."
  },
  "environment": {
    "resolved_id": "ExampleEnv-v2",
    "repo_commit": "...",
    "wrapper_graph_sha256": "...",
    "image_digest": "sha256:..."
  },
  "controller": {
    "type": "osc-pose",
    "config_sha256": "...",
    "action_contract_sha256": "..."
  },
  "scorer": {
    "code_sha256": "...",
    "predicate_sha256": "...",
    "invalid_rule": "v1"
  },
  "policy_bundle_sha256": "...",
  "protocol_sha256": "..."
}
```

还需 field provenance、task overrides、dirty diff、dependency lock、aggregation/CI和 parent run；schema本身也要 version。

## 8. 五项目面试映射

### 8.1 UWM

LIBERO default、UWM Table II OOD、repo reset-style、项目 fixed-pruned-init是四套 protocol。`186/250` 缺 run-specific checkpoint/normalizer、250 episodes、exact init/controller/scorer hash；不和0.928/0.79直接比。

### 8.2 WAM

Cosmos使用未pin的RoboCasa fork；observed 0.2.0与official 1.0.1、MuJoCo pin不同。controller pickle需bytes SHA + decoded config。`86/120→84/118`还缺 exclusion和scorer provenance，所以只到harness smoke。

### 8.3 OpenPiVLA

official OpenPI repo/checkpoint可冻结，但archive 97.4缺checkpoint、environment/controller/scorer/raw episodes；formal Qwen run和archive lineage未闭合，不能称same OpenPI protocol。

### 8.4 OPD

original strict、protocol-fixed strict、lenient geometry是不同scorer/parser versions。应在相同raw predictions上双重重算并保留metric code SHA；parser修复不等于模型提升。

### 8.5 Robot Harness

32B base是n=1333 + Qwen hidden embedding scorer；SFT/GRPO ladder使用token-overlap fallback，GRPO n=1000。`37.8→95.4/95.6`混入dataset/scorer/checkpoint变化，需同suite/n/scorer raw predictions与完整run/config/data/scorer hashes。

## 9. Failure Modes

1. **same tag**：tag移动或annotated tag object未dereference；
2. **same commit**：dirty diff、submodule、LFS/remote asset不同；
3. **same package version**：effective kwargs/wrapper/assets不同；
4. **same controller name**：gains/Hz/action mapping不同；
5. **same scorer name**：threshold/parser/prompt/model snapshot不同；
6. **same seed**：env/reset call graph变化导致init不同；
7. **same summary schema**：rows来自多个protocol hash却被聚合；
8. **hash fetish**：保存hash但不保存label、semantic fields和raw artifact。

## 10. 可执行冻结与比较

```python
def build_protocol(resolved):
    # Resolve mutable labels to exact revisions and content digests.
    manifest = collect_resolved_components(resolved)
    require_clean_git_or_diff_hash(manifest)
    require_content_digests(manifest)

    # Canonicalize only typed, redacted semantic fields.
    semantic = redact(select_semantic(validate(manifest)))
    protocol_sha = sha256(jcs_bytes(semantic))
    return manifest, protocol_sha

def comparison_gate(run_a, run_b):
    # Never compare scores before the semantic manifest diff.
    diff = semantic_diff(run_a.manifest, run_b.manifest)
    if diff.only_changes("policy_bundle"):
        return "EXACT-COMPARABLE"
    if diff.is_known() and matched_bridge_exists(run_a, run_b):
        return "BRIDGE-DIAGNOSTIC"
    return "NON-COMPARABLE"
```

这是一套artifact contract，不是本地项目已部署的平台。protocol hash证明“可识别的exact semantics”，不证明实验设计、实现或指标本身正确。

## 11. 高频追问

1. SemVer patch为什么仍可能破坏指标可比性？
2. Gymnasium unversioned env有什么风险？
3. container tag和OCI digest差在哪？
4. Git commit为什么还要dirty diff hash？
5. controller要保存哪些semantic fields？
6. scorer bug fix后怎样bridge旧结果？
7. VLM scorer如何固定prompt/model/cache？
8. protocol hash应包含哪些字段，哪些只进attempt ledger？
9. exact comparable、bridge diagnostic、non-comparable怎么判？
10. 五项目各自最危险的version断点是什么？

## 12. Review Checklist 与下一入口

- [ ] label、release/tag、immutable revision、content digest都可回查；
- [ ] benchmark/env/controller/scorer/policy/runtime resolved manifest完整；
- [ ] canonical typed semantic hash与secret redaction正确；
- [ ] episodes/summary/artifacts绑定单一protocol SHA；
- [ ] semantic diff先于score comparison；
- [ ] migration有fixed-input bridge，缺raw artifact时fail closed；
- [ ] 项目version缺口不升级为模型效果或个人成果。

本节点保持 `WARN/unseen`。下一内容节点固定为 `VLA-EVAL-007`：init / seed / task coverage 与难度分层；真实口述前不创建coaching state。

## References

1. [EVAL-006 Source Freeze](../sources/vol_05_eval006_benchmark_env_controller_scorer_versioning_source_freeze.html)。
2. SemVer 2.0.0、Gymnasium EnvSpec、OCI descriptor与RFC 8785 frozen sources，revision/hash见source freeze。
3. [VOL 04 Benchmark / Evidence Audit](../sources/vol_04_benchmark_evidence_claim_to_protocol.html)。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)。
5. [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
6. [UWM/LIBERO Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
7. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)。
8. [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)。

