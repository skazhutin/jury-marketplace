# Changelog

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
