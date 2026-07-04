# CV Skills Workspace

This repository collects resume, internship, job-search, and interview-preparation skills for personal use with Codex-compatible agent runtimes.

## Installed Skills

| Skill | Source | Purpose | Notes |
| --- | --- | --- | --- |
| `llm-intern-skill` | https://github.com/couragec/LLMInternSkill | LLM / AI internship resume diagnosis, JD tailoring, evidence audit, interview grilling, and project scouting. | Best first skill for AI internship resume work. Emphasizes truth boundaries and evidence-backed claims. |
| `jd-cv-grill` | https://github.com/mikezhangyl/jd-cv-grill | Bilingual JD-to-CV tailoring with one-question-at-a-time evidence mining, ATS mapping, and recruiter-fit positioning. | Good for targeting a specific JD after the base resume is ready. |
| `get-job` | https://github.com/agentenatalie/get-job.skill | Full job-search workflow: role research, resume rewrite, interview preparation, quality gates, and coverage matrices. | License is CC BY-NC-ND 4.0. Use as-is for personal/non-commercial workflows; do not modify and redistribute. |
| `vibe-resume-editor` | https://github.com/LiuMengxuan04/vibe-resume/tree/main/skills/vibe-resume-editor | Edit a web-to-PDF HTML resume template while keeping one-page PDF output credible and visually stable. | Useful at the final formatting/export stage. |
| `resume-generation` | https://github.com/zhiweio/resume-as-code/tree/master/skills/resume-generation | Generate targeted YAML resumes from structured profile/timeline data and a JD. | Part of `resume-as-code`; best when maintaining long-term structured resume data. |
| `timeline-polishing` | https://github.com/zhiweio/resume-as-code/tree/master/skills/timeline-polishing | Convert raw work/project notes into structured YAML timeline entries. | Use before `resume-generation` to build a reusable master timeline. |
| `interview-preparation` | https://github.com/zhiweio/resume-as-code/tree/master/skills/interview-preparation | Generate role-tailored interview preparation guides from resume, JD analysis, and company analysis. | Use after a tailored resume and JD/company analysis exist. |

## Recommendation Order

1. `llm-intern-skill`: build a truthful AI/LLM internship resume foundation.
2. `jd-cv-grill`: tailor that foundation to a concrete JD and recover missing evidence through focused questions.
3. `vibe-resume-editor`: turn the content into a polished one-page HTML/PDF resume.
4. `timeline-polishing` + `resume-generation`: adopt when you want a long-term resume-as-code workflow.
5. `get-job`: use for complete internship/job-search loops, especially when role research and interview prep are needed together.
6. `interview-preparation`: use for deep interview guides once resume/JD/company analysis artifacts exist.

## Security Review

Static review was performed before deployment. No repository scripts were executed during review.

| Skill / Repo | Review Result |
| --- | --- |
| `llm-intern-skill` | Standard root `SKILL.md`. No automatic credential access or application submission was found. Contains LaTeX templates and a FontAwesome helper shell script that can remove and recreate a temporary font directory and clone FontAwesome if manually run; normal skill use does not require executing it. License: MIT. |
| `jd-cv-grill` | Standard root `SKILL.md`. Prompt-only workflow with no bundled scripts. No automatic network, credential, or submission behavior found. License: MIT. |
| `get-job` | Standard root `SKILL.md`. Includes local helper scripts for DOCX resume rendering and output quality checks. No upload, credential, or automatic application behavior found. Uses WebSearch by design during role research. License: CC BY-NC-ND 4.0. |
| `vibe-resume-editor` | Skill lives under `skills/vibe-resume-editor`. The parent template can run `npm install` and Playwright-based PDF export if used, but the deployed skill directory itself is prompt-only. License: MIT. |
| `resume-as-code` | Parent repo contains Node/pnpm tooling, but the deployed content is limited to the three skill directories under `skills/`. These skills write local YAML/Markdown artifacts and may call for web research during JD/company analysis. License: MIT. |

## Source Revisions

| Repo | Commit Reviewed |
| --- | --- |
| `couragec/LLMInternSkill` | `11db44f57b3d78ae3f83072b3959cd7a5d85df0b` |
| `mikezhangyl/jd-cv-grill` | `8c7875e9cbb9582fb0d61212323b63d8e9a14779` |
| `agentenatalie/get-job.skill` | `d60161842fe308bc8c609a9bb806c00caa326d61` |
| `LiuMengxuan04/vibe-resume` | `f98ed66c7a8e30bc279b3b97c107461fc2cbb7d2` |
| `zhiweio/resume-as-code` | `5d1b7e6208a250215aac1d2d986b86f9c1fbe716` |

## Local Installation

To make these skills available to Codex, copy the desired skill directories into your Codex skills directory:

```powershell
Copy-Item -LiteralPath "C:\Users\mousongzhe\cv\skills\llm-intern-skill" -Destination "C:\Users\mousongzhe\.codex\skills\llm-intern-skill" -Recurse
```

Repeat for each skill you want active, then restart Codex.

