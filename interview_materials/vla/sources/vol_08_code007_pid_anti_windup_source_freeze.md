# VOL 08 CODE-007 Source Freeze：PID Update with Anti-windup

> 状态：`source_frozen / CODE-VLA-007 / knowledge_synced / card_pending / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本页冻结 PID update 的函数签名、离散时间语义、输出饱和、积分 anti-windup、reset 与测试 oracle；下游 knowledge 已在独立 bounded slice 生成，仍不把公开 controller 文档或本地基础知识写成候选人已经实现了闭环控制器。

## 问题（Question）

如何实现一个可测试的离散 PID 更新，使 `dt`、误差符号、导数状态、输出饱和与积分 anti-windup 语义明确？面试中必须能区分：输出 clamp、积分项 clamp、conditional integration、back-calculation、reset，以及这些机制对 VLA action/controller 边界的影响。

## 1. 来源、版本与 claim boundary

| 来源 | 类型 / 固定信息 | 直接支持 | 不能支持 |
| --- | --- | --- | --- |
| [ROS 2 control PID controller userdoc](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html) | official docs；抓取日期 2026-07-20；响应 SHA-256 `88aa83d02cd8712bcb9c00064fb033e1388034fdd81bb6a7965ef26ca146f11d` | `p/i/d` gains、`u_clamp`、`i_clamp`、`antiwindup_strategy={back_calculation,conditional_integration,none}` 与 `tracking_time_constant` 配置语义 | 本地机器人已使用 ROS 2 controller、调参结果或真实闭环成功 |
| [WPILib PIDController documentation](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/controllers/pidcontroller.html) | official docs；抓取日期 2026-07-20；响应 SHA-256 `5160878475dff0129ca10700ade06f1613f11ada79d8d93ad3a93cd1f2a5765a` | 固定 period 假设、`reset()`、integrator range、IZone、输出 clamp、continuous input 的 API/边界提醒 | 任何 VLA action 维度、机器人硬件或候选人 ownership |
| [Feedback Systems](https://fbsbook.org/) | textbook landing page；抓取日期 2026-07-20；响应 SHA-256 `1b550456ff5d81fad55e7ecf79822ed4a233872e7bccc0d089cd205c06200018` | PID、饱和与反馈稳定性所需的控制理论入口 | 某一具体 anti-windup 离散实现的默认参数或项目收益 |
| 本仓库 [VOL 01 advanced-control fact review](vol_01_batch3_advanced_control_independent_fact_review.html) | local canonical；已审查的控制基础与项目边界 | PID/MPC/impedance/learned policy 的选择条件与真实性边界 | CODE-007 的本地实现、白板通过或真机闭环 |

`checked` 只表示来源响应已记录并能支撑上表中的窄 claim。`back-calculation` 的离散公式、条件积分的判定顺序和测试矩阵属于本页明确标注的实现合同/推导，不是 ROS 2 或 WPILib 默认实现的逐行复刻。

## 2. 冻结接口与离散语义

建议把更新函数固定为：

```text
pid_step(setpoint, measurement, state, gains, limits, dt) -> (u_sat, next_state, trace)
```

其中 `state` 至少包含上一时刻误差 `e_prev`、积分输出 `i_state` 和可选导数滤波状态；`trace` 记录 `e`、`p_term`、`i_term`、`d_term`、`u_unsat`、`u_sat`、饱和方向与 anti-windup 分支。`dt` 必须是正的、有限的、与控制周期同一时间单位；`dt=0`、负数、NaN 和突变都必须有显式策略，而不是静默当作固定周期。

令误差采用 `e_k = setpoint - measurement`，并把 `i_state` 定义为已经乘过 `K_i` 的积分输出贡献：

\[
u^{\mathrm{unsat}}_k=K_p e_k+i_k+K_d\frac{e_k-e_{k-1}}{\Delta t},\qquad
u_k=\operatorname{clip}(u^{\mathrm{unsat}}_k,u_{\min},u_{\max}).
\]

若实现采用相反误差符号，所有 P/I/D 与 anti-windup 判定必须成套翻转；只改 P 项符号会造成“看似能跑、饱和方向错误”的隐蔽 bug。

## 3. Anti-windup 合同

### 3.1 Conditional integration

当未饱和时积分正常累加；已经上饱和且误差仍推动输出向上，或已经下饱和且误差仍推动输出向下时，冻结积分。可写成：

\[
i_{k+1}=i_k+K_i\Delta t\,e_k\;\mathbf{1}\!\left[\neg\mathrm{sat}_k\;\lor\;\mathrm{error\ drives\ back\ from\ the\ rail}\right].
\]

判定必须基于 `u_unsat` 与 `u_sat` 的方向，而不是只检查 `abs(e)`；否则会在设定值跨越、负向饱和或不同误差定义下冻结错误。

### 3.2 Back-calculation

把执行器实际可实现的 `u_sat` 反馈回积分状态：

\[
i_{k+1}=i_k+\Delta t\left(K_i e_k+\frac{u_k-u^{\mathrm{unsat}}_k}{T_t}\right),
\]

其中 `T_t>0` 是 tracking time constant。`u_sat-u_unsat` 把积累过多的积分贡献拉回可实现输出；`T_t` 太小会使积分状态剧烈追踪并放大噪声，太大则恢复慢。ROS 2 文档直接暴露该策略和 tracking-time 参数，但本页的离散状态定义仍需在代码中固定并测试。

### 3.3 Clamp、reset 与 IZone 不等价

- `u_clamp` 限制最终输出；它本身不保证积分状态不会继续增长。
- `i_clamp` 限制积分贡献；它能减少 windup，但不等于 back-calculation 的动态回算。
- `reset()` 清除积分、导数历史与滤波器状态；重新启用、episode 切换、robot lease/episode epoch 变化时必须明确是否 reset。
- IZone/误差门控是“何时允许积分”的策略，不能和输出饱和方向判定混为一谈。

## 4. 最小 deterministic probe 矩阵

| Probe | 输入/条件 | 预期检查 |
| --- | --- | --- |
| P1 | `dt=0`、负数、NaN、Inf | reject 或显式 fallback；不得悄悄更新积分 |
| P2 | `K_i=0`、`K_d=0`、`dt` 改变 | P-only/D-only 与时间尺度行为可解释 |
| P3 | 正误差触发上饱和 | conditional integration 冻结；back-calculation 向下回拉 |
| P4 | 误差反向、仍在上饱和 | 积分允许消除 windup，不能继续冻结 |
| P5 | `u_min=u_max`、无限 clamp、`i_clamp` | 边界不产生 NaN；trace 说明饱和与积分状态 |
| P6 | reset 后重复同一输入 | 输出/状态与新 episode 首步一致，旧导数不泄漏 |
| P7 | 角度环绕输入 | 只有显式启用 continuous input 才使用 shortest-path error |
| P8 | 固定 seed 的 step-by-step replay | state、u_unsat、u_sat 与 trace 可逐步复现 |

这些 probes 证明的是函数合同与数值行为，不证明控制器在某个机器人、VLA action schema 或真实硬件上稳定。

## 5. 项目真实性边界

现有五项目材料可以用于追问“动作输出、timeout/cancel、controller hook、simulator rollout 或 action normalization 如何与 PID 接口对齐”，但当前没有可闭合的 CODE-007 local implementation、joint feedback trace、matched controller comparison、anti-windup tuning log 或 candidate ownership artifact。因此安全表达是“我能解释并设计这个更新合同”，不能说“我已经在项目中实现并验证了 anti-windup PID”。

## 6. Source gate 结论与下一步

ROS 2 与 WPILib 官方文档冻结了配置/API/边界语义，Feedback Systems 与本仓库 VOL 01 提供控制理论入口；本页补充的 conditional-integration/back-calculation 公式与 probe 矩阵明确标为实现合同。source gate 通过但保留 `WARN`，下一步只生成 CODE‑VLA‑007 knowledge，题卡继续后置。

## References

1. [ROS 2 control PID controller userdoc](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html)。
2. [WPILib PIDController documentation](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/controllers/pidcontroller.html)。
3. [Feedback Systems](https://fbsbook.org/)。
4. 本仓库 [VOL 01 advanced-control fact review](vol_01_batch3_advanced_control_independent_fact_review.html)。
