# UWM `libero_90.pt` 本地 Immutable Checkpoint Manifest Gate

> 状态：`local-binary-verified / base-checkpoint-only / fine-tune-lineage-open / WARN`
> 审查日期：2026-07-21；证据截止：2026-07-21
> 范围：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer` 中 UWM 官方 LIBERO base checkpoint 与加载脚本。
> 结论先行：本次在用户提供的 project copy 中发现并重新哈希了 `libero_90.pt` 本体；它是一个可读取的 4.04 GB PyTorch archive，SHA-256 为 `E43C562E1D5145662006877AAC0FB30C3C5D57302AEFC16524DA2D862D694602`。归档内部可静态确认顶层包含 `model`、`optimizer`、`scaler`、`scheduler`、`action_normalizer`、`lowdim_normalizer` 与 `step=100000` 等字段，且 `action_normalizer`/`lowdim_normalizer` 的值为 `None`。这关闭了“base binary 只有远端路径引用”的旧缺口，但不证明 RoboCasa 微调后的 `models.pt`、normalizer、fresh-process reload、评估 scorer 或个人 ownership。

## 1. Question 与证据边界

本页只回答四个可审计问题：

1. 当前 project copy 是否真的包含 UWM `libero_90.pt` binary？
2. 文件的字节数、SHA-256、容器结构和 checkpoint step 是什么？
3. 它能支持“加载了哪个 base checkpoint”的哪一级面试表述？
4. 哪些仍不能从 base binary 推断到 RoboCasa fine-tune 或结果 claim？

本页把四层证据分开：

| 层级 | 本页材料 | 允许的结论 |
| --- | --- | --- |
| `local-direct` | `.pt` 文件、zip member inventory、`data.pkl` 静态 opcode、下载脚本与 README | 文件存在、hash、容器字段、上游路径/用途说明 |
| `upstream/recipe` | `download_uwm_libero90_checkpoint.sh`、UWM transfer README | 该文件被项目当作官方 UWM LIBERO base 输入；下载来源与命名合同 |
| `local-inference` | `models_100001`、`step=100000` 与字段结构的共同解释 | 这是可用于迁移初始化的训练 checkpoint，而非只含裸模型权重的 state dict |
| `unverified` | RoboCasa `models.pt`、normalizer JSON、fresh reload、episode scorer、ownership | 不能把 base checkpoint 的 hash 当作 fine-tune 或 benchmark 证据 |

## 2. Immutable manifest 合同

对 checkpoint artifact (c)，最小可复核记录定义为：

\[
M(c)=\bigl(\text{path},\;\text{bytes},\;\text{sha256},\;\text{container},\;\text{logical\_step},\;\text{role}\bigr).
\]

变量解释：`path` 是 project copy 内的相对路径，`bytes` 是文件长度，`sha256` 用于检测替换，`container` 是 PyTorch archive 的成员摘要，`logical_step` 是 checkpoint 内记录的训练步，`role` 区分 base、fine-tune、eval-only 等身份。直觉上，只有这些字段一起冻结，面试中才可以回答“server/loader 实际拿到哪一个文件”，而不是只复述一个字符串路径。此处的 `logical_step` 与 `role=official UWM base` 仍需和上游发布记录一同解释，不能单独证明训练 provenance。

```python
def verify_checkpoint(path, expected_sha256):
    # 1. 只读计算文件 hash；不覆盖、不重新保存、不改变用户 project copy。
    digest = sha256_file(path)
    assert digest == expected_sha256

    # 2. 只列出 PyTorch zip members 与 data.pkl；不执行 pickle 中的任意对象构造。
    members = list_zip_members(path)
    metadata = disassemble_pickle_without_unpickling(path, "models_100001/data.pkl")

    # 3. 把 base binary、fine-tune checkpoint 和 normalizer 分开登记。
    return {"sha256": digest, "members": members, "metadata": metadata}
```

## 3. 本地文件 manifest

根目录：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer`。

| ID | 相对路径 | 字节数 | SHA-256 | 角色 | 状态 |
| --- | --- | ---: | --- | --- | --- |
| C01 | `_downloads/libero_90.pt` | `4,044,929,076` | `E43C562E1D5145662006877AAC0FB30C3C5D57302AEFC16524DA2D862D694602` | UWM LIBERO base checkpoint binary | `local-direct` |
| C02 | `_downloads/libero_90_chunk7.bin` | `268,435,456` | `13B10DFCEF838A3AF30EAF2BF21CE7A306BB31A9B62AD5EA63A60BFA8427596D` | 下载过程中的独立 chunk artifact；不宣称可重组为 C01 | `local-direct / role-open` |
| C03 | `download_uwm_libero90_checkpoint.sh` | `697` | `0C18903D55BB25E1EAFE8731B7770A5BBCCF9E4B5178985CC3DE0362B21F8DCE` | 下载与软链接合同 | `local-direct` |
| C04 | `README.md` | `6,087` | `E05378FC0E1718B073635EFB5159B9FF7DBB0EFB50C817FE7C2F35E1E57C63D0` | 项目用途、checkpoint smoke 与 hash 文字记录 | `local-direct` |

