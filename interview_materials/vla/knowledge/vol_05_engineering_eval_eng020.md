# VOL 05 Engineering / Evaluation：Secret Lifecycle、数据权限与日志脱敏（ENG-020）

> 状态：`drafted / knowledge_22_of_44 / card_1_of_1_unseen / review_warn`  
> 报告日期：2026-07-17  
> 证据截止：2026-07-17  
> 当前节点：`VLA-ENG-020`；来源已冻结，单张题卡同步生成并保持 `unseen`。  
> 来源入口：[ENG-020 Secret / Permission / Logging Source Freeze](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)。  
> 核心边界：OWASP、Kubernetes、NIST 给出安全基线；本地只有 Robot Harness 的特定 token-mask/scope hook 与训练项目暴露面，不能声称 secret manager、IAM、data governance 或审计体系已闭环。

## 问题（Question）

`VLA-ENG-020`：VLA 训练、评估与机器人 Agent 同时接触模型仓库/云/机器人 token、私有数据、checkpoint、内部路径和多模态日志时，怎样设计 secret 生命周期、最小权限、数据 purpose gate、日志脱敏和可验证审计？

回答应按五层展开：

1. **识别资产与泄露面**：secret、sensitive data、infra metadata、model artifact；
2. **管理 secret lifecycle**：lease、inject、use、rotate/expire、revoke、zeroize；
3. **每请求授权**：deny-by-default、least privilege、subject/action/resource/context；
4. **日志 allowlist + redaction**：不复制 token/原始多模态内容；
5. **用负向证据证明**：canary、expired/revoked、over-privilege、wrong-purpose、audit-tamper 和 incident drill。

## 知识地图位置与前置依赖

```text
ENG-009 data/provenance + ENG-019 config/run identity
                         ↓
asset classification → secret lease + data purpose authorization
                         ↓
least-privilege capability → train/eval/agent/publisher isolation
                         ↓
allowlisted event → structured redaction → protected audit sink
                         ↓
canary / deny-case / rotation / incident drill
                         ↓
ENG-021 model/processor/normalizer package gate
```

前置：

- `VLA-ENG-009`：dataset revision、provenance 和 transform manifest。
- `VLA-ENG-018/019`：logical run/attempt identity、effective config 和 secret redaction flag。
- VOL 07 Robot Harness：request token、scope、tool registry 与 history exposure。
- `VLA-ENG-021`：模型/processor/normalizer 打包将在独立节点展开。

## 1. 短答：短期 secret、最小 capability、allowlist 日志

**30 秒回答**：secret 用短期、最小 scope lease，在运行时注入，只在 manifest 留 provider/key-version reference；所有数据、checkpoint、robot/tool 请求按 subject/action/resource/purpose 每次鉴权，默认拒绝。日志先按 schema allowlist，再删除 token 和原始敏感多模态内容，audit sink 防篡改。最后用 canary、过期/撤销 token、越权和错误 purpose 做负向验证。当前项目只有局部 hook，不能说安全闭环。

## 2. Threat Model：安全不是只搜 API key

| 资产 | 示例 | 主要风险 |
| --- | --- | --- |
| secret/authenticator | HF/W&B/cloud token、robot access token、DB/object-store credential | repo/CLI/env/exception/tool payload/log 泄露；长期共享 |
| sensitive data | prompt、图像/视频/音频、位姿/轨迹、位置、订单/业务字段 | 未授权训练、debug sample/gallery 外传、retention 超期 |
| infrastructure metadata | hostname/IP、bucket/path、checkpoint/model location、robot/user ID | 内部拓扑暴露、资源枚举、跨系统关联 |
| model artifact | checkpoint、adapter、processor、normalizer、embedding | 过宽读写、错误 publish、继承训练数据限制 |
| audit evidence | authorization decision、secret use、incident timeline | 未授权改删、无法追责、日志本身含敏感值 |

需要同时覆盖：静态 hardcode、运行时过权、日志/异常泄露、artifact 误发布、撤销不生效和 audit 被篡改。secret scanner 只是其中一层；“没有命中 regex”不等于系统安全。

## 3. Secret Lifecycle：值只在需要时短暂存在

