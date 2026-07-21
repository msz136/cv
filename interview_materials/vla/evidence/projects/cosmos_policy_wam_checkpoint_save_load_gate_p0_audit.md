# Cosmos Policy / WAM Checkpoint Save-Load Gate：P0 证据审计

> 状态：`p0_audited / base-load-backed / train-save-gate-failed / checkpoint-binary-missing / ownership-pending / WARN`  
> 审计日期：2026-07-21  
> 证据截止：2026-06-25  
> 范围：只审计 `muxi_deepspeed_1epoch_20260623` 归档中的 base-model load、1-step/5-step smoke、9907-step save2k gate 与 no-cycle save1500 gate；不把 smoke 的成功、base-load 的完整 key 对齐或空的 output directory写成“训练完成”或“checkpoint 可加载”。

## 1. 结论先行

本轮把上一轮“保存接口失败”的叙述升级成了可复核的 **save/load gate ledger**：

1. 13 个 `base_load_summary.json` 都指向同一个 HF cache snapshot，报告 `715` keys、`missing_count=0`、`unexpected_count=0`。这证明 base model 初始化/加载契约在这些进程中通过了 key-level check；它不是训练后 checkpoint 的 load parity。
2. `batch_size=1` 的 8-GPU fixed-optional 1-step smoke、`batch_size=8` 的 1-step smoke 和 no-cycle 5-step smoke 都有 `exit=0`；它们只覆盖短步训练与初始化，不覆盖保存、重启、完整 epoch 或 eval。
3. 独立 `9907`-step、8-GPU、global batch 128 的 save2k run 在 step 1903 附近出现 rank `-9`，launcher 记录 `EXIT=247`；这是长跑/资源 gate 的失败线，不是 save/load 成功线。
4. no-cycle、同为 `9907` steps 的 save1500 run 进入保存点后明确失败：DeepSpeed 调用 `module.state_dict(destination=..., prefix=..., keep_vars=...)`，Cosmos `DiffusionModel.state_dict()` 不接受 `destination`，launcher `EXIT=1`。这条 first divergence 比“目录存在”更强，但仍没有产生可加载权重。
5. `remote_outputs_20260629` 目录共 `65` 个文件、`18` 个 run contract、`13` 个 base-load summary、`9` 个 exit-code 文件，**0 个 checkpoint-like binary**（`.pt/.pth/.ckpt/.safetensors/.bin` 或 checkpoint 文件名）。因此当前 P0 状态是 `PARTIAL`：base load 通过，短 smoke 通过，长训与 save gate 未闭合，checkpoint/save-load parity 缺失。

面试最安全的说法是：

> 我把“模型能初始化”“1-step/5-step smoke 能跑”“长跑资源 gate”“保存接口”拆开验收。base HF snapshot 的 715 个 key 在 13 条 load summary 中都无 missing/unexpected；短 smoke 有 exit 0。但 9907-step save2k 线在长跑中以 rank -9/EXIT=247 退出，no-cycle save1500 线又在 DeepSpeed 标准 `state_dict` 参数签名处退出。归档中没有训练产出的 checkpoint binary 或新进程 reload parity，所以我能认领的是 gate 分层和 first divergence 审计，不能说 1 epoch 已完成或 checkpoint 可加载。

## 2. 问题（Question）

为什么不能把 `base_load_summary`、1-step/5-step smoke 或一个已经创建的 `step_001500` 目录当作 checkpoint 完成？哪一个 run 证明了长跑资源问题，哪一个 run 证明了保存 API 问题？当前证据能把“初始化、训练、保存、重启加载、评测”五个 gate 关闭到哪一层？

## 3. P0 promotion 结论

```text
P0 status = PARTIAL
base-model initialization = PRESENT
short training smoke = PRESENT
long-run 1-epoch completion = 0
checkpoint save = 0
new-process load parity = 0
same-checkpoint eval = 0
ownership = PENDING
```

