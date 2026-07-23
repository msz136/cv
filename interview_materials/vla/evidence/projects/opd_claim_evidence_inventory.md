# OPD / VLM Grounding Claim–Evidence Inventory（OPD-01）

> 状态：`drafted / local_direct_audit / ownership_audited / WARN`  
> 审查日期：2026-07-19  
> 证据截止：2026-07-19  
> 项目范围：五 expert 数据混合、OPD student route metadata、coldstart、online student-rollout OPD、raw-holdout box/point/text 评估  
> 证据仓库：`C:\Users\mousongzhe\muxi`（只读审计；本轮未修改该仓库）  
> 仓库 HEAD：`756e27e16adcfb3ccbfe98c2920dda42095b127f`

## 结论先行

本轮可以把 OPD 的数据路由、五教师训练机制、OPD5000 checkpoint 曲线和 raw-holdout 去重协议从项目叙述提升到 `local-direct` 或 `report-supported`。`build_expert_mixes_seed0_v2.py` 明确了 800,000 train / 20,000 eval、image-hash split、五个 expert 和 spatial-relation 重采样；`build_opd_student_v1.py` 与 `audit_opd_student_v1.py` 明确了 999,900 条最终 train、46,599 条 eval、seen/unseen/hard、boundary/format-conflict route metadata 与硬校验；formal `point/train_opd_online_vl.py` 和 run summary 明确了五教师 `preloaded_zero3`、teacher selection、coldstart teacher-rollout/full-vocab KL 与 OPD5000 student-rollout/full-vocab KL。根目录同名脚本是 legacy teacher-rollout/top1-CE 路线，不能作为 formal KL claim 的代码锚点；详见 [Training Objective Lineage Gate](opd_training_objective_lineage_gate.html)。

OPD5000 的结果必须绑定到具体 checkpoint 和子集：在 10,000 条 raw-holdout 上，checkpoint-3000 的整体 box IoU 为 0.4761，checkpoint-5000 的 Box Acc@0.5 为 0.5238、Point Hit@50/100 为 0.7493/0.8729，checkpoint-4000 的 keepalive text exact 为 0.8784。不同 pool 的最佳 checkpoint 不一致，不能把 checkpoint-5000 说成所有指标的最佳。

当前 verdict 保持 `WARN`。本地没有模型权重、optimizer state、完整 raw predictions 或可复算的远端 checkpoint bundle；`OPD final`（旧版 8-model 主评估）与 `OPD5000 checkpoint-5000`（新版 new-experts 曲线）不是同一条 run 记录；没有 SFT-only、single-teacher、no-synthetic 或 synthetic-ratio ablation。因此可以讲“组合路线及结果”，不能把提升单因果归因于 OPD，也不能把 Git author 自动等同于个人独立 ownership。逐文件 ownership 已在 [OPD Ownership Ledger](opd_ownership_ledger.html) 建立，但 `msz136` 初始 scaffold、`mousongzhe` 后续提交、远端运行者、工具/协作边界仍需候选人确认。

## 1. 证据标签与面试门槛

| 标签 | 含义 | OPD 例子 |
| --- | --- | --- |
| `local-direct` | 当前工作区可直接读取的源码、配置、manifest、summary 或 committed table | 五 expert 配额、route metadata、run summary、指标表 |
| `local-inference` | 由相邻本地证据推断，未被单独对照实验直接证明 | route specialization 对泛化的因果贡献 |
| `report-supported` | committed report 有结论，但底层远端权重、raw log 或 predictions 未同步 | 远端模型路径、旧版 OPD final 的完整 run 描述 |
| `protocol-limited` | 数字存在，但 scorer、样本量、checkpoint 或输出协议不能直接横比 | original point strict 与 protocol-fixed strict |
| `ownership-partial` | Git author 或项目页支持参与线索，但没有逐文件 ownership ledger | 相关 commit author 为 `mousongzhe` |
| `unverified` | 缺少可审计 artifact，或无法复算 | 真实机器人闭环成功率、单因素 OPD uplift |

面试回答使用四级门槛：C0=知道概念；C1=有本地源码/配置；C2=有设计取舍、失败样例或对照；C3=有 immutable run、checkpoint、完整 scorer、raw prediction 与 ownership。当前 OPD 的训练机制达到 C1/C2，强结果多为 C2，尚未形成完整 C3 bundle。

## 2. Claim reconciliation

