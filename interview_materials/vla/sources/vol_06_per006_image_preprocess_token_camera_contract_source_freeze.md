# VOL 06 PER-006 Source Freeze：Image Preprocess、Patch Token 与 Camera Identity Contract

> 状态：`source_frozen / VLA-PER-006 / upstream_checked / local_double_resize_risk / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-19  
> 证据截止：2026-07-19  
> 本页冻结 raw image 到 Qwen3-VL visual token 的 transform、shape、metadata 与本地调用边界；下游 knowledge/card 已同步且题卡保持 unseen；不把 preprocessing 配置写成模型效果或个人创新。

## 问题（Question）

一张机器人相机图像从磁盘/PIL 进入 VLM 时，`resize/crop/letterbox`、颜色与数值范围、patch/grid/token、camera identity 和坐标逆变换分别在哪里发生？本地 OpenPiVLA 与 OPD 是否真的使用同一条 preprocessing 路径？

## 1. 结论先行

1. ViT v2 只支持“Transformer 可直接处理 image-patch sequence”的基础范式；Qwen3-VL 的具体 resize、grid、merge 和 token 数必须回到官方 processor/model code 与具体 checkpoint 工件。
2. `Qwen/Qwen3-VL-8B-Instruct@0c351d...` 的 `preprocessor_config.json` 声明 `patch_size=16`、`temporal_patch_size=2`、`merge_size=2`、`image_mean=image_std=[0.5,0.5,0.5]`、`shortest_edge=65536`、`longest_edge=16777216`。
3. Qwen 官方 `qwen-vl-utils 0.0.14` 的 `process_vision_info` 默认 `image_patch_size=14`；Qwen3-VL 官方 README 明确示例传 `image_patch_size=16`，并在工具已完成 resize 后向 processor 传 `do_resize=False`。
4. OPD 的 `expert_sft.py` 与 raw-holdout eval 都调用 `process_vision_info(messages)`，没有传16，随后调用 processor 时也没有 `do_resize=False`；静态调用链因此是 factor 28 的工具 resize，再进入 factor 32 的 Qwen3 processor resize。当前没有 matched run 证明其性能影响，但 contract mismatch 直接存在。
5. OpenPiVLA formal path 与 dry-run path 不相同：formal MindCube 分支把原始 RGB PIL 交给 `AutoProcessor` 一次，DROID action 分支当前 `images=[]`；另一个 public-data dry-run adapter 则先把图像强制拉伸到 `224×224`。dry-run 行为不能替 formal Qwen 图像训练补证。
6. 冻结的 Qwen official path 使用保持宽高比的 smart resize，没有 crop/letterbox；因此不能凭通用视觉经验假定 padding offset 或 crop origin。本地也未发现逐样本 `original_size/resized_size/grid/camera_id/frame/timestamp` manifest。

## 2. Primary / official source ledger

SHA-256 对访问到的 UTF-8 文本计算；Git blob/hash、release tag 与模型 revision 分开记录。来源只支持其所在层，不能把上游实现或 model card 归为个人贡献。

| 来源 | 类型 / revision | SHA-256 | 支持的事实 | 不能支持 |
| --- | --- | --- | --- | --- |
| [Vision Transformer](https://arxiv.org/abs/2010.11929v2) | primary paper；arXiv API v2，读取 2026-07-19 | `A6D2B7F1AC2C6F8C3483015E7AD02C2031B01336930D6D993C218A0BEC42F719` | pure Transformer 可直接处理 image-patch sequence 的基础范式 | Qwen3-VL 的具体 patch、resize、merge、normalization 或项目效果 |
| [Qwen3-VL README](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/README.md) | official repo；commit `96588727...`；Apache-2.0 | `FC21106258C51E0B91A652EEF12F5925BECB146EA8B8C79A4251AC2E89A2F1AC` | Qwen3-VL processor 用法、`size` 与 pixel-budget 语义、Qwen3 `image_patch_size=16`、避免重复 resize 的示例 | 本地 checkpoint 的 processor config 或 OPD/OpenPiVLA 已按示例调用 |
| [qwen-vl-utils pyproject](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/qwen-vl-utils/pyproject.toml) | official package metadata；version `0.0.14`；Apache-2.0 | `C931C92AF0714107B2EC3B2DB667BD899BCB7B64E16310A8D78AB14C7196B22B` | 与本地 pip inventory 的 package version 对齐 | wheel 内容、运行环境或调用正确性自动一致 |
| [qwen-vl-utils vision_process.py](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/qwen-vl-utils/src/qwen_vl_utils/vision_process.py) | official code；同一 commit | `46C056F52F8ACD2597A46377868F0BF7436DD893EE2CA53CC3C4CB59EBAE7BF0` | `smart_resize`、factor/pixel band、RGB conversion、直接 PIL resize、`process_vision_info` 默认 patch size 14 | crop/letterbox、插值显式 pin、坐标逆变换或 camera metadata |
| [Transformers Qwen2VLImageProcessor](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py) | official code；`v4.57.1` / commit `8cb5963c...`；Apache-2.0 | `7820A0FCCA107E75605E08D9B774285CA2B0316F857BC0225C779794705ECF4F` | model artifact 指定的 size/patch/merge、bicubic resize、rescale/normalize、`pixel_values` 与 `image_grid_thw` 生成 | 任意本地 checkpoint 都继承相同 processor artifact |
| [Transformers Qwen2VLImageProcessorFast](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen2_vl/image_processing_qwen2_vl_fast.py) | official fast processor；同一 release | `09BFA9B17DF7C3F0C6159BC34008EE50F21D2472CD5BAE7E5C21BA1CA13A423C` | 复用 slow `smart_resize`；显式 bicubic/rescale/normalize；fast patchify 与 grid 输出；与 model artifact 的 processor type 对齐 | 本地实际加载的 class、backend 和 kwargs 已被 run bundle 记录 |
| [Transformers Qwen3VLProcessor](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/processing_qwen3_vl.py) | official code；同一 release | `EFD8D64AAF608AAD1FFB3E6D503D6A99E5227D007DF95C1D9FA905D998CDA4A9` | image placeholder 数由 `image_grid_thw.prod()/merge_size²` 决定 | camera identity、坐标语义或 action alignment |
| [Transformers Qwen3VL modeling](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/modeling_qwen3_vl.py) | official code；同一 release | `DD63ED3B124232735B3DCA1BFA28F9D6B0D3F7182AFCB75DDE8F3E724B2B22DA` | patch embedding kernel、spatial merge 与 image-feature/token count 一致性检查 | 本地图像内容或 camera ordering 正确 |
| [Qwen3VL configuration](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/configuration_qwen3_vl.py) | official code；同一 release | `177FD0A4DC1B08307C08CA72CF26B8D7DC028AB6AB5975BF650FC14AB8132A83` | default patch 16、spatial merge 2、temporal patch 2 | 具体 checkpoint 一定未覆盖 defaults |
| [Qwen3-VL-8B preprocessor config](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/preprocessor_config.json) | official model artifact；revision `0c351dd0...`；Apache-2.0 | `27225450AC9C6529872EE1924FCB0962FF5634834F817040F444118116F4E516` | checkpoint-specific size、patch、merge、mean/std、processor type | 本地复制/checkpoint 的 config hash 相同 |
| [Qwen3-VL-8B config](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/config.json) | official model artifact；同一 revision | `5CD452860DC1E9C29DD71CC3CEF7F39B338B7A40793F7A260655C2D3568F3661` | vision patch16、merge2、temporal2 与 token IDs | 本地 processor/model pair 已绑定或 rollout 可复现 |

## 3. 冻结的上游输入合同

### 3.1 Transform chain

冻结代码中的 image-only path 是：

```text
# qwen-vl-utils path
image path / URL / base64 / PIL
  -> RGB conversion
  -> smart_resize(aspect ratio approximately preserved,
                  H' and W' divisible by patch_size * merge_size)
  -> direct PIL resize
  -> Qwen image processor(do_resize=False in the official two-stage example)
  -> rescale + normalize
  -> patchify + image_grid_thw
  -> spatial merge + image placeholder tokens
