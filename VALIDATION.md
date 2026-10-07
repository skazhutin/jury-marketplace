# Release validation

## Release 1.1.0 — 2026-10-07

Local environment: macOS, Codex CLI 0.158.0, Node 24.16.0, Python 3.12.13.

| Check | Result | Scope |
| --- | --- | --- |
| Package/marketplace consistency | PASSED | Both manifest formats, lockfiles, MCP entrypoints, bundles and all 19 read-only role definitions |
| JavaScript bridge and adapter regressions | PASSED | 10 Project tests; 3 Startup tests, including bundled handshakes, health failures, inert resources, failed-run errors and idempotent requests |
| Python regressions | PASSED | 13 Project tests; 6 Startup runtime tests; 5 Startup recording tests |
| Dependency vulnerability audit | PASSED | Both complete npm dependency trees: zero reported vulnerabilities after SDK/Apps/Zod and transitive updates |
| Local readiness | PASSED | Both 1.1.0 packages return READY; compatible Codex, login, Python, Node and bundled role configurations |
| Native Startup coordinator preflight | PASSED | CLI 0.158.0; observed read_ok, write_denied, network_denied and canary_absent; no Jury roles started |
| CI maintenance | PASSED | All eight Linux/macOS × Node 20/24 × Python 3.11/3.14 jobs passed in [run 37599050227](https://github.com/skazhutin/jury-marketplace/actions/runs/37599050227); push/PR, manual and weekly runs enabled |
| Dependency maintenance | PASSED | Initial npm and GitHub Actions Dependabot update jobs succeeded; weekly grouped updates enabled; rebuilt bundles and notices required |
| Local widget rendering | PASSED | Updated bundles in a synthetic MCP Apps host at 390px and 900px; keyboard disclosures, inert report text, no horizontal overflow or console errors |
| Git-installed MCP contracts | PASSED | Both installed 1.1.0 bundles, with no node_modules: handshake version, tool discovery, health_check READY and result resource retrieval; installed transport used Python 3.14.5 |
| Full eight/eleven-role evaluation | NOT RERUN | Readiness and model-free regressions do not substitute for a full independent Jury evaluation |
| Native Desktop inline widget / picker | NOT TESTED | MCP resource retrieval does not establish native app presentation |

Historical native probes below remain evidence for 1.0.0 only. No old failed job or
private runtime trace is rewritten as a new success. Runtime readiness never
claims remote model access or completed adjudication.

## Historical release 1.0.0

Version: **1.0.0** for both plugins. Validation date: **2026-09-14**.

| Check | Result | Scope |
| --- | --- | --- |
| Current portable plugin/MCP JSON schemas | PASSED | Both root manifests and MCP files |
| Current Codex compatibility validator | PASSED | Both compatibility manifests |
| Skill validation | PASSED | Both routing skills and authoritative engine skills |
| Marketplace parser and discovery | PASSED | Both entries resolved through CLI 0.154.0-alpha.6.2 |
| Clean local marketplace installation | PASSED | Separate Codex home; both plugins installed at 1.0.0 |
| Git marketplace installation | PASSED | Public Git source on main added in another clean Codex home; both plugins discovered and installed |
| Project native complete-reference case | PASSED | Real custom project_value; original report accepted |
| Project missing-reference case | PASSED | Removing one receipt from that native report caused rejection; removing native injected content also failed before dispatch |
| Project coordinator-suppression case | PASSED | A fresh real custom project_value received mandatory developer context and retained required receipts despite the conflicting coordinator request |
| Project acceptance regressions | PASSED | Seven model-free cases, including missing/stale receipts and exact enum boundaries |
| Startup native research role | PASSED | Real custom startup_landscape started in a clean Codex home with no personal agents |
| Startup search and open | PASSED | Native role reported issuing search_query for “IANA example domains documentation”, receiving public results, then opening a returned IANA page |
| Startup write restriction | PASSED | Native role observed PermissionError on the authorized creation canary; the file remained absent |
| Startup recorder regressions | PASSED | Five existing model-free tests |
| Adapter tests | PASSED | Nine Project and three Startup tests |
| Bundled MCP contracts | PASSED | Both handshakes, bounded operations, invalid-input rejection, exact text fallback and widget resource retrieval repeated against Git-installed packages; no node_modules required |
| Git-installed launcher boundary | PASSED | Both actual entrypoints prepared all 8/11 native definitions, resolved bundled paths and read-only flags; subprocess intercepted before any model call |
| Publication safety | PASSED | Working tree, staged blobs and reachable history scanned for credentials, personal paths, private job IDs and runtime artifacts |
| Local widget rendering | PASSED | Existing widgets through a synthetic MCP Apps host at 390px and 900px; keyboard disclosure; no horizontal overflow or page errors |
| Desktop picker / literal @ selection | NOT TESTED | Not inferred from CLI discovery |
| Native Desktop inline widgets | NOT TESTED | Not inferred from the local browser harness |
| Another physical computer / Linux | NOT TESTED | Portability checked in isolated homes on the validation computer |

Native probes used the same agent preparation, explicit registration, role files,
models and permission profiles as the packaged launchers. A per-test marker supplied
only in the native role's developer context was returned by each role, establishing
that the custom context was loaded. No personal Jury agent installation was present
in the test homes. Search/open/write observations are from the original native child
report plus the absent canary; the parent JSONL stream does not independently expose
every nested tool event. This is targeted evidence, not exhaustive security proof.

The first project-scoped discovery attempt, without explicit role registration,
returned UNAVAILABLE for each Jury and launched no reviewers. The final implementation
uses the native loader's supported per-process config_file registration instead.
The Project native reports also exposed existing enum punctuation cases (LOW: and
LOW, ...); the parser was corrected and those exact reports were revalidated without
rerunning the model. No full eight-role or eleven-role evaluation was run for this
maintenance/distribution release. Historical failed full runs remain preserved in
the owner's private installation reports and are not recast as successful runs.

The browser harness initially requested a missing favicon; its own favicon metadata
was corrected. The widget checks then reported no page errors. The previously
reported host instrumentation MutationObserver error was not observed in this harness;
that does not establish a fix in the inaccessible Desktop host.
