# VOL 06 Perception / Grounding / Navigation：Point Cloud、Voxel、BEV、Occupancy 与 Sampling（PER-013）

> 状态：`drafted / VLA-PER-013 / source_synced / card_synced / WARN`  
> 更新日期：2026-07-20  
> 前置：`VLA-PER-002` 2D→3D lift、`VLA-PER-003` multi-view/time、`VLA-PER-012` dense perception；后续：`VLA-PER-014` 3D semantic grounding、`VLA-PER-015` perception→action gate。  
> 来源入口：[PER-013 Point Cloud / Voxel / BEV / Occupancy Source Freeze](../sources/vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html)；对应自测：[PER-013 Atomic Card](../questions/vol_06_per013.html)。本页只把冻结证据转成可教学知识；题卡已生成并保持`unseen`，不创建训练状态，也不改变任何 mastery。

## 问题（Question）

面试官问“点云、voxel、BEV 和 occupancy 怎样选，sampling 怎样影响结果”时，不能只回答“点云精细、voxel 规则、BEV 高效”。需要从 downstream query 反推表示：连续坐标、局部几何、高度、空闲空间、unknown、语义身份分别要保留什么；frame、origin、range、resolution、axis、time 怎样定义同一个 tensor；FPS、ball query、voxel cap 和 aggregation 怎样改变模型身份；稀疏计算为何不是免费午餐；以及本地项目到底只有地图/PCD 接口，还是已有可复现的 3D encoder 与机器人闭环。

本节点建立的主链是：

```text
metric 3D samples + frame/time/schema
  -> point-set sampling and grouping
  -> voxel quantization and aggregation
  -> sparse 3D coordinates + features
  -> pillar or height-compressed BEV
  -> explicit / octree / implicit occupancy
  -> PER-014 semantic 3D grounding
  -> PER-015 reachability / collision / controller gate
```

## 知识地图位置与边界

| 相邻节点 | 该节点负责 | PER-013负责 |
| --- | --- | --- |
| PER-002 | pixel→camera/base 3D、intrinsics、TF | 已有 metric 3D sample 如何编码与量化 |
| PER-003 | multi-view/time identity 与 fusion | representation artifact 保留 source/time lineage |
| PER-008 | point/box/mask/keypoint/affordance 的选择 | point/voxel/BEV/occupancy 内部合同与转换损失 |
| PER-012 | segmentation、metric depth、surface、keypoint、affordance | surface 之后的 3D representation |
| PER-014 | 3D semantic/open-vocabulary grounding | 本页不产生 language-region binding 或 3D box |
| PER-015 | reachability、IK、collision、controller | 本页不从 occupancy score 推出可执行动作 |
| PER-016 | localization、SLAM 与 map drift | OctoMap 只作 representation exemplar |

## 1. 30秒直觉：表示不是形状，而是物理合同

一个可靠的 30 秒回答是：

> 我先从 downstream query 选表示。Point cloud 保留连续坐标，但邻域不规则；PointNet++ 用 FPS、ball query/kNN 和对称 pooling 建 local hierarchy。Voxel 把坐标按 origin、range、axis、voxel size 做 floor 量化，换来规则邻域，同时引入边界跳变、碰撞和 cap/drop。Sparse tensor 只计算 active coordinates，但 coordinate map、kernel map 和索引也有成本。Pillar/BEV 把高度变成 point feature 或 channel，并不天然丢掉全部 z；多传感器 BEV 还必须校准到同一物理平面。Occupancy 要区分 dense/sparse grid、概率 octree 和 implicit function，unknown 不能当 free。最终 occupancy 或 BEV 仍不是 semantic grounding、collision safety 或 robot success。

这段回答先封住六个偷换：

1. 同一个 `[i,j,k]` 被默认在不同 frame/origin 下表示同一位置；
2. FPS 被默认无随机性、无起点依赖且总优于 random；
3. MeanVFE 被默认与 learned VFE 信息等价；
4. “sparse”被默认总是更快、更省显存；
5. BEV 被默认完全删除高度或自动完成传感器对齐；
6. occupancy probability 被默认等于可碰撞、可导航或可执行。

## 2. Typed 3D Representation Manifest

### 2.1 最小 Schema

```json
{
  "sample_id": "...",
  "source_ids": ["camera/depth/lidar/frame ids"],
  "timestamp_range": ["t0", "t1"],
  "coordinate_frame": "camera | base | map",
  "axis_convention": "x-forward/y-left/z-up",
  "unit": "meter",
  "representation": "points | voxels | pillars | bev | occupancy_grid | octree | implicit_occupancy",
  "spatial_range": [[-1, 1], [-1, 1], [0, 2]],
  "origin": [0, 0, 0],
  "resolution_or_voxel_size": [0.02, 0.02, 0.02],
  "point_feature_schema": ["x", "y", "z", "intensity"],
  "sampling": {"method": "fps", "seed": 0, "budget": 4096},
  "aggregation": "max | mean | vfe | sparse_conv",
  "empty_unknown_policy": "unknown != free",
  "model_revision": "sha256:...",
  "validity_and_age": {"valid_ratio": 0.0, "age_ms": 0}
}
```

