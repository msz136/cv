# VLA 真实口述 Drill Queue

> 状态：`queued / no_candidate_answers / no_mastery_changes`  
> 更新日期：2026-07-21  
> 用途：把已有题卡转成一次只问一题的口述队列。这里不记录候选人答案，不替代 `coaching_state.md`；第一次真实回答后，才创建正式训练状态。

## 1. 执行协议

每次只取队首一题，候选人先回答，之后才进入反馈和下一题。回答时优先给出：

1. 任务/问题与输入输出边界；
2. 自己实际负责的接口、决策或验证动作；
3. 机制链与 trade-off；
4. 可定位证据、协议和分母；
5. 当前不能证明的内容与下一步补证。

没有 raw artifact 时，答案必须明确使用 `inference` 或 `unverified`，不能用 Git author、文件名、上游论文、summary 或配置路径代替 ownership。

## 2. 首轮队列

| 顺序 | Stable ID | 题目 | 目标 | 当前状态 |
| ---: | --- | --- | --- | --- |
| 1 | `PROJ-WAM-001` | 如何把 CoffeePressButton diagnostic bundle 讲成可信项目经历？ | 诊断证据、分母、失败边界 | `queued / unseen` |
| 2 | `PROJ-WAM-002` | Cosmos/WAM 哪些部分能说是你做的？ | upstream/local/ownership 分层 | `queued / unseen` |
| 3 | `PROJ-OPENPIVLA-001` | OpenPiVLA 的输入、JSON action 与 causal-CE 链路如何闭合？ | parser/shape/loss contract | `queued / unseen` |
| 4 | `PROJ-OPENPIVLA-009` | formal、smoke、report 与 97.4% 证据如何区分？ | lineage、denominator、结果等级 | `queued / unseen` |
| 5 | `PROJ-HARNESS-001` | Robot Harness 的工具调用闭环和个人贡献如何界定？ | schema/runtime/协作边界 | `queued / unseen` |
| 6 | `PROJ-OPD-001` | OPD 的问题定义、teacher/student 与 point/box/text 输出是什么？ | 数据路由与输出协议 | `queued / unseen` |
| 7 | `PROJ-UWM-001` | UWM/LIBERO 的 strict 与 reset-style 结果如何避免混比？ | protocol tuple 与结果边界 | `queued / unseen` |
| 8 | `VLA-PER-020` | corruption、uncertainty、risk gate、fallback 与 E-stop 如何组成可复现协议？ | robustness/safety 面试主线 | `queued / unseen` |
| 9 | `VLA-WM-025` | Cosmos/WAM slot、mask 与 value auxiliary loss 如何影响训练？ | model/loss 机制 | `queued / unseen` |
| 10 | `VLA-ENG-013` | 如何保证分布式训练的 seed、sampler、RNG 与 resume 可复现？ | engineering evidence | `queued / unseen` |
| 11 | `SYS-VLA-004` | VLA fault recovery、safe-apply、lease fencing 与 observability 如何设计？ | 系统设计与 fail-closed | `queued / unseen` |
| 12 | `CODE-VLA-004` | masked action loss 的 denominator、empty mask 与 distributed reduction 怎么处理？ | 白板实现与边界条件 | `queued / unseen` |

队列顺序是面试收益排序，不是 mastery 排序；任何题都必须在实际回答后才有可能从 `unseen` 迁移到 `weak/pass/strong`。

## 3. 单题评分卡（回答后使用）

每个维度 1–5 分；未回答时不填分数：

| 维度 | 1 分 | 3 分 | 5 分 |
| --- | --- | --- | --- |
| Substance | 只有名词 | 能解释主要机制 | 能补公式/实现/反例与 trade-off |
| Structure | 叙述跳跃 | 有问题→方案→结果 | 证据链与追问顺序清晰 |
| Relevance | 泛泛讲论文 | 对齐题目 | 只保留与该项目/岗位相关的细节 |
| Credibility | 无证据或越界 | 能指出部分缺口 | 每个 claim 都绑定 artifact、protocol 或明确的 unknown |
| Differentiation | 像模板答案 | 有项目接口细节 | 能说清个人决策、失败转折与下一步实验 |

反馈顺序固定为：`What I Heard → What Is Working → Gaps To Close → Priority Move → Next Step`。第一次回答前，不创建 coaching state，也不修改题卡 review JSON。

## 4. 回答提交格式

候选人每次只需发送一题的自然口述文字，建议附带：

```text
Stable ID: PROJ-WAM-001
回答：……
我最不确定的点：……（可选）
```

收到后才记录 transcript、五维评分、证据缺口和下一题；如果回答中出现无法由仓库证据支持的数字，会先降级 claim，再给补证建议。

## 5. 题卡入口

- [WAM 题卡](../questions/proj_wam.html)
- [OpenPiVLA 题卡](../questions/proj_openpivla.html) 与 [Batch 2](../questions/proj_openpivla_batch2.html)
- [Robot Harness 题卡](../questions/proj_robot_harness.html)
- [OPD 题卡](../questions/proj_opd.html)
- [UWM/LIBERO 题卡](../questions/proj_uwm.html)
- [PER-020 题卡](../questions/vol_06_per020.html)
- [VOL 04 WM-025 题卡](../questions/vol_04_world_model_sim2real_wm025.html)
- [VOL 05 ENG-013 题卡](../questions/vol_05_engineering_eval_eng013.html)
- [VOL 08 SYS-VLA-004 题卡](../questions/vol_08_sys004.html)
- [VOL 08 CODE-VLA-004 题卡](../questions/vol_08_code004.html)

## 6. 当前边界与下一步

当前没有真实口述答案，因此：

- 所有 280 张题卡仍为 `unseen`；
- 不创建 `coaching_state.md`；
- 不把 queue 的存在当作练习完成；
- 不把示范回答或题卡内容当作候选人掌握。

下一步只问队首 `PROJ-WAM-001`；可直接填写 [WAM 口述捕获模板](wam_oral_capture_template.html)，收到回答后再进行一次反馈和状态迁移。
