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
| `shushu-internship-tool` | https://github.com/Sunanzhe2004/shushu-internship-resume-optimizer/tree/main/skills/shushu-internship-tool | Turn messy internship materials, code repos, project summaries, and business docs into resume achievements, STAR notes, interview Q&A, and risk checks. | Strong practical fit for converting scattered project evidence into usable resume material. |
| `bigtech-interview-project-upgrader` | https://github.com/YingaoWang-casia/shushu-ProjectProof/tree/main/skills/bigtech-interview-project-upgrader | Diagnose weak or toy-like projects, define truth boundaries, map projects to JD needs, and build interview-ready project narratives. | Good "project proof officer" for small-company, AI, Agent, RAG, backend, frontend, data, and algorithm projects. |
| `job-fit-analyzer` | https://github.com/dj-chow/job-fit-analyzer/tree/master/skill | Analyze actual candidate-to-role fit from resume, LinkedIn, and JD, separating screening gates from real capability fit. | Useful before spending time tailoring a resume for a role. |
| `interview-coach` | https://github.com/noamseg/interview-coach-skill | Persistent interview coaching system with storybank, mock interview, transcript analysis, prep, pitch, resume, LinkedIn, outreach, and progress tracking commands. | Best as a longer-running coaching workspace. Writes/updates local `coaching_state.md` when used. |

## Local-Only Installs

| Skill | Source | Reason |
| --- | --- | --- |
| `resume-polish` | https://github.com/goyalsandeep2k/resume-polish | Installed locally into `C:\Users\mousongzhe\.codex\skills\resume-polish`, but not committed here because the source repository has no license file. |

## Recommendation Order

1. `bigtech-interview-project-upgrader`: audit whether each project can survive big-tech interview follow-ups.
2. `shushu-internship-tool`: turn messy project/internship materials into bullets, STAR notes, Q&A, and risk lists.
3. `job-fit-analyzer`: decide whether a JD is worth tailoring for, and identify screening blockers.
4. `jd-cv-grill`: tailor the strongest evidence to a concrete JD through focused follow-up questions.
5. `llm-intern-skill`: use when the role is specifically LLM, RAG, Agent, post-training, multimodal, or AI algorithm internship.
6. `vibe-resume-editor`: turn the chosen content into a polished one-page HTML/PDF resume.
7. `interview-coach`: use after the resume is plausible, when the next bottleneck is storybank, mock interviews, transcript analysis, or long-term practice.
8. `timeline-polishing` + `resume-generation`: adopt when you want a long-term resume-as-code workflow.

## Security Review

Static review was performed before deployment. No repository scripts were executed during review.

| Skill / Repo | Review Result |
| --- | --- |
| `llm-intern-skill` | Standard root `SKILL.md`. No automatic credential access or application submission was found. Contains LaTeX templates and a FontAwesome helper shell script that can remove and recreate a temporary font directory and clone FontAwesome if manually run; normal skill use does not require executing it. License: MIT. |
| `jd-cv-grill` | Standard root `SKILL.md`. Prompt-only workflow with no bundled scripts. No automatic network, credential, or submission behavior found. License: MIT. |
| `get-job` | Standard root `SKILL.md`. Includes local helper scripts for DOCX resume rendering and output quality checks. No upload, credential, or automatic application behavior found. Uses WebSearch by design during role research. License: CC BY-NC-ND 4.0. |
| `vibe-resume-editor` | Skill lives under `skills/vibe-resume-editor`. The parent template can run `npm install` and Playwright-based PDF export if used, but the deployed skill directory itself is prompt-only. License: MIT. |
| `resume-as-code` | Parent repo contains Node/pnpm tooling, but the deployed content is limited to the three skill directories under `skills/`. These skills write local YAML/Markdown artifacts and may call for web research during JD/company analysis. License: MIT. |
| `shushu-internship-tool` | Skill lives under `skills/shushu-internship-tool`. Includes local Python scripts for achievement audit, resume ranking, document knowledge extraction, repo audit, candidate scoring, and interview pack generation. Static review found no external dependencies, network requests, credential access, or automatic application behavior. Scripts read local files and write local reports. License: Apache-2.0. |
| `bigtech-interview-project-upgrader` | Skill lives under `skills/bigtech-interview-project-upgrader`. The repository includes an `install.sh` that can clone/download the repo and replace the local skill directory; that installer was not executed. Only the reviewed pure skill directory was copied. License: Apache-2.0. |
| `job-fit-analyzer` | Skill lives under `skill/`. Prompt/reference-only workflow with no bundled executable scripts in the deployed directory. Requires resume, LinkedIn, and JD inputs before analysis. License: MIT. |
| `interview-coach` | Standard root `SKILL.md` with references. Prompt/reference-only workflow; no bundled executable scripts. It intentionally writes local coaching state (`coaching_state.md`) during use to preserve session continuity. License: MIT. |
| `resume-polish` | Single `SKILL.md`, prompt-only. No bundled scripts, but the source repository has no license file, so it was installed locally only and not committed to this repository. |

## Source Revisions

| Repo | Commit Reviewed |
| --- | --- |
| `couragec/LLMInternSkill` | `11db44f57b3d78ae3f83072b3959cd7a5d85df0b` |
| `mikezhangyl/jd-cv-grill` | `8c7875e9cbb9582fb0d61212323b63d8e9a14779` |
| `agentenatalie/get-job.skill` | `d60161842fe308bc8c609a9bb806c00caa326d61` |
| `LiuMengxuan04/vibe-resume` | `f98ed66c7a8e30bc279b3b97c107461fc2cbb7d2` |
| `zhiweio/resume-as-code` | `5d1b7e6208a250215aac1d2d986b86f9c1fbe716` |
| `Sunanzhe2004/shushu-internship-resume-optimizer` | `2a40944ccdf9233cf47ffee9792862246c58b5df` |
| `YingaoWang-casia/shushu-ProjectProof` | `28481d553feea024561b9b4ac1cf6b7f841eec7c` |
| `dj-chow/job-fit-analyzer` | `054bec9efa48bd51369d77da16432d9fabdfdb66` |
| `noamseg/interview-coach-skill` | `634a8dd8689e0420c21e5f0c8ae3cfa9e1a7ab7e` |
| `goyalsandeep2k/resume-polish` | `c8f9eba69f7d4e44fcd75279c2f9b7e2cc25fd7e` |

## Local Installation

To make these skills available to Codex, copy the desired skill directories into your Codex skills directory:

```powershell
Copy-Item -LiteralPath "C:\Users\mousongzhe\cv\skills\llm-intern-skill" -Destination "C:\Users\mousongzhe\.codex\skills\llm-intern-skill" -Recurse
```

Repeat for each skill you want active, then restart Codex.
