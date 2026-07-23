# OpenPiVLA / LIBERO Matched Failure Probe Readiness Gate

> 状态：`local-summary-video-timeline-consistent / probe-not-rerun / raw-trace-missing / WARN`
> 审查日期：2026-07-22
> 范围：`C:\Users\mousongzhe\Project\openpivla_deployment\artifacts\libero_franka_true_rollout_v1` 的 summary、server/client log、rollout script 与已生成视频/指标图。
> 结论先行：本轮只使用本地文件，对现有 LIBERO model/no-op bundle 做了可重算的 preflight 与视频时间线审计：9/9 summary/file 检查通过，两条视频均为 71 帧、10 FPS、7.1 秒；前 10 帧共享 dummy warm-up，之后 model branch 出现非零变化 action、机械臂向碗区运动，画面与 state/action norm 明显偏离 no-op，但 70 步内 reward/success 始终为 0，未完成抓取—放置。这足以排除“全程只执行 dummy / 仿真完全没动”，仍不足以把失败单因归到 preprocess、axis/unit、normalizer、controller、scorer 或 policy。

## 1. Question 与边界

前两页已经冻结了官方 `pi05_libero` 的 load/serve/client lineage 与本地 checkpoint 文件缺口。本页只回答：

1. 已归档的 model/no-op rollout 是否在同一个 task/episode/horizon 上可重算；
2. 哪些 observation/action/termination contract 可以从本地 script 直接恢复；
3. 还缺哪些原始 trace，才能执行一个真正的 matched failure probe。

“matched”在本页中不是“两个 summary 看起来相似”，而是至少固定以下 tuple：

\[
P_{mathrm{match}}=(T, I, S, O, A, N, R, C, G)
\]

其中 `T` 是 task suite/id，`I` 是 init-state/episode，`S` 是 seed，`O` 是 observation keys 与图像变换，`A` 是 action order/dimension/unit，`N` 是 normalizer/checkpoint assets，`R` 是 replan/warm-up，`C` 是 controller/environment step，`G` 是 success scorer。变量与代码映射：`T/I/S` 来自 `run_libero_true_rollout.py` 的 benchmark/task/init-state/seed 入口，`O/A/R` 来自 `_policy_action` 与 `deque` 逻辑，`C/G` 来自 `_run_episode` 的 `env.step` 与 `done` 聚合；当前 bundle 只完整落档了部分 tuple，未满足全部 matched 条件。

本页不连接或改动远端，不复制 checkpoint，不把本地视频后验观察当作失败根因，也不更新题卡 mastery。

## 2. Immutable evidence freeze

| ID | 本地对象 | SHA-256 | 直接支持 |
| --- | --- | --- | --- |
| S01 | `artifacts/libero_franka_true_rollout_v1/summary.json` | `341E77110D75E50B601A078923F51EF8FA39AAA045FA491843A1003B0320E1DB` | task tuple、70-step runs、reward/success、norm summary、artifact names |
| S02 | `artifacts/libero_franka_true_rollout_v1/serve.log` | `FF0B39D7B87D604D86486A0088E7CF7FD2D3EA99CB151B99FD5D9B9E60AACD2A` | Orbax restore、checkpoint path、norm-stats load、8399 listen/connection |
| S03 | `artifacts/libero_franka_true_rollout_v1/client.log` | `BC1B7FE6E54735B4623062D151D47667BD418F4F7A46B6CC471EC1F961869572` | client-side summary/log warnings；没有完整 argv |
| C01 | `scripts/run_libero_true_rollout.py` | `1C7F74DE83FD373A27FEDC70D863D5F0BF164B4512ED63E1D76552A0F22C3016` | observation transform、state/action contract、episode loop、scorer wiring |
| V01 | `artifacts/libero_franka_true_rollout_v1/zero_reference/zero_reference_rollout.mp4` | `27BFAB393ECF92E3092D768A6294759287D6F779527EEEB2CE6160F26E7063FA` | no-op visual rollout artifact |
| V02 | `artifacts/libero_franka_true_rollout_v1/model_policy/model_policy_rollout.mp4` | `B8C14912B1202085581286B05949D8957A5AA77E040AE52AB91FFC0F67A60ED6` | model visual rollout artifact |
| V03 | `artifacts/libero_franka_true_rollout_v1/zero_reference_vs_model.mp4` | `226953734221483E03B509C03AE997B98C256722B9281A78A39C86D226D2ECE1` | paired visualization，不等于 paired causal experiment |
| P01 | `artifacts/libero_franka_true_rollout_v1/model_policy/model_policy_metrics.png` | `D5EDB3193BCD2257771304CA97CB226A55CA0567267A9CC209DAC810D7C7CC28` | model reward/action-norm/state-norm/success 曲线 |
| P02 | `artifacts/libero_franka_true_rollout_v1/zero_reference/zero_reference_metrics.png` | `0214FC58F66A3CEFFB9A4B2F652369F76F9C3620E96ED4EF8D06FE5443ED4020` | dummy-reference 同口径曲线 |