```text
REQUEST → AUTHORIZE → ISSUE/LEASE → INJECT → USE
   ↑                                  ↓
REVOKE ← ROTATE/EXPIRE ← AUDIT ← ZEROIZE
```

### 3.1 生命周期合同

- **Issue/lease**：优先 workload identity 或短期 credential；scope 只覆盖当前 job/request/resource。
- **Inject**：secret manager、read-only volume、sidecar 或 workload identity；不用代码常量、CLI、普通 config/manifest。
- **Use**：不进入 checkpoint、experiment tracker、exception、tool payload 或 debug dump。
- **Rotate/expire**：支持 overlap/grace、renewal 和中途失效；行为与训练 retry/checkpoint 合同对齐。
- **Revoke**：compromise/离职/job 结束可快速撤销；失败默认 deny，不回退到共享静态 token。
- **Zeroize/audit**：清理临时材料；audit 只记 subject/resource/action/result/provider reference，不记 secret value。

OWASP 要求 secret 仅对需要者可见、可撤销、可轮换且永不记录明文。环境变量只是载体：仍可能进入 process dump、child process、debug source、exception 或 tracker。[1]

### 3.2 Manifest 只存 reference

```json
{
  "secret_ref": {
    "provider": "example-secret-provider",
    "key_name": "model_registry_read",
    "version_or_lease_id": "opaque-reference",
    "scope": ["model:read"],
    "issued_to": "train-attempt-ref",
    "expires_at": "timestamp",
    "raw_value_persisted": false
  }
}
```

`opaque-reference` 只是示例 schema，不是 credential。不要默认保存 raw secret 的普通 hash：低熵密码/token 可能被离线猜测，稳定 digest 还可能造成跨日志关联。

## 4. Authorization：主体、动作、资源、上下文都要进入决策

\[
allow=Policy(subject,action,resource,context),\qquad default=deny
\]

变量和实现映射：`subject` 是 user/service account/job/robot session；`action` 是 read/write/list/delete/execute/publish；`resource` 是 dataset shard/checkpoint/log/robot/tool；`context` 包括 purpose、scope、environment、time、attempt 和 approval。policy engine 每个请求重新计算，不能只靠 UI 隐藏按钮或 job 启动时一次检查。

NIST AC-3 要求按批准 authorization 执行访问；AC-6 要求用户和代表用户的进程只拥有完成任务所需权限。OWASP 也强调 least privilege、deny by default 与 validate every request。[2][3]

### 4.1 Principal × Capability

| Principal | 允许读 | 允许写/执行 | 明确禁止 |
| --- | --- | --- | --- |
| preprocess | approved raw revision | derived temp/version | checkpoint/final、其他 dataset |
| train | approved dataset/base model/normalizer | attempt temp、checkpoint generation、metrics | 删除 raw data、覆盖他人 final、全 bucket list |
| eval | immutable checkpoint/frozen eval protocol | attempt-scoped result/summary | 训练数据写、checkpoint overwrite |
| policy/Agent | approved model、当前 request/scope | scoped tool/robot action、audit event | 任意 robot/tool、训练数据、cloud admin token |
| publisher | committed artifact + review decision | immutable release/pointer | 训练执行、raw data/secret read |

把 preprocess/train/eval/publish 拆成独立 identity，能缩小 blast radius，也能让 incident/ownership attribution 更清楚。

## 5. 数据权限：可读取不等于可训练、可展示、可导出

数据 permission manifest：

```text
dataset_id / immutable_revision / owner
classification / license_or_consent / approved_purpose
allowed_principals / allowed_actions / environment
retention / deletion / export / derived_artifact_policy
approval_ref / policy_revision / audit_sink
```

VLA/具身数据可能含人脸、语音、家庭/工厂布局、位置、机器人序列号和业务对象。限制不仅跟随 raw sample，还可能传递到 embedding、checkpoint、processor stats、failure video、episode trace 和 case gallery。

工程规则：

1. `train-only`、`eval-only`、`internal-debug`、`publishable` 目的分开；
2. split/protocol manifest 引用 permission revision；
3. derived artifact 计算继承/去标识后的新 classification；
4. retention 到期触发删除或审批续期；
5. wrong-purpose/export principal 必须 deny，并保存不含原始内容的 audit reason。

OWASP/NIST 支持授权原则，但具体 license、consent、purpose 和组织 policy 仍需项目 owner/法务/数据治理证据，不能由代码扫描替代。

