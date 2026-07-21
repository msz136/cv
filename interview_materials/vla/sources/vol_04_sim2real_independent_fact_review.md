# VOL 04 Audit D：Sim2Real 独立事实复核

> 状态：`independent_fact_reviewed / Audit D / public_facts_reconciled / PASS WITH WARNING`  
> 复核日期：2026-07-20  
> 证据截止：2026-07-20  
> 范围：重新获取 10 份固定 arXiv PDF，固定 MuJoCo / OpenCV / robosuite 的官方源码与文档快照，复核 visual/sensor、dynamics、control/timing、contact/compliance、task/protocol、safety/recovery 六层 reality gap，以及 DR、SysID、SimOpt、UP-OSI、RMA、residual、chance constraint、recovery 与五项目真实性边界。  
> Bounded slice：本页只完成 Audit D 独立复核与必要状态同步；不新增知识节点或题卡，不启动 PER-019，不修改 269 张题卡的 `unseen` 状态，不创建 `coaching_state.md`。

## 1. 结论先行

原 [Sim2Real Claim-to-Mechanism Audit D](vol_04_sim2real_claim_to_mechanism.html) 的主干事实成立：Sim2Real 不能缩成“加 domain randomization”，至少要把视觉/传感器、动力学、控制/时序、接触/柔顺、任务/协议与安全/恢复分成六个可测合同。Domain randomization（DR）不是越宽越好；System identification（SysID）与 DR 不是二选一；SimOpt 更新的是能解释 real/sim behavior discrepancy 的 simulator-parameter distribution；UP-OSI 显式估计 dynamics parameter，RMA 估计 task-relevant latent，二者都不等于 rollout 内更新 policy weights；residual policy、chance constraint 与 learned recovery 也都带有前提，不能包装成通用稳定性或零风险保证。[1]–[13]

本轮 verdict 为 **PASS WITH WARNING**，不是无条件 PASS，原因有五类：

1. 六层 taxonomy、range provenance、latency decomposition、matched test、queue flush 与 layered safety state machine 中有工程综合；它们与一手来源一致，但不是某篇论文原封不动的定理或标准。
2. MuJoCo `stable` HTML 只固定了响应内容；页面元数据没有给出可验证的 build commit。本轮另固定 `3.10.0@28009f9` 的 RST 源码，但不声称 `stable` HTML 与该 tag 是同一 build。
3. OpenCV 的 reprojection error 只衡量标定点拟合；它不自动证明部署时 hand-eye extrinsics、mounting、timestamp、resize/crop 与 action frame 正确。[12]
4. residual policy 不自动继承 base controller 的稳定性；未校准 ensemble/disagreement 只能叫 risk heuristic；Recovery RL 是 learned shield，不是 zero-risk theorem。[7]–[9]
5. 五项目目前只有 simulator、offline data、接口、诊断与高层取消/补偿证据；没有形成“真机 calibration + latency/contact measurement + controller/limits + real rollout + incident/E-stop + ownership”的协议完整 bundle。

因此，安全口述仍是“我能按六层合同设计 Sim2Real 诊断与实验矩阵，并在本地 simulator/接口材料上做证据审计”，不能说“已完成真机 Sim2Real 部署”“已证明安全”或把公开方法写成个人原创。

## 2. 独立来源冻结

### 2.1 十份固定 PDF

本轮从固定 arXiv revision 重新下载 10 份 PDF，使用本地 bytes 计算 SHA-256，并逐页抽取文本检查纯空白页；合计 **124 页、0 个纯空白页**。SimOpt 第 3 页、Minitaur 第 5 页与 RMA 第 2 页另经 PNG 视觉抽查，双栏顺序、公式、图注和正文均可读。

