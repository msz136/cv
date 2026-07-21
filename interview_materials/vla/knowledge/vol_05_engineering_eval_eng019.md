# VOL 05 Engineering / Evaluation：Config Resolution、Field Provenance 与 Run Identity（ENG-019）

> 状态：`drafted / knowledge_21_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-019`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-019 Config Resolution / Run Identity Source Freeze](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)。  
> 核心边界：Hydra、Pydantic、argparse、torchrun 分别提供局部机制；统一 precedence、逐字段 provenance、secret-safe canonical hash 和 run→checkpoint→eval lineage 仍是项目工程合同。

## 问题（Question）

`VLA-ENG-019`：默认值、YAML/JSON、Hydra Defaults、CLI、环境变量、scheduler 注入和 runtime-derived 值同时存在时，怎样得到唯一、类型安全、可脱敏、可复算的 effective config，并把它绑定到 logical run、attempt、checkpoint 和评估结果？

面试回答应依次说明：

1. **声明 precedence**：不假设跨框架通用顺序；
2. **保留 provenance**：每个叶子字段记录 winning source 和被覆盖候选；
3. **validate 后再 hash**：对 typed、normalized、redacted semantic config 做 canonical serialization；
4. **拆 identity**：semantic run key、logical run、attempt、rank/service ID 各司其职；
5. **用 artifact 证明**：effective config、source map、secret scan、checkpoint/eval manifest 必须同链。

## 知识地图位置与前置依赖

```text
ENG-009 data/transform manifest + ENG-013 reproducibility
                         ↓
defaults/files/env/CLI/runtime → resolve + typed validation
                         ↓
field provenance → semantic/execution/secret classification
                         ↓
canonical run key → logical run → attempt → checkpoint/eval lineage
                         ↓
ENG-018 retry/preemption + ENG-020 secret/permission gate
```

前置：

- `VLA-ENG-009`：dataset/version/transform manifest 与 provenance。
- `VLA-ENG-013`：code/data/environment/RNG/sampler 的复现边界。
- `VLA-ENG-018`：logical run、attempt、rank 与 retry identity。
- `VLA-ENG-020`：secret、token、数据权限和日志脱敏将在独立节点展开。

## 1. 短答：先解析来源，再生成 identity

**30 秒回答**：我先声明 defaults/file/env/CLI/runtime 的覆盖顺序，每个字段保留最终 typed value、winning source 和旧候选；再把配置分成 semantic、execution、secret。对脱敏后的 semantic config 做 canonical JSON，与 code/data/model revision 一起 hash，形成稳定 run key。attempt、rank、服务 run ID 单独记录。当前项目只有部分 args/effective config，没有完整 source map 和 immutable lineage，不能说配置已可复算。

## 2. 直觉：配置合并是一段需要审计的编译过程

不要把 config 当成“一份 YAML”。它更像编译器：defaults、文件、环境变量、CLI 和 runtime facts 是多份输入；resolver 决定覆盖；schema 做类型检查；normalizer 统一路径、revision 和枚举；redactor 移除 secret；canonicalizer 才产生稳定 bytes。

如果只留最终 YAML，就不知道某个 `batch_size=16` 是默认值、环境变量还是 CLI 覆盖；如果只留 shell command，又不知道 `${VAR:-default}` 展开、Hydra composition、`auto` 推导和 typed conversion 后的真实值。因此可复现的对象是“effective typed config + provenance + revisions”，不是某个孤立文件。

## 3. 覆盖顺序必须按框架和项目声明

| 层/框架 | 官方语义 | 工程注意 |
| --- | --- | --- |
| Hydra Defaults | depth-first composition；同 key 后者覆盖；`_self_` 控制当前文件位置 | config group override 与 object override 不同；shell quoting 仍需验证 |
| Hydra CLI | `foo.bar=value`、`+`、`++`、`~` 修改 object/Defaults List | 必须保存原始 token 和解析后的 typed value |
| pydantic-settings | 默认 CLI→init→env→dotenv→secrets→defaults，高优先级覆盖低优先级 | 顺序可自定义；nested deep update 可能混合不同来源子键 |
| argparse | 参数缺失用 default；`type` 做转换/检查 | 不定义 file/env merge，也不记录 provenance |
| torchrun | 注入 rank/world-size/restart/run ID 等 runtime env | rank 可变；不要把一次 rank 当稳定实验 identity |