### 2.2 为什么 Manifest 属于模型身份

只有 `tensor.shape`，没有 frame、origin、resolution、range 与 axis，就不知道同一个 index 对应哪个物理位置；只有 point count，没有 sampling seed、input order 与 feature schema，就无法复现输入。对于 BEV，还必须记录 z aggregation、meters-per-cell 与 rotation augmentation；对于 occupancy，还必须记录 observed/unknown/free/occupied 的编码、阈值与更新时间。

推荐把 representation hash 计算在“原始来源 ID + frame/time + quantization/sampling config + model revision”之上。这样离线评估、线上日志和失败样本才能追到同一物理合同。

## 3. Representation 选择总览

| 表示 | 保留 | 主要损失/成本 | 适合回答 | 不能自动回答 |
| --- | --- | --- | --- | --- |
| unordered points | 连续坐标、per-point feature | 不规则邻域、sampling、带宽 | surface/local geometry query | free space、语义、可执行性 |
| dense voxel | 规则 3D 邻域 | \(O(N_xN_yN_z)\) memory、量化 | dense 3D feature/collision grid | unknown 语义、动作安全 |
| sparse voxel | active coordinate + feature | index/kernel map、active-pattern drift | 稀疏 3D backbone | 一定更快、更省 |
| pillar | xy cell + 聚合点特征 | z spatial bin 折叠、collision | 快速 2D backbone/BEV | 所有高度关系 |
| height-compressed BEV | z slice→channel | 2D convolution 的归纳偏置 | shared planar query | 自动 calibration |
| probabilistic octree | multi-resolution log odds | sensor model/staleness | ray-consistent map | learned surface/semantics |
| implicit occupancy | continuous query function | query/threshold/calibration | reconstruction/surface | sensor-ray free space、collision guarantee |

选择原则不是“谁最先进”，而是“下游要问什么”。接触点需要局部曲面和法向；导航需要 robot footprint 下的 free/occupied/unknown；语言 grounding 需要实例与语义；控制还需要时间、uncertainty、reachability 与 dynamics。一个 feature map 不会因为名字叫 BEV 就同时满足这些合同。

## 4. Point Set：Permutation Invariance 不等于 Pipeline Invariance

点集可写为：

\[
\mathcal P=\{(\mathbf x_i,\mathbf f_i)\}_{i=1}^{N},
\qquad
\mathbf x_i\in\mathbb R^3.
\]

变量解释：\(\mathbf x_i\) 是连续坐标，\(\mathbf f_i\) 可含 RGB、intensity、normal、timestamp 或 learned feature。直觉：点的排列本身不应改变几何语义，所以 PointNet 用共享 MLP 与 symmetric reduction；但 pipeline 仍会受 input order、采样起点、邻域截断、浮点排序与 tie-break 影响。实现映射：固定 PointNet++ 代码的 set abstraction 先 sampling，再 grouping，再 local PointNet，而不是对全体点一次 max pool。

因此应区分：

- **函数层 permutation invariant**：同一无序集合经理想对称聚合，结果不依赖排列；
- **数据管线不一定 invariant**：random/FPS 初始化、voxel cap、邻域前 K 个、duplicate handling 都可能依赖顺序；
- **物理坐标不等于语义**：点仍需 frame、unit、timestamp 与 source lineage。

## 5. PointNet++ Set Abstraction

一层 set abstraction 可抽象为：

\[
\mathbf h_j=
\operatorname{POOL}_{i\in\mathcal N(\mathbf c_j)}
\phi\!\left([\mathbf x_i-\mathbf c_j,\mathbf f_i]\right).
\]

变量解释：\(\mathbf c_j\) 是 sampled centroid；\(\mathcal N(\mathbf c_j)\) 是 ball query 或 kNN 邻域；\(\phi\) 是 shared PointNet/MLP；POOL 通常是 max 等 symmetric reduction。直觉：先用 centroid 覆盖空间，再在 metric-local neighborhood 中学习相对几何。实现映射：固定 PointNet++ SSG 代码明确使用 512 个 centroid、radius 0.2、K=32，再用 128、radius 0.4、K=64；这些超参共同定义 receptive field。

不能省略的模型身份包括：

1. input order 与 FPS 初始点/seed；
2. centroid 数量、radius、K；
3. ball query 或 kNN；
4. 空邻域、重复 neighbor 与不足 K 的 padding；
5. relative coordinate normalization；
6. point feature schema、pooling 和 multi-scale/density policy。

## 6. Sampling：Coverage、Density 与 Bias

### 6.1 FPS

Farthest Point Sampling 的一步是：

\[
i_t=\arg\max_i\min_{s<t}
\lVert \mathbf x_i-\mathbf x_{i_s}\rVert_2.
\]

变量解释：\(i_t\) 是第 \(t\) 个新点，已选集合为 \(\{i_s\}_{s<t}\)。直觉：每次选择离已有集合最远的点，倾向扩大 coverage。实现映射：固定 PointNet++ 实现维护每点到已选集合的最小距离并反复 argmax；第一个 centroid 与 tie-break 会影响最终集合。

