# 五项目串联：从实现证据反推的 VLA 项目总述口述稿

> 状态：`implementation_derived_portfolio_model_answer / evidence_bounded / not_candidate_transcript / unseen`
> 更新日期：2026-07-22
> 适用场景：面试开场“介绍一下你做过的 VLA/具身项目”、项目选型、跨项目追问

## 1. 30 秒总述

> 我的项目经历可以按一条 VLA 工程链来讲，而不是五个互不相关的 demo。Cosmos Policy/WAM 侧重训练入口、在线文本条件和 RoboCasa 闭环评测；UWM/LIBERO 侧重数据窗口、task-specific checkpoint、normalizer 与 episode 分母；OpenPiVLA 侧重多模态 causal fine-tune、LoRA 和 action formatter 的 shape/lineage 风险；Robot Harness 侧重 robot scope、mutex、cancel、compensation 以及 schema-aware reward；OPD 侧重多 expert 数据合同、路由蒸馏和 holdout 评测。我的共同工作方式是先冻结输入输出和评测协议，再从日志、raw artifact 和 first-divergence 定位问题。现有材料能证明实现接入、运行审计和失败诊断，但不能把不同 checkpoint、scorer 或 denominator 拼成跨项目的统一提升。

## 2. 2 分钟主线

> 我会把这五个项目看成从 policy 到 evaluation 再到执行协议的五个切面。
>
> 第一条是 Cosmos Policy/WAM。我接入了 official trainer/model/dataset 路径和 online Reason1 conditioning，处理 placeholder 与 lazy success metadata，另外把 local DCP checkpoint loader 接回 RoboCasa 官方闭环。训练上有一条单卡 full10k run，日志到 step 10000、loss=`0.0543` 并记录了保存成功；另一条 8 卡、global batch 128、`9907`-step 的 1-epoch gate 则先遇到 `cycle(dataloader)` 引起的 CPU cgroup OOM，修复后的 5-step smoke 通过，但正式 run 又在 DeepSpeed `state_dict(destination=...)` 保存接口失败，所以我不会说 1 epoch gate 已完成。评测固定 24 个任务、每任务 5 个 episode、chunk 32、执行前 16 步；full10k 的 trusted 结果是 `0/118`，同一 harness 的 official-HF path 是 `84/118`，这只能缩小排查范围，不能写成训练 uplift。
>
> 第二条是 UWM/LIBERO。我从 HDF5 转 Zarr 的窗口、`process_batch`、DDP trainer 和 epoch-aligned queue 追到 evaluator。这里最容易讲错的是把五个任务说成一个 multi-task checkpoint；实现和日志显示它们使用 task-specific checkpoints，且 evaluator 只读取 `ckpt["model"]`，没有读取 `action_normalizer`。用户确认的 `186/250` 是 summary-level 结果，本地缺 250 条 raw episode 和 checkpoint/hash，因此我把 strict/reset、completed denominator 和 DataLoader stall 分开讲，不把 `232/250` 或 `186/250` 直接解释成模型改进。
>
> 第三条是 OpenPiVLA。当前可核验的 formal path 是 Qwen3-VL + PEFT LoRA + `model(**batch)` 的 full-chat causal cross-entropy；不是 assistant-only CE，也不是已经闭合的 flow-matching loss。代码里 `H=15,D=72` 与 formatter `limit=16` 形成 lossy representation 风险，所以我会优先讲 token/action round-trip、padding-only label mask 和 checkpoint/parser/normalizer/controller lineage，而不会把 `97.4%`、official `96.85%` 与 formal 100k runs 拼成一条因果曲线。
>
> 第四条是 Robot Harness。它解决的是高层工具调用如何绑定到 robot scope 和 request lifecycle：runtime 管 scope、mutex、cancel、timeout、compensation，训练侧把 SFT/GRPO 数据和 schema-aware reward 分开。sandbox 100% 只是结构化协议 proxy；P0 raw primary JSONL 是 `28/40`，exact common support 是 `6/10`，本地可 hash/load 的 checkpoint binary 是 `0/6`，所以 `37.8→95.6` 不能当作严格 GRPO uplift，也不能当作 physical success。
>
> 第五条是 OPD。它围绕五 expert 数据合同、image-hash split、seen/unseen/boundary/format-conflict、coldstart 到 OPD5000、route teacher 和 full-vocabulary KL 展开。实现上必须区分根目录 legacy teacher-rollout/top1-CE trainer 与 `point/` formal trainer；后者才支持 coldstart teacher rollout、OPD5000 student rollout和 \(D_{KL}(q_\beta\|p_S)\)。route metadata 不是 learned router；跨 split image-hash 交集为 0 也不等于 eval 内没有重复图片，更不等于语义泛化。缺 SFT-only、single-teacher、no-synthetic 和 raw prediction 对照时，我只把结果讲成 protocol-fixed descriptive evidence。
>
> 因此这五个项目共同体现的不是“我发明了五个模型”，而是我能把模型输入输出、数据转换、训练合同、checkpoint、controller 和 scorer 串起来，并在失败时报告 first divergence 和证据缺口。