因此“CLI 永远最高”不是通用事实。一个项目可以选择 `defaults < file < env < CLI < runtime-derived`，也可以禁止 env 覆盖训练超参；关键是把顺序、allowlist 和冲突策略写成 schema 并测试。

## 4. Effective Config 公式与字段级 provenance

假设项目声明右侧覆盖左侧：

\[
C_{eff}=V\!\left(M(D,F,E,A,R;\,P)\right)
\]

变量和实现映射：`D` 是代码/schema defaults，`F` 是 composed file config，`E` 是 allowlisted env，`A` 是 CLI/API overrides，`R` 是 runtime-derived 值，`P` 是显式 precedence；`M` 返回 merged tree 与 source trace，`V` 做类型、范围、互斥和跨字段验证。公式是项目 resolver 合同，不表示各框架默认顺序相同。

每个叶子字段建议记录：

```json
{
  "field_path": "training.global_batch_size",
  "typed_value": 128,
  "value_type": "int",
  "winning_source": "runtime_derived",
  "source_locator": "world_size * micro_batch * accumulation",
  "overridden_candidates": [
    {"source": "yaml", "value": "auto"},
    {"source": "cli", "value": null}
  ],
  "semantic_role": "semantic",
  "redacted": false,
  "included_in_run_key": true
}
```

这个 schema 能回答“为什么是 128”“谁覆盖了 `auto`”“hash 中是否包含它”，并把 config drift 定位到具体 source，而不是靠人工 diff 两份大 YAML。

## 5. Typed validation：hash 前先消除表示差异

以下文本可能语义相同或不同，不能直接按字符串判断：

```text
"1e-4" vs 0.0001
"./data" vs "C:/workspace/project/data"
"true" vs true
"model:latest" vs immutable model revision
batch_size="auto" vs runtime-derived 128
```

在生成 run key 前，应至少完成：

- string→int/float/bool/enum/Path 的 schema conversion；
- 相对路径解析，并优先替换为 dataset/model revision 或 content hash；
- `auto`、插值、默认值和 derived field 展开；
- required/range/choice/互斥校验；
- semantic field 与 execution-only field 分类；
- secret 值删除，只保留 provider/key-version reference。

否则两个语义相同的配置可能得到不同 ID，两个语义不同的运行也可能因为只 hash 原始 YAML 而被误判为同一实验。

## 6. Semantic、Execution、Conditional 与 Secret

| 分类 | 例子 | stable run key | attempt manifest |
| --- | --- | ---: | ---: |
| semantic | dataset/filter/revision、model/processor/normalizer、loss、optimizer、LR、seed、sampler、eval protocol | 是 | 是 |
| conditional semantic | world-size、backend、dtype、worker count | 若改变 batch/sampler/numerics/protocol 则是 | 是 |
| execution | output/log/tmp path、hostname、timestamp | 否 | 是 |
| attempt/runtime | scheduler job/attempt、rank/local-rank、restart count | 否 | 是 |
| secret | access token、password、private key | 不保存 raw value | 只保存 provider/reference/redaction status |

`WORLD_SIZE` 是典型条件字段：如果只是通信布局变化且训练语义被严格保持，可作为 execution/recovery 维度；如果它改变 global batch、sampler partition 或 optimizer schedule，就必须进入 semantic comparison。分类规则应写进 schema，不能靠面试现场临时解释。

## 7. Run Key 与四层 identity

对 normalized、redacted semantic config 使用 RFC 8785 等 canonical JSON，再绑定不可变 revision：

\[
K_{run}=\operatorname{SHA256}\!\left(
JCS(C_{semantic})\,\|\,H_{code}\,\|\,H_{data}\,\|\,R_{model}
\right)
\]

变量和实现映射：`JCS` 输出 canonical JSON bytes；`H_code` 是代码 revision/diff hash，`H_data` 是 dataset/transform manifest hash，`R_model` 是 base model/processor revision。`K_run` 标识实验语义；它不等于 scheduler、TorchElastic、W&B 或 MLflow 的 run ID。

| Identity | 生命周期 | 用途 | 稳定性 |
| --- | --- | --- | --- |
| semantic `run_key` | 同一实验语义 | dedupe、对比、checkpoint/eval lineage | 内容不变则稳定 |
| `logical_run_id` | 一个业务训练目标 | 聚合多个 retry attempt | retry 间稳定，可引用 run key |
| `attempt_id` | scheduler 的一次执行 | failure/retry/preemption ledger | 每次重试变化 |
| rank/service run ID | 当前 worker 或外部跟踪系统 | 通信、日志、UI 查询 | 不当作 semantic identity |

