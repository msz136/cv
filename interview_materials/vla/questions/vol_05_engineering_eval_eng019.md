# VOL 05 Engineering / Evaluation：ENG-019 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-019`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-019 Config Resolution / Run Identity](../knowledge/vol_05_engineering_eval_eng019.html)；来源边界见 [Source Freeze](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)。当前项目没有统一 field source map、secret-safe canonical hash 或 run→checkpoint→eval immutable lineage，不能把 partial args/config 说成完整可复算系统。

## Config / CLI / Env 合并与 Run Identity

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-019</b> · YAML、CLI、环境变量和 runtime-derived 参数冲突时，你如何解析配置并生成稳定 run identity？</summary>

**面试意图**：判断你能否说明 framework-specific precedence、字段 provenance、typed validation、semantic/attempt identity 和 secret 边界，而不是只回答“保存 YAML”。

**30 秒回答**：先声明来源覆盖顺序，保存字段最终值、来源与旧候选；再分 semantic/execution/secret，对脱敏 semantic config 规范化，并绑定 code/data/model revision 生成 run key。attempt/rank/服务 ID 单记。当前缺完整 source map/lineage，不能说配置可复算。

**机制展开（约 2 分钟）**：Hydra、Pydantic、argparse 顺序不同，resolver 声明 precedence。先 allowlist env，merge-with-trace 后展开 auto/interpolation，再 typed validate；字段分 semantic/execution/attempt/secret。用 canonical semantic config 加 code/data/model revision 生成 run key，retry 新建 attempt，rank/服务 ID 不参与。UWM 有 env+Hydra，OpenPiVLA 有 args snapshot，OPD 有 WORLD_SIZE 改写，但都缺 provenance/lineage。

**诊断 / 证据**：保存 resolver/schema/canonicalization version、typed effective config、每字段 winning source/losing candidates、code/data/model revision、semantic hash、attempt/rank/restart、secret redaction 与 canary scan。验证等价 YAML 表示不改 run key，dataset/LR/seed 改变必须改 key；output dir/hostname 只改 attempt manifest；`auto` 展开和 world-size 对 global batch/sampler 的影响必须可复算。

**项目挂钩**：UWM launcher 直接显示 `${VAR:-default}`→Hydra CLI，另有 DeepSpeed effective subset；OpenPiVLA formal plan 和 checkpoint state 保存 argparse 值，但三份 YAML 未被 formal trainer 读取；OPD 会用 `WORLD_SIZE` 改写 DeepSpeed `auto`，summary 又只保留部分字段。它们支持具体 config 路径和 bad case，不支持统一 precedence/source map、secret gate 或 immutable lineage 已完成。

**追问树**：Hydra `_self_` 为什么影响结果？Pydantic priority 能否修改？原始 YAML SHA 与 effective config SHA 有何区别？`WORLD_SIZE` 何时属于 semantic？W&B/TorchElastic ID 与 run key 有何区别？怎样证明日志没泄露 secret？retry 后哪些 identity 保持稳定？

**易错点**：假设 CLI 永远最高；只 hash 原始 YAML；把 timestamp/W&B ID 当实验 identity；把 rank 编进 stable key；dump 全部 env；未展开 `auto` 就生成 hash。

**危险答案**：说“Hydra 会自动保证可复现”“配置文件相同就是同一实验”“把所有环境变量保存下来最安全”或“有 run ID 就能绑定 checkpoint 和评估”。

**来源**：[1][2][3][4]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-019 知识页](../knowledge/vol_05_engineering_eval_eng019.html)：precedence、typed effective config、provenance、identity、secret 与项目边界。
2. [ENG-019 Source Freeze](../sources/vol_05_eng019_config_resolution_run_identity_source_freeze.html)：Hydra/Pydantic/argparse/torchrun/RFC 8785 官方语义和本地直接证据。
3. [ENG-013 Reproducibility](../knowledge/vol_05_engineering_eval_eng013.html)：code/data/env/RNG/sampler run identity 与 replay 强度。
4. [ENG-018 Scheduler / Retry](../knowledge/vol_05_engineering_eval_eng018.html)：logical run、attempt、rank、restart 与 committed checkpoint。

