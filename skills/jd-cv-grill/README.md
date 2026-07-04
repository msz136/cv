# JD CV Grill / JD 简历深挖

> Bilingual JD-to-resume skill for tailoring a CV/resume to a job description through evidence-first questioning, ATS keyword mapping, and interview-ready resume bullets.

`jd-cv-grill` helps an AI agent turn a job description into a targeted, credible CV or resume. It guides the agent to interview the candidate one question at a time, extract project evidence, map experience to JD requirements, identify ATS and recruiter keywords, and rewrite resume bullets without fabricating achievements.

`jd-cv-grill` 是一个面向中英文求职场景的简历优化 skill：根据招聘 JD、职位描述、目标岗位、现有简历/CV、LinkedIn/profile 或项目经历，逐轮追问候选人的真实贡献、项目证据、指标和取舍，然后生成更贴合岗位的简历内容。

## Why This Exists / 为什么需要它

You may know the feeling: you open a job description and cannot immediately see how to reshape your resume around it. The goal is not to invent experience. The real problem is that experienced candidates have often done many things across many projects, roles, and teams, so the most relevant proof can be buried in memory. Many JDs also read like wish lists: long skill lists, broad requirements, and unclear priorities. `jd-cv-grill` helps at that exact point. Through focused one-question-at-a-time interviewing, it helps you read the role, recover overlooked evidence, identify which projects, decisions, results, and strengths matter most for this job, and turn them into a more truthful, specific, and role-fit CV or resume.

你可能也有过这样的感受：看到一份 JD 时，并不是没有经历，而是一时不知道该从哪里改简历。这个过程不是教你编故事。真正的问题往往是，越有经验的候选人，过去做过的项目、承担过的角色、解决过的问题越多，最适合这份工作的证据反而容易被埋在记忆里。再加上很多 JD 写得很大，技能清单很长，表面上什么都要，背后真正看重的能力却不一定清楚。`jd-cv-grill` 想帮你解决的就是这个卡点：它通过一轮一问的方式，帮你读懂岗位、回忆经历、辨认哪些项目、判断、成果和特长最能回应这份工作，最后把这些真实材料整理成一个更清晰、更可信、也更贴近目标岗位的你。

## Search Keywords / 搜索关键词

Use this skill when searching for:

```text
JD resume, job description resume, tailor resume to job description, resume polish,
CV polish, CV rewrite, resume rewrite, ATS resume, ATS keywords, resume bullets,
job application, LinkedIn profile, interview preparation, career story,
简历优化, 简历润色, JD改简历, 根据JD改简历, 岗位匹配, 求职简历,
英文简历, 中文简历, CV优化, ATS关键词, 经历挖掘, 项目经历提炼
```

## What It Does

- Analyzes a JD, job posting, role description, or target company profile.
- Extracts hard requirements, hidden hiring signals, ATS keywords, and recruiter screening logic.
- Interviews the candidate one question at a time instead of asking for a long form.
- Builds an evidence table: JD requirement, candidate proof, strength, missing details, and resume placement.
- Rewrites resume/CV bullets around confirmed facts, personal contribution, scope, impact, tools, and constraints.
- Flags weak evidence, unconfirmed metrics, confidentiality risks, and claims that should not be exaggerated.

## 中文能力

- 根据招聘 JD 拆解岗位画像、硬性要求、隐性标准和 ATS 关键词。
- 通过一轮一问深挖项目经历、个人贡献、业务影响、技术取舍和可验证证据。
- 输出岗位定制版简历 bullet、个人简介、技能映射、缺口补偿策略和待确认事实。
- 支持中文 JD、英文 JD、中文简历、英文简历和中英混合求职场景。

## Install for AI Coding Agents / 安装到 AI 编程助手

The recommended installer is the Agent Skills CLI. It can install this skill into Codex, Claude Code, Cursor, or multiple agents at once. By default, these commands install the skill into the current project. Add `-g` for global user-level installation.

