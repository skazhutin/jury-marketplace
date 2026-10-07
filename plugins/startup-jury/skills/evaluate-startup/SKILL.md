---
name: evaluate-startup
description: Route @Startup Jury evaluation requests to the existing isolated eleven-role Startup Jury engine and display its result. Not general brainstorming or implementation.
---

Use the plugin's startup_jury MCP tools. Send the startup idea and only permitted
user-provided evidence to `start_evaluation` with a stable request_id. Preserve
that ID on retries. Call `get_evaluation` with wait_seconds up to 50 until FINISHED
or FAILED; then call `show_evaluation`. Return the exact Judge report as the text
fallback when rich UI is unavailable. Keep its limitations, citations and verdict.
Do not issue a separate judgment or simulate Jury roles in the calling task.

For an explicitly requested synthetic installation/regression test, use
synthetic_test=true. It runs the engine's fixed fictional packet, not the
submitted real-world idea. Ordinary evaluations use false.

The bundled [Startup Jury engine](../../engine/SKILL.md), its eleven roles, frozen-packet protocol,
recorder and read-only launcher are the only substantive engine. The adapter contains routing and presentation only; substantive rules live in engine/. If tools or engine are unavailable,
report BLOCKED / NOT ISSUED with the failure. Do not bypass isolation. This local
stdio plugin is COMPUTER-ONLY and includes all Jury engine/agent assets. A compatible local Codex login is required; no manual Jury setup is needed. It has no arbitrary shell, file, messaging,
publishing, purchase or startup-execution API. Never supply the calling task's
unrelated history or private files as startup evidence.

For installation troubleshooting or readiness requests, call `health_check` first.
It makes no model calls. Report BLOCKED checks accurately. READY confirms local
readiness only; never present it as a successful full Jury evaluation.
