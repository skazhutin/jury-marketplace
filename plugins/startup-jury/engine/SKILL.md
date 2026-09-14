---
name: startup-jury
description: Run Startup Jury to decide whether a proposed startup merits serious pursuit, using eight independent specialists, factual verification, business-system cross-examination and a final judge. Use for $startup-jury or an explicit request to run Startup Jury on an idea.
---

# Startup Jury

Answer: **Should I seriously pursue this startup idea?** This is a rigorous
business decision, not motivational coaching. Evaluate the proposed thesis;
never silently improve its customer, buyer, scope, monetization or distribution.
Do not mistake an interesting product for a viable business. Apply symmetrical
evidence standards to positive and negative arguments.

## Execution route

If no startup idea was supplied, or the core thesis is fundamentally ambiguous,
ask the one necessary clarification in the calling task before starting the
launcher or any reviewers. Ordinary missing evidence is not a reason to delay.

Use the bundled native custom roles and supported read-only runtime. First
read [runtime.md](references/runtime.md). A skill's `agents/openai.yaml` is UI
metadata; custom reviewers live in this engine’s `native_agents/`; its `runtime.toml` controls Jury sessions.

If the current session lacks effective read-only permissions, custom role
selection, fresh child contexts, or enough lifecycle controls to complete the
stages, invoke `python3 scripts/run.py` from this engine directory with the user's idea and supplied
evidence on stdin. Pass the authorized evaluation request, not this installation
conversation. The launcher uses a dedicated read-only Codex CLI coordinator,
with no inherited conversation and no connectors or external action tools.
It prints the result; return that result faithfully with execution limitations.
Use the shell tool's stdin facility or a safely quoted heredoc. Never interpolate
an idea into a shell command. Do not recursively call the launcher from an
already isolated Jury coordinator. If that route fails, report the failure;
do not simulate independent reviewers or issue a startup verdict from a tooling
failure. No profile settings change the permissions of this existing task.

## Coordinator workflow

1. Read [principles.md](references/principles.md),
   [orchestration.md](references/orchestration.md), and
   [stage-one-report.md](references/stage-one-report.md).
2. Normalize the input using every packet field in orchestration.md. Ask one
   clarification only if the core thesis is fundamentally ambiguous. Otherwise
   label conservative assumptions and unknowns. Unknown ambition is not venture
   scale. Assign stable `INPUT:C001` IDs to decision-critical supplied claims.
3. Freeze one exact STARTUP PACKET and one common source bundle before any
   Stage 1 run. Canonicalize packet line endings to LF with no trailing newline before freezing.
   Assign a packet version and SHA-256 over those UTF-8 bytes if tools permit; otherwise
   preserve exact text and a stable packet ID. Do not rewrite the packet between
   batches. Pass that same packet and sources directly to every first-stage role.
4. Begin every native spawn message with `ROLE_NAME: <exact_role>`. Put the
   identical complete packet between `BEGIN FROZEN STARTUP PACKET` and
   `END FROZEN STARTUP PACKET` on separate lines. Spawn these **eight distinct custom roles**, with fresh contexts
   (`fork_context=false`, or the equivalent supported by the active tool):
   `startup_customer_demand`, `startup_market_timing`, `startup_landscape`,
   `startup_distribution`, `startup_economics`, `startup_product_execution`,
   `startup_advocate`, `startup_skeptic`. Give each only its role instructions,
   shared principles/report schema, frozen packet and common source bundle.
   Never fork coordinator history into Stage 1. Do not send a role another
   role's output. Do not launch generic agents under invented role names.
5. Run all eight concurrently when permitted. Otherwise use the maximum safe
   independent batches. Capture the full report and required claim records from
   each role, validate completeness, record failures, and retry each failed role
   at most once with the unchanged packet in a fresh context. Do not substitute
   a different role. After capturing reports, close/release completed children
   if needed to free slots. Keep captured reports intact.
6. The launcher captures full native reports in memory and seals read-only files
   under the supplied `RECORDS_DIR` at the Verifier spawn boundary, after
   Stage 1 validation and retries complete. Do not read those files before
   launching Verifier; until then, use captured native tool results. Include that
   exact directory in every later-stage spawn. Require later agents to read
   `manifest.json` and all required original reports in full. Never shorten or
   paraphrase reports to save context. If necessary originals cannot be accessed,
   propagate the limitation rather than pretending a summary is complete.
   Only after all eight reports or exhausted failures are recorded, build the
   claim registry, preserving IDs and source dependencies. Record material
   disagreements without adding opinions. Launch `startup_verifier` with the
   exact packet, all successful Stage 1 reports, claim registry, disagreements,
   and failures. Capture its full output and dependencies it invalidates.
7. Only then launch `startup_cross_examiner` with the packet, every available
   Stage 1 report, verifier output, and all execution/verification limitations.
   Capture its output. Never replace this with another round of broad research.
8. Only then launch `startup_judge` with the packet, all Stage 1 reports,
   verifier and cross-examiner outputs, and every limitation. The judge must
   read [judge-rules.md](references/judge-rules.md), assign analysis status first,
   and use its full final format. No voting, averaging, fake precision or
   inference that repeated sources are independent evidence.
9. For a failed later stage, record the failure and retry once in a fresh role
   with the same required inputs if safe. Pass unresolved failures forward;
   never invent a verifier, cross-examination or judge report. If the judge
   cannot run or critical missing context precludes adjudication, the
   coordinator reports `BLOCKED` / `NOT ISSUED` and the minimum resume condition.
   If a bounded verdict is still defensible, the judge may use `LIMITED`.
10. Return the judge's result faithfully, preserving claim citations and material
    limitations. Do not add an encouraging conclusion or quietly strengthen the
    verdict. Keep full reports until adjudication completes, then release children.

## Decision invariants

`FATAL` requires a supported constraint, its applicability to the commercially
relevant business, and a blocked necessary viability condition. Unknowns alone
are not fatal. `PURSUE` needs positive evidence and coherent business structure.
`VALIDATE FIRST` requires a few cheap, discriminating tests with predeclared
PASS / FAIL / INCONCLUSIVE, threshold rationale, measurement conditions,
confounders, and what a pass would not prove. `REFRAME` changes the thesis;
`REJECT` is allowed and should be clear. `NOT ISSUED` is reserved for blocked
adjudication, not ordinary idea-stage uncertainty. Business outcome and verdict
are separate; a strong bootstrapped niche can be worth pursuing.

After compaction, reload this skill and the relevant original reference files;
do not reconstruct packet text or lost reports from a summary. Recover captured
records or mark the missing context explicitly.

## Invocation

`$startup-jury Evaluate this startup idea: ...`

## Business-decision extension
Read [the additional business-decision checks](references/business-decision-checks.md) with the existing framework. They extend the installed eleven-role engine; they do not replace its evidence, independence or verdict rules.