## 6. Kubernetes Secret：对象存在不等于安全

Kubernetes 官方明确：Secret 默认在 API server 底层 data store 未加密，base64 只是编码；应启用 encryption at rest、least-privilege Secret RBAC，并考虑 external Secret store。[4]

训练集群最低 gate：

- 每个 job/service 独立 service account；禁止 namespace-wide Secret list/watch。
- 只挂载当前 job 所需 key；read-only、最小文件权限和非 root container。
- 保护 etcd、backup、API audit、support bundle 和 pod debug dump。
- 禁止把 Secret YAML、decoded value 或全量 env dump 上传 tracker。
- 演练 running job 的 lease renewal、rotation/revocation、fail-closed 与 recovery 行为。

危险说法：“用了 Kubernetes Secret 所以已经加密”“base64 防止泄露”“env 引用不会被日志打出来”。

## 7. 日志脱敏：先 allowlist，再 redact

\[
L=Redact\!\left(Allowlist(E,S)\right)
\]

变量和实现映射：`E` 是原始 event，`S` 是 versioned logging schema；`Allowlist` 只选业务/诊断必需字段，`Redact` 再按字段类型删除、遮蔽、tokenize 或转成受控 reference。allowlist-first 比单纯 denylist/regex 更能防新 key、嵌套 payload 和 exception string 绕过。[2]

### 7.1 Sensitive-field registry

| 字段 | 默认处理 | 安全替代 |
| --- | --- | --- |
| access/refresh token、password、private key | 删除 | provider/key-version reference、auth result |
| Authorization/cookie/DB connection | 删除 | credential class、scope、allow/deny |
| prompt/image/audio/video/trajectory | 默认不记原文 | request ID、content hash、classification、受控 artifact ref |
| path/host/robot/user ID | scoped mask/tokenize | attempt-scoped pseudonym；必要时 threat-reviewed HMAC ref |
| stack trace/tool payload | schema filter + length cap | error class、owner、correlation ID |
| audit decision | 保留并防篡改 | subject/resource ref、policy revision、decision、reason |

OWASP Logging 明确列出 access token、password、encryption key 等通常不应直接记录；NIST AU-9 要求保护 audit 信息和 logging tools 不受未授权访问、修改与删除。[2][3]

### 7.2 为什么普通 hash 也可能不安全

- 低熵 user/robot/phone/order ID 可被字典枚举；
- 跨系统稳定 hash 会形成可关联 identifier；
- secret digest 会向攻击者提供验证 oracle；
- content hash 可能证明某个敏感样本存在。

若确需关联，优先使用 scoped、rotatable HMAC/pseudonym，并定义 key owner、scope、retention 和 re-identification 权限；这仍需 threat review，不是万能脱敏。

## 8. Robot Harness：局部 hook 可以讲，系统闭环不能讲

直接证据：

- `AgentDeps/runtime` 传递 request `access_token`、scope、robot 与 cancel context；registry 按 tool name/allowed robot scope 过滤。
- tool payload 写日志前，registry 把 `__access_token` 改为 `***`；dedup key 排除 token、request 和 robot metadata。
- semantic-navigation 使用命名 credential，并在缺失时失败；没有发现硬编码值被复制到本报告。
- history 压缩/移除 action-tool history，减少 runtime exposure，但不等于正式 privacy/retention policy。

安全表述：

> “Robot Harness 当前有 request scope 和针对 `__access_token` 的定点日志遮蔽，且 token 不进入 dedup hash。这证明一个具体 hook，不证明所有 header/cookie/nested payload、TTL/rotation/revoke、secret manager、RBAC 或 audit protection 已闭环。”

高风险边界：mask 只匹配特定 key；换成 `authorization`、`cookie`、nested `headers`、exception string 或二进制字段可能绕过。因此需要 versioned sensitive-field registry 和 nested property tests。

## 9. UWM、OpenPiVLA、OPD 与 WAM 证据边界