## 3. 项目选择：面试官问什么时优先讲哪一段

| 面试官问题 | 首选项目 | 口述切入点 | 不要越界 |
| --- | --- | --- | --- |
| 训练为什么 OOM、保存为什么失败？ | WAM | `cycle(dataloader)`、no-cycle smoke、`state_dict` first divergence | 不说 1 epoch 已完成 |
| action/normalizer/checkpoint 如何对齐？ | UWM/LIBERO | task-specific checkpoint、`ckpt["model"]`、strict/reset、completed denominator | 不把 summary 当 raw benchmark |
| VLM 到 action token 的训练目标是什么？ | OpenPiVLA | Qwen3-VL、LoRA、full-chat causal CE、`H=15,D=72` 对 formatter 的风险 | 不把 archived flow 当 formal path |
| 如何保证机器人工具调用可取消且不越权？ | Robot Harness | scope → mutex → dispatch/poll → cancel/compensation | 不把 sandbox 分数当物理安全 |
| 多 expert 数据如何路由和蒸馏？ | OPD | 数据合同、route teacher、full-vocabulary KL、holdout split | 不把 route metadata 叫 learned router |
| 你如何证明结果可信？ | 五项目横向 | protocol tuple、raw artifact、checkpoint lineage、scorer、denominator | 不跨项目拼 uplift |

## 4. 共用的实现审计框架

我会按下面六步回答任何一个项目的“你具体怎么做的”：

1. **冻结输入输出**：观测帧、文本/任务条件、action shape、axis/frame/unit、chunk 与执行 prefix。
2. **冻结训练合同**：数据来源与 split、target、mask、normalizer、checkpoint 保存格式和 resume 语义。
3. **冻结运行身份**：代码 revision、配置、模型/Tokenizer/统计量 revision、环境与 seed。
4. **冻结评测协议**：task、init、episode、success predicate、invalid policy、scorer backend 和 denominator。
5. **寻找 first divergence**：先判断是数据、模型 forward、保存/加载、parser/denormalizer、controller 还是 scorer 出现第一处不一致。
6. **分级结论**：把事实、实现推断、候选人 ownership 和仍未验证项分开，不用一个 summary 数字替代整条证据链。

这套框架对应的闭环可以写成：

\[
\text{observation/text}
\rightarrow \text{policy output}
\rightarrow \text{parse/denormalize}
\rightarrow \text{controller/environment}
\rightarrow \text{episode artifact}
\rightarrow \text{scorer + denominator}
\]

其中每个箭头都需要有可复核的 schema 或日志；只看到 loss、视频或 summary，不能自动推出后面的 closed-loop success。

## 5. 横向真实性边界

