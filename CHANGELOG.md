# Changelog

## 1.1.4 — 2026-10-07

- Correct a false preflight block: an imagegen skill catalog entry or image-rendering helper does not establish a callable image-generation backend. Require the actual tool/schema for a mutation-capability block; preserve denied-write probes and stop for genuinely callable mutation integrations.

## 1.1.3 — 2026-10-07

- Make the authorized shell permission canary deterministic: use a quoted shell-builtin redirection command, which works with the intentionally stripped PATH. A missing executable never counts as sandbox-denial evidence; keep both canaries and the fail-closed permission barrier.

## 1.1.2 — 2026-10-07

- Add allowlisted operational progress to Project Jury polling. Never store prompts, commands, role report text or private reasoning in progress metadata; completed context counts include preflight/retries and do not imply a verdict.
- Bound report verbosity while preserving every required section, evidence record and experiment criterion. Keep the 40-minute deadline, native models, fresh contexts and acceptance gates unchanged.
- Preserve only the private intentional completion candidate for validation diagnostics; never expose unvalidated results through MCP.

## 1.1.1 — 2026-10-07

- Fix Project Jury preflight for modern collaboration runtimes that expose no close tool. Confirm terminal completion, preserve permission checks, and require a fresh context for every reviewer and retry. Document active-turn capacity and local V2 completed-agent eviction with primary sources.
- Correct runtime documentation to match PATH-first compatible CLI selection and distinguish READY from a completed evaluation. Startup Jury retains its recorded spawn/close lifecycle; this patch does not claim a full Startup run.

## 1.1.0 — 2026-10-07

- Update MCP SDK to 1.32.1, MCP Apps to 2.0.3, Zod to 4.6.5, and affected transitive dependencies; rebuild shipped server and UI bundles. The release audit reports zero known vulnerabilities.
- Select a compatible Codex on PATH before trying desktop fallbacks. An explicit `JURY_CODEX_BINARY` override fails clearly if incompatible. Check required isolation capabilities rather than assuming a particular app path or version.
- Enforce Node.js 20+ at startup and remove duplicate launcher guards. Keep native role models and decision rules unchanged.
- Add a model-free `health_check` tool and `npm run doctor` to both packages. Check all 19 bundled role definitions, runtime dependencies, isolation flags and login without exposing credentials or making an evaluation request.
- Mark failed Startup Jury runs as tool errors and reject unsuccessful bridge processes. Read MCP version from package metadata.
- Add GitHub Actions on pushes, pull requests and a weekly schedule: Linux/macOS, Node 20/24, Python 3.11/3.14, adapter and engine tests, vulnerability audits, package validation and reproducible bundle checks.
- Add weekly Dependabot updates and document the Git marketplace upgrade and reinstall flow. Dependency updates must include rebuilt distributable bundles and pass CI before release.

## 1.0.0 — 2026-09-14

Initial portable, self-contained Project Jury and Startup Jury packages.
