# VOL 04 World Model / Sim2Real：WM-017 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-WM-017`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[WM-017 Heterogeneous Embodiment Schema](../knowledge/vol_04_world_model_sim2real_wm017.html)；来源边界见 [WM-017 Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)、[Open X frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md) 与 [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)。本题只讲 schema/代码审计，不绑定用户项目强 claim。

## 异构机器人如何统一 schema 而不污染 world loss

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-WM-017</b> · heterogeneous robots 的 camera、state、action 和 horizon 如何统一而不污染 world loss？</summary>

**面试意图**：判断你能否区分统一 episode container 与统一 action/camera 语义，并能把 valid/presence mask、normalizer、timestamp 和 loss reduction 串成证据链。

**30 秒回答**：统一 RLDS 容器和 metadata，不强行统一语义。冻结 camera/frame、action 模式、timestamp、horizon、normalizer、valid/presence mask；padding 不能进 world loss。再做 round-trip、terminal-mask A/B 和分 embodiment 评估。

**机制展开（约 2 分钟）**：RLDS 只统一 episode/step 容器，不统一 camera、action 或 horizon。adapter 要记录字段语义、坐标、control Hz、history/future、gripper 和 stats SHA；缺 camera 用 presence mask，padding 用 valid-step mask，loss 按有效元素 reduction。UWM 的 LIBERO [7]、DROID [10] 说明 7D/10D 与 `action_len=16` 不是通用常数。验证 round-trip、terminal-mask A/B、camera ablation 和 per-embodiment success。

**诊断 / 证据**：保存 source/embodiment id、camera presence、frame transform、timestamp、shape、unit、normalizer SHA、valid-step mask、target denominator 和分层指标；检查 repeated terminal、zero-padding、action axis/gripper、camera flip 与 control frequency。

**项目挂钩**：UWM/LIBERO 可讲 action/history/normalizer/reset/checkpoint/rollout protocol 核对；OpenPiVLA、WAM、Harness 的 camera/action schema 要回到各自 config、processor、controller 与 wrapper。不能把 Open X 的公开容器说成本地已完成统一，也不能用混合 loss 下降证明跨机器人 success 提升。

**追问树**：RLDS 统一了什么、没统一什么？为什么 7D action 不能当通用常数？missing camera 为什么要 presence mask？terminal padding 如何污染 world loss？absolute/delta/velocity 怎样判断？horizon 与 control Hz 如何对齐？如何设计 per-embodiment ablation？

**易错点**：只 zero-pad 不留 mask；把 index 当 timestamp；忽略 gripper/rotation semantics；共享一个 normalizer；把 workspace/wrist camera 混写；只看混合平均 loss；把上游数据转换说成个人工程成果。

**危险答案**：说“RLDS 已统一所有机器人语义”“action 都是 7D”“padding 不影响 loss”“同一 normalizer 可覆盖所有数据”“混合 loss 下降就证明跨 embodiment 泛化”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [WM-017 知识页](../knowledge/vol_04_world_model_sim2real_wm017.html)：schema 七层合同、mask、normalizer、horizon 与 loss 防污染。
2. [WM-017 Source Freeze](../sources/vol_04_wm017_heterogeneous_schema_source_freeze.html)：Open X/UWM source fingerprint 与待验证队列。
3. [Open X frozen README](https://github.com/google-deepmind/open_x_embodiment/blob/9eeb68b989efbcf474e8fb9019e01d02b962a604/README.md)：RLDS、RT-1-X camera/task/action 说明与许可边界。
4. [UWM Source Audit B](../sources/vol_04_uwm_video_action_claim_to_code.html)：LIBERO/DROID shape、action_len、normalizer 与数据合同。
