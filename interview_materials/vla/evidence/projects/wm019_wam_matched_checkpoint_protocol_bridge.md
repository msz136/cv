# WM-019 WAM Matched-Checkpoint Protocol Bridge（iter_000010000）

> 状态：`matched-checkpoint-path / offline-to-rollout bridge / binary-unverified / WARN`  
> 审查日期：2026-07-18  
> 证据截止：2026-07-18  
> 范围：只证明离线 future-image metric 与 trained CoffeePressButton rollout 引用了完全相同的 checkpoint path；不把 path equality 当 checkpoint hash，不把离线视觉指标与 rollout success 直接相关或因果化。

## 1. Identity 结论

离线 `iter_000010000/0000_metrics.json` 的 `checkpoint_path` 与 trained action-rollout `manifest.json` 的 `checkpoint` 字段逐字节相同：

```text
/data/msz/wm/outputs/cosmos_policy_online_text_formal_20260605/
cosmos_policy/cosmos_v2_finetune/
cosmos_policy_online_text_formal_20260605/checkpoints/iter_000010000
```

UTF-8 path string SHA-256 为：

```text
6CAE0B6BAA4378F25A0AF92720303922B709F7B8A21994684E6F77B6ED14E833
```

这是路径字符串 fingerprint，不是 checkpoint binary SHA。当前 Windows 工作区没有该 checkpoint binary，不能独立验证权重内容、processor、normalizer 或 config。

## 2. 冻结输入

| role | local artifact | SHA-256 |
| --- | --- | --- |
| offline protocol manifest | `cosmos_policy_eval_like_dreamdojo_20260605/manifest.json` | `8C4872F711897F718621C7AE8A6DF49EEDDE759CBECEDE530A3D82ABA819EC71` |
| offline iter-10000 metrics | `iter_000010000/0000_metrics.json` | `C9AB7F04AFD9C9057CC548BF0176285E001BA778BCD37DC4FB7D857E29BAEC9D` |
| trained rollout manifest | `cosmos_policy_robocasa_action_rollout_20260605/.../manifest.json` | `809AE4F879C9421F954C7BFC26C70005B94387412449039F9FA8B6E479EF55CC` |
| trained action trace | paired rollout `actions.jsonl` | `9C6A4F00DA8107EB0C1FDDDC642D1986CD510D92F7F6E3A68ADE834E8B82CF2D` |
| trained raw video | paired rollout failure video | `59176353B1E069C6F3A3A20BDF13EE6A9FFD969537C5501B685293D87802877E` |

## 3. Protocol bridge

| field | offline future-image metric | trained action rollout | 是否相同 |
| --- | --- | --- | --- |
| checkpoint path | `.../iter_000010000` | `.../iter_000010000` | exact match |
| task semantics | prompt：press the button on the coffee machine to serve coffee | task=`CoffeePressButton`，description 同 prompt | semantic match |
| input episode | successful regen-demo HDF5，relative indices 0..62 | RoboCasa env episode 0 | 不同 |
| seed | 7 | policy seed 195 / env seed 0 | 不同 |
| horizon | chunk 32；4 denoising steps；12 future frames | 300 env steps；open-loop 16；5 action denoising steps | 不同 |
| output | future-image PSNR/SSIM | action trace、raw video、success predicate | 不同证据层 |
| denominator | sample_count=1 | episode_count=1 | 都过小且单位不同 |

这张表完成的是 checkpoint-reference bridge，不是 protocol equivalence。offline sample 与 rollout episode 不同，不能做逐样本 proxy-success correlation。

## 4. 两侧观测

### Offline future-image side

- `sample_count=1`，`future_frame_count=12`；
- future-only `PSNR=8.2140051576`、`SSIM=0.0428580477`；
- with-condition `PSNR=15.1975432224`、`SSIM=0.1164843517`；
- SSIM implementation 标记为 `skimage`，LPIPS 为 `null`。

### Action-rollout side

- 300 条 action rows，`policy_action7` shape `300×7`，`env_action` shape `300×12`；
- 无非有限 policy value；
- `max_steps=300`、`num_open_loop_steps=16`、`num_denoising_steps_action=5`；
- episode-level `success=false`，逐 step `success_after_step=True` 次数为 0；
- trained raw video 已本地哈希，但 checkpoint 仍未本地验证。

## 5. 能说与不能说

可以说：

> “离线 future-image metric 和一条 CoffeePressButton rollout 确实引用同一个 `iter_000010000` checkpoint path；我能分别复核 metrics JSON、rollout manifest、action trace 和视频。但离线与 rollout 的 episode、seed、horizon 和统计单位不同，所以我只把它当 checkpoint-reference bridge，不把 PSNR/SSIM 与 success 做相关或因果结论。”

不能说：

1. “checkpoint 已被本地 hash/加载验证”——当前只有路径字符串相同。
2. “PSNR/SSIM 低导致 rollout 失败”——n=1、输入不同、无 matched sample。
3. “iter 10000 比 iter 5000 成功率更差”——iter 5000 没有同协议 rollout denominator。
4. “episode 0 失败证明 WAM 0-success”——没有完整任务/seed/init ledger。

## 6. 下一步最小闭环

1. 获取 `iter_000010000` checkpoint binary 或 immutable remote content hash，并绑定 processor/normalizer/config SHA。
2. 对相同 task/init/seed，保存 future metric、action trace、controller、predicate 和 episode outcome。
3. 对 `iter_000005000` 补同协议 rollout，或对 `iter_000010000` 扩展多 sample/multi-seed；再计算 proxy-success correlation。
4. 在完成 matched protocol 前，WAM 历史 MSE/success/uplift 继续保持 `WARN/REMOVED`。

## 参考来源

1. [WAM Future-Metric Paired Diagnostic](wm019_wam_future_metric_paired_diagnostic.html)。
2. [WAM Action-Trace Paired Diagnostic](wm019_wam_action_trace_paired_diagnostic.html)。
3. [WAM Artifact Manifest](wm019_wam_artifact_manifest.html)。
4. [WM-019 Project Metric Artifact Gate](../../sources/vol_04_wm019_project_metric_artifact_gate.html)。