| Paper | 固定 revision | bytes | pages / blank | SHA-256 |
| --- | --- | ---: | ---: | --- |
| UP-OSI | `1702.02453v3` | 1,012,357 | 10 / 0 | `F4ABCAA147175A471B6FA217758AECD80D42DF11F6F19B70A7DFBA66021D24CA` |
| Domain Randomization | `1703.06907v1` | 4,066,798 | 8 / 0 | `3FC98C5F4CEA050686D45858E647E1B704492121FDAE80F8FCD5D560C107F11F` |
| Cautious MPC | `1705.10702v4` | 1,817,694 | 12 / 0 | `2A38976CA6B6ADFB6DD9CF4F85AB9039E46666C2DD263F887E7F54DDCBD0BC36` |
| Dynamics Randomization | `1710.06537v3` | 2,845,918 | 8 / 0 | `A15CB24630A11218865027024AE2353F80F46D40371B42DCCB2B24E9D00D62D8` |
| Minitaur Sim2Real | `1804.10332v2` | 1,062,958 | 11 / 0 | `455EA9154D6C5E905601F91E71EC9F8FD0A348E7BE639E1019FFE1D941B7FF76` |
| Dexterous In-Hand Manipulation | `1808.00177v5` | 4,590,851 | 27 / 0 | `DA6EC44DD0941D674EC58334FF630F83D7BD19E6062AB2837CCFA0B3B94F6F73` |
| SimOpt | `1810.05687v4` | 5,492,359 | 10 / 0 | `5DDE7AD391342C29CDCB80C3728389A59712E6798A21FC5A8F4B5D82E4BAF245` |
| Residual RL | `1812.03201v2` | 2,959,124 | 8 / 0 | `C6279120F9E0A799A9D7A943A5624A5738250E588F99C5FC8A9FAC28E2039641` |
| Recovery RL | `2010.15920v2` | 7,929,814 | 15 / 0 | `3404EF792695647E3900D0E36E608FCF23D261E75F45D16C277206064F2D9AF5` |
| RMA | `2107.04034v1` | 16,534,863 | 15 / 0 | `D8660DA881851756287EFAB24D85F5C629BA97878F70297EB429A8E8A9A57846` |

这里只引用事实与方法边界，不复用论文图表或代码；PDF identity 不证明任何本地项目执行过对应方法。

### 2.2 MuJoCo、OpenCV 与 robosuite

| 来源 | 固定 identity | 本轮重新获取 | 结论与边界 |
| --- | --- | --- | --- |
| MuJoCo source | tag `3.10.0` → commit `28009f9105cd92784b7b0b30c0605a5e29107a77` | `modeling.rst` SHA `F13C1C15...41893` / blob `5492C407...DE4`；`XMLreference.rst` SHA `A6EA3CE3...FD6` / blob `72842F40...B86`；`computation/index.rst` SHA `19D8F088...DE4D` / blob `A0D890F1...3F6` | 支持 contact、friction、`solref/solimp`、solver、timestep 与 sensor-delay 语义；不证明本地 simulator build |
| MuJoCo stable HTML | accessed 2026-07-20 | Modeling `50523078...15DA`；Computation `94228BFD...3AC`；XML Reference `C816A678...229B` | 响应 SHA 与既有 source freeze 一致；页面只标记 `stable`，不与 `3.10.0` build 等同 |
| OpenCV calibration source | commit `f7dd7df170add1655de75b5e95f20f41d2a88293` | `py_calibration.markdown` SHA `72F48A26...03C4` / blob `423F46A2...D6DB` | 支持 pinhole intrinsic/extrinsic、radial/tangential distortion 与 reprojection error；不证明部署标定正确 |
| robosuite | tag `v1.5.1` → commit `51cc01785bab80ffeed20da15e67d7dd4140e76a` | controller RST SHA `843563FE...2314`；gripper base SHA `B4582D44...6CB`；Panda gripper SHA `DF0449A9...AAB8D` | 支持 action split、policy/simulation frequency 与 Panda `-1=open, 1=closed`；不能外推到真实 Panda 或任意 LIBERO/RoboCasa fork |
| licenses | fixed repository files | MuJoCo/OpenCV LICENSE SHA `CFC7749B...23D30`；robosuite LICENSE SHA `177978CB...D9CBA` | MuJoCo/OpenCV 为 Apache-2.0，robosuite 为 MIT；论文、代码、模型与数据许可不能互相替代 |

GitHub 匿名 REST API 本轮命中共享出口限流，因此 tag 解析使用 `git ls-remote`，文件通过 immutable commit URL 获取并计算 Git blob；没有把 mutable branch HEAD 当作固定版本。

## 3. Paper-to-claim 独立复核

