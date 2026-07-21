# PROJ-OPD：OPD / VLM Grounding 项目原子题卡（Direct-Evidence Batch 1 + Ownership）

> 状态：`drafted / cards_8_of_8 / WARN`  
> 更新日期：2026-07-17  
> 当前题数：8 / 8  
> 覆盖范围：`PROJ-OPD-001..009`  
> 难度：L2 4 题 / L3 4 题  
> 优先级：P0 7 题 / P1 1 题  
> 练习状态：全部 `unseen`  
> 前置证据：[OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)；weights、raw predictions、统一 ablation 与 ownership ledger 未闭合，不得升级为强因果结论。

## A. 问题定义与数据路由

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPD-001</b> · OPD 这条路线要解决什么问题，为什么不是简单把五个 expert 的数据混在一起？</summary>

**面试意图**：判断你是否能把多 expert、统一 student 和输出协议问题讲成一个可验证的训练设计，而不是只复述 OPD 名字。

**30 秒回答**：目标是让一个 8B student 同时保留 object/region/relation/point/text 能力，并根据任务输出正确格式。数据先训练五个 specialist，再用 route metadata 选择 teacher 做 coldstart 和在线 KL；直接混数据容易让能力和 `<box>/<point>/text` 格式互相污染。

**机制展开（约 2 分钟）**：五个 expert 分别偏 reasoning、object、region、spatial relation 和 RoboPoint。student 样本保留 `target_expert`、`candidate_experts`、`expected_format`、seen/unseen/hard、boundary 和 format-conflict，训练时按 target route 选 teacher。这样把数据来源、能力边界和输出契约显式化；但 route 是 metadata 驱动，不是已验证的 learned router。组合结果也不能归因于 OPD 单一机制，因为数据配比、specialist、coldstart 和格式对齐同时变化。

**诊断 / 证据**：检查五 expert 配额、student category/format counts、route counts 和训练 summary；再做 no-route、single-teacher、无 boundary/format-conflict 的对照。当前前四项有本地证据，消融未冻结。

**项目挂钩**：个人贡献应表述为多域数据合同、route metadata、训练阶段与评估协议的设计/验收；不要把统一 student 的静态指标说成真实机器人闭环。

**追问树**：为什么要 five expert？route 是模型学出来的吗？general 数据为什么占 25%？格式冲突如何构造？

**危险答案**：说“OPD 自动学会了专家路由”，或说“只要把五个模型平均就能得到最强模型”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPD-002</b> · 五个 expert 的数据配额和 spatial-relation 重采样如何设计？</summary>

**面试意图**：检查你是否能从脚本解释数据分工、长尾关系和 image-level split，而不是只背 expert 名称。

**30 秒回答**：每个 expert 的目标为 train 800k、eval 20k，并按 image hash 做 5% candidate eval。reasoning 偏 keepalive，RoboPoint 偏 point，object/region/relation 提高对应池比例；spatial expert 再平衡长尾关系。

**机制展开（约 2 分钟）**：脚本的 `EXPERT_TRAIN_PLAN` 为五个 expert 指定 source quota，`split_for_image` 用稳定 image/video key 做 train/eval candidate split，避免同图跨 split。`REL_BUCKET_WEIGHTS` 让 spatial relation 不被高频 `on/in` 淹没，并在输出 metadata 中保留 expert、source、source line、seed、relation bucket，便于追溯。它证明了数据路由规则存在，不证明每个 expert 已经独立 raw-holdout 最优；model asset table 还明确五个 200k expert 没有独立 10k 评估。

**诊断 / 证据**：复算 quota 与 eval scale、统计每个 relation bucket、检查 image/fingerprint overlap，并单独评估各 expert。当前配额和 split 是 `local-direct`，独立 expert eval 与因果比较仍缺。

**项目挂钩**：可讲“先解决数据分布和评估泄漏，再讨论 OPD”，把数据工程与模型训练分开。

**追问树**：为什么不用随机行 split？关系 bucket 会不会改变真实分布？eval 20k 是真实 held-out 吗？如何判断重采样过度？

