---
name: evaluate
description: Use the Project Jury plugin to submit an idea to the existing isolated eight-agent Project Jury engine and display its validated result. Trigger when Project Jury is selected or explicitly requested.
---

# Project Jury plugin interface

This is a transport interface to the bundled `project-jury` engine. The files under [engine](../../engine/SKILL.md) are the authoritative evaluation specification. Do not copy, redesign, summarize away, or independently implement its evaluation logic here.

Read [the engine skill](../../engine/SKILL.md) and the full referenced packet and principles instructions before normalizing a real request. The same originals are also available as MCP resources `jury://instructions/packet` and `jury://instructions/principles`. Reread those originals after compaction or uncertainty. Do not improve the idea or convert a research project into a startup. Freeze the full packet and legitimately supplied common materials exactly once.

Use this plugin's `submit_evaluation` MCP tool with `mode=evaluation`, a fresh UUID `request_id`, the frozen `packet`, and `common_sources`. The tool calls the installed isolated `run_jury.py`, which selects six independent native reviewers, the Verifier, and then the Judge. The parent conversation must not run reviewers itself, execute the Jury directly, or fabricate reports. If tools or the installed engine are unavailable, report the limitation; do not substitute an inline review.

When the user explicitly requests a synthetic installation test, call `submit_evaluation` with `mode=synthetic_validation`, a fresh UUID, and no project packet or sources. This uses the existing launcher's synthetic fixture. It must produce no real-project verdict.

Keep the returned job ID. Retrieve it through `get_result` roughly every 30 seconds until `FINISHED` or `FAILED`, with concise progress updates. Reusing the same request ID and identical input is idempotent; never resubmit a new job just because the existing one is still running. On failure, report BLOCKED/NOT ISSUED and the actual limitation, not a judgment about the project. The job continues on this computer if the conversation disconnects; use its ID to retrieve it later.

Show the result component when the surface supports MCP Apps. Always preserve the Judge's final report and its conceptual sections as a structured-text fallback. Do not turn LOW/MEDIUM/HIGH confidence into a numerical project score. `get_result(include_reports=true)` returns intentional reviewer reports for text-only inspection. Never expose runtime JSONL or hidden/private reasoning.

Evaluation is read-only with respect to user repositories/files and external services. The adapter may create only private job artifacts. It exposes no shell, file-reading, publishing or messaging tool. Never transmit credentials or unrelated local contents. This plugin is computer-only and includes its own engine and native agents. A compatible local Codex login is required. No manual Jury setup is needed.