| 项目 | 已有 direct evidence | 仍缺/暴露面 |
| --- | --- | --- |
| UWM | launcher 未启用 shell xtrace；显式设置 runtime env | stdout 打印 run/log/checkpoint/internal path；无 secret manager/env allowlist/data-purpose/retention artifact |
| OpenPiVLA | formal plan 与 checkpoint state 保存训练参数 | `vars(args)` 全量序列化没有 generic redaction；path/data/model metadata 进入 artifact |
| OPD | partial run summary 保存 model/data/teacher paths | 无 sensitive schema、purpose/permission、retention、secret scan result |
| WAM | inventory 未发现 local runtime/config/log bundle | 无法评价 credential/IAM/logging；保持 unverified |

OpenPiVLA smoke 的 `private_data_deployed=false` 只描述该 smoke artifact，不证明 formal run 的数据授权。selected-file scan 未发现 secret-named hardcoded string literal 或 unmasked secret identifier 直接进入选定 log sink，但只覆盖八个文件；Git history、container layer、runtime env、tracker、checkpoint 和对象存储仍未检查。

## 10. 安全证据分层

| 层 | 检查对象 | 最小 artifact |
| --- | --- | --- |
| static | working tree、Git history、config、image/layer | scanner rule/revision、canary、findings location、false-negative boundary |
| runtime | env/process/volume/core dump/exception | injection method、lease/TTL、negative run、no-fallback result |
| logging | stdout/stderr、tool payload、tracker、audit sink | schema revision、redaction tests、no-canary scan、tamper protection |
| data | raw/derived dataset、sample/gallery/video | permission manifest、purpose/retention/export decision |
| artifact | checkpoint/package/processor/normalizer | sensitive scan、classification inheritance、publisher gate |
| incident | compromise/expiry/revoke/rotation | timeline、blast radius、revocation latency、recovery result |

只做 static scan 不能升级为“生产安全”；只有把运行时、权限、日志、数据、artifact 和 incident drill 连起来，才是可抗追问的证据。

## 11. Secure Job 伪代码

```python
def launch_secure_job(request, policy, secret_provider, log_schema):
    # 1. Validate subject/action/resource/purpose on every request; default deny.
    decision = policy.authorize(request.subject, request.action,
                                request.resource, request.context)
    assert decision.allowed

    # 2. Lease short-lived scoped references; never persist raw secret values.
    leases = secret_provider.lease(
        decision.secret_refs, ttl=request.max_runtime, scope=decision.scope
    )

    # 3. Log only schema-approved fields and protect the audit sink.
    logger = secure_logger(log_schema, sensitive_fields=decision.sensitive_fields)
    logger.audit(decision.without_secret_values())

    try:
        # 4. Execute with least-privilege data/model/checkpoint capabilities.
        return run_job(request, leases, logger, capabilities=decision.capabilities)
    finally:
        # 5. Revoke/zeroize, then scan all outputs for a synthetic canary.
        secret_provider.revoke(leases)
        zeroize_local_material(leases)
        assert no_secret_canary_in_outputs(request.attempt_id)
```

伪代码表达 authorize→lease→redact→run→revoke/zeroize→canary 的顺序；policy engine、workload identity、secret provider、secure logger、audit protection 和 scanner 必须由真实系统实现并留 artifact。

## 12. 验证矩阵

| Case | 注入/动作 | 通过条件 |
| --- | --- | --- |
| hardcoded | synthetic canary 写入 test fixture | scanner 阻断；报告不复制 value |
| CLI/process | canary 作为 CLI arg | 拒绝或改 secure injection；history/process list 无明文 |
| env/log | allowlisted/non-allowlisted env canary | resolver/log/exception/tracker/artifact 无 raw canary |
| nested payload | nested header/body/cookie 放 canary | structured redactor 删除；fallback/length cap 不绕过 |
| expired/revoked | 过期或中途撤销 lease | fail closed、无 static fallback、audit reason 完整 |
| over-privilege | train job 删除 raw data/覆盖 final | deny；resource 不变；audit 记录 |
| wrong purpose | eval-only data 用于 train/export | deny；purpose/policy revision 可解释 |
| audit tamper | 非授权主体改删 log | 阻断或告警；audit evidence 可验证 |
| incident rotation | 模拟 credential compromise | 撤销/轮换/刷新/重启语义和 blast radius 可量化 |

验收指标可以报告 detection coverage、false positive/negative、redaction escape count、revocation latency、denied-action count、audit integrity result；不能只写“扫描通过”。

