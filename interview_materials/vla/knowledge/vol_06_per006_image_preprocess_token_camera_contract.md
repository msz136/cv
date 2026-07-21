# VOL 06 Perception / Grounding / Navigation：Image Preprocess、Patch Token 与 Camera Identity（PER-006）

> 状态：`drafted / VLA-PER-006 / source_synced / card_synced / WARN`  
> 报告日期：2026-07-19  
> 证据截止：2026-07-19  
> 来源入口：[PER-006 Source Freeze](../sources/vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html)。  
> 题卡入口：[PER-006 Atomic Card](../questions/vol_06_per006.html)。  
> 前置知识：[PER-001 Grounding / Coordinate](vol_06_per001_grounding_coordinate.html)、[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)。

## 问题（Question）

一张机器人相机图像进入 Qwen3-VL 之前发生了什么？面试中如何从 resize/crop/letterbox、pixel range 与 normalization，一直讲到 patch grid、image tokens、camera identity 和 point/box 坐标逆变换？为什么本地 OPD 与 OpenPiVLA 不能只用一句“都调用 AutoProcessor”概括？

本页回答：

1. 原图、处理图、patch grid、image token 是哪四个坐标/表示空间？
2. Qwen3-VL 的 `patch_size=16`、`merge_size=2` 如何决定 factor32 和 token 数？
3. direct resize、crop、letterbox 的坐标映射有什么不同？
4. `min_pixels=max_pixels` 为什么仍不保证固定尺寸或固定 token 数？
5. camera identity、image order、frame 和 timestamp 为什么不由视觉 token 自动提供？
6. 如何解释 OPD double-resize 与 OpenPiVLA image lineage，而不把静态风险说成性能结论？

## 知识地图位置与前置依赖

```text
raw image + camera/frame/time metadata
  -> PER-006 preprocess / pixel / patch / token contract
  -> PER-001 point/box/text inverse mapping
  -> PER-002 2D-to-3D / calibration / TF
  -> PER-003 multi-view / temporal fusion
  -> PER-007 open-vocabulary grounding pipeline
```

PER-006 不重复 VOL 01 的 Transformer 基础，也不重复 VOL 03 的 VLA action head；它负责把“图像如何成为 visual tokens”变成可复算、可逆映射、可绑定 camera identity 的工程合同。

## 1. 30 秒直觉：图像不是一个 tensor 名字

面试中最容易犯的错是从“输入一张 RGB 图”直接跳到“模型输出 point/box/action”。中间至少有四层：

| 层 | 典型对象 | 必须知道 |
| --- | --- | --- |
| 原图空间 | `I_raw∈R^{H×W×3}` | camera/frame、timestamp、原始宽高、颜色/位深 |
| 处理图空间 | `I_proc∈R^{H'×W'×3}` | resize/crop/pad、插值、pixel range、mean/std |
| patch grid | `(T_g,H_g,W_g)` | patch size、temporal patch、grid 顺序 |
| 语言侧 image tokens | `N_img` 个 `<|image_pad|>` | spatial merge、placeholder 顺序、与图像数量一致性 |

如果只保存 `pixel_values`，却不保存 `original_size`、`processed_size`、`image_grid_thw`、camera identity 和 transform 参数，就无法回答：

- point/box 坐标到底相对哪张图；
- 多个 image placeholders 分别属于哪台相机；
- token 数为何随宽高比变化；
- 训练与评估是否真的使用同一条 processor path。

## 2. Transform chain：先画数据流，再谈模型

冻结的 Qwen3-VL image-only 官方路径可抽象为：

```text
path / URL / base64 / PIL
  -> decode + RGB
  -> smart_resize
  -> rescale + normalize
  -> temporal duplicate for a static image
  -> patchify
  -> image_grid_thw
  -> spatial merge
  -> image placeholder tokens
```

