# VOL 06 Perception / Grounding / Navigation：PER-013 原子题卡

> 状态：`drafted / card_1_of_1 / WARN`  
> 更新日期：2026-07-20  
> 覆盖范围：`VLA-PER-013`  
> 难度：L3 1 题  
> 优先级：P1 1 题  
> 练习状态：`unseen`  
> 前置知识：[PER-013 Point Cloud / Voxel / BEV / Occupancy Knowledge](../knowledge/vol_06_per013_pointcloud_voxel_bev_occupancy.html)；来源边界见 [PER-013 Source Freeze](../sources/vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html)。

## Point Cloud、Voxel、BEV、Occupancy 与 Sampling

<details class="qa">
<summary><span class="lv lv-l3">L3</span> <span class="freq">P1</span> <b>VLA-PER-013</b> · 点云、voxel、BEV和occupancy怎样选？sampling、量化与unknown语义如何影响下游？</summary>

**面试意图**：判断你能否从downstream query反推3D representation，说明PointNet++ sampling/grouping、voxel quantization/VFE、sparse convolution、pillar/BEV和三类occupancy的机制与损失；同时冻结frame/time/config、metric与本地项目证据边界。

**30 秒回答**：按下游选表示，冻结frame/range/resolution/time。PointNet++以FPS、ball/kNN建层次；voxel量化有边界、碰撞、截断和聚合alias。Sparse未必更快；BEV需说明z与校准。occupancy分grid、octree和implicit；unknown不等于free，更不等于碰撞安全或robot success。

**机制展开（约 2 分钟）**：点集函数可排列不变，但FPS起点、radius/K和voxel cap仍属模型身份。q=floor((x-o)/v)由frame、origin、range、axis定义；MeanVFE使[0,2]与[1,1]碰撞。Sparse tensor含坐标/特征，SubM、stride sparse和inverse conv的active pattern不同，索引也有成本。Pillar折叠z bin但可保留z feature；HeightCompression把D放入channel。BEV需标定、pose和time。grid、OctoMap hit/miss与implicit threshold不可混用；unknown、free、occupied分开，再进grounding与controller。

**诊断 / 证据**：按first-divergence检查source/frame/unit/time→sampling seed/start/budget与density→origin/range/axis/voxel size/floor→collision、max-points/max-voxels与aggregation→layerwise active pattern、latency和peak memory→pillar z feature或height channel→BEV calibration/augmentation/time→occupancy observed/unknown/free/occupied、threshold与staleness→semantic grounding→planner rejection与episode trace。确定性probe至少覆盖FPS `[0,1,2,10]`、voxel 0.99/1.01 boundary、MeanVFE `[0,2]`/`[1,1]` alias、`200^3×64×float32` memory、pillar z collapse和implicit threshold 0.5/0.7。

**项目挂钩**：本地Robot Harness有2D occupancy PNG/JSON，编码0 occupied、127 unknown、255 free；固定`world.pcd`有54,856点和`x y z intensity timestamp ring`字段，bridge只暴露occupancy/pointcloud path、existence flag与URL。它们支持地图资产、PCD schema和接口事实，不支持候选人生成地图、在线读取PCD、实现PointNet++/voxel/sparse/BEV/OctoMap/learned occupancy、获得representation uplift或真实机器人结果。86个高信号tracked文本中78个位于`third_party/`；vendored code与Git身份也不能替代逐文件ownership确认。

**追问树**：PointNet为何permutation-invariant而pipeline仍可能依赖顺序？FPS起点、outlier与复杂度怎样影响结果？ball query和kNN在density shift下分别漂移什么？voxel为何必须绑定origin/range/axis/floor？hard与dynamic voxelization有何差异？MeanVFE和learned VFE为何不等价？SubM、Sparse、InverseConv怎样改变active sites？何时sparse未必更快？pillar是否完全丢z？HeightCompression与pillar有何区别？BEVFusion为何仍需calibration？empty、unknown与observed free如何区分？OctoMap怎样利用ray miss/hit？implicit threshold为何属于surface identity？occupancy IoU为何不等于collision safety？本地Harness究竟支持哪些claim？

**易错点**：把permutation invariance扩大成整个pipeline无序敏感；说FPS总优于random；只报voxel size不报frame/origin/range/axis；把MeanVFE叫VoxelNet；忽略boundary、cap/drop与aggregation alias；声称sparse必然节省99%显存；说pillar完全删除z；把同shape BEV当已校准；把空cell当free；把implicit occupancy score当collision probability；用coverage、IoU或Chamfer替代semantic、navigation和episode metric；把公共论文、third-party code、PCD资产或Git身份升级为个人3D系统。

**危险答案**：说“点云直接丢进PointNet就行”“FPS一定最好”“voxel size相同输入就相同”“sparse一定更快更省”“BEV天然对齐相机和LiDAR”“没有点就是free”“occupancy 0.9即可执行”“Harness已经实现完整3D perception”，却不交代sampling、frame/origin/range/resolution、aggregation、active pattern、calibration/time、unknown policy、controller gate、raw artifact与ownership缺口。

**来源**：[1][2][3][4][5][6][7][8][9][10]　**练习状态**：unseen

</details>

## 参考来源

1. [PER-013 Point Cloud / Voxel / BEV / Occupancy Knowledge](../knowledge/vol_06_per013_pointcloud_voxel_bev_occupancy.html)：typed manifest、representation机制、诊断顺序、项目边界与面试模板。
2. [PER-013 Source Freeze](../sources/vol_06_per013_pointcloud_voxel_bev_occupancy_source_freeze.html)：固定paper/code revision、SHA、license、九个deterministic probes与五项目audit。
3. Qi et al., [PointNet++ v1](https://arxiv.org/abs/1706.02413v1)；[official repository](https://github.com/charlesq34/pointnet2/tree/42926632a3c33461aebfbee2d829098b30a23aaa)。
4. Zhou & Tuzel, [VoxelNet v1](https://arxiv.org/abs/1711.06396v1)；Lang et al., [PointPillars v2](https://arxiv.org/abs/1812.05784v2)。
5. Choy et al., [Minkowski ConvNet v4](https://arxiv.org/abs/1904.08755v4)；[MinkowskiEngine](https://github.com/NVIDIA/MinkowskiEngine/tree/02fc608bea4c0549b0a7b00ca1bf15dee4a0b228)。
6. Liu et al., [BEVFusion v3](https://arxiv.org/abs/2205.13542v3)；[official repository](https://github.com/mit-han-lab/bevfusion/tree/326653dc06e0938edf1aae7d01efcd158ba83de5)。
7. Mescheder et al., [Occupancy Networks v2](https://arxiv.org/abs/1812.03828v2)；[official repository](https://github.com/autonomousvision/occupancy_networks/tree/406f79468fb8b57b3e76816aaa73b1915c53ad22)。
8. [OpenPCDet@233f849](https://github.com/open-mmlab/OpenPCDet/tree/233f849829b6ac19afb8af8837a0246890908755)。
9. [OctoMap@f012f5f](https://github.com/OctoMap/octomap/tree/f012f5f0a4f58cad19501833f9c0ea9d864427b6)。
10. [Robot Harness Claim–Evidence Inventory](../evidence/projects/robot_harness_claim_evidence_inventory.html) 与source freeze中固定的本地map/PCD/bridge artifacts。
