# VOL 08 CODE-007：PID Update with Anti-windup

> 状态：`drafted / CODE-VLA-007 / knowledge_10_of_phase / card_pending / WARN`  
> 报告日期：2026-07-20  
> 证据截止：2026-07-20  
> 来源入口：[CODE-007 Source Freeze](../sources/vol_08_code007_pid_anti_windup_source_freeze.html)。

## 问题（Question）

手写 PID 题真正考的不是背出 `P+I+D`，而是能否把离散时间、误差符号、内部状态、输出饱和、积分 anti-windup、reset 和测试 oracle 写成一个可审计的函数。VLA 场景还要继续追问：连续 action 是否已经 denormalize、控制器是否有独立的 rate/limit、安全 gate 和 episode epoch。

## 1. 直觉：为什么会 wind-up？

积分项会把长期误差累起来。当执行器已经达到上限，但误差仍要求更大的输出时，真实系统只能输出饱和值；如果软件仍按理想 `u_unsat` 累积积分，内部状态会越来越大。误差后来反向时，控制器要先“偿还”这笔虚假的积分债，造成 overshoot、恢复慢甚至安全风险，这就是 integral wind-up。

专业上必须区分三层：

1. **理想控制输出** `u_unsat`：P/I/D 相加的结果；
2. **执行器可实现输出** `u_sat`：经过上下限、rate limit 或安全 gate 后真正送出的值；
3. **内部积分状态** `i_state`：下一步更新时是否继续累积、冻结或被 `u_sat-u_unsat` 拉回。

ROS 2 control 文档直接暴露 output/integral clamp 与两类 anti-windup strategy；WPILib 文档强调固定 period、reset、integrator range、IZone 和 output clamp。它们支持 API/边界语义，不等于本地项目已经部署 PID 或证明真机稳定。

## 2. 冻结接口与状态

建议函数签名：

```python
pid_step(
    setpoint: Tensor,
    measurement: Tensor,
    state: PIDState,
    gains: PIDGains,
    limits: PIDLimits,
    dt: Tensor,
) -> tuple[Tensor, PIDState, PIDTrace]
```

最小 `PIDState` 包含 `e_prev`、`i_state` 和可选 derivative-filter state；`PIDTrace` 至少记录 `e`、`p_term`、`i_term`、`d_term`、`u_unsat`、`u_sat`、`saturated_high/low`、anti-windup branch、`dt` 与 reset reason。对于 batch/action dimension，所有 state 和 limit 都要明确广播规则，不能让 `[B]`、`[B,D]`、标量 limit 静默错配。

在本页固定误差为：

\[
e_k=r_k-y_k.
\]

若项目使用 `measurement-setpoint`，必须把 P/I/D 与饱和方向判定一起翻转；只改 P 项会让 conditional integration 在错误的 rail 上冻结。

## 3. 离散 PID 主体

令 `i_state` 是已经乘过 `K_i` 的积分输出贡献，最简单的 backward-difference derivative 为：

\[
u^{\mathrm{unsat}}_k=K_p e_k+i_k+K_d\frac{e_k-e_{k-1}}{\Delta t},
\qquad
u_k=\operatorname{clip}\!\left(u^{\mathrm{unsat}}_k,u_{\min},u_{\max}\right).
\]

变量含义：`r/y` 是 setpoint/measurement，`K_p/K_i/K_d` 是 gain，`Δt` 是本次更新周期，`u_unsat` 是理想输出，`u` 是 clamp 后输出。实现映射是 action/controller tensor 的逐元素计算；`trace` 必须保留 `u_unsat` 与 `u`，否则无法诊断“模型输出大”还是“执行器饱和”。

工程上 derivative 还可能使用 measurement derivative、低通滤波或 dirty-derivative；这些选择必须和噪声、采样抖动、reset 语义一起冻结，不能在面试中把一行差分公式说成所有 PID 的唯一实现。

## 4. Conditional integration

未饱和时正常积分；已上饱和且误差继续把输出推向上 rail 时冻结；已上饱和但误差反向、正在把输出拉回可实现区间时允许积分。概念式为：

\[
i_{k+1}=i_k+K_i\Delta t\,e_k\,g_k,
\qquad
g_k=\mathbf{1}\!\left[\neg\mathrm{sat}_k\;\lor\;\mathrm{error\ drives\ back\ from\ the\ rail}\right].
\]

