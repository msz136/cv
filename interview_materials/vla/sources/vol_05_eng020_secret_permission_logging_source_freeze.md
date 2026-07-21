# VOL 05 ENG-020 Source Freeze：Secret / Token、数据权限与日志脱敏

> 状态：`source_frozen / VLA-ENG-020 / knowledge_drafted / card_1_of_1_unseen / WARN`  
> 冻结日期：2026-07-17  
> 证据截止：2026-07-17  
> 本切片冻结 `VLA-ENG-020` 的 secret lifecycle、最小权限、数据访问与日志脱敏来源和项目边界；下游已生成一个知识节点和一张 `unseen` 题卡，未生成口述成绩。  
> 前置：[ENG-019 Config Resolution / Run Identity](../knowledge/vol_05_engineering_eval_eng019.html)、[Robot Harness Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) 与五项目 evidence inventory。

## 问题（Question）

VLA 训练、评估和机器人 Agent 会接触模型仓库 token、对象存储/数据库 credential、私有数据、机器人 access token、内部路径以及带图像/视频/位置/用户文本的日志。怎样设计 secret 获取与轮换、least-privilege data access、deny-by-default authorization、结构化日志脱敏和可验证审计，而不让“为了复现而保存一切”变成泄露？

本节点要回答：

1. secret 应怎样创建、注入、轮换、撤销和审计，为什么 env/Kubernetes Secret 本身不等于安全？
2. 训练 job、评估 job、在线 policy/Agent 应分别拥有哪些最小权限？
3. dataset/checkpoint/log/episode/video 的访问与使用目的怎样进入 manifest，而不复制敏感数据？
4. 日志中哪些字段必须删除、遮蔽、tokenize 或只留 reference？
5. Robot Harness、UWM、OpenPiVLA、OPD 当前有哪些直接安全 hook，为什么仍不足以声称安全体系闭环？

## 1. Source Freeze 总表

| 来源 | 冻结 revision | source type | 许可 | 可支持 | 不能支持 |
| --- | --- | --- | --- | --- | --- |
| OWASP Secrets Management Cheat Sheet | `ae0b3f22` | official security guidance | CC-BY-SA-4.0 | secret lifecycle、rotation、least visibility、revocation、never log plaintext secret | 用户项目已经接入 secret manager、rotation 已验证 |
| OWASP Logging Cheat Sheet | `ae0b3f22` | official security guidance | CC-BY-SA-4.0 | access token/password/key 不应直接进日志；mask/sanitize/hash/encrypt 选项 | 某个 regex 能发现所有敏感数据、日志合规自动成立 |
| OWASP Authorization Cheat Sheet | `ae0b3f22` | official security guidance | CC-BY-SA-4.0 | least privilege、deny by default、每请求校验权限 | 具体云 IAM/RBAC 配置正确 |
| Kubernetes Secret / Good Practices | `website@5e1d1bde` | official docs | CC-BY-4.0 | Secret 默认未加密存储、base64 不是加密、at-rest encryption、least-privilege RBAC、external store | 创建 Secret object 即完成安全闭环 |
| NIST SP 800-53 Rev.5 OSCAL catalog | `oscal-content@78650f02` | primary control catalog | CC0/public domain | AC-3 access enforcement、AC-6 least privilege、AU-9 audit protection、IA-5 authenticator management | 本地项目满足 NIST 合规认证 |
| pydantic-settings 2.14.1 | `1d0ea26f` | official-code/docs | MIT | settings debug output 可能暴露 env/dotenv/secrets 值 | 本地 resolver 已实现安全 redaction |
| 本地 selected-file scan | 2026-07-17 | local-evidence | local/private | Robot token masking/scope hook、训练脚本 args/path 暴露面与 selected-file no-literal smoke | 全仓无 secret、生产 IAM/rotation/retention 已验证 |

官方来源定义安全原则和平台边界；训练/Agent 系统的 subject/action/resource matrix、数据 purpose manifest、redaction schema、canary tests 和 incident drill 是本节点的工程验收合同。

