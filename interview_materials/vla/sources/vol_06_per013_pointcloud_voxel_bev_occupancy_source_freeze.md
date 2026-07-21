# VOL 06 PER-013 Source Freeze：Point Cloud、Voxel、BEV、Occupancy Representation 与 Sampling

> 状态：`source_frozen / VLA-PER-013 / primary_official_checked / harness_2d_map_pcd_interface_boundary / knowledge_synced / card_synced / WARN`  
> 冻结日期：2026-07-20  
> 证据截止：2026-07-20  
> 本切片只冻结unordered point set、hierarchical sampling/grouping、hard/dynamic voxelization、sparse tensor/convolution、pillar/BEV projection、probabilistic octree occupancy与implicit occupancy的representation contract；不生成knowledge/card，不重讲PER-002的2D→3D lift、PER-003的multi-view/time fusion、PER-014的3D semantic grounding或PER-015的action gate。

## 问题（Question）

面试官问“点云、voxel、BEV和occupancy怎样选，sampling怎样影响结果”时，需要回答哪些信息被保留或丢失、坐标/分辨率/范围如何进入tensor、稀疏计算为何不是免费午餐、free/occupied/unknown与implicit surface为何不等价，以及本地项目到底只有地图/PCD接口还是已经训练了3D encoder。

## 1. 结论先行

1. Point cloud保留连续坐标与per-point feature，但没有规则邻域；PointNet++通过FPS、ball query/kNN与local PointNet建立hierarchy，sampling/grouping policy属于模型身份。
2. Voxel把连续坐标量化到规则3D index；同voxel碰撞、边界抖动、max-points截断、empty-space memory与pooling alias必须显式记录。VoxelNet的VFE、OpenPCDet的MeanVFE和Minkowski sparse convolution不是同一个aggregation contract。
3. Pillar把一整列z范围映射到同一个xy cell，再scatter成2D pseudo-image；BEV是共享坐标平面，不天然等于“丢掉所有高度”。PointPillars可在pillar feature中编码z，而OpenPCDet HeightCompression可把D维折叠为channel。
4. BEVFusion证明camera/LiDAR可在统一BEV中融合，但其固定论文/代码是自动驾驶3D detection/segmentation上下文；不能直接外推为用户 manipulation/VLA 的local BEV stack或收益。
5. Occupancy至少分三类：显式dense/sparse grid、OctoMap式概率octree、Occupancy Networks式连续implicit function。未观测unknown不能当free，binary occupancy threshold也不能当surface/robot collision guarantee。
6. 本地Robot Harness存在2D occupancy PNG/JSON、54,856点PCD资产与path/URL bridge；这支持地图资产和接口事实，不支持候选人实现PointNet++、voxel encoder、BEVFusion、OctoMap或learned 3D occupancy。OPD的“point cloud”只指2D标注点集合转box。
7. 仍为`WARN`：没有本地3D representation checkpoint/config、voxel manifest、raw tensor、frame/time lineage、matched representation ablation、planner/controller trace或候选人ownership确认。

## 2. 冻结来源矩阵

### 2.1 Primary Papers

