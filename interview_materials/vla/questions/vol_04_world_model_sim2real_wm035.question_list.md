# VOL 04 VLA-WM-035 题卡清单

> 状态：drafted / 1 card / unseen / WARN  
> 更新日期：2026-07-18  
> 边界：只覆盖 WM-035 camera geometry/photometric/temporal/visibility/sensor modeling；WM-036..038 保持 deferred。

## 题卡

| ID | 难度 | 优先级 | 问题 | 证据边界 |
| --- | --- | --- | --- | --- |
| VLA-WM-035 | L2 | P1 | camera intrinsics/extrinsics、exposure、blur、occlusion 与 sensor noise 如何建模？ | OpenCV/MuJoCo official docs + Tobin/OpenAI/ImageNet-C primary papers + WM-032/WM-034/PER-002/Evidence Manifest；无 local complete calibration/capture/camera-DR/real-transfer bundle |

## 覆盖合同

- geometry：K/R/t/distortion/image-space/crop/resize；
- photometric：lighting/exposure/gain/WB/gamma/material/compression；
- temporal：exposure/readout/blur/timestamp/drop/multi-camera sync；
- visibility：occluder/visible fraction/duration/solvability；
- sensor：shot/read/bias/fixed-pattern/quantization/depth invalid；
- consistency：label/K/pose/time transform、rig correlation、validity/rejection；
- 评估：factor/combined/overwide 与 sim/holdout/replay/closed-loop；
- 项目：静态视觉/camera 字段与 C2/C3 camera transfer 证据严格分开。

## 状态与下一入口

- 本题保持 `unseen`；没有候选人口述，不创建 `coaching_state.md`。
- 前置：[WM-035 Source Freeze](../sources/vol_04_wm035_camera_sensor_modeling_source_freeze.html) 与 [WM-035 Knowledge](../knowledge/vol_04_world_model_sim2real_wm035_camera_sensor_modeling.html)。
- 下一 bounded slice 是 `VLA-WM-036` friction/contact/compliance/gripper semantics；不批量生成 WM-036..038。

