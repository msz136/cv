# PROJ-WAM：Cosmos Policy / WAM 项目原子题卡（Training Failure + Diagnostic + Ownership Batch 1）

> 状态：`drafted / cards_4_of_4 / WARN`  
> 更新日期：2026-07-21  
> 当前题数：4 / 4  
> 覆盖范围：`PROJ-WAM-001..004`  
> 难度：L3 4 题  
> 优先级：P0 4 题  
> 练习状态：`unseen`  
> 前置证据：[Cosmos Policy 1 Epoch Evidence Freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)、[WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html)、[WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)。

## A. 1 epoch gate 与两类训练系统失败

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-WAM-001</b> · 你是否完成了 Cosmos Policy 1 epoch finetune？如何把两次中断讲成可信项目经历？</summary>

**面试意图**：判断你是否有明确的训练完成门槛，能否从 exit code、资源证据和 error stack 定位 first divergence，并避免把中间 loss、空目录或其他 run 的 baseline 拼成结果。

**30 秒回答**：`9907`-step、8卡/batch128 gate未完成1 epoch：step1903因`cycle(dataloader)`缓存触发cgroup CPU OOM；改iterator后5-step smoke通过，但step1500又因DeepSpeed/Cosmos `state_dict`签名不兼容保存失败，因而无checkpoint/eval。

**机制展开（约 2 分钟）**：完成定义是 `9907` steps→保存→新进程加载→同协议 eval。save-2k run 在 step 1903 后 `EXIT=247`、rank `-9`，无 GPU OOM 栈且 cgroup 证据指向 CPU memory；`cycle` 会缓存已 yield batch。改为普通 iterator、耗尽后重建，8 卡 5-step smoke `EXIT=0`。正式 run 到 step 1500 时，DeepSpeed 传 `destination/prefix/keep_vars`，Cosmos override 不接收，目录无可用权重。因此只认领合同、根因和 smoke，不认领 epoch 结果。

**诊断 / 证据**：先展示 `run_contract.json` 的 8×16、global batch 128 和 `max_steps=9907`，再把两条 run 分开：step 1900 loss `0.2945` 是中断前快照；`step_001500` 是空目录，不是 checkpoint。下一步让 `state_dict` 兼容并正确转发 PyTorch 标准签名，做 1-step train→save→退出→新进程 load smoke，核对参数 key/shape、optimizer/scheduler、global step、文件 SHA 和固定输入 forward parity；通过后才重跑长任务。

**项目挂钩**：可讲 C1/C2 的 run contract、数据统计、cgroup OOM 分析、no-cycle smoke 和保存接口定位。CoffeePressButton manifest、300-step trace、失败视频、PSNR/SSIM proxy 是另一层诊断 bundle；它们不能补出本轮 checkpoint 或 success。C3 禁止讲完整 1 epoch、final loss、closed-loop success、uplift 与官方 baseline ownership。

**追问树**：`cycle(dataloader)` 为什么缓存 batch？如何证明 cgroup CPU OOM 而非 GPU OOM？`EXIT=247` 与 rank `-9` 是什么关系？为什么 5-step smoke 不等于训练成功？`state_dict(destination=...)` 兼容层如何设计？save/load smoke 验收什么？`84/118` 为什么不是本轮结果？

**危险答案**：说“step 1900 就算完成 1 epoch”“loss `0.2945` 是 final”“5-step smoke 证明训练成功”“有 `step_001500` 目录就是 checkpoint”或“`84/118` 是我的 1 epoch eval”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## B. Checkpoint save/load gate 与 base-load 边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-WAM-003</b> · base_load_summary 有 715 个 key，为什么仍不能说 checkpoint 可加载？请给出 save/load gate 的最低验收协议。</summary>

**面试意图**：判断你是否区分 base model 初始化、短训练 smoke、长跑、checkpoint save、fresh-process reload 与同 checkpoint eval，能否把“key 对齐”与“训练产物可复现”拆开。

**30 秒回答**：715-key base-load 与1/5-step smoke均通过，但save2k为rank `-9`/`EXIT=247`，save1500为`state_dict(destination=...)` TypeError/`EXIT=1`；归档无checkpoint binary，所以不能称checkpoint可加载。

**机制展开（约 2 分钟）**：完成门是 `base load → smoke → 9907 steps → save → 销毁进程 → fresh load → fixed-input parity → eval`。715 keys 只代表 HF base snapshot；smoke 没覆盖保存。save2k 是长跑资源线，save1500 是 DeepSpeed 传标准 `destination/prefix/keep_vars` 而 Cosmos override 不接收的 API first divergence。修复后应在配置下跑 1 step save，退出并新进程 load，核对 shard、optimizer/scheduler、global step、文件 SHA 与固定 batch 输出，再重跑 formal gate。