文件时间只作为辅助字段：C01 最后修改时间为 `2026-06-22 11:07:14 UTC`。时间戳不能替代 hash，也不能证明该文件被某一次 RoboCasa rollout 实际加载。

### 3.1 Project-wide negative scan

为避免“只看了一个已知目录”造成假阴性，本次还在 `C:\Users\mousongzhe\project` 全树按扩展名扫描 `.pt/.pth/.ckpt/.safetensors/.bin`。结果只有 C01 与 C02 两个文件：

| 扫描结果 | 数量 | 解释 |
| --- | ---: | --- |
| `libero_90.pt` | 1 | UWM base binary，C01 |
| `libero_90_chunk7.bin` | 1 | 独立下载 chunk，C02；未证明可重组 |
| `models.pt` / `checkpoint_step_*.pt` | 0 | 当前 project copy 中没有可直接冻结的 RoboCasa target checkpoint |
| `.safetensors` / `.ckpt` / `.pth` | 0 | 未发现其他常见 checkpoint 格式 |

```powershell
# 只读负向检索：不把日志中的字符串或目录名误当作 binary。
Get-ChildItem $project -Recurse -File |
  Where-Object { $_.Extension -in '.pt','.pth','.ckpt','.safetensors','.bin' }
```

这个负向结果只对当前 Windows project copy 有效；它不能排除远端 `/data/msz/...` 或其他未挂载目录中存在 target checkpoint。因此安全结论是“本地 target binary 尚未归档”，不是“target checkpoint 从未生成”。

## 4. Container 与静态 metadata 复核

`libero_90.pt` 以 PyTorch zip archive 开头（magic bytes `PK\x03\x04`），共 `1070` 个 member，唯一顶层目录为 `models_100001/`。本次没有调用 `torch.load` 去构造完整 4 GB tensor；而是读取 `data.pkl` 并用 `pickletools` 做不执行对象的 opcode inspection。这样能确认字段名与 storage metadata，同时避免把静态检查误写成模型 forward 或 fresh-load 证明。

| 检查 | 结果 | 可支持的结论 |
| --- | --- | --- |
| archive header | `PK\x03\x04` | 文件是 zip-based PyTorch serialization |
| member count | `1070` | 归档含大量 tensor storage，不是空壳路径 |
| top-level prefix | `models_100001/` | 文件内部目录名与 step 命名一致 |
| `data.pkl` bytes | `182,415` | metadata pickle 可独立读取 |
| tensor-key strings | `453`（unique `452`） | 约 452 个带 weight/bias/running-stat 名称的 tensor key 字符串；不等同于 loader report 的 model-key count |
| optimizer / scaler / scheduler | 字段字符串存在 | 归档不仅有 model 字段；是否按某次 run 恢复仍需 loader log |
| `last_epoch` | `100001` | scheduler metadata 中存在该值 |
| `step` | `100000` | 顶层末尾 metadata 记录该逻辑 step |
| normalizer fields | `action_normalizer=None`、`lowdim_normalizer=None` | base binary 不提供可直接继承的 target normalizer |

这里的“字段存在”来自 pickle opcode，不是把所有 tensor 载入 CPU 后的运行时对象 dump；因此它是 metadata-level evidence。项目 README 另记录了一次 checkpoint smoke：`454/454` 个 shape-compatible model keys 被加载，并按设计跳过两个 normalizer 字段。[1][2]

## 5. Base checkpoint 与 RoboCasa fine-tune 的身份分离

当前身份元组应写成：

```text
base = (
  role="official UWM LIBERO base",
  path="_downloads/libero_90.pt",
  sha256="E43C...694602",
  logical_step=100000,
  action_normalizer=None,
  lowdim_normalizer=None
)

target_finetune = (
  role="RoboCasa target fine-tune",
  checkpoint_path="not frozen in this gate",
  normalizer_path="run-specific JSON, not frozen here",
  scorer="not frozen here"
)
```

因此，base binary 的 SHA 可以证明“这份本地 UWM 初始化文件没有被无声替换”，但不能证明：

- RoboCasa `models.pt` 是由它初始化并成功保存的；
- `--reset-action-head`、7D→12D action adaptation 或 task/prompt/state/right-view head 采用了哪个 exact config；
- fine-tune 后的 normalizer 与 checkpoint 属于同一 run；
- rollout server 在 fresh process 中重新加载了同一 binary；
- `0–2/54` 或 `0/54` 等闭环结果来自可复放且同一 scorer 的 checkpoint；
- 上游 UWM architecture、迁移 patch 或完整 run 是候选人独立原创。

## 6. 与既有 evidence gate 的 reconciliation