FPS 不是“无偏代表性采样”。它对孤立点、outlier 和坐标尺度敏感，精确实现近似 \(O(NM)\)；在非均匀密度下 coverage 改善也不等于任务 accuracy 改善。

### 6.2 Ball Query 与 kNN

| 邻域 | 固定量 | 会漂移的量 | 适用直觉 | 风险 |
| --- | --- | --- | --- | --- |
| ball query | metric radius \(r\) | neighbor count | 保留物理尺度 | 稀疏区可能空、稠密区被 K 截断 |
| kNN | neighbor count \(K\) | metric radius | tensor shape 稳定 | 密度变化使 receptive field 尺度漂移 |

多尺度 grouping 能缓解 density variation，但增加计算，也不会自动消除传感器距离、遮挡和采样模式带来的 domain shift。

### 6.3 必报诊断

至少报告 points kept/dropped、coverage radius、nearest-neighbor density strata、每邻域有效点分布、empty/duplicate ratio、sampling seed 与 run variance。只报告 “4096 points” 不足以复现。

## 7. Voxelization：规则邻域来自离散量化

对 origin \(\mathbf o\) 与 voxel size \(\mathbf v\)：

\[
\mathbf q_i=
\left\lfloor
\frac{\mathbf x_i-\mathbf o}{\mathbf v}
\right\rfloor.
\]

变量解释：\(\mathbf q_i\) 是 integer voxel coordinate；\(\mathbf o\) 决定 grid 相位；\(\mathbf v\) 决定各轴 resolution。直觉：把连续点映射到规则 cell，便于 3D convolution，却牺牲 cell 内精确位置。实现映射：MinkowskiEngine 量化路径会处理负坐标 floor 并生成 unique/inverse map；OpenPCDet 配置同时固定 `POINT_CLOUD_RANGE`、`VOXEL_SIZE`、`MAX_POINTS_PER_VOXEL` 和 train/test max voxels。

### 7.1 四个常见边界

1. **origin/range/axis**：同一世界点在不同原点或轴顺序下 index 不同；
2. **floor/round**：负坐标与边界点归属会改变；
3. **boundary flip**：\(x=0.99\) 与 \(1.01\) 在 \(v=1,o=0\) 时落入 0/1；
4. **cap/drop**：每 voxel 最大点数和全局最大 voxel 数会丢弃数据，且可能受顺序/seed 影响。

训练与部署若只对齐 voxel size、没有对齐 range/origin/axis/floor，得到的是不同模型输入。

## 8. Aggregation：MeanVFE 与 Learned VFE 不等价

固定 OpenPCDet `MeanVFE` 可写为：

\[
\mathbf f_v=
\frac{1}{\max(n_v,1)}
\sum_{i\in v}\mathbf f_i.
\]

变量解释：\(n_v\) 是 voxel 中的 valid point count，\(\mathbf f_i\) 是被聚合的 point feature。直觉：mean 是简单稳定的 permutation-invariant baseline，但会把不同集合压成同一向量。实现映射：集合 \([0,2]\) 与 \([1,1]\) 的 mean 都是 1；若不保留 count、local offset、variance 或 higher moments，二者不可区分。

VoxelNet 的 stacked VFE 会编码 point-wise feature 与 locally aggregated feature，并且 fixed-T voxel 内可能 random sample；PointPillars 也有 point-wise decorated features。它们不能因为最后都得到一个 cell feature 就统称为 “mean pooling”。

面试中应主动说出三种 alias：

- quantization collision：不同连续位置落入同 cell；
- aggregation collision：不同 cell 内集合得到同 feature；
- truncation collision：cap 后不同原始集合变成相同保留子集。

## 9. Sparse Tensor 与 Sparse Convolution

Sparse tensor 由 active coordinates \(\mathcal C\) 与 features \(\mathcal F\) 组成，batch index 也是 coordinate 的一部分。一般化 sparse convolution 可抽象为：

\[
\mathbf y_{\mathbf u}=
\sum_{\mathbf k\in\mathcal K(\mathbf u,\mathcal C_{\mathrm{in}})}
\mathbf W_{\mathbf k}\mathbf x_{\mathbf u+\mathbf k}.
\]

变量解释：\(\mathbf u\) 是 output coordinate；\(\mathcal K\) 只保留 kernel offset 与 active input coordinate 的交集；\(\mathbf W_{\mathbf k}\) 是对应 kernel weight。直觉：避免在大量 empty cell 上做 dense multiply，但要先维护 coordinate 与 kernel mapping。实现映射：固定 OpenPCDet backbone 同时出现 `SubMConv3d`、`SparseConv3d` 与 `SparseInverseConv3d`，它们的 output coordinate set 与 stride 行为不同。

### 9.1 三类算子不可合并

| 算子 | active pattern | 典型作用 | 风险 |
| --- | --- | --- | --- |
| SubMConv | 通常只在原 active sites 输出 | 保持稀疏形状的局部特征 | 信息传播受 active topology 限制 |
| SparseConv | stride/kernel 可产生新 output sites | 下采样与扩大 receptive field | active count 与 coordinate map 改变 |
| InverseConv | 用对应 mapping 恢复分辨率 | decoder/upsampling | 必须绑定正确 indice/key |

