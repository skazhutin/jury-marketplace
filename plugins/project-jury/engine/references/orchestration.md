# Coordinator contract

Before dispatch, verify the current tool schema supports selecting installed custom agents, fresh independent context, research-only tools, and effective read-only restrictions. Never treat `task_name` as a custom-agent selector unless the runtime documents that behavior. If these guarantees are unavailable in the active desktop session, use the isolated launcher. Never simply label six sections as six independent agents.

Freeze the exact serialized packet and common-source material and keep a digest. Pass those exact bytes directly to every Stage 1 invocation, with a separate role assignment and identical common instructions. Do not forward parent conversation history; explicitly request no fork (`fork_context=false` or `fork_turns="none"` only when present in the actual tool schema). Re-read actual tool definitions rather than inventing arguments. If custom agents cannot start without a contaminated fork, stop and record BLOCKED.

Keep reports in coordinator memory, not shared filesystem artifacts during Stage 1. Never expose sibling thread IDs or private role markers to another Stage 1 role. Do not allow specialists to read Codex session stores. Use ephemeral sessions in the launcher. Common source files may be read only if every role receives the same legitimately available content/access. A new user change requires a new frozen packet and restarting affected Stage 1 analyses; do not patch only later roles.

Maintain a role ledger with pending/running/complete/failed, attempt count, packet hash, context receipt, and execution limitation. A role is complete only when all required report sections and enum values are present. Retry a failed/invalid role once in a fresh context with the identical frozen input and a schema-repair instruction, never another agent's report. A repeated invalid report remains a failure. Bound each attempt to 10 minutes, and the overall run to 40 minutes unless the user supplies a different limit; terminate/release timed-out children. These are operational limits, not reasons to reject the project.

Stage barriers: no verifier until each of the six roles has either a valid captured report or an explicit final failure record after the retry procedure. No judge until the verifier has a captured report or explicit verification failure. Do not count a started role as completed. Preserve all available reports even when another role fails. Verifier failure also receives at most one safe retry; if still unavailable, the judge must assess whether a bounded verdict is defensible and normally use BLOCKED/NOT ISSUED when critical claims remain unverified. If the Judge fails twice, report orchestration BLOCKED/NOT ISSUED from the coordinator without pretending it is a Judge decision.

Use stable prefixed claim IDs; preserve every originating ID. Canonicalize equivalent claims only after Stage 1 with an alias mapping, never silently rename or rewrite them. Deduplicate by underlying evidence, not URL count or number of agents citing it. The registry carries the complete compact claim records, their originating roles, source dependencies, and disagreements. Verifier corrections must flow into downstream conclusions.

For each meaningful disagreement, record both positions with claim IDs without a coordinator verdict. Verifier receives packet, all successful reports, registry, disagreements, and failures. Judge receives packet, every available Stage 1 report, verifier report, registry/aliases as needed to interpret references, and all execution limitations. Do not send only summaries in place of required reports.

Capture reports and confirm terminal completion before moving to another batch or stage. Use the runtime's actual close/release tool only when its lifecycle requires it. Modern hosted collaboration exposes no close tool: its cap counts active subagent turns, so completed turns no longer occupy active slots. Local Codex V2 can automatically unload completed idle agents when reserving another slot. Neither mechanism requires deleting the completed context. The synthetic permission-preflight agent must finish before any project dispatch; never resume it or reuse its context for a reviewer. Every reviewer and retry requires a fresh independent context. Do not invent a close tool or treat its absence alone as a blocker. Interruption alone is not terminal-completion or release evidence: wait for a terminal status after cancelling a running child. If actual spawn attempts still cannot obtain a slot after completed reports are captured, record the limitation rather than reusing a contaminated reviewer context. Batch within the current available cap, never lower a user's existing configured cap, and do not assume a file edit changes an already-running session.

Lifecycle references: [hosted collaboration and active-turn limits](https://developers.openai.com/api/docs/guides/responses-multi-agent#how-multi-agent-works), [Codex 0.158.0 V2 idle-agent eviction](https://github.com/openai/codex/blob/rust-v0.158.0/codex-rs/core/src/agent/control/residency.rs), and its [completed-agent eviction regression test](https://github.com/openai/codex/blob/rust-v0.158.0/codex-rs/core/src/agent/control/residency_tests.rs). Apply the lifecycle matching the actual exposed tool schema; these references do not waive permission checks or stage barriers.

The launcher runs in an isolated read-only parent, strips shell environment inheritance, disables configured apps/plugins/MCP integrations and hooks, and uses native web search for current evidence. Native web access does not require shell network access. No reviewer may install dependencies or launch shell network clients. Verify effective permissions at launch and child startup. A stored read-only default alone is not proof.

# 4. Architecture

Use a staged multi-agent process.

## STAGE 1 — Independent evaluation

Run SIX independent specialist agents concurrently.

They must all receive the same frozen PROJECT PACKET and the same permitted common source materials.

Their initial analyses must be independent.

They MUST NOT see each other's reports before submitting their own.

Use these agents:

1. `project_value`
2. `project_technical`
3. `project_landscape`
4. `project_execution`
5. `project_advocate`
6. `project_skeptic`

Wait for all six to finish, or exhaust the defined retry/failure procedure and explicitly record any missing role before Stage 2.

These agents must not recursively create their own subagents.

---

# 22. Agent independence and failure handling

First-stage agents must not anchor one another.

Do not:

1. run Skeptic;
2. show Skeptic to everyone else;
3. ask everyone to respond to Skeptic.

Instead:

all six first-stage agents independently evaluate the same frozen PROJECT PACKET.

Only the Verifier and Judge see the complete set.

Each Stage 1 invocation must be given the frozen PROJECT PACKET directly, not a coordinator-generated paraphrase produced after other agents have run.

If concurrency is lower than six, use independent batches. Later batches must not receive earlier Stage 1 outputs.

If a first-stage agent errors, times out, or returns an invalid/incomplete schema:

1. record the failure;
2. retry that role once with the same frozen packet if the current Codex environment supports a safe retry;
3. do not substitute another role's report;
4. do not simulate multiple agents inside one assistant response while claiming independence;
5. if the missing role is decision-critical and cannot be recovered, propagate the limitation to the Verifier and Judge and use `LIMITED` or `BLOCKED` appropriately.

After a batch's reports are captured by the coordinator, close/release child-agent sessions when the current Codex runtime requires this to free concurrency slots before later stages. Do not discard the captured reports.

---

# 23. Avoid redundant agents

The roles must stay differentiated.

`project_value`
= Why should this exist?

`project_technical`
= Can the technically meaningful/useful version work?

`project_landscape`
= What already exists and what room remains?

`project_execution`
= Can this become a finished real project?

`project_advocate`
= Strongest rigorous case FOR doing it.

`project_skeptic`
= Strongest rigorous case AGAINST doing it.

Do not let every agent write a generic full project review.

---