| Gate | 证据 | 状态 | 能说什么 | 不能说什么 |
| --- | --- | --- | --- | --- |
| base model load | 13 summaries；715 keys；missing/unexpected=0 | `PRESENT` | HF snapshot 在这些进程中 key-level load 通过 | 不能说本地训练 checkpoint 已保存/可重载 |
| 1-step smoke | fixed-optional 与 bs8 记录 `exit=0` | `PRESENT / SMOKE` | 初始化、一个 training step 和分布式启动可运行 | 不能覆盖 checkpoint 或长时资源 |
| no-cycle 5-step | `smoke5_exit_code.txt=0`，5 条 metrics | `PRESENT / SMOKE` | iterator 修复下短运行可启动 | 不能证明 9907 steps、save 或 eval |
| 9907-step save2k | run contract + launcher `rank=-9`/`EXIT=247` | `FAILED` | 长跑在保存前后出现外部 kill/资源失败线 | 不能把中间 loss 当 epoch 结果 |
| 9907-step no-cycle save1500 | launch log TypeError at `state_dict(destination=...)`，`EXIT=1` | `FAILED / FIRST DIVERGENCE` | 保存 API 的具体错误点可复核 | 不能说 `step_001500` 目录就是权重 |
| checkpoint binary | 65-file archive 中 checkpoint-like count `0` | `MISSING` | 只能保留 remote output path/日志 | 不能给 checkpoint SHA 或 reload parity |
| new-process reload | 没有 load-after-save command/result | `MISSING` | 只能把它列为恢复动作 | 不能说参数、optimizer、global step 已恢复 |
| matched eval | 没有同一 produced checkpoint 的 eval bundle | `MISSING` | 不升级为 trained-model benchmark | 不能与 official-HF `84/118` join |
| ownership | operator/patch author/reviewer 未人工确认 | `PENDING` | 只能讲 evidence-backed run boundary | 不能从远端路径推导个人贡献 |

## 4. Frozen inputs 与 SHA-256

| 证据 | SHA-256 | 用途 |
| --- | --- | --- |
| `base_load_summary.json`（13 份内容相同） | `197419EDBEB136DC54F8CC746C5E889FC03FA37A2C0CDA077D4F43441DE81CB9` | load path、HF cache snapshot、715 keys、missing/unexpected |
| save2k `run_contract.json` | `A8D8EB2FE76F2B9EA80DB23C6DCCE006D6B981B68396BEA16E31A5EF9F852BC8` | 8 GPU、per-GPU batch 16、9907 steps、save every 2000、5 frames |
| save2k `launch.log` | `F416050867C71ECC6BA5A7C67AFC67028B04BEC7A1E9DC4F4956BEA5531616C2` | base load、长跑退出、rank -9 与 `EXIT=247` |
| no-cycle save1500 `run_contract.json` | `201B4EEA49DCC5B53F6785B10D1DB3697E286C046A3FA2E060CA063CC7465DF2` | 同一 9907-step contract、save every 1500 |
| no-cycle save1500 `launch.log` | `8FEC262805242AFC3FCD7846A3DDB1043860E17BF5DEB008369D7CD9F67061C3` | DeepSpeed `state_dict(destination=...)` TypeError、`EXIT=1` |
| no-cycle smoke5 `run_contract.json` | `1D0BFE1F1125FC78FA224DA4449E7C60E22161B29345FA0D5F27830AD4E11B18` | 8 GPU、batch16、5 steps、save disabled、5-frame contract |
| no-cycle smoke5 metrics | `5CBD9BBCCE2B3EF171A35F022F84C8320248033F2C0502FCD3251EDFB7D0C50A` | 5 step-level scalar records |
| no-cycle smoke5 exit code | `9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA` | 内容为 `0` |
| formal1420 metrics snapshot | `EDC4799C7494ADE72B9A93D692472B2C1BD3712ECB5C5AD92597CB6540511D31` | 13 条 early scalar records；不是完整曲线 |
| parent `metrics.jsonl` | `C9B8B081EA3FF1329804DD6923FC5ED3AA3EA8FA36BF7E0248DF050B51608C28` | save2k 线仅保留 step100 单条 metrics |
| 1-epoch evidence freeze | `7C9C4EA2B317A00DF72B1CB29457B1ACD112066C01AA25BC6E750F8D0DE91AA6` | 前一切片的 cgroup-OOM / step1500 边界 |
| WAM full10k reconciliation | `70DB0DD0271FD3A90E9DF0D011AA30A52CBFB8E6131773CFCC36C128DC122706` | 与独立 full10k run family 分离 |

