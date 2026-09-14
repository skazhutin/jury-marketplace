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

Startup Jury retains its eight independent Stage-1 roles, Verifier,
Cross-Examiner and Judge, plus the original packet recorder and stage barriers.
The coordinator is GPT-5.5/high for native spawn/close lifecycle support; all eleven
reviewers remain GPT-6 Astra/high. The five business-decision additions are unchanged.
Use scripts/run.py; direct calls from an unrestricted parent do not prove isolation.

Sources: [custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[plugin packaging](https://developers.openai.com/plugins/build/plugins), and the
[validated native loader](https://github.com/openai/codex/blob/rust-v0.154.0-alpha.6.2/codex-rs/agent-roles/src/loader.rs).
