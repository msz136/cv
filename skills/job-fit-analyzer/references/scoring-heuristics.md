# Scoring Heuristics

These rules apply to ALL roles. Each role adds its own rules on top.

## Two-Layer Evaluation Model

This tool uses two layers. They match how hiring works in real life.

**Layer 1 - Screen Check (Will you get past the filter?)**
Hiring teams check hard rules first. If a job says "2+ years running a decision engine" and you have zero, you are cut before anyone reads the rest. The screen check catches this.

**Layer 2 - Fit Score (How well do you match?)**
Once past the screen, scoring looks at how strong you are. This is a deeper look at your skills, depth, and related work.

Both layers run for every job. Even if the screen says "Likely Filtered Out," the fit score still runs. It powers the roadmap and next steps. But the output is honest about the screen barrier.

## Layer 1: Screen Check

### What Makes a Rule "Hard"

Hard gate rules are specific, true or false, and firm. They are the things a recruiter checks before reading the rest.

**Hard gates** look like this:
- They name specific tools or tech ("Taktile," "FICO Blaze," "Salesforce," "Python")
- They name specific fields or product types ("MCA lending," "decision engines," "healthcare claims")
- They need specific certs or clearances ("CPA required," "Secret clearance")
- They use firm language ("must have," "required," "minimum X years of [specific thing]")
- You can answer yes or no: "Have you run a decision engine for 2+ years?"

**Soft signals** are everything else:
- General skills ("strong analytical skills," "excellent communication")
- Broad experience ("5+ years of product management experience")
- Culture fit phrases ("fast-paced environment," "team player")
- Traits scored on a range, not yes or no

### Classification Rules

When reading a JD, pull out each rule and sort it:

1. **If it names a specific tool, platform, field, or cert** and the JD says "required" or "must have": it is a Hard Gate.
2. **If it describes a general skill** that most people in this role would have: it is a Soft Signal.
3. **If it is specific but listed as "nice to have" or "preferred"**: it is a Soft Signal, not a Hard Gate.
4. **Years of general experience** (e.g., "5+ years PM experience") are Soft Signals. **Years of specific experience** (e.g., "2+ years running a decision engine") are Hard Gates.
5. When unsure, ask: "Would a recruiter reject someone missing ONLY this one thing?" If yes, it is a Hard Gate.

Most JDs have 1-3 hard gates and 5-10 soft signals. Some JDs have zero hard gates. Flag when a JD has none. The screen check will show "No hard gates found."

### Title Match Check

Always check if the candidate has ever held a title in the same family as the target role. For example, a "Technical Program Manager" role should look for any form of "Program Manager," "TPM," "Delivery Manager," or similar. This applies to all roles, supported or not.

If no title in the role family appears anywhere in the resume or LinkedIn, flag it as a screening risk. Recruiters and ATS systems often filter by title keywords. A candidate who has done the work but never held the title will be invisible in keyword searches.

This does NOT lower the fit score. Title absence is a visibility problem, not a skills problem. But it must show up in two places:
1. **Screen Check (Section 0):** Add a row for "Title match to role family" with a Pass (held the title), Partial (held a close title like "Delivery Lead" for a TPM role), or Fail (no title in the family).
2. **What the Hiring Manager Is Thinking (Section 4):** Call out that the title gap makes the resume harder to find and harder to read at a glance.

### Checking Each Hard Gate

For each hard gate, check the resume and LinkedIn:

| Verdict | Criteria |
|---|---|
| **Pass** | Clear, direct proof. The person has done this exact thing. Not close, not guessed. |
| **Partial** | Close experience that builds the same skill but is not the exact thing. Or the exact thing but too old (7+ years) or too light (saw it, did not own it). |
| **Fail** | No proof of direct or closely related experience. |

Be strict on Pass. "Worked with data teams" does not pass a "Python required" gate. "Built SQL pipelines" does not pass a "decision engine" gate. Close is Partial, not Pass.

### Screen Verdict

Based on the hard gate results, pick one of three verdicts:

| Verdict | When to Use | What It Means |
|---|---|---|
| **Likely Passes Screen** | All hard gates Pass, or at most 1 Partial with strong close experience | This person would likely get past the first screen |
| **Borderline** | 1 hard gate Fail with strong close experience that a good recruiter might accept, or 2+ Partials | Could go either way. Depends on the recruiter, the pool, and how the person frames their experience |
| **Likely Filtered Out** | 2+ hard gate Fails, or 1 Fail on a rule that defines the role (e.g., the tool the whole job is about) | This person would likely be cut before a human looks closely |

### How Screen Verdict Affects the Output