原始归档根目录：

```text
C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623
```

其中 `remote_outputs_20260629` 只包含日志、JSON、contract 和脚本快照；本页没有把远端 `/data/msz/wm/outputs/...` 路径当作本地权重证据。

## 5. 官方与本地训练合同

5 条主要 run contract 均采用 Cosmos Predict2 / RoboCasa route：

| 字段 | save2k / save1500 formal | no-cycle smoke5 | 证据边界 |
| --- | --- | --- | --- |
| experiment | `cosmos_predict2_2b_480p_robocasa_50_demos_per_task` | 同上 | contract 直接证据 |
| data_dir | `success_only_from_all_episodes` | 同上 | path reference，不等于本地数据 hash |
| rollout_data_dir | `all_episodes` | 同上 | path reference |
| T5 | `success_only_from_all_episodes/t5_embeddings.pkl` | 同上 | 未冻结 binary/hash |
| model class | `CosmosPolicyVideo2WorldModel` | 同上 | contract 直接证据 |
| dataset class | `RoboCasaDataset` | 同上 | contract 直接证据 |
| batch / world size | 16 per GPU / 8 | 16 per GPU / 8 | global batch 128；不是结果本身 |
| max steps | 9907 | 5 | smoke 与 formal gate 不可混合 |
| save interval | 2000 或 1500 | 0 | smoke 禁止把不保存当作 save 通过 |
| p_world_model | 0.5 | 0.5 | objective-side contract |
| action loss multiplier | 1 | 1 | objective-side contract |
| conditional frames | `[5,5]` | `[5,5]` | 与上轮 TurnOffMicrowave 诊断的 conditioning 边界一致 |

base model load summary 的 `local_path` 是：

```text
/data/msz/wm/hf_cache/hub/models--nvidia--Cosmos-Predict2-2B-Video2World/
snapshots/f50c09f5d8ab133a90cac3f4886a6471e9ba3f18/model-480p-16fps.pt
```

这表示进程从 HF cache snapshot 读入上游 base model；它不是 `iter_001500` 或 `iter_010000` 的训练产物。

## 6. 模型输入输出与保存边界

从 contract 可直接确认的模型接口是：`RoboCasaDataset → model.training_step(data_batch, iteration) → CosmosPolicyVideo2WorldModel`。数据 batch 包含 RoboCasa images/proprio/T5 conditioning 与 action/future/value route，但该归档没有单独的 head-shape manifest，因此不把“action/world/value 三个独立 head”写成实现事实；更保守的解释是共享模型内的路由、slot 和 loss contract。

保存前至少需要同时满足模型参数、优化器/调度器状态、global step 与 DeepSpeed 分片元数据的可写入；本轮只看到 DeepSpeed 进入 `_save_checkpoint → module_state_dict → module.state_dict(...)`，没有看到 save/load 完成记录。

对一个 run \(r\)，本页把验收状态写成：

\[
G_r=(L_r,T_r,S_r,R_r,E_r),
\]

其中 \(L\) 是 base-load key check，\(T\) 是 training-step smoke，\(S\) 是 checkpoint save，\(R\) 是新进程 reload parity，\(E\) 是同 checkpoint eval。当前 smoke run 的状态近似为 \((1,1,0,0,0)\)，formal save2k/save1500 run 分别是 \((1,?,0,0,0)\) 与 \((1,1,0,0,0)\)。变量与状态来自 `base_load_summary`、`run_contract`、`launch.log` 和缺失的 checkpoint/reload artifact；直觉是“初始化通过”不能跨越保存、重启和评测三个 gate。

## 7. Run 总账