| 来源 | 固定版本 / 读取日期 | PDF SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| Qi et al., [PointNet++](https://arxiv.org/abs/1706.02413v1) | arXiv `1706.02413v1`；2017-06-07；PDF读取2026-07-20 | `5CD120458CD481078AAF927F0BFED0EF646423E107F5CC2750B9C59F5B8E3795` | set abstraction、FPS、ball query/kNN、density/multi-scale动机 | 任意本地模型、跨域最优或sampling无偏 |
| Zhou & Tuzel, [VoxelNet](https://arxiv.org/abs/1711.06396v1) | arXiv `1711.06396v1`；2017-11-17；PDF读取2026-07-20 | `C470615A7A56B1A84946CD7E00D1AB148636ACC0B6EC074F8B6FB1E322309FD9` | equal-spaced voxel partition、fixed-T random sampling、stacked VFE | OpenPCDet当前实现与原论文逐行等价、本地检测结果 |
| Lang et al., [PointPillars](https://arxiv.org/abs/1812.05784v2) | arXiv `1812.05784v2`；2019-05-07；PDF读取2026-07-20 | `FC3211F5D3754C8C6FB4A36E69A86CC8A21C915796A0B19AB612E610D42B2E69` | vertical pillars、PointNet encoder、scatter到2D pseudo-image | 所有z信息必然消失、用户项目已有pillar部署 |
| Choy et al., [Minkowski ConvNet](https://arxiv.org/abs/1904.08755v4) | arXiv `1904.08755v4`；2019-06-13；PDF读取2026-07-20 | `2FB54CC7B4CDC56B9131CD2A876B63181E44ACAA72BF627A2049B46E88BA3DBD` | coordinate-feature sparse tensor、generalized sparse convolution | 稀疏计算总比dense快、任意occupancy或robot task收益 |
| Liu et al., [BEVFusion](https://arxiv.org/abs/2205.13542v3) | arXiv `2205.13542v3`；2024-09-01；PDF读取2026-07-20 | `8B2D5D3D07FDAFA38119E6876487226CEEAAC1E02E664F4C4F3F2D77206B428F` | camera-to-BEV、optimized BEV pooling、shared-BEV fusion | manipulation/VLA通用收益、本地sensor calibration或部署 |
| Mescheder et al., [Occupancy Networks](https://arxiv.org/abs/1812.03828v2) | arXiv `1812.03828v2`；2019-04-30；PDF读取2026-07-20 | `7FED3471C7F0A149BACD10FD192CCF2996E287CB67734868CDCD78384776D888` | continuous occupancy function、decision boundary、MISE | free-space ray model、dynamic occupancy、碰撞安全 |

六份PDF均检查`%PDF`与`%%EOF`，用`pypdf`读取全部页面，并视觉渲染六份论文的method page；传输截断版本未进入冻结记录。

### 2.2 Official Repositories

| 官方仓库 | 固定revision / license | 直接读取文件与SHA-256 | 本页实际支持 | 不支持 |
| --- | --- | --- | --- | --- |
| [charlesq34/pointnet2](https://github.com/charlesq34/pointnet2/tree/42926632a3c33461aebfbee2d829098b30a23aaa) | `42926632...`；2018-11-20；MIT | `README.md D648976B0E5083F9FC7D244417C667CDE5E3FD13B9ADEA5AD1C4F1357ADA4D4C`；`LICENSE 0E37D31E1E6A1BF82E95E4EC5B6A4B5979377BB0E1A58F3A7FBC794CD6D51EE0`；`pointnet_util.py A87D411C3CF055F6E043A5D0010192950547FFDE0E3E8980D4DC6BAE596A2EB6`；`pointnet2_cls_ssg.py CA710257B06200C908713143C6043233188CB8FB40D3027CF54C6FB9AD486D8F` | `farthest_point_sample`、`query_ball_point`、`sample_and_group`、512/128 centroids与radius/nsample配置 | PyTorch/现代CUDA parity、本地训练或实时性 |
| [open-mmlab/OpenPCDet](https://github.com/open-mmlab/OpenPCDet/tree/233f849829b6ac19afb8af8837a0246890908755) | `233f8498...`；2025-10-08；Apache-2.0 | `README 70A23F56F41D75834A18E4CFD61C9B3AEDB0BD8FB85BB1C709265E8A0A785FFA`；`LICENSE C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4`；`mean_vfe.py 30122ECE7D713E9F367BBD5DF09A67D39DB16CEE9DF3758DD60853E096D91829`；`spconv_backbone.py AC4A16B511A07DE02712B7334F5FF6C3EAC647BADC5B4505F1B83202261EA9CF`；`height_compression.py 5897131B5341DDFC4A7239F30D09007EEC97F4DBA69C17D2792CC76EF2EDA2A5`；`pointpillar_scatter.py 012294A481F91C2D63246E04E88AFF30EDF963B9CBDD2C7BB132B3B3BF7E8AFC`；`pointpillar.yaml 170A9FFE76CFD8509D1044CFBCF1CBD44C5D320FDA81BF0089A8D5EFAF1C91C8` | mean/count reduction、SubM/SparseConv3d、`N,C,D,H,W→N,C·D,H,W`、pillar scatter、range/voxel/max-point config | VoxelNet/PointPillars论文官方唯一实现、用户项目已有这些模块 |
| [NVIDIA/MinkowskiEngine](https://github.com/NVIDIA/MinkowskiEngine/tree/02fc608bea4c0549b0a7b00ca1bf15dee4a0b228) | `02fc608b...`；2023-03-22；MIT | `README 75AB02E4A6B3E677CDEE39B6E4F15C2C76A62324E124213E7F8E0917E61408AD`；`LICENSE B86CBD537380CCCC7914C37CC1600798BC27E49863B7CFBA500EAFB00120A621`；`quantization.py F70F60F2F38C6DC45AF2CCD8030CF4B7D7CFEBCD72997C3D5661B216D848BD15`；`MinkowskiConvolution.py E70F7F92655E0406AB5BB6BF9FF45C7EC120F0C9E174D69FABD9F3BFDA26BBAC` | coordinate quantization、unique/inverse map、coordinate manager与generalized sparse convolution接口 | 当前硬件性能、下游任务收益、无量化碰撞 |
| [mit-han-lab/bevfusion](https://github.com/mit-han-lab/bevfusion/tree/326653dc06e0938edf1aae7d01efcd158ba83de5) | `326653dc...`；2024-07-31；Apache-2.0 | `README DC44DB55ED48EDA88AFCFCFDC0E1C9D75DCCC2ED3F803C330A93E0842C5BB99C`；`LICENSE 02C5C55E19772184872C6C455553B15E4ACAC4B3A757550E7374F47723868CE1`；`vtransforms/base.py 47E22A6A08689893CAF428EA7CB7220A8E958BC518CE4F1D09C9826B20C3E44B`；`fusers/conv.py 7D2DE3CB072DE5CE0E3F8E75BCA53583C517E68CB8D78801378CD980EE6DE7AC`；`bevfusion.py 94CEF3B3BAF2C1A0C1D9ADA03B4B48E8E39B0C0A0B9C5DE29259D409FA217A91`；`pointpillars.yaml 53B0DF8908A1DF37E18F39E9319B751C2562405FA57EA1F277307F683A528B11` | BEV pooling、conv fuser、hard/dynamic voxelization、pillar config | 未绑定sensor/camera artifact的即插即用融合 |
| [autonomousvision/occupancy_networks](https://github.com/autonomousvision/occupancy_networks/tree/406f79468fb8b57b3e76816aaa73b1915c53ad22) | `406f7946...`；2021-05-07；MIT | `README C411DA58F379E4F624C68E64C25A2BA3B92E51E40776E0D5293FDD290CFBFEA5`；`LICENSE.md 27600DDA527C00A7763B14C2478931236E01EF1D862DF70D4B66508E56560B1B`；`decoder.py A23469EE76F6974FE54069494440550D0832286E98EE1C3A9886146498F7D9A2`；`generation.py CE3B27C95F7B0541C72F7DDBC078B005B7D8DC65D954A53DFAE5BCFECAE0015E`；`mise.pyx C272EF3FBCFE738441F525093C3EF40851EA15D9B11B6BF2D1FD81CD10E7399F` | occupancy decoder、0.5 threshold、logit threshold转换与MISE resolution | OctoMap sensor update、导航free-space语义或本地模型 |
| [OctoMap/octomap](https://github.com/OctoMap/octomap/tree/f012f5f0a4f58cad19501833f9c0ea9d864427b6) | `f012f5f0...`；2026-02-08；New BSD | root `README 64DA9308BD1D94841E4F5BB88D6316C52EE83C8641CA0B7924961ABFF76C0276`；library `README 6E5328B11CCC0DAD00FECB77FEA0567610CFBADD38BFB255A4F8C12070ECAD08`；`LICENSE 8A9CE1EADC1DD0FC4EE57A6016CB40EDDC7003D2DA824C58D55463F2B9CEB4CA`；`AbstractOccupancyOcTree.h 0BB74048227B863DC5B757933C967C88F6DC6160C46CBD5F4321A3E8A260F0A5`；`OccupancyOcTreeBase.h E0E6AD4EA2376732923F2462EC22809F59BB6C94ADD681B5624D0D44A5B628D0`；`.hxx 1D34FC3B704038E0F332BEB820D765ADAD1FA870485333CA23E885F8C62A7903` | octree resolution、hit/miss log-odds、clamping、ray-derived free/occupied cells、unknown-as-unallocated boundary | learned implicit occupancy、local OctoMap integration或候选人ownership |

文件SHA是固定commit的Git blob原始字节SHA-256；仓库commit date来自`git show -s --format=%cI`。代码license不自动覆盖模型权重、dataset、CUDA/spconv等依赖。

### 2.3 Repository-reviewed Bridges

| 本地入口 | Canonical SHA-256 | 可复用 | PER-013不重复 |
| --- | --- | --- | --- |
| [PER-002 3D Lift / Frame Source Freeze](vol_06_per002_3d_lift_frame_source_freeze.html) | `A91A32ECA547738C0CC76895F299DFAE49EA134FD54944DC9EB538FBA1228B93` | metric depth、intrinsics、backprojection、TF/frame/time | 不重讲投影公式与camera calibration |
| [PER-003 Multi-view / Temporal Source Freeze](vol_06_per003_multiview_temporal_source_freeze.html) | `A62FBEA8507FF46C9636F0CB3280516546F4F01A3D02EBE777B55877F9338E19` | camera/frame/time/presence/age | 不把representation choice写成fusion完成 |
| [PER-012 Segmentation / Depth / Keypoint / Affordance Source Freeze](vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html) | `2310D4EBF42F838B615E5BB8E8F2F7E37A14C735A2E983162B1A6B0E43854D83` | mask-conditioned metric surface、keypoint/affordance接口 | 不重讲2D dense model与action proposal |
| [PER-004 Navigation Artifact Gate](../evidence/projects/per004_navigation_artifact_gate.html) | `CEE9C3117741840AE701B09C4429923C471B50AD0AB24F8CE721342DC560F295` | 五项目没有local-direct VLN/ObjectNav episode bundle | 不把地图文件推成个人导航成功率 |

## 3. 节点边界与不可合并项

| 相邻节点 | 已负责 | PER-013只新增 |
| --- | --- | --- |
| PER-002 | pixel→camera/base 3D、calibration、TF | 已有3D samples如何编码与稀疏化 |
| PER-003 | multi-view/time identity、fusion时序合同 | representation artifact保留哪些source/time字段 |
| PER-008 | point/box/mask/keypoint/affordance的downstream sufficiency | point cloud/voxel/BEV/occupancy内部结构与转换损失 |
| PER-012 | metric-depth surface、semantic keypoint、affordance proposal | surface→point/voxel/BEV/occupancy representation |
| PER-014 | 3D semantic/open-vocabulary grounding | 本页不产生language-region binding或3D box答案 |
| PER-015 | reachability、IK、collision、controller gate | 本页不从occupancy或BEV推出可执行动作 |
| PER-016 | SLAM/localization/map drift | OctoMap仅作representation exemplar，不展开SLAM闭环 |

## 4. Typed 3D Representation Manifest

最小artifact必须包含：

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
  "sampling": {"method": "fps | random | cap", "seed": 0, "budget": 4096},
  "aggregation": "max | mean | vfe | sparse_conv",
  "empty_unknown_policy": "unknown != free",
  "model_revision": "sha256:...",
  "validity_and_age": {"valid_ratio": 0.0, "age_ms": 0}
}
```

只有`tensor.shape`没有frame、origin、resolution、range与axis，无法判断同一index对应的物理位置；只有point count没有sampling seed/order与feature schema，无法复现实验。

## 5. Point Set 与 PointNet++合同

Point set通常写作\(\mathcal P=\{(\mathbf x_i,\mathbf f_i)\}_{i=1}^{N}\)，其中\(\mathbf x_i\in\mathbb R^3\)是连续坐标，\(\mathbf f_i\)可含颜色、强度、法向、时间或learned feature。点顺序本身不应成为几何语义，但采样、邻域与pooling仍会引入实现选择。

PointNet++ set abstraction可写成：

\[
\mathbf h_j=\operatorname{POOL}_{i\in\mathcal N(\mathbf c_j)}
\phi\!\left([\mathbf x_i-\mathbf c_j,\mathbf f_i]\right).
\]

变量解释：\(\mathbf c_j\)是FPS centroid，\(\mathcal N\)由ball query或kNN定义，\(\phi\)是shared PointNet/MLP，POOL通常为symmetric reduction。直觉是先选覆盖中心，再在metric neighborhood内摘要local geometry。实现映射：固定PointNet++代码先`farthest_point_sample`，再`query_ball_point/group_point`；SSG model明确使用`512,r=.2,K=32`与`128,r=.4,K=64`。

不能省略的身份：input order policy、FPS初始点/seed、radius、K、empty/duplicate neighbor处理、normalization、feature schema、pooling和density augmentation。

## 6. Sampling、Density 与Coverage

| 方法 | 保留逻辑 | 主要优点 | 主要风险 |
| --- | --- | --- | --- |
| random sampling | 固定seed随机取budget | 简单、可作stochastic augmentation | 稀疏区域漏采、run variance |
| FPS | 迭代选离已选集合最远点 | 固定budget下覆盖更均匀 | \(O(NM)\)或近似代价、起点/metric敏感 |
| ball query | 固定radius，最多K点 | 保留metric scale | density变化导致neighbor count变化 |
| kNN | 固定K | tensor shape稳定 | metric radius随density漂移 |
| voxel cap | 每voxel最多T点 | 限制memory/imbalance | dense voxel截断、seed与排序偏差 |
| dynamic voxel | 不固定T，按coordinate scatter | 减少hard cap | reduction/collision和kernel实现仍需冻结 |

固定probe在1D点`[0,1,2,10]`、起点0、budget2上得到FPS index `[0,3]`、coverage radius `2`；固定“随机”样本`[0,1]`的coverage radius为`9`。这只证明该probe的coverage差异，不证明FPS对所有task accuracy更高。

## 7. Voxelization 与量化边界

对origin \(\mathbf o\)、voxel size \(\mathbf v\)：

\[
\mathbf q_i=\left\lfloor
\frac{\mathbf x_i-\mathbf o}{\mathbf v}
\right\rfloor.
\]

变量解释：\(\mathbf q_i\)是integer voxel coordinate；range外点、负坐标floor、边界归属与axis order都必须固定。直觉是规则index换来规则邻域，但付出quantization。实现映射：Minkowski量化代码明确先对负坐标floor并返回unique/inverse map；OpenPCDet config同时冻结`POINT_CLOUD_RANGE`、`VOXEL_SIZE`、`MAX_POINTS_PER_VOXEL`与train/test max voxels。

`x=0.99/1.01`、voxel size 1、origin 0的index分别为0/1；仅平移0.02就跨cell。若训练/评估frame、origin或浮点rounding不同，tensor会发生离散跳变。

## 8. VFE、Pooling Collision 与Information Loss

VoxelNet把每个non-empty voxel的点做VFE；固定OpenPCDet `MeanVFE`则直接：

\[
\mathbf f_v=\frac{1}{\max(n_v,1)}
\sum_{i\in v}\mathbf f_i.
\]

变量解释：\(n_v\)是valid point count。均值是可复现baseline，但集合`[0,2]`与`[1,1]`均得到1；若不同时保存count/higher moments/local offsets，就发生alias。Max pooling、learned VFE也会丢信息，只是碰撞形式不同。

VoxelNet固定论文还在超过T点的voxel内random sample；所以“同一point cloud”若seed、input ordering、T不同，voxel tensor与gradient可能不同。

## 9. Sparse Tensor 与Sparse Convolution

Minkowski式sparse tensor由active coordinates \(\mathcal C\)与features \(\mathcal F\)组成，batch index也是coordinate的一部分。一般化sparse convolution可抽象为：

\[
\mathbf y_{\mathbf u}=
\sum_{\mathbf k\in\mathcal K(\mathbf u,\mathcal C_{in})}
\mathbf W_{\mathbf k}\mathbf x_{\mathbf u+\mathbf k}.
\]

变量解释：只对kernel region与active input coordinate的交集累加；output coordinate set、stride、submanifold或regular sparse convolution会改变active pattern。实现映射：OpenPCDet同时使用`SubMConv3d`、`SparseConv3d`与`SparseInverseConv3d`；不能统称一个“sparse conv”。

Sparse效率取决于active ratio、coordinate-map构建、kernel map、feature width、batch与硬件。量化坐标或kernel map开销可能在小场景主导，因此“稀疏一定更快/更省”是危险答案。

## 10. Pillar、BEV 与Height Compression

PointPillars固定论文把点按vertical columns组织，PointNet编码后scatter回2D pseudo-image。OpenPCDet KITTI config使用range z `[-3,1]`与voxel z size `4`，因此z只有一个spatial bin；`z=-2.5`和`0.5`共享pillar index。这里是z的空间离散维被折叠，不等于per-point z feature必然消失。

另一条OpenPCDet `HeightCompression`路径将dense tensor：

\[
[N,C,D,H,W]\longrightarrow[N,C\cdot D,H,W].
\]

变量解释：D被reshape进channel，仍可能携带height-slice信息；后续2D卷积是否能利用它需要实证。BEV必须冻结map/base frame、x/y axis、origin、meters-per-cell、range、z aggregation、rotation augmentation和validity。

## 11. BEVFusion：共享平面不是自动对齐

固定BEVFusion代码包含camera view transform→BEV pooling、LiDAR hard/dynamic voxelization、conv fuser与shared-BEV head。论文的关键点是不同sensor先映射到同一BEV坐标，再融合；不是把未经校准的feature按array index相加。

至少需要：camera intrinsics/extrinsics、LiDAR-to-ego、ego/map pose、augmentation matrix、depth/view-transform bins、BEV grid origin/range/resolution、timestamp和sensor validity。论文的nuScenes/Waymo/KITTI结果不能直接作为桌面manipulation或本地VLA收益。

## 12. Occupancy三类合同

| 类型 | 表示 | unknown/free | 典型用途 | 主要风险 |
| --- | --- | --- | --- | --- |
| dense/sparse occupancy grid | cell→state/probability/logit | 必须显式编码 | collision/map/scene completion | resolution memory、unobserved误当free |
| probabilistic octree | allocated octree node+log odds | 未分配通常unknown | 多分辨率mapping/raycast | sensor model、clamp/threshold、stale map |
| implicit occupancy | \(o_\theta(\mathbf p,\mathbf z)\in[0,1]\) | 是classifier语义，不自动含ray-free | reconstruction/surface query | query cost、threshold、calibration、动态场景 |

OctoMap代码把hit/miss转换成log odds并clamp，可抽象为：

\[
L_t(n)=\operatorname{clip}\!\left(
L_{t-1}(n)+\lambda(z_t,n),L_{min},L_{max}
\right).
\]

变量解释：ray上的free cells与endpoint occupied cells使用不同update；node只有达到occupancy threshold才叫occupied。未观测node没有free evidence。实现映射：固定代码先`computeUpdate`得到`free_cells/occupied_cells`，再分别`updateNode(..., false/true)`。

Occupancy Networks定义：

\[
o_\theta:\mathbb R^3\times\mathcal Z\rightarrow[0,1],
\qquad
\mathcal S_\tau=\{\mathbf p\mid o_\theta(\mathbf p,\mathbf z)=\tau\}.
\]

变量解释：\(\mathcal S_\tau\)是classifier decision boundary；固定generation代码默认probability threshold 0.5并转成logit 0。若threshold改0.7，logit为0.8473，surface会变。MISE减少dense queries，但不提供sensor ray、dynamic occupancy或collision certification。

## 13. Memory / Compute Scaling

Dense grid feature memory下界：

\[
M_{dense}=N_xN_yN_z\,C\,b.
\]

变量解释：\(b\)是每feature bytes，尚未计gradient、activation、optimizer、indices与framework overhead。`200^3×64×4`为2,048,000,000 bytes，约1.907 GiB；若active ratio 1%，仅feature约19.53 MiB，但sparse coordinates/kernel maps/allocator overhead另计。

降低resolution会影响thin structure、surface thickness、collision margin和small-object recall；扩大range会立方级增加dense cells。必须同时报告range、resolution、active count/ratio、points kept/dropped、latency分位数与memory peak。

## 14. Conversion Loss 与Downstream Sufficiency

```text
metric points
  -> sample/group                    # may drop sparse regions
  -> quantize + aggregate            # boundary collision / cap / alias
  -> sparse 3D features               # coordinate-map and kernel contract
  -> pillar or height compression     # z as feature/channel/spatial loss differs
  -> BEV fusion                       # requires calibrated common frame
  -> occupancy prediction/map         # unknown/free/occupied semantics
  -> PER-014 semantic 3D grounding
  -> PER-015 reachability/collision/controller gate
```

Representation choice由downstream query决定：surface contact需要local geometry，navigation collision需要free/occupied/unknown和robot footprint，language grounding需要semantic identity，控制还需time/uncertainty。一个BEV feature map不能自动满足全部查询。

## 15. Objective 与Metric边界

| 输出 | 可报告的representation诊断 | 不等价于 |
| --- | --- | --- |
| sampled points | coverage radius、retention、density strata | task accuracy、unbiased sampling |
| voxel/pillar | active voxels、collision/cap/drop ratio、quantization residual | 3D detection/action success |
| sparse features | active pattern、memory/latency、parity | always faster、semantic correctness |
| BEV | geometric roundtrip、cell occupancy/feature coverage、sensor validity | calibrated fusion或robot navigation |
| explicit occupancy | observed-cell IoU/free-space error、unknown coverage | implicit surface quality、collision safety |
| implicit occupancy | occupancy IoU、Chamfer/F-score、query cost | ray-consistent free space、dynamic map |

所有数字必须绑定dataset/split、frame/range/resolution、sampling seed、aggregation、threshold、observed denominator与hardware。只报“voxel size 5cm”或“occupancy IoU”无法比较。

## 16. Deterministic Probes

| Probe | 固定输入 | 结果 | 结论边界 |
| --- | --- | --- | --- |
| FPS coverage | `[0,1,2,10]`，start0，budget2 | FPS `[0,3]` radius2；fixed random `[0,1]` radius9 | 该例coverage，不证明普遍accuracy |
| voxel boundary | x=0.99/1.01，v=1，origin0 | index 0/1 | 0.02平移可改变离散tensor |
| mean alias | `[0,2]` vs `[1,1]` | mean均为1 | aggregation需count/offset/variance等补充 |
| dense/sparse memory | `200^3,C=64,float32` | dense 1.907GiB；1% feature 19.53MiB | 未计sparse overhead |
| pillar z collapse | range[-3,1]，dz=4，z=-2.5/0.5 | z index均0 | spatial z bin相同，不等于z feature全丢 |
| implicit threshold | probability .5/.7 | logit 0/0.8473 | threshold是surface identity |
| local pixel/world | pixel(100,200)，H2543，res0.0199977 | world(-48.92593,35.5881134) | local map transform可复算；不证明地图准确 |
| local PCD header | frozen `world.pcd` | 54,856点；x/y/z/intensity/timestamp/ring | 是asset schema，不是encoder/runtime |
| local path census | Harness tracked text high-signal 86 files | 78 third_party、4 data、4 first-party docs/bridge/tests | third-party存在不等于个人实现 |

## 17. 本地五项目Audit

五份canonical Claim–Evidence Inventory对`point cloud/pointcloud/voxel/BEV/occupancy/OctoMap/LiDAR/Minkowski/3d point`的高信号term scan均为0：

| Inventory | Canonical SHA-256 | 安全含义 |
| --- | --- | --- |
| [OPD Inventory](../evidence/projects/opd_claim_evidence_inventory.html) | `C002B2275EB1F747E1E6F383CB271539F081AE8CCEE0C8D11AFC92EBABE99AFA` | inventory未登记3D representation claim |
| [OpenPiVLA Inventory](../evidence/projects/openpivla_claim_evidence_inventory.html) | `13023578D1B7343083BEB588C7F8CE7B1BDC267E2BC834204D309106E8EA132A` | image/language/action evidence不自动含3D encoder |
| [Robot Harness Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) | `71C3B62F52204574C1B854B554258DABC1856F5D9044EB9628280A32500A797F` | 既有inventory未登记地图/PCD representation claim；direct repo exception见下表 |
| [WAM Inventory](../evidence/projects/wam_claim_evidence_inventory.html) | `2362311B8D90A5B82D9D2D6333F5D376625CF2311DD7A3921F42B339BB55AFB4` | camera/world-model artifact不自动含point/voxel/occupancy |
| [UWM Inventory](../evidence/projects/uwm_libero_claim_evidence_inventory.html) | `C35C41D6248E3B072E9181F4AD3AAFA423631D74604207CB5AB65352105DD8A9` | image/action/video world model不自动含3D representation |

### 17.1 Robot Harness Direct Exception

`C:\Users\mousongzhe\agent@3f4c8b3a11ff9512bc18ec4a331ae5ea01555f49`直接读取：

| 文件 | SHA-256 / schema | 直接支持 | 不支持 |
| --- | --- | --- | --- |
| `docs/full-scenario-simulation.md` | `30E2221378417E26A3934A9FF590A085E5654DE9810C84E38F0ED1CF7CB22800` | 文档描述2D occupancy、PCD引用、heightmap/A*与lightweight WebUI | 运行时等价、个人ownership或3D encoder |
| `server/sim/ros2_bridge.py` | `8291D64DE01AAC2EFDF52409008EFD7AE18C5FEC0BA7B9D4677F6636F8287A48` | occupancy/pointcloud path、existence ready flag、URL暴露 | 读取PCD feature、voxelize、sparse conv或learned occupancy |
| `occupancy2d_map.json` | `40A2CE540AC214CABA987BB2BCF3542B197207A9F25D96298C2E65167808EA37` | 0 occupied/127 unknown/255 free、约0.02m、origin/range/pixel→world | OctoMap log-odds、动态更新、地图accuracy |
| `occupancy2d_map.png` | `C41880F676BF5B2FCA24FB528E14A056B55256E07FD949107F1227E073A56D4F` | 2D raster artifact存在 | 3D occupancy或semantic BEV |
| `pointcloud_map/grid_map/world.pcd` | `494A53320AF2EC10C4D1AADD17CE0F7D943820BA34536C23871BB5CA711F0B42`；54,856 points；fields `x y z intensity timestamp ring` | PCD asset与schema | candidate-created map、encoder、online stream或model result |

文本grep的86个高信号tracked files中78个位于`third_party/`；其存在只说明vendored/reference code。第一方可见部分是3个map JSON、state JSON、scenario doc、bridge与两份tests。Git commit/author仍不能替代候选人逐文件ownership确认。

### 17.2 OPD “Point Cloud”不是3D Point Cloud

`muxi@756e27e...`的四处`point cloud(s)`命中指2D标注点集合经min/max x/y加margin转box或prompt文字；没有z、frame、PCD、voxel、BEV或occupancy tensor。因此不能把OPD region/semantic-nav data builder称为3D point-cloud pipeline。

## 18. Project Truth Boundary

| 项目 | 当前可以讲 | 当前不能说 | 补强Artifact |
| --- | --- | --- | --- |
| Robot Harness | 2D tri-state occupancy asset、PCD file/schema、path/URL bridge与文档化planner接口 | 自研PointNet/voxel/BEV/OctoMap、online 3D perception、真实机器人收益或个人ownership | map generator revision、PCD ingest/voxel code、ROS bag、TF/time、planner trace、ownership |
| OPD | 2D point-set→box data conversion | 3D point cloud、voxel/BEV/occupancy或robot闭环 | z/frame/timestamp/schema、3D model/checkpoint/raw eval |
| OpenPiVLA | end-to-end image/language/action可与显式3D intermediate对照 | 已集成3D encoder或其带来97.4 | local module/config/checkpoint/ablation/episodes |
| WAM | future image/world model可作geometry diagnostic候选 | learned occupancy/BEV head或其提升 | local head/loss/config/raw prediction/matched eval |
| UWM | image/action/video world-model与LIBERO protocol | point/voxel/occupancy模型或3D泛化 | exact model diff、3D dataset、checkpoint与same-protocol rollout |

公共论文/代码证明representation mechanism，不证明本地集成；地图/PCD文件证明asset存在，不证明生成、学习、在线更新、效果或候选人ownership。

## 19. Fail-closed Pseudocode

```python
def encode_3d(points, manifest, cfg):
    # 1. Reject geometry without an explicit physical frame and unit.
    require(manifest.frame and manifest.unit == "meter")
    require(manifest.origin and manifest.range and manifest.timestamp_range)

    # 2. Sampling is part of artifact identity, not a hidden dataloader detail.
    sampled, sample_idx = sample_points(
        points,
        method=cfg.sampling_method,
        budget=cfg.point_budget,
        seed=cfg.seed,
    )

    # 3. Quantization must preserve range/origin/axis and report collisions/drops.
    coords = floor((sampled.xyz - cfg.origin) / cfg.voxel_size)
    valid = inside_range(coords, cfg.grid_shape)
    unique, inverse, counts = unique_coordinates(coords[valid])
    audit = report_collision_cap_drop(coords, unique, counts, valid)

    # 4. Keep representation semantics explicit.
    if cfg.representation == "sparse_voxel":
        features = aggregate(sampled.features[valid], inverse, cfg.aggregation)
        return SparseTensor(unique, features), audit
    if cfg.representation == "pillar_bev":
        pillars = aggregate_by_xy(sampled[valid], cfg)
        return scatter_to_bev(pillars, cfg.bev_frame), audit
    if cfg.representation == "occupancy":
        # Unknown cells must not silently become free.
        return update_occupancy(sampled, sensor_origin=manifest.sensor_origin), audit
    raise ValueError("unfrozen representation")
```

这是面试/实现目标合同，不是本地项目已有代码。真实系统还需sensor model、calibration、TF/time、dynamic objects、uncertainty、memory/latency与downstream action/evaluation。

## 20. Source Gate 与下一Slice

本页达到source-freeze条件：

- 六篇primary paper均固定版本、完整PDF SHA并读取method正文；
- 六个official repo固定commit/date/license，32个关键文件逐字节SHA；
- point/FPS/grouping、voxel/aggregation、sparse convolution、pillar/BEV、probabilistic/implicit occupancy合同分离；
- 九个deterministic probe固定输入与结果；
- 五份项目inventory与Robot Harness direct exception逐文件核对；
- 2D occupancy/PCD asset、third-party code、local model integration、robot result与ownership保持分层。

仍为`WARN`，因为本地没有3D model/checkpoint、online PCD ingestion/voxelization、frame/time manifest、raw tensors、matched representation ablation、same-protocol downstream result、planner/controller episode或候选人ownership确认；OctoMap论文PDF未进入本轮冻结，OctoMap机制只引用固定official code与项目说明。

`VLA-PER-001..013` source/knowledge/card保持同步，264张题卡全部`unseen`。下一bounded slice只冻结`VLA-PER-014` 3D semantic/open-vocabulary grounding source；不生成其knowledge/card，不创建`coaching_state.md`，不改变mastery。

## References

1. Qi et al., [PointNet++ v1](https://arxiv.org/abs/1706.02413v1)；[official code@4292663](https://github.com/charlesq34/pointnet2/tree/42926632a3c33461aebfbee2d829098b30a23aaa)。
2. Zhou & Tuzel, [VoxelNet v1](https://arxiv.org/abs/1711.06396v1)。
3. Lang et al., [PointPillars v2](https://arxiv.org/abs/1812.05784v2)。
4. Choy et al., [Minkowski ConvNet v4](https://arxiv.org/abs/1904.08755v4)；[MinkowskiEngine@02fc608](https://github.com/NVIDIA/MinkowskiEngine/tree/02fc608bea4c0549b0a7b00ca1bf15dee4a0b228)。
5. Liu et al., [BEVFusion v3](https://arxiv.org/abs/2205.13542v3)；[official code@326653d](https://github.com/mit-han-lab/bevfusion/tree/326653dc06e0938edf1aae7d01efcd158ba83de5)。
6. Mescheder et al., [Occupancy Networks v2](https://arxiv.org/abs/1812.03828v2)；[official code@406f794](https://github.com/autonomousvision/occupancy_networks/tree/406f79468fb8b57b3e76816aaa73b1915c53ad22)。
7. [OpenPCDet@233f849](https://github.com/open-mmlab/OpenPCDet/tree/233f849829b6ac19afb8af8837a0246890908755)。
8. [OctoMap@f012f5f](https://github.com/OctoMap/octomap/tree/f012f5f0a4f58cad19501833f9c0ea9d864427b6)。
9. [PER-002 3D Lift / Frame](vol_06_per002_3d_lift_frame_source_freeze.html)、[PER-003 Multi-view / Temporal](vol_06_per003_multiview_temporal_source_freeze.html) 与 [PER-012 Segmentation / Depth / Keypoint / Affordance](vol_06_per012_segmentation_depth_keypoint_affordance_source_freeze.html)。
10. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) 与固定`agent@3f4c8b3` direct files。