Qwen frozen `qwen-vl-utils` 代码使用保持宽高比的 smart resize 并直接调用 PIL resize；没有 crop、letterbox 或 padding-offset 分支。Qwen3 官方两阶段示例在 utils 已 resize 后给 processor 传 `do_resize=False`，避免重复 resize。

这不代表所有 VLM 都不使用 crop/letterbox；它只说明当前冻结的 Qwen path 不能被口述成 letterbox。工程回答必须以实际 processor/code revision 为准。

## 3. Smart resize：pixel budget 不是固定分辨率

### 3.1 三个约束

设原图为 \(H\times W\)，patch size 为 \(p\)，spatial merge 为 \(m\)，整除因子：

\[
F=p\,m.
\]

Qwen3-VL-8B 的 checkpoint contract 为 \(p=16,m=2\)，所以：

\[
F=16\times2=32.
\]

smart resize 尝试满足：

1. \(H'\bmod F=0,\;W'\bmod F=0\)；
2. \(H'W'\) 落在 `min_pixels/max_pixels` band；
3. 宽高比尽量接近原图。

变量映射：\(H',W'\) 是 processor 实际输入尺寸；\(F\) 对应 `patch_size*merge_size`；pixel band 来自 checkpoint processor config 或调用覆盖值。

### 3.2 为什么 min=max 也不精确

算法先把高宽 round 到 factor 倍数；若像素积过大，按 \(\sqrt{HW/P_{\max}}\) 缩小并 floor；若过小，按 \(\sqrt{P_{\min}/HW}\) 放大并 ceil。离散 factor 与 ceil/floor 意味着：

\[
P_{\min}=P_{\max}=P
\quad\not\Rightarrow\quad
H'W'=P.
\]

直觉：对某个宽高比，可能不存在同时满足“两个维度都是32倍数、保持近似宽高比、像素积刚好等于50176”的整数解。`min=max` 是一个强 pixel-budget 请求，不是 fixed `H'×W'`。

### 3.3 复杂度含义

视觉 token 数大致随处理后像素积增长；因此 pixel budget 同时影响：

- 细粒度 grounding 信息；
- `image_grid_thw` 与上下文长度；
- vision encoder 计算/显存；
- 文本可用 token budget与batch shape波动。

不能只说“分辨率越大越好”：还要说明目标物大小、宽高比、memory/latency 和训练评估一致性。

## 4. Patch、grid 与 image tokens

### 4.1 从处理图到 grid

对静态图像，Qwen processor 会为 temporal patch 做帧复制，最终通常得到 \(T_g=1\)。空间 grid 为：

\[
H_g=\frac{H'}{p},\qquad W_g=\frac{W'}{p}.
\]

`image_grid_thw=(T_g,H_g,W_g)` 不是原图尺寸；它描述 patchify 后的三维 grid。代码中 `pixel_values` 以 patch rows 组织，model 根据 grid 恢复位置与分组。

### 4.2 Spatial merge 后的 token 数

Qwen3 processor 展开语言侧 image placeholders 的公式是：

\[
N_{\mathrm{img}}
=
\frac{T_gH_gW_g}{m^2}.
\]

其中 \(m^2\) 表示每个 `m×m` spatial block 合并为一个语言侧 image token。对静态图、\(p=16,m=2\)：

\[
N_{\mathrm{img}}
=
\frac{H'W'}{16^2\cdot2^2}
=
\frac{H'W'}{1024}.
\]

例：\(H'=192,W'=288\)，则 \(N_{\mathrm{img}}=192\times288/1024=54\)。

实现映射：

```text
image processor -> pixel_values + image_grid_thw
Qwen3VLProcessor -> prod(image_grid_thw) / merge_size**2
chat text -> repeated <|image_pad|> placeholders
model -> checks placeholder count matches image features
```

因此“图像 token 数”不能用原始分辨率或一个固定常数猜测，必须读取实际 `image_grid_thw`。

## 5. Pixel range、rescale 与 normalization