**危险答案**：把 800k/20k 目标写成实际每个文件都精确达到，或说 relation rebalance 本身就证明关系泛化提升。

**来源**：[1][4][5]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPD-003</b> · student 数据里的 seen/unseen/hard、boundary 和 format-conflict 分别解决什么问题？</summary>

**面试意图**：判断你能否解释训练数据不是单一 iid 混合，而是带有泛化与接口边界的显式合同。

**30 秒回答**：每个 expert 过滤后前 100k 行标为 seen，domain 再拆 unseen/hard；general 防止模型“凡问必坐标”；boundary 覆盖 object/region/point/reasoning 易混边界；format-conflict 强化 tag、坐标范围、错误格式诱导和 prompt injection 下的输出契约。

**机制展开（约 2 分钟）**：最终 train summary 是 domain 599,905、general 250,000、boundary 99,998、format-conflict 49,997，共 999,900。每行写入 target/candidate expert、expected format、source line、fingerprint 与 `seen_by_expert_100k`，使 eval 可以按 exposure 分层。格式样本不是为了制造“更难看”的 prompt，而是防止 box/point/text 之间的输出漂移。严格审计还检查 JSON、坐标、图片、重复和 train/eval image overlap；这些是数据质量 gate，不是模型成功率。

**诊断 / 证据**：按 category、subtype、exposure 和 expected format 分层报 loss/format/geometry；做去掉 boundary 或 format-conflict 的对照。当前 metadata 与硬审计已冻结，分层模型结果和 ablation 未冻结。

**项目挂钩**：可把“问题发现→数据标签→评估切片”的闭环讲成个人设计价值，避免只强调训练步数。

**追问树**：为什么 train 少 100 行？seen 定义会不会泄漏？format-conflict 会不会导致过度拒答？如何构造 hard？

**危险答案**：说“100 万行全部是 unseen”，或把无 overlap 直接说成模型没有过拟合。

**来源**：[1][2][6]　**练习状态**：unseen

</details>

## B. Coldstart 与在线 OPD

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPD-004</b> · coldstart500 和正式 OPD5000 的训练链路有什么区别？</summary>

**面试意图**：检查你是否分清 teacher rollout、student rollout、KL 监督和训练起点。

**30 秒回答**：coldstart 从 8B base 出发，用五个 teacher rollout 做 500 steps 的 full-vocab KL；OPD5000 从该输出继续，让 student rollout，再让 route 对应 teacher 在同一 response 上 forward，完成 5000 steps 在线 KL。

**机制展开（约 2 分钟）**：coldstart 是 `teacher` rollout，`max_new_tokens=128`、prefix=64，veto beta 在 100 steps 内退火；正式 OPD 是 `student` rollout，`max_new_tokens=64`、prefix=64、skip 64,000，保存 1000–5000 checkpoints。五 teacher 以 `preloaded_zero3` 常驻并按 route 选择，做 full-vocab distillation。coldstart 先处理分布与格式启动，online 阶段再覆盖 student 实际 response；缺 coldstart-only raw-holdout 对照，不能量化各阶段贡献。

**诊断 / 证据**：检查两个 run summary 的 student path、rollout source、teacher load counts、route counts、loss/entropy/top-k overlap，并保留每阶段 checkpoint 与 raw eval。当前 summaries 与 checkpoint table 有，完整权重/raw log 没有。

**项目挂钩**：回答时强调训练阶段和 artifact lineage，而不是把“5000 steps”当作算法效果本身。

**追问树**：为什么不直接 online？为什么 full-vocab KL？student rollout 的分布偏移如何处理？veto beta 是什么？

**危险答案**：把 coldstart 的 teacher rollout 说成正式 student on-policy，或说 5000 steps 自动证明收敛。

**来源**：[1][7][8]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPD-005</b> · route-based teacher selection 与 learned router 有什么区别？为什么用 full-vocabulary KL？</summary>

**面试意图**：检查你能否把实现事实、训练目标和未验证假设分层。

