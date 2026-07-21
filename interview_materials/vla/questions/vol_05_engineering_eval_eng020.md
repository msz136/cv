# VOL 05 Engineering / Evaluation：ENG-020 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-020`  
> 难度：L2 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-020 Secret Lifecycle / Permission / Logging](../knowledge/vol_05_engineering_eval_eng020.html)；来源边界见 [Source Freeze](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)。当前项目只有 Robot Harness 的特定 token-mask/scope hook 与 UWM/OpenPiVLA/OPD 的暴露面证据，不能声称统一 secret manager、IAM、data governance、generic redaction 或 audit protection 已闭环。

## Secret、数据权限与日志脱敏

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P1</span> <b>VLA-ENG-020</b> · VLA 训练、评估与机器人 Agent 系统如何管理 secret、数据权限和日志脱敏？</summary>

**面试意图**：判断你能否把 secret 生命周期、每请求授权、数据 purpose、结构化日志和审计验证串成一条可执行合同，并严格区分安全基线、本地 hook 与尚未实现的系统能力。

**30 秒回答**：secret 用短期最小 scope lease，运行时注入，manifest 只留 reference；数据/checkpoint/robot/tool 每次鉴权、默认拒绝。日志先 allowlist 再删 token/敏感原文，audit 防篡改；用 canary、过期撤销、越权和 wrong-purpose 负测。当前只有局部 hook，不说安全闭环。

**机制展开（约 2 分钟）**：先分 secret、敏感数据、内部 metadata、模型 artifact。secret 走 authorize→lease→inject→expire/revoke，值不进 config/checkpoint/log；preprocess/train/eval/Agent/publisher 各用最小 capability。manifest 绑定 owner、purpose、retention、export。日志按 schema allowlist 后脱敏，audit 防改删；用 nested canary、过期/撤销、越权、wrong-purpose、incident rotation 负测。Robot Harness 仅证明定点 mask/scope。

**诊断 / 证据**：保存 secret provider/key-version/lease reference、TTL/scope、authorization policy revision 与 decision、permission manifest、logging schema/redaction registry、audit integrity result 和 incident timeline；不保存 raw secret。验证 canary 不进入 CLI/env dump/log/tracker/checkpoint，expired/revoked token fail closed，train/eval/publisher 越权和 wrong-purpose 被拒绝，nested header/cookie/exception 无脱敏逃逸，非授权主体不能改删 audit。

**项目挂钩**：Robot Harness 的 registry 会遮蔽特定 `__access_token`，dedup 排除 token/request/robot metadata，并按 robot/tool scope 过滤；这是局部 direct evidence。UWM 会输出 run/log/checkpoint path，OpenPiVLA 序列化全部 args，OPD summary 保存 model/data/teacher path；它们是 exposure/bad-case 证据，不是 secret manager、IAM、retention 或 generic redaction 实现。

**追问树**：env var 和 Kubernetes Secret 为什么都不等于完整 secret management？长训练如何处理 lease 续期/轮换/撤销？为什么 train/eval/publisher 要不同 identity？数据限制怎样传递到 checkpoint/failure video？allowlist-first 为什么优于 regex denylist？普通 hash 为什么仍有风险？当前 mask 能被哪些 nested payload 绕过？怎样证明 audit 防篡改？

**易错点**：token 写 CLI/Docker ENV；把 Kubernetes base64 当加密；一个共享 token 跑全链路；只 mask 名为 `token` 的顶层 key；dump 全量 env/args/tool payload；把“路径可读”当训练/展示授权；scanner 零告警就宣称无泄露。

**危险答案**：说“放环境变量就安全”“有 scope 字段就是最小权限”“日志只存 hash 就不敏感”“Robot Harness 已全面脱敏”或“静态扫描通过证明 Git history、runtime、tracker 和 artifact 都没有 secret”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-020 知识页](../knowledge/vol_05_engineering_eval_eng020.html)：secret lifecycle、authorization、data permission、logging/audit、验证矩阵与项目真实性边界。
2. [ENG-020 Source Freeze](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)：OWASP、Kubernetes、NIST、pydantic-settings revision/SHA 与本地 selected-file direct evidence。
3. [ENG-019 Config Resolution](../knowledge/vol_05_engineering_eval_eng019.html)：effective config、run identity 与 secret-safe manifest 边界。
4. [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)：`__access_token` masking、dedup exclusion 与 robot/tool scope 的局部证据。
5. [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html)、[OpenPiVLA](../evidence/projects/openpivla_claim_evidence_inventory.html) 与 [OPD](../evidence/projects/opd_claim_evidence_inventory.html) inventories：args/path/summary 暴露面与未实现边界。
