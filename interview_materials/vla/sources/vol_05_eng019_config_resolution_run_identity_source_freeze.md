# VOL 05 ENG-019 Source Freeze：Config / CLI / Env 合并、Provenance 与 Run Identity

> 状态：`source_frozen / VLA-ENG-019_planned / WARN`  
> 冻结日期：2026-07-17  
> 证据截止：2026-07-17  
> 本切片只冻结 `VLA-ENG-019` 的官方语义、工程合同和项目证据边界；不生成知识页、题卡或口述成绩。  
> 前置：[ENG-009 Manifest / Provenance](../knowledge/vol_05_engineering_eval_batch2a.html)、[ENG-013 Reproducibility](../knowledge/vol_05_engineering_eval_eng013.html)、[ENG-018 Scheduler / Retry](../knowledge/vol_05_engineering_eval_eng018.html)。

## 问题（Question）

训练参数同时来自代码默认值、YAML/JSON、Hydra Defaults、CLI、环境变量、scheduler 注入和运行时推导时，怎样得到唯一、类型安全、可脱敏、可复算的 effective config，并把它绑定到 logical run、attempt、checkpoint 和评估结果？

本节点要回答：

1. 不同框架的覆盖顺序分别是什么，为什么不能假设存在通用的“CLI 一定最高”规则？
2. 怎样记录每个字段的最终值、类型、来源、旧值和覆盖原因？
3. `RANK`、`LOCAL_RANK`、`WORLD_SIZE`、restart count 等 runtime 字段应进入 semantic run identity 还是 attempt identity？
4. config hash 为什么必须基于解析、验证、脱敏、规范化后的对象，而不是原始 YAML 文本或命令字符串？
5. UWM、OpenPiVLA、OPD 当前分别留下了哪些 config/args/manifest，哪些 lineage 仍无法证明？

## 1. Source Freeze 总表

| 来源 | 冻结版本 / revision | source type | 许可 | 本节点可支持 | 不能支持 |
| --- | --- | --- | --- | --- | --- |
| Hydra Defaults List | `hydra@7ef3acab` / v1.3.2 | official-code/docs | MIT | depth-first composition、同 key 后者覆盖、`_self_` 位置 | 用户项目采用 Hydra、环境变量优先级、自动 run hash |
| Hydra Override Grammar | `hydra@7ef3acab` / v1.3.2 | official-code/docs | MIT | config group 与 config object override；`+`/`++`/`~` 语义 | shell quoting 正确、每次 override 已落盘 |
| pydantic-settings | `1d0ea26f` / 2.14.1 | official-code/docs | MIT | 默认 field priority、deep update、source customization、debug secret warning | 任意项目默认采用该顺序；debug 日志天然安全 |
| CPython `argparse` | `cpython@ebf955df` / 3.14.0 | official-code/docs | PSF-2.0 | CLI default、`type` 转换与 `choices` 等 parser 合同 | config file/env 合并、字段 provenance、semantic run identity |
| PyTorch `torchrun` | docs 2.13 | official docs | BSD-style | `LOCAL_RANK/RANK/WORLD_SIZE/TORCHELASTIC_*` 等 runtime context 与 rank 不稳定边界 | 自动配置 lineage、stable semantic ID、exact resume |
| RFC 8785 JSON Canonicalization Scheme | RFC 8785 | primary standard | IETF Trust | JSON canonical representation 可用于可重复 hash/signature 输入 | 自动选择哪些字段属于 semantic config、自动脱敏 secret |
| 本地项目 artifacts | 2026-07-17 snapshot | local-evidence | local/private | UWM shell/Hydra overrides、OpenPiVLA argparse/args snapshot、OPD argparse/DeepSpeed mutation/summary | 完整 source map、统一 schema、secret-safe canonical hash、跨项目 run lineage |

官方来源只定义各自框架/标准的机制。把 defaults、file、env、CLI、runtime-derived 值合成同一个可审计训练合同，是本节点的工程设计，不是 Hydra、Pydantic、argparse 或 torchrun 自动完成的功能。