| 结论类型 | 当前可说 | 当前不能说 |
| --- | --- | --- |
| 项目范围 | “我开展了训练/评测复现、协议对齐、运行审计和失败诊断” | “五个模型都是我独立原创” |
| 训练结果 | “某条 run 到达某 step，并留下相应日志/保存记录” | “有可加载 immutable checkpoint”——除非 binary/hash/reload 已闭合 |
| 指标 | “按某个固定 protocol 重算得到 raw/trusted 结果” | “不同 n、scorer、checkpoint 的数字构成 uplift” |
| 工程能力 | “我能定位 first divergence 并设计下一步 gate” | “一个 smoke 通过就代表长跑、保存和闭环都成功” |
| 机器人能力 | “完成 simulator/offline/interface/proxy 层验证” | “已完成 physical success、Sim2Real 或 real canary” |
| ownership | “按 ledger 说明接入、运行、审计、定位和复核边界” | “Git author、Codex 生成或 upstream 代码自动等于个人原创” |

## 6. 可能的压迫式追问

### “五个项目里哪个最能证明你有 ownership？”

> 我不会用一个项目的 Git author 或生成代码量回答。WAM 最能展示训练/评测协议迁移和 first-divergence 诊断，UWM 最能展示 action/checkpoint/denominator 审计，Harness 最能展示 runtime contract 和安全 proxy，OPD 最能展示数据合同与蒸馏评估。真正的 ownership 需要逐文件、逐命令、逐 artifact 说明我是亲自修改、协作实现、工具辅助、只审查还是只运行；当前若没有候选人逐项确认，我会使用“开展、接入、运行、审计、定位”这些保守动词。

### “你做了这么多项目，为什么没有一个结果能直接证明 uplift？”

> 因为我把可比性当成结果的一部分。WAM 的 full10k 与 8-GPU gate 不是同一 run；UWM 的 summary 缺 raw episode 和 normalizer usage；OpenPiVLA 的 formal causal-CE 与 archived flow/benchmark 不是同一 lineage；Harness 的 scorer、n 和 checkpoint 不完全一致；OPD 缺少关键 ablation。当前最可信的能力信号是把这些断点找出来，而不是用不可比的百分比制造单一结论。下一步如果要证明 uplift，我会先冻结 matched protocol tuple、checkpoint hash、raw per-episode predictions 和 paired rerun。

### “如果只能留一个项目讲，你怎么选？”

> 如果岗位偏训练与评测，我选 WAM，因为它同时覆盖训练入口、OOM、checkpoint save、RoboCasa 闭环和失败诊断；如果岗位偏数据/蒸馏，我选 OPD；如果岗位偏机器人系统和安全，我选 Harness；如果岗位偏 action representation，我选 UWM 或 OpenPiVLA。选择依据是问题与岗位的匹配，不是哪个项目的百分比更大。

## 7. 面试前的最小补强清单

1. 为每个项目补一个 run-specific immutable bundle：配置、代码 revision、checkpoint SHA、stats/tokenizer、eval command、raw episode JSONL 和 scorer 版本。
2. 为每个项目确认个人 ownership：亲自修改、协作修改、工具辅助、仅审查、仅运行五类至少各有一条证据。
3. 只为一个最重要的结论做 matched paired rerun；不要同时声称五个项目都有 uplift。
4. 练习同一项目的 30 秒、2 分钟和 10 分钟版本；回答中始终保留“结果、失败、边界、下一步”四个位置。

## 8. 证据入口

- [WAM implementation-derived oral answer](wam_oral_model_answer.html)
- [UWM/LIBERO implementation-derived oral answer](uwm_oral_model_answer.html)
- [OpenPiVLA implementation-derived oral answer](openpivla_oral_model_answer.html)
- [Robot Harness implementation-derived oral answer](robot_harness_oral_model_answer.html)
- [OPD implementation-derived oral answer](opd_oral_model_answer.html)
- [首轮口述队列](oral_drill_queue.html)
- [通用口述 capture template](oral_drill_capture_template.html)

> 本页是从项目实现、日志和 evidence inventory 反推的示范口述，不是候选人真实 transcript；所有项目题卡仍保持 `unseen`，不得据此创建或更新 `coaching_state.md`。