| ID | 当前 claim | 证据 | Verdict | 面试处理 |
| --- | --- | --- | --- | --- |
| `OPD-CL-001` | 五个 expert 分工覆盖 reasoning、object、region、spatial relation、RoboPoint | `build_expert_mixes_seed0_v2.py` 的 `EXPERT_TRAIN_PLAN`、`REL_BUCKET_WEIGHTS` | `local-direct` | 可解释数据分工；不要说五个 expert 已分别在 raw-holdout 独立最优，因独立 expert eval 未冻结 |
| `OPD-CL-002` | expert mix 为 800k train / 20k eval，按 image hash 做 5% candidate eval | 脚本常量与 split 函数 | `local-direct` | 可讲 image-level split 和 source/expert metadata |
| `OPD-CL-003` | OPD student 数据按 domain/general/boundary/format-conflict 构造并记录 route | `build_opd_student_v1.py`、`report.md`、最终 summary | `local-direct` | 可讲 60/25/10/5 设计、seen 100k 边界与格式冲突；要说明最终 train 为 999,900 |
| `OPD-CL-004` | train/eval 完成 JSON、坐标、图片、fingerprint 与 overlap 审计 | `audit_opd_student_v1.py`、`report.md` | `local-direct / report-supported` | 可报无坏 JSON、无 train/eval image/fingerprint overlap；不要把它当作模型质量证明 |
| `OPD-CL-005` | coldstart 是五教师 teacher-rollout + full-vocab KL，约 500 steps | `point/train_opd_online_vl.py`、coldstart launcher/summary、objective lineage gate | `local-direct / report-supported` | 可解释为什么先让 student 贴近 teacher 分布；未提供独立 coldstart ablation；veto beta>0 时 target 不是纯 teacher |
| `OPD-CL-006` | 正式 OPD 是 student rollout、同一 response 上 teacher forward、route-based full-vocab \(D_{KL}(q_\beta\Vert p_S)\)，5000 steps | `point/train_opd_online_vl.py`、OPD5000 launcher/summary、objective lineage gate | `local-direct` | 可画训练链路并说明 beta=0 才是 teacher∥student；需绑定 max_new_tokens=64、prefix=64、skip=64,000、ZeRO-3 配置 |
| `OPD-CL-007` | OPD5000 ckpt5000 在 point/box/text 上取得 0.7493/0.8729、0.5238、0.8724 | by-format table、by-pool table、run summary | `local-direct / protocol-bounded` | 绑定 10k raw-holdout、格式子集 n=1400/6100/2500；不能说所有域最佳 |
| `OPD-CL-008` | 不同任务池的最佳 checkpoint 不一致 | by-pool table | `local-direct` | semantic-nav=ckpt2000、VG region/relation=ckpt3000、keepalive=ckpt4000、point=ckpt5000；用来说明多目标 trade-off |
| `OPD-CL-009` | raw-holdout 10k 无训练图片泄漏、fingerprint/source-line/prompt-answer-image 重复 | `evalset_summary.json`、`dedupe_audit.json` | `local-direct` | 可讲评估集构造和 leakage gate；重复图片路径不等价于重复样本 |
| `OPD-CL-010` | 旧版 `OPD final` 为 8-model 主评估中的综合结果 | `raw_holdout_eval_8models_report.md` | `report-supported / run-conflict` | 与 OPD5000 ckpt5000 分开报；旧版综合表的 point strict 受协议问题影响 |
| `OPD-CL-011` | point strict=0 的 base/instruct/大模型不能直接解释为不会 point grounding | `report.md` protocol-fixed section、point protocol comparison | `protocol-limited` | 同时报告 original strict、protocol-fixed strict、lenient geometry；避免把 parser failure 说成能力不存在 |
| `OPD-CL-012` | OPD 单独造成全部提升，或所有实现均为个人独立完成 | 无完整 ablation；已有 [ownership ledger](opd_ownership_ledger.html)，但候选人逐项确认未完成 | `unverified / ownership-partial` | 只说“我负责/参与了数据、路由、训练与评估设计的哪些部分”，不要过度承诺因果或 ownership |

## 3. Source inventory（输入冻结）

