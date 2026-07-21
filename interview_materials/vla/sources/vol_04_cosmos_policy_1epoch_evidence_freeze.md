# VOL 04 Cosmos Policy 1 Epoch：本地证据冻结

> 状态：`local_evidence_freeze / 1epoch_gate_not_closed / WARN`
> 复核日期：2026-07-21  
> 证据来源：`C:\Users\mousongzhe\Project\report\cosmos_policy_eval`（只读审计）  
> Bounded slice：本页只冻结 Cosmos Policy / Predict2 RoboCasa 1 epoch 训练 gate 的运行合同、可观测指标、失败原因、checkpoint 与评估边界；不把远端路径、训练中间指标或官方 baseline 升格为完整本地结果，不改变题卡 `unseen` 或 ownership。

## 1. 结论先行

当前证据不能支持“完成了可加载的 1 epoch finetune checkpoint”这一表述。可支持的面试口径是：我按官方风格 Predict2 + T5 + RoboCasa 合同搭建了 8 卡 1 epoch gate，先定位到训练 loop 的 CPU 内存增长，再修复 dataloader 回卷；修复后的正式 run 能到第一个保存点，但在 DeepSpeed 调用 Cosmos `DiffusionModel.state_dict(destination=...)` 时因签名不兼容退出，因此没有可用于后续 eval 的完整 checkpoint。

这一区分很重要：

1. 训练合同和输入数据统计是 `local-direct`，可复核；
2. step 1900/1500 的 loss 是中断前快照，不是 epoch 终点指标；
3. 1 epoch 训练的 checkpoint identity、终点 eval denominator 与本轮 rollout 都没有闭合；
4. 已存在的官方 HF baseline `84/118` 和历史 1k/5k ablation 属于其他 run，不能拼接成这次 1 epoch 的结果。

## 2. 运行合同（Run Contract）

| 字段 | 证据 | 冻结值 | 边界 |
| --- | --- | --- | --- |
| experiment | `muxi_deepspeed_1epoch_20260623/run_contract.json` | `cosmos_predict2_2b_480p_robocasa_50_demos_per_task` | 官方风格实验名；不等于官方训练已完成 |
| base model | `base_load_summary.json` | `hf://nvidia/Cosmos-Predict2-2B-Video2World/model-480p-16fps.pt`；715 keys，missing 0，unexpected 0 | 本地记录了 load summary；权重 binary 仍是远端路径引用 |
| data | `dataset_runtime_summary.json` | dataset_len `1,267,980`；demo episodes `1,199`；rollout episodes `1,291`；rollout steps `343,635`；unique commands `242` | 数据统计可复核；不替代 dataset revision/license manifest |
| parallelism | `run_contract.json` | 8 GPU DDP，batch/GPU `16`，global batch `128`，grad accumulation `1` | 由 world size 与 batch 合同推出 global batch |
| optimization | `run_contract.json` | AdamW (`fused=False`)，`action_loss_multiplier=1`，`p_world_model=0.5` | optimizer 合同已冻结 |
| sequence | `run_contract.json` | conditional frames `[5,5]` | 与官方 RoboCasa query contract 对齐 |
| gate | `run_contract.json` | `max_steps=9907`，`steps_per_epoch_gate=9907` | 只有达到该 gate 且保存/加载成功，才可称完整 1 epoch |

## 3. Run ledger：两条主线与一个保存接口失败

### 3.1 save-2k 主线：CPU cgroup OOM，中断于 step 1903

运行目录：`muxi_deepspeed_1epoch_20260623/remote_outputs_20260629/ds_8gpu_bs16_1epoch_save2k_20260623_2040`。日志显示：

- `max_steps=9907`、`save_every_steps=2000`；
- 最后一条可信 metric 为 step `1900`，随后 step `1903` 后 launcher 返回 `EXIT=247`，rank 7 返回 `-9`；
- 没有 `step_002000` checkpoint，且没有可加载的 checkpoint directory；
- `eval_summary.md` 与 `status_save2k_20260624_0951.log` 将根因定位为 `itertools.cycle(dataloader)` 缓存已迭代 batch，最终触发 memory cgroup OOM，而不是 GPU OOM；
- 该 run 的终点只能写成“中断前 step-1900 snapshot”，不能写成 1 epoch final。

step 1900 的中间指标如下：

| metric | value | 解释 |
| --- | ---: | --- |
| total loss | `0.2945038` | 训练中间快照 |
| EDM loss | `0.0294504` | 主 denoising loss 的中间快照 |
| demo action MSE | `0.0463352` | teacher-forced 诊断项，不是闭环 success |
| future image MSE | `0.0562584` | world-model 诊断项 |
| value MSE | `0.0142408` | value 分支诊断项 |
| teacher-forced gripper dim MSE | `0.0761347` | 第 7 action 维；不等于 rollout gripper |
| GT negative gripper 下预测 `<-0.5` 比例 | `95.17%` | 仅 teacher-forced gate，不能外推到 eval |

### 3.2 no-cycle 修复主线：step 1500 保存阶段失败

修复目录：`muxi_deepspeed_1epoch_20260623/nocycle_fix_20260624`；正式 run contract 为 `formal1420_run_contract.json`，远端对应目录为 `ds_8gpu_bs16_1epoch_nocycle_save1500_20260624_1420`。