| Run ID | 目的/变化 | 配置 | 结果 | 结论 |
| --- | --- | --- | --- | --- |
| `ds_base_load_smoke_1548` | 只验证上游 base load | 1 process、max steps 0 | 715 keys，missing/unexpected 0 | load gate 通过；无训练/保存 |
| `ds_train_smoke_1556` | 1-step train smoke | 1-step、fp route | base load summary 通过 | 短训练启动；无 save/load |
| `ds_8gpu_1step_fixedoptional_1728` | 修复 optional metrics/config 的 8-GPU 1-step smoke | batch1/GPU、world8、max1 | `exit=0` | 分布式短 smoke 通过 |
| `ds_8gpu_bs8_1step_1738` | batch8 1-step 对照 | batch8/GPU、world8、max1 | `exit=0` | batch 变体短 smoke 通过 |
| `ds_8gpu_bs16_nocycle_smoke5_1400` | iterator no-cycle 最小 smoke | batch16/GPU、world8、max5、save0 | `exit=0`；5 metrics | iterator 修复短 smoke 通过 |
| `ds_8gpu_bs16_1epoch_save2k_2040` | formal 9907-step gate，save every 2000 | batch16/GPU、world8、p_world=.5 | rank -9、`EXIT=247`；仅 step100 metrics | 长跑资源/外部 kill 线失败 |
| `ds_8gpu_bs16_1epoch_nocycle_save1500_1420` | no-cycle 后重跑 formal gate | batch16/GPU、world8、save every1500 | 保存时 TypeError，`EXIT=1` | save API first divergence |
| `formal1420_metrics_snapshot` | 对 no-cycle formal run 的 early snapshot | 13 scalar records | step13 loss `2.6662`；随后仍在 save gate失败 | 只能作为片段，不是完整 loss curve |

## 8. 训练 Loss 曲线与可比性

本轮没有完整可绘制的 formal loss curve：

- parent save2k `metrics.jsonl` 只有 1 条 step100 记录，loss `0.609638`；
- no-cycle smoke5 有 5 条记录，loss 从 `2.911592` 到 `2.995014`，但只有 5 steps；
- formal1420 snapshot 有 13 条 early records，step13 loss `2.666178`，随后保存 gate 失败。

因此不能把三条线连接成一条“训练收敛曲线”，也不能用 step100 的 `mse_loss=0.053420` 叫作 epoch MSE。保存的标量可以用于诊断字段覆盖：例如 step100 记录 `world_model_sample_frac=0.1953`、`value_function_sample_frac=0.3281`、GT gripper negative fraction `0.6465`；它们说明 loss logging 在早期可用，不说明最终策略效果。

## 9. 保存失败与资源失败的因果分析

### 9.1 save2k：长跑/外部 kill 线

save2k contract 的 `max_steps=9907`、`batch_size_per_gpu=16`、`world_size=8` 与 `save_every_steps=2000`。launch log 最终记录一个 rank 以 `-9` 退出，DeepSpeed launcher 汇总 `EXIT=247`；前一审计中的 cgroup memory 证据把 step1903 的异常归入 CPU cgroup OOM 候选。当前页只把它称为 **resource/launcher failure line**，因为本 bundle 没有完整 cgroup event 文件、最终 RSS 曲线或 checkpoint artifact。

### 9.2 no-cycle save1500：保存 API first divergence

no-cycle run 的 5-step smoke 通过后，formal save1500 继续到保存点。错误栈核心是：

```text
DeepSpeed engine._save_checkpoint
  -> module_state_dict
  -> self.module.state_dict(destination=destination, prefix=prefix, keep_vars=keep_vars)
TypeError: DiffusionModel.state_dict() got an unexpected keyword argument 'destination'
EXIT=1
```

这条证据比“step_001500 目录存在”更强，因为它说明程序在实际生成可用 module state dict 前已经失败。但没有 patch diff、修复后 rerun、非空权重清单或 load parity，所以根因只确认到 API compatibility boundary，修复状态仍是 `OPEN`。

### 9.3 为什么两个 failure 不能合并