## 2. 冻结 revision、原文指纹与许可

| Artifact | URL | SHA-256 | 核验点 |
| --- | --- | --- | --- |
| Hydra `defaults_list.md` | [pinned source](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/defaults_list.md) | `2be5eed7f90a3ee690b7df3fd8d3c0dc228a8378c48c9bfdb6782e39974d8082` | multiple configs 同 key 时 last wins；`_self_` 控制当前 config 相对位置 |
| Hydra `basic.md` | [pinned source](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/override_grammar/basic.md) | `bd3348440a57e7f9e8a63d2e64848cfd5934e22f850887048efc94624bb381a4` | `foo.bar=value`、`+`、`++`、`~`；Defaults List 与 config object 分开 |
| Hydra LICENSE | [pinned source](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/LICENSE) | `52412d7bc7ce4157ea628bbaacb8829e0a9cb3c58f57f99176126bc8cf2bfc85` | MIT |
| pydantic-settings `docs/index.md` | [pinned source](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/docs/index.md) | `569a3398f65c99f3f72c73b891f633f1767c79992110ebb0a90b136cc95205b9` | CLI→init→env→dotenv→secrets→defaults；可自定义；debug 可能泄露 secrets |
| pydantic-settings LICENSE | [pinned source](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/LICENSE) | `eb355a753e020346d33d83bf9769135b89fc610568ac531a01c295bcee7fd998` | MIT |
| CPython `argparse.rst` | [pinned source](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Doc/library/argparse.rst) | `46c9dc41aa479d4f068b644149ca4cb12c4076ef25ddd2e547e50becb611c40a` | 缺省值、字符串→类型转换、choices/required |
| CPython LICENSE | [pinned source](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/LICENSE) | `b0e25a78cffb43f4d92de8b61ccfa1f1f98ecbc22330b54b5251e7b6ba010231` | PSF License Version 2 |
| PyTorch Elastic Run | [docs 2.13](https://docs.pytorch.org/docs/2.13/elastic/run.html) | normalized main text `77d82a42359b5f76a07260cdd9c44abd3a5002a8fff4fd54b59f64a43342560e` | runtime env、restart/run ID、rank/world-size instability；已由 ENG-018 冻结 |
| RFC 8785 text | [RFC Editor](https://www.rfc-editor.org/rfc/rfc8785.txt) | `63d52294eb0e3f0014174288186d388b4ddbf2c67d1ce8af1d9726eb0c3ab240` | canonical JSON 作为 hashing/signing 的稳定输入 |

所有正文 SHA 均对 2026-07-17 取得的 UTF-8 原文计算；Hydra/Pydantic/CPython 使用 pinned GitHub revision，RFC 8785 为不可变 RFC 文本。PyTorch 页面 hash 复用 [ENG-018 Source Freeze](vol_05_eng018_scheduler_preemption_retry_source_freeze.html) 的规范化主文本记录。

## 3. 官方语义：覆盖顺序不是跨框架常量

Hydra 1.3 的 Defaults List 使用 depth-first composition；多个 config 定义同一值时后者覆盖前者，`_self_` 决定当前文件在 Defaults List 的相对位置。Hydra CLI override 又区分：匹配 config group 的操作修改 Defaults List，其余操作修改 config object；`+`、`++`、`~` 分别涉及 append、append-or-override 和 delete。[1][2]

pydantic-settings 2.14.1 的默认优先级是：CLI（启用时）→ settings initializer → environment → dotenv → secrets directory → model defaults；高优先级 source 覆盖低优先级 source，但 nested object 可由低优先级 source 补齐缺失子键。该顺序可以用 `settings_customise_sources` 改写。[3]

CPython `argparse` 只承诺 CLI 参数缺失时使用 default，并用 `type` 做转换/检查；它不定义 YAML、env 与 CLI 的合并顺序。[4] 因而面试回答必须先说“我的项目声明了哪套 precedence”，不能把某个框架的默认值当成普遍规律。

## 4. Engineering Contract：resolve → validate → redact → canonicalize

项目应显式声明合并层和方向。例如右侧优先时：

\[
C_{eff}=V\left(M(D,F,E,A,R)\right)
\]

其中：(D) 是代码/schema defaults，(F) 是 composed file config，(E) 是 allowlisted environment，(A) 是 CLI/API override，(R) 是 runtime-derived 值；(M) 是项目声明的 merge，(V) 是 typed validation。这个公式是工程合同，不表示 Hydra 与 pydantic-settings 的默认顺序相同；项目必须把实际 order 写进 manifest。

每个叶子字段至少保存：

```text
field_path / typed_value / semantic_role
winning_source / source_locator / source_revision
overridden_values[] / conversion / validation
redaction_policy / included_in_semantic_hash
```

仅保存最终 YAML 不足以回答“为什么是这个值”；仅保存命令字符串又无法证明 shell 展开、env 注入和运行时推导后的 typed value。

## 5. Semantic Config、Execution Config 与 Secret

| 类别 | 典型字段 | identity 处理 |
| --- | --- | --- |
| semantic | dataset/filter/revision、model/processor/normalizer、loss、optimizer、LR、seed、batch/sampler、eval protocol | 进入 semantic config hash |
| conditional semantic | world-size、hardware/backend、dtype、worker count | 如果改变 effective batch、sampler、numerics 或 protocol，则进入；否则仍记录在 execution manifest |
| execution/attempt | output/log/tmp path、hostname、scheduler job/attempt、`RANK/LOCAL_RANK`、restart count、timestamps | 不进入 stable semantic ID；进入 attempt ledger |
| secret | token、password、credential、private key | 不落 raw value；只记录 provider、key/version reference 与 redaction status |

TorchElastic 的 rank/world-size 可能变化，因此不能把 `rank0` 或一次 attempt 的 `LOCAL_RANK` 编进稳定 logical run identity。[5] 但 world-size 若改变 effective batch 或 sampler partition，就必须进入 semantic comparison 或显式标为允许变化的恢复维度。

## 6. Canonical Run Identity

原始 YAML 的 key 顺序、注释、浮点/字符串表现和相对路径都可能不同；在语义相同的情况下直接 hash 原始文件会产生不同 ID。推荐先完成类型解析、路径/revision 归一化、secret redaction 和 semantic field selection，再使用 RFC 8785 等 canonical representation 生成 bytes。[6]

\[
run\_key=\operatorname{SHA256}\left(JCS(C_{semantic})\,\|\,code\_sha\,\|\,data\_manifest\_sha\,\|\,base\_model\_revision\right)
\]

这里 `run_key` 标识实验语义，不等于 scheduler job ID、W&B/MLflow ID 或 TorchElastic run ID；`logical_run_id` 可以引用该 key，而 `attempt_id` 每次重试新建。不要把 raw secret 放入 hash：即使只保存 digest，也可能形成离线猜测或跨系统关联风险。

## 7. Local Evidence：UWM

本地 launcher：

```text
C:\Users\mousongzhe\Project\wm\uwm_libero_official_repro\scripts\remote_muxi_libero_finetune_5tasks_ddp.sh
SHA E5B6DCB03FD6612B996AB9DFD3227CB2426E0A147F21FACEE383BBF56EC29D92
```

该脚本使用 `${VAR:-default}` 接受外部 env 或脚本默认值，导出 CUDA/MACA/NCCL/W&B/HF runtime env，再调用 UWM 的 Hydra entrypoint，以 CLI override 写入 `dataset`、`hydra.run.dir`、checkpoint、batch、step、rollout 和 model 参数。它直接证明“env defaults + Hydra CLI overrides”存在。

[ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html) 还记录 `ds_config_effective.json`（SHA `2bf8216f04391ce4323fc79ae74aae9728e8b13f8d4057f281734a0a4da54642`），能证明某个 DeepSpeed effective subset。当前仍没有：完整 Hydra resolved config、逐字段 winning source、env allowlist/hash、launcher SHA 与 run/checkpoint 的同一 immutable manifest。launcher 会打印若干路径/参数，但日志文本不是 typed provenance ledger。

## 8. Local Evidence：OpenPiVLA

formal trainer：

```text
C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py
SHA 51B67D3E04496E68076BF6461506141EBCDDF9A82E6C30AF1FDC0F1F2CCC6F94
```

该代码通过 `argparse` 定义 recipe/model/data/output、batch/accumulation、LR、dtype、checkpoint、LoRA 和 seed；从 env 读取 `WORLD_SIZE/RANK/LOCAL_RANK`。`formal_plan.json` 保存 recipe/resource/training scale/paths，checkpoint 的 `trainer_state.json` 保存 `vars(args)`，因此它比“只留命令”更接近 effective args snapshot。

三份 YAML 的 SHA 分别为 `78D6C4C9D5A1BA06FCA6C6EE6234DC8400A9501346D9BC8B272A82EED76A3601`、`247151EC457DA90A57AF3416F4A79C563523993345ADABC35316F2612A1F36D2`、`42D0C0A341C118A66C856EF97509F414240F279942D158B6D4BF916FCB64B592`，每份只有 `mode/notes/run_id` 三个顶层键；`formal_train.py` 未加载 YAML。故不能把这些 YAML 当作 formal trainer 的完整输入 config，也不能据此证明 YAML→CLI→env precedence、canonical run hash 或 archive/formal lineage。

## 9. Local Evidence：OPD

formal OPD source：

```text
C:\Users\mousongzhe\muxi\train_opd_online_vl.py
SHA BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9
```

该脚本用 `argparse` 接收 model/data/output、教师、route、DeepSpeed、batch、optimizer、save/resume 和 OPD generation 参数；`load_teacher_ds_config()` 读取 JSON，并用 `WORLD_SIZE` 把 `train_batch_size/micro_batch/accumulation` 的 `auto` 改成数值。这个 runtime mutation 说明“source JSON hash”不等于“effective config hash”。

本地 `zero2.json` / `zero3_opd_maca_gradclip5.json` SHA 为 `C2F2E295B3F2E8E67CBCDF1052710D7ED7A1AD9D95F4C44C9EC40AF178A50BA9` / `CA5C4030CCEC5DAE16B3614ED072035E6BB05CFD3BF411C92CC51D411D6C655F`；两个训练 manifest SHA 为 `CED5328B5EDE5D2BD758A9E6C96841F7A37F69E32EFC1140EFB7F8EF05F9B60F` / `7BB3CF6463507E5C0D8C4DECCDA7AE7B2288B0DA1D4A019E4CAB862C18AB6185`。训练结束的 `opd_online_run_summary.json` 只保存 data/model/teachers、部分 save 与 OPD summary，没有完整 `vars(args)`、mutated DeepSpeed config、env provenance、code/config hash。因此现有证据不能证明唯一 effective config 或 old/new OPD run identity 已闭合。

## 10. Resolver 与 Manifest 伪代码（工程合同）

```python
def resolve_run(defaults, files, env, cli, runtime, schema, source_revisions):
    # 1. Read only allowlisted env keys; never copy the whole process environment.
    env_values = read_allowlisted_env(env, schema.env_allowlist)

    # 2. Merge with one declared precedence and keep every overwritten candidate.
    merged, field_provenance = merge_with_trace(
        defaults, files, env_values, cli, runtime, precedence=schema.precedence
    )

    # 3. Convert and validate types before creating an identity.
    effective = schema.validate(merged)
    semantic, execution, secret_refs = classify_and_redact(effective, schema)

    # 4. Canonicalize semantic values, then bind code/data/model revisions.
    run_key = sha256(jcs(semantic), source_revisions.code,
                     source_revisions.data, source_revisions.base_model)

    # 5. Persist effective config and provenance before training side effects begin.
    return immutable_manifest(run_key, semantic, execution, secret_refs,
                              field_provenance, source_revisions)
```

伪代码不代表 Hydra、Pydantic 或任一项目已有实现；`merge_with_trace`、schema、JCS、secret provider 和 immutable store 均需实际落地、测试并绑定 checkpoint/eval。

## 11. Gate 与不能使用的口径

| Gate | 当前状态 | 退出条件 |
| --- | --- | --- |
| official precedence/type/canonicalization | `PASS WITH WARNING` | 官方机制已冻结；跨框架统一顺序继续标为项目合同 |
| UWM config lineage | `WARN` | full resolved Hydra config + field source map + launcher/env/code/data/checkpoint hashes |
| OpenPiVLA config lineage | `WARN` | args snapshot 与 recipe/YAML/command/env source map、canonical hash、checkpoint/eval manifest 对齐 |
| OPD config lineage | `WARN` | full args + mutated DeepSpeed effective config + env provenance + old/new run lineage |
| secret safety | `PENDING` | env allowlist、redaction test、no-secret-log scan、secret reference/version contract |
| knowledge/card | `DRAFTED / UNSEEN` | ENG-019 知识节点和一张题卡已生成；保持 `unseen`，后续补 resolver/provenance/secret-canary artifacts；ENG-020 后置 |
| oral drill | `PENDING` | 候选人真实回答后才创建或更新 coaching state |

不能说：

1. “用了 Hydra，所以每次 run 自动可复现”——仍需 resolved config、source revisions、data/model/checkpoint 与 runtime artifact。
2. “CLI 永远覆盖 env”——只在声明并验证的 resolver/default policy 中成立。
3. “YAML 一样就是同一个 run”——runtime-derived、code/data/model revision 和 typed value 可能不同。
4. “W&B/TorchElastic run ID 就是实验 identity”——它们是服务/运行标识，不自动等价于 semantic config hash。
5. “把所有 env dump 进日志最可追溯”——可能直接泄露 token、credential 和内部路径。
6. “config 文件 hash 已经绑定 effective config”——CLI/env/default/`auto` mutation 后的值可能不同。

## 12. Source Gate 结论

ENG-019 的 source-first gate 已闭合：Hydra 支持 composition/override，pydantic-settings 给出可自定义的 source priority，argparse 支持 CLI default/type conversion，torchrun 注入并可能改变 runtime identity，RFC 8785 提供 canonical JSON。它们共同支持“显式 resolve、typed validate、field provenance、secret redaction、semantic/attempt identity 分离”的工程合同，但不证明本地三个项目已经完成这套系统。

当前本地最强证据是：UWM launcher 的 env→Hydra CLI override、OpenPiVLA 的完整 argparse snapshot、OPD 的 JSON→`WORLD_SIZE` effective mutation和部分 run summary。共同缺口是统一 schema、逐字段 provenance、secret-safe canonical config hash 以及 run→attempt→checkpoint→eval 的 immutable manifest。Verdict 保持 `WARN`；ENG-019 知识页与一张 `unseen` 题卡已在下游 bounded slice 生成，ENG-020 不展开。

## References

1. Meta, [Hydra 1.3 Defaults List](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/defaults_list.md)。
2. Meta, [Hydra 1.3 Basic Override Grammar](https://github.com/facebookresearch/hydra/blob/7ef3acab78b46bf82370e7931f748aef5fd80e5f/website/versioned_docs/version-1.3/advanced/override_grammar/basic.md)。
3. Pydantic, [pydantic-settings 2.14.1 documentation](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/docs/index.md)。
4. Python Software Foundation, [Python 3.14 `argparse`](https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Doc/library/argparse.rst)。
5. PyTorch 2.13, [Elastic Run / torchrun](https://docs.pytorch.org/docs/2.13/elastic/run.html)。
6. RFC Editor, [RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)。
7. 本仓库，[ENG-004..006 Artifact Gate](vol_05_local_artifact_gate_eng004_006.html)、[ENG-013 Reproducibility](vol_05_eng013_reproducibility_source_freeze.html)、[ENG-018 Scheduler / Retry](vol_05_eng018_scheduler_preemption_retry_source_freeze.html) 与五项目 evidence inventory。
