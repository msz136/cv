# PROJ-OPENPIVLA：OpenPiVLA 项目原子题卡（Direct-Evidence Batch 2）

> 状态：`drafted / cards_4_of_4 / WARN`  
> 更新日期：2026-07-17  
> 当前题数：4 / 4  
> 覆盖范围：`PROJ-OPENPIVLA-009..012`  
> 难度：L2 2 题 / L3 2 题  
> 优先级：P0 3 题 / P1 1 题  
> 练习状态：全部 `unseen`  
> 前置证据：[Batch 2 evidence freeze](../sources/openpivla_batch2_evidence_freeze.html)；未闭合的 checkpoint、parser、axis/unit 和 ownership gate 不得升级为强结论。

## A. 稳定性与证据阶梯

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-009</b> · 为什么 local formal trainer 默认使用 eager attention？</summary>

**面试意图**：判断你能否把硬件/依赖兼容性处理讲成可验证的稳定性决策，而不是性能神话。

**30 秒回答**：历史 co-train 记录指向 Qwen3-VL flash-attention/position-id 失败；current formal CLI 默认 eager，并把它传给 Qwen loader。它证明兼容路径可执行，不证明吞吐或 benchmark 提升。

**机制展开（约 2 分钟）**：`formal_train.py` 的 `--attn-implementation` 默认值是 `eager`，随后传入 `Qwen3VLForConditionalGeneration.from_pretrained`。训练仍走 processor/chat template、padding label `-100`、`outputs.loss` 和 LoRA 更新。eager 的证据是“避开已记录失败点并让路径可诊断”；没有同 recipe、同硬件的 flash/eager profiler、显存、step time 或结果对照，不能说它更快、更准或带来 uplift。

**诊断 / 证据**：固定 recipe、seed、数据和 batch，分别跑 eager/flash smoke；记录 import、显存、step time、OOM/position-id traceback、loss 是否可比，并保存完整 stdout。当前只有 eager call graph 和报告转述，flash 对照与 profiler 缺失。

**项目挂钩**：可讲我在 MACA/C500 迁移中优先关闭已知 attention 崩溃面，再建立可复查的训练路径；不要把硬件适配写成算法创新。

**追问树**：为什么不直接修 flash？eager 会牺牲什么？如何证明不是数据变化造成稳定？同一 checkpoint 的输出是否应一致？

**危险答案**：说“eager 一定比 flash 更稳定/更快”，或把 `complete @ 100000` 直接归因于 eager 带来的 benchmark 提升。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-010</b> · smoke summary、formal report 和 raw log/checkpoint 的证据等级有什么区别？</summary>

**面试意图**：检查你能否把“工程链路跑通”“报告记录完成”和“权重可复核”拆成三件事。

**30 秒回答**：smoke JSON 只证明公开数据的 schema、shape 和 tiny step；formal report 记录三条 `complete @ 100000` 及远端路径；raw log、checkpoint、load smoke 不在本地，不能称模型已验证。

**机制展开（约 2 分钟）**：smoke summaries 标记 `private_data_deployed=false`，给出 public roots、batch shapes 和 tiny optimizer step，属于 local-direct。formal report 是本地 HTML 对历史/远端运行的转述，属于 report-supported；`/data/msz/...` 只是 remote-referenced 路径。只有能读取 immutable raw log、checkpoint/processor hash、load stdout、eval script 和 episode manifest，run 可从“报告记录”升级为 `checkpoint lineage verified`。

**诊断 / 证据**：每条 run 建 manifest，校验 trainer/config/base-model/data/checkpoint/log/eval 的 SHA；执行同一 checkpoint 的 load smoke，再重算一个最小 eval。当前 smoke 与 report 有，raw formal log、checkpoint binary 和 load smoke 仍缺。

**项目挂钩**：简历和面试可说“搭建 public smoke 与 formal training path”；应主动说明 completion 是 report-supported，不能说三条最终模型已加载并完成 benchmark。

**追问树**：为什么 smoke loss 不能代表 full run？报告里的 checkpoint path 算不算 checkpoint？怎样防止日志与权重错配？

**危险答案**：把 `tiny_train_step` 当作私有数据训练结果，或只凭 report 的 `complete` 行声称可 rollout。

**来源**：[1][4][5]　**练习状态**：unseen

</details>

## B. Lineage 与动作 shape

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>PROJ-OPENPIVLA-011</b> · 如何设计一份可审计的 OpenPiVLA checkpoint lineage manifest？</summary>

**面试意图**：看你是否能把训练、数据、权重和评估连接成可恢复链路，而不是只记一个 run id。

**30 秒回答**：lineage manifest 要把 run_id、trainer/config SHA、base model、adapter、checkpoint/processor hash、data manifest、raw log、load smoke 和 eval harness 绑成一条链；当前只是字段设计，hash 与 load evidence 仍缺。

