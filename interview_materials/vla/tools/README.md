# Tools

- `render_report.py`：把 canonical Markdown 渲染为自包含的 `ARIS render-html (academic, v1)` 页面，并在 HTML metadata 中写入完整 SHA-256。它只实现本仓库使用的 Markdown 子集；内容修改应先进入 Markdown，再重新渲染。模板固定 warm-paper 配色、serif 正文、260px sticky TOC、900px 响应式断点、MathJax 3 与 Highlight.js `atom-one-light`，并在 inline Markdown 处理前保护完整数学 span。

示例：

```powershell
# Render one canonical source audit into its browser artifact.
python interview_materials\vla\tools\render_report.py interview_materials\vla\sources\vol_04_world_model_foundations_claim_to_code.md interview_materials\vla\sources\vol_04_world_model_foundations_claim_to_code.html
```

renderer 不替代事实审查、浏览器视觉 QA 或 review JSON；这些仍需单独记录。

- `validate_academic_repo.py`：只读全仓静态审计。检查 canonical Markdown 的 HTML/review 三联件、SHA、单 H1、MathJax delimiter、`.formula em`、本地链接；同时检查所有 HTML 的 ARIS academic v1、palette、serif、260px sticky TOC、900px responsive、MathJax、Highlight.js 和 contained overflow，并重算题卡的唯一 ID/unseen 状态；另外核对 `repository_completion_audit.review.json` 的 canonical/triplet 数量、review verdict 分布、README 当前计数和五项目 P0 audit coverage，防止总账本漂移或漏审项目。

```powershell
python interview_materials\vla\tools\validate_academic_repo.py
```

- `audit_robot_harness_raw_bundle.py`：针对 2026-06 Robot Harness 远端同步解包中的超长 Windows 路径，流式校验十套件 × 四模型的 `*.predictions.jsonl`，只输出 SHA、行数、schema 与 ordered-ID/common-support 指纹，不复制 raw outputs。