## 8. Secret-safe provenance

“为可追溯而 dump 全部 env”是高危做法。env 中可能有 token、cloud credential、代理、内部路径和数据权限信息；pydantic-settings 官方也警告 debug source output 可能包含 secrets。

安全设计：

1. 只读取 schema allowlist 中的 env key；
2. secret 字段不进入 effective config 明文、命令日志或 canonical bytes；
3. manifest 记录 provider、secret key 名、version/reference 和是否成功注入；
4. 不默认保存 raw secret 的普通 SHA，因为低熵 token/密码可能被离线猜测；
5. 对 stdout、exception、resolved config 和上传 artifact 做 secret-pattern/canary scan；
6. 权限与数据访问策略在 `VLA-ENG-020` 单独形成 gate。

## 9. 本地项目映射与真实性边界

### 9.1 UWM

`remote_muxi_libero_finetune_5tasks_ddp.sh`（SHA `E5B6...D92`）使用 `${VAR:-default}` 接收 env/default，导出 CUDA/MACA/NCCL/W&B/HF runtime env，再以 Hydra CLI override 设置 dataset、run dir、checkpoint、batch、steps 和 model 参数。Artifact Gate 还有 `ds_config_effective.json`。

可说：存在 env→shell default→Hydra CLI override 和 DeepSpeed effective subset。不能说：已保存完整 resolved Hydra tree、field source map、env allowlist、canonical run key，或已把 launcher/config/checkpoint/eval 绑定到同一 immutable manifest。

### 9.2 OpenPiVLA

`formal_train.py`（SHA `51B6...C6F94`）用 argparse 定义 recipe/model/data/batch/LR/LoRA/seed，并读取 `WORLD_SIZE/RANK/LOCAL_RANK`；`formal_plan.json` 保存训练规模/路径，checkpoint `trainer_state.json` 保存 `vars(args)`。三份 YAML 只有 `mode/notes/run_id`，且 formal trainer 未加载它们。

可说：有较完整 effective args snapshot。不能把三份 YAML 说成 formal input config，也不能说 archive/formal lineage、field provenance 或 canonical semantic hash 已闭合。

### 9.3 OPD

`train_opd_online_vl.py`（SHA `BF91...D8D9`）用 argparse 接收训练/教师/DeepSpeed/OPD 参数，并按 `WORLD_SIZE` 把 DeepSpeed JSON 中的 `auto` 改成数值；训练 summary 只保存部分字段。

可说：存在 source JSON→runtime effective mutation，证明原始 config hash 与 effective hash 不能混用。不能说：完整 args、mutated DeepSpeed config、env provenance、old/new OPD run lineage 已归档。

| 项目 | 已有 direct evidence | 仍缺 |
| --- | --- | --- |
| UWM | env defaults、Hydra CLI、DeepSpeed effective subset | full resolved config、source trace、run/checkpoint/eval manifest |
| OpenPiVLA | argparse、formal plan、checkpoint args snapshot | YAML/CLI/env source map、semantic hash、formal/archive lineage |
| OPD | argparse、DeepSpeed JSON、`WORLD_SIZE` mutation、partial summary | full args/effective DS config/env trace、old/new run identity |

## 10. Resolver 与 Manifest 伪代码

```python
def prepare_run(defaults, files, process_env, cli, runtime, schema, revisions):
    # 1. Read only declared env keys; never copy the whole process environment.
    env = read_allowlisted_env(process_env, schema.env_allowlist)

    # 2. Merge with one explicit precedence and retain every losing candidate.
    merged, provenance = merge_with_trace(
        defaults, files, env, cli, runtime, precedence=schema.precedence
    )

    # 3. Resolve interpolation/auto values, then validate the typed object.
    effective = schema.validate(resolve_derived_values(merged, runtime))

    # 4. Classify fields and remove raw secrets before serialization or logging.
    semantic, execution, secret_refs = classify_and_redact(effective, schema)
    run_key = sha256(jcs(semantic), revisions.code,
                     revisions.data, revisions.base_model)

    # 5. Persist the source map and identity before checkpoint/log side effects.
    return persist_immutable_run_manifest(
        run_key, semantic, execution, secret_refs, provenance, revisions
    )
```

伪代码表达 resolve→trace→validate→redact→canonicalize→persist 的顺序；`merge_with_trace`、JCS、secret provider、immutable store 和 schema classification 均需项目实际实现与测试，不能作为已有项目能力证明。