| Claim | 直接定位 | 独立结论 | 不能外推 |
| --- | --- | --- | --- |
| visual DR factors 与 ablation | Tobin pp.1, 3, 5 | camera、lighting、pose、texture、distractor 与 ablation 可定位 | object localization / grasp demo 不证明任意 VLA transfer |
| 95 个 dynamics parameters、timestep/latency、recurrent implicit SysID | Peng p.4 | 95 是特定 pushing setup；episode/step cadence 与 memory 边界成立 | 不能抄作默认参数表或保证 target support |
| real/sim trajectory discrepancy 与 KL-bounded distribution update | SimOpt p.3 | SimOpt 更新 distribution，并明确说过宽 distribution 可能含 infeasible scenarios 或过度保守 | 不等于恢复唯一真实物理参数；需要安全 real rollout authority |
| actuator、latency、measurement + margin、robustness–optimality | Tan pp.1, 5, 7 | 延迟会缩小真实闭环稳定区；实测中心与 DR coverage 互补 | Minitaur 数值与范围不能直接迁移到 manipulation |
| history → dynamics parameter → universal policy | UP-OSI pp.1–2 | 显式 OSI 估计有语义的 parameter context | 论文实验主要在 simulation；不是 policy-weight update |
| privileged extrinsics latent、history adaptation、异步部署 | RMA pp.1–3 | 训练期 privileged encoder 与部署期 10 Hz adaptation / 100 Hz base policy 可定位 | legged latent 不自动适配 image VLA；stale latent 仍需协议 |
| conventional/base controller + learned residual | Residual RL pp.1–3 | 真实 contact-rich assembly 支持 residual decomposition | 论文没有给任意 residual 的通用稳定性保证 |
| task policy / recovery policy 与 future-risk threshold | Recovery RL pp.1–3 | learned risk critic 与 recovery switch 成立 | empirical safety improvement 不等于 zero-violation theorem |
| nominal dynamics + GP residual + chance constraint | Cautious MPC pp.1–3 | uncertainty propagation 与概率约束成立 | 依赖 GP/model/distribution assumptions；不是任意 ensemble variance 即可 |
| calibration + extensive randomization + memory | OpenAI pp.3–6 | tendon/contact/sensor mismatch 与 recurrent adaptation 边界成立 | Shadow Hand recipe 不直接推广到 Panda/gripper |

两处原审计措辞需要继续保留限定语：SimOpt 是 **behavior/distribution adaptation**，不是 exact parameter recovery；Residual RL 的真实硬件结果是方法可行性证据，不是 stability inheritance 证明。

## 4. 六层 reality-gap 合同

用一个最小闭环把 sensing、dynamics、controller 与 delay 分开：

\[
o_t^{\mathrm{real}}
=h_{\psi_r}\!\left(x_{t-\tau_s}^{\mathrm{real}}\right)+\epsilon_t,
\qquad
x_{t+1}^{\mathrm{real}}
=f_{\xi_r}\!\left(
x_t^{\mathrm{real}},
\mathcal C_{\kappa_r}\!\left(a_{t-\tau_a}\right)
\right).
\]

变量解释：\(h_{\psi_r}\) 是真实 sensor/image-formation chain，\(f_{\xi_r}\) 是 dynamics/contact，\(\mathcal C_{\kappa_r}\) 是 low-level controller/actuator；\(\tau_s,\tau_a\) 分别是 sensing 与 action-path delay。实现映射：Audit D 的 trace 必须把 camera timestamp、policy、network、queue、controller apply 与下一帧关联。该式是工程抽象，不是某篇论文的原式。

| 层 | 主要 mismatch | first evidence | 不能拿什么替代 |
| --- | --- | --- | --- |
| Visual / sensor | intrinsics/extrinsics、distortion、exposure、blur、occlusion、timestamp、preprocess | calibration bundle、replay、factor ablation | 只看 color jitter 或 sim image quality |
| Dynamics | mass、inertia、damping、motor strength、payload、drift | free-space tracking、SysID residual、parameter manifest | 接触失败时盲调所有 mass/friction |
| Control / timing | controller type/frame/unit/gain、frequency、latency、ZOH、chunk queue | capture-to-apply trace、target/actual action、frequency sweep | 只报一次 inference latency |
| Contact / compliance | sliding/torsional/rolling friction、softness、solver、timestep、pad/object deformation | press/slip/hold/lift micro-bench | 单一 friction scalar |
| Task / protocol | reset/init/layout/object/language/horizon/success predicate | immutable protocol tuple、matched seeds/trials | 同名 task 或 sim score |
| Safety / recovery | OOD、constraint、uncalibrated risk、stale action、collision | limit registry、shield/recovery/fallback/E-stop trace | action clipping 或训练 reward |

