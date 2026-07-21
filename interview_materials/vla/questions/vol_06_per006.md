# VOL 06 Perception / Grounding / Navigation：PER-006 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-19  
> 覆盖范围：`VLA-PER-006`  
> 难度：L3 1 题  
> 优先级：P0 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-006 Image Preprocess / Token / Camera Knowledge](../knowledge/vol_06_per006_image_preprocess_token_camera_contract.html)；来源边界见 [PER-006 Source Freeze](../sources/vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html)。

## 图像预处理、视觉 token 与 camera identity 合同

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P0</span> <b>VLA-PER-006</b> · 图像进入 Qwen3-VL 前，如何审计 preprocess、patch token、坐标逆变换与 camera identity？</summary>

**面试意图**：判断你能否把“调用 AutoProcessor”展开为可复算、可逆、可绑定相机语义的输入合同，并把静态代码风险与实测性能因果分开。

**30 秒回答**：先分原图、处理图、patch grid、image token四层，冻结resize、数值范围、归一化与坐标逆变换。Qwen3-VL的factor为16×2=32，token数由grid/merge决定；相机顺序另存manifest。OPD的factor28→32只是静态风险，无matched A/B不称性能根因。

**机制展开（约 2 分钟）**：逐样本记录原图尺寸、resize/crop/pad、处理尺寸、pixel range、mean/std、`image_grid_thw`、placeholder 顺序与 camera/frame/time。Qwen3 静态图满足 $N_{img}=H'W'/1024$，但 pixel budget 相等不代表固定 shape。point/box 必须按实际 direct resize、crop 或 letterbox 参数逆映射。OPD 先用 utils 默认 factor28、再进 factor32 processor；应先统一 resize ownership、做 grid/token 与坐标 round-trip，再固定 train/eval 跑 matched A/B。

**诊断 / 证据**：保存 `sample_id/image_id/camera_id/frame_id/timestamp`、原始与处理宽高、transform revision、scale/crop/pad、input range、processor/config hash、`image_grid_thw`、token count、placeholder/image index 和 valid mask。用多宽高比 sentinel 复算 $N_{img}=T_gH_gW_g/m^2$，再做 point/box 原图→处理图→原图 round-trip。只有 shape/token trace 能证明合同差异；要归因指标变化，还需相同数据、checkpoint、seed、budget、train/eval policy 的单变量 A/B。

**项目挂钩**：OPD 可安全讲“冻结版本后定位 factor28→32 双阶段 resize 风险，并设计 manifest、round-trip 与 matched A/B gate”，不能说已修复或带来 uplift。OpenPiVLA 要分 formal MindCube 原始 PIL、formal DROID action 的 `images=[]`、dry-run square-224 三条 lineage；不能用 dry-run 或 MindCube 为 image-conditioned DROID 补证。WAM/UWM/Harness 只连接 camera/schema 设计，不声称共享 Qwen processor 或已验证视觉导航。

**追问树**：为什么 `min_pixels=max_pixels` 仍不是固定分辨率？`image_grid_thw` 如何变成 placeholder 数？direct resize、crop、letterbox 的 inverse 各缺什么参数？多图顺序 shape 正确为何仍可能语义错位？pixel range 重复 rescale 会怎样？如何设计 double-resize 的 matched A/B？

**易错点**：把 pixel budget 当固定 shape；把 patch 数直接当 merge 后 token 数；默认 Qwen path 是 letterbox；只保存 `pixel_values` 不保存 inverse/camera manifest；把多图 list 顺序当 camera identity；把静态 mismatch 直接归因指标下降。

**危险答案**：说“AutoProcessor 会自动处理所有坐标和相机语义”“Qwen3 永远固定 224×224”“patch16 就是一行16个 token”“两次 resize 一定导致效果下降”或“OpenPiVLA 的 DROID 已由图像条件训练”。

**来源**：[1][2][3][4][5]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-006 Image Preprocess / Token / Camera Knowledge](../knowledge/vol_06_per006_image_preprocess_token_camera_contract.html)：四层表示、smart resize、patch/grid/token、坐标 inverse、camera manifest 与项目 truth boundary。
2. [PER-006 Image Preprocess / Token / Camera Source Freeze](../sources/vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html)：冻结 Qwen3-VL、Transformers、qwen-vl-utils 与本地 OPD/OpenPiVLA 调用链。
3. [Qwen3-VL frozen README](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/README.md) 与 [qwen-vl-utils vision_process.py](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/qwen-vl-utils/src/qwen_vl_utils/vision_process.py)。
4. [Transformers 4.57.1 Qwen3VLProcessor](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/processing_qwen3_vl.py) 与 [Qwen3-VL modeling](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/modeling_qwen3_vl.py)。
5. [Qwen3-VL-8B preprocessor artifact](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/preprocessor_config.json)。