## 11. 验证矩阵

| Case | 输入变化 | 期望 |
| --- | --- | --- |
| same semantics | YAML key 顺序、注释、等价数值表示变化 | canonical semantic hash 不变 |
| true semantic change | dataset revision、LR、seed、normalizer 变化 | run key 改变 |
| execution-only change | output dir、hostname、timestamp 变化 | run key 不变，attempt manifest 变化 |
| precedence conflict | YAML/env/CLI 同时给同一字段 | winner 与 losing candidates 可查询 |
| invalid type/range | `batch=-1`、unknown enum、字符串 bool 歧义 | 在训练前失败，不生成 committed run |
| runtime derived | `auto` 随 world-size 展开 | effective typed value 与推导公式落盘 |
| secret injection | env/CLI 带 canary token | resolved config/log/artifact 不出现 raw canary |
| retry | 同 logical run 新 attempt/rank | semantic key 稳定；attempt/rank ledger 更新 |

至少要保存 resolver version、precedence/schema revision、canonicalization version、effective config hash、source map hash 和 secret-scan result；否则配置可读不等于配置可重放。

## 12. Trade-off、bad case 与追问

### 12.1 Trade-off

- 字段 provenance 增加 manifest 体积和实现复杂度，但能显著降低“参数为什么变了”的调试成本。
- 把更多 runtime 字段纳入 semantic hash 更保守，却可能把等价运行拆成多个 ID；纳入太少则会错误合并不同实验。
- 严格禁止未知 key 能早失败，但会降低临时实验灵活性；可用显式 `experimental.*` namespace 管理。
- secret reference 提升安全性，却要求 secret provider/version 有稳定审计接口。

### 12.2 高概率 bad case

1. 只 hash 原始 YAML，忽略 CLI/env/`auto` mutation。
2. 用 timestamp/W&B ID 当实验 identity，无法判断两个 run 是否同语义。
3. 把 `RANK=0` 编进 stable run key，retry/rank remap 后 identity 改变。
4. 保存最终 config 却不保存 winning source 和 losing candidate。
5. 为 debug dump 全部 env，泄露 token/credential。
6. `"false"` 被当 truthy string，或 `1e-4`/path/enum 未经过 typed validation。
7. world-size 改变 global batch，却仍声称同一个 semantic run。

### 12.3 面试追问

1. Hydra `_self_` 为什么会改变最终值？
2. pydantic-settings 的默认 priority 能否修改？
3. 为什么原始 YAML SHA 不等于 effective config SHA？
4. `WORLD_SIZE` 什么时候算 semantic，什么时候算 execution？
5. W&B run ID、TorchElastic run ID 和 semantic run key 有什么区别？
6. 怎样证明 secret 没进入 resolved config 和日志？
7. retry 后哪些 identity 保持不变，哪些必须变化？

## 13. 结论与下一步

可靠的 config 系统不是“把 YAML 打印出来”，而是把多来源输入解析成 typed effective config，同时保存字段 provenance；随后区分 semantic、execution、attempt 和 secret，对 normalized/redacted semantic object 做 canonical hash，并与 code/data/model revisions 共同形成 run key。logical run 聚合 retry，attempt/rank/service ID 保持独立。

当前 UWM、OpenPiVLA、OPD 已提供有价值的 env/CLI/args/effective mutation 证据，但没有统一 source map、secret-safe canonical hash 或 run→checkpoint→eval immutable lineage，故知识页和题卡均保持 `WARN/unseen`。下一步可口述 `VLA-ENG-019`，或补一个真实 resolver manifest/secret-canary smoke；`VLA-ENG-020` 继续后置。

## References

1. [ENG-019 Source Freeze](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)：官方 revision/SHA、项目路径与真实性边界。
2. Meta, [Hydra 1.3 Defaults List](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/defaults_list.md) 与 [Override Grammar](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/override_grammar/basic.md)。
3. Pydantic, [pydantic-settings 2.14.1](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/docs/index.md)。
4. Python Software Foundation, [Python 3.14 argparse](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Doc/library/argparse.rst)。
5. PyTorch 2.13, [Elastic Run / torchrun](https://docs.pytorch.org/docs/2.13/elastic/run.html)。
6. RFC Editor, [RFC 8785 JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)。
7. 本仓库，[ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)、[ENG-013 Reproducibility](vol_05_engineering_eval_eng013.html) 与 [ENG-018 Retry](vol_05_engineering_eval_eng018.html)。