冻结的 `Qwen/Qwen3-VL-8B-Instruct@0c351d...` processor artifact 声明：

\[
\mu=[0.5,0.5,0.5],\qquad \sigma=[0.5,0.5,0.5].
\]

若输入 \(x\in[0,255]\)，processor 先做 \(x_s=x/255\)，再：

\[
x_{\mathrm{norm}}
=
\frac{x_s-\mu}{\sigma}
=
2\frac{x}{255}-1.
\]

变量映射：`do_rescale` 控制除255，`do_normalize` 控制减 mean/除 std。若上游已输出0–1，却仍让 processor 再除255，数值会被压到约 \([0,1/255]\) 后再 normalize；这不是“小的数值差异”，而是 input contract 错误。

最小检查：

| 检查 | 正确问题 |
| --- | --- |
| dtype/range | uint8 0–255，还是 float 0–1？ |
| processor kwargs | `do_rescale/do_normalize/do_resize` 实际值是什么？ |
| config | mean/std、patch、merge、pixel band 来自哪个 revision？ |
| parity | train/eval 是否同 processor、同 kwargs、同 input range？ |

## 6. Direct resize、crop 与 letterbox 的坐标映射

PER-006 必须解释三种不同 transform；不能看到“输入尺寸一样”就认为坐标语义一样。

### 6.1 Direct resize

若原图 \((W,H)\) 直接缩放到 \((W',H')\)：

\[
x'=s_xx,\quad y'=s_yy,\qquad
s_x=\frac{W'}{W},\quad s_y=\frac{H'}{H}.
\]

逆映射：

\[
x=\frac{x'}{s_x},\qquad y=\frac{y'}{s_y}.
\]

若 \(s_x\ne s_y\)，形状会发生各向异性变形。Qwen smart resize试图近似保持宽高比，但整数 rounding 仍可能让比例略变；因此逆映射应使用实际 \(s_x,s_y\)，不能只存一个 scale。

### 6.2 Letterbox

若使用统一 scale \(s\) 后在左右/上下 padding \(p_x,p_y\)：

\[
x'=sx+p_x,\qquad y'=sy+p_y.
\]

逆映射：

\[
x=\frac{x'-p_x}{s},\qquad y=\frac{y'-p_y}{s}.
\]

不保存 padding offset 会让 point/box 系统性平移。当前冻结的 Qwen path没有 letterbox，因此不能人为补一个不存在的 padding inverse。

### 6.3 Crop + resize

若先从原图裁剪左上角 \((c_x,c_y)\)，再缩放：

\[
x'=s_x(x-c_x),\qquad y'=s_y(y-c_y).
\]

逆映射必须恢复 crop origin：

\[
x=\frac{x'}{s_x}+c_x,\qquad y=\frac{y'}{s_y}+c_y.
\]

box 应分别变换两个角点，再 clip/validate；不能只变 center 或只变 width/height。无论哪种 transform，都要记录原图尺寸、处理图尺寸、scale、crop、pad 和坐标 convention。

## 7. OPD double-resize：如何讲风险，不讲伪因果

### 7.1 静态调用链

本地 OPD `expert_sft.py` 与 raw-holdout eval 的调用形态是：

```text
message image + min_pixels=max_pixels=50176
  -> qwen_vl_utils.process_vision_info(messages)
     # omitted image_patch_size => default 14, factor 28
  -> processor(images=...)
     # omitted do_resize=False
     # Qwen3 artifact patch 16, merge 2 => factor 32
```

这是直接可见的 contract mismatch：第一阶段按 factor28，第二阶段按 factor32。它不自动等于“训练错了”或“指标下降”，因为还缺 matched preprocessing A/B。

### 7.2 Source-derived probe

