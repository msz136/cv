# VOL 05 Engineering / Evaluation：ENG-021 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-17  
> 覆盖范围：`VLA-ENG-021`  
> 难度：L2 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[ENG-021 Model / Processor / Normalizer Packaging](../knowledge/vol_05_engineering_eval_eng021.html)；来源边界见 [Source Freeze](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)。当前项目只有 processor/collator、recipe、normalizer/load metadata 与远端 path 证据，不能声称 immutable bundle、formal binary、processor/norm hash binding 或 round-trip 已闭环。

## Model、Processor、Normalizer 打包与兼容性

<details class="qa">
<summary><span class="lv lv-l2">L2</span> <span class="freq">P0</span> <b>VLA-ENG-021</b> · VLA 模型、processor、normalizer 和 checkpoint 如何打包并验证版本兼容？</summary>

**面试意图**：判断你能否把“模型能加载”拆成 config/weights、processor、action schema、normalizer、transform、runtime 和闭环 smoke，并区分官方加载语义与本地项目证据。

**30 秒回答**：bundle 固定 model/processor/action schema/normalizer/transform/lineage 的 revision+SHA；strict 查 key/shape/dtype，做 fixed-batch 与 action round-trip。safetensors 只管 tensor。

**机制展开（约 2 分钟）**：manifest 绑定 model config/权重、processor、(H,D)/axis/unit、normalizer、transforms、runtime；revision 固定 commit，strict load 不用 ignore_mismatched_sizes 掩错。校验 key、stats/transform SHA，跑 fixed-batch diff、denorm/parser/controller round-trip。OpenPiVLA 只有 processor/collator、recipe、远端 path；UWM 有 norm metadata，OPD 有 final-only manifest，不能说 bundle-verified。

**诊断 / 证据**：保存 bundle/model/processor/config/weight-shard/normalizer/transform/runtime 的 SHA、resolved commit、model type、dtype、expected key set、missing/unexpected/mismatched report、action schema、fixed batch、round-trip tolerance 和 rollback pointer。负测删除 processor、混用 model/processor revision、缺 shard、norm stats 漂移、H/D/axis/unit/frame 错、BF16/backend 变化；每项应 fail closed 或有显式 compatibility verdict。

**项目挂钩**：OpenPiVLA `formal_train.py` 有 processor/collator/chat-template，`data.py`/`recipes.py` 有 action formatter 与三类 recipe，DEPLOYMENT 记录远端 checkpoint/path；UWM artifact gate 有 normalizer JSON、load report、effective config；OPD 有 final-only/no-optimizer-state manifest。它们证明代码入口和暴露面，不证明本地 checkpoint binary、processor/norm hash binding、固定 batch diff 或 action/controller round-trip。

**追问树**：`from_pretrained` 能加载为什么还会部署失败？safetensors 解决什么、没解决什么？为什么 model/processor/normalizer 要分别 hash？Hub `main` 与 commit revision 如何取舍？如何证明 train/serve transform 顺序一致？`(B,15,72)` 与 `(B,16,72)` 如何区分 horizon/padding/semantics？strict load 和研究迁移的 partial load 如何分开？

**易错点**：只上传 `model.safetensors`；processor 跟随 `main`；复制别的 run 的 normalizer；用 `ignore_mismatched_sizes` 掩错；只对比 H/D 不检查 axis/unit/frame；把 OpenPI `32×50` 当通用规格；把远端 path/report 当本地 checkpoint 验证。

**危险答案**：说“能 `from_pretrained` 就能部署”“safetensors 代表完整安全 bundle”“normalizer 文件名相同所以匹配”“shape 对了语义就对”或“report 里有 checkpoint path 就是我验证过的权重”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [ENG-021 知识页](../knowledge/vol_05_engineering_eval_eng021.html)：immutable bundle、revision、processor/normalizer/action schema、compatibility matrix 与项目边界。
2. [ENG-021 Source Freeze](../sources/vol_05_eng021_model_processor_normalizer_packaging_source_freeze.html)：Transformers/Hub/safetensors/OpenPI pinned source 与本地证据 SHA。
3. [ENG-004..006 Artifact Gate](../sources/vol_05_local_artifact_gate_eng004_006.html)：normalizer、load report、缺 checkpoint binary 与 lineage gate。
4. [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html)：processor/collator、recipe、representation conflict 与远端 formal artifact 边界。
5. [UWM](../evidence/projects/uwm_libero_claim_evidence_inventory.html) 与 [OPD](../evidence/projects/opd_claim_evidence_inventory.html) inventories：normalizer/load metadata、final-only/no-optimizer-state 与未闭合 ownership/lineage。
