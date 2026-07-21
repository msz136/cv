# VOL 03 Source Audit E：Flow Matching / π0 Time–Sign 独立事实复核

> 状态：`independent_fact_reviewed / audit_e / theorem_endpoint_time_sign_checked / PASS WITH WARNING`
> 审查日期：2026-07-19
> 冻结版本：Flow Matching paper arXiv `2210.02747v2`；π0 paper arXiv `2410.24164v4`；OpenPI commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`。
> 结论先行：Flow Matching v2 的 Theorem 2 证明 FM 与 CFM objectives 在假设下相差一个与参数无关的常数，因此参数梯度相同；原论文 OT conditional path 在 data endpoint 保留 `sigma_min` 噪声。π0 paper 与 frozen OpenPI 使用互为反向的时间坐标和速度符号，配合相反积分步长后轨迹完全等价；10-step deterministic oracle 在两套约定下都恢复了同一 action endpoint。

## 1. 直接复核来源与固定摘要

| ID | 来源 | 本次直接读取内容 | 固定摘要 / Verdict |
| --- | --- | --- | --- |
| P01 | [Flow Matching v2 PDF](https://arxiv.org/pdf/2210.02747v2) | Eq. 9、Theorem 2、Eq. 20–23 | SHA-256 `5EEB39BA516396924ABA4787452F9D0ABDEE88467A4D0C264D9F66CAD0C5EE14` / `primary-verified` |
| P02 | [π0 v4 PDF](https://arxiv.org/pdf/2410.24164v4) | action path、velocity target、Euler sampling、shifted Beta | SHA-256 `FBDFBA56258BDBD220207BA63410C6C943E43A73E97A7A5A47CA0BC74204F821` / `primary-verified` |
| C01 | [`openpi/models/pi0.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0.py) | `compute_loss`、`sample_actions`、time/sign/dt | raw file SHA-256 `24B32D7C6ED5E409459AFA8CA5AF96A4DAE09C2DCDF48E828907E411F4F12342` / `official-code / frozen` |
| O01 | 本次 deterministic oracle | paper/code 10-step endpoint 与 Beta coordinate identity | `local-evidence / PASS` |

这些摘要只固定本次下载对象与 frozen raw file；它们不替代 arXiv revision、Git commit 或本地项目 checkpoint 的身份记录。

## 2. Theorem 2：相差常数与梯度相同

Flow Matching 的 marginal objective 与 Conditional Flow Matching objective 分别写为：

\[
\mathcal L_{\mathrm{FM}}(\theta)
=
\mathbb E_{t,\,x\sim p_t}
\left\|v_\theta(x,t)-u_t(x)\right\|_2^2,
\]

\[
\mathcal L_{\mathrm{CFM}}(\theta)
=
\mathbb E_{t,\,x_1\sim q,\,x\sim p_t(\cdot\mid x_1)}
\left\|v_\theta(x,t)-u_t(x\mid x_1)\right\|_2^2.
\]

变量与直觉：`FM` 监督通常不可直接计算的 marginal vector field；`CFM` 对每个 data endpoint 采 conditional path 与解析 velocity。论文 Theorem 2 的原始限定是：若对所有 \(x\in\mathbb R^d,t\in[0,1]\) 都有 \(p_t(x)>0\)，则两项目标相差一个与 \(\theta\) 无关的常数，因此

\[
\nabla_\theta\mathcal L_{\mathrm{FM}}(\theta)
=
\nabla_\theta\mathcal L_{\mathrm{CFM}}(\theta).
\]

面试中应说“期望目标相差参数无关常数、优化梯度相同”，不能说“每个样本的 target 或 loss 数值相同”。原 Audit E 的 gradient-equivalence 口径正确，本次补全了 theorem assumption 与 constant boundary。

## 3. 原论文 OT path 的 `sigma_min` endpoint

Flow Matching v2 Eq. 20 选择：

\[
\mu_t(x_1)=t x_1,
\qquad
\sigma_t=1-(1-\sigma_{\min})t.
\]

对应 sample path 与 conditional target 为：

\[
x_t=
\left[1-(1-\sigma_{\min})t\right]x_0+t x_1,
\qquad
\dot x_t=x_1-(1-\sigma_{\min})x_0.
\]

变量与端点：\(x_0\sim\mathcal N(0,I)\) 是 source noise，\(x_1\) 是 data sample；当 \(t=1\) 时 \(x_1+\sigma_{\min}x_0\)，即以 \(x_1\) 为均值、标准差为 \(\sigma_{\min}\) 的小 Gaussian。常背的

\[
x_t=(1-t)x_0+t x_1,
\qquad
\dot x_t=x_1-x_0
\]

是令 \(\sigma_{\min}=0\) 的 exact-endpoint 特例。原 Audit E 已正确区分 paper convention 与后续 package 的 exact-linear `CondOTProbPath`，本次直接 PDF 复核未发现需要反向修正的事实错误。

## 4. π0 paper 与 OpenPI code 的时间坐标

π0 paper 以 \(\tau=0\) 表示 noise、\(\tau=1\) 表示 action：

\[
A^\tau=\tau A+(1-\tau)\epsilon,
\qquad
u_{\mathrm{paper}}=A-\epsilon.
\]

变量与实现：\(A,\epsilon\in\mathbb R^{B\times H\times D}\)，论文从 \(A^0=\epsilon\) 用正步长 Euler 积分到 \(A^1=A\)，实验使用 10 steps、\(\delta=0.1\)。

frozen `pi0.py` 在 `compute_loss` 中使用：