The screen verdict does NOT change the fit score math. Both layers are separate. But it changes how the output reads:

- **Likely Filtered Out**: The output leads with the screen barrier. The fit score is labeled "Fit Score (if screened in)" to show it is conditional. The roadmap focuses on closing hard gate gaps, not dimension gaps.
- **Borderline**: The output names the screen risk up front. The fit score runs as normal. The weakness section focuses on the borderline hard gate.
- **Likely Passes Screen**: Standard output. No screen warning needed.

## Layer 2: Fit Score

The fit score is 0-100. It answers one question: "Based on what this person has done, how likely are they to succeed in this role?"

It does NOT measure:
- How well the resume is written (that is a separate check)
- Whether the person would take the role
- Culture fit or soft skills beyond what the work history shows
- Potential beyond proven skill
- Whether the person will pass the screen (that is Layer 1)

## Score Calibration

| Range | What It Means | Hiring Outcome (assumes screen is passed) |
|---|---|---|
| 85-100 | Could start this role and perform from week one. Direct experience in most core areas. Few or no gaps. | Phone screen, likely interview |
| 70-84 | Strong fit with 1-2 small gaps. Would need some ramp time but has the base. | Phone screen, maybe interview |
| 55-69 | Mixed fit. Real strengths in some areas but real gaps in others. Would need a lot of help in gap areas. | Maybe pile. Depends on the pool. |
| 40-54 | Stretch pick. Has related experience but this role would be a big step up. | Likely pass unless the pool is thin |
| Below 40 | Poor fit. Little overlap between past work and what the role needs. | Pass |

The fit score assumes the person got past the screen. A score of 72 with "Likely Filtered Out" means "strong fit who will likely never get the chance to prove it." That is very different from a 72 with "Likely Passes Screen."

## Common Scoring Rules

### 1. Recency Weighting
- Work from the last 3 years counts at full weight
- Work from 3-7 years ago counts at roughly 70% weight
- Work older than 7 years counts at roughly 40% weight
- Exception: core skills (leadership, working with stakeholders) do not fade as fast as technical skills

### 2. Depth Over Breadth
- Owning an area scores higher than helping with it
- 2 years of deep ownership beats 5 years of light exposure
- Look for growth within a skill (went from helping to owning)

### 3. Title vs Work Mismatch Handling
- When the title does not match but the work does, score based on the WORK, not the title
- Flag the mismatch in the Adjacent Work section
- Lower confidence by one level when the only proof comes from self-written LinkedIn content with no backup from the resume

### 4. Proof Across Documents
- Same win described in both documents: highest confidence
- Win in one document only: lower confidence a bit
- Conflicting info between documents: flag in hygiene check, use the smaller claim for scoring

### 5. Metric Quality
- Specific metrics with context ("cut processing time from 4 hours to 20 minutes") score higher than relative metrics ("improved efficiency by 80%")
- Any number scores higher than no number
- Missing metrics do not always mean weak experience. Some fields (compliance, infra) have fewer clear metrics

### 6. Company Context Adjustment
- Scale matters. A PM at a 10-person startup did different work than a PM at Google. Neither is better, but the type of experience differs.
- Regulated industry experience transfers well to other regulated fields
- Startup experience transfers to startup roles. Enterprise transfers to enterprise roles. Cross-context transfers are possible but lower confidence.

### 7. Dimension Scoring

Each role has 5-7 scored dimensions. For each dimension:

| Level | Score | What It Looks Like |
|---|---|---|
| Strong | 80-100 | Direct, recent, deep experience with clear results |
| Solid | 60-79 | Good proof but missing depth, recency, or results |
| Partial | 40-59 | Close experience or light direct exposure |
| Weak | 20-39 | Very little relevant experience, mostly guessed |
| Gap | 0-19 | No real proof in either document |

### 8. Overall Score Calculation

The overall score is NOT a simple average. It works like this:

1. Score each dimension for the role (using the role criteria file)
2. Apply the weights from the role criteria
3. Find the weighted average
4. Apply a "critical gap penalty": if ANY dimension is below 20, cut the overall score by 10 points. Two or more gaps below 20 cut by 20 points. This is how it works in real life. One big gap can sink you no matter how strong the rest is.
5. Apply a "proof bonus": if 3+ dimensions are backed by both documents, add 3 points. This reflects the trust signal of being consistent.

### 9. When to Override the Score

Sometimes the math gives a score that does not match reality. Override when:
- The person has a rare mix that is very valuable for this role (score up)
- The person has a gap so big that the dimensions do not fully capture it (score down)
- The role has an odd rule that does not map to standard dimensions (adjust and explain)

Always explain overrides clearly. Never adjust in silence.
