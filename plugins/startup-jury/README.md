# Startup Jury

See the [marketplace README](../../README.md) for installation, compatibility and privacy.

This complete package contains the authoritative rules and native roles in `engine/`,
a bounded stdio MCP bridge, and the existing result widget with structured text fallback.
No global Jury engine or manual agent setup is required.

For development, run `npm ci --ignore-scripts`, `npm test`, and `npm run build` in this directory.
Bundled JavaScript ships with the package; end users do not run npm install.
Change substantive rules only in `engine/`; keep the adapter limited to transport/presentation.

Run `npm run doctor` for a model-free readiness check, or invoke the installed
`health_check` tool. `READY` checks local dependencies, roles, isolation capabilities
and login; it does not claim a full evaluation passed. See the marketplace README
for the upgrade/reinstall flow and weekly CI/Dependabot maintenance.