\[
x_t=t\epsilon+(1-t)A,
\qquad
u_{\mathrm{code}}=\epsilon-A,
\]

并在 `sample_actions` 中从 \(t=1\) noise 以 \(\Delta t=-1/N\) 积分到 \(t=0\) action。令

\[
t=1-\tau,
\qquad
dt=-d\tau,
\qquad
u_{\mathrm{code}}=-u_{\mathrm{paper}},
\]

则每个 infinitesimal displacement 满足

\[
u_{\mathrm{code}}\,dt
=
u_{\mathrm{paper}}\,d\tau.
\]

因此三件事必须一起检查：time coordinate、velocity target sign、solver step sign。只看到 paper/code 时间相反不能判定 code 错误；若只反转其中一项，才会把 endpoint 推离 action。

## 5. Shifted Beta 换元

π0 Appendix 令 \(s=0.999\)，其采样可以写成：

\[
y\sim\operatorname{Beta}(1.5,1),
\qquad
\tau=s(1-y).
\]

OpenPI 的反向 time coordinate 因而是：

\[
t=1-\tau
=1-s+sy
=0.001+0.999y.
\]

这与 frozen code 的 `jax.random.beta(..., 1.5, 1) * 0.999 + 0.001` 精确对应。固定 \(y\in\{0,0.1,0.5,0.9,1\}\) 的 probe 均得到 \(t+\tau=1\)；这证明坐标映射，不证明任意本地模型沿用该 sampler。

## 6. Deterministic oracle probe

本次用固定向量

\[
A=[0.25,-0.50,0.75,1.00],
\qquad
\epsilon=[-1.00,0.50,0.25,-0.75]
\]

运行两个常速度 10-step Euler oracle：

```python
# Paper coordinate: tau goes from 0 to 1 and velocity is A - eps.
x_paper = eps.copy()
for _ in range(10):
    x_paper += 0.1 * (A - eps)

# OpenPI coordinate: t goes from 1 to 0 and velocity is eps - A.
x_code = eps.copy()
for _ in range(10):
    x_code += -0.1 * (eps - A)
```

| 检查 | 结果 |
| --- | --- |
| paper endpoint | `[0.25, -0.5, 0.7500000000000001, 1.0000000000000002]` |
| code endpoint | `[0.25, -0.5, 0.7500000000000001, 1.0000000000000002]` |
| 两者最大绝对 endpoint error | `2.220446049250313e-16` |
| 每步 displacement 是否相同 | `True` |
| 五个固定 Beta coordinate 的 \(t+\tau\) | 均为 `1.000000` |

这里的误差仅来自 float64 round-off。probe 验证的是代数与积分方向，不是 learned velocity accuracy、真实 solver latency 或 closed-loop success。

## 7. 对 ACT-023..030 的回写结论

| 题目 | 本次结论 | 保留边界 |
| --- | --- | --- |
| `VLA-ACT-023` | FM/CFM gradient equivalence 正确；补 theorem positivity assumption 与 constant boundary | 不等于逐样本 loss 相同 |
| `VLA-ACT-024` | paper `sigma_min` endpoint 与 exact-linear 特例区分正确 | 后续 package 不是 2022 historical implementation |
| `VLA-ACT-025` | Euler/NFE/H/K 分离正确 | oracle 不能代替 runtime trace |
| `VLA-ACT-026` | diffusion target/scheduler 与 flow velocity/ODE 分离正确 | 不做无 matched protocol 的速度排名 |
| `VLA-ACT-027` | π0/OpenPI time、velocity、dt 与 Beta 换元正确 | local OpenPiVLA class/sampler 未证实 |
| `VLA-ACT-028` | frozen Pi0 all-D mean 的风险描述保持 WARN | 本次未补 positive local valid-dim mask |
| `VLA-ACT-029` | generic CFG 仍仅是 supporting example | frozen OpenPI action path 未实现 CFG |
| `VLA-ACT-030` | oracle-first 四层调试顺序可保留 | 未运行本地 controller/rollout tests |

## 8. 不能推出的项目事实

- 不推出 OpenPiVLA 使用 frozen `Pi0` class、同一 timestep sampler、10-step Euler 或相同 \(H,D\)。
- 不推出本地 checkpoint、normalizer、axis/unit、valid mask、execution prefix \(K\)、controller 或 97.4% protocol 已闭合。
- 不把 upstream time/sign convention、同一 agent 的推导或本次 oracle 归为候选人的个人设计贡献。
- 不改变 44 张 VOL 03 卡或全局 280 张卡的 `unseen` 状态，也不创建 `coaching_state.md`。

## 9. 下一步

Source Audit E 的 theorem/endpoint/time-sign/Beta 高风险事实已完成独立复核，公共事实层为 `PASS WITH WARNING`；VOL 03 项目层仍因 local runtime、mask、controller、ownership 和 oral drill 缺口保持 `WARN/PENDING`。下一 bounded slice 优先 Source Audit B 的 π0/π0.5/FAST/OpenPI 其余高风险项，或进行一题真实口述。

## 参考入口

- [Flow Matching / π0 Source Audit E](vol_03_flow_matching_pi0_claim_to_code.html)
- [π0 / π0.5 / FAST / OpenPI Source Audit B](vol_03_pi0_fast_openpi_claim_to_code.html)
- [VOL 03 Completion Reconciliation](vol_03_completion_fact_reconciliation.html)
- [VOL 03 Knowledge](../knowledge/vol_03_vla_action.html)
- [VOL 03 Questions](../questions/vol_03_vla_action.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)