六层是独立诊断维度，但不是互不作用：camera timestamp 会进入 timing，controller gain 会改变 contact，task reset 会改变 contact exposure。正确做法是记录 first divergence，再确定下一层 probe。

## 5. DR、SysID 与 SimOpt

### 5.1 “越宽越好”被一手来源否定

固定 simulator distribution \(p_\phi(\xi)\) 时，policy 学到的是分布内期望：

\[
\theta^*(\phi)
=\arg\max_\theta
\mathbb E_{\xi\sim p_\phi}
\left[J\!\left(\pi_\theta;f_\xi\right)\right].
\]

变量解释：\(\xi\) 是 simulator parameters，\(J\) 是 closed-loop return。实现映射：必须保存参数单位、support、相关性、采样 cadence、rejection 与 realized samples。SimOpt p.3 和 Tan p.5/p.7 都明确支持 coverage 与 nominal optimality 的取舍，所以“分布越宽越稳”是错误答案。[3][4]

### 5.2 SysID 给中心，DR 覆盖 residual uncertainty

可测且可辨识的 mass、latency、motor response 先用测量或 fit 定中心；population variation、wear、temperature、payload、不可辨识耦合与 model-form error 再用条件分布覆盖。fit trajectory 好只证明 behavior match，不证明每个 physical parameter 都是真值。

SimOpt 的 outer loop 可写为：

\[
\phi_{k+1}
=\arg\min_\phi
\mathbb E_{\xi\sim p_\phi}
\left[D\!\left(\tau^{\mathrm{real}},\tau^{\mathrm{sim}}(\xi)\right)\right]
\quad
\mathrm{s.t.}\quad
D_{\mathrm{KL}}\!\left(p_\phi\,\|\,p_{\phi_k}\right)\le\varepsilon.
\]

变量解释：\(D\) 比较 real/sim observable trajectories，KL constraint 限制 distribution update。实现映射：这对应 SimOpt Algorithm 1 的 real rollout、sim rollout、cost 与 update distribution；它不要求返回唯一真实 \(\xi_r\)。本地若没有安全 real rollout、同步 observation 与 immutable checkpoint，就没有执行 SimOpt 的 authority。[3]

## 6. Camera、timing、contact 与 controller

### 6.1 Calibration error 不等于 deployment correctness

Pinhole projection 为：

\[
s\begin{bmatrix}u\\v\\1\end{bmatrix}
=K\,[R\mid t]\,
\begin{bmatrix}X_w\\1\end{bmatrix},
\qquad
K=\begin{bmatrix}
f_x&0&c_x\\
0&f_y&c_y\\
0&0&1
\end{bmatrix}.
\]

变量解释：\(K\) 是 intrinsics，\([R\mid t]\) 是 world-to-camera extrinsics，\((u,v)\) 是 image coordinates。实现映射：OpenCV 还给出 radial/tangential distortion 与 reprojection error；部署还需 hand-eye frame、resize/crop 后的 \(K\)、mounting revision 和 timestamp。reprojection error 低不能替代这些 checks。[12]

### 6.2 Latency 必须拆 critical path

\[
\tau_a
=\tau_{\mathrm{capture/transport}}
+\tau_{\mathrm{preprocess}}
+\tau_{\mathrm{policy}}
+\tau_{\mathrm{network}}
+\tau_{\mathrm{queue}}
+\tau_{\mathrm{controller/actuator}}.
\]

变量解释：每项都应记录 distribution 与 tail，而不是只相加平均值。实现映射：chunked VLA 还要保存 observation version、action age、\(H\)、执行前缀 \(K_e\)、deadline、stale/drop/flush/ack。Tan 直接证明未建模 latency 会使真实 feedback oscillate；robosuite source 证明 policy reference 会在多次 simulation/controller step 中保持，但它只是 simulator 语义。[4][13]

