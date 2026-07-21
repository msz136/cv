# VOL 05 Engineering / Evaluation：EVAL-021 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-EVAL-021`  
> 难度：L3 1题  
> 优先级：P1 1题  
> 练习状态：`unseen`  
> 前置知识：[EVAL-021 Deployment Drift / Data Shift / Continuous Monitoring](../knowledge/vol_05_engineering_eval_eval021_deployment_drift_data_shift_continuous_monitoring.html)；来源边界见[Source Freeze](../sources/vol_05_eval021_deployment_drift_data_shift_continuous_monitoring_source_freeze.html)。本题不把distribution test、protocol变化或离线指标直接升级为线上性能退化或自动重训依据。

## Deployment Drift、Data Shift 与持续监控

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-EVAL-021</b> · VLA部署后怎样检测data/concept drift并建立持续监控？</summary>

**面试意图**：判断你能否区分data、concept、protocol、bundle、system、behavior与scorer drift，设计reference/window/slice、统计检测、delayed outcome与安全响应，并避免“告警即重训”。

**30 秒回答**：先锁基准/当前窗口、episode单位、完整bundle版本和关键slice；监控数据合同、覆盖、延迟、策略行为及延迟到达的成功/安全结果。MMD/JS/ADWIN只发变化信号，需以同协议结果验证影响并定位原因，再经回归和canary决定回滚、校准或重训。

**机制展开（约 2 分钟）**：输入分布`P(X)`变是data drift，条件映射`P(Y|X)`变才是concept drift；协议、bundle、系统、scorer另分。基准保留冻结anchor、季节对照和并发control，当前流按episode/task/site分层。L∞/JS查比例，MMD查embedding，ADWIN查标量流；都需效应、样本量、连续窗口和告警预算。用ID补连延迟标签，报告覆盖、延迟与slice风险差；无标签标`impact_pending`。安全critical可限权/回滚，重训仍过fresh audit和canary。

**诊断 / 证据**：monitor registry、reference/current manifests、lineage/context、schema/missing/timestamp、task/site/robot/camera/language support、encoder/kernel/threshold、latency/queue/resource、action saturation/chunk/tool depth/fallback、label coverage/delay、per-slice success/safety/override、alert persistence/budget、incident join、response/update/reference-promotion ledger与checksums。

**项目挂钩**：OPD的pool/format表只适合作离线reference候选；Harness的safety/tool summary不是live SLO；OpenPiVLA/WAM无timestamped deployment stream。UWM `232/250→186/250`改变reset/init协议，只说明distribution/protocol sensitivity，不能称时间drift或模型退化。

**追问树**：data与concept drift区别？reference选训练集还是最近窗口？rolling baseline风险？MMD显著代表什么？TFDV skew/drift区别？ADWIN监控什么？多feature如何控误报？标签晚到怎么办？proxy与outcome怎样join？何时立即rollback？何时recalibrate/retrain？UWM差值能否叫drift？

**易错点**：drift=degradation；只看overall；rolling baseline吞慢性退化；混新旧lineage/scorer；每step当独立样本；照搬0.01阈值；p-value paging；忽略missing labels；proxy当安全；告警即重训；current自动升reference；protocol shift拼历史曲线；把离线summary写成线上monitor。

**危险答案**：说“MMD高说明模型坏了”“concept drift不需要标签”“最近一周自动做baseline即可”“告警后自动抓数据重训并全量发布”“UWM下降18.4pp证明模型发生deployment drift”，或编造五项目线上SLO、drift alarm与auto-retrain。

**来源**：[1][2][3][4][5][6][7][8]　**练习状态**：unseen

</details>

## 参考来源

1. [EVAL-021 知识页](../knowledge/vol_05_engineering_eval_eval021_deployment_drift_data_shift_continuous_monitoring.html)。
2. [EVAL-021 Source Freeze](../sources/vol_05_eval021_deployment_drift_data_shift_continuous_monitoring_source_freeze.html)。
3. [NIST AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1)。
4. [TensorFlow Data Validation guide](https://www.tensorflow.org/tfx/data_validation/get_started)。
5. [Gretton et al., MMD two-sample test](https://www.jmlr.org/papers/v13/gretton12a.html)。
6. [River ADWIN](https://github.com/online-ml/river/blob/5eed38dfd25183049de733b3016ff1edb84266e5/river/drift/adwin.py)。
7. [OPD / UWM inventories](../evidence/evidence_manifest.html)。
8. [Robot Harness / OpenPiVLA / WAM inventories](../evidence/evidence_manifest.html)。