| 原始 H×W | stage1 factor28 | stage2 factor32 | 最终 tokens |
| --- | ---: | ---: | ---: |
| `480×640` | `168×252` | `192×288` | 54 |
| `720×1280` | `168×280` | `192×320` | 60 |
| `1000×1000` | `224×224` | `224×224` | 49 |

面试安全表述：

> 我通过冻结版本与确定性 probe 定位了 factor28→factor32 的双阶段 resize 风险，并提出 train/eval parity、grid manifest 与 coordinate round-trip gate；当前没有 matched A/B，所以不把它说成已确认的性能根因。

### 7.3 修复验证顺序

正确顺序不是“改一行直接报提升”，而是：

1. pin `qwen-vl-utils`、Transformers、model/processor config；
2. Qwen3 path 显式传 `image_patch_size=16`；
3. 二选一：utils resize + processor `do_resize=False`，或只让 processor resize；
4. 保存多个 aspect ratio 的 original/resized/grid/token；
5. 运行 point/box sentinel round-trip；
6. 固定训练/评估同一 policy；
7. 最后才做 matched metric A/B。

## 8. OpenPiVLA：三条 image lineage 不能混

| 路径 | Image behavior | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| formal MindCube | 原始 RGB PIL 列表交给 `AutoProcessor`；默认 `min=max=200704` | VLM QA 分支存在 image processor path | DROID action 或 robot VLA 是 image-conditioned |
| formal DROID action | 当前 sample 返回 `images=[]`，user text含task/state/action JSON监督 | action-text causal path | 图像驱动 DROID action training |
| public-data dry-run adapter | `_read_image` 强制 `224×224`、除255、CHW；dry-run collator | smoke/dry-run tensor path | formal Qwen processor、真实 checkpoint 或 rollout lineage |

同一原图的 formal MindCube source-derived probe：

| 原始 H×W | processed H×W（factor32，min=max200704） | tokens |
| --- | ---: | ---: |
| `480×640` | `384×512` | 192 |
| `720×1280` | `320×576` | 180 |
| `1000×1000` | `448×448` | 196 |

这些数字只说明 pixel/token budget 不同，不能比较 OPD 与 OpenPiVLA 模型效果；dataset、任务、checkpoint、loss 与运行 lineage 不同。

## 9. Camera identity 与 image order

### 9.1 Token不等于camera semantic

`<|image_pad|>` 只占据序列位置；它不会自动知道“这是wrist camera”还是“这是workspace camera”。多图输入至少要绑定：

```text
sample_id / image_id
camera_id / frame_id
capture_timestamp
original_h,w / processed_h,w
transform revision / image_grid_thw
placeholder_index / image_index
valid / presence / uncertainty
```

formal collator 将batch内 image list 依次 flatten；如果message placeholder顺序、flatten顺序和camera metadata没有共同 manifest，即使shape正确也可能语义错位。

### 9.2 与 PER-003 的边界

PER-003 负责多视角/时序 fusion schema；PER-006 负责单张/多张图进入 processor 时的 identity/order。两者连接点是：

```text
PER-003 per-view item
  -> PER-006 transform + grid + placeholder
  -> model tokens
  -> output tied back to the same camera/frame/time
```

若缺 `camera_id/frame/timestamp`，后续3D lift、common-frame fusion和controller mapping都无法可靠归因。

## 10. 最小可复现 manifest

| 类别 | 最小字段 |
| --- | --- |
| provenance | dataset/sample/image ID、source path/hash、split、processor/model revision |
| camera | camera ID、optical frame、intrinsics/extrinsics revision、timestamp |
| raw image | original H/W、mode、dtype、range、orientation |
| transform | resize policy、requested/actual H/W、scale x/y、crop origin、pad offsets、interpolation |
| normalization | rescale flag/factor、normalize flag、mean/std |
| tokenization | patch/temporal/merge、`image_grid_thw`、image token count、placeholder index |
| inverse | point/box convention、processed→raw inverse、raw→camera/robot frame gate |
| validity | decode/resize/finite/range/order checks、failure reason |

