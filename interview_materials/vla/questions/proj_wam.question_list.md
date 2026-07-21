# PROJ-WAM 题卡清单（Training Failure + Diagnostic + Ownership Batch 1）

> 规划日期：2026-07-18；更新：2026-07-21  
> 状态：`source_frozen / batch_1_drafted / evidence_downstreamed / WARN`  
> 题数：4  
> 项目：Cosmos Policy / WAM / CoffeePressButton  
> 规则：先固定 1 epoch 完成 gate，再区分 run contract、训练中间快照、保存/加载、closed-loop eval 与 ownership；CoffeePressButton diagnostic bundle 保持独立证据层。

## 1. 本批题目

| ID | 难度 | 优先级 | 题目 | 证据边界 |
| --- | --- | --- | --- | --- |
| PROJ-WAM-001 | L3 | P0 | 你是否完成了 Cosmos Policy 1 epoch finetune？如何把两次中断讲成可信项目经历？ | 8 卡/global batch 128/`9907`-step contract、step 1903 cgroup OOM、no-cycle smoke、step 1500 state-dict failure 可讲；完整 checkpoint/eval 不存在 |
| PROJ-WAM-002 | L3 | P0 | Cosmos/WAM 哪些部分能说是你做的？如何区分 upstream、训练排障、远端运行和个人 ownership？ | upstream、Project snapshot、candidate/operator/reviewer、CoffeePressButton diagnostic 与官方/其他 run 必须分层；ownership 仍待本人确认 |
| PROJ-WAM-003 | L3 | P0 | base_load_summary 有 715 个 key，为什么仍不能说 checkpoint 可加载？如何设计 save/load gate？ | base-load、short smoke、formal save failure、produced binary、fresh-process reload 与 matched eval 必须分层；当前只有 base-load/短 smoke，checkpoint/reload 仍缺 |
| PROJ-WAM-004 | L3 | P0 | full10k raw `2/120`、trusted `0/118` 与 official-HF raw `86/120`、trusted `84/118` 如何解释？ | 8-GPU gate、independent full10k、official-HF checkpoint 和 invalid policy 分层；不能把 official 71.19% 写成本地训练成绩 |

## 2. 题卡退出条件

1. ID 全局唯一并保持 `unseen`，不创建 `coaching_state.md`。
2. 四张卡均包含短答案、机制展开、诊断/证据、项目挂钩、追问树、危险答案和来源。
3. 明确 `9907` steps→save→new-process load→same-protocol eval 才是 1 epoch 完成 gate。
4. 不把 step 1900 loss `0.2945` 当 final loss，不把 `step_001500` 空目录当 checkpoint，不把 no-cycle 5-step smoke 当完整训练成功。
5. 不把官方 HF `84/118`、历史 1k/5k ablation 或 CoffeePressButton 单 episode/proxy 拼接为本轮结果。
6. 明确 C1/C2 可讲 run contract、数据统计、OOM/no-cycle/save-interface 诊断；C3 完整 epoch、checkpoint、closed-loop success 与 uplift 保持禁止。
7. 回答覆盖 `cycle(dataloader)` 缓存机制、cgroup vs GPU OOM、`EXIT=247`/rank `-9`、`state_dict` 兼容层和 save/load smoke。
8. 30 秒答案保持口述紧凑；HTML 四张卡可折叠，review verdict 保持 `WARN`。

## 3. 依赖与下一步

- 当前证据：[Cosmos Policy 1 Epoch Evidence Freeze](../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)、[WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html) 与 WM-019 diagnostic bundle。
- 结果缺口：标准签名兼容层 diff、1-step save/load smoke、完整 `9907`-step log、checkpoint manifest/SHA、run-specific episode JSONL/scorer。
- ownership 缺口：候选人逐文件确认 iterator patch、远端 operator、error-stack diagnosis、reviewer、协作者与工具辅助边界。
- 下一增量不批量新增题号；可在候选人真实口述后进入单题训练，或先冻结保存接口修复的新证据。