### 6.3 Contact 不是一个 friction scalar

MuJoCo fixed source 明确说明：geom 的 tangential/torsional/rolling 三类 friction 会扩成 contact 的五个 coefficients；`solref`、`solimp`、priority/mixing、cone、solver、timestep 与 no-slip settings 都能改变结果。Panda gripper source 的 `-1=open, 1=closed` 只绑定 robosuite `v1.5.1`；真实 robot driver、另一个 simulator 或本地 adapter 必须重新做 sign/range/aperture/force/current round trip。[11][13]

因此 first-divergence 顺序应是：先 action/parser/controller free-space，再 actuator/latency，再接触触发、press/slip/hold/lift；不能用调 friction 掩盖 axis、unit 或 controller mismatch。

## 7. Adaptation、residual 与 safety 边界

| 方法 | rollout/test-time 更新对象 | policy weights 当场改变？ | 最小 authority | 主要警告 |
| --- | --- | --- | --- | --- |
| Fixed DR | simulator sample | 否 | simulator only | support/range 可能错误 |
| SimOpt | simulator distribution | 否 | 少量安全 real trajectories | behavior metric shortcut、real cost |
| UP-OSI | explicit dynamics parameter context | 否 | history + sim-supervised parameter | identifiability / model assumption |
| RMA | task-relevant latent context | 否 | history + privileged sim teacher | stale/OOD latent、legged→VLA gap |
| Residual policy | executed action correction | residual weights通常离线训练 | reliable base + bounded authority | 不自动继承稳定性 |
| DAgger / real fine-tune | dataset / model weights | 训练轮次改变 | expert/reward + safe collection + rollback | hardware/data cost、catastrophic forgetting |

Residual composition 可写为：

\[
u_t
=\operatorname{sat}\!\left(
u_{\mathrm{base}}(s_t)
+\alpha\,u_{\mathrm{res},\theta}(s_t,o_t)
\right).
\]

变量解释：\(\alpha\) 与 saturation 只限制 residual authority，不构成稳定性证明。实现映射：需要 residual norm/rate/energy、base-only/residual-on paired arms、fallback 与 saturation trace；当前五项目没有这组 bundle。[7]

对概率安全约束：

\[
\Pr\!\left(
g_j(x_{t+k},a_{t+k})\le 0,
\ \forall j,k
\right)\ge 1-\delta.
\]

变量解释：\(g_j\) 是 joint/workspace/collision/force 等 constraints，\(\delta\) 是允许风险。实现映射：Cautious MPC 用 GP residual 与 uncertainty propagation 支撑概率声明；VLA 的 ensemble spread 若没有 reliability/risk-coverage/false-safe calibration，只能当 heuristic。[9]

Recovery RL 的 learned switch 可抽象为：

\[
a_t=
\begin{cases}
\pi_{\mathrm{task}}(s_t),
&\widehat Q_{\mathrm{risk}}(s_t,a_t^{\mathrm{task}})\le\epsilon_{\mathrm{risk}},\\
\pi_{\mathrm{rec}}(s_t),
&\text{otherwise}.
\end{cases}
\]

变量解释：risk critic 预测 future constraint violation，recovery 尝试返回 recoverable region。实现映射：risk event 必须同时阻止当前 proposal、flush/ack queued chunk，并按 hysteresis、timeout、fallback/E-stop state machine 处理；论文不提供任意 VLA 的 zero-risk guarantee。[8]

## 8. 十二个确定性 probes

本轮对几何、接口、范围与 safety state 做了 12 个纯确定性 probe；**12/12 PASS**。这些 probe 验证 contract arithmetic，不代替真实 calibration、simulator rollout、real robot、uncertainty calibration 或 ownership。

