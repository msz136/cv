# VOL 05 EVAL-013：端到端 Latency、Deadline Miss 与 Jitter

> 状态：`drafted / VLA-EVAL-013 / knowledge_35_of_44 / card_1_of_1_unseen / review_warn`  
> 更新日期：2026-07-19  
> 前置：[ENG-007 Latency Budget](vol_05_engineering_eval.html)、[ENG-022 Policy Server](vol_05_engineering_eval_eng022.html)、[WM-034 Control Latency](vol_04_world_model_sim2real_wm034_control_latency_actuator_controller_mismatch.html)、[EVAL-009 Recomputable Bundle](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)、[EVAL-010 Release Gate](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)  
> 来源冻结：[EVAL-013 Source Freeze](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)  
> 项目边界：五项目均无 checkpoint-bound observation-capture→controller-apply trace；UWM 的 DataLoader p95 A/B 只支持训练 input stall，不是 VLA 实时闭环结果。

## 问题（Question）

VLA 的 p50/p95/p99 latency、deadline miss、jitter 与 control frequency 应怎样测，才能区分模型计算、服务排队、网络、动作新鲜度和 controller 调度，并形成可信 release gate？

## 1. 一句话框架

```text
freeze event boundaries + clock contract + model/request/load/H/K/Hz
  -> capture→queue→infer→transport→decode→controller apply spans
  -> cold/warm/load/fault strata
  -> q50/q95/q99/max + miss k/n/CI + jitter + per-offset action age
  -> raw trace recompute + hard latency/safety gate + robot-side canary
```

`infer_ms`、WebSocket RTT、network jitter、controller lateness 和 capture→apply action age 是不同 metric；平均值、单次 timing 和 config 中的 `control_freq` 都不能证明实时性。

## 2. Event Boundary

每个 request 至少绑定：

```text
episode/request/obs/chunk/checkpoint IDs,
sensor capture, preprocess, enqueue/dequeue, infer start/end,
serialize/send/receive, decode, controller accept, apply[j], next sensor,
clock/host/resolution/offset uncertainty,
queue/batch/payload/H/K/Hz/request-shape/deadline/outcome
```

核心 E2E：

\[
L_i^{\mathrm{e2e}}=t_{i,0}^{\mathrm{apply}}-t_i^{\mathrm{capture}}.
\]

变量解释：起点是生成该 request 的 observation capture，终点是第一条动作真正 apply；直觉是“机器人依据多旧的观测开始行动”。实现映射：必须有 obs/request/chunk ID 和可比较 clock，不能用函数 return 或 response receive 代替 controller apply。[1][2]

| metric | 边界 | 用途 |
| --- | --- | --- |
| compute latency | synchronized infer start→end | 模型/solver/backend |
| response latency | client send→receive | queue+infer+transport |
| first-action age | capture→apply[0] | 第一条动作新鲜度 |
| per-offset age | capture→apply[j] | chunk 后续动作是否 stale |
| loop response | capture→apply→next sensor | 闭环状态何时可见 |
| scheduler lateness | planned deadline→actual wake/apply | periodic real-time behavior |

## 3. Clock Contract

同主机 duration 使用 monotonic/performance counter；wall-clock只作日志时间。跨主机要保存同步方法、offset、drift和 residual。[3]

\[
L_i^{\mathrm{true}}\in
[L_i^{\mathrm{obs}}-u_{\mathrm{clock}},\;L_i^{\mathrm{obs}}+u_{\mathrm{clock}}].
\]

变量解释：`u_clock` 是 clock offset uncertainty。直觉：同步误差大于候选优化时，无法声称 latency 改善。实现映射：clock manifest保存 source/resolution/host/sync samples；GPU异步 timing还要 device event或synchronize，并冻结 warm-up/compile/cache 状态。

## 4. Critical Path

\[
L_{\mathrm{parts}}=
L_{\mathrm{sensor}}+L_{\mathrm{pre}}+L_{\mathrm{queue}}+
L_{\mathrm{infer}}+L_{\mathrm{transport}}+L_{\mathrm{decode}}+
L_{\mathrm{controller}}.
\]

变量解释：每项是同 request 的 span。直觉：找出 tail 的第一责任阶段。实现映射：异步阶段会 overlap，所以 `L_e2e` 是 span DAG 的 critical path，不是各阶段平均值之和；既报每段 percentile，也报 `E[L_stage | L_e2e ≥ q99]`。

## 5. p50/p95/p99 与样本量

\[
\widehat F_n(x)=\frac{1}{n}\sum_i\mathbb{1}[L_i\le x],
\qquad
\widehat q_p=\inf\{x:\widehat F_n(x)\ge p\}.
\]