| Source | 类型 | SHA-256（当前工作区） | 能支持 | 不能支持 |
| --- | --- | --- | --- | --- |
| `build_expert_mixes_seed0_v2.py` | local evidence | `19D5EF9E25D8664EA983880B79373098A77D19D5DA11D5B2AD17BEE6195C2F2C` | 五 expert 配额、hash split、relation buckets、source metadata | 实际训练是否按脚本完成、个人 ownership |
| `build_opd_student_v1.py` | local evidence | `44BCC42DE40249363DAE908314DB79BF658AAE4A5DA008732CD724389D5CD3BE` | target/candidate route、seen/unseen/hard、格式冲突 prompt、gold/fingerprint 字段 | 模型是否学会 route、最终远端文件是否与当前脚本完全同版 |
| `audit_opd_student_v1.py` | local evidence | `B38F92C2FE681C250D3BA61C35299935501D014BA8B34965C7ED8D529A92D6BB` | JSON、长度、坐标、图片、重复与 overlap 审计逻辑 | 未执行的环境、权重或训练质量 |
| `train_opd_online_vl.py`（root legacy） | local evidence | `BF9120B5D88180EA4C4725C6F4934913F35FDD36ECB4BC8E6B3B089FB964D8D9` | teacher rollout、teacher top1 hard labels、token CE、legacy mode string | coldstart/OPD5000 的 full-vocab KL 或 student-rollout formal claim |
| `point/train_opd_online_vl.py`（formal） | local evidence | `7103E3B28068A30978F2B14AD980E51CEC2EC60A0445B2B52243342CDA286336` | route teacher、teacher/student rollout switch、full-vocab \(D_{KL}(q_\beta\Vert p_S)\)、veto/prefix/entropy/top-k diagnostics | 远端 checkpoint binary、optimizer state、raw prediction 与因果 uplift |
| `REPORT.md`（Windows 不区分大小写时显示为 `report.md`） | committed report | `0EC1E16D1E15AEDC918B910775E7BFD7C769D9715DFBBB9127C09E23F44A4170` | 数据快照、point protocol 修正、OPD 叙事和历史 run 说明 | raw predictions、远端权重、可复算 checkpoint lineage |
| `report/opd5000_newexperts_20260601/artifact_manifest.json` | local manifest | `035764A0461DEE5942AB25AF1BDFCD2514BD69AAC473B2DE8E43F3A7EC86021A` | synced scope、remote root、final model paths、排除项 | 本地可加载模型权重（manifest 明确排除） |
| `report/opd5000_newexperts_20260601/model_assets_eval_table.md` | local table | `5BA42BA56EFCD586A770D258E8536390942AB249606CA4D4AD88F70FB3BEBE45` | expert 训练摘要、evaluated checkpoints、指标口径 | 五 expert 独立 raw-holdout 结果 |
| `report/opd5000_newexperts_20260601/opd5000_ckpt_eval_by_format_table.md` | local table | `7D797EE1269E082AEEE6AD851EB341588CFCF3B28C939BF870307C01004B9934` | ckpt1000–5000 的 box/point/text 子集指标 | 跨 run 或跨 scorer 因果比较 |
| `report/opd5000_newexperts_20260601/opd5000_ckpt_eval_by_pool_table.md` | local table | `54CA01CAD342AC7F96C1CC0D622E102AB2C9E22E7514180213EF90A48043ADCA` | 八个 pool 的 checkpoint 曲线与最佳点 | 单一“全局最佳”结论 |
| `remote_model_summaries/opd5000_opd_online_run_summary.json` | report-supported summary | `2D670DE0707CD2C6A9D1D4C7EC109C86F0A3F8F87EDE5D6959367017231547CE` | 999,900 raw rows、936,192 expanded、skip 64,000、train loss、teacher/route counts、5000-step config | 原始 train log、checkpoint binary、optimizer state |
| `remote_model_summaries/coldstart500_opd_online_run_summary.json` | report-supported summary | `90FD5A0A5983FEB5673D44CA087F597F0EBCACFD63DF1305C37C297F213D5FC0` | teacher rollout、500-step coldstart 参数与 summary | coldstart-only 对照的 raw eval |
| `report/raw_holdout_eval_8models_20260525/evalset_summary.json` | local eval manifest | `200F7A8B00CDD989D4E8D19B6CD3EB5B47B75B87799394438169702F8BBF6485` | 10k quotas、训练阻断项、pool/format counts、8,251 unique images | 模型 predictions 本身 |
| `report/raw_holdout_eval_8models_20260525/dedupe_audit.json` | local audit | `2E102BB52B925ABA5AFE9E9111C98B3FA67F7032B266B1D08EBB1164A8FFB96D` | 0 fingerprint/source-line/prompt-answer-image duplicates、0 train image leakage | 任务是否足够代表真实部署 |
| `report/raw_holdout_eval_8models_20260525/raw_holdout_eval_8models_report.md` | committed report | `B4520BCA9B27CBDC8E9280E734A915972CDBBEBB213E685F33FD831EA6E0E78E` | 旧版 8-model 主评估、OPD final 表、评估协议与限制 | 与 OPD5000 ckpt5000 同 run 的证明 |