**30 秒回答**：当前 teacher selection 是样本 metadata 的 target route，不是单独训练的 learned router。full-vocabulary KL 在 student 实际 response 的每个 prefix 上约束完整分布，比只蒸馏 top-k 保留更多 teacher 的不确定性与格式偏好，但成本更高。

**机制展开（约 2 分钟）**：脚本把 `target_expert/candidate_experts` 转成 route；`route_policy=target` 时每行只激活 target teacher。五 teacher 以 ZeRO-3 预加载。student rollout 后，teacher 对同一 token sequence forward，计算 full-vocab KL，并记录双方 entropy、top-k overlap、OPD loss 和 route counts。route metadata 是监督来源，不等于部署时模型会识别任务；learned router 还需要额外模型、routing loss 和同协议 ablation。

**诊断 / 证据**：做 target vs candidate route、single-teacher、random route、top-k vs full-vocab 的对照，并按格式/池统计错误。当前代码和 summary 支持实现路径，消融与 learned router 证据缺失。

**项目挂钩**：这是一个适合回答“工程实现与研究假设边界”的问题：可以准确讲当前做了什么，也能指出下一步研究空间。

**追问树**：candidate route 为什么存在？full-vocab KL 会不会过度复制 teacher 错误？为什么不做 MoE gate？如何防止 route imbalance？

**危险答案**：说“route id 就是 learned gating”，或说 full-vocab KL 一定比 top-k 更好且没有显存代价。

**来源**：[1][7][8]　**练习状态**：unseen

</details>

## C. 评估、协议与真实性边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPD-006</b> · OPD5000 的 checkpoint 应该怎么选，为什么不能只报 checkpoint-5000？</summary>

**面试意图**：训练你根据多目标指标做 checkpoint selection，而不是把最后一个 checkpoint 当作全局最佳。

**30 秒回答**：ckpt3000 的整体 box IoU 最高 0.4761，ckpt5000 的 Box Acc@0.5=0.5238、Point Hit@50/100=0.7493/0.8729，ckpt4000 的 text exact=0.8784。按 pool 最佳点也分散，所以 ckpt5000 只能作为综合默认候选，不能说所有指标最佳。

**机制展开（约 2 分钟）**：10k holdout 按 box 6100、point 1400、text 2500 分开计算；ckpt3000 的 VG region/relation 最好，semantic-nav box 在 ckpt2000 最好，VG object 在 ckpt1000 最好，keepalive text 在 ckpt4000 最好，point 与多个 box pool 在 ckpt5000 最好。选择取决于部署目标：若强调统一多格式和 point，5000 合理；若强调整体 IoU 或特定关系池，应保留 3000。当前表格是同一新版 OPD5000 eval line，但没有 raw predictions 和完整 checkpoint bundle。

**诊断 / 证据**：冻结 pool/format denominator、scorer 版本、checkpoint parent、每样本 prediction 与 selection rationale；报告 Pareto frontier 而不是单一排名。当前 by-format/by-pool 表已冻结，raw predictions/lineage 仍缺。

**项目挂钩**：可以把 checkpoint selection 讲成“指标与产品目标对齐”的工程决策，而不是追求最后一步数字。

**追问树**：为什么 ckpt3000 IoU 更高但 ckpt5000 point 更好？如何避免按 holdout 过拟合选点？最终部署选哪个？

**危险答案**：说“5000 一定收敛且全面最好”，或把不同 pool 的 best 拼成一个虚构 checkpoint。

**来源**：[1][9][10]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>PROJ-OPD-007</b> · raw-holdout 的 0 泄漏结论是怎样得到的，重复图片为什么仍然存在？</summary>

**面试意图**：确认你理解 source-line、fingerprint、图片和样本重复是不同层级的 leakage gate。

**30 秒回答**：10k holdout 阻断了五 expert 前 100k、OPD train 和训练图片集合；审计显示 fingerprint、source-line、image+prompt+answer 重复均为 0，训练图片泄漏也为 0。唯一图片 8,251，不是 10k，因为同一张 VG/RefCOCO 图片可以有多个合法标注。