| Probe | 结果 |
| --- | --- |
| 六层 label 唯一性 | PASS；6 个 layer / 6 个 unique names |
| pinhole identity projection | PASS；\((0,0,1)\to(0,0)\) |
| zero-distortion round trip | PASS；\((0.1,-0.2)\) 不变 |
| MuJoCo 3→5 friction expansion | PASS；tangential/rolling 分别复制 |
| Panda gripper sign contract | PASS；fixed source 含 `-1 => open, 1 => closed` |
| composite action split + multi-clock text | PASS；fixed controller RST 同时命中 |
| latency additive decomposition | PASS；`4+3+2+5=14 ms` |
| stale-chunk TTL | PASS；age `1.0 s` 超过 `0.5 s`，拒绝 |
| overwide-DR toy counterexample | PASS；期望 reward 在 \(\sigma=0\) 最大，不随宽度单调增加 |
| SimOpt Gaussian KL ball | PASS；小更新接受、大更新拒绝 |
| UP-OSI/RMA/SimOpt update-object classifier | PASS；parameter / latent / distribution，不是 weights |
| Gaussian one-sided chance threshold | PASS；\(z=1.645\) 对应约 95% |

核心复核逻辑可压缩为：

```python
def audit_sim2real_contract(trace, limits):
    # 先验证 observation/action 的 frame、unit、version 与时间戳。
    assert trace.camera_contract_ok and trace.action_roundtrip_ok

    # action age 超过 TTL 时拒绝整段 chunk；风险事件必须 flush queue。
    if trace.now - trace.action_timestamp > limits.ttl:
        trace.action_queue.clear()
        return "STALE_REJECT"

    # free-space 未闭合前，不允许把失败归因到 friction/contact。
    if not trace.free_space_tracking_ok:
        return "CHECK_CONTROLLER_ACTUATOR_LATENCY"

    # contact 只在 sign/range/controller 已闭合后分解。
    if trace.contact_first_divergence:
        return "RUN_PRESS_SLIP_HOLD_LIFT_MICROBENCH"

    # uncertainty 未校准时只能作为 heuristic，不写 chance guarantee。
    return "RISK_HEURISTIC" if not trace.risk_calibrated else "GUARDED_EXECUTION"
```

## 9. 五项目本地证据与 truth boundary

本轮重新计算 [Evidence Manifest](../evidence/evidence_manifest.html) 与五份 claim–evidence inventory 的 SHA，并做有界 filename/content 复核。以下“缺失”只指审计范围内没有协议完整 bundle，不代表用户其他机器、远端或未归档介质一定不存在。

| 项目 | 本轮 identity / 直接发现 | 当前支持 | 不支持 |
| --- | --- | --- | --- |
| Robot Harness | inventory SHA `71C3B62F...A797F`；项目根 3,726 个文件中有 25 个 calibration/hardware filename hit，均位于 `third_party/sensebot_robotsystem` | 高层 scope、mutex、cancel、timeout、best-effort compensation；第三方机器人资产存在 | 不能把 third-party 文件名写成候选人 Sim2Real 实现；无本项目 calibration→controller→real rollout→incident bundle |
| OPD / VLM Grounding | inventory SHA `C002B227...9AFA`；317 个文件 filename scan 0 个 Sim2Real/hardware hit | token-space teacher/student rollout、grounding 数据与评估 | 不是 robot-state DAgger、SysID、real adaptation 或 hardware deployment |
| OpenPiVLA | inventory SHA `13023578...132A`；`aloha_sim_real_rollout` summary 明确为 `pi0_aloha_sim`、`gym_aloha/AlohaTransferCube-v0`、3 episodes、2/3 simulator success | official-checkpoint simulator diagnostic 与 controller/action interface | 文件名中的 `real_rollout` 不是 real hardware；不能绑定 formal Qwen、97.4 或 Sim2Real transfer |
| Cosmos / WAM | inventory SHA `2362311B...AFB4`；base/trained manifests SHA `63A51867...3A86` / `809AE4F8...55CC`，均 `kind=cosmos_policy_robocasa_action_rollout`、offscreen renderer、`success=false` | RoboCasa simulator controller/config、300-step failure diagnostic、offline real-demo target videos | “real RoboCasa renders”/`real_primary` 不是 physical robot rollout；无 checkpoint binary、calibration、real latency/contact/safety |
| UWM / LIBERO | inventory SHA `C35C41D6...8A9`；156 个项目文件，contact filename hits 是 RoboCasa diagnostic contact sheets | simulator finetune/rollout、action adapter、protocol 与 failure instrumentation | 不支持 physical contact、Sim2Real uplift、real recovery 或 safety completion |