变量解释：`q_p` 是冻结 interpolation 下的经验分位点。实现映射：同时保存 `n`、bin precision、raw spans、max、run/robot-day cluster 与 uncertainty。`n=100` 的 p99 基本由一个样本决定，不能写成稳定 SLO。[1]

《The Tail at Scale》说明 temporary high latency 在规模/利用率上升后可能主导系统响应。[4] 对机器人，tail 还可能跨过 contact、reset或safety deadline；mean、throughput、p99和success回答不同问题。

## 6. Deadline Miss

\[
M_i=\mathbb{1}[t_i^{\mathrm{apply}}>D_i],
\qquad
\widehat r_{\mathrm{miss}}=\frac{1}{n}\sum_iM_i.
\]

变量解释：`D_i` 是事前冻结的 absolute deadline。实现映射：报告 miss `k/n/CI`、lateness、miss stage、连续 burst、late completion、drop/fallback和outcome。timeout返回不等于GPU work或robot action已取消。[2]

ROS 2 pendulum demo同时关注 deadline lateness、max/mean/std、page faults和periodic spikes，说明平均调度 latency 不能替代 worst/tail gate；其示例值不是 VLA 默认阈值。[5]

## 7. Jitter 与 Action Age

若 `T_c=1/f_c`：

\[
e_i=t_i^{\mathrm{apply}}-(t_0+iT_c),
\qquad
J_i=(t_i^{\mathrm{apply}}-t_{i-1}^{\mathrm{apply}})-T_c.
\]

变量解释：`e_i` 是相对理想 schedule 的 phase error，`J_i` 是相邻 apply interval 偏差。实现映射：报 signed/absolute tail、early/late、burst和周期性 spike；standard deviation不能替代非对称 p99。

RFC 3393 的 packet delay variation只属于network stage。[6] 总 control jitter还包含sensor、OS、queue/batch、GPU、decode与controller，不能用ping jitter代表机器人实时性。

chunk 第 `j` 条动作：

\[
A_{i,j}=t_{i,j}^{\mathrm{apply}}-t_i^{\mathrm{capture}}
\approx L_i^{\mathrm{e2e}}+jT_c.
\]

变量解释：这是该动作使用的 observation age；近似只适用于固定周期无额外扰动。实现映射：逐条存 `t_apply[j]`；first-action很快不代表长prefix后半段新鲜。[2]

## 8. Control Frequency、H 与 K

\[
T_c=\frac{1}{f_c},
\qquad T_{\mathrm{chunk}}=\frac{H}{f_c},
\qquad T_{\mathrm{replan}}=\frac{K}{f_c}.
\]

变量解释：`H`是预测 horizon，`K`是每次实际执行 prefix。实现映射：冻结 policy/controller Hz、action repeat、interpolation、action per-step/per-second语义；同样H/K在不同频率下物理时长不同。低频replan增加stale exposure，高频query可能增加contention和miss。

deadline不能简单写成 `1/f_c`：low-level controller可继续执行chunk，而policy query周期是 `K/f_c`。应分别定义 controller deadline、query deadline、max action age 与 safety deadline。

## 9. Cold、Warm、Load 与 Fault

| slice | 必须记录 |
| --- | --- |
| lifecycle | process start、first request、compile/cache、steady、reload |
| load | single-client、target concurrency、burst、overload、multi-robot |
| request | cameras/resolution/token/H/D/NFE/batch/payload |
| runtime | checkpoint/processor/backend/dtype/device/power/thermal |
| task | free-space/contact/recovery/reset transition |
| fault | sensor delay、queue burst、network loss、worker restart、controller reject |

每格记录 intended/offered/accepted/completed/dropped/timeout 和 queue depth。只“发一个等一个”会在长响应期间停止发新 request，低估 backlog。

## 10. Coordinated Omission

HdrHistogram指出，当长响应让本应发生的采样被跳过，原始 histogram会严重低估tail；expected-interval correction用于显露这种 bias。[7]

VLA load test同时保留 intended/actual arrival、expected interval、open-loop scheduled与closed-loop client、raw/corrected histogram。correction是测量诊断，不是虚构真实episode；主证据仍是arrival/queue/span ledger。

## 11. 实验与 Gate

固定 checkpoint、request mix、H/K/Hz、controller、hardware 与 load：

- model/backend/NFE：看 synchronized compute、E2E tail、parity与success；
- H/K/frequency：看 per-offset age、miss/stale、tracking与success；
- batching/queue/concurrency：看 throughput、queue/E2E p99与drop；
- transport/serialization：看 response与E2E tail、payload/CPU；
- fault/load：看 miss burst、cancel、fallback与recovery。