save2k 的 first failure 是长跑/外部 kill 线；save1500 的 first failure 是 state-dict signature 线；两者的 save interval、日期、输出目录不同。把 `EXIT=247`、`EXIT=1`、某个中间 loss 和一个远端 full10k checkpoint 拼成“同一条 1 epoch 训练”会丢失 run identity。

## 10. 假设—证据—修复审计

| 假设/问题 | 证据 | 修复/下一动作 | 当前状态 |
| --- | --- | --- | --- |
| base model 没有正确加载 | 13 summaries，715 keys，missing/unexpected=0 | 保留 snapshot identity；继续做 produced-checkpoint reload | `REJECTED FOR BASE LOAD` |
| 1-step/5-step 分布式路径完全不可运行 | fixedoptional/bs8/smoke5 exit0 | 将 smoke 与 formal gate 分开记录 | `REJECTED FOR SHORT SMOKE` |
| no-cycle 修复已完成全训练 | smoke5 exit0，但 formal save1500 exit1 | 先完成 save/load smoke 再跑长训 | `REJECTED` |
| save2k 是保存 API 失败 | save2k log 最终是 rank -9/EXIT247；没有 state_dict TypeError 作为 first error | 单独保留 resource failure line | `NOT THE SAME FAILURE` |
| save1500 只是远端同步延迟 | launch log 有明确 TypeError，archive 无 checkpoint binary | 修复 `state_dict` 标准签名并做新进程 reload | `REJECTED` |
| `step_001500` 目录等于 checkpoint | archive checkpoint-like count=0；错误发生在 module state dict | 生成 file manifest/hash、参数 key/shape、global step | `REJECTED` |
| early loss `0.0534` 是 epoch-level result | parent metrics 只有 step100 一条 | 记录 step/aggregation，补完整 curve | `REJECTED` |
| base load 通过即可跑 eval | 没有 produced checkpoint、reload 或 matched eval | 完成 save→destroy→load→fixed-input parity | `REJECTED` |

## 11. 恢复所需的最小 save/load smoke

```python
def verify_checkpoint_gate(model, engine, fixed_batch, output_dir):
    # 1. Run one real DeepSpeed training step under the target config.
    train_step(engine, fixed_batch)

    # 2. Save model, optimizer, scheduler and global-step metadata through the real API.
    tag = "step_000001"
    engine.save_checkpoint(output_dir, tag=tag)

    # 3. End the process so reload is not satisfied by in-memory parameters.
    destroy_process_group_and_exit()

    # 4. Start a fresh process, load the exact manifest and assert shard completeness.
    fresh_engine = build_engine_from_same_contract()
    load_result = fresh_engine.load_checkpoint(output_dir, tag=tag)
    assert load_result is not None
    assert parameter_keys_and_shapes_match(fresh_engine, output_dir, tag)

    # 5. Compare a fixed forward/loss before and after reload, including global step.
    reloaded = fresh_engine.forward(fixed_batch)
    assert close_enough(reloaded, reference_output)
    assert fresh_engine.global_steps == 1
    return "save_load_parity_pass"
```

这段伪代码是验收协议，不是归档中已经成功运行的脚本。`state_dict(destination=None, prefix='', keep_vars=False)` 兼容层、DeepSpeed shard/optimizer/scheduler metadata、文件 SHA、固定输入输出 parity 和新进程边界都必须在真实 run 中落档后，才能把 `S=R=1` 写入 gate state。

## 12. 公源、本地证据与 Ownership 边界

| 层级 | 本页支持 | 不支持 |
| --- | --- | --- |
| 公有上游 | PyTorch/DeepSpeed 标准 state-dict 调用形态；Cosmos Predict2/RoboCasa contract | 个人设计了 Cosmos 架构 |
| 本地证据 | base load summary、run contract、metrics、launch logs、exit codes | 训练 checkpoint binary/hash、reload parity |
| 本地推断 | save2k 与 save1500 是两类 first divergence；gate 必须拆分 | 资源失败的唯一 root cause、修复后必然成功 |
| 未核实 | candidate/operator/reviewer、patch author、远端权重归属 | “我完成了 1 epoch”“我修复了 DeepSpeed” |

