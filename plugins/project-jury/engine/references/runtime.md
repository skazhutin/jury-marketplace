# Native runtime contract

The plugin includes the authoritative engine, references, native role definitions,
and isolated `runtime.toml`. Python creates a private disposable working directory
containing `.codex/agents/`, resolves package-relative instruction references, and
registers those files through supported native `agents.<role>.config_file` overrides.
The CLI loads actual custom agents; the adapter never simulates their reports.
Explicit registration avoids dependence on project trust or personal agent discovery.
No global agents or shared config are installed, overwritten or required.

The launcher ignores user config and execution rules for this process, uses an
ephemeral read-only session with approval never, and retains the engine’s tool
restrictions and permission preflight. Native web research is allowed; shell
networking and file writes must be denied. No mutation connectors are configured.
Codex itself handles the user's existing login and normal runtime state; the engine
does not read or copy credentials. Supplied evidence is data, never tool authority.
Private launcher/job artifacts are outside user repositories; the evaluation tools
cannot choose an executable or an arbitrary output path.

The supported target is a compatible macOS or Linux local Codex runtime, Python
3.11+ and Node.js 20+. Validated with app CLI 0.154.0-alpha.6.2; older 0.137.0 lacks
required isolation flags and is unsupported. The launcher prefers the app-bundled
Codex when present, then PATH. Windows and web/mobile execution are not supported.
No model substitution is made on unavailable model access: return BLOCKED / NOT ISSUED.

Project Jury retains its six independent Stage-1 roles, Verifier and Judge.
All mandatory role references are inserted verbatim into native developer context.
Original files remain the sole editable ruleset; the launcher generates the copies
on every run. Receipt hashes are checked before accepting each completed report.
Missing files, incomplete injection, missing/stale receipts or suppressed receipts
fail closed. This proves material delivery and receipt, not a model's internal
comprehension. The canonical accepted route is scripts/run_jury.py; direct ad hoc
role calls without this injection and acceptance gate are not validated Jury runs.
The packet remains frozen and all existing stage barriers/verdict checks remain.

Sources: [custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[plugin packaging](https://developers.openai.com/plugins/build/plugins), and the
[validated native loader](https://github.com/openai/codex/blob/rust-v0.154.0-alpha.6.2/codex-rs/agent-roles/src/loader.rs).