旧的 `vol_05_local_artifact_gate_eng004_006` 以当时可见的 report snapshot 为依据，曾把 `libero_90.pt` 标成“只有远端路径引用”。本次新证据位于用户明确提供的 `project` copy，且包含 C01 binary；因此该旧结论应改写为：

| Claim | 修订前 | 当前修订 | 仍未闭合 |
| --- | --- | --- | --- |
| base checkpoint binary | remote-path-only | `local-direct`，C01 hash 可复算 | 上游发布 revision、下载来源与 loader run UUID |
| base model key load | report reference | README + loader code 支持 `454/454` smoke claim | 一次带 stdout/summary/hash 的 fresh rerun |
| target fine-tune checkpoint | unverified | 仍 `unverified` | `models.pt` binary/hash、normalizer、config、fresh reload |
| closed-loop benchmark | unverified | 仍 `unverified` | episode JSONL、scorer/version、denominator、matched protocol |
| ownership | unverified | 仍 `unverified` | 逐文件个人/协作/工具辅助确认 |

这不是把 base checkpoint 误升级为 RoboCasa 结果；它只修正了“本地是否有 base binary”这一项。

## 7. 面试安全口径

### 30 秒回答

“我会把 base checkpoint 和 fine-tune checkpoint 分开验。当前 project copy 里确实有 UWM 的 `libero_90.pt`，文件大小是 4,044,929,076 bytes，SHA-256 是 `E43C562E...694602`；我还静态检查了 PyTorch archive，确认它内部是 `models_100001`、逻辑 step 100000，并且 action/lowdim normalizer 在 base 中是空值。项目 README 和 loader report 记录过 shape-compatible smoke，但这只能证明 base 初始化文件和加载合同，不能证明 RoboCasa 的 `models.pt`、normalizer、fresh-process reload 或 benchmark scorer。后者必须用 run-specific checkpoint hash、effective argv、episode bundle 和 ownership 再闭合。”

### 高频追问

1. **为什么 `summary.json` 的 checkpoint 字符串不够？** 因为字符串没有绑定文件 hash、加载进程、normalizer、代码 revision 和 run UUID；它可能只是传入参数或上游路径。
2. **base hash 是否证明微调成功？** 不证明。它只冻结初始化文件；微调后的 binary 和 target normalizer 是另一条 lineage。
3. **为什么不直接 `torch.load` 作为验证？** 4 GB 文件的静态 manifest 足以先验证 identity；完整 load 还需要记录 device、代码 revision、shape-match report 和 fresh-process output parity。
4. **你能说“我训练了这个 checkpoint”吗？** 只有在 run manifest、保存产物、日志、加载复现与 ownership 逐项闭合后才能用更强措辞；当前安全说法是“按 UWM base checkpoint 开展迁移/训练尝试并审计加载合同”。

## 8. Gate 状态与下一步

| Gate | 状态 | 下一最小补件 |
| --- | --- | --- |
| C01 base binary existence/hash | `PASS` | 保留 SHA 与 byte count；不移动原文件 |
| C01 archive metadata | `PASS WITH WARNING` | 如需更强结论，保存一次 trusted loader 的 CPU shape report |
| base→RoboCasa fine-tune lineage | `WARN` | `models.pt`、exact config、normalizer 与 shared run ID |
| fine-tune fresh-load parity | `UNVERIFIED` | 新进程 reload + parameter/schema parity |
| closed-loop scorer/denominator | `UNVERIFIED` | episode JSONL、scorer revision、task/init/seed tuple |
| ownership | `PENDING` | 候选人逐文件标注亲手/协作/工具辅助/只运行/只审查 |

本页不新增题卡，不改变任何 `unseen` 状态，也不把 C01 的 base hash 写成 RoboCasa 成绩。现有 `PROJ-UWM-*` 与 RoboCasa ActionHeadFix 题卡继续保持 `unseen`。

## 参考文献（References）

1. 本地项目 README：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer\README.md`（C04；含 base hash、checkpoint smoke 口径与运行合同）。
2. 本地加载实现：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer\uwm_robocasa_train.py`（`torch_load_checkpoint`、`load_shape_compatible`、`checkpoint_smoke`）。
3. 本地下载合同：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer\download_uwm_libero90_checkpoint.sh`（C03）。
4. 本地 base binary：`C:\Users\mousongzhe\project\wm\uwm_robocasa_transfer\_downloads\libero_90.pt`（C01；SHA-256 由本次只读扫描重算）。
5. [UWM/LIBERO/RoboCasa transfer evidence freeze](vol_05_uwm_libero_robocasa_transfer_evidence_freeze.html)。
6. [UWM/LIBERO project claim inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)。
7. [UWM RoboCasa ActionHeadFix P0 audit](../evidence/projects/uwm_robocasa_actionheadfix_30epoch_train_eval_p0_audit.html)。
