# PROJ-OPENPIVLA：OpenPiVLA 项目原子题卡（Direct-Evidence Batch 1）

> 状态：`drafted / cards_8_of_8 / WARN`  
> 更新日期：2026-07-21  
> 当前题数：8 / 8  
> 覆盖范围：`PROJ-OPENPIVLA-001..008`  
> 难度：L2 4 题 / L3 4 题  
> 优先级：P0 6 题 / P1 2 题  
> 练习状态：全部 `unseen`  
> 使用方式：先闭卷回答 30 秒，再展开代码证据与缺口；未真实口述前不得改为 `pass/strong`。

## A. Formal trainer 与动作监督

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-001</b> · 从代码证据看，formal trainer 的模型、参数更新和 loss 是什么？</summary>

**面试意图**：确认你能从源码说明“实现了什么”，又不把实现路径升级成 benchmark 结果。

**30 秒回答**：`formal_train.py` 用 Qwen3-VL + LoRA；collator 复制全部 `input_ids`，只屏蔽 padding，所以优化 full-chat causal CE，不是 assistant-only CE。代码证明 trainer，不证明 checkpoint 效果。

**机制展开（约 2 分钟）**：模型加载、LoRA 配置、`model(**batch)`、梯度累积和 checkpoint 保存都在同一 formal trainer 中；labels 由 `input_ids` 克隆并仅把 attention padding 置为 `-100`，没有 assistant-span mask。因此 user prompt、chat wrapper 与 assistant JSON/QA 的非 padding token 都进入 CE；这不是原始 Pi0 action expert 的连续 flow-matching loss。面试时还要把“代码可读”与“checkpoint 可加载/指标可复算”分开。

**诊断 / 证据**：打印 model class、LoRA target modules、trainable/total params；用一个 batch 检查 `input_ids`、`labels`、padding mask 和 `outputs.loss`；再用 immutable checkpoint 做 load smoke。当前前两层有本地源码/报告，最后一层仍缺 formal checkpoint。

**项目挂钩**：可把个人贡献落在 trainer、collator、recipe 和稳定性路径，但须另做 ownership ledger；不能只凭 Git author 认领所有历史代码。

**追问树**：为什么不用全参训练？`-100` 如何影响 CE？LoRA checkpoint 如何和 base model 合并？为什么这不等于 flow matching？

**危险答案**：说“LoRA trainer 就是原始 OpenPI action expert 的等价实现”，或说代码里有 trainer 就证明 97.4% 已被该模型复现。

