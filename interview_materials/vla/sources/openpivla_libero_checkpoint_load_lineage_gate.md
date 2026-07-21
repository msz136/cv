# OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate

> 状态：`local-direct / log-hash-frozen / checkpoint-load-confirmed / binary-unverified / WARN`
> 审查日期：2026-07-21
> 范围：`C:\Users\mousongzhe\project\openpivla_deployment` 中 `libero_franka_true_rollout_v1` 的 server/client log、rollout script 与部署记录。
> 结论先行：本地 `serve.log` 直接证明 **Orbax 从官方 `pi05_libero/params` 路径恢复了约 6.2 GiB 参数、从 checkpoint assets 加载 normalization stats、启动 WebSocket server 并接受 localhost client 连接**；同目录 `client.log` 与 `summary.json` 记录了随后完成的 LIBERO task-0 70-step model/no-op rollout。该证据关闭了“是否真的 load 并 serve 官方 checkpoint”的主要疑问，但仍没有 checkpoint 文件级 manifest/SHA、精确启动命令、processor/tokenizer revision、run UUID 或私有 LoRA checkpoint，因此不能升级为 fine-tune lineage、完整可重复 benchmark 或个人 ownership。

## 1. Question 与证据目标

上一份 [Runtime Rollout Artifact Gate](openpivla_runtime_rollout_artifact_gate.html) 已冻结 ALOHA `2/3`、多视角 `1/2` 与 LIBERO task-0 `0/1`，但当时只有 summary 中的 checkpoint 字段，尚未直接读取 checkpoint restore 和 server/client 连接日志。本页只回答四个问题：

1. server 是否真正从 `pi05_libero` checkpoint 恢复参数；
2. normalization stats 是否随相同 checkpoint lineage 被加载；
3. server 是否监听、client 是否连接、rollout 是否产生结果；
4. 这组日志仍缺哪些内容，因而不能支持哪些强 claim。

本页不重新运行远端训练或评估，不复制权重，也不把部署日志改写成候选人的算法贡献。

## 2. Immutable evidence freeze

| ID | 本地对象 | SHA-256 | 直接支持 |
| --- | --- | --- | --- |
| L01 | `artifacts\libero_franka_true_rollout_v1\serve.log` | `FF0B39D7B87D604D86486A0088E7CF7FD2D3EA99CB151B99FD5D9B9E60AACD2A` | Orbax version、checkpoint restore path/bytes/time、norm stats path、listen port、client connection |
| L02 | `artifacts\libero_franka_true_rollout_v1\client.log` | `BC1B7FE6E54735B4623062D151D47667BD418F4F7A46B6CC471EC1F961869572` | LIBERO task/config/checkpoint summary、70-step model/no-op run、reward/success/result filenames |
| C01 | `scripts\run_libero_true_rollout.py` | `1C7F74DE83FD373A27FEDC70D863D5F0BF164B4512ED63E1D76552A0F22C3016` | observation schema、state transform、image preprocessing、action slice/replan、environment step 与 summary writer |
| D01 | `DEPLOYMENT.md` | `C0A3DD0C0DA8C1C0D36023046D5337900A71680B413657BC9B1062EEF2EEA14E` | remote directory、OpenPI recorded commit `c23745b`、official checkpoint inventory、环境与结果边界 |

`summary.json` 已在 Runtime Rollout Artifact Gate 中冻结为 `341E77110D75E50B601A078923F51EF8FA39AAA045FA491843A1003B0320E1DB`。本页新增冻结的关键对象是 `serve.log`、`client.log` 与 rollout script。所有路径均指向用户本地项目目录，未把权重或运行产物复制进面试仓库。

## 3. Server-side checkpoint load chain

`L01` 的顺序证据为：

```text
Loading model...
orbax-checkpoint version: 0.11.13
Restoring checkpoint from .../checkpoints/pi05_libero/params
read total bytes: 6.2 GiB
Finished restoring checkpoint in 17.00 seconds
Norm stats not found in official source assets path, skipping
Loaded norm stats from .../checkpoints/pi05_libero/assets/physical-intelligence/libero
server listening on 0.0.0.0:8399
Connection from ('127.0.0.1', 46490) opened
```

这比 summary 的字符串字段更强：它记录了 Orbax restore 的执行、读取体量和完成事件，也把 normalization stats 定位到同一 checkpoint 根目录的 assets。可审计的运行身份可写成：