## 13. 面试可用口径

### 30 秒版本

> 我把 checkpoint gate 拆成 base load、短 smoke、长跑、save、reload、eval 六层。13 个 base-load summary 都是 715 keys 且 missing/unexpected 为 0；8-GPU 1-step 和 no-cycle 5-step smoke 也能 exit 0。但 9907-step save2k 线在长跑中以 rank -9/EXIT=247 退出，no-cycle save1500 线又在 DeepSpeed 调用 `state_dict(destination=...)` 时 TypeError/EXIT=1。归档里 65 个文件没有任何 checkpoint-like binary，所以我能说初始化和 failure boundary 可审计，不能说 1 epoch 完成或 checkpoint 已可加载。

### 高压追问：目录里有 `step_001500`，为什么不是 checkpoint？

> 因为保存流程在生成 module state dict 时就失败了：DeepSpeed 传入 PyTorch 标准的 `destination/prefix/keep_vars`，Cosmos 的 override 不接受 `destination`。目录存在只说明 save routine 开始，不能证明 module weights、optimizer/scheduler、global step 或分片元数据写完。下一步必须做真实 1-step save，销毁进程，新进程 reload，核对文件清单/hash、key/shape、global step 和固定输入 forward parity。

### 高压追问：为什么 5-step smoke 通过还不够？

> 因为 smoke 的 save interval 是 0，且只有 5 steps；它只验证 no-cycle iterator、模型初始化、一个短训练路径和进程退出。正式 gate 需要 9907 steps、定期保存、最后保存、跨进程 reload 和同协议 eval。这个项目里 smoke 通过后，formal run 仍在 save1500 处暴露 state-dict 签名错误，正说明短 smoke 不是完整验收。

## 14. 下一步与关闭条件

1. 给 `DiffusionModel.state_dict` compatibility layer 补标准签名，并记录实际 diff、author 和 review boundary；不要只吞掉关键字参数。
2. 在 1-step/真实 DeepSpeed config 下完成 save→process exit→fresh load→fixed-input parity，生成 checkpoint file manifest 与 SHA-256。
3. 重新跑 save1500 formal gate，保留每个 rank 的 status、checkpoint shard、optimizer/scheduler/global-step 元数据。
4. 只有产生可加载 checkpoint 后，才做同 checkpoint 的 TurnOffMicrowave/RoboCasa eval；不要拿 official-HF `84/118` 或 full10k remote path 做无 key join。
5. 由候选人确认 iterator patch、state-dict patch、运行者、日志审计者与 reviewer 的角色；工具/协作者/上游代码分开登记。

在这些条件闭合前，本页保持 `PARTIAL/WARN`。它可以用于回答“如何定义 save/load gate、如何定位 first divergence”，不能用于宣称 1 epoch 完成、训练 uplift 或 checkpoint ownership。

## References

1. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\remote_outputs_20260629\`（65-file archive；run contracts、base-load summaries、metrics、launch logs）。
2. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\remote_outputs_20260629\ds_8gpu_bs16_1epoch_save2k_20260623_2040\launch.log`。
3. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\remote_outputs_20260629\ds_8gpu_bs16_1epoch_nocycle_save1500_20260624_1420\launch.log`。
4. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\remote_outputs_20260629\ds_8gpu_bs16_nocycle_smoke5_20260624_1400\run_contract.json` 与 `base_load_summary.json`。
5. `C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\nocycle_fix_20260624\smoke5_exit_code.txt`、`smoke5_metrics.jsonl`。
6. [Cosmos 1 Epoch Evidence Freeze](../../sources/vol_04_cosmos_policy_1epoch_evidence_freeze.html)。
7. [WAM 1 epoch / full10k Run Reconciliation](../../sources/vol_04_cosmos_policy_wam_full10k_run_reconciliation.html)。
8. [WAM Claim–Evidence Inventory](wam_claim_evidence_inventory.html)。
