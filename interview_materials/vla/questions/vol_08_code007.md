# VOL 08 CODE-VLA-007 原子手撕题卡：PID Update with Anti-windup

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`CODE-VLA-007`  
> 难度：L2 1 题  
> 优先级：P0  
> 练习状态：`unseen`  
> 前置知识：[CODE-007 Knowledge](../knowledge/vol_08_code007_pid_anti_windup.html)；来源边界见 [CODE-007 Source Freeze](../sources/vol_08_code007_pid_anti_windup_source_freeze.html)。

## 手写带 anti-windup 的离散 PID update

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>CODE-VLA-007</b> · 请实现离散 PID update，处理输出饱和、积分 anti-windup、reset 与测试。</summary>

**面试意图**：判断你能否冻结 `dt`、error sign、内部 state、output/i limits 与 anti-windup 分支，并写出可诊断的更新，而不是只把 `P+I+D` 相加。

**30 秒回答**：固定 e、dt、state 和 limits，算 u_unsat=P+I+D，再 clip 得 u_sat。conditional integration 在饱和且误差继续推向 rail 时冻结、反向时放行；back-calculation 用 (u_sat−u_unsat)/Tt 回拉积分。记录 trace，测 dt、饱和、reset、replay。

**机制展开（约 2 分钟）**：令 i_state 为积分输出贡献，u_unsat=Kp·e+i_state+Kd·Δe/dt，u_sat=clip(u_unsat)。conditional integration 按饱和方向决定是否累加 Ki·dt·e；back-calculation 用 dt·(Ki·e+(u_sat−u_unsat)/Tt) 回拉。u_clamp、i_clamp、IZone、reset 不等价，reset 绑定 episode/lease epoch。返回 action、state、trace，检查 dt、broadcast、NaN 和 limits。VLA 先绑定 action schema/norm/unit；没有 PID 或 tuning artifact，不能声称真机闭环。

**诊断 / 证据**：按 `dt/finite → error sign → state/reset → u_unsat → clamp → anti-windup branch → dtype/device → controller ack` 定位。做 `K_i/K_d=0`、上/下饱和、误差反向、`u_min=u_max`、reset、continuous input、fixed replay 八类 probe；记录 `e/p/i/d/u_unsat/u_sat/branch/dt/reset_reason`。白板答案应说明 `Tt` 与单位；runtime 还需 matched step/reversal、noise/jitter、episode epoch 与 action-limit artifact。现有项目只能作为接口 hook，不能升级为 PID ownership 或 robot success。

**项目挂钩**：OpenPiVLA 可连接 action shape/normalizer/parser；Robot Harness 可连接 timeout/compensation；WAM 可连接 controller/chunk diagnostic；OPD 可连接 route/teacher schedule；UWM/LIBERO 可连接 launcher/task mapping。五项目均没有 CODE-007 local PID implementation、joint feedback trace、anti-windup tuning log 或 matched controller ablation，回答时保持 evidence boundary。

**追问树**：为什么 output clamp 不会自动阻止积分增长？conditional integration 如何判断“误差正在把输出拉回”？back-calculation 的 Tt 如何调？i_state 是 Ki 前还是 Ki 后？measurement derivative 和 error derivative 有何差别？normalized action 上做 PID 还是 physical action 上做？lease/episode epoch 改变时 state 怎么处理？如何证明不是 controller limit 或单位错误？

**易错点**：把 `u_clamp` 当 anti-windup；所有饱和都冻结积分；忽略 error sign；`dt` 固定写死；把 i_state 与 ∫e 混为一谈；不同单位复用 gain；reset 不清 derivative；用最终 action 或 simulator rollout 冒充 tuning/真机证据。

**危险答案**：说“clip 输出就不会 wind-up”“ROS/WPILib 的 PID API 证明我完成了 VLA controller”“Tt 越小越快所以一定更好”“normalized action 直接套 physical gain”“一次 rollout 成功就证明 anti-windup 稳定”。

**来源**：[1][2][3]　**练习状态**：unseen

</details>

## 参考来源

1. [CODE-007 Knowledge](../knowledge/vol_08_code007_pid_anti_windup.html)：PID state、clamp、conditional/back-calculation、reset、probe 与项目边界。
2. [CODE-007 Source Freeze](../sources/vol_08_code007_pid_anti_windup_source_freeze.html)：ROS 2 control、WPILib、Feedback Systems 与 8 probe contract。
3. 本仓库 [VOL 01 advanced-control fact review](../sources/vol_01_batch3_advanced_control_independent_fact_review.html) 与五项目 evidence inventories。
