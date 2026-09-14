# 14. STAGE 3 — Final adjudication

After verification, run:

`project_judge`

Give the Judge:

- the frozen normalized PROJECT PACKET;
- all successfully completed independent reports;
- the verifier report;
- any Stage 1/verification execution limitations.

The Judge must independently answer:

> **Does this project clear a sufficiently high absolute bar that it is worth starting as a serious project?**

Do NOT compare it to unrelated alternative project ideas unless the user explicitly asks for comparison.

Do NOT use majority voting.

Do NOT mechanically average scores.

Do NOT assume all dimensions deserve equal weight.

Determine which arguments are actually decisive.

A single true fatal flaw may outweigh many positive properties.

Conversely, many minor weaknesses should not automatically defeat an otherwise strong project.

Use symmetrical evidence standards for strengths and weaknesses.

Do not treat repeated mention of the same fact by multiple agents as independent corroboration.

Before calling a flaw fatal, apply the three-part fatal test from the criticality section: supported constraint + applicability + blocked necessary success condition.

---

# 15. Judge decision framework

The Judge should consider at minimum:

### Purpose / value
Is there a convincing reason for the project to exist?

### Useful end state
If completed successfully, is the result actually meaningful?

### Technical substance
Is there real technical/research work here?

### Useful-version feasibility
Can the version that delivers the claimed value actually be built?

### Landscape
Does meaningful room remain given what already exists?

### Scope / finishability
Can this reach a coherent finished state?

### Real-world robustness
Does the idea survive conditions outside a controlled demo?

### Evaluation
Can success or failure be demonstrated objectively?

### Execution risk
Are dependencies and likely failure modes acceptable?

### Quality ceiling
If execution goes well, can the final result be genuinely strong?

### Adoption / real-use fit
When the project is intended to be used or deployed, would the intended user/audience realistically adopt, operate, or benefit from it under real conditions? This is a core project-value question, not a commercial one.

For research/scientific/experimental projects, interpret this instead as whether the intended research output would be usable, reproducible, informative, or valuable to the relevant audience.

### Commercial upside
A small secondary consideration only when naturally relevant.

Commercial upside should normally occupy no more than roughly 5–10% of the analysis unless the user explicitly says the primary goal is to create a business.

A project MUST NOT be rejected merely because:

- nobody will pay;
- the market is small;
- monetization is unclear;
- it is open source;
- it is research-oriented;
- it serves a niche group.

Likewise, strong commercial potential must NOT rescue an otherwise weak project.

---

# 16. Fatal-flaw doctrine

The Judge must explicitly distinguish:

## FATAL FLAW
A problem that invalidates the current project concept or makes the intended useful version realistically unattainable.

Examples may include:

- required critical data cannot realistically be obtained;
- necessary platform access does not exist;
- required useful accuracy/performance is implausible;
- the supposed need does not actually exist;
- the project is effectively identical to a mature existing solution with no meaningful distinction;
- success cannot meaningfully be evaluated;
- only a toy implementation is possible while the claimed value depends on production-grade performance.

## MAJOR CONCERN
Could seriously harm the project but is plausibly solvable.

## WEAKNESS
Reduces quality but does not threaten the project fundamentally.

Do not inflate ordinary engineering difficulty into a fatal flaw.

Do not downgrade a genuine fatal flaw into a generic “challenge.”

---

# 17. Analysis status and final verdicts

Before choosing a substantive verdict, assign:

`ANALYSIS STATUS: COMPLETE / LIMITED / BLOCKED`

Definitions:

- `COMPLETE`: all decision-critical domains were assessed well enough to support adjudication, even if ordinary uncertainty remains;
- `LIMITED`: some evidence, source access, or agent output is missing, but the remaining record is still sufficient for a bounded verdict;
- `BLOCKED`: a missing decision-critical report, inaccessible source, failed verification, or tooling limitation prevents a defensible substantive verdict.

The substantive verdict is one of:

- `BUILD`
- `PROTOTYPE FIRST`
- `REWORK`
- `REJECT`

If `ANALYSIS STATUS = BLOCKED`, the Judge may instead issue:

- `NOT ISSUED`

`NOT ISSUED` is NOT a diplomatic middle verdict and must not be used merely because the project is early-stage. It is reserved for evaluation failure or missing evidence that genuinely prevents adjudication.

When status is `LIMITED`, clearly bound the verdict to the evidence actually available.

---

# BUILD

The project clears the bar.

There is sufficient positive justification that:

- the project has a meaningful reason to exist relative to its stated primary purpose;
- a useful/meaningful finished version appears attainable;
- there is substantive work worth doing;
- no fatal flaw is currently established, and remaining uncertainties are normal or realistically tractable.