**诊断 / 证据**：展示 [Checkpoint Save-Load Gate P0 Audit](../evidence/projects/cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html) 的 65-file inventory、13 份 base-load summary、`smoke5_exit_code=0`、save2k `EXIT=247`、save1500 TypeError 与 checkpoint-like binary `0`。不要把 HF cache snapshot、`step_001500` 目录、early loss 或 official `84/118` 当成 produced checkpoint 证据。

**项目挂钩**：可讲你如何定义验收门、拆分 run family、定位保存接口和设计 fresh-process parity；不能讲“1 epoch 已完成”“checkpoint 已保存”“loss 下降带来 closed-loop uplift”或从远端路径推断 ownership。

**追问树**：715 keys 检查的对象到底是什么？为什么 5-step smoke 不覆盖 save？`EXIT=247` 与 `EXIT=1` 是否同一个根因？`state_dict` 兼容层哪些参数必须转发？为什么必须销毁进程再 load？除了模型权重，还要校验哪些 DeepSpeed 状态？

**危险答案**：说“missing=0 就是 checkpoint 可加载”“有 step 目录就是权重”“5-step smoke 证明 epoch 成功”“把 save2k OOM 和 save1500 TypeError 合成一个错误”或“官方 baseline 就是我的训练结果”。

**来源**：[1][3][7]　**练习状态**：unseen

</details>

## C. 上游、运行角色、诊断与个人 ownership

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-WAM-002</b> · Cosmos/WAM 哪些部分能说是你做的？如何区分 upstream、训练排障、远端运行和个人 ownership？</summary>

**面试意图**：判断你能否把上游机制、Project 快照、训练系统改动、operator/reviewer、诊断 artifact 和结果归属拆开，而不是把 Git author、远端目录或报告当作全部个人贡献。

**30 秒回答**：Predict2/WAM architecture是upstream；本地能核验8卡`9907`合同、两类失败和CoffeePressButton诊断。个人贡献必须绑定文件/函数/命令/验收和角色；Git author、远端路径、官方`84/118`都不能自动归我。

**机制展开（约 2 分钟）**：分五层：上游 latent slot/mask/routing；Project 的训练、动作与 rollout 快照；step 1903 cgroup OOM、no-cycle smoke 和 step 1500 保存签名错误；CoffeePressButton manifest/trace/video/proxy；最后才是个人角色。前三层能证明项目与运行发生过，不能证明逐行原创；诊断 bundle 也不证明 benchmark。现场只认领本人能解释的 diff、命令和验收，远端 8 卡运行、review、协作与工具辅助分别记录。

**诊断 / 证据**：用 ownership ledger 逐项回答：谁设定 8×16/`9907` 合同，谁修改 iterator，谁发起远端 run，谁读取 cgroup/launcher 证据，谁定位 `state_dict` stack，谁验收 smoke。升级为“我负责并取得训练结果”还需要 candidate-confirmed diff、operator/reviewer 记录、完整 `9907`-step log、immutable checkpoint/normalizer/config 和 protocol-complete episode/scorer bundle。

**项目挂钩**：当前安全表达是“参与或负责训练协议迁移、系统失败定位和证据审计”，具体动词由候选人逐文件确认。CoffeePressButton 的 7D→12D trace geometry、offline visual proxy 与 path bridge可讲诊断层级；不能把 policy RMSE 当 action-label loss、把单 episode `success=false` 当 benchmark、把 path equality 当 binary verification。

**追问树**：哪个函数是你亲手改的？`cycle` 修复由谁提出、实现和验收？谁运行远端 8 卡？保存接口方案是否已落地？谁是 reviewer？CoffeePressButton 的 checkpoint binary 在哪？Codex/协作者做了什么？若没有完整 checkpoint，为什么简历能写 finetune？

**危险答案**：说“Git author 证明所有代码是我写的”“WAM architecture 是我设计的”“OOM 修了就等于 1 epoch 成功”“官方 `84/118` 是我的结果”或“远端目录存在就等于 checkpoint 归我”。

**来源**：[1][4][5][6]　**练习状态**：unseen

</details>

## D. Eval run provenance 与 raw / trusted denominator

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-WAM-004</b> · Cosmos Policy eval 中 full10k 的 raw 2/120、trusted 0/118 与 official-HF 的 raw 86/120、trusted 84/118 如何解释？为什么不能说本地训练达到 71.19%？</summary>

**面试意图**：判断你能否按 checkpoint lineage、run family、scorer 与 invalid policy 管理结果，而不是把同一评估环境下的数字错误 join 成个人模型 uplift。

