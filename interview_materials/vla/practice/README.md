# Practice

本目录保存长期训练状态，不保存未经核验的知识正文。

当前内容进度：[`module_progress.md`](module_progress.md)。它记录模块和题卡状态，不替代正式口述评分。

首轮逐题入口：[`oral_drill_queue.html`](oral_drill_queue.html) / [`canonical Markdown`](oral_drill_queue.md) / [`review`](oral_drill_queue.review.json)。队列只定义顺序与评分协议；没有真实回答前不创建 `coaching_state.md`。

Ownership 逐题入口：[`ownership_confirmation_queue.html`](ownership_confirmation_queue.html) / [`canonical Markdown`](ownership_confirmation_queue.md) / [`review`](ownership_confirmation_queue.review.json)。40 个条目映射五份项目 ledger；一次只问一题，未回答前全部保持 `unseen`。

队首填写模板：[`wam_oral_capture_template.html`](wam_oral_capture_template.html) / [`canonical Markdown`](wam_oral_capture_template.md) / [`review`](wam_oral_capture_template.review.json)。模板只预填证据锚点与防越界检查，候选人回答和评分仍为空。

Cosmos Policy / WAM 对照材料：[`wam_oral_model_answer.html`](wam_oral_model_answer.html) / [`canonical Markdown`](wam_oral_model_answer.md) / [`review`](wam_oral_model_answer.review.json)。覆盖 8 卡/global batch 128 的 `9907`-step gate、step 1903 cgroup OOM、no-cycle smoke、step 1500 `state_dict` 保存接口失败，独立单卡 full10k 的 step-10000 loss=`0.0543` 与 CoffeePressButton `0/1` smoke，official-HF 24×5 baseline 的 raw `86/120` / trusted `84/118`，TurnOffMicrowave local 1k 的 fixed-batch→closed-loop→same-input first-divergence，以及 715-key base-load/short-smoke/formal save-load gate；五条运行/诊断线不可合并，且不是候选人 transcript。

OpenPiVLA 对照材料：[`openpivla_oral_model_answer.html`](openpivla_oral_model_answer.html) / [`canonical Markdown`](openpivla_oral_model_answer.md) / [`review`](openpivla_oral_model_answer.review.json)。覆盖 formal trainer 的 Qwen3-VL、LoRA、full-chat causal CE、eager/MACA 兼容性、smoke/formal/raw 证据阶梯、`H=15,D=72` 与 `limit=16` shape 冲突、checkpoint lineage，以及 FAST/flow/benchmark 边界；仍不是候选人 transcript。

Robot Harness 对照材料：[`robot_harness_oral_model_answer.html`](robot_harness_oral_model_answer.html) / [`canonical Markdown`](robot_harness_oral_model_answer.md) / [`review`](robot_harness_oral_model_answer.review.json)。覆盖 runtime scope/mutex/cancel/compensation、SFT/GRPO/restraint 数据合同、schema-aware reward、P0 partial-raw（28/40 primary、6/10 exact）、scorer/checkpoint/effect-sink 边界、11 passed/1 config-drift test residual 与 Codex ownership 三轴口径；仍不是候选人 transcript。

OPD 对照材料：[`opd_oral_model_answer.html`](opd_oral_model_answer.html) / [`canonical Markdown`](opd_oral_model_answer.md) / [`review`](opd_oral_model_answer.review.json)。覆盖五 expert 数据路由、coldstart/online OPD、full-vocabulary KL、point protocol、checkpoint selection 与因果/ownership 边界。

UWM/LIBERO 对照材料：[`uwm_oral_model_answer.html`](uwm_oral_model_answer.html) / [`canonical Markdown`](uwm_oral_model_answer.md) / [`review`](uwm_oral_model_answer.review.json)。覆盖 strict/reset/paper protocol、normalizer、remote-final、DataLoader stall，以及 RoboCasa actionheadfix、teacher-forced/open-loop/closed-loop 分层、h4 `0/54` 和 convert_action invalid-policy 防线；仍不是候选人 transcript。

首轮队列对账：[Readiness Audit](oral_drill_readiness_audit.html) / [canonical Markdown](oral_drill_readiness_audit.md) / [review](oral_drill_readiness_audit.review.json)。它只证明材料入口齐全，不代表任何题已 drilled。

训练规则：

1. 一次只问一个问题；每轮聚焦 5-8 个高价值问题。
2. 每题先由候选人口述，再给证据化反馈和示范回答。
3. 按 Substance、Structure、Relevance、Credibility、Differentiation 评分。
4. 每轮更新通过点、高危穿帮点、需要降级/升级的简历表达和下一轮分支。
5. 页面生成完成不等于掌握；只有实际回答达到标准后才标记 `pass/strong`。

后续文件：`coaching_state.md`、`drill_log.md`、`interview_postmortems.md`，在第一次真实训练时创建。
