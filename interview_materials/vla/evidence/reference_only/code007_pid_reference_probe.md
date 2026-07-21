# CODE-VLA-007 Reference-only PID Probe Artifact

> 状态：`reference_only / assistant_generated / WARN`  
> 运行日期：2026-07-20  
> 对应知识：[CODE-007 Knowledge](../../knowledge/vol_08_code007_pid_anti_windup.html)  
> 对应题卡：[CODE-007 Card](../../questions/vol_08_code007.html)

## 重要边界

这是用来验证知识页公式、伪代码和 probe 设计的 **assistant-generated reference harness**，不是候选人项目实现、不是个人 ownership 证据，也不是机器人闭环结果。它只使用标量 Python 浮点状态，未接入 VLA 模型、URDF、joint feedback、真实 controller、GPU 或项目 runtime；因此不能把 `PASS` 解读为项目通过、PID 调参完成或真机稳定。

## Reference contract

固定：`e = setpoint - measurement`；`i_state` 是已乘 `K_i` 的积分输出贡献；

\[
u^{\mathrm{unsat}}=K_p e+i_{state}+K_d\frac{e-e_{prev}}{dt},\qquad
u_{sat}=\operatorname{clip}(u^{\mathrm{unsat}},u_{min},u_{max}).
\]

conditional integration 按饱和方向冻结/放行；back-calculation 使用：

\[
i_{next}=i_{state}+dt\left(K_i e+\frac{u_{sat}-u^{\mathrm{unsat}}}{T_t}\right).
\]

测试 harness 显式检查 `dt`、误差方向、state、limits、reset、continuous-angle helper 与 fixed replay；它没有实现 derivative filter、rate limit 或 controller acknowledgement。

## Run matrix

| Probe | 参考输入/检查 | 结果 |
| --- | --- | --- |
| P1 | `dt=0`、负数、NaN 必须 reject | PASS |
| P2 | `K_i=0/K_d=0` 的 P-only 与 D-zero 行为 | PASS |
| P3 | 正误差上饱和：conditional freeze、back-calculation 回拉且输出 clip | PASS |
| P4 | 误差反向后仍可解除 wind-up | PASS |
| P5 | `u_min=u_max=0` 不产生 NaN | PASS |
| P6 | reset 后重复同一首步输入，输出一致 | PASS |
| P7 | 显式 continuous-angle shortest-path helper | PASS |
| P8 | 固定输入序列逐步 replay，`u/i_state` trace 一致 | PASS |

P8 reference trace（`u_sat`, `i_state`）：

```text
[(1.0, 0.0), (0.6, 0.04), (-1.0, 0.04), (-1.0, 0.04)]
```

## Interpretation

这次运行证明 reference contract 在指定标量 probes 下自洽，特别是：

- output clamp 与积分更新是两个独立状态路径；
- conditional integration 必须判断饱和方向，不能“所有饱和都冻结”；
- back-calculation 的 `T_t` 和 state 单位必须显式记录；
- reset/replay 是可审计的 state lifecycle，而不是附加日志。

它没有证明：VLA action 的 normalized/physical 单位正确、controller rate 满足 deadline、lease/episode epoch 没有 stale state、PID 在真实机器人上稳定，或候选人亲自实现过该逻辑。下一步仍需要候选人的白板/runtime 回答或真实 artifact。

## Reproduction note

运行环境为本地 Python 3 标量 reference function；结果由一次 deterministic invocation 生成。该 artifact 不记录候选人姓名、Git author、项目路径或未验证指标，避免把参考 harness 混入个人经历。

## References

1. [CODE-007 Knowledge](../../knowledge/vol_08_code007_pid_anti_windup.html)。
2. [CODE-007 Source Freeze](../../sources/vol_08_code007_pid_anti_windup_source_freeze.html)。
3. [CODE-007 Card](../../questions/vol_08_code007.html)。