## 3. Local preflight audit

使用 Python 标准库读取 `S01`，按脚本相对目录规则检查结果引用；没有修改项目文件。审计结果如下：

| Check | Result | Evidence |
| --- | --- | --- |
| `status == ok` | `PASS` | `summary.json` |
| task tuple | `PASS` | `libero_spatial / task_id=0 / episode_idx=0` |
| run labels | `PASS` | exactly `zero_reference` and `model_policy` |
| matched horizon | `PASS` | both `steps_executed=70` |
| reward consistency | `PASS` | both `total_reward=0.0` and `mean_reward=0.0` |
| termination boundary | `PASS` | both `success=false`, `done=false` |
| finite scalar metrics | `PASS` | action norm/state norm fields finite |
| success-rate recomputation | `PASS` | `success_rate=0.0` equals mean of run success flags |
| referenced artifacts | `PASS` | per-run video/plot and comparison video paths exist |

这 9/9 只证明归档 summary 与本地文件引用自洽。它没有检查视频帧内的真实动作数组，也没有重新调用 policy server。

### 3.1 Local video timeline audit

本轮在临时目录中只读解码 V01/V02，没有修改 `C:\Users\mousongzhe\Project`。两条视频都得到 71 帧、10 FPS、7.1 秒。帧画面由 72px banner、256×256 agent view 和 256×256 wrist view 构成；对每个 camera \(c\)，以 frame 0 为基准计算 8-bit RGB mean absolute difference：

\[
D_c(t)
=
\frac{1}{3HW}
\sum_{u=1}^{H}\sum_{v=1}^{W}\sum_{k=1}^{3}
\left|I_{t,c}(u,v,k)-I_{0,c}(u,v,k)\right|.
\]

\(D_c(t)\) 只量化像素变化，不是状态距离、物体位姿或任务进度。它的价值是把“视频看起来动了”变成可复算的 local visual proxy。

| Frame / time | model agent MAD | model wrist MAD | dummy agent MAD | dummy wrist MAD |
| --- | ---: | ---: | ---: | ---: |
| 10 / 1.0s | 5.403 | 17.071 | 5.369 | 17.099 |
| 20 / 2.0s | 6.976 | 36.943 | 5.377 | 17.228 |
| 30 / 3.0s | 10.454 | 45.608 | 5.385 | 17.268 |
| 40 / 4.0s | 10.028 | 42.909 | 5.394 | 17.260 |
| 50 / 5.0s | 9.932 | 51.265 | 5.393 | 17.274 |
| 60 / 6.0s | 9.572 | 48.840 | 5.397 | 17.280 |
| 70 / 7.0s | 9.685 | 45.524 | 5.392 | 17.282 |

时间线与脚本互相印证：