**机制展开（约 2 分钟）**：evalset summary 记录每个 pool quota 和 blocklist，dedupe audit 记录 0 duplicate fingerprints、0 duplicate source lines、0 duplicate prompt-answer-image keys、0 image_seen_in_train rows。另有 1,168 个重复图片路径、2,917 行落在重复图片上，这是同图多 object/region/relation annotation，不等于同一监督样本。面试应说“样本级和训练图片级泄漏为零”，不要说“评估图片完全唯一”。

**诊断 / 证据**：复算 source-line、normalized fingerprint、image+prompt+answer key、train image set，并按 pool 输出重复图片分布；再检查近重复图或同源视频是否需要额外 block。当前三类严格重复和训练图片 gate 有本地审计，近重复/分布代表性仍可继续加强。

**项目挂钩**：这是体现评估严谨度的高价值回答：先证明 holdout 干净，再讨论模型数字。

**追问树**：为什么 image hash split 还要 blocklist？同一图片多标注会不会让 n 虚高？如何处理 near-duplicate？

**危险答案**：说“unique images=10,000”，或把重复图片路径直接等同于数据泄漏。

**来源**：[1][11][12]　**练习状态**：unseen

</details>

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>PROJ-OPD-008</b> · point strict=0 的结果如何解释？OPD 的提升能否归因于 OPD？</summary>

**面试意图**：这是项目真实性与协议意识的高压题，要求同时处理 parser mismatch、可比性和个人 ownership。

**30 秒回答**：早期 point prompt 写 `[(x,y)]`，strict parser 却要求 `<point>[[x,y],...]</point>`，所以 strict=0 不等于不会定位。修正 prompt 后 Qwen-122B Hit@100=0.8200；OPD ckpt5000 原 strict=0.8729，但缺消融，不能作单因果归因。

**机制展开（约 2 分钟）**：point 需要分三种口径：original strict 看部署接口是否遵守 tag；protocol-fixed strict 看明确提示下的协议与几何能力；lenient geometry 兼容裸坐标，仅作历史能力估计。当前 OPD 训练期已对齐 `<point>`，因此原 strict 可读；大模型必须用 protocol-fixed strict 才公平。因果上，旧版 OPD final 与新版 OPD5000 也不是同一 run；缺 SFT-only、single-teacher、no-synthetic、synthetic-ratio 和 raw prediction bundle。ownership 方面，Git author 只是提交署名，不能替代逐文件 ledger。

**诊断 / 证据**：冻结 prompt hash、parser version、format/geometry 分项，做同 suite base→SFT→coldstart→OPD paired rerun；补逐文件 personal/collaboration/tool-assisted ledger。当前 protocol correction 和组合指标有，单因素与 ownership 仍 pending。

**项目挂钩**：推荐把“主动指出评估 bug 与因果缺口”作为项目结尾的可信度防线，比把所有结果都包装成 uplift 更有说服力。

**追问树**：为什么 OPD strict 可以直接比而 122B 不行？如果只看 box，谁更强？下一步最重要的 ablation 是什么？哪些代码是你亲手完成？

**危险答案**：说“base/instruct/大模型不会 point”，或说“OPD 比 base 高 11.5 个点，所以 uplift 全来自 OPD”。

**来源**：[1][13][14]　**练习状态**：unseen

</details>

## D. Ownership 与可抗追问边界

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>PROJ-OPD-009</b> · OPD 哪些部分能说是你做的？如何处理 `msz136`、`mousongzhe`、Codex 与远端 run 的边界？</summary>

**面试意图**：判断你是否能把 Git 署名、代码存在、设计决策、运行验收和 checkpoint/result ownership 分开，而不是把一次性快照认领成全部个人工作。

**30 秒回答**：我把数据、训练、评估、结果四条链分开。源码和报告可核验，但初始 scaffold 是 `msz136`，后续是 `mousongzhe` 提交，OPD5000 权重/raw predictions 未同步；所以 Git author 或 summary 不能替代逐文件个人 ownership。

