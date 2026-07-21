# OpenPiVLA ALOHA Action-Level Eval：Checkpoint Load / Serve / L1 Gate

> 状态：`local-direct / log-hash-frozen / official-action-eval / task-success-not-proven / WARN`
> 审查日期：2026-07-21
> 范围：`C:\Users\mousongzhe\project\openpivla_deployment\artifacts\lerobot_action_eval_aloha_sample_real_v2` 与对应 scripts。
> 结论先行：ALOHA LeRobot action-level eval 的 server log 直接确认官方 `pi0_aloha_sim` checkpoint 被 Orbax 恢复约 6.0 GiB、17.31 秒完成，norm stats 从 checkpoint assets 加载，server 在 8020 监听并接受 client；summary 冻结 4 个样本、每个 50 步、14D action 的 mean L1 `0.0330713950`、std `0.0205169544`。这是 action-vector 对齐/部署 harness 证据，不是 task-level success、fine-tune 成绩或泛化 benchmark。

## 1. Evidence freeze

| ID | 本地对象 | SHA-256 | 直接支持 |
| --- | --- | --- | --- |
| A01 | `artifacts\lerobot_action_eval_aloha_sample_real_v2\serve.log` | `F02D0E4D08D6879C2F080B3DA905B4EA11A73B7510B7D8867785FFD1384A0868` | `pi0_aloha_sim` restore、6.0 GiB、17.31 s、norm stats、8020 listen、localhost connection |
| A02 | `artifacts\lerobot_action_eval_aloha_sample_real_v2\summary.json` | `D367885AFB621469C81CB885C53FD36A87F02F06B8F4ED9B854F32BDB6663BAC` | official WebsocketClientPolicy、dataset/config/checkpoint 字段、4×50、14D、L1 统计 |
| A03 | `scripts\eval_lerobot_action_server.py` | `B1B7FB9B7A86355B9C1843CDE971B38FD26A2DAB1F18550128671F79F1AB4F39` | parquet/action window、image/state request、client infer、L1 计算与 summary writer |
| A04 | `scripts\run_lerobot_action_eval.sh` | `61DFE972B20722CF08B3FA139D68B29B6C1B52286671A7705000AE3738A8BF60` | config/checkpoint/port/action-horizon 的 launch 参数与 server/client 顺序 |
| D01 | `DEPLOYMENT.md` | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14E` | deployment provenance、official checkpoint 与 action-eval 边界 |

本页不复制远端权重、parquet 或图片，只冻结本地日志、summary 与脚本 hash。

## 2. Server load / client connection

`A01` 的关键顺序是：

```text
Restoring checkpoint from .../checkpoints/pi0_aloha_sim/params
total bytes: 6.0 GiB
Finished restoring checkpoint in 17.31 seconds
Loaded norm stats from .../checkpoints/pi0_aloha_sim/assets/lerobot/aloha_sim_transfer_cube_human
server listening on 0.0.0.0:8020
Connection from ('127.0.0.1', 40058) opened
Connection ... closed
```

这条日志比 summary 里的 checkpoint 字符串更强，因为它记录了 restore 的执行事件、读取体量、normalizer 路径与 WebSocket 生命周期。它与 [LIBERO Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html) 形成两个 task-specific official checkpoint load 样本：`pi0_aloha_sim` 与 `pi05_libero`。

但 A01 仍不等价于 immutable binary manifest：没有 `params` 目录逐文件 SHA、object-store revision、processor/tokenizer hash 或 shared run UUID。

## 3. Action-level eval contract

`A03` / `A04` 支持的流水线是：

```text
LeRobot parquet row
  -> state/action/image fields
  -> WebsocketClientPolicy(host=127.0.0.1, port=8020)
  -> predicted action chunk
  -> align with GT action window
  -> per-sample L1 + norm statistics
  -> summary.json / dashboard / plots