**30 秒回答**：独立full10k trained run为raw`2/120`、trusted`0/118`；official-HF另一checkpoint为raw`86/120`、trusted`84/118=71.19%`。我能讲harness和重算，不能把官方成绩写成本地训练；8-GPU`9907`仍未完成。

**机制展开（约 2 分钟）**：先冻结 join key：checkpoint/revision、stats/T5、task/init、seed、denoise/chunk、controller、predicate、invalid policy 和 denominator。full10k 是单卡 batch 1 的独立训练线，不能与 8-GPU `9907` gate 合并；其 24×5 只有两个 length=1 immediate success，所以报告 raw `2/120` 与 trusted `0/118`。official-HF 使用另一模型 path，重算为 `86/120` 和 `84/118`；缺 matched checkpoint、scorer 与 raw episode bundle时不能计算 uplift。

**诊断 / 证据**：full10k `eval_summary_conservative.json` 明确记录 `raw_successes=2`、artifact=2、trusted=0、eligible=118；official baseline audit 从 24 个 task log 重算 `86/120`，排除同类两个 CoffeeServeMug length=1 后为 `84/118`，并验证 24 个 action-debug 文件共 2692 行、shape `32×7`、finite。`length<5` 是当前本地审计规则，不应冒充 RoboCasa 官方统一定义；checkpoint binary/hash、完整 episode JSONL 和 scorer version 仍缺。

**项目挂钩**：可讲我如何把 trained、official baseline、8-GPU gate、1k ablation 与 TurnOffMicrowave 单 episode分开管理，复算 raw/trusted denominator 并保留 invalid policy；不可说“本地训练达到 71.19%”“full10k 比 1 epoch 提升”“官方 baseline 是我的模型成绩”。

**追问树**：为什么 denominator 从 120 变 118？排除 invalid episode 后为什么不是 `84/120`？`exit_code=0` 是否等于 success？如何证明两个 eval 使用相同 scorer？checkpoint path 为什么不足以做 paired comparison？若要报告 uplift，最小 matched bundle 是什么？

**危险答案**：说“71.19% 是我的 full10k 成绩”“两个 length=1 success 证明 trained model 有能力”“raw 与 trusted 选更高的报”“同为 24×5 就能直接比”或“官方 checkpoint path 等于我持有并验证了权重”。

**来源**：[1][3][8][9][10]　**练习状态**：unseen

</details>

## 参考来源

1. [Cosmos Policy 1 Epoch Evidence Freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)：8 卡 run contract、`9907`-step gate、step 1903 cgroup OOM、no-cycle smoke、step 1500 保存签名失败与结果边界。
2. [Cosmos Policy / WAM Claim-to-Code Audit](../sources/vol_04_cosmos_policy_wam_claim_to_code.html)：upstream latent slot、mask/routing 与公开 contract。
3. [PROJ-WAM-001 Evidence-Bounded Model Answer](../practice/wam_oral_model_answer.html)：五个高压问题的危险/可过/强三档回答与 save/load smoke。
4. [Cosmos / WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)：claim 等级、C0–C3 证据门与结果升级条件。
5. [Cosmos / WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html)：per-file/per-decision ownership、operator/reviewer 与工具边界。
6. [WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)、[Action-Trace Diagnostic](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html)、[Future-Metric Diagnostic](../evidence/projects/wm019_wam_future_metric_paired_diagnostic.html) 与 [Matched-Checkpoint Bridge](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.html)：CoffeePressButton 诊断证据层。
7. [Checkpoint Save-Load Gate P0 Audit](../evidence/projects/cosmos_policy_wam_checkpoint_save_load_gate_p0_audit.html)：13 份 base-load summary、短 smoke、formal save2k/save1500 first divergence 与 checkpoint/reload 边界。
8. [Cosmos Policy RoboCasa Official-HF Baseline P0 Audit](../evidence/projects/cosmos_policy_robocasa_baseline_p0_audit.html)：official path 下 raw `86/120`、trusted `84/118`、24×5 status、action-debug integrity 与 ownership 边界。
9. [WAM 1 epoch / full10k Run Reconciliation](../sources/vol_04_cosmos_policy_wam_full10k_run_reconciliation.html)：8-GPU `9907` gate、独立单卡 full10k 与最小 eval 的 run-family 分离。
10. [Cosmos Policy full10k trained eval P0 audit](../evidence/projects/cosmos_policy_full10k_trained_eval_p0_audit.html)：trained `iter_000010000` path 下24×5、raw `2/120`、local-policy trusted `0/118`、4066行 action-debug 与 checkpoint/scorer边界。
