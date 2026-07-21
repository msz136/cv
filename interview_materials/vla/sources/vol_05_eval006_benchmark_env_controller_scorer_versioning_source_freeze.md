# VOL 05 EVAL-006 Source Freeze：Benchmark / Environment / Controller / Scorer Versioning

> 状态：`source_frozen / VLA-EVAL-006 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-18  
> 证据截止：2026-07-18  
> 本切片冻结 evaluation manifest、human label / revision / content digest 分层、benchmark/env/controller/scorer semantic identity、canonical protocol hash 与五项目 version 边界；下游只生成一张 `VLA-EVAL-006` 原子题卡，VOL 05 同步为 knowledge/cards 28/44。

## 问题（Question）

两个结果都写“LIBERO-10 success”或“schema-aware-v2 accuracy”并不代表同一评测。benchmark task registry、environment/fork/assets、controller config/timing、scorer code/threshold/parser、model/normalizer 和 runtime 任何一项变化，都可能改变结果。强回答必须把这些 resolved values 写入 immutable manifest，并让 summary、episode 和 artifact 共同引用一个 protocol digest。

本 source gate 固定以下链路：

```text
human label / SemVer
  -> immutable repo revision + asset/config/content digests
  -> resolved benchmark-env-controller-scorer manifest
  -> canonical JSON bytes + protocol SHA-256
  -> episode/summary/artifact binding + semantic diff gate