### 9.2 “Sparse 一定更快”为什么错

总成本还包括 coordinate dedup、hash/map、kernel map、index gather/scatter、allocator、feature width、batch fragmentation 与硬件支持。active ratio 很低且空间大时通常有利；场景很小、feature 很窄或 active pattern 不友好时，索引开销可能主导。应在同硬件、同 batch、同精度下报告 latency p50/p95、peak memory、active count 与 dense/sparse parity。

## 10. Pillar：折叠 z 的 Spatial Bin，不必删除 z Feature

PointPillars 把整个 vertical column 内的点组织成 pillar，用 PointNet 编码后 scatter 到 2D pseudo-image。若 z range 为 \([-3,1]\)，z voxel size 为 4，则 \(z=-2.5\) 和 \(0.5\) 的 spatial z index 都是 0。

这意味着：

- z 不再作为多层 spatial grid index；
- per-point z、相对 pillar center 的 z、height statistics 仍可进入 feature；
- 聚合以后能否保留细粒度高度取决于 feature decoration、encoder 与 cap；
- 不能回答“pillar 完全不含高度”，也不能回答“pillar 无损保存 3D”。

固定 PointPillars/OpenPCDet 配置中的 range、voxel size、max points、scatter shape 与 backbone 都属于 artifact identity。

## 11. Height Compression 与 BEV

OpenPCDet 的一条 HeightCompression 路径将：

\[
[N,C,D,H,W]
\longrightarrow
[N,C\!\cdot\!D,H,W].
\]

变量解释：\(D\) 个 height slice 被 reshape 到 channel，而不是先做数值平均；\(H,W\) 是 BEV 平面。直觉：2D backbone 获得更高效率，同时高度只以 channel pattern 存在。实现映射：固定 `height_compression.py` 直接把 dense spatial feature 的 \(C,D\) 合并。

BEV artifact 至少要绑定：

- frame 与 x/y axis；
- origin、range、meters-per-cell；
- z range 与 aggregation/compression；
- ego/map pose 与 timestamp；
- augmentation matrix；
- invalid/unknown/padding policy。

二维数组相同，不代表物理平面相同。

## 12. BEVFusion：共享平面不是自动对齐

BEVFusion 的关键思想是 camera 与 LiDAR feature 先进入统一 BEV，再在 shared planar coordinates 上融合。camera 分支需要 view transform 与 BEV pooling，LiDAR 分支需要 voxelization，之后才是 fuser/head。

最小 calibration contract 包含：

```text
camera intrinsics/extrinsics
LiDAR-to-ego transform
ego/map pose
image and point-cloud augmentation matrices
depth/view-transform bins
BEV origin/range/resolution
sensor timestamp, validity and age
```

把两张同 shape feature map 按 array index 相加，不构成 calibrated fusion。固定论文/代码的 nuScenes、Waymo、KITTI 结果也不能直接外推为桌面 manipulation、VLA 或本地 Robot Harness 的收益；必须有目标域 config、checkpoint、calibration、matched ablation 与 same-protocol result。

## 13. Occupancy：至少三种不同合同

| 类型 | 表示 | unknown/free 关系 | 典型用途 | 主要风险 |
| --- | --- | --- | --- | --- |
| dense/sparse explicit grid | cell→state/probability/logit | 必须显式编码 | collision map、scene completion | cubic memory、unobserved 误当 free |
| probabilistic octree | allocated node + log odds | 未分配通常 unknown | multi-resolution mapping/raycast | sensor model、clamp、staleness |
| implicit occupancy | \(o_\theta(\mathbf p,\mathbf z)\) | classifier 语义，不自带 ray-free | reconstruction/surface query | query cost、threshold、calibration |

“Occupancy model”若没有说是哪一种，答案仍不完整。

## 14. OctoMap：Observed Free 与 Unknown 必须分开

概率 octree 的 log-odds update 可抽象为：

\[
L_t(n)=
\operatorname{clip}\!\left(
L_{t-1}(n)+\lambda(z_t,n),
L_{\min},L_{\max}
\right).
\]

变量解释：\(L_t(n)\) 是 node \(n\) 的 occupancy log odds；\(\lambda(z_t,n)\) 根据 sensor ray 中的 free cell 或 endpoint hit 使用不同增量；上下界防止置信度无限累积。直觉：free 是“被射线穿过的观测证据”，unknown 是“没有足够观测/未分配”，二者不能合并。实现映射：固定 OctoMap code 先计算 `free_cells` 与 `occupied_cells`，再分别以 miss/hit 更新 node。

Octree resolution、hit/miss probability、occupancy threshold、clamping、max range、ray origin、time decay 与 dynamic-object policy 都会改变地图语义。Source freeze 只用固定 official code 支撑这一机制，没有可靠冻结 OctoMap 论文 PDF，也没有本地 OctoMap integration。

## 15. Occupancy Networks：连续 Query 与 Surface Threshold

Implicit occupancy 可写为：