\[
I_{\mathrm{serve}}
=
(P_{\mathrm{params}}, P_{\mathrm{norm}}, V_{\mathrm{orbax}}, B_{\mathrm{read}}, T_{\mathrm{restore}}, H, p)
\]

变量解释：`P_params` 是 `/pi05_libero/params`，`P_norm` 是 checkpoint 内的 `assets/physical-intelligence/libero`，`V_orbax=0.11.13`，`B_read≈6.2 GiB`，`T_restore=17.00 s`，`H` 是日志中的容器 host，`p=8399`。直觉上，这个 tuple 绑定的是“这次 server 进程加载了什么并监听在哪里”；它来自本地 log 的直接证据，而不是从 summary 反推。

仍不能把它称为 immutable checkpoint manifest：本地没有 `params` 目录的逐文件列表、总 SHA/Merkle root、对象存储 revision 或下载 manifest。路径一致和 restore success 能证明可加载性，不能证明远端目录之后绝不会被替换。

## 4. Client 与 rollout contract

`C01` 说明 client 不是只发一个空请求，而是按以下 contract 构造 policy observation：

| 字段 | 来源与变换 | 当前证据边界 |
| --- | --- | --- |
| `observation/image` | `agentview_image` 双轴翻转，再 resize-with-pad 和 uint8 转换 | script direct；本次 invocation 的原始图像 hash 未保存 |
| `observation/wrist_image` | `robot0_eye_in_hand_image`，同样翻转、resize、uint8 | script direct |
| `observation/state` | eef position + quaternion-to-axis-angle + gripper qpos | script direct；axis/unit 的独立 round-trip 未做 |
| `prompt` | LIBERO task language | script direct；summary 固定了 task-0 文本 |
| `actions` | `client.infer(...)["actions"]`，取前 `replan_steps` 行、前 7 维入队 | script direct；server-side action tensor trace 未落档 |

脚本默认 `resize_size=224`、`replan_steps=5`、`seed=7`，但 `client.log` 没有打印完整 `argv`，所以这些只能说明 **代码默认值**，不能冒充本次 run 的精确 effective config。summary 直接支持本次执行为 task 0、70 steps、model/no-op 都是 `0.0 reward / false success`。

```python
def observed_rollout_contract(obs, task_text, client, replan_steps):
    # 1. 从 LIBERO 观测构造 agent/wrist image、8D state 与语言提示。
    request = build_libero_request(obs, task_text)

    # 2. WebSocket client 请求 action chunk；本地日志证明 server 已接受连接。
    chunk = client.infer(request)["actions"]

    # 3. 只执行 chunk 的前 replan_steps × 7D，再重新请求。
    for action in chunk[:replan_steps, :7]:
        obs, reward, done, info = env.step(action.tolist())
        if done:
            break
```

伪代码是 `C01` 的紧缩映射。它不补造本次 invocation 未打印的 `replan_steps`，也不声称 client 侧的 `--checkpoint` 字段控制了 server；真正的 checkpoint 绑定来自 `L01` 的 server restore path。

## 5. Same-run binding 强度

完整的可重复 run identity 至少需要：

\[
I_{\mathrm{run}}
=
(R_{\mathrm{code}}, M_{\mathrm{checkpoint}}, N_{\mathrm{stats}}, A_{\mathrm{argv}}, O_{\mathrm{request}}, E_{\mathrm{env}}, S_{\mathrm{scorer}}, Y_{\mathrm{raw}})
\]

变量解释：`R_code` 是代码 revision，`M_checkpoint` 是不可变 checkpoint manifest，`N_stats` 是 normalization asset，`A_argv` 是精确启动参数，`O_request` 是 observation/action contract，`E_env` 是环境和 init state，`S_scorer` 是成功判定，`Y_raw` 是逐步输出。当前 bundle 对 `N_stats`、部分 `O_request`、任务级 `E_env` 和 summary `Y_raw` 有直接证据；对 `M_checkpoint` 只有 path+restore、对 `R_code` 只有部署记录中的 commit、对 `A_argv` 和 server-side raw request/response 不完整。

