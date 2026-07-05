---
name: job-fit-analyzer
description: Analyze job fit when a user uploads their resume and LinkedIn profile alongside a job description, or asks how well they match a role, or wants to know their strengths and gaps for a specific position, or asks "should I apply for this job." Triggers on any request involving candidate-to-job evaluation, career fit assessment, or application decision-making. This is NOT a keyword matcher. It evaluates actual work performed regardless of job titles.
---

# Job Fit Analyzer

Check how well a person's real work fits a job. Look at what they did, not their titles.

## What This Skill Does NOT Do

- **Not keyword matching.** ATS tools do that. This looks at the real work done.
- **Not resume writing.** This checks fit. It flags where the resume sells short, but does not rewrite it.
- **Not generic advice.** Every output must be about this person and this job.
- **Not tied to one role type.** This works for any role. Adapt your criteria to fit.

## Inputs Required

Before you start, you MUST have all three:

1. **Resume** (PDF or text): the person's current resume
2. **LinkedIn profile** (PDF or text): the person's LinkedIn export
3. **Job description** (pasted text or PDF): the target role

If any input is missing, ask for it first. Do not try a partial run.

## Analysis Process

Work through these stages in order. Do not skip or merge them.

### Stage 1: Decode the Job Description

Before looking at the person, learn what this role needs.

1. **Find the role type** (engineering, product, design, sales, ops, data, etc.) and level.
2. **Pull out 5-7 core needs**: not every bullet, just the ones that drive a hire or no-hire call. Split stated needs from implied ones. For example, "fast-paced" implies comfort with chaos and quick calls.
3. **Sort each need as a Hard Gate or Soft Signal.** Load [references/scoring-heuristics.md](references/scoring-heuristics.md) and follow the rules in "Layer 1: Screen Check." Hard gates are specific, provable, must-have items (tools, platforms, domains, certs). Soft signals are broad skills on a spectrum. Most JDs have 1-3 hard gates and 5-10 soft signals.
4. **Find the ideal hire**: what kind of person would thrill the hiring manager? What's their dream background? What company or role would they come from?
5. **Pick the right role criteria.** Load [references/roles.md](references/roles.md) to find the matching role. Then load the matching file from `references/role-criteria/` for scoring weights. If no role matches, use common rules only and flag that scoring is less precise.
6. **Note the company context**: stage (startup, growth, or large company), industry, and any clues about team setup or culture.

### Stage 2: Extract What the Person Has Done

Read both the resume and LinkedIn profile fully. Your goal is to learn what this person has really DONE, not what their titles say.

1. **Map their career path**: roles, companies, time in each, and how they moved up.
2. **Break each role into work types.** Load [references/activity-framework.md](references/activity-framework.md) for the framework. Sort what they did into: Strategic, Discovery, Definition, Execution, Growth, Technical, and Communication work.
3. **Find where title and work don't match.** Use the mismatch patterns in the activity framework. A "Solutions Architect" who ran backlogs and wrote requirements was doing product work. A "Business Analyst" who built data pipelines was doing data engineering. Surface these.
4. **Cross-check both documents.** LinkedIn often has richer detail (descriptions, endorsements, activity). The resume may be sparse. Use LinkedIn to fill gaps, and note where the two documents tell different stories.
5. **Split the person from their resume.** A weak resume does not mean a weak person. If the resume is vague but LinkedIn shows strong, specific work, the person is better than their resume shows. Flag this.

### Stage 3: Screen Check (Hard Gate Review)

Before scoring, check if this person would survive the first screen. Use the hard gates from Stage 1.

For each hard gate:
1. Search the resume and LinkedIn for direct proof.
2. If no direct proof, search for nearby experience.
3. Mark as **Pass** (direct proof), **Partial** (nearby or outdated), or **Fail** (no proof).

Then give a screen verdict using the rules in `scoring-heuristics.md`:
- **Likely Passes Screen**: All hard gates Pass, or at most 1 Partial.
- **Borderline**: 1 Fail with strong nearby proof, or 2+ Partials.
- **Likely Filtered Out**: 2+ Fails, or 1 Fail on a must-have need.

Be strict. "Worked with data teams" does not pass a "Python required" gate. Nearby work is Partial, not Pass. If the JD has no hard gates, note this and skip to Stage 4.