## 4. 五 expert 数据与路由设计

### 4.1 Expert mix

`build_expert_mixes_seed0_v2.py` 将 train 目标设为 800,000、eval 目标设为 20,000；以 image/video key 的稳定 hash 进入 5% candidate eval，再按 expert/source 配额抽样。五个 expert 的主分布是：

| Expert | 主数据域 | 设计意图 |
| --- | --- | --- |
| `general_reasoning_expert` | keepalive/general VQA | 保留通用视觉推理与文本能力 |
| `robopoint_expert` | RoboPoint point grounding | 强化 `<point>` 坐标输出 |
| `general_obj_expert` | RefCOCO/Flickr30K/VG object | 强化 object box grounding |
| `region_expert` | VG region | 强化 region description → box |
| `spatial_rel_expert` | VG relationship | 强化关系条件 grounding |

`spatial_rel_expert` 对 relation bucket 显式重采样：`on`、`in_inside`、`near_next_beside`、`under_below`、`above_over`、`front`、`behind`、`left_right`、`between`、`other_spatial`。每个输出样本保留 expert、split、source、source line、seed 和 relation bucket，这些字段支持后续追溯，但不证明专家已经学到可泛化的关系推理。

### 4.2 Student route metadata

`build_opd_student_v1.py` 将每个 expert 过滤后前 100,000 行标记为 `seen`，再构造：

- `domain`：约 600k，含 seen/unseen/hard 子类；
- `general`：约 250k，防止 student 退化为“凡问必坐标”；
- `boundary`：约 100k，覆盖 object/region/spatial/point/reasoning 边界；
- `format_conflict`：约 50k，覆盖 strict tag、错误格式诱导、prompt injection、坐标归一化。

最终 train summary 为 999,900 行：`box=555,537`、`text=293,050`、`point=151,313`。最终 eval 为 46,599 行，未为了凑满目标而用 train overlap 补齐。每行保留 `target_expert`、`candidate_experts`、`expected_format`、`sample_category/subtype`、`source_file/source_line`、`seen_by_expert_100k`、`fingerprint` 等字段。

这套 metadata 证明了“路由监督被写入数据”，不证明 student 在推理时必然选择正确 expert，也不证明 60/25/10/5 是全局最优比例。

## 5. Coldstart 与正式 OPD lineage

### 5.1 Coldstart-500

冷启动 summary 记录五教师 `preloaded_zero3`、teacher rollout、full-vocab distillation、`max_new_tokens=128`、`opd_prefix_loss_tokens=64`、veto beta 从 1 到 0（100 steps）等设置，student 起点为 `/data/msz/models/8b_base`。formal trainer 的 target 在 beta 大于 0 时由 `teacher_logits + beta * stopgrad(student_logits)` 构造，beta=0 后才退化为纯 \(D_{KL}(p_T\|p_S)\)。该阶段的可解释目的，是先让 student 获得稳定的 teacher 行为与输出协议，再进入 on-policy student rollout；但本地没有 coldstart-only raw-holdout 评估，不能把其增益单独量化。

### 5.2 OPD5000

正式 summary 记录：

- student 起点为 coldstart500 输出；五教师均以 `preloaded_zero3` 常驻并按 route 选择；
- `student` rollout 后，在同一 response 上执行 teacher forward；
- full-vocabulary \(D_{KL}(q_\beta\Vert p_S)\)，`max_new_tokens=64`，prefix loss token=64；beta归零后为 \(D_{KL}(p_T\Vert p_S)\)；
- `skip_expanded_samples=64,000`，保存 checkpoint 1000/2000/3000/4000/5000；
- 训练 summary 的 `train_loss=0.0306129573`，`last_opd_loss=0.0215270`，`last_opd_topk_overlap=0.7466`；
- 远端路径与 ZeRO-3 配置写入 manifest，但权重和完整 optimizer state 未同步到本地。

可用的面试链路：

```text
clean pools
  -> five expert mixes (image-hash split)
  -> student rows with target/candidate route metadata
  -> coldstart teacher rollout + full-vocab KL
  -> student rollout -> routed teacher forward -> OPD KL
  -> raw-holdout by-format / by-pool evaluation
```

“teacher 选择”在当前实现中是 route metadata 驱动的 teacher selection，不是一个已经被单独验证的 learned router；回答时应明确这一点。