关键不是背 `g_k`，而是先判断饱和方向：

- `u_unsat > u_max` 且 `e>0`：继续向上推，冻结；
- `u_unsat < u_min` 且 `e<0`：继续向下推，冻结；
- 已上饱和但 `e<0`，或已下饱和但 `e>0`：允许积分消除 wind-up。

如果 limits 是向量，判断必须逐 action dimension 完成；不能用整个 batch 的 `any(saturated)` 冻结所有维度。

## 5. Back-calculation

把执行器实际输出反馈到积分状态：

\[
i_{k+1}=i_k+\Delta t\left(K_i e_k+\frac{u_k-u^{\mathrm{unsat}}_k}{T_t}\right),
\qquad T_t>0.
\]

`u-u_unsat` 在饱和时把积分状态拉回可实现输出；`T_t` 小则回算快但对噪声和 jitter 更敏感，`T_t` 大则恢复慢。这里 `i_state` 的单位是 output contribution，因此 `K_i e` 与 `(u-u_unsat)/T_t` 必须同量纲。若代码把积分器存成未经 `K_i` 的 `∫e dt`，公式和 reset/limit 的位置都要相应改写。

ROS 2 文档支持 `back_calculation`、`conditional_integration`、`none` 和 tracking-time 参数名；本页的离散更新是可测试的实现合同，不声称它等同于某个仓库的默认内部源码。

## 6. Clamp、IZone、reset 的边界

| 机制 | 作用 | 不能替代 |
| --- | --- | --- |
| `u_clamp` | 限制最终 actuator command | 防止 `i_state` 继续增长 |
| `i_clamp` / integrator range | 限制积分贡献的范围 | 具有动态回算的 back-calculation |
| conditional integration | 根据饱和方向决定是否累加 | 对错误 error sign 的修复 |
| back-calculation | 用 `u_sat-u_unsat` 动态拉回积分 | 正确选择 tracking time 或安全 limit |
| IZone | 误差超过阈值时禁用积分 | 饱和方向判断与执行器反馈 |
| `reset()` | 清除积分、历史误差、滤波器状态 | 处理错误的 episode/lease ownership |

VLA/robot action 需要在 reset 时记录 `episode_id`、`robot_id` 或 action epoch；否则旧 observation 的 derivative/integral state 可能泄漏到新任务。reset 的触发条件应包括 controller restart、robot lease epoch 变化、model/schema revision 不兼容与安全 stop 后重新 armed。

## 7. 参考实现（带边界注释）

```python
def pid_step(setpoint, measurement, state, gains, limits, dt):
    # Reject invalid time; silently substituting a nominal period hides jitter.
    if not torch.isfinite(dt).all() or (dt <= 0).any():
        raise ValueError("dt must be finite and positive")

    e = setpoint - measurement
    de = (e - state.e_prev) / dt
    p_term = gains.kp * e
    d_term = gains.kd * de
    u_unsat = p_term + state.i_state + d_term
    u = torch.clamp(u_unsat, limits.u_min, limits.u_max)

    high = u_unsat > limits.u_max
    low = u_unsat < limits.u_min
    if limits.antiwindup == "conditional_integration":
        drives_back = (high & (e < 0)) | (low & (e > 0))
        allow_i = ~(high | low) | drives_back
        next_i = state.i_state + gains.ki * dt * e * allow_i
    elif limits.antiwindup == "back_calculation":
        next_i = state.i_state + dt * (
            gains.ki * e + (u - u_unsat) / limits.tracking_time_constant
        )
    elif limits.antiwindup == "none":
        next_i = state.i_state + gains.ki * dt * e
    else:
        raise ValueError("unknown anti-windup strategy")

    next_i = torch.clamp(next_i, limits.i_min, limits.i_max)
    next_state = PIDState(e_prev=e, i_state=next_i)
    trace = PIDTrace(e=e, u_unsat=u_unsat, u_sat=u,
                     saturated_high=high, saturated_low=low,
                     antiwindup=limits.antiwindup, dt=dt)
    return u, next_state, trace
```

这段伪代码故意把 `u_unsat/u_sat`、方向 mask 和 `antiwindup` branch 暴露出来。生产代码还应处理 derivative kick、NaN/Inf、rate limit、command timeout、batch broadcasting、device/dtype 与 reset reason；不能只返回一个 action tensor。

## 8. 测试与 first-divergence 诊断

