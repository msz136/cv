# VOL 04 Audit C：Cosmos Policy / WAM 独立事实复核

> 状态：`independent_fact_reviewed / Audit C / public_facts_reconciled / PASS WITH WARNING`  
> 复核日期：2026-07-20  
> 证据截止：2026-07-20  
> 范围：重新获取 arXiv 论文、固定 GitHub commit、固定 Hugging Face revision 与本地 WAM diagnostic artifacts；复核 slot/layout、routing、condition/target/metric mask、EDM loss、sampler、direct/planning、LIBERO/RoboCasa protocol、license 和个人项目边界。  
> Bounded slice：本页只完成 Audit C 独立复核及必要状态同步；不新增知识节点或题卡，不启动 PER-019，不修改 269 张题卡的 `unseen` 状态，不创建 `coaching_state.md`。

## 1. 结论先行

原 [Cosmos Policy / WAM Claim-to-Code Audit](vol_04_cosmos_policy_wam_claim_to_code.html) 的主要公开事实成立：统一 latent-video sequence、policy/world/value 三角色、约 50/25/25 base routing、action/value latent injection、condition 与 target mask 分层、noise-weighted latent EDM loss、direct parallel generation、dual-checkpoint best-of-N planning、LIBERO 16×7 与 RoboCasa 32×7→执行16步→7D扩展12D、官方 98.5%/67.1% protocol 均可在重新获取的 paper/code/model card 中定位。

本轮 verdict 为 **PASS WITH WARNING**，而不是无条件 PASS，原因有四类：

1. `mask_value_prediction_loss_for_policy_prediction` 会构造 `final_mask_B_T`，但最终把 mask 乘到 `kendall_loss` 的条件没有包含该 flag；若它单独开启，配置名不等于 mask 真正生效。
2. 两个约 3.91 GB policy checkpoint、T5 pickle 与 base checkpoint 未下载或加载；本轮只冻结 policy revision、远端对象 ETag/大小、两份 config 与 statistics 的本地 SHA。
3. 本地 CoffeePressButton base/trained 两侧均为 `success=false` 的单 episode diagnostic；checkpoint 仍只是远端路径，不能证明 binary identity、模型 uplift、完整 0-success benchmark 或历史成功率。
4. 候选人的逐文件设计、编写、运行、验收角色仍未确认；上游 latent layout、routing、planning 与官方指标不得写成个人原创或个人结果。

另有两项边界被本轮补强：base `Cosmos-Predict2-2B-Video2World` 固定 revision 的模型卡明确是 NVIDIA Open Model License，而两份 policy model card 是 NSCLv1；官方 LIBERO/RoboCasa shape 下 latent volume \(12544\) 恰好分别被 \(16\times7=112\) 和 \(32\times7=224\) 整除，因此这两种 shape 没有不完整 action tail，通用实现仍需保留整除/尾部测试。

## 2. 独立来源冻结

| 层 | 本轮重新获取 | Identity | 结果与边界 |
| --- | --- | --- | --- |
| primary paper | `cosmos_policy.pdf` | arXiv `2601.16163v1`；21,715,508 bytes；SHA-256 `05696475C9B5481AFBF88673A65F80A46CF3FB87A5755C1410E83D0F468CC6E0`；22页、0空白页 | best-of-N、rollout refinement、dual deployment、98.5%/67.1%、0.61s/0.16s、6000/3600 trials 可定位；不支持本地 WAM 结果 |
| official repository | GitHub recursive tree + 13 files | `NVlabs/cosmos-policy@18a2accadf4e7a3531e56754102af5a24d2316da`；tree 664 entries、`truncated=false` | 13/13 下载文件的 computed Git blob 与 tree blob 相同；repo 根 license 为 Apache-2.0 |
| LIBERO policy model | API、README、config、statistics、8个 remote HEAD | revision `cb689ec0e3347c13667d70a78a3447388f5c3bb8` | revision exact match；6 siblings；model card 为 NSCLv1；checkpoint 未下载 |
| RoboCasa policy model | API、README、config、statistics、8个 remote HEAD | revision `4b2a04c80d97202f86127ebec80461e8016ec1dc` | revision exact match；6 siblings；model card 为 NSCLv1；checkpoint 未下载 |
| base model | API + README | revision `f50c09f5d8ab133a90cac3f4886a6471e9ba3f18` | revision exact match；`gated=auto`；NVIDIA Open Model License；本轮未下载权重 |
| local WAM | manifests、traces、videos、log、offline metric | `C:\Users\mousongzhe\Project\wm\outputs` | 9/9 指定文件 SHA 重新命中；仅支持 local-direct diagnostic 与 path-reference bridge |