- 先用 8 卡、5 steps、`SAVE_EVERY=0` 的 smoke 验证普通 `iter(dataloader)` + `StopIteration` 重建 iterator，`EXIT=0`；
- 正式 run 仍为 `max_steps=9907`，保存间隔 `1500`；
- 训练可到 step `1500`，但 `exit_code=1`；
- 失败栈为 DeepSpeed `engine.save_checkpoint` 调用 `DiffusionModel.state_dict(destination=..., prefix=..., keep_vars=...)`，而 Cosmos `DiffusionModel.state_dict()` 不接受 `destination` 参数；
- `checkpoints/step_001500` 目录出现但没有可用权重文件；不能当作 checkpoint、不能触发 gripper gate、不能跑本轮 1 epoch eval。

因此本轮的修复结论是“数据迭代器内存问题已被定位并通过 smoke 修复；保存接口兼容性仍未闭合”，而不是“1 epoch 训练成功”。

## 4. 指标与评估边界

### 4.1 可以写进面试回答的事实

可以说：

- 我保留了官方 Predict2/T5/RoboCasa 的 action chunk `[32,7]`、proprio `[9]` 与 conditional frames=5 合同；
- 我用 `dataset_runtime_summary.json` 固化了 1,199 demo episodes、1,291 rollout episodes、343,635 rollout steps 和 242 条 command；
- 我从 step-1900 日志发现 CPU batch 缓存增长，并从 no-cycle smoke 验证修复方向；
- 我进一步把失败推进到 checkpoint 保存接口，能指出具体的 Python method-signature 不兼容，而不是泛泛说“训练 OOM”。

### 4.2 不可以写成这次 1 epoch 结果的数字

| 数字/结果 | 实际归属 | 不能如何表述 |
| --- | --- | --- |
| `84/118`、`86/120` | 官方 HF baseline 的 24×5 RoboCasa eval，见 `eval_summary.md` | 不能说是本地 1 epoch checkpoint 的 success |
| 1k/5k ablation 的 `0/1` 或 gripper gate | 其他本地小子集/ablation run | 不能与 1 epoch 中间 loss 拼成一条训练曲线 |
| step 1900 loss `0.2945` | save-2k run 的中断前快照 | 不能称 final loss、epoch loss 或 best checkpoint |
| step 1500 loss / teacher-forced gate | no-cycle run 的保存失败前快照 | 不能称可加载模型或 closed-loop eval |
| 远端 `/data/msz/...` checkpoint path | path reference | 不能当作 binary identity 或本地 artifact |

## 5. Evidence classification 与面试叙事

| 层级 | 本页允许的说法 | 仍缺什么 |
| --- | --- | --- |
| `local-direct` | run contract、dataset runtime summary、base load summary、step 日志、exit code、错误栈 | 保存后的权重、immutable manifest、完整 eval bundle |
| `remote-referenced` | 远端输出目录名、远端 checkpoint path、远端运行命令 | 权重内容、SHA、下载/加载记录 |
| `local-inference` | cycle 导致 batch 保留、state_dict 签名导致保存失败的因果解释 | 在同一环境修复后重跑并通过 save/load 验证 |
| `unverified` | 完整 9907 step、1 epoch final metric、1 epoch closed-loop success | 需要成功保存并重新加载 checkpoint，再固定 eval denominator |

建议口述结构：先说目标和合同，再说可观测失败，再说修复和新的失败点，最后明确“没有把中间指标冒充最终 benchmark”。这比只报一个 loss 数字更能体现训练系统排障能力。

## 6. 下一步闭环条件

要把该 run 从 `WARN` 升级为可用于项目题卡的 `local-direct checkpoint + eval`，至少需要：

1. 修复 `DiffusionModel.state_dict` 与 DeepSpeed/PyTorch 标准签名的兼容层，并用 1-step save/load smoke 验证权重可重载；
2. 重新运行 `max_steps=9907`，记录所有 checkpoint 的路径、文件列表、大小和 SHA-256；
3. 固定数据 revision、normalizer/stats、代码 commit、seed、denoising steps、open-loop horizon 和 action execution bridge；
4. 对同一 checkpoint 记录 eval task、trial、success predicate、invalid/error policy、raw episode manifest；
5. 只有在上述字段齐全后，才把结果写进 WAM P0 audit 和项目题卡的“最终结果”段。

## References

1. 本地主报告：`C:\Users\mousongzhe\Project\report\cosmos_policy_eval\eval_summary.md`（Windows 工作区中的只读外部证据；HTML/Markdown 报告保留完整 run ledger）。
2. 本地运行合同：`C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\run_contract.json`、`dataset_runtime_summary.json`、`base_load_summary.json`。
3. save-2k 日志：`C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\status_save2k_20260624_0951.log` 与 `remote_outputs_20260629\ds_8gpu_bs16_1epoch_save2k_20260623_2040\launch.log`。
4. no-cycle 修复与保存失败：`C:\Users\mousongzhe\Project\report\cosmos_policy_eval\muxi_deepspeed_1epoch_20260623\nocycle_fix_20260624\formal1420_run_contract.json`、`status_save1500_20260625_003645.log`、`smoke5_exit_code.txt`。
5. 上游机制与协议边界：[Cosmos/WAM Claim-to-Code Audit](vol_04_cosmos_policy_wam_claim_to_code.html)；本页不重复冻结 upstream 结构。