```

## 1. 冻结来源、revision 与许可

公开 blob hash 对 2026-07-18 取得的 UTF-8 原文计算。版本标准和官方实现支持身份机制；它们不证明本地项目已保存完整 manifest，也不把“API compatible”升级成“score comparable”。

| ID | 来源 | 类型 / revision | 固定入口 | SHA-256 | 支持范围 |
| --- | --- | --- | --- | --- | --- |
| S1 | Semantic Versioning 2.0.0 | primary specification / tag `v2.0.0`, commit `7c834b3f3a4940d77ab593bc32583004d6a426a9` | [semver.md](https://github.com/semver/semver/blob/7c834b3f3a4940d77ab593bc32583004d6a426a9/semver.md) | `d2b702f9e767ef75a4e0665675903a454000884b6d2171f97c1c380fef5e708a` | major/minor/patch 相对 public API 的兼容语义；tag 中无独立 LICENSE 文件，本文只引用规范 |
| S2 | Gymnasium environment registration | official-code / `v1.2.2`, commit `a923da5d4415a1aa5195d99341069da5e16deed7`, MIT | [registration.py](https://github.com/Farama-Foundation/Gymnasium/blob/a923da5d4415a1aa5195d99341069da5e16deed7/gymnasium/envs/registration.py) | source `3053db8b8d4716a2eaa56dc7a5b5d65e80085a091a21dd9fb63e060d524f6d01`; LICENSE `7dacaa9772e856aee6943b32ef663d3634d91d72ec7bbc74d136943673f91e18` | `namespace/name-vN` 解析、EnvSpec registry、unversioned/latest fallback 风险 |
| S3 | OCI Image Specification | primary standard / tag object `de7a13cc...` → commit `147f9c13cedb47a0c4d9a11a222961073d585877`, Apache-2.0 | [descriptor.md](https://github.com/opencontainers/image-spec/blob/147f9c13cedb47a0c4d9a11a222961073d585877/descriptor.md) | descriptor `89399b5ffabfeb9688b66de9afcf08b60691710d94d0f5b061cb30e6fbc75428`; manifest `fc35d252c5cc192ce972bbd52b560184ba427a8a374107fc5cdd7442034cd867`; LICENSE `b0a3f39513927db306adabea11d14c23f079d4febcea241d123a68d1a0d45418` | content descriptor 的 digest/size/mediaType、content addressability 与 verification；tag 名不等于 immutable runtime digest |
| S4 | RFC 8785 JSON Canonicalization Scheme | primary standard / RFC 8785 | [RFC text](https://www.rfc-editor.org/rfc/rfc8785.txt) | `63d52294eb0e3f0014174288186d388b4ddbf2c67d1ce8af1d9726eb0c3ab240` | canonical JSON 作为稳定 hash/signature input；不决定 semantic fields 或 secret policy |
| S5 | ENG-019 Config / Run Identity Source Freeze | canonical local source | [source](vol_05_eng019_config_resolution_run_identity_source_freeze.html) | `6a2934512295cdf5ecdcde3ef8e9b2d597bc2f3af529d7c6f053a16df3aceb54` | resolve→typed validate→redact→JCS hash、semantic/attempt identity 分离 |
| S6 | LIBERO / UWM / Cosmos / RoboCasa benchmark audit | canonical local source + frozen upstream commits | [audit](vol_04_benchmark_evidence_claim_to_protocol.html) | `58a5636e953f44c2aa27e3acf65c621460186daf3732b916eac70e6ffab2de6a` | LIBERO default、UWM OOD/reset/fixed-init、Cosmos fork/controller/scorer protocol diff |
| S7 | 五项目 evidence inventories | local evidence boundary / 2026-07-17..18 | [manifest](../evidence/evidence_manifest.html) | individual hashes recorded in review | WAM/UWM/OpenPiVLA/OPD/Robot Harness 的真实 version/scorer/lineage 缺口 |

本轮抓取 OCI `v1.1.1` 时，`ls-remote` 首先返回 tag object `de7a13...`，dereference 后才得到 content commit `147f9c...`。这不是旁枝：它直接说明“release tag、tag object、target commit、raw blob hash”是不同身份层。

## 2. 四层身份：label 不等于 content

| 层 | 例子 | 作用 | 不能单独证明 |
| --- | --- | --- | --- |
| human label | `LIBERO-10`, `RoboCasa v1`, `schema-aware-v2`, `latest` | 交流、检索 | exact code/assets/config |
| release version / tag | `v1.2.2`, `2.0.0` | release lineage、API contract | tag 不可变、runtime exact bytes |
| immutable revision | Git commit、HF revision、dataset snapshot | 定位源码/模型/数据树 | dirty local diff、resolved runtime/config |
| content digest | file SHA、OCI digest、canonical manifest SHA | 验证 exact bytes/semantic manifest | 内容语义正确、结果有效 |

最低原则：保存可读 label，也保存 immutable revision 和 content digest。只有 hash 没有人类语义难以审计；只有版本字符串无法重放。

### 2.1 SemVer 不能替代 metric version

SemVer 的 major/minor/patch 围绕 public API compatibility。一个“patch bug fix”可能不破坏 API，却改变 reset、controller gain、success threshold 或 parser，从而改变 benchmark score。因此评测 version 必须额外保存 semantic diff 和 scorer/protocol hash，不能说“都是 v1.x，所以指标可比”。

### 2.2 Unversioned environment 的风险

Gymnasium frozen code把 environment ID 解析为 namespace/name/version，并允许 unversioned name 指向 latest versioned environment，同时给出 warning。生产评估不能只存 `env_name`；应保存 resolved `EnvSpec.id`、entry point、kwargs、wrapper stack、max episode steps 和 package commit。

### 2.3 Container tag 与 digest

OCI descriptor 把 digest 定义为内容标识，并要求/建议消费方校验 digest/size。`image:latest` 或普通 tag 可移动；manifest 必须保存 resolved `repo@sha256:...`，同时保存 lockfile、driver/backend 与硬件信息。container digest 也不替代 mounted code/data/config hash。

## 3. Versioned Evaluation Manifest

将一次评测的 semantic manifest 写成：

\[
M_{eval}=(B,E,C,S,P,R),
\]

其中 `B` 是 benchmark，`E` 是 environment，`C` 是 controller，`S` 是 scorer，`P` 是 policy/model bundle，`R` 是 runtime。每部分都保存 resolved value、revision、content hash 和 field provenance。

### 3.1 Benchmark `B`

- benchmark/suite name 与 release/commit；
- ordered task registry、task definition/class、language instruction；
- dataset/split/demo/init-state/scene/object registry hash；
- sampling/seed/coverage 与 aggregation contract；
- benchmark assets、license 和 local patch/diff hash。

### 3.2 Environment `E`

- simulator/physics engine/package/Git commit/container digest；
- task class、scene XML/MJCF/URDF、object meshes/textures；
- reset/init distribution、wrapper graph、observation/camera/preprocess；
- physics timestep、frame skip、horizon、termination/truncation；
- resolved env kwargs 与 environment-variable/CLI provenance。

### 3.3 Controller `C`

- controller type 和 exact config bytes/hash；若是 pickle，同时保存 decoded canonical summary；
- action dim/order/unit/frame、normalizer、clip/saturation、gripper semantics；
- gains、impedance、interpolation/ramp、control Hz/physics Hz/action repeat；
- predicted chunk、executed K、queue/replan、latency/fallback；
- policy action → environment command mapping code hash。

“都叫 `OSC_POSE`”不证明 gains、input convention、frequency 或 gripper mapping 相同。

### 3.4 Scorer `S`

- scorer code commit/file hash、metric name/version；
- success predicate、threshold、tolerance、debounce/window、termination relation；
- parser/normalization/postprocess、invalid/exclusion/missing rule；
- aggregation weights 与 CI method；
- model-based scorer 的 provider/model snapshot、prompt/system template hash、temperature/seed、response cache与 human calibration。

若 scorer 从 `strict parser` 改成 `protocol-fixed`，旧 raw predictions 应用新旧 scorer 双重重算形成 bridge；没有 raw prediction 时，两个 summary 默认不可比。

### 3.5 Policy / Runtime `P,R`

policy bundle 至少包含 checkpoint、config、processor/tokenizer、normalizer/stats、action schema 和 load report hash；runtime 包含 container digest、dependency lock、Python/framework/backend/driver/hardware。Git commit 还要配 clean status；dirty worktree 保存 patch/diff hash。

## 4. Canonical Protocol Digest

先对所有配置 resolve、类型校验、路径/版本归一化、secret redaction 和 semantic field selection，再用 JCS 生成 bytes：

\[
protocol\_sha=\operatorname{SHA256}\!\left(JCS(M_{eval}^{semantic})\right).
\]

变量解释：`M_eval^semantic` 只包含会改变样本、模型行为、环境、controller、scorer 或统计结论的字段；scheduler job ID、临时路径等进入 attempt ledger，不进入稳定 protocol identity。实现上每条 episode、summary、视频 index 和 checkpoint-eval lineage都引用同一个 `protocol_sha`。

不能 hash 原始 YAML 后就结束：CLI/env/default、relative path、pickle、runtime mutation 和 unversioned env 可能使 effective semantics 不同。也不能把 secret raw value放入 manifest/hash。

## 5. Comparability Gate

对两个结果先做 semantic diff：

| verdict | 条件 | 允许结论 |
| --- | --- | --- |
| `EXACT-COMPARABLE` | 除预注册 model/checkpoint variable 外，semantic manifest 相同；raw/summary 完整 | matched model effect + uncertainty |
| `BRIDGE-DIAGNOSTIC` | 存在已知 protocol diff，但用同 checkpoint/common init/raw predictions 做双跑/双评分 bridge | quantifies protocol sensitivity，不冒充原始 benchmark复现 |
| `NON-COMPARABLE` | benchmark/env/controller/scorer 缺失、未知或同时变化 | 分开报告；只能提出待验证 hypothesis |

同 task 名、相同分母、相同 seed 或相同 package version都不能覆盖 semantic diff。若 summary 混入多个 `protocol_sha`，聚合器应 fail closed。

## 6. 变更分类与升级策略

| 变更 | 典型影响 | 处理 |
| --- | --- | --- |
| 增加 task、改 task order/split | target population/权重变化 | 新 benchmark version；共同 registry 重算 |
| 修改 init distribution/assets/physics | state distribution/dynamics 变化 | environment major semantic change；matched bridge |
| controller gain/Hz/action map | closed-loop transition 变化 | 新 controller digest；不可只记同名 controller |
| scorer bug/threshold/parser | label/metric 变化 | 新 scorer version；对同 raw outputs 双重重算 |
| logging-only | 不应改变 outcome | patch + golden replay；仍保存 code hash |
| dependency/container rebuild | numerics/runtime 可能变 | resolved OCI digest + workload parity smoke |

即使改动被发布者标成 patch，也要按“是否改变 evaluation semantics”判断，而不是照搬 SemVer级别。

## 7. 最小 manifest schema

```json
{
  "manifest_schema": "v1",
  "benchmark": {
    "name": "example-benchmark",
    "repo_commit": "...",
    "task_registry_sha256": "...",
    "init_assets_sha256": "..."
  },
  "environment": {
    "resolved_env_id": "ExampleEnv-v2",
    "repo_commit": "...",
    "wrapper_graph_sha256": "...",
    "runtime_image_digest": "sha256:..."
  },
  "controller": {
    "type": "osc-pose",
    "config_sha256": "...",
    "action_contract_sha256": "...",
    "control_hz": 20
  },
  "scorer": {
    "name": "task-success",
    "code_sha256": "...",
    "predicate_sha256": "...",
    "invalid_rule": "pre_registered_v1"
  },
  "policy_bundle_sha256": "...",
  "protocol_sha256": "computed-after-canonicalization"
}
```

JSON 只是最小结构；真实 manifest还要保存 field provenance、task-level overrides、dirty diff、dependency lock、aggregation/CI 和 parent run。

## 8. Version Smoke / Migration Tests

每次 component version 变化至少做：

1. canonicalization：key order/whitespace 不改变 `protocol_sha`；typed value 或 semantic field变化必须改变；
2. environment：同 init snapshot 的 reset observation/state checksum；
3. controller：固定 action input 的 command/next-state/clip/gripper round-trip；
4. scorer：golden success/failure/boundary/invalid raw outputs 的新旧 scorer重放；
5. runtime：相同 fixed batch/episode 的 load、first action 与 tolerance parity；
6. migration report：列 semantic diff、expected metric impact、bridge结果和不再可比的旧 artifact。

这些是 version gate，不等于 EVAL-010 完整 regression/canary 系统；本节点只冻结 identity 与最小迁移验收。

## 9. 五项目真实性边界

### 9.1 UWM / LIBERO

LIBERO frozen default、UWM Table II OOD、UWM repo reset-style、项目 fixed-pruned-init 至少是四套 manifest。项目 inventory 记录 upstream LIBERO revision，但 final `186/250` 仍缺 run-specific checkpoint/normalizer、250 episode、exact init/scorer/controller hash。不能因为都叫 LIBERO task 就比较 0.744、0.928 和论文 0.79。

### 9.2 WAM / Cosmos RoboCasa

Cosmos `ROBOCASA.md` clone 未 pin 的 `moojink/robocasa-cosmos-policy`；访问日 fork package 0.2.0，而 official frozen RoboCasa 是 1.0.1，MuJoCo pins也不同。controller 来自 pickle，必须保存 bytes SHA 和 decoded config。WAM `86/120` raw 与 `84/118` trusted 还缺两条 exclusion、scorer和完整 episode provenance，不能叫 official benchmark。

### 9.3 OpenPiVLA

official OpenPI 可冻结 repo/checkpoint入口；archive `97.4%` 缺 exact checkpoint、suite/task/init/trial、environment/controller/scorer和 raw episodes。formal Qwen runs 与 archive result lineage 未闭合，所以不能用“OpenPI版本一致”推断同一 runtime/protocol。

### 9.4 OPD

point `original strict`、`protocol-fixed strict`、`lenient geometry` 是不同 scorer/parser versions；跨版本数值必须带 scorer label，并优先在相同 raw predictions 上重算。by-format/by-pool table和checkpoint曲线也要绑定 metric code SHA，不能把 parser修复说成模型能力 uplift。

### 9.5 Robot Harness

32B base 使用 `n=1333` 与 Qwen hidden embedding scorer，SFT/GRPO ladder 使用 token-overlap fallback，GRPO holdout `n=1000`。这些是 dataset/scorer/checkpoint protocol变化，现有 `37.8→95.4/95.6` 不能当同协议因果提升；需要统一 suite/n/scorer/raw predictions和 run/config/data/scorer SHA。

## 10. 伪代码：冻结、绑定与比较

```python
def freeze_eval_manifest(resolved):
    # 1. Resolve tags/names to immutable commits, digests and exact bytes.
    manifest = collect_benchmark_env_controller_scorer(resolved)
    require_immutable_revisions(manifest)
    require_clean_git_or_diff_hash(manifest)

    # 2. Select typed semantic fields, redact secrets, then canonicalize.
    semantic = select_semantic_fields(validate_types(manifest))
    semantic = redact_secret_values(semantic)
    protocol_sha = sha256(jcs_bytes(semantic))

    # 3. Every raw episode and summary must bind to the same protocol hash.
    return {"manifest": manifest, "protocol_sha256": protocol_sha}