\[
o_\theta:
\mathbb R^3\times\mathcal Z\rightarrow[0,1],
\qquad
\mathcal S_\tau=
\{\mathbf p\mid o_\theta(\mathbf p,\mathbf z)=\tau\}.
\]

变量解释：\(\mathbf p\) 是任意 3D query point，\(\mathbf z\) 是 condition/latent，\(\tau\) 是 surface decision threshold。直觉：网络没有存储一张固定分辨率网格，而是按坐标查询 inside/outside probability；surface 是某个等值面。实现映射：固定 occupancy-networks generation 默认 probability threshold 0.5，对应 logit 0；阈值改为 0.7 时 logit 约 0.8473，抽取出的 surface 会改变。

MISE 能自适应细化 query 以减少 dense evaluation，却不会自动提供：

- sensor-ray observed free space；
- unknown 与 unobserved policy；
- dynamic occupancy；
- calibrated collision probability；
- robot footprint、swept volume 或控制安全。

因此 implicit occupancy score 不能直接作为 collision gate。

## 16. Memory 与 Compute Scaling

Dense grid feature memory 的下界是：

\[
M_{\mathrm{dense}}=
N_xN_yN_z\,C\,b.
\]

变量解释：\(N_x,N_y,N_z\) 是 cell 数，\(C\) 是 feature channels，\(b\) 是每个 feature 的 bytes。直觉：range 每轴扩大 2 倍，dense 3D cell 数最多扩大 8 倍；resolution 每轴减半同样会带来 8 倍 cell。实现映射：\(200^3\times64\times4=2{,}048{,}000{,}000\) bytes，约 1.907 GiB；若 active ratio 为 1%，仅 active feature 约 19.53 MiB。

后一个数字不包括 coordinates、kernel maps、allocator、activations、gradients 与 optimizer state，所以不能据此宣称“节省 99% 总显存”。报告表示效率时至少需要：

| 类别 | 必报字段 |
| --- | --- |
| geometry | range、resolution、active count/ratio、point count |
| loss | quantization residual、collision/cap/drop、unknown coverage |
| runtime | hardware、batch、precision、warmup、p50/p95 latency |
| memory | feature-only estimate、measured peak、training/inference |
| task | same split/protocol 下的 downstream metric |

## 17. Conversion Loss 与 Downstream Sufficiency

```text
metric points
  -> sample/group                 # sparse region may be dropped
  -> quantize + aggregate         # boundary, collision, cap, alias
  -> sparse 3D features           # coordinate/kernel contract
  -> pillar / height compression  # z loss differs by path
  -> BEV fusion                   # calibrated common frame required
  -> occupancy map/function       # unknown/free/threshold semantics
  -> PER-014 semantic grounding   # object/language identity
  -> PER-015 action gate          # reachability/collision/controller
```

每次转换都应保存 input artifact ID、config/hash、output schema 和 loss diagnostics。建议用 round-trip probe：从 point→voxel index→voxel center，检查 quantization residual；从 sensor ray→occupancy，检查 observed free 与 endpoint occupied；从 3D point→BEV cell→physical center，检查 frame/origin/resolution。

### 17.1 Metric 边界

| 输出 | 可报告 | 不等价于 |
| --- | --- | --- |
| sampled points | coverage radius、retention、density strata | unbiased sampling、task accuracy |
| voxel/pillar | active count、collision/cap/drop、residual | 3D detection 或 action success |
| sparse feature | active pattern、latency、memory、dense parity | 总是更快、semantic correctness |
| BEV | round-trip、cell coverage、sensor validity | calibrated fusion、navigation success |
| explicit occupancy | observed-cell IoU、free error、unknown coverage | implicit surface 或 collision safety |
| implicit occupancy | occupancy IoU、Chamfer/F-score、query cost | ray-consistent free space、dynamic map |

所有数字都要绑定 dataset/split、frame/range/resolution、sampling seed、aggregation、threshold、observed denominator、hardware 与 code/checkpoint revision。

## 18. Deterministic Probes：先验证合同，再跑大模型

| Probe | 固定输入 | 结果 | 只支持 |
| --- | --- | --- | --- |
| FPS coverage | `[0,1,2,10]`，start=0，budget=2 | FPS `[0,3]` radius=2；fixed random `[0,1]` radius=9 | 该例 coverage，不证明普遍 accuracy |
| voxel boundary | x=0.99/1.01，v=1，origin=0 | index 0/1 | 0.02 平移可改离散 tensor |
| mean alias | `[0,2]` vs `[1,1]` | mean 均为 1 | mean 需要 count/offset 等补充 |
| dense/sparse estimate | \(200^3,C=64,\) float32 | dense 1.907 GiB；1% feature 19.53 MiB | 不含 sparse overhead |
| pillar z collapse | range [-3,1]，dz=4 | z=-2.5/0.5 均 index 0 | spatial bin 相同，非 feature 全丢 |
| implicit threshold | probability 0.5/0.7 | logit 0/0.8473 | threshold 属于 surface identity |
| local pixel/world | pixel (100,200)，固定 origin/res | world (-48.92593,35.5881134) | map transform 可复算 |
| local PCD header | 固定 `world.pcd` | 54,856 点，六个 fields | asset/schema，不是 encoder |
| local path census | 86 个 high-signal tracked 文本 | 78 third_party、8 data/docs/bridge/tests | vendored code 不等于个人实现 |