1. frame 0–10 两侧 overlay 都是 `[0,0,0,0,0,0,-1]`；C01 也定义 `LIBERO_DUMMY_ACTION` 为该向量。它不是七维全零，最后一维固定为 \(-1\)，所以“zero reference”应称 dummy/no-motion arm baseline，而不是 GT 或数学零向量。
2. frame 20 以后，model overlay 出现连续变化的 7D action；agent/wrist MAD 明显高于 dummy，P01 的 action norm 约在 1.0–1.53 间变化，state norm 从约 3.37 降到 3.27 后小幅回升。由此可说 policy action 已进入 env 并诱导出不同 trajectory。
3. 抽样帧显示机械臂从初始位姿向左侧碗区移动，并在后半程停留于碗附近；画面没有显示目标碗被稳定抓起并放到盘子上。P01/S01 同时保持 70 步 reward=0、success=false、done=false。
4. 这些观察排除“model 分支全程仍在执行 dummy”与“仿真完全静止”，但不能证明 action order/unit 正确、接触发生、抓取力有效、task predicate 正确，或某个单一模块导致失败。视频 overlay 只有两位小数，不能替代 raw response/env-action trace。

## 4. What the local script fixes

### 4.1 Observation contract

`C01` 的 `_policy_action` 直接固定：

| Field | Local implementation | Remaining uncertainty |
| --- | --- | --- |
| `observation/image` | `agentview_image[::-1, ::-1]`，`resize_with_pad`，`convert_to_uint8` | 本次 invocation 的原始图像 hash 与实际 resize 参数未写入 summary |
| `observation/wrist_image` | `robot0_eye_in_hand_image[::-1, ::-1]`，同样的 resize/uint8 | 同上 |
| `observation/state` | eef position + quaternion-to-axis-angle + flattened gripper qpos | axis convention/unit 的 round-trip 未做；逐步 state 未落档 |
| `prompt` | `str(task_description)` | server 收到的最终文本未落档 |

### 4.2 Action and execution contract

脚本将 `client.infer(element)["actions"]` 转成 `float32`，在空 `action_plan` 时取 `action_chunk[:replan_steps, :7]`，再通过 `env.step(action.tolist())` 执行。默认 `replan_steps=5`、`resize_size=224`、`seed=7`、`max_steps=80`、`wait_steps=10` 写在 argparse 中，但本次 `client.log` 没有完整 argv；summary 的 70 steps 说明实际 effective config 与默认值不能直接等同。

```python
def local_contract(obs, client, task_description, action_plan, replan_steps):
    # 1. 只在 action queue 为空时构造双视角图像、state 和 prompt。
    request = {
        "observation/image": resize_uint8(flip_both_axes(obs["agentview_image"])),
        "observation/wrist_image": resize_uint8(flip_both_axes(obs["robot0_eye_in_hand_image"])),
        "observation/state": state_from_obs(obs),
        "prompt": str(task_description),
    }
    # 2. 请求 action chunk；本地 bundle 没有保存原始 response tensor。
    chunk = np.asarray(client.infer(request)["actions"], dtype=np.float32)
    # 3. 执行前 replan_steps 行、前 7 维，再重新请求。
    action_plan.extend(chunk[:replan_steps, :7])
    return action_plan.popleft()
```

`_run_episode` 将 `success = success or bool(done)`，把 `done` 同时作为 success flag 与 break 条件；`last_info` 仅以字符串形式写入 summary，本次为 `{}`。因此目前的 scorer 不是独立 task-success evaluator，而是脚本层面的 `done` 聚合。

## 5. Matched failure probe matrix

