# Jury Marketplace

Two independent, multi-agent systems for deciding whether an idea deserves serious work:

| Plugin | Question | Native workflow |
| --- | --- | --- |
| **Project Jury** | Is this project worth building? | Six specialists → Verifier → Judge |
| **Startup Jury** | Is this startup worth pursuing? | Eight specialists → Verifier → Cross-Examiner → Judge |

These are multi-agent Jury systems, not ordinary single-prompt reviewers. Stage-1
reviewers receive the same frozen packet in separate contexts. Later stages inspect
the original reports, trace claims, check disagreements, and issue the final verdict.
Both include an inspectable result widget and the Judge's original text fallback.

**Computer-only.** A compatible local Codex runtime and login are required, together
with **Python 3.11+** and **Node.js 20+** available to the desktop host. Native roles
require GPT-6 Astra access; Startup Jury also uses GPT-5.5 for its coordinator.
Validated on macOS with app-bundled Codex **0.154.0-alpha.6.2**. CLI **0.137.0** is
unsupported because it lacks required isolation options. Linux has compatible
packaging but is not tested; Windows, web-only and mobile execution are unsupported.
Account or organization policies may limit local plugins or model access.

## Add this marketplace

In the supported Codex/ChatGPT Desktop **Add plugin marketplace** dialog, enter:

### Source

```text
https://github.com/skazhutin/jury-marketplace.git
```

### Git ref

```text
main
```

### Sparse paths

**Leave blank.** The repository root is the marketplace root, and both complete
plugin directories must be available.

1. Add the marketplace.
2. Open **Jury Marketplace**.
3. Install **Project Jury** and/or **Startup Jury**.
4. Start a fresh conversation/task.
5. Select the installed plugin using the supported mention interface:
   **@Project Jury** or **@Startup Jury**, followed by the idea and permitted evidence.

**No one-time Jury engine setup is required.** Each package includes its own native
agent definitions, engine, instructions, schemas, validators, MCP bridge and UI.
The launcher prepares private runtime files automatically; it never installs agents
into your global configuration. Your existing Jury installations can coexist.

The documented Desktop flow is intended usage. Actual visual marketplace/picker
selection and native inline widget rendering were **NOT TESTED**. CLI installation
and a local MCP Apps harness provide narrower evidence.

### CLI installation

The following commands were tested with the compatible runtime described above.
Use that binary if an older `codex` comes first on your PATH.

```sh
codex plugin marketplace add https://github.com/skazhutin/jury-marketplace.git --ref main
codex plugin list --marketplace jury-marketplace --available --json
codex plugin add project-jury@jury-marketplace
codex plugin add startup-jury@jury-marketplace
```

Start a new CLI session afterward. Installing from Git does not upgrade Codex or
grant model access. Missing capabilities return an execution failure rather than
an invented Jury verdict.

## Runtime and privacy

Each launcher builds a disposable `.codex/agents/` directory from the package and
registers those native files with explicit per-process configuration. This avoids
dependence on personal agents or host-specific project trust. Evaluation uses an
ephemeral, read-only native runtime with approval set to never and mutation
integrations disabled. Native web research is permitted. A failed permission
preflight blocks evaluation.

The MCP APIs expose only bounded evaluation and result operations—no arbitrary
command, filesystem-path, publishing or messaging endpoint. Launcher-owned job
files are stored privately under `$CODEX_HOME/jury-marketplace/<plugin>/jobs`
(default Codex home when unset). They contain submitted evidence and intentional
reports; retain or remove them according to your needs after evaluations finish.
Codex handles its existing login. Credentials and raw runtime traces are never
returned through the plugin API. Submitted evidence is processed by your Codex
model service; public research queries use native web search.

Project Jury injects mandatory reference text into native developer context and
rejects reports with absent or stale reference receipts. This verifies delivery
and receipt, not a model's internal understanding. Existing independence, claim
tracing, failure propagation, stage barriers and verdict semantics are retained.

## Maintenance and validation

The two directories under `plugins/` are the distributable source of truth.
Modify substantive rules in each plugin's `engine/`; keep MCP adapters limited to
transport and presentation. Commit source, lockfiles, bundles and dependency notices
together. Use semantic versions; record Git revisions separately.

Each plugin can be rebuilt with `npm ci`, `npm test`, and `npm run build` from its
directory. End users need no npm installation: the server and widget are bundled.
Run `python3 -m unittest discover -s plugins/project-jury/tests -p 'test_*.py'` and
`python3 plugins/startup-jury/engine/scripts/test_recording.py` for model-free engine checks.

The initial release uses targeted native role/reference/search checks, parser and
adapter tests, isolated marketplace installation, and local widget checks. No full
eight-role or eleven-role evaluation was rerun merely for packaging. Historical
failed installation runs are retained privately; they are not rewritten as passes.
See [VALIDATION.md](VALIDATION.md) for evidence boundaries.

Built against current official [plugin packaging and marketplace documentation](https://developers.openai.com/plugins/build/plugins)
and [native custom-agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents).

## License

Jury source is [MIT licensed](LICENSE). Bundled dependencies retain their
[third-party notices](THIRD_PARTY_NOTICES.md). This is an independent project,
not an OpenAI product or endorsement.