这些 probe 应进入 CI 或 artifact audit；它们验证 contract，不替代真实 dataset 与 robot evaluation。

## 19. Failure Taxonomy 与诊断顺序

| Failure | 表面症状 | 首查字段 | 最小 Probe |
| --- | --- | --- | --- |
| frame/origin drift | 整图平移/旋转 | frame、axis、origin、TF | physical round-trip |
| voxel boundary | 小位姿变化导致 feature 跳变 | floor、resolution、augmentation | 0.99/1.01 |
| sampling miss | 稀疏小物体消失 | seed、budget、density strata | coverage sweep |
| voxel cap/drop | 稠密表面被截断 | max points/voxels、order | shuffled-input parity |
| aggregation alias | 不同局部几何同 feature | mean/max/VFE、count | `[0,2]` vs `[1,1]` |
| sparse pattern explosion | memory/latency 突增 | operator、active sites、stride | layerwise active trace |
| pillar height alias | 上下结构混淆 | z feature/bin/compression | two-height probe |
| BEV misalignment | camera/LiDAR ghosting | calibration/augmentation/time | landmark overlay |
| unknown→free | 未观测区可规划 | occupancy encoding/ray update | occluded-cell test |
| stale occupancy | 动态障碍残留或消失 | timestamp/decay/update | moving-object trace |
| implicit threshold drift | surface thickness 改变 | probability/logit threshold | threshold sweep |
| controller rejection | occupancy 好但动作失败 | footprint/IK/collision/controller | rejection reasons |

推荐顺序：

```text
schema/frame/unit/time
  -> sampling and range
  -> quantization/cap/aggregation
  -> sparse active pattern
  -> BEV calibration
  -> occupancy unknown/threshold/staleness
  -> semantic grounding
  -> planner/controller
  -> episode metric
```

不要在 frame 或 unknown policy 未知时先调网络深度。

## 20. Fail-closed Pseudocode

```python
def encode_3d(points, manifest, cfg):
    # 1. Geometry without an explicit physical identity is rejected.
    require(manifest.coordinate_frame)
    require(manifest.unit == "meter")
    require(manifest.timestamp_range and manifest.source_ids)
    require(cfg.origin and cfg.spatial_range and cfg.voxel_size)

    # 2. Sampling is part of the artifact identity.
    sampled, sample_idx = sample_points(
        points,
        method=cfg.sampling_method,
        budget=cfg.point_budget,
        seed=cfg.seed,
    )

    # 3. Quantization reports every loss mechanism.
    coords = floor((sampled.xyz - cfg.origin) / cfg.voxel_size)
    valid = inside_range(coords, cfg.grid_shape)
    unique, inverse, counts = unique_coordinates(coords[valid])
    audit = report_collision_cap_drop(
        input_count=len(points),
        sampled_count=len(sampled),
        valid_mask=valid,
        unique=unique,
        counts=counts,
    )

    # 4. Representation semantics remain explicit.
    if cfg.representation == "sparse_voxel":
        features = aggregate(sampled.features[valid], inverse, cfg.aggregation)
        return SparseTensor(unique, features), audit

    if cfg.representation == "pillar_bev":
        require(cfg.bev_frame and cfg.meters_per_cell)
        pillars = aggregate_by_xy(sampled[valid], cfg)
        return scatter_to_bev(pillars, cfg.bev_frame), audit

    if cfg.representation == "occupancy":
        # An empty tensor cell is never silently interpreted as observed free.
        require(manifest.sensor_origin and cfg.unknown_policy)
        return update_occupancy(
            sampled,
            sensor_origin=manifest.sensor_origin,
            timestamp=manifest.timestamp_range[1],
        ), audit

    raise ValueError("unfrozen representation")
```

这是面试与目标实现合同，不是本地项目已有代码。真实系统还需 sensor model、calibration、TF/time、dynamic-object policy、uncertainty、footprint/swept volume、memory/latency 与 downstream episode logger。

## 21. Robot Harness：直接证据映射

本地 `agent@3f4c8b3` 有一个必须单独陈述的 direct exception：

| Artifact | 直接支持 | 不能支持 |
| --- | --- | --- |
| `occupancy2d_map.json/png` | 2D tri-state map；0 occupied、127 unknown、255 free；约 0.02m resolution、origin/range | 3D occupancy、OctoMap、地图 accuracy |
| `world.pcd` | 54,856 点；`x y z intensity timestamp ring` schema | 个人生成、online stream、PointNet/voxel inference |
| `ros2_bridge.py` | occupancy/pointcloud path、existence ready flag、URL 暴露 | PCD 解析、voxelization、sparse convolution |
| scenario 文档 | 2D occupancy、PCD 引用、heightmap/A* 与 WebUI 设计说明 | 运行时等价、个人 ownership、机器人收益 |