Evidence Manifest 本轮 SHA 为 `8C870E35736ECCF6201BECF19A1B8E6C3B2367DC225066268724947B70169083`。五项目 ownership ledger 都仍需候选人逐项确认：Git author、文件存在、上游机制、Codex/工具实现或第三方资产不能自动升级为个人独立设计与实现。

当前安全口述：

> “我把 Sim2Real 拆成 visual/sensor、dynamics、control/timing、contact、task/protocol、safety/recovery 六层，先做 frame/unit/timestamp/action round trip，再做 free-space、latency/actuator 与 contact micro-bench，最后才做 matched real rollout。公开论文支持 DR、SysID、SimOpt、OSI/RMA、residual 和 recovery 的机制边界；我的项目材料目前主要是 simulator、接口和诊断证据，没有协议完整的真机 bundle，所以我讲设计与审计方法，不把它说成已经完成硬件迁移。”

## 10. Source → Knowledge → Card reconciliation

| Cluster | Source / Knowledge / Card | 独立结论 | 保留 warning |
| --- | --- | --- | --- |
| WM-031 taxonomy | 六层/first-divergence | PASS AS SYNTHESIS | 原子 source 早期写“五层”；安全/恢复作为第六响应层后形成六层 Audit D 合同，需说明是工程综合 |
| WM-032 visual DR | relevant support、label/geometry consistency、overwide gate | PASS | Tobin/ADR/SimOpt 不能证明本地 visual transfer |
| WM-033 SysID + DR | nominal center、residual uncertainty、identifiability、matched arms | PASS | fit 好不等于参数真；无本地 real excitation bundle |
| WM-034 timing/controller | multi-clock、action age、actuator/controller mismatch | PASS | single inference time 不能替 capture-to-apply latency；无本地真实 tail |
| WM-035 camera/sensor | \(K,R,t\)、distortion、photometric/temporal/noise/occlusion | PASS | reprojection error 不等于 deployment extrinsics 正确 |
| WM-036 contact/gripper | friction/compliance/solver/gripper round trip | PASS | robosuite sign 是 simulator/version-specific；无 real contact trace |
| WM-037 adaptation | residual / UP-OSI / RMA / SimOpt / DAgger 分层 | PASS | 不把 token rollout、offline finetune 或 sim rollout叫 real online adaptation |
| WM-038 safety | constraint、calibration、CBF/training/recovery/fallback/E-stop | PASS WITH WARNING | learned risk、CPO、clipping、高层 cancel 都不是 physical zero-risk guarantee |
| WM-040..044 | metric ladder、matched ablation、consistency、first failure、evidence audit | PASS | offline/sim proxy 不能替 closed-loop real success；ownership仍是独立 gate |

知识页与题卡无需重写；它们已保留上述 boundary。`VLA-WM-031..038` 原子题卡和 `VLA-WM-040..044` 聚合题卡继续保持 `unseen`，独立 fact review 不等于 oral mastery。

## 11. 审查状态与下一步

Audit D 的 public paper/source facts、official semantics、12 probes、local truth boundary 与 source→knowledge→card reconciliation 已完成，可从 `independent_review_pending` 提升为 `independent_fact_reviewed / PASS WITH WARNING`。这不改变 VOL 04 整卷 `WARN`，也不证明任何项目完成真机 Sim2Real。

仍开放：

- 收集每个目标平台的 camera serial/intrinsics/extrinsics/hand-eye、mounting revision、timestamp 与 preprocessing manifest；
- 收集 physics/controller/policy/firmware Hz、capture-to-apply latency distribution、actuator fit/held-out residual 与 queue stale/drop/flush/ack trace；
- 收集 material/object/gripper/contact/solver manifest，以及 press/slip/hold/lift/transport matched micro-benches；
- 在安全 authority 下补 fixed-checkpoint、fixed-init/controller 的 sim/real paired trials，报告 denominator、置信区间与 failure family；
- 补 constraint registry、calibrated risk、shield/recovery/fallback/E-stop、near-miss/incident/reset/approval log；
- 由候选人确认五项目逐文件设计、实现、运行、审查与工具/协作者角色；真实口述前不改变 mastery，不创建 coaching state。