| Hypothesis | Required matched intervention | Current local evidence | Status |
| --- | --- | --- | --- |
| checkpoint/normalizer mismatch | 同一个 `params/assets` manifest，fresh server load，两次 run 共用 manifest ID | server log 只有 path+restore；binary manifest 不在本地 | `OPEN` |
| image flip/resize mismatch | 固定同一 init state，保存 raw image hash，A/B 只切换 flip/resize | script 固定代码路径，但 raw image 未保存 | `OPEN` |
| state axis/unit mismatch | 保存 quaternion、axis-angle、eef/gripper 原始数组与 round-trip probe | 只有最终 state norm，无 raw state | `OPEN` |
| action order/unit/dimension | 保存 server response shape、前 7D slice、denormalized action 与 env action | `:7` 代码和 video rounded 7D overlay 证明非 dummy action 被执行；raw response/denorm/env trace仍缺 | `OPEN` |
| replan/warm-up | 把 effective `wait_steps/replan_steps/max_steps` 写入 run manifest，做 paired sweep | summary 只显示最终 70 steps | `OPEN` |
| controller/termination scorer | 固定 controller、独立 success predicate、逐 step `info`/termination reason | `last_info={}`，脚本用 `done` | `OPEN` |
| task/init-state confound | 同一个 task/init-state/seed，独立 server restart 后重复 | task/episode 已在 summary；seed/argv 未绑定 | `PARTIAL` |

### Probe acceptance criteria

只有同时满足以下条件，才允许把下一次结果标成 matched probe：

1. `run_id`、checkpoint manifest ID、OpenPI commit、processor/tokenizer revision、effective argv 全部落档；
2. 两个条件只改变一个 intervention，task/init-state/seed、camera bytes、normalizer、controller、scorer 与 horizon 完全一致；
3. 每步 raw observation、raw response action、post-transform env action、reward、done、info 和 timestamp 可重放；
4. model/no-op 或 A/B 两侧各有独立 summary，且 success predicate 不由视频后验推断；
5. 结果先经过 shape/finite/unit/axis audit，再讨论根因。

## 6. Interview-safe boundary

### 30 秒回答

“我没有把 LIBERO 的 `0 reward / false success` 直接归因。只看本地 bundle，同一 task-0/episode-0 的 model 与 dummy 都跑了 70 步；视频前 10 帧共享 dummy warm-up，之后 model action、双相机画面和 state/action norm 明显偏离 dummy，机械臂确实向碗区运动，但没有完成抓取—放置。因此能排除‘policy 全程没执行’和‘仿真没动’，不能说一定是 normalizer、轴序或模型能力问题，因为本地仍缺 raw response/env action、effective argv 和独立 success scorer。”

### 禁止的强结论

- 不能说“模型一定输出了错误的 action order/unit”，因为原始 response 和 env action 没保存。
- 不能说“必然是 checkpoint 或 normalizer 错误”，因为官方 checkpoint restore/load 只证明可加载，不证明其他协议层正确。
- 不能把 dummy-reference 当作 GT demonstration 或七维全零，也不能把 paired video/pixel MAD 当作 causal ablation。
- 不能把脚本作者、远端 deployment 或 official `pi05_libero` 归为个人端到端 ownership。

## 7. 下一步

1. 后续仍只在本地操作：先把现有 video timeline、P01/P02 与 script contract 用于失败口述，不把它们升级成 matched rerun。
2. 如果未来有新的本地 rollout bundle，必须保存 effective argv、raw request/response、post-transform action、reward/done/info 和独立 scorer；没有这些字段时不升级 `0/1` 的根因结论。
3. 保持 `PROJ-OPENPIVLA-007/008` 与全局 280 张卡 `unseen`，不创建 `coaching_state.md`。

## 参考文献（References）

1. Local summary：`artifacts/libero_franka_true_rollout_v1/summary.json`（S01）。
2. Local server/client logs：同目录 `serve.log`、`client.log`（S02–S03）。
3. Local rollout implementation：`scripts/run_libero_true_rollout.py`（C01）。
4. Local rollout videos：`zero_reference_rollout.mp4`、`model_policy_rollout.mp4`、`zero_reference_vs_model.mp4`（V01–V03）。
5. [OpenPiVLA / LIBERO Checkpoint Load–Serve–Client Lineage Gate](openpivla_libero_checkpoint_load_lineage_gate.html)。
6. [OpenPiVLA Official Checkpoint Immutable Manifest Gate](openpivla_official_checkpoint_immutable_manifest_gate.html)。