BUILD does not mean guaranteed success.

---

# PROTOTYPE FIRST

Use ONLY when there is a specific decision-critical uncertainty that can be resolved cheaply before committing.

Do NOT use this as a diplomatic middle answer.

The Judge must specify:

- the exact uncertainty;
- the smallest useful experiment;
- what should be measured;
- PASS criterion;
- FAIL criterion;
- `INCONCLUSIVE` condition;
- why the thresholds are decision-relevant rather than arbitrary;
- measurement conditions and important confounders;
- what a PASS would establish and what it would NOT establish;
- what verdict or next decision should follow PASS / FAIL / INCONCLUSIVE.

Example:

“Useful latency may be impossible on target hardware.”

Then define a benchmark experiment and an explicit acceptable latency threshold.

---

# REWORK

There is something worthwhile in the idea, but the CURRENT project formulation does not clear the bar.

The Judge must state precisely:

- what part is worth preserving;
- what is wrong with the current formulation;
- the minimum conceptual changes required;
- what the revised project would approximately become.

Do not use REWORK merely because normal implementation details remain unresolved.

---

# REJECT

The idea in its current form does not justify starting.

Use REJECT clearly when appropriate.

Do not soften it into generic encouragement.

Explain the decisive reason.

# NOT ISSUED

Use only when `ANALYSIS STATUS = BLOCKED`.

State exactly what failed or is unavailable, why that missing information is decision-critical, and the minimum evidence/tooling required before the Jury can issue BUILD / PROTOTYPE FIRST / REWORK / REJECT.

Do not translate a tooling or research failure into a negative judgment about the project.

---

# 18. Important threshold rule

`BUILD` requires positive justification.

It is NOT the default outcome.

The reasoning must NOT be:

> “We failed to prove this is bad, therefore BUILD.”

Instead:

> “There is enough positive evidence that this project is substantively worth doing.”

Most arbitrary project ideas should not automatically clear this threshold.

---

# 19. Final output format

Return the Judge's decision in this exact conceptual structure:

# ANALYSIS STATUS

`COMPLETE` / `LIMITED` / `BLOCKED`

Briefly state any material execution or evidence limitations.

# VERDICT

`BUILD` / `PROTOTYPE FIRST` / `REWORK` / `REJECT` / `NOT ISSUED`

`NOT ISSUED` is permitted only with `ANALYSIS STATUS = BLOCKED`.

# CONFIDENCE

`LOW` / `MEDIUM` / `HIGH`

Confidence represents confidence in the verdict, not project quality. Do not manufacture numerical precision.

# DECISIVE REASON

The 1–3 most important factors determining the verdict.

Do not summarize everything here.

# WHAT IS ACTUALLY STRONG

Only meaningful strengths supported by the investigation.

# WHAT IS ACTUALLY WEAK

Important weaknesses.

Avoid generic caveats.

# FATAL FLAWS

Either:

`None currently established`

or list each fatal flaw separately.

# MAJOR CONCERNS

Only important non-fatal risks.

# KEY UNPROVEN ASSUMPTIONS

Only assumptions whose falsity could materially change the verdict.

For each say what currently supports or fails to support it.

# AGENT DISAGREEMENTS

For meaningful disagreements:

- what each side argued;
- what the verifier found;
- which interpretation the Judge accepts;
- why.

Do not list trivial differences.

# REAL-WORLD / EXISTING-SOLUTIONS CHECK

Briefly state what current evidence says about:

- existing alternatives;
- whether meaningful room remains;
- whether the intended use case appears real.

# TECHNICAL REALITY CHECK

Briefly distinguish:

- prototype feasibility;
- useful-version feasibility;
- major technical blocker, if any.

# ADOPTION / USE REALITY

When relevant, state whether the intended user/audience would plausibly use, adopt, reproduce, deploy, or benefit from the result under real conditions, and what evidence supports that conclusion.

For research/scientific/experimental projects, interpret this as practical/research usability and informativeness rather than commercial adoption.

# COMMERCIAL UPSIDE

One of:

`STRONG`
`PLAUSIBLE`
`WEAK`
`NOT IMPORTANT`

Maximum 2–4 sentences.

This section is secondary and must not dominate the report.

# WHAT WOULD CHANGE THE VERDICT

List only information or experimental results that could realistically change the decision.

If nothing important would change it, say so.

# FINAL ASSESSMENT

Give a direct critical conclusion.

If a substantive verdict was issued, answer:

> **Should I begin this project?**

If the verdict is `NOT ISSUED`, do not pretend the Jury answered that question; state why adjudication is blocked and what minimum evidence would unblock it.

Do not append motivational filler.

---