| Gate | 当前状态 | 证据 | 限制 |
| --- | --- | --- | --- |
| checkpoint load | `PASS WITH WARNING` | Orbax restore 6.2 GiB、17 s、明确 params path | 无逐文件 SHA / immutable manifest |
| normalizer load | `PASS WITH WARNING` | 从 checkpoint assets 明确加载 | stats 内容与 SHA 未冻结 |
| server ready | `PASS` | 监听 `0.0.0.0:8399` | 无 readiness probe latency/SLO |
| client connection | `PASS WITH WARNING` | localhost connection opened；同目录 client log 有结果 | 无 shared run UUID、无带时间戳 request ID |
| observation/action contract | `PASS WITH WARNING` | 本地 script hash 与字段/切片逻辑 | invocation argv 与 server response trace 缺失 |
| success scorer | `WARN` | script 以 `done` 聚合 success | 无独立 scorer/version；`last_info={}` |
| private fine-tune lineage | `UNVERIFIED` | 无 | official `pi05_libero` 不能替代 LoRA/Qwen checkpoint |
| ownership | `PENDING` | 无候选人口述和 pre-snapshot diff | 不能使用个人端到端 ownership 口径 |

## 6. 面试安全口径

### 30 秒回答

“我没有把 summary 里的 checkpoint 字符串当作已经加载的证明，而是继续核对了 server/client log。server 侧 Orbax 0.11.13 确实从官方 `pi05_libero/params` 恢复了约 6.2 GiB 参数，17 秒完成，又从 checkpoint assets 加载了 LIBERO normalization stats，随后在 8399 端口接受了 localhost client。client 脚本把 agent view、wrist view、eef/gripper state 和 task prompt 发给 policy server，并执行返回 action chunk 的 7D 前缀。这个闭环能证明官方 checkpoint 的 load、serve 和 rollout 路径，但没有 checkpoint 文件级 SHA、精确 argv 和私有 LoRA lineage，所以我不会把它说成自己的 fine-tune 成绩；本次 task-0 结果也仍是 0 reward、false success。”

### 高频追问

1. **如何证明 client 连接的是这次 server？** 同目录 server log 记录 localhost connection，client log 紧接着保存任务 summary；这是强运行证据，但没有 shared run UUID/request ID，所以仍标 `PASS WITH WARNING`。
2. **为什么 summary 的 checkpoint 字段不够？** client script 只是把 `--checkpoint` 文本写入 summary；真正控制模型的是 server 进程，因此必须看 server restore log。
3. **normalizer 是否确认？** 确认了加载路径和成功事件；未冻结 stats 文件 hash/内容，故不能主张完整 immutable bundle。
4. **这能否证明私有 fine-tune？** 不能。日志加载的是官方 `pi05_libero`，与 Qwen3-VL LoRA formal trainer 是不同 lineage。
5. **0 success 的根因是什么？** 仍未知。action axis/unit、controller、camera preprocess、replan 参数和 scorer 需要 matched probe；本页只关闭 load/serve 疑问。

## 7. 下一步

1. 在远端只读生成 checkpoint manifest：逐文件 path/size/SHA、norm stats SHA、OpenPI commit、processor/tokenizer revision。
2. 启动时保存 server/client 完整 argv、effective config、UTC timestamp、run UUID，并让每个 request/summary 携带同一 ID。
3. 做一组 matched LIBERO diagnostic probe，固定 observation keys、resize/flip、state axis/unit、7D action order、replan interval、controller 与 success scorer。
4. 本页证据已映射到 `PROJ-OPENPIVLA-007`；该卡仍保持 `unseen`。下一切片优先补 immutable manifest，或执行 matched LIBERO failure probe。

## 参考文献（References）

1. Local server log：`C:\Users\mousongzhe\project\openpivla_deployment\artifacts\libero_franka_true_rollout_v1\serve.log`（L01）。
2. Local client log：同目录 `client.log`（L02）。
3. Local rollout implementation：`C:\Users\mousongzhe\project\openpivla_deployment\scripts\run_libero_true_rollout.py`（C01）。
4. Local deployment record：`C:\Users\mousongzhe\project\openpivla_deployment\DEPLOYMENT.md`（D01）。
5. [OpenPiVLA Runtime Rollout Artifact Gate](openpivla_runtime_rollout_artifact_gate.html)。
6. [OpenPiVLA formal JSON/CE artifact gate](openpivla_formal_json_ce_shape_contract_artifact_gate.html)，用于区分 private formal trainer 与 official deployment lineage。
