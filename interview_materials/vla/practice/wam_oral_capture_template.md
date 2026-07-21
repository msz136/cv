# PROJ-WAM-001 口述捕获模板：CoffeePressButton Diagnostic Bundle

> 状态：`capture_template / awaiting_candidate_answer / unseen`  
> 更新日期：2026-07-21  
> 使用方式：先由候选人填“我的回答”，再由教练按证据核验和五维评分；模板中的事实只来自已登记 artifact，不代表候选人已经确认 ownership。

## 1. 题目

**如何把一组 WAM CoffeePressButton diagnostic bundle 讲成可信的项目经历？**

回答限制：30 秒先讲结论；随后最多 2 分钟展开。一次只处理本题，不提前回答 `PROJ-WAM-002`。

## 2. 证据锚点（可直接引用）

| Evidence layer | 当前已登记事实 | 不能直接推出 |
| --- | --- | --- |
| manifest | base/trained manifest、task/episode/seed/env_seed/max_steps/open-loop/denoise 等字段可读 | checkpoint binary 内容、训练 uplift |
| action trace | 两侧各 300 步；policy 7 维、environment 12 维；finite、shape 可读；有 MAE/RMSE 诊断 | action-label loss、成功率或 benchmark |
| video | CoffeePressButton episode 0 的失败视频已登记 | 完整 suite denominator、泛化或零成功率 |
| future-image metric | 单样本 offline PSNR/SSIM 对照 | 与 rollout success 的相关/因果关系 |
| checkpoint bridge | 两侧引用同一 checkpoint path 字符串 | binary hash、可加载性、processor/normalizer 一致性 |

## 3. 候选人填写区

### 3.1 30 秒回答

> 我在这个项目中面对的任务/约束是：
>
> 【候选人填写】
>
> 我实际负责或亲手验证的是：
>
> 【候选人填写；必须区分亲手、协作、工具辅助、只审查、只运行】
>
> 当前最强证据是：
>
> 【候选人填写；至少绑定一个文件/manifest/trace，而不是只报数字】
>
> 所以我能证明的是：
>
> 【候选人填写】
>
> 目前还不能证明的是：
>
> 【候选人填写；应主动提 checkpoint、denominator、target metric 或 ownership 缺口】

### 3.2 2 分钟机制展开

请按下面顺序填写，不要把 upstream 机制直接写成个人贡献：

1. **任务与接口**：policy action、environment/controller action、chunk/open-loop/replan 如何连接？
   - 我的回答：
   - 证据链接/字段：
2. **诊断方法**：manifest、trace integrity、video、offline proxy、closed-loop outcome 如何分层？
   - 我的回答：
   - 证据链接/字段：
3. **失败或不一致**：first verified divergence 是什么？哪些只是 hypothesis？
   - 我的回答：
   - 证据链接/字段：
4. **个人贡献**：哪一个具体文件、函数、配置、命令或验收动作是我亲自完成的？
   - 我的回答：
   - 证据链接/commit/diff：
5. **下一步补证**：如果要升级成 result-owned claim，最小 P0 bundle 是什么？
   - 我的回答：

## 4. 自动防越界清单

回答提交前逐项自检：

- [ ] 没有把 `0.09718→0.05349` 当作当前已验证 MSE；
- [ ] 没有恢复 `0.90–0.95 / 0.75` 或 `84/118`，除非能给出 checkpoint、task、trial、init、scorer 和 raw episodes；
- [ ] 没有把 episode 0 `success=false` 说成 benchmark 0-success；
- [ ] 没有把 policy MAE/RMSE 说成 action-label loss；
- [ ] 没有把 PSNR/SSIM 说成 rollout success 的预测或因果证据；
- [ ] 没有把 checkpoint path equality 说成 binary verification；
- [ ] 没有把 Cosmos upstream slot/mask/routing 说成原创设计；
- [ ] 没有用 Git author、路径、summary 或文件名证明 ownership；
- [ ] 明确说出至少一个 `unverified` 缺口和下一步 P0 artifact。

## 5. 教练评分区（回答后填写）

### What I Heard

【等待真实回答】

### What Is Working

【等待真实回答】

### Gaps To Close

【等待真实回答】

### Scorecard

| 维度 | 分数 1–5 | 证据化备注 |
| --- | ---: | --- |
| Substance |  |  |
| Structure |  |  |
| Relevance |  |  |
| Credibility |  |  |
| Differentiation |  |  |

**Confidence**：`未评分`。没有候选人回答前，不得填写分数、不得改变题卡状态、不得创建 `coaching_state.md`。

### Priority Move

【回答后填写一个最重要的改进动作】

### Next Step

默认下一题仍由队列决定；只有本题完成反馈后，才进入 `PROJ-WAM-002`。

## 6. 参考证据

- [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)
- [WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html)
- [WM-019 Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)
- [WM-019 Action-Trace Diagnostic](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html)
- [WM-019 Future-Metric Diagnostic](../evidence/projects/wm019_wam_future_metric_paired_diagnostic.html)
- [WM-019 Matched-Checkpoint Bridge](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.html)
- [PROJ-WAM-001 Atomic Card](../questions/proj_wam.html)