### Stage 4: Score the Fit

Now map the person to the job. Match on work done, not titles held.

**Step 4a: Score each dimension from the role criteria file.** Each role has 5-6 weighted items. Score every item using the level notes in the file (Strong, Solid, Partial, Weak, or Gap with number ranges).

**Step 4b: Calculate the total score.** Follow the method in `scoring-heuristics.md`:
1. Score each dimension (0-100).
2. Apply the weights from the role criteria.
3. Get the weighted average.
4. Apply the critical gap penalty (if any dimension is below 20).
5. Apply the backup bonus (if 3+ dimensions have proof in both documents).
6. Override only if the math does not match reality, and say why.

**Step 4c: Map to needs.** For each of the 5-7 core needs from Stage 1:
1. Search for direct proof in the person's background.
2. Search for nearby proof (work that builds the same skill under a different name).
3. Check depth: did they own it or just help? How recent? For how long?
4. Assign confidence: Strong Match, Partial Match, or Gap.

### Stage 5: Write the Output

Produce ALL sections below. Do not skip any.

---

## Output Format

### 0. Screen Check

Show the hard gate results from Stage 3. This comes FIRST, before any scores.

**Format:**

| # | Hard Gate Requirement | Evidence | Verdict |
|---|---|---|---|
| 1 | [Specific need from JD] | [What was found, or "No evidence"] | Pass / Partial / Fail |

**Screen Verdict: [Likely Passes Screen / Borderline / Likely Filtered Out]**

If the verdict is "Likely Filtered Out," add: "This person would likely be cut before a full review. The fit score below shows how they'd do IF they got past screening, but the hard gate gaps are the main barrier."

If the verdict is "Borderline," add: "This person is on the edge. Passing the screen depends on the recruiter, the applicant pool, and how well the application frames nearby experience."

If "Likely Passes Screen," add: "No hard gate barriers found. This person should reach the review stage."

If the JD has no hard gates, state: "No hard gate needs found in this JD. All needs are broad skills on a spectrum. Screen check does not apply. Moving to fit scoring."

### 1. Fit Score and Headline

**Score: X/100** (or **Fit Score (if screened in): X/100** when screen verdict is "Likely Filtered Out")

Give a single score with a one-line summary of the fit. The score shows the person's real skill match, not their resume quality.

When the screen verdict is "Likely Filtered Out," the headline must note the screening barrier first, then the fit. Example: "Would likely be cut due to missing decision engine experience. If screened in, this is a solid PM with skills that transfer."

When the screen verdict is "Borderline," note the risk: "Screening is a coin flip. The [specific hard gate] gap could go either way."

Scoring guide:
- **85-100:** Strong fit. The person could do this role based on proven work.
- **70-84:** Solid fit with small gaps. A good pick who would need to close 1-2 areas.
- **50-69:** Partial fit. Real strengths in some areas but big gaps in others.
- **30-49:** Stretch pick. Nearby experience exists but major skill gaps remain.
- **Below 30:** Poor fit. Little overlap between experience and role needs.

### 2. Requirements Map

A table mapping each core job need to the person's experience:

| Requirement | Evidence From Candidate | Confidence | Source |
|---|---|---|---|
| [Need from JD] | [Specific experience that maps to this] | Strong / Partial / Gap | Resume / LinkedIn / Both |

For each row, be specific. Don't say "has relevant experience." Say "Led 8-person team at BMO building a risk reporting platform. This directly maps to the cross-team leadership this role needs."

### 3. Adjacent Work Recognition

This is the most useful section. Find 2-4 cases where the person did work that fits this role under a different title or in a different context.