def compare_eval_runs(a, b):
    # Compare manifests before scores; fail closed on unknown semantic drift.
    diff = semantic_diff(a.manifest, b.manifest)
    if diff.only_changes("policy_bundle"):
        return "EXACT-COMPARABLE"
    if diff.is_known() and has_matched_bridge(a, b):
        return "BRIDGE-DIAGNOSTIC"
    return "NON-COMPARABLE"
```

伪代码是工程合同，不是五项目已存在的统一工具。不能把 `protocol_sha` 本身当成“评测正确”的证明；它只使 exact semantics 可识别、可diff、可绑定。

## 11. Source Gate 结论与下一入口

EVAL-006 保持 `WARN`：SemVer/EnvSpec/OCI/JCS 一手语义、versioned evaluation manifest、semantic diff gate 与五项目的版本漂移已冻结；本地五项目仍没有统一、run-specific、raw-bound protocol manifest，因此不产生新的可比结果或简历强 claim。

下一内容节点固定为 `VLA-EVAL-007`：init / seed / task coverage 与难度分层。题卡保持 `unseen`，真实口述前不创建 `coaching_state.md`。

## References

1. Semantic Versioning 2.0.0, [pinned specification](https://github.com/semver/semver/blob/7c834b3f3a4940d77ab593bc32583004d6a426a9/semver.md)。
2. Gymnasium `v1.2.2`, [environment registration](https://github.com/Farama-Foundation/Gymnasium/blob/a923da5d4415a1aa5195d99341069da5e16deed7/gymnasium/envs/registration.py)。
3. OCI Image Specification `v1.1.1`, [descriptor](https://github.com/opencontainers/image-spec/blob/147f9c13cedb47a0c4d9a11a222961073d585877/descriptor.md)。
4. RFC 8785, [JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.txt)。
5. [ENG-019 Config / Run Identity](vol_05_eng019_config_resolution_run_identity_source_freeze.html)。
6. [VOL 04 Benchmark / Evidence Audit](vol_04_benchmark_evidence_claim_to_protocol.html)。
7. [Evidence Manifest](../evidence/evidence_manifest.html) 与五项目 inventories。

