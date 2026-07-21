# VOL 03 Source Audit B：π0 / π0.5 / FAST / OpenPI 独立事实复核

> 状态：`independent_fact_reviewed / audit_b / pi05_fast_norm_rollout_checked / PASS WITH WARNING`
> 审查日期：2026-07-19
> 范围：π0.5 hybrid 训练边界、FAST action tokenizer、OpenPI model/config/transform、normalization 与 LIBERO rollout example。
> 结论先行：π0.5 v1 明确把 pre-training 的 FAST 离散 token 目标与 post-training 的连续 flow action expert 分成两阶段；frozen OpenPI 中 `Pi0(pi05=True)` 的主 flow loss 与 `Pi0FAST` 的 autoregressive CE 是两条不同模型路径，不能互称为完整 π0.5 hybrid 复现。FAST paper 的 quantile normalization、DCT、scale-and-round、frequency-first flatten、BPE 顺序得到直接复核；FAST Hub processor 与 OpenPI tokenizer 不负责 quantile normalization。OpenPI 的 32 维 model space、7 维 LIBERO output slice、norm-stat checkpoint contract 与 replan=5 只是官方配置/example，不是本地 OpenPiVLA 事实。

## 1. 直接复核来源与冻结对象

| ID | 来源 | 本次直接读取内容 | SHA / Verdict |
| --- | --- | --- | --- |
| P01 | [π0.5 v1 PDF](https://arxiv.org/pdf/2504.16054v1) | Fig. 3、Sec. IV、Eq. (1)、pre/post training | `6A1029FD8AB6944B74CF22F5E5D30E60BC15699D964B2900AF799B807A34B64C` / `primary-verified` |
| P02 | [FAST v1 PDF](https://arxiv.org/pdf/2501.09747v1) | Sec. V-B、Algorithm 1、scale/vocab、quantile/DCT/BPE | `3739B31F5FECDDE371509FF5BB13619979734E894A255A9B264253F4CC53934A` / `primary-verified` |
| C01 | [OpenPI `pi0_fast.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_fast.py) | `Pi0FASTConfig`、token CE、loss mask、AR decode | `627332A555046F2744EF144C45F8BD3361A9820CF68854A4528D0FDBBA7E9AA3` / `official-code` |
| C02 | [OpenPI `pi0_config.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/pi0_config.py) | Pi0/Pi05 defaults、D/H、discrete state flag | `D321858C30B398126035EA2B6DA09E1C422EEEEBB5EBF8DF631DAF9DC77647FA` / `official-code` |
| C03 | [OpenPI `tokenizer.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/models/tokenizer.py) | FAST prefix/postfix、128 special-token skip、mask、truncation、decode fallback | `965BE8B3C393A6811875BBC32DA9E01CC2F87802DE801CF7293E049748C` / `official-code` |
| C04 | [OpenPI `transforms.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/transforms.py) | quantile/z-score normalize、unnormalize、pad、FAST extract | `A1B94E9E72849A18834778F229C6BB389A495EB7FBE0AA800EDEA728B9424FF4` / `official-code` |
| C05 | [OpenPI `libero_policy.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/policies/libero_policy.py) | valid/padded camera mask、7D output slice | `D8679D99FACC3FEF48DA07406081B20709ED872FCEFDF7DE67EDE99422D623FA` / `official-code` |
| C06 | [OpenPI LIBERO example](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/examples/libero/main.py) | 180° image flip、resize、replan=5、50 trials、success logging | `D53748C95804ADA559E3CA867305B8F755D8651C4C7F4E2723EF80AEA55A3943` / `official-code` |
| C07 | [OpenPI `training/config.py`](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/src/openpi/training/config.py) | `pi0_fast_libero` 的 action_dim=7、action_horizon=10 与 checkpoint config override | `C34231F888AB5DC981D808765B3D98775AB845B04313BF53FCECD567C520B0D` / `official-code` |
| H01 | [FAST Hub processor](https://huggingface.co/physical-intelligence/fast/blob/ec4d7aa71691cac0b8bed6942be45684db2110f4/processing_action_tokenizer.py) | scale=10、vocab=2048、DCT/BPE encode/decode | `6F021CA1F4C1B194AB6FA399D80BAF3D642EADB17EFB8F73301E4AC401522C20` / `official-artifact` |
| H02 | [FAST Hub config](https://huggingface.co/physical-intelligence/fast/blob/ec4d7aa71691cac0b8bed6942be45684db2110f4/processor_config.json) | `scale=10`、`vocab_size=2048`、`min_token=-354` | `F40CFBB1020858FE1D48C0F946B0C1315A90D6E84AA82710036F24F4C167706A` / `official-artifact` |
| D01 | [OpenPI normalization notes](https://github.com/Physical-Intelligence/openpi/blob/15a9616a00943ada6c20a0f158e3adb39df2ccac/docs/norm_stats.md) | stats 与 checkpoint、action axes、单位、频率 | `62E4A39EA7FCDAE53B4466942DB348C3E38FC016B7F7A5273CAFED649EBE614B` / `official-doc` |
| O01 | 本次 deterministic probes | DCT roundtrip、quantile out-of-range、pad/slice、replan queue | `local-evidence / PASS` |

所有 GitHub 代码均固定在 OpenPI commit `15a9616a00943ada6c20a0f158e3adb39df2ccac`；FAST Hub 固定在 `ec4d7aa71691cac0b8bed6942be45684db2110f4`。这些来源支持公开机制和官方 example，不支持用户本地 checkpoint、fork、指标或 ownership。

## 2. π0.5：论文 hybrid 目标与 OpenPI 两条路径

### 2.1 论文的两阶段合同

π0.5 v1 的 Fig. 3 与 Sec. IV 写明：pre-training 把 robot action 表示成 FAST 离散 token，并以 autoregressive next-token prediction 训练；post-training 添加 action expert，用 flow matching 生成连续 action chunk。其联合目标可概括为：

\[
\mathcal L_{\pi0.5}
=
\mathcal L_{\mathrm{CE}}(x_{1:M},y_{1:M})
+
\alpha\,
\mathbb E_{\tau,\omega}
\left\|
\omega-a_{t:t+H}
-f_{\theta}^{a}(a_{t:t+H}^{\tau,\omega},o_t,\ell)
\right\|_2^2 .
\]

变量与实现：`\mathcal L_{\mathrm{CE}}` 覆盖文本/语义/FAST action token 的离散 next-token 目标；`f^a_\theta` 是较小 action expert 的 flow vector field；`\alpha` 是 trade-off。论文 post-training 报告 `\alpha=10.0`、先做 280k pre-training 再追加 80k post-training；这是论文 recipe，不是本地运行证据。[P01]

### 2.2 frozen OpenPI 的分叉

OpenPI `Pi0(pi05=True)` 的配置差异是 state 进入离散 prompt、flow timestep 用 adaRMSNorm；但该类的 `compute_loss` 仍是连续 flow loss 路径。独立读取的 `Pi0FAST` 则在 `compute_loss` 中构造 shifted next-token targets，只对 `token_loss_mask[:,1:]` 做 CE reduction：

\[
\ell_{\mathrm{CE}}
=
-\frac{
\sum_k m_k\log p_\theta(y_k\mid y_{<k})
}{
\max\left(\sum_k m_k,1\right)
}.
\]

变量与实现：`m_k` 来自 FAST postfix mask；prefix state/language 与 padding 不参加 CE。`Pi0FAST.sample_actions` 是 autoregressive token decode，遇到 EOS 可提前停止，之后由 FAST tokenizer 解码成连续动作；它不是 `Pi0(pi05=True)` 的 flow expert sampler。

因此安全结论是：

- 论文 hybrid objective：`primary-verified / paper-level`；
- frozen `Pi0(pi05=True)`：`flow path direct evidence`，不能称完整 hybrid；
- frozen `Pi0FAST`：`FAST token CE direct evidence`，不能自动补出 Pi0.5 paper 的联合 flow loss；
- 本地 OpenPiVLA 采用哪一类，必须由 model class、forward/compute_loss、tokenizer 与 checkpoint manifest 证明。

## 3. FAST：归一化、DCT、量化与 BPE

FAST paper Sec. V-B 的顺序是：

\[
a
\xrightarrow{\mathrm{quantile\ normalize}}
\tilde a
\xrightarrow{\mathrm{DCT\ along\ time}}
C
\xrightarrow{\mathrm{round}(\gamma C)}
\bar C
\xrightarrow{\mathrm{frequency\ first\ flatten}}
T
\xrightarrow{\mathrm{BPE}}
\bar T .
\]

变量与直觉：每个 action dimension 的训练集 1%/99% quantile 映射到 [-1,1]；DCT 把平滑时间序列变成低频优先的系数；`\gamma` 控制量化误差/压缩率；BPE 合并常见 coefficient 字符串。论文 single-dataset 实验使用 `\gamma=10`、BPE vocab 1024，并强调 BPE 是唯一 learned component，DCT 与 inverse DCT 是解析变换。[P02]

Hub revision 的 processor 默认则是：

| 对象 | 值 | 证据 |
| --- | --- | --- |
| `scale` | 10 | H01/H02 |
| `vocab_size` | 2048 | H01/H02 |
| `min_token` | -354 | H02 |
| `time_horizon/action_dim` | 可由构造器或 decode 参数提供 | H01 |

`processing_action_tokenizer.py` 的 `__call__` 从输入 action chunk 直接做 DCT、round、flatten、BPE；其中没有 q01/q99 normalization。OpenPI 的 `FASTTokenizer` 还负责把 FAST token 映射到 PaliGemma vocabulary，跳过最后 128 个 special-token slots，并构造 prefix/postfix、AR mask、loss mask。故“FAST processor 自带 normalization”是错误答案。

## 4. FAST token mask、截断与 malformed decode

OpenPI `FASTTokenizer.tokenize` 直接把：

- prefix：`Task: ... State: ...;`，`loss_mask=False`；
- postfix：`Action: <FAST tokens>|`，`loss_mask=True`；
- padding：`token_mask/ar_mask/loss_mask` 均为 false/zero；
- 超过 `max_len`：截断并记录 warning。

`extract_actions` 在生成文本缺少 `Action: ` 时返回全零 action；FAST processor decode 失败时也捕获异常并构造全零 DCT 矩阵。它们是官方 fallback 行为，不等于安全策略。真实部署应记录 malformed token、fallback 次数、零动作是否触发 controller safety stop，而不是把 fallback 当成功。

## 5. OpenPI action dimension、padding、normalization 与 rollout

### 5.1 model dimension 不是 physical dimension

frozen config 默认：

| Model config | `action_dim` | `action_horizon` | 语义 |
| --- | ---: | ---: | --- |
| `Pi0Config` | 32 | 50 | continuous flow model-side space |
| `Pi0FASTConfig` default | 32 | 32 | FAST AR model-side space |
| `pi0_fast_libero` config override | 7 | 10 | official LIBERO fine-tune example |

`PadStatesAndActions` 把 state/action 在最后一维补到 model dimension；`LiberoOutputs` 再只取前 7 维。`training/config.py` 的 `pi0_fast_libero` 则显式把 Pi0FAST 的 model `D=7,H=10` 覆盖为 LIBERO 任务规格。这个 config override、output slice 与 model default 仍是三件事，不能反推本地项目同样采用；output slice 也不能反推训练 loss 已经 mask padding。该 frozen Pi0 flow path 对 configured D 做 mean 的风险已在 Audit E 记录，本页不把 negative evidence 升级成 local bug。

### 5.2 normalization 是 checkpoint contract

OpenPI docs 明确：state/action normalization stats 由 training data 计算并和 checkpoint 一起保存；可以复用预训练 stats，也可以重新计算新数据 stats。`Normalize` 的 quantile 路径为：

\[
\tilde x
=
\frac{x-q_{01}}{q_{99}-q_{01}+\epsilon}\cdot 2-1,
\qquad
\mathrm{Unnormalize}(\tilde x)
=
\frac{\tilde x+1}{2}(q_{99}-q_{01}+\epsilon)+q_{01}.
\]

变量与实现：`q_{01},q_{99}` 来自 stats artifact；代码对输入先按现有维度切 stats，对输出按 tensor 宽度补 mean=0/std=1 或拼接未归一化尾部。代码没有在 quantile normalization 中自动 clip，因此 q01/q99 外动作可得到 [-1,1] 之外的 normalized value；是否 clip、在哪一层 clip，必须由具体项目 transform/controller 证明。

### 5.3 LIBERO example 的 replan 与视觉合同

官方 example 默认 `replan_steps=5`、`num_trials_per_task=50`、seed=7；每次 policy query 后只把 chunk 前 5 步放入 queue，执行完再重新读取 observation。image 先旋转 180°、resize/pad 到 224，再送入 client；`LiberoInputs` 把不存在的右腕图像补零，并为 Pi0 与 Pi0-FAST 使用不同 image-mask 语义。它们都是 example protocol，不是候选人项目的真实 eval protocol。

```python
def libero_example_step(obs, client, action_plan, replan_steps=5):
    # 1. Match training image orientation and resize contract.
    image = resize_with_pad(rotate_180(obs["agentview_image"]), 224, 224)

    # 2. Build state/action input keys expected by the frozen policy wrapper.
    element = build_libero_element(image, obs["robot0_eef_pos"], obs["robot0_eef_quat"])

    # 3. Re-query only when the previous execution prefix is consumed.
    if not action_plan:
        chunk = client.infer(element)["actions"]
        action_plan.extend(chunk[:replan_steps])

    # 4. Execute one denormalized, dataset-dimension action and log success.
    return action_plan.popleft()
```

代码映射：上述顺序来自 frozen `examples/libero/main.py`、`libero_policy.py` 与 transform factory；本地若另有 denormalize、axis reorder、clip 或 async queue，必须以本地源码覆盖该 example。

## 6. Deterministic probes

本次没有把官方依赖安装到工作区，只用独立 NumPy/SciPy probe 检查公式边界：

| Probe | 结果 | 含义 |
| --- | --- | --- |
| FAST DCT/round/idct，输入 [8,2]、scale=10 | shape 保持 [8,2]，max abs reconstruction error `0.0487787431` | round 是有损量化；DCT shape 不等于 token length |
| quantile normalize q01=[-1,2], q99=[1,6] | q01/q99 附近约 0，value=[2,8] 得到约 [2,2] | frozen formula 不自动 clip |
| quantile inverse | max abs round-trip error 0 | stats 与 inverse 公式相配时可逆（忽略数值 epsilon） |
| 7D→32D pad→slice | tail 25 维全 0，slice round-trip=True | shape mapping 成立，不证明 loss mask |
| queue consume 5 | 12 control steps 触发 3 次 query，首 chunk 执行 5 步 | K/replan 是 rollout contract，不是 H |

Probe 只验证公式、shape 与 queue 逻辑；不证明 learned model、checkpoint、LIBERO success 或个人项目实现。

## 7. 对下游题目的回写

| 题目范围 | 独立复核结论 | 必须保留的边界 |
| --- | --- | --- |
| `VLA-ARCH-002..004` | multi-view/state/token/action expert 的 public I/O 口径通过 | local view/time alignment 未证 |
| `VLA-ARCH-006` | Pi0/Pi05/FAST 三条 model path 分开 | local class/checkpoint 未证 |
| `VLA-ARCH-008` | FAST prefix/postfix、AR/loss mask 与 image mask 分开 | 不把 token mask 当 continuous action mask |
| `VLA-ARCH-010` | D/d、pad/slice 与 model capacity 分开 | positive local valid-dim mask 未证 |
| `VLA-ARCH-011` | FAST AR、flow NFE、prefix/cache、replan queue 分层 | 无 local timing |
| `VLA-ACT-001/002/005..008` | action representation、normalization、FAST processor 与 error boundary 通过 | local normalizer/tokenizer revision 未证 |
| `VLA-ACT-010/011` | H、K、replan 与 chunk queue 分开 | local H/K 未证 |
| `VLA-ACT-023..025/027/028/031..032` | 与 Audit E 的 flow、padding、decode/controller 口径一致 | local runtime/controller/ownership 未证 |

本次不改变 23 张相关卡或全局题卡的 `unseen` 状态，也不创建 `coaching_state.md`。

## 8. 不能推出的本地项目事实

- 不推出 OpenPiVLA 使用 `Pi0`、`Pi0FAST`、Pi05 hybrid 或自定义 Qwen/JSON 路线。
- 不推出本地 action `H=10`、`D=32`、7D slice、FAST revision、scale/vocab、normalizer、replan=5 或 97.4%。
- 不推出官方 example 的 50 trials、seed=7、图像旋转、LIBERO success predicate 已用于用户项目。
- 不把 π0.5 论文的 280k/80k、`\alpha=10` 或公开性能写成本人训练结果。
- 不把 upstream code、Git author 或本次 probe 写成候选人个人 ownership。

## 9. 下一步

Audit B 的 π0.5 hybrid、FAST、OpenPI shape/norm/rollout 高风险事实已完成独立复核，公共事实层为 `PASS WITH WARNING`；整体项目层仍因 local checkpoint、tokenizer revision、stats、axis/unit、H/K、controller、eval bundle 与 ownership 缺失保持 `WARN/PENDING`。下一 bounded slice 优先独立复核 Audit C 的 ACT paper/code gap，或进行一题真实口述。

## 参考入口

- [VOL 03 π0 / π0.5 / FAST / OpenPI Claim-to-Code](vol_03_pi0_fast_openpi_claim_to_code.html)
- [VOL 03 π0 / π0.5 / FAST / OpenPI 独立事实复核](vol_03_pi0_fast_openpi_independent_fact_review.html)
- [VOL 03 Flow Matching / π0 Time–Sign 独立复核](vol_03_flow_pi0_time_sign_independent_fact_review.html)
- [VOL 03 Completion Reconciliation](vol_03_completion_fact_reconciliation.html)
- [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)
- [OpenPiVLA Ownership Ledger](../evidence/projects/openpivla_ownership_ledger.html)