primary endpoint事前冻结；同时报q50/q95/q99/max、miss k/n/CI、jitter、stale/drop/fallback、throughput与success/safety。latency提升不能抵消invalid/safety/success回退，sim/server microbenchmark不能替代robot-side canary。[8]

## 12. 五项目边界

### Robot Harness

tool polling timeout、cancel、lock cleanup和compensation是side-effect控制，不是VLA capture→apply或controller cycle；缺action-age p99与load test。

### OPD

只有static point/box/text eval与checkpoint/by-pool summary；没有policy server、controller、clock、deadline或jitter trace。

### OpenPiVLA

local脚本有connect/infer timeout hook，official OpenPI server有`infer_ms`；缺formal checkpoint绑定的capture/apply、warm/load p99、GPU sync、miss/jitter与robot canary。

### WAM

单episode的300-step action/video与三camera manifest没有per-step timestamp或controller apply；视频时长不能反推control frequency。

### UWM

DataLoader-only p95 wait约`13.86s→0.19s`是训练input stall的local-direct smoke；不是rollout latency，也不能外推action-age或成功率提升。

## 13. Artifact 与伪代码

```text
latency_eval/
  clock_contract.json
  protocol_manifest.json
  raw_spans.parquet
  action_apply.parquet
  arrivals_queue.parquet
  outcomes.jsonl
  summaries/by_slice.json
  figures/{timeline,cdf,tail,load_curve}.svg
  checksums/manifest-sha256.txt
  reproduce.ps1
```

```python
def evaluate_latency(client, controller, schedule, protocol, clock):
    # Freeze event boundaries, clocks, deadlines and model/load/H/K/Hz contract.
    spec = validate_clock_and_protocol(protocol, clock)

    # Use intended arrivals so prior slow responses do not suppress new samples.
    for request in schedule:
        obs, trace = capture_and_start_trace(request, spec)

        # Synchronize device timing and record every queue/infer/transport span.
        chunk = client.infer_with_spans(obs, trace, sync_device=True)

        # Gate stale/late output and timestamp each actual controller apply event.
        for j, action in enumerate(freshness_gate(chunk, request.deadline)):
            trace.mark_apply(j, controller.apply(action))

        # Persist raw spans before any percentile or release summary.
        write_immutable_trace(trace)

    return recompute_tail_miss_jitter_age_report(spec)
```

伪代码是评估合同，不是五项目已有实现。

## 14. 面试防线与下一入口

- `infer_ms`不等于capture→apply；
- mean低不等于p99/deadline安全；
- ping jitter不等于control jitter；
- `control_freq=20`不证明实际20 Hz；
- first-action快不代表chunk后续动作新鲜；
- warm单请求不代表cold/target-load；
- UWM训练DataLoader p95不等于rollout实时性；
- 五项目当前只能讲补证据合同，不能报实时闭环成果。

EVAL-013知识与一张题卡保持`WARN/unseen`。下一节点是`VLA-EVAL-014`：forbidden side effect、scope、取消与补偿评估。没有真实口述前不创建`coaching_state.md`。

## 参考文献（References）

1. [EVAL-013 Source Freeze](../sources/vol_05_eval013_end_to_end_latency_deadline_jitter_source_freeze.html)。
2. [WM-034 Control Latency](../sources/vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)与[ENG-022 Policy Server](vol_05_engineering_eval_eng022.html)。
3. CPython [`time.rst@2931f2`](https://github.com/python/cpython/blob/2931f2067a6ecdc52cb44f694ce14ab8b50b9a32/Doc/library/time.rst)。
4. Dean & Barroso, [*The Tail at Scale*](https://research.google/pubs/the-tail-at-scale/), 2013。
5. ROS 2 [`pendulum_control@54d49d2`](https://github.com/ros2/demos/blob/54d49d22e898d796ea476c42268757ad422bf878/pendulum_control/README.md)。
6. IETF, [RFC 3393](https://www.rfc-editor.org/rfc/rfc3393), 2002。
7. [HdrHistogram@de84b0a](https://github.com/HdrHistogram/HdrHistogram/tree/de84b0a7de2378abfc405da503bf4898e84ea98e)。
8. [EVAL-009](vol_05_engineering_eval_eval009_recomputable_evaluation_bundle.html)、[EVAL-010](vol_05_engineering_eval_eval010_regression_gate_golden_set_canary_rollout.html)与[Evidence Manifest](../evidence/evidence_manifest.html)。