一个summary中写“image_size=224”远远不够：它没有说明是否square stretch、smart resize、crop还是letterbox，也没有说明坐标与camera。

## 11. 可执行审计伪代码

```python
def audit_vlm_image(sample, processor, contract):
    # 1. Freeze provenance and camera identity before image decoding.
    rec = {
        "sample_id": sample.id,
        "image_id": sample.image_id,
        "camera_id": sample.camera_id,
        "frame_id": sample.frame_id,
        "timestamp": sample.timestamp,
        "processor_revision": contract.processor_revision,
    }

    # 2. Record raw image semantics; never infer them after transforms.
    image = decode_rgb(sample.image)
    rec["original_hw"] = image.shape[:2]
    rec["raw_dtype_range"] = inspect_dtype_range(image)

    # 3. Apply exactly one declared resize owner.
    if contract.resize_owner == "qwen_vl_utils":
        image, transform = qwen_resize(
            image,
            patch_size=contract.patch_size,   # Qwen3: 16
            min_pixels=contract.min_pixels,
            max_pixels=contract.max_pixels,
        )
        processor_kwargs = {"do_resize": False}
    elif contract.resize_owner == "processor":
        transform = {"kind": "processor_owned"}
        processor_kwargs = {}
    else:
        raise ValueError("ambiguous resize owner")

    # 4. Processor output must expose actual grid/token count.
    batch = processor(images=[image], return_tensors="pt", **processor_kwargs)
    grid = batch["image_grid_thw"][0]
    token_count = int(grid.prod()) // (contract.merge_size ** 2)
    rec.update({
        "transform": transform,
        "processed_grid_thw": grid.tolist(),
        "image_token_count": token_count,
        "pixel_values_shape": list(batch["pixel_values"].shape),
    })

    # 5. Round-trip a sentinel point/box and bind it to camera/frame.
    assert roundtrip_coordinate(sample.sentinel, transform, tolerance=contract.tol)
    assert rec["camera_id"] is not None and rec["frame_id"] is not None
    return rec
```

伪代码的核心是“resize owner唯一、actual grid可见、coordinate可逆、camera identity显式”。它不是本地已实现证明；只有保存真实manifest和round-trip日志后才能升级。

## 12. Failure taxonomy

| 失败层 | 症状 | 最小诊断 |
| --- | --- | --- |
| decode/color | RGB/BGR、EXIF orientation、alpha/background错误 | raw hash、mode、orientation probe |
| transform | double resize、square stretch、误以为letterbox | original/actual H/W、owner、scale/pad/crop |
| numeric | 0–1再次/255、mean/std错、dtype溢出 | min/max/mean/std before/after |
| grid/token | patch/merge不匹配、placeholder数错 | processor class/config、grid、token count |
| coordinate | point/box无法回原图、rounding偏移 | sentinel round-trip、per-axis error |
| camera/order | wrist/workspace互换、batch flatten错序 | camera ID、placeholder/image index |
| evidence | smoke path冒充formal、public机制冒充个人实现 | lineage、checkpoint/config/run bundle |

## 13. 方案比较与选择

| 选择 | 优点 | 风险 | 适用 gate |
| --- | --- | --- | --- |
| utils负责resize，processor不resize | message级pixel policy清晰、避免二次shape变化 | 必须传正确patch size并关闭processor resize | 记录utils/processor版本与actual grid |
| processor独占resize | 单一owner、配置随checkpoint | message级自定义尺寸需正确传递；本地checkpoint config必须pin | hash preprocessor config、train/eval parity |
| fixed square stretch | batch shape稳定、实现简单 | 破坏宽高比和grounding几何 | 只在任务接受且有matched验证时使用 |
| dynamic aspect-preserving | 保留几何、token按内容变化 | batch显存与token数波动 | pixel budget、bucket、OOM与latency统计 |
| letterbox | 保持宽高比且fixed canvas | 必须保存pad/inverse，模型会看到padding | sentinel inverse + padding mask/ablation |
| crop | 高分辨率局部细节 | 目标可能被裁掉、坐标需恢复crop origin | crop coverage、target visibility、inverse |