其中 PCD SHA-256 为 `494A53320AF2EC10C4D1AADD17CE0F7D943820BA34536C23871BB5CA711F0B42`；bridge SHA-256 为 `8291D64DE01AAC2EFDF52409008EFD7AE18C5FEC0BA7B9D4677F6636F8287A48`。86 个 high-signal tracked 文本中 78 个位于 `third_party/`；依赖或 vendored code 的存在不等于候选人实现。

最安全的项目表述是：

> 我核对到 Harness 中有三态 2D occupancy 资产、带时间戳与 ring 字段的 PCD 文件，以及把路径/URL 暴露给前端的 bridge；这说明数据接口和仿真资产存在。当前没有证据表明第一方路径解析 PCD、做 voxel/BEV/OctoMap 或运行 learned occupancy，所以我不会把它讲成自研 3D perception stack。

## 22. 五项目 Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 若要升级需补 |
| --- | --- | --- | --- |
| Robot Harness | 2D tri-state occupancy、PCD asset/schema、path/URL bridge | 自研 PointNet/voxel/BEV/OctoMap、online 3D、个人 ownership | generator、ingest/voxel code、ROS bag、TF/time、planner trace |
| OPD | 2D 标注点集合可转 box | 3D point cloud、voxel/occupancy | z/frame/time/schema、3D checkpoint/eval |
| OpenPiVLA | image/language/action 可与显式 3D intermediate 比较 | 已集成 3D encoder 或其带来 97.4 | module/config/checkpoint/ablation/episodes |
| WAM | future image 可作为 geometry diagnostic 候选 | learned occupancy/BEV head | local head/loss/config/raw prediction |
| UWM | image/action/video world model 与 LIBERO protocol | point/voxel/occupancy 模型或 3D 泛化 | model diff、3D data、checkpoint、rollout |

OPD 代码中的 “point cloud(s)” 只指 2D 标注点集合经 min/max x/y 加 margin 转 box 或 prompt 文本，没有 z、frame、PCD、voxel、BEV 或 occupancy tensor。公共论文说明机制，项目文件说明资产；二者都不能替代 local integration、matched result 与候选人 ownership。

## 23. 面试回答模板、追问与危险答案

### 23.1 两分钟结构化回答

> 我会先从 downstream query 反推表示，并冻结 frame、axis、origin、range、resolution、time 和 feature schema。Point cloud 保留连续坐标，PointNet++ 用 FPS 选覆盖中心，再用 ball query 或 kNN 建邻域，local PointNet 和 symmetric pooling 得到 hierarchy；采样起点、radius、K 和 density policy 都属于模型身份。Voxel 用 floor((x-origin)/voxel_size) 量化，规则化邻域，但会有边界跳变、同 cell 碰撞、max-points/max-voxels drop；MeanVFE 与 learned VFE 不能混称。Sparse convolution 只计算 active coordinates，但 coordinate/kernel map 有成本，SubM、stride sparse 和 inverse conv 的 active pattern不同。Pillar 折叠 z 的 spatial bin，z 仍可能作为 point feature；另一种 BEV 会把 D reshape 到 channel。多传感器 BEV 必须绑定 calibration 和 timestamp。Occupancy 还要区分 explicit grid、OctoMap log-odds 与 implicit function，unknown 不等于 free，surface threshold 不等于 collision safety。本地 Harness 只有 2D map、PCD asset 和 bridge 的直接证据，不能声称我实现了这些 3D 模型。

### 23.2 高频追问

1. PointNet 为什么 permutation invariant，为什么完整 pipeline 仍可能依赖输入顺序？
2. FPS 的目标是什么？起点、outlier 和复杂度有什么影响？
3. ball query 与 kNN 在 density shift 下分别怎么变？
4. voxel coordinate 为什么要用 origin、range、axis 和 floor 一起定义？
5. hard voxelization 与 dynamic voxelization 的主要边界是什么？
6. `[0,2]` 与 `[1,1]` 为什么暴露 MeanVFE alias？
7. SubMConv、SparseConv 和 InverseConv 的 output sites 有何差异？
8. 什么场景下 sparse convolution 未必比 dense 快？
9. PointPillars 是否完全丢失 z？
10. HeightCompression 把 D 放进 channel 有什么利弊？
11. BEVFusion 为什么仍需要完整 calibration？
12. empty voxel、unknown 和 observed free 有何不同？
13. OctoMap 如何利用 ray 的 miss/hit evidence？
14. implicit occupancy 的 0.5 threshold 改变会怎样？
15. occupancy IoU 为什么不等于 collision safety？
16. 你会怎样用 deterministic probes 检查 representation regression？
17. 本地 Robot Harness 到底支持哪些 3D 相关 claim？

### 23.3 危险答案与修正