**机制展开（约 2 分钟）**：先绑定 artifact：数据 builder/audit/evaluator 在 `3ef636b`，manifest 指向 `point/train_opd_online_vl.py`，不能用根目录副本替代。再区分设计者、提交者、远端运行者、报告生成者和 reviewer。最后按证据降级：报告支持曲线与 protocol，manifest 排除权重、optimizer、raw holdout 和 predictions；强回答要能解释一个函数并指出 diff、load smoke、raw bundle、ablation 与工具边界仍缺。

**诊断 / 证据**：使用 [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html) 的 13 行矩阵；检查 `git log --follow`、blob/SHA、manifest synced scope、run summary、checkpoint table 和 candidate confirmation。没有真实口述前保持 `candidate_confirmation_pending / unseen`，不创建 coaching state。

**项目挂钩**：这是 OPD 项目最重要的真实性题。它允许你讲清真实工程价值，同时避免把 `mousongzhe` 的 commit、`msz136` 的 scaffold、远端 summary 和自己的个人贡献混成一句“全是我做的”。

**追问树**：哪一个函数是你亲手改的？为什么 `point/` 和根目录 trainer 不同？谁在 remote 运行？checkpoint 能 load 吗？Codex/协作者做了什么？如果没有 ablation，为什么不能说 OPD uplift？

**危险答案**：说“Git author 是我，所以所有代码和指标都是我的”，或把“报告里有数字”说成“我拥有模型结果”。

**来源**：[1][15][16]　**练习状态**：unseen

</details>

## 参考来源

1. [OPD / VLM Grounding Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.html)：五 expert、student route、训练 lineage、raw-holdout、point protocol 和 ownership 边界。
2. `C:\Users\mousongzhe\muxi\build_expert_mixes_seed0_v2.py`：expert quota、image-hash split、relation bucket 与 metadata。
3. `C:\Users\mousongzhe\muxi\build_opd_student_v1.py`：student category、seen/unseen/hard、boundary/format-conflict 和 fingerprint 字段。
4. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\model_assets_eval_table.md`：expert 训练摘要、checkpoint 资产边界和 pool readout。
5. `C:\Users\mousongzhe\muxi\report.md`：数据构造、严格审计、point protocol 修正与历史 OPD 说明。
6. `C:\Users\mousongzhe\muxi\audit_opd_student_v1.py`：JSON、长度、坐标、图片、重复与 overlap 审计逻辑。
7. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\remote_model_summaries\coldstart500_opd_online_run_summary.json`：coldstart rollout 与 full-vocab KL summary。
8. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\remote_model_summaries\opd5000_opd_online_run_summary.json` 与 `train_opd_online_vl.py`：student rollout、route、skip、checkpoint 和 full-vocab KL。
9. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\opd5000_ckpt_eval_by_format_table.md`：ckpt1000–5000 的 format-level metrics。
10. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\opd5000_ckpt_eval_by_pool_table.md`：八个 eval pool 的 checkpoint selection。
11. `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\evalset_summary.json`：10k holdout quota、blocklist 和格式分布。
12. `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\dedupe_audit.json`：重复与训练图片泄漏审计。
13. `C:\Users\mousongzhe\muxi\report\raw_holdout_eval_8models_20260525\raw_holdout_eval_8models_report.md`：旧版 OPD final 与 point protocol context。
14. `C:\Users\mousongzhe\muxi\report\openai_base64_point_protocol_qwen122_qwen35_20260603\comparison_summary_table.md`：protocol-fixed Qwen-122B/Qwen3-35B-VL point 结果。
15. [OPD Ownership Ledger](../evidence/projects/opd_ownership_ledger.html)：Git identity、point/root trainer 差异、13 行 ownership matrix 与 C3 gate。
16. `C:\Users\mousongzhe\muxi\report\opd5000_newexperts_20260601\artifact_manifest.json`：OPD5000 本地同步范围与明确排除的权重、optimizer、raw predictions。