下一 bounded slice 优先进行一题真实口述；若继续文档事实复核，则 VOL 04 Audit A–E 已全部完成独立 review，应转向 repository completion / oral gate，而不是生成新的 Sim2Real 节点或启动 PER-019。

## References

1. Tobin et al., [*Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World*](https://arxiv.org/abs/1703.06907v1), arXiv v1, 2017。
2. Peng et al., [*Sim-to-Real Transfer of Robotic Control with Dynamics Randomization*](https://arxiv.org/abs/1710.06537v3), arXiv v3, 2018。
3. Chebotar et al., [*Closing the Sim-to-Real Loop: Adapting Simulation Randomization with Real World Experience*](https://arxiv.org/abs/1810.05687v4), arXiv v4, 2019。
4. Tan et al., [*Sim-to-Real: Learning Agile Locomotion For Quadruped Robots*](https://arxiv.org/abs/1804.10332v2), arXiv v2, 2018。
5. Yu et al., [*Preparing for the Unknown: Learning a Universal Policy with Online System Identification*](https://arxiv.org/abs/1702.02453v3), arXiv v3, 2017。
6. Kumar et al., [*RMA: Rapid Motor Adaptation for Legged Robots*](https://arxiv.org/abs/2107.04034v1), arXiv v1, 2021。
7. Johannink et al., [*Residual Reinforcement Learning for Robot Control*](https://arxiv.org/abs/1812.03201v2), arXiv v2, 2018。
8. Thananjeyan et al., [*Recovery RL: Safe Reinforcement Learning with Learned Recovery Zones*](https://arxiv.org/abs/2010.15920v2), arXiv v2, 2021。
9. Hewing et al., [*Cautious Model Predictive Control using Gaussian Process Regression*](https://arxiv.org/abs/1705.10702v4), arXiv v4, 2019。
10. OpenAI et al., [*Learning Dexterous In-Hand Manipulation*](https://arxiv.org/abs/1808.00177v5), arXiv v5, 2019。
11. Google DeepMind, [MuJoCo `3.10.0@28009f9`](https://github.com/google-deepmind/mujoco/tree/28009f9105cd92784b7b0b30c0605a5e29107a77)，并参照固定响应的 [Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html)、[Computation](https://mujoco.readthedocs.io/en/stable/computation/index.html) 与 [XML Reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)。
12. OpenCV, [`py_calibration.markdown@f7dd7df`](https://github.com/opencv/opencv/blob/f7dd7df170add1655de75b5e95f20f41d2a88293/doc/py_tutorials/py_calib3d/py_calibration/py_calibration.markdown)。
13. ARISE Initiative, [robosuite `v1.5.1@51cc017`](https://github.com/ARISE-Initiative/robosuite/tree/51cc01785bab80ffeed20da15e67d7dd4140e76a)，重点复核 controller 与 Panda gripper source。
14. [VOL 04 Sim2Real Claim-to-Mechanism Audit D](vol_04_sim2real_claim_to_mechanism.html)。
15. [WM-031 Reality-gap](vol_04_wm031_reality_gap_taxonomy_source_freeze.html)、[WM-032 Visual DR](vol_04_wm032_visual_domain_randomization_relevance_source_freeze.html)、[WM-033 Dynamics SysID](vol_04_wm033_dynamics_randomization_system_identification_source_freeze.html)、[WM-034 Timing](vol_04_wm034_control_latency_actuator_controller_mismatch_source_freeze.html)、[WM-035 Camera](vol_04_wm035_camera_sensor_modeling_source_freeze.html)、[WM-036 Contact](vol_04_wm036_contact_friction_compliance_gripper_source_freeze.html)、[WM-037 Adaptation](vol_04_wm037_adaptation_method_selection_source_freeze.html) 与 [WM-038 Safety](vol_04_wm038_uncertainty_safety_fallback_recovery_source_freeze.html)。
16. [VOL 04 Aggregate Knowledge](../knowledge/vol_04_world_model_sim2real.html) 与 [Question Bank](../questions/vol_04_world_model_sim2real.html)。
17. [Evidence Manifest](../evidence/evidence_manifest.html) 与五项目 claim–evidence inventories。
