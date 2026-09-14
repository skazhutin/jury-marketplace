---
name: project-jury
description: Run Project Jury to decide whether a project idea is worth starting as a serious finished project, using six independent specialists, a verifier, and a judge. Use for $project-jury or an explicit request to run Project Jury on an idea; this is not general brainstorming or a startup pitch review.
---

# Project Jury

Answer: **Should I actually begin this project?** Require positive justification for BUILD. Reject weak ideas without encouragement filler; use equally strong evidence standards for favorable and unfavorable claims. Preserve research, open-source, creative, niche, educational, and noncommercial purposes.

This skill explicitly authorizes the eight bounded reviewer subagents below when invoked. It does not authorize changes to application code, communications, publishing, purchases, or external mutations.

## Prepare and freeze

Read [project-packet.md](references/project-packet.md), [principles-and-evidence.md](references/principles-and-evidence.md), and [orchestration.md](references/orchestration.md) in full. Re-read the applicable originals after compaction or uncertainty; a summary is not a substitute.

Normalize the user's actual idea without improving it. Preserve project type and success criterion. Use explicit conservative assumptions for rough input. Ask at most the essential question when evaluation would otherwise be meaningless; do not send a questionnaire. Freeze the exact packet and permitted common-source content before dispatch. Assign P-001 etc. to decision-critical packet claims. User claims remain USER-REPORTED unless independently verified.

## Run

Use the isolated launcher in [runtime.md](references/runtime.md) for every accepted Jury run. It injects mandatory original references into native developer context and validates reference receipts; direct ad hoc role calls without that boundary are not accepted Jury runs. The launcher starts a real local Codex orchestration process with installed custom agents; it does not simulate reviewers. Only the coordinator may create bounded run-input/output artifacts outside application source. Jury specialists return reports in their conversations and write no files.

1. Stage 1: independently dispatch `project_value`, `project_technical`, `project_landscape`, `project_execution`, `project_advocate`, and `project_skeptic` with exactly the same frozen packet and common materials. Use six concurrent agents if supported, otherwise independent batches. No parent-history fork or peer-report access. Apply [stage-one-report.md](references/stage-one-report.md).
2. After all six finish or exhaust one retry each, assemble all reports, the claim registry, disagreements, and explicit failure records. Run `project_verifier` according to [verification.md](references/verification.md).
3. After verification completes or its failure is explicitly recorded, give `project_judge` all available required context and limitations. Apply [adjudication.md](references/adjudication.md). No majority vote, score average, or automatic BUILD.
4. Return the Judge's exact conceptual output structure. Never turn an execution failure into a negative project verdict. BLOCKED/NOT ISSUED is for failed adjudication, not a diplomatic middle answer. Clearly bound LIMITED results.

Do not run a real evaluation during installation or a synthetic smoke test. Normal invocation: `$project-jury Evaluate this idea: ...`.