### 2.1 Fixed-commit 代表文件

| 文件 | bytes | SHA-256 | Git blob |
| --- | ---: | --- | --- |
| `LICENSE` | 11,356 | `7382B1CF711E7A7C7AF9816E0E07B49B91E7149B7C6D347225F98800FCB1F1C2` | `4c9ad980682246bd6ab0d2bae82232be6dbdcbd4` |
| `README.md` | 5,933 | `D2ABD5F64EB132B6EDDAAF3E4CCD8C6EE6C905AA6F1810B004CAE32C88228CA5` | `f7e8dfb762ac595c4612343f88352351936d5a81` |
| `LIBERO.md` | 6,591 | `827B6FC57913E0D54702904AAB193F7410D6534BCB90DC39DB23E0294DF0FE77` | `6640360c6b4d0fe5cedf8418212ba0946e0f7616` |
| `ROBOCASA.md` | 6,977 | `97C518597D3D8BEC56C66161BC01FA1DE04EA2CB7C8D55B5F63057C062E24A27` | `3d816e64b8a5dc0f44dfb47655430c6b5dd093bd` |
| `models/policy_text2world_model.py` | 45,535 | `D2D6AF812E2241FA0D3D8C68620447BD0F23D236412ADA9BAD5C849DF5B848F5` | `efbafee498b91e3865b135599179949e159f8c75` |
| `models/policy_video2world_model.py` | 48,775 | `4F5314FDEA8F3F05D210F99923CA07E3C05FE9E0756B71F77B201F4B52E460EB` | `625bd0aeb1c4fb0ceee20a3b7404f1342ea1ff4d` |
| `modules/cosmos_sampler.py` | 5,621 | `D428B578159D7D2EFDC962A16FA168A627E831BD6D96EBEC4D8C8C4987156D82` | `ef9e42cc321942a7bfbff008dbe44cb700f15617` |
| `experiments/robot/cosmos_utils.py` | 109,448 | `A95C74F33F519F4C0CE048C3BA2694989D3A7C431BF0F324A274413CDE4C0B47` | `00c2845bc9f45e4ef4b333e5e88897b59df142db` |
| `datasets/libero_dataset.py` | 44,590 | `CBEBD356916DE3F7FC6BC084A6F719B6A8A58A9EF496F7F104AE5980F5F177E8` | `200aecfefe022d2768b85b8a35b4fb9c7706a8c8` |
| `datasets/robocasa_dataset.py` | 58,913 | `966D8496A98FCBADCE31C6EEC397BAE5439F461D85789B828EEF866695ABE893` | `63d21e4f3fc7405ac2a7bc20ab46188373c6f9e8` |
| `experiments/robot/libero/run_libero_eval.py` | 46,874 | `4A103710D9057E484B415DA46D5B40C054ABEB736E751AC80AD5A879C5B4AC10` | `8ced47fd42f3c1be0707dca874e18c2707a4a3a8` |
| `experiments/robot/robocasa/run_robocasa_eval.py` | 58,807 | `32AA3B78FF33C9D159A91BBA880953F467740F611D756A2B48223DE80D8E59D7` | `982df9b724e97648a7b7d46bc8678aab2833ec3f` |
| `config/experiment/cosmos_policy_experiment_configs.py` | 20,835 | `16B8C0D1E2112EBF09CC5393F3F38F07CBC82B9EE2844AD79F35FD6532A566FB` | `ba4f98edcb9ed9f9ee0c9985058c71de3c56528a` |