## 2. 冻结指纹与许可

| Artifact | URL | SHA-256 | 核验点 |
| --- | --- | --- | --- |
| OWASP Secrets Management | [pinned source](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Secrets_Management_Cheat_Sheet.md) | `098b2e35ca5b9846bb35cb80fa9eef59aa97d76e10a12a5ff25b121f2c5770bd` | rotation、short-lived token、least privilege、revocation、never log |
| OWASP Logging | [pinned source](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Logging_Cheat_Sheet.md) | `342a2e9161f004a4aebe217da8476344e1b117f579f6252969e3b9054253eca7` | token/password/key removal or mask/sanitize/hash/encrypt |
| OWASP Authorization | [pinned source](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Authorization_Cheat_Sheet.md) | `3292a02e4c3c8424e2f33b79585eb79320d4c1c48725e5564860c07d503ff88a` | least privilege、deny-by-default、validate every request |
| OWASP LICENSE | [pinned source](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/LICENSE.md) | `2b47ecdd5078e948395bc5980226933854228ff688f10d1dd059208be4956084` | CC-BY-SA-4.0 |
| Kubernetes Secret | [pinned source](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/configuration/secret.md) | `7b39556e8ee3853333baa278f8b770048a334c38fe076181ee29deffc813dbac` | 默认未加密、at-rest encryption、RBAC、external store |
| Kubernetes Secret Good Practices | [pinned source](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/security/secrets-good-practices.md) | `06b70ffff8db80ff9f5a456dc9d2fa653549d72b9514b8503864ed7d0637d33d` | base64 非加密、least-privilege Secret access |
| Kubernetes website LICENSE | [pinned source](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/LICENSE) | `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411` | CC-BY-4.0 |
| NIST SP 800-53 Rev.5 catalog | [pinned OSCAL](https://github.com/usnistgov/oscal-content/blob/78650f02ad9321bb7b817846f8fbd4f2bcd620de/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json) | `01f37cf90ea99d92242c936cbfbdebcc338eef1f71454e2acac36cc56e9bc062` | AC-3、AC-6、AU-9、IA-5 control prose |
| NIST OSCAL LICENSE | [pinned source](https://github.com/usnistgov/oscal-content/blob/78650f02ad9321bb7b817846f8fbd4f2bcd620de/LICENSE.md) | `9f0ddd1ed71f691bb483965a7c46e1315ab6cc28dac0426d4c3d27108aafde13` | US public domain + CC0 dedication |
| pydantic-settings docs | [ENG-019 frozen revision](vol_05_eng019_config_resolution_run_identity_source_freeze.html) | `569a3398f65c99f3f72c73b891f633f1767c79992110ebb0a90b136cc95205b9` | debug source output 可能包含 secrets |

所有 SHA 对 2026-07-17 取得的 pinned UTF-8 原文计算；NIST catalog 为约 10 MB 的官方 OSCAL JSON。这里引用 control text 不代表本仓库通过 NIST assessment。

## 3. Threat Model：四类资产、五条泄露路径

| 资产 | VLA/Agent 例子 | 常见泄露路径 |
| --- | --- | --- |
| secret/authenticator | HF/W&B/cloud token、robot access token、DB/object-store credential | repo、CLI/history、env dump、exception、tool payload/log |
| sensitive data | 用户 prompt、图像/视频/音频、位姿/轨迹、位置、订单或业务数据 | dataset copy、debug sample、episode/video、metrics attachment |
| infrastructure metadata | 内部 hostname/IP、bucket/path、checkpoint/model location、robot ID | plan/args、stdout、manifest、error message |
| model artifact | checkpoint、adapter、processor、normalizer、training data fingerprints | 过宽读写权限、public artifact、错误 promotion、日志上传 |

需要同时防：静态 hardcode、运行时过权、日志/异常外泄、artifact 误发布和撤销不生效。一次 regex 扫描只覆盖部分静态字符串，不能证明运行时或下游系统安全。

## 4. Secret Lifecycle：引用 secret，不复制 secret

推荐状态机：

```text
REQUEST → AUTHORIZE → ISSUE/LEASE → INJECT → USE
   ↑                                  ↓
REVOKE ← ROTATE/EXPIRE ← AUDIT ← ZEROIZE
```

工程合同：

- 生产 job 使用 workload identity 或短期、最小 scope credential；避免共享长期静态 token。
- secret value 由 secret manager/volume/sidecar/workload identity 在运行时注入；config、manifest 和 checkpoint 只保存 provider/key/version reference。
- 轮换要支持 overlap/grace 与快速撤销；失败时默认 deny，不降级到硬编码 fallback。
- process memory、临时文件、core dump、exception、child process env 和 artifact uploader 都在泄露面内。
- 对 expired/revoked token 做负向测试；对每次 secret 使用记录 subject/resource/action/result，而不是 secret value。

OWASP 明确要求 secret 只对需要者可见、可撤销、定期轮换且不记录明文；环境变量或 Kubernetes Secret object 只是注入载体，不自动提供完整生命周期。[1][4]

## 5. Authorization：deny by default + least privilege + every request

可把授权决策写成：

\[
allow=Policy(subject,action,resource,context),\qquad default=deny
\]

变量和实现映射：`subject` 是 user/service account/job/robot session，`action` 是 read/write/list/delete/execute/publish，`resource` 是 dataset shard/checkpoint/log/robot/tool，`context` 包含 purpose、scope、environment、time、attempt 和 approval。没有显式 allow 就拒绝；每次请求重新校验，而不是只在 UI 或 job 启动时检查一次。

NIST AC-3 要求按批准的 authorization 执行逻辑访问；AC-6 要求用户或代表用户的进程只拥有完成任务所需权限。OWASP 同样要求 least privilege、deny by default 和每请求 permission validation。[3][5]

### 5.1 VLA job 权限拆分

| Principal | 最小读权限 | 最小写权限 | 不应拥有 |
| --- | --- | --- | --- |
| preprocess job | 指定 raw dataset/version | 指定 derived dataset/temp prefix | checkpoint/final publish、其他数据集 |
| train job | approved dataset、base model、normalizer | attempt temp、checkpoint generation、metrics | 删除 raw data、覆盖他人 final、全 bucket list |
| eval job | immutable checkpoint、frozen eval split/protocol | attempt-scoped raw result/summary | 训练数据写、checkpoint overwrite |
| policy/Agent service | approved model、当前 request/scope | scoped event/audit result | 任意 robot/tool、训练数据、长期 cloud admin token |
| publisher | committed artifact + review gate | immutable release/pointer | 训练执行、raw secret/data read |

world-readable mount、共享云账号和“一个 token 跑完所有阶段”都破坏 least privilege，也让 ownership/incident attribution 失真。

## 6. 数据权限不是文件可读性

数据 access gate 至少记录：

```text
dataset_id / immutable revision / owner
classification / license-or-consent / approved purpose
allowed principals / allowed actions / environment
retention / deletion / export / derived-artifact policy
approval reference / access-policy revision / audit sink
```

“路径能打开”“HF dataset 可下载”“远端同事给了目录”都不等于允许用于训练、评估、对外展示或长期保留。VLA 数据还可能包含人脸、语音、家庭/工厂布局、地理位置、机器人序列号和业务物品；derived embedding、sample video、failure gallery 与 checkpoint 也可能继承限制。

上述 purpose/classification/derived-artifact schema 是工程合同；OWASP/NIST 支持授权与最小权限原则，但不会替项目判断具体数据 license、consent 或组织 policy。

## 7. Kubernetes Secret：base64 不是加密

Kubernetes 官方文档明确：Secret 默认在 API server 底层 data store 中未加密存储，base64 只是编码；应启用 encryption at rest、配置 least-privilege Secret RBAC，并考虑 external Secret store。[4]

训练集群的最低 gate：

1. job 使用独立 service account，不给 namespace-wide Secret list/watch；
2. 只挂载该 job 需要的 secret，文件权限与容器用户最小化；
3. etcd/API audit、backup、debug dump 与 support bundle 同样受保护；
4. 禁止把 Secret manifest、decoded value、pod env dump 上传到 experiment tracker；
5. rotation/revocation 与 running job 的刷新/失败语义要演练。

创建 Secret object、把值 base64 或用 env 引用都不能单独支持“credential 已安全管理”的面试 claim。

## 8. 日志：结构化 allowlist 先于 regex redaction

日志输出可抽象为：

\[
L=Redact\left(Allowlist(E,S)\right)
\]

`E` 是原始 event，`S` 是 versioned logging schema；`Allowlist` 只选择必要字段，`Redact` 再按类型删除/遮蔽/tokenize。实现上应优先 allowlist，因为 denylist/regex 不可能穷举新 key、嵌套对象、异常字符串和图像内容。[2]

| 字段类型 | 默认处理 | 可保留形式 |
| --- | --- | --- |
| access/refresh token、password、private key | 删除 | secret provider/key version reference |
| Authorization/cookie/DB connection string | 删除 | auth method、credential class、result |
| user prompt、图像/音频/video/trajectory | 默认不记录原文 | request ID、content hash、classification、采样后的受控 artifact ref |
| internal path/host/robot/user ID | mask/tokenize | stable scoped pseudonym 或 hashed reference（有 threat review） |
| stack trace/tool payload | schema-filter + length cap | error class、owner、first-failure correlation ID |
| audit decision | 保留并防篡改 | subject ref、action、resource ref、policy revision、allow/deny、reason |

OWASP Logging 明确列出 access token、authentication password、encryption key 等通常不应直接记录，并建议 remove/mask/sanitize/hash/encrypt；NIST AU-9 还要求保护 audit 信息和 logging tools 不受未授权访问、修改与删除。[2][5]

## 9. 本地证据：Robot Harness

Selected local files：

```text
server/agent/deps.py        SHA C083E0208406A668C922BA430FB1CDF8550AA5F3828968AC70FB6A4FDD30C98F
server/agent/runtime.py     SHA CEE9148C2987DA7FF6839534EBCFED75B953A8678742AD9442523F96A6A77280
server/agent/history.py     SHA CAD470FC6B00470C37636285A3F84732EBFCDEB824612D0439AA65B70B5FC805
server/tools/registry.py    SHA EF1AFE36697D16F4C2A1392F618444712A87F2F88EE3BDABE409BD2948D24CF1
server/services/chat_stream.py SHA 029EE34A7A310DF54CD0A73CCA80D155F0D1C0A8E2476696D880348C42444035
```

直接证据：

- `AgentDeps` 和 runtime 传递 request `access_token`、scope、robot 和 cancel context；registry 按 tool name/allowed robot scope 过滤。
- registry 在 tool payload log 前把 `__access_token` 替换为 `***`，并从 dedup hash 中排除 `__access_token`、request/robot metadata。
- semantic-navigation 使用命名 credential `ACEROBOTICS_NAV_SEMANTIC_TOKEN` 构造 Authorization header，并在缺失时失败。
- history 会压缩/移除 action-tool history；这是 runtime exposure reduction，不等同正式 retention/privacy policy。

安全口径：可以说“存在 request scope 和一个已核验 token-mask hook”。不能说所有 token/key/cookie/nested payload 都会脱敏，也不能说 token 来源、TTL、rotation、revocation、secret manager、RBAC、audit protection 或数据 purpose 已闭环。当前 mask 是 key-specific，不是 versioned sensitive-field registry。

## 10. 本地证据：UWM、OpenPiVLA、OPD 与 WAM

| 项目 | selected direct evidence | 暴露面 / 缺口 |
| --- | --- | --- |
| UWM | launcher SHA `E5B6...D92`，`set -Eeuo pipefail` 且未启用 shell xtrace | stdout 打印 run/log/checkpoint/internal path；未见 secret manager、env allowlist、data permission/retention manifest |
| OpenPiVLA | formal trainer SHA `51B6...C6F94`；保存 `formal_plan.json`，checkpoint state 序列化全部 `vars(args)` | 当前 args 无 secret 字段，但“序列化全部参数”没有通用 redaction；path/data/model metadata 会进入 artifact |
| OPD | trainer SHA `BF91...D8D9`；summary 保存 data/model/teacher paths 与部分训练字段 | partial summary 没有敏感字段 schema、purpose/permission、retention、secret scan result |
| WAM | inventory 未发现 local code/config/log/checkpoint bundle | 不能评价 token/IAM/logging implementation；保持 unverified |

OpenPiVLA smoke metadata 中的 `private_data_deployed=false` 只能描述该 smoke artifact，不证明 formal runs 的数据授权；UWM/OPD 路径或 manifest 存在也不证明组织权限。selected-file scan 未发现硬编码 secret-named string literal，也未发现 access-token 直接进入选定 log sink；这是八个文件的启发式 smoke，不是全仓、历史 Git、binary、runtime、tracker 或对象存储的无泄露证明。

## 11. 安全扫描与证据合同

最低扫描层次：

```text
working tree + git history + image/layer + config/manifest
stdout/stderr + exception/core dump + experiment tracker
checkpoint/package + dataset sample + episode/video/gallery
runtime env/process/volume + cloud audit + object-store policy
```

静态 secret scanner 要用合成 canary 检验“能发现”，并把 false negative/allowlist 记录下来；真实 secret 不应被复制到测试报告。日志 redaction 要用 nested payload、header/cookie、exception、binary/URI、Unicode/encoding 和超长字段做 property-based tests。数据权限则需要 deny-case：未授权 principal、过期 approval、错误 purpose、跨 environment/export 均应失败并留下不含敏感值的 audit decision。

## 12. 验证伪代码（工程合同）

```python
def launch_secure_job(request, policy, secret_provider, log_schema):
    # 1. Deny by default; bind principal, action, resource, purpose and policy revision.
    decision = policy.authorize(request.subject, request.action,
                                request.resource, request.context)
    assert decision.allowed

    # 2. Lease only short-lived scoped references; never persist secret values.
    leases = secret_provider.lease(decision.secret_refs,
                                   ttl=request.max_runtime, scope=decision.scope)

    # 3. Emit only allowlisted/redacted events and protect the audit sink.
    logger = secure_logger(log_schema, redact_keys=decision.sensitive_fields)
    logger.audit(decision.without_secret_values())

    try:
        # 4. Run with least-privilege data/model/checkpoint capabilities.
        return run_job(request, leases, logger, capabilities=decision.capabilities)
    finally:
        # 5. Revoke/zeroize and verify no canary leaked to logs or artifacts.
        secret_provider.revoke(leases)
        zeroize_local_material(leases)
        assert no_secret_canary_in_outputs(request.attempt_id)
```

伪代码不代表任何本地项目已有实现；policy engine、workload identity、lease/revoke、secure logger、zeroization 和 canary scan 都需真实系统与演练证明。

## 13. 验证矩阵

| Case | 注入 | 通过条件 |
| --- | --- | --- |
| hardcoded secret | synthetic canary 写入 tracked/test fixture | scanner 阻断；报告只留位置/规则，不复制 value |
| CLI/process leak | canary 作为 CLI arg | job 拒绝或改用 secure injection；history/process list 无明文 |
| env/log leak | canary 进入 allowlisted/non-allowlisted env | resolver/log/exception/tracker/artifact 均无 raw canary |
| nested tool payload | token 放在 nested header/body | structured redactor 删除；长度 cap/serialization fallback 不绕过 |
| expired/revoked | 过期或中途撤销 lease | fail closed；无 hardcoded fallback；audit 有 reason |
| over-privileged job | train job 尝试删除 raw data/覆盖 final | policy deny，资源不变，audit sink 记录 |
| wrong data purpose | eval-only data 用于 train/export | deny；approval/purpose mismatch 可解释 |
| audit tamper | 非授权主体改/删 log | AU-9-style protection 阻断或告警 |
| incident rotation | 模拟 credential compromise | 快速撤销、轮换、重启/刷新语义和 blast radius 可量化 |

## 14. Gate 与不能使用的口径

| Gate | 当前状态 | 退出条件 |
| --- | --- | --- |
| official secret/log/auth source | `PASS WITH WARNING` | OWASP/K8s/NIST/pydantic 来源冻结；项目实现仍待证 |
| Robot Harness token/scope hook | `PASS WITH WARNING` | 已有 key-specific mask/scope；补 generic schema、TTL/rotation/revoke/audit tests |
| UWM/OpenPiVLA/OPD | `WARN` | data purpose/IAM、secret injection、redaction/canary、retention 与 audit artifacts |
| WAM | `UNVERIFIED` | 获取 local runtime/config/log bundle 后再评估 |
| selected-file no-literal scan | `PASS WITH WARNING` | 只覆盖八个文件；需全仓+history+image+runtime+artifact scan |
| knowledge/card | `DRAFTED / UNSEEN` | `knowledge_22_of_44`、`card_1_of_1` 已生成；保持 `unseen`，ENG-021 后置 |
| oral drill | `PENDING` | 候选人真实回答后才创建或更新 coaching state |

不能说：

1. “token 放环境变量里就安全”——env dump、child process、exception 和 tracker 仍可能泄露。
2. “Kubernetes Secret 是加密的”——base64 不是加密，底层存储默认未加密。
3. “日志里只打 hash 就不敏感”——低熵值可猜测，稳定 hash 还可能跨系统关联。
4. “有 scope 字段就完成 authorization”——需要 deny-by-default、每请求 enforcement 和 negative tests。
5. “路径可访问所以数据可训练/可展示”——仍需 license/consent/purpose/retention/export policy。
6. “scanner 没报警说明没有 secret”——规则覆盖、历史/runtime/binary/encoding 都可能漏检。
7. “Robot Harness 已全面脱敏”——当前直接证据只覆盖特定 `__access_token` payload hook 和 selected paths。

## 15. Source Gate 结论

ENG-020 的 source-first gate 已闭合：OWASP 支持 secret lifecycle、least privilege、deny-by-default 和敏感日志字段处理；Kubernetes 明确 Secret 默认存储/编码边界；NIST AC-3/AC-6/AU-9/IA-5 提供 access、least privilege、audit protection 和 authenticator management 控制。它们支持“短期 scoped secret + 每请求授权 + 数据 purpose manifest + allowlist/redaction logging + canary/negative/incident drill”的工程合同，但不证明本地项目已实现或合规。

当前最强 local-direct hook 是 Robot Harness 的 `__access_token` 定点 masking、dedup exclusion 和 robot/tool scope filtering；UWM/OpenPiVLA/OPD 提供了 args/path/summary 暴露面的真实 bad case。统一 secret manager/rotation/revoke、IAM/RBAC、data purpose/retention、generic redaction schema、audit protection 与全链路 canary 仍缺。Verdict 保持 `WARN`；知识页 `knowledge_22_of_44` 与一张 `unseen` 题卡已生成，ENG-021 不展开。

## References

1. OWASP, [Secrets Management Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Secrets_Management_Cheat_Sheet.md)。
2. OWASP, [Logging Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Logging_Cheat_Sheet.md)。
3. OWASP, [Authorization Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Authorization_Cheat_Sheet.md)。
4. Kubernetes, [Secrets](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/configuration/secret.md) 与 [Good practices for Kubernetes Secrets](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/security/secrets-good-practices.md)。
5. NIST, [SP 800-53 Rev.5 OSCAL catalog](https://github.com/usnistgov/oscal-content/blob/78650f02ad9321bb7b817846f8fbd4f2bcd620de/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json)：AC-3、AC-6、AU-9、IA-5。
6. Pydantic, [pydantic-settings 2.14.1](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/docs/index.md)：debug source output secret warning。
7. 本仓库，[ENG-019 Config Resolution](vol_05_eng019_config_resolution_run_identity_source_freeze.html)、[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html)。