## 13. Trade-off、bad case 与追问

### 13.1 Trade-off

- 短期 credential 降低 blast radius，但要求 renewal/expiry 与长训练 checkpoint/retry 协调。
- allowlist 日志更安全，却可能减少 debug 信息；用 correlation ID + 受控 artifact escalation 补偿。
- 数据权限拆分增加运维成本，但能阻止 train/eval/publish 角色越权。
- audit 保留越久越利于调查，也增加隐私和攻击面；需要 retention/minimization。
- generic redaction 更稳健，但过度 mask 会破坏诊断；schema version 与 sampled review 要并行。

### 13.2 高概率 bad case

1. token 写在 CLI、shell history、Docker ENV/ARG 或配置文件。
2. Kubernetes Secret 只做 base64，未开 at-rest encryption/RBAC。
3. 为复现 dump 全部 env、args、tool payload 和 stack trace。
4. 一个共享 token 同时拥有 dataset read、checkpoint delete 和 final publish。
5. 只 mask `token` key，漏掉 nested header/cookie/connection string。
6. 路径可访问就默认可训练/可展示，忽略 license/consent/purpose。
7. scanner 零告警就宣称全仓、历史、runtime 和 artifact 无 secret。
8. audit log 可被同一 train job 改删，事故后无法取证。

### 13.3 面试追问

1. env var 与 Kubernetes Secret 为什么都不等于完整 secret management？
2. 长训练中 token 过期或轮换怎么办？
3. train/eval/publisher 为什么要不同 identity？
4. 怎样保证 dataset permission 传递到 checkpoint 和 failure video？
5. allowlist-first 为什么比 regex denylist 更稳？
6. 为什么普通 hash 仍可能泄露或关联敏感 ID？
7. Robot Harness 当前 mask 能被哪些 nested payload 绕过？
8. 怎样证明撤销、越权拒绝和 audit protection 真正工作？

## 14. 结论与下一步

可靠安全合同把 secret、authorization、data permission、logging 和 audit 放在同一链路：短期 scoped secret 只在运行时出现；每请求按 subject/action/resource/purpose 默认拒绝；train/eval/Agent/publisher capability 分离；日志先 allowlist 再结构化 redaction；audit sink 防篡改；最后用 canary、expiry/revoke、over-privilege、wrong-purpose 和 incident rotation 证明。

当前 Robot Harness 能证明一个具体 token-mask/scope hook，UWM/OpenPiVLA/OPD 能证明真实 args/path/summary exposure；但统一 secret manager、IAM、data governance、generic redaction、audit protection 和全链路 drill 仍缺。因此本节点保持 `WARN`，题卡保持 `unseen`。下一步可口述 `VLA-ENG-020`，或补 nested-redaction/expired-token/permission-deny artifact；`VLA-ENG-021` 继续后置。

## References

1. [ENG-020 Source Freeze](../sources/vol_05_eng020_secret_permission_logging_source_freeze.html)：官方 revision/SHA、本地 selected-file scan 与真实性边界。
2. OWASP, [Secrets Management](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Secrets_Management_Cheat_Sheet.md)、[Logging](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Logging_Cheat_Sheet.md) 与 [Authorization](https://github.com/OWASP/CheatSheetSeries/blob/ae0b3f22f5b24381455f742af9b5fa84063ad770/cheatsheets/Authorization_Cheat_Sheet.md)。
3. Kubernetes, [Secrets](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/configuration/secret.md) 与 [Good Practices](https://github.com/kubernetes/website/blob/5e1d1bde0ca03efe09608d59c573d6ec87052c24/content/en/docs/concepts/security/secrets-good-practices.md)。
4. NIST, [SP 800-53 Rev.5 OSCAL](https://github.com/usnistgov/oscal-content/blob/78650f02ad9321bb7b817846f8fbd4f2bcd620de/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json)：AC-3、AC-6、AU-9、IA-5。
5. Pydantic, [pydantic-settings 2.14.1](https://github.com/pydantic/pydantic-settings/blob/1d0ea26f9e04ec9e20767d70e4508bb33c8708e7/docs/index.md)：debug source secret warning。
6. 本仓库，[Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html)、[OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)、[OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html)、[UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [ENG-019 Config Resolution](vol_05_engineering_eval_eng019.html)。