这张表证明下载内容与 fixed Git tree 相同；它不证明依赖、dataset、checkpoint 或本地 fork 与该 commit 等价。

## 3. Slot / Layout / Injection 复核

config 与 eval source 分别明确记录：LIBERO `state_t=9`，顺序为 blank/current proprio/wrist/primary/action/future proprio/future wrist/future primary/value；RoboCasa `state_t=11`，额外包含左右两路 third-person view。两份固定 model config 又分别记录 action `16×7` 与 `32×7`，proprio 均为 9D。[2][3][4]

令 action chunk 为 \(A\in[-1,1]^{K\times D_a}\)，单个 latent frame 的元素数为 \(M=C'H'W'=16\times28\times28=12544\)，action 元素数为 \(L=KD_a\)。注入实现为：

\[
z_a=operatorname{reshape}\left(
\operatorname{repeat}(\operatorname{vec}(A),\lceil M/L\rceil)_{1:M}
\right).
\]

变量解释：\(K\) 是 chunk horizon，\(D_a\) 是 action 维数；实现映射到 `replace_latent_with_action_chunk` 的 flatten、ceiling repeat、slice 与 overwrite。它没有 action-specific learned encoder，不能描述成独立 action head。

提取只使用完整 copies，并跨 copies 求均值：

\[
\hat A=\frac{1}{q}\sum_{j=1}^{q}
\operatorname{reshape}(z_a^{(j)},K,D_a),qquad
q=\left\lfloor\frac{M}{KD_a}\right\rfloor.
\]

变量解释：LIBERO 的 \(q=112\)、RoboCasa 的 \(q=56\)，两者 tail 都为 0；独立 round-trip probe 的最大浮点误差分别约 \(2.44\times10^{-15}\) 与 \(1.22\times10^{-15}\)。若更换 \(K,D_a,C',H',W'\)，仍需检查 `num_action_elements <= latent_elements`、整除性与尾部语义。

value frame 的提取是对整帧求均值，调用侧再按 (operatorname{clip}((v+1)/2,0,1)) 映射到 ([0,1])。probe 对输入 ([-0.8,0.2,1.0]) 得到 ([0.1,0.6,1.0])。这验证编码/解码算术，不验证 value calibration 或 success probability。

## 4. Routing、Condition Mask 与 Loss

### 4.1 角色概率

base config 对 demo 与 rollout 的 sampling probability 都设为 0.5；rollout 内 LIBERO 固定 `p_world_model=0.5`，RoboCasa 默认 `p_world_model=0.5`。因此 recipe-level 期望比例为：

\[
P(\text{policy})=0.5,qquad
P(\text{world})=0.5\times0.5=0.25,qquad
P(\text{value})=0.5\times0.5=0.25.
\]

变量解释：这是 epoch structure 与随机 role selection 的期望，不是某个实际 batch 的精确计数；runtime 必须记录 realized ratio。rollout refinement 的 ALOHA planning recipe 则是 10% policy、其余90%在world/value间均分，不能与 base 50/25/25混写。[1][2]

### 4.2 Condition 与 target 的分层

`get_data_and_condition` 对 world sample 把 action slot 设为 clean condition；对 value sample 先把全部 frames 设为 clean，再把 value slot 置为需生成。V/Q variant 分别 mask current/action 或 future state。这里 `condition_video_input_mask=1` 表示 clean condition，不能当成 attention mask 或 loss mask。[2]

主训练路径先注入 action、proprio、future proprio 与 value，采样 \(x_t\)，denoiser 输出 \(\hat x_0\)，再形成 noise-level weighted latent MSE：

\[
\mathcal L_{\mathrm{EDM}}=
\frac{1}{BCTHW}
\sum_{b,c,t,h,w}
m_{b,t}\,w(\sigma_{b,t})
\left(x_{0,bcthw}-\hat x_{0,bcthw}\right)^2.
\]

变量解释：\(m_{b,t}\) 是按 latent frame 广播的 target mask/multiplier，\(w(\sigma)\) 是 noise-level weight。实现先构造 per-element `edm_loss_B_C_T_H_W`，再按条件乘 `final_mask_B_T`；action/future/value L1/MSE 是 component diagnostics，不等于主反向目标。

### 4.3 已确认的 flag 风险

`mask_value_prediction_loss_for_policy_prediction=True` 时，代码在 490–539 行构造并更新 `final_mask_B_T`；但 555–560 行的 apply-mask 条件只包含：

- `mask_loss_for_action_future_state_prediction`；
- `mask_current_state_action_for_value_prediction`；
- `mask_future_state_for_qvalue_prediction`；
- `action_loss_multiplier != 1`。

它没有列入 `mask_value_prediction_loss_for_policy_prediction`。所以该 flag 若单独为 true，构造的 mask 不会因它自身进入最终乘法。当前默认 config 两个 target-mask flags 都为 false，本问题不能据此否定官方 checkpoint；个人配置若开启该 flag，必须做 masked/unmasked loss 与 gradient probe。

## 5. Sampler、Direct Policy 与 Planning

`CosmosPolicySampler.forward` 在请求 steps 大于1时先减1个 solver NFE，随后补一次 clean denoise；请求1步时直接在首 sigma 调 denoiser。因此请求5步的合同是 `4 solver NFE + 1 clean denoise`，不是“五次相同 solver loop”。10/10 deterministic probes 中对此计算已单独通过。[2]

direct eval 的 `get_action` 可在一次 generation 中并行产生 action/future/value，但 action selection 不依赖 future/value。planning path 则是：

```python
def audited_best_of_n(observation, task, n):
    # Policy checkpoint proposes N action chunks with distinct seeds.
    proposals = [policy_get_action(observation, task, seed=i) for i in range(n)]

    # A separately loaded planning checkpoint conditions on each proposal.
    futures = [planning_get_future(observation, action) for action in proposals]

    # Value predictions rank proposals; only the selected execution prefix reaches the controller.
    scores = [aggregate_value(planning_get_value(future)) for future in futures]
    return proposals[argmax(scores)][:num_open_loop_steps]
```

代码与论文都支持 action→future→value→argmax 的顺序，且 `get_planning_model` 与主 model 分开加载。论文 ALOHA 实验使用 (N=8)、每 action 3 个 future samples、每 future 5 个 value samples与8张H100；repo 的默认 LIBERO/RoboCasa runtime 则是 `N=1`、ensemble关闭、aggregation=`average`。论文设定不能冒充所有默认配置。[1][2]

best-of-N 可写为：

\[
a^*=\arg\max_{a^{(i)}\sim\pi(\cdot\mid s)}
\widehat V\!\left(\widehat T(s,a^{(i)})\right).
\]

变量解释：(pi) 是 proposal policy，(widehat T,widehat V) 属于 refined planning model；它是排序 policy proposals，不是 CEM/MPPI 的迭代分布更新。候选越多越可能放大 world/value 过估计，因此 N、rank correlation、selected-vs-random、latency 与 failure trace 必须一起报告。

## 6. LIBERO / RoboCasa 与官方数字

| 合同项 | LIBERO | RoboCasa | 独立结论 |
| --- | --- | --- | --- |
| model output | 16×7 action；9D proprio；两路 camera | 32×7 action；9D proprio；三路 camera | config、card 与 code 一致 |
| execution | default open-loop 16；deque maxlen=16 | 先 slice `actions[:16]` 再入 queue | “chunk horizon”与“执行 prefix”分开 |
| reset/warmup | official init state；10个 dummy actions | 每 episode 重建 env；按 episode 每10条切 scene；10个 zero actions | 不能只报 task 名 |
| controller | `env.step(action.tolist())` | PandaMobile + OSC_POSE；7D 后拼 `[0,0,0,0,-1]` 成12D | 7→12 probe 通过 |
| success | eval wrapper 的 `done` | `env._check_success()` | 外部 benchmark/version 仍需独立冻结 |
| official denominator | 4 suites×10 tasks×50 episodes×3 seeds = 6000 | 24 tasks×50 trials×3 seeds = 3600 | 两项 denominator probe 通过 |
| official score | 98.5% | 67.1% | 都是上游 checkpoint/protocol 声明，不是用户 WAM 结果 |

论文还报告同一H100上5-step并行 action/future/value 约0.61s/chunk、1-step约0.16s/chunk；这些 wall-clock 只绑定指定硬件与实现，不能写成本机或本地部署 latency。[1]

## 7. Model Asset 与许可证边界

| Model | revision | 本轮本地下载 | remote-only object | License |
| --- | --- | --- | --- | --- |
| LIBERO policy | `cb689ec...` | `config.json` SHA `6C246E65...2C31F43`；statistics SHA `5B119A98...C580D3`；README SHA `3BD88247...405506` | checkpoint 3,913,017,345 bytes，ETag `c86c9427...fa8d5`；T5 41,957,938 bytes，ETag `f4e95822...ef05b` | NSCLv1，来自 model card正文 |
| RoboCasa policy | `4b2a04c...` | `config.json` SHA `B1690DC2...73521`；statistics SHA `5B9882C8...6DB87`；README SHA `1DC2D061...F7AF9` | checkpoint 3,913,017,345 bytes，ETag `5abf2715...d2992`；T5 463,599,495 bytes，ETag `2feda9de...9fceb` | NSCLv1，来自 model card正文 |
| base Predict2 | `f50c09f...` | API + README；README SHA `738F95DB...DFFBE` | 26 siblings，`gated=auto`，权重未下载 | NVIDIA Open Model License |

ETag 是固定 revision 下的远端对象 identity，不等于本轮已本地读取并复算的 binary SHA。严格运行 manifest 仍需 checkpoint/config/statistics/T5 的本地或不可变远端 identity，并避免 `snapshot_download` 不传 revision 时解析未来 HEAD。

论文 CC BY 4.0、GitHub code Apache-2.0、base model NVIDIA Open Model License、policy checkpoint NSCLv1 必须分列；任何一层的 license 都不能自动覆盖其他 artifact。

## 8. 本地 WAM 再哈希与 Truth Boundary

| Local artifact | 重新命中 | 直接支持 | 仍不能支持 |
| --- | --- | --- | --- |
| base manifest | `63A51867...BD33A86`，3,901 bytes | CoffeePressButton、episode0、seed195/env_seed0、300 steps、open-loop16、denoise5、`success=false` | base checkpoint binary 已验证 |
| trained manifest | `809AE4F8...EF55CC`，3,918 bytes | 同 protocol 字段、`success=false`、远端 iter10000 path | trained checkpoint binary 已验证 |
| base/trained traces | `C6A3623B...88525D` / `9C6A4F00...82CF2D` | 各300×7 policy、300×12 env、finite、success true count均0、reward sum均0 | 目标动作误差、模型好坏、完整成功率 |
| base/trained videos | `D469A8B2...2F388` / `59176353...2877E` | 两条失败 episode 文件存在 | matched suite denominator、root cause |
| rollout log | `19448961...27143` | action chunk/dim/runtime线索 | checkpoint与结果 ownership |
| offline manifest/metric | `8C4872F7...EC71` / `C9AB7F04...EC9D` | offline metric 与 trained rollout checkpoint path 逐字相同；12 future frames | binary identity、matched episode/seed/horizon、proxy-success 因果 |

独立解析两条 action trace 得到：rows 均为300，(t) 序列完全相同，policy shape均为300×7，env shape均为300×12，无 NaN/Inf，逐步 `success_after_step=True` 计数均为0，reward sum均为0；两条 policy trace 之间 MAE 为 `0.3100783610894134`，RMSE 为 `0.3906446458988869`。这是 trace-to-trace 几何差异，不是 prediction-to-target error。

两份 manifest 的 checkpoint 字段仍为 `/data/msz/...` 路径。offline `iter_000010000/0000_metrics.json` 与 trained rollout manifest 的路径字符串 exact match，只能建立 checkpoint-reference bridge；offline 输入是成功 regen-demo、seed7、4 denoise steps与12 future frames，rollout 是另一 environment episode、policy seed195/env seed0、5 action steps与300 env steps，不能做相关或因果推断。

### 8.1 当前安全口述

> “我把 Cosmos/WAM 拆成上游统一 latent contract、训练 routing/mask、RoboCasa controller protocol 与本地诊断四层。上游 slot、50/25/25 routing、direct/planning 和公开分数不是我的原创或本地结果。本地能复核到一组 CoffeePressButton base/trained manifest、300×7→300×12 action traces 与失败视频，但两侧都失败，checkpoint 仍是远端路径，只有 path fingerprint。所以我把它用于接口与失败诊断，不把 trace 差异写成 uplift，也不恢复历史 MSE/成功率。”

候选人的实现/运行/验收 ownership 仍应按 [WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html) 逐项回答；在真实确认前，只能用“本地快照包含”“材料记录”“我按上游合同梳理/对齐”等受限动词。

## 9. 十个独立 Deterministic Probes

| Probe | 结果 |
| --- | --- |
| LIBERO 16×7 action inject→extract | PASS；112完整copies、tail0 |
| RoboCasa 32×7 action inject→extract | PASS；56完整copies、tail0 |
| value frame mean + \([-1,1]\to[0,1]\) | PASS；`[-0.8,0.2,1.0]→[0.1,0.6,1.0]` |
| base recipe role algebra | PASS；`0.5/0.25/0.25` |
| RoboCasa statistics normalize→denormalize | PASS；max error约 `1.11e-16` |
| RoboCasa 7D→12D controller append | PASS；尾部 `[0,0,0,0,-1]` |
| LIBERO official denominator | PASS；6000 |
| RoboCasa official denominator | PASS；3600 |
| requested 5-step sampler contract | PASS；4 solver NFE + 1 clean denoise |
| best-of-N selector | PASS；`argmax([0.1,0.8,0.3])=1` |

10/10 probes 只验证确定性算术与接口合同，不代替 GPU inference、checkpoint load、environment rollout、value calibration 或候选人 ownership。

## 10. Source → Knowledge → Card Reconciliation

| Claim cluster | Source Audit C | WM-025 Knowledge | VLA-WM-025 Card | Verdict / correction |
| --- | --- | --- | --- | --- |
| unified latent sequence | 明确不是三个独立head | 先纠正“三个head” | 30秒回答一致 | PASS |
| layout/injection | 9/11 slots、16×7/32×7、repeat/mean | action/future/value slot分开 | mechanism answer一致 | PASS；补充官方shape tail=0 |
| routing | base约50/25/25 | sample routing与mask分层 | 诊断要求打印role | PASS；实际batch需记录realized ratio |
| condition/target/metric mask | 代码路径与flag边界 | 四类开关明确 | 易错点明确 | PASS WITH WARNING；保留value-aux apply-mask flag风险 |
| EDM/component metrics | noise-weighted latent MSE | 主loss不等于component L1 | 30秒与诊断一致 | PASS |
| direct/planning | parallel direct与dual-checkpoint planning分开 | 卡片聚焦WM-025，不扩写planning | 不混称value=planning | PASS |
| benchmark/license | protocol与四层license分开 | 项目边界不引用官方结果 | 不把公开结构写成个人设计 | PASS WITH WARNING；base license现已补核 |
| local project | raw checkpoint/result/ownership不足 | CoffeePressButton仅partial | 保持受限安全口述 | PASS WITH WARNING；两侧失败、路径不是binary hash |

不需要重写 VLA-WM-025 的30秒答案；面试时应追加两个版本限定：“官方 LIBERO/RoboCasa shape 恰好无 action tail，但换 shape 要重测”；“value-aux mask flag 单独开启时必须查 final apply branch 与 gradient”。题卡继续 `unseen`。

## 11. 审查状态与下一步

Audit C 的 paper/code/model-card public facts 已完成独立再获取、Git blob identity、10 probes、local rehash 与 source→knowledge→card reconciliation，可从 `independent_review_pending` 提升为 `independent_fact_reviewed / PASS WITH WARNING`。这不改变 VOL 04 的整卷 `WARN`，也不表示本地 WAM run 或个人 ownership 已通过。

仍开放：

- 下载/固定 policy/base checkpoint 与 T5 object 仅在许可证、空间和真实复现需要时进行，并建立 immutable manifest；
- 冻结 modified LIBERO/RoboCasa dataset revisions 与数据条款；
- 对 external benchmark commit、reset/success semantics 做独立版本核对；
- 对 value-aux mask flag 跑真实 tensor loss/gradient test；
- 补 local checkpoint binary/hash、processor/normalizer/config、完整 episode denominator与同协议 paired rerun；
- 由候选人逐项确认 WAM 的设计、编写、运行、审查和工具/协作者边界；
- 真实口述前不改变 mastery，不创建 coaching state。

下一 bounded slice 优先进行一题真实口述；若继续文档复核，则只选择 VOL 04 Audit D Sim2Real，不启动 PER-019。

## References

1. Kim et al., [Cosmos Policy: Fine-Tuning Video Models for Visuomotor Control and Planning](https://arxiv.org/abs/2601.16163v1), arXiv v1, 2026。
2. NVlabs, [cosmos-policy@18a2acc](https://github.com/NVlabs/cosmos-policy/tree/18a2accadf4e7a3531e56754102af5a24d2316da)，重点复核 model、dataset、sampler、config 与 eval paths。
3. NVIDIA, [Cosmos-Policy-LIBERO-Predict2-2B@cb689ec](https://huggingface.co/nvidia/Cosmos-Policy-LIBERO-Predict2-2B/tree/cb689ec0e3347c13667d70a78a3447388f5c3bb8)。
4. NVIDIA, [Cosmos-Policy-RoboCasa-Predict2-2B@4b2a04c](https://huggingface.co/nvidia/Cosmos-Policy-RoboCasa-Predict2-2B/tree/4b2a04c80d97202f86127ebec80461e8016ec1dc)。
5. NVIDIA, [Cosmos-Predict2-2B-Video2World@f50c09f](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Video2World/tree/f50c09f5d8ab133a90cac3f4886a6471e9ba3f18)。
6. [Audit C Claim-to-Code](vol_04_cosmos_policy_wam_claim_to_code.html) 与 [WM-025 Source Freeze](vol_04_wm025_cosmos_wam_slot_mask_loss_source_freeze.html)。
7. [WM-025 Knowledge](../knowledge/vol_04_world_model_sim2real_wm025_cosmos_wam_slot_mask_loss.html) 与 [VLA-WM-025 Atomic Card](../questions/vol_04_world_model_sim2real_wm025.html)。
8. [WAM Claim–Evidence Inventory](../evidence/projects/wam_claim_evidence_inventory.html)、[WAM Ownership Ledger](../evidence/projects/wam_ownership_ledger.html)、[Artifact Manifest](../evidence/projects/wm019_wam_artifact_manifest.html)、[Action-Trace Diagnostic](../evidence/projects/wm019_wam_action_trace_paired_diagnostic.html) 与 [Matched-Checkpoint Bridge](../evidence/projects/wm019_wam_matched_checkpoint_protocol_bridge.html)。