## 6. Raw-holdout 协议与结果

### 6.1 评估集 gate

raw-holdout v1 为 10,000 行，pool quota 为：box 6,100、point 1,400、text 2,500；唯一图片 8,251。`source-line`、fingerprint、image+prompt+answer 三类重复均为 0，训练图片泄漏为 0。由于多个 VG/RefCOCO 标注天然共享图片，评估集有 1,168 个重复图片路径、2,917 行位于重复图片上；这不等于重复样本，不能误写成“图片完全唯一”。

### 6.2 OPD5000 checkpoint 曲线

| Checkpoint | Box IoU | Box Acc@0.5 | Point Hit@50 | Point Hit@100 | Text exact |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1000 | 0.4692 | 0.5139 | 0.7000 | 0.8357 | 0.8716 |
| 2000 | 0.4745 | 0.5192 | 0.7157 | 0.8550 | 0.8708 |
| 3000 | **0.4761** | 0.5233 | 0.7414 | 0.8629 | 0.8716 |
| 4000 | 0.4747 | 0.5207 | 0.7379 | 0.8650 | **0.8784** |
| 5000 | 0.4759 | **0.5238** | **0.7493** | **0.8729** | 0.8724 |

按 pool 的最佳点：semantic-nav box=2000；VG object=1000；VG region=3000；VG relationship=3000；point=5000；keepalive text=4000。`model_assets_eval_table.md` 的 readout 将 ckpt5000 作为综合默认候选，但同时保留 ckpt3000 在整体 box IoU / 高阈值 box 上的优势。

### 6.3 旧版 OPD final 与新版 OPD5000 分离

旧版 `raw_holdout_eval_8models_20260525` 主表记录的 `OPD final` 为：Box IoU 0.468、Box Acc@0.5 51.3%、Point Hit@100 84.1%、Text loose 87.4%、Bool acc 90.0%。它来自旧版 8-model 主评估与前一轮 checkpoint 曲线；新版 `opd5000_newexperts_20260601` 的 ckpt5000 是另一条 new-experts run，具有不同的训练 lineage、checkpoint 路径和后续评估表。

安全表述是“旧版 OPD final 在统一 8-model 矩阵中表现均衡；新版 OPD5000 ckpt5000 在 point/box/text 子集上有另一组结果”，而不是把两者拼成一条单调训练曲线。

## 7. Point protocol reconciliation

早期 raw-holdout point prompt 示例使用 `[(x1, y1), ...]`，而 gold 与 strict parser 要求 `<point>[[x1,y1],[x2,y2],...]</point>`。因此 base、instruct、Qwen-122B、Qwen3-35B-VL 的早期 strict=0 不能直接解释为几何能力=0。

| 模型 / 口径 | Point format | Hit@50 | Hit@100 | MinDist | 解释 |
| --- | ---: | ---: | ---: | ---: | --- |
| 8B base，original strict | 0 | 0 | 0 | — | 主要是协议不匹配 |
| 8B base，original lenient | — | 0.4450 | 0.5950 | 89.1 | 接受裸 `[(x,y)]` 的几何估计 |
| 8B instruct，original lenient | — | 0.3686 | 0.5536 | 99.5 | 同上，非 strict deployment 指标 |
| Qwen-122B，protocol-fixed strict | 0.9986 | 0.6771 | 0.8200 | 69.1 | 修正 prompt 后的 strict |
| Qwen3-35B-VL，protocol-fixed strict | 0.9857 | 0.6493 | 0.7871 | 75.9 | 修正 prompt 后的 strict |
| OPD5000 ckpt5000，original strict | 1.0000 | **0.7493** | **0.8729** | 51.7 | 训练期已对齐 `<point>` 协议 |

面试中必须说清三种口径：

1. `original strict` 衡量部署接口是否遵守既定 tag/坐标协议；
2. `protocol-fixed strict` 衡量在提示明确时的协议与几何能力；
3. `lenient geometry` 是兼容历史裸坐标格式的能力估计，不能与 strict deployment score 混报。

## 8. 结果边界与失败域

当前证据支持：OPD5000 把多域 grounding、point 输出和 keepalive text 统一到一个 8B student，并在同一 raw-holdout 上保持稳定格式；但不支持以下强结论：