For each case:
- **What their title said:** [Official title]
- **What they really did:** [The work, described in the target role's language]
- **Why it matters for this role:** [How it maps to a core need]
- **Strength of proof:** [How sure are you: strong, moderate, or guess]

If the person's career is a straight line to this role with matching titles, say so and skip this section.

### 4. What the Hiring Manager Is Thinking

Write 4-6 sentences as the hiring manager reading this application. Be honest, specific, and reflect the mindset of someone scanning resumes under time pressure.

Think about:
- What grabs their eye in the first 7 seconds?
- What makes them pause or feel unsure?
- What biases might play a role (brand prestige, title mismatch, industry fit)?
- Would this resume survive a 7-second scan, or does the real strength need a deeper read?
- Does the career path "make sense" at a glance?

Be direct. If the hiring manager would think "Why is a bank person applying for this?", say that. Then explain what they'd think if they read deeper.

### 5. Biggest Weakness + Flip Strategy

Name the single biggest concern a hiring manager would have about this person for this role. Be blunt: state it clearly.

Then give a concrete flip plan:
- How can the person reframe this concern in their cover letter or interview?
- What specific proof from their background partly covers it?
- What would a strong 2-sentence answer sound like if asked about this in an interview?

### 6. Top 3 Strongest Stories

Pick the 3 most compelling experiences from the person's background for THIS role (not their 3 best wins in general).

For each story:
- **The experience** (1-2 sentences)
- **Why it works for this role** (which specific need it covers)
- **The hook** (what makes it stick: a metric, a surprise outcome, a scale marker)

Pull from whichever document has richer detail. If LinkedIn has more context than the resume, use that.

### 7. Score Improvement Roadmap

This section answers: "What would it take to close the gap?"

List the **top 3 actions** the person could take to boost their fit for this type of role. These should be:

- **Hard gate gaps come first.** If the screen check found Fail or Partial verdicts, the first actions MUST cover those gaps. Raising dimension scores is pointless if the person never gets past screening.
- **Specific and doable.** Not "get more experience." Instead: "Build a small AI tool that solves a problem in your domain and ship it to real users."
- **Ranked by impact on getting hired** (not just score gains). Closing a hard gate gap matters more than moving a dimension from 55 to 70.
- **Realistic for this person.** Think about their current skills, domain, and resources. A banking PM won't become an ML engineer. But they can build with AI tools and publish domain-relevant thinking.
- **Time-bound.** Roughly how long would each action take? Weeks, months?

For each action:
- **What to do** (1-2 sentences)
- **Why it helps** (which scoring dimension it covers and why hiring managers care)
- **Estimated score impact** (e.g., "Could move Dimension 1 from 25 to 50, adding ~6 points to total score")
- **Time needed** (rough estimate)

The goal is not to game the system. It's to close real skill gaps that the scoring found. If the person does these things, they should truly be a stronger pick, not just look like one on paper.

### 8. Hygiene Check

Cross-check the resume and LinkedIn for conflicts. Load [references/hygiene-checks.md](references/hygiene-checks.md) for the full list of patterns to check.

Check for:
- Date gaps (start and end dates that don't align)
- Title conflicts (inflated or different titles between documents)
- Missing roles (appears on one document but not the other)
- Metric conflicts (different numbers for the same result)
- Education gaps (degrees, dates, schools)

For each conflict found:
- **What conflicts:** [Specific issue]
- **Risk level:** High (looks dishonest), Medium (looks careless), or Low (minor format difference)
- **What to fix:** What to change and why

If no conflicts are found, say so clearly. This is a good signal worth noting.

### 9. Resume Narrative Check

This section rates the resume AS A DOCUMENT, apart from the person's actual fit.

Flag issues like:
- Tasks listed instead of outcomes
- Vague language where specifics exist (check LinkedIn for the details)
- Missing numbers on strong work
- Burying strong experience below weaker content
- Generic bullets that could apply to anyone

Rate the resume narrative: **Strong / Adequate / Underselling**

If underselling: list the 2-3 highest-impact fixes that would better show the person's real experience. Point to specific LinkedIn details that could strengthen specific resume bullets.

**Important:** This rating does NOT affect the fit score. A person with a weak resume but strong LinkedIn-backed experience still gets a high fit score. The resume rating is a separate area to improve.

---

## Tone and Calibration

- Be direct and specific. Never use filler like "shows a strong background in" or "has excellent skills."
- Every claim must point to a specific piece of proof from the person's documents.
- When unsure, say so. "LinkedIn suggests X but the resume doesn't confirm it" is more useful than a confident guess.
- Be honest in scoring. Not every person is a strong fit, and saying so is more useful than false hope.
- Adapt your language to the role type. Use engineering terms for engineering roles, product language for PM roles, etc.
