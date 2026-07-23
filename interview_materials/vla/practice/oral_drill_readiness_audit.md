# 首轮口述队列 Readiness Audit

> 状态：`reconciled / 12_queue_entries / 280_cards_unseen / WARN`  
> 审查日期：2026-07-22
> 范围：核对 `oral_drill_queue.md` 的 12 个 Stable ID 是否有题卡、证据入口、知识/系统页和可对照的 model answer；不记录候选人回答，不改变 mastery，不创建 `coaching_state.md`。

## 1. 结论先行

1. 12/12 队列项都有稳定 ID 和现有题卡入口，所有对应题卡保持 `unseen`。
2. 7/12 队列项已有项目 model answer（WAM 两题共享一页，OpenPiVLA 两题共享一页，Harness/OPD/UWM 各一页）；其余 5 题直接使用知识页、题卡和 source audit，尚未单独生成示范回答。
3. 12/12 都可使用统一的 [单题真实口述捕获模板](oral_drill_capture_template.html) 保存 verbatim transcript、自评、Claim–Evidence–Ownership 核验、五维评分与状态迁移；项目题仍可叠加专用 evidence template。
4. “readiness”只表示材料和链接准备好，不表示候选人掌握。没有真实回答前，不能创建 coaching state 或将 `unseen` 改为 `weak/pass/strong`。

## 2. 逐题对账

| 顺序 | Stable ID | 题卡 | Evidence / knowledge 入口 | Model answer | 当前阻断与下一步 |
| ---: | --- | --- | --- | --- | --- |
| 1 | `PROJ-WAM-001` | [WAM card](../questions/proj_wam.html) | [WAM inventory](../evidence/projects/wam_claim_evidence_inventory.html)；[capture template](wam_oral_capture_template.html) | [implementation-derived WAM model answer](wam_oral_model_answer.html) | 项目主线草稿已就绪；实际回答仍未发生，不能把 diagnostic bundle 说成 uplift |
| 2 | `PROJ-WAM-002` | [WAM card](../questions/proj_wam.html) | [WAM ownership ledger](../evidence/projects/wam_ownership_ledger.html) | 共享 [WAM model answer](wam_oral_model_answer.html) 的 ownership section | Git initial-snapshot、upstream/local/operator/tool 边界已写入；实际 drill 仍在 WAM-001 之后 |
| 3 | `PROJ-OPENPIVLA-001` | [OpenPiVLA card](../questions/proj_openpivla.html) | [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)；[JSON/CE gate](../sources/openpivla_formal_json_ce_shape_contract_artifact_gate.html) | [OpenPiVLA model answer](openpivla_oral_model_answer.html) | 等候真实口述；checkpoint/load smoke 仍缺 |
| 4 | `PROJ-OPENPIVLA-009` | [OpenPiVLA Batch 2 card](../questions/proj_openpivla_batch2.html) | [OpenPiVLA inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/openpivla_ownership_ledger.html) | 共享 [OpenPiVLA model answer](openpivla_oral_model_answer.html) | 97.4 lineage 与 raw eval 仍待核 |
| 5 | `PROJ-HARNESS-001` | [Harness card](../questions/proj_robot_harness.html) | [Harness inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/robot_harness_ownership_ledger.html) | [Harness model answer](robot_harness_oral_model_answer.html) | 等候真实口述；proxy 不等于 physical success |
| 6 | `PROJ-OPD-001` | [OPD card](../questions/proj_opd.html) | [OPD inventory](../evidence/projects/opd_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/opd_ownership_ledger.html) | [OPD model answer](opd_oral_model_answer.html) | ablation/raw prediction/ownership 未闭合 |
| 7 | `PROJ-UWM-001` | [UWM card](../questions/proj_uwm.html) | [UWM inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html)；[ownership ledger](../evidence/projects/uwm_libero_ownership_ledger.html) | [UWM model answer](uwm_oral_model_answer.html) | strict/reset/paper protocol 必须逐 tuple 复述 |
| 8 | `VLA-PER-020` | [PER-020 card](../questions/vol_06_per020.html) | [PER-020 knowledge](../knowledge/vol_06_per020_robustness_safety_fallback.html)；[independent review](../sources/vol_06_per020_robustness_safety_fallback_independent_fact_review.html) | 使用 knowledge/card 双档答案 | 等候真实口述；不报个人 safety result |
| 9 | `VLA-WM-025` | [WM-025 card](../questions/vol_04_world_model_sim2real_wm025.html) | [WM-025 knowledge](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html)；[source freeze](../sources/vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html) | 使用 knowledge/card 双档答案 | 白板练习 slot/mask/loss；local gradient bundle 缺失 |
| 10 | `VLA-ENG-013` | [ENG-013 card](../questions/vol_05_engineering_eval_eng013.html) | [ENG-013 knowledge](../knowledge/vol_05_engineering_eval_eng013.html)；[source freeze](../sources/vol_05_eng013_reproducibility_source_freeze.html) | 使用 knowledge/card 双档答案 | 白板练 seed/RNG/resume；不写成项目 exact resume |
| 11 | `SYS-VLA-004` | [SYS-004 card](../questions/vol_08_sys004.html) | [SYS-004 knowledge](../knowledge/vol_08_sys004_fault_recovery_safety_observability.html)；[source freeze](../sources/vol_08_sys004_fault_recovery_safety_observability_source_freeze.html) | 使用 knowledge/card 双档答案 | 系统设计练 first-divergence/safe-apply/fencing |
| 12 | `CODE-VLA-004` | [CODE-004 card](../questions/vol_08_code004.html) | [CODE-004 knowledge](../knowledge/vol_08_code004_masked_loss.html)；[source freeze](../sources/vol_08_code004_masked_loss_source_freeze.html) | 使用 knowledge/card 双档答案 | 白板练 empty mask/denominator/reduction |