推荐使用 Agent Skills CLI 安装。它可以把这个 skill 安装到 Codex、Claude Code、Cursor，或者一次安装到多个 AI coding agents。默认是安装到当前项目；如果想安装到用户全局环境，加 `-g`。

### Quick Install / 快速安装

Install for Codex:

```bash
npx skills add mikezhangyl/jd-cv-grill -a codex -y --copy
```

Install for Claude Code:

```bash
npx skills add mikezhangyl/jd-cv-grill -a claude-code -y --copy
```

Install for Cursor:

```bash
npx skills add mikezhangyl/jd-cv-grill -a cursor -y --copy
```

Install for both Claude Code and Cursor:

```bash
npx skills add mikezhangyl/jd-cv-grill -a claude-code cursor -y --copy
```

中文说明：

- Codex 用户运行 `npx skills add mikezhangyl/jd-cv-grill -a codex -y --copy`
- Claude Code 用户运行 `npx skills add mikezhangyl/jd-cv-grill -a claude-code -y --copy`
- Cursor 用户运行 `npx skills add mikezhangyl/jd-cv-grill -a cursor -y --copy`
- 如果你同时使用 Claude Code 和 Cursor，运行 `npx skills add mikezhangyl/jd-cv-grill -a claude-code cursor -y --copy`
- `-y` 表示跳过确认提示，`--copy` 表示复制文件而不是创建软链接，适合文档里的复制粘贴安装。

### Preview Before Installing / 安装前预览

List the skills available in this repository without installing:

```bash
npx skills add mikezhangyl/jd-cv-grill --list
```

### Global Install / 全局安装

Install globally instead of only for the current project:

```bash
npx skills add mikezhangyl/jd-cv-grill -g -a claude-code cursor -y --copy
```

如果你希望这个 skill 在所有项目里都可用，可以加 `-g` 做全局安装。

### Advanced: Install for Every Agent / 高级：安装到所有 Agent

This command is valid, but it can write to many agent directories in the current project. Use it only if you know you want that.

```bash
npx skills add mikezhangyl/jd-cv-grill --all --copy
```

这条命令有效，但会把 skill 安装到很多 agent 目录里。只在你明确需要“一次装给所有 agent”时使用。

### Update / 更新

When this skill is updated, run:

```bash
npx skills update jd-cv-grill
```

Or update all installed skills:

```bash
npx skills update
```

### Verify Installation / 验证安装

List installed skills:

```bash
npx skills list
```

For global skills:

```bash
npx skills list -g
```

### Manual Codex Install / 手动安装到 Codex

```bash
git clone https://github.com/mikezhangyl/jd-cv-grill.git
mkdir -p ~/.codex/skills/jd-cv-grill
cp -R jd-cv-grill/SKILL.md jd-cv-grill/agents ~/.codex/skills/jd-cv-grill/
```

Manual installation is mainly useful if the CLI is unavailable. In most cases, prefer `npx skills add`.

手动安装只建议在 CLI 不可用时使用。大多数情况下，直接使用 `npx skills add` 更稳。

## Usage

Trigger with prompts like:

```text
使用 $jd-cv-grill 根据这份 JD 追问我的经历，并为我定制简历。
```

```text
Use $jd-cv-grill to tailor my resume to this job description and identify missing evidence.
```

```text
使用 $jd-cv-grill 帮我根据这个岗位优化英文简历，重点处理 ATS 关键词和项目 bullet。
```

You can provide a JD, an existing CV/resume, LinkedIn/profile text, portfolio notes, or local files. The skill tells the agent to inspect available materials first, ask only one high-value question at a time, avoid fabricating experience, and label weak or unconfirmed evidence.

## Best For

- Tailoring a resume or CV to a specific job description.
- Turning vague project experience into strong resume bullets.
- Preparing an English resume from Chinese career notes, or vice versa.
- Mapping candidate evidence to ATS keywords and recruiter expectations.
- Stress-testing whether a resume claim can survive interview follow-up.

## Skill Structure

```text
SKILL.md
agents/openai.yaml
```

## License

MIT
