# VOL 08 SYS-001 原子题卡：可复现的 VLA 训练—评估平台

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-18  
> 覆盖范围：`SYS-VLA-001`  
> 难度：L3 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[SYS-001 Knowledge](../knowledge/vol_08_sys001_vla_training_eval_platform.html)；来源边界见 [SYS-001 Source Freeze](../sources/vol_08_sys001_vla_training_eval_platform_source_freeze.html)。

## 设计可复现的 VLA 训练—评估平台

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>SYS-VLA-001</b> · 如何设计一个可复现的 VLA 训练—评估平台，避免数据、checkpoint、评估协议和 rollout 互相污染？</summary>

**面试意图**：判断你能否把数据版本、训练 lineage、模型 bundle、评估 tuple、episode artifact 和安全边界串成系统，而不是只画 trainer/server 方框。

**30 秒回答**：画五层 lineage：dataset→run→bundle→fixed eval→episode artifact。冻结 schema、seed、processor/normalizer、checkpoint、scorer、分母；offline/sim/real 分 namespace。缺 trace/hash，只讲接口，不称平台或 benchmark。

**机制展开（约 2 分钟）**：五类 manifest：dataset 记 episode/frame/unit/mask/split/hash；run 记 code/config/seed/rank/model/processor/normalizer；bundle 做 load/hash gate；eval 固定 task/init/seed/horizon/success/scorer/分母；rollout 存 action trace、latency、terminal reason，分 train/offline/sim/real/proxy。项目仅局部证据，缺 registry、bundle hash、raw rollout、ownership，不能把 loss、远端 summary 或脚本写成平台。

**诊断 / 证据**：先对固定 sample 做 processor→model→decode→denorm→schema roundtrip，检查 shape、dtype、finite、range 和 parser；再用冻结 holdout 复算 offline metric；最后按同一 checkpoint/bundle 运行 simulator 或 real rollout，保存逐 episode trace、terminal reason、latency、scorer 和 denominator。用 dataset split、normalizer swap、checkpoint load、init/seed replay 做 first-failure 分层；缺 raw bundle 时保持 `WARN`。

**项目挂钩**：OpenPiVLA 可连接 formal trainer、recipe、action packaging 和 timeout hook；UWM/LIBERO 可连接 task mapping、fixed/reset protocol、normalizer/action shape 与 DataLoader stall；WAM 可连接 rollout provenance；Robot Harness 可连接 timeout/cancel/compensation；OPD 可连接 split、raw holdout 和 strict scorer。安全表达是“我能设计 lineage 和验证门”，不把局部脚本、远端 summary 或上游框架写成个人完成的平台。

**追问树**：为什么 checkpoint path 不能证明权重相同？normalizer 放在 bundle 哪一层？offline MSE 与 simulator success 如何分 namespace？如何防相邻 window 泄漏？mid-epoch resume 需要保存什么？没有 episode JSONL 时能否报成功率？怎样区分 protocol change 与 model uplift？

**易错点**：只固定 seed；忽略 processor/normalizer/action schema；把 simulator summary 当 real result；把 report-supported 数字当 local-direct；用单卡 smoke 证明分布式复现；覆盖 latest checkpoint 导致 lineage 丢失。

**危险答案**：说“有 checkpoint 就能复现”“固定随机种子即可 bitwise identical”“loss 降了所以 success 一定升”“一个 summary JSON 足以证明 benchmark”或“OpenPiVLA/UWM 脚本就是我搭建的完整平台”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [SYS-001 Knowledge](../knowledge/vol_08_sys001_vla_training_eval_platform.html)：dataset/run/bundle/eval/rollout contract、failure tree 与项目边界。
2. [SYS-001 Source Freeze](../sources/vol_08_sys001_vla_training_eval_platform_source_freeze.html)：PyTorch DCP/reproducibility、Open X、LIBERO、OpenPI 与本地 evidence inventory。
3. PyTorch [Distributed Checkpoint](https://docs.pytorch.org/docs/2.13/distributed.checkpoint.html) 与 [Reproducibility](https://pytorch.org/docs/stable/notes/randomness.html)。
4. [Open X-Embodiment](https://github.com/google-deepmind/open_x_embodiment/tree/9eeb68b989efbcf474e8fb9019e01d02b962a604)、[LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO/tree/8f1084e3132a39270c3a13ebe37270a43ece2a01)、[OpenPI policy interface](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/policy.py)。