**机制展开（约 2 分钟）**：最小链路是 `recipe/config → launch script → trainer → data manifest → base model/LoRA → checkpoint + processor → raw log → load smoke → eval harness → episode manifest`。每项记录 SHA、版本、路径、时间，并区分 public smoke、remote-referenced、archive-only。`complete @ 100000` 只填 `steps_reached`；缺 checkpoint/processor hash 或 load stdout，manifest 保持 `lineage-open`，不能把路径当权重证明。

**诊断 / 证据**：为三条 run 生成 manifest，先检查脚本/配置/源代码 SHA，再核对 checkpoint 目录、adapter config、processor 文件、log step 和 eval 输入是否一一对应；最后运行只读 load smoke。当前模板已写入 Batch 2 审计，但真实 checkpoint/processor/raw log 字段仍为 missing。

**项目挂钩**：这是我把训练迁移从“能跑”提升到“能复查”的工程抓手；个人 ownership 仍需另做 per-file ledger，不能由 manifest 自动推断。

**追问树**：为什么 processor 也要 hash？base model 没有 binary 怎么记录？如何处理远端不可访问的 artifact？

**危险答案**：只保存 `run_id` 和最终 step，或把 manifest 模板写成已经完成的 checkpoint 证据。

**来源**：[1][3][6][7]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-012</b> · `H=15,D=72` 与 formal formatter 的 `limit=16` 冲突时，应该怎样解释？</summary>

**面试意图**：检查你能否发现 shape 看似一致、语义却未闭合的动作表示风险。

**30 秒回答**：recipe 是 `H=15,D=72`，formatter 每步只保留 16 个数；probe 丢 840/1080 positions，formal package 又没有 action parser。Python JSON 只恢复 `15×16` 前缀，不是 controller round-trip。

**机制展开（约 2 分钟）**：令 \(\mathbf{A}\in\mathbb{R}^{H\times D}\)，其中 `H=15,D=72`。formal formatter 只把每行前 16 个数写入 JSON，再重复尾行补满 horizon；`dumps→loads` 只能恢复 lossy prefix。empty window/row 还会产生 `15×1/15×0`，NaN 未被拒绝。没有 strict parser、valid mask、axis/unit、normalizer 与 controller trace，shape 和执行语义都未闭合。

**诊断 / 证据**：已用 72D sentinel 冻结 retained/dropped positions、tail-repeat、empty/ragged/NaN 与 collator label mask；还要记录 immutable Qwen generation、strict parser、normalizer/denormalizer、axis/unit 和 controller 输入，做逐维 round-trip。项目中 7D/4-step official WebSocket eval 使用 `pi0_aloha_sim` checkpoint，是平行 lineage，不能替 formal Qwen 补证据。

**项目挂钩**：安全表达是“我用 probe 量化了 72→16 的 77.78% schema loss，并确认 formal text route 缺 parser/controller；当前这是可信 bad case，不是已修复上线结果”。

**追问树**：为什么 smoke 要 pad/repeat？`limit=16` 是临时占位还是正式设计？如何判断截断丢的是哪类关节？loss 下降能否证明 shape 正确？

**危险答案**：说“配置写 72 所以模型已经预测 72 维控制量”，或把 public smoke 的重复动作当成真实 DROID 未来窗口。

**来源**：[1][2][4][6][9]　**练习状态**：unseen

</details>

## 参考来源

1. [OpenPiVLA Batch 2 evidence freeze](../sources/openpivla_batch2_evidence_freeze.html)：eager、evidence ladder、lineage、`H=15,D=72`/`limit=16` 冲突的冻结审计。
2. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py`：eager 参数、JSON formatter、Qwen `outputs.loss`，SHA `51b67d3e04496e68076bf6461506141ebcddf9a82e6c30af1fdc0f1f2ccc6f94`。
3. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\artifacts\vla_formal_reproduction_report_20260617.html`：report-supported formal completion 与 attention 边界，SHA `d74126a3896f68ad44b75c7a88f1b7b9a90cb55df0c6c6beb90a5748e9e8e074`。
4. 本地 `artifacts/vla_train_repro/*_smoke_summary.json`：public smoke shape、tiny train step 与 `private_data_deployed=false`。
5. 本地三份 `repro_train/configs/*.yaml` 与 `recipes.py`：run mode、shape 字段、历史 metadata，SHA `397d1b384a2bd93d9dc81b7003e6ab7bfac3fc458ea04008197c3f503f9d780e`。
6. 本地 `data.py`：public smoke 的 `(H,D)` padding/repeat 逻辑，SHA `32c6aa76929d941c4832d2eb4c2550527d3e607e31c2a9f5507cc76eeedbc2ec`。
7. [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：项目 claim、证据等级与 ownership 边界。
8. [OpenPiVLA 项目页](../../03_openpivla_action_modeling.html)：安全口述口径与项目 hook。
9. [OpenPiVLA Action JSON Parser / Round-trip Artifact Gate](../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html)：deterministic probes、full-sequence CE 与 parallel official-eval lineage。