- 不能说 OPD 单独带来全部 uplift：数据配比、五 expert specialization、route metadata、coldstart、student rollout、format alignment 和 on-policy KL 同时变化；
- 不能把 aggregate comparison summary 中的跨格式数字当作格式子集数字，应优先使用 by-format / by-pool 表；
- 不能说五个 expert 已各自通过独立 raw-holdout 最优验证；model asset table 明确写着尚未独立评估；
- 不能说 point strict=0 的 base/instruct“大模型不会 point grounding”；必须给 protocol caveat；
- 不能说 raw-holdout 证明了真实机器人闭环成功率；它是静态视觉 grounding/VQA 协议评估。

## 9. Ablation、lineage 与 ownership 队列

### P0

1. 把旧版 OPD final 与新版 OPD5000 的 base model、数据 manifest、训练脚本 SHA、checkpoint parent、scorer 版本和 run directory 收敛到单一 lineage manifest。
2. 同一 raw-holdout、同一 n、同一 scorer 复跑 base / SFT-only / coldstart-only / OPD5000，并保留 raw predictions 与逐样本 JSON。
3. 冻结 original strict、protocol-fixed strict、lenient geometry 三套 point scorer，记录 prompt hash。
4. 逐文件 ownership ledger 已建立；下一步补候选人确认，分别标记个人设计、个人实现、协作实现、历史 scaffold、工具辅助和仅读审计。

### P1

1. single-teacher vs five-teacher；no-synthetic vs synthetic；synthetic ratio；route metadata ablation；skip-expanded policy ablation。
2. 按 pool 输出 calibration、错误样例和 checkpoint selection rationale。
3. 绑定远端 checkpoint 可加载 smoke、optimizer state 和完整训练 log。

## 10. 面试安全表述

推荐 60 秒版本：

> 我把多域视觉数据先按 image-hash 做 train/eval 隔离，再为 reasoning、object、region、spatial relation 和 RoboPoint 训练五个 expert。student 数据额外写入 target/candidate expert、seen/unseen、boundary 和 format-conflict metadata。训练上先做五教师 coldstart，再做 student rollout，在同一 response 上让 route 对应的 teacher 做 full-vocabulary KL；教师是 metadata route 选择，不是单独训练的 learned router。OPD5000 在 10k raw-holdout 上的 ckpt5000 达到 Box Acc@0.5 0.5238、Point Hit@100 0.8729、Text exact 0.8724，但不同 pool 的最佳 checkpoint 不同。point 指标我会区分 original strict、protocol-fixed strict 和 lenient geometry，避免把输出协议不一致误判成模型没有定位能力。当前仍缺同协议 ablation、raw predictions 和逐文件 ownership ledger，所以我把结果称为组合路线证据，而不是 OPD 的单因果证明。

高压追问的诚实回答：

- “为什么不说 OPD 带来 11.5 个点提升？”——因为 base、数据、expert、coldstart、route 和 scorer/协议同时变化，当前没有同 suite 的单因素对照。
- “point strict=0 是不是模型不会？”——不是；早期 prompt 示例和 strict parser 不一致，protocol-fixed 后 Qwen-122B 达到 Hit@100=0.8200，OPD ckpt5000 原 strict 为 0.8729。
- “5000 是不是最佳 checkpoint？”——它是 point 和 Box Acc@0.5 的最佳点，但 box IoU、VG region/relation、keepalive text 的最佳点分散在 3000/2000/4000。
- “这些代码是不是你一个人写的？”——Git author 只能证明提交署名；我会按 ownership ledger 区分自己的设计、实现、协作和工具辅助范围。

## 11. References

- `C:\Users\mousongzhe\muxi\build_expert_mixes_seed0_v2.py`
- `C:\Users\mousongzhe\muxi\build_opd_student_v1.py`
- `C:\Users\mousongzhe\muxi\train_opd_online_vl.py`
- `C:\Users\mousongzhe\muxi\point\train_opd_online_vl.py`
- `C:\Users\mousongzhe\muxi\audit_opd_student_v1.py`
- `C:\Users\mousongzhe\muxi\REPORT.md`（Windows 下可能显示为 `report.md`）
- `C:\Users\mousongzhe\cv\interview_materials\vla\evidence\projects\opd_ownership_ledger.md`
- `C:\Users\mousongzhe\cv\interview_materials\vla\evidence\projects\opd_training_objective_lineage_gate.md`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\artifact_manifest.json`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\model_assets_eval_table.md`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\opd5000_ckpt_eval_by_format_table.md`
- `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\opd5000_ckpt_eval_by_pool_table.md`
- `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\evalset_summary.json`
- `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\dedupe_audit.json`
- `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\raw_holdout_eval_8models_report.md`