```

本地脚本中可直接核对的字段与边界：

| 项目 | 证据 | 边界 |
| --- | --- | --- |
| dataset | `lerobot/aloha_sim_transfer_cube_human` 的 sample copy | 只取本地 sample parquet，不等于全量 benchmark |
| checkpoint/config | `pi0_aloha_sim` 与 official checkpoint path | server restore direct；binary SHA 缺失 |
| sample count | 4 | 四个采样点来自 episode 0 的 row 0/50/100/150 |
| action window | horizon 50 | 这是离线 action comparison，不是环境执行 50 步 |
| action dimension | 14 | summary 与 script compare shape direct；不推断 task controller semantics |
| image/state request | `observation.images.top`、state key，wrist placeholders 按脚本构造 | 数据字段/预处理可复核；完整 camera calibration 未闭合 |
| metric | per-sample absolute error 的 mean L1 | 不等价 reward/success 或 closed-loop success |

L1 的实现语义可以写成：

\[
\operatorname{L1}_{i}
=
\frac{1}{H D}
\sum_{h=1}^{H}\sum_{d=1}^{D}
\left|\hat a_{i,h,d}-a_{i,h,d}\right|
\]

其中 (i) 是 sample，(H=50) 是 action horizon，(D=14) 是比较维度，(hat a) 是 server 返回动作，(a) 是 parquet 中的 GT action window。直觉上，它只回答“预测 action vector 与离线标签在数值上有多近”；实现映射来自 `A03` 的 `compare_horizon`、`compare_dim` 与逐元素 absolute error。它不包含环境状态转移、接触、终止或 success predicate。

## 4. Frozen result and comparability

| sample | row/frame | L1 | predicted norm | GT norm |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 0 / 0 | `0.0678215474` | `2.0785110` | `2.1135752` |
| 1 | 50 / 50 | `0.0227967594` | `2.18176198` | `2.21180510` |
| 2 | 100 / 100 | `0.0148706269` | `2.14331412` | `2.14696836` |
| 3 | 150 / 150 | `0.0267966483` | `2.04372430` | `2.08739448` |
| aggregate | 4 samples | mean `0.0330713950`, std `0.0205169544` | — | — |

这组数字可以安全表述为：

> “我通过官方 OpenPI WebSocket server 对 ALOHA LeRobot sample 做了 4 个 action-window 对齐检查，每个窗口 50 步、14 维，mean L1 是 0.03307；同时保留了 server restore、norm stats 与 client connection log。”

不能表述为：

- ALOHA task success rate 或官方 benchmark score；
- 训练后模型的结果；
- 4 个 sample 代表完整数据集泛化；
- L1 较低就证明 controller/axis/unit/normalizer 全部正确；
- 与 LIBERO `0/1` 或 ALOHA true-physics `2/3` 直接做 uplift 比较。

## 5. Pseudocode mapping

```python
def offline_action_eval(parquet, policy_client, row_indices, horizon):
    # 1. Read one LeRobot row and its future GT action window.
    for row_index in row_indices:
        row = parquet[row_index]
        gt = stack_future_actions(parquet, row_index, horizon)

        # 2. Build the official OpenPI observation request from image/state fields.
        request = build_openpi_observation(row)

        # 3. Query the WebSocket policy server for a predicted action chunk.
        pred = policy_client.infer(request)["actions"]

        # 4. Compare only the common horizon and dimensions; do not step a simulator.
        pred_cmp, gt_cmp = align(pred, gt, horizon=horizon)
        l1 = abs(pred_cmp - gt_cmp).mean()
        save_sample_metrics(row_index, l1, pred_cmp, gt_cmp)

    # 5. Aggregate mean/std and write summary.json and plots.
    return write_action_eval_summary()
```

此伪代码只抽象 `A03` 的离线 action comparison；它明确没有 `env.step`、controller、reward 或 success scorer。

## 6. Interview boundary

### 30 秒回答

“除了 true-physics rollout，我还把官方 `pi0_aloha_sim` 接到 LeRobot action-eval harness，先验证 server load、normalizer、WebSocket client 和 action parsing 是否闭环。4 个 sample、每个 50 步、14D action 的 mean L1 是 0.03307，std 是 0.02052。它只能说明离线 action-vector 对齐和部署链路可运行，不是 task success，也不是我训练出的 checkpoint；要升级到 benchmark，还要补完整 task matrix、controller、success scorer 和 immutable checkpoint manifest。”

### 高频追问

1. **为什么 L1 不是成功率？** 因为没有环境状态转移和终止条件，只比较预测 chunk 与 parquet GT。
2. **为什么 summary checkpoint 字段不够？** 因为 A01 的 server restore 才证明真正加载了 `pi0_aloha_sim/params`。
3. **14D 是什么？** 是该 action comparison 的共同 tensor 维度；本页不把它解释成某个真实 controller 的 axis/unit contract。
4. **能否与 LIBERO 0-success 对比？** 不能直接比较；一个是离线 L1、一个是 task-level physics rollout，协议层级不同。
5. **下一步是什么？** 固定 action axis/order/unit、normalizer、controller 和 success scorer，再做 matched closed-loop probe。

## 7. 公源 / 本地 / 未核实边界

| 类型 | 当前内容 |
| --- | --- |
| public / official-code | OpenPI WebSocket policy server/client、官方 `pi0_aloha_sim` config/checkpoint convention |
| local evidence | A01–A04 的 hash、4×50×14 action comparison、L1/norm summary |
| local inference | server restore + summary + launch script 共同支持一次 action-eval pipeline 的运行链 |
| unverified | checkpoint binary SHA、processor/tokenizer revision、完整数据集覆盖、controller semantics、个人 ownership、fine-tune lineage |

## 8. 下一步

1. 把 `pi0_aloha_sim` 与 `pi05_libero` 的 params/assets 生成逐文件 manifest，并绑定 OpenPI commit、processor/tokenizer revision。
2. 记录 server/client exact argv、UTC timestamp、shared run UUID 与 request IDs。
3. 用相同 action contract 做 matched LIBERO diagnostic probe，再连接 task-native controller/scorer。
4. 本页已作为诊断来源加入 `PROJ-OPENPIVLA-007`；题卡仍保持 `unseen`。

## 参考文献（References）

1. Local action-eval server log（A01）。
2. Local action-eval summary（A02）。
3. Local evaluator script（A03）与 launch script（A04）。
4. Local deployment record（D01）。
5. [OpenPiVLA Runtime Rollout Artifact Gate](openpivla_runtime_rollout_artifact_gate.html)。
6. [OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html)。