| 危险答案 | 问题 | 安全修正 |
| --- | --- | --- |
| “PointNet 对点顺序完全不敏感” | sampling/cap/tie-break 可依赖顺序 | 区分 symmetric function 与 pipeline |
| “FPS 总比 random 好” | 只保证某种 coverage 倾向 | 报 task、seed、coverage 与 matched result |
| “voxel size 一样输入就一样” | origin/range/axis/floor 仍可不同 | 冻结完整 quantization contract |
| “MeanVFE 就是 VoxelNet” | learned VFE 与 mean 机制不同 | 指明具体 encoder/revision |
| “Sparse 一定节省 99% 显存” | 忽略坐标/kernel/allocator | 测 measured peak 和 latency |
| “Pillar 把高度全丢了” | z 可能仍在 point feature | 区分 spatial z bin 与 feature |
| “BEV 天然对齐多传感器” | shared shape 不等于 shared frame | 绑定 calibration/augmentation/time |
| “没有点就是 free” | 无点可能是 occluded/unobserved | unknown 与 observed free 分离 |
| “occupancy 0.9 就可以执行” | 缺 footprint、uncertainty、controller | 继续过 PER-015 gate |
| “Harness 已有 3D perception” | 只有 asset/path direct evidence | 只说 2D map、PCD schema、bridge |

## 24. 白板 Checklist 与练习标准

能够不看材料完成：

- 画出 point→sample/group→voxel→sparse→pillar/BEV→occupancy 主链；
- 写出 typed 3D manifest 的 frame/origin/range/resolution/time；
- 推导 PointNet++ set abstraction 并解释 FPS、ball query、kNN；
- 写出 voxel floor 公式并演示 boundary flip；
- 用 `[0,2]` 与 `[1,1]` 解释 aggregation alias；
- 比较 SubM/Sparse/Inverse convolution 与 active pattern；
- 解释 pillar z bin 与 height-compression channel 的区别；
- 列出 BEVFusion 的 calibration contract；
- 比较 explicit grid、OctoMap 和 implicit occupancy；
- 算出 \(200^3\times64\times4\) 的 memory；
- 走完十二类 failure 的诊断顺序；
- 说清 Robot Harness 与其余四项目的真实性边界；
- 完成两分钟回答并接住至少八个追问。

`drafted` 不等于掌握。只有真实口述、追问、评分与纠错后才能改变题卡状态；对应题卡已生成并保持`unseen`，`coaching_state.md` 也不应创建。

## 25. 结论与下一步

Point、voxel、sparse tensor、pillar/BEV 与 occupancy 不是几种可随意替换的 tensor shape，而是不同的信息保留、物理坐标、unknown 语义与计算合同。可靠答案必须同时讲清 representation identity、conversion loss、runtime cost、metric boundary 与 downstream sufficiency。

本地项目目前最强的直接映射是 Robot Harness 的 2D 三态 occupancy 资产、54,856 点 PCD schema 和 path/URL bridge；没有证据支持自研 PointNet++、voxel encoder、BEVFusion、OctoMap、learned occupancy、online 3D perception 或其 robot benefit。

`VLA-PER-013` source、knowledge 与 card 已在独立 bounded slices 同步，题卡保持`unseen/WARN`。后续`VLA-PER-014` source与knowledge也已同步；下一 bounded slice只生成一张PER-014 atomic card并保持unseen，不启动PER-015，不创建`coaching_state.md`，不改变任何 mastery。

## References

1. [PER-013 Point Cloud / Voxel / BEV / Occupancy Source Freeze](../sources/vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html)：固定六篇 primary papers、六个 official repositories、九个 deterministic probes 与五项目 audit。
2. Qi et al., [PointNet++ v1](https://arxiv.org/abs/1706.02413v1)；[official code@4292663](https://github.com/charlesq34/pointnet2/tree/42926632a3c33461aebfbee2d829098b30a23aaa)。
3. Zhou & Tuzel, [VoxelNet v1](https://arxiv.org/abs/1711.06396v1)。
4. Lang et al., [PointPillars v2](https://arxiv.org/abs/1812.05784v2)。
5. Choy et al., [Minkowski ConvNet v4](https://arxiv.org/abs/1904.08755v4)；[MinkowskiEngine@02fc608](https://github.com/NVIDIA/MinkowskiEngine/tree/02fc608bea4c0549b0a7b00ca1bf15dee4a0b228)。
6. Liu et al., [BEVFusion v3](https://arxiv.org/abs/2205.13542v3)；[official code@326653d](https://github.com/mit-han-lab/bevfusion/tree/326653dc06e0938edf1aae7d01efcd158ba83de5)。
7. Mescheder et al., [Occupancy Networks v2](https://arxiv.org/abs/1812.03828v2)；[official code@406f794](https://github.com/autonomousvision/occupancy_networks/tree/406f79468fb8b57b3e76816aaa73b1915c53ad22)。
8. [OpenPCDet@233f849](https://github.com/open-mmlab/OpenPCDet/tree/233f849829b6ac19afb8af8837a0246890908755) 与 [OctoMap@f012f5f](https://github.com/OctoMap/octomap/tree/f012f5f0a4f58cad19501833f9c0ea9d864427b6)。
9. [PER-002 3D Lift / Frame](vol_06_per002_3d_lift_frame.html)、[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal.html)、[PER-012 Segmentation / Depth / Keypoint / Affordance](vol_06_per012_segmentation_depth_keypoint_affordance.html)。
10. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) 与 source freeze 中固定的 `agent@3f4c8b3` direct artifacts。