| Probe | 期望 | 首个分叉意味着什么 |
| --- | --- | --- |
| `dt=0/negative/NaN` | reject 或显式 fallback | 时间合同/输入校验缺失 |
| `K_i=0`、`K_d=0` | P-only/D-only 行为可解释 | gain 或 state 路径错 |
| 正误差上饱和 | conditional freeze；back-calc 回拉 | 饱和方向或公式错 |
| 误差反向 | 积分能消除 wind-up | 把所有饱和都冻结 |
| `u_min=u_max` / infinite clamp | 无 NaN，trace 可解释 | 边界/广播错 |
| reset 后同一输入 | 与新 episode 首步一致 | state 泄漏 |
| continuous input | 仅显式启用时走 shortest path | 角度 wrap 误用 |
| fixed replay | step-by-step trace 相同 | 非确定性或未记录状态 |

诊断顺序固定为：`dt/finite → error sign → state/reset → u_unsat → clamp/limit → anti-windup branch → dtype/device → downstream controller ack`。不要从最终 action 失败直接跳到“PID 参数不对”。

## 9. VLA 映射与项目边界

连续 VLA action 可能是归一化的 joint delta、pose residual 或 velocity command。PID 前必须确认 action schema、单位、normalizer revision、joint order、limit 与 controller rate；否则同一个 `K_i` 在 normalized space 和 physical space 不是同一语义。PID 只处理已定义的 setpoint/measurement/control interface，不替代 perception、IK、collision check、lease fencing、独立 e-stop 或 robot success scorer。

现有五项目可作为追问 hook：OpenPiVLA 的 action shape/normalizer/parser、Robot Harness 的 timeout/compensation、WAM 的 controller/chunk diagnostic、OPD 的 route/teacher schedule、UWM/LIBERO 的 launcher/task mapping。但当前没有 CODE-007 local implementation、joint feedback trace、anti-windup tuning log、matched controller ablation 或 candidate ownership artifact，因此安全回答是“我能实现并测试这个合同”，不能说“我已在项目中完成并验证了 anti-windup PID”。

## 10. 30 秒回答与高压追问

**30 秒回答**：先固定误差符号、`dt`、state 和 output limits。算 `u_unsat=P+I+D`，再得到 `u_sat=clip(u_unsat)`。积分 anti-windup 有两种常讲法：conditional integration 在饱和且误差继续推向 rail 时冻结、反向时放行；back-calculation 用 `(u_sat-u_unsat)/T_t` 把积分拉回。`u_clamp`、`i_clamp`、IZone、reset 不是一回事。代码要记录 `u_unsat/u_sat/branch`，测 `dt` 异常、正反向饱和、reset、边界和 replay；这只证明更新合同，不等于真机闭环成功。

**高压追问**：

- 为什么 `mean(mask*loss)` 的问题与 PID 积分饱和有相似性？——两者都需要明确“有效贡献”的 denominator/state，而不是只看最终标量。
- back-calculation 的 `T_t` 如何调？——先固定单位和采样周期，做 matched step/reversal sweep，看 settling、overshoot、noise sensitivity 与 saturation duration；没有 trace 不报收益。
- action 已 normalized 怎么办？——先绑定 normalizer/schema revision，再决定 PID 在 normalized 还是 physical space 工作，limit 与 gain 必须在同一量纲。
- controller timeout 或 lease epoch 变化时是否继续积累？——停止/失租约时拒绝旧 action，并按 episode/epoch contract reset 或冻结，不能让 stale state 继续驱动输出。

## 11. 结论与下一步

PID anti-windup 的高分答案是把公式、状态、饱和方向、时间单位、reset、trace 和测试 oracle 绑定起来，并明确它与 VLA action schema、controller safety 和项目证据的边界。当前 source contract 已冻结；下一步只生成 CODE‑VLA‑007 题卡，仍需另一个 bounded slice，且不改变 `unseen`。

## References

1. [CODE-007 Source Freeze](../sources/vol_08_code007_pid_anti_windup_source_freeze.html)。
2. [ROS 2 control PID controller userdoc](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html)。
3. [WPILib PIDController documentation](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/controllers/pidcontroller.html)。
4. [Feedback Systems](https://fbsbook.org/)。
5. 本仓库 [VOL 01 advanced-control fact review](../sources/vol_01_batch3_advanced_control_independent_fact_review.html) 与五项目 evidence inventories。