## 3. Readiness gate

| Gate | 结果 | 证据 |
| --- | --- | --- |
| Stable ID 与题卡 | `12/12 PASS` | queue ID 可映射到现有 question Markdown/HTML |
| Evidence / knowledge 入口 | `12/12 PASS` | 每项至少一个 inventory、source、knowledge 或 system page |
| Model answer | `7/12 PASS` | 五项目 pages，WAM/OpenPiVLA 各共享一页 |
| 单题 capture template | `12/12 PASS` | 一个 Stable ID、原始回答、自评、证据核验、五维评分和迁移规则均有统一字段 |
| 真实回答 | `0/12` | 当前没有候选人 transcript |
| Mastery migration | `0/280` | 所有题卡仍 unseen |
| Coaching state | `not created` | 遵守 practice contract |

## 4. 使用规则

- 队列只允许一次问一题；示范回答必须在候选人先回答后再作为对照。
- 每题先复制空白 capture template，保存 verbatim transcript 后再进行自评和教练反馈；不直接修改空白 canonical 模板。
- 项目题优先评估 evidence、ownership、protocol 和 first divergence，不以流畅背诵 model answer 代替掌握。
- 知识/系统题可以进行白板练习，但仍要记录公式、实现映射和边界，不把页面覆盖当作 drilled。
- 新 artifact 先进入 inventory/ledger/source audit，再修改回答；不要只改 narrative。

## 5. 下一步

五项目 implementation-derived model-answer bundle 与通用 capture template 已就绪；真实训练侧仍只收集 `PROJ-WAM-001` 的实际回答。回答应先进入 capture template，再按五维评分卡记录 `What I Heard → What Is Working → Gaps To Close → Priority Move → Next Step`，最后才决定是否创建 `coaching_state.md`。

## References

1. [Oral Drill Queue](oral_drill_queue.html)。
2. [General Single-Question Capture Template](oral_drill_capture_template.html)。
3. [WAM Capture Template](wam_oral_capture_template.html)。
4. [Five-project Evidence Reconciliation](../sources/vol_07_project_evidence_reconciliation.html)。