```

没有 crop、letterbox 或 padding-offset 分支。`resized_height/resized_width` 仍会被 round 到 factor 的倍数，不等于无条件采用请求尺寸。

对 Qwen3-VL-8B：

\[
F=p\,m=16\times2=32
\]

其中 \(p\) 是 spatial patch size，\(m\) 是 spatial merge size，\(F\) 是 resize divisibility factor。代码映射：`qwen-vl-utils.fetch_image(image_patch_size=16)` 与 checkpoint `preprocessor_config.json`。

### 3.2 Patch / grid / token

静态图像经过 temporal duplication 后，`image_grid_thw` 可写作 \((T_g,H_g,W_g)\)，image placeholder 数为：

\[
N_{\mathrm{img}}=\frac{T_gH_gW_g}{m^2}
\]

其中 \(H_g=H'/p\)、\(W_g=W'/p\)、静态图像通常 \(T_g=1\)。对 \(p=16,m=2\)，若 \(H',W'\) 都是32的倍数，则：

\[
N_{\mathrm{img}}=\frac{H'W'}{1024}.
\]

直觉：每个 `16×16` patch 先进入视觉 encoder，`2×2` spatial merge 后每四个 spatial patches 对应一个语言侧 image placeholder。实现映射：Transformers image processor 生成 `pixel_values/image_grid_thw`，Qwen3 processor 按 `prod(grid)/merge²` 展开 `<|image_pad|>`。

### 3.3 Pixel value 与 normalization

`Qwen3-VL-8B-Instruct@0c351d...` 的 processor artifact 声明 RGB mean/std 都为0.5；Transformers class 仍支持 `do_rescale/do_normalize`。因此：

- 输入若是0–255，应允许 processor rescale；
- 输入若已是0–1，重复 `do_rescale` 会形成错误量级，官方 image processor 文档要求此时关闭；
- 不能只记录“用了 AutoProcessor”，必须同时冻结本地 `preprocessor_config.json`、调用 kwargs 与实际 input range。

## 4. Local evidence audit

| 路径 / SHA | 直接事实 | 风险边界 |
| --- | --- | --- |
| `C:\Users\mousongzhe\muxi\metax_pkgs\pip-list.json` / `2A730543...` | local environment 记录 `transformers=4.57.1`、`qwen-vl-utils=0.0.14`、`Pillow=10.4.0` | 版本对齐不证明调用 kwargs 正确；remote run image/config hash 未闭合 |
| `C:\Users\mousongzhe\muxi\point\expert_sft.py` / `2A1D37F...` | 每个 image message 写 `min_pixels=max_pixels=50176`；调用 `process_vision_info(full_messages)`；随后 processor 编码，未传 `image_patch_size=16` 或 `do_resize=False` | 形成 factor28→factor32 双阶段 resize 风险；没有 per-sample grid/transform log 或 matched ablation |
| `C:\Users\mousongzhe\muxi\point\eval_qwen_vl_raw_holdout.py` / `29574ADC...` | eval 同样用 `min=max=50176`、默认 `process_vision_info` 与 processor；训练/评估调用形态一致 | “一致”不等于正确；point/box protocol 仍需原图↔处理图 round-trip |
| `C:\Users\mousongzhe\Project\openpivla_deployment\repro_train\openpi_src\src\openpi\training\vla_qwen3_repro\formal_train.py` / `51B67D3E...` | formal defaults `min=max=200704`；MindCube 将原始 RGB PIL 交给 processor；DROID action dataset 返回 `images=[]` | 不能把 MindCube 图像 path 证明为 DROID/VLA image training；未记录 camera identity 或 output grid manifest |
| `...\vla_qwen3_repro\data.py` / `32C6AA76...` | public-data dry-run `_read_image` 直接 `resize((224,224))`、除255并输出 CHW；`VLAQwen3ReproCollator` 是 dry-run adapter | 强制方形会改变非方图像几何；该路径不是 formal Qwen processor path，不能混为一谈 |

### 4.1 OPD double-resize deterministic probe

probe 直接复刻 frozen `smart_resize` 的整数舍入，不加载模型、不声称已复现实验。

| 原始 H×W | qwen-vl-utils stage（factor28，min=max50176） | Qwen3 processor stage（factor32，同一 pixel budget） | 最终 image tokens |
| --- | ---: | ---: | ---: |
| `480×640` | `168×252` | `192×288` | 54 |
| `720×1280` | `168×280` | `192×320` | 60 |
| `1000×1000` | `224×224` | `224×224` | 49 |

`min_pixels=max_pixels` 不保证最终像素积严格等于该值：divisibility 与 ceil/floor rounding 可以让第一阶段低于、第二阶段高于目标。当前结论是 shape/token contract 可变且未归档，不是“已证明性能下降”。

### 4.2 OpenPiVLA formal comparison

formal MindCube defaults `min=max=200704` 且只由 Qwen processor resize 一次。相同原图的 source-derived probe：

| 原始 H×W | formal processed H×W（factor32） | image tokens |
| --- | ---: | ---: |
| `480×640` | `384×512` | 192 |
| `720×1280` | `320×576` | 180 |
| `1000×1000` | `448×448` | 196 |

这只说明两个本地入口的 pixel/token budget 不同；不能比较模型质量，因为 dataset、task、checkpoint、训练目标和运行 lineage 都不同。

## 5. Camera identity、order 与坐标 round-trip

image token 本身不携带“workspace camera / wrist camera / front-left camera”的机器人语义。最小输入 manifest 应记录：

| 字段 | 必须回答 | 当前本地状态 |
| --- | --- | --- |
| `sample_id / image_id` | 哪个样本、哪张原图？ | OPD 有 path；formal MindCube 有 row image list；统一 immutable manifest 未见 |
| `camera_id / frame_id` | 这张图属于哪台相机、哪个 optical frame？ | formal/OPD message 仅靠 image order/path；未见显式 camera identity |
| `capture_timestamp` | 观测与 state/action 的时间关系？ | 本切片未找到 |
| `original_h,w` | 坐标输出相对哪张图？ | processor 可读取，但 local run bundle 未归档 |
| `resize/crop/pad` | scale、crop origin、padding offset、interpolation？ | official path 为 smart resize；local 未归档逐样本 transform；crop/letterbox 不应假定 |
| `processed_h,w / image_grid_thw` | 实际 patch grid 与 token 数？ | processor runtime 可返回；local result bundle 未见保存 |
| `pixel_range / mean / std` | 0–255 还是0–1，是否重复 rescale？ | checkpoint config 可查；dry-run adapter 已先/255，与 formal path分离 |
| `inverse mapping` | point/box 如何回到原图/3D/controller frame？ | PER-001/002 规定 gate；本地 round-trip artifact 缺失 |

多图输入还必须证明 message placeholder 顺序、flatten 后 image 顺序和 camera metadata 一一对应。formal collator 将 batch 内 image list 依次 flatten；代码没有显式 camera key，因此“第几个 image token”不能自动解释为某个机器人相机。

## 6. Cross-volume 去重边界

| 已有页面 | 已覆盖 | PER-006 新增边界 |
| --- | --- | --- |
| VOL 01 Transformer / representation | attention、patch/token 基础直觉 | 具体 Qwen processor transform、grid/token 与 pixel contract |
| VOL 03 VLA Architecture | image/language/action 接口、mask、action head | raw image 到 visual placeholders 的前处理与 camera identity |
| PER-001 Grounding | point/box/text 与 coordinate inverse | 坐标 inverse 所依赖的原图→处理图 manifest |
| PER-003 Multi-view / Temporal | per-view camera/frame/time/presence schema | 单图 processor 不会自动提供 camera semantic；flatten/order gate |
| VOL 05 Engineering/Eval | dataset/manifest/reproducibility | perception-specific transform/grid/token fields与 deterministic probe |

PER-006 knowledge 已按该边界讲清“如何解释和审计”，没有重复 Transformers/ViT 通用教学，也没有把本页的静态 mismatch 升级为 causal performance conclusion。

## 7. Claim boundary 与验收门

当前可以说：

- “我审计了 Qwen3-VL 图像输入链，区分 qwen-vl-utils factor28 默认与 Qwen3 factor32，并定位本地 OPD 未传 patch16/未关闭二次 resize 的 shape/token contract 风险。”
- “OpenPiVLA formal MindCube、DROID action 与 dry-run adapter 是三条不同 image lineage；当前 DROID formal action 分支没有图像。”

当前不能说：

- “已修复 preprocessing 并提升 grounding/VLA 成功率。”
- “50176 pixels 一定产生固定49个 visual tokens。”
- “模型天然知道 camera identity，或 resize 不影响 point/box 坐标。”
- “OpenPiVLA 已完成 image-conditioned DROID VLA training。”

升级前至少需要：

1. pin 本地 model/processor/qwen-vl-utils revision 与 config hash；
2. 对多种宽高比保存 original/resized/grid/token/inverse manifest；
3. 统一 `image_patch_size=16` 与 `do_resize` policy，做 train/eval parity test；
4. point/box sentinel 从原图→processor→parser→原图 round-trip；
5. 多相机样本保存 camera/frame/timestamp/order；
6. matched preprocessing A/B 后才能讨论 metric 或 closed-loop 影响。

## 8. 下一 bounded slice

`VLA-PER-007..009` source/knowledge/card已同步且保持`unseen`。下一轮只做PER-010 metric/parser source freeze，不生成knowledge/card或修改其他mastery。

## 参考入口（References）

1. [VOL 06 Coverage-Gap Audit](vol_06_perception_grounding_navigation_coverage_gap_audit.md)
2. [VOL 06 Phase 0 Question List](../questions/vol_06_perception_grounding_navigation.question_list.md)
3. [PER-001 Grounding Source Freeze](vol_06_per001_grounding_coordinate_source_freeze.md)
4. [PER-003 Multi-view / Temporal Source Freeze](vol_06_per003_multiview_temporal_source_freeze.md)
5. [OpenPiVLA JSON/CE Shape Contract Gate](openpivla_formal_json_ce_shape_contract_artifact_gate.md)
6. [OPD Claim–Evidence Inventory](../evidence/projects/opd_claim_evidence_inventory.md)
