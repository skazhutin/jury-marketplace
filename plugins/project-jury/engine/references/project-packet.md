# 3. Project-type normalization and frozen input contract

Before launching Stage 1, create a neutral normalized PROJECT PACKET containing:

- `PROJECT TYPE`: e.g. user-facing tool, developer tool, research/scientific, infrastructure, hardware/system, educational, creative, experimental, or other;
- `PRIMARY PURPOSE`;
- `INTENDED DELIVERABLE`;
- `INTENDED USER / AUDIENCE / BENEFICIARY`, if applicable;
- `WHAT WOULD COUNT AS SUCCESS`;
- `TARGET ENVIRONMENT / PLATFORM`, if relevant;
- `KNOWN TEAM / TIME / BUDGET / COMPUTE / HARDWARE / DATA / ACCESS`;
- `USER-SUPPLIED EVIDENCE`;
- `EXPLICIT ASSUMPTIONS`;
- `IMPORTANT UNKNOWNS`.

Do not improve the idea while normalizing it.

The success criterion must match the project type. For example, a research project may succeed by producing a valid reproducible result even if it has no end-user adoption; a deployed utility must be judged on real use conditions, not only on experiment quality.

Freeze this packet before Stage 1.

Every first-stage agent must receive the SAME frozen packet plus the same user-provided source materials that are legitimately available to all roles.

Do NOT include:

- coordinator opinions;
- summaries of another first-stage agent;
- partial conclusions from earlier first-stage runs;
- an advocate/skeptic framing added after normalization.

If Stage 1 must run in multiple batches because of concurrency limits, later batches still receive only the frozen packet and permitted common sources, never previous Stage 1 reports.

---

# 20. Input handling

The skill should work even when the user gives only a rough idea.

Do not respond with a large questionnaire.

Instead:

1. build the normalized PROJECT PACKET defined earlier;
2. identify missing information;
3. make conservative explicit assumptions where reasonable;
4. investigate what can be investigated;
5. mark unresolved context as uncertainty;
6. preserve the user's intended project type and success criterion instead of silently converting it into a startup/product thesis.

Ask the user a question before running the Jury only when evaluation would otherwise be fundamentally meaningless.

Do not make the idea sound more impressive during normalization.

Preserve what the user actually proposed.

---
