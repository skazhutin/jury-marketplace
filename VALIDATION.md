# Release validation

Version: **1.0.0** for both plugins. Validation date: **2026-09-14**.

| Check | Result | Scope |
| --- | --- | --- |
| Current portable plugin/MCP JSON schemas | PASSED | Both root manifests and MCP files |
| Current Codex compatibility validator | PASSED | Both compatibility manifests |
| Skill validation | PASSED | Both routing skills and authoritative engine skills |
| Marketplace parser and discovery | PASSED | Both entries resolved through CLI 0.154.0-alpha.6.2 |
| Clean local marketplace installation | PASSED | Separate Codex home; both plugins installed at 1.0.0 |
| Git marketplace installation | NOT TESTED | Updated after public repository validation |
| Project native complete-reference case | PASSED | Real custom project_value; original report accepted |
| Project missing-reference case | PASSED | Removing one receipt from that native report caused rejection; removing native injected content also failed before dispatch |
| Project coordinator-suppression case | PASSED | A fresh real custom project_value received mandatory developer context and retained required receipts despite the conflicting coordinator request |
| Project acceptance regressions | PASSED | Seven model-free cases, including missing/stale receipts and exact enum boundaries |
| Startup native research role | PASSED | Real custom startup_landscape started in a clean Codex home with no personal agents |
| Startup search and open | PASSED | Native role reported issuing search_query for “IANA example domains documentation”, receiving public results, then opening a returned IANA page |
| Startup write restriction | PASSED | Native role observed PermissionError on the authorized creation canary; the file remained absent |
| Startup recorder regressions | PASSED | Five existing model-free tests |
| Adapter tests | PASSED | Nine Project and three Startup tests |
| Bundled MCP contracts | PASSED | Both handshakes, bounded operations, invalid-input rejection, exact text fallback, widget resource retrieval; no node_modules required |
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