没有通用最优解；面试中应根据grounding精度、目标大小、宽高比分布、memory/latency和坐标可逆性选择。

## 14. 项目映射与真实性边界

| 项目 | 可以安全连接 | 当前不能声称 |
| --- | --- | --- |
| OPD | Qwen3-VL processor调用、50176 pixel budget、factor28→32静态风险、point/box protocol | mismatch已修复、导致某个metric下降、修复带来uplift |
| OpenPiVLA | MindCube单次processor、DROID action无图像、dry-run square224三条lineage | formal DROID是image-conditioned VLA、dry-run等于formal |
| WAM/UWM | camera/schema/provenance字段可迁移到manifest设计 | 已使用同一Qwenprocessor或同一token contract |
| Robot Harness | 工具输入可引用camera/frame/time schema | 已运行视觉导航或验证image token mapping |

安全回答遵循：

```text
public upstream contract
  -> local static code evidence
  -> deterministic probe
  -> missing runtime/roundtrip/A-B evidence
  -> bounded conclusion
```

## 15. 面试回答检查表

回答 PER-006 至少覆盖：

1. 先画 raw image→processed image→grid→tokens 四层；
2. 给出 \(F=p\,m\) 与 \(N_{\mathrm{img}}=T_gH_gW_g/m^2\)；
3. 解释pixel budget不是fixed shape，`min=max`仍受factor和rounding影响；
4. 区分direct resize、crop、letterbox和各自inverse；
5. 说明pixel range/rescale/normalize与train/eval parity；
6. 说明camera ID/order不是token自动提供；
7. 用OPD double-resize和OpenPiVLA三条lineage做项目hook；
8. 明确静态风险不等于性能因果，补证需要manifest、round-trip和matched A/B。

## 16. 结论与下一步

PER-006 的核心不是背“Qwen3 patch size是16”，而是把图像输入变成一条可复算合同：谁resize、实际shape、pixel范围、grid/token数、坐标inverse、camera/order和lineage都必须显式。当前source、knowledge与card已闭合，但OPD double-resize性能影响、OpenPiVLA image-conditioned DROID、camera/round-trip manifest仍未闭合，因此保持`WARN/unseen`。

`VLA-PER-007..009` source/knowledge/card已同步且保持`unseen`。下一bounded slice只做PER-010 metric/parser source freeze，不生成knowledge/card或修改其他mastery。

## References

1. [PER-006 Image Preprocess / Token / Camera Source Freeze](../sources/vol_06_per006_image_preprocess_token_camera_contract_source_freeze.html)。
2. [Vision Transformer v2](https://arxiv.org/abs/2010.11929v2)。
3. [Qwen3-VL frozen README](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/README.md) 与 [qwen-vl-utils vision_process.py](https://github.com/QwenLM/Qwen3-VL/blob/96588727e44c78b25ba03ea03b8e12f7e64fd0da/qwen-vl-utils/src/qwen_vl_utils/vision_process.py)。
4. [Transformers 4.57.1 Qwen2VLImageProcessorFast](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen2_vl/image_processing_qwen2_vl_fast.py) 与 [Qwen3VLProcessor](https://github.com/huggingface/transformers/blob/8cb5963cc22174954e7dca2c0a3320b7dc2f4edc/src/transformers/models/qwen3_vl/processing_qwen3_vl.py)。
5. [Qwen3-VL-8B preprocessor artifact](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct/blob/0c351dd01ed87e9c1b53cbc748cba10e6187ff3b/preprocessor_config.json)。
6. [PER-001 Grounding / Coordinate](vol_06_per001_grounding_coordinate.html) 与 [PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)。