**来源**：[1][2][3][4][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-002</b> · local action route 如何把连续 action window 变成 Qwen supervision？</summary>

**面试意图**：检查你是否能讲清 formatter、chat template、label mask 和执行端缺口。

**30 秒回答**：DROID 读取未来动作窗口，按 horizon 截断或补齐，序列化为 `{"actions": [...]}` assistant 文本；Qwen processor/chat template 转成 token，collator 屏蔽 padding label。这是 JSON/causal-CE 路线，不是已证明的 FAST DCT/BPE。

**机制展开（约 2 分钟）**：`DroidActionTextDataset` 按 episode 收集 action，每行最多保留 16 个数并重复尾行，再用 `json.dumps` 生成 assistant content。collator 复制全部 `input_ids`，只屏蔽 padding。72D probe 只能恢复 `15×16` prefix；formal package 没有 Qwen generation/action parser，official WebSocket eval 又属于另一 checkpoint lineage。因此这里只证明训练文本构造，不证明 formal Qwen closed-loop rollout。

**诊断 / 证据**：现有 sentinel 已确认 72→16 丢 840/1080 positions、tail-repeat 与 empty/NaN schema 风险；collator probe 确认只有 padding 被 mask。下一步必须用 immutable Qwen checkpoint 做 tokenizer→generate→strict parser→normalizer→controller round-trip。若只看 loss 下降，不能证明动作单位、轴序和夹爪语义正确。

**项目挂钩**：简历可写“assistant JSON content + full-chat causal-CE formal path，并定位 lossy serializer/parser gap”，不能写“复用了 FAST tokenizer”“assistant-only loss”或“已证明 action expert 等价”。

**追问树**：为什么用 JSON？数值精度怎么控制？parser 在哪里？D=72 每一维是什么？

**危险答案**：看到 recipe 里的 `fast_tokenizer` 字段，就说 local action 已经过 DCT/BPE；或把 JSON 字符串直接称为机器人控制量。

**来源**：[1][2][5][6][19]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-003</b> · 为什么不能把 `fast_tokenizer` 字段说成 local FAST DCT/BPE 实现？</summary>

**面试意图**：检查你能否用 call graph 而不是字段名判断真实实现。

**30 秒回答**：`recipes.py` 有 `fast_tokenizer` 字段，但 trainer 调用 Qwen processor、JSON assistant text 和 `outputs.loss`；未见 FAST processor、DCT/BPE 或 roundtrip。因此 local route 只能称 JSON/causal-CE。

**机制展开（约 2 分钟）**：证据审计要从 recipe 字段追到运行时调用：配置声明不等于执行。当前 call graph 是 DROID parquet → action JSON → chat template → Qwen processor → causal CE；FAST 的公开 call graph 则包含 normalization、DCT、量化/BPE、decode/IDCT。两条路径都能把动作纳入序列模型，但 token 语义、损失和反解析合同不同，不能在简历或口述中合并。

**诊断 / 证据**：静态检查是否 import/call frozen FAST processor；用一个 action window 做两条 encode/decode roundtrip；比较 token length、重建误差和 parser 输出。当前 local FAST call/roundtrip 证据缺失，应保持 `representation-conflict` 风险。

**项目挂钩**：这道题是 OpenPiVLA 的高频防穿帮题；主动区分 upstream FAST、历史 action expert 和本地 Qwen formal path，反而能体现证据意识。

**追问树**：如果后续接入 FAST，哪些文件和测试必须变化？JSON/CE 为什么可能更容易先跑通？两条 loss 能否比较数值大小？

**危险答案**：说“配置里写 fast_tokenizer，所以已经实现 FAST”，或说两条 loss 只差 tokenizer。

**来源**：[2][3][7][8]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-004</b> · VLA-only、VLM-only、co-train 三类 recipe 的数据流区别是什么？</summary>

**面试意图**：确认你能把 run mode 映射到数据集、采样和训练目标，而不是只背三个名字。

**30 秒回答**：VLA-only 只启用 DROID action-text dataset；VLM-only 只启用 MindCube QA；co-train 同时构造两者并由 `AlternatingDataset` 交替采样。三类 recipe/config 和 public smoke shape 可直接核验，但不自动证明私有数据结果或某个模式更优。

**机制展开（约 2 分钟）**：`build_dataset` 根据 recipe mode 选择 DROID/MindCube iterable dataset，并设置各自权重；DROID 样本含机器人动作 JSON 目标，MindCube 样本含视觉语言答案，co-train 将它们送进同一 Qwen causal CE。配置中的 private roots 与 public smoke roots 要分开：smoke 只验证 schema、batch shape 和 tiny optimizer step，不能替代历史私有语料或 benchmark。

**诊断 / 证据**：打印每个 mode 的 dataset source、sample count、mixture schedule、batch fields 和 labels mask；对 co-train 做单源/双源比例消融。若缺完整 run ledger，不能从 loss 绝对值推断三类模式的性能排序。

**项目挂钩**：可讲 recipe 设计和数据 contract；“三条都完成并保存可加载 checkpoint”属于 report-supported/remote-referenced，需单独补证据。

**追问树**：co-train 如何防止 QA 淹没 action？private/public 数据差异？为什么保留 VLM-only？

**危险答案**：把 public smoke 当作私有 DROID/MindCube 的等价替代，或把三种 mode 当作三种模型架构创新。

**来源**：[2][3][4][9]　**练习状态**：unseen

</details>

## B. Formal completion、归档结果与评估边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>PROJ-OPENPIVLA-005</b> · 三条 100k formal run 应该如何分层陈述？</summary>

**面试意图**：训练你区分源码、报告、远端日志和 checkpoint load smoke 四种证据强度。

**30 秒回答**：scripts/config/report 是 direct；report 记三条 `complete @ 100000`，属 report-supported；远端 log/checkpoint 为路径引用，属 remote-referenced。缺 raw log、checkpoint SHA、load smoke，不能称 checkpoint 已验证。

**机制展开（约 2 分钟）**：先列证据链：recipe/config → launch command → formal log → checkpoint hash → load smoke → eval manifest。当前已有前两项和 committed report，后两项只保留 `/data/msz/openpivla/...` 路径引用。报告还说明 formal JSON/CE/LoRA 与原 flow/action expert 不等价，因此“跑到 100k”只能说明该 formal execution path 被记录为完成，不能说明复现了原项目性能。

**诊断 / 证据**：为每个 run 建 immutable manifest，记录脚本 SHA、config SHA、steps reached、checkpoint SHA、base model、LoRA adapter、load command 和 stdout；再用同一 checkpoint 做 eval smoke。当前 gate 未关闭。

**项目挂钩**：简历只写“搭建/迁移 formal training path”；面试可说“报告记录 completion，raw checkpoint 待核”，不要说“我已加载三条最终模型并验证 benchmark”。

**追问树**：为什么 report-supported 不等于 verified？保存点如何生成？第三条 batch 参数为何需要看远端脚本？

**危险答案**：只凭报告中的 `complete` 行就声称三条 checkpoint 已加载、可 rollout、可复现。

**来源**：[3][4][10][11]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-006</b> · `224_h10_40000` 的 97.4% 能否与 official 96.85 比较？</summary>

**面试意图**：检查你是否会在数字很诱人时主动冻结 protocol tuple。

**30 秒回答**：不能下“高于 official”的结论。97.4% 只有 committed report 汇总，属 `archive-summary-only`；official 96.85 是 frozen README 事实，但 checkpoint、trial/seed、init state、harness、controller、raw episodes 尚未对齐。

**机制展开（约 2 分钟）**：可比 benchmark 至少要绑定 suite/task version、checkpoint/base model、image preprocessing、normalizer、H/K、controller、trial/seed/init state、success predicate、metric code 和 aggregation。当前报告确实有四套件数字，但没有 raw summary、episodes 和 archive→formal lineage；因此要把“报告里出现的数字”“官方 baseline”“统计可比性”分成三层，不能用 0.55pp 差值做 uplift 结论。

**诊断 / 证据**：收集 archive checkpoint SHA、每 suite/task/seed episode records、eval script/config、norm stats 和 metric recomputation；用 protocol diff 表逐字段对齐，再考虑多 seed 或置信区间。

**项目挂钩**：这是简历与项目页的高压边界题；安全回答不是回避数字，而是说明数字目前处于什么证据等级、下一步怎样升级。

**追问树**：official 96.85 的 suite order 和 trials？97.4 是哪条模型链？单点差是否有统计意义？

**危险答案**：说“97.4 比 96.85 高，所以我超过了官方”，或把归档表格自动归因给 current Qwen formal。

**来源**：[3][12][13][14]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPENPIVLA-007</b> · local ALOHA/LIBERO/replay artifacts 分别证明什么？</summary>

**面试意图**：防止把 official baseline rollout、诊断视频和 formal Qwen benchmark 混成一个结果。

**30 秒回答**：ALOHA `pi0_aloha_sim` 为 `2/3`，多视角 `1/2`；LIBERO `pi05_libero` task-0 为 `0/1`。server log 确认 Orbax restore、norm stats 与 client connect；replay/L1 仅诊断，不证明 formal Qwen 或 97.4。

**机制展开（约 2 分钟）**：ALOHA 3 集 `2/3`、六相机 2 集 `1/2`；LIBERO task 0 的 model/no-op 各 70 步、均 `0.0` reward/false success。server log 记录 Orbax 从 `pi05_libero/params` 恢复约 6.2 GiB、17 秒完成，从 checkpoint assets 加载 norm stats，并在 8399 接受 localhost client；script 固定 image/wrist/state/prompt 与 action chunk 前 `K×7D`。仍缺逐文件 SHA、exact argv/run UUID、独立 scorer 和 formal Qwen lineage。

**诊断 / 证据**：summary 字段只描述结果，不能证明 server 真正加载了什么；checkpoint 绑定必须看 restore log。ALOHA LeRobot action eval 的 4×50×14 mean L1 `0.033071` 只作离线 action-level diagnostic。当前 load/serve/connect 已闭合到 `PASS WITH WARNING`，下一步生成 params/norm-stats 逐文件 SHA，并保存 shared run ID、完整 argv、request trace 与 scorer revision。

**项目挂钩**：可讲“我用 restore/normalizer/connect log 审计部署闭环”；在 ownership 未确认前仍不把脚本实现或 official checkpoint 训练归到个人名下。

**追问树**：为什么 client summary 的 checkpoint 字段不够？如何证明 client 连的是同一 server？0-success 排除了哪些原因、还没排除哪些？

**危险答案**：把 replay video 当作 Bridge/Fractal 任务成功，或把 official `pi05_libero` rollout 说成自己的 Qwen 模型结果。

**来源**：[3][10][11][15][20][21][22]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>PROJ-OPENPIVLA-008</b> · 如何回答 OpenPiVLA 的个人 ownership？</summary>

**面试意图**：区分 Git authorship、代码事实、个人贡献和工具/协作边界。

**30 秒回答**：`c4469eb` 只证明候选账号提交了包含 360 个 OpenPiVLA paths 的初始快照。13-row ledger 已区分上游、本地文件、验证和待确认角色；没有逐项回答前，不能把 Git author 当作独立原创证明。

**机制展开（约 2 分钟）**：Git 审计发现 OpenPiVLA 的 360 paths 一次进入 root snapshot，关键文件没有更早 diff；frozen OpenPI tree 又没有 `vla_qwen3_repro`，只能证明它是相对该上游的本地新增路径，不能证明由谁独立编写。ledger 把 trainer、JSON/collator、recipe、smoke、MACA、eval、report 与 upstream 分成 13 行，并要求逐项填写亲手、协作、工具辅助或上游。设计/修复还需 before/after、决策记录和运行验收。

**诊断 / 证据**：ledger 结构已完成，当前 gate 是候选人回答 8 个角色问题，并为关键函数补 pre-snapshot 来源、diff、命令或 review；所有题卡仍 unseen。

**项目挂钩**：未确认前说“项目快照包含 Qwen/recipe/eval contract”；确认后只认领 ledger 中自己的模块，不说“整个 OpenPiVLA 都是我写的”。

**追问树**：哪一段代码是你亲手改的？为什么选择 JSON/CE/eager？工具生成代码如何审查？没有 commit diff 怎么证明贡献？

**危险答案**：把 Git author 等同于所有代码的独立原创证明，或把上游 FAST/OpenPI 贡献算成自己的算法创新。

**来源**：[3][16][17][18]　**练习状态**：unseen

</details>

## 参考来源

1. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py`：Qwen3-VL、LoRA、JSON dataset、collator 和训练循环。
2. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\recipes.py`：三类 recipe、shape 字段与 formal 计划。
3. 本地 [OpenPiVLA Claim–Evidence Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：local-direct / report-supported / archive-summary-only / missing 分层。
4. 本地 `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\data.py`：public smoke data contract 与 batch shape。
5. 本地 `formal_train.py` 中的 `DroidActionTextDataset`：action window → compact JSON assistant text。
6. 本地 `formal_train.py` 中的 `Qwen3VLCollator`：chat template、processor 和 padding label mask。
7. Physical Intelligence, [FAST](https://arxiv.org/abs/2501.09747)：上游 DCT/量化/BPE 机制；不证明 local Qwen route 使用 FAST。
8. 本地 [formal report](C:/Users/mousongzhe/Project/openpivla_deployment/artifacts/vla_formal_reproduction_report_20260617.html)：三条 report-supported formal run 与 `224_h10_40000` archive summary。
9. 本地三份 `repro_train/configs/*.yaml` 与 `run_formal_*.sh`：recipe/config/launch evidence。
10. 本地 [DEPLOYMENT.md](C:/Users/mousongzhe/Project/openpivla_deployment/DEPLOYMENT.md)：remote-referenced logs/checkpoints、ALOHA/LIBERO/replay 边界。
11. 本地 [official LIBERO launcher](C:/Users/mousongzhe/Project/openpivla_run_libero_official_eval.sh)：official policy server/client eval harness。
12. Frozen OpenPI `examples/libero/README.md`：official `pi05_libero` 96.85 baseline；见 inventory frozen source SHA。
13. 本地 `224_h10_40000` report summary：97.4% archive-summary-only；不含 raw episode bundle。
14. 本地 `openpivla_deployment` rollout artifacts：ALOHA/LIBERO true rollout、replay-only、action adapter 和 L1 diagnostics。
15. 本地 `Project` Git commit `c4469eb8ec4bb879bdb7d12cf9a303c8264a41ea`：粗粒度 authorship signal，不等于 ownership ledger。
16. 本地 [OpenPiVLA 项目页](../../03_openpivla_action_modeling.html)：安全口述、项目 hook 与高压边界。
17. 本地 [resume restructure plan](../../../output/resume_restructure_plan.md)：当前安全简历口径和禁写规则。
18. 本地 [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)：13 个文件/决策、Git/upstream 边界与 8 项候选人确认问题。
19. 本地 [OpenPiVLA Action JSON Parser / Round-trip Artifact Gate](../sources/openpivla_action_json_parser_roundtrip_artifact_gate.html)：72→16 loss、full-sequence CE、parser absence 与 official WebSocket parallel lineage。
20. 本地 [OpenPiVLA Runtime Rollout Artifact Gate](../sources/openpivla_runtime_rollout_artifact_gate.html)：冻结 ALOHA/LIBERO summary SHA、true-physics rollout、视频/轨迹清单与 fine-tune/benchmark/ownership 边界。
21. 本地 [OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate](../sources/openpivla_libero_checkpoint_load_lineage_gate.html)：冻结 Orbax restore、checkpoint norm stats、8399 listen/localhost connect 与 hashed rollout contract；binary manifest、exact argv/run UUID 和 private fine-tune lineage 仍未闭合。
22. 本地 [OpenPiVLA ALOHA Action-Level Eval Load Gate](../sources/openpivla_aloha_action_eval_load_gate.html)：冻结 `pi0_aloha_sim` restore/norm-stats/8020 connection 与 4×50×14 offline action L1；不支持 task success 或 fine-tune claim。
